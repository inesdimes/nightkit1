"""2D vintage lithograph / 1940s newspaper style for nightkit (style "litho44").
The picture is printed like an old poster: separate colour PLATES (ink, red, blue, green, sepia, gold) are drawn as masks,
roughened like spread ink, slightly mis-registered, and multiplied onto an aged paper. Shading is halftone dots.
Animation is "on twos" (a new drawing every 2 frames) and outlines "boil" (tiny jitter per drawing) like hand-drawn work.
Usage: see examples/litho_pilot.py. A STYLE is just a dict of parameters, so new styles are new dicts."""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONTS=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','assets','fonts')
STYLES={
 'litho44':dict(paper=(233,214,174),edge=(201,168,118),
                plates={'ink':(42,36,30),'red':(224,54,31),'red_dark':(168,38,26),'blue':(158,194,212),'blue_dark':(93,126,144),
                        'green':(95,122,58),'sepia':(138,106,74),'gold':(217,169,58),'mast':(232,69,42)},
                misreg={'red':(2,-1),'red_dark':(2,-1),'blue':(-2,1),'blue_dark':(-2,1),'green':(1,2),'gold':(-1,-2),'sepia':(0,1),'mast':(1,0)},
                outline=4.0,wobble=1.6,halftone=9,rough=0.22,grain=4.0,stains=0.07,vignette=0.22),
}
_GRID={}
def font(name,size,variation=None):
    f=ImageFont.truetype(os.path.join(FONTS,name),size)
    if variation:
        try: f.set_variation_by_name(variation)
        except Exception: pass
    return f

