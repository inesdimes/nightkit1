"""THE T-REX SIZE MYSTERY - 60 s PS1 comedy, 9:16. Fully procedural (nightkit).
TEST=t1,t2 python examples/trex_size.py | PART=a:b | PART=audio"""
import os, sys, math, json
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, box, quad, tiled_plane, transform
from nightkit import motion, post, font
from nightkit.audio import Sound
for ch,rows in {'?':['01110','10001','00001','00110','00100','00000','00100'],'!':['00100','00100','00100','00100','00100','00000','00100'],
                '+':['00000','00100','00100','11111','00100','00100','00000'],'%':['11001','11010','00010','00100','01000','01011','10011']}.items():
    font.FONT.setdefault(ch,rows)
OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6; DUR=63.5; N=int(DUR*FPS)
HOOK_LEN=9.0; SHIFT=4.0          # new slow hook (0-9 s), the rest of the story is the old timeline +4 s
def story_t(V): return V-HOOK_LEN if V<HOOK_LEN else V-SHIFT
sm=motion.smooth
def seg01(t,a,b): return max(0.0,min(1.0,(t-a)/(b-a)))
def win(t,a,b,ra=0.2,rb=0.2): return sm(seg01(t,a,a+ra))*(1-sm(seg01(t,b-rb,b)))
def lerp(a,b,u): return a+(b-a)*u
def lerp3(a,b,u): return tuple(a[i]+(b[i]-a[i])*u for i in range(len(a)))
def Rx(a): c,s=math.cos(a),math.sin(a); return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def Ry(a): c,s=math.cos(a),math.sin(a); return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def Rz(a): c,s=math.cos(a),math.sin(a); return np.array([[c,-s,0],[s,c,0],[0,0,1]])
PI=math.pi
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
def tagD(D,hc):
    for q in D: q['hc']=np.array(hc,float)
    return D
# ======================= T-REX (one model) =======================
HAND={}
OLIVE=(112,128,58); OLIVE_D=(86,100,44); BELLY=(176,172,112); BROW=(72,44,26); TOOTH=(240,236,220); MOUTH=(110,30,34)
def trex(base,yaw,t=0.0,lean=0.0,neck=0.0,hy=0.0,jaw=0.0,brow=0.0,brow_up=0.0,eye=1.0,look=(0.0,0.0),rh=None,lh=None,walk=0.0,tail=0.0):
    """faces -z at yaw 0. brow: +1 angry (inner ends down), -1 sad. brow_up raises them. rh/lh: tiny-arm hand targets (local)."""
    b=np.array(base,float); Rb=Ry(yaw); hip=np.array([0,2.0,0.1])
    def WB(p): p=np.array(p,float); return tuple(b+Rb@(hip+Rx(-lean)@(p-hip)))
    npv=np.array([0,2.95,-1.6])
    def WH(p): p=np.array(p,float); return WB(npv+Ry(hy)@Rx(-neck)@(p-npv))
    jp=np.array([0,2.78,-1.75])
    def WJ(p): p=np.array(p,float); return WH(jp+Rx(-0.55*jaw)@(p-jp))
    Q=[];D=[]
    # legs
    for sx,ph in ((-1,1),(1,-1)):
        a=0.35*ph*math.sin(walk); hp_=np.array([sx*0.48,2.0,0.1])
        kn=hp_+np.array([sx*0.04,-0.9*math.cos(a),-0.35-0.9*math.sin(a)]); an=kn+np.array([0,-0.75,0.45]); an[1]=max(0.32,an[1]); ft=np.array([an[0],0.0,an[2]-0.25])
        Q+=seg(tuple(b+Rb@hp_),tuple(b+Rb@kn),0.5,OLIVE)+seg(tuple(b+Rb@kn),tuple(b+Rb@an),0.32,OLIVE_D)
        Q+=obox(tuple(b+Rb@(ft+np.array([0,0.12,0]))),(0.22,0.12,0.38),Rb,OLIVE_D)
        for k in (-1,0,1): Q+=obox(tuple(b+Rb@(ft+np.array([k*0.12,0.06,-0.42]))),(0.04,0.04,0.06),Rb,TOOTH)
    # body, belly, neck
    Q+=transform(seg((0,2.05,0.5),(0,2.5,-1.25),1.0,OLIVE,depth=1.05),WB)
    Q+=transform(seg((0,1.72,0.25),(0,2.12,-1.15),0.7,BELLY,depth=0.25),WB)
    Q+=transform(seg((0,2.45,-1.1),(0,2.95,-1.62),0.62,OLIVE),WB)
    for k in range(5): D+=transform(box(-0.04,0.04,2.58-0.02*k,2.66-0.02*k,0.2-0.32*k,0.38-0.32*k,OLIVE_D),WB)   # back ridges
    # tail
    pts=[(0,2.15,0.5),(0.2*math.sin(tail),2.0,1.4),(0.45*math.sin(tail),1.8,2.3),(0.75*math.sin(tail+0.4),1.55,3.2),(1.0*math.sin(tail+0.8),1.35,3.9)]
    for i in range(4): Q+=transform(seg(pts[i],pts[i+1],0.82-0.18*i,OLIVE if i%2==0 else OLIVE_D),WB)
    # tiny arms
    for sx,hd in ((-1,rh),(1,lh)):
        sh=np.array([sx*0.36,2.25,-1.15]); hd=np.array(hd if hd is not None else (sx*0.36,1.95,-1.48))
        el=sh+np.array([sx*0.06,-0.22,-0.05]) if np.linalg.norm(hd-sh)<0.5 else (sh+hd)/2
        Q+=transform(seg(sh,el,0.12,OLIVE_D)+seg(el,hd,0.1,OLIVE_D),WB)
        if sx<0: HAND['r']=np.array(WB(hd))
        for k in (-1,1): Q+=transform(seg(hd,hd+np.array([k*0.03,-0.06,-0.08]),0.035,TOOTH),WB)
    HAND['head']=np.array(WH((0,3.1,-2.0)))
    # head: skull + snout + jaw
    Q+=transform(box(-0.38,0.38,2.78,3.32,-2.2,-1.45,OLIVE),WH)
    Q+=transform(box(-0.3,0.3,2.78,3.12,-2.85,-2.2,OLIVE),WH)
    Q+=transform(box(-0.33,0.33,2.5,2.78,-2.75,-1.6,OLIVE_D),WJ)+transform(box(-0.25,0.25,2.74,2.79,-2.7,-1.7,MOUTH),WJ)
    for k in range(6):
        z=-2.78+0.18*k
        for sx in (-1,1):
            D+=transform(box(sx*0.27-0.03,sx*0.27+0.03,2.68,2.78,z-0.03,z+0.03,TOOTH),WH)
            D+=transform(box(sx*0.27-0.03,sx*0.27+0.03,2.78,2.86,z-0.03,z+0.03,TOOTH),WJ)
    # nostrils
    for sx in (-1,1): D+=transform(box(sx*0.12-0.035,sx*0.12+0.035,3.04,3.08,-2.86,-2.85,(30,30,20)),WH)
    # cartoon eyes on the brow ridge + the EYEBROWS (big, bushy, setup for the punchline)
    Q+=transform(box(-0.4,0.4,3.22,3.4,-2.2,-1.6,OLIVE),WH)
    for sx in (-1,1):
        eh=0.13*eye; ez=-1.92; ey=3.2
        D+=transform(box(sx*0.4,sx*0.415,ey-eh,ey+eh,ez-0.13,ez+0.13,(250,250,244)),WH)       # eye on the side of the head
        D+=transform(box(sx*0.415,sx*0.425,ey-min(0.06,eh)+0.05*look[1],ey+min(0.06,eh)+0.05*look[1],ez-0.06-0.07*look[0],ez+0.06-0.07*look[0],(14,14,16)),WH)
        D+=transform(box(-0.36+0.42*(sx>0),-0.06+0.42*(sx>0),3.08,3.32,-2.205,-2.2,(250,250,244)) if False else [],WH)
        # EYEBROWS: huge, bushy, over each eye, angle = mood
        ang=sx*0.4*brow; by=3.44+0.1*brow_up
        def WBr(p,sx=sx,ang=ang,by=by): p=np.array(p,float); q=np.array([sx*0.36,by,-1.92])+Rx(ang*sx*0)@Ry(0)@p; q=np.array([sx*0.36,by,-1.92])+np.array([[1,0,0],[0,math.cos(ang),-math.sin(ang)],[0,math.sin(ang),math.cos(ang)]])@p; return WH(q)
        Q+=transform(box(-0.12,0.16,-0.09,0.09,-0.4,0.36,BROW),WBr)
        for k in (-1,0,1): Q+=transform(box(-0.1,0.13,0.08,0.16,k*0.24-0.09,k*0.24+0.09,BROW),WBr)
    hcW=np.array(WH((0,3.05,-2.1))); bcW=np.array(WB((0,2.2,-0.6)))
    for q in D: q['hc']=hcW if q['c'][1]>2.6 else bcW
    return Q,D
