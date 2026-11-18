"""Voice lines for WHY DO CATS KNOCK THINGS OVER? (calm channel narrator). Writes $TTS_DIR/cs/N1..N5.wav + script.json.  Run: python tools/tts/cs.py [speed]"""
import json, os, sys, subprocess, tempfile
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','tts'))
OUT=os.path.join(TTS_DIR,'cs'); os.makedirs(OUT,exist_ok=True)
RAW=os.path.join(tempfile.gettempdir(),'nk_tts_raw.wav')
k=Kokoro(f'{TTS_DIR}/kokoro-v1.0.int8.onnx',f'{TTS_DIR}/voices-v1.0.bin')
AF='rubberband=pitch=0.9,equalizer=f=120:t=q:w=1:g=3,acompressor=threshold=-20dB:ratio=3:makeup=4'      # channel narrator chain
L={'N1':"Why do cats knock things over?",'N2':"Not to annoy you.",'N3':"They're testing something.",'N4':"A hidden food switch.",'N5':"And somehow... it works every time."}
SPEED=float(sys.argv[1]) if len(sys.argv)>1 else 1.0
dur={}
for key,txt in L.items():
    a,sr=k.create(txt,voice='am_onyx',speed=SPEED*(0.95 if key=='N5' else 1.0),lang='en-us'); nz=np.where(np.abs(a)>0.01)[0]; a=a[max(0,nz[0]-240):nz[-1]+480]
    sf.write(RAW,a,sr); p=os.path.join(OUT,key+'.wav')
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',RAW,'-af',AF,'-ar','48000','-ac','1',p],check=True)
    b,_=sf.read(p); nz=np.where(np.abs(b)>0.01)[0]; b=b[:nz[-1]+1200]; b=b/np.max(np.abs(b))*0.95; sf.write(p,b,48000)
    dur[key]=round(len(b)/48000,2); print(key,dur[key],txt)
json.dump({'text':L,'dur':dur},open(os.path.join(OUT,'script.json'),'w'),indent=1)
