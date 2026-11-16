"""HOW BIG WAS IT? - 60 s PS1 game-show comedy, 9:16. Fully procedural (nightkit).
TEST=t1,t2 python examples/trex_size.py | PART=a:b | PART=audio"""
import os, sys, math, json
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, box, quad, tiled_plane, transform
from nightkit.engine import box as _engine_box
def box(x0,x1,y0,y1,z0,z1,col,xf=None,emit=False):
    """engine box with sorted extents; tagged so back faces can be culled (box faces wind inward)"""
    Q=_engine_box(min(x0,x1),max(x0,x1),min(y0,y1),max(y0,y1),min(z0,z1),max(z0,z1),col,xf=xf,emit=emit)
    for q in Q: q['wind']=-1
    return Q
def cull(Q,cp):
    """drop faces that point away from the camera (closed boxes/segments only); open planes have no 'wind' tag and stay"""
    out=[]
    for q in Q:
        w=q.get('wind')
        if w is None or w*float(np.dot(q['n'],cp-q['c']))>0: out.append(q)
    return out
from nightkit import motion, post, font
from nightkit.zraster import zrender
from nightkit.audio import Sound
for ch,rows in {'?':['01110','10001','00001','00110','00100','00000','00100'],'!':['00100','00100','00100','00100','00100','00000','00100'],
                '+':['00000','00100','00100','11111','00100','00100','00000'],'%':['11001','11010','00010','00100','01000','01011','10011']}.items():
    font.FONT.setdefault(ch,rows)
OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6; DUR=59.0; N=int(DUR*FPS)
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
    Q=[quad([tuple(v[i]) for i in f],col,emit) for f in F]
    for q in Q: q['wind']=1
    return Q
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
HOST_OUT=dict(coat=(226,180,40),coat_d=(180,140,30),pants=(24,24,30),hair=(20,18,20),skin=(214,166,128),shirt=(240,240,240),glasses=False,mous=True,mic=True)
def doc(base,yaw,t=0.0,walk=0.0,rh=None,lh=None,lean=0.0,hy=0.0,hp=0.0,eye=1.0,brow=0.0,mouth=0.0,sweat=0.0,nod=0.0,out=None):
    out=out or HOST_OUT; COAT,COAT_D,PANTS,HAIR,SKIN=out['coat'],out['coat_d'],out['pants'],out['hair'],out['skin']
    b=np.array(base,float); Rb=Ry(yaw)
    def W(p): return tuple(b+Rb@np.array(p,float))
    hip=0.86
    def WL(p): p=np.array(p,float); piv=np.array([0,hip,0]); return W(piv+Rx(-lean)@(p-piv))
    Q=[];D=[]; sw=0.42*math.sin(walk)
    for sx,ph in ((-1,1),(1,-1)):
        hp_=np.array([sx*0.08,hip,0]); a=ph*sw; ft=hp_+np.array([0,-0.82*math.cos(a),-0.82*math.sin(a)]); ft[1]=max(0.05,ft[1]); kn=(hp_+ft)/2+np.array([0,0,-0.04])
        Q+=transform(seg(hp_,kn,0.11,PANTS)+seg(kn,ft,0.1,PANTS)+box(ft[0]-0.05,ft[0]+0.05,ft[1]-0.05,ft[1]+0.03,ft[2]-0.12,ft[2]+0.05,(50,40,34)),W)
    Q+=box(-0.16,0.16,0.84,1.36,-0.1,0.1,COAT,xf=WL)+box(-0.18,0.18,0.5,0.9,-0.115,0.115,COAT,xf=WL)
    D+=box(-0.02,0.02,0.5,1.3,-0.118,-0.112,COAT_D,xf=WL)+box(-0.07,0.07,1.12,1.36,-0.118,-0.11,out['shirt'],xf=WL)+box(-0.035,0.035,1.26,1.32,-0.122,-0.118,(200,20,30),xf=WL)   # jacket, shirt, bow tie
    hc=np.array([0,1.52,0]); n_=0.3*math.sin(nod*PI*2)*(nod>0)
    def WH(p): p=np.array(p,float); return WL(hc+Ry(hy)@Rx(hp+n_)@(p-hc))
    Q+=box(-0.045,0.045,1.34,1.42,-0.045,0.045,SKIN,xf=WL)+box(-0.1,0.1,1.4,1.64,-0.11,0.1,SKIN,xf=WH)
    Q+=box(-0.11,0.11,1.6,1.72,-0.12,0.12,HAIR,xf=WH)+box(-0.105,0.105,1.5,1.62,0.06,0.12,HAIR,xf=WH)+box(-0.02,0.12,1.7,1.76,-0.13,0.0,HAIR,xf=WH)
    for sx in (-1,1):                                                        # round-ish glasses + eyes
        x=sx*0.048
        if out['glasses']:
            for (x0,x1,y0,y1) in ((x-0.04,x+0.04,1.555,1.565),(x-0.04,x+0.04,1.485,1.495),(x-0.045,x-0.035,1.49,1.56),(x+0.035,x+0.045,1.49,1.56)):
                D+=box(x0,x1,y0,y1,-0.122,-0.116,(20,20,24),xf=WH)
        e=0.013*eye; D+=box(x-0.012,x+0.012,1.525-e,1.525+e,-0.12,-0.112,(24,20,22),xf=WH)
        by=1.585+0.012*(eye-1); bt=brow
        D+=transform(seg((x-sx*0.03,by+0.008*bt,-0.116),(x+sx*0.025,by-0.01*bt,-0.116),0.012,HAIR,depth=0.004),WH)
    if out['mous']: D+=box(-0.045,0.045,1.465,1.48,-0.12,-0.112,HAIR,xf=WH)
    mh=0.008+0.035*mouth; D+=box(-0.025+0.008*mouth,0.025-0.008*mouth,1.445-mh/2,1.445+mh/2,-0.118,-0.11,(120,50,50),xf=WH)
    if sweat>0:
        for k,(sx,yy) in enumerate(((1,1.6),(-1,1.56))):
            D+=box(sx*0.1-0.012+sx*0.004,sx*0.1+0.012+sx*0.004,yy-0.04*sweat,yy,-0.09,-0.06,(140,200,255),xf=WH)
    for sx,hd in ((-1,rh),(1,lh)):
        if hd is None: s_=-sx*0.3*math.sin(walk)*(1 if walk else 0); hd=(sx*0.22,0.86,-0.3*s_-0.05)
        sh=np.array(WL((sx*0.22,1.3,0))); hw=np.array(WL(hd)); el=elbow(sh,hw,tuple(Rb@np.array([sx*0.6,0,-0.15])),0.56)
        Q+=seg(sh,el,0.095,COAT)+seg(el,hw,0.085,COAT)+obox(hw,(0.04,0.045,0.04),Rb,SKIN)
        if out['mic'] and sx<0: Q+=seg(hw,hw+Rb@np.array([0.0,0.2,-0.05]),0.035,(30,30,34))+obox(hw+Rb@np.array([0,0.24,-0.06]),(0.04,0.04,0.04),Rb,(80,80,90))
    hcW=np.array(WH((0,1.52,0))); tcW=np.array(WL((0,1.1,0)))
    for q in D: q['hc']=hcW if q['c'][1]>hcW[1]-0.14 else tcW
    return Q,D