# ======================= SCIENTIST =======================
COAT=(236,238,240); COAT_D=(200,204,210); PANTS=(54,76,150); SKIN=(232,192,160); HAIR=(108,68,38)
def doc(base,yaw,t=0.0,walk=0.0,rh=None,lh=None,lean=0.0,hy=0.0,hp=0.0,eye=1.0,brow=0.0,mouth=0.0,sweat=0.0,nod=0.0):
    b=np.array(base,float); Rb=Ry(yaw)
    def W(p): return tuple(b+Rb@np.array(p,float))
    hip=0.86
    def WL(p): p=np.array(p,float); piv=np.array([0,hip,0]); return W(piv+Rx(-lean)@(p-piv))
    Q=[];D=[]; sw=0.42*math.sin(walk)
    for sx,ph in ((-1,1),(1,-1)):
        hp_=np.array([sx*0.08,hip,0]); a=ph*sw; ft=hp_+np.array([0,-0.82*math.cos(a),-0.82*math.sin(a)]); ft[1]=max(0.05,ft[1]); kn=(hp_+ft)/2+np.array([0,0,-0.04])
        Q+=transform(seg(hp_,kn,0.11,PANTS)+seg(kn,ft,0.1,PANTS)+box(ft[0]-0.05,ft[0]+0.05,ft[1]-0.05,ft[1]+0.03,ft[2]-0.12,ft[2]+0.05,(50,40,34)),W)
    Q+=box(-0.16,0.16,0.84,1.36,-0.1,0.1,COAT,xf=WL)+box(-0.18,0.18,0.5,0.9,-0.115,0.115,COAT,xf=WL)
    D+=box(-0.02,0.02,0.5,1.3,-0.118,-0.112,COAT_D,xf=WL)+box(-0.07,0.07,1.2,1.36,-0.118,-0.11,(120,170,220),xf=WL)   # coat seam + shirt
    D+=box(0.07,0.13,1.12,1.2,-0.12,-0.115,(60,80,200),xf=WL)                                                            # pen in pocket
    hc=np.array([0,1.52,0]); n_=0.3*math.sin(nod*PI*2)*(nod>0)
    def WH(p): p=np.array(p,float); return WL(hc+Ry(hy)@Rx(hp+n_)@(p-hc))
    Q+=box(-0.045,0.045,1.34,1.42,-0.045,0.045,SKIN,xf=WL)+box(-0.1,0.1,1.4,1.64,-0.11,0.1,SKIN,xf=WH)
    Q+=box(-0.16,0.16,1.6,1.84,-0.14,0.15,HAIR,xf=WH)+box(-0.14,0.14,1.46,1.62,0.06,0.16,HAIR,xf=WH)+box(-0.17,-0.1,1.48,1.7,-0.08,0.12,HAIR,xf=WH)+box(0.1,0.17,1.48,1.7,-0.08,0.12,HAIR,xf=WH)
    for sx in (-1,1):                                                        # round-ish glasses + eyes
        x=sx*0.048
        for (x0,x1,y0,y1) in ((x-0.04,x+0.04,1.555,1.565),(x-0.04,x+0.04,1.485,1.495),(x-0.045,x-0.035,1.49,1.56),(x+0.035,x+0.045,1.49,1.56)):
            D+=box(x0,x1,y0,y1,-0.122,-0.116,(20,20,24),xf=WH)
        e=0.013*eye; D+=box(x-0.012,x+0.012,1.525-e,1.525+e,-0.12,-0.112,(24,20,22),xf=WH)
        by=1.585+0.012*(eye-1); bt=brow
        D+=transform(seg((x-sx*0.03,by+0.008*bt,-0.116),(x+sx*0.025,by-0.01*bt,-0.116),0.012,HAIR,depth=0.004),WH)
    D+=box(-0.04,0.04,1.52,1.53,-0.122,-0.116,(20,20,24),xf=WH)
    mh=0.008+0.035*mouth; D+=box(-0.025+0.008*mouth,0.025-0.008*mouth,1.445-mh/2,1.445+mh/2,-0.118,-0.11,(120,50,50),xf=WH)
    if sweat>0:
        for k,(sx,yy) in enumerate(((1,1.6),(-1,1.56))):
            D+=box(sx*0.1-0.012+sx*0.004,sx*0.1+0.012+sx*0.004,yy-0.04*sweat,yy,-0.09,-0.06,(140,200,255),xf=WH)
    for sx,hd in ((-1,rh),(1,lh)):
        if hd is None: s_=-sx*0.3*math.sin(walk)*(1 if walk else 0); hd=(sx*0.22,0.86,-0.3*s_-0.05)
        sh=np.array(WL((sx*0.22,1.3,0))); hw=np.array(WL(hd)); el=elbow(sh,hw,tuple(Rb@np.array([sx*0.6,0,-0.15])),0.56)
        Q+=seg(sh,el,0.095,COAT)+seg(el,hw,0.085,COAT)+obox(hw,(0.04,0.045,0.04),Rb,SKIN)
    hcW=np.array(WH((0,1.52,0))); tcW=np.array(WL((0,1.1,0)))
    for q in D: q['hc']=hcW if q['c'][1]>hcW[1]-0.14 else tcW
    return Q,D
# ======================= BIRD + CROC =======================
PIGEON=(138,140,152); PIGEON_D=(96,100,116); BEAK=(240,160,40); CROC=(72,112,62); CROC_D=(52,84,44); CROC_B=(180,176,120)
def bird(base,yaw,t=0.0,hop=0.0,bob=0.0,beak=0.0,flap=0.0,s=1.6):
    b=np.array(base,float); Rb=Ry(yaw)
    def W(p): return tuple(b+Rb@(np.array(p,float)*s)+np.array([0,hop,0]))
    Q=[];D=[]
    Q+=box(-0.11,0.11,0.12,0.34,-0.14,0.16,PIGEON,xf=W)+box(-0.08,0.08,0.18,0.3,0.16,0.3,PIGEON_D,xf=W)
    hz=-0.17-0.05*bob
    def WH(p): p=np.array(p,float); return W(p+np.array([0,0,hz]))
    Q+=box(-0.07,0.07,0.32,0.46,-0.06,0.07,PIGEON_D,xf=WH)
    Q+=box(-0.025,0.025,0.37,0.4,-0.13,-0.06,BEAK,xf=WH)+box(-0.02,0.02,0.34-0.03*beak,0.37-0.03*beak,-0.12,-0.06,BEAK,xf=WH)
    for sx in (-1,1):
        D+=box(sx*0.07-0.002,sx*0.07+0.004*sx,0.41,0.43,-0.03,-0.0,(250,250,250),xf=WH)
        D+=box(sx*0.071-0.002,sx*0.071+0.006*sx,0.415,0.427,-0.025,-0.012,(10,10,10),xf=WH)
        a=0.9*flap*math.sin(t*40)
        def WW(p,sx=sx,a=a): p=np.array(p,float); q=np.array([sx*0.11,0.3,0])+Rz(sx*a)@p; return W(q)
        Q+=transform(box(min(0,sx*0.02),max(0,sx*0.02),-0.12,0.02,-0.1,0.14,PIGEON_D),WW)
        Q+=transform(seg((sx*0.04,0.13,0),(sx*0.04,0.0,-0.02),0.025,BEAK),W)
    hcW=np.array(WH((0,0.4,0)))
    return Q,tagD(D,hcW)
