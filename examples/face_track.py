"""AUTO-TRACK - "She hid her boyfriend from 10,000 viewers". PS1 short told through a face-tracking stream camera. 9:16, ~34 s.
Run: python examples/face_track.py   (PART=a:b renders frames, PART=audio builds the soundtrack)"""
import os, sys, math, json, random
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','tts'))   # Kokoro models + generated voice lines live here
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, box, quad, tiled_plane, transform, rx, ry, rz, refresh
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

def keys(T,K):
    if T<=K[0][0]: return K[0][1]
    for (t0,a),(t1,b) in zip(K,K[1:]):
        if t0<=T<=t1: u=sm((T-t0)/(t1-t0)) if t1>t0 else 1.0; return tuple(a[i]+(b[i]-a[i])*u for i in range(len(a)))
    return K[-1][1]
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


# ---------------- palette ----------------
SKIN=(236,200,176); HAIR=(26,22,26); PINK=(240,156,190); PINK_D=(210,120,160); JEANS=(64,86,150); WHITE=(240,240,240)
GRAY=(128,132,142); GRAY_D=(104,108,118); BLACK=(34,34,42); BHAIR=(54,38,30)
# ---------------- characters (face details go to a separate decal list, culled when facing away) ----------------
def tag(D,c):
    for q in D: q['hc']=np.array(c,float)
    return D
def limb(sh,hd,out,col,hand=SKIN,w=0.09):
    el=elbow(sh,hd,out,0.56); return seg(sh,el,w,col)+seg(el,hd,w*0.9,col)+obox(np.array(hd),(0.042,0.042,0.042),np.eye(3),hand)
def girl(base,yaw,t,sit=0.0,walk=0.0,rh=None,lh=None,hy=0.0,hp=0.0,eye=1.0,mouth=0.0,smile=0.0,panic=0.0,lean=0.0,phone=False,blush=0.0):
    b=np.array(base,float); Rb=Ry(yaw)
    def W(p): return tuple(b+Rb@np.array(p,float))
    hip=0.82-0.34*sit
    def WL(p):
        p=np.array(p,float)+np.array([0,hip-0.82,0]); piv=np.array([0,hip,0]); return W(piv+Rx(lean)@(p-piv))
    Q=[]; D=[]; sw=0.45*math.sin(walk)
    for sx,ph in ((-1,1),(1,-1)):
        hp_=np.array([sx*0.09,hip,0])
        if sit>0.5: kn=hp_+np.array([0,0.02,-0.42]); ft=kn+np.array([0,-0.46,-0.02])
        else:
            a=ph*sw; ft=hp_+np.array([0,-0.78*math.cos(a),-0.78*math.sin(a)]); kn=(hp_+ft)/2+np.array([0,0,-0.04])
        Q+=transform(seg(hp_,kn,0.13,JEANS)+seg(kn,ft,0.115,JEANS)+box(ft[0]-0.06,ft[0]+0.06,ft[1]-0.04,ft[1]+0.03,ft[2]-0.12,ft[2]+0.05,WHITE),W)
    Q+=box(-0.18,0.18,0.8,1.33,-0.11,0.11,PINK,xf=WL)+box(-0.13,0.13,0.84,1.0,-0.116,-0.11,PINK_D,xf=WL)+box(-0.12,0.12,1.24,1.38,0.06,0.15,PINK,xf=WL)
    hc=np.array([0,1.47,0])
    def WH(p): p=np.array(p,float); return WL(hc+Ry(hy)@Rx(hp)@(p-hc))
    Q+=box(-0.05,0.05,1.32,1.38,-0.05,0.05,SKIN,xf=WL)
    Q+=box(-0.1,0.1,1.36,1.6,-0.11,0.1,SKIN,xf=WH)
    Q+=box(-0.118,0.118,1.53,1.65,-0.125,0.125,HAIR,xf=WH)+box(-0.122,0.122,0.98,1.62,0.08,0.135,HAIR,xf=WH)
    for sx in (-1,1): Q+=box(sx*0.104-0.018,sx*0.104+0.018,1.08,1.58,-0.07,0.11,HAIR,xf=WH)
    D+=box(-0.1,0.1,1.5,1.56,-0.124,-0.112,HAIR,xf=WH)
    for sx in (-1,1):
        x=sx*0.045; e=0.017*eye
        D+=box(x-e*0.8,x+e*0.8,1.47-e,1.47+e,-0.118,-0.11,(20,16,20),xf=WH)+box(x-0.004-sx*0.004,x+0.003-sx*0.004,1.478,1.486,-0.12,-0.118,(255,255,255),xf=WH)
        if blush>0: D+=box(x+sx*0.02-0.018,x+sx*0.02+0.018,1.42,1.435,-0.116,-0.11,(250,150,160),xf=WH)
    mh=0.008+0.03*mouth
    D+=box(-0.022-0.01*smile,0.022+0.01*smile,1.405-mh/2,1.405+mh/2,-0.118,-0.11,(150,60,70) if mouth>0.1 else (120,60,60),xf=WH)
    if panic>0:
        for k in range(2):
            u=((t*1.6+k*0.5)%1.0); y=1.6-0.14*u
            D+=box(0.1-0.012,0.1+0.012,y-0.02,y+0.02,-0.13,-0.1,(130,200,255),emit=True,xf=WH)
    rh=rh or (-0.26,0.9,-0.08); lh=lh or (0.26,0.9,-0.08)
    for sx,hd in ((-1,rh),(1,lh)):
        Q+=limb(np.array(WL((sx*0.24,1.28,0))),np.array(WL(hd)),tuple(Rb@np.array([sx*0.6,0,-0.2])),PINK,w=0.085)
    if phone: Q+=obox(np.array(WL(lh))+Rb@np.array([0,0.06,-0.03]),(0.035,0.065,0.01),Rb,(20,20,24))+obox(np.array(WL(lh))+Rb@np.array([0,0.06,-0.042]),(0.03,0.058,0.002),Rb,(140,200,255),emit=True)
    tag(D,WH((0,1.47,0)))
    return Q,D
