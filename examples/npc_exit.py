"""NPC.exe Has Stopped Working - when GTA-style PS1 NPCs forget how doors work. 14 s, 9:16.
Same car / officer / driver models as window_stop.py. Run: python examples/npc_exit.py -> out/npc_exit.mp4"""
import os, sys, math
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, box, quad, tiled_plane, transform, rx, ry, refresh
from nightkit import motion, post, font, check
from nightkit.audio import Sound
OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6
sm=motion.smooth
def refresh_q(q): return q
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

# ---------------- timeline ----------------
T_REACH=(1.0,1.6); T_PULL=(1.6,3.4); T_GLITCH=(3.4,5.8); T_POP=5.8; T_LAND=6.5; T_TPOSE=6.95
T_FREEZE=(7.6,9.2); T_WALK=(9.4,10.2); T_HANDLE=10.5; T_OPEN=(10.55,11.2); T_TEXT=11.15; T_LOOK=11.9; DUR=14.0
STUTTER=[(3.55,3.75),(4.45,4.6),(5.2,5.4)]
def gwin(t): return T_GLITCH[0]<=t<T_GLITCH[1]
NAVY=(34,44,84); NAVY2=(22,28,56); GLASS=(26,32,52); CHROME=(160,166,180); INT=(20,20,24)
DSKIN=(150,104,74); HAIR=(26,20,16); TANK=(226,226,226); JEANS=(46,56,84)
OSHIRT=(160,176,204); OPANTS=(36,42,64); OSKIN=(224,182,152); BLK=(14,14,18)
# ---------------- world (door is its own part so it can open) ----------------
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
def door_theta(t): return 0.95*sm((t-T_OPEN[0])/(T_OPEN[1]-T_OPEN[0]))+0.04*math.sin(9*(t-T_OPEN[1]))*math.exp(-3*(t-T_OPEN[1]))*(t>T_OPEN[1])
def to_door(p,th): q=Ry(-th)@np.array(p,float); return (q[0]+HINGE[0],q[1],q[2]+HINGE[2])
def door(t): th=door_theta(t); return [refresh_q(q) for q in transform(door_local(),lambda p:to_door(p,th))],th
def handle_pos(t): return to_door((-0.935,0.875,-0.03),door_theta(t))


def background():
    import random; Rr=random.Random(7); Q=[]
    Q+=tiled_plane(-9,9,-8,12,0,1.0,lambda i,j:(34,34,40) if (i*7+j*3)%5 else (30,30,36))
    for x in (-3.0,3.4): Q+=box(x,x+0.12,0.001,0.006,-6,8,(150,150,120))
    Q+=box(1.95,2.15,0,7.0,3.2,3.4,(78,66,54))+box(1.3,2.8,6.2,6.3,3.25,3.35,(70,60,50))     # utility pole
    Q+=box(-9,9,0,5.5,12,12.5,(18,20,30))
    for k in range(26):
        x=Rr.uniform(-8,8); y=Rr.uniform(0.8,4.8); Q.append(quad([(x,y,11.98),(x+0.6,y,11.98),(x+0.6,y+0.5,11.98),(x,y+0.5,11.98)],(230,200,140) if Rr.random()<0.6 else (120,150,200),emit=True))
    Q+=box(-4.1,-3.98,0,4.6,4,4.12,(60,60,64)); Q.append(quad([(-4.4,4.6,3.8),(-3.7,4.6,3.8),(-3.7,4.6,4.3),(-4.4,4.6,4.3)],(255,214,150),emit=True))
    return Q
