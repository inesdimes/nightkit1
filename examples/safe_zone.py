"""SAFE ZONE - "Why are dungeon shops safe?"  PS1 fantasy-RPG comedy short, 9:16, ~58.6 s. Fully procedural (nightkit).
LOCKED ASSETS (for a shorter cut later): the channel knight (final_boss.knight, brown boots), skeleton(), keeper(), the shop set,
the safe-zone barrier, the payment terminal, props and every UI overlay. All text is a 2D overlay.
Voices: python tools/tts/sz.py -> $TTS_DIR/sz/*.wav
Run: TEST=0.3,5,12 python examples/safe_zone.py -> test.png | PART=a:b | PART=audio | QA: python tools/qa/scene_qa.py examples/safe_zone.py"""
import os, sys, math, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, quad
from nightkit import post, font
from nightkit.zraster import zrender
from nightkit.audio import Sound
import final_boss as FB
import guard_forgets as GF                                # path helpers, text helpers
box,seg,xform,limb,prelit=FB.box,FB.seg,FB.xform,FB.limb,FB.prelit
sm,seg01,lerp,lerp3,PI,Ry,Rx=FB.sm,FB.seg01,FB.lerp,FB.lerp3,FB.PI,FB.Ry,FB.Rx
alerp,path3,path_yaw=GF.alerp,GF.path3,GF.path_yaw
TTS_DIR=FB.TTS_DIR; OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6; DUR=58.6; N=int(round(DUR*FPS))
SCR=json.load(open(os.path.join(TTS_DIR,'sz','script.json')))
for ch,rows in {'!':['00100','00100','00100','00100','00100','00000','00100'],'?':['01110','10001','00001','00110','00100','00000','00100'],
                '+':['00000','00100','00100','11111','00100','00100','00000']}.items(): font.FONT.setdefault(ch,rows)

# ======================= palette =======================
BONE=(226,220,196); BONE_D=(170,162,140); SOCKET=(34,26,24); RUST=(150,96,62); RUST_D=(108,66,44); CARD=(150,80,220); GOLDC=(250,206,60)
VEST=(60,140,70); VEST_D=(44,108,52); SHIRT=(236,230,214); TROU=(96,70,48); SKIN=(232,190,150); HAIR=(236,236,236); GLASS=(70,52,30)
WOOD=(122,80,44); WOOD_D=(92,60,32); WOOD_L=(150,104,58); STONE=(92,86,96); STONE_D=(74,70,80); FLOOR1=(118,82,52); FLOOR2=(104,72,46)
KBOOTS=(112,72,40)
WHT=(242,238,226); YEL=(255,210,60); RED=(232,44,40); GRN=(120,230,90); BLU=(110,170,255); GRY=(150,150,160); CYAN=(90,210,255)

# ======================= LOCKED ASSET: knight helpers (final_boss.knight + brown boots) =======================
KN_KEYS={'base','yaw','walk','run','sword','rh','lh','lean','head','sit','boots','swing'}
def knight(**st): return FB.knight(**{k:v for k,v in st.items() if k in KN_KEYS})
def kpoint(st,p):
    b=np.array(st['base'],float); sit=st.get('sit',0.0); hip=0.82-0.42*sit; piv=np.array([0,hip,0])
    q=np.array(p,float)-piv+np.array([0,hip-0.82,0]); return tuple(b+Ry(st['yaw'])@(piv+Rx(st.get('lean',0.0)+0.22*st.get('run',0.0))@q))
def khand(st,side=1):
    h=st.get('rh' if side>0 else 'lh')
    if h is None: h=(0.27*side,0.86,0.04)
    return kpoint(st,h)
def k_local(st,w):
    """world point -> knight torso coords (inverse of kpoint)"""
    b=np.array(st['base'],float); sit=st.get('sit',0.0); hip=0.82-0.42*sit; piv=np.array([0,hip,0])
    q=Rx(-(st.get('lean',0.0)+0.22*st.get('run',0.0)))@(Ry(-st['yaw'])@(np.array(w,float)-b)-piv); return tuple(q+piv-np.array([0,hip-0.82,0]))

# ======================= LOCKED ASSET: the skeleton =======================
def skeleton(base,yaw,walk=0.0,run=0.0,lean=0.0,rh=None,lh=None,jaw=0.0,head=0.0,card=True,sdir=(0.0,-1.0,0.35),rage=0.0):
    """low-poly skeleton, rusty sword in the right hand, a purple PREMIUM card clipped to the left hip. local forward +z, ~1.75 m."""
    b=np.array(base,float); Rb=Ry(yaw)
    def Wd(p): return tuple(b+Rb@np.array(p,float))
    hip=0.86
    def T(p): p=np.array(p,float); piv=np.array([0,hip,0]); return Wd(piv+Rx(lean+0.2*run)@(p-piv))
    Q=[]; amp=0.45+0.35*run; sw=amp*math.sin(walk)
    for sx,ph in ((-1,1),(1,-1)):
        hp=np.array([sx*0.1,hip,0]); a=ph*sw; ft=hp+np.array([0,-0.8*math.cos(a),0.8*math.sin(a)]); ft[1]=max(0.05,ft[1]+0.08*max(0,math.sin(walk*ph+PI/2))*(1 if walk else 0))
        lq,kn=limb(hp,ft,(0,0,1),0.86,0.07,BONE,BONE,0.06); Q+=xform(lq,Wd)
        Q+=box(kn[0]-0.05,kn[0]+0.05,kn[1]-0.05,kn[1]+0.05,kn[2]-0.04,kn[2]+0.06,BONE_D,xf=Wd)
        Q+=box(ft[0]-0.06,ft[0]+0.06,ft[1]-0.05,ft[1]+0.02,ft[2]-0.05,ft[2]+0.14,BONE,xf=Wd)
    Q+=box(-0.16,0.16,0.8,0.94,-0.08,0.08,BONE_D,xf=T)                                                 # pelvis
    Q+=box(-0.18,0.18,0.92,0.98,-0.09,0.09,(86,60,40),xf=T)+box(-0.16,-0.04,0.8,0.95,-0.17,-0.09,(110,78,46),xf=T)   # belt + coin pouch (back left)
    if card: Q+=box(-0.24,-0.2,0.78,0.94,-0.06,0.07,CARD,xf=T)+box(-0.245,-0.235,0.84,0.88,-0.065,0.075,GOLDC,xf=T)   # PREMIUM card
    Q+=box(-0.035,0.035,0.94,1.52,-0.06,0.0,BONE_D,xf=T)                                                # spine
    for k,y in enumerate((1.08,1.17,1.26,1.35)): Q+=box(-0.17+0.02*k*0,0.17,y,y+0.045,-0.08,0.1,BONE,xf=T)  # ribs
    Q+=box(-0.03,0.03,1.06,1.42,0.09,0.11,BONE,xf=T)                                                   # sternum
    Q+=box(-0.24,0.24,1.42,1.5,-0.07,0.07,BONE,xf=T)                                                   # collarbones
    hy=1.52; Rh=Ry(head)
    def Hh(p): p=np.array(p,float); return T(np.array([0,hy,0])+Rh@(p-np.array([0,hy,0])))
    Q+=box(-0.13,0.13,1.56,1.84,-0.14,0.14,BONE,xf=Hh)                                                # skull
    for sx in (-1,1):
        Q+=box(sx*0.025,sx*0.105,1.66,1.75,0.14,0.145,SOCKET,xf=Hh)
        g=tuple(int(c) for c in lerp3((200,40,30),(255,70,40),rage))
        Q+=box(sx*0.05,sx*0.08,1.69,1.72,0.145,0.15,g,xf=Hh,emit=True)
    Q+=box(-0.02,0.02,1.62,1.66,0.14,0.145,SOCKET,xf=Hh)
    jy=1.56-0.06*jaw
    Q+=box(-0.11,0.11,jy-0.06,jy,-0.08,0.13,BONE_D,xf=Hh)+box(-0.08,0.08,jy,jy+0.025,0.125,0.135,WHT,xf=Hh)  # jaw + teeth
    Q+=box(-0.08,0.08,1.565,1.59,0.135,0.145,WHT,xf=Hh)
    sh={-1:np.array([-0.24,1.45,0]),1:np.array([0.24,1.45,0])}
    idle={-1:np.array([-0.26,0.88,0.06]),1:np.array([0.26,0.9,0.14])}
    if run: idle={-1:np.array([-0.24,1.0,-0.18*math.sin(walk)]),1:np.array([0.24,1.05,0.25])}
    hand={-1:np.array(lh,float) if lh is not None else idle[-1],1:np.array(rh,float) if rh is not None else idle[1]}
    for sx in (-1,1):
        aq,_=limb(sh[sx],hand[sx],(sx*0.5,-0.4,-0.6),0.62,0.05,BONE,BONE,0.045); Q+=xform(aq,T)
        hp=hand[sx]; Q+=box(hp[0]-0.04,hp[0]+0.04,hp[1]-0.04,hp[1]+0.04,hp[2]-0.04,hp[2]+0.04,BONE_D,xf=T)
    if sdir is not None:                                                                                # rusty sword
        hp=hand[1]; dr=np.array(sdir,float); dr/=np.linalg.norm(dr)
        Q+=xform(seg(hp+dr*0.05,hp+dr*0.8,0.05,RUST,0.018)+seg(hp+dr*0.3,hp+dr*0.36,0.052,RUST_D,0.02),T)
        cr=np.cross(dr,np.array([0,1.0,0]) if abs(dr[1])<0.9 else np.array([1.0,0,0])); cr/=np.linalg.norm(cr)+1e-9
        Q+=xform(seg(hp+dr*0.04-cr*0.09,hp+dr*0.04+cr*0.09,0.035,(90,80,70))+seg(hp-dr*0.09,hp+dr*0.04,0.03,(70,50,36)),T)
    return Q
