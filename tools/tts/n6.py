import json, soundfile as sf, numpy as np
from kokoro_onnx import Kokoro
k=Kokoro('/home/claude/tts/kokoro-v1.0.int8.onnx','/home/claude/tts/voices-v1.0.bin')
L=[("N1",0.12,"He picked a fight with one NPC... and accidentally activated the entire street.","am_michael",1.13),
("N2",5.2,"Downtown. Rush hour. Nobody looks up.","am_michael",0.95),
("N3",8.4,"He blocked the crosswalk. Every time they moved... so did he.","am_michael",0.98),
("N4",12.4,"People walked past. Nobody wanted a side quest.","am_michael",0.98),
("C1",15.9,"Leave them alone.","am_liam",0.95),
("B1",17.15,"Stay out of it.","am_onyx",0.95),
("N5",19.6,"One stranger said no. And that changed everything.","am_michael",0.98),
("N6",22.9,"Then the light turned green.","am_michael",0.98),
("N7",25.6,"A taxi driver saw everything... and refused to move.","am_michael",0.98),
("N8",29.6,"Suddenly, the street was paying attention.","am_michael",0.98),
("N9",36.6,"One became two. Two became four.","am_michael",0.95),
("N10",40.4,"And for the first time... he was the one outnumbered.","am_michael",0.95),
("N11",46.4,"No fight. No damage. He just walked away.","am_michael",0.93),
("N12",50.2,"They walked the stranger all the way to the sidewalk.","am_michael",0.93),
("N13",53.6,"Sometimes, the whole street is on your team.","am_michael",0.9)]
out=[]
for key,t0,txt,v,sp in L:
    a,sr=k.create(txt,voice=v,speed=sp,lang='en-us')
    nz=np.where(np.abs(a)>0.01)[0]; a=a[max(0,nz[0]-240):nz[-1]+480]
    sf.write(f'/home/claude/tts/v6/{key}.wav',a,sr); d=round(len(a)/sr,2); out.append([key,t0,txt,d,v]); print(key,t0,d,round(t0+d,2),txt)
json.dump(out,open('/home/claude/tts/v6/script.json','w'))
