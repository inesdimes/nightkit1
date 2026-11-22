"""Placeholder voice for the mechanism-style mimic test (Kokoro bm_george, four_phases pace: speed 1.22, short pauses).
The PC can replace these files with the Enes-timbre VC / own-voice versions (same keys). Writes $TTS_DIR/mmx/<key>.wav + script.json."""
import os, sys, json
import numpy as np, soundfile as sf
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','tts'))
import emph
from kokoro_onnx import Kokoro
TTS=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','tts')); OUT=os.path.join(TTS,'mmx'); os.makedirs(OUT,exist_ok=True)
DUR=os.path.join(TTS,'kokoro-dur.onnx')
if not os.path.exists(DUR): emph.make_dur_model(os.path.join(TTS,'kokoro-v1.0.int8.onnx'),DUR)
k=Kokoro(DUR,os.path.join(TTS,'voices-v1.0.bin')); S=1.22
L=[('1',["Why do mimics pretend to be chests?"]),('2',["This chest was opened by every hero for a hundred years."]),
   ('3',["They always took something.","Nobody ever put anything back."]),('4',["One day, it learned to bite."]),
   ('5',["Then a knight opened it,","and didn't draw his sword."]),('6',["He took nothing.","He left a coin."]),
   ('7',["For the first time in a hundred years,","something was given back."])]
dur={}; txt={}
for key,sents in L:
    parts=[]
    for i,s in enumerate(sents):
        if i: parts.append(np.zeros(int(0.12*emph.SR)))
        parts.append(emph.trim(emph.render(k,'bm_george',S,'en-gb',s,pitch=-0.6),0.01,120,360))
    y=np.concatenate(parts); y=y/np.max(np.abs(y))*0.95; sf.write(os.path.join(OUT,key+'.wav'),y,emph.SR)
    dur[key]=round(len(y)/emph.SR,2); txt[key]=' '.join(sents); print(key,dur[key],txt[key])
json.dump({'text':txt,'dur':dur},open(os.path.join(OUT,'script.json'),'w'),indent=1); print('total',round(sum(dur.values()),2))
