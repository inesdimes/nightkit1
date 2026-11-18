"""THE SMALLEST UMBRELLA - "He had the world's smallest umbrella... but he still wanted to share."  PS1 wholesome short, 9:16, 15 s. Fully procedural (nightkit).
LOCKED ASSETS: the duckling (duckling()), the dog (dog()), the miniature red umbrella (umbrella_quads), the rainy cobblestone street at dusk (street()).
One fixed camera side (from -z). All text (subtitles) and the rain streaks are 2D overlays. Voice: python tools/tts/um.py -> $TTS_DIR/um/N1..N3.wav (warm female narrator).
Run: TEST=0.5,5,12 python examples/umbrella.py -> test.png | SHOT=a:b TEST=.. | PART=a:b | PART=audio | QA: python tools/qa/scene_qa.py examples/umbrella.py"""
import os, sys, math, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, box, quad, transform, tiled_plane
from nightkit import post, font
from nightkit.zraster import zrender
from nightkit.audio import Sound
_T=os.environ.pop('TEST',None)                      # face_track (imported by cat_dodge) has its own TEST hook at import time
import cat_dodge as CD
if _T is not None: os.environ['TEST']=_T
FT=CD.FT
sm,seg01,lerp3,seg,tag,Rx,Ry,Rz=FT.sm,FT.seg01,FT.lerp3,FT.seg,FT.tag,FT.Rx,FT.Ry,FT.Rz
PI=math.pi
def lerp(a,b,u): return a+(b-a)*u
TTS_DIR=CD.TTS_DIR; OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6; DUR=15.0; N=int(round(DUR*FPS))
SCR=json.load(open(os.path.join(TTS_DIR,'um','script.json')))

# ======================= palette =======================
DUCK=(255,224,70); DUCK_D=(236,196,44); BEAK=(255,136,28); BLK=(20,16,20); WHT=(244,240,228)
DOG=(122,80,48); DOG_D=(98,64,38); DOG_T=(170,120,78); DOG_L=(142,98,62); EAR=(84,52,32); NOSE=(26,22,26); PINK=(240,130,150)
UMB=(212,36,46); UMB2=(238,72,72); UMB_IN=(138,22,32); POLE=(78,56,44); GOLD=(236,196,84)
DROP=(170,205,255)

# ======================= timeline (seconds) =======================
X_DOG=0.45                                         # the dog's body centre (x), it faces -x
T_NOTICE=(0.7,1.3); T_WALK_DUCK=(1.9,3.6); T_RAISE=(3.4,4.4); T_HEADDOWN=(4.4,5.4); T_APPROACH=(6.0,8.4)
T_LIE=(10.7,11.4); T_CLIMB=(10.8,11.95); T_RISE=(11.9,12.5); T_WALK=12.5; T_CUT=12.1; T_ZOOM=(12.1,14.8)
BLINKS=[1.2,6.2,10.3]
DUCK_R=0.21; UP_LEN=0.36

# ======================= LOCKED ASSET: the dog =======================
POSE={
 'sit':  dict(fsh=0.12,R=(0,0.24,-0.34),F=(0,0.80,0.10),Hc=(0,1.07,0.36),hp=0.0, fp=((-0.13,0.0,0.22),(0.13,0.0,0.22)),hk=((-0.20,0.20,0.02),(0.20,0.20,0.02)),hpw=((-0.15,0.0,0.10),(0.15,0.0,0.10)),tail=(0,0.05,-0.80),ear=0.0),
 'head': dict(fsh=0.12,R=(0,0.24,-0.34),F=(0,0.80,0.10),Hc=(0,0.47,0.40),hp=0.5, fp=((-0.13,0.0,0.22),(0.13,0.0,0.22)),hk=((-0.20,0.20,0.02),(0.20,0.20,0.02)),hpw=((-0.15,0.0,0.10),(0.15,0.0,0.10)),tail=(0,0.05,-0.80),ear=0.0),
 'bow':  dict(fsh=0.18,R=(0,0.30,-0.34),F=(0,0.38,0.18),Hc=(0,0.36,0.46),hp=0.25,fp=((-0.22,0.04,0.55),(0.22,0.04,0.55)),hk=((-0.20,0.20,0.02),(0.20,0.20,0.02)),hpw=((-0.15,0.0,0.10),(0.15,0.0,0.10)),tail=(0,0.05,-0.80),ear=0.2),
 'lie':  dict(fsh=0.25,R=(0,0.22,-0.40),F=(0,0.27,0.12),Hc=(0,0.30,0.52),hp=0.2, fp=((-0.30,0.06,0.70),(0.30,0.06,0.70)),hk=((-0.24,0.12,-0.10),(0.24,0.12,-0.10)),hpw=((-0.22,0.0,-0.55),(0.22,0.0,-0.55)),tail=(0,0.06,-0.90),ear=0.1),
 'stand':dict(fsh=0.12,R=(0,0.64,-0.36),F=(0,0.68,0.22),Hc=(0,0.62,0.36),hp=0.6, fp=((-0.12,0.0,0.22),(0.12,0.0,0.22)),hk=((-0.15,0.30,-0.46),(0.15,0.30,-0.46)),hpw=((-0.12,0.0,-0.34),(0.12,0.0,-0.34)),tail=(0,0.88,-0.72),ear=0.0)}
def mix(a,b,u):
    if isinstance(a,dict): return {k:mix(a[k],b[k],u) for k in a}
    if isinstance(a,(tuple,list)): return tuple(mix(x,y,u) for x,y in zip(a,b))
    return a+(b-a)*u
def perch(P):
    """where the duckling stands on the dog's back (dog-local coords)"""
    R=np.array(P['R']); F=np.array(P['F']); al=(F-R); al/=np.linalg.norm(al); n=np.array([0,al[2],-al[1]])
    return F+n*0.172+al*0.06
