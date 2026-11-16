"""Voice lines for FINAL BOSS (Experiment A/B share these). Writes $TTS_DIR/fb/<key>.wav + script.json.
Run: python tools/tts/fb.py [key ...]   (no args = all lines)"""
import json, os, sys, subprocess, tempfile
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','tts'))
OUT=os.path.join(TTS_DIR,'fb'); os.makedirs(OUT,exist_ok=True)
RAW=os.path.join(tempfile.gettempdir(),'nk_tts_raw.wav')
k=Kokoro(f'{TTS_DIR}/kokoro-v1.0.int8.onnx',f'{TTS_DIR}/voices-v1.0.bin')
# narrator: deep + mysterious; boss: huge, slow, echoing
V={'N':('am_onyx',0.98,'rubberband=pitch=0.9,equalizer=f=120:t=q:w=1:g=3,acompressor=threshold=-20dB:ratio=3:makeup=4'),
   'B':('am_fenrir',0.82,'rubberband=pitch=0.7:formant=shifted,equalizer=f=90:t=q:w=1:g=5,acompressor=threshold=-22dB:ratio=4:makeup=6,aecho=0.8:0.6:70|140:0.25|0.12')}
L={'N1':"Why do final bosses never leave their rooms?",
   'N2':"A knight opens the final arena.",
   'N3':"The boss whispers,",
   'B1':"You finally came.",
   'N4':"The gate slams shut.",
   'N5':"But instead of fighting, the boss walks straight out.",
   'N6':"The knight runs after him... and hits an invisible wall.",
   'N7':"One must remain.",
   'N8':"A new health bar appears: Final Boss.",
   'N9':"He wasn't waiting to fight you.",
   'N10':"He was waiting to be replaced."}
keys=sys.argv[1:] or list(L)
for key in keys:
    v,sp,af=V[key[0]]
    a,sr=k.create(L[key],voice=v,speed=sp,lang='en-us'); nz=np.where(np.abs(a)>0.01)[0]; a=a[max(0,nz[0]-240):nz[-1]+480]
    sf.write(RAW,a,sr); p=os.path.join(OUT,f'{key}.wav')
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',RAW,'-af',af,'-ar','48000','-ac','1',p],check=True)
    b,_=sf.read(p); nz=np.where(np.abs(b)>0.01)[0]; b=b[:nz[-1]+1200]; b=b/np.max(np.abs(b))*0.95; sf.write(p,b,48000)
    print(key,round(len(b)/48000,2),L[key])
dur={}
for key in L:
    p=os.path.join(OUT,f'{key}.wav')
    if os.path.exists(p): dur[key]=round(sf.info(p).duration,2)
json.dump({'text':L,'dur':dur},open(os.path.join(OUT,'script.json'),'w'),indent=1)
