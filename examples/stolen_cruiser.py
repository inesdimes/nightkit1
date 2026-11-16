"""THE WORST ARREST IN GTA HISTORY - PS1 GTA parody, 17.5 s, 9:16. Same suspect car / officer / driver models as npc_exit.py.
Hook (the stolen cruiser) -> rewind -> GET OUT! -> pulled through the window -> dragged and flung beside the open cruiser
-> officer celebrates -> driver steals the cruiser -> officer chases on foot. Run: python examples/stolen_cruiser.py"""
import os, sys, math
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, box, quad, tiled_plane, transform, rx, ry
from nightkit import motion, post, font, check
from nightkit.audio import Sound
OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6
sm=motion.smooth
def clamp01(u): return max(0.0,min(1.0,u))
def seg01(t,a,b): return clamp01((t-a)/(b-a))
def lerp3(a,b,u): return tuple(a[i]+(b[i]-a[i])*u for i in range(3))
def bez(a,c,b,u): return tuple((1-u)**2*a[i]+2*(1-u)*u*c[i]+u*u*b[i] for i in range(3))
def Rx(a): c,s=math.cos(a),math.sin(a); return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def Ry(a): c,s=math.cos(a),math.sin(a); return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def obox(center,hs,R,col,emit=False):
    c=np.array(center,float); return box(-hs[0],hs[0],-hs[1],hs[1],-hs[2],hs[2],col,xf=lambda p:tuple(c+R@np.array(p)),emit=emit)
def seg(p0,p1,w,col,depth=None):
    p0=np.array(p0,float); p1=np.array(p1,float); d=p1-p0; L=np.linalg.norm(d)+1e-9; d/=L
    up=np.array([0,0,-1.0]) if abs(d[1])>0.9 else np.array([0,1.0,0]); a=np.cross(d,up); a/=np.linalg.norm(a)+1e-9; b=np.cross(a,d); dp=depth or w
    v=[p0-a*w/2-b*dp/2,p0+a*w/2-b*dp/2,p0+a*w/2+b*dp/2,p0-a*w/2+b*dp/2,p1-a*w/2-b*dp/2,p1+a*w/2-b*dp/2,p1+a*w/2+b*dp/2,p1-a*w/2+b*dp/2]
    F=[(0,1,2,3),(5,4,7,6),(4,0,3,7),(1,5,6,2),(3,2,6,7),(4,5,1,0)]
    return [quad([tuple(v[i]) for i in f],col) for f in F]
def elbow(sh,hand,out_dir,L=0.62):
    sh=np.array(sh); hand=np.array(hand); m=(sh+hand)/2; d=np.linalg.norm(hand-sh)
    bend=max(0.0,(L-d)/L)*0.25+0.03; return tuple(m+np.array(out_dir)*bend+np.array([0,-1,0])*bend*0.6)

NAVY=(34,44,84); NAVY2=(22,28,56); GLASS=(26,32,52); CHROME=(160,166,180); INT=(20,20,24)
DSKIN=(150,104,74); HAIR=(26,20,16); TANK=(226,226,226); JEANS=(46,56,84)
OSHIRT=(160,176,204); OPANTS=(36,42,64); OSKIN=(224,182,152); BLK=(14,14,18)
HINGE=(1.15,0.0,0.0)
def car():
    main=[]; pre=[]
    main+=box(-1.5,0.03,0.32,1.0,0.0,0.08,NAVY)+box(1.15,1.24,0.32,1.0,0.0,0.08,NAVY)+box(-1.5,1.24,0.32,1.0,1.72,1.8,NAVY)
    main+=box(-2.3,-1.5,0.32,1.56,0.0,1.8,NAVY)
    main.append(quad([(-2.22,1.08,-0.005),(-1.58,1.08,-0.005),(-1.58,1.48,-0.005),(-2.22,1.48,-0.005)],GLASS))
    main+=box(1.24,2.35,0.32,1.06,0.0,1.8,NAVY)
    for x in (-1.5,1.62):
        main+=box(x-0.42,x+0.42,0.0,0.6,-0.06,0.3,(12,12,14)); main+=box(x-0.17,x+0.17,0.2,0.4,-0.075,-0.06,(120,120,130))
    main+=box(-1.33-0.012,-1.33+0.012,0.36,1.0,-0.012,-0.002,NAVY2)
    main+=box(-0.5,-0.31,0.85,0.9,-0.035,0.0,CHROME)
    main+=box(1.12,1.25,1.0,1.56,0.0,0.1,NAVY2)+box(-0.05,0.04,1.0,1.56,0.0,0.1,NAVY2)+box(-1.5,-1.33,1.0,1.56,0.0,0.1,NAVY2)
    main+=box(-2.3,1.25,1.56,1.64,0.0,1.8,NAVY)
    main.append(quad([(-1.33,1.0,0.04),(-0.05,1.0,0.04),(-0.05,1.55,0.04),(-1.33,1.55,0.04)],(30,38,62)))
    main.append(quad([(1.25,1.58,0.1),(1.25,1.58,1.7),(1.98,1.06,1.7),(1.98,1.06,0.1)],(40,54,84)))
    main+=box(2.33,2.37,0.55,0.76,0.12,0.5,(250,248,220),emit=True)
    main+=box(1.6,1.75,1.12,1.2,-0.18,-0.0,NAVY2)
    pre+=box(-2.2,2.2,0.3,1.6,1.66,1.72,INT)+box(-2.2,2.2,0.3,0.36,0.08,1.7,INT)+box(-2.2,1.2,1.5,1.56,0.08,1.7,INT)
    pre+=box(0.1,0.85,0.4,0.6,0.3,1.0,(40,40,46))+box(-0.05,0.12,0.6,1.45,0.3,1.0,(46,46,52))
    pre+=box(1.02,1.25,0.82,1.12,0.12,1.66,(28,28,32))+box(0.95,1.02,0.9,1.3,0.48,0.82,(18,18,20))+box(-1.3,-0.1,0.4,1.25,0.3,1.6,(38,38,44))
    return main,pre
CAR_MAIN,CAR_PRE=car()
def door_local():
    Q=box(-1.12,0.0,0.32,1.0,0.0,0.08,NAVY)+box(-1.12,-1.09,0.36,1.0,-0.012,-0.002,NAVY2)+box(-0.03,0.0,0.36,1.0,-0.012,-0.002,NAVY2)
    Q+=box(-1.03,-0.84,0.85,0.9,-0.035,0.0,CHROME)
    return Q

def to_door(p,th): q=Ry(-th)@np.array(p,float); return (q[0]+HINGE[0],q[1],q[2]+HINGE[2])
def sdoor_theta(t): return 0.14*sm(seg01(t,1.6,1.95))           # the driver cracks his own door open
def sdoor(t):
    th=sdoor_theta(t); return transform(door_local(),lambda p:to_door(p,th))
