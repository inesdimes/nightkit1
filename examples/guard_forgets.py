"""GUARD FORGETS - "Why do game guards forget you so fast?"  PS1 stealth comedy short, 9:16. Fully procedural (nightkit).
Experiment A = 30 s cut (this file). Also the LOCKED ASSET SOURCE for Experiment B (60 s): thief(), guard(), note(), cuffs(),
crown(), the castle corridor, the alert/memory meter, emotes, the mission-complete banner, hook_shot()/HOOK_* (0-3.3 s)
and the punchline (self-arrest -> crown -> STEALTH MISSION COMPLETE). All written text is a 2D/texture layer, never geometry.
Voices: python tools/tts/gf.py -> $TTS_DIR/gf/*.wav
Run: TEST=0.5,5,12 python examples/guard_forgets.py -> test.png | PART=a:b | PART=audio | QA: python tools/qa/scene_qa.py examples/guard_forgets.py"""
import os, sys, math, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, quad
from nightkit import post, font
from nightkit.zraster import zrender
from nightkit.audio import Sound
import final_boss as FB                                   # shared geometry helpers (box/seg/limb/xform)
box,seg,xform,limb=FB.box,FB.seg,FB.xform,FB.limb
sm,seg01,lerp,lerp3,PI,Ry,Rx=FB.sm,FB.seg01,FB.lerp,FB.lerp3,FB.PI,FB.Ry,FB.Rx
def Rz(a): c,s=math.cos(a),math.sin(a); return np.array([[c,-s,0],[s,c,0],[0,0,1]])
TTS_DIR=FB.TTS_DIR; OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6
SCR=json.load(open(os.path.join(TTS_DIR,'gf','script.json')))
for ch,rows in {'!':['00100','00100','00100','00100','00100','00000','00100'],'?':['01110','10001','00001','00110','00100','00000','00100']}.items(): font.FONT.setdefault(ch,rows)

# ======================= palette =======================
CLOAK=(44,40,60); CLOAK_D=(32,29,44); HOODF=(14,12,20); TEYE=(255,236,150); TLEG=(52,50,62); BOOT=(112,72,40); POUCH=(126,86,46); BELT=(84,56,32)
ARMOR=(186,38,36); ARMOR_D=(146,28,28); SILVER=(196,200,210); SILVER_D=(140,144,156); FACE=(232,190,156); GLOVE=(120,78,42); MAIL=(128,128,138); GBOOT=(70,46,30)
STONE=(80,78,92); STONE_D=(64,62,76); FLOOR1=(76,74,86); FLOOR2=(64,62,74); RUG=(120,24,34); GOLDC=(250,206,60); VELVET=(110,30,140)
PAPER=(236,226,190); INK=(40,26,20)
WHT=(242,238,226); YEL=(255,210,60); RED=(232,44,40); GRN=(120,230,90); BLU=(110,170,255); GRY=(150,150,160)

# ======================= LOCKED ASSET: the thief =======================
def thief(base,yaw,walk=0.0,run=0.0,lean=0.0,rh=None,lh=None,crouch=0.0,peek=0.0,head=0.0,tiptoe=0.0,crown_on=False):
    """slim, short dark hooded cloak, brown boots, small belt pouch. local forward +z, ~1.55 m. peek: leans sideways (+ = to his left)."""
    b=np.array(base,float); Rb=Ry(yaw)
    def Wd(p): return tuple(b+Rb@np.array(p,float))
    hip=0.78-0.22*crouch
    def T(p):
        p=np.array(p,float)+np.array([0,hip-0.78,0]); piv=np.array([0,hip,0])
        return Wd(piv+Rz(-0.35*peek)@Rx(lean+0.22*run+0.25*crouch)@(p-piv))
    Q=[]; amp=0.45+0.35*run+0.15*tiptoe; sw=amp*math.sin(walk)
    for sx,ph in ((-1,1),(1,-1)):
        hp=np.array([sx*0.08,hip,0]); a=ph*sw
        if crouch>0.5: ft=np.array([sx*0.12,0.06,0.18*ph*math.sin(walk)]); bend=(0,0.3,1)
        else:
            ft=hp+np.array([0,-0.76*math.cos(a),0.76*math.sin(a)]); ft[1]=max(0.06,ft[1]+(0.1+0.1*tiptoe)*max(0,math.sin(walk*ph+PI/2))*(1 if walk else 0)); bend=(0,0,1)
        lq,_=limb(hp,ft,bend,0.8,0.11,TLEG,TLEG,0.1); Q+=xform(lq,Wd)
        Q+=box(ft[0]-0.065,ft[0]+0.065,ft[1]-0.06,ft[1]+0.12,ft[2]-0.07,ft[2]+0.12,BOOT,xf=Wd)                       # boots
    Q+=box(-0.14,0.14,0.76,1.2,-0.09,0.09,TLEG,xf=T)
    Q+=box(-0.15,0.15,0.78,0.84,-0.1,0.1,BELT,xf=T)+box(0.1,0.2,0.7,0.84,0.02,0.13,POUCH,xf=T)                    # belt + pouch
    Q+=box(-0.2,0.2,0.92,1.24,-0.13,0.11,CLOAK,xf=T)+box(-0.18,0.18,0.82,0.94,-0.14,-0.06,CLOAK_D,xf=T)        # short cloak
    hy=1.24; Rh=Ry(head)
    def Hh(p): p=np.array(p,float); return T(np.array([0,hy,0])+Rh@(p-np.array([0,hy,0])))
    Q+=box(-0.14,0.14,1.24,1.52,-0.15,0.12,CLOAK,xf=Hh)+box(-0.06,0.06,1.46,1.56,-0.2,-0.08,CLOAK_D,xf=Hh)    # hood
    Q+=box(-0.1,0.1,1.27,1.45,0.12,0.125,HOODF,xf=Hh)                                                          # shadowed face
    for sx in (-1,1): Q+=box(sx*0.025,sx*0.075,1.37,1.405,0.125,0.13,TEYE,xf=Hh,emit=True)                    # glinting eyes
    if crown_on: Q+=crown_quads(Hh((0,1.56,-0.03)),yaw+head,0.85)
    sh={-1:np.array([-0.19,1.17,0]),1:np.array([0.19,1.17,0])}
    idle={-1:np.array([-0.22,0.82,0.05]),1:np.array([0.22,0.82,0.05])}
    if run: idle={-1:np.array([-0.2,0.95,-0.18*math.sin(walk)]),1:np.array([0.2,0.95,0.18*math.sin(walk)])}
    if tiptoe: idle={-1:np.array([-0.22,1.05,0.22]),1:np.array([0.22,1.05,0.22])}                              # cartoon sneak hands
    hand={-1:np.array(lh,float) if lh is not None else idle[-1],1:np.array(rh,float) if rh is not None else idle[1]}
    for sx in (-1,1):
        aq,_=limb(sh[sx],hand[sx],(sx*0.5,-0.4,-0.6),0.58,0.08,CLOAK,TLEG,0.07); Q+=xform(aq,T)
        hp=hand[sx]; Q+=box(hp[0]-0.045,hp[0]+0.045,hp[1]-0.045,hp[1]+0.045,hp[2]-0.045,hp[2]+0.045,TLEG,xf=T)
    return Q
def thief_point(st,p):
    """world position of a point given in the thief's torso space (hands etc.)"""
    b=np.array(st['base'],float); hip=0.78-0.22*st.get('crouch',0.0); q=np.array(p,float)+np.array([0,hip-0.78,0]); piv=np.array([0,hip,0])
    return tuple(b+Ry(st['yaw'])@(piv+Rz(-0.35*st.get('peek',0.0))@Rx(st.get('lean',0.0)+0.22*st.get('run',0.0)+0.25*st.get('crouch',0.0))@(q-piv)))
def thief_hand(st,side=1):
    h=st.get('rh' if side>0 else 'lh')
    if h is None: h=(0.22*side,1.05,0.22) if st.get('tiptoe') else (0.22*side,0.82,0.05)
    return thief_point(st,h)

