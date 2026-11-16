"""THE CHEST THAT SCAMMED ME - 60 s PS1 pirate-shop comedy, 9:16. Fully procedural (nightkit).
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
FPS=24; W,H,S=180,320,6; DUR=59.6; N=int(DUR*FPS)
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
# ======================= THE ADVENTURER (player) =======================
SKIN=(236,196,166); HOOD=(236,96,156); HOOD_D=(196,70,126); SHORTS=(40,40,56); HAIR=(64,214,206); HAIR_D=(36,160,156)
BOOT=(122,78,44); SOCK=(236,236,236); STEEL=(176,182,196); STEEL_D=(130,136,150); PACK=(250,206,40); PACK_D=(206,160,20); LEATH=(90,58,34); GOLD=(240,196,40)
ALL_GEAR={'sword','armor','boots','pack'}
def hero(base,yaw,t=0.0,walk=0.0,run=0.0,rh=None,lh=None,lean=0.0,hy=0.0,hp=0.0,eye=1.0,brow=0.0,mouth=0.0,smile=0.0,gear=ALL_GEAR,crouch=0.0):
    """faces -z at yaw 0. gear decides which sellable items are still on her."""
    b=np.array(base,float); Rb=Ry(yaw)
    def W(p): return tuple(b+Rb@np.array(p,float))
    hip=0.78-0.28*crouch
    def WL(p): p=np.array(p,float)+np.array([0,hip-0.78,0]); piv=np.array([0,hip,0]); return W(piv+Rx(-(lean+0.25*run+0.3*crouch))@(p-piv))
    Q=[];D=[]; amp=0.45+0.3*run; sw=amp*math.sin(walk)
    for sx,ph in ((-1,1),(1,-1)):
        hp_=np.array([sx*0.085,hip,0]); a=ph*sw
        if crouch>0: ft=np.array([sx*0.11,0.05,-0.12*crouch]); kn=np.array([sx*0.1,hip*0.5+0.12*crouch,-0.3*crouch])
        else:
            ft=hp_+np.array([0,-0.74*math.cos(a),-0.74*math.sin(a)]); ft[1]=max(0.05,ft[1]+0.07*max(0,math.sin(walk*ph+PI/2))*(1 if walk else 0)); kn=(hp_+ft)/2+np.array([0,0,-0.05-0.06*run])
        mid=hp_+(kn-hp_)*0.45
        Q+=transform(seg(hp_,mid,0.13,SHORTS)+seg(mid,kn,0.1,SKIN),W)
        if 'boots' in gear:
            bt=kn+(ft-kn)*0.35; Q+=transform(seg(kn,bt,0.09,SKIN)+seg(bt,ft,0.12,BOOT)+box(ft[0]-0.06,ft[0]+0.06,ft[1]-0.05,ft[1]+0.04,ft[2]-0.13,ft[2]+0.05,BOOT),W)
        else:
            Q+=transform(seg(kn,ft,0.09,SKIN)+box(ft[0]-0.05,ft[0]+0.05,ft[1]-0.05,ft[1]+0.02,ft[2]-0.12,ft[2]+0.04,SOCK),W)
    Q+=box(-0.16,0.16,0.76,1.28,-0.1,0.1,HOOD,xf=WL)+box(-0.13,0.13,1.12,1.3,0.08,0.15,HOOD_D,xf=WL)          # hoodie + hood
    D+=box(-0.09,0.09,0.82,0.94,-0.106,-0.1,HOOD_D,xf=WL)                                                           # pocket
    if 'armor' in gear:
        Q+=box(-0.15,0.15,0.95,1.26,-0.14,-0.095,STEEL,xf=WL)+box(-0.16,0.16,0.9,0.96,-0.13,0.11,LEATH,xf=WL)
        for sx in (-1,1): Q+=box(sx*0.22-0.08,sx*0.22+0.08,1.2,1.3,-0.1,0.1,STEEL_D,xf=WL)
    if 'sword' in gear:
        Q+=transform(seg((0.2,0.92,-0.02),(0.25,0.42,0.12),0.06,LEATH)+seg((0.19,0.92,-0.02),(0.17,1.06,-0.06),0.04,GOLD)+seg((0.13,0.95,-0.04),(0.26,0.93,0.0),0.035,GOLD),WL)
    if 'pack' in gear:
        Q+=box(-0.15,0.15,0.82,1.22,0.1,0.27,PACK,xf=WL)+box(-0.15,0.15,1.12,1.24,0.09,0.28,PACK_D,xf=WL)+box(-0.06,0.06,0.9,1.0,0.27,0.29,PACK_D,xf=WL)
        for sx in (-1,1): D+=box(sx*0.1-0.025,sx*0.1+0.025,0.98,1.28,-0.108,-0.1,PACK,xf=WL)
    hc=np.array([0,1.45,0])
    def WH(p): p=np.array(p,float); return WL(hc+Ry(hy)@Rx(-hp)@(p-hc))
    Q+=box(-0.045,0.045,1.27,1.34,-0.045,0.045,SKIN,xf=WL)+box(-0.095,0.095,1.33,1.56,-0.1,0.09,SKIN,xf=WH)
    Q+=box(-0.11,0.11,1.5,1.64,-0.11,0.11,HAIR,xf=WH)+box(-0.11,0.11,1.36,1.52,0.05,0.11,HAIR,xf=WH)                    # short bob
    for sx in (-1,1): Q+=box(sx*0.095-0.017,sx*0.095+0.017,1.38,1.52,-0.08,0.1,HAIR,xf=WH)
    D+=box(-0.1,0.06,1.49,1.53,-0.106,-0.098,HAIR,xf=WH)+box(0.03,0.1,1.47,1.53,-0.106,-0.098,HAIR,xf=WH)                # fringe
    for sx in (-1,1):
        x=sx*0.043; e=0.022*eye
        D+=box(x-0.024,x+0.024,1.45-e,1.45+e,-0.104,-0.099,(250,250,250),xf=WH)
        D+=box(x-0.014+0.006*sx*0,x+0.014,1.45-min(e,0.017),1.45+min(e,0.017)*0.8,-0.108,-0.104,(40,90,120),xf=WH)
        D+=box(x-0.027,x+0.027,1.45+e,1.45+e+0.008,-0.108,-0.1,(30,24,30),xf=WH)                                            # lash line
        by=1.495+0.01*(eye-1); bt=brow
        D+=transform(seg((x-sx*0.025,by+0.007*bt,-0.105),(x+sx*0.022,by-0.009*bt,-0.105),0.011,HAIR_D,depth=0.004),WH)
        D+=box(x-0.02,x+0.02,1.395,1.41,-0.103,-0.099,(255,150,170),xf=WH)                                                    # blush
    if smile>0.5 and mouth<0.3:
        for k in range(5): xx=-0.03+0.015*k; yy=1.375+0.006*abs(k-2)*smile; D+=box(xx-0.008,xx+0.008,yy-0.004,yy+0.004,-0.106,-0.099,(140,50,60),xf=WH)
    else:
        mh=0.008+0.035*mouth; D+=box(-0.02+0.006*mouth,0.02-0.006*mouth,1.375-mh/2,1.375+mh/2,-0.106,-0.099,(140,50,60),xf=WH)
    for sx,hd in ((-1,rh),(1,lh)):
        if hd is None: s_=-sx*amp*0.7*math.sin(walk)*(1 if walk else 0); hd=(sx*0.22,0.8+0.06*abs(s_)+0.15*run,-0.3*s_-0.1*run)
        sh=np.array(WL((sx*0.22,1.24,0))); hw=np.array(WL(hd)); el=elbow(sh,hw,tuple(Rb@np.array([sx*0.6,0,-0.15])),0.52)
        Q+=seg(sh,el,0.09,HOOD)+seg(el,hw,0.08,HOOD)+obox(hw,(0.04,0.045,0.04),Rb,SKIN)
    hcW=np.array(WH((0,1.45,0))); tcW=np.array(WL((0,1.05,0)))
    for q in D: q['hc']=hcW if q['c'][1]>hcW[1]-0.13 else tcW
    return Q,D
# ======================= CHESTER =======================
WOOD=(150,92,44); WOOD_D=(110,64,28); IRON=(120,124,134); BLK=(24,22,26)
def chester(base,yaw,t=0.0,lid=0.0,eye=1.0,smug=0.0,look=(0.0,0.0),mouth='smile',talk=0.0,hop=0.0,glow=0.0,scale=1.0):
    """original talking treasure chest: big cartoon eyes on the front, smile, iron corners, tiny pirate hat on the lid"""
    b=np.array(base,float)+np.array([0,hop,0]); Rb=Ry(yaw)
    def W(p): return tuple(b+Rb@(np.array(p,float)*scale))
    hp=np.array([0,0.42,0.24])
    def WLd(p): p=np.array(p,float); return W(hp+Rx(-1.7*lid)@(p-hp))
    Q=[];D=[]
    Q+=box(-0.36,0.36,0.0,0.42,-0.24,0.24,WOOD,xf=W)
    for y in (0.13,0.27): D+=box(-0.36,0.36,y-0.008,y+0.008,-0.246,-0.24,WOOD_D,xf=W)
    for sx in (-1,1):
        for sz in (-1,1): Q+=box(sx*0.36-sx*0.05,sx*0.36+sx*0.01,0.0,0.42,sz*0.24-sz*0.05,sz*0.24+sz*0.01,IRON,xf=W)
    if glow>0 or lid>0.05: Q+=box(-0.32,0.32,0.36,0.41,-0.2,0.2,(255,226,90),emit=True,xf=W)                          # gold inside
    Q+=box(-0.37,0.37,0.42,0.6,-0.25,0.25,WOOD,xf=WLd)+box(-0.37,0.37,0.5,0.53,-0.255,0.255,IRON,xf=WLd)
    D+=box(-0.06,0.06,0.44,0.56,-0.262,-0.25,GOLD,xf=WLd)                                                                # lock plate
    # tiny pirate hat on the lid
    Q+=box(-0.2,0.2,0.6,0.64,-0.12,0.12,BLK,xf=WLd)+box(-0.12,0.12,0.64,0.74,-0.08,0.08,BLK,xf=WLd)
    D+=box(-0.2,0.2,0.635,0.645,-0.125,-0.12,GOLD,xf=WLd)+box(-0.025,0.025,0.67,0.71,-0.085,-0.08,(240,240,240),xf=WLd)
    # face on the front
    for sx in (-1,1):
        x=sx*0.13; e=0.085*eye
        D+=box(x-0.085,x+0.085,0.27-e,0.27+e,-0.252,-0.24,(250,250,246),xf=W)
        px=x+0.035*look[0]; py=0.27+0.03*look[1]; pe=min(e,0.045)
        D+=box(px-0.04,px+0.04,py-pe,py+pe,-0.258,-0.252,(18,18,22),xf=W)
        D+=box(px+0.008,px+0.024,py+0.012,py+0.028,-0.262,-0.258,(255,255,255),xf=W)
        if smug>0: D+=box(x-0.088,x+0.088,0.27+e-2*e*smug*0.55,0.27+e+0.004,-0.264,-0.256,WOOD_D,xf=W)                   # half-lidded smug eyes
    if mouth=='o' or talk>0.05:
        h_=0.03+0.07*max(talk,1.0 if mouth=='o' else 0); w_=0.06 if mouth=='o' else 0.1
        D+=box(-w_,w_,0.1-h_/2,0.1+h_/2,-0.252,-0.24,(70,20,24),xf=W)
    elif mouth=='smirk':
        for k in range(6): xx=-0.1+0.04*k; yy=0.08+0.012*k; D+=box(xx-0.022,xx+0.022,yy-0.01,yy+0.01,-0.252,-0.24,(60,20,20),xf=W)
    else:
        for k in range(7): xx=-0.15+0.05*k; yy=0.07+0.0055*(k-3)**2; D+=box(xx-0.028,xx+0.028,yy-0.012,yy+0.012,-0.252,-0.24,(60,20,20),xf=W)
    hcW=np.array(W((0,0.25,0)))
    return Q,tagD(D,hcW)
# ======================= SKELETON PIRATE =======================
BONE=(232,228,210); COATR=(176,34,40); COATR_D=(130,24,30)
def skeleton(base,yaw,t=0.0,walk=0.0,rh=None,lh=None,hy=0.0,hp=0.0,jaw=0.0,lean=0.0):
    b=np.array(base,float); Rb=Ry(yaw)
    def W(p): return tuple(b+Rb@np.array(p,float))
    hip=0.92
    def WL(p): p=np.array(p,float); piv=np.array([0,hip,0]); return W(piv+Rx(-lean)@(p-piv))
    Q=[];D=[]; sw=0.35*math.sin(walk)
    for sx,ph in ((-1,1),(1,-1)):
        hp_=np.array([sx*0.09,hip,0]); a=ph*sw; ft=hp_+np.array([0,-0.86*math.cos(a),-0.86*math.sin(a)]); ft[1]=max(0.06,ft[1]); kn=(hp_+ft)/2+np.array([0,0,-0.04])
        bt=kn+(ft-kn)*0.2
        Q+=transform(seg(hp_,kn,0.05,BONE)+seg(kn,bt,0.05,BONE)+seg(bt,ft,0.15,BLK)+box(ft[0]-0.07,ft[0]+0.07,ft[1]-0.06,ft[1]+0.05,ft[2]-0.16,ft[2]+0.06,BLK),W)
    Q+=box(-0.19,0.19,0.95,1.46,-0.11,0.11,COATR,xf=WL)+box(-0.21,0.21,0.55,0.98,0.0,0.12,COATR_D,xf=WL)
    D+=box(-0.07,0.07,1.0,1.42,-0.118,-0.11,(40,30,30),xf=WL)                                                    # open coat
    for k in range(4): D+=box(-0.06,0.06,1.12+0.07*k,1.14+0.07*k,-0.122,-0.118,BONE,xf=WL)                    # ribs
    for k in range(3):
        for sx in (-1,1): D+=box(sx*0.11-0.015,sx*0.11+0.015,1.1+0.1*k,1.13+0.1*k,-0.12,-0.11,GOLD,xf=WL)
    hc=np.array([0,1.62,0])
    def WH(p): p=np.array(p,float); return WL(hc+Ry(hy)@Rx(-hp)@(p-hc))
    Q+=transform(seg((0,1.44,0),(0,1.52,0),0.05,BONE),WL)
    Q+=box(-0.12,0.12,1.56,1.8,-0.12,0.11,BONE,xf=WH)
    jp=np.array([0,1.57,-0.02])
    def WJ(p): p=np.array(p,float); return WH(jp+Rx(0.5*jaw)@(p-jp))
    Q+=box(-0.09,0.09,1.49,1.57,-0.11,0.06,BONE,xf=WJ)
    for sx in (-1,1): D+=box(sx*0.05-0.035,sx*0.05+0.035,1.65,1.72,-0.128,-0.12,BLK,xf=WH)
    D+=box(-0.015,0.015,1.6,1.63,-0.128,-0.12,BLK,xf=WH)
    for k in range(5): D+=box(-0.06+0.03*k-0.008,-0.06+0.03*k+0.008,1.57,1.6,-0.124,-0.118,BLK,xf=WH)
    Q+=box(-0.32,0.32,1.78,1.83,-0.24,0.24,BLK,xf=WH)+box(-0.16,0.16,1.83,2.0,-0.14,0.14,BLK,xf=WH)                 # oversized tricorn
    for sx in (-1,1): Q+=box(sx*0.32-0.05,sx*0.32+0.05,1.8,1.92,-0.24,0.24,BLK,xf=WH)
    D+=box(-0.32,0.32,1.825,1.84,-0.245,-0.24,GOLD,xf=WH)+box(-0.04,0.04,1.88,1.95,-0.146,-0.14,(240,240,240),xf=WH)
    for sx,hd in ((-1,rh),(1,lh)):
        if hd is None: s_=-sx*0.25*math.sin(walk)*(1 if walk else 0); hd=(sx*0.24,0.95,-0.25*s_-0.05)
        sh=np.array(WL((sx*0.24,1.4,0))); hw=np.array(WL(hd)); el=elbow(sh,hw,tuple(Rb@np.array([sx*0.6,0,-0.15])),0.6)
        Q+=seg(sh,el,0.11,COATR)+seg(el,hw,0.045,BONE)+obox(hw,(0.04,0.04,0.04),Rb,BONE)
    hcW=np.array(WH((0,1.66,0))); tcW=np.array(WL((0,1.15,0)))
    for q in D: q['hc']=hcW if q['c'][1]>hcW[1]-0.12 else tcW
    return Q,D
# ======================= PIRATE SHOP (one set) =======================
KEY=(255,0,255)
PLANK=lambda i,j:[(122,80,46),(108,70,40),(132,88,52),(100,64,36)][(j*3+(i//3))%4]
WALLP=lambda i,j:[(96,62,38),(86,56,34),(104,68,42)][(i+j*2)%3]
X0,X1,Z0,Z1,YC=-4.0,4.0,-2.5,5.0,3.2
DOOR_Z=(1.2,2.3); DOOR_H=2.2
def shop_static():
    F=tiled_plane(X0,X1,Z0,Z1,0,0.5,PLANK)
    Wq=[]
    def wall_x(x,hole=None):
        Q=[]
        for i,z in enumerate(np.arange(Z0,Z1,0.5)):
            for j,y in enumerate(np.arange(0,YC,0.8)):
                za,zb,ya,yb=z,min(Z1,z+0.5),y,min(YC,y+0.8)
                if hole and za>=hole[0]-1e-6 and zb<=hole[1]+1e-6 and ya<hole[2]-1e-6:
                    if yb<=hole[2]+1e-6: continue
                    ya=hole[2]
                Q.append(quad([(x,ya,za),(x,ya,zb),(x,yb,zb),(x,yb,za)],WALLP(i,j)))
        return Q
    def wall_z(z,hole=None):
        Q=[]
        for i,x in enumerate(np.arange(X0,X1,0.5)):
            for j,y in enumerate(np.arange(0,YC,0.8)):
                xa,xb,ya,yb=x,min(X1,x+0.5),y,min(YC,y+0.8)
                if hole and xa>=hole[0]-1e-6 and xb<=hole[1]+1e-6 and ya<hole[2]-1e-6:
                    if yb<=hole[2]+1e-6: continue
                    ya=hole[2]
                Q.append(quad([(xa,ya,z),(xb,ya,z),(xb,yb,z),(xa,yb,z)],WALLP(i+1,j)))
        return Q
    Wq+=wall_x(X0,hole=(1.0,2.5,2.4))+wall_x(X1)+wall_z(Z1,hole=(2.0,3.0,2.4))
    Wq+=tiled_plane(X0,X1,Z0,Z1,YC,1.0,lambda i,j:(70,46,28))
    P=[]
    for z in (-1.0,1.0,3.0): P+=box(X0,X1,YC-0.25,YC,z-0.12,z+0.12,(78,50,30))                                  # ceiling beams
    P+=box(X0,X0+0.08,0,2.4,0.9,1.2,(70,44,26))+box(X0,X0+0.08,0,2.4,2.3,2.6,(70,44,26))+box(X0,X0+0.08,2.2,2.5,1.0,2.5,(70,44,26))   # door frame
    P.append(quad([(X0-0.6,0,1.2),(X0-0.6,0,2.3),(X0-0.6,2.2,2.3),(X0-0.6,2.2,1.2)],(250,240,200),emit=True))                          # daylight outside
    P+=tiled_plane(X0-0.6,X0,1.2,2.3,0.002,0.3,lambda i,j:(230,220,170))
    # sign "FREE LEGENDARY LOOT" next to Chester (chroma keyed, text warped in later)
    P+=box(0.98,1.06,0,1.3,1.75,1.83,(90,58,34))+box(0.4,1.64,1.22,1.82,1.82,1.86,(90,58,34))
    P.append(quad([(0.46,1.27,1.81),(1.58,1.27,1.81),(1.58,1.77,1.81),(0.46,1.77,1.81)],KEY,emit=True))
    # weapon rack on the right wall
    P+=box(3.9,3.97,0.8,2.1,1.3,2.9,(84,54,32))
    P+=seg((3.86,0.95,1.6),(3.86,1.85,1.6),0.05,(110,80,50))+box(3.83,3.88,1.65,1.95,1.45,1.6,(150,150,160))      # axe
    P+=seg((3.86,0.9,2.65),(3.86,1.95,2.65),0.04,(120,80,40))                                                     # bow-ish staff
    # shop counter at the back + curtain doorway
    P+=box(1.6,3.4,0,0.95,3.7,4.3,(120,78,44))+box(1.55,3.45,0.95,1.02,3.65,4.35,(150,100,58))+box(2.2,2.8,0.35,0.7,3.68,3.7,(150,110,46))
    # treasure piles, barrels, crates
    rng=np.random.default_rng(3)
    for (cx,cz,n) in ((-3.1,4.1,26),(-2.4,4.5,18),(3.3,0.2,20),(-3.3,-1.2,12)):
        for k in range(n):
            x=cx+rng.normal(0,0.25); z=cz+rng.normal(0,0.2); y=max(0,0.35-0.5*math.hypot(x-cx,z-cz))*rng.random()
            P+=box(x-0.05,x+0.05,y,y+0.03,z-0.05,z+0.05,(250,206,50) if k%3 else (230,180,40),emit=k%5==0)
    for (x,z) in ((-3.4,3.2),(3.4,-1.6),(-1.9,4.5),(3.5,4.6)):
        P+=box(x-0.32,x+0.32,0,0.85,z-0.32,z+0.32,(120,76,40))
        for y in (0.15,0.7): P+=box(x-0.33,x+0.33,y,y+0.05,z-0.33,z+0.33,IRON)
    P+=box(-3.6,-2.9,0,0.6,-0.4,0.3,(140,100,60))+box(-3.55,-3.0,0.6,1.05,-0.3,0.2,(150,108,64))
    # magic gear on the walls/floor for the "vault" look
    P+=seg((-3.9,1.0,3.6),(-3.9,1.8,3.9),0.05,(100,200,255),emit=True)+seg((3.9,2.3,0.0),(3.9,2.8,0.6),0.05,(200,120,255),emit=True)
    return F,Wq,P
SHOP_F,SHOP_W,SHOP_P=shop_static()
LANTERNS=[(-2.0,2.6,0.8),(1.4,2.6,0.6),(0.2,2.6,3.6),(3.0,2.6,2.6)]
def lanterns(t):
    Q=[]
    for k,(x,y,z) in enumerate(LANTERNS):
        Q+=seg((x,YC-0.25,z),(x,y+0.2,z),0.02,(40,30,20))+box(x-0.1,x+0.1,y-0.15,y+0.15,z-0.1,z+0.1,(255,190,90),emit=True)+box(x-0.12,x+0.12,y+0.15,y+0.2,z-0.12,z+0.12,(40,30,24))
    return Q
def door_angle(st):
    if st<28.4: return 1.35                                              # left open after she walked in
    if st<28.55: return 1.35*(1-seg01(st,28.4,28.55))                    # SLAM
    if st<53.0: return 0.0
    return 1.5*sm(seg01(st,53.0,53.6))
def door(st):
    a=door_angle(st); hz=DOOR_Z[0]
    def Tf(p): p=np.array(p,float)-np.array([X0,0,hz]); return tuple(Ry(-a)@p+np.array([X0,0,hz]))
    Q=transform(box(0.0,0.07,0,DOOR_H,0.0,DOOR_Z[1]-hz,(110,70,36))+box(0.0,0.09,0.4,0.48,0.0,DOOR_Z[1]-hz,IRON)+box(0.0,0.09,1.7,1.78,0.0,DOOR_Z[1]-hz,IRON)+box(0.07,0.12,1.0,1.1,0.85,0.95,GOLD),lambda p:Tf((p[0]+X0,p[1],p[2]+hz)))
    locked=28.45<=st<53.2
    if locked:
        lift=sm(seg01(st,52.95,53.2))
        Q+=box(X0+0.1,X0+0.18,1.1+0.6*lift,1.22+0.6*lift,DOOR_Z[0]-0.05,DOOR_Z[1]+0.05,IRON)
        Q+=box(X0+0.16,X0+0.26,0.9+0.6*lift,1.16+0.6*lift,1.6,1.9,(230,40,40),emit=True)
    return Q
def sword(st):
    if st>=53.6: pass
    return box(3.82,3.87,1.0,1.18,2.05,2.15,GOLD)+box(3.82,3.88,1.18,1.21,1.95,2.25,GOLD)+box(3.83,3.86,1.21,1.85,2.06,2.14,(120,240,255),emit=True)
def curtain(st):
    u=sm(seg01(st,49.9,50.4))*(1-sm(seg01(st,50.9,51.3)))
    Q=[]
    for k in range(4):
        x0=2.0+k*0.25; x1=x0+0.25; off=(-0.35 if k<2 else 0.35)*u
        Q.append(quad([(x0+off,0,Z1-0.02),(x1+off,0,Z1-0.02),(x1+off,2.4,Z1-0.02),(x0+off,2.4,Z1-0.02)],(170,30,40) if k%2 else (140,20,30)))
    return Q
# ======================= STORY STATE =======================
SCRIPT=json.load(open('/home/claude/tts/v9/script.json'))
def on(key,t):
    for k,t0,txt,d in SCRIPT:
        if k==key: return t0<=t<t0+d
    return False
def talk(key,t,sp=24): return (0.5+0.5*math.sin(t*sp)) if on(key,t) else 0.0
class Path:
    def __init__(s,K,stride=0.62):
        s.K=K; s.stride=stride; ts=np.arange(0,61,1/48); P=np.array([s.pos(t) for t in ts]); s.ts=ts; s.D=np.r_[0,np.cumsum(np.linalg.norm(np.diff(P,axis=0),axis=1))]
    def pos(s,t):
        K=s.K
        if t<=K[0][0]: return np.array(K[0][1],float)
        for (a,pa),(b,pb) in zip(K,K[1:]):
            if t<b: return np.array(pa,float)+(np.array(pb,float)-np.array(pa,float))*((t-a)/(b-a))
        return np.array(K[-1][1],float)
    def phase(s,t): i=int(np.clip(t*48,0,len(s.D)-1)); return s.D[i]/s.stride*PI
    def moving(s,t): return np.linalg.norm(s.pos(t+0.04)-s.pos(t-0.04))>0.003
    def heading(s,t):
        d=s.pos(t+0.06)-s.pos(t-0.06); return math.atan2(-d[0],-d[1]) if np.linalg.norm(d)>1e-3 else None
AT_CHEST=(-0.75,1.05); AT_SWORD=(3.15,2.1); AT_DOOR=(-3.5,1.75); AT_COUNTER=(2.5,3.1)
PP=Path([(0,(-5.4,1.75)),(4.6,(-5.2,1.75)),(8.0,AT_CHEST),(17.8,AT_CHEST),(20.4,AT_SWORD),(27.0,AT_SWORD),(27.6,(1.2,0.9)),(28.35,AT_DOOR),
         (30.8,AT_DOOR),(32.2,AT_CHEST),(47.9,AT_CHEST),(49.4,AT_COUNTER),(53.7,AT_COUNTER),(54.2,(1.0,1.5)),(54.9,AT_DOOR),(55.4,(-5.6,1.75)),(60,(-5.6,1.75))])
Y_CHEST=math.atan2(-0.75,-0.95)
def yaw_of(t):
    h=PP.heading(t)
    if h is not None and PP.moving(t): return h
    if t<17.8: return Y_CHEST
    if t<22.9: return -PI/2
    if t<27.0: return lerp(-PI/2,PI/2-0.03,sm(seg01(t,22.9,23.2)))
    if t<29.8: return PI/2
    if t<31.0: return lerp(PI/2,-PI/2-0.07,sm(seg01(t,29.8,30.2)))
    if t<47.9: return Y_CHEST
    if t<53.7: return PI
    return PI/2
def gear_at(t):
    g=set(ALL_GEAR)
    for name,ts in (('sword',32.6),('armor',34.4),('boots',36.2),('pack',38.0)):
        if t>=ts: g.discard(name)
    return g
SALES=[('sword',32.6,250),('armor',34.4,500),('boots',36.2,750),('pack',38.0,999)]
def gold_at(t):
    g=0
    for n,ts,v in SALES:
        if t>=ts+0.5: g=v
    if t>=39.7: g=int(999*(1-sm(seg01(t,39.7,40.4))))
    if t>=51.3: g=1
    if t>=52.6: g=0
    return g
def hero_state(t,hook=False):
    p=PP.pos(t); ph=PP.phase(t) if PP.moving(t) else 0.0
    running=(27.0<=t<28.4) or (53.7<=t<55.4)
    kw=dict(walk=ph,run=1.0 if running else 0.0,gear=gear_at(t),eye=1.0,brow=0.0,mouth=0.0,smile=0.0)
    if t<8.0: kw['lh']=(0.12,1.05,-0.32); kw['rh']=(-0.12,1.05,-0.32); kw['hp']=0.25                                 # reading the map
    elif t<12.0: kw['smile']=1.0; kw['eye']=1.15; kw['brow']=0.5; kw['hp']=0.1*math.sin(t*3)
    elif t<15.6:
        u=win(t,12.0,13.0,0.3,0.4); kw['crouch']=0.6*u; kw['rh']=lerp3((-0.22,0.8,-0.1),(-0.1,0.55,-0.45),u); kw['lh']=lerp3((0.22,0.8,-0.1),(0.1,0.55,-0.45),u)
        kw['eye']=1.4 if t>=12.5 else 1.0; kw['mouth']=0.6 if t>=12.5 else 0.0
    elif t<17.8: kw['smile']=1.0; kw['eye']=1.2; kw['rh']=(-0.3,1.6,-0.05) if int(t*4)%2 else (-0.25,1.4,-0.1); kw['lh']=(0.3,1.6,-0.05)   # cheering
    elif t<22.9:
        kw['eye']=1.3; kw['smile']=1.0
        if t>=21.0: kw['rh']=lerp3((-0.22,0.8,-0.1),(-0.1,1.35,-0.55),sm(seg01(t,21.0,21.8)))
        if t>=22.4: kw['eye']=1.6; kw['smile']=0.0; kw['mouth']=0.6
    elif t<27.0: kw['brow']=1.2; kw['mouth']=0.8*talk('P2',t,22); kw['rh']=(-0.3,1.25,-0.3) if on('P2',t) else None; kw['eye']=1.1
    elif t<28.4: kw['eye']=1.4; kw['brow']=-0.5; kw['mouth']=0.4
    elif t<29.8:                                                                         # yanking the door handle
        y=math.sin(t*16); kw['rh']=(-0.08,1.05,-0.48-0.06*y); kw['lh']=(0.08,1.05,-0.48-0.06*y); kw['lean']=-0.15+0.06*y; kw['eye']=1.5; kw['brow']=-1.0; kw['mouth']=0.5
        if hook and on('P1',t-28.15): kw['mouth']=talk('P1',t-28.15,24)
    elif t<31.2: kw['eye']=0.8; kw['brow']=1.0; kw['mouth']=0.0                          # the stare (awkward silence)
    elif t<39.4: kw['brow']=-0.6; kw['eye']=1.0; kw['mouth']=0.2
    elif t<40.5: kw['eye']=0.7; kw['smile']=1.0; kw['lean']=0.12; kw['rh']=(-0.1,1.05,-0.45); kw['lh']=(0.1,1.05,-0.45)  # pays
    elif t<45.3: kw['eye']=0.6+0.8*(t>=41.6); kw['brow']=-1.0 if t>=41.6 else 0.0; kw['mouth']=0.4 if t>=41.6 else 0.0
    elif t<47.9: u=sm(seg01(t,46.4,47.3)); kw['smile']=u; kw['eye']=lerp(1.0,0.75,u); kw['brow']=lerp(0.0,1.0,u); kw['mouth']=0.6*talk('P3',t,22)*(1-u)
    elif t<49.6: kw['rh']=(-0.18,0.95,-0.4); kw['lh']=(0.18,0.95,-0.4); kw['smile']=1.0; kw['brow']=1.0
    elif t<53.7:
        kw['smile']=1.0; kw['brow']=0.8
        if 51.2<=t<51.5: kw['rh']=(-0.2,1.3,-0.4)
        if 52.3<=t<52.7: kw['rh']=lerp3((-0.22,1.1,-0.3),(-0.1,1.45,-0.55),win(t,52.3,52.7,0.1,0.15))      # flick the coin
    else: kw['smile']=1.0; kw['eye']=1.2
    return (p[0],0.0,p[1]),yaw_of(t),kw
CH_HOME=(0.0,0.0,2.0); CH_COUNTER=(2.5,1.02,4.0)
SK=Path([(0,(2.5,5.7)),(50.0,(2.5,5.7)),(50.9,(3.05,4.75)),(60,(3.05,4.75))],stride=0.7)
def chester_state(t):
    kw=dict(lid=0.0,eye=1.0,smug=0.0,look=(0.0,0.0),mouth='smile',talk=0.0,hop=0.0,glow=0.0)
    for key in ('C0','C1','C2','C3','C4'):
        if on(key,t): kw['talk']=0.5+0.5*math.sin(t*22); kw['hop']=0.03*abs(math.sin(t*11))
    pos=CH_HOME; yaw=0.0
    if t<12.4: kw['eye']=0.0 if t<12.6 else 1.0
    if t<12.6: kw['eye']=0.06                                                             # asleep / closed before opening
    if 12.4<=t<15.6: kw['lid']=0.7*sm(seg01(t,12.4,12.8))*(1-sm(seg01(t,15.0,15.5))); kw['eye']=1.3 if t>=12.6 else 0.06; kw['hop']+=0.06*win(t,12.7,13.3,0.1,0.2)
    if 22.4<=t<27.0: kw['smug']=0.7; kw['mouth']='smirk' if not on('C2',t) else 'smile'
    if 28.4<=t<29.8: kw['smug']=0.5; kw['mouth']='smirk'
    if 29.8<=t<31.2: kw['eye']=1.25; kw['mouth']='smile'; kw['eye']=0.1 if 30.6<=t<30.75 else 1.25          # innocent blink
    for n,ts,v in SALES:
        if ts-0.25<=t<ts+0.45: kw['lid']=0.55*win(t,ts-0.25,ts+0.45,0.12,0.15)
    if 39.7<=t<40.5: kw['lid']=0.5*win(t,39.7,40.5,0.1,0.2)
    if 40.5<=t<45.3: kw['smug']=0.4; kw['eye']=1.15
    if 45.3<=t<47.9: kw['look']=(-0.6,0.3); kw['eye']=1.1+0.2*(t>46.8); kw['mouth']='smile'
    if 47.9<=t<49.4:                                                                         # carried to the counter
        hp,hy,_=hero_state(t); R_=Ry(hy); pos=tuple(np.array(hp)+R_@np.array([0,0.68,-0.42])); yaw=hy; kw['mouth']='o'; kw['eye']=1.4
    elif 49.4<=t<51.7: pos=CH_COUNTER; yaw=0.0; kw['mouth']='o'; kw['eye']=1.45; kw['look']=(0.0,0.6) if t>=50.2 else (0,0)
    elif t>=51.7:
        u=sm(seg01(t,51.7,52.1)); pos=lerp3(CH_COUNTER,(2.55,1.12,4.32),u); yaw=0.0
        kw['mouth']='o'; kw['eye']=1.45
        if 52.55<=t<52.9: kw['lid']=0.4*win(t,52.55,52.9,0.06,0.15)
        if t>=55.2:
            pos=(2.5,1.32,4.45); kw['look']=(0.8,0.7); kw['eye']=1.3; kw['mouth']='o'
            if t>=57.6: kw['smug']=0.75*sm(seg01(t,57.6,57.95)); kw['mouth']='smirk' if not on('C4',t) else 'smile'; kw['look']=(0.3,0.4)
    return pos,yaw,kw
def skel_state(t):
    p=SK.pos(t); ph=SK.phase(t) if SK.moving(t) else 0.0; yaw=0.0
    kw=dict(walk=ph,jaw=0.6*talk('S1',t,9))
    if t>=51.0 and t<51.4: kw['rh']=(-0.25,1.25,-0.4)                                       # flips the coin
    if t>=51.7: kw['rh']=(-0.75,1.2,-0.4); kw['lh']=(-0.38,1.2,-0.45)
    if t>=55.2: kw['rh']=(-0.8,1.3,-0.3); kw['lh']=(-0.42,1.3,-0.35); kw['hy']=0.6; kw['hp']=0.2
    return (p[0],0.0,p[1]),yaw,kw
# ======================= SHOTS =======================
def shot(V):
    """V = video time. Returns (story_time, cam, target, fov, hook)."""
    if V<4.0:
        st=28.15+V
        if V<0.55: return st,(-2.5,1.55,0.55),(-3.9,1.35,1.75),52,True
        if V<1.55: return st,(0.15,0.72,0.75),(0.0,0.42,2.0),50,True
        return st,(-2.35,1.55,0.6),(-3.45,1.4,1.75),50,True
    if V<4.6: return None
    st=V
    if st<8.0: return st,(-0.6,1.7,-0.9),(-3.0,1.0,1.7),58,False
    if st<12.0: return st,(-0.45,1.5,0.0),(0.25,0.8,2.0),56,False
    if st<15.6: return st,(0.18,0.8,0.65),(0.0,0.5,2.0),52,False
    if st<17.8: return st,(0.7,1.25,-0.95),(-0.4,0.9,1.6),56,False
    if st<20.6: return st,(2.3,1.45,1.0),(3.85,1.4,2.1),54,False
    if st<23.0: return st,(2.05,1.5,0.95),(3.4,1.3,2.1),56,False
    if st<25.0: return st,(1.75,1.5,1.55),(3.15,1.42,2.1),50,False
    if st<27.0: return st,(0.22,0.8,0.8),(0.0,0.45,2.0),50,False
    if st<28.35: return st,(0.6,2.6,-2.3),(-0.6,0.9,1.8),62,False
    if st<29.7: return st,(-2.5,1.55,0.55),(-3.9,1.35,1.75),52,False
    if st<30.4: return st,(-2.35,1.55,0.6),(-3.45,1.4,1.75),50,False
    if st<31.2: return st,(0.15,0.72,0.75),(0.0,0.42,2.0),50,False
    if st<40.5: return st,(-2.9,1.5,2.75),(-0.5,0.85,1.4),54,False
    if st<43.3: return st,(0.22,0.8,0.8),(0.0,0.45,2.0),50,False
    if st<45.3: return st,(-3.3,1.55,3.0),(-0.45,0.8,1.45),60,False
    if st<47.9: return st,(-0.2,1.45,1.72),(-0.75,1.4,1.05),46,False
    if st<49.6: return st,(3.3,1.6,1.3),(0.9,0.95,2.1),58,False
    if st<52.9: return st,(3.7,1.65,2.0),(2.35,1.2,3.95),56,False
    if st<53.7: return st,(-2.5,1.55,0.55),(-3.9,1.35,1.75),52,False
    if st<55.2: return st,(1.7,1.5,0.35),(-4.0,1.15,1.75),58,False
    return st,(2.85,1.6,2.15),(2.8,1.45,4.55),56,False
R=Renderer(W,H,fog=(30,20,16))
def build(st,cp,hook):
    groups=[]
    def add(Q,D=None):
        if not Q: return
        c=np.mean([q['c'] for q in Q],axis=0); groups.append((Q,[x for x in (D or []) if np.linalg.norm(x['c']-cp)<np.linalg.norm(x['hc']-cp)]))
    b,y,kw=hero_state(st,hook)
    if b[0]>X0-0.45 or st<4.7: add(*hero(b,y,st,**kw))
    b,y,kw=chester_state(st); add(*chester(b,y,st,**kw))
    if st>=49.9: b,y,kw=skel_state(st); add(*skeleton(b,y,st,**kw))
    add(door(st)); add(sword(st)); add(curtain(st)); add(lanterns(st))
    L=[]
    for Q,D in groups: L+=[Q,D]
    return L
def lights(st):
    L=[((x,y-0.3,z),(255,200,120),1.0) for (x,y,z) in LANTERNS]+[((0,2.5,-1.5),(255,240,220),0.9)]
    if 12.5<=st<15.5: L.append(((0,0.9,1.8),(255,220,90),4.0*win(st,12.5,15.5,0.2,0.6)))
    L.append(((3.6,1.4,2.1),(120,230,255),1.2))
    if 28.45<=st<53.2: L.append(((-3.7,1.2,1.75),(255,40,40),1.2))
    return L
def find_coeffs(pa,pb):
    A=[]
    for p1,p2 in zip(pa,pb): A.append([p1[0],p1[1],1,0,0,0,-p2[0]*p1[0],-p2[0]*p1[1]]); A.append([0,0,0,p1[0],p1[1],1,-p2[1]*p1[0],-p2[1]*p1[1]])
    return np.linalg.lstsq(np.array(A,float),np.array(pb,float).reshape(8),rcond=None)[0]
WHT=(244,244,240); YEL=(255,214,60); RED=(236,50,50); GRN=(80,230,100); GRY=(150,150,160); CYA=(110,230,255); PNK=(255,120,190)
def otext(d,s,x,y,col,sc=1):
    o=max(1,sc//2)
    for ox,oy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)): font.text(d,s,x+ox*o,y+oy*o,(0,0,0),sc,None)
    font.text(d,s,x,y,col,sc,None)
def ctext_w(d,s,y,col,sc,w,x0=0): otext(d,s,x0+(w-font.width(s,sc))//2,y,col,sc)
def sign_img():
    img=Image.new('RGB',(112,50),(200,160,100)); d=ImageDraw.Draw(img)
    for k in range(0,50,7): d.line([0,k,112,k],fill=(186,146,90))
    ctext_w(d,'FREE',4,(170,30,30),2,112); ctext_w(d,'LEGENDARY',22,(60,30,10),1,112); ctext_w(d,'LOOT!',34,(60,30,10),1,112)
    return img
SIGN=sign_img()
def render_scene(st,pos,tgt,fov,hook):
    cam=Camera.look(pos,tgt); cp=np.array(pos)
    env=[SHOP_F,SHOP_W,SHOP_P]; chars=build(st,cp,hook)
    bias=[1.0]*len(env)+[1.0 if i%2==0 else 1.004 for i in range(len(chars))]
    img,vi=zrender(R,cam,env+chars,lights(st),fov=fov,fog_start=9,fog_end=22,ambient=0.36,bias=bias)
    a=np.asarray(img); m=(a[...,0]>240)&(a[...,1]<15)&(a[...,2]>240)
    if m.any():
        corners=[(0.46,1.77,1.81),(1.58,1.77,1.81),(1.58,1.27,1.81),(0.46,1.27,1.81)]; P=[R.project(c,vi) for c in corners]
        if all(P):
            co=find_coeffs([(p[0],p[1]) for p in P],[(0,0),(112,0),(112,50),(0,50)])
            warped=SIGN.transform((W,H),Image.PERSPECTIVE,co,Image.BILINEAR)
            img=Image.composite(warped,img,Image.fromarray((m*255).astype(np.uint8)))
        else: img=Image.fromarray(np.where(m[...,None],np.array([200,160,100],np.uint8),a))
    return post.ps1(img),vi
# ======================= UI =======================
def proj(vi,p):
    q=R.project(tuple(p),vi); return (q[0],q[1]) if q else None
def banner(d,lines,col,y,sc=1,bg=(20,10,6)):
    wmax=max(font.width(s,sc) for s,_ in lines)+16; x0=(W-wmax)//2; h=len(lines)*(8*sc+4)+8
    d.rectangle([x0,y,x0+wmax,y+h],fill=bg,outline=col); d.rectangle([x0+2,y+2,x0+wmax-2,y+h-2],outline=tuple(int(c*0.5) for c in col))
    for i,(s,c) in enumerate(lines): ctext_w(d,s,y+6+i*(8*sc+4),c,sc,W)
def tag(d,x,y,l1,l2,col=(240,226,190)):
    w=max(font.width(l1),font.width(l2))+10; x0=int(max(4,min(W-w-4,x-w//2))); y0=int(y-30)
    d.line([x,y,x0+w//2,y0+24],fill=(60,40,20)); d.polygon([(x0,y0+4),(x0+6,y0),(x0+w,y0),(x0+w,y0+24),(x0+6,y0+24),(x0,y0+20)],fill=col,outline=(90,60,30))
    otext(d,l1,x0+8,y0+4,WHT); otext(d,l2,x0+8,y0+14,YEL)
def coin(d,x,y,r=3): d.ellipse([x-r,y-r,x+r,y+r],fill=(250,210,50),outline=(150,100,20))
def item_icon(d,name,x,y):
    if name=='sword': d.line([x-6,y+6,x+6,y-6],fill=(200,200,210),width=3); d.line([x-6,y+1,x-1,y+6],fill=GOLD,width=2)
    elif name=='armor': d.rectangle([x-6,y-6,x+6,y+6],fill=STEEL,outline=STEEL_D)
    elif name=='boots': d.rectangle([x-5,y-6,x,y+4],fill=BOOT); d.rectangle([x-5,y+2,x+5,y+6],fill=BOOT)
    else: d.rectangle([x-6,y-7,x+6,y+6],fill=PACK,outline=PACK_D); d.rectangle([x-6,y-7,x+6,y-3],fill=PACK_D)
def glow_fx(img,x,y,u,t,col=(255,220,100),rays=12,rad=40):
    lay=Image.new('L',(W,H),0); d=ImageDraw.Draw(lay)
    for r_,a_ in ((rad,50),(rad*0.65,70),(rad*0.35,90)):
        r2=int(r_*u); d.ellipse([x-r2,y-r2,x+r2,y+r2],fill=a_)
    for k in range(rays):
        a=t*1.6+k*2*PI/rays; L=int((rad*1.6+8*math.sin(t*7+k))*u); wa=0.06
        d.polygon([(x+6*math.cos(a),y+6*math.sin(a)),(x+L*math.cos(a-wa),y+L*math.sin(a-wa)),(x+L*math.cos(a+wa),y+L*math.sin(a+wa))],fill=int(140*u))
    a=np.asarray(img).astype(np.float32); m=np.asarray(lay).astype(np.float32)[...,None]/255.0
    return Image.fromarray(np.clip(a*(1-0.3*m)+m*np.array(col)*1.2,0,255).astype(np.uint8))
SPK={'P':('PLAYER:',PNK),'N':('',CYA),'C':('CHESTER:',YEL),'S':('SKELETON:',(220,220,210))}
HIL={'CHEST','MONEY?!','SECRET','FREE.','SHOP!','FREE!','ACCESS','ONE','PROCESSING','FEE.','SELL.','TREASURE..','FREE?','IS.','WONDERFUL!'}
def subtitle(d,V,st,hook):
    cur=None
    for k,t0,txt,dd in SCRIPT:
        tt=V if (hook or k in ('C0','P1') and hook) else st
        if k=='P1' and not hook: continue
        if k=='C0' and not hook: tt=st-28.2
        if t0<=tt<t0+dd+0.15: cur=(k,txt)
    if not cur: return
    k,txt=cur; spk=SPK[k[0]]
    words=((spk[0]+' ') if spk[0] else '')+txt.upper().replace('...','..'); ws=words.split(); lines=[]; c=''
    for w_ in ws:
        if len(c)+len(w_)+(1 if c else 0)>27: lines.append(c); c=w_
        else: c=(c+' '+w_).strip()
    lines.append(c); y=272-11*(len(lines)-1)
    for ln in lines:
        xw=font.width(ln); x=(W-xw)//2; d.rectangle([x-3,y-2,x+xw+2,y+8],fill=(0,0,0)); cx=x
        for wd in ln.split(' '):
            col=spk[1] if (wd==spk[0] or not spk[0]) else (YEL if wd in HIL else WHT)
            if not spk[0] and wd in HIL: col=YEL
            otext(d,wd,cx,y,col); cx+=font.width(wd)+6
        y+=11
def hud(img,vi,V,st,hook):
    T=st
    # golden light when Chester opens
    if 12.5<=T<14.2 and vi is not None:
        p=proj(vi,(0,0.6,2.0))
        if p: img=glow_fx(img,p[0],p[1],win(T,12.5,14.2,0.15,0.5),T,rad=55,rays=14)
        if T<12.75: img=Image.blend(img,Image.new('RGB',(W,H),(255,236,160)),0.7*(1-seg01(T,12.5,12.75)))
    if 17.8<=T<22.4 and vi is not None:
        p=proj(vi,(3.85,1.55,2.1))
        if p: img=glow_fx(img,p[0],p[1],0.5+0.2*math.sin(T*9),T,col=(120,230,255),rays=8,rad=18)
    d=ImageDraw.Draw(img)
    if 18.0<=T<19.2 and vi is not None:
        hp,hy,_=hero_state(T); p=proj(vi,np.array(hp)+np.array([0,1.85,0]))
        if p: otext(d,'!',int(p[0])-2,int(p[1])-8,YEL,2)
    if 13.6<=T<17.6:
        y=int(lerp(-40,36,sm(seg01(T,13.6,13.85)))); banner(d,[('PIRATE SHOP ACCESS',YEL),('UNLOCKED!',WHT)],YEL,y)
    if 22.4<=T<27.0 and vi is not None:
        p=proj(vi,(3.85,1.85,2.1))
        if p: tag(d,int(p[0]),int(p[1]),'PRICE:','999 GOLD')
    if 28.45<=T<31.2 or (hook and V>=0.3):
        k=(T-28.45); sh=int(3*math.sin(k*40)*math.exp(-k*4)) if k>0 else 0
        y=30+sh; banner(d,[('EXIT FEE:',RED),('999 GOLD',RED)],RED,y,sc=2,bg=(40,6,6))
    if 31.2<=T<53.7 and not hook:
        g=gold_at(T); d.rectangle([4,4,74,20],fill=(20,12,6),outline=YEL); coin(d,13,12,4); otext(d,str(g),22,9,RED if (g==0 and T>=40.4) else YEL)
        if T<40.4: otext(d,'/999',22+font.width(str(g))+2,9,GRY)
    for n,ts,v in SALES:
        if ts-0.3<=T<ts and vi is not None:
            hp,hy,_=hero_state(T); a=proj(vi,np.array(hp)+np.array([0,1.0,0])); b_=proj(vi,(0,0.6,2.0)); u=seg01(T,ts-0.3,ts)
            if a and b_: item_icon(d,n,int(lerp(a[0],b_[0],u)),int(lerp(a[1],b_[1],u)-20*math.sin(PI*u)))
        if ts<=T<ts+1.3:
            nm={'sword':'SWORD','armor':'ARMOR','boots':'BOOTS','pack':'BACKPACK'}[n]; inc=v-(SALES[SALES.index((n,ts,v))-1][2] if n!='sword' else 0)
            y=int(lerp(-30,30,sm(seg01(T,ts,ts+0.15)))); banner(d,[('SOLD: '+nm,WHT),('+%d GOLD'%inc,YEL)],YEL,y)
            if vi is not None and T<ts+0.5:
                b_=proj(vi,(0,0.6,2.0))
                if b_:
                    for k in range(6):
                        u=seg01(T,ts+k*0.05,ts+0.35+k*0.05)
                        if 0<u<1: coin(d,int(lerp(b_[0],13,u)),int(lerp(b_[1],12,u)-30*math.sin(PI*u)))
    if 39.7<=T<40.5 and vi is not None:
        hp,hy,_=hero_state(T); a=proj(vi,np.array(hp)+np.array([0,1.0,0])); b_=proj(vi,(0,0.5,2.0))
        if a and b_:
            for k in range(10):
                u=seg01(T,39.7+k*0.05,39.95+k*0.05)
                if 0<u<1: coin(d,int(lerp(a[0],b_[0],u)),int(lerp(a[1],b_[1],u)-25*math.sin(PI*u)))
        banner(d,[('PAID: 999 GOLD',GRN)],GRN,30)
    if 41.8<=T<43.3: y=int(lerp(-30,30,sm(seg01(T,41.8,42.0)))); banner(d,[('PROCESSING FEE:',WHT),('1 GOLD',RED)],RED,y)
    if 43.3<=T<45.3:
        a=np.asarray(img).astype(np.float32)*0.45; img=Image.fromarray(a.astype(np.uint8)); d=ImageDraw.Draw(img)
        d.rectangle([20,70,160,200],fill=(26,18,12),outline=YEL); ctext_w(d,'INVENTORY',78,YEL,1,W)
        for i in range(4):
            x0=36+(i%2)*58; y0=96+(i//2)*44; d.rectangle([x0,y0,x0+50,y0+36],outline=GRY); ctext_w(d,'EMPTY',y0+14,GRY,1,50,x0)
        coin(d,60,188,4); otext(d,'GOLD: 0',70,184,RED if int(T*4)%2 else WHT)
    if 49.6<=T<51.7 and vi is not None:
        p=proj(vi,(2.5,1.75,4.0))
        if p: tag(d,int(p[0]),int(p[1]),'TALKING CHEST','1 GOLD')
    if 51.0<=T<51.4 and vi is not None:
        a=proj(vi,(2.85,1.3,4.4)); hp,hy,_=hero_state(T); b_=proj(vi,np.array(hp)+np.array([0,1.2,0])); u=seg01(T,51.0,51.35)
        if a and b_: coin(d,int(lerp(a[0],b_[0],u)),int(lerp(a[1],b_[1],u)-30*math.sin(PI*u)),4)
    if 51.35<=T<52.3: banner(d,[('+1 GOLD',YEL)],YEL,30)
    if 52.35<=T<52.65 and vi is not None:
        hp,hy,_=hero_state(T); a=proj(vi,np.array(hp)+np.array([0,1.4,0])); b_=proj(vi,(2.55,1.4,4.32)); u=seg01(T,52.35,52.6)
        if a and b_: coin(d,int(lerp(a[0],b_[0],u)),int(lerp(a[1],b_[1],u)-35*math.sin(PI*u)),4)
    if 52.65<=T<53.7: banner(d,[('FEE PAID!',GRN),('DOOR UNLOCKED',WHT)],GRN,30)
    subtitle(d,V,st,hook)
    return img
def frame(V):
    s=shot(V)
    if s is None:                                                         # quick rewind 4.0-4.6
        u=seg01(V,4.0,4.6); st=lerp(31.0,4.7,u); _,cam,tgt,fov,_=shot(lerp(31.0,4.7,u)) if False else (None,(0.6,2.6,-2.3),(-0.6,0.9,1.8),62,False)
        img,vi=render_scene(st,cam,tgt,fov,False); a=np.asarray(img).astype(np.float32)
        rnd=np.random.default_rng(int(V*100))
        for _ in range(6): y=int(rnd.integers(0,H-6)); a[y:y+3]=a[y:y+3]*0.4+160
        a=a*0.8+np.array([10,10,30]); img=Image.fromarray(np.clip(a,0,255).astype(np.uint8)); d=ImageDraw.Draw(img)
        for k in range(2): d.polygon([(70+k*9,150),(78+k*9,144),(78+k*9,156)],fill=WHT,outline=(0,0,0))
        otext(d,'EARLIER',92,147,WHT); return img
    st,cam,tgt,fov,hook=s
    if st>=59.0: return Image.new('RGB',(W,H),(0,0,0))
    img,vi=render_scene(st,cam,tgt,fov,hook)
    return hud(img,vi,V,st,hook)
TEST=os.environ.get('TEST')
if TEST:
    ims=[frame(float(x)) for x in TEST.split(',')]; sh=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): sh.paste(im,(i*182,0))
    sh.resize((sh.width*2,640),Image.NEAREST).save('test.png'); sys.exit()
# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=61); sr=s.sr; n=s.n; t=s.t; M=np.zeros(n)
    def note(buf,t0,m,d,v,wave='sq',duty=0.5,dec=3.0,att=0.004):
        f=440*2**((m-69)/12); tt=s.T(d); ph=(f*tt)%1
        x=np.where(ph<duty,1.0,-1.0) if wave=='sq' else (4*np.abs(ph-0.5)-1 if wave=='tri' else np.sin(2*np.pi*ph))
        env=np.minimum(1,tt/att)*np.exp(-tt*dec); i=int(t0*sr); j=min(n,i+len(tt)); buf[i:j]+=(x*env*v)[:j-i]
    def blip(t0,f,d=0.06,v=0.035,dec=10): tt=s.T(d); s.place(np.where((f*tt)%1<0.5,1.0,-1.0)*np.exp(-tt*dec),t0,v)
    def bell(t0,f,v=0.05,d=0.8): tt=s.T(d); s.place((np.sin(2*np.pi*f*tt)+0.5*np.sin(2*np.pi*f*2.76*tt))*np.exp(-tt*5),t0,v)
    def nb(t0,d,lo,hi,v,seed,shape=2,pan=0.0): s.place(s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v,pan)
    def thud(t0,f=70,v=0.3,d=0.5): tt=s.T(d); s.place(np.sin(2*np.pi*f*tt*(1-0.3*tt/d))*np.exp(-tt*9)+s.filt_short(s.noise(d,int(t0*13)),lo=80,hi=900)*np.exp(-tt*14)*0.6,t0,v)
    def clank(t0,v=0.15,seed=0): tt=s.T(0.5); s.place(sum(np.sin(2*np.pi*f*tt)*np.exp(-tt*k) for f,k in ((440,10),(1100,14),(1760,20)))*0.4+s.filt_short(s.noise(0.5,seed),lo=1500,hi=7000)*np.exp(-tt*35),t0,v)
    def coins(t0,cnt=6,v=0.04,spread=0.4,seed=0):
        r=np.random.default_rng(seed)
        for k in range(cnt): bell(t0+r.uniform(0,spread),r.uniform(2400,4200),v*r.uniform(0.6,1),0.25)
    def register(t0,v=0.08): clank(t0,v*0.6,int(t0*7)); bell(t0+0.08,1568,v,1.0); bell(t0+0.08,2093,v*0.8,1.0)
    def step(t0,v=0.04,seed=0): tt=s.T(0.07); s.place(s.filt_short(s.noise(0.07,seed),lo=200,hi=2500)*np.exp(-tt*60),t0,v)
    def jig(a,b,v=1.0,minor=False,seed=0):
        sc=[0,2,3,5,7,8,10,12] if minor else [0,2,4,5,7,9,11,12]; root=57 if minor else 60
        pat=[0,2,4,2,4,5,4,2,0,1,2,4,7,4,2,1]; bass=[0,0,4,4,3,3,4,4]; k=0; tc=a
        while tc<b-1e-6:
            m=root+12+sc[pat[k%16]%8]; note(M,tc,m,0.15,0.022*v,'sq',0.25,9)
            if k%3==0: note(M,tc,root-12+sc[bass[(k//3)%8]%8],0.3,0.06*v,'tri',dec=4)
            if k%6==3: s.place(s.filt_short(s.noise(0.05,k+seed),lo=5000)*np.exp(-s.T(0.05)*80),tc,0.012*v)
            k+=1; tc+=0.18
    # ---------- hook ----------
    s.silence(0,0.25,level=0.0)
    thud(0.25,60,0.6,0.7); clank(0.32,0.14,1); note(M,0.25,40,1.4,0.08,'sq',0.4,1.5); note(M,0.25,46,1.4,0.06,'sq',0.4,1.5)
    blip(0.35,220,0.5,0.06,2); blip(0.85,165,0.6,0.06,2)                                  # EXIT FEE alarm
    for k in range(10): nb(0.6+k*0.12,0.08,300,2000,0.03,10+k)                            # rattling the handle
    tt=s.T(0.6); s.place(np.sin(2*np.pi*np.cumsum(2400-2100*tt/0.6)/sr)*0.4+s.filt_short(s.noise(0.6,3),lo=1000,hi=6000)*0.3,4.0,0.1)   # rewind
    # ---------- discovery ----------
    jig(4.7,12.3,0.8,minor=True)
    for k in range(9): step(4.75+k*0.38,0.035,100+k)
    tt=s.T(1.2); s.place(sum(np.sin(2*np.pi*f*tt*(1+0.004*np.sin(2*np.pi*5*tt)))*0.3 for f in (523,659,784,1047))*np.minimum(1,tt/0.1)*np.exp(-tt*1.5),12.45,0.08)   # magic chest opening
    nb(12.4,0.6,1500,8000,0.06,5); clank(12.42,0.05,6)
    for k,f in enumerate((1047,1319,1568,2093,2637)): bell(12.6+k*0.08,f,0.04)
    jig(13.4,22.3,0.85)
    for k,f in enumerate((784,988,1175,1568)): bell(17.9+k*0.07,f,0.045)                 # item discovery
    register(22.4,0.09); M[int(22.45*sr):int(22.9*sr)]*=np.linspace(1,0,int(0.45*sr))
    for k in range(6): note(M,23.0+k*0.66,38 if k%2==0 else 37,0.5,0.05,'tri',dec=3)
    for k in range(6): step(27.0+k*0.22,0.05,200+k)
    jig(27.0,28.38,0.9)
    M[int(28.38*sr):int(31.2*sr)]=0
    thud(28.4,60,0.6,0.7); clank(28.47,0.14,7); blip(28.5,220,0.5,0.06,2); blip(29.0,165,0.6,0.06,2)
    for k in range(9): nb(28.62+k*0.12,0.08,300,2000,0.03,30+k)
    # awkward silence 29.8-31.2 (only the room)
    # ---------- selling montage ----------
    jig(31.2,39.3,1.0,seed=3)
    for nm,ts,v in SALES:
        nb(ts-0.3,0.3,800,5000,0.05,int(ts*10)); clank(ts-0.02,0.05,int(ts)); thud(ts,110,0.12,0.25)     # item into Chester (gulp)
        coins(ts+0.05,8,0.035,0.45,int(ts)); register(ts+0.5,0.06)
    coins(39.7,16,0.035,0.7,99); register(40.3,0.08)
    blip(41.85,180,0.35,0.06,2); blip(42.2,140,0.4,0.06,2)                                 # processing fee
    blip(43.35,330,0.15,0.04,3); blip(43.55,247,0.35,0.04,3)                              # empty inventory
    # revenge: sneaky pizzicato
    for k in range(int((53.0-46.4)/0.24)):
        m=[57,None,60,None,57,None,64,63][k%8]
        if m: note(M,46.4+k*0.24,m,0.12,0.045,'sq',0.25,16)
        if k%2==0: note(M,46.4+k*0.24,45,0.2,0.05,'tri',dec=8)
    for k in range(5): step(47.95+k*0.3,0.035,300+k)
    thud(49.4,140,0.12,0.25); bell(49.6,1319,0.04)
    nb(49.9,0.5,800,4000,0.05,40)                                                          # curtain
    for k in range(4): step(50.0+k*0.25,0.04,400+k); nb(50.02+k*0.25,0.1,2500,8000,0.02,450+k)     # bony steps
    tt=s.T(0.35); s.place(np.sin(2*np.pi*np.cumsum(1800+1600*tt/0.35)/sr)*np.exp(-tt*4),51.0,0.04); bell(51.35,3136,0.05,0.4)   # coin flip + catch
    tt=s.T(0.25); s.place(np.sin(2*np.pi*np.cumsum(2000+1800*tt/0.25)/sr)*np.exp(-tt*4),52.35,0.04); bell(52.62,2637,0.05,0.4); register(52.65,0.07)
    clank(52.95,0.12,77)
    tt=s.T(0.7); s.place(np.sin(2*np.pi*np.cumsum(140+50*np.sin(2*np.pi*1.5*tt))/sr)*np.sin(np.pi*tt/0.7)*0.5,53.0,0.06)     # door creak
    for k,m in enumerate((60,64,67,72,76,79)): note(M,53.7+k*0.1,m,0.25,0.04,'sq',0.25,6)
    jig(53.75,55.15,1.0,seed=5)
    for k in range(6): step(53.7+k*0.2,0.05,500+k)
    birds=np.zeros(n)
    for k in range(5):
        tc=53.8+k*0.3; tt=s.T(0.12); i=int(tc*sr); birds[i:i+len(tt)]+=np.sin(2*np.pi*np.cumsum(3000+1200*np.sin(2*np.pi*20*tt))/sr)*np.exp(-tt*20)*0.02
    s.L+=birds; s.R+=birds
    # ---------- end ----------
    register(59.05,0.12)
    # ---------- voices ----------
    NB=np.zeros(n); duck=np.ones(n)
    for k_,t0,txt,dd in SCRIPT:
        a,ar=_sf.read(f'/home/claude/tts/v9/{k_}.wav'); a=a if a.ndim==1 else a.mean(1)
        starts=[t0] if k_ not in ('C0',) else [0.55,28.75]
        if k_=='P1': starts=[1.55]
        for t0_ in starts:
            i=int(t0_*sr); j=min(n,i+len(a)); NB[i:j]+=a[:j-i]*(0.9 if k_[0]!='S' else 1.0)
            duck[max(0,i-int(0.06*sr)):min(n,j+int(0.12*sr))]=0.38
    duck=np.convolve(duck,np.ones(2000)/2000,'same')
    note(M,3.0,33,1.0,0.06,'tri',dec=2.0)
    s.L+=2.0*M*duck; s.R+=2.0*M*duck
    room=s.filt(s.rng.normal(0,1,n),lo=80,hi=700)*0.006; s.L+=room; s.R+=room
    s.reverb(0.1,length=0.6,decay=6)
    pk=max(np.abs(s.L).max(),np.abs(s.R).max()); gv=pk*1.0/np.abs(NB).max()
    s.L=s.L*(0.6+0.4*duck)+NB*gv; s.R=s.R*(0.6+0.4*duck)+NB*gv
    i0=int(59.0*sr); s.L[i0:int(59.05*sr)]=0; s.R[i0:int(59.05*sr)]=0
    return s.save(path,peak=0.9)
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'chest_scam.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','20','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'cs_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.95,vignette=0.25,grain=1.6,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(post.upscale(frame(f/FPS),S),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
