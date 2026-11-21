"""WHY DO ENEMIES ATTACK ONE AT A TIME? (Insert Disc 2, 14-day test day 1, 02:00 slot) ~29 s PS1 comedy, 9:16, nightkit.
Brief: briefs/enemies_queue.md. The goblins take a number; #47 waited three hours, the hero saved and quit right when he stepped up;
the hero came back the next morning just for him; #47 lost in one hit and framed the ticket.
Reuses: locked knight (examples/final_boss.py), locked goblin + hallway of chests (examples/loot_restocker.py; colour / scale variants only).
NEW: ticket machine, NOW SERVING sign (2D number overlay), paper ticket, club, picture frame, defeat puff.
HUD: WAIT timer, pause menu (CONTINUE / SAVE AND QUIT; the font has no '&'), PAUSED.
Voice: python tools/tts/eq.py src ; <chatterbox python> tools/tts/vc.py eq ; python tools/tts/eq.py build vc  -> $TTS_DIR/eq/
Run: TEST=1,5,9 python examples/enemies_queue.py -> test.png | PART=a:b | PART=audio | tools/render_parts.py --prefix eq --audio enemies_queue.wav"""
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
import loot_restocker as LR

OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6; F=1.0/FPS
PI=math.pi; sm=motion.smooth
def seg01(t,a,b): return max(0.0,min(1.0,(t-a)/(b-a)))
def lerp(a,b,u): return a+(b-a)*u
def lerp3(a,b,u): return tuple(a[i]+(b[i]-a[i])*u for i in range(3))
box=FB.box; xform=FB.xform
WHT=(242,238,226); YEL=(255,210,60); RED=(240,50,40); GRN=(80,220,90); GRAY=(150,150,160); GOLD=(236,190,60); BLU=(110,170,255)

# ======================= voice timings (tools/tts/eq.py) =======================
SCR=json.load(open(os.path.join(TTS_DIR,'eq','script.json')))
GAP=0.3; EXTRA={'1':0.2,'4':0.3,'5':0.5,'6':0.4,'7':0.2,'8':0.45}
def _lines():
    t=0.12; out=[]
    for k in [str(i) for i in range(1,10)]: out.append((k,round(t,3))); t+=SCR['dur'][k]+GAP+EXTRA.get(k,0.0)
    return out,t-GAP
LINES,_vend=_lines(); T0=dict(LINES)
DUR=round(T0['9']+SCR['dur']['9']+0.55,2); N=int(round(DUR*FPS))
def ws(k,i): return T0[k]+SCR['sent'][k][i][0]
def we(k,i): return T0[k]+SCR['sent'][k][i][1]
LEAD=2*F

# ======================= story events =======================
HITS={44:ws('1',0)+1.55-LEAD, 45:ws('4',0)+0.85-LEAD, 46:ws('4',1)+0.85-LEAD, 47:ws('8',0)+1.45-LEAD}
STEP={45:HITS[44]+0.75, 46:HITS[45]+0.6, 47:T0['5']+0.05}             # the next number steps up to the front
T_CLUB=ws('5',0)+0.75                                                 # #47 raises his club
T_MENU=ws('5',1)+0.25; T_QUIT=ws('5',1)+1.1                           # pause menu opens, SAVE AND QUIT is clicked
T_GONE=(T_QUIT+0.05,T_QUIT+0.45)                                      # the knight flickers out
T_DARK=(ws('6',0)+0.55,ws('6',0)+1.0)
T_LIGHT=(T0['7']+0.1,T0['7']+0.7); T_CONT=(T0['7']-0.25,T0['7']+0.55)  # CONTINUE menu, light returns
T_BACK=(ws('7',0)+1.15,ws('7',0)+1.5)                                 # the knight flickers back ("back")
T_NOD=ws('7',1)+0.35
T_FRAME=T0['9']-0.1
FS=(0.6,0.0,7.25); KN_P=(0.0,0.0,6.55); KN_YAW=math.atan2(FS[0]-KN_P[0],FS[2]-KN_P[2]); QX=0.6; FRONT_YAW=PI+KN_YAW
def slot_z(k): return FS[2] if k<=0 else FS[2]+0.2+1.1*k
NUMS=list(range(44,60))
CUTS=[0.0,T0['2']-0.06,T0['3']-0.06,T0['4']-0.06,T0['5']-0.06,T0['6']-0.06,T0['7']-0.25,T0['9']-0.12,DUR]

# ======================= LOCKED ASSET: goblin variants (colour / scale only) + NEW props =======================
VAR=[{},{LR.SKIN:(120,182,84),LR.SKIN_D:(90,140,62)},{LR.SKIN:(88,150,96),LR.SKIN_D:(64,116,72),LR.TUNIC:(96,84,120),LR.TUNIC_D:(70,60,92)},
     {LR.SKIN:(136,170,70),LR.SKIN_D:(104,132,52),LR.TUNIC:(128,64,48),LR.TUNIC_D:(96,46,34)}]