# ======================= BIRD + CROC =======================
PIGEON=(138,140,152); PIGEON_D=(96,100,116); BEAK=(240,160,40); CROC=(72,112,62); CROC_D=(52,84,44); CROC_B=(180,176,120)
BIRDS={'pigeon':dict(body=(138,140,152),dark=(96,100,116),head=(96,100,116),beak=(240,160,40),feet=(240,160,40),comb=None),
       'duck':dict(body=(236,236,228),dark=(212,212,204),head=(236,236,228),beak=(250,150,30),feet=(250,150,30),comb=None),
       'chicken':dict(body=(196,110,52),dark=(150,76,34),head=(196,110,52),beak=(250,200,40),feet=(250,200,40),comb=(220,30,36))}
def bird(base,yaw,t=0.0,hop=0.0,bob=0.0,beak=0.0,flap=0.0,s=1.6,kind='pigeon',hy=0.0):
    P=BIRDS[kind]; PIGEON,PIGEON_D,HEADC,BEAK,FEET=P['body'],P['dark'],P['head'],P['beak'],P['feet']
    b=np.array(base,float); Rb=Ry(yaw)
    def W(p): return tuple(b+Rb@(np.array(p,float)*s)+np.array([0,hop,0]))
    Q=[];D=[]
    Q+=box(-0.11,0.11,0.12,0.34,-0.14,0.16,PIGEON,xf=W)+box(-0.08,0.08,0.18,0.3,0.16,0.3,PIGEON_D,xf=W)
    hz=-0.17-0.05*bob
    def WH(p): p=np.array(p,float); return W(Ry(hy)@p+np.array([0,0,hz]))
    Q+=box(-0.07,0.07,0.32,0.46,-0.06,0.07,HEADC,xf=WH)
    if P['comb']: Q+=box(-0.015,0.015,0.46,0.52,-0.05,0.04,P['comb'],xf=WH)+box(-0.012,0.012,0.3,0.34,-0.11,-0.08,P['comb'],xf=WH)
    Q+=box(-0.025,0.025,0.37,0.4,-0.13,-0.06,BEAK,xf=WH)+box(-0.02,0.02,0.34-0.03*beak,0.37-0.03*beak,-0.12,-0.06,BEAK,xf=WH)
    for sx in (-1,1):
        D+=box(sx*0.069,sx*0.076,0.395,0.445,-0.05,0.004,(250,250,250),xf=WH)
        D+=box(sx*0.075,sx*0.08,0.405,0.432,-0.04,-0.014,(10,10,10),xf=WH)
        a=0.9*flap*math.sin(t*40)
        def WW(p,sx=sx,a=a): p=np.array(p,float); q=np.array([sx*0.11,0.3,0])+Rz(sx*a)@p; return W(q)
        Q+=transform(box(min(0,sx*0.02),max(0,sx*0.02),-0.12,0.02,-0.1,0.14,PIGEON_D),WW)
        Q+=transform(seg((sx*0.04,0.13,0),(sx*0.04,0.0,-0.02),0.025,FEET),W)
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
# ======================= STUDIO =======================
KEY=(255,0,255)                                      # chroma key for the big screen (UI is warped onto it)
STAGE=lambda i,j:[(46,40,96),(34,30,74)][(i+j)%2]
def studio():
    F=tiled_plane(-8,8,-1.5,7.5,0,0.8,STAGE)+tiled_plane(-8,8,-7,-1.5,-0.6,1.0,lambda i,j:(30,24,40))
    B=box(-8,8,-0.6,0,-1.55,-1.5,(60,50,120))
    for k in range(20): x=-7.6+k*0.8; B+=box(x,x+0.4,-0.35,-0.25,-1.57,-1.55,(255,210,90),emit=True)        # stage-edge bulbs
    Wq=[quad([(-8,-0.6,7.5),(8,-0.6,7.5),(8,7.5,7.5),(-8,7.5,7.5)],(36,22,60))]
    for x in (-7,-5,5,7): Wq+=box(x-0.12,x+0.12,0,7,7.38,7.45,(120,60,200),emit=True)
    Wq.append(quad([(-2.7,1.9,7.42),(2.7,1.9,7.42),(2.7,5.1,7.42),(-2.7,5.1,7.42)],KEY,emit=True))
    Wq+=box(-2.95,2.95,1.7,1.9,7.3,7.45,(70,60,90))+box(-2.95,2.95,5.1,5.3,7.3,7.45,(70,60,90))+box(-2.95,-2.7,1.7,5.3,7.3,7.45,(70,60,90))+box(2.7,2.95,1.7,5.3,7.3,7.45,(70,60,90))
    return F,B,Wq
ST_F,ST_B,ST_W=studio()
def marquee(t):
    Q=[]
    for k in range(26):
        on=(k+int(t*6))%3==0; c=(255,220,90) if on else (110,80,40)
        if k<8: x,y=-2.82+k*0.8,5.2
        elif k<16: x,y=-2.82+(k-8)*0.8,1.8
        elif k<21: x,y=-2.82,2.2+(k-16)*0.65
        else: x,y=2.82,2.2+(k-21)*0.65
        Q+=box(x-0.06,x+0.06,y-0.06,y+0.06,7.25,7.3,c,emit=True)
    return Q
TB=(-3.4,0.0,3.0); TYAW=-0.35
def trex_podium(t,buzz=False):
    Rb=Ry(TYAW); b=np.array(TB)
    def W(p): return tuple(b+Rb@np.array(p,float))
    Q=box(-0.6,0.6,0,1.82,-2.0,-1.55,(70,40,140),xf=W)+box(-0.66,0.66,1.82,1.88,-2.06,-1.5,(230,200,90),xf=W)
    Q+=box(-0.45,0.45,0.6,1.3,-2.02,-2.005,(250,90,200),emit=True,xf=W)
    Q+=box(-0.1,0.1,1.88,1.98-(0.04 if buzz else 0),-1.82,-1.65,(255,40,40) if buzz else (200,30,30),emit=buzz,xf=W)
    return Q
