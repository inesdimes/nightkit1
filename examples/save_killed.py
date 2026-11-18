"""ONE SMALL MISTAKE #01 - "The Save That Killed Him" (Insert Disc 2). ~41.6 s PS1 dark comedy, 9:16, procedural (nightkit).
A knight beats the final boss, saves at 1 HP while poisoned, and the save point keeps respawning him into the same death.
Rule (kept on screen): the save stores HP 1 AND the poison bar at its saved level; every respawn restores exactly that, the bar
drains, he dies. Escape: DELETE SAVE -> 30 h gone, HP 100, BOSS: ALIVE.
Reuses the locked knight (examples/final_boss.py) and the dungeon hall (examples/last10_collapse.py).
NEW: purple save crystal + pedestal, potion, fallen pose (whole-model rotation, knight() untouched), HUD / save panel / pause menu.
Voice: python tools/tts/sk.py -> $TTS_DIR/sk/*.wav (+ sentence timings in script.json; picture events are keyed to them).
Run: TEST=1,12,25 python examples/save_killed.py -> test.png | PART=a:b (frames -> out/sk_a.mp4) | PART=audio"""
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
import last10_collapse as L10
font.FONT['>']=font.FONT.get('>',['10000','01000','00100','00010','00100','01000','10000'])

OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=180,320,6; F=1.0/FPS
PI=math.pi; sm=motion.smooth
def seg01(t,a,b): return max(0.0,min(1.0,(t-a)/(b-a)))
def lerp(a,b,u): return a+(b-a)*u
def lerp3(a,b,u): return tuple(a[i]+(b[i]-a[i])*u for i in range(3))
def hsh(i,s=0): v=math.sin(i*127.1+s*311.7)*43758.5453; return v-math.floor(v)
box=FB.box
WHT=(242,238,226); YEL=(255,210,60); RED=(240,50,40); GRN=(80,220,90); GRAY=(150,150,160); GOLD=(236,190,60)
PUR=(176,84,255); PUR_L=(222,170,255); PUR_D=(96,36,150)

# ======================= voice timings (from tools/tts/sk.py) =======================
SCR=json.load(open(os.path.join(TTS_DIR,'sk','script.json')))
GAP=0.3
def _lines():
    t=0.15; out=[]
    for k in [str(i) for i in range(1,10)]: out.append((k,round(t,3))); t+=SCR['dur'][k]+GAP
    return out,t-GAP
LINES,_vend=_lines(); T0=dict(LINES)
DUR=round(_vend+0.45,2); N=int(round(DUR*FPS))
def ws(k,i): return T0[k]+SCR['sent'][k][i][0]                 # sentence start
def we(k,i): return T0[k]+SCR['sent'][k][i][1]                 # sentence end
LEAD=2*F                                                        # reactions start 2 frames before the word

# ======================= story events =======================
T_SAVE=ws('3',0)+0.9-LEAD                     # "...flashed SAVE complete": the hand lands on the crystal
T_HOOK_END=we('1',0)
D=[ws('3',1)+1.25-LEAD]                       # "he dropped DEAD"
R=[T0['4']-LEAD]                              # "He respawned"
D.append(ws('5',1)-LEAD); R.append(D[-1]+0.6) # "Dead." -> quick respawn before "Reached for a potion"
D.append(ws('5',4)-LEAD); R.append(D[-1]+0.6) # "Dead again."
PAUSE=T0['8']-0.1                             # pause menu (game frozen)
LIFE=2.6
while R[-1]+LIFE<PAUSE-0.3: D.append(R[-1]+LIFE); R.append(D[-1]+0.6)   # the loop goes on while he wonders why
R_LAST=R[-1]
T_RUN=ws('5',0)-LEAD; T_POT=ws('5',2)-LEAD
T_CUR=[PAUSE+0.25,PAUSE+1.05,PAUSE+1.85,ws('8',1)-0.12]        # cursor reaches DELETE SAVE on "Delete save."
T_CONF=we('8',1)-0.05; T_WIPE=T0['9']-LEAD; T_WIPED=we('9',0)
T_NEW=ws('9',1)-LEAD                          # "He survived."  -> NEW GAME, HP 100
T_BOSS=ws('9',2)+0.3-LEAD                     # "The final BOSS got a second chance."
CUTS=[0.0,ws('3',1)-0.05,T0['5']-0.1,PAUSE,DUR]               # 4 cameras, 3 hard cuts
SAVED_LVL=0.14                                # the poison bar at the moment of the save (= what every respawn restores)
def life_index(t):
    """-1 before the first death; k = in life after respawn k-1 ... (None while dead)"""
    if t<D[0]: return -1
    for k in range(len(R)):
        nd=D[k+1] if k+1<len(D) else 1e9
        if R[k]<=t<nd: return k
    return None