BG=background()
BG=background()
# ---------------- driver: inside / stuck in the window ----------------
def driver_in(t):
    import random as _r
    p=0.45+0.55*sm((t-T_PULL[0])/(T_PULL[1]-T_PULL[0])); gl=gwin(t)
    Hs=(0.48,0.66,0.62); Hl=(0.5,0.98,0.24); H_=np.array(lerp3(Hs,Hl,p))
    tug=0.05*max(0.0,math.sin(2*math.pi*2.5*(t-T_PULL[0]))) if t>=T_PULL[0] else 0.0
    H_=H_+np.array([0,0,-tug])
    if gl:
        r=_r.Random(int(t*12))
        if r.random()<0.65: H_=H_+np.array([r.uniform(-0.06,0.06),r.uniform(-0.03,0.05),r.uniform(-0.05,0.03)])
    Lean=0.79+(1.75-0.79)*sm((t-T_PULL[0])/(T_PULL[1]-T_PULL[0]))
    yaw=0.0; nod=0.0
    if t<T_REACH[0]+0.2:
        s_=math.sin(2*math.pi*1.7*t); yaw=0.65*max(-1,min(1,s_*3))
    if gl: nod=0.45*math.sin(t*37)
    R=Rx(-Lean); d=R@np.array([0,1,0]); Sc=H_+d*0.52
    Rh=Ry(yaw)@Rx(-Lean-nod); Hc=Sc+(Rx(-Lean-nod)@np.array([0,1,0]))*0.21
    Q=[]; FP=[]
    Q+=obox(H_+d*0.27,(0.19,0.27,0.11),R,TANK)+obox(H_+d*0.47,(0.06,0.06,0.06),R,DSKIN)
    for sx in (-1,1): Q+=obox(Sc+R@np.array([sx*0.17,0.0,0.0]),(0.06,0.05,0.07),R,DSKIN)
    Q+=obox(Hc,(0.11,0.13,0.12),Rh,DSKIN)
    for sx in (-1,1): Q+=obox(Hc+Rh@np.array([sx*0.045,0.03,-0.121]),(0.02,0.012,0.004),Rh,(14,10,8))
    Q+=obox(Hc+Rh@np.array([0,0.11,0.01]),(0.115,0.035,0.125),Rh,HAIR)
    for k in range(7):
        xo=-0.09+0.03*k; root=Hc+Rh@np.array([xo,0.06,0.1])
        if gl: end=root+np.array([0.05*math.sin(t*29+k),0.42+0.05*math.sin(t*41+k),0.04*math.cos(t*23+k)])
        else: end=root+np.array([0.04*math.sin(t*3+k),-0.5,0])+Rh@np.array([xo*1.5,0,0.08])
        Q+=seg(root,end,0.035,HAIR)
    grabs=[]
    for sx in (-1,1):
        sh=Sc+R@np.array([sx*0.2,-0.02,0]); grabs.append(tuple(sh+np.array([0,0.04,-0.06])))
        sill=np.array((0.18 if sx<0 else 0.92,1.03,-0.03))
        if gl:
            w=2*math.pi*2.6*t+(0 if sx<0 else math.pi)
            hand=tuple(sh+np.array([sx*0.35*math.cos(w),0.4*math.sin(w),-0.25]))
        elif t<T_PULL[1]: hand=tuple(sill+np.array([0,0.04*math.sin(t*8+sx),0]))
        else: hand=tuple(sh+np.array([sx*0.3,-0.35,-0.1]))
        el=elbow(sh,hand,(sx*0.6,0,-0.3),0.6)
        Q+=seg(sh,el,0.09,DSKIN)+seg(el,hand,0.08,DSKIN)+obox(hand,(0.045,0.045,0.045),np.eye(3),DSKIN)
    for sx in (-1,1):
        hip=H_+np.array([sx*0.1,-0.03,0])
        clip=gl and (int(t*5)%3==1)
        if clip:   # legs clip straight up through the roof
            k=hip+np.array([0.15,0.55,sx*0.06]); f=k+np.array([0.05,0.5+0.05*math.sin(t*30),0])
            FP+=seg(hip,k,0.13,JEANS)+seg(k,f,0.11,JEANS)+obox(f,(0.06,0.09,0.04),np.eye(3),(220,220,220))
        else:
            k=hip+np.array([0.42,0.0,sx*0.1]); f=k+np.array([0.05,-0.42,0.0])
            Q+=seg(hip,k,0.13,JEANS)+seg(k,f,0.11,JEANS)+obox(f,(0.06,0.04,0.09),np.eye(3),(220,220,220))
    return Q,FP,grabs
