"""Scare-moment generator: outages that move a figure only while it is dark, plus overlay effects."""
import random, math
import numpy as np
from PIL import Image, ImageDraw, ImageChops, ImageFilter
class Outages:
    def __init__(self,windows): self.windows=sorted(windows)
    def on(self,t): return not any(a<=t<b for a,b in self.windows)
    def index(self,t):
        """number of outages that have fully ended by time t"""
        return sum(1 for a,b in self.windows if t>=b)
def plan_outages(seed,t_start,t_end,count,min_len=0.12,max_len=0.26,jitter=0.25):
    """Irregular but controlled outage schedule between t_start and t_end (reproducible from the seed)."""
    r=random.Random(seed); gap=(t_end-t_start)/count; out=[]
    for i in range(count):
        a=t_start+i*gap+r.uniform(0,gap*jitter); out.append((round(a,3),round(a+r.uniform(min_len,max_len),3)))
    return out
def creeping_positions(start,end,count,presence=(0.25,0.9)):
    """Positions from far (start) to near (end), plus how solid the figure reads at each step."""
    out=[]
    for i in range(count):
        u=i/(count-1) if count>1 else 1
        out.append((start[0]+(end[0]-start[0])*u,start[1]+(end[1]-start[1])*u,presence[0]+(presence[1]-presence[0])*u))
    return out
class CreepWhenDark:
    """The series rule: it only moves when the lights go out. Visible from appear_after outage onward until hide_at."""
    def __init__(self,outages,positions,appear_after=0,hide_at=None):
        self.o=outages; self.pos=positions; self.k0=appear_after; self.hide=hide_at
    def state(self,t):
        if self.hide is not None and t>=self.hide: return None
        if not self.o.on(t): return None
        k=self.o.index(t)-1-self.k0
        if k<0: return None
        return self.pos[min(k,len(self.pos)-1)]
def reflection(img,rect,strength=0.45,x_frac=0.62,blur=2):
    """Faint head-and-shoulders silhouette darkening inside rect (x0,y0,x1,y1) - e.g. a reflection on metal or glass."""
    W,H=img.size; x0,y0,x1,y1=rect; hh=y1-y0; cx=x0+(x1-x0)*x_frac
    ov=Image.new('L',(W,H),0); od=ImageDraw.Draw(ov)
    od.ellipse([cx-hh*0.09,y0+hh*0.08,cx+hh*0.09,y0+hh*0.27],fill=255)
    od.polygon([(cx-hh*0.2,y0+hh*0.3),(cx+hh*0.2,y0+hh*0.3),(cx+hh*0.17,y1),(cx-hh*0.17,y1)],fill=255)
    mask=Image.new('L',(W,H),0); ImageDraw.Draw(mask).rectangle([x0,y0,x1,y1],fill=255)
    ov=ImageChops.multiply(ov.filter(ImageFilter.GaussianBlur(blur)),mask)
    a=np.asarray(img).astype(np.float32); m=np.asarray(ov).astype(np.float32)[...,None]/255*strength
    return Image.fromarray((a*(1-m)).astype(np.uint8))
def shake(t,t0,dur,amp_px=3,seed=0):
    if not (t0<=t<t0+dur): return (0,0)
    r=random.Random(int(t*1000)+seed); k=1-(t-t0)/dur; return (r.uniform(-amp_px,amp_px)*k,r.uniform(-amp_px,amp_px)*k)
