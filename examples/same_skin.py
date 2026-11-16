"""SAME SKIN SQUAD - PS1 lobby remake of a 4-streamer clip. The streamers' own (PS1-processed) audio drives it; no invented dialogue.
Run: python examples/same_skin.py -> out/same_skin.mp4"""
import os, sys, math, wave
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, box, quad, tiled_plane, transform, rx, ry
from nightkit import motion, post, font, check
from nightkit.audio import Sound
OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6
sm=motion.smooth
def seg01(t,a,b): return max(0.0,min(1.0,(t-a)/(b-a)))
SRC=os.environ.get('SRC','/home/claude/v4/src48.wav')
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


# ---------------- source audio + loudness (drives the laughing) ----------------
def wav_read(p):
    w=wave.open(p); x=np.frombuffer(w.readframes(w.getnframes()),np.int16).reshape(-1,w.getnchannels()).astype(float)/32768; return x,w.getframerate()
SRCW,SR=wav_read(SRC); mono=SRCW.mean(1)
hop=SR//24; ENV=np.array([np.sqrt((mono[i*hop:(i+1)*hop]**2).mean()) for i in range(len(mono)//hop)])
ENV=np.convolve(ENV,np.ones(5)/5,'same'); ENV=np.clip(ENV/np.percentile(ENV,92),0,1.3)
def loud(s): i=int(s*24); return float(ENV[i]) if 0<=i<len(ENV) else 0.0
# source-time events (measured from the clip)
SW1=13.4; SW2=19.3; LOOK=13.8; DANCE=20.0
# ---------------- skins ----------------
SKIN=(150,104,74); HAIR=(22,18,16)
PIRATE=dict(top=SKIN,coat=(190,30,36),pants=(30,34,30),shoe=(120,80,50),sleeve=(190,30,36),sash=(200,30,36),hair=HAIR,shorts=False)
JERSEY=dict(top=(250,220,40),coat=None,pants=(40,80,200),shoe=(250,250,250),sleeve=(250,220,40),sash=None,hair=HAIR,shorts=True)
BLACK=dict(top=(28,28,32),coat=None,pants=(50,50,56),shoe=(235,235,235),sleeve=(28,28,32),sash=None,hair=(60,44,30),shorts=False)
def avatar(x,z,skin,pose,t,phase=0.0,head_yaw=0.0,spin=0.0,lf=0.0):
    w=2*math.pi*2.0*t+phase
    bounce=0.0; sway=0.0; lean=0.0
    if pose=='dance': bounce=0.05*abs(math.sin(w)); sway=0.06*math.sin(w/2)
    if pose=='laugh': bounce=0.03*lf*abs(math.sin(2*math.pi*5*t+phase)); lean=0.18*lf
    base=np.array([x+sway,bounce,z]); Rb=Ry(math.pi+spin)       # faces the camera (-z)
    def W(p,piv_lean=True):
        p=np.array(p,float)
        if piv_lean: piv=np.array([0,0.9,0]); p=piv+Rx(-lean)@(p-piv)
        return tuple(base+Rb@p)
    Q=[]
    for sx in (-1,1):
        hip=(sx*0.1,0.9,0); ft=(sx*0.12,0.06,0)
        if pose=='dance': ft=(sx*0.12+0.05*math.sin(w+sx),0.06+0.06*max(0,math.sin(w+(0 if sx<0 else math.pi))),0)
        if skin['shorts']:
            Q+=transform(seg(hip,(sx*0.11,0.6,0),0.15,skin['pants']),lambda p:W(p,False))+transform(seg((sx*0.11,0.6,0),(sx*0.12,0.25,0),0.11,SKIN),lambda p:W(p,False))
            Q+=transform(seg((sx*0.12,0.25,0),ft,0.115,(245,245,245)),lambda p:W(p,False))
        elif skin is PIRATE:
            Q+=transform(seg(hip,(sx*0.12,0.3,0),0.14,skin['pants']),lambda p:W(p,False))+transform(seg((sx*0.12,0.3,0),ft,0.1,SKIN),lambda p:W(p,False))
        else: Q+=transform(seg(hip,ft,0.13,skin['pants']),lambda p:W(p,False))
        Q+=transform(box(ft[0]-0.06,ft[0]+0.06,0.0,0.06,-0.13,0.06,skin['shoe']),lambda p:W(p,False))
    Q+=transform(box(-0.19,0.19,0.9,1.45,-0.11,0.11,skin['top']),W)
    if skin is PIRATE:
        for sx in (-1,1): Q+=transform(box(sx*0.12 if sx>0 else -0.215,0.215 if sx>0 else -0.12,0.62,1.46,-0.125,0.12,skin['coat']),W)
        Q+=transform(box(-0.215,0.215,0.55,1.46,0.1,0.125,skin['coat']),W)
        Q+=transform(box(-0.195,0.195,0.88,0.98,-0.118,0.118,skin['sash'])+box(-0.04,0.04,0.89,0.97,-0.123,-0.118,(240,200,60)),W)
        Q+=transform(box(-0.08,0.08,1.1,1.42,-0.112,-0.11,(120,80,60)),W)
    if skin is JERSEY:
        Q+=transform(box(-0.07,0.07,1.38,1.45,-0.113,-0.11,(30,150,70))+box(-0.03,0.03,1.15,1.21,-0.113,-0.11,(30,150,70)),W)
    if skin is BLACK:
        Q+=transform(box(-0.01,0.01,0.92,1.44,-0.114,-0.11,(90,90,96)),W)
    Q+=transform(box(-0.06,0.06,1.45,1.53,-0.06,0.06,SKIN),W)
    hc=np.array([0,1.66,0])
    def WH(p): p=np.array(p,float); return W(hc+Ry(head_yaw)@(p-hc))
    Q+=transform(box(-0.11,0.11,1.53,1.79,-0.12,0.12,SKIN),WH)
    for sx in (-1,1): Q+=transform(box(sx*0.045-0.02,sx*0.045+0.02,1.67,1.695,-0.124,-0.12,(14,10,8)),WH)
    Q+=transform(box(-0.03,0.03,1.58,1.6,-0.124,-0.12,(90,40,40)),WH)
    Q+=transform(box(-0.12,0.12,1.74,1.82,-0.13,0.13,skin['hair']),WH)
    if skin is not BLACK:
        for k in range(6):
            a=k*math.pi/3; Q+=transform(box(-0.03,0.03,0,0.09,-0.03,0.03,skin['hair'],xf=lambda p,a=a:tuple(np.array([0.09*math.cos(a),1.8,0.09*math.sin(a)])+Rx(0.6*math.sin(a))@Ry(a)@np.array(p))),WH)
    # arms
    for sx in (-1,1):
        sh=(sx*0.26,1.42,0)
        if pose=='cross': hd=(-sx*0.1,1.2,-0.2)
        elif pose=='dance': hd=(sx*(0.32+0.08*math.sin(w)),1.25+0.35*math.sin(w+(0 if sx<0 else math.pi)),-0.15)
        elif pose=='laugh': hd=(sx*0.12,1.02+0.03*math.sin(2*math.pi*5*t),-0.18)
        else: hd=(sx*0.3,0.95,0.03)
        el=elbow(sh,hd,(sx*0.6,0,0.2),0.6)
        sl=skin['sleeve'] if skin['coat'] is None else skin['coat']
        Q+=transform(seg(sh,el,0.1,sl)+seg(el,hd,0.085,SKIN if skin is not BLACK else sl)+box(hd[0]-0.045,hd[0]+0.045,hd[1]-0.05,hd[1]+0.04,hd[2]-0.045,hd[2]+0.045,SKIN),W)
    return Q
