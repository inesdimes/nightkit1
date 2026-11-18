"""WHY DO LIGHTHOUSES BLINK?  PS1 maritime survival short, 9:16, exactly 60 s (1440 frames @ 24 fps). Fully procedural (nightkit).
LOCKED ASSETS: captain() (blocky, navy raincoat, dark square cap, brown boots, rigid segmented arms; ONLY animated character), boat() (low-poly wooden fishing boat, console, ONE steering wheel at a fixed place),
rocks() (angular pyramids, ALWAYS on the left), sea(), lighthouses() (A = headland, LEFT, near, bright, ONE flash per cycle; B = harbor, RIGHT, far, softer, TWO flashes per cycle), harbor markers,
chart_overlay() (2D). Fog = zrender fog distance (thins briefly to reveal the rocks, which were in the scene all along) + 2D noise; light glows = 2D sprites anchored to world coordinates;
all text / HUD / chart are 2D overlays after the 3D render.
Axes: +x = right of the screen, boat travels towards +z. The boat path is INTEGRATED from keyframed heading and speed (no teleporting). Flash timing is deterministic (see FLASH below).
Cameras: A forward boat view (mounted on the boat), B helm detail (front-left of the captain), C external coastal view (fixed in the world). Hard cuts only.
Voice: python tools/tts/lh.py -> $TTS_DIR/lh/*.wav (one file per sentence; cues are placed from the MEASURED lengths).
Run: TEST=0.1,8 python examples/lighthouse.py -> test.png | PART=a:b | PART=audio      QA: python tools/qa/scene_qa.py examples/lighthouse.py"""
import os, sys, math, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
import numpy as np
from PIL import Image, ImageDraw
_T=os.environ.pop('TEST',None)
import mirror_copy as mc                              # reuse: subtitle chunker / drawer, ui_box, HIL, face_track helpers
if _T is not None: os.environ['TEST']=_T
from nightkit.engine import Renderer, Camera, box, quad, transform, tiled_plane
from nightkit import post, font
from nightkit.zraster import zrender
from nightkit.audio import Sound
FT=mc.FT; sm,seg01,seg,tag,Rx,Ry,Rz=FT.sm,FT.seg01,FT.seg,FT.tag,FT.Rx,FT.Ry,FT.Rz
PI=math.pi; lerp=mc.lerp; env=mc.env
TTS_DIR=mc.TTS_DIR; OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6; DUR=60.0; N=int(round(DUR*FPS)); N_OUT=N
try: SCR=json.load(open(os.path.join(TTS_DIR,'lh','script.json')))
except Exception: SCR=None

# ======================= narration schedule (MEASURED sentence lengths) =======================
ORDER=['1a','1b','2a','2b','3a','3b','4a','4b','5a','5b','6a','6b','7a','7b','7c','8a','8b','8c','8d','9a','10a','10b']
TEXT={'1a':"Why do lighthouses blink?",'1b':"One wrong choice almost sent this captain straight into the rocks.",'2a':"Lost in thick fog, he spotted two lights.",'2b':"He followed the brighter, closer one.",
      '3a':"But the fog suddenly cleared.",'3b':"A wall of jagged rocks filled his entire path.",'4a':"He spun the wheel.",'4b':"The boat was still drifting, and the rocks were getting closer.",
      '5a':"Then he remembered his chart.",'5b':"The lights looked similar, but their blinking patterns were different.",'6a':"On his chart, one flash marked the dangerous headland.",
      '6b':"Two flashes marked the harbor on the right.",'7a':"He counted the nearer light's flashes.",'7b':"Just one.",'7c':"He'd been following the wrong lighthouse.",
      '8a':"Through the fog, the other light flickered.",'8b':"Once.",'8c':"Twice.",'8d':"There was still a chance.",
      '9a':"He steered onto the harbor approach marked on his chart, barely slipping past the rocks.",'10a':"Those flashes weren't decoration.",'10b':"They told him which lighthouse he was seeing."}
DURS={k:(SCR['dur'][k] if SCR else 2.0) for k in ORDER}
GAP=(DUR-0.2-sum(DURS.values()))/(len(ORDER)-1)            # equal pauses (< 0.5 s): narration runs through the whole minute
ST={}; _t=0.05
for k in ORDER: ST[k]=_t; _t+=DURS[k]+GAP
def s(k,o=0.0): return ST[k]+o
mc.ORDER,mc.ST,mc.DURS=ORDER,ST,DURS; mc.TEXT.update(TEXT); mc.HIL|={'LIGHTHOUSES','LIGHTHOUSES?','ROCKS','ROCKS.','CHART','CHART.','FLASH','FLASHES','FLASHES.','ONE','TWO','WRONG','LIGHTHOUSE.','LIGHTHOUSE'}
SUBS=mc.sub_chunks(); mc.SUBS=SUBS
_first={}
for k in ORDER: _first.setdefault(int(''.join(c for c in k if c.isdigit())),k)
CUTS=[0.0]+[round((ST[_first[i]]-GAP/2)*FPS)/FPS for i in range(2,11)]+[DUR]          # shot i = CUTS[i-1] .. CUTS[i]
def shot_of(t):
    for i in range(1,11):
        if t<CUTS[i]: return i
    return 10
CAMS={1:'A',2:'A',3:'C',4:'B',5:'B',6:'B',7:'A',8:'A',9:'C',10:'A'}
def cam_id(t): return CAMS[shot_of(t)]

# ======================= FLASH (deterministic; the same pattern whenever a light is visible) =======================
FA_LEN=0.40; FB_LEN=0.32
_tA=s('7b',0.1); _nA=max(1,round((_tA-0.8)/4.0)); PA=(_tA-0.8)/_nA; TA0=_tA                  # LIGHT A: one flash per cycle (period ~4 s), in sync with "Just one."; also flashes at ~0.8 s in frame 0
_tB=s('8b',0.08); DB=s('8c')-s('8b'); _t10=s('10a',0.9); PB=(_t10-_tB)/2; TB0=_tB                 # LIGHT B: two flashes per cycle (DB apart, period ~5.6 s), in sync with "Once. Twice." and again in the last shot
def _pulse(t,t0,period,ln): u=(t-t0)%period; return float(min(1.0,u/0.04)*min(1.0,(ln-u)/0.06)) if 0<=u<ln else 0.0
def flash_a(t): return _pulse(t,TA0,PA,FA_LEN)
def flash_b(t): return max(_pulse(t,TB0,PB,FB_LEN),_pulse(t,TB0+DB,PB,FB_LEN))
def flash_times_a(): return [TA0+PA*k for k in range(-20,20) if 0<=TA0+PA*k<DUR]
def flash_times_b(): return sorted([TB0+PB*k+o for k in range(-20,20) for o in (0,DB) if 0<=TB0+PB*k+o<DUR])

