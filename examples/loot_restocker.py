"""THE LOOT RESTOCKER - "Who refills every treasure chest?"  PS1 fantasy-RPG comedy short, 9:16. Fully procedural (nightkit).
Experiment A = ~30 s cut (this file). This file is also the LOCKED ASSET SOURCE for Experiment B (60 s):
goblin(), work_hat(), chest(), sack(), coin(), the hatch, the hallway set, notification(), the narrator/voice lines,
hook_shot()/HOOK_* (0-3 s, identical in B) and the ending (job transfer + final shot). The knight is the channel's
locked knight from examples/final_boss.py.
Voices: python tools/tts/lr.py  ->  $TTS_DIR/lr/*.wav
Run: TEST=0.5,5,12 python examples/loot_restocker.py -> test.png | PART=a:b (frames -> out/lr_a.mp4) | PART=audio
QA:  python tools/qa/scene_qa.py examples/loot_restocker.py"""
import os, sys, math, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, quad
from nightkit import post, font
from nightkit.zraster import zrender
from nightkit.audio import Sound
import final_boss as FB                                   # locked channel knight + geometry helpers
knight_model,prelit,box,seg,xform,limb=FB.knight,FB.prelit,FB.box,FB.seg,FB.xform,FB.limb
sm,seg01,lerp,lerp3,PI,Ry,Rx=FB.sm,FB.seg01,FB.lerp,FB.lerp3,FB.PI,FB.Ry,FB.Rx
TTS_DIR=FB.TTS_DIR
OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6
SCR=json.load(open(os.path.join(TTS_DIR,'lr','script.json')))
for ch,rows in {'!':['00100','00100','00100','00100','00100','00000','00100'],'?':['01110','10001','00001','00110','00100','00000','00100']}.items(): font.FONT.setdefault(ch,rows)

# ======================= palette =======================
SKIN=(96,170,70); SKIN_D=(70,132,52); TUNIC=(112,78,46); TUNIC_D=(84,58,34); ROPE=(170,140,90); EYEW=(240,236,220); PUPIL=(20,16,14)
HAT=(250,196,40); HAT_D=(206,150,20); LAMP=(255,250,200)
WOOD=(122,78,40); WOOD_D=(92,58,30); WOOD_L=(150,100,52); IRONB=(70,70,78); GOLDC=(250,206,60); GOLD_D=(200,150,30)
STONE=(92,84,78); STONE_D=(74,67,62); FLOOR1=(96,88,80); FLOOR2=(82,75,68); PIT=(18,14,12)
WHT=(242,238,226); YEL=(255,210,60); RED=(232,44,40); GRN=(120,230,90); BLU=(110,170,255); GRY=(150,150,160)

# ======================= LOCKED ASSET: work hat =======================
def work_hat(center,yaw,s=1.0):
    """yellow miner's work hat; center = bottom centre of the hat in world space"""
    c=np.array(center,float); Rb=Ry(yaw)
    def Wd(p): return tuple(c+Rb@(np.array(p,float)*s))
    return (box(-0.17,0.17,0.0,0.1,-0.17,0.17,HAT,xf=Wd)+box(-0.12,0.12,0.1,0.16,-0.12,0.12,HAT,xf=Wd)
            +box(-0.18,0.18,0.0,0.025,0.1,0.26,HAT_D,xf=Wd)+box(-0.045,0.045,0.04,0.11,0.17,0.2,LAMP,xf=Wd,emit=True)
            +box(-0.175,0.175,0.03,0.06,-0.175,0.175,HAT_D,xf=Wd))
HAT_SCALE_ON_KNIGHT=1.0

# ======================= LOCKED ASSET: the goblin =======================
def goblin_head_top(base,yaw,lean=0.0,hop=0.0):
    b=np.array(base,float)+np.array([0,hop,0]); piv=np.array([0,0.34,0]); p=np.array([0,0.95,0.0])
    return tuple(b+Ry(yaw)@(piv+Rx(lean)@(p-piv)))
def goblin(base,yaw,walk=0.0,run=0.0,lean=0.0,rh=None,lh=None,eyes=1.0,smile=0.0,hat=True,head=0.0,hop=0.0,climb=0.0,ears_down=0.0):
    """local forward = +z, ~0.95 m with the hat. eyes: 1 open .. 0.3 exhausted. smile: -1 frown .. 1 grin. climb>0: arms on the floor edge."""
    b=np.array(base,float)+np.array([0,hop,0]); Rb=Ry(yaw)
    def Wd(p): return tuple(b+Rb@np.array(p,float))
    hip=0.34
    def T(p): p=np.array(p,float); piv=np.array([0,hip,0]); return Wd(piv+Rx(lean+0.25*run)@(p-piv))
    Q=[]; amp=0.55+0.3*run; sw=amp*math.sin(walk)
    for sx,ph in ((-1,1),(1,-1)):
        hp=np.array([sx*0.08,hip,0]); a=ph*sw; ft=hp+np.array([0,-0.31*math.cos(a),0.31*math.sin(a)]); ft[1]=max(0.04,ft[1]+0.05*max(0,math.sin(walk*ph+PI/2))*(1 if walk else 0))
        lq,_=limb(hp,ft,(0,0,1),0.34,0.08,TUNIC_D,SKIN,0.07); Q+=xform(lq,Wd)
        Q+=box(ft[0]-0.05,ft[0]+0.05,ft[1]-0.04,ft[1]+0.03,ft[2]-0.04,ft[2]+0.12,SKIN_D,xf=Wd)                 # big bare feet
    Q+=box(-0.14,0.14,0.3,0.6,-0.09,0.09,TUNIC,xf=T)+box(-0.145,0.145,0.36,0.4,-0.095,0.095,ROPE,xf=T)
    Q+=box(-0.15,0.15,0.28,0.34,-0.1,0.1,TUNIC_D,xf=T)                                                     # ragged hem
    hy=0.6; Rh=Ry(head)
    def Hh(p): p=np.array(p,float); return T(np.array([0,hy,0])+Rh@(p-np.array([0,hy,0])))
    Q+=box(-0.15,0.15,0.6,0.86,-0.13,0.13,SKIN,xf=Hh)
    Q+=box(-0.035,0.035,0.66,0.76,0.13,0.21,SKIN_D,xf=Hh)                                                  # long nose
    for sx in (-1,1):
        e1=(sx*lerp(0.36,0.24,ears_down),lerp(0.86,0.66,ears_down),-0.06); e2=(sx*lerp(0.46,0.27,ears_down),lerp(0.9,0.5,ears_down),-0.1)   # ears (flop down in tight spaces)
        Q+=xform(seg((sx*0.15,0.76,0.0),e1,0.09,SKIN,0.03)+seg(e1,e2,0.05,SKIN_D,0.02),Hh)
        Q+=box(sx*0.03,sx*0.11,0.74,0.8,0.13,0.135,EYEW,xf=Hh,emit=True)+box(sx*0.055,sx*0.085,0.745,0.775,0.135,0.14,PUPIL,xf=Hh,emit=True)
        lid=0.8-0.06*(1-eyes)                                                                               # heavy eyelids when tired
        if eyes<0.98: Q+=box(sx*0.025,sx*0.115,lid,0.805,0.13,0.142,SKIN_D,xf=Hh)
    my=0.655; cy=my+0.022*smile                                                                             # mouth: centre + two corners
    Q+=box(-0.035,0.035,my-0.008,my+0.008,0.13,0.137,(40,20,16),xf=Hh)
    for sx in (-1,1): Q+=box(sx*0.035,sx*0.07,cy-0.008,cy+0.008,0.13,0.137,(40,20,16),xf=Hh)
    if smile>0.6: Q+=box(-0.05,0.05,my-0.004,my+0.012,0.137,0.14,(250,250,240),xf=Hh,emit=True)          # teeth in the grin
    if hat: Q+=xform(work_hat((0,0,0),0.0),lambda p: Hh(np.array(p)+np.array([0,0.86,0])))
    sh={-1:np.array([-0.17,0.56,0]),1:np.array([0.17,0.56,0])}
    idle={-1:np.array([-0.2,0.32,0.04]),1:np.array([0.2,0.32,0.04])}
    if run: idle={-1:np.array([-0.18,0.4,-0.12*math.sin(walk)]),1:np.array([0.18,0.4,0.12*math.sin(walk)])}
    if climb: idle={-1:np.array([-0.3,0.6+0.25*climb,0.2]),1:np.array([0.3,0.6+0.25*climb,0.2])}
    hand={-1:np.array(lh,float) if lh is not None else idle[-1],1:np.array(rh,float) if rh is not None else idle[1]}
    for sx in (-1,1):
        aq,_=limb(sh[sx],hand[sx],(sx*0.5,-0.3,-0.5),0.4,0.06,SKIN,SKIN,0.055); Q+=xform(aq,T)
        hp=hand[sx]; Q+=box(hp[0]-0.04,hp[0]+0.04,hp[1]-0.04,hp[1]+0.04,hp[2]-0.04,hp[2]+0.04,SKIN_D,xf=T)
    return Q
