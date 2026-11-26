"""Claude cannot listen: transcribe every cloned take with Whisper (small.en, cached) and pick, per line, the take whose words
match the script (Chatterbox sometimes repeats or invents words after a long pause). 26 Nov 2026, Bridge Troll.
Run with the Chatterbox Python (it has torch + transformers):
  D:\\chatter\\Chatterbox-TTS-Server-2.0.0\\python_embedded\\python.exe tools/tts/asr_check.py bt [--pick]
--pick copies the best take to <key>_all.wav (best = exact words first, then closest to the planned length) and writes asr_log.json."""
import os, sys, re, json, glob, shutil, importlib.util, difflib
import numpy as np, soundfile as sf, torch
from transformers import pipeline
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
name = sys.argv[1]; pick = '--pick' in sys.argv
spec = importlib.util.spec_from_file_location(name, os.path.join(REPO, 'tools', 'tts', name + '.py'))
sys.path.insert(0, os.path.join(REPO, 'tools', 'tts')); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
lines = mod.lines_json('en'); plan = {k: sum(v) + 0.3 * (len(v) - 1) for k, v in mod.PLAN.items()}
TTS_DIR = os.environ.get('TTS_DIR', os.path.join(REPO, 'tts')); D = os.path.join(TTS_DIR, name + '_own')
asr = pipeline('automatic-speech-recognition', model='openai/whisper-small.en', device=0 if torch.cuda.is_available() else -1)
def norm(s): return re.sub(r"[^a-z0-9' ]", ' ', s.lower().replace('-', ' ')).split()
def speech_len(y, sr):
    fr = int(0.01 * sr); n = len(y) // fr; db = 20 * np.log10(np.sqrt((y[:n * fr].reshape(n, fr) ** 2).mean(1)) + 1e-9)
    v = np.where(db > -38)[0]; return (v[-1] - v[0] + 1) / 100 if len(v) else 0.0
log = {}
for k, L in lines.items():
    want = norm(L['text']); res = []
    for f in sorted(glob.glob(os.path.join(D, f'{k}_take*.wav'))):
        y, sr = sf.read(f); y = y if y.ndim == 1 else y.mean(1)
        got = asr({'raw': y.astype(np.float32), 'sampling_rate': sr})['text']
        g = norm(got); ratio = difflib.SequenceMatcher(None, want, g).ratio(); d = speech_len(y, sr)
        res.append(dict(file=os.path.basename(f), heard=got.strip(), match=round(ratio, 2), speech=round(d, 2)))
    for r in res: r['score'] = (r['match'] < 0.999, abs(r['speech'] - plan[k]))
    best = min(res, key=lambda r: r['score']) if res else None
    log[k] = dict(text=L['text'], best=best['file'] if best else None, takes=[{x: r[x] for x in ('file', 'heard', 'match', 'speech')} for r in res])
    print(k, L['text']); [print('   ', '*' if r is best else ' ', r['file'], r['match'], r['speech'], '|', r['heard']) for r in res]
    if pick and best: shutil.copy(os.path.join(D, best['file']), os.path.join(D, f'{k}_all.wav'))
json.dump(log, open(os.path.join(D, 'asr_log.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