# ======================= LOCKED ASSET: the guard =======================
def guard(base,yaw,walk=0.0,run=0.0,lean=0.0,rh=None,lh=None,head=0.0,pitch=0.0,look=(0.0,0.0),wide=0.0,mouth=0.0,cuffs='belt',relax=0.0):
    """red armour, big silver helmet with an open face, big exaggerated eyes, brown gloves, handcuffs on the belt.
    local forward +z, ~1.85 m. look: pupils (x,y in -1..1). wide: eyes pop. cuffs: 'belt' | 'hand' | 'wrists' | None."""
    b=np.array(base,float); Rb=Ry(yaw)
    def Wd(p): return tuple(b+Rb@np.array(p,float))
    hip=0.86
    def T(p): p=np.array(p,float); piv=np.array([0,hip,0]); return Wd(piv+Rx(lean+0.2*run-0.06*relax)@(p-piv))
    Q=[]; amp=0.45+0.35*run; sw=amp*math.sin(walk)
    for sx,ph in ((-1,1),(1,-1)):
        hp=np.array([sx*0.12,hip,0]); a=ph*sw; ft=hp+np.array([0,-0.82*math.cos(a),0.82*math.sin(a)]); ft[1]=max(0.07,ft[1]+0.08*max(0,math.sin(walk*ph+PI/2))*(1 if walk else 0))
        lq,_=limb(hp,ft,(0,0,1),0.88,0.16,MAIL,MAIL,0.15); Q+=xform(lq,Wd)
        Q+=box(ft[0]-0.08,ft[0]+0.08,ft[1]-0.07,ft[1]+0.1,ft[2]-0.08,ft[2]+0.17,GBOOT,xf=Wd)
    Q+=box(-0.26,0.26,0.84,1.44,-0.16,0.16,ARMOR,xf=T)+box(-0.2,0.2,0.98,1.36,0.16,0.19,ARMOR_D,xf=T)             # red breastplate
    Q+=box(-0.27,0.27,0.84,0.93,-0.17,0.17,BELT,xf=T)+box(-0.05,0.05,0.85,0.92,0.17,0.19,SILVER,xf=T)
    for sx in (-1,1): Q+=box(sx*0.24,sx*0.42,1.3,1.48,-0.18,0.18,SILVER,xf=T)                                   # pauldrons
    if cuffs=='belt':
        for k in (-1,1): Q+=box(0.27,0.3,0.78+0.0*k,0.86,0.02+0.05*k-0.025,0.02+0.05*k+0.025,SILVER,xf=T)        # cuffs hanging on the belt
    hy=1.46; Rh=Ry(head)@Rx(pitch)
    def Hh(p): p=np.array(p,float); return T(np.array([0,hy,0])+Rh@(p-np.array([0,hy,0])))
    Q+=box(-0.22,0.22,1.44,1.92,-0.22,0.2,SILVER,xf=Hh)+box(-0.24,0.24,1.44,1.5,-0.24,0.22,SILVER_D,xf=Hh)        # big helmet + rim
    Q+=box(-0.03,0.03,1.92,2.02,-0.2,0.16,SILVER_D,xf=Hh)                                                            # crest
    Q+=box(-0.16,0.16,1.5,1.78,0.195,0.205,FACE,xf=Hh)                                                               # open face
    ew=0.06+0.015*wide
    for sx in (-1,1):
        cx=sx*0.075; Q+=box(cx-ew,cx+ew,1.62-0.01*wide,1.75+0.02*wide,0.205,0.21,WHT,xf=Hh,emit=True)
        px,py=cx+0.03*look[0],1.68+0.03*look[1]; Q+=box(px-0.025,px+0.025,py-0.03,py+0.03,0.21,0.215,(20,16,14),xf=Hh,emit=True)
    Q+=box(-0.025,0.025,1.58,1.64,0.205,0.24,(214,160,128),xf=Hh)                                                     # nose
    Q+=box(-0.09,0.09,1.535+0.0*mouth,1.56,0.205,0.22,(96,60,36),xf=Hh)                                               # moustache
    if mouth>0.05: Q+=box(-0.05,0.05,1.505-0.03*mouth,1.53,0.205,0.212,(60,20,16),xf=Hh)
    sh={-1:np.array([-0.32,1.36,0]),1:np.array([0.32,1.36,0])}
    idle={-1:np.array([-0.32,0.9+0.06*relax,0.06]),1:np.array([0.32,0.9+0.06*relax,0.06])}
    if run: idle={-1:np.array([-0.3,1.0,-0.2*math.sin(walk)]),1:np.array([0.3,1.0,0.2*math.sin(walk)])}
    hand={-1:np.array(lh,float) if lh is not None else idle[-1],1:np.array(rh,float) if rh is not None else idle[1]}
    for sx in (-1,1):
        aq,_=limb(sh[sx],hand[sx],(sx*0.5,-0.4,-0.6),0.64,0.14,ARMOR,MAIL,0.12); Q+=xform(aq,T)
        hp=hand[sx]; Q+=box(hp[0]-0.06,hp[0]+0.06,hp[1]-0.06,hp[1]+0.06,hp[2]-0.06,hp[2]+0.06,GLOVE,xf=T)
    return Q
def guard_point(st,p):
    b=np.array(st['base'],float); piv=np.array([0,0.86,0]); q=np.array(p,float)
    return tuple(b+Ry(st['yaw'])@(piv+Rx(st.get('lean',0.0)+0.2*st.get('run',0.0)-0.06*st.get('relax',0.0))@(q-piv)))
def guard_hand(st,side=1):
    h=st.get('rh' if side>0 else 'lh')
    if h is None: h=(0.32*side,0.9+0.06*st.get('relax',0.0),0.06)
    return guard_point(st,h)
NOTE_ON_CHEST=(0.0,1.2,0.205)                     # pinned note, guard torso space

# ======================= LOCKED ASSET: props =======================
def crown_quads(c,yaw,s=1.0):
    c=np.array(c,float); Rb=Ry(yaw)
    def Wd(p): return tuple(c+Rb@(np.array(p,float)*s))
    Q=box(-0.15,0.15,0.0,0.08,-0.15,0.15,GOLDC,xf=Wd,emit=True)
    for k in range(5):
        a=k*2*PI/5; x,z=0.12*math.sin(a),0.12*math.cos(a); Q+=box(x-0.03,x+0.03,0.08,0.18,z-0.03,z+0.03,GOLDC,xf=Wd,emit=True)
    Q+=box(-0.03,0.03,0.03,0.06,0.15,0.17,(220,40,60),xf=Wd,emit=True)+box(-0.03,0.03,0.03,0.06,-0.17,-0.15,(60,120,240),xf=Wd,emit=True)
    return Q
def cuffs_quads(p1,p2):
    """handcuffs: two rings + chain between p1 and p2"""
    Q=[]
    for p in (p1,p2): x,y,z=p; Q+=box(x-0.055,x+0.055,y-0.025,y+0.025,z-0.055,z+0.055,SILVER,emit=False)
    Q+=seg(p1,p2,0.02,SILVER_D,0.02); return Q
def note_quad(center,right,up,w=0.26,h=0.18):
    c=np.array(center,float); r=np.array(right,float)*w/2; u=np.array(up,float)*h/2
    TL,TR,BR,BL=c-r+u,c+r+u,c+r-u,c-r-u
    return [quad([tuple(TL),tuple(TR),tuple(BR),tuple(BL)],PAPER)],(TL,TR,BR,BL)

