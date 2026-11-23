"""WHY DOES THE TUTORIAL GUY NEVER COME WITH YOU? (Insert Disc 2, 14-day test day 3, 22:00 slot, Tone 2.0 + Format 3.0) ~37 s final (build x1.2), PS1 drama, 9:16.
Brief: briefs/tutorial_guy.md. An old tutorial guide says "Press SPACE to jump!" to every hero at the fence; ten thousand jumped and never looked back.
Forty years ago he tried it himself, saw the first slime and froze. One knight jumps, turns back and holds out a hand: he takes ONE step and now leaves the gate open.
Format 3.0: constant camera (Path through keys: the speed never drops to zero), subject (the guide) in the middle third, group framing (look.follow_group) when a helper enters,
character cards (briefs/tutorial_guy.md), several voices (tools/tts/tg.py + multi.py), 270x480 + depth outline (nightkit/look.py), finished video x1.2 afterwards.
Run: TEST=1,5,9 python examples/tutorial_guy.py -> test_tg.png | PART=a:b | PART=audio | tools/render_parts.py --prefix tg --audio tutorial_guy.wav"""
import os, sys, math, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','tts'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, quad, tiled_plane
from nightkit import motion, post, font, look
from nightkit.zraster import zrender
from nightkit.audio import Sound, duck_envelope
import final_boss as FB
import npc_well as NW

OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=270,480,4
PI=math.pi; sm=motion.smooth
def seg01(t,a,b): return max(0.0,min(1.0,(t-a)/(b-a))) if b>a else (1.0 if t>=b else 0.0)
def lerp(a,b,u): return a+(b-a)*u
def lerp3(a,b,u): return tuple(a[i]+(b[i]-a[i])*u for i in range(3))
def hsh(i,s=0): v=math.sin(i*127.1+s*311.7)*43758.5453; return v-math.floor(v)
box=FB.box; xform=FB.xform; seg=FB.seg
WHT=(242,238,226); GOLD=(255,204,64)
COL={'N':WHT,'G':(255,204,64),'H1':(255,96,88),'H2':(90,190,255),'H3':(196,120,255),'K':(176,206,255)}      # subtitle colour = speaker

# ======================= voice timings (tools/tts/tg.py) =======================
SCR=json.load(open(os.path.join(TTS_DIR,'tg','script.json')))
KEYS=['1','2','3a','3b','3c','4','5','6','7','8','9','10','11','12','13']
GAP=0.3; EXTRA={'1':0.35,'3b':0.55,'3c':0.9,'4':0.7,'6':0.7,'7':0.9,'8':0.5,'9':1.2,'10':0.3,'11':0.5,'12':1.1}
def _lines():
    t=0.12; out=[]
    for k in KEYS: out.append((k,round(t,3))); t+=SCR['dur'][k]+GAP+EXTRA.get(k,0.0)
    return out
LINES=_lines(); T0=dict(LINES)
DUR=round(T0['13']+SCR['dur']['13']+1.5,2); N=int(round(DUR*FPS))
def ws(k,i): return T0[k]+SCR['sent'][k][i][0]
def we(k,i): return T0[k]+SCR['sent'][k][i][1]

# ======================= world / story events =======================
GS=(1.9,0.0,-0.7); FX=3.0; LZ=0.7                       # guide's spot, fence line x = FX (runs along z), hero lane z = LZ
Y_WATCH=-2.07; Y_EAST=-4.71; Y_WEST=-1.57               # body yaw: watching the heroes (3/4 to the camera) | facing the grass (+x) | facing west (-x)
HERO=[dict(cape=(206,60,52),kind='run'),dict(cape=(50,160,190),kind='nerve'),dict(cape=(150,84,196),kind='flip')]
TJ1=T0['3a']+0.12                                        # hero 1 starts his jump
TA2=T0['3b']+0.35; TJ2=TA2+1.0                           # hero 2 arrives at the fence, checks twice, hops
TJ3=T0['3c']+0.25                                        # hero 3 starts his flip
T_FB0=T0['5']-0.12                                       # hard cut into the flashback
T_YSTEP=T0['5']+1.1; T_SLIME=T0['6']-0.15; T_FREEZE=T0['6']+0.95; T_BACK=T0['7']+0.05   # young guide: steps over, slime rises, freezes, walks back
T_DIS=(T0['7']+2.2,T0['7']+3.0)                         # dissolve young -> old on the same spot
T_KN=T0['9']+0.7                                         # the knight's jump
T_TURN=(T0['9']+1.7,T0['9']+2.5)                         # the guide turns to the grass
T_STEP=(T0['11']+1.2,T0['12']+1.15)                      # walks to the gate and takes ONE step past the fence line
T_BACK2=T0['13']+0.25                                    # steps back, the gate swings open
T_GATE=(T0['13']+0.05,T0['13']+1.0)
def in_fb(t): return T_FB0<=t<T_DIS[1]
def dis_a(t): return sm(seg01(t,*T_DIS))                  # 0 = flashback .. 1 = now
SEAS=[('leaves',T0['3a']-0.4,T0['3b']-0.1),('snow',T0['3b']-0.1,T0['3c']-0.1),('rain',T0['3c']-0.1,T0['4']+1.6)]

# ======================= characters =======================
HAT=(120,84,46); HAT_D=(92,62,34); TUNIC=((70,126,88),(50,92,64))
def guide_acc(young):
    def acc(Hh,T,Wd):
        Q=box(-0.31,0.31,1.385,1.415,-0.31,0.31,HAT_D,xf=Hh)+box(-0.17,0.17,1.415,1.62,-0.17,0.17,HAT,xf=Hh)+box(-0.175,0.175,1.415,1.46,-0.175,0.175,GOLD,xf=Hh)
        Q+=box(-0.19,-0.06,0.8,0.93,0.145,0.165,GOLD,xf=T)+box(-0.14,-0.11,0.855,0.905,0.165,0.172,(40,30,20),xf=T)+box(-0.14,-0.11,0.815,0.835,0.165,0.172,(40,30,20),xf=T)   # the '?' patch
        return Q
    return acc
def hand_world(base,yaw,lean,hl,hy=0.62):
    piv=np.array([0,hy,0]); return np.array(base,float)+FB.Ry(yaw)@(piv+FB.Rx(lean)@(np.array(hl,float)-piv))
