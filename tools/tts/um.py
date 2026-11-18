"""Voice lines for THE SMALLEST UMBRELLA (warm female narrator). Writes $TTS_DIR/um/N1..N3.wav + script.json.  Run: python tools/tts/um.py [speed]"""
import json, os, sys, subprocess, tempfile
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','tts'))
OUT=os.path.join(TTS_DIR,'um'); os.makedirs(OUT,exist_ok=True)
RAW=os.path.join(tempfile.gettempdir(),'nk_tts_raw.wav')
k=Kokoro(f'{TTS_DIR}/kokoro-v1.0.int8.onnx',f'{TTS_DIR}/voices-v1.0.bin')
L={'N1':"This tiny duck saw a dog freezing in the rain.",'N2':"So he offered his umbrella.",'N3':"There was just one problem...",'N4':"It only covered his nose!",'N5':"So the dog gave him a ride.",'N6':"Best friends!"}
SPEED=float(sys.argv[1]) if len(sys.argv)>1 else 0.9
AF='equalizer=f=200:t=q:w=1:g=2,acompressor=threshold=-22dB:ratio=2.5:makeup=3'
dur={}
for key,txt in L.items():
    a,sr=k.create(txt.lstrip('.'),voice='af_heart',speed=SPEED,lang='en-us'); nz=np.where(np.abs(a)>0.01)[0]; a=a[max(0,nz[0]-240):nz[-1]+480]
    sf.write(RAW,a,sr); p=os.path.join(OUT,key+'.wav')
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',RAW,'-af',AF,'-ar','48000','-ac','1',p],check=True)
    b,_=sf.read(p); nz=np.where(np.abs(b)>0.01)[0]; b=b[:nz[-1]+1200]; b=b/np.max(np.abs(b))*0.95; sf.write(p,b,48000)
    dur[key]=round(len(b)/48000,2); print(key,dur[key],txt)
json.dump({'text':L,'dur':dur},open(os.path.join(OUT,'script.json'),'w'),indent=1)
