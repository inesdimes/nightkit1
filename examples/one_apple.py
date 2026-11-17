"""THE ONE APPLE PROBLEM - "Why can RPG heroes carry 99 swords but not ONE apple?"  PS1 RPG comedy short, 9:16, ~30 s. Fully procedural (nightkit).
LOCKED ASSETS: the channel knight (final_boss.knight) + the 99-sword pack, apple (4 bite stages), stump, legendary golden sword, dragon, meadow, UI.
All text is a 2D overlay. Voice: python tools/tts/ap.py -> $TTS_DIR/ap/N1.wav (hook only; the rest is visual comedy + sound).
Run: TEST=0.5,5,12 python examples/one_apple.py -> test.png | PART=a:b | PART=audio | QA: python tools/qa/scene_qa.py examples/one_apple.py"""
import os, sys, math, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, quad
from nightkit import post, font
from nightkit.zraster import zrender
from nightkit.audio import Sound
import final_boss as FB
box,seg,xform,limb,prelit=FB.box,FB.seg,FB.xform,FB.limb,FB.prelit
sm,seg01,lerp,lerp3,PI,Ry,Rx=FB.sm,FB.seg01,FB.lerp,FB.lerp3,FB.PI,FB.Ry,FB.Rx
def Rz(a): c,s=math.cos(a),math.sin(a); return np.array([[c,-s,0],[s,c,0],[0,0,1]])
TTS_DIR=FB.TTS_DIR; OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6
SCR=json.load(open(os.path.join(TTS_DIR,'ap','script.json')))
for ch,rows in {'+':['00000','00100','00100','11111','00100','00100','00000']}.items(): font.FONT.setdefault(ch,rows)

# ======================= palette =======================
GRASS1=(96,184,72); GRASS2=(84,166,62); DIRT=(150,116,76); BARK=(112,74,42); BARK_L=(150,106,62); RING=(196,150,92)
PINE1=(40,110,56); PINE2=(52,128,64); ROCKC=(130,128,136); MOUNT=(120,130,170); MOUNT2=(150,158,196)
APPLE=(214,34,44); APPLE_D=(160,24,34); FLESH=(250,238,196); STEM=(96,62,34); LEAF=(70,176,70); SEED=(70,40,26)
GOLD=(255,214,70); GOLD_D=(208,150,30); GEM=(230,40,70); BLADE_S=(190,196,210); BLADE_D=(120,126,140); BLADE_R=(150,100,70); SACK=(140,104,58); SACK_D=(108,78,42); STRAP=(86,56,32)
DR=(200,44,58); DR_D=(142,30,44); DR_BELLY=(236,190,110); DR_WING=(120,36,100); CLAW=(236,230,206); WHT=(242,238,226); YEL=(255,210,60); RED=(232,44,40); GRN=(120,230,90); BLU=(110,170,255); CYAN=(90,210,255); GRY=(150,150,160)

# ======================= timeline (story seconds) =======================
HOOK=3.5
T_RECOIL=(3.5,4.0); T_REAPP=(4.0,4.0); T_TIP=(4.0,4.6); T_FLAIL=(4.6,5.6); T_GETUP=(5.6,6.6); T_THINK=(6.6,7.2)
T_MENU=(9.0,13.0); T_DROP=(13.0,14.2); T_PICK=(14.2,15.7); T_EAT=(15.7,17.7); T_DANCE=(17.7,20.1); T_RETAKE=T_DANCE; T_TREMOR=(20.1,22.6)
T_LAND=22.6; T_HOLSTER=(23.0,23.9); T_SWORDLOOK=(23.9,25.1); T_CORELOOK=(25.1,26.5); T_SILENCE=(26.5,27.5); T_FIRE=(27.5,28.3); T_FLASH=28.3
T_DIED=(28.5,29.4); STING=(29.4,32.0); DUR=32.4; BLACK=32.0
BITES=[16.55,17.0,17.45]; SWORD_DROP=13.2; APPLE_GRAB=15.0; ITEM_GET=(15.0,16.2); BULB=6.8; CORE_GET=17.95; RETRY=(19.55,20.5)
SKIPS=[(7.2,9.0)]                                            # dead time cut at the shot change into the menu
SKIPPED=sum(b-a for a,b in SKIPS)
def story_t(V):
    st=V
    for a,b in SKIPS:
        if st>=a: st+=b-a
    return st
N=int(round((DUR-SKIPPED)*FPS))                                  # video frames

# ======================= world layout =======================
STUMP_H=0.5; APPLE_C=np.array([0.0,STUMP_H+0.18,-0.28]); SW_LAND=np.array([-0.72,0.04,-0.5]); DRAGON_AT=(0.3,0.0,3.5)
KN_KEYS={'base','yaw','walk','run','sword','rh','lh','lean','head','sit','eyes','swing','boots'}
def Tmap(st):
    b=np.array(st['base'],float); sit=st.get('sit',0.0); hip=0.82-0.42*sit; piv=np.array([0,hip,0]); lean=st.get('lean',0.0)+0.22*st.get('run',0.0); Rb=Ry(st['yaw'])
    def T(p): p=np.array(p,float); return tuple(b+Rb@(piv+Rx(lean)@(p-piv+np.array([0,hip-0.82,0]))))
    return T
def kpoint(st,p): return Tmap(st)(p)
def k_local(st,w):
    b=np.array(st['base'],float); sit=st.get('sit',0.0); hip=0.82-0.42*sit; piv=np.array([0,hip,0]); lean=st.get('lean',0.0)+0.22*st.get('run',0.0)
    q=Rx(-lean)@(Ry(-st['yaw'])@(np.array(w,float)-b)-piv); return tuple(q+piv-np.array([0,hip-0.82,0]))
def khand(st,side=1):
    h=st.get('rh' if side>0 else 'lh')
    if h is None: h=(0.27*side,0.86,0.04)
    return kpoint(st,h)
def solve_reach(lean=1.0):
    best=None
    for z in np.arange(-2.0,-0.859,0.01):
        st=dict(base=(0,0,z),yaw=0.0,lean=lean); d=np.linalg.norm(np.array(kpoint(st,(0.22,1.27,0)))-APPLE_C)
        if best is None or abs(d-0.5)<best[0]: best=(abs(d-0.5),z)
    return round(best[1],2)
LEAN_REACH=1.12; RZ=solve_reach(LEAN_REACH); RZ2=round(RZ-0.3,2)      # RZ2: where he stands after the eating scene (room for the dance)

# ======================= LOCKED ASSET: the knight with his 99-sword pack =======================
def pack_quads(st):
    T=Tmap(st); r=np.random.default_rng(11); jig=st.get('jig',0.0); ph=st.get('ph',0.0); Q=[]
    Q+=xform(box(-0.36,0.36,0.72,1.52,-0.7,-0.32,SACK)+box(-0.38,0.38,0.62,0.74,-0.72,-0.3,SACK_D)+box(-0.3,0.3,1.52,1.62,-0.66,-0.36,SACK_D),T)   # fat sack behind the cape
    for sx in (-1,1): Q+=box(sx*0.15-0.03,sx*0.15+0.03,0.82,1.34,0.13,0.145,STRAP,xf=T)                       # chest straps
    cols=[BLADE_S,BLADE_D,BLADE_R,(176,182,204),(206,170,90)]
    for i in range(26):
        top=i<16
        if top: p0=np.array([r.uniform(-0.3,0.3),1.58,r.uniform(-0.62,-0.4)]); a=r.uniform(-1.0,1.0); b_=r.uniform(-0.45,0.25); d=np.array([math.sin(a),math.cos(a)*0.95,b_])
        else: sx=1 if i%2 else -1; p0=np.array([sx*0.36,r.uniform(0.85,1.45),r.uniform(-0.62,-0.4)]); d=np.array([sx*1.0,r.uniform(-0.1,0.5),r.uniform(-0.3,0.1)])
        d=d+np.array([math.sin(ph*5+i)*0.12*jig,math.cos(ph*4+i*1.3)*0.08*jig,0.0]); d=d/np.linalg.norm(d); L=r.uniform(0.75,1.1)
        c=cols[i%5]
        Q+=xform(seg(p0,p0+d*L,0.075,c,0.03)+seg(p0-d*0.02-np.cross(d,[0,0,1.0])*0.1,p0-d*0.02+np.cross(d,[0,0,1.0])*0.1,0.04,GOLD_D),T)
    return Q
def tilt_quads(Q,st,ang):
    """whole-body fall onto the back (pivot: behind the heels); lifted so nothing sinks into the floor"""
    b=np.array(st['base'],float); Rb=Ry(st['yaw']); P=b+Rb@np.array([0,0.05,-0.3]); M=Rb@Rx(-ang)@Rb.T
    xform(Q,lambda p: tuple(P+M@(np.array(p,float)-P)))
    ymin=min(p[1] for q in Q for p in q['p'])
    if ymin<0.0: xform(Q,lambda p:(p[0],p[1]-ymin,p[2]))
    return Q
def knight_full(**st):
    Q=FB.knight(**{k:v for k,v in st.items() if k in KN_KEYS})
    if st.get('pack',True): Q+=pack_quads(st)
    if st.get('tilt',0.0)>1e-4: Q=tilt_quads(Q,st,st['tilt'])
    return Q
def reach_to(st,w,side=1,L=0.6):
    """torso-space hand target for a world point, clamped so the arm never stretches"""
    sh=np.array(kpoint(st,(side*0.22,1.27,0))); v=np.array(w,float)-sh; d=np.linalg.norm(v)
    if d>L: w=sh+v/d*L
    return k_local(st,w)
def knight_head_top(st): return kpoint(st,(0,1.95,0))

# ======================= LOCKED ASSETS: apple, stump, golden sword =======================
AP_S=1.5                                                        # apple scale (readable at 9:16)
def apple_quads(c,stage=0,yaw=0.0):
    """stage 0 whole, 1 one bite, 2 two bites, 3 core"""
    c=np.array(c,float); R_=Ry(yaw)
    def Wd(p): return tuple(c+R_@(np.array(p,float)*AP_S))
    Q=[]
    if stage==0:
        Q+=box(-0.075,0.075,-0.12,-0.05,-0.075,0.075,APPLE_D,xf=Wd)+box(-0.12,0.12,-0.05,0.06,-0.12,0.12,APPLE,xf=Wd)+box(-0.1,0.1,0.06,0.11,-0.1,0.1,APPLE,xf=Wd)
        Q+=box(-0.01,0.01,0.11,0.19,-0.01,0.01,STEM,xf=Wd)+box(0.01,0.09,0.15,0.17,-0.03,0.03,LEAF,xf=Wd)+box(0.03,0.07,0.0,0.045,0.12,0.121,(255,210,210),xf=Wd,emit=True)   # glint
    elif stage==1:
        Q+=box(-0.075,0.075,-0.12,-0.05,-0.075,0.075,APPLE_D,xf=Wd)+box(-0.12,0.0,-0.05,0.06,-0.12,0.12,APPLE,xf=Wd)+box(0.0,0.12,-0.05,0.06,-0.12,0.0,APPLE,xf=Wd)+box(-0.1,0.0,0.06,0.11,-0.1,0.1,APPLE,xf=Wd)
        Q+=box(0.0,0.1,-0.05,0.06,0.0,0.12,FLESH,xf=Wd)+box(-0.01,0.01,0.11,0.19,-0.01,0.01,STEM,xf=Wd)
    elif stage==2:
        Q+=box(-0.075,0.075,-0.12,-0.05,-0.075,0.075,APPLE_D,xf=Wd)+box(-0.12,0.0,-0.05,0.06,-0.12,0.0,APPLE,xf=Wd)
        Q+=box(0.0,0.12,-0.05,0.06,-0.12,0.12,FLESH,xf=Wd)+box(-0.12,0.0,-0.05,0.06,0.0,0.12,FLESH,xf=Wd)+box(-0.01,0.01,0.06,0.14,-0.01,0.01,STEM,xf=Wd)
    else:
        Q+=box(-0.035,0.035,-0.11,0.11,-0.035,0.035,FLESH,xf=Wd)+box(-0.05,0.05,-0.12,-0.1,-0.05,0.05,APPLE_D,xf=Wd)+box(-0.01,0.01,0.11,0.17,-0.01,0.01,STEM,xf=Wd)
        Q+=box(0.035,0.05,-0.03,0.0,-0.012,0.012,SEED,xf=Wd)+box(-0.05,-0.035,0.02,0.05,-0.012,0.012,SEED,xf=Wd)
    return Q
