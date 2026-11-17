"""FINAL BOSS - "Why do final bosses never leave their rooms?"  PS1 dark-fantasy mystery short, 9:16. Fully procedural (nightkit).
Experiment A = 30 s cut (this file, VERSION=A). The 0-4 s hook (hook_* functions + HOOK_* constants) is shared with
Experiment B (60 s) and must stay identical: same camera, models, narrator line N1 and music motif.
Voices: python tools/tts/fb.py  ->  $TTS_DIR/fb/*.wav
Run: TEST=0.2,5,10 python examples/final_boss.py -> test.png | PART=a:b (frames -> out/fb_a.mp4) | PART=audio"""
import os, sys, math, json
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','tts'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, quad, tiled_plane, wall_region
from nightkit.engine import box as _engine_box
from nightkit import motion, post, font
from nightkit.zraster import zrender
from nightkit.audio import Sound

OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6; DUR=30.5; N=int(round(DUR*FPS))
PI=math.pi; sm=motion.smooth
def seg01(t,a,b): return max(0.0,min(1.0,(t-a)/(b-a)))
def lerp(a,b,u): return a+(b-a)*u
def lerp3(a,b,u): return tuple(a[i]+(b[i]-a[i])*u for i in range(3))
def Rx(a): c,s=math.cos(a),math.sin(a); return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def Ry(a): c,s=math.cos(a),math.sin(a); return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def Rz(a): c,s=math.cos(a),math.sin(a); return np.array([[c,-s,0],[s,c,0],[0,0,1]])

# ======================= geometry helpers =======================
def box(x0,x1,y0,y1,z0,z1,col,xf=None,emit=False):
    Q=_engine_box(min(x0,x1),max(x0,x1),min(y0,y1),max(y0,y1),min(z0,z1),max(z0,z1),col,xf=xf,emit=emit)
    for q in Q: q['wind']=-1
    return Q
def seg(p0,p1,w,col,depth=None,emit=False):
    p0=np.array(p0,float); p1=np.array(p1,float); d=p1-p0; L=np.linalg.norm(d)+1e-9; d/=L
    up=np.array([0,0,-1.0]) if abs(d[1])>0.9 else np.array([0,1.0,0]); a=np.cross(d,up); a/=np.linalg.norm(a)+1e-9; b=np.cross(a,d); dp=depth or w
    v=[p0-a*w/2-b*dp/2,p0+a*w/2-b*dp/2,p0+a*w/2+b*dp/2,p0-a*w/2+b*dp/2,p1-a*w/2-b*dp/2,p1+a*w/2-b*dp/2,p1+a*w/2+b*dp/2,p1-a*w/2+b*dp/2]
    F=[(0,1,2,3),(5,4,7,6),(4,0,3,7),(1,5,6,2),(3,2,6,7),(4,5,1,0)]
    Q=[quad([tuple(v[i]) for i in f],col,emit) for f in F]
    for q in Q: q['wind']=1
    return Q
def xform(Q,fn):
    for q in Q:
        q['p']=[fn(v) for v in q['p']]; a=np.subtract(q['p'][1],q['p'][0]); b=np.subtract(q['p'][2],q['p'][0]); n=np.cross(a,b)
        q['n']=n/(np.linalg.norm(n)+1e-9); q['c']=np.mean(q['p'],axis=0)
    return Q
def limb(a,b,bend_dir,L,w,col1,col2=None,w2=None):
    """two-segment limb a->joint->b; the joint bulges along bend_dir when the limb is shorter than L"""
    a=np.array(a,float); b=np.array(b,float); d=np.linalg.norm(b-a); m=(a+b)/2
    k=math.sqrt(max(0.0,(L/2)**2-(d/2)**2)); j=m+np.array(bend_dir,float)*k
    return seg(a,j,w,col1)+seg(j,b,w2 or w*0.9,col2 or col1),j

# ======================= palette =======================
STEEL=(178,186,200); STEEL_L=(214,220,232); STEEL_D=(112,120,138); CAPE=(40,86,200); CAPE_D=(28,60,150); PLUME=(60,120,230)
GOLD=(220,176,60); LEATH=(84,56,34); BLADE=(206,214,226)
DARK=(46,40,54); DARK2=(30,26,36); DARK3=(66,58,74); TRIM=(150,24,28); HORN=(196,186,160); HORN_D=(150,140,118)
EYE_R=(255,60,40); RUNE=(255,70,40); BSWORD=(70,66,78); BEDGE=(190,40,40)
STONE=(74,68,72); STONE_D=(56,51,56); STONE_L=(92,85,88); FLOOR1=(66,60,64); FLOOR2=(56,51,55); IRON=(52,50,54); IRON_L=(78,76,82)
RUG=(110,18,24); GOLDT=(190,150,60)
WHT=(242,238,226); YEL=(255,210,60); RED=(240,50,40); GRN=(80,220,90); GRY=(150,150,160); BLU=(110,170,255)

# ======================= THE KNIGHT (small, silver, blue cape) =======================
def knight(base,yaw,walk=0.0,run=0.0,sword='hip',rh=None,lh=None,lean=0.0,head=0.0,sit=0.0,eyes=0.0,swing=0.0,boots=None):
    """local forward = +z. rh/lh: hand targets in local coords (None = idle). eyes>0: visor glows red (new boss)."""
    b=np.array(base,float); Rb=Ry(yaw)
    def Wd(p): return tuple(b+Rb@np.array(p,float))
    hip=0.82-0.42*sit
    def T(p):                                   # torso space: lean pivots at the hip
        p=np.array(p,float); piv=np.array([0,hip,0]); return Wd(piv+Rx(lean+0.22*run)@(p-piv+np.array([0,hip-0.82,0])))
    Q=[]; amp=0.5+0.35*run; sw=amp*math.sin(walk)
    for sx,ph in ((-1,1),(1,-1)):
        hp=np.array([sx*0.1,hip,0])
        if sit>0:
            ft=np.array([sx*0.16,0.06,0.62*sit+0.02]); bend=(0,1,0.3)
        else:
            a=ph*sw; ft=hp+np.array([0,-0.78*math.cos(a),0.78*math.sin(a)]); ft[1]=max(0.06,ft[1]+0.08*max(0,math.sin(walk*ph+PI/2))*(1 if walk else 0)); bend=(0,0,1)
        lq,_=limb(hp,ft,bend,0.84,0.15,STEEL_D,STEEL,0.13); Q+=xform(lq,Wd)
        if boots=='off': Q+=box(ft[0]-0.055,ft[0]+0.055,0.0 if sit==0 else ft[1]-0.05,ft[1]+0.03,ft[2]-0.05,ft[2]+0.12,(214,206,188),xf=Wd)   # socks
        else: Q+=box(ft[0]-0.07,ft[0]+0.07,0.0 if sit==0 else ft[1]-0.06,ft[1]+0.05,ft[2]-0.06,ft[2]+0.15,boots or STEEL_D,xf=Wd)
    Q+=box(-0.17,0.17,0.8,1.32,-0.11,0.11,STEEL,xf=T)                              # cuirass
    Q+=box(-0.12,0.12,0.92,1.24,0.11,0.13,STEEL_L,xf=T)                            # chest plate highlight
    Q+=box(-0.18,0.18,0.78,0.88,-0.12,0.12,LEATH,xf=T)                             # belt
    Q+=box(-0.04,0.04,0.79,0.87,0.12,0.135,GOLD,xf=T)                              # buckle
    for sx in (-1,1): Q+=box(sx*0.15,sx*0.27,1.2,1.36,-0.13,0.13,STEEL_L,xf=T)     # pauldrons
    # cape: hangs from the shoulders, flares when running
    fl=0.12+0.35*run+0.1*abs(math.sin(walk))*(1 if walk else 0); cy=0.38+0.25*run+0.5*sit
    Q+=xform([quad([(-0.2,1.33,-0.12),(0.2,1.33,-0.12),(0.27,cy,-0.16-fl-0.3*sit),(-0.27,cy,-0.16-fl-0.3*sit)],CAPE),
              quad([(0.2,1.33,-0.125),(-0.2,1.33,-0.125),(-0.27,cy,-0.165-fl-0.3*sit),(0.27,cy,-0.165-fl-0.3*sit)],CAPE_D)],T)
    # head / helmet
    hy=1.36; Rh=Ry(head)
    def Hh(p): p=np.array(p,float); return T(np.array([0,hy,0])+Rh@(p-np.array([0,hy,0])))
    Q+=box(-0.13,0.13,1.36,1.64,-0.14,0.14,STEEL,xf=Hh)
    Q+=box(-0.135,0.135,1.47,1.52,0.13,0.145,(16,16,22) if eyes<0.5 else (20,10,10),xf=Hh)          # visor slit
    if eyes>0:
        g=tuple(int(lerp(40,c,eyes)) for c in EYE_R)
        for sx in (-1,1): Q+=box(sx*0.015,sx*0.115,1.46,1.53,0.14,0.156,g,xf=Hh,emit=True)
    Q+=box(-0.02,0.02,1.64,1.8,-0.12,0.04,PLUME,xf=Hh)+box(-0.02,0.02,1.58,1.72,-0.2,-0.12,PLUME,xf=Hh)  # plume
    # arms
    sh={-1:np.array([-0.22,1.27,0]),1:np.array([0.22,1.27,0])}
    idle={-1:np.array([-0.27,0.86,0.04]),1:np.array([0.27,0.86,0.04])}
    if run: idle={-1:np.array([-0.24,0.95,-0.15*math.sin(walk)]),1:np.array([0.24,0.95,0.15*math.sin(walk)])}
    hand={-1:np.array(lh,float) if lh is not None else idle[-1],1:np.array(rh,float) if rh is not None else idle[1]}
    for sx in (-1,1):
        aq,_=limb(sh[sx],hand[sx],(sx*0.5,-0.4,-0.6),0.62,0.11,STEEL,STEEL_D,0.1); Q+=xform(aq,T)
        hp=hand[sx]; Q+=box(hp[0]-0.05,hp[0]+0.05,hp[1]-0.05,hp[1]+0.05,hp[2]-0.05,hp[2]+0.05,STEEL_D,xf=T)
    # short sword
    Q+=xform(seg((-0.21,0.86,0.06),(-0.24,0.28+0.46*sit,-0.16-0.45*sit),0.05,LEATH),T)  # scabbard (always there; lies back when sitting)
    if sword=='hip':
        Q+=box(-0.25,-0.17,0.86,0.9,0.0,0.12,GOLD,xf=T)                                  # hilt of the sheathed sword
    elif sword=='hand':
        hp=hand[1]; dr=np.array([0,math.cos(swing),math.sin(swing)])            # swing 0 = straight up, pi/2 = forward
        tip=hp+dr*0.78; Q+=xform(seg(hp+dr*0.06,tip,0.055,BLADE,0.02),T)
        cr=np.cross(dr,np.array([0,0,1.0]) if abs(dr[2])<0.9 else np.array([0,1.0,0])); cr/=np.linalg.norm(cr)+1e-9
        Q+=xform(seg(hp+dr*0.06-cr*0.11,hp+dr*0.06+cr*0.11,0.04,GOLD),T)+xform(seg(hp-dr*0.1,hp+dr*0.05,0.035,LEATH),T)
    return Q
