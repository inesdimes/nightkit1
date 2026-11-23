"""WHY DO HEROES SMASH EVERY POT? (Insert Disc 2, 14-day test day 3, 02:00 slot, Tone 2.0 + Format 3.0) ~30 s final (build x1.2), PS1 drama, 9:16.
Brief: briefs/pots.md. An old woman sets out a new clay pot every morning; every hero smashes it for the coin she hides inside. Forty years, nobody says thank you:
her son left to be a hero and never wrote, so she hopes someone does the same for him. One knight puts the coin back and sits down; she makes tea.
Format 3.0: constant camera (look.Path), the woman in the middle third, group framing (look.follow_group), character cards, several voices (tools/tts/pt.py + multi.py),
270x480 + depth outline (nightkit/look.py), finished video x1.2 afterwards. Reuses the guide helpers of examples/tutorial_guy.py (hand_world, Subtitles, sparkle).
Run: TEST=1,5,9 python examples/pots.py -> test_pt.png | PART=a:b | PART=audio | tools/render_parts.py --prefix pt --audio pots.wav"""
import os, sys, math, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','tts'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, quad, tiled_plane
from nightkit import motion, post, font, look
from nightkit.zraster import zrender
from nightkit.audio import Sound, duck_envelope
import final_boss as FB
import npc_well as NW

OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=270,480,4
PI=math.pi; sm=motion.smooth
def seg01(t,a,b): return max(0.0,min(1.0,(t-a)/(b-a))) if b>a else (1.0 if t>=b else 0.0)
def lerp(a,b,u): return a+(b-a)*u
def lerp3(a,b,u): return tuple(a[i]+(b[i]-a[i])*u for i in range(3))
def hsh(i,s=0): v=math.sin(i*127.1+s*311.7)*43758.5453; return v-math.floor(v)
box=FB.box; xform=FB.xform; seg=FB.seg
GOLD=(255,204,64)
COL={'N':(242,238,226),'W':(255,204,64),'H1':(255,120,100),'H2':(100,190,255),'H3':(120,230,130),'K':(176,206,255)}   # subtitle colour = speaker

# ======================= voice timings (tools/tts/pt.py) =======================
SCR=json.load(open(os.path.join(TTS_DIR,'pt','script.json')))
KEYS=['1','2','3a','3b','3c','4','5','6','7','8','9','10']
GAP=0.3; EXTRA={'1':0.7,'2':0.5,'3a':0.35,'3b':0.45,'3c':0.9,'4':0.5,'5':0.7,'6':0.6,'7':0.7,'8':2.0,'9':1.4,'10':1.6}
def _lines():
    t=0.12; out=[]
    for k in KEYS: out.append((k,round(t,3))); t+=SCR['dur'][k]+GAP+EXTRA.get(k,0.0)
    return out
LINES=_lines(); T0=dict(LINES)
DUR=round(T0['10']+SCR['dur']['10']+1.5,2); N=int(round(DUR*FPS))
def ws(k,i): return T0[k]+SCR['sent'][k][i][0]

# ======================= layout / events =======================
PD=(0.2,0.0,4.5); W0=(1.0,0.0,4.75); TBL=(1.5,0.0,4.0); STOOL=(2.15,0.0,4.0); DOOR_X=0.2; HSTAND=5.2     # pedestal, woman's spot, tea table, knight's stool, heroes' stand line
Y_FACE=PI+0.45                                                              # woman: faces the camera, a little towards the pedestal
TS=[0.28,T0['3a']+0.02,T0['3b']+0.02,T0['3c']+0.02]                          # smash times of heroes 0..3 (hero 0 is the frame-0 hero)
HCAPE=[(130,92,62),(150,150,162),(60,110,220),(70,150,84)]
LEAVE_DT=[0.5,0.5,1.5,0.4]                                                   # hero 2 stays to shake the shards (greedy)
T_FB=(T0['5']-0.12,T0['6']-0.05)                                             # flashback window (hard cut in and out)
T_KIN=T0['7']-0.2; T_KARR=T0['7']+1.6                                        # knight walks in, stops at the pedestal
T_LID=(T0['8']+0.05,T0['8']+0.65,T0['8']+1.3,T0['8']+1.8)                    # lid up, coin seen, lid down
T_KW=(T0['8']+1.9,T0['9']-0.05); T_SIT=(T0['9']-0.05,T0['9']+0.55)
T_CUP=(T0['9']+0.9,T0['9']+1.5)                                              # she sets the two cups
T_HUD0=T0['9']+0.3                                                           # the counter becomes POTS SMASHED TODAY: 0
def in_fb(t): return T_FB[0]<=t<T_FB[1]
def ang_lerp(a,b,u): return a+((b-a+PI)%(2*PI)-PI)*u
def pulse(t,a,d): return math.exp(-((t-a)/d)**2) if abs(t-a)<4*d else 0.0

# ======================= characters =======================
def woman_acc(young):
    def acc(Hh,T,Wd):
        Q=[] if young else box(-0.1,0.1,1.36,1.5,-0.2,-0.04,(176,174,170),xf=Hh)+box(-0.075,0.075,1.46,1.54,-0.19,-0.07,(176,174,170),xf=Hh)    # grey bun
        Q+=box(-0.3,0.3,0.98,1.12,-0.17,0.17,(84,98,124),xf=T)+box(-0.2,0.2,0.72,1.0,0.12,0.17,(84,98,124),xf=T)                               # shawl
        Q+=box(-0.19,0.19,0.34,0.8,0.14,0.185,(226,214,182),xf=T)                                                                              # apron
        Q+=box(0.12,0.2,1.0,1.08,0.17,0.2,GOLD,xf=T)                                                                                           # brooch (the accent)
        return Q
    return acc
def woman_model(st,cp,young=False,lum=1.2):
    kw={k:st[k] for k in ('lean','head','tilt','rh','lh','blink','walk','gaze') if k in st}
    Q=NW.human(st['base'],st['yaw'],kind='woman',cane=False,hair=((106,70,44) if young else (186,184,180)),coat_col=((104,76,60),(80,58,46)),acc=woman_acc(young),**kw)
    lh=st.get('lh') if st.get('lh') is not None else (-0.26,0.68,0.05); hw=TG_hand(st['base'],st['yaw'],st.get('lean',0.0),lh,hy=0.7)
    Rb=FB.Ry(st['yaw']); a=hw+Rb@np.array([0,0.3,0.0]); b=hw+Rb@np.array([-0.04,-0.78,0.28])                                               # the broom
    Q+=seg(a,b,0.04,(140,104,64))+box(b[0]-0.12,b[0]+0.12,b[1]-0.02,b[1]+0.14,b[2]-0.03,b[2]+0.03,(196,170,96),xf=None)
    return NW.lum_lit(Q,cp,lum,0.15)