def stump_quads():
    Q=box(-0.4,0.4,0,STUMP_H,-0.4,0.4,BARK)+box(-0.46,0.46,0,0.1,-0.46,0.46,BARK)+box(-0.37,0.37,STUMP_H,STUMP_H+0.02,-0.37,0.37,RING)+box(-0.24,0.24,STUMP_H+0.021,STUMP_H+0.03,-0.24,0.24,BARK_L)+box(-0.1,0.1,STUMP_H+0.031,STUMP_H+0.04,-0.1,0.1,BARK)
    for k in range(4): a=k*PI/2; Q+=box(0.28*math.cos(a)-0.04,0.28*math.cos(a)+0.04,0.1,STUMP_H-0.05,0.28*math.sin(a)-0.04,0.28*math.sin(a)+0.04,BARK_L)
    return Q
def golden_sword(hilt,d,glow=1.0):
    """legendary golden sword: hilt position + blade direction"""
    h=np.array(hilt,float); d=np.array(d,float); d/=np.linalg.norm(d); cr=np.cross(d,[0,1.0,0] if abs(d[1])<0.9 else [1.0,0,0]); cr/=np.linalg.norm(cr)+1e-9
    Q=seg(h+d*0.1,h+d*1.12,0.1,GOLD,0.035,emit=True)+seg(h+d*0.14,h+d*1.0,0.035,(255,244,170),0.04,emit=True)                    # blade + bright fuller
    Q+=seg(h+d*0.1-cr*0.22,h+d*0.1+cr*0.22,0.07,GOLD_D,0.06)+seg(h-d*0.12,h+d*0.1,0.06,(120,60,30),0.05)+seg(h-d*0.16,h-d*0.1,0.09,GOLD_D,0.08)
    Q+=seg(h+d*0.11,h+d*0.14,0.07,GEM,0.07,emit=True)
    return Q

# ======================= LOCKED ASSET: the dragon =======================
def dragon(base,yaw,fold=1.0,flap=0.0,head=(0.0,2.55,2.1),hpitch=0.15,hyaw=0.0,jaw=0.0,eye=0.0,fire=0.0,tail=0.0,breathe=0.0,roll=0.0):
    """low-poly crimson dragon. local forward +z, ~4.5 m long. fold: 1 wings spread .. 0.2 tucked. flap: wing lift angle. eye: 0 red .. 1 gold. fire: mouth glow 0..1."""
    b=np.array(base,float); R_=Ry(yaw)
    def Wd(p): return tuple(b+R_@np.array(p,float))
    Q=[]; by=0.03*breathe
    Q+=box(-0.55,0.55,0.95+by,1.95+by,-1.0,1.0,DR,xf=Wd)+box(-0.45,0.45,0.9,1.02+by,-0.95,0.95,DR_BELLY,xf=Wd)+box(-0.35,0.35,1.95+by,2.05+by,-0.9,0.8,DR_D,xf=Wd)
    for k in range(5): z=-0.8+0.35*k; Q+=box(-0.05,0.05,2.05+by,2.25+by,z-0.07,z+0.07,CLAW,xf=Wd)                         # back spikes
    for sx,sz in ((-1,0.65),(1,0.65),(-1,-0.65),(1,-0.65)):
        x=sx*0.5; Q+=box(x-0.18,x+0.18,0.1,1.0,sz-0.21,sz+0.21,DR_D,xf=Wd)+box(x-0.22,x+0.22,0.0,0.12,sz-0.22,sz+0.42,DR,xf=Wd)
        for cx in (-0.12,0.0,0.12): Q+=box(x+cx-0.035,x+cx+0.035,0.0,0.09,sz+0.4,sz+0.52,CLAW,xf=Wd)
    pts=[np.array([0,1.45,-1.0])]
    for i in range(1,6): pts.append(np.array([0.3*tail*i*math.sin(i*0.8),1.45-0.12*i+0.05*math.sin(i)*breathe,-1.0-0.5*i]))
    for i in range(5): Q+=xform(seg(pts[i],pts[i+1],0.55-0.09*i,DR if i%2==0 else DR_D,0.5-0.08*i),Wd)
    Q+=xform(seg(pts[5]+np.array([-0.18,0,0.1]),pts[5]+np.array([0.18,0,-0.2]),0.1,CLAW,0.4),Wd)
    N0=np.array([0.0,1.65,1.0]); H=np.array(head,float); C=N0+np.array([0.0,0.9,0.7]); bez=lambda u:(1-u)**2*N0+2*(1-u)*u*C+u*u*H
    nk=[bez(u) for u in (0.0,0.22,0.45,0.7,0.9)]
    for i in range(4): Q+=xform(seg(nk[i],nk[i+1],0.5-0.07*i,DR if i%2==0 else DR_D,0.45-0.06*i),Wd)
    Mh=Ry(hyaw)@Rx(hpitch)
    def Hd(p): return Wd(H+Mh@np.array(p,float))
    Q+=box(-0.24,0.24,-0.2,0.24,-0.3,0.4,DR,xf=Hd)+box(-0.17,0.17,-0.12,0.12,0.4,1.0,DR,xf=Hd)+box(-0.26,0.26,0.2,0.3,0.05,0.4,DR_D,xf=Hd)           # skull, snout, brow ridge
    for sx in (-1,1):
        Q+=box(sx*0.17-0.03,sx*0.17+0.03,0.1,0.2,0.4,0.41,CLAW,xf=Hd)                                                                                          # eye bulge placeholder
        g=tuple(int(v) for v in lerp3((255,60,30),(255,214,70),eye)); Q+=box(sx*0.13,sx*0.21,0.08,0.18,0.405,0.42,g,xf=Hd,emit=True)
        Q+=box(sx*0.04,sx*0.07,-0.04,0.0,0.995,1.01,(30,16,16),xf=Hd)                                                                                          # nostrils
        Q+=xform(seg((sx*0.17,0.22,-0.2),(sx*0.28,0.72,-0.72),0.13,CLAW,0.13)+seg((sx*0.28,0.72,-0.72),(sx*0.2,1.0,-0.6),0.08,CLAW,0.08),Hd)
        for k in range(4): z=0.55+0.1*k; Q+=box(sx*0.14-0.02,sx*0.14+0.02,-0.2,-0.12,z-0.025,z+0.025,CLAW,xf=Hd)                                              # upper fangs
    jp=np.array([0.0,-0.12,0.25]); Mj=Rx(jaw*0.7)
    def Jd(p): p=np.array(p,float); return Hd(jp+Mj@(p-jp))
    Q+=box(-0.15,0.15,-0.26,-0.12,0.2,0.92,DR_D,xf=Jd)+box(-0.1,0.1,-0.27,-0.24,0.86,0.95,DR,xf=Jd)
    for sx in (-1,1):
        for k in range(3): z=0.45+0.14*k; Q+=box(sx*0.12-0.02,sx*0.12+0.02,-0.12,-0.05,z-0.025,z+0.025,CLAW,xf=Jd)
    if fire>0.02 and jaw>0.3: Q+=box(-0.12,0.12,-0.1,0.1*fire-0.1+0.02,0.3,0.85,(255,150,40),xf=Hd,emit=True)+box(-0.07,0.07,-0.08,0.0,0.4,0.8,(255,230,120),xf=Hd,emit=True)   # glowing throat
    for sx in (-1,1):                                                                                                                                            # wings
        S_=np.array([sx*0.5,1.95,0.3]); Rw=Rz(sx*(flap-0.1+(1-fold)*-0.9))
        def wp(v): return tuple(S_+Rw@np.array([sx*v[0]*fold,v[1],v[2]]))
        Wr=np.array(wp((1.9,0.9,-0.2))); Tp=np.array(wp((3.0,-0.1,-1.4))); Rt=np.array([sx*0.42,1.5,-0.9]); Tm=np.array(wp((1.9,-0.3,-1.0)))
        Q+=xform(seg(S_,Wr,0.14,DR_D,0.12)+seg(Wr,Tp,0.08,DR_D,0.08)+seg(Wr,Tm,0.07,DR_D,0.07),Wd)
        Q+=xform([quad([tuple(S_),tuple(Wr),tuple(Tp)],DR_WING),quad([tuple(S_),tuple(Tp),tuple(Tm)],DR_WING),quad([tuple(S_),tuple(Tm),tuple(Rt)],(140,34,88))],Wd)
    if roll>1e-4:                                                     # tips over sideways (like the knight's turtle fall)
        P=np.array(Wd((-0.75,0.0,0.0))); xform(Q,lambda p: tuple(P+Rz(-roll)@(np.array(p,float)-P)))
        ymin=min(p[1] for q in Q for p in q['p'])
        if ymin<0.0: xform(Q,lambda p:(p[0],p[1]-ymin,p[2]))
    return Q
DR_KEYS={'base','yaw','fold','flap','head','hpitch','hyaw','jaw','eye','fire','tail','breathe','roll'}

# ======================= the meadow =======================
def world_static():
    Q=[]
    for i in range(-12,12):
        for j in range(-10,14): Q.append(quad([(i*1.6,0,j*1.6),((i+1)*1.6,0,j*1.6),((i+1)*1.6,0,(j+1)*1.6),(i*1.6,0,(j+1)*1.6)],GRASS1 if (i+j)%2 else GRASS2))
    Q+=[quad([(-0.9,0.01,-14),(0.9,0.01,-14),(0.9,0.01,20),(-0.9,0.01,20)],DIRT)]
    r=np.random.default_rng(5)
    for k in range(34):
        side=-1 if k%2 else 1; x=side*r.uniform(4.2,12); z=r.uniform(-12,16); sc=r.uniform(0.8,1.3)
        if abs(z-1.0)<4.5 and abs(x)<10.0: continue
        Q+=box(x-0.18*sc,x+0.18*sc,0,1.1*sc,z-0.18*sc,z+0.18*sc,BARK)
        for lv,(rd,hh) in enumerate(((1.25,1.1),(0.95,1.1),(0.6,1.0))): Q+=box(x-rd*sc,x+rd*sc,(0.9+lv*0.85)*sc,(0.9+lv*0.85+hh)*sc,z-rd*sc,z+rd*sc,PINE1 if lv%2 else PINE2)
    for k in range(14): x=r.uniform(-9,9); z=r.uniform(-8,12); s_=r.uniform(0.08,0.2); Q+=box(x-s_,x+s_,0,s_*1.2,z-s_,z+s_,ROCKC) if abs(x)>1.6 else []
    for k,(x,w,h) in enumerate(((-30,10,9),(-16,12,13),(0,14,16),(18,12,12),(32,10,8))): Q+=box(x-w,x+w,0,h,48,52,MOUNT if k%2 else MOUNT2)
    return Q
WORLD=world_static()
FLOWERS=[(x,z,c) for (x,z,c) in [(-1.6,-1.8,(255,230,90)),(1.7,-2.4,(250,120,170)),(-2.4,0.6,(250,250,250)),(2.2,1.4,(255,230,90)),(1.4,-0.9,(250,120,170)),(-1.2,-3.6,(250,250,250))]]
def flowers():
    Q=[]
    for x,z,c in FLOWERS: Q+=box(x-0.015,x+0.015,0,0.18,z-0.015,z+0.015,(60,150,60))+box(x-0.06,x+0.06,0.18,0.24,z-0.06,z+0.06,c,emit=True)
    return Q
def pebbles(t):
    Q=[]; amp=seg01(t,T_TREMOR[0]+0.3,T_LAND)*(1-seg01(t,T_LAND+0.6,T_LAND+1.5))
    if t>=T_TREMOR[0]+0.3 and t<T_LAND+1.5:
        r=np.random.default_rng(9)
        for k in range(10):
            a=r.uniform(0,2*PI); rad=r.uniform(1.0,3.2); y=abs(math.sin(t*(11+k)+k))*0.18*amp; s_=0.07
            x,z=rad*math.cos(a),rad*math.sin(a)+1.0; Q+=box(x-s_,x+s_,y,y+s_*1.3,z-s_,z+s_,ROCKC)
    return Q
def dust(t):
    Q=[]; u=(t-T_LAND)/1.0
    if 0<=u<1:
        r=np.random.default_rng(3)
        for k in range(14):
            a=k*2*PI/14+r.uniform(-0.2,0.2); rad=0.9+3.0*u; y=0.15+0.6*u*r.uniform(0.6,1.0); s_=0.12+0.18*u; c=tuple(int(v) for v in lerp3((150,126,96),sky_color(t),min(1.0,u*1.3)))
            x,z=DRAGON_AT[0]+rad*math.cos(a),DRAGON_AT[2]+rad*math.sin(a)*0.8; Q+=box(x-s_,x+s_,y-s_,y+s_,z-s_,z+s_,c,emit=True)
    return Q

