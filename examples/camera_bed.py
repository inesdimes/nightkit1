"""THE CAMERA UNDER MY BED - 30 s PS1 psychological horror, 9:16. Fully procedural (nightkit).
A man stands awake in his bedroom while a live feed on his CRT shows the SAME man still asleep in the same bed, filmed from under it.
LOCKED ASSETS: man() (one character reference, used for the awake man AND the sleeping duplicate, face = texture swaps), room() (one bedroom, nothing ever moves),
feed_img() (the CRT picture: a separate render of the same room from an impossible disembodied viewpoint, composited onto the screen quad at full resolution).
Character cadence 15 fps (poses are evaluated at floor(t*15)/15), cameras 24 fps. Hard cuts only, no music, no fades; the last second is pure black.
Voice: python tools/tts/cb.py -> $TTS_DIR/cb/N1..N5.wav (dry narrator) + W1.wav (whisper).
Run: TEST=0.5,5,12 python examples/camera_bed.py -> test.png | PART=a:b | PART=audio | QA: python tools/qa/scene_qa.py examples/camera_bed.py"""
import os, sys, math, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, box, quad, transform, tiled_plane, refresh
from nightkit import post, font
from nightkit.zraster import zrender
from nightkit.audio import Sound
_T=os.environ.pop('TEST',None)                      # face_track (imported by cat_dodge) has its own TEST hook at import time
import cat_dodge as CD
if _T is not None: os.environ['TEST']=_T
FT=CD.FT
sm,seg01,seg,tag,Rx,Ry,Rz=FT.sm,FT.seg01,FT.seg,FT.tag,FT.Rx,FT.Ry,FT.Rz
PI=math.pi
def lerp(a,b,u): return a+(b-a)*u
TTS_DIR=CD.TTS_DIR; OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6; DUR=30.0; N=int(round(DUR*FPS)); T_BLACK=29.0
SCR=json.load(open(os.path.join(TTS_DIR,'cb','script.json')))

# ======================= palette (midnight blues, cold shadows, the CRT green) =======================
WALL=(40,48,74); WALL_D=(30,36,58); CEIL=(30,34,54); BOARD=[(62,54,56),(54,48,52),(70,60,60)]; WOOD=(56,40,34); WOOD_D=(40,30,28)
SKIN=(222,202,190); SKIN_D=(196,172,166); HAIR=(44,30,26); SHIRT=(120,122,130); PANTS=(34,42,82)
BLANKET=(28,40,92); SHEET=(74,80,104); PILLOW=(196,200,212); CRT_G=(90,92,98); MARK=(255,0,255)
BLK=(14,12,18)

# ======================= LOCKED ENVIRONMENT: one small bedroom, nothing ever moves =======================
SCREEN=dict(x0=-1.43,x1=-0.77,y0=0.86,y1=1.355,z=2.499)             # the CRT screen (4:3), faces -z
BED=dict(x0=-0.1,x1=1.65,z0=2.1,z1=3.0)
def strip_bottom(Q): return [q for q in Q if q['n'][1]>-0.9]
def strip_open(Q): return [q for q in Q if abs(q['n'][1])<0.9]            # open top and bottom: the feed camera looks up through the mattress (boxes are two-sided)
def room(feed=False):
    F=tiled_plane(-1.7,1.7,0,3.0,0,0.2,lambda i,j:BOARD[((i*7+j*3)%5)%3])
    F+=box(-0.1,1.65,0.0,0.004,2.1,3.0,(26,24,32))                                                       # the dark under-bed floor
    Wl=box(-1.75,1.75,0,2.4,3.0,3.05,WALL)+box(-1.75,-1.7,0,2.4,-0.05,3.05,WALL_D)+box(1.7,1.75,0,2.4,-0.05,3.05,WALL_D)+box(-1.75,1.75,0,2.4,-0.1,-0.05,WALL_D)
    Wl+=box(-1.75,1.75,2.4,2.45,-0.1,3.05,CEIL)+box(-1.7,1.7,0,0.1,2.95,3.0,WOOD_D)
    Wl+=box(0.45,1.25,1.0,1.95,2.985,3.0,WOOD_D)+box(0.5,1.2,1.05,1.9,2.98,2.99,(52,76,130),emit=True)+box(0.83,0.87,1.05,1.9,2.97,2.98,WOOD_D)+box(0.5,1.2,1.45,1.5,2.97,2.98,WOOD_D)   # window, cold moon blue
    Wl+=box(-1.745,-1.7,0,2.05,0.5,1.4,WOOD_D)+[quad([(-1.745,0.0,1.4),(-1.745,2.0,1.4),(-1.745,2.0,0.5),(-1.745,0.0,0.5)],(2,2,5),emit=True)]   # doorway into pitch darkness
    Wl+=[quad([(-1.69,0.0,1.4),(-1.69,2.0,1.4),(-1.24,2.0,0.86),(-1.24,0.0,0.86)],(50,38,36))]       # the door, slightly ajar
    P=box(-1.65,-0.55,0,0.8,2.4,3.0,WOOD)+box(-1.6,-0.6,0.05,0.75,2.395,2.4,WOOD_D)+box(-1.6,-0.6,0.4,0.42,2.39,2.395,BLK)                      # dresser
    P+=box(-1.55,-0.65,0.8,1.42,2.5,3.0,CRT_G)+box(-1.5,-0.7,1.42,1.46,2.55,2.95,CRT_G)                                                              # CRT housing
    for x0,x1,y0,y1 in ((-1.55,-1.43,0.86,1.42),(-0.77,-0.65,0.86,1.42),(-1.43,-0.77,1.355,1.42),(-1.43,-0.77,0.8,0.86)): P+=box(x0,x1,y0,y1,2.49,2.5,(64,66,72))   # bezel
    P+=box(-0.76,-0.7,0.82,0.85,2.485,2.49,BLK)+box(-0.88,-0.82,0.82,0.85,2.485,2.49,BLK)
    B=[]
    if not feed: B+=box(-0.1,1.65,0.24,0.3,2.1,2.14,WOOD)                                                                                 # low side rail
    if not feed: B+=box(BED['x0'],BED['x1'],0.27,0.3,BED['z0'],BED['z1'],WOOD_D)                                                           # slats (the feed camera looks up through them)
    for x in (-0.1,1.58):
        for z in (2.1,2.93): B+=box(x,x+0.07,0,0.3,z,z+0.07,WOOD)                                                                           # legs
    B+=box(1.6,1.65,0.15,1.05,2.1,3.0,WOOD)+box(-0.1,-0.05,0.3,0.88,2.1,3.0,WOOD)                                                           # TALL headboard + footboard
    mat=box(-0.05,1.6,0.3,0.46,2.14,2.96,SHEET)+box(-0.05,1.2,0.46,0.49,2.14,2.96,BLANKET)+box(-0.05,1.2,0.34,0.49,2.1,2.14,BLANKET)
    pil=box(1.2,1.58,0.46,0.52,2.3,2.8,PILLOW)
    B+=[] if feed else mat+pil                                                                                              # the feed sees the sleeper through the (invisible) mattress
    B+=box(1.3,1.68,0,0.55,1.5,2.05,WOOD)+box(1.4,1.58,0.55,0.63,1.7,1.85,(24,24,30))                                                       # bedside table + clock
    for x in (1.43,1.47,1.52,1.56): B+=box(x,x+0.025,0.58,0.61,1.699,1.7,(255,36,28),emit=True)                                             # unreadable red digits
    return F,Wl,P,B
