"""THE RAT KING - "I Stole From The Wrong Rat". 60 s PS1 RPG short, 9:16. Everything procedural (nightkit).
Run: python examples/rat_king.py -> out/rat_king.mp4    REF=1 renders the character reference sheet."""
import os, sys, math, json, wave
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, box, quad, tiled_plane, transform, rx, ry, rz
from nightkit import motion, post, font, check
from nightkit.audio import Sound
font.FONT['+']=['00000','00100','00100','11111','00100','00100','00000']
OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6
sm=motion.smooth
def seg01(t,a,b): return max(0.0,min(1.0,(t-a)/(b-a)))
def win(t,a,b,ra=0.2,rb=0.2): return sm(seg01(t,a,a+ra))*(1-sm(seg01(t,b-rb,b)))
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


def Rz(a): c,s=math.cos(a),math.sin(a); return np.array([[c,-s,0],[s,c,0],[0,0,1]])
def place(Q,base,yaw=0.0,scale=1.0):
    Rb=Ry(yaw); b=np.array(base,float); return transform(Q,lambda p:tuple(b+Rb@(np.array(p,float)*scale)))
# ---------------- palette ----------------
FUR=(128,106,92); FUR_D=(104,86,74); BELLY=(176,156,140); TUFT=(240,236,228); PINK=(236,150,160); EYE=(10,8,8)
IRON=(74,76,86); IRON_L=(110,112,124); GOLD=(240,196,60); CAPE=(170,24,36); RUST=(150,104,72)
SILVER=(178,184,196); SILVER_D=(130,136,150); TABARD=(40,70,170); BOOT=(66,52,44); PLUME=(210,30,40)
CHEESE=(250,212,64); CHEESE_D=(214,170,40)
# ---------------- cheese ----------------
def cheese_local(s=1.0):
    a=(0,0,0); b=(0.12*s,0,0); c=(0.02*s,0,0.09*s); h=0.07*s
    Q=[quad([a,b,c],CHEESE_D),quad([(a[0],h,a[2]),(c[0],h,c[2]),(b[0],h,b[2])],CHEESE)]
    for p,q in ((a,b),(b,c),(c,a)): Q.append(quad([p,q,(q[0],h,q[2]),(p[0],h,p[2])],CHEESE))
    for (x,y) in ((0.035,0.03),(0.075,0.045),(0.055,0.02)):
        Q.append(quad([(x*s,y*s,-0.002),(x*s+0.012*s,y*s,-0.002),(x*s+0.012*s,y*s+0.012*s,-0.002),(x*s,y*s+0.012*s,-0.002)],CHEESE_D))
    return transform(Q,lambda p:(p[0]-0.05*s,p[1]-0.035*s,p[2]-0.03*s))
def cheese_at(center,yaw=0.0,s=1.0,glow=0.0):
    Q=place(cheese_local(s),center,yaw)
    if glow>0:
        for q in Q: q['emit']=True; q['col']=tuple(min(255,int(c+80*glow)) for c in q['col'])
    return Q
# ---------------- the rat (same model at every size) ----------------
def ear_poly(r,notch):
    pts=[]
    for k in range(10):
        a=math.pi/2-2*math.pi*k/10
        if notch and k==1:
            pts+=[(r*math.cos(a+0.3),r*math.sin(a+0.3)),(0.32*r*math.cos(a),0.32*r*math.sin(a)),(r*math.cos(a-0.3),r*math.sin(a-0.3))]
        else: pts.append((r*math.cos(a),r*math.sin(a)))
    return pts
def ear(sx,droop,notch):
    Q=[]; c=np.array([sx*0.075,0.43,-0.005])
    def T(x,y,z):
        p=np.array([x*sx,y,z]); p=Rz(sx*(-0.35-0.9*droop))@p; p=Rx(-0.25-0.6*droop)@p; return tuple(c+p)
    outer=ear_poly(0.07,notch); inner=ear_poly(0.046,notch)
    for i in range(len(outer)):
        a,b=outer[i],outer[(i+1)%len(outer)]; Q.append(quad([T(0,0,0),T(a[0],a[1],0),T(b[0],b[1],0)],FUR))
    for i in range(len(inner)):
        a,b=inner[i],inner[(i+1)%len(inner)]; Q.append(quad([T(0,-0.004,-0.004),T(a[0],a[1]-0.004,-0.004),T(b[0],b[1]-0.004,-0.004)],PINK))
    return Q
def rat_local(t,armor=0,eye=1.0,droop=0.0,sad=0.0,happy=0.0,glow=0.0,rp=None,lp=None,sword=None,sword_kind='rusty',
              hug_cheese=False,bob=0.0,lean=0.0,head_yaw=0.0,head_pitch=0.0,tail_wag=1.0):
    Q=[]; D=[]
    for sx in (-1,1):
        Q+=box(sx*0.05-0.035,sx*0.05+0.035,0.0,0.022,-0.07,0.01,PINK)+box(sx*0.055-0.03,sx*0.055+0.03,0.02,0.09,-0.035,0.035,FUR)
        if armor>=3: Q+=box(sx*0.055-0.034,sx*0.055+0.034,0.05,0.095,-0.04,0.0,IRON_L)
    body=box(-0.11,0.11,0.07,0.27,-0.09,0.09,FUR)+box(-0.08,0.08,0.09,0.22,-0.093,-0.09,BELLY)
    tuft=[quad([(-0.04,0.275,-0.096),(0.04,0.275,-0.096),(0.0,0.205,-0.096)],TUFT),quad([(-0.055,0.26,-0.095),(-0.02,0.27,-0.095),(-0.035,0.225,-0.095)],TUFT),quad([(0.02,0.27,-0.095),(0.055,0.26,-0.095),(0.035,0.225,-0.095)],TUFT)]
    if armor>=2:
        body+=box(-0.105,0.105,0.09,0.205,-0.105,-0.093,IRON)+box(-0.02,0.02,0.12,0.19,-0.109,-0.105,GOLD)
        for sx in (-1,1): body+=box(sx*0.1-0.05,sx*0.1+0.05,0.23,0.29,-0.07,0.07,IRON_L)
    if armor>=3: body+=box(-0.12,0.12,0.02,0.28,0.09,0.105,CAPE)
    piv=np.array([0,0.07,0])
    def B(p): p=np.array(p,float); return tuple(piv+Rx(-lean)@(p-piv)+np.array([0,bob,0]))
    Q+=transform(body,B); D+=transform(tuft,B)
    # head
    hc=np.array([0,0.335,-0.005])
    Hd=box(-0.085,0.085,0.27,0.4,-0.08,0.07,FUR)+box(-0.045,0.045,0.28,0.345,-0.15,-0.08,FUR_D)
    Fd=box(-0.018,0.018,0.32,0.348,-0.165,-0.148,PINK)+box(-0.011,0.011,0.262,0.284,-0.137,-0.127,(250,250,245))
    for sx in (-1,1):
        x=sx*0.045; e=0.012*eye
        if happy>0.5: Fd+=box(x-0.016,x+0.016,0.352,0.358,-0.083,-0.081,EYE)+box(x+sx*0.012-0.012,x+sx*0.012+0.012,0.315,0.325,-0.082,-0.08,(250,160,170))
        else:
            ec=(255,40,30) if glow>0.5 else EYE
            Fd+=box(x-e,x+e,0.355-e,0.355+e,-0.084,-0.08,ec,emit=glow>0.5)
            if glow<0.5: Fd+=box(x-0.004-sx*0.003,x+0.003-sx*0.003,0.358+0.004*eye,0.364+0.005*eye,-0.0855,-0.084,(255,255,250),emit=True)
        for k in (-1,0,1):
            Hd+=seg((sx*0.04,0.315+0.01*k,-0.13),(sx*0.13,0.32+0.03*k,-0.12),0.004,(40,30,30),depth=0.004)
        Hd+=ear(sx,droop,notch=(sx<0))
    if armor>=1:
        Hd+=box(-0.09,0.09,0.375,0.415,-0.085,0.075,IRON)+box(-0.093,0.093,0.37,0.38,-0.088,0.078,IRON_L)
    if armor>=3:
        Hd+=box(-0.06,0.06,0.415,0.44,-0.04,0.04,GOLD)
        for k in range(5): x=-0.05+0.025*k; Hd+=box(x-0.008,x+0.008,0.44,0.47,-0.008,0.008,GOLD)
    if sad>0:
        for sx in (-1,1):
            for k in range(2):
                u=((t*1.3+k*0.5+(0.25 if sx>0 else 0))%1.0); y=0.34-0.09*u
                Fd+=box(sx*0.05-0.006,sx*0.05+0.006,y-0.008,y+0.008,-0.09-0.02*u,-0.084-0.02*u,(120,190,255),emit=True)
    def HH(p):
        p=np.array(p,float); p=hc+Ry(head_yaw)@Rx(head_pitch)@(p-hc); return B(p)
    Q+=transform(Hd,HH); D+=transform(Fd,HH)
    # arms + paws (+ sword / cheese)
    rp=rp or (0.11,0.15,-0.07); lp=lp or (-0.11,0.15,-0.07)
    if hug_cheese: rp=(0.03,0.2,-0.13); lp=(-0.03,0.2,-0.13)
    for sx,pp in ((1,rp),(-1,lp)):
        sh=np.array(B((sx*0.1,0.24,-0.02))); pp=np.array(B(pp))
        Q+=seg(sh,pp,0.045,FUR)+box(pp[0]-0.025,pp[0]+0.025,pp[1]-0.025,pp[1]+0.025,pp[2]-0.025,pp[2]+0.025,IRON_L if armor>=3 else PINK)
    if hug_cheese: Q+=cheese_at(B((0.0,0.21,-0.15)),0.3,1.0)
    if sword is not None:
        hand=np.array(B(rp)); d=np.array(sword,float); d/=np.linalg.norm(d)+1e-9
        if sword_kind=='rusty': L,wd,col,gc=0.36,0.024,RUST,(120,90,60)
        else: L,wd,col,gc=0.46,0.05,(150,156,170),GOLD
        side=np.cross(d,np.array([0,0,1.0])); side/=np.linalg.norm(side)+1e-9
        Q+=seg(hand-d*0.04,hand+d*0.02,0.016,(80,50,30))+seg(hand+d*0.02-side*wd*1.6,hand+d*0.02+side*wd*1.6,0.018,gc)
        Q+=seg(hand+d*0.02,hand+d*L,wd,col,depth=0.012)
        if sword_kind=='rusty': Q+=seg(hand+d*0.15,hand+d*0.22,wd*1.05,(120,80,50),depth=0.013)
    # tail
    pts=[]
    for k in range(9):
        u=k/8; pts.append((0.06*math.sin(2.2*u*math.pi+t*3*tail_wag)*u,0.06+0.08*u*u,0.09+0.32*u))
    for a,b in zip(pts,pts[1:]): Q+=seg(a,b,0.022-0.012*pts.index(a)/8,PINK)
    return Q,D
