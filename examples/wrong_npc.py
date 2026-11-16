"""HE PICKED THE WRONG NPC - 60 s PS1 open-world-city short, 9:16. Fully procedural (nightkit).
TEST=t1,t2 python examples/wrong_npc.py | PART=a:b | PART=audio"""
import os, sys, math, json
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','tts'))   # Kokoro models + generated voice lines live here
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, box, quad, tiled_plane, transform
from nightkit import motion, post, font
from nightkit.audio import Sound
OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6; DUR=60.0; N=int(DUR*FPS)
sm=motion.smooth
def seg01(t,a,b): return max(0.0,min(1.0,(t-a)/(b-a)))
def win(t,a,b,ra=0.2,rb=0.2): return sm(seg01(t,a,a+ra))*(1-sm(seg01(t,b-rb,b)))
def lerp(a,b,u): return a+(b-a)*u
def lerp3(a,b,u): return tuple(a[i]+(b[i]-a[i])*u for i in range(len(a)))
def Rx(a): c,s=math.cos(a),math.sin(a); return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def Ry(a): c,s=math.cos(a),math.sin(a); return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def Rz(a): c,s=math.cos(a),math.sin(a); return np.array([[c,-s,0],[s,c,0],[0,0,1]])
def obox(center,hs,R,col,emit=False):
    c=np.array(center,float); return box(-hs[0],hs[0],-hs[1],hs[1],-hs[2],hs[2],col,xf=lambda p:tuple(c+R@np.array(p)),emit=emit)
def seg(p0,p1,w,col,depth=None,emit=False):
    p0=np.array(p0,float); p1=np.array(p1,float); d=p1-p0; L=np.linalg.norm(d)+1e-9; d/=L
    up=np.array([0,0,-1.0]) if abs(d[1])>0.9 else np.array([0,1.0,0]); a=np.cross(d,up); a/=np.linalg.norm(a)+1e-9; b=np.cross(a,d); dp=depth or w
    v=[p0-a*w/2-b*dp/2,p0+a*w/2-b*dp/2,p0+a*w/2+b*dp/2,p0-a*w/2+b*dp/2,p1-a*w/2-b*dp/2,p1+a*w/2-b*dp/2,p1+a*w/2+b*dp/2,p1-a*w/2+b*dp/2]
    F=[(0,1,2,3),(5,4,7,6),(4,0,3,7),(1,5,6,2),(3,2,6,7),(4,5,1,0)]
    return [quad([tuple(v[i]) for i in f],col,emit) for f in F]
def elbow(sh,hand,out_dir,L=0.58):
    sh=np.array(sh); hand=np.array(hand); m=(sh+hand)/2; d=np.linalg.norm(hand-sh)
    bend=max(0.0,(L-d)/L)*0.25+0.03; return tuple(m+np.array(out_dir)*bend+np.array([0,-1,0])*bend*0.6)
def yaw_to(frm,to): d=np.array(to,float)-np.array(frm,float); return math.atan2(-d[0],-d[-1])
# ======================= PEOPLE (one function, fixed outfits) =======================
OUTFITS={
 'A':dict(skin=(214,170,140),hair=(60,36,24),hat='beret',hatc=(198,26,36),top=(232,232,228),check=(20,20,22),pants=(52,62,92),shoes=(236,236,236),pack=(116,84,52),h=0.96),
 'B':dict(skin=(186,138,108),hair=(18,16,16),top=(26,26,30),pants=(38,38,44),shoes=(14,14,16),collar=True,h=1.07,brow=True),
 'C':dict(skin=(166,118,88),hair=(20,18,18),top=(128,130,138),hood=True,pants=(62,72,104),shoes=(200,200,200),pack=(38,48,82),h=1.0),
 'D':dict(skin=(228,190,160),hair=(206,170,96),top=(218,204,174),pants=(196,194,186),shoes=(150,110,80),h=0.98),
 'E':dict(skin=(120,80,60),hair=(16,14,14),top=(56,118,82),pants=(30,30,36),shoes=(236,236,236),h=1.02),
 'F':dict(skin=(200,150,118),hair=(40,32,28),hat='cap',hatc=(30,40,70),top=(70,104,164),pants=(150,124,90),shoes=(40,30,24),mous=True,h=1.0),
 'P1':dict(skin=(220,180,150),hair=(90,60,40),top=(170,60,60),pants=(40,40,60),shoes=(30,30,30),h=0.97),
 'P2':dict(skin=(150,100,70),hair=(20,20,20),top=(60,80,140),pants=(120,110,100),shoes=(60,40,30),h=1.0),
 'P3':dict(skin=(230,196,170),hair=(220,200,150),top=(200,180,60),pants=(50,50,50),shoes=(220,220,220),h=0.95),
 'P4':dict(skin=(190,140,100),hair=(30,24,20),top=(90,90,96),pants=(30,40,70),shoes=(30,30,30),pack=(150,40,40),h=1.01),
 'P5':dict(skin=(110,74,56),hair=(14,12,12),top=(210,210,214),pants=(60,64,70),shoes=(30,30,30),h=1.03),
 'P6':dict(skin=(210,166,130),hair=(120,70,40),top=(120,50,110),pants=(40,40,46),shoes=(200,200,200),h=0.94),
}
def person(key,base,yaw,walk=0.0,run=0.0,rh=None,lh=None,lean=0.0,hy=0.0,hp=0.0,eye=1.0,brow=0.0,mouth=0.0,t=0.0):
    """faces -z at yaw 0. Faces/patterns live in decals (hc-culled). brow: -1 worried .. +1 angry."""
    O=OUTFITS[key]; k=O['h']; b=np.array(base,float); Rb=Ry(yaw)
    def W(p): return tuple(b+Rb@(np.array(p,float)*k))
    hip=0.84
    def WL(p):
        p=np.array(p,float); piv=np.array([0,hip,0]); return W(piv+Rx(lean+0.25*run)@(p-piv))
    Q=[]; D=[]; amp=0.45+0.25*run; sw=amp*math.sin(walk)
    for sx,ph in ((-1,1),(1,-1)):
        hp_=np.array([sx*0.09,hip,0]); a=ph*sw
        ft=hp_+np.array([0,-0.8*math.cos(a),-0.8*math.sin(a)]); lift=0.08*max(0,math.sin(walk*ph+math.pi/2))*(1 if walk else 0)
        ft[1]=max(0.05,ft[1]+lift); kn=(hp_+ft)/2+np.array([0,0,-0.05-0.06*run])
        Q+=transform(seg(hp_,kn,0.13,O['pants'])+seg(kn,ft,0.115,O['pants'])+box(ft[0]-0.06,ft[0]+0.06,ft[1]-0.05,ft[1]+0.03,ft[2]-0.13,ft[2]+0.05,O['shoes']),W)
    Q+=box(-0.18,0.18,0.82,1.36,-0.11,0.11,O['top'],xf=WL)
    if O.get('check'):                                       # black & white checked shirt (front + back)
        for zf in (-0.116,0.116):
            for i in range(4):
                for j in range(6):
                    if (i+j)%2==0: x0=-0.17+i*0.085; y0=0.84+j*0.085; D+=box(x0,x0+0.07,y0,y0+0.07,min(zf,zf+0.004),max(zf,zf+0.004),O['check'],xf=WL)
    if O.get('collar'): D+=box(-0.07,0.07,1.22,1.36,-0.118,-0.11,(60,60,66),xf=WL)+box(-0.015,0.015,0.84,1.22,-0.118,-0.112,(10,10,12),xf=WL)
    if O.get('hood'): Q+=box(-0.15,0.15,1.3,1.46,0.07,0.17,O['top'],xf=WL); D+=box(-0.08,0.08,0.95,1.06,-0.118,-0.11,(108,110,118),xf=WL)
    if O.get('pack'):
        Q+=box(-0.15,0.15,0.9,1.3,0.11,0.26,O['pack'],xf=WL)
        for sx in (-1,1): D+=box(sx*0.1-0.025,sx*0.1+0.025,0.95,1.36,-0.118,-0.11,O['pack'],xf=WL)
    hc=np.array([0,1.5,0])
    def WH(p): p=np.array(p,float); return WL(hc+Ry(hy)@Rx(hp)@(p-hc))
    Q+=box(-0.05,0.05,1.34,1.4,-0.05,0.05,O['skin'],xf=WL)+box(-0.1,0.1,1.38,1.62,-0.11,0.1,O['skin'],xf=WH)
    Q+=box(-0.108,0.108,1.56,1.66,-0.1,0.11,O['hair'],xf=WH)+box(-0.108,0.108,1.42,1.6,0.07,0.115,O['hair'],xf=WH)
    if O.get('hat')=='beret':
        Q+=box(-0.125,0.135,1.62,1.7,-0.115,0.12,O['hatc'],xf=WH)+box(-0.11,0.12,1.69,1.72,-0.1,0.1,O['hatc'],xf=WH)+box(0.02,0.04,1.72,1.75,-0.01,0.01,O['hatc'],xf=WH)
    if O.get('hat')=='cap': Q+=box(-0.115,0.115,1.6,1.7,-0.11,0.115,O['hatc'],xf=WH)+box(-0.1,0.1,1.6,1.62,-0.22,-0.1,O['hatc'],xf=WH)
    if O.get('hood'): pass
    D+=box(-0.1,0.1,1.57,1.6,-0.118,-0.11,O['hair'],xf=WH)                      # fringe
    for sx in (-1,1):
        x=sx*0.045; e=0.016*eye
        D+=box(x-0.014,x+0.014,1.5-e,1.5+e,-0.118,-0.11,(24,20,22),xf=WH)
        if eye>1.2: D+=box(x-0.004,x+0.004,1.505,1.512,-0.12,-0.118,(255,255,255),xf=WH)
        bt=brow+(0.8 if O.get('brow') else 0.0); by=1.535+0.012*(eye-1)
        D+=transform(seg((x-sx*0.025,by+0.006*bt,-0.116),(x+sx*0.02,by-0.008*bt,-0.116),0.012,O['hair'],depth=0.004),WH)
    if O.get('mous'): D+=box(-0.04,0.04,1.44,1.455,-0.118,-0.11,O['hair'],xf=WH)
    mh=0.008+0.03*mouth; D+=box(-0.022+0.008*mouth,0.022-0.008*mouth,1.425-mh/2,1.425+mh/2,-0.118,-0.11,(110,50,50),xf=WH)
    for sx,hd in ((-1,rh),(1,lh)):
        if hd is None: s_=-sx*amp*0.7*math.sin(walk)*(1 if walk else 0); hd=(sx*0.24,0.86+0.06*abs(s_)+0.18*run,-0.32*s_-0.1*run)
        sh=np.array(WL((sx*0.24,1.3,0))); hw=np.array(WL(hd)); el=elbow(sh,hw,tuple(Rb@np.array([sx*0.6,0,-0.15])),0.58*k)
        Q+=seg(sh,el,0.1*k,O['top'])+seg(el,hw,0.09*k,O['top'])+obox(hw,(0.045*k,0.05*k,0.045*k),Rb,O['skin'])
    hcW=np.array(WH((0,1.5,0))); tcW=np.array(WL((0,1.1,0)))
    for q in D: q['hc']=hcW if q['c'][1]>hcW[1]-0.14*k else tcW
    return Q,D
