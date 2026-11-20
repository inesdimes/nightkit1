"""WHAT HAPPENS TO THE GUY WHOSE CAR YOU STEAL? (Insert Disc 2) ~31 s PS1 comedy, 9:16, procedural (nightkit). Brief: briefs/stolen_car.md.
Gary's car is stolen 900 times; he leaves keys + sandwich + note; the driver is the "nicest guy in town" (five wanted stars, police lights).
No game name / logo / character / map / music inside the video. NEW assets: Gary + the driver (box humans), car (open cabin, dents, lock, key, sandwich, note),
police car, street + house + palms + lamp posts, day -> sunset sky, HUD (VEHICLE STOLEN, STOLEN counter, FUEL: FULL, wanted stars, notes).
Voice: python tools/tts/sc.py src; python tools/tts/sc_vc.py (Chatterbox python); python tools/tts/sc.py build vc  -> $TTS_DIR/sc/*.wav (+ sentence timings)
Run: TEST=1,5,9 python examples/stolen_car.py -> test.png | PART=a:b (frames -> out/sc_a.mp4) | PART=audio"""
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
FPS=24; W,H,S=180,320,6; F=1.0/FPS
PI=math.pi; sm=motion.smooth
def seg01(t,a,b): return max(0.0,min(1.0,(t-a)/(b-a)))
def lerp(a,b,u): return a+(b-a)*u
def lerp3(a,b,u): return tuple(a[i]+(b[i]-a[i])*u for i in range(3))
box=FB.box; xform=FB.xform; Rx,Ry=FB.Rx,FB.Ry
WHT=(242,238,226); YEL=(255,210,60); RED=(240,50,40); GRN=(80,220,90); BLU=(110,170,255); GRY=(150,150,160)

# ======================= voice timings (tools/tts/sc.py) =======================
SCR=json.load(open(os.path.join(TTS_DIR,'sc','script.json')))
GAP=0.3
def _lines():
    t=0.15; out=[]
    for k in [str(i) for i in range(1,12)]: out.append((k,round(t,3))); t+=SCR['dur'][k]+GAP
    return out,t-GAP
LINES,_vend=_lines(); T0=dict(LINES)
DUR=round(_vend+0.45,2); N=int(round(DUR*FPS))
def ws(k,i): return T0[k]+SCR['sent'][k][i][0]
def we(k,i): return T0[k]+SCR['sent'][k][i][1]
LEAD=2*F
def at(k,i,u): return ws(k,i)+(we(k,i)-ws(k,i))*u          # time inside a sentence

# ======================= story events =======================
T_TICK=at('2',1,0.52)-LEAD                                      # "nine hundred": 899 -> 900
T_LOCK=we('3',0)-0.30-LEAD                                      # "lock"
T_ALARM=we('3',1)-0.34-LEAD                                     # "alarm"
T_CAR2=we('3',2)-0.30-LEAD                                      # "car": the second car lands beside the first
T_THEFT=ws('4',0)+0.25                                          # "stole": both cars reverse out
T_KEYS=at('5',0,0.40)-LEAD                                      # "keys"
T_SAND=at('6',0,0.30)-LEAD                                      # "sandwich"
T_NOTE=at('7',0,0.42)-LEAD                                      # "note"
T_RET=T0['8']-0.04                                              # the car comes back
T_FULL=ws('8',1)                                                # "Full tank"
T_DENT=we('8',2)-0.42-LEAD                                      # "dents"
T_STAR0=ws('10',0)+0.15                                         # wanted stars light up one by one
T_POLICE=T0['11']-0.15
T_EXIT=T0['11']+0.2                                             # the driver steps out
T_NOTE2=T0['11']+1.1                                            # THANKS GARY note on the trunk
T_RUN=T0['11']+1.35                                             # sprints off
CUTS=[0.0,T0['3']-0.04,T0['5']-0.04,T0['8']-0.04,T0['9']-0.04,T0['10']-0.04,T0['11']-0.04,DUR]
CAR1=(-1.2,9.2); CAR2=(1.4,9.2); LANE=2.2

# ======================= palette =======================
SKIN=(250,210,174); SKIN_D=(222,176,138)
ROBE=(150,46,72); ROBE_D=(118,34,56)
RC=[(196,60,48),(70,120,200)]       # car 1 red, car 2 blue (the second car)
CHROME=(190,194,204)

# ======================= LOCKED ASSET: box humans (Gary, the driver) =======================
def _inv_local(w,b,Rb,lean,hip):
    """world point -> torso-space point (inverse of T in human())"""
    piv=np.array([0,hip,0.0]); o=np.array([0,hip-0.88,0.0]); loc=Rb.T@(np.array(w,float)-b)
    return piv-o+Rx(lean).T@(loc-piv)