ROOM=room(); ROOM_FEED=room(True)
SCREEN_Q=quad([(SCREEN['x0'],SCREEN['y1'],SCREEN['z']),(SCREEN['x1'],SCREEN['y1'],SCREEN['z']),(SCREEN['x1'],SCREEN['y0'],SCREEN['z']),(SCREEN['x0'],SCREEN['y0'],SCREEN['z'])],MARK,emit=True)
SCREEN_C=np.array([-1.1,1.108,2.499])
LIGHTS=[((-1.1,1.1,2.2),(105,255,135),1.15),((0.85,1.5,2.7),(90,120,210),0.45),((0.0,2.3,1.2),(70,100,190),0.5)]     # CRT green, moon blue, cold fill

# ======================= LOCKED CHARACTER: one reference, used verbatim for both selves =======================
def lerpP(A,B,u): return {k:(np.array(A[k])+(np.array(B[k])-np.array(A[k]))*u if k in ('kn','an','el','ha') else (A[k] if u<0.5 else B[k])) for k in A}
STAND=dict(kn=[(-0.09,-0.46,0.03),(0.09,-0.46,0.03)],an=[(-0.09,-0.89,0.0),(0.09,-0.89,0.0)],el=[(-0.23,0.22,-0.02),(0.23,0.22,-0.02)],ha=[(-0.23,-0.04,0.03),(0.23,-0.04,0.03)],foot=1.0)
KNEEL=dict(kn=[(-0.1,-0.44,0.14),(0.1,-0.44,0.14)],an=[(-0.1,-0.44,-0.36),(0.1,-0.44,-0.36)],el=[(-0.23,0.2,0.05),(0.23,0.2,0.05)],ha=[(-0.23,-0.04,0.1),(0.23,-0.04,0.1)],foot=-1.0)
SIDE=dict(kn=[(-0.09,-0.36,0.2),(0.09,-0.4,0.22)],an=[(-0.09,-0.74,0.0),(0.09,-0.76,0.02)],el=[(-0.17,0.2,0.04),(0.17,0.2,0.05)],ha=[(-0.12,0.18,-0.02),(0.12,0.28,0.0)],foot=1.0)
def head_rot(f_local):
    z=np.array(f_local,float); z/=np.linalg.norm(z); x=np.cross([0,1.0,0],z); x/=np.linalg.norm(x)+1e-9; y=np.cross(z,x); return np.stack([x,y,z],1)