SK_KEYS={'base','yaw','walk','run','lean','rh','lh','jaw','head','card','sdir','rage'}
def skpoint(st,p):
    b=np.array(st['base'],float); piv=np.array([0,0.86,0]); q=np.array(p,float)
    return tuple(b+Ry(st['yaw'])@(piv+Rx(st.get('lean',0.0)+0.2*st.get('run',0.0))@(q-piv)))
def sk_local(st,w):
    b=np.array(st['base'],float); piv=np.array([0,0.86,0])
    return tuple(piv+Rx(-(st.get('lean',0.0)+0.2*st.get('run',0.0)))@(Ry(-st['yaw'])@(np.array(w,float)-b)-piv))
def skhand(st,side=1):
    h=st.get('rh' if side>0 else 'lh')
    if h is None: h=(0.26,0.9,0.14) if side>0 else (-0.26,0.88,0.06)
    return skpoint(st,h)

# ======================= LOCKED ASSET: the shopkeeper =======================
def keeper(base,yaw,rh=None,lh=None,smile=1.0,mouth=0.0,head=0.0,lean=0.0,blink=0.0):
    """elderly cheerful NPC: bald with white hair, round glasses, white moustache, green vest. local forward +z, ~1.6 m."""
    b=np.array(base,float); Rb=Ry(yaw)
    def Wd(p): return tuple(b+Rb@np.array(p,float))
    hip=0.82
    def T(p): p=np.array(p,float); piv=np.array([0,hip,0]); return Wd(piv+Rx(lean)@(p-piv))
    Q=[]
    for sx in (-1,1):
        Q+=box(sx*0.04,sx*0.16,0.06,0.82,-0.08,0.08,TROU,xf=Wd)+box(sx*0.03,sx*0.17,0.0,0.07,-0.09,0.14,(60,40,28),xf=Wd)
    Q+=box(-0.2,0.2,0.78,1.36,-0.14,0.15,SHIRT,xf=T)+box(-0.21,0.21,0.8,1.3,-0.15,0.12,VEST,xf=T)               # shirt + vest (open at the front)
    Q+=box(-0.21,-0.07,0.8,1.3,0.12,0.16,VEST,xf=T)+box(0.07,0.21,0.8,1.3,0.12,0.16,VEST,xf=T)
    for y in (0.95,1.08,1.21): Q+=box(-0.1,-0.07,y,y+0.03,0.16,0.17,GOLDC,xf=T)
    Q+=box(-0.18,0.18,0.86,1.0,0.14,0.2,SHIRT,xf=T)                                                           # round belly
    hy=1.38; Rh=Ry(head)
    def Hh(p): p=np.array(p,float); return T(np.array([0,hy,0])+Rh@(p-np.array([0,hy,0])))
    Q+=box(-0.13,0.13,1.38,1.64,-0.12,0.13,SKIN,xf=Hh)
    for sx in (-1,1): Q+=box(sx*0.12,sx*0.15,1.44,1.58,-0.12,0.06,HAIR,xf=Hh)                                  # white hair at the sides
    Q+=box(-0.12,0.12,1.4,1.43,-0.13,-0.08,HAIR,xf=Hh)
    for sx in (-1,1):
        cx=sx*0.06; y0,y1=1.5,1.57
        for (x0,x1,yy0,yy1) in ((cx-0.045,cx+0.045,y1,y1+0.012),(cx-0.045,cx+0.045,y0-0.012,y0),(cx-0.05,cx-0.04,y0,y1),(cx+0.04,cx+0.05,y0,y1)):
            Q+=box(x0,x1,yy0,yy1,0.13,0.14,GLASS,xf=Hh)                                                          # round(ish) glasses
        ey=lerp(0.02,0.004,blink)
        Q+=box(cx-0.015,cx+0.015,1.535-ey,1.535+ey,0.13,0.135,(30,24,20),xf=Hh,emit=True)
        Q+=box(sx*0.07,sx*0.11,1.45,1.48,0.13,0.134,(236,140,130),xf=Hh)                                          # rosy cheeks
    Q+=box(-0.005,0.005,1.53,1.545,0.13,0.14,GLASS,xf=Hh)
    Q+=box(-0.02,0.02,1.47,1.53,0.13,0.17,(214,160,128),xf=Hh)                                                    # nose
    Q+=box(-0.08,0.08,1.44,1.47,0.13,0.15,HAIR,xf=Hh)                                                             # moustache
    my=1.415+0.008*smile; Q+=box(-0.05,0.05,my-0.008-0.025*mouth,my,0.13,0.136,(90,30,26),xf=Hh)
    for sx in (-1,1): Q+=box(sx*0.045,sx*0.065,my,my+0.012*smile,0.13,0.136,(90,30,26),xf=Hh)
    sh={-1:np.array([-0.24,1.28,0]),1:np.array([0.24,1.28,0])}
    idle={-1:np.array([-0.2,1.02,0.3]),1:np.array([0.2,1.02,0.3])}                                          # hands resting on the counter
    hand={-1:np.array(lh,float) if lh is not None else idle[-1],1:np.array(rh,float) if rh is not None else idle[1]}
    for sx in (-1,1):
        aq,_=limb(sh[sx],hand[sx],(sx*0.5,-0.4,-0.4),0.56,0.09,SHIRT,SHIRT,0.08); Q+=xform(aq,T)
        hp=hand[sx]; Q+=box(hp[0]-0.045,hp[0]+0.045,hp[1]-0.045,hp[1]+0.045,hp[2]-0.045,hp[2]+0.045,SKIN,xf=T)
    return Q
KP_KEYS={'base','yaw','rh','lh','smile','mouth','head','lean','blink'}
def kppoint(st,p):
    b=np.array(st['base'],float); piv=np.array([0,0.82,0]); return tuple(b+Ry(st['yaw'])@(piv+Rx(st.get('lean',0.0))@(np.array(p,float)-piv)))
def kp_local(st,w):
    b=np.array(st['base'],float); piv=np.array([0,0.82,0]); return tuple(piv+Rx(-st.get('lean',0.0))@(Ry(-st['yaw'])@(np.array(w,float)-b)-piv))

# ======================= LOCKED ASSET: the shop, barrier, terminal, props =======================
DOOR_W=1.0; DOOR_H=2.4; BAR_Z=0.04; SX=2.6; BACKZ=6.0; COUNTER=(-1.6,1.6,3.9,4.4,1.0); KEEPER=(0.0,0,4.85)
TERM=(1.62,-0.32); STOOL=(-1.95,2.35); BELL=(0.62,1.0,4.12)
def shop_static():
    Q=[]
    xs=list(np.arange(-SX,SX+0.01,0.65)); zs=list(np.arange(0.0,BACKZ+0.01,0.75))
    for i in range(len(xs)-1):
        for j in range(len(zs)-1): Q.append(quad([(xs[i],0,zs[j]),(xs[i+1],0,zs[j]),(xs[i+1],0,zs[j+1]),(xs[i],0,zs[j+1])],FLOOR1 if (i+j)%2 else FLOOR2))
    def wc(i,j,v): return STONE if (i+j)%2 else STONE_D
    Q+=FB.wall_region('x',-SX,0,BACKZ,0,3.4,1.0,0.85,wc,facing=-1)+FB.wall_region('x',SX,0,BACKZ,0,3.4,1.0,0.85,wc)
    Q+=FB.wall_region('z',BACKZ,-SX,SX,0,3.4,1.0,0.85,wc,facing=-1)
    Q+=FB.wall_region('z',0.0,-SX,-DOOR_W,0,3.4,0.8,0.85,wc)+FB.wall_region('z',0.0,DOOR_W,SX,0,3.4,0.8,0.85,wc)+FB.wall_region('z',0.0,-DOOR_W,DOOR_W,DOOR_H,3.4,1.0,1.0,wc)
    Q+=[quad([(-SX,3.4,0),(SX,3.4,0),(SX,3.4,BACKZ),(-SX,3.4,BACKZ)],(52,40,34))]
    Q+=box(-DOOR_W-0.25,-DOOR_W,0,DOOR_H+0.25,-0.25,0.3,WOOD_D)+box(DOOR_W,DOOR_W+0.25,0,DOOR_H+0.25,-0.25,0.3,WOOD_D)+box(-DOOR_W-0.25,DOOR_W+0.25,DOOR_H,DOOR_H+0.25,-0.25,0.3,WOOD_D)
    x0,x1,z0,z1,h=COUNTER                                                                              # the counter
    Q+=box(x0,x1,0,h-0.06,z0,z1,WOOD)+box(x0-0.05,x1+0.05,h-0.06,h,z0-0.05,z1+0.05,WOOD_L)+box(x0+0.1,x1-0.1,0.1,0.8,z0-0.02,z0,WOOD_D)
    for x in (-1.0,0.0,1.0): Q+=box(x-0.03,x+0.03,0.1,0.8,z0-0.025,z0-0.005,WOOD_L)
    for k,y in enumerate((0.9,1.55,2.2)):                                                               # shelves of potions on the back wall
        Q+=box(-2.2,2.2,y,y+0.06,BACKZ-0.45,BACKZ,WOOD_D)
        for i in range(11):
            x=-2.0+i*0.4; c=[(220,40,60),(60,120,240),(80,200,90),(230,180,40)][(i+k)%4]
            Q+=box(x-0.07,x+0.07,y+0.06,y+0.28,BACKZ-0.3,BACKZ-0.16,c,emit=True)+box(x-0.03,x+0.03,y+0.28,y+0.34,BACKZ-0.26,BACKZ-0.2,(200,190,170))
    Q+=box(-2.55,-1.9,0,1.3,1.2,1.8,WOOD_D)+box(-2.5,-1.95,1.3,1.36,1.2,1.8,WOOD_L)                      # barrel stack / crate
    sx,sz=STOOL; Q+=box(sx-0.22,sx+0.22,0.42,0.48,sz-0.22,sz+0.22,WOOD_L)
    for dx in (-0.16,0.16):
        for dz in (-0.16,0.16): Q+=box(sx+dx-0.03,sx+dx+0.03,0,0.42,sz+dz-0.03,sz+dz+0.03,WOOD_D)
    # outside corridor
    def cc(i,j,v): return (60,58,70) if (i+j)%2 else (50,48,60)
    Q+=FB.tiled_plane(-2.4,2.4,-7.0,0.0,0.0,0.8,lambda i,j:(70,68,78) if (i+j)%2 else (58,56,66))
    Q+=FB.wall_region('x',-2.4,-7.0,0.0,0,3.4,1.2,0.85,cc)+FB.wall_region('x',2.4,-7.0,0.0,0,3.4,1.2,0.85,cc,facing=-1)
    Q+=[quad([(-2.4,3.4,-7.0),(2.4,3.4,-7.0),(2.4,3.4,0),(-2.4,3.4,0)],(36,34,44))]
    Q+=box(-0.9,0.9,2.7,3.15,-0.32,-0.26,WOOD_L)                                                       # shop sign board above the door
    return Q
