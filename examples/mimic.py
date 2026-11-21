"""WHY DO MIMICS PRETEND TO BE CHESTS? (Insert Disc 2, 14-day test day 2, 02:00 slot, Tone 2.0) ~30 s PS1 drama, 9:16, nightkit.
Brief: briefs/mimic.md. A chest was opened and emptied by every hero for a hundred years; nobody put anything back. It learned to bite.
One knight opens it, does not draw his sword, takes nothing and leaves one coin. The lid closes like a breath.
Reuses: locked knight (examples/final_boss.py). NEW: chest with hinged lid + teeth + tongue + eyes, coin, hero hands, dust, dungeon alcove, one torch.
Voice: python tools/tts/mm.py src ; <chatterbox python> tools/tts/vc.py mm ; python tools/tts/mm.py build vc  -> $TTS_DIR/mm/
Run: TEST=1,5,9 python examples/mimic.py -> test.png | PART=a:b | PART=audio | tools/render_parts.py --prefix mm --audio mimic.wav"""
import os, sys, math, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','tts'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, quad
from nightkit import motion, post, font
from nightkit.zraster import zrender
from nightkit.audio import Sound, duck_envelope, soft_fire
import final_boss as FB

OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6; F=1.0/FPS
PI=math.pi; sm=motion.smooth
def seg01(t,a,b): return max(0.0,min(1.0,(t-a)/(b-a)))
def lerp(a,b,u): return a+(b-a)*u
def lerp3(a,b,u): return tuple(a[i]+(b[i]-a[i])*u for i in range(3))
def hsh(i,s=0): v=math.sin(i*127.1+s*311.7)*43758.5453; return v-math.floor(v)
box=FB.box; xform=FB.xform; seg=FB.seg
WHT=(242,238,226); YEL=(255,210,60); GOLD=(236,190,60); GOLD_D=(190,146,40)

# ======================= voice timings (tools/tts/mm.py) =======================
SCR=json.load(open(os.path.join(TTS_DIR,'mm','script.json')))
GAP=0.3; EXTRA={'3':0.1,'4':0.7,'5':0.0,'6':0.2}
def _lines():
    t=0.12; out=[]
    for k in [str(i) for i in range(1,8)]: out.append((k,round(t,3))); t+=SCR['dur'][k]+GAP+EXTRA.get(k,0.0)
    return out
LINES=_lines(); T0=dict(LINES)
DUR=round(T0['7']+SCR['dur']['7']+1.0,2); N=int(round(DUR*FPS))
def ws(k,i): return T0[k]+SCR['sent'][k][i][0]
def we(k,i): return T0[k]+SCR['sent'][k][i][1]

# ======================= story events =======================
CH=(0.0,0.0,3.0)                                                     # chest centre (on the floor), front faces -z
N_PULSE=5; MONT=(T0['2']+0.15,T0['2']+SCR['dur']['2']-0.2); PD=(MONT[1]-MONT[0])/N_PULSE
def pulse(k): return MONT[0]+k*PD
T_CLOSE=(ws('3',1)+0.2,we('3',1)-0.05)                               # the lid creaks shut on the empty inside
T_BITE=T0['4']-0.05                                                  # it learns to bite: the lid opens, chomps, a hero jumps back
T_JUMP=T_BITE+0.65; T_FLASH=T_BITE+1.05; T_LEAVE=T_BITE+1.5
T_KNEEL=T0['5']-0.35; T_STILL=ws('5',0)+0.8                           # the knight kneels; the teeth stop
T_PLACE=(ws('6',1)-0.35,ws('6',1)+0.45)                              # the coin goes in
T_SHUT=(T0['7']+0.35,T0['7']+SCR['dur']['7']-0.3)                    # the lid closes like a breath
CUTS=[0.0,T0['3']-0.06,T_BITE-0.1,T0['5']-0.06,T0['6']-0.06,T_PLACE[0]-0.15,T0['7']-0.1,DUR]
CUTS=[0.0,T0['3']-0.06,T0['4']-0.1,T0['5']-0.06,ws('6',1)-0.7,T0['7']-0.1,DUR]

