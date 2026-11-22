"""ONE TAKE, mimic v2 - the story version (Enes, 22 Nov): one continuous take whose camera BREATHES with the story:
close on the chest -> pulls back: heroes come, take the gold, leave (time-lapse) -> pushes in: empty chest, dust, it learns to bite ->
pulls back: one knight comes, does not draw his sword, kneels -> close on his hand: a coin -> back to the opening close-up (loop).
Reuses the chest from examples/onetake/mimic_v1.py and the locked knight from examples/final_boss.py. Separate from the main look.
Voice: tools/onetake/voice_mimic.py (placeholder). Run: TEST=1,5,9,12,15,17.5,21 python examples/onetake/mimic_v2.py | PART=a:b | PART=audio"""
import os, sys, math
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.join(HERE,'..','..')
sys.path.insert(0,HERE); sys.path.insert(0,os.path.join(ROOT,'examples')); sys.path.insert(0,ROOT)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import mimic_v1 as M
import final_boss as FB
from nightkit.engine import Camera, quad
from nightkit.zraster import zrender
from nightkit import motion
sm=motion.smooth; PI=math.pi; seg01=M.seg01; lerp=M.lerp; box=M.box; hsh=M.hsh

DUR=26.0; FPS=M.FPS; N=int(round(DUR*FPS)); M.DUR=DUR
M.LINES=[('1',0.3),('2',2.8),('3',6.6),('4',10.5),('5',13.0),('6',16.2),('7',18.9)]
T_HEROES=(3.0,7.4); NH=9
def hero_win(i): a=T_HEROES[0]+i*(T_HEROES[1]-T_HEROES[0]-0.9)/(NH-1); return a,a+0.9
M.T_LAPSE=(3.0,7.4); M.T_DUST=(7.6,10.2); M.T_BITE=11.65; M.T_ARM=(13.0,15.8); M.T_COIN=17.75; M.T_CALM=(18.9,23.5)
T_KN=(12.8,14.3); T_OPEN=(14.3,15.0); T_KNEEL=(15.5,16.2); T_REACH=(16.4,17.7); T_RISE=(19.6,20.6); T_LEAVE=(20.8,23.2)

# ---------------- chest behaviour overrides ----------------
def gold_level(t):
    k=sum(1 for i in range(NH) if t>=hero_win(i)[0]+0.55); return 1.0-k/NH
def lid_angle(t):
    a=0.06+0.05*math.sin(t*3.0)
    for i in range(NH):
        a0,a1=hero_win(i); u=seg01(t,a0+0.3,a1-0.15)
        if 0<u<1: a=max(a,0.75*math.sin(PI*u))
    if M.T_BITE-0.6<=t<M.T_BITE+0.6:
        u=seg01(t,M.T_BITE-0.6,M.T_BITE+0.6); a=0.95*math.sin(PI*min(1,u*1.6)) if u<0.62 else 0.06
    if M.T_BITE+0.6<=t<T_OPEN[0]: a=0.06+0.02*math.sin(t*9)
    if T_OPEN[0]<=t<M.T_CALM[0]+0.4: a=lerp(0.06,0.85,sm(seg01(t,T_OPEN[0],T_OPEN[1])))
    if t>=M.T_CALM[0]+0.4: a=lerp(0.85,0.06,sm(seg01(t,M.T_CALM[0]+0.4,M.T_CALM[1])))+0.05*math.sin(t*3.0)*seg01(t,M.T_CALM[1]-0.4,DUR)
    return a
def cutaway(t): return sm(seg01(t,2.4,3.1))*(1-sm(seg01(t,M.T_CALM[1]-0.3,DUR-0.6)))
def coins_out(t):                                                           # a small burst when each hero grabs
    Q=[]
    for i in range(NH):
        tb=hero_win(i)[0]+0.5; u=t-tb
        for j in range(4):
            if 0<u<0.45:
                vx=0.6+hsh(i*7+j)*0.6; vy=1.6+hsh(i*7+j,2); vz=(hsh(i*7+j,3)-0.5)*0.8
                x,y,z=vx*u,M.CH*0.7+vy*u-4.9*u*u,vz*u
                if y>0: Q+=box(x-0.03,x+0.03,y-0.01,y+0.01,z-0.03,z+0.03,M.GOLD,emit=True)
    return Q
