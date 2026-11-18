"""WHY DO GHOSTS SAY BOO?  PS1 horror-comedy / wholesome short, 9:16, 60 s (1440 frames @ 24 fps). Fully procedural (nightkit).
LOCKED ASSETS: ghost() (pale little ghost, stacked boxes, 3 mouth states), janitor() (blocky, brown, cap, lantern in the RIGHT hand), lantern() (yellow box + 2D glow),
corridor() (one stone corridor with a dark corner at the left end). All text / UI / glow / fog dither are 2D overlays after the 3D render.
Camera A medium-wide (shots 1-3, 6-7), B ghost medium close-up (shots 4-5), C low static final (shot 8). Hard cuts only.
Scene axes: +x = right of the screen. Janitor walks -x (left), ghost waits at the left, the dark corner is the left end. Camera looks +z from -z.
Voice: python tools/tts/gb.py -> $TTS_DIR/gb/*.wav.   Run: TEST=0.5,5,12 python examples/ghost_boo.py -> test.png | PART=a:b | PART=audio
QA: python tools/qa/scene_qa.py examples/ghost_boo.py"""
import os, sys, math, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, box, quad, transform, tiled_plane
from nightkit import post, font
from nightkit.zraster import zrender
from nightkit.audio import Sound
_T=os.environ.pop('TEST',None)                       # face_track has a TEST hook at import time
import face_track as FT
if _T is not None: os.environ['TEST']=_T
sm,seg01,seg,tag,Rx,Ry,Rz=FT.sm,FT.seg01,FT.seg,FT.tag,FT.Rx,FT.Ry,FT.Rz
PI=math.pi
def lerp(a,b,u): return a+(b-a)*u
TTS_DIR=FT.TTS_DIR; OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6; DUR=60.0; N=int(round(DUR*FPS))
try: SCR=json.load(open(os.path.join(TTS_DIR,'gb','script.json')))
except Exception: SCR=None

# ======================= palette =======================
GH=(255,255,255); GH_D=(230,244,255); GH_L=(255,255,255); BLK=(14,12,20); GH_ARM=(240,250,255)   # lit values are scaled by the renderer, so these read pale blue-white
UNI=(92,58,38); UNI_D=(68,42,28); CAP=(54,34,24); SKIN=(214,170,138); BOOT=(36,26,22); BELT=(30,24,22)
LAN=(255,206,64); LAN_D=(120,92,30); LAN_OFF=(104,80,34); LAN_CAP=(60,48,40); LAN_CORE=(255,236,150)
STONE=[(58,64,92),(50,56,84),(64,70,100),(46,52,78)]; STONE_W=[(66,72,102),(58,64,94),(72,78,108),(52,58,86)]

# ======================= timeline =======================
V_WALK=0.2                                           # janitor walking speed (m/s)
T_STOP=(20.4,21.2); T_GO=(38.3,38.9); T_HALT=(39.6,40.2)
T_BOO=44.0; T_JUMP=(44.25,45.05); T_CUT7=46.0
T_KNOCK=(15.15,15.7,16.25); T_FLICK=((23.2,23.38),(24.4,24.66))
T_SCARE_CUT=46.0
SHOT_CUTS=[21.0,38.0,46.0,53.0]
J_B=-1.5                                             # janitor x while he stands (shots 4-5)
JZ=0.2                                               # janitor path z
GZ=0.0                                               # ghost z in the staging at the left
X_ENDWALL=-4.2

def _speed(t):
    if t<T_STOP[0]: return V_WALK
    if t<T_STOP[1]: return V_WALK*(1-sm(seg01(t,*T_STOP)))
    if t<T_GO[0]: return 0.0
    if t<T_GO[1]: return V_WALK*sm(seg01(t,*T_GO))
    if t<T_HALT[0]: return V_WALK
    if t<T_HALT[1]: return V_WALK*(1-sm(seg01(t,*T_HALT)))
    return 0.0
_DT=1/240.; _TS=np.arange(0,DUR+1,_DT); _SP=np.array([_speed(t) for t in _TS]); _CUM=np.concatenate([[0],np.cumsum(_SP[:-1]*_DT)])
def _dist(t): return float(np.interp(t,_TS,_CUM))
X0=J_B+_dist(21.2)                                   # janitor x at t=0 so he stands at J_B during shots 4-5
def jx_walk(t): return X0-_dist(t)
XS=jx_walk(46.0)                                     # where he is frightened
LANTERN_FLOOR=(XS-0.2,0.0,JZ-0.32)                   # established drop spot

# ======================= LOCKED ASSET: the little ghost =======================
def ghost(base,yaw,hover=0.12,arms=((0.0,0.0),(0.0,0.0)),eye=1.0,mouth='neutral',lean=0.0,hyaw=0.0,squash=0.0,tremble=0.0,closed=False,t=0.0,shade=0.0,tipx=0.0,**_):
    """pale blue-white ghost, ~1.0 m tall, stacked boxes, no legs. arms: ((pitch,spread) for the character's LEFT arm, same for the RIGHT arm);
    spread 0 = hanging, pi/2 = out sideways, pi = straight up; pitch = swing forward(+z). local forward +z. returns (quads, face decals)"""
    b=np.array(base,float); Rb=Ry(yaw+hyaw); k=1-0.35*shade; c=lambda col: tuple(int(v*k) for v in col)
    sq=1-0.28*squash; jit=np.array([tremble*0.012*math.sin(t*61),0,tremble*0.008*math.cos(t*53)])
    def Wd(p):
        p=np.array(p,float); p=np.array([p[0]+lean*p[1]*0.35,p[1]*sq,p[2]]); return tuple(b+jit+np.array([0,hover*(1-0.9*squash),0])+Rb@p)
    Q=[]; D=[]
    # hem: four notched teeth (stepped geometry), then stepped body rows
    for i,x0 in enumerate((-0.27,-0.16,-0.05,0.06,0.17)): Q+=box(x0,x0+0.10,0.0 if i%2==0 else 0.07,0.18,-0.19,0.19,c(GH),xf=Wd)                  # scalloped hem (reads as cloth, not legs)
    Q+=box(-0.28,0.28,0.16,0.42,-0.21,0.21,c(GH),xf=Wd)+box(-0.31,0.31,0.42,0.68,-0.22,0.22,c(GH),xf=Wd)
    Q+=box(-0.27,0.27,0.68,0.86,-0.21,0.21,c(GH_L),xf=Wd)+box(-0.20,0.20,0.86,0.96,-0.17,0.17,c(GH_L),xf=Wd)+box(-0.12,0.12,0.96,1.0,-0.12,0.12,c(GH_L),xf=Wd)
    # face is on the head rows (yaw of the face only: hyaw)
    Hc=np.array([0,0.78,0]); Hd=Wd
    fz=0.2245                                                                             # in front of the widest row (0.22)
    es=0.13*(0.8+0.55*eye) if not closed else 0.13
    for sx in (-1,1):
        ex=sx*0.125
        if closed:                                                                        # happy closed eyes: thin ^ shapes
            D+=box(ex-0.06,ex+0.06,0.74,0.765,fz,fz+0.002,BLK,xf=Hd)+box(ex-0.06,ex-0.03,0.715,0.74,fz,fz+0.002,BLK,xf=Hd)+box(ex+0.03,ex+0.06,0.715,0.74,fz,fz+0.002,BLK,xf=Hd)
        else: D+=box(ex-es/2,ex+es/2,0.74-es/2+0.02,0.74+es/2+0.02,fz,fz+0.002,BLK,xf=Hd)
    if mouth=='neutral': D+=box(-0.045,0.045,0.58,0.605,fz,fz+0.002,BLK,xf=Hd)
    elif mouth=='afraid': D+=box(-0.04,0.04,0.54,0.62,fz,fz+0.002,BLK,xf=Hd)+box(-0.02,0.02,0.56,0.60,fz+0.002,fz+0.003,(70,40,60),xf=Hd)
    elif mouth=='happy': D+=box(-0.075,0.075,0.585,0.61,fz,fz+0.002,BLK,xf=Hd)+box(-0.095,-0.075,0.61,0.635,fz,fz+0.002,BLK,xf=Hd)+box(0.075,0.095,0.61,0.635,fz,fz+0.002,BLK,xf=Hd)
    tag(D,Wd(Hc))
    # short rectangular arms (rigid segments from the shoulder)
    for i,sx in enumerate((-1,1)):
        pit,spr=arms[i]; sh=np.array([sx*0.34,0.55,0.0]); d0=np.array([sx*math.sin(spr),-math.cos(spr),0.0]); d=Rx(-pit)@d0
        hand=sh+d*0.28; Q+=transform(seg(tuple(sh),tuple(hand),0.085,c(GH_ARM),0.085)+box(-0.05,0.05,-0.05,0.05,-0.05,0.05,c(GH_L),xf=lambda p,hand=hand: tuple(hand+np.array(p))),Wd)
    return Q,D