# ======================= chest =======================
WOOD=(96,66,40); WOOD_D=(70,48,30); IRON=(58,58,66); STONE=(62,66,88); STONE_D=(46,50,70); STONE_L=(84,88,112)
def lid_angle(t):
    """the chest lid (0 = shut, ~1.2 = wide open)"""
    a=0.0
    if t<MONT[0]:                                                     # frame 0: the lid twitches
        a=(0.21+0.05*math.sin(2*PI*t/2.2))*(1-sm(seg01(t,MONT[0]-0.6,MONT[0]-0.15)))     # open a crack, breathing
    for k in range(N_PULSE):
        p=pulse(k)
        if p<=t<p+PD: a=1.05*sm(seg01(t,p+0.05,p+0.3))*(1-sm(seg01(t,p+PD-0.3,p+PD-0.05)))
    if MONT[1]-0.05<=t<T_CLOSE[0]: a=1.05                              # left open after the last hero
    if T_CLOSE[0]<=t<T_CLOSE[1]: a=1.05*(1-sm(seg01(t,*T_CLOSE)))
    if T_CLOSE[1]<=t<T_BITE: a=0.0
    if T_BITE<=t<T_BITE+1.6:                                           # bites: opens wide and chomps
        u=t-T_BITE; a=1.1*sm(seg01(u,0.0,0.25));
        if u>0.3: a=0.65+0.45*math.cos(2*PI*(u-0.3)*1.6)*(1-seg01(u,0.9,1.6)*0.5)
    if T_BITE+1.6<=t<T_STILL: a=lerp(0.9,1.15,sm(seg01(t,T_BITE+1.6,T_STILL)))
    if T_STILL<=t<T_SHUT[0]: a=1.15
    if T_SHUT[0]<=t: a=1.15*(1-sm(seg01(t,*T_SHUT)))
    return a
def eyes_on(t): return T_BITE-0.2<=t<T_STILL-0.2
def teeth_on(t): return t<MONT[0]-0.15 or t>=T_BITE-0.05                                   # before it learned to bite it is only a chest
def gold_level(t):
    """height of the gold left in the chest (the heroes take it all)"""
    if t<MONT[0]: return 0.16
    if t<MONT[1]: return 0.16*(1-sm(seg01(t,MONT[0]+0.4,MONT[1]-0.2)))
    return 0.0
def dust(t):
    return 0.15+0.85*sm(seg01(t,MONT[0],MONT[1]))                     # 0..1: dust on the chest and floor
def chest_model(t):
    cx,_,cz=CH; w,h,d=0.5,0.42,0.32; a=lid_angle(t); du=dust(t)
    wood=tuple(int(c*(1-0.35*du)+105*0.35*du) for c in WOOD); wood_d=tuple(int(c*(1-0.35*du)+90*0.35*du) for c in WOOD_D)
    Q=box(cx-w,cx+w,0,h,cz-d,cz-d+0.06,wood)+box(cx-w,cx+w,0,h,cz+d-0.06,cz+d,wood)+box(cx-w,cx-w+0.06,0,h,cz-d,cz+d,wood_d)+box(cx+w-0.06,cx+w,0,h,cz-d,cz+d,wood_d)
    Q+=box(cx-w+0.06,cx+w-0.06,0,0.05,cz-d+0.06,cz+d-0.06,(18,12,10))                                       # dark inside
    Q+=box(cx-w-0.02,cx+w+0.02,h*0.5,h*0.58,cz-d-0.02,cz+d+0.02,IRON)                                          # iron band
    Q+=box(cx-0.05,cx+0.05,h*0.55,h*0.85,cz-d-0.03,cz-d,GOLD)                                                  # lock
    gl=gold_level(t)
    if gl>0.001:
        for k in range(9):
            Q+=box(cx-0.42+0.1*k,cx-0.3+0.1*k,0.05,0.05+gl*(0.5+0.5*hsh(k)),cz-0.2+0.18*hsh(k,1),cz-0.05+0.18*hsh(k,1),GOLD if k%2 else GOLD_D)
    if teeth_on(t):
        Q+=box(cx-w+0.06,cx+w-0.06,0.05,0.07,cz-d+0.06,cz+d-0.06,(84,14,26))                                  # dark red mouth floor
        calm=sm(seg01(t,T_STILL,T_STILL+0.7)); tt=0.2+0.14*calm                                              # once calm the tongue rises: the coin will sit on it
        Q+=box(cx-0.3,cx+0.3,0.07,tt,cz-0.22,cz+0.26,(150,40,54))                                             # tongue
        for k in range(9): Q+=tooth(cx-0.4+0.1*k,0.07,cz-d+0.0,cz-d+0.06,h,+1,sc=(1.0-0.6*calm)*TS(t))                               # lower teeth on the front rim
    hinge=(cx,h,cz+d)
    def LID(p): return FB_rx(p,a,hinge)
    Lq=box(cx-w-0.02,cx+w+0.02,h,h+0.12,cz-d-0.02,cz+d+0.02,wood_d,xf=LID)+box(cx-w-0.02,cx+w+0.02,h+0.12,h+0.15,cz-d,cz+d,wood,xf=LID)
    Lq+=box(cx-w-0.03,cx+w+0.03,h,h+0.15,cz-d*0.1,cz+d*0.1,IRON,xf=LID)
    if teeth_on(t):
        Lq+=box(cx-w+0.04,cx+w-0.04,h-0.03,h,cz-d+0.04,cz+d-0.04,(74,12,26),xf=LID)                          # dark mouth inside the lid
        for k in range(9): Lq+=tooth(cx-0.35+0.1*k,0.07,cz-d+0.0,cz-d+0.06,h,-1,xf=LID,sc=TS(t))                      # upper teeth (pointed, interleaved)
        if t<MONT[0]:                                                                                          # frame 0: a glint on a tooth
            g=max(0.0,math.sin(2*PI*(t-0.3)/1.4))*0.055
            if g>0.004:
                gx,gy,gz=cx-0.05,h+0.075,cz-d-0.01
                Q+=box(gx-g,gx+g,gy-0.004,gy+0.004,gz-0.005,gz+0.005,(255,255,235),emit=True)+box(gx-0.004,gx+0.004,gy-g,gy+g,gz-0.005,gz+0.005,(255,255,235),emit=True)
    if eyes_on(t) and a>0.35:
        for sx in (-1,1): Lq+=box(cx+sx*0.18-0.03,cx+sx*0.18+0.03,h+0.0,h+0.05,cz-0.02,cz+0.0,(255,190,80),xf=LID,emit=True)
    return Q+Lq