def sword_on_floor(t,t_drop,start,end):
    """the knight's sword after he drops it: falls from his hand (start) and lands flat at end (world coords)"""
    if t<t_drop: return []
    u=sm(seg01(t,t_drop,t_drop+0.3)); hp=np.array(lerp3(start,end,u))+np.array([0,0.25*math.sin(PI*u),0])
    d0=np.array([0.0,-0.4,-1.0]); d1=np.array([1.0,0.0,0.35]); dr=d0+(d1-d0)*u; dr/=np.linalg.norm(dr)
    tip=hp+dr*0.78; tip[1]=max(tip[1],0.03)
    cr=np.cross(dr,np.array([0,1.0,0])); cr/=np.linalg.norm(cr)+1e-9
    return seg(hp+dr*0.06,tip,0.055,BLADE,0.02)+seg(hp+dr*0.06-cr*0.11,hp+dr*0.06+cr*0.11,0.04,GOLD)+seg(hp-dr*0.1,hp+dr*0.05,0.035,LEATH)

# ======================= THE BOSS (giant, dark armour, horns, huge sword) =======================
def boss(base,yaw,walk=0.0,rh=None,lh=None,lean=0.0,head=0.0,sword='hand',tip=None,eyes=1.0,core=1.0):
    """local forward = +z, ~3.7 m tall. sword: 'back' | 'hand' (blade from right hand to local point tip)."""
    b=np.array(base,float); Rb=Ry(yaw)
    def Wd(p): return tuple(b+Rb@np.array(p,float))
    hip=1.55
    def T(p): p=np.array(p,float); piv=np.array([0,hip,0]); return Wd(piv+Rx(lean)@(p-piv))
    Q=[]; sw=0.32*math.sin(walk)
    for sx,ph in ((-1,1),(1,-1)):
        hp=np.array([sx*0.3,hip,0]); a=ph*sw; ft=hp+np.array([0,-1.5*math.cos(a),1.5*math.sin(a)])
        ft[1]=max(0.1,ft[1]+0.16*max(0,math.sin(walk*ph+PI/2))*(1 if walk else 0))
        lq,kn=limb(hp,ft,(0,0,1),1.6,0.36,DARK,DARK3,0.3); Q+=xform(lq,Wd)
        Q+=box(kn[0]-0.2,kn[0]+0.2,kn[1]-0.14,kn[1]+0.16,kn[2]-0.05,kn[2]+0.24,DARK3,xf=Wd)          # knee guard
        Q+=box(ft[0]-0.2,ft[0]+0.2,ft[1]-0.1,ft[1]+0.16,ft[2]-0.16,ft[2]+0.36,DARK2,xf=Wd)            # sabaton
    Q+=box(-0.5,0.5,1.4,1.75,-0.3,0.3,DARK2,xf=T)                                  # fauld
    Q+=box(-0.52,0.52,1.4,1.5,-0.32,0.32,TRIM,xf=T)
    Q+=box(-0.62,0.62,1.72,2.85,-0.38,0.38,DARK,xf=T)                              # torso
    Q+=box(-0.42,0.42,1.95,2.7,0.38,0.42,DARK3,xf=T)                               # breastplate
    g=tuple(int(c*core+40*(1-core)) for c in RUNE)
    Q+=box(-0.12,0.12,2.2,2.46,0.42,0.45,g,xf=T,emit=True)                          # glowing core rune
    for sx in (-1,1):                                                              # spiked pauldrons
        Q+=box(sx*0.55,sx*1.05,2.6,3.0,-0.45,0.45,DARK3,xf=T)+box(sx*0.55,sx*1.07,2.56,2.64,-0.47,0.47,TRIM,xf=T)
        Q+=xform(seg((sx*0.85,2.98,0),(sx*1.0,3.38,-0.05),0.12,HORN_D),T)
    # head + horned helmet
    hy=2.9; Rh=Ry(head)
    def Hh(p): p=np.array(p,float); return T(np.array([0,hy,0])+Rh@(p-np.array([0,hy,0])))
    Q+=box(-0.3,0.3,2.86,3.5,-0.32,0.32,DARK2,xf=Hh)
    Q+=box(-0.32,0.32,3.06,3.14,0.3,0.34,(8,6,10),xf=Hh)                            # visor slit
    if eyes>0:
        ge=tuple(int(lerp(30,c,eyes)) for c in EYE_R)
        for sx in (-1,1): Q+=box(sx*0.07,sx*0.2,3.07,3.13,0.335,0.35,ge,xf=Hh,emit=True)
    Q+=box(-0.04,0.04,3.5,3.62,-0.3,0.3,TRIM,xf=Hh)                                  # crest
    for sx in (-1,1):                                                              # horns: out, then up, then in
        p0=(sx*0.3,3.32,0); p1=(sx*0.72,3.42,0.02); p2=(sx*0.9,3.86,0.0); p3=(sx*0.78,4.18,-0.06)
        Q+=xform(seg(p0,p1,0.17,HORN)+seg(p1,p2,0.13,HORN)+seg(p2,p3,0.08,HORN_D),Hh)
    # arms
    sh={-1:np.array([-0.82,2.62,0]),1:np.array([0.82,2.62,0])}
    idle={-1:np.array([-0.92,1.55,0.15]),1:np.array([0.92,1.55,0.2])}
    hand={-1:np.array(lh,float) if lh is not None else idle[-1],1:np.array(rh,float) if rh is not None else idle[1]}
    for sx in (-1,1):
        aq,j=limb(sh[sx],hand[sx],(sx*0.6,-0.3,-0.7),1.5,0.3,DARK,DARK3,0.27); Q+=xform(aq,T)
        Q+=box(j[0]-0.17,j[0]+0.17,j[1]-0.17,j[1]+0.17,j[2]-0.17,j[2]+0.17,DARK3,xf=T)               # elbow
        hp=hand[sx]; Q+=box(hp[0]-0.15,hp[0]+0.15,hp[1]-0.15,hp[1]+0.15,hp[2]-0.15,hp[2]+0.15,DARK2,xf=T)
    # enormous sword
    if sword=='back':
        a_=np.array([-0.7,1.0,-0.48]); c_=np.array([0.75,3.75,-0.48])
        Q+=xform(seg(a_,c_,0.3,BSWORD,0.06)+seg(c_-np.array([0.26,-0.14,0]),c_+np.array([0.26,-0.14,0])+np.array([0,0,0]),0.1,TRIM)+seg(c_,c_+np.array([0.2,0.38,0]),0.09,LEATH),T)
    else:
        hp=hand[1]; tp=np.array(tip if tip is not None else (1.0,0.12,1.6),float); dr=tp-hp; L=np.linalg.norm(dr); dr/=L+1e-9
        if hp[1]+dr[1]*3.0<0.1:                                                     # tip rests on / drags along the floor
            dy=-(hp[1]-0.1)/3.0; hz=np.array([dr[0],0.0,dr[2]]); hz/=np.linalg.norm(hz)+1e-9; dr=hz*math.sqrt(max(0.0,1-dy*dy))+np.array([0,dy,0])
        start=hp+dr*0.18; Q+=xform(seg(start,hp+dr*3.0,0.3,BSWORD,0.06),T)
        Q+=xform(seg(start+dr*0.05,hp+dr*2.9,0.07,BEDGE,0.075,emit=True),T)                          # glowing fuller
        cr=np.cross(dr,np.array([1.0,0,0]) if abs(dr[0])<0.9 else np.array([0,1.0,0])); cr/=np.linalg.norm(cr)+1e-9
        Q+=xform(seg(start-cr*0.42,start+cr*0.42,0.12,TRIM)+seg(hp-dr*0.5,hp+dr*0.1,0.09,LEATH),T)
    return Q