# ======================= LOCKED ASSET: the castle corridor =======================
HALL_X=3.6; Z0=-3.0; Z1=22.0
PILLARS=[(sx*1.8,z) for z in (1.0,4.0,7.0,10.0,13.0,16.0,19.0) for sx in (-1,1)]
HERO_PILLAR=(1.8,4.0); PH=0.34                    # half-size of a pillar
HIDE=(2.42,4.0)                                    # the thief's hiding spot behind the hero pillar (seen by the camera, not by the guard)
PEDESTAL=(0.0,8.6)                                # crown display
def hall_static():
    Q=[]
    xs=list(np.arange(-HALL_X,HALL_X+0.01,1.2)); zs=list(np.arange(Z0,Z1+0.01,1.0))
    for i in range(len(xs)-1):
        for j in range(len(zs)-1):
            Q.append(quad([(xs[i],0,zs[j]),(xs[i+1],0,zs[j]),(xs[i+1],0,zs[j+1]),(xs[i],0,zs[j+1])],FLOOR1 if (i+j)%2 else FLOOR2))
    Q+=[quad([(-0.7,0.01,Z0),(0.7,0.01,Z0),(0.7,0.01,PEDESTAL[1]-0.7),(-0.7,0.01,PEDESTAL[1]-0.7)],RUG)]
    for sx in (-1,1):
        x=sx*HALL_X
        for j in range(len(zs)-1):
            for k,(y0,y1) in enumerate(((0,1.3),(1.3,2.6),(2.6,3.9))):
                pts=[(x,y0,zs[j]),(x,y0,zs[j+1]),(x,y1,zs[j+1]),(x,y1,zs[j])]; Q.append(quad(pts if sx<0 else pts[::-1],STONE if (j+k)%2 else STONE_D))
    Q+=[quad([(-HALL_X,3.9,Z0),(HALL_X,3.9,Z0),(HALL_X,3.9,Z1),(-HALL_X,3.9,Z1)],(40,36,44))]
    for x,z in PILLARS:
        Q+=box(x-PH,x+PH,0,3.9,z-PH,z+PH,STONE)+box(x-PH-0.08,x+PH+0.08,0,0.3,z-PH-0.08,z+PH+0.08,STONE_D)+box(x-PH-0.06,x+PH+0.06,3.4,3.6,z-PH-0.06,z+PH+0.06,STONE_D)
    px,pz=PEDESTAL                                                                                       # the crown display
    Q+=box(px-0.35,px+0.35,0,0.95,pz-0.35,pz+0.35,STONE_D)+box(px-0.42,px+0.42,0.95,1.05,pz-0.42,pz+0.42,STONE)+box(px-0.22,px+0.22,1.05,1.15,pz-0.22,pz+0.22,VELVET)
    Q+=box(-HALL_X,HALL_X,0,3.9,Z1,Z1+0.2,STONE_D)
    for sx in (-1,1):                                                                                    # banners
        for z in (2.5,8.5,14.5):
            x=sx*(HALL_X-0.02); pts=[(x,3.2,z-0.4),(x,3.2,z+0.4),(x,1.7,z+0.4),(x,1.9,z),(x,1.7,z-0.4)]
            Q.append(quad(pts[:4] if sx<0 else pts[:4][::-1],(150,26,36)))
    return Q
HALL=hall_static()
TORCH_Z=[2.5,5.5,8.5,11.5,14.5,17.5]
def torches(t):
    Q=[]
    for k,z in enumerate(TORCH_Z):
        for sx in (-1,1):
            x=sx*(HALL_X-0.08); fl=0.06*math.sin(t*13+k*2.1+sx)
            Q+=box(x-0.05,x+0.05,2.0,2.35,z-0.05,z+0.05,(60,50,40))+box(x-0.1,x+0.1,2.37,2.58+fl,z-0.1,z+0.1,(255,120,40),emit=True)+box(x-0.05,x+0.05,2.47,2.68+fl,z-0.05,z+0.05,(255,214,90),emit=True)
    return Q
def lights(t):
    L=[((sx*(HALL_X-0.5),2.5,z),(255,170,100),0.95+0.1*math.sin(t*11+k+sx)) for k,z in enumerate(TORCH_Z[:4]) for sx in (-1,1)]
    L.append(((0,3.0,PEDESTAL[1]),(255,230,160),1.6))                                                    # spotlight on the crown
    return L

# ======================= STORY TIMELINE =======================
DUR=30.6; N=int(round(DUR*FPS)); HOOK_DUR=3.3
VOICE=[('N1',0.08),('G1',6.35),('G2',9.6),('G3',16.75),('G4',24.85)]
GSPOT=(0.35,0,3.55)                                # where the guard ends up standing (facing the camera, -z)
SPOT1=(0.95,0,4.6)                                 # the exploit: the thief walks right behind the guard
SPOT_SWAP=(0.9,0,3.05)                            # beside the guard, reaching round to his chest
# alert / memory meter: (start, end, label) - counts 10 -> 0
METERS=[(3.5,6.15,'ALERT'),(10.9,12.7,'ALERT'),(18.6,23.8,'MEMORY')]
ALERTS=[0.0,9.5]                                   # '!' moments (full red meter)
CUFF=(25.75,26.9); CROWN_TAKE=28.85; NOTE_SWAP=(20.35,21.95)
MISSION=29.55
def meter_value(t):
    for a,b,lab in METERS:
        if a<=t<b: return lab,10.0*(1-seg01(t,a,b))
    for a in ALERTS:
        if a<=t<a+1.1 or (a==0.0 and t<3.25): return 'ALERT',10.0
    if 9.5<=t<10.9: return 'ALERT',10.0
    if 16.6<=t<18.6: return 'MEMORY',10.0
    return None,0.0

def thief_state(t):
    st=_thief_state(t)
    if st.get('walk') and math.hypot(st['base'][0]-HIDE[0],st['base'][2]-HIDE[1])<0.32: st=dict(st,walk=0.0)
    return st
