"""CAT DODGE BOSS - "Why do cats dodge food guards better than video game bosses?"  PS1 comedy short, 9:16, 15 s. Fully procedural (nightkit).
LOCKED ASSETS: the woman = face_track.girl() (pink top, jeans, white socks; only the optional `legs` argument was added),
the cat (cat_model: orange tabby, big head, pixel shades), the bed room, the pizza (slice_quads) and the plate.
All text is a 2D overlay. Voice: python tools/tts/cd.py -> $TTS_DIR/cd/N1.wav (hook line only; the rest is visual comedy + sound).
Run: TEST=0.5,5,12 python examples/cat_dodge.py -> test.png | PART=a:b | PART=audio | QA: python tools/qa/scene_qa.py examples/cat_dodge.py"""
import os, sys, math, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, box, quad, transform, tiled_plane
from nightkit import post, font
from nightkit.zraster import zrender
from nightkit.audio import Sound
_T=os.environ.pop('TEST',None)                      # face_track has its own TEST hook at import time
import face_track as FT
if _T is not None: os.environ['TEST']=_T
sm,seg01,lerp3,seg,tag,Rx,Ry,Rz=FT.sm,FT.seg01,FT.lerp3,FT.seg,FT.tag,FT.Rx,FT.Ry,FT.Rz
PI=math.pi
def lerp(a,b,u): return a+(b-a)*u
TTS_DIR=FT.TTS_DIR; OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6; DUR=15.0; N=int(round(DUR*FPS))
SCR=json.load(open(os.path.join(TTS_DIR,'cd','script.json')))
for ch,rows in {'+':['00000','00100','00100','11111','00100','00100','00000'],'%':['11001','11010','00010','00100','01000','01011','10011']}.items(): font.FONT.setdefault(ch,rows)

# ======================= palette =======================
ORANGE=(232,150,70); ORANGE_D=(196,112,48); CREAM=(250,226,190); PINK_N=(240,130,150); EYE_Y=(255,214,70); BLACKC=(22,20,28)
CHEESE=(255,196,64); CRUST=(214,150,80); PEPP=(196,48,40); PLATE=(236,240,250); PLATE_D=(150,170,210)
YEL=(255,210,60); RED=(232,44,40); GRN=(120,230,90); WHT=(242,238,226); CYAN=(90,210,255); GRY=(150,150,160)
WOOD=(150,106,72); WOOD2=(138,96,64); WALL=(150,120,190); WALL2=(132,104,174); QUILT1=(92,130,210); QUILT2=(150,180,240); PILLOW=(246,238,226); FRAME=(104,66,44)

# ======================= timeline (seconds) =======================
HOOK=2.9; T_BLOCK=(1.05,1.4); T_DODGE=3.0; T_SHADES=3.0; T_CALM=10.5
ATT=[3.5,4.4,5.4,6.3,7.5,8.6,9.7]; MISS_AT=[7.5,8.6,9.7]        # foot attempts (MISS text on the last three)
T_BITE=(10.6,11.4); T_NOTICE=11.3; T_CROUCH=(11.3,11.95); T_LUNGE=(11.95,12.7); T_DIVE=(12.7,13.1); T_TURN=(13.0,13.35); T_FREEZE=13.45; T_WIN=13.6
SHOTS=[(0.0,3.0,'hook'),(3.0,4.0,'faceR'),(4.0,5.0,'wideL'),(5.0,6.0,'over'),(6.0,7.0,'faceL'),(7.0,8.1,'overL'),(8.1,9.2,'faceR'),(9.2,10.3,'wideR'),
       (10.3,11.3,'wideL'),(11.3,11.95,'faceR'),(11.95,12.9,'wideR'),(12.9,DUR,'final')]

# ======================= world layout =======================
BED_Y=0.42; GBASE=(0.0,0.0,0.25)
PLATE_C=np.array([0.0,0.60,-0.08])
REST_FOOT={-1:(-0.34,0.47,-0.80),1:(0.34,0.47,-0.80)}
GUARD_Z=-0.78; GUARD_Y=0.72
CAT_Y=BED_Y; ZC0=-1.65; ZC_STOP=-1.15