# ---------------- police cruiser (local: centre origin, front +x, near/driver side z=-0.9) ----------------
PW=(232,232,236); PB=(20,20,24); PC0=(-5.2,-0.95)
def pletter(s,x0,y0,z,pix,col):
    Q=[]
    for k,ch in enumerate(s):
        for j,row in enumerate(font.FONT[ch]):
            for i,b in enumerate(row):
                if b=='1': x=x0+(k*6+i)*pix; y=y0-j*pix; Q.append(quad([(x,y-pix,z),(x+pix,y-pix,z),(x+pix,y,z),(x,y,z)],col))
    return Q
def cruiser_body(t):
    B=[]; I=[]
    B+=box(-2.3,-1.1,0.3,0.95,-0.9,0.9,PB)+box(1.1,2.3,0.3,0.95,-0.9,0.9,PB)
    B+=box(-1.1,0.0,0.3,0.95,-0.9,-0.82,PW)+box(-1.1,1.1,0.3,0.95,0.82,0.9,PW)
    B+=pletter('POLICE',-1.02,0.78,-0.905,0.026,PB)
    B+=box(1.0,1.12,0.95,1.45,-0.9,-0.8,PB)+box(-0.05,0.05,0.95,1.45,-0.9,-0.8,PB)+box(-1.2,-1.08,0.95,1.45,-0.9,-0.8,PB)
    B+=box(1.0,1.12,0.95,1.45,0.8,0.9,PB)+box(-1.2,-1.08,0.95,1.45,0.8,0.9,PB)
    B+=box(-1.2,1.12,1.45,1.53,-0.9,0.9,PW)
    B.append(quad([(-1.08,0.97,-0.86),(-0.05,0.97,-0.86),(-0.05,1.43,-0.86),(-1.08,1.43,-0.86)],(26,30,44)))
    B.append(quad([(-1.08,0.97,0.86),(1.0,0.97,0.86),(1.0,1.43,0.86),(-1.08,1.43,0.86)],(26,30,44)))
    B+=box(-2.3,-1.2,0.95,1.05,-0.9,0.9,PB)+box(1.12,2.3,0.95,1.02,-0.9,0.9,PB)
    B.append(quad([(-1.2,1.45,-0.85),(-1.2,1.45,0.85),(-1.75,1.05,0.85),(-1.75,1.05,-0.85)],(30,36,52)))
    B.append(quad([(1.12,1.45,-0.85),(1.12,1.45,0.85),(1.75,1.02,0.85),(1.75,1.02,-0.85)],(44,56,80)))
    B+=box(2.3,2.42,0.3,0.8,-0.6,0.6,PB)
    for z in (-0.6,0.6):
        B+=box(2.3,2.33,0.6,0.75,z-0.18,z+0.18,(255,250,220),emit=True)+box(-2.33,-2.3,0.6,0.75,z-0.18,z+0.18,(230,30,30),emit=True)
    for x in (-1.45,1.45):
        for z0,z1 in ((-0.96,-0.76),(0.76,0.96)):
            B+=box(x-0.36,x+0.36,0.0,0.6,z0,z1,(10,10,12)); B+=box(x-0.15,x+0.15,0.17,0.43,z0-0.012 if z0<0 else z1,z0 if z0<0 else z1+0.012,(130,130,140))
    ph=(t*2.6)%1; red=ph<0.5
    B+=box(-0.2,0.2,1.53,1.63,-0.62,0.0,(255,40,40) if red else (90,20,20),emit=True)
    B+=box(-0.2,0.2,1.53,1.63,0.0,0.62,(50,90,255) if not red else (20,30,90),emit=True)
    I+=box(-1.1,1.1,0.3,0.36,-0.85,0.85,INT)+box(-1.1,1.1,1.4,1.45,-0.85,0.85,INT)+box(-1.1,1.0,0.36,0.95,0.78,0.82,INT)
    I+=box(0.05,0.6,0.36,0.6,-0.8,-0.1,(40,40,46))+box(-0.06,0.08,0.6,1.25,-0.8,-0.1,(46,46,52))
    I+=box(1.0,1.12,0.8,1.05,-0.85,0.85,(28,28,32))+box(0.86,0.9,0.85,1.15,-0.6,-0.3,(18,18,20))
    I+=box(-1.0,-0.1,0.36,1.15,-0.8,0.8,(38,38,44))
    return B,I
PHINGE=(1.1,0.0,-0.9)
def cdoor_local():
    Q=box(-1.1,0.0,0.3,0.95,0.0,0.08,PW)+box(-1.08,-1.05,0.36,0.95,-0.012,0.0,PB)+box(-0.03,0.0,0.36,0.95,-0.012,0.0,PB)
    Q+=pletter('POLICE',-0.98,0.78,-0.006,0.022,PB)
    Q+=box(-1.02,-0.84,0.82,0.87,-0.035,0.0,CHROME)
    return Q
def cdoor_theta(t): return 1.0*(1-sm(seg01(t,8.75,8.95)))
def cdoor_local_q(t):
    th=cdoor_theta(t); return transform(cdoor_local(),lambda p:tuple(np.array(PHINGE)+Ry(-th)@np.array(p,float))),th
# drive path
def car_s(t):
    if t<10.0: return 0.0
    u=t-10.0; return 3.0*u*u if u<1.5 else 6.75+9.0*(u-1.5)
def car_pose(t):
    s=car_s(t); z=PC0[1]-1.25*sm(clamp01(s/1.8)); x=PC0[0]+s
    ds=0.01; z2=PC0[1]-1.25*sm(clamp01((s+ds)/1.8)); yaw=math.atan2(-(z2-z),ds)
    jolt=0.025*math.sin(40*(t-9.0))*math.exp(-4*(t-9.0)) if 9.0<=t<10.0 else 0.0
    return np.array([x,jolt,z]),yaw
def car_to_world(p,t):
    c,yaw=car_pose(t); return tuple(c+Ry(yaw)@np.array(p,float))
def world_to_car(p,t):
    c,yaw=car_pose(t); return Ry(-yaw)@(np.array(p,float)-c)
# ---------------- generic driver body (same look as the window model) ----------------
def basis_from(up,face):
    Y=np.array(up,float); Y/=np.linalg.norm(Y); Z=-np.array(face,float); Z-= (Z@Y)*Y; Z/=np.linalg.norm(Z); X=np.cross(Y,Z); return np.stack([X,Y,Z],1)
