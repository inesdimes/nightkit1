"""THE LAST SAVE POINT - 60 s PS1 survival-horror short, 9:16. Everything procedural (nightkit).
Run: TEST=t1,t2 python examples/last_save.py  |  PART=a:b (frames)  |  PART=audio"""
import os, sys, math, json
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, box, quad, tiled_plane, transform, refresh
from nightkit import motion, post, font
from nightkit.audio import Sound
font.FONT['?']=font.FONT.get('?',['01110','10001','00001','00110','00100','00000','00100'])
OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6
DUR=60.0; N=int(DUR*FPS)
sm=motion.smooth
def seg01(t,a,b): return max(0.0,min(1.0,(t-a)/(b-a)))
def win(t,a,b,ra=0.2,rb=0.2): return sm(seg01(t,a,a+ra))*(1-sm(seg01(t,b-rb,b)))
def lerp(a,b,u): return a+(b-a)*u
def lerp3(a,b,u): return tuple(a[i]+(b[i]-a[i])*u for i in range(3))
def Rx(a): c,s=math.cos(a),math.sin(a); return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def Ry(a): c,s=math.cos(a),math.sin(a); return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def obox(center,hs,R,col,emit=False):
    c=np.array(center,float); return box(-hs[0],hs[0],-hs[1],hs[1],-hs[2],hs[2],col,xf=lambda p:tuple(c+R@np.array(p)),emit=emit)
def seg(p0,p1,w,col,depth=None,emit=False):
    p0=np.array(p0,float); p1=np.array(p1,float); d=p1-p0; L=np.linalg.norm(d)+1e-9; d/=L
    up=np.array([0,0,-1.0]) if abs(d[1])>0.9 else np.array([0,1.0,0]); a=np.cross(d,up); a/=np.linalg.norm(a)+1e-9; b=np.cross(a,d); dp=depth or w
    v=[p0-a*w/2-b*dp/2,p0+a*w/2-b*dp/2,p0+a*w/2+b*dp/2,p0-a*w/2+b*dp/2,p1-a*w/2-b*dp/2,p1+a*w/2-b*dp/2,p1+a*w/2+b*dp/2,p1-a*w/2+b*dp/2]
    F=[(0,1,2,3),(5,4,7,6),(4,0,3,7),(1,5,6,2),(3,2,6,7),(4,5,1,0)]
    return [quad([tuple(v[i]) for i in f],col,emit) for f in F]
def elbow(sh,hand,out_dir,L=0.62):
    sh=np.array(sh); hand=np.array(hand); m=(sh+hand)/2; d=np.linalg.norm(hand-sh)
    bend=max(0.0,(L-d)/L)*0.25+0.03; return tuple(m+np.array(out_dir)*bend+np.array([0,-1,0])*bend*0.6)
def keys(T,K):
    if T<=K[0][0]: return K[0][1]
    for (a,va),(b,vb) in zip(K,K[1:]):
        if T<b: u=sm((T-a)/(b-a)); return tuple(va[i]+(vb[i]-va[i])*u for i in range(len(va)))
    return K[-1][1]
# ---------------- palette ----------------
IRON=(104,106,116); IRON_D=(74,76,86); IRON_K=(52,54,62); LEATHER=(70,50,38); CLOTH=(196,22,30); CLOTH_D=(150,14,22)
SLIT=(6,6,8); CRACK=(14,12,14); BLADE=(128,132,142)
STONE=lambda i,j:[(64,64,72),(56,56,64),(70,70,78),(52,52,60)][(i*7+j*3)%4]
# ================= KNIGHT (one model, used for the original AND the copy) =================
def knight(base,yaw,walk=0.0,rhand=None,lhand=None,lean=0.0,sword=False,sword_dir=(0,0.3,-1),sit=0.0,head_yaw=0.0,head_pitch=0.0,tremble=0.0,t=0.0):
    """Faces -z at yaw 0. Signature details: crack on the helmet (front, his left) + red cloth on the LEFT shoulder (+x local)."""
    bc=np.array(base,float); Rb=Ry(yaw)
    def W(p): return tuple(bc+Rb@np.array(p,float))
    hip_y=0.86-0.5*sit
    def WL(p):
        p=np.array(p,float)+np.array([0,hip_y-0.86,0]); piv=np.array([0,hip_y,0]); return W(piv+Rx(lean)@(p-piv))
    Q=[]; D=[]; sw=0.42*math.sin(walk)
    for sx,ph in ((-1,1),(1,-1)):
        hip=np.array([sx*0.1,hip_y,0.0])
        if sit>0: ft=np.array([sx*0.14,0.06,-0.78*sit]); kn=(hip+ft)/2+np.array([0,0.14*sit,0])
        else:
            a=ph*sw; ft=hip+np.array([0,-0.82*math.cos(a),-0.82*math.sin(a)]); ft[1]=max(0.06,ft[1]); kn=(hip+ft)/2+np.array([0,0,-0.05])
        Q+=transform(seg(hip,kn,0.15,IRON_D)+seg(kn,ft,0.13,IRON)+box(ft[0]-0.07,ft[0]+0.07,ft[1]-0.06,ft[1]+0.04,ft[2]-0.13,ft[2]+0.06,IRON_K),W)
    Q+=box(-0.2,0.2,0.86,1.42,-0.12,0.12,IRON,xf=WL)                                        # cuirass
    Q+=box(-0.21,0.21,0.84,0.93,-0.128,0.128,LEATHER,xf=WL)                                 # belt
    D+=box(-0.14,0.14,1.12,1.16,-0.126,-0.12,IRON_K,xf=WL)+box(-0.02,0.02,0.96,1.36,-0.126,-0.12,IRON_D,xf=WL)  # chest ridge
    for sx in (-1,1): Q+=box(sx*0.27-0.09,sx*0.27+0.09,1.3,1.44,-0.11,0.11,IRON_D,xf=WL)   # pauldrons
    # red cloth on the LEFT shoulder: wraps over the pauldron, hangs front and back
    Q+=box(0.17,0.38,1.43,1.47,-0.125,0.125,CLOTH,xf=WL)
    D+=box(0.17,0.36,0.98,1.44,-0.14,-0.126,CLOTH,xf=WL)+box(0.17,0.36,0.9,1.44,0.126,0.14,CLOTH_D,xf=WL)
    D+=box(0.36,0.385,1.06,1.44,-0.11,0.11,CLOTH_D,xf=WL)
    hc=np.array([0,1.6,0]); tr=tremble*0.05*math.sin(t*47)
    def WH(p): p=np.array(p,float); return WL(hc+Ry(head_yaw+tr)@Rx(head_pitch)@(p-hc))
    Q+=box(-0.13,0.13,1.44,1.76,-0.13,0.12,IRON,xf=WH)+box(-0.02,0.02,1.76,1.81,-0.13,0.1,IRON_D,xf=WH)   # helm + crest
    D+=box(-0.1,0.1,1.58,1.62,-0.136,-0.13,SLIT,xf=WH)                                       # visor slit
    for i in range(3): D+=box(-0.006,0.006,1.48+0.03*i,1.52+0.03*i,-0.136,-0.13,SLIT,xf=WH)   # breathing holes
    # the crack: zig-zag from the crest down to the slit, on his left (+x) side
    for (x0,y0,x1,y1) in ((0.03,1.75,0.06,1.70),(0.06,1.70,0.045,1.665),(0.045,1.665,0.08,1.625),(0.06,1.70,0.1,1.69)):
        D+=transform(seg((x0,y0,-0.133),(x1,y1,-0.133),0.014,CRACK,depth=0.004),WH)
    rh=np.array(WL(rhand or (-0.3,0.95,-0.1))); lh=np.array(WL(lhand or (0.3,0.95,-0.05)))
    if tremble: j=np.array([math.sin(t*53),math.sin(t*61),math.sin(t*43)])*0.02*tremble; rh=rh+j; lh=lh-j
    for sx,h in ((-1,rh),(1,lh)):
        sh=np.array(WL((sx*0.28,1.36,0))); el=elbow(sh,h,tuple(Rb@np.array([sx*0.6,0,-0.2])))
        Q+=seg(sh,el,0.11,IRON)+seg(el,h,0.1,IRON_D)+obox(h,(0.06,0.06,0.06),Rb,IRON_K)
    if sword:
        d=Rb@np.array(sword_dir,float); d/=np.linalg.norm(d)+1e-9; side=np.cross(d,np.array([0,1.0,0.0001])); side/=np.linalg.norm(side)+1e-9
        Q+=seg(rh-d*0.1,rh+d*0.05,0.04,LEATHER)+seg(rh+d*0.05-side*0.11,rh+d*0.05+side*0.11,0.04,IRON_K)+seg(rh+d*0.06,rh+d*0.86,0.065,BLADE,depth=0.02)
    hcW=np.array(WL((0,1.6,0))); tcW=np.array(WL((0,1.1,0)))
    for q in D: q['hc']=hcW if q['c'][1]>hcW[1]-0.22 else tcW
    return Q,D
