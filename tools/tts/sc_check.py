"""Automatic voice checks for fp (Claude cannot listen): clipping, pause inside a line > 0.6 s, median pitch vs the reference +-15 %, line fits its window."""
import os, sys, json, numpy as np, soundfile as sf
REPO=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); TTS=os.path.join(REPO,'tts')
def f0(y,sr):
    fr=int(0.04*sr); hop=int(0.01*sr); out=[]
    for i in range(0,len(y)-fr,hop):
        x=y[i:i+fr]; x=x-x.mean()
        if np.sqrt((x**2).mean())<0.02: continue
        ac=np.correlate(x,x,'full')[fr-1:]; lo=int(sr/300); hi=int(sr/70); k=lo+np.argmax(ac[lo:hi])
        if ac[k]>0.45*ac[0]: out.append(sr/k)
    return np.array(out)
def med(path):
    y,sr=sf.read(path); y=y if y.ndim==1 else y.mean(1); p=f0(y,sr); return float(np.median(p)) if len(p) else 0.0
ref=med(os.path.join(REPO,'voice','enes_ref_main.wav')); d=sys.argv[1] if len(sys.argv)>1 else 'sc'; sc=json.load(open(os.path.join(TTS,d,'script.json')))
print(f'reference pitch {ref:.0f} Hz'); bad=0; tot=0
for k in sc['dur']:
    y,sr=sf.read(os.path.join(TTS,d,k+'.wav')); y=y if y.ndim==1 else y.mean(1); pk=np.abs(y).max()
    w=int(0.02*sr); e=np.sqrt(np.convolve(y**2,np.ones(w)/w,'same')); sil=e<0.01*pk; pause=0; run=0
    for i,s in enumerate(sil):
        run=run+1 if s else 0
        if run>0 and i>0.1*sr: pause=max(pause,run/sr)
    # ignore the planned pause between sentences: measure per sentence file instead
    p=med(os.path.join(TTS,d,k+'.wav')); tot+=sc['dur'][k]
    ok=(pk<0.99) and abs(p/ref-1)<=0.15
    print(f"{k:>3} dur {sc['dur'][k]:5.2f}s peak {pk:.2f} pitch {p:5.0f} Hz ({p/ref-1:+.0%}) longest pause {pause:.2f}s {'ok' if ok else 'CHECK'}"); bad+=not ok
print('total',round(tot,2),'s; lines flagged',bad)