def human(H_,R,hands,feet,head_yaw=0.0,knee_fwd=0.12,dread_up=False,t=0.0):
    H_=np.array(H_,float); d=R@np.array([0,1,0]); Sc=H_+d*0.52; Rh=R@Ry(head_yaw); Hc=Sc+d*0.21
    Q=[]
    Q+=obox(H_+d*0.27,(0.19,0.27,0.11),R,TANK)+obox(H_+d*0.47,(0.06,0.06,0.06),R,DSKIN)
    for sx in (-1,1): Q+=obox(Sc+R@np.array([sx*0.17,0.0,0.0]),(0.06,0.05,0.07),R,DSKIN)
    Q+=obox(Hc,(0.11,0.13,0.12),Rh,DSKIN)
    for sx in (-1,1): Q+=obox(Hc+Rh@np.array([sx*0.045,0.03,-0.121]),(0.02,0.012,0.004),Rh,(14,10,8))
    Q+=obox(Hc+Rh@np.array([0,0.11,0.01]),(0.115,0.035,0.125),Rh,HAIR)
    for k in range(7):
        xo=-0.09+0.03*k; root=Hc+Rh@np.array([xo,0.06,0.1])
        end=root+(np.array([0,0.45,0]) if dread_up else np.array([0.03*math.sin(t*3+k),-0.48,0]))+Rh@np.array([xo*1.4,0,0.08])
        if end[1]<0.02: end[1]=0.02
        Q+=seg(root,end,0.035,HAIR)
    for i,sx in enumerate((-1,1)):
        sh=Sc+R@np.array([sx*0.2,-0.02,0]); hd=np.array(hands[i],float)
        el=elbow(sh,hd,tuple(R@np.array([sx*0.6,0,0.15])),0.6)
        Q+=seg(sh,el,0.09,DSKIN)+seg(el,hd,0.08,DSKIN)+obox(hd,(0.045,0.045,0.045),np.eye(3),DSKIN)
    for i,sx in enumerate((-1,1)):
        hip=H_+R@np.array([sx*0.1,-0.03,0]); ft=np.array(feet[i],float)
        kn=(hip+ft)/2+R@np.array([0,0,-1.0])*knee_fwd*max(0.0,1-np.linalg.norm(ft-hip)/0.9)*3
        Q+=seg(hip,kn,0.13,JEANS)+seg(kn,ft,0.11,JEANS)+obox(ft,(0.06,0.04,0.08),R,(220,220,220))
    return Q,Sc,Hc
# ---------------- background (longer street for the getaway) ----------------
def background():
    import random; Rr=random.Random(7); Q=[]
    Q+=tiled_plane(-12,42,-12,12,0,2.0,lambda i,j:(34,34,40) if (i*7+j*3)%5 else (30,30,36))
    Q+=box(-12,42,0.001,0.006,-4.2,-4.05,(150,150,120))
    for x in np.arange(-11,42,3.0): Q+=box(x,x+1.4,0.001,0.006,-6.6,-6.45,(170,170,150))
    Q+=box(1.95,2.15,0,7.0,3.2,3.4,(78,66,54))+box(1.3,2.8,6.2,6.3,3.25,3.35,(70,60,50))
    Q+=box(-12,42,0,5.5,12,12.5,(18,20,30))
    for k in range(60):
        x=Rr.uniform(-11,41); y=Rr.uniform(0.8,4.8); Q.append(quad([(x,y,11.98),(x+0.6,y,11.98),(x+0.6,y+0.5,11.98),(x,y+0.5,11.98)],(230,200,140) if Rr.random()<0.6 else (120,150,200),emit=True))
    for x in (-4.0,8.0,20.0,32.0):
        Q+=box(x-0.06,x+0.06,0,4.6,4,4.12,(60,60,64)); Q.append(quad([(x-0.35,4.6,3.8),(x+0.35,4.6,3.8),(x+0.35,4.6,4.3),(x-0.35,4.6,4.3)],(255,214,150),emit=True))
    return Q
BG=background()
# ---------------- officer ----------------
OKEYS=[(0,-0.25,-0.62),(2.95,-0.25,-0.62),(3.15,-0.35,-0.95),(5.0,-2.0,-3.0),(5.85,-2.0,-3.0),(6.4,-2.4,-3.9),(10.9,-2.4,-3.9)]
YKEYS=[(0,0.91),(2.95,0.91),(3.15,0.68),(5.0,0.68),(5.5,4.71),(5.85,4.71),(6.0,3.56),(6.4,3.56),(6.65,2.82),(9.4,2.82),(9.7,5.52),(10.45,5.52),(10.9,5.52+2*math.pi),(11.05,math.pi/2+4*math.pi)]
RUN0=10.9
def interp(keys,t,linear_spans=()):
    if t<=keys[0][0]: return keys[0][1:]
    for a,b in zip(keys,keys[1:]):
        if a[0]<=t<=b[0]:
            u=(t-a[0])/(b[0]-a[0]) if b[0]>a[0] else 1.0
            if not any(abs(a[0]-l)<1e-6 for l in linear_spans): u=sm(u)
            return tuple(a[i]+(b[i]-a[i])*u for i in range(1,len(a)))
    return keys[-1][1:]
STOP_U=3.1
def run_dist(u):
    d0=lambda v:4.5*v-1.1*(1-math.exp(-v/0.25))
    if u<STOP_U: return d0(u)
    w=min(u-STOP_U,0.4); return d0(STOP_U)+4.5*w-(4.5/0.8)*w*w
def run_speed(u):
    if u<STOP_U: return 1.0
    return max(0.0,1-(u-STOP_U)/0.4)
def cop_base(t):
    if t>=RUN0:
        u=t-RUN0; d=run_dist(u); return np.array([-2.4+max(0.0,d),0.0,-3.9+0.6*sm(min(1.0,u/0.6))])
    x,z=interp(OKEYS,t,linear_spans=(3.15,)); return np.array([x,0.0,z])
def cop_yaw(t): return interp(YKEYS,t)[0]
def cop_lean(t):
    if 2.0<=t<2.2: return 0.18
    if 2.2<=t<2.95: return -0.1-0.08*max(0.0,math.sin(2*math.pi*3*(t-2.2)))
    if 3.15<=t<5.0: return -0.15
    if 5.5<=t<5.85: return 0.15
    if t>=RUN0+STOP_U+0.4: return 0.55*sm(seg01(t,RUN0+STOP_U+0.3,RUN0+STOP_U+0.6))
    if t>=RUN0+0.15: return 0.18
    return 0.0
def cop_local_to_world(p,t):
    bc=cop_base(t); Rb=Ry(cop_yaw(t)); lean=cop_lean(t); p=np.array(p,float); piv=np.array([0,0.92,0])
    return tuple(bc+Rb@(piv+Rx(lean)@(p-piv)))
def cop_hands(t,grabs):
    L=lambda p:cop_local_to_world(p,t)
    rest=[L((-0.3,0.98,0.05)),L((0.3,0.98,0.05))]
    w=2*math.pi*3.2*(t-RUN0)
    if 0.2<=t<1.7:
        jab=0.06*math.sin(2*math.pi*4*t); return [L((-0.28,1.38+jab,0.6)),L((0.3,0.98,0.05))]
    if 1.85<=t<2.95 and grabs: u=sm(seg01(t,1.85,2.05)); return [lerp3(rest[0],grabs[0],u),lerp3(rest[1],grabs[1],u)]
    if 2.95<=t<5.0: return [L((-0.12,0.78,0.62)),L((0.32,1.0,-0.05))]
    if 5.0<=t<5.5: return [L((-0.05,1.0,0.68)),L((0.35,1.25,-0.1))]
    if 5.5<=t<5.85: return [L((-0.22,1.25,0.55)),L((0.22,1.25,0.55))]
    if 6.65<=t<6.95: c=0.04*abs(math.sin(2*math.pi*5*(t-6.65))); return [L((-0.06-c,1.12,0.35)),L((0.06+c,1.12,0.35))]
    if 7.0<=t<9.35: return [L((-0.33,1.58,0.28)),L((0.3,0.98,0.1))]
    if 9.7<=t<10.45: return [L((-0.3,1.85,0.12)),L((0.3,1.85,0.12))]
    if 10.45<=t<RUN0: return [L((-0.6,1.45,0.0)),L((0.6,1.45,0.0))]
    if t>=RUN0+STOP_U+0.3: return [L((-0.17,0.62,0.3)),L((0.17,0.62,0.3))]
    if t>=RUN0: return [L((-0.3,1.1+0.12*math.sin(w),0.25*math.sin(w))),L((0.3,1.1-0.12*math.sin(w),-0.25*math.sin(w)))]
    return rest