M.INSIDE=(18,10,8); M.gold_level=gold_level; M.lid_angle=lid_angle; M.cutaway=cutaway; M.coins_out=coins_out

# ---------------- the room ----------------
STONE=(64,60,74); STONE_D=(46,43,56)
def room():
    Q=[]
    for i in range(-5,6):
        for j in range(-3,6):
            c=(40,38,50) if (i+j)%2 else (34,32,44); q=quad([(i,0,j),(i+1,0,j),(i+1,0,j+1),(i,0,j+1)],c); q['wind']=1; Q.append(q)
    Q+=box(-5,6,0,3.6,-3.4,-3.0,STONE)                                      # back wall
    Q+=box(4.4,4.8,0,3.6,-3.0,-1.3,STONE)+box(4.4,4.8,0,3.6,0.3,6,STONE)+box(4.4,4.8,2.6,3.6,-1.3,0.3,STONE)   # right wall with a doorway
    Q+=box(4.79,4.8,0,2.6,-1.3,0.3,(8,8,12))                                # dark beyond the door
    for x in (-1.8,1.8):
        Q+=box(x-0.06,x+0.06,1.6,1.95,-2.99,-2.9,(70,50,34))+box(x-0.08,x+0.08,1.95,2.18,-2.98,-2.86,(255,160,60),emit=True)
    for x in (-3.5,3.0):                                                    # pillars
        Q+=box(x-0.3,x+0.3,0,3.6,-2.9,-2.3,STONE_D)
    return Q
ROOM=room()

# ---------------- heroes (time-lapse) and the knight ----------------
CAPES=[(200,60,50),(60,150,80),(170,120,40),(120,70,170),(60,120,190),(190,90,140),(90,90,90),(200,150,60),(70,160,160)]
def recolor(Q,col):
    for q in Q:
        if q['col'] in (FB.CAPE,FB.PLUME): q['col']=col
        elif q['col']==FB.CAPE_D: q['col']=tuple(int(c*0.75) for c in col)
    return Q
DOOR=(4.2,0.0,-0.5); SPOT=(1.0,0.0,0.15)
def hero(i,t):
    a,b=hero_win(i)
    if not (a<=t<b): return []
    u=(t-a)/(b-a)
    if u<0.4: k=sm(u/0.4); base=(lerp(DOOR[0],SPOT[0],k),0,lerp(DOOR[2],SPOT[2],k)); yaw=-PI/2; walk=t*28; rh=None; gold=False
    elif u<0.62: base=SPOT; yaw=-PI/2; walk=0; rh=(0.2,1.0,0.6) if u<0.52 else (0.25,1.25,0.3); gold=u>=0.52
    else: k=sm((u-0.62)/0.38); base=(lerp(SPOT[0],DOOR[0],k),0,lerp(SPOT[2],DOOR[2],k)); yaw=PI/2; walk=t*28; rh=(0.25,1.2,0.25); gold=True
    Q=recolor(FB.knight(base,yaw,walk=walk,run=0.6 if walk else 0.0,rh=rh,sword='hip'),CAPES[i])
    if gold:
        hx=FB.Ry(yaw)@np.array(rh if rh else (0.27,0.86,0.04)); p=np.array(base)+hx; Q+=box(p[0]-0.07,p[0]+0.07,p[1]-0.05,p[1]+0.05,p[2]-0.07,p[2]+0.07,M.GOLD,emit=True)
    return Q
