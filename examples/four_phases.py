"""WHY DO FINAL BOSSES HAVE THREE PHASES? (Insert Disc 2) ~31 s PS1 comedy, 9:16, procedural (nightkit). Brief: briefs/four_phases.md.
The "final boss" is a cloak over three stacked goblins; the knight sees it, lowers his sword and crawls under the cloak.
Reuses: locked knight + arena (examples/final_boss.py), goblin (examples/loot_restocker.py, colour/scale variants only).
NEW: cloak (tapered stack + crown + eyes), giant sword prop, cup, boss bar / banners / carry-weight HUD.
Voice: python tools/tts/fp.py src; python tools/tts/fp_vc.py (Chatterbox python); python tools/tts/fp.py build vc  -> $TTS_DIR/fp/*.wav (+ sentence timings)
Run: TEST=1,5,9 python examples/four_phases.py -> test.png | PART=a:b (frames -> out/fp_a.mp4) | PART=audio"""
import os, sys, math, json, re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','tts'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, quad
from nightkit import motion, post, font
from nightkit.zraster import zrender
from nightkit.audio import Sound, duck_envelope
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

# ======================= voice timings (tools/tts/fp.py) =======================
SCR=json.load(open(os.path.join(TTS_DIR,'fp','script.json')))
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

# ======================= story events =======================
HIT=[we('2',0)-LEAD, ws('3',1)+1.1-LEAD, ws('4',1)+0.5-LEAD]      # the three sword hits ("blow", "shorter", "shorter")
RISE=[ws('3',0)-LEAD, max(ws('4',0)-LEAD,HIT[1]+0.45)]            # the boss stands up again: phase 2, phase 3
T_SLIP=ws('5',0)+0.40                                            # the cloak slides off ("slips")
T_LAND=T_SLIP+0.60
T_KID_UP=T_LAND-0.15
T_OLD_UP=ws('7',0)+0.2; T_OLD_STAND=T0['8']-0.1
T_LOWER=ws('8',0)+0.35                                           # both lower their swords
T_MID_UP=T0['8']+0.2
T_KN_GO=T0['9']-0.1                                              # knight walks to the cloak spot
T_CLOAK_UP=T0['9']+0.45                                          # cloak is lifted over him
T_MID_IN=T0['9']+1.05
T_KID_IN=T0['10']+0.12
T_FOUR=ws('10',0)+1.25                                           # "four"
T_DAYOFF=ws('11',0)+1.55                                         # "day off"
CUTS=[0.0,T0['2']-0.05,T_LAND,T0['8']-0.08,T0['10']-0.1,DUR]
BOSS_P=(0.0,0.0,5.6)
KN_P=(-0.15,0.0,3.95)

# ======================= LOCKED ASSET: cloak boss (stack of goblins under a cloak) =======================
CLK=(54,38,78); CLK_D=(38,26,58); CLK_L=(74,52,100); CROWN=(240,196,70)
def cloak(t,h,tilt=0.0,lean=0.0,x=0.0,plume=False):
    """tapered 8-sided cloak, total height h (m, incl. head), base centre BOSS_P+x. tilt: whole-model fall about the +x rim (rad, 0 upright).
    lean: small back/forward sway; the head (hood box, crown, two glowing eyes) sits on top. Cloak faces -z (towards the knight)."""
    r0=0.8+0.1*min(h,3.6); hb=max(0.2,h-0.5); r1=0.42; n=8; Q=[]
    def rr(y): return lerp(r0,r1,min(1.0,y/hb)) if y<=hb else r1
    for k in range(n):
        a0=2*PI*k/n; a1=2*PI*(k+1)/n; col=CLK if k%2 else CLK_D
        if math.cos((a0+a1)/2)>0.0 and math.sin((a0+a1)/2)<0.2: col=CLK_L if k%2 else CLK
        Q.append(quad([(r0*math.cos(a0),0.0,r0*math.sin(a0)),(r0*math.cos(a1),0.0,r0*math.sin(a1)),(r1*math.cos(a1),hb,r1*math.sin(a1)),(r1*math.cos(a0),hb,r1*math.sin(a0))],col))
    Q+=box(-0.42,0.42,hb-0.05,h,-0.42,0.42,CLK_D)                                   # hood / head block
    fz=-0.425
    Q+=box(-0.36,0.36,hb+0.1,hb+0.32,fz-0.01,fz+0.02,(10,6,14))                    # dark face slit
    for sx in (-1,1): Q+=box(sx*0.07,sx*0.3,hb+0.16,hb+0.27,fz-0.025,fz,RED,emit=True)       # red eyes
    Q+=box(-0.38,0.38,h,h+0.05,-0.38,0.38,CROWN,emit=True)
    for sx in (-0.3,0.0,0.3): Q+=box(sx-0.05,sx+0.05,h+0.05,h+0.24,-0.05,0.05,CROWN,emit=True)
    if plume: Q+=box(-0.03,0.03,h+0.05,h+0.55,-0.05,0.1,(60,120,230),emit=True)+box(-0.03,0.03,h+0.35,h+0.5,-0.2,-0.05,(60,120,230),emit=True)
    c=np.array([BOSS_P[0]+x,0,BOSS_P[2]],float); piv=np.array([-r0,0,0.0]); Rt=FB.Rz(tilt); Rl=FB.Rx(lean)
    def tf(p):
        p=np.array(p,float); p=Rl@p; p=piv+Rt@(p-piv); return tuple(c+p)
    Q=xform(Q,tf)
    if tilt>0:                                                                      # lying: rests on the floor, never through it
        ymin=min(v[1] for q in Q for v in q['p'])
        if ymin<0.0: Q=xform(Q,lambda p:(p[0],p[1]-ymin,p[2]))
    return Q