G47={LR.TUNIC:(70,92,150),LR.TUNIC_D:(50,68,112)}
def gscale(n): return 0.86 if n==47 else (1.0+0.06*math.sin(n*1.7))
PAPER=(236,232,214); CLUB=(110,70,36); CLUB_D=(82,52,28)
def gpt(st,p):
    """goblin-local point -> world (same transform as LR.goblin incl. lean, hop and the variant scale)"""
    b=np.array(st['base'],float); piv=np.array([0,0.34,0]); q=piv+FB.Rx(st.get('lean',0.0))@(np.array(p,float)-piv)
    w=b+np.array([0,st.get('hop',0.0),0])+FB.Ry(st['yaw'])@q; s=gscale(st['n']); return b+(w-b)*s
def fall_xf(Q,base,yaw,a):
    if a<=0: return Q
    Rb=FB.Ry(yaw); Rf=Rb@FB.Rx(-1.45*a)@Rb.T; piv=np.array(base,float)+Rb@np.array([0,0,-0.12])
    Q=xform(Q,lambda p:tuple(piv+Rf@(np.array(p,float)-piv)))
    ymin=min(v[1] for q in Q for v in q['p'])
    if ymin<0.005: Q=xform(Q,lambda p:(p[0],p[1]-ymin+0.005,p[2]))
    return Q
def club(st):
    if st.get('rh') is None: return []
    hp=gpt(st,st['rh']); up=st.get('club_up',0.0)
    d=np.array([0.0,lerp(-0.35,0.75,up),lerp(0.75,-0.25,up)]); d=FB.Ry(st['yaw'])@d; d/=np.linalg.norm(d)
    return FB.seg(hp-d*0.05,hp+d*0.22,0.05,CLUB_D)+FB.seg(hp+d*0.2,hp+d*0.5,0.1,CLUB)
def ticket_quad(st):
    if st.get('lh') is None or not st.get('ticket'): return []
    c=gpt(st,np.array(st['lh'])+np.array([0,0.09,0.03])); Rb=FB.Ry(st['yaw']); r=Rb@np.array([0.1,0,0]); u=np.array([0,0.13,0])
    pts=[c-r-u,c+r-u,c+r+u,c-r+u]
    return [quad([tuple(p) for p in pts],PAPER,True),quad([tuple(p) for p in pts[::-1]],PAPER,True)]
def gmodel(n,base,yaw,walk=0.0,lean=0.0,rh=None,lh=None,eyes=1.0,smile=0.0,head=0.0,hop=0.0,fall=0.0,club_up=0.0,ticket=False,has_club=True,**_):
    st=dict(n=n,base=base,yaw=yaw,lean=lean,hop=hop,rh=rh,lh=lh,club_up=club_up,ticket=ticket)
    Q=LR.goblin(base,yaw,walk=walk,lean=lean,rh=rh,lh=lh,eyes=eyes,smile=smile,hat=False,head=head,hop=hop)
    col=G47 if n==47 else VAR[n%4]
    for q in Q:
        c=col.get(tuple(q['col']))
        if c: q['col']=c
    s=gscale(n); b=np.array(base,float)
    if s!=1.0: Q=xform(Q,lambda p:tuple(b+(np.array(p,float)-b)*s))
    Q+=(club(st) if has_club else [])+ticket_quad(st)
    return fall_xf(Q,base,yaw,fall)

# ======================= queue logic =======================
def front(t):
    f=44
    for n in (45,46,47):
        if t>=STEP[n]: f=n
    return f