def croc(base,yaw,t=0.0,walk=0.0,jaw=0.0,lid=0.5,tail=0.0):
    b=np.array(base,float); Rb=Ry(yaw)
    def W(p): return tuple(b+Rb@np.array(p,float))
    jp=np.array([0,0.28,-0.75])
    def WJ(p): p=np.array(p,float); return W(jp+Rx(-0.5*jaw)@(p-jp))
    Q=[];D=[]
    Q+=box(-0.32,0.32,0.12,0.42,-0.75,0.6,CROC,xf=W)+box(-0.3,0.3,0.1,0.14,-0.72,0.58,CROC_B,xf=W)
    Q+=box(-0.22,0.22,0.28,0.42,-1.6,-0.75,CROC,xf=W)                                        # upper snout
    Q+=box(-0.2,0.2,0.16,0.28,-1.55,-0.75,CROC_D,xf=WJ)                                  # lower jaw
    for k in range(6):
        z=-1.5+0.13*k
        for sx in (-1,1): D+=box(sx*0.2-0.02,sx*0.2+0.02,0.24,0.3,z-0.02,z+0.02,TOOTH,xf=W)
    for sx in (-1,1):
        Q+=box(sx*0.14-0.08,sx*0.14+0.08,0.42,0.54,-0.88,-0.7,CROC,xf=W)
        D+=box(sx*0.14-0.06,sx*0.14+0.06,0.44,0.52,-0.884,-0.88,(230,210,90),xf=W)
        D+=box(sx*0.14-0.015,sx*0.14+0.015,0.44,0.52,-0.89,-0.884,(10,10,10),xf=W)
        D+=box(sx*0.14-0.065,sx*0.14+0.065,0.52-0.08*lid,0.53,-0.892,-0.886,CROC_D,xf=W)        # deadpan eyelids
    for k in range(6): D+=box(-0.2,0.2,0.42,0.46,-0.6+0.2*k,-0.5+0.2*k,CROC_D,xf=W)
    pts=[(0,0.3,0.6),(0.15*math.sin(tail),0.26,1.2),(0.35*math.sin(tail+0.5),0.2,1.8),(0.55*math.sin(tail+1.0),0.14,2.3)]
    for i in range(3): Q+=transform(seg(pts[i],pts[i+1],0.5-0.14*i,CROC,depth=0.24-0.05*i),W)
    for sx in (-1,1):
        for zz,ph in ((-0.5,1),(0.4,-1)):
            a=0.3*ph*sx*math.sin(walk); hip=np.array([sx*0.3,0.25,zz]); ft=hip+np.array([sx*0.25,-0.22,-0.15*math.sin(a)-0.1])
            Q+=transform(seg(hip,ft,0.12,CROC_D),W)
    hcW=np.array(W((0,0.4,-0.5)))
    return Q,tagD(D,hcW)
# ======================= LAB SET =======================
TILE=lambda i,j:[(196,204,200),(150,166,164)][(i+j)%2]
DESK=(120,96,70); BEIGE=(206,196,170); BEIGE_D=(170,160,136)
X0,X1,Z0,Z1,YC=-9.0,4.2,-4.0,5.0,5.2
def lab():
    F=tiled_plane(X0,X1,Z0,Z1,0,0.7,TILE)
    Wq=[]
    wall=lambda i,j:[(176,196,186),(168,188,178)][(i+j)%2]
    def vz(z,x0,x1,hole=None):
        Q=[]
        for i,x in enumerate(np.arange(x0,x1,1.0)):
            for j,y in enumerate(np.arange(0,YC,1.0)):
                xa,xb,ya,yb=x,min(x1,x+1),y,min(YC,y+1)
                if hole and xa>=hole[0]-1e-6 and xb<=hole[1]+1e-6 and yb<=hole[2]+1e-6: continue
                Q.append(quad([(xa,ya,z),(xb,ya,z),(xb,yb,z),(xa,yb,z)],wall(i,j)))
        return Q
    def vx(x,z0,z1):
        return [quad([(x,y,z),(x,y,min(z1,z+1)),(x,min(YC,y+1),min(z1,z+1)),(x,min(YC,y+1),z)],wall(i,j)) for i,z in enumerate(np.arange(z0,z1,1.0)) for j,y in enumerate(np.arange(0,YC,1.0))]
    Wq+=vz(Z0,X0,X1)+vz(Z1,X0,X1,hole=(-0.5,1.5,2.0))+vx(X0,Z0,Z1)+vx(X1,Z0,Z1)
    Wq+=tiled_plane(X0,X1,Z0,Z1,YC,1.0,lambda i,j:(214,218,214))
    for x in (-7.5,-4.5,-1.5,1.5):
        for z in (-2.0,2.5): Wq.append(quad([(x,YC-0.01,z),(x+1.6,YC-0.01,z),(x+1.6,YC-0.01,z+0.5),(x,YC-0.01,z+0.5)],(250,252,240),emit=True))
    P=[]
    # wall stripe + posters (dino skeleton silhouette, evolution tree)
    P+=box(X0,X1,1.0,1.12,Z0+0.01,Z0+0.03,(60,120,110))
    P+=box(-3.6,-1.4,2.0,3.6,Z0+0.02,Z0+0.04,(236,230,206))
    for (a,b_) in (((-3.3,2.6),(-2.2,2.9)),((-2.2,2.9),(-1.8,3.3)),((-1.8,3.3),(-1.6,3.1)),((-2.6,2.75),(-2.7,2.2)),((-2.1,2.85),(-2.0,2.2))):
        P+=seg((a[0],a[1],Z0+0.05),(b_[0],b_[1],Z0+0.05),0.06,(80,70,60),depth=0.01)
    # door (opens at 24.6 for the relatives)
    # desk + CRT + keyboard + mouse pad
    P+=box(1.2,2.7,0.7,0.78,-0.5,0.7,DESK)
    for (x,z) in ((1.25,-0.45),(2.65,-0.45),(1.25,0.65),(2.65,0.65)): P+=box(x-0.04,x+0.04,0,0.7,z-0.04,z+0.04,(70,70,76))
    P+=box(2.0,2.62,0.78,1.36,-0.2,0.42,BEIGE)+box(2.3,2.62,0.86,1.28,-0.12,0.34,BEIGE_D)+box(2.05,2.45,0.78,0.84,-0.1,0.32,BEIGE_D)
    P+=box(1.48,1.72,0.78,0.81,-0.15,0.35,BEIGE)
    # tall lab cabinet (the T-Rex slams it)
    P+=box(-1.55,-0.8,0,1.22,-0.55,0.25,(150,150,160))+box(-1.6,-0.75,1.22,1.27,-0.6,0.3,(110,110,120))
    # fossil table with bones
    P+=box(0.3,2.1,0.7,0.78,-3.4,-2.5,DESK)
    for (x,z) in ((0.35,-3.35),(2.05,-3.35),(0.35,-2.55),(2.05,-2.55)): P+=box(x-0.04,x+0.04,0,0.7,z-0.04,z+0.04,(70,70,76))
    # shelf with jars (back-left)
    P+=box(-8.95,-8.6,0,2.4,1.2,3.4,(120,96,70))
    for k,c in enumerate(((120,200,120),(200,180,90),(160,120,200),(120,190,210))): P+=box(-8.85,-8.65,1.6,1.9,1.4+0.5*k,1.7+0.5*k,c)
    return F,Wq,P
LAB_F,LAB_W,LAB_P=lab()
BONE=(232,224,196)
def beakers(t):
    j=0.12*max(0,math.sin((t-21.4)*PI/0.35))*(21.4<=t<21.75)
    Q=[]
    for k,(x,z,c) in enumerate(((-1.4,-0.35,(120,220,140)),(-1.15,-0.1,(220,120,200)),(-0.95,-0.4,(120,180,240)))):
        jj=j*(1+0.4*k); Q+=box(x-0.06,x+0.06,1.27+jj,1.45+jj,z-0.06,z+0.06,c)+box(x-0.03,x+0.03,1.45+jj,1.52+jj,z-0.03,z+0.03,(200,220,220))
    return Q
def bones(t):
    """fossils on the table; the doc flips through them 15.2-20.6"""
    Q=[]; jit=lambda k:0.06*max(0,math.sin(t*9+k*1.7))*win(t,15.4,20.6,0.2,0.2)
    Q+=seg((0.5,0.82+jit(0),-3.1),(1.2,0.84+jit(0),-2.8),0.07,BONE)+box(0.45,0.58,0.79+jit(0),0.9+jit(0),-3.15,-3.02,BONE)+box(1.14,1.27,0.79+jit(0),0.9+jit(0),-2.86,-2.72,BONE)
    Q+=box(1.4,1.8,0.79+jit(1),1.0+jit(1),-3.2,-2.85,BONE)+box(1.43,1.77,0.79+jit(1),0.83+jit(1),-3.3,-3.2,BONE)
    for k in range(4): Q+=box(0.6+0.12*k,0.66+0.12*k,0.79,0.84+jit(2+k),-2.75,-2.6,BONE)
    return Q
def door(open_k):
    a=1.6*open_k
    def Tf(p): p=np.array(p,float)-np.array([-0.5,0,Z1]); return tuple(Ry(a)@p+np.array([-0.5,0,Z1]))
    Q=transform(box(-0.5,1.5,0,2.0,Z1-0.03,Z1+0.03,(150,120,90))+box(1.25,1.35,0.95,1.05,Z1-0.06,Z1-0.03,(200,200,90)),Tf)
    Q.append(quad([(-0.5,0,Z1+0.6),(1.5,0,Z1+0.6),(1.5,2.0,Z1+0.6),(-0.5,2.0,Z1+0.6)],(60,64,70)))
    return Q