def man(O,Rl,Rt,P,Rh,face='tired',mouth=0,jit=0.0,fr=0):
    """gaunt man, ~500 polygons. O = hip (world), Rl = legs frame, Rt = torso frame, P = joints, Rh = head rotation (torso frame). face = texture swap."""
    O=np.array(O,float); Wl=lambda p:tuple(O+Rl@np.array(p,float)); Wt=lambda p:tuple(O+Rt@np.array(p,float)); Q=[]; D=[]
    Q+=box(-0.16,0.16,-0.1,0.09,-0.1,0.1,PANTS,xf=Wl)
    for s,sx in enumerate((-1,1)):
        hip=(sx*0.09,-0.05,0.0); kn=np.array(P['kn'][s]); an=np.array(P['an'][s]); fz=P['foot']
        Q+=seg(Wl(hip),Wl(kn),0.12,PANTS,0.12)+seg(Wl(kn),Wl(an),0.1,PANTS,0.1)
        Q+=box(an[0]-0.045,an[0]+0.045,an[1]-0.03,an[1]+0.035,(an[2] if fz>0 else an[2]-0.2),(an[2]+0.2 if fz>0 else an[2]),SKIN,xf=Wl)
        sh=np.array((sx*0.19,0.47,0.0)); el=np.array(P['el'][s]); ha=np.array(P['ha'][s]); mid=sh+(el-sh)*0.4
        Q+=seg(Wt(sh),Wt(mid),0.1,SHIRT,0.1)+seg(Wt(mid),Wt(el),0.085,SKIN,0.085)+seg(Wt(el),Wt(ha),0.08,SKIN,0.08)+box(ha[0]-0.04,ha[0]+0.04,ha[1]-0.04,ha[1]+0.04,ha[2]-0.04,ha[2]+0.04,SKIN,xf=Wt)
    Q+=box(-0.18,0.18,0.0,0.52,-0.1,0.1,SHIRT,xf=Wt)+box(-0.05,0.05,0.5,0.6,-0.045,0.045,SKIN,xf=Wt)
    HC=np.array((0.0,0.58,0.0))
    def Hd(p): return Wt(HC+Rh@np.array(p,float))
    Q+=box(-0.095,0.095,0.0,0.25,-0.105,0.105,SKIN,xf=Hd)+box(-0.02,0.02,0.07,0.13,0.105,0.135,SKIN_D,xf=Hd)                            # skull + nose
    Q+=box(-0.1,0.1,0.22,0.285,-0.11,0.11,HAIR,xf=Hd)+box(-0.105,0.105,0.1,0.24,-0.115,-0.06,HAIR,xf=Hd)+box(-0.1,0.1,0.2,0.25,0.085,0.115,HAIR,xf=Hd)   # messy hair
    for x,h,z in ((-0.06,0.33,0.0),(0.03,0.34,-0.03),(0.08,0.32,0.04),(-0.02,0.325,0.06)): Q+=box(x-0.02,x+0.02,0.28,h,z-0.03,z+0.03,HAIR,xf=Hd)
    Q+=box(0.095,0.105,0.1,0.16,-0.02,0.03,SKIN_D,xf=Hd)+box(-0.105,-0.095,0.1,0.16,-0.02,0.03,SKIN_D,xf=Hd)
    z0=0.1055; sc=(215,208,200)
    D+=box(-0.075,-0.05,0.07,0.1,z0,z0+0.001,SKIN_D,xf=Hd)+box(0.05,0.075,0.07,0.1,z0,z0+0.001,SKIN_D,xf=Hd)                                 # gaunt cheeks
    for sx in (-1,1):
        x=sx*0.045; D+=box(x-0.027,x+0.027,0.108,0.12,z0,z0+0.001,(104,86,106),xf=Hd)                                                         # dark under-eye circles
        if face=='closed': D+=box(x-0.026,x+0.026,0.135,0.141,z0+0.0005,z0+0.0015,(38,28,32),xf=Hd)
        elif face=='tired':
            D+=box(x-0.024,x+0.024,0.124,0.146,z0+0.0005,z0+0.0015,sc,xf=Hd)+box(x-0.008,x+0.008,0.126,0.14,z0+0.001,z0+0.002,BLK,xf=Hd)+box(x-0.026,x+0.026,0.138,0.15,z0+0.002,z0+0.003,SKIN_D,xf=Hd)
            D+=box(x-sx*0.004-0.026,x-sx*0.004+0.026,0.162,0.17,z0,z0+0.001,HAIR,xf=Hd)
        elif face=='wide':
            D+=box(x-0.026,x+0.026,0.112,0.162,z0+0.0005,z0+0.0015,(238,234,228),xf=Hd)+box(x-0.007,x+0.007,0.128,0.146,z0+0.001,z0+0.002,BLK,xf=Hd)
            D+=box(x-0.028,x+0.028,0.184,0.192,z0,z0+0.001,HAIR,xf=Hd)
        else:                                                                                                                                  # 'stare': the duplicate awake
            D+=box(x-0.025,x+0.025,0.116,0.156,z0+0.0005,z0+0.0015,(240,238,232),xf=Hd)+box(x-0.006,x+0.006,0.129,0.143,z0+0.001,z0+0.002,BLK,xf=Hd)
            D+=box(x-0.026,x+0.026,0.17,0.177,z0,z0+0.001,HAIR,xf=Hd)
    if face=='wide' and not mouth is None and mouth!=-1: D+=box(-0.022,0.022,0.035,0.07,z0+0.0005,z0+0.0015,(48,22,28),xf=Hd)
    elif face=='wide': D+=box(-0.03,0.03,0.05,0.056,z0+0.0005,z0+0.0015,(118,82,84),xf=Hd)
    else: D+=box(-0.03,0.03,0.05,0.056,z0+0.0005,z0+0.0015,(118,82,84),xf=Hd)+(box(-0.016,0.016,0.04,0.058,z0+0.001,z0+0.002,(58,28,32),xf=Hd) if mouth else [])
    tag(D,Hd((0,0.12,0)))
    if jit>0:                                                                                                                                  # PS1 vertex jitter: vertices snap on a coarse grid, per frame
        for q in Q+D:
            p=np.array(q['p']); key=np.round(p*400).astype(np.int64); h=((key[:,0]*73856093)^(key[:,1]*19349663)^(key[:,2]*83492791)^(fr*2654435761))&0xffff
            q['p']=[tuple(pp+(np.array([(hh&31)/31.0-0.5,((hh>>5)&31)/31.0-0.5,((hh>>10)&31)/31.0-0.5]))*jit) for pp,hh in zip(p,h)]; refresh(q)
    return Q,D