def dog(base,yaw,P,walk=0.0,wag=0.0,lid=0.3,smile=0.0,hroll=0.0,hyaw=0.0,earsw=0.0,t=0.0,dry_nose=False,shade=0.0,**_):
    """big friendly wet brown dog, local forward +z. P: pose dict (see POSE). returns (quads, face decals)"""
    b=np.array(base,float); Rb=Ry(yaw)
    def Wd(p): return tuple(b+Rb@np.array(p,float))
    k=1-0.4*shade; c=lambda col: tuple(int(v*k) for v in col)
    R_=np.array(P['R'],float); F_=np.array(P['F'],float); Hc=np.array(P['Hc'],float); hp=P['hp']
    Q=[]; D=[]; bob=0.012*math.sin(2*walk) if walk else 0.0
    R_[1]+=bob; F_[1]+=bob; Hc[1]+=bob*1.2
    Q+=transform(seg(tuple(R_),tuple(F_),0.40,c(DOG),0.34)+seg((0,R_[1]+0.02,R_[2]+0.05),(0,F_[1]-0.02,F_[2]-0.05),0.42,c(DOG_D),0.36),Wd)         # torso (darker wet belly line under it)
    for sx in (-1,1):                                                                                                                          # front legs
        pw=np.array(P['fp'][0 if sx<0 else 1],float); ph=0.0
        if walk: ph=walk+(0.0 if sx>0 else PI); pw[2]+=0.14*math.sin(ph); pw[1]+=0.07*max(0.0,math.cos(ph))
        top=(sx*P['fsh'],F_[1]-0.12,F_[2]-0.02); Q+=transform(seg(top,(pw[0],pw[1]+0.06,pw[2]),0.13,c(DOG),0.13)+box(pw[0]-0.075,pw[0]+0.075,pw[1],pw[1]+0.07,pw[2]-0.07,pw[2]+0.09,c(DOG_L)),Wd)
        pw=np.array(P['hpw'][0 if sx<0 else 1],float); kn=np.array(P['hk'][0 if sx<0 else 1],float)                                              # hind legs
        if walk: ph=walk+(PI if sx>0 else 0.0); pw[2]+=0.14*math.sin(ph); pw[1]+=0.07*max(0.0,math.cos(ph)); kn[2]+=0.07*math.sin(ph)
        hip=(sx*0.16,R_[1]-0.02,R_[2]+0.06)
        Q+=transform(seg(hip,tuple(kn),0.15,c(DOG),0.15)+seg(tuple(kn),(pw[0],pw[1]+0.06,pw[2]),0.12,c(DOG),0.12)+box(pw[0]-0.07,pw[0]+0.07,pw[1],pw[1]+0.07,pw[2]-0.07,pw[2]+0.09,c(DOG_L)),Wd)
    tip=np.array(P['tail'],float); tip[0]+=wag*0.16
    Q+=transform(seg((0,R_[1]+0.05,R_[2]-0.1),tuple(tip),0.09,c(DOG_D),0.09),Wd)
    Q+=transform(seg((0,F_[1]+0.02,F_[2]+0.02),(Hc[0],Hc[1]-0.1,Hc[2]-0.14),0.27,c(DOG),0.27),Wd)                                                  # neck
    Rh=Rz(hroll)@Ry(hyaw)@Rx(hp)
    def Hd(p): p=np.array(p,float); return Wd(Hc+Rh@p)
    Q+=box(-0.17,0.17,-0.15,0.13,-0.2,0.14,c(DOG),xf=Hd)+box(-0.095,0.095,-0.14,0.0,0.14,0.32,c(DOG_T),xf=Hd)+box(-0.07,0.07,-0.05,0.03,0.32,0.37,c(NOSE),xf=Hd)
    D+=box(-0.02,0.02,0.0,0.014,0.361,0.363,(255,255,255),xf=Hd)                                                                                # nose shine
    for sx in (-1,1):
        def Ed(p,sx=sx): p=np.array(p,float); A=np.array([sx*0.17,0.1,-0.02]); sw=P['ear']+earsw+0.12; return Hd(A+Rz(sx*sw)@p)
        Q+=box(0.0 if sx>0 else -0.045,0.045 if sx>0 else 0.0,-0.30,0.0,-0.12,0.06,c(EAR),xf=Ed)                                              # floppy ears
        for z0,z1,y0,y1,col in ((0.05,0.125,0.0,0.07,BLK),):
            D+=box(sx*0.1715-0.0007,sx*0.1715+0.0007,y0,y1,z0,z1,col,xf=Hd)
            D+=box(sx*0.1722-0.0007,sx*0.1722+0.0007,y1-0.025,y1-0.01,z1-0.03,z1-0.012,(255,255,255),xf=Hd)
            if lid>0: D+=box(sx*0.1725-0.0007,sx*0.1725+0.0007,y1-0.07*lid,y1+0.002,z0-0.003,z1+0.003,c(DOG),xf=Hd)                              # sleepy / happy lid
        D+=box(sx*0.1-0.03,sx*0.1+0.03,0.0,0.07,0.1405,0.1415,BLK,xf=Hd)+box(sx*0.1+0.006,sx*0.1+0.022,0.045,0.06,0.1415,0.1425,(255,255,255),xf=Hd)
        if lid>0: D+=box(sx*0.1-0.031,sx*0.1+0.031,0.07-0.07*lid,0.071,0.1418,0.1428,c(DOG),xf=Hd)
    if smile>0.05: D+=box(-0.075,0.075,-0.12,-0.108,0.2,0.2012,BLK,xf=Hd)+box(-0.03,0.03,-0.14,-0.108,0.2,0.2012,PINK,xf=Hd)                      # happy mouth + tongue
    if not dry_nose and t>0:                                                                                                                  # rain drips from nose and ears
        for kk in range(5):
            ph=(t*1.3+kk*0.37)%1.0; src=[(0,-0.04,0.34),(-0.17,-0.28,0.0),(0.17,-0.28,0.0),(0,-0.14,0.2),(-0.1,-0.1,0.3)][kk]
            Q+=box(-0.009,0.009,-0.02-0.3*ph*ph,0.01-0.3*ph*ph,-0.009,0.009,DROP,xf=lambda p,s=src: Hd(np.array(s)+np.array(p)),emit=True)
    tag(D,Wd(Hc)); return Q,D

