"""WHY DO MIRRORS COPY US?  PS1 surreal mystery / light comedy short, 9:16, exactly 60 s (1440 frames @ 24 fps). Fully procedural (nightkit).
LOCKED ASSETS: robot() (small orange robot, the ONLY 3D character; poses are parameters of one pose dict), mirror_room() (flat wooden floor, plain dark-blue wall,
wooden mirror frame, square ceiling lamp), reflection() (2D pale-blue sprite drawn inside the mirror rectangle from the SAME pose dict; its timing is a lagged,
rate-limited follower of the robot's pose, with freeze / rest / independent phases). Text, UI, subtitles are 2D overlays after the 3D render.
Cameras: A main room view (shots 1-4, 6, 8, 9), B mirror close-up (shots 5, 7). Hard cuts only, both fixed.
Scene axes: +x = right of the screen; the mirror hangs on the back wall (z = WALL_Z) at the right; the robot stands left of it facing it (3/4 towards the camera).
Voice: python tools/tts/mc.py -> $TTS_DIR/mc/*.wav (one file per sentence; the cues below are placed from the MEASURED lengths).
Run: TEST=0.1,6,20 python examples/mirror_copy.py -> test.png | PART=a:b | PART=audio      QA: python tools/qa/scene_qa.py examples/mirror_copy.py"""
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
def env(t,a,b,ra=0.3,rb=0.3): return FT.win(t,a,b,ra,rb)
TTS_DIR=FT.TTS_DIR; OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6; DUR=60.0; N=int(round(DUR*FPS)); N_OUT=N
try: SCR=json.load(open(os.path.join(TTS_DIR,'mc','script.json')))
except Exception: SCR=None

# ======================= narration schedule (from the MEASURED sentence lengths) =======================
ORDER=['1a','1b','2a','2b','3a','3b','3c','4a','4b','5a','5b','5c','6a','6b','7a','7b','7c','8a','9a','9b','9c']
TEXT={'1a':"Why do mirrors copy us?",'1b':"This little robot thought he knew.",'2a':"Every morning, he waved at his reflection.",'2b':"But today, the wave came back a second late.",
      '3a':"He tried again.",'3b':"One arm up. One arm down.",'3c':"Somehow, the reflection kept getting further behind.",'4a':"He tried a silly dance.",
      '4b':"Halfway through, his reflection froze with both arms in the air.",'5a':"A message appeared on the glass: BREAK REQUESTED.",'5b':"The robot blinked.",
      '5c':"Wait... reflections can get tired?",'6a':"He waved again. Nothing.",'6b':"The figure on the other side lowered its arms and refused to move.",
      '7a':"That was when he understood.",'7b':"The mirror wasn't magical.",'7c':"Someone inside had been copying him all day.",
      '8a':"So, for once, he stood completely still and let his exhausted little reflection rest.",'9a':"Then the reflection moved first.",'9b':"YOUR TURN.",'9c':"And he had to copy it."}
DURS={k:(SCR['dur'][k] if SCR else 2.0) for k in ORDER}
GAP=(DUR-0.2-sum(DURS.values()))/(len(ORDER)-1)      # equal pauses between sentences (< 0.5 s) so the narration runs through the whole minute
ST={}; _t=0.05
for k in ORDER: ST[k]=_t; _t+=DURS[k]+GAP
def s(k,o=0.0): return ST[k]+o
_first={}
for k in ORDER: _first.setdefault(int(k[0]),k)
CUTS=[0.0]+[round((ST[_first[i]]-GAP/2)*FPS)/FPS for i in range(2,10)]+[DUR]     # shot i = CUTS[i-1] .. CUTS[i]
def shot_of(t):
    for i in range(1,10):
        if t<CUTS[i]: return i
    return 9
def cam_id(t): return 'B' if shot_of(t) in (5,7) else 'A'

# ======================= palette =======================
ORG=(236,124,30); ORG_D=(196,92,20); ORG_L=(250,152,52); GREY=(84,88,102); BLK=(14,12,20); BLUE=(60,110,235)
SP_BODY=(138,186,232); SP_D=(98,146,200); SP_L=(168,210,248)                   # reflection: pale-blue tint of the same robot
WOOD=[(150,100,56),(132,86,46),(142,94,52)]; WALL=(30,42,96); WALL_D=(22,30,72); FRAME=(120,78,40); FRAME_D=(88,54,28); MIRBG=(14,20,40); LAMP=(255,240,180)

