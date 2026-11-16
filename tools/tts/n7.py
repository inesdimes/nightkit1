import json, soundfile as sf, numpy as np, subprocess
from kokoro_onnx import Kokoro
k=Kokoro('/home/claude/tts/kokoro-v1.0.int8.onnx','/home/claude/tts/voices-v1.0.bin')
V={'T':('am_fenrir',1.0,'rubberband=pitch=0.78:formant=shifted,acompressor=threshold=-20dB:ratio=4:makeup=6,equalizer=f=110:t=q:w=1:g=5,aexciter=drive=6:blend=-2'),
   'S':('am_puck',1.18,'rubberband=pitch=1.07,acompressor=threshold=-20dB:ratio=3:makeup=4'),
   'B':('af_sky',1.1,'rubberband=pitch=1.4:formant=shifted,acompressor=threshold=-20dB:ratio=3:makeup=4'),
   'C':('bm_george',0.78,'rubberband=pitch=0.8:formant=shifted,acompressor=threshold=-20dB:ratio=3:makeup=4')}
L=[("T1",0.15,"Doc! How big was it?!"),("S1",5.3,"Twenty years! Every bone, every tooth, every claw!"),
("T2",11.4,"You rebuilt everything... except that?!"),("S2",15.4,"We only found your bones! Soft tissue rarely survives!"),
("T3",21.9,"Then ask my relatives!"),("B1",31.1,"Don't look at me. Most birds don't even have one."),
("C1",34.6,"We do. ... Doesn't help you."),("S3",40.1,"We can only guess."),("T4",41.6,"Then I'll pick my own size!"),
("T5",53.1,"So... nobody actually knows?"),("T6",56.6,"Then why did you give me eyebrows?!")]
out=[]
for key,t0,txt in L:
    v,sp,af=V[key[0]]
    a,sr=k.create(txt,voice=v,speed=sp,lang='en-us'); nz=np.where(np.abs(a)>0.01)[0]; a=a[max(0,nz[0]-240):nz[-1]+480]
    sf.write('/tmp/claude-0/raw.wav',a,sr)
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i','/tmp/claude-0/raw.wav','-af',af,'-ar','48000','-ac','1',f'/home/claude/tts/v7/{key}.wav'],check=True)
    b,_=sf.read(f'/home/claude/tts/v7/{key}.wav')
    if key[0]=='T':          # dino growl: sub-octave + soft clip
        sub=np.sign(np.sin(np.cumsum(np.ones(len(b)))*0))  # placeholder no-op
        b=np.tanh(2.6*b/np.max(np.abs(b)))/np.tanh(2.6)
    b=b/np.max(np.abs(b))*0.95; sf.write(f'/home/claude/tts/v7/{key}.wav',b,48000)
    d=round(len(b)/48000,2); out.append([key,t0,txt,d]); print(key,t0,d,round(t0+d,2),txt)
json.dump(out,open('/home/claude/tts/v7/script.json','w'))