def goblin_arm(shoulder,hand):
    """LOCKED: just the goblin's arm reaching up out of the hatch (hook). Same skin, thickness and hand as goblin()."""
    aq,_=limb(shoulder,hand,(0.0,0.0,-1.0),0.62,0.06,SKIN,SKIN,0.055); hp=np.array(hand,float)
    return aq+box(hp[0]-0.04,hp[0]+0.04,hp[1]-0.04,hp[1]+0.04,hp[2]-0.04,hp[2]+0.04,SKIN_D)
def goblin_hand_world(st,side=1):
    """world position of a goblin hand for a state dict (for held props)"""
    if st.get('arm_only'): return st['hand_w']
    b=np.array(st['base'],float)+np.array([0,st.get('hop',0.0),0]); h=st.get('rh' if side>0 else 'lh')
    if h is None: h=(0.2*side,0.32,0.04)
    piv=np.array([0,0.34,0]); p=np.array(h,float); return tuple(b+Ry(st['yaw'])@(piv+Rx(st.get('lean',0.0))@(p-piv)))

# ======================= LOCKED ASSET: props =======================
def chest(base,yaw,lid=0.0,fill=0.0,coins=0,lod=0):
    """treasure chest, local forward (+z) = front. lid 0 shut .. 1 open (~110 deg). fill: gold mound 0..1; coins: loose coins at the bottom"""
    b=np.array(base,float); Rb=Ry(yaw)
    def Wd(p): return tuple(b+Rb@np.array(p,float))
    w,d,h=0.45,0.3,0.5
    if lod: Q=box(-w,w,0,h,-d,d,WOOD,xf=Wd)
    else:
        Q=(box(-w,w,0,0.06,-d,d,WOOD_D,xf=Wd)+box(-w,w,0.06,h,d-0.05,d,WOOD,xf=Wd)+box(-w,w,0.06,h,-d,-d+0.05,WOOD,xf=Wd)
           +box(-w,-w+0.05,0.06,h,-d+0.05,d-0.05,WOOD,xf=Wd)+box(w-0.05,w,0.06,h,-d+0.05,d-0.05,WOOD,xf=Wd))
        Q+=[quad([Wd((-w+0.05,0.07,d-0.05)),Wd((w-0.05,0.07,d-0.05)),Wd((w-0.05,0.07,-d+0.05)),Wd((-w+0.05,0.07,-d+0.05))],(30,20,12))]
    for sx in (-1,1): Q+=box(sx*0.3-0.04,sx*0.3+0.04,0.0,h+0.005,-d-0.01,d+0.01,IRONB,xf=Wd)
    if fill>0 and not lod: Q+=box(-w+0.07,w-0.07,0.07,0.07+0.36*fill,-d+0.07,d-0.07,GOLDC,xf=Wd)
    if not lod:
        for k in range(coins): x_=-0.25+0.11*(k%5); z_=-0.12+0.1*((k//5)%3); Q+=box(x_-0.035,x_+0.035,0.07,0.085,z_-0.035,z_+0.035,GOLDC,xf=Wd,emit=True)
    a=-1.9*lid                                                                                             # lid hinges on the back top edge
    def Ld(p): p=np.array(p,float); piv=np.array([0,h,-d]); return Wd(piv+Rx(a)@(p-piv))
    Q+=box(-w,w,h,h+0.16,-d,d,WOOD_L,xf=Ld)+box(-w-0.01,w+0.01,h+0.12,h+0.17,-d-0.01,d+0.01,IRONB,xf=Ld)
    Q+=box(-0.06,0.06,h-0.08,h+0.04,d,d+0.04,GOLD_D,xf=Wd)                                                 # lock
    return Q
def coin(p,r=0.045): x,y,z=p; return box(x-r,x+r,y-0.012,y+0.012,z-r,z+r,GOLDC,emit=True)
def sack(base,fill=1.0):
    """open coin sack: bulging cloth bag, rolled rim, gold showing at the top"""
    x,y,z=base; h=0.18+0.12*fill
    Q=box(x-0.15,x+0.15,y,y+0.06,z-0.13,z+0.13,(132,98,56))+box(x-0.19,x+0.19,y+0.06,y+h*0.75,z-0.17,z+0.17,(150,112,64))
    Q+=box(x-0.15,x+0.15,y+h*0.75,y+h,z-0.13,z+0.13,(140,104,60))+box(x-0.17,x+0.17,y+h,y+h+0.04,z-0.15,z+0.15,(118,86,48))
    if fill>0.05: Q+=box(x-0.12,x+0.12,y+h,y+h+0.03,z-0.1,z+0.1,GOLDC,emit=True)
    return Q

# ======================= LOCKED ASSET: the hallway of chests =======================
HATCH=(0.65,1.35,2.65,3.35)          # x0,x1,z0,z1 of the floor hatch
HERO_CHEST=((2.05,0,3.0),-PI/2)      # the chest of the story, facing the corridor centre
HALL_X=2.6; HALL_Z0=-6.0; HALL_Z1=84.0
def floor_tiles():
    xs=sorted(set([-HALL_X,HALL_X,HATCH[0],HATCH[1]]+list(np.arange(-HALL_X,HALL_X,0.7))))
    zs=sorted(set([HALL_Z0,HALL_Z1,HATCH[2],HATCH[3]]+list(np.arange(HALL_Z0,12,0.7))+list(np.arange(12,HALL_Z1,1.4))))
    Q=[]
    for i in range(len(xs)-1):
        for j in range(len(zs)-1):
            a,b_,c,d=xs[i],xs[i+1],zs[j],zs[j+1]
            if b_-a<1e-6 or d-c<1e-6: continue
            if HATCH[0]<=a and b_<=HATCH[1] and HATCH[2]<=c and d<=HATCH[3]: continue           # the hole
            par=(int(math.floor((a+b_)/1.4))+int(math.floor((c+d)/1.4)))%2
            Q.append(quad([(a,0,c),(b_,0,c),(b_,0,d),(a,0,d)],FLOOR1 if par else FLOOR2))
    return Q
def hall_static():
    Q=floor_tiles()
    x0,x1,z0,z1=HATCH                                                                                 # the pit under the hatch
    Q+=[quad([(x0,0,z0),(x1,0,z0),(x1,-1.2,z0),(x0,-1.2,z0)],(52,40,32)),quad([(x1,0,z1),(x0,0,z1),(x0,-1.2,z1),(x1,-1.2,z1)],(46,36,28)),
        quad([(x0,0,z1),(x0,0,z0),(x0,-1.2,z0),(x0,-1.2,z1)],(40,31,25)),quad([(x1,0,z0),(x1,0,z1),(x1,-1.2,z1),(x1,-1.2,z0)],(58,45,36)),
        quad([(x0,-1.2,z0),(x1,-1.2,z0),(x1,-1.2,z1),(x0,-1.2,z1)],PIT)]
    for sx in (-1,1):                                                                                  # walls, coarser far away
        zs=list(np.arange(HALL_Z0,12,1.5))+list(np.arange(12,HALL_Z1+0.1,4.0))
        for j in range(len(zs)-1):
            for k,(y0,y1) in enumerate(((0,1.2),(1.2,2.4),(2.4,3.6))):
                c=STONE if (j+k)%2 else STONE_D; x=sx*HALL_X
                pts=[(x,y0,zs[j]),(x,y0,zs[j+1]),(x,y1,zs[j+1]),(x,y1,zs[j])]
                Q.append(quad(pts if sx<0 else pts[::-1],c))
    Q+=[quad([(-HALL_X,3.6,HALL_Z0),(HALL_X,3.6,HALL_Z0),(HALL_X,3.6,HALL_Z1),(-HALL_X,3.6,HALL_Z1)],(34,28,26))]
    # entrance wall with the open exit (daylight) at z=-6
    Q+=box(-HALL_X,-0.8,0,3.6,HALL_Z0-0.3,HALL_Z0,STONE_D)+box(0.8,HALL_X,0,3.6,HALL_Z0-0.3,HALL_Z0,STONE_D)+box(-0.8,0.8,2.3,3.6,HALL_Z0-0.3,HALL_Z0,STONE_D)
    Q+=[quad([(-0.8,0,HALL_Z0-0.31),(0.8,0,HALL_Z0-0.31),(0.8,2.3,HALL_Z0-0.31),(-0.8,2.3,HALL_Z0-0.31)],(255,246,214),emit=True)]
    # the endless rows of chests (both walls, facing the centre); the hero chest is drawn separately
    for sx in (-1,1):
        for k,z in enumerate(np.arange(3.0 if sx<0 else 4.5,HALL_Z1-2,1.5)):
            Q+=chest((sx*2.05,0,z),-sx*PI/2,lod=1 if z>14 else 0,lid=0.0)
    return Q
HALL=hall_static()
TORCH_Z=list(np.arange(0.0,80,6.0))
def torches(t):
    Q=[]
    for k,z in enumerate(TORCH_Z):
        x=(-1 if k%2 else 1)*(HALL_X-0.08); fl=0.06*math.sin(t*13+k*2.1)+0.04*math.sin(t*29+k)
        Q+=box(x-0.05,x+0.05,2.0,2.4,z-0.05,z+0.05,IRONB)+box(x-0.1,x+0.1,2.42,2.62+fl,z-0.1,z+0.1,(255,120,40),emit=True)+box(x-0.05,x+0.05,2.52,2.72+fl,z-0.05,z+0.05,(255,214,90),emit=True)
    return Q
def lights(t):
    L=[]
    for k,z in enumerate(TORCH_Z[:7]):
        x=(-1 if k%2 else 1)*(HALL_X-0.5); L.append(((x,2.5,z),(255,170,90),1.1+0.12*math.sin(t*11+k)))
    L.append(((0,2.0,HALL_Z0+0.5),(255,240,210),1.2))
    return L
def hatch_lid(ang):
    """trapdoor hinged on its x0 edge, swinging up toward the corridor centre. ang 0 shut .. ~1.9 open"""
    x0,x1,z0,z1=HATCH
    def Wd(p): p=np.array(p,float); piv=np.array([x0,0,0]); return tuple(piv+Rz(ang)@(p-piv))
    Q=box(x0,x1,-0.0,0.05,z0,z1,WOOD,xf=Wd)
    for zz in (z0+0.15,z1-0.15): Q+=box(x0+0.02,x1-0.02,0.05,0.07,zz-0.04,zz+0.04,IRONB,xf=Wd)
    Q+=box(x1-0.14,x1-0.06,0.05,0.09,(z0+z1)/2-0.05,(z0+z1)/2+0.05,IRONB,xf=Wd)                                     # ring
    return Q
def Rz(a): c,s=math.cos(a),math.sin(a); return np.array([[c,-s,0],[s,c,0],[0,0,1]])

# ======================= STORY TIMELINE =======================
DUR=29.9; N=int(round(DUR*FPS))
VOICE=[('N1',0.10),('K1',9.1),('G1',11.45),('K2',16.35),('N2',28.0)]
HOOK_DUR=3.0                        # 0-3 s are shared verbatim with Experiment B
HOOK_COIN=(1.75,2.05)               # coin flicked from the hatch into the empty chest
GOB_SPOT=(1.25,0,2.35); GOB_YAW=math.atan2(2.05-1.25,3.0-2.35)
TOSSES=[4.55+k*0.42 for k in range(8)]          # goblin throws coins into the chest
NOTICE=8.45                                       # goblin notices the knight
KN_COIN_IN=19.55; DING=19.9; NOTE_ON=20.15; NOTE_OFF=26.9
HAT_GRAB=(21.8,22.3); HAT_JUMP=(22.85,23.45); HAT_ON=23.15
RUN=(23.9,26.4)
KNIGHT_SPOT=(1.38,0,3.85)
def kyaw_to(src,dst): return math.atan2(dst[0]-src[0],dst[2]-src[2])

def hatch_angle(t):
    if t<HOOK_DUR: return 0.6*sm(seg01(t,0.35,0.75))*(1-sm(seg01(t,2.45,2.85)))
    return 1.9*sm(seg01(t,3.0,3.3))
def chest_state(t):
    lid=1.0
    coins=1 if t>=HOOK_COIN[1] else 0
    fill=0.0
    if t>=TOSSES[0]: fill=min(0.75,0.1*sum(1 for x in TOSSES if t>=x+0.32))
    if t>=KN_COIN_IN+0.3: fill=0.8
    return dict(lid=lid,fill=fill,coins=coins if fill==0 else 0)

def goblin_state(t):
    x,_,z=GOB_SPOT
    if t<HOOK_DUR:                                            # HOOK: only an arm comes out of the hatch
        u=sm(seg01(t,0.8,1.3))*(1-sm(seg01(t,2.2,2.6))); flick=sm(seg01(t,1.6,1.8))
        hand=lerp3((1.15,-0.25,3.0),lerp3((1.3,0.24,3.0),(1.4,0.33,3.0),flick),u)
        return dict(base=(1.0,-1.1,3.0),yaw=PI/2,arm_only=True,shoulder_w=(1.0,-0.38,3.0),hand_w=hand)
    if t<4.2:                                                 # climbs out of the hatch (sack in hand), steps beside it
        c=sm(seg01(t,3.3,4.0)); st=sm(seg01(t,4.02,4.3))
        edge=(1.12,2.56)                                        # pulls himself onto the hole's edge while rising (diagonal: the ears fit the hole)
        e=sm(seg01(t,3.83,4.04))                                # pulls himself onto the edge as his feet reach floor level
        bx=lerp(lerp(0.97,edge[0],e),x,st); bz=lerp(lerp(2.97,edge[1],e),z,st); by=lerp(-1.15,0.0,c)
        hy=min(0.95,0.03-by) if e<0.5 else lerp(0.6,0.32,st)       # right hand grips the rim, left hand drags the sack
        return dict(base=(bx,by,bz),yaw=lerp(PI*0.75,GOB_YAW,max(st,sm(seg01(t,3.6,3.9))*0.5)),walk=t*10 if 0<st<1 else 0.0,eyes=0.55,
                    rh=(0.2,hy,0.14),lh=(-0.18,min(0.95,0.03-by) if e<0.5 else 0.35,0.1),ears_down=1.0-sm(seg01(c,0.85,1.0)),sack_hand=c<1.0)
    if t<NOTICE:                                              # hurried coin tossing, exhausted
        k=max(0,min(len(TOSSES)-1,int((t-TOSSES[0]+0.42)/0.42))); p=((t-4.2)%0.42)/0.42
        rh=lerp3((0.22,0.15,-0.05),(0.2,0.7,0.3),sm(seg01(p,0.35,0.75))) if t>=4.2 else None
        return dict(base=(x,0,z),yaw=GOB_YAW,rh=rh,lean=0.18,eyes=0.5,head=0.0)
    if t<16.35:                                               # caught; answers; slumps
        look=sm(seg01(t,NOTICE,NOTICE+0.3)); slump=sm(seg01(t,11.4,12.2))*(1-sm(seg01(t,16.1,16.6)))
        jump=0.12*math.sin(PI*seg01(t,NOTICE,NOTICE+0.3))
        return dict(base=(x,0,z),yaw=GOB_YAW,head=lerp(0.0,-1.3,look),hop=jump,lean=0.18*(1-look)+0.35*slump,eyes=lerp(0.9,0.35,slump),smile=-0.7*slump,
                    rh=(0.2,0.3,0.06),lh=(-0.2,0.3,0.06))
    if t<HAT_GRAB[0]:                                         # steps aside for the knight; watches; realises; grins
        a_=sm(seg01(t,16.7,17.5)); bx=lerp(x,GOB_ASIDE[0],a_); bz=lerp(z,GOB_ASIDE[2],a_)
        look_c=sm(seg01(t,18.6,19.2)); perk=sm(seg01(t,DING,DING+0.3)); grin=sm(seg01(t,20.6,21.3))
        face=kyaw_to(GOB_ASIDE,(1.6,0,3.4))
        return dict(base=(bx,0,bz),yaw=lerp(GOB_YAW,face,a_),walk=t*12 if 0<a_<1 else 0.0,head=lerp(-1.3,-0.4,look_c),eyes=lerp(0.5,1.0,perk),smile=lerp(0.0,1.0,grin),lean=0.1*(1-perk),hop=0.08*math.sin(PI*seg01(t,DING,DING+0.35)))
    hx,hy,hz=KNIGHT_SPOT; tgt=GOB_HAT_SPOT
    if t<HAT_JUMP[1]+0.25:                                    # takes his hat off, hops toward the knight, puts it on him
        g=sm(seg01(t,HAT_GRAB[0],HAT_GRAB[1])); mv=seg01(t,HAT_GRAB[0],HAT_JUMP[0]); j=seg01(t,HAT_JUMP[0],HAT_JUMP[1])
        bx,bz=path_xz([GOB_ASIDE,(0.42,0,3.4),tgt],mv); yaw=lerp(kyaw_to(GOB_ASIDE,(1.6,0,3.4)),kyaw_to((bx,0,bz),KNIGHT_SPOT),sm(seg01(mv,0.6,1.0))) if mv<1 else kyaw_to(tgt,KNIGHT_SPOT)
        dk=np.array([hx-tgt[0],hz-tgt[2]]); dk/=np.linalg.norm(dk); arc=GOB_HOP_IN*math.sin(PI*j) if 0<j<1 else 0.0
        bx+=dk[0]*arc; bz+=dk[1]*arc
        hop=1.0*math.sin(PI*j) if 0<j<1 else 0.0
        reach=sm(seg01(t,HAT_JUMP[0],HAT_ON))*(1-sm(seg01(t,HAT_ON+0.03,HAT_ON+0.2)))
        rh=lerp3(lerp3((0.2,0.32,0.04),(0.06,0.98,0.02),g),(0.06,0.95,0.36),reach)
        return dict(base=(bx,0,bz),yaw=yaw,hop=hop,rh=rh,smile=1.0,eyes=1.0,hat=t<HAT_GRAB[0]+0.25,walk=t*12 if 0<mv<1 else 0.0)
    # runs away to the exit (daylight), happy
    u=seg01(t,RUN[0],RUN[1]); bx,bz=path_xz([tgt,(0.38,0,3.35),(0.3,0,1.0),(0.0,0,HALL_Z0-0.6)],u)
    turn=sm(seg01(t,HAT_JUMP[1]+0.25,RUN[0]+0.1))
    return dict(base=(bx,0,bz),yaw=lerp(kyaw_to((tgt[0],0,tgt[2]),KNIGHT_SPOT),PI,turn),run=1.0 if t>=RUN[0] else 0.0,walk=t*16 if t>=RUN[0] else 0.0,
                smile=1.0,eyes=1.0,hat=False,hop=0.06*abs(math.sin(t*16)) if t>=RUN[0] else 0.0,gone=t>=RUN[1])

GOB_HAT_SPOT=(0.72,0,3.66); GOB_HOP_IN=0.12
SACK_SPOT=(1.58,0,1.72)                                       # where the sack sits after the climb
GOB_ASIDE=(0.42,0,2.45)                                       # left of the hatch, out of the knight's way
def path_xz(P,u):
    """constant-speed position along a polyline of (x,0,z) points, u in 0..1"""
    P=[np.array([p[0],p[2]],float) for p in P]; L=[np.linalg.norm(b-a) for a,b in zip(P,P[1:])]; d=max(0.0,min(1.0,u))*sum(L)
    for a,b,l in zip(P,P[1:],L):
        if d<=l or l==L[-1]: v=a+(b-a)*(d/l if l>0 else 0); return v[0],v[1]
        d-=l
    return P[-1][0],P[-1][1]                 # where the goblin stands to jump; how far the hop carries him in
def knight_state(t):
    kx,_,kz=KNIGHT_SPOT
    if t<4.0:                                                 # walks away from the looted chest, back to camera
        u=seg01(t,0.0,4.0); return dict(base=(lerp(0.3,0.9,u),0,lerp(3.9,8.4,u)),yaw=math.atan2(0.6,4.5),walk=t*8.0,sword='hip')
    if t<6.1:                                                 # stops, looks around at the rows of chests
        return dict(base=(0.9,0,8.4),yaw=lerp(math.atan2(0.6,4.5),0.0,sm(seg01(t,4.0,4.4))),head=0.6*math.sin(PI*seg01(t,4.4,5.6)),sword='hip')
    if t<8.3:                                                 # turns back, returns
        tu=sm(seg01(t,6.1,6.6)); w=sm(seg01(t,6.5,8.3)); p=(lerp(0.9,0.35,w),0,lerp(8.4,4.05,w))
        return dict(base=p,yaw=lerp(0.0,PI,tu),walk=t*8.0 if 0.0<w<1.0 else 0.0,sword='hip')
    face=kyaw_to((0.35,0,4.05),GOB_SPOT)
    if t<16.35:
        tilt=0.3*math.sin(PI*seg01(t,9.1,9.8)); point=sm(seg01(t,10.0,10.3))*(1-sm(seg01(t,10.9,11.3)))
        return dict(base=(0.35,0,4.05),yaw=lerp(PI,face,sm(seg01(t,8.3,8.7))),head=tilt,rh=(lerp(0.27,0.15,point),lerp(0.86,1.25,point),lerp(0.04,0.55,point)) if point>0.02 else None,sword='hip')
    if t<17.4:                                                # sympathetic: hand on heart
        hh=sm(seg01(t,16.4,16.8))*(1-sm(seg01(t,17.1,17.4)))
        return dict(base=(0.35,0,4.05),yaw=face,head=0.18*hh,lh=(-0.05,1.15,0.2) if hh>0.02 else None,sword='hip')
    to_chest=kyaw_to(KNIGHT_SPOT,(2.05,0,3.0))
    if t<18.5:                                                # takes a coin from his belt pouch, walks to the chest
        w=sm(seg01(t,17.7,18.5)); pouch=sm(seg01(t,17.4,17.65)); up=sm(seg01(t,17.65,17.9))
        rh=lerp3(lerp3((0.27,0.86,0.04),(0.15,0.8,0.14),pouch),(0.25,1.05,0.3),up)
        return dict(base=(lerp(0.35,kx,w),0,lerp(4.05,kz,w)),yaw=lerp(face,to_chest,w),walk=t*8.0 if 0<w<1 else 0.0,rh=rh,sword='hip',coin_hand=pouch>0.5)
    if t<HAT_GRAB[0]:                                         # places the coin inside the open chest
        r=sm(seg01(t,18.6,19.45))*(1-sm(seg01(t,19.8,20.3))); lean=0.22*r
        drop_pt=chest_drop_local()
        rh=lerp3((0.25,1.05,0.3),drop_pt,r)
        look=sm(seg01(t,20.2,20.6))*(-0.5)
        return dict(base=KNIGHT_SPOT,yaw=to_chest,rh=rh,lean=lean,sword='hip',coin_hand=t<KN_COIN_IN,head=look)
    if t<27.0:                                                # gets the hat; watches the goblin run off
        follow=sm(seg01(t,RUN[0],RUN[0]+1.2)); face_g=kyaw_to(KNIGHT_SPOT,GOB_HAT_SPOT)
        turn=sm(seg01(t,22.3,22.8)); bow=sm(seg01(t,22.75,23.05))*(1-sm(seg01(t,HAT_JUMP[1],HAT_JUMP[1]+0.35)))       # turns to the goblin, bows his head
        look_g=lerp(-0.5,0.0,turn)*(1-follow)
        yaw=lerp(lerp(to_chest,face_g,turn),kyaw_to(KNIGHT_SPOT,(0.0,0,-5.0)),follow)
        flinch=0.08*math.sin(PI*seg01(t,HAT_ON,HAT_ON+0.3))
        return dict(base=KNIGHT_SPOT,yaw=yaw,head=look_g+flinch,lean=0.28*bow,sword='hip',hat=t>=HAT_ON)
    # ENDING (shared with B): turns to the endless hallway of chests
    tu=sm(seg01(t,27.0,27.9)); slump=sm(seg01(t,28.4,29.2))
    return dict(base=KNIGHT_SPOT,yaw=lerp(kyaw_to(KNIGHT_SPOT,(0.0,0,-5.0)),2*PI,tu),head=0.0,lean=0.08*slump,sword='hip',hat=True,
                rh=(0.25,lerp(0.86,0.8,slump),0.04),lh=(-0.25,lerp(0.86,0.8,slump),0.04))
def chest_drop_local():
    """knight-local hand target just above the open chest, a little inside the front edge"""
    p=np.array([1.88,0.62,3.25])-np.array(KNIGHT_SPOT); return tuple(Ry(-kyaw_to(KNIGHT_SPOT,(2.05,0,3.0)))@p)
def knight_hand_world(ks,side=1):
    b=np.array(ks['base'],float); h=ks.get('rh' if side>0 else 'lh') or ((0.27,0.86,0.04) if side>0 else (-0.27,0.86,0.04))
    piv=np.array([0,0.82,0]); p=np.array(h,float); return tuple(b+Ry(ks['yaw'])@(piv+Rx(ks.get('lean',0.0))@(p-piv)))
def knight_head_top(ks):
    b=np.array(ks['base'],float); piv=np.array([0,0.82,0]); p=np.array([0,1.8,-0.04])
    return tuple(b+Ry(ks['yaw'])@(piv+Rx(ks.get('lean',0.0))@(p-piv)))

# ======================= SHOTS =======================
def hook_shot(t):
    """0-3 s, shared with Experiment B: low 3/4 view of the empty chest + hatch, knight walking away in the back"""
    u=sm(seg01(t,0,HOOK_DUR)); return dict(cam=lerp3((-0.25,0.68,0.55),(-0.05,0.64,0.95),u),tgt=(1.3,0.32,3.45),fov=52)
def ending_shot(t):
    """final shot (shared with B): behind the knight, down the endless hallway"""
    u=sm(seg01(t,27.0,DUR)); return dict(cam=lerp3((1.2,1.25,1.1),(1.35,1.45,2.2),u),tgt=(0.4,1.0,40.0),fov=60)
def shot(V):
    if V<HOOK_DUR: return hook_shot(V)
    if V<6.2:  u=sm(seg01(V,3.0,6.2)); return dict(cam=lerp3((0.05,0.85,0.9),(0.15,0.95,1.15),u),tgt=(1.55,0.45,2.9),fov=66)
    if V<9.0:  u=sm(seg01(V,6.2,9.0)); return dict(cam=lerp3((-1.4,1.25,0.3),(-1.3,1.3,0.6),u),tgt=(1.15,0.75,3.8),fov=66)
    if V<11.3: u=sm(seg01(V,9.0,11.3)); return dict(cam=lerp3((2.15,1.2,1.3),(2.1,1.22,1.45),u),tgt=(0.4,1.35,4.05),fov=58)
    if V<13.9: u=sm(seg01(V,11.3,13.9)); return dict(cam=lerp3((0.88,0.88,3.32),(0.92,0.86,3.2),u),tgt=(1.25,0.74,2.35),fov=60)
    if V<16.35: u=sm(seg01(V,13.9,16.35)); return dict(cam=lerp3((0.3,1.2,1.0),(0.0,3.2,-2.6),u),tgt=lerp3((0.8,0.9,4.0),(0.0,0.6,22.0),u),fov=lerp(64,58,u))
    if V<18.55: u=sm(seg01(V,16.35,18.55)); return dict(cam=lerp3((-1.1,1.3,1.2),(-0.9,1.35,1.5),u),tgt=(1.1,0.9,3.3),fov=64)
    if V<21.0: u=sm(seg01(V,18.55,21.0)); return dict(cam=lerp3((1.45,1.5,1.5),(1.4,1.45,1.65),u),tgt=(1.85,0.6,3.2),fov=60)
    if V<23.8: u=sm(seg01(V,21.0,23.8)); return dict(cam=lerp3((-0.3,1.35,1.4),(-0.2,1.4,1.6),u),tgt=(1.2,1.2,3.5),fov=62)
    if V<27.0: u=sm(seg01(V,23.8,27.0)); return dict(cam=lerp3((0.25,1.55,7.0),(0.3,1.5,6.6),u),tgt=(-0.1,0.9,-5.5),fov=62)
    return ending_shot(V)

# ======================= RENDER =======================
R=Renderer(W,H,fog=(22,16,14))
def held_props(V,ks,gs):
    Q=[]
    if gs is not None and not gs.get('gone'):
        if gs.get('sack_hand'): Q+=sack(np.array(goblin_hand_world(gs,-1))-np.array([0,0.3,0]),1.0)
        if V<HOOK_COIN[0] and 1.15<V: Q+=coin(np.array(goblin_hand_world(gs,1))+np.array([0,0.05,0]),0.065)
        if HOOK_COIN[0]<=V<HOOK_COIN[1]:                                                            # the hook coin arcs into the chest
            u=seg01(V,HOOK_COIN[0],HOOK_COIN[1]); a=np.array(goblin_hand_world(goblin_state(HOOK_COIN[0]),1)); b=np.array([1.95,0.12,3.05])
            Q+=coin(tuple(a+(b-a)*u+np.array([0,0.35*math.sin(PI*u),0])),0.065)
        for t0 in TOSSES:                                                                          # tossed coins (3 per throw)
            if t0<=V<t0+0.36:
                u=seg01(V,t0,t0+0.36); a=np.array(goblin_hand_world(goblin_state(t0),1)); b=np.array([2.0,0.3,3.0])
                for k in range(3):
                    off=np.array([0.06*(k-1),0.03*k,0.05*(k-1)]); Q+=coin(tuple(a+off+(b+off-a)*u+np.array([0,0.4*math.sin(PI*u),0])),0.04)
    if 4.2<=V and gs is not None:                                                                  # the sack stays by the hatch
        if not gs.get('sack_hand'): Q+=sack(SACK_SPOT,max(0.2,1.0-0.1*sum(1 for x in TOSSES if V>=x)))
    if ks.get('coin_hand'): Q+=coin(knight_hand_world(ks,1))
    if KN_COIN_IN<=V<KN_COIN_IN+0.25:                                                              # the knight's coin falls in
        u=seg01(V,KN_COIN_IN,KN_COIN_IN+0.25); a=np.array(knight_hand_world(knight_state(KN_COIN_IN),1)); b=np.array([1.9,0.07+0.36*0.75,3.15])
        Q+=coin(tuple(a+(b-a)*u))
    # the work hat: on the goblin (drawn by goblin()), in his hand, or on the knight
    if gs is not None and HAT_GRAB[0]+0.25<=V<HAT_ON: Q+=work_hat(np.array(goblin_hand_world(gs,1))+np.array([0,0.04,0]),gs['yaw'])
    if ks.get('hat'): Q+=work_hat(knight_head_top(ks),ks['yaw'],HAT_SCALE_ON_KNIGHT)
    return Q
def render(V,sh):
    cam=Camera.look(sh['cam'],sh['tgt'])
    ks=knight_state(V); gs=goblin_state(V); cs=chest_state(V)
    layers=[HALL,torches(V),hatch_lid(hatch_angle(V)),chest(HERO_CHEST[0],HERO_CHEST[1],**cs)]
    layers.append(prelit(knight_model(**{k:v for k,v in ks.items() if k in KN_KEYS}),sh['cam'],warm=0.12))
    if gs is not None and gs.get('arm_only'): layers.append(goblin_arm(gs['shoulder_w'],gs['hand_w']))
    elif gs is not None and not gs.get('gone'): layers.append(goblin(**{k:v for k,v in gs.items() if k in GB_KEYS}))
    layers.append(held_props(V,ks,gs))
    L=lights(V)
    if DING<=V<DING+0.8: L=L+[((2.0,1.0,3.0),(255,220,120),2.5*(1-seg01(V,DING,DING+0.8)))]
    img,vi=zrender(R,cam,layers,L,fov=sh['fov'],fog_start=6,fog_end=34,ambient=0.32)
    return post.ps1(img),vi
KN_KEYS={'base','yaw','walk','run','sword','rh','lh','lean','head','sit','eyes','swing'}
GB_KEYS={'base','yaw','walk','run','lean','rh','lh','eyes','smile','hat','head','hop','climb','ears_down'}

# ======================= UI (2D overlays) =======================
def otext(d,s,x,y,col,sc=1):
    o=max(1,sc//2)
    for ox,oy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)): font.text(d,s,x+ox*o,y+oy*o,(0,0,0),sc,None)
    font.text(d,s,x,y,col,sc,None)
HOOK_LINES=['WHO REFILLS','ALL THE','TREASURE','CHESTS IN','VIDEO GAMES?']
HIL={'REFILLS','TREASURE','CHESTS','YOU','FILL','EVERY.','SINGLE.','ONE.','HELP','ONE.','LAST','ASKED.','WAIT..'}
SPK={'N':(None,WHT),'K':('KNIGHT:',BLU),'G':('GOBLIN:',GRN)}
def wrap(txt,n=27):
    out=[]; c=''
    for w_ in txt.split():
        if len(c)+len(w_)+(1 if c else 0)>n: out.append(c); c=w_
        else: c=(c+' '+w_).strip()
    return out+[c]
def subtitle(d,V):
    cur=None
    for k,t0 in VOICE:
        if (t0<=V or k=='N1') and V<t0+SCR['dur'][k]+0.15: cur=k
    if cur is None: return
    if cur=='N1':
        y=26
        for ln in HOOK_LINES:
            x=(W-font.width(ln,2))//2
            for wd in ln.split(' '): otext(d,wd,x,y,YEL if wd in HIL else WHT,2); x+=font.width(wd,2)+12
            y+=19
        return
    name,col=SPK[cur[0]]; txt=SCR['text'][cur].upper().replace('...','..')
    lines=wrap(((name+' ') if name else '')+txt); y=266-11*(len(lines)-1)
    for ln in lines:
        xw=font.width(ln); x=(W-xw)//2; d.rectangle([x-3,y-2,x+xw+2,y+8],fill=(0,0,0)); cx=x
        for wd in ln.split(' '):
            c=col if wd==name else (YEL if wd in HIL else WHT); otext(d,wd,cx,y,c); cx+=font.width(wd)+6
        y+=11
def notification(d,V):
    """LOCKED: the hiring notification (shared with B)"""
    if not (NOTE_ON<=V<NOTE_OFF): return
    drop=sm(seg01(V,NOTE_ON,NOTE_ON+0.25)); y=int(lerp(-50,44,drop)); x0,x1=6,W-6
    blink=(int(V*6)%2==0) or V>NOTE_ON+1.0
    d.rectangle([x0,y,x1,y+44],fill=(24,6,8),outline=(255,90,80) if blink else (160,30,30)); d.rectangle([x0+2,y+2,x1-2,y+14],fill=RED)
    otext(d,'! NEW EMPLOYEE REGISTERED',x0+6,y+5,WHT)
    otext(d,'SHIFT: 999 YEARS',x0+6,y+20,YEL); otext(d,'BREAKS: 0',x0+6,y+31,GRY) if False else None
    sec=V-NOTE_ON
    if sec>0.6: otext(d,'ROLE: LOOT RESTOCKER',x0+6,y+31,GRY)
def emotes(d,vi,V,gs):
    if gs is None or gs.get('gone'): return
    if gs.get('arm_only'): gs=dict(gs,base=(9,9,9))
    if NOTICE<=V<NOTICE+0.9:                                                                       # '!' when he is caught
        p=R.project(goblin_head_top(gs['base'],gs['yaw'],gs.get('lean',0),gs.get('hop',0))+np.array([0,0.35,0]),vi)
        if p: x,y=int(p[0]),int(p[1]); d.rectangle([x-6,y-10,x+6,y+8],fill=WHT,outline=(0,0,0)); font.text(d,'!',x-2,y-7,RED,1,None) ; font.text(d,'!',x-2,y-7,RED,1,None)
    if 4.3<=V<NOTICE or 11.6<=V<16.2:                                                              # sweat drops: exhausted
        p=R.project(goblin_head_top(gs['base'],gs['yaw'],gs.get('lean',0),gs.get('hop',0)),vi)
        if p:
            for k in range(2):
                ph=(V*1.6+k*0.5)%1.0; x=int(p[0])+(-7 if k else 8); y=int(p[1])+4+int(14*ph)
                d.rectangle([x,y,x+1,y+2],fill=(150,210,255)); d.point((x,y-1),fill=(150,210,255))
    if HOOK_COIN[1]<=V<HOOK_COIN[1]+0.6 or 1.15<=V<HOOK_COIN[0]:                                   # glint on the hook coin
        p=R.project((1.95,0.2,3.05) if V>=HOOK_COIN[1] else np.array(goblin_hand_world(goblin_state(V),1))+np.array([0,0.05,0]),vi)
        if p:
            x,y=int(p[0]),int(p[1]); r=3+int(2*math.sin(V*20))
            for dx,dy in ((r,0),(-r,0),(0,r),(0,-r)): d.line([x,y,x+dx,y+dy],fill=(255,244,170))
    if DING<=V<DING+0.9:                                                                           # sparkle on the chest
        p=R.project((2.0,0.6,3.0),vi)
        if p:
            r=int(4+10*seg01(V,DING,DING+0.9)); x,y=int(p[0]),int(p[1])
            for a in range(8):
                ang=a*PI/4+V*3; d.point((x+int(r*math.cos(ang)),y+int(r*math.sin(ang))),fill=(255,240,160))
def frame(V):
    sh=shot(V); img,vi=render(V,sh); d=ImageDraw.Draw(img)
    emotes(d,vi,V,goblin_state(V)); notification(d,V); subtitle(d,V)
    return img

# ======================= QA manifest (tools/qa/scene_qa.py, PIPELINE.md) =======================
def _kn(t): return {k:v for k,v in knight_state(t).items() if k in KN_KEYS}
def _gb(t):
    g=goblin_state(t)
    if g is None or g.get('gone') or g.get('arm_only'): return None       # the hook arm is checked in _extra
    return {k:v for k,v in g.items() if k in GB_KEYS}
def _geom(t,name,st,V):
    out=[]
    if V[:,1].min()<-0.04:                                                       # below the floor only through the hatch hole
        below=V[V[:,1]<-0.04]; x0,x1,z0,z1=HATCH
        if ((below[:,0]<x0-0.02)|(below[:,0]>x1+0.02)|(below[:,2]<z0-0.02)|(below[:,2]>z1+0.02)).any(): out.append(('floor',f'{name} under the floor outside the hatch'))
    if (np.abs(V[:,0])>HALL_X+0.02).any(): out.append(('wall',f'{name} inside a hallway wall'))
    x0,x1,z0,z1=HATCH; bx,by,bz=st['base']
    if by>-0.01 and st.get('hop',0)<0.05 and hatch_angle(t)>0.3 and x0+0.03<bx<x1-0.03 and z0+0.03<bz<z1-0.03: out.append(('floor',f'{name} stands over the open hatch'))
    if hatch_angle(t)<0.3:
        m=(V[:,0]>x0+0.02)&(V[:,0]<x1-0.02)&(V[:,2]>z0+0.02)&(V[:,2]<z1-0.02)&(V[:,1]>-0.02)&(V[:,1]<0.06)
        if m.any(): out.append(('intersect',f'{name} passes through the shut trapdoor'))
    # chest boxes (hero chest and the first rows): bodies must not enter them
    for cx,cz in [(2.05,3.0)]+[(-2.05,z) for z in np.arange(3.0,12,1.5)]+[(2.05,z) for z in np.arange(4.5,12,1.5)]:
        inn=(np.abs(V[:,0]-cx)<0.27)&(np.abs(V[:,2]-cz)<0.4)&(V[:,1]<0.48)
        if name=='knight' and KN_COIN_IN-1.0<t<KN_COIN_IN+0.6 and cx==2.05 and cz==3.0: continue     # his hand reaches into the open chest
        if inn.sum()>0: out.append(('intersect',f'{name} inside a chest at z={cz:.1f}'))
    return out
def _extra(t):
    out=[]
    ks=knight_state(t); gs=goblin_state(t)
    if gs.get('arm_only'):                                                                          # the hook arm only comes out of the hole
        V=np.array([p for q in goblin_arm(gs['shoulder_w'],gs['hand_w']) for p in q['p']]); below=V[V[:,1]<-0.02]; x0,x1,z0,z1=HATCH
        if len(below) and ((below[:,0]<x0)|(below[:,0]>x1)|(below[:,2]<z0)|(below[:,2]>z1)).any(): out.append(('floor','goblin arm under the floor outside the hatch'))
    if ks.get('hat') and HAT_ON<=t:                                                                 # the hat sits on the head
        top=np.array(knight_head_top(ks)); kb=np.array(ks['base'])
        if not (1.7<top[1]<1.95 and np.linalg.norm(top[[0,2]]-kb[[0,2]])<0.25): out.append(('hat',f'hat not on the knight head ({tuple(np.round(top,2))})'))
    if HAT_GRAB[0]+0.25<=t<HAT_ON:                                                                 # hat in the goblin hand must reach the head at HAT_ON
        if abs(t-(HAT_ON-1/FPS))<0.5/FPS:
            hp=np.array(goblin_hand_world(goblin_state(t),1)); top=np.array(knight_head_top(knight_state(HAT_ON)))
            if np.linalg.norm(hp-top)>0.3: out.append(('hat',f'hat jumps {np.linalg.norm(hp-top):.2f} m from the goblin hand to the head'))
    if KN_COIN_IN-1/FPS<=t<KN_COIN_IN:                                                             # coin leaves the hand above the chest opening
        hp=np.array(knight_hand_world(ks,1))
        if not (1.62<hp[0]<2.45 and 2.75<hp[2]<3.4 and 0.45<hp[1]<1.0): out.append(('coin',f'knight releases the coin outside the chest opening ({tuple(np.round(hp,2))})'))
    return out
QA=dict(fps=FPS,dur=DUR,W=W,frame=frame,
    chars={'knight':(_kn,knight_model,'sword','hip'),'goblin':(_gb,goblin,'hat',True)},
    geom=_geom,extra=_extra,
    camera=lambda t: shot(t)['cam'],
    min_cam_dist=0.6,
    camera_ok=lambda p: abs(p[0])<HALL_X-0.1 and 0.05<p[1]<3.5 and HALL_Z0+0.2<p[2]<HALL_Z1,
    scenes=[dict(id='hook',t0=0.0,t1=3.0,action='knight walks away; a tiny hand flicks a coin into the empty chest',env='hallway, hero chest'),
            dict(id='climb-out',t0=3.0,t1=6.2,action='goblin climbs out with a sack, throws coins in',env='hero chest'),
            dict(id='knight-returns',t0=6.2,t1=9.0,action='knight comes back; goblin is caught (!)',env='hero chest'),
            dict(id='you-fill',t0=9.0,t1=11.3,action='knight: Wait.. YOU fill these?',env='hero chest'),
            dict(id='every-one',t0=11.3,t1=13.9,action='goblin, exhausted: Every. Single. One.',env='hero chest'),
            dict(id='reveal',t0=13.9,t1=16.35,action='camera rises: endless hallway of chests',env='hallway'),
            dict(id='help',t0=16.35,t1=18.55,action='knight: I will help with one; takes a coin',env='hero chest'),
            dict(id='coin-in',t0=18.55,t1=21.0,action='knight places the coin; ding; notification',env='hero chest'),
            dict(id='hat',t0=21.0,t1=23.8,action='goblin grins, puts his work hat on the knight',env='hero chest'),
            dict(id='run',t0=23.8,t1=27.0,action='goblin runs out into the daylight',env='hallway, exit'),
            dict(id='ending',t0=27.0,t1=DUR,action='knight turns to the endless chests',env='hallway')],
    weapon_events=[('goblin',HAT_GRAB[0]+0.25,True,False)],
    texts=lambda: [(k,ln,1) for k in SCR['text'] for ln in wrap((SPK[k[0]][0]+' ' if SPK[k[0]][0] else '')+SCR['text'][k].upper().replace('...','..'))]
          +[('N1',x,2) for x in HOOK_LINES]+[('note',s,1) for s in ('! NEW EMPLOYEE REGISTERED','SHIFT: 999 YEARS','ROLE: LOOT RESTOCKER')])

TEST=os.environ.get('TEST')
if TEST and __name__=='__main__':
    ims=[frame(float(x)) for x in TEST.split(',')]; shp=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): shp.paste(im,(i*182,0))
    shp.resize((shp.width*2,640),Image.NEAREST).save('test.png'); sys.exit()

# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=31); sr=s.sr; n=s.n; t=s.t; M=np.zeros(n); AMB=np.zeros(n)
    def note(buf,t0,m,d,v,wave='sq',duty=0.5,dec=3.0,att=0.005):
        f=440*2**((m-69)/12); tt=s.T(d); ph=(f*tt)%1
        x=np.where(ph<duty,1.0,-1.0) if wave=='sq' else (4*np.abs(ph-0.5)-1 if wave=='tri' else np.sin(2*np.pi*ph))
        env=np.minimum(1,tt/att)*np.exp(-tt*dec); i=int(t0*sr); j=min(n,i+len(tt)); buf[i:j]+=(x*env*v)[:j-i]
    def nb(t0,d,lo,hi,v,seed,shape=2,pan=0.0): s.place(s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v,pan)
    def clink(t0,v=0.05,seed=0):
        r=np.random.default_rng(seed); tt=s.T(0.35)
        for f in (r.uniform(2600,3400),r.uniform(4200,5200)): s.place(np.sin(2*np.pi*f*tt)*np.exp(-tt*14),t0,v)
    def step_k(t0,v=0.05,seed=0): tt=s.T(0.12); s.place(s.filt_short(s.noise(0.12,seed),lo=900,hi=5000)*np.exp(-tt*45)+np.sin(2*np.pi*2300*tt)*np.exp(-tt*60)*0.3,t0,v)
    def step_g(t0,v=0.03,seed=0): tt=s.T(0.06); s.place(s.filt_short(s.noise(0.06,seed),lo=300,hi=2500)*np.exp(-tt*70),t0,v)
    def creak(t0,d=0.45,v=0.08,f0=320): tt=s.T(d); s.place(np.sin(2*np.pi*np.cumsum(f0+120*np.sin(2*np.pi*7*tt))/sr)*np.sin(np.pi*tt/d)*0.6,t0,v)
    def thud(t0,f=70,v=0.15,d=0.3): tt=s.T(d); s.place(np.sin(2*np.pi*f*tt)*np.exp(-tt*14),t0,v)
    def whoosh(t0,v=0.03,seed=0): nb(t0,0.18,800,4000,v,seed)
    def boing(t0,v=0.05): tt=s.T(0.35); s.place(np.where(np.sin(2*np.pi*np.cumsum(180+380*tt/0.35)/sr)>0,1.0,-1.0)*np.exp(-tt*6)*0.5,t0,v)
    # ambience: dungeon air + torch crackle
    AMB+=s.filt(s.rng.normal(0,1,n),lo=60,hi=600)*0.012
    pr=np.random.default_rng(7)
    for tc in np.cumsum(pr.exponential(0.35,120)):
        if tc<DUR: i=int(tc*sr); x=np.sign(s.noise(0.01,int(tc*991)))*np.exp(-s.T(0.01)*300)*0.012; AMB[i:i+len(x)]+=x[:max(0,min(len(x),n-i))]
    # ---------- music ----------
    for k,(dt,m) in enumerate(HOOK_MOTIF): note(M,0.15+dt,m,0.5,0.03,'tri',dec=3)          # hook: sneaky plucks (shared with B)
    for k in range(6): note(M,0.15+k*0.5,45 if k%2==0 else 40,0.4,0.05,'tri',dec=5)
    def bouncy(a,b,v=1.0,root=60,minor=False,step=0.16):
        sc=[0,2,3,5,7,8,10,12] if minor else [0,2,4,5,7,9,11,12]; pat=[0,4,2,4,5,4,2,1,0,2,4,7,5,4,2,4]; bass=[0,0,4,4,5,5,4,4]; k=0; tc=a
        while tc<b-1e-6:
            note(M,tc,root+12+sc[pat[k%16]%8],step*0.8,0.02*v,'sq',0.25,10)
            if k%2==0: note(M,tc,root-12+sc[bass[(k//2)%8]%8],step*1.6,0.05*v,'tri',dec=5)
            if k%4==2: s.place(s.filt_short(s.noise(0.04,k),lo=5000)*np.exp(-s.T(0.04)*90),tc,0.01*v)
            k+=1; tc+=step
    bouncy(3.0,8.45,0.9)                                          # hurried restocking
    for k in range(4): note(M,8.45+k*0.12,72-k*5,0.1,0.03,'sq',0.5,10)          # caught!
    bouncy(13.9,16.3,0.6,root=57,minor=True,step=0.22)            # the endless hallway (slow, minor)
    bouncy(16.35,19.5,0.55,root=60,step=0.2)
    for k,m in enumerate((72,76,79,84,88,91)): note(M,DING+k*0.07,m,0.25,0.035,'sq',0.25,6)    # achievement jingle
    note(M,DING+0.45,96,0.6,0.03,'sq',0.25,3)
    note(M,NOTE_ON,36,0.5,0.08,'tri',dec=3); note(M,NOTE_ON,48,0.3,0.04,'sq',0.5,6)
    bouncy(21.0,23.85,0.6,root=57,minor=True,step=0.18)           # uh-oh
    bouncy(23.9,26.9,1.0,root=64,step=0.12)                       # the goblin's happy escape
    for k,(m,d) in enumerate(((58,0.45),(57,0.45),(56,0.45),(55,1.2))):     # sad trombone (ending, shared with B)
        tc=27.05+k*0.47; f=440*2**((m-69)/12); tt=s.T(d)
        x=(np.sin(2*np.pi*np.cumsum(f*(1+0.012*np.sin(2*np.pi*5*tt))*np.ones_like(tt))/sr)+0.4*np.sin(2*np.pi*np.cumsum(2*f*np.ones_like(tt))/sr))*np.minimum(1,tt/0.03)*np.exp(-tt*(1.5 if k<3 else 0.7))
        s.place(x,tc,0.045)
    # ---------- hook ----------
    for k in range(int(4.0/0.5)): step_k(0.05+k*0.5,0.04,k)
    creak(0.35,0.4,0.05,420); clink(HOOK_COIN[0],0.03,1); whoosh(HOOK_COIN[0],0.015,2); clink(HOOK_COIN[1],0.06,3); creak(2.45,0.4,0.04,380); thud(2.85,90,0.06)
    # ---------- the answer ----------
    creak(3.0,0.35,0.08,300); thud(3.3,60,0.1); nb(3.35,0.5,300,2000,0.03,4)        # trapdoor flips open, he scrambles out
    for k in range(3): step_g(3.9+k*0.1,0.03,10+k)
    for t0 in TOSSES: whoosh(t0,0.02,int(t0*10)); [clink(t0+0.33+0.04*k,0.035,int(t0*100)+k) for k in range(3)]
    for k in range(int((8.3-6.5)/0.42)): step_k(6.55+k*0.42,0.045,30+k)
    # ---------- the mistake ----------
    for k in range(5): step_g(16.75+k*0.16,0.03,40+k)
    s.place(np.sin(2*np.pi*3200*s.T(0.2))*np.exp(-s.T(0.2)*20),17.55,0.02)                    # coin out of the pouch
    for k in range(2): step_k(17.8+k*0.35,0.04,50+k)
    clink(KN_COIN_IN+0.25,0.07,60); clink(KN_COIN_IN+0.33,0.04,61)
    # ---------- the twist ----------
    for k in range(6): step_g(21.85+k*0.17,0.03,70+k)
    boing(HAT_JUMP[0],0.04); s.place(np.sin(2*np.pi*1400*s.T(0.12))*np.exp(-s.T(0.12)*30),HAT_ON,0.05); boing(HAT_ON+0.02,0.025)   # plop on the helmet
    thud(HAT_JUMP[1],120,0.06)
    for k in range(16): step_g(RUN[0]+k*0.14,0.035*(1-k/20),80+k)
    # ---------- voices ----------
    NB=np.zeros(n); duck=np.ones(n)
    for k_,t0 in VOICE:
        a,ar=_sf.read(os.path.join(TTS_DIR,'lr',f'{k_}.wav')); a=a if a.ndim==1 else a.mean(1)
        a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a)
        act=a[np.abs(a)>0.02]; a=a/(np.sqrt((act**2).mean())+1e-9)*0.2                 # every line at the same loudness (the helmet filter makes the knight quieter)
        i=int(t0*sr); j=min(n,i+len(a)); NB[i:j]+=a[:j-i]
        duck[max(0,i-int(0.05*sr)):min(n,j+int(0.1*sr))]=0.45
    duck=np.convolve(duck,np.ones(2400)/2400,'same')
    s.L+=2.0*M*duck+AMB; s.R+=2.0*np.roll(M,240)*duck+np.roll(AMB,700)
    s.reverb(0.16,length=1.2,decay=4.0)
    pk=max(np.abs(s.L).max(),np.abs(s.R).max()); gv=pk*1.05/np.abs(NB).max()
    s.L=s.L*(0.55+0.45*duck)+NB*gv; s.R=s.R*(0.55+0.45*duck)+NB*gv
    return s.save(path,peak=0.9)
HOOK_MOTIF=[(0.0,69),(0.25,72),(0.5,76),(1.0,74),(1.25,71),(1.75,69)]       # the restocker theme, shared with B
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'loot_restocker_a.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'lr_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.96,vignette=0.22,grain=1.5,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(post.upscale(frame(f/FPS),S),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