def mouse(t):
    p=np.array([1.4,0.8,0.62])
    if t>=44.5 and 'r' in HAND: h=HAND['r']; p=np.array([h[0],0.8,h[2]])
    return box(p[0]-0.05,p[0]+0.05,0.78,0.82,p[2]-0.07,p[2]+0.07,(220,220,212))
def alarm_light(t):
    on=46.9<=t<51.0; Q=box(-0.15,0.15,4.4,4.7,Z0+0.01,Z0+0.2,(80,30,30))
    a=t*8
    if on: Q+=[quad([(0.2*math.cos(a),4.55,Z0+0.2),(0.2*math.cos(a)+0.6*math.cos(a),4.55+0.3,Z0+0.2+0.6*math.sin(a)),(0.2*math.cos(a)+0.6*math.cos(a),4.55-0.3,Z0+0.2+0.6*math.sin(a))],(255,60,40),emit=True)]
    Q+=box(-0.1,0.1,4.48,4.62,Z0+0.2,Z0+0.3,(255,50,40) if on else (120,40,40),emit=on)
    return Q
# ======================= STORY STATE =======================
TREX_HOME=(-2.6,0.0,0.75); TREX_GRAB=(0.14,0.0,0.95); TREX_YAW=-PI/2
def trex_base(t):
    u=sm(seg01(t,43.0,44.2))*(1-sm(seg01(t,51.0,51.8))); mv=(43.0<t<44.2) or (51.0<t<51.8)
    return lerp3(TREX_HOME,TREX_GRAB,u),t*7*mv
DOC_SIDE=(0.95,0.0,-0.75)
DOC_DESK=(1.0,0.0,0.15); DOC_TABLE=(1.2,0.0,-2.15)
def talk(t,a,b,sp=24): return (0.5+0.5*math.sin(t*sp))*win(t,a,b,0.05,0.05)
SCRIPT=json.load(open('/home/claude/tts/v7/script.json'))
def line_on(key,t):
    for k,t0,txt,d in SCRIPT:
        if k==key: return t0<=t<t0+d
    return False
def T_line(t):
    for k,t0,txt,d in SCRIPT:
        if k[0]=='T' and t0<=t<t0+d: return True
    return False
def trex_state(t):
    kw=dict(lean=0.0,neck=0.0,hy=0.0,jaw=0.0,brow=0.3,brow_up=0.0,eye=1.0,look=(0,0),tail=0.15*math.sin(t*1.3))
    if T_line(t): kw['jaw']=0.25+0.55*(0.5+0.5*math.sin(t*19))
    # hook: head swoops down to the doc
    if t<0:                                                            # NEW HOOK: the head slowly lowers behind the doc
        u=sm(seg01(t,-9.0,-6.6)); kw['lean']=0.36*u; kw['neck']=0.3*u; kw['brow']=0.0; kw['brow_up']=0.5; kw['eye']=1.15
        if -7.7<=t<-7.5: kw['eye']=0.15                                # blink
        if t>=-5.5: kw['brow']=1.1; kw['brow_up']=0.0; kw['eye']=1.3
        if t>=-2.0: kw['look']=(sm(seg01(t,-2.0,-1.3)),-0.8*sm(seg01(t,-2.0,-1.3))); kw['brow']=0.6
    elif t<11.0: kw['brow']=0.0; kw['brow_up']=0.4*math.sin(t*2.0)
    elif t<15.0:                                                       # stares, brows sink into rage
        u=sm(seg01(t,11.0,12.2)); kw['brow']=lerp(0.0,1.2,u); kw['brow_up']=-0.4*u; kw['lean']=0.25*sm(seg01(t,12.6,13.3)); kw['neck']=0.25*sm(seg01(t,12.6,13.3)); kw['eye']=lerp(1.0,0.75,u)
    elif t<21.0: kw['hy']=-0.35; kw['brow']=0.8; kw['look']=(-0.6,-0.6)
    elif t<24.5:                                                       # slams the desk
        u=sm(seg01(t,21.0,21.4)); kw['lean']=0.4*u; kw['neck']=0.2*u; kw['rh']=lerp3((-0.36,1.95,-1.48),(-0.5,1.95,-1.55),u); kw['brow']=1.2; kw['eye']=1.2
    elif t<38.4: kw['brow']=0.2; kw['hy']=0.35*win(t,24.6,29.5,0.4,0.4); kw['look']=(0,-0.8) if 30<t<37 else (0,0)
    elif t<40.0: u=sm(seg01(t,38.4,39.0)); kw['brow']=-1.2*u; kw['brow_up']=0.3*u; kw['neck']=0.3*u; kw['eye']=lerp(1.0,0.7,u)    # disappointed
    elif t<43.6: u=sm(seg01(t,41.4,41.8)); kw['brow']=lerp(-1.0,1.0,u); kw['brow_up']=0.5*u; kw['eye']=1.25
    elif t<51.0:                                                       # grabs the mouse with a tiny arm
        u=sm(seg01(t,43.9,44.5)); kw['lean']=0.6*u; kw['neck']=-0.15*u; kw['rh']=lerp3((-0.36,1.95,-1.48),(-0.25,1.85,-1.65),u)
        if t>=44.5: kw['rh']=(-0.25+0.03*math.sin(t*9),1.85,-1.65+0.03*math.sin(t*9)); kw['brow']=1.0; kw['eye']=1.3; kw['look']=(0.7,-0.6)
        if t>=47.0: kw['brow']=-0.6+0.4*math.sin(t*20); kw['brow_up']=0.7; kw['eye']=1.5; kw['jaw']=0.5
    elif t<55.9: kw['brow']=-0.3; kw['brow_up']=0.2; kw['lean']=0.3; kw['neck']=0.2; kw['eye']=1.1
    else:
        wig=(55.9<=t<56.6)
        kw['brow_up']=(0.8*abs(math.sin((t-55.9)*PI*3.5)) if wig else 0.6); kw['brow']=0.0 if wig else 1.3+0.2*math.sin(t*30)
        kw['lean']=0.3; kw['neck']=0.25; kw['eye']=1.4 if wig else 1.25
    return kw
def doc_state(t):
    base=DOC_DESK; yaw=-PI/2; kw=dict(eye=1.2,brow=-0.8,mouth=0.0,sweat=0.0)
    face_trex=PI/2+0.25                                          # turns to look at the T-Rex (to -x)
    if t<0:                                                      # NEW HOOK: typing, freezes, turns very slowly
        typing=t<-6.5
        kw['eye']=1.0 if typing else 1.6; kw['brow']=0.2 if typing else -1.0; kw['sweat']=0.0 if t<-5.5 else 1.0
        if typing:
            kw['rh']=(-0.12,0.84+0.02*max(0,math.sin(t*23)),-0.46); kw['lh']=(0.12,0.84+0.02*max(0,math.sin(t*19+1)),-0.46); kw['hp']=0.15
        else:
            kw['rh']=(-0.12,0.86,-0.42); kw['lh']=(0.12,0.86,-0.42)
            yaw=lerp(-PI/2,face_trex,sm(seg01(t,-6.3,-5.5))); kw['hp']=-0.25*sm(seg01(t,-6.3,-5.5))
        if t>=-5.5: kw['rh']=(-0.2,1.2,-0.25); kw['lh']=(0.2,1.2,-0.25); kw['lean']=-0.15
        if -3.55<=t<-2.24: kw['mouth']=talk(t,-3.55,-2.24,26)
        if t>=-2.0: yaw=lerp(face_trex,-PI/2+0.3,sm(seg01(t,-1.7,-1.1))); kw['hp']=0.1
    elif t<11.0:
        yaw=face_trex; kw['eye']=1.1; kw['brow']=0.4; kw['mouth']=talk(t,5.3,7.62)
        u=win(t,5.3,7.8,0.2,0.3); kw['rh']=lerp3((-0.22,0.86,-0.05),(-0.3,1.45,-0.3),u)
    elif t<14.8: yaw=face_trex; kw['eye']=1.5; kw['brow']=-1.0; kw['sweat']=sm(seg01(t,12.0,12.5)); kw['lean']=-0.15*sm(seg01(t,12.6,13.3))
    elif t<21.0:                                                 # frantic fossil search
        u=sm(seg01(t,14.8,15.4)); base=lerp3(DOC_DESK,DOC_TABLE,u); yaw=lerp(face_trex,0.0,u) if u<1 else 0.0; kw['walk']=(t-14.8)*14*(u<1)
        kw['mouth']=talk(t,15.4,17.98,30); kw['sweat']=1.0; kw['eye']=1.4; kw['brow']=-1.0
        if t>=15.4: kw['rh']=(-0.2+0.1*math.sin(t*14),0.95+0.08*math.sin(t*11),-0.45); kw['lh']=(0.2+0.1*math.sin(t*13+1),0.95+0.08*math.sin(t*12),-0.45); kw['lean']=0.25
        if t>=19.2:
            u2=sm(seg01(t,19.2,19.7)); base=lerp3(DOC_TABLE,DOC_DESK,u2); yaw=lerp(0.0,face_trex,u2); kw['walk']=(t-19.2)*14*(u2<1); kw['lean']=0.0
    elif t<24.5: base=DOC_DESK; yaw=face_trex; kw['eye']=1.7; kw['brow']=-1.2; kw['sweat']=1.0; kw['lean']=-0.25*win(t,21.3,23.5,0.1,0.4)
    elif t<40.0:
        base=DOC_DESK; yaw=lerp(face_trex,PI*0.95,sm(seg01(t,24.6,25.3))) if t<29.0 else face_trex; kw['eye']=1.2; kw['brow']=-0.3
        if 28.8<=t<31.0: yaw=-PI/2; kw['rh']=(-0.1,1.2,-0.4)
        if t>=37.2: kw['brow']=-1.0; kw['eye']=1.0
    elif t<46.8:
        base=lerp3(DOC_DESK,DOC_SIDE,sm(seg01(t,42.9,43.4))); kw['walk']=(t-42.9)*14*(42.9<t<43.4)
        yaw=face_trex; kw['mouth']=talk(t,40.1,40.9,22); kw['brow']=-0.6; kw['eye']=1.0+0.6*sm(seg01(t,41.6,42.0)); kw['rh']=(-0.25,1.0,-0.2) if t<41.6 else (-0.3,1.4,-0.35)
    elif t<51.0: base=DOC_SIDE; yaw=face_trex; kw['eye']=1.8; kw['brow']=-1.3; kw['sweat']=1.0; kw['rh']=(-0.18,1.62,-0.12); kw['lh']=(0.18,1.62,-0.12); kw['hy']=0.25*math.sin(t*7)
    else:
        base=DOC_SIDE; yaw=face_trex; kw['eye']=1.5; kw['brow']=-1.1; kw['sweat']=1.0; kw['rh']=(-0.2,1.15,-0.25); kw['lh']=(0.2,1.15,-0.25)
        if 55.0<=t<55.9: kw['nod']=(t-55.0)/0.45
        if t>=58.3: kw['eye']=2.2; kw['brow']=-1.6; kw['mouth']=1.0; kw['lean']=-0.2
    return base,yaw,kw