def human(kind,base,yaw,walk=0.0,run=0.0,lean=0.0,head=0.0,rh=None,lh=None,rhw=None,lhw=None,sit=0.0,mug=False,smile=0.0,eyes=1.0,fob=False,note=None,keys=False):
    """local forward +z. rh/lh: hand targets in torso space; rhw/lhw: hand targets in WORLD space (IK, solved here). kind 'gary' | 'driver'."""
    b=np.array(base,float); Rb=Ry(yaw); hip=0.88-0.40*sit
    def Wd(p): return tuple(b+Rb@np.array(p,float))
    def T(p):
        p=np.array(p,float); piv=np.array([0,hip,0]); return Wd(piv+Rx(lean+0.2*run)@(p-piv+np.array([0,hip-0.88,0])))
    G=(kind=='gary')
    if rhw is not None: rh=_inv_local(rhw,b,Rb,lean+0.2*run,hip)
    if lhw is not None: lh=_inv_local(lhw,b,Rb,lean+0.2*run,hip)
    LEG=(SKIN,SKIN) if G else ((52,74,132),(40,58,108)); SHOE=(255,140,176) if G else (240,240,244)
    Q=[]; amp=0.5+0.35*run; sw=amp*math.sin(walk)
    for sx,ph in ((-1,1),(1,-1)):
        hp=np.array([sx*0.1,hip,0])
        if sit>0: ft=np.array([sx*0.11,0.1,0.62*sit+0.02]); bend=(0,1,0.2)
        else:
            a=ph*sw; ft=hp+np.array([0,-0.84*math.cos(a),0.84*math.sin(a)]); ft[1]=max(0.05,ft[1]+0.1*max(0,math.sin(walk*ph+PI/2))*(1 if walk else 0)); bend=(0,0,1)
        lq,_=FB.limb(hp,ft,bend,0.9,0.14,LEG[0],LEG[1],0.12); Q+=xform(lq,Wd)
        Q+=box(ft[0]-0.075,ft[0]+0.075,max(0.0,ft[1]-0.06) if sit==0 else ft[1]-0.06,ft[1]+0.05,ft[2]-0.06,ft[2]+0.19,SHOE,xf=Wd)
    if G:
        Q+=box(-0.2,0.2,0.86,1.38,-0.13,0.13,ROBE,xf=T)+box(-0.205,0.205,0.46,0.88,-0.14,0.14,ROBE_D,xf=T)         # bathrobe + skirt
        Q+=box(-0.21,0.21,0.84,0.93,-0.145,0.145,(236,214,170),xf=T)+box(-0.05,0.05,1.0,1.38,0.13,0.14,(236,214,170),xf=T)  # sash, open front
    else:
        Q+=box(-0.19,0.19,0.86,1.38,-0.12,0.12,(236,236,240),xf=T)+box(-0.2,0.2,0.8,0.9,-0.13,0.13,(50,70,130),xf=T)  # tank top, belt
        Q+=box(-0.17,-0.1,1.2,1.38,-0.125,-0.12,SKIN,xf=T)+box(0.1,0.17,1.2,1.38,-0.125,-0.12,SKIN,xf=T)
    hy=1.4; Rh=Ry(head)
    def Hh(p): p=np.array(p,float); return T(np.array([0,hy,0])+Rh@(p-np.array([0,hy,0])))
    Q+=box(-0.14,0.14,hy,hy+0.3,-0.14,0.14,SKIN,xf=Hh)
    if G:
        Q+=box(-0.145,-0.1,hy+0.12,hy+0.3,-0.145,0.1,(150,150,156),xf=Hh)+box(0.1,0.145,hy+0.12,hy+0.3,-0.145,0.1,(150,150,156),xf=Hh)   # grey side hair
        Q+=box(-0.15,0.15,hy+0.24,hy+0.3,-0.15,-0.04,(150,150,156),xf=Hh)
        Q+=box(-0.13,0.13,hy+0.085,hy+0.14,0.14,0.18,(86,52,34),xf=Hh)                                   # moustache
        Q+=box(-0.04,0.04,hy+0.13,hy+0.18,0.14,0.2,(236,184,148),xf=Hh)                                  # nose
        Q+=box(-0.06,0.06,hy+0.035,hy+0.06,0.14,0.15,(150,60,60) if smile<0.3 else (250,250,250),xf=Hh)  # mouth / teeth
        if smile>0.3: Q+=box(-0.095,-0.06,hy+0.06,hy+0.085,0.14,0.15,(150,60,60),xf=Hh)+box(0.06,0.095,hy+0.06,hy+0.085,0.14,0.15,(150,60,60),xf=Hh)
        ey=hy+0.17
        for sx in (-1,1):
            Q+=box(sx*0.035,sx*0.09,ey,ey+(0.045 if eyes>0.5 else 0.015),0.14,0.155,(20,16,18),xf=Hh)
            Q+=box(sx*0.03,sx*0.1,ey+0.07,ey+0.085,0.14,0.158,(86,52,34),xf=Hh)
    else:
        Q+=box(-0.15,0.15,hy+0.27,hy+0.36,-0.15,0.15,(200,36,40),xf=Hh)+box(-0.15,0.15,hy+0.27,hy+0.32,0.14,0.34,(170,28,32),xf=Hh)   # red cap + brim
        Q+=box(-0.15,0.15,hy+0.1,hy+0.27,-0.16,-0.1,(34,26,22),xf=Hh)                                  # hair at the back
        Q+=box(-0.12,0.12,hy+0.15,hy+0.22,0.14,0.16,(14,14,18),xf=Hh)                                   # shades
    sh={-1:np.array([-0.26,1.31,0]),1:np.array([0.26,1.31,0])}
    idle={-1:np.array([-0.3,0.74,0.04]),1:np.array([0.3,0.74,0.04])}
    if run: idle={-1:np.array([-0.26,0.85,-0.2*math.sin(walk)]),1:np.array([0.26,0.85,0.2*math.sin(walk)])}
    hand={-1:np.array(lh,float) if lh is not None else idle[-1],1:np.array(rh,float) if rh is not None else idle[1]}
    for sx in (-1,1):
        c1=ROBE if G else SKIN; c2=SKIN if G else SKIN_D
        aq,_=FB.limb(sh[sx],hand[sx],(sx*0.5,-0.4,-0.6),0.68,0.12,c1,c2,0.1); Q+=xform(aq,T)
        hp=hand[sx]; Q+=box(hp[0]-0.05,hp[0]+0.05,hp[1]-0.05,hp[1]+0.05,hp[2]-0.05,hp[2]+0.05,SKIN,xf=T)
    if mug:                                                                                              # mug in the right hand (never floating)
        hp=hand[1]; Q+=box(hp[0]-0.06,hp[0]+0.06,hp[1]-0.02,hp[1]+0.13,hp[2]-0.06,hp[2]+0.06,(244,244,248),xf=T)+box(hp[0]-0.05,hp[0]+0.05,hp[1]+0.125,hp[1]+0.14,hp[2]-0.05,hp[2]+0.05,(110,64,34),xf=T,emit=True)
        Q+=box(hp[0]+0.06,hp[0]+0.1,hp[1]+0.02,hp[1]+0.1,hp[2]-0.015,hp[2]+0.015,(244,244,248),xf=T)
    if fob:
        hp=hand[1]; Q+=box(hp[0]-0.03,hp[0]+0.03,hp[1]+0.04,hp[1]+0.12,hp[2]-0.02,hp[2]+0.02,(30,30,34),xf=T)+box(hp[0]-0.02,hp[0]+0.02,hp[1]+0.1,hp[1]+0.115,hp[2]-0.025,hp[2]-0.02,RED,xf=T,emit=True)
    if keys:                                                                                             # two key sets, one per hand
        for sx in (-1,1):
            hp=hand[sx]; Q+=box(hp[0]-0.04,hp[0]+0.04,hp[1]+0.04,hp[1]+0.2,hp[2]-0.012,hp[2]+0.012,(255,226,110),xf=T,emit=True)+box(hp[0]-0.07,hp[0]+0.07,hp[1]+0.17,hp[1]+0.24,hp[2]-0.012,hp[2]+0.012,(190,190,200),xf=T,emit=True)
    if note:
        hp=hand[1]; Q+=box(hp[0]-0.1,hp[0]+0.1,hp[1]-0.02,hp[1]+0.16,hp[2]-0.01,hp[2]+0.01,(250,246,200),xf=T,emit=True)
    return Q
def keys_in_hands(b,yaw,lean,hand_l,hand_r):
    """two key sets held up (Gary after the second theft): small gold boxes at the hand positions (world)"""
    return []

# ======================= LOCKED ASSET: car (open cabin, dents, lock, key, sandwich, note) =======================
def _dent_pos(i):
    side=-1 if i%2==0 else 1; z=-1.5+((i*37)%29)/29*3.0; y=0.38+((i*13)%7)/7*0.34
    return side,z,y