# ======================= THE ARENA (one set, reused by every shot) =======================
GATE_W=2.2; GATE_H=5.0; BARRIER_Z=0.55
def arena_static():
    Q=[]
    Q+=tiled_plane(-8,8,0,18,0.0,1.6,lambda i,j:FLOOR1 if (i+j)%2 else FLOOR2)
    Q+=[quad([(-1.1,0.01,1.0),(1.1,0.01,1.0),(1.1,0.01,15.0),(-1.1,0.01,15.0)],RUG)]                 # red carpet to the throne
    def wc(i,j,v): return STONE if (i+j)%2 else STONE_D
    Q+=wall_region('z',0.0,-8,-GATE_W,0,10,1.6,1.25,wc)+wall_region('z',0.0,GATE_W,8,0,10,1.6,1.25,wc)+wall_region('z',0.0,-GATE_W,GATE_W,GATE_H,10,1.1,1.25,wc)
    Q+=wall_region('z',18.0,-8,8,0,10,1.6,1.25,wc,facing=-1)
    Q+=wall_region('x',-8.0,0,18,0,10,1.6,1.25,wc,facing=-1)+wall_region('x',8.0,0,18,0,10,1.6,1.25,wc)
    # door frame (inside)
    Q+=box(-GATE_W-0.45,-GATE_W,0,GATE_H+0.5,0.0,0.3,STONE_L)+box(GATE_W,GATE_W+0.45,0,GATE_H+0.5,0.0,0.3,STONE_L)+box(-GATE_W-0.45,GATE_W+0.45,GATE_H,GATE_H+0.6,0.0,0.3,STONE_L)
    # pillars
    for x in (-5.6,5.6):
        for z in (4.0,9.0,14.0): Q+=box(x-0.5,x+0.5,0,10,z-0.5,z+0.5,STONE_L)+box(x-0.62,x+0.62,0,0.5,z-0.62,z+0.62,STONE_D)
    # throne on a dais
    Q+=box(-2.4,2.4,0,0.4,14.6,17.6,STONE_L)+box(-1.6,1.6,0.4,0.8,15.2,17.6,STONE)
    Q+=box(-1.0,1.0,0.8,1.6,16.0,17.2,DARK3)+box(-1.0,1.0,1.6,4.6,16.9,17.3,DARK2)+box(-1.2,-0.9,0.8,2.4,16.0,17.3,DARK3)+box(0.9,1.2,0.8,2.4,16.0,17.3,DARK3)
    Q+=box(-0.6,0.6,4.0,4.4,16.95,17.25,TRIM)
    # outside corridor (z<0)
    def cc(i,j,v): return (48,46,52) if (i+j)%2 else (40,38,44)
    Q+=tiled_plane(-GATE_W,GATE_W,-15,0,0.0,1.1,lambda i,j:(46,44,48) if (i+j)%2 else (38,36,40))
    Q+=wall_region('x',-GATE_W,-15,0,0,GATE_H,1.5,1.25,cc)+wall_region('x',GATE_W,-15,0,0,GATE_H,1.5,1.25,cc,facing=-1)
    Q+=[quad([(-GATE_W,GATE_H,-15),(GATE_W,GATE_H,-15),(GATE_W,GATE_H,0),(-GATE_W,GATE_H,0)],(30,28,34))]
    Q+=wall_region('z',-15.0,-GATE_W,-1.2,0,GATE_H,1.0,1.25,cc)+wall_region('z',-15.0,1.2,GATE_W,0,GATE_H,1.0,1.25,cc)+wall_region('z',-15.0,-1.2,1.2,3.2,GATE_H,1.2,0.9,cc)
    Q+=[quad([(-1.2,0,-15.05),(1.2,0,-15.05),(1.2,3.2,-15.05),(-1.2,3.2,-15.05)],(255,244,214),emit=True)]   # daylight at the end
    return Q
ARENA=arena_static()
TORCHES=[(-5.6,3.4,3.4),(5.6,3.4,3.4),(-5.6,3.4,8.4),(5.6,3.4,8.4),(-5.6,3.4,13.4),(5.6,3.4,13.4),(-3.0,3.2,0.35),(3.0,3.2,0.35)]
CTORCH=[(-2.05,2.8,-4.0),(2.05,2.8,-8.0)]
def torches(t):
    Q=[]
    for k,(x,y,z) in enumerate(TORCHES+CTORCH):
        fl=0.1*math.sin(t*13+k*2.1)+0.06*math.sin(t*29+k)
        dz=-0.15 if z>0.2 and k<6 else (0.15 if k>=6 and z>0 else 0.0)
        Q+=box(x-0.06,x+0.06,y-0.5,y,z-0.06,z+0.06,IRON_L)
        Q+=box(x-0.13,x+0.13,y+0.02,y+0.26+fl,z-0.13,z+0.13,(255,70,30),emit=True)+box(x-0.07,x+0.07,y+0.15,y+0.38+fl,z-0.07,z+0.07,(255,180,60),emit=True)
    return Q
def torch_lights(t,dim=1.0):
    L=[]
    for k,(x,y,z) in enumerate(TORCHES):
        L.append(((x*0.85,y+0.4,z+0.4),(255,80,40),(1.15+0.15*math.sin(t*11+k))*dim))
    for k,(x,y,z) in enumerate(CTORCH): L.append(((x*0.7,y+0.3,z),(255,130,60),0.8*dim))
    L.append(((0,2.5,-14.0),(255,240,210),1.4))                                                 # daylight spill
    return L
