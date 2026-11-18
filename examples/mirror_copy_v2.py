"""WHY DO MIRRORS COPY US? v2 - tighter, closer, more game-like cut (34 s, 816 frames @ 24 fps). Imports the locked assets of mirror_copy.py (robot, mirror room, 2D reflection
sprite, subtitle + UI helpers) and only adds what is new: a closer camera with slow push-ins, squash & stretch, a MIRROR SYNC HUD that drains / refills (stakes in frame 0),
a tighter script (tools/tts/mc2.py -> $TTS_DIR/mc2/*.wav), screen-pop on the beats, a 'Zz' while the reflection rests, and a new payoff line.
Run: TEST=0.1,6 python examples/mirror_copy_v2.py -> test.png | PART=a:b | PART=audio      QA: python tools/qa/scene_qa.py examples/mirror_copy_v2.py"""
import os, sys, math, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
_T=os.environ.pop('TEST',None)
import numpy as np
from PIL import Image, ImageDraw, ImageChops
import mirror_copy as mc
if _T is not None: os.environ['TEST']=_T
from nightkit import post, font
from nightkit.engine import Camera
from nightkit.zraster import zrender
from nightkit.audio import Sound
sm,seg01,PI,lerp,env=mc.sm,mc.seg01,mc.PI,mc.lerp,mc.env
IDLE,UP=mc.IDLE,mc.UP
TTS_DIR=mc.TTS_DIR; OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6; DUR=34.0; N=int(round(DUR*FPS)); N_OUT=N
try: SCR=json.load(open(os.path.join(TTS_DIR,'mc2','script.json')))
except Exception: SCR=None

# ======================= narration schedule (measured lengths) =======================
ORDER=['1a','1b','2a','2b','3a','3b','4a','5a','5b','6a','7a','7b','7c']
TEXT={'1a':"Why do mirrors copy us?",'1b':"Today, his reflection was a second late.",'2a':"He tried harder. Arms up. Arms down. Still behind.",'2b':"Then it froze.",
      '3a':"A message appeared: BREAK REQUESTED.",'3b':"Wait... reflections get tired?",'4a':"He waved again. Nothing.",'5a':"The mirror wasn't magic.",
      '5b':"Someone inside had been copying him all day.",'6a':"So he stood still, and let it rest.",'7a':"Then the reflection moved first.",'7b':"YOUR TURN.",'7c':"Even your reflection deserves a day off."}
DURS={k:(SCR['dur'][k] if SCR else 2.0) for k in ORDER}
GAP=(DUR-0.2-sum(DURS.values()))/(len(ORDER)-1)
ST={}; _t=0.05
for k in ORDER: ST[k]=_t; _t+=DURS[k]+GAP
def s(k,o=0.0): return ST[k]+o
mc.ORDER,mc.ST,mc.DURS=ORDER,ST,DURS; mc.TEXT.update(TEXT); mc.HIL|={'TIRED?','MAGIC.','DAY','OFF.','FROZE.'}      # reuse mirror_copy's subtitle chunker / drawer
SUBS=mc.sub_chunks(); mc.SUBS=SUBS
_first={}
for k in ORDER: _first.setdefault(int(k[0]),k)
CUTS=[0.0]+[round((ST[_first[i]]-GAP/2)*FPS)/FPS for i in range(2,8)]+[DUR]            # shot i = CUTS[i-1] .. CUTS[i]
def shot_of(t):
    for i in range(1,8):
        if t<CUTS[i]: return i
    return 7
def cam_id(t): return 'B' if shot_of(t) in (3,5) else 'A'

# ======================= camera: closer than v1, slow push-in on the A shots =======================
RB2=(0.12,0.0,0.5)
def cam_shot(t):
    i=shot_of(t); u=seg01(t,CUTS[i-1],CUTS[i])
    if cam_id(t)=='A': z=lerp(-2.45,-2.15,u) if i!=1 else lerp(-2.4,-2.2,u); return (0.5,1.15,z),(0.5,1.0,1.25),34.0
    return (0.62,1.2,lerp(-1.1,-0.85,u)),(0.62,1.05,1.25),42.0