# ======================= palette =======================
COAT=(46,82,150); COAT_D=(34,62,120); CAP=(26,30,52); BOOT=(120,72,38); SKIN=(214,170,138); BLK=(14,12,20); PANTS=(36,52,96)
HULL=(128,84,48); HULL_D=(92,58,32); DECK=(158,112,66); CONS=(104,72,46); WHEEL=(150,100,52); WHEEL_D=(110,72,38)
ROCK=[(6,6,12),(3,3,9),(9,9,16),(5,5,11)]; SEA=[(26,42,68),(32,50,76)]; FOGC=(58,72,100)
LIGHT_A=(255,240,205); LIGHT_B=(225,236,255)

# ======================= LOCKED ASSET: the boat path (integrated from heading + speed) =======================
YAW_K=[(0,0.02),(6,0.0),(8.0,-0.02),(9.6,-0.20),(12,-0.22),(17.9,-0.22),(20,-0.12),(23,0.02),(27,0.12),(36,0.12),(49,0.12),(50.5,0.40),(52,0.78),(54,0.80),(56,0.55),(58,0.42),(60,0.40)]
SPD_K=[(0,2.8),(17.9,2.8),(21,0.6),(24,0.25),(27,-0.10),(49,-0.10),(50.4,1.2),(52,3.0),(54,3.6),(56,3.4),(60,3.2)]
from scipy.interpolate import PchipInterpolator
_yaw=PchipInterpolator([k[0] for k in YAW_K],[k[1] for k in YAW_K]); _spd=PchipInterpolator([k[0] for k in SPD_K],[k[1] for k in SPD_K])
_DT=1/240.; _TS=np.arange(0,DUR+1,_DT); _X=np.zeros(len(_TS)); _Z=np.zeros(len(_TS)); _X[0]=1.4; _Z[0]=0.0
for _i in range(1,len(_TS)):
    _y=float(_yaw(_TS[_i-1])); _v=float(_spd(_TS[_i-1])); _X[_i]=_X[_i-1]+_v*math.sin(_y)*_DT; _Z[_i]=_Z[_i-1]+_v*math.cos(_y)*_DT
def boat_xz(t): return float(np.interp(t,_TS,_X)),float(np.interp(t,_TS,_Z))
def boat_yaw(t): return float(_yaw(min(max(t,0),DUR)))
def boat_speed(t): return float(_spd(min(max(t,0),DUR)))

# ======================= LOCKED ASSET: the rocks (always on the LEFT) =======================
def _tri(a,b,c,col): return quad([a,b,c],col)
def spike(cx,cz,hw,hd,h,ax,az,col):
    """angular pyramid: base rectangle on the sea, apex offset (ax,az); faces wound outward"""
    c=[(cx-hw,0,cz-hd),(cx+hw,0,cz-hd),(cx+hw,0,cz+hd),(cx-hw,0,cz+hd)]; ap=(cx+ax,h,cz+az); Q=[]; ctr=np.array([cx,h*0.3,cz])
    for i in range(4):
        q=_tri(c[i],c[(i+1)%4],ap,col)
        if np.dot(q['n'],q['c']-ctr)<0: q=_tri(c[(i+1)%4],c[i],ap,col)
        Q.append(q)
    return Q
ROCKS=[]                                             # (cx,cz,hw,hd,h,ax,az)
ROCKS+=[(-2.3,9.0,1.7,1.5,8.5,1.3,-0.4),(-3.4,17.0,1.7,1.5,7.0,0.6,0.2),(-2.6,25.0,1.6,1.5,7.5,0.8,0.0),(-4.5,32.0,1.8,1.6,8.0,0.5,0.0)]      # reef chain along the left: danger from frame 0                             # foreground silhouette in frame 0 + a second one
_rng=np.random.default_rng(23)
for cx in np.arange(-34,-6,3.6):                    # the wall
    for cz in (66.0,71.0,77.0):
        ROCKS.append((cx+_rng.uniform(-0.8,0.8),cz+_rng.uniform(-1.2,1.2),_rng.uniform(3.0,4.2),_rng.uniform(2.6,3.4),_rng.uniform(8,15),_rng.uniform(-1.6,1.6),_rng.uniform(-1.2,1.2)))
ROCKS+=[(-17.0,56.0,2.4,2.0,8.0,0.3,0.2),(-12.0,60.0,2.2,1.8,7.0,-0.2,0.3),(-9.5,64.5,2.2,1.9,11.0,0.3,0.0)]
SPUR=(-3.6,63.0,1.5,2.1,9.5,-0.4,0.3)                # the final rock the boat slips past
ROCKS.append(SPUR)
def rocks():
    Q=[]
    for i,(cx,cz,hw,hd,h,ax,az) in enumerate(ROCKS):
        Q+=spike(cx,cz,hw,hd,h,ax,az,ROCK[i%4])
        sg=1 if i%2 else -1; Q+=spike(cx+sg*hw*0.5,cz-hd*0.15,hw*0.5,hd*0.55,h*0.62,-sg*0.3,0.2,ROCK[(i+1)%4])          # a second, smaller spike makes the silhouette jagged
    return Q
ROCK_Q=rocks()
def rock_clearance(x,z):
    """horizontal distance from a point to the nearest rock base footprint (m)"""
    d=1e9
    for cx,cz,hw,hd,h,ax,az in ROCKS:
        dx=max(abs(x-cx)-hw,0); dz=max(abs(z-cz)-hd,0); d=min(d,math.hypot(dx,dz))
    return d

# ======================= LOCKED ASSET: sea, lighthouses, harbor markers =======================
def sea():
    return tiled_plane(-90,90,-20,230,0.0,10.0,lambda i,j:SEA[(i+j)%2])
