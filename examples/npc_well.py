"""WHY DO NPCs REPEAT THE SAME LINE? (Insert Disc 2, 14-day test day 2, 22:00 slot, Tone 2.0) ~48 s PS1 drama, 9:16, nightkit.
Brief: briefs/npc_well.md. An old villager says "THE WELL IS DRY, TRAVELER." to every hero for forty years, so nobody climbs down where his
wife's ring fell. One knight climbs down and brings it up; the old man says something new and walks away from the well.
Reuses: locked knight (examples/final_boss.py; cape colours only for the passing heroes).
NEW: old villager + wife (box humans), stone well + windlass + rope, village at dusk, lantern, ring, RPG dialogue box.
Voice: python tools/tts/nw.py src ; <chatterbox python> tools/tts/vc.py nw ; python tools/tts/nw.py build vc  -> $TTS_DIR/nw/
Run: TEST=1,5,9 python examples/npc_well.py -> test.png | PART=a:b | PART=audio | tools/render_parts.py --prefix nw --audio npc_well.wav"""
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

OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6; F=1.0/FPS
PI=math.pi; sm=motion.smooth
def seg01(t,a,b): return max(0.0,min(1.0,(t-a)/(b-a)))
def lerp(a,b,u): return a+(b-a)*u
def lerp3(a,b,u): return tuple(a[i]+(b[i]-a[i])*u for i in range(3))
def hsh(i,s=0): v=math.sin(i*127.1+s*311.7)*43758.5453; return v-math.floor(v)
box=FB.box; xform=FB.xform; seg=FB.seg
WHT=(242,238,226); YEL=(255,210,60); GRAY=(150,150,160); GOLD=(236,190,60)

# ======================= voice timings (tools/tts/nw.py) =======================
SCR=json.load(open(os.path.join(TTS_DIR,'nw','script.json')))
GAP=0.3; EXTRA={'4':0.2,'6':0.2,'8':0.1,'10':1.3,'11':0.3,'12':0.1}
def _lines():
    t=0.12; out=[]
    for k in [str(i) for i in range(1,14)]: out.append((k,round(t,3))); t+=SCR['dur'][k]+GAP+EXTRA.get(k,0.0)
    return out
LINES=_lines(); T0=dict(LINES)
DUR=round(T0['13']+SCR['dur']['13']+1.3,2); N=int(round(DUR*FPS))
def ws(k,i): return T0[k]+SCR['sent'][k][i][0]
def we(k,i): return T0[k]+SCR['sent'][k][i][1]

# ======================= story events =======================
WELL=(0.0,6.2); MAN0=(-1.75,0.0,5.7); MAN1=(-1.2,0.0,5.75); LANT=(1.5,1.95,4.8)   # MAN0 -> MAN1: he shuffles closer to the well while the flashback plays
HEROES=[(T0['2']+1.0,(196,60,52),3.8),(ws('3',0)+0.55,(70,150,84),4.3),(ws('3',1)+0.35,(150,84,196),3.5),(ws('3',2)+0.35,(220,170,50),4.0)]  # (time at x=-1.4, cape, lane z)
HERO_V=4.4
BOXES=[(0.0,'THE WELL IS DRY, TRAVELER.'),(HEROES[0][0]-0.35,'THE WELL IS DRY, TRAVELER.'),(HEROES[1][0]-0.35,'THE WELL IS DRY, TRAVELER.'),
       (HEROES[2][0]-0.3,'THE WELL IS DRY, TRAVELER.'),(HEROES[3][0]-0.3,'THE WELL IS DRY, TRAVELER.'),
       (T0['7']+0.75,'THE WELL IS DRY, TRAVELER.'),(ws('12',1)-0.05,'...THANK YOU.')]       # Enes's own recording: he now says it (line 12, sentence 1)
BOX_LEN=1.9
SEAS=[('leaves',ws('3',0)-0.3,ws('3',1)-0.3),('snow',ws('3',1)-0.3,ws('3',2)-0.3),('rain',ws('3',2)-0.3,T0['4']+0.5)]
T_FB=(T0['5']-0.2,T0['7']-0.1)                       # flashback window
T_RING=T0['5']+2.35                                  # the ring leaves her hand
T_WDOWN=(T0['6']+0.35,T0['6']+1.9)                   # she climbs down
T_GREY=(we('6',1)-0.2,T0['7']-0.12)                  # flashback fades to grey
T_K_IN=T0['9']-0.45; T_K_STOP=T0['9']+0.85           # knight walks in, stops
T_K_RIM=(T0['10']+0.05,T0['10']+0.8); T_K_UP=(T0['10']+0.8,T0['10']+1.15); T_K_DOWN=(T0['10']+1.2,T0['10']+2.1)
T_K_ASC=(T0['10']+2.3,T0['11']+0.35); T_K_OUT=(T0['11']+0.35,T0['11']+1.0)
T_HOLD=ws('11',0)+1.1                                # he holds out the ring
T_TAKE=(we('12',0)-1.7,we('12',0)-0.5)               # the old man takes the ring (just before he says "Thank you")
T_WALK=(T0['13']+0.15,DUR)                           # the old man walks away
CUTS=[0.0,T0['3']-0.06,T0['4']-0.06,T_FB[0],T0['7']-0.1,T0['8']-0.06,T0['9']-0.06,ws('10',1)+0.35,T0['11']-0.15,T_HOLD-0.2,T0['12']-0.06,T0['13']-0.1,DUR]

# ======================= humans (old man, wife) =======================
SKIN=(214,170,132); SKIN_D=(176,132,100); GREY=(176,174,170); COAT=(74,66,58); COAT_D=(54,48,44); TROUS=(46,42,42)
def frustum(yb,yt,hwb,hdb,hwt,hdt,col,xf):
    v=[(-hwb,yb,-hdb),(hwb,yb,-hdb),(hwt,yt,-hdt),(-hwt,yt,-hdt),(-hwb,yb,hdb),(hwb,yb,hdb),(hwt,yt,hdt),(-hwt,yt,hdt)]
    v=[xf(p) for p in v]; Fc=[(0,1,2,3),(5,4,7,6),(4,0,3,7),(1,5,6,2),(3,2,6,7),(4,5,1,0)]
    return [quad([v[i] for i in f],col) for f in Fc]
