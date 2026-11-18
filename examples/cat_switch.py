"""WHY DO CATS KNOCK THINGS OVER?  PS1 comedy short, 9:16, 15 s, 5 shots of 3 s. Fully procedural (nightkit).
The cat swipes three objects off a low shelf; each one lands on a floor button; the third press opens a hidden food dispenser.
LOCKED ASSETS imported from cat_dodge.py: the cat (cat_model; this video uses its `paw` pose parameter), the bedroom floor + walls
(the bed, nightstand and beanbag are left out: plain room), the UI helpers. The shelf, objects, pads, dispenser and bowl are built here.
All text is a 2D overlay. Voice: python tools/tts/cs.py -> $TTS_DIR/cs/N1..N5.wav.
Run: TEST=0,3.1,9.1,11,14 python examples/cat_switch.py -> test.png | PART=a:b | PART=audio | QA: python tools/qa/scene_qa.py examples/cat_switch.py"""
import os, sys, math, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
import numpy as np
from PIL import Image, ImageDraw, ImageOps
from nightkit.engine import Renderer, Camera, box, transform
from nightkit import post, font
from nightkit.zraster import zrender
from nightkit.audio import Sound
import cat_dodge as CD
sm,seg01,lerp,lerp3,PI,Rx,Ry,Rz=CD.sm,CD.seg01,CD.lerp,CD.lerp3,CD.PI,CD.Rx,CD.Ry,CD.Rz
cat_model,otext,ctext,panel=CD.cat_model,CD.otext,CD.ctext,CD.panel
YEL,RED,GRN,WHT,CYAN=CD.YEL,CD.RED,CD.GRN,CD.WHT,CD.CYAN
TTS_DIR=CD.TTS_DIR; OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6; DUR=15.0; N=int(round(DUR*FPS))
SCR=json.load(open(os.path.join(TTS_DIR,'cs','script.json')))

# ======================= layout (fixed for the whole video) =======================
TAB=dict(x0=-0.86,x1=0.04,z0=-2.25,z1=-1.97,h=0.16)                 # low shelf, left of frame
X_OBJ=[-0.76,-0.42,-0.08]; Z_OBJ=-2.12; Z_EDGE=-1.995; PAD_Z=-1.76; PAD_H=0.022; PAD_R=0.085
DISP=dict(x0=0.42,x1=0.70,z0=-2.86,z1=-2.58,h=0.62)                  # food dispenser against the back wall, right of frame
BOWL=np.array([0.56,0.0,-2.36]); CHUTE=np.array([0.56,0.25,-2.56])
CAT_Z=-2.47; CAT_YAW=-0.3; CAT_DX=0.17
FOOD_SPOT=np.array([0.20,0.0,-2.36])                                 # where the cat stands to eat (faces +x)
# timeline
T_PUSH=[(-0.3,0.12),(4.7,5.0),(6.85,7.15)]                           # paw pushes the object to the shelf edge
T_TAP=[2.72,5.72,8.72]; SLIDE=0.08; FALL=0.26                         # final tap -> slide -> fall; lands at tap+0.34
T_LAND=[t+SLIDE+FALL for t in T_TAP]
T_WALK=[None,(4.0,4.55),(6.2,6.7)]
T_ALL=T_LAND[2]+0.12; T_CLICK=10.9; T_FLAP=(10.9,11.1); T_FOOD=(12.1,12.75)
T_LOOKCAM=(12.12,12.7); T_GO=(12.75,13.7); T_EAT=13.75
SHOTS=[(0.0,3.0,'s1'),(3.0,6.0,'s2'),(6.0,9.0,'s3'),(9.0,12.0,'s4'),(12.0,DUR,'s5')]

# ======================= palette =======================
SHELF=(150,100,66); SHELF_D=(118,78,52); BOOK=(70,110,210); PAGES=(244,236,214); MUG=(236,236,244); MUG_D=(110,70,50); POT=(206,104,64); LEAF=(80,180,90); LEAF_D=(56,140,70)
PAD_OFF=(70,66,96); PAD_RIM=(150,150,170); PAD_ON=(120,255,120); DISP_C=(216,222,236); DISP_D=(120,134,170); HOP=(150,200,240); KIB=(170,100,50); BOWL_C=(232,90,110)