def ghost_hand(st,side):
    """world position of the ghost's hand (side -1/+1 as in ghost())"""
    pit,spr=st['arms'][0 if side<0 else 1]; sh=np.array([side*0.34,0.55,0.0]); d=Rx(-pit)@np.array([side*math.sin(spr),-math.cos(spr),0.0]); p=sh+d*0.28
    sq=1-0.28*st.get('squash',0.0); p=np.array([p[0]+st.get('lean',0.0)*p[1]*0.35,p[1]*sq,p[2]])
    return np.array(st['base'])+np.array([0,st['hover']*(1-0.9*st.get('squash',0.0)),0])+Ry(st['yaw']+st.get('hyaw',0.0))@p

# ======================= LOCKED ASSET: the janitor =======================
def janitor(base,yaw,walk=0.0,run=0.0,hyaw=0.0,rarm=None,larm=None,lift=0.0,crouch=0.0,shrug=0.0,lean=0.0,fear=0.0,t=0.0,shade=0.0,lantern_lit=True,**_):
    """blocky 1.7 m janitor, dark brown uniform, square cap. local forward +z, local -x is HIS RIGHT HAND (holds the lantern). rarm/larm = (pitch,spread).
    returns (quads, face decals, right-hand world position function inputs)"""
    b=np.array(base,float); Rb=Ry(yaw); k=1-0.35*shade; c=lambda col: tuple(int(v*k) for v in col)
    sw=math.sin(walk); amp=0.34 if not run else 0.9
    def Wd(p):
        p=np.array(p,float); p=np.array([p[0],p[1]-crouch*0.12*(1 if p[1]>0.8 else p[1]/0.8),p[2]+lean*max(0,p[1]-0.8)*0.5]); return tuple(b+np.array([0,lift,0])+Rb@p)
    Q=[]; D=[]; hipy=0.80-crouch*0.12
    for sx in (-1,1):                                                                             # legs: stiff swing from the hip
        a=amp*sw*(1 if sx>0 else -1); foot=np.array([sx*0.11,0.0,0.0]); hip=np.array([sx*0.11,hipy,0.0])
        fz=0.80*math.sin(a)*(1.0); fy=0.80*math.cos(a)-0.0; ft=np.array([sx*0.11,hipy-fy+0.0,fz]); ft[1]=max(0.0,hipy-fy*(1.0)) if True else 0
        Q+=transform(seg(tuple(hip),tuple(ft+np.array([0,0.07,0])),0.15,c(UNI_D),0.17)+box(-0.09,0.09,-0.07,0.0,-0.08,0.16,c(BOOT),xf=lambda p,ft=ft: tuple(ft+np.array([0,0.07,0])+np.array(p))),Wd)
    Q+=box(-0.26,0.26,0.78,0.86,-0.15,0.15,c(BELT),xf=Wd)+box(-0.25,0.25,0.86,1.42,-0.14,0.14,c(UNI),xf=Wd)+box(-0.215,0.215,1.42,1.46,-0.12,0.12,c(UNI_D),xf=Wd)
    Hc=np.array([0,1.43,0.0]); Rh=Ry(hyaw)
    def Hd(p): return Wd(Hc+Rh@(np.array(p,float)-Hc)) if True else None
    Q+=box(-0.145,0.145,1.46,1.70,-0.145,0.145,c(SKIN),xf=Hd)+box(-0.17,0.17,1.64,1.74,-0.17,0.17,c(CAP),xf=Hd)+box(-0.12,0.12,1.62,1.66,0.14,0.22,c(CAP),xf=Hd)         # head, cap, small brim
    fz=0.1465
    for sx in (-1,1):
        D+=box(sx*0.07-0.025,sx*0.07+0.025,1.56-(0.0 if fear<0.5 else 0.01),1.60+(0.0 if fear<0.5 else 0.02),fz,fz+0.002,BLK,xf=Hd)
    D+=box(-0.05,0.05,1.49,1.515,fz,fz+0.002,(80,50,40) if fear<0.5 else BLK,xf=Hd)
    if fear>0.5: D+=box(-0.03,0.03,1.475,1.53,fz,fz+0.002,BLK,xf=Hd)
    tag(D,Wd(Hc))
    # arms (rigid): right arm (local -x) holds the lantern unless rarm is overridden
    arms={}
    for sx in (-1,1):
        sh=np.array([sx*0.32,1.36+0.04*shrug,0.0])
        if sx<0: pit,spr=rarm if rarm is not None else (0.55,0.12)
        else: pit,spr=larm if larm is not None else (0.5*sw*(1 if not run else 2.4)*-1+0.0,0.08)
        d=Rx(-pit)@np.array([sx*math.sin(spr),-math.cos(spr),0.0]); hand=sh+d*0.64; arms[sx]=hand
        Q+=transform(seg(tuple(sh),tuple(hand),0.12,c(UNI),0.13)+box(-0.06,0.06,-0.06,0.06,-0.06,0.06,c(SKIN),xf=lambda p,hand=hand: tuple(hand+np.array(p))),Wd)
    return Q,D,tuple(Wd(arms[-1]))
def janitor_hand(st):
    return np.array(janitor(**st)[2])

# ======================= LOCKED ASSET: the lantern =======================
def lantern(pos,on=True,glowk=1.0,tilt=0.0):
    """rectangular yellow lantern: body 0.14 x 0.22 x 0.14, dark cap + base, wire handle. pos = centre of its body. emissive core when lit."""
    p=np.array(pos,float); R=Rz(tilt)
    def Wd(q): return tuple(p+R@np.array(q,float))
    body=LAN if on else LAN_OFF
    Q=box(-0.07,0.07,-0.11,0.11,-0.07,0.07,body,xf=Wd,emit=on)+box(-0.085,0.085,-0.14,-0.11,-0.085,0.085,LAN_CAP,xf=Wd)+box(-0.085,0.085,0.11,0.14,-0.085,0.085,LAN_CAP,xf=Wd)
    Q+=box(-0.045,0.045,-0.08,0.08,-0.072,0.072,LAN_CORE if on else LAN_D,xf=Wd,emit=on)+box(-0.05,0.05,0.14,0.17,-0.012,0.012,LAN_CAP,xf=Wd)+box(-0.05,-0.035,0.11,0.17,-0.012,0.012,LAN_CAP,xf=Wd)+box(0.035,0.05,0.11,0.17,-0.012,0.012,LAN_CAP,xf=Wd)
    return Q