def gstate(n,t):
    """None when the goblin is gone (defeated + puffed)"""
    if n<47 and n in HITS and t>=HITS[n]+0.75: return None
    if n==47 and t>=HITS[47]+1.6: return None                                   # (the respawned #47 stands by the frame: see g47_frame)
    f=front(t); k=n-f
    # step-up animation: the whole queue moves one slot forward after each STEP
    z=slot_z(k); wk=0.0; yaw=FRONT_YAW if k<=0 else PI
    for m in (45,46,47):
        if STEP[m]<=t<STEP[m]+0.6 and n>=m:
            u=sm(seg01(t,STEP[m],STEP[m]+0.6)); z=lerp(slot_z(n-m+1),slot_z(n-m),u); wk=t*9.0
            if n==m: yaw=lerp(PI,FRONT_YAW,u)
    st=dict(n=n,base=(QX,0.0,z),yaw=yaw,walk=wk,lean=0.0,rh=(0.2,0.32,0.06),lh=None,eyes=1.0,smile=-0.2,head=0.0,hop=0.0,fall=0.0,club_up=0.0)
    if k>0: st['head']=0.12*math.sin(t*0.9+n); st['lean']=0.02*math.sin(t*1.3+n*2)
    if k==0 and n!=47:                                                          # at the front: fighting stance, club up, bouncing
        st.update(rh=(0.22,0.62,0.18),club_up=1.0,lean=0.15,smile=-0.6); st['hop']=0.05*abs(math.sin(t*7))
    if n in HITS and t>=HITS[n]:                                                # knocked back and falls
        a=seg01(t,HITS[n],HITS[n]+0.35); st.update(fall=a*a,hop=0.0,eyes=0.4,club_up=0.0)
        if n==47: st.update(smile=1.0,eyes=1.0)
    if n==47:
        st.update(lh=(-0.16,0.5,0.22),ticket=True,smile=-0.5)
        if T0['3']<=t<T0['4']:                                                  # checks his ticket, sighs
            u=sm(seg01(t,T0['3']+0.2,T0['3']+0.6)); st['lh']=lerp3((-0.16,0.5,0.22),(-0.08,0.66,0.26),u); st['head']=-0.25*u
            st['lean']=0.12*math.sin(PI*seg01(t,ws('3',0)+2.0,ws('3',0)+2.9)); st['eyes']=0.55
        if t>=T_CLUB and t<HITS[47]:
            u=sm(seg01(t,T_CLUB,T_CLUB+0.3)); st.update(rh=lerp3((0.2,0.32,0.06),(0.22,0.66,0.16),u),club_up=u,smile=0.6*u-0.5*(1-u),lean=0.12*u)
            if t>=T_GONE[1]: st.update(smile=-0.3,lean=0.05,club_up=0.6,rh=(0.22,0.5,0.14))                # the hero is gone: club half down
            if t>=T_DARK[0]: st['eyes']=0.75
            if t>=T_BACK[1]: st.update(smile=0.9,eyes=1.0,club_up=1.0,rh=(0.22,0.66,0.16),lean=0.12)
            if T_DARK[1]<=t<T_LIGHT[0]: st['head']=0.15*math.sin(t*1.2)
        if t>=HITS[47]: st.update(smile=1.0,eyes=1.0,club_up=0.0)
    return st
def g47_frame(t):
    """#47 again (respawned) next to the framed ticket, last line"""
    if t<CUTS[7]: return None
    return dict(n=47,base=(-1.3,0.0,8.85),yaw=0.55,walk=0.0,lean=-0.06,rh=(0.24,0.72,0.12),lh=None,eyes=1.0,smile=1.0,head=-0.3,hop=0.03*abs(math.sin(t*5)),fall=0.0,club_up=0.0,has_club=False)
def puffs(t):
    Q=[]
    for n,h in HITS.items():
        a=t-(h+0.6)
        if 0<=a<0.4:
            z=FS[2]+1.1; r=0.15+0.9*a; c=tuple(int(lerp(255,120,a/0.4)) for _ in range(3))
            for k in range(8):
                ang=k*PI/4; p=np.array([QX+r*math.cos(ang),0.25+0.6*a+0.15*math.sin(k*1.3),z+r*math.sin(ang)*0.6]); s=0.12*(1-a/0.4)+0.03
                Q+=box(p[0]-s,p[0]+s,p[1]-s,p[1]+s,p[2]-s,p[2]+s,c,emit=True)
    return Q

# ======================= knight =======================
def kvisible(t):
    if T_GONE[0]<=t<T_GONE[1]: return int((t-T_GONE[0])*24)%2==0
    if T_GONE[1]<=t<T_BACK[0]: return False
    if T_BACK[0]<=t<T_BACK[1]: return int((t-T_BACK[0])*24)%2==1
    return True
def kstate(t):
    d=dict(base=KN_P,yaw=KN_YAW,walk=0.0,lean=0.05+0.02*math.sin(t*2.2),head=0.0,rh=(0.26,1.0,0.42),sword='hand',swing=1.0,eyes=0.0)
    for n,h in HITS.items():
        if h-0.5<=t<h+0.55:
            up=sm(seg01(t,h-0.5,h-0.14)); down=sm(seg01(t,h-0.14,h)); rec=sm(seg01(t,h+0.05,h+0.5))
            if t<h-0.14: d['rh']=lerp3((0.26,1.0,0.42),(0.28,1.6,0.05),up); d['swing']=lerp(1.0,0.15,up)
            elif t<h: d['rh']=lerp3((0.28,1.6,0.05),(0.26,0.95,0.62),down); d['swing']=lerp(0.15,1.85,down); d['lean']+=0.3*down
            else: d['rh']=lerp3((0.26,0.95,0.62),(0.26,1.0,0.42),rec); d['swing']=lerp(1.85,1.0,rec); d['lean']+=0.3*(1-rec)
    if T_MENU<=t<T_GONE[1]: d.update(lean=0.05,rh=(0.26,1.0,0.42),swing=1.0)                         # frozen while the menu is open
    if T_NOD<=t<T_NOD+0.6: d['lean']+=0.22*math.sin(PI*seg01(t,T_NOD,T_NOD+0.6))                    # the nod
    return d