def gator_podium():
    return box(-0.45,1.05,0,0.85,1.6,4.6,(40,90,150))+box(-0.5,1.1,0.85,0.9,1.55,4.65,(230,200,90))+box(-0.2,0.8,0.25,0.65,1.58,1.59,(90,240,140),emit=True)
def duck_podium():
    return box(2.2,3.0,0,1.05,1.6,2.4,(150,50,90))+box(2.15,3.05,1.05,1.1,1.55,2.45,(230,200,90))+box(2.3,2.9,0.3,0.8,1.58,1.59,(255,240,120),emit=True)+\
           box(2.35,2.85,1.1,1.2,1.75,2.25,(160,40,40))+box(2.38,2.82,1.2,1.3,1.78,2.22,(40,90,160))+box(2.33,2.87,1.3,1.38,1.74,2.26,(220,190,60))
HOST_P=(4.6,0.0,1.0); HOST_YAW=0.93
def lectern():
    Rb=Ry(HOST_YAW); b=np.array(HOST_P)
    return box(-0.35,0.35,0,1.05,-0.75,-0.45,(230,180,40),xf=lambda p:tuple(b+Rb@np.array(p,float)))
AUD=[]
_r=np.random.default_rng(7)
for row,z in enumerate((-2.5,-3.5,-4.5,-5.5)):
    for k in range(17):
        x=-7.2+k*0.9+(0.45 if row%2 else 0)
        if row==0 and abs(x-1.5)<0.5: continue                      # the chicken's seat
        AUD.append((x,z,tuple(int(c) for c in _r.integers(40,140,3)),tuple(int(c) for c in _r.integers(90,200,3)),_r.uniform(0,6)))
def audience(t,laugh=0.0):
    Q=[]
    for (x,z,c1,c2,ph) in AUD:
        y=-0.6+0.02*math.sin(t*2+ph)+0.06*laugh*abs(math.sin(t*11+ph))
        Q+=box(x-0.32,x+0.32,-0.6,-0.15,z-0.25,z+0.25,(50,30,60))                                   # seat
        Q+=box(x-0.18,x+0.18,y+0.4,y+0.95,z-0.12,z+0.12,c2)+box(x-0.11,x+0.11,y+0.97,y+1.2,z-0.11,z+0.11,(180,140,110))+box(x-0.12,x+0.12,y+1.16,y+1.25,z-0.12,z+0.12,c1)
    return Q
CHICK_P=(1.5,-0.15,-2.45)
def banana_pos(t):
    Rb=Ry(TYAW); top=np.array(TB)+Rb@np.array([-0.32,1.9,-1.95])
    if t<49.2: u=(t-48.4)/0.8; y=lerp(7.0,top[1],u*u)
    else: k=t-49.2; y=top[1]+0.25*abs(math.sin(k*9))*math.exp(-k*5)
    return np.array([top[0],y+0.2,top[2]])
def star(d,x,y,r,col):
    d.polygon([(x,y-r),(x+r*0.28,y-r*0.28),(x+r,y),(x+r*0.28,y+r*0.28),(x,y+r),(x-r*0.28,y+r*0.28),(x-r,y),(x-r*0.28,y-r*0.28)],fill=col)
def banana_fx(img,vi,t):
    """legendary-item drop: light beam, glow, rotating rays and twinkling stars around the banana"""
    if not (48.4<=t<50.55) or vi is None: return img
    P=R.project(tuple(banana_pos(t)),vi)
    if not P: return img
    x,y=P[0],P[1]; Wd,Hd=img.size
    lay=Image.new('L',(Wd,Hd),0); d=ImageDraw.Draw(lay)
    if t<49.2:                                                     # sparkle trail while it falls
        for k in range(6):
            tp=t-0.06*(k+1)
            if tp<48.4: break
            q=R.project(tuple(banana_pos(tp)),vi)
            if q: star(d,q[0]+3*math.sin(k*2.1),q[1],3.5-0.4*k,int(230-30*k))
    else:
        u=sm(seg01(t,49.2,49.45)); pulse=0.85+0.15*math.sin(t*14)
        bw=int(14*u); d.polygon([(x-bw*0.6,0),(x+bw*0.6,0),(x+bw,y+6),(x-bw,y+6)],fill=int(70*u))      # beam from above
        for r_,a_ in ((32,45),(24,60),(16,55)):
            r2=int(r_*u*pulse); d.ellipse([x-r2,y-r2,x+r2,y+r2],fill=a_)
        rot=t*2.2
        for k in range(10):                                        # rotating rays
            a=rot+k*2*math.pi/10; L=int((34+10*math.sin(t*9+k))*u); wa=0.07
            r0=10; d.polygon([(x+r0*math.cos(a),y+r0*math.sin(a)),(x+L*math.cos(a-wa),y+L*math.sin(a-wa)),(x+L*math.cos(a+wa),y+L*math.sin(a+wa))],fill=int(150*u))
        for k in range(7):                                         # twinkling stars orbiting
            a=-t*1.6+k*2*math.pi/7; rr=18+5*math.sin(t*3+k); tw=abs(math.sin(t*8+k*1.3))
            star(d,x+rr*math.cos(a),y+rr*0.7*math.sin(a),2+3.5*tw*u,int(255*tw*u))
    a=np.asarray(img).astype(np.float32); m=np.asarray(lay).astype(np.float32)[...,None]/255.0
    a=a*(1-0.35*m)+m*np.array([255,220,90])*1.25
    return Image.fromarray(np.clip(a,0,255).astype(np.uint8))
def banana(t):
    if t<48.4 or t>=56.4: return []
    Rb=Ry(TYAW); top=np.array(TB)+Rb@np.array([-0.32,1.9,-1.95])
    if t<49.2: u=(t-48.4)/0.8; y=lerp(7.0,top[1],u*u); rot=t*9
    else: k=t-49.2; y=top[1]+0.25*abs(math.sin(k*9))*math.exp(-k*5); rot=1.2
    c=np.array([top[0],y+0.07,top[2]]); Q=[]
    for i in range(5):
        a0=-0.9+i*0.36; a1=a0+0.36
        p0=c+Rz(rot)@np.array([0.34*math.sin(a0),-0.34*math.cos(a0)+0.3,0]); p1=c+Rz(rot)@np.array([0.34*math.sin(a1),-0.34*math.cos(a1)+0.3,0])
        glow=t>=49.2
        Q+=seg(p0,p1,0.13-0.015*abs(i-2),((255,236,110) if glow else (250,220,60)) if 0<i<4 else (150,110,40),emit=glow and 0<i<4)
    return Q