LA=(-13.0,100.0); LB=(26.0,150.0); LA_Y=24.0; LB_Y=14.0                          # lantern positions (x,z), heights
def lighthouse(x,z,hgt,base_h,col,wide):
    Q=box(x-wide*2,x+wide*2,0,base_h,z-wide*2,z+wide*2,(18,18,28))                                  # rocky foot
    Q+=box(x-wide,x+wide,base_h,hgt-2.6,z-wide,z+wide,col)+box(x-wide*0.75,x+wide*0.75,hgt-2.6,hgt-1.2,z-wide*0.75,z+wide*0.75,(60,60,80))
    return Q
def lantern_box(x,z,hgt,on,col):
    return box(x-0.9,x+0.9,hgt-1.2,hgt,z-0.9,z+0.9,col if on else (70,66,56),emit=True)+box(x-1.1,x+1.1,hgt,hgt+0.5,z-1.1,z+1.1,(28,28,40))
MARK_L=(13.0,112.0); MARK_R=(22.0,112.0)
def markers():
    Q=[]
    for (x,z),c in ((MARK_L,(200,50,50)),(MARK_R,(50,190,90))): Q+=box(x-0.3,x+0.3,0,2.6,z-0.3,z+0.3,(40,40,52))+box(x-0.45,x+0.45,2.6,3.2,z-0.45,z+0.45,c,emit=True)
    Q+=box(8,16,0,1.2,106,116,(14,14,22))+box(19,40,0,1.5,106,125,(14,14,22))                         # low shore on either side of the entrance
    return Q
def tall_a(): return lighthouse(LA[0],LA[1],LA_Y,3.2,(190,190,200),1.3)
def tall_b(): return lighthouse(LB[0],LB[1],LB_Y,2.2,(150,150,170),1.1)
SEA_Q=sea(); LH_A=tall_a(); LH_B=tall_b(); MARK_Q=markers()

# ======================= LOCKED ASSET: boat + captain =======================
DECK_Y=0.5; CAPT_Z=-0.55; WHEEL_C=(0.0,1.30,0.10); WHEEL_R=0.27
def _outward(q,c):
    if np.dot(q['n'],q['c']-c)<0: q['p']=q['p'][::-1]; q=quad(q['p'],q['col'],q.get('emit',False))
    return q
def boat_local():
    """fishing boat in boat-local coordinates (origin at the waterline centre, bow +z); returns quads. Wheel is added separately (it turns)."""
    Q=box(-1.1,1.1,-0.35,DECK_Y,-2.6,1.4,HULL)+box(-1.1,1.1,DECK_Y-0.02,DECK_Y,-2.6,1.4,DECK)
    for i in range(0,11):                                                                   # deck planks (alternating tone)
        z0=-2.6+i*0.4; Q+=box(-1.08,1.08,DECK_Y,DECK_Y+0.012,z0,min(z0+0.4,1.4),DECK if i%2==0 else (146,102,60))
    Q+=box(-1.18,-1.1,DECK_Y-0.35,DECK_Y+0.38,-2.6,1.4,HULL_D)+box(1.1,1.18,DECK_Y-0.35,DECK_Y+0.38,-2.6,1.4,HULL_D)+box(-1.18,1.18,DECK_Y-0.35,DECK_Y+0.38,-2.66,-2.6,HULL_D)   # gunwales + transom
    # triangular bow: top triangle + two slanted side faces
    ctr=np.array([0,0.1,1.9]); tip=(0,DECK_Y,3.3)
    for p in (([(-1.1,DECK_Y+0.012,1.4),(0,DECK_Y+0.012,3.3),(1.1,DECK_Y+0.012,1.4)],DECK),
              ([(-1.1,-0.35,1.4),(-1.1,DECK_Y+0.38,1.4),(0,DECK_Y+0.38,3.3),(0,-0.35,3.3)],HULL_D),([(1.1,-0.35,1.4),(0,-0.35,3.3),(0,DECK_Y+0.38,3.3),(1.1,DECK_Y+0.38,1.4)],HULL_D),
              ([(-1.1,DECK_Y+0.38,1.4),(-1.1,DECK_Y+0.4,1.4),(0,DECK_Y+0.4,3.3),(0,DECK_Y+0.38,3.3)],HULL),([(1.1,DECK_Y+0.38,1.4),(0,DECK_Y+0.38,3.3),(0,DECK_Y+0.4,3.3),(1.1,DECK_Y+0.4,1.4)],HULL)):
        Q.append(_outward(quad(p[0],p[1]),ctr))
    Q+=box(-0.55,0.55,DECK_Y,1.05,0.20,0.85,CONS)+box(-0.5,0.5,1.05,1.10,0.18,0.87,(80,54,34))                    # console + top
    Q+=box(-0.09,0.09,1.10,1.40,0.20,0.34,WHEEL_D)                                                    # wheel column
    Q+=box(0.80,0.92,DECK_Y,DECK_Y+0.7,-2.4,-2.28,(70,60,50))+box(0.76,0.96,DECK_Y+0.7,DECK_Y+0.86,-2.44,-2.24,(255,200,110),emit=True)      # stern lamp (keeps the boat findable in the wide shots)
    return Q
def wheel(ang):
    """the steering wheel: octagonal rim + 8 spokes + hub, turns by ang (+ = clockwise from the captain = turn RIGHT)"""
    c=np.array(WHEEL_C); Q=[]
    for k in range(8):
        a0=ang+k*PI/4; a1=a0+PI/4; p0=c+np.array([WHEEL_R*math.cos(a0),WHEEL_R*math.sin(a0),0]); p1=c+np.array([WHEEL_R*math.cos(a1),WHEEL_R*math.sin(a1),0])
        Q+=seg(tuple(p0),tuple(p1),0.05,WHEEL,0.05)+seg(tuple(c),tuple(p0),0.035,WHEEL_D,0.035)
    Q+=box(-0.06,0.06,WHEEL_C[1]-0.06,WHEEL_C[1]+0.06,WHEEL_C[2]-0.06,WHEEL_C[2]+0.06,WHEEL_D)
    return Q
