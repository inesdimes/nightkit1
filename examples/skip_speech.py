"""WHY DO FINAL BOSSES GIVE A SPEECH BEFORE THE FIGHT? (Insert Disc 2, 14-day test day 1, 22:00 slot) ~39 s PS1 comedy, 9:16, nightkit.
Brief: briefs/skip_speech.md. The boss wrote his speech 30 years ago; every hero presses SKIP; one knight listens for 11 minutes and claps;
the boss is too happy to dodge and loses in one hit.
Reuses: locked boss + knight + arena (examples/final_boss.py; heroes = knight with recoloured cape/plume only).
NEW: scroll (strip from the boss's left hand to the floor), boss cape (accessory layer, flips), candles, happy ^ ^ eyes,
HUD: PRESS X TO SKIP, REHEARSAL / SKIPPED counters, speech timer, VICTORY, +1 FAN.
Voice: python tools/tts/ss.py src ; <chatterbox python> tools/tts/vc.py ss ; python tools/tts/ss.py build vc  -> $TTS_DIR/ss/
Run: TEST=1,5,9 python examples/skip_speech.py -> test.png | PART=a:b | PART=audio | tools/render_parts.py --prefix ss --audio skip_speech.wav"""
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
box=FB.box; xform=FB.xform
WHT=(242,238,226); YEL=(255,210,60); RED=(240,50,40); GRN=(80,220,90); GRAY=(150,150,160); GOLD=(236,190,60); BLU=(110,170,255); PINK=(255,120,170)

# ======================= voice timings (tools/tts/ss.py) =======================
SCR=json.load(open(os.path.join(TTS_DIR,'ss','script.json')))
GAP=0.3; EXTRA={'3':0.1,'4':0.75,'5':0.25,'6':0.6,'7':0.1,'8':1.9,'9':0.3,'10':0.35}
def _lines():
    t=0.12; out=[]
    for k in [str(i) for i in range(1,12)]: out.append((k,round(t,3))); t+=SCR['dur'][k]+GAP+EXTRA.get(k,0.0)
    return out,t-GAP
LINES,_vend=_lines(); T0=dict(LINES)
DUR=round(T0['11']+SCR['dur']['11']+0.55,2); N=int(round(DUR*FPS))
def ws(k,i): return T0[k]+SCR['sent'][k][i][0]
def we(k,i): return T0[k]+SCR['sent'][k][i][1]
LEAD=2*F

# ======================= story events =======================
SKIP=[ws('4',1)+0.52-LEAD, ws('5',0)+0.72-LEAD, ws('5',1)+0.42-LEAD]     # the three heroes press X ("skip", "next", "next")
FLASH=[s+0.24 for s in SKIP]                                          # fight flash right after each skip
T_STILL=ws('6',1)                                                     # the listener does not press anything
T_FADE=(T_STILL+0.2,we('6',1)+0.45)                                   # the skip prompt fades out
T_FROZE=ws('7',0)+0.25-LEAD
T_TL=(ws('8',0)+0.25, T0['9']-0.25)                                   # time-lapse: candles burn down, timer 00:00 -> 11:02
T_SIT=(ws('8',0)+0.05, ws('8',0)+0.55)
T_STAND=(T0['9']+0.05, T0['9']+0.6)
T_CLAP=(we('9',0)-0.5, T0['10']+0.15)
T_BOW=(we('9',0)-0.45, we('9',0)+0.25)
T_DRAW=(T0['10']+0.1, T0['10']+0.45)                                  # knight draws his sword
T_WALK=(T0['10']+0.35, ws('10',1)+0.45)
T_HIT=ws('10',1)+1.02-LEAD                                            # "dodge"
T_FAN=ws('11',1)-0.1
KN_STOP=6.0; KN_HIT_Z=8.45
BOSS_B=(0.0,0.0,10.0)
CUTS=[0.0,T0['3']-0.08,T0['4']-0.08,T0['5']-0.03,ws('5',1)-0.03,T0['6']-0.05,ws('6',1)-0.1,T0['7']-0.08,T0['8']-0.08,T0['10']-0.08,DUR]

# ======================= LOCKED ASSET: hero variants (the locked knight, cape + plume colours only) =======================
HERO_COL={'orange':{FB.CAPE:(214,112,30),FB.CAPE_D:(160,80,22),FB.PLUME:(240,150,40)},
          'green':{FB.CAPE:(40,150,70),FB.CAPE_D:(28,108,50),FB.PLUME:(70,200,90)},
          'purple':{FB.CAPE:(128,56,170),FB.CAPE_D:(92,40,128),FB.PLUME:(170,90,220)},
          'blue':{}}
def hero(col,**st):
    Q=FB.knight(**st)
    for q in Q:
        c=HERO_COL[col].get(tuple(q['col']))
        if c: q['col']=c
    return Q

# ======================= boss: locked model + NEW accessories (cape, happy eyes, scroll) =======================
CAPE_B=(92,18,28); CAPE_BD=(66,13,21)
def bT(st,p):
    """boss torso-local point -> world (same transform as FB.boss, before the fall)"""
    piv=np.array([0,1.55,0]); q=piv+FB.Rx(st.get('lean',0.0))@(np.array(p,float)-piv); return np.array(st['base'],float)+FB.Ry(st['yaw'])@q
def bH(st,p):
    hy=np.array([0,2.9,0]); return bT(st,hy+FB.Ry(st.get('head',0.0))@(np.array(p,float)-hy))
def dq(pts,col,emit=False):
    return [quad([tuple(p) for p in pts],col,emit),quad([tuple(p) for p in pts[::-1]],col,emit)]
