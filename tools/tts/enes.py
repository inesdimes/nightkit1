"""Enes's own voice (English) via Chatterbox voice cloning. Settings = the "2b" test Enes approved on 20 Nov 2026:
ORIGINAL Chatterbox (not Turbo: Turbo ignores cfg_weight/exaggeration), reference voice/enes_ref_main.wav,
exaggeration 0.5, cfg_weight 0.2, seed 3000. cfg 0.2 is what removes the Turkish accent the reference carries.

Needs the Chatterbox install's own Python (system Python has no chatterbox/torch). Run:
  D:\\chatter\\Chatterbox-TTS-Server-2.0.0\\python_embedded\\python.exe tools/tts/enes.py lines.json <name>
lines.json = {"1": "First line.", "2": "Second line."}  (same keys as the Kokoro scripts)
Output: $TTS_DIR/<name>/<key>.wav (24 kHz mono) + script.json {text, dur}.
Stop the Chatterbox web server first (it holds ~6 GB of the 8 GB VRAM). Not verified by ear for every text: Enes judges."""
import os, sys, json, argparse
import torch, torchaudio

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ap = argparse.ArgumentParser()
ap.add_argument("lines"); ap.add_argument("name")
ap.add_argument("--ref", default=os.environ.get("ENES_REF", os.path.join(REPO, "voice", "enes_ref_main.wav")))
ap.add_argument("--exag", type=float, default=0.5)
ap.add_argument("--cfg", type=float, default=0.2)
ap.add_argument("--seed", type=int, default=3000)
a = ap.parse_args()
if a.cfg <= 0:
    a.cfg = 1e-6   # exactly 0.0 crashes in this chatterbox version (batch-2 CFG path); 1e-6 is equivalent
TTS_DIR = os.environ.get("TTS_DIR", os.path.join(REPO, "tts"))
OUT = os.path.join(TTS_DIR, a.name); os.makedirs(OUT, exist_ok=True)
lines = json.load(open(a.lines, encoding="utf-8"))

from chatterbox.tts import ChatterboxTTS
tts = ChatterboxTTS.from_pretrained("cuda")
txt, dur = {}, {}
for key, text in lines.items():
    torch.manual_seed(a.seed)
    wav = tts.generate(text, audio_prompt_path=a.ref, exaggeration=a.exag, cfg_weight=a.cfg)
    if wav.dim() == 1: wav = wav.unsqueeze(0)
    torchaudio.save(os.path.join(OUT, key + ".wav"), wav.cpu(), tts.sr)
    txt[key] = text; dur[key] = round(wav.shape[-1] / tts.sr, 2); print(key, dur[key], text, flush=True)
print("TOTAL", round(sum(dur.values()), 2), "words", sum(len(t.split()) for t in txt.values()))
json.dump({"text": txt, "dur": dur}, open(os.path.join(OUT, "script.json"), "w", encoding="utf-8"), indent=1)