BIRD_P=[(24.8,(0.3,0,4.6)),(26.6,(0.5,0,2.6)),(27.4,(1.25,0.78,0.9)),(28.2,(1.6,0.78,-0.35)),(39.5,(1.6,0.78,-0.35)),(40.3,(2.0,0.78,-2.6))]
def bird_state(t):
    if t<24.8: return None
    p=None
    for (a,pa),(b_,pb) in zip(BIRD_P,BIRD_P[1:]):
        if a<=t<b_: u=(t-a)/(b_-a); p=lerp3(pa,pb,u); hop=0.12*abs(math.sin(u*PI*4)) if b_<=26.6 else (0.0 if a==28.2 else 0.25*math.sin(u*PI)); break
    if p is None: p=BIRD_P[-1][1]; hop=0.0
    flap=1.0 if (26.6<=t<28.2 or 39.5<=t<40.3) else 0.0
    yaw=0.0 if t<26.6 else (-0.42 if t<28.2 else PI/2)
    return p,yaw,dict(hop=hop,bob=math.sin(t*9)*(t<31.0 or t>33.6),beak=talk(t,31.1,33.44,28),flap=flap)
def croc_state(t):
    if t<25.6: return None
    u=sm(seg01(t,25.6,30.2)); p=lerp3((0.4,0,6.2),(-0.3,0,2.9),u); yaw=0.0
    return p,yaw,dict(walk=(t-25.6)*3*(u<1),jaw=0.35*talk(t,34.6,36.79,9),lid=0.55+0.4*(abs(((t*0.6)%3.0)-1.5)<0.06),tail=0.3*math.sin(t*1.1))
def door_open(t): return sm(seg01(t,24.5,25.0))*(1-sm(seg01(t,31.0,31.5)))
# ======================= SHOTS =======================
R=Renderer(W,H,fog=(150,170,166))
SCREENS={}
def shot(T):
    """returns (kind, cam_pos, target, fov). kind: 'lab' | screen name"""
    if T<-5.5: u=sm(seg01(T,-9.0,-5.5)); return 'lab',lerp3((2.1,1.5,-0.85),(1.85,1.6,-0.6),u),(0.35,1.95,0.5),lerp(58,52,u)
    if T<-3.8: return 'lab',(1.55,1.75,-0.4),(-0.4,2.25,0.75),54
    if T<-2.0: return 'lab',(0.25,1.6,-0.65),(1.0,1.57,0.15),42
    if T<-1.0: return 'lab',(1.3,2.0,-0.55),(-0.25,2.35,0.75),48
    if T<0: return 'crt_size',None,None,None
    if T<5.0: return 'lab',(0.25,1.6,-0.65),(1.0,1.57,0.15),42
    if T<11.0: return 'creator',None,None,None
    if T<15.0: u=sm(seg01(T,11.0,15.0)); return 'lab',lerp3((2.0,2.5,-1.4),(1.5,2.45,-0.95),u),(-0.45,2.55,0.75),50
    if T<18.4: return 'lab',(2.9,1.7,-4.4),(0.9,1.0,-2.3),52
    if T<20.0: return 'crt_tissue',None,None,None
    if T<24.5: return 'lab',(-1.0,1.5,-3.4),(-1.3,1.6,0.4),58
    if T<29.0: return 'lab',(1.9,0.95,1.3),(0.1,0.5,4.6),58
    if T<31.0: return 'crt_tree',None,None,None
    if T<34.4: return 'lab',(0.15,1.3,-1.25),(1.6,1.0,-0.35),46
    if T<37.2: return 'lab',(-0.65,0.78,-0.05),(-0.3,0.45,1.7),52
    if T<38.4: return 'crt_inconclusive',None,None,None
    if T<40.0: return 'lab',(1.6,2.6,-0.9),(-0.5,2.5,0.75),48
    if T<43.6: return 'lab',(3.1,1.9,-1.55),(-0.8,1.7,0.6),60
    if T<45.0: return 'lab',(1.8,1.05,-0.25),(1.3,0.85,0.7),52
    if T<48.2: return 'slider',None,None,None
    if T<49.6: return 'lab',(3.4,2.4,-3.2),(0.5,1.6,0.7),60
    if T<51.0: return 'slider',None,None,None
    if T<53.0: return 'err404',None,None,None
    if T<55.9: return 'lab',(3.1,1.9,-1.5),(-0.5,1.9,0.55),56
    if T<58.3:
        trex(trex_base(T)[0],TREX_YAW,T,**trex_state(T)); h=HAND['head']; return 'lab',tuple(h+np.array([2.0,0.0,-1.2])),tuple(h+np.array([0,0.05,0])),44
    return 'lab',(0.3,1.6,-1.0),(0.95,1.57,-0.75),36
def build(T,cp,menu=False):
    groups=[]
    def add(Q,D=None):
        if not Q: return
        c=np.mean([q['c'] for q in Q],axis=0); groups.append((np.linalg.norm(c-cp),Q,[x for x in (D or []) if np.linalg.norm(x['c']-cp)<np.linalg.norm(x['hc']-cp)]))
    tk=trex_state(T)
    if menu: add(*trex((0,0,1.2),T*0.7+0.6,T,**{k:v for k,v in tk.items() if k not in ('lean','neck','hy')}))
    else:
        tb,tw=trex_base(T); tk.setdefault('walk',tw); add(*trex(tb,TREX_YAW,T,**tk))
        b,y,kw=doc_state(T); add(*doc(b,y,T,**kw))
        bs=bird_state(T)
        if bs: add(*bird(bs[0],bs[1],T,**bs[2]))
        cs=croc_state(T)
        if cs: add(*croc(cs[0],cs[1],T,**cs[2]))
        add(bones(T)); add(beakers(T)); add(mouse(T)); add(door(door_open(T))); add(alarm_light(T))
    groups.sort(key=lambda g:-g[0]); L=[]
    for _,Q,D in groups: L+=[Q,D]
    return L
def render_lab(T,pos,tgt,fov):
    shake=(0,0)
    if 21.35<=T<21.7: k=(21.7-T)/0.35; shake=(int(3*k*math.sin(T*90)),int(3*k*math.cos(T*70)))
    cam=Camera.look(pos,tgt); cp=np.array(pos)
    layers=[LAB_F,LAB_W,LAB_P]+build(T,cp)
    L=[((0,4.8,0),(255,255,245),1.15),((-3,4.8,2.5),(255,255,245),0.8),((-6.5,4.8,0.5),(255,255,245),0.8),((2.5,1.4,0.1),(150,255,170),0.35)]
    if 46.9<=T<51.0: L.append(((0,4.3,Z0+0.6),(255,40,30),2.5*(0.5+0.5*math.sin(T*16))))
    img,vi=R.render(cam,layers,L,fov=fov,fog_start=12,fog_end=30,ambient=0.38,shake=shake)
    return post.ps1(img),vi
