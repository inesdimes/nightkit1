"""Body checks for a whole video (phase 4 of the human performance system; nightkit/bodycheck.py does the maths).
Every hd.human call the script makes is checked, so no script changes are needed:
  arms / hands / fingers inside the body or the head, forearms through each other, fingers through the other hand,
  a hand inside another character, legs through each other, feet in the ground, folded elbows,
  joint jumps (a pose that snaps) and pops (a joint that starts / stops dead), body-relative, per 24 fps frame.

  python tools/qa/body_qa.py examples/tutorial_jump.py [--step 1] [--t0 0 --t1 99]
Writes out/qa/<name>/body.md and prints the issue windows. Exit code 1 when there are issues.
Speed is not measured across scene cuts (QA['scenes'] t0). Skipped frames (--step 2) make jump checks per 2 frames,
normalised to 24 fps, and pops weaker - use --step 1 before delivering."""
import os, sys, io, argparse, contextlib
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')); sys.path.insert(0, ROOT); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scene_qa import load
from nightkit import bodycheck

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('script'); ap.add_argument('--step', type=int, default=1)
    ap.add_argument('--t0', type=float, default=0.0); ap.add_argument('--t1', type=float, default=1e9); a = ap.parse_args()
    os.environ.pop('TEST', None)
    with contextlib.redirect_stdout(io.StringIO()): m = load(a.script)
    QA = m.QA; fps = QA['fps']; dur = min(QA['dur'], a.t1); name = os.path.splitext(os.path.basename(a.script))[0]
    cuts = sorted(s['t0'] for s in QA.get('scenes', []))
    mon = bodycheck.Monitor(fps=fps / a.step); undo = bodycheck.install(mon)
    try:
        f = int(round(a.t0 * fps)); last = None
        while f / fps < dur:
            t = f / fps
            if last is not None and any(last < c <= t for c in cuts): mon.cut()
            mon.frame(t)
            with contextlib.redirect_stdout(io.StringIO()): QA['frame'](t)
            last = t; f += a.step
    finally:
        undo()
    txt = mon.text(); print(txt)
    outd = os.path.join(ROOT, 'out', 'qa', name); os.makedirs(outd, exist_ok=True)
    with open(os.path.join(outd, 'body.md'), 'w', encoding='utf-8') as fh:
        fh.write(f'# body checks: {name}\n\nstep {a.step}, {a.t0:.1f}-{dur:.1f} s\n\n```\n{txt}\n```\n')
    sys.exit(1 if mon.windows() else 0)

if __name__ == '__main__':
    main()
