"""Voice line for ONE APPLE (15 s TikTok cut, faster read). Writes $TTS_DIR/ap/N1_15.wav + script15.json.  Run: python tools/tts/ap15.py"""
import json, os, sys, subprocess, tempfile
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','tts'))
OUT=os.path.join(TTS_DIR,'ap'); os.makedirs(OUT,exist_ok=True)
RAW=os.path.join(tempfile.gettempdir(),'nk_tts_raw.wav')
k=Kokoro(f'{TTS_DIR}/kokoro-v1.0.int8.onnx',f'{TTS_DIR}/voices-v1.0.bin')
AF='rubberband=pitch=0.9,equalizer=f=120:t=q:w=1:g=3,acompressor=threshold=-20dB:ratio=3:makeup=4'      # channel narrator chain
TXT="Why can RPG heroes carry 99 swords... but not ONE apple?"
SPEED=float(sys.argv[1]) if len(sys.argv)>1 else 1.35
a,sr=k.create(TXT,voice='am_onyx',speed=SPEED,lang='en-us'); nz=np.where(np.abs(a)>0.01)[0]; a=a[max(0,nz[0]-240):nz[-1]+480]
sf.write(RAW,a,sr); p=os.path.join(OUT,'N1_15.wav')
subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',RAW,'-af',AF,'-ar','48000','-ac','1',p],check=True)
b,_=sf.read(p); nz=np.where(np.abs(b)>0.01)[0]; b=b[:nz[-1]+1200]; b=b/np.max(np.abs(b))*0.95; sf.write(p,b,48000)
d=round(len(b)/48000,2); print('N1',d,TXT)
json.dump({'text':{'N1':TXT},'dur':{'N1':d}},open(os.path.join(OUT,'script15.json'),'w'),indent=1)