TOOTH=(240,236,214)
def TS(t): return 1.0-sm(seg01(t,T_SHUT[0]-0.15,T_SHUT[0]+0.6))      # the teeth retract before the lid closes
def tooth(x,w_,z0,z1,y0,dirn,xf=None,sc=1.0):
    if sc<0.06: return []
    """a stepped, pointed tooth: base at y0, grows up (dirn=+1) or down (-1) in three narrowing steps"""
    Q=[]; y=y0
    for wd,hh in ((w_*0.5,0.052*sc),(w_*0.34,0.046*sc),(w_*0.18,0.042*sc)):
        ya,yb=(y,y+hh) if dirn>0 else (y-hh,y)
        Q+=box(x-wd,x+wd,ya,yb,z0,z1,TOOTH,xf=xf); y+=dirn*hh
    return Q
def FB_rx(p,a,c):
    x,y,z=p[0]-c[0],p[1]-c[1],p[2]-c[2]; ca,sa=math.cos(a),math.sin(a)
    return (c[0]+x,c[1]+ca*y-sa*z,c[2]+sa*y+ca*z)
def coin_pos(t):
    """the coin: in the knight's hand, then in the chest (None before he has it)"""
    if t<T_PLACE[0]-0.4: return None
    ks=kstate(t)
    if t<T_PLACE[0]+0.45 and ks is not None:
        hp=np.array(ks['base'])+FB.Ry(ks['yaw'])@np.array(ks['rh'])+np.array([0,0.0,0.0]); return tuple(hp+np.array([0,0.06,0]))
    return (0.0,0.345,2.88)
def coin_model(t):
    p=coin_pos(t)
    if p is None: return []
    Q=box(p[0]-0.075,p[0]+0.075,p[1],p[1]+0.022,p[2]-0.075,p[2]+0.075,GOLD,emit=True)+box(p[0]-0.05,p[0]+0.05,p[1]+0.022,p[1]+0.03,p[2]-0.05,p[2]+0.05,(255,226,120),emit=True)
    if t>=T_PLACE[0]+0.4 and lid_angle(t)>0.6:                                                                                      # a slow, steady glint
        g=0.07+0.08*(0.5+0.5*math.sin(2*PI*(t-T_PLACE[0])/1.1)); y=p[1]+0.045
        Q+=box(p[0]-g,p[0]+g,y,y+0.007,p[2]-0.006,p[2]+0.006,(255,250,210),emit=True)+box(p[0]-0.006,p[0]+0.006,y,y+0.007,p[2]-g,p[2]+g,(255,250,210),emit=True)+box(p[0]-0.006,p[0]+0.006,y,y+g*1.6,p[2]-0.006,p[2]+0.006,(255,250,210),emit=True)
    return Q

# ======================= heroes (hands in the montage, one hero who jumps back) =======================
HAND_COL=[((178,186,200),(112,120,138)),((120,84,56),(84,56,34)),((70,130,84),(52,98,62)),((190,64,56),(140,44,40)),((60,96,190),(44,70,150))]
def hand_model(t):
    Q=[]
    for k in range(N_PULSE):
        p=pulse(k)
        if not (p<=t<p+PD): continue
        u=t-p; sl,hd=HAND_COL[k]; side=-1 if k%2==0 else 1
        reach=sm(seg01(u,0.0,0.3)); dip=sm(seg01(u,0.4,0.6))*(1-sm(seg01(u,0.6,0.8))); out=1-sm(seg01(u,PD-0.3,PD-0.05))
        # hand goes to the lid front, then into the chest and back with a coin
        x=side*lerp(0.9,0.3,reach*out+0.0)*1.0; y=lerp(0.75,0.5,reach)-0.28*dip; z=lerp(2.2,2.7,reach)+0.0+0.25*dip
        hp=np.array([x*0.7,y,z]); sh=hp+np.array([side*0.6,0.45,-0.7])
        Q+=seg(sh,hp,0.13,sl)+box(hp[0]-0.075,hp[0]+0.075,hp[1]-0.06,hp[1]+0.06,hp[2]-0.075,hp[2]+0.075,hd)
        if dip>0.3 or (u>0.62 and u<PD-0.3): Q+=box(hp[0]-0.04,hp[0]+0.04,hp[1]-0.09,hp[1]-0.06,hp[2]-0.04,hp[2]+0.04,GOLD,emit=True)
    return Q
