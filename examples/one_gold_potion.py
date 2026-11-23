"""WHY IS THIS POTION ONLY 1 GOLD? (pilot for othercreators/RAPOR.md) ~39 s wordless PS1 drama, 9:16, nightkit. Brief: briefs/one_gold_potion.md.
A dungeon shopkeeper sells the best potion for 1 gold. Flashback: he charged 50, a party was 3 gold short and never came back.
Now a kid with 0 gold gets the potion; the tag turns 1 G -> 0 G.
Report changes vs older shorts: 270x480 internal (x4), depth outline pass, soft post (no scanlines), one accent colour (red potion), HUD counter,
hard cuts 1-3 s, caption cards (<=5 words), loop-style ending, CTA. Reuses: knight (final_boss.py) and the box human (npc_well.py).
Run: TEST=1,5,9 python examples/one_gold_potion.py -> test.png | PART=a:b | PART=audio | tools/render_parts.py --prefix og --audio one_gold.wav"""
import os, sys, math
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, quad, tiled_plane, ry as eng_ry
from nightkit import motion, post, font
from nightkit.zraster import zrender
from nightkit.audio import Sound, soft_fire
import final_boss as FB
import npc_well as NW

OUT='out'; os.makedirs(OUT,exist_ok=True)
FPS=24; W,H,S=270,480,4; F=1.0/FPS
PI=math.pi; sm=motion.smooth
def seg01(t,a,b): return max(0.0,min(1.0,(t-a)/(b-a)))
def lerp(a,b,u): return a+(b-a)*u
def lerp3(a,b,u): return tuple(a[i]+(b[i]-a[i])*u for i in range(3))
def hsh(i,s=0): v=math.sin(i*127.1+s*311.7)*43758.5453; return v-math.floor(v)
box=FB.box; xform=FB.xform
WHT=(246,242,230); YEL=(255,214,70); RED=(255,70,80)

# ======================= timeline =======================
SHOTS=[('hook',0.0,3.6),('buy1',3.6,5.4),('buy2',5.4,7.1),('mute',7.1,9.0),('door1',9.0,9.9),('door2',9.9,10.8),('door3',10.8,11.7),('door4',11.7,12.6),
       ('wall',12.6,15.6),('fb_party',15.6,18.4),('fb_tray',18.4,21.4),('fb_face',21.4,23.6),('fb_door',23.6,27.0),('now_wall',27.0,30.5),('kid',30.5,34.5),('end',34.5,38.5)]
DUR=39.0; N=int(round(DUR*FPS))
def shot_of(t):
    for n,a,b in SHOTS:
        if a<=t<b: return n,a,b
    return SHOTS[-1]
FLASH=(15.6,27.0)
def in_flash(t): return FLASH[0]<=t<FLASH[1]
CAPS=[(0.0,3.6,['WHY IS THIS POTION','ONLY 1 GOLD?'],{'1','GOLD?'},8),(3.9,5.4,['EVERY HERO','ASKS WHY.'],{'WHY.'},8),(5.9,7.0,['EVERY HERO','ASKS WHY.'],{'WHY.'},8),
      (7.4,9.0,['HE NEVER','ANSWERS.'],{'NEVER'},8),(9.0,12.6,['12 YEARS.'],{'12'},9),(12.8,15.6,['FOUR HELMETS','ON HIS WALL.'],{'FOUR','WALL.'},8),
      (15.8,18.4,['HE USED TO','CHARGE 50.'],{'50.'},8),(18.6,21.4,['THEY WERE 3','GOLD SHORT.'],{'3','SHORT.'},8),(21.6,23.6,['BUSINESS IS','BUSINESS.'],set(),8),
      (24.4,27.0,['THEY NEVER','CAME BACK.'],{'NEVER'},8),(27.2,30.5,['NOW NOBODY','IS SHORT.'],{'NOBODY','SHORT.'},8),(31.2,34.5,['SOME PRICES','GET PAID FORWARD.'],{'PAID','FORWARD.'},8),
      (35.2,38.5,['SEND THIS TO SOMEONE','WHO HELPED YOU.'],{'HELPED'},7)]