# ======================= props =======================
def shelf():
    t=TAB; Q=box(t['x0'],t['x1'],t['h']-0.035,t['h'],t['z0'],t['z1'],SHELF)
    for x in (t['x0']+0.02,t['x1']-0.06):
        for z in (t['z0']+0.02,t['z1']-0.06): Q+=box(x,x+0.04,0.0,t['h']-0.035,z,z+0.04,SHELF_D)
    Q+=box(t['x0']+0.02,t['x1']-0.02,0.04,0.06,t['z0']+0.03,t['z1']-0.03,SHELF_D)
    return Q
SHELF_Q=shelf()
# objects: (model fn, half size x, half height, half depth)
def book_q(): return box(-0.045,0.045,-0.045,0.045,-0.045,0.045,BOOK)+box(-0.04,0.046,-0.038,0.038,0.046,0.048,PAGES)+box(0.046,0.048,-0.038,0.038,-0.04,0.04,PAGES)
def mug_q():
    Q=box(-0.035,0.035,-0.042,0.042,-0.035,0.035,MUG)+box(-0.028,0.028,0.042,0.044,-0.028,0.028,MUG_D)
    Q+=box(0.035,0.055,-0.02,0.025,-0.008,0.008,MUG)+box(-0.036,0.036,0.0,0.012,0.0355,0.037,(232,70,70)); return Q
def pot_q(): return box(-0.04,0.04,-0.04,0.02,-0.04,0.04,POT)+box(-0.045,0.045,0.02,0.035,-0.045,0.045,POT)+box(-0.03,0.03,0.035,0.05,-0.012,0.012,LEAF)+box(-0.012,0.012,0.035,0.058,-0.03,0.03,LEAF_D)
OBJ=[(book_q,0.045),(mug_q,0.042),(pot_q,0.04)]                       # (model fn, half height to the bottom face); built fresh per frame (transform works in place)

def obj_state(i,t):
    """centre + tilt (about x, + = top falls toward camera) of object i"""
    hb=OBJ[i][1]; x=X_OBJ[i]; y0=TAB['h']+hb; a,b=T_PUSH[i]; tp=T_TAP[i]
    z=lerp(Z_OBJ,Z_EDGE,sm(seg01(t,a,b))); tilt=0.0; y=y0
    if b<t<tp: tilt=0.10*max(0.0,math.sin((t-b)*7.0))*math.exp(-(t-b)*1.2)   # teeters on the edge
    for k,tt in enumerate((1.45,2.05)):                                         # first object: two little nudges while the question is asked
        if i==0 and tt<=t<tt+0.4: tilt+=0.16*math.sin(PI*seg01(t,tt,tt+0.4))
    if t>=tp:
        u=seg01(t,tp,tp+SLIDE); z=lerp(Z_EDGE,Z_EDGE+0.04,u); tilt=0.25*u
        if t>=tp+SLIDE:
            v=seg01(t,tp+SLIDE,tp+SLIDE+FALL); z=lerp(Z_EDGE+0.04,PAD_Z,v); y=lerp(y0,PAD_H+0.045,v*v); tilt=lerp(0.25,PI/2,v)
    return np.array([x,y,z]),tilt
def obj_quads(i,t):
    c,tl=obj_state(i,t); R_=Rx(tl); return transform(OBJ[i][0](),lambda p:tuple(c+R_@np.array(p,float)))