# ======================= animation: the real robot =======================
def real_pose(t):
    p=dict(IDLE); sq=0.0
    w1=1-sm(seg01(t,s('1b',1.9),s('1b',2.4)))
    w4=max(env(t,s('4a',0.1),s('4a',0.9),0.25,0.25),env(t,s('4a',1.15),s('4a',1.75),0.25,0.25))
    wave=max(w1,w4); ph=2*PI*2.8*t
    up=max(env(t,s('2a',0.2),s('2a',1.3),0.35,0.35),env(t,s('2a',1.9),s('2b',0.9),0.35,0.4),sm(seg01(t,s('7c',0.15),s('7c',0.55))))
    p['aW']=lerp(0.14,UP,up) if up>=wave else lerp(0.14,2.25,wave); p['aO']=lerp(0.14,UP,up)
    p['bW']=wave*0.6*math.sin(ph)*(0.7 if w4>0 and wave==w4 else 1.0); p['bO']=0.0
    hopA=0.08*abs(math.sin(2*PI*1.7*(t-s('2a',2.4))))*env(t,s('2a',2.4),s('2b',0.6),0.05,0.05)
    hopB=0.08*math.sin(PI*seg01(t,s('7c',1.05),s('7c',1.5)))
    p['hop']=hopA+hopB; act=max(env(t,s('2a',2.4),s('2b',0.6),0.05,0.05),env(t,s('7c',1.0),s('7c',1.6),0.02,0.02))
    p['sq']=0.6*max(0.0,1-p['hop']/0.03)*act
    p['roll']=0.3*max(env(t,s('1b',0.3),s('1b',1.6)),0.6*env(t,s('2b',0.5),s('3a',0.4)),env(t,s('3a',1.5),s('3b',0.7)),0.7*env(t,s('7a',1.2),s('7b',0.8)))
    hs=0.35*math.sin(2*PI*1.5*(t-s('7a',1.2)))*env(t,s('7a',1.2),s('7b',0.9),0.1,0.1)
    p['hyaw']=-0.15-0.25*env(t,s('2b',0.5),s('3a',1.0))-0.2*env(t,s('5a',0.0),s('5b',2.8))+hs
    p['hp']=0.18*env(t,s('5a',0.2),s('5a',1.6))+0.35*math.sin(PI*seg01(t,s('6a',1.5),s('6a',2.4)))
    bl=math.sin(PI*seg01(t,s('3b',0.05),s('3b',0.25)))+math.sin(PI*seg01(t,s('1b',2.3),s('1b',2.5)))
    p['eyes']=1.0-min(1.0,bl)+0.4*env(t,s('3b',0.3),s('3b',1.4),0.1,0.3)+0.4*env(t,s('5b',0.0),s('5b',1.0),0.1,0.3)         # eyes widen on surprise
    p['mouth_o']=env(t,s('3b',0.3),s('3b',1.4),0.1,0.3)>0.4 or env(t,s('5b',0.0),s('5b',1.0),0.1,0.3)>0.4
    p['smile']=s('6a',1.6)<=t<s('7a',0.0)
    return p

# ======================= animation: the reflection =======================
T_FREEZE=s('2b',0.3); T_REST=s('3b',0.0); T7=s('7a',0.0)
def lag(t):
    if t<s('2a'): return 1.0
    return lerp(1.0,1.7,seg01(t,s('2a'),s('2a',0.6)))
def vmax(t):
    if t<s('2a'): return 7.0
    if t<T_FREEZE: return 2.2
    if t<T7: return 1.2
    return 8.0
def ref_target(t):
    if t<T_FREEZE:
        tau=t-lag(t); return dict(IDLE) if tau<0 else real_pose(tau)
    if t<T_REST: return dict(IDLE,aW=UP,aO=UP)
    if t<T7: return dict(IDLE,hop=0.012*(0.5+0.5*math.sin(2*PI*0.4*t)))
    u=sm(seg01(t,s('7a',0.5),s('7a',1.0)))
    return dict(IDLE,aW=lerp(0.14,UP,u),aO=lerp(0.14,UP,u),hop=0.08*math.sin(PI*seg01(t,s('7c',0.6),s('7c',1.05))))
