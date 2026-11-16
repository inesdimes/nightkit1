"""FINAL BOSS - Experiment B (60 s): same story as Experiment A (final_boss.py), slower mystery build-up.
Reuses A's models, set, renderer and HUD. 0-4 s are A's frames + A's audio verbatim; the ending (56.3 s-end) is A's
26.6-30.5 s (outside daylight + trapped knight) verbatim, video and audio.
Run: TEST=5,14,30 python examples/final_boss_b.py -> test.png | PART=a:b (frames -> out/fbb_a.mp4) | PART=audio
Needs out/final_boss_a.wav (PART=audio python examples/final_boss.py) for the shared hook/ending audio."""
import os, sys, math
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import final_boss as A
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Camera, quad
from nightkit.zraster import zrender
from nightkit import post, font
from nightkit.audio import Sound
knight,boss,prelit,box,seg,xform=A.knight,A.boss,A.prelit,A.box,A.seg,A.xform
sm,seg01,lerp,lerp3,PI,Ry,Rx=A.sm,A.seg01,A.lerp,A.lerp3,A.PI,A.Ry,A.Rx
W,H,S,FPS=A.W,A.H,A.S,A.FPS
OUT='out'; os.makedirs(OUT,exist_ok=True)
END_OFF=29.75                                 # B time = A time + 29.75 (= 714 frames, so grain and motion match A exactly)
END_START=26.6+END_OFF; DUR=A.DUR+END_OFF; N=int(round(DUR*FPS))      # 56.35 s .. 60.25 s
TTS_DIR=A.TTS_DIR; SCR=A.SCR

# ======================= narration schedule =======================
NARR=[('M2',4.30),('M3',10.0),('M4',16.4),('M5',20.4),('B1',25.4),('M6',27.7),('M7',29.3),('M8',31.7),('M9',33.5),
      ('M10',41.0),('M11',47.6),('M12',51.0),('M13',53.0)]
# ======================= events =======================
OUT_IMPACTS=[7.75,8.65,10.9]                  # heard (and leaking light) from the corridor side
POV_IMPACT=15.35                              # seen through the gap
SLAM=29.8
CRASH=43.6
PUSHES=[45.45,46.35,47.25]
BOSS_DRAW=25.55; SWORD_DROP=A.SWORD_DROP+24.7
LETTERS_ON=49.2; BAR_OFF=(51.4,51.9); BAR_ON=54.0

# ======================= B-only set dressing: abandoned corridor, damage, lever =======================
LEVER=(-2.12,1.25,-1.3)
def dressing():
    Q=[]; r=np.random.default_rng(7)
    for k in range(26):                                                    # rubble on the corridor floor
        x=r.uniform(-2.0,2.0); z=r.uniform(-14,-0.4); s_=r.uniform(0.08,0.28)
        if abs(x)<0.7 and z<-2: x=math.copysign(r.uniform(0.9,2.0),x)
        Q+=box(x-s_,x+s_,0,s_*1.2,z-s_,z+s_,(72,66,70) if k%2 else (58,54,58))
    Q+=box(1.0,2.1,0,0.55,-9.2,-6.4,(80,74,78))+box(1.1,2.0,0.55,0.62,-9.0,-6.6,(66,60,64))       # fallen pillar
    for sx,z in ((-1,-6.0),(1,-10.5),(-1,-12.8)):                         # torn banners
        x=sx*2.17
        Q.append(quad([(x,3.9,z-0.45),(x,3.9,z+0.45),(x,2.4,z+0.45),(x,1.9,z+0.1),(x,2.3,z-0.45)][:4],(96,20,26)))
        Q.append(quad([(x,2.4,z+0.45),(x,1.9,z+0.1),(x,2.3,z-0.45),(x,2.35,z)],(96,20,26)))
    # damage marks around the doorway: gouges + red-glowing cracks on both corridor walls, scorched floor
    for sx in (-1,1):
        x=sx*2.185
        for k in range(7):
            y0=r.uniform(0.6,4.3); z0=r.uniform(-1.6,-0.15); L=r.uniform(0.5,1.1); a=r.uniform(-0.6,0.6)
            p0=(x,y0,z0); p1=(x,y0+L*math.cos(a),z0+L*math.sin(a)*0.8)
            Q+=seg(p0,p1,0.07,(20,14,16),0.02)
        for k in range(4):
            y0=r.uniform(1.0,4.0); z0=-0.25; pts=[(x,y0,z0)]
            for j in range(4): pts.append((x,pts[-1][1]+r.uniform(-0.5,0.5),pts[-1][2]-r.uniform(0.25,0.45)))
            for p0,p1 in zip(pts,pts[1:]): Q+=seg(p0,p1,0.04,(150,30,24),0.015,emit=True)
    for k in range(9):
        x=r.uniform(-1.9,1.9); z=r.uniform(-1.5,-0.2); s_=r.uniform(0.25,0.6)
        Q.append(quad([(x-s_,0.012,z-s_*0.5),(x+s_,0.012,z-s_*0.5),(x+s_,0.012,z+s_*0.5),(x-s_,0.012,z+s_*0.5)],(28,22,24)))
    # lever mechanism: wall plate + chain up into the ceiling
    lx,ly,lz=LEVER
    Q+=box(lx-0.06,lx+0.04,ly-0.45,ly+0.45,lz-0.22,lz+0.22,A.IRON_L)+box(lx-0.02,lx+0.04,ly+0.45,A.GATE_H,lz-0.03,lz+0.03,A.IRON)
    return Q
DRESS=dressing()
def lever_tip(ang): lx,ly,lz=LEVER; return np.array([lx+0.25,ly+0.5*math.cos(ang),lz+0.5*math.sin(ang)])
def lever(ang):
    lx,ly,lz=LEVER; tip=lever_tip(ang)
    return seg((lx+0.25,ly,lz),tip,0.07,A.IRON_L)+box(lx+0.02,lx+0.3,ly-0.06,ly+0.06,lz-0.06,lz+0.06,A.IRON)+box(tip[0]-0.07,tip[0]+0.07,tip[1]-0.07,tip[1]+0.07,tip[2]-0.07,tip[2]+0.07,(150,28,28))