def pads_quads(t):
    Q=[]; allon=t>=T_ALL
    for i,x in enumerate(X_OBJ):
        on=t>=T_LAND[i]; press=0.008*math.exp(-(t-T_LAND[i])*12) if on else 0.0
        blink=allon and t<T_ALL+0.6 and int((t-T_ALL)*10)%2==1
        Q+=box(x-PAD_R-0.012,x+PAD_R+0.012,0.0,0.012,PAD_Z-PAD_R-0.012,PAD_Z+PAD_R+0.012,PAD_RIM)
        Q+=box(x-PAD_R,x+PAD_R,0.0,PAD_H-press,PAD_Z-PAD_R,PAD_Z+PAD_R,(255,255,200) if blink else (PAD_ON if on else PAD_OFF),emit=on)
    return Q
def kibble(t):
    Q=[]
    for k in range(7):
        t0=T_FOOD[0]+0.07*k; u=seg01(t,t0,t0+0.32)
        if t<t0: continue
        rest=BOWL+np.array([0.035*math.cos(k*2.4),0.035+0.012*(k%3),0.035*math.sin(k*2.4)])
        p=CHUTE+(rest-CHUTE)*u+np.array([0,0.08*math.sin(PI*u)-0.0,0])
        Q+=box(p[0]-0.012,p[0]+0.012,p[1]-0.01,p[1]+0.01,p[2]-0.012,p[2]+0.012,KIB)
    return Q
def dispenser_quads(t):
    d=DISP; Q=box(d['x0'],d['x1'],0.0,d['h'],d['z0'],d['z1'],DISP_C)+box(d['x0']-0.01,d['x1']+0.01,d['h'],d['h']+0.03,d['z0']-0.01,d['z1']+0.01,DISP_D)
    Q+=box(d['x0']+0.04,d['x1']-0.04,0.34,0.58,d['z1'],d['z1']+0.006,HOP)+box(d['x0']+0.06,d['x1']-0.06,0.36,0.46,d['z1']+0.006,d['z1']+0.008,KIB)    # window into the hopper
    Q+=box(0.50,0.62,0.19,0.29,d['z1'],d['z1']+0.004,(30,30,40))                                                                              # chute opening
    fo=sm(seg01(t,*T_FLAP)); R_=Rx(-1.2*fo); hinge=np.array([0.56,0.29,d['z1']+0.012])
    Q+=transform(box(-0.065,0.065,-0.105,0.0,-0.006,0.006,DISP_D),lambda p:tuple(hinge+R_@np.array(p,float)))                                 # the flap swings up
    on=t>=T_CLICK; Q+=box(0.64,0.68,0.52,0.56,d['z1'],d['z1']+0.01,(120,255,120) if on else (230,60,50),emit=True)                             # status lamp
    b=BOWL; Q+=box(b[0]-0.09,b[0]+0.09,0.0,0.05,b[2]-0.09,b[2]+0.09,BOWL_C)+box(b[0]-0.07,b[0]+0.07,0.05,0.052,b[2]-0.07,b[2]+0.07,(150,50,70))
    return Q+kibble(t)
ROOM_F,ROOM_W=CD.ROOM_F,CD.ROOM_W+box(-1.8,1.8,2.7,2.76,-2.96,1.32,(176,166,204))      # + the same ceiling as cat_pov.py
LIGHTS=[((-0.6,1.6,-0.6),(255,236,210),0.9),((0.8,1.2,-1.2),(200,210,255),0.5),((0.0,2.2,-2.0),(255,240,225),0.4)]

# ======================= the cat =======================
def cat_x(i): return X_OBJ[i]+CAT_DX
def paw_local(base,yaw,wp):
    return tuple(Ry(-yaw)@(np.array(wp,float)-np.array(base,float)))