# ======================= LOCKED ASSET: the duckling + the miniature red umbrella =======================
def umbrella_quads(grip,ut,ulen,Wd,shade=0.0):
    """miniature red umbrella: pole from the grip, 8-panel canopy. all local to the duckling"""
    u=Rx(ut)@np.array([0,1.0,0]); e1=np.array([1.0,0,0]); e2=np.cross(u,e1); G=np.array(grip,float); C=G+u*ulen
    Q=transform(seg(tuple(G),tuple(C),0.012,POLE,0.012),Wd)
    rim=[C-u*0.03+DUCK_R*(math.cos(a)*e1+math.sin(a)*e2) for a in np.linspace(0,2*PI,9)[:-1]]
    ap=C+u*0.085; ai=C+u*0.045
    for kk in range(8):
        a,b_=rim[kk],rim[(kk+1)%8]
        Q.append(quad([Wd(ap),Wd(a),Wd(b_)],UMB if kk%2 else UMB2)); Q.append(quad([Wd(ai),Wd(b_),Wd(a)],UMB_IN))
    Q+=box(-0.012,0.012,0.0,0.03,-0.012,0.012,GOLD,xf=lambda p: Wd(ap+np.array(p)))
    return Q
def duckling(base,yaw,walk=0.0,flap=0.0,hp=0.0,hy=0.0,ut=0.0,ulen=UP_LEN,blink=False,beak=0.0,squash=0.0,shade=0.0,**_):
    """tiny bright-yellow duckling, local forward +z. returns (body quads, face decals, umbrella quads)"""
    b=np.array(base,float); Rb=Ry(yaw); k=1-0.3*shade; c=lambda col: tuple(int(v*k) for v in col)
    def Wd(p): return tuple(b+Rb@np.array(p,float))
    Q=[]; D=[]; bob=0.006*abs(math.sin(walk)) if walk else 0.0; sq=1-0.12*squash
    for sx in (-1,1):
        ph=walk+(0.0 if sx>0 else PI); dz=0.02*math.sin(ph) if walk else 0.0; lf=0.012*max(0.0,math.cos(ph)) if walk else 0.0
        Q+=transform(seg((sx*0.022,0.045,0.0),(sx*0.022,0.008+lf,dz),0.012,c(BEAK),0.012)+box(sx*0.022-0.018,sx*0.022+0.018,lf,lf+0.008,dz-0.012,dz+0.045,c(BEAK)),Wd)
    Q+=box(-0.045,0.045,0.04+bob,0.04+bob+0.075*sq,-0.055,0.05,c(DUCK),xf=Wd)+box(-0.036,0.036,0.04+bob+0.075*sq,0.04+bob+0.09*sq,-0.045,0.04,c(DUCK),xf=Wd)+box(-0.012,0.012,0.09+bob,0.12+bob,-0.075,-0.055,c(DUCK_D),xf=Wd)
    sxh=1 if math.sin(yaw)>=0 else -1; gp=np.array([0.07*math.sin(yaw),0.075+bob,0.03])
    for sx in (-1,1):                                                                                                                       # wings
        S=np.array([sx*0.047,0.105+bob,0.0])
        if sx==sxh: Q+=transform(seg(tuple(S),tuple(gp),0.014,c(DUCK_D),0.034),Wd); continue                                             # the near wing holds the umbrella pole
        f=max(flap,0.15)
        Q+=box(-0.006,0.006,-0.05,0.0,-0.03,0.03,c(DUCK_D),xf=lambda p,S=S,sx=sx,f=f: Wd(S+Rz(sx*f)@np.array(p)))
    HC=np.array([0,0.15+bob,0.04]); Rh=Ry(hy)@Rx(hp)
    def Hd(p): p=np.array(p,float); return Wd(HC+Rh@p)
    Q+=box(-0.042,0.042,-0.04,0.045,-0.04,0.045,c(DUCK),xf=Hd)+box(-0.016,0.016,-0.012,0.006,0.045,0.085,c(BEAK),xf=Hd)
    if beak>0: Q+=box(-0.013,0.013,-0.012-0.012*beak,-0.004-0.012*beak,0.045,0.07,c(BEAK),xf=Hd)
    for sx in (-1,1):
        h=0.003 if blink else 0.009
        D+=box(sx*0.0425-0.0005,sx*0.0425+0.0005,0.018-h,0.018+h,0.012,0.03,BLK,xf=Hd)+box(sx*0.026,sx*0.04,0.018-h,0.018+h,0.0455,0.0465,BLK,xf=Hd)
    tag(D,Wd(HC))
    side=math.sin(yaw); grip=(0.07*side,0.075+bob,0.03)
    U=umbrella_quads(grip,ut,ulen,Wd)
    return Q,D,U

