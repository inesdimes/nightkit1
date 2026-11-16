import soundfile as sf, numpy as np, subprocess, json
SR=48000
def env_db(a,w=0.02):
    n=int(w*SR); e=np.sqrt(np.convolve(a**2,np.ones(n)/n,'same')); return 20*np.log10(e+1e-9)
for i in range(1,21):
    a,sr=sf.read(f'raw/K{i}.wav'); a=a[int(0.14*SR):]                     # drop the record-button click
    db=env_db(a); floor=np.percentile(db,15); thr=floor+(12 if i==20 else 16)
    on=db>thr
    # bridge tiny gaps, drop tiny blips
    idx=np.where(on)[0]; s0,s1=idx[0],idx[-1]
    # shorten long pauses inside the line (> 0.42 s -> 0.38 s)
    keep=np.ones(len(a),bool); k=s0; maxgap=int(0.26*SR)
    while k<s1:
        if not on[k]:
            j=k
            while j<s1 and not on[j]: j+=1
            if j-k>int(0.3*SR): keep[k+maxgap//2:j-maxgap//2]=False
            k=j
        else: k+=1
    a2=a[max(0,s0-int(0.06*SR)):s1+int(0.18*SR)]; kp=keep[max(0,s0-int(0.06*SR)):s1+int(0.18*SR)]
    a2=a2[kp]; f=int(0.01*SR); a2[:f]*=np.linspace(0,1,f); a2[-4*f:]*=np.linspace(1,0,4*f)
    sf.write(f'clean/K{i}.wav',a2,SR)
    print(i,'floor %.0f dB'%floor,'len %.2f -> %.2f'%(len(a)/SR,len(a2)/SR))
