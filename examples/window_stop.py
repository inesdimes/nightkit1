"""PS1 remake: TRAFFIC STOP SIMULATOR '98 - the officer picks the window over the door.
Anonymised low-poly characters, no real logos, no source audio. Narration is recorded separately.
Run: python examples/window_stop.py -> out/window_stop.mp4"""
import os, sys, math
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, box, quad, tiled_plane
from nightkit import motion, post, font, check
from nightkit.audio import Sound
OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6
sm=motion.smooth
def lerp3(a,b,u): return tuple(a[i]+(b[i]-a[i])*u for i in range(3))
def bez(a,c,b,u): return tuple((1-u)**2*a[i]+2*(1-u)*u*c[i]+u*u*b[i] for i in range(3))
def Rx(a): c,s=math.cos(a),math.sin(a); return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def Ry(a): c,s=math.cos(a),math.sin(a); return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def obox(center,hs,R,col,emit=False):
    c=np.array(center,float); return box(-hs[0],hs[0],-hs[1],hs[1],-hs[2],hs[2],col,xf=lambda p:tuple(c+R@np.array(p)),emit=emit)
def seg(p0,p1,w,col,depth=None):
    p0=np.array(p0,float); p1=np.array(p1,float); d=p1-p0; L=np.linalg.norm(d)+1e-9; d/=L
    up=np.array([0,0,-1.0]) if abs(d[1])>0.9 else np.array([0,1.0,0]); a=np.cross(d,up); a/=np.linalg.norm(a)+1e-9; b=np.cross(a,d); dp=depth or w
    v=[p0-a*w/2-b*dp/2,p0+a*w/2-b*dp/2,p0+a*w/2+b*dp/2,p0-a*w/2+b*dp/2,p1-a*w/2-b*dp/2,p1+a*w/2-b*dp/2,p1+a*w/2+b*dp/2,p1-a*w/2+b*dp/2]
    F=[(0,1,2,3),(5,4,7,6),(4,0,3,7),(1,5,6,2),(3,2,6,7),(4,5,1,0)]
    return [quad([tuple(v[i]) for i in f],col) for f in F]
def elbow(sh,hand,out_dir,L=0.62):
    sh=np.array(sh); hand=np.array(hand); m=(sh+hand)/2; d=np.linalg.norm(hand-sh)
    bend=max(0.0,(L-d)/L)*0.25+0.03; return tuple(m+np.array(out_dir)*bend+np.array([0,-1,0])*bend*0.6)
# ---------------- timeline (sim seconds) ----------------
T_MENU=(6.5,9.5); T_SELECT=9.0; T_REACH=(9.5,10.3); T_PULL=(10.3,12.6); T_EXIT=(13.0,14.8); T_DONE=15.4; SIM_LEN=19.0
def lean_p(t): return sm((t-T_PULL[0])/(T_PULL[1]-T_PULL[0]))
def exit_q(t): return sm((t-T_EXIT[0])/(T_EXIT[1]-T_EXIT[0]))
def gest(t,spans):
    g=0.0
    for a,b in spans: g=max(g,sm((t-a)/0.3)*(1-sm((t-b)/0.3)))
    return g