# ======================= LOCKED ASSET: the robot =======================
RB=(0.0,0.0,0.35); YAW=2.3                                    # stands left of the mirror, 3/4 towards the camera, facing the mirror
IDLE=dict(aW=0.14,bW=0.0,aO=0.14,bO=0.0,hop=0.0,roll=0.0,hyaw=-0.15,hp=0.0,eyes=1.0,happy=False,smile=False)
NECK=0.69
def arm_dir(a,sx): return np.array([sx*math.sin(a),-math.cos(a),0.0])
def robot(pose,base=RB,yaw=YAW):
    """small orange robot, ~1.02 m: square head, rectangular torso, two segmented arms, two short legs, two black square eyes, a flat mouth, blue chest square.
    pose keys: aW/aO = shoulder angle of the arm nearer the camera / the mirror (0 hanging, pi/2 sideways, pi up), bW/bO = elbow bend, hop, roll/hyaw/hp = head roll/yaw/pitch,
    eyes 0..1, happy, smile. returns (quads, face decals)"""
    p=pose; b=np.array(base,float); Rb=Ry(yaw)
    sq=p.get('sq',0.0)                                                                 # optional squash & stretch (v2 cut); 0 = the locked proportions
    def Wd(q): q=np.array(q,float); q=np.array([q[0]*(1+0.10*sq),q[1]*(1-0.18*sq),q[2]*(1+0.10*sq)]); return tuple(b+np.array([0,p['hop'],0])+Rb@q)
    N_=np.array([0,NECK,0]); Rh=Ry(p['hyaw'])@Rx(p['hp'])@Rz(p['roll'])
    def Hd(q): return Wd(N_+Rh@(np.array(q,float)-N_))
    Q=[]; D=[]; Dc=[]
    for sx in (-1,1): Q+=box(sx*0.115-0.065,sx*0.115+0.065,0.0,0.28,-0.07,0.07,ORG_D,xf=Wd)+box(sx*0.115-0.065,sx*0.115+0.065,0.0,0.04,-0.07,0.11,GREY,xf=Wd)
    Q+=box(-0.22,0.22,0.28,0.68,-0.13,0.13,ORG,xf=Wd)+box(-0.16,0.16,0.68,0.70,-0.09,0.09,GREY,xf=Wd)
    Q+=box(-0.16,0.16,0.70,1.02,-0.15,0.15,ORG_L,xf=Hd)
    fz=0.1515; eh=0.07*max(p['eyes'],0.14)
    for sx in (-1,1):
        ex=sx*0.075; ey=0.88
        if p['happy']: D+=box(ex-0.035,ex+0.035,ey+0.0,ey+0.016,fz,fz+0.002,BLK,xf=Hd)+box(ex-0.035,ex-0.02,ey-0.02,ey+0.0,fz,fz+0.002,BLK,xf=Hd)+box(ex+0.02,ex+0.035,ey-0.02,ey+0.0,fz,fz+0.002,BLK,xf=Hd)
        else: D+=box(ex-0.034,ex+0.034,ey-eh/2,ey+eh/2,fz,fz+0.002,BLK,xf=Hd)
    if p.get('mouth_o'): D+=box(-0.035,0.035,0.745,0.815,fz,fz+0.002,BLK,xf=Hd)                        # surprised 'o' mouth (v2 cut)
    else: D+=box(-0.06,0.06,0.77,0.79,fz,fz+0.002,BLK,xf=Hd)
    if p['smile']: D+=box(-0.075,-0.06,0.79,0.81,fz,fz+0.002,BLK,xf=Hd)+box(0.06,0.075,0.79,0.81,fz,fz+0.002,BLK,xf=Hd)
    tag(D,Hd((0,0.86,0)))
    Dc+=box(-0.055,0.055,0.44,0.55,0.1315,0.1335,BLUE,xf=Wd); tag(Dc,Wd((0,0.5,0)))
    for sx,a,bd in ((1,p['aW'],p['bW']),(-1,p['aO'],p['bO'])):
        sh=np.array([sx*0.26,0.60,0.0]); el=sh+arm_dir(a,sx)*0.20; ha=el+arm_dir(a+bd*sx,sx)*0.18
        Q+=transform(seg(tuple(sh),tuple(el),0.08,ORG_D,0.08)+seg(tuple(el),tuple(ha),0.075,ORG,0.075)+box(-0.045,0.045,-0.045,0.045,-0.045,0.045,GREY,xf=lambda q,ha=ha: tuple(ha+np.array(q))),Wd)
    return Q,D+Dc
def robot_state(t): return dict(base=RB,yaw=YAW,**real_pose(t))
def robot_model(**st): return robot({k:v for k,v in st.items() if k not in ('base','yaw')})[0]