def car(pos,yaw,col,dents=0,door=0.0,lock=False,key=False,sand=False,note=False,flash=0.0,fl=0.0,police=0.0):
    """local forward +z, driver side = local -x. pos = ground centre. door: driver-door swing 0..1.2 rad. flash: emissive indicator blink 0/1.
    police: 0 = civilian, else light-bar phase (0..1 alternates red/blue)"""
    cd=tuple(int(c*0.72) for c in col); cl=tuple(min(255,int(c*1.18)) for c in col); Q=[]
    Q+=box(-0.9,0.9,0.3,0.78,-2.1,2.1,col)                                                              # chassis
    Q+=box(-0.88,0.88,0.78,0.9,0.9,2.1,cl)+box(-0.88,0.88,0.78,0.9,-2.1,-1.2,cl)                      # hood + trunk lid
    Q+=box(0.82,0.9,0.78,0.94,-1.2,0.85,col)+box(-0.9,-0.82,0.78,0.94,-1.2,-0.5,col) if door<=0 else box(0.82,0.9,0.78,0.94,-1.2,0.85,col)
    Q+=box(-0.88,0.88,0.78,1.2,0.88,1.0,(40,40,48))                                                    # dash
    Q+=box(-0.88,0.88,0.78,1.2,-1.28,-1.2,col)                                                          # rear panel
    Q+=box(-0.85,0.85,1.46,1.53,-1.2,0.85,cl)                                                           # roof
    for x,z in ((-0.82,0.82),(0.82,0.82),(-0.82,-1.15),(0.82,-1.15)): Q+=box(x-0.04,x+0.04,0.9,1.46,z-0.04,z+0.04,cd)
    Q.append(quad([(-0.84,0.98,0.94),(0.84,0.98,0.94),(0.84,1.46,0.78),(-0.84,1.46,0.78)],(70,100,140)))   # windshield
    for sx in (-0.45,0.45):                                                                             # seats
        Q+=box(sx-0.24,sx+0.24,0.3,0.5,-0.55,0.1,(46,44,50))+box(sx-0.24,sx+0.24,0.5,1.12,-0.62,-0.5,(56,54,60))
    for sx in (-1,1):
        for z in (-1.3,1.3):
            Q+=box(sx*0.9-0.1 if sx>0 else sx*0.9-0.12,sx*0.9+0.12 if sx>0 else sx*0.9+0.1,0.0,0.66,z-0.33,z+0.33,(16,16,18))
            Q+=box(sx*0.9+(0.1 if sx>0 else -0.14),sx*0.9+(0.14 if sx>0 else -0.1),0.17,0.49,z-0.15,z+0.15,CHROME)
    hl=(255,250,200) if not flash else (255,170,40)
    for sx in (-0.6,0.6): Q+=box(sx-0.16,sx+0.16,0.52,0.68,2.1,2.13,hl,emit=True)
    for sx in (-0.65,0.65): Q+=box(sx-0.15,sx+0.15,0.52,0.64,-2.13,-2.1,(255,170,40) if flash else (170,30,30),emit=True)
    for i in range(dents):                                                                              # dents = darker quads on both sides
        side,z,y=_dent_pos(i); x=side*0.905
        Q.append(quad([(x,y,z-0.22),(x,y,z+0.22),(x,y+0.18,z+0.18),(x,y+0.2,z-0.2)],tuple(int(c*0.5) for c in col)))
    Q+=box(-0.62,-0.28,0.95,1.2,0.62,0.68,(28,28,32))                                                   # steering wheel
    if lock: Q+=box(-0.88,0.0,1.0,1.14,0.5,0.76,(255,214,40),emit=True)+box(-0.88,-0.8,0.9,1.3,0.5,0.76,(255,214,40),emit=True)+box(-0.1,0.0,0.9,1.3,0.5,0.76,(255,214,40),emit=True)
    if key: Q+=box(-0.5,-0.44,0.9,0.96,0.76,0.84,(255,226,110),emit=True)+box(-0.49,-0.45,0.8,0.9,0.8,0.82,(255,226,110),emit=True)
    if sand:
        x,z=0.45,-0.25; Q+=box(x-0.17,x+0.17,0.5,0.54,z-0.12,z+0.12,(222,176,100))+box(x-0.18,x+0.18,0.54,0.56,z-0.13,z+0.13,(90,190,70))+box(x-0.15,x+0.15,0.56,0.58,z-0.1,z+0.1,(220,60,50))+box(x-0.17,x+0.17,0.58,0.62,z-0.12,z+0.12,(228,184,108))
    if note: Q+=box(-0.2,0.2,1.2,1.21,0.9,1.0,(252,248,205),emit=True)
    if police:
        a=police; Q+=box(-0.7,0.0,1.53,1.78,-0.35,0.25,(255,60,50) if a<0.5 else (120,20,20),emit=True)+box(0.0,0.7,1.53,1.78,-0.35,0.25,(70,120,255) if a>=0.5 else (14,24,70),emit=True)
    c=np.array(pos,float) if len(pos)==3 else np.array([pos[0],0.0,pos[1]]); Rb=Ry(yaw)
    def tf(p): return tuple(c+Rb@np.array(p,float))
    Q=xform(Q,tf)
    if door>0:                                                                                          # driver door swings open about its front edge
        hing=np.array([-0.9,0.0,0.85]); Rd=Ry(door)
        D=box(-0.9,-0.82,0.3,0.94,-0.5,0.85,cd)+box(-0.92,-0.9,0.5,0.8,-0.2,0.0,CHROME)
        D=xform(D,lambda p:tuple(c+Rb@(hing+Rd@(np.array(p,float)-hing)))); Q+=D
    return Q
def car_xf(pos,yaw): return lambda p:tuple(np.array(pos,float)+Ry(yaw)@np.array(p,float))

# --- car motion: arrive from the road (arc into the driveway) / reverse out and drive off to -x
R_ARC=2.0
def _path_dims(xt): return dict(xc=xt+R_ARC,lead=6.0,L_arc=PI/2*R_ARC,L_out=CAR1[1]-(LANE+R_ARC))
def path(s,xt):
    """arc-length s from the start of the road lead: heading -x on the lane, a quarter turn into the driveway, then straight to the house"""
    d=_path_dims(xt); xc,lead,La=d['xc'],d['lead'],d['L_arc']
    if s<=lead: return (xc+lead-s,LANE,-PI/2)
    if s<=lead+La:
        ph=(s-lead)/R_ARC; return (xc-R_ARC*math.sin(ph),LANE+R_ARC*(1-math.cos(ph)),-PI/2+ph)
    z=LANE+R_ARC+(s-lead-La); return (xt,z,0.0)
def s_end(xt): d=_path_dims(xt); return d['lead']+d['L_arc']+d['L_out']
def drive_in(t,t0,t1,xt):
    """position along the path, decelerating to a stop at t1; before t0 off screen on the road"""
    u=seg01(t,t0,t1); e=1-(1-u)**2; return path(e*s_end(xt),xt)
def reverse_out(t,t0,t1,xt):
    u=seg01(t,t0,t1); e=u*u; return path((1-e)*s_end(xt),xt)
def leave(t,xt,t0):
    """after reversing out the car drives off to -x along the lane, accelerating"""
    d=_path_dims(xt); return (d['xc']-0.5*14.0*(t-t0)**2,LANE,-PI/2)

def car1_state(t):
    """returns dict(pos, yaw, shown, extras) for the red car"""
    dents=3
    if t>=T_RET: dents=5
    if t>=T_DENT: dents=9
    dd=dict(dents=dents,key=False,sand=False,note=False,lock=False,door=0.0,flash=0.0,police=0.0)
    if t<T0['3']-0.04:                                                                                 # shot A: it screeches away along the road
        d=0.5*7.0*(t**2)+0.5*t; x=_path_dims(CAR1[0])['xc']-1.7-d; wob=0.12*math.sin(t*9)*seg01(t,0.0,0.5)*(1-seg01(t,0.5,2.4))
        return dict(pos=(x,LANE-0.4),yaw=-PI/2+wob,**dd)
    T_BACK=T_THEFT+0.7                                                                                 # reversed onto the road
    if t<T_THEFT: x,z,yw=CAR1[0],CAR1[1],0.0
    elif t<T_BACK: x,z,yw=reverse_out(t,T_THEFT,T_BACK,CAR1[0])
    elif t<T0['5']-0.04: x,z,yw=leave(t,CAR1[0],T_BACK)
    elif t<T_RET: x,z,yw=CAR1[0],CAR1[1],0.0                                                          # a new day: parked again (cut)
    else: x,z,yw=drive_in(t,T_RET,T_FULL-0.1,CAR1[0])
    if T0['3']-0.04<=t<T_THEFT: dd['lock']=t>=T_LOCK; dd['flash']=1.0 if (T_ALARM<=t<T_ALARM+0.9 and int((t-T_ALARM)*8)%2==0) else 0.0
    if T0['5']-0.04<=t<T_RET:
        dd['door']=1.2*sm(seg01(t,T_KEYS-0.5,T_KEYS-0.1)); dd['key']=t>=T_KEYS; dd['sand']=t>=T_SAND; dd['note']=t>=T_NOTE
    if t>=T_RET: dd['door']=1.2*(1-sm(seg01(t,T_FULL-0.3,T_FULL))) if t<T_FULL else 0.0
    if t>=T_POLICE: dd['door']=1.2*sm(seg01(t,T_EXIT-0.1,T_EXIT+0.15))
    return dict(pos=(x,z),yaw=yw,**dd)
def car2_state(t):
    """blue car: arrives for the third beat of line 3, is stolen with the first"""
    T_BACK=T_THEFT+0.8
    if t<T_CAR2-1.0 or t>=T0['5']-0.04: return None
    if t<T_CAR2+0.15: x,z,yw=drive_in(t,T_CAR2-1.0,T_CAR2+0.15,CAR2[0])
    elif t<T_THEFT+0.1: x,z,yw=CAR2[0],CAR2[1],0.0
    elif t<T_BACK: x,z,yw=reverse_out(t,T_THEFT+0.1,T_BACK,CAR2[0])
    else: x,z,yw=leave(t,CAR2[0],T_BACK)
    return dict(pos=(x,z),yaw=yw,dents=2,key=False,sand=False,note=False,lock=False,door=0.0,flash=0.0,police=0.0)
