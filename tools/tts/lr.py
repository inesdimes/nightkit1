"""Voice lines for THE LOOT RESTOCKER (Experiment A 30 s / B 60 s share these). Writes $TTS_DIR/lr/<key>.wav + script.json.
Run: python tools/tts/lr.py [key ...]   (no args = all lines)"""
import json, os, sys, subprocess, tempfile
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','tts'))
OUT=os.path.join(TTS_DIR,'lr'); os.makedirs(OUT,exist_ok=True)
RAW=os.path.join(tempfile.gettempdir(),'nk_tts_raw.wav')
k=Kokoro(f'{TTS_DIR}/kokoro-v1.0.int8.onnx',f'{TTS_DIR}/voices-v1.0.bin')
# N = channel narrator (same chain as Final Boss), K = knight (inside a helmet), G = tired little goblin
V={'N':('am_onyx',0.98,'rubberband=pitch=0.9,equalizer=f=120:t=q:w=1:g=3,acompressor=threshold=-20dB:ratio=3:makeup=4'),
   'K':('am_michael',1.0,'highpass=f=180,lowpass=f=5200,equalizer=f=900:t=q:w=1:g=4,aecho=0.6:0.4:12:0.25,acompressor=threshold=-20dB:ratio=3:makeup=4'),
   'G':('am_puck',0.86,'rubberband=pitch=1.38:formant=shifted,acompressor=threshold=-20dB:ratio=3:makeup=5')}
L={'N1':"Who refills all the treasure chests in video games?",
   'K1':["Wait...",0.32,"YOU fill these?"],             # list = parts joined with pauses (s)
   'G1':["Every.",0.38,"Single.",0.38,"One."],
   'K2':"I'll help with one.",
   'N2':"The last person who asked."}
def text(v): return ' '.join(x for x in v if isinstance(x,str)) if isinstance(v,list) else v
sr=24000
for key in (sys.argv[1:] or list(L)):
    v,sp,af=V[key[0]]
    parts=L[key] if isinstance(L[key],list) else [L[key]]; chunks=[]
    for p_ in parts:
        if isinstance(p_,(int,float)): chunks.append(np.zeros(int(p_*sr))); continue
        a,sr=k.create(p_,voice=v,speed=sp,lang='en-us'); nz=np.where(np.abs(a)>0.01)[0]; chunks.append(a[max(0,nz[0]-240):nz[-1]+480])
    a=np.concatenate(chunks)
    sf.write(RAW,a,sr); p=os.path.join(OUT,f'{key}.wav')
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',RAW,'-af',af,'-ar','48000','-ac','1',p],check=True)
    b,_=sf.read(p); nz=np.where(np.abs(b)>0.01)[0]; b=b[:nz[-1]+1200]; b=b/np.max(np.abs(b))*0.95; sf.write(p,b,48000)
    print(key,round(len(b)/48000,2),text(L[key]))
dur={key:round(sf.info(os.path.join(OUT,f'{key}.wav')).duration,2) for key in L if os.path.exists(os.path.join(OUT,f'{key}.wav'))}
json.dump({'text':{k_:text(v) for k_,v in L.items()},'dur':dur},open(os.path.join(OUT,'script.json'),'w'),indent=1)
