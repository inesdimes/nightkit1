"""Voice lines for THE LIGHTNING MISSED (lm). One British narrator (bm_george) with per-sentence DIRECTION, because Kokoro has no emotion control:
speed, pitch (rubberband semitones), gain (dB) and a pause before each sentence carry the mood (urgent run, deadpan shield, low ominous reveal,
bright joke). One wav per line in $TTS_DIR/lm/<key>.wav + script.json (text, dur). Run: python tools/tts/lm.py [--voice bm_george]
Windows = where each line may live in the edit (start, latest end); the script warns when a line overflows."""
import json, os, sys, subprocess, tempfile, argparse
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
ap=argparse.ArgumentParser(); ap.add_argument('--voice',default='bm_george'); a=ap.parse_args()
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','tts'))
OUT=os.path.join(TTS_DIR,'lm'); os.makedirs(OUT,exist_ok=True); TMP=tempfile.gettempdir()
k=Kokoro(f'{TTS_DIR}/kokoro-v1.0.int8.onnx',f'{TTS_DIR}/voices-v1.0.bin'); SR=48000
# (key, window start, latest end, [(sentence, speed, pitch semitones, gain dB, pause before s), ...])
D=[('1',0.25,4.50,[("The lightning misses the knight, but his health bar drops by half.",0.95,0.4,1.5,0)]),
   ('2',4.57,8.10,[("His shield is untouched.",0.97,-0.3,0,0),("The pillar took the hit.",1.05,0.6,1.0,0.1)]),
   ('3',8.16,12.80,[("He runs.",1.18,1.2,2.0,0),("Another bolt lands behind him!",1.15,1.0,3.0,0.08),("One HP left.",0.88,-1.2,1.0,0.25)]),
   ('4',12.87,16.15,[("Wait.",0.95,1.0,0,0),("If it keeps missing, what is hurting him?",1.0,0.5,0,0.1)]),
   ('5',16.23,21.30,[("You see,",0.95,-0.3,0,0),("lightning doesn't need a direct hit.",1.03,0,0,0.03),("Its current spreads through the ground.",1.0,-0.3,1.0,0.1)]),
   ('6',21.35,25.95,[("Boots on two different voltages let current pass through his body.",0.93,-0.6,1.5,0)]),
   ('7',26.18,28.60,[("He slams the guardhouse door!",1.1,0.8,3.0,0)]),
   ('8',28.80,32.95,[("His shield was useless.",0.95,-0.6,0,0),("So he equipped the whole castle.",1.03,0.8,1.5,0.25)])]
def ff(src,dst,af): subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',src,'-af',af,'-ar',str(SR),'-ac','1',dst],check=True)
dur={}; txt={}; bad=0
for key,w0,w1,sents in D:
    parts=[]
    for s,sp,st,g,pause in sents:
        wav,sr=k.create(s,voice=a.voice,speed=sp,lang='en-gb'); nz=np.where(np.abs(wav)>0.01)[0]; wav=wav[max(0,nz[0]-240):nz[-1]+480]
        raw=os.path.join(TMP,'nk_lm_raw.wav'); sf.write(raw,wav,sr); p=os.path.join(TMP,'nk_lm_p.wav')
        chain=(f"rubberband=pitch={2**(st/12):.4f}," if abs(st)>0.01 else '')+f"equalizer=f=180:t=q:w=1:g=2,acompressor=threshold=-22dB:ratio=2.5:makeup=3,volume={g}dB"
        ff(raw,p,chain); b,_=sf.read(p); nz=np.where(np.abs(b)>0.01)[0]; b=b[:nz[-1]+1200]
        parts.append(np.zeros(int(pause*SR))); parts.append(b)
    y=np.concatenate(parts); y=y/np.max(np.abs(y))*0.95; sf.write(os.path.join(OUT,key+'.wav'),y,SR)
    dur[key]=round(len(y)/SR,2); txt[key]=' '.join(x[0] for x in sents); over=w0+dur[key]-w1
    print(key,dur[key],'s  window',round(w1-w0,2),'OVER by %.2f'%over if over>0 else 'ok',txt[key]); bad+=over>0
print('TOTAL',round(sum(dur.values()),2),'words',sum(len(t.split()) for t in txt.values()),'| overflowing lines:',bad)
json.dump({'text':txt,'dur':dur},open(os.path.join(OUT,'script.json'),'w'),indent=1)