DRV_TALK=[(0.8,2.6),(3.8,5.6),(6.8,8.8)]; OFF_TALK=[(2.4,3.9),(5.4,6.9)]
# ---------------- palette ----------------
NAVY=(34,44,84); NAVY2=(22,28,56); GLASS=(26,32,52); CHROME=(160,166,180); INT=(20,20,24)
DSKIN=(150,104,74); HAIR=(26,20,16); TANK=(226,226,226); JEANS=(46,56,84)
OSHIRT=(160,176,204); OPANTS=(36,42,64); OSKIN=(224,182,152); BLK=(14,14,18)
# ---------------- world ----------------
def car():
    main=[]; pre=[]
    main+=box(-1.5,1.24,0.32,1.0,0.0,0.08,NAVY)+box(-1.5,1.24,0.32,1.0,1.72,1.8,NAVY)     # door panels near/far
    main+=box(-2.3,-1.5,0.32,1.56,0.0,1.8,NAVY)                                             # rear section
    main.append(quad([(-2.22,1.08,-0.005),(-1.58,1.08,-0.005),(-1.58,1.48,-0.005),(-2.22,1.48,-0.005)],GLASS))
    main+=box(1.24,2.35,0.32,1.06,0.0,1.8,NAVY)                                             # front/hood
    for x in (-1.5,1.62):
        main+=box(x-0.42,x+0.42,0.0,0.6,-0.06,0.3,(12,12,14)); main+=box(x-0.17,x+0.17,0.2,0.4,-0.075,-0.06,(120,120,130))
    for x in (0.03,-1.33): main+=box(x-0.012,x+0.012,0.36,1.0,-0.012,-0.002,NAVY2)
    main+=box(1.12,1.15,0.36,1.0,-0.012,-0.002,NAVY2)
    main+=box(0.80,0.99,0.85,0.9,-0.035,0.0,CHROME)+box(-0.5,-0.31,0.85,0.9,-0.035,0.0,CHROME)
    main+=box(1.12,1.25,1.0,1.56,0.0,0.1,NAVY2)+box(-0.05,0.04,1.0,1.56,0.0,0.1,NAVY2)+box(-1.5,-1.33,1.0,1.56,0.0,0.1,NAVY2)
    main+=box(-2.3,1.25,1.56,1.64,0.0,1.8,NAVY)
    main.append(quad([(-1.33,1.0,0.04),(-0.05,1.0,0.04),(-0.05,1.55,0.04),(-1.33,1.55,0.04)],(30,38,62)))  # rear glass (closed)
    main.append(quad([(1.25,1.58,0.1),(1.25,1.58,1.7),(1.98,1.06,1.7),(1.98,1.06,0.1)],(40,54,84)))
    main+=box(2.33,2.37,0.55,0.76,0.12,0.5,(250,248,220),emit=True)
    main+=box(1.6,1.75,1.12,1.2,-0.18,-0.0,NAVY2)                                            # mirror
    pre+=box(-2.2,2.2,0.3,1.6,1.66,1.72,INT)+box(-2.2,2.2,0.3,0.36,0.08,1.7,INT)+box(-2.2,1.2,1.5,1.56,0.08,1.7,INT)
    pre+=box(0.1,0.85,0.4,0.6,0.3,1.0,(40,40,46))+box(-0.05,0.12,0.72,1.45,0.3,1.0,(46,46,52))
    pre+=box(1.02,1.25,0.82,1.12,0.12,1.66,(28,28,32))
    pre+=box(0.95,1.02,0.9,1.3,0.48,0.82,(18,18,20))
    pre+=box(-1.3,-0.1,0.4,1.25,0.3,1.6,(38,38,44))
    return main,pre
CAR_MAIN,CAR_PRE=car()
def background():
    import random; Rr=random.Random(7); Q=[]
    Q+=tiled_plane(-9,9,-8,12,0,1.0,lambda i,j:(34,34,40) if (i*7+j*3)%5 else (30,30,36))
    for x in (-3.0,3.4): Q+=box(x,x+0.12,0.001,0.006,-6,8,(150,150,120))
    Q+=box(1.95,2.15,0,7.0,3.2,3.4,(78,66,54))+box(1.3,2.8,6.2,6.3,3.25,3.35,(70,60,50))     # utility pole
    Q+=box(-9,9,0,5.5,12,12.5,(18,20,30))
    for k in range(26):
        x=Rr.uniform(-8,8); y=Rr.uniform(0.8,4.8); Q.append(quad([(x,y,11.98),(x+0.6,y,11.98),(x+0.6,y+0.5,11.98),(x,y+0.5,11.98)],(230,200,140) if Rr.random()<0.6 else (120,150,200),emit=True))
    Q+=box(-4.1,-3.98,0,4.6,4,4.12,(60,60,64)); Q.append(quad([(-4.4,4.6,3.8),(-3.7,4.6,3.8),(-3.7,4.6,4.3),(-4.4,4.6,4.3)],(255,214,150),emit=True))
    return Q