IDLE=dict(wheel=0.0,hyaw=0.0,hp=0.0,lean=0.0,fear=0.0,relief=0.0,eyes=1.0)
def captain_local(p):
    """blocky captain in boat-local coords, facing +z, standing on the deck at CAPT_Z. Poses: wheel angle (hands follow the rim), head yaw/pitch, lean, fear (wide eyes), relief (slumped shoulders)"""
    oy=DECK_Y+0.012; lean=p['lean']-0.10*p['relief']; sl=-0.07*p['relief']
    def B(q): q=np.array(q,float); y=q[1]+(0 if q[1]<0.5 else 0); return (q[0],q[1]+oy,q[2]+CAPT_Z+lean*max(0,q[1]-0.5))
    Q=[]; D=[]
    for sx in (-1,1): Q+=box(sx*0.11-0.075,sx*0.11+0.075,0.0,0.15,-0.11,0.2,BOOT,xf=B)+box(sx*0.11-0.065,sx*0.11+0.065,0.15,0.50,-0.08,0.09,PANTS,xf=B)
    Q+=box(-0.29,0.29,0.40,0.56,-0.17,0.17,COAT_D,xf=B)+box(-0.27,0.27,0.56,1.12+sl,-0.145,0.145,COAT,xf=B)
    Hc=np.array([0,1.12+sl,0]); Rh=Ry(p['hyaw'])@Rx(p['hp'])
    def Hd(q): q=np.array(q,float); return B(Hc+Rh@(q-Hc)+np.array([0,0,0]))
    Q+=box(-0.15,0.15,1.12+sl,1.40+sl,-0.15,0.15,SKIN,xf=Hd)+box(-0.18,0.18,1.32+sl,1.45+sl,-0.18,0.18,CAP,xf=Hd)+box(-0.14,0.14,1.32+sl,1.355+sl,0.15,0.27,CAP,xf=Hd)
    fz=0.1515; eh=0.06*(1+0.5*p['fear'])*max(p['eyes'],0.15)
    for sx in (-1,1): D+=box(sx*0.065-0.03,sx*0.065+0.03,1.255+sl-eh/2,1.255+sl+eh/2+0.015,fz,fz+0.002,BLK,xf=Hd)
    D+=box(-0.05,0.05,1.18+sl,1.2+sl,fz,fz+0.002,BLK,xf=Hd) if p['fear']<0.5 else box(-0.03,0.03,1.15+sl,1.21+sl,fz,fz+0.002,BLK,xf=Hd)
    tag(D,Hd((0,1.26+sl,0)))
    for sx in (-1,1):                                                                           # rigid segmented arms: shoulder -> elbow -> hand on the rim
        a=p['wheel']+(0.0 if sx>0 else PI); hand=np.array([WHEEL_C[0]+WHEEL_R*math.cos(a)+sx*0.0,WHEEL_C[1]+WHEEL_R*math.sin(a),WHEEL_C[2]-0.07])
        sh=np.array(B((sx*0.33,1.06+sl,0.0))); el=(sh+hand)/2+np.array([sx*0.10,-0.12,-0.06])
        Q+=seg(tuple(sh),tuple(el),0.11,COAT,0.11)+seg(tuple(el),tuple(hand),0.10,COAT_D,0.10)+box(-0.055,0.055,-0.055,0.055,-0.055,0.055,SKIN,xf=lambda q,hand=hand: tuple(hand+np.array(q)))
    return Q,D
def bob_pose(t):
    amp=1.0+0.8*env(t,s('3b',0.0),s('4b',3.4),0.3,0.3)
    return 0.07*math.sin(1.25*t)*amp,0.018*math.sin(0.9*t+1.0)*amp,0.012*math.sin(1.05*t)*amp     # bob (y), roll, pitch
def boat_xf(t):
    x,z=boat_xz(t); bb,rl,pt=bob_pose(t); R_=Ry(boat_yaw(t))@Rx(pt)@Rz(rl); base=np.array([x,bb,z])
    return lambda q: tuple(base+R_@np.array(q,float))
# ======================= animation: the captain =======================
def captain_pose(t):
    p=dict(IDLE)
    w=-0.55*env(t,s('2b',0.2),s('3b',1.5),0.5,0.7)                                              # steers LEFT slightly towards the brighter light
    w+=PI*1.3*sm(seg01(t,s('4a',0.1),s('4a',0.75)))*(1-sm(seg01(t,s('5a',0.0),s('5a',1.2))))      # spins the wheel hard RIGHT (too late)
    w+=0.9*sm(seg01(t,s('9a',0.2),s('9a',1.4)))*(1-sm(seg01(t,s('9a',3.5),s('10a',0.8))))          # charted approach: wheel right
    p['wheel']=w
    look_l=-0.40*env(t,s('2a',1.0),s('2b',2.0),0.3,0.3); look_r=0.45*env(t,s('8a',0.2),s('8d',1.4),0.3,0.4)
    p['hyaw']=look_l+look_r-0.45*env(t,s('7a',0.2),s('7c',0.0),0.3,0.3)-0.55*sm(seg01(t,s('4a',0.0),s('4a',0.12)))*(1-sm(seg01(t,s('5a',0.0),s('5a',0.4))))      # snap towards the rocks
    p['hp']=0.55*env(t,s('5a',0.5),s('6b',0.4),0.4,0.5)-0.12*env(t,s('10a',0.4),DUR,0.6,0.1)
    p['fear']=env(t,s('3b',0.0),s('4b',3.0),0.2,0.5)
    p['lean']=-0.12*sm(seg01(t,s('4a',0.0),s('4a',0.15)))*(1-sm(seg01(t,s('4b',1.0),s('4b',2.5))))
    p['relief']=env(t,s('9a',3.6),DUR,0.8,0.1)
    p['eyes']=1.0-min(1.0,math.sin(PI*seg01(t,s('2a',2.0),s('2a',2.2)))+math.sin(PI*seg01(t,s('7a',1.5),s('7a',1.7))))
    return p

# ======================= cameras =======================
def cam_shot(t):
    c=cam_id(t); x,z=boat_xz(t); yw=boat_yaw(t); bb,rl,pt=bob_pose(t); R_=Ry(yw)
    def Bw(q): return tuple(np.array([x,bb,z])+R_@np.array(q,float))
    if c=='A': return Bw((0.0,2.15,-3.5)),Bw((0.0,1.75,8.0)),42.0
    if c=='B': return Bw((-1.45,1.95,1.55)),Bw((0.0,1.55,-0.1)),44.0
    if shot_of(t)==3: return (4.0,3.0,22.0),(-4.0,3.2,56.0),62.0
    return (2.5,3.4,44.0),(-3.5,3.0,62.0),62.0