def silhouette(base,yaw,s,reach=1.0,col=(10,2,4)):
    """a trapped player: just a dark shape with palms on the glass"""
    b=np.array(base,float); Rb=Ry(yaw)
    def W(p): return tuple(b+Rb@(np.array(p,float)*s))
    Q=[]
    Q+=box(-0.18,0.18,0.85,1.42,-0.1,0.1,col,xf=W,emit=True)+box(-0.12,0.12,1.44,1.74,-0.11,0.11,col,xf=W,emit=True)
    for sx in (-1,1):
        Q+=transform(seg((sx*0.1,0.88,0),(sx*0.12,0.05,-0.05),0.13,col,emit=True),W)
        Q+=transform(seg((sx*0.24,1.38,0),(sx*0.26,1.38+0.3*reach,-0.42*reach),0.1,col,emit=True),W)
    return Q
# ================= CASTLE =================
def vwall_z(x0,x1,y0,y1,z,hole=None,step=1.0,col=STONE):
    Q=[]
    for i,x in enumerate(np.arange(x0,x1,step)):
        for j,y in enumerate(np.arange(y0,y1,step)):
            xa,xb,ya,yb=x,min(x1,x+step),y,min(y1,y+step)
            if hole and xa>=hole[0]-1e-6 and xb<=hole[1]+1e-6 and yb<=hole[2]+1e-6: continue
            Q.append(quad([(xa,ya,z),(xb,ya,z),(xb,yb,z),(xa,yb,z)],col(i,j)))
    return Q
def vwall_x(z0,z1,y0,y1,x,step=1.0,col=STONE):
    Q=[]
    for i,z in enumerate(np.arange(z0,z1,step)):
        for j,y in enumerate(np.arange(y0,y1,step)):
            Q.append(quad([(x,y,z),(x,y,min(z1,z+step)),(x,min(y1,y+step),min(z1,z+step)),(x,min(y1,y+step),z)],col(i+3,j)))
    return Q
CR_C=np.array([0.0,2.05,1.5]); CR_R=1.0; CR_H=1.7
def castle():
    F=tiled_plane(-1.6,1.6,-17,-4,0,1.0,lambda i,j:STONE(i,j))+tiled_plane(-5,5,-4,7,0,1.0,lambda i,j:STONE(i+1,j))
    Wq=[]
    Wq+=vwall_x(-17,-4,0,4,-1.6)+vwall_x(-17,-4,0,4,1.6)+tiled_plane(-1.6,1.6,-17,-4,4,1.0,lambda i,j:(40,38,44))
    Wq+=vwall_z(-1.6,1.6,0,4,-17)
    Wq+=vwall_z(-5,5,0,6,-4,hole=(-1.6,1.6,4.0))+vwall_z(-5,5,0,6,7,hole=(-1.0,1.0,3.0))
    Wq+=vwall_x(-4,7,0,6,-5)+vwall_x(-4,7,0,6,5)+tiled_plane(-5,5,-4,7,6,1.0,lambda i,j:(36,34,40))
    Wq+=box(-1.6,1.6,4.0,4.4,-4.2,-3.9,(60,56,62))                                          # arch lintel
    P=[]
    for x in (-3.6,3.6):
        for z in (-1.8,4.6): P+=box(x-0.35,x+0.35,0,6,z-0.35,z+0.35,(80,76,84))+box(x-0.45,x+0.45,0,0.35,z-0.45,z+0.45,(66,62,70))
    # pedestal (octagonal steps)
    for k,(r,y0,y1) in enumerate(((0.75,0,0.14),(0.6,0.14,0.32))):
        P+=box(-r,r,y0,y1,CR_C[2]-r,CR_C[2]+r,(84,80,88) if k==0 else (96,92,100))
    for k in range(6): P+=box(-0.62+0.2*k,-0.5+0.2*k,0.2,0.26,CR_C[2]-0.605,CR_C[2]-0.6,(150,20,28),emit=True)   # runes
    return F,Wq,P
CASTLE_F,CASTLE_W,CASTLE_P=castle()
TORCHES=[(-1.5,2.2,-13.0),(1.5,2.2,-9.5),(-1.5,2.2,-6.0),(-3.2,2.6,-1.8),(3.2,2.6,-1.8),(-3.2,2.6,4.6),(3.2,2.6,4.6)]
def flame(x,y,z,t,seed=0):
    f=0.8+0.2*math.sin(t*17+seed)+0.12*math.sin(t*31+seed*2)
    h=0.3*f; w=0.09
    return [quad([(x-w,y,z),(x+w,y,z),(x,y+h,z)],(255,150,40),emit=True),quad([(x,y,z-w),(x,y,z+w),(x,y+h*0.8,z)],(255,210,90),emit=True)]