SHOP=shop_static()
def sign_coin():
    return box(-0.13,0.13,2.8,3.06,-0.34,-0.32,GOLDC,emit=True)
def terminal(state):
    """payment terminal outside the door: post + box with slot; screen colour shows the state"""
    x,z=TERM; Q=box(x-0.06,x+0.06,0,0.95,z-0.06,z+0.06,(70,70,80))+box(x-0.2,x+0.2,0.95,1.35,z-0.16,z+0.06,(96,96,110))
    scr={'idle':(30,40,90),'busy':(200,170,40),'ok':(60,220,80)}[state]
    Q+=box(x-0.14,x+0.14,1.08,1.3,z-0.165,z-0.155,scr,emit=True)+box(x-0.06,x+0.06,0.99,1.02,z-0.165,z-0.155,(20,20,24))
    return Q
TERM_SLOT=(TERM[0],1.005,TERM[1]-0.215); TERM_SCREEN=(TERM[0],1.19,TERM[1]-0.215)
TORCH=[(-2.35,2.0,-2.0),(2.35,2.0,-4.5),(-2.5,2.4,3.0),(2.5,2.4,3.0)]
def torches(t):
    Q=[]
    for k,(x,y,z) in enumerate(TORCH):
        fl=0.05*math.sin(t*13+k*2.1); Q+=box(x-0.06,x+0.06,y+0.02,y+0.22+fl,z-0.06,z+0.06,(255,140,50),emit=True)+box(x-0.04,x+0.04,y-0.3,y,z-0.04,z+0.04,(60,50,40))
    return Q
def lights(t):
    L=[((x*0.8,y+0.3,z),(255,170,90),1.0+0.1*math.sin(t*11+k)) for k,(x,y,z) in enumerate(TORCH)]
    L+=[((0,2.9,3.4),(255,226,170),1.6),((0,2.6,0.6),(255,226,170),0.8)]
    return L
def barrier_quads(alpha,flash,rc,rr,tint):
    Q=[]; nx,ny=8,10
    for i in range(nx):
        for j in range(ny):
            a=-DOOR_W+2*DOOR_W*i/nx; b_=-DOOR_W+2*DOOR_W*(i+1)/nx; c=DOOR_H*j/ny; d=DOOR_H*(j+1)/ny; cx,cy=(a+b_)/2,(c+d)/2
            g=alpha*(0.12+0.06*((i+j)%2)+0.05*math.sin(cy*3+cx*2))
            if rc is not None: r=math.hypot(cx-rc[0],cy-rc[1]); g+=flash*(max(0.0,1-abs(r-rr)/0.6)*1.1+0.5*max(0,1-r/1.8))
            Q.append(quad([(a,c,BAR_Z),(b_,c,BAR_Z),(b_,d,BAR_Z),(a,d,BAR_Z)],tuple(min(255,int(v*g)) for v in tint),emit=True))
    return Q
def potion(p,s=1.0):
    x,y,z=p; return box(x-0.05*s,x+0.05*s,y-0.06*s,y+0.06*s,z-0.05*s,z+0.05*s,(220,40,60),emit=True)+box(x-0.02,x+0.02,y+0.06*s,y+0.1*s,z-0.02,z+0.02,(200,190,170))
def rusty_sword(hilt,dirv):
    h=np.array(hilt,float); d=np.array(dirv,float); d/=np.linalg.norm(d)
    cr=np.cross(d,np.array([0,1.0,0]) if abs(d[1])<0.9 else np.array([1.0,0,0])); cr/=np.linalg.norm(cr)+1e-9
    return seg(h+d*0.06,h+d*0.8,0.055,RUST,0.02)+seg(h+d*0.4,h+d*0.46,0.057,RUST_D,0.022)+seg(h+d*0.05-cr*0.11,h+d*0.05+cr*0.11,0.04,(200,160,60))+seg(h-d*0.1,h+d*0.05,0.035,(84,56,34))
def boot(p,yaw):
    c=np.array(p,float); R_=Ry(yaw)
    def Wd(q): return tuple(c+R_@np.array(q,float))
    return box(-0.07,0.07,-0.06,0.05,-0.06,0.15,KBOOTS,xf=Wd)+box(-0.06,0.06,0.05,0.2,-0.06,0.05,KBOOTS,xf=Wd)
def coin(p,r=0.04): x,y,z=p; return box(x-r,x+r,y-0.01,y+0.01,z-r,z+r,GOLDC,emit=True)
def card(p,yaw): c=np.array(p,float); R_=Ry(yaw); return box(-0.07,0.07,-0.045,0.045,-0.008,0.008,CARD,xf=lambda q:tuple(c+R_@np.array(q,float)))+box(-0.07,0.07,0.02,0.03,-0.009,0.009,GOLDC,xf=lambda q:tuple(c+R_@np.array(q,float)))
def bell(p,ring=0.0):
    x,y,z=p; return box(x-0.08,x+0.08,y,y+0.03,z-0.08,z+0.08,(60,50,40))+box(x-0.06,x+0.06,y+0.03,y+0.11,z-0.06,z+0.06,(230,190,60),emit=ring>0.1)+box(x-0.015,x+0.015,y+0.11-0.02*ring,y+0.15-0.02*ring,z-0.015,z+0.015,(200,170,50))

# ======================= STORY TIMELINE =======================
VOICE=[('N1',0.05),('K1',5.0),('K2',16.0),('S1',17.0),('S2',24.0),('S3',38.3),('K3',44.6),('S4',47.0),('S5',53.6)]
HOOK=3.0
IMPACTS=[0.9,2.2,6.1,8.3,45.9]                       # skeleton hits on the barrier
FADE=(42.0,42.9); RESTORE=(45.0,45.6)
SWORD_SOLD=(26.0,27.1); BOOTS_SOLD=(27.6,29.4); APPROVED=36.6; COIN_IN=35.25; SCAN=(35.6,36.5)
GOLD_EVENTS=[(27.1,65),(29.4,90)]
NOTE_TRIAL=(15.0,18.2); TIMER=(18.2,56.4); FINAL=56.4; BLACK=58.0
KSPOT=(0.0,0,1.25); COUNTER_SPOT=(0.0,0,3.42)
SK_SPOTS=[(0.0,0,-0.62),(-0.65,0,-0.85),(0.75,0,-0.85)]
def talk(k,t):
    t0=dict(VOICE)[k]; return (0.5+0.5*math.sin(t*22)) if t0<=t<t0+SCR['dur'][k] else 0.0
def bounce(t,impacts,dur=0.45):
    best=0.0
    for ti in impacts:
        if ti<=t<ti+dur: best=max(best,1-(t-ti)/dur)
    return best

