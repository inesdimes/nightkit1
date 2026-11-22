"""ONE TAKE (extra system, separate from the main Insert Disc 2 look) - test on "Why do mimics pretend to be chests?"
Lessons from two reference explainers (see briefs/STYLE_one_take.md): one big hero object in the centre of a dark clean stage,
bright and high-contrast, glowing key parts, the object itself always moving, the animation SHOWS the mechanism (cutaway,
time-lapse tag, ticking counters), one camera move with no cuts, one boxed label at a time, the end loops into the start.
Smooth (not pixelated): rendered at 360x640, upscaled x3 with LANCZOS + bloom. Does not touch examples/mimic.py.
Voice: python tools/onetake/voice_mimic.py (placeholder Kokoro; the PC can swap in the Enes-timbre lines, same keys).
Run: TEST=1,5,11,17 python examples/onetake/mimic_v1.py -> test.png | PART=a:b | PART=audio"""
import os, sys, math, json
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..'); sys.path.insert(0,ROOT)
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(ROOT,'tts'))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from nightkit.engine import Renderer, Camera, quad
from nightkit.engine import box as _ebox
from nightkit import motion, font
from nightkit.zraster import zrender
from nightkit.audio import Sound, duck_envelope

OUT=os.path.join(ROOT,'out'); os.makedirs(OUT,exist_ok=True)
FPS=24; IW,IH=360,640; W,H=1080,1920; DUR=23.5; N=int(round(DUR*FPS))
sm=motion.smooth; PI=math.pi
def seg01(t,a,b): return max(0.0,min(1.0,(t-a)/(b-a)))
def lerp(a,b,u): return a+(b-a)*u
def box(x0,x1,y0,y1,z0,z1,col,xf=None,emit=False):
    Q=_ebox(min(x0,x1),max(x0,x1),min(y0,y1),max(y0,y1),min(z0,z1),max(z0,z1),col,xf=xf,emit=emit)
    for q in Q: q['wind']=-1
    return Q
def seg(p0,p1,w,col):
    """oriented box from p0 to p1 (square cross-section w)"""
    p0=np.array(p0,float); p1=np.array(p1,float); dv=p1-p0; L=np.linalg.norm(dv)+1e-9; dv/=L
    up=np.array([0,0,-1.0]) if abs(dv[1])>0.9 else np.array([0,1.0,0]); a_=np.cross(dv,up); a_/=np.linalg.norm(a_)+1e-9; b_=np.cross(a_,dv)
    v=[p0-a_*w/2-b_*w/2,p0+a_*w/2-b_*w/2,p0+a_*w/2+b_*w/2,p0-a_*w/2+b_*w/2,p1-a_*w/2-b_*w/2,p1+a_*w/2-b_*w/2,p1+a_*w/2+b_*w/2,p1-a_*w/2+b_*w/2]
    F=[(0,1,2,3),(5,4,7,6),(4,0,3,7),(1,5,6,2),(3,2,6,7),(4,5,1,0)]; Q=[quad([tuple(v[i]) for i in f],col) for f in F]
    for q in Q: q['wind']=1
    return Q
def hsh(i,s=0): v=math.sin(i*127.1+s*311.7)*43758.5453; return v-math.floor(v)

# ---------------- timing (from the measured voice) ----------------
SCR=json.load(open(os.path.join(TTS_DIR,'mmx','script.json')))
LINES=[('1',0.3),('2',2.6),('3',6.3),('4',10.2),('5',12.6),('6',15.8),('7',18.4)]
END={k:t0+SCR['dur'][k] for k,t0 in LINES}
T_LAPSE=(2.7,6.1); T_DUST=(6.3,9.7); T_BITE=11.0; T_ARM=(12.6,15.4); T_COIN=17.3; T_CALM=(18.4,22.2)

# ---------------- the chest (hero object) ----------------
WOOD=(150,92,48); WOOD_D=(112,66,34); GOLD=(240,190,70); IRON=(70,64,70); INSIDE=(40,22,18); TOOTH=(245,236,214); DUST=(150,140,128)
CW,CH,CD=1.2,0.7,0.8
def gold_level(t): return 1.0-sm(seg01(t,T_LAPSE[0]+0.3,T_LAPSE[1]))            # 1000 -> 0
def heroes(t): return int(round(9412*sm(seg01(t,T_LAPSE[0]+0.2,T_LAPSE[1]))))
def bite(t):                                                                    # teeth size 0..1
    b=sm(seg01(t,T_BITE-0.6,T_BITE+0.1)); return b*(1-sm(seg01(t,T_CALM[0]+0.8,T_CALM[1])))*1.0