def gate_doors(ang):
    """two iron doors hinged at x=+-GATE_W, swinging outward (into the corridor). ang 0 = shut."""
    Q=[]
    for sx in (-1,1):
        hx=sx*GATE_W; a=-sx*ang
        def Wd(p,hx=hx,a=a): return tuple(np.array([hx,0,0])+Ry(a)@(np.array(p,float)-np.array([hx,0,0])))
        x0,x1=(hx,hx-sx*GATE_W) if sx>0 else (hx,hx+GATE_W)
        x0,x1=min(x0,x1),max(x0,x1)
        Q+=box(x0,x1,0,GATE_H,-0.16,-0.02,IRON,xf=Wd)
        for k in range(5):                                                                   # vertical bars
            xx=x0+0.22+k*(x1-x0-0.44)/4; Q+=box(xx-0.06,xx+0.06,0.1,GATE_H-0.1,-0.02,0.05,IRON_L,xf=Wd)
        for yy in (0.8,2.5,4.2): Q+=box(x0+0.05,x1-0.05,yy-0.09,yy+0.09,-0.02,0.06,IRON_L,xf=Wd)
        Q+=box(x0+0.1,x1-0.1,0.8,4.2,-0.2,-0.16,IRON,xf=Wd)                                  # outer face plate
    return Q
def letters_quad_alpha(t): return sm(seg01(t,21.0,21.9))*(0.85+0.15*math.sin(t*6))

# ======================= barrier (transparent: composited after the scene with the z-buffer) =======================
BAR_NX,BAR_NY=10,12
def barrier_quads(flash,ripple_c=None,ripple_r=0.0,base=0.12,tint=(255,40,30)):
    """grid of emissive tiles over the doorway at z=BARRIER_Z; colour = additive glow strength"""
    Q=[]; x0,x1,y0,y1=-GATE_W,GATE_W,0.0,GATE_H
    for i in range(BAR_NX):
        for j in range(BAR_NY):
            a=x0+(x1-x0)*i/BAR_NX; b_=x0+(x1-x0)*(i+1)/BAR_NX; c=y0+(y1-y0)*j/BAR_NY; d=y0+(y1-y0)*(j+1)/BAR_NY
            cx,cy=(a+b_)/2,(c+d)/2; g=base*(0.6+0.4*((i+j)%2))
            if ripple_c is not None:
                r=math.hypot(cx-ripple_c[0],cy-ripple_c[1]); g+=flash*max(0.0,1-abs(r-ripple_r)/0.7)*1.2+flash*0.5*max(0,1-r/2.2)
            else: g+=flash*0.5
            col=tuple(min(255,int(c_*g)) for c_ in tint)
            Q.append(quad([(a,c,BARRIER_Z),(b_,c,BARRIER_Z),(b_,d,BARRIER_Z),(a,d,BARRIER_Z)],col,emit=True))
    return Q

# ======================= STORY TIMELINE =======================
SCR=json.load(open(os.path.join(TTS_DIR,'fb','script.json')))
NARR=[('N1',0.10),('N2',4.15),('N3',6.40),('B1',7.65),('N4',10.45),('N5',12.15),('N6',16.55),('N7',21.15),('N8',22.85),('N9',26.70),('N10',28.62)]
HOOK_IMPACTS=[0.12,0.95,1.8,2.65,3.45]                     # shared with Experiment B
KNIGHT_IMPACTS=[18.9,20.75,21.7,28.95,29.75]
def impact(t,lst,dur=0.45):
    best=0.0;src=None
    for ti in lst:
        if ti<=t<ti+dur: v=1-(t-ti)/dur
        else: continue
        if v>best: best=v; src=ti
    return best,src
def gate_angle(t):
    if t<4.0: return 0.0
    if t<10.65: return 1.75*sm(seg01(t,4.0,5.4))
    if t<14.8: return 1.75*(1-seg01(t,10.65,10.95)**2)
    return 1.75*sm(seg01(t,14.8,15.9))

BOSS_IDLE_RH=(0.92,1.55,0.2); BOSS_GRIP=(0.75,3.65,-0.45); BOSS_OVER=(0.95,3.85,0.1)
BOSS_BACKTIP=(-0.75,0.95,-0.48); BOSS_UPTIP=(1.0,7.0,-0.3); BOSS_READY_RH=(0.95,2.3,0.9); BOSS_READY_TIP=(0.9,3.4,2.6)
def boss_draw(t,t0):
    """(sword, rh, tip): reach to the hilt on the back, pull it up over the shoulder, bring it forward to ready"""
    if t<t0+0.3: return 'back',lerp3(BOSS_IDLE_RH,BOSS_GRIP,sm(seg01(t,t0,t0+0.3))),None
    u2=sm(seg01(t,t0+0.3,t0+0.6)); u3=sm(seg01(t,t0+0.6,t0+0.95))
    if u3<=0: return 'hand',lerp3(BOSS_GRIP,BOSS_OVER,u2),lerp3(BOSS_BACKTIP,BOSS_UPTIP,u2)
    return 'hand',lerp3(BOSS_OVER,BOSS_READY_RH,u3),lerp3(BOSS_UPTIP,BOSS_READY_TIP,u3)
def shove_phase(t,impacts,lunge=0.12,dur=0.85):
    """0 = hands on the wall, 1 = wound up. The lunge into each impact takes `lunge` s (no 1-frame jumps)."""
    iv,_=impact(t,impacts,dur); ph=1-iv
    nxt=[ti for ti in impacts if ti>t]
    if nxt: ph=min(ph,(nxt[0]-t)/lunge)
    return max(0.0,min(1.0,ph))
def reach_local(D,lean,y,hip):
    """local hand z so that, after the torso lean about the hip, the hand's front is D metres ahead of the body base"""
    return (D-math.sin(lean)*(y-hip))/math.cos(lean)
def boss_state(t):
    """returns dict for boss(), or None when off-set (outside)."""
    if t<4.0:                                               # HOOK: shoving the invisible wall
        ph=shove_phase(t,HOOK_IMPACTS)                       # 0 at contact, 1 at wind-up
        z=1.55+0.35*ph; lean=0.22-0.12*ph; yr=2.8-0.25*ph; yl=2.9-0.2*ph
        D=z-BARRIER_Z-0.17                                   # palms (0.15 half-size) stop just short of the wall
        return dict(base=(0,0,z),yaw=PI,rh=(1.15,yr,reach_local(D,lean,yr,1.55)),lh=(-1.15,yl,reach_local(D,lean,yl,1.55)-0.05*ph),lean=lean,sword='back',head=0.08*math.sin(t*3))
    if t<12.6:                                              # arrival: gives up at the door, walks away, turns, draws the sword
        if t<5.6:
            tu=sm(seg01(t,4.15,4.75)); w=seg01(t,4.0,5.6); x=lerp(0.0,-1.0,sm(w)); z=lerp(1.9,5.2,sm(w))
            return dict(base=(x,0,z),yaw=lerp(PI,2*PI,tu),walk=t*5.2 if 0.0<w<1.0 else 0.0,sword='back',rh=BOSS_IDLE_RH)
        yaw=lerp(0.0,PI,sm(seg01(t,5.6,6.8)))
        sw,rh,tip=boss_draw(t,7.0)
        if t>=12.15:                                       # lowers the weapon
            l=sm(seg01(t,12.3,12.9)); rh=lerp3(rh,(0.92,1.6,0.25),l); tip=lerp3(tip,(1.1,0.05,1.9),l)
        return dict(base=(-1.0,0,5.2),yaw=yaw,sword=sw,rh=rh,tip=tip,head=0.0)
    # walks out, keeping clear of the knight: (-1,5.2) -> (-1.3,3.4) -> (-1.3,1.9) -> door -> corridor -> daylight
    P=[(12.6,(-1.0,5.2)),(13.9,(-1.3,3.4)),(14.9,(-1.3,1.9)),(15.9,(0.0,0.2)),(16.4,(0.0,-0.8)),(23.6,(0.0,-14.0))]
    for (t0,p0),(t1,p1) in zip(P,P[1:]):
        if t<t1 or (t1==P[-1][0]):
            u=seg01(t,t0,t1); x=lerp(p0[0],p1[0],u); z=lerp(p0[1],p1[1],u); break
    yaw=PI+(0.35 if 14.4<t<15.6 else 0.0)*math.sin(PI*seg01(t,14.4,15.6))
    return dict(base=(x,0,z),yaw=yaw,walk=t*5.2,rh=(0.92,1.6,0.25),tip=(1.1,0.05,1.9),head=0.0)