def police_state(t,i):
    """two police cars from the road: arrive from +x skidding, one stops across the lane, one stops behind it"""
    t0=T_POLICE+0.15*i; t1=t0+1.0; xs=(2.0,-3.4)[i]; u=seg01(t,t0,t1); e=1-(1-u)**2
    if t<t0-0.01: return None
    x=lerp((22,-30)[i],xs,e); yw=(-PI/2 if i==0 else PI/2)+(0.28*math.sin(u*PI)*(-1 if i else 1))
    return dict(pos=(x,LANE+0.2*i),yaw=yw,dents=0,key=False,sand=False,note=False,lock=False,door=0.0,flash=0.0,police=1.0 if int(t*10+i)%2 else 0.0)

# ======================= people: states =======================
GARY_A=(0.2,4.4)
def kf(t,keys):
    if t<=keys[0][0]: return dict(keys[0][1])
    for (t0,a),(t1,b) in zip(keys,keys[1:]):
        if t0<=t<=t1:
            u=sm((t-t0)/(t1-t0) if t1>t0 else 1.0); out={}
            for k in a:
                va,vb=a[k],b.get(k,a[k]); out[k]=lerp3(va,vb,u) if isinstance(va,tuple) else lerp(va,vb,u)
            return out
    return dict(keys[-1][1])
def with_walk(t,keys,speed=8.0):
    d=kf(t,keys); d2=kf(t+0.04,keys); mv=math.hypot(d2['x']-d['x'],d2['z']-d['z'])/0.04
    return d,(t*speed if mv>0.08 else 0.0)

def gary_state(t):
    """Gary: A on the sidewalk (frame 0 big, watching the car go), B at the driveway (lock / alarm / keys), window (line 9)"""
    st=dict(mug=False,fob=False,smile=0.0,eyes=1.0,head=0.0,lean=0.0,walk=0.0)
    if t<CUTS[1]:
        d=kf(t,[(0,dict(x=GARY_A[0],z=GARY_A[1],yaw=-0.95,head=0.0,lean=0.0)),(0.9,dict(x=GARY_A[0],z=GARY_A[1],yaw=-0.95,head=0.0,lean=0.02)),
                (we('1',0)-0.2,dict(x=GARY_A[0],z=GARY_A[1],yaw=-0.5,head=0.0,lean=-0.02)),(ws('2',0)+0.2,dict(x=GARY_A[0],z=GARY_A[1],yaw=-0.05,head=0.0,lean=0.0)),
                (T_TICK,dict(x=GARY_A[0],z=GARY_A[1],yaw=0.0,head=0.0,lean=0.0)),(T_TICK+0.5,dict(x=GARY_A[0],z=GARY_A[1],yaw=0.0,head=0.0,lean=0.16))])
        st.update(mug=True,lean=d['lean'],head=d['head'],eyes=1.0 if t<T_TICK else 0.2)
        # sigh: shoulders drop, mug lowers
        sg=sm(seg01(t,T_TICK,T_TICK+0.5)); st['rh']=lerp3((0.22,1.0,0.36),(0.24,0.78,0.3),sg) if t>0.3 else (0.22,1.0,0.36)
        st['head']=0.0; st['smile']=-0.5
        return dict(kind='gary',base=(d['x'],0.0,d['z']),yaw=d['yaw'],**{k:v for k,v in st.items() if k!='head'},head=st['head'])
    if t<CUTS[2]:                                                                                       # driveway: lock, alarm, second car, theft, keys in hand
        gx,gz=-2.75,9.1
        d=kf(t,[(CUTS[1],dict(x=gx,z=gz,yaw=PI/2,lean=0.0)),(T_LOCK-0.5,dict(x=gx,z=gz,yaw=PI/2,lean=0.0)),(T_LOCK-0.15,dict(x=gx,z=gz,yaw=PI/2,lean=0.2)),(T_LOCK+0.4,dict(x=gx,z=gz,yaw=PI/2,lean=0.0))])
        rh=None; lh=None; fob=False
        if T_LOCK-0.45<=t<T_LOCK+0.45: rhw=(-1.35,1.0,9.55)
        else: rhw=None
        if T_ALARM-0.4<=t<T_ALARM+1.0: fob=True; rhw=(gx+0.45,1.35,gz+0.28)
        if t>=T_THEFT+0.4: rhw=(gx+0.26,1.45,gz+0.25); lhw=(gx+0.26,1.38,gz-0.25); fob=False
        else: lhw=None
        sm_=0.0 if t<T_THEFT else -0.6
        base=(gx,0.0,gz); yaw=d['yaw']
        if t>=T_THEFT: yaw=lerp(PI/2,PI,sm(seg01(t,T_THEFT+0.2,T_THEFT+0.7)))
        return dict(kind='gary',base=base,yaw=yaw,mug=False,fob=fob,smile=sm_,lean=d['lean'],rhw=rhw,lhw=lhw if t>=T_THEFT+0.4 else None,eyes=1.0,keys=t>=T_THEFT+0.4)
    if t<CUTS[3]:                                                                                       # leaving keys / sandwich / note
        gx,gz=-2.55,9.15
        lean=0.45*sm(seg01(t,T_KEYS-0.7,T_KEYS-0.15))*(1-sm(seg01(t,T_KEYS+0.3,T_KEYS+0.7)))+0.4*sm(seg01(t,T_SAND-0.6,T_SAND-0.15))*(1-sm(seg01(t,T_SAND+0.3,T_SAND+0.7)))+0.35*sm(seg01(t,T_NOTE-0.6,T_NOTE-0.15))*(1-sm(seg01(t,T_NOTE+0.3,T_NOTE+0.7)))
        yaw=PI/2; rhw=None; lhw=None
        if T_KEYS-0.75<=t<T_KEYS+0.7: rhw=(-1.78,0.94,9.7)
        elif T_SAND-0.75<=t<T_SAND+0.7:
            u=sm(seg01(t,T_SAND-0.75,T_SAND-0.1)); rhw=lerp3((gx+0.4,1.05,gz+0.1),(-0.75,0.7,9.0),u) if t<T_SAND else (-0.75,0.7,9.0)
        elif T_NOTE-0.75<=t<T_NOTE+0.7: rhw=(-1.55,1.22,9.55)
        return dict(kind='gary',base=(gx,0.0,gz),yaw=yaw,mug=False,smile=0.3,lean=lean,rhw=rhw,lhw=lhw,eyes=1.0)
    return dict(kind='gary',base=(-3.6,0.0,13.1),yaw=PI,mug=True,smile=1.0,lean=0.0,eyes=0.0 if int(t*2.3)%9==0 else 1.0,rh=(0.2,1.02,0.34) if t<ws('9',0)+0.6 else (0.12,1.28,0.2))
def sand_held(t):
    return False