def human(base,yaw,kind='man',lean=0.0,head=0.0,tilt=0.0,rh=None,lh=None,blink=0.0,walk=0.0,gaze=0.0,cane=True,hair=None,coat_col=None,acc=None,**_):
    """kind: 'man' (old, grey beard) | 'woman' | 'boy' (man proportions, short brown hair, no beard). Format 3.0 additions (all optional, default = the old output):
    hair = colour override for every hair part; coat_col = (coat, coat_dark); acc(Hh, T, Wd) -> extra faces in head space / torso space / world space (hat, bun, apron...)."""
    b=np.array(base,float); Rb=FB.Ry(yaw)
    def Wd(p): return tuple(b+Rb@np.array(p,float))
    man=(kind in ('man','boy')); old=(kind=='man'); hy=0.62 if man else 0.7; hairc=hair or (GREY if old else (96,62,40) if kind=='boy' else None)
    def T(p): p=np.array(p,float); piv=np.array([0,hy,0]); return Wd(piv+FB.Rx(lean)@(p-piv))
    Q=[]; coat=COAT if man else (150,66,64); coat_d=COAT_D if man else (112,48,48)
    if coat_col: coat,coat_d=coat_col
    sw=0.45*math.sin(walk)
    for sx,ph in ((-1,1),(1,-1)):
        hp=np.array([sx*0.07,hy,0]); a=ph*sw; ft=hp+np.array([0,-0.6*math.cos(a),0.6*math.sin(a)]); ft[1]=max(0.04,ft[1])
        lq,_=FB.limb(hp,ft,(0,0,1),0.62,0.1,TROUS,TROUS,0.09); Q+=xform(lq,Wd); Q+=box(ft[0]-0.05,ft[0]+0.05,0.0,0.05,ft[2]-0.05,ft[2]+0.12,(30,26,26),xf=Wd)
    hem=0.3 if man else 0.1
    Q+=frustum(hem,1.08,0.25 if man else 0.3,0.17 if man else 0.2,0.18,0.12,coat,T)                 # coat / dress
    Q+=box(-0.19,0.19,1.0,1.1,-0.13,0.13,coat_d,xf=T)                                                # shoulders / collar
    if man: Q+=box(-0.2,0.2,0.62,0.68,-0.14,0.14,(40,32,26),xf=T)                                    # belt
    sh={-1:np.array([-0.2,1.05,0]),1:np.array([0.2,1.05,0])}; idle={-1:np.array([-0.26,0.68,0.05]),1:np.array([0.26,0.68,0.05])}
    hand={-1:np.array(lh,float) if lh is not None else idle[-1],1:np.array(rh,float) if rh is not None else idle[1]}
    for sx in (-1,1):
        aq,_=FB.limb(sh[sx],hand[sx],(sx*0.5,-0.4,-0.5),0.55,0.1,coat,coat_d,0.09); Q+=xform(aq,T)
        hp=hand[sx]; Q+=box(hp[0]-0.04,hp[0]+0.04,hp[1]-0.04,hp[1]+0.04,hp[2]-0.04,hp[2]+0.04,SKIN,xf=T)
    if man and cane:
        hw=np.array(T(hand[-1]+np.array([0,0.0,0.0]))); Q+=seg(hw+np.array([0,0.02,0]),hw+np.array([0,-hw[1]+b[1]+0.0,0.0]),0.035,(88,60,36))
    hp0=np.array([0,1.12,0.03]); Rh=FB.Ry(head)@FB.Rx(tilt)
    def Hh(p): p=np.array(p,float); return T(hp0+Rh@(p-hp0))
    Q+=box(-0.115,0.115,1.14,1.4,-0.115,0.115,SKIN,xf=Hh)                                            # head
    for sx in (-1,1):
        Q+=box(sx*0.05-0.028,sx*0.05+0.028,1.275,1.315,0.114,0.122,(228,222,206),xf=Hh)             # eye whites
        Q+=box(sx*0.05-0.014+gaze*0.012,sx*0.05+0.014+gaze*0.012,1.28,1.31,0.121,0.128,(26,22,22),xf=Hh)   # pupils
        if blink>0: Q+=box(sx*0.05-0.03,sx*0.05+0.03,1.272,1.272+0.046*blink,0.123,0.13,SKIN,xf=Hh)
        Q+=seg((sx*0.095,1.342-0.0,0.13),(sx*0.02,1.362,0.13),0.026,hairc if man else (92,60,40),0.02) if man else seg((sx*0.09,1.345,0.13),(sx*0.02,1.35,0.13),0.016,hair or (92,60,40),0.02)   # brows (sad)
    Q+=box(-0.018,0.018,1.2,1.285,0.114,0.15,SKIN_D,xf=Hh)                                           # nose
    if old:
        Q+=box(-0.075,0.075,1.18,1.21,0.114,0.14,hairc,xf=Hh)                                        # moustache
        Q+=box(-0.11,0.11,1.02,1.18,-0.02,0.128,hairc,xf=Hh)                                         # beard
        for sx in (-1,1): Q+=box(sx*0.115,sx*0.14,1.2,1.34,-0.09,0.06,hairc,xf=Hh)                   # side hair
        Q+=box(-0.115,0.115,1.2,1.34,-0.14,-0.115,hairc,xf=Hh)
        for yy in (1.375,1.39): Q+=box(-0.07,0.07,yy,yy+0.007,0.114,0.12,SKIN_D,xf=Hh)               # forehead wrinkles
    elif man:                                                                                        # boy: short hair cap, no beard
        Q+=box(-0.125,0.125,1.36,1.43,-0.125,0.125,hairc,xf=Hh)+box(-0.125,0.125,1.2,1.43,-0.14,-0.115,hairc,xf=Hh)
        for sx in (-1,1): Q+=box(sx*0.115,sx*0.14,1.26,1.40,-0.09,0.06,hairc,xf=Hh)
        Q+=box(-0.02,0.02,1.17,1.19,0.114,0.12,(150,70,70),xf=Hh)                                    # mouth
    else:
        hc=hair or (96,62,40)
        Q+=box(-0.125,0.125,1.34,1.42,-0.125,0.125,hc,xf=Hh)+box(-0.125,0.125,1.0,1.42,-0.14,-0.115,hc,xf=Hh)   # long hair
        Q+=box(-0.02,0.02,1.17,1.19,0.114,0.12,(150,70,70),xf=Hh)                                      # mouth
    if acc: Q+=acc(Hh,T,Wd)
    return Q
def loc(base,yaw,P): return tuple(FB.Ry(yaw).T@(np.array(P,float)-np.array(base,float)))
def lum_lit(Q,cam_p,lum=0.7,warm=0.15,tint=(1.0,1.0,1.0)):
    """bake simple lighting into a model (emissive): lum = overall brightness (lantern-lit dusk is darker than the knight's dungeon default)"""
    c=np.mean([q['c'] for q in Q],axis=0); Ld=np.array(cam_p,float)-c+np.array([0,2.5,0]); Ld/=np.linalg.norm(Ld)+1e-9
    for q in Q:
        if q['emit']: continue
        k=(0.42+0.58*abs(float(q['n']@Ld)))*lum; col=np.array(q['col'],float)*k*np.array(tint)
        col=col*(1-warm)+col*np.array([1.0,0.78,0.6])*warm; q['col']=tuple(int(min(255,v)) for v in col); q['emit']=True
    return Q

# ======================= knights (heroes recolour the cape only) =======================
def hero_knight(cape,**st):
    Q=FB.knight(**st)
    for q in Q:
        c=tuple(q['col'])
        if c==FB.CAPE: q['col']=cape
        elif c==FB.CAPE_D: q['col']=tuple(int(v*0.7) for v in cape)
        elif c==FB.PLUME: q['col']=tuple(min(255,int(v*1.1)) for v in cape)
    return Q