def cop(t,grabs):
    bc=cop_base(t); yaw=cop_yaw(t); Rb=Ry(yaw); lean=cop_lean(t)
    def W(p): return tuple(bc+Rb@np.array(p,float))
    def WL(p): return cop_local_to_world(p,t)
    walking=(3.15<=t<5.0) or (5.85<=t<6.4)
    sw=0.0
    if walking: sw=0.42*math.sin(2*math.pi*2.4*t)
    if t>=RUN0: sw=0.75*math.sin(2*math.pi*3.2*(t-RUN0))*run_speed(t-RUN0)
    hy=0.35*math.sin(2*math.pi*1.2*(t-9.4))*sm(seg01(t,9.35,9.45))*(t<9.7)
    Q=[]
    for sx,ph in ((-1,1),(1,-1)):
        Q+=transform(box(sx*0.11-0.08,sx*0.11+0.08,0.06,0.92,-0.08,0.08,OPANTS)+box(sx*0.11-0.09,sx*0.11+0.09,0.0,0.07,-0.06,0.12,BLK),lambda p,ph=ph:W(rx(p,ph*sw,(0,0.92,0))))
    Q+=box(-0.21,0.21,0.92,1.5,-0.12,0.12,OSHIRT,xf=WL)+box(-0.22,0.22,0.88,0.99,-0.13,0.13,BLK,xf=WL)
    Q+=box(-0.31,-0.22,0.7,0.96,-0.06,0.08,BLK,xf=WL)+box(0.07,0.14,1.3,1.38,0.12,0.126,(230,190,60),xf=WL)+box(0.1,0.18,1.4,1.5,0.06,0.13,BLK,xf=WL)
    Q+=box(-0.06,0.06,1.5,1.56,-0.06,0.06,OSKIN,xf=WL)
    def WH(p): return WL(ry(p,hy,(0,1.67,0)))
    Q+=box(-0.11,0.11,1.54,1.8,-0.12,0.12,OSKIN,xf=WH)+box(-0.125,-0.11,1.62,1.7,-0.03,0.03,OSKIN,xf=WH)+box(0.11,0.125,1.62,1.7,-0.03,0.03,OSKIN,xf=WH)
    for sx in (-1,1): Q+=box(sx*0.045-0.02,sx*0.045+0.02,1.68,1.7,0.12,0.124,BLK,xf=WH)
    hands=cop_hands(t,grabs)
    for k,sx in enumerate((-1,1)):
        sh=WL((sx*0.27,1.44,0)); h=hands[k]
        el=elbow(sh,h,tuple(Rb@np.array([sx*0.6,0,-0.2])))
        Q+=seg(sh,el,0.11,OSHIRT)+seg(el,h,0.09,OSKIN)+obox(h,(0.05,0.05,0.05),np.eye(3),OSKIN)
    if 7.0<=t<9.35: Q+=obox(np.array(hands[0])+np.array([0,0.07,0]),(0.018,0.04,0.018),np.eye(3),OSKIN)   # thumb up
    return Q,bc
# ---------------- driver ----------------
def driver_window(t):
    p=0.45+0.55*sm(seg01(t,2.2,2.95))
    Hs=(0.48,0.66,0.62); Hl=(0.5,0.98,0.24); H_=np.array(lerp3(Hs,Hl,p))
    if 2.2<=t<2.95: H_=H_+np.array([0,0,-0.05*max(0.0,math.sin(2*math.pi*3*(t-2.2)))])
    Lean=0.79+(1.75-0.79)*sm(seg01(t,2.2,2.95))
    yaw=-0.35*sm(seg01(t,0.1,0.4))*(1-sm(seg01(t,1.2,1.4))); nod=0.18*math.sin(2*math.pi*2*t)*(t<1.2)
    if 1.2<=t<2.0: yaw=-0.4*sm(seg01(t,1.2,1.4))
    R=Rx(-Lean); d=R@np.array([0,1,0]); Sc=H_+d*0.52
    Rh=Ry(yaw)@Rx(-Lean-nod); Hc=Sc+(Rx(-Lean-nod)@np.array([0,1,0]))*0.21
    Q=[]
    Q+=obox(H_+d*0.27,(0.19,0.27,0.11),R,TANK)+obox(H_+d*0.47,(0.06,0.06,0.06),R,DSKIN)
    for sx in (-1,1): Q+=obox(Sc+R@np.array([sx*0.17,0.0,0.0]),(0.06,0.05,0.07),R,DSKIN)
    Q+=obox(Hc,(0.11,0.13,0.12),Rh,DSKIN)
    for sx in (-1,1): Q+=obox(Hc+Rh@np.array([sx*0.045,0.03,-0.121]),(0.02,0.012,0.004),Rh,(14,10,8))
    Q+=obox(Hc+Rh@np.array([0,0.11,0.01]),(0.115,0.035,0.125),Rh,HAIR)
    for k in range(7):
        xo=-0.09+0.03*k; root=Hc+Rh@np.array([xo,0.06,0.1])
        Q+=seg(root,root+np.array([0.04*math.sin(t*3+k),-0.5,0])+Rh@np.array([xo*1.5,0,0.08]),0.035,HAIR)
    grabs=[]
    for i,sx in enumerate((-1,1)):
        sh=Sc+R@np.array([sx*0.2,-0.02,0]); grabs.append(tuple(sh+np.array([0,0.04,-0.06])))
        if t<1.2: hand=Sc+np.array([sx*0.3,0.15+0.06*math.sin(t*9+sx),-0.18])            # "what?!" hands
        elif t<2.2 and sx<0: hand=lerp3(tuple(Sc+np.array([-0.3,0.15,-0.18])),(0.2,0.88,0.1),sm(seg01(t,1.2,1.6)))   # reaches for his door handle
        elif t<2.2: hand=Sc+np.array([0.25,-0.05,-0.15])
        else: w=2*math.pi*3*t+(0 if sx<0 else math.pi); hand=sh+np.array([sx*0.3*math.cos(w),0.3*math.sin(w),-0.2])
        hand=np.array(hand,float); el=elbow(sh,hand,(sx*0.6,0,-0.3),0.6)
        Q+=seg(sh,el,0.09,DSKIN)+seg(el,hand,0.08,DSKIN)+obox(hand,(0.045,0.045,0.045),np.eye(3),DSKIN)
    for sx in (-1,1):
        hip=H_+np.array([sx*0.1,-0.03,0]); k=hip+np.array([0.42,0.0,sx*0.1]); f=k+np.array([0.05,-0.42,0.0])
        Q+=seg(hip,k,0.13,JEANS)+seg(k,f,0.11,JEANS)+obox(f,(0.06,0.04,0.09),np.eye(3),(220,220,220))
    return Q,grabs