def knight_state(t):
    if t<9.0:                                               # outside, opening the gate
        if t<5.0: p=lerp(0.45,0.0,0)                        # hands on the doors while they swing
        z=lerp(-0.75,-1.05,sm(seg01(t,4.0,5.2))); push=1-sm(seg01(t,5.0,5.6))
        return dict(base=(0.0,0,z),yaw=0.0,rh=(0.35,1.15,lerp(0.3,0.6,push)) if push>0.05 else None,lh=(-0.35,1.15,lerp(0.3,0.6,push)) if push>0.05 else None,head=0.0)
    if t<10.0:                                              # walks in through the barrier
        u=seg01(t,9.0,10.0); return dict(base=(lerp(0.0,0.3,u),0,lerp(-1.05,2.6,u)),yaw=0.0,walk=t*9.0,head=0.0)
    if t<17.6:
        dr=sm(seg01(t,10.0,10.4))                          # draws the sword
        rh=lerp3((0.27,0.86,0.04),(0.3,1.15,0.38),dr); sword='hand' if dr>0.35 else 'hip'
        look=0.0
        if 11.0<t<11.9: look=-1.1*math.sin(PI*seg01(t,11.0,11.9))          # glances back at the slammed gate
        if t>=13.3: look=sm(seg01(t,13.3,15.6))*(-0.9)                       # watches the boss pass
        yaw=0.0 if t<15.0 else lerp(0.0,PI,sm(seg01(t,15.0,16.6)))           # turns to the door
        return dict(base=(0.3,0,2.6),yaw=yaw,rh=rh,sword=sword,swing=lerp(0.0,0.5,dr),head=look if t<15.0 else look*(1-seg01(t,15.0,16.0)),lean=0.0)
    if t<18.9:                                              # runs after him
        u=seg01(t,17.6,18.9); z=lerp(2.6,KNIGHT_STOP,u**0.9); x=lerp(0.3,0.0,u)
        return dict(base=(x,0,z),yaw=PI,walk=t*15,run=1.0,sword='hand',rh=(0.3,1.1,0.2),swing=0.25)
    if t<20.4:                                              # crash, knocked back, sits
        k=sm(seg01(t,18.9,19.25)); z=lerp(KNIGHT_STOP,1.75,k); sit=sm(seg01(t,19.05,19.45))*(1-sm(seg01(t,19.9,20.4)))
        return dict(base=(0.0,0,z),yaw=PI,lean=-0.35*k*(1-sit),sit=sit,sword='hand' if t<SWORD_DROP else 'none',rh=(0.3,1.1,0.2) if t<SWORD_DROP else (0.35,0.9,0.3),swing=0.25)
    # pushes the barrier (mirror of the hook) ... then becomes the boss
    return knight_push(t,lerp(1.75,BARRIER_Z+0.42,sm(seg01(t,20.2,20.65))),KNIGHT_IMPACTS,
                       eyes=sm(seg01(t,25.4,26.2)) if t<26.6 else 1.0,turn=sm(seg01(t,25.0,25.9)) if t<26.6 else 0.0)
KNIGHT_STOP=BARRIER_Z+0.62                                 # where the running knight meets the wall
SWORD_DROP=18.95; SWORD_FROM=(-0.3,1.0,0.85); SWORD_TO=(0.55,0.03,1.55)
def knight_push(t,z,impacts,eyes=0.0,turn=0.0):
    """palms against the barrier (mirror of the boss in the hook); turn>0.5 = has turned to face the arena"""
    ph=shove_phase(t,impacts,0.1,0.8); zb=z+0.12*ph; lean=0.15-0.1*ph
    hands=turn<0.02; zb+=0.15*turn                              # lets go of the wall before turning round
    yr,yl=1.35-0.1*ph,1.4-0.1*ph; D=zb-BARRIER_Z-0.07
    return dict(base=(0.0,0,zb),yaw=PI+turn*PI,rh=(0.25,yr,max(0.2,reach_local(D,lean,yr,0.82))) if hands else None,
                lh=(-0.25,yl,max(0.2,reach_local(D,lean,yl,0.82))) if hands else None,lean=lean if hands else 0.0,eyes=eyes,sword='none',head=0.0)

# ======================= SHOTS =======================
def hook_shot(t):
    """0-4 s, shared with Experiment B: low 3/4 view of the boss shoving the barrier, slow push-in"""
    u=sm(seg01(t,0,4.0)); iv,_=impact(t,HOOK_IMPACTS,0.3)
    sh=(math.sin(t*90)*2.0*iv,math.cos(t*70)*1.5*iv)
    return dict(cam=lerp3((3.1,0.9,5.4),(2.5,1.0,4.6),u),tgt=(0.0,2.6,0.6),fov=72,shake=sh)
def shot(V):
    if V<4.0: return hook_shot(V)
    if V<6.3:  u=sm(seg01(V,4.0,6.3)); return dict(cam=lerp3((-0.95,1.6,-3.9),(-0.9,1.65,-3.4),u),tgt=(-1.1,2.3,8.0),fov=64)
    if V<9.0:  u=sm(seg01(V,6.3,9.0)); return dict(cam=lerp3((1.4,2.1,1.6),(1.2,2.3,2.1),u),tgt=(-1.0,3.0,5.2),fov=62)
    if V<12.15:
        sh=(0,0)
        if 10.95<=V<11.5: k=1-seg01(V,10.95,11.5); sh=(math.sin(V*80)*4*k,math.cos(V*65)*3*k)
        u=sm(seg01(V,9.0,12.15)); return dict(cam=lerp3((2.0,1.1,5.6),(1.7,1.2,5.0),u),tgt=(0.1,1.5,1.0),fov=66,shake=sh)
    if V<15.8: u=sm(seg01(V,12.15,15.8)); return dict(cam=lerp3((6.2,2.6,6.4),(5.6,2.4,5.2),u),tgt=lerp3((-1.0,2.0,4.6),(-0.5,1.8,2.0),u),fov=66)
    if V<17.5: u=sm(seg01(V,15.8,17.5)); return dict(cam=lerp3((1.6,1.0,5.2),(1.3,1.0,4.8),u),tgt=(-0.1,2.0,-1.0),fov=66)
    if V<20.0:
        sh=(0,0)
        if 18.9<=V<19.5: k=1-seg01(V,18.9,19.5); sh=(math.sin(V*90)*5*k,math.cos(V*70)*4*k)
        return dict(cam=(2.9,1.3,3.6),tgt=(0.0,1.0,0.9),fov=64,shake=sh)
    if V<21.0: return dict(cam=(0.9,1.6,5.2),tgt=(0.0,1.5,-6.0),fov=62)
    if V<26.6:
        u=sm(seg01(V,21.0,26.6)); return dict(cam=lerp3((0.0,1.0,8.0),(0.0,1.4,5.2),u),tgt=lerp3((0.0,4.6,0.0),(0.0,2.6,0.0),sm(seg01(V,23.0,26.0))),fov=64)
    if V<28.55: return dict(outside=True)
    u=sm(seg01(V,28.55,30.5)); return dict(cam=lerp3((0.25,1.45,-2.3),(0.3,1.5,-3.4),u),tgt=(0.0,1.3,1.5),fov=62)

# ======================= RENDER =======================
R=Renderer(W,H,fog=(14,8,12))
def prelit(Q,cam_p,warm=0.22):
    """bake simple cool lighting into the knight's faces and make them emissive: silver stays silver under red torches"""
    c=np.mean([q['c'] for q in Q],axis=0); Ld=np.array(cam_p,float)-c+np.array([0,2.5,0]); Ld/=np.linalg.norm(Ld)+1e-9
    for q in Q:
        if q['emit']: continue
        k=0.42+0.58*abs(float(q['n']@Ld)); col=np.array(q['col'],float)*k
        col=col*(1-warm)+col*np.array([1.0,0.55,0.5])*warm; q['col']=tuple(int(min(255,v)) for v in col); q['emit']=True
    return Q
