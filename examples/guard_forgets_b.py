"""GUARD FORGETS - Experiment B (60 s): same story as Experiment A (guard_forgets.py) with more escalation.
Imports A's LOCKED assets (thief, guard, props, corridor, notes, meter style, emotes). 0-3.3 s are A's frames and A's
audio samples verbatim. The note writing / pinning / swap (B 34-43.9 s) is A's animation re-timed (+20 s), the cuffing is
A's cuff motion (+22.05 s) and the crown grab is A's (+23.95 s). Everything else is new B action with the same models.
Run: TEST=5,14,30 python examples/guard_forgets_b.py | PART=a:b | PART=audio (needs out/guard_forgets_a.wav)
QA:  python tools/qa/scene_qa.py examples/guard_forgets_b.py"""
import os, sys, math
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import guard_forgets as A
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Camera
from nightkit.zraster import zrender
from nightkit import post, font
from nightkit.audio import Sound
sm,seg01,lerp,lerp3,PI,Ry=A.sm,A.seg01,A.lerp,A.lerp3,A.PI,A.Ry
alerp,path3,path_yaw=A.alerp,A.path3,A.path_yaw
W,H,S,FPS=A.W,A.H,A.S,A.FPS; OUT='out'; TTS_DIR=A.TTS_DIR; SCR=A.SCR
HOOK=A.HOOK_DUR; DUR=59.6; N=int(round(DUR*FPS))
GSPOT=A.GSPOT; HIDE3=A.HIDE3; WR=20.0; CU=22.05; CR=23.95          # offsets into A for the re-used animations
VOICE=[('G5',3.55),('G1',9.5),('G6',14.05),('N2',20.9),('G7',25.6),('G8',27.9),('G9',32.5),('G10',36.75),('G11',44.6),('G4',46.6),('G12',49.2)]
RESETS=[9.0,18.6,43.8]                                             # meter hits 0 -> memory reset
P1=[HIDE3,(2.72,0,4.0),(2.72,0,2.9),(1.6,0,2.55),(0.9,0,2.5)]      # first walk-past (stops in front of the guard)
PW=[HIDE3,(2.72,0,4.0),(2.72,0,2.9),(1.6,0,2.55),(-1.05,0,2.5)]    # waving walk-past
PT=[(-1.05,0,2.5),(-1.05,0,6.0),(0.7,0,7.75)]                       # tiptoe to the crown
STATUE=(0.7,0,7.75); STATUE_YAW=math.atan2(A.PEDESTAL[0]-0.7,A.PEDESTAL[1]-7.75)
PBACK=[STATUE,(1.0,0,6.3),(2.72,0,5.0),(2.72,0,4.0),HIDE3]
PEXIT=[(0.0,0,7.6),(-0.9,0,7.1),(-0.7,0,3.0),(-1.1,0,2.2),(-2.7,0,2.4)]

def talkB(t):
    for k,t0 in VOICE:
        if k[0]=='G' and t0<=t<t0+SCR['dur'][k]: return 0.5+0.5*math.sin(t*24)
    return 0.0
def head_to(gs_base,gyaw,p,lim=1.1):
    d=np.array(p,float)-np.array(gs_base,float); a=math.atan2(d[0],d[2]); h=(a-gyaw+math.pi)%(2*math.pi)-math.pi
    return max(-lim,min(lim,h))

# ======================= thief =======================
HID=dict(yaw=PI/2,lh=(-0.2,1.0,-0.05),rh=(0.2,1.0,-0.05))
def thief_state(t):
    st=_thief(t)
    if st.get('walk') and math.hypot(st['base'][0]-A.HIDE[0],st['base'][2]-A.HIDE[1])<0.32: st=dict(st,walk=0.0)
    return st
