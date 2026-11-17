"""THE ONE APPLE PROBLEM - 15 s cut (TikTok). Same story as one_apple.py (v4, 30 s: Instagram/YouTube), stripped to the brief:
hook -> OVERENCUMBERED freeze -> inventory, throw the golden sword -> eat, +1 HP, celebrate -> dragon lands, empty holster, look to camera -> YOU DIED.
LOCKED ASSETS are imported from one_apple.py (knight + 99-sword pack, apple, stump, golden sword, dragon, meadow, UI helpers); nothing is redrawn here.
Voice: python tools/tts/ap15.py -> $TTS_DIR/ap/N1_15.wav (hook only, faster read).
Run: TEST=0,2.5,5 python examples/one_apple_15.py -> test.png | PART=a:b | PART=audio | QA: python tools/qa/scene_qa.py examples/one_apple_15.py"""
import os, sys, math
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Camera
from nightkit import post, font
from nightkit.zraster import zrender
from nightkit.audio import Sound
import one_apple as OA
from one_apple import (FB,sm,seg01,lerp,lerp3,PI,box,prelit,kpoint,khand,k_local,knight_full,apple_quads,stump_quads,golden_sword,dragon,DR_KEYS,
                       WORLD,flowers,R,otext,ctext,panel,banner,RZ,APPLE_C,DRAGON_AT,LEAN_REACH,REACH_APPLE,HOOK_LINES,HIL,bounce,
                       W,H,S,FPS,GOLD,GOLD_D,BLADE_S,BLADE_R,YEL,RED,GRN,WHT,GRY,CYAN,BLU)
TTS_DIR=OA.TTS_DIR; OUT='out'; os.makedirs(OUT,exist_ok=True)

# ======================= timeline (seconds) =======================
HOOK=3.0                                   # hand touches the apple
T_FREEZE=(3.0,4.7); T_CONF=(4.7,6.0); T_MENU=(6.0,7.3); YES_AT=6.9
T_THROW=(7.3,8.05); PULL=7.4; RELEASE=7.52; SW_HIT=7.95
T_PICK=(8.05,9.0); APPLE_GRAB=8.45; T_EAT=(9.0,10.5); BITES=[9.45,9.85,10.25]; HP_UP=BITES[2]+0.05
T_JOY=(10.5,11.9); T_FALL=(11.9,12.2); T_LAND=12.2; T_HOLSTER=(13.0,13.75); T_LOOK=(13.75,14.45); T_DIED=14.45; DUR=15.25
N=int(round(DUR*FPS))
SW15=np.array([-1.55,0.04,-0.55]); HILT15=SW15+np.array([0.0,1.12,0.0])      # where the thrown sword sticks in the grass
DAY=(120,180,235); STORM=(96,80,120)