def lid_angle(t):
    a=0.06+0.05*math.sin(t*3.0)                                                 # breathing, from frame 0
    if T_LAPSE[0]<=t<T_LAPSE[1]: a=0.15+0.55*max(0.0,math.sin((t-T_LAPSE[0])*PI*2.6))   # every hero opens it
    if T_LAPSE[1]<=t<T_BITE-0.6: a=lerp(0.15,0.05,seg01(t,T_LAPSE[1],T_LAPSE[1]+0.5))
    if T_BITE-0.6<=t<T_BITE+0.6:                                                # CHOMP
        u=seg01(t,T_BITE-0.6,T_BITE+0.6); a=0.95*math.sin(PI*min(1,u*1.6)) if u<0.62 else 0.06
    if T_BITE+0.6<=t<T_ARM[0]+0.9: a=0.06+0.02*math.sin(t*9)                       # trembling
    if T_ARM[0]+0.9<=t<T_CALM[0]+0.4: a=lerp(0.06,0.85,sm(seg01(t,T_ARM[0]+0.9,T_ARM[0]+2.0)))
    if t>=T_CALM[0]+0.4: a=lerp(0.85,0.06,sm(seg01(t,T_CALM[0]+0.4,T_CALM[1])))+0.05*math.sin(t*3.0)*seg01(t,T_CALM[1]-0.4,DUR)
    return a
def cutaway(t): return sm(seg01(t,T_LAPSE[0]-0.3,T_LAPSE[0]+0.4))*(1-sm(seg01(t,T_CALM[1]-0.2,DUR-0.4)))
def chest(t):
    Q=[]; x0,x1=-CW/2,CW/2; z0,z1=-CD/2,CD/2; th=0.06; cut=cutaway(t)
    Q+=box(x0,x1,0,th,z0,z1,WOOD_D)+box(x0,x1,0,CH,z0,z0+th,WOOD)+box(x0,x0+th,0,CH,z0,z1,WOOD)+box(x1-th,x1,0,CH,z0,z1,WOOD)
    Q+=box(x0+th,x1-th,th,th+0.01,z0+th,z1-th,INSIDE)
    if cut<0.5: Q+=box(x0,x1,0,CH,z1-th,z1,WOOD)+box(-0.08,0.08,CH*0.45,CH*0.8,z1,z1+0.03,GOLD,emit=True)          # front + lock
    else:                                                                       # cutaway: gold edging where the front was
        for y in (0.0,CH-0.04): Q+=box(x0,x1,y,y+0.04,z1-0.03,z1,GOLD,emit=True)
    for xx in (x0+0.18,x1-0.22): Q+=box(xx,xx+0.04,0,CH,z0-0.01,z0+th+0.005,IRON)
    # gold pile, shrinking; dust settling on it
    gl=gold_level(t); n=int(gl*24)
    for i in range(n):
        gx=lerp(x0+0.15,x1-0.15,hsh(i)); gz=lerp(z0+0.15,z1-0.15,hsh(i,1)); gy=th+0.02+0.06*(i%4)
        Q+=box(gx-0.05,gx+0.05,gy,gy+0.04,gz-0.05,gz+0.05,GOLD,emit=True)
    dust=sm(seg01(t,T_DUST[0],T_DUST[1]))*(1-sm(seg01(t,T_CALM[0],T_CALM[1])))
    if dust>0.02: Q+=box(x0+th,x1-th,th+0.012,th+0.012+0.01*dust,z0+th,z1-th,tuple(int(lerp(c,d_,dust)) for c,d_ in zip(INSIDE,DUST)))
    # eyes inside the back wall
    e=bite(t)
    if e>0.05: Q+=box(-0.22,-0.12,0.45,0.52,z0+th+0.002,z0+th+0.01,(255,int(60+40*(1-e)),40),emit=True)+box(0.12,0.22,0.45,0.52,z0+th+0.002,z0+th+0.01,(255,int(60+40*(1-e)),40),emit=True)
    # teeth on the front rim of the box (point up)
    for i in range(7):
        if e<0.05: break
        tx=lerp(x0+0.1,x1-0.1,i/6); hgt=0.16*e
        Q.append(quad([(tx-0.05,CH,z1-0.05),(tx+0.05,CH,z1-0.05),(tx,CH+hgt,z1-0.05),(tx,CH+hgt,z1-0.05)],TOOTH))
    # the lid, hinged at the back top edge
    a=lid_angle(t); hy,hz=CH,z0
    def rot(p): x,y,z=p; dy,dz=y-hy,z-hz; c,s=math.cos(-a),math.sin(-a); return (x,hy+dy*c-dz*s,hz+dy*s+dz*c)
    Q+=box(x0-0.02,x1+0.02,CH,CH+0.12,z0-0.02,z1+0.02,WOOD,xf=rot)+box(x0+0.05,x1-0.05,CH+0.12,CH+0.2,z0+0.05,z1-0.05,WOOD_D,xf=rot)
    Q+=box(x0-0.025,x1+0.025,CH+0.04,CH+0.08,z1-0.02,z1+0.03,GOLD,xf=rot,emit=True)
    for i in range(7):                                                          # teeth under the lid (point down)
        if e<0.05: break
        tx=lerp(x0+0.15,x1-0.15,i/6); hgt=0.18*e
        Q.append(quad([rot((tx+0.05,CH,z1-0.04)),rot((tx-0.05,CH,z1-0.04)),rot((tx,CH-hgt,z1-0.04)),rot((tx,CH-hgt,z1-0.04))],TOOTH))
    return Q
