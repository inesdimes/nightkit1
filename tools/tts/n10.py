import json, soundfile as sf, numpy as np, subprocess
from kokoro_onnx import Kokoro
import os, tempfile
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','tts'))   # Kokoro models + generated voice lines live here
RAW=os.path.join(tempfile.gettempdir(),'nk_tts_raw.wav')
k=Kokoro(f'{TTS_DIR}/kokoro-v1.0.int8.onnx',f'{TTS_DIR}/voices-v1.0.bin')
V={'P':('af_bella',1.1,'rubberband=pitch=1.06,acompressor=threshold=-20dB:ratio=3:makeup=4'),
   'N':('af_bella',1.0,'rubberband=pitch=1.06,acompressor=threshold=-20dB:ratio=3:makeup=4'),
   'C':('am_puck',1.08,'rubberband=pitch=1.22:formant=shifted,acompressor=threshold=-20dB:ratio=3:makeup=5'),
   'S':('am_onyx',0.72,'rubberband=pitch=0.8:formant=shifted,acompressor=threshold=-20dB:ratio=3:makeup=5,aecho=0.7:0.5:60:0.2')}
L=[("C0",0.55,"Heh heh heh heh!"),
("P1",1.55,"Why does a chest want my money?!"),
("N1",5.0,"I found a secret pirate vault."),
("N2",7.4,"And everything was supposed to be free."),
("C1",13.4,"Congratulations! You've unlocked my shop!"),
("P2",23.2,"You said it was free!"),
("C2",25.0,"The access is free."),
("C3",40.6,"Wonderful! Just one more gold for the processing fee."),
("P3",45.4,"Actually... I have one thing left to sell."),
("S1",55.4,"Is the treasure... free?"),
("C4",58.0,"The access is.")]
out=[]
for key,t0,txt in L:
    v,sp,af=V[key[0]]
    a,sr=k.create(txt,voice=v,speed=sp,lang='en-us'); nz=np.where(np.abs(a)>0.01)[0]; a=a[max(0,nz[0]-240):nz[-1]+480]
    sf.write(RAW,a,sr)
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',RAW,'-af',af,'-ar','48000','-ac','1',f'{TTS_DIR}/v9/{key}.wav'],check=True)
    b,_=sf.read(f'{TTS_DIR}/v9/{key}.wav'); nz=np.where(np.abs(b)>0.01)[0]; b=b[:nz[-1]+2400]
    b=b/np.max(np.abs(b))*0.95; sf.write(f'{TTS_DIR}/v9/{key}.wav',b,48000)
    d=round(len(b)/48000,2); out.append([key,t0,txt,d]); print(key,t0,d,round(t0+d,2),txt)
json.dump(out,open(f'{TTS_DIR}/v9/script.json','w'))