def hero_state(i,t):
    tp,cape,lane=HEROES[i]; x=-1.4+HERO_V*(t-tp)
    if x<-8 or x>8: return None
    return dict(base=(x,0.0,lane),yaw=PI/2,walk=x*4.0,run=0.0,sword='hip',lean=0.03,head=0.0)

# ======================= set =======================
STONE=(92,90,102); STONE_D=(66,64,76); STONE_L=(116,114,126); WOOD=(84,58,36); WOOD_D=(60,42,28); ROPE=(150,120,82)
def ground(season):
    cols={'clear':((40,52,44),(34,44,38)),'leaves':((54,50,38),(46,40,30)),'snow':((196,200,214),(180,186,204)),'rain':((30,40,40),(26,34,36))}[season]
    road={'clear':(78,66,56),'leaves':(80,66,50),'snow':(214,218,232),'rain':(52,46,44)}[season]
    Q=[]; xs=np.arange(-14,14.01,1.4); zs=list(np.arange(-3,8.0,1.4))+list(np.arange(8,34,2.4))
    for i in range(len(xs)-1):
        for j in range(len(zs)-1):
            cx=(xs[i]+xs[i+1])/2; cz=(zs[j]+zs[j+1])/2
            if abs(cx-WELL[0])<0.8 and abs(cz-WELL[1])<0.8: continue                  # the well shaft
            col=road if 2.8<cz<5.0 else cols[(i+j)%2]
            col=tuple(int(c*(0.92+0.1*hsh(i*31+j))) for c in col)
            Q.append(quad([(xs[i],0,zs[j]),(xs[i+1],0,zs[j]),(xs[i+1],0,zs[j+1]),(xs[i],0,zs[j+1])],col))
    return Q
GROUND={k:ground(k) for k in ('clear','leaves','snow','rain')}
def well_static():
    wx,wz=WELL; Q=[]
    for k,(y0,y1) in enumerate(((0,0.4),(0.4,0.8))):
        c=STONE if k==0 else STONE_D
        Q+=box(wx-0.7,wx+0.7,y0,y1,wz-0.7,wz-0.42,c)+box(wx-0.7,wx+0.7,y0,y1,wz+0.42,wz+0.7,c)+box(wx-0.7,wx-0.42,y0,y1,wz-0.42,wz+0.42,c)+box(wx+0.42,wx+0.7,y0,y1,wz-0.42,wz+0.42,c)
    Q+=box(wx-0.74,wx+0.74,0.8,0.88,wz-0.74,wz-0.38,STONE_L)+box(wx-0.74,wx+0.74,0.8,0.88,wz+0.38,wz+0.74,STONE_L)+box(wx-0.74,wx-0.38,0.8,0.88,wz-0.38,wz+0.38,STONE_L)+box(wx+0.38,wx+0.74,0.8,0.88,wz-0.38,wz+0.38,STONE_L)
    for k in range(6):                                                                          # the shaft (darker with depth)
        y0=-1.0*(k+1); y1=-1.0*k; c=tuple(int(v*(0.95-0.1*k)) for v in STONE_D)
        Q+=box(wx-0.52,wx-0.42,y0,y1,wz-0.52,wz+0.52,c)+box(wx+0.42,wx+0.52,y0,y1,wz-0.52,wz+0.52,c)+box(wx-0.42,wx+0.42,y0,y1,wz-0.52,wz-0.42,c)+box(wx-0.42,wx+0.42,y0,y1,wz+0.42,wz+0.52,c)
    Q+=box(wx-0.52,wx+0.52,-6.2,-6.0,wz-0.52,wz+0.52,(14,18,32))
    for sx in (-1,1): Q+=box(wx+sx*0.9-0.06,wx+sx*0.9+0.06,0,2.1,wz-0.06,wz+0.06,WOOD)               # windlass posts
    Q+=box(wx-1.0,wx+1.0,2.0,2.14,wz-0.07,wz+0.07,WOOD_D)+box(wx-1.0,wx-0.85,0.5,0.62,wz-0.07,wz+0.07,WOOD_D)
    Q+=box(wx-0.2,wx+0.2,2.14,2.2,wz-0.14,wz+0.14,WOOD_D)
    return Q
WELL_Q=well_static()
def lantern_post():
    x,y,z=LANT; Q=box(x-0.05,x+0.05,0,y,z-0.05,z+0.05,WOOD_D)+box(x-0.05,x+0.4,y,y+0.07,z-0.05,z+0.05,WOOD_D)
    Q+=box(x+0.3,x+0.5,y-0.3,y-0.05,z-0.1,z+0.1,(255,190,100),emit=True)+box(x+0.28,x+0.52,y-0.32,y-0.3,z-0.12,z+0.12,(40,30,24))+box(x+0.28,x+0.52,y-0.05,y-0.03,z-0.12,z+0.12,(40,30,24))
    return Q
LANTERN_Q=lantern_post()
HOUSES=[(-4.5,13.0,3.4,2.8,2.4,(84,66,60),False),(0.5,15.0,3.8,3.0,2.8,(78,70,72),True),(5.0,12.0,3.0,2.6,2.2,(70,62,66),False),(-9.0,16.0,3.4,3.0,2.6,(76,64,58),False),(9.5,17.0,3.6,3.0,2.5,(72,66,70),False)]
def house(x,z,w,d,h,col,lit):
    Q=box(x-w/2,x+w/2,0,h,z-d/2,z+d/2,col)
    rc=tuple(int(c*0.55) for c in col); Q+=[quad([(x-w/2-0.2,h,z-d/2-0.15),(x+w/2+0.2,h,z-d/2-0.15),(x+w/2+0.2,h+0.9,z),(x-w/2-0.2,h+0.9,z)],rc),quad([(x-w/2-0.2,h+0.9,z),(x+w/2+0.2,h+0.9,z),(x+w/2+0.2,h,z+d/2+0.15),(x-w/2-0.2,h,z+d/2+0.15)],rc)]
    Q+=[quad([(x-w/2,h,z-d/2-0.01),(x+w/2,h,z-d/2-0.01),(x,h+0.9,z-d/2-0.01)],col)]
    Q+=box(x-0.2,x+0.2,0,1.5,z-d/2-0.02,z-d/2,(48,36,28))
    wc=(255,196,100) if lit else (30,34,52)
    Q+=box(x+w/2-1.0,x+w/2-0.4,1.1,1.7,z-d/2-0.03,z-d/2,wc,emit=lit)
    return Q
VILLAGE=sum((house(*h) for h in HOUSES),[])
def tree(x,z,s=1.0):
    return box(x-0.18*s,x+0.18*s,0,2.2*s,z-0.18*s,z+0.18*s,(44,34,30))+box(x-1.1*s,x+1.1*s,2.0*s,3.4*s,z-1.1*s,z+1.1*s,(28,42,38))+box(x-0.7*s,x+0.7*s,3.2*s,4.2*s,z-0.7*s,z+0.7*s,(26,38,34))