def poison_level(t):
    if t>=T_NEW: return None
    tf=min(t,PAUSE) if t>=PAUSE else t                         # frozen while paused
    if tf<D[0]: return lerp(0.30,0.0,seg01(tf,0.0,D[0])) if tf<T_SAVE else lerp(SAVED_LVL,0.0,seg01(tf,T_SAVE,D[0]))
    k=life_index(tf)
    if k is None: return 0.0
    nd=D[k+1] if k+1<len(D) else R_LAST+LIFE
    return lerp(SAVED_LVL,0.0,seg01(tf,R[k],nd))
def deaths(t): return sum(1 for d in D if t>=d+0.3)
def dead_at(t):
    for k,d in enumerate(D):
        if d<=t<R[k]: return k
    return None

# ======================= set: reused hall + NEW crystal, pedestal, potion =======================
CR=np.array([-0.85,1.32,7.7]); CR_H=0.3; CR_R=0.19
P_SAVE=(-0.25,0.0,7.05); Y_C=math.atan2(CR[0]-P_SAVE[0],CR[2]-P_SAVE[2])      # facing the crystal
POT=(0.45,0.0,5.55)
def flash_at(t):
    """crystal flash: the save, and every respawn"""
    v=0.0
    for e in [T_SAVE]+R: v=max(v,math.exp(-max(0.0,t-e)*5.0) if t>=e-F else 0.0)
    return v
def crystal(t):
    yaw=t*0.8; bob=0.03*math.sin(t*2.0); c=CR+np.array([0,bob,0]); Q=[]; n=6
    fl=flash_at(t); glow=0.75+0.25*math.sin(t*3.0)
    top=c+np.array([0,CR_H,0]); bot=c-np.array([0,CR_H,0])
    ring=[c+FB.Ry(yaw+k*2*PI/n)@np.array([CR_R,0,0]) for k in range(n)]
    for k in range(n):
        a,b=ring[k],ring[(k+1)%n]; shade=0.7+0.3*math.cos(yaw+k*2*PI/n+0.6)
        for tip,up in ((top,1),(bot,-1)):
            g=glow*shade*(1.1 if up>0 else 0.85)
            col=tuple(int(min(255,lerp(PUR_D[i],PUR_L[i],g)+fl*(255-PUR_L[i]))) for i in range(3))
            Q.append(quad([tuple(a),tuple(b),tuple(tip)] if up>0 else [tuple(b),tuple(a),tuple(tip)],col,emit=True))
    return Q
STONE=(92,84,90); STONE_L=(118,108,112)
PEDESTAL=box(CR[0]-0.24,CR[0]+0.24,0,0.72,CR[2]-0.24,CR[2]+0.24,STONE)+box(CR[0]-0.3,CR[0]+0.3,0.72,0.82,CR[2]-0.3,CR[2]+0.3,STONE_L)+\
         box(CR[0]-0.31,CR[0]+0.31,0.0,0.1,CR[2]-0.31,CR[2]+0.31,STONE_L)
def rune_ring(t):
    """flat glowing ring on the floor around the save point (the respawn spot)"""
    Q=[]; n=12; r=0.62; fl=flash_at(t); g=0.45+0.15*math.sin(t*2.5)+0.55*fl
    col=tuple(int(min(255,PUR_D[i]+(PUR_L[i]-PUR_D[i])*g)) for i in range(3))
    for k in range(n):
        a0=2*PI*k/n; a1=2*PI*(k+0.6)/n
        p=lambda a,rr:(P_SAVE[0]+rr*math.cos(a),0.012,P_SAVE[2]+rr*math.sin(a))
        Q.append(quad([p(a0,r),p(a1,r),p(a1,r-0.07),p(a0,r-0.07)],col,emit=True))
    return Q
def potion():
    x,y,z=POT
    return box(x-0.07,x+0.07,0,0.15,z-0.07,z+0.07,(214,36,52),emit=False)+box(x-0.03,x+0.03,0.15,0.22,z-0.03,z+0.03,(200,200,210))+\
           box(x-0.035,x+0.035,0.22,0.26,z-0.035,z+0.035,(120,80,46))+box(x-0.05,x+0.05,0.04,0.1,z-0.075,z-0.071,(255,120,130),emit=True)
