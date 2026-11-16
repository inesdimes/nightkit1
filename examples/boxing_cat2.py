"""BOXING CAT 2.0 - THE LASER TRAP. PS1 fighting-game short, 9:16, same cat model as boxing_cat.py.
Scene 1 (0-4 s): FIGHT! -> punch flurry at the lens -> victory pose + paw taps.
Run: python examples/boxing_cat2.py [SCENES=1]  -> out/boxing_cat2_scene1.mp4"""
import os, sys, math
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, box, quad, transform, rx, ry, rz, tiled_plane, wall_region
from nightkit import motion, post, font, check
from nightkit.audio import Sound
OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6
ORANGE=(214,134,64); ORANGE_D=(176,100,44); CREAM=(236,222,196); WHITE=(246,240,228); PINK=(222,140,140)
sm=motion.smooth
def win(t,a,b,ra=0.15,rb=0.15): return sm((t-a)/ra)*(1-sm((t-b)/rb))
# ---------------- scene 1 timeline ----------------
PUNCH=[(0.05,-1,0.34),(0.45,1,0.34),(0.85,-1,0.34),(1.25,1,0.34),(1.62,-1,0.36)]   # 4 jabs + a heavy finisher
HITS=[a+0.4*d for a,s,d in PUNCH]
def ext(t,t0,d):
    u=(t-t0)/d
    if u<0 or u>1: return 0.0
    if u<0.4: return motion.ease_out(u/0.4)
    if u<0.5: return 1.0
    return 1-sm((u-0.5)/0.5)
def arm_ext(t,side): return max([ext(t,a,d) for a,s,d in PUNCH if s==side]+[0.0])
def shake(t):
    sx=sy=0.0
    for k,th in enumerate(HITS):
        amp=0.05 if k==len(HITS)-1 else 0.016
        if 0<=t-th<0.2:
            q=1-(t-th)/0.2; sx+=amp*q*math.sin(97*t); sy+=amp*q*math.cos(71*t)
    return sx,sy
UP1=(2.3,3.05); TAPS=(3.25,3.45); UP2=3.65
FREEZE=4.0; DOT=(0.13,0.004,0.0)                                     # laser dot appears beside the right foot
def look(t): return sm((t-4.12)/0.3)
def pop(t): return sm((t-4.3)/0.1)                  # victory pose, two paw taps, victory pose again (hand-off to scene 2)
# ---------------- geometry helpers ----------------
def seg(p0,p1,w0,w1,col,depth=None):
    p0=np.array(p0,float); p1=np.array(p1,float); d=p1-p0; L=np.linalg.norm(d)+1e-9; d/=L
    up=np.array([0,0,-1.0]) if abs(d[1])>0.9 else np.array([0,1.0,0])
    a=np.cross(d,up); a/=np.linalg.norm(a)+1e-9; b=np.cross(a,d)
    d0=depth or w0; d1=depth or w1
    v=[p0-a*w0/2-b*d0/2,p0+a*w0/2-b*d0/2,p0+a*w0/2+b*d0/2,p0-a*w0/2+b*d0/2,
       p1-a*w1/2-b*d1/2,p1+a*w1/2-b*d1/2,p1+a*w1/2+b*d1/2,p1-a*w1/2+b*d1/2]
    F=[(0,1,2,3),(5,4,7,6),(4,0,3,7),(1,5,6,2),(3,2,6,7),(4,5,1,0)]
    return [quad([tuple(v[i]) for i in f],col) for f in F]
def tri(a,b,c,col,emit=False): return quad([a,b,c],col,emit)
def ear(sx,perk=0.0,droop=0.0):
    x=sx*0.048; base=[(x-0.03,0.055,-0.02),(x+0.03,0.055,-0.02),(x,0.055,0.03)]; tip=(x+sx*(0.012+0.045*droop),0.125+0.01*perk-0.05*droop,-0.005-0.035*perk+0.01*droop)
    Q=[tri(base[0],base[1],tip,ORANGE),tri(base[1],base[2],tip,ORANGE_D),tri(base[2],base[0],tip,ORANGE_D)]
    Q.append(tri((x-0.018,0.062,-0.024),(x+0.018,0.062,-0.024),(x+sx*(0.01+0.035*droop),0.108+0.008*perk-0.04*droop,-0.012-0.03*perk),PINK))
    return Q