def boss_cape(st,flip):
    """cape behind the shoulders (behind the sword on the back); flip 0..1..0 swings the hem up and out"""
    th=2.1*math.sin(PI*min(1.0,flip)) if flip>0 else 0.0; side=0.7*math.sin(PI*min(1.0,flip))
    top=[np.array([-0.66,2.84,-0.56]),np.array([0.66,2.84,-0.56])]
    Q=[]
    v0=np.array([0,-2.45,-0.22]); v=FB.Rx(-th)@v0
    bot=[np.array([-0.88+side,0,0])+top[0]+v+np.array([0,0,-0.02]),np.array([0.88+side,0,0])+top[1]+v+np.array([0,0,-0.02])]
    mid=[(top[i]+bot[i])/2+np.array([0.0,0.0,-0.1-0.15*math.sin(th)]) for i in range(2)]
    for a,b,c in ((top,mid,CAPE_B),(mid,bot,CAPE_BD)):
        Q+=dq([bT(st,a[0]),bT(st,a[1]),bT(st,b[1]),bT(st,b[0])],c)
    return Q
def happy_eyes(st):
    Q=[]
    for sx in (-1,1):
        cx=sx*0.16
        for a,b in (((cx-0.13,3.0,0.37),(cx,3.2,0.37)),((cx,3.2,0.37),(cx+0.13,3.0,0.37))):
            Q+=FB.seg(bH(st,a),bH(st,b),0.075,(255,200,90),0.03,emit=True)
    return Q
def fall_xf(Q,st,a):
    if a<=0: return Q
    Rb=FB.Ry(st['yaw']); Rf=Rb@FB.Rx(-1.5*a)@Rb.T; piv=np.array(st['base'],float)+Rb@np.array([0,0,-0.2])
    Q=xform(Q,lambda p:tuple(piv+Rf@(np.array(p,float)-piv)))
    ymin=min(v[1] for q in Q for v in q['p'])
    if ymin<0.01: Q=xform(Q,lambda p:(p[0],p[1]-ymin+0.01,p[2]))
    return Q
def bmodel(base,yaw,rh,lh,lean=0.0,head=0.0,eyes=1.0,happy=0.0,flip=0.0,fall=0.0,**_):
    st=dict(base=base,yaw=yaw,lean=lean,head=head)
    Q=FB.boss(base,yaw,rh=rh,lh=lh,lean=lean,head=head,sword='back',eyes=0.0 if happy>0.5 else eyes)
    Q+=boss_cape(st,flip)
    if happy>0.5: Q+=happy_eyes(st)
    return fall_xf(Q,st,fall)

# ----- boss poses (torso-local hand targets; forward = +z) -----
R_REST=(0.92,1.55,0.2); L_SCROLL=(-0.78,2.05,0.78); R_UP=(1.02,3.85,0.55); R_OPEN=(1.55,2.55,0.7); R_CHEST=(0.38,2.55,0.62)
L_OPEN=(-1.55,2.55,0.7); R_POINT=(0.7,2.9,1.2)
def speaking(t,ph=0.0,fast=1.0):
    """talking gestures: the right hand moves between raised, open and pointing; small head turns"""
    u=0.5+0.5*math.sin((t+ph)*2.3*fast); v=0.5+0.5*math.sin((t+ph)*3.7*fast+1.0)
    rh=lerp3(lerp3(R_OPEN,R_UP,u),R_POINT,0.4*v)
    return rh,0.12*math.sin((t+ph)*1.7*fast),0.04*math.sin((t+ph)*2.9*fast)
