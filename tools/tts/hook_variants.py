"""More lively takes of ONE line (26 Nov 2026, Enes: the Bridge Troll hook must sound more alive so nobody swipes away).
Original Chatterbox (cfg 0.2 keeps the accent off), Enes's narrator reference, several texts x exaggerations x seeds.
  <chatterbox python> tools/tts/hook_variants.py bt 00 N      -> $TTS_DIR/<name>_hook/<text>_<exag>_<seed>.wav
Then score with tools/tts/hook_score.py (Whisper words + pitch range)."""
import os, sys, torch, torchaudio
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
name, key, spk = sys.argv[1], sys.argv[2], sys.argv[3]
TEXTS = {'a': "Why do bridge trolls want tolls?", 'b': "Why do bridge trolls want TOLLS?!", 'c': "Why do bridge trolls... want TOLLS?!"}
EXAGS = [float(x) for x in os.environ.get('EXAGS', '0.9,1.15,1.4').split(',')]; SEEDS = [int(x) for x in os.environ.get('SEEDS', '11,23,37').split(',')]
ONLY = os.environ.get('TEXTS', 'abc')
OUT = os.path.join(os.environ.get('TTS_DIR', os.path.join(REPO, 'tts')), f'{name}_hook'); os.makedirs(OUT, exist_ok=True)
ref = os.path.join(REPO, 'tts', f'{name}_refs', f'{spk}_en.wav')
from chatterbox.tts import ChatterboxTTS
tts = ChatterboxTTS.from_pretrained('cuda')
for tk, tx in TEXTS.items():
    if tk not in ONLY: continue
    for ex in EXAGS:
        for sd in SEEDS:
            torch.manual_seed(sd); w = tts.generate(tx, audio_prompt_path=ref, exaggeration=ex, cfg_weight=0.2)
            w = w.unsqueeze(0) if w.dim() == 1 else w
            f = os.path.join(OUT, f'{tk}_{ex}_{sd}.wav'); torchaudio.save(f, w.cpu(), tts.sr); print(f, round(w.shape[-1] / tts.sr, 2), flush=True)