# ======================= LOCKED ENVIRONMENT: the rainy cobblestone street at dusk =======================
STONE=[(86,90,108),(74,78,96),(98,100,116),(68,72,90)]
def street():
    F=tiled_plane(-5.5,3.2,-1.7,1.3,0,0.15,lambda i,j:STONE[((i*73856093)^(j*19349663))%4])+tiled_plane(-5.5,3.2,-5.0,-1.7,0,0.3,lambda i,j:STONE[((i*73856093)^(j*19349663))%4])
    Bd=[]; rng=np.random.default_rng(4)
    Bd+=box(-5.5,3.2,0,0.12,1.3,1.45,(120,118,134))+box(-5.5,3.2,0,0.1,1.45,2.0,(104,102,120))
    for x0,x1,h,col in ((-5.5,-3.8,3.0,(112,86,108)),(-3.8,-2.2,2.5,(92,98,138)),(-2.2,-0.4,3.2,(124,100,94)),(-0.4,1.3,2.6,(86,94,128)),(1.3,3.2,3.0,(108,90,120))):
        Bd+=box(x0,x1,0,h,2.0,2.7,col)
        for xx in np.arange(x0+0.25,x1-0.3,0.45):
            for yy in np.arange(0.6,h-0.3,0.62):
                lit=rng.random()<0.6; Bd+=box(xx,xx+0.26,yy,yy+0.36,1.995,2.0,(255,204,118) if lit else (38,48,78),emit=lit)
    Bd+=box(-5.5,3.2,0,3.4,2.7,2.76,(70,64,92))
    for lx in (0.95,-2.4,-4.6):                                                                                                               # street lamps
        Bd+=box(lx-0.025,lx+0.025,0,2.1,1.18,1.23,(50,46,60))+box(lx-0.025,lx+0.025,2.1,2.15,0.95,1.23,(50,46,60))+box(lx-0.09,lx+0.09,2.0,2.1,0.88,1.02,(255,214,130),emit=True)
    return F,Bd
STREET_F,STREET_B=street()
PUDDLES=[(-0.3,-0.55,0.30,0.16),(-1.5,-0.3,0.36,0.18),(-2.7,0.25,0.4,0.2),(-3.9,-0.45,0.34,0.17),(0.9,-0.4,0.3,0.15),(-0.2,0.7,0.5,0.2)]
def puddles(t):
    Q=[]
    for k,(x,z,hw,hd) in enumerate(PUDDLES):
        Q+=box(x-hw,x+hw,0.0,0.004,z-hd,z+hd,(56,72,116))+box(x-hw*0.3,x+hw*0.3,0.004,0.0055,z-hd*0.25,z+hd*0.25,(255,214,130),emit=True)
        for rr in range(2):                                                                                                                       # rain ripples
            ph=(t*0.9+k*0.31+rr*0.5)%1.0; r=0.015+0.09*ph; rx,rz=x+0.12*math.sin(k*2+rr*3),z+0.06*math.cos(k*3+rr)
            for a,b_,c_,d_ in ((-r,r,-r,-r+0.006),(-r,r,r-0.006,r),(-r,-r+0.006,-r,r),(r-0.006,r,-r,r)): Q+=box(rx+a,rx+b_,0.005,0.0065,rz+c_,rz+d_,(160,180,224),emit=True)
    return Q
LIGHTS=[((0.95,2.0,0.9),(255,200,130),1.3),((-2.4,2.0,0.9),(255,200,130),0.9),((0.0,3.0,-2.5),(150,170,255),0.5),((0.0,1.2,-2.2),(255,235,215),0.3)]

# ======================= animation: the dog =======================
def dog_x(t):
    V=0.5; ramp=0.7; t1=T_WALK+ramp
    if t<=T_WALK: return X_DOG
    if t<t1: u=(t-T_WALK)/ramp; return X_DOG-V*ramp*(u**3-u**4/2)
    return X_DOG-V*ramp*0.5-V*(t-t1)
def dog_state(t):
    ph=0.0
    if t<T_LIE[0]:
        hl=sm(seg01(t,*T_HEADDOWN)); P=mix(POSE['sit'],POSE['head'],hl)
    elif t<T_RISE[0]:                                                    # a gentle play-bow first (front down), then the hips fold: no collapse
        a=sm(seg01(t,T_LIE[0],T_LIE[0]+0.4)); b=sm(seg01(t,T_LIE[0]+0.3,T_LIE[1])); P=mix(mix(POSE['head'],POSE['bow'],a),POSE['lie'],b)
    else:
        u=sm(seg01(t,*T_RISE)); P=mix(POSE['lie'],POSE['stand'],u)
    sniff=0.03*math.sin(t*17)*sm(seg01(t,6.2,6.6))*(1-sm(seg01(t,8.2,8.6)))                    # nose twitch while the umbrella creeps closer
    P=dict(P,hp=P['hp']+sniff)
    walk=0.0
    if t>=T_WALK: walk=(t-T_WALK)*9.0*sm(seg01(t,T_WALK,T_WALK+0.5))
    wag=math.sin(t*(3.0 if t<10.4 else 9.0)) if (t>=10.4) else 0.25*math.sin(t*2.2)
    shiver=0.004*math.sin(t*34)*(1-sm(seg01(t,2.0,2.6))) if t<2.6 else 0.0
    blink=any(abs(t-b)<0.1 for b in BLINKS)
    lid=1.0 if blink else (0.3 if t<10.4 else 0.45)
    if 6.4<=t<8.6: lid=min(lid,0.08)                                       # wide, curious eyes on the umbrella
    smile=sm(seg01(t,10.4,10.9)) if t<T_RISE[0] else 1.0
    hroll=0.2*math.sin(PI*seg01(t,3.7,4.5))+0.16*math.sin(PI*seg01(t,10.2,10.9))
    earsw=0.1*math.sin(t*3)+(0.12*math.sin(walk*2) if walk else 0.0)
    nose_dry=(8.4<=t<T_LIE[0]) or (t>=T_WALK+0.4)
    return dict(base=(dog_x(t)+shiver,0.0,0.0),yaw=-PI/2,P=P,walk=walk,wag=wag,lid=lid,smile=smile,hroll=hroll,earsw=earsw,t=t,dry_nose=nose_dry,shade=sm(seg01(t,13.3,14.8)))
def dog_model(**st):
    return dog(**st)[0]