def guide_model(st,cp,young=False,lum=1.15):
    """st: dict(base,yaw,lean,head,tilt,rh,lh,blink,walk,gaze,stick) -> faces (baked light). The stick hangs from the right hand (stick = 'down' | 'up')."""
    kw={k:st[k] for k in ('lean','head','tilt','rh','lh','blink','walk','gaze') if k in st}
    Q=NW.human(st['base'],st['yaw'],kind='boy' if young else 'man',cane=False,coat_col=TUNIC,acc=guide_acc(young),**kw)
    rh=st.get('rh') if st.get('rh') is not None else (0.26,0.68,0.05); hw=hand_world(st['base'],st['yaw'],st.get('lean',0.0),rh)
    Rb=FB.Ry(st['yaw'])
    if st.get('stick','down')=='up': a=hw+np.array([0,-0.3,0]); b=hw+np.array([0,1.0,0])
    else: a=hw+Rb@np.array([0,0.25,-0.05]); b=hw+Rb@np.array([0.02,-0.78,0.3])
    top=b if st.get('stick','down')=='up' else a
    Q+=seg(a,b,0.05,(150,104,60))+box(top[0]-0.045,top[0]+0.045,top[1]-0.02,top[1]+0.04,top[2]-0.045,top[2]+0.045,GOLD,emit=True)
    return NW.lum_lit(Q,cp,lum,0.15)
def hero_model(i,st,cp,lum=0.78):
    Q=NW.hero_knight(HERO[i]['cape'],**{k:v for k,v in st.items() if k not in ('spin',)})
    if st.get('spin'):
        c=np.array(st['base'],float)+np.array([0,0.9,0]); xform(Q,lambda p:tuple(c+FB.Rz(st['spin'])@(np.array(p)-c)))
    return NW.lum_lit(Q,cp,lum,0.2)
def slime_model(p,sc,t,u_eye=1.0):
    x,y,z=p; wob=1+0.07*math.sin(t*6); Q=[]
    G=(86,214,112); GD=(54,160,86)
    Q+=box(x-0.34*sc,x+0.34*sc,y,y+0.18*sc*wob,z-0.34*sc,z+0.34*sc,G,emit=True)+box(x-0.29*sc,x+0.29*sc,y+0.18*sc*wob,y+0.38*sc*wob,z-0.29*sc,z+0.29*sc,G,emit=True)+box(x-0.19*sc,x+0.19*sc,y+0.38*sc*wob,y+0.52*sc*wob,z-0.19*sc,z+0.19*sc,GD,emit=True)
    for sz in (-1,1): Q+=box(x-0.3*sc-0.01,x-0.3*sc+0.0,y+0.26*sc*wob,y+0.4*sc*wob,z+sz*0.12*sc-0.05*sc,z+sz*0.12*sc+0.05*sc,(255,255,255),emit=True)+box(x-0.3*sc-0.02,x-0.3*sc-0.01,y+0.28*sc*wob,y+0.34*sc*wob,z+sz*0.12*sc-0.025*sc,z+sz*0.12*sc+0.025*sc,(20,20,30),emit=True)
    return Q
def sparkle(path_fn,t,n=9,dt=0.035):
    """gold trail behind a jump (emissive confetti along the last positions)"""
    Q=[]
    for k in range(n):
        p=path_fn(t-k*dt)
        if p is None: continue
        s=0.05*(1-k/n)+0.012; Q+=box(p[0]-s,p[0]+s,p[1]+0.9-s,p[1]+0.9+s,p[2]-s,p[2]+s,GOLD,emit=True)
    return Q

# ======================= trajectories =======================
def hero_pos(i,t):
    """(base xyz, yaw, walk, spin, air) of hero i at t; None when out of the world"""
    z=LZ+(0.1 if i==1 else 0.0); yaw=PI/2
    if i==0:
        V=5.0; tj=TJ1; d=0.6
        if t<tj: x=2.0+V*(t-tj); y=0; sp=0
        elif t<tj+d: u=(t-tj)/d; x=2.0+2.4*u; y=1.1*4*u*(1-u); sp=0
        else: x=4.4+V*(t-tj-d); y=0; sp=0
        walk=x*4.5
    elif i==1:
        V=2.6; d=0.5
        if t<TA2: x=2.35+V*(t-TA2); y=0
        elif t<TJ2: x=2.35; y=0
        elif t<TJ2+d: u=(t-TJ2)/d; x=2.35+1.3*u; y=0.55*4*u*(1-u)
        else: x=3.65+V*(t-TJ2-d); y=0
        walk=x*4.0 if (t<TA2 or t>=TJ2+d) else 0.0; sp=0
    else:
        V=4.0; tj=TJ3; d=0.8
        if t<tj: x=1.7+V*(t-tj); y=0; sp=0
        elif t<tj+d: u=(t-tj)/d; x=1.7+3.2*u; y=1.3*4*u*(1-u); sp=-2*PI*sm(u)
        else: x=4.9+V*(t-tj-d); y=0; sp=0
        walk=x*4.5
    if x<-9 or x>15: return None
    hd=0.0
    if i==1 and TA2<=t<TJ2: hd=0.8*math.sin(2*PI*(t-TA2)/0.9)*sm(seg01(t,TA2,TA2+0.2))              # checks left, right
    return dict(base=(x,y,z),yaw=yaw,walk=walk,run=(0.8 if i!=1 else 0.0),sword='hip',lean=0.05,head=hd,spin=sp)
def hero_air(i,t): p=hero_pos(i,t); return None if p is None else (p['base'][0],p['base'][1],p['base'][2])
KN_RUN_T0=T_KN-1.3
def kn_pos(t):
    if t<KN_RUN_T0: return None
    d=0.6; V=4.6; z=LZ; y=0.0; yaw=PI/2; walk=0.0; run=0.8; rh=None; head=0.0
    if t<T_KN: x=2.0+V*(t-T_KN)
    elif t<T_KN+d: u=(t-T_KN)/d; x=2.0+2.4*u; y=1.0*math.sin(PI*u)**1.5
    else:
        t1=T_KN+d; x=4.4+V*min(t-t1,0.35)*(1-0.5*sm(seg01(t,t1+0.1,t1+0.4)))         # lands, runs a few steps, stops
        x=min(x,5.0)
    walk=x*4.5 if (t<T_KN or t>=T_KN+d) else 0.0
    tt=T_KN+d+0.55
    if t>=tt:                                                                        # turns to face the guide, walks back one pace, holds out a hand
        u=sm(seg01(t,tt,tt+0.75)); yaw=lerp(PI/2,-PI/2,u); run=0.0; walk=0.0
        if t>=tt+0.75:
            v=sm(seg01(t,tt+0.75,tt+1.6)); x=5.0-0.65*v; walk=x*5.0 if v<0.98 else 0.0
            h=sm(seg01(t,tt+1.3,tt+2.1)); rh=lerp3((0.27,0.86,0.04),(0.2,1.0,0.7),h)
        else: x=5.0
        head=0.0
    if t<T_KN+d: run=0.8
    return dict(base=(x,y,z),yaw=yaw,walk=walk,run=run,sword='hip',lean=0.03,head=head,rh=rh)