BG=background()
FG=[]
# ---------------- characters ----------------
def driver(t):
    p=lean_p(t); q=exit_q(t); g=gest(t,DRV_TALK)*(1-p)
    Hs=(0.48,0.66,0.62); Hl=(0.5,0.98,0.24); Ho=(0.5,0.6,-0.62)
    Hp=lerp3(Hs,Hl,p); Hp=bez(Hp,(0.5,1.2,-0.1),Ho,q) if q>0 else Hp
    jitter=0.05*math.sin(t*23)*(p*(1-p))*4
    Lean=0.12*math.sin(t*1.7)*(1-p)+1.75*p+jitter; Lean=Lean*(1-q)+0.55*q
    nod=0.15*g*math.sin(t*9)+0.1*math.sin(t*1.3)*(1-p)
    R=Rx(-Lean); H_=np.array(Hp); d=R@np.array([0,1,0])
    Sc=H_+d*0.52; Hc=Sc+(Rx(-Lean-nod)@np.array([0,1,0]))*0.21; Rh=Rx(-Lean-nod)
    Q=[]
    Q+=obox(H_+d*0.27,(0.19,0.27,0.11),R,TANK)
    Q+=obox(H_+d*0.47,(0.06,0.06,0.06),R,DSKIN)
    for sx in (-1,1): Q+=obox(Sc+R@np.array([sx*0.17,0.0,0.0]),(0.06,0.05,0.07),R,DSKIN)
    Q+=obox(Hc,(0.11,0.13,0.12),Rh,DSKIN)
    for sx in (-1,1): Q+=obox(Hc+Rh@np.array([sx*0.045,0.03,-0.121]),(0.02,0.012,0.004),Rh,(14,10,8))
    Q+=obox(Hc+Rh@np.array([0,0.11,0.01]),(0.115,0.035,0.125),Rh,HAIR)
    # dreads
    grab=Hc+Rh@np.array([0,0.1,0.09]); grabbed=t>=T_REACH[1]
    for k in range(7):
        xo=-0.09+0.03*k; root=Hc+Rh@np.array([xo,0.06,0.1])
        sway=0.04*math.sin(t*3+k)
        if grabbed and k in (2,3,4):
            end=grab+np.array([0.0,0.06,-0.08])
        else:
            back=Rh@np.array([0,0,1])
            end=root+np.array([sway,-0.5,0])+back*0.08+Rh@np.array([xo*1.5,0,0])
        Q+=seg(root,end,0.035,HAIR)
    # arms
    for sx in (-1,1):
        sh=Sc+R@np.array([sx*0.2,-0.02,0])
        talk=Sc+np.array([sx*0.32,0.18+0.07*math.sin(t*8+sx),-0.18])
        rest=H_+np.array([sx*0.22,0.12,-0.2])
        h0=lerp3(tuple(rest),tuple(talk),g)
        sill=(0.18 if sx<0 else 0.92,1.03,-0.03)
        h1=lerp3(h0,sill,sm(p*1.6))
        body=tuple(Sc+R@np.array([sx*0.24,-0.5,-0.12]))
        hand=lerp3(h1,body,q)
        el=elbow(sh,hand,(sx*0.6,0,-0.3),0.6)
        Q+=seg(sh,el,0.09,DSKIN)+seg(el,hand,0.08,DSKIN)+obox(hand,(0.045,0.045,0.045),np.eye(3),DSKIN)
    # legs (seated -> through window -> kneeling)
    for sx in (-1,1):
        hip=tuple(H_+np.array([sx*0.1,-0.03,0]))
        k=tuple(np.array(hip)+np.array(lerp3((0.42,0.0,sx*0.1),(sx*0.03,-0.48,0.12),q)))
        f=tuple(np.array(k)+np.array(lerp3((0.05,-0.42,0.0),(0.0,-0.05,0.42),q)))
        Q+=seg(hip,k,0.13,JEANS)+seg(k,f,0.11,JEANS)+obox(f,(0.06,0.04,0.09),np.eye(3),(220,220,220))
    return Q,tuple(grab),tuple(Sc)