def head(blink,eye=1.0,glint=0.0,perk=0.0,droop=0.0):
    Q=box(-0.08,0.08,-0.06,0.06,-0.065,0.065,ORANGE)
    Q+=box(-0.082,0.082,0.045,0.062,-0.06,0.05,ORANGE_D)                          # darker stripe on top
    Q+=box(-0.035,0.035,-0.055,-0.02,-0.085,-0.06,CREAM)
    Q+=box(-0.095,-0.075,-0.05,0.01,-0.04,0.03,ORANGE)+box(0.075,0.095,-0.05,0.01,-0.04,0.03,ORANGE)                              # muzzle
    Q+=box(-0.012,0.012,-0.022,-0.008,-0.093,-0.088,PINK)                          # nose
    for sx in (-1,1):
        x=sx*0.036
        if blink: Q+=box(x-0.016,x+0.016,0.008,0.014,-0.068,-0.066,(30,20,14))
        else:
            e=0.016*eye; cy=0.011+0.004*(eye-1)
            Q+=box(x-e,x+e,cy-e,cy+e,-0.075,-0.066,(18,14,10))
            hc=(255,int(255-185*glint),int(240-200*glint)); hs=0.008*(1+0.6*(eye-1)); hx=x+sx*0.004*eye; hy=cy+0.003*eye
            Q.append(quad([(hx-hs,hy,-0.0765),(hx,hy,-0.0765),(hx,hy+hs,-0.0765),(hx-hs,hy+hs,-0.0765)],hc,emit=True))
        Q+=ear(sx,perk,droop)
    return Q
def paw(c,col=WHITE,s=0.026): return box(c[0]-s,c[0]+s,c[1]-s,c[1]+s,c[2]-s,c[2]+s,col)
def cat(t):
    T0=t; t=min(t,FREEZE); lk=look(T0); pp=pop(T0)
    hop=sm((t-2.0)/0.3)                                           # hops one step back after the flurry
    weave=0.03*math.sin(2*math.pi*t*2.4)*(1-sm((t-1.9)/0.2))
    root=np.array([weave,0.012*abs(math.sin(math.pi*(t-2.0)/0.3)) if 2.0<=t<=2.3 else 0.0,0.09*hop])
    lean=0.05*math.sin(2*math.pi*t*1.2)*(1-hop)+weave*1.5
    proud=sm((t-2.3)/0.3)                                         # chest out, leaning back
    fwd=-0.10*proud+0.06*(1-hop)*max(arm_ext(t,-1),arm_ext(t,1))
    bob=0.008*math.sin(2*math.pi*t*2.0)
    def Wd(p,lf=0.0):
        p=rz(p,lean,(0,0,0)); p=rx(p,-lf,(0,0.1,0)); return (p[0]+root[0],p[1]+root[1]+bob,p[2]+root[2])
    Q=[]
    for sx in (-1,1):
        Q+=transform(box(sx*0.06-0.05,sx*0.06+0.05,0.03,0.16,-0.05,0.07,ORANGE),Wd)
        Q+=transform(box(sx*0.06-0.03,sx*0.06+0.03,0.0,0.03,-0.08,0.03,WHITE),Wd)
    Q+=transform(seg((0,0.10,0.01),(0,0.37,-0.01),0.18,0.15,ORANGE,depth=0.13),lambda p:Wd(p,fwd))
    Q+=transform(seg((0,0.13,-0.062),(0,0.34,-0.074),0.085,0.07,CREAM,depth=0.012),lambda p:Wd(p,fwd))
    Q+=transform(box(-0.065,0.065,0.33,0.43,-0.075,0.03,ORANGE),lambda p:Wd(p,fwd))
    Q+=transform(box(-0.04,0.04,0.33,0.41,-0.079,-0.07,CREAM),lambda p:Wd(p,fwd))
    flick=1+2.5*win(t,2.3,3.1,0.1,0.2)                             # proud tail flick
    tail=[(0.0,0.08,0.07)]; stiff=sm((T0-4.25)/0.12)
    for k in range(1,6):
        a=(0.06*k*0.45+0.03*math.sin(2*math.pi*t*1.5*flick+k*0.6),0.08+0.055*k,0.07+0.02*k); b=(0.0,0.08+0.06*k,0.075)
        tail.append(motion.lerpv(a,b,stiff))
    for a,b in zip(tail,tail[1:]): Q+=transform(seg(a,b,0.035,0.03,ORANGE_D if tail.index(a)%2 else ORANGE),Wd)
    hp=(0,0.46,-0.03)
    smug=0.09*proud*(1-0.6*win(t,TAPS[0]-0.15,TAPS[1]+0.2))
    tilt=0.08*math.sin(2*math.pi*t*1.6)*(1-proud)+lean*0.5+0.12*proud
    blink=any(abs(t-b)<0.05 for b in (1.95,3.0))
    if T0>FREEZE: blink=False
    hd=head(blink,eye=1+0.5*pp,glint=pp,perk=pp)
    Q+=transform(hd,lambda p:Wd(ry(rx(rz((p[0]+hp[0],p[1]+hp[1],p[2]+hp[2]),tilt*(1-lk),hp),smug*(1-lk)-0.3*lk,hp),-0.18*lk,hp),fwd))
    up=sm((t-UP1[0])/0.3)*(1-sm((t-UP1[1])/0.2))+sm((t-UP2)/0.3)
    tapzone=win(t,UP1[1],UP2,0.2,0.2)
    for sx in (-1,1):
        e=arm_ext(t,sx); sh=(sx*0.075,0.345,-0.03)
        guard=(sx*0.075,0.385,-0.10); hit=(sx*0.02,0.40,-0.30)
        p=motion.lerpv(guard,hit,e)
        meet=max(0.0,math.sin(math.pi*(t-TAPS[0])/0.1)) if TAPS[0]<=t<TAPS[1]+0.1 else 0.0
        tap=(sx*(0.07-0.055*meet),0.33,-0.15)
        p=motion.lerpv(p,tap,tapzone)
        vic=(sx*(0.11+0.02*math.sin(t*9+sx)),0.61,-0.03)
        p=motion.lerpv(p,vic,min(1.0,up))
        el=((sh[0]+p[0])/2+sx*0.035,(sh[1]+p[1])/2-0.05*(1-e)*(1-up),(sh[2]+p[2])/2)
        Q+=transform(seg(sh,el,0.05,0.045,ORANGE),lambda q:Wd(q,fwd))
        Q+=transform(seg(el,p,0.045,0.042,ORANGE if e<0.5 else ORANGE_D),lambda q:Wd(q,fwd))
        Q+=transform(paw(p),lambda q:Wd(q,fwd))
    return Q
