"""Several voices in one short (Format 3.0 item 4, 23 Nov 2026). Narrator = Kokoro bm_george -> ChatterboxVC (Enes timbre) like every day-1/2 video;
every character = its OWN Kokoro voice, raw (not converted: the conversion flattens them). Used by tools/tts/tg.py (tutorial_guy) and pt.py (pots).
  python tools/tts/<name>.py src            # narrator sentences -> $TTS_DIR/<name>_src/ and character sentences -> $TTS_DIR/<name>_chr/
  <chatterbox python> tools/tts/vc.py <name>  # narrator only needs this (it converts every file in <name>_src)
  python tools/tts/<name>.py build <src|vc|own>   # assemble lines + sentence timings -> $TTS_DIR/<name>/ + script.json (with 'spk')
mode own: a file $TTS_DIR/<name>_own/<key>_<i>.wav (Enes's recording, made with tools/tts/own_prep.py or by hand) replaces that sentence, the rest stays AI.
D = [(key, speaker, [(text, speed, pitch_st, gain_db, pause_before_s), ...]), ...]; speaker 'N' = narrator.
VOICES = {speaker: (kokoro voice, lang)} for every other speaker."""
import json, os, sys
import numpy as np, soundfile as sf
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(HERE,'..','..','tts'))
def sentences(D): return [(f'{k}_{i}',spk,*x) for k,spk,ss in D for i,x in enumerate(ss)]
def src(D,VOICES,name):
    import emph
    from kokoro_onnx import Kokoro
    ds=os.path.join(TTS_DIR,name+'_src'); dc=os.path.join(TTS_DIR,name+'_chr'); os.makedirs(ds,exist_ok=True); os.makedirs(dc,exist_ok=True)
    DUR=f'{TTS_DIR}/kokoro-dur.onnx'
    if not os.path.exists(DUR): emph.make_dur_model(f'{TTS_DIR}/kokoro-v1.0.int8.onnx',DUR)
    k=Kokoro(DUR,f'{TTS_DIR}/voices-v1.0.bin')
    for nm,spk,tx,sp,st,g,pause in sentences(D):
        voice,lang=('bm_george','en-gb') if spk=='N' else VOICES[spk]
        try: y=emph.render(k,voice,sp,lang,tx,pitch=st,gain=g)
        except ValueError as e: y=emph.render(k,voice,sp,lang,tx.replace('*',''),pitch=st,gain=g)
        y=emph.trim(y,0.01,120,360); sf.write(os.path.join(ds if spk=='N' else dc,nm+'.wav'),y,emph.SR); print(nm,spk,voice,round(len(y)/emph.SR,2),tx)
