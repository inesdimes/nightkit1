"""Format 3.0 framing check (no render): python tools/qa/framing.py examples/<script>.py [t1,t2,...]
Reports, over every frame: subject centre inside the middle third (target >= 95 %), camera speed (never ~0), and the subject's height as % of the frame at the given times.
The script must define W, H, N, FPS, cam_shot(t,fb), in_fb(t) and subject_pts(t,fb)."""
import sys, os, importlib.util, numpy as np
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..')); sys.path.insert(0,ROOT); sys.path.insert(0,os.path.join(ROOT,'examples'))
spec=importlib.util.spec_from_file_location('m',sys.argv[1]); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
from nightkit import look
bad=[]; cam=[]
for f in range(m.N):
    t=f/m.FPS; fb=m.in_fb(t); sh=m.cam_shot(t,fb); P=np.array(m.subject_pts(t,fb)); c=P[1]
    x,_=look.subject_screen(sh['cam'],sh['tgt'],sh['fov'],m.W,m.H,c)
    if abs(x-0.5)>1/6: bad.append((round(t,2),round(x,2)))
    cam.append(sh['cam'])
cam=np.array(cam); v=np.linalg.norm(np.diff(cam,axis=0),axis=1)*m.FPS
print(f'subject outside the middle third: {len(bad)} of {m.N} frames ({100*len(bad)/m.N:.1f} %) {bad[:10]}')
print(f'camera speed m/s: min {v.min():.2f} median {np.median(v):.2f}; frames < 0.03 m/s (static): {int((v<0.03).sum())}; hard cuts (> 20 m/s): {[round((i+1)/m.FPS,2) for i in np.where(v>20)[0]]}')
for ts in (sys.argv[2].split(',') if len(sys.argv)>2 else ['0','1']):
    t=float(ts); fb=m.in_fb(t); sh=m.cam_shot(t,fb); P=np.array(m.subject_pts(t,fb))
    _,y0=look.subject_screen(sh['cam'],sh['tgt'],sh['fov'],m.W,m.H,P[0]); _,y1=look.subject_screen(sh['cam'],sh['tgt'],sh['fov'],m.W,m.H,P[-1])
    print(f't={t}: subject height {100*abs(y0-y1):.0f} % of the frame (feet {100*y0:.0f} %, head {100*y1:.0f} %)')