def knight_state(t):
    B=KBOOTS
    if t<1.0:                                                     # HOOK: sprints in through the door, toward the camera
        u=seg01(t,0.0,1.0); z=lerp(-0.25,1.25,1-(1-u)**1.7); return dict(base=(0.0,0,z),yaw=0.0,walk=t*15,run=1.0-seg01(t,0.75,1.0),boots=B)
    if t<3.0:                                                     # turns round to look at the door
        tu=sm(seg01(t,1.0,1.5)); return dict(base=KSPOT,yaw=lerp(0.0,PI,tu),lean=0.1*(1-tu),boots=B,rh=(0.27,1.0,0.2),lh=(-0.27,1.0,0.2))
    if t<4.7:                                                     # hands on knees, catching his breath
        k=sm(seg01(t,3.0,3.3))*(1-sm(seg01(t,4.4,4.7))); br=0.04*math.sin(t*9)
        return dict(base=KSPOT,yaw=PI,lean=0.5*k+br*k,rh=lerp3((0.27,0.86,0.04),(0.17,0.72,0.3),k),lh=lerp3((-0.27,0.86,0.04),(-0.17,0.72,0.3),k),boots=B)
    if t<12.0:                                                    # laughs at them: HA! YOU CAN'T TOUCH ME IN HERE!
        p=sm(seg01(t,4.9,5.15))*(1-sm(seg01(t,6.6,6.9))); belly=sm(seg01(t,6.8,7.1))*(1-sm(seg01(t,9.6,10.0))); sh_=0.06*math.sin(t*16)*(belly+p*0.5)
        rh=lerp3(lerp3((0.27,0.86,0.04),(0.24,1.32,0.55),p),(0.12,1.0,0.22),belly); lh=lerp3((-0.27,0.86,0.04),(-0.12,1.0,0.22),belly)
        return dict(base=KSPOT,yaw=PI,lean=-0.12*belly+sh_,rh=rh,lh=lh,head=0.1*math.sin(t*3)*belly,boots=B)
    if t<13.4:                                                    # walks to the stool and sits facing the room
        P=[KSPOT,(-1.2,0,1.9),(STOOL[0]+0.05,0,STOOL[1]-0.05)]; u=seg01(t,12.0,13.0)
        yaw=alerp(PI,path_yaw(P,u),sm(seg01(t,12.0,12.3))) if t<13.0 else alerp(path_yaw(P,1.0),PI/2,sm(seg01(t,13.0,13.3)))
        return dict(base=tuple(path3(P,u)),yaw=yaw,walk=t*8 if u<1 else 0.0,sit=sm(seg01(t,13.1,13.4)),boots=B)
    seat=(STOOL[0]+0.05,0,STOOL[1]-0.05)
    if t<20.6:                                                    # potion; FREE TRIAL? - listens
        pot=sm(seg01(t,13.7,13.95)); up=sm(seg01(t,14.1,14.4))*(1-sm(seg01(t,15.1,15.4))); away=sm(seg01(t,15.5,15.8))
        rh=lerp3(lerp3((0.27,0.86,0.04),(0.2,0.84,0.12),pot),(0.04,1.48,0.24),up); rh=lerp3(rh,(0.2,0.84,0.12),away) if t>15.5 else rh
        confused=0.25*sm(seg01(t,15.9,16.2))*(1-sm(seg01(t,16.8,17.1)))
        return dict(base=seat,yaw=PI/2,sit=1.0,rh=rh,head=confused+0.25*sm(seg01(t,17.0,17.4)),lean=-0.25*up,boots=B,potion=t>=13.9 and t<15.7)
    if t<22.1:                                                    # gets up, goes to the counter
        st_=1-sm(seg01(t,20.6,20.9)); P=[seat,(-1.0,0,2.9),COUNTER_SPOT]; u=seg01(t,20.9,22.0)
        return dict(base=tuple(path3(P,u)),yaw=alerp(PI/2,path_yaw(P,u),sm(seg01(t,20.9,21.2))) if u<1 else alerp(path_yaw(P,1.0),0.0,sm(seg01(t,21.9,22.1))),
                    sit=st_,walk=t*8 if 0<u<1 else 0.0,boots=B)
    b=COUNTER_SPOT
    if t<SWORD_SOLD[1]:                                           # checks inventory... sells the sword
        g=sm(seg01(t,SWORD_SOLD[0],SWORD_SOLD[0]+0.4)); lift=sm(seg01(t,SWORD_SOLD[0]+0.4,SWORD_SOLD[1]))
        rh=lerp3(lerp3((0.27,0.86,0.04),(-0.16,0.9,0.12),g),(0.1,1.1,0.42),lift)
        return dict(base=b,yaw=0.0,rh=rh,sword='hip' if t<SWORD_SOLD[0]+0.4 else 'none',boots=B,head=-0.15*sm(seg01(t,22.2,22.5))*(1-sm(seg01(t,24.0,24.3))))
    if t<BOOTS_SOLD[1]:                                           # bends behind the counter, comes up with his boots
        bd=sm(seg01(t,27.6,28.0))*(1-sm(seg01(t,28.2,28.6))); put=sm(seg01(t,28.9,29.3))
        hy=lerp(0.86,0.8,bd); hz=lerp(0.04,0.42,bd)
        rh=(0.15,hy,hz); lh=(-0.15,hy,hz)
        if t>=28.6: rh=lerp3((0.15,1.0,0.25),(0.18,1.12,0.5),put); lh=lerp3((-0.15,1.0,0.25),(-0.18,1.12,0.5),put)
        elif t>=28.2: rh=lerp3((0.15,0.8,0.42),(0.15,1.0,0.25),sm(seg01(t,28.2,28.6))); lh=lerp3((-0.15,0.8,0.42),(-0.15,1.0,0.25),sm(seg01(t,28.2,28.6)))
        return dict(base=b,yaw=0.0,lean=0.95*bd,rh=rh,lh=lh,sword='none',boots=B if t<28.15 else 'off',boot_hands=28.15<=t<29.3)
    BO='off'
    if t<43.5:                                                    # still short. waits at the counter, slumped
        slump=sm(seg01(t,29.9,30.4)); return dict(base=b,yaw=0.0,lean=0.12*slump,head=-0.2*slump*(1-sm(seg01(t,38.0,38.4))),sword='none',boots=BO)
    if t<44.3:                                                    # turns: a skeleton is INSIDE
        tu=sm(seg01(t,43.5,43.95)); return dict(base=b,yaw=lerp(0.0,-PI,tu),sword='none',boots=BO,rh=(0.24,lerp(0.86,1.4,tu),0.25),lh=(-0.24,lerp(0.86,1.4,tu),0.25))
    if t<52.0:                                                    # rushes back to the counter: WAIT!...
        tb=sm(seg01(t,44.3,44.6)); slam=sm(seg01(t,44.55,44.7))
        rh=lerp3((0.24,1.4,0.25),(0.22,1.16,0.5),slam); lh=lerp3((-0.24,1.4,0.25),(-0.22,1.16,0.5),slam)
        menu=sm(seg01(t,49.0,49.3)); rh=lerp3(rh,(0.1,1.25,0.3),menu)
        return dict(base=b,yaw=lerp(-PI,0.0,tb),lean=0.15*slam*(1-menu),rh=rh,lh=lh if t<49.0 else lerp3(lh,(-0.24,0.86,0.06),menu),sword='none',boots=BO,head=0.0)
    if t<55.4: return dict(base=b,yaw=0.0,sword='none',boots=BO,rh=(0.22,1.0,0.2),lh=(-0.22,1.0,0.2),head=-0.35*sm(seg01(t,52.6,53.1)))
    tu=sm(seg01(t,55.4,55.9)); return dict(base=b,yaw=lerp(0.0,PI/2,tu),sword='none',boots=BO,rh=(0.27,0.86,0.04),lh=(-0.27,0.86,0.04))   # looks straight into the camera

def skel_state(i,t):
    sx,_,sz=SK_SPOTS[i]
    if i==0:
        if t<0.9: u=seg01(t,0.0,0.9); return dict(base=(0.0,0,lerp(-1.6,-0.62,u)),yaw=0.0,walk=t*15,run=1.0,rage=1.0,jaw=0.5,sdir=(0.0,1.0,-0.25))
    if i==1 and t<4.2: u=seg01(t,2.4,4.2); return dict(base=(lerp(-1.2,sx,sm(u)),0,lerp(-5.5,sz,u)),yaw=0.0,walk=t*10,rage=1.0,jaw=0.3)
    if i==2 and t<4.0: u=seg01(t,2.0,4.0); return dict(base=(lerp(1.4,sx,sm(u)),0,lerp(-5.8,sz,u)),yaw=0.0,walk=t*10,rage=1.0,jaw=0.3)
    hit=bounce(t,[x for x in IMPACTS if x<12 and i==0]+([45.9] if i==1 else []),0.6)
    if i==0 and t<12:                                             # bangs on the barrier, bounces back
        z=SK_SPOTS[0][2]+0.2*hit if t>1.5 else lerp(-0.42,-0.62,sm(seg01(t,0.9,1.4))) if t>=0.9 else -0.62
        nxt=[x for x in IMPACTS if x>t and x<12]
        wind=min(1.0,(nxt[0]-t)/0.18) if nxt else 1.0
        fw=min(0.62,BAR_Z-0.06-z)                                          # palms stop at the barrier
        return dict(base=(0.0,0,z),yaw=0.0,rh=(0.24,1.25,lerp(fw,0.2,wind) if t>1.0 else 0.2),lh=(-0.24,1.35,lerp(fw,0.2,wind) if t>1.0 else 0.2),
                    sdir=(0.0,1.0,-0.25),rage=1.0,jaw=0.5+0.5*math.sin(t*20) if t<12 else 0.0)
    if t<12.0:                                                    # furious: shaking fists, chattering jaw
        return dict(base=SK_SPOTS[i],yaw=0.0,rh=(0.24,1.5+0.08*math.sin(t*14+i),0.25),lh=(-0.24,1.45+0.08*math.sin(t*14+i+1),0.25),sdir=(0.0,1.0,0.1),rage=1.0,jaw=0.5+0.5*math.sin(t*18+i))
    if i==2 and t>=33.0: return premium_state(t)
    if i==1 and 45.4<=t<46.6:                                     # tries to follow the premium one... bonk
        u=sm(seg01(t,45.4,45.88))*(1-sm(seg01(t,45.95,46.5))); return dict(base=(lerp(sx,-0.25,u),0,lerp(sz,-0.5,u)),sdir=(0.0,1.0,0.1),yaw=alerp(0.0,0.35,u),walk=t*8 if 0.05<u<0.95 else 0.0,rage=1.0,jaw=0.6)
    wait=0.04*math.sin(t*2+i)                                     # impatient waiting outside
    if i==0 and t>=42.2:                                          # steps back to let the premium customer through
        u=sm(seg01(t,42.2,42.9)); return dict(base=(lerp(0.0,0.05,u),0,lerp(SK_SPOTS[0][2],-1.45,u)),yaw=0.0,walk=t*6 if 0.02<u<0.98 else 0.0,rh=(0.12,1.15,0.14),lh=(-0.12,1.12,0.16),sdir=(0.9,-0.2,0.2),jaw=0.1)
    if i==0: return dict(base=SK_SPOTS[0],yaw=0.0,rh=(0.12,1.15,0.14),lh=(-0.12,1.12,0.16),sdir=(0.9,-0.2,0.2),head=wait,jaw=0.1)       # arms crossed-ish
    return dict(base=SK_SPOTS[i],yaw=0.0,walk=0.35*math.sin(t*7) if 32<t<40 else 0.0,head=wait,jaw=0.1)