# ======================= LOCKED ENVIRONMENT: the stone corridor =======================
WALL_Z=1.25
def corridor():
    F=tiled_plane(-4.6,12.0,-5.0,WALL_Z,0.0,0.35,lambda i,j:STONE[((i*73856093)^(j*19349663))%4])
    Wl=[]; rng=np.random.default_rng(11)
    for i,x in enumerate(np.arange(-4.2,12.0,0.45)):                                              # back wall: running-bond stone blocks, darker toward the corner
        for j,y in enumerate(np.arange(0.0,3.0,0.42)):
            xo=x+(0.22 if j%2 else 0.0); sh=float(np.clip((xo+3.0)/2.4,0.0,1.0))**1.2*0.88+0.12
            col=tuple(int(v*sh) for v in STONE_W[((i*31)^(j*17))%4]); Wl+=box(xo,xo+0.43,y,y+0.40,WALL_Z,WALL_Z+0.04,col)
    Wl+=box(-4.6,-4.2,0,3.0,-5.0,WALL_Z+0.04,(10,12,24))                                           # end wall of the corridor (dark corner)
    Wl+=box(-4.6,12.0,3.0,3.2,-5.0,WALL_Z+0.04,(30,34,56))                                         # ceiling slab
    for px in np.arange(-3.4,12.0,2.0):                                                           # pillars: depth cue + distant corridor
        sh=float(np.clip((px+3.0)/2.4,0.0,1.0))*0.8+0.2; Wl+=box(px,px+0.3,0,3.0,WALL_Z-0.22,WALL_Z,tuple(int(v*sh) for v in (84,90,122)))
    Wl+=box(-4.2,12.0,0,0.12,WALL_Z-0.06,WALL_Z,(40,44,70))                                         # skirting
    Wl+=box(5.0,12.0,0,3.2,WALL_Z-1.0,WALL_Z+0.2,(16,20,40))                                       # far, dark end of the corridor on the right (distance)
    return F,Wl
COR_F,COR_W=corridor()
LIGHTS_BASE=[((0.0,2.6,-1.5),(120,140,230),0.0)]

# ======================= animation: janitor =======================
def jwalk_phase(t): return _dist(t)/0.19*PI            # one half-stride per 0.19 m
def janitor_state(t):
    x=jx_walk(t); sp=_speed(t) if t<46.0 else 0.0
    st=dict(base=(x,0.0,JZ),yaw=-PI/2,walk=0.0,run=0.0,hyaw=0.0,rarm=None,larm=None,lift=0.0,crouch=0.0,shrug=0.0,lean=0.0,fear=0.0,t=t,shade=0.0)
    ph=jwalk_phase(t) if t<46.0 else 0.0
    walking=sp>0.01
    st['walk']=ph if walking else 0.0
    # lantern arm swings a little with the walk, rest idle sway
    st['rarm']=(0.55+0.05*math.sin(ph) if walking else 0.55+0.02*math.sin(t*1.6),0.12)
    st['larm']=(-0.5*math.sin(ph) if walking else 0.03*math.sin(t*1.3),0.08)
    # shot 3: brief head turn toward the knock, then a shrug
    hy=0.9*math.sin(PI*seg01(t,16.35,18.0))**1; st['hyaw']=hy*0.0+0.9*sm(seg01(t,16.35,16.8))*(1-sm(seg01(t,17.5,17.95)))
    sh=math.sin(PI*seg01(t,18.1,18.9)); st['shrug']=sh;
    if 18.1<t<18.9: st['larm']=(0.0,0.08+0.55*sh);
    # flicker: he stops and glances at the lantern (shots 4-5): small shake
    if 22.0<t<38.0: st['hyaw']=-0.35*sm(seg01(t,22.4,22.9))*(1-sm(seg01(t,36.0,36.8)))
    # shot 6/7: frightened
    if t>=T_BOO:
        j=seg01(t,*T_JUMP); hop=math.sin(PI*j)
        if t<T_CUT7:
            st['lift']=0.28*hop*(1 if j<1 else 0)
            st['yaw']=-PI/2-sm(seg01(t,44.2,44.7))*PI/4
            st['fear']=1.0
            st['larm']=(0.3,2.3*sm(seg01(t,44.2,44.5)))
            st['rarm']=(0.55+0.25*hop,0.12+0.3*hop)
            st['hyaw']=0.0
            st['crouch']=0.45*sm(seg01(t,44.1,44.25))*(1-sm(seg01(t,44.25,44.4)))
    return st
def janitor_flee(t):
    """shot 7 (after the hard cut): the janitor is already backing away, then runs out of the right edge"""
    p0=XS
    b=(p0+0.15,);
    if t<46.45:
        u=seg01(t,46.0,46.45); x=p0+0.15+0.55*sm(u); st=dict(yaw=lerp(-PI*0.75,-PI*1.5,sm(seg01(t,46.3,46.8))),walk=-(t-46.0)*14.0,run=0.0)
    else:
        x=p0+0.70+3.2*(t-46.45)*(0.4+0.6*sm(seg01(t,46.45,47.0))); yaw=lerp(-PI*0.75,-PI*1.5,sm(seg01(t,46.3,46.8))); st=dict(yaw=yaw,walk=(t-46.45)*17.0,run=1.0)
    s=dict(base=(x,0.0,JZ),hyaw=0.0,rarm=(0.55,0.1),larm=(0.9,0.1),lift=0.0,crouch=0.0,shrug=0.0,lean=0.0,fear=1.0,t=t,shade=0.0)
    s.update(st)
    if t>=46.45: s.update(rarm=(-1.2*math.sin(s['walk']),0.1),larm=(1.2*math.sin(s['walk']),0.1),fear=0.0,lean=0.2)
    return s
def jan(t):
    return janitor_state(t) if t<T_CUT7 else janitor_flee(t)

# ======================= animation: ghost =======================
def gx_follow(t):
    """shots 1-3: the ghost floats beside the janitor's path, drifting closer; world x"""
    return jx_walk(t)-lerp(1.3,1.15,sm(seg01(t,0.0,5.0)))       # never so close that the held lantern covers its face
