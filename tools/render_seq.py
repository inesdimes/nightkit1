"""Render a nightkit short as separate SEQUENCES (Enes, 26 Nov 2026: at most 5 per video, so a fix re-renders only the sequence
it touches; cheaper and faster). The script defines SEQS = [(name, first_frame, end_frame), ...] and supports PART=a:b /
PART_PREFIX / PART=audio like every example.
  python tools/render_seq.py examples/bridge_troll.py --prefix bt --seqs s1,s3        # -> ../renders/<project>/seq/<name>.mp4
  python tools/render_seq.py examples/bridge_troll.py --prefix bt --master out.mp4    # concat all sequences + PART=audio + x1.2 master
  --jobs N   parallel processes (default 8, split over the requested sequences by length)
  --speed 1.0   no speed-up in the master (default 1.2, Format 3.0)
A sequence file is only valid while the timing of the script is unchanged: when the voice timings move, re-render all of them."""
import os, sys, subprocess, argparse, importlib.util, json, shutil
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ap = argparse.ArgumentParser(); ap.add_argument('script'); ap.add_argument('--prefix', required=True); ap.add_argument('--seqs', default='')
ap.add_argument('--master', default=''); ap.add_argument('--jobs', type=int, default=8); ap.add_argument('--speed', type=float, default=1.2)
ap.add_argument('--project', default=''); ap.add_argument('--audio', default='')
a = ap.parse_args()
sys.path.insert(0, os.path.dirname(os.path.abspath(a.script))); sys.path.insert(0, ROOT)
spec = importlib.util.spec_from_file_location('m', a.script); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
SEQS = {n: (f0, f1) for n, f0, f1 in m.SEQS}; N = m.N; FPS = m.FPS
proj = a.project or os.path.splitext(os.path.basename(a.script))[0]
SEQ_DIR = os.path.join(ROOT, '..', 'renders', proj, 'seq'); os.makedirs(SEQ_DIR, exist_ok=True)
OUT = os.path.join(ROOT, 'out'); os.makedirs(OUT, exist_ok=True)
manifest = os.path.join(SEQ_DIR, 'manifest.json')
man = json.load(open(manifest)) if os.path.exists(manifest) else {}
if a.seqs:
    names = [x for x in a.seqs.split(',') if x]
    tot = sum(SEQS[n][1] - SEQS[n][0] for n in names); jobs = []
    for n in names:
        f0, f1 = SEQS[n]; k = max(1, round(a.jobs * (f1 - f0) / tot)); step = -(-(f1 - f0) // k)
        jobs += [(n, lo, min(f1, lo + step)) for lo in range(f0, f1, step)]
    procs = []
    for n, lo, hi in jobs:
        env = dict(os.environ, PART=f'{lo}:{hi}', PART_PREFIX=f'{a.prefix}_{n}'); procs.append(subprocess.Popen([sys.executable, a.script], env=env, cwd=ROOT))
    for p in procs:
        if p.wait(): sys.exit('a part failed')
    for n in names:
        lst = os.path.join(OUT, f'{a.prefix}_{n}_list.txt'); parts = [lo for nn, lo, _ in jobs if nn == n]
        open(lst, 'w').write(''.join(f"file '{os.path.join(OUT, f'{a.prefix}_{n}_{lo:05d}.mp4').replace(chr(92), '/')}'\n" for lo in parts))
        dst = os.path.join(SEQ_DIR, f'{n}.mp4')
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', dst], check=True)
        man[n] = dict(frames=list(SEQS[n]), seconds=[round(SEQS[n][0] / FPS, 3), round(SEQS[n][1] / FPS, 3)], dur_total=m.DUR)
        print('sequence', n, SEQS[n], '->', dst)
    json.dump(man, open(manifest, 'w'), indent=1)
if a.master:
    for n, (f0, f1) in SEQS.items():
        if n not in man: sys.exit(f'sequence {n} missing: render it')
        g0, g1 = man[n]['frames']
        if g1 - g0 != f1 - f0: sys.exit(f'sequence {n} has a new length ({g1 - g0} -> {f1 - f0} frames): re-render it')
        if g0 != f0:   # same length, whole-frame shift (e.g. a hook added before it): the file is still valid, only its place moved
            print(f'sequence {n} reused, shifted {f0 - g0:+d} frames'); man[n]['frames'] = [f0, f1]
    json.dump(man, open(manifest, 'w'), indent=1)
    lst = os.path.join(OUT, f'{a.prefix}_seq_list.txt')
    open(lst, 'w').write(''.join(f"file '{os.path.abspath(os.path.join(SEQ_DIR, n + '.mp4')).replace(chr(92), '/')}'\n" for n, _, _ in m.SEQS))
    video = os.path.join(OUT, f'{a.prefix}_video.mp4')
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', video], check=True)
    wav = a.audio or f'{proj}.wav'
    subprocess.run([sys.executable, a.script], env=dict(os.environ, PART='audio', AUDIO_NAME=wav), cwd=ROOT, check=True)
    dur = round(N / FPS / a.speed, 3)
    if abs(a.speed - 1.0) > 1e-6:
        subprocess.run(['sh', os.path.join(ROOT, 'tools', 'speedup_raw.sh'), video, os.path.join(OUT, wav), os.path.abspath(a.master), str(dur)], cwd=ROOT, check=True)
    else:
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', video, '-i', os.path.join(OUT, wav), '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af', 'loudnorm=I=-14:TP=-1.5',
                        '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', os.path.abspath(a.master)], check=True)
    print('master', a.master, dur, 's')