def _thief_state(t):
    hx,hz=HIDE
    if t<1.35:                                     # HOOK: running from the guard toward the camera, then ducks behind the pillar
        P=[(0.4,0,7.4),(0.9,0,6.0),(2.64,0,5.0),(2.7,0,4.2),(2.7,0,4.0),HIDE3]; u=seg01(t,0.0,1.35); slow=1-seg01(t,1.15,1.35)
        return dict(base=tuple(path3(P,u)),yaw=alerp(path_yaw(P,u),PI/2,sm(seg01(t,1.1,1.35))),walk=t*15,run=slow)
    if t<7.0:                                      # hides flat against the pillar (back to it), breathing
        return dict(base=(hx,0,hz),yaw=PI/2,lean=-0.05,crouch=0.15+0.05*math.sin(t*5),rh=(0.2,1.0,-0.05),lh=(-0.2,1.0,-0.05))
    if t<8.0:                                      # peeks out round the pillar's edge
        p=sm(seg01(t,7.0,7.35))*(1-sm(seg01(t,7.7,8.0)))
        return dict(base=(hx,0,lerp(hz,hz-0.3,p)),yaw=PI/2,peek=-0.8*p,crouch=0.2,head=-0.6*p)
    if t<9.3:                                      # tiptoes right behind the guard
        P=[HIDE3,(2.72,0,4.0),(2.72,0,4.65),(2.0,0,5.05),SPOT1]; u=seg01(t,8.0,9.25)
        return dict(base=tuple(path3(P,u)),yaw=alerp(PI/2,path_yaw(P,u),sm(seg01(t,8.0,8.3))),walk=t*9.0,tiptoe=1.0,crouch=0.1)
    if t<9.85:                                     # frozen mid-step when the guard turns
        return dict(base=SPOT1,yaw=path_yaw([HIDE3,(2.72,0,4.0),(2.72,0,4.65),(2.0,0,5.05),SPOT1],1.0),tiptoe=1.0,walk=0.0,crouch=0.1)
    if t<10.6:                                     # dashes back behind the pillar
        P=[SPOT1,(2.0,0,5.05),(2.72,0,4.65),(2.72,0,4.0),HIDE3]; u=seg01(t,9.85,10.5); y0=path_yaw([HIDE3,(2.72,0,4.0),(2.72,0,4.65),(2.0,0,5.05),SPOT1],1.0)
        yw=y0+PI*sm(seg01(t,9.85,10.15)) if t<10.15 else alerp(y0+PI,path_yaw(P,u),sm(seg01(t,10.15,10.3)))
        return dict(base=tuple(path3(P,u)),yaw=alerp(yw,PI/2,sm(seg01(t,10.25,10.55))),walk=t*16 if u<1 else 0.0,run=1.0 if u<1 else 0.0)
    if t<19.0:
        sneak=0.0 if t<17.5 else 0.0
        return dict(base=(hx,0,hz),yaw=PI/2,crouch=0.18+0.04*math.sin(t*5),peek=(-0.6*sm(seg01(t,14.2,14.6))*(1-sm(seg01(t,17.0,17.4)))),rh=(0.2,1.0,-0.05),lh=(-0.2,1.0,-0.05))
    if t<NOTE_SWAP[0]:                             # sneaks up beside the guard
        P=[HIDE3,(2.72,0,4.0),(2.72,0,3.35),(1.95,0,3.0),SPOT_SWAP]; u=seg01(t,19.0,20.2)
        return dict(base=tuple(path3(P,u)),yaw=alerp(alerp(PI/2,path_yaw(P,u),sm(seg01(t,19.0,19.3))),SWAP_YAW,sm(seg01(t,19.95,20.3))),walk=t*9.0 if u<1 else 0.0,tiptoe=1.0)
    if t<22.0:                                     # the swap (hands driven by the note path)
        return dict(base=SPOT_SWAP,yaw=SWAP_YAW,lean=0.25,rh=swap_hand_local(t),lh=(-0.2,0.86,0.12))
    if t<23.0:                                     # tiptoes back behind the pillar
        P=[SPOT_SWAP,(1.95,0,3.0),(2.72,0,3.35),(2.72,0,4.0),HIDE3]; u=seg01(t,22.0,22.85)
        return dict(base=tuple(path3(P,u)),yaw=alerp(alerp(alerp(SWAP_YAW,path_yaw(P,0.35),sm(seg01(t,22.0,22.3))),path_yaw(P,min(u,0.8)),sm(seg01(t,22.3,22.45))),PI/2,sm(seg01(t,22.55,22.95))),walk=t*9.0 if u<1 else 0.0,tiptoe=1.0)
    if t<CUFF[1]+0.15:                             # watches from the pillar
        return dict(base=(hx,0,hz),yaw=PI/2,peek=-0.7*sm(seg01(t,24.0,24.4)),crouch=0.15,head=-0.5*sm(seg01(t,24.0,24.4)))
    # takes the crown (only after the guard is cuffed) and strolls away wearing it
    if t<CROWN_TAKE-0.25:
        P=[HIDE3,(2.72,0,4.0),(2.72,0,5.0),(1.0,0,5.9),CROWN_STAND]; u=seg01(t,CUFF[1]+0.15,CROWN_TAKE-0.3)
        return dict(base=tuple(path3(P,u)),yaw=alerp(alerp(PI/2,path_yaw(P,u),sm(seg01(t,CUFF[1]+0.15,CUFF[1]+0.4))),0.0,sm(seg01(t,CROWN_TAKE-0.55,CROWN_TAKE-0.3))),walk=t*13 if u<0.93 else 0.0,run=0.7 if u<0.9 else 0.0)
    if t<CROWN_TAKE+0.6:
        l=sm(seg01(t,CROWN_TAKE-0.25,CROWN_TAKE)); on=sm(seg01(t,CROWN_TAKE+0.25,CROWN_TAKE+0.55)); lean=0.4*l*(1-on)
        st=dict(base=CROWN_STAND,yaw=0.0,lean=lean)
        grip={sx:world_to_thief_local(st,(PEDESTAL[0]+sx*0.13,1.2,PEDESTAL[1])) for sx in (-1,1)}
        lift=sm(seg01(t,CROWN_TAKE+0.02,CROWN_TAKE+0.25)); grip={sx:tuple(np.array(g)+np.array([0,0.15*lift,-0.2*lift])) for sx,g in grip.items()}
        return dict(base=CROWN_STAND,yaw=0.0,lean=lean,rh=lerp3(reach2((0.22,0.82,0.05),(0.2,1.3,0.25),grip[1],l),(0.1,1.6,0.05),on),lh=lerp3(reach2((-0.22,0.82,0.05),(-0.2,1.3,0.25),grip[-1],l),(-0.1,1.6,0.05),on))
    u=seg01(t,CROWN_TAKE+0.6,DUR+0.6)
    P=[CROWN_STAND,(-0.9,0,7.3),(-1.0,0,3.0)]
    return dict(base=tuple(path3(P,u)),yaw=alerp(0.0,path_yaw(P,u),sm(seg01(t,CROWN_TAKE+0.6,CROWN_TAKE+0.95))),walk=t*8,crown_on=True)
HIDE3=(HIDE[0],0,HIDE[1]); CROWN_STAND=(0.0,0,PEDESTAL[1]-0.7)
def alerp(a,b,u):
    """angle lerp along the short way round"""
    d=(b-a+math.pi)%(2*math.pi)-math.pi; return a+d*u
def reach2(a,mid,b,u):
    """hand path: up over an obstacle edge first, then to the target"""
    return lerp3(a,mid,sm(seg01(u,0,0.5))) if u<0.5 else lerp3(mid,b,sm(seg01(u,0.5,1)))
def path_yaw(P,u,w=0.08):
    """facing direction along a path (central difference: corners turn smoothly)"""
    a=path3(P,u-w); b=path3(P,u+w); d=b-a; return math.atan2(d[0],d[2])
def path3(P,u):
    P=[np.array(p,float) for p in P]; L=[np.linalg.norm(b-a) for a,b in zip(P,P[1:])]; d=max(0.0,min(1.0,u))*sum(L)
    for a,b,l in zip(P,P[1:],L):
        if d<=l: return a+(b-a)*(d/l if l>0 else 0)
        d-=l
    return P[-1]

def guard_state(t):
    gx,_,gz=GSPOT
    if t<1.9:                                      # HOOK: chasing (2 m behind), then skids to a stop
        u=seg01(t,0.0,1.9); z=lerp(9.4,gz,u**1.15)
        return dict(base=(lerp(0.95,gx,u),0,z),yaw=PI,walk=t*14,run=1.0 if t<1.6 else 1.0-seg01(t,1.6,1.9),mouth=0.6,wide=0.6)
    if t<3.3:                                      # looks left, right... confused
        h=0.7*math.sin(PI*seg01(t,1.95,2.6))-0.6*math.sin(PI*seg01(t,2.55,3.2))
        return dict(base=GSPOT,yaw=PI,head=h,look=(1.0 if h>0 else -1.0,0.0),wide=0.8)
    if t<9.35:                                     # memory runs out; relaxes; "Must've been the wind."
        r=sm(seg01(t,5.8,6.3))
        return dict(base=GSPOT,yaw=PI,relax=r,look=(0.0,0.6*r),wide=0.3*(1-r),mouth=talk('G1',t),head=0.15*math.sin(t*1.3)*r)
    if t<10.9:                                     # turns, spots the thief: HEY! STOP!
        tu=sm(seg01(t,9.35,9.6)); return dict(base=GSPOT,yaw=lerp(PI,0.5,tu),wide=1.0,mouth=talk('G2',t),rh=(0.3,1.35,0.5) if t>9.65 else None)
    if t<13.0:                                     # stares at the pillar while the meter runs out, then turns back
        back=sm(seg01(t,12.4,12.9)); return dict(base=GSPOT,yaw=lerp(0.5,PI,back),wide=0.6*(1-back),look=(0.4*(1-back),0.0),relax=back*0.6)
    if t<14.0:                                     # something is wrong... scratches his helmet
        s_=sm(seg01(t,13.05,13.3))*(1-sm(seg01(t,13.75,13.95)))
        return dict(base=GSPOT,yaw=PI,rh=(0.18,lerp(0.9,1.86,s_),lerp(0.06,0.1,s_)) if s_>0.02 else None,look=(0.0,0.8),head=0.12*s_)
    if t<16.05:                                    # pulls out paper + quill, writes
        tk=sm(seg01(t,14.0,14.4)); wr=seg01(t,14.55,15.95)
        lh=lerp3((-0.32,0.9,0.06),NOTE_HELD,tk); rh=lerp3((0.32,0.9,0.06),(0.05+0.12*wr,1.12+0.012*math.sin(t*40),0.4),tk)
        return dict(base=GSPOT,yaw=PI,lh=lh,rh=rh,pitch=0.35*tk,look=(0.0,-1.0))
    if t<16.7:                                     # pins it on his chest
        p=sm(seg01(t,16.05,16.5)); return dict(base=GSPOT,yaw=PI,lh=lerp3(NOTE_HELD,(-0.12,1.2,0.25),p),rh=lerp3((0.17,1.12,0.4),(0.12,1.2,0.25),p),pitch=0.35*(1-p),look=(0.0,-0.6))
    if t<19.0:                                     # proud: "Now I won't forget!" - taps the note
        tap=0.05*abs(math.sin(PI*seg01(t,17.0,17.8)*2))
        return dict(base=GSPOT,yaw=PI,rh=(0.1,1.22,0.27+tap) if t<18.0 else None,mouth=talk('G3',t),lean=-0.06,wide=0.2)
    if t<24.0:                                     # humming, staring at the ceiling (doesn't notice the swap)
        return dict(base=GSPOT,yaw=PI,look=(0.3*math.sin(t*0.9),1.0),head=0.1*math.sin(t*0.9),relax=1.0,mouth=0.15*(1+math.sin(t*6)))
    if t<CUFF[0]:                                  # memory empty -> reads his note: "I'M THE THIEF?!"
        rd=sm(seg01(t,24.0,24.35)); shock=sm(seg01(t,24.85,25.0))
        return dict(base=GSPOT,yaw=PI,pitch=0.45*rd*(1-shock*0.6),look=(0.0,-1.0+shock),wide=shock,mouth=talk('G4',t))
    if t<CUFF[1]:                                  # takes the cuffs off his belt and cuffs his own wrists
        g=sm(seg01(t,CUFF[0],CUFF[0]+0.3)); tog=sm(seg01(t,CUFF[0]+0.35,CUFF[0]+0.75))
        rh=lerp3(lerp3((0.32,0.9,0.06),(0.3,0.86,0.08),g),(0.06,1.0,0.32),tog); lh=lerp3((-0.32,0.9,0.06),(-0.06,1.0,0.32),tog)
        return dict(base=GSPOT,yaw=PI,rh=rh,lh=lh,pitch=0.3*tog,look=(0.0,-1.0),cuffs='hand' if t<CUFF[0]+0.8 else 'wrists')
    return dict(base=GSPOT,yaw=PI,rh=(0.06,1.0,0.32),lh=(-0.06,1.0,0.32),cuffs='wrists',look=(0.0,-0.3),wide=0.3,head=0.08*math.sin(t*2))