# ======================= LOCKED ASSET: the cat =======================
def cat_model(base,yaw=0.0,walk=0.0,hx=0.0,hyaw=0.0,hroll=0.0,hpitch=0.0,lid=0.5,pupil=0.0,tail=0.0,crouch=0.0,ears=0.0,mouth=0.0,bpitch=0.0,shades=0.0,cheese=0.0,smug=0.0,wl=1.0,wu=0.0,paw=0.0,paw_to=(-0.15,0.1,0.3),**_):
    """orange tabby, local forward +z. hx: sideways head shift (the main gag). crouch/bpitch: pounce. paw/paw_to: left front paw reach (0 = off). returns (quads, face decals)"""
    b=np.array(base,float); Rb=Ry(yaw); piv=np.array([0,0.2,-0.05])
    def Wd(p): p=np.array(p,float); p=piv+Rx(bpitch)@(p-piv); return tuple(b+Rb@p)
    Q=[]; D=[]; cy=-0.07*crouch
    for sx in (-1,1):
        for zz,front in ((0.13,True),(-0.17,False)):
            ph=walk+(0.0 if (sx>0)==front else PI); sw=0.06*math.sin(ph) if walk else 0.0; lift=0.035*max(0.0,math.cos(ph)) if walk else 0.0
            top=(sx*0.065,0.16+cy+(0.02*crouch if not front else 0.0),zz); ft=(sx*0.065,lift,zz+sw)
            if paw and sx<0 and front: ft=lerp3(ft,paw_to,paw)                               # paw reach / swipe (left front leg, local coords)
            Q+=transform(seg(top,ft,0.05,ORANGE,0.05)+box(ft[0]-0.03,ft[0]+0.03,ft[1],ft[1]+0.028,ft[2]-0.03,ft[2]+0.05,CREAM),Wd)
    Q+=box(-0.10,0.10,0.10+cy+0.02*crouch,0.29+cy+0.03*crouch,-0.26,-0.04,ORANGE,xf=Wd)+box(-0.085,0.085,0.11+cy,0.29+cy,-0.04,0.17,ORANGE,xf=Wd)
    Q+=box(-0.05,0.05,0.10+cy,0.115+cy,-0.2,0.15,CREAM,xf=Wd)
    for k in range(3): z=-0.2+0.09*k; Q+=box(-0.088,0.088,0.29+cy,0.299+cy,z,z+0.035,ORANGE_D,xf=Wd)
    pts=[(0,0.26+cy,-0.25),(0,0.34,-0.31),(0,0.46,-0.34),(0,0.58,-0.33),(0,0.68,-0.29),(0,0.74,-0.22)]
    for k in range(5):
        a=np.array(pts[k],float); c=np.array(pts[k+1],float)
        a[0]+=0.05*math.sin(tail)*(k/5)**1.5; c[0]+=0.05*math.sin(tail)*((k+1)/5)**1.5
        Q+=transform(seg(a,c,0.045-0.004*k,ORANGE_D if k%2 else ORANGE,0.045-0.004*k),Wd)
    HP=np.array([hx,0.37+cy*0.7,0.25]); Rh=Ry(hyaw)@Rz(hroll)@Rx(hpitch)
    def Hd(p): p=np.array(p,float); return Wd(HP+Rh@p)
    Q+=transform(seg((0,0.27+cy,0.12),tuple(HP+np.array([0,-0.04,-0.05])),0.1,ORANGE,0.1),Wd)
    Q+=box(-0.12,0.12,-0.09,0.10,-0.09,0.09,ORANGE,xf=Hd)+box(-0.055,0.055,-0.065,0.0,0.09,0.135,CREAM,xf=Hd)+box(-0.035,0.035,-0.085,-0.065,0.085,0.125,CREAM,xf=Hd)
    Q+=box(-0.017,0.017,-0.012,0.012,0.135,0.142,PINK_N,xf=Hd)
    for x in (-0.04,0.0,0.04): Q+=box(x-0.008,x+0.008,0.10,0.107,-0.07,0.05,ORANGE_D,xf=Hd)
    for sx in (-1,1):
        def Ed(p,sx=sx): p=np.array(p,float); bp=np.array([sx*0.075,0.095,0.0]); return Hd(bp+Rz(-sx*ears*0.7)@(p-bp))
        Q+=box(sx*0.075-0.04,sx*0.075+0.04,0.095,0.15,-0.035,0.025,ORANGE,xf=Ed)+box(sx*0.075-0.025,sx*0.075+0.025,0.15,0.2,-0.03,0.02,ORANGE,xf=Ed)
        D+=box(sx*0.075-0.02,sx*0.075+0.02,0.1,0.15,0.0255,0.027,PINK_N,xf=Ed)
        for k in (-1,0,1): Q+=transform(seg((sx*0.05,-0.035,0.125),(sx*(0.05+0.16*wl),-0.035+k*0.035*wl+0.09*wu,0.115),0.006,WHT,0.006),Hd)
        ex=sx*0.062
        D+=box(ex-0.026,ex+0.026,0.015,0.065,0.0905,0.0915,EYE_Y,xf=Hd)
        D+=box(ex+sx*pupil*0.012-0.006,ex+sx*pupil*0.012+0.006,0.018,0.062,0.0925,0.0935,BLACKC,xf=Hd)
        if lid>0: D+=box(ex-0.027,ex+0.027,0.065-0.05*lid,0.067,0.0935,0.0945,ORANGE,xf=Hd)
    if mouth>0.1: D+=box(-0.025,0.025,-0.075,-0.04,0.1355,0.137,BLACKC,xf=Hd)+box(-0.015,0.015,-0.073,-0.058,0.1365,0.138,PINK_N,xf=Hd)
    else: D+=box(-0.034,-0.004,-0.045,-0.038,0.1355,0.137,BLACKC,xf=Hd)+box(0.004,0.034,-0.045,-0.038,0.1355,0.137,BLACKC,xf=Hd)
    if shades>0.01:                                                                         # pixel shades drop in from above
        dy=0.35*(1-shades)**2
        D+=box(-0.118,0.118,0.012+dy,0.07+dy,0.095,0.103,BLACKC,xf=Hd)+box(-0.015,0.015,0.05+dy,0.062+dy,0.095,0.104,BLACKC,xf=Hd)
        D+=box(-0.095,-0.055,0.05+dy,0.062+dy,0.1035,0.1045,(250,250,255),xf=Hd,emit=True)+box(0.03,0.07,0.05+dy,0.062+dy,0.1035,0.1045,(250,250,255),xf=Hd,emit=True)
        for sx in (-1,1): D+=box(sx*0.118,sx*0.124,0.03+dy,0.045+dy,-0.08,0.1,BLACKC,xf=Hd)
    if cheese>0.01:                                                                          # pizza on the muzzle and forehead (eyes stay clear)
        D+=box(-0.05,0.05,-0.05,-0.005+0.02*cheese,0.139,0.148,CHEESE,xf=Hd)+box(-0.035,-0.01,-0.045,-0.02,0.149,0.153,PEPP,xf=Hd)+box(0.012,0.04,-0.04,-0.015,0.149,0.153,PEPP,xf=Hd)
        D+=box(-0.015,0.025,0.072,0.097,0.0905,0.0925,PEPP,xf=Hd)
    tag(D,Wd(HP)); return Q,D
def head_world(st):
    """world position + rough half size of the cat's head, for QA clearance checks"""
    b=np.array(st['base'],float); Rb=Ry(st.get('yaw',0.0)); piv=np.array([0,0.2,-0.05]); cy=-0.07*st.get('crouch',0.0)
    p=np.array([st.get('hx',0.0),0.37+cy*0.7,0.25]); p=piv+Rx(st.get('bpitch',0.0))@(p-piv); return b+Rb@p

