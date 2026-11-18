"""THE LIGHTNING MISSED - series "What Happens Next?" (Insert Disc 2). PS1 science-suspense short, 9:16, fully procedural (nightkit).
A knight is never hit by lightning, yet his HP drops: ground current. He reaches the guardhouse and "equips the castle".
Brief + decisions: briefs/lightning_missed.md. Voice: python tools/tts/lm.py -> $TTS_DIR/lm/*.wav (80 words, bm_george).
Reuses the locked knight from examples/final_boss.py (+ a NEW shield prop and crouch/inspect poses built on the same knight()).
Run: TEST=0.2,3,6 python examples/lightning_missed.py -> test.png | PART=a:b (frames -> out/lm_a.mp4) | PART=audio"""
import os, sys, math, json
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','tts'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, quad
from nightkit import motion, post, font
from nightkit.zraster import zrender
from nightkit.audio import Sound, duck_envelope
import final_boss as FB                                   # locked knight model + geometry helpers

OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6; DUR=33.0; N=int(round(DUR*FPS))
PI=math.pi; sm=motion.smooth
def seg01(t,a,b): return max(0.0,min(1.0,(t-a)/(b-a)))
def lerp(a,b,u): return a+(b-a)*u
def lerp3(a,b,u): return tuple(a[i]+(b[i]-a[i])*u for i in range(3))
box=FB.box; xform=FB.xform
WHT=(242,238,226); YEL=(255,210,60); RED=(240,50,40); GRN=(80,220,90); CYAN=(70,230,255); BLU=(110,170,255)

# ======================= voice timings (locked in briefs/lightning_missed.md) =======================
LINES=[('1',0.25),('2',4.57),('3',8.16),('4',12.87),('5',16.23),('6',21.5),('7',26.18),('8',28.8)]
try: SCR=json.load(open(os.path.join(TTS_DIR,'lm','script.json')))
except Exception: SCR=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','tools','tts','scripts','lm_text.json')))
CUTS=[0.0,4.57,12.87,26.0,DUR]                            # CAM 01 | CAM 02 | CAM 03 (replay) | CAM 04
S1,S2,S3=0.0,9.8,28.5                                     # lightning strikes 1, 2, 3
REPLAY0,REPLAY1=12.87,26.0
def replay_clock(t): return 9.4+(t-REPLAY0)*0.121       # slow motion: strike 2 (9.8) lands at t=16.9

# ======================= LOCKED ASSET: the courtyard =======================
STONE=(70,76,92); STONE_D=(52,57,70); STONE_L=(92,98,116); CHAR=(22,20,24); WOOD=(92,62,36); DARKR=(120,22,30); DARKR2=(86,14,22)
PILLAR=(-2.2,3.6); PW=0.8; PH=2.9                          # pillar centre x,z / width / height (1.6 x knight)
GX=3.3; ZF=4.6; DW=1.3; DH=2.4; FH=3.8                     # guardhouse door centre x, facade plane z, door width/height, facade height
HINGE=GX-DW/2; FACADE=(GX-2.4,GX+2.4)
def floor_tiles():
    Q=[]
    for i in range(-8,10):
        for j in range(-6,10):
            c=(74,82,102) if (i+j)%2 else (60,66,84)
            Q.append(quad([(i,0,j),(i+1,0,j),(i+1,0,j+1),(i,0,j+1)],c))
    return Q
def courtyard():
    Q=floor_tiles()
    Q+=box(-9,11,0,3.2,9.5,10.2,STONE_D)                                       # back wall
    for k in range(-9,11,2): Q+=box(k,k+1,3.2,3.7,9.5,10.2,STONE_D)            # crenellations
    Q+=box(-8.4,-7.6,0,3.0,-3,10,STONE_D)                                      # left wall
    for z in range(-3,10,2): Q+=box(-8.4,-7.6,3.0,3.5,z,z+1,STONE_D)
    Q+=box(10.6,11.4,0,3.0,-3,10,STONE_D)                                      # right wall
    for tx in (-7.4,9.6):                                                       # corner towers: the castle behind the guardhouse
        Q+=box(tx-1.2,tx+1.2,0,6.6,8.6,10.6,STONE)+box(tx-1.5,tx+1.5,6.6,7.0,8.3,10.9,STONE_L)
        for kx in (-1.3,0.0,1.3): Q+=box(tx+kx-0.3,tx+kx+0.3,7.0,7.5,8.3,8.9,STONE_L)
    return Q
