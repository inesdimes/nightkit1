"""Voice for "Why do final bosses always have three phases?" (fp). One narrator, 11 lines (briefs/four_phases.md).
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
D=[('1',[("Why do final *bosses* always have three phases?",S,0.3,1.5,0)]),
   ('2',[("The knight lands the final blow.",S,0,0.5,0),("Phase one... *down*.",S*0.95,-0.3,0.5,0.15)]),
   ('3',[("Phase two.",S,0.2,0.5,0),("The boss is *somehow* shorter.",S,0,0.5,0.1)]),
   ('4',[("Phase three.",S,0.2,0.5,0),("Even *shorter*.",S,-0.2,0.5,0.1)]),
   ('5',[("Then the cloak *slips*.",S*0.92,0.5,1.0,0)]),
   ('6',[("It was never one monster.",S,-0.2,0.5,0),("It was three *goblins*, stacked.",S,0.3,1.0,0.15)]),
   ('7',[("The one at the bottom had been holding the others for *thirty* years.",S,-0.2,0.5,0)]),
   ('8',[("The knight lowers his sword.",S,-0.1,0.5,0)]),
   ('9',[("And crawls under the *cloak*.",S,0.1,0.5,0)]),
   ('10',[("Now the final boss has *four* phases.",S,0.2,1.0,0)]),
   ('11',[("And the old goblin finally gets a day *off*.",S*0.95,-0.4,1.0,0)])]
SRC=os.path.join(TTS_DIR,'fp_src'); VCD=os.path.join(TTS_DIR,'fp_vc'); OUT=os.path.join(TTS_DIR,'fp')
# pitch trim after the first automatic check (VC follows the source pitch; the reference sits at ~116 Hz): all -0.6 st, line 4 a further -0.5
D=[(k,[(sx,sp,st-0.6-(0.5 if k=='4' else 0)-(0.2 if k=='1' else 0),g,pause) for sx,sp,st,g,pause in ss]) for k,ss in D]
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
        src=os.path.join(TTS_DIR,'fp_'+sys.argv[2]); os.makedirs(OUT,exist_ok=True); dur={}; txt={}; sent={}
        for k,ss in D:
            parts=[]; pos=0; sent[k]=[]; SR=None
            for i,(sx,sp,st,g,pause) in enumerate(ss):
                y,SR=sf.read(os.path.join(src,f'{k}_{i}.wav')); y=y if y.ndim==1 else y.mean(1)
                if sys.argv[2]=='vc':                       # VC follows the source pitch loosely: pull each sentence to ~+5 % of the reference (clamped +-2.5 st)
                    import emph, fp_check_lib as C
                    p_=C.f0(y,SR)
                    if len(p_)>=15:
                        st_=float(np.clip(12*np.log2(C.REF*1.05/np.median(p_)),-2.5,2.5))
                        if abs(st_)>0.15: y=emph.shape(__import__('scipy.signal',fromlist=['x']).resample_poly(y,emph.SR,SR),st_,1.0,0.0); SR=emph.SR
                z=np.zeros(int(pause*SR)); parts+=[z,y]; pos+=len(z); sent[k].append([round(pos/SR,3),round((pos+len(y))/SR,3),sx.replace('*','')]); pos+=len(y)
            y=np.concatenate(parts); y=y/np.max(np.abs(y))*0.95; nz=np.where(np.abs(y)>0.01)[0]; y=y[:nz[-1]+1200]; sf.write(os.path.join(OUT,k+'.wav'),y,SR)
            dur[k]=round(len(y)/SR,2); txt[k]=' '.join(x[0].replace('*','') for x in ss); print(k,dur[k],txt[k])
        print('TOTAL',round(sum(dur.values()),2),'words',sum(len(t.split()) for t in txt.values()))
        json.dump({'text':txt,'dur':dur,'sent':sent},open(os.path.join(OUT,'script.json'),'w'),indent=1)