# ======================= LOCKED ASSET: goblin variants (parameters only) =======================
OLD_COL={LR.SKIN:(104,138,98),LR.SKIN_D:(76,104,76),LR.TUNIC:(98,86,76),LR.TUNIC_D:(72,62,56)}
KID_COL={LR.SKIN:(132,205,92),LR.SKIN_D:(96,160,66),LR.TUNIC:(70,84,150),LR.TUNIC_D:(50,60,112)}
GOB=dict(old=dict(s=1.12,col=OLD_COL),mid=dict(s=1.0,col={}),kid=dict(s=0.82,col=KID_COL))
BEARD=(212,212,206); BEARD_D=(168,168,162)
def gpt(base,yaw,lean,p):
    """goblin-local point (head-level props) -> world, same transform as LR.goblin for head=0, hop=0"""
    b=np.array(base,float); piv=np.array([0,0.34,0]); return b+FB.Ry(yaw)@(piv+FB.Rx(lean)@(np.array(p,float)-piv))
def fall_xf(Q,base,yaw,a,fwd=True):
    if a<=0: return Q
    Rb=FB.Ry(yaw); ang=(1.45 if fwd else -1.45)*a; Rf=Rb@FB.Rx(ang)@Rb.T
    piv=np.array(base,float)+Rb@np.array([0,0,0.12 if fwd else -0.12])
    Q=xform(Q,lambda p:tuple(piv+Rf@(np.array(p,float)-piv)))
    ymin=min(v[1] for q in Q for v in q['p'])
    if ymin<0.005: Q=xform(Q,lambda p:(p[0],p[1]-ymin+0.005,p[2]))
    return Q
def gmodel(who,base,yaw,walk=0.0,lean=0.0,rh=None,lh=None,eyes=1.0,smile=0.0,fall=0.0,fwd=True,head=0.0,hop=0.0,**_):
    g=GOB[who]; s=g['s']; b=np.array(base,float)
    Q=LR.goblin(base,yaw,walk=walk,lean=lean,rh=rh,lh=lh,eyes=eyes,smile=smile,hat=(who=='mid'),head=head,hop=hop)
    if who=='old':                                                                  # grey beard + sparse hair
        P=lambda p: tuple(gpt(base,yaw,lean,np.array(p)+np.array([0,hop,0])))
        Q+=box(-0.11,0.11,0.52,0.64,0.11,0.15,BEARD,xf=P)+box(-0.07,0.07,0.42,0.54,0.11,0.15,BEARD_D,xf=P)+box(-0.04,0.04,0.34,0.44,0.115,0.15,BEARD,xf=P)
        Q+=box(-0.16,-0.1,0.74,0.9,-0.12,0.12,BEARD_D,xf=P)+box(0.1,0.16,0.74,0.9,-0.12,0.12,BEARD_D,xf=P)
    if who=='kid':                                                                  # small gold crown
        P=lambda p: tuple(gpt(base,yaw,lean,np.array(p)+np.array([0,hop,0])))
        Q+=box(-0.14,0.14,0.86,0.92,-0.14,0.14,CROWN,xf=P,emit=True)
        for sx in (-0.1,0.0,0.1): Q+=box(sx-0.025,sx+0.025,0.92,1.0,-0.025,0.025,CROWN,xf=P,emit=True)
    for q in Q:
        c=g['col'].get(tuple(q['col']))
        if c: q['col']=c
    if s!=1.0: Q=xform(Q,lambda p:tuple(b+(np.array(p,float)-b)*s))
    return fall_xf(Q,base,yaw,fall,fwd)

# ======================= keyframes =======================
def kf(t,keys):
    """keys: [(t, dict)] with numeric / tuple fields; piecewise smooth interpolation, holds before / after."""
    if t<=keys[0][0]: return dict(keys[0][1])
    for (t0,a),(t1,b) in zip(keys,keys[1:]):
        if t0<=t<=t1:
            u=sm((t-t0)/(t1-t0) if t1>t0 else 1.0); out={}
            for k in a:
                va,vb=a[k],b.get(k,a[k]); out[k]=lerp3(va,vb,u) if isinstance(va,tuple) else lerp(va,vb,u)
            return out
    return dict(keys[-1][1])