# ======================= UI SCREENS =======================
WHT=(240,240,240); YEL=(255,214,60); RED=(240,50,50); GRN=(70,230,90); GRY=(150,150,160); PH=(80,255,120)
def otext(d,s,x,y,col,sc=1):
    o=max(1,sc//2)
    for ox,oy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)): font.text(d,s,x+ox*o,y+oy*o,(0,0,0),sc,None)
    font.text(d,s,x,y,col,sc,None)
def ctext(d,s,y,col,sc=1): otext(d,s,(W-font.width(s,sc))//2,y,col,sc)
def crt(img):
    a=np.asarray(img).astype(np.float32); a[::2]*=0.72
    yy,xx=np.mgrid[0:H,0:W]; v=1-0.55*(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2)**1.5
    a*=np.clip(v,0.2,1)[...,None]; return Image.fromarray(np.clip(a,0,255).astype(np.uint8))
def screen_crt(T,lines):
    img=Image.new('RGB',(W,H),(6,18,10)); d=ImageDraw.Draw(img)
    d.rectangle([4,4,W-5,H-5],outline=(40,120,60))
    for (txt,y,col,sc,blink) in lines:
        if blink and int(T*4)%2==0: continue
        ctext(d,txt,y,col,sc)
    return crt(img)
def screen_creator(T):
    cp=np.array([0.0,2.2,-6.6]); cam=Camera.look(tuple(cp),(0,0.9,1.2))
    img,_=R.render(cam,[tiled_plane(-6,6,-3,6,0,1.0,lambda i,j:(24,30,70) if (i+j)%2 else (30,38,90))]+build(T,cp,menu=True),[((0,6,-4),(255,255,255),5.0)],fov=54,fog_start=8,fog_end=20,ambient=0.55)
    img=post.ps1(img); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W,22],fill=(10,10,40)); ctext(d,'DINO CREATOR',6,YEL,1)
    rows=[('TEETH','COMPLETE',GRN,5.7),('CLAWS','COMPLETE',GRN,6.3),('TAIL','COMPLETE',GRN,6.9),('EYEBROWS','COMPLETE',GRN,7.5),('PRIVATE PARTS','UNKNOWN',RED,8.3)]
    d.rectangle([6,172,W-7,252],fill=(10,12,40),outline=(120,130,220))
    cur=min(4,int(max(0,T-5.7)/0.65)) if T<10.3 else 4
    for i,(a,b_,col,t0) in enumerate(rows):
        if T<t0: continue
        y=178+i*14
        if i==cur: d.rectangle([9,y-3,W-10,y+9],fill=(60,60,20) if i<4 else (70,10,10))
        otext(d,a+':',14,y,WHT); bw=font.width(b_)
        if not (i==4 and T>=9.0 and int(T*4)%2==0): otext(d,b_,W-14-bw,y,col)
    if T>=10.0 and int(T*3)%2==0: ctext(d,'! DATA MISSING !',258-0,RED)
    return img
def screen_slider(T):
    img=Image.new('RGB',(W,H),(14,14,46)); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W,22],fill=(10,10,40)); ctext(d,'DINO CREATOR',6,YEL)
    ctext(d,'PRIVATE PARTS',60,WHT); ctext(d,'SIZE',74,GRY)
    x0,x1,y=20,160,124
    d.rectangle([x0,y-3,x1,y+3],fill=(40,40,70),outline=GRY)
    otext(d,'MIN',x0,y+12,GRY); otext(d,'MAX',x1-font.width('MAX'),y+12,YEL)
    t2=T if T<48.2 else T-1.4                                   # the lab cutaway (48.2-49.6) does not stop the drag
    u=seg01(t2,45.2,47.2); hx=int(lerp(x0+8,x1,sm(u))); over=max(0,t2-47.2)
    hx=hx+int(over*90)
    fill_to=min(hx,x1); d.rectangle([x0+1,y-2,fill_to,y+2],fill=GRN if hx<x1-10 else (YEL if hx<=x1 else RED))
    if hx<W+10: d.rectangle([hx-3,y-7,hx+3,y+7],fill=WHT,outline=(0,0,0))
    cx=min(hx+2,W+40); d.polygon([(cx,y+2),(cx,y+14),(cx+3,y+11),(cx+6,y+16),(cx+8,y+15),(cx+5,y+10),(cx+9,y+10)],fill=WHT,outline=(0,0,0))
    if hx<x1-10: val='%.1fX'%(1+9*sm(u))
    elif hx<=x1: val='MAX'
    else: val=['MAX+1','999X','99999X','OVERFLOW','???????'][min(4,int(over*2.2))]
    col=GRN if hx<x1-10 else (YEL if hx<=x1 else RED)
    otext(d,'VALUE:',30,160,WHT); otext(d,val,30+font.width('VALUE:')+6,160,col)
    if hx>x1:
        if int(T*6)%2==0: d.rectangle([10,196,W-11,226],fill=(90,0,0),outline=RED); ctext(d,'WARNING:',201,YEL); ctext(d,'VALUE NOT SUPPORTED',213,WHT)
    img2=img
    if t2>=48.3:                                                 # the crash: the menu itself breaks apart
        a=np.asarray(img).copy(); rnd=np.random.default_rng(int(T*24))
        for _ in range(int(4+10*seg01(t2,48.3,49.6))):
            yy=int(rnd.integers(0,H-10)); h=int(rnd.integers(2,10)); a[yy:yy+h]=np.roll(a[yy:yy+h],int(rnd.integers(-30,30)),axis=1)
        img2=Image.fromarray(a)
    return crt(img2)
def subtitle(d,T):
    cur=None
    for k,t0,txt,dd in SCRIPT:
        if t0<=T<t0+dd+0.15: cur=(k,txt)
    if not cur: return
    k,txt=cur; spk={'T':('T-REX:',(140,230,90)),'S':('DOC:',(150,200,255)),'B':('BIRD:',(255,200,90)),'C':('CROC:',(120,210,150))}[k[0]]
    words=(spk[0]+' '+txt.upper().replace('...','..')).split(); lines=[]; cur_=''
    for w_ in words:
        if len(cur_)+len(w_)+(1 if cur_ else 0)>27: lines.append(cur_); cur_=w_
        else: cur_=(cur_+' '+w_).strip()
    lines.append(cur_)
    y=272-11*(len(lines)-1)
    HIL={'BIG','EYEBROWS?!','THAT?!','BONES!','RELATIVES!','ONE.','DO.','GUESS.','OWN','SIZE!','NOBODY','KNOWS?','EVERYTHING..','TWENTY'}
    for ln in lines:
        xw=font.width(ln); x=(W-xw)//2; d.rectangle([x-3,y-2,x+xw+2,y+8],fill=(0,0,0)); cx=x
        for wd in ln.split(' '):
            col=spk[1] if wd==spk[0] else (YEL if wd in HIL else WHT)
            otext(d,wd,cx,y,col); cx+=font.width(wd)+6
        y+=11
FREEZE=59.0
def frame(V):
    T=story_t(V)
    if T>=FREEZE: T_=FREEZE-1e-3
    else: T_=T
    kind,pos,tgt,fov=shot(T_)
    if kind=='lab': img,vi=render_lab(T_,pos,tgt,fov)
    elif kind=='creator': img=screen_creator(T_)
    elif kind=='slider': img=screen_slider(T_)
    elif kind=='crt_size': img=screen_crt(T_,[('SIZE:',120,PH,2,False),('???',146,RED,3,True)])
    elif kind=='crt_tissue': img=screen_crt(T_,[('FOSSIL SCAN',90,PH,1,False),('BONES:',120,PH,1,False),('FOUND',132,GRN,1,False),('SOFT TISSUE:',160,PH,1,False),('NOT PRESERVED',172,RED,1,True)])
    elif kind=='crt_tree': img=screen_tree(T_)
    elif kind=='crt_inconclusive': img=screen_crt(T_,[('ESTIMATE:',120,PH,2,False),('INCONCLUSIVE',150,RED,1,True)])
    elif kind=='err404':
        img=Image.new('RGB',(W,H),(0,0,0)); d=ImageDraw.Draw(img)
        ctext(d,'ERROR 404',110,RED,2); ctext(d,'FOSSIL EVIDENCE',142,WHT); ctext(d,'NOT FOUND',156,WHT)
        if int(T_*2)%2==0: ctext(d,'PRESS START',200,GRY)
        img=crt(img)
    if 55.9<=T_<58.3 and kind=='lab':                            # he is looking at his reflection in the dead CRT
        a=np.asarray(img).astype(np.float32); a=a*np.array([0.7,0.95,0.78])+np.array([0,10,4]); a[::2]*=0.85
        img=Image.fromarray(np.clip(a,0,255).astype(np.uint8)); d=ImageDraw.Draw(img)
        for k in range(10): d.rectangle([k,k,W-1-k,H-1-k],outline=tuple(int(c*(0.55+0.04*k)) for c in BEIGE))
    if T>=FREEZE:
        a=np.asarray(img).astype(np.float32); g=a.mean(2,keepdims=True); a=0.5*a+0.5*g; img=Image.fromarray(np.clip(a*1.05,0,255).astype(np.uint8))
    d=ImageDraw.Draw(img)
    if T<FREEZE: subtitle(d,T_)
    return img