TREES=tree(-6.5,9.5,1.1)+tree(7.0,8.5,1.0)+tree(-2.5,19.0,1.3)+tree(3.8,21.0,1.2)+tree(-11.0,11.0,1.2)
FENCE=sum((box(-5.8+k*0.9,-5.7+k*0.9,0,0.9,7.4,7.45,WOOD_D) for k in range(12)),[])+box(-5.8,5.0,0.55,0.62,7.4,7.45,WOOD_D)+box(-5.8,5.0,0.8,0.86,7.4,7.45,WOOD_D)
DUSK_SET=[VILLAGE,TREES,FENCE,WELL_Q,LANTERN_Q]
def season_state(t):
    """(name, weight 0..1) of the strongest season particles now"""
    for n,a,b in SEAS:
        if a<=t<b: return n,min(seg01(t,a,a+0.4),1-seg01(t,b-0.3,b))
    return None,0.0
def particles(t):
    n,w=season_state(t)
    if not n or w<=0: return []
    Q=[]; cnt=int(90*w)
    for i in range(cnt):
        x=-4.5+9*hsh(i,1); z=2.2+8*hsh(i,2); y0=3.4*hsh(i,3)
        if n=='leaves':
            y=(y0-0.6*t)%3.4; x+=0.5*math.sin(t*1.4+i); s=0.07
            Q+=box(x-s,x+s,y,y+s*0.4,z-s,z+s,(200,110+int(60*hsh(i,5)),40),emit=True)
        elif n=='snow':
            y=(y0-0.55*t)%3.4; x+=0.2*math.sin(t*1.1+i*1.7); s=0.035
            Q+=box(x-s,x+s,y,y+2*s,z-s,z+s,(236,240,255),emit=True)
        else:
            y=(y0-8.0*t)%3.4; Q+=seg((x,y,z),(x+0.06,y+0.4,z),0.012,(150,168,200),emit=True)
    return Q
def ground_key(t):
    n,w=season_state(t)
    return n if (n in ('leaves','snow','rain') and w>0.2) else 'clear'

# ======================= actors =======================
def mstate(t):
    """the old man (None never)"""
    base=MAN0 if t<T_FB[0] else MAN1; yaw=PI-0.28; d=dict(lean=0.30+0.015*math.sin(t*1.5),head=0.0,tilt=0.0,rh=None,lh=None,blink=0.0,walk=0.0,gaze=0.0,cane=True)
    ph=(t*0.5)%1.0; d['blink']=1.0 if 0.0<ph<0.04 else 0.0                                       # a slow blink every 2 s
    d['tilt']=0.04*math.sin(t*0.8)
    for tp,_,_ in HEROES:                                                                         # his eyes follow each hero, he nods a little
        if tp-0.9<t<tp+1.0: d['head']=-0.5*sm(seg01(t,tp-0.9,tp-0.1))*(1-sm(seg01(t,tp+0.3,tp+1.0))); d['gaze']=1.0
    if T0['7']-0.05<=t<T0['8']-0.05:                                                              # his hand on the rim
        u=sm(seg01(t,T0['7']-0.05,T0['7']+0.5))*(1-sm(seg01(t,T0['8']-0.5,T0['8']-0.05)))
        tgt=loc(base,yaw,(-0.7,0.88,5.95)); d['lh' if tgt[0]<0 else 'rh']=lerp3((-0.26 if tgt[0]<0 else 0.26,0.68,0.05),tgt,u); d['lean']=0.34
    if T0['9']<=t<T0['11']: d['head']=lerp(0.0,0.5,sm(seg01(t,T0['9']+0.7,T0['9']+1.3)))*(1-sm(seg01(t,T0['10']+1.9,T0['10']+2.8)))+(-0.3 if False else 0)
    kx,kz=-0.55,5.05
    if t>=T0['11']+0.8:                                                                           # turns to the knight
        yaw=lerp(yaw,math.atan2(kx-base[0],kz-base[2]),sm(seg01(t,T0['11']+0.8,T0['11']+1.7))); d['head']=0.0; d['lean']=0.26
    if T_TAKE[0]<=t<T_WALK[0]+0.4:                                                                # reaches for the ring, closes his hand
        u=sm(seg01(t,*T_TAKE)); tgt=loc(base,yaw,(-0.33,0.95,5.2)); idx='lh' if tgt[0]<0 else 'rh'
        d[idx]=lerp3((-0.26 if idx=='lh' else 0.26,0.68,0.05),tgt,u*(1-sm(seg01(t,T_TAKE[1]+0.1,T_TAKE[1]+0.9))))
        if t>=T_TAKE[1]+0.1: d[idx]=lerp3(tgt,(-0.14 if idx=='lh' else 0.14,0.95,0.2),sm(seg01(t,T_TAKE[1]+0.1,T_TAKE[1]+0.9)))
    if t>=T_WALK[0]:                                                                              # walks away, ring in his closed hand
        end=(-3.6,0.0,10.2); u=sm(seg01(t,T_WALK[0],T_WALK[1])); pos=lerp3(MAN1,end,u); dist=math.dist(MAN1,pos)
        base=pos; yaw=lerp(yaw,math.atan2(end[0]-MAN1[0],end[2]-MAN1[2]),sm(seg01(t,T_WALK[0],T_WALK[0]+0.9))); d['walk']=dist*3.0; d['lean']=0.3; d['head']=0.0
        d['lh' if False else 'rh']=(0.14,0.95,0.2) if True else None
    d.update(base=base,yaw=yaw); return d
def wstate(t):
    """the wife (flashback only)"""
    if not (T_FB[0]-0.1<=t<T_GREY[1]+0.3): return None
    base=(0.0,0.8*0,5.0); yaw=0.0; lean=0.0; head=0.0; tilt=0.0; rh=lh=None; y=0.0; z=5.05
    leanu=sm(seg01(t,T_FB[0]+0.2,T_RING-0.5))*(1-sm(seg01(t,T_RING+0.9,T_RING+1.5)))
    lean=0.5*leanu; tilt=0.35*leanu
    rim=loc((0,0,z),0.0,(0.25,0.86,5.7)); rim2=loc((0,0,z),0.0,(-0.25,0.86,5.7)); rh=lerp3((0.26,0.68,0.05),rim,leanu); lh=lerp3((-0.26,0.68,0.05),rim2,leanu)
    if t>=T_WDOWN[0]:                                                                            # she climbs onto the rim and down along the rope
        a=sm(seg01(t,T_WDOWN[0],T_WDOWN[0]+0.5)); b=sm(seg01(t,T_WDOWN[0]+0.5,T_WDOWN[1]))
        z=lerp(5.05,5.98,a); y=0.8*a-3.4*b; lean=0.0; tilt=0.0; rh=(0.12,1.45,0.22); lh=(-0.12,1.45,0.22)
    return dict(base=(0.0,y,z),yaw=0.0,kind='woman',lean=lean,head=head,tilt=tilt,rh=rh,lh=lh,blink=0.0,walk=0.0,cane=False)