# ======================= states =======================
IDLE_R=(0.27,0.86,0.04); IDLE_L=(-0.27,0.86,0.04); HIP=(-0.22,0.9,0.08); CORE=(0.3,0.95,0.2)
def knight_state(t):
    st=dict(base=(0.0,0.0,RZ),yaw=0.0,sword='hip',boots=FB.STEEL_D)
    if t<2.2:                                                      # lumbers up to the stump under the weight (already close in frame 0)
        u=seg01(t,0.0,2.2); return dict(st,base=(0.0,0.0,RZ-1.0*(1-u)),walk=t*6.5,lean=0.12+0.04*math.sin(t*13),jig=1.0,ph=t,head=0.12*math.sin(t*3.2))
    if t<HOOK:                                                     # bends and reaches
        l=sm(seg01(t,2.2,2.75)); k=dict(st,lean=lerp(0.12,LEAN_REACH,l),jig=0.5,ph=t)
        return dict(k,rh=lerp3(IDLE_R,REACH_APPLE(dict(k,lean=LEAN_REACH)),sm(seg01(t,2.35,HOOK))),head=0.0)
    if t<T_FREEZE[1]:                                              # OVERENCUMBERED: frozen mid-reach, straining, trembling
        k=dict(st,lean=LEAN_REACH+0.025*math.sin(t*41),jig=1.4,ph=t*2); return dict(k,rh=REACH_APPLE(dict(st,lean=LEAN_REACH)),lh=(-0.32,0.95+0.03*math.sin(t*37),0.12),head=0.0)
    if t<T_MENU[0]:                                                # straightens up, looks back at the pack, scratches his helmet: ?
        a=sm(seg01(t,T_CONF[0],T_CONF[0]+0.35)); rh=lerp3(REACH_APPLE(dict(st,lean=LEAN_REACH)),IDLE_R,a)
        if t>=5.35: rh=lerp3(IDLE_R,(0.1,1.42,0.32),sm(seg01(t,5.35,5.65)))
        head=0.75*sm(seg01(t,4.95,5.15))*(1-sm(seg01(t,5.3,5.45)))-0.75*sm(seg01(t,5.4,5.55))*(1-sm(seg01(t,5.7,5.9)))
        return dict(st,lean=lerp(LEAN_REACH,0.12,a),rh=rh,head=head,jig=0.3,ph=t)
    if t<T_THROW[0]:                                               # (menu open) hand on helmet, deciding
        return dict(st,lean=0.12,rh=(0.1,1.42,0.32),head=0.08*math.sin((t-T_MENU[0])*3),jig=0.0,ph=0.0)
    if t<T_THROW[1]:                                               # grabs the hilt at his hip and flings the sword away over his left shoulder
        lh=lerp3(IDLE_L,HIP,sm(seg01(t,T_THROW[0],PULL)))
        if t>=PULL: lh=lerp3(HIP,(-0.55,1.62,0.12),sm(seg01(t,PULL,RELEASE)))
        if t>=RELEASE+0.12: lh=lerp3((-0.55,1.62,0.12),IDLE_L,sm(seg01(t,RELEASE+0.12,T_THROW[1])))
        rh=lerp3((0.1,1.42,0.32),IDLE_R,sm(seg01(t,T_THROW[0],T_THROW[0]+0.25)))
        return dict(st,sword='hip' if t<PULL else 'none',lean=0.12-0.17*sm(seg01(t,PULL,RELEASE)),rh=rh,lh=lh,head=-0.6*sm(seg01(t,RELEASE,RELEASE+0.15))*(1-sm(seg01(t,SW_HIT+0.05,T_THROW[1]))),jig=0.8,ph=t)
    s0=dict(st,sword='none',jig=0.4,ph=t)
    if t<T_PICK[1]:                                                # light now: bends and picks the apple up
        a=seg01(t,*T_PICK); l=sm(seg01(a,0.0,0.4))*(1-sm(seg01(a,0.6,1.0)))*(LEAN_REACH-0.1)+0.05
        rh=lerp3(IDLE_R,REACH_APPLE(dict(s0,lean=LEAN_REACH)),sm(seg01(a,0.05,0.42)))
        if a>0.6: rh=lerp3(REACH_APPLE(dict(s0,lean=LEAN_REACH)),(0.12,1.18,0.32),sm(seg01(a,0.6,1.0)))
        return dict(s0,lean=l,rh=rh,head=0.0)
    if t<T_EAT[1]:                                                 # three bites
        up=sm(seg01(t,T_EAT[0],T_EAT[0]+0.3)); down=sm(seg01(t,10.3,10.5)); bite=max(bounce(t,[b_],0.18) for b_ in BITES)
        rh=lerp3(lerp3((0.12,1.18,0.32),(0.02,1.5,0.3),up),CORE,down); return dict(s0,lean=0.05-0.08*bite,rh=rh,head=-0.15*bite)
    if t<T_HOLSTER[0]:                                             # +1 HP! two proud hops with both arms up... then the ground booms
        arms=sm(seg01(t,10.5,10.65))*(1-sm(seg01(t,11.6,11.85))); hop=sum(abs(math.sin(PI*seg01(t,h0,h0+0.28)))*0.14 for h0 in (10.6,10.95,11.3))
        flinch=sm(seg01(t,T_LAND,T_LAND+0.15))*(1-sm(seg01(t,T_LAND+0.5,T_HOLSTER[0])))
        return dict(s0,base=(0.0,hop if t<T_LAND else 0.0,RZ),rh=lerp3(CORE,(0.3,1.75,0.0),arms),lh=lerp3(lerp3(IDLE_L,(-0.3,1.75,0.0),arms),(-0.6,1.1,0.2),flinch),lean=0.05-0.2*flinch,head=0.0,jig=1.0 if t<11.6 else 1.5,ph=t*2)
    if t<T_LOOK[0]:                                                # confident reach for the sword... pat, pat... nothing
        a=seg01(t,*T_HOLSTER); up=sm(seg01(a,0.0,0.3)); sw=sm(seg01(a,0.3,0.45)); pat=0.04*abs(math.sin((a-0.5)*30))*sm(seg01(a,0.5,0.52))*(1-sm(seg01(a,0.9,1.0)))
        lh=lerp3(lerp3((-0.6,1.1,0.2),(-0.5,1.45,0.2),up),(-0.24,0.9+pat,0.1),sw)
        return dict(s0,rh=CORE,lh=lh,lean=0.12*sw,head=-0.6*sm(seg01(a,0.7,0.95)),jig=0.3,ph=t)
    a=sm(seg01(t,T_LOOK[0]+0.15,T_LOOK[0]+0.55))                   # ...slowly turns his head to the camera
    return dict(s0,rh=CORE,lh=(-0.24,0.9,0.1),lean=0.12*(1-a)+0.012*math.sin(t*34),head=lerp(-0.6,LOOK_HEAD,a),jig=0.2,ph=t)
def sword_state(t):
    """golden sword: in the holster (None), in his hand, thrown (spinning arc), stuck in the grass + wobble"""
    if t<PULL: return None
    if t<RELEASE:
        u=sm(seg01(t,PULL,RELEASE)); d=np.array(lerp3((0.5,-0.7,-0.5),(-0.2,1.0,-0.1),u)); return dict(hilt=khand(knight_state(t),-1),dir=tuple(d/np.linalg.norm(d)))
    p0=np.array(khand(knight_state(RELEASE),-1)); u=seg01(t,RELEASE,SW_HIT)
    if u<1.0:
        hz=SW15-np.array([p0[0],0,p0[2]]); hz[1]=0; hz/=np.linalg.norm(hz); th=PI*(1-u)
        d=np.array([math.sin(th)*hz[0],-math.cos(th),math.sin(th)*hz[2]]); pos=lerp3(tuple(p0),tuple(HILT15),u)
        return dict(hilt=tuple(np.array(pos)+np.array([0,0.9*math.sin(PI*u),0])),dir=tuple(d))
    tl=t-SW_HIT; w=0.26*math.exp(-5*tl)*math.sin(26*tl); d=np.array([math.sin(w),-math.cos(w),0.0])
    return dict(hilt=tuple(SW15-d*1.12),dir=tuple(d))
def apple_state(t):
    if t<APPLE_GRAB: return tuple(APPLE_C),0
    ks=knight_state(t); n=sum(1 for b_ in BITES if t>=b_+0.05)
    return tuple(np.array(khand(ks,1))+np.array([0,0.08 if n==0 else (0.06 if n<3 else 0.0),0.02 if n==0 else 0.0])),n