# ======================= the awake man: timeline (15 fps cadence) =======================
def q15(t): return math.floor(t*15+1e-6)/15.0
BED_X=0.30
def man_state(t):
    """the awake man. returns dict(O,Rl,Rt,P,Rh,face,mouth)"""
    t=q15(t); x=-0.15; yaw=-1.0; lean=0.08; hy=0.0; hp=0.0; Pp=STAND; ox=0.0; height=0.92; face='tired'; mouth=0; kn=0.0; shr=0.0
    breathe=0.004*math.sin(t*2.2)
    if t<4.5: yaw=-1.0; hy=0.0                                                                  # frozen, staring at the CRT
    else:
        a=sm(seg01(t,4.5,5.2)); yaw=lerp(-1.0,1.05,a); hy=lerp(0.0,-0.05,a)                   # turns toward the bed, eyes on the bed
    # two slow, hesitant steps toward the bed
    st1=seg01(t,5.0,5.9); st2=seg01(t,6.5,7.4)
    x=-0.15+0.2*sm(st1)+0.25*sm(st2)
    Pp=dict(STAND); kn_l=list(map(list,STAND['kn'])); an_l=list(map(list,STAND['an']))
    for u,s in ((st1,0),(st2,1)):
        if 0<u<1: an_l[s][2]+=0.22*math.sin(PI*u); an_l[s][1]+=0.07*math.sin(PI*u); kn_l[s][2]+=0.12*math.sin(PI*u)
    Pp=dict(STAND,kn=kn_l,an=an_l)
    z=1.9
    if t>=7.4:                                                                                  # turns to face the bed side, then drops to his knees
        a=sm(seg01(t,7.5,8.4)); yaw=lerp(1.05,0.0,a)
    kd=sm(seg01(t,8.8,9.7)) if t<13.9 else 1-sm(seg01(t,13.95,14.9))                          # kneel down (9.0-9.7), up again (14.0-14.9)
    peer=sm(seg01(t,9.5,10.2))*(1.0 if t<13.9 else (1-sm(seg01(t,13.95,14.5))))
    if t>=14.9:                                                                                 # turns toward the CRT
        a=sm(seg01(t,14.9,15.6)); yaw=lerp(0.0,-PI/2,a); hy=lerp(0.0,0.0,a)
    if t>=15.0: face='wide'
    if 8.0<=t<14.0: hy=lerp(hy,0.0,0.5)
    if t<4.5: hy=0.0
    Pp=lerpP(Pp,KNEEL,kd); height=lerp(0.92,0.5,kd)
    if t>=15.6: yaw=-PI/2
    O=np.array([x,height,z+0.05*kd])
    Rl=Ry(yaw); lean=lerp(0.08,1.0,peer); Rt=Ry(yaw)@Rx(lean)
    hp=lerp(0.0,0.45,peer)
    if kd>0.02:                                                                                 # hands on the floor while peering
        for s,sx in enumerate((-1,1)):
            hw=O+Rl@np.array([sx*0.16,0,0])+Rl@np.array([0,0,0.5*peer])+np.array([0,0.0,0])
            hw[1]=0.04; hl=Rt.T@(hw-O); el=(np.array((sx*0.2,0.47,0))+hl)/2+np.array([sx*0.06,-0.04,0.0])
            Pp=dict(Pp); Pp['ha']=[tuple(hl) if k==s else Pp['ha'][k] for k in range(2)]; Pp['el']=[tuple(el) if k==s else Pp['el'][k] for k in range(2)]
    elif t>=14.9: pass
    shiver=0.0
    Rh=Ry(hy)@Rx(hp+0.06*(1-peer))
    if 28.0<=t<28.6: shr=0.03
    mouth=-1 if t>=22.9 else (1 if (face=='wide' and 15.5<t<17.0 and int(t*15)%3==0) else 0)
    return dict(O=O,Rl=Rl,Rt=Rt,P=Pp,Rh=Rh,face=face,mouth=mouth,breathe=breathe,shr=shr)
def man_model(**st):
    return man(st['O'],st['Rl'],st['Rt'],st['P'],st['Rh'],st['face'],st['mouth'])[0]

# ======================= the sleeping duplicate (inside the CRT feed): same model, same face =======================
SLEEP_O=np.array([0.62,0.65,2.55]); R_SIDE=np.stack([[0,1.0,0],[1.0,0,0],[0,0,-1.0]],1)        # lies on his side along +x, chest toward the bed edge (-z)
CAM_FEED=np.array([1.0,0.22,2.0]); HEAD_C=np.array([1.3,0.65,2.55])
F0=np.array([0.2,0.05,-0.98]); F1=(CAM_FEED-HEAD_C); F1=F1/np.linalg.norm(F1)
def sleeper_state(t):
    t=q15(t)
    face='closed' if t<20.5 else 'stare'; mouth=0
    a=0.0
    if t>=21.5: a=min(1.0,(t-21.5)/1.5); a=math.floor(a*8)/8.0                                 # stiff, mechanical: 8 discrete steps, no flesh-and-blood easing
    f=F0*(1-a)+F1*a; f/=np.linalg.norm(f); fl=R_SIDE.T@f
    if 26.0<=t<27.5: mouth=1 if int((t-26.0)*7)%2==0 else 0                               # barely moves while he whispers
    O=SLEEP_O+np.array([0,0.004*math.sin(t*1.6),0]) if t<20.5 else SLEEP_O
    return dict(O=O,Rl=R_SIDE,Rt=R_SIDE,P=SIDE,Rh=head_rot(fl),face=face,mouth=mouth)
def sleeper_model(**st): return man(st['O'],st['Rl'],st['Rt'],st['P'],st['Rh'],st['face'],st['mouth'])[0]

# ======================= the CRT feed: a separate render, then VCR / curved glass on top =======================
FR=Renderer(224,224,fog=(0,0,0)); FEED_ROLL=78                       # the disembodied camera is rolled, so the sleeper's face reads upright and the room is wrong
FEED_W,FEED_H=320,240
def _barrel():
    yy,xx=np.mgrid[0:FEED_H,0:FEED_W].astype(np.float32); u=(xx-FEED_W/2)/(FEED_W/2); v=(yy-FEED_H/2)/(FEED_H/2); r2=u*u+v*v
    k=1+0.16*r2; sx=(u*k)*(FEED_W/2)+FEED_W/2; sy=(v*k)*(FEED_H/2)+FEED_H/2
    ok=(sx>=0)&(sx<FEED_W-1)&(sy>=0)&(sy<FEED_H-1); return np.clip(sx,0,FEED_W-1).astype(np.int32),np.clip(sy,0,FEED_H-1).astype(np.int32),ok,np.clip(1.0-0.55*r2**1.4,0.25,1.0)