def _thief(t):
    if t<HOOK: return A.thief_state(t)
    if t<10.5: return dict(base=HIDE3,crouch=0.15+0.05*math.sin(t*5),lean=-0.05,**HID)
    if t<11.6: return A.thief_state(t-3.5)                          # A's peek (7.0-8.1)
    if t<12.0: return dict(base=HIDE3,crouch=0.18,**HID)
    if t<14.0:                                                      # casual stroll right in front of the guard
        u=seg01(t,12.0,14.0); return dict(base=tuple(path3(P1,u)),yaw=alerp(PI/2,path_yaw(P1,u),sm(seg01(t,12.0,12.3))),walk=t*8.0 if u<1 else 0.0)
    if t<14.5: return dict(base=P1[-1],yaw=path_yaw(P1,1.0),walk=1.3,tiptoe=1.0,rh=(0.22,1.05,0.22),lh=(-0.22,1.05,0.22))     # caught mid-step
    if t<15.6:                                                      # dashes back behind the pillar
        R_=P1[::-1][:-1]; u=seg01(t,14.5,15.2); y0=path_yaw(P1,1.0)
        if t<15.2:
            yw=y0+PI*sm(seg01(t,14.5,14.85)) if t<14.85 else alerp(y0+PI,path_yaw(R_,min(u,0.85)),sm(seg01(t,14.85,15.0)))
            return dict(base=tuple(path3(R_,u)),yaw=yw,walk=t*16,run=1.0)
        return dict(base=tuple(path3([R_[-1],HIDE3],seg01(t,15.35,15.55))),yaw=alerp(path_yaw(R_,0.85),PI/2,sm(seg01(t,15.2,15.4))),**{k:v for k,v in HID.items() if k!='yaw'})
    if t<19.0: return dict(base=HIDE3,crouch=0.18+0.04*math.sin(t*5),**HID)
    if t<22.4:                                                      # walks past again, waving
        u=seg01(t,19.0,22.4); p=path3(PW,u); waving=sm(seg01(t,20.0,20.3))*(1-sm(seg01(t,21.9,22.3)))
        rh=(lerp(0.22,0.3,waving),lerp(0.82,1.55,waving),lerp(0.05,0.12+0.12*math.sin(t*14),waving))
        return dict(base=tuple(p),yaw=alerp(PI/2,path_yaw(PW,u),sm(seg01(t,19.0,19.3))),walk=t*8.0,rh=rh,head=-0.6*waving)
    if t<25.2:                                                      # tiptoes to the crown
        u=seg01(t,22.4,25.2); return dict(base=tuple(path3(PT,u)),yaw=alerp(path_yaw(PW,1.0),path_yaw(PT,u),sm(seg01(t,22.4,22.8))),walk=t*11,tiptoe=1.0)
    if t<29.8:                                                      # reaches... freezes as a 'statue' when the guard turns
        r=sm(seg01(t,25.2,25.45)); st=sm(seg01(t,25.45,25.6))
        rh=lerp3((0.22,1.05,0.22),(0.42,1.2,0.3),max(r,st)); lh=lerp3((-0.22,1.05,0.22),(-0.42,1.2,0.3),st)
        return dict(base=STATUE,yaw=alerp(path_yaw(PT,1.0),STATUE_YAW,r),walk=1.3,tiptoe=1.0,rh=rh,lh=lh)
    if t<32.4:                                                      # while the guard checks his meter: sneaks back to the pillar
        u=seg01(t,29.8,32.4); return dict(base=tuple(path3(PBACK,u)),yaw=alerp(alerp(STATUE_YAW,path_yaw(PBACK,u),sm(seg01(t,29.8,30.1))),PI/2,sm(seg01(t,32.0,32.4))),walk=t*12 if u<1 else 0.0,tiptoe=1.0)
    if t<34.0: return dict(base=HIDE3,crouch=0.15,**HID)
    if t<43.9: return A.thief_state(t-WR)                           # A's writing watch + swap + back to the pillar
    if t<51.0:
        pk=sm(seg01(t,44.4,44.8))*(1-sm(seg01(t,50.5,50.95)))
        return dict(base=HIDE3,yaw=PI/2,peek=-0.7*pk,crouch=0.15,head=-0.5*pk)
    if t<53.45: return A.thief_state(t-CR)                          # A's crown grab
    u=seg01(t,53.75,58.9)                                           # steps back from the pedestal, turns, then walks
    if u<=0: return dict(base=tuple(lerp3(A.CROWN_STAND,PEXIT[0],sm(seg01(t,53.45,53.7)))),yaw=alerp(0.0,path_yaw(PEXIT,0.02),sm(seg01(t,53.55,53.8))),crown_on=True)
    return dict(base=tuple(path3(PEXIT,u)),yaw=alerp(A.thief_state(29.44)['yaw'],path_yaw(PEXIT,max(u,0.02)),sm(seg01(t,53.45,53.8))),walk=t*8 if 0<u<1 else 0.0,crown_on=True)

# ======================= guard =======================
def guard_state(t):
    g=_guard(t)
    m=talkB(t)
    if t>=HOOK: g=dict(g,mouth=m)
    return g