def ear_notch_world(base,yaw,scale):
    c=np.array([-0.075,0.43,-0.005]); a=math.pi/2-2*math.pi/10; r=0.07*0.72
    p=np.array([-r*math.cos(a),r*math.sin(a),0.0]); p=Rz(0.35)@p; p=Rx(-0.25)@p
    return tuple(np.array(base,float)+Ry(yaw)@((c+p)*scale))
def rat(base,yaw,scale,t,**kw):
    Q,D=rat_local(t,**kw)
    for q in D: q['hc']=np.array(base,float)+Ry(yaw)@(np.array((0,0.335,-0.005) if q['c'][1]>0.29 else (0,0.17,0.0))*scale)
    return place(Q,base,yaw,scale),place(D,base,yaw,scale)
# ---------------- the knight ----------------
def knight(base,yaw,t,walk=0.0,rhand=None,lhand=None,lean=0.0,sword=True,sword_dir=(0,0.3,-1),sit=0.0,cheese=False,cheese_glow=0.0,head_yaw=0.0,head_pitch=0.0):
    bc=np.array(base,float); Rb=Ry(yaw)
    def W(p): return tuple(bc+Rb@np.array(p,float))
    hip_y=0.86-0.5*sit
    def WL(p):
        p=np.array(p,float)+np.array([0,hip_y-0.86,0]); piv=np.array([0,hip_y,0]); return W(piv+Rx(lean)@(p-piv))
    Q=[]; sw=0.45*math.sin(walk)
    for sx,ph in ((-1,1),(1,-1)):
        hip=np.array([sx*0.1,hip_y,0.0])
        if sit>0: ft=np.array([sx*0.13,0.06,-0.75*sit]); kn=(hip+ft)/2+np.array([0,0.12*sit,0])
        else:
            a=ph*sw; ft=hip+np.array([0,-0.82*math.cos(a),-0.82*math.sin(a)]); ft[1]=max(0.06,ft[1]); kn=(hip+ft)/2+np.array([0,0,-0.05])
        Q+=transform(seg(hip,kn,0.14,SILVER_D)+seg(kn,ft,0.13,SILVER)+box(ft[0]-0.07,ft[0]+0.07,ft[1]-0.06,ft[1]+0.04,ft[2]-0.12,ft[2]+0.06,BOOT),W)
    D=[]
    Q+=box(-0.2,0.2,0.86,1.42,-0.12,0.12,SILVER,xf=WL); D+=box(-0.13,0.13,0.6,1.36,-0.126,-0.12,TABARD,xf=WL)
    D+=box(-0.05,0.05,1.08,1.22,-0.13,-0.126,GOLD,xf=WL); Q+=box(-0.21,0.21,0.84,0.92,-0.128,0.128,(90,60,40),xf=WL)
    for sx in (-1,1): Q+=box(sx*0.27-0.09,sx*0.27+0.09,1.3,1.44,-0.11,0.11,SILVER_D,xf=WL)
    hc=np.array([0,1.6,0])
    def WH(p): p=np.array(p,float); return WL(hc+Ry(head_yaw)@Rx(head_pitch)@(p-hc))
    Q+=box(-0.13,0.13,1.44,1.76,-0.13,0.12,SILVER,xf=WH); D+=box(-0.1,0.1,1.58,1.62,-0.136,-0.13,(10,10,14),xf=WH)+box(-0.015,0.015,1.46,1.62,-0.135,-0.13,SILVER_D,xf=WH)
    Q+=transform(seg((0,1.76,0.0),(0,1.95,0.08),0.07,PLUME)+seg((0,1.95,0.08),(0,1.88,0.3),0.06,PLUME),WH)
    rh=np.array(WL(rhand or (-0.3,0.95,-0.12))); lh=np.array(WL(lhand or (0.3,0.95,-0.05)))
    for sx,h in ((-1,rh),(1,lh)):
        sh=np.array(WL((sx*0.28,1.36,0))); el=elbow(sh,h,tuple(Rb@np.array([sx*0.6,0,-0.2])))
        Q+=seg(sh,el,0.11,SILVER)+seg(el,h,0.1,SILVER_D)+obox(h,(0.06,0.06,0.06),Rb,(90,92,100))
    if sword:
        d=Rb@np.array(sword_dir,float); d/=np.linalg.norm(d)+1e-9; side=np.cross(d,np.array([0,1.0,0.0001])); side/=np.linalg.norm(side)+1e-9
        Q+=seg(rh-d*0.1,rh+d*0.05,0.04,(90,60,40))+seg(rh+d*0.05-side*0.12,rh+d*0.05+side*0.12,0.045,GOLD)+seg(rh+d*0.06,rh+d*0.8,0.07,(225,230,240),depth=0.02)
    if cheese: Q+=cheese_at(tuple(lh+np.array([0,0.07,0])),yaw,1.0,glow=cheese_glow)
    hcW=np.array(WL((0,1.6,0))); tcW=np.array(WL((0,1.05,0)))
    for q in D: q['hc']=hcW if q['c'][1]>hcW[1]-0.25 else tcW
    return Q,D
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


# ---------------- sets ----------------
import random
def tree(x,z,h=2.6,r=0.9,seed=0):
    Q=box(x-0.12,x+0.12,0,h*0.45,z-0.12,z+0.12,(96,66,40))
    for k,(y0,rr) in enumerate(((h*0.35,r),(h*0.6,r*0.75),(h*0.82,r*0.5))):
        n=7; top=(x,y0+h*0.35,z)
        for i in range(n):
            a0=2*math.pi*i/n+seed; a1=2*math.pi*(i+1)/n+seed
            Q.append(quad([top,(x+rr*math.cos(a1),y0,z+rr*math.sin(a1)),(x+rr*math.cos(a0),y0,z+rr*math.sin(a0))],(46,120,52) if (i+k)%2 else (38,104,46)))
    return Q
def forest_set():
    r=random.Random(5); Q=[]
    G=tiled_plane(-8,8,-6,12,0,1.0,lambda i,j:(70,140,60) if (i*3+j)%4 else (62,128,54))
    P=tiled_plane(-8,8,-0.75,0.2,0.004,1.0,lambda i,j:(150,120,80) if (i+j)%2 else (140,110,72))
    for x,z,h in ((-3.2,3.0,3.0),(-1.6,4.5,2.6),(1.8,3.6,3.2),(3.6,2.4,2.8),(0.2,6.0,3.4),(-4.5,6.5,3.0),(4.8,6.0,3.2),(-2.6,1.6,2.2),(2.9,1.2,2.4)): Q+=tree(x,z,h,0.9,seed=x)
    for k in range(8):
        x=r.uniform(-5,5); z=r.uniform(1.2,5); s_=r.uniform(0.15,0.35); Q+=box(x-s_,x+s_,0,s_*0.8,z-s_,z+s_,(130,130,126))
    for i in range(8):                                                   # stump
        a0=2*math.pi*i/8; a1=2*math.pi*(i+1)/8; c=(0.5,0.4)
        p0=(c[0]+0.24*math.cos(a0),c[1]+0.24*math.sin(a0)); p1=(c[0]+0.24*math.cos(a1),c[1]+0.24*math.sin(a1))
        Q.append(quad([(p0[0],0,p0[1]),(p1[0],0,p1[1]),(p1[0],0.35,p1[1]),(p0[0],0.35,p0[1])],(110,76,46)))
        Q.append(quad([(c[0],0.35,c[1]),(p1[0],0.35,p1[1]),(p0[0],0.35,p0[1])],(200,166,110)))
    return G,P,Q
FOREST_G,FOREST_P,FOREST_R=forest_set(); FOREST=FOREST_G+FOREST_P+FOREST_R
def dummy(x,z,s=1.0,hit=0.0,smashed=0.0,t=0.0):
    Q=[]; wob=0.25*hit*math.sin(t*40)
    if smashed<=0:
        def T(p): p=np.array(p,float); return tuple(np.array([x,0,z])+Rz(wob)@(p*s))
        Q+=transform(box(-0.03,0.03,0,0.5,-0.03,0.03,(110,80,50))+box(-0.1,0.1,0.25,0.5,-0.07,0.07,(214,186,110))+box(-0.07,0.07,0.5,0.62,-0.06,0.06,(220,192,120))+box(-0.18,0.18,0.38,0.42,-0.025,0.025,(200,170,100)),T)
    else:
        rr=random.Random(9)
        for k in range(10):
            a=rr.uniform(0,2*math.pi); d=smashed*rr.uniform(0.3,1.2)*s; y=max(0.0,rr.uniform(0.2,0.6)*s+smashed*1.6*s-4.9*(smashed*0.6)**2*s)
            px=x+math.cos(a)*d; pz=z+math.sin(a)*d; q=0.05*s
            Q+=box(px-q,px+q,y,y+q*1.4,pz-q,pz+q,(214,186,110) if k%2 else (110,80,50))
    return Q
def castle_set():
    Q=[]
    Q+=tiled_plane(-8,8,-9,1,0,1.0,lambda i,j:(84,80,92) if (i+j)%2 else (74,70,82))
    for x0,x1 in ((-8,-1.4),(1.4,8)):
        Q+=box(x0,x1,0,6.0,0.0,0.8,(98,96,110))
        for x in np.arange(x0,x1,0.8): Q+=box(x,x+0.4,6.0,6.5,0.0,0.8,(98,96,110))
    Q+=box(-1.4,1.4,3.6,6.0,0.0,0.8,(98,96,110))
    for x in (-3.4,3.4): Q+=box(x-1.0,x+1.0,0,8.0,-0.4,1.0,(88,86,100))+box(x-1.1,x+1.1,8.0,8.5,-0.5,1.1,(98,96,110))
    for j in range(7):
        for i in range(-8,8):
            if (i+j)%3==0: Q+=box(i+0.05,i+0.55,j*0.85+0.1,j*0.85+0.3,-0.01,0.0,(84,82,96))
    Q+=box(-1.5,1.5,3.4,3.6,-0.05,0.8,(70,66,76))
    return Q