# ======================= clearance (HUD + QA) =======================
_BV=np.array([p for q in boat_local() for p in q['p']])
def hull_clear(t):
    """smallest distance (m) between the boat hull and the rock footprints that are ahead of / beside it"""
    xf=boat_xf(t); Wv=np.array([xf(v) for v in _BV]); bz=boat_xz(t)[1]; d=1e9
    for cx,cz,hw,hd,h,ax,az in ROCKS:
        if cz+hd<bz-1.0: continue
        dx=np.maximum(np.abs(Wv[:,0]-cx)-hw,0); dz=np.maximum(np.abs(Wv[:,2]-cz)-hd,0); d=min(d,float(np.hypot(dx,dz).min()))
    return d
_CT=np.arange(0,DUR+0.01,1/12.); _CL=np.array([hull_clear(t) for t in _CT])
def clearance(t): return float(np.interp(t,_CT,_CL))

# ======================= render =======================
R=Renderer(W,H,fog=FOGC)
def fog_end(t): return 24+70*env(t,s('3a',-0.4),s('4b',2.8),0.9,1.6)+14*env(t,s('5a',0.0),s('7c',2.5),1.0,1.0)+46*env(t,s('8a',0.0),DUR,1.2,0.1)
_fn=np.random.default_rng(5).random((H//8+2,W//8+2))
def _smooth_noise():
    a=np.array(Image.fromarray((_fn*255).astype(np.uint8)).resize((W,H),Image.BICUBIC),np.float32)/255.0; return a
FOGN=_smooth_noise()
def proj(x,y,z,cam,fov): return R.project((x,y,z),R.view(cam,fov))
def glow(a,pr,fpx,rm,col,k):
    """additive banded 2D glow anchored at a projected world point; rm = radius in metres"""
    if not pr or k<=0.01: return
    gx,gy=np.meshgrid(np.arange(W)+0.5,np.arange(H)+0.5); r=max(2.0,fpx*rm/pr[2]); d=np.sqrt((gx-pr[0])**2+(gy-pr[1])**2)/r
    g=np.clip(1-d,0,1)**1.6; g=np.round(g*6)/6; a+=g[...,None]*np.array(col,np.float32)*k
def render(t):
    cp,tg,fov=cam_shot(t); cam=Camera.look(cp,tg); cpa=np.array(cp); xf=boat_xf(t); st=captain_pose(t)
    fa,fb=flash_a(t),flash_b(t); visb=0.6+0.4*env(t,s('8a',-0.3),DUR,0.8,0.1)
    bq=transform(boat_local()+wheel(st['wheel']),xf); cq,cd=captain_local(st); cq=transform(cq,xf); cd=transform(cd,xf)
    cd[:]=[x for x in cd if np.linalg.norm(x['c']-cpa)<np.linalg.norm(x['hc']-cpa)]
    lamA=transform(lantern_box(LA[0],LA[1],LA_Y,fa>0.3,LIGHT_A),lambda q:q); lamB=transform(lantern_box(LB[0],LB[1],LB_Y,fb>0.3,LIGHT_B),lambda q:q)
    lights=[(xf((0,2.7,-0.9)),(255,196,120),0.95),(xf((0,3.4,2.6)),(255,190,110),0.45),((-30,60,-10),(150,170,255),0.55)]
    img,vi,zb=zrender(R,cam,[SEA_Q,ROCK_Q,LH_A,LH_B,MARK_Q,lamA,lamB,bq,cq,cd],lights,fov=fov,fog_start=4,fog_end=fog_end(t),ambient=0.42,bias=[1,1,1,1,1,1,1,1,1,1.004],return_z=True)
    a=np.asarray(img).astype(np.float32)*np.array([0.9,0.96,1.1],np.float32)
    a+=FOGN[...,None]*np.array([5,6,9],np.float32)*(1.0-0.7*env(t,s('3a',-0.4),s('4b',2.8),0.9,1.6))                       # low-res 2D fog noise
    fpx=R.view(cam,fov)[7]
    glow(a,proj(LA[0],LA_Y-0.5,LA[1],cam,fov),fpx,3.0+4.0*fa,LIGHT_A,0.62+0.7*fa)
    glow(a,proj(LB[0],LB_Y-0.5,LB[1],cam,fov),fpx,2.0+6.0*fb,LIGHT_B,(0.34+1.0*fb)*visb)
    if cam_id(t)=='C': glow(a,proj(*xf((0.86,DECK_Y+0.8,-2.34)),cam,fov),fpx,0.7,(255,200,110),0.8)
    for (mx,mz),c in ((MARK_L,(255,70,70)),(MARK_R,(70,255,120))): glow(a,proj(mx,2.9,mz,cam,fov),fpx,1.6,c,0.55*visb)
    return post.ps1(Image.fromarray(np.clip(a,0,255).astype(np.uint8))),cam,fov

# ======================= HUD, chart, UI (2D overlays) =======================
ACC,WHT,RED,GRN,CYAN=mc.ACC,mc.WHT,mc.RED,(130,255,150),mc.CYAN
def hud(d,t):
    c=clearance(t); col=RED if c<8 and int(t*6)%2==0 else (ACC if c<16 else GRN) if c>=8 else (255,160,160)
    d.rectangle([0,0,118,22],fill=(8,8,20)); font.text(d,'ROCKS',4,4,col,1,(0,0,0)); font.text(d,f'{c:.0f} M' if c<100 else '99 M',64,4,col,1,(0,0,0))
    d.rectangle([4,14,4+104,19],fill=(8,8,20),outline=col); d.rectangle([5,15,5+int(102*min(1.0,c/30)),18],fill=col)
    if c<8: font.text(d,'DANGER',74,4,RED,1,(0,0,0)) if False else None
def _text(d,s_,x,y,col,sc=1): font.text(d,s_,x,y,col,sc,(0,0,0))
def chart_small(d,t0,t):
    u=sm(seg01(t,t0,t0+0.3)); oy=int(lerp(70,0,u)); x0,y0,x1,y1=10,128+oy,170,252+oy
    d.rectangle([x0,y0,x1,y1],fill=(214,196,150)); d.rectangle([x0+3,y0+12,x1-3,y1-3],fill=(24,52,100))
    _text(d,'NAUTICAL CHART',x0+22,y0+3,(60,40,20),1)
    for k in range(1,6): d.line([x0+3+k*26,y0+12,x0+3+k*26,y1-3],fill=(36,70,124)); 
    for k in range(1,5): d.line([x0+3,y0+12+k*20,x1-3,y0+12+k*20],fill=(36,70,124))
    d.polygon([(x0+3,y0+12),(x0+62,y0+12),(x0+54,y0+40),(x0+40,y0+62),(x0+3,y0+70)],fill=(26,26,36))                         # rocky headland (left)
    d.polygon([(x1-3,y0+12),(x1-40,y0+12),(x1-46,y0+44),(x1-3,y0+52)],fill=(52,90,60)); d.polygon([(x1-3,y0+64),(x1-40,y0+66),(x1-50,y0+78),(x1-3,y0+100)],fill=(52,90,60))   # harbor shore with a gap
    d.rectangle([x0+50,y0+34,x0+57,y0+47],fill=(240,240,240)); d.rectangle([x0+51,y0+31,x0+56,y0+34],fill=(255,220,90))                      # lighthouse A
    d.rectangle([x1-52,y0+52,x1-46,y0+63],fill=(240,240,240)); d.rectangle([x1-51,y0+49,x1-47,y0+52],fill=(255,220,90))                    # lighthouse B
    _text(d,'HEADLAND',x0+6,y0+16,(255,120,120),1); _text(d,'HARBOR',x1-50,y0+16,(130,255,150),1)
    bx,by=x0+78,y1-14; d.polygon([(bx,by-7),(bx-5,by+5),(bx+5,by+5)],fill=ACC)                                                              # the boat
    pts=[(bx,by-9),(bx+6,by-24),(bx+22,by-40),(bx+40,by-56),(x1-48,y0+57)]                                                                  # dotted charted approach into the gap on the RIGHT
    for (ax_,ay_),(bx_,by_) in zip(pts,pts[1:]):
        for k in range(4): px=ax_+(bx_-ax_)*k/4; py=ay_+(by_-ay_)*k/4; d.rectangle([px,py,px+1,py+1],fill=CYAN)
def panels(d,t):
    t0=s('6a',-0.2); u=sm(seg01(t,t0,t0+0.25)); oy=int(lerp(60,0,u))
    d.rectangle([3,118+oy,177,172+oy],fill=(58,18,24),outline=RED); d.rectangle([3,178+oy,177,232+oy],fill=(14,48,28),outline=GRN)
    _text(d,'ROCKY HEADLAND',6,123+oy,(255,150,150),2); _text(d,'HARBOR',6,183+oy,(150,255,170),2)
    lit1=any(a<=t<a+0.45 for a in (s('6a',1.15),)); lit2=any(a<=t<a+0.4 for a in (s('6b',0.55),s('6b',1.35)))
    d.ellipse([18,146+oy,34,162+oy],fill=ACC if lit1 else (60,50,20),outline=WHT); _text(d,'1 FLASH',44,149+oy,ACC if lit1 else WHT,2)
    for k,cx in enumerate((18,42)): d.ellipse([cx,206+oy,cx+16,222+oy],fill=(160,255,255) if lit2 and (k==0)==(t<s('6b',0.95)) or (lit2 and k==1 and t>=s('6b',0.95)) else (20,70,60),outline=WHT)
    _text(d,'2 FLASHES',66,209+oy,GRN,2)
def label_light(d,t,cam,fov,x,y,z,text,col):
    pr=proj(x,y,z,cam,fov)
    if pr and 0<pr[0]<W: _text(d,text,max(2,min(W-2-font.width(text,1),int(pr[0])-font.width(text,1)//2)),int(pr[1])+18,col,1)
def ui(d,t,cam,fov):
    a=s('5a',0.5)
    if a<=t<CUTS[6]-0.0 and shot_of(t)==5: chart_small(d,a,t)
    if shot_of(t)==6: panels(d,t)
    if s('7b',0.0)<=t<s('7c',0.0)+1.9 and shot_of(t)==7:
        mc.ui_box(d,['1 FLASH'],96,ACC,3); label_light(d,t,cam,fov,LA[0],LA_Y,LA[1],'HEADLAND',RED)
    if shot_of(t)==8:
        label_light(d,t,cam,fov,LB[0],LB_Y,LB[1],'HARBOR',GRN)
        if s('8c',0.35)<=t: mc.ui_box(d,['LIGHT','IDENTIFIED'],26,GRN if int((t-s('8c',0.35))*6)%2==0 else (220,255,225),2)
    if shot_of(t)==10 and s('10a',0.7)<=t: mc.ui_box(d,['LIGHTHOUSE','IDENTIFIED'],26,CYAN if int((t-s('10a',0.7))*4)%2==0 else (210,245,255),2)
def shake(t):
    for t0,amp in ((s('3b',0.0),2.0),(s('4a',0.1),4.0),(s('7b',0.1),2.0),(s('8b',0.08),1.5),(s('8c',0.0),1.5)):
        u=(t-t0)/0.3
        if 0<=u<1: return int(round(amp*math.sin(70*(t-t0))*(1-u))),int(round(amp*0.6*math.cos(55*(t-t0))*(1-u)))
    if 52.0<=t<54.6 and clearance(t)<2.2: return (1 if int(t*24)%2 else -1),0                                                                   # subtle vibration near the rocks
    return 0,0
def frame(t):
    img,cam,fov=render(t); dx,dy=shake(t)
    if dx or dy:
        from PIL import ImageChops; img=ImageChops.offset(img,dx,dy)
    d=ImageDraw.Draw(img); hud(d,t); ui(d,t,cam,fov); mc.subtitles(d,t); return img

# ======================= QA manifest =======================
def boat_state(t): return dict(base=(*boat_xz(t),),yaw=boat_yaw(t))
def captain_state(t): x,z=boat_xz(t); return dict(base=(x,0.0,z),yaw=boat_yaw(t),**captain_pose(t))
def _tf(t): return boat_xf(t)
def boat_model(**st):
    t=st['t'] if 't' in st else 0.0
    return transform(boat_local()+wheel(0.0),boat_xf(CUR[0]))
def captain_model(**st):
    p={k:v for k,v in st.items() if k in IDLE}; return transform(captain_local(p)[0],boat_xf(CUR[0]))
CUR=[0.0]
def _chars_state(fn):
    def g(t): CUR[0]=t; return fn(t)
    return g
def _extra(t):
    out=[]; c=clearance(t)
    if t>0:
        x0,z0=boat_xz(t-1/FPS); x1,z1=boat_xz(t)
        if math.hypot(x1-x0,z1-z0)>0.3: out.append(('teleport',f'boat moves {math.hypot(x1-x0,z1-z0):.2f} m in one frame'))
    if c<0.35: out.append(('rock',f'boat hull {c:.2f} m from the rocks'))
    if t<0.05:
        cp,tg,fov=cam_shot(0.0); pr=proj(ROCKS[0][0],3.0,ROCKS[0][1],Camera.look(cp,tg),fov)
        if not pr or not (0<pr[0]<W): out.append(('camera','the foreground rock is not in the first frame'))
        if clearance(0.0)>10: out.append(('hud','danger is not shown in the first frame'))
    return out
QA=dict(fps=FPS,dur=DUR,W=W,frame=lambda t: frame(t),chars={'captain':(_chars_state(captain_state),captain_model,'_none',1.0)},
    geom=lambda t,name,st,V: [('floor',f'{name} under the sea')] if V[:,1].min()<-0.5 else [],
    extra=_extra,camera=lambda t: cam_shot(t)[0],min_cam_dist=0.4,camera_ok=lambda p: -60<p[0]<60 and 0.5<p[1]<8,allow_jump=[('captain',c+d) for c in CUTS[1:-1] for d in (0.0,0.12,0.25)],weapon_events=[],
    scenes=[dict(id=f'shot{i}',t0=CUTS[i-1],t1=CUTS[i],action=a) for i,a in enumerate((
        'foreground rock, captain at the wheel, light A flashes, ROCKS counter (cam A)','two lights in the fog, steers LEFT to the brighter one (cam A)','fog clears, wall of rocks on the left (cam C)',
        'wheel spun right, head snaps, boat still drifting (cam B)','looks down at the chart, chart overlay (cam B)','1 FLASH headland / 2 FLASHES harbor panels (cam B)',
        'counts light A: one flash, 1 FLASH, HEADLAND (cam A)','light B flashes twice, LIGHT IDENTIFIED, HARBOR (cam A)','turns RIGHT, slips past the last rock (cam C)','harbor ahead, B flashes twice, LIGHTHOUSE IDENTIFIED (cam A)'),1)],
    texts=lambda: [('sub',' '.join(r),mc.SUB_SC) for _,_,rows,_ in SUBS for r in rows]+[('ui',l,sc) for l,sc in (('1 FLASH',3),('LIGHT',2),('IDENTIFIED',2),('LIGHTHOUSE',2),('ROCKY HEADLAND',2),('HARBOR',2),('2 FLASHES',2),('NAUTICAL CHART',1),('HEADLAND',1),('ROCKS',1))])

TEST=os.environ.get('TEST')
if TEST and __name__=='__main__':
    ims=[frame(float(x)) for x in TEST.split(',')]; shp=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): shp.paste(im,(i*182,0))
    shp.resize((shp.width*2,640),Image.NEAREST).save('test.png'); sys.exit()

# ======================= AUDIO: synthesized suspense bed, ocean, engine (follows the boat speed), creaks, flash cues, UI, narration =======================
def build_audio(path):
    import soundfile as _sf
    s_=Sound(DUR,loop=False,seed=81); sr=s_.sr; n=s_.n; M=np.zeros(n); M2=np.zeros(n); AMB=np.zeros(n); tt_all=s_.t
    def hz(m): return 440*2**((m-69)/12)
    def note(buf,t0,m,d,v,wave='tri',dec=3.0,att=0.005):
        tt=s_.T(d); ph=2*np.pi*hz(m)*tt
        x={'sin':np.sin(ph),'tri':(2/np.pi)*np.arcsin(np.sin(ph)),'bell':np.sin(ph)+0.35*np.sin(2*ph)+0.12*np.sin(3.01*ph),'sq':np.sign(np.sin(ph))*0.5}[wave]
        i=int(t0*sr); j=min(n,i+len(tt))
        if i>=n: return
        buf[i:j]+=(x*np.minimum(1,tt/att)*np.exp(-tt*dec)*v)[:j-i]
    def tone(t0,f0,f1,d,v,harm=(1.0,0.4),buf=None):
        tt=s_.T(d); fr=f0+(f1-f0)*(tt/d); ph=np.cumsum(fr)/sr; x=sum(h*np.sin(2*np.pi*ph*(k+1)) for k,h in enumerate(harm))*np.minimum(1,tt/0.004)*np.sin(np.pi*np.clip(tt/d,0,1))**0.5
        if buf is None: s_.place(x,t0,v)
        else: i=int(t0*sr); j=min(n,i+len(tt)); buf[i:j]+=(x*v)[:j-i]
    def nb(t0,d,lo,hi,v,seed,sh=1.0): s_.place(s_.filt_short(s_.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s_.T(d)/d)**sh,t0,v)
    def thud(t0,f=60,v=0.1,d=0.25): tt=s_.T(d); s_.place(np.sin(2*np.pi*f*tt*(1-0.3*tt/d))*np.exp(-tt*14),t0,v)
    def creak(t0,d=0.5,v=0.04,f=320): tt=s_.T(d); fr=f*(1+0.5*np.sin(2*np.pi*7*tt))*(1-0.3*tt/d); s_.place(np.sign(np.sin(np.cumsum(fr)/sr*2*np.pi))*0.4*np.sin(np.pi*tt/d)**2*np.abs(s_.noise(d,int(t0*77))+0.6),t0,v)
    # ---- ocean bed + engine hum that follows the boat speed + a low drone ----
    AMB+=s_.filt(s_.rng.normal(0,1,n),lo=50,hi=400)*0.09*(1+0.5*np.sin(2*np.pi*0.11*tt_all))+s_.filt(s_.rng.normal(0,1,n),lo=1500,hi=4500)*0.004*(1+0.6*np.sin(2*np.pi*0.17*tt_all+1))
    sp=np.interp(tt_all,_TS,np.array([abs(float(_spd(min(max(t,0),DUR)))) for t in _TS])); eng=(np.sin(2*np.pi*46*tt_all)+0.5*np.sin(2*np.pi*92*tt_all)+0.25*np.sin(2*np.pi*138*tt_all))*(1+0.15*np.sin(2*np.pi*8*tt_all))
    AMB+=eng*(0.006+0.0045*sp)
    drone=(np.sin(2*np.pi*55*tt_all)+np.sin(2*np.pi*55.6*tt_all)+0.4*np.sin(2*np.pi*82.4*tt_all))*0.014*(0.6+0.4*np.sin(2*np.pi*0.07*tt_all))
    M+=drone
    # ---- music sections (0-12 mysterious drone + mechanical ticks / 12-30 heartbeat + tension / 30-43 quiet investigative / 43-55 build / 55-60 restrained resolution) ----
    c2,c3,c4,c5=CUTS[3],CUTS[6],CUTS[8],CUTS[10]
    for k in range(int(c2/0.5)): note(M,0.1+k*0.5,[57,57,60,57,55,57,60,64][k%8],0.08,0.012,'sq',30.0)                    # mechanical retro ticks
    t0=c2
    while t0<c3:                                                                                                         # heartbeat-like bass pulse, speeding up
        thud(t0,52,0.10,0.25); thud(t0+0.2,48,0.07,0.2); t0+=lerp(0.95,0.62,(t0-c2)/(c3-c2))
    for k in range(int((c3-c2)/0.5)): note(M,c2+k*0.5,[45,45,48,43][(k//2)%4],0.5,0.035,'tri',3.0)
    for k,m_ in enumerate((69,72,64,67,69,0,72,76,0,69,64,0)):                                                          # quiet investigative tones
        if m_ and c3+k*1.15<c4: note(M,c3+k*1.15,m_,1.2,0.022,'bell',3.0)
    k=0; t0=c4
    while t0<c5-0.2: note(M,t0,[45,52,57,52][k%4]+int(7*(t0-c4)/(c5-c4)),0.2,0.04,'sq',9.0); k+=1; t0+=lerp(0.34,0.14,(t0-c4)/(c5-c4))        # building ostinato
    for m_ in (45,52,57,60): note(M,c5,m_,DUR-c5+0.3,0.03,'sin',0.5,0.4)                                               # restrained resolution
    note(M,c5+0.6,76,2.0,0.03,'bell',1.6)
    # ---- foley ----
    for t0 in (2.1,6.4,9.0,14.2,21.5,26.0,31.5,37.0,44.5,48.0,56.5): creak(t0,0.55,0.03)
    for t0 in (s('2b',0.4),s('4a',0.1),s('9a',0.2)): creak(t0,0.7,0.06,380)                                           # steering wheel creaks
    tone(s('3a',0.2),90,520,1.6,0.05,harm=(1.0,0.5,0.3)); nb(s('3a',0.2),1.6,300,2500,0.03,31,2.0)                       # rising suspense tone when the fog clears
    tone(s('4a',0.0),200,70,0.4,0.07,harm=(1.0,0.6)); thud(s('4a',0.05),70,0.14,0.3)                                    # panic
    tone(s('4b',0.2),70,140,2.6,0.035,harm=(1.0,0.5,0.25))                                                              # rising low-frequency pulse
    nb(s('5a',0.5),0.7,2000,7000,0.04,41,1.0); note(M2,s('5a',0.5)+0.4,84,0.5,0.04,'bell',4.0); note(M2,s('5a',0.5)+0.55,91,0.7,0.04,'bell',3.5)   # paper rustle + discovery chime
    for t0 in (s('6a',1.15),): note(M2,t0,76,0.35,0.05,'sq',7.0)                                                          # one-flash identification
    for t0 in (s('6b',0.55),s('6b',1.35)): note(M2,t0,88,0.25,0.05,'sq',9.0)                                              # two-flash identification
    for t0 in flash_times_a(): note(M2,t0,60,0.12,0.010,'sq',20.0)                                                       # soft ticks for every flash (consistent pattern)
    for t0 in flash_times_b(): note(M2,t0,84,0.1,0.008,'sq',24.0)
    tone(TA0,330,300,0.45,0.07,harm=(1.0,0.4)); tone(TA0+0.5,150,110,0.6,0.05,harm=(1.0,0.6,0.3))                          # one-flash cue + low warning
    for t0 in (s('8b',0.08),s('8c',0.08)): tone(t0,880,880,0.3,0.07,harm=(1.0,0.3))                                     # two synchronized flash cues
    for k,m_ in enumerate((72,76,79)): note(M2,s('8c',0.4)+k*0.14,m_,0.9,0.045,'bell',3.0)                              # hopeful rising notes
    tone(s('9a',0.6),110,600,3.4,0.045,harm=(1.0,0.5,0.3)); nb(s('9a',0.6),3.4,200,3000,0.03,53,2.0)                    # escape crescendo
    thud(s('9a',3.9),55,0.15,0.5)
    for k,m_ in enumerate((60,64,67,72)): note(M2,c5+k*0.12,m_,1.6,0.04,'bell',2.5)                                      # relieved release
    for t0 in (s('10a',0.9)+0.05,s('10a',0.9)+DB+0.05): tone(t0,784,784,0.25,0.05,harm=(1.0,0.3))
    # ---- voice ----
    NB=np.zeros(n); duck=np.ones(n); mdip=np.ones(n)
    mdip[int(s('7a',1.2)*sr):int(s('7b',1.4)*sr)]=0.4                                                                    # brief music dip while counting
    for key in ORDER:
        a,_=_sf.read(os.path.join(TTS_DIR,'lh',key+'.wav')); a=a if a.ndim==1 else a.mean(1)
        act=a[np.abs(a)>0.02]; a=a*0.2/(np.sqrt((act**2).mean())+1e-9)
        i=int(ST[key]*sr); j=min(n,i+len(a)); NB[i:j]+=a[:j-i]; duck[max(0,i-int(0.05*sr)):min(n,j+int(0.1*sr))]=0.55
    duck=np.convolve(duck,np.ones(2400)/2400,'same'); mdip=np.convolve(mdip,np.ones(4800)/4800,'same')
    s_.L+=AMB+M*duck*mdip*3.0+M2*(0.6+0.4*duck); s_.R+=np.roll(AMB,900)+np.roll(M,300)*duck*mdip*3.0+M2*(0.6+0.4*duck)
    s_.reverb(0.12,length=1.0,decay=4.0)
    pk=max(np.abs(s_.L).max(),np.abs(s_.R).max()); gv=pk/np.abs(NB).max()*0.95
    s_.L=s_.L*(0.8+0.2*duck)+NB*gv; s_.R=s_.R*(0.8+0.2*duck)+NB*gv
    st=np.stack([s_.L,s_.R],1); k=int(0.05*sr); st[-k:]*=np.linspace(1,0,k)[:,None]
    st=st/np.max(np.abs(st))*0.9; _sf.write(path,st,sr,subtype='PCM_16'); return path
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'lighthouse.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'lh_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.96,vignette=0.25,grain=1.5,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(post.upscale(frame(f/FPS),S),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