# ---------------- driver: rigid glitch T-pose (flight, landing, standing) ----------------
def tpose_local(look=0.0):
    Q=[]
    for sx in (-1,1):
        Q+=seg((sx*0.1,0.88,0),(sx*0.12,0.06,0),0.13,JEANS)+box(sx*0.12-0.06,sx*0.12+0.06,0.0,0.07,-0.12,0.06,(220,220,220))
        Q+=seg((sx*0.2,1.36,0),(sx*0.86,1.36,0),0.09,DSKIN)+box(sx*0.86-0.045+sx*0.045,sx*0.86+0.045+sx*0.045,1.315,1.405,-0.045,0.045,DSKIN)
    Q+=box(-0.19,0.19,0.85,1.39,-0.11,0.11,TANK)+box(-0.06,0.06,1.39,1.5,-0.06,0.06,DSKIN)
    for sx in (-1,1): Q+=box(sx*0.17-0.06,sx*0.17+0.06,1.33,1.43,-0.07,0.07,DSKIN)
    Rh=Ry(look); hc=np.array([0,1.62,0])
    Q+=obox(hc,(0.11,0.13,0.12),Rh,DSKIN)
    for sx in (-1,1): Q+=obox(hc+Rh@np.array([sx*0.045,0.03,-0.121]),(0.02,0.012,0.004),Rh,(14,10,8))
    Q+=obox(hc+Rh@np.array([0,0.11,0.01]),(0.115,0.035,0.125),Rh,HAIR)
    for k in range(7):
        xo=-0.09+0.03*k; root=hc+Rh@np.array([xo,0.06,0.1]); Q+=seg(root,root+np.array([0,-0.5,0])+Rh@np.array([xo*1.5,0,0.08]),0.035,HAIR)
    return Q
LAND=(2.0,-1.1)
def driver_out(t):
    c=np.array([0,0.9,0])
    if t<T_LAND:
        u=(t-T_POP)/(T_LAND-T_POP); A=np.array([0.5,1.25,-0.15]); B=np.array([LAND[0],0.12,LAND[1]])
        pos=A+(B-A)*u; pos[1]+=1.1*math.sin(math.pi*u)
        pitch=(2*math.pi+math.pi/2)*u; yaw=0.6*u; base=pos-np.array([0,0.9,0])
    elif t<T_TPOSE:
        b=0.16*abs(math.sin(math.pi*(t-T_LAND)/0.25))*(t<T_LAND+0.5)*(1-(t-T_LAND)/0.6)
        base=np.array([LAND[0],0.12+b-0.9,LAND[1]]); pitch=math.pi/2; yaw=0.6
    else:
        base=np.array([LAND[0],0.0,LAND[1]]); pitch=0.0
        spin=2*math.pi*sm((t-T_TPOSE-0.15)/2.3); yaw=spin
        yaw+= 0.9*sm((t-T_TEXT)/0.4)
    look=0.0
    Q=tpose_local(look)
    M=Ry(yaw)@Rx(pitch)
    return transform(Q,lambda p:tuple(base+c+M@(np.array(p,float)-c)))