def pillar(charred):
    x,z=PILLAR; c=CHAR if charred else STONE; cl=(40,36,42) if charred else STONE_L
    return box(x-PW/2,x+PW/2,0,PH,z-PW/2,z+PW/2,c)+box(x-PW/2-0.08,x+PW/2+0.08,PH,PH+0.22,z-PW/2-0.08,z+PW/2+0.08,cl)+box(x-PW/2-0.08,x+PW/2+0.08,0,0.25,z-PW/2-0.08,z+PW/2+0.08,cl)
def guardhouse(door):
    """door: 0 = shut ... 1 = open (leaf swung outward, 90 deg). Facade with one door, solid roof, a dark enclosed entrance volume."""
    a,b=FACADE; Q=[]
    Q+=box(a,HINGE,0,FH,ZF,ZF+0.5,STONE)+box(GX+DW/2,b,0,FH,ZF,ZF+0.5,STONE)    # facade left / right of the door
    Q+=box(HINGE,GX+DW/2,DH,FH,ZF,ZF+0.5,STONE)                                 # lintel
    Q+=box(a-0.2,b+0.2,FH,FH+0.35,ZF-0.3,ZF+3.4,STONE_D)                        # roof
    Q+=box(a,b,0,FH,ZF+3.0,ZF+3.5,STONE_D)+box(a,a+0.4,0,FH,ZF,ZF+3.5,STONE_D)+box(b-0.4,b,0,FH,ZF,ZF+3.5,STONE_D)   # back + side walls
    Q+=box(HINGE,GX+DW/2,-0.02,0.0,ZF,ZF+3.0,(10,9,14))                          # dark floor of the entrance
    for k in range(4): Q+=box(a+0.3+k*1.18,a+0.9+k*1.18,2.9,3.2,ZF-0.08,ZF,STONE_L)                    # cornice blocks
    ang=door*PI/2                                                                 # leaf hinged at x=HINGE, swings toward -z
    def rot(p): x,y,zz=p; dx=x-HINGE; dz=zz-ZF; return (HINGE+dx*math.cos(ang)-dz*math.sin(ang),y,ZF+dx*math.sin(ang)+dz*math.cos(ang))
    Q+=box(HINGE,HINGE+DW,0.0,DH-0.05,ZF-0.08,ZF+0.04,WOOD,xf=rot)+box(HINGE+0.05,HINGE+DW-0.05,0.9,1.0,ZF-0.1,ZF-0.08,(60,56,60),xf=rot)+box(HINGE+DW-0.25,HINGE+DW-0.15,1.0,1.1,ZF-0.12,ZF-0.08,(200,170,70),xf=rot)
    return Q
COURT=courtyard()

# ======================= LOCKED ASSET: the knight + shield =======================
def _shield(base,yaw,lh,lean=0.0,run=0.0,sit=0.0):
    """dark-red shield (0.55 x the knight's height) fixed to the left hand, built in the same space as FB.knight's torso"""
    b=np.array(base,float); Rb=FB.Ry(yaw); hip=0.82-0.42*sit
    def T(p):
        p=np.array(p,float); piv=np.array([0,hip,0]); return tuple(b+Rb@(piv+FB.Rx(lean+0.22*run)@(p-piv+np.array([0,hip-0.82,0]))))
    h=np.array(lh,float); Q=[]
    cx,cy,cz=h[0]-0.06,h[1]+0.02,h[2]+0.1
    Q+=box(cx-0.26,cx+0.26,cy-0.5,cy+0.5,cz,cz+0.07,DARKR,xf=T)
    Q+=box(cx-0.22,cx+0.22,cy-0.44,cy+0.44,cz+0.07,cz+0.085,DARKR2,xf=T)
    Q+=box(cx-0.05,cx+0.05,cy-0.12,cy+0.12,cz+0.085,cz+0.12,FB.GOLD,xf=T)                    # boss stud
    return Q
IDLE_LH=(-0.27,0.86,0.04)
def kmodel(**st):
    st=dict(st); st.pop('shield',None); lh=st.get('lh') or IDLE_LH; st['lh']=lh
    return FB.knight(**st)+_shield(st['base'],st['yaw'],lh,st.get('lean',0.0),st.get('run',0.0),st.get('sit',0.0))