CASTLE=castle_set()
def castle_door(open_k):
    Q=[]; DQ=[]
    for sx in (-1,1):
        def T(p,sx=sx): p=np.array(p,float); q=Ry(sx*1.4*open_k)@(p-np.array([sx*1.4,0,0]))+np.array([sx*1.4,0,0]); return tuple(q)
        panel=box(min(0,sx*1.4),max(0,sx*1.4),0,3.4,0.05,0.15,(96,62,36))
        for y in (0.6,1.7,2.8): panel+=box(min(0,sx*1.4),max(0,sx*1.4),y,y+0.12,0.03,0.05,(50,50,56))
        Q+=transform(panel,T)
    sk=[".###.","#####","#.#.#","#####",".#.#."]
    for j,row in enumerate(sk):
        for i,c in enumerate(row):
            if c=='#' and open_k<0.05: x=0.5-i*0.2-0.2; y=2.6-j*0.2; DQ.append(quad([(x,y,0.02),(x+0.2,y,0.02),(x+0.2,y+0.2,0.02),(x,y+0.2,0.02)],(230,226,210)))
    Q.append(quad([(-1.4,0,0.6),(1.4,0,0.6),(1.4,3.4,0.6),(-1.4,3.4,0.6)],(8,6,10)))
    return Q,DQ
def flame(x,y,z,t,s=1.0,on=1.0,seed=0):
    if on<=0: return []
    f=0.8+0.2*math.sin(t*17+seed)+0.1*math.sin(t*29+seed*2)
    h=0.32*s*f*on; w=0.1*s*on
    return [quad([(x-w,y,z),(x+w,y,z),(x,y+h,z)],(255,170,40),emit=True),quad([(x,y,z-w),(x,y,z+w),(x,y+h*0.8,z)],(255,220,90),emit=True)]
def boss_room():
    Q=[]
    F=tiled_plane(-6,6,-6,9,0,1.0,lambda i,j:(70,66,72) if (i+j)%2 else (58,54,60))
    C=tiled_plane(-1.2,1.2,-6,7,0.004,1.0,lambda i,j:(120,20,30))
    Q+=box(-6,6,0,8,9,9.4,(64,60,70))+box(-6.4,-6,0,8,-6,9.4,(60,56,66))+box(6,6.4,0,8,-6,9.4,(60,56,66))
    for x in (-3.4,3.4):
        for z in (-3.0,0.5,4.0,7.5): Q+=box(x-0.4,x+0.4,0,7.0,z-0.4,z+0.4,(86,82,92))+box(x-0.5,x+0.5,0,0.4,z-0.5,z+0.5,(76,72,82))
    Q+=box(-1.6,1.6,0,0.8,6.6,8.4,(80,70,60))+box(-1.6,1.6,0.8,4.8,8.0,8.4,(120,20,30))+box(-1.8,1.8,4.6,5.4,7.9,8.5,(240,196,60))
    for x in (-1.6,1.6): Q+=box(x-0.2,x+0.2,0,2.6,6.6,7.0,(240,196,60))
    return F,C,Q
