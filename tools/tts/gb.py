"""Voice lines for WHY DO GHOSTS SAY BOO? Narrator (calm British male) + the little ghost (af_sky, pitched up x1.2: small but still clear). Writes $TTS_DIR/gb/*.wav + script.json.  Run: python tools/tts/gb.py [narrator_speed]"""
import json, os, sys, subprocess, tempfile
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','tts'))
OUT=os.path.join(TTS_DIR,'gb'); os.makedirs(OUT,exist_ok=True); RAW=os.path.join(tempfile.gettempdir(),'nk_tts_raw.wav')
k=Kokoro(f'{TTS_DIR}/kokoro-v1.0.int8.onnx',f'{TTS_DIR}/voices-v1.0.bin')
L={'N1':("Why do ghosts always say boo?",3.0),'N2':("This little ghost had a problem.",2.1),'G1':("Excuse me?",1.4),'N3':("He tried asking nicely. Nobody listened.",4.0),'N4a':("So he tried knocking.",1.6),'N4b':("Still nothing.",1.4),
   'N5':("Then the lantern flickered... and the ghost panicked.",6.0),'N6':("He wasn't trying to haunt anyone. He just hated the dark.",7.0),'N7':("So he tried one last thing...",4.0),'G2':("BOO!",1.0),
   'N8':("The janitor ran... and left his lantern behind.",5.0),'N9':("Turns out, boo wasn't a threat.",4.0),'N10':("He just wanted a nightlight.",3.0)}   # (text, window in s)
SP=float(sys.argv[1]) if len(sys.argv)>1 else 1.0
dur={}; txt={}
for key,(t,win) in L.items():
    g=key.startswith('G'); a,sr=k.create(t.rstrip('.') if t.endswith('...') is False else t,voice='af_sky' if g else 'bm_george',speed=(0.8 if key=='G2' else 0.9) if g else SP,lang='en-gb' if not g else 'en-us')
    nz=np.where(np.abs(a)>0.01)[0]; a=a[max(0,nz[0]-240):nz[-1]+480]; sf.write(RAW,a,sr); p=os.path.join(OUT,key+'.wav')
    af='asetrate=%d,aresample=48000,highpass=f=140,equalizer=f=2500:t=q:w=1:g=3,acompressor=threshold=-24dB:ratio=3:makeup=4'%int(sr*1.2) if g else 'equalizer=f=180:t=q:w=1:g=2,acompressor=threshold=-22dB:ratio=2.5:makeup=3,aresample=48000'
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',RAW,'-af',af,'-ac','1',p],check=True)
    b,_=sf.read(p); nz=np.where(np.abs(b)>0.01)[0]; b=b[:nz[-1]+1200]; b=b/np.max(np.abs(b))*0.95; sf.write(p,b,48000)
    dur[key]=round(len(b)/48000,2); txt[key]=t; print(key,dur[key],'/',win,'' if dur[key]<=win else '  <-- TOO LONG',t)
json.dump({'text':txt,'dur':dur,'win':{k_:v[1] for k_,v in L.items()}},open(os.path.join(OUT,'script.json'),'w'),indent=1)