def with_walk(t,keys,speed=9.0):
    d=kf(t,keys); d2=kf(t+0.04,keys); mv=math.hypot(d2['x']-d['x'],d2['z']-d['z'])/0.04
    return d,(t*speed if mv>0.08 else 0.0)

# ----- goblins (positions: heap inside the cloak -> reveal -> they walk to the cloak) -----
HEAP=dict(old=(0.5,6.0,1.2),mid=(-0.5,5.6,-2.0),kid=(0.0,5.4,PI))
def gstate(who,t):
    hx,hz,hy=HEAP[who]
    if who=='kid':
        keys=[(0,dict(x=hx,z=hz,yaw=hy,fall=1.0,lean=0.0)),(T_KID_UP,dict(x=hx,z=hz,yaw=PI,fall=1.0,lean=0.0)),(T_KID_UP+0.55,dict(x=hx,z=hz,yaw=PI,fall=0.0,lean=0.12)),
              (T_LOWER+0.5,dict(x=hx,z=hz,yaw=PI,fall=0.0,lean=0.12)),(T0['9']+0.1,dict(x=hx,z=hz,yaw=PI*0.8,fall=0.0,lean=0.0)),
              (T0['9']+0.95,dict(x=1.2,z=6.3,yaw=PI*0.35,fall=0.0,lean=0.0)),(T_KID_IN-0.05,dict(x=1.2,z=6.3,yaw=-PI/2,fall=0.0,lean=0.0)),
              (T_KID_IN+0.5,dict(x=0.15,z=5.95,yaw=-PI/2,fall=0.0,lean=0.0))]
    elif who=='old':
        keys=[(0,dict(x=hx,z=hz,yaw=hy,fall=1.0,lean=0.0)),(T_OLD_UP,dict(x=hx,z=hz,yaw=hy,fall=1.0,lean=0.0)),(T_OLD_UP+0.8,dict(x=hx,z=hz,yaw=hy,fall=0.45,lean=0.2)),
              (T_OLD_STAND,dict(x=hx,z=hz,yaw=hy,fall=0.45,lean=0.2)),(T_OLD_STAND+0.55,dict(x=hx,z=hz,yaw=2.2,fall=0.0,lean=0.42)),
              (T0['9']+0.9,dict(x=2.0,z=6.2,yaw=1.1,fall=0.0,lean=0.42)),(T0['10']+1.0,dict(x=2.75,z=5.3,yaw=-PI/2,fall=0.0,lean=0.42)),
              (ws('11',0)+0.5,dict(x=2.75,z=5.3,yaw=-PI/2,fall=0.0,lean=0.1)),(ws('11',0)+1.1,dict(x=2.75,z=5.3,yaw=-PI/2,fall=0.0,lean=-0.2))]
    else:
        keys=[(0,dict(x=hx,z=hz,yaw=hy,fall=1.0,lean=0.0)),(T_MID_UP,dict(x=hx,z=hz,yaw=hy,fall=1.0,lean=0.0)),(T_MID_UP+0.55,dict(x=hx,z=hz,yaw=hy,fall=0.0,lean=0.3)),
              (T0['9']-0.05,dict(x=hx,z=hz,yaw=0.8,fall=0.0,lean=0.3)),(T0['9']+0.65,dict(x=1.25,z=5.0,yaw=1.2,fall=0.0,lean=0.1)),
              (T_MID_IN-0.05,dict(x=1.25,z=5.0,yaw=PI/2*1.0,fall=0.0,lean=0.1)),(T_MID_IN+0.42,dict(x=0.5,z=5.45,yaw=PI/2,fall=0.0,lean=0.1))]
    d,wk=with_walk(t,keys); d['walk']=wk
    tr=0.0
    if who=='kid' and T_KID_UP+0.7<t<T_LOWER+0.6: tr=0.012*math.sin(t*55)                  # trembling
    d['x']+=tr
    pant=0.0
    if who in('old','mid') and d['fall']>0.5 and T_SLIP<t<T_OLD_UP+1.0: pant=0.5*math.sin(t*11)
    kid_stand=(who=='kid' and d['fall']<0.05)
    hop=0.0
    if who=='mid' and T_MID_IN+0.12<t<T_MID_IN+0.45: hop=0.3*math.sin(PI*seg01(t,T_MID_IN+0.12,T_MID_IN+0.45))
    if who=='kid' and T_KID_IN+0.2<t<T_KID_IN+0.55: hop=0.3*math.sin(PI*seg01(t,T_KID_IN+0.2,T_KID_IN+0.55))
    base=(d['x'],0.0,d['z']); eyes=0.35 if who=='old' else (0.5 if who=='mid' and d['fall']>0.3 else 1.0)
    st=dict(who=who,base=base,hop=hop,yaw=d['yaw'],walk=d['walk'],lean=d['lean']+0.04*pant,fall=d['fall'],fwd=(who!='kid'),eyes=eyes,smile=-0.8 if who in ('old','kid') else (-0.4 if who=='mid' else 0.0))
    if who=='kid':
        held=t<T_KID_IN+0.1; st['rh']=(0.1,0.34,0.2) if held else None
    if who=='old' and t>ws('11',0)+0.5: st['rh']=(0.2,0.55,0.28); st['smile']=0.8; st['eyes']=0.4        # raises the cup
    return st