# ---------------- scene 3: chase, leap, splat on the shutter, slide, flop ----------------
IMPACT=6.85
def nrm(v): v=np.array(v,float); return v/(np.linalg.norm(v)+1e-9)
def basis(f,u):
    f=nrm(f); u=np.array(u,float); u=nrm(u-(u@f)*f); return np.stack([f,u,np.cross(f,u)],1)
POSE=dict(stand=((0.10,-0.125,0.06),(-0.11,-0.13,0.06)),crouch=((0.13,-0.09,0.065),(-0.07,-0.085,0.07)),
          leap=((0.21,-0.01,0.05),(-0.23,-0.03,0.05)),splat=((0.14,-0.04,0.16),(-0.14,-0.04,0.16)),
          back=((0.08,-0.17,0.07),(-0.08,-0.16,0.07)))
#      time  centre               forward        up           pose     squash pitch faceCam
KEYS=[(5.00,(0.0,0.115,0.0),(-1,-0.18,0),(0,1,0),'crouch',0.0,0.15,0.0),
      (5.35,(0.0,0.115,0.0),(-1,-0.18,0),(0,1,0),'crouch',0.0,0.15,0.0),
      (5.45,(-0.05,0.13,0.0),(-1,0,0),(0,1,0),'stand',0.0,0.0,0.0),
      (6.25,(-0.86,0.13,0.0),(-1,0,0),(0,1,0),'stand',0.0,0.0,0.0),
      (6.35,(-0.88,0.10,0.0),(-1,0.35,0),(0,1,0),'crouch',0.0,0.45,0.0),
      (6.55,(-0.88,0.10,0.0),(-1,0.35,0),(0,1,0),'crouch',0.0,0.45,0.0),
      (6.83,(-1.28,0.66,0.0),(-0.6,0.8,0),(0,1,0),'leap',0.0,0.2,0.0),
      (IMPACT,(-1.335,0.70,0.0),(0,1,0),(1,0,0),'splat',1.0,0.0,1.0),
      (7.25,(-1.335,0.70,0.0),(0,1,0),(1,0,0),'splat',1.0,0.0,1.0),
      (7.60,(-1.335,0.24,0.0),(0,1,0),(1,0,0),'splat',1.0,0.0,1.0),
      (7.85,(-1.10,0.075,0.0),(1,0,0),(0,-1,0),'back',0.25,0.0,1.0),
      (9.99,(-1.10,0.075,0.0),(1,0,0),(0,-1,0),'back',0.25,0.0,1.0)]
def keystate(t):
    for a,b in zip(KEYS,KEYS[1:]):
        if a[0]<=t<=b[0]:
            u=sm((t-a[0])/(b[0]-a[0])) if b[0]>a[0] else 1.0
            if a[4]=='crouch' and b[4]=='leap': u=(t-a[0])/(b[0]-a[0])
            C=np.array(motion.lerpv(a[1],b[1],u))
            if a[4]=='crouch' and b[4]=='leap': C[1]+=0.14*math.sin(math.pi*u)
            if a[4]=='splat' and b[4]=='back': C[1]+=0.12*math.sin(math.pi*u)
            f=motion.lerpv(a[2],b[2],u); up=motion.lerpv(a[3],b[3],u)
            pa,pb=POSE[a[4]],POSE[b[4]]
            fr=motion.lerpv(pa[0],pb[0],u); hi=motion.lerpv(pa[1],pb[1],u)
            return C,f,up,fr,hi,a[5]+(b[5]-a[5])*u,a[6]+(b[6]-a[6])*u,a[7]+(b[7]-a[7])*u
    return keystate(KEYS[-1][0]-1e-3)