def gstate(t):
    """the old guide"""
    base=list(GS); yaw=Y_WATCH; d=dict(lean=0.04+0.01*math.sin(t*1.7),head=0.0,tilt=0.0,rh=None,lh=None,blink=0.0,walk=0.0,gaze=0.0,stick='down')
    base[1]=0.03*abs(math.sin(2*PI*1.7*t))                                           # bounces on his toes
    ph=(t%2.0)/2.0; tap=math.exp(-((ph-0.15)/0.04)**2)                               # stick taps the post every 2 s
    d['rh']=(0.26,0.68+0.05*tap,0.05+0.07*tap); d['blink']=1.0 if (t*0.5)%1.0<0.05 else 0.0
    # eyes + head follow every hero
    tgt=None; wsum=0.0
    for i in range(3):
        p=hero_pos(i,t)
        if p is None: continue
        hx=p['base'][0]
        if -4.5<hx<5.8: wgt=sm(seg01(hx,-4.5,-1.0))*(1-sm(seg01(hx,2.5,5.8)))
        else: wgt=0
        if wgt>wsum: wsum=wgt; tgt=p['base']
    if tgt is not None and t<T_FB0:
        want=math.atan2(tgt[0]-GS[0],tgt[2]-GS[2]); rel=(want-yaw+PI)%(2*PI)-PI; d['head']=float(np.clip(rel,-1.0,1.0))*wsum; d['gaze']=wsum
    # line 2: stick up, proud
    u2=sm(seg01(t,T0['2']+0.05,T0['2']+0.45))*(1-sm(seg01(t,T0['2']+1.3,T0['2']+1.7)))
    if u2>0: d['rh']=lerp3(d['rh'],(0.3,1.55,0.15),u2); d['stick']='up' if u2>0.5 else 'down'; d['lean']-=0.08*u2
    # line 8: tired, softer
    u8=sm(seg01(t,T0['8']-0.1,T0['8']+0.5))*(1-sm(seg01(t,T0['9']-0.1,T0['9']+0.6)))
    d['tilt']+=0.22*u8; d['lean']+=0.07*u8
    # turns to the knight / the grass
    if t>=T_TURN[0]:
        u=sm(seg01(t,*T_TURN)); yaw=lerp(Y_WATCH,Y_EAST,u); d['head']=0.0; d['gaze']=0.0
    if T0['11']<=t<T_STEP[0]: d['head']=0.0
    # the step: walks to the gate, ONE step past the fence line, stays a beat
    if t>=T_STEP[0]:
        u=sm(seg01(t,T_STEP[0],T_STEP[0]+1.1)); x=lerp(GS[0],2.75,u); z=lerp(GS[2],LZ,u); base=[x,0.03*abs(math.sin(2*PI*1.7*t))*(1-u),z]; d['walk']=u*0+ (t*6.0 if u<0.97 else 0.0); yaw=lerp(Y_EAST,Y_EAST,u)
        h=sm(seg01(t,T_STEP[0]+1.1,T_STEP[0]+1.75)); base[0]=lerp(base[0],3.4,h); base[1]+=0.22*4*h*(1-h) if h<1 else 0.0; d['walk']=0.0 if h>0 else d['walk']
        if t>=T_STEP[0]+1.75: base[0]=3.4
    if t>=T_BACK2:
        u=sm(seg01(t,T_BACK2,T_BACK2+1.9)); tx=lerp(3.4,GS[0],u); tz=lerp(LZ,GS[2],u)
        base=[tx,0.0,tz]; yaw=lerp(Y_EAST,Y_WEST,sm(seg01(t,T_BACK2,T_BACK2+0.5))); d['walk']=t*6.0 if u<0.97 else 0.0
        if u>=0.97: yaw=lerp(Y_WEST,Y_WATCH,sm(seg01(t,T_BACK2+1.85,T_BACK2+2.6))); base[1]=0.03*abs(math.sin(2*PI*1.7*t))
    return dict(base=tuple(base),yaw=yaw,**d)
def ystate(t):
    """the young guide (flashback)"""
    x0=1.0; d=dict(lean=0.03,head=0.0,tilt=0.0,rh=None,lh=None,blink=0.0,walk=0.0,gaze=0.0,stick='down'); yaw=Y_EAST; y=0.0
    tw=T_FB0
    if t<T_FREEZE: x=x0+1.4*max(0.0,t-tw)*(1 if t<T_FREEZE else 0); x=min(x,4.1)
    else: x=min(x0+1.4*(T_FREEZE-tw),4.1)
    if T_YSTEP<=t<T_YSTEP+0.6: y=0.28*4*seg01(t,T_YSTEP,T_YSTEP+0.6)*(1-seg01(t,T_YSTEP,T_YSTEP+0.6))
    x=min(x0+1.4*max(0.0,t-tw),4.1) if t<T_FREEZE else 4.1
    d['walk']=(x*6.0 if (t<T_FREEZE and t>=tw) else 0.0)
    z=LZ
    if t>=T_FREEZE-0.25: u=sm(seg01(t,T_FREEZE-0.25,T_FREEZE+0.25)); d['rh']=lerp3((0.26,0.68,0.05),(0.18,1.25,0.4),u); d['lh']=lerp3((-0.26,0.68,0.05),(-0.18,1.25,0.4),u); d['lean']=-0.1*u; d['stick']='up' if u>0.6 else 'down'
    if t>=T_BACK:
        u=sm(seg01(t,T_BACK,T_BACK+0.5)); yaw=lerp(Y_EAST,Y_WEST,u); d['rh']=None; d['lh']=None; d['lean']=0.03; d['stick']='down'
        v=seg01(t,T_BACK+0.4,T_BACK+2.1); x=lerp(4.1,GS[0],sm(v)); z=lerp(LZ,GS[2],sm(seg01(v,0.55,1.0))); d['walk']=t*6.5 if 0<v<0.98 else 0.0
        if 0.35<v<0.6: y=0.22*4*((v-0.35)/0.25)*(1-(v-0.35)/0.25)
        if v>=0.98: yaw=lerp(Y_WEST,Y_WATCH,sm(seg01(t,T_BACK+2.0,T_BACK+2.5)))
    return dict(base=(x,y,z),yaw=yaw,**d)