# ======================= LOCKED ASSET: pizza + plate =======================
def slice_quads(c,yaw=0.0,tilt=0.0,sc=1.0):
    """one pizza slice; tip +z, crust -z, centre c"""
    c=np.array(c,float); R_=Ry(yaw)@Rx(tilt)
    def Wd(p): return tuple(c+R_@(np.array(p,float)*sc))
    tip=(0,0.02,0.1); a=(-0.07,0.02,-0.1); b_=(0.07,0.02,-0.1); lo=lambda p:(p[0],0.0,p[2])
    Q=[quad([Wd(tip),Wd(b_),Wd(a)],CHEESE)]
    for p,q_ in ((tip,a),(a,b_),(b_,tip)): Q.append(quad([Wd(p),Wd(q_),Wd(lo(q_)),Wd(lo(p))],CRUST if (p,q_)==(a,b_) else (236,176,70)))
    Q+=box(-0.076,0.076,0.0,0.03,-0.118,-0.092,CRUST,xf=Wd)
    for x,z in ((0.0,0.03),(-0.035,-0.05),(0.035,-0.05)): Q+=box(x-0.014,x+0.014,0.02,0.027,z-0.014,z+0.014,PEPP,xf=Wd)
    return Q
def plate_quads(t_splat):
    Q=box(-0.19,0.19,0.0,0.014,-0.19,0.19,PLATE)+box(-0.15,0.15,0.014,0.018,-0.15,0.15,PLATE_D)
    c=PLATE_C
    if t_splat<=0:
        Q=transform(Q,lambda p:tuple(c+np.array(p,float)))+slice_quads(c+np.array([-0.05,0.02,0.02]),0.4)+slice_quads(c+np.array([0.06,0.02,-0.02]),-0.5)
    else:                                                                              # the slices scatter when the cat lands in them
        u=t_splat; Q=transform(Q,lambda p:tuple(c+np.array(p,float)+np.array([0.0,0.0,0.0])))
        Q+=slice_quads(c+np.array([-0.05-0.2*u,0.02+0.2*math.sin(PI*min(1,u*1.2)),0.02+0.12*u]),0.4+3*u,0.6*u)+slice_quads(c+np.array([-0.02-0.26*u,0.02+0.28*math.sin(PI*min(1,u*1.1)),-0.04-0.16*u]),-0.5-2.5*u,-0.5*u)
    return Q

# ======================= the bedroom (locked) =======================
def room():
    F=tiled_plane(-1.8,1.8,-2.9,1.3,0,0.3,lambda i,j:WOOD if (i+j)%2 else WOOD2)
    F+=box(-1.25,1.25,0.0,0.012,-2.6,-0.2,(214,110,96))+box(-1.1,1.1,0.012,0.02,-2.45,-0.35,(236,160,120))                  # rug
    B=[]; Wl=[]
    Wl+=box(-1.8,1.8,0,2.7,1.25,1.32,WALL)+box(-1.8,-1.74,0,2.7,-2.9,1.3,WALL2)+box(1.74,1.8,0,2.7,-2.9,1.3,WALL2)+box(-1.8,1.8,0,2.7,-2.96,-2.9,WALL2)
    for k in range(9): x=-1.8+0.4*k; Wl+=box(x+0.2,x+0.4,0.0,2.7,1.24,1.25,(164,134,204))                                    # stripes
    Wl+=box(-1.8,1.8,0.0,0.14,1.18,1.25,(236,226,210))
    Wl+=box(-1.0,-0.2,1.1,2.0,1.2,1.24,FRAME)+box(-0.95,-0.25,1.15,1.95,1.19,1.2,(30,40,90))                                 # poster: a tiny pixel game
    for x,y,c in ((-0.8,1.7,(255,220,80)),(-0.55,1.45,(80,220,120)),(-0.7,1.25,(230,80,90)),(-0.4,1.7,(255,255,255))): Wl+=box(x,x+0.12,y,y+0.12,1.185,1.19,c,emit=True)
    Wl+=box(1.7,1.76,0.9,2.0,-0.4,0.8,FRAME)+box(1.68,1.7,1.0,1.9,-0.3,0.7,(50,70,150),emit=True)+box(1.67,1.69,1.45,1.5,-0.3,0.7,FRAME)+box(1.67,1.69,1.0,1.9,0.38,0.42,FRAME)   # window
    Wl+=box(1.66,1.68,1.5,1.62,0.1,0.22,(250,250,220),emit=True)
    B+=box(-0.76,0.76,0.18,0.42-0.012,-1.95,0.95,(220,230,250))                                                              # mattress
    B+=box(-0.8,0.8,0.0,0.2,-1.99,1.0,FRAME)+box(-0.8,0.8,0.0,1.15,0.98,1.06,FRAME)+box(-0.84,-0.72,0.0,0.7,-1.99,-1.9,FRAME)+box(0.72,0.84,0.0,0.7,-1.99,-1.9,FRAME)
    B+=tiled_plane(-0.76,0.76,-1.95,0.95,0.409,0.19,lambda i,j:QUILT1 if (i+j)%2 else QUILT2)
    B+=box(-0.6,-0.05,0.409,0.54,0.45,0.9,PILLOW)+box(0.05,0.6,0.409,0.54,0.45,0.9,PILLOW)
    B+=box(0.9,1.4,0.0,0.5,0.4,1.0,FRAME)+box(1.0,1.3,0.5,0.54,0.55,0.85,(60,50,70))+box(1.1,1.2,0.54,0.74,0.65,0.75,(70,60,80))   # nightstand + lamp base
    B+=box(1.02,1.28,0.74,0.98,0.57,0.83,(255,214,150),emit=True)
    B+=box(-1.5,-1.1,0.0,0.34,0.4,1.0,(110,70,150))+box(-1.45,-1.15,0.34,0.4,0.45,0.95,(170,120,210))                           # beanbag
    return F,Wl,B
ROOM_F,ROOM_W,ROOM_B=room()
LIGHTS=[((1.15,0.95,0.7),(255,200,130),1.1),((-1.4,2.3,-1.6),(150,170,255),0.55),((0.0,1.7,-1.7),(255,240,225),0.6),((0.0,1.8,0.3),(255,235,210),0.35)]