def cat_state(t):
    st=dict(base=(cat_x(0),0.0,CAT_Z),yaw=CAT_YAW,walk=0.0,hx=0.0,hyaw=0.25,hroll=0.0,hpitch=0.2,lid=0.35,pupil=0.0,tail=0.0,crouch=0.0,ears=0.1,mouth=0.0,bpitch=0.0,shades=0.0,paw=0.0)
    # where along the shelf
    x=cat_x(0)
    for i in (1,2):
        a,b=T_WALK[i]
        if t>=a: x=lerp(cat_x(i-1),cat_x(i),sm(seg01(t,a,b))); st['walk']=t*11.0 if t<b else 0.0
        if a<=t<b: st['yaw']=CAT_YAW+1.4*math.sin(PI*seg01(t,a,b)); st['_walking']=True          # turns into the walk, head stays clear of the objects
    base=np.array([x,0.0,CAT_Z]); st['base']=tuple(base)
    # which object is current, and the paw
    i=0 if t<T_WALK[1][0] else (1 if t<T_WALK[2][0] else 2)
    oc,_=obj_state(i,min(t,T_TAP[i]+0.05)); back=oc+np.array([0.065,0.03,-0.015])  # paw rests on the cat-side of the object, in view
    a,b=T_PUSH[i]; tp=T_TAP[i]
    reach=sm(seg01(t,a-0.25,a)) if i else 1.0
    tap=math.sin(PI*seg01(t,tp-0.25,tp+0.1))                                       # final tap
    nud=sum(math.sin(PI*seg01(t,tt-0.15,tt+0.25)) for tt in (1.45,2.05)) if i==0 else 0.0
    if i==2: reach*=1-sm(seg01(t,7.35,7.6))*(1-sm(seg01(t,8.3,8.5)))              # paw down while he looks at us
    hold=1.0-sm(seg01(t,tp+0.15,tp+0.45))
    pw=back+np.array([0.0,0.03*max(0,1-nud)+0.03*(1-tap),-0.02+0.06*max(tap,nud)])
    st['paw']=reach*hold; st['paw_to']=paw_local(base,st['yaw'],pw)
    st['hpitch']=0.18; st['hyaw']=0.0
    if st.pop('_walking',False): st['hyaw']=0.0; st['hpitch']=0.1
    # beats
    st['tail']=0.4*math.sin(t*2.0)
    if t>=T_LAND[0]-0.1 and t<T_WALK[1][0]: k=sm(seg01(t,T_LAND[0]-0.1,T_LAND[0]+0.2)); st['hpitch']=0.38*k; st['hyaw']=-0.35*k; st['ears']=0.3       # looks down at the click
    if i==2 and 7.35<=t<8.5:                                                                                                    # smug look at the lens
        k=sm(seg01(t,7.35,7.6))*(1-sm(seg01(t,8.3,8.5))); st['hyaw']=-CAT_YAW*0.9*k; st['hpitch']=lerp(0.18,0.0,k); st['lid']=lerp(0.35,0.55,k)
    if t>=T_LAND[2]-0.1:
        k=sm(seg01(t,T_LAND[2]-0.1,T_LAND[2]+0.2)); st['hpitch']=lerp(0.18,0.4,k)
        lk=sm(seg01(t,9.75,10.1)); st['hyaw']=1.1*lk; st['hpitch']=lerp(st['hpitch'],0.05,lk)                                     # turns to the dispenser
        if t>=T_CLICK: st['ears']=0.7*sm(seg01(t,T_CLICK,T_CLICK+0.1)); st['lid']=0.0
    if t>=12.0:                                                                                                                 # payoff
        k=sm(seg01(t,*T_LOOKCAM))*(1-sm(seg01(t,T_GO[0]-0.05,T_GO[0]+0.15)))
        st.update(hyaw=lerp(1.1,-CAT_YAW,k)*(1-sm(seg01(t,T_GO[0],T_GO[0]+0.2))),hpitch=0.0,lid=lerp(0.0,0.55,k),ears=0.2,tail=0.6*math.sin(t*3))
        u=sm(seg01(t,*T_GO)); p0=np.array([cat_x(2),0.0,CAT_Z])
        mid=np.array([0.13,0.0,-2.42]); p=lerp3(lerp3(p0,mid,u),lerp3(mid,FOOD_SPOT,u),u)
        st['base']=tuple(p); st['yaw']=lerp(CAT_YAW,PI/2,sm(seg01(t,T_GO[0],T_GO[0]+0.6))); st['walk']=t*11.0 if T_GO[0]<t<T_GO[1] else 0.0
        if t>=T_GO[0]: st['hyaw']=0.0
        if t>=T_EAT:
            e=sm(seg01(t,T_EAT,T_EAT+0.3)); st['bpitch']=0.18*e; st['hpitch']=0.6*e+0.06*e*math.sin((t-T_EAT)*16); st['lid']=0.6*e; st['tail']=0.7*math.sin(t*4)
    return st

