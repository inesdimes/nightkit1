"""WHY DON'T ENEMIES EVER ATTACK ALL AT ONCE? (Insert Disc 2, 02:00 slot) ~31 s PS1, 9:16, nightkit. NEW STORY (21 Nov, Enes: new story, same question).
The goblins' rule: ONE AT A TIME was carved after the first hero came - nine goblins rushed a level-1 kid and he never came back; they stood in
the dark; the oldest carved the rule. Since then every goblin in the line steps up knowing he will lose, so the next hero can reach level two.
Reuses: locked knight (examples/final_boss.py), locked goblin + hallway (examples/loot_restocker.py; colour / scale variants + a grey elder with a hat only).
NEW: rule board on the wall (2D text carved letter by letter), flashback (rookie hero, nine goblins rushing, dogpile, mourning ring, elder), LEVEL 2 pop.
Voice: python tools/tts/eq2.py src ; <chatterbox python> tools/tts/vc.py eq2 ; python tools/tts/eq2.py build vc  -> $TTS_DIR/eq2/
Run: TEST=1,5,9 python examples/enemies_queue.py -> test.png | PART=a:b | PART=audio | tools/render_parts.py --prefix eq --audio enemies_queue.wav"""
import os, sys, math, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','tts'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, quad
from nightkit import motion, post, font
from nightkit.zraster import zrender
from nightkit.audio import Sound, duck_envelope, soft_fire
import final_boss as FB
import loot_restocker as LR

OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6; F=1.0/FPS
PI=math.pi; sm=motion.smooth
def seg01(t,a,b): return max(0.0,min(1.0,(t-a)/(b-a)))
def lerp(a,b,u): return a+(b-a)*u
def lerp3(a,b,u): return tuple(a[i]+(b[i]-a[i])*u for i in range(3))
def hsh(i,s=0): v=math.sin(i*127.1+s*311.7)*43758.5453; return v-math.floor(v)
box=FB.box; xform=FB.xform
WHT=(242,238,226); YEL=(255,210,60); RED=(240,50,40); GRN=(80,220,90); GRAY=(150,150,160); GOLD=(236,190,60); BLU=(110,170,255)

# ======================= voice timings (tools/tts/eq2.py) =======================
SCR=json.load(open(os.path.join(TTS_DIR,'eq2','script.json')))
GAP=0.3; EXTRA={'1':0.2,'3':0.1,'4':0.55,'5':0.3,'6':0.5,'7':0.45,'8':0.25,'9':0.2,'10':0.35}
def _lines():
    t=0.12; out=[]
    for k in [str(i) for i in range(1,12)]: out.append((k,round(t,3))); t+=SCR['dur'][k]+GAP+EXTRA.get(k,0.0)
    return out,t-GAP
LINES,_vend=_lines(); T0=dict(LINES)
DUR=round(T0['11']+SCR['dur']['11']+0.7,2); N=int(round(DUR*FPS))
def ws(k,i): return T0[k]+SCR['sent'][k][i][0]
def we(k,i): return T0[k]+SCR['sent'][k][i][1]
LEAD=2*F

# ======================= story events =======================
T_FB=(T0['3']-0.1,T0['8']-0.15)                                       # the flashback window (lines 3-7)
HITS={44:ws('1',0)+1.55-LEAD, 45:ws('8',0)+0.95-LEAD, 46:ws('8',1)+0.55-LEAD, 47:ws('10',1)+0.7-LEAD}
STEP={45:HITS[44]+0.75, 46:HITS[45]+0.6, 47:T0['10']-0.05}            # the next number steps up to the front
T_NOD=ws('11',1)+0.2                                                  # the knight nods
T_RUSH=ws('4',0)+0.55; T_FLASH=T_RUSH+0.95; T_GONE=T_RUSH+1.1          # nine goblins rush the rookie; he is gone
T_DARK=(ws('6',0)+0.3,ws('6',0)+1.0); T_LIGHT=(T0['7']+0.05,T0['7']+0.6)
T_ELD=(T0['7']+0.1,T0['7']+1.1); T_CARVE0=T0['7']+1.0; T_TYPE=(ws('7',1)-0.1,we('7',1)+0.1)
T_LEVEL=HITS[47]+0.3; T_WAVE=T0['11']-0.1
FS=(0.6,0.0,7.25); KN_P=(0.0,0.0,6.55); KN_YAW=math.atan2(FS[0]-KN_P[0],FS[2]-KN_P[2]); QX=0.6; FRONT_YAW=PI+KN_YAW
def slot_z(k): return FS[2] if k<=0 else FS[2]+0.2+1.1*k
NUMS=list(range(44,60))
CUTS=[0.0,T0['2']-0.06,T0['3']-0.1,T0['5']-0.06,T0['7']-0.06,T0['8']-0.15,T0['9']-0.08,T0['10']-0.1,T0['11']-0.1,DUR]
def infb(t): return T_FB[0]<=t<T_FB[1]