def lever_angle(t): return lerp(0.5,-0.5,sm(seg01(t,21.35,21.85)))

# ======================= state =======================
def impact(t,lst,dur): return A.impact(t,lst,dur)
def gate_b(t):
    if t<12.2: base=0.0
    elif t<22.0: base=0.45*sm(seg01(t,12.2,12.9))*(1.0 if t<20.2 else 1-sm(seg01(t,20.2,20.8)))
    elif t<29.5: base=1.75*sm(seg01(t,22.0,23.4))
    elif t<36.8: base=1.75*(1-seg01(t,29.5,29.8)**2)
    else: base=1.75*sm(seg01(t,36.8,37.9))
    iv,_=impact(t,OUT_IMPACTS+[POV_IMPACT],0.35)
    return base+0.035*iv*math.sin(t*70)
def seam_glow(t):
    iv,_=impact(t,OUT_IMPACTS+[POV_IMPACT],0.6)
    return 0.35+0.65*iv
def boss_b(t):
    if t<13.6: return None
    if t<17.2:                                                    # POV: approaches, shoves, thrown back
        if t<15.15:
            u=sm(seg01(t,13.6,15.15)); z=lerp(7.0,1.75,u)
            a_=sm(seg01(t,14.6,15.15)); lean=0.15*u
            return dict(base=(0,0,z),yaw=PI,walk=t*5.2 if u<0.98 else 0.0,sword='back',rh=(lerp(0.92,1.15,a_),lerp(1.55,2.8,a_),lerp(0.2,0.8,a_)),
                        lh=(lerp(-0.92,-1.15,a_),lerp(1.55,2.9,a_),lerp(0.2,0.8,a_)),lean=lean)
        k=sm(seg01(t,POV_IMPACT,POV_IMPACT+0.5)); rec=sm(seg01(t,16.1,16.9))
        z=lerp(1.75,3.7,k); lean=lerp(0.18,-0.3,k)*(1-rec)+0.05*rec; yr=lerp(2.8,3.3,k*(1-rec)); yl=lerp(2.9,3.4,k*(1-rec))
        D=1.75-A.BARRIER_Z-0.17
        return dict(base=(0,0,z),yaw=PI,sword='back',rh=(1.15,yr,lerp(A.reach_local(D,0.18,yr,1.55),0.3,k)),lh=(-1.15,yl,lerp(A.reach_local(D,0.18,yl,1.55),0.3,k)),lean=lean,head=0.0)
    if t<23.6:
        w=seg01(t,17.2,20.2); tu=sm(seg01(t,17.2,17.8))
        return dict(base=(lerp(0.0,-1.3,sm(w)),0,lerp(3.7,8.0,sm(w))),yaw=lerp(PI,2*PI,tu),walk=t*5.2 if 0<w<1 else 0.0,sword='back',rh=A.BOSS_IDLE_RH)
    if t<33.0:                                                    # A's arrival behaviour, slowed down
        u=sm(seg01(t,23.9,25.3)); yaw=lerp(0.0,PI,u); sw,rh,tip=A.boss_draw(t,BOSS_DRAW)
        l=sm(seg01(t,31.6,32.6))
        if l>0: rh=lerp3(rh,(0.92,1.6,0.25),l); tip=lerp3(tip,(1.1,0.05,1.9),l)
        return dict(base=(-1.3,0,8.0),yaw=yaw,sword=sw,rh=rh,tip=tip,head=0.0)
    P=[(33.0,(-1.3,8.0)),(35.5,(-1.3,3.4)),(36.5,(-1.3,1.9)),(38.2,(0.0,0.2)),(39.4,(0.0,-0.8)),(40.0,(0.0,-1.4)),(40.9,(0.0,-1.4)),(47.5,(0.0,-14.0))]
    for (t0,p0),(t1,p1) in zip(P,P[1:]):
        if t<t1 or t1==P[-1][0]: u=seg01(t,t0,t1); x=lerp(p0[0],p1[0],u); z=lerp(p0[1],p1[1],u); moving=p0!=p1; break
    lean=-0.12*math.sin(PI*seg01(t,40.0,40.9))                    # stops, looks up at the daylight: free
    yaw=PI+(0.35*math.sin(PI*seg01(t,34.8,36.2)))                  # glances at the knight while passing
    return dict(base=(x,0,z),yaw=yaw,walk=t*5.2 if moving else 0.0,rh=(0.92,1.6,0.25),tip=(1.1,0.05,1.9),lean=lean)

