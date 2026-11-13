"""Verification from the output file itself: specs, frame uniqueness, loop seams, spectrogram, contact sheets."""
import json, subprocess
import numpy as np
def probe(path):
    v=json.loads(subprocess.run(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration','-of','json',path],capture_output=True,text=True).stdout)['streams'][0]
    a=json.loads(subprocess.run(['ffprobe','-v','error','-select_streams','a:0','-show_entries','stream=sample_rate,channels,duration','-of','json',path],capture_output=True,text=True).stdout).get('streams',[{}])
    return dict(width=v['width'],height=v['height'],fps=v['r_frame_rate'],frames=int(v['nb_read_frames']),video_seconds=float(v['duration']),
                audio=a[0] if a else None)
def near_duplicates(path,fps=24):
    out=subprocess.run(['ffmpeg','-nostdin','-i',path,'-vf','mpdecimate,showinfo','-f','null','-'],capture_output=True,text=True).stderr
    kept=[round(float(x.split(':')[1])*fps) for x in out.split() if x.startswith('pts_time:')]
    total=probe(path)['frames']; return sorted(set(range(total))-set(kept))
def _frames(path,w=270,h=480):
    raw=subprocess.run(['ffmpeg','-nostdin','-v','error','-i',path,'-vf',f'scale={w}:{h}','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
    return np.frombuffer(raw,dtype=np.uint8).reshape(-1,h,w,3).astype(np.float32)
def loop_seam(path,w=270,h=480):
    v=_frames(path,w,h); d=np.array([np.abs(v[i+1]-v[i]).mean() for i in range(len(v)-1)])
    return dict(seam=float(np.abs(v[0]-v[-1]).mean()),median=float(np.median(d)),p90=float(np.percentile(d,90)))
def audio_seam(path,sr=48000):
    raw=subprocess.run(['ffmpeg','-nostdin','-v','error','-i',path,'-vn','-f','s16le','-ac','1','-ar',str(sr),'-'],capture_output=True).stdout
    a=np.frombuffer(raw,dtype=np.int16).astype(float)/32768
    X=np.fft.rfft(a); f=np.fft.rfftfreq(len(a),1/sr); hp=np.fft.irfft(X*(f>6000),len(a)); win=int(sr*0.01)
    e=np.array([np.sqrt((hp[i:i+win]**2).mean()) for i in range(0,len(hp)-win,win)]); wrap=np.concatenate([hp[-win//2:],hp[:win//2]])
    return dict(seam_hf=float(np.sqrt((wrap**2).mean())),median_hf=float(np.median(e)),p95_hf=float(np.percentile(e,95)))
def spectrogram(wav_or_mp4,out_png,labels=None,fmax=8000,sr=48000):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    raw=subprocess.run(['ffmpeg','-nostdin','-v','error','-i',wav_or_mp4,'-vn','-f','s16le','-ac','1','-ar',str(sr),'-'],capture_output=True).stdout
    m=np.frombuffer(raw,dtype=np.int16).astype(float)/32768
    fig,ax=plt.subplots(1,1,figsize=(14,4)); ax.specgram(m,NFFT=2048,Fs=sr,noverlap=1536,cmap='magma',vmin=-120); ax.set_ylim(0,fmax)
    for tt,l in (labels or {}).items(): ax.axvline(tt,color='cyan',lw=0.6); ax.text(tt+0.05,fmax*0.92,l,color='cyan',fontsize=7,rotation=90,va='top')
    plt.tight_layout(); plt.savefig(out_png,dpi=80); plt.close(fig); return out_png
def contact_sheet(path,frames,out_png,width=200):
    from PIL import Image
    tiles=[]
    for n in frames:
        raw=subprocess.run(['ffmpeg','-nostdin','-v','error','-i',path,'-vf',f'select=eq(n\\,{n}),scale={width}:-2','-frames:v','1','-vsync','vfr','-f','image2pipe','-vcodec','png','-'],capture_output=True).stdout
        import io; tiles.append(Image.open(io.BytesIO(raw)).convert('RGB'))
    W=sum(t.width for t in tiles)+2*len(tiles); H=max(t.height for t in tiles); sheet=Image.new('RGB',(W,H),(0,0,0)); x=0
    for t in tiles: sheet.paste(t,(x,0)); x+=t.width+2
    sheet.save(out_png); return out_png