# ======================= state functions =======================
def sky_color(t):
    if t>=STING[0]: return (112,84,136)
    DAY=(120,180,235); STORM=(96,80,120); DUSK=(128,96,150); DARK=(46,24,44)
    if t<T_TREMOR[0]: return DAY
    if t<T_LAND: return tuple(int(v) for v in lerp3(DAY,STORM,sm(seg01(t,T_TREMOR[0],T_LAND))))
    if t<T_FIRE[0]: return tuple(int(v) for v in lerp3(STORM,DUSK,sm(seg01(t,T_LAND,T_SWORDLOOK[1]))))
    return tuple(int(v) for v in lerp3(DUSK,DARK,sm(seg01(t,T_FIRE[0],T_FLASH))))
def dance_pose(t):
    u=t-T_DANCE[0]; beat=(T_DANCE[1]-T_DANCE[0])/4; k=min(3,int(u/beat)); ph=u/beat-k
    P=[((0.3,1.8,0.0),(-0.3,1.8,0.0),0.0),((0.62,1.7,0.0),(-0.42,0.72,0.1),0.55),((0.45,0.74,0.1),(-0.62,1.7,0.0),-0.55),((0.7,1.3,0.0),(-0.7,1.3,0.0),0.0)]
    prev=P[k-1] if k>0 else ((0.3,0.95,0.2),(-0.27,0.86,0.04),0.0); cur=P[k]; e=sm(seg01(ph,0.0,0.4))
    rh=lerp3(prev[0],cur[0],e); lh=lerp3(prev[1],cur[1],e); yo=lerp(prev[2],cur[2],e)
    spin=2*PI*seg01(ph,0.0,1.0) if k==3 else 0.0
    return rh,lh,yo+spin,0.12*abs(math.sin(PI*ph*2))
REACH_APPLE=lambda st: k_local(st,APPLE_C)
HILT=SW_LAND+np.array([0.0,1.12,0.0])                           # the golden sword stands planted in the grass: tip at SW_LAND, hilt at chest height
def solve_retake():
    """where he stands, which way he faces and how far he leans to grip the planted sword with his LEFT hand"""
    best=None
    for x in np.arange(-0.7,0.01,0.05):
        for z in np.arange(RZ2-0.2,RZ2+0.36,0.05):
            if abs(x)<0.64 and abs(z)<0.64: continue
            if math.hypot(x-SW_LAND[0],z-SW_LAND[2])<0.5: continue
            yaw=math.atan2(HILT[0]-x,HILT[2]-z)
            for lean in (0.1,0.2,0.3):
                st=dict(base=(x,0,z),yaw=yaw,lean=lean); d=np.linalg.norm(np.array(kpoint(st,(-0.22,1.27,0)))-HILT)
                sc=abs(d-0.5)+0.25*abs(x)+0.25*abs(z-RZ2)
                if best is None or sc<best[0]: best=(sc,x,z,yaw,lean)
    return best[1:]
XR,ZR,YAW_R,LEAN_RE=solve_retake(); XR=round(float(XR),2); ZR=round(float(ZR),2)
def zbase(t):
    ZS=RZ-0.5
    if t<4.0: return RZ
    if t<14.2: return ZS
    if t<14.6: return lerp(ZS,RZ,sm(seg01(t,14.2,14.6)))
    if t<17.35: return RZ
    return lerp(RZ,RZ2,sm(seg01(t,17.35,17.7)))
def knight_state(t):
    ZS=RZ-0.5; z0=zbase(t); xb=XR if t>=19.15 else (lerp(0.0,XR,sm(seg01(t,18.7,19.15))) if t>=18.7 else 0.0)
    zr=ZR if t>=19.15 else (lerp(RZ2,ZR,sm(seg01(t,18.7,19.15))) if t>=18.7 else z0)
    B=lambda z=z0,y=0.0:(xb,y,z if t<18.7 else zr)
    st=dict(base=B(),yaw=0.0,sword='hip',boots=FB.STEEL_D)
    if t<2.0:                                                      # lumbers up to the stump under the weight
        u=seg01(t,0.0,2.0); return dict(st,base=B(RZ-2.0*(1-u)),walk=t*6.5,lean=0.12+0.04*math.sin(t*6.5*2),jig=1.0,ph=t,head=0.12*math.sin(t*3.2))
    if t<HOOK:                                                     # bends and reaches for the apple
        l=sm(seg01(t,2.0,2.8)); k=dict(st,lean=lerp(0.12,LEAN_REACH,l)+0.03*math.sin(t*30)*l,jig=0.5,ph=t)
        rh=lerp3((0.27,0.86,0.04),REACH_APPLE(dict(k,lean=LEAN_REACH)),sm(seg01(t,2.3,HOOK))); return dict(k,rh=rh,head=0.0)
    fling=lerp3(REACH_APPLE(dict(st,lean=LEAN_REACH)),(0.4,1.2,0.1),sm(seg01(t,T_RECOIL[0],T_RECOIL[0]+0.3)))
    if t<T_RECOIL[1]:                                              # OVERENCUMBERED: the weight yanks him backwards...
        u=seg01(t,*T_RECOIL); z=RZ-0.5*sm(u); l=lerp(LEAN_REACH,-0.25,sm(seg01(t,T_RECOIL[0],T_RECOIL[0]+0.35)))
        return dict(st,base=B(z),walk=-t*10 if 0.1<u<1 else 0.0,lean=l,rh=fling,lh=(-0.4,1.2,0.1),jig=1.0,ph=t)
    if t<T_TIP[1]:                                                 # ...straight onto his back (turtle mode)
        a=seg01(t,*T_TIP); tilt=1.45*(sm(a)**1.4)
        return dict(st,base=B(ZS),tilt=tilt,lean=-0.25*(1-a),rh=(0.4,1.2,0.1),lh=(-0.4,1.2,0.1),jig=1.0,ph=t)
    if t<T_FLAIL[1]:                                               # on his back, legs and arms flailing
        u=t-T_FLAIL[0]; return dict(st,base=B(ZS),tilt=1.45+0.05*math.sin(u*18),walk=t*18,rh=(0.4,1.25+0.3*math.sin(t*14),0.3),lh=(-0.4,1.25+0.3*math.sin(t*14+PI),0.3),jig=1.0,ph=t*2)
    if t<T_GETUP[1]:                                               # rocks back and forth, then up
        K=[(5.6,1.45),(5.85,0.9),(6.1,1.45),(6.35,0.55),(6.6,0.0)]
        for (t0,a0),(t1,a1) in zip(K,K[1:]):
            if t<=t1: tilt=lerp(a0,a1,sm(seg01(t,t0,t1))); break
        return dict(st,base=B(ZS),tilt=tilt,walk=t*12 if tilt>0.7 else 0.0,rh=(0.4,1.2,0.3),lh=(-0.4,1.2,0.3),lean=0.0,jig=1.0,ph=t*2)
    if t<T_MENU[0]:                                                # catches his breath, thinks (this pose holds through the cut into the menu)
        return dict(st,base=B(ZS),lean=0.15,rh=lerp3((0.27,0.86,0.04),(0.1,1.42,0.32),sm(seg01(t,6.7,7.0))),jig=0.0,ph=0.0,head=0.0)
    if t<T_MENU[1]:                                                # (menu is open) hand on his helmet, deciding... then a confident nod
        nod=sm(seg01(t,12.3,12.5))*(1-sm(seg01(t,12.5,12.8)))
        return dict(st,base=B(ZS),lean=0.15+0.1*nod,rh=(0.1,1.42,0.32),head=0.1*math.sin((t-T_MENU[0])*1.6),jig=0.0,ph=0.0)
    if t<T_DROP[1]:                                                # the sword leaves the holster; he feels lighter
        up=sm(seg01(t,SWORD_DROP+0.4,T_DROP[1]))
        return dict(st,base=B(ZS),sword='hip' if t<SWORD_DROP else 'none',lean=lerp(0.15,-0.05,up),rh=lerp3((0.1,1.42,0.32),(0.27,0.86,0.04),sm(seg01(t,SWORD_DROP,SWORD_DROP+0.4))),jig=0.6,ph=t,head=0.0)
    s0=dict(st,sword='none',jig=0.5,ph=t)
    if t<T_PICK[1]:                                                # steps up to the stump and picks the apple up
        a=seg01(t,14.45,T_PICK[1]); l=sm(seg01(a,0.0,0.4))*(1-sm(seg01(a,0.6,1.0)))*(LEAN_REACH-0.1)+0.1
        rh=lerp3((0.27,0.86,0.04),REACH_APPLE(dict(s0,lean=LEAN_REACH)),sm(seg01(a,0.15,0.5)))
        if a>0.6: rh=lerp3(REACH_APPLE(dict(s0,lean=LEAN_REACH)),(0.12,1.18,0.32),sm(seg01(a,0.6,1.0)))
        return dict(s0,lean=l if t>=14.45 else 0.1,rh=rh if t>=14.45 else (0.27,0.86,0.04),head=0.0,walk=t*7 if 14.2<t<14.6 else 0.0)
    if t<T_EAT[1]:                                                 # eats it: three bites
        up=sm(seg01(t,T_EAT[0],T_EAT[0]+0.4)); down=sm(seg01(t,17.4,17.7)); bite=max([bounce(t,[b_],0.18) for b_ in BITES])
        rh=lerp3(lerp3((0.12,1.18,0.32),(0.02,1.5,0.3),up),(0.3,0.95,0.2),down)
        return dict(s0,lean=0.1-0.08*bite,rh=rh,head=-0.15*bite,walk=-t*9 if 17.35<t<17.7 else 0.0)
    core=(0.3,0.95,0.2)
    if t<T_RETAKE[1]:                                              # +1 HP joy, a free slot! he goes to take the golden sword back...
        hopk=abs(math.sin(PI*(t-17.7)/0.25))*0.12 if t<18.2 else 0.0; arms=sm(seg01(t,17.7,17.85))*(1-sm(seg01(t,18.05,18.25)))
        rh=lerp3(core,(0.3,1.75,0.0),arms); lh=lerp3((-0.27,0.86,0.04),(-0.3,1.75,0.0),arms)
        head=-0.9*sm(seg01(t,18.3,18.55))*(1-sm(seg01(t,18.65,18.85)))
        yaw=lerp(0.0,YAW_R,sm(seg01(t,18.7,19.15))); walk=t*8 if 18.7<t<19.15 else 0.0
        bend=sm(seg01(t,19.15,19.55))*(1-sm(seg01(t,19.75,20.1))); lean=lerp(0.05,LEAN_RE,bend)
        stb=dict(s0,base=B(z0=None,y=hopk) if False else (xb,hopk,zr),yaw=yaw,lean=lean)
        if t>=19.15: lh=reach_to(stb,HILT,-1) if bend>0.02 else lh
        if t>=19.75: lh=lerp3(reach_to(dict(stb,lean=LEAN_RE),HILT,-1),(-0.5,1.2,0.1),sm(seg01(t,19.75,20.05)))
        return dict(stb,rh=rh if t<19.15 else core,lh=lh,head=head if t<19.15 else (0.8*sm(seg01(t,19.8,20.05))),walk=walk,jig=1.0,ph=t*2)
    xt=XR; zt=ZR
    if t<T_LAND:                                                   # the ground shakes: he stops, looks around (still holding the core)
        a=seg01(t,*T_TREMOR); return dict(s0,base=(xt,0.0,zt),yaw=lerp(YAW_R,0.0,sm(seg01(t,20.15,20.7))),rh=core,lean=0.04*math.sin(t*38)*a,head=0.9*math.sin(t*3.0)*sm(seg01(t,T_TREMOR[0]+0.5,T_TREMOR[0]+1.0)),jig=1.5,ph=t*3)
    s0=dict(s0,base=(xt,0.0,zt),yaw=0.0)
    if t<T_HOLSTER[0]: sh=sm(seg01(t,T_LAND,T_LAND+0.25))*(1-sm(seg01(t,T_LAND+0.25,T_LAND+0.4))); return dict(s0,rh=core,lean=-0.18*sh,lh=(-0.6,1.1,0.2),head=0.0,jig=1.5,ph=t*3)
    if t<T_HOLSTER[1]:                                             # confident reach for the holster... pat, pat... nothing
        a=seg01(t,*T_HOLSTER); up=sm(seg01(a,0.0,0.3)); sw=sm(seg01(a,0.3,0.45)); pat=0.04*abs(math.sin((a-0.5)*30))*sm(seg01(a,0.5,0.52))*(1-sm(seg01(a,0.9,1.0)))
        lh=lerp3(lerp3((-0.27,0.86,0.04),(-0.5,1.45,0.2),up),(-0.24,0.9+pat,0.1),sw)
        return dict(s0,rh=core,lh=lh,lean=0.12*sw,head=-0.75*sm(seg01(a,0.75,1.0)),jig=0.3,ph=t)
    if t<T_CORELOOK[0]: return dict(s0,rh=core,lh=(-0.24,0.9,0.1),lean=0.12+0.015*math.sin(t*30),head=-0.75,jig=0.2,ph=t)     # frozen, trembling
    if t<T_CORELOOK[1]:                                            # slowly raises the apple core and looks at it
        a=sm(seg01(t,T_CORELOOK[0],T_CORELOOK[0]+0.7)); return dict(s0,rh=lerp3(core,(0.14,1.38,0.34),a),lh=(-0.24,0.9,0.1),lean=lerp(0.12,0.0,a)+0.01*math.sin(t*30),head=lerp(-0.75,0.8,a),jig=0.2,ph=t)
    return dict(s0,rh=(0.14,1.38,0.34),lh=(-0.24,0.9,0.1),lean=0.012*math.sin(t*34),head=0.8,jig=0.2,ph=t)