def hero_state(t):
    """the hero who meets the biting chest: steps up, jumps back, leaves"""
    if not (T_BITE-0.4<=t<T_LEAVE+0.9): return None
    d=dict(base=(-0.4,0.0,1.95),yaw=0.12,walk=0.0,run=0.0,sword='hand',lean=0.0,head=0.0,rh=(0.26,0.95,0.45),lh=None,swing=1.2)
    if t<T_BITE: d['base']=(-0.4,0.0,lerp(1.5,1.95,sm(seg01(t,T_BITE-0.4,T_BITE))))
    elif t<T_JUMP: d['lean']=-0.2*sm(seg01(t,T_BITE,T_JUMP))
    elif t<T_LEAVE:
        u=sm(seg01(t,T_JUMP,T_JUMP+0.3)); d.update(base=(-0.4-0.2*u,0.35*math.sin(PI*min(1.0,(t-T_JUMP)/0.4)),lerp(1.95,1.25,u)),lean=-0.25*(1-u),swing=1.0)
        if t>=T_FLASH: d['swing']=lerp(1.0,1.9,sm(seg01(t,T_FLASH-0.1,T_FLASH+0.05)))
    else:
        u=seg01(t,T_LEAVE,T_LEAVE+0.9); d.update(base=(lerp(-0.6,-1.6,u),0.0,lerp(1.25,0.4,u)),yaw=lerp(0.12,-2.4,sm(seg01(t,T_LEAVE,T_LEAVE+0.3))),walk=t*8.0,run=1.0,sword='hip')
    return d
def hero_knight(**st):
    Q=FB.knight(**st)
    for q in Q:
        c=tuple(q['col'])
        if c==FB.CAPE: q['col']=(196,60,52)
        elif c==FB.CAPE_D: q['col']=(140,40,36)
        elif c==FB.PLUME: q['col']=(220,90,60)
    return Q
def kstate(t):
    """the knight who gives something back (blue cape: the original)"""
    if t<T_KNEEL-0.9: return None
    sit=0.3*sm(seg01(t,T_KNEEL,T_KNEEL+0.8)); base=(-0.75,0.0,2.25); yaw=math.atan2(0.75,0.75)
    d=dict(base=base,yaw=yaw,walk=0.0,run=0.0,sword='hip',lean=0.34*sm(seg01(t,T_KNEEL,T_KNEEL+0.8)),head=0.0,rh=(0.26,0.86,0.3),lh=None,sit=sit)
    if t<T_KNEEL: d.update(base=(lerp(-2.2,-0.75,sm(seg01(t,T_KNEEL-0.9,T_KNEEL))),0.0,lerp(1.2,2.25,sm(seg01(t,T_KNEEL-0.9,T_KNEEL)))),walk=t*7.0,sit=0.0,lean=0.05)
    if t>=T_PLACE[0]-0.3:                                                                          # the right hand carries the coin to the chest
        u=sm(seg01(t,T_PLACE[0]-0.3,T_PLACE[0]+0.35)); d['rh']=lerp3((0.26,0.86,0.3),(0.55,0.52,0.78),u)
        if t>=T_PLACE[0]+0.5: d['rh']=lerp3((0.55,0.52,0.78),(0.26,0.86,0.3),sm(seg01(t,T_PLACE[0]+0.5,T_PLACE[1]+0.3)))
    if t>=T_SHUT[0]-0.2: d.update(sit=0.3*(1-sm(seg01(t,T_SHUT[0]-0.2,T_SHUT[0]+0.7))),lean=0.34*(1-sm(seg01(t,T_SHUT[0]-0.2,T_SHUT[0]+0.7))))
    return d

# ======================= set: stone alcove + corridor, one torch =======================
TORCH=(-1.45,1.5,3.0)
def room():
    Q=[]; zs=list(np.arange(-5,4.01,1.5))
    for i,z in enumerate(zs[:-1]):
        for j,x in enumerate(np.arange(-1.6,1.6,0.8)):
            Q.append(quad([(x,0,z),(x+0.8,0,z),(x+0.8,0,zs[i+1]),(x,0,zs[i+1])],(58,62,80) if (i+j)%2 else (48,52,68)))
    Q+=box(-2.2,-1.6,0,3.2,-5.0,4.2,STONE_D)+box(1.6,2.2,0,3.2,-5.0,4.2,STONE_D)+box(-2.2,2.2,0,3.2,4.0,4.4,STONE)
    for z in np.arange(-4,4.0,1.4): Q+=box(-1.62,-1.58,0.0,3.2,z,z+0.04,(40,36,44))+box(1.58,1.62,0.0,3.2,z,z+0.04,(40,36,44))
    for k,y in enumerate(np.arange(0.4,3.2,0.8)): Q+=box(-1.6,1.6,y,y+0.03,3.98,4.0,(40,36,44))
    Q+=box(-1.6,1.6,3.2,3.5,-5.0,4.0,(24,22,28))                                                       # ceiling
    Q+=box(-1.5,-1.35,1.1,1.5,2.9,3.1,(70,50,34))+box(-1.52,-1.33,1.5,1.62,2.88,3.12,(255,150,50),emit=True)  # the torch
    return Q