def officer(t,grab,dshoulder):
    reach=sm((t-T_REACH[0])/(T_REACH[1]-T_REACH[0])); q=exit_q(t)
    lean=0.18*reach*(1-sm((t-T_REACH[1])/0.4))-0.12*sm((t-T_REACH[1])/0.6)*(1-sm((t-T_DONE)/0.8))
    base=lerp3((1.55,0,-0.62),(1.3,0,-0.95),q); yaw=-0.55+0.25*q
    Rb=Ry(yaw); bc=np.array(base)
    def W(p): return tuple(bc+Rb@np.array(p,float))
    def WL(p):
        p=np.array(p,float); piv=np.array([0,0.92,0]); return W(piv+Rx(lean)@(p-piv))
    Q=[]
    for sx in (-1,1):
        Q+=box(sx*0.11-0.08,sx*0.11+0.08,0.06,0.92,-0.08,0.08,OPANTS,xf=W)+box(sx*0.11-0.09,sx*0.11+0.09,0.0,0.07,-0.06,0.12,BLK,xf=W)
    Q+=box(-0.21,0.21,0.92,1.5,-0.12,0.12,OSHIRT,xf=WL)+box(-0.22,0.22,0.88,0.99,-0.13,0.13,BLK,xf=WL)
    Q+=box(-0.31,-0.22,0.7,0.96,-0.06,0.08,BLK,xf=WL)+box(0.07,0.14,1.3,1.38,0.12,0.126,(230,190,60),xf=WL)
    Q+=box(0.1,0.18,1.4,1.5,0.06,0.13,BLK,xf=WL)
    Q+=box(-0.06,0.06,1.5,1.56,-0.06,0.06,OSKIN,xf=WL)+box(-0.11,0.11,1.54,1.8,-0.12,0.12,OSKIN,xf=WL)
    Q+=box(-0.125,-0.11,1.62,1.7,-0.03,0.03,OSKIN,xf=WL)+box(0.11,0.125,1.62,1.7,-0.03,0.03,OSKIN,xf=WL)
    for sx in (-1,1): Q+=box(sx*0.045-0.02,sx*0.045+0.02,1.68,1.7,0.12,0.124,BLK,xf=WL)
    # right arm (-x side): sill / pointing -> reach -> hair
    shR=WL((-0.27,1.44,0)); g=gest(t,OFF_TALK)
    sill=(1.02,1.03,-0.1); point=(0.85,1.3,-0.05)
    h=lerp3(sill,point,g)
    if t>=T_REACH[0]: h=lerp3(h,grab,reach)
    el=elbow(shR,h,tuple(Rb@np.array([-0.6,0,-0.2])))
    Q+=seg(shR,el,0.11,OSHIRT)+seg(el,h,0.09,OSKIN)+obox(h,(0.05,0.05,0.05),np.eye(3),OSKIN)
    # left arm: belt -> driver's shoulder during the exit
    shL=WL((0.27,1.44,0)); hl=WL((0.3,0.98,0.05))
    hl=lerp3(hl,dshoulder,sm((t-T_EXIT[0])/0.5)*(1-sm((t-T_DONE-0.5)/0.6)))
    el=elbow(shL,hl,tuple(Rb@np.array([0.6,0,-0.2])))
    Q+=seg(shL,el,0.11,OSHIRT)+seg(el,hl,0.09,OSKIN)+obox(hl,(0.05,0.05,0.05),np.eye(3),OSKIN)
    return Q