def gob_model(**st): who=st.pop('who'); return gmodel(who,**st)
def gstate_for(who): return lambda t: gstate(who,t)

# ----- giant sword of the kid -----
GS_LEN=1.55
def gsword(t):
    ks=gstate('kid',t); b=np.array(ks['base'],float)
    if t>=T_KID_IN+0.1:                                                              # dropped on the floor at the cloak entrance
        d=np.array([0.2,0.0,1.0]); d/=np.linalg.norm(d); hp=np.array([1.0,0.04,5.9]); return seg_sword(hp,d)
    if ks['fall']>0.3: hp=b+np.array([0.0,0.1,0.0]); d=np.array([0.0,0.1,1.0]); d/=np.linalg.norm(d); hp=b+np.array([0.15,0.12,0.0]); return seg_sword(hp,d)
    s=GOB['kid']['s']; Rb=FB.Ry(ks['yaw']); hp=b+Rb@(np.array(ks['rh'] or (0.1,0.34,0.2))*s*1.0+np.array([0,0.0,0.0]))
    hp=b+FB.Ry(ks['yaw'])@(np.array([0.1,0.30,0.22])*1.0)
    up=np.array([0.12,1.0,0.15]); up/=np.linalg.norm(up)
    low=np.array([0.1,-0.25,1.0]); low/=np.linalg.norm(low)
    u=sm(seg01(t,T_LOWER,T_LOWER+0.45)); d=up+(low-up)*u; d/=np.linalg.norm(d); dloc=d
    dw=Rb@dloc
    if hp[1]+dw[1]*GS_LEN<0.04:                                                      # tip rests on the floor
        dy=-(hp[1]-0.04)/GS_LEN; hz=np.array([dw[0],0,dw[2]]); hz/=np.linalg.norm(hz)+1e-9; dw=hz*math.sqrt(max(0.0,1-dy*dy))+np.array([0,dy,0])
    if t>T0['9']+0.5 and t<T_KID_IN+0.1:
        dw=np.array([0.3,-0.3,0.9]); dw/=np.linalg.norm(dw); hp=b+Rb@np.array([0.1,0.3,0.25])
        if hp[1]+dw[1]*GS_LEN<0.04: dw=np.array([0.3,-(hp[1]-0.04)/GS_LEN,0.9]); dw/=np.linalg.norm(dw)
    return seg_sword(hp,dw)
def seg_sword(hp,d):
    hp=np.array(hp,float); tip=hp+d*GS_LEN; cr=np.cross(d,np.array([0,1.0,0])); cr/=np.linalg.norm(cr)+1e-9
    if abs(d[1])>0.95: cr=np.array([1.0,0,0])
    return (FB.seg(hp+d*0.1,tip,0.17,FB.BSWORD,0.05)+FB.seg(hp+d*0.2,tip-d*0.1,0.05,FB.BEDGE,0.06,emit=True)+FB.seg(hp-cr*0.2+d*0.1,hp+cr*0.2+d*0.1,0.07,FB.TRIM)+FB.seg(hp-d*0.15,hp+d*0.1,0.06,FB.LEATH))

# ----- cup (day off) -----
def cup(t):
    if t<ws('11',0)+0.5: return []
    st=gstate('old',t); b=np.array(st['base'],float); s=GOB['old']['s']
    p=gpt(st['base'],st['yaw'],st['lean'],(0.2,0.6,0.3)); p=b+(p-b)*s
    return box(p[0]-0.05,p[0]+0.05,p[1]-0.04,p[1]+0.07,p[2]-0.05,p[2]+0.05,(236,236,240))+box(p[0]-0.04,p[0]+0.04,p[1]+0.06,p[1]+0.075,p[2]-0.04,p[2]+0.04,(120,70,40),emit=True)

# ======================= cloak state =======================
def cloak_h(t):
    k=[(0.0,3.6),(HIT[0],3.6),(HIT[0]+0.3,1.6),(RISE[0],1.6),(RISE[0]+0.35,2.4),(HIT[1],2.4),(HIT[1]+0.25,0.8),(RISE[1],0.8),(RISE[1]+0.35,1.2),(HIT[2],1.2),(HIT[2]+0.12,0.95),(HIT[2]+0.4,1.2),
       (T_SLIP,1.2)]
    if t<=T_SLIP: return motion.Track([(a,(b,)) for a,b in k])(t)[0]
    if t<T_CLOAK_UP: return 1.2
    k2=[(T_CLOAK_UP,1.2),(T_CLOAK_UP+0.7,2.4),(T_MID_IN+0.3,2.4),(T_MID_IN+0.85,3.6),(T_KID_IN+0.35,3.6),(T_KID_IN+1.0,4.8)]
    return motion.Track([(a,(b,)) for a,b in k2])(t)[0]