ROOM=room()
def floor_dust(t):
    du=dust(t); Q=[]
    for k in range(40):
        a=2*PI*hsh(k,1); r=0.2+0.9*hsh(k,2); x=0.0+r*math.cos(a)*1.1; z=3.0+r*math.sin(a)*0.8; s=0.06+0.12*hsh(k,3)
        if k/40.0<du: Q+=[quad([(x-s,0.005,z-s),(x+s,0.005,z-s),(x+s,0.005,z+s),(x-s,0.005,z+s)],(86,84,94))]
    return Q
def motes(t):
    Q=[]; du=dust(t)
    for k in range(int(18*du)):
        x=-1.0+2.0*hsh(k,4); z=2.0+1.8*hsh(k,5); y=(0.2+hsh(k,6)*1.5+0.05*t*(0.5+hsh(k,7)))%1.7+0.1; x+=0.15*math.sin(t*0.7+k)
        s=0.012; Q+=box(x-s,x+s,y,y+s,z-s,z+s,(190,176,150),emit=True)
    return Q
def lights(t):
    fl=1.0+0.07*math.sin(t*9)+0.05*math.sin(t*17.5+1)
    L=[(TORCH,(255,160,84),1.5*fl),((0.0,1.4,1.0),(255,170,110),0.18*fl)]
    if t>=T_PLACE[0]+0.2: L.append(((0.0,0.6,2.8),(255,205,110),0.55*sm(seg01(t,T_PLACE[0]+0.2,T_PLACE[0]+0.6))))
    return L

# ======================= cameras =======================
def creep(t,t0,rate=0.0014): return motion.creep(t,t0,rate,FPS)
def cam_shot(t):
    if t<CUTS[1]:      # A+B: close on the chest from one angle (the montage keeps it); each hero shifts it a little
        k=min(N_PULSE-1,max(0,int((t-MONT[0])/PD))) if t>=MONT[0] else 0; j=0.04*(k%3-1) if t>=MONT[0] else 0.0
        tgt=(0.0,0.4,3.0); return dict(cam=motion.dolly((0.3+j,0.62+0.02*k,1.05),tgt,creep(t,0.0,0.0012)),tgt=tgt,fov=46)
    if t<CUTS[2]:      # C: higher, looking into the empty chest as the lid shuts
        tgt=(0.0,0.3,3.0); return dict(cam=motion.dolly((0.5,1.2,1.5),tgt,creep(t,CUTS[1],0.0016)),tgt=tgt,fov=44)
    if t<CUTS[3]:      # D: the bite, the hero jumps back and leaves (wide from the right)
        tgt=(-0.15,0.6,2.45); return dict(cam=motion.dolly((1.25,1.15,0.35),tgt,creep(t,CUTS[2],0.0008)),tgt=tgt,fov=60)
    if t<CUTS[4]:      # E: the knight kneels, the teeth stop (two-shot from the right)
        tgt=(-0.25,0.55,2.75); return dict(cam=motion.dolly((1.6,0.95,1.5),tgt,creep(t,CUTS[3],0.0012)),tgt=tgt,fov=54)
    if t<CUTS[5]:      # F: the gauntlet puts the coin in (close, from above)
        tgt=(0.0,0.35,2.9); return dict(cam=motion.dolly((0.2,1.3,1.45),tgt,creep(t,CUTS[4],0.0016)),tgt=tgt,fov=36)
    tgt=(0.0,0.4,3.0)  # G: the lid closes like a breath
    return dict(cam=motion.dolly((0.3,1.0,1.6),tgt,creep(t,CUTS[5],0.0014)),tgt=tgt,fov=42)

# ======================= render =======================
RND=Renderer(W,H,fog=(12,10,16))
def lum_lit(Q,cam_p,lum=0.8,warm=0.2):
    c=np.mean([q['c'] for q in Q],axis=0); Ld=np.array(cam_p,float)-c+np.array([0,2.5,0]); Ld/=np.linalg.norm(Ld)+1e-9
    for q in Q:
        if q['emit']: continue
        k=(0.42+0.58*abs(float(q['n']@Ld)))*lum; col=np.array(q['col'],float)*k
        col=col*(1-warm)+col*np.array([1.0,0.7,0.5])*warm; q['col']=tuple(int(min(255,v)) for v in col); q['emit']=True
    return Q