NOTE_HELD=(-0.02,1.12,0.42)
def talk(k,t):
    t0=dict(VOICE)[k]; return (0.5+0.5*math.sin(t*24))*(1 if t0<=t<t0+SCR['dur'][k] else 0)

# ---- the notes (written text is a texture layer) ----
OLD,NEW='ARREST THE THIEF!','YOU ARE THE THIEF!'
def swap_hand_local(t):
    """thief right hand (torso space) during the swap: reach chest -> pouch -> chest"""
    gs=guard_state(t); chest=np.array(guard_point(gs,NOTE_ON_CHEST))+Ry(gs['yaw'])@np.array([0,0,0.05])
    ts=thief_state_static(); pouch=np.array(thief_point(ts,(0.16,0.8,0.14)))
    a,b=NOTE_SWAP; k=[(a,'rest'),(a+0.35,'chest'),(a+0.6,'chest'),(a+0.95,'pouch'),(a+1.15,'pouch'),(b-0.15,'chest'),(b,'chest')]
    pos={'rest':np.array(thief_point(ts,(0.22,0.82,0.05))),'chest':chest,'pouch':pouch}
    for (t0,p0),(t1,p1) in zip(k,k[1:]):
        if t<=t1: w=np.array(pos[p0])+(np.array(pos[p1])-np.array(pos[p0]))*sm(seg01(t,t0,t1)); break
    else: w=chest
    return tuple(Ry(-ts['yaw'])@(w-np.array(ts['base']))-np.array([0,0,0])) if False else world_to_thief_local(ts,w)
SWAP_YAW=math.atan2(GSPOT[0]-SPOT_SWAP[0],GSPOT[2]-0.205-SPOT_SWAP[2])
def thief_state_static(): return dict(base=SPOT_SWAP,yaw=SWAP_YAW,lean=0.25)
def world_to_thief_local(st,w):
    b=np.array(st['base'],float); piv=np.array([0,0.78,0]); p=Ry(-st['yaw'])@(np.array(w,float)-b)
    return tuple(piv+Rx(-st.get('lean',0.0))@(p-piv))
def notes(t,gs,ts):
    """[(text, center, right, up, chars_shown)] for every note that exists at time t"""
    out=[]; a,b=NOTE_SWAP
    def on_chest(st):
        R_=Ry(st['yaw']); c=np.array(guard_point(st,NOTE_ON_CHEST))+R_@np.array([0,0,0.012]); return c,R_@np.array([-1.0,0,0]),R_@np.array([0,1.0,0])
    if 14.0<=t<16.05:                                                         # in the guard's hand while writing (faces up toward him)
        R_=Ry(gs['yaw']); c=np.array(guard_hand(gs,-1))+R_@np.array([0.12,0.03,0.05])
        out.append((OLD,c,R_@np.array([1.0,0,0]),R_@np.array([0,0.35,1.0])/np.linalg.norm([0,0.35,1.0]),int(len(OLD)*seg01(t,14.55,15.95)+0.5)))
    elif 16.05<=t<16.5:                                                       # carried to the chest
        p=sm(seg01(t,16.05,16.5)); R_=Ry(gs['yaw']); c0=np.array(guard_hand(guard_state(16.04),-1))+R_@np.array([0.12,0.03,0.05]); c1,r1,u1=on_chest(gs)
        u0=R_@np.array([0,0.35,1.0])/np.linalg.norm([0,0.35,1.0]); r0=R_@np.array([1.0,0,0])
        out.append((OLD,c0+(c1-c0)*p,(r0+(r1-r0)*p)/np.linalg.norm(r0+(r1-r0)*p),(u0+(u1-u0)*p)/np.linalg.norm(u0+(u1-u0)*p),len(OLD)))
    elif 16.5<=t<a+0.6: c,r,u=on_chest(gs); out.append((OLD,c,r,u,len(OLD)))
    if a+0.6<=t<a+1.0:                                                        # old note: thief's hand -> into his pouch
        c=np.array(thief_hand(ts,1)); _,r,u=on_chest(gs); sc=1-seg01(t,a+0.85,a+1.0)
        if sc>0.05: out.append((OLD,c,r*sc,u*sc,len(OLD)))
    if a+1.05<=t<b-0.15:                                                      # new note: out of the pouch -> to the chest
        c=np.array(thief_hand(ts,1)); _,r,u=on_chest(gs); sc=seg01(t,a+1.05,a+1.2); out.append((NEW,c,r*max(sc,0.05),u*max(sc,0.05),len(NEW)))
    if t>=b-0.15:                                                             # pinned on the guard
        c,r,u=on_chest(gs); out.append((NEW,c,r,u,len(NEW)))
    return out

# ======================= SHOTS =======================
def hook_shot(t):
    """0-3.3 s (shared with B): the chase comes toward the camera down the corridor, thief ducks behind the pillar"""
    u=sm(seg01(t,0,HOOK_DUR)); return dict(cam=lerp3((-0.55,1.35,1.4),(-0.45,1.4,1.7),u),tgt=lerp3((1.1,0.95,6.6),(1.2,1.0,4.6),u),fov=58)
def shot(V):
    if V<HOOK_DUR: return hook_shot(V)
    if V<8.0:  u=sm(seg01(V,3.3,8.0)); return dict(cam=lerp3((2.55,1.45,1.25),(2.5,1.5,1.45),u),tgt=(0.9,1.15,4.3),fov=62)
    if V<9.35: u=sm(seg01(V,8.0,9.35)); return dict(cam=lerp3((1.2,1.5,0.95),(1.15,1.5,1.1),u),tgt=(0.55,1.15,4.1),fov=64)
    if V<13.0: u=sm(seg01(V,9.35,13.0)); return dict(cam=lerp3((1.65,1.6,6.2),(1.6,1.6,6.0),u),tgt=(0.45,1.3,3.7),fov=60)          # side view: he turns and spots him
    if V<14.5: u=sm(seg01(V,13.0,14.5)); return dict(cam=lerp3((-0.35,1.55,2.1),(-0.3,1.55,2.2),u),tgt=(0.35,1.5,3.55),fov=60)
    if V<16.05: return dict(cam=(0.4,2.2,2.82),tgt=(0.38,1.12,2.72),fov=40)                          # insert: over his shoulder, writing the note
    if V<19.0: u=sm(seg01(V,16.05,19.0)); return dict(cam=lerp3((0.3,1.4,2.6),(0.32,1.4,2.75),u),tgt=(0.35,1.35,3.55),fov=54)
    if V<23.0: u=sm(seg01(V,19.0,23.0)); return dict(cam=lerp3((0.15,1.4,2.0),(0.2,1.38,2.15),u),tgt=(0.75,1.2,3.6),fov=62)
    if V<24.75: return dict(cam=(0.35,1.18,2.6),tgt=(0.35,1.2,3.6),fov=50)                            # insert: the new note
    if V<26.95: u=sm(seg01(V,24.75,26.95)); return dict(cam=lerp3((0.0,1.4,2.15),(0.05,1.35,2.3),u),tgt=(0.35,1.2,3.55),fov=60)
    u=sm(seg01(V,26.95,DUR)); return dict(cam=lerp3((-1.0,1.65,1.3),(-1.05,1.65,1.1),u),tgt=(0.25,1.05,7.0),fov=56)

