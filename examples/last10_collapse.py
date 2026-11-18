"""THE LAST 10 SECONDS - ep. 1 "The Dungeon Collapse" (series: The Last 10 Seconds, Insert Disc 2). 60 s PS1 comedy, 9:16, procedural (nightkit).
A knight has 10 game seconds to escape a collapsing dungeon and spends them looting (loss aversion). He escapes with one apple.
The HUD timer counts 10.0 -> 0.0 over the story (bullet time: ~5 story seconds per game second). Voice: python tools/tts/l10.py -> $TTS_DIR/l10/*.wav.
Reuses the locked knight from examples/final_boss.py. Run: TEST=1,12,25 python examples/last10_collapse.py -> test.png | PART=a:b | PART=audio"""
import os, sys, math, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','tts'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, quad
from nightkit import motion, post, font
from nightkit.zraster import zrender
from nightkit.audio import Sound, duck_envelope
import final_boss as FB

OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6; DUR=58.0; N=int(round(DUR*FPS))
PI=math.pi; sm=motion.smooth
def seg01(t,a,b): return max(0.0,min(1.0,(t-a)/(b-a)))
def lerp(a,b,u): return a+(b-a)*u
def lerp3(a,b,u): return tuple(a[i]+(b[i]-a[i])*u for i in range(3))
def hsh(i,s=0): v=math.sin(i*127.1+s*311.7)*43758.5453; return v-math.floor(v)
box=FB.box
WHT=(242,238,226); YEL=(255,210,60); RED=(240,50,40); GRN=(80,220,90); GRAY=(150,150,160)

# ======================= voice timings =======================
LINES=[('1',0.2),('2',5.1),('3',9.8),('4',15.4),('5',19.4),('6',23.2),('7',30.3),('8',35.6),('9',38.5),('10',41.4),('11',45.4),('12',48.5),('13',53.2)]
try: SCR=json.load(open(os.path.join(TTS_DIR,'l10','script.json')))
except Exception: SCR=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','tools','tts','scripts','l10_text.json')))
CUTS=[0.0,5.1,9.8,19.4,30.3,41.4,48.2,DUR]                       # 6 camera setups
T0,T1=1.0,51.5                                                   # the HUD timer: 10.0 at T0, 0.0 at T1
def timer(t): return max(0.0,10.0*(1-seg01(t,T0,T1)))

# ======================= the hall =======================
STONE=(86,78,84); STONE_D=(60,54,60); STONE_L=(112,102,106); WOOD=(98,66,38); IRON=(60,60,68); GOLD=(236,190,60); GOLD_D=(190,146,40)
HX=3.0; DOORZ=18.0; ZMIN=-2.0
def hall():
    Q=[]
    Q+=box(-HX-0.8,-HX,0,5.2,ZMIN,DOORZ+0.4,STONE_D)+box(HX,HX+0.8,0,5.2,ZMIN,DOORZ+0.4,STONE_D)           # side walls
    Q+=box(-HX,HX,5.0,5.6,ZMIN,DOORZ+0.4,STONE_D)                                                         # ceiling
    Q+=box(-HX,HX,0,5.2,ZMIN-0.8,ZMIN,STONE_D)                                                            # back wall
    for z in np.arange(-1,DOORZ,3.0):                                                                     # ceiling beams
        Q+=box(-HX,HX,4.5,5.0,z,z+0.35,(70,52,40))
    for z in np.arange(0.5,DOORZ,4.0):                                                                    # torches
        for sx in (-1,1):
            Q+=box(sx*(HX-0.05)-0.06,sx*(HX-0.05)+0.06,1.7,2.1,z-0.06,z+0.06,(70,50,34))+box(sx*(HX-0.05)-0.08,sx*(HX-0.05)+0.08,2.1,2.35,z-0.08,z+0.08,(255,150,40),emit=True)
    for z in np.arange(2.0,DOORZ,6.0):                                                                    # pillars along the walls
        for sx in (-1,1): Q+=box(sx*(HX-0.45)-0.3,sx*(HX-0.45)+0.3,0,4.5,z-0.3,z+0.3,STONE)
    return Q
HALL=hall()
FACADE=box(-HX-0.8,-1.5,0,6.0,DOORZ+0.4,DOORZ+0.9,STONE)+box(1.5,HX+0.8,0,6.0,DOORZ+0.4,DOORZ+0.9,STONE)+box(-1.5,1.5,3.9,6.0,DOORZ+0.4,DOORZ+0.9,STONE_L)+box(-HX-0.9,HX+0.9,5.9,6.3,ZMIN-0.9,DOORZ+1.0,STONE_D)
import copy
def sunk(Q,dy,tilt=0.0):
    Q=copy.deepcopy(Q); return FB.xform(Q,lambda p:(p[0],p[1]-dy-tilt*(p[2]-DOORZ),p[2]))
