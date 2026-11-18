"""Voice lines for WHY DO MIRRORS COPY US? v2 (tighter ~32 s cut). One calm British narrator (same voice chain as gb.py). One file per sentence so shots can be cued to real timings.
Writes $TTS_DIR/mc/*.wav + script.json.  Run: python tools/tts/mc.py [speed]"""
import json, os, sys, subprocess, tempfile
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','tts'))
OUT=os.path.join(TTS_DIR,'mc2'); os.makedirs(OUT,exist_ok=True); RAW=os.path.join(tempfile.gettempdir(),'nk_tts_raw_mc2.wav')
k=Kokoro(f'{TTS_DIR}/kokoro-v1.0.int8.onnx',f'{TTS_DIR}/voices-v1.0.bin')
L=[('1a',"Why do mirrors copy us?",1.0),('1b',"Today, his reflection was a second late.",1.0),('2a',"He tried harder. Arms up. Arms down. Still behind.",1.0),('2b',"Then it froze.",0.95),
   ('3a',"A message appeared: BREAK REQUESTED.",1.0),('3b',"Wait... reflections get tired?",0.95),('4a',"He waved again. Nothing.",1.0),
   ('5a',"The mirror wasn't magic.",0.95),('5b',"Someone inside had been copying him all day.",0.95),('6a',"So he stood still, and let it rest.",0.9),
   ('7a',"Then the reflection moved first.",1.0),('7b',"YOUR TURN.",0.9),('7c',"Even your reflection deserves a day off.",0.88)]
SP=float(sys.argv[1]) if len(sys.argv)>1 else 1.0
dur={}; txt={}
for key,t,sp_ in L:
    spoken=t.replace('BREAK REQUESTED','break requested').replace('YOUR TURN','your turn')
    a,sr=k.create(spoken,voice='bm_george',speed=SP*sp_,lang='en-gb')
    nz=np.where(np.abs(a)>0.01)[0]; a=a[max(0,nz[0]-240):nz[-1]+480]; sf.write(RAW,a,sr); p=os.path.join(OUT,key+'.wav')
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',RAW,'-af','equalizer=f=180:t=q:w=1:g=2,acompressor=threshold=-22dB:ratio=2.5:makeup=3,aresample=48000','-ac','1',p],check=True)
    b,_=sf.read(p); nz=np.where(np.abs(b)>0.01)[0]; b=b[:nz[-1]+1200]; b=b/np.max(np.abs(b))*0.95; sf.write(p,b,48000)
    dur[key]=round(len(b)/48000,2); txt[key]=t; print(key,dur[key],t)
print('TOTAL',round(sum(dur.values()),2),'words',sum(len(t.split()) for t in txt.values()))
json.dump({'text':txt,'dur':dur},open(os.path.join(OUT,'script.json'),'w'),indent=1)