def bounce(t,impacts,dur=0.45):
    best=0.0
    for ti in impacts:
        if ti<=t<ti+dur: best=max(best,1-(t-ti)/dur)
    return best

DESC=(T_LAND-2.0,T_LAND)
def dragon_state(t):
    if t<DESC[0] or T_DIED[0]<=t<STING[0]: return None
    if t>=STING[0]: return sting_dragon(t)
    st=dict(yaw=PI,eye=0.0,fire=0.0,jaw=0.0,tail=0.4*math.sin(t*2),breathe=math.sin(t*3))
    if t<T_LAND:                                                   # swoops down, wings flapping
        u=seg01(t,*DESC); y=7.5*(1-(0.6*u+0.4*sm(u))); return dict(st,base=(DRAGON_AT[0]+0.2*(1-u),y,DRAGON_AT[2]+1.2*(1-u)),fold=1.0,flap=0.9*math.sin((t-DESC[0])*13)+0.3,head=(0,2.3,2.2),hpitch=0.25)
    land=sm(seg01(t,T_LAND,T_LAND+0.45)); base=(DRAGON_AT[0],0.0,DRAGON_AT[2]); fold=lerp(1.0,0.25,land) if t>T_LAND+0.1 else 1.0; flap=0.5*(1-land)+(-0.1)*land
    H0=(0,2.5,2.15)
    if t<T_HOLSTER[0]:                                             # ROAR
        r=sm(seg01(t,T_LAND+0.2,T_LAND+0.45))*(1-sm(seg01(t,T_LAND+0.8,T_HOLSTER[0]+0.2)))
        return dict(st,base=base,fold=fold,flap=flap,head=lerp3(H0,(0,3.05,1.85),r),hpitch=lerp(0.2,-0.5,r),jaw=r,tail=0.5*math.sin(t*5))
    if t<T_SWORDLOOK[0]: return dict(st,base=base,fold=0.25,flap=-0.1,head=H0,hpitch=0.2)
    if t<T_SWORDLOOK[1]:                                           # looks down at the golden sword (eyes turn gold)
        a=sm(seg01(t,T_SWORDLOOK[0],T_SWORDLOOK[0]+0.9)); return dict(st,base=base,fold=0.25,flap=-0.1,head=lerp3(H0,(1.15,1.7,2.5),a),hpitch=lerp(0.2,0.55,a),hyaw=lerp(0.0,0.2,a),eye=sm(seg01(t,T_SWORDLOOK[0]+0.4,T_SWORDLOOK[0]+1.0)),jaw=0.12*a)
    if t<T_SILENCE[0]: bob=0.04*math.sin(t*6); return dict(st,base=base,fold=0.25,flap=-0.1,head=(1.15,1.7+bob,2.5),hpitch=0.55,hyaw=0.2,eye=1.0,jaw=0.15)
    if t<T_FIRE[0]:                                                # slowly swings round to the knight
        a=sm(seg01(t,T_SILENCE[0]+0.2,T_SILENCE[1])); return dict(st,base=base,fold=0.25,flap=-0.1,head=lerp3((1.15,1.7,2.5),(0.0,2.0,2.5),a),hpitch=lerp(0.55,0.1,a),hyaw=lerp(0.2,0.0,a),eye=lerp(1.0,0.0,a),jaw=0.1)
    a=seg01(t,*T_FIRE if t<T_FIRE[1] else (T_FIRE[0],T_FIRE[1])); f=sm(a)
    return dict(st,base=base,fold=0.25,flap=-0.1,head=(0.0,2.0,2.5),hpitch=0.1,hyaw=0.0,eye=0.0,jaw=sm(seg01(t,T_FIRE[0],T_FIRE[0]+0.35)),fire=f)
def sting_dragon(t):
    """after YOU DIED: chews, eyes the golden sword, tries to take it... OVERENCUMBERED, tips over"""
    base=(DRAGON_AT[0],0.0,DRAGON_AT[2]); st=dict(base=base,yaw=PI,fold=0.25,flap=-0.1,tail=0.4*math.sin(t*2),breathe=math.sin(t*3),eye=0.0,fire=0.0)
    if t<29.95: return dict(st,head=(0.0,2.4,2.2),hpitch=0.1,jaw=0.35+0.3*math.sin(t*18))
    if t<STING_BUZZ:
        a=sm(seg01(t,29.95,30.5)); return dict(st,head=lerp3((0.0,2.4,2.2),(1.15,1.45,2.9),a),hpitch=lerp(0.1,0.6,a),hyaw=lerp(0.0,0.2,a),eye=a,jaw=0.6*sm(seg01(t,30.3,30.55)))
    jolt=sm(seg01(t,STING_BUZZ,STING_BUZZ+0.15)); roll=1.5*sm(seg01(t,STING_BUZZ+0.25,STING_BUZZ+0.85))**1.4+(0.05*math.sin(t*14) if t>STING_BUZZ+0.85 else 0.0)
    back=sm(seg01(t,STING_BUZZ+0.15,STING_BUZZ+0.5))
    rr=min(1.0,roll/1.5); st=dict(st,fold=lerp(0.25,0.05,rr),flap=lerp(-0.1,0.6,rr))           # wings tuck in as it rolls
    return dict(st,head=lerp3(lerp3((1.15,1.45,2.9),(0.9,1.7,2.4),jolt),(0.0,1.7,2.0),back),hpitch=lerp(lerp(0.6,0.4,jolt),0.2,back),hyaw=0.2*(1-back),eye=1.0-jolt,jaw=0.3,roll=roll)
STING_BUZZ=30.6
def sword_state(t):
    """legendary sword: in the holster (None), falls point-first, sticks in the grass and wobbles"""
    if t<SWORD_DROP: return None
    ks=knight_state(SWORD_DROP-0.01); hip=np.array(kpoint(ks,(-0.22,0.9,0.08))); u=seg01(t,SWORD_DROP,SWORD_DROP+0.55)
    if u<1.0:
        pos=np.array(lerp3(tuple(hip),tuple(HILT),sm(u)))+np.array([0,0.15*math.sin(PI*u),0]); d=np.array([0.35*math.sin(u*7)*(1-u),-1.0,0.0]); d/=np.linalg.norm(d)
        return dict(hilt=tuple(pos),dir=tuple(d))
    tl=t-(SWORD_DROP+0.55); w=0.26*math.exp(-5*tl)*math.sin(26*tl); d=np.array([math.sin(w),-math.cos(w),0.0])
    return dict(hilt=tuple(np.array(SW_LAND)-d*1.12),dir=tuple(d))
def apple_state(t):
    """(centre, stage) or None when it is gone"""
    ks=knight_state(t)
    if t<APPLE_GRAB: return tuple(APPLE_C),0
    if t<T_EAT[0]+0.5 or t<BITES[0]: return tuple(np.array(khand(ks,1))+np.array([0,0.08,0.02])),0
    n=sum(1 for b_ in BITES if t>=b_+0.05); return tuple(np.array(khand(ks,1))+np.array([0,0.06 if n<3 else 0.0,0.0])),n
CORE_IN_HAND=lambda t: t>=BITES[2]+0.05

# ======================= shots =======================
def shake(V):
    sx=sy=0.0
    a=seg01(V,T_TREMOR[0],T_LAND)*2.2
    if T_TREMOR[0]<=V<T_LAND: sx+=a*math.sin(V*87); sy+=a*0.8*math.cos(V*71)
    k=bounce(V,[T_LAND],0.7)
    if k>0: sx+=9*k*math.sin(V*97); sy+=7*k*math.cos(V*83)
    if T_LAND+0.2<=V<T_HOLSTER[0]: sx+=1.6*math.sin(V*110)
    k=bounce(V,[T_RECOIL[0]+0.02,T_FLAIL[0]-0.1],0.35)
    if k>0: sx+=4*k*math.sin(V*90); sy+=3*k*math.cos(V*70)
    return (sx,sy)
def shot(V):
    sh=(0,0)
    if V<HOOK: u=sm(seg01(V,0,HOOK)); kz=knight_state(V)['base'][2]; return dict(cam=lerp3((-2.5,0.8,RZ-3.0),(-2.4,0.9,RZ-1.2),u),tgt=(0.0,1.0,kz+0.2),fov=50)
    if V<T_RECOIL[1]+0.0: return dict(cam=(-2.4,1.2,RZ-0.3),tgt=(0.0,0.75,-0.3),fov=44,shake=shake(V))                                   # insert: hand on the apple
    if V<T_GETUP[1]: return dict(cam=(-3.3,1.3,RZ-0.8),tgt=(0.0,0.7,RZ-0.8),fov=58,shake=shake(V))
    if V<T_THINK[1]: return dict(cam=(1.5,1.4,RZ+2.9),tgt=(0.0,1.2,RZ-0.5),fov=52)
    if V<T_MENU[1]: return dict(cam=(1.5,1.35,RZ+1.9),tgt=(0.0,1.85,RZ-0.5),fov=50)
    if V<T_DROP[1]: return dict(cam=(-2.9,0.8,RZ-2.1),tgt=(-0.4,0.6,RZ-0.7),fov=56)
    if V<T_DANCE[0]: return dict(cam=(1.6,1.25,RZ+2.9),tgt=(0.0,0.9,RZ-0.05),fov=54)
    if V<T_RETAKE[1]: return dict(cam=(XR-2.5,1.3,ZR+0.2),tgt=(XR-0.15,1.1,ZR-0.1),fov=48)
    if V<T_TREMOR[0]+1.4: return dict(cam=(XR+1.7,1.35,ZR+2.3),tgt=(XR,1.3,ZR),fov=46,shake=shake(V))                              # close: he looks around
    if V<T_HOLSTER[0]: return dict(cam=WIDE_CAM,tgt=WIDE_TGT,fov=58,shake=shake(V))                                               # wide side view: the dragon swoops in and lands
    if V<T_HOLSTER[1]: return dict(cam=(XR-2.5,1.2,ZR),tgt=(XR,1.15,ZR),fov=40,shake=shake(V))                                      # profile: his hand pats the empty holster
    if V<T_CORELOOK[0]: return dict(cam=WIDE_CAM,tgt=WIDE_TGT,fov=58)                                                              # wide: the dragon eyes the golden sword
    if V<T_CORELOOK[1]: return dict(cam=(XR+2.5,1.3,ZR),tgt=(XR,1.3,ZR),fov=40)                                                      # profile: he studies the apple core
    if V>=STING[0]: return dict(cam=(-5.0,1.7,1.6),tgt=(0.3,1.3,1.7),fov=58,shake=(4*bounce(V,[STING_BUZZ+0.8],0.5)*math.sin(V*90),0))
    return dict(cam=WIDE_CAM,tgt=WIDE_TGT,fov=58)
WIDE_CAM=(-6.4,2.0,0.7); WIDE_TGT=(0.2,2.0,0.7)

# ======================= render =======================
R=Renderer(W,H,fog=(120,180,235))
def lights_amb(V):
    sun=lerp3((255,250,230),(210,160,140),sm(seg01(V,T_TREMOR[0],T_LAND))); amb=lerp(0.62,0.42,sm(seg01(V,T_TREMOR[0],T_LAND)))
    if V>=T_FIRE[0]: amb=lerp(0.42,0.3,sm(seg01(V,T_FIRE[0],T_FLASH)))
    return [((20,40,-10),tuple(int(v) for v in sun),3.0)],amb
def _pile():
    st=dict(base=(0.0,0.0,RZ2),yaw=0.4,jig=0.0,ph=0.0); return tilt_quads(pack_quads(st),st,1.45)