def cloak_tilt(t):
    if t<T_SLIP: return 0.0
    if t<T_CLOAK_UP: u=seg01(t,T_SLIP,T_LAND); return 1.5*u*u+0.05*math.sin(PI*seg01(t,T_LAND,T_LAND+0.25))*(1 if t>T_LAND else 0)
    return 1.5*(1-sm(seg01(t,T_CLOAK_UP,T_CLOAK_UP+0.65)))
def cloak_lean(t):
    v=0.02*math.sin(t*2.3)
    for h in HIT:
        if h<=t<h+0.5: v+=0.16*math.exp(-(t-h)*7)*math.sin((t-h)*30+0.6)*-1+0.0
    if T_CLOAK_UP+0.7<=t<T_KID_IN: v+=0.015*math.sin(t*9)
    return v
def boss_phase(t): return 1+sum(1 for r in RISE if t>=r)
def hp_segments(t):
    """boss bar: list of 3 (or 4) booleans (full?)"""
    if t>=T_FOUR-0.1: return [True]*4
    return [t<HIT[i]+0.04 for i in range(3)]

# ======================= knight =======================
def kstate(t):
    d=dict(walk=0.0,run=0.0,lean=0.0,head=0.0,sit=0.0,rh=(0.26,1.02,0.42),lh=None,sword='hand',swing=1.0,eyes=0.0); base=KN_P; yaw=0.0
    breathe=0.02*math.sin(t*2.2); d['lean']=0.05+breathe
    # sword strikes on the three hits: raise (0.34 s before), strike (0.12 s before -> impact), recover
    sy=(1.02,0.9,0.7)
    for i,h in enumerate(HIT):
        if h-0.5<=t<h+0.55:
            up=sm(seg01(t,h-0.5,h-0.14)); down=sm(seg01(t,h-0.14,h)); rec=sm(seg01(t,h+0.05,h+0.5))
            pull=up*(1-down)
            d['rh']=lerp3((0.26,1.02,0.42),(0.28,1.6,0.05),pull) if t<h else lerp3((0.26,sy[i],0.6),(0.26,1.02,0.42),rec)
            if t<h and down>0: d['rh']=lerp3((0.28,1.6,0.05),(0.26,sy[i],0.6),down)
            d['swing']=lerp(1.0,0.15,pull) if t<h and down==0 else (lerp(0.15,1.75,down) if t<h else lerp(1.75,1.0,rec))
            d['lean']+=0.3*down*(1-rec) if t>=h-0.14 else 0.0
            zoff=0.34*down*(1-rec); base=(KN_P[0],0.0,KN_P[2]+zoff)
    if t>=T_SLIP-0.2:
        d['rh']=(0.26,1.02,0.42); d['swing']=1.0; base=KN_P
    if t>=T_LAND:                                                                   # shocked, then slowly lowers the sword
        d['head']=0.0
        if t>=T_LOWER-0.2:
            u=sm(seg01(t,T_LOWER-0.2,T_LOWER+0.5)); d['rh']=lerp3((0.26,1.02,0.42),(0.2,0.92,0.14),u); d['swing']=lerp(1.0,2.45,u); d['lean']=0.05+0.1*u
        if t>=T0['8']:
            u=sm(seg01(t,T0['8'],T0['8']+1.2)); base=lerp3(KN_P,(-0.3,0.0,4.4),u); d['walk']=t*8 if 0<u<1 else 0.0
    if t>=T_KN_GO:
        u=sm(seg01(t,T_KN_GO,T_KN_GO+1.0)); base=lerp3((-0.3,0.0,4.4),(-0.3,0.0,5.5),u); d['walk']=t*8 if 0<u<1 else 0.0
        yaw=lerp(0.0,0.0,u); c=sm(seg01(t,T_KN_GO+0.6,T_KN_GO+1.1)); d['sit']=0.5*c; d['lean']=0.3*c
    if t>=T_CLOAK_UP+0.5: d.update(sit=0.0,lean=0.0)
    return dict(base=base,yaw=yaw,**d)
def kmodel(**st):
    return FB.prelit(FB.knight(**st),CAM_NOW[0]) if CAM_NOW else FB.knight(**st)
CAM_NOW=[]