DRIVER_SEAT=(-0.45,0.0,-0.3)
def driver_state(t):
    c=car1_state(t)
    if t<T_RET-0.02 or t>=T_EXIT+0.35: pass
    if t<T_RET: return None
    if t<T_EXIT:                                                                                   # seated; the last 0.3 s he climbs out through the open door
        base=np.array([c['pos'][0],0.0,c['pos'][1]])+Ry(c['yaw'])@np.array(DRIVER_SEAT)
        lh=(-0.18,0.85,0.5)
        st=dict(kind='driver',base=tuple(base),yaw=c['yaw'],sit=1.0,rh=(0.18,0.95,0.55),lh=(-0.3,0.96,0.5),lean=0.05+0.02*math.sin(t*3),head=0.0 if t<T0['10'] else 0.12*math.sin((t-T0['10'])*1.4))
        u=sm(seg01(t,T_EXIT-0.3,T_EXIT))
        if u>0:
            tgt=np.array([CAR1[0]-1.55,0.0,CAR1[1]+0.1]); st['base']=tuple(np.array(base)+(tgt-np.array(base))*u); st['yaw']=lerp(c['yaw'],PI+0.15,u); st['sit']=1.0-u; st['rh']=None; st['lh']=None; st['lean']=0.05*(1-u)
        return st
    # out of the car: beside the driver door, slaps the note on the trunk, then runs off to -x
    keys=[(T_EXIT,dict(x=CAR1[0]-1.55,z=CAR1[1]+0.1,yaw=PI+0.15)),(T_EXIT+0.5,dict(x=CAR1[0]-1.75,z=CAR1[1]-1.5,yaw=PI)),
          (T_NOTE2,dict(x=CAR1[0]-0.5,z=CAR1[1]-2.55,yaw=PI)),(T_RUN,dict(x=CAR1[0]-0.5,z=CAR1[1]-2.55,yaw=PI*0.8)),(T_RUN+1.3,dict(x=CAR1[0]-6.2,z=CAR1[1]-5.0,yaw=-PI/2-0.2))]
    d,wk=with_walk(t,keys,speed=11.0)
    run=1.0 if t>=T_RUN else 0.0
    st=dict(kind='driver',base=(d['x'],0.0,d['z']),yaw=d['yaw'],walk=wk*(1.3 if run else 1.0),run=run,lean=0.0)
    if T_NOTE2-0.4<=t<T_NOTE2+0.2: st['rhw']=(d['x']-0.02,1.05,d['z']+0.5) if False else (CAR1[0]-0.5,1.0,CAR1[1]-2.2); st['lean']=0.2
    if T_EXIT+0.6<=t<T_NOTE2-0.4: st['note']=True; st['rh']=(0.25,1.05,0.3)
    return st
def person_model(st): st=dict(st); k=st.pop('kind'); return human(k,st.pop('base'),st.pop('yaw'),**st)
def gary_model(**st): return human('gary',st.pop('base'),st.pop('yaw'),**{k:v for k,v in st.items() if k!='kind'})

# ======================= set =======================
def _grass(i,j): return (70,126,64) if (i+j)%2 else (64,116,58)
def static_world():
    Q=[]
    Q+=box(-120,120,-0.2,0.0,-120,120,(66,120,60))                                                     # ground
    Q+=box(-120,120,0.0,0.02,-2.0,3.5,(52,52,58))                                                      # road
    for x in np.arange(-60,60,3.2): Q+=box(x,x+1.6,0.021,0.03,LANE-0.08,LANE+0.08,(222,206,90))
    Q+=box(-120,120,0.0,0.12,3.5,5.2,(170,168,160))+box(-120,120,0.0,0.12,-2.7,-2.0,(170,168,160))    # kerbs / sidewalks
    Q+=box(-2.7,2.9,0.0,0.03,5.2,12.0,(152,150,142))+box(-2.7,2.9,0.0,0.01,3.5,5.2,(140,138,130))      # driveway
    return Q
def house():
    Q=[]; wall=(238,216,172); wall_d=(214,192,150)
    x0,x1=-4.6,-2.6; y0,y1=0.9,2.3                                                                     # window opening
    Q+=box(-12,x0,0,3.4,12.0,12.4,wall)+box(x1,12,0,3.4,12.0,12.4,wall)+box(x0,x1,0,y0,12.0,12.4,wall)+box(x0,x1,y1,3.4,12.0,12.4,wall)
    Q+=box(x0-0.1,x1+0.1,y0-0.1,y0,11.8,12.5,(250,248,240))+box(x0-0.1,x0,y0,y1,11.9,12.5,(250,248,240))+box(x1,x1+0.1,y0,y1,11.9,12.5,(250,248,240))+box(x0-0.1,x1+0.1,y1,y1+0.1,11.9,12.5,(250,248,240))
    Q+=box(-12,12,3.4,3.6,11.7,13.0,(150,70,60))+box(-12,12,3.6,4.4,12.0,17,(190,86,70))               # roof band + roof
    Q+=box(3.4,4.6,0,2.4,11.9,12.45,(120,74,46))+box(4.3,4.4,1.0,1.15,11.85,11.9,(240,200,80))         # door + handle
    Q+=box(-12,12,0,0.12,17.0,17.4,(30,28,34))                                                         # interior: floor + back walls
    Q+=box(-12,12,0,0.05,12.4,17.0,(122,84,62))+box(-12,12,0.05,3.4,17.0,17.4,(216,196,160))+box(-12,-11.6,0.05,3.4,12.4,17.0,(216,196,160))+box(11.6,12,0.05,3.4,12.4,17.0,(216,196,160))
    Q+=box(-12,12,3.38,3.4,12.4,17.0,(200,190,170))
    Q+=box(-5.2,-2.0,0.05,0.6,16.2,17.0,(96,62,48))+box(-4.9,-4.6,0.6,1.5,16.9,16.95,(240,220,150),emit=True)   # sofa + warm picture
    Q+=box(-3.2,-3.0,2.6,3.4,13.0,13.04,(240,236,200),emit=True)                                       # ceiling lamp
    Q+=box(x0+0.05,x0+0.4,y0,y1,12.4,12.55,(180,60,70))+box(x1-0.4,x1-0.05,y0,y1,12.4,12.55,(180,60,70))   # curtains
    Q+=box(-0.6,0.6,0,1.0,12.4,12.4,(0,0,0))
    # mailbox
    Q+=box(3.2,3.25,0,1.1,6.0,6.05,(90,60,40))+box(3.05,3.4,1.1,1.4,5.95,6.4,(200,40,40))
    return Q
def palm(x,z,h=4.2,k=0):
    Q=[]; tr=(120,86,56)
    for i in range(4):
        y0=h*i/4; y1=h*(i+1)/4; w=0.18-0.025*i; ox=0.1*i*(1 if k%2 else -1)
        Q+=box(x+ox-w,x+ox+w,y0,y1,z-w,z+w,tr if i%2 else (104,72,46))
    top=(x+0.3*(1 if k%2 else -1),h,z)
    for a in range(7):
        ang=a*2*PI/7+k; ex=top[0]+1.5*math.cos(ang); ez=top[2]+1.5*math.sin(ang); ey=h-0.7
        px=-math.sin(ang)*0.35; pz=math.cos(ang)*0.35
        Q.append(quad([(top[0],h,top[2]),(top[0]+px*0.4+0.6*math.cos(ang),h+0.25,top[2]+pz*0.4+0.6*math.sin(ang)),(ex,ey,ez),(top[0]-px*0.4+0.6*math.cos(ang),h+0.25,top[2]-pz*0.4+0.6*math.sin(ang)),],(52,150,70) if a%2 else (40,128,58)))
    return Q
def lamp(x,z):
    return box(x-0.05,x+0.05,0,4.6,z-0.05,z+0.05,(70,70,76))+box(x-0.05,x+0.6,4.55,4.65,z-0.05,z+0.05,(70,70,76))
def lamp_glow(x,z,on):
    c=(255,226,150) if on>0.2 else (190,190,170); return box(x+0.35,x+0.65,4.4,4.52,z-0.15,z+0.15,c,emit=True)
