"""Voice lines for THE LAST 10 SECONDS, ep. 1 "The Dungeon Collapse" (l10). One British narrator (bm_george). Kokoro has no emotion or stress control, so each sentence carries
a DIRECTION (speed, pitch in semitones, gain in dB, pause before) and WORD STRESS marks: *word* = stressed, **word** = strongly stressed
(tools/tts/emph.py: the whole sentence is spoken naturally; only the stressed word is made slower, higher and louder, using exact phoneme timings). Edit the table, run, listen.
One wav per line in $TTS_DIR/lm/<key>.wav + script.json. Run: python tools/tts/lm.py [--voice bm_george]
A line that overflows its window is time-compressed (pitch kept) up to 1.18x; beyond that the script warns."""
import json, os, sys, subprocess, tempfile, argparse
import numpy as np, soundfile as sf
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import emph
from kokoro_onnx import Kokoro
ap=argparse.ArgumentParser(); ap.add_argument('--voice',default='bm_george'); a=ap.parse_args()
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','tts'))
OUT=os.path.join(TTS_DIR,'l10'); os.makedirs(OUT,exist_ok=True); TMP=tempfile.gettempdir()
DUR=f'{TTS_DIR}/kokoro-dur.onnx'
if not os.path.exists(DUR): emph.make_dur_model(f'{TTS_DIR}/kokoro-v1.0.int8.onnx',DUR)    # same model + a duration output
k=Kokoro(DUR,f'{TTS_DIR}/voices-v1.0.bin'); SR=emph.SR
# (key, [(sentence, speed, pitch semitones, gain dB, pause before s), ...])
D=[('1',[("He had ten seconds to escape the dungeon, and he spent four of them looting.",0.97,0.3,1.5,0)]),
   ('2',[("The ceiling is crumbling.",1.0,-0.3,1.0,0),("The exit is forty steps away.",1.0,0,0,0.1)]),
   ('3',[("He grabs one chest.",1.0,0,0,0),("Overencumbered.",0.95,-0.5,1.0,0.1),("His speed drops to almost nothing.",1.0,0,0,0.1)]),
   ('4',[("So he swaps it for a smaller chest.",1.05,0,0,0),("Still too heavy.",0.95,-0.4,0.5,0.1)]),
   ('5',[("Wait.",0.95,1.0,0,0),("Why doesn't he just drop everything and run?",1.0,0.5,0,0.1)]),
   ('6',[("You see, losing something hurts twice as much as gaining it feels good.",1.0,-0.3,1.0,0),("Scientists call it loss aversion.",0.98,-0.3,0.5,0.1)]),
   ('7',[("So he drops his loot one item at a time.",1.08,0.3,0.5,0),("Every drop costs him a second.",1.0,-0.2,0.5,0.1)]),
   ('8',[("Finally, he lets go of everything and sprints.",1.12,0.8,2.0,0)]),
   ('9',[("The floor collapses behind every step.",1.1,0.6,2.0,0)]),
   ('10',[("The door is locked.",0.95,-0.6,1.0,0),("The key was in the first chest.",0.95,-0.4,0.5,0.15)]),
   ('11',[("He kicks it open with one second left.",1.1,0.8,2.5,0)]),
   ('12',[("He escapes with zero gold, zero swords, and one apple.",0.97,0,1.0,0)]),
   ('13',[("It was the only thing the game let him carry.",0.93,-0.5,0.5,0)])]
def fit(y,maxlen):
    r=len(y)/SR/maxlen
    if r<=1.0: return y,1.0
    r=min(r,1.18); p=os.path.join(TMP,'nk_lm_f.wav'); q=os.path.join(TMP,'nk_lm_g.wav'); sf.write(p,y,SR)
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',p,'-af',f'rubberband=tempo={r:.4f}','-ar',str(SR),'-ac','1',q],check=True)
    z,_=sf.read(q); return z,r
dur={}; txt={}
for key,sents in D:
    parts=[]
    for sx,sp,st,g,pause in sents:
        parts.append(np.zeros(int(pause*SR))); parts.append(emph.trim(emph.render(k,a.voice,sp,'en-gb',sx,pitch=st,gain=g),0.01,120,360))
    y=np.concatenate(parts); y=y/np.max(np.abs(y))*0.95; nz=np.where(np.abs(y)>0.01)[0]; y=y[:nz[-1]+1200]; sf.write(os.path.join(OUT,key+'.wav'),y,SR)
    dur[key]=round(len(y)/SR,2); txt[key]=' '.join(x[0] for x in sents); print(key,dur[key],txt[key])
print('TOTAL',round(sum(dur.values()),2),'words',sum(len(t.split()) for t in txt.values()))
json.dump({'text':txt,'dur':dur},open(os.path.join(OUT,'script.json'),'w'),indent=1)