def _guard(t):
    if t<HOOK: return A.guard_state(t)
    if t<9.0:                                                       # furious search, slowing down as the meter empties
        amp=sm(seg01(t,3.3,3.7))*(1-0.6*seg01(t,7.0,9.0)); h=0.9*amp*math.sin((t-3.3)*3.4)
        fist=sm(seg01(t,3.3,3.6))*(1-sm(seg01(t,8.3,8.9)))
        return dict(base=GSPOT,yaw=PI,head=h,look=(1.0 if h>0 else -1.0,0.0),wide=1.0-0.6*seg01(t,7.5,9.0),lean=0.08*fist,
                    rh=lerp3((0.32,0.9,0.06),(0.3,1.25,0.3),fist),lh=lerp3((-0.32,0.9,0.06),(-0.3,1.25,0.3),fist))
    if t<13.85:                                                     # calm, gazing at the ceiling
        r=sm(seg01(t,9.0,9.4)); return dict(base=GSPOT,yaw=PI,relax=r,look=(0.0,0.7*r),head=0.12*math.sin(t*1.3)*r)
    if t<18.6:                                                      # spots him: STOP RIGHT THERE! - tracks him to the pillar, stares
        ts=thief_state(min(t,15.4)); h=head_to(GSPOT,PI,ts['base'])
        point=sm(seg01(t,13.95,14.15))*(1-sm(seg01(t,15.3,15.7)))
        return dict(base=GSPOT,yaw=PI,head=h,wide=1.0-0.5*seg01(t,15.6,18.6),look=(0.6 if h>0 else -0.6,0.0),relax=1-sm(seg01(t,13.85,14.0)),
                    rh=lerp3((0.32,0.9,0.06),(0.3,1.35,0.5),point))
    if t<19.0:
        r=sm(seg01(t,18.6,19.0)); h0=head_to(GSPOT,PI,thief_state(15.4)['base']); return dict(base=GSPOT,yaw=PI,relax=r,head=h0*(1-r),look=(0.0,0.4*r))
    if t<25.0:                                                      # waving thief: head follows him, does nothing
        ts=thief_state(min(t,22.4)); f=sm(seg01(t,19.4,19.8))*(1-sm(seg01(t,22.3,22.9))); h=head_to(GSPOT,PI,ts['base'])*f
        return dict(base=GSPOT,yaw=PI,relax=1.0,head=h,look=(0.8*h,0.0),wide=0.3*f)
    if t<29.6:                                                      # turns around: WAIT... SOMETHING'S WRONG! stares right at the 'statue'
        tu=sm(seg01(t,25.0,25.5)); yaw=lerp(PI,2*PI,tu); h=head_to(GSPOT,2*PI,STATUE,0.6)*sm(seg01(t,26.3,26.8))
        scr=sm(seg01(t,28.9,29.1))*(1-sm(seg01(t,29.4,29.6)))
        return dict(base=GSPOT,yaw=yaw,relax=1-tu,head=h,wide=1.0*sm(seg01(t,25.4,25.6)),look=(0.0,0.0),
                    rh=(0.18,lerp(0.9,1.86,scr),lerp(0.06,0.1,scr)) if scr>0.02 else None)
    if t<31.6:                                                      # checks his memory meter (looks up at it)
        u=sm(seg01(t,29.6,29.9))*(1-sm(seg01(t,31.3,31.6))); return dict(base=GSPOT,yaw=2*PI,pitch=-0.3*u,look=(-1.0*u,1.0*u),head=0.0,wide=0.6)
    if t<34.0:                                                      # turns back; gets an idea: I'LL WRITE IT DOWN!
        tu=sm(seg01(t,31.6,32.3)); idea=sm(seg01(t,32.4,32.6))*(1-sm(seg01(t,33.5,33.9)))
        return dict(base=GSPOT,yaw=lerp(2*PI,PI,tu),rh=lerp3((0.32,0.9,0.06),(0.22,1.8,0.25),idea),wide=0.6*idea,look=(0.0,0.5*idea))
    if t<43.9: return A.guard_state(t-WR)                           # A: writes, pins, hums (memory meter runs out)
    if t<47.8:                                                      # reads the new note... YOU ARE THE THIEF...? - gasp
        rel=1-sm(seg01(t,43.9,44.2)); rd=sm(seg01(t,44.2,44.55)); gasp=sm(seg01(t,46.3,46.45)); calm=sm(seg01(t,47.3,47.8))
        return dict(base=GSPOT,yaw=PI,relax=rel,pitch=0.45*rd*(1-gasp*0.5)*(1-calm),look=(0.0,-1.0+gasp*(1-calm)),wide=gasp*(1-calm))
    if t<48.95: return A.guard_state(t-CU)                          # A: cuffs his own wrists
    pr=sm(seg01(t,49.0,49.3))                                       # proud of his arrest
    return dict(base=GSPOT,yaw=PI,rh=(0.06,1.0,0.32),lh=(-0.06,1.0,0.32),cuffs='wrists',lean=-0.1*pr,look=(0.0,0.2*pr),wide=0.3)

# ======================= shots =======================
def shot(V):
    if V<12.0: u=sm(seg01(V,HOOK,12.0)); return dict(cam=lerp3((2.55,1.45,1.25),(2.45,1.5,1.55),u),tgt=(0.9,1.15,4.3),fov=62)
    if V<16.0: u=sm(seg01(V,12.0,16.0)); return dict(cam=lerp3((-0.9,1.5,0.7),(-0.85,1.5,0.85),u),tgt=(0.7,1.15,3.3),fov=64)
    if V<19.0: u=sm(seg01(V,16.0,19.0)); return dict(cam=lerp3((2.55,1.45,1.25),(2.5,1.48,1.4),u),tgt=(0.9,1.15,4.3),fov=62)
    if V<22.6: u=sm(seg01(V,19.0,22.6)); return dict(cam=lerp3((-2.95,1.5,2.95),(-2.9,1.5,3.0),u),tgt=(0.8,1.2,3.05),fov=60)
    if V<25.4: u=sm(seg01(V,22.6,25.4)); return dict(cam=lerp3((0.9,1.7,9.9),(0.88,1.68,9.8),u),tgt=(0.0,1.2,3.6),fov=60)
    if V<31.6: u=sm(seg01(V,25.4,31.6)); return dict(cam=lerp3((1.15,1.6,9.3),(1.12,1.6,9.15),u),tgt=(0.3,1.45,3.55),fov=36)      # over the 'statue' onto the guard's face
    if V<34.0: u=sm(seg01(V,31.6,34.0)); return dict(cam=lerp3((-0.35,1.55,2.1),(-0.3,1.55,2.2),u),tgt=(0.35,1.5,3.55),fov=60)
    if V<44.75: return A.shot(V-WR)
    if V<51.0: u=sm(seg01(V,44.75,51.0)); return dict(cam=lerp3((0.0,1.4,2.15),(0.05,1.35,2.3),u),tgt=(0.35,1.2,3.55),fov=60)
    u=sm(seg01(V,51.0,DUR)); return dict(cam=lerp3((-1.0,1.65,1.3),(-1.05,1.65,1.1),u),tgt=(0.25,1.05,7.0),fov=56)