def render_inside(V,sh):
    cam=Camera.look(sh['cam'],sh['tgt']); cp=np.array(sh['cam'])
    ks=dict(knight_state(V)); bs=boss_state(V)
    chars=[]
    chars.append(prelit(knight(**ks),sh['cam']))
    if bs is not None: chars.append(boss(**bs))
    layers=[ARENA,gate_doors(gate_angle(V)),torches(V),sword_on_floor(V,SWORD_DROP,SWORD_FROM,SWORD_TO)]+chars
    L=torch_lights(V)
    fl,_=impact(V,HOOK_IMPACTS if V<4 else KNIGHT_IMPACTS,0.4)
    if fl>0: L=L+[((0,2.2,BARRIER_Z+0.6),(255,40,30),2.5*fl)]
    L=L+[((0,2.4,BARRIER_Z+0.4),(255,40,30),0.5)]                                                # barrier's steady glow
    img,vi,zb=zrender(R,cam,layers,L,fov=sh['fov'],fog_start=7,fog_end=26,ambient=0.2,shake=sh.get('shake',(0,0)),return_z=True)
    # --- barrier pass ---
    base=0.2 if V<4.0 else 0.1; flash=0.0; rc=None; rr=0.0; tint=(255,40,30)
    if V<4.0 or V>=18.0:
        fl,src=impact(V,HOOK_IMPACTS if V<4 else KNIGHT_IMPACTS,0.6)
        if src is not None:
            flash=fl*(1.6 if V<4 else 1.0); rr=(V-src)*5.0; rc=(0.0,2.8) if V<4 else (0.0,1.3)
    if 9.15<V<9.75: flash=0.5*math.sin(PI*seg01(V,9.15,9.75)); rc=(0.0,1.2); rr=(V-9.15)*5; tint=(120,170,255)       # lets the knight in
    if 16.0<V<16.8: flash=0.6*math.sin(PI*seg01(V,16.0,16.8)); rc=(0.0,2.2); rr=(V-16.0)*5; tint=(120,170,255)       # lets the boss out
    bimg,_,bz=zrender(R,cam,[barrier_quads(flash,rc,rr,base,tint)],[],fov=sh['fov'],fog_start=7,fog_end=26,shake=sh.get('shake',(0,0)),return_z=True)
    m=(bz>zb)&(bz>0)
    a=np.asarray(img).astype(np.float32); b=np.asarray(bimg).astype(np.float32)-np.array(R.fog,np.float32)*0.5
    a=np.where(m[...,None],np.clip(a+np.clip(b,0,255),0,255),a)
    img=Image.fromarray(a.astype(np.uint8))
    # --- glowing letters above the door (21 s+) ---
    al=letters_quad_alpha(V) if V>=21.0 else 0.0
    if al>0: img=letters(img,vi,al)
    return post.ps1(img),vi
LET=None
def letters(img,vi,al):
    global LET
    if LET is None:
        s='ONE MUST REMAIN'; w=font.width(s)+4; LET=Image.new('RGB',(w,11),(0,0,0)); font.text(ImageDraw.Draw(LET),s,2,2,(255,60,30),1,None)
    P=[R.project(c,vi) for c in [(3.7,7.2,0.05),(-3.7,7.2,0.05),(-3.7,6.05,0.05),(3.7,6.05,0.05)]]
    if not all(P): return img
    glow=Image.new('RGB',img.size,(0,0,0)); post.map_texture(glow,[(p[0],p[1]) for p in P],LET,Image.NEAREST)
    a=np.asarray(img).astype(np.float32); g=np.asarray(glow).astype(np.float32)
    return Image.fromarray(np.clip(a+g*al*1.3,0,255).astype(np.uint8))

R_OUT=Renderer(W,H,fog=(176,206,236))
def hill(x,z): return 0.6*math.sin(x*0.35+1.0)+0.5*math.sin(z*0.21)+0.02*(z-20)
def outside_static():
    Q=[]
    def gc(i,j): return (92,150,64) if (i+j)%2 else (80,136,56)
    xs=np.arange(-30,30.01,3.0); zs=np.arange(-6,60.01,3.0)
    for i in range(len(xs)-1):
        for j in range(len(zs)-1):
            a,b,c,d=xs[i],xs[i+1],zs[j],zs[j+1]
            Q.append(quad([(a,hill(a,c),c),(b,hill(b,c),c),(b,hill(b,d),d),(a,hill(a,d),d)],gc(i,j)))
    for j in range(len(zs)-1):                                                                 # dirt path
        c,d=zs[j],zs[j+1]; Q.append(quad([(-0.9,hill(-0.9,c)+0.03,c),(0.9,hill(0.9,c)+0.03,c),(0.9,hill(0.9,d)+0.03,d),(-0.9,hill(-0.9,d)+0.03,d)],(150,122,80)))
    for k,(x,z) in enumerate([(-6,8),(5,12),(-9,20),(8,26),(-4,32),(11,40),(-12,44),(4,50)]):  # pine trees
        y=hill(x,z); Q+=box(x-0.2,x+0.2,y,y+1.2,z-0.2,z+0.2,(90,62,40))
        for lv,(r,h) in enumerate(((1.4,1.2),(1.0,1.2),(0.6,1.1))):
            Q+=box(x-r,x+r,y+1.0+lv*0.9,y+1.0+lv*0.9+h,z-r,z+r,(40,98,52) if lv%2 else (48,112,60))
    # castle wall + open doorway behind the camera side (z<0)
    return Q
OUTSIDE=outside_static()
def render_outside(V):
    u=seg01(V,26.6,28.55); bz=lerp(1.0,7.5,u); y=hill(0,bz)
    camp=(0.9,1.4+hill(0,bz-5.0),bz-5.0+lerp(0,1.0,u)); cam=Camera.look(camp,(0.0,y+2.6,bz+6.0))
    bs=dict(base=(0.0,y,bz),yaw=0.0,walk=V*5.2,rh=(0.92,1.6,0.25),tip=(1.1,0.05,1.9),head=0.15*math.sin(V*1.3))
    img,vi,zb=zrender(R_OUT,cam,[OUTSIDE,boss(**bs)],[((20,40,-10),(255,250,230),3.0)],fov=64,fog_start=20,fog_end=70,ambient=0.65,return_z=True)
    a=np.asarray(img).astype(np.float32); yy=np.linspace(0,1,H)[:,None,None]
    sky=(np.array([92,150,226])*(1-yy)+np.array([196,222,244])*yy)*np.ones((1,W,1))
    sun=np.zeros((H,W,1)); X,Y=np.meshgrid(np.arange(W),np.arange(H)); d=np.hypot(X-140,Y-40); sun[...,0]=np.clip(1-d/14,0,1)
    sky=sky+sun*np.array([60,50,20])
    a=np.where((zb==0)[...,None],sky,a)
    return post.ps1(Image.fromarray(np.clip(a,0,255).astype(np.uint8))),vi

# ======================= HUD / SUBTITLES =======================
def otext(d,s,x,y,col,sc=1):
    o=max(1,sc//2)
    for ox,oy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)): font.text(d,s,x+ox*o,y+oy*o,(0,0,0),sc,None)
    font.text(d,s,x,y,col,sc,None)