def split(Q):
    pre=[q for q in Q if q['c'][2]>0.03]; post=[q for q in Q if q['c'][2]<=0.03]; return pre,post
def lights(t):
    ph=(t*2.2)%1
    L=[((-0.3,2.0,-2.6),(255,255,255),1.9),((-2.6,1.8,-3.4),(60,90,255),3.4 if ph<0.5 else 1.2),((0.6,1.45,0.9),(255,220,170),0.35),((-4,4.5,4),(255,200,140),1.8)]
    if 0.5<=ph<0.68: L.append(((-0.9,1.8,-3.4),(255,40,40),2.2))
    return L
def camera(t):
    z=sm((t-9.8)/2.2)*(1-sm((t-15.0)/1.5))
    pos=lerp3((0.15,1.5,-2.9),(0.35,1.38,-2.3),z); tgt=lerp3((0.98,1.0,0.0),(0.9,0.92,-0.25),z)
    dx,dy,dyaw,dpit=motion.handheld(t,SIM_LEN,amp=0.7)
    c=Camera.look((pos[0]+dx,pos[1]+dy,pos[2]),tgt); return (c[0],c[1],c[2],c[3]+dyaw,c[4]+dpit)
R=Renderer(W,H,fog=(10,12,24))
def render(t):
    dq,grab,dsh=driver(t); oq=officer(t,grab,dsh)
    dpre,dpost=split(dq); opre,opost=split(oq)
    img,vi=R.render(camera(t),[BG,CAR_PRE+dpre+opre,CAR_MAIN,dpost+opost,FG],lights(t),fov=58,fog_start=6,fog_end=22,ambient=0.2)
    return post.ps1(img),vi
# ---------------- HUD ----------------
def otext(d,s,x,y,col,sc):
    o=max(1,sc//2)
    for ox,oy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)): font.text(d,s,x+ox*o,y+oy*o,(0,0,0),sc,None)
    font.text(d,s,x,y,col,sc,None)