def slime_state(t):
    if not (T_SLIME<=t<T_DIS[1]+0.1): return None
    u=sm(seg01(t,T_SLIME,T_SLIME+0.8)); w=sm(seg01(t,T_FREEZE-0.2,T_FREEZE+0.9)); back=sm(seg01(t,T_BACK+0.3,T_BACK+1.0))
    sc=lerp(0.2,1.0,u)*lerp(1.0,2.4,w)*lerp(1.0,0.5,back); x=lerp(7.3,5.3,w)+0.6*back; return dict(p=(x,0.0,LZ),sc=sc)
GATE_OPEN=lambda t: sm(seg01(t,*T_GATE))*1.5

# ======================= set =======================
def ground(season):
    near={'clear':((66,92,110),(60,84,102)),'leaves':((112,92,62),(102,82,56)),'snow':((206,212,226),(190,198,216)),'rain':((48,66,82),(44,60,76))}[season]
    far={'clear':((176,154,70),(164,144,62)),'leaves':((190,150,60),(176,140,56)),'snow':((226,214,176),(214,204,168)),'rain':((142,128,64),(132,120,58))}[season]
    trail={'clear':((120,108,92),(112,100,86)),'leaves':((132,104,70),(124,98,66)),'snow':((226,226,236),(214,216,230)),'rain':((70,72,76),(66,68,72))}[season]
    Q=[]; xs=list(np.arange(-14,3.01,1.5))+list(np.arange(3,17,1.5)); xs=sorted(set(round(v,3) for v in xs)); zs=list(np.arange(-9,3.4,1.2))+[3.4,5,8,12]
    zs=sorted(set(round(v,3) for v in zs))
    for i in range(len(xs)-1):
        for j in range(len(zs)-1):
            cx=(xs[i]+xs[i+1])/2; cz=(zs[j]+zs[j+1])/2; fr=cx>FX
            c=(far if fr else near)[(i+j)%2]
            if 0.05<cz<1.35: c=trail[(i+j)%2]
            c=tuple(int(v*(0.93+0.1*hsh(i*31+j))) for v in c)
            Q.append(quad([(xs[i],0,zs[j]),(xs[i+1],0,zs[j]),(xs[i+1],0,zs[j+1]),(xs[i],0,zs[j+1])],c))
    return Q
GROUND={k:ground(k) for k in ('clear','leaves','snow','rain')}
WOOD=(120,84,50); WOOD_D=(88,60,36)
def fence_static():
    Q=[]
    for z in list(np.arange(-8,-0.2,0.8))+list(np.arange(1.6,8.1,0.8))+[0.0,1.4]:
        Q+=box(FX-0.07,FX+0.07,0,0.62,z-0.07,z+0.07,WOOD)
    Q+=box(FX-0.03,FX+0.03,0.4,0.46,-8,0,WOOD_D)+box(FX-0.03,FX+0.03,0.4,0.46,1.4,8,WOOD_D)+box(FX-0.03,FX+0.03,0.52,0.57,-8,0,WOOD_D)+box(FX-0.03,FX+0.03,0.52,0.57,1.4,8,WOOD_D)
    Q+=box(FX-0.1,FX+0.1,0.62,0.7,-0.1,0.1,GOLD,emit=True)                                   # the hinge post wears the gold cap
    return Q
FENCE=fence_static()
def gate_model(a):
    """leaf hinged on the post at z = 0, closed along z (a = 0), swinging away towards +x when open (a up to 1.5 rad)"""
    GL=(206,156,84); Q=box(FX-0.04,FX+0.04,0.38,0.46,0.0,1.4,GL)+box(FX-0.04,FX+0.04,0.52,0.6,0.0,1.4,GL)+box(FX-0.045,FX+0.045,0.38,0.6,1.32,1.4,GL)+seg((FX,0.42,0.05),(FX,0.57,1.35),0.05,GL)
    hinge=np.array([FX,0.0,0.0]); xform(Q,lambda p:tuple(hinge+FB.Ry(-a)@(np.array(p)-hinge)))
    return Q
def post_sign():
    x,z=2.65,-1.35
    Q=box(x-0.07,x+0.07,0,1.35,z-0.07,z+0.07,WOOD)+box(x-0.4,x+0.1,1.0,1.35,z-0.09,z-0.07,(214,196,150),emit=True)+box(x-0.36,x+0.06,1.2,1.24,z-0.1,z-0.09,(70,56,40),emit=True)+box(x-0.3,x+0.0,1.1,1.14,z-0.1,z-0.09,(70,56,40),emit=True)
    return Q
SIGN=post_sign()
def scenery():
    Q=[]
    for (x,z,s) in ((8,6,1.0),(11,-2,1.2),(14,3,1.0),(6.5,-6,0.9),(-6,8,1.2),(-3,10,1.0),(0.5,11,1.3),(-10,5,1.1),(-9,-7,1.0)):
        c=(52,86,70) if x<FX else (120,128,60)
        Q+=box(x-0.18*s,x+0.18*s,0,1.8*s,z-0.18*s,z+0.18*s,(70,54,40))+box(x-1.0*s,x+1.0*s,1.5*s,2.8*s,z-1.0*s,z+1.0*s,c)+box(x-0.6*s,x+0.6*s,2.7*s,3.6*s,z-0.6*s,z+0.6*s,tuple(int(v*0.9) for v in c))
    for k,(x,z,w,h) in enumerate(((20,4,9,2.6),(22,-5,8,3.4),(18,12,10,2.2))): Q+=box(x-w/2,x+w/2,0,h,z-w/2,z+w/2,(170,152,72) if k!=1 else (150,138,66))
    return Q
SCENERY=scenery()
SET=[FENCE,SIGN,SCENERY]
def season_state(t):
    for n,a,b in SEAS:
        if a<=t<b: return n,min(seg01(t,a,a+0.35),1-seg01(t,b-0.3,b))
    return None,0.0