BX,BY,BOK,VIG=_barrel()
def feed_img(t,reflect=None):
    tq=q15(t); sl=sleeper_state(tq); Qs,Ds=man(sl['O'],sl['Rl'],sl['Rt'],sl['P'],sl['Rh'],sl['face'],sl['mouth'],jit=0.0035,fr=int(tq*15))
    mound=strip_bottom(box(-0.1,0.95,0.46,0.72,2.2,2.9,BLANKET))
    cam=Camera.look(tuple(CAM_FEED),tuple(HEAD_C+np.array([0.0,0.0,0.0])))
    layers=list(ROOM_FEED)+[mound,Qs,Ds]
    img,vi=zrender(FR,cam,layers,[((CAM_FEED[0],CAM_FEED[1]+0.05,CAM_FEED[2]),(255,255,255),0.8)],fov=50,fog_start=5,fog_end=14,ambient=0.3,bias=[1.0]*(len(ROOM_FEED)+2)+[1.004])
    img=post.ps1(img).rotate(FEED_ROLL,Image.NEAREST); img=img.crop((32,52,192,172)).resize((FEED_W,FEED_H),Image.NEAREST); a=np.asarray(img).astype(np.float32); lum=a@np.array([0.3,0.59,0.11],np.float32)
    rng=np.random.default_rng(int(tq*15)); lum=lum*1.25+rng.normal(0,8,lum.shape)
    # slow VHS tracking: a gentle row wobble, plus one rolling band
    yy=np.arange(FEED_H); sh=(2.2*np.sin(yy*0.045+t*1.1)).astype(int)+np.where(np.abs(yy-((t*18)%(FEED_H+120)-60))<8,5,0)
    lum=np.stack([np.roll(lum[i],sh[i]) for i in range(FEED_H)]); lum[np.abs(yy-((t*18)%(FEED_H+120)-60))<4]*=1.25
    lum=np.clip(lum,0,255); lum[::2]*=0.78                                                                                                   # scanlines
    g=np.stack([lum*0.42,lum*1.0+6,lum*0.52],-1)
    im=Image.fromarray(np.clip(g,0,255).astype(np.uint8)); d=ImageDraw.Draw(im)
    for ox,oy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(1,-1),(-1,1)): font.text(d,'REC 03:14 AM',14+ox,12+oy,(0,0,0),2,None)
    font.text(d,'REC 03:14 AM',14,12,(236,240,236),2,None)                                                                                  # 1999 camcorder text, steady
    a=np.asarray(im).astype(np.float32)
    if reflect is not None: a=a*(1-0.35*reflect[...,None])+reflect[...,None]*np.array([16,26,30],np.float32)*0.35                          # the faint reflection in the glass
    out=a[BY,BX]*VIG[...,None]; out[~BOK]=(2,3,3)
    return Image.fromarray(np.clip(out,0,255).astype(np.uint8))

# ======================= shots (hard cuts, 24 fps cameras) =======================
def shot(t):
    """returns (cam, tgt, fov, name). Layout lock: CRT upper third, the man/the empty mattress in the middle, the bed's dark gap + scuffed floorboards at the bottom."""
    if t<4.0:                                                                                      # S1: extreme close-up on the feed, snap pull-back (one continuous move)
        near=(np.array([-1.10,1.12,1.88]),np.array([-1.10,0.90,2.5]),56); far=(np.array([-0.45,1.38,0.22]),np.array([-0.45,0.88,2.5]),64)
        u=sm(seg01(t,1.4,1.85))**0.6 if t>=1.4 else 0.0
        c=near[0]+(far[0]-near[0])*u; g=near[1]+(far[1]-near[1])*u; f=near[2]+(far[2]-near[2])*u
        if t<1.4: c=c+np.array([0,0,0.03*t]);
        if t>=1.85: c=c+np.array([0.02*(t-1.85),0,0.03*(t-1.85)])
        return tuple(c),tuple(g),f,'S1'
    if t<9.0: u=seg01(t,4.0,9.0); return (-0.12+0.08*u,1.55,0.3),(0.0+0.1*u,0.68,2.6),66,'S2'        # S2: over the shoulder, the bed in the depth of frame
    if t<10.4: return (-0.85,0.75,1.75),(0.3,0.42,2.15),56,'S3a'                                      # S3a: he kneels and peers into the gap
    if t<14.0: u=seg01(t,10.4,14.0); return (1.25-0.35*u,0.09,1.75+0.2*u),(0.15,0.13,2.75),66,'S3b'          # S3b: the empty space under the bed
    if t<15.3: return (1.05,1.4,0.9),(-0.1,0.95,2.1),56,'S4a'                                       # S4a: he stands and turns to the CRT
    if t<16.8: return (-0.55,1.72,1.65),(0.3,1.68,1.95),46,'S4b'                                    # S4b: close-up of the awake, terrified face
    if t<19.0: return (-1.10,1.0,2.499-0.46),(-1.10,1.04,2.5),56,'S4c'                              # S4c: match cut: the sleeping face in the feed
    if t<23.0: u=seg01(t,19.0,23.0); return (-1.10,1.08,2.499-0.88+0.06*u),(-1.10,0.88,2.5),56,'S5a'  # S5a: medium close-up of the CRT
    if t<24.0: return (-0.85,1.62,1.45),(0.3,1.68,1.95),50,'S5b'                                    # S5b: the awake man, paralysed, CRT glow on his face
    if t<25.0: return (-1.10,1.08,2.499-0.78),(-1.10,0.9,2.5),56,'S5c'
    u=seg01(t,25.0,29.0); return (-1.10,1.04,2.499-0.52+0.05*u),(-1.10,1.02,2.5),56,'S6'            # S6: extreme close-up, filling the frame