def build(D,name,mode):
    import emph
    from scipy.signal import resample_poly
    out=os.path.join(TTS_DIR,name); os.makedirs(out,exist_ok=True); dur={}; txt={}; sent={}; spkmap={}; SR=emph.SR
    nar_dir=os.path.join(TTS_DIR,name+('_src' if mode=='src' else '_vc')); chr_dir=os.path.join(TTS_DIR,name+'_chr'); own_dir=os.path.join(TTS_DIR,name+'_own')
    for k,spk,ss in D:
        parts=[]; pos=0; sent[k]=[]; spkmap[k]=spk
        whole=os.path.join(own_dir,f'{k}_all.wav')
        if mode=='own' and os.path.exists(whole):                      # Enes read the whole line in one take: keep it, find the sentence breaks in it
            y,sr=sf.read(whole); y=y if y.ndim==1 else y.mean(1)
            if sr!=SR: y=resample_poly(y,SR,sr)
            act=np.abs(y)>0.01; y=y*(0.11/np.sqrt((y[act]**2).mean())); pk=np.abs(y).max()
            if pk>0.9: y=np.tanh(y/0.9)*0.9
            fr=int(0.01*SR); nf=len(y)//fr; db=20*np.log10(np.sqrt((y[:nf*fr].reshape(nf,fr)**2).mean(1))+1e-9); voiced=db>-38
            segs=[]; i=0
            while i<nf:
                if voiced[i]:
                    j=i
                    while j<nf and voiced[j]: j+=1
                    if segs and i-segs[-1][1]<12: segs[-1]=[segs[-1][0],j,max(segs[-1][2],float(db[i:j].max()))]
                    else: segs.append([i,j,float(db[i:j].max())])
                    i=j
                else: i+=1
            peak=max(s_[2] for s_ in segs)
            while len(segs)>1 and (segs[0][1]-segs[0][0]<6 or segs[0][2]<-33): segs.pop(0)          # clicks / faint breaths before the line (quiet WORDS stay)
            while len(segs)>1 and (segs[-1][1]-segs[-1][0]<6 or segs[-1][2]<-33): segs.pop()            # blips after it
            a0=max(0,segs[0][0]-5); a1=min(nf,segs[-1][1]+12); y=y[a0*fr:a1*fr].copy(); f_=int(0.01*SR); y[:f_]*=np.linspace(0,1,f_); y[-f_:]*=np.linspace(1,0,f_)
            env=np.sqrt(np.convolve(y**2,np.ones(int(0.2*SR))/int(0.2*SR),'same'))+1e-5               # gentle levelling: quiet spoken parts up (max +12 dB), pauses untouched
            vm=np.convolve((env>0.012).astype(float),np.ones(int(0.1*SR))/int(0.1*SR),'same'); gg=np.clip((0.09/env)**0.6,0.6,4.0)
            y=y*(1+(gg-1)*vm); pk=np.abs(y).max(); y=np.tanh(y/0.95)*0.95 if pk>0.95 else y
            gaps=[((segs[q][1]+segs[q+1][0])/2-a0,segs[q][1]-a0,segs[q+1][0]-a0) for q in range(len(segs)-1)]
            L=len(y)/SR; w=np.cumsum([len(x[0]) for x in ss]); w=w/w[-1]; sp0=(segs[0][0]-a0)/100; sp1=(segs[-1][1]-a0)/100
            starts=[0.0]; ends=[]; used=-1
            for frac in w[:-1]:                                          # each sentence break -> the pause nearest its expected place (in order)
                exp_=(sp0+frac*(sp1-sp0))*100; cand=[(abs(g[0]-exp_),q) for q,g in enumerate(gaps) if q>used]
                if cand: _,q=min(cand); used=q; ends.append(gaps[q][1]/100); starts.append(gaps[q][2]/100)
                else: ends.append(exp_/100); starts.append(exp_/100)
            ends.append(L)
            for (tx,*_),a_,b_ in zip(ss,starts,ends): sent[k].append([round(a_,3),round(b_,3),tx.replace('*','')])
            y=y/np.max(np.abs(y))*0.95; sf.write(os.path.join(out,k+'.wav'),y,SR); dur[k]=round(len(y)/SR,2); txt[k]=' '.join(x[0].replace('*','') for x in ss)
            print(k,spk,dur[k],'OWN',txt[k],[s_[:2] for s_ in sent[k]]); continue
        for i,(tx,sp,st,g,pause) in enumerate(ss):
            own=os.path.join(own_dir,f'{k}_{i}.wav'); is_own=(mode=='own' and os.path.exists(own))
            f=own if is_own else os.path.join(nar_dir if spk=='N' else chr_dir,f'{k}_{i}.wav')
            y,sr=sf.read(f); y=y if y.ndim==1 else y.mean(1)
            if sr!=SR: y=resample_poly(y,SR,sr)                       # one sample rate for the whole line
            if spk=='N' and not is_own and mode!='src':               # narrator VC: pull each sentence to ~+5 % of the reference pitch (clamped +-2.5 st)
                import fp_check_lib as C
                p_=C.f0(y,SR)
                if len(p_)>=15:
                    st_=float(np.clip(12*np.log2(C.REF*1.05/np.median(p_)),-2.5,2.5))
                    if abs(st_)>0.15: y=emph.shape(y,st_,1.0,0.0)
            if is_own:                                                 # Enes's own take: one loudness (RMS of the voiced samples), soft limiter
                act=np.abs(y)>0.01; y=y*(0.11/np.sqrt((y[act]**2).mean())); pk=np.abs(y).max()
                if pk>0.9: y=np.tanh(y/0.9)*0.9
            z=np.zeros(int(pause*SR)); parts+=[z,y]; pos+=len(z); sent[k].append([round(pos/SR,3),round((pos+len(y))/SR,3),tx.replace('*','')]); pos+=len(y)
        y=np.concatenate(parts); y=y/np.max(np.abs(y))*0.95; nz=np.where(np.abs(y)>0.01)[0]; y=y[:nz[-1]+1200]; sf.write(os.path.join(out,k+'.wav'),y,SR)
        dur[k]=round(len(y)/SR,2); txt[k]=' '.join(x[0].replace('*','') for x in ss); print(k,spk,dur[k],txt[k])
    print('TOTAL',round(sum(dur.values()),2),'words',sum(len(t.split()) for t in txt.values()))
    json.dump({'text':txt,'dur':dur,'sent':sent,'spk':spkmap},open(os.path.join(out,'script.json'),'w'),indent=1)
def main(D,VOICES,name,TR=None):
    if sys.argv[1]=='src': src(D,VOICES,name)
    else:
        if TR and os.environ.get('SUB_LANG')=='tr':                   # Turkish take: find the sentence breaks from the TURKISH sentence lengths (26 Nov)
            D=[(k,spk,[(t,)+tuple(x[1:]) for t,x in zip(TR[k],ss)] if len(TR[k])==len(ss) else ss) for k,spk,ss in D]
        build(D,name,sys.argv[2])