TORCH_OUT={1:24.3,2:25.6}
def torch_on(T,i):
    if i in TORCH_OUT and 22.0<=T<40.0: return 1.0-seg01(T,TORCH_OUT[i],TORCH_OUT[i]+0.25)
    return 1.0
def torches(T):
    Q=[]
    for k,(x,y,z) in enumerate(TORCHES):
        Q+=box(x-0.05,x+0.05,y-0.35,y,z-0.05,z+0.05,(50,40,32))
        if torch_on(T,k)>0.3: Q+=flame(x,y,z,T,k)
    return Q
def torch_lights(T,k=1.0):
    return [((x,y+0.4,z),(255,175,115),k*torch_on(T,i)*(0.85+0.22*math.sin(T*13+i*2)+0.12*math.sin(T*29+i))) for i,(x,y,z) in enumerate(TORCHES)]
def door(open_k):
    Q=[]
    for sx in (-1,1):
        hx=sx*1.0
        def Tf(p,sx=sx,hx=hx): p=np.array(p,float); q=Ry(-sx*1.5*open_k)@(p-np.array([hx,0,7.0]))+np.array([hx,0,7.0]); return tuple(q)
        pn=box(min(0,hx),max(0,hx),0,3.0,6.98,7.08,(78,50,30))
        for y in (0.5,1.5,2.5): pn+=box(min(0,hx),max(0,hx),y,y+0.1,6.95,6.98,(40,40,44))
        Q+=transform(pn,Tf)
    Q.append(quad([(-1.0,0,7.5),(1.0,0,7.5),(1.0,3.0,7.5),(-1.0,3.0,7.5)],(235,228,210),emit=True))   # daylight outside
    Q+=tiled_plane(-1.0,1.0,7.0,7.5,0.001,0.5,lambda i,j:(200,194,180))
    return Q
def sword_on_floor():
    p0=np.array([-0.75,0.04,0.35]); d=np.array([0.62,0,-0.78]); d/=np.linalg.norm(d)
    return seg(p0,p0+d*0.15,0.04,LEATHER)+seg(p0+d*0.15,p0+d*0.95,0.06,BLADE,depth=0.02)+seg(p0+d*0.15+np.array([0.1,0,0.08]),p0+d*0.15-np.array([0.1,0,0.08]),0.04,IRON_K)
# ================= SAVE CRYSTAL (same design in every shot) =================
def crystal_faces(T,glow=1.0,flash=0.0):
    yaw=T*0.35; Qs=[]; n=8
    top=CR_C+np.array([0,CR_H,0]); bot=CR_C-np.array([0,CR_H,0])
    ring=[CR_C+Ry(yaw+k*2*math.pi/n)@np.array([CR_R,0,0]) for k in range(n)]
    for k in range(n):
        a,b=ring[k],ring[(k+1)%n]
        for tip,up in ((top,1),(bot,-1)):
            shade=0.72+0.28*math.cos(yaw+k*2*math.pi/n+0.6)+(0.12 if up>0 else -0.08)
            g=glow*shade; col=(min(255,int((150+90*g)+flash*90)),min(255,int(18*g+flash*160)),min(255,int(30*g+flash*160)))
            q=quad([tuple(a),tuple(b),tuple(tip)] if up>0 else [tuple(b),tuple(a),tuple(tip)],col,emit=True)
            q['out']=q['c']-CR_C; Qs.append(q)
    return Qs
def crystal_split(T,cp,glow=1.0,flash=0.0):
    back=[];front=[]
    for q in crystal_faces(T,glow,flash):
        (front if np.dot(q['out'],np.array(cp)-q['c'])>0 else back).append(q)
    for q in back: q['col']=tuple(int(c*0.55) for c in q['col'])
    return back,front
def motes(T,k=1.0):
    Q=[]
    for i in range(14):
        ph=(T*0.25+i*0.137)%1.0; a=i*2.4+T*0.3; r=0.9+0.3*math.sin(i*1.7)
        x=CR_C[0]+r*math.cos(a); z=CR_C[2]+r*math.sin(a); y=0.3+ph*3.6; s=0.025*k*(1-ph)
        if s>0.004: Q.append(quad([(x-s,y-s,z),(x+s,y-s,z),(x+s,y+s,z),(x-s,y+s,z)],(255,60,70),emit=True))
    return Q
# ================= STORY STATE =================
INSIDE=(0.0,0.95,1.5)
CORR=[(5.6,-15.5),(9.6,-11.8),(14.0,-6.6),(16.8,0.3)]
def orig_z(T):
    for (a,za),(b,zb) in zip(CORR,CORR[1:]):
        if T<b: return za+(zb-za)*(T-a)/(b-a)
    return CORR[-1][1]
def hits(T,t0):
    """pounding: alternating fists, returns (rh_push, lh_push) 0..1"""
    p=(T-t0)/0.42; k=int(math.floor(p)); f=p-k
    pulse=max(0.0,1-abs(f-0.35)/0.35)
    return (pulse,0.0) if k%2==0 else (0.0,pulse)
def trapped_pose(T,t0=0.0):
    r,l=hits(T,t0)
    return dict(rhand=(-0.17,1.62,-0.32-0.16*r),lhand=(0.17,1.62,-0.32-0.16*l),lean=0.06,head_pitch=-0.05,tremble=0.4,t=T)
