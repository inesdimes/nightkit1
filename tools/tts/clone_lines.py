"""Clone every line of a short in Enes's voice, one reference per speaker (tts/<name>_refs/<spk>_<lang>.wav, built by the
<name>.py 'refs' step). English = ORIGINAL Chatterbox with the approved "2b" settings (cfg 0.2 removes the Turkish accent,
exaggeration per line); Turkish = Chatterbox Multilingual, language_id 'tr' (native accent wanted, default cfg 0.5).
Run with the Chatterbox install's Python (stop the web server first, it holds ~6 GB VRAM):
  D:\\chatter\\Chatterbox-TTS-Server-2.0.0\\python_embedded\\python.exe tools/tts/clone_lines.py sp en [--takes 3]
Writes $TTS_DIR/<name>_own/<key>_all.wav (+ _take<n>.wav), then run `python tools/tts/<name>.py build own`.
With --takes N it makes N seeds per line and keeps the one closest to the planned length (Claude cannot listen; Enes judges)."""
import os, sys, json, argparse, importlib.util
import torch, torchaudio
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ap = argparse.ArgumentParser(); ap.add_argument('name'); ap.add_argument('lang', choices=['en', 'tr'])
ap.add_argument('--takes', type=int, default=1); ap.add_argument('--seed', type=int, default=3000); ap.add_argument('--only', default='')
a = ap.parse_args()
spec = importlib.util.spec_from_file_location(a.name, os.path.join(REPO, 'tools', 'tts', a.name + '.py'))
sys.path.insert(0, os.path.join(REPO, 'tools', 'tts'))
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
lines = mod.lines_json(a.lang); plan = {k: sum(v) + 0.3 * (len(v) - 1) for k, v in mod.PLAN.items()}
TTS_DIR = os.environ.get('TTS_DIR', os.path.join(REPO, 'tts')); OUT = os.path.join(TTS_DIR, a.name + '_own'); os.makedirs(OUT, exist_ok=True)
REFS = os.path.join(REPO, 'tts', a.name + '_refs')
if a.lang == 'en':
    from chatterbox.tts import ChatterboxTTS
    tts = ChatterboxTTS.from_pretrained('cuda')
    def gen(text, ref, ex): return tts.generate(text, audio_prompt_path=ref, exaggeration=ex, cfg_weight=0.2)
else:
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    tts = ChatterboxMultilingualTTS.from_pretrained(torch.device('cuda'))
    def gen(text, ref, ex): return tts.generate(text, language_id='tr', audio_prompt_path=ref, exaggeration=ex, cfg_weight=0.5)
log = {}
for k, L in lines.items():
    if a.only and k not in a.only.split(','): continue
    ref = os.path.join(REFS, f"{L['spk']}_{a.lang}.wav"); best = None
    for n in range(a.takes):
        torch.manual_seed(a.seed + 17 * n)
        w = gen(L['text'], ref, L['exag']); w = w.unsqueeze(0) if w.dim() == 1 else w
        d = w.shape[-1] / tts.sr; torchaudio.save(os.path.join(OUT, f'{k}_take{n}.wav'), w.cpu(), tts.sr)
        score = abs(d - plan[k] * (1.15 if a.lang == 'tr' else 1.0))
        if best is None or score < best[0]: best = (score, n, d, w)
    torchaudio.save(os.path.join(OUT, f'{k}_all.wav'), best[3].cpu(), tts.sr)
    log[k] = dict(take=best[1], dur=round(best[2], 2), plan=round(plan[k], 2), spk=L['spk'], text=L['text']); print(k, log[k], flush=True)
json.dump(log, open(os.path.join(OUT, 'clone_log.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