def TG_hand(base,yaw,lean,hl,hy=0.7):
    piv=np.array([0,hy,0]); return np.array(base,float)+FB.Ry(yaw)@(piv+FB.Rx(lean)@(np.array(hl,float)-piv))
def boy_model(st,cp,lum=0.95):
    Q=NW.human(st['base'],st['yaw'],kind='boy',cane=False,coat_col=((96,120,150),(70,92,120)),rh=st.get('rh'),walk=st.get('walk',0.0),head=st.get('head',0.0))
    b=np.array(st['base'],float); sc=0.62; xform(Q,lambda p:tuple(b+(np.array(p)-b)*sc))
    hw=b+(TG_hand(st['base'],st['yaw'],0.0,st.get('rh') or (0.26,0.68,0.05),hy=0.62)-b)*sc; Rb=FB.Ry(st['yaw'])
    Q+=seg(hw+Rb@np.array([0,-0.1,0.0]),hw+Rb@np.array([0.0,0.35,0.5]),0.04,(190,150,96))                                                       # wooden sword
    return NW.lum_lit(Q,cp,lum,0.2)
def hero_model(i,st,cp,lum=0.72):
    Q=NW.hero_knight(HCAPE[i],**st); return NW.lum_lit(Q,cp,lum,0.2)

# ======================= pots / props =======================
TERRA=(166,94,66); TERRA_D=(138,76,52)
def pot_model(p,scale=1.0,lid=None,glow=0.0,coin=False,t=0.0):
    """clay pot with a lid. lid = None (on) or (x,y,z) world position of the lid; coin = the coin lies inside (seen while the lid is off)"""
    x,y,z=p; s=scale
    c1=tuple(int(a+(b-a)*glow) for a,b in zip(TERRA,GOLD)); c2=tuple(int(a+(b-a)*glow) for a,b in zip(TERRA_D,GOLD))
    Q=box(x-0.14*s,x+0.14*s,y,y+0.1*s,z-0.14*s,z+0.14*s,c2)+box(x-0.22*s,x+0.22*s,y+0.1*s,y+0.38*s,z-0.22*s,z+0.22*s,c1)+box(x-0.15*s,x+0.15*s,y+0.38*s,y+0.5*s,z-0.15*s,z+0.15*s,c2)+box(x-0.19*s,x+0.19*s,y+0.5*s,y+0.55*s,z-0.19*s,z+0.19*s,c1)
    if glow>0.05: Q+=box(x-0.22*s,x+0.22*s,y+0.2*s,y+0.24*s,z-0.225*s,z+0.225*s,GOLD,emit=True)
    if lid is None: lx,ly,lz=x,y+0.55*s,z
    else: lx,ly,lz=lid
    Q+=box(lx-0.17*s,lx+0.17*s,ly,ly+0.05*s,lz-0.17*s,lz+0.17*s,c2)+box(lx-0.04*s,lx+0.04*s,ly+0.05*s,ly+0.1*s,lz-0.04*s,lz+0.04*s,c1)
    if coin: g=0.8+0.2*math.sin(t*10); Q+=box(x-0.08,x+0.08,y+0.5*s,y+0.53*s,z-0.08,z+0.08,tuple(int(c*g) for c in GOLD),emit=True)
    return Q
def shards(ts,p,seed,t,n=11):
    """ballistic terracotta pieces thrown towards the camera (-z); they lie on the floor afterwards, then sink"""
    Q=[]; tau=t-ts
    if tau<0 or tau>3.6: return Q
    for k in range(n):
        vx=(hsh(k,seed)-0.5)*3.0; vy=2.0+2.4*hsh(k,seed+1); vz=-(1.2+2.6*hsh(k,seed+2)); s=0.03+0.05*hsh(k,seed+3)
        tl=(vy+math.sqrt(vy*vy+2*9.8*0.5))/9.8; ta=min(tau,tl)
        x=p[0]+vx*ta; z=p[2]+vz*ta; y=p[1]+0.5+vy*ta-4.9*ta*ta
        if tau>=tl: x+=vx*0.12*(1-math.exp(-(tau-tl)*8)); z+=vz*0.12*(1-math.exp(-(tau-tl)*8)); y=0.02+s*0.5
        sink=1-sm(seg01(tau,2.6,3.5))
        c=TERRA if k%2 else TERRA_D; ss=s*sink
        if ss>0.004: Q+=box(x-ss,x+ss,max(0.0,y-ss*0.5),max(0.0,y-ss*0.5)+ss,z-ss,z+ss,c)
    return Q
def coin_model(p,t): g=0.75+0.25*math.sin(t*12); return box(p[0]-0.06,p[0]+0.06,p[1],p[1]+0.025,p[2]-0.06,p[2]+0.06,tuple(int(c*g) for c in GOLD),emit=True)
def steam(p,t,k0=0):
    Q=[]
    for k in range(4):
        u=((t*0.5+k*0.25+hsh(k0,k))%1.0); s=0.018+0.02*u; Q+=box(p[0]+0.03*math.sin(t*3+k)-s,p[0]+0.03*math.sin(t*3+k)+s,p[1]+0.1+0.4*u,p[1]+0.1+0.4*u+2*s,p[2]-s,p[2]+s,(236,236,236),emit=True)
    return Q

