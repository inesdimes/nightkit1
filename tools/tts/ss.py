"""Voice for "Why do final bosses give a speech before the fight?" (ss). One narrator, 11 lines (briefs/skip_speech.md). Same pipeline as sc.py.
  python tools/tts/ss.py src                 # Kokoro bm_george sentences -> $TTS_DIR/ss_src/<key>_<i>.wav
  <chatterbox python> tools/tts/vc.py ss     # ChatterboxVC -> Enes timbre -> $TTS_DIR/ss_vc/
  python tools/tts/ss.py build <src|vc>      # assemble lines + sentence timings -> $TTS_DIR/ss/ + script.json
  python tools/tts/sc_check.py ss            # clipping / pitch checks
Per sentence: (text, speed, pitch semitones, gain dB, pause before s); *word* = stressed."""
import json, os, sys
import numpy as np, soundfile as sf
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','tts'))
S=1.18
D=[('1',[("Why do final bosses always give a *speech* before the fight?",S,0.3,1.5,0)]),
   ('2',[("This one wrote his speech *thirty years* ago.",S,0.1,0.5,0)]),
   ('3',[("He rehearsed it every *night*.",S,0.1,0.5,0),("Pauses.",S,0,0.5,0.15),("Hand gestures.",S,0,0.5,0.12),("A dramatic *cape* flip.",S,0.1,0.5,0.12)]),
   ('4',[("Then the first hero arrived,",S,0.1,0.5,0),("and pressed *skip*.",S,0,0.5,0.08)]),
   ('5',[("So did the *next* one.",S,0.1,0.5,0),("And the next.",S,0,0.5,0.1)]),
   ('6',[("Until one knight walked in...",S*0.95,0,0.5,0),("and didn't press *anything*.",S*0.95,-0.1,0.5,0.3)]),
   ('7',[("The boss *froze*.",S,-0.1,0.5,0),("Nobody had ever heard his *second* sentence.",S,0.1,0.5,0.15)]),
   ('8',[("He spoke for *eleven minutes*.",S,0.1,0.5,0)]),
   ('9',[("When it ended, the knight *clapped*.",S,0.1,0.5,0)]),
   ('10',[("Then the fight began.",S,0,0.5,0),("He was too *happy* to dodge.",S,0.2,0.5,0.12)]),
   ('11',[("He lost in *one* hit.",S,0,0.5,0),("Best day of his *life*.",S*0.95,-0.3,1.0,0.25)])]
NAME='ss'; SRC=os.path.join(TTS_DIR,NAME+'_src'); OUT=os.path.join(TTS_DIR,NAME)
D=[(k,[(sx,sp,st-0.6,g,pause) for sx,sp,st,g,pause in ss]) for k,ss in D]      # same pitch trim as sc.py (VC follows the source pitch)
def sentences(): return [(f'{k}_{i}',sx,sp,st,g,pause) for k,ss in D for i,(sx,sp,st,g,pause) in enumerate(ss)]
def build(D,name,mode):
    import emph
    src=os.path.join(TTS_DIR,name+'_'+mode); out=os.path.join(TTS_DIR,name); os.makedirs(out,exist_ok=True); dur={}; txt={}; sent={}
    for k,ss in D:
        parts=[]; pos=0; sent[k]=[]; SR=emph.SR
        for i,(sx,sp,st,g,pause) in enumerate(ss):
            y,sr=sf.read(os.path.join(src,f'{k}_{i}.wav')); y=y if y.ndim==1 else y.mean(1)
            if sr!=SR: y=__import__('scipy.signal',fromlist=['x']).resample_poly(y,SR,sr)       # one sample rate for the whole line
            if mode=='own': y=emph.trim(y,0.01,120,360)      # Enes's own recordings: only trim the silence
            if mode=='vc':                                  # pull each sentence to ~+5 % of the reference pitch (clamped +-2.5 st)
                import fp_check_lib as C
                p_=C.f0(y,SR)
                if len(p_)>=15:
                    st_=float(np.clip(12*np.log2(C.REF*1.05/np.median(p_)),-2.5,2.5))
                    if abs(st_)>0.15: y=emph.shape(y,st_,1.0,0.0)
            z=np.zeros(int(pause*SR)); parts+=[z,y]; pos+=len(z); sent[k].append([round(pos/SR,3),round((pos+len(y))/SR,3),sx.replace('*','')]); pos+=len(y)
        y=np.concatenate(parts); y=y/np.max(np.abs(y))*0.95; nz=np.where(np.abs(y)>0.01)[0]; y=y[:nz[-1]+1200]; sf.write(os.path.join(out,k+'.wav'),y,SR)
        dur[k]=round(len(y)/SR,2); txt[k]=' '.join(x[0].replace('*','') for x in ss); print(k,dur[k],txt[k])
    print('TOTAL',round(sum(dur.values()),2),'words',sum(len(t.split()) for t in txt.values()))
    json.dump({'text':txt,'dur':dur,'sent':sent},open(os.path.join(out,'script.json'),'w'),indent=1)
def src(D,name):
    import emph
    from kokoro_onnx import Kokoro
    d=os.path.join(TTS_DIR,name+'_src'); os.makedirs(d,exist_ok=True); DUR=f'{TTS_DIR}/kokoro-dur.onnx'
    if not os.path.exists(DUR): emph.make_dur_model(f'{TTS_DIR}/kokoro-v1.0.int8.onnx',DUR)
    k=Kokoro(DUR,f'{TTS_DIR}/voices-v1.0.bin')
    for nm,sx,sp,st,g,pause in [(f'{k_}_{i}',*x) for k_,ss in D for i,x in enumerate(ss)]:
        try: y=emph.render(k,'bm_george',sp,'en-gb',sx,pitch=st,gain=g)
        except ValueError as e: print('  no stress:',sx,e); y=emph.render(k,'bm_george',sp,'en-gb',sx.replace('*',''),pitch=st,gain=g)
        y=emph.trim(y,0.01,120,360); sf.write(os.path.join(d,nm+'.wav'),y,emph.SR); print(nm,round(len(y)/emph.SR,2),sx)
if __name__=='__main__':
    if sys.argv[1]=='src': src(D,NAME)
    else: build(D,NAME,sys.argv[2])
