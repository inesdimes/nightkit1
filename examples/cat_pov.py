"""CAT POV - "POV: Cat is trying to steal your food".  PS1 comedy short, 9:16, 15 s. Fully procedural (nightkit).
Idea from a real POV clip (a cat peeking around a raised sock foot); recreated from scratch in the channel style as a stealth-game parody:
the foot is the cover, the cat finds the gap, a LINE OF SIGHT meter fills, the foot never gives up: the cat crouches behind it, slips past the late swipe and jumps straight at the lens.
LOCKED ASSETS are imported from cat_dodge.py (cat model, bedroom, pizza slice); the POV legs are built here.
All text is a 2D overlay. Voice: python tools/tts/cp.py -> $TTS_DIR/cp/N1.wav (hook line only).
Run: TEST=0.5,5,12 python examples/cat_pov.py -> test.png | PART=a:b | PART=audio | QA: python tools/qa/scene_qa.py examples/cat_pov.py"""
import os, sys, math, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, box
from nightkit import post, font
from nightkit.zraster import zrender
from nightkit.audio import Sound
import cat_dodge as CD
FT=CD.FT
sm,seg01,lerp,lerp3,seg,PI=CD.sm,CD.seg01,CD.lerp,CD.lerp3,CD.seg,CD.PI
cat_model,slice_quads,otext,ctext,panel=CD.cat_model,CD.slice_quads,CD.otext,CD.ctext,CD.panel
YEL,RED,GRN,WHT,CYAN,GRY=CD.YEL,CD.RED,CD.GRN,CD.WHT,CD.CYAN,CD.GRY
TTS_DIR=CD.TTS_DIR; OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6; DUR=15.0; N=int(round(DUR*FPS))
SCR=json.load(open(os.path.join(TTS_DIR,'cp','script.json')))

# ======================= timeline (seconds) =======================
T_TIRE=11.3; T_DASH=(11.5,12.9); T_JUMP=(12.2,12.9); T_FREEZE=12.9; T_WIN=13.05
CAM=np.array([0.0,0.85,0.5]); TGT=np.array([0.0,0.78,-1.0]); FOV=50; FPX=90/math.tan(math.radians(FOV/2))
CAT_Z=-1.2; D_CAT=CAM[2]-CAT_Z; D_FOOT=0.85
PJ=(92,112,168); PJ_D=(76,96,150); SKIN=(206,164,138); SOCK=(206,198,216); SOCK_S=(150,128,190)
PLATE_C=np.array([0.0,0.6,0.02]); CEIL=box(-1.8,1.8,2.7,2.76,-2.96,1.32,(176,166,204))

# ======================= the game: the foot chases the cat's peek =======================
def flips():
    t=0.6; out=[]
    while t<T_TIRE-0.3:
        out.append(t); t+=0.9 if t<3.0 else (0.7 if t<7.2 else 0.55)
    return out
FL=flips()
def tau(t): return 0.18 if t<3.0 else (0.34 if t<7.2 else 0.55)        # the foot gets slower, the cat does not
def _sim():
    DT=1/240; n=int(DUR/DT)+2; hx=np.zeros(n); F=np.zeros(n); h=0.0; f=0.0
    for i in range(n):
        t=i*DT; k=sum(1 for x in FL if x<=t)-1; side=0.0 if (k<0 or t>=T_TIRE) else (-1.0 if k%2==0 else 1.0)
        late=t>=T_JUMP[0]                                                   # her last swipe: too late, she misses
        h+=(0.2*side-h)*min(1.0,DT/0.045); f+=((0.13 if late else 0.07*side)-f)*min(1.0,DT/(0.15 if late else (0.25 if t>=T_TIRE else tau(t)))); hx[i]=h; F[i]=f
    return DT,hx,F