def ctext(d,s,y,col,sc=1): otext(d,s,(W-font.width(s,sc))//2,y,col,sc)
HIL={'FINAL','BOSSES','ROOMS?','KNIGHT','ARENA.','WHISPERS,','FINALLY','SLAMS','WALKS','OUT.','INVISIBLE','WALL.','ONE','REMAIN.','HEALTH','BAR','BOSS.','FIGHT','REPLACED.'}
def subtitle(d,V):
    cur=None
    for k,t0 in NARR:
        if (t0<=V or k=='N1') and V<t0+SCR['dur'][k]+0.12: cur=k
    if cur is None: return
    txt=SCR['text'][cur].upper().replace('...','..')
    if cur=='B1': txt='"'+txt+'"' if '"' in font.FONT else "'"+txt+"'"
    if cur=='N1':                                         # hook: big title-size subtitle at the top
        lines=['WHY DO FINAL','BOSSES NEVER','LEAVE THEIR','ROOMS?']; y=30
        for ln in lines:
            xw=font.width(ln,2); x=(W-xw)//2; cx=x
            for wd in ln.split(' '): otext(d,wd,cx,y,YEL if wd in HIL else WHT,2); cx+=font.width(wd,2)+12
            y+=19
        return
    ws=txt.split(); lines=[]; c=''
    for w_ in ws:
        if len(c)+len(w_)+(1 if c else 0)>27: lines.append(c); c=w_
        else: c=(c+' '+w_).strip()
    lines.append(c); y=266-11*(len(lines)-1)
    col_spk=RED if cur=='B1' else None
    for ln in lines:
        xw=font.width(ln); x=(W-xw)//2; d.rectangle([x-3,y-2,x+xw+2,y+8],fill=(0,0,0)); cx=x
        for wd in ln.split(' '):
            col=col_spk or (YEL if wd.strip("'\"") in HIL else WHT)
            otext(d,wd,cx,y,col); cx+=font.width(wd)+6
        y+=11
def hp_knight(d,V):
    if not (9.0<=V<23.4) or 26.6<=V<28.55: return
    if 23.0<=V and int(V*16)%2: return                     # flickers out
    otext(d,'KNIGHT',8,10,BLU); d.rectangle([8,20,72,25],fill=(0,0,0),outline=(200,200,210)); d.rectangle([9,21,71,24],fill=GRN)
def hp_boss(d,V):
    if V<24.35 or 26.6<=V<28.55: return
    drop=sm(seg01(V,24.35,24.6)); fill=sm(seg01(V,24.6,25.5)); y=int(lerp(-30,22,drop))
    otext(d,'FINAL BOSS',(W-font.width('FINAL BOSS',2))//2,y,RED,2)
    x0,x1=10,W-10; d.rectangle([x0-1,y+18,x1+1,y+28],fill=(0,0,0),outline=(230,190,90)); d.rectangle([x0+1,y+20,x0+1+int((x1-x0-2)*fill),y+26],fill=RED)
    d.rectangle([x0+1,y+20,x0+1+int((x1-x0-2)*fill),y+21],fill=(255,140,120))
def frame(V):
    sh=shot(V)
    if sh.get('outside'): img,vi=render_outside(V)
    else: img,vi=render_inside(V,sh)
    d=ImageDraw.Draw(img)
    hp_knight(d,V); hp_boss(d,V); subtitle(d,V)
    return img

TEST=os.environ.get('TEST')
if TEST and __name__=='__main__':
    ims=[frame(float(x)) for x in TEST.split(',')]; shp=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): shp.paste(im,(i*182,0))
    shp.resize((shp.width*2,640),Image.NEAREST).save('test.png'); sys.exit()

# ======================= QA manifest (tools/qa/scene_qa.py, PIPELINE.md) =======================
QA=dict(fps=FPS,dur=DUR,W=W,frame=frame,knight_fn=knight,boss_fn=boss,barrier_z=BARRIER_Z,gate_w=GATE_W,gate_h=GATE_H,corridor_w=GATE_W,
    knight=lambda t: knight_state(t),
    boss=lambda t: boss_state(t),
    camera=lambda t: None if shot(t).get('outside') else shot(t)['cam'],
    scenes=[dict(id='hook',t0=0.0,t1=4.0,action='boss shoves the invisible wall, barrier flashes red',env='arena, gate shut'),
            dict(id='arrival',t0=4.0,t1=6.3,action='knight opens the gate; boss turns around',env='corridor -> arena'),
            dict(id='boss-line',t0=6.3,t1=9.0,action='boss readies sword: You finally came',env='arena'),
            dict(id='enter',t0=9.0,t1=12.15,action='knight walks in, draws sword; gate slams',env='arena, gate'),
            dict(id='walk-out',t0=12.15,t1=15.8,action='boss lowers sword and walks past the knight',env='arena'),
            dict(id='exit',t0=15.8,t1=17.5,action='boss passes through the barrier',env='arena, open gate'),
            dict(id='crash',t0=17.5,t1=20.0,action='knight runs after him and hits the wall',env='arena, open gate'),
            dict(id='push',t0=20.0,t1=21.0,action='knight pushes the barrier, boss leaves down the corridor',env='arena, open gate'),
            dict(id='reveal',t0=21.0,t1=26.6,action='ONE MUST REMAIN; health bars swap; knight turns, eyes glow',env='arena'),
            dict(id='daylight',t0=26.6,t1=28.55,action='old boss walks into daylight',env='outside',set='outside'),
            dict(id='trapped',t0=28.55,t1=DUR,action='knight trapped behind the barrier',env='corridor view into arena')],
    weapon_events=[('boss',7.3,'back','hand'),('knight',10.2,'hip','hand'),('knight',SWORD_DROP,'hand','none')],
    crossings=[('knight',9.0,10.0),('boss',15.0,16.6)],
    texts=lambda: [(k,ln,1) for k in SCR['text'] for ln in _wrap(SCR['text'][k].upper().replace('...','..'))]+[('N1',x,2) for x in ('WHY DO FINAL','BOSSES NEVER','LEAVE THEIR','ROOMS?')]
          +[('hud','FINAL BOSS',2),('hud','KNIGHT',1),('letters','ONE MUST REMAIN',1)])
def _wrap(txt,n=27):
    out=[]; c=''
    for w_ in txt.split():
        if len(c)+len(w_)+(1 if c else 0)>n: out.append(c); c=w_
        else: c=(c+' '+w_).strip()
    return out+[c]

# ======================= AUDIO =======================
MOTIF=[(0,62,0.5),(0.5,65,0.5),(1.0,64,0.5),(1.5,57,1.0)]      # D-F-E-A: the music identity (shared with B)
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=23); sr=s.sr; n=s.n; t=s.t; M=np.zeros(n); AMB=np.zeros(n)
    def note(buf,t0,m,d,v,wave='sq',duty=0.5,dec=3.0,att=0.01):
        f=440*2**((m-69)/12); tt=s.T(d); ph=(f*tt)%1
        x=np.where(ph<duty,1.0,-1.0) if wave=='sq' else (4*np.abs(ph-0.5)-1 if wave=='tri' else np.sin(2*np.pi*ph))
        env=np.minimum(1,tt/att)*np.exp(-tt*dec); i=int(t0*sr); j=min(n,i+len(tt)); buf[i:j]+=(x*env*v)[:j-i]
    def organ(t0,m,d,v):
        for k,a in ((1,1.0),(2,0.4),(0.5,0.6)): note(M,t0,m+12*math.log2(k),d,v*a,'sin',dec=0.6,att=0.08)
    def nb(t0,d,lo,hi,v,seed,shape=2,pan=0.0): s.place(s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v,pan)
    def thud(t0,f=55,v=0.3,d=0.6): tt=s.T(d); s.place(np.sin(2*np.pi*f*tt*(1-0.3*tt/d))*np.exp(-tt*8)+s.filt_short(s.noise(d,int(t0*13)),lo=60,hi=700)*np.exp(-tt*12)*0.6,t0,v)
    def clank(t0,v=0.15,seed=0): tt=s.T(0.6); s.place(sum(np.sin(2*np.pi*f*tt)*np.exp(-tt*k) for f,k in ((310,6),(820,9),(1490,14)))*0.4+s.filt_short(s.noise(0.6,seed),lo=1200,hi=6000)*np.exp(-tt*30),t0,v)
    def step_k(t0,v=0.05,seed=0): tt=s.T(0.12); s.place(s.filt_short(s.noise(0.12,seed),lo=900,hi=5000)*np.exp(-tt*45)+np.sin(2*np.pi*2300*tt)*np.exp(-tt*60)*0.3,t0,v)
    def step_b(t0,v=0.35): thud(t0,45,v,0.5); nb(t0,0.15,200,1500,v*0.15,int(t0*31))
    def zap(t0,v=0.25,seed=0):                               # barrier impact
        tt=s.T(0.7); sweep=np.sin(2*np.pi*np.cumsum(900*np.exp(-tt*5)+70)/sr)*np.exp(-tt*5)
        s.place(sweep*0.6+s.filt_short(s.noise(0.7,seed),lo=1500,hi=9000)*np.exp(-tt*14)*0.5,t0,v); thud(t0,60,v*0.8,0.4)
    def chime(t0,v=0.06,up=True):                            # barrier lets someone through
        for k,m in enumerate((74,79,83,86) if up else (86,83,79,74)): note(s.L if False else M,t0+k*0.06,m,0.6,v,'sin',dec=4)
    # ---------- ambience (dungeon air, drips) ----------
    AMB+=s.filt(s.rng.normal(0,1,n),lo=50,hi=500)*0.02
    pr=np.random.default_rng(4)
    for tc in np.cumsum(pr.exponential(1.4,40)):
        if tc<DUR: tt=s.T(0.15); i=int(tc*sr); j=min(n,i+len(tt)); AMB[i:j]+=(np.sin(2*np.pi*np.cumsum(1400+900*np.exp(-tt*30))/sr)*np.exp(-tt*25)*0.02)[:j-i]
    # ---------- music: low ominous drone + motif ----------
    dr=(np.sin(2*np.pi*36.7*t)+0.6*np.sin(2*np.pi*55.0*t+np.sin(2*np.pi*0.2*t)))*0.03; M+=dr
    for k in range(int(DUR/1.0)): note(M,k*1.0,26,0.9,0.05,'tri',dec=2.5)             # heartbeat pulse
    for t0 in (0.15,):                                                                 # HOOK motif (shared with B)
        for dt,m,dd in MOTIF: organ(t0+dt,m,dd+0.2,0.035)
    for dt,m,dd in MOTIF: organ(4.2+dt,m-12,dd+0.3,0.03)
    for dt,m,dd in MOTIF: organ(21.2+dt,m,dd+0.3,0.04)
    for dt,m,dd in MOTIF: organ(26.7+dt*1.2,m+12,dd+0.4,0.03)
    for dt,m,dd in MOTIF: organ(28.6+dt,m-12,dd+0.3,0.045)
    # ---------- hook ----------
    for k,ti in enumerate(HOOK_IMPACTS): zap(ti,0.3,10+k); step_b(ti-0.1,0.25)
    # ---------- arrival ----------
    for k in range(10): nb(4.0+k*0.14,0.12,300,2500,0.04,20+k)                          # chains rattle
    tt=s.T(1.4); s.place(np.sin(2*np.pi*np.cumsum(90+40*np.sin(2*np.pi*1.2*tt))/sr)*np.sin(np.pi*tt/1.4)*0.6+s.filt_short(s.noise(1.4,3),lo=100,hi=900)*0.4,4.0,0.2)  # gate creak
    for k in range(3): step_b(4.25+k*0.55,0.2)                                       # boss walks away from the door
    for k in range(2): step_b(5.9+k*0.5,0.16)                                        # ...and turns
    tt=s.T(0.6); s.place(s.filt_short(s.noise(0.6,17),lo=1800,hi=8000)*np.sin(np.pi*tt/0.6)+np.sin(2*np.pi*np.cumsum(600+900*tt)/sr)*np.exp(-tt*4)*0.3,7.3,0.1)   # draws the sword from his back
    # ---------- knight enters ----------
    for k in range(5): step_k(9.0+k*0.22,0.05,40+k)
    chime(9.2,0.03)
    tt=s.T(0.45); s.place(s.filt_short(s.noise(0.45,7),lo=2500,hi=9000)*np.sin(np.pi*tt/0.45)+np.sin(2*np.pi*np.cumsum(2000+2500*tt)/sr)*np.exp(-tt*3)*0.2,10.0,0.08)   # sword draw
    nb(10.65,0.3,200,2000,0.08,9)
    thud(10.95,40,0.9,1.4); clank(10.97,0.35,11); thud(11.1,32,0.5,1.0)                # GATE SLAM
    M[int(10.95*sr):int(11.6*sr)]*=0.3
    # ---------- boss walks out ----------
    tt=s.T(0.6); s.place(np.sin(2*np.pi*np.cumsum(70+20*tt)/sr)*np.exp(-tt*3),12.35,0.12)   # weapon lowered
    for k in range(6): step_b(12.7+k*0.62,0.22)
    nb(12.9,3.2,1500,6000,0.025,12,shape=1)                                           # blade scraping the floor
    tt=s.T(1.1); s.place(np.sin(2*np.pi*np.cumsum(100+40*np.sin(2*np.pi*1.5*tt))/sr)*np.sin(np.pi*tt/1.1)*0.6,14.8,0.15)   # gate opens by itself
    chime(16.0,0.035)
    # ---------- SUDDEN SILENCE 16.2-17.5 ----------
    sil=np.ones(n); a_,b_=int(16.2*sr),int(17.5*sr); sil[a_:b_]=0.03; k=int(0.03*sr); sil=np.convolve(sil,np.ones(k)/k,'same')
    # ---------- knight runs, crash ----------
    for k in range(7): step_k(17.65+k*0.18,0.06,60+k)
    for k,ti in enumerate(KNIGHT_IMPACTS): zap(ti,0.32 if k==0 else 0.22,30+k)
    clank(18.92,0.25,31); thud(19.3,80,0.2,0.4); clank(19.32,0.08,32)                  # falls on armour
    for k,dt in enumerate((0.3,0.42,0.5)): clank(SWORD_DROP+dt,0.1-0.025*k,33+k)        # dropped sword clatters on the stone
    # ---------- reveal ----------
    tt=s.T(2.0); s.place(np.sin(2*np.pi*55*tt)*np.minimum(1,tt/0.6)*np.exp(-tt*1.2)+0.5*np.sin(2*np.pi*82.4*tt)*np.minimum(1,tt/0.6)*np.exp(-tt*1.2),21.0,0.18)  # letters ignite
    for k in range(5): note(M,23.05+k*0.07,84-k*3,0.08,0.03,'sq',0.5,20)                 # knight bar flickers out
    note(M,24.35,45,0.4,0.08,'sq',0.5,4); note(M,24.35,33,0.6,0.1,'tri',dec=2)           # boss bar slam
    for k in range(14): note(M,24.6+k*0.064,57+k,0.06,0.03,'sq',0.25,15)                # bar fills
    note(M,25.55,69,0.5,0.05,'sq',0.5,4)
    # ---------- twist: daylight ----------
    out=np.zeros(n); i0,i1=int(26.6*sr),int(28.55*sr); out[i0:i1]=1; out=np.convolve(out,np.ones(1200)/1200,'same')
    birds=np.zeros(n)
    for k in range(6):
        tc=26.7+k*0.3; tt=s.T(0.12); i=int(tc*sr); birds[i:i+len(tt)]+=np.sin(2*np.pi*np.cumsum(3000+1200*np.sin(2*np.pi*20*tt))/sr)*np.exp(-tt*20)*0.02
    wind=s.filt(s.rng.normal(0,1,n),lo=200,hi=1500)*0.012
    for k in range(3): step_b(26.75+k*0.62,0.12)
    # ---------- voices ----------
    NB=np.zeros(n); duck=np.ones(n)
    for k_,t0 in NARR:
        a,ar=_sf.read(os.path.join(TTS_DIR,'fb',f'{k_}.wav')); a=a if a.ndim==1 else a.mean(1)
        a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a)
        i=int(t0*sr); j=min(n,i+len(a)); NB[i:j]+=a[:j-i]*(1.15 if k_=='B1' else 1.0)
        duck[max(0,i-int(0.05*sr)):min(n,j+int(0.1*sr))]=0.45
    duck=np.convolve(duck,np.ones(2400)/2400,'same')
    inside=1-out
    s.L+=(2.2*M*duck+AMB*inside)*sil; s.R+=(2.2*np.roll(M,300)*duck+np.roll(AMB,900)*inside)*sil
    s.L+=(birds+wind)*out; s.R+=(np.roll(birds,500)+wind)*out
    s.reverb(0.28,length=2.2,decay=2.6)
    pk=max(np.abs(s.L).max(),np.abs(s.R).max()); gv=pk*1.05/np.abs(NB).max()
    s.L=s.L*(0.55+0.45*duck)+NB*gv; s.R=s.R*(0.55+0.45*duck)+NB*gv
    return s.save(path,peak=0.9)
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'final_boss_a.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'fb_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.95,vignette=0.3,grain=1.8,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(post.upscale(frame(f/FPS),S),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