KN_BASE=(-3.0,0.0,4.6)
def kstate(t):
    if t<T_K_IN: return None
    d=dict(base=KN_BASE,yaw=PI/2,walk=0.0,run=0.0,sword='hip',lean=0.02,head=0.0,rh=None,lh=None)
    if t<T_K_STOP:                                                                               # walks in along the road
        x=-3.0+2.2*(t-T_K_IN); d.update(base=(x,0,4.6),walk=x*4.0,yaw=lerp(PI/2,0.0,sm(seg01(t,T_K_STOP-0.55,T_K_STOP+0.3)))); d['base']=(x,0,lerp(4.6,4.7,seg01(t,T_K_IN,T_K_STOP)))
        return d
    x0=-3.0+2.2*(T_K_STOP-T_K_IN); d.update(base=(x0,0.0,4.7),yaw=0.0)
    d['head']=-0.8*sm(seg01(t,T_K_STOP+0.1,T_K_STOP+0.5))*(1-sm(seg01(t,T0['10']-0.1,T0['10']+0.45)))
    if t<T_K_RIM[0]: return d
    if t<T_K_UP[0]:                                                                              # steps up to the well
        u=sm(seg01(t,*T_K_RIM)); d.update(base=(lerp(x0,0.0,sm(seg01(t,T_K_RIM[0],T_K_RIM[0]+0.5))),0.0,lerp(4.7,5.42,u)),walk=t*7.0 if u<0.97 else 0.0); return d
    if t<T_K_DOWN[0]:                                                                            # onto the rim
        u=sm(seg01(t,*T_K_UP)); d.update(base=(0.0,0.8*u,lerp(5.42,5.95,u)),walk=0.0,rh=(0.1,1.35,0.25),lh=(-0.1,1.35,0.25)); return d
    if t<T_K_ASC[0]:                                                                             # down the rope (hands on it), a pause at the bottom
        u=sm(seg01(t,*T_K_DOWN)); d.update(base=(0.0,lerp(0.8,-2.7,u),lerp(5.95,6.0,u)),walk=0.0,rh=(0.1,1.4,0.24),lh=(-0.1,1.4,0.24),lean=0.0); return d
    if t<T_K_OUT[0]:                                                                             # up again
        u=sm(seg01(t,*T_K_ASC)); d.update(base=(0.0,lerp(-2.7,0.86,u),lerp(6.0,5.7,u*u*u)),walk=0.0,rh=(0.1,1.4,0.24),lh=(-0.1,1.4,0.24),lean=0.0); return d
    u=sm(seg01(t,*T_K_OUT)); yaw=lerp(0.0,math.atan2(MAN1[0]-(-0.55),MAN1[2]-5.05),u)
    d.update(base=(lerp(0.0,-0.55,u),0.86*(1-u),lerp(5.7,5.05,u)),yaw=yaw,walk=t*6.0 if u<0.95 else 0.0,lean=0.0)
    if t>=T_K_OUT[1]:
        h=sm(seg01(t,T_K_OUT[1]-0.2,T_HOLD+0.35)); d.update(rh=lerp3((0.26,0.86,0.04),(0.16,1.0,0.5),h),head=0.0)
        if t>=T_WALK[0]: d['head']=0.5*sm(seg01(t,T_WALK[0],T_WALK[0]+1.0))
    return d
def ring_pos(t):
    """world position of the ring (None = not visible)"""
    wx,wz=WELL
    if T_RING<=t<T_RING+0.7:                                                                      # falls from her hand into the well
        u=seg01(t,T_RING,T_RING+0.7); return (0.15,lerp(1.0,-4.5,u*u),5.78+0.35*u)
    if t>=T_K_OUT[0]:
        k=kstate(t);
        if k is None or k.get('rh') is None: return None
        if t<T_TAKE[0]+0.7: return tuple(np.array(k['base'])+FB.Ry(k['yaw'])@np.array([k['rh'][0],k['rh'][1]+0.07,k['rh'][2]]))
        m=mstate(t); idx='lh' if m['lh'] is not None else 'rh'
        if m[idx] is None: return None
        hp=np.array(m[idx]); b=np.array(m['base']); R=FB.Ry(m['yaw']); lean=m['lean']; hy=0.62
        p=np.array([0,hy,0])+FB.Rx(lean)@(hp-np.array([0,hy,0])); return tuple(b+R@p+np.array([0,0.04,0]))
    return None
def ring_model(t):
    p=ring_pos(t)
    if p is None: return []
    g=0.5+0.5*math.sin(t*14)
    return box(p[0]-0.03,p[0]+0.03,p[1]-0.012,p[1]+0.012,p[2]-0.03,p[2]+0.03,GOLD,emit=True)+box(p[0]-0.012,p[0]+0.012,p[1]-0.014,p[1]+0.014,p[2]-0.012,p[2]+0.012,(60,50,30),emit=True)+(box(p[0]-0.06,p[0]+0.06,p[1]+0.03,p[1]+0.036,p[2]-0.004,p[2]+0.004,(255,250,210),emit=True) if g>0.55 else [])
def rope_model(t):
    wx,wz=WELL; L=6.5
    th=0.0
    if t>=T_WDOWN[1]: th=0.07*math.exp(-(t-T_WDOWN[1])*0.35)*math.sin((t-T_WDOWN[1])*2.4)*(1-seg01(t,T0['9']-0.8,T0['9']+0.2))
    if T_K_DOWN[0]<=t: th+=0.012*math.sin(t*3.1)
    top=(wx,2.0,wz); bot=(wx+L*math.sin(th),2.0-L*math.cos(th),wz)
    Q=seg(top,bot,0.04,ROPE)+box(bot[0]-0.1,bot[0]+0.1,bot[1]-0.2,bot[1],bot[2]-0.1,bot[2]+0.1,WOOD_D)
    Q+=seg((wx+0.9,1.2,wz),(wx,2.0,wz),0.035,ROPE)                                               # the rope is tied to the post
    for k in range(4): Q+=seg((wx+0.9-0.03*k,1.2,wz),(wx+0.9+0.05*(k-1.5),1.07-0.05*k,wz+0.02*k),0.012,(176,150,108))   # frayed end
    Q+=box(wx+0.84,wx+0.96,1.14,1.26,wz-0.08,wz+0.08,(120,96,66))                                # knot
    return Q

# ======================= lights / look =======================
def in_fb(t): return T_FB[0]<=t<T_FB[1]
def grey_amt(t): return sm(seg01(t,*T_GREY))
def fb_amt(t): return sm(seg01(t,T_FB[0],T_FB[0]+0.35))*(1-sm(seg01(t,T_FB[1]-0.05,T_FB[1]+0.05)))
def lights(t):
    if in_fb(t): return [((6,8,2),(255,214,160),1.7),((-4,5,2),(255,226,190),0.9)]
    fl=1.0+0.08*math.sin(t*11)+0.05*math.sin(t*23)
    return [((LANT[0],LANT[1]-0.2,LANT[2]),(255,186,106),1.5*fl),((-1.2,2.4,3.4),(255,190,120),0.25*fl)]