def ground_key(t):
    n,w=season_state(t); return n if (n and w>0.25) else 'clear'
def particles(t):
    n,w=season_state(t)
    if not n or w<=0: return []
    Q=[]; cnt=int(70*w)
    for i in range(cnt):
        x=-2+8*hsh(i,1); z=-3.5+8*hsh(i,2); y0=3.4*hsh(i,3)
        if n=='leaves': y=(y0-0.7*t)%3.4; x+=0.5*math.sin(t*1.4+i); s=0.07; Q+=box(x-s,x+s,y,y+s*0.4,z-s,z+s,(214,120+int(60*hsh(i,5)),44),emit=True)
        elif n=='snow': y=(y0-0.55*t)%3.4; x+=0.2*math.sin(t*1.1+i*1.7); s=0.04; Q+=box(x-s,x+s,y,y+2*s,z-s,z+s,(240,244,255),emit=True)
        else: y=(y0-8.0*t)%3.4; Q+=seg((x,y,z),(x+0.04,y+0.4,z),0.014,(170,190,224),emit=True)
    return Q

# ======================= camera (Format 3.0: always moving, subject in the middle third, group framing) =======================
FOV=46
LIFT_A=look.Path([(0,0.62),(1.2,0.5),(2.9,0.12),(T0['2']+0.5,0.05),(T_FB0,0.0)])    # frame 0: the guide sits low so the title card does not cover his face
# every track is a Path (continuous speed); keys in build time
YAW_A=look.Path([(0,-0.62),(T0['2'],-0.50),(T0['4'],-0.30),(T_FB0-0.01,-0.2)])
PIT_A=look.Path([(0,0.05),(T0['2'],0.10),(T0['4']-0.2,0.2),(T0['4']+1.2,0.55),(T_FB0-0.01,0.5)])
DMIN_A=look.Path([(0,2.35),(1.0,2.0),(T0['2'],2.6),(T0['3c'],3.0),(T0['4']-0.2,3.6),(T0['4']+1.2,8.5),(T_FB0-0.01,8.0)])
FOV_A=look.Path([(0,44),(T0['4'],46),(T0['4']+1.2,52),(T_FB0-0.01,52)])
YAW_B=look.Path([(T_FB0,-1.45),(T0['6']+0.5,-1.3),(T_DIS[0],-1.05),(T0['8']+1.0,-0.85),(T0['9'],-0.62),(T0['10']+0.5,-0.40),(T0['11'],-0.3),(T0['12'],-0.16),(T0['13'],-0.25),(T0['13']+2.0,-0.45),(DUR,-0.62)])
PIT_B=look.Path([(T_FB0,0.14),(T0['6']+0.5,0.10),(T_DIS[0],0.10),(T0['8'],0.06),(T0['9'],0.12),(T0['10'],0.10),(T0['11'],0.04),(T0['12'],0.08),(T0['13'],0.12),(T0['13']+2.0,0.30),(DUR-0.6,0.10),(DUR,0.05)])
DMIN_B=look.Path([(T_FB0,3.2),(T0['6'],2.5),(T0['6']+1.2,2.0),(T0['7']+0.5,3.0),(T_DIS[0],3.4),(T0['8']+0.2,2.7),(T0['8']+1.7,2.0),(T0['9'],2.6),(T0['10'],2.9),(T0['11'],1.5),(T0['11']+1.6,1.3),(T0['12'],3.4),(T0['13'],4.0),(T0['13']+2.0,6.0),(DUR-0.6,3.0),(DUR,2.35)])
FOV_B=look.Path([(T_FB0,44),(T0['10'],46),(T0['11'],40),(T0['12'],46),(T0['13']+2.0,50),(DUR-0.6,46),(DUR,44)])
def cam_params(t):
    if t<T_FB0: return YAW_A(t),PIT_A(t),DMIN_A(t),FOV_A(t)
    return YAW_B(t),PIT_B(t),DMIN_B(t),FOV_B(t)
def pts_of(base,top=1.85,lift=0.0):
    return [(base[0],base[1],base[2]),(base[0],base[1]+top,base[2])]
def subject_pts(t,fb):
    st=ystate(t) if fb else gstate(t); b=st['base']; P=[(b[0],b[1],b[2]),(b[0],b[1]+1.0,b[2]),(b[0],b[1]+1.9,b[2])]
    return P
def helper_pts(t,fb,anchor):
    O=[]
    if fb:
        s=slime_state(t)
        if s: w=sm(seg01(t,T_SLIME+0.2,T_SLIME+1.0)); O+=look.blend_pts([(s['p'][0],0,s['p'][2]),(s['p'][0],0.9*s['sc']+0.3,s['p'][2])],anchor,w*(1-sm(seg01(t,T_BACK+0.3,T_BACK+1.2))))
        return O
    for i in range(3):
        p=hero_pos(i,t)
        if p is None: continue
        b=p['base']; x=b[0]; w=sm(seg01(x,-2.4,0.0))*(1-sm(seg01(x,5.4,9.5)))
        if w>0.001: O+=look.blend_pts([(b[0],b[1],b[2]),(b[0],b[1]+1.9,b[2])],anchor,w)
    k=kn_pos(t)
    if k is not None:
        b=k['base']; x=b[0]; w=sm(seg01(t,T_KN-1.0,T_KN-0.1))*(1-0.0)
        w=w*(1.0 if t<T0['13']+1.2 else 1-sm(seg01(t,T0['13']+1.2,T0['13']+2.6)))
        if t>=T0['11']+0.4 and t<T0['12']-0.3: w*=0.0 if False else 1.0
        O+=look.blend_pts([(b[0],b[1],b[2]),(b[0],b[1]+1.9,b[2])],anchor,w)
    return O
def cam_raw(t,fb=None):
    fb=in_fb(t) if fb is None else fb
    yaw,pit,dmin,fov=cam_params(t); sub=subject_pts(t,fb); anchor=sub[1]
    others=helper_pts(t,fb,anchor)
    lift=LIFT_A(t) if t<T_FB0 else (LIFT_A(0.0)*seg01(t,DUR-1.4,DUR) if t>DUR-1.4 else 0.0)
    pos,tgt=look.follow_group(sub,others,look.orbit_dir(yaw,pit),fov,W,H,d_min=dmin,d_max=6.5,margin=0.12,third=0.15,lift=lift)
    return dict(cam=pos,tgt=tgt,fov=fov)

