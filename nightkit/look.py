"""Format 3.0 helpers (23 Nov 2026, briefs/SERIES_14_DAYS.md): the shared look + camera + subtitles for every new short.
  outline()        depth outline pass (ported from examples/one_gold_potion.py; use with zrender(..., return_z=True))
  follow_group()   group framing: everybody who speaks or acts fits the frame, the subject stays in the middle third
  blend_pts()      eased entry / exit of a helper into the group framing
  orbit_dir()      slow orbit direction for a camera that never stops
  subject_screen() where the subject is on screen (QA: middle third in >= 95 % of frames)
  Subtitles        speaker-coloured subtitles at 1080x1920 (question = title card) built from tts/<name>/script.json
  text_cells / draw_cells / hud_counter   2D overlay text at full resolution"""
import math
import numpy as np
from PIL import Image, ImageDraw
from .engine import Camera
from . import font

# ------------------------------------------------------------------ look
def outline(a,zb,thr=0.10,dark=0.42,tint=(14,10,30)):
    """Darken pixels on the FAR side of a depth discontinuity (relative 1/Z jump > thr). a = float image (H,W,3), zb = 1/Z buffer."""
    z=zb; m=np.zeros(z.shape,bool)
    for sl_a,sl_b in ((np.s_[:,:-1],np.s_[:,1:]),(np.s_[:-1,:],np.s_[1:,:])):
        za,zb2=z[sl_a],z[sl_b]; rel=np.abs(za-zb2)/(np.maximum(za,zb2)+1e-9); e=(rel>thr)&(np.maximum(za,zb2)>0)
        far_a=za<zb2; mm=np.zeros(z.shape,bool); mm[sl_a]|=e&far_a; mm[sl_b]|=e&~far_a; m|=mm
    a[m]=a[m]*dark+np.array(tint)*(1-dark)*0.4
    return a

# ------------------------------------------------------------------ camera
class Path:
    """Smooth value track through keys [(t, v), ...] (v = float or tuple): Catmull-Rom with the neighbours' slope at every key, so the speed is
    continuous and NEVER drops to zero between keys (motion.Track eases to a stop at each key: that reads as a camera that halts). Holds outside."""
    def __init__(self,keys): self.k=sorted(keys,key=lambda k:k[0]); self.sc=not hasattr(self.k[0][1],'__len__')
    def _v(self,v): return np.array([v] if self.sc else v,float)
    def __call__(self,t):
        k=self.k
        if t<=k[0][0]: r=self._v(k[0][1])
        elif t>=k[-1][0]: r=self._v(k[-1][1])
        else:
            i=max(j for j in range(len(k)-1) if k[j][0]<=t); t0,v0=k[i][0],self._v(k[i][1]); t1,v1=k[i+1][0],self._v(k[i+1][1]); h=t1-t0; u=(t-t0)/h
            def slope(j):
                a=k[max(j-1,0)]; b=k[min(j+1,len(k)-1)]
                return (self._v(b[1])-self._v(a[1]))/max(1e-6,b[0]-a[0])
            m0=slope(i)*h; m1=slope(i+1)*h
            r=(2*u**3-3*u**2+1)*v0+(u**3-2*u**2+u)*m0+(-2*u**3+3*u**2)*v1+(u**3-u**2)*m1
        return float(r[0]) if self.sc else tuple(float(x) for x in r)
def orbit_dir(yaw,pitch):
    """unit vector from the target towards the camera (yaw 0 = camera on the -z side looking +z, positive yaw swings it to +x)"""
    return np.array([math.sin(yaw)*math.cos(pitch),math.sin(pitch),-math.cos(yaw)*math.cos(pitch)])
def blend_pts(pts,anchor,w):
    """pull a helper's points towards the subject by (1-w): w = 0 the helper does not count yet, w = 1 fully in the group"""
    a=np.array(anchor,float); return [tuple(a+(np.array(p,float)-a)*w) for p in pts]
def _screen(cam,fov,W,H,P):
    cx,cy,cz,yaw,pitch=cam; ca,sa,cp,sp=math.cos(yaw),math.sin(yaw),math.cos(pitch),math.sin(pitch); fpx=W/(2*math.tan(math.radians(fov)/2))
    p=np.asarray(P,float)-np.array([cx,cy,cz]); X=ca*p[:,0]-sa*p[:,2]; Z=sa*p[:,0]+ca*p[:,2]; Y=cp*p[:,1]-sp*Z; Z2=sp*p[:,1]+cp*Z
    Z2=np.maximum(Z2,1e-3); return W/2+fpx*X/Z2,H/2-fpx*Y/Z2