# ======================= LOCKED ASSET: goblin variants (colour / scale only) + NEW props =======================
VAR=[{},{LR.SKIN:(120,182,84),LR.SKIN_D:(90,140,62)},{LR.SKIN:(88,150,96),LR.SKIN_D:(64,116,72),LR.TUNIC:(96,84,120),LR.TUNIC_D:(70,60,92)},
     {LR.SKIN:(136,170,70),LR.SKIN_D:(104,132,52),LR.TUNIC:(128,64,48),LR.TUNIC_D:(96,46,34)}]
G47={LR.TUNIC:(70,92,150),LR.TUNIC_D:(50,68,112)}
ELDER={LR.SKIN:(150,160,132),LR.SKIN_D:(112,122,98),LR.TUNIC:(70,64,60),LR.TUNIC_D:(50,46,44)}
def gscale(n): return 0.92 if n==60 else (0.86 if n==47 else (1.0+0.06*math.sin(n*1.7)))
CLUB=(110,70,36); CLUB_D=(82,52,28)
def gpt(st,p):
    b=np.array(st['base'],float); piv=np.array([0,0.34,0]); q=piv+FB.Rx(st.get('lean',0.0))@(np.array(p,float)-piv)
    w=b+np.array([0,st.get('hop',0.0),0])+FB.Ry(st['yaw'])@q; s=gscale(st['n']); return b+(w-b)*s
def fall_xf(Q,base,yaw,a):
    if a<=0: return Q
    Rb=FB.Ry(yaw); Rf=Rb@FB.Rx(-1.45*a)@Rb.T; piv=np.array(base,float)+Rb@np.array([0,0,-0.12])
    Q=xform(Q,lambda p:tuple(piv+Rf@(np.array(p,float)-piv)))
    ymin=min(v[1] for q in Q for v in q['p'])
    if ymin<0.005: Q=xform(Q,lambda p:(p[0],p[1]-ymin+0.005,p[2]))
    return Q
def club(st):
    if st.get('rh') is None or not st.get('has_club',True): return []
    hp=gpt(st,st['rh']); up=st.get('club_up',0.0)
    d=np.array([0.0,lerp(-0.35,0.75,up),lerp(0.75,-0.25,up)]); d=FB.Ry(st['yaw'])@d; d/=np.linalg.norm(d)
    return FB.seg(hp-d*0.05,hp+d*0.22,0.05,CLUB_D)+FB.seg(hp+d*0.2,hp+d*0.5,0.1,CLUB)
def gmodel(n,base,yaw,walk=0.0,lean=0.0,rh=None,lh=None,eyes=1.0,smile=0.0,head=0.0,hop=0.0,fall=0.0,club_up=0.0,has_club=True,hat=False,**_):
    st=dict(n=n,base=base,yaw=yaw,lean=lean,hop=hop,rh=rh,lh=lh,club_up=club_up,has_club=has_club)
    Q=LR.goblin(base,yaw,walk=walk,lean=lean,rh=rh,lh=lh,eyes=eyes,smile=smile,hat=hat,head=head,hop=hop)
    col=ELDER if n==60 else (G47 if n==47 else VAR[n%4])
    for q in Q:
        c=col.get(tuple(q['col']))
        if c: q['col']=c
    s=gscale(n); b=np.array(base,float)
    if s!=1.0: Q=xform(Q,lambda p:tuple(b+(np.array(p,float)-b)*s))
    Q+=club(st)
    return fall_xf(Q,base,yaw,fall)
def rookie_model(base,yaw,walk=0.0,lean=0.0,head=0.0,rh=None):
    """the first hero: the locked knight, small, with a red cape (a level-1 kid)"""
    Q=FB.knight(base=base,yaw=yaw,walk=walk,run=0.0,sword='hand',lean=lean,head=head,rh=rh if rh else (0.26,1.0,0.42),lh=None,swing=1.0,eyes=0.0)
    for q in Q:
        c=tuple(q['col'])
        if c==FB.CAPE: q['col']=(196,60,52)
        elif c==FB.CAPE_D: q['col']=(140,40,36)
        elif c==FB.PLUME: q['col']=(220,90,60)
    b=np.array(base,float); return xform(Q,lambda p:tuple(b+(np.array(p,float)-b)*0.72))

# ======================= present: the queue =======================
def front(t):
    f=44
    for n in (45,46,47):
        if t>=STEP[n]: f=n
    return f