# ======================= render =======================
R=A.R
def props(V,gs,ts):
    if V>=51.0: return A.props(V-CR,gs,ts)
    Q=A.crown_quads((A.PEDESTAL[0],1.15,A.PEDESTAL[1]),0.0)
    if 34.0<=V<36.05: p=np.array(A.guard_hand(gs,1)); Q+=A.seg(p,p+np.array([-0.05,0.24,0.08]),0.025,(240,240,230),0.012)
    if gs.get('cuffs')=='hand': p=np.array(A.guard_hand(gs,1)); Q+=A.cuffs_quads(tuple(p+np.array([0,-0.08,0])),tuple(p+np.array([0.05,-0.14,0.03])))
    if gs.get('cuffs')=='wrists':
        p1=np.array(A.guard_hand(gs,1)); p2=np.array(A.guard_hand(gs,-1)); d=Ry(gs['yaw'])@np.array([0,0,-0.09]); Q+=A.cuffs_quads(tuple(p1+d),tuple(p2+d))
    return Q
def notes(V,gs,ts):
    if V<34.0: return []
    if V<43.9: return A.notes(V-WR,A.guard_state(V-WR),A.thief_state(V-WR))
    return A.notes(25.0,gs,ts)                                      # the new note stays pinned
def render(V,sh):
    cam=Camera.look(sh['cam'],sh['tgt']); gs=guard_state(V); ts=thief_state(V)
    layers=[A.HALL,A.torches(V),A.FB.prelit(A.thief(**{k:v for k,v in ts.items() if k in A.TH_KEYS}),sh['cam'],warm=0.12),
            A.FB.prelit(A.guard(**{k:v for k,v in gs.items() if k in A.GU_KEYS}),sh['cam'],warm=0.12),A.FB.prelit(props(V,gs,ts),sh['cam'],warm=0.1)]
    NQ=notes(V,gs,ts)
    for txt,c,r,u,n in NQ: layers.append(A.note_quad(c,r,u)[0])
    img,vi=zrender(R,cam,layers,A.lights(V),fov=sh['fov'],fog_start=7,fog_end=26,ambient=0.22)
    for txt,c,r,u,n in NQ: img=A.note_text(img,vi,sh['cam'],txt,c,r,u,n)
    return post.ps1(img),vi

# ======================= UI =======================
def meter_value(t):
    if t<SCR['dur']['N1']+0.25: return None,0,False
    if t<4.3: return 'ALERT',10.0,False
    if t<9.0: return 'ALERT',10*(1-seg01(t,4.3,9.0)),False
    if t<9.5: return 'ALERT',0.0,False
    if 14.0<=t<15.6: return 'ALERT',10.0,False
    if 15.6<=t<18.6: return 'ALERT',10*(1-seg01(t,15.6,18.6)),False
    if 18.6<=t<19.1: return 'ALERT',0.0,False
    if 25.5<=t<26.6: return 'ALERT',10.0,False
    if 26.6<=t<36.5: return 'MEMORY',3.0-2.4*seg01(t,26.6,36.4),29.6<=t<31.6
    if 36.5<=t<38.6: return 'MEMORY',10.0,False
    if 38.6<=t<43.8: return 'MEMORY',10*(1-seg01(t,38.6,43.8)),False
    if 43.8<=t<44.4: return 'MEMORY',0.0,False
    return None,0,False
def meter(d,V):
    lab,val,blink=meter_value(V)
    if lab is None: return
    x0,y0=6,8; full=val>=9.99; col=A.RED if (full or (blink and int(V*6)%2)) else (A.YEL if val>3 else A.GRN)
    d.rectangle([x0,y0,x0+78,y0+30],fill=(10,8,14),outline=col)
    A.otext(d,lab,x0+5,y0+4,A.WHT); num='!' if full else str(int(math.ceil(val-1e-9)))
    A.otext(d,num,x0+78-6-font.width(num,2),y0+3,col,2)
    bw=int(66*val/10.0); d.rectangle([x0+5,y0+21,x0+71,y0+26],fill=(40,30,40)); d.rectangle([x0+5,y0+21,x0+5+bw,y0+26],fill=col)
def bulb(d,vi,p3):
    p=R.project(tuple(p3),vi)
    if not p: return
    x,y=int(p[0]),int(p[1]); d.ellipse([x-6,y-12,x+6,y],fill=A.YEL,outline=(0,0,0)); d.rectangle([x-3,y,x+3,y+4],fill=A.GRY,outline=(0,0,0))
    for a in range(5): ang=-PI/2+(a-2)*0.5; d.line([x+int(9*math.cos(ang)),y-6+int(9*math.sin(ang)),x+int(13*math.cos(ang)),y-6+int(13*math.sin(ang))],fill=A.YEL)