DT_,HX,FX=_sim()
def hx_of(t): return float(np.interp(t,np.arange(len(HX))*DT_,HX))
def fx_of(t): return float(np.interp(t,np.arange(len(FX))*DT_,FX))
def los(t):
    if t>=T_JUMP[0]: return min(1.0,(t-T_JUMP[0])/0.1)
    """0 = the cat is hidden behind the foot, 1 = clear line of sight (screen-space gap between cat head and foot)"""
    h=hx_of(t); dx=abs((h+0.35*h)*FPX/D_CAT-fx_of(t)*FPX/D_FOOT)
    u=max(0.0,min(1.0,(dx-14)/26)); return u*u*(3-2*u)
def spot_events():
    out=[]; last=-9; prev=0.0
    for i in range(int(T_TIRE*FPS*4)):
        t=i/(FPS*4); v=los(t)
        if prev<0.7<=v and t-last>0.75: out.append(t); last=t
        prev=v
    return out
SPOTS=spot_events()+[T_JUMP[0]+0.05]                  # the final slip: SPOTTED!

# ======================= states =======================
def drop_of(t): return 0.0                                                # the foot never gives up
def cat_state(t):
    hx=hx_of(t); rise=0.0
    if t<T_DASH[0]:
        return dict(base=(0.35*hx,CD.CAT_Y,CAT_Z),yaw=-0.5*hx,walk=0.0,hx=hx,hyaw=-1.6*hx,hroll=-1.4*hx,hpitch=0.0,lid=0.2,pupil=-6*hx,tail=t*5.0,crouch=0.6,ears=0.1,mouth=0.0,bpitch=0.0,shades=0.0)
    if t<T_JUMP[0]:                                                # the foot gave up: he crouches and wiggles his butt
        c=sm(seg01(t,T_DASH[0],T_DASH[0]+0.35)); wig=0.012*math.sin(t*38)*c
        return dict(base=(wig,CD.CAT_Y,CAT_Z),yaw=0.0,walk=0.0,hx=0.0,hyaw=0.0,hroll=0.0,hpitch=0.05*c,lid=0.0,pupil=0.0,tail=t*14,crouch=0.6+0.4*c,ears=0.9*c,mouth=0.0,bpitch=0.08*c,shades=0.0)
    u=seg01(t,*T_JUMP)                                             # ONE big jump straight at the lens
    z=lerp(CAT_Z,-0.05,sm(u)*0.35+u*0.65); y=lerp(CD.CAT_Y,CD.CAT_Y+0.04,u)+0.55*math.sin(PI*u)
    return dict(base=(-0.2*math.sin(PI*u),y,z),yaw=0.0,walk=0.0,hx=0.0,hyaw=0.0,hroll=0.0,hpitch=lerp(0.05,0.5,sm(u)),lid=0.0,pupil=0.0,tail=t*12,crouch=1.0-sm(seg01(u,0.0,0.2)),ears=0.7,mouth=0.0,bpitch=lerp(0.1,-0.55,sm(seg01(u,0.1,1.0))),shades=0.0,cheese=sm(seg01(u,0.8,1.0)))
def legs_quads(t):
    d=drop_of(t); fx=fx_of(t)+(0.004*math.sin(t*60) if 7.2<=t<T_JUMP[0] else 0.0)
    Q=[]
    hipL=(-0.10,0.48,0.12); knL=(-0.22,0.50,-0.30); anL=(-0.26,0.47,-0.78)
    Q+=seg(hipL,knL,0.15,PJ)+seg(knL,anL,0.13,PJ)+box(-0.32,-0.2,0.435,0.5,-0.97,-0.77,SOCK)
    hipR=np.array((0.10,0.48,0.12)); kUp=np.array((0.15,0.58,-0.25)); aUp=np.array((fx,0.95,-0.32)); kRest=np.array((0.24,0.52,-0.35)); aRest=np.array((0.27,0.47,-0.80))
    kn=kUp+(kRest-kUp)*d; an=aUp+(aRest-aUp)*d
    Q+=seg(hipR,kn,0.15,PJ)
    P=lambda u: kn+(an-kn)*u
    Q+=seg(kn,P(0.45),0.13,PJ)+seg(P(0.45),P(0.78),0.1,SKIN)+seg(P(0.78),an+(an-kn)*0.16,0.115,SOCK,0.11)
    ax=an+(an-kn)*0.06; Q+=seg(ax,ax+(an-kn)*0.05,0.12,SOCK_S,0.115)                            # lilac stripe on the sock
    Q+=box(an[0]-0.05,an[0]+0.05,an[1]-0.03+(0.0 if d<0.5 else 0.0),an[1]+0.06,an[2]-0.19*(0.3+0.7*d),an[2]-0.04,SOCK) if d>0.3 else []   # toes lie flat once she gives up
    return Q