PREM_AT=(TERM[0],0,TERM[1]-0.5)
PIN=[(0.75,0,-0.85),(0.6,0,-0.55),(0.4,0,0.8),(0.25,0,1.9)]
def premium_state(t):
    if t<34.3:
        P=[SK_SPOTS[2],(1.2,0,-1.05),PREM_AT]; u=seg01(t,33.0,34.0)
        return dict(base=tuple(path3(P,u)),yaw=alerp(alerp(0.0,path_yaw(P,min(u,0.7)),sm(seg01(t,33.0,33.25))),0.0,sm(seg01(t,33.8,34.25))),walk=t*8 if u<0.88 else 0.0)
    st=dict(base=PREM_AT,yaw=0.0)
    if t<SCAN[1]+0.3:                                             # left hand: coin from the pouch into the slot, then the card on the screen
        POUCH=(-0.12,0.9,-0.16); HIPC=(-0.24,0.88,0.0); REST=(-0.26,0.88,0.06)
        K=[(34.3,REST),(34.6,POUCH),(34.75,POUCH),(COIN_IN,sk_local(st,TERM_SLOT)),(35.4,sk_local(st,TERM_SLOT)),(SCAN[0],HIPC),(SCAN[0]+0.15,HIPC),
           (SCAN[0]+0.55,sk_local(st,TERM_SCREEN)),(SCAN[1],sk_local(st,TERM_SCREEN)),(SCAN[1]+0.3,REST)]
        lh=REST
        for (t0,p0),(t1,p1) in zip(K,K[1:]):
            if t0<=t<t1: lh=lerp3(p0,p1,sm(seg01(t,t0,t1))); break
        return dict(st,lh=tuple(lh),sdir=(0.0,-1.0,-0.15),card=not (SCAN[0]+0.15<=t<SCAN[1]+0.15),coin=34.75<=t<COIN_IN)
    if t<FADE[1]-0.5:                                             # waits for the barrier to drop, waits for the barrier to drop
        return dict(base=PREM_AT,yaw=0.0,sdir=(0.0,-1.0,-0.15),jaw=0.0,head=0.3*sm(seg01(t,37.0,37.5))*(1-sm(seg01(t,40.5,41.0))))
    P=[PREM_AT,(1.25,0,-1.0)]+PIN[1:]                              # steps back from the terminal, then to the door
    if t<45.3: u=seg01(t,FADE[1]-0.1,45.3); return dict(base=tuple(path3(P,u)),yaw=alerp(0.0,path_yaw(P,max(u,0.03)),sm(seg01(t,FADE[1]-0.5,FADE[1]-0.1))),walk=t*7 if u>0 else 0.0,sdir=(0.0,-1.0,-0.15) if u<0.3 else (0.0,-1.0,0.35))
    if t<52.0: return dict(base=PIN[-1],yaw=path_yaw(P,1.0)*(1-sm(seg01(t,45.3,45.8))),jaw=0.15*math.sin(t*3))
    u=seg01(t,52.0,55.0); up=sm(seg01(t,54.2,54.7)); return dict(base=tuple(lerp3(PIN[-1],(0.18,0,2.72),u)),yaw=0.0,walk=t*4 if u<1 else 0.0,rh=lerp3((0.26,0.9,0.14),(0.28,1.6,0.05),up),sdir=lerp3((0.0,-1.0,0.25),(0.0,1.0,0.05),up),rage=0.6)

def keeper_state(t):
    st=dict(base=KEEPER,yaw=PI,smile=1.0,mouth=max(talk(k,t) for k in ('S1','S2','S3','S4','S5')),blink=1.0 if int(t*10)%37==0 else 0.0)
    if 10.4<=t<12.0: st['rh']=(0.24,1.5,0.3+0.06*math.sin(t*10))                                         # little wave
    if 17.0<=t<19.6: st['rh']=(0.2,1.2+0.05*math.sin(t*6),0.36); st['head']=0.12*math.sin(t*2)
    if 24.0<=t<26.9: st['rh']=(0.14,1.25,0.4)                                                          # points at the sword / boots
    if 38.3<=t<40.0: st['head']=0.25; st['lh']=(-0.18,1.18,0.32)
    if 52.6<=t<53.5:                                                                                    # rings the service bell
        st0=dict(st); tap=sm(seg01(t,52.75,52.95))*(1-sm(seg01(t,53.05,53.35)))
        bl=np.array(kp_local(st0,(BELL[0],BELL[1]+0.17,BELL[2]))); st['lh']=tuple(np.array((-0.2,1.02,0.3))*(1-tap)+bl*tap) if False else st.get('lh')
        st['rh']=tuple(lerp3((0.2,1.02,0.3),kp_local(st0,(BELL[0],BELL[1]+0.17,BELL[2])),tap))
    return st
def bell_ring(t): return bounce(t,[52.95],0.6)

# ======================= SHOTS =======================
def hook_shot(t): u=sm(seg01(t,0,HOOK)); return dict(cam=lerp3((0.55,1.25,2.65),(0.5,1.3,2.45),u),tgt=(0.0,1.05,-0.8),fov=62)
def shot(V):
    if V<HOOK: return hook_shot(V)
    if V<7.6:  u=sm(seg01(V,3.0,7.6)); return dict(cam=lerp3((-1.75,1.45,2.35),(-1.7,1.45,2.25),u),tgt=(0.25,1.0,0.3),fov=62)
    if V<10.3: u=sm(seg01(V,7.6,10.3)); return dict(cam=lerp3((0.0,3.1,-3.6),(0.0,3.05,-3.4),u),tgt=(0.0,1.1,1.25),fov=46)       # over the skeletons' heads
    if V<12.0: return dict(cam=(0.45,1.55,2.95),tgt=(0.0,1.42,4.85),fov=48)
    if V<15.0: u=sm(seg01(V,12.0,15.0)); return dict(cam=lerp3((0.95,1.35,0.6),(0.85,1.35,0.75),u),tgt=(-1.9,0.9,2.3),fov=60)
    if V<17.0: return dict(cam=(-0.6,1.15,2.05),tgt=(-1.9,1.0,2.3),fov=50)
    if V<20.4: return dict(cam=(-1.2,1.5,3.05),tgt=(0.0,1.45,4.85),fov=52)
    if V<22.0: return dict(cam=(1.4,1.5,1.2),tgt=(-0.6,1.0,2.9),fov=62)
    if V<32.0: u=sm(seg01(V,22.0,32.0)); return dict(cam=lerp3((0.8,1.72,5.45),(0.75,1.7,5.35),u),tgt=(0.0,1.25,3.3),fov=58)
    if V<36.0: return dict(cam=(-1.3,1.55,-3.2),tgt=(0.8,1.05,-0.6),fov=60)
    if V<37.8: return dict(cam=(0.85,1.35,-1.05),tgt=(TERM[0],1.15,TERM[1]-0.15),fov=44)
    if V<42.0: return dict(cam=(1.3,1.6,3.6),tgt=(0.0,1.45,4.85),fov=50)
    if V<45.5: return dict(cam=(-1.3,1.75,3.2),tgt=(0.3,1.05,0.4),fov=60)
    if V<52.0: return dict(cam=(0.8,1.72,5.45),tgt=(0.0,1.25,3.3),fov=58)
    if V<55.3: return dict(cam=(1.7,1.5,1.95),tgt=(-0.2,1.2,3.45),fov=60)
    return dict(cam=(1.55,1.55,3.45),tgt=(0.0,1.45,3.42),fov=46)

# ======================= RENDER =======================
R=Renderer(W,H,fog=(14,12,16))
def barrier_alpha(t):
    if t<FADE[0]: return 1.0
    if t<RESTORE[0]: return 1-sm(seg01(t,FADE[0],FADE[1]))
    return sm(seg01(t,RESTORE[0],RESTORE[1]))