# ======================= set =======================
STONE_B=(86,80,86)
BACKREST=box(3.3,3.9,0,0.7,4.9,5.7,STONE_B)+box(3.25,3.95,0.7,0.8,4.85,5.75,(104,96,104))
def lights(t):
    L=[((x*0.85,y+0.4,z+0.4),(255,110,60),(1.15+0.15*math.sin(t*11+k))*1.05) for k,(x,y,z) in enumerate(FB.TORCHES)]
    L.append(((0.0,5.0,3.0),(150,160,230),0.9)); L.append(((0.0,3.0,5.6),(255,70,50),0.3))
    return L

# ======================= cameras =======================
def creep(t,t0,rate=0.0014): return motion.creep(t,t0,rate,FPS)
def cam_shot(t):
    if t<CUTS[1]:   # A: low-angle wide, huge boss in frame 0 (slow push in)
        tgt=(-0.2,1.9,5.6); return dict(cam=motion.dolly((1.8,0.5,1.5),tgt,creep(t,0.0,0.0016)),tgt=tgt,fov=64)
    if t<CUTS[2]:   # B: side medium for the hits; the target follows the boss height
        hh=cloak_h(t); tgt=(0.0,max(0.9,min(1.9,hh*0.5)),4.9); return dict(cam=motion.dolly((4.6,1.25,4.7),tgt,creep(t,CUTS[1],0.0012)),tgt=tgt,fov=60)
    if t<CUTS[3]:   # C: close on the goblins; pushes in to the old goblin on line 7
        u=sm(seg01(t,ws('7',0)-0.3,ws('7',0)+0.6)); tgt=lerp3((0.0,0.55,5.5),(0.22,0.38,5.78),u)
        p=lerp3((1.6,0.85,3.3),(1.0,0.7,4.15),u); return dict(cam=motion.dolly(p,tgt,creep(t,CUTS[2],0.0013)),tgt=tgt,fov=56)
    if t<CUTS[4]:   # D: side two-shot, knight left / goblin right
        tgt=(0.0,0.8,4.9); return dict(cam=motion.dolly((3.8,1.0,4.9),tgt,creep(t,CUTS[3],0.0013)),tgt=tgt,fov=46)
    # E: wide on the new boss (low angle), then pans to the old goblin on the last line
    u=sm(seg01(t,ws('11',0)-0.1,ws('11',0)+0.9)); hh=cloak_h(t)
    tgt=lerp3((0.0,min(2.6,hh*0.5),5.6),(2.6,0.6,5.3),u); p=lerp3((-1.3,0.9,2.6),(1.5,0.85,3.7),u)
    return dict(cam=motion.dolly(p,tgt,creep(t,CUTS[4],0.0008)),tgt=tgt,fov=lerp(76,44,u))
def shake_px(t):
    for h in HIT:
        k=motion.kick(t,h,2.2,7,FPS)
        if k: return (0.0,k)
    k=motion.kick(t,T_LAND,1.6,6,FPS)
    return (0.0,k) if k else (0.0,0.0)

def visible(w,t):
    """goblins are inside the cloak (not drawn) until it slips; mid / kid are inside it again once they have hopped in"""
    if t<T_SLIP-0.05: return False
    if w=='mid' and t>=T_MID_IN+0.45: return False
    if w=='kid' and t>=T_KID_IN+0.5: return False
    return True
# ======================= render =======================
RND=Renderer(W,H,fog=(16,10,16))
def render3d(t):
    sh=cam_shot(t); cam=Camera.look(sh['cam'],sh['tgt']); CAM_NOW[:]=[sh['cam']]
    ks=kstate(t); K=kmodel(**ks)
    Gs=[FB.prelit(gob_model(**gstate(w,t)),sh['cam'],warm=0.3) for w in ('old','mid','kid') if visible(w,t)]
    Cl=cloak(t,cloak_h(t),cloak_tilt(t),cloak_lean(t),plume=(t>=T_KID_IN+0.3))
    sw=FB.prelit(gsword(t),sh['cam'],warm=0.25)
    layers=[FB.ARENA,FB.gate_doors(0.0),FB.torches(t),BACKREST,Cl,sw,cup(t)]+Gs+[K]
    L=lights(t)
    for h in HIT:
        if h-F<=t<h+0.3: L=L+[((0.0,1.2,4.6),(255,200,150),0.9*math.exp(-(t-h)*9))]
    img,vi,zb=zrender(RND,cam,layers,L,fov=sh['fov'],fog_start=8,fog_end=26,ambient=0.3,shake=shake_px(t),return_z=True)
    return post.ps1(img),vi

# ======================= HUD / UI =======================
def otext(d,s,x,y,col,sc=1):
    o=max(1,sc//2)
    for ox,oy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)): font.text(d,s,x+ox*o,y+oy*o,(0,0,0),sc,None)
    font.text(d,s,x,y,col,sc,None)