# ---------------- lobby set ----------------
def palm(x,z,h=3.0,lean=0.3,seed=0):
    Q=[]; pts=[(x+lean*(k/5)**2,h*k/5,z) for k in range(6)]
    for k,(a,b) in enumerate(zip(pts,pts[1:])): Q+=seg(a,b,0.2-0.02*k,(120,86,50) if k%2 else (104,74,42))
    top=pts[-1]
    for i in range(7):
        a=2*math.pi*i/7+seed; d=(math.cos(a),math.sin(a)); tip=(top[0]+d[0]*1.4,top[1]-0.6,top[2]+d[1]*1.4); mid=(top[0]+d[0]*0.75,top[1]+0.15,top[2]+d[1]*0.75); sd=(-d[1]*0.25,d[0]*0.25)
        Q.append(quad([top,(mid[0]+sd[0],mid[1],mid[2]+sd[1]),tip,(mid[0]-sd[0],mid[1],mid[2]-sd[1])],(56,160,60) if i%2 else (40,130,48)))
    return Q
def lobby():
    import random; r=random.Random(3); Q=[]
    Q+=tiled_plane(-9,9,-6,8,0,1.0,lambda i,j:(236,214,156) if (i+j)%3 else (226,202,144))
    Q+=tiled_plane(-30,30,8,40,-0.04,4.0,lambda i,j:(40,160,215) if (i+j)%2 else (54,175,225))
    for x,z,h,l in ((-3.6,3.0,3.6,0.4),(3.8,3.4,3.2,-0.35),(-5.5,6.0,3.0,0.2),(5.6,6.5,3.8,-0.2),(-2.2,7.0,2.8,0.3)): Q+=palm(x,z,h,l,seed=x)
    Q+=box(-1.6,1.6,0,1.6,4.2,5.6,(150,90,40))+box(-1.65,1.65,1.5,2.3,4.15,5.65,(170,104,48))
    for x in (-1.2,0.0,1.2): Q+=box(x-0.12,x+0.12,0,2.32,4.12,4.18,(240,200,60))
    Q+=box(-0.25,0.25,1.2,1.7,4.08,4.15,(255,220,80),emit=True)
    for k in range(40):
        x=r.uniform(-1.4,1.4); Q+=box(x-0.12,x+0.12,1.62,1.75,4.3+r.uniform(0,1),4.42+r.uniform(0,1),(255,215,60),emit=r.random()<0.5)
    for x,z,s in ((-6.5,5,1.4),(7.0,5.5,1.8)): Q+=box(x-s,x+s,0,s,z-s,z+s,(150,140,130))
    return Q