CUTS=[0.0,T_FB0]
def cam_shot(t,fb=None): return look.smooth_shot(cam_raw,t,CUTS)

# ======================= render =======================
RND=Renderer(W,H,fog=(150,170,196)); RNF=Renderer(W,H,fog=(168,146,124))
def lights(fb):
    return [((-3,7,-5),(255,244,214),1.3),((8,5,-3),(255,226,170),0.45)] if not fb else [((-3,7,-5),(255,226,184),1.3),((8,5,-3),(255,210,160),0.5)]
def render_world(t,fb,sh):
    cam=Camera.look(sh['cam'],sh['tgt']); cp=sh['cam']; gk='clear' if fb else ground_key(t)
    layers=[GROUND[gk]]+SET+[gate_model(0.0 if fb else GATE_OPEN(t))]
    if fb:
        layers.append(guide_model(ystate(t),cp,young=True,lum=1.2))
        s=slime_state(t)
        if s: layers.append(slime_model(s['p'],s['sc'],t))
    else:
        layers.append(guide_model(gstate(t),cp,lum=1.2))
        for i in range(3):
            p=hero_pos(i,t)
            if p is not None: layers.append(hero_model(i,p,cp))
        k=kn_pos(t)
        if k is not None: layers.append(NW.lum_lit(FB.knight(**k),cp,0.8,0.2))
        for i in range(3): layers.append(sparkle(lambda tt,i=i:hero_air(i,tt) if (hero_air(i,tt) and hero_air(i,tt)[1]>0.05) else None,t))
        layers.append(particles(t))
    R=RNF if fb else RND
    img,vi,zb=zrender(R,cam,layers,lights(fb),fov=sh['fov'],fog_start=9,fog_end=40,ambient=0.55,return_z=True)
    a=np.asarray(img).astype(np.float32); a=look.outline(a,zb)
    if fb:
        l=a.mean(axis=2,keepdims=True); a=(l*0.55+a*0.45)*np.array([1.06,0.97,0.86])*0.92
    return a,vi
def frame_low(t):
    fb=in_fb(t); sh=cam_shot(t,fb)
    a,vi=render_world(t,fb,sh)
    if T_DIS[0]<=t<T_DIS[1]:                                                           # dissolve: the same camera, flashback -> now
        a2,_=render_world(t,False,dict(sh)); k=dis_a(t); a=a*(1-k)+a2*k
    a=np.clip((a-118)*1.08+118,0,255)
    img=post.ps1(Image.fromarray(a.astype(np.uint8)),levels=6); return img,vi,sh
def counter_value(t):
    n=10000+sum(1 for tl in (TJ1+0.6,TJ2+0.5,TJ3+0.8) if t>=tl); return n
def hud_text(t):
    if t>=T_STEP[0]+1.7: return 'STEPS OUTSIDE',1
    return 'HEROES TAUGHT',f'{counter_value(t):,}'
KEYCAP=[(T0['2']+0.05,T0['2']+1.5),(T0['8']+0.05,T0['8']+1.7)]
def overlays(arr,t,vi,sh):
    im=Image.fromarray(np.clip(arr,0,255).astype(np.uint8)); d=ImageDraw.Draw(im)
    lab,val=hud_text(t)
    pop=0.0
    for tl in (TJ1+0.6,TJ2+0.5,TJ3+0.8,T_STEP[0]+1.7):
        if 0<=t-tl<0.25: pop=1-(t-tl)/0.25
    look.hud_counter(d,lab,val,GOLD if pop<=0 else (255,255,255),y=70)
    for a,b in KEYCAP:                                                                  # the tutorial prompt over his head: a SPACE key cap
        if a<=t<b:
            st=gstate(t); P=(st['base'][0],st['base'][1]+2.1,st['base'][2]); pr=RND.project(P,vi)
            if pr:
                sx,sy,z=pr; sc=8; txt='SPACE'; wd=len(txt)*6*sc; x0=int(sx*S-wd/2-14); y0=int(sy*S-4*sc-int(6*math.sin(t*9)))
                d.rectangle([x0-6,y0-8,x0+wd+16,y0+7*sc+8],fill=(230,226,214),outline=(0,0,0),width=4); d.rectangle([x0-6,y0+7*sc+2,x0+wd+16,y0+7*sc+14],fill=(150,146,136))
                look.draw_cells(d,look.text_cells(txt,x0+4,y0,sc,(40,34,30)),0)
    return np.asarray(im).astype(np.float32)
SUBS=look.Subtitles(SCR,LINES,W,H,S,COL,hil={'TUTORIAL','SLIME,','FROZE.','SPACE','STEP.','OPEN.','FORTY','EVER','KNIGHT'},card_y=0.2,card_sc=8.0,card_n=18)
def finish(t):
    img,vi,sh=frame_low(t); end=seg01(t,DUR-0.5,DUR)
    if end>0: img=Image.fromarray((np.asarray(img).astype(np.float32)*(1-0.12*end)).astype(np.uint8))
    return img,vi,sh
def frame_final(t):
    img,vi,sh=finish(t); arr=post.upscale(img,S); arr=overlays(arr,t,vi,sh); return SUBS.apply(arr,t)
def frame(t):
    return Image.fromarray(np.clip(frame_final(t),0,255).astype(np.uint8)).resize((W,H),Image.BOX)