def emotes(d,vi,V,gs,ts):
    top=np.array(A.guard_point(gs,(0,2.25,0)))
    if 14.0<=V<15.0 or 25.5<=V<26.3 or 46.3<=V<46.9: A.emote(d,vi,top,'!',A.RED)
    if 20.0<=V<22.3 or 28.4<=V<29.5: A.emote(d,vi,top,'?',A.BLU)
    if 32.4<=V<33.7: bulb(d,vi,top)
    if 39.2<=V<43.8 and int(V*2)%2==0:
        p=R.project(tuple(top+np.array([0.2,0.05*math.sin(V*3),0])),vi)
        if p: x,y=int(p[0]),int(p[1]); d.line([x,y-6,x,y+2],fill=A.WHT); d.rectangle([x-3,y+1,x,y+3],fill=A.WHT); d.line([x,y-6,x+3,y-4],fill=A.WHT)
    if 50.5<=V<51.4:                                                # victory sparkles
        for k in range(4):
            p=R.project(tuple(top+np.array([0.35*math.cos(k*1.6+V*4),0.15*math.sin(V*6+k),0])),vi)
            if p: x,y=int(p[0]),int(p[1]); d.line([x-3,y,x+3,y],fill=A.YEL); d.line([x,y-3,x,y+3],fill=A.YEL)