# ---------------- officer ----------------
def officer2(t,grabs):
    tf=min(t,T_FREEZE[0]) if t<T_FREEZE[1] else t
    walk=sm((t-T_WALK[0])/(T_WALK[1]-T_WALK[0])) if t>=T_WALK[0] else 0.0
    A=np.array([1.5,0,-0.6]); B=np.array([-0.38,0,-0.62])
    base=A+(B-A)*walk
    stepping=T_WALK[0]<=t<T_WALK[1]+0.3
    back=sm((t-T_OPEN[0])/(T_OPEN[1]-T_OPEN[0]))
    base=base+np.array([-0.12,0,-0.38])*back
    yaw=-0.95
    if t>=T_WALK[0]: yaw=-0.95+(-math.pi/2+0.95)*sm((t-T_WALK[0])/0.25)
    if t>=T_WALK[1]-0.05: yaw=-math.pi/2+(math.pi/2+0.25)*sm((t-T_WALK[1]+0.05)/0.25)
    reach=sm((tf-T_REACH[0])/(T_REACH[1]-T_REACH[0]))
    pulling=T_PULL[0]<=tf<T_POP
    lean=0.18*reach*(1-sm((tf-T_PULL[0])/0.3))
    if pulling: lean=-0.1-0.08*max(0.0,math.sin(2*math.pi*2.5*(tf-T_PULL[0])))
    head_yaw=0.0
    if t>=T_LOOK: head_yaw=0.85*sm((t-T_LOOK)/0.25)
    Rb=Ry(yaw); bc=base
    def W(p): return tuple(bc+Rb@np.array(p,float))
    def WL(p):
        p=np.array(p,float); piv=np.array([0,0.92,0]); return W(piv+Rx(lean)@(p-piv))
    sw=0.4*math.sin(2*math.pi*2.5*(t-T_WALK[0])) if stepping and t<T_WALK[1] else 0.0
    Q=[]
    for sx,ph in ((-1,1),(1,-1)):
        Q+=transform(box(sx*0.11-0.08,sx*0.11+0.08,0.06,0.92,-0.08,0.08,OPANTS)+box(sx*0.11-0.09,sx*0.11+0.09,0.0,0.07,-0.06,0.12,BLK),
                     lambda p,ph=ph:W(rx(p,ph*sw,(0,0.92,0))))
    Q+=box(-0.21,0.21,0.92,1.5,-0.12,0.12,OSHIRT,xf=WL)+box(-0.22,0.22,0.88,0.99,-0.13,0.13,BLK,xf=WL)
    Q+=box(-0.31,-0.22,0.7,0.96,-0.06,0.08,BLK,xf=WL)+box(0.07,0.14,1.3,1.38,0.12,0.126,(230,190,60),xf=WL)+box(0.1,0.18,1.4,1.5,0.06,0.13,BLK,xf=WL)
    Q+=box(-0.06,0.06,1.5,1.56,-0.06,0.06,OSKIN,xf=WL)
    def WH(p): return WL(ry(p,head_yaw,(0,1.67,0)))
    Q+=box(-0.11,0.11,1.54,1.8,-0.12,0.12,OSKIN,xf=WH)+box(-0.125,-0.11,1.62,1.7,-0.03,0.03,OSKIN,xf=WH)+box(0.11,0.125,1.62,1.7,-0.03,0.03,OSKIN,xf=WH)
    for sx in (-1,1): Q+=box(sx*0.045-0.02,sx*0.045+0.02,1.68,1.7,0.12,0.124,BLK,xf=WH)
    surprise=sm((tf-T_POP)/0.25)*(1-sm((t-T_FREEZE[1])/0.25))
    for k,sx in enumerate((-1,1)):
        sh=WL((sx*0.27,1.44,0))
        rest=WL((sx*0.3,0.98,0.05)); h=rest
        if tf>=T_REACH[0] and tf<T_POP+0.05: h=lerp3(rest,grabs[k] if grabs else rest,reach)
        h=lerp3(h,WL((sx*0.32,1.88,0.12)),surprise)
        if sx>0 and t>=T_WALK[1]+0.1:
            h=lerp3(h,handle_pos(t),sm((t-T_WALK[1]-0.1)/0.3)*(1-sm((t-T_OPEN[1]-0.15)/0.3)))
        el=elbow(sh,h,tuple(Rb@np.array([sx*0.6,0,-0.2])))
        Q+=seg(sh,el,0.11,OSHIRT)+seg(el,h,0.09,OSKIN)+obox(h,(0.05,0.05,0.05),np.eye(3),OSKIN)
    return Q,base
def split(Q):
    pre=[q for q in Q if q['c'][2]>0.03]; post=[q for q in Q if q['c'][2]<=0.03]; return pre,post
def lights(t):
    ph=(t*2.2)%1
    L=[((-0.3,2.0,-2.6),(255,255,255),1.9),((-2.6,1.8,-3.4),(60,90,255),3.4 if ph<0.5 else 1.2),((0.6,1.45,0.9),(255,220,170),0.35),((-4,4.5,4),(255,200,140),1.8)]
    if 0.5<=ph<0.68: L.append(((-0.9,1.8,-3.4),(255,40,40),2.2))
    return L