# ======================= animation =======================
def search(t):
    """the rapid left-right head search of Dodge Mode"""
    ph=2*PI*(2.0*t+0.6*max(0.0,t-7.0)); return 0.15*math.sin(ph)*sm(seg01(t,T_DODGE-0.1,T_DODGE+0.15))*(1-sm(seg01(t,T_CALM,T_CALM+0.3)))
def att_info(ta,k):
    xa=search(ta+0.22); d=-1.0 if xa>=0 else 1.0
    if abs(xa)<0.03: d=1.0 if k%2 else -1.0
    return xa,max(-0.2,min(0.2,xa+d*0.22))
ATTINFO=[att_info(ta,k) for k,ta in enumerate(ATT)]
def hx_of(t):
    h=search(t)
    for (ta,(xa,dx)) in zip(ATT,ATTINFO):
        w=sm(seg01(t,ta+0.15,ta+0.25))*(1-sm(seg01(t,ta+0.48,ta+0.68))); h=lerp(h,dx,w)
    return h
def dodge_w(t): return max([sm(seg01(t,ta+0.15,ta+0.25))*(1-sm(seg01(t,ta+0.48,ta+0.68))) for ta in ATT]+[0.0])
def cat_state(t):
    hx=hx_of(t); dw=dodge_w(t)
    if t<T_CROUCH[0]:
        if t<T_BLOCK[0]+0.25: u=seg01(t,0.0,T_BLOCK[0]+0.25); zc=lerp(ZC0,ZC_STOP,sm(u)); walk=t*9.5 if u<1 else 0.0
        else: zc=ZC_STOP+0.025*math.sin(t*13)*(1-sm(seg01(t,2.6,3.0))); walk=0.0                       # pressed against the foot: bonk, bonk
        zc+=0.05*sm(seg01(t,T_DODGE,10.3))
        smug=sm(seg01(t,T_CALM-0.3,T_CALM+0.3))
        st=dict(base=(0.4*hx,CAT_Y,zc),yaw=-0.5*hx,walk=walk,hx=hx,hyaw=-1.6*hx*(0.5+0.5*dw),hroll=-1.4*hx,hpitch=0.0,lid=0.45 if t>T_DODGE else 0.15,pupil=-6*hx,tail=t*5.0,
                crouch=0.0,ears=0.1+0.5*dw,mouth=0.0,bpitch=0.0,shades=sm(seg01(t,T_SHADES,T_SHADES+0.25)))
        if t<T_BLOCK[1]+0.6 and t>=T_BLOCK[0]: st.update(hpitch=-0.15,hroll=0.15*math.sin(t*8))
        if smug>0: st.update(lid=0.5,tail=t*2.2,hroll=0.12*math.sin(t*3),hyaw=0.1*math.sin(t*2.2))
        if t>=T_NOTICE: a=sm(seg01(t,T_NOTICE,T_NOTICE+0.25)); st.update(hx=0.0,hroll=0.0,hyaw=0.0,lid=0.0,crouch=a*sm(seg01(t,T_CROUCH[0],T_CROUCH[1])),tail=t*14.0*a,ears=0.9*a,bpitch=0.0,pupil=0.0)
        return st
    zc0=ZC_STOP+0.05
    if t<T_LUNGE[1]:
        if t<T_LUNGE[0]: wig=0.012*math.sin(t*40)*seg01(t,11.6,T_LUNGE[0]); return dict(base=(wig,CAT_Y,zc0),yaw=0.0,walk=0.0,hx=0.0,hyaw=0.0,hroll=0.0,hpitch=0.05,lid=0.0,pupil=0.0,tail=t*14.0,crouch=1.0,ears=0.9,mouth=0.0,bpitch=0.08,shades=1.0)
        u=seg01(t,*T_LUNGE); zc=lerp(zc0,-0.5,sm(u))
        return dict(base=(0.0,CAT_Y+0.04*math.sin(PI*u),zc),yaw=0.0,walk=t*22,hx=0.0,hyaw=0.0,hroll=0.0,hpitch=0.1*u,lid=0.0,pupil=0.0,tail=t*10,crouch=1-u,ears=0.9,mouth=0.0,bpitch=0.25*u,shades=1.0)
    u=sm(seg01(t,*T_DIVE)); zc=lerp(-0.5,-0.43,u); tf=min(t,T_FREEZE); tn=sm(seg01(t,*T_TURN))     # face in the pizza, then he turns to the lens
    return dict(base=(0.0,CAT_Y,zc),yaw=0.0,walk=0.0,hx=0.0,hyaw=1.1*tn,hroll=0.06*math.sin(tf*30)*(1-u)+0.14*tn,hpitch=0.25*u*(1-tn)-0.3*tn,lid=0.0,pupil=0.0,tail=tf*8,crouch=0.0,ears=0.2,mouth=0.0,
                bpitch=0.25+0.3*u*(1-0.4*tn),shades=1.0,cheese=u,smug=1.0,wl=1.0-0.3*u,wu=u)
def foot_state(t):
    """(x,y,z) of her blocking foot (+x leg), base-relative; z is local (forward = -z)"""
    zl=GUARD_Z; y=GUARD_Y; gx=0.6*search(t-0.3)
    if t<T_BLOCK[0]: x,y,zl=REST_FOOT[1][0]*(1.0),REST_FOOT[1][1],REST_FOOT[1][2]; x=lerp(REST_FOOT[1][0],0.08,0.0)
    else:
        a=sm(seg01(t,*T_BLOCK))
        x=lerp(REST_FOOT[1][0],gx,a); y=lerp(REST_FOOT[1][1],GUARD_Y,a); zl=lerp(REST_FOOT[1][2],GUARD_Z,a)
    for ta,(xa,dx) in zip(ATT,ATTINFO):
        u=t-ta
        if -0.05<u<0.6:
            wind=sm(seg01(u,0,0.15))*(1-sm(seg01(u,0.15,0.2))); thr=sm(seg01(u,0.15,0.3))*(1-sm(seg01(u,0.42,0.55)))
            x=lerp(x,xa,thr); zl=zl+0.08*wind-0.12*thr; y=y+0.07*wind-0.03*thr
    if t>=T_BITE[0]+0.25:                                                                            # the tiny mistake: she relaxes her leg
        r=sm(seg01(t,T_BITE[0]+0.25,T_BITE[0]+0.6)); x=lerp(x,REST_FOOT[1][0],r); y=lerp(y,REST_FOOT[1][1],r); zl=lerp(zl,REST_FOOT[1][2],r)
    x=max(-0.16,min(0.16,x)) if t<T_BITE[0]+0.25 else x
    return (x,y,zl)