def knight_state(t):
    if t<T_KN[0] or t>=T_LEAVE[1]: return None
    d=dict(walk=0.0,run=0.0,lean=0.0,sit=0.0,rh=None,lh=None,head=0.0,sword='hip'); yaw=-PI/2
    if t<T_KN[1]: k=sm(seg01(t,*T_KN)); base=(lerp(DOOR[0],SPOT[0],k),0,lerp(DOOR[2],SPOT[2],k)); d['walk']=t*9
    else:
        base=SPOT
        if T_OPEN[0]<=t<T_OPEN[1]+0.3: d['lh']=(-0.15,1.05,0.62)                   # lifts the lid
        if t>=T_KNEEL[0]: d['sit']=0.45*sm(seg01(t,*T_KNEEL))*(1-sm(seg01(t,*T_RISE)))
        if T_REACH[0]<=t<T_RISE[0]:
            u=sm(seg01(t,T_REACH[0],T_REACH[1])); d['rh']=(lerp(0.27,0.05,u),lerp(0.9,0.7,u),lerp(0.1,0.75,u))
        if t>=T_LEAVE[0]: k=sm(seg01(t,*T_LEAVE)); base=(lerp(SPOT[0],DOOR[0],k),0,lerp(SPOT[2],DOOR[2],k)); yaw=PI/2; d['walk']=t*9
    return dict(base=base,yaw=yaw,**d)
def tspace(base,yaw,lean=0.0,run=0.0,sit=0.0):
    b=np.array(base,float); Rb=FB.Ry(yaw); hip=0.82-0.42*sit
    def T(p):
        p=np.array(p,float); piv=np.array([0,hip,0]); return tuple(b+Rb@(piv+FB.Rx(lean+0.22*run)@(p-piv+np.array([0,hip-0.82,0]))))
    return T
def knight_q(t):
    st=knight_state(t)
    if st is None: return []
    Q=FB.knight(**st)
    if st['rh'] is not None and t<M.T_COIN:
        T=tspace(st['base'],st['yaw'],st['lean'],st['run'],st['sit']); p=T(st['rh']); Q+=box(p[0]-0.06,p[0]+0.06,p[1]-0.1,p[1]-0.08,p[2]-0.06,p[2]+0.06,(255,214,90),emit=True)
    return Q

# ---------------- camera: one take that breathes with the story ----------------
CLOSE=((0.68,1.45,2.2),(0,0.48,0),40)
KEYS=[(0.0,CLOSE),(2.5,((0.6,1.5,2.0),(0,0.48,0),40)),(3.8,((0.6,2.7,6.2),(1.0,0.9,-0.4),50)),(7.4,((0.4,2.6,5.8),(1.0,0.9,-0.4),50)),
      (9.2,((0.25,1.95,1.6),(0,0.35,0),42)),(12.3,((0.2,1.85,1.45),(0,0.35,0),42)),(13.9,((-1.6,2.0,4.0),(0.7,0.8,-0.1),48)),
      (15.9,((-1.4,1.9,3.6),(0.6,0.75,0),46)),(17.0,((2.5,1.7,2.4),(0.35,0.55,0.0),44)),(18.6,((2.4,1.7,2.3),(0.35,0.55,0.0),44)),
      (20.4,((-1.5,1.9,3.8),(0.8,0.8,-0.1),48)),(22.6,((-0.6,1.7,3.0),(0.5,0.7,0),46)),(25.0,CLOSE),(DUR,CLOSE)]
def cam(t):
    for (a,(p0,t0,f0)),(b,(p1,t1,f1)) in zip(KEYS,KEYS[1:]):
        if a<=t<=b:
            g=motion.glide(seg01(t,a,b)); return tuple(lerp(p0[i],p1[i],g) for i in range(3)),tuple(lerp(t0[i],t1[i],g) for i in range(3)),lerp(f0,f1,g)
    return CLOSE