def town():
    Q=[]
    for k,x in enumerate((-17,-10,6.5,14)): Q+=palm(x,5.0 if k%2==0 else 4.6,4.4+0.4*(k%2),k)
    Q+=palm(-9,7.5,3.8,5)+palm(8.5,7.0,4.0,6)
    for x in (-20,-6,10,24): Q+=lamp(x,3.9)
    # neighbours' houses + far skyline + parked cars along the kerb
    for k,(x0,x1,h,c) in enumerate(((-40,-13,3.6,(220,200,170)),(13,40,3.4,(190,210,220)),(-90,-45,6,(190,170,200)),(44,90,5.5,(200,180,170)))):
        Q+=box(x0,x1,0,h,12.0,12.4,c)+box(x0,x1,h,h+0.2,11.8,12.6,(140,70,60))
        for xx in np.arange(x0+2,x1-2,5.0): Q+=box(xx,xx+1.4,1.1,2.2,11.95,12.0,(60,80,110))
    for k,(x0,x1,h,c) in enumerate(((-70,-50,14,(64,70,96)),(-48,-34,22,(78,84,112)),(-33,-20,11,(70,76,100)),(22,34,18,(70,76,104)),(36,52,26,(84,90,118)),(54,72,12,(66,72,98)))):
        Q+=box(x0,x1,0,h,-34,-30,c)
        for yy in np.arange(2,h-1,2.4):
            for xx in np.arange(x0+1.5,x1-1,3.0): Q+=box(xx,xx+1.0,yy,yy+0.9,-30.05,-30.0,(240,214,140) if (int(xx*3+yy*5))%3 else (70,80,110),emit=True)
    return Q
def parked(x,col,yaw=0.0):
    c=car((x,-1.3),yaw+PI/2,col); return c
def sky(t):
    sn=sun(t); top=lerp3((96,150,226),(112,72,130),sn); hor=lerp3((196,222,244),(255,166,92),sn); Q=[]
    bands=6
    def wallq(fix_axis,fix,ext=130):
        out=[]
        for i in range(bands):
            y0=i*14; y1=(i+1)*14; u=(i+0.5)/bands; c=lerp3(hor,top,u**0.9)
            if fix_axis=='z': out.append(quad([(-ext,y0,fix),(ext,y0,fix),(ext,y1,fix),(-ext,y1,fix)],tuple(int(v) for v in c),emit=True))
            else: out.append(quad([(fix,y0,-ext),(fix,y0,ext),(fix,y1,ext),(fix,y1,-ext)],tuple(int(v) for v in c),emit=True))
        return out
    Q+=wallq('z',110)+wallq('z',-110)+wallq('x',110)+wallq('x',-110)
    if sn>0.15:                                                                                       # sunset sun on the horizon (+x, far)
        Q+=[quad([(109,3,-18),(109,3,-6),(109,15,-6),(109,15,-18)],(255,224,150),emit=True)]
    return Q,tuple(int(v) for v in hor)
def sun(t): return seg01(t,T0['5']+0.5,T0['8']+1.2)
def lights(t):
    sn=sun(t); wc=lerp3((255,246,226),(255,150,84),sn); L=[((8.0,14.0,0.0),wc,16.0*(1-0.35*sn)),((-6.0,9.0,6.0),lerp3((255,240,220),(255,160,100),sn),9.0*(1-0.3*sn))]
    L.append(((-3.6,2.4,14.0),(255,214,150),0.9+0.5*sn))
    if t>=T_POLICE:
        ph=(t*5)%2; L.append(((1.5,2.2,3.0),(255,40,30) if ph<1 else (30,40,255),6.0)); L.append(((-3.0,2.2,3.0),(30,40,255) if ph<1 else (255,40,30),5.0))
    return L

STATIC=[static_world()+house(),town()]
PARKED=[parked(x,c) for x,c in ((-14,(80,160,100)),(-5.5,(220,200,70)),(11,(150,90,180)))]
LAMPG=lambda t: sum([lamp_glow(x,3.9,sun(t)-0.5) for x in (-20,-6,10,24)],[])

# ======================= cameras =======================
CAM_NOW=[]
def creep(t,t0,rate=0.0014): return motion.creep(t,t0,rate,FPS)
def cam_shot(t):
    if t<CUTS[1]:   # A: close on Gary, big and moving (frame 0)
        tgt=(-0.4,1.28,4.4); u=sm(seg01(t,0.0,1.2)); p=lerp3((0.5,1.5,6.0),(0.2,1.45,6.6),u)
        return dict(cam=motion.dolly(p,tgt,creep(t,0.0,0.0012)),tgt=tgt,fov=58)
    if t<CUTS[2]:   # B: driveway wide from the street corner (lock / alarm / second car / theft)
        tgt=(-1.1,1.0,9.4); return dict(cam=motion.dolly((-4.7,2.3,4.9),tgt,creep(t,CUTS[1],0.0010)),tgt=tgt,fov=60)
    if t<CUTS[3]:   # B': closer at the open driver door (keys / sandwich / note); the sandwich + note beats push in
        u=sm(seg01(t,T_SAND-0.4,T_SAND+0.4)); tgt=lerp3((-2.0,1.0,9.4),(-1.6,0.9,9.3),u); p=lerp3((-3.4,2.9,4.4),(-3.0,2.5,5.2),u)
        return dict(cam=motion.dolly(p,tgt,creep(t,CUTS[2],0.0012)),tgt=tgt,fov=52)
    if t<CUTS[4]:   # C: sunset wide, the car comes back
        u=sm(seg01(t,T_FULL-0.4,T_DENT+0.3)); tgt=lerp3((-1.6,1.15,5.2),(-1.3,1.0,9.3),u); p=lerp3((2.6,1.35,-0.9),(-0.2,1.7,3.6),u)
        return dict(cam=motion.dolly(p,tgt,creep(t,CUTS[3],0.0006)),tgt=tgt,fov=lerp(58,46,u))
    if t<CUTS[5]:   # D: window, Gary + mug (outside, slightly low, pushes in)
        tgt=(-3.65,1.45,12.4); return dict(cam=motion.dolly((-5.0,1.5,9.0),tgt,creep(t,CUTS[4],0.0016)),tgt=tgt,fov=38)
    if t<CUTS[6]:   # E1: street, the driver's back from behind, wanted stars
        tgt=(-1.5,1.05,9.0); return dict(cam=motion.dolly((-0.3,2.35,3.4),tgt,creep(t,CUTS[5],0.0012)),tgt=tgt,fov=46)
    # E2: wide from across the street: police cross the road, the driver sprints off to the left
    tgt=(-0.8,1.0,6.0); return dict(cam=motion.dolly((0.4,2.7,-2.2),tgt,creep(t,CUTS[6],0.0008)),tgt=tgt,fov=64)
def shake_px(t):
    for tt in (T_CAR2+0.15,T_DENT,T_FULL-0.1):
        k=motion.kick(t,tt,2.0,6,FPS)
        if k: return (0.0,k)
    return (0.0,0.0)

# ======================= render =======================
RND=Renderer(W,H,fog=(196,222,244))
SMOKE=[]
def smoke(t):
    Q=[]
    if t<CUTS[1]:
        x0=_path_dims(CAR1[0])['xc']-1.7
        for i in range(6):
            ts=0.1+0.12*i
            if t<ts or t-ts>0.9: continue
            age=t-ts; d=0.5*7.0*(ts**2)+0.5*ts; x=x0-d; r=0.18+0.35*age
            Q+=box(x-r,x+r,0.0,r*1.3,LANE-0.4-r*0.6,LANE-0.4+r*0.6,(215,215,220) if age<0.5 else (190,190,196))
    return Q
