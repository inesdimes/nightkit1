"""Voice for "What happens to the guy whose car you steal?" (sc). One narrator, 11 lines (briefs/stolen_car.md). Same pipeline as fp.py.
Pipeline (voice option order in the brief): 1) Kokoro bm_george speaks every SENTENCE (source: accent + rhythm),
2) tools/tts/fp_vc.py (Chatterbox embedded python) converts each sentence to Enes's timbre (ChatterboxVC) -> $TTS_DIR/fp_vc/,
3) this script assembles the lines with pauses + sentence timings.   Same output shape as sk.py: $TTS_DIR/fp/<key>.wav + script.json.
  python tools/tts/fp.py src                 # Kokoro sentences -> $TTS_DIR/fp_src/<key>_<i>.wav
  python tools/tts/fp.py build <src|vc>      # assemble from fp_src (option 3 = Kokoro) or fp_vc (option 1); writes fp/ + fp/script.json
Pace / pitch per sentence: (text, speed, pitch semitones, gain dB, pause before s); *word* = stressed."""
import json, os, sys
import numpy as np, soundfile as sf
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','tts'))
S=1.22
D=[('1',[("What happens to the *guy* whose car you steal?",S,0.3,1.5,0)]),
   ('2',[("Meet Gary.",S,0.2,0.5,0),("His car has been stolen *nine hundred* times.",S,0,0.5,0.12)]),
   ('3',[("First, he bought a *lock*.",S,0.1,0.5,0),("Then an *alarm*.",S,0.1,0.5,0.1),("Then a second *car*.",S,0.1,0.5,0.1)]),
   ('4',[("They stole that one *too*.",S,-0.1,0.5,0)]),
   ('5',[("So now, Gary leaves the *keys* in the ignition.",S,0.1,0.5,0)]),
   ('6',[("And a *sandwich* on the passenger seat.",S,0.1,0.5,0)]),
   ('7',[("And a *note*: Bring her back by *six*.",S,0.1,0.5,0)]),
   ('8',[("Every evening at six, the car comes *back*.",S,0.1,0.5,0),("Full tank.",S,0,0.5,0.1),("New *dents*.",S,-0.2,0.5,0.1)]),
   ('9',[("Gary has *never* met the driver.",S,-0.1,0.5,0)]),
   ('10',[("He thinks it's the *nicest* guy in town.",S,0.2,0.5,0)]),
   ('11',[("The rest of the town *disagrees*.",S*0.95,-0.4,1.0,0)])]
SRC=os.path.join(TTS_DIR,'sc_src'); VCD=os.path.join(TTS_DIR,'sc_vc'); OUT=os.path.join(TTS_DIR,'sc')
# pitch trim after the first automatic check (VC follows the source pitch; the reference sits at ~116 Hz): all -0.6 st, line 4 a further -0.5
D=[(k,[(sx,sp,st-0.6-(0.2 if k=='1' else 0),g,pause) for sx,sp,st,g,pause in ss]) for k,ss in D]
def sentences(): return [(f'{k}_{i}',sx,sp,st,g,pause) for k,ss in D for i,(sx,sp,st,g,pause) in enumerate(ss)]
if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='src':
        import emph
        from kokoro_onnx import Kokoro
        os.makedirs(SRC,exist_ok=True); DUR=f'{TTS_DIR}/kokoro-dur.onnx'
        if not os.path.exists(DUR): emph.make_dur_model(f'{TTS_DIR}/kokoro-v1.0.int8.onnx',DUR)
        k=Kokoro(DUR,f'{TTS_DIR}/voices-v1.0.bin')
        for name,sx,sp,st,g,pause in sentences():
            try: y=emph.render(k,'bm_george',sp,'en-gb',sx,pitch=st,gain=g)
            except ValueError as e: print('  no stress:',sx,e); y=emph.render(k,'bm_george',sp,'en-gb',sx.replace('*',''),pitch=st,gain=g)
            y=emph.trim(y,0.01,120,360); sf.write(os.path.join(SRC,name+'.wav'),y,emph.SR); print(name,round(len(y)/emph.SR,2),sx)
    elif mode=='build':
        src=os.path.join(TTS_DIR,'sc_'+sys.argv[2]); os.makedirs(OUT,exist_ok=True); dur={}; txt={}; sent={}
        for k,ss in D:
            parts=[]; pos=0; sent[k]=[]; SR=None
            for i,(sx,sp,st,g,pause) in enumerate(ss):
                y,SR=sf.read(os.path.join(src,f'{k}_{i}.wav')); y=y if y.ndim==1 else y.mean(1)
                import emph as _e
                if SR!=_e.SR: y=__import__('scipy.signal',fromlist=['x']).resample_poly(y,_e.SR,SR); SR=_e.SR      # one sample rate for the whole line (mixed rates wrecked line 3)
                if sys.argv[2]=='vc':                       # VC follows the source pitch loosely: pull each sentence to ~+5 % of the reference (clamped +-2.5 st)
                    import emph, fp_check_lib as C
                    p_=C.f0(y,SR)
                    if len(p_)>=15:
                        st_=float(np.clip(12*np.log2(C.REF*1.05/np.median(p_)),-2.5,2.5))
                        if abs(st_)>0.15: y=emph.shape(y,st_,1.0,0.0)
                z=np.zeros(int(pause*SR)); parts+=[z,y]; pos+=len(z); sent[k].append([round(pos/SR,3),round((pos+len(y))/SR,3),sx.replace('*','')]); pos+=len(y)
            y=np.concatenate(parts); y=y/np.max(np.abs(y))*0.95; nz=np.where(np.abs(y)>0.01)[0]; y=y[:nz[-1]+1200]; sf.write(os.path.join(OUT,k+'.wav'),y,SR)
            dur[k]=round(len(y)/SR,2); txt[k]=' '.join(x[0].replace('*','') for x in ss); print(k,dur[k],txt[k])
        print('TOTAL',round(sum(dur.values()),2),'words',sum(len(t.split()) for t in txt.values()))
        json.dump({'text':txt,'dur':dur,'sent':sent},open(os.path.join(OUT,'script.json'),'w'),indent=1)