# ======================= palette / set =======================
FLOOR_A=(150,100,64); FLOOR_B=(128,84,54); WALL=(46,86,110); WALL_D=(34,64,86); WOOD=(150,98,58); WOOD_D=(104,66,40); TRIM=(86,54,34)
GOLD=(255,206,70); RUG=(52,104,120)
def tod(name): return dict(day=(255,238,180),dusk=(255,140,72),night=(46,66,150),dawn=(255,176,170),cold=(196,218,255),dark=(10,10,16))[name]
TAGP=(0.13,0.98,2.7)
PR=(-0.03,0.76,2.56)
def room():
    Q=tiled_plane(-2.6,2.6,-1.2,4.4,0.0,0.6,lambda i,j:FLOOR_A if (i+j)%2 else FLOOR_B)
    Q+=[quad([(-0.9,0.006,0.2),(0.9,0.006,0.2),(0.9,0.006,1.9),(-0.9,0.006,1.9)],RUG)]
    Q+=box(2.5,2.7,0,3.2,-1.2,4.6,WALL_D)+box(-2.7,2.7,0,3.2,4.4,4.6,WALL)+box(-2.7,2.7,0,3.2,-1.4,-1.2,WALL_D)               # right, back, front walls
    Q+=box(-2.7,-2.5,0,3.2,-1.2,0.8,WALL_D)+box(-2.7,-2.5,0,3.2,2.0,4.4,WALL_D)+box(-2.7,-2.5,2.1,3.2,0.8,2.0,WALL_D)           # left wall with the door opening
    Q+=box(-2.62,-2.5,0,2.1,0.74,0.8,TRIM)+box(-2.62,-2.5,0,2.1,2.0,2.06,TRIM)+box(-2.62,-2.5,2.1,2.18,0.74,2.06,TRIM)
    Q+=box(-2.7,2.7,3.2,3.4,-1.4,4.6,(26,40,56))
    for x in np.arange(-2.4,2.5,0.6): Q+=box(x,x+0.05,0.0,3.2,4.38,4.4,WALL_D)                                                 # back wall panelling
    for z in (0.0,1.6,3.2): Q+=box(-2.5,2.5,3.05,3.2,z,z+0.18,TRIM)                                                              # ceiling beams
    Q+=box(-1.5,1.5,0,0.2,2.9,4.4,WOOD_D)                                                                                          # platform behind the counter
    Q+=box(-1.5,1.5,0,0.7,2.1,2.9,WOOD)+box(-1.56,1.56,0.7,0.76,2.04,2.96,WOOD_D)                                                  # counter + top
    Q+=box(-1.45,1.45,0.14,0.3,2.08,2.1,TRIM)
    for k,(y,cols) in enumerate(((1.0,((90,170,210),(110,200,140),(180,120,220),(90,170,210))),(1.5,((110,200,140),(180,120,220),(90,170,210),(110,200,140))),(2.0,((180,120,220),(90,170,210),(110,200,140),(180,120,220))))):
        Q+=box(-2.45,-0.55,y-0.04,y,4.0,4.38,WOOD_D)                                                                               # shelves
        for i,c in enumerate(cols):
            x=-2.2+i*0.46; Q+=box(x-0.06,x+0.06,y,y+0.2,4.15,4.27,c,emit=True)+box(x-0.025,x+0.025,y+0.2,y+0.27,4.18,4.24,(210,214,222))
    for i in range(4):                                                                                                               # hooks + dusty helmets (plume = the party's cape colour)
        x=0.95+i*0.35; Q+=box(x-0.015,x+0.015,1.78,1.84,4.3,4.4,(60,60,66))
        Q+=box(x-0.14,x+0.14,1.46,1.76,4.0,4.28,(104,108,124))+box(x-0.145,x+0.145,1.58,1.64,3.985,4.0,(18,18,26))+box(x-0.03,x+0.03,1.76,1.9,4.06,4.2,tuple(int(c*0.6+40) for c in HELM_C[i]))
    Q+=box(-0.04,0.04,2.3,3.05,2.38,2.42,(40,40,46))+box(-0.1,0.1,2.22,2.3,2.3,2.5,(255,206,130),emit=True)                          # lamp chain + lamp
    Q+=box(TAGP[0]-0.01,TAGP[0]+0.01,0.76,0.93,2.7,2.72,(90,70,50))                                                                                 # tag stand (stick part, behind the board)
    return Q
HELM_C=[(206,60,52),(70,150,90),(236,196,60),(150,84,200)]
ROOM=room()
def door_dyn(t,col,a,show_light=True):
    """outside light, light patch on the floor, and the door leaf (a = opening angle, 0 closed)"""
    Q=[quad([(-4.0,0,-3),(-4.0,0,6),(-4.0,6,6),(-4.0,6,-3)],col,True)]
    if show_light and a>0.05:
        k=min(1.0,a); fl=tuple(int(lerp(c1,c2,0.45*k)) for c1,c2 in zip(FLOOR_A,col))
        Q+=[quad([(-2.6,0.01,0.8),(-0.9,0.01,0.3),(-0.9,0.01,2.5),(-2.6,0.01,2.0)],fl,True)]
    hinge=(-2.6,0,2.0); Qd=box(-2.64,-2.56,0,2.06,0.8,2.0,WOOD_D)+box(-2.66,-2.54,1.0,1.1,0.8,2.0,TRIM)
    return Q+xform(Qd,lambda p:eng_ry(p,-a,hinge))

# ======================= characters / props =======================
def recolor(Q,mp):
    for q in Q:
        c=tuple(q['col'])
        if c in mp: q['col']=mp[c]
    return Q
def lit(Q,cp,lum=0.85,warm=0.2): return NW.lum_lit(Q,cp,lum,warm)
KEEPER=(0.0,0.2,3.35)
def keeper(cp,young=False,base=KEEPER,yaw=PI,lum=1.35,**kw):
    Q=NW.human(base,yaw,kind='man',cane=False,**kw)
    mp={NW.COAT:(188,140,58),NW.COAT_D:(134,96,42),NW.TROUS:(58,52,72)}
    if young: mp[NW.GREY]=(74,46,30)
    return lit(recolor(Q,mp),cp,lum)