def tiles():
    Q=[]
    for i in range(-3,3):
        for j in range(-2,18): Q.append(quad([(i,0,j),(i+1,0,j),(i+1,0,j+1),(i,0,j+1)],(96,88,96) if (i+j)%2 else (80,72,82)))
    return Q
TILES=tiles()
def respawn_pillar(t):
    for r in R:
        if r-F<=t<r+0.5:
            u=seg01(t,r,r+0.5); w=0.07*(1-u)+0.02; c=tuple(int(lerp(255,PUR[i],min(1.0,u*2.5))) for i in range(3))
            x,_,z=P_SAVE; return box(x-w,x+w,0,3.6,z-w,z+w,c,emit=True)
    return []

# ======================= knight =======================
def walk_to(t,t0,t1,p0,p1):
    u=seg01(t,t0,t1); return lerp3(p0,p1,u)
STAND_POT=(0.42,0.0,6.15)
RUN_END=(0.3,0.0,4.5)
def kstate(t):
    d=dict(walk=0.0,run=0.0,lean=0.0,head=0.0,sit=0.0,rh=None,lh=None,sword='hip',fall=0.0,fwd=False); base=P_SAVE; yaw=Y_C
    breathe=0.03*math.sin(t*2.2)
    if t>=PAUSE and t<T_NEW: t=PAUSE                                   # paused: frozen
    if t<D[0]:                                                         # hook: reaches for the crystal, saves, stands
        u=sm(seg01(t,-1.2,T_SAVE))
        d['rh']=lerp3((0.22,1.02,0.32),(0.06,1.3,0.62),u) if t<T_SAVE+0.5 else lerp3((0.06,1.3,0.62),(0.27,0.86,0.04),sm(seg01(t,T_SAVE+0.5,T_SAVE+1.0)))
        d['lean']=0.08*u+breathe; d['head']=-0.15
        if t>D[0]-0.7: d['lean']=0.15+0.08*math.sin(t*30)*(1-seg01(t,D[0]-0.7,D[0]))   # poison shudder
    k=dead_at(t)
    if k is not None:                                                  # collapse, then lie until the respawn flash
        pd=kstate(D[k]-F); base=pd['base']; yaw=pd['yaw']; fwd=(k in (1,2) or k%2==0 and k>2)
        u=seg01(t,D[k],D[k]+0.5); d.update(sit=0.35*min(1.0,u*2.0),lean=0.3*u,fall=sm(seg01(t,D[k]+0.12,D[k]+0.55)),fwd=fwd)
        return dict(base=base,yaw=yaw,**d)
    li=life_index(t)
    if li is None or li<0: return dict(base=base,yaw=yaw,**d)
    tr=R[li]
    if li==0:                                                          # first respawn: looks himself over, then runs
        d['lean']=0.12+breathe
        if t>=ws('4',1)-LEAD: d['head']=0.5*math.sin(PI*seg01(t,ws('4',1)-LEAD,ws('4',1)+1.4))
        if t>=T_RUN:
            u=seg01(t,T_RUN,D[1]); yaw=lerp(Y_C,-PI,sm(seg01(t,T_RUN,T_RUN+0.35))); base=lerp3(P_SAVE,RUN_END,min(1.0,max(0.0,(t-T_RUN-0.08)/(D[1]-T_RUN-0.08))))
            d.update(run=1.0,walk=t*14,lean=0.0)
    elif li==1:                                                        # the potion: walks over, crouches, reaches - too slow
        if t<T_POT: d['lean']=0.1
        else:
            u=seg01(t,T_POT,T_POT+0.75); base=lerp3(P_SAVE,STAND_POT,sm(u))
            yaw=lerp(Y_C,-PI,sm(seg01(t,T_POT,T_POT+0.4))); d['walk']=t*9 if u<1 else 0.0
            c=sm(seg01(t,T_POT+0.7,T_POT+1.25)); d.update(sit=0.4*c,lean=0.55*c,rh=lerp3((0.27,0.86,0.04),(0.1,0.6,0.66),c))
    else:                                                              # later loops: stands, stares at the crystal, tries to step away
        d['lean']=0.1+breathe; d['head']=0.35*sm(seg01(t,tr+0.3,tr+0.9))
        if li%2==1:
            u=seg01(t,tr+0.9,tr+1.9); yaw=lerp(Y_C,-PI,sm(seg01(t,tr+0.8,tr+1.15))); base=lerp3(P_SAVE,(0.0,0.0,6.1),sm(u)); d['walk']=t*8 if 0<u<1 else 0.0
    if t>=T_NEW:                                                       # new game: stands up straight ... then the shoulders drop
        d.update(lean=0.0,head=0.0,rh=None,lh=None)
        if t>=T_BOSS+0.25:
            u=sm(seg01(t,T_BOSS+0.25,T_BOSS+0.9)); d.update(lean=0.24*u,sit=0.07*u,head=0.0,
                rh=lerp3((0.27,0.86,0.04),(0.21,0.74,0.13),u),lh=lerp3((-0.27,0.86,0.04),(-0.21,0.74,0.13),u))
    return dict(base=base,yaw=yaw,**d)
