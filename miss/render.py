#!/usr/bin/env python3
"""MISS - a PS1-style corridor short. Headless, deterministic. Dependencies: numpy, Pillow and ffmpeg (via subprocess), nothing else.

  python render.py --cut master      -> out/MISS_15s_master.mp4  (+ out/contact_master.png, out/stills/, out/qa_report.txt)
  python render.py --cut extended    -> out/MISS_30s_extended.mp4 (+ out/contact_extended.png, out/stills/, out/qa_report.txt)

Debug / review outputs (steps 1-4):
  python render.py --debug world     -> out/debug/*  the five cameras, a turntable and the camera asserts
  python render.py --debug poses     -> out/contact_poses.png  the 8 key poses (archer IDLE/DRAW/RELEASE/LOWER, goblin STAND/DUCK/WALK/CARRY)
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
import raster as R
import font as FNT
import world as WORLD
import characters as CH
import timeline as T
import scene as SC
import audio as AU
import qa as QA
import subprocess, time

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')

def shot(faces, cam, frame=0):
    """one finished 180x320 frame: render + the PS1 post chain"""
    return R.post(R.render(faces, cam, frame), frame)

def label(sheet, x, y, text, scale=2):
    FNT.draw_text(sheet, x, y, text, fill=(242, 242, 234), scale=scale, outline=(20, 20, 26), outline_px=1)

def grid(cells, cols, labels=None, zoom=3, pad=6, title_h=0):
    """cells: list of 180x320x3 uint8 images -> one labelled sheet (each cell shown at zoom x)"""
    rows = (len(cells) + cols - 1) // cols; cw, ch = R.W * zoom, R.H * zoom
    sheet = np.full((rows * (ch + pad) + pad, cols * (cw + pad) + pad, 3), 16, np.uint8)
    for i, c in enumerate(cells):
        r, k = divmod(i, cols); big = np.repeat(np.repeat(c, zoom, 0), zoom, 1)
        y0, x0 = pad + r * (ch + pad), pad + k * (cw + pad); sheet[y0:y0 + ch, x0:x0 + cw] = big
        if labels: label(sheet, x0 + 8, y0 + ch - 28, labels[i], 2)
    return sheet

def debug_world():
    os.makedirs(os.path.join(OUT, 'debug'), exist_ok=True)
    faces = WORLD.build_world(); archer = CH.make_archer(dict(pose='IDLE')); goblin = CH.make_goblin(dict(pose='STAND'))
    scene = faces + archer + goblin
    cells, labels = [], []
    for k, cam in WORLD.CAMERAS.items():
        img = shot(scene, cam, 0); cells.append(img); labels.append('CAM ' + k)
        Image.fromarray(R.upscale(img)).save(os.path.join(OUT, 'debug', f'cam_{k}.png'))
    Image.fromarray(grid(cells, 5, labels, zoom=2)).save(os.path.join(OUT, 'debug', 'cameras.png'))
    # turntable: eight cameras orbiting the middle of the corridor at 2 m height, looking at the middle of the action
    cells, labels = [], []
    centre = np.array([3.5, 0.6, 0.0])
    for i in range(8):
        a = np.radians(i * 45); pos = centre + np.array([8.5 * np.cos(a), 1.6, 6.0 * np.sin(a)]); cam = R.Camera(pos, centre, 50)
        cells.append(shot(scene, cam, i)); labels.append(f'TURN {i * 45}')
    Image.fromarray(grid(cells, 4, labels, zoom=2)).save(os.path.join(OUT, 'debug', 'turntable.png'))
    # camera asserts + where things land on screen in CAM A
    lines = []
    for k, rule, ok, detail in WORLD.check_cameras(): lines.append(f'{"PASS" if ok else "FAIL"}  CAM {k}: {rule} ({detail})')
    cam = WORLD.CAMERAS['A']
    for name, p in (('archer (head)', (2.6, 0.9, -0.55)), ('board (centre)', (6.98, 0.78, 0.0)), ('goblin (head)', (6.45, 0.4, 0.0))):
        q = cam.project(p); lines.append(f'CAM A: {name:15s} at screen x={q[0] / R.W:.2f} y={q[1] / R.H:.2f} of the frame')
    print('\n'.join(lines)); open(os.path.join(OUT, 'debug', 'camera_asserts.txt'), 'w').write('\n'.join(lines) + '\n')

def debug_poses():
    os.makedirs(OUT, exist_ok=True)
    world = WORLD.build_world(); cells, labels = [], []
    acam = R.Camera((3.55, 0.60, 2.05), (2.78, 0.50, 0.38), 50)
    for pose in ('IDLE', 'DRAW', 'RELEASE', 'LOWER'):
        cells.append(shot(world + CH.make_archer(dict(pose=pose, quiver=4)), acam, 0)); labels.append('ARCHER ' + pose)
    gcam = R.Camera((5.75, 0.34, 1.15), (6.45, 0.25, 0.0), 50)
    for pose, ex in (('STAND', {}), ('DUCK', {}), ('WALK', dict(phase=0)), ('CARRY', {})):
        cells.append(shot(world + CH.make_goblin(dict(pose=pose, **ex)), gcam, 0)); labels.append('GOBLIN ' + pose)
    Image.fromarray(grid(cells, 4, labels, zoom=3)).save(os.path.join(OUT, 'contact_poses.png'))
    print('wrote', os.path.join(OUT, 'contact_poses.png'))

def shot_name(cut, f):
    for sid, a, b in T.CUTS[cut]['shots']:
        if a <= f < b: return sid
    return T.CUTS[cut]['shots'][-1][0]

def contact_sheet(cut):
    """one frame per shot, labelled with the shot id and the frame number; the individual stills go to out/stills/"""
    frames = T.CUTS[cut]['sheet']; os.makedirs(os.path.join(OUT, 'stills'), exist_ok=True); cells, labels = [], []
    for f in frames:
        img, _ = SC.frame180(cut, f); cells.append(img); sid = shot_name(cut, f); labels.append(f'{sid}  f{f}')
        Image.fromarray(R.upscale(img)).save(os.path.join(OUT, 'stills', f'{cut}_{sid}_f{f:03d}.png'))
    cols = 3 if len(cells) <= 6 else 4
    Image.fromarray(grid(cells, cols, labels, zoom=2)).save(os.path.join(OUT, f'contact_{cut}.png'))

def write_qa_reports(cut, res):
    txt, counts = QA.format_report(cut, res); os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, f'qa_report_{cut}.txt'), 'w').write(txt)
    parts = [open(os.path.join(OUT, f'qa_report_{c}.txt')).read() for c in ('master', 'extended') if os.path.exists(os.path.join(OUT, f'qa_report_{c}.txt'))]
    open(os.path.join(OUT, 'qa_report.txt'), 'w').write('\n'.join(parts)); return counts

def render_cut(cut, force=False):
    C = T.CUTS[cut]; N = C['frames']; os.makedirs(OUT, exist_ok=True); t0 = time.time()
    wav = os.path.join(OUT, f'{cut}.wav'); ai = AU.build_audio(cut, wav, OUT)                       # audio first: the QA reports its loudness
    res = QA.run_qa(cut, ai); counts = write_qa_reports(cut, res)
    print(f'[{cut}] QA: {counts["PASS"]} pass, {counts["FAIL"]} fail, {counts["DEVIATION"]} deviation (see out/qa_report.txt)')
    if counts['FAIL'] and not force:
        for st, rule, detail in res:
            if st == 'FAIL': print('  FAIL', rule, '->', detail)
        print('Refusing to encode with failing asserts (use --force to override).', file=sys.stderr); sys.exit(1)
    path = os.path.join(OUT, C['file'])
    cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{R.W * R.SCALE}x{R.H * R.SCALE}', '-r', '24', '-i', '-', '-i', wav,
           '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-c:a', 'aac', '-b:a', '192k', '-r', '24', '-movflags', '+faststart', '-shortest', path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(N):
        img, _ = SC.frame180(cut, f); p.stdin.write(np.ascontiguousarray(R.upscale(img)).tobytes())
    p.stdin.close(); rc = p.wait()
    if rc: print('ffmpeg failed', file=sys.stderr); sys.exit(1)
    contact_sheet(cut)
    return dict(cut=cut, frames=N, seconds=N / 24, path=path, size=os.path.getsize(path), counts=counts, lufs=ai['lufs'], peak=ai['peak_db'], narration=ai['narration'], secs=time.time() - t0)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--cut', choices=['master', 'extended']); ap.add_argument('--debug', choices=['world', 'poses', 'all', 'qa'])
    ap.add_argument('--force', action='store_true', help='encode even if an assert FAILs'); a = ap.parse_args()
    if a.debug in ('world', 'all'): debug_world()
    if a.debug in ('poses', 'all'): debug_poses()
    if a.debug == 'qa':
        for c in ('master', 'extended'): res = QA.run_qa(c); print(QA.format_report(c, res)[0])
    if a.cut:
        r = render_cut(a.cut, a.force)
        print(f"\n{r['cut']}: {r['frames']} frames = {r['seconds']:.2f} s, {r['size'] / 1e6:.1f} MB -> {r['path']}\n"
              f"QA: {r['counts']['PASS']} pass / {r['counts']['FAIL']} fail / {r['counts']['DEVIATION']} deviation; loudness {r['lufs']:.1f} LUFS, peak {r['peak']:.1f} dBFS; {r['narration']}; took {r['secs']:.0f} s")
    if not a.cut and not a.debug: ap.print_help()

if __name__ == '__main__': main()