# ======================= VEHICLES =======================
TAXI=(236,190,30); TAXI_D=(190,150,20); GLASS=(40,52,70); TIRE=(20,20,22)
def car_model(col,col_d,taxi=False,hazard=False,brake=False,door=0.0):
    """local: forward +x, length 4.2, width 1.8, ground y=0. driver door on -z side."""
    Q=box(-2.1,2.1,0.32,0.9,-0.9,0.9,col)+box(-1.0,1.05,0.9,1.4,-0.82,0.82,col_d)
    Q+=box(1.05,1.1,0.93,1.36,-0.76,0.76,GLASS)+box(-1.05,-1.0,0.93,1.36,-0.76,0.76,GLASS)
    for zs in (-1,1): Q+=box(-0.9,0.95,0.95,1.34,zs*0.825-0.01,zs*0.825+0.01,GLASS)
    Q+=box(2.1,2.14,0.45,0.6,-0.8,-0.5,(250,250,230),emit=True)+box(2.1,2.14,0.45,0.6,0.5,0.8,(250,250,230),emit=True)
    rc=(255,40,40) if brake else (150,20,20)
    Q+=box(-2.14,-2.1,0.55,0.7,-0.8,-0.55,rc,emit=brake)+box(-2.14,-2.1,0.55,0.7,0.55,0.8,rc,emit=brake)
    hz=(255,160,20) if hazard else (130,90,20)
    for x in (2.11,-2.15):
        for zs in (-1,1): Q+=box(x,x+0.04,0.48,0.56,zs*0.9-0.1*zs-0.05,zs*0.9-0.1*zs+0.05,hz,emit=hazard)
    for x in (-1.35,1.35):
        for zs in (-1,1): Q+=box(x-0.33,x+0.33,0.0,0.62,zs*0.9-0.13,zs*0.9+0.04*zs,TIRE)
    if taxi:
        Q+=box(-0.3,0.3,1.4,1.58,-0.22,0.22,(250,246,220),emit=True)
        for zs in (-1,1): Q+=box(-1.9,1.9,0.6,0.66,zs*0.905-0.01,zs*0.905+0.01,(20,20,20))   # checker stripe
    if door>0:                                             # driver door swinging out on -z side
        hx=0.85; a=1.1*door
        def Tf(p): p=np.array(p,float)-np.array([hx,0,-0.9]); return tuple(Ry(a)@p+np.array([hx,0,-0.9]))
        Q+=transform(box(-0.25,hx,0.35,0.9,-0.93,-0.88,col)+box(-0.2,hx-0.05,0.92,1.32,-0.92,-0.9,GLASS),Tf)
    return Q
def place(Q,pos,yaw,pitch=0.0):
    R=Ry(yaw)@Rz(pitch); p=np.array(pos,float); return transform(Q,lambda v:tuple(p+R@np.array(v)))
