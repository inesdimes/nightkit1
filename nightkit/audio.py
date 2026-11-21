"""Loop-safe sound design. With loop=True all filtering and reverb are circular and events wrap around the end,
so the last sample flows into the first. Frequencies are snapped to whole cycles per loop with cyc()."""
import wave
import numpy as np
class Sound:
    def __init__(self,duration,sr=48000,loop=True,seed=42):
        self.D,self.sr,self.loop=duration,sr,loop; self.n=int(sr*duration); self.t=np.arange(self.n)/sr
        self.L=np.zeros(self.n); self.R=np.zeros(self.n); self.rng=np.random.default_rng(seed)
    # --- helpers ---
    def T(self,d): return np.arange(int(self.sr*d))/self.sr
    def noise(self,d,seed): return np.random.default_rng(seed).normal(0,1,int(self.sr*d))
    def cyc(self,f): return round(f*self.D)/self.D if self.loop else f
    def filt(self,x,lo=None,hi=None):
        """band-limit with an FFT mask (circular over the whole buffer when x is full length)"""
        X=np.fft.rfft(x); fr=np.fft.rfftfreq(len(x),1/self.sr); m=np.ones_like(fr)
        if lo: m*=1/(1+(lo/np.maximum(fr,1e-3))**4)
        if hi: m*=1/(1+(fr/hi)**4)
        return np.fft.irfft(X*m,len(x))
    def filt_short(self,x,lo=None,hi=None):
        pad=np.concatenate([x,np.zeros(self.n-len(x))]) if len(x)<self.n else x
        return self.filt(pad,lo,hi)[:len(x)]
    def place(self,x,t0,v=1.0,pan=0.0):
        i=int(t0*self.sr); l=np.sqrt(0.5*(1-pan))*1.41; r=np.sqrt(0.5*(1+pan))*1.41
        if self.loop:
            idx=(np.arange(len(x))+i)%self.n; np.add.at(self.L,idx,x*v*l); np.add.at(self.R,idx,x*v*r)
        else:
            j=min(self.n,i+len(x)); self.L[i:j]+=x[:j-i]*v*l; self.R[i:j]+=x[:j-i]*v*r
    def bed(self,sig,v=1.0,stereo_offset=1200):
        self.L+=sig*v; self.R+=np.roll(sig,stereo_offset)*v
    def gate(self,windows,ramp=0.004):
        g=np.ones(self.n)
        for a,b in windows: g[int(a*self.sr):int(b*self.sr)]=0
        k=max(1,int(self.sr*ramp)); return np.convolve(np.concatenate([g[-k:],g,g[:k]]),np.ones(k)/k,'same')[k:-k]
    # --- beds ---
    def mains_hum(self,base=50,v=0.04):
        t=self.t; return sum(a*np.sin(2*np.pi*self.cyc(base*h)*t) for h,a in ((1,0.5),(2,0.3),(3,0.12)))*v
    def building_air(self,v=0.10): return self.filt(self.rng.normal(0,1,self.n),lo=40,hi=400)*v
    def drone(self,freqs=(41.2,43.65,61.7),v=0.022,wobble=0.15):
        t=self.t; return sum(np.sin(2*np.pi*self.cyc(f)*t+np.sin(2*np.pi*self.cyc(wobble)*t)*1.5) for f in freqs)*v
    def fluorescent(self,v=0.03): t=self.t; return np.sign(np.sin(2*np.pi*self.cyc(100)*t))*v*(0.8+0.2*np.sin(2*np.pi*self.cyc(0.35)*t))
    # --- events ---
    def crackle(self,t0,v=0.08,pan=0.1,seed=None):
        x=np.sign(self.noise(0.015,seed if seed is not None else int(t0*1000)))*np.exp(-self.T(0.015)*200); self.place(x,t0,v,pan)
    def door_slide(self,t0,d=1.6,v=0.35,seed=3):
        x=self.filt_short(self.noise(d,seed),lo=120,hi=1600)*np.sin(np.pi*self.T(d)/d)**1.5; self.place(x,t0,v)
    def thud(self,t0,f=70,v=0.25): self.place(np.sin(2*np.pi*f*self.T(0.25))*np.exp(-self.T(0.25)*16),t0,v)
    def motor(self,t0,d=2.5,v=0.12):
        mt=self.T(d); x=(np.sin(2*np.pi*(55+8*np.sin(np.pi*mt/d))*mt)*0.5+np.sign(np.sin(2*np.pi*110*mt))*0.05)*np.sin(np.pi*mt/d)**2; self.place(x,t0,v)
    def creak(self,t0,v=0.03,pan=0.0,f0=900):
        d=0.35; tt=self.T(d); self.place(np.sin(2*np.pi*(f0+300*np.sin(tt*40))*tt)*np.exp(-tt*6),t0,v,pan)
    def tick(self,t0,v=0.05): tt=self.T(0.02); self.place(np.sin(2*np.pi*1800*tt)*np.exp(-tt*150),t0,v)
    def ding(self,t0,v=0.07): tt=self.T(1.2); self.place(np.sin(2*np.pi*1046.5*tt)*np.exp(-tt*3)+0.3*np.sin(2*np.pi*2093*tt)*np.exp(-tt*5),t0,v)
    def knock(self,t0,v=1.2,pan=0.15,seed=77): x=self.filt_short(self.noise(0.12,seed),lo=60,hi=500)*np.exp(-self.T(0.12)*30); self.place(x,t0,v,pan)
    def breath(self,t0,d=0.9,v=0.09,pan=0.0,seed=99): x=self.filt_short(self.noise(d,seed),lo=300,hi=2500)*np.sin(np.pi*self.T(d)/d)**2; self.place(x,t0,v,pan)
    def music_box(self,t0,notes,step=0.32,v=0.035,reverse=True,pan=0.25):
        out=np.zeros(int(self.sr*(step*len(notes)+1.5)))
        for i,m in enumerate(notes):
            f=440*2**((m-69)/12); tt=self.T(1.4); wob=1+0.004*np.sin(2*np.pi*5*tt)
            x=(np.sin(2*np.pi*f*wob*tt)+0.35*np.sin(2*np.pi*2*f*wob*tt)+0.12*np.sin(2*np.pi*3.01*f*tt))*np.exp(-tt*3.5)
            i0=int(i*step*self.sr); out[i0:i0+len(x)]+=x
        if reverse: out=out[::-1]
        out=self.filt_short(out,lo=500,hi=3500); self.place(out/np.max(np.abs(out))*v,t0,1.0,pan)
    def poisson(self,rate=0.45,avoid=(),seed=1234):
        """irregular ticks and creaks with exponential gaps (rate per second), reproducible"""
        pr=np.random.default_rng(seed); tt=0.0
        while True:
            tt+=pr.exponential(1/rate)
            if tt>=self.D: break
            if any(a<=tt<=b for a,b in avoid): continue
            pan=pr.uniform(-0.9,0.9); g=pr.uniform(0.25,1.0)
            if pr.random()<0.6: self.place(np.sign(self.noise(0.01,int(tt*997)))*np.exp(-self.T(0.01)*300)*0.05,tt,g,pan)
            else: self.creak(tt,0.02*g,pan,f0=pr.uniform(500,1100))
    # --- finishing ---
    def reverb(self,wet=0.35,length=1.6,decay=3.2,seed=5):
        irn=int(self.sr*length); ir=np.random.default_rng(seed).normal(0,1,irn)*np.exp(-np.arange(irn)/self.sr*decay)
        ir=np.convolve(ir,np.ones(6)/6,'same'); ir/=np.abs(ir).sum()/25
        if self.loop:
            H=np.fft.rfft(np.concatenate([ir,np.zeros(self.n-irn)]))
            self.L=self.L+np.fft.irfft(np.fft.rfft(self.L)*H,self.n)*wet; self.R=self.R+np.fft.irfft(np.fft.rfft(self.R)*H,self.n)*wet
        else:
            m=self.n+irn
            for ch in ('L','R'):
                x=getattr(self,ch); setattr(self,ch,x+np.fft.irfft(np.fft.rfft(x,m)*np.fft.rfft(ir,m),m)[:self.n]*wet)
    def silence(self,a,b,level=0.06,ramp=0.06):
        s=np.ones(self.n); s[int(a*self.sr):int(b*self.sr)]=level; k=int(self.sr*ramp)
        s=np.convolve(np.concatenate([s[-k:],s,s[:k]]),np.ones(k)/k,'same')[k:-k]; self.L*=s; self.R*=s
    def save(self,path,rotate_seconds=0.0,peak=0.85):
        st=np.stack([self.L,self.R],1); st=st/np.max(np.abs(st))*peak
        if rotate_seconds: st=np.roll(st,-int(rotate_seconds*self.sr),axis=0)
        w=wave.open(path,'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(self.sr); w.writeframes((st*32767).astype(np.int16).tobytes()); w.close()
        return path

def duck_envelope(n,sr,windows,depth_db=-3.0,attack=0.05,release=0.25,pre=0.05):
    """Gain curve (length n) that dips by `depth_db` while the voice speaks. `windows` = [(t0,t1),...] in seconds, taken from
    the voice lines' real timings (key it from the script, not from the audio). Smooth edges: `attack` s down, `release` s up.
    Usage: music*duck_envelope(len(music),48000,[(t,t+dur) for ...],-4). Added 18 Nov 2026."""
    g=np.ones(n); lo=10**(depth_db/20)
    for a,b in windows: g[max(0,int((a-pre)*sr)):min(n,int(b*sr))]=lo
    k1,k2=max(1,int(attack*sr)),max(1,int(release*sr)); up=np.where(g<1)[0]
    if len(up)==0: return g
    x=g.copy()
    for i in range(1,n): x[i]=x[i-1]+(g[i]-x[i-1])/(k1 if g[i]<x[i-1] else k2)
    return x


def soft_fire(s, level=0.02, crackles_per_s=4.0, mask=None, seed=5):
    """Fire sound that is NOT digital static: a low-passed noise bed (200-1500 Hz) with a slow random
    amplitude wobble, plus a few real crackles (5-15 ms noise bursts with an exponential decay).
    Never a per-sample random gate (rng.random(n) < p): that gives single-sample clicks.
    level = RMS of the bed; mask = optional 0..1 array (length s.n) that switches it on/off."""
    sr, n = s.sr, s.n; rng = np.random.default_rng(seed)
    bed = s.filt(rng.normal(0, 1, n), lo=200, hi=1500)
    wob = s.filt(rng.normal(0, 1, n), hi=2.5); wob = 1 + 0.6 * wob / (np.abs(wob).max() + 1e-9)
    bed = bed * np.clip(wob, 0.2, None); bed *= level / (np.sqrt(np.mean(bed ** 2)) + 1e-9)
    cr = np.zeros(n); t0 = rng.exponential(1 / crackles_per_s)
    while t0 < n / sr - 0.02:
        d = rng.uniform(0.005, 0.015); k = int(d * sr); i = int(t0 * sr)
        ka = max(2, int(0.002 * sr)); ar_ = np.arange(k); burst = rng.normal(0, 1, k) * np.exp(-ar_ / (k / 4.0)) * np.minimum(1.0, ar_ / ka) * rng.uniform(0.4, 1.0)
        cr[i:i + k] += burst[:max(0, n - i)][:k]; t0 += rng.exponential(1 / crackles_per_s)
    cr = s.filt(cr, lo=600, hi=2500); cr *= level * 0.25 / (np.sqrt(np.mean(cr ** 2)) + 1e-9)
    out = bed + cr
    return out if mask is None else out * mask