# ======================= states =======================
def hero_pose(i,t):
    """hero i (0..3): enters through the door, smashes the pot, takes the coin, leaves. None when out of the room."""
    tsi=TS[i]; x=PD[0]; z=HSTAND; yaw=PI; walk=0.0; run=0.0; rh=None; lh=None; lean=0.04; head=0.0; sword='hip'; swing=0.0
    t_arr=tsi-0.3; speed=3.2 if i!=3 else 4.2
    if t<t_arr:
        z=HSTAND+speed*(t_arr-t); walk=z*4.5; run=0.7
        if z>9.2: return None
    up=sm(seg01(t,tsi-0.62,tsi-0.3)); hit=sm(seg01(t,tsi-0.3,tsi+0.04))
    if up>0 or hit>0:
        sword='hand' if t<tsi+0.4 else 'hip'; rh=lerp3((0.27,0.86,0.04),(0.25,1.45,0.15),up) if hit<=0 else lerp3((0.25,1.45,0.15),(0.25,0.98,0.6),hit); swing=lerp(0.25,2.05,hit); lean=0.04+0.12*hit
    if t>=tsi+0.4: sword='hip'; rh=None; lean=0.04
    if t>=tsi+0.08 and t<tsi+0.5: lh=lerp3((-0.27,0.86,0.04),(-0.1,1.2,0.5),sm(seg01(t,tsi+0.08,tsi+0.38)))                    # catches the coin
    if i==2 and tsi+0.45<=t<tsi+1.35: lean=0.04+0.5*math.sin(PI*seg01(t,tsi+0.45,tsi+1.35))**0.8; head=0.0                       # bends to shake the shards
    tl=tsi+LEAVE_DT[i]
    if t>=tl:
        u=sm(seg01(t,tl,tl+0.4)); yaw=lerp(PI,0.0,u)
        if t>=tl+0.35: z=HSTAND+3.4*(t-tl-0.35); walk=z*4.5; run=0.7
        if z>9.4: return None
    return dict(base=(x,0.0,z),yaw=yaw,walk=walk,run=run,sword=sword,lean=lean,head=head,rh=rh,lh=lh,swing=swing)
def anon_pose(t):
    """a hero walking away down the lane (line 6): back to the camera, coin glint"""
    a=T0['6']-0.05
    if not (a<=t<T0['6']+SCR['dur']['6']+0.6): return None
    z=7.4+1.7*(t-a); return dict(base=(DOOR_X+0.1*math.sin(t*0.8),0.0,z),yaw=0.0,walk=z*4.5,run=0.0,sword='hip',lean=0.04)
def kn_pose(t):
    if t<T_KIN: return None
    base=[PD[0],0.0,HSTAND]; yaw=PI; walk=0.0; rh=None; head=0.0; sit=0.0; lean=0.02; kst=5.05
    if t<T_KARR: z=lerp(8.6,kst,seg01(t,T_KIN,T_KARR)); base=[PD[0],0.0,z]; walk=z*4.5
    else:
        base=[PD[0],0.0,kst]; head=-0.35*sm(seg01(t,T_KARR,T_KARR+0.4))*(1-sm(seg01(t,T0['8']-0.1,T0['8']+0.2)))
        if T_LID[0]<=t<T_LID[3]+0.3:
            u=sm(seg01(t,T_LID[0],T_LID[1]))*(1-sm(seg01(t,T_LID[2],T_LID[3]))); rh=lerp3((0.27,0.86,0.04),(0.08,1.02,0.72),u)
        if t>=T_KW[0]:
            way=[(PD[0],5.05),(1.75,5.62),(2.05,5.1),(2.15,4.15)]; u=seg01(t,*T_KW); lens=[math.dist(way[i],way[i+1]) for i in range(3)]; tot=sum(lens)
            def P(uu):
                d=min(max(uu,0.0),1.0)*tot; k=0
                while k<2 and d>lens[k]: d-=lens[k]; k+=1
                f=d/lens[k]; return np.array([lerp(way[k][0],way[k+1][0],f),lerp(way[k][1],way[k+1][1],f)])
            px,pz=P(u); base=[float(px),0.0,float(pz)]
            dl=0.14; hd=P(u+dl)-P(u-dl); h=math.atan2(hd[0],hd[1])                                         # heading from a look-ahead / look-behind chord: turns smoothly at the corners
            yaw=ang_lerp(PI,h,sm(seg01(u,0.0,0.18))); yaw=ang_lerp(yaw,1.5*PI,sm(seg01(u,0.8,1.0))); walk=t*6.0 if u<0.97 else 0.0
    if t>=T_SIT[0]:
        u=sm(seg01(t,*T_SIT)); sit=u; base=[STOOL[0],0.0,STOOL[2]]; yaw=1.5*PI; walk=0.0
        if u>=1.0: head=0.25*math.sin(t*0.7)*0.3
    return dict(base=tuple(base),yaw=yaw,walk=walk,run=0.0,sword='hip',lean=lean,head=head,rh=rh,sit=sit)
def lid_state(t):
    """(lid world pos or None, coin visible) for the pedestal pot while the knight opens it"""
    if not (T_LID[0]<=t<T_LID[3]): return None,False
    u=sm(seg01(t,T_LID[0],T_LID[1]))*(1-sm(seg01(t,T_LID[2],T_LID[3]))); k=kn_pose(t); b=np.array(k['base']); R=FB.Ry(k['yaw'])
    hand=b+R@np.array([0.08,1.02,0.72]); lid=lerp3((PD[0],0.55,PD[2]),tuple(hand+np.array([0,-0.02,0])),u)
    return lid,u>0.5
def pot_present(t):
    for i,tsi in enumerate(TS):
        if tsi<=t<tsi+0.9: return None
    return 1.0
def pot_scale(t):
    for tsi in TS:
        if tsi+0.9<=t<tsi+1.15: return 0.55+0.45*sm(seg01(t,tsi+0.9,tsi+1.15))
    return 1.0