def plate_quads(t):
    s=sm(seg01(t,12.6,12.95)); c=PLATE_C
    Q=box(-0.14,0.14,0.0,0.014,-0.14,0.14,CD.PLATE,xf=lambda p:tuple(c+np.array(p,float)))+box(-0.11,0.11,0.014,0.018,-0.11,0.11,CD.PLATE_D,xf=lambda p:tuple(c+np.array(p,float)))
    Q+=slice_quads(c+np.array([-0.04-0.2*s,0.02+0.25*math.sin(PI*min(1,s*1.1)),-0.02-0.1*s]),0.4+3*s,0.5*s,0.8)+slice_quads(c+np.array([0.05+0.22*s,0.02+0.3*math.sin(PI*min(1,s*1.2)),-0.04-0.1*s]),-0.5-2.5*s,-0.4*s,0.8)
    return Q
def cam_shot(t):
    sx=0.008*math.sin(t*1.7)+0.004*math.sin(t*5.1); sy=0.006*math.sin(t*2.3)
    k=max(0.0,1-(t-T_FREEZE+0.12)/0.5) if T_FREEZE-0.12<=t<T_FREEZE+0.4 else 0.0
    return CAM+np.array([sx,sy,0.0]),TGT+np.array([sx*0.5,sy*0.5+0.1*seg01(t,12.0,12.9),0.0]),(7*k*math.sin(t*90),5*k*math.cos(t*77))

# ======================= render =======================
R=Renderer(W,H,fog=(40,30,60))
def render(t,T):
    cp,tg,shake=cam_shot(t); cam=Camera.look(tuple(cp),tuple(tg))
    cs=cat_state(T); cq,cd=cat_model(**cs); cd=[x for x in cd if np.linalg.norm(x['c']-cp)<np.linalg.norm(x['hc']-cp)]
    layers=[CD.ROOM_F,CD.ROOM_W+CEIL,CD.ROOM_B,plate_quads(T),legs_quads(T),cq,cd]
    img,vi=zrender(R,cam,layers,[(a,b,c*0.8) for a,b,c in CD.LIGHTS],fov=FOV,fog_start=14,fog_end=40,ambient=0.42,shake=shake,bias=[1.0]*6+[1.004])
    return post.ps1(img),vi,cs

# ======================= UI (2D overlays) =======================
POV_LINES=['POV: CAT IS','TRYING TO','STEAL YOUR','FOOD']; HIL={'CAT','FOOD'}
def pov_text(d):
    y=6
    for ln in POV_LINES:
        x=(W-font.width(ln,2))//2
        for wd in ln.split(' '): otext(d,wd,x,y,YEL if wd in HIL else WHT,2); x+=font.width(wd,2)+12
        y+=17
def meter(d,t):
    v=los(t); panel(d,5,77,175,103,CYAN if v<0.5 else RED,(12,10,30))
    otext(d,'COVER: FOOT',9,81,YEL,1); st='SPOTTED!' if v>0.7 else ('NOT SEEN' if v<0.3 else 'DANGER'); col=RED if v>0.7 else (GRN if v<0.3 else YEL)
    otext(d,st,171-font.width(st,1),81,col if (v<=0.7 or int(t*10)%2) else (255,150,120),1)
    d.rectangle([9,92,171,99],fill=(30,20,30),outline=(200,200,210)); w=int(160*v); c=(int(60+195*v),int(220-170*v),70)
    if w>0: d.rectangle([10,93,10+w,98],fill=c)
    otext(d,'LINE OF SIGHT',9,89,WHT,1) if False else None