PULL0,PULL1=46.3,48.6
def orig(T):
    """returns (mode, base, yaw, kw) for the original knight"""
    if T<5.6 or T>=PULL1: return 'inside',INSIDE,math.pi,trapped_pose(T)
    if T<16.8:
        z=orig_z(T); ph=(z+15.5)/0.62*math.pi; bob=-0.05*abs(math.sin(ph))
        return 'walk',(0.06*math.sin(ph*0.5),bob,z),math.pi,dict(walk=ph,rhand=(-0.3,0.82,0.02),sword=True,sword_dir=(0,-0.8,0.5),lhand=(0.16,1.02,-0.17),lean=0.16,head_pitch=0.22-0.3*sm(seg01(T,9.8,10.6)))
    if T<20.6:
        u=sm(seg01(T,16.8,17.5)); breath=0.04*math.sin((T-16.8)*3.2)*(T<17.9)
        lh=lerp3((0.16,1.02,-0.17),(0.12,1.45,-0.56),sm(seg01(T,17.7,18.2)))
        return 'stand',(0,0,0.3),math.pi,dict(rhand=(-0.3,0.82,0.02),sword=True,sword_dir=(0,-0.8,0.45),lhand=lh,lean=lerp(0.16,-0.06,u)+breath,head_pitch=lerp(0.1,-0.28,u))
    if T<22.0:
        turn=sm(seg01(T,20.6,21.2)); st=sm(seg01(T,21.2,21.9)); z=lerp(0.3,0.75,sm(seg01(T,20.9,21.5)))
        return 'stand',(0,0,z),math.pi*(1-turn),dict(sit=st,lean=0.1*st,rhand=(-0.3,0.95-0.45*st,-0.1-0.2*st),lhand=(0.3,0.95-0.45*st,-0.1-0.2*st),head_pitch=0.35*st)
    if T<29.2:
        hp=0.38 if T<24.6 else lerp(0.38,-0.08,sm(seg01(T,24.6,25.2)))
        return 'stand',(0,0,0.75),0.0,dict(sit=1.0,lean=0.1,rhand=(-0.3,0.5,-0.3),lhand=(0.3,0.5,-0.3),head_pitch=hp+0.015*math.sin(T*2))
    if T<31.0:
        u=sm(seg01(T,29.2,30.2)); return 'stand',(0,0,lerp(0.75,0.3,u)),0.0,dict(sit=1-u,lean=0.1*(1-u),rhand=lerp3((-0.3,0.5,-0.3),(-0.3,0.95,-0.1),u),lhand=lerp3((0.3,0.5,-0.3),(0.3,0.95,-0.1),u),head_pitch=-0.05*(1-u))
    if T<40.0: return 'stand',(0,0,0.3),0.0,mirror_pose(T,True)
    if T<PULL0:
        jerks=sum(sm(seg01(T,40.6+0.28*k,40.72+0.28*k)) for k in range(4))/4
        lift=sm(seg01(T,45.6,46.3))
        arms=lerp3((-0.3,1.1,-0.25),(-0.5,1.5,0.15),lift)
        return 'stand',(0,0.3*lift,0.3),math.pi*jerks,dict(rhand=arms,lhand=(-arms[0],arms[1],arms[2]),tremble=1.0,t=T,head_pitch=-0.15*lift,head_yaw=0.0)
    return 'pull',None,None,None
def mirror_pose(T,is_orig):
    """33.5-40: both do the same thing. At 36.0 the original lowers his arm... and the copy's arm pulls it back up."""
    up=sm(seg01(T,33.6,34.6)); hy=0.45*win(T,35.0,35.9,0.25,0.25)
    rh=lerp3((-0.3,0.95,-0.1),(-0.24,1.42,-0.5),up)
    if is_orig:
        down=sm(seg01(T,36.0,36.6))*(1-sm(seg01(T,37.0,37.22))); rh=lerp3(rh,(-0.3,0.95,-0.1),down); hy+=0.22*math.sin(T*15)*win(T,36.2,37.0,0.1,0.1)
    point=sm(seg01(T,37.0,37.8)); rh=lerp3(rh,(-0.16,1.62,-0.55),point)
    look=sm(seg01(T,38.3,39.2)); hy+=-0.9*look if is_orig else 0.9*look      # both turn their heads toward the crystal
    tr=(1.0 if is_orig and T>=36.9 else 0.0)
    return dict(rhand=rh,head_yaw=hy,tremble=tr,t=T)
COPY_PATH=[(40.0,(0,0,-1.9)),(41.6,(1.25,0,-0.7)),(43.2,(1.0,0,0.95))]
EXIT_PATH=[(50.2,(1.0,0,0.95)),(51.2,(1.75,0,2.6)),(52.6,(0.2,0,5.6)),(54.0,(0.0,0,8.3))]
def path_at(T,P):
    if T<=P[0][0]: return P[0][1],None
    for (a,pa),(b,pb) in zip(P,P[1:]):
        if T<b:
            u=(T-a)/(b-a); p=lerp3(pa,pb,u); d=np.array(pb)-np.array(pa); return p,math.atan2(-d[0],-d[2])
    return P[-1][1],None
def copy(T):
    if T<4.0: return copy(51.0+T*0.75)
    if T<22.0: return None
    if T<28.6:
        z=-9.5+3.0*sm(seg01(T,22.0,27.6)); ph=(z+9.5)/0.62*math.pi*(T<27.6)
        return (0,0,z-0.5),math.pi,dict(walk=ph)
    if T<31.0:
        z=lerp(-6.0,-1.9,seg01(T,28.6,31.0)); steps=(T-28.6)/0.6; ph=math.pi*steps
        return (0,0,z),math.pi,dict(walk=ph*(T<30.9))
    if T<40.0: return (0,0,-1.9),math.pi,mirror_pose(T,False)
    if T<43.4:
        p,yw=path_at(T,COPY_PATH); ph=(T-40.0)*1.3*2*math.pi
        yaw=yw if T<43.0 and yw is not None else 2.07
        return p,yaw,dict(walk=ph)
    if T<50.2:
        lh=lerp3((0.3,0.95,-0.05),(0.08,1.45,-0.52),win(T,43.5,46.0,0.4,0.4)); return (1.0,0,0.95),2.07,dict(lhand=lh,head_yaw=0.5*sm(seg01(T,46.2,46.8)))
    if T<54.0:
        p,yw=path_at(T,EXIT_PATH); return p,yw if yw is not None else 0.0,dict(walk=(T-50.2)*1.25*2*math.pi)
    return None
def door_open(T):
    if T<4.0: return door_open(51.0+T*0.75)
    return sm(seg01(T,51.4,52.2))*(1-sm(seg01(T,56.3,56.9)))
SIL=[((-0.42,1.2,1.75),0.15,0.58),((0.44,1.25,1.8),-0.15,0.56),((-0.12,1.75,2.05),0.0,0.48),((0.2,0.75,1.95),0.3,0.5),((-0.55,1.85,1.45),0.5,0.42),((0.55,1.9,1.4),-0.5,0.42),((0.0,0.55,1.7),0.0,0.4)]
def sil_k(T): return sm(seg01(T,54.9,56.0)) if T>=54.0 else 0.0
# ================= SHOTS =================
def shot(T):
    """camera (pos,target,fov) + fog for each storyboard shot"""
    if T<2.2: return (0.28,2.0,3.55),(0,2.15,1.5),56,(4,18)
    if T<4.0: u=seg01(T,2.2,4.0); return (-1.25,1.55+0.05*u,-1.6),(0.1,1.7,5.0),58,(4,18)
    if T<5.6: return None
    if T<9.6: return (1.25,3.5,-4.6),(0.0,0.9,-11.5-1.2*seg01(T,5.6,9.6)),54,(3,13)
    if T<14.0: z=orig_z(T); return (0.45,0.75,z-2.1),(0.0,1.7,z+4.0),56,(4,15)
    if T<17.5: return (3.9,3.4,-3.55),(-0.5,1.0,-0.6),60,(6,18)
    if T<22.0: return (2.1,1.6,-0.35),(-0.1,1.45,0.75),54,(5,18)
    if T<25.5: return (0.75,1.25,-0.75),(0.0,1.0,0.75),52,(5,18)
    if T<28.5: return (0.05,1.15,0.35),(0.0,1.35,-6.0),50,(6,30)
    if T<31.0: return (-1.3,1.25,1.3),(0.1,1.5,-2.0),54,(4,17)
    if T<32.2: return (0.24,1.56,-0.66),(0.04,1.5,0.3),46,(4,17)
    if T<33.5: return (-0.24,1.56,-0.94),(-0.04,1.5,-1.9),46,(4,17)
    if T<40.0: return (3.3,1.45,-0.8),(0.0,1.35,-0.8),52,(5,17)
    if T<43.5: return (-2.6,2.2,-3.0),(0.4,1.3,0.4),54,(5,17)
    if T<46.0: return (2.0,1.75,-0.55),(0.1,1.55,0.7),52,(4,17)
    if T<50.0: return (-2.5,2.0,-1.7),(0.1,1.7,1.0),56,(5,17)
    if T<54.0: return (-1.25,1.6,-1.6),(0.1,1.7,5.0),58,(4,18)
    if T<57.5: u=sm(seg01(T,54.0,57.5)); return lerp3((0.25,2.0,3.4),(0.05,2.35,5.4),u),(0,2.05,1.5),lerp(54,60,u),(4,18)
    return None