# coins flying out during the time-lapse (one burst per opening)
def coins_out(t):
    Q=[]
    if not (T_LAPSE[0]<=t<T_LAPSE[1]+0.8): return Q
    for b in range(9):
        tb=T_LAPSE[0]+b*(1/2.6)*0.5+0.05
        for j in range(5):
            u=t-tb
            if 0<u<0.9:
                vx=(hsh(b*7+j)-0.5)*2.2; vz=0.6+hsh(b*7+j,2)*1.2; vy=2.6+hsh(b*7+j,3)
                x,y,z=vx*u,CH*0.6+vy*u-4.9*u*u,vz*u
                if y>0: Q+=box(x-0.035,x+0.035,y-0.01,y+0.01,z-0.035,z+0.035,GOLD,emit=True)
    return Q
# the knight's gauntlet (only the arm: no limb acting) and the coin
def arm(t):
    Q=[]; u_in=sm(seg01(t,T_ARM[0],T_ARM[0]+0.9)); u_out=sm(seg01(t,T_COIN+0.5,T_CALM[0]+1.2))
    if u_in<=0 or u_out>=1: return Q
    hx=lerp(1.9,0.05,u_in); hy=lerp(2.1,1.15,u_in); hz=lerp(0.9,0.15,u_in)
    if t>=T_COIN-0.9: d=sm(seg01(t,T_COIN-0.9,T_COIN)); hy=lerp(1.15,0.55,d); hz=lerp(0.15,0.0,d)
    hx=lerp(hx,1.9,u_out); hy=lerp(hy,2.2,u_out)
    STEEL=(196,204,218); STEEL_D=(130,138,156)
    sx,sy,sz=hx+1.1,hy+0.9,hz+0.3
    el=((sx+hx)/2+0.1,(sy+hy)/2+0.15,(sz+hz)/2)
    Q+=seg((sx,sy,sz),el,0.24,STEEL)+seg(el,(hx,hy,hz),0.2,STEEL_D)
    for f_ in (0.3,0.65): pp=tuple(el[i]+((hx,hy,hz)[i]-el[i])*f_ for i in range(3)); Q+=seg(pp,tuple(pp[i]+((hx,hy,hz)[i]-el[i])*0.08 for i in range(3)),0.235,STEEL)
    Q+=box(hx-0.12,hx+0.12,hy-0.16,hy+0.04,hz-0.1,hz+0.1,STEEL_D)
    if t<T_COIN+0.05: Q+=box(hx-0.07,hx+0.07,hy-0.2,hy-0.18,hz-0.07,hz+0.07,(255,214,90),emit=True)
    return Q
