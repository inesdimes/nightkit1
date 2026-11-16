import json, soundfile as sf, numpy as np, subprocess
from kokoro_onnx import Kokoro
k=Kokoro('/home/claude/tts/kokoro-v1.0.int8.onnx','/home/claude/tts/voices-v1.0.bin')
V={'T':('am_fenrir',0.95,'rubberband=pitch=0.78:formant=shifted,acompressor=threshold=-20dB:ratio=4:makeup=6,equalizer=f=110:t=q:w=1:g=5,aexciter=drive=6:blend=-2'),
   'S':('am_puck',1.0,'rubberband=pitch=1.07,acompressor=threshold=-20dB:ratio=3:makeup=4')}
out=json.load(open('/home/claude/tts/v7/script.json'))
for key,t0,txt in (("TH1",-5.4,"Doc... how big was it?!"),("SD0",-3.55,"H-how big was... what?")):
    v,sp,af=V[key[0]]
    a,sr=k.create(txt,voice=v,speed=sp,lang='en-us'); nz=np.where(np.abs(a)>0.01)[0]; a=a[max(0,nz[0]-240):nz[-1]+480]
    sf.write('/tmp/claude-0/raw.wav',a,sr)
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i','/tmp/claude-0/raw.wav','-af',af,'-ar','48000','-ac','1',f'/home/claude/tts/v7/{key}.wav'],check=True)
    b,_=sf.read(f'/home/claude/tts/v7/{key}.wav')
    if key[0]=='T': b=np.tanh(2.6*b/np.max(np.abs(b)))/np.tanh(2.6)
    b=b/np.max(np.abs(b))*0.95; sf.write(f'/home/claude/tts/v7/{key}.wav',b,48000)
    d=round(len(b)/48000,2); out=[o for o in out if o[0]!=key]+[[key,t0,txt,d]]; print(key,t0,d,round(t0+d,2))
json.dump(out,open('/home/claude/tts/v7/script.json','w'))