def kmodel(**st):
    st=dict(st); fall=st.pop('fall',0.0); fwd=st.pop('fwd',False)
    Q=FB.knight(**st)
    if fall>0:
        a=(1.45 if fwd else -1.45)*fall; Rb=FB.Ry(st['yaw']); Rf=Rb@FB.Rx(a)@Rb.T
        piv=np.array(st['base'],float)+Rb@np.array([0,0,0.15 if fwd else -0.15])
        Q=FB.xform(Q,lambda p:tuple(piv+Rf@(np.array(p,float)-piv)))
        ymin=min(v[1] for q in Q for v in q['p'])
        if ymin<0.005: Q=FB.xform(Q,lambda p:(p[0],p[1]-ymin+0.005,p[2]))          # rests on the floor, never through it
    return Q

# ======================= cameras =======================
def creep(t,t0,rate=0.0014): return motion.creep(t,t0,rate,FPS)
def cam_shot(t):
    if t<CUTS[1]:   # CAM A: medium three-quarter on the knight reaching for the crystal, slow push
        tgt=(-0.5,1.2,7.3); return dict(cam=motion.dolly((-0.15,1.55,9.5),tgt,creep(t,0.0,0.0022)),tgt=tgt,fov=58)
    if t<CUTS[2]:   # CAM B: wider frontal: poison tick, collapse, YOU DIED, respawn
        tgt=(-0.3,0.9,6.7); return dict(cam=motion.dolly((0.75,1.75,10.0),tgt,creep(t,CUTS[1],0.0013)),tgt=tgt,fov=62)
    if t<CUTS[3]:   # CAM C: side-wide down the hall: the loop (runs toward camera, potion, deaths)
        tgt=(0.25,0.85,5.9); return dict(cam=motion.dolly((-0.95,1.65,3.0),tgt,creep(t,CUTS[2],0.0011)),tgt=tgt,fov=62)
    # CAM D: frontal medium, knight in the lower half under the pause menu
    tgt=(-0.5,1.65,7.1); return dict(cam=motion.dolly((0.45,1.7,10.4),tgt,creep(t,CUTS[3],0.0018)),tgt=tgt,fov=56)
def shake_px(t):
    for e in D:
        k=motion.kick(t,e+0.45,1.8,7,FPS)
        if k: return (0.0,k)
    k=motion.kick(t,T_BOSS,1.6,7,FPS)
    return (0.0,k) if k else (0.0,0.0)

# ======================= render =======================
RND=Renderer(W,H,fog=(28,20,30))
def render3d(t):
    sh=cam_shot(t); cam=Camera.look(sh['cam'],sh['tgt']); st=kstate(t)
    tc=min(t,PAUSE) if PAUSE<=t<T_NEW else t                         # paused world: crystal and lights freeze too
    layers=[L10.HALL,TILES,PEDESTAL,crystal(tc),rune_ring(tc),potion(),respawn_pillar(t),kmodel(**st)]
    fl=flash_at(tc)
    Ls=[((0.0,3.5,3.5),(255,160,90),0.75),((0.0,3.5,11.0),(255,160,90),0.6),(tuple(CR),(200,110,255),0.45+0.1*math.sin(tc*3)+1.0*fl)]
    img,vi,zb=zrender(RND,cam,layers,Ls,fov=sh['fov'],fog_start=7,fog_end=26,ambient=0.6,shake=shake_px(t),return_z=True)
    a=np.asarray(img).astype(np.float32)
    a=np.where((zb==0)[...,None],np.array([24,18,26])*np.ones((H,W,1)),a)
    if dead_at(t) is not None and t>D[dead_at(t)]+0.3:                 # dead: drained colour
        g=a.mean(2,keepdims=True); a=(a*0.35+g*0.65)*0.6+np.array([30,0,0])
    if PAUSE<=t<T_NEW:                                                 # paused: dim + desaturate behind the menu
        g=a.mean(2,keepdims=True); a=(a*0.4+g*0.6)*0.5
    return post.ps1(Image.fromarray(np.clip(a,0,255).astype(np.uint8))),vi