# ======================= RENDER =======================
R=Renderer(W,H,fog=(18,14,20))
TH_KEYS={'base','yaw','walk','run','lean','rh','lh','crouch','peek','head','tiptoe','crown_on'}
GU_KEYS={'base','yaw','walk','run','lean','rh','lh','head','pitch','look','wide','mouth','cuffs','relax'}
def props(V,gs,ts):
    Q=[]
    if not ts.get('crown_on'):                                                                         # the crown: cushion -> hands -> head
        if V<CROWN_TAKE+0.02: Q+=crown_quads((PEDESTAL[0],1.15,PEDESTAL[1]),0.0)
        else:
            c=(np.array(thief_hand(ts,1))+np.array(thief_hand(ts,-1)))/2+np.array([0,-0.05,0]); Q+=crown_quads(c,0.0,1.0)
    if gs.get('cuffs')=='hand': p=np.array(guard_hand(gs,1)); Q+=cuffs_quads(tuple(p+np.array([0,-0.08,0])),tuple(p+np.array([0.05,-0.14,0.03])))
    if gs.get('cuffs')=='wrists':
        p1=np.array(guard_hand(gs,1)); p2=np.array(guard_hand(gs,-1)); d=Ry(gs['yaw'])@np.array([0,0,-0.09])
        Q+=cuffs_quads(tuple(p1+d),tuple(p2+d))
    if 14.0<=V<16.05: p=np.array(guard_hand(gs,1)); Q+=seg(p,p+np.array([-0.05,0.24,0.08]),0.025,(240,240,230),0.012)       # quill
    return Q
def render(V,sh):
    cam=Camera.look(sh['cam'],sh['tgt'])
    gs=guard_state(V); ts=thief_state(V)
    layers=[HALL,torches(V),FB.prelit(thief(**{k:v for k,v in ts.items() if k in TH_KEYS}),sh['cam'],warm=0.12),
            FB.prelit(guard(**{k:v for k,v in gs.items() if k in GU_KEYS}),sh['cam'],warm=0.12),FB.prelit(props(V,gs,ts),sh['cam'],warm=0.1)]
    NQ=notes(V,gs,ts)
    for txt,c,r,u,n in NQ: layers.append(note_quad(c,r,u)[0])
    img,vi=zrender(R,cam,layers,lights(V),fov=sh['fov'],fog_start=7,fog_end=26,ambient=0.22,shake=sh.get('shake',(0,0)))
    for txt,c,r,u,n in NQ: img=note_text(img,vi,sh['cam'],txt,c,r,u,n)
    return post.ps1(img),vi
_TXT={}
def note_text(img,vi,campos,txt,c,r,u,n,w=0.26,h=0.18):
    """written text as a texture layer on the paper (only on the side facing the camera)"""
    nrm=np.cross(u,r)                                                                         # front normal (towards a viewer who sees r to the right)
    if float(nrm@(np.array(campos)-c))<=0 or n<=0: return img
    key=(txt,n)
    if key not in _TXT:
        words=txt.split(' '); lines=[' '.join(words[:2]),' '.join(words[2:])] if len(words)>2 else [txt]
        tex=Image.new('RGB',(64,40),PAPER); d=ImageDraw.Draw(tex); left=n
        for i,ln in enumerate(lines):
            shown=ln[:max(0,left)]; left-=len(ln)+1
            font.text(d,shown,(64-font.width(ln))//2,6+i*14,(30,20,18) if txt==OLD else (170,20,20),1,None)
        _TXT[key]=tex
    rr=np.array(r)*w/2; uu=np.array(u)*h/2; P=[R.project(tuple(p),vi) for p in (c-rr+uu,c+rr+uu,c+rr-uu,c-rr-uu)]
    if not all(P): return img
    lay=img.copy(); post.map_texture(lay,[(p[0],p[1]) for p in P],_TXT[key],Image.NEAREST); return lay

# ======================= UI layers =======================
def otext(d,s,x,y,col,sc=1):
    o=max(1,sc//2)
    for ox,oy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)): font.text(d,s,x+ox*o,y+oy*o,(0,0,0),sc,None)
    font.text(d,s,x,y,col,sc,None)
HOOK_LINES=['WHY DO GUARDS','IN VIDEO GAMES','FORGET YOU','AFTER TEN','SECONDS?']
HIL={'GUARDS','FORGET','TEN','SECONDS?','WIND.','HEY!','STOP!','FORGET!',"WON'T",'THIEF?!'}
SPK={'N':(None,WHT),'G':('GUARD:',RED)}
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
        y=24
        for ln in HOOK_LINES:
            x=(W-font.width(ln,2))//2
            for wd in ln.split(' '): otext(d,wd,x,y,YEL if wd in HIL else WHT,2); x+=font.width(wd,2)+12
            y+=19
        return
    name,col=SPK[cur[0]]; txt=SCR['text'][cur].upper()
    lines=wrap(((name+' ') if name else '')+txt); y=266-11*(len(lines)-1)
    for ln in lines:
        xw=font.width(ln); x=(W-xw)//2; d.rectangle([x-3,y-2,x+xw+2,y+8],fill=(0,0,0)); cx=x
        for wd in ln.split(' '): otext(d,wd,cx,y,col if wd==name else (YEL if wd in HIL else WHT)); cx+=font.width(wd)+6
        y+=11
def meter(d,V):
    """LOCKED: the guard's alert / memory meter (top left)"""
    lab,val=meter_value(V)
    if lab is None or V<SCR['dur']['N1']+0.25: return
    x0,y0=6,8; full=val>=9.99; col=RED if full else (YEL if val>3 else GRN)
    d.rectangle([x0,y0,x0+78,y0+30],fill=(10,8,14),outline=col)
    otext(d,lab,x0+5,y0+4,WHT); num=str(int(math.ceil(val))) if not full else '!'
    otext(d,num,x0+78-6-font.width(num,2),y0+3,col,2)
    bw=int(66*val/10.0); d.rectangle([x0+5,y0+21,x0+71,y0+26],fill=(40,30,40)); d.rectangle([x0+5,y0+21,x0+5+bw,y0+26],fill=col)
def emote(d,vi,p3,ch,col=RED):
    p=R.project(tuple(p3),vi)
    if not p: return
    x,y=int(p[0]),int(p[1]); d.rectangle([x-6,y-10,x+6,y+8],fill=WHT,outline=(0,0,0)); d.polygon([(x-2,y+8),(x+2,y+8),(x,y+11)],fill=WHT)
    font.text(d,ch,x-2,y-7,col,1,None)
def emotes(d,vi,V,gs,ts):
    top=np.array(guard_point(gs,(0,2.25,0)))
    if 1.95<=V<3.3 or 12.75<=V<13.0: emote(d,vi,top,'?',BLU)
    if 9.45<=V<10.6: emote(d,vi,top,'!',RED)
    if 13.05<=V<13.95:
        p=R.project(tuple(top),vi)
        if p:
            for k in range(int(seg01(V,13.05,13.6)*3)+1): d.rectangle([int(p[0])-7+k*6,int(p[1]),int(p[0])-5+k*6,int(p[1])+2],fill=WHT)
    if 19.2<=V<24.0 and int(V*2)%2==0:                                                                  # humming
        p=R.project(tuple(top+np.array([0.2,0.05*math.sin(V*3),0])),vi)
        if p: x,y=int(p[0]),int(p[1]); d.line([x,y-6,x,y+2],fill=WHT); d.rectangle([x-3,y+1,x,y+3],fill=WHT); d.line([x,y-6,x+3,y-4],fill=WHT)