def dragon_state(t):
    if t<T_FALL[0] or t>=T_DIED: return None
    st=dict(yaw=PI,eye=0.0,fire=0.0,jaw=0.0,tail=0.4*math.sin(t*2),breathe=math.sin(t*3))
    if t<T_LAND:                                                   # drops out of the sky
        u=seg01(t,*T_FALL); return dict(st,base=(DRAGON_AT[0],6.5*(1-u*u),DRAGON_AT[2]),fold=1.0,flap=0.9,head=(0,2.3,2.2),hpitch=0.25)
    land=sm(seg01(t,T_LAND,T_LAND+0.4)); base=(DRAGON_AT[0],0.0,DRAGON_AT[2]); fold=lerp(1.0,0.25,land); flap=0.5*(1-land)-0.1*land; H0=(0,2.5,2.15)
    r=sm(seg01(t,T_LAND+0.2,T_LAND+0.45))*(1-sm(seg01(t,T_LAND+0.95,T_HOLSTER[0]+0.2)))                     # ROAR
    if t<T_LOOK[0]: return dict(st,base=base,fold=fold,flap=flap,head=lerp3(H0,(0,3.05,1.85),r),hpitch=lerp(0.2,-0.5,r),jaw=r,tail=0.5*math.sin(t*5))
    a=sm(seg01(t,T_LOOK[0],T_LOOK[1])); return dict(st,base=base,fold=0.25,flap=-0.1,head=H0,hpitch=0.1,jaw=0.6*a,fire=a)               # mouth glows: fire is coming
def sky_color(t): return DAY if t<T_FALL[0] else tuple(int(v) for v in lerp3(DAY,STORM,sm(seg01(t,T_FALL[0],T_LAND+0.6))))
def dust(t): return OA.dust(t-T_LAND+OA.T_LAND)
def shadow(t):
    if not (T_FALL[0]<=t<T_LAND+0.05): return []
    k=0.6+1.6*seg01(t,*T_FALL); x,_,z=DRAGON_AT; return box(x-k,x+k,0.012,0.02,z-k*1.3,z+k*1.3,(40,70,40))

# ======================= shots =======================
def shake(V):
    sx=sy=0.0; k=bounce(V,[HOOK+0.02],0.4)
    if k>0: sx+=4*k*math.sin(V*90); sy+=3*k*math.cos(V*70)
    if T_FREEZE[0]<=V<T_FREEZE[1]: sx+=0.8*math.sin(V*120)
    k=bounce(V,[T_LAND],0.8)
    if k>0: sx+=10*k*math.sin(V*97); sy+=8*k*math.cos(V*83)
    if T_LAND+0.2<=V<T_HOLSTER[0]: sx+=1.6*math.sin(V*110)
    return (sx,sy)
WIDE_CAM=(-6.4,2.0,0.7); WIDE_TGT=(0.2,2.0,0.7); LOOK_CAM=(1.25,1.55,RZ+1.55); OTS_CAM=(-1.9,2.7,RZ-2.2)
LOOK_HEAD=math.atan2(LOOK_CAM[0],LOOK_CAM[2]-RZ)
def shot(V):
    if V<HOOK:                                                     # frame 0: big, close, moving; pulls back a little as he reaches
        kz=knight_state(V)['base'][2]; u=sm(seg01(V,0,HOOK)); return dict(cam=lerp3((-1.25,1.35,kz+1.45),(-2.5,1.2,kz+0.55),u),tgt=(0.0,lerp(1.25,0.95,u),kz+lerp(0.25,0.4,u)),fov=lerp(50,52,u),shake=shake(V))
    if V<T_CONF[0]: return dict(cam=(-2.6,1.2,RZ+0.5),tgt=(0.0,0.95,RZ+0.35),fov=52,shake=shake(V))           # straining over the apple
    if V<T_THROW[0]: return dict(cam=(1.95,1.5,RZ+1.05),tgt=(0.0,1.35,RZ),fov=50)                            # 3/4 front: confused, menu
    if V<T_PICK[0]: return dict(cam=(-1.5,1.55,RZ+2.3),tgt=(-0.75,1.0,RZ+0.1),fov=56)                         # wide-ish: the throw and the landing
    if V<T_EAT[0]: return dict(cam=(1.6,1.25,RZ+2.9),tgt=(0.0,0.9,RZ-0.05),fov=54)                          # picks the apple
    if V<T_FALL[0]: return dict(cam=(1.2,1.45,RZ+1.8),tgt=(0.0,1.4,RZ),fov=50,shake=shake(V))              # eats, celebrates
    if V<T_HOLSTER[0]: return dict(cam=OTS_CAM,tgt=lerp3((0.3,3.0,2.6),(0.2,1.5,2.2),sm(seg01(V,T_FALL[0],T_LAND+0.1))),fov=60,shake=shake(V))   # over his shoulder: the dragon lands right in front of him
    if V<T_LOOK[0]: return dict(cam=(-1.6,0.95,RZ+0.65),tgt=(-0.2,0.95,RZ),fov=46)                               # profile: empty holster
    return dict(cam=LOOK_CAM,tgt=(0.0,1.45,RZ),fov=46)                                                     # he looks at us

# ======================= render =======================
def render(V,sh):
    cam=Camera.look(sh['cam'],sh['tgt']); ks=knight_state(V); ds=dragon_state(V); ss=sword_state(V); ap=apple_state(V)
    sky=sky_color(V); R.fog=sky
    props=apple_quads(ap[0],ap[1])+(golden_sword(ss['hilt'],ss['dir']) if ss is not None else [])
    layers=[WORLD,flowers(),stump_quads(),shadow(V),prelit(knight_full(**ks),sh['cam'],warm=0.08),props]
    if ds is not None: layers.append(dragon(**{k:v for k,v in ds.items() if k in DR_KEYS}))
    layers.append(dust(V))
    dk=sm(seg01(V,T_FALL[0],T_LAND+0.6)); sun=lerp3((255,250,230),(210,160,140),dk); amb=lerp(0.62,0.45,dk)
    img,vi,zb=zrender(R,cam,layers,[((20,40,-10),tuple(int(v) for v in sun),3.0)],fov=sh['fov'],fog_start=14,fog_end=60,ambient=amb,shake=sh.get('shake',(0,0)),return_z=True)
    a=np.asarray(img).astype(np.float32); yy=np.linspace(0,1,H)[:,None,None]; sky_a=np.array(sky,np.float32)
    grad=(sky_a*(1-0.35*(1-yy))+np.array([255,255,255],np.float32)*0.18*yy)*np.ones((1,W,1),np.float32)
    a=np.where((zb==0)[...,None],grad,a)
    return post.ps1(Image.fromarray(np.clip(a,0,255).astype(np.uint8))),vi