_DT=1/240.; _TS=np.arange(0,DUR+1,_DT); _K=mc._K
def _sim():
    X={k:np.zeros(len(_TS)) for k in _K}; x={k:IDLE[k] for k in _K}
    for i,t in enumerate(_TS):
        tg=ref_target(t); vm=vmax(t)*_DT
        for k in _K: x[k]+=float(np.clip(14*(tg[k]-x[k])*_DT,-vm,vm)); X[k][i]=x[k]
    return X
_SIM=_sim()
def ref_eyes(t):
    e=1.0-0.2*seg01(t,s('1b'),s('2a',1.5))-0.2*seg01(t,s('2a',1.5),T_FREEZE)
    if t>=s('3a',0.3): e=lerp(e,0.2,sm(seg01(t,s('3a',0.3),s('3a',1.8))))
    if t>=s('4a'): e=0.35
    if t>=s('5a',0.3): e=0.35*(1-math.sin(PI*seg01(t,s('5a',0.4),s('5a',1.3)))**0.5) if t<s('5a',1.4) else 0.35
    if t>=s('6a',0.4): e=lerp(0.35,0.0,sm(seg01(t,s('6a',0.4),s('6a',0.9))))
    if t>=s('6a',1.6): e=lerp(0.0,1.0,sm(seg01(t,s('6a',1.6),s('6a',2.0))))
    return e,(s('6a',2.0)<=t<s('7a',0.4))
def ref_pose(t):
    p=dict(IDLE)
    for k in _K: p[k]=float(np.interp(t,_TS,_SIM[k]))
    p['eyes'],p['happy']=ref_eyes(t); p['smile']=t>=s('6a',1.9); return p

# ======================= render =======================
R=mc.R
def pop(t,t0,a=3.0,d=0.28):
    u=(t-t0)/d
    return (int(round(a*math.sin(70*(t-t0))*(1-u))),int(round(a*0.6*math.cos(55*(t-t0))*(1-u)))) if 0<=u<1 else (0,0)
def render(t):
    cp,tg,fov=cam_shot(t); cpa=np.array(cp); cam=Camera.look(cp,tg); st=real_pose(t)
    rq,rd=mc.robot(st,base=RB2); rd[:]=[x for x in rd if np.linalg.norm(x['c']-cpa)<np.linalg.norm(x['hc']-cpa)]
    lights=[((mc.LAMP_POS[0],mc.LAMP_POS[1]-0.1,mc.LAMP_POS[2]-0.2),(255,236,190),0.8)]
    img,vi,zb=zrender(R,cam,[mc.ROOM_F,mc.ROOM_W,mc.ROOM_FR,mc.ROOM_L,rq,rd],lights,fov=fov,fog_start=6,fog_end=18,ambient=0.40,bias=[1,1,1,1,1,1.004],return_z=True)
    a=np.asarray(img).astype(np.float32)*np.array([0.88,0.94,1.1],np.float32); im=Image.fromarray(np.clip(a,0,255).astype(np.uint8)); d=ImageDraw.Draw(im)
    x0,x1=mc.MX-mc.MW/2,mc.MX+mc.MW/2; v2=R.view(cam,fov); pts=[R.project((x,y,mc.ZM),v2) for x,y in ((x0,mc.MY0),(x1,mc.MY0),(x1,mc.MY1),(x0,mc.MY1))]
    mc.glint(im,a,cam,fov,pts)
    sp=Image.new('RGBA',(W,H),(0,0,0,0)); mc.reflection(ImageDraw.Draw(sp),ref_pose(t),cam,fov)
    clip=Image.new('L',(W,H),0); ImageDraw.Draw(clip).polygon([(p_[0],p_[1]) for p_ in pts],fill=255)
    sp.putalpha(Image.fromarray(np.minimum(np.asarray(sp)[...,3],np.asarray(clip)))); im.paste(sp,(0,0),sp)
    return post.ps1(im),cam,fov,pts