def mission(d,V):
    """LOCKED: the punchline banner"""
    if V<MISSION: return
    pop=sm(seg01(V,MISSION,MISSION+0.2)); y=int(lerp(-40,30,pop))
    d.rectangle([8,y,W-8,y+30],fill=(10,24,12),outline=GRN); d.rectangle([10,y+2,W-10,y+12],fill=(30,120,40))
    otext(d,'STEALTH MISSION',(W-font.width('STEALTH MISSION'))//2,y+4,WHT); otext(d,'COMPLETE',(W-font.width('COMPLETE',2))//2,y+14,YEL,2)
def frame(V):
    sh=shot(V); img,vi=render(V,sh); d=ImageDraw.Draw(img)
    gs=guard_state(V); ts=thief_state(V)
    emotes(d,vi,V,gs,ts); meter(d,V); mission(d,V); subtitle(d,V)
    return img

TEST=os.environ.get('TEST')
if TEST and __name__=='__main__':
    ims=[frame(float(x)) for x in TEST.split(',')]; shp=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): shp.paste(im,(i*182,0))
    shp.resize((shp.width*2,640),Image.NEAREST).save('test.png'); sys.exit()

# ======================= QA manifest (tools/qa/scene_qa.py, PIPELINE.md) =======================
def _th(t): return {k:v for k,v in thief_state(t).items() if k in TH_KEYS}
def _gu(t): return {k:v for k,v in guard_state(t).items() if k in GU_KEYS}
def _geom(t,name,st,V):
    out=[]
    if V[:,1].min()<-0.04: out.append(('floor',f'{name} under the floor'))
    if (np.abs(V[:,0])>HALL_X-0.02).any(): out.append(('wall',f'{name} inside a corridor wall'))
    for x,z in PILLARS+[PEDESTAL]:
        hs=PH if (x,z)!=PEDESTAL else 0.42
        inn=(np.abs(V[:,0]-x)<hs-0.02)&(np.abs(V[:,2]-z)<hs-0.02)&(V[:,1]<(3.9 if (x,z)!=PEDESTAL else 1.0))
        if inn.any(): out.append(('intersect',f'{name} inside {"the crown pedestal" if (x,z)==PEDESTAL else f"a pillar at ({x:.1f},{z:.1f})"}'))
    return out
_prev_notes={}
def _extra(t):
    out=[]; gs=guard_state(t); ts=thief_state(t)
    cur={txt:np.array(c) for txt,c,r,u,n in notes(t,gs,ts)}
    for txt,c in cur.items():                                    # a note never jumps (no magic swap)
        p=_prev_notes.get(txt)
        if p is not None and p[0]==round(t*FPS)-1 and np.linalg.norm(c-p[1])>0.25: out.append(('note',f'note "{txt}" jumps {np.linalg.norm(c-p[1]):.2f} m in one frame'))
        _prev_notes[txt]=(round(t*FPS),c)
    if OLD in cur and NEW in cur: out.append(('note','both notes visible at once'))
    if t>=NOTE_SWAP[1] and OLD in cur: out.append(('note','old note still visible after the swap'))
    if t>=CROWN_TAKE and t<CUFF[1]: out.append(('crown','crown taken before the guard is cuffed'))
    if CROWN_TAKE<=t<CROWN_TAKE+0.6:                             # hands are on the crown when it leaves the cushion
        hc=(np.array(thief_hand(ts,1))+np.array(thief_hand(ts,-1)))/2
        if abs(t-CROWN_TAKE-0.0)<0.5/FPS and np.linalg.norm(hc-np.array([PEDESTAL[0],1.17,PEDESTAL[1]]))>0.3: out.append(('crown',f'thief hands {np.linalg.norm(hc-np.array([PEDESTAL[0],1.17,PEDESTAL[1]])):.2f} m from the crown when he lifts it'))
    for nm,st_,pt,hand_,L_ in (('thief',ts,thief_point,thief_hand,0.6),('guard',gs,guard_point,guard_hand,0.68)):
        for sx in (-1,1):
            sh_=np.array(pt(st_,(sx*(0.19 if nm=='thief' else 0.32),1.17 if nm=='thief' else 1.36,0)))
            dd=np.linalg.norm(np.array(hand_(st_,sx))-sh_)
            if dd>L_: out.append(('stretch',f'{nm} arm stretched beyond its length ({dd:.2f} m)'))
    if gs.get('cuffs')=='wrists' and np.linalg.norm(np.array(guard_hand(gs,1))-np.array(guard_hand(gs,-1)))>0.25: out.append(('cuffs','cuffed wrists are too far apart'))
    if NOTE_SWAP[0]+0.3<=t<NOTE_SWAP[1]:                         # the swap: the thief's hand reaches the chest
        if abs(t-(NOTE_SWAP[0]+0.45))<0.5/FPS:
            d=np.linalg.norm(np.array(thief_hand(ts,1))-np.array(guard_point(gs,NOTE_ON_CHEST)))
            if d>0.12: out.append(('note',f'thief hand {d:.2f} m from the pinned note when he takes it'))
    return out
QA=dict(fps=FPS,dur=DUR,W=W,frame=frame,
    chars={'thief':(_th,thief,'crown_on',False),'guard':(_gu,guard,'cuffs','belt')},
    geom=_geom,extra=_extra,camera=lambda t: shot(t)['cam'],min_cam_dist=0.45,
    camera_ok=lambda p: abs(p[0])<HALL_X-0.1 and 0.05<p[1]<3.8 and Z0+0.1<p[2]<Z1 and not any(abs(p[0]-x)<PH+0.05 and abs(p[2]-z)<PH+0.05 for x,z in PILLARS),
    scenes=[dict(id='hook',t0=0.0,t1=HOOK_DUR,action='guard chases thief; thief ducks behind a pillar; guard stops, confused',env='corridor'),
            dict(id='reset',t0=HOOK_DUR,t1=8.0,action='alert meter 10->0; Must have been the wind; thief peeks',env='pillar'),
            dict(id='exploit',t0=8.0,t1=13.0,action='thief tiptoes behind guard; HEY STOP; hides; meter resets',env='corridor'),
            dict(id='suspicious',t0=13.0,t1=14.5,action='guard scratches his helmet, takes out paper',env='corridor'),
            dict(id='writing',t0=14.5,t1=16.05,action='insert: ARREST THE THIEF! written letter by letter',env='note',pov=False),
            dict(id='pinned',t0=16.05,t1=19.0,action='pins the note; Now I wont forget!',env='corridor'),
            dict(id='swap',t0=19.0,t1=23.0,action='thief sneaks up, swaps the note by hand, memory meter runs',env='corridor'),
            dict(id='new-note',t0=23.0,t1=24.75,action='insert: YOU ARE THE THIEF!',env='note'),
            dict(id='self-arrest',t0=24.75,t1=26.95,action='Im the thief?! guard cuffs his own wrists',env='corridor'),
            dict(id='crown',t0=26.95,t1=DUR,action='thief takes the crown, walks off; STEALTH MISSION COMPLETE',env='corridor, pedestal')],
    weapon_events=[('guard',CUFF[0]+0.02,'belt','hand'),('guard',CUFF[0]+0.8,'hand','wrists'),('thief',CROWN_TAKE+0.6,False,True)],
    texts=lambda: [(k,ln,1) for k in SCR['text'] for ln in wrap((SPK[k[0]][0]+' ' if SPK[k[0]][0] else '')+SCR['text'][k].upper())]
          +[('N1',x,2) for x in HOOK_LINES]+[('ui','STEALTH MISSION',1),('ui','COMPLETE',2),('ui','MEMORY',1),('ui','ALERT',1),('note','ARREST THE',1),('note','YOU ARE',1),('note','THE THIEF!',1)])

