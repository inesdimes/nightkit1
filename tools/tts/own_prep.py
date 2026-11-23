"""Prepare Enes's own recordings for a video's voice build.
  python tools/tts/own_prep.py <module: eq2|ss|mm|nw> <folder with Kayit (1).m4a ... in sentence order>
Maps the files by their number to the sentences of tools/tts/<module>.py (D order), cleans them (high-pass 80 Hz,
removes the record-button click, trims, levels), and writes $TTS_DIR/<module>_own/<key>_<i>.wav (mono, 44.1 kHz). Then: python tools/tts/<module>.py build own"""
import os, sys, re, glob, subprocess, importlib.util, shutil
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
TTS_DIR=os.environ.get('TTS_DIR',os.path.join(HERE,'..','..','tts'))
mod=sys.argv[1]; folder=sys.argv[2]; LINES='--lines' in sys.argv     # --lines: one file per LINE (Kayit (n) = line n) -> <key>_all.wav
sys.argv=['x','none']; spec=importlib.util.spec_from_file_location(mod,os.path.join(HERE,mod+'.py')); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
keys=[f'{x[0]}_all' for x in m.D] if LINES else [f'{x[0]}_{i}' for x in m.D for i,_ in enumerate(x[-1])]
files={}
for f in glob.glob(os.path.join(folder,'*')):
    g=re.search(r'\((\d+)\)',os.path.basename(f))
    if g: files[int(g.group(1))]=f
assert len(files)==len(keys),(len(files),len(keys))
out=os.path.join(TTS_DIR,mod+'_own'); os.makedirs(out,exist_ok=True)
for n,key in enumerate(keys,1):
    dst=os.path.join(out,key+'.wav')
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',files[n],'-ac','1','-ar','44100','-af','highpass=f=80','-c:a','pcm_s16le',dst],check=True)
    import numpy as np, soundfile as sf
    y,sr=sf.read(dst); fr=int(sr*0.01); nf=len(y)//fr; db=20*np.log10(np.sqrt((y[:nf*fr].reshape(nf,fr)**2).mean(1))+1e-9)
    i0=0
    while i0<nf and db[i0]<=-80: i0+=1                                 # leading digital zeros
    while i0<nf and db[i0]>-80: i0+=1                                  # the record-button click at the start, then digital silence
    i1=i0
    while i1<nf and db[i1]<-62: i1+=1                                  # first voiced frame
    last=max(j for j in range(nf) if db[j]>-66)
    a=max(0,(i1-12)*fr); b=min(len(y),(last+25)*fr); y=y[a:b].copy()
    fade=int(sr*0.015); y[:fade]*=np.linspace(0,1,fade); y[-fade:]*=np.linspace(1,0,fade)
    act=np.abs(y)>10**(-55/20); g=10**(-22/20)/np.sqrt((y[act]**2).mean()); y=np.tanh(y*g/0.9)*0.9 if np.abs(y*g).max()>0.9 else y*g
    sf.write(dst,y,sr)
    print(n,'->',key,os.path.basename(files[n]))