# ======================= HUD + UI (2D overlays) =======================
ACC,WHT,RED,CYAN=mc.ACC,mc.WHT,mc.RED,mc.CYAN
def sync(t):
    if t<s('2a'): return lerp(62,55,seg01(t,0,s('2a')))
    if t<T_FREEZE: return lerp(55,18,seg01(t,s('2a'),T_FREEZE))
    if t<T7: return 0.0
    return 100*sm(seg01(t,s('7c',0.15),s('7c',1.3)))
def hud(d,t):
    v=sync(t); lost=v<1 and t<T7; ok=v>=100 or t>=T7
    col=(130,255,150) if t>=s('7c',0.15) else (RED if v<45 and int(t*6)%2==0 or lost else ACC if v>=45 else (255,200,200))
    lab='SYNC LOST' if lost else ('SYNC' if t<T7 or t>=s('7c',0.15) else 'SYNC')
    if t>=T7 and t<s('7c',0.15): lab='RESTING' if False else 'SYNC'
    if T_REST<=t<T7 and t>=s('6a',0.4): lab='ON BREAK'; col=CYAN
    d.rectangle([0,0,114,22],fill=(8,8,20)); font.text(d,lab,4,4,col,1,(0,0,0)); d.rectangle([4,14,4+104,19],fill=(8,8,20),outline=col)
    if v>0: d.rectangle([5,15,5+int(102*v/100),18],fill=col)
def ui(d,t):
    A=lambda k,o: s(k,o)
    a,b=0.0,A('1b',3.0)
    if a<=t<b and int((t-a)*5)%2==0: mc.ui_box(d,['LAG DETECTED'],26,RED)
    a,b=A('3a',0.9),A('3b',0.1)
    if a<=t<b: mc.ui_box(d,['BREAK','REQUESTED'],172,RED if int((t-a)*8)%2==0 else (255,200,200),3)
    a,b=A('4a',0.4),CUTS[4]
    if a<=t<b: mc.ui_box(d,['REFLECTION','OFFLINE'],26,RED if int((t-a)*4)%2==0 else ACC)
    a,b=A('5a',1.2),CUTS[5]
    if a<=t<b: mc.ui_box(d,['MIRROR','EMPLOYEE:','EXHAUSTED'],24,CYAN if t-a<0.25 or int((t-a)*3)%2==0 else (200,240,255))
    a,b=A('7b',-0.05),A('7c',0.9)
    if a<=t<b: mc.ui_box(d,['YOUR TURN'],26,ACC if int((t-a)*8)%2==0 else (255,244,170),3)
    a,b=A('7c',1.05),DUR
    if a<=t<b:
        u=min(1.0,(t-a)/0.25); y=int(lerp(-60,26,sm(u))); mc.ui_box(d,['SHIFT','STARTED'],y,(130,255,150) if int((t-a)*8)%2==0 else (220,255,225),3)
    if s('6a',0.9)<=t<s('6a',1.8):                                                  # Zz while the reflection rests
        u=(t-s('6a',0.9))/0.9
        for k,(ch,sc) in enumerate((('Z',2),('z',1))): font.text(d,ch,int(112+10*k+6*u),int(120-22*u-12*k),(200,230,255),sc,(0,0,0))
def frame(t):
    img,cam,fov,pts=render(t)
    for t0,amp in ((T_FREEZE,4.0),(s('3a',0.9),3.0),(s('7c',1.05),3.0),(0.0,3.0)):
        dx,dy=pop(t,t0,amp)
        if dx or dy: img=ImageChops.offset(img,dx,dy)
    d=ImageDraw.Draw(img); hud(d,t); ui(d,t); mc.subtitles(d,t); return img

