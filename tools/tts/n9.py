import json, soundfile as sf, numpy as np, subprocess
from kokoro_onnx import Kokoro
k=Kokoro('/home/claude/tts/kokoro-v1.0.int8.onnx','/home/claude/tts/voices-v1.0.bin')
V={'H':('am_adam',1.08,'rubberband=pitch=1.02,acompressor=threshold=-20dB:ratio=3:makeup=4,aecho=0.8:0.6:40:0.15'),
   'T':('am_fenrir',0.98,'rubberband=pitch=0.78:formant=shifted,acompressor=threshold=-20dB:ratio=4:makeup=6,equalizer=f=110:t=q:w=1:g=5,aexciter=drive=6:blend=-2'),
   'A':('bm_george',0.72,'rubberband=pitch=0.78:formant=shifted,acompressor=threshold=-20dB:ratio=3:makeup=4'),
   'D':('af_sky',1.12,'rubberband=pitch=1.45:formant=shifted,acompressor=threshold=-20dB:ratio=3:makeup=4'),
   'C':('af_bella',1.15,'rubberband=pitch=1.3:formant=shifted,acompressor=threshold=-20dB:ratio=3:makeup=4')}
L=[("H1",0.25,"Tonight's question: how big was a T-Rex's... you-know-what?"),
("H2",5.6,"Scientists have two estimates."),
("H3",8.4,"Somewhere between a banana... and a car!"),
("T1",12.2,"Obviously, it's the car."),
("H4",15.0,"Not so fast! Let's ask your relatives!"),
("H5",18.0,"Alligator! You weigh hundreds of pounds."),
("A1",21.4,"Four inches."),
("H6",26.0,"Duck?"),
("D1",27.0,"Seven inches. Corkscrew."),
("T2",33.8,"That makes no sense!"),
("H7",35.6,"Size doesn't match body size. And soft tissue almost never fossilizes."),
("H8",40.4,"Nobody knows!"),
("T3",42.8,"Fine. I'm locking in... the car!"),
("H9",50.6,"And birds?"),
("C1",51.8,"Most of us ditched ours. Lighter for flying... probably."),
("T4",56.6,"You did WHAT?!")]
out=[]
for key,t0,txt in L:
    v,sp,af=V[key[0]]
    a,sr=k.create(txt,voice=v,speed=sp,lang='en-us'); nz=np.where(np.abs(a)>0.01)[0]; a=a[max(0,nz[0]-240):nz[-1]+480]
    sf.write('/tmp/claude-0/raw.wav',a,sr)
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i','/tmp/claude-0/raw.wav','-af',af,'-ar','48000','-ac','1',f'/home/claude/tts/v8/{key}.wav'],check=True)
    b,_=sf.read(f'/home/claude/tts/v8/{key}.wav')
    if key[0]=='T': b=np.tanh(2.6*b/np.max(np.abs(b)))/np.tanh(2.6)
    nz=np.where(np.abs(b)>0.01)[0]; b=b[:nz[-1]+2400]
    b=b/np.max(np.abs(b))*0.95; sf.write(f'/home/claude/tts/v8/{key}.wav',b,48000)
    d=round(len(b)/48000,2); out.append([key,t0,txt,d]); print(key,t0,d,round(t0+d,2),txt)
json.dump(out,open('/home/claude/tts/v8/script.json','w'))