START=(-1.0,0.0,2.0); CROUCH=(2.2,0.0,3.0); DOOR_IN=(GX,0.0,ZF+1.6)
def kstate(t):
    """the knight in story time"""
    base=START; yaw=PI; d=dict(walk=0.0,run=0.0,lean=0.0,head=0.0,sit=0.0,lh=IDLE_LH,rh=None,sword='none')
    if t<0.9:                                                                   # strike 1: recoil, shield arm jerks up
        d['lean']=-0.32*math.sin(PI*seg01(t,0.0,0.7)); u=seg01(t,0.3,0.9)
        d['lh']=lerp3(IDLE_LH,(-0.36,1.3,0.18),math.sin(PI*u))
    elif t<4.57:                                                                # stands, looks at the shield
        d['lean']=0.02*math.sin(t*3); d['head']=0.9*sm(seg01(t,3.0,4.2))
    elif t<6.3:                                                                 # inspects the shield
        u=sm(seg01(t,4.65,5.2))*(1-sm(seg01(t,5.9,6.3))); d['lh']=lerp3(IDLE_LH,(-0.1,1.42,0.4),u); d['head']=0.9*(1-u)+0.1*u
    elif t<8.16:                                                                # notices the guardhouse, turns +x
        u=sm(seg01(t,6.3,7.4)); yaw=lerp(PI,PI/2,u); d['head']=-0.5*math.sin(PI*seg01(t,6.3,7.4))
    elif t<S2+0.45:                                                             # sprints toward the guardhouse
        u=seg01(t,8.1,S2+0.1); e=u*u*(3-2*u) if u<1 else 1.0
        base=lerp3(START,CROUCH,0.0); base=(lerp(START[0],CROUCH[0],e),0.0,lerp(START[2],CROUCH[2],e)); yaw=PI/2-0.25*(1-u)
        d['walk']=t*17; d['run']=min(1.0,seg01(t,8.1,8.4)); d['rh']=None
    else:                                                                       # stagger, crouch, stays low
        k=seg01(t,S2+0.1,S2+0.45); base=(CROUCH[0],0.0,CROUCH[2]); yaw=PI/2
        d['sit']=0.55*sm(k); d['lean']=0.35*math.sin(PI*seg01(t,S2+0.1,S2+0.7))*(1-sm(seg01(t,S2+0.7,S2+0.9)))+0.12
        d['head']=-0.4*sm(seg01(t,11.1,11.6)); d['lh']=lerp3(IDLE_LH,(-0.3,0.98,0.2),sm(k))
        if t>=12.4:                                                             # gets up and walks the last metres (off-screen during the replay)
            u=sm(seg01(t,12.4,13.2)); d['sit']=0.55*(1-u); d['lean']=0.12*(1-u)
            if t>=13.2:
                e=seg01(t,13.2,25.5); x=lerp(CROUCH[0],GX+0.1,sm(e)); z=lerp(CROUCH[2],ZF-0.7,sm(e))
                base=(x,0.0,z); yaw=lerp(lerp(PI/2,0.5,sm(seg01(t,13.2,14.2))),0.0,sm(seg01(t,24.5,26.0))); d['walk']=t*9; d['run']=0.0
            if t>=25.5:                                                         # through the door and in
                e=seg01(t,REPLAY1,27.45); base=(GX+0.1,0.0,lerp(ZF-0.7,ZF+1.6,sm(e))); yaw=0.0; d['walk']=t*9
    return dict(base=base,yaw=yaw,**d)
def view_state(t):
    """the pose the camera sees: during the replay a slowed copy of the stagger/crouch"""
    if REPLAY0<=t<REPLAY1: return kstate(min(replay_clock(t),12.3))
    return kstate(t)

# ======================= cameras =======================
def creep(t,t0,rate=0.0016): return motion.creep(t,t0,rate,FPS)
def cam_shot(t):
    if t<CUTS[1]:  # CAM 01: close three-quarter, knight fills ~55 % of the height, slow push
        k=creep(t,0.0,0.0022); tgt=(-1.0,1.0,2.0); pos=motion.dolly((-0.55,1.25,0.5),tgt,k); return dict(cam=pos,tgt=tgt,fov=62)
    if t<CUTS[2]:  # CAM 02: wide, pillar left / guardhouse right, tracking glide 8.1-9.3 then push
        g=motion.glide(seg01(t,8.1,9.3)); tgt=lerp3((-0.3,1.0,3.5),(1.2,1.0,3.6),g); pos0=lerp3((-0.3,1.5,-0.1),(0.5,1.4,0.1),g)
        pos=motion.dolly(pos0,tgt,creep(t,CUTS[1],0.0014)); return dict(cam=pos,tgt=tgt,fov=70)
    if t<CUTS[3]:  # CAM 03: low three-quarter on the boots (both on adjacent tiles), slow orbit-like glide at 21.4
        g=motion.glide(seg01(t,21.4,23.2)); tgt=(2.25,0.65,3.0)
        pos0=lerp3((4.3,1.1,0.9),(3.9,0.85,0.5),g); pos=motion.dolly(pos0,tgt,creep(t,CUTS[2],0.0013)); return dict(cam=pos,tgt=tgt,fov=52)
    g=motion.glide(seg01(t,29.0,31.0)); tgt=lerp3((3.0,1.4,4.6),(3.0,1.9,6.0),g); pos0=lerp3((1.0,1.6,1.5),(1.6,2.3,-2.2),g)
    pos=motion.dolly(pos0,tgt,creep(t,31.0 if t>=31.0 else CUTS[3],0.0012)); return dict(cam=pos,tgt=tgt,fov=lerp(64,72,g))   # CAM 04: pulls back to show the castle