LOBBY=lobby()
SLOTS=[-1.35,-0.45,0.45,1.35]
def pads(t):
    Q=[]
    for k,x in enumerate(SLOTS):
        g=0.75+0.25*math.sin(t*3+k)
        for i in range(10):
            a0=2*math.pi*i/10; a1=2*math.pi*(i+1)/10; c=(int(80*g),int(240*g),int(250*g))
            Q.append(quad([(x,0.02,0),(x+0.42*math.cos(a1),0.02,0.42*math.sin(a1)),(x+0.42*math.cos(a0),0.02,0.42*math.sin(a0))],c,emit=True))
    return Q
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

SKULL=[".#####.","#######","#..#..#","#..#..#","#######",".##.##.",".#####.",".#.#.#."]
def skull(d,x,y,sc):
    for j,row in enumerate(SKULL):
        for i,c in enumerate(row):
            if c=='#':
                d.rectangle([x+i*sc-1,y+j*sc-1,x+i*sc+sc,y+j*sc+sc],fill=(0,0,0))
    for j,row in enumerate(SKULL):
        for i,c in enumerate(row):
            if c=='#': d.rectangle([x+i*sc,y+j*sc,x+i*sc+sc-1,y+j*sc+sc-1],fill=(240,240,240))

YEL=(255,214,40); WHT=(255,255,255); GRN=(90,230,90); CYN=(120,230,255)
# ---------------- video edit: (video start, video end, source start, mode) ----------------
EDIT=[(0.0,1.5,19.0,'hook'),(1.75,15.65,9.4,'story'),(15.65,17.15,26.6,'match')]
DUR=17.15; N=int(DUR*FPS)
def vmap(T):
    for a,b,s0,m in EDIT:
        if a<=T<b: return s0+(T-a),m
    if 1.5<=T<1.75: return None,'wipe'
    return 28.1,'match'
def state(s,mode):
    """returns list of (x,skin,pose,phase,head_yaw,spin,lf) for the 4 slots"""
    out=[]; lf=loud(s)
    for k,x in enumerate(SLOTS):
        if mode=='hook' or mode=='match': out.append((x,PIRATE,'dance',0.0,0.0,0.0,lf)); continue
        if k<3:
            if s<LOOK: pose,hy='cross',0.0
            elif s<DANCE-0.3: pose,hy='laugh',(0.55+0.15*k)*sm(seg01(s,LOOK,LOOK+0.3))
            else: pose,hy='dance',0.0
            out.append((x,PIRATE,pose,0.0,hy,0.0,lf))
        else:
            if s<SW1: skin,pose='BLACK','idle'
            elif s<SW2: skin,pose='JERSEY','idle' if s<SW1+0.6 else 'laugh'
            else: skin,pose='PIRATE','idle' if s<DANCE-0.3 else 'dance'
            spin=0.0
            for sw in (SW1,SW2):
                if sw-0.2<=s<sw+0.25: spin=2*math.pi*sm(seg01(s,sw-0.2,sw+0.25))
            sk={'BLACK':BLACK,'JERSEY':JERSEY,'PIRATE':PIRATE}[skin]
            if SW1-0.2<=s<SW1: sk=BLACK
            if SW2-0.2<=s<SW2: sk=JERSEY
            out.append((x,sk,pose,0.0,0.0,spin,lf))
    return out