def ghost_state(t):
    bob=0.05*math.sin(t*2.2)
    st=dict(base=(0,0,GZ),yaw=PI,hover=0.14+bob,arms=((0.0,0.1),(0.0,0.1)),eye=1.0,mouth='neutral',lean=0.0,hyaw=0.0,squash=0.0,tremble=0.0,closed=False,t=t,shade=0.0)
    arms=[(0.0,0.1+0.04*math.sin(t*2.0)),(0.0,0.1+0.04*math.sin(t*2.0+1.0))]
    X=gx_follow(t); Z=0.75; yaw=PI
    if t<5.0:
        # shot 1: already moving toward the lantern; raises a hand toward the janitor
        yaw=lerp(PI-0.25,PI-0.55,sm(seg01(t,0,4)));
        r=sm(seg01(t,3.0,4.0))*(1-sm(seg01(t,4.6,5.0))); arms[1]=(0.3,0.1+1.9*r+0.15*math.sin(t*9)*r)
        st['hyaw']=-0.4
    elif t<13.0:
        # shot 2: floats closer, polite "Excuse me?" gesture, disappointed
        u=sm(seg01(t,5.0,6.0)); X=jx_walk(t)-lerp(1.15,0.95,u); yaw=PI-0.6
        st['hyaw']=-0.5
        g=sm(seg01(t,5.3,5.9))*(1-sm(seg01(t,7.3,7.7)))
        arms[1]=(0.9*g,0.1+1.0*g+0.1*math.sin(t*8)*g)                                 # tiny whisper gesture: hand up beside the mouth
        if 6.0<t<7.3: st['mouth']='afraid'; st['mouth']='neutral' if int(t*9)%2 else 'afraid'
        dr=sm(seg01(t,7.7,8.5)); st['lean']=-0.25*dr; st['squash']=0.12*dr; st['eye']=1.0-0.35*dr; X=X-0.06*dr
    elif t<21.0:
        # shot 3: moves beside the wall and knocks three times
        u=sm(seg01(t,13.3,14.8)); Z=lerp(0.75,0.88,u)*(1-sm(seg01(t,19.2,20.9)))+0.3*sm(seg01(t,19.2,20.9)); X=jx_walk(t)-lerp(1.01,1.0,u)
        yaw=lerp(PI-0.6,PI-0.3,u); st['hyaw']=0.0
        k=0.0
        for tk in T_KNOCK:
            k=max(k,math.sin(PI*seg01(t,tk-0.12,tk+0.14)))
        # the arm toward the wall (character's LEFT, local -x) hammers
        up=sm(seg01(t,14.55,14.9))*(1-sm(seg01(t,16.5,16.9)))                         # screen-left arm (away from the lantern) raised against the wall, taps 3x
        arms[1]=(lerp(0.0,-0.35-0.25*k,up),lerp(0.1,2.25-0.3*k,up))
        if 16.4<t<18.3: st['eye']=1.35; st['mouth']='happy'; arms[1]=(0.0,0.3+0.2*math.sin(t*6));
        if t>=18.3:
            dr=sm(seg01(t,18.9,19.6)); st['eye']=lerp(1.35,0.7,dr); st['mouth']='neutral'; st['lean']=-0.2*dr
    elif t<30.0:
        # shot 4 (camera B): trembles at the flicker, instantly relaxes when the light is back
        X=J_B-0.85; Z=0.3; yaw=PI-0.45; st['hyaw']=-0.35
        lo=lantern_state(t)['on']
        fl=sm(seg01(t,23.2,23.5))*(1-sm(seg01(t,26.0,26.6)))
        if t<23.2 or t>=26.6: st['mouth']='neutral'
        tr=1.0 if (23.2<=t<26.5) else 0.0
        if tr:
            st.update(mouth='afraid',eye=1.7,tremble=1.0,squash=0.10); arms=[(0.1,2.6),(0.1,2.6)]; st['hyaw']=0.0
        if 26.6<=t<30.0:
            r=sm(seg01(t,26.6,27.2)); st['hyaw']=lerp(0.0,-0.45,r); st['eye']=lerp(1.5,1.0,r)
    elif t<38.0:
        # shot 5: dark corner behind, then the lantern, reaching, gathering courage
        X=J_B-0.85; Z=0.3; yaw=PI-0.35
        look_c=sm(seg01(t,30.4,31.2))*(1-sm(seg01(t,32.2,32.8)))
        st['hyaw']=lerp(-0.45,0.9,look_c) if t<32.8 else lerp(0.9,-0.45,sm(seg01(t,32.8,33.4)))
        if t>=32.8: st['hyaw']=-0.5
        st['eye']=1.25
        # looks at the dark corner: uneasy
        if 30.4<t<32.8: st['mouth']='afraid'; st['eye']=1.45; st['lean']=0.12
        rch=sm(seg01(t,34.0,35.2))*(1-sm(seg01(t,35.6,36.4)))
        arms[1]=(0.35*rch,0.1+1.15*rch); X=X+0.0
        if t>=35.8:
            br=sm(seg01(t,36.4,37.3))*(1-sm(seg01(t,37.3,37.9)))                            # a small breath: gathering courage
            st['squash']=-0.05*br; st['lean']=0.0; st['mouth']='neutral'; st['eye']=1.1; arms=[(0.0,0.25+0.2*br),(0.0,0.25+0.2*br)]; st['hyaw']=-0.3
    elif t<46.0:
        # shot 6 (camera A): backs off into the dark, then dashes in front of the janitor; BOO lunge
        a=sm(seg01(t,38.3,40.2)); b=sm(seg01(t,42.9,43.55)); X=lerp(J_B-0.85,XS-1.35,a); X=lerp(X,XS-1.0,b); Z=lerp(0.3,0.0,sm(seg01(t,42.9,43.55)))
        yaw=lerp(PI-0.35,PI-0.7,sm(seg01(t,42.9,43.6))); st['hyaw']=0.0
        st['hover']=0.14+0.05*math.sin(t*2.2)+0.12*math.sin(PI*b)
        if t>=43.0:
            rr=sm(seg01(t,43.1,43.7)); arms=[(-0.15*rr,0.1+2.6*rr),(-0.15*rr,0.1+2.6*rr)]; st['eye']=1.5; st['mouth']='afraid' if t<43.95 else 'happy'
        if t<42.9 and t>=38.3: st['tremble']=0.5; st['mouth']='afraid'; st['eye']=1.2
        if t>=T_BOO:
            lu=math.sin(PI*seg01(t,T_BOO,T_BOO+0.32)); X=XS-1.0+0.14*lu; st['mouth']='afraid'; st['eye']=1.7; st['squash']=-0.08*lu
            if t>=44.7: X=XS-1.0+0.14*lu - 0.25*sm(seg01(t,44.8,46.0)); st['mouth']='neutral'; st['eye']=1.4; arms=[(0.0,0.7),(0.0,0.7)]
    elif t<53.0:
        # shot 7: surprised, slowly approaches the lantern
        X=lerp(XS-1.25,-2.55,sm(seg01(t,48.6,52.8))); Z=0.0; yaw=PI-0.8; st['hyaw']=0.0
        st['eye']=lerp(1.5,1.0,sm(seg01(t,47.2,49.0))); st['mouth']='afraid' if t<48.3 else 'neutral'; arms=[(0.0,0.3),(0.0,0.3)]
        if t>=48.3: st['hyaw']=-0.4
        X=min(X,-2.5) if t>=52.9 else X
        yaw=lerp(PI-0.8,PI-0.55,sm(seg01(t,48.6,52.8)))
    else:
        # shot 8 (camera C): lifts the lantern, sets it beside itself, curls into a resting pose; happy blink at the end
        X=-2.55; Z=0.0; yaw=PI-0.15
        lf=lantern_state(t)
        reach=sm(seg01(t,53.2,53.9)); hold=sm(seg01(t,54.0,55.0)); place=sm(seg01(t,55.0,56.0)); rest=sm(seg01(t,56.0,57.0))
        yaw=PI-0.15
        arms=[(0.0,0.1),(0.9*(reach)*(1-0.0),0.1+0.9*reach)]
        if t>=54.0: arms[1]=(1.3*hold,0.05+0.35*hold)
        if t>=55.0: arms[1]=(1.3*(1-place)+0.5*place,0.4*(1-place)+0.1*place); arms[0]=(0.0,0.1)
        if t>=56.0: arms=[(0.0,0.1),(0.2*(1-rest),0.1)]
        st['squash']=0.55*rest; st['lean']=-0.18*rest; st['hover']=0.14*(1-rest)+0.0+0.03*math.sin(t*2.2)*(1-rest)
        st['eye']=1.0; st['mouth']='happy' if t>=53.9 else 'neutral'
        st['closed']=t>=56.6 and not (58.9<=t<59.1)
        st['hyaw']=-0.3*(1-rest)
        X=-2.55-0.0*rest
    st['hyaw']=max(PI-0.6,min(PI+0.6,yaw+st['hyaw']))-yaw                              # the face always stays turned toward the camera side
    st.update(base=(X,0.0,Z),yaw=yaw,arms=(tuple(arms[0]),tuple(arms[1])))
    st['shade']=0.0
    return st
def ghost_model(**st): return ghost(**st)[0]
def jan_model(**st):
    q=janitor(**{k:v for k,v in st.items()})[0]
    return q

# ======================= animation: lantern =======================
def lantern_flick(t):
    for a,b in T_FLICK:
        if a<=t<b: return False
    return True
def lantern_state(t):
    """pos (centre of the body), on, tilt. Held in the janitor's right hand until the hard cut at 46 s, then it lies on the floor, then the ghost lifts it."""
    if t<T_CUT7:
        js=jan(t); hand=janitor_hand(js)
        return dict(pos=tuple(hand+np.array([0,-0.14,0.0])),on=lantern_flick(t),tilt=0.0,held='janitor')
    fl=np.array(LANTERN_FLOOR)+np.array([0,0.14,0])
    if t<53.0 or t<54.0: return dict(pos=tuple(fl),on=True,tilt=0.0,held='floor')
    up=np.array([fl[0]+0.05,0.55,fl[2]]); side=np.array([-2.08,0.14,-0.15])
    if t<55.0: p=fl+(up-fl)*sm(seg01(t,54.0,55.0)); return dict(pos=tuple(p),on=True,tilt=0.0,held='ghost')
    p=up+(side-up)*sm(seg01(t,55.0,56.0)); return dict(pos=tuple(p),on=True,tilt=0.0,held='ghost' if t<56.0 else 'floor')