SLIDE_END=np.array([-5.3,0.12,-3.25]); STAND=np.array([-5.35,0.95,-3.25])
SEAT_L=np.array([0.33,0.66,-0.45])
def lying(H_,up,hand_held,t,twitch=0.0):
    up=np.array(up,float); up[1]=0; up/=np.linalg.norm(up)+1e-9
    R=basis_from(up,(0,1,0)); side=R@np.array([1,0,0])
    other=H_+up*0.35+side*(0.38+0.05*math.sin(t*11))
    feet=[H_-up*0.86-side*0.13+np.array([0,0.06+twitch*abs(math.sin(t*17)),0]),H_-up*0.86+side*0.13+np.array([0,0.06+twitch*abs(math.sin(t*13+1)),0])]
    hands=[hand_held,other]
    return human(H_,R,hands,feet,t=t)[0]
def driver_out(t,cop_hand,cop_pos):
    if t<3.25:                                        # flops out of the window onto the ground, still held by the hand
        u=sm(seg01(t,2.95,3.25)); up=np.array(cop_hand)-np.array([0.55,0,-0.6]); up[1]=0
        Hg=np.array(cop_hand)-up/np.linalg.norm(up)*1.12; Hg[1]=0.12
        H_=lerp3((0.5,1.0,-0.2),tuple(Hg),u); H_=np.array(H_); H_[1]+=0.25*math.sin(math.pi*u)
        return lying(H_,up,cop_hand,t,0.3),'out'
    if t<5.5:                                         # dragged, then swung round
        up=np.array(cop_hand)-np.array(cop_pos); up[1]=0; up/=np.linalg.norm(up)+1e-9
        H_=np.array(cop_hand)-up*1.12; H_[1]=0.12+(0.35*math.sin(math.pi*seg01(t,5.0,5.5)) if t>=5.0 else 0.0)
        return lying(H_,up,cop_hand,t,0.15),'out'
    if t<6.5:                                         # flung: slides beside the open cruiser door, lies there
        A=np.array([-3.25,0.12,-3.25]); u=1-(1-seg01(t,5.5,5.95))**2.5
        H_=A+(SLIDE_END-A)*u; up=np.array([1.0,0,0])
        return lying(H_,up,tuple(H_+np.array([0.95,0.05,0.25])),t,0.25 if t>5.95 else 0.0),'out'
    if t<7.3:                                         # gets up, spots the open door
        u=sm(seg01(t,6.5,7.0)); up=lerp3((1,0,0),(0,1,0),u); face=lerp3((0,1,0),(0.66,0,0.37),u)
        R=basis_from(up,face); H_=SLIDE_END+(STAND-SLIDE_END)*u
        side=R@np.array([1,0,0]); fwd=-(R@np.array([0,0,1]))
        hands=[H_+R@np.array([-0.3,0.05,-0.05]),H_+R@np.array([0.3,0.05,-0.05])]
        ground=lambda sx:H_-R@np.array([0,0.88,0])+side*sx*0.13
        feet=[ground(-1),ground(1)]
        for f in feet: f[1]=max(0.04,f[1])
        hy=0.5*sm(seg01(t,6.95,7.15))
        return human(H_,R,hands,feet,head_yaw=-hy,t=t)[0],'out'
    if t<8.2:                                         # sneaks on tiptoe to the gap behind the open door
        u=seg01(t,7.3,8.2); A=STAND; B=np.array([-4.95,0.82,-2.25])
        H_=A+(B-A)*sm(u); H_[1]=0.82+0.13*(1-sm(seg01(t,7.3,7.45)))+0.025*abs(math.sin(2*math.pi*2.2*(t-7.3)))
        face=(0.4,0,0.9); R=basis_from((0,1,0),face)@Rx(0.3)
        fwd=np.array(face)/np.linalg.norm(face); side=np.cross(np.array([0,1,0]),-fwd)
        w=2*math.pi*2.2*(t-7.3); feet=[]
        for sx in (-1,1):
            f=H_-np.array([0,0.78,0])+side*sx*0.12+fwd*0.15*math.sin(w+(0 if sx<0 else math.pi)); f[1]=0.04+0.06*max(0.0,math.sin(w+(0 if sx<0 else math.pi))); feet.append(f)
        hands=[H_+np.array([0,0.45,0])+side*-0.18+fwd*0.25,H_+np.array([0,0.45,0])+side*0.18+fwd*0.25]
        return human(H_,R,hands,feet,knee_fwd=0.2,t=t)[0],'out'
    if t<8.7:                                         # climbs into the driver's seat
        u=sm(seg01(t,8.2,8.7)); seatW=np.array(car_to_world(SEAT_L,t))
        H_=np.array([-4.95,0.82,-2.25])+(seatW-np.array([-4.95,0.82,-2.25]))*u
        face=lerp3((0.4,0,0.9),(1,0,0),u); R=basis_from((0,1,0),face)
        fw=[np.array(car_to_world((0.95,0.38,-0.45+sx*0.1),t)) for sx in (-1,1)]
        fo=[H_+np.array([sx*0.12,-0.78,0]) for sx in (-1,1)]
        feet=[fo[i]+(fw[i]-fo[i])*u for i in range(2)]
        for f in feet: f[1]=max(0.04,f[1])
        hands=[np.array(car_to_world((0.86,1.0,-0.57),t))*u+(H_+np.array([-0.2,0.4,0]))*(1-u),np.array(car_to_world((0.86,1.0,-0.33),t))*u+(H_+np.array([0.2,0.4,0]))*(1-u)]
        return human(H_,R,hands,feet,t=t)[0],'car'
    # seated, attached to the cruiser
    c,yaw=car_pose(t); Rc=Ry(yaw)
    H_=np.array(car_to_world(SEAT_L,t)); R=Rc@basis_from((0,1,0),(1,0,0))
    hands=[car_to_world((0.86,1.0,-0.57),t),car_to_world((0.86,1.0,-0.33),t)]
    feet=[car_to_world((0.95,0.38,-0.55),t),car_to_world((0.95,0.38,-0.35),t)]
    hy=1.1*sm(seg01(t,9.3,9.6))*(1-sm(seg01(t,10.4,10.7)))
    return human(H_,R,hands,feet,head_yaw=hy,t=t)[0],'car'