def pulled_knight(T):
    """the LOAD: the original comes apart into red pixels and is rebuilt inside the crystal"""
    u=seg01(T,PULL0,PULL1)
    kw=dict(rhand=(-0.5,1.5,0.15),lhand=(0.5,1.5,0.15),tremble=1.0,t=T)
    Qa,_=knight((0,0.3,0.3),math.pi,**kw); Qb,_=knight(INSIDE,math.pi,**trapped_pose(T))
    out=[]; cc=CR_C
    for i,(qa,qb) in enumerate(zip(Qa,Qb)):
        if len(qa['p'])!=len(qb['p']): continue
        d=np.linalg.norm(qa['c']-cc); delay=0.45*min(1.0,max(0.0,(d-0.6)/1.6))+0.08*((i*37)%11)/11
        e=sm(min(1.0,max(0.0,(u-delay)/0.5)))
        c=qa['c']+(qb['c']-qa['c'])*e+np.array([0,0.35*math.sin(math.pi*e),0]); s=1-0.8*math.sin(math.pi*e)
        pts=[tuple(c+s*((np.array(pa)+(np.array(pb)-np.array(pa))*e)-(qa['c']+(qb['c']-qa['c'])*e))) for pa,pb in zip(qa['p'],qb['p'])]
        hot=math.sin(math.pi*e)
        col=tuple(int(qa['col'][k]+((255,40,50)[k]-qa['col'][k])*min(1,hot*1.6)) for k in range(3))
        out.append(quad(pts,col,emit=hot>0.25))
    return out
R=Renderer(W,H,fog=(6,4,8))
def crystal_alpha(T):
    a=0.62+0.05*math.sin(T*3.1)
    if T>=54.9: a-=0.3*sm(seg01(T,54.9,55.5))*(0.85+0.15*math.sin(T*5))
    return a
def render(T):
    sh=shot(T)
    if sh is None: return Image.new('RGB',(W,H),(0,0,0)),None
    pos,tgt,fov,(fs,fe)=sh; cam=Camera.look(pos,tgt); cp=np.array(pos)
    env=[CASTLE_F,CASTLE_W,CASTLE_P+torches(T)+door(door_open(T))+(sword_on_floor() if 20.8<=T else [])]
    groups=[]
    mode,base,yaw,kw=orig(T)
    inner=[]
    if mode=='inside':
        q,d=knight(base,yaw,**kw); inner.append((q,d))
    elif mode=='pull':
        inner.append((pulled_knight(T),[]))
    else:
        q,d=knight(base,yaw,**kw); groups.append((np.mean([x['c'] for x in q],axis=0),[q,d]))
    c=copy(T)
    if c:
        q,d=knight(c[0],c[1],**c[2])
        if 22.0<=T<29.0 and c[0][2]<-4.1:                      # still in the dark corridor: only a silhouette
            for x in q+d: x['col']=(34,4,6) if x['col'] in (CLOTH,CLOTH_D) else (5,4,6); x['emit']=True
        groups.append((np.mean([x['c'] for x in q],axis=0),[q,d]))
    flash=0.0
    if PULL0<=T<PULL1+0.5: flash=0.6*win(T,PULL1-0.2,PULL1+0.5,0.15,0.3)
    glow=1.0+0.15*math.sin(T*3.1)+0.5*win(T,45.3,46.3,0.1,0.3)
    back,front=crystal_split(T,cp,glow,flash)
    sk=sil_k(T); sil=[]
    for (p,yw,s_) in SIL:
        if sk>0: d_=np.array(p)-CR_C; sil+=silhouette(tuple(CR_C+d_*(0.55+0.45*sk)),yw+math.pi,s_*(0.75+0.25*sk))
    cgroup=[back+['SIL']]
    for q,d in inner: cgroup+=[q,[x for x in d if np.linalg.norm(x['c']-cp)<np.linalg.norm(x['hc']-cp)]]
    groups.append((CR_C,cgroup+['FRONT']))
    groups.sort(key=lambda g:-np.linalg.norm(g[0]-cp))
    LA=[];LB=[];LS=[]
    for _,g in groups:
        for i,lay in enumerate(g):
            if lay=='FRONT': LB.append(front); continue
            if isinstance(lay,list) and 'SIL' in lay:
                b_=[x for x in lay if x!='SIL']; LA.append(b_); LB.append(b_); LS.append(b_+sil); continue
            LS.append(lay)
            if len(g)==2 and i==1 and lay and isinstance(lay[0],dict) and 'hc' in lay[0]:
                lay=[x for x in lay if np.linalg.norm(x['c']-cp)<np.linalg.norm(x['hc']-cp)]
            LA.append(lay); LB.append(lay)
    fx=motes(T)
    LA.append(fx); LB.append(fx); LS.append(fx)
    lights=torch_lights(T)+[(tuple(CR_C),(255,40,50),0.75*glow+6*flash),((0,5.6,1.5),(100,120,190),2.4),((0,3.8,-10.5),(100,120,190),1.1)]
    if 25.5<=T<28.5: lights.append(((0,2.4,-13.5),(255,170,110),3.0))
    if door_open(T)>0.05: lights.append(((0,2.0,7.6),(220,220,255),5*door_open(T)))
    A,vi=R.render(cam,env+LA,lights,fov=fov,fog_start=fs,fog_end=fe,ambient=0.05)
    B,_=R.render(cam,env+LB,lights,fov=fov,fog_start=fs,fog_end=fe,ambient=0.05)
    a=np.asarray(A).astype(np.float32); b=np.asarray(B).astype(np.float32)
    m=(np.abs(a-b).sum(2)>6)[...,None]; al=crystal_alpha(T)
    ai=a
    if sil:                                                     # trapped players exist only INSIDE the crystal
        As,_=R.render(cam,env+LS,lights,fov=fov,fog_start=fs,fog_end=fe,ambient=0.05); ai=np.asarray(As).astype(np.float32)
    out=np.where(m,ai*(1-al)+b*al+np.array([18,0,0])*al,a)
    img=Image.fromarray(np.clip(out,0,255).astype(np.uint8))
    return post.ps1(img),vi