def girl_state(t):
    ft=foot_state(t); legs={-1:REST_FOOT[-1],1:ft}
    notice=sm(seg01(t,1.0,1.2)); eat=sm(seg01(t,0.0,0.45))*(1-sm(seg01(t,0.55,0.95)))
    thr=max([sm(seg01(t-ta,0.1,0.3))*(1-sm(seg01(t-ta,0.42,0.55))) for ta in ATT]+[0.0])
    mouth_=0.55*abs(math.sin(t*14)) if 0.55<t<1.0 else 0.0
    rh=(-0.24,0.93,-0.3); lh=lerp3((0.05,1.4,-0.2),(0.2,1.08,-0.2),notice)
    lh=lerp3(lh,(0.05,1.4,-0.2),eat)
    lean=-0.06*notice-0.08*thr; hp=-0.12*notice; eye=1.0+0.35*notice; smile=0.0
    if t>=T_CALM: a=sm(seg01(t,T_CALM,T_CALM+0.3)); lh=lerp3(lh,(0.06,1.3,-0.17),a); eye=lerp(eye,1.0,a); smile=0.5*a
    if t>=T_BITE[0]:                                                                               # bite! eyes shut, bliss
        b=sm(seg01(t,T_BITE[0],T_BITE[0]+0.3)); lh=lerp3(lh,(0.02,1.4,-0.2),b); eye=lerp(eye,0.12,b); smile=lerp(smile,1.0,b); hp=lerp(hp,0.12,b); lean=lerp(lean,0.04,b)
        mouth_=0.6*abs(math.sin((t-T_BITE[0])*13)) if t>T_BITE[0]+0.4 else 0.35*b
    hy=0.0
    return dict(base=GBASE,yaw=0.0,t=t,sit=1.0,rh=rh,lh=lh,hy=hy,hp=hp,eye=eye,mouth=mouth_,smile=smile,lean=lean,legs=legs,blush=1.0 if t>=T_BITE[0]+0.3 else 0.0)
def girl_model(**st): return FT.girl(**st)
def hand_world(st,side=1):
    b=np.array(st['base'],float); hip=0.82-0.34*st['sit']; piv=np.array([0,hip,0]); h=st['lh'] if side>0 else st['rh']
    p=np.array(h,float)+np.array([0,hip-0.82,0]); return b+Ry(st['yaw'])@(piv+Rx(st['lean'])@(p-piv))

# ======================= shots =======================
def shot(t):
    name=[n for a,b,n in SHOTS if a<=t<b][0]; a0=[a for a,b,n in SHOTS if a<=t<b][0]; b0=[b for a,b,n in SHOTS if a<=t<b][0]; u=seg01(t,a0,b0)
    sh=(0.0,0.0)
    if name=='hook': return dict(cam=lerp3((-0.75,0.85,-2.2),(-0.5,0.8,-1.95),u),tgt=(0.05,0.6,-0.8),fov=52)
    if name=='faceR': return dict(cam=(0.24-0.03*u,0.98,-0.24),tgt=(0.0,0.66,-0.95),fov=50)
    if name=='faceL': return dict(cam=(-0.24+0.03*u,0.98,-0.24),tgt=(0.0,0.66,-0.95),fov=50)
    if name=='wideL': return dict(cam=lerp3((-1.5,1.3,-1.1),(-1.4,1.25,-1.0),u),tgt=(0.0,0.7,-0.3),fov=54)
    if name=='wideR': return dict(cam=lerp3((1.5,1.3,-1.1),(1.4,1.25,-1.0),u),tgt=(0.0,0.7,-0.3),fov=54)
    if name=='over': return dict(cam=lerp3((0.40,0.88,-2.05),(0.30,0.86,-1.95),u),tgt=(0.0,0.7,-0.5),fov=46)
    if name=='overL': return dict(cam=lerp3((-0.4,0.8,-1.9),(-0.3,0.78,-1.8),u),tgt=(0.0,0.7,-0.5),fov=46)
    return dict(cam=lerp3((0.85,0.95,0.3),(0.74,0.88,0.25),sm(seg01(t,12.9,DUR))),tgt=(0.0,0.66,-0.14),fov=36)

# ======================= render =======================
R=Renderer(W,H,fog=(40,30,60))
def render(t,sh,T):
    cam=Camera.look(sh['cam'],sh['tgt']); cp=np.array(sh['cam'])
    gs=girl_state(T); gq,gd=girl_model(**gs); cs=cat_state(T); cq,cd=cat_model(**cs)
    gd=[x for x in gd if np.linalg.norm(x['c']-cp)<np.linalg.norm(x['hc']-cp)]; cd=[x for x in cd if np.linalg.norm(x['c']-cp)<np.linalg.norm(x['hc']-cp)]
    hand=hand_world(gs,1); held=slice_quads(hand+np.array([0.0,-0.02,0.04]),0.0,-0.25) if T<T_BITE[0]+0.6 or True else []
    plate=plate_quads(seg01(T,T_DIVE[0]+0.25,T_FREEZE+0.1) if T>=T_DIVE[0]+0.25 else 0.0)
    chars=[gq,gd,cq,cd,held]
    layers=[ROOM_F,ROOM_W,ROOM_B,plate]+chars
    bias=[1.0]*4+[1.0,1.004,1.0,1.004,1.0]
    img,vi=zrender(R,cam,layers,LIGHTS,fov=sh['fov'],fog_start=14,fog_end=40,ambient=0.5,shake=sh.get('shake',(0,0)),bias=bias)
    return post.ps1(img),vi,gs,cs