PILE=_pile()
def render(V,sh):
    cam=Camera.look(sh['cam'],sh['tgt']); ks=knight_state(V); ds=dragon_state(V); ss=sword_state(V); ap=apple_state(V)
    sky=sky_color(V); R.fog=sky
    layers=[WORLD,flowers(),stump_quads(),pebbles(V)]+([prelit(knight_full(**ks),sh['cam'],warm=0.08)] if V<STING[0] else [PILE])
    props=[]
    if V>=STING[0]: props+=apple_quads((0.35,0.11,RZ2+0.35),3,0.6)
    elif ap is not None: props+=apple_quads(ap[0],ap[1],V*0.0)
    if ss is not None: props+=golden_sword(ss['hilt'],ss['dir'])
    layers.append(props)
    if ds is not None: layers.append(dragon(**{k:v for k,v in ds.items() if k in DR_KEYS}))
    layers.append(dust(V))
    L,amb=lights_amb(V)
    img,vi,zb=zrender(R,cam,layers,L,fov=sh['fov'],fog_start=14,fog_end=60,ambient=amb,shake=sh.get('shake',(0,0)),return_z=True)
    a=np.asarray(img).astype(np.float32); yy=np.linspace(0,1,H)[:,None,None]; sky_a=np.array(sky,np.float32)
    grad=(sky_a*(1-0.35*(1-yy))+np.array([255,255,255],np.float32)*0.18*yy)*np.ones((1,W,1),np.float32)
    a=np.where((zb==0)[...,None],grad,a)
    return post.ps1(Image.fromarray(np.clip(a,0,255).astype(np.uint8))),vi

# ======================= UI overlays =======================
def otext(d,s,x,y,col,sc=1):
    o=max(1,sc//2)
    for ox,oy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)): font.text(d,s,x+ox*o,y+oy*o,(0,0,0),sc,None)
    font.text(d,s,x,y,col,sc,None)