# ======================= set: hallway + NEW ticket machine, sign, frame =======================
MACH_Z=7.6; SIGN_C=(-2.52,2.5,7.6); FRAME_C=(-2.53,1.42,8.5)
def machine(t):
    x0=-2.6; Q=box(x0,x0+0.28,1.1,1.75,MACH_Z-0.22,MACH_Z+0.22,(176,40,36))+box(x0+0.28,x0+0.3,1.2,1.6,MACH_Z-0.17,MACH_Z+0.17,(130,26,24))
    Q+=box(x0+0.29,x0+0.33,1.38,1.42,MACH_Z-0.08,MACH_Z+0.08,(20,16,16))                                       # ticket slot
    Q+=box(x0+0.3,x0+0.42,1.34,1.4,MACH_Z-0.05,MACH_Z+0.05,PAPER,emit=True)                                   # the next ticket sticking out
    lit=any(0<=t-s<0.35 for s in STEP.values())
    Q+=box(x0+0.08,x0+0.2,1.75,1.86,MACH_Z-0.06,MACH_Z+0.06,(255,70,50) if lit or int(t*1.5)%2 else (120,30,26),emit=True)
    # NOW SERVING sign (the number is a 2D overlay)
    cx,cy,cz=SIGN_C; Q+=box(-2.6,-2.47,cy-0.32,cy+0.32,cz-0.62,cz+0.62,(30,26,30))+box(-2.47,-2.45,cy-0.28,cy+0.28,cz-0.58,cz+0.58,(12,10,14),emit=True)
    return Q
def picture_frame(t):
    if t<T_FRAME: return []
    cx,cy,cz=FRAME_C; return box(-2.6,-2.5,cy-0.2,cy+0.2,cz-0.17,cz+0.17,(212,170,60),emit=True)+box(-2.5,-2.48,cy-0.15,cy+0.15,cz-0.12,cz+0.12,PAPER,emit=True)
def dark(t):
    """0 = normal light .. 1 = the paused, dark dungeon"""
    return sm(seg01(t,*T_DARK))*(1-sm(seg01(t,*T_LIGHT)))
def lights(t):
    dk=dark(t); L=[]
    for k,z in enumerate(LR.TORCH_Z[:7]):
        x=(-1 if k%2 else 1)*(LR.HALL_X-0.5); L.append(((x,2.5,z),(255,170,90),(1.1+0.12*math.sin(t*11+k))*lerp(1.0,0.45,dk)))
    L.append(((0,2.0,LR.HALL_Z0+0.5),(255,240,210),1.2*(1-dk)))                                               # daylight from the exit
    L.append(((0.0,3.0,7.0),(200,200,230),0.6*(1-dk)))
    if t>=T_LIGHT[0]: L.append(((0,2.4,3.0),(255,236,200),0.6*sm(seg01(t,*T_LIGHT))))                           # morning
    return L

# ======================= cameras =======================
def creep(t,t0,rate=0.0014): return motion.creep(t,t0,rate,FPS)
def cam_shot(t):
    if t<CUTS[1]:      # A: close on #47's face + ticket, then swings round behind the queue to the fight at the front
        u=motion.glide(seg01(t,0.85,1.95)); tgt=lerp3((0.55,0.74,10.75),(0.35,0.85,7.2),u); p=lerp3((-0.35,0.86,9.8),(-0.95,1.2,11.5),u)
        return dict(cam=motion.dolly(p,tgt,creep(t,0.0,0.0016)),tgt=tgt,fov=lerp(50,60,u))
    if t<CUTS[2]:      # B: from behind the knight's right: the front, machine + NOW SERVING sign, the queue
        tgt=(-0.8,1.4,8.0); return dict(cam=motion.dolly((1.4,1.7,3.8),tgt,creep(t,CUTS[1],0.0014)),tgt=tgt,fov=64)
    if t<CUTS[3]:      # A2: front 3/4 close on #47 checking his ticket
        tgt=(0.6,0.68,9.65); return dict(cam=motion.dolly((-0.75,0.85,8.55),tgt,creep(t,CUTS[2],0.0018)),tgt=tgt,fov=50)
    if t<CUTS[4]:      # B: the two quick hits, sign ticks
        tgt=(-0.8,1.4,8.0); return dict(cam=motion.dolly((1.4,1.7,3.8),tgt,creep(t,CUTS[3],0.0012)),tgt=tgt,fov=64)
    if t<CUTS[5]:      # D: side two-shot: #47 steps up, the pause menu, the knight vanishes
        tgt=(0.4,0.8,7.0); return dict(cam=motion.dolly((-1.25,0.95,8.3),tgt,creep(t,CUTS[4],0.0014)),tgt=tgt,fov=56)
    if t<CUTS[6]:      # C: #47 alone at the front in the dark
        tgt=(0.6,0.62,7.3); return dict(cam=motion.dolly((-0.55,0.72,6.1),tgt,creep(t,CUTS[5],0.0020)),tgt=tgt,fov=54)
    if t<CUTS[7]:      # D: morning, the knight comes back, nods, one hit
        tgt=(0.5,0.78,7.15); return dict(cam=motion.dolly((-1.25,0.95,8.3),tgt,creep(t,CUTS[6],0.0012)),tgt=tgt,fov=62)
    # E: the framed ticket on the wall, #47 proud next to it
    tgt=(-2.0,1.15,8.4); return dict(cam=motion.dolly((-0.1,1.25,9.95),tgt,creep(t,CUTS[7],0.0022)),tgt=tgt,fov=58)