# ======================= QA manifest =======================
def robot_state(t): return dict(base=RB2,yaw=mc.YAW,**real_pose(t))
def robot_model(**st): return mc.robot({k:v for k,v in st.items() if k not in ('base','yaw')},base=RB2)[0]
def _extra(t):
    out=[]
    if t<0.05:
        r=real_pose(0.0); f=ref_pose(0.0)
        if not (r['aW']>1.5 and f['aW']<0.6): out.append(('reflection','first frame must show the robot waving and the reflection arm still down'))
        cp,tg,fov=cam_shot(0.0); pr=R.project((RB2[0],1.0,RB2[2]),R.view(Camera.look(cp,tg),fov))
        if not pr or not (0<pr[0]<W): out.append(('camera','robot is not in the first frame'))
    if abs(t-s('3a',0.95))<0.02 and ref_pose(t)['aW']<2.0: out.append(('reflection','reflection is not frozen with arms up when BREAK REQUESTED appears'))
    if t>=s('7a',1.2) and ref_pose(t)['aW']<2.0: out.append(('reflection','reflection arms not up in the final shot'))
    return out
QA=dict(fps=FPS,dur=DUR,W=W,frame=lambda t: frame(t),chars={'robot':(robot_state,robot_model,'_none',1.0)},
    geom=lambda t,name,st,V: [('floor',f'{name} under the floor')] if V[:,1].min()<-0.04 else ([('wall',f'{name} inside the back wall')] if V[:,2].max()>mc.WALL_Z-0.05 else []),
    extra=_extra,camera=lambda t: cam_shot(t)[0],min_cam_dist=0.4,camera_ok=lambda p: -4.0<p[2]<0.0 and 0.1<p[1]<2.0,allow_jump=[],weapon_events=[],
    scenes=[dict(id=f'shot{i}',t0=CUTS[i-1],t1=CUTS[i],action=a) for i,a in enumerate((
        'robot waving big in frame 0, reflection arm down, LAG DETECTED, SYNC bar (cam A)','arms up/down then dance, reflection falls behind and freezes with arms up (cam A)','BREAK REQUESTED, tired eyes, robot surprised (cam B)',
        'robot waves twice, reflection offline (cam A)','slow blink, MIRROR EMPLOYEE: EXHAUSTED (cam B)','robot stands still, reflection rests, Zz, happy eyes, nod (cam A)','reflection moves first, YOUR TURN, robot copies, SHIFT STARTED (cam A)'),1)],
    texts=lambda: [('sub',' '.join(r),mc.SUB_SC) for _,_,rows,_ in SUBS for r in rows]+[('ui',l,sc) for l,sc in (('LAG DETECTED',2),('BREAK',3),('REQUESTED',3),('REFLECTION',2),('OFFLINE',2),('MIRROR',2),('EMPLOYEE:',2),('EXHAUSTED',2),('YOUR TURN',3),('SHIFT',3),('STARTED',3),('SYNC LOST',1),('ON BREAK',1))])

TEST=os.environ.get('TEST')
if TEST and __name__=='__main__':
    ims=[frame(float(x)) for x in TEST.split(',')]; shp=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): shp.paste(im,(i*182,0))
    shp.resize((shp.width*2,640),Image.NEAREST).save('test.png'); sys.exit()