def flash_amt(t):
    f=0.0
    for s,v in ((S1,1.0),(S2,1.0),(S3,0.4),(16.9,0.35)):
        if t>=s: f=max(f,v*math.exp(-(t-s)*13)+v*0.4*math.exp(-abs(t-(s+0.19))*60))
    return min(1.0,f)
def shake_px(t):
    for s in (S1,S2,S3,27.55):                                                  # strikes and the door slam: 7-frame flip-sign kick
        k=motion.kick(t,s,2.2 if s!=S3 else 1.0,7,FPS)
        if k: return (0.0,k)
    return (0.0,0.0)

# ======================= render =======================
R=Renderer(W,H,fog=(14,18,30))
def overlay_tiles(t):
    """the educational replay overlay: ground-current bands (from 17.6), HIGH / LOW tinted tiles (from 22.2). Never shown outside the replay."""
    if not (REPLAY0<=t<REPLAY1): return []
    Q=[]; fade=1.0-seg01(t,25.2,REPLAY1)
    if t>=17.6 and fade>0:
        sx,sz=1.0,2.2; r0=((t-17.6)*1.25)%3.2
        for ring in range(3):
            r=(r0+ring*1.1)%3.4; a=1.0-r/3.4
            if a<=0.05: continue
            col=tuple(int(c*a*fade*0.85) for c in CYAN)
            n=18
            for k in range(n):
                a0=-PI*0.15+PI*1.3*k/n+PI*0.0; a1=-PI*0.15+PI*1.3*(k+1)/n
                P=[(sx+math.cos(a0)*r,0.012,sz+math.sin(a0)*r),(sx+math.cos(a1)*r,0.012,sz+math.sin(a1)*r),(sx+math.cos(a1)*(r+0.3),0.012,sz+math.sin(a1)*(r+0.3)),(sx+math.cos(a0)*(r+0.3),0.012,sz+math.sin(a0)*(r+0.3))]
                if all(-8<=p[0]<=10 and -6<=p[2]<=10 for p in P): Q.append(quad(P,col,True))
    if t>=22.2 and fade>0:
        pulse=0.75+0.25*math.sin(t*9)
        for (i,j),c in (((2,2),(255,120,50)),((2,3),(60,120,255))):
            Q.append(quad([(i+0.03,0.02,j+0.03),(i+0.97,0.02,j+0.03),(i+0.97,0.02,j+0.97),(i+0.03,0.02,j+0.97)],tuple(int(v*pulse*fade) for v in c),True))
    return Q
def render3d(t):
    sh=cam_shot(t); cam=Camera.look(sh['cam'],sh['tgt']); st=view_state(t)
    door=1.0
    if t>=REPLAY1: door=1.0-sm(seg01(t,27.15,27.55))
    charred=t>=6.0
    Q=[COURT,pillar(charred),guardhouse(door),kmodel(**st),overlay_tiles(t)]
    fl=flash_amt(t); L=[((GX-1.0,3.0,ZF-2.0),(190,215,255),0.5+3.0*fl),((-1.5,4.0,2.5),(170,190,255),0.3+2.2*fl)]
    img,vi,zb=zrender(R,cam,Q,L,fov=sh['fov'],fog_start=7,fog_end=26,ambient=0.68,shake=shake_px(t),return_z=True)
    a=np.asarray(img).astype(np.float32); yy=np.linspace(0,1,H)[:,None,None]
    sky=(np.array([20,26,46])*(1-yy)+np.array([40,48,76])*yy)*np.ones((1,W,1))
    a=np.where((zb==0)[...,None],sky,a)
    a=a+fl*np.array([150,160,185])*0.55                                        # screen flash
    if REPLAY0<=t<REPLAY1: a=a*np.array([0.78,0.95,1.0])+np.array([0,6,12])     # replay look: slightly cyan and dim
    return post.ps1(Image.fromarray(np.clip(a,0,255).astype(np.uint8))),vi