# ======================= render =======================
R=Renderer(W,H,fog=(4,6,12))
def reflection_mask(t):
    """the awake man's frozen silhouette in the CRT glass (only 28.0-28.6): rendered from the screen looking back at him, mirrored"""
    ms=man_state(t); Q,_=man(ms['O'],ms['Rl'],ms['Rt'],ms['P'],ms['Rh'],'wide',0); rr=Renderer(64,48,fog=(0,0,0))
    if ms['shr']>0: Q=[dict(q,p=[(p[0],p[1]+(0.03 if p[1]>1.3 else 0.0),p[2]) for p in q['p']]) for q in Q]; Q=[refresh(q) for q in Q]
    pos=np.array([-1.1,1.1,2.45]); cam=Camera.look(tuple(pos),tuple(ms['O']+np.array([0,0.55,0])))
    img,vi,zb=zrender(rr,cam,[Q],[],fov=62,fog_start=50,fog_end=60,ambient=1.0,return_z=True)
    m=(zb>0).astype(np.float32)[:,::-1]; m=np.asarray(Image.fromarray((m*255).astype(np.uint8)).resize((FEED_W,FEED_H),Image.BILINEAR)).astype(np.float32)/255.0
    return m
def render_frame(t):
    if t>=T_BLACK: return np.zeros((H*S,W*S,3),np.uint8)
    cam_p,tgt,fov,name=shot(t); cam=Camera.look(cam_p,tgt); cpa=np.array(cam_p)
    ms=man_state(t); fr=int(q15(t)*15)
    Qm,Dm=man(ms['O'],ms['Rl'],ms['Rt'],ms['P'],ms['Rh'],ms['face'],ms['mouth'],jit=0.0035,fr=fr)
    if ms['breathe']: Qm=[refresh(dict(q,p=[(p[0],p[1]+(ms['breathe'] if p[1]>1.2 else 0.0),p[2]) for p in q['p']])) for q in Qm]
    Dm=[x for x in Dm if np.linalg.norm(x['c']-cpa)<np.linalg.norm(x['hc']-cpa)]
    layers=list(ROOM)+[[SCREEN_Q],Qm,Dm]
    bias=[1.0]*len(layers); bias[-1]=1.004                      # the face decals are the last layer
    L=LIGHTS; amb=0.2
    if name=='S3b': layers=layers[:-1]+[dust(t),layers[-1]]; bias=[1.0]*len(layers); bias[-1]=1.004; L=[LIGHTS[0],((cam_p[0]+0.3,0.3,cam_p[2]+0.1),(110,180,140),0.45),((0.6,0.2,2.4),(70,90,150),0.4)]; amb=0.3
    img,vi,zb=zrender(R,cam,layers,L,fov=fov,fog_start=60,fog_end=70,ambient=amb,bias=bias,return_z=True)
    base=np.asarray(img); mask=(base==np.array(MARK)).all(-1)
    big=post.upscale(post.ps1(img,6),S)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=0,scan_dark=1.0,vignette=0.45,grain=1.6,band_period=1e9)
    out=vhs(big,fr,t)
    if mask.any():
        refl=reflection_mask(28.1) if (28.0<=t<28.6) else None
        tex=feed_img(t,refl); pts=[R.project(tuple(p),vi) for p in ((SCREEN['x0'],SCREEN['y1'],SCREEN['z']),(SCREEN['x1'],SCREEN['y1'],SCREEN['z']),(SCREEN['x1'],SCREEN['y0'],SCREEN['z']),(SCREEN['x0'],SCREEN['y0'],SCREEN['z']))]
        if all(pts):
            co=post._homography([(p[0]*S,p[1]*S) for p in pts],[(0,0),(FEED_W,0),(FEED_W,FEED_H),(0,FEED_H)])
            warp=np.asarray(tex.transform((W*S,H*S),Image.PERSPECTIVE,tuple(co),Image.NEAREST)); cov=np.asarray(Image.new('L',(FEED_W,FEED_H),255).transform((W*S,H*S),Image.PERSPECTIVE,tuple(co),Image.NEAREST))>0
            mu=np.repeat(np.repeat(mask,S,0),S,1); use=mu&cov; out=out.copy(); out[use]=warp[use]; out[mu&~cov]=(3,5,4)
    return out
def dust(t):
    cp=shot(t)[0]; r=np.random.default_rng(12); Q=[]
    for k in range(34):
        x=r.uniform(-0.4,1.5)+0.03*math.sin(t*0.7+k); y=r.uniform(0.03,0.24)+0.02*math.sin(t*0.9+k*1.7); z=r.uniform(2.18,2.95)
        if abs(x-cp[0])+abs(z-cp[2])>0.7: Q+=box(x-0.006,x+0.006,y-0.006,y+0.006,z-0.006,z+0.006,(120,128,150),emit=True)
    return Q

# ======================= subtitles (bottom-safe zone) =======================
SUBS=[(0.5,3.7,['SOMEONE WAS WATCHING HIM','SLEEP... FROM UNDER HIS BED.']),(4.5,7.1,["THE CAMERA WASN'T",'SUPPOSED TO BE THERE.']),(9.5,11.9,['HE CHECKED UNDERNEATH.','NOTHING.']),
      (14.5,17.3,['THEN HE REALIZED...','HE WAS STILL ASLEEP.']),(19.5,21.7,['AND THEN...','THE OTHER HIM WOKE UP.']),(26.0,27.1,["HE'S AWAKE."])]