def wstate(t,young=False):
    base=list(W0); yaw=Y_FACE; d=dict(lean=0.03+0.01*math.sin(t*1.5),head=0.0,tilt=0.0,rh=None,lh=None,blink=0.0,walk=0.0,gaze=0.0)
    d['blink']=1.0 if (t*0.45)%1.0<0.05 else 0.0
    d['head']=0.35*math.sin(t*0.9)*(0.4+0.6*(math.sin(t*0.35)>0.6))                              # glances at the door every few seconds
    if not young:
        d['rh']=(0.28,0.8+0.04*math.sin(t*2.0),0.2)
        for tsi in TS:                                                                           # flinch, then sweep
            f=pulse(t,tsi+0.1,0.22); d['lean']-=0.22*f; d['tilt']+=0.12*f
            if tsi+0.5<=t<tsi+1.3: d['lh']=(-0.3,0.55,0.2+0.25*math.sin(2*PI*(t-tsi-0.5)/0.45))
            d['lean']+=0.04*sm(seg01(t,tsi+1.0,tsi+2.0))
        # she puts a new pot out: both hands towards the pedestal after each smash
        for tsi in TS:
            u=sm(seg01(t,tsi+0.55,tsi+0.8))*(1-sm(seg01(t,tsi+1.05,tsi+1.3)))
            if u>0: tg=NW.loc(tuple(base),yaw,(PD[0],0.82,PD[2])); d['rh']=lerp3(d['rh'],tg,u*0.9); d['lh']=lerp3(d['lh'] or (-0.26,0.68,0.05),(tg[0]-0.12,tg[1],tg[2]),u*0.9)
        # line 4: she presses a coin into a pot and pats it
        u4=sm(seg01(t,T0['4']-0.1,T0['4']+0.5))*(1-sm(seg01(t,T0['4']+2.4,T0['4']+3.0)))
        if u4>0:
            tg=NW.loc(tuple(base),yaw,(PD[0]+0.05,0.8,PD[2])); pat=0.04*math.sin(t*9)*(seg01(t,T0['4']+1.4,T0['4']+1.5))
            d['rh']=lerp3(d['rh'],(tg[0],tg[1]+pat,tg[2]),u4); d['lh']=lerp3(d['lh'] or (-0.26,0.68,0.05),(tg[0]-0.16,tg[1]-0.02,tg[2]),u4); d['lean']+=0.06*u4; d['tilt']+=0.08*u4
        # line 6: she stands in the doorway, watching the lane
        u6=(1.0 if t>=T_FB[1] else 0.0)*(1-sm(seg01(t,T0['7']-0.6,T0['7']+0.6)))
        if u6>0: base=[lerp(W0[0],0.95,u6),0.0,lerp(W0[2],5.45,u6)]; yaw=lerp(Y_FACE,0.0+0.15,u6); d['head']=0.0
        # tea: she sets two cups on the table
        if t>=T_CUP[0]:
            u=sm(seg01(t,T_CUP[0],T_CUP[0]+0.35))*(1-sm(seg01(t,T_CUP[1]-0.2,T_CUP[1]+0.3)))
            tg=NW.loc(tuple(base),yaw,(TBL[0]-0.12,0.8,TBL[2]+0.15)); tg2=NW.loc(tuple(base),yaw,(TBL[0]+0.18,0.8,TBL[2]+0.15))
            d['rh']=lerp3(d['rh'],tg,u); d['lh']=lerp3(d['lh'] or (-0.26,0.68,0.05),tg2,u); d['lean']+=0.1*u
        if t>=T0['9']-0.1:
            tl=NW.loc(tuple(base),yaw,(STOOL[0],1.1,STOOL[2])); d['head']=float(np.clip(math.atan2(tl[0],tl[2])*0.6,-0.8,0.8))*sm(seg01(t,T0['9']-0.1,T0['9']+0.4))
    else:
        d['rh']=(0.28,0.75,0.25); d['head']=0.2*math.sin(t*0.8)
    return dict(base=tuple(base),yaw=yaw,**d)
def boy_state(t):
    a=T_FB[0]; b=T0['6']-0.05
    if not (a<=t<b): return None
    x=DOOR_X; z=lerp(5.2,5.35,seg01(t,a,a+1.4)); yaw=0.0; walk=0.0; rh=None; head=0.0
    rh=(0.28+0.06*math.sin(t*10),0.9+0.14*math.sin(t*10+1),0.3)                                  # swings the wooden sword at the air
    if t>=a+1.5: rh=lerp3(rh,(0.3,1.3,0.1),sm(seg01(t,a+1.5,a+1.8))); head=0.5*sm(seg01(t,a+1.6,a+1.9))       # waves at the door
    if t>=a+2.0: z=5.35+1.5*(t-a-2.0); walk=z*5.0; rh=None; head=0.0
    return dict(base=(x,0.0,z),yaw=yaw,walk=walk,rh=rh,head=head)

# ======================= set =======================
FLOOR_A=(120,84,58); FLOOR_B=(106,72,50); WALL=(84,62,50); WALL_D=(66,48,40); BEAM=(60,42,32); WOODC=(112,78,50)
def room():
    Q=tiled_plane(-3.2,3.2,-0.6,6.0,0.0,0.8,lambda i,j:FLOOR_A if (i+j)%2 else FLOOR_B)
    Q+=box(3.2,3.4,0,2.9,-0.6,6.2,WALL_D)+box(-3.4,-3.2,0,1.0,-0.6,6.2,WALL)+box(-3.4,-3.2,2.3,2.9,-0.6,6.2,WALL)+box(-3.4,-3.2,1.0,2.3,-0.6,1.9,WALL)+box(-3.4,-3.2,1.0,2.3,3.5,6.2,WALL)    # right wall, left wall with the window
    Q+=box(-3.4,3.4,0,2.9,-0.8,-0.6,WALL_D)
    Q+=box(-3.4,-0.4,0,2.9,6.0,6.2,WALL)+box(0.8,3.4,0,2.9,6.0,6.2,WALL)+box(-0.4,0.8,2.1,2.9,6.0,6.2,WALL)               # back wall with the door opening x -0.4..0.8
    Q+=box(-0.5,-0.4,0,2.2,5.95,6.25,BEAM)+box(0.8,0.9,0,2.2,5.95,6.25,BEAM)+box(-0.5,0.9,2.1,2.2,5.95,6.25,BEAM)         # door frame
    Q+=box(-3.4,3.4,2.9,3.1,-0.8,6.2,(40,30,26))
    for z in (0.4,2.2,4.0,5.6): Q+=box(-3.2,3.2,2.7,2.9,z,z+0.2,BEAM)
    Q+=box(-3.45,-3.38,1.0,1.05,1.9,3.5,BEAM)+box(-3.45,-3.38,2.25,2.3,1.9,3.5,BEAM)+box(-3.45,-3.38,1.0,2.3,2.65,2.7,BEAM)   # window frame
    Q+=[quad([(-3.6,0.9,1.9),(-3.6,0.9,3.5),(-3.6,2.4,3.5),(-3.6,2.4,1.9)],(255,236,190),True)]                          # the window light (outside)
    Q+=[quad([(-3.15,0.01,1.9),(-1.4,0.01,1.5),(-1.4,0.01,3.9),(-3.15,0.01,3.5)],(190,150,88),True)]                      # light patch on the floor
    for k,y in enumerate((0.55,1.1,1.65)):                                                                               # the shelf along the right wall, full of the pots she has put out
        Q+=box(2.7,3.2,y-0.04,y,0.4,5.0,WOODC)
        for j in range(5):
            c=TERRA if (j+k)%2 else TERRA_D; zz=0.8+j*0.85; Q+=box(2.78,3.08,y,y+0.34,zz-0.15,zz+0.15,c)+box(2.82,3.04,y+0.34,y+0.42,zz-0.1,zz+0.1,TERRA_D)
    Q+=box(PD[0]-0.32,PD[0]+0.32,0.58,0.64,PD[2]-0.28,PD[2]+0.28,WOODC)+box(PD[0]-0.3,PD[0]-0.26,0,0.58,PD[2]-0.26,PD[2]-0.22,WOODC)+box(PD[0]+0.26,PD[0]+0.3,0,0.58,PD[2]-0.26,PD[2]-0.22,WOODC)+box(PD[0]-0.3,PD[0]-0.26,0,0.58,PD[2]+0.22,PD[2]+0.26,WOODC)+box(PD[0]+0.26,PD[0]+0.3,0,0.58,PD[2]+0.22,PD[2]+0.26,WOODC)   # the door shelf
    tx,tz=TBL[0],TBL[2]; Q+=box(tx-0.45,tx+0.45,0.68,0.73,tz-0.4,tz+0.4,WOODC)
    for sx in (-1,1):
        for sz in (-1,1): Q+=box(tx+sx*0.4-0.03,tx+sx*0.4+0.03,0,0.68,tz+sz*0.35-0.03,tz+sz*0.35+0.03,WOODC)
    sx_,sz_=STOOL[0],STOOL[2]; Q+=box(sx_-0.2,sx_+0.2,0.38,0.43,sz_-0.2,sz_+0.2,WOODC)+box(sx_-0.17,sx_-0.13,0,0.38,sz_-0.17,sz_-0.13,WOODC)+box(sx_+0.13,sx_+0.17,0,0.38,sz_+0.13,sz_+0.17,WOODC)+box(sx_-0.17,sx_-0.13,0,0.38,sz_+0.13,sz_+0.17,WOODC)+box(sx_+0.13,sx_+0.17,0,0.38,sz_-0.17,sz_-0.13,WOODC)
    return Q
