"""Voice lines for THE LIGHTNING MISSED (lm). One British narrator (bm_george). Kokoro has no emotion or stress control, so each sentence carries
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
OUT=os.path.join(TTS_DIR,'lm'); os.makedirs(OUT,exist_ok=True); TMP=tempfile.gettempdir()
DUR=f'{TTS_DIR}/kokoro-dur.onnx'
if not os.path.exists(DUR): emph.make_dur_model(f'{TTS_DIR}/kokoro-v1.0.int8.onnx',DUR)    # same model + a duration output
k=Kokoro(DUR,f'{TTS_DIR}/voices-v1.0.bin'); SR=emph.SR
# (key, window start, latest end, [(sentence with *stress* marks, speed, pitch semitones, gain dB, pause before s), ...])
D=[('1',0.25,4.50,[("The lightning *misses* the knight, but his health bar drops by **half**.",1.0,0.4,1.5,0)]),
   ('2',4.57,8.10,[("His shield is *untouched*.",1.0,-0.3,0,0),("The **pillar** took the hit.",1.05,0.6,1.0,0.1)]),
   ('3',8.16,12.80,[("He **runs**.",1.2,1.2,2.0,0),("Another bolt lands *behind* him!",1.15,1.0,3.0,0.06),("**One** HP left.",0.95,-1.2,1.0,0.25)]),
   ('4',12.87,16.15,[("**Wait**.",1.0,1.0,0,0),("If it keeps missing, what is **hurting** him?",1.05,0.5,0,0.08)]),
   ('5',16.23,21.30,[("You see,",1.0,-0.3,0,0),("lightning doesn't need a *direct* hit.",1.05,0,0,0.03),("Its current spreads through the **ground**.",1.03,-0.3,1.0,0.1)]),
   ('6',21.50,25.95,[("Boots on two *different* voltages let current pass through his **body**.",1.0,-0.6,1.5,0)]),
   ('7',26.18,28.60,[("He **slams** the guardhouse door!",1.12,0.8,3.0,0)]),
   ('8',28.80,32.95,[("His shield was **useless**.",1.0,-0.6,0,0),("So he equipped the *whole* **castle**.",1.08,0.8,1.5,0.22)])]
def fit(y,maxlen):
    r=len(y)/SR/maxlen
    if r<=1.0: return y,1.0
    r=min(r,1.18); p=os.path.join(TMP,'nk_lm_f.wav'); q=os.path.join(TMP,'nk_lm_g.wav'); sf.write(p,y,SR)
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',p,'-af',f'rubberband=tempo={r:.4f}','-ar',str(SR),'-ac','1',q],check=True)
    z,_=sf.read(q); return z,r
dur={}; txt={}; bad=0
for key,w0,w1,sents in D:
    parts=[]
    for s,sp,st,g,pause in sents:
        b=emph.trim(emph.render(k,a.voice,sp,'en-gb',s,pitch=st,gain=g),0.01,120,360)
        parts.append(np.zeros(int(pause*SR))); parts.append(b)
    y=np.concatenate(parts); y,r=fit(y,w1-w0); y=y/np.max(np.abs(y))*0.95
    nz=np.where(np.abs(y)>0.01)[0]; y=y[:nz[-1]+1200]; sf.write(os.path.join(OUT,key+'.wav'),y,SR)
    dur[key]=round(len(y)/SR,2); txt[key]=' '.join(emph.parse(x[0])[0] for x in sents); over=w0+dur[key]-w1
    print(key,dur[key],'s  window',round(w1-w0,2),('OVER by %.2f'%over if over>0.02 else 'ok'),'(squeezed %.2fx)'%r if r>1 else '',txt[key]); bad+=over>0.02
print('TOTAL',round(sum(dur.values()),2),'words',sum(len(t.split()) for t in txt.values()),'| overflowing lines:',bad)
json.dump({'text':txt,'dur':dur},open(os.path.join(OUT,'script.json'),'w'),indent=1)