# ---------------- assembly ----------------
def split_z(Q,z=0.03): return [q for q in Q if q['c'][2]>z],[q for q in Q if q['c'][2]<=z]
def gcenter(Q): return np.mean([q['c'] for q in Q],axis=0) if Q else np.zeros(3)
def scene(t):
    groups=[]
    # suspect car + anything reaching inside it
    spre=list(CAR_PRE); smain=list(CAR_MAIN)+sdoor(t)
    drv_out=[]; grabs=None
    if t<2.95:
        dq,grabs=driver_window(t); a,b=split_z(dq); spre+=a; drv_out+=b
    cq,cpos=cop(t,grabs); a,b=split_z(cq); spre+=a; cop_out=b
    if t>=2.95:
        hand=cop_hands(t,None)[0]
        dq,mode=driver_out(t,hand,cpos)
    # cruiser
    B,I=cruiser_body(t); B=transform(B,lambda p:car_to_world(p,t)); I=transform(I,lambda p:car_to_world(p,t))
    dl,th=cdoor_local_q(t); dl=transform(dl,lambda p:car_to_world(p,t))
    c_in=list(I); c_body=list(B); c_post=[]
    (c_body if th<0.03 else c_post).extend(dl)
    if t>=2.95:
        if mode=='car':
            for q in dq: (c_in if world_to_car(q['c'],t)[2]>-0.86 else c_post).append(q)
        else: drv_out+=dq
    groups.append((gcenter(CAR_MAIN),[spre,smain]))
    groups.append((np.array(car_pose(t)[0])+np.array([0,0.8,0]),[c_in,c_body,c_post]))
    if cop_out: groups.append((gcenter(cop_out),[cop_out]))
    if drv_out: groups.append((gcenter(drv_out),[drv_out]))
    return groups,cpos
def cam_track(target,off): return (tuple(np.array(target)+np.array(off)),tuple(target))
CAM_A=((3.3,1.6,-2.2),(-2.0,0.95,-0.5))
CAM_C=((-1.6,1.5,-6.3),(-4.2,0.9,-2.4))
def driver_hip_est(t):
    if t<3.25: return np.array([0.3,0.3,-0.8])
    if t<5.5:
        ch=np.array(cop_hands(t,None)[0]); cp=cop_base(t); up=ch-cp; up[1]=0; up/=np.linalg.norm(up)+1e-9; return ch-up*1.12
    return SLIDE_END
def camera(t):
    if t<2.95: pos,tgt=CAM_A
    elif t<6.0:
        h=driver_hip_est(t); tg=(h[0]+0.2,0.6,h[2]+0.3); P,Tg=(tuple(np.array(tg)+np.array([1.9,1.1,-2.6])),tg)
        u=sm(seg01(t,2.95,3.5)); pos=lerp3(CAM_A[0],P,u); tgt=lerp3(CAM_A[1],Tg,u)
    elif t<10.4:
        h=SLIDE_END; tg=(h[0]+0.2,0.6,h[2]+0.3); P=tuple(np.array(tg)+np.array([1.9,1.1,-2.6]))
        u=sm(seg01(t,5.95,6.6)); pos=lerp3(P,CAM_C[0],u); tgt=lerp3(tg,CAM_C[1],u)
        z=sm(seg01(t,7.3,8.2))*(1-sm(seg01(t,9.3,10.2))); pos=lerp3(pos,(-1.85,1.5,-6.1),z); tgt=lerp3(tgt,(-3.95,0.92,-2.65),z)
    else:
        ox=cop_base(t)[0]; cx=car_pose(t)[0][0]; mid=min(0.5*(ox+cx),ox+0.9); P=(mid-1.0,1.35,-7.0); Tg=(mid+0.6,0.8,-2.6)
        u=sm(seg01(t,10.4,11.4)); pos=lerp3(CAM_C[0],P,u); tgt=lerp3(CAM_C[1],Tg,u)
        v=sm(seg01(t,RUN0+STOP_U-0.5,RUN0+STOP_U+0.4)); pos=lerp3(pos,(ox-3.0,1.35,-2.6),v); tgt=lerp3(tgt,(ox+5.0,0.8,-2.4),v)
    dx,dy,dyaw,dpit=motion.handheld(t,15.5,amp=0.6)
    c=Camera.look((pos[0]+dx,pos[1]+dy,pos[2]),tgt); return (c[0],c[1],c[2],c[3]+dyaw,c[4]+dpit)
def lights(t):
    ph=(t*2.6)%1
    cpz=camera(t)
    L=[((-6,4.5,4),(255,200,140),1.6),((cpz[0],cpz[1]+1.0,cpz[2]),(190,200,240),1.2),((0.6,1.45,0.9),(255,220,170),0.3)]
    bar=car_to_world((0,1.8,-0.3 if ph<0.5 else 0.3),t)
    L.append((bar,(255,50,50) if ph<0.5 else (60,90,255),3.2))
    if cdoor_theta(t)>0.05: L.append((car_to_world((0.35,1.3,-0.5),t),(255,225,160),1.3))
    if t>=9.0: L.append((car_to_world((3.2,0.8,0.0),t),(255,245,210),1.6))
    for x in (8.0,20.0,32.0): L.append(((x,4.4,4.0),(255,200,140),1.8))
    return L
R=Renderer(W,H,fog=(10,12,24))
SHAKES=[(2.0,2),(2.95,3),(3.25,3),(5.5,3),(5.95,2),(8.95,3),(9.0,2),(10.0,3),(10.5,5)]
def shake_px(t):
    sx=sy=0.0
    for t0,a in SHAKES:
        if 0<=t-t0<0.22: k=1-(t-t0)/0.22; sx+=a*k*math.sin(97*t); sy+=a*k*math.cos(71*t)
    return (sx,sy)
def render(t,fog_end=24):
    groups,cpos=scene(t); cam=camera(t); cp=np.array(cam[:3])
    groups.sort(key=lambda g:-np.linalg.norm(g[0]-cp))
    layers=[BG]+[L for g in groups for L in g[1]]
    img,vi=R.render(cam,layers,lights(t),fov=58,fog_start=8,fog_end=fog_end,ambient=0.28,shake=shake_px(t))
    return post.ps1(img),vi,cpos
# ---------------- HUD ----------------
def otext(d,s,x,y,col,sc):
    o=max(1,sc//2)
    for ox,oy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)): font.text(d,s,x+ox*o,y+oy*o,(0,0,0),sc,None)
    font.text(d,s,x,y,col,sc,None)