def cat3(t):
    C,f,up,fr,hi,sq,pitch,facecam=keystate(t)
    run=5.45<=t<6.25; tau=t-5.45
    if 5.0<=t<5.35:                                                 # butt wiggle before the sprint
        a=0.18*math.sin(2*math.pi*7*(t-5.0)); f=(f[0]*math.cos(a),f[1],math.sin(a))
    if run:
        C=C+np.array([0,0.045*abs(math.sin(math.pi*5*tau)),0]); f=(f[0],f[1]+0.12*math.cos(2*math.pi*5*tau),f[2])
    if t>=7.85:
        C=C+np.array([0,0.025*abs(math.sin(math.pi*(t-7.85)/0.12))*(t<7.97),0])
    Rb=basis(f,up)
    if t>=IMPACT: sq=sq*(1+0.3*math.sin(45*(t-IMPACT))*math.exp(-(t-IMPACT)*7))
    Sd=np.array([1+0.05*sq,1-0.45*sq,1+0.25*sq])
    def L2W(p): return tuple(C+Rb@(Sd*np.array(p,float)))
    Q=[]
    Q+=seg((-0.12,0.0,0.0),(0.10,0.01,0.0),0.15,0.14,ORANGE,depth=0.13)
    Q+=seg((-0.09,-0.066,0.0),(0.08,-0.066,0.0),0.085,0.075,CREAM,depth=0.012)
    Q+=box(0.07,0.15,-0.05,0.06,-0.065,0.065,ORANGE)+box(0.15,0.154,-0.05,0.02,-0.04,0.04,CREAM)
    dazed=t>=IMPACT
    hd=head(dazed,eye=1.0 if dazed else 1.5,glint=0.0 if dazed else 1.0,perk=0.0 if dazed else 1.0)
    hc=(0.21,0.075,0.0); yaw=-math.pi/2-(math.pi/2)*facecam
    roll=0.25*math.sin(t*9) if t>=7.85 else 0.0
    Q+=transform(hd,lambda p:(lambda q:(q[0]+hc[0],q[1]+hc[1],q[2]+hc[2]))(ry(rz(rx(p,pitch),roll),yaw)))
    tl=[(-0.12,0.03,0.0)]
    for k in range(1,6):
        wag=0.025*math.sin(t*14+k*0.8) if run else 0.0
        stiff=0.0 if t>=IMPACT else 1.0
        tl.append((-0.12-0.045*k,0.03+(0.04*stiff+0.005)*k,wag+(0.0 if stiff else 0.015*k)))
    for a,b in zip(tl,tl[1:]): Q+=seg(a,b,0.035,0.03,ORANGE_D if tl.index(a)%2 else ORANGE)
    for sz in (-1,1):
        g=2*math.pi*5*tau
        dxf=0.07*math.sin(g) if run else 0.0; lf=0.03*max(0.0,math.sin(g)) if run else 0.0
        tw=0.02*math.sin(t*20+sz) if t>=7.85 else 0.0
        sh=(0.08,-0.04,sz*0.055); pf=(fr[0]+dxf,fr[1]+lf+tw,sz*fr[2])
        Q+=seg(sh,pf,0.045,0.042,ORANGE)+paw(pf)
        hp_=(-0.09,-0.04,sz*0.06); ph=(hi[0]-dxf,hi[1]+0.03*max(0.0,-math.sin(g))*run+tw,sz*hi[2])
        Q+=seg(hp_,ph,0.07,0.06,ORANGE)+box(ph[0]-0.035,ph[0]+0.03,ph[1]-0.015,ph[1]+0.015,ph[2]-0.03,ph[2]+0.03,WHITE)
    return transform(Q,L2W)
def dot_pos(t):
    j=(0.003*math.sin(t*31)+0.002*math.sin(t*53),0.002*math.sin(t*41))
    if 4.0<=t<5.0: return (DOT[0]+j[0],DOT[1],DOT[2])
    if 5.0<=t<5.3: return (-0.27+j[0],0.004,0.0)
    if 5.3<=t<5.52: u=motion.ease_in((t-5.3)/0.22); return (-0.27-1.11*u,0.004,0.0)
    if 5.52<=t<5.75: u=sm((t-5.52)/0.23); return (-1.392,0.004+0.776*u,0.0)
    if 5.75<=t<IMPACT: return (-1.392,0.78+j[1],j[0])
    return None
def camera3(t):
    C=keystate(min(t,6.25))[0]; cx=max(-0.86,min(0.0,C[0])); hold=sm((t-6.25)/0.4)
    sx=sy=0.0
    for th,amp in ((IMPACT,0.035),(7.85,0.015)):
        if 0<=t-th<0.25: q=1-(t-th)/0.25; sx+=amp*q*math.sin(97*t); sy+=amp*q*math.cos(71*t)
    runpos=(cx+0.22,0.2,-0.78); runtgt=(cx-0.3,0.15,0.3)
    hpos=(-0.42,0.42,-0.72); htgt=(-1.36,0.42,0.08)
    pos=motion.lerpv(runpos,hpos,hold); tgt=motion.lerpv(runtgt,htgt,hold); pos=(pos[0]+sx,pos[1]+sy,pos[2])
    return Camera.look(pos,tgt)
