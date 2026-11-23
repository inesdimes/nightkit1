"""Regression fingerprints (PIPELINE phase 1 'Changes'). After touching a shared model, the engine, post or the fonts,
this tells which videos changed, instead of re-checking all of them by hand.
  python tools/qa/regress.py snapshot [examples/a.py ...]   # write tools/qa/baseline.json (default: every script with a QA manifest)
  python tools/qa/regress.py compare  [examples/a.py ...]   # report scripts whose frames differ from the baseline (exit 1 if any)
Each script is fingerprinted by the md5 of its frame(t) pixels at 10 %, 50 % and 90 % of its story duration.
Scripts that fail to load (missing voice files, etc.) are reported as 'skipped', never as unchanged."""
import os, sys, json, glob, hashlib, argparse, io, contextlib
import numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from scene_qa import load
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..')); BASE=os.path.join(os.path.dirname(os.path.abspath(__file__)),'baseline.json')
def scripts(args):
    if args: return args
    return sorted(p for p in glob.glob(os.path.join(ROOT,'examples','*.py')) if 'QA=dict(' in open(p,encoding='utf-8').read())
def fingerprint(path):
    env=os.environ.pop('TEST',None); os.environ.pop('PART',None)
    try:
        with contextlib.redirect_stdout(io.StringIO()): m=load(path)
        d=m.QA['dur']; return {f'{f:.1f}':hashlib.md5(np.ascontiguousarray(np.asarray(m.QA['frame'](d*f))).tobytes()).hexdigest() for f in (0.1,0.5,0.9)}
    finally:
        if env is not None: os.environ['TEST']=env
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('mode',choices=['snapshot','compare']); ap.add_argument('scripts',nargs='*'); a=ap.parse_args()
    os.chdir(ROOT); base=json.load(open(BASE)) if os.path.exists(BASE) else {}
    changed=[]; skipped=[]
    for p in scripts(a.scripts):
        key=os.path.relpath(os.path.abspath(p),ROOT)
        try: fp=fingerprint(p)
        except Exception as e: skipped.append(key); print(f'skipped    {key}  ({type(e).__name__}: {str(e)[:80]})'); continue
        if a.mode=='snapshot': base[key]=fp; print(f'snapshot   {key}')
        elif key not in base: print(f'NEW        {key}  (no baseline yet)')
        elif base[key]!=fp:
            changed.append(key); print(f'CHANGED    {key}  at t = '+', '.join(f"{k} x dur" for k in fp if base[key].get(k)!=fp[k]))
        else: print(f'unchanged  {key}')
    if a.mode=='snapshot': json.dump(base,open(BASE,'w'),indent=1,sort_keys=True); print(f'\nwrote {os.path.relpath(BASE,ROOT)} ({len(base)} scripts)')
    else: print(f'\n{len(changed)} changed, {len(skipped)} skipped'); sys.exit(1 if changed else 0)
if __name__=='__main__': main()