def grade(img,V):
    a=np.asarray(img).astype(np.float32)
    if T_MENU[0]<=V<T_MENU[1]: m=sm(seg01(V,T_MENU[0],T_MENU[0]+0.2))*(1-sm(seg01(V,T_MENU[1]-0.2,T_MENU[1]))); a=a*(1-0.5*m)
    if V>=T_LOOK[0]+0.3: f=sm(seg01(V,T_LOOK[0]+0.3,T_DIED)); a=a*(1-0.2*f)+f*np.array([255,120,20])*0.22          # orange glow: the dragon's fire behind the camera
    return Image.fromarray(np.clip(a,0,255).astype(np.uint8))

# ======================= UI (2D overlays) =======================
def hook_text(d,V):
    if V>=HOOK: return
    y=12
    for ln in HOOK_LINES:
        x=(W-font.width(ln,2))//2
        for wd in ln.split(' '): otext(d,wd,x,y,YEL if wd in HIL else WHT,2); x+=font.width(wd,2)+12
        y+=18
def inv_count(V): return 100 if V<RELEASE else (99 if V<APPLE_GRAB else 100)
def hud(d,V):
    if V<HOOK or T_MENU[0]<=V<T_MENU[1] or V>=T_DIED: return
    n=inv_count(V); full=n>=100; col=RED if full else GRN
    if full and int(V*4)%2==0 and T_FREEZE[0]<=V<T_MENU[0]: col=(255,120,100)
    y0=5
    panel(d,4,y0,80,y0+14,col); otext(d,'INV',9,y0+4,WHT); otext(d,f'{n}/100',31,y0+4,col)
    hp=2 if V>=HP_UP else 1; d.rectangle([4,y0+18,80,y0+27],fill=(12,10,30),outline=(200,200,210)); otext(d,'HP',7,y0+19,WHT)
    d.rectangle([22,y0+20,78,y0+25],fill=(40,20,24)); d.rectangle([22,y0+20,22+int(56*hp/10),y0+25],fill=RED if hp<3 else GRN)
    if HP_UP<=V<HP_UP+0.9 and int(V*10)%2==0: d.rectangle([22,y0+20,22+int(56*hp/10),y0+25],fill=(255,255,255))
def banners(d,V):
    if T_FREEZE[0]<=V<T_FREEZE[0]+1.5:
        y=int(lerp(-30,52,sm(seg01(V,T_FREEZE[0],T_FREEZE[0]+0.15)))); banner(d,[('INVENTORY: 100/100',YEL)],y,CYAN,(12,10,30))
        if V>=T_FREEZE[0]+0.12: banner(d,[('OVERENCUMBERED!',RED if int(V*7)%2==0 else (255,150,120))],y+34,RED if int(V*7)%2==0 else (255,90,80))
    if T_FREEZE[0]+0.6<=V<T_CONF[0]+0.3: banner(d,[('MOVE SPEED: 0%',YEL)],128,YEL,(30,24,8))
    if T_LAND+0.6<=V<T_DIED:                                                   # boss bar
        a=sm(seg01(V,T_LAND+0.6,T_LAND+0.9)); y=int(lerp(340,282,a)); otext(d,'DRAGON',8,y,RED); otext(d,'LV 99',W-8-font.width('LV 99'),y,YEL)
        d.rectangle([7,y+10,W-7,y+18],fill=(0,0,0),outline=(230,190,90)); d.rectangle([9,y+12,W-9,y+16],fill=RED); d.rectangle([9,y+12,W-9,y+13],fill=(255,140,120))
def menu(d,V):
    if not (T_MENU[0]<=V<T_MENU[1]): return
    a=sm(seg01(V,T_MENU[0],T_MENU[0]+0.2))*(1-sm(seg01(V,T_MENU[1]-0.2,T_MENU[1])))
    y0=int(lerp(-170,4,a)); panel(d,22,y0,158,y0+196,YEL)
    n=99 if V>=YES_AT+0.1 else 100; otext(d,'INVENTORY',30,y0+6,YEL); otext(d,f'{n}/100',152-font.width(f'{n}/100'),y0+6,GRN if n==99 else RED)
    for r in range(10):
        for c in range(10):
            x,y=OA.slot_xy(r,c); x-=6; y=y+y0-14
            d.rectangle([x,y,x+10,y+10],fill=(30,26,52),outline=(70,66,110))
            if (r,c)==(0,0):
                if V<YES_AT+0.1: g=GOLD if int(V*8)%2 else (255,244,170); d.line([x+2,y+8,x+8,y+2],fill=g,width=2); d.rectangle([x+1,y+6,x+4,y+8],fill=GOLD_D)
            else: d.line([x+2,y+8,x+8,y+2],fill=(BLADE_S if (r+c)%3 else BLADE_R),width=1)
    e=sm(seg01(V,T_MENU[0]+0.2,T_MENU[0]+0.35)); r,c=lerp(5,0,e),lerp(5,0,e)                  # the cursor jumps straight to the golden sword
    x,y=OA.slot_xy(r,c); x=int(x-6); y=int(y+y0-14); d.rectangle([x-1,y-1,x+11,y+11],outline=WHT if int(V*10)%2 else YEL)
    if V<YES_AT+0.1: ctext(d,'LEGENDARY GOLDEN SWORD',y0+170,GOLD); ctext(d,'ATK 999   EQUIPPED',y0+182,WHT)
    else: ctext(d,'DROPPED: GOLDEN SWORD',y0+176,GRN)
    if T_MENU[0]+0.5<=V<YES_AT+0.15:                                          # the warning dialog, YES
        panel(d,14,y0+52,166,y0+128,RED,(30,8,10)); ctext(d,'ARE YOU SURE YOU WANT',y0+60,WHT); ctext(d,'TO DROP THIS ITEM?',y0+72,RED)
        yes=V>=YES_AT-0.2; press=V>=YES_AT
        for lab,xx,sel in (('YES',44,yes),('NO',112,not yes)):
            bc=YEL if sel and int(V*8)%2 else (WHT if sel else GRY)
            d.rectangle([xx-8,y0+98,xx+30,y0+114],fill=(255,240,200) if press and lab=='YES' else ((60,20,24) if sel else (24,12,20)),outline=bc)
            tx=xx+(22-font.width(lab))//2+2
            if press and lab=='YES': font.text(d,lab,tx,y0+102,(30,10,10),1,None)
            else: otext(d,lab,tx,y0+102,bc)
