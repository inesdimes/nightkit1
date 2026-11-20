"""Voice lines for ONE SMALL MISTAKE #01 "The Save That Killed Him" (sk). One British narrator (bm_george), calm.
Same format as l10.py: each sentence = (text, speed, pitch semitones, gain dB, pause before s); *word* = stressed (tools/tts/emph.py).
One wav per line in $TTS_DIR/sk/<key>.wav + script.json. Run: python tools/tts/sk.py [--voice bm_george]"""
import json, os, sys, argparse
import numpy as np, soundfile as sf
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import emph
from kokoro_onnx import Kokoro
ap=argparse.ArgumentParser(); ap.add_argument('--voice',default='bm_george'); ap.add_argument('--cut',default='30',choices=['30','15']); a=ap.parse_args()
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','tts'))
OUT=os.path.join(TTS_DIR,'sk' if a.cut=='30' else 'sk15'); os.makedirs(OUT,exist_ok=True)
DUR=f'{TTS_DIR}/kokoro-dur.onnx'
if not os.path.exists(DUR): emph.make_dur_model(f'{TTS_DIR}/kokoro-v1.0.int8.onnx',DUR)
k=Kokoro(DUR,f'{TTS_DIR}/voices-v1.0.bin'); SR=emph.SR
S=1.25  # base speed: the brief's 115 words are dense
D=[('1',[("The knight beat the final boss, but one *save* turned victory into a death sentence.",S,0.3,1.5,0)]),
   ('2',[("He had exactly *one* health point, and the poison timer was almost empty.",S,0,0.5,0)]),
   ('3',[("The crystal flashed save complete.",S,0.2,0.5,0),("Moments later, he dropped *dead* on the floor.",S,-0.3,0.5,0.12)]),
   ('4',[("He respawned with one health point.",S,0,0,0),("And the poison was *still* there.",S*0.97,-0.4,0.5,0.12)]),
   ('5',[("He ran.",S*1.05,0.3,0.5,0),("Dead.",S,-0.5,1.0,0.45),("Reached for a potion.",S*1.05,0.3,0,0.35),
         ("Too slow.",S,-0.2,0.5,0.3),("Dead again.",S,-0.6,1.0,0.4)]),   # pauses: the death loop must read on screen
   ('6',[("Wait.",S*0.95,1.0,0,0),("Why did every single restart kill him, over and over?",S,0.5,0,0.12)]),
   ('7',[("You see, the crystal saved his *poison* too, not just his hard-earned progress.",S,-0.3,1.0,0)]),
   ('8',[("There was only one terrible button left on the entire menu.",S,-0.2,0.5,0),("Delete save.",S*0.92,-0.5,1.5,0.15)]),
   ('9',[("Thirty hours of progress vanished.",S,-0.2,0.5,0),("He survived.",S,0.3,0.5,0.12),
         ("The final boss got a *second* chance.",S*0.95,-0.5,1.0,0.15)])]
# subtitle text per line (exactly the spoken words; UI words in caps)
SUB={'3':"The crystal flashed SAVE COMPLETE. Moments later, he dropped dead on the floor.",
     '8':"There was only one terrible button left on the entire menu. DELETE SAVE."}
if a.cut=='15':   # TikTok cut (python tools/tts/sk.py --cut 15 -> $TTS_DIR/sk15/), 55 words, a bit faster
    S=1.32
    D=[('1',[("One *save* turned the knight's victory into a death sentence.",S,0.3,1.5,0)]),
       ('2',[("He had one HP and a poison timer running out fast.",S,0,0.5,0)]),
       ('3',[("He saved anyway.",S,0.2,0.5,0),("Then *died*.",S,-0.5,1.0,0.35)]),
       ('4',[("Respawned.",S,0.2,0.5,0),("Died again.",S,-0.6,1.0,0.6)]),
       ('5',[("Wait, why?",S*0.95,1.0,0,0)]),
       ('6',[("You see, the checkpoint saved his *poison* too.",S,-0.3,1.0,0)]),
       ('7',[("His only escape was delete save.",S,-0.2,1.0,0)]),
       ('8',[("Thirty hours gone forever.",S,-0.3,0.5,0)]),
       ('9',[("And the final boss was *alive* again.",S*0.95,-0.5,1.0,0)])]
    SUB={'7':"His only escape was DELETE SAVE."}
def say(sx,sp,st,g):
    try: return emph.render(k,a.voice,sp,'en-gb',sx,pitch=st,gain=g)
    except ValueError as e:            # phonemizer merged words ("on the"): no word span -> render without the stress mark
        print('  no stress:',sx,'|',e); return emph.render(k,a.voice,sp,'en-gb',sx.replace('*',''),pitch=st,gain=g)
dur={}; txt={}; sent={}
for key,sents in D:
    parts=[]; pos=0; sent[key]=[]
    for sx,sp,st,g,pause in sents:
        z=np.zeros(int(pause*SR)); y_=emph.trim(say(sx,sp,st,g),0.01,120,360)
        parts+= [z,y_]; pos+=len(z); sent[key].append([round(pos/SR,3),round((pos+len(y_))/SR,3),sx.replace('*','')]); pos+=len(y_)
    y=np.concatenate(parts); y=y/np.max(np.abs(y))*0.95; nz=np.where(np.abs(y)>0.01)[0]; y=y[:nz[-1]+1200]; sf.write(os.path.join(OUT,key+'.wav'),y,SR)
    dur[key]=round(len(y)/SR,2); txt[key]=SUB.get(key,' '.join(x[0].replace('*','') for x in sents)); print(key,dur[key],txt[key])
print('TOTAL',round(sum(dur.values()),2),'words',sum(len(t.split()) for t in txt.values()))
json.dump({'text':txt,'dur':dur,'sent':sent},open(os.path.join(OUT,'script.json'),'w'),indent=1)