# ======================= cameras =======================
def creep(t,t0,rate=0.0014): return motion.creep(t,t0,rate,FPS)
HEAD_M=(MAN0[0],1.24,MAN0[2]+0.1)
def cam_shot(t):
    if t<CUTS[1]:      # A: close on the old man's face, then a slow pull back to the well
        u=motion.glide(seg01(t,0.9,T0['3']-0.3)); tgt=lerp3((MAN0[0]-0.02,1.22,MAN0[2]+0.1),(-0.3,1.15,6.0),u); p=lerp3((MAN0[0]+0.28,1.3,MAN0[2]-1.0),(2.6,1.55,1.4),u)
        return dict(cam=motion.dolly(p,tgt,creep(t,0.0,0.0016) if u<0.01 else 1.0),tgt=tgt,fov=lerp(44,60,u))
    if t<CUTS[2]:      # B: wide, the road in front of the well; heroes pass
        tgt=(-0.4,1.15,5.6); return dict(cam=motion.dolly((2.8,1.6,0.8),tgt,creep(t,CUTS[1],0.0012)),tgt=tgt,fov=62)
    if t<CUTS[3]:      # the old man alone, the empty village and one lit window behind him
        tgt=(-0.9,1.2,6.0); return dict(cam=motion.dolly((-2.3,1.0,3.4),tgt,creep(t,CUTS[2],0.0016)),tgt=tgt,fov=50)
    if t<CUTS[4]:      # C flashback: from above the road, the wife leans over the well
        tgt=(0.0,1.0,5.7); return dict(cam=motion.dolly((2.5,2.3,3.1),tgt,creep(t,CUTS[3],0.0012)),tgt=tgt,fov=52)
    if t<CUTS[5]:      # D1: his hand on the stone rim
        tgt=(-0.95,1.05,5.9); return dict(cam=motion.dolly((-0.15,1.2,4.45),tgt,creep(t,CUTS[4],0.0018)),tgt=tgt,fov=52)
    if t<CUTS[6]:      # D2: the frayed rope, tied to the post
        tgt=(0.72,1.22,6.2); return dict(cam=motion.dolly((0.05,1.4,5.25),tgt,creep(t,CUTS[5],0.0018)),tgt=tgt,fov=36)
    if t<CUTS[7]:      # E: two-shot from the road: the knight, the old man, the well
        tgt=(-0.35,1.05,5.5); return dict(cam=motion.dolly((2.5,1.45,2.7),tgt,creep(t,CUTS[6],0.0012)),tgt=tgt,fov=56)
    if t<CUTS[8]:      # the dark well from above
        tgt=(0.0,-0.9,6.1); return dict(cam=motion.dolly((0.1,3.3,5.4),tgt,creep(t,CUTS[7],0.0010)),tgt=tgt,fov=52)
    if t<CUTS[9]:      # low at the rim: he comes back up
        tgt=(-0.05,1.1,5.95); return dict(cam=motion.dolly((1.5,1.0,3.6),tgt,creep(t,CUTS[8],0.0012)),tgt=tgt,fov=54)
    if t<CUTS[10]:     # the ring on the open gauntlet
        tgt=(-0.82,1.02,5.5); return dict(cam=motion.dolly((-1.45,1.15,4.55),tgt,creep(t,CUTS[9],0.0016)),tgt=tgt,fov=38)
    if t<CUTS[11]:     # the old man's face: ...THANK YOU.
        tgt=(MAN1[0]+0.1,1.22,MAN1[2]+0.05); return dict(cam=motion.dolly((MAN1[0]-1.0,1.32,MAN1[2]-0.85),tgt,creep(t,CUTS[10],0.0018)),tgt=tgt,fov=44)
    tgt=(-2.2,1.1,8.5)                                                                           # last: he walks away from the well, the knight stays
    return dict(cam=motion.dolly((-0.3,1.4,2.8),tgt,creep(t,CUTS[11],0.0012)),tgt=tgt,fov=54)

# ======================= render =======================
RND=Renderer(W,H,fog=(30,30,54)); RNF=Renderer(W,H,fog=(126,98,82))
VI=[None]
def render3d(t):
    sh=cam_shot(t); cam=Camera.look(sh['cam'],sh['tgt']); fb=in_fb(t); A=[]; cp=sh['cam']
    lum=0.78 if not fb else 1.0; tint=(1,1,1) if not fb else (1.15,1.0,0.8)
    gk=ground_key(t) if not fb else 'clear'
    layers=[GROUND[gk]]+DUSK_SET+[rope_model(t)]
    for i in range(len(HEROES)):
        st=hero_state(i,t)
        if st is not None: layers.append(lum_lit(hero_knight(HEROES[i][1],**st),cp,lum,0.2))
    ks=kstate(t)
    if ks is not None:
        dep=max(0.0,min(1.0,-ks['base'][1]/2.6)); layers.append(lum_lit(FB.knight(**ks),cp,lerp(lum,0.5,dep),0.2,tint))
    if not fb: layers.append(lum_lit(human(**mstate(t)),cp,lum,0.2,tint))
    ws_=wstate(t)
    if ws_ is not None: layers.append(lum_lit(human(**ws_),cp,1.05,0.1,tint))
    layers+=[ring_model(t),particles(t)]
    R=RNF if fb else RND
    img,vi,zb=zrender(R,cam,layers,lights(t),fov=sh['fov'],fog_start=7,fog_end=30,ambient=0.7 if fb else 0.2,return_z=True)
    VI[0]=vi; return post.ps1(img),vi

# ======================= HUD / UI =======================
def otext(d,s,x,y,col,sc=1):
    o=max(1,sc//2)
    for ox,oy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)): font.text(d,s,x+ox*o,y+oy*o,(0,0,0),sc,None)
    font.text(d,s,x,y,col,sc,None)
def dialogue(d,t):
    """classic RPG box (one UI element at a time): the NPC's line typed out"""
    for tb,txt in BOXES:
        if tb<=t<tb+BOX_LEN:
            x0,y0,x1,y1=8,186,W-9,226
            d.rectangle([x0,y0,x1,y1],fill=(12,14,38),outline=(236,234,226)); d.rectangle([x0+2,y0+2,x1-2,y1-2],outline=(70,82,150))
            n=int(len(txt)*min(1.0,(t-tb)/0.9)); sc=1; s=txt[:n]; cut=txt.rfind(' ',0,18) if len(txt)*6>W-26 else -1
            if cut>0:
                font.text(d,s[:cut],x0+9,y0+11,WHT,sc,(0,0,0))
                if n>cut+1: font.text(d,s[cut+1:],x0+9,y0+23,WHT,sc,(0,0,0))
            else: font.text(d,s,x0+9,y0+16,WHT,sc,(0,0,0))
            if n>=len(txt) and int(t*3)%2==0: d.polygon([(x1-12,y1-9),(x1-6,y1-9),(x1-9,y1-5)],fill=WHT)
            return