# ======================= STORY STATE =======================
SCRIPT=json.load(open('/home/claude/tts/v8/script.json'))
def on(key,t):
    for k,t0,txt,d in SCRIPT:
        if k==key: return t0<=t<t0+d
    return False
def talk_of(prefix,t,sp=22):
    for k,t0,txt,d in SCRIPT:
        if k[0]==prefix and t0<=t<t0+d: return 0.5+0.5*math.sin(t*sp)
    return 0.0
def trex_state(t):
    kw=dict(lean=0.0,neck=0.05,hy=0.0,jaw=0.0,brow=0.0,brow_up=0.0,eye=1.0,look=(0,0),tail=0.15*math.sin(t*1.3),rh=(-0.3,1.95,-1.6),lh=(0.3,1.95,-1.6))
    j=talk_of('T',t,19)
    if j: kw['jaw']=0.25+0.55*j
    if t<5.5: kw['brow']=-0.6; kw['brow_up']=0.4; kw['eye']=1.25; kw['look']=(0.0,0.4*math.sin(t*3))          # nervous under the spotlight
    elif t<11.6: u=sm(seg01(t,7.6,8.2)); kw['brow']=-0.3*(1-u); kw['brow_up']=0.9*u; kw['eye']=1.0+0.35*u; kw['lean']=-0.08*u   # 12 FT?! proud
    elif t<15.0: kw['brow_up']=0.5*abs(math.sin((t-11.6)*7)) if t<12.2 else 0.6; kw['brow']=0.4; kw['lean']=-0.1; kw['eye']=0.85   # smug
    elif t<24.0: kw['hy']=0.45*sm(seg01(t,15.6,16.4)); kw['brow']=0.2
    elif t<25.8: kw['hy']=0.45; kw['eye']=1.6; kw['brow']=-1.0; kw['brow_up']=1.0; kw['jaw']=0.6                           # 4 inches?!
    elif t<33.6: kw['hy']=0.6; kw['brow']=-0.8; kw['brow_up']=0.6; kw['eye']=1.4
    elif t<35.4: kw['brow']=1.3; kw['lean']=0.15; kw['neck']=0.15; kw['eye']=1.2
    elif t<42.6: kw['brow']=0.6; kw['hy']=0.3
    elif t<48.4:
        kw['brow']=1.0; kw['eye']=1.25; kw['brow_up']=0.3
        if 43.9<=t<44.5: u=win(t,43.9,44.5,0.12,0.25); kw['rh']=lerp3((-0.3,1.95,-1.6),(-0.05,1.98,-1.72),u); kw['lean']=0.1*u
    elif t<50.4: kw['eye']=1.5 if t>=49.2 else 1.2; kw['brow']=-0.8; kw['brow_up']=0.8; kw['look']=(0.0,-1.0) if t>=49.2 else (0.0,1.0)
    elif t<56.4: kw['hy']=0.35; kw['brow']=-0.4; kw['brow_up']=0.3; kw['look']=(0.6,-0.6)
    else: kw['brow']=-1.2; kw['brow_up']=1.0; kw['eye']=1.7; kw['lean']=0.1; kw['hy']=0.3
    return kw
def host_state(t):
    kw=dict(eye=1.1,brow=0.3,mouth=0.6*talk_of('H',t,24),out=HOST_OUT)
    yaw=HOST_YAW; kw['rh']=(-0.18,1.25,-0.3)
    if 14.8<=t<17.6: kw['lh']=lerp3((0.22,0.86,-0.05),(0.45,1.4,-0.35),win(t,15.0,17.4,0.2,0.3))
    if 50.4<=t<51.6: yaw=lerp(HOST_YAW,PI*0.85,sm(seg01(t,50.4,50.9)))
    elif t>=51.6: yaw=PI*0.85
    return HOST_P,yaw,kw
def gator_state(t):
    yaw=0.0
    if 31.0<=t<35.4: yaw=-0.75*sm(seg01(t,31.0,32.6))                 # slow deadpan turn to the duck
    return (0.3,0.85,3.0),yaw,dict(jaw=0.35*(0.5+0.5*math.sin(t*9))*on('A1',t),lid=0.55+0.4*(abs(((t*0.6)%3.0)-1.5)<0.06),tail=0.2*math.sin(t*1.1))
def duck_state(t):
    return (2.6,1.38,2.0),-0.55,dict(bob=math.sin(t*9)*(not on('D1',t)),beak=0.6*talk_of('D',t,30),kind='duck',s=1.8,hop=0.06*abs(math.sin(t*12))*(28.6<=t<30.5))
def chick_state(t):
    hy=0.0
    return CHICK_P,PI,dict(bob=math.sin(t*8)*(not on('C1',t)),beak=0.6*talk_of('C',t,30),kind='chicken',s=1.7,hy=hy)
def laugh_at(t):
    return max(win(t,13.4,15.0,0.2,0.6),win(t,28.6,31.5,0.2,0.8),win(t,49.2,50.6,0.15,0.6),0.6*win(t,23.2,24.8,0.2,0.5))
# ======================= SHOTS =======================
R=Renderer(W,H,fog=(16,10,30))
def trex_cam(t,side=0.75,dist=2.6,up=0.25,drop=0.1,fov=46,tgt_drop=0.1):
    """3/4 view on the T-Rex's right side so the eye + eyebrows read (front views only show the snout)"""
    trex(TB,TYAW,t,**trex_state(t)); h=HAND['head']
    f=Ry(TYAW)@np.array([0,0,-1.0]); r=Ry(TYAW)@np.array([-1.0,0,0]); d=f*(1-side*0.5)+r*side; d/=np.linalg.norm(d)
    return 'stage',tuple(h+d*dist+np.array([0,up,0])),tuple(h-np.array([0,tgt_drop,0])),fov
def shot(t):
    if t<3.3: u=sm(seg01(t,0,3.3)); k=trex_cam(t,0.8,lerp(3.4,2.6,u),0.2,fov=lerp(54,46,u),tgt_drop=0.35); return k
    if t<5.5: return 'stage',(0.6,2.9,-6.2),(0.2,2.0,3.0),58
    if t<11.6: return 'screen',None,None,None
    if t<14.8: return trex_cam(t,0.85,2.5,0.15)
    if t<17.6: return 'stage',(3.55,1.85,-0.3),(4.55,1.6,1.0),44
    if t<24.0: return 'stage',(0.85,2.15,-0.55),(0.3,1.1,2.3),50
    if t<25.8: return trex_cam(t,0.95,2.2,0.0)
    if t<31.0: return 'stage',(4.15,2.3,2.45),(2.6,1.95,1.72),46
    if t<33.6: return 'stage',(1.7,1.6,-1.6),(1.4,1.25,2.3),50
    if t<35.4: return trex_cam(t,0.7,2.4,0.1)
    if t<40.3: return 'stage',(3.55,1.85,-0.3),(4.55,1.6,1.0),44
    if t<42.6: return 'screen',None,None,None
    if t<45.0: return trex_cam(t,0.8,3.0,-0.2,fov=50,tgt_drop=0.6)
    if t<48.4: return 'screen',None,None,None
    if t<49.2: return trex_cam(48.4,0.75,3.2,-0.35,fov=52,tgt_drop=0.75)
    if t<50.55: return trex_cam(49.2,0.85,2.5,-0.75,fov=48,tgt_drop=1.15)
    if t<51.6: return 'stage',(3.55,1.85,-0.3),(4.55,1.6,1.0),44
    if t<56.4: return 'stage',(0.55,0.95,-1.35),(1.45,0.6,-2.45),48
    return trex_cam(t,0.9,2.0,0.05,fov=46)