# ======================= animation: the duckling =======================
def nose_world(st):
    P=st['P']; Hc=np.array(P['Hc'],float); Rh=Rz(st['hroll'])@Ry(0.0)@Rx(P['hp']); p=Hc+Rh@np.array([0,-0.01,0.37]); return np.array(st['base'])+Ry(st['yaw'])@p
def stand_x():
    ds=dog_state(6.2); nw=nose_world(ds); ut=0.25; cz=0.03+UP_LEN*math.sin(ut); return float(nw[0]+0.06-DUCK_R-cz)
X_STAND=stand_x()                                                  # duckling stands so the canopy edge covers only the very tip of the nose
def leg_surface(z):                                                # top of the dog's near foreleg while lying (dog-local z -> y)
    return lerp(0.222,0.192,seg01(z,0.10,0.70))
X_APP=X_STAND-0.22
def duck_state(t):
    d=dog_state(t); dx=d['base'][0]
    st=dict(base=(-0.98,0.0,0.0),yaw=PI/2,walk=0.0,flap=0.2,hp=0.0,hy=0.0,ut=0.0,ulen=UP_LEN,blink=False,beak=0.0,squash=0.0,shade=d['shade'])
    st['ut']=0.25*sm(seg01(t,*T_RAISE)); st['blink']=any(abs(t-b)<0.08 for b in (2.6,5.0,8.7))
    if t<T_WALK_DUCK[0]:                                                     # sees the freezing dog: looks up, a small startled hop, then decides
        hop=0.03*math.sin(PI*seg01(t,1.25,1.5)); st.update(base=(-0.98,hop,0.0),squash=0.35*abs(math.sin(t*3))*(1-sm(seg01(t,1.2,1.5))),hp=0.5*sm(seg01(t,*T_NOTICE))*(1-0.4*sm(seg01(t,1.6,1.9))),flap=0.2+0.8*math.sin(PI*seg01(t,1.25,1.5)))
        return st
    if t<T_APPROACH[0]:
        a=sm(seg01(t,*T_WALK_DUCK)); st.update(base=(lerp(-0.98,X_APP,a),0.0,0.0),walk=t*9.0 if 0<a<1 else 0.0,hp=0.3+0.1*sm(seg01(t,3.4,4.4)))
        if t>=T_RAISE[0]: st['flap']=0.2+0.9*sm(seg01(t,*T_RAISE))*(1-sm(seg01(t,4.4,4.9)))
        return st
    if t<T_CLIMB[0]:
        a=sm(seg01(t,*T_APPROACH)); st.update(base=(lerp(X_APP,X_STAND,a),0.0,0.0),walk=t*6.5 if 0<a<1 else 0.0,hp=0.45)        # the slow, careful approach (anticipation)
        if t>=8.4: st.update(hp=0.45 if t<9.0 else lerp(0.45,0.9,sm(seg01(t,9.0,9.8))),squash=0.3*sm(seg01(t,8.4,8.7))*(1-sm(seg01(t,8.8,9.2))))
        if t>=9.8: st.update(hp=lerp(0.9,-0.2,sm(seg01(t,9.8,10.3))),squash=0.5*sm(seg01(t,10.0,10.4)))                              # looks up at the big dog... and droops: it only covers the nose
        return st
    # ---- the climb: ground -> paw -> along the foreleg -> back ----
    zlat=-0.34; ulen=lerp(UP_LEN,0.46,sm(seg01(t,T_CLIMB[0],11.1)))
    st.update(ulen=ulen,ut=0.0,hp=0.2)
    p_start=np.array([X_STAND,0.0,0.0]); p_ground=np.array([dx-0.88,0.0,zlat]); p_paw=np.array([dx-0.69,leg_surface(0.69),zlat]); p_elb=np.array([dx-0.17,leg_surface(0.17),-0.255])
    if t<11.2:
        a=sm(seg01(t,T_CLIMB[0],11.2)); pos=p_start+(p_ground-p_start)*a; st.update(base=tuple(pos),walk=t*9.0)
    elif t<11.4:                                                          # hop 1: onto the paw
        a=seg01(t,11.2,11.4); pos=p_ground+(p_paw-p_ground)*sm(a); pos[1]+=0.2*math.sin(PI*a); st.update(base=tuple(pos),flap=1.1)
    elif t<11.75:                                                         # waddles up the forearm
        a=sm(seg01(t,11.4,11.75)); pos=p_paw+(p_elb-p_paw)*a; pos[1]=leg_surface(0.69-(0.69-0.17)*a); pos[2]=lerp(zlat,-0.255,a*a); st.update(base=tuple(pos),walk=t*10.0)
    else:                                                                 # hop 2: onto the back, then turns to face forward
        P_now=dog_state(t); pn=np.array(P_now['base'])+Ry(P_now['yaw'])@perch(P_now['P'])
        if t<11.95:
            a=seg01(t,11.75,11.95); pos=p_elb+(pn-p_elb)*sm(a); pos[1]+=0.2*math.sin(PI*a); st.update(base=tuple(pos),flap=1.1)
        else: st.update(base=tuple(pn))
        st['yaw']=lerp(PI/2,-PI/2,sm(seg01(t,11.95,12.35)))
        st['ut']=0.8*sm(seg01(t,12.1,12.8)); st['ulen']=lerp(0.46,UP_LEN,sm(seg01(t,12.1,12.7)))
        if t>=T_WALK: st.update(squash=0.15*abs(math.sin((t-T_WALK)*9.0)),walk=0.0,hp=0.1*math.sin(t*4))
        st['flap']=(0.2+0.5*abs(math.sin(t*5))) if t>=12.0 else st['flap']
    return st
def duck_model(**st): return duckling(**st)[0]+duckling(**st)[2]