def ctext(d,s,y,col,sc): otext(d,s,(W-font.width(s,sc))//2,y,col,sc)
def panel(d,x0,y0,x1,y1): d.rectangle([x0,y0,x1,y1],fill=(8,10,30),outline=(230,230,240))
def tri(d,x,y,col,left=False,down=False):
    if down: d.polygon([(x-4,y),(x+4,y),(x,y+5)],fill=col,outline=(0,0,0))
    elif left: d.polygon([(x,y),(x+5,y-4),(x+5,y+4)],fill=col)
    else: d.polygon([(x,y-3),(x+4,y),(x,y+3)],fill=col)
YEL=(255,214,40); WHT=(255,255,255); RED=(255,70,60)
MENU=['OPEN THE DOOR','ASK NICELY','USE THE WINDOW']
def hud(img,vi,t,mode,T):
    d=ImageDraw.Draw(img)
    if mode in ('hook','freeze'):
        ctext(d,'THE DOOR',26,WHT,2); ctext(d,'WAS RIGHT',44,WHT,2); ctext(d,'THERE...',62,YEL,2)
        if mode=='freeze':
            d.rectangle([0,0,W-1,H-1],outline=RED,width=2); ctext(d,'?!',84,RED,3)
    elif mode=='rewind':
        for k in range(2): tri(d,62+k*6,160,WHT,left=True)
        otext(d,'REWIND',78,156,WHT,1)
    elif mode=='play':
        if t<2.6:
            d.rectangle([0,96,W,150],fill=(8,10,30)); ctext(d,'TRAFFIC STOP',102,YEL,2); ctext(d,"SIMULATOR '98",120,WHT,2)
            if int(t*3)%2==0: ctext(d,'PRESS START',140,WHT,1)
        else:
            otext(d,"TRAFFIC STOP SIM '98",5,5,YEL,1)
            if t<T_DONE: otext(d,'OBJ: GET DRIVER OUT',5,15,WHT,1)
        if T_MENU[0]<=t<T_MENU[1]:
            panel(d,20,226,160,276); otext(d,'CHOOSE ACTION',28,231,YEL,1)
            sel=0 if t<7.6 else (1 if t<8.4 else 2)
            for k,m in enumerate(MENU):
                y=244+k*10; on=k==sel; flash=on and t>=T_SELECT and int(t*10)%2==0
                col=YEL if on else (170,170,190)
                if flash: col=WHT
                if on: tri(d,28,y+3,col)
                otext(d,m,36,y,col,1)
        if 10.4<=t<T_EXIT[0]:
            q=R.project((0.9,0.9,-0.03),vi)
            if q:
                bob=int(3*math.sin(t*10)); tri(d,int(q[0]),int(q[1])-14+bob,YEL,down=True)
                if int(t*4)%2==0: otext(d,'DOOR',int(q[0])-11,int(q[1])-24+bob,YEL,1)
            if int(t*3)%2==0: ctext(d,'HINT: TRY THE DOOR',258,YEL,1)
        if t>=T_DONE:
            ctext(d,'MISSION',34,WHT,2); ctext(d,'COMPLETE?',52,YEL,2)
            if t>=16.3: ctext(d,'DOOR USED: NO',76,RED,1)
            if t>=17.0: ctext(d,'STYLE POINTS: 0',86,RED,1)
            if t>=17.6:
                panel(d,22,236,158,266); otext(d,'ACHIEVEMENT UNLOCKED',30,241,YEL,1); ctext(d,'THE HARD WAY',253,WHT,1)
    elif mode=='end':
        d.rectangle([0,0,W,H],fill=(8,10,30))
        ctext(d,'WHAT WOULD',70,WHT,2); ctext(d,'YOU PRESS?',88,YEL,2)
        for k,m in enumerate(MENU):
            y=128+k*16; d.rectangle([34,y,41,y+7],outline=WHT); otext(d,m,48,y,WHT,1)
        if int(T*3)%2==0: ctext(d,'COMMENT BELOW!',190,YEL,1)
    wx=int(6+(W-font.width('VIDIVENIGAMING')-12)*(0.5+0.5*math.sin(T*0.31))); wy=int(290+10*math.sin(T*0.23))
    font.text(d,'VIDIVENIGAMING',wx,wy,(150,160,200),1,None)
    return img
# ---------------- video timeline ----------------
HOOK_END,FREEZE_END,REW_END=1.25,1.6,2.2; END0=REW_END+SIM_LEN; DUR=END0+2.4; N=int(DUR*FPS)
HOOK_START=10.9
def vmap(T):
    if T<HOOK_END: return HOOK_START+T,'hook'
    if T<FREEZE_END: return HOOK_START+HOOK_END,'freeze'
    if T<REW_END: u=(T-FREEZE_END)/(REW_END-FREEZE_END); return (HOOK_START+HOOK_END)*(1-u)**1.5,'rewind'
    if T<END0: return T-REW_END,'play'
    return SIM_LEN,'end'
def frame(T):
    t,mode=vmap(T)
    if mode=='end': img=Image.new('RGB',(W,H)); vi=None
    else: img,vi=render(t)
    return hud(img,vi,t,mode,T),mode
TEST=os.environ.get('TEST')
if TEST:
    ims=[frame(float(x))[0] for x in TEST.split(',')]; sh=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): sh.paste(im,(i*182,0))
    sh.resize((sh.width*2,640),Image.NEAREST).save('test.png'); sys.exit()
# ---------------- sound (no narration: leaves room for the voice-over) ----------------
s=Sound(DUR,loop=False,seed=5)
eng=(np.sin(2*np.pi*31*s.t)*0.6+np.sin(2*np.pi*62*s.t)*0.3)*0.02; s.L+=eng; s.R+=eng
amb=s.filt(s.rng.normal(0,1,s.n),lo=150,hi=1800)*0.02; s.bed(amb)
for k,tt in enumerate(np.arange(0.3,END0,0.9)):
    tc=s.T(0.06); s.place(np.sin(2*np.pi*4600*tc)*(np.sin(2*np.pi*60*tc)>0)*np.exp(-tc*30),tt+0.13*math.sin(k),0.012,pan=-0.6 if k%2 else 0.6)