def subtitle_layer(t):
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    for t0,t1,lines in SUBS:
        if t0<=t<t1:
            w=max(font.width(l,1) for l in lines)+8; x0=(W-w)//2; y0=250; d.rectangle([x0,y0,x0+w,y0+len(lines)*10+4],fill=(0,0,0,255))
            for i,l in enumerate(lines): font.text(d,l,x0+4,y0+3+i*10,(226,230,226),1,None)
    return lay.resize((W*S,H*S),Image.NEAREST)
def frame_full(t):
    out=render_frame(t)
    if t<T_BLACK:
        lay=subtitle_layer(t); im=Image.fromarray(out); im.paste(lay,(0,0),lay); out=np.asarray(im)
    return out
def frame(t): return Image.fromarray(frame_full(t)).resize((W,H),Image.NEAREST)

# ======================= QA manifest (tools/qa/scene_qa.py, PIPELINE.md) =======================
def _man(t): s=man_state(t); return dict(base=tuple(s['O']),yaw=math.atan2(s['Rl'][0,2],s['Rl'][2,2]),**{k:v for k,v in s.items() if k not in ('O',)})
def _man_model(**st): return man(st['base'],st['Rl'],st['Rt'],st['P'],st['Rh'],st['face'],st['mouth'])[0]
def _extra(t):
    out=[]
    ms=man_state(t); cp=np.array(shot(t)[0])
    if ms['O'][1]<0.45 and not (8.8<=t<14.95): out.append(('floor','man too low'))
    if not (-1.65<cp[0]<1.65 and 0.05<cp[1]<2.3 and 0.05<cp[2]<2.97): out.append(('camera',f'camera outside the room {tuple(np.round(cp,2))}'))
    return out
QA=dict(fps=FPS,dur=DUR,W=W,frame=frame,chars={'man':(_man,_man_model,'_none',1.0)},geom=lambda t,name,st,V: [('floor',f'{name} under the floor ({-V[:,1].min():.2f} m)')] if V[:,1].min()<-0.04 else [],extra=_extra,
    camera=lambda t: shot(t)[0],min_cam_dist=0.3,camera_ok=lambda p: -1.65<p[0]<1.65 and 0.05<p[1]<2.3 and -0.05<p[2]<2.97,
    scenes=[dict(id='broadcast',t0=0.0,t1=4.0,action='extreme close-up of the feed, snap pull-back to the awake man staring at the CRT'),dict(id='angle',t0=4.0,t1=9.0,action='over the shoulder: two hesitant steps toward the empty bed'),
            dict(id='kneel',t0=9.0,t1=10.4,action='he drops to his knees and peers into the gap'),dict(id='nothing',t0=10.4,t1=14.0,action='the space under the bed: completely empty'),
            dict(id='stands',t0=14.0,t1=15.3,action='he stands and turns to the CRT'),dict(id='face',t0=15.3,t1=16.8,action='terrified awake face'),dict(id='paradox',t0=16.8,t1=19.0,action='match cut: the sleeping face in the feed'),
            dict(id='wakes',t0=19.0,t1=25.0,action='the duplicate wakes, head turns stiffly to the lens; the paralysed man'),dict(id='reveal',t0=25.0,t1=29.0,action='extreme close-up, whisper, silence, knock, flinch reflection, snap to black'),dict(id='black',t0=29.0,t1=30.0,action='pure black')],
    weapon_events=[],texts=lambda: [('ui',l,1) for _,_,ls in SUBS for l in ls])

TEST=os.environ.get('TEST')
if TEST and __name__=='__main__':
    ts=[float(x) for x in TEST.split(',')]; ims=[Image.fromarray(frame_full(t)).resize((W*2,H*2),Image.NEAREST) for t in ts]
    shp=Image.new('RGB',(len(ims)*(W*2+4),H*2))
    for i,im in enumerate(ims): shp.paste(im,(i*(W*2+4),0))
    shp.save('test.png'); sys.exit()