LOW=dict(sword='hand',rh=(0.3,0.95,0.35),swing=2.0)              # sword drawn, held low
SIDE=dict(sword='hand',rh=(0.3,0.9,0.05),swing=3.0)              # sword drawn, pointing at the floor by his side (near walls)
KN_LEVER=(-1.45,LEVER[2]-0.15)
def to_local(p,base,yaw): return tuple(Ry(-yaw)@(np.array(p,float)-np.array(base,float)))
def knight_b(t):
    if t<7.6: u=seg01(t,4.0,7.6); return dict(base=(0.2,0,lerp(-11.0,-5.7,u)),yaw=0.0,walk=t*7.0,head=0.25*math.sin(t*1.3),**LOW)
    if t<9.2:
        g=sm(seg01(t,7.8,8.2)); return dict(base=(0.2,0,-5.7),yaw=0.0,lean=-0.12*g,sword='hand',rh=lerp3((0.3,0.95,0.35),(0.3,1.2,0.35),g),swing=lerp(2.0,0.45,g),head=0.0)
    if t<12.2:
        u=sm(seg01(t,9.2,10.6)); x=lerp(0.2,-1.6,u); z=lerp(-5.7,-0.95,u); yaw=lerp(0.0,-PI/2,sm(seg01(t,10.3,10.8)))
        touch=sm(seg01(t,10.6,10.85))*(1-sm(seg01(t,10.95,11.3))); hold=sm(seg01(t,9.6,10.3))
        return dict(base=(x,0,z),yaw=yaw,walk=t*7.0 if u<0.99 else 0.0,lh=(-0.1,1.45,lerp(0.2,0.52,touch)) if touch>0.02 else None,
                    head=(0.9*sm(seg01(t,11.0,11.4)) if t>11.0 else 0.0),lean=-0.08*sm(seg01(t,10.95,11.2)),sword='hand',
                    rh=lerp3(LOW['rh'],SIDE['rh'],hold),swing=lerp(LOW['swing'],SIDE['swing'],hold))
    if t<17.2 and t>=16.8:
        u=sm(seg01(t,16.8,17.5)); return dict(base=(0.0,0,lerp(-1.1,-1.9,u)),yaw=0.0,walk=t*7.0,lean=0.22*(1-u),**LOW)
    if t<17.2:
        u=sm(seg01(t,12.2,13.0)); x=lerp(-1.6,0.0,u); z=lerp(-0.95,-1.1,u); hold=sm(seg01(t,12.3,12.9))
        return dict(base=(x,0,z),yaw=lerp(-PI/2,0.0,u),walk=t*7.0 if u<0.99 else 0.0,lean=0.22*sm(seg01(t,12.8,13.4)),sword='hand',
                    rh=lerp3(SIDE['rh'],LOW['rh'],hold),swing=lerp(SIDE['swing'],LOW['swing'],hold))
    if t<20.2:
        u=sm(seg01(t,16.8,17.5)); tilt=0.35*sm(seg01(t,18.0,18.5))*(1-sm(seg01(t,19.6,20.0)))
        return dict(base=(0.0,0,lerp(-1.1,-1.9,u)),yaw=0.0,walk=t*7.0 if 0.02<u<0.98 else 0.0,head=tilt,lean=-0.05,**LOW)
    if t<23.6:
        if t<21.1:
            u=sm(seg01(t,20.3,21.1)); h=sm(seg01(t,20.4,21.0))
            return dict(base=(lerp(0.0,KN_LEVER[0],u),0,lerp(-1.9,KN_LEVER[1],u)),yaw=0.0,walk=t*7.0 if u<0.99 else 0.0,sword='hand',rh=lerp3(LOW['rh'],SIDE['rh'],h),swing=lerp(LOW['swing'],SIDE['swing'],h))
        if t<22.6:                                                 # left hand on the lever handle the whole time it moves
            base=(KN_LEVER[0],0,KN_LEVER[1]); grab=sm(seg01(t,21.1,21.35)); rel=sm(seg01(t,22.0,22.3))
            hand=np.array(to_local(lever_tip(lever_angle(t)),base,0.0)); idle=np.array((-0.27,0.86,0.04))
            lh=tuple(idle+(hand-idle)*grab*(1-rel))
            return dict(base=base,yaw=0.0,lh=lh if grab*(1-rel)>0.02 else None,lean=-0.06*sm(seg01(t,21.35,21.85))*(1-rel),**SIDE)
        u=sm(seg01(t,22.6,23.5)); h=sm(seg01(t,22.7,23.4))
        return dict(base=(lerp(KN_LEVER[0],0.0,u),0,lerp(KN_LEVER[1],-1.05,u)),yaw=0.0,walk=t*7.0 if u<0.99 else 0.0,sword='hand',rh=lerp3(SIDE['rh'],LOW['rh'],h),swing=lerp(SIDE['swing'],LOW['swing'],h))
    if t<26.9: return dict(base=(0.0,0,-1.05),yaw=0.0,**LOW)
    if t<30.6:                                                    # enters cautiously, raises the sword
        u=seg01(t,26.9,28.6); r=sm(seg01(t,27.8,28.3)); look=-1.1*math.sin(PI*seg01(t,29.9,30.6)) if t>29.9 else 0.0
        return dict(base=(lerp(0.0,-0.5,u),0,lerp(-1.05,2.8,sm(u))),yaw=0.0,walk=t*6.0 if u<0.98 else 0.0,sword='hand',
                    rh=lerp3((0.3,0.95,0.35),(0.3,1.15,0.38),r),swing=lerp(2.0,0.5,r),head=look,lean=-0.05)
    if t<41.0:
        st=sm(seg01(t,34.3,35.0)); x=lerp(-0.5,0.3,st); z=lerp(2.8,2.6,st)
        look=sm(seg01(t,34.6,36.6))*(-0.9) if t<37.0 else -0.9*(1-seg01(t,37.0,38.0))
        yaw=0.0 if t<37.0 else lerp(0.0,PI,sm(seg01(t,37.0,38.4)))
        low=sm(seg01(t,38.8,40.6))
        return dict(base=(x,0,z),yaw=yaw,walk=t*7.0 if 0.02<st<0.98 else 0.0,sword='hand',rh=lerp3((0.3,1.15,0.38),(0.3,0.95,0.35),low),swing=lerp(0.5,2.0,low),
                    head=look if t<37.0 else look,lean=-0.06*(1-low))
    if t<44.9: return A.knight_state(t-24.7)                       # run, crash, knocked down (A's motion)
    if t<54.6:                                                    # pushes the wall, then gives up under the inscription
        z=lerp(1.75,A.BARRIER_Z+0.42,sm(seg01(t,44.9,45.35)))
        if t<48.9: return A.knight_push(t,z,PUSHES)
        back=sm(seg01(t,48.9,49.5))                                # lets go and steps back, looks up at the words
        return dict(base=(0.0,0,lerp(A.BARRIER_Z+0.54,A.BARRIER_Z+0.7,back)),yaw=PI,lean=-0.12*sm(seg01(t,49.0,50.0)),sword='none',head=0.25*math.sin(PI*seg01(t,51.2,52.4)))
    turn=sm(seg01(t,54.6,55.3)); st=seg01(t,55.2,56.2); eyes=sm(seg01(t,55.5,56.2))
    return dict(base=(0.0,0,lerp(A.BARRIER_Z+0.7,2.6,sm(st))),yaw=PI+turn*PI,walk=t*6.0 if 0.02<st<0.98 else 0.0,sword='none',eyes=eyes,lean=0.0)