def bstate(t):
    d=dict(base=BOSS_B,yaw=PI,lh=L_SCROLL,eyes=1.0,happy=0.0,flip=0.0,fall=0.0,lean=0.0,head=0.0)
    rh,hd,ln=speaking(t); d.update(rh=rh,head=hd,lean=ln)
    if t<T0['3']:                                             # line 1-2: mid-speech, scroll unrolling
        pass
    elif t<CUTS[2]:                                           # line 3: rehearsal
        if ws('3',1)-0.05<=t<ws('3',2):                        # "Pauses." arm raised, frozen
            d.update(rh=R_UP,head=0.0,lean=0.0)
        elif ws('3',2)<=t<ws('3',3):                           # "Hand gestures." quick flourishes
            rh,hd,ln=speaking(t,0.0,2.6); d.update(rh=rh,head=hd,lean=ln)
        elif t>=ws('3',3):                                     # "A dramatic cape flip."
            f=seg01(t,ws('3',3)+0.45,ws('3',3)+1.25); d['flip']=f; d['rh']=lerp3(R_CHEST,R_OPEN,sm(f*2)); d['head']=0.0
    else:
        # skip montage: speaks, freezes on the skip, lies on the floor after the flash (until the next hero)
        for i,s in enumerate(SKIP):
            end=CUTS[3+i]
            if CUTS[2+i]<=t<end:
                if t>=s:
                    k=seg01(t,s,s+0.2); d.update(rh=lerp3(d['rh'],R_UP,1.0),head=0.0,lean=0.0)
                if t>=FLASH[i]: d.update(fall=1.0,happy=0.0,eyes=0.3)
        if t>=CUTS[5]:                                         # the listener
            if t>=T_FROZE and t<T0['8']:                       # froze: arm stuck in the air, eyes flicker
                d.update(rh=(0.95,3.4,0.75),head=0.0,lean=0.0)
                if t<T_FROZE+0.6: d['eyes']=1.0 if int((t-T_FROZE)*14)%2==0 else 0.15
                if t>=ws('7',1)+0.2:                           # looks down at the scroll: the second sentence
                    u=sm(seg01(t,ws('7',1)+0.2,ws('7',1)+0.8)); d.update(rh=lerp3((0.95,3.4,0.75),R_CHEST,u),lean=0.14*u)
            if T0['8']<=t<T_TL[1]+0.1:                         # time-lapse: wild gestures, cape flips
                fast=1.0+3.0*sm(seg01(t,T_TL[0],T_TL[0]+0.4))
                rh,hd,ln=speaking(t,0.0,fast); d.update(rh=rh,head=hd*1.6,lean=ln*2.0)
                if t>=T_TL[0]: ph=((t-T_TL[0])/0.9)%1.0; d['flip']=ph if ph<0.6 else 0.0; d['flip']=seg01(d['flip'],0,0.6)
            if T_TL[1]+0.1<=t<T0['10']:                        # the end of the speech: arms wide, then a deep bow
                u=sm(seg01(t,T_TL[1]+0.1,T_TL[1]+0.5)); d.update(rh=lerp3(R_OPEN,(1.6,3.0,0.6),u),lh=L_SCROLL,head=0.0,lean=0.0)
                b=sm(seg01(t,*T_BOW))
                d['lean']=0.55*b; d['rh']=lerp3(d['rh'],(0.5,2.3,0.6),b)
            if t>=T0['10']:                                    # the fight: arms open, happy, one hit, falls back
                u=sm(seg01(t,T0['10'],T0['10']+0.5)); d.update(rh=lerp3((0.5,2.3,0.6),(1.6,3.0,0.6),u),lh=lerp3(L_SCROLL,(-1.6,3.0,0.6),u),head=0.0,lean=0.55*(1-u),happy=1.0)
                d['lean']+=0.04*math.sin(t*6)*(1-seg01(t,T_HIT-0.1,T_HIT))
                if t>=T_HIT: a=seg01(t,T_HIT,T_HIT+0.55); d['fall']=a*a*(1.0 if a<1 else 1.0)+0.04*math.sin(PI*seg01(t,T_HIT+0.55,T_HIT+0.8))*(-1 if t>T_HIT+0.55 else 0)
                if t>=T_HIT+0.55: d['fall']=1.0-0.03*math.sin(PI*seg01(t,T_HIT+0.55,T_HIT+0.8))
    return d

# ----- scroll -----
PAPER=(206,192,154); PAPER_D=(176,160,124); INK=(70,52,40)
def scroll_u(t):
    """unrolled fraction: 0.35 at frame 0, full by line 2, longer after 'second sentence'"""
    u=lerp(0.35,1.0,sm(seg01(t,ws('2',0)+0.2,ws('2',0)+1.7)))
    if t>=ws('7',1)+0.3: u+=0.45*sm(seg01(t,ws('7',1)+0.3,ws('7',1)+1.4))
    if t>=T_TL[0]: u+=0.8*seg01(t,T_TL[0],T_TL[1])
    return u
def scroll_drop(t):
    for i,s in enumerate(SKIP):
        end=CUTS[3+i]
        if s<=t<end: return seg01(t,s+0.02,s+0.22)
    if t>=T0['10']+0.15: return seg01(t,T0['10']+0.15,T0['10']+0.4)
    return 0.0
def scroll(t,bs):
    st=dict(base=bs['base'],yaw=bs['yaw'],lean=bs['lean'],head=bs['head'])
    hw=bT(st,np.array(bs['lh'])+np.array([0,0,0.12])); Rb=FB.Ry(bs['yaw']); r=Rb@np.array([1.0,0,0])*0.2; fw=Rb@np.array([0,0,1.0])
    if bs['fall']>0 and scroll_drop(t)<=0: return []
    dr=scroll_drop(t)
    if t>=T_FROZE and t<T_FROZE+0.9: hw=hw+np.array([0.02*math.sin(t*70),0.015*math.sin(t*53),0])     # trembling
    L=scroll_u(t)*(2.0+1.8); top=lerp(hw[1],0.04,dr)
    v=min(L,top-0.03); g=np.array([hw[0],0.03,hw[2]]); Q=[]
    t0=np.array([hw[0],top,hw[2]]); t1=np.array([hw[0],top-v,hw[2]])
    if v>0.02: Q+=dq([t0-r,t0+r,t1+r,t1-r],PAPER,True)
    Q+=box(hw[0]-0.24,hw[0]+0.24,top-0.06,top+0.06,hw[2]-0.06,hw[2]+0.06,PAPER_D,emit=True)                         # rolled top edge
    rest=L-v
    if rest>0.02:
        a=g+np.array([0,0.0,0]); b=g+fw*rest
        Q+=dq([a-r,a+r,b+r,b-r],PAPER,True)
        Q+=box(b[0]-0.24,b[0]+0.24,0.0,0.14,b[2]-0.08,b[2]+0.08,PAPER_D,emit=True)                                   # the roll at the end
    # ink lines (the speech) on the visible paper
    k=0.18
    while k<v-0.05:
        p=t0-np.array([0,k,0])+fw*0.012; Q+=dq([p-r*0.8,p+r*0.5,p+r*0.5-np.array([0,0.03,0]),p-r*0.8-np.array([0,0.03,0])],INK,True); k+=0.16
    k=0.12
    while k<rest-0.1:
        p=g+fw*k+np.array([0,0.012,0]); Q+=dq([p-r*0.8,p+r*0.5,p+r*0.5+fw*0.03,p-r*0.8+fw*0.03],INK,True); k+=0.16
    return Q