def shake_px(t):
    for h in HITS.values():
        k=motion.kick(t,h,2.0,6,FPS)
        if k: return (0.0,k)
    return (0.0,0.0)

# ======================= render =======================
RND=Renderer(W,H,fog=(14,10,10))
VI=[None]
def render3d(t):
    sh=cam_shot(t); cam=Camera.look(sh['cam'],sh['tgt'])
    Gs=[]
    for n in NUMS:
        st=gstate(n,t)
        if st is None: continue
        if st['base'][2]>sh['cam'][2]+30: continue
        Gs.append(FB.prelit(gmodel(**st),sh['cam'],warm=0.3))
    g2=g47_frame(t)
    if g2: Gs.append(FB.prelit(gmodel(**g2),sh['cam'],warm=0.3))
    K=[FB.prelit(FB.knight(**kstate(t)),sh['cam'])] if kvisible(t) else []
    layers=[LR.HALL,LR.torches(t),machine(t),picture_frame(t),puffs(t)]+Gs+K
    L=lights(t)
    for h in HITS.values():
        if h-F<=t<h+0.3: L=L+[((QX,1.2,FS[2]-0.3),(255,220,170),0.9*math.exp(-(t-h)*9))]
    img,vi,zb=zrender(RND,cam,layers,L,fov=sh['fov'],fog_start=6,fog_end=24,ambient=lerp(0.3,0.12,dark(t)),shake=shake_px(t),return_z=True)
    VI[0]=vi
    return post.ps1(img),vi

# ======================= HUD / UI =======================
def otext(d,s,x,y,col,sc=1):
    o=max(1,sc//2)
    for ox,oy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)): font.text(d,s,x+ox*o,y+oy*o,(0,0,0),sc,None)
    font.text(d,s,x,y,col,sc,None)