def tiles_static(): return [(i,j) for i in range(-3,3) for j in range(int(ZMIN),int(DOORZ))]
TILES=tiles_static()
def chest(x,y,z,s=1.0,lid=0.0,col=WOOD):
    w,h,d=0.8*s,0.45*s,0.5*s
    Q=box(x-w/2,x+w/2,y,y+h,z-d/2,z+d/2,col)+box(x-w/2-0.02,x+w/2+0.02,y+h*0.55,y+h*0.62,z-d/2-0.02,z+d/2+0.02,IRON)
    Q+=box(x-w/2,x+w/2,y+h,y+h+0.13*s,z-d/2,z+d/2,tuple(int(c*0.85) for c in col))+box(x-0.05*s,x+0.05*s,y+h*0.45,y+h*0.75,z-d/2-0.04,z-d/2,GOLD)
    return Q
def pile(x,z,s=1.0):
    Q=[]
    for k in range(7): Q+=box(x-0.5*s+0.11*s*k,x-0.3*s+0.11*s*k,0,0.18*s+0.1*s*hsh(k),z-0.35*s+0.2*s*hsh(k,1),z-0.1*s+0.2*s*hsh(k,1),GOLD if k%2 else GOLD_D)
    return Q

# ======================= knight state =======================
def zk_keys(): return [(0,2.2),(9.8,2.2),(14.9,2.9),(19.0,3.4),(30.3,3.4),(35.5,4.6),(38.2,11.5),(41.0,16.9),(46.3,16.9),(51.5,22.0),(DUR,23.0)]
ZK=zk_keys()
def zk(t):
    for (a,za),(b,zb) in zip(ZK,ZK[1:]):
        if a<=t<=b: return lerp(za,zb,sm(seg01(t,a,b)) if b-a>1.2 else seg01(t,a,b))
    return ZK[-1][1]
def xk(t):
    if t<9.8: return 0.5
    if t<14.9: return lerp(0.5,0.1,sm(seg01(t,10.5,14.9)))
    return 0.1
CH_BIG=(2.2,2.2)                                    # the first chest (key inside)
CH_SMALL=(-0.5,3.7)
N_LOOT=8
DROPS=[30.5]+[31.3+0.55*k for k in range(N_LOOT)]    # chest first, then the eight loot items from his back
def sack_count(t): return N_LOOT-sum(1 for d in DROPS[1:] if t>=d)
def carry_state(t):
    if 9.8<=t<16.0: return 'big'
    if 16.0<=t<30.5: return 'small'
    return 'none'
def kstate(t):
    d=dict(walk=0.0,run=0.0,lean=0.0,head=0.0,sit=0.0,rh=None,lh=None,sword='none'); yaw=PI/2; base=(xk(t),0.0,zk(t))
    c=carry_state(t)
    if t<9.8:                                                                  # loots the wall chests (facing +x), looks up at the alarm
        d['sit']=0.30+0.15*math.sin(t*3.0); d['lean']=0.25; ph=math.sin(t*5.0)
        d['rh']=(0.25,0.8+0.15*ph,0.5); d['lh']=(-0.25,0.8-0.15*ph,0.5)
        d['head']=0.0 if not 4.2<t<5.6 else -0.7*math.sin(PI*seg01(t,4.2,5.6))
    else:
        yaw=lerp(PI/2,0.0,sm(seg01(t,10.4,11.6)))                              # turns toward the exit
        if c in ('big','small'): d['rh']=(0.24,1.0,0.5); d['lh']=(-0.24,1.0,0.5)
        if t<30.3: d['walk']=(t*5.0) if (10.8<t<19.0) else 0.0; d['lean']=-0.2 if c=='big' else -0.1
        if 19.4<=t<30.3: d['head']=0.5*math.sin(t*1.3)
        if 30.3<=t<35.5:                                                       # drops things one by one, steps forward
            d['walk']=t*4; d['lean']=0.0; d['rh']=None if t>31.0 else d['rh']; d['lh']=None
        if 35.6<=t<41.2: d['run']=1.0; d['walk']=t*14; d['lean']=0.0
        if 41.2<=t<46.3:                                                       # at the locked door: tries the handle, looks back, thinks
            d['rh']=(0.2,1.0,0.5) if t<43.0 else None; d['head']=(0.0 if t<43.0 else -1.0*sm(seg01(t,43.0,43.8))*(1-sm(seg01(t,45.0,45.6))))
        if 46.2<=t<47.0:                                                       # the kick
            u=seg01(t,46.2,46.55); d['walk']=PI/2; d['lean']=-0.3*math.sin(PI*u); base=(xk(t),0.0,zk(t)+0.4*u)
        if t>=47.0: d['run']=1.0 if t<51.5 else 0.0; d['walk']=t*14 if t<51.5 else 0.0; d['lean']=0.0
        if t>=52.4: d['rh']=(0.28,1.25,0.32); d['head']=0.3                    # raises the apple
    return dict(base=base,yaw=yaw,**d)