def emotes(d,vi,V,ks):
    top=np.array(kpoint(ks,(0,2.1,0)))
    def bubble(ch,col):
        p=R.project(tuple(top),vi)
        if p: x,y=int(p[0]),int(p[1]); d.rectangle([x-6,y-10,x+6,y+8],fill=WHT,outline=(0,0,0)); d.polygon([(x-2,y+8),(x+2,y+8),(x,y+11)],fill=WHT); font.text(d,ch,x-2,y-7,col,1,None)
    if T_FREEZE[0]<=V<T_FREEZE[0]+0.7 or T_LAND+0.1<=V<T_LAND+0.7: bubble('!',RED)
    if T_CONF[0]+0.2<=V<T_MENU[0] or T_HOLSTER[1]-0.2<=V<T_HOLSTER[1]+0.4: bubble('?',BLU)
    for t0 in (T_FREEZE[0]+0.4,T_LOOK[0]+0.4):                                 # sweat drops
        if t0<=V<t0+1.2:
            p=R.project(tuple(top-np.array([0,0.25,0])),vi)
            if p:
                for k in range(2): ph=((V-t0)*1.8+k*0.5)%1.0; x=int(p[0])+(-9 if k else 10); y=int(p[1])+4+int(16*ph); d.rectangle([x,y,x+1,y+3],fill=(150,210,255)); d.point((x,y-1),fill=(150,210,255))
    for b_ in BITES:
        if b_<=V<b_+0.3:
            p=R.project(tuple(top-np.array([0,0.3,0])),vi)
            if p: otext(d,'CRUNCH',int(p[0])-17,int(p[1])-6-int(8*(V-b_)/0.3),YEL)
    if HP_UP<=V<HP_UP+1.1:                                                     # tiny +1 HP
        p=R.project(tuple(top),vi)
        if p: k=seg01(V,HP_UP,HP_UP+1.1); x=int(p[0])+8; y=int(p[1])-4-int(14*k); panel(d,x-3,y-3,x+font.width('+1 HP')+3,y+9,GRN,(8,26,12)); otext(d,'+1 HP',x,y,GRN)
    if T_JOY[0]<=V<T_JOY[1]-0.2:                                               # happy notes
        for k in range(3):
            ph=((V-T_JOY[0])*1.6+k*0.33)%1.0; p=R.project(tuple(top+np.array([0.5*(k-1),-0.4+1.0*ph,0.0])),vi)
            if p: x,y=int(p[0]),int(p[1]); d.line([x,y-6,x,y+2],fill=WHT); d.rectangle([x-3,y+1,x,y+3],fill=WHT); d.line([x,y-6,x+3,y-4],fill=WHT)
    if SW_HIT<=V<SW_HIT+0.7:                                                   # sparkle + clang where the sword lands
        p=R.project(tuple(SW15+np.array([0,0.2,0])),vi)
        if p:
            x,y=int(p[0]),int(p[1]); r=int(4+8*seg01(V,SW_HIT,SW_HIT+0.7))
            for a in range(8): ang=a*PI/4+V*3; d.line([x,y,x+int(r*math.cos(ang)),y+int(r*math.sin(ang))],fill=(255,244,170))
            otext(d,'CLANG!',x-17,y-20,YEL)
    if APPLE_GRAB<=V<APPLE_GRAB+0.6:
        a=sm(seg01(V,APPLE_GRAB,APPLE_GRAB+0.12)); y=int(lerp(-30,56,a)); panel(d,40,y,140,y+26,GRN,(8,26,12)); ctext(d,'ITEM GET!',y+5,GRN); ctext(d,'APPLE',y+16,WHT)
def died(d,V):
    a=sm(seg01(V,T_DIED,T_DIED+0.06)); y=int(lerp(124,128,a)); ctext(d,'YOU DIED',y,(int(60+170*a),int(10+20*a),int(10+20*a)),3)
def frame(V):
    if V>=T_DIED:
        img=Image.new('RGB',(W,H),(int(40*(1-seg01(V,T_DIED,DUR))),0,0)); d=ImageDraw.Draw(img); died(d,V); return img
    sh=shot(V); img,vi=render(V,sh); img=grade(img,V); d=ImageDraw.Draw(img); ks=knight_state(V)
    emotes(d,vi,V,ks); hud(d,V); banners(d,V); menu(d,V)
    if V<HOOK: hook_text(d,V)
    return img