def camera(s,mode,T):
    if mode=='hook': pos=(0,1.2,-3.9+0.3*T/1.5); tgt=(0,1.0,0)
    elif mode=='match': pos=(0,1.3,-4.0); tgt=(0,1.0,0)
    else:
        wide=((0,1.3,-4.1),(0,1.0,0)); p4=((1.05,1.35,-2.0),(1.35,1.05,0))
        z1=sm(seg01(s,SW1-0.4,SW1))*(1-sm(seg01(s,SW1+1.6,SW1+2.4)))
        z2=sm(seg01(s,SW2-0.4,SW2))*(1-sm(seg01(s,SW2+0.9,SW2+1.6)))
        z=max(z1,z2); push=0.25*sm(seg01(s,9.4,13.0))
        pos=lerp3(wide[0],p4[0],z); tgt=lerp3(wide[1],p4[1],z); pos=(pos[0],pos[1],pos[2]+push*(1-z))
    dx,dy,dyaw,dpit=motion.handheld(T,DUR,amp=0.5)
    c=Camera.look((pos[0]+dx,pos[1]+dy,pos[2]),tgt); return (c[0],c[1],c[2],c[3]+dyaw,c[4]+dpit)
R=Renderer(W,H,fog=(120,180,235))
def render(s,mode,T):
    Q=[]
    for x,sk,pose,ph,hy,spin,lf in state(s,mode): Q+=avatar(x,0.0,sk,pose,s,ph,hy,spin,lf)
    L=[((-4,6,-4),(255,246,225),5.0),((3,3,-3),(200,220,255),2.0),((0,2.5,4.3),(255,210,90),1.0)]
    img,vi=R.render(camera(s,mode,T),[LOBBY+pads(s),Q],L,fov=58,fog_start=14,fog_end=45,ambient=0.4)
    return post.ps1(img),vi
def flash_at(s):
    for sw in (SW1,SW2):
        if abs(s-sw)<0.12: return 1-abs(s-sw)/0.12
    return 0.0
