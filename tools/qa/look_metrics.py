"""Look metrics for the optional ONE TAKE system (briefs/STYLE_one_take.md). Separate tool: the main pipeline does not use it.
  python tools/qa/look_metrics.py <video.mp4> [...]
Per video: motion (mean abs change per frame, 0-255, at 90x160), brightness (mean luma), contrast (mean per-frame luma std),
saturation, the share of held frames, and the opening motion (first second). Targets measured on two reference explainers:
motion >= 3, brightness >= 50, contrast >= 35 (ours before: motion 1.5-1.8, brightness 32-36, contrast 16-23)."""
import sys, subprocess
import numpy as np
def frames(v,W=90,H=160):
    raw=subprocess.run(['ffmpeg','-nostdin','-v','error','-i',v,'-vf',f'scale={W}:{H}','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
    return np.frombuffer(raw,np.uint8).reshape(-1,H,W,3).astype(np.float32)
def fps(v):
    r=subprocess.run(['ffprobe','-v','error','-select_streams','v','-show_entries','stream=r_frame_rate','-of','csv=p=0',v],capture_output=True,text=True).stdout.strip(); a,b=map(int,r.split('/')); return a/b
for v in sys.argv[1:]:
    F=frames(v); r=fps(v); d=np.abs(F[1:]-F[:-1]).mean(axis=(1,2,3)); lum=F.mean(axis=3)
    m,b,c=d.mean(),lum.mean(),lum.std(axis=(1,2)).mean(); s=(F.max(3)-F.min(3)).mean(); op=d[:int(r)].mean()
    ok=lambda x,tg:'ok' if x>=tg else 'LOW'
    print(f"{v}\n  motion {m:5.2f} ({ok(m,3)})  brightness {b:5.1f} ({ok(b,50)})  contrast {c:5.1f} ({ok(c,35)})  saturation {s:5.1f}  held {100*(d<0.15).mean():4.1f}%  opening motion {op:5.2f}")