def render3d(t):
    sh=cam_shot(t); cam=Camera.look(sh['cam'],sh['tgt']); CAM_NOW[:]=[sh['cam']]
    skyQ,hor=sky(t); RND.fog=hor
    layers=list(STATIC)+[skyQ]+PARKED
    c1=car1_state(t); c2=car2_state(t)
    def cmod(cs,col): return car((cs['pos'][0],0.0,cs['pos'][1]),cs['yaw'],col,**{k:v for k,v in cs.items() if k not in('pos','yaw')})
    layers.append(cmod(c1,RC[0]))
    if c2: layers.append(cmod(c2,RC[1]))
    for i in (0,1):
        ps=police_state(t,i)
        if ps: layers.append(car((ps['pos'][0],0.0,ps['pos'][1]),ps['yaw'],(30,30,38),police=ps['police']) )
    layers.append(smoke(t)); layers.append(LAMPG(t))
    gs=gary_state(t); layers.append(FB.prelit(person_model(gs),sh['cam'],warm=0.12))
    ds=driver_state(t)
    if ds:
        D=person_model(ds); layers.append(FB.prelit(D,sh['cam'],warm=0.12))
    layers+=layers_extra(t)
    img,vi,zb=zrender(RND,cam,layers,lights(t),fov=sh['fov'],fog_start=30,fog_end=120,ambient=0.7-0.18*sun(t),shake=shake_px(t),return_z=True)
    return post.ps1(img),vi,cam,sh['fov']
def layers_extra(t):
    L=[]
    if t>=T_NOTE2:                                                                                     # THANKS GARY note on the trunk lid
        x,z=CAR1[0],CAR1[1]-1.7; L+=box(x-0.3,x+0.3,0.915,0.93,z-0.2,z+0.2,(252,248,205),emit=True)
    return [L] if L else []

# ======================= HUD / UI =======================
def otext(d,s,x,y,col,sc=1):
    o=max(1,sc//2)
    for ox,oy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)): font.text(d,s,x+ox*o,y+oy*o,(0,0,0),sc,None)
    font.text(d,s,x,y,col,sc,None)
