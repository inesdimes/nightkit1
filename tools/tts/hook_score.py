"""Score the hook variants (tools/tts/hook_variants.py). Claude cannot listen, so 'lively' is measured:
  words  = Whisper small.en transcript must match the line (exact, ignoring case / punctuation)
  range  = pitch range in semitones (90th - 10th percentile of the voiced f0): a flat read scores low
  punch  = loudness contrast (dB) between the loudest and the median 50 ms frame: stressed words stand out
  speech = voiced length (s); shorter = more energy (and the hook must stay short)
Step 1 (Chatterbox Python, has transformers):  python tools/tts/hook_score.py bt asr
Step 2 (system Python):                        python tools/tts/hook_score.py bt score   -> ranked list + a listening file"""
import os, sys, re, json, glob
import numpy as np, soundfile as sf
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
name, step = sys.argv[1], sys.argv[2]
D = os.path.join(os.environ.get('TTS_DIR', os.path.join(REPO, 'tts')), f'{name}_hook'); WANT = "why do bridge trolls want tolls"
def norm(s): return ' '.join(re.sub(r"[^a-z' ]", ' ', s.lower()).split())
if step == 'asr':
    import torch
    from transformers import pipeline
    asr = pipeline('automatic-speech-recognition', model='openai/whisper-small.en', device=0)
    out = {}
    for f in sorted(glob.glob(os.path.join(D, '*.wav'))):
        y, sr = sf.read(f); y = y if y.ndim == 1 else y.mean(1); out[os.path.basename(f)] = asr({'raw': y.astype(np.float32), 'sampling_rate': sr})['text'].strip()
    json.dump(out, open(os.path.join(D, 'asr.json'), 'w'), indent=1)
else:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import fp_check_lib as C
    heard = json.load(open(os.path.join(D, 'asr.json'))); rows = []
    for fn, tx in heard.items():
        y, sr = sf.read(os.path.join(D, fn)); y = y if y.ndim == 1 else y.mean(1)
        fr = int(0.05 * sr); n = len(y) // fr; db = 20 * np.log10(np.sqrt((y[:n * fr].reshape(n, fr) ** 2).mean(1)) + 1e-9)
        v = db > db.max() - 30; speech = (np.where(v)[0][-1] - np.where(v)[0][0] + 1) * 0.05
        p = C.f0(y, sr); p = p[p > 50]
        rng = float(12 * np.log2(np.percentile(p, 90) / np.percentile(p, 10))) if len(p) > 10 else 0.0
        punch = float(db[v].max() - np.median(db[v]))
        rows.append(dict(file=fn, ok=norm(tx) == WANT, heard=tx, range=round(rng, 1), punch=round(punch, 1), speech=round(speech, 2)))
    good = [r for r in rows if r['ok'] and r['speech'] <= 2.6]
    for r in good: r['score'] = round(r['range'] + 0.5 * r['punch'] - 2.0 * max(0.0, r['speech'] - 2.0), 2)
    good.sort(key=lambda r: -r['score'])
    print('correct words:', len(good), 'of', len(rows))
    for r in good: print(r['score'], r['file'], 'range', r['range'], 'st  punch', r['punch'], 'dB  speech', r['speech'], 's')
    print('rejected:', [(r['file'], r['heard']) for r in rows if not r['ok']][:12])
    json.dump(good, open(os.path.join(D, 'ranked.json'), 'w'), indent=1)