# ======================= cameras =======================
def cam_shot(t):
    """A: static medium-wide, follows the janitor's walk with a constant-velocity glide in shots 1-3 | B: ghost medium close-up | C: low static"""
    if t<21.0:
        cx=jx_walk(t)-0.6; return (cx,0.95,-3.4),(cx,0.62,0.0),32.0
    if t<38.0: cx=-2.15; return (cx,0.85,-2.8),(cx,0.50,0.0),32.0
    if t<53.0: cx=-2.45; return (cx,0.95,-3.4),(cx,0.62,0.0),32.0
    return (-2.3,0.45,-3.0),(-2.3,0.50,0.0),32.0
def cam_id(t): return 'A' if (t<21.0 or 38.0<=t<53.0) else ('B' if t<38.0 else 'C')

# ======================= render =======================
R=Renderer(W,H,fog=(10,14,34))
def render(t):
    cp,tg,fov=cam_shot(t); cpa=np.array(cp); cam=Camera.look(cp,tg)
    gs=ghost_state(t); js=jan(t); ls=lantern_state(t)
    gq,gd=ghost(**gs); jq,jd,_h=janitor(**js)
    for dd in (gd,jd):
        dd[:]=[x for x in dd if np.linalg.norm(x['c']-cpa)<np.linalg.norm(x['hc']-cpa)]
    lq=lantern(ls['pos'],ls['on'])
    glow=1.0+0.08*math.sin(t*5.0) if ls['on'] else 0.0
    lights=[((ls['pos'][0],ls['pos'][1]+0.1,ls['pos'][2]-0.15),(255,196,100),0.75*glow),((cpa[0],2.4,-1.0),(110,130,230),0.0)]
    layers=[COR_F,COR_W,jq,jd,gq,gd,lq]
    img,vi,zb=zrender(R,cam,layers,lights,fov=fov,fog_start=5,fog_end=16,ambient=0.34 if t<53.0 else 0.68,bias=[1,1,1,1.004,1,1.004,1.0],return_z=True)
    a=np.asarray(img).astype(np.float32)
    a=a*np.array([0.82,0.9,1.12],np.float32)                                              # dark blue ambient grade
    # 2D lantern glow: banded, additive, warm; vanishes while the lantern is off
    if ls['on']:
        pr=R.project(tuple(ls['pos']),R.view(cam,fov))
        if pr:
            gxs,gys=np.meshgrid(np.arange(W)+0.5,np.arange(H)+0.5); rad=pr[2]; sc=R.view(cam,fov)[7]/pr[2]                 # pixels per metre at the lantern
            d=np.sqrt((gxs-pr[0])**2+(gys-pr[1])**2)/(sc*0.62*(1+0.04*math.sin(t*5.0)))
            g=np.clip(1-d,0,1)**1.7; g=np.round(g*6)/6
            a+=g[...,None]*np.array([90,58,18],np.float32)
    return post.ps1(Image.fromarray(np.clip(a,0,255).astype(np.uint8))),gs,js,ls,cam,fov

# ======================= subtitles and UI (2D overlays only) =======================
ACC=(255,214,70); WHT=(244,240,228)
HIL={'BOO':1,"'BOO'":1,"'BOO'?":1,"'BOO'.":1,'LANTERN':1,'LANTERN.':1,'PANICKED.':1,'PANICKED':1,'DARK.':1,'DARK':1,'NIGHTLIGHT.':1,'NIGHTLIGHT':1,"BOO'":1}
LINES=[('N1',0.15,'Why do ghosts always say \'boo\'?'),('N2',2.45,'This little ghost had a problem.'),('G1',6.0,'Excuse me?'),('N3',8.0,'He tried asking nicely. Nobody listened.'),
       ('N4a',13.3,'So he tried knocking.'),('N4b',18.2,'Still nothing.'),('N5',22.3,'Then the lantern flickered... and the ghost panicked.'),('N6',30.9,"He wasn't trying to haunt anyone. He just hated the dark."),
       ('N7',39.2,'So he tried one last thing...'),('G2',44.0,'BOO!'),('N8',47.0,'The janitor ran... and left his lantern behind.'),('N9',53.2,"Turns out, 'boo' wasn't a threat."),('N10',57.0,'He just wanted a nightlight.')]
# ======================= EDIT: time remap (v3, shorter + faster) =======================
# Story time (all animation, QA, UI cues) stays 0-60 s. Output time plays the important parts at 1x (every voice line, the knocks,
# the flicker, BOO + hop, the lantern drop / flee, the payoff) and the dead stretches in between at FAST x. No jump cuts inside a shot.
FAST=3.0
def _keep():
    K=[(0.0,5.0),(14.9,16.5),(23.0,25.0),(42.8,45.3),(46.0,47.3),(53.0,56.1),(57.3,60.0)]
    for key,t0,_ in LINES: K.append((max(0.0,t0-0.1),t0+(SCR['dur'][key] if SCR else 2.0)+0.2))
    K.sort(); out=[]
    for a,b in K:
        if out and a<=out[-1][1]: out[-1]=(out[-1][0],max(out[-1][1],b))
        else: out.append((a,b))
    return out
KEEP=_keep()
_BS=[0.0]; _BO=[0.0]
for _a,_b in KEEP:
    if _a>_BS[-1]: _BO.append(_BO[-1]+(_a-_BS[-1])/FAST); _BS.append(_a)
    _BO.append(_BO[-1]+(_b-_a)); _BS.append(_b)
if _BS[-1]<DUR: _BO.append(_BO[-1]+(DUR-_BS[-1])/FAST); _BS.append(DUR)
N_OUT=int(math.ceil(_BO[-1]*FPS)); DUR_OUT=N_OUT/FPS
def SRC(to): return float(np.interp(to,_BO,_BS))
def OUTT(ts): return float(np.interp(ts,_BS,_BO))
def sub_chunks():
    """split every line into short chunks (<= 2 rows of ~15 chars), timed by character share over the measured voice length"""
    out=[]
    for key,t0,txt in LINES:
        dur=(SCR['dur'][key] if SCR else 2.0); words=txt.split(' '); n=sum(len(w)+1 for w in words); chunks=[]; cur=[]
        for w in words:
            if cur and (sum(len(x)+1 for x in cur)+len(w)>15 or (cur[-1].endswith(('.','?','!','...')) and len(cur)>=2)): chunks.append(cur); cur=[]
            cur.append(w)
        if cur: chunks.append(cur)
        pos=0
        for ch in chunks:
            L=sum(len(x)+1 for x in ch); o0=OUTT(t0); a=o0+dur*pos/n; b=o0+dur*(pos+L)/n; pos+=L                # output time
            rows=[]; r=[]
            for w in ch:
                if r and sum(len(x)+1 for x in r)+len(w)>14: rows.append(r); r=[]
                r.append(w)
            rows.append(r); out.append((a,b+0.12,rows,key))
    for i in range(len(out)-1):                                                           # chunk stays until the next one starts (inside the same line)
        if out[i][3]==out[i+1][3]: out[i]=(out[i][0],out[i+1][0],out[i][2],out[i][3])
    return out
SUBS=sub_chunks()
def subtitles(d,t):
    for a,b,rows,key in SUBS:
        if a<=t<b:
            lines=[' '.join(r) for r in rows]; w=max(font.width(l,1) for l in lines)+10; x0=(W-w)//2; y0=266; d.rectangle([x0,y0,x0+w,y0+len(lines)*10+5],fill=(0,0,0))
            for i,r in enumerate(rows):
                x=x0+5
                for wd in r: font.text(d,wd,x,y0+3+i*10,ACC if wd.upper().strip('.,!?') in {'BOO','\'BOO\'','LANTERN','PANICKED','DARK','NIGHTLIGHT'} or wd.upper() in HIL else WHT,1,None); x+=font.width(wd,1)+6