# ======================= shots (hard cuts, camera locked within a shot) =======================
def shot(t):
    n=[n_ for a,b,n_ in SHOTS if a<=t<b or (n_=='s5' and t>=a)][0]
    if n=='s1': return dict(cam=(-0.60,0.56,-1.42),tgt=(-0.60,0.30,-2.2),fov=58)
    if n in ('s2','s3'): return dict(cam=(-0.40,0.64,-1.25),tgt=(-0.40,0.32,-2.15),fov=68)
    if n=='s4': return dict(cam=(-0.13,0.50,-0.62),tgt=(-0.13,0.46,-2.3),fov=74)
    return dict(cam=(-0.10,0.58,-0.64),tgt=(-0.10,0.50,-2.3),fov=74)

# ======================= render =======================
R=Renderer(W,H,fog=(40,30,60))
def render(t):
    sh=shot(t); cam=Camera.look(sh['cam'],sh['tgt']); cp=np.array(sh['cam'])
    cs=cat_state(t); cq,cd=cat_model(**cs); cd=[x for x in cd if np.linalg.norm(x['c']-cp)<np.linalg.norm(x['hc']-cp)]
    objs=sum((obj_quads(i,t) for i in range(3)),[])
    layers=[ROOM_F,ROOM_W,SHELF_Q,pads_quads(t),dispenser_quads(t),objs,cq,cd]
    img,vi=zrender(R,cam,layers,LIGHTS,fov=sh['fov'],fog_start=14,fog_end=40,ambient=0.5,bias=[1.0]*7+[1.004])
    return ImageOps.mirror(post.ps1(img)),vi,cs                              # world +x renders screen-left: mirror so the shelf is left, dispenser right

# ======================= UI (2D overlays) =======================
SUBS=[('N1',0.0,2.95,['WHY DO CATS','KNOCK THINGS','OVER?'],{'KNOCK','THINGS','OVER?'}),('N2',3.15,5.6,['NOT TO','ANNOY YOU.'],{'ANNOY'}),
      ('N3',6.15,8.6,["THEY'RE",'TESTING','SOMETHING.'],{'TESTING'}),('N4',9.75,11.9,['A HIDDEN','FOOD SWITCH.'],{'HIDDEN','FOOD','SWITCH.'}),
      ('N5',12.2,14.95,['AND SOMEHOW...','IT WORKS','EVERY TIME.'],{'EVERY','TIME.'})]
def subtitles(d,t):
    for key,t0,t1,lines,hil in SUBS:
        if t0<=t<t1:
            y0=50
            for i,l in enumerate(lines):
                x=(W-font.width(l,2))//2
                for wd in l.split(' '): otext(d,wd,x,y0+i*17,YEL if wd in hil else WHT,2); x+=font.width(wd,2)+12