def hud(d,t): dialogue(d,t)
def frame_low(t):
    img,vi=render3d(t); a=np.asarray(img).astype(np.float32)
    if in_fb(t):
        g=grey_amt(t); lumg=(a*np.array([0.3,0.59,0.11])).sum(2,keepdims=True)
        a=a*(1-g)+(lumg*np.array([0.82,0.82,0.86]))*g; a=a*lerp(1.0,0.72,g)
        fa=1-fb_amt(t)
        if fa>0: a=a*(1-fa*0.0)
    return Image.fromarray(np.clip(a,0,255).astype(np.uint8))
def flash_pass(t,img):
    """soft warm flash into / out of the flashback"""
    fa=0.0
    if T_FB[0]-0.05<=t<T_FB[0]+0.25: fa=0.55*(1-seg01(t,T_FB[0]-0.05,T_FB[0]+0.25))
    if fa<=0: return img
    return Image.fromarray(np.clip(np.asarray(img).astype(np.float32)*(1-fa)+np.array([255,230,190])*fa,0,255).astype(np.uint8))
def finish(t):
    img=flash_pass(t,frame_low(t)); d=ImageDraw.Draw(img); hud(d,t)
    end=seg01(t,DUR-0.5,DUR)
    if end>0: img=Image.fromarray((np.asarray(img).astype(np.float32)*(1-0.55*end)).astype(np.uint8))
    return img

# ======================= subtitles (1080x1920, 1.25x, sentence timings from the voice) =======================
SUB_F=7.0; ADV=6.9; HIL={'FORTY','YEARS.','RING','CLIMBED.','NEW.','QUIETER.','CHESTS?','LINE?','BITE?','YEARS?'}
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
            res.append((t0+a-0.03,t0+nxt-0.02,_rows(tx,14 if k=='1' else 17),k))
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
            x0=(W*S-w)/2; y0=(H*S*0.34-h/2) if card else (H*S-130-h)
            ov=Image.new('RGB',(W*S,H*S),(0,0,0)); m=Image.new('L',(W*S,H*S),0); do=ImageDraw.Draw(ov); dm=ImageDraw.Draw(m)
            if not card: dm.rectangle([round(x0),round(y0),round(x0+w)-1,round(y0+h)-1],fill=255)
            o=max(2,round(sc*0.55)); cells=[]
            for i,r in enumerate(rows):
                lw=_tw(' '.join(r),sc)-(ADV-6)*sc; x=x0+(w-lw)/2
                for wd in r:
                    col=YEL if wd.upper().strip(',!?:') in HIL or wd.upper() in HIL else WHT; font.check(wd)
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
def frame_final(t):
    arr=post.upscale(finish(t),S); so=sub_overlay(t)
    if so: m=np.asarray(so[1])>0; arr[m]=np.asarray(so[0])[m].astype(np.float32)
    return arr
def frame(t):
    img=finish(t); so=sub_overlay(t)
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
    if V[:,1].min()<-0.05 and not (name in ('knight','wife') and abs(V[:,0]).max()<0.7): out.append(('floor',f'{name} under the floor'))
    return out
def _kn(t): return kstate(t)
def _man(t): return None if in_fb(t) else mstate(t)
def _wife(t): return wstate(t)
QA=dict(fps=FPS,dur=DUR,W=W,frame=frame,
    chars={'knight':(_kn,FB.knight,'sword','hip'),'oldman':(_man,human,'none','none'),'wife':(_wife,human,'none','none')},
    geom=_geom,camera=lambda t: cam_shot(t)['cam'],min_cam_dist=0.35,camera_ok=lambda p: -13<p[0]<13 and -4<p[2]<30 and (0.1<p[1]<4.0 or (p[1]>2.0)),
    allow_jump=[(w,f/FPS) for w in ('knight','oldman','wife') for c in CUTS+[T_FB[0],T_FB[1]] for f in range(int(c*FPS)-2,int(c*FPS)+4)],
    weapon_events=[],
    scenes=[dict(id=f's{i}',t0=CUTS[i],t1=CUTS[i+1],action=a) for i,a in enumerate((
        'hook: close on the old man, dialogue box, pull back, a hero walks past (CAM A)',
        'three heroes pass: leaves, snow, rain (CAM B)',
        'the old man alone, the empty village, one lit window',
        'flashback: his wife drops her ring and climbs down (CAM C)',
        'his hand on the rim, the same line (D1)',
        'the frayed rope tied to the post (D2)',
        'a knight stops, looks at the old man, then the rope (E)',
        'he climbs down into the dark well (top view)',
        'he climbs out at the rim (low)',
        'he holds out the ring (close)',
        'the old man says: THANK YOU (close)',
        'the old man walks away, the knight stays (wide)'))],
    texts=lambda: [('hud','THE WELL IS DRY, TRAVELER.',1),('hud','...THANK YOU.',1)])

# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=41); sr=s.sr; n=s.n; t=s.t; BED=np.zeros(n); FX=np.zeros(n); PAD=np.zeros(n)
    def put(buf,x,t0,v=1.0):
        i=int(t0*sr)
        if i>=n or i<0: return
        j=min(n,i+len(x)); buf[i:j]+=(x*v)[:j-i]
    def nb(t0,d,lo,hi,v,seed,shape=2,buf=None): put(FX if buf is None else buf,s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v)
    def tone(t0,m,d,v,wave='sq',duty=0.5,dec=3.0,att=0.005,glide=0.0,buf=None):
        f=440*2**((m-69)/12); tt=s.T(d); fr=f*(1+glide*tt/d); ph=np.cumsum(fr)/sr%1
        x=np.where(ph<duty,1.0,-1.0) if wave=='sq' else (4*np.abs(ph-0.5)-1 if wave=='tri' else np.sin(2*np.pi*ph))
        put(FX if buf is None else buf,x*np.minimum(1,tt/att)*np.exp(-tt*dec),t0,v)
    def step(t0,v=0.03,seed=0):
        tt=s.T(0.12); put(FX,s.filt_short(s.noise(0.12,seed),lo=200,hi=1800)*np.exp(-tt*38)+np.sin(2*np.pi*90*tt)*np.exp(-tt*30)*0.25,t0,v)
    def creak(t0,d=0.9,v=0.05,seed=0,f0=210):
        tt=s.T(d); f=f0*(1+0.25*np.sin(2*np.pi*(2.1+0.6*hsh(seed))*tt))+40*tt/d; ph=np.cumsum(f)/sr; x=np.sin(2*np.pi*ph)*0.5+0.3*np.sin(4*np.pi*ph)+0.25*s.filt_short(s.noise(d,seed),lo=300,hi=1400)
        put(FX,x*np.sin(np.pi*tt/d)**1.5,t0,v)
    def echo(buf_from,t0,d,v,taps=((0.16,0.5),(0.33,0.3),(0.52,0.18))):
        i=int(t0*sr); j=min(n,i+int(d*sr)); seg_=FX[i:j].copy()
        for dl,g in taps: k=i+int(dl*sr); e=min(n,k+len(seg_)); FX[k:e]+=seg_[:e-k]*g*v
    # ---- bed: dusk wind (slow swell, low-passed), crickets in groups, soft far lantern hum (never a per-sample gate)
    sw=0.6+0.4*np.sin(2*np.pi*t/9.0+0.7)+0.15*np.sin(2*np.pi*t/3.7)
    BED+=s.filt(s.rng.normal(0,1,n),lo=80,hi=700)*0.07*np.clip(sw,0.2,None)
    BED+=s.filt(s.rng.normal(0,1,n),lo=500,hi=2200)*0.012*np.clip(0.4+0.6*np.sin(2*np.pi*t/5.3),0,None)
    ck=np.zeros(n); tc=0.4
    while tc<DUR-0.4:                                                                       # three-chirp groups of a soft cricket (smooth bursts)
        for k in range(3):
            d=0.045; tt=s.T(d); put(ck,np.sin(2*np.pi*(4300+80*k)*tt)*np.sin(np.pi*tt/d)**2,tc+k*0.085,1.0)
        tc+=1.1+0.7*hsh(int(tc*10))
    BED+=ck*0.011
    # ---- seasons: leaves rustle, snow hush, rain hiss
    for nme,a,b in SEAS:
        m=np.clip(np.minimum(t-a,b-t)/0.35,0,1)*((t>=a)&(t<b))
        if nme=='leaves': BED+=s.filt(s.rng.normal(0,1,n),lo=1500,hi=6000)*0.010*m*np.clip(0.5+0.5*np.sin(2*np.pi*t*0.9),0,None)
        elif nme=='snow': BED+=s.filt(s.rng.normal(0,1,n),lo=300,hi=1500)*0.012*m
        else: BED+=s.filt(s.rng.normal(0,1,n),lo=2500,hi=9000)*0.018*m
    # ---- dialogue box: a dull blip per typed letter (soft), box open/close
    for tb,txt in BOXES:
        for k in range(len(txt)):
            if txt[k]!=' ' and k*0.9/len(txt)<0.9: tone(tb+k*0.9/len(txt),72 if k%2 else 69,0.03,0.012,'sq',duty=0.4,dec=60)
        tone(tb+BOX_LEN-0.05,60,0.08,0.012,'sin',dec=30)
    # ---- heroes pass: soft footsteps
    for tp,_,_ in HEROES:
        t_a=tp-1.4/HERO_V*0.0-4.6/HERO_V; k=0
        while t_a+k*0.27<tp+6.6/HERO_V and t_a+k*0.27<DUR: step(t_a+k*0.27,0.022,100+k+int(tp*3)); k+=1
    # ---- flashback: warmer air (a soft low sweep), the ring: tink, falling, a distant tink
    nb(T_FB[0]-0.05,0.5,200,1800,0.04,201,1); tone(T_RING,102,0.5,0.03,'sin',dec=7); tone(T_RING+0.62,98,0.9,0.014,'sin',dec=5)
    creak(T_WDOWN[0],1.4,0.05,seed=7)
    for k in range(4): nb(T_WDOWN[0]+0.2+k*0.35,0.18,300,1500,0.02,210+k)
    # ---- the knight: arrival steps, rope creak, climbing, the stone scrape, echo from the well
    for k in range(int((T_K_STOP-T_K_IN)/0.3)): step(T_K_IN+0.15+k*0.3,0.03,300+k)
    for k in range(3): step(T_K_RIM[0]+0.1+k*0.3,0.03,320+k)
    nb(T0['9']+1.4,0.5,300,1600,0.05,331,1); creak(T0['9']+1.45,0.55,0.05,seed=13,f0=190)       # his head turns to the old man: armour + a creak of the rope (no silent gap)
    creak(T0['10']+0.8,0.8,0.06,seed=11); nb(T_K_UP[0]+0.1,0.35,300,1500,0.03,330)
    k=0
    while T_K_DOWN[0]+k*0.5<T_K_ASC[1]:
        a=T_K_DOWN[0]+k*0.5
        if not (T_K_DOWN[1]<a<T_K_ASC[0]-0.2): creak(a,0.7,0.045,seed=20+k,f0=190+10*(k%3)); nb(a+0.1,0.2,250,1600,0.018,340+k)
        k+=1
    echo(None,T_K_DOWN[0],T_K_ASC[1]-T_K_DOWN[0],0.55)
    nb(T_K_ASC[1]-0.3,0.4,300,1600,0.04,360);
    for k in range(3): step(T_K_OUT[0]+0.1+k*0.28,0.03,370+k)
    # ---- the ring: one soft chime when he holds it out; the old man's closing hand
    for k_,m in enumerate((88,95)): tone(T_HOLD+0.15+k_*0.18,m,1.4,0.03,'sin',dec=2.5)
    nb(T_TAKE[1]+0.05,0.2,200,1200,0.02,380)
    # ---- the old man walks away: slow shuffle + cane taps
    k=0
    while T_WALK[0]+0.3+k*0.7<DUR-0.9: step(T_WALK[0]+0.3+k*0.7,0.018,400+k); tone(T_WALK[0]+0.45+k*0.7,52,0.08,0.012,'sin',dec=40); k+=1
    # ---- a low two-note pad under the last line (D2 + A2)
    a0=T0['13']-0.2; m=np.clip(np.minimum(t-a0,DUR-t)/1.6,0,1)*(t>=a0)
    PAD+=(np.sin(2*np.pi*73.4*t)+0.55*np.sin(2*np.pi*110.0*t+0.4))*0.05*m
    # ---- voice
    NB=np.zeros(n); wins=[]
    for k_,t0 in LINES:
        a,ar=_sf.read(os.path.join(TTS_DIR,'nw',f'{k_}.wav')); a=a if a.ndim==1 else a.mean(1)
        a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a); put(NB,a,t0); wins.append((t0,t0+len(a)/sr))
    g=duck_envelope(n,sr,wins,-6.0,0.05,0.25); bed=BED*g+PAD; fx=FX*(0.55+0.45*g)
    L=bed+fx; R_=np.roll(bed,700)+np.roll(fx,200); pk=max(np.abs(L).max(),np.abs(R_).max()); gv=pk*1.6/np.abs(NB).max()
    s.L=L+NB*gv; s.R=R_+NB*gv; s.reverb(0.16,length=1.6,decay=3.0)
    end=np.clip((DUR-t)/0.6,0,1); s.L*=end; s.R*=end
    return s.save(path,peak=0.9)
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'npc_well.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'nw_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.96,vignette=0.3,grain=1.5,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(frame_final(f/FPS),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