def boyfriend(base,yaw,t,walk=0.0,rh=None,lh=None,hy=0.0,hood=0.0,eye=1.0,mouth=0.0,charger=False,lamp=0.0):
    b=np.array(base,float); Rb=Ry(yaw)
    def W(p): return tuple(b+Rb@np.array(p,float))
    Q=[]; D=[]; sw=0.45*math.sin(walk)
    for sx,ph in ((-1,1),(1,-1)):
        hp_=np.array([sx*0.1,0.92,0]); a=ph*sw; ft=hp_+np.array([0,-0.86*math.cos(a),-0.86*math.sin(a)]); kn=(hp_+ft)/2+np.array([0,0,-0.04])
        Q+=transform(seg(hp_,kn,0.15,BLACK)+seg(kn,ft,0.13,BLACK)+box(ft[0]-0.065,ft[0]+0.065,ft[1]-0.05,ft[1]+0.03,ft[2]-0.13,ft[2]+0.06,WHITE),W)
    Q+=box(-0.21,0.21,0.9,1.5,-0.12,0.12,GRAY,xf=W)+box(-0.14,0.14,0.94,1.1,-0.126,-0.12,GRAY_D,xf=W)
    hc=np.array([0,1.66,0])
    def WH(p): p=np.array(p,float); return W(hc+Ry(hy)@(p-hc))
    Q+=box(-0.05,0.05,1.5,1.56,-0.05,0.05,SKIN,xf=W)
    Q+=box(-0.11,0.11,1.54,1.8,-0.12,0.11,SKIN,xf=WH)+box(-0.118,0.118,1.74,1.84,-0.126,0.12,BHAIR,xf=WH)+box(-0.116,0.116,1.6,1.8,0.11,0.128,BHAIR,xf=WH)
    if hood<0.5: Q+=box(-0.15,0.15,1.44,1.6,0.09,0.2,GRAY,xf=W)
    else:
        Q+=box(-0.15,0.15,1.5,1.9,-0.1,0.16,GRAY,xf=WH)
        if lamp>0.5: Q+=box(-0.14,0.14,1.52,1.88,-0.136,-0.1,GRAY_D,xf=WH)
    if lamp<0.5:
        for sx in (-1,1):
            x=sx*0.045; e=0.016*eye
            D+=box(x-e,x+e,1.68-e,1.68+e,-0.126,-0.12,(20,16,20),xf=WH)+box(x-e,x+e,1.715,1.722,-0.126,-0.12,BHAIR,xf=WH)
        mh=0.008+0.03*mouth; D+=box(-0.025,0.025,1.6-mh/2,1.6+mh/2,-0.126,-0.12,(130,60,60),xf=WH)
    rh=rh or (-0.3,0.98,-0.06); lh=lh or (0.3,0.98,-0.06)
    if lamp>0: rh=lerp3(rh,(-0.04,2.25,-0.02),lamp); lh=lerp3(lh,(0.04,2.25,-0.02),lamp)
    for sx,hd in ((-1,rh),(1,lh)):
        Q+=limb(np.array(W((sx*0.28,1.44,0))),np.array(W(hd)),tuple(Rb@np.array([sx*0.6,0,-0.2])),GRAY,w=0.1)
    if charger: Q+=obox(np.array(W(rh))+Rb@np.array([0,-0.05,-0.04]),(0.03,0.04,0.02),Rb,WHITE)+seg(np.array(W(rh))+Rb@np.array([0,-0.09,-0.04]),np.array(W(rh))+Rb@np.array([0.05,-0.4,0.0]),0.012,WHITE)
    tag(D,WH((0,1.66,0)))
    return Q,D