def follow_group(subject,others,vdir,fov,W,H,d_min=2.0,d_max=16.0,margin=0.13,third=0.16,lift=0.0):
    """Camera (pos, target) for a group shot. subject / others: lists of 3D points (feet, hips, head, hands, held props).
    The target slides from the subject towards the group centre as far as the subject stays inside the middle third
    (|x - 0.5| <= third); the distance is the smallest one (>= d_min) that keeps every point inside the margins.
    Continuous in the inputs (bisection, no discrete steps), so a helper that enters or leaves gives an eased re-frame."""
    S=np.asarray(subject,float); A=S if not others else np.vstack([S,np.asarray(others,float)])
    sc=S.mean(0); gc=(A.min(0)+A.max(0))/2; vdir=np.asarray(vdir,float); vdir=vdir/np.linalg.norm(vdir)
    sc_pt=sc[None,:]
    def cam_for(b,d):
        tgt=sc+(gc-sc)*b+np.array([0,lift,0]); pos=tgt+vdir*d; return Camera.look(tuple(pos),tuple(tgt)),pos,tgt
    def ok(b,d):
        cam,_,_=cam_for(b,d); x,y=_screen(cam,fov,W,H,A); xs,_=_screen(cam,fov,W,H,sc_pt)
        return (x.min()>=margin*W and x.max()<=(1-margin)*W and y.min()>=margin*H*0.6 and y.max()<=(1-margin*0.6)*H and abs(xs[0]/W-0.5)<=third)
    def dist(b):
        if ok(b,d_min): return d_min
        if not ok(b,d_max): return None
        lo,hi=d_min,d_max
        for _ in range(14):
            mid=(lo+hi)/2
            if ok(b,mid): hi=mid
            else: lo=mid
        return hi
    def cost(b):
        d=dist(b); return (1e9 if d is None else d)-0.05*b
    lo,hi=0.0,1.0                                   # ternary search: the blend with the smallest distance (a closer, bigger subject) wins
    for _ in range(14):
        m1=lo+(hi-lo)/3; m2=hi-(hi-lo)/3
        if cost(m1)<=cost(m2): hi=m2
        else: lo=m1
    b=(lo+hi)/2
    for cand in (0.0,1.0):
        if cost(cand)<cost(b): b=cand
    d=dist(b) or d_max
    _,pos,tgt=cam_for(b,d); return tuple(pos),tuple(tgt)
def smooth_shot(fn,t,cuts,half=0.45,n=13):
    """Temporal smoothing of a camera shot (dict with cam, tgt, fov): triangular average of fn over t +- half, never across a hard cut
    (cuts = times where the shot changes on purpose). Removes the jumps that group framing makes when a helper enters quickly. Deterministic in t."""
    lo=max([c for c in cuts if c<=t+1e-9],default=-1e9); hi=min([c for c in cuts if c>t+1e-9],default=1e9)
    acc=None; wsum=0.0
    for i in range(n):
        u=2*i/(n-1)-1; tt=min(max(t+half*u,lo),hi-1/48); w=1-abs(u)+0.05; sh=fn(tt)
        v=(np.array(sh['cam']),np.array(sh['tgt']),sh['fov'])
        acc=tuple(a*w for a in v) if acc is None else tuple(a+b*w for a,b in zip(acc,v)); wsum+=w
    return dict(cam=tuple(acc[0]/wsum),tgt=tuple(acc[1]/wsum),fov=float(acc[2]/wsum))
def subject_screen(cam_pos,tgt,fov,W,H,pts):
    """(x, y) of the mean of pts on screen, as fractions of the frame"""
    cam=Camera.look(cam_pos,tgt); x,y=_screen(cam,fov,W,H,np.asarray(pts,float)[None,:] if np.ndim(pts)==1 else np.asarray(pts,float))
    return float(x.mean()/W),float(y.mean()/H)

# ------------------------------------------------------------------ 2D text at full resolution
def text_cells(s,x,y,sc,col):
    font.check(s); C=[]
    for k,ch in enumerate(s.upper()):
        for j,row in enumerate(font.FONT[ch]):
            for i,b in enumerate(row):
                if b=='1': C.append((x+(k*6+i)*sc,y+j*sc,x+(k*6+i)*sc+sc-1,y+j*sc+sc-1,col))
    return C