# ======================= shots =======================
def shot(V):
    def sh_at(ts,k=4.0,dur=0.55):
        iv,_=impact(V,ts,dur); return (math.sin(V*85)*k*iv,math.cos(V*67)*k*0.8*iv)
    if V<7.6:  u=sm(seg01(V,4.0,7.6)); return dict(cam=lerp3((0.9,1.7,-3.1),(0.85,1.65,-2.7),u),tgt=(0.1,1.4,-10.0),fov=62)
    if V<9.2:  return dict(cam=(0.9,1.6,-8.6),tgt=(0.0,2.1,0.0),fov=60,shake=sh_at(OUT_IMPACTS,3.0))
    if V<12.2: u=sm(seg01(V,9.2,12.2)); return dict(cam=lerp3((1.55,1.95,-3.3),(1.45,1.9,-3.0),u),tgt=(-1.9,1.75,-0.7),fov=60,shake=sh_at(OUT_IMPACTS,2.5))
    if V<13.6: u=sm(seg01(V,12.2,13.6)); return dict(cam=lerp3((1.5,2.0,-3.7),(1.0,2.0,-2.9),u),tgt=(-0.2,1.55,-0.3),fov=62)
    if V<17.2: return dict(cam=(0.0,1.6,-1.55),tgt=(0.0,2.4,6.0),fov=70,shake=sh_at([POV_IMPACT],3.5),pov=True)
    if V<20.2: u=sm(seg01(V,17.2,20.2)); return dict(cam=lerp3((0.0,1.6,-0.45),(0.0,1.6,-0.4),u),tgt=(0.0,1.45,-2.2),fov=64)
    if V<23.6: u=sm(seg01(V,20.2,23.6)); return dict(cam=lerp3((0.7,1.65,-3.9),(0.6,1.6,-3.5),u),tgt=(-1.5,1.4,-1.1),fov=62)
    if V<25.2: u=sm(seg01(V,23.6,25.2)); return dict(cam=lerp3((-0.95,1.6,-3.9),(-0.9,1.65,-3.5),u),tgt=(-1.1,2.3,8.0),fov=64)
    if V<26.9: u=sm(seg01(V,25.2,26.9)); return dict(cam=lerp3((1.0,2.2,4.3),(0.8,2.4,4.9),u),tgt=(-1.3,3.0,8.0),fov=60)
    if V<30.6: u=sm(seg01(V,26.9,30.6)); return dict(cam=lerp3((2.0,1.1,5.8),(1.7,1.2,5.2),u),tgt=(-0.2,1.5,1.0),fov=66,shake=sh_at([SLAM],4.0))
    if V<33.0: u=sm(seg01(V,30.6,33.0)); return dict(cam=lerp3((1.2,2.0,4.6),(1.0,2.2,5.1),u),tgt=(-1.3,2.6,8.0),fov=60)
    if V<38.6: u=sm(seg01(V,33.0,38.6)); return dict(cam=lerp3((6.2,2.6,6.4),(5.6,2.4,5.2),u),tgt=lerp3((-1.0,2.0,6.5),(-0.5,1.8,2.4),u),fov=66)
    if V<41.0: u=sm(seg01(V,38.6,41.0)); return dict(cam=lerp3((1.6,1.0,5.2),(1.3,1.0,4.6),u),tgt=(-0.1,2.0,-1.0),fov=66)
    if V<44.4: return dict(cam=(2.9,1.3,3.6),tgt=(0.0,1.0,0.9),fov=64,shake=sh_at([CRASH],5.0,0.6))
    if V<46.4: return dict(cam=(0.9,1.6,5.2),tgt=(0.0,1.5,-6.0),fov=62,shake=sh_at(PUSHES,1.5,0.3))
    if V<47.6: u=sm(seg01(V,46.4,47.6)); return dict(cam=lerp3((0.3,1.5,-2.5),(0.3,1.5,-2.2),u),tgt=(0.0,1.35,1.2),fov=62,shake=sh_at(PUSHES,2.0,0.3))
    if V<54.6: u=sm(seg01(V,47.6,54.6)); return dict(cam=lerp3((0.0,1.0,8.0),(0.0,1.4,5.2),u),tgt=lerp3((0.0,4.6,0.0),(0.0,2.6,0.0),sm(seg01(V,50.5,53.5))),fov=64)
    u=sm(seg01(V,54.6,56.35)); return dict(cam=lerp3((0.6,1.75,-1.1),(0.5,1.75,-0.7),u),tgt=(-0.1,1.9,15.0),fov=56,fog_end=40)