ROOM=room()
def outside():
    Q=tiled_plane(-14,14,6.2,26,0.0,1.6,lambda i,j:(190,182,150) if (i+j)%2 else (176,170,140))
    Q+=box(-0.7,1.1,0.001,0.002,6.2,26,(206,196,160))
    for (x,z,s) in ((-5,10,1.1),(4,13,1.2),(-3,18,1.3),(7,20,1.0),(-8,22,1.2)):
        Q+=box(x-0.2*s,x+0.2*s,0,2*s,z-0.2*s,z+0.2*s,(80,60,44))+box(x-1.1*s,x+1.1*s,1.7*s,3.2*s,z-1.1*s,z+1.1*s,(86,124,84))
    Q+=[quad([(-30,0,34),(30,0,34),(30,16,34),(-30,16,34)],(214,226,238),True)]
    return Q
OUTSIDE=outside()
BROOM_LEAN=[]

# ======================= camera =======================
LIFT_A=look.Path([(0,0.28),(1.4,0.22),(2.8,0.05),(T0['3a'],0.0),(T_FB[0]-0.01,0.0)])
YAW_A=look.Path([(0,-0.38),(1.5,-0.25),(T0['3a'],-0.10),(T0['4'],0.12),(T_FB[0]-0.01,0.2)])
PIT_A=look.Path([(0,0.04),(T0['3a'],0.06),(T0['4'],0.08),(T_FB[0]-0.01,0.05)])
DMIN_A=look.Path([(0,2.25),(1.3,2.0),(T0['2'],2.7),(T0['3a'],3.1),(T0['3c'],3.1),(T0['4'],2.5),(T0['4']+2.4,2.1),(T_FB[0]-0.01,2.1)])
FOV_A=look.Path([(0,44),(T_FB[0]-0.01,44)])
YAW_F=look.Path([(T_FB[0],0.3),(T0['5']+1.5,0.12),(T_FB[1],0.0)])
PIT_F=look.Path([(T_FB[0],0.36),(T0['5']+1.2,0.26),(T_FB[1],0.14)])
DMIN_F=look.Path([(T_FB[0],4.4),(T0['5']+1.5,4.0),(T_FB[1],3.6)])
YAW_B=look.Path([(T_FB[1],0.42),(T0['6']+2.5,0.15),(T0['7'],0.02),(T0['7']+2.0,-0.30),(T0['8']+0.5,-0.45),(T0['8']+2.5,-0.25),(T0['9'],0.05),(T0['9']+1.8,0.28),(T0['10']+1.7,0.2),(DUR,-0.38)])
PIT_B=look.Path([(T_FB[1],0.10),(T0['7'],0.06),(T0['8'],0.10),(T0['9'],0.08),(T0['10'],0.10),(T0['10']+1.7,0.30),(DUR,0.04)])
DMIN_B=look.Path([(T_FB[1],1.8),(T0['6']+2.5,2.6),(T0['6']+4.5,3.4),(T0['7'],3.2),(T0['8']-0.2,2.6),(T0['8']+1.6,2.0),(T0['9'],2.9),(T0['9']+2.0,3.2),(T0['10'],3.4),(T0['10']+1.7,4.4),(DUR,2.25)])
LIFT_B=look.Path([(T_FB[1],0.0),(DUR-2.2,0.0),(DUR,0.28)])
def cam_params(t):
    if t<T_FB[0]: return YAW_A(t),PIT_A(t),DMIN_A(t),44.0,LIFT_A(t)
    if t<T_FB[1]: return YAW_F(t),PIT_F(t),DMIN_F(t),44.0,0.0
    return YAW_B(t),PIT_B(t),DMIN_B(t),44.0,LIFT_B(t)
def subject_pts(t,fb):
    b=wstate(t,fb)['base']; return [(b[0],b[1],b[2]),(b[0],b[1]+1.0,b[2]),(b[0],b[1]+1.75,b[2])]