def cat_health(t): return 1.0-sm((t-IMPACT)/0.25)
# ---------------- scene 4: dazed, YOU WIN! ----------------
SIT=(-1.1,0.0,0.05); SIT_YAW=-0.95; END4=8.0
def sit_world(p): q=ry(p,SIT_YAW); return (q[0]+SIT[0],q[1]+SIT[1],q[2]+SIT[2])
def cat4(t):
    u=t-END4; slump=sm((u-0.95)/0.3)
    wa=0.13*math.sin(2*math.pi*1.1*u); wb=0.10*math.cos(2*math.pi*1.1*u)
    fwd=0.08+0.12*slump
    def Wl(p): return rx(p,-fwd,(0,0.05,0))
    Q=[]
    for sx in (-1,1):
        Q+=box(sx*0.065-0.05,sx*0.065+0.05,0.0,0.09,-0.13,0.03,ORANGE)+box(sx*0.065-0.032,sx*0.065+0.032,0.0,0.035,-0.17,-0.12,WHITE)
    Q+=transform(seg((0,0.05,0.02),(0,0.31,0.0),0.18,0.15,ORANGE,depth=0.13),Wl)
    Q+=transform(seg((0,0.08,-0.05),(0,0.29,-0.067),0.085,0.07,CREAM,depth=0.012),Wl)
    Q+=transform(box(-0.065,0.065,0.27,0.37,-0.075,0.03,ORANGE),Wl)+transform(box(-0.04,0.04,0.27,0.35,-0.079,-0.07,CREAM),Wl)
    hp=(0,0.40,-0.03)
    Q+=transform(head(True,droop=1.0),lambda p:Wl(rx(rz((p[0]+hp[0],p[1]+hp[1],p[2]+hp[2]),wa,hp),wb-0.22*slump,hp)))
    for sx in (-1,1):
        sh=(sx*0.075,0.29,-0.03); pw=(sx*0.045,0.15-0.02*slump,-0.12)
        el=(sx*0.1,0.21,-0.08)
        Q+=transform(seg(sh,el,0.05,0.045,ORANGE)+seg(el,pw,0.045,0.042,ORANGE)+paw(pw),Wl)
    tl=[(0.0,0.035,0.08)]
    for k in range(1,6): tl.append((0.045*k*0.8+0.01*math.sin(u*3+k),0.025,0.08+0.04*k-0.006*k*k))
    for a,b in zip(tl,tl[1:]): Q+=seg(a,b,0.035,0.03,ORANGE_D if tl.index(a)%2 else ORANGE)
    return transform(Q,sit_world)
def camera4(t):
    u=sm((t-END4)/2.0); d=0.82-0.14*u; dirc=(0.81,-0.58)
    return Camera.look((SIT[0]+dirc[0]*d,0.24,SIT[2]+dirc[1]*d),(SIT[0],0.40-0.02*u,SIT[2]))
def star(d,cx,cy,r,col):
    pts=[]
    for k in range(10):
        a=-math.pi/2+k*math.pi/5; rr=r if k%2==0 else r*0.45; pts.append((cx+rr*math.cos(a),cy+rr*math.sin(a)))
    d.polygon(pts,fill=col,outline=(0,0,0))
# ---------------- street ----------------
def street():
    import random; Rr=random.Random(4); Q=[]
    Q+=tiled_plane(-1.4,6.0,-1.5,40,0,0.5,lambda i,j:(46,44,42) if i<4 else ((38,38,40) if (i+j)%2 else (42,42,44)))
    Q+=box(-1.4,6.0,0.0,0.015,1.2,1.35,(200,190,60))                                # yellow kerb line
    for z in np.arange(1.6,30,1.4): Q+=box(-1.35,-1.2,0,0.32,z,z+0.12,(220,200,60) if int(z*10)%3 else (230,230,224))   # bollards
    Q+=wall_region('x',-1.4,-1.5,40,0,0.5,1.0,0.5,lambda i,j,v:(70,70,74),facing=1)
    Q+=wall_region('x',-1.4,-1.5,8,0.5,3.4,0.5,0.12,lambda i,j,v:(150,152,156) if j%2 else (128,130,136),facing=1)  # roller shutter
    Q+=wall_region('x',-1.4,8,40,0.5,6.0,2.0,1.0,lambda i,j,v:(54,54,60),facing=1)
    for z in np.arange(9,38,4):                                                     # shop windows
        Q.append(quad([(-1.39,0.6,z),(-1.39,0.6,z+2),(-1.39,2.2,z+2),(-1.39,2.2,z)],(240,220,170) if Rr.random()<0.5 else (90,110,140),emit=True))
    for k in range(5):                                                              # parked white cars
        x=2.2+(k%2)*1.8; z=10+k*4.5
        Q+=box(x-0.8,x+0.8,0.15,0.75,z,z+3.6,(206,208,212))+box(x-0.7,x+0.7,0.75,1.2,z+0.8,z+2.6,(150,156,166))
        Q.append(quad([(x-0.7,0.5,z-0.01),(x-0.4,0.5,z-0.01),(x-0.4,0.62,z-0.01),(x-0.7,0.62,z-0.01)],(255,250,220),emit=True))
        Q.append(quad([(x+0.4,0.5,z-0.01),(x+0.7,0.5,z-0.01),(x+0.7,0.62,z-0.01),(x+0.4,0.62,z-0.01)],(255,250,220),emit=True))
    lamps=[]
    for z in (6,16,26,36):                                                          # street lamps + wet reflections
        Q+=box(3.9,4.0,0,5.0,z,z+0.1,(60,60,60)); Q.append(quad([(3.6,5.0,z-0.2),(4.2,5.0,z-0.2),(4.2,5.0,z+0.3),(3.6,5.0,z+0.3)],(255,214,140),emit=True))
        Q.append(quad([(3.7,0.004,z-3.5),(4.1,0.004,z-3.5),(4.1,0.004,z+0.3),(3.7,0.004,z+0.3)],(120,96,60),emit=True))
        lamps.append(((3.95,4.8,z),(255,200,130),3.2))
    for z in np.arange(3,30,0.6): Q+=box(1.0,1.35,0,0.008,z,z+0.08,(70,72,76))       # drain grate stripes
    Q+=box(-1.4,8,0,14,45,46,(26,28,36))                                            # far buildings
    for k in range(40):
        x=Rr.uniform(-1,7.5); y=Rr.uniform(4,13)
        Q.append(quad([(x,y,44.9),(x+0.5,y,44.9),(x+0.5,y+0.6,44.9),(x,y+0.6,44.9)],(255,230,170),emit=True))
    return Q,lamps