def coin_inside(t):
    if t<T_COIN+0.05: return []
    g=0.6+0.4*math.sin((t-T_COIN)*6)*math.exp(-(t-T_COIN)*0.4)
    return box(-0.07,0.07,0.075,0.095,-0.07,0.07,(255,int(200+40*g),int(80+60*g)),emit=True)

def motes(t):
    """glowing dust motes always rising around the chest (keeps the frame alive from frame 0; periodic, so the loop closes)"""
    Q=[]
    for i in range(46):
        per=4.7; ph=(t/per+hsh(i))%1.0; ang=hsh(i,1)*2*PI+t*0.3; rr=0.7+0.5*hsh(i,2)
        x,z=rr*math.cos(ang),rr*math.sin(ang)*0.8; y=0.05+ph*1.9; b_=math.sin(PI*ph)
        if b_<0.15: continue
        c=(int(255*b_),int(200*b_),int(110*b_)); sz=0.012+0.012*hsh(i,3)
        Q+=box(x-sz,x+sz,y-sz,y+sz,z-sz,z+sz,c,emit=True)
    return Q
# ---------------- camera: one continuous turntable move, ends where it starts (loop) ----------------
def cam(t):
    a=0.75*math.sin(2*PI*t/DUR); r=2.35-0.25*math.sin(PI*t/DUR)
    pos=(r*math.sin(a),1.45+0.12*math.sin(PI*t/DUR),r*math.cos(a)); return pos,(0,0.48,0),40
R=Renderer(IW,IH,fog=(14,18,32))
FLOOR=[quad([(-6,0,-6),(-6,0,6),(6,0,6),(6,0,-6)],(28,30,42))]
FLOOR[0]['wind']=1
def shake(t):
    k=motion.kick(t,T_BITE,6.0,7,FPS)
    return (0.0,k)
def render3d(t):
    pos,tgt,fov=cam(t); c=Camera.look(pos,tgt)
    L=[((-2.5,3.2,3.0),(255,236,210),2.1),((2.8,2.4,-2.5),(140,170,255),1.3)]+([((0,0.35,0.0),(255,200,110),1.2*min(1,(t-T_COIN)*2))] if t>=T_COIN else [])
    if bite(t)>0.1: L.append(((0,0.5,-0.2),(255,60,40),0.9*bite(t)))
    img,vi,zb=zrender(R,c,[FLOOR,chest(t),coins_out(t),arm(t),coin_inside(t),motes(t)],L,fov=fov,fog_start=6,fog_end=16,ambient=0.33,shake=shake(t),return_z=True)
    a=np.asarray(img).astype(np.float32); yy=np.linspace(0,1,IH)[:,None,None]
    bg=np.array([10,14,26])*(1-yy)+np.array([24,30,48])*yy
    a=np.where((zb==0)[...,None],bg*np.ones((1,IW,1)),a)
    X,Y=np.meshgrid(np.linspace(-1,1,IW),np.linspace(-1,1,IH)); spot=np.clip(1.25-np.hypot(X*1.1,(Y-0.15)*0.8),0.55,1.0)
    return Image.fromarray(np.clip(a*spot[...,None],0,255).astype(np.uint8))

# ---------------- UI (full resolution, one boxed label at a time) ----------------
WHT=(240,240,235); YEL=(255,210,70); RED=(255,90,70); CYAN=(110,220,255); GRY=(150,156,170)
def fbox(d,lines,y,border,px=9,pad=14,center=True):
    ws=[font.width(s,1)*px*sc for s,sc in lines]; w=max(ws)+2*pad; h=sum(9*px*sc for _,sc in lines)+2*pad-2*px
    x0=(W-w)//2 if center else 40
    d.rectangle([x0,y,x0+w,y+h],fill=(12,14,22),outline=border,width=5)
    yy=y+pad
    for (s,sc),wd in zip(lines,ws):
        p=px*sc; xx=x0+(w-wd)//2 if center else x0+pad
        draw_text(d,s,xx,yy,p,lines_color(s,border)); yy+=9*p