def hud(img,vi,s,mode,T):
    d=ImageDraw.Draw(img)
    def proj(p): return R.project(p,vi) if vi is not None else None
    if mode in ('story','hook','match'):
        for k,x in enumerate(SLOTS):
            q=proj((x,2.05,0))
            if q: otext(d,'P%d'%(k+1),int(q[0])-5,int(q[1])-4,WHT,1)
    if mode=='hook':
        otext(d,'4 PLAYERS',(W-font.width('4 PLAYERS',2))//2,30,WHT,2)
        w=font.width('1 SKIN',2)+6+14; x0=(W-w)//2; otext(d,'1 SKIN',x0,50,YEL,2); skull(d,x0+font.width('1 SKIN',2)+6,49,2)
    if mode=='story':
        n=3 if s<SW2 else 4; done=n==4
        d.rectangle([40,24,140,40],fill=(10,30,10) if done else (20,20,30),outline=GRN if done else WHT)
        otext(d,'SAME SKIN: %d/4'%n,(W-font.width('SAME SKIN: %d/4'%n))//2,29,GRN if done else WHT,1)
        if done and s<SW2+1.2:
            u=sm(seg01(s,SW2+0.1,SW2+0.3)); sc=2 if u>0.5 else 3
            otext(d,'FULL SQUAD',(W-font.width('FULL SQUAD',2))//2,232,YEL,2)
        for sw in (SW1,SW2):
            if sw<=s<sw+1.0:
                q=proj((1.35,2.25,0))
                if q: otext(d,'EQUIPPED!',max(2,min(W-font.width('EQUIPPED!')-2,int(q[0])-font.width('EQUIPPED!')//2)),int(q[1])-10-int(6*sm(seg01(s,sw,sw+0.3))),YEL,1)
        d.rectangle([6,262,72,282],fill=(40,40,30),outline=(180,170,120))
        otext(d,'FINDING SERVER',9,265,(220,220,200),1) if False else None
        font.text(d,'SEARCHING',9,265,(230,230,210),1,None); font.text(d,'0:%02d'%int(s),9,274,WHT,1,None)
    if mode=='match':
        u=sm(seg01(s,26.6,26.8)); otext(d,'MATCH',(W-font.width('MATCH',3))//2,int(40-10*(1-u)),YEL,3); otext(d,'FOUND!',(W-font.width('FOUND!',3))//2,int(64-10*(1-u)),YEL,3)
    wx=int(6+(W-font.width('VIDIVENIGAMING')-12)*(0.5+0.5*math.sin(T*0.31))); wy=int(298+6*math.sin(T*0.23))
    font.text(d,'VIDIVENIGAMING',wx,wy,(70,90,140),1,None)
    return img
def frame(T):
    s,mode=vmap(T)
    if mode=='wipe':
        u=(T-1.5)/0.25; a,vi=render(20.8,'hook',T); b,vi2=render(9.4,'story',T)
        A=np.asarray(a); B=np.asarray(b); x=int(W*u); o=A.copy(); o[:,:x]=B[:,W-x:] if x>0 else o[:,:0]
        img=Image.fromarray(o); return img,True
    img,vi=render(s,mode,T)
    f=flash_at(s) if mode=='story' else 0.0
    if f>0: img=Image.blend(img,Image.new('RGB',img.size,(255,255,255)),0.7*f)
    return hud(img,vi,s,mode,T),False
TEST=os.environ.get('TEST')
if TEST:
    ims=[frame(float(x))[0] for x in TEST.split(',')]; sh=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): sh.paste(im,(i*182,0))
    sh.resize((sh.width*2,640),Image.NEAREST).save('test.png'); sys.exit()

# ---------------- sound: the streamers' own audio (PS1-processed), edited to the cut, plus game SFX ----------------
s=Sound(DUR,loop=False,seed=4)
def put_src(v0,s0,s1,fade=0.03):
    i0,i1=int(s0*SR),int(s1*SR); seg_=SRCW[i0:i1].copy(); k=int(fade*SR)
    seg_[:k]*=np.linspace(0,1,k)[:,None]; seg_[-k:]*=np.linspace(1,0,k)[:,None]
    j=int(v0*s.sr); n=min(len(seg_),s.n-j); s.L[j:j+n]+=seg_[:n,0]*0.9; s.R[j:j+n]+=seg_[:n,1]*0.9
put_src(0.0,19.0,20.5); put_src(1.75,9.4,23.3); put_src(15.65,26.6,28.1)
# PS1 voice treatment: 22 kHz feel + light bit reduction
for ch in ('L','R'):
    x=getattr(s,ch); x=s.filt(x,hi=8500); x=np.round(x*2048)/2048; setattr(s,ch,x)
def sq(t0,notes,step,v,dec=8,duty=0.5):
    for i,m in enumerate(notes):
        f=440*2**((m-69)/12); tt=s.T(step*1.8); ph=(f*tt)%1; s.place(np.where(ph<duty,1.0,-1.0)*np.exp(-tt*dec),t0+i*step,v)
def whoosh(t0,d,v,seed):
    tt=s.T(d); x=s.filt_short(s.noise(d,seed),lo=500,hi=5000)*np.sin(np.pi*tt/d)**2; s.place(x,t0,v)
def sparkle(t0,v=0.04):
    for k in range(6): tt=s.T(0.12); s.place(np.sin(2*np.pi*(2200+350*k)*tt)*np.exp(-tt*30),t0+k*0.04,v)
V=lambda src:src-7.65
sq(0.0,[67,74],0.06,0.05)
whoosh(1.48,0.3,0.25,1)
for sw in (13.4,19.3): whoosh(V(sw)-0.2,0.45,0.22,int(sw)); sparkle(V(sw)); s.thud(V(sw),f=110,v=0.12)
sq(V(19.4),[72,76,79,84],0.06,0.05,duty=0.25)
sq(15.65,[72,79,84,91],0.07,0.06)
s.reverb(0.08,length=0.6,decay=6)
wav=s.save(os.path.join(OUT,'same_skin.wav'),peak=0.9)
vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.94,vignette=0.25,grain=1.8,band_period=1e9)
mp4=os.path.join(OUT,'same_skin.mp4')
with post.Encoder(mp4,W*S,H*S,wav,FPS,DUR) as enc:
    for f in range(N):
        T=f/FPS; img,g=frame(T); enc.write(vhs(post.upscale(img,S),f,T,glitch=g))
print('probe',check.probe(mp4))