class Page:
    """One frame: plates (float masks) + paper. Draw into plates, then print()."""
    def __init__(self,W,H,style='litho44',seed=0):
        self.W,self.H=W,H; self.S=STYLES[style]; self.seed=seed
        self.m={k:Image.new('L',(W,H),0) for k in self.S['plates']}
        self.d={k:ImageDraw.Draw(v) for k,v in self.m.items()}
    # ---------- geometry helpers ----------
    def wobble(self,pts,amp=None,step=10,closed=True,seed=0):
        """subdivide a polyline and jitter it (hand-drawn line); seed changes per drawing = 'boil'"""
        amp=self.S['wobble'] if amp is None else amp
        P=list(pts)+([pts[0]] if closed else []); out=[]
        r=np.random.default_rng(int(seed*7919+self.seed)%2147483647)
        for (x0,y0),(x1,y1) in zip(P,P[1:]):
            n=max(1,int(math.hypot(x1-x0,y1-y0)/step))
            for i in range(n):
                u=i/n; out.append((x0+(x1-x0)*u+r.normal(0,amp*0.6),y0+(y1-y0)*u+r.normal(0,amp*0.6)))
        if not closed: out.append(P[-1])
        return out
    def knockout(self,mask):
        """clear every plate under mask (L image): what is drawn next sits in front, on bare paper"""
        k=np.asarray(mask)>0
        for n in self.m:
            a=np.asarray(self.m[n]).copy(); a[k]=0; self.m[n]=Image.fromarray(a); self.d[n]=ImageDraw.Draw(self.m[n])
    def shape(self,pts,fill=None,outline='ink',width=None,seed=0,wob=True,solid=False):
        p=self.wobble(pts,seed=seed) if wob else list(pts)
        if solid:
            km=Image.new('L',(self.W,self.H),0); ImageDraw.Draw(km).polygon(p,fill=255); self.knockout(km)
        if fill: self.d[fill].polygon(p,fill=255)
        if outline:
            w=int(round(width or self.S['outline'])); self.d[outline].line(p+[p[0]],fill=255,width=w,joint='curve')
        return p
    def line(self,pts,plate='ink',width=None,seed=0):
        p=self.wobble(pts,closed=False,seed=seed); self.d[plate].line(p,fill=255,width=int(round(width or self.S['outline'])),joint='curve')
    def ellipse(self,cx,cy,rx,ry,fill=None,outline='ink',width=None,seed=0,rot=0.0,n=40):
        pts=[(cx+rx*math.cos(a)*math.cos(rot)-ry*math.sin(a)*math.sin(rot),cy+rx*math.cos(a)*math.sin(rot)+ry*math.sin(a)*math.cos(rot)) for a in np.linspace(0,2*math.pi,n,endpoint=False)]
        return self.shape(pts,fill,outline,width,seed)
    def blob(self,ellipses,fill='blue',shade=None,shade_level=0.5,outline='ink',width=3,seed=0):
        """a cloud-like union of ellipses [(cx,cy,rx,ry),...]: one outer outline, flat fill, halftone shade on the lower half"""
        m=Image.new('L',(self.W,self.H),0); d=ImageDraw.Draw(m)
        for i,(cx,cy,rx,ry) in enumerate(ellipses):
            pts=[(cx+rx*math.cos(a),cy+ry*math.sin(a)) for a in np.linspace(0,2*math.pi,36,endpoint=False)]
            d.polygon(self.wobble(pts,seed=seed*13+i),fill=255)
        self.knockout(m)
        if fill: self.m[fill]=Image.fromarray(np.maximum(np.asarray(self.m[fill]),np.asarray(m))); self.d[fill]=ImageDraw.Draw(self.m[fill])
        if shade:
            ys=[cy for cx,cy,rx,ry in ellipses]; y0=min(c-r for (_,c,_,r) in ellipses); y1=max(c+r for (_,c,_,r) in ellipses)
            yy=np.arange(self.H,dtype=np.float32)[:,None]*np.ones((1,self.W),np.float32); lev=np.clip((yy-(y0+y1)/2)/max(1,(y1-y0)/2),0,1)*shade_level
            self.tone(shade,m,lev,angle=45)
        if outline:
            ring=np.asarray(m.filter(ImageFilter.MaxFilter(2*int(width)//2*2+1)),np.int16)-np.asarray(m,np.int16)
            o=np.clip(ring,0,255).astype(np.uint8); self.m[outline]=Image.fromarray(np.maximum(np.asarray(self.m[outline]),o)); self.d[outline]=ImageDraw.Draw(self.m[outline])
    def text(self,s,xy,fnt,plate='ink',anchor='la',spacing=0):
        if spacing:
            x,y=xy; w=sum(fnt.getlength(c) for c in s)+spacing*(len(s)-1)
            if anchor[0]=='m': x-=w/2
            for c in s: self.d[plate].text((x,y),c,font=fnt,fill=255,anchor='l'+anchor[1]); x+=fnt.getlength(c)+spacing
        else: self.d[plate].text(xy,s,font=fnt,fill=255,anchor=anchor)
    def tone(self,plate,mask,level,angle=45.0,cell=None):
        """halftone: fill `mask` (L image or ndarray 0..1) with dots of coverage `level` (0..1 or ndarray) on `plate`"""
        cell=cell or self.S['halftone']; M=np.asarray(mask,np.float32)/(255.0 if np.asarray(mask).dtype==np.uint8 else 1.0)
        H,W=M.shape; key=(H,W,angle,cell)
        if key not in _GRID:
            y,x=np.mgrid[0:H,0:W].astype(np.float32); a=math.radians(angle)
            u=(x*math.cos(a)+y*math.sin(a))/cell; v=(-x*math.sin(a)+y*math.cos(a))/cell; _GRID[key]=np.hypot(u-np.round(u),v-np.round(v))
        d=_GRID[key]; lev=np.clip(level if np.isscalar(level) else np.asarray(level,np.float32),0,1)
        dots=(d<0.5*np.sqrt(lev)*1.25)*M
        cur=np.asarray(self.m[plate],np.float32)/255.0; self.m[plate]=Image.fromarray((np.maximum(cur,dots)*255).astype(np.uint8)); self.d[plate]=ImageDraw.Draw(self.m[plate])
    # ---------- printing ----------
    def print(self,paper,frame_seed=0):
        S=self.S; out=paper.copy(); r=np.random.default_rng(frame_seed+11)
        noise=r.random((self.H,self.W)).astype(np.float32)
        for k,col in S['plates'].items():
            m=np.asarray(self.m[k].filter(ImageFilter.BoxBlur(1)),np.float32)/255.0
            if not m.any(): continue
            m=np.clip((m-0.5+(noise-0.5)*S['rough'])*3.0+0.5,0,1)                       # ink spread: rough edges, uneven coverage
            dx,dy=S['misreg'].get(k,(0,0)); m=np.roll(np.roll(m,dy,0),dx,1)
            c=np.array(col,np.float32)/255.0; out*=1.0-m[...,None]*(1.0-c)
        out+=r.normal(0,S['grain'],out.shape[:2]).astype(np.float32)[...,None]
        return Image.fromarray(np.clip(out,0,255).astype(np.uint8))

def make_paper(W,H,style='litho44',seed=3):
    """aged paper: base colour, low-frequency stains, fibres/specks, darker edges (float array HxWx3, 0..255)"""
    S=STYLES[style]; r=np.random.default_rng(seed)
    base=np.ones((H,W,3),np.float32)*np.array(S['paper'],np.float32)
    lo=Image.fromarray((r.random((H//60+2,W//60+2))*255).astype(np.uint8)).resize((W,H),Image.BICUBIC)
    st=(np.asarray(lo,np.float32)/255.0-0.5)*2*S['stains']; base*=(1+st)[...,None]
    y,x=np.mgrid[0:H,0:W].astype(np.float32); e=np.maximum(np.abs(x/W-0.5)*2,np.abs(y/H-0.5)*2)**4
    base=base*(1-e[...,None]*S['vignette'])+np.array(S['edge'],np.float32)*(e[...,None]*S['vignette'])
    for _ in range(int(W*H/40000)):                                                            # specks (foxing)
        cx,cy=r.integers(0,W),r.integers(0,H); rr=r.integers(1,4); base[max(0,cy-rr):cy+rr,max(0,cx-rr):cx+rr]*=0.82
    return base