def hud(d,vi,t,cs):
    n=sum(1 for tl in T_LAND if t>=tl)
    if 3.0<=t<T_ALL:                                                                  # BUTTON n/3 counter
        s_=f'BUTTON {n} / 3'; pop=1.0+0.0*seg01(t,T_LAND[n-1],T_LAND[n-1]+0.2) if n else 1.0
        panel(d,14,8,166,30,CYAN); ctext(d,s_,13,YEL if n and t<T_LAND[n-1]+0.4 and int(t*10)%2 else WHT,2)
        for k in range(3): d.rectangle([66+k*18,34,78+k*18,40],fill=GRN if k<n else (50,46,70),outline=WHT)
    if T_ALL<=t<T_CLICK:
        panel(d,14,8,166,30,GRN); ctext(d,'BUTTON 3 / 3',13,GRN if int(t*10)%2 else WHT,2)
        for k in range(3): d.rectangle([66+k*18,34,78+k*18,40],fill=GRN,outline=WHT)
    if T_CLICK<=t<12.0:                                                               # SECRET FOUND + the "!" gag above the cat
        a=sm(seg01(t,T_CLICK,T_CLICK+0.12)); c=YEL if int(t*8)%2 else WHT; y=int(lerp(-30,10,a))
        panel(d,14,y-2,166,y+24,c,(30,22,6)); ctext(d,'SECRET FOUND',y+4,c,2)
        if t<T_CLICK+0.7:
            p=R.project(tuple(np.array(CD.head_world(cs))+np.array([0,0.24,0])),vi)
            if p:
                x,yy=W-1-int(p[0]),int(p[1]-6*seg01(t,T_CLICK,T_CLICK+0.15)); d.rectangle([x-6,yy-10,x+6,yy+8],fill=WHT,outline=(0,0,0)); d.polygon([(x-2,yy+8),(x+2,yy+8),(x,yy+11)],fill=WHT); font.text(d,'!',x-2,yy-7,RED,1,None)
    if t>=T_FOOD[1]-0.1:                                                               # FOOD UNLOCKED
        a=sm(seg01(t,T_FOOD[1]-0.1,T_FOOD[1]+0.05)); c=YEL if int(t*6)%2 else WHT; y=int(lerp(-30,10,a))
        panel(d,10,y-2,170,y+24,GRN,(6,30,10)); ctext(d,'FOOD UNLOCKED',y+4,c,2)
def frame(t):
    img,vi,cs=render(t); d=ImageDraw.Draw(img); hud(d,vi,t,cs); subtitles(d,t); return img

# ======================= QA manifest =======================
def _cat_model(**st): return cat_model(**st)[0]
def _extra(t):
    out=[]; cs=cat_state(t)
    V=np.array([v for q in cat_model(**{**cs,'paw':0.0})[0] for v in q['p']],float)      # cat body without the paw (the paw is meant to touch)
    for i in range(3):
        c,_=obj_state(i,t); O=np.array([v for q in obj_quads(i,t) for v in q['p']],float); lo,hi=O.min(0)-0.005,O.max(0)+0.005
        if np.all((V>lo)&(V<hi),axis=1).any(): out.append(('intersect',f'cat touches object {i+1}'))
        if t>=T_LAND[i] and abs(c[2]-PAD_Z)>0.01: out.append(('physics',f'object {i+1} is not on its pad'))
    b=np.array(cs['base'])
    if t<T_GO[0] and b[2]+0.13+0.05>TAB['z0']: out.append(('intersect','cat front feet inside the shelf'))
    if b[2]-0.34<-2.9: out.append(('wall','tail in the back wall'))
    if t<T_TAP[2]+SLIDE+FALL and t>=T_CLICK-1: out.append(('order','dispenser before third press'))
    if b[0]+0.15>DISP['x0'] and b[2]-0.15<DISP['z1']: out.append(('intersect','cat in the dispenser'))
    return out
QA=dict(fps=FPS,dur=DUR,W=W,frame=frame,chars={'cat':(cat_state,_cat_model,'_none',1.0)},
    geom=lambda t,name,st,V: [('floor',f'{name} under the floor')] if V[:,1].min()<-0.04 else [],extra=_extra,
    camera=lambda t: shot(t)['cam'],min_cam_dist=0.4,camera_ok=lambda p: 0.2<p[1]<1.4 and abs(p[0])<1.6 and -2.8<p[2]<1.2,
    allow_jump=[],
    scenes=[dict(id='s1-hook',t0=0.0,t1=3.0,action='the cat swipes the book to the shelf edge, two nudges, final tap: it falls'),
            dict(id='s2-click',t0=3.0,t1=6.0,action='book lands on pad 1 (BUTTON 1/3); the cat looks down, steps right, swipes the mug'),
            dict(id='s3-test',t0=6.0,t1=9.0,action='mug lands on pad 2; the cat steps to the pot, pushes it to the edge, glances at us, taps it'),
            dict(id='s4-secret',t0=9.0,t1=12.0,action='pot lands on pad 3, all pads flash, pause, the cat looks right, dispenser clicks: SECRET FOUND'),
            dict(id='s5-food',t0=12.0,t1=DUR,action='kibble drops, FOOD UNLOCKED, the cat glances at us, walks over and eats')],
    weapon_events=[],texts=lambda: [('sub',l,2) for _,_,_,ls,_ in SUBS for l in ls]+[('ui',s_,2) for s_ in ('BUTTON 0 / 3','BUTTON 3 / 3','SECRET FOUND','FOOD UNLOCKED')])