STREET,LAMPS=street()
# ---------------- HUD ----------------
def you_health(t):
    h=1.0-0.16*sum(1 for th in HITS if t>=th)
    if t>=2.0: h-=0.05*sm((t-2.0)/1.5)                             # bleeds down to 15 percent
    return max(0.0,h)
def otext(d,s,x,y,col,sc):
    o=max(1,sc//2)
    for ox,oy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)): font.text(d,s,x+ox*o,y+oy*o,(0,0,0),sc,None)
    font.text(d,s,x,y,col,sc,None)
def hud(img,t,vi=None):
    d=ImageDraw.Draw(img)
    for x0,name,hlt,right in ((8,'CAT',cat_health(t),False),(98,'YOU',you_health(t),True)):
        d.rectangle([x0-1,13,x0+74,21],fill=(10,10,10)); d.rectangle([x0,14,x0+73,20],fill=(120,10,10))
        w=int(73*hlt)
        if w>0:
            col=(250,210,40) if hlt>0.3 or int(t*8)%2 else (255,90,40)
            if right: d.rectangle([x0+73-w,14,x0+73,20],fill=col)
            else: d.rectangle([x0,14,x0+w,20],fill=col)
        font.text(d,name,x0 if not right else x0+73-font.width(name),25,(255,255,255))
    if t<0.75:
        sc=4 if t>0.08 else 5; s='FIGHT!'; otext(d,s,(W-font.width(s,sc))//2,120,(255,214,40),sc)
    for th in HITS:                                                 # small hit sparks at the lens
        if 0<=t-th<0.1:
            k=HITS.index(th); cx=90+(-22 if PUNCH[k][1]<0 else 22); cy=150
            for a in range(8):
                ang=a*math.pi/4; d.line([cx+6*math.cos(ang),cy+6*math.sin(ang),cx+16*math.cos(ang),cy+16*math.sin(ang)],fill=(255,240,180),width=2)
    if IMPACT+0.05<=t<END4 and int((t-IMPACT)*8)%2==0: otext(d,'K.O.',(W-font.width('K.O.',4))//2,52,(255,60,40),4)
    if t>=END4 and vi is not None:
        u=t-END4; top=sit_world((0,0.56,-0.03))
        pts=[]
        for k in range(3):
            a=2*math.pi*(1.2*u+k/3); P=(top[0]+0.085*math.cos(a),top[1]+0.012*math.sin(2*a),top[2]+0.085*math.sin(a))
            q=R.project(P,vi)
            if q: pts.append((q[2],q))
        for _,q in sorted(pts,reverse=True): star(d,q[0],q[1],max(4,int(4.0/q[2])),(255,228,60))
        if int(u*4)%4!=3: otext(d,'YOU WIN!',(W-font.width('YOU WIN!',3))//2,64,(255,214,40),3)
    if 4.3<=t<4.75 and vi is not None:
        q=R.project((0.0,0.66,0.0),vi)
        if q: otext(d,'!',int(q[0])-2,int(q[1])-8-int(3*sm((t-4.3)/0.08)),(255,60,50),2)
    return img
def laser(img,t,vi):
    dp=dot_pos(t)
    if dp is None or vi is None: return img
    q=R.project(dp,vi)
    if not q: return img
    a=np.asarray(img).astype(np.float32); yy,xx=np.mgrid[0:H,0:W]; r2=(xx-q[0])**2+((yy-q[1])*1.6)**2
    fl=0.85+0.15*math.sin(t*40)
    g=(np.exp(-r2/40.0)[...,None]*np.array([200,20,15])+np.exp(-r2/6.0)[...,None]*np.array([255,60,40])+np.exp(-r2/1.5)[...,None]*np.array([255,230,220]))*fl
    return Image.fromarray(np.clip(a+g,0,255).astype(np.uint8))
# ---------------- render ----------------
R=Renderer(W,H,fog=(14,15,24))
def frame(t):
    sx,sy=shake(t); push=sm((t-2.0)/2.0); zoom=sm((t-4.4)/0.6)
    pos=(0.0+sx,0.29+sy+0.12*zoom,-0.43+0.15*zoom); tgt=(0.0,0.37*(1-zoom)+0.45*zoom,0.6*(1-zoom)+0.0*zoom)
    c=Camera.look(pos,tgt)
    if t>=5.0: c=camera3(t)
    if t>=END4: c=camera4(t)
    lights=LAMPS+[((-0.4,0.8,-1.1),(255,226,190),0.75),((-1.0,2.5,1.0),(200,210,255),0.6)]
    img,vi=R.render(c,[STREET,cat4(t) if t>=END4 else (cat3(t) if t>=5.0 else cat(t))],lights,fov=58,fog_start=4,fog_end=46,ambient=0.10)
    img=post.ps1(laser(img,t,vi))
    if any(abs(t-th)<1.0/FPS for th in HITS[-1:]+[IMPACT]): img=img.point(lambda v:min(255,v+80))
    return hud(img,t,vi)
DUR=float(os.environ.get('END','10.0')); N=int(DUR*FPS)
TEST=os.environ.get('TEST')
if TEST:
    ims=[frame(float(x)) for x in TEST.split(',')]; sh=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): sh.paste(im,(i*182,0))
    sh.resize((sh.width*2,640),Image.NEAREST).save('test.png'); sys.exit()
# ---------------- sound: 8-bit fight music + hits ----------------
s=Sound(DUR,loop=False,seed=12)
def sqv(f,d,duty=0.5):
    tt=s.T(d); ph=(f*tt)%1; return np.where(ph<duty,1.0,-1.0)
BPM=150; st=60/BPM/4
bass=[45,45,57,45,48,48,60,48,43,43,55,43,47,47,59,50]
lead=[69,72,76,72,69,72,76,79,67,71,74,71,71,74,78,74]
for i in range(int(DUR/st)):
    t0=i*st; f=440*2**((bass[i%16]-69)/12)
    s.place(s.filt_short(sqv(f,st*0.9),hi=1400)*np.exp(-s.T(st*0.9)*5),t0,0.05)
    if i%2==0:
        f=440*2**((lead[(i//2)%16]-69)/12); s.place(sqv(f,st*1.6,0.25)*np.exp(-s.T(st*1.6)*7),t0,0.022)
for i in range(int(DUR/(st*4))):                                   # kick + hat
    tt=s.T(0.12); s.place(np.sin(2*np.pi*(120-60*tt/0.12)*tt)*np.exp(-tt*30),i*st*4,0.12)
    s.place(s.filt_short(s.noise(0.03,i),lo=6000)*np.exp(-s.T(0.03)*120),i*st*4+st*2,0.05)
def whoosh(t0,d=0.13,v=0.22,seed=1):
    x=s.filt_short(s.noise(d,seed),lo=400,hi=3500)*np.sin(np.pi*s.T(d)/d)**2; s.place(x,t0,v)
def impact(t0,v=0.5,f=90,seed=2):
    tt=s.T(0.22); x=np.sin(2*np.pi*f*tt*(1-0.4*tt))*np.exp(-tt*22)+s.filt_short(s.noise(0.22,seed),lo=300,hi=4000)*np.exp(-tt*45)*0.6
    s.place(x,t0,v)
def chip(t0,notes,step=0.07,v=0.07,duty=0.5):
    for i,m in enumerate(notes):
        f=440*2**((m-69)/12); s.place(sqv(f,step*1.6,duty)*np.exp(-s.T(step*1.6)*9),t0+i*step,v)
mute=np.ones(s.n); mute[int(FREEZE*s.sr):]=0.0; s.L*=mute; s.R*=mute          # music stops dead at the laser
chip(0.0,[79,84],0.05,0.06)                                         # FIGHT! sting
for k,(a,sd,d) in enumerate(PUNCH):
    whoosh(a,0.12,0.2,seed=10+k); impact(HITS[k],0.5 if k<4 else 0.9,95+8*(k%3) if k<4 else 60,seed=40+k)
chip(HITS[-1]+0.03,[60,55],0.05,0.05)
chip(UP1[0]+0.05,[72,76,79,84],0.06,0.06,0.25)                      # ta-da
for k in range(2):
    tt=s.T(0.05); s.place(s.filt_short(s.noise(0.05,70+k),lo=800,hi=5000)*np.exp(-tt*80),TAPS[0]+0.05+k*0.1,0.25)
chip(UP2+0.05,[84,88],0.05,0.04,0.25)
tt=s.T(0.6); s.place(np.sin(2*np.pi*2350*tt)*np.exp(-tt*9)+0.3*np.sin(2*np.pi*4700*tt)*np.exp(-tt*14),FREEZE+0.02,0.05)   # tiny ding
tt=s.T(0.18); s.place(np.sin(2*np.pi*np.cumsum(500+2200*tt/0.18)/s.sr)*np.sin(np.pi*tt/0.18),4.3,0.06)                    # eye pop
air=s.filt(s.rng.normal(0,1,s.n),lo=100,hi=700)*0.008*(s.t>=FREEZE); s.L+=air; s.R+=air
def music(t0,t1,bpm,v=1.0):
    st_=60/bpm/4; i=0; L0,R0=s.L.copy(),s.R.copy()
    while t0+i*st_<t1:
        tt0=t0+i*st_; f=440*2**((bass[i%16]-69)/12)
        s.place(s.filt_short(sqv(f,st_*0.9),hi=1400)*np.exp(-s.T(st_*0.9)*5),tt0,0.05*v)
        if i%2==0: f=440*2**((lead[(i//2)%16]-69)/12); s.place(sqv(f,st_*1.6,0.25)*np.exp(-s.T(st_*1.6)*7),tt0,0.024*v)
        if i%4==0: tt=s.T(0.1); s.place(np.sin(2*np.pi*(120-60*tt/0.1)*tt)*np.exp(-tt*30),tt0,0.12*v)
        i+=1
    g=np.ones(s.n); g[int(t1*s.sr):]=0; s.L=L0+(s.L-L0)*g; s.R=R0+(s.R-R0)*g
if DUR>5.0:
    music(5.0,IMPACT,260)                                             # same tune, double time, cut dead on impact
    sweep_t=s.T(0.22); s.place(np.sin(2*np.pi*np.cumsum(900+2600*sweep_t/0.22)/s.sr)*np.sin(np.pi*sweep_t/0.22),5.3,0.05)    # laser zip
    for k in range(4):                                                # paw patter
        for j in range(2): s.place(s.filt_short(s.noise(0.03,90+k*2+j),lo=300,hi=2500)*np.exp(-s.T(0.03)*90),5.45+k*0.2+j*0.04,0.16)
    tt=s.T(0.25); s.place(np.sin(2*np.pi*np.cumsum(220+500*tt/0.25)/s.sr)*np.exp(-tt*4),6.55,0.12)                      # boing
    tt=s.T(0.6); clang=sum(np.sin(2*np.pi*f*tt)*np.exp(-tt*dk) for f,dk in ((317,6),(523,8),(861,10),(1290,14)))
    s.place(clang*0.5+np.sin(2*np.pi*55*tt)*np.exp(-tt*12)*1.2,IMPACT,0.35)                                           # SPLAT on the shutter
    rat=s.filt_short(s.noise(0.7,123),lo=200,hi=3000)*(0.5+0.5*np.sign(np.sin(2*np.pi*22*s.T(0.7))))*np.exp(-s.T(0.7)*5); s.place(rat,IMPACT+0.02,0.22)
    chip(IMPACT+0.08,[72,67,63,60,55,48],0.08,0.06)                    # arcade K.O.
    tt=s.T(0.35); s.place(np.sin(2*np.pi*np.cumsum(1300-850*tt/0.35+40*np.sin(tt*60))/s.sr)*0.6,7.25,0.05)              # squeaky slide
    s.thud(7.82,f=70,v=0.35); s.thud(7.95,f=80,v=0.12)
if DUR>END4:
    chip(END4+0.05,[72,76,79,84,79,84],0.09,0.06,0.25)               # ironic victory jingle
    for k in range(int((DUR-END4-0.2)/0.33)):                         # dizzy birdie chirps
        tt=s.T(0.07); s.place(np.sin(2*np.pi*np.cumsum(3000+700*tt/0.07)/s.sr)*np.sin(np.pi*tt/0.07),END4+0.15+k*0.33,0.025,pan=0.4*math.sin(k*2.1))
    def meow(t0,d=0.75,v=0.3):
        tt=s.T(d); u=tt/d
        f0=np.where(u<0.28,470+290*(u/0.28),760-430*np.clip((u-0.28)/0.72,0,1))*(1+0.018*np.sin(2*np.pi*6*tt))
        ph=2*np.pi*np.cumsum(f0)/s.sr; x=sum((1/h**0.8)*np.sin(h*ph) for h in range(1,10))
        env=np.minimum(1,tt/0.07)*np.exp(-np.maximum(0,tt-0.4)*5)
        x=s.filt_short(x*env,lo=350,hi=3200); x=np.round(x/np.max(np.abs(x))*48)/48; s.place(x,t0,v)
    meow(END4+0.75)
    s.place(s.filt_short(s.noise(0.5,321),lo=200,hi=1500)*np.sin(np.pi*s.T(0.5)/0.5)**2,END4+0.95,0.06)  # slump sigh
s.reverb(0.15,length=0.7,decay=6)
wav=s.save(os.path.join(OUT,'boxing_cat2.wav'),peak=0.85)
vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,vignette=0.35,grain=2.5,band_period=1e9)
mp4=os.path.join(OUT,'boxing_cat2.mp4')
with post.Encoder(mp4,W*S,H*S,wav,FPS,DUR) as enc:
    for f in range(N): enc.write(vhs(post.upscale(frame(f/FPS),S),f,f/FPS))
print('probe',check.probe(mp4))
