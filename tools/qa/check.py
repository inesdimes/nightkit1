"""Final-file check (PIPELINE phase 5). One command instead of ffprobe + ebur128 by hand.
  python tools/qa/check.py <video.mp4> [--script examples/<x>.py] [--fps 24] [--size 1080x1920] [--lufs -14] [--tol 1.0]
Checks: codec h264 + aac, resolution, fps, frame count == duration*fps, (with --script) duration == the script's length,
integrated loudness within tol of the target, true peak <= -1.0 dBTP, no silent half-second (> 30 dB under the loudest one),
and determinism: the script's frame(t) rendered twice at 3 times gives identical pixels. Exit code 1 if anything fails.
Frame scan (on by default, --no-frames to skip): black frames, unplanned white frames, frozen spans >= 12 frames, unplanned
frame-difference pops. These are WARN lines (observations, a horror short may flicker or hold on purpose) and do not change the
exit code unless --strict-frames is given. With --script, the scene starts (QA['scenes'] t0) count as planned cuts."""
import os, sys, json, subprocess, argparse, re
import numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
def probe(v):
    r=subprocess.run(['ffprobe','-v','error','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,nb_frames','-show_entries','format=duration','-of','json',v],capture_output=True,text=True,check=True)
    return json.loads(r.stdout)
def loudness(v):
    r=subprocess.run(['ffmpeg','-nostdin','-i',v,'-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True).stderr
    s=r[r.rfind('Summary:'):]; I=float(re.search(r'I:\s+(-?[\d.]+) LUFS',s).group(1)); P=float(re.search(r'Peak:\s+(-?[\d.]+|-inf) dBFS',s).group(1))
    return I,P
def silent_windows(v,below=30.0):
    raw=subprocess.run(['ffmpeg','-nostdin','-v','error','-i',v,'-ac','1','-ar','8000','-f','f32le','-'],capture_output=True,check=True).stdout
    a=np.frombuffer(raw,np.float32); w=4000
    r=np.array([20*np.log10(np.sqrt((a[i:i+w]**2).mean())+1e-9) for i in range(0,len(a)-w+1,w)])
    return [i*0.5 for i,x in enumerate(r) if x-r.max()<-below]
def frame_scan(v,fps,planned=()):
    """Scan every frame at 90x160. Returns dict of lists of frame numbers (frozen: (start,end) spans)."""
    W,H=90,160
    raw=subprocess.run(['ffmpeg','-nostdin','-v','error','-i',v,'-vf',f'scale={W}:{H}:flags=area','-f','rawvideo','-pix_fmt','gray','-'],capture_output=True,check=True).stdout
    F=np.frombuffer(raw,np.uint8)[:len(raw)//(W*H)*W*H].reshape(-1,H,W); n=len(F)
    mean=F.reshape(n,-1).mean(1)/255.0
    diff=np.abs(np.diff(F.astype(np.int16),axis=0)).mean(axis=(1,2)) if n>1 else np.zeros(0)
    pl=set()
    for f in planned: pl.update(range(f-1,f+2))
    med=np.array([np.median(diff[max(0,i-8):i+9]) for i in range(len(diff))])
    pops=[i+1 for i in range(len(diff)) if diff[i]>3*med[i]+1.0 and (i+1) not in pl]
    black=[i for i in range(n) if mean[i]<0.04]
    white=[i for i in range(n) if mean[i]>0.93 and i not in pl]
    frozen=[]; st=None
    for i in range(len(diff)+1):
        if i<len(diff) and diff[i]<0.02:
            st=i if st is None else st
        else:
            if st is not None and i-st>=12: frozen.append((st,i))
            st=None
    return dict(frames=n,black=black,white=white,frozen=frozen,pops=pops)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('video'); ap.add_argument('--script'); ap.add_argument('--fps',type=float,default=24); ap.add_argument('--size',default='1080x1920')
    ap.add_argument('--lufs',type=float,default=-14.0); ap.add_argument('--tol',type=float,default=1.0)
    ap.add_argument('--no-frames',action='store_true'); ap.add_argument('--strict-frames',action='store_true'); a=ap.parse_args()
    res=[]; ok=lambda name,cond,info: res.append((name,bool(cond),info))
    p=probe(a.video); V=[s for s in p['streams'] if s['codec_type']=='video'][0]; A=[s for s in p['streams'] if s['codec_type']=='audio']
    W,H=map(int,a.size.split('x')); num,den=map(int,V['r_frame_rate'].split('/')); fps=num/den; dur=float(p['format']['duration']); nf=int(V.get('nb_frames',0))
    ok('codec',V['codec_name']=='h264' and A and A[0]['codec_name']=='aac',f"{V['codec_name']} / {A[0]['codec_name'] if A else 'no audio'}")
    ok('resolution',(V['width'],V['height'])==(W,H),f"{V['width']}x{V['height']}")
    ok('fps',abs(fps-a.fps)<1e-6,f'{fps:g}')
    ok('frames',abs(nf-round(dur*fps))<=1,f'{nf} frames, {dur:.3f} s')
    if A:
        I,P=loudness(a.video); ok('loudness',abs(I-a.lufs)<=a.tol,f'{I:.1f} LUFS (target {a.lufs:g} +/- {a.tol:g})'); ok('true peak',P<=-1.0,f'{P:.1f} dBFS')
        sw=silent_windows(a.video); ok('no silence',not sw,'none' if not sw else f'silent at {sw[:8]} s')
    planned=[]
    if a.script:
        from scene_qa import load
        m=load(a.script); planned=[int(round(sc['t0']*fps)) for sc in m.QA.get('scenes',[])]; n_exp=getattr(m,'N_OUT',None) or int(round(m.QA['dur']*m.QA['fps']))
        ok('script length',abs(nf-n_exp)<=1,f'video {nf} vs script {n_exp} frames')
        dur_s=m.QA['dur']; same=True
        for t in (dur_s*0.1,dur_s*0.5,dur_s*0.9):
            x=np.asarray(m.QA['frame'](t)); y=np.asarray(m.QA['frame'](t)); same&=bool(np.array_equal(x,y))
        ok('deterministic',same,'frame(t) twice -> identical' if same else 'frame(t) differs between two calls')
    if not a.no_frames:
        r=frame_scan(a.video,fps,planned); sp=lambda L:'none' if not L else f"{len(L)}: {L[:8]}"
        for name,L in (('black frames',r['black']),('white frames',r['white']),('frozen spans',r['frozen']),('frame pops',r['pops'])):
            good=not L; res.append(('scan: '+name,True if good else (False if a.strict_frames else 'WARN'),sp(L)))
    w=max(len(r[0]) for r in res)
    tag=lambda g:'WARN' if g=='WARN' else ('PASS' if g else 'FAIL')
    for name,good,info in res: print(f"{tag(good):<4}  {name:<{w}}  {info}")
    warn=[r for r in res if r[1]=='WARN']; bad=[r for r in res if r[1] is False]
    print(f"\n{len(res)-len(bad)-len(warn)}/{len(res)} passed"+(f", {len(warn)} warning(s)" if warn else '')); sys.exit(1 if bad else 0)
if __name__=='__main__': main()