MISSION=57.1
def mission(d,V):
    if V<MISSION: return
    pop=sm(seg01(V,MISSION,MISSION+0.2)); y=int(lerp(-50,30,pop))
    d.rectangle([8,y,W-8,y+42],fill=(10,24,12),outline=A.GRN); d.rectangle([10,y+2,W-10,y+12],fill=(30,120,40))
    A.otext(d,'STEALTH MISSION',(W-font.width('STEALTH MISSION'))//2,y+4,A.WHT); A.otext(d,'COMPLETE',(W-font.width('COMPLETE',2))//2,y+14,A.YEL,2)
    if V>=MISSION+0.5: A.otext(d,'GUARDS DEFEATED: 0',(W-font.width('GUARDS DEFEATED: 0'))//2,y+31,A.WHT)
HIL=A.HIL|{'WHERE','GO?!','STOP','RIGHT','THERE!','MEMORY','TEN','SECONDS.','WRONG!','THIEF!','WRITE','DOWN!','NEVER','FORGET!','THIEF..?','CATCH','ME!'}
def subtitle(d,V):
    if V<HOOK: return
    cur=None
    for k,t0 in VOICE:
        if t0<=V<t0+SCR['dur'][k]+0.15: cur=k
    if cur is None: return
    name,col=A.SPK[cur[0]]; txt=SCR['text'][cur].upper().replace('...','..')
    lines=A.wrap(((name+' ') if name else '')+txt); y=266-11*(len(lines)-1)
    for ln in lines:
        xw=font.width(ln); x=(W-xw)//2; d.rectangle([x-3,y-2,x+xw+2,y+8],fill=(0,0,0)); cx=x
        for wd in ln.split(' '): A.otext(d,wd,cx,y,col if wd==name else (A.YEL if wd in HIL else A.WHT)); cx+=font.width(wd)+6
        y+=11
def frame(V):
    if V<HOOK: return A.frame(V)                                    # identical hook
    sh=shot(V); img,vi=render(V,sh); d=ImageDraw.Draw(img)
    emotes(d,vi,V,guard_state(V),thief_state(V)); meter(d,V); mission(d,V); subtitle(d,V)
    return img

# ======================= QA manifest =======================
def _th(t): return {k:v for k,v in thief_state(t).items() if k in A.TH_KEYS}
def _gu(t): return {k:v for k,v in guard_state(t).items() if k in A.GU_KEYS}
_prev={}
def _extra(t):
    out=[]; gs=guard_state(t); ts=thief_state(t)
    cur={txt:np.array(c) for txt,c,r,u,n in notes(t,gs,ts)}
    for txt,c in cur.items():
        p=_prev.get(txt)
        if p is not None and p[0]==round(t*FPS)-1 and np.linalg.norm(c-p[1])>0.25: out.append(('note',f'note "{txt}" jumps {np.linalg.norm(c-p[1]):.2f} m in one frame'))
        _prev[txt]=(round(t*FPS),c)
    if A.OLD in cur and A.NEW in cur: out.append(('note','both notes visible at once'))
    if t>=44.0 and A.OLD in cur: out.append(('note','old note visible after the swap'))
    if t>=51.0+(A.CROWN_TAKE-27.05) and t<48.95: out.append(('crown','crown taken before the guard is cuffed'))
    if t<52.8 and ts.get('crown_on'): out.append(('crown','crown off the pedestal too early'))
    for nm,st_,pt,hand_,L_ in (('thief',ts,A.thief_point,A.thief_hand,0.6),('guard',gs,A.guard_point,A.guard_hand,0.68)):
        for sx in (-1,1):
            sh_=np.array(pt(st_,(sx*(0.19 if nm=='thief' else 0.32),1.17 if nm=='thief' else 1.36,0)))
            dd=np.linalg.norm(np.array(hand_(st_,sx))-sh_)
            if dd>L_: out.append(('stretch',f'{nm} arm stretched beyond its length ({dd:.2f} m)'))
    lab,val,_=meter_value(t-1.0/FPS)
    for r_ in RESETS:
        if abs(t-r_)<0.5/FPS and not (lab is not None and val<0.5): out.append(('meter',f'meter does not show 0 at the reset ({t:.2f})'))
    return out
QA=dict(A.QA,dur=DUR,frame=frame,chars={'thief':(_th,A.thief,'crown_on',False),'guard':(_gu,A.guard,'cuffs','belt')},extra=_extra,
    camera=lambda t: (A.shot(t) if t<HOOK else shot(t))['cam'],
    scenes=[dict(id='hook (=A)',t0=0.0,t1=HOOK,action='chase; thief ducks behind the pillar; guard stops'),
            dict(id='first-reset',t0=HOOK,t1=12.0,action='WHERE DID HE GO?! meter 10->0; wind; thief peeks'),
            dict(id='stroll',t0=12.0,t1=16.0,action='thief strolls in front of the dreaming guard; STOP RIGHT THERE!; runs back'),
            dict(id='second-reset',t0=16.0,t1=19.0,action='guard stares at the pillar; meter 10->0; relaxes'),
            dict(id='wave',t0=19.0,t1=22.6,action='thief walks past waving; guard follows him with his eyes, does nothing'),
            dict(id='statue',t0=22.6,t1=31.6,action='thief tiptoes to the crown; guard turns; thief freezes; guard checks meter; thief sneaks back'),
            dict(id='idea',t0=31.6,t1=34.0,action='I WILL WRITE IT DOWN! (lightbulb)'),
            dict(id='writing (=A)',t0=34.0,t1=36.05,action='insert: ARREST THE THIEF!'),
            dict(id='pinned (=A)',t0=36.05,t1=39.0,action='pins the note; NOW I WILL NEVER FORGET!'),
            dict(id='swap (=A)',t0=39.0,t1=43.0,action='thief swaps the note by hand; memory 10->0'),
            dict(id='new-note',t0=43.0,t1=44.75,action='reset; insert: YOU ARE THE THIEF!'),
            dict(id='self-arrest',t0=44.75,t1=51.0,action='You are the thief..? I am the thief?! cuffs himself; I knew I would catch me!'),
            dict(id='crown',t0=51.0,t1=DUR,action='thief takes the crown, walks past the proud guard; MISSION COMPLETE, GUARDS DEFEATED: 0')],
    weapon_events=[('guard',47.8+0.02,'belt','hand'),('guard',47.8+0.8,'hand','wrists'),('thief',53.45,False,True)],
    texts=lambda: [(k,ln,1) for k,_ in VOICE for ln in A.wrap((A.SPK[k[0]][0]+' ' if A.SPK[k[0]][0] else '')+SCR['text'][k].upper().replace('...','..'))]
          +[('ui','GUARDS DEFEATED: 0',1),('ui','STEALTH MISSION',1),('ui','COMPLETE',2)])

TEST=os.environ.get('TEST')
if TEST and __name__=='__main__':
    ims=[frame(float(x)) for x in TEST.split(',')]; shp=Image.new('RGB',(len(ims)*182,320))
    for i,im in enumerate(ims): shp.paste(im,(i*182,0))
    shp.resize((shp.width*2,640),Image.NEAREST).save('test.png'); sys.exit()

# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as _sf
    s=Sound(DUR,loop=False,seed=41); sr=s.sr; n=s.n; M=np.zeros(n); AMB=np.zeros(n)
    def note(buf,t0,m,d,v,wave='sq',duty=0.5,dec=3.0,att=0.005):
        f=440*2**((m-69)/12); tt=s.T(d); ph=(f*tt)%1
        x=np.where(ph<duty,1.0,-1.0) if wave=='sq' else (4*np.abs(ph-0.5)-1 if wave=='tri' else np.sin(2*np.pi*ph))
        env=np.minimum(1,tt/att)*np.exp(-tt*dec); i=int(t0*sr); j=min(n,i+len(tt)); buf[i:j]+=(x*env*v)[:j-i]
    def nb(t0,d,lo,hi,v,seed,shape=2): s.place(s.filt_short(s.noise(d,seed),lo=lo,hi=hi)*np.sin(np.pi*s.T(d)/d)**shape,t0,v)
    def clank(t0,v=0.06,seed=0): tt=s.T(0.25); s.place(sum(np.sin(2*np.pi*f*tt)*np.exp(-tt*k) for f,k in ((620,14),(1500,20)))*0.4+s.filt_short(s.noise(0.25,seed),lo=2000,hi=7000)*np.exp(-tt*40),t0,v)
    def step_g(t0,v=0.05,seed=0): tt=s.T(0.14); s.place(s.filt_short(s.noise(0.14,seed),lo=150,hi=1800)*np.exp(-tt*40),t0,v); clank(t0,v*0.25,seed+500)
    def step_t(t0,v=0.025,seed=0): tt=s.T(0.06); s.place(s.filt_short(s.noise(0.06,seed),lo=600,hi=3000)*np.exp(-tt*80),t0,v)
    def alert(t0): [note(M,t0+k*0.09,m,0.12,0.05,'sq',0.5,6) for k,m in enumerate((88,93,100))]
    def beep(t0,last=False): note(M,t0,84 if not last else 72,0.07 if not last else 0.2,0.03,'sq',0.5,20 if not last else 6)
    def reset_snd(t0):                                               # memory reset: falling 'bloop' + rewind whirr
        tt=s.T(0.6); s.place(np.where(np.sin(2*np.pi*np.cumsum(900*np.exp(-tt*4)+80)/sr)>0,1.0,-1.0)*np.exp(-tt*3)*0.5,t0,0.035); nb(t0,0.4,1500,6000,0.02,int(t0*7))
    AMB+=s.filt(s.rng.normal(0,1,n),lo=60,hi=500)*0.012
    pr=np.random.default_rng(3)
    for tc in np.cumsum(pr.exponential(0.3,260)):
        if tc<DUR: i=int(tc*sr); x=np.sign(s.noise(0.01,int(tc*991)))*np.exp(-s.T(0.01)*300)*0.01; AMB[i:i+len(x)]+=x[:max(0,min(len(x),n-i))]
    def sneak(a,b,v=1.0,root=57,step=0.2):
        pat=[0,None,3,None,0,None,7,6,0,None,3,None,10,None,7,None]; k=0; tc=a
        while tc<b-1e-6:
            m=pat[k%16]
            if m is not None: note(M,tc,root+12+m,step*0.6,0.022*v,'sq',0.25,14)
            if k%2==0: note(M,tc,root-12+(0 if (k//8)%2==0 else 3),step*1.5,0.05*v,'tri',dec=6)
            if k%4==2: s.place(s.filt_short(s.noise(0.03,k),lo=6000)*np.exp(-s.T(0.03)*120),tc,0.008*v)
            k+=1; tc+=step
    def chase(a,b,v=1.0,root=64):
        k=0; tc=a
        while tc<b-1e-6:
            dt,m=A.HOOK_MOTIF[k%6]; note(M,tc,m+12,0.12,0.026*v,'sq',0.5,10)
            if k%2==0: note(M,tc,root-24+(0 if (k//6)%2==0 else -2),0.2,0.06*v,'tri',dec=5)
            if k%3==0: s.place(s.filt_short(s.noise(0.05,k),lo=80,hi=400)*np.exp(-s.T(0.05)*60),tc,0.05*v)
            k+=1; tc+=0.15
    # ---------- music + sfx (0-3.3 s is replaced by A's audio below) ----------
    chase(3.3,8.6,0.7)                                               # furious search (same chase riff, fading)
    for k in range(10): step_g(3.5+k*0.5,0.03,20+k)
    for k in range(10): beep(4.3+k*0.47,k==9)                         # countdown beeps, 10 -> 0
    reset_snd(RESETS[0]); nb(9.9,0.9,300,1500,0.02,41)
    sneak(9.5,13.9,0.6)
    for k in range(10): step_t(12.05+k*0.2,0.02,50+k)
    alert(14.0); chase(14.1,15.5,0.9)
    for k in range(5): step_t(14.55+k*0.15,0.04,60+k)
    for k in range(7): beep(15.6+k*0.5,k==6)
    reset_snd(RESETS[1])
    sneak(19.0,22.4,0.8,root=60,step=0.18)
    for k in range(9): step_t(19.05+k*0.38,0.022,70+k)
    for k in range(4): note(M,20.1+k*0.4,79 if k%2==0 else 84,0.12,0.02,'sq',0.25,10)       # cheeky 'hi!' waves
    sneak(22.4,25.0,0.9,step=0.15)
    for k in range(10): step_t(22.45+k*0.27,0.02,80+k)
    M[int(25.0*sr):int(25.5*sr)]*=np.linspace(1,0,int(0.5*sr))       # record scratch / freeze
    nb(25.05,0.25,800,5000,0.05,90); alert(25.5)
    for k in range(3): note(M,27.0+k*0.6,45-k,0.5,0.04,'tri',dec=3)  # suspense
    for k in range(6): beep(29.65+k*0.3,False) if k%2==0 else None     # meter warning
    sneak(29.8,32.3,0.7,step=0.16)
    for k in range(9): step_t(29.85+k*0.27,0.022,95+k)
    for k,m in enumerate((72,79,84)): note(M,32.45+k*0.07,m,0.25,0.035,'sq',0.25,6)        # idea 'ding'
    sneak(32.6,34.0,0.5,root=60)
    nb(34.0,0.3,1000,4000,0.03,71); nb(34.55,1.3,2500,8000,0.02,72,shape=1)                  # paper + quill
    s.place(np.sin(2*np.pi*900*s.T(0.05))*np.exp(-s.T(0.05)*60),36.45,0.04)                  # pin
    for k,m in enumerate((67,72,76)): note(M,36.5+k*0.08,m,0.2,0.03,'sq',0.25,6)            # memory refilled
    sneak(36.6,39.0,0.6,root=60)
    sneak(39.0,43.8,0.9,step=0.17)
    for k in range(6): step_t(39.05+k*0.2,0.02,110+k)
    nb(40.8,0.15,1500,6000,0.03,111); nb(41.25,0.2,500,2500,0.02,112); nb(41.65,0.2,1500,6000,0.03,113)   # rip, pouch, pin
    s.place(np.sin(2*np.pi*900*s.T(0.05))*np.exp(-s.T(0.05)*60),41.8,0.04)
    for k in range(5): step_t(42.05+k*0.18,0.02,115+k)
    for k,tt_ in enumerate((40.6,41.65,42.7)): beep(tt_,False)
    beep(43.3,False); beep(43.8,True); reset_snd(RESETS[2])           # 3 -> 2 -> 1 -> 0
    for k,m in enumerate((60,59,58,57)): note(M,46.6+k*0.18,m,0.2,0.04,'sq',0.5,6)          # dun-dun-dun
    clank(47.9,0.06,95); clank(48.6,0.1,96); clank(48.75,0.08,97)                            # click-click
    for k,(m,d) in enumerate(((67,0.12),(67,0.12),(67,0.12),(72,0.5))):                     # ridiculous victory fanfare
        tc=50.55+k*0.13; f=440*2**((m-69)/12); tt=s.T(d); x=np.where((f*tt)%1<0.5,1.0,-1.0)*(0.6+0.4*np.sin(2*np.pi*7*tt))*np.exp(-tt*2)
        s.place(s.filt_short(x,hi=2500),tc,0.04)
    sneak(51.0,MISSION,0.7,root=60,step=0.16)
    for k in range(5): step_t(51.1+k*0.25,0.025,130+k)
    for k,f in enumerate((2600,3300,4100)): tt=s.T(0.5); s.place(np.sin(2*np.pi*f*tt)*np.exp(-tt*8),52.82+k*0.06,0.03)
    for k in range(20): step_t(53.8+k*0.27,0.025,140+k)
    for k,m in enumerate((72,76,79,84)): note(M,MISSION+k*0.09,m,0.22 if k<3 else 1.2,0.04,'sq',0.25,5 if k<3 else 1.8)   # one achievement chime
    # ---------- voices ----------
    NB=np.zeros(n); duck=np.ones(n)
    for k_,t0 in VOICE:
        a,ar=_sf.read(os.path.join(TTS_DIR,'gf',f'{k_}.wav')); a=a if a.ndim==1 else a.mean(1)
        a=np.interp(np.arange(int(len(a)*sr/ar))/sr,np.arange(len(a))/ar,a)
        act=a[np.abs(a)>0.02]; a=a/(np.sqrt((act**2).mean())+1e-9)*0.2
        i=int(t0*sr); j=min(n,i+len(a)); NB[i:j]+=a[:j-i]
        duck[max(0,i-int(0.05*sr)):min(n,j+int(0.1*sr))]=0.45
    duck=np.convolve(duck,np.ones(2400)/2400,'same')
    s.L+=2.0*M*duck+AMB; s.R+=2.0*np.roll(M,240)*duck+np.roll(AMB,700)
    s.reverb(0.18,length=1.4,decay=3.5)
    pk=max(np.abs(s.L).max(),np.abs(s.R).max()); gv=pk*1.05/np.abs(NB).max()
    s.L=s.L*(0.55+0.45*duck)+NB*gv; s.R=s.R*(0.55+0.45*duck)+NB*gv
    st=np.stack([s.L,s.R],1); st=st/np.max(np.abs(st))*0.9
    a_wav,asr=_sf.read(os.path.join(OUT,'guard_forgets_a.wav')); assert asr==sr                 # A's exact hook audio
    L_=int((HOOK+0.06)*sr); seg_=a_wav[:L_].copy(); g=np.sqrt((st[L_:L_+sr]**2).mean())/np.sqrt((a_wav[L_:L_+sr]**2).mean()+1e-12); seg_*=g
    x=int(0.06*sr); w=np.ones(L_); w[-x:]=np.linspace(1,0,x); st[:L_]=st[:L_]*(1-w[:,None])+seg_*w[:,None]
    st=st/np.max(np.abs(st))*0.9; _sf.write(path,st,sr,subtype='PCM_16'); return path
if __name__=='__main__' and os.environ.get('PART')=='audio':
    print(build_audio(os.path.join(OUT,'guard_forgets_b.wav'))); sys.exit()
if __name__=='__main__' and os.environ.get('PART'):
    a,b=map(int,os.environ['PART'].split(':'))
    import subprocess
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p',os.path.join(OUT,f'gfb_{a:05d}.mp4')],stdin=subprocess.PIPE)
    vhs=post.VHS(W*S,H*S,S,grade='none',chroma=1,scan_dark=0.96,vignette=0.22,grain=1.5,band_period=1e9)
    for f in range(a,min(b,N)): p.stdin.write(vhs(post.upscale(frame(f/FPS),S),f,f/FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done',a,b); sys.exit()