def props(V,ks,sks,kp):
    Q=terminal('ok' if V>=APPROVED else ('busy' if V>=COIN_IN else 'idle'))+sign_coin()+bell(BELL,bell_ring(V))
    if ks.get('potion'): Q+=potion(np.array(khand(ks,1))+np.array([0,0.05,0]))
    s0,s1=SWORD_SOLD
    if s0+0.4<=V<s1: h=np.array(khand(ks,1)); Q+=rusty_sword(h,(0.25,0.25,-0.1) if V<s0+0.8 else (1.0,0.05,0.05))
    if V>=s1: Q+=rusty_sword((0.75,1.04,4.08),(-1.0,0.0,0.05))
    if ks.get('boot_hands'):
        for sd in (1,-1): Q+=boot(np.array(khand(ks,sd))+np.array([0,-0.12,0]),ks['yaw'])
    if V>=BOOTS_SOLD[1]: Q+=boot((-0.55,1.06,4.1),0.3)+boot((-0.35,1.06,4.08),-0.2)
    ps=sks[2]
    if ps.get('coin'): Q+=coin(skhand(ps,-1))
    if SCAN[0]+0.15<=V<SCAN[1]+0.15: Q+=card(skhand(ps,-1),ps['yaw'])
    return Q
def render(V,sh):
    cam=Camera.look(sh['cam'],sh['tgt'])
    ks=knight_state(V); sks=[skel_state(i,V) for i in range(3)]; kp=keeper_state(V)
    layers=[SHOP,torches(V),prelit(knight(**ks),sh['cam'],warm=0.12),keeper(**{k:v for k,v in kp.items() if k in KP_KEYS})]
    for s_ in sks: layers.append(skeleton(**{k:v for k,v in s_.items() if k in SK_KEYS}))
    layers.append(props(V,ks,sks,kp))
    img,vi,zb=zrender(R,cam,layers,lights(V),fov=sh['fov'],fog_start=8,fog_end=26,ambient=0.3,return_z=True)
    fl=bounce(V,IMPACTS,0.6); src=max([x for x in IMPACTS if x<=V] or [-9]); rc=(0.0,1.3)
    tint=CYAN; flash=fl; rr=(V-src)*4.0
    if V<0.45: flash=0.6*math.sin(PI*seg01(V,0.05,0.45)); rc=(0.0,1.0); rr=V*4; tint=(120,255,160)           # lets the knight in
    al=barrier_alpha(V)
    if FADE[0]<=V<FADE[1]: flash=0.5*math.sin(PI*seg01(V,FADE[0],FADE[1])); rc=(0.0,1.2); rr=(V-FADE[0])*3; tint=(255,200,80)
    if al>0.01 or flash>0.01:
        bimg,_,bz=zrender(R,cam,[barrier_quads(max(al,0.0),flash,rc,rr,tint)],[],fov=sh['fov'],fog_start=8,fog_end=26,return_z=True)
        m=(bz>zb)&(bz>0); a=np.asarray(img).astype(np.float32); b=np.asarray(bimg).astype(np.float32)-np.array(R.fog,np.float32)
        img=Image.fromarray(np.where(m[...,None],np.clip(a+np.clip(b,0,255),0,255),a).astype(np.uint8))
    return post.ps1(img),vi

# ======================= UI overlays =======================
otext=GF.otext; wrap=GF.wrap
HOOK_LINES=['WHY DO','MONSTERS NEVER','ATTACK YOU','INSIDE SHOPS?']
HIL={'MONSTERS','NEVER','SHOPS?','HA!',"CAN'T",'TOUCH','FREE','TRIAL?','PROTECTION',"ISN'T",'FREE','FOREVER.','RUSTY','SWORD.','BOOTS!','PREMIUM','CUSTOMER.','MONSTERS','PAY','ENTER?!','SERVICE.','UPGRADE?'}
SPK={'N':(None,WHT),'K':('KNIGHT:',BLU),'S':('SHOPKEEPER:',GRN)}
def subtitle(d,V):
    cur=None
    for k,t0 in VOICE:
        if (t0<=V or k=='N1') and V<t0+SCR['dur'][k]+0.15: cur=k
    if cur is None or V>=FINAL: return
    if cur=='N1':
        y=18
        for ln in HOOK_LINES:
            x=(W-font.width(ln,2))//2
            for wd in ln.split(' '): otext(d,wd,x,y,YEL if wd in HIL else WHT,2); x+=font.width(wd,2)+12
            y+=18
        return
    name,col=SPK[cur[0]]; txt=SCR['text'][cur].upper()
    lines=wrap(((name+' ') if name else '')+txt); y=268-11*(len(lines)-1)
    for ln in lines:
        xw=font.width(ln); x=(W-xw)//2; d.rectangle([x-3,y-2,x+xw+2,y+8],fill=(0,0,0)); cx=x
        for wd in ln.split(' '): otext(d,wd,cx,y,col if wd==name else (YEL if wd in HIL else WHT)); cx+=font.width(wd)+6
        y+=11
def panel(d,x0,y0,x1,y1,col):
    d.rectangle([x0,y0,x1,y1],fill=(12,10,30),outline=col); d.rectangle([x0+2,y0+2,x1-2,y1-2],outline=tuple(int(c*0.5) for c in col))
def gold_value(t):
    g=20
    for te,v in GOLD_EVENTS:
        if t>=te: g=v
        elif t>=te-0.4: g=int(lerp(g,v,seg01(t,te-0.4,te)))
    return g