def sq(t0,notes,step,v,dec=8):
    for i,m in enumerate(notes):
        f=440*2**((m-69)/12); tt=s.T(step*1.8); s.place(np.sign(np.sin(2*np.pi*f*tt))*np.exp(-tt*dec),t0+i*step,v)
def noise_burst(t0,d,lo,hi,v,seed,shape=2):
    x=s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape; s.place(x,t0,v)
def sweep(t0,d,f0,f1,v,square=False):
    tt=s.T(d); f=f0+(f1-f0)*tt/d; ph=2*np.pi*np.cumsum(f)/s.sr; x=np.sign(np.sin(ph)) if square else np.sin(ph)
    s.place(x*np.sin(np.pi*tt/d)**0.5,t0,v)
V=lambda t:t+REW_END
noise_burst(0.0,0.3,500,5000,0.25,1); s.thud(0.05,f=60,v=0.3)
sweep(HOOK_END,0.32,900,120,0.12); noise_burst(HOOK_END,0.32,300,3000,0.18,2)
sweep(FREEZE_END,0.6,180,1600,0.06,square=True); noise_burst(FREEZE_END,0.6,800,6000,0.12,3)
sq(V(0.0),[60,64,67,72],0.1,0.06)
for k in range(int((END0-V(2.6))/0.25)):                                                  # quiet PS1 bass loop under the play section
    m=[45,45,52,48,45,45,55,52][k%8]; f=440*2**((m-69)/12); tt=s.T(0.22)
    s.place(s.filt_short(np.sign(np.sin(2*np.pi*f*tt)),hi=900)*np.exp(-tt*6),V(2.6)+k*0.25,0.022)
sq(V(2.6),[76],0.1,0.04)
sq(V(T_MENU[0]),[72,79],0.06,0.05)
for tt in (7.6,8.4): sq(V(tt),[84],0.05,0.04,dec=20)
sq(V(T_SELECT),[72,76,79],0.04,0.06)
noise_burst(V(T_REACH[0]),0.25,600,4000,0.25,4)
s.thud(V(T_REACH[1]),f=90,v=0.25)
x=s.filt_short(s.noise(2.2,6),lo=80,hi=600)*np.linspace(0.2,1,int(2.2*s.sr)); s.place(x,V(T_PULL[0]),0.06)
tt=s.T(0.4); s.place(np.sign(np.sin(2*np.pi*110*tt))*np.exp(-tt*4),V(10.4),0.06)
noise_burst(V(T_EXIT[0]),1.6,200,2500,0.12,7,shape=1); s.thud(V(14.7),f=55,v=0.45)
sq(V(T_DONE),[72,76,79,84],0.09,0.06); sq(V(T_DONE+0.5),[70,66],0.18,0.05,dec=4)
for tt in (16.3,17.0): sq(V(tt),[60],0.05,0.05,dec=12)
sq(V(17.6),[84,88,91,96],0.07,0.05)
sq(END0,[72,76],0.08,0.05)
s.reverb(0.12,length=0.8,decay=5)
wav=s.save(os.path.join(OUT,'window_stop.wav'),peak=0.8)
vhs=post.VHS(W*S,H*S,S,grade='cold_blue',chroma=2,scan_dark=0.92,vignette=0.32,grain=2.0,band_period=1e9)
mp4=os.path.join(OUT,'window_stop.mp4')
with post.Encoder(mp4,W*S,H*S,wav,FPS,DUR) as enc:
    for f in range(N):
        T=f/FPS; img,mode=frame(T); enc.write(vhs(post.upscale(img,S),f,T,glitch=(mode=='rewind')))
print('probe',check.probe(mp4))