def ctext(d,s,y,col,sc=1,x0=0,w=W): otext(d,s,x0+(w-font.width(s,sc))//2,y,col,sc)
def panel(d,x0,y0,x1,y1,col,bg=(12,10,30)):
    d.rectangle([x0,y0,x1,y1],fill=bg,outline=col); d.rectangle([x0+2,y0+2,x1-2,y1-2],outline=tuple(int(c*0.5) for c in col))
HOOK_LINES=['WHY CAN RPG','HEROES CARRY','99 SWORDS BUT','NOT ONE APPLE?']
HIL={'RPG','99','SWORDS','ONE','APPLE?'}
def hook_text(d,V):
    if V>=SCR['dur']['N1']+0.2: return
    y=12
    for ln in HOOK_LINES:
        x=(W-font.width(ln,2))//2
        for wd in ln.split(' '): otext(d,wd,x,y,YEL if wd in HIL else WHT,2); x+=font.width(wd,2)+12
        y+=18
def inv_count(V):
    """(count, flash colour key) for the inventory badge"""
    if V<SWORD_DROP+0.4: return 100
    if V<APPLE_GRAB: return 99
    if V<BITES[2]+0.05: return 100
    if V<CORE_GET: return 99
    return 100
def hp_value(V): return 2 if V>=BITES[2]+0.05 else 1
def hud(d,V):
    if V<HOOK or T_MENU[0]<=V<T_MENU[1] or V>=T_FLASH: return
    n=inv_count(V); full=n>=100; col=RED if full else GRN
    if full and int(V*4)%2==0 and (T_RECOIL[0]<=V<T_MENU[0] or CORE_GET<=V<RETRY[1]+0.2): col=(255,120,100)
    panel(d,4,5,80,19,col); otext(d,'INV',9,9,WHT); otext(d,f'{n}/100',31,9,col)
    hp=hp_value(V); d.rectangle([4,23,80,32],fill=(12,10,30),outline=(200,200,210)); otext(d,'HP',7,24,WHT)
    d.rectangle([22,25,78,30],fill=(40,20,24))
    d.rectangle([22,25,22+int(56*hp/10),30],fill=RED if hp<3 else GRN)
    if V>=BITES[2]+0.05 and V<BITES[2]+0.9 and int(V*10)%2==0: d.rectangle([22,25,22+int(56*hp/10),30],fill=(255,255,255))
    if BITES[2]+0.05<=V<CORE_GET and int(V*8)%2==0: otext(d,'FREE SLOT!',4,36,GRN)
    elif T_RECOIL[1]<=V<BITES[2]+0.05: otext(d,'QUEST: EAT THE APPLE',4,36,YEL)
    elif CORE_GET<=V<T_LAND-0.2 and not (T_TREMOR[0]<=V): otext(d,'QUEST: GET SWORD BACK',4,36,YEL)
def banner(d,lines,y,col,bg=(40,6,8)):
    wmax=max(font.width(s) for s,_ in lines)+14; x0=(W-wmax)//2; h=len(lines)*11+8
    panel(d,x0,y,x0+wmax,y+h,col,bg)
    for i,(s,c) in enumerate(lines): ctext(d,s,y+5+i*11,c)
def slot_xy(r,c): return 31+c*12,34+r*12
ITEMS=['SWORD','ANOTHER SWORD','SWORD BUT BLUE','SWORD, AGAIN']
REASONS=["CAN'T DROP: STARTER","CAN'T DROP: CURSED","CAN'T DROP: SOULBOUND","CAN'T DROP: PRECIOUS"]
CURSOR_PATH=[(4,4),(6,7),(2,8),(7,2),(0,0)]; HOP=0.42; SWEEP_END=T_MENU[0]+0.2+4*HOP
DLG2=11.85
def menu(d,V):
    if not (T_MENU[0]<=V<T_MENU[1]): return
    a=sm(seg01(V,T_MENU[0],T_MENU[0]+0.2))*(1-sm(seg01(V,T_MENU[1]-0.25,T_MENU[1])))
    y0=int(lerp(-170,4,a)); panel(d,22,y0,158,y0+196,YEL)
    otext(d,'INVENTORY',30,y0+6,YEL); n=99 if V>=12.4 else 100; col=GRN if n==99 else RED
    otext(d,f'{n}/100',152-font.width(f'{n}/100'),y0+6,col)
    for r in range(10):
        for c in range(10):
            x,y=slot_xy(r,c); x-=6; y=y+y0-26+12
            d.rectangle([x,y,x+10,y+10],fill=(30,26,52),outline=(70,66,110))
            if (r,c)==(0,0):
                if V<12.7: g=GOLD if int(V*8)%2 else (255,244,170); d.line([x+2,y+8,x+8,y+2],fill=g,width=2); d.rectangle([x+1,y+6,x+4,y+8],fill=GOLD_D)
            else: d.line([x+2,y+8,x+8,y+2],fill=(BLADE_S if (r+c)%3 else BLADE_R),width=1)
    if V<10.9:                                                            # cursor sweep over the swords
        t=V-(T_MENU[0]+0.2); k=min(len(CURSOR_PATH)-2,max(0,int(t/HOP))); p0=CURSOR_PATH[k]; p1=CURSOR_PATH[k+1]; e=sm(seg01(t-k*HOP,HOP-0.08,HOP))
        r=lerp(p0[0],p1[0],e) if t>=0 else p0[0]; c=lerp(p0[1],p1[1],e) if t>=0 else p0[1]
        if t>=(len(CURSOR_PATH)-1)*HOP: r,c=0,0
    else: r,c=0,0
    x,y=slot_xy(r,c); x=int(x-6); y=int(y+y0-26+12); d.rectangle([x-1,y-1,x+11,y+11],outline=WHT if int(V*10)%2 else YEL)
    if V<SWEEP_END:
        t=max(0.0,V-(T_MENU[0]+0.2)); k=min(len(ITEMS)-1,int(t/HOP)); ctext(d,ITEMS[k],y0+170,WHT)
        if t-k*HOP>0.08 or t<0.01: ctext(d,REASONS[k],y0+182,RED if int(V*10)%2 else (255,140,120))      # junk items are locked
    elif V<12.7: ctext(d,'LEGENDARY GOLDEN SWORD',y0+170,GOLD); ctext(d,'DROPPABLE: YES',y0+182,GRN)
    else: ctext(d,'DROPPED: GOLDEN SWORD',y0+176,GRN)
    if 11.0<=V<12.75:                                                     # the warning dialog
        panel(d,14,y0+52,166,y0+128,RED,(30,8,10))
        second=V>=DLG2
        if not second: ctext(d,'ARE YOU SURE YOU WANT',y0+60,WHT); ctext(d,'TO DROP THIS ITEM?',y0+72,RED); yes=V>=11.45; press=V>=11.65
        else: ctext(d,'ARE YOU SURE SURE?',y0+60,WHT); ctext(d,"IT'S LEGENDARY.",y0+72,GOLD); yes=V>=12.15; press=V>=12.35
        for (lab,xx,sel) in (('YES',44,yes),('NO',112,not yes)):
            bc=YEL if sel and int(V*8)%2 else (WHT if sel else GRY)
            d.rectangle([xx-8,y0+98,xx+30,y0+114],fill=(60,20,24) if sel else (24,12,20),outline=bc)
            if press and lab=='YES': d.rectangle([xx-8,y0+98,xx+30,y0+114],fill=(255,240,200))
            tx=xx+(22-font.width(lab))//2+2
            if press and lab=='YES': font.text(d,lab,tx,y0+102,(30,10,10),1,None)
            else: otext(d,lab,tx,y0+102,bc)
        if not yes: otext(d,'>',0,0,(0,0,0)) if False else None
def banners(d,V):
    if T_RECOIL[0]<=V<T_RECOIL[0]+1.35:
        y=int(lerp(-30,52,sm(seg01(V,T_RECOIL[0],T_RECOIL[0]+0.15))));  banner(d,[('INVENTORY: 100/100',YEL)],y,CYAN,(12,10,30))
        if V>=T_RECOIL[0]+0.15 and int(V*7)%2==0: banner(d,[('OVERENCUMBERED!',RED)],y+34,RED)
        elif V>=T_RECOIL[0]+0.15: banner(d,[('OVERENCUMBERED!',(255,150,120))],y+34,(255,90,80))
    if T_FLAIL[0]-0.2<=V<T_FLAIL[1]+0.4: banner(d,[('MOVE SPEED: 0%',YEL)],110,YEL,(30,24,8))
    if RETRY[0]<=V<RETRY[0]+1.0:                                          # second try, the core is still an item
        y=int(lerp(-30,52,sm(seg01(V,RETRY[0],RETRY[0]+0.15)))); banner(d,[('INVENTORY: 100/100',YEL)],y,CYAN,(12,10,30))
        if V>=RETRY[0]+0.15: banner(d,[('OVERENCUMBERED!',RED if int(V*7)%2 else (255,150,120))],y+34,RED)
    if CORE_GET<=V<CORE_GET+1.0:
        a=sm(seg01(V,CORE_GET,CORE_GET+0.15)); y=int(lerp(-30,56,a)); panel(d,30,y,150,y+38,GRN,(8,26,12)); ctext(d,'ITEM GET!',y+6,GRN); ctext(d,'APPLE CORE',y+18,WHT); ctext(d,'INV 100/100',y+28,RED)
    if ITEM_GET[0]<=V<ITEM_GET[1]:
        a=sm(seg01(V,ITEM_GET[0],ITEM_GET[0]+0.15)); y=int(lerp(-30,56,a)); panel(d,30,y,150,y+38,GRN,(8,26,12)); ctext(d,'ITEM GET!',y+6,GRN); ctext(d,'APPLE',y+18,WHT); ctext(d,'INV 100/100',y+28,YEL)
    if BITES[2]+0.05<=V<BITES[2]+1.15:
        k=seg01(V,BITES[2]+0.05,BITES[2]+1.15); otext(d,'+1 HP',(W-font.width('+1 HP',2))//2,int(lerp(150,110,k)),GRN,2)
def warning(d,V):
    if not (T_TREMOR[0]+0.6<=V<T_LAND+0.2): return
    on=int(V*5)%2==0; c=RED if on else (120,20,20)
    d.rectangle([0,0,W,6],fill=c); d.rectangle([0,H-7,W,H],fill=c)
    if on: panel(d,18,60,162,92,RED,(40,6,8)); ctext(d,'WARNING!',64,WHT,2); ctext(d,'LARGE ENEMY NEARBY',82,RED)
def boss_bar(d,V):
    if not (T_LAND+0.9<=V<T_FLASH): return
    a=sm(seg01(V,T_LAND+0.9,T_LAND+1.2)); y=int(lerp(340,282,a)); otext(d,'DRAGON',8,y,RED); otext(d,'LV 99',W-8-font.width('LV 99'),y,YEL)
    d.rectangle([7,y+10,W-7,y+18],fill=(0,0,0),outline=(230,190,90)); d.rectangle([9,y+12,W-9,y+16],fill=RED); d.rectangle([9,y+12,W-9,y+13],fill=(255,140,120))
def emotes(d,vi,V,ks):
    top=np.array(kpoint(ks,(0,2.1,0)))
    def bubble(ch,col):
        p=R.project(tuple(top),vi)
        if p: x,y=int(p[0]),int(p[1]); d.rectangle([x-6,y-10,x+6,y+8],fill=WHT,outline=(0,0,0)); d.polygon([(x-2,y+8),(x+2,y+8),(x,y+11)],fill=WHT); font.text(d,ch,x-2,y-7,col,1,None)
    def bulb():
        p=R.project(tuple(top),vi)
        if p:
            x,y=int(p[0]),int(p[1]); d.ellipse([x-6,y-12,x+6,y],fill=YEL,outline=(0,0,0)); d.rectangle([x-3,y,x+3,y+4],fill=GRY,outline=(0,0,0))
            for a in range(5): ang=-PI/2+(a-2)*0.5; d.line([x+int(9*math.cos(ang)),y-6+int(9*math.sin(ang)),x+int(13*math.cos(ang)),y-6+int(13*math.sin(ang))],fill=YEL)
    if T_RECOIL[0]<=V<T_RECOIL[0]+0.9 or T_TIP[0]+0.5<=V<T_TIP[1]+0.3 or T_LAND-2.0<=V<T_LAND-1.3: bubble('!',RED)
    if 6.3<=V<6.75 or RETRY[0]+0.55<=V<RETRY[1]+0.3 or T_SILENCE[0]-0.1<=V<T_SILENCE[0]+0.7 or T_HOLSTER[1]<=V<T_HOLSTER[1]+0.8: bubble('?',BLUE if False else BLU)
    if BULB<=V<BULB+0.5 or 18.3<=V<18.8: bulb()
    for t0 in (T_HOLSTER[1]+0.1,T_CORELOOK[0]+0.3,T_FIRE[0]-0.3):                                      # sweat drops
        if t0<=V<t0+1.1:
            p=R.project(tuple(top-np.array([0,0.25,0])),vi)
            if p:
                for k in range(2): ph=((V-t0)*1.8+k*0.5)%1.0; x=int(p[0])+(-9 if k else 10); y=int(p[1])+4+int(16*ph); d.rectangle([x,y,x+1,y+3],fill=(150,210,255)); d.point((x,y-1),fill=(150,210,255))
    if T_RETAKE[0]<=V<T_RETAKE[0]+0.6:                                                                    # happy notes (+1 HP)
        for k in range(3):
            ph=((V-T_RETAKE[0])*1.6+k*0.33)%1.0; p=R.project(tuple(top+np.array([0.5*(k-1),-0.4+1.0*ph,0.0])),vi)
            if p: x,y=int(p[0]),int(p[1]); d.line([x,y-6,x,y+2],fill=WHT); d.rectangle([x-3,y+1,x,y+3],fill=WHT); d.line([x,y-6,x+3,y-4],fill=WHT)
    if T_EAT[0]+0.4<=V<BITES[2]+0.05 and V<T_EAT[0]+0.5+0.0: pass
    for b_ in BITES:                                                                                    # crunch text
        if b_<=V<b_+0.3: p=R.project(tuple(top-np.array([0,0.3,0])),vi); otext(d,'CRUNCH',int(p[0])-17,int(p[1])-6-int(8*(V-b_)/0.3),YEL) if p else None
    if SWORD_DROP+0.5<=V<SWORD_DROP+1.2:                                                                 # sparkle + clang where the sword lands
        p=R.project(tuple(SW_LAND+np.array([0,0.2,-0.2])),vi)
        if p:
            x,y=int(p[0]),int(p[1]); r=int(4+8*seg01(V,SWORD_DROP+0.5,SWORD_DROP+1.2))
            for a in range(8): ang=a*PI/4+V*3; d.line([x,y,x+int(r*math.cos(ang)),y+int(r*math.sin(ang))],fill=(255,244,170))
            otext(d,'CLANG!',x-17,y-20,YEL)
    if T_SWORDLOOK[0]+0.8<=V<T_CORELOOK[1]+0.5:                                                          # the sword keeps glinting
        p=R.project(tuple(HILT+np.array([0,0.15,0.0])),vi)
        if p and int(V*6)%2==0: x,y=int(p[0]),int(p[1]); d.line([x-4,y,x+4,y],fill=(255,244,170)); d.line([x,y-4,x,y+4],fill=(255,244,170))
def grade(img,V):
    a=np.asarray(img).astype(np.float32)
    if T_MENU[0]<=V<T_MENU[1]: m=sm(seg01(V,T_MENU[0],T_MENU[0]+0.2))*(1-sm(seg01(V,T_MENU[1]-0.2,T_MENU[1]))); a=a*(1-0.5*m)
    if T_FIRE[0]<=V<T_FLASH+0.2:                                                                         # orange glow of the fire charge, then a white-orange flash
        f=sm(seg01(V,T_FIRE[0],T_FLASH)); a=a*(1-0.25*f)+f*np.array([160,70,10])*0.35
        if V>=T_FLASH: k=1-seg01(V,T_FLASH,T_FLASH+0.2); a=a*(1-k)+k*np.array([255,230,190])
    return Image.fromarray(np.clip(a,0,255).astype(np.uint8))
def tooltip(d,vi,p3,lines,col):
    p=R.project(tuple(p3),vi)
    if not p: return
    w=max(font.width(s_) for s_,_ in lines)+10; h=len(lines)*10+6; x=int(max(3,min(W-w-3,p[0]-w/2))); y=int(max(40,p[1]-h-16))
    d.line([int(p[0]),int(p[1]),x+w//2,y+h],fill=col); panel(d,x,y,x+w,y+h,col,(12,10,26))
    for i,(s_,c) in enumerate(lines): otext(d,s_,x+5,y+4+i*10,c)
def sting_ui(d,vi,V):
    head=np.array(DRAGON_AT)+np.array([0,3.4,-2.0])
    if V<STING_BUZZ+1.4:
        k=seg01(V,STING[0],STING[0]+0.6); p=R.project(tuple(head),vi)
        if p and V<30.3: otext(d,'+1 KNIGHT',int(p[0])-26,int(p[1])-int(14*k),GRN)
    if V>=STING[0]+0.25:
        a=sm(seg01(V,STING[0]+0.25,STING[0]+0.4)); y=int(lerp(-30,40,a)); col=RED; banner(d,[('DRAGON INV: 100/100',RED)],y,CYAN,(12,10,30))
    if V>=STING_BUZZ:
        a=sm(seg01(V,STING_BUZZ,STING_BUZZ+0.15)); y=int(lerp(-30,74,a)); banner(d,[('OVERENCUMBERED!',RED if int(V*7)%2 else (255,150,120))],y,RED)
    if V>=STING_BUZZ+0.9: banner(d,[('MOVE SPEED: 0%',YEL)],98,YEL,(30,24,8))
def died(d,V):
    if V<T_DIED[0]: return
    a=sm(seg01(V,T_DIED[0],T_DIED[0]+0.4)); y=int(lerp(110,128,a))
    ctext(d,'YOU DIED',y,(int(60+170*a),int(10+20*a),int(10+20*a)),3)
def tooltips(d,vi,V,ks):
    if T_SWORDLOOK[0]+0.5<=V<T_CORELOOK[0]: tooltip(d,vi,HILT+np.array([0,0.3,0.0]),[('GOLDEN SWORD',GOLD),('X99 DMG VS DRAGONS',RED)],GOLD)
    if T_CORELOOK[0]+0.7<=V<T_CORELOOK[1]: tooltip(d,vi,np.array(khand(ks,1))+np.array([0,0.12,0]),[('APPLE CORE',WHT),('HEALS: 0 HP',RED)],WHT)
def achievement(d,V):
    if 4.8<=V<6.5:
        a=sm(seg01(V,4.8,5.0))*(1-sm(seg01(V,6.3,6.5))); y=int(lerp(330,250,a)); panel(d,16,y,164,y+30,GOLD,(30,22,6)); ctext(d,'ACHIEVEMENT UNLOCKED',y+6,GOLD); ctext(d,'TURTLE MODE',y+17,WHT)
def hook_hp(d,V):
    if V>=HOOK: return
    col=RED if int(V*4)%2 else (120,20,20); panel(d,6,296,76,312,col,(20,8,10)); otext(d,'HP 1/10',12,300,col)
def frame(Vv): return frame_story(story_t(Vv))
def frame_story(V):
    if V>=BLACK: return Image.new('RGB',(W,H),(0,0,0))
    if T_DIED[0]<=V<STING[0]:
        img=Image.new('RGB',(W,H),(int(40*(1-seg01(V,T_DIED[0],STING[0]))),0,0)); d=ImageDraw.Draw(img); died(d,V); return img
    if V>=STING[0]:
        sh=shot(V); img,vi=render(V,sh); d=ImageDraw.Draw(img); sting_ui(d,vi,V); return img
    sh=shot(V); img,vi=render(V,sh); img=grade(img,V); d=ImageDraw.Draw(img); ks=knight_state(V)
    emotes(d,vi,V,ks); tooltips(d,vi,V,ks); hud(d,V); banners(d,V); achievement(d,V); menu(d,V); warning(d,V); boss_bar(d,V)
    if V<HOOK: hook_text(d,V); hook_hp(d,V)
    return img

# ======================= QA manifest (tools/qa/scene_qa.py, PIPELINE.md) =======================
def _kn(t): return knight_state(t) if t<T_DIED[0] else None
def _dr(t): return dragon_state(t)
TREES=[]
def _geom(t,name,st,V):
    out=[]
    if V[:,1].min()<-0.04: out.append(('floor',f'{name} under the floor'))
    m=(np.abs(V[:,0])<0.42)&(np.abs(V[:,2])<0.42)&(V[:,1]<STUMP_H-0.03)&(V[:,1]>0.1)
    if m.any(): out.append(('intersect',f'{name} inside the stump'))
    return out
def _extra(t):
    out=[]; ks=knight_state(t); ds=dragon_state(t); ap=apple_state(t); ss=sword_state(t)
    if t>=T_DIED[0]: return out
    for sx in (-1,1):                                                                                   # arms never stretch
        sh_=np.array(kpoint(ks,(sx*0.22,1.27,0))); dd=np.linalg.norm(np.array(khand(ks,sx))-sh_)
        if dd>0.66 and not ks.get('tilt'): out.append(('stretch',f'knight arm stretched beyond its length ({dd:.2f} m)'))
    if abs(t-RETRY[0])<0.5/FPS and np.linalg.norm(np.array(khand(ks,-1))-HILT)>0.22: out.append(('sword',f'his left hand is {np.linalg.norm(np.array(khand(ks,-1))-HILT):.2f} m from the hilt when he tries to take it'))
    if abs(t-HOOK)<0.5/FPS and np.linalg.norm(np.array(khand(ks,1))-APPLE_C)>0.16: out.append(('apple',f'hand is {np.linalg.norm(np.array(khand(ks,1))-APPLE_C):.2f} m from the apple when he touches it'))
    if ap is not None and t>=APPLE_GRAB and np.linalg.norm(np.array(ap[0])-np.array(khand(ks,1)))>0.16: out.append(('apple','apple is not in his hand'))
    if abs(t-(APPLE_GRAB-0.5/FPS))<0.5/FPS and np.linalg.norm(np.array(khand(ks,1))-APPLE_C)>0.2: out.append(('apple',f'his hand is {np.linalg.norm(np.array(khand(ks,1))-APPLE_C):.2f} m from the apple when he grabs it'))
    if ss is not None:
        h=np.array(ss['hilt']); d=np.array(ss['dir']); tip=h+d/np.linalg.norm(d)*1.12
        if t<SWORD_DROP+0.02 and False: pass
        if abs(t-(SWORD_DROP+1/FPS))<0.5/FPS and np.linalg.norm(h-np.array(kpoint(knight_state(SWORD_DROP-0.01),(-0.22,0.9,0.08))))>0.3: out.append(('sword','sword does not leave the holster'))
        if t>=SWORD_DROP+0.6:
            for u_ in np.linspace(0,1.12,10):
                p_=h+d/np.linalg.norm(d)*u_
                if abs(p_[0])<0.47 and abs(p_[2])<0.47 and p_[1]<STUMP_H-0.02: out.append(('sword','sword inside the stump')); break
                if np.linalg.norm(np.array([p_[0]-ks['base'][0],p_[2]-ks['base'][2]]))<0.3 and p_[1]<1.5: out.append(('sword','sword inside the knight')); break
            if p_[1]<-0.02 or h[1]<-0.02: out.append(('sword','sword under the floor'))
    if ds is not None:                                                                                    # the dragon head never touches the knight
        Q=dragon(**{k:v for k,v in ds.items() if k in DR_KEYS}); Vd=np.array([p for q in Q for p in q['p']])
        KV=np.array([p for q in knight_full(**ks) for p in q['p']]); dmin=min(np.linalg.norm(KV-v,axis=1).min() for v in Vd[::7])
        if dmin<0.35: out.append(('intersect',f'dragon is {dmin:.2f} m from the knight'))
    if t>=T_LAND and t<T_LAND+0.02 and ds is not None and ds['base'][1]>0.05: out.append(('dragon','dragon is still in the air at landing'))
    return out
QA=dict(fps=FPS,dur=DUR,W=W,frame=frame_story,
    chars={'knight':(_kn,knight_full,'sword','hip'),'dragon':(_dr,dragon,'_none',1.0)},
    geom=_geom,extra=_extra,camera=lambda t: shot(t)['cam'],min_cam_dist=0.45,
    camera_ok=lambda p: p[1]>0.12 and not (abs(p[0])<0.5 and abs(p[2])<0.5 and p[1]<STUMP_H+0.05),
    scenes=[dict(id='hook',t0=0.0,t1=HOOK,action='knight lumbers under 99 swords toward the apple and reaches for it'),
            dict(id='touch',t0=HOOK,t1=T_RECOIL[1],action='insert: touches the apple; INVENTORY 100/100; OVERENCUMBERED; yanked back'),
            dict(id='tip-over',t0=T_RECOIL[1],t1=T_GETUP[1],action='the pack tips him onto his back (turtle mode); flails; rocks back up'),
            dict(id='think',t0=T_GETUP[1],t1=T_MENU[0],action='catches his breath; lightbulb'),
            dict(id='menu',t0=T_MENU[0],t1=T_MENU[1],action='inventory menu; joke sword names; golden sword; ARE YOU SURE x2; YES'),
            dict(id='drop',t0=T_MENU[1],t1=T_DROP[1],action='the golden sword falls from the holster and lands on the grass'),
            dict(id='pick-eat',t0=T_DROP[1],t1=T_RETAKE[0],action='steps up, picks up the apple, ITEM GET, three bites, +1 HP'),
            dict(id='retake',t0=T_RETAKE[0],t1=T_RETAKE[1],action='joy; free slot... but the core fills it: he tries to take the sword back, OVERENCUMBERED'),
            dict(id='tremor',t0=T_RETAKE[1],t1=T_TREMOR[0]+1.4,action='ground shakes; he looks around'),
            dict(id='dragon',t0=T_TREMOR[0]+1.4,t1=T_HOLSTER[0],action='wide: the dragon swoops in and lands, roars'),
            dict(id='holster',t0=T_HOLSTER[0],t1=T_HOLSTER[1],action='profile: he pats the empty holster'),
            dict(id='sword-look',t0=T_HOLSTER[1],t1=T_CORELOOK[0],action='wide: the dragon eyes the golden sword'),
            dict(id='core-look',t0=T_CORELOOK[0],t1=T_CORELOOK[1],action='profile: he looks at the apple core'),
            dict(id='fire',t0=T_CORELOOK[1],t1=T_DIED[0],action='wide: silence; the dragon turns, its mouth glows; flash'),
            dict(id='died',t0=T_DIED[0],t1=STING[0],action='YOU DIED'),
            dict(id='stinger',t0=STING[0],t1=DUR,action='dragon chews; DRAGON INV 100/100; reaches for the sword; OVERENCUMBERED; tips over')],
    weapon_events=[('knight',SWORD_DROP,'hip','none')],
    texts=lambda: [('hook',x,2) for x in HOOK_LINES]+[('ui',s_,1) for s_ in ('INVENTORY: 100/100','OVERENCUMBERED!','MOVE SPEED: 0%','ARE YOU SURE YOU WANT','TO DROP THIS ITEM?','LEGENDARY GOLDEN SWORD','ATK 999   EQUIPPED','DROPPED: GOLDEN SWORD','ITEM GET!','INV 100/100','QUEST: EAT THE APPLE','QUEST: GET SWORD BACK','FREE SLOT!','APPLE CORE','LARGE ENEMY NEARBY','CRUNCH','CLANG!','ARE YOU SURE SURE?',"IT'S LEGENDARY.",'DROPPABLE: YES',*REASONS,'GOLDEN SWORD','X99 DMG VS DRAGONS','APPLE CORE','HEALS: 0 HP','ACHIEVEMENT UNLOCKED','TURTLE MODE','HP 1/10','+1 KNIGHT','DRAGON INV: 100/100')+tuple(ITEMS)]
          +[('ui',s_,2) for s_ in ('+1 HP','WARNING!')]+[('ui','YOU DIED',3),('ui','DRAGON',1)])

TEST=os.environ.get('TEST')
if TEST and __name__=='__main__':
    ims=[frame(float(x)) for x in TEST.split(',')]; shp=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): shp.paste(im,(i*182,0))
    shp.resize((shp.width*2,640),Image.NEAREST).save('test.png'); sys.exit()


# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=71); sr=s.sr; n=s.n; M=np.zeros(n); AMB=np.zeros(n)
    def note(buf,t0,m,d,v,wave='sq',duty=0.5,dec=3.0,att=0.005):
        f=440*2**((m-69)/12); tt=s.T(d); ph=(f*tt)%1
        x=np.where(ph<duty,1.0,-1.0) if wave=='sq' else (4*np.abs(ph-0.5)-1 if wave=='tri' else np.sin(2*np.pi*ph))
        env=np.minimum(1,tt/att)*np.exp(-tt*dec); i=int(t0*sr); j=min(n,i+len(tt)); buf[i:j]+=(x*env*v)[:j-i]
    def nb(t0,d,lo,hi,v,seed,shape=2): s.place(s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v)
    def clank(t0,v=0.1,seed=0): tt=s.T(0.5); s.place(sum(np.sin(2*np.pi*f*tt)*np.exp(-tt*k) for f,k in ((620,9),(1500,13),(2900,19)))*0.35+s.filt_short(s.noise(0.5,seed),lo=2000,hi=8000)*np.exp(-tt*30),t0,v)
    def rattle(t0,d,v=0.03,seed=0):
        r=np.random.default_rng(seed)
        for k in range(int(d/0.04)): tt=s.T(0.04); s.place(s.filt_short(s.noise(0.04,seed*77+k),lo=1800,hi=7000)*np.exp(-tt*90),t0+k*0.04+r.uniform(0,0.012),v*r.uniform(0.4,1.0))
    def thud(t0,f=55,v=0.25,d=0.5): tt=s.T(d); s.place(np.sin(2*np.pi*f*tt*(1-0.35*tt/d))*np.exp(-tt*9)+s.filt_short(s.noise(d,int(t0*13)),lo=50,hi=600)*np.exp(-tt*12)*0.5,t0,v)
    def whoosh(t0,d=0.4,v=0.05,seed=0,lo=300,hi=3500): nb(t0,d,lo,hi,v,seed)
    def tick(t0,v=0.03): tt=s.T(0.03); s.place(np.sin(2*np.pi*2300*tt)*np.exp(-tt*120),t0,v)
    def buzzer(t0,d=0.45,v=0.12):
        tt=s.T(d); s.place(np.where(np.sin(2*np.pi*98*tt)>0,1.0,-1.0)*(0.6+0.4*np.sign(np.sin(2*np.pi*22*tt)))*np.exp(-tt*2.5),t0,v)
    def step_h(t0,v=0.06,seed=0): thud(t0,70,v,0.25); rattle(t0,0.15,0.03,seed)
    def crunch(t0,v=0.12,seed=0):
        for k in range(3): tt=s.T(0.06); s.place(s.filt_short(s.noise(0.06,seed*9+k),lo=1500,hi=5500)*np.exp(-tt*45),t0+k*0.05,v)
        nb(t0,0.12,200,1200,v*0.4,seed*5)
    def chime(t0,notes,v=0.04,step=0.07,d=0.3):
        for k,m in enumerate(notes): note(M,t0+k*step,m,d,v,'sq',0.25,6)
    def growl(t0,d=0.9,v=0.12,f=60):
        tt=s.T(d); mod=0.6+0.4*np.sin(2*np.pi*9*tt); s.place(s.filt_short(np.sign(np.sin(2*np.pi*np.cumsum(f+10*np.sin(2*np.pi*7*tt))/sr))*0.6+s.noise(d,int(t0*17))*0.3,hi=500)*mod*np.sin(np.pi*tt/d),t0,v)
    def grunt(t0,v=0.07,f=120,d=0.25):
        tt=s.T(d); x=np.where((f*(1-0.3*tt/d)*tt)%1<0.5,1.0,-1.0); s.place(s.filt_short(x,lo=100,hi=900)*np.exp(-tt*8),t0,v)
    def roar(t0,d,v=0.2):
        tt=s.T(d); ph=np.cumsum(88+30*np.sin(2*np.pi*5.5*tt)+25*np.sin(np.pi*tt/d))/sr
        x=np.sign(np.sin(2*np.pi*ph))*0.6+s.filt_short(s.noise(d,3),lo=200,hi=2500)*0.5
        s.place(s.filt_short(x,hi=2400)*np.sin(np.pi*tt/d)**0.6,t0,v)
    def siren(t0,d,v=0.04):
        tt=s.T(d); s.place(np.where(np.sin(2*np.pi*np.cumsum(440+300*(np.floor(tt/0.2)%2))/sr)>0,1.0,-1.0)*np.sin(np.pi*tt/d)**0.3,t0,v)
    def heartbeat(t0,v=0.3): thud(t0,48,v,0.3); thud(t0+0.2,44,v*0.7,0.3)
    AMB+=s.filt(s.rng.normal(0,1,n),lo=80,hi=800)*0.012                                              # breeze
    # ---------- music ----------
    def jaunty(a,b,v=1.0,root=60,step=0.2,minor=False):
        sc=[0,2,3,5,7,8,10,12] if minor else [0,2,4,5,7,9,11,12]; pat=[0,2,4,2,4,5,4,2,0,1,2,4,7,5,4,2]; bass=[0,0,4,4,5,5,4,4]; k=0; tc=a
        while tc<b-1e-6:
            note(M,tc,root+12+sc[pat[k%16]%8],step*0.7,0.02*v,'sq',0.25,9)
            if k%2==0: note(M,tc,root-12+sc[bass[(k//2)%8]%8],step*1.6,0.05*v,'tri',dec=5)
            k+=1; tc+=step
    for k in range(7): note(M,0.1+k*0.5,[36,43,36,43,34,41,36][k],0.4,0.07,'tri',dec=4)            # heavy tuba march (hook)
    for k in range(7): note(M,0.35+k*0.5,67,0.12,0.02,'sq',0.25,12)
    for k,m in enumerate((57,56,55,54)): note(M,3.55+k*0.17,m,0.2,0.04,'sq',0.5,6)               # sad-trombone-ish after the first bounce
    jaunty(4.6,7.2,0.45,root=57,step=0.24,minor=True)
    for k,m in enumerate([69,72,76,72,69,72,76,81]*5): note(M,T_MENU[0]+0.05+k*0.25,m,0.2,0.016,'sq',0.25,7)      # curious menu arpeggio
    jaunty(13.3,15.7,0.7,step=0.19)
    for k,m in enumerate((72,76,79,84,88,91)): note(M,15.0+k*0.07,m,0.25,0.035,'sq',0.25,6)       # ITEM GET
    jaunty(15.7,17.7,0.6,step=0.17)
    jaunty(T_RETAKE[0],18.7,1.1,root=62,step=0.15)                                                # +1 HP joy
    for k,m in enumerate((72,76,79,84)): note(M,T_RETAKE[0]+k*0.09,m,0.25,0.04,'sq',0.25,5)
    jaunty(18.7,RETRY[0],0.6,root=60,step=0.19)                                                   # hopeful: he goes for the sword
    for k,m in enumerate((64,63,62,61)): note(M,RETRY[0]+0.35+k*0.14,m,0.2,0.04,'sq',0.5,6)         # ...or not
    for k in range(int((T_TREMOR[1]-T_TREMOR[0])/0.5)): note(M,T_TREMOR[0]+k*0.5,28+(k%2)*2,0.45,0.04+0.01*k,'tri',dec=2)
    for k,tt_ in enumerate(np.arange(23.0,26.5,0.6)): note(M,tt_,31-(k%2),0.55,0.04,'tri',dec=2)
    # ---------- sfx ----------
    for k in range(7): step_h(0.1+k*0.28,0.05,k)                                                    # hook: heavy steps + clanking swords
    rattle(0.0,2.0,0.03,50); growl(2.8,0.6,0.05,90); grunt(3.2,0.07)                                # strain
    for k in range(7): note(M,0.3+k*0.5,95,0.06,0.012,'sq',0.5,30)                                 # low-HP beep
    growl(1.5,0.6,0.06,48)                                                                           # stomach
    buzzer(3.55,0.45,0.12); rattle(3.5,0.8,0.05,51); whoosh(3.6,0.35,0.04,52)
    for k in range(4): step_h(3.85+k*0.18,0.05,60+k)
    grunt(4.05,0.09,140,0.4); whoosh(4.0,0.5,0.05,53)
    clank(4.45,0.16,1); thud(4.5,45,0.4,0.6); rattle(4.45,0.8,0.08,54)                              # the big fall
    for k,m in enumerate((79,84,88,91)): note(M,4.85+k*0.07,m,0.2,0.03,'sq',0.25,6)             # ACHIEVEMENT UNLOCKED
    for k in range(int(1.0/0.28)): rattle(4.65+k*0.28,0.25,0.05,80+k); grunt(4.7+k*0.28,0.04,150+10*k)
    for k in range(4): clank(5.65+k*0.25,0.05,10+k); grunt(5.7+k*0.25,0.06,130)                     # rocking up
    thud(6.55,60,0.25,0.3); rattle(6.55,0.6,0.07,55)
    growl(6.7,0.5,0.09,50)                                                                           # stomach
    for k,m in enumerate((79,84,91)): note(M,BULB+0.05+k*0.05,m,0.2,0.03,'sq',0.25,6)             # lightbulb ding
    whoosh(T_MENU[0],0.3,0.04,90,800,5000); tick(T_MENU[0]+0.1,0.04)
    for k in range(4): note(M,T_MENU[0]+0.2+k*HOP+0.06,45,0.12,0.06,'sq',0.5,9); tick(T_MENU[0]+0.2+k*HOP+HOP-0.08,0.035)   # 'bzzt' CAN'T DROP + cursor hop
    for k,m in enumerate((84,91,96,103)): note(M,SWEEP_END+k*0.06,m,0.25,0.03,'sq',0.25,5)       # golden slot: DROPPABLE
    for k in range(3): note(M,11.0+k*0.2,70 if k!=1 else 64,0.12,0.05,'sq',0.5,10)                  # warning dialog
    for f_ in (110,164.8,220): note(M,11.0,69+12*math.log2(f_/440)+0,1.4,0.03,'sin',dec=0.8,att=0.3)
    tick(11.45,0.05); note(M,11.65,55,0.25,0.06,'sq',0.5,6); nb(11.65,0.2,1500,8000,0.03,89)                  # first YES
    for k in range(2): note(M,DLG2+k*0.15,76+k*3,0.12,0.05,'sq',0.5,10)                            # 'are you SURE sure?'
    tick(12.15,0.05); note(M,12.35,48,0.4,0.07,'sq',0.5,4); note(M,12.35,60,0.25,0.05,'sq',0.5,6); nb(12.35,0.3,1500,8000,0.04,91)      # YES
    chime(12.7,(72,79,84),0.035)
    whoosh(SWORD_DROP+0.05,0.5,0.05,92,600,4000)
    clank(SWORD_DROP+0.55,0.2,93); clank(SWORD_DROP+0.7,0.1,94)
    for k,f in enumerate((2600,3300,4100)): tt=s.T(0.8); s.place(np.sin(2*np.pi*f*tt)*np.exp(-tt*5),SWORD_DROP+0.6+k*0.07,0.03)        # golden ring
    nb(SWORD_DROP+0.8,0.5,300,2500,0.04,95)                                                         # relief 'ahh'
    for k in range(5): rattle(14.0+k*0.2,0.15,0.03,100+k)
    nb(14.35,0.4,500,3000,0.03,96)                                                                  # reaching
    tt=s.T(0.1); s.place(np.sin(2*np.pi*np.cumsum(500+1200*tt/0.1)/sr)*np.exp(-tt*25),APPLE_GRAB,0.06)  # apple pop
    for b_ in BITES: crunch(b_,0.14,int(b_*10))
    chime(BITES[2]+0.05,(76,81,85,88,93),0.04,0.06)                                                 # +1 HP
    for k in range(3): grunt(16.0+k*0.2,0.03,160)                                                   # happy 'mm'
    for k in range(2): thud(T_RETAKE[0]+0.12+k*0.25,60,0.1,0.15); rattle(T_RETAKE[0]+0.1+k*0.25,0.15,0.04,130+k)            # two joyful hops
    chime(CORE_GET,(72,76,79),0.035)                                                                # ITEM GET: apple core (FREE SLOT gone)
    for k,m in enumerate((79,84,91)): note(M,18.3+k*0.05,m,0.2,0.03,'sq',0.25,6)                   # lightbulb: the sword!
    for k in range(4): step_h(18.75+k*0.12,0.04,120+k)
    whoosh(19.15,0.3,0.04,97)
    buzzer(RETRY[0],0.45,0.13); clank(RETRY[0]+0.02,0.08,131); rattle(RETRY[0]+0.05,0.5,0.06,132); grunt(RETRY[0]+0.25,0.07,140,0.3)  # OVERENCUMBERED again
    # tremor + dragon
    r=np.random.default_rng(8); rum=s.filt_short(s.noise(T_LAND-T_TREMOR[0],77),hi=90)*np.linspace(0.0,1.0,int((T_LAND-T_TREMOR[0])*sr))**1.5*0.5; i0=int(T_TREMOR[0]*sr); s.L[i0:i0+len(rum)]+=rum; s.R[i0:i0+len(rum)]+=rum
    for k in range(14): tick(T_TREMOR[0]+0.4+k*0.17+r.uniform(0,0.05),0.03)
    for k in range(int((T_LAND-DESC[0])/0.483)): whoosh(DESC[0]+k*0.483,0.35,0.05+0.015*k,200+k,80,900)         # wing beats
    siren(T_TREMOR[0]+0.6,T_LAND-T_TREMOR[0]-0.4,0.035)
    thud(T_LAND,40,0.55,0.9); clank(T_LAND+0.02,0.08,7); nb(T_LAND,0.6,50,500,0.2,98)              # landing boom
    roar(T_LAND+0.25,1.0,0.22)
    for t0 in (23.45,23.58,23.7): clank(t0,0.07,int(t0*10))                                         # pat pat on the empty holster
    growl(T_SWORDLOOK[0]+0.1,1.1,0.1,55)
    for k,f in enumerate((3000,3900)): tt=s.T(0.6); s.place(np.sin(2*np.pi*f*tt)*np.exp(-tt*6),T_SWORDLOOK[0]+0.7+k*0.08,0.03)             # gold glint
    for k,m in enumerate((84,79)): note(M,T_SWORDLOOK[0]+0.5+k*0.08,m,0.15,0.03,'sq',0.25,8)          # tooltip pop
    for k,m in enumerate((60,57)): note(M,T_CORELOOK[0]+0.7+k*0.1,m,0.2,0.04,'sq',0.5,6)               # 'heals: 0' bwomp
    tt=s.T(0.3); s.place(np.sin(2*np.pi*np.cumsum(1400+500*tt/0.3)/sr)*np.exp(-tt*10),25.7,0.05)     # knight's squeak
    M[int(T_SILENCE[0]*sr):int(T_FIRE[0]*sr)]=0
    for t0 in (T_SILENCE[0]+0.3,T_SILENCE[0]+0.95): heartbeat(t0,0.3)
    s.L[int(T_SILENCE[0]*sr):int(T_FIRE[0]*sr)]*=0.25; s.R[int(T_SILENCE[0]*sr):int(T_FIRE[0]*sr)]*=0.25
    tt=s.T(T_FLASH-T_FIRE[0]); s.place(np.sin(2*np.pi*np.cumsum(120+700*(tt/(T_FLASH-T_FIRE[0]))**2)/sr)*(tt/(T_FLASH-T_FIRE[0]))*0.5+s.filt_short(s.noise(T_FLASH-T_FIRE[0],99),lo=300,hi=4000)*(tt/(T_FLASH-T_FIRE[0]))*0.5,T_FIRE[0],0.14)   # fire charge
    thud(T_FLASH,38,0.7,0.7); nb(T_FLASH,0.5,60,3000,0.25,98)                                       # flash boom
    tt=s.T(2.0); s.place((np.sin(2*np.pi*55*tt)+0.7*np.sin(2*np.pi*110.5*tt)+0.4*np.sin(2*np.pi*165*tt))*np.exp(-tt*1.4),T_DIED[0],0.3)   # YOU DIED gong
    for k,m in enumerate((67,64,60)): note(M,28.85+k*0.16,m,0.2,0.06,'sq',0.5,6)                    # game over
    # ---------- the stinger ----------
    for k in range(4): crunch(STING[0]+0.05+k*0.14,0.09,300+k)                                   # chomp chomp
    chime(STING[0]+0.3,(72,76,79),0.035)                                                            # +1 KNIGHT / item get
    growl(29.95,0.6,0.08,60)
    for k,f in enumerate((3000,3900)): tt=s.T(0.5); s.place(np.sin(2*np.pi*f*tt)*np.exp(-tt*6),30.25+k*0.08,0.03)
    buzzer(STING_BUZZ,0.45,0.13)
    for k,m in enumerate((57,56,55,54)): note(M,STING_BUZZ+0.3+k*0.17,m,0.2,0.04,'sq',0.5,6)
    thud(STING_BUZZ+0.8,36,0.6,0.8); rattle(STING_BUZZ+0.8,0.6,0.06,310); nb(STING_BUZZ+0.8,0.5,50,500,0.15,311)   # the dragon topples
    roar(STING_BUZZ+1.0,0.6,0.08)
    for k,(m,d_) in enumerate(((60,0.3),(59,0.3),(58,0.3),(57,0.9))):                            # wah wah wah waaah
        tc=31.25+k*0.2 if k<3 else 31.85; f=440*2**((m-69)/12); tt=s.T(d_)
        s.place((np.sin(2*np.pi*np.cumsum(f*(1+0.012*np.sin(2*np.pi*5*tt)))/sr)+0.4*np.sin(2*np.pi*np.cumsum(2*f*np.ones_like(tt))/sr))*np.minimum(1,tt/0.03)*np.exp(-tt*(2 if k<3 else 1.0)),tc,0.05)
    # ---------- voice ----------
    NB=np.zeros(n); duck=np.ones(n)
    a,ar=_sf.read(os.path.join(TTS_DIR,'ap','N1.wav')); a=a if a.ndim==1 else a.mean(1)
    a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a); act=a[np.abs(a)>0.02]; a=a/(np.sqrt((act**2).mean())+1e-9)*0.2
    i=int(0.05*sr); j=min(n,i+len(a)); NB[i:j]+=a[:j-i]; duck[max(0,i-int(0.05*sr)):min(n,j+int(0.1*sr))]=0.4
    duck=np.convolve(duck,np.ones(2400)/2400,'same')
    s.L+=2.0*M*duck+AMB; s.R+=2.0*np.roll(M,240)*duck+np.roll(AMB,700)
    s.reverb(0.14,length=1.2,decay=4.0)
    pk=max(np.abs(s.L).max(),np.abs(s.R).max()); gv=pk*1.05/np.abs(NB).max()
    s.L=s.L*(0.6+0.4*duck)+NB*gv; s.R=s.R*(0.6+0.4*duck)+NB*gv
    st=np.stack([s.L,s.R],1); st[int(BLACK*sr):]*=np.linspace(1,0.0,len(st)-int(BLACK*sr))[:,None]**0.5
    keep=[]; prev=0
    for a_,b_ in SKIPS: keep.append(st[int(prev*sr):int(a_*sr)]); prev=b_
    keep.append(st[int(prev*sr):]); x=int(0.03*sr); out=keep[0]
    for sg in keep[1:]:
        w=np.linspace(0,1,x)[:,None]; out=np.concatenate([out[:-x],out[-x:]*(1-w)+sg[:x]*w,sg[x:]])
    st=out/np.max(np.abs(out))*0.9; _sf.write(path,st,sr,subtype='PCM_16'); return path
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'one_apple.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'ap_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.96,vignette=0.22,grain=1.5,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(post.upscale(frame(f/FPS),S),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