def helper_pts(t,fb,anchor):
    O=[]
    if fb:
        b=boy_state(t)
        if b: O+=look.blend_pts([(b['base'][0],0,b['base'][2]),(b['base'][0],1.1,b['base'][2])],anchor,sm(seg01(t,T_FB[0],T_FB[0]+0.5)))
        return O
    pp=(PD[0],0.0,PD[2]); O+=[(pp[0],0.0,pp[2]),(pp[0],0.7,pp[2])]                                    # the pot on the door shelf is always in the picture
    for i in range(4):
        p=hero_pose(i,t)
        if p is None: continue
        z=p['base'][2]; w=sm(seg01(8.2-z,0.0,2.0))*(1-sm(seg01(z,6.4,8.6)))
        if w>0.001: O+=look.blend_pts([(p['base'][0],0,z),(p['base'][0],1.9,z)],anchor,w)
    a=anon_pose(t)
    if a: O+=look.blend_pts([(a['base'][0],0,a['base'][2]),(a['base'][0],1.8,a['base'][2])],anchor,1.0-sm(seg01(t,T0['6']+SCR['dur']['6']-0.4,T0['6']+SCR['dur']['6']+0.6)))
    k=kn_pose(t)
    if k is not None:
        z=k['base'][2]; w=sm(seg01(8.4-z,0.0,2.2)); O+=look.blend_pts([(k['base'][0],0,k['base'][2]),(k['base'][0],1.8-0.5*k.get('sit',0),k['base'][2])],anchor,w*(1-sm(seg01(t,T0['10']+1.7,DUR-0.6))))
    fade=1-sm(seg01(t,T0['10']+1.7,DUR-0.6))                                                          # table + knight leave the group at the end: the last frame = frame 0 composition
    if t>=T0['9']-0.5: O+=look.blend_pts([(TBL[0],0.7,TBL[2])],anchor,fade)
    return O
def cam_raw(t,fb=None):
    fb=in_fb(t) if fb is None else fb
    yaw,pit,dmin,fov,lift=cam_params(t); sub=subject_pts(t,fb); anchor=sub[1]
    pos,tgt=look.follow_group(sub,helper_pts(t,fb,anchor),look.orbit_dir(yaw,pit),fov,W,H,d_min=dmin,d_max=5.0,margin=0.12,third=0.15,lift=lift)
    return dict(cam=pos,tgt=tgt,fov=fov)

CUTS=[0.0,T_FB[0],T_FB[1]]
def cam_shot(t,fb=None): return look.smooth_shot(cam_raw,t,CUTS)

# ======================= render =======================
RND=Renderer(W,H,fog=(150,150,158)); RNF=Renderer(W,H,fog=(150,128,108))
def lights(t,fb):
    fl=1.0+0.03*math.sin(t*7)
    if fb: return [((-2.8,1.7,2.9),(255,226,184),1.7),((0.2,1.9,5.8),(255,230,196),0.9),((0,2.5,1.0),(255,214,170),0.4)]
    return [((-2.8,1.7,2.9),(255,214,150),1.7*fl),((0.2,1.9,5.8),(236,242,255),1.0),((0,2.5,1.0),(255,200,150),0.35)]
def glow_amt(t):
    """the knight's pot glows gold from the moment the coin is back (end of the lid lift)"""
    return 0.45*sm(seg01(t,T_LID[3],T_LID[3]+1.6))
def render_world(t,fb,sh):
    cam=Camera.look(sh['cam'],sh['tgt']); cp=sh['cam']; layers=[ROOM,OUTSIDE]
    ps=pot_present(t); gl=0.0 if fb else glow_amt(t)
    if ps is not None:
        lid,cn=(None,False) if fb else lid_state(t)
        layers.append(pot_model((PD[0],0.64,PD[2]),pot_scale(t),lid=lid,glow=gl,coin=cn,t=t))
    for tsi in TS: layers.append(shards(tsi,(PD[0],0.64,PD[2]),int(tsi*10)%97+3,t))
    if fb:
        layers.append(woman_model(wstate(t,True),cp,young=True,lum=1.25))
        b=boy_state(t)
        if b: layers.append(boy_model(b,cp))
    else:
        layers.append(woman_model(wstate(t),cp,lum=1.25))
        for i in range(4):
            p=hero_pose(i,t)
            if p is not None:
                layers.append(hero_model(i,p,cp))
                tsi=TS[i]
                if tsi+0.02<=t<tsi+0.95:                                                                 # the coin: out of the pot, caught, pocketed
                    u=seg01(t,tsi,tsi+0.45); c0=np.array((PD[0],0.9,PD[2])); c1=np.array((PD[0]-0.1,1.2,HSTAND-0.4)); cc=c0+(c1-c0)*u; cc[1]+=0.5*math.sin(PI*u)
                    if t<tsi+0.8: layers.append(coin_model(tuple(cc),t))
        a=anon_pose(t)
        if a: layers.append(hero_model(1,a,cp,lum=0.8)+box(a['base'][0]-0.02,a['base'][0]+0.02,1.0+0.05*math.sin(t*14),1.06,a['base'][2]-0.3,a['base'][2]-0.26,GOLD,emit=True))
        k=kn_pose(t)
        if k is not None: layers.append(NW.lum_lit(FB.knight(**k),cp,0.85,0.2))
        if t>=T_CUP[0]+0.25:
            for cx in (TBL[0]-0.12,TBL[0]+0.18):
                layers.append(box(cx-0.05,cx+0.05,0.73,0.82,TBL[2]+0.15-0.05,TBL[2]+0.15+0.05,(236,232,222),emit=True)+box(cx-0.035,cx+0.035,0.8,0.815,TBL[2]+0.15-0.035,TBL[2]+0.15+0.035,(150,96,52),emit=True))
            layers.append(steam((TBL[0]-0.12,0.82,TBL[2]+0.15),t,1)+steam((TBL[0]+0.18,0.82,TBL[2]+0.15),t,2))
    R=RNF if fb else RND
    img,vi,zb=zrender(R,cam,layers,lights(t,fb),fov=sh['fov'],fog_start=14,fog_end=60,ambient=0.5,return_z=True)
    a=np.asarray(img).astype(np.float32); a=look.outline(a,zb)
    if fb:
        l=a.mean(axis=2,keepdims=True); a=(l*0.55+a*0.45)*np.array([1.06,0.97,0.86])*0.94
    return a,vi
def frame_low(t):
    fb=in_fb(t); sh=cam_shot(t,fb); a,vi=render_world(t,fb,sh)
    a=np.clip((a-110)*1.08+112,0,255)
    return post.ps1(Image.fromarray(a.astype(np.uint8)),levels=6),vi,sh
def counter(t):
    if t>=T_HUD0: return 'POTS SMASHED TODAY',0
    n=14600+sum(1 for tsi in TS if t>=tsi+0.05); return 'POTS',f'{n:,}'
def overlays(arr,t,vi,sh):
    im=Image.fromarray(np.clip(arr,0,255).astype(np.uint8)); d=ImageDraw.Draw(im); lab,val=counter(t)
    pop=any(0<=t-(tsi+0.05)<0.25 for tsi in TS)or(0<=t-T_HUD0<0.3)
    look.hud_counter(d,lab,val,(255,255,255) if pop else GOLD,y=70)
    return np.asarray(im).astype(np.float32)