# ======================= knight / heroes =======================
def hero_of(t):
    if t<CUTS[2]: return None
    if t<CUTS[3]: return 'orange'
    if t<CUTS[4]: return 'green'
    if t<CUTS[5]: return 'purple'
    return 'blue'
def kwalk(t,t0,t1,z0,z1):
    u=seg01(t,t0,t1); return lerp(z0,z1,u),(t*8.5 if 0<u<1 else 0.0)
def kstate(t):
    h=hero_of(t)
    if h is None: return None
    d=dict(yaw=0.0,walk=0.0,run=0.0,lean=0.03*math.sin(t*2.2),head=0.0,sit=0.0,rh=None,lh=None,sword='hip',swing=0.0,eyes=0.0)
    if h!='blue':
        i=['orange','green','purple'].index(h); t0=CUTS[2+i]; s=SKIP[i]
        z0={0:0.6,1:5.0,2:KN_STOP}[i]
        z,wk=kwalk(t,t0-0.05,s-0.25,z0,KN_STOP); d['walk']=wk
        if t>=s-0.25: d['rh']=lerp3((0.27,0.86,0.04),(0.3,1.05,0.4),sm(seg01(t,s-0.25,s)))      # reaches for the button: impatient
        if t>=FLASH[i]:                                                                         # after the fight: victory pose by the fallen boss
            z=8.3; d.update(sword='hand',rh=(0.28,1.62,0.1),swing=0.12,walk=0.0,lean=0.0)
        return dict(base=(0.0,0.0,z),**d)
    # the listener
    z,wk=kwalk(t,CUTS[5]-0.05,we('6',0)-0.1,0.6,KN_STOP); d['walk']=wk
    if t>=T_SIT[0]: d['sit']=sm(seg01(t,*T_SIT))*(1-sm(seg01(t,*T_STAND)))
    if d['sit']>0: d['lean']=-0.05*d['sit']
    if T_TL[0]<=t<T_TL[1]: d['head']=0.15*math.sin(t*5.0); d['lean']+=0.03*math.sin(t*9)
    if T_CLAP[0]<=t<T_CLAP[1]:                                                                  # claps
        c=0.5+0.5*math.cos((t-T_CLAP[0])*2*PI*3.6); x=lerp(0.03,0.17,c)
        d['rh']=(x,1.18,0.38); d['lh']=(-x,1.18,0.38)
    if t>=T_DRAW[0]:
        u=sm(seg01(t,*T_DRAW)); d['rh']=lerp3((0.27,0.86,0.04),(0.28,1.0,0.42),u); d['sword']='hand' if u>0.4 else 'hip'; d['swing']=lerp(0.0,1.0,u)
        z,wk=kwalk(t,T_WALK[0],T_WALK[1],KN_STOP,KN_HIT_Z); d['walk']=wk
        h_=T_HIT
        if h_-0.5<=t<h_+0.6:                                                                    # one strike: raise, strike, recover
            up=sm(seg01(t,h_-0.5,h_-0.14)); down=sm(seg01(t,h_-0.14,h_)); rec=sm(seg01(t,h_+0.1,h_+0.6))
            if t<h_-0.14: d['rh']=lerp3((0.28,1.0,0.42),(0.28,1.6,0.05),up); d['swing']=lerp(1.0,0.15,up)
            elif t<h_: d['rh']=lerp3((0.28,1.6,0.05),(0.26,1.05,0.62),down); d['swing']=lerp(0.15,1.6,down); d['lean']=0.3*down
            else: d['rh']=lerp3((0.26,1.05,0.62),(0.28,1.0,0.42),rec); d['swing']=lerp(1.6,1.0,rec); d['lean']=0.3*(1-rec)
        if t>=h_+0.6: d.update(rh=(0.28,1.0,0.42),swing=1.0)
    return dict(base=(0.0,0.0,z),**d)
CAM_NOW=[]

# ======================= set: candles, lights =======================
CANDLES=[(-1.9,8.3),(1.9,8.3),(-2.4,10.2),(2.4,10.2),(-1.5,6.9),(1.5,6.9)]
def candle_h(t): return lerp(0.5,0.1,seg01(t,T_TL[0],T_TL[1]))
def candles(t):
    Q=[]; h=candle_h(t)
    for k,(x,z) in enumerate(CANDLES):
        fl=0.03*math.sin(t*17+k*2.3)
        Q+=box(x-0.12,x+0.12,0,0.04,z-0.12,z+0.12,FB.IRON_L)+box(x-0.05,x+0.05,0.04,0.04+h,z-0.05,z+0.05,(226,214,186),emit=True)
        Q+=box(x-0.035,x+0.035,0.06+h,0.17+h+fl,z-0.035,z+0.035,(255,190,70),emit=True)
    return Q
def night(t): return CUTS[1]<=t<CUTS[2]
def lights(t):
    dim=0.35 if night(t) else 1.0
    L=[((x*0.85,y+0.4,z+0.4),(255,90,45),(1.1+0.15*math.sin(t*11+k))*dim) for k,(x,y,z) in enumerate(FB.TORCHES)]
    L+=[((x,0.6,z),(255,170,80),0.35) for x,z in CANDLES[:4]]
    if night(t): L.append(((0.0,7.0,6.0),(110,130,255),0.9))
    else: L.append(((0.0,5.0,5.0),(150,160,230),0.8))
    return L

