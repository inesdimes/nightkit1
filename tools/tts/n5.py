import json, soundfile as sf, numpy as np
from kokoro_onnx import Kokoro
import os, tempfile
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','tts'))   # Kokoro models + generated voice lines live here
k=Kokoro(f'{TTS_DIR}/kokoro-v1.0.int8.onnx',f'{TTS_DIR}/voices-v1.0.bin')
L=[("L1",0.3,"This is me."),("L2",2.3,"And that... is also me."),
("L3",5.9,"Nine HP. No potions. No way back."),("L4",9.9,"Then I saw the red light. A save point."),
("L5",14.3,"I made it. I was safe."),("L6",20.8,"Game saved. I could finally rest."),
("L7",23.3,"Then I heard footsteps."),("L8",25.4,"But I was the only player here."),
("L9",31.1,"Same crack."),("L10",32.3,"Same cloth."),("L11",33.7,"Whatever I did... it did."),
("L12",36.0,"So I stopped."),("L13",37.25,"It didn't."),("L14",38.3,"And my body followed it."),
("L15",40.7,"It walked to my save point."),("L16",43.7,"It didn't press save."),
("L17",49.1,"When you load a save... the old you has to go somewhere."),("L18",52.9,"Now it plays as me."),("L19",54.3,"And I'm not the first.")]
out=[]
for key,t0,txt in L:
    a,sr=k.create(txt,voice='am_michael',speed=0.92,lang='en-us')
    nz=np.where(np.abs(a)>0.01)[0]; a=a[max(0,nz[0]-240):nz[-1]+480]
    sf.write(f'{TTS_DIR}/v5/{key}.wav',a,sr); d=len(a)/sr; out.append([key,t0,txt,round(d,2)]); print(key,t0,round(d,2),round(t0+d,2),txt)
json.dump(out,open(f'{TTS_DIR}/v5/script.json','w'))
