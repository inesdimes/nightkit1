import soundfile as sf, numpy as np, subprocess, json
from scipy.signal import fftconvolve, butter, sosfilt
import os, tempfile
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','tts'))   # Kokoro models + generated voice lines live here
SR=48000
PLAN={1:(0.12,1.0),2:(1.52,1.05),3:(5.7,1.0),4:(9.75,1.0),5:(14.3,1.0),6:(19.4,1.05),7:(23.85,1.0),8:(28.62,1.18),9:(31.0,1.12),10:(32.25,1.12),
      11:(33.62,1.12),12:(36.1,1.15),13:(37.62,1.0),14:(38.88,1.05),15:(41.0,1.1),16:(43.6,1.05),17:(48.7,1.0),18:(52.28,1.1),19:(53.9,1.2),20:(56.1,1.0)}
CRYSTAL={1,2,17,18,19}          # spoken from inside the crystal
ECHOED={9,10,11,13}             # the copy's "shadow" voice answers
TXT=[x[2] for x in json.load(open(f'{TTS_DIR}/v5/script.json'))]+["Don't save here..."]
def ff(src,dst,af):
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',src,'-af',af,'-ar',str(SR),'-ac','1',dst],check=True)
def rd(p): a,_=sf.read(p); return a if a.ndim==1 else a.mean(1)
def lp(x,f): return sosfilt(butter(4,f,'low',fs=SR,output='sos'),x)
def hp(x,f): return sosfilt(butter(2,f,'high',fs=SR,output='sos'),x)
def ir(length,decay,seed,bright=5000):
    r=np.random.default_rng(seed); t=np.arange(int(length*SR))/SR; n=r.normal(0,1,len(t))*np.exp(-t*decay)
    n=lp(n,bright); n[:int(0.012*SR)]*=np.linspace(0,1,int(0.012*SR)); return n/np.sqrt(np.sum(n**2))
IR_L=ir(2.0,3.2,1); IR_R=ir(2.0,3.2,2)
def pad(x,n): return np.pad(x,(0,max(0,n-len(x))))[:n]
out=[]
for i in range(1,21):
    t0,tempo=PLAN[i]; src=f'clean/K{i}.wav'
    if i==20:
        base='afftdn=nr=24:nf=-62,highpass=f=250,lowpass=f=9000,volume=24dB,acompressor=threshold=-28dB:ratio=5:attack=3:release=120:makeup=6'
        ff(src,'fx/w0.wav',base+',rubberband=pitch=0.94')
        ff(src,'fx/w1.wav',base+',rubberband=pitch=0.84')
        ff(src,'fx/w2.wav',base+',rubberband=pitch=1.07')
        w0,w1,w2=rd('fx/w0.wav'),rd('fx/w1.wav'),rd('fx/w2.wav'); n=int(len(w0)+2.4*SR)
        L=pad(w0,n)+0.55*np.roll(pad(w1,n),int(0.17*SR))+0.35*np.roll(pad(w2,n),int(0.41*SR))
        R=pad(w0,n)+0.35*np.roll(pad(w1,n),int(0.29*SR))+0.55*np.roll(pad(w2,n),int(0.23*SR))
        L=L+0.75*fftconvolve(L,IR_L)[:n]; R=R+0.75*fftconvolve(R,IR_R)[:n]
    else:
        base=f'afftdn=nr=10:nf=-65,highpass=f=85,rubberband=tempo={tempo}:pitch=0.87:formant=shifted,acompressor=threshold=-26dB:ratio=4:attack=5:release=160:makeup=8,equalizer=f=130:t=q:w=1:g=3,equalizer=f=3000:t=q:w=1.5:g=2.5,equalizer=f=7500:t=q:w=1:g=-3'
        ff(src,'fx/m.wav',base); ff(src,'fx/s.wav',base.replace('pitch=0.87','pitch=0.435'))
        m=rd('fx/m.wav'); s=lp(rd('fx/s.wav'),900); s=pad(s,len(m))
        v=m+0.16*s                                                     # sub-octave shadow under the voice
        v=np.tanh(2.2*v/ (np.max(np.abs(v))+1e-9))/np.tanh(2.2)        # warm drive
        n=int(len(v)+2.2*SR); v=pad(v,n)
        if i in CRYSTAL:                                               # trapped: glassy comb resonance + muffled
            d=int(0.0047*SR); c=v.copy()
            for k in range(1,7): c[d*k:]+=v[:-d*k]*(0.62**k)
            v=0.55*lp(v,4200)+0.45*hp(c,300)/ (np.max(np.abs(c))+1e-9)*np.max(np.abs(v))
        L=v.copy(); R=v.copy()
        if i in ECHOED:                                                # the copy's voice right behind his own
            ff(src,'fx/e.wav',base.replace('pitch=0.87','pitch=0.83')); e=pad(lp(rd('fx/e.wav'),3500),n)
            R+=0.42*np.roll(e,int(0.085*SR)); L+=0.12*np.roll(e,int(0.14*SR))
        L+=0.3*np.roll(v,int(0.11*SR)); R+=0.24*np.roll(v,int(0.13*SR))    # stone slapback
        wet=0.55 if i in CRYSTAL else 0.42
        L=L+wet*fftconvolve(L,IR_L)[:n]; R=R+wet*fftconvolve(R,IR_R)[:n]
    pk=max(np.abs(L).max(),np.abs(R).max()); L/=pk; R/=pk
    nz=np.where(np.abs(L)+np.abs(R)>0.003)[0]; L=L[:nz[-1]+1]; R=R[:nz[-1]+1]
    sf.write(f'fx/F{i}.wav',np.stack([L,R],1),SR)
    dry=len(rd(src))/SR/tempo
    out.append([f'F{i}',t0,TXT[i-1],round(dry,2)])
    print(i,t0,'speech %.2f -> ends %.2f'%(dry,t0+dry),'| tail file %.2f'%(len(L)/SR),TXT[i-1])
json.dump(out,open('fx/script.json','w'))