def tspace(base,yaw,lean=0.0,run=0.0,sit=0.0):
    b=np.array(base,float); Rb=FB.Ry(yaw); hip=0.82-0.42*sit
    def T(p):
        p=np.array(p,float); piv=np.array([0,hip,0]); return tuple(b+Rb@(piv+FB.Rx(lean+0.22*run)@(p-piv+np.array([0,hip-0.82,0]))))
    return T
def kmodel(**st):
    st=dict(st); Q=FB.knight(**st); T=tspace(st['base'],st['yaw'],st.get('lean',0.0),st.get('run',0.0),st.get('sit',0.0))
    Q+=box(-0.2,-0.16,0.82,0.9,0.1,0.14,(220,40,40),xf=T)+box(-0.18,-0.17,0.9,0.94,0.11,0.12,(60,140,50),xf=T)       # the apple on his belt
    return Q
def knight_items(t,st):
    """what he carries: held chest, loot sack on his back"""
    T=tspace(st['base'],st['yaw'],st.get('lean',0.0),st.get('run',0.0),st.get('sit',0.0)); Q=[]; c=carry_state(t)
    if c=='big': Q+=box(-0.4,0.4,0.85,1.3,0.45,0.95,WOOD,xf=T)+box(-0.42,0.42,1.3,1.43,0.45,0.95,(84,56,32),xf=T)+box(-0.42,0.42,1.0,1.06,0.43,0.97,IRON,xf=T)
    if c=='small': Q+=box(-0.25,0.25,0.9,1.2,0.4,0.78,WOOD,xf=T)+box(-0.26,0.26,1.2,1.3,0.4,0.78,(84,56,32),xf=T)
    if t>=52.4: Q+=box(0.22,0.34,1.22,1.34,0.26,0.38,(230,40,40),xf=T)+box(0.27,0.29,1.34,1.38,0.3,0.32,(60,140,50),xf=T)    # the apple, raised
    n=sack_count(t) if t>=0 else N_LOOT
    if n>0:
        s=0.18+0.025*n; Q+=box(-s/2,s/2,0.8,0.8+s*1.1,-0.14-0.5*s,-0.13,(150,120,80),xf=T)
        for k in range(min(n,8)): Q+=box(-0.15+0.09*(k%4),-0.08+0.09*(k%4),0.8+s*1.1+0.0,0.8+s*1.1+0.12+0.05*(k//4),-0.26,-0.18,LOOT[k][1],xf=T)
    return Q
LOOT=[('sword',(205,214,226)),('helmet',(150,152,170)),('potion',(70,200,90)),('crown',GOLD),('book',(120,60,50)),('gem',(80,220,240)),('sack',(190,160,100)),('coins',GOLD_D)]
def loot_floor(t,st):
    """dropped items: arc from his back to a resting place, then they fall with their tile when the floor goes"""
    Q=[]
    for k,td in enumerate(DROPS[1:]):
        if t<td: continue
        T=tspace(*[(xk(td),0.0,zk(td)),0.0][:1],0.0) if False else None
        rest=(xk(td)-0.5+0.28*(k%4)*(1 if k%2 else -1)+0.2,0.0,zk(td)-0.7-0.25*(k//3))
        u=seg01(t,td,td+0.4); start=(xk(td),1.0,zk(td)-0.4); p=lerp3(start,rest,u); p=(p[0],p[1]+0.5*math.sin(PI*u)+(0.06 if u>=1 else 0),p[2])
        y=p[1]-tile_fall(rest[2],t)
        Q+=box(p[0]-0.1,p[0]+0.1,y,y+0.12+(0.35 if k==0 else 0),p[2]-0.1,p[2]+0.1,LOOT[k][1])
    if t>=DROPS[0]:                                                               # the chest he dropped
        u=seg01(t,DROPS[0],DROPS[0]+0.45); rest=(xk(DROPS[0]),0.0,zk(DROPS[0])-0.9); p=lerp3((rest[0],1.0,rest[2]+0.7),rest,u)
        Q+=chest(p[0],p[1]-tile_fall(rest[2],t),p[2],0.65)
    return Q
# ======================= collapse =======================
def tile_drop_time(j):
    """a tile starts to fall once the knight is 3 m past it (only after the sprint begins)"""
    zt=j+3.0
    for tt in np.arange(35.6,DUR,0.05):
        if zk(tt)>=zt: return tt+0.25*hsh(j)
    return 1e9
TDROP={j:tile_drop_time(j) for j in range(int(ZMIN),int(DOORZ))}
def tile_fall(z,t):
    j=int(math.floor(z)); td=TDROP.get(j,1e9)
    return 0.5*5.0*max(0.0,t-td)**2 if t>td else 0.0
STONES=[]
for i in range(60):
    ts=5.0+i*0.9+hsh(i)*0.6
    if ts>DUR-2: break
    a=hsh(i,2); b=hsh(i,3); dx=(a-0.5)*5.2; dz=(b-0.5)*7.0
    if abs(dx)<0.9 and abs(dz)<0.9: dx+=1.4*(1 if dx>=0 else -1)
    STONES.append((ts,dx,dz,0.25+0.35*hsh(i,4)))
def stone_boxes(t):
    Q=[]
    for ts,dx,dz,s in STONES:
        if t<ts: continue
        z=zk(ts+0.9)+dz; x=max(-2.5,min(2.5,xk(ts)+dx)); z=min(z,DOORZ-1.0)
        u=t-ts; y=5.0-0.5*14.0*u*u*3; y=max(y,0.0)
        if y>5.0: continue
        yy=y-tile_fall(z,t)
        if yy<-6: continue
        Q+=box(x-s,x+s,yy,yy+s*1.3,z-s,z+s,STONE_L if int(ts*7)%2 else STONE)
    return Q
def impacts(t):
    ev=[ts+0.65 for ts,_,_,_ in STONES]
    return ev
def shake_px(t):
    best=(0.0,0.0)
    for e in impacts(t):
        k=motion.kick(t,e,1.6,7,FPS)
        if k: best=(0.0,k)
    for e in (DROPS[0]+0.4,46.4,49.5):
        k=motion.kick(t,e,2.4,7,FPS)
        if k: best=(0.0,k)
    return best

# ======================= door, outside =======================
def door_open(t): return sm(seg01(t,46.4,47.3))
def door(t):
    u=door_open(t); ang=u*1.5; Q=[]
    for sx in (-1,1):                                                         # two leaves hinged at x=+-1.2, swinging outward (+z)
        hx=sx*1.2
        def rot(p,sx=sx,hx=hx):
            x,y,z=p; dx=x-hx; dz=z-DOORZ; c,s_=math.cos(-sx*ang),math.sin(-sx*ang); return (hx+dx*c-dz*s_,y,DOORZ+dx*s_+dz*c)
        x0,x1=(hx-1.2,hx) if sx==-1 else (hx,hx+1.2)
        Q+=box(x0,x1,0,3.4,DOORZ-0.12,DOORZ+0.12,WOOD,xf=rot)+box(x0,x1,0.6,0.8,DOORZ-0.14,DOORZ+0.14,IRON,xf=rot)+box(x0,x1,2.4,2.6,DOORZ-0.14,DOORZ+0.14,IRON,xf=rot)
    Q+=box(-1.2-0.3,-1.2,0,3.7,DOORZ-0.3,DOORZ+0.3,STONE_L)+box(1.2,1.2+0.3,0,3.7,DOORZ-0.3,DOORZ+0.3,STONE_L)+box(-1.5,1.5,3.4,3.9,DOORZ-0.3,DOORZ+0.3,STONE_L)
    if u<0.05: Q+=box(-0.2,0.2,1.1,1.5,DOORZ-0.2,DOORZ-0.1,(40,40,46))+box(-0.05,0.05,1.2,1.3,DOORZ-0.22,DOORZ-0.2,GOLD)     # lock
    return Q
def outside():
    Q=[]
    for i in range(-10,10):
        for j in range(18,40,2): Q.append(quad([(i*2,0,j),(i*2+2,0,j),(i*2+2,0,j+2),(i*2,0,j+2)],(92,150,64) if (i+j//2)%2 else (80,136,56)))
    Q+=box(-1.2,1.2,0,0.01,DOORZ,DOORZ+1.0,(150,122,80))
    return Q
OUTSIDE=outside()
LIGHTS_T=[((0.0,3.5,z),(255,150,60),0.7) for z in (2.0,8.0,14.0)]

# ======================= cameras =======================
def creep(t,t0,rate=0.0014): return motion.creep(t,t0,rate,FPS)
def cam_shot(t):
    zkn=zk(t); xkn=xk(t)
    if t<CUTS[1]:  # CAM 1: close three-quarter on the looting knight, big in frame 0, slow push
        tgt=(xkn,1.0,zkn); pos=motion.dolly((1.5,1.35,zkn-1.6),tgt,creep(t,0.0,0.0022)); return dict(cam=pos,tgt=tgt,fov=60)
    if t<CUTS[2]:  # CAM 2: wide side view of the hall: crumbling ceiling, far exit
        tgt=(0.0,1.5,8.0); pos=motion.dolly((-2.7,2.4,2.4),tgt,creep(t,CUTS[1],0.0012)); return dict(cam=pos,tgt=tgt,fov=74)
    if t<CUTS[3]:  # CAM 3: side-medium on the chest struggle (tracks him slowly)
        tgt=(xkn,1.0,zkn+0.2); pos=motion.dolly((-1.9+0.2*seg01(t,CUTS[2],CUTS[3]),1.25,zkn-1.3),tgt,creep(t,CUTS[2],0.0014)); return dict(cam=pos,tgt=tgt,fov=56)
    if t<CUTS[4]:  # CAM 4: front-low orbit for the thought beat (loss aversion), glide halfway
        g=motion.glide(seg01(t,26.0,28.5)); tgt=(xkn,1.1,zkn); pos0=lerp3((1.1,1.0,zkn+1.9),(-1.0,1.15,zkn+1.8),g)
        return dict(cam=motion.dolly(pos0,tgt,creep(t,CUTS[3],0.0012)),tgt=tgt,fov=56)
    if t<CUTS[5]:  # CAM 5: tracking from the side-front, he sprints, floor collapses behind
        ahead=min(zkn+1.6,DOORZ-1.2); tgt=(xkn,1.0,min(zkn+0.6,DOORZ-0.5)); pos=(-1.7,1.25,ahead); return dict(cam=pos,tgt=tgt,fov=64)
    if t<CUTS[6]:  # CAM 6: the locked door, close; the kick; the door flies open
        tgt=(0.0,1.3,DOORZ-0.4); pos=motion.dolly((-1.9,1.35,DOORZ-3.4),tgt,creep(t,CUTS[5],0.0012)); return dict(cam=pos,tgt=tgt,fov=62)
    # CAM 7 (outside, daylight): he runs out toward the camera while the dungeon collapses behind; pulls back
    g=motion.glide(seg01(t,52.5,55.5)); tgt=lerp3((0.0,1.3,DOORZ+3.0),(0.2,1.5,DOORZ+4.2),g); pos=lerp3((2.4,1.4,DOORZ+10.5),(2.0,1.8,DOORZ+8.2),g)
    return dict(cam=pos,tgt=tgt,fov=lerp(60,64,g))

# ======================= render =======================
R=Renderer(W,H,fog=(40,30,28)); R_OUT=Renderer(W,H,fog=(176,206,236))
def render3d(t):
    sh=cam_shot(t); cam=Camera.look(sh['cam'],sh['tgt']); st=kstate(t); out=t>=48.2
    tiles=[]
    for i,j in TILES:
        td=TDROP.get(j,1e9)
        if t>=td+0.9 and (t-td)>1.6: continue
        f=0.5*5.0*max(0.0,t-td)**2 if t>td else 0.0; tilt=min(0.8,(t-td)*0.9) if t>td else 0.0
        a=0.5 if (i+j)%2 else 0.0; col=(96,88,96) if (i+j)%2 else (80,72,82)
        dy=-f; zt=tilt*0.5
        tiles.append(quad([(i,dy,j+zt),(i+1,dy,j+zt),(i+1,dy-zt,j+1),(i,dy-zt,j+1)],col))
    held=knight_items(t,st)
    layers=[HALL,tiles,pile(2.55,0.8,1.2)+pile(2.5,5.0,1.0)+pile(-2.5,1.5,1.1),
            (chest(2.2,0,0.9)+chest(2.4,0,3.4,0.9)+chest(-2.3,0,3.0)+chest(-0.5,0,3.7,0.6) if t<9.8 else (chest(2.4,0,3.4,0.9)+chest(-2.3,0,3.0)+chest(-0.5,0,3.7,0.6) if t<10.8 else chest(2.4,0,3.4,0.9)+chest(-2.3,0,3.0)) ),
            chest(CH_BIG[0],0,CH_BIG[1],1.1) if t<10.0 else (chest(CH_BIG[0],lerp(0,0,0),CH_BIG[1],1.1) if False else []),
            stone_boxes(t),door(t),kmodel(**st),held,loot_floor(t,st)]
    if t>=15.4 and t<16.2: layers.append(chest(xk(t)-0.2,0,zk(t)+0.7,1.1))                   # he sets the big chest down
    if t>=16.2 and t<30.5 and False: pass
    if 16.2<=t: layers.append(chest(0.4,0,2.6,1.1))                                            # ...and leaves it
    alarm=0.5+0.5*math.sin(t*6.0)
    L=[((0.0,3.8,zk(t)),(255,120+int(40*alarm),110),0.7+0.5*alarm)]+[((0.0,3.5,z),(255,170,90),0.7) for z in (zk(t)+3.0,zk(t)-3.0)]
    if out:
        dy=0.0 if t<50.6 else 0.6*(t-50.6)**2*2.0
        layers=[OUTSIDE,sunk(HALL,dy,0.0) if dy>0 else HALL,sunk(FACADE,dy,0.0) if dy>0 else FACADE,(sunk(door(t),dy) if dy>0 else door(t)),kmodel(**st),knight_items(t,st)]; L=[((20,40,-10),(255,250,230),3.0)]
    Rr=R_OUT if out else R
    img,vi,zb=zrender(Rr,cam,layers,L,fov=sh['fov'],fog_start=7,fog_end=30,ambient=0.62 if not out else 0.75,shake=shake_px(t),return_z=True)
    a=np.asarray(img).astype(np.float32); yy=np.linspace(0,1,H)[:,None,None]
    sky=(np.array([92,150,226])*(1-yy)+np.array([196,222,244])*yy) if (out or t>=47.0) else np.array([30,24,24])*np.ones((1,1,1))
    a=np.where((zb==0)[...,None],sky*np.ones((1,W,1)),a)
    if not out and t>=46.4: a=a+door_open(t)*0.0
    if not out and 0.3<t<48: a=a*np.array([1.0+0.05*math.sin(t*6.0),0.98,0.98])                    # alarm tint
    return post.ps1(Image.fromarray(np.clip(a,0,255).astype(np.uint8))),vi

# ======================= HUD / UI =======================
def otext(d,s,x,y,col,sc=1):
    o=max(1,sc//2)
    for ox,oy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)): font.text(d,s,x+ox*o,y+oy*o,(0,0,0),sc,None)
    font.text(d,s,x,y,col,sc,None)
def ctext(d,s,y,col,sc=1): otext(d,s,(W-font.width(s,sc))//2,y,col,sc)
def hud(d,t,vi):
    v=timer(t); blink=(v<3.0 and int(t*4)%2==0)
    ctext(d,'THE LAST 10 SECONDS',6,WHT,1)
    col=RED if (v<3.0 and not blink) else (YEL if v>=3 else WHT)
    ctext(d,f'{v:04.1f}',16,col,3)
    if 2.0<t<9.8 and int(t*3)%2==0: ctext(d,'DUNGEON COLLAPSING',42,RED,1)
    if 9.9<t<14.0: ctext(d,'OVERENCUMBERED!',50,RED,1)
    if 11.0<t<15.0: otext(d,'SPEED 10%',6,64,YEL)
    if 16.4<t<19.0: otext(d,'STILL 90%',6,64,YEL)
    if 23.8<t<29.8:                                                          # loss aversion: +10 vs -10
        ctext(d,'GOT 10 GOLD',72,GRN,1)
        if t>=25.6: ctext(d,'LOST 10 GOLD',92,RED,2 if int(t*6)%2 else 1)
        if t>=27.4: ctext(d,'LOSS HURTS 2X',130,YEL,1)
    if 41.8<t<45.2 and int(t*3)%3: ctext(d,'LOCKED',64,RED,2)
    if 43.4<t<45.6:                                                          # the key is in the first chest
        ctext(d,'KEY: IN CHEST 1',130,YEL,1)
    if 46.5<t<47.2: ctext(d,'KICK!',110,YEL,3)
    if 51.5<=t<DUR:
        ctext(d,'LOOT: 0',200,GRAY,1)
        if t>=52.6: ctext(d,'APPLE: 1',212,GRN,2)
    if t>=55.6: ctext(d,'INVENTORY 1/1',232,WHT,1)
# ======================= subtitles (1080x1920, 1.25x) =======================
SUB_F=7.5; HIL={'SECONDS','LOOTING','OVERENCUMBERED','LOSS','AVERSION','DROP','APPLE','DOOR','LOCKED','KEY','ZERO','SPRINTS','COLLAPSES'}
def _rows(text,n=20):
    out=[]; c=[]
    for w_ in text.split():
        if len(' '.join(c+[w_]))>n and c: out.append(c); c=[w_]
        else: c.append(w_)
    return out+[c]
def _split_line(k,t0):
    import re
    txt=SCR['text'][k]; dur=SCR['dur'][k]; sents=[s.strip() for s in re.split(r'(?<=[.!?])\s+',txt) if s.strip()]
    tot=sum(len(s) for s in sents); a=t0; res=[]
    for s in sents:
        b=a+dur*len(s)/tot; res.append((a-0.03,b+0.2 if s is sents[-1] else b,s)); a=b
    return res
SUBS=[(a_,b_,_rows(tx),k) for k,t0 in LINES for a_,b_,tx in _split_line(k,t0)]
def sub_overlay(t):
    for a,b,rows,key in SUBS:
        if a<=t<b:
            sc=SUB_F; lines=[' '.join(r) for r in rows]; lh=9.4*sc; pad=2*sc; wmax=max(font.width(l,sc) for l in lines)
            w=wmax+2*pad; h=(len(lines)-1)*lh+7*sc+2*pad; x0=(W*S-w)/2; y0=H*S-36-h
            ov=Image.new('RGB',(W*S,H*S),(0,0,0)); m=Image.new('L',(W*S,H*S),0); do=ImageDraw.Draw(ov); dm=ImageDraw.Draw(m)
            dm.rectangle([round(x0),round(y0),round(x0+w)-1,round(y0+h)-1],fill=255)
            for i,r in enumerate(rows):
                x=x0+pad
                for wd in r:
                    col=YEL if wd.upper().strip('.,!?:') in HIL else WHT; font.check(wd)
                    for k_,ch in enumerate(wd.upper()):
                        for j,row in enumerate(font.FONT[ch]):
                            for i2,bit in enumerate(row):
                                if bit=='1':
                                    X=x+(k_*6+i2)*sc; Y=y0+pad+i*lh+j*sc; bx=[round(X),round(Y),round(X+sc)-1,round(Y+sc)-1]; do.rectangle(bx,fill=col); dm.rectangle(bx,fill=255)
                    x+=font.width(wd,sc)+6*sc
            return ov,m
    return None
def frame_low(t):
    img,vi=render3d(t); d=ImageDraw.Draw(img); hud(d,t,vi); return img
def frame_final(t):
    arr=post.upscale(frame_low(t),S); so=sub_overlay(t)
    if so: m=np.asarray(so[1])>0; arr[m]=np.asarray(so[0])[m].astype(np.float32)
    return arr
def frame(t):
    img=frame_low(t); so=sub_overlay(t)
    if so: ov=so[0].resize((W,H),Image.BOX); m=so[1].resize((W,H),Image.BOX).point(lambda v:255 if v>100 else 0); img.paste(ov,(0,0),m)
    return img

TEST=os.environ.get('TEST')
if TEST and __name__=='__main__':
    ims=[frame(float(x)) for x in TEST.split(',')]; shp=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): shp.paste(im,(i*182,0))
    shp.resize((shp.width*2,640),Image.NEAREST).save('test.png'); sys.exit()

# ======================= QA manifest =======================
def _geom(t,name,st,V):
    out=[]
    if V[:,1].min()<-0.04-tile_fall(st['base'][2],t): out.append(('floor',f'{name} under the floor'))
    if (np.abs(V[:,0])>HX-0.05).any() and st['base'][2]<DOORZ-0.5: out.append(('wall',f'{name} inside a hall wall'))
    return out
QA=dict(fps=FPS,dur=DUR,W=W,frame=frame,chars={'knight':(kstate,kmodel,'sword','none')},geom=_geom,camera=lambda t: cam_shot(t)['cam'],min_cam_dist=0.4,
    camera_ok=lambda p: -HX<p[0]<HX+0.5 and -2.0<p[2]<45 and 0.1<p[1]<5,allow_jump=[('knight',c+d/FPS) for c in CUTS for d in range(3)],weapon_events=[],
    scenes=[dict(id=f's{i}',t0=CUTS[i],t1=CUTS[i+1],action=a) for i,a in enumerate(('hook: loots, alarm, timer 10 (CAM 1)','wide: ceiling crumbles, exit far (CAM 2)','chest struggle, overencumbered (CAM 3)','thinks: loss aversion, drops one by one (CAM 4)','sprint, floor collapses (CAM 5)','locked door, key in chest 1, kick (CAM 6)','daylight: escapes with one apple (CAM 7)'))],
    texts=lambda: [('hud','THE LAST 10 SECONDS',1),('hud','DUNGEON COLLAPSING',1),('hud','OVERENCUMBERED!',1),('hud','LOSS HURTS 2X',1),('hud','KEY: IN CHEST 1',1),('hud','INVENTORY 1/1',1),('hud','APPLE: 1',2),('hud','LOST 10 GOLD',2),('hud','09.9',3)])

# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=41); sr=s.sr; n=s.n; t=s.t; BED=np.zeros(n); FX=np.zeros(n)
    def nb(buf,t0,d,lo,hi,v,seed,shape=2):
        x=s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape; i=int(t0*sr); j=min(n,i+len(x)); buf[i:j]+=(x*v)[:j-i]
    def tone(buf,t0,m,d,v,wave='sq',duty=0.5,dec=3.0,att=0.005):
        f=440*2**((m-69)/12); tt=s.T(d); ph=(f*tt)%1; x=np.where(ph<duty,1.0,-1.0) if wave=='sq' else (4*np.abs(ph-0.5)-1 if wave=='tri' else np.sin(2*np.pi*ph))
        e=np.minimum(1,tt/att)*np.exp(-tt*dec); i=int(t0*sr); j=min(n,i+len(tt)); buf[i:j]+=(x*e*v)[:j-i]
    def thud(t0,f=55,v=0.3,d=0.6): tt=s.T(d); x=np.sin(2*np.pi*f*tt*(1-0.3*tt/d))*np.exp(-tt*8)+s.filt_short(s.noise(d,int(t0*13)),lo=60,hi=700)*np.exp(-tt*12)*0.6; i=int(t0*sr); j=min(n,i+len(tt)); FX[i:j]+=(x*v)[:j-i]
    def clank(t0,v=0.15,seed=0): tt=s.T(0.5); x=sum(np.sin(2*np.pi*f*tt)*np.exp(-tt*k) for f,k in ((310,6),(820,9),(1490,14)))*0.4+s.filt_short(s.noise(0.5,seed),lo=1200,hi=6000)*np.exp(-tt*30); i=int(t0*sr); j=min(n,i+len(tt)); FX[i:j]+=(x*v)[:j-i]
    def step(t0,v=0.05,seed=0): tt=s.T(0.12); x=s.filt_short(s.noise(0.12,seed),lo=900,hi=5000)*np.exp(-tt*45)+np.sin(2*np.pi*2300*tt)*np.exp(-tt*60)*0.3; i=int(t0*sr); j=min(n,i+len(tt)); FX[i:j]+=(x*v)[:j-i]
    ramp=np.clip((t-1)/40,0,1)                                                               # the collapse rumble grows
    BED+=s.filt(s.rng.normal(0,1,n),lo=30,hi=220)*(0.08+0.25*ramp)*(0.8+0.2*np.sin(2*np.pi*0.4*t))
    BED+=s.filt(s.rng.normal(0,1,n),lo=1500,hi=6000)*0.01*ramp
    for i in range(0,int(DUR*2)):                                                            # alarm siren: two-tone pulse until the door opens
        t0=i*0.5
        if 0.5<t0<46.4: tone(FX,t0,(81 if i%2 else 76),0.28,0.02,'sq',dec=2.0)
    for k in range(10): tone(FX,T0+k*(T1-T0)/10.0,93,0.08,0.05,'sq',dec=25)                  # one tick per game second
    for ts,dx,dz,sz in STONES:                                                               # falling stones
        thud(ts+0.65,45+int(30*hsh(int(ts*10))),0.15+0.3*sz,0.5); nb(FX,ts+0.65,0.3,200,2500,0.05,int(ts*10))
    thud(DROPS[0]+0.4,40,0.4,0.6); clank(DROPS[0]+0.4,0.12,3)
    for k,td in enumerate(DROPS[1:]): clank(td+0.35,0.06,10+k)                               # loot clatters
    tone(FX,9.95,70,0.2,0.05,'sq',dec=12); tone(FX,10.15,64,0.3,0.05,'sq',dec=8)             # OVERENCUMBERED
    for k in range(18): step(10.8+k*0.45,0.035,40+k)                                         # heavy slow steps
    for k in range(14): step(35.7+k*0.2,0.05,70+k)                                           # sprint
    for tf in np.arange(36.8,41.0,0.5): nb(FX,tf,0.8,100,900,0.06,int(tf*10),1)               # floor crumbling behind
    tone(FX,43.6,60,0.15,0.05,'sq',dec=12); tone(FX,43.8,55,0.4,0.05,'sq',dec=6)            # locked
    thud(46.4,35,0.9,0.9); clank(46.4,0.4,31); nb(FX,46.4,0.5,300,3000,0.12,77)             # the kick
    tt=s.T(1.2); i=int(46.6*sr); FX[i:i+len(tt)]+=np.sin(2*np.pi*np.cumsum(80+30*tt)/sr)*np.sin(np.pi*tt/1.2)*0.12      # door creak open
    for k in range(10): step(48.3+k*0.2,0.05,90+k)
    thud(51.4,30,0.9,1.4); nb(FX,51.2,1.8,40,500,0.3,81,1)                                    # the dungeon finally collapses
    for k,tb in enumerate((52.9,53.6)): tone(FX,tb,60+k*4,0.1,0.03,'sq',dec=15)              # apple crunch-ish
    for k,m in enumerate((72,76,79,84)): tone(FX,55.7+k*0.08,m,0.5,0.05,'sin',dec=4)         # inventory chime
    for m in (60,64,67): tone(FX,55.9,m,2.2,0.04,'sin',dec=1.2,att=0.05)                       # soft closing chord (keeps the ending from going silent)
    out=np.clip((t-48.2)/0.4,0,1); BED_m=BED*(1-0.85*out)
    wind=s.filt(s.rng.normal(0,1,n),lo=200,hi=1500)*0.16*out
    for k in range(14):
        tc=49.0+k*0.65+0.3*hsh(k); tt=s.T(0.14); i=int(tc*sr)
        if i+len(tt)<n: FX[i:i+len(tt)]+=np.sin(2*np.pi*np.cumsum(2800+900*np.sin(2*np.pi*18*tt))/sr)*np.exp(-tt*18)*0.03        # birds
    for k,tb in enumerate((52.0,52.9,54.1)): thud(tb,38+4*k,0.12,0.5)                                                # the last stones settle
    NB=np.zeros(n); wins=[]
    for k_,t0 in LINES:
        a,ar=_sf.read(os.path.join(TTS_DIR,'l10',f'{k_}.wav')); a=a if a.ndim==1 else a.mean(1)
        a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a); i=int(t0*sr); j=min(n,i+len(a)); NB[i:j]+=a[:j-i]; wins.append((t0,t0+len(a)/sr))
    g=duck_envelope(n,sr,wins,-4.0,0.05,0.25); bed=(BED_m+wind)*g; fx=FX*(0.5+0.5*g)
    L=bed+fx; R_=np.roll(bed,700)+np.roll(fx,200); pk=max(np.abs(L).max(),np.abs(R_).max()); gv=pk*1.6/np.abs(NB).max()
    s.L=L+NB*gv; s.R=R_+NB*gv; s.reverb(0.12,length=1.2,decay=3.0)
    return s.save(path,peak=0.9)
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'last10_collapse.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'l10_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.96,vignette=0.25,grain=1.5,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(frame_final(f/FPS),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