def ui_box(d,lines,y,col,sc=2,blink=0):
    w=max(font.width(l,sc) for l in lines)+12; x0=(W-w)//2; h=len(lines)*(7*sc+3)+8
    d.rectangle([x0,y,x0+w,y+h],fill=(8,8,20),outline=col); d.rectangle([x0+2,y+2,x0+w-2,y+h-2],outline=(60,60,100))
    for i,l in enumerate(lines): font.ctext(d,l,y+5+i*(7*sc+3),col,W,sc)
def ui(d,t):
    if 10.6<=t<13.0: ui_box(d,['ATTEMPT 1:','FAILED'],8,(255,90,90))
    if 19.0<=t<21.0: ui_box(d,['ATTEMPT 2:','FAILED'],8,(255,90,90))
    if 44.3<=t<46.0 and int(t*12)%2==0 or 44.3<=t<44.8: ui_box(d,['SCARE','SUCCESS!'],8,ACC)
    if 57.4<=t<60.0:
        pulse=1 if int(t*6)%2 else 0; ui_box(d,['NIGHTLIGHT','UNLOCKED'],8,(255,226,120) if pulse else ACC)
def knock_marks(d,t,gs,cam,fov):
    for tk in T_KNOCK:
        u=(t-tk)/0.22
        if 0<=u<1:
            h=ghost_hand(gs,1); pr=R.project(tuple(h),R.view(cam,fov))
            if not pr: continue
            r=3+6*u; c=(int(220*(1-u)+60),int(220*(1-u)+60),int(255*(1-u)+80))
            for ang in range(0,360,45):
                a=math.radians(ang); x0,y0=pr[0]+math.cos(a)*r*0.5,pr[1]+math.sin(a)*r*0.5; d.line([x0,y0,pr[0]+math.cos(a)*r,pr[1]+math.sin(a)*r],fill=c,width=1)
def frame(t,to=None):
    """t = story time; to = output time (subtitles follow the voices, which play in output time)"""
    to=OUTT(t) if to is None else to
    if to>=DUR_OUT-1e-9: return Image.new('RGB',(W,H),(0,0,0))
    img,gs,js,ls,cam,fov=render(t); d=ImageDraw.Draw(img); knock_marks(d,t,gs,cam,fov)
    ui(d,t); subtitles(d,to); return img

# ======================= QA manifest =======================
def _verts(Q): return np.array([p for q in Q for p in q['p']])
def _extra(t):
    out=[]; gs=ghost_state(t); ls=lantern_state(t)
    if t<0.05:
        for nm,p in (('ghost',np.array(gs['base'])+np.array([0,0.6,0])),('janitor',np.array(jan(t)['base'])+np.array([0,0.9,0]))):
            cp,tg,fov=cam_shot(t); pr=R.project(tuple(p),R.view(Camera.look(cp,tg),fov))
            if not pr or not (0<pr[0]<W and 0<pr[1]<H): out.append(('camera',f'{nm} is not in the first frame'))
    if t<T_CUT7:                                                                          # ghost must never touch the lantern before the scare
        G=_verts(ghost(**gs)[0]); lp=np.array(ls['pos']); lo=lp-np.array([0.085,0.14,0.085]); hi=lp+np.array([0.085,0.17,0.085])
        dist=np.maximum(np.maximum(lo-G,G-hi),0).max(axis=1) if False else np.linalg.norm(np.maximum(np.maximum(lo-G,G-hi),0),axis=1)
        if dist.min()<0.03: out.append(('lantern',f'ghost touches the lantern before the scare ({dist.min()*100:.1f} cm)'))
    if t>=46.0 and t<53.0 and np.linalg.norm(np.array(ls['pos'])-(np.array(LANTERN_FLOOR)+[0,0.14,0]))>1e-6: out.append(('lantern','lantern moved while lying on the floor'))
    cp=cam_shot(t)[0]
    if t>=46.6 and t<53.0 and jan(t)['base'][0]<cp[0]+1.1 and False: out.append(('janitor','janitor still in frame'))
    return out
def _lantern_events():
    return []
QA=dict(fps=FPS,dur=DUR,W=W,frame=lambda t: frame(t),chars={'ghost':(ghost_state,ghost_model,'_none',1.0),'janitor':(jan,jan_model,'_none',1.0)},
    geom=lambda t,name,st,V: [('floor',f'{name} under the floor')] if V[:,1].min()<-0.04 else ([('wall',f'{name} inside the back wall')] if V[:,2].max()>WALL_Z-0.0 else ([('wall',f'{name} inside the end wall')] if V[:,0].min()<X_ENDWALL+0.02 else [])),
    extra=_extra,camera=lambda t: cam_shot(t)[0],min_cam_dist=0.4,camera_ok=lambda p: -6.0<p[2]<-0.5 and 0.1<p[1]<1.7,
    allow_jump=[('janitor',46.0),('ghost',21.0)],weapon_events=[],
    scenes=[dict(id='hook',t0=0.0,t1=5.0,action='ghost already floating toward the janitor with the lantern; raises a hand (cam A)'),
            dict(id='whisper',t0=5.0,t1=13.0,action='ghost floats closer, "Excuse me?", ignored, disappointed (cam A)'),
            dict(id='knock',t0=13.0,t1=21.0,action='ghost knocks the wall 3x, janitor glances, shrugs, walks on (cam A)'),
            dict(id='flicker',t0=21.0,t1=30.0,action='lantern flickers twice; ghost trembles, then relaxes (cam B)'),
            dict(id='motive',t0=30.0,t1=38.0,action='dark corner, lantern, reaches, gathers courage (cam B)'),
            dict(id='scare',t0=38.0,t1=46.0,action='ghost dashes in front, BOO lunge, janitor hops (cam A)'),
            dict(id='left_behind',t0=46.0,t1=53.0,action='hard cut: lantern on the floor, janitor flees right, ghost approaches (cam A)'),
            dict(id='payoff',t0=53.0,t1=60.0,action='ghost lifts the lantern, curls up beside it; NIGHTLIGHT UNLOCKED (cam C)')],
    texts=lambda: [('ui',l,1) for _,_,rows,_ in SUBS for l in [' '.join(r) for r in rows]]+[('ui',l,2) for l in ('ATTEMPT 1:','ATTEMPT 2:','FAILED','SCARE','SUCCESS!','NIGHTLIGHT','UNLOCKED')])

TEST=os.environ.get('TEST')
if TEST and __name__=='__main__':
    ims=[frame(float(x)) for x in TEST.split(',')]; shp=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): shp.paste(im,(i*182,0))
    shp.resize((shp.width*2,640),Image.NEAREST).save('test.png'); sys.exit()


# ======================= AUDIO: synthesized mystery loop, corridor ambience, foley, voices =======================
def _steps_walk():
    ev=[]; k=0
    while True:
        d=(k+0.5)*0.19
        if d>_CUM[-1] or d>_dist(46.0): break
        i=int(np.searchsorted(_CUM,d)); ev.append(float(_TS[min(i,len(_TS)-1)])); k+=1
    return [t for t in ev if t<46.0]