def ctext(d,s,y,col,sc=1): otext(d,s,(W-font.width(s,sc))//2,y,col,sc)
def proj(p):
    if VI[0] is None: return None
    q=RND.project(p,VI[0]); return q
def serving(t):
    return 48 if t>=HITS[47]+0.8 else front(t)
def sign_overlay(d,t):
    """NOW SERVING: <n> drawn on the sign (projected centre; scale from the projected sign height)"""
    c=proj(SIGN_C); top=proj((SIGN_C[0],SIGN_C[1]+0.28,SIGN_C[2])); bot=proj((SIGN_C[0],SIGN_C[1]-0.28,SIGN_C[2]))
    if not c or not top or not bot: return
    hpx=abs(bot[1]-top[1])
    if hpx<9: return
    sc=1; n=serving(t); lit=any(0<=t-s<0.35 for s in STEP.values())
    s1='NOW SERVING'; s2=str(n); y=int(c[1]-(7*sc+3+7*sc*2)/2)
    if font.width(s1,sc)>W-8: sc=1
    cl=lambda x,w: int(max(3,min(W-3-w,x)))
    otext(d,s1,cl(c[0]-font.width(s1,sc)/2,font.width(s1,sc)),y,WHT,sc); otext(d,s2,cl(c[0]-font.width(s2,sc*2)/2,font.width(s2,sc*2)),y+7*sc+3,(255,90,70) if not lit or int(t*12)%2 else YEL,sc*2)
def ticket_overlay(d,t):
    """'47' printed on #47's ticket when it is big enough on screen"""
    st=gstate(47,t)
    if st is None or not st.get('ticket') or st.get('fall',0)>0.05: return
    Rb=FB.Ry(st['yaw']); c=proj(tuple(gpt(st,np.array(st['lh'])+np.array([0,0.09,0.03])))); e=proj(tuple(gpt(st,np.array(st['lh'])+np.array([0,0.09,0.03])+Rb.T@np.array([0.1,0,0])*0+np.array([0.1,0,0]))))
    if not c or not e: return
    wpx=abs(c[0]-e[0])*2
    if wpx<9: return
    sc=max(1,int(wpx/13)); s='47'; font.text(d,s,int(c[0]-font.width(s,sc)/2),int(c[1]-7*sc/2),(30,24,20),sc,None)
def frame_overlay(d,t):
    if t<T_FRAME: return
    c=proj(FRAME_C); e=proj((FRAME_C[0],FRAME_C[1]+0.15,FRAME_C[2]))
    if not c or not e: return
    hpx=abs(c[1]-e[1])*2; sc=max(1,int(hpx/9)); s='47'; font.text(d,s,int(c[0]-font.width(s,sc)/2),int(c[1]-7*sc/2),(30,24,20),sc,None)
def menu(d,t,sel,flash):
    """pause menu panel: CONTINUE / SAVE AND QUIT, sel = highlighted row"""
    x0,y0,x1,y1=22,66,W-22,146
    d.rectangle([x0,y0,x1,y1],fill=(10,10,24),outline=(200,200,220))
    ctext(d,'PAUSED',y0+8,WHT,2)
    for i,s in enumerate(('CONTINUE','SAVE AND QUIT')):
        y=y0+36+i*18; on=(i==sel)
        if on:
            col=(255,255,255) if flash and int(t*16)%2==0 else YEL
            d.rectangle([x0+6,y-3,x1-6,y+9],fill=(60,50,20) if not flash else (110,90,30))
        else: col=GRAY
        otext(d,s,(W-font.width(s,1))//2,y,col,1)
        if on: d.polygon([(x0+10,y),(x0+16,y+3),(x0+10,y+6)],fill=YEL)
def hud(d,t):
    sign_overlay(d,t); ticket_overlay(d,t); frame_overlay(d,t)
    if CUTS[2]<=t<CUTS[3]:
        secs=3*3600+2*60+11+int((t-CUTS[2])*3); s_=f'{secs//3600}:{secs%3600//60:02d}:{secs%60:02d}'
        otext(d,'WAIT',8,10,WHT,1); otext(d,s_,8,20,RED,2)
    if T_MENU<=t<T_GONE[0]+0.15:
        menu(d,t,1,t>=T_QUIT-0.12)
    if T_GONE[1]<=t<T_CONT[0] and int(t*2)%2==0: ctext(d,'PAUSED',46,WHT,2)
    if T_DARK[1]<=t<T_CONT[0]:
        secs=11*3600+48*60+int((t-T_DARK[1])*600)%60; otext(d,'WAIT',8,10,WHT,1); otext(d,f'{secs//3600}:{secs%3600//60:02d}:{secs%60:02d}',8,20,RED,2)
    if T_CONT[0]<=t<T_CONT[1]: menu(d,t,0,t>=T_CONT[0]+0.35)
def flash_alpha(t):
    a=0.0
    for h in HITS.values():
        if h-F<=t<h+0.2: a=max(a,0.22*(1.0-seg01(t,h,h+0.2)))
    return a

# ======================= subtitles (1080x1920, 1.25x, sentence timings from the voice) =======================
SUB_F=7.5; HIL={'ONE','NUMBER.','FORTY-SEVEN','THREE','HOURS.','HIT.','SAVED','QUIT.','DARK.','WAITING.','BACK.','HIM.','FRAMED'}
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
                    col=YEL if wd.upper().strip('.,!?:') in HIL or wd.upper() in HIL else WHT; font.check(wd)
                    for k_,ch in enumerate(wd.upper()):
                        for j,row in enumerate(font.FONT[ch]):
                            for i2,bit in enumerate(row):
                                if bit=='1':
                                    X=x+(k_*6+i2)*sc; Y=y0+pad+i*lh+j*sc; bx=[round(X),round(Y),round(X+sc)-1,round(Y+sc)-1]; do.rectangle(bx,fill=col); dm.rectangle(bx,fill=255)
                    x+=font.width(wd,sc)+6*sc
            return ov,m
    return None
def frame_low(t):
    img,vi=render3d(t); fa=flash_alpha(t)
    if fa>0: img=Image.fromarray(np.clip(np.asarray(img).astype(np.float32)*(1-fa)+255*fa,0,255).astype(np.uint8))
    dk=dark(t)
    if dk>0: img=Image.fromarray(np.clip(np.asarray(img).astype(np.float32)*lerp3((1,1,1),(0.62,0.66,0.9),dk),0,255).astype(np.uint8))
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
    if (np.abs(V[:,0])>LR.HALL_X-0.02).any(): out.append(('wall',f'{name} inside a hall wall'))
    return out
def _kn(t): return kstate(t) if kvisible(t) else None
def _g(n): return lambda t: gstate(n,t)
QA=dict(fps=FPS,dur=DUR,W=W,frame=frame,
    chars={'knight':(_kn,FB.knight,'sword','hand'),'g47':(_g(47),gmodel,'none','none'),'g46':(_g(46),gmodel,'none','none'),'g45':(_g(45),gmodel,'none','none')},
    geom=_geom,camera=lambda t: cam_shot(t)['cam'],min_cam_dist=0.4,camera_ok=lambda p: -2.45<p[0]<2.45 and -5.8<p[2]<80 and 0.1<p[1]<3.4,
    allow_jump=[(w,f/FPS) for w in ('knight','g47','g46','g45') for c in CUTS for f in range(int(c*FPS)-2,int(c*FPS)+4)],
    weapon_events=[],
    scenes=[dict(id=f's{i}',t0=CUTS[i],t1=CUTS[i+1],action=a) for i,a in enumerate((
        'hook: over #47 (ticket 47 up), the knight hits #44 at the front (CAM A)',
        'ticket machine + NOW SERVING 45 sign (CAM B)',
        '#47 checks his ticket and sighs, WAIT 3:02:11 (CAM A2)',
        '#45 hit, sign 46, #46 hit, sign 47 (CAM B)',
        '#47 steps up, raises his club, pause menu SAVE AND QUIT, the knight flickers out (CAM D)',
        '#47 alone in the dark, PAUSED, still waiting (CAM C)',
        'CONTINUE, morning light, the knight is back, nods, one hit, #47 falls smiling (CAM D)',
        'the framed ticket 47 on the wall, #47 proud next to it (CAM E)'))],
    texts=lambda: [('hud','NOW SERVING',1),('hud','WAIT',1),('hud','3:02:11',2),('hud','PAUSED',2),('hud','SAVE AND QUIT',1),('hud','CONTINUE',1)])

# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=31); sr=s.sr; n=s.n; t=s.t; BED=np.zeros(n); FX=np.zeros(n)
    def put(buf,x,t0,v=1.0):
        i=int(t0*sr)
        if i>=n or i<0: return
        j=min(n,i+len(x)); buf[i:j]+=(x*v)[:j-i]
    def nb(t0,d,lo,hi,v,seed,shape=2): put(FX,s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v)
    def tone(t0,m,d,v,wave='sq',duty=0.5,dec=3.0,att=0.005,glide=0.0):
        f=440*2**((m-69)/12); tt=s.T(d); fr=f*(1+glide*tt/d); ph=np.cumsum(fr)/sr%1
        x=np.where(ph<duty,1.0,-1.0) if wave=='sq' else (4*np.abs(ph-0.5)-1 if wave=='tri' else np.sin(2*np.pi*ph))
        put(FX,x*np.minimum(1,tt/att)*np.exp(-tt*dec),t0,v)
    def thud(t0,f=55,v=0.3,d=0.6):
        tt=s.T(d); put(FX,np.sin(2*np.pi*f*tt*(1-0.3*tt/d))*np.exp(-tt*8)+s.filt_short(s.noise(d,int(t0*13)),lo=60,hi=700)*np.exp(-tt*12)*0.6,t0,v)
    def bonk(t0,v=0.2,seed=0):
        tt=s.T(0.35); put(FX,np.sin(2*np.pi*190*tt*(1-0.4*tt))*np.exp(-tt*14)+s.filt_short(s.noise(0.35,seed),lo=300,hi=3000)*np.exp(-tt*28)*0.7,t0,v)
    def step(t0,v=0.04,seed=0):
        tt=s.T(0.1); put(FX,s.filt_short(s.noise(0.1,seed),lo=700,hi=4000)*np.exp(-tt*50),t0,v)
    def ding(t0,v=0.06):
        for m,dt in ((88,0.0),(84,0.16)): tone(t0+dt,m,0.7,v,'sin',dec=4)
    # ---- bed: hall drone + torch crackle; the queue murmur (goblin chatter) while the lights are on
    BED+=s.filt(s.rng.normal(0,1,n),lo=30,hi=200)*0.08
    BED+=soft_fire(s,level=0.004,crackles_per_s=3,seed=32)       # soft fire bed + real crackles (no per-sample gate)
    dk=np.array([dark(x) for x in t[::200]]); dk=np.interp(np.arange(n),np.arange(0,n,200),dk)
    rng=np.random.default_rng(7); tt=0.0
    while tt<DUR-0.2:                                                     # goblin murmur: short squeaky syllables, many voices
        d=rng.uniform(0.07,0.16); f0=rng.uniform(260,420); T_=s.T(d); ph=np.cumsum(f0*(1+0.3*np.sin(np.pi*T_/d))*np.ones(len(T_)))/sr%1
        x=s.filt_short(2*ph-1,lo=300,hi=1800)*np.sin(np.pi*T_/d)**2
        i=int(tt*sr); g=1.0-0.85*dk[min(i,n-1)]
        if T_GONE[1]<tt<T_LIGHT[0]: g*=0.25
        put(BED,x,tt,0.022*g*rng.uniform(0.5,1.0)); tt+=rng.uniform(0.04,0.14)
    # ---- hits: whoosh, bonk, thud of the fall, defeat puff
    for nn,h in HITS.items():
        nb(h-0.22,0.2,500,5000,0.06,10+nn); bonk(h,0.22,20+nn); thud(h+0.3,70,0.18,0.4)
        if nn<47: nb(h+0.6,0.35,1500,8000,0.05,30+nn); tone(h+0.6,84,0.25,0.025,'sq',duty=0.25,dec=8,glide=0.5)
    # ---- ticket machine dings on every new number; queue shuffle footsteps
    for nn,s_ in STEP.items():
        ding(s_+0.1,0.06)
        for k in range(4): step(s_+0.05+k*0.14,0.03,40+nn*5+k)
    ding(T0['2']+0.1,0.05)
    # ---- the sigh (soft breath noise), club raise
    nb(ws('3',0)+2.0,0.8,300,2500,0.06,50,1)
    nb(T_CLUB,0.25,400,3000,0.05,51)
    # ---- pause menu: click in, cursor move, SAVE AND QUIT click, everything mutes (a tape-stop on the bed)
    tone(T_MENU,81,0.06,0.07,'sq',dec=30); tone(T_QUIT-0.35,86,0.03,0.05,'sq',dec=50); tone(T_QUIT,93,0.08,0.08,'sq',dec=25); tone(T_QUIT+0.04,98,0.06,0.06,'sq',dec=30)
    tone(T_QUIT+0.05,57,0.5,0.06,'sq',duty=0.3,dec=4,glide=-0.6)
    for k in range(5): tone(T_GONE[0]+k*0.08,90-k*3,0.05,0.03,'sq',dec=30)          # flicker out
    # ---- dark: lights go out (thunk), only torches; a cricket-like tick while he waits
    thud(T_DARK[0],48,0.2,0.5)
    # paused stretch: only the torches crackle + a low pause-menu hum (keeps the gap from going silent)
    pa,pb=T_GONE[1],T_CONT[0]; m=(t>=pa)&(t<pb); env=np.clip(np.minimum(t-pa,pb-t)/0.3,0,1)*m
    FX+=soft_fire(s,level=0.012,crackles_per_s=5,mask=env,seed=33)
    FX+=(np.sin(2*np.pi*98*t)+0.5*np.sin(2*np.pi*147*t))*0.035*env
    k=0
    while T_DARK[1]+0.3+k*0.8<T_CONT[0]: tone(T_DARK[1]+0.3+k*0.8,100,0.04,0.012,'sin',dec=30); k+=1
    # ---- continue: chime, light up, the knight flickers back, nod
    for k_,m in enumerate((76,79,84)): tone(T_CONT[0]+0.35+k_*0.08,m,0.4,0.04,'sq',duty=0.25,dec=4)
    nb(T_LIGHT[0],0.6,800,5000,0.03,60)
    for k in range(5): tone(T_BACK[0]+k*0.07,78+k*3,0.05,0.03,'sq',dec=30)
    # ---- #47 goes down happy: a short cheerful 'defeated' jingle bridges to the last line
    for k_,m in enumerate((79,76,72,74,79)): tone(HITS[47]+0.45+k_*0.17,m,0.3 if k_<4 else 0.7,0.04,'sq',duty=0.25,dec=4 if k_<4 else 2)
    # ---- the frame: a tiny proud trumpet (square + vibrato)
    for k_,(m,d) in enumerate(((72,0.14),(72,0.14),(79,0.6))):
        tt0=T_FRAME+0.25+[0,0.16,0.32][k_]; tone(tt0,m,d+0.2,0.045,'sq',duty=0.3,dec=1.5)
    # ---- voice
    NB=np.zeros(n); wins=[]
    for k_,t0 in LINES:
        a,ar=_sf.read(os.path.join(TTS_DIR,'eq',f'{k_}.wav')); a=a if a.ndim==1 else a.mean(1)
        a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a); put(NB,a,t0); wins.append((t0,t0+len(a)/sr))
    g=duck_envelope(n,sr,wins,-6.0,0.05,0.25); bed=BED*g; fx=FX*(0.55+0.45*g)
    L=bed+fx; R_=np.roll(bed,700)+np.roll(fx,200); pk=max(np.abs(L).max(),np.abs(R_).max()); gv=pk*1.6/np.abs(NB).max()
    s.L=L+NB*gv; s.R=R_+NB*gv; s.reverb(0.14,length=1.4,decay=3.0)
    end=np.clip((DUR-t)/0.04,0,1); s.L*=end; s.R*=end
    return s.save(path,peak=0.9)
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'enemies_queue.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'eq_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.96,vignette=0.25,grain=1.5,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(frame_final(f/FPS),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()








