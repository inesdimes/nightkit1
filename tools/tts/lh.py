"""Voice lines for WHY DO LIGHTHOUSES BLINK? One calm British narrator (same voice chain as gb.py). One file per sentence so shots can be cued to real timings.
Writes $TTS_DIR/mc/*.wav + script.json.  Run: python tools/tts/mc.py [speed]"""
import json, os, sys, subprocess, tempfile
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','tts'))
OUT=os.path.join(TTS_DIR,'lh'); os.makedirs(OUT,exist_ok=True); RAW=os.path.join(tempfile.gettempdir(),'nk_tts_raw_lh.wav')
k=Kokoro(f'{TTS_DIR}/kokoro-v1.0.int8.onnx',f'{TTS_DIR}/voices-v1.0.bin')
L=[('1a',"Why do lighthouses blink?",1.0),('1b',"One wrong choice sent this captain straight into the rocks.",1.05),
   ('2a',"Lost in thick fog, he spotted two lights.",1.0),('2b',"He followed the brighter, closer one.",1.0),('2c',"It looked so much safer.",0.95),
   ('3a',"But the fog suddenly cleared.",1.05),('3b',"A wall of jagged rocks filled his entire path.",1.05),
   ('4a',"He spun the wheel.",1.1),('4b',"The boat drifted. The rocks drew closer.",1.05),('4c',"He cut the throttle. It was too late.",1.0),
   ('5a',"His chart lay unread beside him.",1.0),('5b',"On it, one flash marked the headland.",1.0),('5c',"Two flashes marked the harbor.",1.0),
   ('6a',"But he never counted.",0.95),('6b',"The fog swallowed both lights.",0.95),('6c',"The engine coughed, and died.",0.95),('6d',"He was lost, and completely alone.",0.9),('6e',"No light. No sound. No way home.",0.9),
   ('7a',"Then the water moved.",0.85),
   ('8a',"Lighthouses blink so sailors can tell them apart.",0.92),('8b',"He never learned to read them.",0.88)]
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
