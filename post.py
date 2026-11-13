"""PS1 colour reduction, upscaling, VHS wear, colour grading, full-resolution text/texture compositing and encoding.
Every time-dependent effect takes the loop length so looping videos stay seamless."""
import subprocess
import numpy as np
from PIL import Image
_BAY=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]])/16.0-0.5
def ps1(img,levels=8):
    """15-bit-ish colour with ordered dithering (do this at the low internal resolution)."""
    a=np.asarray(img).astype(np.float32); H,W=a.shape[:2]
    b=np.tile(_BAY,(H//4+1,W//4+1))[:H,:W]
    return Image.fromarray(np.clip(np.round((a+b[...,None]*levels)/levels)*levels,0,255).astype(np.uint8))
def upscale(img,S): return np.asarray(img).repeat(S,0).repeat(S,1).astype(np.float32)
GRADES=dict(none=np.eye(3,dtype=np.float32),
            sick_green=np.array([[0.86,0.10,0.04],[0.06,0.90,0.04],[0.05,0.10,0.80]],dtype=np.float32),
            cold_blue=np.array([[0.85,0.05,0.10],[0.05,0.90,0.05],[0.05,0.08,0.95]],dtype=np.float32))
class VHS:
    """Full-resolution post: grade, chroma shift, scanlines, vignette, grain (cycled), one tracking band per band_period."""
    def __init__(self,W,H,S,grade='none',chroma=2,scan_dark=0.93,vignette=0.42,grain=3.5,band_period=20.0,seed=3):
        r=np.random.default_rng(seed); yy=np.arange(H)[:,None]; xx=np.arange(W)[None,:]
        self.W,self.H,self.chroma,self.band_period=W,H,chroma,band_period
        self.G=GRADES[grade] if isinstance(grade,str) else grade
        self.mask=(np.clip(1-vignette*(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2),0.45,1)*np.where(yy%S<1,scan_dark,1.0))[...,None].astype(np.float32)
        self.noise=[r.normal(0,grain,(H,W,1)).astype(np.float32) for _ in range(6)]
        self.rng=np.random.default_rng(seed+1)
    def __call__(self,a,f,t,glitch=False):
        a=a@self.G.T; o=a.copy(); c=self.chroma
        if c: o[:,c:,0]=a[:,:-c,0]; o[:,:-c,2]=a[:,c:,2]
        if glitch:
            for _ in range(6):
                y0=self.rng.integers(0,self.H-50); h=self.rng.integers(6,50); o[y0:y0+h]=np.roll(o[y0:y0+h],self.rng.integers(-30,30),axis=1)
        by=int(((t%self.band_period)/self.band_period)*(self.H+400))-200
        if 0<by<self.H-10: o[by:by+10]=o[by:by+10]*0.9+12
        return np.clip(o*self.mask+self.noise[f%6],0,255).astype(np.uint8)
def _homography(src,dst):
    A=[];B=[]
    for (x,y),(u,v) in zip(src,dst):
        A.append([x,y,1,0,0,0,-u*x,-u*y]);B.append(u); A.append([0,0,0,x,y,1,-v*x,-v*y]);B.append(v)
    return np.linalg.solve(np.array(A,float),np.array(B,float))
def map_texture(img,corners,tex,resample=Image.BILINEAR):
    """Paste tex onto img inside the quad corners [TL,TR,BR,BL] (image pixels, as the viewer sees them)."""
    W,H=img.size; w,h=tex.size; co=tuple(_homography(corners,[(0,0),(w,0),(w,h),(0,h)]))
    img.paste(tex.transform((W,H),Image.PERSPECTIVE,co,resample),(0,0),Image.new('L',(w,h),255).transform((W,H),Image.PERSPECTIVE,co,resample))
    return img
class Encoder:
    """with Encoder('out.mp4',1080,1920,'audio.wav',fps=24,seconds=20) as enc: enc.write(uint8_array)"""
    def __init__(self,path,W,H,audio=None,fps=24,seconds=None,crf=19):
        cmd=['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','-']
        if audio: cmd+=['-i',audio]
        cmd+=['-c:v','libx264','-crf',str(crf),'-preset','medium','-pix_fmt','yuv420p','-r',str(fps)]
        if audio: cmd+=['-c:a','aac','-b:a','192k','-ar','48000']
        if seconds: cmd+=['-t',str(seconds)]
        cmd+=['-movflags','+faststart',path]; self.cmd=cmd
    def __enter__(self): self.p=subprocess.Popen(self.cmd,stdin=subprocess.PIPE); return self
    def write(self,arr): self.p.stdin.write(np.ascontiguousarray(arr,dtype=np.uint8).tobytes())
    def __exit__(self,*a):
        self.p.stdin.close(); self.p.wait()
        if self.p.returncode: raise RuntimeError('ffmpeg failed')