# ======================= LOCKED ENVIRONMENT: the mirror room =======================
WALL_Z=1.25; MX=0.85; MW=1.0; MY0=0.3; MY1=2.0                  # inner mirror rectangle: x MX +- MW/2, y MY0..MY1
ZM=WALL_Z-0.035
LAMP_POS=(0.35,2.35,0.7)
def mirror_room():
    F=tiled_plane(-3.0,3.0,-5.0,WALL_Z,0.0,0.4,lambda i,j:WOOD[(i+(j//3))%3])
    Wl=box(-3.2,3.2,0,3.4,WALL_Z,WALL_Z+0.05,WALL)+box(-3.2,3.2,0,0.14,WALL_Z-0.04,WALL_Z,WALL_D)
    Wl+=box(-3.25,-3.0,0,3.4,-5.0,WALL_Z+0.05,WALL)+box(3.0,3.25,0,3.4,-5.0,WALL_Z+0.05,WALL)+box(-3.2,3.2,3.4,3.6,-5.0,WALL_Z+0.05,WALL_D)
    x0,x1=MX-MW/2,MX+MW/2; fw=0.11
    Fr=box(x0-fw,x1+fw,MY0-fw,MY0,ZM-0.06,WALL_Z,FRAME)+box(x0-fw,x1+fw,MY1,MY1+fw,ZM-0.06,WALL_Z,FRAME)+box(x0-fw,x0,MY0,MY1,ZM-0.06,WALL_Z,FRAME_D)+box(x1,x1+fw,MY0,MY1,ZM-0.06,WALL_Z,FRAME_D)
    Fr+=box(x0,x1,MY0,MY1,ZM,ZM+0.005,MIRBG,emit=True)                                           # flat mirror panel (the sprite is composited on it in 2D)
    Lp=box(LAMP_POS[0]-0.25,LAMP_POS[0]+0.25,LAMP_POS[1],LAMP_POS[1]+0.06,LAMP_POS[2]-0.25,LAMP_POS[2]+0.25,LAMP,emit=True)+box(LAMP_POS[0]-0.015,LAMP_POS[0]+0.015,LAMP_POS[1]+0.06,3.5,LAMP_POS[2]-0.015,LAMP_POS[2]+0.015,GREY)
    return F,Wl,Fr,Lp
ROOM_F,ROOM_W,ROOM_FR,ROOM_L=mirror_room()
def cam_shot(t):
    if cam_id(t)=='A': return (0.38,1.25,-2.75),(0.38,1.0,1.25),31.0
    return (0.58,1.2,-1.1),(0.58,1.05,1.25),42.0

# ======================= animation: the real robot =======================
UP=2.85
def real_pose(t):
    p=dict(IDLE)
    w1=1-sm(seg01(t,s('1b',1.2),s('1b',1.6)))                                                       # shot 1: already waving in frame 0
    w2=env(t,s('2a',0.6),s('2b',0.4),0.4,0.4)                                                       # shot 2: waves again
    w6=max(env(t,s('6a',0.15),s('6a',0.95),0.25,0.25),env(t,s('6a',1.4),s('6b',0.3),0.25,0.25))      # shot 6: two tries
    wave=max(w1,w2,w6); ph=2*PI*2.6*t
    up=max(env(t,s('3a',0.1),s('3b',1.1),0.5,0.5),env(t,s('4a',0.2),s('4b',1.4),0.4,0.45),sm(seg01(t,s('9c',0.2),s('9c',0.6))))     # both arms: experiment, dance, copy
    p['aW']=lerp(0.14,UP,up) if up>=wave else lerp(0.14,2.25,wave)
    p['bW']=wave*0.55*math.sin(ph)*(0.7 if (w6>0 and wave==w6) else 1.0)
    p['aO']=lerp(0.14,UP,up)
    p['hop']=0.07*abs(math.sin(2*PI*1.7*(t-s('4a',1.0))))*env(t,s('4a',1.0),s('4b',1.25),0.05,0.05)+0.07*math.sin(PI*seg01(t,s('9c',0.95),s('9c',1.4)))
    p['roll']=0.3*max(env(t,s('1b',0.4),s('1b',1.6)),env(t,s('2b',1.0),s('2b',2.6)),env(t,s('3c',0.1),s('3c',1.7)),0.6*env(t,s('4b',2.2),s('4b',3.9)),env(t,s('5a',2.0),s('5b',1.0)),0.7*env(t,s('9b',0.1),s('9b',0.8)))
    hs=0.35*math.sin(2*PI*1.5*(t-s('9b',0.1)))*env(t,s('9b',0.1),s('9b',0.9),0.1,0.1)                  # hesitates: looks around
    p['hyaw']=-0.15-0.25*env(t,s('4b',2.0),s('5a',0.0))-0.2*env(t,s('7a',0.0),s('7c',2.5))+hs
    p['hp']=0.18*env(t,s('7a',0.2),s('7b',1.5))+0.35*math.sin(PI*seg01(t,s('8a',4.2),s('8a',5.3)))
    bl=math.sin(PI*seg01(t,s('5b',0.3),s('5b',0.5)))+math.sin(PI*seg01(t,s('2a',2.2),s('2a',2.4)))+math.sin(PI*seg01(t,s('7c',0.4),s('7c',0.6)))
    p['eyes']=1.0-min(1.0,bl); p['smile']=s('8a',4.1)<=t<s('9a',0.0)
    return p

# ======================= animation: the reflection (2D sprite driven by the same pose dict) =======================
T_FREEZE=s('4b',1.55); T_REST=s('5b',0.0); T9=s('9a',0.0)
def lag(t):
    if t<s('3a'): return 1.0
    if t<s('4a'): return lerp(1.6,2.0,seg01(t,s('3a'),s('4a')))
    return 2.0
def vmax(t):
    if t<s('3a'): return 7.0
    if t<s('4a'): return 2.2
    if t<T_FREEZE: return 2.2
    if t<T9: return 1.2
    return 8.0
def ref_target(t):
    if t<T_FREEZE:
        tau=t-lag(t); return dict(IDLE) if tau<0 else real_pose(tau)               # copies the robot LATE (arm down until the first delayed wave)
    if t<T_REST: return dict(IDLE,aW=UP,aO=UP)                                         # frozen with both arms in the air
    if t<T9: return dict(IDLE,hop=0.012*(0.5+0.5*math.sin(2*PI*0.4*t)))                # arms lowered, refuses to move (tiny breathing while resting)
    u=sm(seg01(t,s('9a',0.7),s('9a',1.2)))                                            # role reversal: moves FIRST
    return dict(IDLE,aW=lerp(0.14,UP,u),aO=lerp(0.14,UP,u),hop=0.07*math.sin(PI*seg01(t,s('9c',0.55),s('9c',1.0))))
_DT=1/240.; _TS=np.arange(0,DUR+1,_DT); _K=('aW','bW','aO','bO','hop','roll')
def _sim():
    X={k:np.zeros(len(_TS)) for k in _K}; x={k:IDLE[k] for k in _K}
    for i,t in enumerate(_TS):
        tg=ref_target(t); vm=vmax(t)*_DT
        for k in _K: x[k]+=float(np.clip(14*(tg[k]-x[k])*_DT,-vm,vm)); X[k][i]=x[k]
    return X
_SIM=_sim()
def ref_eyes(t):
    """(openness 0..1, happy). progressively more tired -> eyes lowered -> slow blink -> rest -> small happy -> alert"""
    e=1.0-0.25*seg01(t,s('3a'),s('4a'))-0.15*seg01(t,s('4a'),T_FREEZE)
    e=lerp(e,0.2,sm(seg01(t,s('5a',0.4),s('5a',2.6)))) if t>=s('5a',0.4) else e
    if t>=s('6a'): e=lerp(0.2,0.4,sm(seg01(t,s('6a'),s('6a',1.0))))
    if t>=s('7a',0.3): e=0.4*(1-math.sin(PI*seg01(t,s('7a',0.4),s('7a',1.4)))**0.5)+0.0 if t<s('7a',1.5) else 0.4
    if t>=s('8a',0.8): e=lerp(0.4,0.0,sm(seg01(t,s('8a',0.8),s('8a',1.6))))
    if t>=s('8a',4.0): e=lerp(0.0,1.0,sm(seg01(t,s('8a',4.0),s('8a',4.5))))
    return e,(s('8a',4.5)<=t<s('9a',0.5))
def ref_pose(t):
    p=dict(IDLE)
    for k in _K: p[k]=float(np.interp(t,_TS,_SIM[k]))
    p['eyes'],p['happy']=ref_eyes(t); p['smile']=t>=s('8a',4.3)
    return p
def reflection(d,pose,cam,fov):
    """2D sprite of the robot (same proportions, front view, pale-blue) drawn inside the mirror rectangle at the low internal resolution"""
    vi=R.view(cam,fov); p=pose; FY=MY0+0.07
    def P(x,y): pr=R.project((MX+x,FY+y+p['hop'],ZM),vi); return (pr[0],pr[1])
    def rect(x0,x1,y0,y1,col,rot=None):
        pts=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
        if rot: pts=[rot(q) for q in pts]
        d.polygon([P(*q) for q in pts],fill=col)
    def line(a,b,w,col):
        a=np.array(a);b=np.array(b); n=b-a; n=n/(np.linalg.norm(n)+1e-9); o=np.array([-n[1],n[0]])*w/2
        d.polygon([P(*(a+o)),P(*(b+o)),P(*(b-o)),P(*(a-o))],fill=col)
    ca,sa=math.cos(p['roll']),math.sin(p['roll'])
    def rot(q): x,y=q[0],q[1]-NECK; return (x*ca-y*sa,x*sa+y*ca+NECK)
    for sx in (-1,1): rect(sx*0.115-0.065,sx*0.115+0.065,0.0,0.28,SP_D); rect(sx*0.115-0.065,sx*0.115+0.065,0.0,0.04,SP_BODY)
    for sx,a,bd in ((1,p['aW'],p['bW']),(-1,p['aO'],p['bO'])):                              # arm index +1 (nearer the camera) is on the screen-left of the sprite
        sh=np.array([-sx*0.26,0.60]); dr=lambda an: np.array([-sx*math.sin(an),-math.cos(an)])
        el=sh+dr(a)*0.20; ha=el+dr(a+bd*sx)*0.18; line(sh,el,0.08,SP_D); line(el,ha,0.075,SP_BODY); rect(ha[0]-0.045,ha[0]+0.045,ha[1]-0.045,ha[1]+0.045,SP_L)
    rect(-0.22,0.22,0.28,0.68,SP_BODY); rect(-0.16,0.16,0.68,0.70,SP_D); rect(-0.055,0.055,0.44,0.55,BLUE)
    rect(-0.16,0.16,0.70,1.02,SP_L,rot)
    eh=0.07*max(p['eyes'],0.14)
    for sx in (-1,1):
        ex=sx*0.075; ey=0.88
        if p['happy']: rect(ex-0.035,ex+0.035,ey,ey+0.016,BLK,rot); rect(ex-0.035,ex-0.02,ey-0.02,ey,BLK,rot); rect(ex+0.02,ex+0.035,ey-0.02,ey,BLK,rot)
        else: rect(ex-0.034,ex+0.034,ey-eh/2,ey+eh/2,BLK,rot)
        if not p['happy'] and p['eyes']<0.7: rect(ex-0.04,ex+0.04,ey+eh/2,ey+0.05,SP_D,rot)           # heavy eyelid
    rect(-0.06,0.06,0.77,0.79,BLK,rot)
    if p['smile']: rect(-0.075,-0.06,0.79,0.81,BLK,rot); rect(0.06,0.075,0.79,0.81,BLK,rot)

# ======================= render =======================
R=Renderer(W,H,fog=(10,14,34))
def glint(im,a,cam,fov,pts):
    """two banded diagonal glints on the glass (2D). Masked to the mirror rectangle AND to pixels that still show the bare mirror panel, so they never cross the robot"""
    x0,x1=MX-MW/2,MX+MW/2; v2=R.view(cam,fov); m=Image.new('L',(W,H),0); dm=ImageDraw.Draw(m)
    for k in range(2):
        q=[R.project((x0+(0.15+0.28*k)*MW+dx,y,ZM),v2) for dx,y in ((0,MY1),(0.07,MY1),(0.07-0.45,MY0+0.2),(-0.45,MY0+0.2))]
        dm.polygon([(a_[0],a_[1]) for a_ in q],fill=255)
    clip=Image.new('L',(W,H),0); ImageDraw.Draw(clip).polygon([(p_[0],p_[1]) for p_ in pts],fill=255)
    bare=(np.abs(a-np.array(MIRBG,np.float32)*np.array([0.88,0.94,1.1],np.float32)).max(axis=2)<10).astype(np.uint8)*255
    mask=np.minimum(np.minimum(np.asarray(m),np.asarray(clip)),bare); im.paste(Image.new('RGB',(W,H),(22,32,60)),(0,0),Image.fromarray(mask))

def render(t):
    cp,tg,fov=cam_shot(t); cpa=np.array(cp); cam=Camera.look(cp,tg); st=real_pose(t)
    rq,rd=robot(st); rd[:]=[x for x in rd if np.linalg.norm(x['c']-cpa)<np.linalg.norm(x['hc']-cpa)]
    lights=[((LAMP_POS[0],LAMP_POS[1]-0.1,LAMP_POS[2]-0.2),(255,236,190),0.8)]
    layers=[ROOM_F,ROOM_W,ROOM_FR,ROOM_L,rq,rd]
    img,vi,zb=zrender(R,cam,layers,lights,fov=fov,fog_start=6,fog_end=18,ambient=0.40,bias=[1,1,1,1,1,1.004],return_z=True)
    a=np.asarray(img).astype(np.float32)*np.array([0.88,0.94,1.1],np.float32)
    im=Image.fromarray(np.clip(a,0,255).astype(np.uint8)); d=ImageDraw.Draw(im)
    x0,x1=MX-MW/2,MX+MW/2; vi2=R.view(cam,fov); pts=[R.project((x,y,ZM),vi2) for x,y in ((x0,MY0),(x1,MY0),(x1,MY1),(x0,MY1))]
    glint(im,a,cam,fov,pts)
    sp=Image.new('RGBA',(W,H),(0,0,0,0)); reflection(ImageDraw.Draw(sp),ref_pose(t),cam,fov)         # sprite on its own layer, clipped to the glass
    clip=Image.new('L',(W,H),0); ImageDraw.Draw(clip).polygon([(p_[0],p_[1]) for p_ in pts],fill=255)
    al=np.minimum(np.asarray(sp)[...,3],np.asarray(clip)); sp.putalpha(Image.fromarray(al)); im.paste(sp,(0,0),sp)
    return post.ps1(im),cam,fov

# ======================= subtitles and UI (2D overlays only) =======================
ACC=(255,214,70); WHT=(244,240,228)
HIL={'MIRRORS','SECOND','LATE','FROZE','BREAK','REQUESTED','COPYING','COPY','YOUR','TURN'}
SUB_SC=2; SUB_ROW=13
def sub_chunks():
    """each sentence wrapped to rows of <= 13 characters (fits 180 px at 2x), shown two rows at a time, timed by character share over the measured voice length"""
    out=[]; END=('.','?','!'); WEAK={'a','the','to','his','he','so','of','on'}
    for key in ORDER:
        t0=ST[key]; dur=DURS[key]; words=TEXT[key].split(' '); n=sum(len(w)+1 for w in words); rows=[]; r=[]
        for w in words:
            if r and (sum(len(x)+1 for x in r)+len(w)>SUB_ROW or r[-1].endswith(END)): rows.append(r); r=[]
            r.append(w)
        rows.append(r)
        for i in range(len(rows)-1):
            if len(rows[i])>1 and rows[i][-1].lower() in WEAK and sum(len(x)+1 for x in rows[i+1])+len(rows[i][-1])<=SUB_ROW: rows[i+1].insert(0,rows[i].pop())
        chunks=[]; c=[]
        for rw in rows:
            c.append(rw)
            if len(c)==2 or rw[-1].endswith(END): chunks.append(c); c=[]
        if c: chunks.append(c)
        pos=0
        for ch in chunks:
            L=sum(len(x)+1 for rw in ch for x in rw); a=t0+dur*pos/n; b=t0+dur*(pos+L)/n; pos+=L; out.append([a,b,ch,key])
    for i in range(len(out)-1): out[i][1]=out[i+1][0] if out[i+1][0]-out[i][1]<0.5 else out[i][1]+0.12     # a chunk stays until the next one starts
    return out
SUBS=sub_chunks()
def subtitles(d,t):
    for a,b,rows,key in SUBS:
        if a<=t<b:
            sc=SUB_SC; lh=7*sc+3; lines=[' '.join(r) for r in rows]; w=max(font.width(l,sc) for l in lines)+4*sc; h=len(lines)*lh+2*sc
            x0=(W-w)//2; y0=H-6-h; d.rectangle([x0,y0,x0+w,y0+h],fill=(0,0,0))
            for i,r in enumerate(rows):
                x=x0+2*sc
                for wd in r: font.text(d,wd,x,y0+2*sc+i*lh,ACC if wd.upper().strip('.,!?:') in HIL else WHT,sc,None); x+=font.width(wd,sc)+6*sc
def ui_box(d,lines,y,col,sc=2,fill=(8,8,20)):
    w=max(font.width(l,sc) for l in lines)+12; x0=(W-w)//2; h=len(lines)*(7*sc+3)+8
    d.rectangle([x0,y,x0+w,y+h],fill=fill,outline=col); d.rectangle([x0+2,y+2,x0+w-2,y+h-2],outline=(60,60,110))
    for i,l in enumerate(lines): font.ctext(d,l,y+5+i*(7*sc+3),col,W,sc)
RED=(255,90,90); CYAN=(120,230,255)
UI_T=dict(lag=(s('2b',0.3),s('2b',2.7)),brk=(s('5a',1.9),s('5c',0.0)),off=(s('6b',0.5),s('6b',3.6)),emp=(s('7a',1.4),CUTS[7]),turn=(s('9b',-0.05),s('9c',0.9)),shift=(s('9c',0.9),DUR))
def ui(d,t):
    a,b=UI_T['lag']
    if a<=t<b and int((t-a)*5)%2==0: ui_box(d,['LAG DETECTED'],10,ACC)
    a,b=UI_T['brk']
    if a<=t<b: ui_box(d,['BREAK','REQUESTED'],172,RED if int((t-a)*8)%2==0 else (255,200,200),3)
    a,b=UI_T['off']
    if a<=t<b: ui_box(d,['REFLECTION','OFFLINE'],12,RED if int((t-a)*4)%2==0 else ACC)
    a,b=UI_T['emp']
    if a<=t<b: ui_box(d,['MIRROR','EMPLOYEE:','EXHAUSTED'],4,CYAN if t-a<0.25 or int((t-a)*3)%2==0 else (200,240,255))
    a,b=UI_T['turn']
    if a<=t<b: ui_box(d,['YOUR TURN'],14,ACC if int((t-a)*8)%2==0 else (255,244,170),3)
    a,b=UI_T['shift']
    if a<=t<b:
        u=min(1.0,(t-a)/0.25); y=int(lerp(-60,14,sm(u))); ui_box(d,['SHIFT','STARTED'],y,(130,255,150) if int((t-a)*8)%2==0 else (220,255,225),3)
def frame(t):
    img,cam,fov=render(t); d=ImageDraw.Draw(img); ui(d,t); subtitles(d,t); return img

# ======================= QA manifest =======================
def _extra(t):
    out=[]
    if t<0.05:
        r=real_pose(0.0); f=ref_pose(0.0)
        if not (r['aW']>1.5 and f['aW']<0.6): out.append(('reflection','first frame must show the robot waving and the reflection arm still down'))
    if t>=s('9c',0.0)-0.05 and t<DUR:                                       # the reflection must move first, the robot copies
        if t>=s('9a',1.4) and ref_pose(t)['aW']<2.0: out.append(('reflection','reflection arms not up in the final shot'))
    if abs(t-s('5a',1.9))<0.02 and ref_pose(t)['aW']<2.0: out.append(('reflection','reflection is not frozen with arms up when BREAK REQUESTED appears'))
    return out
QA=dict(fps=FPS,dur=DUR,W=W,frame=lambda t: frame(t),chars={'robot':(robot_state,robot_model,'_none',1.0)},
    geom=lambda t,name,st,V: [('floor',f'{name} under the floor')] if V[:,1].min()<-0.04 else ([('wall',f'{name} inside the back wall')] if V[:,2].max()>WALL_Z-0.05 else []),
    extra=_extra,camera=lambda t: cam_shot(t)[0],min_cam_dist=0.4,camera_ok=lambda p: -4.0<p[2]<0.0 and 0.1<p[1]<2.0,allow_jump=[],weapon_events=[],
    scenes=[dict(id=f'shot{i}',t0=CUTS[i-1],t1=CUTS[i],action=a) for i,a in enumerate((
        'robot already waving, reflection arm down (cam A)','robot waves again, reflection waves a second late, LAG DETECTED (cam A)','both arms up/down, reflection falls further behind (cam A)',
        'two-pose dance, reflection freezes halfway with arms up (cam A)','BREAK REQUESTED over the mirror, tired eyes, head tilt (cam B)','robot waves twice, reflection offline (cam A)',
        'close look, slow blink, MIRROR EMPLOYEE: EXHAUSTED (cam B)','robot stands completely still, reflection rests, happy eyes, nod (cam A)','reflection moves first, YOUR TURN, robot copies, SHIFT STARTED (cam A)'),1)],
    texts=lambda: [('sub',' '.join(r),SUB_SC) for _,_,rows,_ in SUBS for r in rows]+[('ui',l,sc) for l,sc in (('LAG DETECTED',2),('BREAK',3),('REQUESTED',3),('REFLECTION',2),('OFFLINE',2),('MIRROR',2),('EMPLOYEE:',2),('EXHAUSTED',2),('YOUR TURN',3),('SHIFT',3),('STARTED',3))])

TEST=os.environ.get('TEST')
if TEST and __name__=='__main__':
    ims=[frame(float(x)) for x in TEST.split(',')]; shp=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): shp.paste(im,(i*182,0))
    shp.resize((shp.width*2,640),Image.NEAREST).save('test.png'); sys.exit()

# ======================= AUDIO: synthesized mystery-comedy loop, room ambience, foley, retro UI sounds, narration =======================
def build_audio(path):
    """mix: one synthesized 120 bpm loop (curious/playful 0-19 s, comic tension 19-40, warm 40-54, playful payoff 54-60) kept quiet under the voice, room bed, soft robot/arm foley,
    delayed-wave beeps, dance blips, record-stop, UI alerts, chimes, then the narrator (one sentence per file, cued from the measured lengths). Everything is original synthesis."""
    import soundfile as _sf
    s_=Sound(DUR,loop=False,seed=71); sr=s_.sr; n=s_.n; M=np.zeros(n); AMB=np.zeros(n)
    def hz(m): return 440*2**((m-69)/12)
    def note(buf,t0,m,d,v,wave='tri',dec=3.0,att=0.005):
        tt=s_.T(d); ph=2*np.pi*hz(m)*tt
        x={'sin':np.sin(ph),'tri':(2/np.pi)*np.arcsin(np.sin(ph)),'bell':np.sin(ph)+0.35*np.sin(2*ph)+0.12*np.sin(3.01*ph),'sq':np.sign(np.sin(ph))*0.5}[wave]
        i=int(t0*sr); j=min(n,i+len(tt)); buf[i:j]+=(x*np.minimum(1,tt/att)*np.exp(-tt*dec)*v)[:j-i]
    def tone(t0,f0,f1,d,v,harm=(1.0,0.4),dec=0.0):
        tt=s_.T(d); fr=f0+(f1-f0)*(tt/d); ph=np.cumsum(fr)/sr; x=sum(h*np.sin(2*np.pi*ph*(k+1)) for k,h in enumerate(harm))
        s_.place(x*np.minimum(1,tt/0.004)*np.sin(np.pi*np.clip(tt/d,0,1))**0.5*np.exp(-tt*dec),t0,v)
    def nb(t0,d,lo,hi,v,seed,shape=1): s_.place(s_.filt_short(s_.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s_.T(d)/d)**shape,t0,v)
    def thud(t0,f=70,v=0.1,d=0.2): tt=s_.T(d); s_.place(np.sin(2*np.pi*f*tt*(1-0.3*tt/d))*np.exp(-tt*16),t0,v)
    def servo(t0,d=0.35,v=0.035,f=520,up=True): tone(t0,f,f*1.5 if up else f*0.7,d,v,harm=(1.0,0.5,0.25)); nb(t0,d,1500,5000,v*0.5,int(t0*97))       # small mechanical arm sound
    def wave_whirr(a,b,v=0.02):
        t0=a
        while t0<b: servo(t0,0.16,v,640+60*((int(t0*7))%3)); t0+=0.38
    def blip(t0,m,v=0.05,d=0.12): note(M2,t0,m,d,v,'sq',14.0)
    def delayed(t0,v=0.03): tone(t0,900,1100,0.09,v,harm=(1.0,0.3))                                                                    # reflection's late echo of a robot sound
    M2=np.zeros(n)                                                                                                                       # UI / blip layer (not ducked by voice)
    # ---- bed: low room air + soft drips ----
    AMB+=s_.filt(s_.rng.normal(0,1,n),lo=40,hi=260)*0.06+s_.filt(s_.rng.normal(0,1,n),lo=1800,hi=5000)*0.003
    tt=s_.t; AMB+=(np.sin(2*np.pi*100*tt)+0.3*np.sin(2*np.pi*200*tt))*0.006*(1+0.2*np.sin(2*np.pi*0.3*tt))        # lamp hum
    for t0 in (3.1,9.4,16.8,23.3,29.7,37.2,45.1,51.6): tt=s_.T(0.16); s_.place(np.sin(2*np.pi*(1500-800*tt/0.16)*tt)*np.exp(-tt*30),t0,0.015)
    # ---- music (120 bpm: 0.5 s beat) ----
    B=0.5; bass=[45,48,52,48,45,47,52,47,41,45,48,45,40,44,47,44]; mel=[76,0,72,74,76,0,79,77,76,0,72,71,69,0,0,0]
    for k in range(int(19/(B/2))):                                                          # curious + playful
        t0=0.05+k*B/2
        if k%2==0: note(M,t0,bass[(k//2)%16],0.45,0.06,'tri',5.0)
        if mel[k%16]: note(M,t0,mel[k%16],0.35,0.026,'bell',6.0)
    for k in range(int(21/B)): note(M,19+k*B,[38,38,41,40][(k//2)%4],0.5,0.06,'tri',3.5)       # slight comic tension: darker pulse
    for k in range(int(21/(B/2))):
        if k%3==0: note(M,19+k*B/2,[62,63,62,61][(k//3)%4],0.15,0.012,'sq',12.0)
    pad=np.zeros(n); 
    for m_ in (50,53): tone_i=int(19*sr); tt=s_.T(21); pad[tone_i:tone_i+len(tt)]+=(np.sin(2*np.pi*hz(m_)*tt)*np.minimum(1,tt/1.0)*0.02)[:n-tone_i]
    M+=pad*(1+0.35*np.sin(2*np.pi*5*s_.t))
    for k in range(int(14/(B/2))):                                                          # gentle warm realization: music-box + soft chords
        t0=40+k*B/2
        if k%2==0: note(M,t0,[60,64,67,72,71,67,64,67][(k//2)%8],1.0,0.032,'bell',2.6)
    for c,(a_,b_) in enumerate(((40,47),(47,54))):
        for m_ in ((48,55,60,64),(53,57,60,65))[c]: note(M,a_,m_,b_-a_+0.4,0.02,'sin',0.5,0.8)
    for k in range(int(6/(B/2))):                                                           # short playful payoff
        t0=54+k*B/2
        if k%2==0: note(M,t0,[45,52,45,50][(k//2)%4],0.4,0.06,'tri',4.0)
        note(M,t0,[84,88,91,88,84,79][k%6],0.3,0.03,'bell',6.0)
    # ---- foley / sfx (all cued from the same time variables as the animation) ----
    wave_whirr(0.0,s('1b',1.5)); wave_whirr(s('2a',0.6),s('2b',0.5)); wave_whirr(s('6a',0.15),s('6a',0.95)); wave_whirr(s('6a',1.4),s('6b',0.3))
    for a_,b_ in ((1.0,s('1b',2.5)),(s('2a',1.6),s('2b',1.5))):                              # delayed beeps of the reflection's late wave
        t0=a_
        while t0<b_: delayed(t0); t0+=0.38
    for t0 in (s('3a',0.1),s('4a',0.2)): servo(t0,0.4,0.04,520,True)
    for t0 in (s('3b',0.6),s('4b',0.95)): servo(t0,0.4,0.04,700,False)
    for t0 in (s('3a',0.1)+1.7,s('4a',0.2)+2.0): servo(t0,0.9,0.02,420,True)                  # reflection struggling to keep up (slow, quiet)
    for k,t0 in enumerate(np.arange(s('4a',1.0),s('4b',1.25),0.294)): blip(t0,[72,76,79,76,84][k%5],0.045); thud(t0+0.02,90,0.03,0.08)      # comedic dance blips
    tt=s_.T(0.7); fr=900*np.exp(-tt*4.5); s_.place(np.sin(np.cumsum(fr)/sr*2*np.pi)*np.exp(-tt*4)+0.4*s_.filt_short(s_.noise(0.7,5),lo=300,hi=3000)*np.exp(-tt*8),T_FREEZE,0.16)  # record-stop
    for k in range(2): tone(s('5a',1.9)+k*0.28,1180,1180,0.18,0.07,harm=(1.0,0.5,0.3))     # BREAK REQUESTED warning beep
    for k,m_ in enumerate((70,65,58)): blip(s('6b',0.5)+k*0.3,m_,0.05,0.25)                  # low battery-style beeps
    for k,m_ in enumerate((72,76,79,84)): note(M2,s('7a',1.4)+k*0.1,m_,0.9,0.045,'bell',3.5)  # realization chime
    for k,m_ in enumerate((79,84,88)): note(M2,s('8a',4.4)+k*0.12,m_,1.2,0.045,'bell',2.8)      # gentle positive chime
    note(M2,s('9b',-0.05),84,0.3,0.05,'sq',8.0); note(M2,s('9b',-0.05)+0.12,91,0.4,0.05,'sq',6.0)  # YOUR TURN ping
    for k,m_ in enumerate((72,76,79,84,88)): note(M2,s('9c',0.9)+k*0.07,m_,0.9,0.05,'bell',3.0); note(M2,s('9c',0.9)+k*0.07,m_-12,0.6,0.03,'sq',6.0)   # SHIFT STARTED
    for t0 in (s('9a',0.7),s('9c',0.55)): servo(t0,0.4,0.03,600,True)                           # the reflection moves first
    for t0 in (s('9c',0.2),s('9c',0.95)): servo(t0,0.4,0.03,600,True)                           # the robot copies
    # ---- voice (one calm narrator) ----
    NB=np.zeros(n); duck=np.ones(n)
    for key in ORDER:
        a,_=_sf.read(os.path.join(TTS_DIR,'mc',key+'.wav')); a=a if a.ndim==1 else a.mean(1)
        act=a[np.abs(a)>0.02]; a=a*0.2/(np.sqrt((act**2).mean())+1e-9)
        i=int(ST[key]*sr); j=min(n,i+len(a)); NB[i:j]+=a[:j-i]; duck[max(0,i-int(0.05*sr)):min(n,j+int(0.1*sr))]=0.55
    duck=np.convolve(duck,np.ones(2400)/2400,'same')
    s_.L+=AMB+M*duck*3.2+M2; s_.R+=np.roll(AMB,900)+np.roll(M,300)*duck*3.2+M2
    s_.reverb(0.1,length=0.9,decay=4.0)
    pk=max(np.abs(s_.L).max(),np.abs(s_.R).max()); gv=pk/np.abs(NB).max()*0.95
    s_.L=s_.L*(0.8+0.2*duck)+NB*gv; s_.R=s_.R*(0.8+0.2*duck)+NB*gv
    st=np.stack([s_.L,s_.R],1); k=int(0.05*sr); st[-k:]*=np.linspace(1,0,k)[:,None]
    st=st/np.max(np.abs(st))*0.9; _sf.write(path,st,sr,subtype='PCM_16'); return path
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'mirror_copy.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'mc_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.96,vignette=0.25,grain=1.5,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(post.upscale(frame(f/FPS),S),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