def build(t,cp):
    groups=[]
    def add(Q,D=None):
        if not Q: return
        c=np.mean([q['c'] for q in Q],axis=0); groups.append((np.linalg.norm(c-cp),cull(Q,cp),cull([x for x in (D or []) if np.linalg.norm(x['c']-cp)<np.linalg.norm(x['hc']-cp)],cp)))
    add(*trex(TB,TYAW,t,**trex_state(t)))
    add(trex_podium(t,buzz=44.25<=t<44.9))
    b,y,kw=host_state(t); add(*doc(b,y,t,**kw)); add(lectern())
    b,y,kw=gator_state(t); cq,cd=croc(b,y,t,**kw); add(gator_podium()+cq,cd)
    b,y,kw=duck_state(t); add(*bird(b,y,t,**kw)); add(duck_podium())
    b,y,kw=chick_state(t); add(*bird(b,y,t,**kw))
    add(banana(t))
    groups.sort(key=lambda g:-g[0]); L=[]
    for _,Q,D in groups: L+=[Q,D]
    return L
def lights(t):
    L=[((-2.4,6.5,-0.5),(255,236,200),3.4),((0.3,6.0,0.2),(200,255,220),2.4),((2.6,6.0,0.4),(255,220,240),2.4),((4.4,6.0,-0.6),(255,230,180),2.4),((0,5.0,-3.0),(255,255,255),1.5),
       ((0,3.0,-4.0),(140,120,255),1.2),((0,4.0,6.5),(200,100,255),1.4)]
    if 44.25<=t<45.0: L.append(((-2.9,2.2,1.6),(255,40,40),3.0))
    return L
def find_coeffs(pa,pb):
    A=[]
    for p1,p2 in zip(pa,pb): A.append([p1[0],p1[1],1,0,0,0,-p2[0]*p1[0],-p2[0]*p1[1]]); A.append([0,0,0,p1[0],p1[1],1,-p2[1]*p1[0],-p2[1]*p1[1]])
    Am=np.array(A,float); B=np.array(pb,float).reshape(8); return np.linalg.lstsq(Am,B,rcond=None)[0]
SCR_W,SCR_H=216,128
def render_stage(t,pos,tgt,fov):
    cam=Camera.look(pos,tgt); cp=np.array(pos)
    env=[ST_F,ST_B,ST_W,marquee(t),audience(t,laugh_at(t))]; chars=build(t,cp)
    bias=[1.0]*len(env)+[1.0 if i%2==0 else 1.004 for i in range(len(chars))]     # odd layers = face decals
    img,vi=zrender(R,cam,env+chars,lights(t),fov=fov,fog_start=16,fog_end=40,ambient=0.44,bias=bias)
    a=np.asarray(img); m=(a[...,0]>240)&(a[...,1]<15)&(a[...,2]>240)
    if m.any():                                                        # warp the screen UI onto the big screen (chroma key keeps occlusion)
        corners=[(-2.7,5.1,7.42),(2.7,5.1,7.42),(2.7,1.9,7.42),(-2.7,1.9,7.42)]
        P=[R.project(c,vi) for c in corners]
        ui=screen_ui(t,SCR_W,SCR_H)
        if all(P):
            co=find_coeffs([(p[0],p[1]) for p in P],[(0,0),(SCR_W,0),(SCR_W,SCR_H),(0,SCR_H)])
            warped=ui.transform((W,H),Image.PERSPECTIVE,co,Image.BILINEAR)
            img=Image.composite(warped,img,Image.fromarray((m*255).astype(np.uint8)))
        else:
            img=Image.fromarray(np.where(m[...,None],np.array([20,20,60],np.uint8),a))
    return post.ps1(img),vi
# ======================= SCREEN UI =======================
WHT=(240,240,240); YEL=(255,214,60); RED=(240,50,50); GRN=(70,230,90); GRY=(150,150,160); PNK=(255,90,200); CYA=(90,220,255)
def otext(d,s,x,y,col,sc=1):
    o=max(1,sc//2)
    for ox,oy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)): font.text(d,s,x+ox*o,y+oy*o,(0,0,0),sc,None)
    font.text(d,s,x,y,col,sc,None)
