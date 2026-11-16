"""Voice lines for GUARD FORGETS (Experiment A 30 s / B 60 s share these). Writes $TTS_DIR/gf/<key>.wav + script.json.
Run: python tools/tts/gf.py [key ...]"""
import json, os, sys, subprocess, tempfile
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','tts'))
OUT=os.path.join(TTS_DIR,'gf'); os.makedirs(OUT,exist_ok=True)
RAW=os.path.join(tempfile.gettempdir(),'nk_tts_raw.wav')
k=Kokoro(f'{TTS_DIR}/kokoro-v1.0.int8.onnx',f'{TTS_DIR}/voices-v1.0.bin')
# N = channel narrator (same chain as Final Boss / Loot Restocker), G = dim but proud castle guard inside a big helmet
V={'N':('am_onyx',0.98,'rubberband=pitch=0.9,equalizer=f=120:t=q:w=1:g=3,acompressor=threshold=-20dB:ratio=3:makeup=4'),
   'G':('bm_lewis',1.0,'rubberband=pitch=0.9:formant=shifted,highpass=f=120,equalizer=f=1000:t=q:w=1:g=4,aecho=0.6:0.4:14:0.25,acompressor=threshold=-20dB:ratio=3:makeup=5')}
L={'N1':"Why do guards in video games forget you after ten seconds?",
   'G1':"Must've been the wind.",
   'G2':"HEY! STOP!",
   'G3':"Now I won't forget!",
   'G4':"I'm the thief?!"}
SPEED={'N1':1.13}                        # the hook line must fit in 3 s
for key in (sys.argv[1:] or list(L)):
    v,sp,af=V[key[0]]
    sp=SPEED.get(key,sp)
    a,sr=k.create(L[key],voice=v,speed=sp,lang='en-us'); nz=np.where(np.abs(a)>0.01)[0]; a=a[max(0,nz[0]-240):nz[-1]+480]
    sf.write(RAW,a,sr); p=os.path.join(OUT,f'{key}.wav')
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',RAW,'-af',af,'-ar','48000','-ac','1',p],check=True)
    b,_=sf.read(p); nz=np.where(np.abs(b)>0.01)[0]; b=b[:nz[-1]+1200]; b=b/np.max(np.abs(b))*0.95; sf.write(p,b,48000)
    print(key,round(len(b)/48000,2),L[key])
dur={key:round(sf.info(os.path.join(OUT,f'{key}.wav')).duration,2) for key in L if os.path.exists(os.path.join(OUT,f'{key}.wav'))}
json.dump({'text':L,'dur':dur},open(os.path.join(OUT,'script.json'),'w'),indent=1)