# ======================= UI (2D overlays) =======================
def otext(d,s,x,y,col,sc=1): FT.otext(d,s,x,y,col,sc)
def ctext(d,s,y,col,sc=1): otext(d,s,(W-font.width(s,sc))//2,y,col,sc)
def panel(d,x0,y0,x1,y1,col,bg=(12,10,30)): d.rectangle([x0,y0,x1,y1],fill=bg,outline=col)
HOOK_CHUNKS=['WHY DO CATS','DODGE FOOD','GUARDS BETTER','THAN VIDEO','GAME BOSSES?']; HIL={'CATS','BOSSES?','DODGE'}
def hook_text(d,t):
    D=SCR['dur']['N1']; w=[len(c) for c in HOOK_CHUNKS]; edges=np.concatenate([[0.05],0.05+D*np.cumsum(w)/sum(w)]); edges[-1]=HOOK+0.2
    for i,c in enumerate(HOOK_CHUNKS):
        if edges[i]<=t<edges[i+1]:
            x=(W-font.width(c,2))//2
            for wd in c.split(' '): otext(d,wd,x,14,YEL if wd in HIL else WHT,2); x+=font.width(wd,2)+12
def banners(d,vi,t,gs,cs):
    if T_DODGE+0.05<=t<T_DODGE+2.0:
        a=sm(seg01(t,T_DODGE+0.05,T_DODGE+0.2)); c=CYAN if int(t*8)%2 else YEL; y=int(lerp(-30,16,a))
        panel(d,26,y-4,154,y+36,c,(12,10,30)); ctext(d,'DODGE MODE',y+2,c,2); ctext(d,'ACTIVATED',y+20,WHT,2)
    if T_DODGE<=t<T_WIN+1.7 and not (T_WIN<=t):                                    # the boss bar of the cat
        a=sm(seg01(t,T_DODGE,T_DODGE+0.3)); y=int(lerp(340,286,a)); otext(d,'CAT',8,y,RED); otext(d,'LV 99',W-8-font.width('LV 99'),y,YEL); ctext(d,'DODGE 100%',y,CYAN)
        d.rectangle([7,y+10,W-7,y+18],fill=(0,0,0),outline=(230,190,90)); d.rectangle([9,y+12,W-9,y+16],fill=RED); d.rectangle([9,y+12,W-9,y+13],fill=(255,140,120))
    for ta in MISS_AT:
        if ta+0.3<=t<ta+1.0:
            ft=foot_state(ta+0.3); p=R.project(tuple(np.array(GBASE)+np.array([ft[0],ft[1]+0.15,ft[2]])),vi); k=seg01(t,ta+0.3,ta+1.0)
            x=int(max(8,min(W-8-font.width('MISS',3),(p[0] if p else W/2)-font.width('MISS',3)/2))); y=int(max(60,min(220,(p[1] if p else 120)-24-24*k)))
            otext(d,'MISS',x,y,RED if int(t*10)%2 else (255,130,110),3)
    if T_NOTICE<=t<T_NOTICE+0.7:
        p=R.project(tuple(np.array(head_world(cs))+np.array([0,0.25,0])),vi)
        if p: x,y=int(p[0]),int(p[1]); d.rectangle([x-6,y-10,x+6,y+8],fill=WHT,outline=(0,0,0)); d.polygon([(x-2,y+8),(x+2,y+8),(x,y+11)],fill=WHT); font.text(d,'!',x-2,y-7,RED,1,None)
    if t>=T_WIN:
        a=sm(seg01(t,T_WIN,T_WIN+0.12)); c=YEL if int(t*8)%2 else WHT; y=int(lerp(100,92,a))
        panel(d,14,y-6,166,y+28,c,(30,22,6)); ctext(d,'CAT WINS',y,c,3)
        ctext(d,'+1 PIZZA',y+36,GRN,1) if False else otext(d,'+1 PIZZA',(W-font.width('+1 PIZZA',1))//2,y+34,GRN,1)
def frame(t):
    T=min(t,T_FREEZE); sh=shot(t); img,vi,gs,cs=render(t,sh,T); d=ImageDraw.Draw(img)
    if t<HOOK: hook_text(d,t)
    banners(d,vi,t,gs,cs)
    return img

# ======================= QA manifest (tools/qa/scene_qa.py, PIPELINE.md) =======================
def _cat(t): return cat_state(min(t,T_FREEZE))
def _girl(t): return girl_state(min(t,T_FREEZE))
def _cat_model(**st): return cat_model(**st)[0]
def _girl_model(**st): return girl_model(**st)[0]
def _extra(t):
    out=[]; T=min(t,T_FREEZE); cs=cat_state(T); gs=girl_state(T); ft=np.array(gs['legs'][1]); hp=np.array(GBASE)
    d_hip=np.linalg.norm(ft-np.array([0.09,0.48,0.0]))
    if d_hip>0.97: out.append(('stretch',f'her leg is stretched ({d_hip:.2f} m)'))
    if ft[1]<0.45: out.append(('floor','her foot is under the bed surface'))
    hw=head_world(cs); fw=np.array(GBASE)+ft
    if abs(hw[0]-fw[0])<0.12+0.06-0.0 and abs(hw[2]-(fw[2]-0.035))<0.14 and abs(hw[1]-fw[1])<0.1 and T<T_BITE[0]: out.append(('intersect',f'her foot touches the cat head (dx {abs(hw[0]-fw[0]):.2f} m)'))
    if cs['base'][0]!=cs['base'][0]: out.append(('nan','cat'))
    return out
QA=dict(fps=FPS,dur=DUR,W=W,frame=frame,
    chars={'cat':(_cat,_cat_model,'_none',1.0),'woman':(_girl,_girl_model,'_none',1.0)},
    geom=lambda t,name,st,V: [('floor',f'{name} under the floor')] if V[:,1].min()<-0.04 else [],
    extra=_extra,camera=lambda t: shot(t)['cam'],min_cam_dist=0.3,camera_ok=lambda p: p[1]>0.12 and abs(p[0])<1.65 and -2.85<p[2]<1.2,
    scenes=[dict(id=f'{n}-{int(a*10)}',t0=a,t1=b,action=act) for (a,b,n),act in zip(SHOTS,[
        'woman eats on the bed; the cat walks up to the pizza; her foot blocks it','dodge mode: cat head left/right, foot attempt 1','wide: foot attempt 2, the cat dodges',
        'over the cat: attempt 3','boss face: attempt 4','over the cat (low): attempt 5 MISS','boss face: attempt 6 MISS','wide: attempt 7 MISS',
        'she takes a bite, eyes shut, leg relaxes','cat notices and crouches','cat runs to the plate','CAT WINS: face in the pizza, freeze'])],
    weapon_events=[],
    texts=lambda: [('hook',c,2) for c in HOOK_CHUNKS]+[('ui',s_,1) for s_ in ('DODGE MODE','ACTIVATED','CAT','LV 99','DODGE 100%','+1 PIZZA','!')]+[('ui','MISS',3),('ui','CAT WINS',3)])

TEST=os.environ.get('TEST')
if TEST and __name__=='__main__':
    ims=[frame(float(x)) for x in TEST.split(',')]; shp=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): shp.paste(im,(i*182,0))
    shp.resize((shp.width*2,640),Image.NEAREST).save('test.png'); sys.exit()


# ======================= AUDIO (same synth palette as the other shorts) =======================
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=23); sr=s.sr; n=s.n; M=np.zeros(n); AMB=np.zeros(n)
    def note(buf,t0,m,d,v,wave='sq',duty=0.5,dec=3.0,att=0.005):
        f=440*2**((m-69)/12); tt=s.T(d); ph=(f*tt)%1
        x=np.where(ph<duty,1.0,-1.0) if wave=='sq' else (4*np.abs(ph-0.5)-1 if wave=='tri' else np.sin(2*np.pi*ph))
        env=np.minimum(1,tt/att)*np.exp(-tt*dec); i=int(t0*sr); j=min(n,i+len(tt)); buf[i:j]+=(x*env*v)[:j-i]
    def nb(t0,d,lo,hi,v,seed,shape=2): s.place(s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v)
    def thud(t0,f=55,v=0.25,d=0.5): tt=s.T(d); s.place(np.sin(2*np.pi*f*tt*(1-0.35*tt/d))*np.exp(-tt*9)+s.filt_short(s.noise(d,int(t0*13)),lo=50,hi=600)*np.exp(-tt*12)*0.5,t0,v)
    def whoosh(t0,d=0.4,v=0.05,seed=0,lo=300,hi=3500): nb(t0,d,lo,hi,v,seed)
    def tick(t0,v=0.03,f=2300): tt=s.T(0.03); s.place(np.sin(2*np.pi*f*tt)*np.exp(-tt*120),t0,v)
    def zip_(t0,v=0.05,f0=500,f1=2400,d=0.13): tt=s.T(d); s.place(np.sin(2*np.pi*np.cumsum(f0+(f1-f0)*tt/d)/sr)*np.exp(-tt*14)*np.minimum(1,tt/0.004),t0,v)
    def pad(t0,v=0.035,seed=0): thud(t0,90,v,0.15); nb(t0,0.06,1500,6000,v*0.3,seed,1)                   # soft paw step
    def crunch(t0,v=0.12,seed=0):
        for k in range(3): tt=s.T(0.06); s.place(s.filt_short(s.noise(0.06,seed*9+k),lo=1500,hi=5500)*np.exp(-tt*45),t0+k*0.05,v)
        nb(t0,0.12,200,1200,v*0.4,seed*5)
    def chime(t0,notes,v=0.04,step=0.07,d=0.3):
        for k,m in enumerate(notes): note(M,t0+k*step,m,d,v,'sq',0.25,6)
    def meow(t0,d=0.55,v=0.2,f=620):
        tt=s.T(d); fr=f*(1+0.55*np.sin(np.pi*tt/d)-0.25*tt/d)*(1+0.012*np.sin(2*np.pi*7*tt)); ph=np.cumsum(fr)/sr
        x=np.sin(2*np.pi*ph)+0.6*np.sin(4*np.pi*ph)+0.35*np.sin(6*np.pi*ph)+0.2*np.sin(8*np.pi*ph)
        s.place(s.filt_short(x,lo=300,hi=3800)*np.sin(np.pi*tt/d)**0.7,t0,v)
    def purr(t0,d,v=0.05):
        tt=s.T(d); s.place(s.filt_short(s.noise(d,31),lo=40,hi=220)*(0.5+0.5*np.sign(np.sin(2*np.pi*24*tt)))*np.sin(np.pi*tt/d)**0.5,t0,v)
    def sneaky(a,b,v=1.0,step=0.2,tense=0.0):
        bass=[45,45,52,45,48,48,52,48]; mel=[69,0,72,0,76,72,0,69,67,0,69,0,72,0,64,0]; k=0; tc=a
        while tc<b-1e-6:
            if k%2==0: note(M,tc,bass[(k//2)%8],step*1.5,0.06*v,'tri',dec=7)
            if mel[k%16]: note(M,tc,mel[k%16]+12*(1 if tense else 0),step*0.6,0.018*v,'sq',0.25,10)
            if tense and k%4==2: nb(tc,0.05,2000,8000,0.025*v,int(tc*100)+3,1)                                  # tiny snare tick
            k+=1; tc+=step
    AMB+=s.filt(s.rng.normal(0,1,n),lo=80,hi=800)*0.008                                                   # room tone
    # ---------- music ----------
    sneaky(0.05,T_DODGE,0.8,step=0.22)
    sneaky(T_DODGE,T_CALM,1.1,step=0.16,tense=1.0)
    sneaky(T_CALM,T_BITE[0]+0.2,0.5,step=0.24)
    for k,m in enumerate((81,84,88,93,88,84)): note(M,T_BITE[0]+0.2+k*0.1,m,0.2,0.022,'sq',0.25,6)             # yum arpeggio
    for k in range(int((T_CROUCH[1]-T_NOTICE)/0.1)): note(M,T_NOTICE+k*0.1,33+(k%2),0.12,0.03+0.0015*k,'tri',dec=5)       # tension tremolo
    for k,m in enumerate((57,60,64,67,69,72,76,79,81,84,88)): note(M,T_LUNGE[0]+k*0.06,m,0.12,0.03,'sq',0.25,8)       # run-up
    # ---------- sfx ----------
    for k in range(10): pad(0.1+k*0.12,0.03,k)                                                          # paws padding in
    for t0 in (0.6,0.78,0.95): crunch(t0,0.1,int(t0*10))                                               # she is eating
    note(M,1.05,88,0.1,0.04,'sq',0.25,10); note(M,1.12,91,0.12,0.04,'sq',0.25,10)                       # '!' she notices
    whoosh(T_BLOCK[0]+0.05,0.25,0.05,5); thud(T_BLOCK[1],70,0.12,0.2); note(M,T_BLOCK[1]+0.03,60,0.12,0.05,'sq',0.5,10)      # the foot blocks
    for k,t0 in enumerate((1.65,1.95,2.3)): tick(t0,0.02); thud(t0,100,0.05,0.12)                         # cat bonks the foot
    chime(T_DODGE+0.05,(72,76,79,84,88),0.04,0.06)                                                       # DODGE MODE ACTIVATED
    tt=s.T(0.5); s.place(np.sin(2*np.pi*55*tt)*np.exp(-tt*5)+0.5*np.sin(2*np.pi*110*tt)*np.exp(-tt*6),T_DODGE+0.05,0.12)
    for k,f in enumerate((3000,3900,4800)): tt=s.T(0.5); s.place(np.sin(2*np.pi*f*tt)*np.exp(-tt*7),T_SHADES+0.2+k*0.06,0.025)    # shades ping
    for ta in ATT:
        whoosh(ta+0.1,0.28,0.06,int(ta*10),500,5000); zip_(ta+0.17,0.05)                                  # foot thrust, head dodge
        for k,t0 in enumerate((ta+0.26,ta+0.55)): tick(t0,0.02,3000-300*k)
    for t0 in np.arange(T_DODGE+0.2,T_CALM,0.25): tick(t0,0.008,1500)                                    # fast head-search ticks
    for ta in MISS_AT:
        note(M,ta+0.3,67,0.14,0.07,'sq',0.5,6); note(M,ta+0.44,60,0.3,0.07,'sq',0.5,4)                    # MISS: bwomp
    # the mistake
    crunch(T_BITE[0]+0.1,0.14,77)
    for t0 in (11.0,11.18,11.36): crunch(t0,0.07,int(t0*7))
    tt=s.T(0.4); s.place(np.sin(2*np.pi*np.cumsum(260+60*np.sin(2*np.pi*3*tt))/sr)*np.sin(np.pi*tt/0.4)**1.5,10.95,0.03)       # 'mmm'
    thud(T_BITE[0]+0.45,80,0.07,0.15)                                                                      # her leg drops
    note(M,T_NOTICE,91,0.1,0.05,'sq',0.25,10); note(M,T_NOTICE+0.1,96,0.14,0.05,'sq',0.25,10)             # cat notices
    purr(T_NOTICE,T_CROUCH[1]-T_NOTICE,0.07); nb(T_CROUCH[0]+0.3,0.3,2000,7000,0.015,41,1)
    whoosh(T_LUNGE[0],0.5,0.07,43,300,4000)
    for k in range(10): pad(T_LUNGE[0]+0.04+k*0.07,0.03,60+k)
    # splat + the win
    thud(T_DIVE[0]+0.25,60,0.3,0.4); nb(T_DIVE[0]+0.25,0.25,200,2500,0.1,47); crunch(T_DIVE[0]+0.3,0.12,48)
    tt=s.T(0.3); s.place(np.sin(2*np.pi*np.cumsum(300+500*tt/0.3)/sr)*np.exp(-tt*10),T_DIVE[0]+0.3,0.05)  # boing
    M[int(T_FREEZE*sr):int(T_WIN*sr)]=0
    for k,m in enumerate((67,72,76,84)): note(M,T_WIN+k*0.09,m,0.3,0.06,'sq',0.5,4)                       # victory sting
    for f_ in (261.6,329.6,392.0,523.3): note(M,T_WIN+0.4,69+12*math.log2(f_/440),1.3,0.04,'sq',0.25,2.0)
    meow(T_WIN+0.05,0.5,0.22,640); tick(T_WIN+0.62,0.05,4200)
    for k,f in enumerate((3200,4200,5200)): tt=s.T(0.7); s.place(np.sin(2*np.pi*f*tt)*np.exp(-tt*6),T_WIN+0.5+k*0.07,0.025)
    # ---------- voice ----------
    NB=np.zeros(n); duck=np.ones(n)
    a,ar=_sf.read(os.path.join(TTS_DIR,'cd','N1.wav')); a=a if a.ndim==1 else a.mean(1)
    a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a); act=a[np.abs(a)>0.02]; a=a/(np.sqrt((act**2).mean())+1e-9)*0.2
    i=int(0.05*sr); j=min(n,i+len(a)); NB[i:j]+=a[:j-i]; duck[max(0,i-int(0.05*sr)):min(n,j+int(0.1*sr))]=0.4
    duck=np.convolve(duck,np.ones(2400)/2400,'same')
    s.L+=2.0*M*duck+AMB; s.R+=2.0*np.roll(M,240)*duck+np.roll(AMB,700)
    s.reverb(0.12,length=1.0,decay=4.0)
    pk=max(np.abs(s.L).max(),np.abs(s.R).max()); gv=pk*1.05/np.abs(NB).max()
    s.L=s.L*(0.6+0.4*duck)+NB*gv; s.R=s.R*(0.6+0.4*duck)+NB*gv
    st=np.stack([s.L,s.R],1); k=int(0.25*sr); st[-k:]*=np.linspace(1,0,k)[:,None]
    st=st/np.max(np.abs(st))*0.9; _sf.write(path,st,sr,subtype='PCM_16'); return path
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'cat_dodge.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'cd_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.96,vignette=0.22,grain=1.5,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(post.upscale(frame(f/FPS),S),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