def gstate(n,t):
    """None when the goblin is gone (defeated + puffed)"""
    if n in HITS and t>=HITS[n]+0.75: return None
    f=front(t); k=n-f
    z=slot_z(k); wk=0.0; yaw=FRONT_YAW if k<=0 else PI
    for m in (45,46,47):
        if STEP[m]<=t<STEP[m]+0.6 and n>=m:
            u=sm(seg01(t,STEP[m],STEP[m]+0.6)); z=lerp(slot_z(n-m+1),slot_z(n-m),u); wk=t*9.0
            if n==m: yaw=lerp(PI,FRONT_YAW,u)
    st=dict(n=n,base=(QX,0.0,z),yaw=yaw,walk=wk,lean=0.0,rh=(0.2,0.32,0.06),lh=None,eyes=1.0,smile=-0.2,head=0.0,hop=0.0,fall=0.0,club_up=0.0)
    if k>0: st['head']=0.12*math.sin(t*0.9+n); st['lean']=0.02*math.sin(t*1.3+n*2)
    if k==0 and n!=47:                                                          # at the front: fighting stance, club up, bouncing
        st.update(rh=(0.22,0.62,0.18),club_up=1.0,lean=0.15,smile=-0.6); st['hop']=0.05*abs(math.sin(t*7))
    if n==47 and t>=STEP[47]:                                                   # he steps up anyway: club up, a small brave smile
        u=sm(seg01(t,STEP[47]+0.5,STEP[47]+0.9)); st.update(rh=lerp3((0.2,0.32,0.06),(0.22,0.66,0.16),u),club_up=u,smile=lerp(-0.2,0.4,u),lean=0.1*u)
    if n==47 and T0['9']<=t<STEP[47]:                                           # "knows he will lose": a gulp, wide eyes
        st.update(eyes=1.0,smile=-0.8,head=0.18*math.sin(t*2.0),lean=0.03+0.05*max(0.0,math.sin(t*3.0)))
    if n in HITS and t>=HITS[n]:                                                # knocked back and falls
        a=seg01(t,HITS[n],HITS[n]+0.35); st.update(fall=a*a,hop=0.0,eyes=0.4,club_up=0.0)
        if n==47: st.update(smile=1.0,eyes=1.0)
    if t>=T_WAVE and k>0 and n!=47:                                             # the last line: the whole queue waves
        st['rh']=(0.24,0.98+0.1*math.sin(t*7+n*1.7),0.1); st.update(smile=0.8,eyes=1.0,head=0.1*math.sin(t*2+n))
    return st
def puffs(t):
    Q=[]
    for n,h in HITS.items():
        a=t-(h+0.6)
        if 0<=a<0.4:
            z=FS[2]+1.1; r=0.15+0.9*a; c=tuple(int(lerp(255,120,a/0.4)) for _ in range(3))
            for k in range(8):
                ang=k*PI/4; p=np.array([QX+r*math.cos(ang),0.25+0.6*a+0.15*math.sin(k*1.3),z+r*math.sin(ang)*0.6]); s=0.12*(1-a/0.4)+0.03
                Q+=box(p[0]-s,p[0]+s,p[1]-s,p[1]+s,p[2]-s,p[2]+s,c,emit=True)
    return Q
def kstate(t):
    d=dict(base=KN_P,yaw=KN_YAW,walk=0.0,lean=0.05+0.02*math.sin(t*2.2),head=0.0,rh=(0.26,1.0,0.42),sword='hand',swing=1.0,eyes=0.0)
    for n,h in HITS.items():
        if h-0.5<=t<h+0.55:
            up=sm(seg01(t,h-0.5,h-0.14)); down=sm(seg01(t,h-0.14,h)); rec=sm(seg01(t,h+0.05,h+0.5))
            if t<h-0.14: d['rh']=lerp3((0.26,1.0,0.42),(0.28,1.6,0.05),up); d['swing']=lerp(1.0,0.15,up)
            elif t<h: d['rh']=lerp3((0.28,1.6,0.05),(0.26,0.95,0.62),down); d['swing']=lerp(0.15,1.85,down); d['lean']+=0.3*down
            else: d['rh']=lerp3((0.26,0.95,0.62),(0.26,1.0,0.42),rec); d['swing']=lerp(1.85,1.0,rec); d['lean']+=0.3*(1-rec)
    if T_NOD<=t<T_NOD+0.7: d['lean']+=0.22*math.sin(PI*seg01(t,T_NOD,T_NOD+0.7))                    # the nod
    return d

