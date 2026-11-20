"""Render a nightkit short in parallel parts, concat, mux with loudnorm (PIPELINE phase 5).
  python tools/render_parts.py examples/four_phases.py --prefix fp --audio four_phases.wav --out ../renders/four_phases/x.mp4 [--parts 7]
The script must support PART=a:b (-> out/<prefix>_<a:05d>.mp4) and PART=audio (-> out/<audio>). Frame count is read from the script (N)."""
import os, sys, subprocess, argparse, importlib.util
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
ap=argparse.ArgumentParser(); ap.add_argument('script'); ap.add_argument('--prefix',required=True); ap.add_argument('--audio',required=True); ap.add_argument('--out',required=True); ap.add_argument('--parts',type=int,default=7); a=ap.parse_args()
sys.path.insert(0,os.path.dirname(os.path.abspath(a.script))); sys.path.insert(0,ROOT)
spec=importlib.util.spec_from_file_location('m',a.script); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); N=m.N
OUT=os.path.join(ROOT,'out'); os.makedirs(os.path.dirname(os.path.abspath(a.out)),exist_ok=True)
step=-(-N//a.parts); bounds=[(i,min(N,i+step)) for i in range(0,N,step)]
procs=[]
for lo,hi in bounds:
    env=dict(os.environ,PART=f'{lo}:{hi}'); procs.append(subprocess.Popen([sys.executable,a.script],env=env,cwd=ROOT))
envA=dict(os.environ,PART='audio'); pa=subprocess.Popen([sys.executable,a.script],env=envA,cwd=ROOT)
for p in procs+[pa]:
    if p.wait(): sys.exit('a part failed')
lst=os.path.join(OUT,f'{a.prefix}_list.txt'); open(lst,'w').write(''.join(f"file '{os.path.join(OUT,f'{a.prefix}_{lo:05d}.mp4').replace(chr(92),'/')}'\n" for lo,_ in bounds))
video=os.path.join(OUT,f'{a.prefix}_video.mp4')
subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-f','concat','-safe','0','-i',lst,'-c','copy',video],check=True)
subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',video,'-i',os.path.join(OUT,a.audio),'-map','0:v','-map','1:a','-c:v','copy','-af','loudnorm=I=-14:TP=-1.5','-c:a','aac','-b:a','192k','-ar','48000','-shortest','-movflags','+faststart',a.out],check=True)
print('done',a.out)