TEST=os.environ.get('TEST')
if TEST and __name__=='__main__':
    ims=[frame(float(x)) for x in TEST.split(',')]; shp=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): shp.paste(im,(i*182,0))
    shp.resize((shp.width*2,640),Image.NEAREST).save(os.environ.get('TEST_OUT','test.png')); sys.exit()

# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=31); sr=s.sr; n=s.n; M=np.zeros(n); AMB=np.zeros(n)
    def note(buf,t0,m,d,v,wave='sq',duty=0.5,dec=3.0,att=0.005):
        f=440*2**((m-69)/12); tt=s.T(d); ph=(f*tt)%1
        x=np.where(ph<duty,1.0,-1.0) if wave=='sq' else (4*np.abs(ph-0.5)-1 if wave=='tri' else np.sin(2*np.pi*ph))
        env=np.minimum(1,tt/att)*np.exp(-tt*dec); i=int(t0*sr); j=min(n,i+len(tt)); buf[i:j]+=(x*env*v)[:j-i]
    def nb(t0,d,lo,hi,v,seed,shape=2): s.place(s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v)
    def thud(t0,f=55,v=0.25,d=0.5): tt=s.T(d); s.place(np.sin(2*np.pi*f*tt*(1-0.35*tt/d))*np.exp(-tt*9)+s.filt_short(s.noise(d,int(t0*13)),lo=50,hi=600)*np.exp(-tt*12)*0.5,t0,v)
    def tick(t0,v=0.03,f=2300,dec=120): tt=s.T(0.04); s.place(np.sin(2*np.pi*f*tt)*np.exp(-tt*dec),t0,v)
    def whoosh(t0,d=0.3,v=0.04,seed=0,lo=500,hi=4000): nb(t0,d,lo,hi,v,seed)
    def drop(t0,k):                                                       # three distinct object falls
        whoosh(t0-0.22,0.22,0.03,40+k,600+300*k,4000)
        if k==0: thud(t0,70,0.22,0.3); nb(t0,0.08,300,2000,0.06,51,1)       # book: flat paper thump
        if k==1: thud(t0,110,0.14,0.2); tick(t0+0.01,0.06,1900,40); tick(t0+0.03,0.03,2900,60)   # mug: ceramic clink
        if k==2: thud(t0,60,0.2,0.35); nb(t0,0.12,150,900,0.08,52,1)        # pot: dull clay thud
    def click(t0,k): tick(t0+0.02,0.09,1500+200*k,90); tick(t0+0.06,0.05,900,90); note(M,t0+0.08,79+4*k,0.12,0.04,'sq',0.25,10)
    AMB+=s.filt(s.rng.normal(0,1,n),lo=60,hi=500)*0.007
    # ---------- music: light playful loop (pizzicato square + tri bass), stops before the click ----------
    bass=[48,55,52,55,50,57,53,57]; mel=[72,0,76,79,0,76,72,0,74,0,77,81,0,77,74,0]; step=0.1875; tc=0.0; k=0
    while tc<12.0-1e-6:
        if 9.55<=tc<T_CLICK+0.25: tc+=step; k+=1; continue                         # the tiny pause before the dispenser
        if k%2==0: note(M,tc,bass[(k//2)%8]-12,step*1.6,0.05,'tri',dec=6)
        if mel[k%16]: note(M,tc,mel[k%16],step*0.5,0.016,'sq',0.25,12)
        if k%4==2: nb(tc,0.04,4000,9000,0.012,int(tc*100),1)
        tc+=step; k+=1
    for k2,m in enumerate((60,64,67,72,76,79,84)): note(M,12.0+k2*0.05,m,0.2,0.02,'sq',0.5,6)        # payoff run
    tc=12.4; k=0
    while tc<DUR-0.3:
        if k%2==0: note(M,tc,bass[(k//2)%8]-12,step*1.6,0.05,'tri',dec=6)
        if mel[(k+8)%16]: note(M,tc,mel[(k+8)%16]+5,step*0.5,0.015,'sq',0.25,12)
        tc+=step; k+=1
    # ---------- sfx ----------
    for k2 in range(3):
        a,b=T_PUSH[k2]; nb(max(0.0,a+0.05),max(0.1,b-max(0.0,a+0.05)),800,3000,0.02,60+k2,1)            # object slides on wood
        tick(T_TAP[k2]-0.02,0.03,1200,80)                                                                 # paw tap
        drop(T_LAND[k2],k2); click(T_LAND[k2],k2)
    for tt in (1.45,2.05): tick(tt,0.02,900,70)                                                           # nudges
    for k2 in range(3): note(M,T_ALL+0.02+k2*0.08,84+k2*3,0.1,0.035,'sq',0.5,10)                         # all three lit
    tick(T_CLICK,0.14,700,50); thud(T_CLICK,90,0.14,0.15); tick(T_CLICK+0.09,0.08,1300,60); nb(T_FLAP[0]+0.02,0.2,400,2500,0.05,70,1)   # dispenser activation
    for k2 in range(7): tick(T_FOOD[0]+0.07*k2+0.32,0.035,2500+300*(k2%3),110)                           # food drop
    nb(T_FOOD[0],0.4,1500,6000,0.03,71,1)
    for k2,m in enumerate((76,79,84,88)): note(M,T_FOOD[1]+k2*0.07,m,0.25,0.04,'sq',0.5,5)              # success chime
    for k2 in range(int((T_GO[1]-T_GO[0])/0.18)): tick(T_GO[0]+k2*0.18,0.008,600,90)                       # soft paw steps
    for k2 in range(int((DUR-T_EAT-0.2)/0.22)): tick(T_EAT+0.2+k2*0.22,0.02,1700,60); tick(T_EAT+0.26+k2*0.22,0.012,2400,80)   # crunch
    # ---------- voice ----------
    NB=np.zeros(n); duck=np.ones(n)
    for key,t0,_,_,_ in SUBS:
        a,ar=_sf.read(os.path.join(TTS_DIR,'cs',key+'.wav')); a=a if a.ndim==1 else a.mean(1)
        a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a); act=a[np.abs(a)>0.02]; a=a/(np.sqrt((act**2).mean())+1e-9)*0.2
        i=int(t0*sr); j=min(n,i+len(a)); NB[i:j]+=a[:j-i]; duck[max(0,i-int(0.08*sr)):min(n,j+int(0.15*sr))]=0.45
    duck=np.convolve(duck,np.ones(2400)/2400,'same')
    s.L+=2.0*M*duck+AMB; s.R+=2.0*np.roll(M,240)*duck+np.roll(AMB,700)
    s.reverb(0.12,length=1.0,decay=4.0)
    pk=max(np.abs(s.L).max(),np.abs(s.R).max()); gv=pk*1.0/np.abs(NB).max()
    s.L=s.L*(0.7+0.3*duck)+NB*gv; s.R=s.R*(0.7+0.3*duck)+NB*gv
    st=np.stack([s.L,s.R],1); k=int(0.3*sr); st[-k:]*=np.linspace(1,0,k)[:,None]
    st=st/np.max(np.abs(st))*0.9; _sf.write(path,st,sr,subtype='PCM_16'); return path
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'cat_switch.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'cs_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.96,vignette=0.22,grain=1.5,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(post.upscale(frame(f/FPS),S),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