def ctext_w(d,s,y,col,sc,w): otext(d,s,(w-font.width(s,sc))//2,y,col,sc)
def draw_banana(d,cx,cy,s=1.0):
    pts=[(cx-14*s,cy-6*s),(cx-8*s,cy+4*s),(cx,cy+7*s),(cx+9*s,cy+4*s),(cx+15*s,cy-5*s),(cx+11*s,cy-1*s),(cx+2*s,cy+2*s),(cx-6*s,cy+0*s),(cx-11*s,cy-7*s)]
    d.polygon(pts,fill=(250,220,50),outline=(120,90,20)); d.rectangle([cx+13*s,cy-8*s,cx+16*s,cy-5*s],fill=(110,80,30))
def draw_car(d,cx,cy,s=1.0):
    d.rectangle([cx-22*s,cy-4*s,cx+22*s,cy+6*s],fill=(220,60,60),outline=(60,20,20)); d.polygon([(cx-12*s,cy-4*s),(cx-7*s,cy-13*s),(cx+9*s,cy-13*s),(cx+15*s,cy-4*s)],fill=(220,60,60),outline=(60,20,20))
    d.polygon([(cx-9*s,cy-5*s),(cx-6*s,cy-11*s),(cx,cy-11*s),(cx,cy-5*s)],fill=(150,210,240)); d.polygon([(cx+2*s,cy-5*s),(cx+2*s,cy-11*s),(cx+8*s,cy-11*s),(cx+12*s,cy-5*s)],fill=(150,210,240))
    for x in (-12,12): d.ellipse([cx+x*s-5*s,cy+2*s,cx+x*s+5*s,cy+12*s],fill=(20,20,20)); d.ellipse([cx+x*s-2*s,cy+5*s,cx+x*s+2*s,cy+9*s],fill=(160,160,160))
def draw_spiral(d,cx,cy,r,col):
    pts=[(cx+r*(k/40)*math.cos(k*0.5),cy-12+k*0.6) for k in range(40)]
    d.line(pts,fill=col,width=2)
def draw_chicken(d,cx,cy):
    d.ellipse([cx-10,cy-6,cx+10,cy+8],fill=(196,110,52)); d.rectangle([cx+4,cy-14,cx+12,cy-4],fill=(196,110,52)); d.rectangle([cx+6,cy-17,cx+10,cy-14],fill=(220,30,36)); d.polygon([(cx+12,cy-10),(cx+17,cy-8),(cx+12,cy-7)],fill=(250,200,40))
def ui_frame(img,title,col=PNK):
    d=ImageDraw.Draw(img); w,h=img.size
    d.rectangle([0,0,w-1,h-1],outline=col,width=3); d.rectangle([0,0,w,18],fill=col); ctext_w(d,title,6,WHT,1,w); return d
def screen_ui(t,w,h,full=False):
    img=Image.new('RGB',(w,h),(18,14,60)); 
    if t<5.5:
        d=ui_frame(img,"TONIGHT'S QUESTION"); ctext_w(d,'HOW BIG WAS',30,WHT,1,w); ctext_w(d,"T-REX'S",42,YEL,2,w); ctext_w(d,'YOU-KNOW-WHAT?',62,WHT,1,w)
        if int(t*3)%2==0: ctext_w(d,'???',86,RED,3,w)
    elif t<17.5:
        d=ui_frame(img,"SCIENTISTS' ESTIMATES"); d.line([w//2,24,w//2,h-8],fill=(60,50,120),width=2)
        if t>=6.4: draw_banana(d,w//4,58,1.3); ctext_w(d,'LOWER',28,GRY,1,w//2); otext(d,'10 IN',w//4-font.width('10 IN',2)//2,86,YEL,2)
        if t>=7.6: draw_car(d,3*w//4,58,1.15); otext(d,'UPPER',3*w//4-font.width('UPPER')//2,28,GRY,1); otext(d,'12 FT',3*w//4-font.width('12 FT',2)//2,86,RED,2)
        if 8.4<=t: ctext_w(d,'SOMEWHERE BETWEEN',h-14,CYA,1,w)
    elif t<25.8:
        d=ui_frame(img,'RELATIVE #1: ALLIGATOR',GRN); ctext_w(d,'HUNDREDS OF POUNDS',30,WHT,1,w)
        if t<21.4: ctext_w(d,'??? IN',58,GRY,3,w)
        else: ctext_w(d,'4 IN',58,GRN,3,w)
    elif t<31.0:
        d=ui_frame(img,'RELATIVE #2: DUCK',YEL); ctext_w(d,'A FEW POUNDS',30,WHT,1,w)
        if t<27.8: ctext_w(d,'??? IN',58,GRY,3,w)
        else: ctext_w(d,'7 IN',58,YEL,3,w); draw_spiral(d,w-36,72,14,YEL); ctext_w(d,'CORKSCREW!',h-16,GRY,1,w)
    elif t<35.4:
        d=ui_frame(img,'SIZE VS BODY SIZE',CYA)
        otext(d,'GATOR',14,42,GRN,1); d.rectangle([60,42,60+4*16,50],fill=GRN); otext(d,'4 IN',60+4*16+6,42,WHT,1)
        otext(d,'DUCK',14,70,YEL,1); d.rectangle([60,70,60+7*16,78],fill=YEL); otext(d,'7 IN',60+7*16+6,70,WHT,1)
        ctext_w(d,'NO MATCH!',100,RED,1,w)
    elif t<40.3:
        d=ui_frame(img,'FOSSIL RECORD',CYA); ctext_w(d,'BONES:',36,WHT,1,w); ctext_w(d,'FOUND',48,GRN,1,w); ctext_w(d,'SOFT TISSUE:',72,WHT,1,w); ctext_w(d,'ALMOST NEVER',84,RED,1,w); ctext_w(d,'FOSSILIZES',96,RED,1,w)
    elif t<45.0:
        d=ui_frame(img,'FINAL ANSWER',RED); ctext_w(d,'ANSWER:',40,WHT,2,w)
        if int(t*3)%2==0 or t<41.0: ctext_w(d,'UNKNOWN',70,RED,2,w)
    elif t<48.4:
        d=ui_frame(img,'LOCKED IN: THE CAR',RED)
        k=int((t-45.0)*(14-11*seg01(t,45.0,47.4))) if t<47.4 else -1
        if k>=0:
            opt=k%3
            if opt==0: draw_banana(d,w//2,62,1.6)
            elif opt==1: draw_car(d,w//2,62,1.5)
            else: ctext_w(d,'???',50,GRY,3,w)
        else:
            ctext_w(d,'ERROR:',40,RED,2,w); ctext_w(d,'NO FOSSIL',66,WHT,1,w); ctext_w(d,'EVIDENCE',78,WHT,1,w)
    elif t<50.4:
        d=ui_frame(img,'RESULT',RED); d.line([w//2-24,40,w//2+24,96],fill=RED,width=6); d.line([w//2+24,40,w//2-24,96],fill=RED,width=6)
    elif t<56.4:
        d=ui_frame(img,'BONUS: BIRDS',YEL); draw_chicken(d,w//2-40,64)
        if t>=51.8: otext(d,'MOST BIRDS:',w//2-10,48,WHT,1); otext(d,'NONE',w//2-10,62,RED,2)
    else:
        d=ui_frame(img,'???',RED); ctext_w(d,'WHAT?!',52,RED,3,w)
    return img
def screen_full(t):
    ui=screen_ui(t,SCR_W,SCR_H).resize((W-12,int((W-12)*SCR_H/SCR_W)),Image.NEAREST)
    img=Image.new('RGB',(W,H),(14,8,30)); d=ImageDraw.Draw(img)
    y0=(H-ui.height)//2-20; d.rectangle([2,y0-8,W-3,y0+ui.height+8],fill=(70,60,90))
    for k in range(18):
        on=(k+int(t*6))%3==0; x=6+k*9.5; c=(255,220,90) if on else (110,80,40)
        d.rectangle([x,y0-6,x+3,y0-3],fill=c); d.rectangle([x,y0+ui.height+3,x+3,y0+ui.height+6],fill=c)
    img.paste(ui,(6,y0)); a=np.asarray(img).astype(np.float32); a[::2]*=0.85
    return Image.fromarray(a.astype(np.uint8))
# ======================= SUBTITLES / FRAME =======================
SPK={'H':('HOST:',(255,214,60)),'T':('T-REX:',(140,230,90)),'A':('GATOR:',(120,210,150)),'D':('DUCK:',(255,240,140)),'C':('CHICKEN:',(255,150,90))}
HIL={'T-REX\'S..','YOU-KNOW-WHAT?','TWO','BANANA..','CAR!','CAR.','RELATIVES!','HUNDREDS','FOUR','INCHES.','SEVEN','CORKSCREW.','NO','SENSE!','SOFT','TISSUE','NEVER','NOBODY','KNOWS!','CAR!','BIRDS?','DITCHED','LIGHTER','FLYING..','WHAT?!','BODY'}
def subtitle(d,t):
    cur=None
    for k,t0,txt,dd in SCRIPT:
        if t0<=t<t0+dd+0.15: cur=(k,txt)
    if not cur: return
    k,txt=cur; spk=SPK[k[0]]
    words=(spk[0]+' '+txt.upper().replace('...','..')).split(); lines=[]; c=''
    for w_ in words:
        if len(c)+len(w_)+(1 if c else 0)>27: lines.append(c); c=w_
        else: c=(c+' '+w_).strip()
    lines.append(c); y=272-11*(len(lines)-1)
    for ln in lines:
        xw=font.width(ln); x=(W-xw)//2; d.rectangle([x-3,y-2,x+xw+2,y+8],fill=(0,0,0)); cx=x
        for wd in ln.split(' '):
            col=spk[1] if wd==spk[0] else (YEL if wd in HIL else WHT); otext(d,wd,cx,y,col); cx+=font.width(wd)+6
        y+=11
FREEZE=57.6
def frame(t):
    T_=min(t,FREEZE-1e-3)
    kind,pos,tgt,fov=shot(T_)
    if kind=='stage': img,vi=render_stage(T_,pos,tgt,fov); img=banana_fx(img,vi,T_)
    else: img=screen_full(T_)
    if t>=FREEZE:
        a=np.asarray(img).astype(np.float32); g=a.mean(2,keepdims=True); a=0.45*a+0.55*g; img=Image.fromarray(np.clip(a,0,255).astype(np.uint8))
        d=ImageDraw.Draw(img); u=sm(seg01(t,FREEZE,FREEZE+0.25)); y=int(lerp(-30,120,u))
        d.rectangle([14,y,W-15,y+34],fill=(10,0,20),outline=RED); ctext_w(d,'GAME OVER',y+10,RED,2,W)
    d=ImageDraw.Draw(img)
    if t<FREEZE: subtitle(d,T_)
    return img
TEST=os.environ.get('TEST')
if TEST:
    ims=[frame(float(x)) for x in TEST.split(',')]; sh=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): sh.paste(im,(i*182,0))
    sh.resize((sh.width*2,640),Image.NEAREST).save('test.png'); sys.exit()
# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=51); sr=s.sr; n=s.n; t=s.t; M=np.zeros(n)
    def note(buf,t0,m,d,v,wave='sq',duty=0.5,dec=3.0,att=0.004):
        f=440*2**((m-69)/12); tt=s.T(d); ph=(f*tt)%1
        x=np.where(ph<duty,1.0,-1.0) if wave=='sq' else (4*np.abs(ph-0.5)-1 if wave=='tri' else np.sin(2*np.pi*ph))
        env=np.minimum(1,tt/att)*np.exp(-tt*dec); i=int(t0*sr); j=min(n,i+len(tt)); buf[i:j]+=(x*env*v)[:j-i]
    def kick(t0,v=0.15): tt=s.T(0.14); i=int(t0*sr); j=min(n,i+len(tt)); M[i:j]+=(np.sin(2*np.pi*(110-60*tt/0.14)*tt)*np.exp(-tt*22)*v)[:j-i]
    def hat(t0,v=0.02,seed=0): x=s.filt_short(s.noise(0.04,seed),lo=7000)*np.exp(-s.T(0.04)*90); i=int(t0*sr); j=min(n,i+len(x)); M[i:j]+=(x*v)[:j-i]
    def snare(t0,v=0.05,seed=0): x=s.filt_short(s.noise(0.12,seed),lo=1500,hi=7000)*np.exp(-s.T(0.12)*28); i=int(t0*sr); j=min(n,i+len(x)); M[i:j]+=(x*v)[:j-i]
    def blip(t0,f,d=0.06,v=0.035,dec=10): tt=s.T(d); s.place(np.where((f*tt)%1<0.5,1.0,-1.0)*np.exp(-tt*dec),t0,v)
    def bell(t0,f,v=0.06,d=1.2): tt=s.T(d); s.place((np.sin(2*np.pi*f*tt)+0.5*np.sin(2*np.pi*f*2.76*tt)+0.25*np.sin(2*np.pi*f*5.4*tt))*np.exp(-tt*3.5),t0,v)
    def crowd(t0,d,kind,v=0.1,seed=0):
        r=np.random.default_rng(seed); tt=s.T(d); out=np.zeros(len(tt))
        env=np.sin(np.pi*np.clip(tt/d,0,1))**0.6
        if kind in ('ooh','aww'):
            for k in range(14):
                f0=r.uniform(150,300); glide=(1+0.25*tt/d) if kind=='ooh' else (1.15-0.35*tt/d)
                ph=np.cumsum(f0*glide*(1+0.01*np.sin(2*np.pi*r.uniform(4,7)*tt)))/sr; out+=(2*(ph%1)-1)*r.uniform(0.5,1)
            out=s.filt_short(out,lo=180,hi=900 if kind=='ooh' else 1200)
        elif kind=='laugh':
            for k in range(12):
                rate=r.uniform(4.5,7.5); f0=r.uniform(180,420)
                g=np.clip(np.sin(2*np.pi*rate*tt+r.uniform(0,6)),0,1)**2*np.clip(np.sin(np.pi*tt/d*r.uniform(0.8,1.2)),0,1)
                ph=np.cumsum(f0*(1+0.1*np.sin(2*np.pi*rate*tt)))/sr; out+=(np.sin(2*np.pi*ph)*0.6+r.normal(0,0.3,len(tt)))*g
            out=s.filt_short(out,lo=200,hi=3000)
        else:   # applause
            nz=r.normal(0,1,len(tt))*(r.random(len(tt))<0.08); out=s.filt_short(nz,lo=800,hi=6000)
        s.place(out/ (np.abs(out).max()+1e-9)*env,t0,v)
    # ---------- music: game-show theme ----------
    for k,m in enumerate((72,76,79,84)): note(M,0.0+k*0.09,m,0.5,0.06,'sq',0.25,4)                                    # fanfare hit
    note(M,0.0,48,1.5,0.1,'tri',dec=1.2); note(M,0.0,55,1.5,0.05,'tri',dec=1.2); crowd(0.0,1.6,'applause',0.08,1)
    bass=[36,36,43,43,41,41,43,38]; mel=[72,None,74,None,76,79,None,76]
    def groove(a,b,v=1.0,lead=True):
        k=0; tc=a
        while tc<b:
            note(M,tc,bass[k%8],0.22,0.075*v,'tri',dec=5)
            if k%2==0: kick(tc,0.11*v)
            if k%4==2: snare(tc,0.04*v,k)
            hat(tc+0.125,0.014*v,k)
            if lead and mel[k%8] and k%16<8: note(M,tc,mel[k%8],0.2,0.02*v,'sq',0.25,6)
            k+=1; tc+=0.25
    groove(1.0,5.4,0.8); groove(11.6,17.4,0.8); groove(33.6,42.4,0.7,False); groove(50.4,56.3,0.6)
    # ---------- reveals ----------
    crowd(3.2,2.0,'ooh',0.1,2)
    bell(6.4,880,0.07); crowd(6.5,1.0,'ooh',0.05,3)
    for k,f in enumerate((660,880,1320)): bell(7.6+k*0.07,f,0.06)
    crowd(7.7,2.0,'ooh',0.13,4)
    crowd(13.4,1.8,'laugh',0.09,5)
    tt=s.T(0.7); s.place(s.filt_short(s.noise(0.7,6),lo=300,hi=3000)*np.sin(np.pi*tt/0.7),15.3,0.06)                        # spotlight swing
    for a,b in ((20.1,21.35),(26.5,26.98)):                                                                             # drumrolls
        tc=a
        while tc<b: snare(tc,0.03+0.03*(tc-a)/(b-a),int(tc*100)); tc+=0.05
    note(M,21.4,43,0.6,0.08,'sq',0.5,3); note(M,21.65,36,1.0,0.08,'sq',0.5,2)                                           # "4 inches" sad stinger
    crowd(21.9,2.2,'aww',0.12,7); crowd(23.4,1.4,'laugh',0.06,8)
    tt=s.T(0.6); s.place(np.where((np.cumsum(220+600*(tt/0.6))/sr)%1<0.5,1.0,-1.0)*np.exp(-tt*2),24.0,0.03)               # T-Rex double take
    for k,m in enumerate((79,83,86,91)): note(M,27.8+k*0.06,m,0.3,0.05,'sq',0.25,6)                                     # "7 inches" ta-da
    tt=s.T(0.9); s.place(np.sin(2*np.pi*np.cumsum(600+900*np.sin(2*np.pi*3*tt)**2)/sr)*np.exp(-tt*1.5),28.3,0.05)      # corkscrew boing
    crowd(28.6,3.0,'laugh',0.13,9); crowd(28.8,2.5,'applause',0.05,10)
    tt=s.T(1.6); s.place(np.sin(2*np.pi*np.cumsum(90+10*np.sin(2*np.pi*0.7*tt))/sr)*0.4*np.sin(np.pi*tt/1.6),31.0,0.04)  # deadpan head turn creak
    blip(40.4,150,0.35,0.07,1.5); blip(40.8,110,0.6,0.07,1.5); crowd(40.6,1.6,'ooh',0.06,11)                            # UNKNOWN buzzer
    blip(44.3,1046,0.08,0.06,6); blip(44.42,1568,0.15,0.06,4)                                                            # buzzer slam
    tc=45.0; k=0
    while tc<47.4: blip(tc,1200,0.02,0.04,60); tc+=1/(14-11*seg01(tc,45.0,47.4)); k+=1                                 # roulette ticks
    blip(47.45,180,0.5,0.08,1.2); blip(47.9,120,0.7,0.08,1.0)                                                            # WRONG
    tt=s.T(0.8); s.place(np.sin(2*np.pi*np.cumsum(1800-1500*(tt/0.8))/sr)*0.5,48.4,0.07)                                # slide whistle down
    tt=s.T(0.25); s.place((np.sin(2*np.pi*520*tt)+0.6*np.sin(2*np.pi*780*tt))*np.exp(-tt*25),49.2,0.12)                # banana BONK
    # legendary-item shimmer + choir "aaah" when the banana lands
    for k,f in enumerate((1568,1976,2349,2637,3136,3951)): bell(49.22+k*0.07,f,0.035,0.9)
    tt=s.T(1.4); ch=sum(np.sin(2*np.pi*f*tt*(1+0.004*np.sin(2*np.pi*5.5*tt+k)))/(1+k*0.3) for k,f in enumerate((392,494,587,784)))
    s.place(s.filt_short(ch,hi=2500)*np.minimum(1,tt/0.15)*np.exp(-np.maximum(0,tt-0.9)*4),49.25,0.07)
    crowd(49.6,1.6,'laugh',0.12,12)
    crowd(55.0,1.2,'ooh',0.07,13)
    # final: silence, then GAME OVER
    M[int(56.35*sr):]=0
    for k,f in enumerate((523,392,262)): blip(57.65+k*0.16,f,0.15 if k<2 else 0.5,0.07,4)
    crowd(57.7,1.3,'ooh',0.09,14)
    # ---------- voices ----------
    NB=np.zeros(n); duck=np.ones(n)
    for k_,t0,txt,dd in SCRIPT:
        a,ar=_sf.read(f'/home/claude/tts/v8/{k_}.wav'); a=a if a.ndim==1 else a.mean(1)
        g_=0.6 if k_[0]=='T' else 0.95
        i=int(t0*sr); j=min(n,i+len(a)); NB[i:j]+=a[:j-i]*g_
        duck[max(0,i-int(0.06*sr)):min(n,j+int(0.12*sr))]=0.4
    duck=np.convolve(duck,np.ones(2000)/2000,'same')
    s.L+=M*duck; s.R+=M*duck
    hum=s.filt(s.rng.normal(0,1,n),lo=100,hi=1500)*0.008; s.L+=hum; s.R+=hum
    s.reverb(0.12,length=0.9,decay=5)
    pk=max(np.abs(s.L).max(),np.abs(s.R).max()); gv=pk*1.0/np.abs(NB).max()
    s.L=s.L*(0.6+0.4*duck)+NB*gv; s.R=s.R*(0.6+0.4*duck)+NB*gv
    return s.save(path,peak=0.9)
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'gameshow.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','20','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'gs_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.95,vignette=0.25,grain=1.6,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(post.upscale(frame(f/FPS),S),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