def popups(d,t):
    for te in SPOTS:
        if te<=t<te+0.5:
            k=seg01(t,te,te+0.5); x=int(lerp(12,W-12-font.width('SPOTTED!',2),0.5+0.35*math.sin(te*7))); y=int(124-14*k)
            otext(d,'SPOTTED!',x,y,RED if int(t*12)%2 else (255,140,120),2)
def frame(t):
    T=min(t,T_FREEZE); img,vi,cs=render(t,T); d=ImageDraw.Draw(img)
    if t<T_DASH[1]-0.1: pov_text(d)
    if t<T_JUMP[0]+0.4: meter(d,t)
    popups(d,t)
    if t>=T_WIN:
        a=sm(seg01(t,T_WIN,T_WIN+0.12)); c=YEL if int(t*8)%2 else WHT
        panel(d,3,10,177,62,RED,(40,6,8)); ctext(d,'MISSION FAILED',14,RED,2); ctext(d,'CAT WINS',34,c,3)
        otext(d,'FOOD STOLEN',(W-font.width('FOOD STOLEN',1))//2,300,GRN,1)
    return img

# ======================= QA manifest =======================
def _cat(t): return cat_state(min(t,T_FREEZE))
def _cat_model(**st): return cat_model(**st)[0]
def _extra(t):
    out=[]; cs=cat_state(min(t,T_FREEZE)); x,_,z=cs['base']
    if T_JUMP[0]<=t<T_FREEZE and abs(x-fx_of(t))<0.16 and -0.5<z<-0.15: out.append(('intersect',f'the cat touches her foot (dx {abs(x-fx_of(t)):.2f} m)'))
    if t<T_TIRE and abs(fx_of(t))>0.09: out.append(('stretch','foot sways too far'))
    return out
QA=dict(fps=FPS,dur=DUR,W=W,frame=frame,chars={'cat':(_cat,_cat_model,'_none',1.0)},
    geom=lambda t,name,st,V: [('floor',f'{name} under the floor')] if V[:,1].min()<-0.04 else [],extra=_extra,
    camera=lambda t: cam_shot(t)[0],min_cam_dist=0.2,      # the face-in-lens ending is intentional; the 25 cm near-plane clip limit still applies
    camera_ok=lambda p: 0.3<p[1]<1.2 and abs(p[0])<1.0 and -1.5<p[2]<1.0,
    scenes=[dict(id='cover',t0=0.0,t1=3.0,action='POV: the foot is her cover; the cat peeks, the foot chases'),dict(id='peek',t0=3.0,t1=7.0,action='faster peeks, LINE OF SIGHT fills, SPOTTED'),
            dict(id='chase',t0=7.0,t1=T_TIRE,action='very fast peeks; the foot cannot keep up'),dict(id='hold',t0=T_TIRE,t1=T_DASH[0],action='the foot centres and hides him: NOT SEEN'),
            dict(id='crouch',t0=T_DASH[0],t1=T_JUMP[0],action='the cat crouches and wiggles'),dict(id='jump',t0=T_JUMP[0],t1=T_FREEZE,action='her late swipe misses; he slips past the foot and jumps straight into the lens'),dict(id='win',t0=T_FREEZE,t1=DUR,action='freeze: face in the camera, MISSION FAILED / CAT WINS')],
    weapon_events=[],texts=lambda: [('hook',x,2) for x in POV_LINES]+[('ui',s_,1) for s_ in ('COVER: FOOT','SPOTTED!','NOT SEEN','DANGER','FOOD STOLEN')]+[('ui','SPOTTED!',2),('ui','MISSION FAILED',2),('ui','CAT WINS',3)])

TEST=os.environ.get('TEST')
if TEST and __name__=='__main__':
    ims=[frame(float(x)) for x in TEST.split(',')]; shp=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): shp.paste(im,(i*182,0))
    shp.resize((shp.width*2,640),Image.NEAREST).save('test.png'); sys.exit()