# ======================= CITY =======================
ASPH=lambda i,j:[(70,72,78),(64,66,72),(74,76,80)][(i*3+j)%3]
WALK=lambda i,j:[(150,146,138),(140,136,128)][(i+j)%2]
def city():
    G=tiled_plane(-46,46,-4.5,4.5,0,2.0,ASPH)
    G+=tiled_plane(-46,46,-8.5,-4.5,0.15,2.0,WALK)+tiled_plane(-46,46,4.5,8.5,0.15,2.0,WALK)
    G+=tiled_plane(-46,46,-0.8,0.8,0.004,2.0,lambda i,j:(96,92,90))                # tram bed
    O=[]
    for x in np.arange(-46,46,4.0):
        for z in (-0.38,0.38): O.append(quad([(x,0.012,z-0.04),(x+4,0.012,z-0.04),(x+4,0.012,z+0.04),(x,0.012,z+0.04)],(170,170,176)))
        for zz in (-4.5,4.5): O+=box(x,x+4,0,0.15,zz-0.06,zz+0.06,(120,118,112))           # curbs
        for zz in (-2.65,2.65):
            if abs(x+2)>3: O.append(quad([(x+0.5,0.008,zz-0.06),(x+2.5,0.008,zz-0.06),(x+2.5,0.008,zz+0.06),(x+0.5,0.008,zz+0.06)],(220,220,210)))
    for i in range(5):                                                             # zebra bars
        x0=-1.6+i*0.72
        for z0,z1 in ((-4.4,-0.85),(0.85,4.4)): O.append(quad([(x0,0.01,z0),(x0+0.42,0.01,z0),(x0+0.42,0.01,z1),(x0,0.01,z1)],(232,232,226)))
    for x,z0,z1 in ((-2.4,-4.4,-0.85),(2.4,0.85,4.4)): O.append(quad([(x-0.15,0.01,z0),(x+0.15,0.01,z0),(x+0.15,0.01,z1),(x-0.15,0.01,z1)],(232,232,226)))
    B=[]
    rng=np.random.default_rng(4); pal=[(150,120,100),(120,124,132),(170,160,140),(110,90,80),(140,140,150),(160,110,90)]
    for side in (-1,1):
        x=-46.0
        while x<46:
            w=rng.uniform(6,10); h=rng.uniform(7,15); c=pal[int(rng.integers(0,len(pal)))]
            z0=side*8.5; z1=side*15
            if abs(x+w/2+17)<4: x+=w; continue                                 # gap for the cross street
            B+=box(x,x+w-0.3,0,h,min(z0,z1),max(z0,z1),c)
            fz=z0-side*0.02
            for fl in range(1,int(h/2.6)):
                for wx in np.arange(x+0.8,x+w-1.2,1.6):
                    y=fl*2.6+0.6; B.append(quad([(wx,y,fz),(wx+0.9,y,fz),(wx+0.9,y+1.1,fz),(wx,y+1.1,fz)],(70,90,120)))
            B.append(quad([(x+0.4,2.6,fz-side*0.4),(x+w-0.7,2.6,fz-side*0.4),(x+w-0.7,3.0,fz),(x+0.4,3.0,fz)],[(180,40,40),(40,110,60),(40,60,140),(200,150,40)][int(rng.integers(0,4))]))
            x+=w
    G+=tiled_plane(-21,-13,-46,-8.5,0,2.0,ASPH)+tiled_plane(-21,-13,8.5,46,0,2.0,ASPH)    # cross street
    return G,O,B