def shake_px(t):
    k=motion.kick(t,T_FLASH,2.4,6,FPS); return (0.0,k)
def render3d(t):
    sh=cam_shot(t); cam=Camera.look(sh['cam'],sh['tgt']); cp=sh['cam']
    layers=[ROOM,floor_dust(t),chest_model(t),hand_model(t),coin_model(t),motes(t)]
    hs=hero_state(t)
    if hs is not None: layers.append(lum_lit(hero_knight(**hs),cp,0.7))
    ks=kstate(t)
    if ks is not None: layers.append(lum_lit(FB.knight(**ks),cp,0.7))
    img,vi,zb=zrender(RND,cam,layers,lights(t),fov=sh['fov'],fog_start=3,fog_end=16,ambient=0.2,shake=shake_px(t),return_z=True)
    return post.ps1(img),vi
def flash_alpha(t):
    return 0.35*(1.0-seg01(t,T_FLASH,T_FLASH+0.18)) if T_FLASH-F<=t<T_FLASH+0.18 else 0.0
def frame_low(t):
    img,vi=render3d(t); fa=flash_alpha(t)
    if fa>0: img=Image.fromarray(np.clip(np.asarray(img).astype(np.float32)*(1-fa)+255*fa,0,255).astype(np.uint8))
    return img
def finish(t):
    img=frame_low(t); end=seg01(t,DUR-0.5,DUR)
    if end>0: img=Image.fromarray((np.asarray(img).astype(np.float32)*(1-0.6*end)).astype(np.uint8))
    return img

# ======================= subtitles (1080x1920, 1.25x, sentence timings from the voice) =======================
SUB_F=7.0; ADV=6.9; HIL={'HUNDRED','BITE.','COIN.','BACK.','CHESTS?','LINE?'}
def _rows(text,n=17):
    out=[]; c=[]
    for w_ in text.split():
        if len(' '.join(c+[w_]))>n and c: out.append(c); c=[w_]
        else: c.append(w_)
    return out+[c]
def _subs():
    res=[]
    for k,t0 in LINES:
        for i,(a,b,tx) in enumerate(SCR['sent'][k]):
            nxt=SCR['sent'][k][i+1][0] if i+1<len(SCR['sent'][k]) else b+(0.6 if k=='1' else 0.25)
            res.append((t0+a-0.03,t0+nxt-0.02,_rows(tx,14 if k=='1' else 17),k))
    return res
SUBS=_subs()
def _tw(wd,sc): return len(wd)*ADV*sc
def sub_overlay(t):
    """line 1 (the question) is a centred title card with an outline, no box; every other sentence is a roomy box near the bottom"""
    for a,b,rows,key in SUBS:
        if a<=t<b:
            card=(key=='1'); sc=9.0 if card else SUB_F; lh=(12.5 if card else 12.8)*sc
            lines=[' '.join(r) for r in rows]; wmax=max(_tw(l,sc) for l in lines)-(ADV-6)*sc
            padx=5.5*sc; pady=3.6*sc; w=wmax+2*padx; h=(len(lines)-1)*lh+7*sc+2*pady
            x0=(W*S-w)/2; y0=(H*S*0.34-h/2) if card else (H*S-130-h)
            ov=Image.new('RGB',(W*S,H*S),(0,0,0)); m=Image.new('L',(W*S,H*S),0); do=ImageDraw.Draw(ov); dm=ImageDraw.Draw(m)
            if not card: dm.rectangle([round(x0),round(y0),round(x0+w)-1,round(y0+h)-1],fill=255)
            o=max(2,round(sc*0.55)); cells=[]
            for i,r in enumerate(rows):
                lw=_tw(' '.join(r),sc)-(ADV-6)*sc; x=x0+(w-lw)/2
                for wd in r:
                    col=YEL if wd.upper().strip(',!?:') in HIL or wd.upper() in HIL else WHT; font.check(wd)
                    for k_,ch in enumerate(wd.upper()):
                        for j,row in enumerate(font.FONT[ch]):
                            for i2,bit in enumerate(row):
                                if bit=='1': X=x+(k_*ADV+i2)*sc; Y=y0+pady+i*lh+j*sc; cells.append((round(X),round(Y),round(X+sc)-1,round(Y+sc)-1,col))
                    x+=_tw(wd,sc)+ADV*sc
            if card:
                for bx in cells: dm.rectangle([bx[0]-o,bx[1]-o,bx[2]+o,bx[3]+o],fill=255)
            for bx in cells: do.rectangle(bx[:4],fill=bx[4]); dm.rectangle(bx[:4],fill=255)
            return ov,m
    return None
def frame_final(t):
    arr=post.upscale(finish(t),S); so=sub_overlay(t)
    if so: m=np.asarray(so[1])>0; arr[m]=np.asarray(so[0])[m].astype(np.float32)
    return arr