# ======================= render =======================
R=A.R
def render_b(V,sh):
    cam=Camera.look(sh['cam'],sh['tgt']); cp=np.array(sh['cam'])
    layers=[A.ARENA,DRESS,lever(lever_angle(V)),A.gate_doors(gate_b(V)),A.torches(V),A.sword_on_floor(V,SWORD_DROP,A.SWORD_FROM,A.SWORD_TO)]
    ks=knight_b(V)
    if not sh.get('pov'): layers.append(prelit(knight(**ks),sh['cam']))
    bs=boss_b(V)
    if bs is not None: layers.append(boss(**bs))
    g=gate_b(V)
    if g<0.1:                                                     # red light leaking through the seam / under the doors
        gl=seam_glow(V); c=tuple(int(v*gl) for v in (255,50,30))
        layers.append([quad([(-0.05,0.0,-0.19),(0.05,0.0,-0.19),(0.05,A.GATE_H,-0.19),(-0.05,A.GATE_H,-0.19)],c,emit=True),
                       quad([(-A.GATE_W,0.005,-0.4),(A.GATE_W,0.005,-0.4),(A.GATE_W,0.005,-0.05),(-A.GATE_W,0.005,-0.05)],tuple(int(v*0.45) for v in c),emit=True)])
    L=A.torch_lights(V)
    fl,_=impact(V,OUT_IMPACTS+[POV_IMPACT,CRASH]+PUSHES,0.4)
    if fl>0: L=L+[((0,2.2,A.BARRIER_Z+0.6),(255,40,30),2.5*fl),((0,1.6,-0.8),(255,40,30),1.2*fl*(1 if g<0.5 else 0))]
    L=L+[((0,2.4,A.BARRIER_Z+0.4),(255,40,30),0.5),((0,1.6,-0.6),(255,50,30),0.35 if g<0.5 else 0.0)]
    if V>=54.6: L=L+[((0,3.2,13.8),(255,70,40),3.0),((0,6.0,15.5),(255,60,40),1.5)]                                            # light on the empty throne
    img,vi,zb=zrender(R,cam,layers,L,fov=sh['fov'],fog_start=7,fog_end=sh.get('fog_end',26),ambient=0.2,shake=sh.get('shake',(0,0)),return_z=True)
    base=0.1; flash=0.0; rc=None; rr=0.0; tint=(255,40,30)
    f2,src=impact(V,[POV_IMPACT,CRASH]+PUSHES,0.6)
    if src is not None: flash=f2*(1.6 if src==POV_IMPACT else 1.0); rr=(V-src)*5.0; rc=(0.0,2.8) if src==POV_IMPACT else (0.0,1.3)
    if 27.35<V<27.95: flash=0.5*math.sin(PI*seg01(V,27.35,27.95)); rc=(0.0,1.2); rr=(V-27.35)*5; tint=(120,170,255)
    if 39.0<V<39.8: flash=0.6*math.sin(PI*seg01(V,39.0,39.8)); rc=(0.0,2.2); rr=(V-39.0)*5; tint=(120,170,255)
    bimg,_,bz=zrender(R,cam,[A.barrier_quads(flash,rc,rr,base,tint)],[],fov=sh['fov'],fog_start=7,fog_end=26,shake=sh.get('shake',(0,0)),return_z=True)
    m=(bz>zb)&(bz>0)
    a=np.asarray(img).astype(np.float32); b=np.asarray(bimg).astype(np.float32)-np.array(R.fog,np.float32)*0.5
    img=Image.fromarray(np.where(m[...,None],np.clip(a+np.clip(b,0,255),0,255),a).astype(np.uint8))
    if V>=LETTERS_ON: img=A.letters(img,vi,sm(seg01(V,LETTERS_ON,LETTERS_ON+0.9))*(0.85+0.15*math.sin(V*6)))
    if sh.get('pov'):                                             # dark door edges framing the gap
        a=np.asarray(img).astype(np.float32); X=np.arange(W)[None,:,None]; edge=np.clip((np.abs(X-W/2)-50)/14,0,1)
        img=Image.fromarray((a*(1-0.85*edge)).astype(np.uint8))
    return post.ps1(img),vi

# ======================= HUD =======================
HIL=A.HIL|{'LAST','GAME.','POUNDING','CROSS','DOORWAY.','GATE,','MONSTER','SWORD.','SLAMMED','SHUT','DIDN\'T','ATTACK.','STRAIGHT','RAN','SAME',
           'WORDS','DOOR:','VANISHED.','NEW','BOSS.'}
def subtitle(d,V):
    cur=None
    for k,t0 in NARR:
        if t0<=V<t0+SCR['dur'][k]+0.12: cur=k
    if cur is None: return
    txt=SCR['text'][cur].upper().replace('...','..')
    if cur=='B1': txt="'"+txt+"'"
    ws=txt.split(); lines=[]; c=''
    for w_ in ws:
        if len(c)+len(w_)+(1 if c else 0)>27: lines.append(c); c=w_
        else: c=(c+' '+w_).strip()
    lines.append(c); y=266-11*(len(lines)-1)
    for ln in lines:
        xw=font.width(ln); x=(W-xw)//2; d.rectangle([x-3,y-2,x+xw+2,y+8],fill=(0,0,0)); cx=x
        for wd in ln.split(' '):
            col=A.RED if cur=='B1' else (A.YEL if wd.strip("'") in HIL else A.WHT)
            A.otext(d,wd,cx,y,col); cx+=font.width(wd)+6
        y+=11
def hp_knight(d,V):
    if not (26.9<=V<BAR_OFF[1]): return
    if V>=BAR_OFF[0] and int(V*16)%2: return
    A.otext(d,'KNIGHT',8,10,A.BLU); d.rectangle([8,20,72,25],fill=(0,0,0),outline=(200,200,210)); d.rectangle([9,21,71,24],fill=A.GRN)