def screen_tree(T):
    img=Image.new('RGB',(W,H),(6,18,10)); d=ImageDraw.Draw(img); d.rectangle([4,4,W-5,H-5],outline=(40,120,60))
    ctext(d,'FAMILY TREE',40,PH)
    u=seg01(T,29.0,30.2)
    ctext(d,'ARCHOSAURS',250,PH)
    d.line([90,244,90,226],fill=PH); d.line([45,226,135,226],fill=PH)
    if u>0.2: d.line([45,226,45,190],fill=PH); otext(d,'CROCS',45-font.width('CROCS')//2,178,GRN)
    if u>0.4: d.line([135,226,135,150],fill=PH); otext(d,'DINOSAURS',135-font.width('DINOSAURS')//2,138,PH)
    if u>0.6: d.line([135,134,135,110],fill=PH); d.line([105,110,160,110],fill=PH)
    if u>0.8: otext(d,'T-REX',105-font.width('T-REX')//2,96,YEL); otext(d,'BIRDS',160-font.width('BIRDS')//2,96,GRN)
    return crt(img)
TEST=os.environ.get('TEST')
if TEST:
    ims=[frame(float(x)) for x in TEST.split(',')]; sh=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): sh.paste(im,(i*182,0))
    sh.resize((sh.width*2,640),Image.NEAREST).save('test.png'); sys.exit()

if __name__=='__main__' and os.environ.get('PART') and os.environ['PART']!='audio':
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','20','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'tx_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.95,vignette=0.25,grain=1.6,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(post.upscale(frame(f/FPS),S),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
# ======================= AUDIO =======================
def build_old(path):
    import soundfile as _sf
    s=Sound(59.5,loop=False,seed=41); sr=s.sr; n=s.n; t=s.t; M=np.zeros(n)
    def note(buf,t0,m,d,v,wave='sq',duty=0.5,dec=3.0,att=0.004,vib=0.0):
        f=440*2**((m-69)/12); tt=s.T(d); fr=f*(1+vib*np.sin(2*np.pi*6*tt)); ph=np.cumsum(fr)/sr%1
        x=np.where(ph<duty,1.0,-1.0) if wave=='sq' else (4*np.abs(ph-0.5)-1 if wave=='tri' else np.sin(2*np.pi*ph))
        env=np.minimum(1,tt/att)*np.exp(-tt*dec); i=int(t0*sr); j=min(n,i+len(tt)); buf[i:j]+=(x*env*v)[:j-i]
    def kick(t0,v=0.15): tt=s.T(0.14); i=int(t0*sr); j=min(n,i+len(tt)); M[i:j]+=(np.sin(2*np.pi*(110-60*tt/0.14)*tt)*np.exp(-tt*22)*v)[:j-i]
    def hat(t0,v=0.02,seed=0): x=s.filt_short(s.noise(0.04,seed),lo=7000)*np.exp(-s.T(0.04)*90); i=int(t0*sr); j=min(n,i+len(x)); M[i:j]+=(x*v)[:j-i]
    def snare(t0,v=0.05,seed=0): x=s.filt_short(s.noise(0.12,seed),lo=1500,hi=7000)*np.exp(-s.T(0.12)*28); i=int(t0*sr); j=min(n,i+len(x)); M[i:j]+=(x*v)[:j-i]
    def blip(t0,f,d=0.06,v=0.035,dec=10): tt=s.T(d); s.place(np.where((f*tt)%1<0.5,1.0,-1.0)*np.exp(-tt*dec),t0,v)
    def nb(t0,d,lo,hi,v,seed,shape=2,pan=0.0): s.place(s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v,pan)
    def stomp(t0,v=0.5): tt=s.T(0.7); s.place(np.sin(2*np.pi*(55-20*tt)*tt)*np.exp(-tt*7)+s.filt_short(s.noise(0.7,int(t0*9)),hi=400)*np.exp(-tt*9)*0.6,t0,v)
    def sweep(t0,d,f0,f1,v,wave='sq'): tt=s.T(d); f=f0+(f1-f0)*tt/d; ph=np.cumsum(f)/sr%1; x=np.where(ph<0.5,1.0,-1.0) if wave=='sq' else np.sin(2*np.pi*ph); s.place(x*np.minimum(1,(d-tt)/0.01),t0,v)
    def step(t0,v=0.04,seed=0): tt=s.T(0.08); s.place(s.filt_short(s.noise(0.08,seed),lo=300,hi=3000)*np.exp(-tt*60),t0,v)
    room=s.filt(s.rng.normal(0,1,n),lo=80,hi=900)*0.01; hum=np.sin(2*np.pi*60*t)*0.006+np.sin(2*np.pi*120*t)*0.004
    bed=room+hum; bed[int(55.9*sr):int(56.6*sr)]=0
    s.L+=bed; s.R+=bed
    # ---------- hook ----------
    stomp(0.03,0.6); nb(0.0,0.45,300,4000,0.12,1); note(M,0.05,40,1.0,0.07,'sq',0.3,2); note(M,0.05,46,1.0,0.05,'sq',0.3,2)
    blip(2.65,440,0.18,0.06,3); blip(2.85,330,0.3,0.06,3)                                       # comedic error "bwomp"
    for k in range(3): blip(3.0+k*0.25,880,0.06,0.02)
    # ---------- character select theme 5.0-11.0 ----------
    mel=[76,79,81,79,76,74,72,74,76,79,84,81,79,76,74,76]; bas=[48,48,55,55,53,53,55,55]
    for k in range(int(6.0/0.25)):
        tc=5.0+k*0.25
        note(M,tc,mel[k%16],0.22,0.03,'sq',0.25,6)
        if k%2==0: note(M,tc,bas[(k//2)%8],0.45,0.06,'tri',dec=3)
        if k%4==0: kick(tc,0.12)
        if k%4==2: snare(tc,0.04,k)
        hat(tc+0.125,0.015,k)
    for k,tc in enumerate((5.7,6.3,6.9,7.5)): blip(tc,1047,0.05,0.035); blip(tc+0.06,1568,0.08,0.035)
    blip(8.3,180,0.35,0.06,2); blip(8.65,140,0.35,0.06,2)                                        # PRIVATE PARTS: UNKNOWN
    for k in range(5): blip(5.7+k*0.65,660,0.03,0.02)                                            # cursor moves
    for k in range(3): blip(10.0+k*0.33,220,0.12,0.03,6)
    note(M,11.35,38,1.6,0.08,'sq',0.4,1.2); note(M,11.35,39,1.6,0.06,'sq',0.4,1.2)            # music cut + tense sting
    # ---------- frantic search 15-21 ----------
    for k in range(int(5.6/0.125)):
        tc=15.2+k*0.125; note(M,tc,[62,65,69,65,64,67,71,67][k%8],0.1,0.022,'sq',0.25,14)
        if k%4==0: note(M,tc,38 if (k//8)%2==0 else 40,0.2,0.05,'tri',dec=8)
    for k in range(22): nb(15.4+k*0.24+0.05*math.sin(k*3),0.06,600,3000,0.05,100+k,shape=1)      # bone clatter
    for k in range(8): blip(18.45+k*0.17,1200,0.02,0.015,40)                                     # CRT typing
    blip(19.3,200,0.25,0.04,4)
    for tc in (14.85,15.05,15.25,19.25,19.45): step(tc,0.04,int(tc*10))
    stomp(21.4,0.7); nb(21.42,0.4,1500,6000,0.08,2,shape=1)                                     # desk slam + rattle
    # ---------- relatives ----------
    tt=s.T(0.7); s.place(np.sin(2*np.pi*np.cumsum(150+60*np.sin(2*np.pi*1.6*tt))/sr)*np.sin(np.pi*tt/0.7)*0.5,24.5,0.06)   # door creak
    for k in range(9): step(24.85+k*0.2,0.025,200+k)
    for a_,b_ in ((26.6,28.2),(39.5,40.3)):
        x=s.filt(s.rng.normal(0,1,int((b_-a_)*sr)),lo=500,hi=3000)*(0.5+0.5*np.sign(np.sin(2*np.pi*14*s.T(b_-a_)))); s.place(x,a_,0.03)
    for k in range(8): nb(25.7+k*0.55,0.45,80,700,0.05,300+k,shape=1)                          # croc slow drag
    lo_=[45,None,48,None,43,None,45,47]
    for k in range(int(12.6/0.5)):
        tc=24.6+k*0.5; m=lo_[k%8]
        if m and tc<37.1: note(M,tc,m,0.4,0.09,'sq',0.5,4)
        if k%2==0 and tc<37.1: hat(tc,0.012,k)
    for k in range(6): blip(29.1+k*0.2,880+k*110,0.04,0.02)                                     # tree drawing
    blip(37.25,150,0.3,0.06,1.5); blip(37.6,110,0.5,0.06,1.5)                                    # INCONCLUSIVE buzzer
    for k,m in enumerate((55,54,53,52)): note(M,38.45+k*0.35,m,0.34 if k<3 else 0.9,0.06,'sq',0.5,1.0 if k==3 else 2.5,vib=0.012 if k==3 else 0.0)   # sad trombone
    # ---------- the bad idea ----------
    for k,m in enumerate((60,64,67,72)): note(M,42.95+k*0.07,m,0.25,0.04,'sq',0.25,5)            # determination sting
    stomp(43.35,0.35); stomp(43.75,0.35)
    for k in range(4): step(43.05+k*0.15,0.035,400+k)
    blip(44.3,2400,0.015,0.04,100); blip(44.42,2400,0.015,0.04,100)                              # mouse click
    sweep(45.2,2.0,300,1200,0.05,'sq')                                                          # value rising with the slider
    for k in range(10): blip(45.2+k*0.2,600+k*80,0.02,0.015,50)
    sweep(47.2,1.0,1200,2400,0.05,'sq'); sweep(49.6,1.4,2400,3600,0.045,'sq')
    tc=46.9
    while tc<51.0:                                                                               # alarm siren
        sweep(tc,0.45,620,880,0.1,'sin'); sweep(tc+0.45,0.45,880,620,0.1,'sin'); tc+=0.9
    for k in range(12): blip(47.3+k*0.3,1760,0.08,0.02,20)
    g=s.filt(s.rng.normal(0,1,int(2.7*sr)),lo=500,hi=8000)*(np.sin(2*np.pi*31*s.T(2.7))>0.3)*np.linspace(0.2,1,int(2.7*sr)); s.place(g,48.3,0.09)
    # crash -> 404
    M[int(51.0*sr):]=0; s.silence(51.0,51.05,level=0.0,ramp=0.005)
    blip(51.05,523,0.12,0.06,4); blip(51.2,392,0.12,0.06,4); blip(51.35,262,0.35,0.06,3)
    nb(55.2,0.25,300,2000,0.02,600)                                                               # doc gulp
    # ---------- payoff ----------
    stomp(58.3,0.45); nb(58.3,0.3,1000,6000,0.12,700)
    for k,f in enumerate((880,660,440)): blip(59.0+k*0.14,f,0.12,0.06,5)
    # ---------- voices ----------
    NB=np.zeros(n); duck=np.ones(n)
    for key,t0,txt,dd in SCRIPT:
        a,ar=_sf.read(f'/home/claude/tts/v7/{key}.wav'); a=a if a.ndim==1 else a.mean(1)
        if ar!=sr: a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a)
        g_=0.55 if key[0]=='T' else 0.9
        i=int(t0*sr); j=min(n,i+len(a)); NB[i:j]+=a[:j-i]*g_
        duck[max(0,i-int(0.06*sr)):min(n,j+int(0.12*sr))]=0.42
    duck=np.convolve(duck,np.ones(2000)/2000,'same')
    s.L+=M*duck; s.R+=M*duck
    s.reverb(0.1,length=0.7,decay=6)
    pk=max(np.abs(s.L).max(),np.abs(s.R).max()); gv=pk*1.0/np.abs(NB).max()
    s.L=s.L*(0.65+0.35*duck)+NB*gv; s.R=s.R*(0.65+0.35*duck)+NB*gv
    s.L[int(55.9*sr):int(56.55*sr)]=0; s.R[int(55.9*sr):int(56.55*sr)]=0                        # sudden silence before the punchline
    return s.save(path,peak=0.9)
def build_hook(path):
    """new slow hook, 0-9 s"""
    import soundfile as _sf
    s=Sound(HOOK_LEN,loop=False,seed=43); sr=s.sr; n=s.n; t=s.t
    def blip(t0,f,d=0.06,v=0.035,dec=10): tt=s.T(d); s.place(np.where((f*tt)%1<0.5,1.0,-1.0)*np.exp(-tt*dec),t0,v)
    def key(t0,v,seed): tt=s.T(0.03); s.place(s.filt_short(s.noise(0.03,seed),lo=1500,hi=7000)*np.exp(-tt*120),t0,v)
    room=s.filt(s.rng.normal(0,1,n),lo=80,hi=900)*0.01; hum=np.sin(2*np.pi*60*t)*0.006+np.sin(2*np.pi*120*t)*0.004
    s.L+=room+hum; s.R+=room+hum
    rng=np.random.default_rng(5); tc=0.15
    while tc<2.5: key(tc,0.05+0.02*rng.random(),int(tc*100)); tc+=0.07+0.09*rng.random()      # typing, unaware
    tt=s.T(2.4); s.place(s.filt_short(s.noise(2.4,9),hi=260)*np.sin(np.pi*tt/2.4)*0.8+np.sin(2*np.pi*42*tt)*0.4*np.sin(np.pi*tt/2.4),0.3,0.12)   # big breath above him
    drone=(np.sin(2*np.pi*55*t)+0.6*np.sin(2*np.pi*58.3*t))*0.025*np.clip(t/2.5,0,1)*(t<3.5); s.L+=drone; s.R+=drone
    for k,f in enumerate((70,0)): pass
    tt=s.T(0.9); s.place(np.sin(2*np.pi*np.cumsum(180+40*np.sin(2*np.pi*1.2*tt))/sr)*np.sin(np.pi*tt/0.9)*0.3,2.65,0.04)    # slow creaky turn
    tt=s.T(1.4); s.place((np.sin(2*np.pi*48*tt*(1-0.2*tt))*np.exp(-tt*3)+s.filt_short(s.noise(1.4,3),hi=400)*np.exp(-tt*5)*0.5),3.5,0.45)   # sting
    for m in (40,46,51):
        f=440*2**((m-69)/12); tt=s.T(1.3); s.place(np.where((f*tt)%1<0.35,1.0,-1.0)*np.exp(-tt*1.8),3.5,0.03)
    tt=s.T(0.8); s.place(np.where((np.cumsum(np.full(len(tt),1.0))/sr*14)%1<0.5,1.0,-1.0)*0.3*np.exp(-tt*0.5),7.05,0.025)  # eyes sliding (ratchet)
    for k in range(8): blip(7.05+k*0.1,300+30*k,0.02,0.02,60)
    blip(8.05,440,0.18,0.06,3); blip(8.25,330,0.3,0.06,3)                                            # SIZE: ??? bwomp
    for k in range(3): blip(8.5+k*0.15,880,0.05,0.02)
    NB=np.zeros(n)
    for k_,t0,txt,dd in SCRIPT:
        if t0<0:
            a,ar=_sf.read(f'/home/claude/tts/v7/{k_}.wav'); g_=0.55 if k_[0]=='T' else 0.9
            i=int((t0+HOOK_LEN)*sr); j=min(n,i+len(a)); NB[i:j]+=a[:j-i]*g_
    return s,NB
def build_audio(path):
    import soundfile as _sf
    old=build_old(os.path.join(OUT,'trex_old.wav')); a_old,sr=_sf.read(os.path.join(OUT,'trex_old.wav'))
    sh,NB=build_hook(None)
    pk=np.abs(a_old).max(); hk=np.stack([sh.L,sh.R],1); hk=hk/ (np.abs(hk).max()+1e-9)*pk*0.8
    nb=NB/np.abs(NB).max()*pk*1.0; hk=hk+nb[:,None]
    tail=a_old[int(5.0*sr):]
    out=np.concatenate([hk[:int(HOOK_LEN*sr)],tail],0)
    f=int(0.03*sr); out[int(HOOK_LEN*sr)-f:int(HOOK_LEN*sr)]*=np.linspace(1,0.3,f)[:,None]
    out=out[:int(DUR*sr)]; out=out/np.abs(out).max()*0.9
    _sf.write(path,out,sr); return path
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'trex_size.wav'))); sys.exit()