def lines_color(s,border): return border if any(ch.isdigit() for ch in s) else WHT
def draw_text(d,s,x,y,p,col):
    font.check(s)
    for k,ch in enumerate(s.upper()):
        for j,row in enumerate(font.FONT[ch]):
            for i,b in enumerate(row):
                if b=='1': d.rectangle([x+(k*6+i)*p,y+j*p,x+(k*6+i)*p+p-1,y+j*p+p-1],fill=col)
def tag(d,s,col,x=40,y=40,px=6):
    w=font.width(s,1)*px+24; d.rectangle([x,y,x+w,y+9*px+6],fill=(12,14,22),outline=col,width=4); draw_text(d,s,x+12,y+8,px,col)
def ui(d,t):
    if t<2.5 or t>=21.9: fbox(d,[('WHY DO MIMICS',1),('PRETEND TO BE',1),('CHESTS?',1)],150,YEL,px=13)
    if T_LAPSE[0]-0.1<=t<T_LAPSE[1]+0.3:
        tag(d,'100 YEARS IN 3 SECONDS',CYAN); fbox(d,[('HEROES: '+f'{heroes(t):,}',1),('GOLD INSIDE: '+f'{int(round(1000*gold_level(t))):,}',1)],170,YEL,px=10)
    if T_DUST[0]+0.3<=t<T_BITE-0.7: tag(d,'CUTAWAY',GRY); fbox(d,[('TAKEN: 1,000',1),('GIVEN BACK: 0',1)],170,RED,px=11)
    if T_BITE-0.2<=t<T_BITE+0.9: fbox(d,[('CHOMP!',2)],180,RED,px=14)
    if T_ARM[0]+0.4<=t<T_COIN-0.4: tag(d,'SWORD: NOT DRAWN',CYAN)
    if T_COIN-0.1<=t<T_CALM[1]-0.4: fbox(d,[('TAKEN: 1,000',1),('GIVEN BACK: '+('1' if t>=T_COIN+0.05 else '0'),1)],170,YEL if t>=T_COIN+0.05 else RED,px=11)
SUB_P=7.5
def subs(d,t):
    import re
    for k,t0 in LINES:
        txt=SCR['text'][k]; dur=SCR['dur'][k]; sents=[s for s in re.split(r'(?<=[.!?,])\s+',txt) if s]
        tot=sum(len(s) for s in sents); a=t0
        for s in sents:
            b=a+dur*len(s)/tot
            if a-0.03<=t<b+0.15:
                words=s.upper().split(); rows=[]; cur=[]
                for w_ in words:
                    if len(' '.join(cur+[w_]))>20 and cur: rows.append(cur); cur=[w_]
                    else: cur.append(w_)
                rows.append(cur); lh=9.4*SUB_P; y0=H-120-lh*len(rows)
                for i,r in enumerate(rows):
                    line=' '.join(r); wpx=font.width(line,1)*SUB_P; x=(W-wpx)/2
                    d.rectangle([x-16,y0+i*lh-10,x+wpx+16,y0+i*lh+7*SUB_P+10],fill=(0,0,0)); draw_text(d,line,int(x),int(y0+i*lh),SUB_P,WHT)
                return
            a=b
def frame_full(t):
    im=render3d(t).resize((W,H),Image.LANCZOS)
    a=np.asarray(im).astype(np.float32); lum=a.max(axis=2)
    br=np.clip((lum-228)/27,0,1)[...,None]*a; bl=np.asarray(Image.fromarray(br.astype(np.uint8)).filter(ImageFilter.GaussianBlur(18))).astype(np.float32)
    a=np.clip(a*1.1+bl*0.7,0,255)
    im=Image.fromarray(a.astype(np.uint8)); d=ImageDraw.Draw(im); ui(d,t); subs(d,t); return im

QA=dict(fps=FPS,dur=DUR,W=IW,frame=lambda t: frame_full(t).resize((IW,IH)),chars={},camera=lambda t: cam(t)[0],scenes=[dict(id='all',t0=0,t1=DUR,action='one take')],texts=lambda: [])