def frame(t):
    img=finish(t); so=sub_overlay(t)
    if so: ov=so[0].resize((W,H),Image.BOX); m=so[1].resize((W,H),Image.BOX).point(lambda v:255 if v>100 else 0); img.paste(ov,(0,0),m)
    return img

TEST=os.environ.get('TEST')
if TEST and __name__=='__main__':
    ims=[frame(float(x)) for x in TEST.split(',')]; shp=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): shp.paste(im,(i*182,0))
    shp.resize((shp.width*2,640),Image.NEAREST).save(os.environ.get('TEST_OUT','test.png')); sys.exit()

# ======================= QA manifest =======================
def _kn(t): return kstate(t)
def _hero(t): return hero_state(t)
QA=dict(fps=FPS,dur=DUR,W=W,frame=frame,
    chars={'knight':(_kn,FB.knight,'sword','hip'),'hero':(_hero,FB.knight,'sword','hand')},
    geom=lambda t,name,st,V: [('floor',f'{name} under the floor')] if V[:,1].min()<-0.05 else [],
    camera=lambda t: cam_shot(t)['cam'],min_cam_dist=0.3,camera_ok=lambda p: -2.0<p[0]<2.0 and -5<p[2]<4.0 and 0.1<p[1]<3.2,
    allow_jump=[(w,f/FPS) for w in ('knight','hero') for c in CUTS for f in range(int(c*FPS)-2,int(c*FPS)+4)]+[('hero',T_JUMP+i/FPS) for i in range(0,12)],
    weapon_events=[('hero',T_LEAVE,'hand','hip')],
    scenes=[dict(id=f's{i}',t0=CUTS[i],t1=CUTS[i+1],action=a) for i,a in enumerate((
        'hook + montage: close on the chest, the lid twitches, five heroes take the gold (CAM A/B)',
        'the lid creaks shut on the empty inside (CAM C)',
        'it bites: a hero jumps back, a clang, he leaves (CAM D)',
        'the knight kneels, the teeth stop (CAM E)',
        'the gauntlet puts one coin inside (CAM F)',
        'the lid closes like a breath (CAM G)'))],
    texts=lambda: [])

# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=47); sr=s.sr; n=s.n; t=s.t; BED=np.zeros(n); FX=np.zeros(n)
    def put(buf,x,t0,v=1.0):
        i=int(t0*sr)
        if i>=n or i<0: return
        j=min(n,i+len(x)); buf[i:j]+=(x*v)[:j-i]
    def nb(t0,d,lo,hi,v,seed,shape=2): put(FX,s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v)
    def tone(t0,m,d,v,wave='sin',duty=0.5,dec=3.0,att=0.004,glide=0.0):
        f=440*2**((m-69)/12); tt=s.T(d); fr=f*(1+glide*tt/d); ph=np.cumsum(fr)/sr%1
        x=np.where(ph<duty,1.0,-1.0) if wave=='sq' else (4*np.abs(ph-0.5)-1 if wave=='tri' else np.sin(2*np.pi*ph))
        put(FX,x*np.minimum(1,tt/att)*np.exp(-tt*dec),t0,v)
    def creak(t0,d=0.9,v=0.05,seed=0,f0=170,rev=False):
        tt=s.T(d); f=f0*(1+0.3*np.sin(2*np.pi*(2.4+0.5*hsh(seed))*tt))+(60*tt/d if not rev else -60*tt/d); ph=np.cumsum(f)/sr; x=np.sin(2*np.pi*ph)*0.5+0.3*np.sin(4*np.pi*ph)+0.25*s.filt_short(s.noise(d,seed),lo=300,hi=1500)
        put(FX,x*np.sin(np.pi*tt/d)**1.5,t0,v)
    def coin_clink(t0,v=0.03,seed=0):
        for k,f in enumerate((3100,4200,2600)): tt=s.T(0.35); put(FX,np.sin(2*np.pi*f*(1+0.01*hsh(seed+k))*tt)*np.exp(-tt*(14+4*k)),t0+k*0.045,v*(1-0.25*k))
    def snap(t0,v=0.1):
        tt=s.T(0.25); put(FX,s.filt_short(s.noise(0.25,int(t0*7)),lo=600,hi=5000)*np.exp(-tt*42)+np.sin(2*np.pi*95*tt)*np.exp(-tt*16)*0.6,t0,v)
    def clang(t0,v=0.12):
        tt=s.T(0.6); put(FX,sum(np.sin(2*np.pi*f*tt)*np.exp(-tt*k) for f,k in ((310,6),(820,9),(1490,14)))*0.4+s.filt_short(s.noise(0.6,int(t0*13)),lo=1200,hi=6000)*np.exp(-tt*28),t0,v)
    def step(t0,v=0.03,seed=0):
        tt=s.T(0.12); put(FX,s.filt_short(s.noise(0.12,seed),lo=200,hi=1800)*np.exp(-tt*38)+np.sin(2*np.pi*80*tt)*np.exp(-tt*30)*0.25,t0,v)
    # ---- bed: dungeon air (low drone + a slow filtered breeze) and ONE torch: soft low-passed flicker + a few real crackles (never a per-sample gate)
    BED+=s.filt(s.rng.normal(0,1,n),lo=40,hi=300)*0.07*(0.7+0.3*np.sin(2*np.pi*t/6.3))
    BED+=(np.sin(2*np.pi*49*t)+0.5*np.sin(2*np.pi*73.5*t+0.4))*0.016
    BED+=s.filt(s.rng.normal(0,1,n),lo=400,hi=1800)*0.008*np.clip(0.5+0.5*np.sin(2*np.pi*t/4.1+1.0),0,None)
    BED+=soft_fire(s,level=0.0045,crackles_per_s=3,seed=61)
    # ---- frame 0: the lid twitches
    creak(0.5,0.6,0.035,seed=1,f0=150); creak(1.35,0.5,0.04,seed=2,f0=140)
    # ---- montage: each hero: lid creak, coins clinking out, a thud as the lid falls
    for k in range(N_PULSE):
        p=pulse(k); creak(p+0.05,0.4,0.05,seed=10+k,f0=160+8*k); coin_clink(p+0.45,0.034-0.003*k,seed=20+k); nb(p+PD-0.18,0.15,80,500,0.03,30+k)
    # ---- the lid shuts: a long creak, the end on a hollow thud
    creak(T_CLOSE[0],T_CLOSE[1]-T_CLOSE[0],0.055,seed=40,f0=150,rev=True); nb(T_CLOSE[1]-0.12,0.25,60,400,0.07,41)
    # ---- it bites: lid flung open, two snaps, the jump, the clang, footsteps away; then quiet
    creak(T_BITE,0.25,0.05,seed=50,f0=200); snap(T_BITE+0.35,0.1); snap(T_BITE+0.7,0.12)
    nb(T_JUMP,0.2,300,2500,0.05,51); step(T_JUMP+0.38,0.05,52); clang(T_FLASH,0.11)
    for k in range(5): step(T_LEAVE+k*0.17,0.03,60+k)
    # ---- the hall after the hero has left: two far water drips keep the quiet from going dead
    for dt in (T_LEAVE+1.25,T_LEAVE+2.0): tone(dt,96,0.5,0.014,dec=9); tone(dt+0.2,84,0.4,0.006,dec=10)
    # ---- the knight: steps, kneeling, a breath
    for k in range(int((T_KNEEL-(T_KNEEL-0.9))/0.3)): step(T_KNEEL-0.9+k*0.3,0.028,70+k)
    nb(T_KNEEL+0.2,0.5,200,1400,0.035,80,1)
    # ---- the teeth stop: the bed alone for a moment, then the coin: one tink, a soft chime under it
    tone(T_PLACE[0]+0.45,98,0.9,0.05,dec=5); tone(T_PLACE[0]+0.47,104,0.6,0.02,dec=7)
    for k_,m in enumerate((88,93)): tone(T_PLACE[0]+0.9+k_*0.2,m,1.6,0.018,dec=2.6)
    # ---- the lid closes like a slow exhale: a falling breath of filtered noise + a last soft knock
    d=T_SHUT[1]-T_SHUT[0]; env=np.clip(np.minimum(t-T_SHUT[0],T_SHUT[1]-t)/(d*0.5),0,1)*((t>=T_SHUT[0])&(t<T_SHUT[1]))
    FX+=s.filt(s.rng.normal(0,1,n),lo=150,hi=1000)*0.045*env; creak(T_SHUT[0],d,0.03,seed=90,f0=130,rev=True); nb(T_SHUT[1]-0.05,0.3,60,350,0.04,91)
    # ---- voice
    NB=np.zeros(n); wins=[]
    for k_,t0 in LINES:
        a,ar=_sf.read(os.path.join(TTS_DIR,'mm',f'{k_}.wav')); a=a if a.ndim==1 else a.mean(1)
        a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a); put(NB,a,t0); wins.append((t0,t0+len(a)/sr))
    g=duck_envelope(n,sr,wins,-6.0,0.05,0.25); bed=BED*g; fx=FX*(0.55+0.45*g)
    L=bed+fx; R_=np.roll(bed,700)+np.roll(fx,200); pk=max(np.abs(L).max(),np.abs(R_).max()); gv=pk*1.6/np.abs(NB).max()
    s.L=L+NB*gv; s.R=R_+NB*gv; s.reverb(0.16,length=1.5,decay=3.0)
    end=np.clip((DUR-t)/0.6,0,1); s.L*=end; s.R*=end
    return s.save(path,peak=0.9)
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'mimic.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'mm_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.96,vignette=0.3,grain=1.5,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(frame_final(f/FPS),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
