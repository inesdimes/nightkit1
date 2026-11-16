import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
k=Kokoro('/home/claude/tts/kokoro-v1.0.int8.onnx','/home/claude/tts/voices-v1.0.bin')
for v in ('am_michael','af_heart'):
    a,sr=k.create("Don't save here...",voice=v,speed=0.78,lang='en-us')
    # whisper: keep spectral envelope, randomize phase (removes pitch)
    n=512; hop=128; win=np.hanning(n); x=np.pad(a,(n,n)); frames=[]
    out=np.zeros(len(x)); norm=np.zeros(len(x)); rng=np.random.default_rng(3)
    for i in range(0,len(x)-n,hop):
        X=np.fft.rfft(x[i:i+n]*win); Y=np.abs(X)*np.exp(1j*rng.uniform(0,2*np.pi,len(X)))
        out[i:i+n]+=np.fft.irfft(Y)*win; norm[i:i+n]+=win**2
    w=(out/np.maximum(norm,1e-6))[n:-n]; w=w/np.max(np.abs(w))*0.9
    sf.write(f'/home/claude/tts/v4/whisper_{v}.wav',w,sr); print(v,len(w)/sr)