SUBS=look.Subtitles(SCR,LINES,W,H,S,COL,hil={'POT?','SMASH','FORTY','THANK','COIN','SON','HERO,','WROTE.','SWING.','REPLACE.','SHELF.','TEA?'},card_y=0.2,card_sc=8.0,card_n=18)
def finish(t):
    img,vi,sh=frame_low(t); end=seg01(t,DUR-0.5,DUR)
    if end>0: img=Image.fromarray((np.asarray(img).astype(np.float32)*(1-0.12*end)).astype(np.uint8))
    return img,vi,sh
def frame_final(t):
    img,vi,sh=finish(t); arr=post.upscale(img,S); arr=overlays(arr,t,vi,sh); return SUBS.apply(arr,t)
def frame(t): return Image.fromarray(np.clip(frame_final(t),0,255).astype(np.uint8)).resize((W,H),Image.BOX)

TEST=os.environ.get('TEST')
if TEST and __name__=='__main__':
    ts=[float(x) for x in TEST.split(',')]; ims=[Image.fromarray(np.clip(frame_final(x),0,255).astype(np.uint8)).resize((270,480),Image.LANCZOS) for x in ts]
    per=int(os.environ.get('PER','8')); rows=(len(ims)+per-1)//per; shp=Image.new('RGB',(min(per,len(ims))*272,rows*482))
    for i,im in enumerate(ims): shp.paste(im,((i%per)*272,(i//per)*482))
    shp.save(os.environ.get('TEST_OUT','test_pt.png')); sys.exit()

# ======================= QA manifest =======================
def _w(t): return wstate(t,in_fb(t))
def _kn(t): return kn_pose(t)
QA=dict(fps=FPS,dur=DUR,W=W,frame=frame,
    chars={'woman':(_w,lambda **k:NW.human(kind='woman',cane=False,**k),'none','none'),'knight':(_kn,FB.knight,'sword','hip')},
    geom=lambda t,name,st,V:[],camera=lambda t:cam_shot(t)['cam'],min_cam_dist=0.35,camera_ok=lambda p:-3.3<p[0]<3.3 and -0.55<p[2]<5.9 and 0.1<p[1]<2.8,
    allow_jump=[(w,f/FPS) for w in ('woman','knight') for c in (0.0,T_FB[0],T_FB[1]) for f in range(int(c*FPS)-3,int(c*FPS)+6)],weapon_events=[],
    scenes=[dict(id='now1',t0=0.0,t1=T_FB[0],action='frame 0: a sword shatters the pot; three heroes smash and take the coin; she presses a coin into a new pot'),
            dict(id='flash',t0=T_FB[0],t1=T_FB[1],action='flashback: the boy with the wooden sword leaves through the door'),
            dict(id='now2',t0=T_FB[1],t1=DUR,action='a hero walks away; the knight lifts the lid, puts the coin back, sits; tea; the pot glows')],
    texts=lambda:[('hud','POTS SMASHED TODAY',1)])

# ======================= AUDIO =======================
LVL={'3a':1.0,'3c':1.5,'8':-3.0,'9':-1.0}
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=61); sr=s.sr; n=s.n; t=s.t; BED=np.zeros(n); FXb=np.zeros(n); PAD=np.zeros(n)
    def put(buf,x,t0,v=1.0):
        i=int(t0*sr)
        if i>=n or i<0: return
        j=min(n,i+len(x)); buf[i:j]+=(x*v)[:j-i]
    def nb(t0,d,lo,hi,v,seed,shape=2): put(FXb,s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v)
    def tone(t0,m,d,v,wave='sin',duty=0.5,dec=3.0,att=0.005,glide=0.0,buf=None):
        f=440*2**((m-69)/12); tt=s.T(d); fr=f*(1+glide*tt/d); ph=np.cumsum(fr)/sr%1
        x=np.where(ph<duty,1.0,-1.0) if wave=='sq' else (4*np.abs(ph-0.5)-1 if wave=='tri' else np.sin(2*np.pi*ph))
        put(FXb if buf is None else buf,x*np.minimum(1,tt/att)*np.exp(-tt*dec),t0,v)
    def step(t0,v=0.03,seed=0):
        tt=s.T(0.12); put(FXb,s.filt_short(s.noise(0.12,seed),lo=150,hi=1500)*np.exp(-tt*34)+np.sin(2*np.pi*80*tt)*np.exp(-tt*28)*0.3,t0,v)
    def tock(t0,v=0.04): tt=s.T(0.09); put(FXb,np.sin(2*np.pi*190*tt)*np.exp(-tt*38)+s.filt_short(s.noise(0.09,int(t0*29)),lo=300,hi=2500)*np.exp(-tt*45)*0.5,t0,v)
    def shatter(t0,v=0.09):
        nb(t0,0.5,700,6000,v,int(t0*100)%977,1)
        for k in range(7): tone(t0+0.02+0.035*k*(1+hsh(k,int(t0*10))),88+4*hsh(k,3)+3*k%7,0.12,v*0.18,'sin',dec=30)
        tt=s.T(0.2); put(FXb,s.filt_short(s.noise(0.2,int(t0*7)%311),lo=60,hi=500)*np.exp(-tt*18),t0,v*0.8)
    def clink(t0,v=0.02,seed=0):
        for k,f in enumerate((3100,4200,2600)): tt=s.T(0.3); put(FXb,np.sin(2*np.pi*f*(1+0.01*hsh(seed+k))*tt)*np.exp(-tt*(16+4*k)),t0+k*0.04,v*(1-0.25*k))
    def hum(t0,notes,v=0.018,step_=0.34):
        for i,m in enumerate(notes):
            d=0.3; tt=s.T(d); f=440*2**((m-69)/12)*(1+0.012*np.sin(2*np.pi*5.5*tt)); ph=2*np.pi*np.cumsum(f)/sr
            put(FXb,(np.sin(ph)+0.3*np.sin(2*ph))*np.sin(np.pi*tt/d)**1.5,t0+i*step_,v)
    # ---- bed: morning birds in the air (smooth chirps), soft room tone; the flashback goes quiet (never a per-sample gate)
    warm=np.where((t>=T_FB[0])&(t<T_FB[1]),1.0,0.0); sm_f=np.convolve(warm,np.ones(2400)/2400,'same')
    BED+=s.filt(s.rng.normal(0,1,n),lo=60,hi=500)*0.04*(0.5+0.5*np.sin(2*np.pi*t/6.7+1.0))*(1-0.5*sm_f)
    BED+=(np.sin(2*np.pi*55*t)+0.5*np.sin(2*np.pi*82.4*t+0.4))*0.015*sm_f
    for k in range(int(DUR/1.3)):
        tb=0.5+k*1.3+hsh(k,9)*0.7
        if not (T_FB[0]-0.1<tb<T_FB[1]+0.1):
            for j in range(2+k%2): tt=s.T(0.08); put(BED,np.sin(2*np.pi*(2800+700*j+400*hsh(k,j))*tt*(1+0.35*tt/0.08))*np.sin(np.pi*tt/0.08)**2,tb+j*0.12,0.007)
    # ---- 0.0 s: the smash. every hero: boots in, sword whoosh, shatter, coin clink, boots out; the new pot is set down (tock)
    for i,tsi in enumerate(TS):
        shatter(tsi,0.10); clink(tsi+0.2,0.03,seed=i*3); nb(tsi-0.28,0.3,500,3000,0.03,int(tsi*13)%401,1)
        if i>0:
            k=0
            while tsi-0.3-1.1+k*0.26<tsi-0.3: step(tsi-1.4+k*0.26,0.028,100+i*20+k); k+=1
        k=0
        while tsi+LEAVE_DT[i]+0.4+k*0.26<tsi+LEAVE_DT[i]+1.4: step(tsi+LEAVE_DT[i]+0.4+k*0.26,0.026,200+i*20+k); k+=1
        tock(tsi+1.12,0.04); nb(tsi+0.55,0.5,300,1500,0.015,int(tsi*5)%113,1)                              # new pot set down, a sweep of the broom
    nb(TS[2]+0.45,0.9,2000,7000,0.012,31,1)                                                                  # hero 2 rattles the shards
    # ---- her humming (4-5 soft notes) in the quiet stretches, a creak of the door
    hum(0.9,[64,67,69,67,64],0.016); hum(T0['4']+0.2,[62,64,67,64],0.014,0.42)
    # ---- line 4: the coin pressed into the clay, a pat
    clink(T0['4']+0.7,0.02,seed=40); tock(T0['4']+1.55,0.03); tock(T0['4']+1.9,0.026)
    # ---- flashback: wooden sword taps, a child's laugh (two rising chirps), steps away, door
    for k in range(5): tone(T_FB[0]+0.2+k*0.3,81,0.07,0.03,'sq',duty=0.4,dec=45)
    tone(T0['5']+0.9,84,0.18,0.02,'sin',dec=10,glide=0.7); tone(T0['5']+1.1,89,0.2,0.02,'sin',dec=10,glide=0.7)
    for k in range(5): step(T_FB[0]+2.2+k*0.3,0.018,300+k)
    nb(T_FB[0]-0.04,0.5,200,1800,0.04,181,1); nb(T_FB[1]-0.6,0.5,300,1400,0.015,182,1)
    # ---- line 6: steps down the lane, a coin glint
    k=0
    while T0['6']+k*0.3<T0['6']+SCR['dur']['6']+0.5: step(T0['6']+k*0.3,0.02,400+k); k+=1
    for k in range(3): clink(T0['6']+1.2+k*1.3,0.012,seed=50+k)
    # ---- the knight: boots in, armour, lid lifted (scrape), the coin glints, lid back, boots to the stool, sits
    k=0
    while T_KIN+k*0.3<T_KARR: step(T_KIN+k*0.3,0.034,500+k); k+=1
    nb(T_KARR+0.2,0.5,300,1600,0.04,531,1)
    nb(T_LID[0]+0.05,0.5,200,1500,0.035,541,1); tone(T_LID[1]+0.05,100,1.0,0.03,'sin',dec=3); clink(T_LID[1]+0.1,0.02,seed=61); tone(T_LID[1]+0.2,91,1.1,0.02,'sin',dec=3)
    tock(T_LID[3]+0.0,0.04); clink(T_LID[3]+0.05,0.015,seed=62)
    k=0
    while T_KW[0]+k*0.38<T_KW[1]: step(T_KW[0]+k*0.38,0.03,600+k); k+=1
    nb(T_SIT[0]+0.15,0.4,200,900,0.035,641,1); tock(T_SIT[1]-0.1,0.03)
    # ---- tea: kettle hiss, pour, cups set down, steam
    nb(T0['9']+0.3,1.6,3000,9000,0.012,701,1); nb(T_CUP[0]+0.1,0.5,900,3500,0.012,702,1); tock(T_CUP[0]+0.32,0.03); tock(T_CUP[1]-0.05,0.03)
    # ---- a low two-note pad under the last line (D2 + A2), a gold chime as the pot glows
    a0=T0['10']-0.2; m=np.clip(np.minimum(t-a0,DUR-t)/1.6,0,1)*(t>=a0)
    PAD+=(np.sin(2*np.pi*73.4*t)+0.55*np.sin(2*np.pi*110.0*t+0.4))*0.05*m
    for k_,mm in enumerate((88,95)): tone(T_LID[3]+0.5+k_*0.18,mm,1.6,0.025,'sin',dec=2.5)
    # ---- voice: RMS-levelled per line, per-line trim, ducking
    NB=np.zeros(n); wins=[]
    for k_,t0 in LINES:
        a,ar=_sf.read(os.path.join(TTS_DIR,'pt',f'{k_}.wav')); a=a if a.ndim==1 else a.mean(1)
        a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a); act=np.abs(a)>0.02*np.abs(a).max(); a=a*(0.12/np.sqrt((a[act]**2).mean()))*10**(LVL.get(k_,0.0)/20)
        put(NB,a,t0); wins.append((t0,t0+len(a)/sr))
    g=duck_envelope(n,sr,wins,-6.0,0.05,0.25); bed=BED*g+PAD; fx=FXb*(0.55+0.45*g)
    L=bed+fx; R_=np.roll(bed,700)+np.roll(fx,200); pk=max(np.abs(L).max(),np.abs(R_).max()); gv=pk*1.6/np.abs(NB).max()
    s.L=L+NB*gv; s.R=R_+NB*gv; s.reverb(0.12,length=1.4,decay=3.0)
    end=np.clip((DUR-t)/0.6,0,1); s.L*=end; s.R*=end
    return s.save(path,peak=0.9)
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'pots.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','17','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'pt_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=0,scan_dark=1.0,vignette=0.22,grain=0.9,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(frame_final(f/FPS),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
