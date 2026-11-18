"""Voice lines for WHY DO MIRRORS COPY US? One calm British narrator (same voice chain as gb.py). One file per sentence so shots can be cued to real timings.
Writes $TTS_DIR/mc/*.wav + script.json.  Run: python tools/tts/mc.py [speed]"""
import json, os, sys, subprocess, tempfile
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','tts'))
OUT=os.path.join(TTS_DIR,'mc'); os.makedirs(OUT,exist_ok=True); RAW=os.path.join(tempfile.gettempdir(),'nk_tts_raw_mc.wav')
k=Kokoro(f'{TTS_DIR}/kokoro-v1.0.int8.onnx',f'{TTS_DIR}/voices-v1.0.bin')
L=[('1a',"Why do mirrors copy us?"),('1b',"This little robot thought he knew."),
   ('2a',"Every morning, he waved at his reflection."),('2b',"But today, the wave came back a second late."),
   ('3a',"He tried again."),('3b',"One arm up. One arm down."),('3c',"Somehow, the reflection kept getting further behind."),
   ('4a',"He tried a silly dance."),('4b',"Halfway through, his reflection froze with both arms in the air."),
   ('5a',"A message appeared on the glass: BREAK REQUESTED."),('5b',"The robot blinked."),('5c',"Wait... reflections can get tired?"),
   ('6a',"He waved again. Nothing."),('6b',"The figure on the other side lowered its arms and refused to move."),
   ('7a',"That was when he understood."),('7b',"The mirror wasn't magical."),('7c',"Someone inside had been copying him all day."),
   ('8a',"So, for once, he stood completely still and let his exhausted little reflection rest."),
   ('9a',"Then the reflection moved first."),('9b',"YOUR TURN."),('9c',"And he had to copy it.")]
SP=float(sys.argv[1]) if len(sys.argv)>1 else 1.0
dur={}; txt={}
for key,t in L:
    spoken=t.replace('BREAK REQUESTED','break requested').replace('YOUR TURN','your turn')
    a,sr=k.create(spoken,voice='bm_george',speed=SP,lang='en-gb')
    nz=np.where(np.abs(a)>0.01)[0]; a=a[max(0,nz[0]-240):nz[-1]+480]; sf.write(RAW,a,sr); p=os.path.join(OUT,key+'.wav')
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',RAW,'-af','equalizer=f=180:t=q:w=1:g=2,acompressor=threshold=-22dB:ratio=2.5:makeup=3,aresample=48000','-ac','1',p],check=True)
    b,_=sf.read(p); nz=np.where(np.abs(b)>0.01)[0]; b=b[:nz[-1]+1200]; b=b/np.max(np.abs(b))*0.95; sf.write(p,b,48000)
    dur[key]=round(len(b)/48000,2); txt[key]=t; print(key,dur[key],t)
print('TOTAL',round(sum(dur.values()),2),'words',sum(len(t.split()) for t in txt.values()))
json.dump({'text':txt,'dur':dur},open(os.path.join(OUT,'script.json'),'w'),indent=1)