def build_audio(path):
    """mix: synthesized retro mystery music (never drops out), corridor bed, foley, NON-VERBAL ghost noises that fill every gap
    (no extra dialogue), retro UI sounds, then the voices. The BOO gets a clear window: everything else ducks under it and the sting follows it."""
    import soundfile as _sf
    s=Sound(DUR_OUT,loop=False,seed=61); sr=s.sr; n=s.n; M=np.zeros(n); AMB=np.zeros(n); X=np.zeros(n)
    _pl=s.place; s.place=lambda x,t0,v=1.0,pan=0.0: _pl(x,OUTT(t0),v,pan)                    # every SFX is cued in story time -> output time
    def hz(m): return 440*2**((m-69)/12)
    def note(buf,t0,m,d,v,wave='tri',dec=3.0,att=0.005):
        tt=s.T(d); f=hz(m); ph=2*np.pi*f*tt
        x={'sin':np.sin(ph),'tri':(2/np.pi)*np.arcsin(np.sin(ph)),'bell':np.sin(ph)+0.35*np.sin(2*ph)+0.12*np.sin(3.01*ph),'saw':sum(np.sin(ph*(k+1))/(k+1) for k in range(5))*0.6,'sq':np.sign(np.sin(ph))*0.5}[wave]
        env=np.minimum(1,tt/att)*np.exp(-tt*dec); i=int((OUTT(t0) if buf is X else t0)*sr); j=min(n,i+len(tt)); buf[i:j]+=(x*env*v)[:j-i]   # music notes are in output time, UI notes in story time
    def tone(t0,f0,f1,d,v,vib=0.0,harm=(1.0,0.5,0.25),att=0.01,dec=0.0,buf=None,vr=7.0):
        tt=s.T(d); fr=f0+(f1-f0)*(tt/d); fr=fr*(1+vib*np.sin(2*np.pi*vr*tt)); ph=np.cumsum(fr)/sr
        x=sum(h*np.sin(2*np.pi*ph*(k+1)) for k,h in enumerate(harm)); env=np.minimum(1,tt/att)*np.sin(np.pi*np.clip(tt/d,0,1))**0.6*np.exp(-tt*dec)
        if buf is None: s.place(x*env,t0,v)
        else: i=int(t0*sr); j=min(n,i+len(tt)); buf[i:j]+=(x*env*v)[:j-i]
    def nb(t0,d,lo,hi,v,seed,shape=2): s.place(s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v)
    def thud(t0,f=70,v=0.1,d=0.2): tt=s.T(d); s.place(np.sin(2*np.pi*f*tt*(1-0.3*tt/d))*np.exp(-tt*16),t0,v)
    def step(t0,v=0.06,seed=0): thud(t0,85,v,0.12); nb(t0+0.005,0.06,600,3200,v*0.6,seed,1)
    def knock(t0,v=0.3): tt=s.T(0.25); s.place((np.sin(2*np.pi*150*tt)+0.5*np.sin(2*np.pi*310*tt))*np.exp(-tt*24),t0,v); nb(t0,0.03,800,4000,v*0.4,int(t0*77),1)
    def zap(t0,d,v=0.08): tt=s.T(d); s.place(np.sign(np.sin(2*np.pi*(110+400*np.random.default_rng(int(t0*10)).random())*tt))*np.exp(-tt*18)*np.abs(s.noise(d,int(t0*13))),t0,v)
    # ---- ghost: small non-verbal voice (formant-ish 'oo' tones), always soft ----
    def oo(t0,f0,f1,d,v=0.06,vib=0.03): tone(t0,f0,f1,d,v,vib=vib,harm=(1.0,0.45,0.18,0.06),att=0.04)
    def squeak(t0,v=0.06): tone(t0,1200,2600,0.1,v,harm=(1.0,0.4),att=0.004); tone(t0+0.11,2600,1800,0.1,v*0.8,harm=(1.0,0.4),att=0.004)
    def sigh(t0,d=0.7,v=0.05): nb(t0,d,300,2200,v,int(t0*31),1.2); oo(t0+0.05,520,360,d*0.8,v*0.6,0.01)
    def breath_in(t0,d=0.5,v=0.04): nb(t0,d,900,5000,v,int(t0*37),0.8)
    def whoosh(t0,d=0.45,v=0.07):
        x=s.noise(d,int(t0*41)); tt=s.T(d); y=np.zeros_like(x)
        for k_,(lo,hi) in enumerate(((300,900),(600,1800),(1200,3600))): y+=s.filt_short(x,lo=lo,hi=hi)*np.exp(-((tt/d-0.25-0.25*k_)**2)/0.02)
        s.place(y*np.sin(np.pi*tt/d),t0,v)
    def chirp(t0,v=0.06,up=True): tone(t0,700 if up else 1100,1100 if up else 700,0.16,v,harm=(1.0,0.4,0.15),att=0.01)
    def ui_fail(t0): [note(X,t0+i*0.16,m,0.22,0.05,'sq',6.0) for i,m in enumerate((67,63,58))]
    def ui_success(t0): [note(X,t0+i*0.07,m,0.3,0.045,'sq',5.0) for i,m in enumerate((72,76,79,84))]
    # ---- corridor bed: low air + distant drips + soft wind swell ----
    AMB+=s.filt(s.rng.normal(0,1,n),lo=40,hi=300)*0.07+s.filt(s.rng.normal(0,1,n),lo=1800,hi=5000)*0.003
    for tt0 in (2.3,7.7,12.6,18.4,20.3,26.2,29.4,33.5,36.9,41.6,49.2,52.0,55.6): tt=s.T(0.18); s.place(np.sin(2*np.pi*(1500-900*tt/0.18)*tt)*np.exp(-tt*30),tt0,0.02)
    # ---- lantern hum: a soft warm buzz whenever the lantern is lit and on screen (drops out on each flicker) ----
    tt=s.t; hum=(np.sin(2*np.pi*120*tt)+0.4*np.sin(2*np.pi*240*tt)+0.15*np.sin(2*np.pi*360*tt))*(1+0.25*np.sin(2*np.pi*0.8*tt))
    g=np.ones(n)*0.010
    for a_,b_ in T_FLICK: g[int(OUTT(a_)*sr):int(OUTT(b_)*sr)]=0
    g[int(OUTT(21.0)*sr):int(OUTT(38.0)*sr)]*=1.8                                              # close-up: louder
    g[int(OUTT(53.0)*sr):]*=1.6
    AMB+=hum*np.convolve(g,np.ones(480)/480,'same')
    # ================= MUSIC (continuous, 120 bpm, written in OUTPUT time so the tempo stays steady through the speed-ups) =================
    o21,o30,o38,o44,o447,o46,o53,o575=[OUTT(x) for x in (21.0,30.0,38.0,43.95,44.72,46.3,53.0,57.5)]
    def mpl(x,to,v): i=int(to*sr); j=min(n,i+len(x)); M[i:j]+=(x*v)[:j-i]
    def hat(to,v,seed): d=0.03; mpl(s.filt_short(s.noise(d,seed),lo=6000,hi=12000)*np.sin(np.pi*s.T(d)/d),to,v)
    B=0.5
    bass=[45,48,52,48,45,47,52,47, 41,45,48,45,40,44,47,44]; mel=[76,0,72,74,76,0,79,77, 76,0,72,71,69,0,0,0]
    for k in range(int(o21/(B/2))):                                                    # playful suspense
        t0=0.05+k*B/2
        if k%2==0: note(M,t0,bass[(k//2)%16],0.45,0.06,'tri',5.0)
        m=mel[k%16]
        if m: note(M,t0,m,0.35,0.026,'bell',6.0)
        hat(t0,0.006 if k%2 else 0.004,500+k)
    for k in range(int((o38-o21)/B)): note(M,o21+k*B,[38,38,41,40][(k//2)%4],0.5,0.06,'tri',3.5)          # darker pulse + tremolo pad
    pad=np.zeros(n); tone(o21,hz(50),hz(50),o38-o21,0.03,vib=0.004,harm=(1.0,0.5,0.3),att=1.0,buf=pad)
    tone(o21,hz(53),hz(53),o38-o21,0.022,vib=0.004,harm=(1.0,0.4),att=1.2,buf=pad); M+=pad*(1+0.35*np.sin(2*np.pi*5*s.t))
    for t0 in np.arange(23.2,26.6,0.5): thud(t0,55,0.07,0.15); thud(t0+0.16,50,0.05,0.12)                     # heartbeat (story time)
    for k,m in enumerate((69,72,76,74,72,69,68,0,69,72,76,79,77,76,74,0)):
        if m and o30+k*0.4<o38: note(M,o30+k*0.4,m,0.45,0.018,'bell',4.0)
    t0=o38; k=0                                                                         # comic tension: chromatic ostinato speeding up
    while t0<o44: note(M,t0,45+(k%12),0.12,0.035,'sq',14.0); note(M,t0,57+(k%12),0.1,0.014,'bell',14.0); t0+=lerp(0.3,0.09,(t0-o38)/(o44-o38)); k+=1
    tone(OUTT(41.5),80,160,o44-OUTT(41.5),0.03,harm=(1.0,0.5),att=0.3,buf=M)
    for m in (57,60,63,66): note(M,o447,m,0.5,0.05,'saw',3.5,0.003)                    # sting right AFTER the BOO
    thud(44.72,60,0.3,0.5); nb(44.72,0.4,500,5000,0.07,901,0.7)
    for i,m in enumerate((55,53,51,48)): note(M,o447+0.28+i*0.2,m,0.32,0.035,'sq',4.0)  # comic wah-wah
    for k in range(int((o53-o46)/0.25)):                                                # tiptoe
        t0=o46+k*0.25
        if k%2==0: note(M,t0,[40,47,45,47][(k//2)%4],0.3,0.05,'tri',5.0)
        if k%4==1: note(M,t0,[64,67,71,72][(k//4)%4],0.3,0.025,'bell',6.0)
    for k,m in enumerate((72,76,79,84,79,76,72,76,79,84,88,84,91)):                    # warm music box + pad, resolving chord
        if o53+0.05+k*0.3<DUR_OUT: note(M,o53+0.05+k*0.3,m,1.0,0.034,'bell',2.6)
    for m in (48,55,60,64): note(M,o53,m,o575-o53+0.5,0.025,'sin',0.5,0.6)
    for m in (48,55,60,64,67,72): note(M,o575,m,2.5,0.032,'sin',0.9,0.01)
    # ================= SFX / FOLEY =================
    for i,t0 in enumerate(_steps_walk()): step(t0,0.06,i)
    for i,t0 in enumerate((46.12,46.34,46.62,46.8,46.99,47.17)): step(t0,0.09,200+i)
    for t0 in T_KNOCK: knock(t0)
    for a_,b_ in T_FLICK: zap(a_,0.1); zap(b_,0.14); nb(a_,b_-a_,2500,9000,0.02,int(a_*7),1)
    tone(44.78,170,110,0.3,0.1,harm=(1.0,0.6,0.3),att=0.01)                                                          # janitor 'uh!' (after the BOO)
    thud(45.05,70,0.12,0.2); nb(44.78,0.45,200,1800,0.035,909,1)
    tt=s.T(0.35); s.place((np.sin(2*np.pi*1900*tt)+0.6*np.sin(2*np.pi*2870*tt))*np.exp(-tt*22),46.0,0.1); thud(46.0,60,0.12,0.15)  # lantern on the floor
    tt=s.T(0.3); s.place((np.sin(2*np.pi*1400*tt)+0.5*np.sin(2*np.pi*2100*tt))*np.exp(-tt*16),54.05,0.05)              # lifted
    tt=s.T(0.3); s.place((np.sin(2*np.pi*1700*tt)+0.5*np.sin(2*np.pi*2500*tt))*np.exp(-tt*20),55.95,0.06); thud(55.95,90,0.05,0.1)  # set down
    # ghost: floating shimmer while it moves, and its little noises (no words) in every gap
    for t0 in (0.0,5.0,13.3,42.9,48.6): whoosh(t0,0.6,0.05)
    oo(0.7,420,520,0.6,0.045); chirp(3.6,0.05)                                       # hum, then a small 'hm!' as it raises its hand
    oo(7.4,620,420,0.7,0.06,0.05)                                                     # disappointed 'aww'
    sigh(11.6,0.8,0.05); oo(12.5,380,330,0.5,0.035)
    chirp(16.55,0.065); chirp(16.8,0.05)                                              # hopeful 'oh! oh!'
    sigh(19.2,0.9,0.06); oo(20.2,400,350,0.6,0.035)
    squeak(23.25,0.07); squeak(24.45,0.06)
    oo(24.8,700,760,1.2,0.04,0.09); oo(25.5,760,700,0.9,0.035,0.1)                   # trembling whimper
    sigh(26.65,0.8,0.06); oo(27.6,480,620,0.5,0.045); oo(28.3,560,640,0.45,0.04)      # relieved, then a happy little 'mm-mm'
    oo(29.2,600,520,0.5,0.03)
    oo(30.4,520,470,1.0,0.04,0.08)                                                    # uneasy whimper at the dark corner
    chirp(32.9,0.05)                                                                  # sees the lantern again
    oo(34.1,450,700,0.9,0.045)                                                        # reaching 'nnngh'
    oo(35.6,600,420,0.6,0.04)                                                         # lowers its arms
    breath_in(36.4,0.9,0.06)                                                          # gathers courage
    oo(38.4,560,520,1.4,0.035,0.08); breath_in(42.2,0.5,0.045); breath_in(43.3,0.6,0.06)
    chirp(47.4,0.06,False); oo(47.7,500,760,0.5,0.045)                                # surprised 'oh?'
    oo(49.6,480,560,0.5,0.035); oo(51.0,520,600,0.5,0.035); oo(52.3,560,700,0.6,0.04)
    oo(53.5,480,600,0.35,0.045); oo(54.1,500,620,0.4,0.05)                            # 'hup' lifting
    oo(56.1,600,700,0.6,0.045); sigh(56.9,1.0,0.045); oo(58.8,560,620,0.7,0.035)      # contented hum, sleepy sigh
    ui_fail(10.6); ui_fail(19.0); ui_success(44.95)
    for i,m in enumerate((84,88,91,96)): note(X,57.45+i*0.09,m,0.9,0.06,'bell',3.0)    # happy UI chime
    note(X,57.45,100,1.2,0.035,'bell',3.5)
    s.L+=AMB; s.R+=np.roll(AMB,900)
    # ================= VOICES =================
    NB=np.zeros(n); duck=np.ones(n)
    for key,t0,_ in LINES:
        a,ar=_sf.read(os.path.join(TTS_DIR,'gb',key+'.wav')); a=a if a.ndim==1 else a.mean(1)
        act=a[np.abs(a)>0.02]; g=0.2/(np.sqrt((act**2).mean())+1e-9)*{'G2':1.35,'G1':1.1}.get(key,1.0); a=a*g
        i=int(OUTT(t0)*sr); j=min(n,i+len(a)); NB[i:j]+=a[:j-i]; duck[max(0,i-int(0.08*sr)):min(n,j+int(0.15*sr))]=0.6
    duck=np.convolve(duck,np.ones(2400)/2400,'same')
    s.L+=M*duck*3.4+X; s.R+=np.roll(M,300)*duck*3.4+X
    s.reverb(0.12,length=1.0,decay=4.0)
    clear=np.ones(n); clear[int(OUTT(43.95)*sr):int(OUTT(44.72)*sr)]=0.2; clear=np.convolve(clear,np.ones(960)/960,'same')         # the BOO window
    pk=max(np.abs(s.L).max(),np.abs(s.R).max()); gv=pk/np.abs(NB).max()*0.95
    s.L=s.L*clear*(0.8+0.2*duck)+NB*gv; s.R=s.R*clear*(0.8+0.2*duck)+NB*gv
    st=np.stack([s.L,s.R],1); k=int(0.05*sr); st[-k:]*=np.linspace(1,0,k)[:,None]
    st=st/np.max(np.abs(st))*0.9; _sf.write(path,st,sr,subtype='PCM_16'); return path
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'ghost_boo.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'gb_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.96,vignette=0.25,grain=1.5,band_period=1e9)
    for f in range(a,min(b,N_OUT)): p.stdin.write(vhs(post.upscale(frame(SRC(f/FPS),f/FPS),S),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
