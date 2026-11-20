import os, numpy as np, soundfile as sf
REPO=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def f0(y,sr):
    fr=int(0.04*sr); hop=int(0.01*sr); out=[]
    for i in range(0,len(y)-fr,hop):
        x=y[i:i+fr]; x=x-x.mean()
        if np.sqrt((x**2).mean())<0.02: continue
        ac=np.correlate(x,x,'full')[fr-1:]; lo=int(sr/300); hi=int(sr/70); k=lo+np.argmax(ac[lo:hi])
        if ac[k]>0.45*ac[0]: out.append(sr/k)
    return np.array(out)
_y,_sr=sf.read(os.path.join(REPO,'voice','enes_ref_main.wav')); _y=_y if _y.ndim==1 else _y.mean(1)
REF=float(np.median(f0(_y,_sr)))