def ctext(d,s,y,col,sc): otext(d,s,(W-font.width(s,sc))//2,y,col,sc)
def panel(d,x0,y0,x1,y1): d.rectangle([x0,y0,x1,y1],fill=(8,10,30),outline=(230,230,240))
def tri(d,x,y,col,left=False,down=False):
    if down: d.polygon([(x-4,y),(x+4,y),(x,y+5)],fill=col,outline=(0,0,0))
    elif left: d.polygon([(x,y),(x+5,y-4),(x+5,y+4)],fill=col)
    else: d.polygon([(x,y-3),(x+4,y),(x,y+3)],fill=col)

SKULL=[".#####.","#######","#..#..#","#..#..#","#######",".##.##.",".#####.",".#.#.#."]
def skull(d,x,y,sc):
    for j,row in enumerate(SKULL):
        for i,c in enumerate(row):
            if c=='#':
                d.rectangle([x+i*sc-1,y+j*sc-1,x+i*sc+sc,y+j*sc+sc],fill=(0,0,0))
    for j,row in enumerate(SKULL):
        for i,c in enumerate(row):
            if c=='#': d.rectangle([x+i*sc,y+j*sc,x+i*sc+sc-1,y+j*sc+sc-1],fill=(240,240,240))
def star5(d,cx,cy,r,col):
    pts=[]
    for k in range(10):
        a=-math.pi/2+k*math.pi/5; rr=r if k%2==0 else r*0.45; pts.append((cx+rr*math.cos(a),cy+rr*math.sin(a)))
    d.polygon(pts,fill=col,outline=(0,0,0))
YEL=(255,214,40); WHT=(255,255,255); RED=(255,70,60); GRN=(90,230,90)
def bubble(d,x,y,txt,col=(0,0,0)):
    w=font.width(txt,1)+8; x0=int(max(2,min(W-w-2,x-w//2))); y0=int(y-16)
    d.rectangle([x0,y0,x0+w,y0+12],fill=(250,250,250),outline=(0,0,0))
    tx=int(max(x0+3,min(x0+w-3,x))); d.polygon([(tx-3,y0+12),(tx+3,y0+12),(tx,y0+17)],fill=(250,250,250),outline=(0,0,0)); d.line([tx-2,y0+12,tx+2,y0+12],fill=(250,250,250))
    font.text(d,txt,x0+4,y0+3,col,1,None)
def bang(d,x,y,col=(255,60,50)): otext(d,'!',int(x)-2,int(y)-12,col,2)
def hud(img,vi,t,mode,T,cpos):
    d=ImageDraw.Draw(img)
    def proj(p): return R.project(p,vi) if vi is not None else None
    if mode=='hook':
        otext(d,'HOW DID HE',(W-font.width('HOW DID HE',2))//2,30,WHT,2); otext(d,'STEAL IT?!',(W-font.width('STEAL IT?!',2))//2,50,YEL,2)
    if mode=='rewind':
        for k in range(2): d.polygon([(64+k*7,160),(70+k*7,155),(70+k*7,165)],fill=WHT,outline=(0,0,0))
        otext(d,'REWIND',84,156,WHT,1)
    if mode=='play':
        if 0.2<=t<1.75:
            q=proj((cpos[0],2.0,cpos[2]))
            if q: bubble(d,q[0],q[1],'GET OUT!',(200,0,0))
        if 1.3<=t<2.0:
            q=proj((0.5,1.75,-0.1))
            if q: bubble(d,q[0],q[1],'OK OK...')
        if 7.05<=t<7.7:
            q=proj((STAND[0],2.0,STAND[2]))
            if q: bang(d,q[0],q[1],YEL)
        if 7.0<=t<9.0:
            u=sm(seg01(t,7.0,7.15)); y=int(-20+46*u)
            d.rectangle([22,y,158,y+18],fill=(10,40,10),outline=GRN)
            d.line([30,y+9,34,y+13,41,y+5],fill=GRN,width=2)
            otext(d,'SUSPECT DETAINED',48,y+6,GRN,1)
        if 9.7<=t<10.4:
            q=proj((cpos[0],2.05,cpos[2]))
            if q: bang(d,q[0],q[1])
        if t>=12.6:
            u=sm(seg01(t,12.6,12.75)); sc=3
            otext(d,'MISSION',(W-font.width('MISSION',sc))//2,int(34-12*(1-u)),RED,sc); otext(d,'FAILED',(W-font.width('FAILED',sc))//2,int(58-12*(1-u)),RED,sc)
            if t>=13.0: otext(d,'POLICE CAR',(W-font.width('POLICE CAR',2))//2,92,WHT,2); otext(d,'STOLEN',(W-font.width('STOLEN',2))//2,110,YEL,2)
    if t>=9.0 and mode in ('play','hook'):
        for k in range(5): star5(d,118+k*12,12,4,YEL if (k<3 and int(T*4)%2==0) else (60,60,70))
    wx=int(6+(W-font.width('VIDIVENIGAMING')-12)*(0.5+0.5*math.sin(T*0.31))); wy=int(296+8*math.sin(T*0.23))
    font.text(d,'VIDIVENIGAMING',wx,wy,(150,160,200),1,None)
    return img
# ---------------- video timeline ----------------
HOOK=(11.1,12.6); DUR=17.5; N=int(DUR*FPS)
def vmap(T):
    if T<1.5: return HOOK[0]+T,'hook'
    if T<2.0: u=(T-1.5)/0.5; return HOOK[1]*(1-u)**1.3,'rewind'
    return T-2.0,'play'
def glitch_lowres(img,seed):
    import random as _r
    a=np.asarray(img).copy(); r=_r.Random(seed); o=a.copy(); o[:,2:,0]=a[:,:-2,0]; o[:,:-2,2]=a[:,2:,2]
    for _ in range(r.randint(3,6)):
        y0=r.randint(20,300); h=r.randint(3,16); o[y0:y0+h]=np.roll(o[y0:y0+h],r.randint(-24,24),axis=1)
    return Image.fromarray(o)
def frame(T):
    t,mode=vmap(T)
    img,vi,cpos=render(t,fog_end=34 if t>=10.5 else 24)
    g=mode=='rewind'
    if g: img=glitch_lowres(img,int(T*FPS))
    return hud(img,vi,t,mode,T,cpos),g
TEST=os.environ.get('TEST')
if TEST:
    key='T' if os.environ.get('VIDEO') else 't'
    ims=[]
    for x in TEST.split(','):
        T=float(x) if key=='T' else float(x)+2.0
        ims.append(frame(T)[0])
    sh=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): sh.paste(im,(i*182,0))
    sh.resize((sh.width*2,640),Image.NEAREST).save('test.png'); sys.exit()
# ---------------- sound (video time; story sim t plays at video t+2.0) ----------------
s=Sound(DUR,loop=False,seed=21)
V=lambda tt:tt+2.0
def sq(t0,notes,step,v,dec=8,duty=0.5):
    for i,m in enumerate(notes):
        f=440*2**((m-69)/12); tt=s.T(step*1.8); ph=(f*tt)%1; s.place(np.where(ph<duty,1.0,-1.0)*np.exp(-tt*dec),t0+i*step,v)
def nb(t0,d,lo,hi,v,seed,shape=2,pan=0.0):
    x=s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape; s.place(x,t0,v,pan)
def sweep(t0,d,f0,f1,v,square=False):
    tt=s.T(d); f=f0+(f1-f0)*tt/d; ph=2*np.pi*np.cumsum(f)/s.sr; x=np.sign(np.sin(ph)) if square else np.sin(ph); s.place(x*np.sin(np.pi*tt/d)**0.5,t0,v)
def step(t0,v=0.18,seed=0): s.place(s.filt_short(s.noise(0.05,seed),lo=150,hi=1400)*np.exp(-s.T(0.05)*60),t0,v)
def whistle(t0,d=0.7,v=0.07):
    tt=s.T(d); f=2900+120*np.sign(np.sin(2*np.pi*28*tt)); x=np.sin(2*np.pi*np.cumsum(f)/s.sr)*np.minimum(1,tt/0.02)*np.minimum(1,(d-tt)/0.05); s.place(x,t0,v)
def engine(t0,t1,f0,f1,v,seed=3):
    d=t1-t0; tt=s.T(d); f=f0+(f1-f0)*(tt/d)**0.7; ph=np.cumsum(f)/s.sr
    x=((ph%1)*2-1)*0.6+np.sign(np.sin(2*np.pi*ph*0.5))*0.3; x=s.filt_short(x,hi=900)*np.minimum(1,tt/0.08)
    s.place(x,t0,v)
def screech(t0,d,v):
    tt=s.T(d); x=s.filt_short(s.noise(d,77),lo=1800,hi=4500)*(0.7+0.3*np.sin(2*np.pi*31*tt))*np.sin(np.pi*tt/d)**0.6; s.place(x,t0,v)
# beds
eng0=(np.sin(2*np.pi*31*s.t)*0.6+np.sin(2*np.pi*62*s.t)*0.3)*0.012; s.L+=eng0; s.R+=eng0
s.bed(s.filt(s.rng.normal(0,1,s.n),lo=150,hi=1800)*0.02)
for k,tt in enumerate(np.arange(0.3,DUR,0.9)):
    tc=s.T(0.06); s.place(np.sin(2*np.pi*4600*tc)*(np.sin(2*np.pi*60*tc)>0)*np.exp(-tc*30),tt+0.13*math.sin(k),0.01,pan=-0.6 if k%2 else 0.6)
# music: PS1 bass loop through the arrest, sneaky plucks for the theft, fast loop for the chase
def loop(t0,t1,step_,notes,v,kick=True):
    k=0
    while t0+k*step_<t1:
        m=notes[k%len(notes)]; f=440*2**((m-69)/12); tt=s.T(step_*0.9)
        s.place(s.filt_short(np.sign(np.sin(2*np.pi*f*tt)),hi=900)*np.exp(-tt*6),t0+k*step_,v)
        if kick and k%2==0: tt=s.T(0.1); s.place(np.sin(2*np.pi*(120-60*tt/0.1)*tt)*np.exp(-tt*30),t0+k*step_,v*2.2)
        k+=1
BASS=[45,45,52,48,45,45,55,52]
loop(0.0,1.5,0.16,BASS,0.03)                                      # hook: chase tempo
loop(V(0.0),V(7.0),0.25,BASS,0.026)                                # arrest
for k,tt in enumerate(np.arange(V(7.3),V(8.2),0.225)): sq(tt,[[64,67,69,67][k%4]],0.06,0.035,dec=18)   # tiptoe plucks
loop(V(10.0),V(12.6),0.16,BASS,0.03)                               # chase
# hook
engine(0.0,1.5,95,140,0.07); screech(0.0,0.5,0.05)
for k in range(9): step(0.05+k*0.156,0.14,k)
whistle(0.3); sq(0.0,[55],0.1,0.06,dec=6)
# rewind
for k in range(5): sweep(1.5+k*0.1,0.1,500,2600,0.035)
nb(1.5,0.5,800,6000,0.08,5)
# arrest
sq(V(0.2),[50,50],0.14,0.05,dec=10,duty=0.3); sq(V(0.7),[50],0.14,0.05,dec=10,duty=0.3)        # angry "GET OUT!"
sq(V(1.3),[62,64],0.12,0.035,dec=14,duty=0.3)                                                   # "ok ok"
s.place(s.filt_short(s.noise(0.03,9),lo=1500,hi=6000)*np.exp(-s.T(0.03)*150),V(1.65),0.25)      # door unlatches
s.thud(V(2.0),f=90,v=0.25)
tt=s.T(0.75); s.place(np.sin(2*np.pi*np.cumsum(150+200*tt/0.75+25*np.sin(2*np.pi*6*tt))/s.sr)*0.6*np.sin(np.pi*tt/0.75),V(2.2),0.07)
sweep(V(2.95),0.3,200,900,0.1); s.thud(V(3.25),f=60,v=0.4)                                      # pops out, hits the ground
drag=s.filt_short(s.noise(1.75,11),lo=200,hi=1800)*(0.6+0.4*np.abs(np.sin(2*np.pi*2.4*s.T(1.75)))); s.place(drag,V(3.25),0.09)
for k in range(8): step(V(3.3)+k*0.21,0.15,20+k)
nb(V(5.0),0.5,300,3000,0.2,12); nb(V(5.5),0.3,600,5000,0.18,13)                                # swing, fling
s.place(s.filt_short(s.noise(0.45,14),lo=200,hi=2000)*np.linspace(1,0,int(0.45*s.sr)),V(5.5),0.12); s.thud(V(5.95),f=80,v=0.15)
for k in range(3): s.place(s.filt_short(s.noise(0.03,30+k),lo=800,hi=5000)*np.exp(-s.T(0.03)*120),V(6.67)+k*0.1,0.2)   # dusts his hands
sq(V(7.0),[72,76,79,84],0.07,0.055)                                                             # SUSPECT DETAINED
sq(V(7.05),[88,93],0.06,0.04,dec=12)                                                            # "!"
s.thud(V(8.95),f=75,v=0.35); s.place(s.filt_short(s.noise(0.06,40),lo=800,hi=4000)*np.exp(-s.T(0.06)*60),V(8.95),0.2)   # door slam
tt=s.T(0.5); s.place(s.filt_short(s.noise(0.5,41),lo=200,hi=1500)*(0.5+0.5*np.sign(np.sin(2*np.pi*15*tt))),V(9.0),0.08)   # starter
engine(V(9.5),V(10.0),70,80,0.06); engine(V(10.0),V(15.5),90,230,0.08)
g=np.ones(s.n); i0=int(V(12.0)*s.sr); g[i0:]=np.linspace(1,0.25,s.n-i0)
sq(V(9.7),[84,79,84,79],0.07,0.05,dec=10)                                                       # officer "!"
screech(V(10.0),0.9,0.07); nb(V(10.45),0.45,400,4000,0.22,50); sweep(V(10.5),0.45,900,250,0.05)   # near miss + spin
for k in range(int((STOP_U)/0.156)): step(V(RUN0)+0.05+k*0.156,0.15,60+k)
whistle(V(RUN0+0.4)); whistle(V(RUN0+1.6),0.5,0.06)
sq(V(12.6),[67,63,60,55],0.16,0.06,dec=5)                                                       # MISSION FAILED
tt=s.T(1.0); s.place(s.filt_short(s.noise(1.0,70),lo=300,hi=1200)*np.abs(np.sin(2*np.pi*1.6*tt))*0.5,V(RUN0+STOP_U+0.4),0.08)   # panting
s.reverb(0.12,length=0.8,decay=5)
wav=s.save(os.path.join(OUT,'stolen_cruiser.wav'),peak=0.85)
vhs=post.VHS(W*S,H*S,S,grade='none',chroma=2,scan_dark=0.92,vignette=0.3,grain=2.0,band_period=1e9)
mp4=os.path.join(OUT,'stolen_cruiser.mp4')
with post.Encoder(mp4,W*S,H*S,wav,FPS,DUR) as enc:
    for f in range(N):
        T=f/FPS; img,g_=frame(T); enc.write(vhs(post.upscale(img,S),f,T,glitch=g_))
print('probe',check.probe(mp4))