# ======================= camera =======================
CAM_Y=0.78; TGT_Y=0.62
def cam_shot(t):
    """A 0-3 wide push-in | B 3-6 medium | C 6-9 CLOSE-UP on the umbrella and the nose | D 9-10.7 pull-out reveal | E climb | F final walking shot (cut at T_CUT)"""
    if t<3.0: u=sm(seg01(t,0,3.0)); D=lerp(2.45,2.15,u); cx=lerp(-0.25,-0.32,u); cy,ty,fov=CAM_Y,TGT_Y,44
    elif t<6.0: u=sm(seg01(t,3.0,6.0)); D=lerp(2.15,1.75,u); cx=lerp(-0.32,-0.30,u); cy,ty,fov=CAM_Y,TGT_Y,44
    elif t<9.0: D=1.2-0.1*seg01(t,6.0,9.0); cx=-0.42; cy,ty,fov=0.5,0.42,40
    elif t<10.7: u=sm(seg01(t,9.0,10.7)); D=lerp(1.35,1.95,u); cx=-0.12; cy,ty,fov=lerp(0.6,0.78,u),lerp(0.5,0.62,u),42
    elif t<T_CUT: D=2.2; cx=-0.17; cy,ty,fov=CAM_Y,TGT_Y,44
    else:
        zoom=sm(seg01(t,*T_ZOOM)); D=lerp(2.5,3.7,zoom); cx=dog_x(t)-0.22; cy,ty,fov=CAM_Y+0.3*zoom,TGT_Y+0.1*zoom,lerp(44,42,zoom)
    return (cx,cy,-D),(cx,ty,0.0),fov

# ======================= render =======================
R=Renderer(W,H,fog=(52,42,90))
def render(t):
    cp,tg,fov=cam_shot(t); cpa=np.array(cp); cam=Camera.look(cp,tg)
    ds=dog_state(t); dq,dd=dog(**ds); us=duck_state(t); kq,kd,ku=duckling(**us)
    dd=[x for x in dd if np.linalg.norm(x['c']-cpa)<np.linalg.norm(x['hc']-cpa)]; kd=[x for x in kd if np.linalg.norm(x['c']-cpa)<np.linalg.norm(x['hc']-cpa)]
    layers=[STREET_F,STREET_B,puddles(t),dq,dd,kq,kd,ku]
    img,vi,zb=zrender(R,cam,layers,LIGHTS,fov=fov,fog_start=9,fog_end=30,ambient=0.46,bias=[1.0]*4+[1.004,1.0,1.004,1.0],return_z=True)
    a=np.asarray(img).astype(np.float32); yy=np.linspace(0,1,H)[:,None,None]
    grad=(np.array([46,36,86],np.float32)*(1-yy)+np.array([140,92,120],np.float32)*yy)*np.ones((1,W,1),np.float32); a=np.where((zb==0)[...,None],grad,a)
    return post.ps1(Image.fromarray(np.clip(a,0,255).astype(np.uint8))),vi,ds,us

# ======================= overlays: rain + subtitles =======================
_rr=np.random.default_rng(9); RAIN=[(_rr.uniform(-10,W+10),_rr.uniform(0,H+20),_rr.uniform(0.6,1.0)) for _ in range(90)]
def rain(d,t):
    for x0,y0,sp in RAIN:
        y=(y0+t*sp*230)%(H+24)-8; x=x0-y*0.09; L=int(5+5*sp); col=(int(150+60*sp),int(176+50*sp),int(230+20*sp))
        d.line([x,y,x-0.09*L,y+L],fill=col,width=1)
SUBS=[(0.2,2.85,['THIS TINY DUCK SAW A DOG','FREEZING IN THE RAIN.'],{'FREEZING'}),(3.0,4.6,['SO HE OFFERED','HIS UMBRELLA.'],{'UMBRELLA.'}),(6.0,7.6,['THERE WAS JUST','ONE PROBLEM...'],{'PROBLEM...'}),
      (9.0,10.6,['IT ONLY COVERED','HIS NOSE!'],{'NOSE!'}),(11.0,12.7,['SO THE DOG','GAVE HIM A RIDE.'],{'RIDE.'}),(13.1,14.2,['BEST FRIENDS!'],{'BEST','FRIENDS!'})]
def subtitles(d,t):
    for t0,t1,lines,hil in SUBS:
        if t0<=t<t1:
            w=max(font.width(l,1) for l in lines)+10; x0=(W-w)//2; y0=278; d.rectangle([x0,y0,x0+w,y0+len(lines)*10+5],fill=(0,0,0))
            for i,l in enumerate(lines):
                x=x0+5
                for wd in l.split(' '): font.text(d,wd,x,y0+3+i*10,(255,214,70) if wd in hil else (244,240,228),1,None); x+=font.width(wd,1)+6
def frame(t):
    img,vi,ds,us=render(t); d=ImageDraw.Draw(img); rain(d,t); subtitles(d,t); return img

# ======================= QA manifest =======================
def _extra(t):
    out=[]; ds=dog_state(t); us=duck_state(t)
    if t<0.05:
        for nm,p in (('dog',np.array(ds['base'])+np.array([0,0.6,0])),('duckling',np.array(us['base'])+np.array([0,0.1,0]))):
            cp,tg,fov=cam_shot(t); pr=R.project(tuple(p),R.view(Camera.look(cp,tg),fov))
            if not pr or not (0<pr[0]<W and 0<pr[1]<H): out.append(('camera',f'{nm} is not in the first frame'))
    if abs(t-9.0)<0.5/FPS:
        nw=nose_world(dog_state(9.0)); cx=us['base'][0]+0.03+UP_LEN*math.sin(us['ut']); edge=cx+DUCK_R
        if not (nw[0]-0.02<edge<nw[0]+0.12): out.append(('umbrella',f'canopy edge {edge:.2f} vs nose tip {nw[0]:.2f}: it must cover only the very tip of the nose'))
    return out