def hero(cape,base,yaw,cp,walk=0.0,rh=None,lh=None,scale=1.0,lum=0.9,head=0.0):
    Q=NW.hero_knight(cape,base=base,yaw=yaw,walk=walk,run=0.0,sword='hip',rh=rh,lh=lh,lean=0.0,head=head)
    if scale!=1.0:
        b=np.array(base,float); xform(Q,lambda p:tuple(b+(np.array(p)-b)*scale))
    return lit(Q,cp,lum)
def potion(p,t,scale=1.0):
    x,y,z=p; s=scale; g=0.9+0.1*math.sin(t*3.0)
    c=lambda v:tuple(int(min(255,a*g)) for a in v)
    Q=box(x-0.07*s,x+0.07*s,y,y+0.2*s,z-0.07*s,z+0.07*s,c((255,60,96)),emit=True)+box(x-0.03*s,x+0.03*s,y+0.2*s,y+0.28*s,z-0.03*s,z+0.03*s,(226,236,246),emit=True)
    Q+=box(x-0.035*s,x+0.035*s,y+0.28*s,y+0.32*s,z-0.035*s,z+0.035*s,(150,98,56),emit=True)+box(x-0.05*s,x-0.03*s,y+0.04*s,y+0.16*s,z-0.072*s,z-0.07*s,(255,176,196),emit=True)
    return Q
def tag_board(): return box(TAGP[0]-0.07,TAGP[0]+0.07,TAGP[1]-0.045,TAGP[1]+0.045,TAGP[2]-0.01,TAGP[2]+0.01,(238,226,196),emit=True)
def coin(p): return box(p[0]-0.04,p[0]+0.04,p[1],p[1]+0.016,p[2]-0.04,p[2]+0.04,GOLD,emit=True)
def motes(t):
    Q=[]
    for k in range(26):
        x=-1.2+2.4*hsh(k,4)+0.12*math.sin(t*0.6+k); z=1.4+2.0*hsh(k,5); y=(0.4+hsh(k,6)*1.8+0.06*t*(0.4+hsh(k,7)))%2.0+0.3; s=0.011
        Q+=box(x-s,x+s,y,y+s,z-s,z+s,(255,226,170),emit=True)
    return Q
def blink(t,times): return max([math.sin(PI*seg01(t,b,b+0.2)) for b in times]+[0.0])
def ang(u,a,b): return seg01(u,a,b)

# ======================= shots =======================
def day_color(u):
    cols=[tod('day'),tod('dusk'),tod('night'),tod('dawn')]; return cols
HINGE_OPEN=1.5
def sold(t):
    if t<3.6: return 4017
    if t<5.0: return 4017
    if t<5.4: return 4018
    if t<9.0: return 4018+(1 if t>=6.6 else 0)
    if t<12.6: return int(lerp(4019,52417,sm(seg01(t,9.0,12.6))**1.6))
    if t<34.2: return 52418
    return 52419
def buy_shot(u,cape,cp,flip,t):
    """hero pays, takes the potion, asks 'why?'. flip mirrors the camera."""
    base=(-0.15,0.0,1.85); L=[]; P0=(base[0]+0.05,0.72,2.46); potion_p=P0; rh=None
    pay=(0.22,0.84,0.52); coin_at=(base[0]+0.04,0.72,2.38)
    if 0.15<=u<0.6:
        a=sm(seg01(u,0.15,0.4)); rh=lerp3((0.27,0.86,0.04),pay,a)
        L+=coin((base[0]+0.0+0.22*a,0.74+0.1*(1-a),base[2]+0.52*a))
    elif u>=0.6:
        L+=coin(coin_at); rh=lerp3(pay,(0.27,0.86,0.04),sm(seg01(u,0.6,0.85)))
    if u>=0.85:
        a=sm(seg01(u,0.85,1.2)); hand=lerp3((0.27,0.86,0.04),(0.22,0.92,0.62),a if u<1.2 else 1.0)
        hw=(base[0]+hand[0],base[1]+hand[1]-0.05,base[2]+hand[2]); potion_p=lerp3(P0,hw,a) if u<1.2 else (base[0]+0.2,0.92-0.05,base[2]+0.35)
        if u<1.2: rh=hand
        else: rh=lerp3((0.22,0.92,0.62),(0.2,1.0,0.3),sm(seg01(u,1.2,1.5))); potion_p=(base[0]+rh[0],base[1]+rh[1]-0.12,base[2]+rh[2])
    cam=(0.95,1.5,0.7) if not flip else (-1.05,1.4,0.75); tgt=(-0.05,1.15,3.0)
    return dict(cam=cam,tgt=tgt,fov=56,layers=[hero(cape,base,0.0,cam,rh=rh),keeper(cam,blink=blink(t,(5.0+0.1*flip,)),head=0.0,gaze=0.0),potion(potion_p,t),coin_free(L)],
                bubbles=[((base[0],2.02,base[2]),'?')] if u>1.3 else [])