# ---------------- audio ----------------
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=9); sr=s.sr; n=s.n; t=s.t; FX=np.zeros(n); BED=np.zeros(n)
    def put(x,t0,v):
        i=int(t0*sr); j=min(n,i+len(x))
        if i<n: FX[i:j]+=(x*v)[:j-i]
    def tone(t0,m,d,v,dec=6.0,wave='sin'):
        f=440*2**((m-69)/12); tt=s.T(d); ph=(f*tt)%1; x=np.sin(2*PI*ph) if wave=='sin' else np.where(ph<0.5,1.0,-1.0); put(x*np.exp(-tt*dec)*np.minimum(1,tt/0.005),t0,v)
    def nb(t0,d,lo,hi,v,seed): put(s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(PI*s.T(d)/d)**2,t0,v)
    def thud(t0,f,v,d=0.6): tt=s.T(d); put(np.sin(2*PI*f*tt*(1-0.3*tt/d))*np.exp(-tt*8),t0,v)
    BED+=s.filt(s.rng.normal(0,1,n),lo=40,hi=260)*0.16+np.sin(2*PI*55*t)*0.03+np.sin(2*PI*82.4*t+1.0)*0.02*(0.7+0.3*np.sin(2*PI*0.25*t))
    for k in range(9): tb=T_LAPSE[0]+k*(1/2.6)*0.5; nb(tb,0.18,400,2500,0.06,10+k); [tone(tb+0.05+j*0.04,96+(j%3),0.12,0.025,dec=30) for j in range(4)]
    for k in range(30): tone(T_LAPSE[0]+0.2+k*0.11,100,0.03,0.012,dec=60,wave='sq')              # counter ticks
    nb(T_DUST[0],3.0,1500,6000,0.012,40)                                                         # dust hiss
    thud(T_BITE,48,0.6); nb(T_BITE,0.25,300,3000,0.12,41); tone(T_BITE+0.02,40,0.4,0.06,dec=6)  # CHOMP
    for k in range(4): nb(T_ARM[0]+0.2+k*0.3,0.12,500,4000,0.035,50+k)                           # armour moves
    nb(T_ARM[0]+1.0,0.9,200,1200,0.05,60)                                                        # lid creaks open
    tone(T_COIN+0.05,91,1.2,0.07,dec=3); tone(T_COIN+0.07,98,1.0,0.05,dec=3.5)                  # the coin
    nb(T_CALM[0]+0.4,3.2,150,900,0.05,70)                                                        # slow exhale as the lid closes
    for m in (60,64,67): tone(T_CALM[0]+1.0,m,DUR-T_CALM[0]-1.0,0.03,dec=0.35)
    NB=np.zeros(n); wins=[]
    for k_,t0 in LINES:
        a,ar=_sf.read(os.path.join(TTS_DIR,'mmx',f'{k_}.wav')); a=a if a.ndim==1 else a.mean(1)
        a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a); i=int(t0*sr); j=min(n,i+len(a)); NB[i:j]+=a[:j-i]; wins.append((t0,t0+len(a)/sr))
    g=duck_envelope(n,sr,wins,-5.0,0.05,0.25); bed=BED*g; fx=FX*(0.6+0.4*g)
    pk=max(np.abs(bed+fx).max(),1e-6); gv=pk*1.7/np.abs(NB).max()
    s.L=bed+fx+NB*gv; s.R=np.roll(bed,600)+np.roll(fx,150)+NB*gv; s.reverb(0.12,length=1.1,decay=3.0)
    return s.save(path,peak=0.9)

if __name__=='__main__':
    if os.environ.get('TEST'):
        ims=[frame_full(float(x)) for x in os.environ['TEST'].split(',')]; sh=Image.new('RGB',(len(ims)*W//3,H//3))
        for i,im in enumerate(ims): sh.paste(im.resize((W//3,H//3),Image.LANCZOS),(i*W//3,0))
        sh.save(os.path.join(ROOT,'test.png')); sys.exit()
    if os.environ.get('PART')=='audio': print(build_audio(os.path.join(OUT,'one_take_mimic_v1.wav'))); sys.exit()
    if os.environ.get('PART'):
        import subprocess
        a,b=map(int,os.environ['PART'].split(':'))
        p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'mm_{a:05d}.mp4')],stdin=subprocess.PIPE)
        for f in range(a,min(b,N)): p.stdin.write(np.asarray(frame_full(f/FPS)).tobytes())
        p.stdin.close(); p.wait(); print('part done',a,b)