# ================= HUD =================
WHT=(236,236,236); RED=(220,30,36); GRN=(80,210,90); GRY=(150,150,160)
def otext(d,s,x,y,col,sc):
    o=max(1,sc//2)
    for ox,oy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)): font.text(d,s,x+ox*o,y+oy*o,(0,0,0),sc,None)
    font.text(d,s,x,y,col,sc,None)
def ctext(d,s,y,col,sc=1): otext(d,s,(W-font.width(s,sc))//2,y,col,sc)
def hp_at(T):
    if T<19.3: return 9
    if T<20.3: return int(9+91*sm(seg01(T,19.3,20.3)))
    return 100
def hud(img,T):
    d=ImageDraw.Draw(img)
    if 5.6<=T<45.4:
        hp=hp_at(T); low=hp<30; col=RED if low else GRN
        if not (low and int(T*3)%2==0): otext(d,'HP',8,12,col,1)
        d.rectangle([22,12,84,18],fill=(0,0,0),outline=GRY); d.rectangle([23,13,23+int(60*hp/100),17],fill=col)
        if low and 6.0<T<16.8 and int(T*1.25)%2==0: otext(d,'DANGER',90,12,RED,1)
    if 45.4<=T<46.6:                                            # HP readout corrupts on LOAD
        rnd=np.random.default_rng(int(T*24)); s_=''.join(rnd.choice(list('HP-0#?'),6))
        otext(d,s_,8+int(rnd.integers(-2,3)),12,RED,1)
    def menu(sel,pressed,t0):
        u=sm(seg01(T,t0,t0+0.2)); y0=int(lerp(330,206,u))
        d.rectangle([40,y0,140,y0+42],fill=(14,4,6),outline=(170,30,36)); d.rectangle([42,y0+2,138,y0+40],outline=(70,14,18))
        for i,s_ in enumerate(('SAVE','LOAD')):
            c=WHT if i==sel else GRY
            if pressed and i==sel and int(T*12)%2==0: c=RED
            otext(d,s_,76,y0+9+i*14,c,1)
        x=66; y=y0+12+sel*14; d.polygon([(x,y-3),(x+4,y),(x,y+3)],fill=RED)
    if 18.3<=T<19.3: menu(0,T>=19.2,18.3)
    if 19.3<=T<20.6:
        u=sm(seg01(T,19.3,19.5)); d.rectangle([34,214,146,234],fill=(14,4,6),outline=(170,30,36)); ctext(d,'GAME SAVED.',221,WHT)
    if 43.6<=T<45.6: menu(0 if T<44.4 else 1,T>=45.3,43.6)
    if 45.6<=T<46.6:
        rnd=np.random.default_rng(int(T*24)+7); ox=int(rnd.integers(-3,4))
        d.rectangle([34+ox,214,146+ox,234],fill=(14,4,6),outline=(170,30,36)); txt='LOADING' if int(T*8)%3 else 'L0AD1NG'
        ctext(d,txt+'.'*(int(T*6)%4),221,WHT)
    if 4.0<=T<5.6:
        k=int((T-4.15)*18)
        if k>0:
            l1='ONE MINUTE'[:k]; l2='EARLIER'[:max(0,k-10)]
            otext(d,l1,(W-font.width('ONE MINUTE',2))//2,140,WHT,2)
            if l2: otext(d,l2,(W-font.width('EARLIER',2))//2,162,WHT,2)
    if 57.5<=T<58.6:
        if int(T*4)%2==0: ctext(d,'SAVE?',150,WHT,2)
        d.polygon([(52,156),(57,159),(52,162)],fill=RED)
    if T>=58.6:
        u=sm(seg01(T,58.6,59.0)); col=tuple(int(c*u) for c in RED)
        ctext(d,'THE LAST',138,col,2); ctext(d,'SAVE POINT',160,col,2)
    subtitle(d,T)
    return img
VOICE=os.environ.get('VOICE','kokoro')
if VOICE=='enes': _N=json.load(open('/home/claude/tts/enes/fx/script.json')); NARR=_N[:19]
else: NARR=json.load(open('/home/claude/tts/v5/script.json'))
HIL={'ME.','NINE','HP.','RED','SAVE','SAFE.','SAVED.','FOOTSTEPS.','ONLY','CRACK.','CLOTH.','IT','STOPPED.',"DIDN'T.",'BODY','MY','LOAD','OLD','FIRST.'}
WHISPER=(56.1,58.4,"DON'T SAVE HERE...") if VOICE=='enes' else (55.6,57.3,"DON'T SAVE HERE...")
def wrap(txt,n=26):
    out=[]; cur=''
    for w_ in txt.split():
        if len(cur)+len(w_)+(1 if cur else 0)>n: out.append(cur); cur=w_
        else: cur=(cur+' '+w_).strip()
    if cur: out.append(cur)
    return out
def subtitle(d,T):
    lines=None; red=False
    for key,t0,txt,dd in NARR:
        if t0<=T<t0+dd+0.25: lines=wrap(txt.upper().replace('...','..'))      # latest line that has started wins
    if lines is None and WHISPER[0]<=T<WHISPER[1]: lines=[WHISPER[2].replace('...','..')]; red=True
    if not lines: return
    y=272-11*(len(lines)-1)
    for ln in lines:
        xw=font.width(ln); x=(W-xw)//2; d.rectangle([x-3,y-2,x+xw+2,y+8],fill=(0,0,0)); cx=x
        for wd in ln.split(' '):
            col=(235,60,60) if red else ((255,214,90) if wd in HIL else WHT)
            otext(d,wd,cx,y,col,1); cx+=font.width(wd)+6
        y+=11
def ring_fx(img,vi,T,t0):
    """small light ring where a fist hits the crystal"""
    if vi is None: return img
    d=ImageDraw.Draw(img)
    for side,sx in ((0,-0.17),(1,0.17)):
        p=(T-t0)/0.42; k=int(math.floor(p)); f=p-k
        if k%2!=side or not (0.3<f<0.8): continue
        base=np.array(INSIDE); world=base+Ry(math.pi)@np.array([sx,1.62,-0.52])
        q=R.project(tuple(world),vi)
        if q:
            r=int(2+10*(f-0.3)); d.ellipse([q[0]-r,q[1]-r*0.7,q[0]+r,q[1]+r*0.7],outline=(255,190,190) if f<0.55 else (200,60,70))
    return img
def frame(T):
    img,vi=render(T)
    mode=orig(T)[0]
    if mode=='inside' and (T<4.0 or 49.0<=T<57.5) and shot(T) is not None: img=ring_fx(img,vi,T,0.0)
    if 45.3<=T<45.9:                                              # LOAD: tear the picture (motivated glitch only)
        a=np.asarray(img).copy(); rnd=np.random.default_rng(int(T*24))
        for _ in range(5):
            y=int(rnd.integers(0,H-8)); h=int(rnd.integers(2,8)); a[y:y+h]=np.roll(a[y:y+h],int(rnd.integers(-12,12)),axis=1)
        img=Image.fromarray(a)
    if 3.85<=T<4.0 or 57.35<=T<57.5: img=Image.fromarray((np.asarray(img)*0.0).astype(np.uint8))
    return hud(img,T)
TEST=os.environ.get('TEST')
if TEST:
    ims=[frame(float(x)) for x in TEST.split(',')]; sh=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): sh.paste(im,(i*182,0))
    sh.resize((sh.width*2,640),Image.NEAREST).save('test.png'); sys.exit()

if __name__=='__main__' and os.environ.get('PART') and os.environ.get('PART')!='audio':
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,('lse_' if VOICE=='enes' else 'ls_')+f'{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.92,vignette=0.45,grain=2.6,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(post.upscale(frame(f/FPS),S),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=21); sr=s.sr; n=s.n; t=s.t
    def nb(t0,d,lo,hi,v,seed,shape=2,pan=0.0): s.place(s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v,pan)
    def tone(t0,f,d,v,wave='sq',dec=6.0,pan=0.0):
        tt=s.T(d); ph=(f*tt)%1; x=np.where(ph<0.5,1.0,-1.0) if wave=='sq' else np.sin(2*np.pi*f*tt)
        s.place(x*np.exp(-tt*dec)*np.minimum(1,tt/0.003),t0,v,pan)
    def metal(t0,v=0.1,seed=0,pan=0.0,base=1.0):
        tt=s.T(0.45); x=sum(np.sin(2*np.pi*f*base*tt)*np.exp(-tt*dk) for f,dk in ((520,12),(830,16),(1370,20),(2210,26)))*0.3
        x+=s.filt_short(s.noise(0.45,seed),lo=800,hi=6000)*np.exp(-tt*40)*0.6; s.place(x,t0,v,pan)
    def step(t0,v=0.08,seed=0,pan=0.0,metal_k=0.4):
        tt=s.T(0.18); x=s.filt_short(s.noise(0.18,seed),lo=90,hi=1200)*np.exp(-tt*35)+np.sin(2*np.pi*75*tt)*np.exp(-tt*30)*0.8
        s.place(x,t0,v,pan); metal(t0+0.01,v*metal_k*0.5,seed+500,pan,1.3)
    def thud(t0,f=60,v=0.3,d=0.6): tt=s.T(d); s.place(np.sin(2*np.pi*f*tt*(1-0.3*tt/d))*np.exp(-tt*7),t0,v)
    # ---- low horror bed (drone + air), keeps running except in the silences ----
    drone=(np.sin(2*np.pi*41.2*t)+0.7*np.sin(2*np.pi*43.6*t)+0.35*np.sin(2*np.pi*61.7*t+np.sin(2*np.pi*0.13*t)))*0.03
    air=s.filt(s.rng.normal(0,1,n),lo=60,hi=500)*0.02
    tension=np.clip((t-36.9)/8.4,0,1)*(t<45.3)
    swell=np.sin(2*np.pi*(98+12*tension)*t)*0.012*tension+np.sin(2*np.pi*103.8*t)*0.012*tension
    corr=((t>=5.6)&(t<14.0)).astype(float); crack=np.zeros(n); rng=np.random.default_rng(5)
    for tc in rng.uniform(0,DUR,260): i=int(tc*sr); crack[i:i+200]+=rng.normal(0,1,200)*np.exp(-np.arange(200)/40)
    crack=s.filt(crack,lo=1500,hi=7000)*0.05
    s.L+=drone+air+swell+crack; s.R+=drone+np.roll(air,900)+swell+np.roll(crack,300)
    # ---- the pounding from inside the crystal: muffled + glassy ----
    def pound(t0,v=1.0):
        tt=s.T(0.35); x=s.filt_short(np.sin(2*np.pi*70*tt)*np.exp(-tt*16)+s.noise(0.35,int(t0*100))*np.exp(-tt*30)*0.4,hi=380)
        g=(np.sin(2*np.pi*2150*tt)+0.6*np.sin(2*np.pi*3310*tt))*np.exp(-tt*14)*0.12; s.place(x*0.9+g,t0,0.32*v)
    for k in range(200):
        tp=0.42*k+0.147
        if tp<3.85 or 49.0<=tp<57.3: pound(tp,0.35 if 55.3<tp<57.0 else (0.75 if 54<tp else 1.0))
    for k in range(6): step(0.2+k*0.42,0.012,700+k)                 # the copy leaving (hook, far)
    # ---- rewind ----
    tt=s.T(0.9); s.place(np.sin(2*np.pi*np.cumsum(2400-2100*tt/0.9)/sr)*0.3*np.sin(np.pi*tt/0.9)+s.filt_short(s.noise(0.9,9),lo=1000,hi=6000)*0.4*np.sin(np.pi*tt/0.9),4.15 if VOICE=='enes' else 4.0,0.12)
    # ---- corridor: limping steps, sword drag, heartbeat ----
    last=None
    for f in range(int(5.6*100),int(16.8*100)):
        T=f/100; k=int((orig_z(T)+15.5)/0.62)
        if last is not None and k!=last:
            loud=k%2==0; step(T,0.09 if loud else 0.05,k,0.0,0.6)
            if not loud: nb(T+0.05,0.35,1800,5200,0.02,900+k,shape=1)       # dragging foot
        last=k
    drag=s.filt(s.rng.normal(0,1,n),lo=2200,hi=6000)*(0.6+0.4*np.sin(2*np.pi*1.7*t))*((t>=5.6)&(t<16.8))*0.016
    s.L+=drag; s.R+=drag
    for k in range(17):
        tb=5.8+k*0.82
        if tb<19.3: v=0.32 if tb<16.8 else 0.2; thud(tb,52,v,0.3); thud(tb+0.22,48,v*0.7,0.3)
    nb(16.9,1.1,200,1800,0.05,30,shape=1)                                  # relief exhale
    # ---- save menu ----
    tone(18.3,660,0.08,0.035); tone(18.38,990,0.1,0.035)
    tone(19.2,1320,0.05,0.035)
    for k,f in enumerate([523,659,784,1047]): tone(19.3+k*0.09,f,0.25,0.03,dec=8)
    for k in range(10): tone(19.4+k*0.09,400+k*60,0.06,0.018)
    metal(20.85,0.2,40,-0.2); thud(20.85,90,0.08,0.2)                     # sword dropped
    metal(21.65,0.1,41,0.0,0.8); step(21.65,0.06,42)                       # sits down
    # ---- the copy approaches (steady, not limping), torches die ----
    last=None
    for f in range(2200,2760):
        T=f/100; z=-9.5+3.0*sm(seg01(T,22.0,27.6)); k=int((z+9.5)/0.62*2)
        if last is not None and k!=last: v=0.012+0.07*seg01(T,22.0,27.6); step(T,v,300+k,0.0,0.7)
        last=k
    for tc in TORCH_OUT.values(): nb(tc,0.5,60,700,0.18,int(tc*10),shape=1)
    tone(24.62,0,0.01,0.0)
    s.silence(27.6,28.6,level=0.0,ramp=0.02)                               # total silence before the silhouette
    for k in range(4): step(28.6+k*0.6,0.13,400+k,0.0,0.8)                 # steps into the light
    metal(29.4,0.12,50); metal(29.9,0.08,51)                               # original stands
    # ---- identical helmets / mirror ----
    for tc in (31.0,32.2): thud(tc,41,0.35,1.2); tone(tc,82,1.0,0.02,'sin',dec=2)
    for tc in (33.6,35.0): metal(tc,0.06,60,-0.3,0.9); metal(tc,0.06,60,0.3,0.9)     # same creak, both at once
    metal(36.0,0.07,61,0.3,0.9)                                             # only the original moves...
    metal(37.0,0.22,62,0.3,1.4); thud(37.0,70,0.2,0.4)                      # ...and gets yanked back
    rat=s.filt(s.rng.normal(0,1,n),lo=3000,hi=8000)*(np.sin(2*np.pi*23*t)>0.6)*((t>=36.9)&(t<46.3))*0.012
    s.L+=rat; s.R+=rat
    metal(38.3,0.05,63,-0.3); metal(38.3,0.05,63,0.3)
    for k in range(4): metal(40.6+0.28*k,0.1,70+k,0.0,0.8)
    for k in range(9): step(40.0+k*0.385,0.08,80+k,0.3,0.7)
    # ---- LOAD ----
    tone(43.6,660,0.08,0.035); tone(43.68,990,0.1,0.035); tone(44.4,880,0.05,0.035)
    tone(45.3,1320,0.05,0.04)
    tt=s.T(0.7); x=np.sin(2*np.pi*np.cumsum(1400-1250*tt/0.7)/sr); x=np.round(x*3)/3; x=np.repeat(x[::12],12)[:len(tt)]
    s.place(x*np.exp(-tt*2),45.35,0.12)
    seg_=s.filt_short(s.noise(0.08,99),lo=400,hi=5000)
    for k in range(6): s.place(seg_*0.8,45.35+k*0.09,0.08*(1-k/7))
    tt=s.T(2.3); wh=s.filt_short(s.noise(2.3,101),lo=300,hi=4000)*(tt/2.3)**2+np.sin(2*np.pi*np.cumsum(60+300*(tt/2.3)**2)/sr)*0.5*(tt/2.3)
    s.place(wh,46.3,0.16)
    thud(48.6,38,0.6,1.6); nb(48.6,0.8,80,900,0.2,102,shape=1)
    # ---- the copy leaves ----
    for k in range(10): step(50.2+k*0.4,0.08*(1-k/12),120+k,0.0,0.7)
    tt=s.T(0.8); s.place(np.sin(2*np.pi*np.cumsum(140+60*np.sin(2*np.pi*1.4*tt)+25*np.sin(2*np.pi*11*tt))/sr)*np.sin(np.pi*tt/0.8)*0.5,51.4,0.07)
    wind=s.filt(s.rng.normal(0,1,n),lo=300,hi=2500)*np.clip(np.array([door_open(x_) for x_ in t[::480]]).repeat(480)[:n],0,1)*0.03
    s.L+=wind; s.R+=np.roll(wind,700)
    thud(56.6,55,0.45,0.9); nb(56.6,0.4,80,1500,0.12,130)
    # ---- whisper ----
    a,ar=_sf.read('/home/claude/tts/v4/whisper_am_michael.wav'); a=a if a.ndim==1 else a.mean(1)
    a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a); a=s.filt_short(a,lo=500,hi=7000)
    if VOICE!='enes': s.place(a,55.6,0.5,-0.1); s.place(a,55.63,0.25,0.25)
    # ---- end ----
    s.silence(57.3,57.5,level=0.0,ramp=0.01)
    tone(57.5,660,0.08,0.03); tone(58.0,660,0.08,0.03)
    thud(58.6,36,0.5,1.4)
    s.reverb(0.35,length=2.2,decay=3.0)
    s.silence(27.6,28.55,level=0.0,ramp=0.03)
    # ---- narration (the original knight), dry-ish with a short stone echo; world ducks under it ----
    if VOICE=='enes':                                          # Enes' own recordings, already processed (fx/F*.wav, stereo)
        NL=np.zeros(n); NR=np.zeros(n); duck=np.ones(n)
        for key,t0,txt,dd in _N:
            a,ar=_sf.read(f'/home/claude/tts/enes/fx/{key}.wav')
            i=int(t0*sr); j=min(n,i+len(a)); NL[i:j]+=a[:j-i,0]; NR[i:j]+=a[:j-i,1]
            duck[max(0,i-int(0.08*sr)):min(n,i+int((dd+0.3)*sr))]=0.5
        duck=np.convolve(duck,np.ones(2400)/2400,'same')
        pk=max(np.max(np.abs(s.L)),np.max(np.abs(s.R))); g=pk*1.05/max(1e-6,np.max(np.abs(NL)),np.max(np.abs(NR)))
        s.L=s.L*duck+NL*g; s.R=s.R*duck+NR*g
        return s.save(path,peak=0.9)
    Nb=np.zeros(n); duck=np.ones(n)
    for key,t0,txt,dd in NARR:
        a,ar=_sf.read(f'/home/claude/tts/v5/{key}.wav'); a=a if a.ndim==1 else a.mean(1)
        a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a)
        i=int(t0*sr); j=min(n,i+len(a)); Nb[i:j]+=a[:j-i]
        duck[max(0,i-int(0.08*sr)):min(n,j+int(0.15*sr))]=0.55
    duck=np.convolve(duck,np.ones(2400)/2400,'same')
    echo=np.zeros(n); dly=int(0.11*sr); echo[dly:]=Nb[:-dly]*0.18; echo[2*dly:]+=Nb[:-2*dly]*0.08
    pk=max(np.max(np.abs(s.L)),np.max(np.abs(s.R)))
    g=pk*0.95/max(1e-6,np.max(np.abs(Nb)))
    s.L=s.L*duck+(Nb+echo)*g; s.R=s.R*duck+(Nb+np.roll(echo,300))*g
    return s.save(path,peak=0.9)
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'last_save_enes.wav' if VOICE=='enes' else 'last_save.wav'))); sys.exit()