# ---------------- the stream room ----------------
def room():
    r=random.Random(2); F=[]; B=[]; Rr=[]
    F+=tiled_plane(-2.2,2.2,-2.0,2.0,0,0.4,lambda i,j:(150,110,80) if (i+j//3)%2 else (138,100,72))
    for i,x in enumerate(np.arange(-2.2,2.2,0.4)):
        for j,y in enumerate(np.arange(0.0,2.6,0.4)):
            c=(46,46,54) if (i+j)%2 else (58,58,68); B+=box(x+0.02,x+0.38,y+0.02,y+0.38,1.94,2.0,c)
            B.append(quad([(x+0.2,y+0.2,1.9),(x+0.04,y+0.04,1.94),(x+0.36,y+0.04,1.94)],(c[0]+10,c[1]+10,c[2]+12)))
    B+=box(-2.2,2.2,0,2.7,2.0,2.06,(30,30,36))
    for k in range(11):
        x=-2.2+0.4*k; B.append(quad([(x,2.62,1.92),(x+0.4,2.62,1.92),(x+0.4,2.68,1.92),(x,2.68,1.92)],(255,80,200) if k%2 else (90,160,255),emit=True))
    Rr+=box(-2.26,-2.2,0,2.7,-2.0,2.0,(176,176,184))+box(-2.19,-2.18,1.0,1.9,-0.6,0.2,(70,90,160))+box(-2.18,-2.17,1.2,1.7,-0.45,0.05,(240,200,90))
    Rr+=box(2.2,2.26,0,2.7,-2.0,0.3,(176,176,184))+box(2.2,2.26,0,2.7,1.3,2.0,(176,176,184))+box(2.2,2.26,2.1,2.7,0.3,1.3,(176,176,184))
    Rr+=box(2.18,2.3,0,2.12,0.26,0.32,WHITE)+box(2.18,2.3,0,2.12,1.28,1.34,WHITE)+box(2.18,2.3,2.06,2.12,0.26,1.34,WHITE)
    Rr+=box(2.3,3.2,0,2.6,0.3,1.3,(20,18,24))
    Rr+=box(-2.2,2.2,2.7,2.76,-2.0,2.06,(40,40,48))
    for y in (0.55,1.05,1.55): Rr+=box(1.55,2.18,y,y+0.04,1.62,1.96,(120,90,60))
    Rr+=box(1.6,1.7,1.09,1.3,1.7,1.8,(60,140,70))+box(1.85,2.0,1.59,1.75,1.7,1.85,(220,90,80))+box(1.75,1.85,0.59,0.7,1.7,1.8,(90,120,200))
    Rr+=box(-0.35,0.35,0.0,0.06,-0.15,0.35,(30,30,36))
    return F,B,Rr
ROOM_F,ROOM_B,ROOM_R=room()
CHARGER_SPOT=(1.95,1.13,1.78)
def desk(t):
    Q=box(-1.0,1.0,0.72,0.77,-1.1,-0.5,(30,30,36))+box(-0.95,-0.9,0,0.72,-1.05,-0.55,(30,30,36))+box(0.9,0.95,0,0.72,-1.05,-0.55,(30,30,36))
    for k in range(10):
        x=-1.0+0.2*k; h=(k*37+int(t*8))%3; c=[(255,80,200),(120,90,255),(80,200,255)][h]
        Q.append(quad([(x,0.7,-0.5),(x+0.2,0.7,-0.5),(x+0.2,0.72,-0.5),(x,0.72,-0.5)],c,emit=True))
    Q+=box(-0.3,0.25,0.77,0.8,-0.85,-0.7,(50,50,60))+box(0.35,0.42,0.77,0.79,-0.82,-0.74,(60,60,70))
    Q+=seg((-0.6,0.77,-0.8),(-0.55,1.2,-0.6),0.03,(40,40,46))+seg((-0.55,1.2,-0.6),(-0.3,1.25,-0.35),0.03,(40,40,46))+box(-0.36,-0.24,1.18,1.32,-0.38,-0.28,(50,50,58))
    return Q
def chair(pull=0.0):
    z=0.12+0.25*pull; x=0.0+0.2*pull
    Q=box(x-0.28,x+0.28,0.42,0.5,z-0.2,z+0.25,(110,60,160))+box(x-0.28,x+0.28,0.5,1.45,z+0.22,z+0.32,(110,60,160))+box(x-0.2,x+0.2,1.0,1.4,z+0.18,z+0.22,(40,30,50))
    Q+=box(x-0.04,x+0.04,0.1,0.42,z-0.04,z+0.04,(40,40,46))+box(x-0.3,x+0.3,0.05,0.1,z-0.3,z+0.3,(40,40,46))
    return Q
# ======================= TIMELINE (story time = video time; the hook replays 21.0 s onward) =======================
TTS=os.environ.get('TTS',TTS_DIR)
SCRIPT=json.load(open(os.path.join(TTS,'v3','script.json')))
DUR=34.5; N=int(DUR*FPS); STORY0=5.3
CAM0=np.array([0.0,1.32,-0.95]); BFK=1.13
DOOR=(2.6,0.0,0.8); SHELF_POS=(1.75,0.0,1.6); BLOCK=(1.55,0.0,1.3)
def girl_state(T):
    st=dict(base=(0.0,0.0,0.05),yaw=0.0,sit=1.0,walk=0.0,rh=(-0.15,0.79,-0.55),lh=(0.15,0.79,-0.55),hy=0.0,hp=0.0,eye=1.0,mouth=0.0,smile=0.6,panic=0.0,phone=False,blush=0.0,lean=0.0)
    talk=lambda a,b:(0.5+0.5*math.sin(T*28))*win(T,a,b,0.05,0.05)
    if T<15.6:
        if 5.9<=T<7.4: u=win(T,5.9,7.4,0.2,0.3); st['rh']=lerp3(st['rh'],(-0.3,1.55,-0.15),u); st['lh']=lerp3(st['lh'],(0.3,1.55,-0.15),u); st['mouth']=talk(5.9,7.35); st['smile']=1.0
        if T>=10.9:
            pick=win(T,11.05,13.6,0.3,0.3); st['lh']=lerp3(st['lh'],(0.1,1.28,-0.32),pick); st['phone']=pick>0.05 or (10.9<=T<11.05)
            st['eye']=1.0+0.45*sm(seg01(T,11.6,11.8)); st['panic']=1.0 if T>=11.8 else 0.0; st['smile']=0.6*(1-sm(seg01(T,11.6,11.8)))
            st['hy']=-0.9*win(T,12.2,13.0,0.2,0.2)
        if 14.7<=T<15.6:
            u=win(T,14.7,15.6,0.15,0.2); st['rh']=lerp3(st['rh'],(-0.06,1.42,-0.15),u); st['lh']=lerp3(st['lh'],(0.06,1.42,-0.15),u); st['hy']=-0.8*u; st['mouth']=talk(14.85,15.7)*0.6
        st['hy']+=0.04*math.sin(T*1.7); return st
    st['panic']=1.0; st['eye']=1.4; st['smile']=0.0
    if T<16.1: st['sit']=1-sm(seg01(T,15.6,16.0)); st['base']=(0.0,0.0,0.05-0.2*sm(seg01(T,15.6,16.1))); return st
    st['sit']=0.0; st['rh']=(-0.26,0.9,-0.08); st['lh']=(0.26,0.9,-0.08)
    if T<17.2:
        u=sm(seg01(T,16.1,17.0)); st['base']=lerp3((0.0,0.0,-0.15),(-0.9,0.0,0.35),u); st['walk']=2*math.pi*1.8*(T-16.1)*(T<17.0); st['yaw']=0.5*win(T,16.1,17.0,0.2,0.2)
        st['smile']=0.8; return st
    if T<17.6: st['base']=(-0.9,0.0,0.35); st['hy']=-1.0*sm(seg01(T,17.2,17.4)); return st
    if T<19.4:
        u=sm(seg01(T,17.6,19.3)); st['base']=lerp3((-0.9,0.0,0.35),BLOCK,u); st['walk']=2*math.pi*2.6*(T-17.6)*(T<19.3); st['yaw']=-0.6*win(T,17.6,19.3,0.2,0.3)
        st['rh']=(-0.3,1.1,0.1); st['lh']=(0.3,1.1,0.1); return st
    st['base']=BLOCK
    if T<24.0:
        u=sm(seg01(T,19.4,19.7)); st['rh']=lerp3(st['rh'],(-0.6,1.28,-0.02),u); st['lh']=lerp3(st['lh'],(0.6,1.28,-0.02),u); st['smile']=0.9; st['mouth']=0.2
        st['hy']=2.4*win(T,21.6,22.6,0.25,0.25)*-1+0.0; st['blush']=1.0 if T>=21.0 else 0.0
        return st
    if T<24.7:
        u=sm(seg01(T,24.0,24.45)); hd=to_local_g(BF_HEAD_W(),BLOCK,0.0); st['rh']=lerp3(st['rh'],(hd[0]-0.12,hd[1]+0.12,hd[2]),u); st['lh']=lerp3(st['lh'],(hd[0]+0.12,hd[1]+0.12,hd[2]),u); st['hy']=-2.6*u
        return st
    st['hy']=-2.6*(1-sm(seg01(T,24.7,25.0))); st['rh']=(-0.26,0.9,-0.08); st['lh']=lerp3((0.26,0.9,-0.08),(0.62,1.15,-0.05),win(T,24.8,26.0,0.2,0.3))
    st['mouth']=(0.5+0.5*math.sin(T*24))*win(T,24.8,25.8,0.05,0.05); st['smile']=1.0; st['blush']=1.0; st['eye']=1.25
    return st
def to_local_g(world,base,yaw): return tuple(Ry(-yaw)@(np.array(world,float)-np.array(base,float)))
def BF_HEAD_W(): return (SHELF_POS[0],1.66*BFK,SHELF_POS[2])
def bf_state(T):
    st=dict(base=(3.6,0.0,0.8),yaw=2.33,walk=0.0,rh=None,lh=None,hy=0.0,hood=0.0,eye=1.0,mouth=0.0,charger=False,lamp=0.0,visible=False)
    if T<15.95: return st
    st['visible']=True
    if T<17.6:
        u=seg01(T,15.95,17.6); st['base']=lerp3(DOOR,SHELF_POS,sm(u)); st['walk']=2*math.pi*1.6*(T-15.95); return st
    st['base']=SHELF_POS
    if T<20.3:
        st['yaw']=keys(T,[(17.6,(2.33,)),(17.9,(math.pi,))])[0]
        reach=win(T,18.0,19.0,0.3,0.3); st['rh']=lerp3((-0.3,0.98,-0.06),to_local_g(CHARGER_SPOT,SHELF_POS,math.pi),reach); st['charger']=T>=18.6
        return st
    st['charger']=T<24.0; st['yaw']=keys(T,[(20.3,(math.pi,)),(20.6,(0.0,))])[0]; st['rh']=(-0.25,1.1,-0.2)
    st['eye']=1.3; st['mouth']=0.3*win(T,20.6,23.8,0.2,0.2); st['hy']=0.5*win(T,21.4,23.6,0.3,0.3)
    if T>=24.0: st['hood']=1.0 if T>=24.35 else 0.0
    if T>=25.1: st['lamp']=sm(seg01(T,25.1,25.4)); st['rh']=(-0.3,0.98,-0.06)
    return st
def head_world(base,yaw,local): return np.array(base,float)+Ry(yaw)@np.array(local,float)
def girl_head(T):
    g=girl_state(T); return head_world(g['base'],g['yaw'],(0,1.47-0.34*g['sit'],0))
def track_target(T):
    gh=girl_head(T)
    if T>=20.6: return 0.5*(gh+np.array(BF_HEAD_W()))-np.array([0,0.05,0])
    return gh
_TRACK={}
def track(T):
    """critically damped follow of the face target, integrated from the story start (deterministic per T)"""
    key=round(T,4)
    if key in _TRACK: return _TRACK[key]
    dt=1/60; w=4.6; x=track_target(STORY0).copy(); v=np.zeros(3); t=STORY0
    while t<T:
        a=w*w*(track_target(t)-x)-2*w*v; v=v+a*dt; x=x+v*dt; t+=dt
    _TRACK[key]=(x,np.linalg.norm(v)); return _TRACK[key]
def fov_at(T): return 44-8*sm(seg01(T,16.2,19.0))-10*sm(seg01(T,20.6,21.0))-6*sm(seg01(T,28.4,31.0))
# ---------------- chat + viewers ----------------
CHAT=[(5.6,'MOCHI','ARE U SINGLE??'),(6.4,'JK_77','SINGLE??'),(7.3,'NOVA','W STREAMER'),(8.6,'TOFU','SINGLE FOREVER'),(9.6,'ZED','LOL'),
      (11.2,'MOCHI','WHO TEXTED?'),(12.3,'KAI','SHE LOOKS SCARED'),(13.4,'ZED','SUS'),(16.2,'NOVA','WHO SAID BABE??'),(17.0,'TOFU','I HEARD A GUY'),
      (18.2,'KAI','CAMERA TURNING'),(19.4,'JK_77','OH NO'),(20.7,'MOCHI','WHO IS THAT'),(20.9,'ZED','WHO IS THAT'),(21.1,'NOVA','BROOOO'),
      (21.4,'TOFU','SINGLE?? LOL'),(22.1,'KAI','HE IS TALLER LMAO'),(23.0,'ZED','CLIP IT'),(25.3,'MOCHI','A LAMP??'),(25.8,'NOVA','LAMP WITH SHOES'),
      (26.5,'TOFU','LAMP IS SWEATING'),(27.4,'KAI','CLIP IT CLIP IT'),(28.6,'JK_77','AUTO-TRACK MVP'),(29.8,'ZED','W CAMERA')]
UCOL={'MOCHI':(255,140,200),'JK_77':(120,200,255),'NOVA':(255,214,40),'TOFU':(140,240,150),'ZED':(255,150,90),'KAI':(190,150,255)}
def viewers(T):
    v=10284+int(40*max(0,T-5.3))
    if T>=20.6: v+=int(48000*sm(seg01(T,20.6,31.0)))
    return v
YEL=(255,214,40); WHT=(255,255,255); RED=(255,70,60); GRN=(90,230,90)
def fmt(n): return '{:,}'.format(n)
def brackets(d,x,y,r,col,label):
    x0,y0,x1,y1=int(x-r),int(y-r),int(x+r),int(y+r); L=max(3,int(r*0.45))
    for (ax,ay,dx,dy) in ((x0,y0,1,1),(x1,y0,-1,1),(x0,y1,1,-1),(x1,y1,-1,-1)):
        d.line([ax,ay,ax+dx*L,ay],fill=col,width=1); d.line([ax,ay,ax,ay+dy*L],fill=col,width=1)
    otext(d,label,x0,y0-10,col,1)
def bubble(d,x,y,txt,col=(0,0,0)):
    w=font.width(txt)+8; x0=int(max(2,min(W-w-2,x-w//2))); y0=int(y-16)
    d.rectangle([x0,y0,x0+w,y0+12],fill=(250,250,250),outline=(0,0,0)); tx=int(max(x0+4,min(x0+w-4,x)))
    d.polygon([(tx-3,y0+12),(tx+3,y0+12),(tx,y0+17)],fill=(250,250,250),outline=(0,0,0)); d.line([tx-2,y0+12,tx+2,y0+12],fill=(250,250,250))
    font.text(d,txt,x0+4,y0+3,col,1,None)
def wrap(txt,n=29):
    out=[]; cur=''
    for w_ in txt.split():
        if len(cur)+len(w_)+(1 if cur else 0)>n: out.append(cur); cur=w_
        else: cur=(cur+' '+w_).strip()
    if cur: out.append(cur)
    return out
HIL={'BOYFRIEND','CAMERA','SINGLE.','FACE-TRACKING','TALLER.','FACE','PLANS.','JOB.'}
def subtitle(d,T):
    for key,t0,txt,dd,v in SCRIPT:
        if key.startswith('N') and t0<=T<t0+dd+0.3:
            lines=wrap(txt.upper().replace('...','..')); y=262-10*(len(lines)-1)
            for ln in lines:
                xw=font.width(ln); x=(W-xw)//2; d.rectangle([x-3,y-2,x+xw+2,y+8],fill=(0,0,0)); cx=x
                for wd in ln.split(' '): otext(d,wd,cx,y,YEL if wd in HIL else WHT,1); cx+=font.width(wd)+6
                y+=11
            return
SPEECH={'G1':'SINGLE! FOREVER SINGLE!','G2':"DON'T COME IN!",'B1':"BABE? WHERE'S MY CHARGER?",'G3':"IT'S.. A LAMP."}
# ---------------- render ----------------
R=Renderer(W,H,fog=(20,18,26))
def scale_y(Q,k):
    out=[]
    for q in Q:
        q=dict(q); q['p']=[(x,y*k,z) for (x,y,z) in q['p']]
        if 'hc' in q: q['hc']=np.array([q['hc'][0],q['hc'][1]*k,q['hc'][2]])
        out.append(refresh(q))
    return out
def scene(T):
    g=girl_state(T); b=bf_state(T)
    gq,gd=girl(g['base'],g['yaw'],T,sit=g['sit'],walk=g['walk'],rh=g['rh'],lh=g['lh'],hy=g['hy'],hp=g['hp'],eye=g['eye'],mouth=g['mouth'],smile=g['smile'],panic=g['panic'],phone=g['phone'],blush=g['blush'])
    chars=[(gq,gd)]
    if b['visible']:
        bq,bd=boyfriend(b['base'],b['yaw'],T,walk=b['walk'],rh=b['rh'],lh=b['lh'],hy=b['hy'],hood=b['hood'],eye=b['eye'],mouth=b['mouth'],charger=b['charger'],lamp=b['lamp']); chars.append((scale_y(bq,BFK),scale_y(bd,BFK)))
    if T>=18.6: ch=[]
    else: ch=box(CHARGER_SPOT[0]-0.04,CHARGER_SPOT[0]+0.04,CHARGER_SPOT[1]-0.03,CHARGER_SPOT[1]+0.03,CHARGER_SPOT[2]-0.03,CHARGER_SPOT[2]+0.03,WHITE)
    pull=sm(seg01(T,15.6,16.1)) if T>=15.6 else 0.0
    return g,b,chars,chair(pull)+ch
def render(T):
    g,b,chars,props=scene(T)
    tgt,_=track(T); cam=Camera.look(tuple(CAM0),tuple(tgt))
    cp=CAM0
    chars=sorted(chars,key=lambda cd:-np.linalg.norm(np.mean([q['c'] for q in cd[0]],axis=0)-cp))
    layers=[ROOM_F,ROOM_B,ROOM_R+props]
    for q,dd in chars:
        layers+=[q,[x for x in dd if np.linalg.norm(x['c']-cp)<np.linalg.norm(x['hc']-cp)]]
    layers.append(desk(T))
    L=[((0.8,2.3,1.7),(255,90,210),0.55),((-1.4,2.3,1.6),(90,150,255),0.5),((0.0,1.5,-0.8),(255,240,225),0.75),((0.5,2.6,0.4),(255,235,210),0.45)]
    img,vi=R.render(cam,layers,L,fov=fov_at(T),fog_start=12,fog_end=30,ambient=0.42)
    return post.ps1(img),vi,g,b
def hud(img,vi,T,g,b,hook=False):
    d=ImageDraw.Draw(img)
    def proj(p): return R.project(p,vi)
    d.rectangle([6,6,36,16],fill=(220,30,40)); d.ellipse([9,9,13,13],fill=WHT); font.text(d,'LIVE',16,8,WHT,1,None)
    vs=fmt(viewers(T)); d.rectangle([40,6,48+font.width(vs)+10,16],fill=(0,0,0)); d.ellipse([43,8,51,14],outline=WHT); d.ellipse([46,10,48,12],fill=WHT); font.text(d,vs,54,8,WHT,1,None)
    _,spd=track(T); on='AUTO-TRACK'; d.rectangle([W-6-font.width(on)-12,6,W-6,16],fill=(0,0,0)); d.ellipse([W-6-font.width(on)-9,9,W-6-font.width(on)-5,13],fill=GRN if int(T*4)%2 or spd<0.2 else (40,120,40)); font.text(d,on,W-6-font.width(on)-2,8,WHT,1,None)
    if 12.6<=T<14.4 and int(T*5)%2==0: otext(d,'AUTO-TRACK: ON',(W-font.width('AUTO-TRACK: ON',2))//2,40,GRN,2)
    # face boxes
    gh=girl_head(T); q=proj(tuple(gh))
    if q: brackets(d,q[0],q[1],max(6,int(70/q[2]*0.16)),GRN,'FACE 1')
    if b['visible'] and T>=20.6:
        qb=proj(BF_HEAD_W())
        if qb: brackets(d,qb[0],qb[1],max(6,int(70/qb[2]*0.16)),YEL if int(T*6)%2 else RED,'FACE 2' if T<25.2 else 'LAMP?')
    if 20.6<=T<22.6:
        u=sm(seg01(T,20.6,20.75)); y=int(-14+44*u); d.rectangle([28,y,152,y+16],fill=(40,0,0),outline=RED); otext(d,'FACE DETECTED: 2',(W-font.width('FACE DETECTED: 2'))//2,y+5,YEL,1)
    # phone popup
    if 10.9<=T<12.9:
        u=sm(seg01(T,10.9,11.1)); x0=int(W-4-100*u)
        d.rectangle([x0,60,x0+96,104],fill=(30,30,40),outline=(200,200,220)); font.text(d,'1 NEW MESSAGE',x0+5,64,(160,200,255),1,None)
        font.text(d,'BF: COMING IN',x0+5,78,WHT,1,None); font.text(d,'FOR MY CHARGER',x0+5,88,WHT,1,None)
    # speech
    for key,t0,txt,dd,v in SCRIPT:
        if key in SPEECH and t0<=T<t0+dd+0.4:
            if key=='B1': bubble(d,W-30,120,"BABE? MY CHARGER?")
            else:
                q=proj(tuple(gh+np.array([0,0.24,0])))
                if q: bubble(d,q[0],q[1],SPEECH[key] if len(SPEECH[key])<=26 else SPEECH[key][:26])
    # chat
    msgs=[m for m in CHAT if m[0]<=T][-4:]
    if msgs:
        y0=244-len(msgs)*10; reg=img.crop((3,y0-3,142,246)); img.paste(Image.blend(reg,Image.new('RGB',reg.size,(0,0,0)),0.62),(3,y0-3)); d=ImageDraw.Draw(img)
        for i,(t0,u_,tx) in enumerate(msgs):
            y=y0+i*10; ux=font.width(u_+':'); otext(d,u_+':',6,y,UCOL[u_],1)
            room_=(140-6-ux-4)//6; otext(d,tx[:room_],6+ux+4,y,WHT,1)
    if T>=31.4:
        u=sm(seg01(T,31.4,31.6)); d.rectangle([10,52,170,120],fill=(16,20,60),outline=WHT)
        otext(d,'RELATIONSHIP STATUS:',(W-font.width('RELATIONSHIP STATUS:'))//2,60,WHT,1)
        if T>=31.8: otext(d,'LEAKED',(W-font.width('LEAKED',3))//2,74,RED,3)
        if T>=32.4: s_='VIEWERS: '+fmt(viewers(T)); otext(d,s_,(W-font.width(s_))//2,104,GRN,1)
    subtitle(d,T)
    return img
def frame(T):
    if T<4.9:
        st=21.0+T*0.5; img,vi,g,b=render(st); img=hud(img,vi,st,g,b,hook=True)
        d=ImageDraw.Draw(img)
        for key,t0,txt,dd,v in SCRIPT:
            if key in ('N1','N2') and t0<=T<t0+dd+0.3:
                d.rectangle([0,248,W,282],fill=(0,0,0))
                for i,ln in enumerate(wrap(txt.upper())): otext(d,ln,(W-font.width(ln))//2,252+i*11,WHT,1)
        return img,False
    if T<STORY0:
        u=(T-4.9)/(STORY0-4.9); img,vi,g,b=render(23.4-18*u); d=ImageDraw.Draw(img)
        for k in range(2): d.polygon([(66+k*7,160),(72+k*7,155),(72+k*7,165)],fill=WHT,outline=(0,0,0))
        otext(d,'EARLIER',86,156,WHT,1); return img,True
    img,vi,g,b=render(T); return hud(img,vi,T,g,b),False
TEST=os.environ.get('TEST')
if TEST:
    ims=[frame(float(x))[0] for x in TEST.split(',')]; sh=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): sh.paste(im,(i*182,0))
    sh.resize((sh.width*2,640),Image.NEAREST).save('test.png'); sys.exit()
# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=11); sr=s.sr
    M=np.zeros(s.n)
    def note(buf,t0,m,d,v,wave='sq',duty=0.5,dec=3.0,att=0.005):
        f=440*2**((m-69)/12); tt=s.T(d); ph=(f*tt)%1
        if wave=='sq': x=np.where(ph<duty,1.0,-1.0)
        elif wave=='tri': x=4*np.abs(ph-0.5)-1
        else: x=np.sin(2*np.pi*f*tt)
        env=np.minimum(1,tt/att)*np.exp(-tt*dec); i=int(t0*sr); j=min(s.n,i+len(tt)); buf[i:j]+=(x*env*v)[:j-i]
    def kick(t0,v=0.2): tt=s.T(0.14); i=int(t0*sr); j=min(s.n,i+len(tt)); M[i:j]+=(np.sin(2*np.pi*(100-55*tt/0.14)*tt)*np.exp(-tt*22)*v)[:j-i]
    def hat(t0,v=0.03,seed=0): x=s.filt_short(s.noise(0.05,seed),lo=6000)*np.exp(-s.T(0.05)*80); i=int(t0*sr); j=min(s.n,i+len(x)); M[i:j]+=(x*v)[:j-i]
    def snare(t0,v=0.07,seed=0): x=s.filt_short(s.noise(0.12,seed),lo=1500,hi=6000)*np.exp(-s.T(0.12)*28); i=int(t0*sr); j=min(s.n,i+len(x)); M[i:j]+=(x*v)[:j-i]
    def nb(t0,d,lo,hi,v,seed,shape=2,pan=0.0): s.place(s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v,pan)
    def chirp(t0,d,f0,f1,v,pan=0.0,shape=1): tt=s.T(d); s.place(np.sin(2*np.pi*np.cumsum(f0+(f1-f0)*tt/d)/sr)*np.sin(np.pi*tt/d)**shape,t0,v,pan)
    def step(t0,v=0.06,seed=0,pan=0.0): s.place(s.filt_short(s.noise(0.05,seed),lo=120,hi=1400)*np.exp(-s.T(0.05)*60),t0,v,pan)
    def click(t0,v=0.03,seed=0): s.place(s.filt_short(s.noise(0.02,seed),lo=2000,hi=8000)*np.exp(-s.T(0.02)*200),t0,v,-0.2)
    def beep(t0,f,d,v): tt=s.T(d); s.place(np.where((f*tt)%1<0.5,1.0,-1.0)*np.minimum(1,(d-tt)/0.01),t0,v)
    # ---- music ----
    # hook: tense pulse
    for k in range(int(4.8/0.2)): note(M,0.0+k*0.2,40 if (k//4)%2==0 else 41,0.18,0.08,'tri',dec=4)
    for k in range(6): note(M,0.0+k*0.8,64 if k%2==0 else 63,0.6,0.025,'sq',duty=0.25,dec=3)
    # story lo-fi beat 5.3 -> 20.6 (98 bpm-ish swing)
    st=0.3; chords=[(45,57,60,64),(41,57,60,65),(48,55,60,64),(43,55,59,62)]
    k=0; t=5.3
    while t<20.6-1e-6:
        c=chords[(k//8)%4]
        if k%8==0:
            for m in c[1:]: note(M,t,m,st*8,0.018,'tri',dec=0.7,att=0.04)
        if k%2==0: note(M,t,c[0],st*1.8,0.07,'tri',dec=2.5)
        if k%8 in (0,5): kick(t,0.16)
        if k%8==4: snare(t,0.05,k)
        hat(t+(0.04 if k%2 else 0),0.02,k)
        k+=1; t+=st
    # record scratch at the reveal, then silence
    M[int(20.6*sr):]=0
    # 21.0-24.0 sneaky pizzicato
    for k,m in enumerate([57,None,60,None,57,None,64,63,57,None,60,None,57,None,52,None]*2):
        if m and 21.0+k*0.19<24.0: note(M,21.0+k*0.19,m,0.15,0.05,'sq',duty=0.25,dec=14)
    for k in range(8): note(M,21.0+k*0.38,33,0.3,0.06,'tri',dec=6)
    # lamp sting (wah-wah) 25.15
    for k,m in enumerate([62,61,60,59]): note(M,25.2+k*0.32,m,0.34 if k<3 else 0.9,0.05,'sq',duty=0.5,dec=1.5 if k==3 else 3)
    # upbeat outro 26.6-31.4
    k=0; t=26.6
    while t<31.4-1e-6:
        c=chords[(k//8)%4]
        if k%2==0: note(M,t,c[0],0.25,0.07,'tri',dec=3)
        note(M,t,[69,72,76,72,71,74,77,74][k%8],0.18,0.022,'sq',duty=0.25,dec=8)
        if k%4==0: kick(t,0.15)
        if k%4==2: snare(t,0.05,k)
        hat(t,0.015,k); k+=1; t+=0.2
    # end jingle
    for k,m in enumerate([72,76,79,84,79,84]): note(M,31.5+k*0.11,m,0.3,0.05,'sq',duty=0.25,dec=5)
    note(M,31.5,48,1.8,0.08,'tri',dec=1.2); note(M,31.5,55,1.8,0.04,'tri',dec=1.2)
    # ---- voices ----
    Nb=np.zeros(s.n); duck=np.ones(s.n)
    for key,t0,txt,dd,v in SCRIPT:
        a,ar=_sf.read(os.path.join(TTS,'v3',key+'.wav')); a=a if a.ndim==1 else a.mean(1)
        a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a)
        if key.startswith('B'): a=s.filt_short(a,lo=250,hi=3200)*1.1          # offscreen, through the door
        if key=='G2': a=a*0.75
        i=int(t0*sr); j=min(s.n,i+len(a)); Nb[i:j]+=a[:j-i]*0.95
        i0=max(0,i-int(0.1*sr)); j1=min(s.n,j+int(0.2*sr)); duck[i0:j1]=0.38
    duck=np.convolve(duck,np.ones(2400)/2400,'same'); s.L+=M*duck; s.R+=M*duck
    # ---- sfx ----
    s.bed(s.filt(s.rng.normal(0,1,s.n),lo=60,hi=500)*0.012)                                 # room tone
    beep(0.12,880,0.07,0.05); beep(0.22,1320,0.1,0.05)                                       # face detected (hook)
    for t0 in (0.6,1.3,1.9,2.6,3.4,4.1): chirp(t0,0.05,1500,2100,0.02)                      # chat spam blips
    chirp(4.9,0.4,1800,300,0.08); nb(4.9,0.4,800,6000,0.1,5)                                 # rewind
    for k in range(16): click(5.35+k*0.07+0.02*math.sin(k*3),0.035,k)                        # keyboard
    for k in range(20): click(8.1+k*0.11+0.03*math.sin(k*5),0.03,30+k)
    for c in CHAT:
        if c[0]>=5.3: chirp(c[0],0.05,1500,2100,0.018)
    for k in range(2):                                                                        # phone buzz
        tt=s.T(0.32); s.place(np.where((150*tt)%1<0.5,1.0,-1.0)*np.sin(np.pi*tt/0.32)*(0.6+0.4*np.sin(2*np.pi*30*tt)),10.9+k*0.42,0.05,0.2)
    chirp(11.65,0.25,400,1200,0.05)                                                           # panic gulp
    beep(12.6,1046,0.06,0.03); beep(12.7,1568,0.08,0.03)                                      # AUTO-TRACK ON
    tt=s.T(1.0); s.place(np.sin(2*np.pi*np.cumsum(120+50*np.sin(2*np.pi*1.4*tt)+20*np.sin(2*np.pi*11*tt))/sr)*np.sin(np.pi*tt)*0.6,15.75,0.06,0.6)  # door creak
    nb(15.6,0.5,200,1500,0.05,7)                                                              # chair roll
    for k in range(5): step(16.0+k*0.33,0.07,50+k,0.6)                                        # his steps
    for k in range(4): step(16.15+k*0.24,0.05,60+k,-0.2)                                      # her steps
    for k in range(8): step(17.65+k*0.21,0.06,70+k,0.2)
    click(18.6,0.06,90); chirp(18.62,0.06,2400,2600,0.02)                                     # grabs charger
    # record scratch
    chirp(20.6,0.18,1400,300,0.12); nb(20.6,0.2,500,5000,0.12,100)
    beep(20.66,880,0.07,0.06); beep(20.78,880,0.07,0.06); beep(20.9,1320,0.12,0.06)          # FACE DETECTED: 2
    for k in range(10): chirp(20.8+k*0.25,0.04,1600,2200,0.02)                               # chat explodes
    nb(24.25,0.3,600,5000,0.1,110)                                                            # hood whoosh
    for k in range(14): chirp(25.4+k*0.3,0.04,1600,2200,0.016)
    nb(31.4,0.3,500,4000,0.1,120); s.thud(31.8,f=60,v=0.4); nb(31.8,0.3,100,1500,0.15,121)  # LEAKED stamp
    # servo whir follows how fast the camera pans
    dt=1/60; w=4.6; x=track_target(STORY0).copy(); v=np.zeros(3); t=STORY0; sp=[]
    while t<31.4:
        a=w*w*(track_target(t)-x)-2*w*v; v=v+a*dt; x=x+v*dt; t+=dt; sp.append(np.linalg.norm(v))
    env=np.zeros(s.n); i0=int(STORY0*sr); e=np.interp(np.arange(int(len(sp)*dt*sr))/sr,np.arange(len(sp))*dt,sp); env[i0:i0+len(e)]=e[:s.n-i0]
    whir=np.sin(2*np.pi*np.cumsum(700+500*np.clip(env,0,1.5))/sr)*0.5+s.filt(s.rng.normal(0,1,s.n),lo=1500,hi=4000)*0.6
    s.L+=whir*np.clip(env,0,1.5)*0.03; s.R+=whir*np.clip(env,0,1.5)*0.03
    s.L+=Nb; s.R+=Nb
    s.reverb(0.08,length=0.6,decay=6)
    return s.save(path,peak=0.9)
if __name__=='__main__':
    PART=os.environ.get('PART')
    if PART=='audio':
        print(build_audio(os.path.join(OUT,'face_track.wav'))); sys.exit()
    if PART:
        a,b=map(int,PART.split(':'))
        import subprocess
        p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'ft_{a:05d}.mp4')],stdin=subprocess.PIPE)
        vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.93,vignette=0.3,grain=1.8,band_period=1e9)
        for f in range(a,min(b,N)): p.stdin.write(vhs(post.upscale(frame(f/FPS)[0],S),f,f/FPS).tobytes())
        p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