# ======================= AUDIO: no music. hum, breathing, creaks, true silences, one synth tone, a whisper, one dry knock =======================
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=314); sr=s.sr; n=s.n; t=np.arange(n)/sr
    def env(pts):                                              # piecewise-linear envelope from [(time,level),...]
        return np.interp(t,[p[0] for p in pts],[p[1] for p in pts])
    def cut(x,a,b,k=0.004):                                    # hard but click-free removal of [a,b)
        m=np.ones(n); i,j=int(a*sr),int(b*sr); m[i:j]=0; kk=max(1,int(k*sr)); m=np.convolve(m,np.ones(kk)/kk,'same'); return x*m
    hum=(0.5*np.sin(2*PI*60*t)+0.32*np.sin(2*PI*120*t)+0.16*np.sin(2*PI*180*t)+0.06*np.sin(2*PI*240*t)+0.025*np.sin(2*PI*15734*t))*env([(0,0.17),(3.5,0.17),(4.2,0.075),(12.5,0.075),(14.0,0.0),(15.0,0.075),(27.5,0.075)])
    hiss=s.filt(s.rng.normal(0,1,n),lo=2500,hi=9000)*env([(0,0.028),(4.0,0.012),(12.5,0.012),(14.0,0.0),(15.0,0.012),(27.5,0.012)])
    drone=(np.sin(2*PI*43*t)+0.8*np.sin(2*PI*45.4*t))*env([(0,0.035),(12.5,0.05),(14.0,0.0),(15.0,0.075),(19.0,0.09),(27.5,0.09)])
    bed=hum+hiss+drone; bed=cut(bed,12.5,14.0); bed=cut(bed,27.5,29.0)                                   # TRUE silence 12.5-14.0 (the drone returns at 14.0), dead silence from 27.5
    s.L+=bed; s.R+=np.roll(bed,36)
    def place(x,t0,v=1.0,pan=0.0): s.place(x,t0,v,pan)
    def breath(t0,v=0.05,d_in=0.5,d_out=0.7,seed=0):
        a=s.filt_short(s.noise(d_in,seed),lo=500,hi=2600)*np.sin(np.pi*s.T(d_in)/d_in)**1.4; place(a,t0,v)
        b=s.filt_short(s.noise(d_out,seed+1),lo=350,hi=2000)*np.sin(np.pi*s.T(d_out)/d_out)**1.1; place(b,t0+d_in+0.12,v*0.85)
    tb=0.7; k=0
    while tb<28.0:                                                                                       # shallow, steady; faster as he gets frightened
        gap=2.3 if tb<14 else (1.7 if tb<19 else 1.25); lv=0.045 if not (12.4<tb<14.1) else 0.07
        breath(tb,lv,seed=k*3); tb+=gap; k+=1
    def creak(t0,v=0.18,f=95):
        d=0.55; tt=s.T(d); fr=f*(1+0.35*np.sin(2*PI*2.4*tt)-0.3*tt/d); x=np.sign(np.sin(2*PI*np.cumsum(fr)/sr))*0.5+np.sin(2*PI*np.cumsum(fr*2.02)/sr)*0.2
        x=s.filt_short(x+s.noise(d,int(t0*50))*0.6,lo=80,hi=900)*np.sin(np.pi*tt/d)**0.7*np.exp(-tt*1.5); place(x,t0,v)
        tt2=s.T(0.2); place(np.sin(2*PI*55*tt2)*np.exp(-tt2*18),t0,v*0.5)
    def pat(t0,v=0.06): tt=s.T(0.18); place(s.filt_short(s.noise(0.18,int(t0*77)),lo=60,hi=500)*np.exp(-tt*28)+np.sin(2*PI*70*tt)*np.exp(-tt*22)*0.5,t0,v)
    pat(5.45); creak(5.55,0.2,92); pat(7.0); creak(7.1,0.22,84)                                          # two distinct, heavy floorboard creaks
    pat(9.2,0.07); pat(9.4,0.09); place(s.filt_short(s.noise(0.5,91),lo=300,hi=2200)*np.sin(np.pi*s.T(0.5)/0.5)**1.5,9.3,0.02)   # kneeling, cloth
    pat(14.4,0.05); place(s.filt_short(s.noise(0.5,92),lo=300,hi=2200)*np.sin(np.pi*s.T(0.5)/0.5)**1.5,14.1,0.02)
    # the PS1-style synth tension tone, rising and discordant (the only musical element)
    i0,i1=int(19.0*sr),int(27.5*sr); tt=t[i0:i1]; pr=(tt-19.0)/8.5; f1=210+250*pr**1.4; f2=f1*1.0595*(1+0.004*np.sin(2*PI*0.7*tt))
    ph1=np.cumsum(f1)/sr; ph2=np.cumsum(f2)/sr; tone=np.sign(np.sin(2*PI*ph1))*0.5+np.sign(np.sin(2*PI*ph2+1.3))*0.5
    hold=np.repeat(tone[::6],6)[:len(tone)]; q=np.round(hold*3)/3; amp=(0.012+0.075*pr**1.6)*(0.7+0.3*np.sin(2*PI*5.5*tt)); tn=np.zeros(n); tn[i0:i1]=q*amp; tn=cut(tn,27.5,28.0,0.003)
    s.L+=tn; s.R+=np.roll(tn,20)
    # the narrator and the whisper (dry, no reverb)
    NB=np.zeros(n)
    for key,t0 in (('N1',0.4),('N2',4.5),('N3',9.5),('N4',14.5),('N5',19.5)):
        a,ar=_sf.read(os.path.join(TTS_DIR,'cb',key+'.wav')); a=a if a.ndim==1 else a.mean(1)
        a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a); act=a[np.abs(a)>0.02]; a=a/(np.sqrt((act**2).mean())+1e-9)*0.2
        i=int(t0*sr); j=min(n,i+len(a)); NB[i:j]+=a[:j-i]
    w,wr=_sf.read(os.path.join(TTS_DIR,'cb','W1.wav')); w=w if w.ndim==1 else w.mean(1); i=int(26.0*sr); j=min(n,i+len(w)); wh=np.zeros(n); wh[i:j]=w[:j-i]*0.55
    place(s.filt_short(s.noise(0.5,5),lo=40,hi=300)*0.0,0.0,0.0)                                         # (no reverb anywhere: nothing is wet)
    # the knock: dry, hollow, knuckles on plywood, behind and below him (a little left, high end rolled off)
    kd=0.2; tk=s.T(kd); kn=np.sin(2*PI*168*tk)*np.exp(-tk*34)+0.45*np.sin(2*PI*332*tk)*np.exp(-tk*48)+s.filt_short(s.noise(kd,66),lo=250,hi=1800)*np.exp(-tk*85)*0.55
    kn=s.filt_short(kn,lo=60,hi=2200); place(kn,28.0,0.95,pan=-0.35)
    place(s.filt_short(s.noise(0.3,67),lo=500,hi=2500)*np.sin(np.pi*s.T(0.3)/0.3)**2,28.12,0.012)       # the flinch: a breath-sized rustle
    gv=1.0*np.abs(s.L).max()/np.abs(NB).max()
    s.L=s.L+NB*gv*0.62+wh*gv*0.34; s.R=s.R+NB*gv*0.62+wh*gv*0.34
    st=np.stack([s.L,s.R],1); st=st/np.max(np.abs(st))*0.9
    st[int(27.5*sr):int(28.0*sr)]=0; st[int(29.0*sr):]=0                                              # dead silence at 27.5, and the last second is absolute silence (the knock is at 28.0)
    _sf.write(path,st,sr,subtype='PCM_16'); return path
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'camera_bed.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'cb_{a:05d}.mp4')],stdin=subprocess.PIPE)
    for f in range(a,min(b,N)): p.stdin.write(frame_full(f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