BOSS_F,BOSS_C,BOSS_R=boss_room(); BOSSROOM=BOSS_F+BOSS_C+BOSS_R
TORCHES=[(x*2.9,2.6,z) for z in (-3.0,0.5,4.0,7.5) for x in (-1,1)]
if os.environ.get('REF'):
    R0=Renderer(240,320,fog=(36,40,60)); tiles=[]
    def shot(parts,cam,lights,label):
        if isinstance(parts,tuple): parts=[parts]
        layers=[tiled_plane(-3,3,-3,3,0,0.5,lambda i,j:(70,74,90) if (i+j)%2 else (60,64,80))]
        for q,dd in parts: layers+=[q,dd]
        img,vi=R0.render(cam,layers,lights,fov=40,fog_start=20,fog_end=60,ambient=0.45)
        img=post.ps1(img); d=ImageDraw.Draw(img); otext(d,label,(240-font.width(label))//2,8,(255,214,40),1); return img
    Lg=[((-1.5,3,-3),(255,245,230),6.0),((2,2,-2),(180,200,255),3.0)]
    tiles.append(shot(knight((0,0,0),0.0,0.0),Camera.look((0.6,1.3,-3.0),(0,0.95,0)),Lg,'KNIGHT LV 1'))
    tiles.append(shot(rat((0,0,0),0.0,1.0,0.0,rp=(0.1,0.16,-0.08),lp=(-0.03,0.2,-0.13),hug_cheese=True),Camera.look((0.12,0.32,-0.75),(0,0.22,0)),Lg,'RAT LV 1'))
    tiles.append(shot(rat((0,0,0),0.0,1.0,0.0,armor=1,sword=(0.3,1,-0.2),rp=(0.12,0.2,-0.08)),Camera.look((0.12,0.32,-0.75),(0,0.22,0)),Lg,'RAT LV 15'))
    tiles.append(shot(rat((0,0,0),0.0,1.0,0.0,armor=2,sword=(0.3,1,-0.2),rp=(0.12,0.2,-0.08)),Camera.look((0.12,0.32,-0.75),(0,0.22,0)),Lg,'RAT LV 47'))
    tiles.append(shot([rat((0,0,0),0.0,9.5,0.0,armor=3,glow=1.0,sword=(0.2,1,-0.3),sword_kind='king',rp=(0.12,0.2,-0.09)),knight((1.6,0,-1.6),0.4,0.0)],Camera.look((2.4,2.4,-8.0),(0,2.3,0)),Lg,'RAT KING LV 99'))
    tiles.append(shot(rat((0,0,0),0.0,1.0,0.0,armor=3,sword=(0.2,1,-0.3),sword_kind='king',rp=(0.12,0.2,-0.09)),Camera.look((-0.05,0.4,-0.42),(-0.05,0.36,0)),Lg,'SAME EAR. SAME RAT.'))
    tiles.append(shot((FOREST+dummy(0.9,0.9),[]),Camera.look((0.2,1.3,-3.2),(0.3,0.6,1.0)),[((0,8,-4),(255,250,230),40.0)],'FOREST'))
    tiles.append(shot((CASTLE+castle_door(0.0)[0],castle_door(0.0)[1]),Camera.look((1.5,1.6,-7.0),(0,2.5,0)),[((0,5,-6),(220,210,255),40.0)],'CASTLE GATE'))
    tiles.append(shot((BOSSROOM+[q for x,y,z in TORCHES for q in flame(x,y,z,0.3)],[]),Camera.look((1.2,1.4,-4.5),(0,2.0,5.0)),[((x,y+0.4,z),(255,170,80),6.0) for x,y,z in TORCHES],'BOSS ROOM'))
    sh=Image.new('RGB',(3*242,3*322),(0,0,0))
    for i,im in enumerate(tiles): sh.paste(im,((i%3)*242,(i//3)*322))
    sh.resize((sh.width*2,sh.height*2),Image.NEAREST).save('rat_ref.png'); sys.exit()
# ======================= TIMELINE =======================
TTS=os.environ.get('TTS','/home/claude/tts')
SCRIPT=json.load(open(os.path.join(TTS,'v2','script.json')))
LTXT={k:txt for k,t,txt,d in SCRIPT}; LDUR={k:d for k,t,txt,d in SCRIPT}; NARR=[(k,t) for k,t,txt,d in SCRIPT]
DUR=60.0; N=int(DUR*FPS)
DAY=(120,180,235); DUSK=(230,140,90); NIGHT=(28,30,60); PURPLE=(56,40,90)
def lerpc3(a,b,u): return tuple(int(a[i]+(b[i]-a[i])*u) for i in range(3))
def nrm(v): v=np.array(v,float); return v/(np.linalg.norm(v)+1e-9)
def lerpd(a,b,u): return tuple(nrm(np.array(a)*(1-u)+np.array(b)*u))
def keys(T,K):
    """K: [(t, value_tuple)], smooth between"""
    if T<=K[0][0]: return K[0][1]
    for (t0,a),(t1,b) in zip(K,K[1:]):
        if t0<=T<=t1: u=sm((T-t0)/(t1-t0)) if t1>t0 else 1.0; return tuple(a[i]+(b[i]-a[i])*u for i in range(len(a)))
    return K[-1][1]
def to_rat_local(world,base,yaw,scale): return tuple(Ry(-yaw)@(np.array(world,float)-np.array(base,float))/scale)
def to_knight_local(world,base,yaw): return tuple(Ry(-yaw)@(np.array(world,float)-np.array(base,float)))
def look(pos,tgt): return Camera.look(pos,tgt)
SHAKES=[(0.35,6),(46.5,4),(47.0,3),(44.5,3)]
def shake_px(T):
    sx=sy=0.0
    for t0,a in SHAKES:
        if 0<=T-t0<0.3: k=1-(T-t0)/0.3; sx+=a*k*math.sin(97*T); sy+=a*k*math.cos(71*T)
    return (sx,sy)
TORCH_L=lambda on:[((x,y+0.45,z),(255,160,70),5.5*on) for (x,y,z) in TORCHES]
def torches(T,on):
    Q=[]
    for k,(x,y,z) in enumerate(TORCHES): Q+=box(x-0.06,x+0.06,y-0.4,y,z-0.06,z+0.06,(60,50,40))+flame(x,y,z,T,1.0,on[k],seed=k)
    return Q
BOSS_BASE=(0.0,0.0,5.0); BS=11.5
def boss_sword_rest(): return (0.13,0.2,-0.09),(0.15,1,-0.25)
# ---------------- S1: hook ----------------
def s1(T):
    over=((0.07,0.44,0.02),(0,0.6,1)); slam=((0.06,0.13,-0.2),(0,-0.55,-1)); rest=boss_sword_rest()
    if T<0.1: rp,sd=over
    elif T<0.35: u=motion.ease_in((T-0.1)/0.25); rp=lerp3(over[0],slam[0],u); sd=lerpd(over[1],slam[1],u)
    elif T<1.4: rp,sd=slam
    else: u=sm(seg01(T,1.4,2.6)); rp=lerp3(slam[0],rest[0],u); sd=lerpd(slam[1],rest[1],u)
    lean=0.22*win(T,0.15,1.6,0.2,0.6)
    boss=rat(BOSS_BASE,0.0,BS,T,armor=3,glow=1.0,rp=rp,lp=(-0.11,0.16,-0.08),sword=sd,sword_kind='king',lean=lean,bob=0.004*math.sin(T*2))
    kn=knight((1.55,0,2.4),math.pi+0.2,T,lean=-0.22*win(T,0.35,1.4,0.05,0.5),rhand=(-0.3,1.0,-0.25),lhand=lerp3((0.3,0.95,-0.05),(0.3,1.6,-0.15),win(T,0.35,1.6,0.1,0.4)),sword_dir=(0,0.2,-1))
    fx=[]
    if 0.35<=T<1.2:
        u=(T-0.35)/0.85; r_=0.4+3.2*u; c=(0.7,0.02,0.1); col=(int(255*(1-u)+60*u),int(190*(1-u)+30*u),int(80*(1-u)))
        for i in range(16):
            a0=2*math.pi*i/16; a1=2*math.pi*(i+1)/16
            fx.append(quad([(c[0]+r_*math.cos(a0),0.03,c[2]+r_*math.sin(a0)),(c[0]+r_*math.cos(a1),0.03,c[2]+r_*math.sin(a1)),(c[0]+(r_+0.25)*math.cos(a1),0.03,c[2]+(r_+0.25)*math.sin(a1)),(c[0]+(r_+0.25)*math.cos(a0),0.03,c[2]+(r_+0.25)*math.sin(a0))],col,emit=True))
        rr=random.Random(3)
        for k in range(14):
            a=rr.uniform(0,math.pi*2); d=u*rr.uniform(0.8,2.4); y=rr.uniform(0.2,1.4)*math.sin(math.pi*min(1,u*1.2)); q=0.1
            fx+=box(c[0]+math.cos(a)*d-q,c[0]+math.cos(a)*d+q,y,y+q*1.5,c[2]+math.sin(a)*d-q,c[2]+math.sin(a)*d+q,(150,140,130))
    pos=lerp3((1.5,0.85,-3.6),(1.3,1.0,-2.9),sm(seg01(T,0.8,4.6))); cam=look(pos,(0.3,2.9,3.8))
    return dict(env=[BOSS_F,BOSS_C,BOSS_R+torches(T,[1]*8)],chars=[boss,kn],fx=fx,cam=cam,lights=TORCH_L(1.0)+[((0,6,1),(255,90,70),3.0)],fog=(16,12,20),amb=0.16,fog_end=26)
# ---------------- S2: level 1, the steal ----------------
RAT_STUMP=(0.5,0.35,0.4); CHEESE_HUG=(0.5,0.56,0.25)
def knight_s2(T):
    if T<7.4: x=-2.4+(0.15+2.4)*seg01(T,5.0,7.4); yaw=-math.pi/2; wk=2*math.pi*1.6*(T-5.0); return (x,0,-0.3),yaw,wk,0.0
    if T<8.7:
        yaw=keys(T,[(7.4,(-math.pi/2,)),(7.8,(-2.67,)),(8.3,(-2.67,)),(8.7,(-math.pi/2,))])[0]
        lean=0.35*win(T,7.8,8.5,0.25,0.25); return (0.15,0,-0.3),yaw,0.0,lean
    x=0.15+(3.2-0.15)*seg01(T,8.7,11.4); return (x,0,-0.3),-math.pi/2,2*math.pi*1.6*(T-8.7),0.0
def s2(T):
    base,yaw,wk,lean=knight_s2(T)
    has=T>=8.3
    lh=None
    if 7.8<=T<8.3: lh=to_knight_local(lerp3((0.6,1.0,-0.6),CHEESE_HUG,sm(seg01(T,7.8,8.25))),base,yaw)
    if has: lh=(0.32,1.12,-0.28)
    kn=knight(base,yaw,T,walk=wk if wk else 0.0,lean=lean,lhand=lh,cheese=has,sword_dir=(0,-0.5,-1),rhand=(-0.3,0.92,-0.1))
    if T<8.3: kw=dict(happy=1.0,hug_cheese=True,bob=0.008*abs(math.sin(T*6)))
    else:
        sadk=sm(seg01(T,10.4,11.2)); hy=-0.7*sm(seg01(T,8.4,8.9))*(1-sm(seg01(T,10.6,11.2)))
        empty=(0.03,0.2,-0.13); down=(0.1,0.12,-0.06)
        rp=lerp3(empty,down,sadk); lp=lerp3((-0.03,0.2,-0.13),(-0.1,0.12,-0.06),sadk)
        kw=dict(eye=1.45-0.15*sadk,rp=rp,lp=lp,droop=sadk,sad=1.0 if T>=11.0 else 0.0,head_yaw=hy,head_pitch=0.25*sadk,tail_wag=1-0.8*sadk)
    r=rat(RAT_STUMP,0.0,1.0,T,**kw)
    xf=lerp3((-0.8,0,0),(0.4,0,0),sm(seg01(T,5.0,8.0)))[0]
    pos=(-0.2+xf*0.6,1.0,-2.5); tgt=(xf,0.62,0.3)
    z=sm(seg01(T,10.4,12.0)); pos=lerp3(pos,(0.55,0.62,-0.5),z); tgt=lerp3(tgt,(0.5,0.62,0.4),z)
    return dict(env=[FOREST_G,FOREST_P,FOREST_R],chars=[r,kn],fx=[],cam=look(pos,tgt),lights=[((-3,8,-5),(255,248,230),46.0)],fog=DAY,amb=0.36,fog_end=30,knight=(base,'LV 1') if T<11.0 else None)
# ---------------- S3: the sword ----------------
SWORD_SPOT=(-0.62,0.0,1.0)
def s3(T):
    sky=lerpc3(DAY,DUSK,seg01(T,14.0,16.0)) if T<16 else lerpc3(DUSK,PURPLE,seg01(T,16.0,20.5))
    kw=dict(); yaw=0.0; base=RAT_STUMP; sword=None
    if T<15.8:
        wipe=win(T,14.3,15.0,0.15,0.15)
        kw=dict(droop=1.0-0.6*sm(seg01(T,15.0,15.6)),sad=1.0 if T<14.7 else 0.0,eye=1.25,rp=lerp3((0.1,0.12,-0.06),(0.04,0.34,-0.12),wipe),lp=(-0.1,0.12,-0.06),
                head_pitch=0.25*(1-sm(seg01(T,15.0,15.4))),head_yaw=0.75*sm(seg01(T,15.2,15.6)),tail_wag=0.3)
    elif T<16.3:
        u=seg01(T,15.8,16.3); base=(0.5-0.25*u,0.35*(1-u)+0.25*math.sin(math.pi*u),0.4-0.2*u); yaw=2.33*u
        kw=dict(droop=0.4,eye=1.2,tail_wag=1.0)
    elif T<17.3:
        u=sm(seg01(T,16.3,17.3)); base=(0.25-0.65*u,0.0,0.2+0.55*u); yaw=2.33
        kw=dict(droop=0.4,eye=1.2,bob=0.015*abs(math.sin(T*14)),tail_wag=1.2)
    else:
        base=(-0.4,0.0,0.75); yaw=2.33
        hilt=to_rat_local((SWORD_SPOT[0],0.34,SWORD_SPOT[2]),base,yaw,1.0)
        if T<18.3:
            kw=dict(droop=0.3,eye=0.9,rp=hilt,lp=(hilt[0]-0.03,hilt[1]-0.03,hilt[2]),lean=-0.18-0.08*math.sin(T*22),tail_wag=2.0)
        else:
            u=sm(seg01(T,18.3,18.7)); rp=lerp3(hilt,(0.05,0.47,-0.04),u); sword=lerpd((0,-1,0.15),(0,1,0.12),u)
            kw=dict(droop=0.0,eye=0.8,rp=rp,lp=(-0.11,0.2,-0.1),sword=sword,tail_wag=1.5,bob=0.01*abs(math.sin(T*4)))
    r=rat(base,yaw,1.0,T,**kw)
    fx=[]
    if T<18.3:
        x,_,z=SWORD_SPOT; d=(0,-1,0.12)
        fx+=seg((x,0.42,z),(x,0.28,z),0.016,(80,50,30))+seg((x-0.05,0.28,z),(x+0.05,0.28,z),0.018,(120,90,60))+seg((x,0.28,z),(x,0.0,z+0.03),0.024,RUST,depth=0.012)
        if T>=15.4:
            g=0.6+0.4*math.sin(T*9); fx+=[quad([(x-0.06,0.45,z-0.02),(x+0.06,0.45,z-0.02),(x,0.45+0.15*g,z-0.02)],(255,250,200),emit=True)]
            fx+=box(x-0.05,x+0.05,0.0,3.5,z-0.05,z+0.05,(255,236,170),emit=True) if (int(T*10)%3 and T<17.0) else []
    if T<15.6: pos,tgt=(0.45,0.7,-0.75),(0.5,0.62,0.4)
    elif T<16.3: u=sm(seg01(T,15.6,16.3)); pos=lerp3((0.45,0.7,-0.75),(0.4,0.8,-1.3),u); tgt=lerp3((0.5,0.62,0.4),(-0.3,0.35,0.8),u)
    elif T<18.3: pos,tgt=(0.05,0.55,-0.15),(-0.42,0.28,0.78)
    else: u=sm(seg01(T,18.3,18.9)); pos=lerp3((0.3,0.65,-0.8),(0.05,0.12,0.05),u); tgt=lerp3((-0.35,0.3,0.8),(-0.45,0.48,0.82),u)
    sun=lerpc3((255,240,210),(255,150,90),seg01(T,14,18))
    return dict(env=[FOREST_G,FOREST_P,FOREST_R],chars=[r],fx=fx,cam=look(pos,tgt),lights=[((-6,4,-3),sun,40.0*(1-0.6*seg01(T,16,20.5)))],fog=sky,amb=0.33-0.12*seg01(T,16,20.5),fog_end=30)
# ---------------- S4: training montage ----------------
LVS=[(20.5,1,1.0,0),(22.0,2,1.25,0),(24.6,15,2.0,1),(27.2,47,3.4,2),(29.6,99,6.0,3)]
def lvstate(T):
    cur=LVS[0]; prev=LVS[0]
    for e in LVS:
        if T>=e[0]: prev,cur=cur,e
    u=seg01(T,cur[0],cur[0]+0.35); pop=math.sin(math.pi*u)*0.12*(u<1)
    sc=prev[2]+(cur[2]-prev[2])*sm(u)+pop*cur[2]
    return cur,sc
def s4(T):
    (t0,lv,scl,arm),sc=lvstate(T)
    ph=((T-20.5)/0.72)%1.0
    raised=((0.08,0.42,-0.02),(0,1,0.25)); strike=((0.06,0.17,-0.21),(0,-0.35,-1))
    u=sm(min(1,ph/0.45)) if ph<0.45 else 1-sm((ph-0.45)/0.55)
    rp=lerp3(raised[0],strike[0],u); sd=lerpd(raised[1],strike[1],u)
    if T>=30.0: v=sm(seg01(T,30.0,30.35)); rp=lerp3(raised[0],strike[0],v); sd=lerpd(raised[1],strike[1],v)
    base=(-0.4,0.0,0.9)
    r=rat(base,-math.pi/2,sc,T,armor=arm,rp=rp,lp=(-0.1,0.18,-0.1),sword=sd,sword_kind='rusty' if arm<3 else 'king',eye=0.85,lean=0.12*u)
    hit=1.0 if (0.4<ph<0.75 and T<29.9) else 0.0
    smashed=seg01(T,30.25,31.0)
    fx=dummy(0.42,0.9,1.0,hit,smashed,T)
    for (tl,lvv,_,_) in LVS[1:]:
        if tl<=T<tl+0.6:
            k=(T-tl)/0.6; h=2.0*sc
            for i in range(6):
                a=2*math.pi*i/6+T*4; rr_=0.35*sc*(0.6+k)
                fx+=box(base[0]+rr_*math.cos(a)-0.02*sc,base[0]+rr_*math.cos(a)+0.02*sc,h*k,h*k+0.05*sc,base[2]+rr_*math.sin(a)-0.02*sc,base[2]+rr_*math.sin(a)+0.02*sc,(255,236,120),emit=True)
    cyc=0.7*(0.5-0.5*math.cos(2*math.pi*(T-20.5)/2.6))
    sky=lerpc3((150,200,240),NIGHT,cyc)
    tgt=(-0.05,0.24*sc,0.9); pos=(tgt[0]+0.1,tgt[1]+0.1*sc+0.12,tgt[2]-(0.5+0.62*sc))
    return dict(env=[FOREST_G,FOREST_P,FOREST_R],chars=[r],fx=fx,cam=look(pos,tgt),lights=[((-4,8,-5),lerpc3((255,248,230),(120,140,220),cyc),46.0*(1-0.55*cyc))],fog=sky,amb=0.34-0.14*cyc,fog_end=30,lv=(lv,t0,base,sc))
# ---------------- S5: meanwhile, level 3 ----------------
def s5(T):
    if T<34.6: z=-7.5+(5.9)*sm(seg01(T,31.0,34.6))**0.9; wk=2*math.pi*1.6*(T-31.0) if T<34.5 else 0.0
    else: z=-1.6; wk=0.0
    if T>=36.6: z=-1.6+0.9*seg01(T,36.6,37.0); wk=2*math.pi*1.6*(T-36.6)
    base=(0.0,0.0,z); hp=-0.35*win(T,34.6,35.4,0.2,0.2)
    rh=(-0.3,0.95,-0.12); lh=None
    if 35.0<=T<35.5: rh=(-0.25,1.75,-0.1)
    push=win(T,35.5,36.6,0.25,0.3)
    if push>0: rh=lerp3(rh,(-0.25,1.25,-0.75),push); lh=lerp3((0.3,0.95,-0.05),(0.25,1.25,-0.75),push)
    kn=knight(base,math.pi,T,walk=wk,rhand=rh,lhand=lh,sword_dir=(0,1,0.2) if 35.0<=T<35.5 else (0,-0.5,-1),head_pitch=hp,lean=0.15*push)
    door,dd=castle_door(sm(seg01(T,35.6,36.6)))
    fl=flame(-1.9,2.9,-0.3,T)+flame(1.9,2.9,-0.3,T,seed=3)+box(-1.96,-1.84,2.4,2.9,-0.36,-0.24,(60,50,40))+box(1.84,1.96,2.4,2.9,-0.36,-0.24,(60,50,40))
    if T<34.6: pos=(1.1,1.9,z-2.8); tgt=(0.0,2.0,0.5)
    else: u=sm(seg01(T,34.6,35.2)); pos=lerp3((1.1,1.9,-4.4),(1.5,0.9,-4.6),u); tgt=lerp3((0.0,2.0,0.5),(0.0,2.4,0.0),u)
    return dict(env=[CASTLE+door,dd+fl],chars=[kn],fx=[],cam=look(pos,tgt),lights=[((0,6,-8),(170,170,230),30.0),((-1.9,3.2,-0.6),(255,160,70),4.0),((1.9,3.2,-0.6),(255,160,70),4.0)],fog=(34,26,60),amb=0.22,fog_end=30,knight=(base,'LV 3'))
# ---------------- S6: the reveal ----------------
def s6(T):
    if T<38.6: z=-5.0+3.2*sm(seg01(T,37.0,38.6)); wk=2*math.pi*1.4*(T-37.0)
    else: z=-1.8; wk=0.0
    kb=(0.6,0.0,z)
    on=[sm(seg01(T,37.8+0.5*(k//2),37.95+0.5*(k//2))) for k in range(8)]
    shock=win(T,44.0,45.5,0.15,0.4)
    kn=knight(kb,math.pi,T,walk=wk,lean=-0.3*shock,rhand=lerp3((-0.3,0.95,-0.12),(-0.35,1.7,-0.1),shock),lhand=lerp3((0.3,0.95,-0.05),(0.35,1.7,-0.1),shock),sword_dir=(0,0.3,-1))
    glow=1.0 if T>=39.6 else 0.0
    roar=win(T,44.4,45.5,0.2,0.3)
    rp,sd=boss_sword_rest(); rp=lerp3(rp,(0.14,0.36,-0.06),roar)
    boss=rat(BOSS_BASE,0.0,BS,T,armor=3,glow=glow,rp=rp,lp=lerp3((-0.11,0.16,-0.08),(-0.14,0.36,-0.06),roar),sword=sd,sword_kind='king',head_pitch=-0.25*roar,bob=0.004*math.sin(T*2))
    flash=None
    earW=ear_notch_world(BOSS_BASE,0.0,BS)
    if T<39.8: pos=lerp3((1.4,1.0,-7.0),(1.4,1.0,-5.2),seg01(T,37.0,39.8)); tgt=(0.0,2.3,4.0)
    elif T<41.0: pos=lerp3((1.4,1.0,-5.2),(1.3,1.1,-4.8),seg01(T,39.8,41.0)); tgt=(0.0,2.6,4.0)
    elif T<43.2: u=sm(seg01(T,41.0,42.6)); pos=lerp3((1.3,1.1,-4.8),(earW[0]-0.3,earW[1]+0.25,earW[2]-3.0),u); tgt=lerp3((0.0,2.6,4.0),earW,u)
    else: u=sm(seg01(T,44.0,44.4)); pos=lerp3((earW[0]-0.3,earW[1]+0.25,earW[2]-3.0),(2.6,1.2,-3.8),u if T>=44.0 else 0); tgt=lerp3(earW,(0.3,2.3,2.0),u if T>=44.0 else 0)
    if 43.2<=T<44.0: return dict(flashback=True,**s2_flash(T))
    return dict(env=[BOSS_F,BOSS_C,BOSS_R+torches(T,on)],chars=[boss,kn],fx=[],cam=look(pos,tgt),lights=TORCH_L(1.0)[:0]+[((x,y+0.45,z_),(255,160,70),5.5*on[k]) for k,(x,y,z_) in enumerate(TORCHES)]+[((0,4.3,3.8),(255,60,50),2.5*glow)],fog=(10,8,14),amb=0.05+0.12*min(1,sum(on)/8),fog_end=26,boss_bar=T>=40.0,knight=(kb,'LV 3') if T>=44.0 else None,bang=T>=44.0 and T<44.9,ring=earW if 41.9<=T<43.2 else None)
def s2_flash(T):
    r=rat(RAT_STUMP,0.0,1.0,T,happy=1.0,hug_cheese=True,bob=0.008*abs(math.sin(T*6)))
    earW=(RAT_STUMP[0]-0.075,RAT_STUMP[1]+0.43,RAT_STUMP[2]-0.01)
    nw=ear_notch_world(RAT_STUMP,0.0,1.0); u=seg01(T,43.2,44.0); pos=lerp3((nw[0]-0.05,nw[1]+0.04,nw[2]-0.42),(nw[0]-0.04,nw[1]+0.03,nw[2]-0.36),u); tgt=(nw[0]+0.07,nw[1]-0.08,nw[2])
    return dict(ring=nw,env=[FOREST_G,FOREST_P,FOREST_R],chars=[r],fx=[],cam=look(pos,tgt),lights=[((-3,8,-5),(255,248,230),46.0)],fog=DAY,amb=0.36,fog_end=30)
# ---------------- S7 + S8: fight, inventory, cheese ----------------
def knight_fight(T):
    if T<45.5: return (0.6,0,-1.8),0.0,0.0
    if T<46.2: u=seg01(T,45.5,46.2); return (0.6-0.2*u,0,-1.8+3.2*u),2*math.pi*2.4*(T-45.5),0.0
    if T<46.5: return (0.4,0,1.4),0.0,0.0
    if T<47.0: u=seg01(T,46.5,47.0); return (0.4+0.1*u,0.6*math.sin(math.pi*u),1.4-2.6*u),0.0,sm(u)
    return (0.5,0,-1.2),0.0,1.0
def s78(T):
    kb,wk,sit=knight_fight(T)
    broken=T>=46.5
    rh=(-0.3,0.95,-0.12); sd=(0,0.3,-1); lh=None; hp=0.0; hy=0.0; cheese=False; cg=0.0
    if 45.5<=T<46.2: rh=(-0.25,1.9,0.0); sd=(0,1,0.3)
    elif 46.2<=T<46.5: u=sm(seg01(T,46.2,46.45)); rh=lerp3((-0.25,1.9,0.0),(-0.2,1.2,-0.55),u); sd=lerpd((0,1,0.3),(0,-0.3,-1),u)
    elif T>=47.0 and T<49.6: rh=(-0.3,0.75,-0.45); hp=0.2
    if 49.6<=T<52.4: rh=(-0.15,0.7,-0.05); lh=(0.15,0.7,-0.05)
    if T>=52.4:
        up=win(T,52.4,55.0,0.3,0.4); cheese=T<54.6; cg=1.0 if T<54.6 else 0.0
        rh=lerp3((-0.3,0.75,-0.3),(-0.08,1.35,-0.45),up); lh=lerp3((0.3,0.75,-0.3),(0.08,1.35,-0.45),up)
    if T>=57.4: hy=-0.9*sm(seg01(T,57.4,57.8))
    kn=knight(kb,math.pi,T,walk=wk,sit=sit,rhand=rh,lhand=lh,sword=not broken,sword_dir=sd,cheese=cheese,cheese_glow=cg,head_pitch=hp,head_yaw=hy)
    # boss
    rest=boss_sword_rest(); over=((0.07,0.44,0.02),(0,0.6,1))
    rp,sd2=rest; lp=(-0.11,0.16,-0.08); glow=1.0; eye=1.0; happy=0.0; lean=0.0; hpit=0.0; byaw=0.0; bbase=list(BOSS_BASE); held=None
    bbase[2]=BOSS_BASE[2]-2.0*sm(seg01(T,53.4,54.0))+2.6*sm(seg01(T,55.3,56.8)) if T>=53.4 else BOSS_BASE[2]
    if 46.25<=T<46.65:
        u=sm(seg01(T,46.25,46.6)); rp=lerp3((0.22,0.26,0.05),(-0.05,0.15,-0.24),u); sd2=lerpd((1,0.3,0.3),(-0.6,-0.1,-1),u)
    elif 46.65<=T<48.0: u=sm(seg01(T,46.65,47.4)); rp=lerp3((-0.05,0.15,-0.24),rest[0],u); sd2=lerpd((-0.6,-0.1,-1),rest[1],u)
    elif 48.0<=T<53.4: u=sm(seg01(T,48.0,49.6)); rp=lerp3(rest[0],over[0],u); sd2=lerpd(rest[1],over[1],u)
    elif T>=53.4: u=sm(seg01(T,53.4,54.0)); rp=lerp3(over[0],(0.16,0.12,-0.05),u); sd2=lerpd(over[1],(0.3,-1,-0.2),u)
    lh_=lh if lh is not None else (0.3,0.95,-0.05)
    kRb=Ry(math.pi); handsW=np.array(kb)+kRb@(np.array(lerp3(rh,lh_,0.5))+np.array([0,-0.5*sit+0.07,0]))
    if T>=52.6:
        glow=1.0-sm(seg01(T,52.8,53.0)); eye=1.0+0.5*sm(seg01(T,52.8,53.0)); hpit=-0.3*win(T,52.6,54.6,0.3,0.4)+0.03*math.sin(T*40)*win(T,52.9,53.5,0.05,0.05)
    if T>=54.0:
        lean=0.35*win(T,54.0,55.2,0.4,0.5)
        reach=sm(seg01(T,54.0,54.6))*(1-sm(seg01(T,54.7,55.2)))
        lp=lerp3(lp,to_rat_local(tuple(handsW),tuple(bbase),0.0,BS),reach)
        if T>=54.6: held='hug'
    if T>=55.0: happy=1.0; glow=0.0
    bbase[2]=BOSS_BASE[2]-2.0*sm(seg01(T,53.4,54.0))+2.6*sm(seg01(T,55.3,56.8)) if T>=53.4 else BOSS_BASE[2]
    hug=T>=55.0
    boss=rat(tuple(bbase),byaw,BS,T,armor=3,glow=glow if happy<0.5 else 0.0,eye=eye,happy=happy,rp=rp if not hug else (0.03,0.2,-0.13),lp=lp if not hug else (-0.03,0.2,-0.13),
             sword=sd2 if T<53.9 else None,sword_kind='king',lean=lean,head_pitch=hpit,bob=(0.02*abs(math.sin(T*7)) if hug else 0.004*math.sin(T*2)),tail_wag=3.0 if hug else 1.0)
    fx=[]
    dropped=[]
    if T>=53.9:
        dropped=seg((-1.9,0.12,3.6),(-1.9,0.12,3.6-5.0),0.5,(150,156,170),depth=0.18)+seg((-2.4,0.15,3.6),(-1.4,0.15,3.6),0.25,GOLD)+seg((-1.9,0.15,3.6),(-1.9,0.15,4.4),0.2,(80,50,30))
    if 54.6<=T<55.0:
        pw=np.array(bbase)+np.array(lp)*BS; fx+=cheese_at(tuple(pw),0.0,2.4)
    if hug:
        cw=np.array(bbase)+np.array([0,0.19*BS+0.02*abs(math.sin(T*7))*BS,-0.19*BS]); fx+=cheese_at(tuple(cw),0.3,6.0)
        rr=random.Random(4)
        for k in range(8):
            ph=((T-55.0)*0.6+k/8)%1.0; x=bbase[0]+rr.uniform(-1.4,1.4); y=3.6+ph*2.6; zz=bbase[2]-1.2
            q=0.14*(1-ph)+0.05; fx+=box(x-q,x,y,y+q,zz,zz+0.02,(255,110,150),emit=True)+box(x,x+q,y,y+q,zz,zz+0.02,(255,110,150),emit=True)+box(x-q*0.5,x+q*0.5,y-q*0.8,y+q*0.2,zz,zz+0.02,(255,110,150),emit=True)
    if 46.5<=T<47.8:
        u=(T-46.5)/1.3; rr=random.Random(11); c=np.array([0.35,1.5,1.2])
        for k in range(12):
            v=np.array([rr.uniform(-2,2),rr.uniform(0.5,3.0),rr.uniform(-2.5,0.5)]); p=c+v*u+np.array([0,-4.9*u*u,0]); p[1]=max(0.02,p[1]); q=0.05
            fx+=box(p[0]-q,p[0]+q,p[1]-q,p[1]+q,p[2]-q,p[2]+q,(225,230,240),emit=True)
        if u<0.15: fx+=box(0.25,0.45,1.4,1.6,1.1,1.3,(255,255,230),emit=True)
    if broken and T<52.4: fx+=box(kb[0]-0.03,kb[0]+0.03,0.6,0.75,kb[2]+0.3,kb[2]+0.36,(225,230,240))
    # cameras
    if T<46.5: pos,tgt=(3.3,1.5,-2.2),(0.3,1.8,1.6)
    elif T<48.0: pos,tgt=(3.3,1.5,-2.2),(0.3,1.6,1.2)
    elif T<52.4: u=sm(seg01(T,48.0,49.4)); pos=lerp3((3.3,1.5,-2.2),(1.25,0.55,-3.7),u); tgt=lerp3((0.3,1.6,1.2),(0.0,3.3,3.5),u)
    elif T<53.3: pos,tgt=(2.6,1.4,-4.2),(0.2,2.2,2.0)
    elif T<55.0: pos,tgt=(5.4,2.4,2.25),(0.2,2.2,1.25)
    elif T<57.0: u=sm(seg01(T,55.0,55.6)); pos=lerp3((5.4,2.4,2.25),(2.4,3.2,0.0),u); tgt=lerp3((0.3,2.0,2.2),(0.0,3.0,5.0),u)
    else: u=sm(seg01(T,57.0,57.8)); pos=lerp3((2.4,3.2,0.0),(2.2,1.5,-4.8),u); tgt=lerp3((0.0,3.0,5.0),(0.3,1.9,3.2),u)
    music_on=T<52.4
    return dict(env=[BOSS_F,BOSS_C,dropped,BOSS_R+torches(T,[1]*8)],chars=[boss,kn],fx=fx,cam=look(pos,tgt),lights=TORCH_L(1.0)+[((0,4.3,3.8),(255,60,50),2.5*glow)],fog=(16,12,20),amb=0.17,fog_end=26,
                boss_bar=True,knight=(kb,'LV 3'),hp=(1 if T>=46.6 else 30),menu=49.9<=T<52.4,broken_toast=46.6<=T<48.2,boss_hp=1.0-sm(seg01(T,56.9,57.25)))
SCENES=[(0.0,5.0,s1),(5.0,14.0,s2),(14.0,20.5,s3),(20.5,31.0,s4),(31.0,37.0,s5),(37.0,45.5,s6),(45.5,60.01,s78)]
def scene_at(T):
    for a,b,f in SCENES:
        if a<=T<b: return f(T)
    return s78(T)
# ---------------- render + HUD ----------------
R=Renderer(W,H,fog=(0,0,0))
def render(T):
    sc=scene_at(T); R.fog=sc['fog']; cam=sc['cam']; cp=np.array(cam[:3])
    chars=sorted(sc['chars'],key=lambda cd:-np.linalg.norm(np.mean([q['c'] for q in cd[0]],axis=0)-cp))
    layers=list(sc['env'])
    for q,d in chars:
        dd=[x for x in d if 'hc' not in x or np.linalg.norm(x['c']-cp)<np.linalg.norm(x['hc']-cp)]
        layers+=[q,dd]
    layers.append(sc['fx'])
    img,vi=R.render(cam,layers,sc['lights'],fov=58,fog_start=10,fog_end=sc.get('fog_end',26),ambient=sc['amb'],shake=shake_px(T))
    return post.ps1(img),vi,sc
YEL=(255,214,40); WHT=(255,255,255); RED=(255,70,60); GRN=(90,230,90); PANEL=(16,20,60)
def panel(d,x0,y0,x1,y1,fill=PANEL,edge=(230,230,240)): d.rectangle([x0,y0,x1,y1],fill=fill,outline=edge); d.rectangle([x0+2,y0+2,x1-2,y1-2],outline=(90,100,160))
def ctext(d,s_,y,col,sc_=1): otext(d,s_,(W-font.width(s_,sc_))//2,y,col,sc_)
def wrap(txt,n=27):
    out=[]; cur=''
    for w_ in txt.split():
        if len(cur)+len(w_)+(1 if cur else 0)>n: out.append(cur); cur=w_
        else: cur=(cur+' '+w_).strip()
    if cur: out.append(cur)
    return out
HIL={'THIS','CHEESE','CHEESE.','EAR.','BIGGER.','TRAINED.','THREE.','STARVING,','BOSS.','TINY.','SWORD..','REASON.','HIM.','ATTACKED.','SWING.','ITEM','HUGGED','SURVIVE.','HUGE','ZERO'}
def subtitle(d,T):
    for key,t0 in NARR:
        if t0<=T<t0+LDUR[key]+0.3:
            lines=wrap(LTXT[key].upper().replace('...','..'))
            y=246-10*(len(lines)-1)
            for ln in lines:
                xw=font.width(ln); x=(W-xw)//2; d.rectangle([x-3,y-2,x+xw+2,y+8],fill=(0,0,0))
                cx=x
                for wd in ln.split(' '):
                    otext(d,wd,cx,y,YEL if wd in HIL else WHT,1); cx+=font.width(wd)+6
                y+=11
            return
def draw_ring(d,vi,p,T):
    q=R.project(p,vi)
    if not q: return
    r_=10+2*math.sin(T*10)
    for k in range(2): d.ellipse([q[0]-r_-k,q[1]-r_-k,q[0]+r_+k,q[1]+r_+k],outline=(255,214,40))
def hud(img,vi,sc,T):
    d=ImageDraw.Draw(img)
    def proj(p): return R.project(p,vi)
    if sc.get('ring') is not None and vi is not None: draw_ring(d,vi,sc['ring'],T)
    if sc.get('boss_bar') or (T<5.0 and T>=0.5):
        u=sm(seg01(T,0.5,0.8)) if T<5.0 else sm(seg01(T,40.0,40.3)) if T<45.5 else 1.0
        y=int(-20+28*u); hpv=sc.get('boss_hp',1.0)
        otext(d,'RAT KING',8,y,WHT,1); otext(d,'LV 99',W-8-font.width('LV 99'),y,YEL,1)
        d.rectangle([7,y+10,W-8,y+16],fill=(0,0,0)); d.rectangle([8,y+11,W-9,y+15],fill=(70,10,10))
        if hpv>0: d.rectangle([8,y+11,8+int((W-17)*hpv),y+15],fill=(220,40,40))
    if 5.05<=T<6.6:
        a=win(T,5.05,6.6,0.15,0.3); y=int(56-10*(1-a)); ctext(d,'LEVEL 1',y,YEL,3)
    k=sc.get('knight')
    if k and vi is not None:
        q=proj((k[0][0],2.15+k[0][1],k[0][2]))
        if q: otext(d,k[1],int(q[0])-font.width(k[1])//2,int(q[1])-4,GRN,1)
    if 8.35<=T<9.9:
        u=sm(seg01(T,8.35,8.5)); y=int(-14+40*u); panel(d,44,y,136,y+16); otext(d,'+1 CHEESE',(W-font.width('+1 CHEESE'))//2,y+5,YEL,1)
    if 18.6<=T<20.3:
        u=sm(seg01(T,18.6,18.75)); y=int(-14+40*u); panel(d,18,y,162,y+16); otext(d,'OBTAINED: RUSTY SWORD',(W-font.width('OBTAINED: RUSTY SWORD'))//2,y+5,YEL,1)
    if 'lv' in sc:
        lv,t0,base,scl=sc['lv']; panel(d,6,8,72,24); otext(d,'RAT LV %d'%lv,12,13,WHT,1)
        if t0>20.6 and t0<=T<t0+1.2:
            u=sm(seg01(T,t0,t0+0.15)); ctext(d,'LEVEL UP!',int(56-8*(1-u)),YEL,2); ctext(d,'LV %d'%lv,80,WHT,2)
    if sc.get('bang') and vi is not None:
        kb=sc['knight'][0]; q=proj((kb[0],2.35,kb[2]))
        if q: otext(d,'!',int(q[0])-3,int(q[1])-14,YEL,3)
    if 'hp' in sc and T<57.0:
        hpv=sc['hp']; panel(d,6,280,104,300); otext(d,'KNIGHT',11,284,WHT,1)
        col=RED if (hpv<5 and int(T*6)%2==0) else WHT; otext(d,'HP %d/30'%hpv,11,292,col,1) if False else font.text(d,'HP %d/30'%hpv,52,284,col,1,None)
    if sc.get('broken_toast'):
        u=sm(seg01(T,46.6,46.75)); y=int(-14+44*u); panel(d,34,y,146,y+16,edge=RED); otext(d,'WEAPON BROKEN',(W-font.width('WEAPON BROKEN'))//2,y+5,RED,1)
    if sc.get('menu'):
        img.paste(Image.blend(img,Image.new('RGB',img.size,(0,0,0)),0.45)); d=ImageDraw.Draw(img)
        panel(d,22,150,158,212); otext(d,'ITEMS',30,155,YEL,1)
        sel=0 if T<51.0 else 1
        items=[('POTION','X0'),('STOLEN CHEESE','X1')]
        for i,(nm,ct) in enumerate(items):
            y=172+i*14; on=i==sel; col=(YEL if on else (150,150,170)) if not (i==0) else ((120,120,130) if not on else (200,120,120))
            if on and i==1 and T>=51.6 and int(T*10)%2==0: col=WHT
            if on: d.polygon([(28,y),(32,y+3),(28,y+6)],fill=col)
            otext(d,nm,36,y,col,1); otext(d,ct,150-font.width(ct),y,col,1)
        if 50.6<=T<51.0: otext(d,'EMPTY',(W-font.width('EMPTY'))//2,218,RED,1)
    if T>=57.2:
        rows=[('BOSS DEFEATED',57.2,YEL,2),('REWARD: 0 XP',57.9,WHT,1),('CHEESE RETURNED',58.6,GRN,1)]
        panel(d,4,40,176,104)
        for i,(txt,t0,col,sc_) in enumerate(rows):
            if T>=t0:
                y=48 if i==0 else (72 if i==1 else 86); ctext(d,txt,y,col,sc_)
                if i==2: x=(W+font.width(txt))//2+4; d.line([x,y+4,x+3,y+7,x+9,y],fill=GRN,width=2)
    subtitle(d,T)
    return img
def sepia(img):
    a=np.asarray(img).astype(np.float32); g=a@np.array([0.3,0.59,0.11]); o=np.stack([g*1.07+20,g*0.9+8,g*0.7],-1)
    yy,xx=np.mgrid[0:H,0:W]; v=np.clip(1-0.55*(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2),0.5,1)[...,None]
    return Image.fromarray(np.clip(o*v,0,255).astype(np.uint8))
def frame(T):
    img,vi,sc=render(T)
    if sc.get('flashback'): img=sepia(img); d=ImageDraw.Draw(img); draw_ring(d,vi,sc['ring'],T); otext(d,'LEVEL 1',W-6-font.width('LEVEL 1'),6,(255,230,190),1); subtitle(d,T); return img
    if 4.5<=T<5.0: img=Image.blend(img,Image.new('RGB',img.size,(0,0,0)),sm(seg01(T,4.5,4.95)))
    if abs(T-0.35)<1.5/FPS or abs(T-46.5)<1.5/FPS: img=img.point(lambda v:min(255,v+60))
    return hud(img,vi,sc,T)
TEST=os.environ.get('TEST')
if TEST:
    ims=[frame(float(x)) for x in TEST.split(',')]; sh=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): sh.paste(im,(i*182,0))
    sh.resize((sh.width*2,640),Image.NEAREST).save('test.png'); sys.exit()
# ======================= SOUND =======================
def build_audio(path):
    s=Sound(DUR,loop=False,seed=8); sr=s.sr
    M=np.zeros(s.n)                                                   # music bus (mono), ducked under narration
    def note(buf,t0,m,d,v,wave='sq',duty=0.5,dec=3.0,att=0.005):
        f=440*2**((m-69)/12); tt=s.T(d); ph=(f*tt)%1
        if wave=='sq': x=np.where(ph<duty,1.0,-1.0)
        elif wave=='tri': x=4*np.abs(ph-0.5)-1
        else: x=np.sin(2*np.pi*f*tt)
        env=np.minimum(1,tt/att)*np.exp(-tt*dec)
        i=int(t0*sr); j=min(s.n,i+len(tt)); buf[i:j]+=(x*env*v)[:j-i]
    def kick(buf,t0,v=0.3): tt=s.T(0.14); i=int(t0*sr); j=min(s.n,i+len(tt)); buf[i:j]+=(np.sin(2*np.pi*(110-60*tt/0.14)*tt)*np.exp(-tt*25)*v)[:j-i]
    def snare(buf,t0,v=0.12,seed=0): x=s.filt_short(s.noise(0.12,seed),lo=1200,hi=7000)*np.exp(-s.T(0.12)*30); i=int(t0*sr); j=min(s.n,i+len(x)); buf[i:j]+=(x*v)[:j-i]
    def seq(t0,t1,step,bass,lead=None,v=1.0,drums=True,bw='tri',lw='sq',duty=0.25,ldec=6):
        k=0
        while t0+k*step<t1-1e-6:
            tt=t0+k*step
            if bass[k%len(bass)] is not None: note(M,tt,bass[k%len(bass)],step*0.95,0.10*v,bw,dec=2)
            if lead and lead[k%len(lead)] is not None: note(M,tt,lead[k%len(lead)],step*1.4,0.045*v,lw,duty=duty,dec=ldec)
            if drums:
                if k%4==0: kick(M,tt,0.22*v)
                if k%4==2: snare(M,tt,0.08*v,k)
            k+=1
    # cues
    seq(0.0,4.6,0.18,[38,38,41,38,43,41,40,37],[62,None,65,None,62,None,61,None],v=1.0)          # boss theme (hook)
    for m in (50,53,57): note(M,0.35,m,1.2,0.05,'sq',duty=0.5,dec=1.5)
    seq(5.0,8.3,0.2,[48,55,52,55],[72,76,79,76,74,77,81,77],v=0.8,drums=False,lw='tri',ldec=3)       # happy forest
    note(M,8.32,64,0.25,0.06,'sq',dec=10); note(M,8.45,60,0.35,0.06,'sq',dec=8)                     # the steal
    for k,m in enumerate([69,None,67,None,65,None,64,None,62,None,60,None,59,None,57,None,57,None,60,None,64,None,62,None]):
        if m: note(M,10.0+k*0.4,m,0.8,0.04,'tri',dec=1.5)
    for k in range(10): note(M,10.0+k*0.8,45 if k%2==0 else 41,0.8,0.05,'tri',dec=1)                  # sad
    seq(15.6,18.3,0.15,[45,45,48,50,45,45,52,50],None,v=0.7,drums=True)                               # resolve
    for k,m in enumerate([69,71,72,74,76]): note(M,15.6+k*0.5,m,0.4,0.03,'sq',duty=0.25,dec=4)
    for k,m in enumerate([67,72,76,79,84]): note(M,18.35+k*0.08,m,0.3,0.05,'sq',duty=0.25,dec=6)    # item get
    seq(20.5,31.0,0.13,[45,45,57,45,48,48,60,48,43,43,55,43,47,47,59,50],[69,72,76,72,69,72,76,79,67,71,74,71,71,74,78,74],v=0.9)   # training
    for k in range(int(13.5/0.6)): note(M,31.0+k*0.6,38 if k%4 else 37,0.6,0.07,'tri',dec=0.8)      # ominous castle + reveal
    for k in range(9): note(M,31.0+k*1.5,74 if k%2 else 73,1.2,0.02,'sin',dec=2)
    seq(44.5,52.4,0.14,[38,38,50,38,41,41,53,41,36,36,48,36,37,37,49,37],[62,65,69,65,62,65,70,65,60,64,67,64,61,64,69,64],v=1.1)   # boss battle
    M[int(52.4*sr):int(57.0*sr)]=0                                                                      # cut dead at the cheese
    for k,m in enumerate([72,72,72,76,79,77,79,84]): note(M,57.0+k*(0.12 if k<3 else 0.16),m,0.4,0.06,'sq',duty=0.25,dec=4)  # victory
    note(M,57.0,48,1.6,0.08,'tri',dec=1)
    # narration
    Nb=np.zeros(s.n); duck=np.ones(s.n)
    for key,t0 in NARR:
        w=wave.open(os.path.join(TTS,key+'.wav')) if False else None
        import soundfile as _sf
        a,ar=_sf.read(os.path.join(TTS,'v2',key+'.wav')); a=a if a.ndim==1 else a.mean(1)
        a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a)
        i=int(t0*sr); j=min(s.n,i+len(a)); Nb[i:j]+=a[:j-i]*0.95
        i0=max(0,i-int(0.1*sr)); j1=min(s.n,j+int(0.2*sr)); duck[i0:j1]=0.4
    duck=np.convolve(duck,np.ones(2400)/2400,'same')
    s.L+=M*duck; s.R+=M*duck
    # sfx
    def nb(t0,d,lo,hi,v,seed,shape=2,pan=0.0): s.place(s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v,pan)
    def chirp(t0,d,f0,f1,v,pan=0.0): tt=s.T(d); s.place(np.sin(2*np.pi*np.cumsum(f0+(f1-f0)*tt/d)/sr)*np.sin(np.pi*tt/d),t0,v,pan)
    def squeak(t0,v=0.06,f=2200): tt=s.T(0.16); s.place(np.sin(2*np.pi*np.cumsum(f+600*np.sin(np.pi*tt/0.16))/sr)*np.sin(np.pi*tt/0.16)**0.7,t0,v)
    def clang(t0,v=0.25): tt=s.T(0.6); s.place(sum(np.sin(2*np.pi*f*tt)*np.exp(-tt*dk) for f,dk in ((420,7),(690,9),(1130,12),(1710,15)))*0.4,t0,v)
    def step(t0,v=0.08,seed=0): s.place(s.filt_short(s.noise(0.05,seed),lo=150,hi=1500)*np.exp(-s.T(0.05)*60),t0,v)
    nb(0.08,0.3,300,3000,0.2,1); s.thud(0.35,f=45,v=0.9); clang(0.35,0.3); nb(0.36,1.2,60,600,0.35,2,shape=1)   # SLAM
    for k in range(9): step(5.0+k*0.31,0.06,k)
    squeak(6.2,0.03,2600); chirp(8.3,0.12,900,1600,0.06); squeak(8.6,0.05,2000)
    for k in range(7): step(8.7+k*0.31,0.06,20+k)
    squeak(11.0,0.05,1600); squeak(12.6,0.04,1400)
    nb(14.3,0.4,800,3000,0.04,3)                                                                         # sniff/wipe
    for k in range(6): chirp(15.4+k*0.35,0.12,2400,3200,0.012)                                          # sword glint
    nb(15.8,0.15,300,2000,0.08,4); s.thud(16.3,f=120,v=0.08)
    for k in range(5): step(16.35+k*0.2,0.04,30+k)
    for k in range(5): squeak(17.4+k*0.2,0.03,1800+k*80)                                                 # straining
    chirp(18.3,0.25,600,2800,0.07); clang(18.35,0.12)                                                    # sword out
    for k in range(int(9.4/0.72)):                                                                       # training swings + hits
        t0=20.5+k*0.72; nb(t0+0.2,0.18,500,4000,0.12,50+k)
        if t0+0.33<29.9: s.thud(t0+0.33,f=150,v=0.12)
    for tl,lv,_,_ in LVS[1:]:
        for k,m in enumerate([72,76,79,84,88]): note(s.L,tl+k*0.06,m,0.25,0.035,'sq',duty=0.25,dec=8); note(s.R,tl+k*0.06,m,0.25,0.035,'sq',duty=0.25,dec=8)
        nb(tl,0.6,1500,8000,0.05,60+lv)
    s.thud(30.3,f=70,v=0.4); nb(30.3,0.6,200,3000,0.25,70)                                               # dummy smashed
    for k in range(11): step(31.0+k*0.31,0.07,80+k)
    tt=s.T(1.2); s.place(np.sin(2*np.pi*np.cumsum(110+40*np.sin(2*np.pi*1.7*tt)+20*np.sin(2*np.pi*13*tt))/sr)*np.sin(np.pi*tt/1.2)*0.6,35.6,0.09)  # door creak
    nb(35.6,1.2,40,300,0.25,90,shape=1)
    for k in range(5): step(37.0+k*0.36,0.07,100+k)
    for k in range(4): nb(37.8+0.5*k,0.35,200,2500,0.16,110+k); s.thud(37.8+0.5*k,f=90,v=0.1)          # torches
    note(s.L,39.6,38,1.5,0.08,'tri',dec=1); note(s.R,39.6,38,1.5,0.08,'tri',dec=1)                       # eyes
    for k in range(4): s.thud(41.0+k*0.55,f=55,v=0.18)                                                     # heartbeat
    nb(43.2,0.25,800,6000,0.1,120); nb(44.0,0.25,800,6000,0.1,121)                                        # flashback whooshes
    chirp(44.05,0.15,1200,1800,0.06)
    tt=s.T(1.3); roar=s.filt_short(s.noise(1.3,130),lo=80,hi=900)*np.sin(np.pi*tt/1.3)**0.6+np.sin(2*np.pi*np.cumsum(90-30*tt/1.3)/sr)*np.sin(np.pi*tt/1.3)*0.5; s.place(roar,44.4,0.3)
    for k in range(5): step(45.5+k*0.14,0.08,140+k)
    nb(46.2,0.25,500,5000,0.2,150); nb(46.3,0.3,300,3000,0.25,151)
    clang(46.5,0.35)
    for k in range(10): s.place(np.sin(2*np.pi*(2000+300*k)*s.T(0.08))*np.exp(-s.T(0.08)*40),46.52+k*0.03,0.03)  # shatter
    s.thud(47.0,f=80,v=0.3)
    nb(48.0,1.6,100,800,0.06,160,shape=1)
    for k,(t0,m) in enumerate([(49.95,79),(50.3,76),(50.65,60),(51.0,79),(51.6,84)]): note(s.L,t0,m,0.1,0.04,'sq',duty=0.25,dec=20); note(s.R,t0,m,0.1,0.04,'sq',duty=0.25,dec=20)
    note(s.L,50.65,40,0.3,0.05,'sq',dec=5); note(s.R,50.65,40,0.3,0.05,'sq',dec=5)                       # "empty" buzz
    for k in range(6): chirp(52.4+k*0.08,0.1,3000,4200,0.02)                                                # cheese sparkle
    for k in range(3): nb(52.9+k*0.18,0.08,2000,6000,0.05,170+k)                                          # sniff sniff
    squeak(53.25,0.08,2500)                                                                                # the tiny squeak
    clang(54.0,0.25); s.thud(54.0,f=70,v=0.2)                                                              # sword dropped
    for k in range(10): nb(55.4+k*0.27,0.06,600,3000,0.05,180+k)                                          # munch
    squeak(56.2,0.05,2800); squeak(56.9,0.05,3000)
    s.L+=Nb; s.R+=Nb
    s.reverb(0.1,length=0.8,decay=5)
    return s.save(path,peak=0.9)
if __name__=='__main__' and not os.environ.get('NOAUDIO_RENDER'):
    PART=os.environ.get('PART')
    if PART=='audio':
        print(build_audio(os.path.join(OUT,'rat_king.wav'))); sys.exit()
    if PART:
        a,b=map(int,PART.split(':'))
        import subprocess
        p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'rk_{a:05d}.mp4')],stdin=subprocess.PIPE)
        vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.93,vignette=0.3,grain=1.8,band_period=1e9)
        for f in range(a,min(b,N)): p.stdin.write(vhs(post.upscale(frame(f/FPS),S),f,f/FPS).tobytes())
        p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