def render3d(t):
    pos,tgt,fov=cam(t); c=Camera.look(pos,tgt)
    L=[((-2.5,3.2,3.0),(255,236,210),1.7),((2.8,2.4,-2.5),(140,170,255),1.1),((-1.8,2.0,-2.6),(255,150,70),1.4),((1.8,2.0,-2.6),(255,150,70),1.4)]
    if t>=M.T_COIN: L.append(((0,0.3,-0.1),(255,200,110),0.6*min(1,(t-M.T_COIN)*2)))
    if M.bite(t)>0.1: L.append(((0,0.5,-0.2),(255,60,40),0.55*M.bite(t)))
    H_=[q for i in range(NH) for q in hero(i,t)]
    img,vi,zb=zrender(M.R,c,[ROOM,M.chest(t),coins_out(t),H_,knight_q(t),M.coin_inside(t),M.motes(t)],L,fov=fov,fog_start=6,fog_end=16,ambient=0.36,shake=M.shake(t),return_z=True)
    a=np.asarray(img).astype(np.float32); yy=np.linspace(0,1,M.IH)[:,None,None]
    bg=np.array([10,14,26])*(1-yy)+np.array([24,30,48])*yy; a=np.where((zb==0)[...,None],bg*np.ones((1,M.IW,1)),a)
    X,Y=np.meshgrid(np.linspace(-1,1,M.IW),np.linspace(-1,1,M.IH)); spot=np.clip(1.3-np.hypot(X*1.0,(Y-0.15)*0.75),0.6,1.0)
    return Image.fromarray(np.clip(a*spot[...,None],0,255).astype(np.uint8))
M.render3d=render3d; M.cam=cam
def heroes_count(t): return int(round(9412*seg01(t,T_HEROES[0],T_HEROES[1])))
M.heroes=heroes_count

def ui(d,t):
    W=M.W; fbox=M.fbox; tag=M.tag; YEL,RED,CYAN,GRY=M.YEL,M.RED,M.CYAN,M.GRY
    if t<2.6 or t>=24.9: fbox(d,[('WHY DO MIMICS',1),('PRETEND TO BE',1),('CHESTS?',1)],150,YEL,px=13)
    if T_HEROES[0]-0.2<=t<T_HEROES[1]+0.3:
        tag(d,'100 YEARS IN 4 SECONDS',CYAN); fbox(d,[('HEROES: '+f'{heroes_count(t):,}',1),('GOLD INSIDE: '+f'{int(round(1000*gold_level(t))):,}',1)],170,YEL,px=10)
    if M.T_DUST[0]+0.2<=t<M.T_BITE-0.7: tag(d,'CUTAWAY',GRY); fbox(d,[('TAKEN: 1,000',1),('GIVEN BACK: 0',1)],170,RED,px=11)
    if M.T_BITE-0.2<=t<M.T_BITE+0.9: fbox(d,[('CHOMP!',2)],180,RED,px=14)
    if T_OPEN[0]<=t<T_REACH[0]: tag(d,'SWORD: NOT DRAWN',CYAN)
    if M.T_COIN-0.1<=t<M.T_CALM[1]-0.2: fbox(d,[('TAKEN: 1,000',1),('GIVEN BACK: '+('1' if t>=M.T_COIN+0.05 else '0'),1)],170,YEL if t>=M.T_COIN+0.05 else RED,px=11)
M.ui=ui

if __name__=='__main__':
    OUT=M.OUT
    if os.environ.get('TEST'):
        ims=[M.frame_full(float(x)) for x in os.environ['TEST'].split(',')]; sh=Image.new('RGB',(len(ims)*M.W//3,M.H//3))
        for i,im in enumerate(ims): sh.paste(im.resize((M.W//3,M.H//3),Image.LANCZOS),(i*M.W//3,0))
        sh.save(os.path.join(ROOT,'test.png')); sys.exit()
    if os.environ.get('PART')=='audio':
        # extra footsteps for the heroes and the knight on top of the v1 sound design
        print(M.build_audio(os.path.join(OUT,'one_take_mimic_v2.wav'))); sys.exit()
    if os.environ.get('PART'):
        import subprocess
        a,b=map(int,os.environ['PART'].split(':'))
        p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{M.W}x{M.H}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'mm2_{a:05d}.mp4')],stdin=subprocess.PIPE)
        for f in range(a,min(b,N)): p.stdin.write(np.asarray(M.frame_full(f/FPS)).tobytes())
        p.stdin.close(); p.wait(); print('part done',a,b)
