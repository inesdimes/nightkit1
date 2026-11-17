"""Voice lines for SAFE ZONE (premium shop). Writes $TTS_DIR/sz/<key>.wav + script.json.  Run: python tools/tts/sz.py [key ...]"""
import json, os, sys, subprocess, tempfile
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','tts'))
OUT=os.path.join(TTS_DIR,'sz'); os.makedirs(OUT,exist_ok=True)
RAW=os.path.join(tempfile.gettempdir(),'nk_tts_raw.wav')
k=Kokoro(f'{TTS_DIR}/kokoro-v1.0.int8.onnx',f'{TTS_DIR}/voices-v1.0.bin')
# N = channel narrator, K = knight inside his helmet (same chain as Loot Restocker), S = cheerful old shopkeeper
V={'N':('am_onyx',1.08,'rubberband=pitch=0.9,equalizer=f=120:t=q:w=1:g=3,acompressor=threshold=-20dB:ratio=3:makeup=4'),
   'K':('am_michael',1.02,'highpass=f=180,lowpass=f=5200,equalizer=f=900:t=q:w=1:g=4,aecho=0.6:0.4:12:0.25,acompressor=threshold=-20dB:ratio=3:makeup=4'),
   'S':('bm_george',1.0,'rubberband=pitch=1.08:formant=shifted,equalizer=f=2500:t=q:w=1:g=2,acompressor=threshold=-20dB:ratio=3:makeup=4')}
L={'N1':"Why do monsters NEVER attack you inside shops?",
   'K1':"HA! YOU CAN'T TOUCH ME IN HERE!",
   'K2':"Free trial?",
   'S1':"Of course! Protection isn't free forever.",
   'S2':"I'll buy that rusty sword. And those boots!",
   'S3':"Ah! A premium customer.",
   'K3':"WAIT! YOU LET MONSTERS PAY TO ENTER?!",
   'S4':"Naturally. Everyone deserves good service.",
   'S5':"Would you like to upgrade?"}
for key in (sys.argv[1:] or list(L)):
    v,sp,af=V[key[0]]
    a,sr=k.create(L[key],voice=v,speed=sp,lang='en-us'); nz=np.where(np.abs(a)>0.01)[0]; a=a[max(0,nz[0]-240):nz[-1]+480]
    sf.write(RAW,a,sr); p=os.path.join(OUT,f'{key}.wav')
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',RAW,'-af',af,'-ar','48000','-ac','1',p],check=True)
    b,_=sf.read(p); nz=np.where(np.abs(b)>0.01)[0]; b=b[:nz[-1]+1200]; b=b/np.max(np.abs(b))*0.95; sf.write(p,b,48000)
    print(key,round(len(b)/48000,2),L[key])
dur={key:round(sf.info(os.path.join(OUT,f'{key}.wav')).duration,2) for key in L if os.path.exists(os.path.join(OUT,f'{key}.wav'))}
json.dump({'text':L,'dur':dur},open(os.path.join(OUT,'script.json'),'w'),indent=1)