def shake_xy(t):
    sx=sy=0.0
    for th,amp in ((T_PULL[0],0.02),(T_LAND,0.05),(T_TPOSE,0.02),(T_OPEN[1],0.01))+tuple((a,0.03) for a,b in STUTTER):
        if 0<=t-th<0.25: q=1-(t-th)/0.25; sx+=amp*q*math.sin(97*t); sy+=amp*q*math.cos(71*t)
    return sx,sy
def camera(t):
    z=sm((t-T_PULL[0])/1.6); out=sm((t-T_POP)/0.5); fin=sm((t-T_TEXT)/2.2)
    pos=lerp3((-0.05,1.45,-2.75),(0.05,1.38,-2.2),z); tgt=lerp3((0.85,1.02,0.0),(0.8,0.95,-0.25),z)
    pos=lerp3(pos,(0.8,1.45,-3.5),out); tgt=lerp3(tgt,(0.9,0.92,-0.5),out)
    pos=lerp3(pos,(0.85,1.4,-3.55),fin); tgt=lerp3(tgt,(0.8,0.86,-0.5),fin)
    dx,dy,dyaw,dpit=motion.handheld(t,DUR,amp=0.6); sx,sy=shake_xy(t)
    c=Camera.look((pos[0]+dx+sx,pos[1]+dy+sy,pos[2]),tgt); return (c[0],c[1],c[2],c[3]+dyaw,c[4]+dpit)
R=Renderer(W,H,fog=(10,12,24))
def render(t):
    pre=list(CAR_PRE); main=list(CAR_MAIN); post_=[]
    grabs=None
    if t<T_POP:
        dq,fp,grabs=driver_in(t); a,b=split(dq); pre+=a; post_+=b+fp
    else: post_+=driver_out(t)
    oq,obase=officer2(t,grabs); a,b=split(oq); pre+=a; post_+=b
    dq,th=door(t)
    (main if th<0.03 else post_).extend(dq)
    img,vi=R.render(camera(t),[BG,pre,main,post_],lights(t),fov=58,fog_start=6,fog_end=22,ambient=0.2)
    return img,vi,obase
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

YEL=(255,214,40); WHT=(255,255,255); RED=(255,70,60); GRN=(90,230,90)
SKULL=[".#####.","#######","#..#..#","#..#..#","#######",".##.##.",".#####.",".#.#.#."]
def skull(d,x,y,sc):
    for j,row in enumerate(SKULL):
        for i,c in enumerate(row):
            if c=='#':
                d.rectangle([x+i*sc-1,y+j*sc-1,x+i*sc+sc,y+j*sc+sc],fill=(0,0,0))
    for j,row in enumerate(SKULL):
        for i,c in enumerate(row):
            if c=='#': d.rectangle([x+i*sc,y+j*sc,x+i*sc+sc-1,y+j*sc+sc-1],fill=(240,240,240))
def npc_hp(t):
    if t>=T_TPOSE: return 1.0
    h=1.0-0.12*sm((t-T_PULL[0])/1.8)
    if t>=T_GLITCH[0]: h-=0.55*min(1.0,(int((t-T_GLITCH[0])*6))/14.0)
    if t>=T_LAND: h=0.04
    return max(0.0,h)
def bar(d,x0,y,w,h_,frac,col,label,right=False):
    d.rectangle([x0-1,y-1,x0+w+1,y+6],fill=(0,0,0)); d.rectangle([x0,y,x0+w,y+5],fill=(70,10,10))
    fw=int(w*frac)
    if fw>0:
        if right: d.rectangle([x0+w-fw,y,x0+w,y+5],fill=col)
        else: d.rectangle([x0,y,x0+fw,y+5],fill=col)
    otext(d,label,x0 if not right else x0+w-font.width(label),y+9,WHT,1)
def star5(d,cx,cy,r,col):
    pts=[]
    for k in range(10):
        a=-math.pi/2+k*math.pi/5; rr=r if k%2==0 else r*0.45; pts.append((cx+rr*math.cos(a),cy+rr*math.sin(a)))
    d.polygon(pts,fill=col,outline=(0,0,0))