TEST=os.environ.get('TEST')
if TEST and __name__=='__main__':
    ts=[float(x) for x in TEST.split(',')]; ims=[Image.fromarray(np.clip(frame_final(x),0,255).astype(np.uint8)).resize((270,480),Image.LANCZOS) for x in ts]
    per=int(os.environ.get('PER','8')); rows=(len(ims)+per-1)//per; shp=Image.new('RGB',(min(per,len(ims))*272,rows*482))
    for i,im in enumerate(ims): shp.paste(im,((i%per)*272,(i//per)*482))
    shp.save(os.environ.get('TEST_OUT','test_tg.png')); sys.exit()

# ======================= QA manifest =======================
def _g(t): return None if in_fb(t) else gstate(t)
def _kn(t): return kn_pos(t)
QA=dict(fps=FPS,dur=DUR,W=W,frame=frame,
    chars={'guide':(_g,lambda **k:NW.human(kind='man',cane=False,**{a:b for a,b in k.items() if a not in ('stick',)}),'none','none'),'knight':(_kn,FB.knight,'sword','hip')},
    geom=lambda t,name,st,V:[],camera=lambda t:cam_shot(t)['cam'],min_cam_dist=0.35,camera_ok=lambda p:-14<p[0]<16 and -10<p[2]<14 and p[1]>0.1,
    allow_jump=[(w,f/FPS) for w in ('guide','knight') for c in (0.0,T_FB0,T_DIS[0],T_DIS[1]) for f in range(int(c*FPS)-3,int(c*FPS)+6)],weapon_events=[],
    scenes=[dict(id='now1',t0=0.0,t1=T_FB0,action='frame 0: guide close and bouncing; three heroes jump the fence; the crane up on the empty field'),
            dict(id='flash',t0=T_FB0,t1=T_DIS[0],action='flashback: the young guide steps over, the slime rises, he freezes and walks back'),
            dict(id='now2',t0=T_DIS[0],t1=DUR,action='dissolve to the old guide; the knight; one step; the gate swings open')],
    texts=lambda:[('hud','HEROES TAUGHT',1),('hud','STEPS OUTSIDE',1),('hud','SPACE',1)])

# ======================= AUDIO =======================
LVL={'3c':2.0,'8':-4.0,'10':-3.0,'2':0.0}              # per-line level trim (dB) on top of the RMS levelling
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=53); sr=s.sr; n=s.n; t=s.t; BED=np.zeros(n); FXb=np.zeros(n); PAD=np.zeros(n)
    def put(buf,x,t0,v=1.0):
        i=int(t0*sr)
        if i>=n or i<0: return
        j=min(n,i+len(x)); buf[i:j]+=(x*v)[:j-i]
    def nb(t0,d,lo,hi,v,seed,shape=2): put(FXb,s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v)
    def tone(t0,m,d,v,wave='sin',duty=0.5,dec=3.0,att=0.005,glide=0.0):
        f=440*2**((m-69)/12); tt=s.T(d); fr=f*(1+glide*tt/d); ph=np.cumsum(fr)/sr%1
        x=np.where(ph<duty,1.0,-1.0) if wave=='sq' else (4*np.abs(ph-0.5)-1 if wave=='tri' else np.sin(2*np.pi*ph))
        put(FXb,x*np.minimum(1,tt/att)*np.exp(-tt*dec),t0,v)
    def step(t0,v=0.03,seed=0):
        tt=s.T(0.12); put(FXb,s.filt_short(s.noise(0.12,seed),lo=200,hi=1800)*np.exp(-tt*38)+np.sin(2*np.pi*90*tt)*np.exp(-tt*30)*0.25,t0,v)
    def boing(t0,v=0.04,m=64,d=0.28): tone(t0,m,d,v,'sin',dec=9,glide=1.4)
    def tap(t0,v=0.03): tt=s.T(0.06); put(FXb,np.sin(2*np.pi*520*tt)*np.exp(-tt*55)+s.filt_short(s.noise(0.06,int(t0*37)),lo=800,hi=4000)*np.exp(-tt*60)*0.4,t0,v)
    def creak(t0,d=0.9,v=0.05,seed=0,f0=210):
        tt=s.T(d); f=f0*(1+0.25*np.sin(2*np.pi*(2.1+0.6*hsh(seed))*tt))+40*tt/d; ph=np.cumsum(f)/sr; x=np.sin(2*np.pi*ph)*0.5+0.3*np.sin(4*np.pi*ph)+0.25*s.filt_short(s.noise(d,seed),lo=300,hi=1400)
        put(FXb,x*np.sin(np.pi*tt/d)**1.5,t0,v)
    def squelch(t0,d=0.45,v=0.05): tt=s.T(d); f=300*np.exp(-3*tt/d)+80; ph=np.cumsum(f)/sr; put(FXb,(np.sin(2*np.pi*ph)*0.6+0.4*s.filt_short(s.noise(d,int(t0*13)),lo=200,hi=900))*np.exp(-tt*6),t0,v)
    # ---- bed: open-field wind (slow swell, low-passed) + a few distant birds (smooth chirps); the flashback is quiet with a low drone (never a per-sample gate)
    warm=np.where((t>=T_FB0)&(t<T_DIS[1]),1.0,0.0); sm_f=np.convolve(warm,np.ones(2400)/2400,'same')
    sw=0.6+0.4*np.sin(2*np.pi*t/9.0+0.7)+0.15*np.sin(2*np.pi*t/3.7)
    BED+=s.filt(s.rng.normal(0,1,n),lo=80,hi=800)*0.06*np.clip(sw,0.2,None)*(1-0.5*sm_f)
    BED+=s.filt(s.rng.normal(0,1,n),lo=1500,hi=5000)*0.006*np.clip(0.4+0.6*np.sin(2*np.pi*t/6.1),0,None)*(1-sm_f)
    BED+=(np.sin(2*np.pi*55*t)+0.5*np.sin(2*np.pi*82.4*t+0.4))*0.016*sm_f
    for k in range(7):
        tb=1.4+k*6.1+hsh(k,3)*1.5
        if tb<T_FB0-0.5 or tb>T_DIS[1]+0.5:
            for j in range(3): tt=s.T(0.09); put(BED,np.sin(2*np.pi*(2600+500*j+300*hsh(k,j))*tt*(1+0.3*tt/0.09))*np.sin(np.pi*tt/0.09)**2,tb+j*0.14,0.008)
    # ---- 0.0 s: the stick taps the post; then every 2 s; the key-cap blips on his lines
    for k in range(int(DUR/2.0)):
        tk=0.3+k*2.0
        if not (T_FB0<=tk<T_DIS[0]): tap(tk,0.03)
    for a,b in KEYCAP: tone(a,84,0.1,0.02,'sq',duty=0.4,dec=25); tone(a+0.12,88,0.14,0.02,'sq',duty=0.4,dec=20)
    # ---- heroes: footsteps, boing per jump, counter tick, a gold chime on the landing
    def run_steps(x_fn,ta,tb,seed):
        tt_=ta
        while tt_<tb: step(tt_,0.026,seed+int(tt_*10)); tt_+=0.24
    run_steps(None,TJ1-1.1,TJ1,100); run_steps(None,TJ1+0.6,TJ1+1.3,110)
    run_steps(None,TA2-1.6,TA2,120); run_steps(None,TJ2+0.5,TJ2+1.4,130)
    run_steps(None,TJ3-1.0,TJ3,140); run_steps(None,TJ3+0.8,TJ3+1.3,150)
    for tj,m in ((TJ1,64),(TJ2,70),(TJ3,60)): boing(tj,0.045,m,0.3)
    for tl in (TJ1+0.6,TJ2+0.5,TJ3+0.8): tone(tl,88,0.4,0.03,'sin',dec=6); tone(tl+0.08,95,0.5,0.02,'sin',dec=6); nb(tl-0.1,0.12,200,1500,0.02,int(tl*7),1)
    nb(TA2+0.1,0.3,300,1500,0.02,161,1); nb(TA2+0.55,0.3,300,1500,0.02,162,1)               # hero 2 looks left / right (cloth)
    # ---- seasons
    for nme,a,b in SEAS:
        m=np.clip(np.minimum(t-a,b-t)/0.3,0,1)*((t>=a)&(t<b))
        if nme=='leaves': BED+=s.filt(s.rng.normal(0,1,n),lo=1500,hi=6000)*0.010*m*np.clip(0.5+0.5*np.sin(2*np.pi*t*0.9),0,None)
        elif nme=='snow': BED+=s.filt(s.rng.normal(0,1,n),lo=300,hi=1500)*0.012*m
        else: BED+=s.filt(s.rng.normal(0,1,n),lo=2500,hi=9000)*0.018*m
    # ---- the crane up: a long soft swell; the field is empty, a lone wind chime
    nb(T0['4']+0.2,1.6,150,900,0.04,171,1); tone(T0['4']+0.9,93,1.4,0.012,'sin',dec=2.5)
    # ---- flashback: warm whoosh in, steps (soft, slower), fence creak, the slime rises (squelch), a held breath, steps back
    nb(T_FB0-0.04,0.5,200,1800,0.04,181,1)
    k=0
    while T_FB0+0.15+k*0.38<T_FREEZE-0.1: step(T_FB0+0.15+k*0.38,0.022,190+k); k+=1
    creak(T_YSTEP-0.1,0.6,0.035,seed=3,f0=180); tone(T_YSTEP+0.5,50,0.2,0.04,'sin',dec=12)
    squelch(T_SLIME,0.5,0.05); squelch(T_FREEZE-0.1,0.5,0.07); squelch(T_FREEZE+0.55,0.35,0.05)
    nb(T_FREEZE+0.2,0.8,200,900,0.012,191,1)                                                    # the held breath
    k=0
    while T_BACK+0.5+k*0.4<T_DIS[0]+0.4: step(T_BACK+0.5+k*0.4,0.02,200+k); k+=1
    # ---- now again: a soft low chord returns; the guide's quiet stick tap (line 8)
    for k_,m in enumerate((50,57)): tone(T_DIS[0]+0.2,m,2.0,0.02,'sin',dec=1.8)
    # ---- the knight: running steps, jump boing, landing, armour, turn, step back, gauntlet
    run_steps(None,KN_RUN_T0,T_KN,210); boing(T_KN,0.04,58,0.3); step(T_KN+0.62,0.05,220); nb(T_KN+0.6,0.3,300,2000,0.04,221,1)
    run_steps(None,T_KN+0.7,T_KN+1.1,230); nb(T_KN+1.4,0.6,300,1600,0.04,231,1)
    nb(T_TURN[0],0.5,300,1600,0.03,241,1)                                                      # the guide turns
    k=0
    while T_KN+2.0+k*0.4<T0['10']+0.1: step(T_KN+2.0+k*0.4,0.03,250+k); k+=1
    nb(T0['10']-0.3,0.4,300,1600,0.04,271,1)                                                    # gauntlet held out
    # ---- the step: steps, a held breath, one soft landing + a gold note; line 13: gate creak, steps back, gate stops
    k=0
    while T_STEP[0]+0.1+k*0.4<T_STEP[0]+1.1: step(T_STEP[0]+0.1+k*0.4,0.03,300+k); k+=1
    nb(T_STEP[0]+1.1,0.35,300,1400,0.012,311,1); step(T_STEP[0]+1.72,0.05,315); tone(T_STEP[0]+1.75,76,1.2,0.035,'sin',dec=2.2); tone(T_STEP[0]+1.9,83,1.4,0.025,'sin',dec=2.2)
    creak(T_GATE[0],1.0,0.06,seed=17,f0=230); tone(T_GATE[1],45,0.25,0.05,'sin',dec=12)
    k=0
    while T_BACK2+0.1+k*0.4<T_BACK2+2.0: step(T_BACK2+0.1+k*0.4,0.028,330+k); k+=1
    # ---- a low two-note pad under the last line (D2 + A2)
    a0=T0['13']-0.2; m=np.clip(np.minimum(t-a0,DUR-t)/1.6,0,1)*(t>=a0)
    PAD+=(np.sin(2*np.pi*73.4*t)+0.55*np.sin(2*np.pi*110.0*t+0.4))*0.05*m
    # ---- voice: RMS-levelled per line (characters are raw Kokoro, narrator is Enes timbre), per-line trim, ducking
    NB=np.zeros(n); wins=[]
    for k_,t0 in LINES:
        a,ar=_sf.read(os.path.join(TTS_DIR,'tg',f'{k_}.wav')); a=a if a.ndim==1 else a.mean(1)
        a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a); act=np.abs(a)>0.02*np.abs(a).max(); a=a*(0.12/np.sqrt((a[act]**2).mean()))*10**(LVL.get(k_,0.0)/20)
        put(NB,a,t0); wins.append((t0,t0+len(a)/sr))
    g=duck_envelope(n,sr,wins,-6.0,0.05,0.25); bed=BED*g+PAD; fx=FXb*(0.55+0.45*g)
    L=bed+fx; R_=np.roll(bed,700)+np.roll(fx,200); pk=max(np.abs(L).max(),np.abs(R_).max()); gv=pk*1.6/np.abs(NB).max()
    s.L=L+NB*gv; s.R=R_+NB*gv; s.reverb(0.12,length=1.4,decay=3.0)
    end=np.clip((DUR-t)/0.6,0,1); s.L*=end; s.R*=end
    return s.save(path,peak=0.9)
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'tutorial_guy.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','17','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'tg_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=0,scan_dark=1.0,vignette=0.22,grain=0.9,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(frame_final(f/FPS),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