def ctext(d,s,y,col,sc=1): otext(d,s,(W-font.width(s,sc))//2,y,col,sc)
def boss_bar(d,t):
    segs=hp_segments(t); n=len(segs); x0,x1=6,W-6; y0,y1=14,22
    four=t>=T_FOUR-0.1
    otext(d,'FINAL BOSS',6,4,WHT if not four else YEL)
    gap=3; w=(x1-x0-gap*(n-1))//n
    for i,full in enumerate(segs):
        xa=x0+i*(w+gap); d.rectangle([xa,y0,xa+w,y1],fill=(24,10,12),outline=(0,0,0))
        if full:
            col=RED if not four else (250,120,40)
            d.rectangle([xa+1,y0+1,xa+w-1,y1-1],fill=col)
        else:
            e=t-HIT[i]
            if e<0.25: d.rectangle([xa+1,y0+1,xa+w-1,y1-1],fill=(255,255,255) if int(e*24)%2==0 else RED)
def hud(d,t):
    boss_bar(d,t)
    if 0.08<=t<min(1.35,we('1',0)):
        ctext(d,'PHASE 1',38,WHT,2)
    for i,r in enumerate(RISE):
        if r<=t<r+1.1: ctext(d,f'PHASE {i+2}',38,YEL if int(t*8)%2==0 else WHT,3)
    if ws('7',0)+1.0<=t<T0['8']+0.2:
        ctext(d,'CARRY WEIGHT: 2 GOBLINS',46,YEL,1); ctext(d,'30 YEARS',58,RED,2)
    if T_FOUR<=t<T_FOUR+2.6: ctext(d,'PHASES: 4',44,YEL if int(t*6)%2==0 else WHT,2)
    if t>=T_DAYOFF: ctext(d,'DAY OFF',58,GRN,2);
    if t>=T_DAYOFF+0.4 and int(t*3)%3: ctext(d,'ZZZ',80,BLU,1)
def flash_alpha(t):
    a=0.0
    for h in HIT:
        if h-F<=t<h+0.3: a=max(a,0.2*(1.0-seg01(t,h,h+0.2)))
    return a

# ======================= subtitles (1080x1920, 1.25x, sentence timings from the voice) =======================
SUB_F=7.5; HIL={'BOSSES','PHASES?','PHASE','DOWN','SHORTER','SLIPS','GOBLINS,','THIRTY','CLOAK','FOUR','OFF','SOMEHOW','MONSTER.'}
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
    img,vi=render3d(t); d=ImageDraw.Draw(img); hud(d,t)
    fa=flash_alpha(t)
    if fa>0: img=Image.fromarray(np.clip(np.asarray(img).astype(np.float32)*(1-fa)+255*fa,0,255).astype(np.uint8))
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
QA=dict(fps=FPS,dur=DUR,W=W,frame=frame,
    chars={'knight':(_kn,_kmodel,'sword','hand'),'kid':(gstate_for('kid'),gob_model,'none','none'),'old':(gstate_for('old'),gob_model,'none','none')},
    geom=_geom,camera=lambda t: cam_shot(t)['cam'],min_cam_dist=0.4,camera_ok=lambda p: -7.5<p[0]<7.5 and 0.2<p[2]<17 and 0.1<p[1]<6,
    allow_jump=[(w,f/FPS) for w in ('knight','kid','old') for c in CUTS for f in range(int(c*FPS)-2,int(c*FPS)+4)],
    weapon_events=[],
    scenes=[dict(id=f's{i}',t0=CUTS[i],t1=CUTS[i+1],action=a) for i,a in enumerate((
        'hook: the huge cloaked boss, boss bar split in 3, PHASE 1',
        'three hits: the boss shrinks (phase 2, phase 3) and the cloak slips off (CAM B)',
        'reveal: three goblins, the kid trembling with the giant sword, old goblin CARRY WEIGHT (CAM C)',
        'knight lowers his sword, kid lowers his, knight crawls under the cloak, the goblins climb on (CAM D)',
        'new boss rises to 4 phases, old goblin gets a day off (CAM E)'))],
    texts=lambda: [('hud','FINAL BOSS',1),('hud','PHASE 3',3),('hud','CARRY WEIGHT: 2 GOBLINS',1),('hud','30 YEARS',2),('hud','PHASES: 4',2),('hud','DAY OFF',2)])

# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=11); sr=s.sr; n=s.n; t=s.t; BED=np.zeros(n); FX=np.zeros(n)
    def put(buf,x,t0,v=1.0):
        i=int(t0*sr)
        if i>=n or i<0: return
        j=min(n,i+len(x)); buf[i:j]+=(x*v)[:j-i]
    def nb(t0,d,lo,hi,v,seed,shape=2): put(FX,s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v)
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
    def whoosh(t0,d,v,seed,lo=300,hi=4000): nb(t0,d,lo,hi,v,seed,2)
    # ---- bed: low dungeon drone + torch crackle
    BED+=s.filt(s.rng.normal(0,1,n),lo=30,hi=200)*0.10
    BED+=(np.sin(2*np.pi*55*t)+0.6*np.sin(2*np.pi*82.4*t+0.5))*0.025*(0.8+0.2*np.sin(2*np.pi*0.3*t))
    BED+=s.filt(s.rng.normal(0,1,n),lo=1500,hi=7000)*(s.rng.random(n)<0.002)*0.6*0.25
    # ---- hook: low boss rumble + menacing two-note
    tone(0.1,40,1.2,0.10,'sq',duty=0.3,dec=2.0); tone(0.9,38,1.4,0.09,'sq',duty=0.3,dec=1.8)
    # ---- three hits: swing whoosh, clang, kick thud, phase stinger on each stand-up
    for k,h in enumerate(HIT):
        whoosh(h-0.28,0.26,0.07,300+k,500,5000); clank(h,0.16,40+k); thud(h+0.02,50,0.34,0.5)
        tone(h+0.02,36,0.3,0.07,'sq',duty=0.25,dec=8)
    for k,r in enumerate(RISE):
        for m,dt in ((57+2*k,0.0),(64+2*k,0.14)): tone(r+dt,m,0.5,0.05,'sq',duty=0.25,dec=4)          # two-note stinger
        thud(r+0.18,45,0.15,0.4)
    # ---- the cloak slips: long whoosh + soft fall thud
    whoosh(T_SLIP-0.1,0.7,0.09,321,200,3000); thud(T_LAND,38,0.4,0.8); nb(T_LAND,0.5,100,1200,0.06,322)
    # ---- goblin panting (filtered noise breaths) while they lie there
    for k in range(int((ws('7',0)+1.6-T_LAND)/0.45)):
        tb=T_LAND+0.1+k*0.45
        if tb<T0['8']: nb(tb,0.3,500,3000,0.03,330+k,2)
    # tremble: tiny rapid ticks while the kid shakes
    for k in range(int((T_LOWER-T_KID_UP)/0.13)): tone(T_KID_UP+0.7+k*0.13,92,0.03,0.008,'sq',dec=60)
    # ---- both lower the swords: two metal scrapes
    clank(T_LOWER+0.1,0.07,350); clank(T_LOWER+0.35,0.09,351)
    # ---- footsteps (knight, goblins)
    for k in range(5): step(T0['8']+0.1+k*0.24,0.05,360+k)
    for k in range(4): step(T_KN_GO+0.1+k*0.25,0.05,370+k)
    for k in range(4): step(T0['9']+0.1+k*0.2,0.025,380+k)
    for k in range(3): step(T_MID_IN-0.2+k*0.14,0.035,390+k);
    for k in range(3): step(T_KID_IN-0.1+k*0.14,0.035,395+k)
    # ---- the cloak is lifted, goblins hop in, the boss grows
    whoosh(T_CLOAK_UP-0.05,0.55,0.07,400,200,2500)
    for tt_,v in ((T_MID_IN+0.3,0.2),(T_KID_IN+0.35,0.25)): thud(tt_,48,v,0.4); whoosh(tt_,0.5,0.05,int(tt_*7),200,3000)
    # ---- "four phases": rising chord
    for m in (52,59,64,71): tone(T_FOUR,m,1.0,0.045,'sq',duty=0.4,dec=2.2)
    # ---- day off: cup clink, sigh, a heroic chord that turns comic
    tone(T_DAYOFF-0.1,96,0.5,0.03,'sin',dec=8); tone(T_DAYOFF-0.1+0.05,103,0.5,0.02,'sin',dec=8)
    for k,m in enumerate((67,71,74,79)): tone(T_DAYOFF+0.05+k*0.08,m,0.9,0.045,'sq',duty=0.25,dec=3)
    tone(T_DAYOFF+0.5,60,0.7,0.035,'sin',dec=2.5,glide=-0.3); tone(T_DAYOFF+0.75,55,0.9,0.03,'sin',dec=2.0,glide=-0.25)    # deflating wah
    # ---- voice
    NB=np.zeros(n); wins=[]
    for k_,t0 in LINES:
        a,ar=_sf.read(os.path.join(TTS_DIR,'fp',f'{k_}.wav')); a=a if a.ndim==1 else a.mean(1)
        a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a); put(NB,a,t0); wins.append((t0,t0+len(a)/sr))
    g=duck_envelope(n,sr,wins,-6.0,0.05,0.25); bed=BED*g; fx=FX*(0.55+0.45*g)
    L=bed+fx; R_=np.roll(bed,700)+np.roll(fx,200); pk=max(np.abs(L).max(),np.abs(R_).max()); gv=pk*1.6/np.abs(NB).max()
    s.L=L+NB*gv; s.R=R_+NB*gv; s.reverb(0.14,length=1.4,decay=3.0)
    end=np.clip((DUR-t)/0.04,0,1); s.L*=end; s.R*=end
    return s.save(path,peak=0.9)
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'four_phases.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'fp_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.96,vignette=0.25,grain=1.5,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(frame_final(f/FPS),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