def hud(img,vi,t,obase):
    d=ImageDraw.Draw(img)
    bar(d,6,8,70,6,1.0,GRN,'COP')
    hp=npc_hp(t); bar(d,104,8,70,6,hp,(250,210,40) if hp>0.3 or int(t*8)%2 else RED,'NPC',right=True)
    lit=0 if t<T_PULL[0] else (2 if t<T_POP else 3)
    for k in range(5):
        on=k<lit and (int(t*4)%2==0 or t>=T_TPOSE)
        star5(d,118+k*12,38,4,YEL if on else (60,60,70))
    cx,cy=26,292; d.ellipse([cx-19,cy-19,cx+19,cy+19],fill=(20,40,30),outline=(200,200,200))
    for r_ in (7,13): d.ellipse([cx-r_,cy-r_,cx+r_,cy+r_],outline=(40,80,60))
    a=t*1.3; d.line([cx,cy,cx+18*math.cos(a),cy+18*math.sin(a)],fill=(90,200,120))
    d.polygon([(cx,cy-4),(cx-3,cy+3),(cx+3,cy+3)],fill=WHT); d.rectangle([cx+7,cy-9,cx+10,cy-6],fill=(80,140,255) if int(t*3)%2 else RED)
    if t<1.5:
        d.rectangle([20,236,160,256],fill=(0,0,0)); d.rectangle([20,236,160,256],outline=(180,180,180))
        pressed=0.85<=t<1.0
        otext(d,'PRESS',26,243,YEL,1)
        d.rectangle([56,240+pressed,68,252+pressed],fill=(230,230,230) if not pressed else YEL,outline=(0,0,0))
        font.text(d,'E',60,243+pressed,(0,0,0),1,None)
        otext(d,'TO EXIT VEHICLE',72,243,WHT,1)
    if 1.9<=t<4.6 and (t<2.2 or int(t*4)%4!=3):
        d.rectangle([14,224,166,250],fill=(40,0,0),outline=RED)
        d.polygon([(26,229),(20,242),(32,242)],fill=YEL,outline=(0,0,0)); font.text(d,'!',24,233,(0,0,0),1,None)
        otext(d,'NPC PATHFINDING',40,228,RED,1); otext(d,'ERROR',40,238,WHT,1)
    if T_FREEZE[0]+0.15<=t<T_FREEZE[1] and vi is not None:
        q=R.project((obase[0],2.05,obase[2]),vi)
        if q:
            x,y=int(q[0]),int(q[1])
            for k in range(8):
                a=2*math.pi*k/8+t*6; c=int(90+165*k/7); d.rectangle([x+7*math.cos(a)-1,y+7*math.sin(a)-1,x+7*math.cos(a)+1,y+7*math.sin(a)+1],fill=(c,c,c))
            wd=font.width('NOT RESPONDING'); otext(d,'NOT RESPONDING',max(3,min(W-wd-3,x-wd//2)),y-18,WHT,1)
    if t>=T_TEXT:
        u=sm((t-T_TEXT)/0.15); sc=2
        y0=int(52-20*(1-u))
        otext(d,'THE DOOR WAS',(W-font.width('THE DOOR WAS',sc))//2,y0,WHT,sc)
        wtot=font.width('UNLOCKED',sc)+6+14; x0=(W-wtot)//2
        otext(d,'UNLOCKED',x0,y0+20,YEL,sc); skull(d,x0+font.width('UNLOCKED',sc)+6,y0+19,2)
    return img
def glitch_lowres(img,t,seed):
    import random as _r
    a=np.asarray(img).copy(); r=_r.Random(seed)
    o=a.copy(); o[:,2:,0]=a[:,:-2,0]; o[:,:-2,2]=a[:,2:,2]
    for _ in range(r.randint(2,5)):
        y0=r.randint(40,280); h=r.randint(3,14); o[y0:y0+h]=np.roll(o[y0:y0+h],r.randint(-18,18),axis=1)
    if r.random()<0.4:
        y0=r.randint(80,240); o[y0:y0+2]=[255,0,255]
    return Image.fromarray(o)
def time_eff(t):
    for a,b in STUTTER:
        if a<=t<b: return a+math.floor((t-a)*6)/6
    return t
def frame(t):
    te=time_eff(t)
    img,vi,ob=render(te)
    img=post.ps1(img)
    g=any(a<=t<b for a,b in STUTTER) or (T_POP<=t<T_POP+0.12)
    if g: img=glitch_lowres(img,t,int(t*FPS))
    if abs(t-T_TPOSE)<1.5/FPS: img=img.point(lambda v:min(255,v+60))
    return hud(img,vi,t,ob),g
N=int(DUR*FPS)
TEST=os.environ.get('TEST')
if TEST:
    ims=[frame(float(x))[0] for x in TEST.split(',')]; sh=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): sh.paste(im,(i*182,0))
    sh.resize((sh.width*2,640),Image.NEAREST).save('test.png'); sys.exit()

# ---------------- sound ----------------
s=Sound(DUR,loop=False,seed=9)
eng=(np.sin(2*np.pi*31*s.t)*0.6+np.sin(2*np.pi*62*s.t)*0.3)*0.02; s.L+=eng; s.R+=eng
s.bed(s.filt(s.rng.normal(0,1,s.n),lo=150,hi=1800)*0.02)
for k,tt in enumerate(np.arange(0.3,DUR,0.9)):
    tc=s.T(0.06); s.place(np.sin(2*np.pi*4600*tc)*(np.sin(2*np.pi*60*tc)>0)*np.exp(-tc*30),tt+0.13*math.sin(k),0.012,pan=-0.6 if k%2 else 0.6)
def sq(t0,notes,step,v,dec=8):
    for i,m in enumerate(notes):
        f=440*2**((m-69)/12); tt=s.T(step*1.8); s.place(np.sign(np.sin(2*np.pi*f*tt))*np.exp(-tt*dec),t0+i*step,v)
def noise_burst(t0,d,lo,hi,v,seed,shape=2):
    x=s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape; s.place(x,t0,v)
def sweep(t0,d,f0,f1,v,square=False):
    tt=s.T(d); f=f0+(f1-f0)*tt/d; ph=2*np.pi*np.cumsum(f)/s.sr; x=np.sign(np.sin(ph)) if square else np.sin(ph)
    s.place(x*np.sin(np.pi*tt/d)**0.5,t0,v)

mus=s.L.copy()*0, s.R.copy()*0
L0,R0=s.L.copy(),s.R.copy()
for k in range(int(T_FREEZE[0]/0.25)):                       # PS1 bass loop, stops dead when the cop freezes
    m=[45,45,52,48,45,45,55,52][k%8]; f=440*2**((m-69)/12); tt=s.T(0.22)
    s.place(s.filt_short(np.sign(np.sin(2*np.pi*f*tt)),hi=900)*np.exp(-tt*6),k*0.25,0.03)
    if k%2==0: tt=s.T(0.1); s.place(np.sin(2*np.pi*(120-60*tt/0.1)*tt)*np.exp(-tt*30),k*0.25,0.06)
g=np.ones(s.n); g[int(T_FREEZE[0]*s.sr):]=0; s.L=L0+(s.L-L0)*g; s.R=R0+(s.R-R0)*g
sweep(0.0,0.35,700,1400,0.08); sweep(0.35,0.35,1400,700,0.08)                     # siren whoop
sq(0.1,[84],0.05,0.04,dec=20); sq(0.88,[76],0.05,0.05,dec=25)                    # prompt blip, E key click
tt=s.T(0.25); s.place(np.sign(np.sin(2*np.pi*110*tt))*np.exp(-tt*6),0.95,0.05)    # nothing happens buzz
noise_burst(T_REACH[0],0.25,600,4000,0.22,4); s.thud(T_PULL[0],f=90,v=0.25)
tt=s.T(1.8); s.place(np.sin(2*np.pi*np.cumsum(150+180*tt/1.8+25*np.sin(2*np.pi*5*tt))/s.sr)*0.6*np.sin(np.pi*tt/1.8),T_PULL[0],0.07)  # stretchy strain
for k in range(5): s.place(s.filt_short(s.noise(0.06,50+k),lo=200,hi=1500)*np.exp(-s.T(0.06)*40),T_PULL[0]+k*0.4,0.15)       # tug grunts (thuds)
for tt0 in (1.9,2.15): sq(tt0,[86,74],0.06,0.05,dec=14)                           # error beeps
for a,b in STUTTER:                                                              # digital stutter: a tiny buffer looped
    tt=s.T(0.05); grain=np.sign(np.sin(2*np.pi*(300+600*np.random.default_rng(int(a*100)).random())*tt))*np.hanning(len(tt))
    for k in range(int((b-a)/0.05)): s.place(grain,a+k*0.05,0.05)
for k in range(int((T_POP-T_GLITCH[0])/0.17)):                                   # plastic ragdoll clacks
    rr=np.random.default_rng(k); s.place(s.filt_short(s.noise(0.03,200+k),lo=800,hi=5000)*np.exp(-s.T(0.03)*120),T_GLITCH[0]+k*0.17+rr.uniform(0,0.05),0.12,pan=rr.uniform(-0.5,0.5))
tt=s.T(0.3); s.place(np.sin(2*np.pi*np.cumsum(200+900*tt/0.3)/s.sr)*np.exp(-tt*5),T_POP,0.14)   # pop out
noise_burst(T_POP+0.05,0.6,400,3500,0.18,9)                                      # spin whoosh
s.thud(T_LAND,f=65,v=0.45); s.thud(T_LAND+0.25,f=80,v=0.15)
sweep(T_TPOSE-0.05,0.12,2500,4500,0.05); sq(T_TPOSE+0.05,[84,91],0.05,0.05,dec=10)  # snap to T-pose + HP refill
tt=s.T(0.45); hang=np.tile(np.sign(np.sin(2*np.pi*233*s.T(0.04)))*0.6,12)[:len(tt)]; s.place(hang,T_FREEZE[0],0.05)  # frozen audio buzz
sq(T_FREEZE[1],[79],0.05,0.04,dec=20)
for k in range(4): s.place(s.filt_short(s.noise(0.05,300+k),lo=150,hi=1200)*np.exp(-s.T(0.05)*60),T_WALK[0]+0.1+k*0.2,0.2)   # footsteps
s.place(s.filt_short(s.noise(0.03,400),lo=1500,hi=6000)*np.exp(-s.T(0.03)*150),T_HANDLE,0.25)                       # handle click
tt=s.T(0.65); s.place(np.sin(2*np.pi*np.cumsum(420+130*np.sin(2*np.pi*1.3*tt)+60*np.sin(2*np.pi*23*tt))/s.sr)*np.sin(np.pi*tt/0.65)*0.5,T_OPEN[0],0.08)  # creak
tr=[(T_TEXT+0.05,58,0.28),(T_TEXT+0.36,57,0.28),(T_TEXT+0.67,56,0.28),(T_TEXT+0.98,55,0.9)]                          # sad trombone
for t0,m,d in tr:
    tt=s.T(d); f=440*2**((m-69)/12)*(1+(0.03*np.sin(2*np.pi*6*tt) if d>0.5 else 0)); ph=2*np.pi*np.cumsum(np.ones_like(tt)*f)/s.sr
    s.place(s.filt_short(np.sign(np.sin(ph))+0.5*np.sign(np.sin(2*ph)),hi=1800)*np.minimum(1,tt/0.03)*np.exp(-np.maximum(0,tt-d*0.6)*6),t0,0.05)
s.reverb(0.12,length=0.8,decay=5)
wav=s.save(os.path.join(OUT,'npc_exit.wav'),peak=0.85)
vhs=post.VHS(W*S,H*S,S,grade='cold_blue',chroma=2,scan_dark=0.92,vignette=0.3,grain=2.0,band_period=1e9)
mp4=os.path.join(OUT,'npc_exit.mp4')
with post.Encoder(mp4,W*S,H*S,wav,FPS,DUR) as enc:
    for f in range(N):
        t=f/FPS; img,g=frame(t); enc.write(vhs(post.upscale(img,S),f,t,glitch=g))
print('probe',check.probe(mp4))