# ======================= HUD / UI =======================
def otext(d,s,x,y,col,sc=1):
    o=max(1,sc//2)
    for ox,oy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)): font.text(d,s,x+ox*o,y+oy*o,(0,0,0),sc,None)
    font.text(d,s,x,y,col,sc,None)
def ctext(d,s,y,col,sc=1): otext(d,s,(W-font.width(s,sc))//2,y,col,sc)
def skull(d,x,y,col):
    for j,row in enumerate(['01110','11111','10101','11111','01110','01010']):
        for i,b in enumerate(row):
            if b=='1': d.point((x+i,y+j),fill=col)
def hud(d,t):
    newg=t>=T_NEW
    hp=1 if not newg else int(round(lerp(1,100,sm(seg01(t,T_NEW+0.1,T_NEW+0.6)))))
    otext(d,'HP',5,7,WHT)
    d.rectangle([18,7,96,13],fill=(20,10,12),outline=(0,0,0)); fw=max(1,int(77*hp/100))
    d.rectangle([19,8,19+fw,12],fill=RED if not newg else GRN)
    low=(not newg) and int(t*4)%2==0 and not (PAUSE<=t<T_NEW)
    otext(d,f'{hp}/100',100,7,(RED if low else WHT) if not newg else GRN)
    lv=poison_level(t)
    if lv is not None:
        skull(d,6,18,PUR_L if int(t*3)%2 else PUR)
        d.rectangle([18,19,96,23],fill=(20,10,24),outline=(0,0,0)); d.rectangle([19,20,19+max(0,int(77*lv)),22],fill=PUR)
        otext(d,'POISON',100,18,PUR_L)
    n=deaths(t)
    if n and not newg: s_=f'DEATHS {n:02d}'; otext(d,s_,W-5-font.width(s_),32,RED if t-max([x for x in D if t>=x+0.3])<0.5 else WHT)
    if t<T_HOOK_END+0.2:                                               # the victory the save locked in
        ctext(d,'BOSS DEFEATED',62,GOLD if int(t*5)%2==0 or t>1.0 else YEL,2)
        ctext(d,'PLAYTIME 30:12:45',84,YEL,1)
    if T_SAVE<=t<D[0]-0.2:
        u=seg01(t,T_SAVE,T_SAVE+0.15); y=int(lerp(150,138,u))
        d.rectangle([14,y-5,W-14,y+17],fill=(40,14,64),outline=PUR_L); ctext(d,'SAVE COMPLETE',y,WHT,2)
    if T_SAVE+0.6<=t<D[0]-0.2 and int(t*4)%2==0: ctext(d,'HP 1  POISON SAVED',164,PUR_L,1)
    k=dead_at(t)
    if k is not None and t>=D[k]+0.35:
        d.rectangle([0,128,W,168],fill=(10,0,0)); ctext(d,'YOU DIED',136,RED,3)
    if T0['4']<=t<we('4',1) and ws('4',1)-LEAD<=t and int(t*5)%2==0: ctext(d,'POISON: STILL ACTIVE',54,PUR_L,1)
    if R[0]-F<=t<R[0]+1.6: ctext(d,'RESPAWNED AT SAVE',54 if t<ws('4',1)-LEAD else 66,WHT,1)
    if ws('5',3)-LEAD<=t<D[2] : ctext(d,'TOO SLOW',112,YEL,2)
    if ws('6',0)-LEAD<=t<ws('6',1)+0.6: ctext(d,'WAIT.',64,YEL,3)
    if T0['7']-LEAD<=t<PAUSE: save_panel(d,t)
    if PAUSE<=t<T_NEW: pause_menu(d,t)
    if t>=T_NEW: ctext(d,'NEW GAME',62,WHT,2); ctext(d,'PLAYTIME 00:00:00',82,GRAY,1)
    if t>=T_BOSS:
        ctext(d,'BOSS: ALIVE',104,WHT if t<T_BOSS+0.12 else RED,2)
def save_panel(d,t):
    """what the save file really holds (the replay of the save moment)"""
    t0=T0['7']-LEAD; x0,y0,x1,y1=20,40,160,132
    d.rectangle([x0,y0,x1,y1],fill=(18,10,28),outline=PUR_L); ctext(d,'SAVE FILE 1',y0+5,PUR_L,1)
    rows=[('BOSS DEFEATED',GOLD),('PLAYTIME 30:12:45',WHT),('HP 1/100',RED),('POISON ACTIVE',PUR_L)]
    hl=ws('7',0)+1.45-LEAD                                              # "...saved his POISON too"
    for i,(s_,c) in enumerate(rows):
        if t<t0+0.25+0.3*i: continue
        y=y0+20+i*16
        if i>=2 and t>=hl:
            if int(t*5)%2==0: d.rectangle([x0+6,y-3,x1-6,y+9],fill=(70,14,20) if i==2 else (60,20,90))
            if i==3: otext(d,'>',x0+8,y,YEL)
        ctext(d,s_,y,c,1)
    if t>=hl+0.8: ctext(d,'LOADED EVERY RESPAWN',y1+6,YEL,1)
def pause_menu(d,t):
    x0,y0,x1,y1=26,56,154,168
    d.rectangle([x0,y0,x1,y1],fill=(12,10,16),outline=WHT); ctext(d,'PAUSED',y0+6,WHT,2)
    items=['CONTINUE','LOAD SAVE','OPTIONS','DELETE SAVE']; cur=max([i for i,tc in enumerate(T_CUR) if t>=tc]+[0])
    for i,s_ in enumerate(items):
        y=y0+30+i*16; sel=(i==cur)
        if sel: d.rectangle([x0+6,y-3,x1-6,y+9],fill=(110,20,24) if i==3 else (50,50,60))
        if sel: otext(d,'>',x0+10,y,YEL)
        ctext(d,s_,y,RED if i==3 and not sel else WHT,1)
    if t>=T_CONF:                                                       # confirmation, then the wipe
        d.rectangle([14,174,W-14,232],fill=(30,6,8),outline=RED)
        if t<T_WIPE: ctext(d,'DELETE SAVE?',182,WHT,2); ctext(d,'> YES      NO',206,YEL,1); ctext(d,'30 HOURS WILL BE LOST',218,GRAY,1)
        else:
            u=sm(seg01(t,T_WIPE,T_WIPED)); sec=int((30*3600+12*60+45)*(1-u))
            ctext(d,'DELETING...',180,RED,1); ctext(d,f'{sec//3600:02d}:{sec//60%60:02d}:{sec%60:02d}',194,WHT,2)
            d.rectangle([22,216,W-22,222],outline=GRAY); d.rectangle([23,217,23+int((W-46)*(1-u)),221],fill=GOLD)
def flash_alpha(t):
    a=0.0
    for e in R+[T_NEW]:
        if e-F<=t<e+0.35: a=max(a,1.0-seg01(t,e,e+0.35))
    if T_SAVE<=t<T_SAVE+0.2: a=max(a,0.45*(1-seg01(t,T_SAVE,T_SAVE+0.2)))
    return a

# ======================= subtitles (1080x1920, 1.25x, sentence timings from the voice) =======================
SUB_F=7.5; HIL={'SAVE','COMPLETE','DEAD','POISON','DELETE','THIRTY','HOURS','BOSS','SECOND','CHANCE','ONE','RESTART'}
def _rows(text,n=20):
    out=[]; c=[]
    for w_ in text.split():
        if len(' '.join(c+[w_]))>n and c: out.append(c); c=[w_]
        else: c.append(w_)
    return out+[c]
def _subs():
    res=[]
    for k,t0 in LINES:
        shown=[s.strip() for s in re.split(r'(?<=[.!?])\s+',SCR['text'][k]) if s.strip()]
        for i,(a,b,_) in enumerate(SCR['sent'][k]):
            nxt=SCR['sent'][k][i+1][0] if i+1<len(SCR['sent'][k]) else b+0.25
            res.append((t0+a-0.03,t0+nxt-0.02,_rows(shown[i]),k))
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
    shp.resize((shp.width*2,640),Image.NEAREST).save('test.png'); sys.exit()

# ======================= QA manifest =======================
def _geom(t,name,st,V):
    out=[]
    if V[:,1].min()<-0.05: out.append(('floor',f'{name} under the floor'))
    if (np.abs(V[:,0])>L10.HX-0.05).any(): out.append(('wall',f'{name} inside a hall wall'))
    return out
QA=dict(fps=FPS,dur=DUR,W=W,frame=frame,chars={'knight':(kstate,kmodel,'sword','none')},geom=_geom,camera=lambda t: cam_shot(t)['cam'],min_cam_dist=0.4,
    camera_ok=lambda p: -L10.HX<p[0]<L10.HX and -2.0<p[2]<18 and 0.1<p[1]<5,
    allow_jump=[('knight',f/FPS) for c in CUTS+R for f in range(int(c*FPS)-2,int(c*FPS)+4)],weapon_events=[],
    allow_teleport=[('knight',r) for r in R],   # respawn at the save point, hidden by the white flash (brief MUST)
    scenes=[dict(id=f's{i}',t0=CUTS[i],t1=CUTS[i+1],action=a) for i,a in enumerate((
        'hook: BOSS DEFEATED, HP 1 + poison, reaches the crystal, SAVE COMPLETE (CAM A)',
        'poison empties, collapse, YOU DIED, white flash respawn: HP 1, poison still there (CAM B)',
        'the loop: runs-dies, potion too slow-dies, WAIT, save file shows HP 1 + POISON (CAM C)',
        'pause menu: DELETE SAVE, 30 h wiped, NEW GAME HP 100, BOSS: ALIVE, shoulders drop (CAM D)'))],
    texts=lambda: [('hud','BOSS DEFEATED',2),('hud','SAVE COMPLETE',2),('hud','YOU DIED',3),('hud','DELETE SAVE?',2),('hud','BOSS: ALIVE',2),
                   ('hud','POISON: STILL ACTIVE',1),('hud','LOADED EVERY RESPAWN',1),('hud','30 HOURS WILL BE LOST',1),('hud','PLAYTIME 30:12:45',1),('hud','00:00:00',2)])

# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=7); sr=s.sr; n=s.n; t=s.t; BED=np.zeros(n); FX=np.zeros(n)
    def put(buf,x,t0,v=1.0):
        i=int(t0*sr)
        if i>=n: return
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
    # ---- bed: low dungeon drone + torch crackle (frozen-thin while paused, warmer after the new game)
    BED+=s.filt(s.rng.normal(0,1,n),lo=30,hi=200)*0.10
    BED+=(np.sin(2*np.pi*55*t)+0.6*np.sin(2*np.pi*82.4*t+0.5))*0.025*(0.8+0.2*np.sin(2*np.pi*0.3*t))
    cr=s.filt(s.rng.normal(0,1,n),lo=1500,hi=7000)*(s.rng.random(n)<0.002)*0.6; BED+=cr*0.25
    pz=((t>=PAUSE)&(t<T_NEW)).astype(float); BED*=1-0.65*pz
    # ---- 0.0 victory chime, abruptly cut short by the poison sting
    V=np.zeros(n)
    for k,m in enumerate((72,76,79,84,88)): tone(k*0.09,m,0.6,0.06,'sq',dec=3,buf=V)
    V*=(t<0.5); FX+=V; tone(0.5,40,0.5,0.12,'sq',duty=0.3,dec=7); nb(0.5,0.25,200,1200,0.06,3)
    # ---- poison: slow heartbeat + bubble ticks while alive (faster near the end of each life), frozen at pause
    for tb in np.arange(0.9,PAUSE,0.05):
        lv=poison_level(tb)
        if lv is None or dead_at(tb) is not None: continue
        per=0.55 if lv<0.05 else 0.85
        if abs((tb/per)%1)<0.06: thud(tb,48,0.07,0.25); thud(tb+0.16,44,0.05,0.22)
    for k in range(int(PAUSE*2.2)):
        tb=0.7+k/2.2+0.12*hsh(k)
        if tb<PAUSE and dead_at(tb) is None: tone(tb,60+int(12*hsh(k,2)),0.06,0.012,'sin',dec=40,glide=0.8)
    # ---- the save
    for k,m in enumerate((79,84,88,91)): tone(T_SAVE+k*0.07,m,1.2,0.05,'sin',dec=2.5)
    nb(T_SAVE,0.7,3000,9000,0.03,11,1)
    # ---- deaths: poison tick, collapse thud + armour, YOU DIED gong
    for k,d in enumerate(D):
        tone(d-0.04,52,0.18,0.08,'sq',duty=0.25,dec=10); nb(d-0.04,0.2,180,900,0.05,20+k)
        thud(d+0.42,40,0.35,0.6); clank(d+0.45,0.10,30+k)
        put(FX,(np.sin(2*np.pi*41.2*s.T(1.6))+0.5*np.sin(2*np.pi*82.4*s.T(1.6)))*np.exp(-s.T(1.6)*2.2),d+0.55,0.10)
    # ---- respawns: rising whoosh + short digital glitch
    for k,r in enumerate(R):
        d_=0.4; tt=s.T(d_); x=s.filt_short(s.noise(d_,50+k),lo=400,hi=5000)*np.sin(np.pi*tt/d_)**2; put(FX,x,r-0.25,0.06)
        tone(r-0.05,72,0.25,0.03,'sin',dec=6,glide=1.0)
        for g in range(3):
            q=s.noise(0.03,70+k*3+g); q=np.round(q*2)/2; put(FX,q,r+0.03+g*0.05,0.018)
    # ---- footsteps
    for k in range(6): step(T_RUN+0.12+k*0.16,0.06,100+k)
    for k in range(3): step(T_POT+0.1+k*0.25,0.045,120+k)
    for li in range(2,len(R)):
        if li%2==1:
            for k in range(3): step(R[li]+1.0+k*0.32,0.04,140+li*5+k)
    # ---- save file panel: low diagnostic pulse + row blips
    t7=T0['7']-LEAD
    for k in range(4): tone(t7+0.25+0.3*k,84,0.06,0.03,'sq',dec=30)
    for k in range(7): put(FX,np.sin(2*np.pi*110*s.T(0.35))*np.sin(np.pi*s.T(0.35)/0.35),t7+0.1+0.55*k,0.05)
    tone(ws('7',0)+1.45-LEAD,64,0.3,0.04,'sq',dec=6); tone(ws('7',0)+1.6-LEAD,61,0.4,0.04,'sq',dec=5)
    # ---- pause menu
    tone(PAUSE,84,0.08,0.05,'sq',dec=20); tone(PAUSE+0.08,72,0.15,0.05,'sq',dec=12)
    for tc in T_CUR[1:]: tone(tc,88,0.04,0.035,'sq',dec=40)
    tone(T_CUR[-1]+0.02,57,0.3,0.05,'sq',dec=8)
    tone(T_CONF,76,0.1,0.04,'sq',dec=15); tone(T_CONF+0.1,76,0.1,0.04,'sq',dec=15)
    dw=T_WIPED-T_WIPE; tone(T_WIPE,96,dw,0.035,'sq',dec=0.6,glide=-0.93); nb(T_WIPE,dw,800,6000,0.03,200,1)
    for k in range(int(dw*18)): tone(T_WIPE+k/18,100,0.02,0.015,'sq',dec=80)
    # ---- new game, boss alive
    for k,m in enumerate((72,76,79,84)): tone(T_NEW+k*0.08,m,0.9,0.05,'sq',duty=0.25,dec=3)
    for m in (36,43,48): tone(T_BOSS,m,1.6,0.05,'sq',duty=0.4,dec=1.6)
    thud(T_BOSS,36,0.3,0.9)
    tone(T_BOSS+0.9,64,0.5,0.025,'sin',dec=3); tone(T_BOSS+1.15,60,0.8,0.025,'sin',dec=2)                     # the deflated sigh
    # ---- voice
    NB=np.zeros(n); wins=[]
    for k_,t0 in LINES:
        a,ar=_sf.read(os.path.join(TTS_DIR,'sk',f'{k_}.wav')); a=a if a.ndim==1 else a.mean(1)
        a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a); put(NB,a,t0); wins.append((t0,t0+len(a)/sr))
    g=duck_envelope(n,sr,wins,-6.0,0.05,0.25); bed=BED*g; fx=FX*(0.55+0.45*g)
    L=bed+fx; R_=np.roll(bed,700)+np.roll(fx,200); pk=max(np.abs(L).max(),np.abs(R_).max()); gv=pk*1.6/np.abs(NB).max()
    s.L=L+NB*gv; s.R=R_+NB*gv; s.reverb(0.14,length=1.4,decay=3.0)
    end=np.clip((DUR-t)/0.04,0,1); s.L*=end; s.R*=end                                                         # hard end
    return s.save(path,peak=0.9)
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'save_killed.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'sk_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.96,vignette=0.25,grain=1.5,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(frame_final(f/FPS),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