# ======================= QA manifest (tools/qa/scene_qa.py, PIPELINE.md) =======================
def _kn(t): return knight_state(t) if t<T_DIED else None
def _extra(t):
    out=[]
    if t>=T_DIED: return out
    ks=knight_state(t); ap=apple_state(t); ss=sword_state(t); ds=dragon_state(t)
    for sx in (-1,1):
        dd=np.linalg.norm(np.array(khand(ks,sx))-np.array(kpoint(ks,(sx*0.22,1.27,0))))
        if dd>0.66: out.append(('stretch',f'knight arm stretched beyond its length ({dd:.2f} m)'))
    if HOOK<=t<T_FREEZE[1] and np.linalg.norm(np.array(khand(ks,1))-APPLE_C)>0.16: out.append(('apple','his hand leaves the apple while frozen'))
    if t>=APPLE_GRAB and np.linalg.norm(np.array(ap[0])-np.array(khand(ks,1)))>0.16: out.append(('apple','apple is not in his hand'))
    if abs(t-(APPLE_GRAB-0.5/FPS))<0.5/FPS and np.linalg.norm(np.array(khand(ks,1))-APPLE_C)>0.2: out.append(('apple','hand is not on the apple when he grabs it'))
    if ss is not None:
        h=np.array(ss['hilt']); d=np.array(ss['dir'])
        if PULL<=t<RELEASE and np.linalg.norm(h-np.array(khand(ks,-1)))>0.05: out.append(('sword','sword is not in his hand'))
        for u_ in np.linspace(0,1.12,10):
            p_=h+d*u_
            if abs(p_[0])<0.47 and abs(p_[2])<0.47 and p_[1]<OA.STUMP_H-0.02: out.append(('sword','sword inside the stump')); break
            if t>=RELEASE+0.1 and math.hypot(p_[0]-ks['base'][0],p_[2]-ks['base'][2])<0.3 and p_[1]<1.9: out.append(('sword','sword inside the knight')); break
            if p_[1]<-0.05: out.append(('sword','sword under the floor')); break
    if ds is not None:
        Vd=np.array([p for q in dragon(**{k:v for k,v in ds.items() if k in DR_KEYS}) for p in q['p']]); KV=np.array([p for q in knight_full(**ks) for p in q['p']])
        dmin=min(np.linalg.norm(KV-v,axis=1).min() for v in Vd[::7])
        if dmin<0.35: out.append(('intersect',f'dragon is {dmin:.2f} m from the knight'))
    return out
TEXTS=('INVENTORY: 100/100','OVERENCUMBERED!','MOVE SPEED: 0%','INVENTORY','100/100','99/100','LEGENDARY GOLDEN SWORD','ATK 999   EQUIPPED','DROPPED: GOLDEN SWORD',
       'ARE YOU SURE YOU WANT','TO DROP THIS ITEM?','YES','NO','ITEM GET!','APPLE','CRUNCH','CLANG!','+1 HP','DRAGON','LV 99','INV','HP')
QA=dict(fps=FPS,dur=DUR,W=W,frame=frame,
    chars={'knight':(_kn,knight_full,'sword','hip'),'dragon':(dragon_state,dragon,'_none',1.0)},
    geom=OA._geom,extra=_extra,camera=lambda t: shot(t)['cam'],min_cam_dist=0.45,
    camera_ok=lambda p: p[1]>0.12 and not (abs(p[0])<0.5 and abs(p[2])<0.5 and p[1]<OA.STUMP_H+0.05),
    scenes=[dict(id='hook',t0=0.0,t1=HOOK,action='close: knight lumbers under 99 swords to the apple, reaches for it'),
            dict(id='freeze',t0=HOOK,t1=T_CONF[0],action='touches the apple; INVENTORY 100/100; OVERENCUMBERED; frozen, straining'),
            dict(id='confused',t0=T_CONF[0],t1=T_MENU[0],action='straightens up, looks back at the pack, scratches his helmet: ?'),
            dict(id='menu',t0=T_MENU[0],t1=T_THROW[0],action='inventory; cursor on the golden sword; DROP? YES'),
            dict(id='throw',t0=T_THROW[0],t1=T_PICK[0],action='pulls the golden sword from his hip and flings it; it sticks in the grass, CLANG'),
            dict(id='pick',t0=T_PICK[0],t1=T_EAT[0],action='bends and picks the apple up: ITEM GET'),
            dict(id='eat-joy',t0=T_EAT[0],t1=T_FALL[0],action='three bites, tiny +1 HP, two proud hops with arms up'),
            dict(id='dragon',t0=T_FALL[0],t1=T_HOLSTER[0],action='wide: the dragon drops out of the sky in front of him and roars'),
            dict(id='holster',t0=T_HOLSTER[0],t1=T_LOOK[0],action='profile: reaches for his sword, pats the empty holster'),
            dict(id='look',t0=T_LOOK[0],t1=T_DIED,action='he slowly looks at the camera; orange fire glow rises'),
            dict(id='died',t0=T_DIED,t1=DUR,action='smash cut: YOU DIED')],
    weapon_events=[('knight',PULL,'hip','none')],
    texts=lambda: [('hook',x,2) for x in HOOK_LINES]+[('ui',s_,1) for s_ in TEXTS]+[('ui','YOU DIED',3)])

TEST=os.environ.get('TEST')
if TEST and __name__=='__main__':
    ims=[frame(float(x)) for x in TEST.split(',')]; shp=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): shp.paste(im,(i*182,0))
    shp.resize((shp.width*2,640),Image.NEAREST).save('test.png'); sys.exit()