# ======================= AUDIO =======================
HOOK_MOTIF=[(0.0,64),(0.15,67),(0.3,64),(0.45,70),(0.6,69),(0.75,67)]     # the chase riff (shared with B)
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=37); sr=s.sr; n=s.n; M=np.zeros(n); AMB=np.zeros(n)
    def note(buf,t0,m,d,v,wave='sq',duty=0.5,dec=3.0,att=0.005):
        f=440*2**((m-69)/12); tt=s.T(d); ph=(f*tt)%1
        x=np.where(ph<duty,1.0,-1.0) if wave=='sq' else (4*np.abs(ph-0.5)-1 if wave=='tri' else np.sin(2*np.pi*ph))
        env=np.minimum(1,tt/att)*np.exp(-tt*dec); i=int(t0*sr); j=min(n,i+len(tt)); buf[i:j]+=(x*env*v)[:j-i]
    def nb(t0,d,lo,hi,v,seed,shape=2): s.place(s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v)
    def clank(t0,v=0.06,seed=0): tt=s.T(0.25); s.place(sum(np.sin(2*np.pi*f*tt)*np.exp(-tt*k) for f,k in ((620,14),(1500,20)))*0.4+s.filt_short(s.noise(0.25,seed),lo=2000,hi=7000)*np.exp(-tt*40),t0,v)
    def step_g(t0,v=0.05,seed=0): tt=s.T(0.14); s.place(s.filt_short(s.noise(0.14,seed),lo=150,hi=1800)*np.exp(-tt*40),t0,v); clank(t0,v*0.25,seed+500)
    def step_t(t0,v=0.025,seed=0): tt=s.T(0.06); s.place(s.filt_short(s.noise(0.06,seed),lo=600,hi=3000)*np.exp(-tt*80),t0,v)
    def blip(t0,m,v=0.04,d=0.08): note(M,t0,m,d,v,'sq',0.25,18)
    def alert(t0): [note(M,t0+k*0.09,m,0.12,0.05,'sq',0.5,6) for k,m in enumerate((88,93,100))]
    def tick(t0): tt=s.T(0.03); s.place(np.sin(2*np.pi*2200*tt)*np.exp(-tt*120),t0,0.03)
    def scratch(t0,d=1.3): nb(t0,d,2500,8000,0.02,int(t0*10),shape=1)
    AMB+=s.filt(s.rng.normal(0,1,n),lo=60,hi=500)*0.012
    pr=np.random.default_rng(3)
    for tc in np.cumsum(pr.exponential(0.3,140)):
        if tc<DUR: i=int(tc*sr); x=np.sign(s.noise(0.01,int(tc*991)))*np.exp(-s.T(0.01)*300)*0.01; AMB[i:i+len(x)]+=x[:max(0,min(len(x),n-i))]
    # ---------- music ----------
    def sneak(a,b,v=1.0,root=57,step=0.2):
        pat=[0,None,3,None,0,None,7,6,0,None,3,None,10,None,7,None]; k=0; tc=a
        while tc<b-1e-6:
            m=pat[k%16]
            if m is not None: note(M,tc,root+12+m,step*0.6,0.022*v,'sq',0.25,14)
            if k%2==0: note(M,tc,root-12+(0 if (k//8)%2==0 else 3),step*1.5,0.05*v,'tri',dec=6)
            if k%4==2: s.place(s.filt_short(s.noise(0.03,k),lo=6000)*np.exp(-s.T(0.03)*120),tc,0.008*v)
            k+=1; tc+=step
    def chase(a,b,v=1.0,root=64):
        k=0; tc=a
        while tc<b-1e-6:
            dt,m=HOOK_MOTIF[k%6]; note(M,tc,m+12,0.12,0.026*v,'sq',0.5,10)
            if k%2==0: note(M,tc,root-24+(0 if (k//6)%2==0 else -2),0.2,0.06*v,'tri',dec=5)
            if k%3==0: s.place(s.filt_short(s.noise(0.05,k),lo=80,hi=400)*np.exp(-s.T(0.05)*60),tc,0.05*v)
            k+=1; tc+=0.15
    chase(0.0,1.95)
    for k,m in enumerate((76,72,68)): note(M,1.95+k*0.12,m,0.14,0.03,'sq',0.5,8)             # skid + record stop
    sneak(3.5,9.3,0.8)
    alert(9.45); chase(9.6,10.6,0.9)
    sneak(10.9,13.0,0.7)
    sneak(16.6,19.0,0.6,root=60)
    sneak(19.0,23.9,0.9,step=0.17)
    alert(24.85)
    for k,m in enumerate((60,59,58,57)): note(M,25.0+k*0.18,m,0.2,0.04,'sq',0.5,6)             # dun-dun-dun
    sneak(26.95,MISSION,0.7,root=60,step=0.16)
    for k,m in enumerate((72,76,79,84,79,84,88)): note(M,MISSION+k*0.08,m,0.2 if k<6 else 0.6,0.035,'sq',0.25,5 if k<6 else 2)   # mission complete
    # ---------- sfx ----------
    for k in range(9): step_t(0.05+k*0.15,0.035,k)
    for k in range(10): step_g(0.1+k*0.19,0.05,20+k)
    nb(1.6,0.3,800,4000,0.03,40)                                                                   # skid
    for k in range(int((6.15-3.5)/0.29)): tick(3.5+k*0.29)                                        # meter counting down
    blip(6.15,60,0.05,0.2)
    nb(6.6,0.9,300,1500,0.02,41)                                                                   # 'the wind'
    for k in range(6): step_t(8.05+k*0.2,0.02,50+k)
    for k in range(5): step_t(9.9+k*0.13,0.04,60+k)
    for k in range(int((12.7-10.9)/0.18)): tick(10.9+k*0.18)
    blip(12.7,60,0.05,0.2)
    nb(13.05,0.7,1500,5000,0.015,70)                                                               # helmet scratch
    nb(14.0,0.3,1000,4000,0.03,71); scratch(14.55)                                                # paper + quill
    s.place(np.sin(2*np.pi*900*s.T(0.05))*np.exp(-s.T(0.05)*60),16.45,0.04)                       # pin
    for k in range(int((23.8-18.6)/0.52)): tick(18.6+k*0.52)
    for k in range(6): step_t(19.05+k*0.2,0.02,80+k)
    nb(NOTE_SWAP[0]+0.45,0.15,1500,6000,0.03,81); nb(NOTE_SWAP[0]+0.9,0.2,500,2500,0.02,82); nb(NOTE_SWAP[1]-0.3,0.2,1500,6000,0.03,83)   # rip, pouch, pin
    s.place(np.sin(2*np.pi*900*s.T(0.05))*np.exp(-s.T(0.05)*60),NOTE_SWAP[1]-0.15,0.04)
    for k in range(5): step_t(22.05+k*0.18,0.02,90+k)
    blip(23.8,60,0.05,0.25)
    clank(CUFF[0]+0.1,0.06,95); clank(CUFF[0]+0.8,0.1,96); clank(CUFF[0]+0.95,0.08,97)            # click-click
    for k in range(10): step_t(CUFF[1]+0.2+k*0.17,0.03,100+k)
    for k,f in enumerate((2600,3300,4100)): tt=s.T(0.5); s.place(np.sin(2*np.pi*f*tt)*np.exp(-tt*8),CROWN_TAKE+0.02+k*0.06,0.03)   # crown shimmer
    for k in range(9): step_t(CROWN_TAKE+0.65+k*0.25,0.025,120+k)
    # ---------- voices ----------
    NB=np.zeros(n); duck=np.ones(n)
    for k_,t0 in VOICE:
        a,ar=_sf.read(os.path.join(TTS_DIR,'gf',f'{k_}.wav')); a=a if a.ndim==1 else a.mean(1)
        a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a)
        act=a[np.abs(a)>0.02]; a=a/(np.sqrt((act**2).mean())+1e-9)*0.2
        i=int(t0*sr); j=min(n,i+len(a)); NB[i:j]+=a[:j-i]
        duck[max(0,i-int(0.05*sr)):min(n,j+int(0.1*sr))]=0.45
    duck=np.convolve(duck,np.ones(2400)/2400,'same')
    s.L+=2.0*M*duck+AMB; s.R+=2.0*np.roll(M,240)*duck+np.roll(AMB,700)
    s.reverb(0.18,length=1.4,decay=3.5)
    pk=max(np.abs(s.L).max(),np.abs(s.R).max()); gv=pk*1.05/np.abs(NB).max()
    s.L=s.L*(0.55+0.45*duck)+NB*gv; s.R=s.R*(0.55+0.45*duck)+NB*gv
    return s.save(path,peak=0.9)
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'guard_forgets_a.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'gf_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.96,vignette=0.22,grain=1.5,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(post.upscale(frame(f/FPS),S),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
