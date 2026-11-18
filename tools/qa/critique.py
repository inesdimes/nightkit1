"""Critique pass on a rendered draft (PIPELINE phase 3b). scene_qa catches geometry; this catches what it cannot:
pacing, silence, a static opening, and gives the sheets for a scored review by eye.
  python tools/qa/critique.py <video.mp4> [--name <script name>] [--round N]
Writes out/qa/<name>/critique_r<N>.png (12 evenly spaced frames + each cut: B = last frame before, A = first after, in yellow) and appends
a round to reviews/<name>.md (tracked in git; the sheets stay in out/qa) with the measured numbers and an empty score table to fill in.
Measured (automatic):
  - motion in the first second (a still opening loses the viewer)
  - 'still' stretches: >= 2 s where the picture barely changes
  - 'quiet' stretches: >= 1.5 s with no voice-level sound (> 18 dB under the loudest half-second)
  - longest gap between voice-level sounds
Scored by eye, 1-10 (PIPELINE rule: every score >= 8 before the final render; at most 3 rounds, then ask Enes):
  readability (faces / eyes / props), motivation + timing of actions, framing, limbs + contacts, text, cuts, sound vs picture, pacing."""
import os, sys, subprocess, argparse, datetime, io
import numpy as np
from PIL import Image, ImageDraw
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..')); sys.path.insert(0,ROOT)
from nightkit import font
SW,SH=90,160
def frames(v):
    p=subprocess.run(['ffprobe','-v','error','-select_streams','v','-show_entries','stream=r_frame_rate','-of','csv=p=0',v],capture_output=True,text=True,check=True).stdout.strip()
    n,d=map(int,p.split('/')); fps=n/d
    raw=subprocess.run(['ffmpeg','-nostdin','-v','error','-i',v,'-vf',f'scale={SW}:{SH}','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True,check=True).stdout
    return np.frombuffer(raw,np.uint8).reshape(-1,SH,SW,3),fps
def audio_rms(v):
    raw=subprocess.run(['ffmpeg','-nostdin','-v','error','-i',v,'-ac','1','-ar','8000','-f','f32le','-'],capture_output=True,check=True).stdout
    a=np.frombuffer(raw,np.float32); w=800                                                       # 0.1 s windows
    return np.array([20*np.log10(np.sqrt((a[i:i+w]**2).mean())+1e-9) for i in range(0,len(a)-w+1,w)])
def runs(mask,step,min_len):
    out=[]; s=None
    for i,m in enumerate(list(mask)+[False]):
        if m and s is None: s=i
        if not m and s is not None:
            if (i-s)*step>=min_len: out.append((round(s*step,1),round(i*step,1)))
            s=None
    return out
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('video'); ap.add_argument('--name'); ap.add_argument('--round',type=int,default=1); a=ap.parse_args()
    name=a.name or os.path.splitext(os.path.basename(a.video))[0]; od=os.path.join(ROOT,'out','qa',name); os.makedirs(od,exist_ok=True)
    F,fps=frames(a.video); n=len(F); dur=n/fps; f32=F.astype(np.float32)
    diff=np.abs(f32[1:]-f32[:-1]).mean(axis=(1,2,3))                                            # mean abs change per frame (0-255)
    def far(i,j): return float(np.abs(f32[i]-f32[j]).mean())
    cuts=[]                                                                                     # a cut = a jump that does NOT come back (a light flicker does)
    for i in range(1,n-1):
        dj=diff[i-1]
        if dj>6 and dj>5*np.median(diff[max(0,i-12):i+12]) and min(far(i-1,j) for j in range(i,min(n,i+9)))>0.5*dj and min(far(k,i) for k in range(max(0,i-9),i))>0.5*dj: cuts.append(i)
    per_s=np.array([diff[int(i*fps):int((i+1)*fps)].mean() for i in range(int(dur))])
    still=runs(np.convolve(diff,np.ones(int(fps//2))/int(fps//2),'same')<0.35,1/fps,2.0)
    opening=float(diff[:int(fps)].mean())
    r=audio_rms(a.video); loud=r.max(); voiced=r>loud-18
    quiet=runs(~voiced,0.1,1.5); gaps=[b-a_ for a_,b in runs(~voiced,0.1,0.0)]
    # ---- contact sheet: 12 even frames, then each cut (last frame before | first after) ----
    idx=[int(i*(n-1)/11) for i in range(12)]; pairs=[(c-1,c) for c in cuts]
    cols=6; rows=2+(len(pairs)*2+cols-1)//cols; sh=Image.new('RGB',(cols*(SW+2),rows*(SH+12)),(0,0,0)); d=ImageDraw.Draw(sh)
    tiles=[(i,f'{i/fps:.2f}') for i in idx]+[(x,f'{"B" if k==0 else "A"}{x/fps:.2f}') for p in pairs for k,x in enumerate(p)]   # B = last frame before a cut, A = first after
    for k,(i,lab) in enumerate(tiles):
        x=(k%cols)*(SW+2); y=(k//cols)*(SH+12); sh.paste(Image.fromarray(F[i]),(x,y+12)); font.text(d,lab,x+2,y+3,(255,214,70) if lab[0] in 'BA' else (230,230,230),1,None)
    png=os.path.join(od,f'critique_r{a.round}.png'); sh.save(png)
    # ---- log ----
    L=[f'## Round {a.round} - {datetime.date.today()} - {os.path.basename(a.video)}','',
       f'- duration {dur:.2f} s, {n} frames, {len(cuts)} cuts at '+(', '.join(f'{c/fps:.2f}' for c in cuts) or 'none'),
       f'- opening motion (first 1 s): {opening:.2f}'+('  <-- STATIC OPENING' if opening<0.4 else ''),
       f'- still stretches (>= 2 s): '+(', '.join(f'{s}-{e} s' for s,e in still) or 'none'),
       f'- quiet stretches (>= 1.5 s without voice-level sound): '+(', '.join(f'{s}-{e} s' for s,e in quiet) or 'none'),
       f'- longest gap between voice-level sounds: {max(gaps) if gaps else 0:.1f} s',
       f'- sheet: {os.path.relpath(png,ROOT)}','',
       '| criterion | score 1-10 | worst problem |','|---|---|---|']
    L+=[f'| {c} |  |  |' for c in ('readability (faces, eyes, props)','motivation + timing','framing','limbs + contacts','text','cuts','sound vs picture','pacing')]
    L+=['','Top 3 fixes this round:','1. ','2. ','3. ','']
    os.makedirs(os.path.join(ROOT,'reviews'),exist_ok=True); log=os.path.join(ROOT,'reviews',f'{name}.md'); new=not os.path.exists(log)
    with open(log,'a') as f:
        if new: f.write(f'# Review log - {name}\n\nEvery score >= 8 before the final render; at most 3 rounds, then the decision goes to Enes.\n\n')
        f.write('\n'.join(L)+'\n')
    print('\n'.join(L[:8])); print(f'\nlog: {os.path.relpath(log,ROOT)}')
if __name__=='__main__': main()