# ======================= AUDIO: synthesized loop (curious -> tension -> warm -> playful payoff), room bed, foley, UI sounds, narration =======================
def build_audio(path):
    import soundfile as _sf
    s_=Sound(DUR,loop=False,seed=72); sr=s_.sr; n=s_.n; M=np.zeros(n); M2=np.zeros(n); AMB=np.zeros(n)
    def hz(m): return 440*2**((m-69)/12)
    def note(buf,t0,m,d,v,wave='tri',dec=3.0,att=0.005):
        tt=s_.T(d); ph=2*np.pi*hz(m)*tt
        x={'sin':np.sin(ph),'tri':(2/np.pi)*np.arcsin(np.sin(ph)),'bell':np.sin(ph)+0.35*np.sin(2*ph)+0.12*np.sin(3.01*ph),'sq':np.sign(np.sin(ph))*0.5}[wave]
        i=int(t0*sr); j=min(n,i+len(tt)); buf[i:j]+=(x*np.minimum(1,tt/att)*np.exp(-tt*dec)*v)[:j-i]
    def tone(t0,f0,f1,d,v,harm=(1.0,0.4)):
        tt=s_.T(d); fr=f0+(f1-f0)*(tt/d); ph=np.cumsum(fr)/sr; x=sum(h*np.sin(2*np.pi*ph*(k+1)) for k,h in enumerate(harm))
        s_.place(x*np.minimum(1,tt/0.004)*np.sin(np.pi*np.clip(tt/d,0,1))**0.5,t0,v)
    def nb(t0,d,lo,hi,v,seed): s_.place(s_.filt_short(s_.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s_.T(d)/d),t0,v)
    def thud(t0,f=70,v=0.1,d=0.2): tt=s_.T(d); s_.place(np.sin(2*np.pi*f*tt*(1-0.3*tt/d))*np.exp(-tt*16),t0,v)
    def servo(t0,d=0.35,v=0.035,f=520,up=True): tone(t0,f,f*1.5 if up else f*0.7,d,v,harm=(1.0,0.5,0.25)); nb(t0,d,1500,5000,v*0.5,int(t0*97))
    def whirr(a,b,v=0.02):
        t0=a
        while t0<b: servo(t0,0.16,v,640+60*((int(t0*7))%3)); t0+=0.36
    def blip(t0,m,v=0.05,d=0.12): note(M2,t0,m,d,v,'sq',14.0)
    def delayed(t0,v=0.03): tone(t0,900,1100,0.09,v,harm=(1.0,0.3))
    AMB+=s_.filt(s_.rng.normal(0,1,n),lo=40,hi=260)*0.06+s_.filt(s_.rng.normal(0,1,n),lo=1800,hi=5000)*0.003
    tt=s_.t; AMB+=(np.sin(2*np.pi*100*tt)+0.3*np.sin(2*np.pi*200*tt))*0.006
    B=0.5; bass=[45,48,52,48,45,47,52,47,41,45,48,45,40,44,47,44]; mel=[76,0,72,74,76,0,79,77,76,0,72,71,69,0,0,0]
    t_ten=T_FREEZE-0.6; t_warm=s('6a',-0.2); t_pay=s('7a',0.0)
    for k in range(int(t_ten/(B/2))):
        t0=0.05+k*B/2
        if k%2==0: note(M,t0,bass[(k//2)%16],0.45,0.06,'tri',5.0)
        if mel[k%16]: note(M,t0,mel[k%16],0.35,0.026,'bell',6.0)
    for k in range(int((t_warm-t_ten)/B)): note(M,t_ten+k*B,[38,38,41,40][(k//2)%4],0.5,0.06,'tri',3.5)
    for k in range(int((t_warm-t_ten)/(B/2))):
        if k%3==0: note(M,t_ten+k*B/2,[62,63,62,61][(k//3)%4],0.15,0.012,'sq',12.0)
    for k in range(int((t_pay-t_warm)/(B/2))):
        if k%2==0: note(M,t_warm+k*B/2,[60,64,67,72,71,67,64,67][(k//2)%8],1.0,0.032,'bell',2.6)
    for m_ in (48,55,60,64): note(M,t_warm,m_,t_pay-t_warm+0.4,0.02,'sin',0.5,0.8)
    for k in range(int((DUR-t_pay)/(B/2))):
        t0=t_pay+k*B/2
        if k%2==0: note(M,t0,[45,52,45,50][(k//2)%4],0.4,0.06,'tri',4.0)
        note(M,t0,[84,88,91,88,84,79][k%6],0.3,0.03,'bell',6.0)
    whirr(0.0,s('1b',2.0)); whirr(s('4a',0.1),s('4a',0.9)); whirr(s('4a',1.15),s('4a',1.75))
    t0=1.0
    while t0<s('1b',3.0): delayed(t0); t0+=0.36                                                              # the reflection's late echo
    for t0 in (s('2a',0.2),s('2a',1.9)): servo(t0,0.4,0.04,520,True)
    for t0 in (s('2a',1.0),s('2b',0.9)): servo(t0,0.4,0.04,700,False)
    for t0 in (s('2a',0.2)+1.7,s('2a',1.9)+1.7): servo(t0,0.9,0.02,420,True)
    for k,t0 in enumerate(np.arange(s('2a',2.4),s('2b',0.6),0.294)): blip(t0,[72,76,79,76,84][k%5],0.045); thud(t0+0.02,90,0.03,0.08)
    tt=s_.T(0.7); fr=900*np.exp(-tt*4.5); s_.place(np.sin(np.cumsum(fr)/sr*2*np.pi)*np.exp(-tt*4)+0.4*s_.filt_short(s_.noise(0.7,5),lo=300,hi=3000)*np.exp(-tt*8),T_FREEZE,0.16)   # record-stop
    for k in range(2): tone(s('3a',0.9)+k*0.28,1180,1180,0.18,0.07,harm=(1.0,0.5,0.3))                         # BREAK REQUESTED
    note(M2,s('3b',0.3),88,0.25,0.04,'sq',10.0)                                                              # surprised blip
    for k,m_ in enumerate((70,65,58)): blip(s('4a',0.4)+k*0.3,m_,0.05,0.25)                                  # low battery
    for k,m_ in enumerate((72,76,79,84)): note(M2,s('5a',1.2)+k*0.1,m_,0.9,0.045,'bell',3.5)                 # realization
    for k,m_ in enumerate((79,84,88)): note(M2,s('6a',1.9)+k*0.12,m_,1.2,0.045,'bell',2.8)                   # gentle positive chime
    note(M2,s('7b',-0.05),84,0.3,0.05,'sq',8.0); note(M2,s('7b',-0.05)+0.12,91,0.4,0.05,'sq',6.0)
    for k,m_ in enumerate((72,76,79,84,88)): note(M2,s('7c',1.05)+k*0.07,m_,0.9,0.05,'bell',3.0); note(M2,s('7c',1.05)+k*0.07,m_-12,0.6,0.03,'sq',6.0)
    for t0 in (s('7a',0.5),s('7c',0.6)): servo(t0,0.4,0.03,600,True)
    for t0 in (s('7c',0.15),s('7c',1.05)): servo(t0,0.4,0.03,600,True)
    NB=np.zeros(n); duck=np.ones(n)
    for key in ORDER:
        a,_=_sf.read(os.path.join(TTS_DIR,'mc2',key+'.wav')); a=a if a.ndim==1 else a.mean(1)
        act=a[np.abs(a)>0.02]; a=a*0.2/(np.sqrt((act**2).mean())+1e-9)
        i=int(ST[key]*sr); j=min(n,i+len(a)); NB[i:j]+=a[:j-i]; duck[max(0,i-int(0.05*sr)):min(n,j+int(0.1*sr))]=0.55
    duck=np.convolve(duck,np.ones(2400)/2400,'same')
    s_.L+=AMB+M*duck*3.2+M2; s_.R+=np.roll(AMB,900)+np.roll(M,300)*duck*3.2+M2
    s_.reverb(0.1,length=0.9,decay=4.0)
    pk=max(np.abs(s_.L).max(),np.abs(s_.R).max()); gv=pk/np.abs(NB).max()*0.95
    s_.L=s_.L*(0.8+0.2*duck)+NB*gv; s_.R=s_.R*(0.8+0.2*duck)+NB*gv
    st=np.stack([s_.L,s_.R],1); k=int(0.05*sr); st[-k:]*=np.linspace(1,0,k)[:,None]
    st=st/np.max(np.abs(st))*0.9; _sf.write(path,st,sr,subtype='PCM_16'); return path
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'mirror_v2.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'm2_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.96,vignette=0.25,grain=1.5,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(post.upscale(frame(f/FPS),S),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