QA=dict(fps=FPS,dur=DUR,W=W,frame=frame,chars={'dog':(dog_state,dog_model,'_none',1.0),'duckling':(duck_state,duck_model,'_none',1.0)},
    geom=lambda t,name,st,V: [('floor',f'{name} under the floor')] if V[:,1].min()<-0.04 else [],extra=_extra,camera=lambda t: cam_shot(t)[0],min_cam_dist=0.4,
    camera_ok=lambda p: -4.0<p[2]<-0.5 and abs(p[0])<5.0 and 0.3<p[1]<1.6,
    scenes=[dict(id='freezing',t0=0.0,t1=3.0,action='tiny duckling notices the soaked huge dog (slow push-in)'),dict(id='offer',t0=3.0,t1=6.0,action='the duckling walks to the dog and raises the umbrella; the dog lowers its head once'),
            dict(id='problem',t0=6.0,t1=9.0,action='CLOSE-UP: the tiny umbrella creeps toward the big nose'),dict(id='punchline',t0=9.0,t1=10.7,action='pull-out: it only covers the nose; squeak; the dog blinks and smiles'),
            dict(id='climb',t0=10.7,t1=T_CUT,action='play-bow, the duckling climbs paw-forearm-back, the dog rises'),dict(id='ride',t0=T_CUT,t1=15.0,action='walking shot: the duckling rides, umbrella over both; wide ending')],
    weapon_events=[],texts=lambda: [('ui',l,1) for _,_,ls,_ in SUBS for l in ls])

TEST=os.environ.get('TEST')
if TEST and __name__=='__main__':
    ims=[frame(float(x)) for x in TEST.split(',')]; shp=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): shp.paste(im,(i*182,0))
    shp.resize((shp.width*2,640),Image.NEAREST).save('test.png'); sys.exit()