CITY_G,CITY_O,CITY_B=city()
def signal_heads(T):
    """car signal: red while pedestrians walk. ped signal: walking figure / flashing red hand."""
    car_go=22.8<=T<44.5; ped_flash=20.6<=T<22.8
    Q=[]
    for (px,pz,face) in ((-2.1,-4.8,1),(2.1,4.8,-1)):
        Q+=box(px-0.06,px+0.06,0.15,3.4,pz-0.06,pz+0.06,(60,62,66))
        Q+=box(px-0.06,px+0.06,3.3,3.4,pz-0.06,pz+0.06+face*0.0,(60,62,66))
        # car head (faces traffic: along x)
        hx=px-face*0.0; Q+=box(hx-0.14,hx+0.14,2.5,3.2,pz-0.14,pz+0.14,(30,30,34))
        for k,(cy,on,c) in enumerate(((3.05,not car_go,(255,40,30)),(2.85,False,(255,170,0)),(2.65,car_go,(40,240,90)))):
            fx=hx-face*0.15; Q.append(quad([(fx,cy-0.07,pz-0.07),(fx,cy-0.07,pz+0.07),(fx,cy+0.07,pz+0.07),(fx,cy+0.07,pz-0.07)],c if on else tuple(v//5 for v in c),emit=True))
        # ped head (faces across the street)
        Q+=box(px-0.16,px+0.16,1.9,2.3,pz-0.1,pz+0.1,(30,30,34))
        green=not car_go and not ped_flash; red=car_go or (ped_flash and int(T*3)%2==0)
        fz=pz+face*0.105
        Q.append(quad([(px-0.12,1.94,fz),(px+0.12,1.94,fz),(px+0.12,2.1,fz),(px-0.12,2.1,fz)],(40,240,90) if green else (20,50,30),emit=True))
        Q.append(quad([(px-0.12,2.12,fz),(px+0.12,2.12,fz),(px+0.12,2.27,fz),(px-0.12,2.27,fz)],(255,60,40) if red else (60,20,16),emit=True))
    return Q
# ======================= MOTION TRACKS =======================
class Track:
    def __init__(s,keys,stride=0.72,yaw_keys=None):
        s.k=keys; s.stride=stride; s.yk=yaw_keys; s.ts=np.arange(-1,61,1/48); s.P=np.array([s.pos(t) for t in s.ts])
        d=np.r_[0,np.cumsum(np.linalg.norm(np.diff(s.P,axis=0),axis=1))]; s.D=d
    def pos(s,t):
        K=s.k
        if t<=K[0][0]: return np.array(K[0][1],float)
        for (a,pa),(b,pb) in zip(K,K[1:]):
            if t<b: u=(t-a)/(b-a); u=u if len(K)>2 and False else u; return np.array(pa,float)+(np.array(pb,float)-np.array(pa,float))*u
        return np.array(K[-1][1],float)
    def at(s,t):
        p=s.pos(t); i=int(np.clip((t+1)*48,0,len(s.D)-1)); dist=s.D[i]
        moving=np.linalg.norm(s.pos(t+0.05)-s.pos(t-0.05))>0.004
        return p,dist/s.stride*math.pi,moving
    def heading(s,t):
        a=s.pos(t-0.08); b=s.pos(t+0.08); d=b-a
        return math.atan2(-d[0],-d[1]) if np.linalg.norm(d)>1e-3 else None
def yawk(t,K,default=None):
    if not K: return default
    if t<=K[0][0]: return K[0][1]
    for (a,va),(b,vb) in zip(K,K[1:]):
        if t<b: return va+(vb-va)*sm((t-a)/(b-a))
    return K[-1][1]
PI=math.pi
# A (red beret): crosses north, gets blocked, pushed back behind the line, escorted to the north sidewalk
TA=Track([(0,(0.05,-6.6)),(4.0,(0.05,-4.2)),(6.5,(0.05,-0.85)),(7.3,(0.05,-0.85)),(7.8,(0.72,-0.9)),(8.5,(0.72,-0.9)),(9.0,(-0.5,-0.9)),(9.6,(-0.5,-0.9)),(10.2,(-0.5,-1.45)),
          (18.3,(-0.5,-1.45)),(18.8,(-0.85,-1.8)),(27.5,(-0.85,-1.8)),(29.0,(-0.3,-2.35)),(47.6,(-0.3,-2.35)),(52.4,(0.3,5.55)),(60,(0.3,5.55))])
YA=[(0,PI),(10.2,PI),(18.3,PI),(18.8,PI+0.25),(27.5,PI+0.25),(29.0,PI),(47.6,PI),(53.4,PI),(54.0,PI/2+0.25),(60,PI/2+0.25)]
# B (black jacket)
TB=Track([(0,(0.3,9.0)),(4.0,(0.3,5.6)),(6.6,(0.08,-0.15)),(7.6,(0.08,-0.15)),(8.1,(0.75,-0.2)),(8.75,(0.75,-0.2)),(9.25,(-0.48,-0.2)),(10.0,(-0.48,-0.2)),(10.6,(-0.45,-0.55)),
          (19.4,(-0.45,-0.55)),(20.0,(-0.68,-1.05)),(28.0,(-0.68,-1.05)),(29.0,(-0.35,-0.55)),(43.2,(-0.35,-0.55)),(43.8,(-0.35,-0.05)),(46.4,(-0.35,-0.05)),(49.2,(-0.45,4.9)),(53.0,(-6.5,5.9)),(60,(-14.0,5.9))],stride=0.8)
YB=[(0,0.0),(6.6,0.0),(19.4,0.0),(20.0,0.2),(28.0,0.2),(29.0,0.0),(46.0,0.0),(46.4,PI),(49.0,PI),(49.4,PI/2),(60,PI/2)]
# C (gray hoodie): walks by, stops, steps in, gets pushed, comes back, leads the escort
TC=Track([(0,(-15.0,-5.6)),(12.0,(-6.8,-5.6)),(13.1,(-3.0,-5.6)),(13.7,(-3.0,-5.6)),(14.6,(-1.5,-2.4)),(15.5,(-0.42,-0.98)),(18.25,(-0.42,-0.98)),(19.0,(0.75,-2.3)),
          (27.0,(0.75,-2.3)),(28.5,(-0.95,-1.6)),(47.6,(-0.95,-1.6)),(52.4,(-0.55,5.65)),(60,(-0.55,5.65))])
YC=[(0,-PI/2),(13.1,-PI/2),(13.3,-PI/2-0.6),(13.7,-PI/2-0.6),(14.0,None),(15.5,None),(15.6,PI),(18.25,PI),(18.9,PI+0.5),(27.0,PI+0.5),(27.2,None),(28.4,None),(28.6,PI),(47.6,PI),(48.0,None),(52.3,None),(53.0,-PI/2),(60,-PI/2)]
# D (light clothes) / E (green jacket): on the south sidewalk, notice, jog in once the taxi has blocked the lane
TD=Track([(0,(18.0,-5.9)),(22.4,(3.2,-5.9)),(25.0,(3.2,-5.9)),(27.6,(-0.2,-1.55)),(47.6,(-0.2,-1.55)),(52.4,(0.95,5.5)),(60,(0.95,5.5))])
TE=Track([(0,(19.4,-6.4)),(22.4,(4.0,-6.4)),(25.2,(4.0,-6.4)),(28.0,(0.5,-1.65)),(47.6,(0.5,-1.65)),(52.4,(1.0,4.75)),(60,(1.0,4.75))])
YD=[(0,PI/2),(22.4,PI/2),(22.8,PI/2+0.75),(25.0,PI/2+0.75),(25.1,None),(27.5,None),(27.8,PI),(47.6,PI),(47.9,None),(52.3,None),(53.0,PI/2+0.8),(60,PI/2+0.8)]
YE=[(0,PI/2),(22.6,PI/2),(23.0,PI/2+0.8),(25.2,PI/2+0.8),(25.3,None),(27.9,None),(28.2,PI),(47.6,PI),(47.9,None),(52.3,None),(53.0,PI/2+1.1),(60,PI/2+1.1)]
# F taxi driver
TF=Track([(0,(-4.2,-2.6)),(27.9,(-4.2,-2.6)),(28.5,(-4.0,-3.7)),(29.3,(-2.6,-3.6)),(31.0,(-1.75,-1.4)),(46.8,(-1.75,-1.4)),(48.6,(-3.6,-3.65)),(49.3,(-4.2,-2.6)),(60,(-4.2,-2.6))])
YF=[(0,-PI/2),(28.5,-PI/2),(28.6,None),(30.9,None),(31.1,PI+0.7),(46.8,PI+0.7),(46.9,None),(49.2,None),(49.4,-PI/2),(60,-PI/2)]
def ppos(track,yk,t,default_yaw=0.0):
    p,ph,mv=track.at(t); y=None
    if yk:
        for (a,va),(b,vb) in zip(yk,yk[1:]):
            if a<=t<b:
                if va is None or vb is None: y=track.heading(t)
                else: y=va+(vb-va)*sm((t-a)/(b-a))
                break
        else: y=yk[-1][1] if t>=yk[-1][0] else yk[0][1]
    if y is None: y=track.heading(t) or default_yaw
    return (p[0],0.15 if abs(p[1])>4.5 else 0.0,p[1]),y,ph if mv else 0.0
def taxi_x(t):
    """cruise 11 m/s, brake hard 23.7-24.9 (stops before the crosswalk), wait, leave at 50.8"""
    if t<23.7: return -11.2-11*(23.7-t)
    if t<24.9: u=(t-23.7)/1.2; return -11.2+11*1.2*(u-u*u/2)
    if t<50.8: return -4.6
    d=t-50.8; return -4.6+0.5*2.6*min(d,4)**2+(10.4*(d-4) if d>4 else 0)
def taxi_pitch(t): return -0.05*win(t,23.75,25.05,0.15,0.35)+0.02*win(t,50.8,51.6,0.2,0.4)
WALKERS=[('P1',-1,-6.9,1.15,-8.0),('P2',1,-7.6,1.05,12.0),('P3',-1,6.4,1.0,4.0),('P4',1,7.3,1.2,-18.0),('P5',-1,7.6,1.1,20.0),('P6',1,-6.6,1.0,-30.0)]
def walkers(t):
    out=[]
    for key,dr,z,v,x0 in WALKERS:
        x=((x0+dr*v*t)+40)%80-40
        out.append(person(key,(x,0.15,z),-dr*PI/2,walk=abs(v*t)/0.72*PI,t=t))
    return out
def traffic(t):
    """north lane (-x) queue goes on green; south lane cars queue behind the taxi; cross street flows while main road is red"""
    C=[]; cols=[((60,90,150),(40,60,110)),((150,40,40),(110,30,30)),((200,200,205),(150,150,156)),((40,40,44),(26,26,30)),((70,120,80),(50,90,60))]
    def acc(t0,a=3.0,v=9.0):
        d=max(0,t-t0); tv=v/a; return 0.5*a*d*d if d<tv else 0.5*a*tv*tv+v*(d-tv)
    for i,x0 in enumerate((4.7,10.3,15.9)):
        x=x0-acc(22.8+0.6*i)
        if x>-46: C.append((car_model(*cols[i]),(x,0,2.6),PI,0.0))
    for j in range(6):                                                  # stream passes 25-41.5
        te=24.5+j*2.9; x=46-9*(t-te)
        if -46<x<46 and t>=te: C.append((car_model(*cols[(j+3)%5]),(x,0,2.6),PI,0.0))
    for i,(xs,ta) in enumerate(((-10.2,26.5),(-15.8,28.2))):            # behind the taxi
        if t<ta: x=xs-9*(ta-t)*(1-0.5*min(1,(ta-t)/2))
        elif t<51.4+0.6*i: x=xs
        else: x=xs+acc(51.4+0.6*i,2.6,10.4)
        C.append((car_model(*cols[(i+1)%5],brake=ta-0.8<t<51.4),(x,0,-2.6),0.0,0.0))
    if t<22.8 or t>=44.5:                                               # cross street (perpendicular), far west
        for j in range(5):
            z=((t*9+j*19)%90)-45; C.append((car_model(*cols[j%5]),(-15.5,0,z),-PI/2,0.0))
            z2=45-((t*8+j*23)%90); C.append((car_model(*cols[(j+2)%5]),(-18.5,0,z2),PI/2,0.0))
    return C
# ======================= CHARACTER STATES =======================
def talk(t,a,b): return (0.5+0.5*math.sin(t*26))*win(t,a,b,0.05,0.05)
def state_A(t):
    base,yaw,ph=ppos(TA,YA,t)
    kw=dict(walk=ph,eye=1.0,brow=-0.4,mouth=0.0)
    if 6.5<=t<47.6:
        kw['rh']=(-0.1,1.22,-0.13); kw['lh']=(0.1,1.22,-0.13); kw['brow']=-1.0; kw['eye']=1.25     # clutching the straps
        if 18.2<=t<18.9: kw['lean']=-0.15; kw['eye']=1.5
        if 29.0<=t: kw['brow']=-0.5; kw['eye']=1.1
        kw['hp']=0.12 if t<20 else 0.05
    if 47.6<=t<53.0: kw['brow']=-0.2; kw['hy']=-0.3*win(t,49.0,50.5,0.3,0.3)
    if t>=53.0:
        kw['brow']=0.0; kw['mouth']=0.15; kw['hp']=0.28*(math.sin((t-54.6)*PI/0.45)**2)*(54.6<=t<55.5)        # the nod
    return base,yaw,kw
def state_B(t):
    base,yaw,ph=ppos(TB,YB,t)
    kw=dict(walk=ph,brow=1.0,eye=0.9)
    if 6.6<=t<19.4:
        kw['lean']=0.12
        if 10.4<=t<15.5: kw['rh']=lerp3((-0.24,0.86,-0.1),(-0.12,1.35,-0.62),win(t,10.4,15.5,0.25,0.3)); kw['mouth']=talk(t,10.6,12.0)*0.8   # pointing at them
        if 15.5<=t<18.4: kw['lean']=0.0 if t<17.1 else 0.14; kw['mouth']=talk(t,17.15,18.1)
        if 18.0<=t<18.6:
            u=win(t,18.0,18.6,0.15,0.25); kw['rh']=lerp3((-0.24,0.86,-0.1),(-0.13,1.24,-0.5),u); kw['lh']=lerp3((0.24,0.86,-0.1),(0.13,1.24,-0.5),u); kw['lean']=0.2*u
    if 19.4<=t<29.0: kw['lean']=0.1; kw['rh']=(-0.12,1.3,-0.55) if 20.2<t<23.5 else None; kw['mouth']=0.3*(20.2<t<23.5)
    if 29.0<=t<46.4:
        kw['lean']=0.0
        surprise=sm(seg01(t,39.4,39.8)); kw['eye']=0.9+0.6*surprise; kw['brow']=1.0-1.8*surprise; kw['mouth']=0.6*surprise
        kw['hy']=0.7*win(t,40.6,41.3,0.2,0.2)-0.7*win(t,41.6,42.3,0.2,0.2)
        up=win(t,44.0,46.3,0.3,0.3); kw['rh']=lerp3((-0.24,0.86,-0.1),(-0.3,1.45,-0.22),up); kw['lh']=lerp3((0.24,0.86,-0.1),(0.3,1.45,-0.22),up)
    if t>=46.4: kw['brow']=0.2; kw['hp']=0.2
    return base,yaw,kw
def state_C(t):
    base,yaw,ph=ppos(TC,YC,t)
    kw=dict(walk=ph,brow=0.2)
    if 13.1<=t<13.7: kw['hy']=-0.4
    if 15.5<=t<18.25:
        u=win(t,15.7,18.1,0.25,0.25); kw['rh']=lerp3((-0.24,0.86,-0.1),(-0.18,1.32,-0.42),u); kw['mouth']=talk(t,15.9,17.1); kw['brow']=0.6
    if 18.25<=t<19.3:
        u=win(t,18.25,19.3,0.1,0.4); kw['lean']=-0.35*u; kw['rh']=(-0.45,1.2,0.1); kw['lh']=(0.45,1.2,0.1)
    if 28.5<=t<47.6: kw['brow']=0.7; kw['rh']=(-0.32,0.95,-0.1); kw['lh']=(0.32,0.95,-0.1)
    if t>=53.0: kw['brow']=-0.2; kw['mouth']=0.2; kw['hp']=0.22*(math.sin((t-55.3)*PI/0.45)**2)*(55.3<=t<56.2)
    return base,yaw,kw
def helper_state(track,yk,t,run_window):
    base,yaw,ph=ppos(track,yk,t); kw=dict(walk=ph,brow=0.5)
    if run_window[0]<=t<run_window[1]: kw['run']=1.0
    if 22.5<=t<25.0: kw['hy']=0.0
    if 28.4<=t<47.6: kw['rh']=(-0.32,0.95,-0.1); kw['lh']=(0.32,0.95,-0.1); kw['brow']=0.7
    return base,yaw,kw
def state_F(t):
    base,yaw,ph=ppos(TF,YF,t); kw=dict(walk=ph,brow=0.6)
    if 31.0<=t<46.8: kw['rh']=(-0.05,1.12,-0.2); kw['lh']=(0.05,1.08,-0.22)   # arms folded
    return base,yaw,kw
def taxi_door(t): return win(t,27.7,29.4,0.35,0.5)+win(t,48.9,49.7,0.3,0.3)
def driver_visible(t): return 28.3<=t<49.4
# ======================= SHOTS =======================
HOOK=lambda T:24.0+T*0.5
def shot(T):
    """(story_time, cam_pos, cam_target, fov)"""
    if T<4.8: st=HOOK(T); return st,(2.5,1.05,-0.15),(-2.6,1.25,-2.0),48
    if T<8.6: u=sm(seg01(T,4.8,8.6)); return T,lerp3((6.5,7.5,-7.6),(5.0,5.2,-6.4),u),(0.0,0.4,-0.3),58
    if T<12.0: return T,(2.4,1.45,-2.7),(-0.15,1.25,-0.7),50
    if T<14.6: return T,(-6.2,1.6,-7.7),(-0.9,1.1,-1.6),54
    if T<19.6: return T,(2.6,1.5,-1.25),(-0.5,1.2,-1.2),54
    if T<22.6: return T,(0.2,2.08,-0.35),(-0.9,1.35,-1.85),50
    if T<23.9: return T,(6.6,1.6,-7.8),(0.6,1.1,-2.5),54
    if T<27.6: return T,(-11.0,1.5,-3.3),(0.0,1.0,-1.8),52
    if T<31.0: return T,(1.8,2.8,-8.8),(-1.0,0.8,-1.6),56
    if T<34.0: return T,(3.3,1.5,-0.5),(-0.6,1.2,-1.3),54
    if T<39.2: return T,(-0.1,1.9,0.8),(-0.35,1.15,-2.0),54
    if T<46.0: return T,(-0.12,1.7,-1.25),(-0.35,1.66,-0.4),48
    if T<50.0: return T,(1.3,3.0,-6.9),(-0.3,1.0,1.5),56
    if T<54.0: return T,(-1.9,1.7,7.9),(0.3,1.0,2.5),54
    return T,(0.15,1.55,2.55),(-0.1,1.3,5.65),50
R=Renderer(W,H,fog=(176,190,204))
def render(T):
    st,pos,tgt,fov=shot(T); cam=Camera.look(pos,tgt); cp=np.array(pos)
    groups=[]
    def add(Q,D=None,c=None):
        if not Q: return
        c=np.mean([q['c'] for q in Q],axis=0) if c is None else np.array(c)
        groups.append((np.linalg.norm(c-cp),Q,[x for x in (D or []) if np.linalg.norm(x['c']-cp)<np.linalg.norm(x['hc']-cp)]))
    for key,fn in (('A',state_A),('B',state_B),('C',state_C)):
        b,y,kw=fn(st); add(*person(key,b,y,t=st,**kw))
    b,y,kw=helper_state(TD,YD,st,(25.0,27.6)); add(*person('D',b,y,t=st,**kw))
    b,y,kw=helper_state(TE,YE,st,(25.2,28.0)); add(*person('E',b,y,t=st,**kw))
    if driver_visible(st): b,y,kw=state_F(st); add(*person('F',b,y,t=st,**kw))
    for q,d in walkers(st): add(q,d)
    hz=25.2<=st<50.6 and int(st*2.5)%2==0
    add(place(car_model(TAXI,TAXI_D,taxi=True,hazard=hz,brake=23.7<=st<51.0,door=taxi_door(st)),(taxi_x(st),0,-2.6),0.0,taxi_pitch(st)))
    for Q,p,yw,pt in traffic(st): add(place(Q,p,yw,pt))
    add(signal_heads(st)[:len(signal_heads(st))//2],c=(-2.1,1.5,-4.8)); add(signal_heads(st)[len(signal_heads(st))//2:],c=(2.1,1.5,4.8))
    groups.sort(key=lambda g:-g[0])
    layers=[CITY_B,CITY_G,CITY_O]
    for _,Q,D in groups: layers+=[Q,D]
    L=[((40,70,-50),(255,246,226),900.0)]
    img,vi=R.render(cam,layers,L,fov=fov,fog_start=14,fog_end=55,ambient=0.5)
    return post.ps1(img),vi,st
# ======================= HUD =======================
WHT=(240,240,240); YEL=(255,214,60); RED=(230,40,40); GRN=(60,230,90); GRY=(160,160,170)
def otext(d,s,x,y,col,sc=1):
    o=max(1,sc//2)
    for ox,oy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)): font.text(d,s,x+ox*o,y+oy*o,(0,0,0),sc,None)
    font.text(d,s,x,y,col,sc,None)
def ctext(d,s,y,col,sc=1): otext(d,s,(W-font.width(s,sc))//2,y,col,sc)
NARR=json.load(open(f'{TTS_DIR}/v6/script.json'))
HIL={'NPC..','ENTIRE','STREET.','NOBODY','BLOCKED','SIDE','QUEST.','STRANGER','NO.','EVERYTHING.','GREEN.','TAXI','REFUSED','MOVE.','STREET','ONE','TWO.','FOUR.','OUTNUMBERED.','WALKED','AWAY.','SIDEWALK.','TEAM.','ALONE.','IT.'}
def wrap(txt,n=27):
    out=[]; cur=''
    for w_ in txt.split():
        if len(cur)+len(w_)+(1 if cur else 0)>n: out.append(cur); cur=w_
        else: cur=(cur+' '+w_).strip()
    if cur: out.append(cur)
    return out
def subtitle(d,T):
    cur=None
    for key,t0,txt,dd,v in NARR:
        if t0<=T<t0+dd+0.2: cur=(key,txt)
    if not cur: return
    key,txt=cur; spk={'C1':'STRANGER: ','B1':'HIM: '}.get(key,'')
    lines=wrap((spk+txt).upper().replace('...','..'))
    y=270-11*(len(lines)-1)
    for ln in lines:
        xw=font.width(ln); x=(W-xw)//2; d.rectangle([x-3,y-2,x+xw+2,y+8],fill=(0,0,0)); cx=x
        for wd in ln.split(' '):
            col=(150,200,255) if wd in ('STRANGER:','HIM:') else (YEL if wd in HIL else WHT)
            otext(d,wd,cx,y,col,1); cx+=font.width(wd)+6
        y+=11
def diamond(d,x,y,col,r=4):
    d.polygon([(x,y-r),(x+r,y),(x,y+r),(x-r,y)],fill=col,outline=(0,0,0))
JOIN={'C':35.5,'D':37.2,'E':38.8,'F':38.8}
def hud(img,vi,T,st):
    d=ImageDraw.Draw(img)
    def proj(p): return R.project(tuple(p),vi)
    def head_of(key,fn):
        b,y,kw=fn(st); k=OUTFITS[key]['h']; return np.array(b)+np.array([0,1.95*k,0])
    # radar (simple): top-left
    if 4.8<=T<56.0:
        cx,cy,r=26,30,19; d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=(20,40,30),outline=(200,220,200))
        d.line([cx,cy-r,cx,cy+r],fill=(40,70,50)); d.line([cx-r,cy,cx+r,cy],fill=(40,70,50))
        a,_,_=state_A(st)
        for key,fn in (('B',state_B),('C',state_C),('D',lambda s:helper_state(TD,YD,s,(0,0))),('E',lambda s:helper_state(TE,YE,s,(0,0)))):
            p,_,_=fn(st); dx=(p[0]-a[0])*3.2; dz=(p[2]-a[2])*3.2
            if dx*dx+dz*dz<(r-3)**2:
                col=RED if key=='B' else (GRN if st>=JOIN.get(key,99) else (220,220,220))
                d.rectangle([cx+int(dx)-1,cy-int(dz)-1,cx+int(dx)+1,cy-int(dz)+1],fill=col)
        d.polygon([(cx,cy-3),(cx+2,cy+2),(cx-2,cy+2)],fill=WHT)
    # threat marker + warning (hook)
    if T<4.8:
        if 0.25<=T<3.6 and int(T*5)%2==0:
            s_='NPC THREAT DETECTED'; w=font.width(s_); d.rectangle([(W-w)//2-5,62,(W+w)//2+5,76],fill=(60,0,0),outline=RED); ctext(d,s_,66,(255,90,80))
        q=proj(head_of('B',state_B))
        if q: diamond(d,q[0],q[1],RED,5)
    if 8.6<=T<12.0:
        q=proj(head_of('B',state_B))
        if q: diamond(d,q[0],q[1],RED,4)
    # side quest
    if 18.6<=T<22.4:
        u=sm(seg01(T,18.6,18.85)); y=int(lerp(-30,58,u))
        d.rectangle([12,y,168,y+30],fill=(10,14,40),outline=YEL); ctext(d,'SIDE QUEST ACTIVATED:',y+5,YEL); ctext(d,'PROTECT THE STRANGER',y+17,WHT)
    if 27.2<=T<30.6 and int(T*4)%4!=0:
        s_='NEARBY PLAYERS ALERTED'; w=font.width(s_); d.rectangle([(W-w)//2-5,62,(W+w)//2+5,76],fill=(10,30,14),outline=GRN); ctext(d,s_,66,GRN)
    # teammates
    if 34.0<=T<47.6:
        for key,fn in (('C',state_C),('D',lambda s:helper_state(TD,YD,s,(0,0))),('E',lambda s:helper_state(TE,YE,s,(0,0))),('F',state_F)):
            if st>=JOIN[key]:
                q=proj(head_of(key,fn)); bob=int(2*math.sin(T*4+ord(key)))
                if q: diamond(d,q[0],q[1]+bob,GRN,4)
        n=1 if T<37.2 else (2 if T<38.8 else 4)
        if T>=35.5:
            d.rectangle([22,62,158,76],fill=(10,30,14),outline=GRN); x=30
            otext(d,'TEAMMATES:',x,66,WHT); x+=font.width('TEAMMATES:')+6
            for i,v in enumerate((1,2,4)):
                if (v==1) or (v==2 and T>=37.2) or (v==4 and T>=38.8):
                    if i>0: d.polygon([(x,67),(x+5,70),(x,73)],fill=GRN); x+=9
                    otext(d,str(v),x,66,GRN if v==n else GRY); x+=10
    # achievement
    if T>=56.0:
        u=sm(seg01(T,56.0,56.3)); y=int(lerp(-40,46,u))
        d.rectangle([8,y,172,y+30],fill=(16,16,20),outline=YEL)
        cx,cy=24,y+15; d.rectangle([cx-6,cy-7,cx+6,cy+1],fill=YEL); d.rectangle([cx-2,cy+1,cx+2,cy+5],fill=YEL); d.rectangle([cx-5,cy+5,cx+5,cy+7],fill=YEL)
        otext(d,'SECRET ACHIEVEMENT',36,y+6,YEL); otext(d,'UNLOCKED',36,y+17,WHT)
        if T>=56.9:
            ctext(d,'YOU WERE NEVER',92,WHT,2); ctext(d,'PLAYING ALONE.',112,GRN,2)
    subtitle(d,T)
    return img
def frame(T):
    img,vi,st=render(T)
    if 4.6<=T<4.8: img=Image.blend(img,Image.new('RGB',(W,H),(255,255,255)),seg01(T,4.6,4.8))
    return hud(img,vi,T,st)
TEST=os.environ.get('TEST')
if TEST:
    ims=[frame(float(x)) for x in TEST.split(',')]; sh=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): sh.paste(im,(i*182,0))
    sh.resize((sh.width*2,640),Image.NEAREST).save('test.png'); sys.exit()

if __name__=='__main__' and os.environ.get('PART') and os.environ['PART']!='audio':
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','20','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'wn_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.95,vignette=0.25,grain=1.6,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(post.upscale(frame(f/FPS),S),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=31); sr=s.sr; n=s.n; t=s.t; M=np.zeros(n)
    def note(buf,t0,m,d,v,wave='sq',duty=0.5,dec=3.0,att=0.005):
        f=440*2**((m-69)/12); tt=s.T(d); ph=(f*tt)%1
        x=np.where(ph<duty,1.0,-1.0) if wave=='sq' else (4*np.abs(ph-0.5)-1 if wave=='tri' else np.sin(2*np.pi*f*tt))
        env=np.minimum(1,tt/att)*np.exp(-tt*dec); i=int(t0*sr); j=min(n,i+len(tt)); buf[i:j]+=(x*env*v)[:j-i]
    def kick(t0,v=0.2): tt=s.T(0.16); i=int(t0*sr); j=min(n,i+len(tt)); M[i:j]+=(np.sin(2*np.pi*(110-60*tt/0.16)*tt)*np.exp(-tt*20)*v)[:j-i]
    def snare(t0,v=0.06,seed=0): x=s.filt_short(s.noise(0.14,seed),lo=1500,hi=7000)*np.exp(-s.T(0.14)*26); i=int(t0*sr); j=min(n,i+len(x)); M[i:j]+=(x*v)[:j-i]
    def hat(t0,v=0.02,seed=0): x=s.filt_short(s.noise(0.04,seed),lo=7000)*np.exp(-s.T(0.04)*90); i=int(t0*sr); j=min(n,i+len(x)); M[i:j]+=(x*v)[:j-i]
    def nb(t0,d,lo,hi,v,seed,shape=2,pan=0.0): s.place(s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v,pan)
    def tone(t0,f,d,v,dec=8,pan=0.0): tt=s.T(d); s.place(np.where((f*tt)%1<0.5,1.0,-1.0)*np.exp(-tt*dec)*np.minimum(1,tt/0.003),t0,v,pan)
    def step(t0,v=0.05,seed=0,pan=0.0): tt=s.T(0.09); s.place(s.filt_short(s.noise(0.09,seed),lo=200,hi=3000)*np.exp(-tt*55),t0,v,pan)
    def boom(t0,v=0.5,f=48): tt=s.T(1.4); s.place(np.sin(2*np.pi*f*tt*(1-0.25*tt/1.4))*np.exp(-tt*3.5)+s.filt_short(s.noise(1.4,int(t0*10)),hi=300)*np.exp(-tt*5)*0.5,t0,v)
    # ---------- city bed ----------
    rum=s.filt(s.rng.normal(0,1,n),lo=35,hi=260)*0.05; air=s.filt(s.rng.normal(0,1,n),lo=800,hi=5000)*0.006
    s.L+=rum+air; s.R+=np.roll(rum,1500)+np.roll(air,900)
    for k,tc in enumerate((6.5,14.0,33.0,41.0)): tone(tc,370 if k%2 else 415,0.35,0.012,dec=2,pan=0.7*(-1)**k)   # far horns
    for j in range(16): tc=0.3+j*3.7; nb(tc,1.6,200,2500,0.035,500+j,pan=-0.8+0.1*(j%16))                      # distant cars
    # ---------- crosswalk signal ticks ----------
    tc=4.9
    while tc<60:
        green=(tc<20.6) or (tc>=44.5); fl=20.6<=tc<22.8
        if green or fl: tone(tc,1800,0.025,0.012,dec=60)
        tc+=0.25 if fl else 0.9
        if 22.8<=tc<44.5: tc=44.5
    # ---------- music ----------
    # hook stab + pulse
    boom(0.0,0.28); [note(M,0.0,m,1.2,0.05,'sq',0.3,1.6) for m in (45,52,56)]
    for k in range(19): note(M,0.25*k,33 if k%4<3 else 36,0.22,0.07,'tri',dec=7); hat(0.25*k+0.125,0.02,k)
    # tension 4.8-18.2 (sparse), urgent 18.2-34
    bt=0.5
    for k in range(int((34-4.8)/bt)):
        tc=4.8+k*bt; urgent=tc>=18.2
        note(M,tc,[33,33,36,31][(k//4)%4],0.45,0.06 if urgent else 0.045,'tri',dec=4)
        if k%8==0: note(M,tc,57,bt*7,0.012,'sq',0.25,0.5,att=0.3); note(M,tc,60,bt*7,0.01,'sq',0.25,0.5,att=0.3)
        if urgent:
            if k%2==0: kick(tc,0.13)
            if k%4==2: snare(tc,0.04,k)
            hat(tc+0.25,0.016,k)
    # team build 34-46: rising, major lift
    prog=[(41,53,57,60),(43,55,59,62),(45,57,60,64),(48,55,60,64)]
    for k in range(24):
        tc=34.0+k*0.5; c=prog[min(3,k//6)]
        note(M,tc,c[0],0.45,0.07,'tri',dec=3)
        if k%2==0:
            for m in c[1:]: note(M,tc,m,0.95,0.012,'sq',0.25,1.5,att=0.05)
        kick(tc,0.12 if k%2==0 else 0.0)
        if k%2==1: snare(tc,0.035,k)
    for k in range(10): snare(38.3+k*0.05,0.02+0.003*k,200+k)
    M[int(39.4*sr):int(39.9*sr)]*=np.linspace(1,0.2,int(0.5*sr))
    note(M,39.4,76,0.5,0.03,'sq',0.25,4); note(M,39.42,71,0.5,0.02,'sq',0.25,4)
    # emotional 45.6-60: slow warm chords + simple melody
    warm=[(41,57,60,65),(48,55,60,64),(45,57,60,64),(46,58,62,65),(41,57,60,65),(48,55,60,67)]
    for k,c in enumerate(warm):
        tc=45.6+k*2.0
        note(M,tc,c[0],2.0,0.06,'tri',dec=0.8,att=0.05)
        for m in c[1:]: note(M,tc,m,2.0,0.016,'tri',dec=0.6,att=0.3)
    for k,(m,d_) in enumerate([(72,1.0),(74,0.5),(76,0.5),(77,1.5),(76,0.5),(72,1.0),(74,1.0),(69,2.0),(72,1.0),(76,1.0),(77,1.0),(79,2.0)]):
        tc=46.6+sum(x[1] for x in [(72,1.0),(74,0.5),(76,0.5),(77,1.5),(76,0.5),(72,1.0),(74,1.0),(69,2.0),(72,1.0),(76,1.0),(77,1.0),(79,2.0)][:k])
        if tc<56: note(M,tc,m,d_*0.95,0.022,'sq',0.25,1.2,att=0.02)
    # achievement
    for k,m in enumerate((72,76,79,84,88)): note(M,56.0+k*0.08,m,0.5,0.08,'sq',0.25,4)
    note(M,56.0,60,3.5,0.11,"tri",dec=0.6); note(M,56.0,67,3.5,0.06,'tri',dec=0.9)
    for k in range(6): note(M,56.5+k*0.12,96-k,0.25,0.012,'sin',dec=6)
    # ---------- sfx ----------
    tt=s.T(1.6); scr=s.filt_short(s.noise(1.6,7),lo=2200,hi=4200)*np.sin(np.pi*tt/1.6)**0.4+np.sin(2*np.pi*np.cumsum(2600+300*np.sin(2*np.pi*13*tt))/sr)*0.4*np.exp(-tt*1.2)
    s.place(scr,0.05,0.06,-0.4)                                                        # hook: taxi brakes behind them
    s.place(scr[:int(1.2*sr)],23.7,0.11,-0.5)                                          # the real stop
    tt=s.T(2.3); s.place(s.filt_short(np.where((np.cumsum(np.full(len(tt),60+30*0))/sr*1)%1<0.5,1.0,-1.0)*(tt/2.3),hi=500),21.4,0.05,-0.6)   # taxi engine approaching
    for tc,d_ in ((25.3,0.18),(25.55,0.45)):                                           # horn
        tone(tc,350,d_,0.05,dec=0.5,pan=-0.4); tone(tc,440,d_,0.04,dec=0.5,pan=-0.4)
    tc=25.2
    while tc<50.6: tone(tc,900,0.012,0.008,dec=200,pan=-0.4); tc+=0.4                   # hazard relay
    for tc in (27.7,48.95): nb(tc,0.15,300,3000,0.06,int(tc*7),pan=-0.4)               # door open
    for tc in (29.3,49.7): s.thud(tc,90,0.12)                                          # door close
    nb(50.8,3.0,60,600,0.06,701,shape=1,pan=0.3)                                       # taxi leaves
    for j in range(6): te=24.5+j*2.9+46/9; nb(te-0.5,1.0,150,3000,0.05,800+j,pan=0.0)   # north-lane cars pass
    nb(22.8,2.0,60,500,0.05,820)                                                       # queue pulls away
    nb(18.18,0.22,400,4000,0.08,900); s.thud(18.27,80,0.12)                           # the push (no impact gore)
    tone(18.6,523,0.08,0.03); tone(18.68,659,0.08,0.03); tone(18.76,784,0.08,0.03); tone(18.84,1047,0.2,0.035,dec=4)   # quest start
    tone(27.2,880,0.08,0.03); tone(27.32,1175,0.12,0.03)                               # alert
    for tc,f in ((35.5,784),(37.2,988),(38.8,1175)): tone(tc,f,0.07,0.03); tone(tc+0.08,f*1.5,0.1,0.03)
    # footsteps from the tracks
    for tr,v in ((TA,0.03),(TB,0.04),(TC,0.035),(TD,0.035),(TE,0.035),(TF,0.03)):
        last=None
        for f in range(0,6000):
            tm=f/100; p,ph,mv=tr.at(tm); kk=int(ph/math.pi) if mv else None
            if kk is not None and last is not None and kk!=last: step(tm,v,int(tm*100)%997)
            last=kk if mv else last
    # ---------- voices ----------
    NB=np.zeros(n); duck=np.ones(n)
    for key,t0,txt,dd,v in NARR:
        a,ar=_sf.read(f'{TTS_DIR}/v6/{key}.wav'); a=a if a.ndim==1 else a.mean(1)
        a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a)
        if key in ('C1','B1'): a=a*1.05
        i=int(t0*sr); j=min(n,i+len(a)); NB[i:j]+=a[:j-i]
        duck[max(0,i-int(0.08*sr)):min(n,j+int(0.15*sr))]=0.45
    duck=np.convolve(duck,np.ones(2400)/2400,'same')
    s.L+=M*duck; s.R+=M*duck
    s.reverb(0.12,length=0.9,decay=5)
    pk=max(np.abs(s.L).max(),np.abs(s.R).max()); g=pk*1.0/np.abs(NB).max()
    s.L=s.L*(0.6+0.4*duck)+NB*g; s.R=s.R*(0.6+0.4*duck)+NB*g
    return s.save(path,peak=0.9)
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'wrong_npc.wav'))); sys.exit()
