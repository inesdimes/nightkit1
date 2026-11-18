"""Voice lines for THE CAMERA UNDER MY BED: five dry documentary narrator lines + the duplicate's whisper.
Writes $TTS_DIR/cb/N1..N5.wav, W1.wav (whisper) and script.json.  Run: python tools/tts/cb.py [speed]"""
import json, os, sys, subprocess, tempfile
import numpy as np, soundfile as sf
from scipy import signal
from kokoro_onnx import Kokoro
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','tts'))
OUT=os.path.join(TTS_DIR,'cb'); os.makedirs(OUT,exist_ok=True)
RAW=os.path.join(tempfile.gettempdir(),'nk_tts_raw.wav')
k=Kokoro(f'{TTS_DIR}/kokoro-v1.0.int8.onnx',f'{TTS_DIR}/voices-v1.0.bin')
L={'N1':"Someone was watching him sleep... from under his bed.",'N2':"The camera wasn't supposed to be there.",'N3':"He checked underneath. Nothing.",
   'N4':"Then he realized... he was still asleep.",'N5':"And then... the other him woke up."}
SPEED=float(sys.argv[1]) if len(sys.argv)>1 else 0.92
AF='highpass=f=70,equalizer=f=3000:t=q:w=1:g=-2,acompressor=threshold=-24dB:ratio=3:makeup=3'      # flat, dry, no reverb
dur={}
def clean(a): nz=np.where(np.abs(a)>0.01)[0]; return a[max(0,nz[0]-240):nz[-1]+480]
for key,txt in L.items():
    a,sr=k.create(txt,voice='bm_george',speed=SPEED,lang='en-gb'); a=clean(a)
    sf.write(RAW,a,sr); p=os.path.join(OUT,key+'.wav')
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',RAW,'-af',AF,'-ar','48000','-ac','1',p],check=True)
    b,_=sf.read(p); nz=np.where(np.abs(b)>0.01)[0]; b=b[:nz[-1]+1200]; b=b/np.max(np.abs(b))*0.95; sf.write(p,b,48000)
    dur[key]=round(len(b)/48000,2); print(key,dur[key],txt)
# ---- the whisper: speech envelope on band-limited noise (a real whisper has no voiced pitch) ----
a,sr=k.create("He's awake.",voice='am_adam',speed=0.8,lang='en-us'); a=clean(a)
f,t,Z=signal.stft(a,sr,nperseg=1024,noverlap=768); mag=np.abs(Z)
rng=np.random.default_rng(5); ph=np.exp(1j*rng.uniform(0,2*np.pi,Z.shape)); _,w=signal.istft(mag*ph,sr,nperseg=1024,noverlap=768)
sos=signal.butter(4,[400,7500],'bandpass',fs=sr,output='sos'); w=signal.sosfilt(sos,w)
w=signal.resample_poly(w,48000,sr) if sr!=48000 else w
w=w[:int(len(w))]; nz=np.where(np.abs(w)>0.02*np.max(np.abs(w)))[0]; w=w[max(0,nz[0]-480):nz[-1]+960]; w=w/np.max(np.abs(w))*0.6
sf.write(os.path.join(OUT,'W1.wav'),w,48000); dur['W1']=round(len(w)/48000,2); print('W1',dur['W1'],"He's awake. (whisper)")
json.dump({'text':dict(L,W1="He's awake."),'dur':dur},open(os.path.join(OUT,'script.json'),'w'),indent=1)