def ui(d,V):
    if V>=BLACK: return
    if NOTE_TRIAL[0]<=V<NOTE_TRIAL[1]:                                    # SAFE ZONE FREE TRIAL notification
        y=int(lerp(-40,40,sm(seg01(V,NOTE_TRIAL[0],NOTE_TRIAL[0]+0.25)))); panel(d,6,y,W-6,y+40,CYAN)
        otext(d,'SAFE ZONE FREE TRIAL:',12,y+6,CYAN); otext(d,'30 SECONDS',12,y+17,YEL,1); otext(d,'REMAINING',12,y+28,WHT)
    if TIMER[0]<=V<FINAL:                                                 # trial timer badge
        sec=int(math.ceil(30*(1-seg01(V,TIMER[0],TIMER[1])))); col=RED if sec<=10 and int(V*4)%2 else (YEL if sec>10 else RED)
        panel(d,4,6,72,28,col); otext(d,'FREE TRIAL',9,9,WHT); otext(d,f'0:{sec:02d}',9,18,col)
    if V>=22.0 and V<FINAL:                                               # gold counter
        g=gold_value(V); col=RED if (29.8<=V<32.0 and int(V*5)%2) else YEL
        panel(d,W-62,6,W-4,28,col); otext(d,'GOLD',W-57,9,WHT); otext(d,f'{g}/100',W-57,18,col)
        for te,v in GOLD_EVENTS:
            if te<=V<te+0.9: otext(d,f'+{v-(20 if v==65 else 65)}',W-40,32+int(-8*seg01(V,te,te+0.9)),GRN)
    if 22.2<=V<25.6:                                                      # inventory / renewal price
        panel(d,14,70,W-14,150,YEL); otext(d,'INVENTORY',(W-font.width('INVENTORY'))//2,76,YEL)
        for i,(a,b) in enumerate((('GOLD','20'),('RUSTY SWORD','X1'),('OLD BOOTS','X1'))): otext(d,a,22,92+i*11,WHT); otext(d,b,W-22-font.width(b),92+i*11,GRY)
        otext(d,'RENEW SAFE ZONE:',22,128,CYAN); otext(d,'100 GOLD',W-22-font.width('100 GOLD'),138,RED)
    for (t0,t1),lab,val in ((SWORD_SOLD,'RUSTY SWORD',45),(BOOTS_SOLD,'OLD BOOTS',25)):
        if t1-0.2<=V<t1+1.1: s_=f'SOLD: {lab} +{val}'; panel(d,(W-font.width(s_))//2-6,64,(W+font.width(s_))//2+6,80,GRN); otext(d,s_,(W-font.width(s_))//2,69,GRN)
    if 29.9<=V<32.0: s_='STILL 10 GOLD SHORT'; otext(d,s_,(W-font.width(s_))//2,90,RED)
    if APPROVED<=V<39.2:                                                  # terminal result
        y=int(lerp(-40,70,sm(seg01(V,APPROVED,APPROVED+0.2)))); panel(d,6,y,W-6,y+34,GRN)
        otext(d,'MONSTER PREMIUM ACCESS:',(W-font.width('MONSTER PREMIUM ACCESS:'))//2,y+7,WHT); otext(d,'APPROVED',(W-font.width('APPROVED',2))//2,y+18,GRN,2)
    elif SCAN[0]<=V<APPROVED: s_='SCANNING...'; otext(d,s_,(W-font.width(s_))//2,80,YEL)
    if 49.2<=V<52.4:                                                      # subscription menu
        panel(d,14,70,W-14,140,CYAN); otext(d,'SAFE ZONE PREMIUM',(W-font.width('SAFE ZONE PREMIUM'))//2,77,CYAN)
        otext(d,'PRICE: 100 GOLD',22,93,WHT); otext(d,'YOU HAVE: 90',22,104,WHT)
        if V>=50.1: s_='INSUFFICIENT GOLD'; d.rectangle([20,118,W-20,132],fill=(70,10,10)); otext(d,s_,(W-font.width(s_))//2,122,RED)
        else: otext(d,'- RENEW -',22,120,YEL if int(V*4)%2 else WHT)
    if FINAL<=V<BLACK:                                                    # the punchline
        pop=sm(seg01(V,FINAL,FINAL+0.15)); y=int(lerp(400,200,pop)); panel(d,4,y,W-4,y+58,RED)
        for i,ln in enumerate(('YOUR FREE','TRIAL HAS','ENDED.')): otext(d,ln,(W-font.width(ln,2))//2,y+6+i*17,WHT if i<2 else RED,2)
def emotes(d,vi,V,ks,sks):
    if 43.6<=V<44.5:
        top=np.array(kpoint(ks,(0,1.95,0))); GF.emote(d,vi,top,'!',RED) if False else None
        p=R.project(tuple(top),vi)
        if p: x,y=int(p[0]),int(p[1]); d.rectangle([x-6,y-10,x+6,y+8],fill=WHT,outline=(0,0,0)); font.text(d,'!',x-2,y-7,RED,1,None)
    if 16.0<=V<16.9:
        top=np.array(kpoint(ks,(0,1.95,0))); p=R.project(tuple(top),vi)
        if p: x,y=int(p[0]),int(p[1]); d.rectangle([x-6,y-10,x+6,y+8],fill=WHT,outline=(0,0,0)); font.text(d,'?',x-2,y-7,BLU,1,None)
    if 52.95<=V<53.6:                                                     # 'ding!'
        p=R.project(tuple(np.array(BELL)+np.array([0,0.3,0])),vi)
        if p: otext(d,'DING!',int(p[0])-14,int(p[1])-8,YEL)
def frame(V):
    if V>=BLACK:
        img=Image.new('RGB',(W,H),(0,0,0)); return img
    sh=shot(V); img,vi=render(V,sh); d=ImageDraw.Draw(img)
    ks=knight_state(V); sks=[skel_state(i,V) for i in range(3)]
    emotes(d,vi,V,ks,sks); ui(d,V); subtitle(d,V)
    return img

# ======================= QA manifest =======================
def _kn(t): return {k:v for k,v in knight_state(t).items() if k in KN_KEYS}
def _sk(i): return lambda t: {k:v for k,v in skel_state(i,t).items() if k in SK_KEYS}
def _kp(t): return {k:v for k,v in keeper_state(t).items() if k in KP_KEYS}
CROSS={'knight':[(0.0,0.55)],'skel2':[(FADE[1]-0.1,45.0)]}
def _geom(t,name,st,V):
    out=[]
    if V[:,1].min()<-0.04: out.append(('floor',f'{name} under the floor'))
    inside=st['base'][2]>0.0
    if inside:
        if (np.abs(V[:,0])>SX-0.02).any() or (V[:,2]>BACKZ-0.02).any(): out.append(('wall',f'{name} inside a shop wall'))
        if name!='keeper':
            x0,x1,z0,z1,h=COUNTER; m=(V[:,0]>x0+0.02)&(V[:,0]<x1-0.02)&(V[:,2]>z0+0.02)&(V[:,2]<z1-0.02)&(V[:,1]<h-0.02)
            if m.any(): out.append(('intersect',f'{name} inside the counter'))
        sx,sz=STOOL
        if name!='knight' and ((np.abs(V[:,0]-sx)<0.2)&(np.abs(V[:,2]-sz)<0.2)&(V[:,1]<0.45)).any(): out.append(('intersect',f'{name} inside the stool'))
    else:
        if (np.abs(V[:,0])>2.4-0.02).any(): out.append(('wall',f'{name} inside a corridor wall'))
        x,z=TERM; m=(np.abs(V[:,0]-x)<0.18)&(V[:,2]>z-0.14)&(V[:,2]<z+0.05)&(V[:,1]<1.33)
        if m.any(): out.append(('intersect',f'{name} inside the terminal'))
    side=(np.abs(V[:,0])>DOOR_W+0.02)&(V[:,2]>-0.24)&(V[:,2]<0.28)
    if side.any(): out.append(('wall',f'{name} inside the front wall / door frame'))
    allowed=any(a<=t<=b for a,b in CROSS.get(name,[]))
    if not allowed and name!='keeper':
        door=np.abs(V[:,0])<DOOR_W
        if inside and door.any() and V[door,2].min()<BAR_Z-0.03: out.append(('barrier',f'{name} reaches through the barrier from inside'))
        if (not inside) and door.any() and V[door,2].max()>BAR_Z+0.03 and barrier_alpha(t)>0.5: out.append(('barrier',f'{name} reaches through the barrier from outside'))
    return out
def _extra(t):
    out=[]; ks=knight_state(t); ps=skel_state(2,t)
    if abs(t-COIN_IN)<0.5/FPS and np.linalg.norm(np.array(skhand(ps,-1))-np.array(TERM_SLOT))>0.08: out.append(('terminal','coin is not at the slot when it goes in'))
    if abs(t-(SCAN[0]+0.6))<0.5/FPS and np.linalg.norm(np.array(skhand(ps,-1))-np.array(TERM_SCREEN))>0.12: out.append(('terminal','card is not on the screen when it scans'))
    if FADE[1]<=t and ps['base'][2]>BAR_Z and t<FADE[1]-0.01: out.append(('barrier','skeleton enters before the barrier is gone'))
    if ps['base'][2]>-0.15 and t<FADE[1]: out.append(('barrier','premium skeleton reaches the door before the barrier is gone'))
    for nm,st_,pt,hand_,L_ in (('knight',ks,kpoint,khand,0.66),('skel2',ps,skpoint,skhand,0.66)):
        for sx in (-1,1):
            sh_=np.array(pt(st_,(sx*(0.22 if nm=='knight' else 0.24),1.27 if nm=='knight' else 1.45,0))); dd=np.linalg.norm(np.array(hand_(st_,sx))-sh_)
            if dd>L_: out.append(('stretch',f'{nm} arm stretched beyond its length ({dd:.2f} m)'))
    return out
QA=dict(fps=FPS,dur=BLACK,W=W,frame=frame,
    chars={'knight':(_kn,knight,'sword','hip'),'skel0':(_sk(0),skeleton,'card',True),'skel1':(_sk(1),skeleton,'card',True),'skel2':(_sk(2),skeleton,'card',True),
           'keeper':(_kp,keeper,'smile',1.0)},
    geom=_geom,extra=_extra,camera=lambda t: shot(t)['cam'],min_cam_dist=0.45,
    camera_ok=lambda p: (abs(p[0])<SX-0.1 and 0.1<p[2]<BACKZ-0.1 and 0.1<p[1]<3.3) or (abs(p[0])<2.3 and -6.9<p[2]<-0.1 and 0.1<p[1]<3.3),
    scenes=[dict(id='hook',t0=0.0,t1=HOOK,action='knight sprints into the shop; skeleton slams into the barrier'),
            dict(id='breath',t0=HOOK,t1=7.6,action='knight catches his breath; two more skeletons arrive; HA! you cant touch me'),
            dict(id='laugh',t0=7.6,t1=10.3,action='from outside: furious skeletons, laughing knight behind the barrier'),
            dict(id='keeper-smile',t0=10.3,t1=12.0,action='shopkeeper smiles and waves'),
            dict(id='stool',t0=12.0,t1=17.0,action='knight sits, drinks a potion; FREE TRIAL notification; Free trial?'),
            dict(id='explain',t0=17.0,t1=20.4,action='shopkeeper: protection isnt free forever'),
            dict(id='to-counter',t0=20.4,t1=22.0,action='knight goes to the counter'),
            dict(id='sell',t0=22.0,t1=32.0,action='inventory; sells sword (+45) and boots (+25); still 10 short'),
            dict(id='outside',t0=32.0,t1=36.0,action='skeleton walks to the terminal, pays a coin'),
            dict(id='scan',t0=36.0,t1=37.8,action='insert: card scan, PREMIUM ACCESS APPROVED'),
            dict(id='premium',t0=37.8,t1=42.0,action='shopkeeper: a premium customer'),
            dict(id='enter',t0=42.0,t1=45.5,action='barrier fades, skeleton walks in, barrier returns'),
            dict(id='argue',t0=45.5,t1=52.0,action='WAIT! you let monsters pay?; subscription menu: INSUFFICIENT GOLD'),
            dict(id='bell',t0=52.0,t1=55.3,action='skeleton approaches; shopkeeper rings the bell: upgrade?'),
            dict(id='final',t0=55.3,t1=BLACK,action='knight looks at the camera; YOUR FREE TRIAL HAS ENDED')],
    weapon_events=[('knight',SWORD_SOLD[0]+0.4,'hip','none'),('skel2',SCAN[0]+0.15,True,False),('skel2',SCAN[1]+0.15,False,True)],
    texts=lambda: [(k,ln,1) for k in SCR['text'] for ln in wrap((SPK[k[0]][0]+' ' if SPK[k[0]][0] else '')+SCR['text'][k].upper())]+[('N1',x,2) for x in HOOK_LINES]
          +[('ui',s_,1) for s_ in ('- RENEW -','SAFE ZONE FREE TRIAL:','SOLD: RUSTY SWORD +45','SOLD: OLD BOOTS +25','STILL 10 GOLD SHORT','MONSTER PREMIUM ACCESS:','INSUFFICIENT GOLD','SAFE ZONE PREMIUM','RENEW SAFE ZONE:')]
          +[('ui',s_,2) for s_ in ('APPROVED','YOUR FREE','TRIAL HAS','ENDED.')])

TEST=os.environ.get('TEST')
if TEST and __name__=='__main__':
    ims=[frame(float(x)) for x in TEST.split(',')]; shp=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): shp.paste(im,(i*182,0))
    shp.resize((shp.width*2,640),Image.NEAREST).save('test.png'); sys.exit()

# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=53); sr=s.sr; n=s.n; M=np.zeros(n); AMB=np.zeros(n)
    def note(buf,t0,m,d,v,wave='sq',duty=0.5,dec=3.0,att=0.005):
        f=440*2**((m-69)/12); tt=s.T(d); ph=(f*tt)%1
        x=np.where(ph<duty,1.0,-1.0) if wave=='sq' else (4*np.abs(ph-0.5)-1 if wave=='tri' else np.sin(2*np.pi*ph))
        env=np.minimum(1,tt/att)*np.exp(-tt*dec); i=int(t0*sr); j=min(n,i+len(tt)); buf[i:j]+=(x*env*v)[:j-i]
    def nb(t0,d,lo,hi,v,seed,shape=2): s.place(s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v)
    def rattle(t0,d=0.4,v=0.03,seed=0):
        r=np.random.default_rng(seed)
        for k in range(int(d/0.035)): tt=s.T(0.03); s.place(s.filt_short(s.noise(0.03,seed*50+k),lo=1500,hi=6000)*np.exp(-tt*120),t0+k*0.035+r.uniform(0,0.01),v*r.uniform(0.5,1))
    def zap(t0,v=0.2,seed=0):
        tt=s.T(0.6); s.place(np.sin(2*np.pi*np.cumsum(1200*np.exp(-tt*6)+180)/sr)*np.exp(-tt*6)*0.6+s.filt_short(s.noise(0.6,seed),lo=2000,hi=9000)*np.exp(-tt*16)*0.4,t0,v)
    def step(t0,v=0.04,seed=0,lo=300,hi=2500): tt=s.T(0.08); s.place(s.filt_short(s.noise(0.08,seed),lo=lo,hi=hi)*np.exp(-tt*60),t0,v)
    def coinsnd(t0,v=0.04,seed=0):
        r=np.random.default_rng(seed); tt=s.T(0.3)
        for f in (r.uniform(2800,3400),r.uniform(4300,5000)): s.place(np.sin(2*np.pi*f*tt)*np.exp(-tt*14),t0,v)
    def register(t0,v=0.08):
        tt=s.T(0.5); s.place(sum(np.sin(2*np.pi*f*tt)*np.exp(-tt*k) for f,k in ((420,10),(1100,14)))*0.3+s.filt_short(s.noise(0.5,int(t0)),lo=2000,hi=7000)*np.exp(-tt*35),t0,v*0.6)
        tt=s.T(1.0); s.place((np.sin(2*np.pi*1568*tt)+0.8*np.sin(2*np.pi*2093*tt))*np.exp(-tt*4),t0+0.08,v)
    def blip(t0,m,v=0.03,d=0.08): note(M,t0,m,d,v,'sq',0.25,18)
    def bellsnd(t0,v=0.08): tt=s.T(1.4); s.place((np.sin(2*np.pi*2350*tt)+0.6*np.sin(2*np.pi*3520*tt)+0.3*np.sin(2*np.pi*5600*tt))*np.exp(-tt*3.5),t0,v)
    AMB+=s.filt(s.rng.normal(0,1,n),lo=60,hi=600)*0.01
    # ---------- music: a cosy shop jingle that turns sour ----------
    def jingle(a,b,v=1.0,root=60,minor=False,step=0.18):
        sc=[0,2,3,5,7,8,10,12] if minor else [0,2,4,5,7,9,11,12]; pat=[0,2,4,7,4,2,5,4,0,2,4,7,9,7,5,4]; bass=[0,0,5,5,3,3,4,4]; k=0; tc=a
        while tc<b-1e-6:
            note(M,tc,root+12+sc[pat[k%16]%8],step*0.7,0.02*v,'sq',0.25,10)
            if k%2==0: note(M,tc,root-12+sc[bass[(k//2)%8]%8],step*1.6,0.045*v,'tri',dec=5)
            k+=1; tc+=step
    def chase(a,b,v=1.0):
        k=0; tc=a
        while tc<b-1e-6:
            note(M,tc,[76,79,76,82,81,79][k%6],0.1,0.026*v,'sq',0.5,10)
            if k%2==0: note(M,tc,40 if (k//6)%2==0 else 38,0.18,0.06*v,'tri',dec=5)
            k+=1; tc+=0.13
    chase(0.0,0.95)
    jingle(3.0,12.0,0.8)
    jingle(12.0,15.0,0.6,step=0.22)
    for k,m in enumerate((84,79,84,91)): note(M,15.0+k*0.08,m,0.12,0.03,'sq',0.25,8)          # notification
    jingle(17.0,22.0,0.6,step=0.2)
    jingle(22.0,32.0,0.8,root=57,minor=True,step=0.16)             # the panic
    for k,m in enumerate((64,63,62,61)): note(M,29.9+k*0.16,m,0.18,0.035,'sq',0.5,6)           # still short
    jingle(32.0,36.6,0.6,root=57,minor=True,step=0.2)
    for k,m in enumerate((72,76,79,84,88)): note(M,APPROVED+k*0.07,m,0.2,0.035,'sq',0.25,6)     # approved
    jingle(37.5,42.0,0.7)                                           # shopkeeper delighted (cosy tune again)
    for k,m in enumerate((79,74,70,67)): note(M,42.0+k*0.18,m,0.3,0.03,'tri',dec=4)            # barrier powers down
    jingle(44.5,52.5,0.9,root=57,minor=True,step=0.13)
    for k,m in enumerate((52,52,52)): note(M,50.1+k*0.12,m,0.1,0.05,'sq',0.5,10)               # INSUFFICIENT
    jingle(53.0,FINAL,0.6,step=0.2)
    M[int(FINAL*sr):]=0
    # ---------- sfx ----------
    for k in range(8): step(0.02+k*0.12,0.05,k)                     # knight sprinting
    s.place(np.sin(2*np.pi*np.cumsum(500+700*s.T(0.4))/sr)*np.exp(-s.T(0.4)*6),0.1,0.03)       # barrier lets him in
    for k,t0 in enumerate(IMPACTS): zap(t0,0.22 if k<4 else 0.18,k); rattle(t0+0.05,0.35,0.04,k)
    rattle(2.4,1.8,0.015,20); rattle(2.0,2.0,0.015,21)               # two more skeletons arrive
    for t0 in np.arange(4.9,7.0,0.25): nb(t0,0.12,300,1500,0.015,int(t0*10))                    # laughing
    for k in range(6): rattle(7.6+k*0.7,0.3,0.02,30+k)              # furious chattering
    for k in range(5): step(12.05+k*0.22,0.035,40+k)
    nb(13.95,0.6,200,1200,0.03,45)                                  # gulp
    for k in range(5): step(20.95+k*0.22,0.035,50+k)
    nb(22.2,0.3,1000,5000,0.02,55)                                  # inventory open
    nb(SWORD_SOLD[0]+0.4,0.4,2000,8000,0.03,56); register(SWORD_SOLD[1]); [coinsnd(SWORD_SOLD[1]+0.1+0.05*k,0.03,60+k) for k in range(5)]
    nb(28.1,0.4,300,2000,0.03,57); register(BOOTS_SOLD[1]); [coinsnd(BOOTS_SOLD[1]+0.1+0.05*k,0.03,70+k) for k in range(3)]
    for k in range(5): step(33.0+k*0.22,0.03,80+k,lo=1200,hi=5000); rattle(33.0+k*0.22,0.1,0.01,80+k)
    coinsnd(COIN_IN,0.05,90); nb(COIN_IN+0.02,0.15,1500,5000,0.02,91)
    for k in range(4): blip(SCAN[0]+k*0.2,88,0.025)
    for k in range(5): step(42.9+k*0.48,0.03,100+k,lo=1200,hi=5000)
    zap(45.9,0.15,110); rattle(45.95,0.4,0.04,111)                   # the other skeleton bonks
    nb(44.6,0.2,200,1500,0.06,112)                                  # slams the counter
    bellsnd(52.95,0.09)
    for k in range(4): step(52.1+k*0.75,0.03,120+k,lo=1200,hi=5000)
    nb(54.3,0.3,1500,6000,0.03,125)                                 # sword raised
    for k in range(int((FINAL-TIMER[0])/1.0)): s.place(np.sin(2*np.pi*1900*s.T(0.02))*np.exp(-s.T(0.02)*150),TIMER[0]+k*1.0,0.012 if k<28 else 0.03)
    for k,m in enumerate((60,55,52,48)): note(M,FINAL+k*0.11,m,0.15 if k<3 else 0.5,0.05,'sq',0.5,5 if k<3 else 2)   # trial ended
    register(BLACK+0.02,0.1)                                        # cheerful cash register chime on black
    # ---------- voices ----------
    NB=np.zeros(n); duck=np.ones(n)
    for k_,t0 in VOICE:
        a,ar=_sf.read(os.path.join(TTS_DIR,'sz',f'{k_}.wav')); a=a if a.ndim==1 else a.mean(1)
        a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a)
        act=a[np.abs(a)>0.02]; a=a/(np.sqrt((act**2).mean())+1e-9)*0.2
        i=int(t0*sr); j=min(n,i+len(a)); NB[i:j]+=a[:j-i]
        duck[max(0,i-int(0.05*sr)):min(n,j+int(0.1*sr))]=0.45
    duck=np.convolve(duck,np.ones(2400)/2400,'same')
    s.L+=2.0*M*duck+AMB; s.R+=2.0*np.roll(M,240)*duck+np.roll(AMB,700)
    s.reverb(0.14,length=1.0,decay=4.5)
    pk=max(np.abs(s.L).max(),np.abs(s.R).max()); gv=pk*1.05/np.abs(NB).max()
    s.L=s.L*(0.55+0.45*duck)+NB*gv; s.R=s.R*(0.55+0.45*duck)+NB*gv
    return s.save(path,peak=0.9)
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'safe_zone.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'sz_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.96,vignette=0.22,grain=1.5,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(post.upscale(frame(f/FPS),S),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