def ctext(d,s,y,col,sc=1): otext(d,s,(W-font.width(s,sc))//2,y,col,sc)
def star5(d,cx,cy,r,col,outline=(255,255,255)):
    pts=[]
    for k in range(10):
        a=-PI/2+k*PI/5; rr=r if k%2==0 else r*0.45; pts.append((cx+rr*math.cos(a),cy+rr*math.sin(a)))
    d.polygon(pts,fill=col,outline=outline)
def hud(d,t):
    if 0.08<=t<we('1',0)+0.35:
        on=int(t*6)%2==0 or t<0.6; w=font.width('VEHICLE STOLEN',2)+8; x0=(W-w)//2
        d.rectangle([x0,8,x0+w,28],fill=(150,10,16) if on else (60,8,12),outline=(0,0,0)); ctext(d,'VEHICLE STOLEN',13,WHT,2)
    if T0['2']<=t<T0['3']-0.05:
        n=900 if t>=T_TICK else 899; col=YEL if t<T_TICK+0.5 and int(t*12)%2==0 else WHT
        ctext(d,'STOLEN:',12,WHT,1); ctext(d,str(n),22,col if t>=T_TICK else WHT,3)
    if T_NOTE<=t<T0['8']+0.2: ctext(d,'BRING HER BACK BY 6',22,YEL,1); ctext(d,'THE NOTE:',12,WHT,1)
    if T_FULL<=t<T0['9']-0.1: ctext(d,'FUEL: FULL',16,GRN,2)
    if T_FULL<=t<T0['9']-0.1 and t>=T_DENT: ctext(d,'4 NEW DENTS',34,RED,1)
    if t>=T0['10']-0.05:
        for i in range(5):
            lit=t>=T_STAR0+0.3*i; blink=(int(t*5)%2==0) if t>=T_STAR0+1.6 else True
            star5(d,W//2-32+i*16,14,6,(YEL if blink else (176,128,24)) if lit else (50,50,60),outline=WHT if not lit else (0,0,0))
        if t<T_STAR0+1.8: ctext(d,'WANTED',26,RED,1)
    if t>=T_NOTE2+0.1 and t<DUR+1:
        w=font.width('THANKS GARY',2)+10; x0=(W-w)//2; y0=126; ang=int(t*8)%2
        d.rectangle([x0,y0,x0+w,y0+19],fill=(252,248,205),outline=(0,0,0)); font.text(d,'THANKS GARY',x0+5,y0+5,(30,40,120),2,None)

# ======================= subtitles =======================
SUB_F=7.5; HIL={'GUY','STEAL?','NINE','HUNDRED','LOCK.','ALARM.','CAR.','TOO.','KEYS','SANDWICH','NOTE:','SIX.','BACK.','DENTS.','NEVER','NICEST','DISAGREES.'}
def _rows(text,n=20):
    out=[]; c=[]
    for w_ in text.split():
        if len(' '.join(c+[w_]))>n and c: out.append(c); c=[w_]
        else: c.append(w_)
    return out+[c]
def _subs():
    res=[]
    for k,t0 in LINES:
        for i,(a,b,tx) in enumerate(SCR['sent'][k]):
            nxt=SCR['sent'][k][i+1][0] if i+1<len(SCR['sent'][k]) else b+0.25
            res.append((t0+a-0.03,t0+nxt-0.02,_rows(tx.replace('...','..')),k))
    return res
SUBS=_subs()
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
                    col=YEL if wd.upper().strip(',') in HIL else WHT; font.check(wd)
                    for k_,ch in enumerate(wd.upper()):
                        for j,row in enumerate(font.FONT[ch]):
                            for i2,bit in enumerate(row):
                                if bit=='1':
                                    X=x+(k_*6+i2)*sc; Y=y0+pad+i*lh+j*sc; bx=[round(X),round(Y),round(X+sc)-1,round(Y+sc)-1]; do.rectangle(bx,fill=col); dm.rectangle(bx,fill=255)
                    x+=font.width(wd,sc)+6*sc
            return ov,m
    return None
def frame_low(t):
    img,vi,cam,fov=render3d(t); d=ImageDraw.Draw(img); hud(d,t)
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
    return out
def _gst(t): return gary_state(t)
def _dst(t):
    d=driver_state(t)            # seated in the moving car = rigid with the car, not tracked as a walker
    return d if (d and t>=T_EXIT-0.3) else dict(kind='driver',base=(40,0,40),yaw=0.0)    # one known false positive at T_EXIT-0.3: the QA stand-in jumps to the seat
QA=dict(fps=FPS,dur=DUR,W=W,frame=frame,
    chars={'gary':(_gst,lambda **st: person_model(st),'none','none'),'driver':(_dst,lambda **st: person_model(st),'none','none')},
    geom=_geom,camera=lambda t: cam_shot(t)['cam'],min_cam_dist=0.4,camera_ok=lambda p: -60<p[0]<60 and -5<p[2]<18 and 0.2<p[1]<6,
    allow_jump=[(w,f/FPS) for w in ('gary','driver') for c in CUTS+[x/FPS for x in range(int(T_RET*FPS),int(T_FULL*FPS))] for f in range(int(c*FPS)-2,int(c*FPS)+4)],
    weapon_events=[],
    scenes=[dict(id=f's{i}',t0=CUTS[i],t1=CUTS[i+1],action=a) for i,a in enumerate((
        'hook: Gary on the sidewalk, his car screeches away, VEHICLE STOLEN, counter 899 -> 900 (CAM A)',
        'lock, alarm, second car, both stolen, Gary holds two key sets (CAM B)',
        'keys in the ignition, sandwich, note (CAM B2)',
        'sunset: the car comes back dented, FUEL: FULL (CAM C)',
        'Gary at the window with his mug (CAM D)',
        'the driver from behind, five wanted stars (CAM E1)',
        'THANKS GARY note, police lights, the driver sprints off (CAM E2)'))],
    texts=lambda: [('hud','VEHICLE STOLEN',2),('hud','STOLEN:',1),('hud','BRING HER BACK BY 6',1),('hud','FUEL: FULL',2),('hud','4 NEW DENTS',1),('hud','THANKS GARY',2),('hud','WANTED',1)])

# ======================= AUDIO =======================
def hsh_(i): v=math.sin(i*127.1)*43758.5453; return v-math.floor(v)
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=21); sr=s.sr; n=s.n; t=s.t; BED=np.zeros(n); FX=np.zeros(n)
    def put(buf,x,t0,v=1.0):
        i=int(t0*sr)
        if i>=n or i<0: return
        j=min(n,i+len(x)); buf[i:j]+=(x*v)[:j-i]
    def nb(t0,d,lo,hi,v,seed,shape=2): put(FX,s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v)
    def tone(t0,m,d,v,wave='sq',duty=0.5,dec=3.0,att=0.005,glide=0.0):
        f=440*2**((m-69)/12); tt=s.T(d); fr=f*(1+glide*tt/d); ph=np.cumsum(fr)/sr%1
        x=np.where(ph<duty,1.0,-1.0) if wave=='sq' else (4*np.abs(ph-0.5)-1 if wave=='tri' else np.sin(2*np.pi*ph))
        put(FX,x*np.minimum(1,tt/att)*np.exp(-tt*dec),t0,v)
    def thud(t0,f=60,v=0.3,d=0.5):
        tt=s.T(d); put(FX,np.sin(2*np.pi*f*tt*(1-0.3*tt/d))*np.exp(-tt*9)+s.filt_short(s.noise(d,int(t0*13)),lo=60,hi=800)*np.exp(-tt*14)*0.5,t0,v)
    def clunk(t0,v=0.15,seed=0):
        tt=s.T(0.3); put(FX,sum(np.sin(2*np.pi*f*tt)*np.exp(-tt*k) for f,k in ((260,14),(690,20),(1400,30)))*0.4+s.filt_short(s.noise(0.3,seed),lo=900,hi=5000)*np.exp(-tt*40),t0,v)
    def step(t0,v=0.04,seed=0):
        tt=s.T(0.12); put(FX,s.filt_short(s.noise(0.12,seed),lo=700,hi=4000)*np.exp(-tt*40),t0,v)
    def screech(t0,d,v,seed):
        tt=s.T(d); f=1500+500*np.sin(tt*9); ph=np.cumsum(f)/sr; x=(np.sin(2*np.pi*ph)+0.5*np.sin(4*np.pi*ph))*0.5+s.filt_short(s.noise(d,seed),lo=1500,hi=6000)*0.6
        put(FX,x*np.minimum(1,tt/0.04)*np.exp(-tt*(2.2/d)),t0,v)
    def engine(t0,d,f0,f1,v):
        tt=s.T(d); f=f0+(f1-f0)*(tt/d); ph=np.cumsum(f)/sr%1; x=(2*ph-1)*0.6+np.sign(np.sin(2*np.pi*ph*2))*0.25
        put(FX,s.filt_short(x,lo=60,hi=900)*np.minimum(1,tt/0.08)*np.minimum(1,(d-tt)/0.2),t0,v)
    def siren(t0,d,v,f0=640,f1=980):
        tt=s.T(d); f=f0+(f1-f0)*(0.5+0.5*np.sin(2*np.pi*1.3*tt)); ph=np.cumsum(f)/sr; x=np.sin(2*np.pi*ph)+0.3*np.sin(4*np.pi*ph)
        put(FX,x*np.minimum(1,tt/0.2)*np.minimum(1,(d-tt)/0.1),t0,v)
    def chirp(t0,v=0.03,f=3200):
        tt=s.T(0.09); put(FX,np.sin(2*np.pi*f*tt*(1+0.4*tt/0.09))*np.exp(-tt*28),t0,v)
    # ---- bed: street air + low hum; evening birds late
    BED+=s.filt(s.rng.normal(0,1,n),lo=80,hi=900)*0.05*(1+0.3*np.sin(2*np.pi*0.2*t))
    BED+=np.sin(2*np.pi*110*t)*0.012
    for k in range(10):
        tb=T0['8']+0.2+k*0.5+0.2*hsh_(k)
        if tb<DUR-0.5: chirp(tb,0.025,2600+300*(k%4))
    for k in range(int(T0['3']/0.55)): nb(0.1+k*0.55,0.25,200,1600,0.015,700+k,2)                    # distant traffic
    # ---- hook: tyre screech + engine pulling away, counter tick
    screech(0.0,1.1,0.10,11); engine(0.0,1.8,90,260,0.20); thud(0.02,70,0.15)
    tone(T_TICK,84,0.12,0.06,'sq',dec=25); tone(T_TICK+0.06,91,0.2,0.06,'sq',dec=18)
    # ---- lock clunk, alarm chirps, second car arrives, both stolen
    clunk(T_LOCK,0.2,5); clunk(T_LOCK+0.12,0.1,6)
    for k in range(4): tone(T_ALARM+k*0.125,100,0.07,0.05,'sq',duty=0.5,dec=20)
    engine(T_CAR2-1.0,1.1,70,150,0.12); thud(T_CAR2+0.1,50,0.1)
    screech(T_THEFT,0.8,0.09,12); engine(T_THEFT,1.6,80,300,0.2); screech(T_THEFT+0.1,0.7,0.07,13)
    # ---- keys / sandwich / note
    clunk(T_KEYS-0.3,0.12,21); tone(T_KEYS,96,0.3,0.04,'sin',dec=9)
    nb(T_SAND-0.15,0.25,500,4000,0.05,22,2); thud(T_SAND+0.05,100,0.05,0.2)
    nb(T_NOTE-0.2,0.35,2000,8000,0.06,23,2)                                                           # paper rustle
    # ---- the car comes back: engine, tyre scrub, FULL ping, dent clunks, idle
    engine(T_RET-0.3,2.2,120,70,0.14); nb(T_RET+0.5,0.6,300,2500,0.05,24,2)
    tone(T_FULL,76,0.25,0.04,'sin',dec=7); tone(T_FULL+0.08,83,0.3,0.04,'sin',dec=7)
    for k in range(3): clunk(T_DENT+0.06*k,0.2-0.04*k,30+k)
    thud(T_DENT+0.02,55,0.25,0.4)
    for k in range(int(max(0,T0['9']-T_FULL-0.4)/0.35)): thud(T_FULL+0.4+k*0.35,58,0.03,0.3)          # engine idle
    # ---- window: mug sip + a content sigh
    nb(ws('9',0)+0.7,0.3,300,1800,0.04,40,2); tone(ws('9',0)+1.0,70,0.5,0.025,'sin',dec=3,glide=-0.1)
    # ---- stars: pings, then the police
    for k in range(5): tone(T_STAR0+0.3*k,81+2*k,0.25,0.045,'sq',duty=0.25,dec=10)
    siren(T_POLICE,2.7,0.045); siren(T_POLICE+0.35,2.4,0.04,700,1040)
    for k in range(2): engine(T_POLICE+0.1*k,1.2,180,300,0.1); screech(T_POLICE+0.7+0.15*k,0.6,0.06,50+k)
    clunk(T_NOTE2,0.1,60); nb(T_NOTE2-0.1,0.2,2500,8000,0.04,61,2)
    for k in range(8): step(T_RUN+k*0.1,0.05,70+k)
    # ---- voice
    NB=np.zeros(n); wins=[]
    for k_,t0 in LINES:
        a,ar=_sf.read(os.path.join(TTS_DIR,'sc',f'{k_}.wav')); a=a if a.ndim==1 else a.mean(1)
        a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a); put(NB,a,t0); wins.append((t0,t0+len(a)/sr))
    g=duck_envelope(n,sr,wins,-6.0,0.05,0.25); bed=BED*g; fx=FX*(0.55+0.45*g)
    L=bed+fx; R_=np.roll(bed,700)+np.roll(fx,200); pk=max(np.abs(L).max(),np.abs(R_).max()); gv=pk*1.6/np.abs(NB).max()
    s.L=L+NB*gv; s.R=R_+NB*gv; s.reverb(0.1,length=1.0,decay=3.0)
    end=np.clip((DUR-t)/0.04,0,1); s.L*=end; s.R*=end
    return s.save(path,peak=0.9)
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'stolen_car.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'sc_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.96,vignette=0.25,grain=1.5,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(frame_final(f/FPS),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