# ======================= AUDIO: gentle music box, rain, tiny animal voices, soft steps =======================
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=47); sr=s.sr; n=s.n; M=np.zeros(n); AMB=np.zeros(n)
    def note(buf,t0,m,d,v,wave='sin',dec=3.0,att=0.004,harm=(1.0,0.35,0.15)):
        f=440*2**((m-69)/12); tt=s.T(d); x=sum(h*np.sin(2*np.pi*f*(k+1)*tt) for k,h in enumerate(harm)) if wave=='bell' else np.sin(2*np.pi*f*tt)
        env=np.minimum(1,tt/att)*np.exp(-tt*dec); i=int(t0*sr); j=min(n,i+len(tt)); buf[i:j]+=(x*env*v)[:j-i]
    def tone(t0,f0,f1,d,v,vib=0.0,harm=(1.0,0.5,0.25),att=0.01,dec=0.0,pw=1.0):
        tt=s.T(d); fr=f0+(f1-f0)*(tt/d)**pw; fr=fr*(1+vib*np.sin(2*np.pi*7*tt)); ph=np.cumsum(fr)/sr
        x=sum(h*np.sin(2*np.pi*ph*(k+1)) for k,h in enumerate(harm)); env=np.minimum(1,tt/att)*np.sin(np.pi*np.clip(tt/d,0,1))**0.6*np.exp(-tt*dec); s.place(x*env,t0,v)
    def nb(t0,d,lo,hi,v,seed,shape=2): s.place(s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v)
    def thud(t0,f=70,v=0.1,d=0.2): tt=s.T(d); s.place(np.sin(2*np.pi*f*tt*(1-0.3*tt/d))*np.exp(-tt*16),t0,v)
    def tick(t0,v=0.02,f=3000): tt=s.T(0.025); s.place(np.sin(2*np.pi*f*tt)*np.exp(-tt*140),t0,v)
    def peep(t0,v=0.045,f=3000,rise=1.25,d=0.07): tone(t0,f,f*rise,d,v,harm=(1.0,0.3),att=0.004)
    def squeak(t0,v=0.05): tone(t0,900,2000,0.12,v,harm=(1.0,0.6,0.3),att=0.004); tone(t0+0.11,2000,1500,0.1,v*0.8,harm=(1.0,0.5),att=0.004)
    def whimper(t0,d=0.6,v=0.06,f0=480,f1=340): tone(t0,f0,f1,d,v,vib=0.03,harm=(1.0,0.5,0.2),att=0.08)
    def snuffle(t0,v=0.04): nb(t0,0.1,1500,6000,v,int(t0*100),1); nb(t0+0.13,0.08,1500,6000,v*0.7,int(t0*100)+1,1)
    def woof(t0,v=0.09): tone(t0,210,120,0.16,v,harm=(1.0,0.6,0.3),att=0.01); nb(t0,0.1,300,1800,v*0.4,int(t0*50),1)
    def pant(t0,d,v=0.02):
        for k in range(int(d/0.3)): nb(t0+k*0.3,0.14,1200,5000,v,int(t0*10)+k,1)
    def step_dog(t0,v=0.05,seed=0): thud(t0,75,v,0.12); nb(t0+0.01,0.07,700,3500,v*0.5,seed,1)
    rr=np.random.default_rng(3)
    AMB+=s.filt(s.rng.normal(0,1,n),lo=2200,hi=9000)*0.02+s.filt(s.rng.normal(0,1,n),lo=60,hi=500)*0.006                                    # rain
    for t0 in np.sort(rr.uniform(0.0,DUR-0.1,int(DUR*13))): tick(t0,0.008+0.006*rr.random(),1500+1500*rr.random())                        # drops on the umbrella
    # ---------- music box, in C ----------
    CH=[(0,(72,76,79),48),(1,(74,77,81),50),(2,(71,74,79),43),(3,(72,76,79),48)]
    def phrase(a,b,v=1.0,lift=0):
        t=a; k=0; st=0.385
        while t<b-1e-6:
            ch=CH[(k//4)%4]; m=ch[1][[0,1,2,1][k%4]]+12*(1 if (k%8==7) else 0)+lift
            note(M,t,m,0.9,0.034*v,'bell',2.6)
            if k%4==0: note(M,t,ch[2]+lift,1.4,0.05*v,'sin',1.6,0.02)
            k+=1; t+=st
    phrase(0.1,3.0,0.85); phrase(3.0,6.0,0.95)
    for k,m in enumerate((72,74,76,78,79,81,82,84)): note(M,6.0+k*0.3+(0.0 if k<4 else 0.1*(k-3)),m,0.5,0.03,'bell',4.0)                    # curiosity: tiptoeing notes
    tone(6.0,150,330,2.4,0.03,harm=(1.0,0.4),att=0.6)                                                                                        # a soft rising pad: what will happen?
    note(M,8.6,79,0.8,0.03,'bell',3.0)
    phrase(9.0,10.7,0.7)
    phrase(10.7,12.1,1.05); phrase(12.1,14.2,1.15)
    for m,t0 in ((60,14.2),(64,14.2),(67,14.2),(72,14.2),(74,14.2)): note(M,t0,m,0.8,0.035,'sin',0.5,0.4)                                  # the warm resolving chord (C add9)
    for k,m in enumerate((84,88,91,96,100)): note(M,14.25+k*0.07,m,0.9,0.02,'bell',3.0)                                                   # sparkle
    # ---------- animal voices ----------
    for t0,f,r in ((0.45,3000,1.2),(1.3,3300,1.5),(2.0,3100,1.25),(2.8,3000,1.2),(3.5,3200,1.3),(4.1,3000,1.2),(4.25,3250,1.2),(5.0,3100,1.2),(6.6,2900,1.15),(7.4,3000,1.2),(8.5,3200,1.3)): peep(t0,0.045,f,r)
    peep(9.9,0.05,2800,1.5,0.1); peep(10.35,0.035,2200,0.8,0.12)                                                                            # 'pip?' then a sheepish falling peep
    for t0,f,r in ((11.0,3100,1.3),(11.25,3200,1.3),(11.5,3000,1.2),(11.8,3300,1.3),(12.15,3100,1.25),(12.3,3300,1.2),(13.25,3200,1.25),(13.6,3300,1.3),(14.25,3200,1.2)): peep(t0,0.05,f,r)
    squeak(10.15); note(M,10.2,88,0.3,0.03,'bell',6.0)                                                                                       # 'nose!': the one soft, funny squeak
    whimper(0.9,0.6,0.055); whimper(2.0,0.5,0.04,420,320)
    tone(3.9,200,300,0.35,0.05,vib=0.02,harm=(1.0,0.5),att=0.05)                                                                             # curious 'hm?'
    snuffle(6.9); snuffle(7.8,0.035)                                                                                                         # the nose twitches as the umbrella creeps closer
    tone(10.45,210,290,0.3,0.045,harm=(1.0,0.4),att=0.05); tone(10.8,230,260,0.3,0.04,harm=(1.0,0.4),att=0.08)                                # a gentle 'huh?', then a happy 'mm'
    nb(11.0,0.6,300,1500,0.03,77,1.2)                                                                                                        # a sigh as he bows down
    tone(12.1,150,190,0.4,0.05,harm=(1.0,0.5),att=0.1); woof(12.7,0.08); pant(13.0,1.7,0.018)
    # ---------- steps ----------
    for k in range(8): tick(1.95+k*0.21,0.015,3400)
    for k in range(7): tick(6.1+k*0.34,0.012,3400)                                                                                           # slow, careful tiptoes
    thud(11.1,55,0.1,0.25); nb(11.1,0.3,200,900,0.03,78,1); thud(11.35,60,0.06,0.2)                                                          # the dog bows and settles
    for k in range(4): tick(10.85+k*0.12,0.015,3400)
    for k in range(5): tick(11.45+k*0.08,0.014,3400)
    nb(11.9,0.5,200,1200,0.02,79,1); thud(12.3,90,0.05,0.12)
    for k in range(int((DUR-12.75)/0.34)): step_dog(12.75+k*0.34,0.05,200+k)                                                              # soft wet steps
    s.L+=AMB; s.R+=np.roll(AMB,700)
    NB=np.zeros(n); duck=np.ones(n)
    for key,t0 in (('N1',0.15),('N2',3.0),('N3',6.0),('N4',9.0),('N5',11.0),('N6',13.1)):
        a,ar=_sf.read(os.path.join(TTS_DIR,'um',key+'.wav')); a=a if a.ndim==1 else a.mean(1)
        a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a); act=a[np.abs(a)>0.02]; a=a/(np.sqrt((act**2).mean())+1e-9)*0.2
        i=int(t0*sr); j=min(n,i+len(a)); NB[i:j]+=a[:j-i]; duck[max(0,i-int(0.08*sr)):min(n,j+int(0.15*sr))]=0.45
    duck=np.convolve(duck,np.ones(2400)/2400,'same')
    s.L+=2.0*M*duck; s.R+=2.0*np.roll(M,300)*duck
    s.reverb(0.16,length=1.2,decay=4.0)
    pk=max(np.abs(s.L).max(),np.abs(s.R).max()); gv=pk*1.0/np.abs(NB).max()
    s.L=s.L*(0.7+0.3*duck)+NB*gv; s.R=s.R*(0.7+0.3*duck)+NB*gv
    st=np.stack([s.L,s.R],1); k=int(0.4*sr); st[-k:]*=np.linspace(1,0,k)[:,None]
    st=st/np.max(np.abs(st))*0.9; _sf.write(path,st,sr,subtype='PCM_16'); return path
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'umbrella.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'um_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.96,vignette=0.22,grain=1.5,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(post.upscale(frame(f/FPS),S),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