def hp_boss(d,V):
    if V<BAR_ON: return
    drop=sm(seg01(V,BAR_ON,BAR_ON+0.25)); fill=sm(seg01(V,BAR_ON+0.25,BAR_ON+1.1)); y=int(lerp(-30,22,drop))
    A.otext(d,'FINAL BOSS',(W-font.width('FINAL BOSS',2))//2,y,A.RED,2)
    x0,x1=10,W-10; d.rectangle([x0-1,y+18,x1+1,y+28],fill=(0,0,0),outline=(230,190,90)); d.rectangle([x0+1,y+20,x0+1+int((x1-x0-2)*fill),y+26],fill=A.RED)
    d.rectangle([x0+1,y+20,x0+1+int((x1-x0-2)*fill),y+21],fill=(255,140,120))
def emote(d,vi,V,ks):
    """retro RPG '?' bubble over the knight: he doesn't understand why the boss is trapped"""
    if not (17.9<=V<19.7): return
    p=R.project(tuple(np.array(ks['base'])+np.array([0,2.15,0])),vi)
    if not p: return
    pop=sm(seg01(V,17.9,18.1)); bob=int(2*math.sin(V*8)); x,y=int(p[0]),int(p[1])-6+bob; r=int(9*pop)
    if r<2: return
    d.rectangle([x-r,y-r-2,x+r,y+r],fill=A.WHT,outline=(0,0,0)); d.polygon([(x-3,y+r),(x+3,y+r),(x,y+r+5)],fill=A.WHT,outline=(0,0,0))
    if pop>0.9: font.text(d,'?',x-4,y-7,(20,20,30),2,None)
def frame(V):
    if V<4.0: return A.frame(V)                                  # identical hook
    if V>=END_START: return A.frame(min(V-END_OFF,A.DUR-1e-3))   # identical ending
    sh=shot(V); img,vi=render_b(V,sh); d=ImageDraw.Draw(img)
    if not sh.get('pov'): emote(d,vi,V,knight_b(V))
    hp_knight(d,V); hp_boss(d,V); subtitle(d,V)
    return img

TEST=os.environ.get('TEST')
if TEST and __name__=='__main__':
    ims=[frame(float(x)) for x in TEST.split(',')]; shp=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): shp.paste(im,(i*182,0))
    shp.resize((shp.width*2,640),Image.NEAREST).save('test.png'); sys.exit()

# ======================= QA manifest =======================
def _cam(t):
    if t<4.0: return A.shot(t)['cam']
    if t>=END_START: s_=A.shot(t-END_OFF); return None if s_.get('outside') else s_['cam']
    return shot(t)['cam']
QA=dict(A.QA,dur=DUR,frame=frame,
    knight=lambda t: A.knight_state(t) if t<4.0 else (A.knight_state(t-END_OFF) if t>=END_START else knight_b(t)),
    boss=lambda t: A.boss_state(t) if t<4.0 else (A.boss_state(t-END_OFF) if t>=END_START else boss_b(t)),
    camera=_cam,
    scenes=[dict(id='hook (=A)',t0=0.0,t1=4.0,action='boss shoves the invisible wall',env='arena'),
            dict(id='corridor',t0=4.0,t1=7.6,action='knight walks the abandoned corridor, sword drawn',env='corridor'),
            dict(id='impacts',t0=7.6,t1=9.2,action='impacts behind the gate; knight raises guard',env='corridor'),
            dict(id='damage',t0=9.2,t1=12.2,action='knight touches gouges/cracks by the door',env='corridor'),
            dict(id='peek',t0=12.2,t1=13.6,action='knight leans to the gap in the gate',env='corridor'),
            dict(id='pov',t0=13.6,t1=17.2,action='POV: boss shoves the barrier, thrown back',env='through the gap',pov=True),
            dict(id='confused',t0=17.2,t1=20.2,action='knight steps back, ? emote',env='corridor'),
            dict(id='lever',t0=20.2,t1=23.6,action='knight pulls the lever, gate opens',env='corridor'),
            dict(id='boss-turns',t0=23.6,t1=25.2,action='boss slowly turns around',env='corridor -> arena'),
            dict(id='boss-line',t0=25.2,t1=26.9,action='boss: You finally came',env='arena'),
            dict(id='enter',t0=26.9,t1=30.6,action='knight enters, raises sword; gate slams',env='arena'),
            dict(id='lowers',t0=30.6,t1=33.0,action='boss lowers his sword',env='arena'),
            dict(id='walk-out',t0=33.0,t1=38.6,action='boss walks past, knight steps aside',env='arena'),
            dict(id='exit',t0=38.6,t1=41.0,action='boss passes the barrier, stops in the daylight',env='arena, open gate'),
            dict(id='crash',t0=41.0,t1=44.4,action='knight runs and hits the wall',env='arena'),
            dict(id='push',t0=44.4,t1=46.4,action='knight pushes the barrier',env='arena'),
            dict(id='push-front',t0=46.4,t1=47.6,action='knight panics against the barrier (front)',env='corridor view'),
            dict(id='reveal',t0=47.6,t1=54.6,action='ONE MUST REMAIN; health bars swap',env='arena'),
            dict(id='throne',t0=54.6,t1=END_START,action='knight turns to the empty throne',env='arena'),
            dict(id='daylight (=A)',t0=END_START,t1=END_START+1.95,action='old boss walks into daylight',env='outside',set='outside'),
            dict(id='trapped (=A)',t0=END_START+1.95,t1=DUR,action='knight trapped behind the barrier',env='corridor view')],
    weapon_events=[('knight',4.0,'hip','hand'),('boss',BOSS_DRAW+0.3,'back','hand'),('knight',SWORD_DROP,'hand','none')],
    crossings=[('knight',27.0,28.6),('boss',36.6,39.8)],
    allow_jump=[('knight',4.0),('boss',END_START)],
    texts=lambda: A.QA['texts']())

# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=29); sr=s.sr; n=s.n; t=s.t; M=np.zeros(n); AMB=np.zeros(n)
    def note(buf,t0,m,d,v,wave='sq',duty=0.5,dec=3.0,att=0.01):
        f=440*2**((m-69)/12); tt=s.T(d); ph=(f*tt)%1
        x=np.where(ph<duty,1.0,-1.0) if wave=='sq' else (4*np.abs(ph-0.5)-1 if wave=='tri' else np.sin(2*np.pi*ph))
        env=np.minimum(1,tt/att)*np.exp(-tt*dec); i=int(t0*sr); j=min(n,i+len(tt)); buf[i:j]+=(x*env*v)[:j-i]
    def organ(t0,m,d,v):
        for k,a in ((1,1.0),(2,0.4),(0.5,0.6)): note(M,t0,m+12*math.log2(k),d,v*a,'sin',dec=0.6,att=0.08)
    def nb(t0,d,lo,hi,v,seed,shape=2,pan=0.0): s.place(s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v,pan)
    def thud(t0,f=55,v=0.3,d=0.6): tt=s.T(d); s.place(np.sin(2*np.pi*f*tt*(1-0.3*tt/d))*np.exp(-tt*8)+s.filt_short(s.noise(d,int(t0*13)),lo=60,hi=700)*np.exp(-tt*12)*0.6,t0,v)
    def clank(t0,v=0.15,seed=0): tt=s.T(0.6); s.place(sum(np.sin(2*np.pi*f*tt)*np.exp(-tt*k) for f,k in ((310,6),(820,9),(1490,14)))*0.4+s.filt_short(s.noise(0.6,seed),lo=1200,hi=6000)*np.exp(-tt*30),t0,v)
    def step_k(t0,v=0.05,seed=0): tt=s.T(0.12); s.place(s.filt_short(s.noise(0.12,seed),lo=900,hi=5000)*np.exp(-tt*45)+np.sin(2*np.pi*2300*tt)*np.exp(-tt*60)*0.3,t0,v)
    def step_b(t0,v=0.35): thud(t0,45,v,0.5); nb(t0,0.15,200,1500,v*0.15,int(t0*31))
    def zap(t0,v=0.25,seed=0,muffled=False):
        tt=s.T(0.7); sweep=np.sin(2*np.pi*np.cumsum(900*np.exp(-tt*5)+70)/sr)*np.exp(-tt*5)
        x=sweep*0.6+s.filt_short(s.noise(0.7,seed),lo=1500,hi=9000)*np.exp(-tt*14)*0.5
        if muffled: x=s.filt_short(x,hi=500)*2.0
        s.place(x,t0,v); thud(t0,60,v*(1.4 if muffled else 0.8),0.6 if muffled else 0.4)
    def chime(t0,v=0.06):
        for k,m in enumerate((74,79,83,86)): note(M,t0+k*0.06,m,0.6,v,'sin',dec=4)
    # ambience
    AMB+=s.filt(s.rng.normal(0,1,n),lo=50,hi=500)*0.02
    pr=np.random.default_rng(4)
    for tc in np.cumsum(pr.exponential(1.4,80)):
        if tc<DUR: tt=s.T(0.15); i=int(tc*sr); j=min(n,i+len(tt)); AMB[i:j]+=(np.sin(2*np.pi*np.cumsum(1400+900*np.exp(-tt*30))/sr)*np.exp(-tt*25)*0.02)[:j-i]
    # music: same drone, heartbeat and D-F-E-A motif as A, spread over the longer build-up
    M+=(np.sin(2*np.pi*36.7*t)+0.6*np.sin(2*np.pi*55.0*t+np.sin(2*np.pi*0.2*t)))*0.03
    for k in range(int(DUR/1.0)): note(M,k*1.0,26,0.9,0.05 if k<20 else 0.06,'tri',dec=2.5)
    for dt,m,dd in A.MOTIF: organ(0.15+dt,m,dd+0.2,0.035)
    for t0,tr,v in ((4.4,-12,0.03),(12.4,-12,0.03),(20.4,0,0.03),(31.8,-12,0.03),(47.8,0,0.04)):
        for dt,m,dd in A.MOTIF: organ(t0+dt*1.3,m+tr,dd+0.4,v)
    for dt,m,dd in A.MOTIF: organ(26.7+END_OFF+dt*1.2,m+12,dd+0.4,0.03)
    for dt,m,dd in A.MOTIF: organ(28.6+END_OFF+dt,m-12,dd+0.3,0.045)
    # hook (replaced by A's samples, kept so the splice level matches)
    for k,ti in enumerate(A.HOOK_IMPACTS): zap(ti,0.3,10+k); step_b(ti-0.1,0.25)
    # the final dungeon: knight's steps, muffled impacts behind the gate
    for k in range(int((7.6-4.0)/0.5)): step_k(4.05+k*0.5,0.045,40+k)
    for k,ti in enumerate(OUT_IMPACTS): zap(ti,0.35,50+k,muffled=True); nb(ti,0.5,300,3000,0.04,60+k); clank(ti+0.02,0.06,61+k)   # dust + gate rattle
    tt=s.T(0.45); s.place(s.filt_short(s.noise(0.45,7),lo=2500,hi=9000)*np.sin(np.pi*tt/0.45)*0.5,7.85,0.05)                   # guard up
    for k in range(4): step_k(9.25+k*0.35,0.045,70+k)
    nb(10.65,0.4,1500,6000,0.03,71)                                                       # fingers over the gouges
    # the strange discovery: heavy steps inside, the shove, the boss thrown back
    for k in range(4): step_b(13.7+k*0.4,0.2)
    zap(POV_IMPACT,0.4,80); thud(POV_IMPACT+0.45,40,0.45,0.8); clank(POV_IMPACT+0.5,0.12,81)
    for k in range(3): note(M,17.95+k*0.12,76+k*3,0.1,0.03,'sq',0.5,12)                   # '?' emote blip
    # the arrival
    clank(21.4,0.18,90); thud(21.85,70,0.25,0.4)                                          # lever
    for k in range(12): nb(21.95+k*0.12,0.1,300,2500,0.04,91+k)                          # chains
    tt=s.T(1.4); s.place(np.sin(2*np.pi*np.cumsum(90+40*np.sin(2*np.pi*1.2*tt))/sr)*np.sin(np.pi*tt/1.4)*0.6+s.filt_short(s.noise(1.4,3),lo=100,hi=900)*0.4,22.0,0.2)
    for k in range(3): step_b(23.95+k*0.5,0.2)
    tt=s.T(0.6); s.place(s.filt_short(s.noise(0.6,18),lo=1800,hi=8000)*np.sin(np.pi*tt/0.6)+np.sin(2*np.pi*np.cumsum(600+900*tt)/sr)*np.exp(-tt*4)*0.3,BOSS_DRAW+0.3,0.1)
    for k in range(4): step_b(17.4+k*0.7,0.12)                                            # boss walks back to the throne
    for k in range(5): step_k(27.0+k*0.34,0.045,110+k)
    chime(27.4,0.03)
    tt=s.T(0.45); s.place(s.filt_short(s.noise(0.45,8),lo=2500,hi=9000)*np.sin(np.pi*tt/0.45)+np.sin(2*np.pi*np.cumsum(2000+2500*tt)/sr)*np.exp(-tt*3)*0.2,27.8,0.08)
    nb(29.5,0.3,200,2000,0.08,120); thud(SLAM,40,0.9,1.4); clank(SLAM+0.02,0.35,121); thud(SLAM+0.15,32,0.5,1.0)
    M[int(SLAM*sr):int((SLAM+0.7)*sr)]*=0.3
    # unexpected behaviour
    tt=s.T(0.8); s.place(np.sin(2*np.pi*np.cumsum(70+20*tt)/sr)*np.exp(-tt*3),31.7,0.12)
    for k in range(9): step_b(33.1+k*0.66,0.22)
    nb(33.3,4.0,1500,6000,0.025,130,shape=1)
    tt=s.T(1.1); s.place(np.sin(2*np.pi*np.cumsum(100+40*np.sin(2*np.pi*1.5*tt))/sr)*np.sin(np.pi*tt/1.1)*0.6,36.8,0.15)
    chime(39.0,0.035)
    sil=np.ones(n); a_,b_=int(39.3*sr),int(40.9*sr); sil[a_:b_]=0.03; k=int(0.03*sr); sil=np.convolve(sil,np.ones(k)/k,'same')
    # escape
    for k in range(7): step_k(42.35+k*0.18,0.06,140+k)
    zap(CRASH,0.32,150); clank(CRASH+0.02,0.25,151); thud(CRASH+0.4,80,0.2,0.4); clank(CRASH+0.42,0.08,152)
    for k,dt in enumerate((0.3,0.42,0.5)): clank(SWORD_DROP+dt,0.1-0.025*k,153+k)
    for k,ti in enumerate(PUSHES): zap(ti,0.22,160+k)
    # reveal
    tt=s.T(2.0); s.place(np.sin(2*np.pi*55*tt)*np.minimum(1,tt/0.6)*np.exp(-tt*1.2)+0.5*np.sin(2*np.pi*82.4*tt)*np.minimum(1,tt/0.6)*np.exp(-tt*1.2),LETTERS_ON,0.18)
    for k in range(5): note(M,BAR_OFF[0]+0.05+k*0.07,84-k*3,0.08,0.03,'sq',0.5,20)
    note(M,BAR_ON,45,0.4,0.08,'sq',0.5,4); note(M,BAR_ON,33,0.6,0.1,'tri',dec=2)
    for k in range(14): note(M,BAR_ON+0.25+k*0.06,57+k,0.06,0.03,'sq',0.25,15)
    note(M,BAR_ON+1.15,69,0.5,0.05,'sq',0.5,4)
    tt=s.T(1.6); s.place(np.sin(2*np.pi*41.2*tt)*np.minimum(1,tt/0.4)*np.exp(-tt*1.5),55.2,0.15)   # the throne is his
    # ending (replaced by A's samples)
    out=np.zeros(n); i0,i1=int((26.6+END_OFF)*sr),int((28.55+END_OFF)*sr); out[i0:i1]=1; out=np.convolve(out,np.ones(1200)/1200,'same')
    for k in range(3): step_b(26.75+END_OFF+k*0.62,0.12)
    # voices
    NB=np.zeros(n); duck=np.ones(n)
    for k_,t0 in [('N1',0.10)]+NARR+[('N9',26.70+END_OFF),('N10',28.62+END_OFF)]:
        a,ar=_sf.read(os.path.join(TTS_DIR,'fb',f'{k_}.wav')); a=a if a.ndim==1 else a.mean(1)
        a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a)
        i=int(t0*sr); j=min(n,i+len(a)); NB[i:j]+=a[:j-i]*(1.15 if k_=='B1' else 1.0)
        duck[max(0,i-int(0.05*sr)):min(n,j+int(0.1*sr))]=0.45
    duck=np.convolve(duck,np.ones(2400)/2400,'same')
    s.L+=(2.2*M*duck+AMB*(1-out))*sil; s.R+=(2.2*np.roll(M,300)*duck+np.roll(AMB,900)*(1-out))*sil
    s.reverb(0.28,length=2.2,decay=2.6)
    pk=max(np.abs(s.L).max(),np.abs(s.R).max()); gv=pk*1.05/np.abs(NB).max()
    s.L=s.L*(0.55+0.45*duck)+NB*gv; s.R=s.R*(0.55+0.45*duck)+NB*gv
    st=np.stack([s.L,s.R],1); st=st/np.max(np.abs(st))*0.9
    # splice A's exact audio for the shared hook and ending (gain-matched, 60 ms crossfades)
    a_wav,asr=_sf.read(os.path.join(OUT,'final_boss_a.wav')); assert asr==sr
    def splice(b0,a0,a1):
        seg_=a_wav[int(a0*sr):int(a1*sr)].copy(); i=int(b0*sr); L_=min(len(seg_),n-i); seg_=seg_[:L_]
        g=np.sqrt((st[i:i+L_]**2).mean()+1e-12)/np.sqrt((seg_**2).mean()+1e-12); seg_*=g
        x=int(0.06*sr); w=np.ones(L_)
        if i>0: w[:x]=np.linspace(0,1,x)
        if i+L_<n: w[-x:]=np.linspace(1,0,x)
        st[i:i+L_]=st[i:i+L_]*(1-w[:,None])+seg_*w[:,None]
    splice(0.0,0.0,4.06); splice(END_START,END_START-END_OFF,A.DUR)
    st=st/np.max(np.abs(st))*0.9
    _sf.write(path,st,sr,subtype='PCM_16'); return path
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'final_boss_b.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'fbb_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.95,vignette=0.3,grain=1.8,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(post.upscale(frame(f/FPS),S),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