# ======================= cameras =======================
def creep(t,t0,rate=0.0014): return motion.creep(t,t0,rate,FPS)
def cam_shot(t):
    if t<CUTS[1]:      # A: close on the boss, then glides back to show the scroll reach the floor (line 2)
        u=motion.glide(seg01(t,T0['2']-0.1,T0['2']+1.4))
        tgt=lerp3((0.0,2.95,10.0),(0.0,1.95,9.6),u); p=lerp3((1.05,2.05,6.75),(1.5,1.55,4.6),u)
        return dict(cam=motion.dolly(p,tgt,creep(t,0.0,0.0012)),tgt=tgt,fov=lerp(42,54,u))
    if t<CUTS[2]:      # B: wide empty arena at night, the boss rehearses alone
        tgt=(0.0,1.9,10.2); return dict(cam=motion.dolly((5.0,3.4,4.4),tgt,creep(t,CUTS[1],0.0016)),tgt=tgt,fov=62)
    if t<CUTS[5]:      # C: over the boss's shoulder towards the gate (variants per hero)
        i=[c for c in (CUTS[2],CUTS[3],CUTS[4]) if t>=c].__len__()-1
        P=[(2.7,2.5,14.9),(-2.8,2.4,14.7),(2.4,2.3,14.4)][i]; tgt=[(0.0,1.5,4.0),(0.0,1.5,4.6),(0.2,1.5,5.0)][i]
        return dict(cam=motion.dolly(P,tgt,creep(t,CUTS[2+i],0.0018)),tgt=tgt,fov=[50,50,48][i])
    if t<CUTS[6]:      # C4: the listener walks in
        tgt=(0.0,1.5,4.0); return dict(cam=motion.dolly((2.7,2.5,14.9),tgt,creep(t,CUTS[5],0.0016)),tgt=tgt,fov=50)
    if t<CUTS[7]:      # D: side two-shot, the prompt fades
        tgt=(0.0,1.6,8.3); return dict(cam=motion.dolly((5.4,1.5,7.0),tgt,creep(t,CUTS[6],0.0012)),tgt=tgt,fov=66)
    if t<CUTS[8]:      # A2: close on the boss: froze, eyes flicker; tilts down to the scroll
        u=motion.glide(seg01(t,ws('7',1)+0.1,ws('7',1)+1.3)); tgt=lerp3((0.0,3.0,10.0),(0.0,2.3,9.6),u)
        return dict(cam=motion.dolly((1.0,2.1,6.7),tgt,creep(t,CUTS[7],0.0016)),tgt=tgt,fov=40)
    if t<CUTS[9]:      # D: side two-shot: time-lapse, clapping, bow
        tgt=(0.0,1.6,8.3); return dict(cam=motion.dolly((5.4,1.5,7.0),tgt,creep(t,CUTS[8],0.0009)),tgt=tgt,fov=66)
    # E: low side for the hit and the happy fall; glides up to the boss lying on the floor for the last line
    u=motion.glide(seg01(t,T0['11']-0.2,T0['11']+1.1))
    tgt=lerp3((0.0,1.4,9.4),(0.0,0.4,12.4),u); p=lerp3((3.9,0.5,6.9),(0.9,5.0,10.9),u)
    return dict(cam=motion.dolly(p,tgt,creep(t,CUTS[9],0.0010)),tgt=tgt,fov=lerp(64,60,u))
def shake_px(t):
    for f in FLASH:
        k=motion.kick(t,f,2.4,7,FPS)
        if k: return (0.0,k)
    k=motion.kick(t,T_HIT,2.6,7,FPS) or motion.kick(t,T_HIT+0.55,1.8,6,FPS)
    return (0.0,k)

# ======================= render =======================
RND=Renderer(W,H,fog=(16,10,16))
VI=[None]
def render3d(t):
    sh=cam_shot(t); cam=Camera.look(sh['cam'],sh['tgt']); CAM_NOW[:]=[sh['cam']]
    bs=bstate(t); B=bmodel(**bs); Sc=scroll(t,bs)
    ks=kstate(t); Ks=[]
    if ks is not None: Ks=[FB.prelit(hero(hero_of(t),**ks),sh['cam'])]
    gate=0.0 if t<CUTS[2] else 1.75
    layers=[FB.ARENA,FB.gate_doors(gate),FB.torches(t),candles(t),B,Sc]+Ks
    L=lights(t)
    for f in FLASH+[T_HIT]:
        if f-F<=t<f+0.3: L=L+[((0.0,2.0,8.5),(255,220,170),1.2*math.exp(-(t-f)*9))]
    img,vi,zb=zrender(RND,cam,layers,L,fov=sh['fov'],fog_start=9,fog_end=28,ambient=0.32,shake=shake_px(t),return_z=True)
    VI[0]=vi
    return post.ps1(img),vi

# ======================= HUD / UI =======================
def otext(d,s,x,y,col,sc=1):
    o=max(1,sc//2)
    for ox,oy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)): font.text(d,s,x+ox*o,y+oy*o,(0,0,0),sc,None)
    font.text(d,s,x,y,col,sc,None)