# ======================= flashback: the rookie, nine goblins, the elder =======================
RC=(0.0,0.0,5.6)                                                       # where the rookie stops
NINE=[(-0.9+0.9*(i%3)+0.12*hsh(i),9.0+0.85*(i//3)+0.15*hsh(i,1)) for i in range(9)]
def rookie_state(t):
    if not infb(t) or t>=T_GONE+0.35: return None
    u=sm(seg01(t,T_FB[0],T_RUSH-0.35)); z=lerp(2.5,RC[2],u)
    d=dict(base=(0.0,0.0,z),yaw=0.0,walk=t*7.0 if u<0.98 else 0.0,lean=0.02,head=0.25*sm(seg01(t,T_RUSH-0.6,T_RUSH-0.2)))
    if t>=T_RUSH: d.update(lean=-0.15*sm(seg01(t,T_RUSH,T_RUSH+0.4)),head=0.3)
    return d
def rookie_visible(t):
    if T_FLASH<=t<T_GONE+0.35: return int((t-T_FLASH)*24)%2==0
    return True
def fb_goblin(i,t):
    """nine goblins: wait in a bunch, rush the rookie, pile on, then stand in a ring with their heads down"""
    if not infb(t): return None
    x0,z0=NINE[i]; a=2*PI*i/9+0.4
    r_ring=lerp(0.55,1.0,sm(seg01(t,T_GONE+0.2,T_GONE+1.2)))
    tx=RC[0]+r_ring*math.cos(a); tz=RC[2]+0.4+r_ring*math.sin(a)*0.9
    u=sm(seg01(t,T_RUSH+0.05*i,T_RUSH+0.05*i+0.8))
    x=lerp(x0,tx,u); z=lerp(z0,tz,u); yaw=lerp(PI,math.atan2(RC[0]-tx,RC[2]+0.2-tz),u)
    st=dict(n=70+i,base=(x,0.0,z),yaw=yaw,walk=t*10.0 if 0<u<1 else 0.0,lean=0.0,rh=(0.2,0.32,0.06),lh=None,eyes=1.0,smile=-0.2,head=0.0,hop=0.0,fall=0.0,club_up=0.0)
    if 0<u<1: st.update(rh=(0.22,0.62,0.18),club_up=1.0,lean=0.15,smile=-0.6)
    if u>=1 and t<T_GONE+0.2: st.update(rh=(0.22,0.62,0.18),club_up=1.0,lean=0.15,smile=0.6,hop=0.14*abs(math.sin(t*15+i)))   # the dogpile
    if t>=T_GONE+0.2:                                                            # the ring: heads down
        k=sm(seg01(t,T_GONE+0.2,T_GONE+0.9)); st.update(smile=-1.0,eyes=0.5,head=-0.3*k,lean=0.12*k,club_up=0.0,rh=(0.2,0.32,0.06))
    return st
def elder_state(t):
    if not infb(t) or t<T0['6']: return None
    a=2*PI*4.5/9+0.4; r=1.0; p0=(RC[0]+r*math.cos(a),RC[2]+0.4+r*math.sin(a)*0.9); EP=(-1.95,7.0)
    u=sm(seg01(t,*T_ELD)); x=lerp(p0[0],EP[0],u); z=lerp(p0[1],EP[1],u)
    yaw=lerp(math.atan2(RC[0]-p0[0],RC[2]-p0[1]),-PI/2,sm(seg01(t,T_ELD[0]+0.2,T_ELD[1])))
    st=dict(n=60,base=(x,0.0,z),yaw=yaw,walk=t*8.0 if 0<u<1 else 0.0,lean=0.08,rh=(0.2,0.32,0.06),lh=None,eyes=0.7,smile=-0.5,head=0.0,hop=0.0,fall=0.0,club_up=0.0,has_club=False,hat=True)
    if t>=T_CARVE0: st.update(rh=(0.22,0.82+0.07*math.sin(t*16),0.26),lean=0.1,eyes=0.9)      # chiselling
    return st
def board_visible(t): return (not infb(t)) or t>=T_CARVE0
def board_text(t):
    """(line 1, line 2) of the rule board; in the flashback line 2 is carved letter by letter"""
    full='ONE AT A TIME'
    if not board_visible(t): return None
    if infb(t) and t>=T_CARVE0:
        n=int(len(full)*sm(seg01(t,*T_TYPE))); return ('RULE 1',full[:n])
    return ('RULE 1',full)

# ======================= set: hallway + the rule board =======================
SIGN_C=(-2.52,2.5,7.6)
def board(t):
    if not board_visible(t): return []
    cx,cy,cz=SIGN_C; return box(-2.6,-2.47,cy-0.34,cy+0.34,cz-0.7,cz+0.7,(60,40,26))+box(-2.47,-2.45,cy-0.3,cy+0.3,cz-0.66,cz+0.66,(20,14,10),emit=True)
def dark(t):
    return sm(seg01(t,*T_DARK))*(1-sm(seg01(t,*T_LIGHT)))
def lights(t):
    dk=dark(t); L=[]
    for k,z in enumerate(LR.TORCH_Z[:7]):
        x=(-1 if k%2 else 1)*(LR.HALL_X-0.5); L.append(((x,2.5,z),(255,170,90),(1.1+0.12*math.sin(t*11+k))*lerp(1.0,0.45,dk)))
    L.append(((0,2.0,LR.HALL_Z0+0.5),(255,240,210),1.2*(1-dk)))
    L.append(((0.0,3.0,7.0),(200,200,230),0.6*(1-dk)))
    return L

# ======================= cameras =======================
def creep(t,t0,rate=0.0014): return motion.creep(t,t0,rate,FPS)
def cam_shot(t):
    if t<CUTS[1]:      # A: over the knight's shoulder: the front goblin gets hit
        tgt=(0.5,0.85,7.2); return dict(cam=motion.dolly((1.5,1.45,4.3),tgt,creep(t,0.0,0.0016)),tgt=tgt,fov=58)
    if t<CUTS[2]:      # B: the rule board on the wall
        tgt=(-2.5,2.35,7.6); return dict(cam=motion.dolly((-0.3,1.75,5.7),tgt,creep(t,CUTS[1],0.0014)),tgt=tgt,fov=54)
    if t<CUTS[3]:      # F1 (flashback): from the side, the rookie walks in, nine goblins rush him
        tgt=(0.0,0.8,6.8); return dict(cam=motion.dolly((-1.9,1.25,3.3),tgt,creep(t,CUTS[2],0.0012)),tgt=tgt,fov=62)
    if t<CUTS[4]:      # F2: the ring of goblins where he stood, then the dark
        tgt=(0.0,0.55,6.5); return dict(cam=motion.dolly((1.25,1.1,4.8),tgt,creep(t,CUTS[3],0.0016)),tgt=tgt,fov=56)
    if t<CUTS[5]:      # G: the elder carves the rule
        tgt=(-2.4,1.7,7.3); return dict(cam=motion.dolly((-0.2,1.5,5.1),tgt,creep(t,CUTS[4],0.0014)),tgt=tgt,fov=56)
    if t<CUTS[6]:      # A2: from behind the queue: the next hero, the next goblin
        tgt=(0.5,0.78,7.15); return dict(cam=motion.dolly((-1.25,0.95,8.3),tgt,creep(t,CUTS[5],0.0012)),tgt=tgt,fov=62)
    if t<CUTS[7]:      # H: the faces in the line
        tgt=(0.7,0.8,10.2); return dict(cam=motion.dolly((-0.3,0.95,8.3),tgt,creep(t,CUTS[6],0.0014)),tgt=tgt,fov=56)
    if t<CUTS[8]:      # D: he steps up anyway, the hit, LEVEL 2
        tgt=(0.45,0.8,7.1); return dict(cam=motion.dolly((-1.25,0.95,8.3),tgt,creep(t,CUTS[7],0.0012)),tgt=tgt,fov=62)
    tgt=(0.5,1.0,8.6); return dict(cam=motion.dolly((-1.95,1.2,5.4),tgt,creep(t,CUTS[8],0.0018)),tgt=tgt,fov=64)   # E: the welcome, the whole queue waves
def shake_px(t):
    for h in list(HITS.values())+[T_RUSH+0.5]:
        k=motion.kick(t,h,2.0,6,FPS)
        if k: return (0.0,k)
    return (0.0,0.0)

# ======================= render =======================
RND=Renderer(W,H,fog=(14,10,10))
VI=[None]
def render3d(t):
    sh=cam_shot(t); cam=Camera.look(sh['cam'],sh['tgt']); Gs=[]
    if infb(t):
        for i in range(9):
            st=fb_goblin(i,t)
            if st: Gs.append(FB.prelit(gmodel(**st),sh['cam'],warm=0.3))
        el=elder_state(t)
        if el: Gs.append(FB.prelit(gmodel(**el),sh['cam'],warm=0.3))
        rk=rookie_state(t)
        if rk and rookie_visible(t): Gs.append(FB.prelit(rookie_model(**rk),sh['cam']))
        layers=[LR.HALL,LR.torches(t),board(t)]+Gs
    else:
        for n in NUMS:
            st=gstate(n,t)
            if st is None: continue
            if st['base'][2]>sh['cam'][2]+30: continue
            Gs.append(FB.prelit(gmodel(**st),sh['cam'],warm=0.3))
        layers=[LR.HALL,LR.torches(t),board(t),puffs(t)]+Gs+[FB.prelit(FB.knight(**kstate(t)),sh['cam'])]
    L=lights(t)
    for h in HITS.values():
        if h-F<=t<h+0.3: L=L+[((QX,1.2,FS[2]-0.3),(255,220,170),0.9*math.exp(-(t-h)*9))]
    img,vi,zb=zrender(RND,cam,layers,L,fov=sh['fov'],fog_start=6,fog_end=24,ambient=lerp(0.3,0.12,dark(t)),shake=shake_px(t),return_z=True)
    VI[0]=vi
    return post.ps1(img),vi

# ======================= HUD / UI =======================
def otext(d,s,x,y,col,sc=1):
    o=max(1,sc//2)
    for ox,oy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)): font.text(d,s,x+ox*o,y+oy*o,(0,0,0),sc,None)
    font.text(d,s,x,y,col,sc,None)
def ctext(d,s,y,col,sc=1): otext(d,s,(W-font.width(s,sc))//2,y,col,sc)
def proj(p):
    if VI[0] is None: return None
    return RND.project(p,VI[0])
def sign_overlay(d,t):
    """RULE 1 / ONE AT A TIME written on the board (projected centre; scale from the projected board width)"""
    bt=board_text(t)
    if bt is None: return
    c=proj(SIGN_C); a=proj((SIGN_C[0],SIGN_C[1],SIGN_C[2]-0.66)); b=proj((SIGN_C[0],SIGN_C[1],SIGN_C[2]+0.66))
    if not c or not a or not b: return
    wpx=math.hypot(a[0]-b[0],a[1]-b[1])
    if wpx<40 or not (10<c[0]<W-10 and 10<c[1]<H-10): return
    sc=max(1,int(wpx/92)); s1,s2=bt; y=int(c[1]-(7*sc+3*sc+7*sc)/2)
    cl=lambda x,w: int(max(3,min(W-3-w,x)))
    otext(d,s1,cl(c[0]-font.width(s1,sc)/2,font.width(s1,sc)),y,YEL,sc)
    if s2:
        full='ONE AT A TIME'; x2=c[0]-font.width(full,sc)/2; otext(d,s2,cl(x2,font.width(full,sc)),y+10*sc,WHT,sc)
def hud(d,t):
    sign_overlay(d,t)
    if T_LEVEL<=t<T_LEVEL+1.5:
        u=seg01(t,T_LEVEL,T_LEVEL+0.25); sc=3 if u>=1 else 4; ctext(d,'LEVEL 2',64,YEL,sc)
def flash_alpha(t):
    a=0.0
    for h in HITS.values():
        if h-F<=t<h+0.2: a=max(a,0.22*(1.0-seg01(t,h,h+0.2)))
    if T_FLASH-F<=t<T_FLASH+0.3: a=max(a,0.45*(1.0-seg01(t,T_FLASH,T_FLASH+0.3)))
    return a

# ======================= subtitles (1080x1920, 1.25x, sentence timings from the voice) =======================
SUB_F=7.0; ADV=6.9; HIL={'ONCE?','ONCE.','RULE','RULE..','FIRST','BACK.','LIVED.','LOSE.','TWO.','WELCOME.'}
def _rows(text,n=17):
    out=[]; c=[]
    for w_ in text.split():
        if len(' '.join(c+[w_]))>n and c: out.append(c); c=[w_]
        else: c.append(w_)
    return out+[c]
def _subs():
    res=[]
    for k,t0 in LINES:
        for i,(a,b,tx) in enumerate(SCR['sent'][k]):
            nxt=SCR['sent'][k][i+1][0] if i+1<len(SCR['sent'][k]) else b+(0.6 if k=='1' else 0.25)
            res.append((t0+a-0.03,t0+nxt-0.02,_rows(tx.replace('...','..'),14 if k=='1' else 17),k))
    return res
SUBS=_subs()
def _tw(wd,sc): return len(wd)*ADV*sc
def sub_overlay(t):
    """line 1 (the question) is a centred title card with an outline, no box; every other sentence is a roomy box near the bottom"""
    for a,b,rows,key in SUBS:
        if a<=t<b:
            card=(key=='1'); sc=9.0 if card else SUB_F; lh=(12.5 if card else 12.8)*sc
            lines=[' '.join(r) for r in rows]; wmax=max(_tw(l,sc) for l in lines)-(ADV-6)*sc
            padx=5.5*sc; pady=3.6*sc; w=wmax+2*padx; h=(len(lines)-1)*lh+7*sc+2*pady
            x0=(W*S-w)/2; y0=(H*S*0.43-h/2) if card else (H*S-150-h)
            ov=Image.new('RGB',(W*S,H*S),(0,0,0)); m=Image.new('L',(W*S,H*S),0); do=ImageDraw.Draw(ov); dm=ImageDraw.Draw(m)
            if not card: dm.rectangle([round(x0),round(y0),round(x0+w)-1,round(y0+h)-1],fill=255)
            o=max(2,round(sc*0.55)); cells=[]
            for i,r in enumerate(rows):
                lw=_tw(' '.join(r),sc)-(ADV-6)*sc; x=x0+(w-lw)/2
                for wd in r:
                    col=YEL if wd.upper() in HIL or wd.upper().strip('.,!?:') in HIL else WHT; font.check(wd)
                    for k_,ch in enumerate(wd.upper()):
                        for j,row in enumerate(font.FONT[ch]):
                            for i2,bit in enumerate(row):
                                if bit=='1': X=x+(k_*ADV+i2)*sc; Y=y0+pady+i*lh+j*sc; cells.append((round(X),round(Y),round(X+sc)-1,round(Y+sc)-1,col))
                    x+=_tw(wd,sc)+ADV*sc
            if card:
                for bx in cells: dm.rectangle([bx[0]-o,bx[1]-o,bx[2]+o,bx[3]+o],fill=255)
            for bx in cells: do.rectangle(bx[:4],fill=bx[4]); dm.rectangle(bx[:4],fill=255)
            return ov,m
    return None
def fb_tint(t):
    return sm(seg01(t,T_FB[0],T_FB[0]+0.25))*(1-sm(seg01(t,T_FB[1]-0.2,T_FB[1])))
def frame_low(t):
    img,vi=render3d(t); fa=flash_alpha(t)
    if fa>0:
        col=(255,70,60) if T_FLASH-F<=t<T_FLASH+0.3 else (255,255,255)
        img=Image.fromarray(np.clip(np.asarray(img).astype(np.float32)*(1-fa)+np.array(col,np.float32)*fa,0,255).astype(np.uint8))
    dk=dark(t); ft=fb_tint(t)
    if dk>0 or ft>0:
        m=np.array(lerp3((1,1,1),(0.62,0.66,0.9),dk),np.float32)*np.array(lerp3((1,1,1),(0.78,0.84,1.0),ft),np.float32)
        img=Image.fromarray(np.clip(np.asarray(img).astype(np.float32)*m,0,255).astype(np.uint8))
    d=ImageDraw.Draw(img); hud(d,t)
    return img
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
    shp.resize((shp.width*2,640),Image.NEAREST).save(os.environ.get('TEST_OUT','test.png')); sys.exit()

# ======================= QA manifest =======================
def _geom(t,name,st,V):
    out=[]
    if V[:,1].min()<-0.05: out.append(('floor',f'{name} under the floor'))
    if (np.abs(V[:,0])>LR.HALL_X-0.02).any(): out.append(('wall',f'{name} inside a hall wall'))
    return out
def _kn(t): return None if infb(t) else kstate(t)
def _g(n): return lambda t: None if infb(t) else gstate(n,t)
QA=dict(fps=FPS,dur=DUR,W=W,frame=frame,
    chars={'knight':(_kn,FB.knight,'sword','hand'),'g47':(_g(47),gmodel,'none','none'),'g46':(_g(46),gmodel,'none','none'),'g45':(_g(45),gmodel,'none','none')},
    geom=_geom,camera=lambda t: cam_shot(t)['cam'],min_cam_dist=0.4,camera_ok=lambda p: -2.45<p[0]<2.45 and -5.8<p[2]<80 and 0.1<p[1]<3.4,
    allow_jump=[(w,f/FPS) for w in ('knight','g47','g46','g45') for c in CUTS for f in range(int(c*FPS)-2,int(c*FPS)+4)],
    weapon_events=[],
    scenes=[dict(id=f's{i}',t0=CUTS[i],t1=CUTS[i+1],action=a) for i,a in enumerate((
        'hook: over the knight, the front goblin gets hit (CAM A)',
        'the rule board on the wall: RULE 1, ONE AT A TIME (CAM B)',
        'flashback: the rookie walks in, nine goblins rush him, the dogpile (CAM F1)',
        'flashback: the ring of goblins with their heads down, the dark (CAM F2)',
        'flashback: the elder carves the rule (CAM G)',
        'the next hero, the next goblin gets hit (CAM A2)',
        'the faces in the line: #47 gulps (CAM H)',
        '#47 steps up anyway, the hit, LEVEL 2 (CAM D)',
        'the welcome: the whole queue waves at the knight (CAM E)'))],
    texts=lambda: [('hud','RULE 1',1),('hud','ONE AT A TIME',1),('hud','LEVEL 2',3)])

# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=31); sr=s.sr; n=s.n; t=s.t; BED=np.zeros(n); FX=np.zeros(n)
    def put(buf,x,t0,v=1.0):
        i=int(t0*sr)
        if i>=n or i<0: return
        j=min(n,i+len(x)); buf[i:j]+=(x*v)[:j-i]
    def nb(t0,d,lo,hi,v,seed,shape=2): put(FX,s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v)
    def tone(t0,m,d,v,wave='sq',duty=0.5,dec=3.0,att=0.005,glide=0.0):
        f=440*2**((m-69)/12); tt=s.T(d); fr=f*(1+glide*tt/d); ph=np.cumsum(fr)/sr%1
        x=np.where(ph<duty,1.0,-1.0) if wave=='sq' else (4*np.abs(ph-0.5)-1 if wave=='tri' else np.sin(2*np.pi*ph))
        put(FX,x*np.minimum(1,tt/att)*np.exp(-tt*dec),t0,v)
    def thud(t0,f=55,v=0.3,d=0.6):
        tt=s.T(d); put(FX,np.sin(2*np.pi*f*tt*(1-0.3*tt/d))*np.exp(-tt*8)+s.filt_short(s.noise(d,int(t0*13)),lo=60,hi=700)*np.exp(-tt*12)*0.6,t0,v)
    def bonk(t0,v=0.2,seed=0):
        tt=s.T(0.35); put(FX,np.sin(2*np.pi*190*tt*(1-0.4*tt))*np.exp(-tt*14)+s.filt_short(s.noise(0.35,seed),lo=300,hi=3000)*np.exp(-tt*28)*0.7,t0,v)
    def step(t0,v=0.04,seed=0):
        tt=s.T(0.1); put(FX,s.filt_short(s.noise(0.1,seed),lo=700,hi=4000)*np.exp(-tt*50),t0,v)
    def ding(t0,v=0.06):
        for m,dt in ((88,0.0),(84,0.16)): tone(t0+dt,m,0.7,v,'sin',dec=4)
    # ---- bed: hall drone + torch crackle; the queue murmur (goblin chatter) while the lights are on
    BED+=s.filt(s.rng.normal(0,1,n),lo=30,hi=200)*0.08
    BED+=soft_fire(s,level=0.004,crackles_per_s=3,seed=32)       # soft fire bed + real crackles (no per-sample gate)
    dk=np.array([dark(x) for x in t[::200]]); dk=np.interp(np.arange(n),np.arange(0,n,200),dk)
    rng=np.random.default_rng(7); tt=0.0
    while tt<DUR-0.2:                                                     # goblin murmur: short squeaky syllables, many voices
        d=rng.uniform(0.07,0.16); f0=rng.uniform(260,420); T_=s.T(d); ph=np.cumsum(f0*(1+0.3*np.sin(np.pi*T_/d))*np.ones(len(T_)))/sr%1
        x=s.filt_short(2*ph-1,lo=300,hi=1800)*np.sin(np.pi*T_/d)**2
        i=int(tt*sr); g=1.0-0.85*dk[min(i,n-1)]
        if T_GONE<tt<T_LIGHT[0]: g*=0.3
        if infb(tt) and tt<T_RUSH-0.3: g*=0.4
        put(BED,x,tt,0.022*g*rng.uniform(0.5,1.0)); tt+=rng.uniform(0.04,0.14)
    # ---- hits: whoosh, bonk, thud of the fall, defeat puff
    for nn,h in HITS.items():
        nb(h-0.22,0.2,500,5000,0.06,10+nn); bonk(h,0.22,20+nn); thud(h+0.3,70,0.18,0.4)
        nb(h+0.6,0.35,1500,8000,0.05,30+nn); tone(h+0.6,84,0.25,0.025,'sq',duty=0.25,dec=8,glide=0.5)
    # ---- the rule board lights up (line 2): two soft dings
    ding(T0['2']+0.1,0.05)
    # ---- flashback: the kid walks in (steps), nine goblins rush (stomp + squeaks), the dogpile, a hollow thud, then nearly nothing
    for k in range(int((T_RUSH-0.35-T_FB[0])/0.32)): step(T_FB[0]+0.1+k*0.32,0.03,200+k)
    for k in range(14): step(T_RUSH+0.05+k*0.06,0.045,220+k); nb(T_RUSH+0.1+k*0.05,0.06,700,2600,0.02,240+k,1)
    thud(T_FLASH,52,0.22,0.6); nb(T_FLASH-0.05,0.5,200,2000,0.07,260)
    tone(T_GONE,57,0.9,0.05,'sq',duty=0.3,dec=3,glide=-0.7)                                   # the kid is gone: a falling tone
    # ---- the dark: the room tone drops, only torches and a low hum (no dead gap)
    thud(T_DARK[0],48,0.2,0.5)
    pa,pb=T_GONE+0.3,T_LIGHT[0]+0.3; m=(t>=pa)&(t<pb); env=np.clip(np.minimum(t-pa,pb-t)/0.3,0,1)*m
    FX+=soft_fire(s,level=0.012,crackles_per_s=5,mask=env,seed=33)
    FX+=(np.sin(2*np.pi*98*t)+0.5*np.sin(2*np.pi*147*t))*0.03*env
    k=0
    while T_DARK[1]+0.1+k*0.7<T_LIGHT[0]: tone(T_DARK[1]+0.1+k*0.7,100,0.04,0.012,'sin',dec=30); k+=1
    # ---- the elder walks to the wall and carves: stone scrape + chisel ticks while the letters appear
    for k in range(4): step(T_ELD[0]+0.1+k*0.3,0.03,280+k)
    nb(T_CARVE0-0.1,0.3,600,3000,0.04,290,1)
    kk=0
    while T_CARVE0+kk*0.13<T0['8']-0.35: tone(T_CARVE0+kk*0.13,92+(kk%3)*2,0.04,0.025,'sq',duty=0.25,dec=45); nb(T_CARVE0+kk*0.13,0.05,1500,5000,0.025,300+kk); kk+=1
    tone(T0['8']-0.35,79,0.5,0.03,'sq',duty=0.25,dec=3)                                      # the rule is done: a soft chime
    # ---- present: queue shuffle, the nod, the gulp, LEVEL 2 jingle, the welcome (a small cheer)
    for nn,s_ in STEP.items():
        for k in range(4): step(s_+0.05+k*0.14,0.03,40+nn*5+k)
    nb(ws('9',0)+1.6,0.5,300,2500,0.05,50,1)
    for k_,m in enumerate((72,76,79,84)): tone(T_LEVEL+k_*0.09,m,0.3 if k_<3 else 0.8,0.045,'sq',duty=0.25,dec=4 if k_<3 else 2)
    for k_ in range(6): tone(T_WAVE+0.2+k_*0.21,(79,76,81,79,84,81)[k_],0.25,0.02,'sq',duty=0.3,dec=5)
    # ---- voice
    NB=np.zeros(n); wins=[]
    for k_,t0 in LINES:
        a,ar=_sf.read(os.path.join(TTS_DIR,'eq2',f'{k_}.wav')); a=a if a.ndim==1 else a.mean(1)
        a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a); put(NB,a,t0); wins.append((t0,t0+len(a)/sr))
    g=duck_envelope(n,sr,wins,-6.0,0.05,0.25); bed=BED*g; fx=FX*(0.55+0.45*g)
    L=bed+fx; R_=np.roll(bed,700)+np.roll(fx,200); pk=max(np.abs(L).max(),np.abs(R_).max()); gv=pk*1.6/np.abs(NB).max()
    s.L=L+NB*gv; s.R=R_+NB*gv; s.reverb(0.14,length=1.4,decay=3.0)
    end=np.clip((DUR-t)/0.6,0,1); s.L*=end; s.R*=end
    return s.save(path,peak=0.7)
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'enemies_queue.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'eq_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.96,vignette=0.25,grain=1.5,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(frame_final(f/FPS),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