# ======================= HUD / UI (2D overlays) =======================
def otext(d,s,x,y,col,sc=1):
    o=max(1,sc//2)
    for ox,oy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)): font.text(d,s,x+ox*o,y+oy*o,(0,0,0),sc,None)
    font.text(d,s,x,y,col,sc,None)
def ctext(d,s,y,col,sc=1): otext(d,s,(W-font.width(s,sc))//2,y,col,sc)
def hp_value(t):
    if t<2.8: return 100.0
    if t<3.2: return lerp(100,50,sm(seg01(t,2.8,3.2)))
    if t<11.3: return 50.0
    if t<11.6: return lerp(50,1,sm(seg01(t,11.3,11.6)))
    return 1.0
def hud(d,t,vi):
    v=hp_value(t); small=v>=1.0 and t>=REPLAY0 and False
    col=GRN if v>60 else (YEL if v>20 else RED)
    otext(d,'HP',8,8,WHT); n=str(int(round(v))); otext(d,n,8+font.width('HP',1)+6,8,col)
    d.rectangle([8,19,76,24],fill=(0,0,0),outline=(200,200,210)); d.rectangle([9,20,9+int(66*v/100.0),23],fill=col)
    if 11.6<=t<12.87 and int(t*6)%2==0: ctext(d,'1 HP',70,RED,3)
    if 0.1<=t<1.7 and int(t*12)%3!=2:                                          # MISS beside the pillar
        p=R.project((PILLAR[0]+0.4,2.1,PILLAR[1]-0.5),vi)
        if p: otext(d,'MISS',int(min(W-26,max(2,p[0]))),int(p[1]),YEL,1)
    if 10.0<=t<10.9:                                                           # strike 2 also "MISS"
        p=R.project((1.6,0.3,2.0),vi)
        if p: otext(d,'MISS',int(min(W-26,max(2,p[0]))),int(p[1]),YEL,1)
    if REPLAY0<=t<REPLAY1:
        if int(t*2)%2==0: d.polygon([(W-50,8),(W-50,16),(W-44,12)],fill=RED)
        otext(d,'REPLAY',W-40,8,WHT)
        if 13.7<=t<19.6: ctext(d,'HIT SOURCE: ???',44,YEL)
        if 19.6<=t<REPLAY1-0.4: ctext(d,'GROUND CURRENT',44,CYAN)
        if t>=22.2 and t<REPLAY1-0.4:
            for lab,(x,z),c in (('HIGH',(2.5,2.5),(255,150,70)),('LOW',(2.5,3.5),(110,170,255))):
                p=R.project((x,0.05,z),vi)
                if p: otext(d,lab,int(p[0])-font.width(lab)//2+(10 if lab=='HIGH' else -10),int(p[1])+8,c)
        if t>=23.4 and t<REPLAY1-0.4: path_overlay(d,vi,t)
    if t>=28.9 and t<30.0: ctext(d,'NO DAMAGE',120,GRN,2)
    if t>=29.2: equip(d,t)
def path_overlay(d,vi,t):
    """schematic path of the current through the lower body (an explanatory drawing, not a discharge)"""
    pts=[(2.5,0.03,2.5),(2.23,0.12,2.84),(2.23,0.75,3.0),(2.23,0.12,3.16),(2.5,0.03,3.5)]
    P=[R.project(p,vi) for p in pts]
    if not all(P): return
    u=seg01(t,23.4,24.4); n=max(1,int(u*(len(P)-1)));
    for i in range(n):
        a,b=P[i],P[i+1]; d.line([a[0],a[1],b[0],b[1]],fill=CYAN,width=2)
    for p in P[:n+1]: d.rectangle([p[0]-1,p[1]-1,p[0]+1,p[1]+1],fill=WHT)
def equip(d,t):
    """equipment slot: shield icon -> castle icon, then EQUIPPED: CASTLE"""
    x0,y0=W//2-12,100-34; d.rectangle([x0-3,y0-3,x0+27,y0+27],fill=(10,10,16),outline=(200,200,210))
    if t<30.6:                                                                  # shield icon
        d.rectangle([x0+4,y0+2,x0+20,y0+22],fill=(120,22,30),outline=WHT); d.rectangle([x0+10,y0+8,x0+14,y0+14],fill=FB.GOLD)
        if t>=30.1: d.line([x0+2,y0+2,x0+22,y0+22],fill=RED,width=2)
    else:                                                                       # castle icon
        d.rectangle([x0+3,y0+10,x0+21,y0+23],fill=(150,156,176),outline=WHT)
        for k in (3,9,15): d.rectangle([x0+k,y0+5,x0+k+4,y0+10],fill=(150,156,176),outline=WHT)
        d.rectangle([x0+9,y0+15,x0+15,y0+23],fill=(20,18,26))
    if t>=31.2: ctext(d,'EQUIPPED:',112,WHT,1); ctext(d,'CASTLE',124,YEL,3)
def bolt(d,vi,t):
    """white jagged bolt, 3 frames, from the top of the frame to the strike point (strike 1: pillar top; 2 and the replay: the ground)"""
    for s,P3 in ((S1,(PILLAR[0],PH,PILLAR[1])),(S2,(1.0,0.0,2.2)),(16.9,(1.0,0.0,2.2)),(S3,(1.5,0.0,3.6))):
        if s<=t<s+3/FPS:
            p=R.project(P3,vi)
            if not p: return
            rng=np.random.default_rng(int(s*10)+int((t-s)*FPS)); x=p[0]+float(rng.uniform(-18,18)); y=0.0; pts=[(x,y)]
            while y<p[1]-6:
                y+=float(rng.uniform(10,22)); x=lerp(x,p[0],0.35)+float(rng.uniform(-9,9)); pts.append((x,min(y,p[1])))
            pts.append((p[0],p[1])); w=3 if s!=S3 else 2
            d.line(pts,fill=(170,200,255),width=w+2); d.line(pts,fill=(255,255,255),width=w-1 if w>2 else 1)
def frame_low(t):
    img,vi=render3d(t); d=ImageDraw.Draw(img); bolt(d,vi,t); hud(d,t,vi); return img

# ======================= subtitles (1080x1920, 1.25x like lighthouse) =======================
SUB_F=7.5; HIL={'LIGHTNING','MISSES','HEALTH','HP','SHIELD','PILLAR','VOLTAGES','CURRENT','GROUND','CASTLE','BOOTS','DOOR'}
def _rows(text,n=20):
    out=[]; c=[]
    for w_ in text.split():
        if len(' '.join(c+[w_]))>n and c: out.append(c); c=[w_]
        else: c.append(w_)
    return out+[c]
def sub_chunks():
    out=[]
    for k,t0 in LINES:
        for a_,b_,txt in _split_line(k,t0): out.append((a_,b_,_rows(txt),k))
    return out
def _split_line(k,t0):
    """a line may hold several sentences: show them one after another across the line's real duration, by character share"""
    import re
    txt=SCR['text'][k]; dur=SCR['dur'][k]; sents=[s.strip() for s in re.split(r'(?<=[.!?])\s+',txt) if s.strip()]
    tot=sum(len(s) for s in sents); a=t0; res=[]
    for s in sents:
        b=a+dur*len(s)/tot; res.append((a-0.03,b+0.2 if s is sents[-1] else b,s)); a=b
    return res
SUBS=sub_chunks()
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

# ======================= QA manifest (tools/qa/scene_qa.py, PIPELINE.md) =======================
def _geom(t,name,st,V):
    out=[]
    if V[:,1].min()<-0.04: out.append(('floor',f'{name} under the floor'))
    px,pz=PILLAR; inp=(np.abs(V[:,0]-px)<PW/2-0.02)&(np.abs(V[:,2]-pz)<PW/2-0.02)&(V[:,1]<PH)
    if inp.any(): out.append(('intersect',f'{name} inside the pillar'))
    a,b=FACADE; door_ok=(V[:,0]>HINGE+0.02)&(V[:,0]<GX+DW/2-0.02)
    wall=(V[:,0]>a)&(V[:,0]<b)&(V[:,2]>ZF+0.02)&(V[:,2]<ZF+0.48)&(V[:,1]<FH)&~(door_ok&(V[:,1]<DH))
    if wall.any(): out.append(('wall',f'{name} inside the guardhouse facade'))
    return out
def _extra(t):
    out=[]; s=kstate(t)
    if t>=REPLAY0 and t<REPLAY1 and False: out.append(('x','x'))
    return out
QA=dict(fps=FPS,dur=DUR,W=W,frame=frame,chars={'knight':(kstate,kmodel,'sword','none')},
    geom=_geom,extra=_extra,camera=lambda t: cam_shot(t)['cam'],min_cam_dist=0.4,
    camera_ok=lambda p: -8<p[0]<10.5 and -4.5<p[2]<9 and 0.05<p[1]<8 and not (FACADE[0]<p[0]<FACADE[1] and p[2]>ZF-0.1),
    allow_jump=[('knight',t) for t in (REPLAY0,REPLAY1)]+[('knight',t+d/FPS) for t in (REPLAY0,REPLAY1) for d in (0,1,2)],weapon_events=[],
    scenes=[dict(id='hook',t0=0.0,t1=4.57,action='bolt hits the pillar, knight recoils, MISS, HP 100 -> 50 (CAM 01)',env='courtyard'),
            dict(id='shield',t0=4.57,t1=8.16,action='he inspects the shield, the pillar chars, he spots the guardhouse (CAM 02)',env='courtyard'),
            dict(id='run',t0=8.16,t1=12.87,action='sprints, bolt 2 lands behind him, crouch, HP 50 -> 1 (CAM 02)',env='courtyard'),
            dict(id='question',t0=12.87,t1=16.23,action='slow replay, HIT SOURCE: ??? (CAM 03)',env='courtyard'),
            dict(id='mechanism',t0=16.23,t1=21.35,action='ground-current bands spread, GROUND CURRENT (CAM 03)',env='courtyard'),
            dict(id='voltage',t0=21.35,t1=26.0,action='HIGH / LOW tiles, current path through the boots (CAM 03)',env='courtyard'),
            dict(id='shelter',t0=26.0,t1=29.14,action='reaches the guardhouse, slams the door, bolt 3 outside, NO DAMAGE (CAM 04)',env='courtyard + guardhouse'),
            dict(id='payoff',t0=29.14,t1=DUR,action='EQUIPPED: CASTLE (CAM 04)',env='courtyard + guardhouse')],
    texts=lambda: [(k,ln,1) for k in SCR['text'] for ln in []]+[('hud','HIT SOURCE: ???',1),('hud','GROUND CURRENT',1),('hud','EQUIPPED:',1),('hud','CASTLE',3),('hud','NO DAMAGE',2),('hud','1 HP',3),('hud','REPLAY',1)])

# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=31); sr=s.sr; n=s.n; t=s.t; BED=np.zeros(n); FX=np.zeros(n)
    def nb(buf,t0,d,lo,hi,v,seed,shape=2):
        x=s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape; i=int(t0*sr); j=min(n,i+len(x)); buf[i:j]+=(x*v)[:j-i]
    def tone(buf,t0,m,d,v,wave='sq',duty=0.5,dec=3.0,att=0.005):
        f=440*2**((m-69)/12); tt=s.T(d); ph=(f*tt)%1; x=np.where(ph<duty,1.0,-1.0) if wave=='sq' else (4*np.abs(ph-0.5)-1 if wave=='tri' else np.sin(2*np.pi*ph))
        e=np.minimum(1,tt/att)*np.exp(-tt*dec); i=int(t0*sr); j=min(n,i+len(tt)); buf[i:j]+=(x*e*v)[:j-i]
    def thud(t0,f=55,v=0.3,d=0.6): tt=s.T(d); x=np.sin(2*np.pi*f*tt*(1-0.3*tt/d))*np.exp(-tt*8)+s.filt_short(s.noise(d,int(t0*13)),lo=60,hi=700)*np.exp(-tt*12)*0.6; i=int(t0*sr); j=min(n,i+len(tt)); FX[i:j]+=(x*v)[:j-i]
    def crack(t0,v=0.5,seed=0): tt=s.T(0.35); x=s.filt_short(s.noise(0.35,seed),lo=1500,hi=9000)*np.exp(-tt*18); i=int(t0*sr); j=min(n,i+len(tt)); FX[i:j]+=(x*v)[:j-i]
    def thunder(t0,v=0.5,muff=False,seed=0):
        tt=s.T(3.0); x=s.filt_short(s.noise(3.0,seed),lo=25,hi=220 if not muff else 140)*np.exp(-tt*1.3)*np.minimum(1,tt/0.05); i=int(t0*sr); j=min(n,i+len(tt)); FX[i:j]+=(x*v*(2.2 if muff else 3.0))[:j-i]
        if not muff: crack(t0,v*0.9,seed+1); thud(t0,48,v*0.8,0.8)
    def step(t0,v=0.05,seed=0): tt=s.T(0.12); x=s.filt_short(s.noise(0.12,seed),lo=900,hi=5000)*np.exp(-tt*45)+np.sin(2*np.pi*2300*tt)*np.exp(-tt*60)*0.3; i=int(t0*sr); j=min(n,i+len(tt)); FX[i:j]+=(x*v)[:j-i]
    # ---------- storm bed (continuous, so no silent stretch) ----------
    BED+=s.filt(s.rng.normal(0,1,n),lo=40,hi=380)*0.16*(0.7+0.3*np.sin(2*np.pi*0.13*t))              # wind rumble
    BED+=s.filt(s.rng.normal(0,1,n),lo=2500,hi=9000)*0.05                                               # rain
    BED+=(np.sin(2*np.pi*52*t)+0.5*np.sin(2*np.pi*78*t+1.0))*0.02
    # ---------- strikes ----------
    thunder(S1,0.5,False,3); tone(FX,2.8,72,0.18,0.04,'sq',dec=14); tone(FX,3.0,60,0.2,0.04,'sq',dec=14)   # HP loss blips
    thunder(S2,0.6,False,8); thunder(16.9,0.18,False,12)                                               # replay strike: quiet
    thunder(S3,0.4,True,15)
    nb(FX,6.0,0.7,300,2500,0.06,5)                                                                      # stone chars
    for k in range(10): step(8.2+k*0.17,0.06,70+k)                                                      # sprint
    for k in range(8):  tone(FX,11.3+k*0.17,(96,88)[k%2],0.1,0.05,'sq',0.25,dec=14)                     # critical HP warning
    tone(FX,REPLAY0,88,0.12,0.05,'sq',dec=16); tone(FX,REPLAY0+0.11,93,0.12,0.05,'sq',dec=16)           # replay blip
    tt=s.T(2.5); i=int(REPLAY0*sr); FX[i:i+len(tt)]+=np.sin(2*np.pi*np.cumsum(70+10*np.sin(2*np.pi*0.8*tt))/sr)*np.minimum(1,tt/0.5)*np.exp(-tt*1.4)*0.08   # mystery cue
    tt=s.T(0.8); i=int(19.6*sr); FX[i:i+len(tt)]+=np.sin(2*np.pi*np.cumsum(400+1400*tt/0.8)/sr)*np.exp(-tt*3)*0.06                  # ground-current cue
    for k in range(3): tone(FX,22.2+k*0.2,(79,83,86)[k],0.3,0.04,'sin',dec=5)                                                    # HIGH / LOW cue
    tt=s.T(0.6); i=int(REPLAY1*sr); FX[i:i+len(tt)]+=np.sin(2*np.pi*np.cumsum(1500-1200*tt/0.6)/sr)*np.exp(-tt*5)*0.07            # back to reality
    for k in range(6): step(26.1+k*0.4,0.05,90+k)
    thud(27.55,38,0.9,1.0); nb(FX,27.55,0.25,300,2500,0.18,21)                                          # door slam
    tone(FX,28.9,91,0.15,0.04,'sq',dec=12); tone(FX,29.05,96,0.2,0.04,'sq',dec=10)                      # no-damage ping
    for k,m in enumerate((72,76,79,84)): tone(FX,31.0+k*0.08,m,0.5,0.05,'sin',dec=4)                    # equip chime
    tone(FX,31.9,84,0.8,0.05,'sin',dec=2.5)
    # ---------- voice ----------
    NB=np.zeros(n); wins=[]
    for k_,t0 in LINES:
        a,ar=_sf.read(os.path.join(TTS_DIR,'lm',f'{k_}.wav')); a=a if a.ndim==1 else a.mean(1)
        a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a); i=int(t0*sr); j=min(n,i+len(a)); NB[i:j]+=a[:j-i]; wins.append((t0,t0+len(a)/sr))
    g=duck_envelope(n,sr,wins,-4.0,0.05,0.25)                                                            # storm + effects dip under the narrator
    bed=BED*g; fx=FX*(0.5+0.5*g)
    L=bed+fx; R_=np.roll(bed,700)+np.roll(fx,200)
    pk=max(np.abs(L).max(),np.abs(R_).max()); gv=pk*1.6/np.abs(NB).max()
    s.L=L+NB*gv; s.R=R_+NB*gv; s.reverb(0.12,length=1.2,decay=3.0)
    return s.save(path,peak=0.9)
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'lightning_missed.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'lm_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.96,vignette=0.25,grain=1.5,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(frame_final(f/FPS),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