def coin_free(L): return L
def make_shot(t):
    name,t0,t1=shot_of(t); u=t-t0; cpk=None
    flash=in_flash(t); young=flash
    # ---------------- present ----------------
    if name=='hook':
        k=motion.creep(t,0.0,0.0016,FPS); cam=motion.dolly((0.05,1.0,1.9),(0.0,1.3,3.35),k); tgt=(0.0,1.3,3.35)
        return dict(cam=cam,tgt=tgt,fov=34,layers=[keeper(cam,blink=blink(t,(1.0,2.6)),gaze=1.0*sm(seg01(t,1.8,2.2))*(1-sm(seg01(t,2.9,3.2))),head=0.35*sm(seg01(t,1.8,2.2))*(1-sm(seg01(t,2.8,3.2)))),potion(PR,t,1.0),tag_board()],tag='1 G')
    if name=='buy1': s=buy_shot(u,(206,60,52),None,0,t); s['tag']='1 G'; s['layers'].append(tag_board()); return s
    if name=='buy2': s=buy_shot(u,(70,150,90),None,1,t); s['tag']='1 G'; s['layers'].append(tag_board()); return s
    if name=='mute':
        k=motion.creep(t,t0,0.002,FPS); cam=motion.dolly((0.08,1.1,2.15),(0.0,1.4,3.35),k); tgt=(0.0,1.38,3.35); hd=0.8*sm(seg01(u,1.1,1.5)); lean=0.12*math.sin(PI*seg01(u,0.4,1.0))
        return dict(cam=cam,tgt=tgt,fov=36,layers=[keeper(cam,blink=blink(t,(7.8,8.5)),head=hd,tilt=0.1*sm(seg01(u,0.2,0.5)),lean=lean,gaze=-0.6*sm(seg01(u,0.0,0.6))+0.6*sm(seg01(u,1.1,1.4))),potion(PR,t),tag_board()],tag='1 G',bubbles_screen=[(0.2,0.62,'?',1.0)] if u<1.2 else [])
    if name.startswith('door'):
        i=int(name[-1])-1; col=[tod('day'),tod('dusk'),tod('night'),tod('dawn')][i]; capes=[(206,60,52),(70,150,90),(236,196,60),(150,84,200)]
        cam=(0.9,1.35,1.35); tgt=(-2.6,1.2,1.4); x=lerp(-4.2,-0.45,sm(seg01(u,0.0,0.85))); b=(x,0.0,1.4)
        return dict(cam=cam,tgt=tgt,fov=62,layers=[door_dyn(t,col,HINGE_OPEN),hero(capes[i],b,PI/2,cam,walk=x*4.5,lum=0.38,scale=1.0)],ambient_boost=0.0,door_col=col)
    if name=='wall':
        z=lerp(0.9,2.15,sm(seg01(u,0.0,2.8))); cam=(1.45,lerp(1.5,1.62,seg01(u,0,3.0)),z); tgt=(1.45,1.62,4.4)
        return dict(cam=cam,tgt=tgt,fov=52,layers=[],extra_lights=[((1.4,1.8,3.0),(255,214,160),0.7)])
    # ---------------- flashback ----------------
    if name=='fb_party':
        cam=motion.dolly((0.0,1.55,0.3),(0.0,1.2,3.3),motion.creep(t,t0,0.0012,FPS)); tgt=(0.0,1.2,3.3); L=[]
        caps=[(206,60,52),(70,150,90),(236,196,60),(150,84,200)]; xs=(-1.12,-0.62,0.62,1.12)
        for i,(c,x) in enumerate(zip(caps,xs)):
            rh=None
            if i==2: rh=lerp3((0.27,0.86,0.04),(0.2,0.9,0.55),sm(seg01(u,0.4,0.9)))
            L.append(hero(c,(x,0.0,1.85-0.06*(i%2)),0.0,cam,rh=rh,lum=0.8))
        return dict(cam=cam,tgt=tgt,fov=50,layers=L+[keeper(cam,young=True,gaze=0.0,blink=blink(t,(17.0,)),tilt=0.08),potion((0.0,0.76,2.5),t),tag_board()],tag='50 G',grade='flash')
    if name=='fb_tray':
        cam=(0.3,1.36,2.499); tgt=(0.3,0.72,2.5); L=[]; n=int(min(47,47*sm(seg01(u,0.2,1.7))));
        L+=box(0.0,0.6,0.76,0.77,2.2,2.82,(70,22,36))                                                                            # tray cloth
        for k in range(50):
            cx=0.08+0.1*(k%5)*0.9*1.0+0.0; cx=0.06+0.12*(k%5); cz=2.24+0.056*(k//5)
            if k<n: L+=box(cx-0.045,cx+0.045,0.77,0.79,cz-0.024,cz+0.024,GOLD,emit=True)
            else:
                pulse=0.5+0.5*math.sin(u*9.0) if k>=47 and u>1.9 else 0.2
                L+=box(cx-0.045,cx+0.045,0.77,0.772,cz-0.024,cz+0.024,tuple(int(a*(0.35+0.65*pulse)) for a in ((255,60,60) if k>=47 else (110,50,60))),emit=True)
        pz=lerp(2.5,3.9,sm(seg01(u,2.3,2.95))); L+=potion((0.62,0.76,pz),t)
        return dict(cam=cam,tgt=tgt,fov=50,layers=[L],tag=None,grade='flash',tray=(n,u))
    if name=='fb_face':
        cam=motion.dolly((0.08,1.1,2.15),(0.0,1.4,3.35),motion.creep(t,t0,0.002,FPS)); tgt=(0.0,1.38,3.35)
        sh=0.5*math.sin(2*PI*(u-0.5)/1.0)*(1-seg01(u,1.5,2.2)) if u>0.5 else 0.0
        return dict(cam=cam,tgt=tgt,fov=36,layers=[keeper(cam,young=True,head=sh,blink=blink(t,(22.0,)),gaze=0.0),potion(PR,t),tag_board()],tag='50 G',grade='flash')
    if name=='fb_door':
        cam=(1.2,1.35,1.4); tgt=(-2.6,1.2,1.4); a=HINGE_OPEN*(1-sm(seg01(u,2.5,3.05))); col=tod('cold'); L=[door_dyn(t,col,a)]
        caps=[(70,150,90),(236,196,60),(150,84,200),(206,60,52)]
        for i,c in enumerate(caps):
            d=0.3*i; sp=1.55; x=-0.3-sp*max(0.0,u-d)
            hd=0.0
            if i==3:                                                                                                          # the red one stops and looks back
                x=-0.3-sp*max(0.0,min(u-d,1.1))-sp*max(0.0,u-d-1.9); hd=-1.0*sm(seg01(u,1.2,1.5))*(1-sm(seg01(u,1.9,2.15)))
            if x>-4.4: L.append(hero(c,(x,0.0,1.3+0.18*(i%2)),-PI/2,cam,walk=x*4.5,lum=0.3,head=hd))
        return dict(cam=cam,tgt=tgt,fov=60,layers=L,grade='flash',door_col=col,door_a=a)
    # ---------------- present again ----------------
    if name=='now_wall':
        cam=motion.dolly((0.15,1.5,2.0),(1.0,1.5,4.0),motion.creep(t,t0,0.0014,FPS)); tgt=(1.05,1.5,4.2)
        rh=lerp3((0.27,0.68,0.05),(0.0,1.4,0.42),sm(seg01(u,0.5,1.3)))*1 if u<2.2 else lerp3((0.0,1.4,0.42),(0.27,0.68,0.05),sm(seg01(u,2.2,2.8)))
        hd=0.0 if u<2.3 else -0.9*sm(seg01(u,2.3,2.8))
        return dict(cam=cam,tgt=tgt,fov=50,layers=[keeper(cam,base=(0.95,0.2,3.95),yaw=0.0,rh=rh,head=hd,lum=0.95),potion(PR,t)],extra_lights=[((1.3,2.0,3.4),(255,214,160),0.6)])
    if name=='kid':
        kb=(-0.15,0.0,2.0); L=[]; cam=(0.9,1.35,0.85); tgt=(-0.05,1.12,3.0)
        rh=lerp3((0.27,0.86,0.04),(0.2,0.8,0.62),sm(seg01(u,0.3,0.8))) if u<2.1 else lerp3((0.2,0.8,0.62),(0.22,0.95,0.3),sm(seg01(u,2.1,2.6)))
        pp=(0.05,0.72,2.46)
        if 1.2<=u<2.1: pp=(lerp(0.05,-0.12,sm(seg01(u,1.2,1.9))),0.72,lerp(2.46,2.32,sm(seg01(u,1.2,1.9))))
        if u>=2.1: pp=(kb[0]+0.6*(0.2)*1,0.8,kb[2]+0.62*0.6)
        walk=0.0; base=kb; yaw=0.0
        if u>=3.0: yaw=lerp(0.0,-PI/2,sm(seg01(u,3.0,3.3))); base=(kb[0]-1.6*max(0.0,u-3.2),0.0,kb[2]-0.3*sm(seg01(u,3.0,3.4))); walk=base[0]*5.0; rh=None
        if u>=3.0: pp=None
        pk=keeper(cam,head=-0.0,tilt=0.15*sm(seg01(u,1.0,1.4)),rh=lerp3((0.27,0.68,0.05),(0.15,0.62,0.7),sm(seg01(u,0.9,1.3)))*1 if u<1.9 else lerp3((0.15,0.62,0.7),(0.27,0.68,0.05),sm(seg01(u,1.9,2.4))),blink=blink(t,(31.6,)))
        L=[hero((200,200,210),base,yaw,cam,walk=walk,rh=rh,scale=0.62,lum=0.95),pk,tag_board()]
        if pp is not None: L.append(potion(pp,t,1.0))
        return dict(cam=cam,tgt=tgt,fov=56,layers=L,tag='1 G' if u<1.3 else '0 G',bubbles=[((kb[0],1.55,kb[2]),'...')] if 0.9<u<1.9 else ([((kb[0],1.55,kb[2]),'!')] if 2.3<u<3.0 else []),hud_gold=True)
    # end
    k=motion.creep(t,t0,0.0016,FPS); cam=motion.dolly((0.05,1.0,1.9),(0.0,1.3,3.35),k); tgt=(0.0,1.3,3.35)
    return dict(cam=cam,tgt=tgt,fov=34,layers=[keeper(cam,blink=blink(t,(35.6,37.0)),tilt=0.1*sm(seg01(u,0.6,1.4))),potion(PR,t,1.0),tag_board()],tag='1 G' if u<1.5 else '0 G',tag_pop=1.5)

# ======================= render =======================
RND=Renderer(W,H,fog=(20,26,40))
def lights(t,sh):
    fl=1.0+0.05*math.sin(t*9)+0.03*math.sin(t*17.5+1)
    L=[((0.0,2.2,2.4),(255,196,120),1.9*fl),((-1.6,1.7,3.7),(255,220,160),0.55),((0.0,1.6,0.8),(255,214,170),0.35)]
    dc=sh.get('door_col') or tod('day'); L.append(((-2.2,1.3,1.4),dc,0.9 if not in_flash(t) else 0.5))
    return L+sh.get('extra_lights',[])
from nightkit.look import outline   # shared since 23 Nov 2026 (was defined here)
def grade_flash(a):
    l=a.mean(axis=2,keepdims=True); a=l*0.4+a*0.6; return a*np.array([0.86,0.95,1.1])*0.95
def render_low(t):
    sh=make_shot(t); cam=Camera.look(sh['cam'],sh['tgt']); layers=[ROOM]
    if not sh['layers'] or not any(True for _ in sh['layers']): pass
    nm=shot_of(t)[0]
    if nm.startswith('door') or nm=='fb_door': dd=sh['layers'][0]; layers=[ROOM]+sh['layers']
    else:
        col=tod('cold') if in_flash(t) else tod('day'); a=HINGE_OPEN
        layers=[ROOM,door_dyn(t,col,a if not in_flash(t) else 0.0,show_light=not in_flash(t))]+sh['layers']
        if nm in('fb_party','fb_tray','fb_face'): layers[1]=door_dyn(t,tod('cold'),0.0,False)
    layers.append(motes(t))
    sh['layers']=layers
    img,vi,zb=zrender(RND,cam,layers,lights(t,sh),fov=sh['fov'],fog_start=5,fog_end=22,ambient=0.34,return_z=True)
    a=np.asarray(img).astype(np.float32); a=outline(a,zb)
    if sh.get('grade')=='flash': a=grade_flash(a)
    a=np.clip((a-118)*1.1+118,0,255)
    return Image.fromarray(a.astype(np.uint8)),vi,sh
def frame_low(t):
    img,vi,sh=render_low(t); img=post.ps1(img,levels=6); d=ImageDraw.Draw(img)
    if sh.get('tag'):
        sx,sy,z=RND.project(TAGP,vi); px=vi[7]*0.09/z; sc=max(1,min(5,int(round(px*0.55/7))))
        txt=sh['tag']; font.text(d,txt,int(sx-font.width(txt,sc)/2),int(sy-3.5*sc),(40,28,28),sc,shadow=None)
    return img,vi,sh
def finish(t):
    img,vi,sh=frame_low(t); end=seg01(t,DUR-0.6,DUR)
    if end>0: img=Image.fromarray((np.asarray(img).astype(np.float32)*(1-end)).astype(np.uint8))
    return img,vi,sh

# ======================= overlays at 1080x1920 =======================
def words_layout(lines,sc,gap_row=4):
    out=[]
    for ln in lines:
        ws=ln.split(' '); wid=sum(len(w)*6*sc for w in ws)+6*sc*(len(ws)-1)-sc; out.append((ws,wid))
    return out
def draw_cells(d,cells,o,fill_main=True):
    for (x0,y0,x1,y1,col) in cells: d.rectangle([x0-o,y0-o,x1+o,y1+o],fill=(0,0,0))
    for (x0,y0,x1,y1,col) in cells: d.rectangle([x0,y0,x1,y1],fill=col)
def text_cells(s,x,y,sc,col):
    font.check(s); C=[]
    for k,ch in enumerate(s.upper()):
        for j,row in enumerate(font.FONT[ch]):
            for i,b in enumerate(row):
                if b=='1': C.append((x+(k*6+i)*sc,y+j*sc,x+(k*6+i)*sc+sc-1,y+j*sc+sc-1,col))
    return C
def draw_caption(d,lines,hil,sc,y0,pop=1.0):
    C=[]; y=y0
    for ln,(ws,wid) in zip(lines,words_layout(lines,sc)):
        x=(W*S-wid)//2
        for w in ws:
            col=YEL if w.strip(',')in hil else WHT; C+=text_cells(w,x,y,sc,col); x+=len(w)*6*sc+6*sc
        y+=10*sc
    draw_cells(d,C,max(2,int(sc*0.5)))
def overlays(arr,t,vi,sh):
    im=Image.fromarray(arr.astype(np.uint8)); d=ImageDraw.Draw(im)
    for (a,b,lines,hil,sc) in CAPS:
        if a<=t<b:
            pop=min(1.0,(t-a)/0.12); d_y=int(250+(1-pop)*18); draw_caption(d,lines,hil,sc,d_y)
    nm=shot_of(t)[0]
    if sh.get('tray'):
        n,u=sh['tray']; C=text_cells('THEIR GOLD',56,70,4,WHT)+text_cells(f'{n} / 50',56,112,8,RED if n>=47 else WHT); draw_cells(d,C,3)
    elif sh.get('hud_gold'):
        u=t-30.5; C=text_cells('YOUR GOLD',56,70,4,WHT)+text_cells('0',56,112,8,RED if u>0.9 else WHT); draw_cells(d,C,3)
    elif not in_flash(t) and t<34.4:
        C=text_cells('SOLD AT 1 G',56,70,4,WHT)+text_cells(f'{sold(t):,}',56,112,8,YEL); draw_cells(d,C,3)
    for (P,txt) in sh.get('bubbles',[]):
        pr=RND.project(P,vi)
        if pr: sx,sy,z=pr; sc=11; bob=int(6*math.sin(t*7)); wd=len(txt)*6*sc-sc; draw_cells(d,text_cells(txt,int(sx*S-wd/2),int(sy*S-4*sc+bob),sc,YEL),4)
    for (fx,fy,txt,_) in sh.get('bubbles_screen',[]):
        sc=14; bob=int(8*math.sin(t*7)); draw_cells(d,text_cells(txt,int(fx*W*S),int(fy*H*S*0.5+bob),sc,YEL),5)
    return np.asarray(im).astype(np.float32)
def frame_final(t):
    img,vi,sh=finish(t); arr=post.upscale(img,S); return overlays(arr,t,vi,sh)
def frame(t):
    return Image.fromarray(np.clip(frame_final(t),0,255).astype(np.uint8)).resize((W,H),Image.BOX)

TEST=os.environ.get('TEST')
if TEST and __name__=='__main__':
    ts=[float(x) for x in TEST.split(',')]; ims=[Image.fromarray(np.clip(frame_final(x),0,255).astype(np.uint8)).resize((360,640),Image.LANCZOS) for x in ts]
    per=int(os.environ.get('PER','6')); rows=(len(ims)+per-1)//per; shp=Image.new('RGB',(min(per,len(ims))*362,rows*642))
    for i,im in enumerate(ims): shp.paste(im,((i%per)*362,(i//per)*642))
    shp.save(os.environ.get('TEST_OUT','test_og.png')); sys.exit()

QA=dict(fps=FPS,dur=DUR,W=W,frame=frame,scenes=[dict(id=n,t0=a,t1=b,action=n) for n,a,b in SHOTS],texts=lambda:[])

# ======================= AUDIO (no voice) =======================
def build_audio(path):
    s=Sound(DUR,loop=False,seed=71); sr=s.sr; n=s.n; t=s.t; BED=np.zeros(n); FX=np.zeros(n); MU=np.zeros(n)
    def put(buf,x,t0,v=1.0):
        i=int(t0*sr)
        if i>=n or i<0: return
        j=min(n,i+len(x)); buf[i:j]+=(x*v)[:j-i]
    def tone(buf,t0,m,d,v,dec=3.0,att=0.004,wave='sin'):
        f=440*2**((m-69)/12); tt=s.T(d); ph=2*np.pi*f*tt
        x=np.sin(ph)+0.32*np.sin(2*ph)+0.1*np.sin(3.01*ph) if wave=='mb' else np.sin(ph)
        put(buf,x*np.minimum(1,tt/att)*np.exp(-tt*dec),t0,v)
    def nb(t0,d,lo,hi,v,seed,shape=2): put(FX,s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v)
    def clink(t0,v=0.02,seed=0):
        for k,f in enumerate((3100,4200,2600)): tt=s.T(0.3); put(FX,np.sin(2*np.pi*f*(1+0.01*hsh(seed+k))*tt)*np.exp(-tt*(16+4*k)),t0+k*0.04,v*(1-0.25*k))
    def bell(t0,v=0.05):
        for f,dc in ((1568,5),(2349,7),(3136,9)): tt=s.T(1.2); put(FX,np.sin(2*np.pi*f*tt)*np.exp(-tt*dc),t0,v*(1 if f==1568 else 0.5))
    def step(t0,v=0.03,seed=0): tt=s.T(0.12); put(FX,s.filt_short(s.noise(0.12,seed),lo=200,hi=1800)*np.exp(-tt*38)+np.sin(2*np.pi*80*tt)*np.exp(-tt*30)*0.25,t0,v)
    def pop(t0,v=0.06): tt=s.T(0.1); put(FX,np.sin(2*np.pi*(380-1800*tt)*tt)*np.exp(-tt*30)+s.filt_short(s.noise(0.1,int(t0*91)),lo=800,hi=4000)*np.exp(-tt*50)*0.4,t0,v)
    def thud(t0,v=0.18): tt=s.T(0.7); put(FX,np.sin(2*np.pi*(62-20*tt)*tt)*np.exp(-tt*7)+s.filt_short(s.noise(0.7,int(t0*13)),lo=60,hi=500)*np.exp(-tt*9)*0.5,t0,v)
    def swish(t0,d=0.5,v=0.03,seed=5): nb(t0,d,500,3000,v,seed)
    # ---- bed: room tone + quiet lamp flame (never per-sample gating); cold hollow drone in the flashback
    warm=np.where((t<FLASH[0])|(t>=FLASH[1]),1.0,0.0); cold=1-warm
    sm_w=np.convolve(warm,np.ones(2400)/2400,'same'); sm_c=1-sm_w
    BED+=s.filt(s.rng.normal(0,1,n),lo=50,hi=420)*0.05*(0.7+0.3*np.sin(2*np.pi*t/7.1))*(0.35+0.65*sm_w)
    BED+=soft_fire(s,level=0.004,crackles_per_s=2.2,seed=33)*sm_w
    BED+=(np.sin(2*np.pi*55*t)+0.5*np.sin(2*np.pi*82.4*t+0.5))*0.014*sm_c
    BED+=s.filt(s.rng.normal(0,1,n),lo=300,hi=1500)*0.006*np.clip(0.5+0.5*np.sin(2*np.pi*t/5.3),0,None)*(1-0.4*sm_c)
    # ---- music box (A minor), stops in the flashback, returns in major at 27 s
    PH=[69,72,76,72,71,67,64,67]; PHM=[69,73,76,73,71,68,64,69]
    def phrase(t0,notes,v,step_=0.42):
        for i,m in enumerate(notes): tone(MU,t0+i*step_,m,1.6,v*(0.8+0.2*hsh(i,t0)),dec=3.2,wave='mb')
    phrase(0.25,PH,0.05); phrase(3.9,PH[:4],0.04); phrase(9.0,PH,0.05,0.4); phrase(12.6,PH[4:]+PH[:4],0.045,0.4)
    for k_,tt in enumerate((16.0,18.6,21.6)): tone(MU,tt,45,2.4,0.04,dec=1.5)                                   # lone low note, flashback
    phrase(27.4,PHM[:6],0.05,0.46); phrase(31.0,PHM,0.055,0.44); tone(MU,35.5,81,2.5,0.05,dec=1.4,wave='mb'); tone(MU,35.5,69,2.8,0.04,dec=1.2,wave='mb')
    # ---- hook / buys / mute
    for k_,(a,b) in enumerate(((3.6,5.4),(5.4,7.1))):
        step(a-0.3,0.025,100+k_); clink(a+0.55,0.03,seed=k_); pop(a+1.15,0.05); swish(a+0.82,0.4,0.02,seed=10+k_)
    bell(3.55,0.04); bell(5.35,0.04)
    nb(7.6,0.4,200,1400,0.02,40,1)                                                                                # shopkeeper's breath, no answer
    # ---- door montage: bell + footsteps + a ticking counter that speeds up
    for i in range(4):
        t0=9.0+0.9*i; bell(t0+0.1,0.05)
        for k_ in range(5): step(t0+0.2+k_*0.14,0.028,200+i*7+k_)
    x=9.0; tk=0
    while x<12.6:
        put(FX,np.sin(2*np.pi*1800*s.T(0.02))*np.exp(-s.T(0.02)*150),x,0.02+0.02*seg01(x,9,12.6)); x+=lerp(0.28,0.045,seg01(x,9.0,12.6)); tk+=1
    # ---- wall dolly: a quiet dust shimmer
    for k_ in range(3): tone(FX,12.8+k_*0.6,96+k_*3,0.7,0.006,dec=6)
    # ---- flashback: the tray counts 47 coins, three dull knocks on the empty slots, the potion is pulled away
    for k_ in range(47):
        tc=18.4+0.2+1.5*(k_/46.0)**0.9; clink(tc,0.012+0.006*seg01(k_,0,47),seed=k_)
    for k_ in range(3): tone(FX,20.45+k_*0.22,40,0.3,0.06,dec=9)
    swish(20.75,0.6,0.03,seed=51)
    nb(22.0,0.5,100,800,0.02,61,1); nb(22.9,0.4,100,800,0.015,62,1)                                              # head shake: cloth
    for i in range(4):
        for k_ in range(6): step(23.7+0.3*i+k_*0.19,0.018,300+i*9+k_)
    nb(25.1,0.5,300,2000,0.015,70,1)
    thud(26.15,0.22); nb(26.2,0.6,60,300,0.05,71)
    # ---- present: back to the shop (bell), hand to the wall, kid
    bell(30.55,0.05)
    for k_ in range(4): step(30.2+k_*0.15,0.02,400+k_)
    swish(31.9,0.5,0.025,seed=81); pop(32.4,0.04); tone(FX,32.9,81,0.5,0.03,dec=5); bell(31.6,0.0)
    for k_ in range(5): step(33.7+k_*0.17,0.02,500+k_)
    tone(FX,35.5,93,2.0,0.03,dec=3)                                                                                # the tag flips
    # ---- mix: silence after the door thud (1.0 s), then the shop returns
    gdoor=np.ones(n); a0=int(26.25*sr); a1=int(27.3*sr); gdoor[a0:a1]=0.0; k=int(0.15*sr); gdoor=np.convolve(gdoor,np.ones(k)/k,'same')
    bed=BED*gdoor; fx=FX; mu=MU
    s.L=bed+fx+mu; s.R=np.roll(bed,700)+np.roll(fx,150)+np.roll(mu,300); s.reverb(0.18,length=1.6,decay=3.0)
    end=np.clip((DUR-t)/0.7,0,1); s.L*=end; s.R*=end
    return s.save(path,peak=0.9)
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'one_gold.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','17','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'og_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=0,scan_dark=1.0,vignette=0.22,grain=0.9,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(frame_final(f/FPS),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