def draw_cells(d,cells,o):
    for (x0,y0,x1,y1,col) in cells: d.rectangle([x0-o,y0-o,x1+o,y1+o],fill=(0,0,0))
    for (x0,y0,x1,y1,col) in cells: d.rectangle([x0,y0,x1,y1],fill=col)
def hud_counter(d,label,value,col,x=56,y=70):
    """the one HUD counter: small label over a big number (1080x1920 pixels)"""
    draw_cells(d,text_cells(label,x,y,4,(246,242,230))+text_cells(str(value),x,y+42,8,col),3)

# ------------------------------------------------------------------ subtitles
class Subtitles:
    """Speaker-coloured subtitles at 1080x1920 from a voice build (tools/tts/multi.py). Line key '1' (the question) is a centred title card
    with an outline and no box; everything else is a roomy box near the bottom. colours: {speaker: (r,g,b)}; hil: words drawn in `hilcol`."""
    SUB_F=7.0; ADV=6.9
    def __init__(self,scr,lines,W,H,S,colours,hil=(),hilcol=(255,210,60),white=(242,238,226),title_key='1',n=17,card_y=0.34,card_sc=9.0,card_n=14):
        self.W,self.H,self.S=W,H,S; self.card_y=card_y; self.card_sc=card_sc; self.col=colours; self.hil=set(hil); self.hilcol=hilcol; self.white=white; self.title=title_key; self.items=[]
        for k,t0 in lines:
            for i,(a,b,tx) in enumerate(scr['sent'][k]):
                nxt=scr['sent'][k][i+1][0] if i+1<len(scr['sent'][k]) else b+(0.6 if k==title_key else 0.25)
                self.items.append((t0+a-0.03,t0+nxt-0.02,self._rows(tx,card_n if k==title_key else n),k,scr.get('spk',{}).get(k,'N')))
    @staticmethod
    def _rows(text,n=17):
        out=[]; c=[]
        for w_ in text.split():
            if len(' '.join(c+[w_]))>n and c: out.append(c); c=[w_]
            else: c.append(w_)
        return out+[c]
    def _tw(self,wd,sc): return len(wd)*self.ADV*sc
    def at(self,t):
        """(overlay RGB image, mask) at 1080x1920 or None"""
        W,H,S=self.W,self.H,self.S
        for a,b,rows,key,spk in self.items:
            if a<=t<b:
                card=(key==self.title); sc=self.card_sc if card else self.SUB_F; lh=(12.5 if card else 12.8)*sc
                lines=[' '.join(r) for r in rows]; wmax=max(self._tw(l,sc) for l in lines)-(self.ADV-6)*sc
                padx=5.5*sc; pady=3.6*sc; w=wmax+2*padx; h=(len(lines)-1)*lh+7*sc+2*pady
                x0=(W*S-w)/2; y0=(H*S*self.card_y-h/2) if card else (H*S-130-h)
                ov=Image.new('RGB',(W*S,H*S),(0,0,0)); m=Image.new('L',(W*S,H*S),0); do=ImageDraw.Draw(ov); dm=ImageDraw.Draw(m)
                if not card: dm.rectangle([round(x0),round(y0),round(x0+w)-1,round(y0+h)-1],fill=255)
                o=max(2,round(sc*0.55)); cells=[]; base=self.col.get(spk,self.white)
                for i,r in enumerate(rows):
                    lw=self._tw(' '.join(r),sc)-(self.ADV-6)*sc; x=x0+(w-lw)/2
                    for wd in r:
                        hot=wd.upper().strip(',!?:.') in self.hil or wd.upper() in self.hil; col=self.hilcol if (hot and spk=='N') else base; font.check(wd)
                        for k_,ch in enumerate(wd.upper()):
                            for j,row in enumerate(font.FONT[ch]):
                                for i2,bit in enumerate(row):
                                    if bit=='1': X=x+(k_*self.ADV+i2)*sc; Y=y0+pady+i*lh+j*sc; cells.append((round(X),round(Y),round(X+sc)-1,round(Y+sc)-1,col))
                        x+=self._tw(wd,sc)+self.ADV*sc
                if card:
                    for bx in cells: dm.rectangle([bx[0]-o,bx[1]-o,bx[2]+o,bx[3]+o],fill=255)
                for bx in cells: do.rectangle(bx[:4],fill=bx[4]); dm.rectangle(bx[:4],fill=255)
                return ov,m
        return None
    def apply(self,arr,t):
        """paste onto a full-resolution float array (H*S, W*S, 3)"""
        so=self.at(t)
        if so: m=np.asarray(so[1])>0; arr[m]=np.asarray(so[0])[m].astype(np.float32)
        return arr