# ======================= AUDIO (same synth palette as one_apple.py, re-timed) =======================
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=71); sr=s.sr; n=s.n; M=np.zeros(n); AMB=np.zeros(n)
    def note(buf,t0,m,d,v,wave='sq',duty=0.5,dec=3.0,att=0.005):
        f=440*2**((m-69)/12); tt=s.T(d); ph=(f*tt)%1
        x=np.where(ph<duty,1.0,-1.0) if wave=='sq' else (4*np.abs(ph-0.5)-1 if wave=='tri' else np.sin(2*np.pi*ph))
        env=np.minimum(1,tt/att)*np.exp(-tt*dec); i=int(t0*sr); j=min(n,i+len(tt)); buf[i:j]+=(x*env*v)[:j-i]
    def nb(t0,d,lo,hi,v,seed,shape=2): s.place(s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v)
    def clank(t0,v=0.1,seed=0): tt=s.T(0.5); s.place(sum(np.sin(2*np.pi*f*tt)*np.exp(-tt*k) for f,k in ((620,9),(1500,13),(2900,19)))*0.35+s.filt_short(s.noise(0.5,seed),lo=2000,hi=8000)*np.exp(-tt*30),t0,v)
    def rattle(t0,d,v=0.03,seed=0):
        r=np.random.default_rng(seed)
        for k in range(int(d/0.04)): tt=s.T(0.04); s.place(s.filt_short(s.noise(0.04,seed*77+k),lo=1800,hi=7000)*np.exp(-tt*90),t0+k*0.04+r.uniform(0,0.012),v*r.uniform(0.4,1.0))
    def thud(t0,f=55,v=0.25,d=0.5): tt=s.T(d); s.place(np.sin(2*np.pi*f*tt*(1-0.35*tt/d))*np.exp(-tt*9)+s.filt_short(s.noise(d,int(t0*13)),lo=50,hi=600)*np.exp(-tt*12)*0.5,t0,v)
    def whoosh(t0,d=0.4,v=0.05,seed=0,lo=300,hi=3500): nb(t0,d,lo,hi,v,seed)
    def tick(t0,v=0.03): tt=s.T(0.03); s.place(np.sin(2*np.pi*2300*tt)*np.exp(-tt*120),t0,v)
    def buzzer(t0,d=0.45,v=0.12): tt=s.T(d); s.place(np.where(np.sin(2*np.pi*98*tt)>0,1.0,-1.0)*(0.6+0.4*np.sign(np.sin(2*np.pi*22*tt)))*np.exp(-tt*2.5),t0,v)
    def step_h(t0,v=0.06,seed=0): thud(t0,70,v,0.25); rattle(t0,0.15,0.03,seed)
    def crunch(t0,v=0.12,seed=0):
        for k in range(3): tt=s.T(0.06); s.place(s.filt_short(s.noise(0.06,seed*9+k),lo=1500,hi=5500)*np.exp(-tt*45),t0+k*0.05,v)
        nb(t0,0.12,200,1200,v*0.4,seed*5)
    def chime(t0,notes,v=0.04,step=0.07,d=0.3):
        for k,m in enumerate(notes): note(M,t0+k*step,m,d,v,'sq',0.25,6)
    def growl(t0,d=0.9,v=0.12,f=60):
        tt=s.T(d); mod=0.6+0.4*np.sin(2*np.pi*9*tt); s.place(s.filt_short(np.sign(np.sin(2*np.pi*np.cumsum(f+10*np.sin(2*np.pi*7*tt))/sr))*0.6+s.noise(d,int(t0*17))*0.3,hi=500)*mod*np.sin(np.pi*tt/d),t0,v)
    def grunt(t0,v=0.07,f=120,d=0.25): tt=s.T(d); x=np.where((f*(1-0.3*tt/d)*tt)%1<0.5,1.0,-1.0); s.place(s.filt_short(x,lo=100,hi=900)*np.exp(-tt*8),t0,v)
    def roar(t0,d,v=0.2):
        tt=s.T(d); ph=np.cumsum(88+30*np.sin(2*np.pi*5.5*tt)+25*np.sin(np.pi*tt/d))/sr
        x=np.sign(np.sin(2*np.pi*ph))*0.6+s.filt_short(s.noise(d,3),lo=200,hi=2500)*0.5; s.place(s.filt_short(x,hi=2400)*np.sin(np.pi*tt/d)**0.6,t0,v)
    def jaunty(a,b,v=1.0,root=60,step=0.2,minor=False):
        sc=[0,2,3,5,7,8,10,12] if minor else [0,2,4,5,7,9,11,12]; pat=[0,2,4,2,4,5,4,2,0,1,2,4,7,5,4,2]; bass=[0,0,4,4,5,5,4,4]; k=0; tc=a
        while tc<b-1e-6:
            note(M,tc,root+12+sc[pat[k%16]%8],step*0.7,0.02*v,'sq',0.25,9)
            if k%2==0: note(M,tc,root-12+sc[bass[(k//2)%8]%8],step*1.6,0.05*v,'tri',dec=5)
            k+=1; tc+=step
    AMB+=s.filt(s.rng.normal(0,1,n),lo=80,hi=800)*0.012                                              # breeze
    # ---------- hook: tuba march, heavy steps, clanking swords ----------
    for k in range(6): note(M,0.05+k*0.5,[36,43,36,43,34,41][k],0.4,0.07,'tri',dec=4); note(M,0.3+k*0.5,67,0.12,0.02,'sq',0.25,12); step_h(0.05+k*0.36,0.05,k)
    rattle(0.0,2.3,0.03,50); growl(2.4,0.5,0.05,90); grunt(2.7,0.07)
    # ---------- OVERENCUMBERED freeze ----------
    buzzer(HOOK+0.02,0.5,0.13); rattle(HOOK,0.6,0.05,51); clank(HOOK+0.03,0.08,2)
    for k,m in enumerate((57,56,55,54)): note(M,HOOK+0.45+k*0.17,m,0.2,0.04,'sq',0.5,6)        # sad trombone
    for k in range(5): grunt(3.4+k*0.25,0.05,150+12*k,0.2); rattle(3.4+k*0.25,0.15,0.03,60+k)     # strain, strain...
    note(M,T_CONF[0]+0.25,72,0.12,0.03,'sq',0.25,8); note(M,T_CONF[0]+0.4,79,0.2,0.03,'sq',0.25,8)   # '?' boop
    jaunty(T_CONF[0]+0.2,T_MENU[0],0.4,root=57,step=0.22,minor=True)
    for k in (5.4,5.55,5.7): tick(k,0.025)                                                          # helmet scratch
    # ---------- menu + throw ----------
    whoosh(T_MENU[0],0.3,0.04,90,800,5000); tick(T_MENU[0]+0.3,0.04)
    for k,m in enumerate((84,91,96,103)): note(M,T_MENU[0]+0.3+k*0.05,m,0.25,0.03,'sq',0.25,5)    # golden slot
    for k in range(3): note(M,T_MENU[0]+0.5+k*0.12,70 if k!=1 else 64,0.1,0.05,'sq',0.5,10)          # warning dialog
    tick(YES_AT-0.2,0.05); note(M,YES_AT,48,0.35,0.07,'sq',0.5,4); note(M,YES_AT,60,0.25,0.05,'sq',0.5,6); nb(YES_AT,0.25,1500,8000,0.04,91)
    clank(PULL,0.06,3); grunt(RELEASE-0.05,0.09,140,0.3); whoosh(RELEASE,0.45,0.07,92,600,4000)
    clank(SW_HIT,0.2,93); clank(SW_HIT+0.12,0.1,94)
    for k,f in enumerate((2600,3300,4100)): tt=s.T(0.8); s.place(np.sin(2*np.pi*f*tt)*np.exp(-tt*5),SW_HIT+0.05+k*0.07,0.03)
    # ---------- pick, eat, +1 HP, joy ----------
    jaunty(T_PICK[0],T_EAT[1],0.7,step=0.17)
    tt=s.T(0.1); s.place(np.sin(2*np.pi*np.cumsum(500+1200*tt/0.1)/sr)*np.exp(-tt*25),APPLE_GRAB,0.06)   # apple pop
    for k,m in enumerate((72,76,79,84,88,91)): note(M,APPLE_GRAB+k*0.05,m,0.2,0.03,'sq',0.25,6)   # ITEM GET
    for b_ in BITES: crunch(b_,0.14,int(b_*10))
    chime(HP_UP,(88,93),0.02,0.06,0.2)                                                              # tiny +1 HP ding
    jaunty(T_JOY[0],T_FALL[0]-0.15,1.1,root=62,step=0.15)
    for h0 in (10.6,10.95,11.3): thud(h0+0.28,60,0.1,0.15); rattle(h0+0.26,0.15,0.04,int(h0*10))
    # ---------- dragon ----------
    M[int((T_FALL[0]-0.1)*sr):]*=0                                                                  # the music cuts out
    tt=s.T(0.35); s.place(s.filt_short(s.noise(0.35,7),lo=200,hi=3000)*(tt/0.35)**2,T_FALL[0]-0.05,0.12)   # falling whoosh
    thud(T_LAND,40,0.6,0.9); clank(T_LAND+0.02,0.08,7); nb(T_LAND,0.6,50,500,0.2,98); rattle(T_LAND,0.6,0.07,140)
    roar(T_LAND+0.25,0.9,0.22)
    for k,tt_ in enumerate(np.arange(12.6,T_DIED,0.55)): note(M,tt_,31-(k%2),0.5,0.045,'tri',dec=2)   # boss drone
    for t0 in (13.4,13.5,13.6): clank(t0,0.06,int(t0*10))                                          # pat pat pat
    for k,m in enumerate((60,57)): note(M,T_HOLSTER[1]-0.15+k*0.1,m,0.2,0.04,'sq',0.5,6)            # bwomp
    tt=s.T(T_DIED-T_LOOK[0]-0.3); L_=len(tt); s.place(s.filt_short(s.noise(T_DIED-T_LOOK[0]-0.3,99),lo=100,hi=2500)*(tt/tt[-1])**2,T_LOOK[0]+0.3,0.16)   # fire charging behind us
    growl(T_LOOK[0],0.6,0.08,55)
    tt=s.T(0.8); s.place((np.sin(2*np.pi*55*tt)+0.7*np.sin(2*np.pi*110.5*tt)+0.4*np.sin(2*np.pi*165*tt))*np.exp(-tt*1.8),T_DIED,0.32)   # YOU DIED gong
    s.L[int(T_DIED*sr):]*=0; s.R[int(T_DIED*sr):]*=0                                               # smash cut: everything stops but the gong
    tt=s.T(0.8); g=(np.sin(2*np.pi*55*tt)+0.7*np.sin(2*np.pi*110.5*tt)+0.4*np.sin(2*np.pi*165*tt))*np.exp(-tt*1.8)*0.32; i=int(T_DIED*sr); j=min(n,i+len(g)); s.L[i:j]+=g[:j-i]; s.R[i:j]+=g[:j-i]
    for k,m in enumerate((67,64,60)): note(M,T_DIED+0.15+k*0.16,m,0.2,0.06,'sq',0.5,6)               # game over
    # ---------- voice ----------
    NB=np.zeros(n); duck=np.ones(n)
    a,ar=_sf.read(os.path.join(TTS_DIR,'ap','N1_15.wav')); a=a if a.ndim==1 else a.mean(1)
    a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a); act=a[np.abs(a)>0.02]; a=a/(np.sqrt((act**2).mean())+1e-9)*0.2
    i=int(0.05*sr); j=min(n,i+len(a)); NB[i:j]+=a[:j-i]; duck[max(0,i-int(0.05*sr)):min(n,j+int(0.1*sr))]=0.4
    duck=np.convolve(duck,np.ones(2400)/2400,'same')
    s.L+=2.0*M*duck+AMB*(np.arange(n)<int(T_DIED*sr)); s.R+=2.0*np.roll(M,240)*duck+np.roll(AMB,700)*(np.arange(n)<int(T_DIED*sr))
    s.reverb(0.14,length=1.2,decay=4.0)
    pk=max(np.abs(s.L).max(),np.abs(s.R).max()); gv=pk*1.05/np.abs(NB).max()
    s.L=s.L*(0.6+0.4*duck)+NB*gv; s.R=s.R*(0.6+0.4*duck)+NB*gv
    st=np.stack([s.L,s.R],1); st[-int(0.3*sr):]*=np.linspace(1,0,int(0.3*sr))[:,None]
    st=st/np.max(np.abs(st))*0.9; _sf.write(path,st,sr,subtype='PCM_16'); return path
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'one_apple_15.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'ap15_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.96,vignette=0.22,grain=1.5,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(post.upscale(frame(f/FPS),S),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