def ctext(d,s,y,col,sc=1): otext(d,s,(W-font.width(s,sc))//2,y,col,sc)
def prompt_state(t):
    """(visible, pressed, colour factor) of the PRESS X TO SKIP prompt"""
    if t<CUTS[1]: return True,False,1.0
    for i,s in enumerate(SKIP):
        if CUTS[2+i]<=t<s: return True,False,1.0
        if s<=t<s+0.22: return True,True,1.0
    if CUTS[5]<=t<T_FADE[1]: return True,False,1.0-sm(seg01(t,*T_FADE))
    return False,False,0.0
def skip_prompt(d,t):
    vis,pr,a=prompt_state(t)
    if not vis or a<=0.02: return
    blink=(int(t*2.5)%2==0) or pr
    if not blink and a>0.99: return
    col=tuple(int(lerp(60,c,a)) for c in WHT); bcol=tuple(int(lerp(50,c,a)) for c in ((255,255,255) if pr else (90,130,230)))
    y=234; w1=font.width('PRESS',1); w2=font.width('TO SKIP',1); bw=11; tot=w1+4+bw+4+w2; x=(W-tot)//2
    otext(d,'PRESS',x,y+2,col)
    bx=x+w1+4; d.ellipse([bx-1,y-1,bx+bw,y+bw],fill=(0,0,0)); d.ellipse([bx,y,bx+bw-1,y+bw-1],fill=bcol)
    font.text(d,'X',bx+3,y+2,(0,0,0) if pr else col,1,None)
    otext(d,'TO SKIP',bx+bw+4,y+2,col)
def fmt_int(n): return f'{n:,}'
def emote_pos(t):
    """screen position above the fallen boss (projected from 3D)"""
    if VI[0] is None: return None
    p=RND.project((0.0,1.2,13.9),VI[0])
    return None if p is None else (p[0],p[1])
def plus_text(d,x,y,col,sc):
    """'+' (not in the font) drawn with rectangles, then the rest"""
    s=sc; d.rectangle([x-1,y+2*s-1,x+5*s,y+3*s],fill=(0,0,0)); d.rectangle([x+2*s-1,y-1,x+3*s,y+5*s],fill=(0,0,0))
    d.rectangle([x,y+2*s,x+5*s-1,y+3*s-1],fill=col); d.rectangle([x+2*s,y,x+3*s-1,y+5*s-1],fill=col)
def hud(d,t):
    skip_prompt(d,t)
    if night(t):
        n=int(lerp(1,10950,min(1.0,seg01(t,CUTS[1]+0.1,CUTS[1]+1.4)**0.5)))
        otext(d,'REHEARSAL',(W-font.width('REHEARSAL',2))//2,28,WHT,2); ctext(d,'#'+fmt_int(n),48,YEL,2)
    for i,f in enumerate(FLASH):
        end=CUTS[3+i]
        if f+0.08<=t<end: ctext(d,'VICTORY',40,YEL if int(t*8)%2==0 else WHT,3)
    if CUTS[3]<=t<CUTS[5]:
        n=int(lerp(2,1248,sm(seg01(t,CUTS[3],CUTS[5]-0.2)))); otext(d,'SKIPPED: '+fmt_int(n),6,8,RED,1)
    if T_TL[0]-0.1<=t<CUTS[9]:
        sec=int(662*seg01(t,T_TL[0],T_TL[1])); s_=f'{sec//60:02d}:{sec%60:02d}'
        otext(d,'SPEECH',6,8,WHT,1); otext(d,s_,6,18,YEL,2)
        if T_TL[0]<=t<T_TL[1]:                                    # fast-forward icon (no '>' in the font)
            c=WHT if int(t*6)%2 else YEL
            for x0 in (W-30,W-19):
                d.polygon([(x0-1,7),(x0+11,15),(x0-1,23)],fill=(0,0,0)); d.polygon([(x0,9),(x0+9,15),(x0,21)],fill=c)
    if T_HIT+0.15<=t<T0['11']+0.2: ctext(d,'VICTORY',40,YEL if int(t*8)%2==0 else WHT,3)
    if t>=T_FAN:
        p=emote_pos(t)
        if p:
            pop=1.0+0.4*math.exp(-(t-T_FAN)*10); sc=2; w=5*sc+4+font.width('1 FAN',sc); x=int(p[0]-w/2); y=int(p[1]-8-6*(t-T_FAN))
            plus_text(d,x,y,PINK,sc); otext(d,'1 FAN',x+5*sc+4,y,PINK,sc)
def flash_alpha(t):
    a=0.0
    for f in FLASH:
        if f-F<=t<f+0.2: a=max(a,0.75*(1.0-seg01(t,f,f+0.2)))
    if T_HIT-F<=t<T_HIT+0.25: a=max(a,0.3*(1.0-seg01(t,T_HIT,T_HIT+0.25)))
    return a

# ======================= subtitles (1080x1920, 1.25x, sentence timings from the voice) =======================
SUB_F=7.0; ADV=6.9; HIL={'SPEECH','THIRTY','YEARS','NIGHT.','CAPE','SKIP.','NEXT','ANYTHING.','FROZE.','SECOND','ELEVEN','MINUTES.','CLAPPED.','HAPPY','ONE','LIFE.','HEARS?'}
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
def frame_low(t):
    img,vi=render3d(t); fa=flash_alpha(t)
    if fa>0: img=Image.fromarray(np.clip(np.asarray(img).astype(np.float32)*(1-fa)+255*fa,0,255).astype(np.uint8))
    if night(t): img=Image.fromarray(np.clip(np.asarray(img).astype(np.float32)*np.array([0.8,0.86,1.12]),0,255).astype(np.uint8))
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
    if (np.abs(V[:,0])>7.9).any() or (V[:,2]>17.9).any(): out.append(('wall',f'{name} inside an arena wall'))
    return out
def _kn(t): return kstate(t)
def _kmodel(**st): return FB.knight(**st)
def _bs(t): return bstate(t)
def _bmodel(**st): return bmodel(**st)
QA=dict(fps=FPS,dur=DUR,W=W,frame=frame,
    chars={'knight':(_kn,_kmodel,'sword','hip'),'boss':(_bs,_bmodel,'none','none')},
    geom=_geom,camera=lambda t: cam_shot(t)['cam'],min_cam_dist=0.4,camera_ok=lambda p: -7.5<p[0]<7.5 and 0.2<p[2]<17 and 0.1<p[1]<6,
    allow_jump=[(w,f/FPS) for w in ('knight','boss') for c in CUTS for f in range(int(c*FPS)-2,int(c*FPS)+4)],
    allow_teleport=[('knight',round(int(f*FPS)/FPS+k/FPS,4)) for f in FLASH for k in (0,1)],
    weapon_events=[('knight',f,'hip','hand') for f in FLASH]+[('knight',T_DRAW[0]+0.2,'hip','hand')]+[('knight',c,'hand','hip') for c in CUTS[3:6]],
    scenes=[dict(id=f's{i}',t0=CUTS[i],t1=CUTS[i+1],action=a) for i,a in enumerate((
        'hook: close on the boss mid-speech, PRESS X TO SKIP; the scroll unrolls to the floor (CAM A)',
        'rehearsal at night, empty arena: pauses, gestures, cape flip, REHEARSAL #10,950 (CAM B)',
        'first hero (orange) walks in, presses X, scroll drops, fight flash, VICTORY (CAM C)',
        'second hero (green) skips, SKIPPED counter (CAM C2)',
        'third hero (purple) skips (CAM C3)',
        'the blue knight walks in (CAM C)',
        'he stands still, the skip prompt fades out (CAM D)',
        'the boss froze, eyes flicker, looks at the scroll (CAM A2)',
        'time-lapse 11 minutes: knight sits, candles burn down, timer; knight claps, boss bows (CAM D)',
        'the fight: one hit, the happy boss falls back, +1 FAN (CAM E)'))],
    texts=lambda: [('hud','REHEARSAL',2),('hud','#10,950',2),('hud','SKIPPED: 1,248',1),('hud','VICTORY',3),('hud','11:02',2),('hud','PRESS',1),('hud','TO SKIP',1),('hud','1 FAN',2)])

# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=21); sr=s.sr; n=s.n; t=s.t; BED=np.zeros(n); FX=np.zeros(n); MUR=np.zeros(n)
    def put(buf,x,t0,v=1.0):
        i=int(t0*sr)
        if i>=n or i<0: return
        j=min(n,i+len(x)); buf[i:j]+=(x*v)[:j-i]
    def nb(t0,d,lo,hi,v,seed,shape=2,buf=None): put(FX if buf is None else buf,s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v)
    def tone(t0,m,d,v,wave='sq',duty=0.5,dec=3.0,att=0.005,buf=None,glide=0.0):
        f=440*2**((m-69)/12); tt=s.T(d); fr=f*(1+glide*tt/d); ph=np.cumsum(fr)/sr%1
        x=np.where(ph<duty,1.0,-1.0) if wave=='sq' else (4*np.abs(ph-0.5)-1 if wave=='tri' else np.sin(2*np.pi*ph))
        put(FX if buf is None else buf,x*np.minimum(1,tt/att)*np.exp(-tt*dec),t0,v)
    def thud(t0,f=55,v=0.3,d=0.6):
        tt=s.T(d); put(FX,np.sin(2*np.pi*f*tt*(1-0.3*tt/d))*np.exp(-tt*8)+s.filt_short(s.noise(d,int(t0*13)),lo=60,hi=700)*np.exp(-tt*12)*0.6,t0,v)
    def clank(t0,v=0.15,seed=0):
        tt=s.T(0.5); put(FX,sum(np.sin(2*np.pi*f*tt)*np.exp(-tt*k) for f,k in ((310,6),(820,9),(1490,14)))*0.4+s.filt_short(s.noise(0.5,seed),lo=1200,hi=6000)*np.exp(-tt*30),t0,v)
    def step(t0,v=0.05,seed=0):
        tt=s.T(0.12); put(FX,s.filt_short(s.noise(0.12,seed),lo=900,hi=5000)*np.exp(-tt*45)+np.sin(2*np.pi*2300*tt)*np.exp(-tt*60)*0.3,t0,v)
    def clap(t0,v=0.08,seed=0):
        tt=s.T(0.09); put(FX,s.filt_short(s.noise(0.09,seed),lo=900,hi=6000)*np.exp(-tt*70),t0,v)
    def mwah(t0,t1,rate=4.2,pitch=1.0,v=0.12,seed=0):
        """the boss's muffled speech: buzzy syllables through a low-pass (no words)"""
        rng=np.random.default_rng(seed); tt=t0
        while tt<t1-0.08:
            d=rng.uniform(0.6,1.25)/rate; d=min(d,t1-tt); f0=rng.uniform(78,112)*pitch; T_=s.T(d)
            ph=np.cumsum(f0*(1+0.15*np.sin(np.pi*T_/d))*np.ones(len(T_)))/sr%1; saw=2*ph-1
            x=s.filt_short(saw+0.3*s.noise(d,int(tt*97)),lo=90,hi=int(700*pitch))*np.sin(np.pi*T_/d)**1.5
            put(MUR,x,tt,v*rng.uniform(0.7,1.1)); tt+=d+rng.uniform(0.0,0.08)
    # ---- bed: low drone + torch crackle
    BED+=s.filt(s.rng.normal(0,1,n),lo=30,hi=200)*0.09
    BED+=(np.sin(2*np.pi*55*t)+0.6*np.sin(2*np.pi*82.4*t+0.5))*0.022*(0.8+0.2*np.sin(2*np.pi*0.3*t))
    BED+=soft_fire(s,level=0.006,crackles_per_s=4,seed=31)       # soft fire bed + real crackles (no per-sample gate)
    # ---- the boss's speech (murmur): hook + line 2, rehearsal (with the pause), each hero until the skip, the listener
    mwah(0.0,CUTS[1],seed=1); mwah(CUTS[1],ws('3',1)-0.05,seed=2); mwah(ws('3',2),ws('3',3)+0.4,rate=6.0,seed=3)
    for i,s_ in enumerate(SKIP): mwah(CUTS[2+i]+0.02,s_,seed=10+i)
    mwah(CUTS[5]+0.05,T_FROZE-0.05,seed=20); mwah(ws('7',1)+0.6,T_TL[0],v=0.07,seed=21)
    mwah(T_TL[0],T_TL[1],rate=11.0,pitch=1.7,v=0.3,seed=22)                               # fast-forward chatter
    mwah(T_TL[1]+0.05,T_TL[1]+0.5,seed=23)
    # ---- cape flip whoosh; rehearsal counter ticks
    nb(ws('3',3)+0.45,0.6,300,3500,0.08,31)
    for k in range(10): tone(CUTS[1]+0.12+k*0.12,96,0.03,0.012,'sq',dec=50)
    # ---- skips: UI click + tape stop on the murmur, fight flash, victory jingle
    for i,s_ in enumerate(SKIP):
        tone(s_,88,0.06,0.08,'sq',dec=40); tone(s_+0.03,100,0.05,0.05,'sq',dec=50)
        tone(s_+0.02,52,0.25,0.05,'sq',duty=0.3,dec=6,glide=-0.6)                           # the speech dies
        f=FLASH[i]; nb(f-0.06,0.12,500,5000,0.09,40+i); clank(f,0.16,50+i); thud(f+0.02,48,0.32,0.5)
        for k,m in enumerate((72,76,79,84)): tone(f+0.12+k*0.07,m,0.25 if k<3 else 0.45,0.035,'sq',duty=0.25,dec=4 if k<3 else 2.5)
    # ---- footsteps of each hero walking in
    for i in range(3):
        a=CUTS[2+i]; b=SKIP[i]-0.25
        for k in range(int((b-a)/0.3)): step(a+0.1+k*0.3,0.035,60+10*i+k)
    for k in range(int((we('6',0)-0.1-CUTS[5])/0.3)): step(CUTS[5]+0.1+k*0.3,0.04,90+k)
    # ---- the prompt fades: a soft falling blip; the boss freezes: a record-scratch-like squeak
    tone(T_FADE[0],84,0.4,0.02,'sin',dec=3,glide=-0.3)
    nb(T_FROZE-0.02,0.18,1500,6000,0.05,95); tone(T_FROZE,79,0.25,0.03,'sq',duty=0.2,dec=6,glide=-0.5)
    # ---- sitting down; time-lapse: fast clock ticks; candles sizzle
    nb(T_SIT[0]+0.2,0.25,200,1500,0.05,100)
    k=0
    while T_TL[0]+k*0.09<T_TL[1]: tone(T_TL[0]+k*0.09,98 if k%2 else 93,0.02,0.035,'sq',dec=80); k+=1
    BED+=s.filt(s.rng.normal(0,1,n),lo=2000,hi=8000)*0.012*((t>T_TL[0])&(t<T_TL[1]))
    # ---- standing, clapping, the bow
    nb(T_STAND[0],0.3,200,1500,0.04,110)
    k=0
    while T_CLAP[0]+k/3.6<T_CLAP[1]: clap(T_CLAP[0]+k/3.6+0.12,0.1,120+k); k+=1
    nb(T_BOW[0]+0.1,0.5,200,2000,0.04,130)
    # ---- the fight: draw, steps, one clang, the happy fall, victory jingle, +1 FAN chime
    nb(T_DRAW[0],0.25,1500,7000,0.05,140); tone(T_DRAW[0]+0.15,91,0.3,0.02,'sin',dec=6)
    for k in range(int((T_WALK[1]-T_WALK[0])/0.28)): step(T_WALK[0]+0.1+k*0.28,0.045,150+k)
    nb(T_HIT-0.25,0.24,500,5000,0.07,160); clank(T_HIT,0.2,161); thud(T_HIT+0.55,40,0.42,0.8); nb(T_HIT+0.55,0.5,100,1200,0.06,162)
    for k,m in enumerate((72,76,79,84,88)): tone(T_HIT+0.35+k*0.09,m,0.3 if k<4 else 0.8,0.04,'sq',duty=0.25,dec=4 if k<4 else 2.0)
    tone(T_FAN,96,0.25,0.03,'sin',dec=6); tone(T_FAN+0.08,100,0.4,0.03,'sin',dec=5)
    # ---- voice
    NB=np.zeros(n); wins=[]
    for k_,t0 in LINES:
        a,ar=_sf.read(os.path.join(TTS_DIR,'ss',f'{k_}.wav')); a=a if a.ndim==1 else a.mean(1)
        a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a); put(NB,a,t0); wins.append((t0,t0+len(a)/sr))
    g=duck_envelope(n,sr,wins,-6.0,0.05,0.25); gm=duck_envelope(n,sr,wins,-12.0,0.05,0.25)
    bed=BED*g; fx=FX*(0.55+0.45*g)+MUR*gm
    L=bed+fx; R_=np.roll(bed,700)+np.roll(fx,200); pk=max(np.abs(L).max(),np.abs(R_).max()); gv=pk*1.6/np.abs(NB).max()
    s.L=L+NB*gv; s.R=R_+NB*gv; s.reverb(0.14,length=1.4,decay=3.0)
    end=np.clip((DUR-t)/0.04,0,1); s.L*=end; s.R*=end
    return s.save(path,peak=0.9)
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'skip_speech.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'ss_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.96,vignette=0.25,grain=1.5,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(frame_final(f/FPS),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