# ======================= AUDIO (same synth palette as the other shorts) =======================
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=29); sr=s.sr; n=s.n; M=np.zeros(n); AMB=np.zeros(n)
    def note(buf,t0,m,d,v,wave='sq',duty=0.5,dec=3.0,att=0.005):
        f=440*2**((m-69)/12); tt=s.T(d); ph=(f*tt)%1
        x=np.where(ph<duty,1.0,-1.0) if wave=='sq' else (4*np.abs(ph-0.5)-1 if wave=='tri' else np.sin(2*np.pi*ph))
        env=np.minimum(1,tt/att)*np.exp(-tt*dec); i=int(t0*sr); j=min(n,i+len(tt)); buf[i:j]+=(x*env*v)[:j-i]
    def nb(t0,d,lo,hi,v,seed,shape=2): s.place(s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v)
    def thud(t0,f=55,v=0.25,d=0.5): tt=s.T(d); s.place(np.sin(2*np.pi*f*tt*(1-0.35*tt/d))*np.exp(-tt*9)+s.filt_short(s.noise(d,int(t0*13)),lo=50,hi=600)*np.exp(-tt*12)*0.5,t0,v)
    def whoosh(t0,d=0.4,v=0.05,seed=0,lo=300,hi=3500): nb(t0,d,lo,hi,v,seed)
    def tick(t0,v=0.03,f=2300): tt=s.T(0.03); s.place(np.sin(2*np.pi*f*tt)*np.exp(-tt*120),t0,v)
    def zip_(t0,v=0.05,f0=500,f1=2400,d=0.13): tt=s.T(d); s.place(np.sin(2*np.pi*np.cumsum(f0+(f1-f0)*tt/d)/sr)*np.exp(-tt*14)*np.minimum(1,tt/0.004),t0,v)
    def pad(t0,v=0.035,seed=0): thud(t0,90,v,0.15); nb(t0,0.06,1500,6000,v*0.3,seed,1)
    def meow(t0,d=0.55,v=0.2,f=620):
        tt=s.T(d); fr=f*(1+0.55*np.sin(np.pi*tt/d)-0.25*tt/d)*(1+0.012*np.sin(2*np.pi*7*tt)); ph=np.cumsum(fr)/sr
        x=np.sin(2*np.pi*ph)+0.6*np.sin(4*np.pi*ph)+0.35*np.sin(6*np.pi*ph)+0.2*np.sin(8*np.pi*ph)
        s.place(s.filt_short(x,lo=300,hi=3800)*np.sin(np.pi*tt/d)**0.7,t0,v)
    def sneaky(a,b,v=1.0,step=0.2,tense=0.0):
        bass=[45,45,52,45,48,48,52,48]; mel=[69,0,72,0,76,72,0,69,67,0,69,0,72,0,64,0]; k=0; tc=a
        while tc<b-1e-6:
            if k%2==0: note(M,tc,bass[(k//2)%8],step*1.5,0.06*v,'tri',dec=7)
            if mel[k%16]: note(M,tc,mel[k%16]+12*(1 if tense else 0),step*0.6,0.018*v,'sq',0.25,10)
            if tense and k%4==2: nb(tc,0.05,2000,8000,0.025*v,int(tc*100)+3,1)
            k+=1; tc+=step
    AMB+=s.filt(s.rng.normal(0,1,n),lo=80,hi=800)*0.008
    # ---------- music: slow stealth march that speeds up ----------
    sneaky(0.05,3.0,0.7,step=0.26); sneaky(3.0,7.2,0.9,step=0.2,tense=1.0); sneaky(7.2,T_TIRE,1.1,step=0.15,tense=1.0)
    for k in range(int((T_JUMP[0]-T_TIRE)/0.1)): note(M,T_TIRE+k*0.1,33+(k%2),0.12,0.03+0.001*k,'tri',dec=5)                # crouch tension
    for k,m in enumerate((57,60,64,67,69,72,76,79,81,84,88)): note(M,T_JUMP[0]+k*0.06,m,0.12,0.03,'sq',0.25,8)                 # the jump run-up
    # ---------- sfx ----------
    for k,t0 in enumerate(FL):
        zip_(t0,0.04,500+60*(k%3),1700+100*(k%3),0.11)                                                   # the cat pops out
        whoosh(t0+0.12,0.25,0.035,int(t0*10),400,3500)                                                   # the foot chases
    for te in SPOTS:                                                                                     # SPOTTED!
        for k,m in enumerate((88,95)): note(M,te+k*0.09,m,0.1,0.055,'sq',0.5,10)
        thud(te,70,0.1,0.2)
    whoosh(T_JUMP[0]+0.1,0.3,0.07,79,400,4000); tick(T_JUMP[0]+0.45,0.04,900)                         # her late swipe: whiff
    for k in range(int((T_JUMP[0]-T_DASH[0]-0.1)/0.1)): pad(T_DASH[0]+0.1+k*0.1,0.02+0.002*k,80+k)                               # butt wiggle
    zip_(T_JUMP[0],0.09,300,1500,0.22); thud(T_JUMP[0],80,0.18,0.2); whoosh(T_JUMP[0]+0.05,0.7,0.09,73,200,3500)              # boing + the flight
    thud(T_FREEZE,45,0.5,0.5); nb(T_FREEZE,0.3,100,2500,0.12,75)
    M[int(T_FREEZE*sr):int(T_WIN*sr)]=0
    for k,m in enumerate((67,72,76,84)): note(M,T_WIN+k*0.09,m,0.3,0.06,'sq',0.5,4)
    for f_ in (261.6,329.6,392.0,523.3): note(M,T_WIN+0.4,69+12*math.log2(f_/440),1.3,0.04,'sq',0.25,2.0)
    meow(T_FREEZE+0.02,0.5,0.22,640); tick(T_WIN+0.62,0.05,4200)
    for k,f in enumerate((3200,4200,5200)): tt=s.T(0.7); s.place(np.sin(2*np.pi*f*tt)*np.exp(-tt*6),T_WIN+0.5+k*0.07,0.025)
    # ---------- voice ----------
    NB=np.zeros(n); duck=np.ones(n)
    a,ar=_sf.read(os.path.join(TTS_DIR,'cp','N1.wav')); a=a if a.ndim==1 else a.mean(1)
    a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a); act=a[np.abs(a)>0.02]; a=a/(np.sqrt((act**2).mean())+1e-9)*0.2
    i=int(0.05*sr); j=min(n,i+len(a)); NB[i:j]+=a[:j-i]; duck[max(0,i-int(0.05*sr)):min(n,j+int(0.1*sr))]=0.4
    duck=np.convolve(duck,np.ones(2400)/2400,'same')
    s.L+=2.0*M*duck+AMB; s.R+=2.0*np.roll(M,240)*duck+np.roll(AMB,700)
    s.reverb(0.12,length=1.0,decay=4.0)
    pk=max(np.abs(s.L).max(),np.abs(s.R).max()); gv=pk*1.05/np.abs(NB).max()
    s.L=s.L*(0.6+0.4*duck)+NB*gv; s.R=s.R*(0.6+0.4*duck)+NB*gv
    st=np.stack([s.L,s.R],1); k=int(0.25*sr); st[-k:]*=np.linspace(1,0,k)[:,None]
    st=st/np.max(np.abs(st))*0.9; _sf.write(path,st,sr,subtype='PCM_16'); return path
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'cat_pov.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'cp_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.96,vignette=0.22,grain=1.5,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(post.upscale(frame(f/FPS),S),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
