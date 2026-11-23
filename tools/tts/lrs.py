"""THE LAST RESPAWN - PLACEHOLDER voices (Kokoro, PC). Never presented as Enes's performance (briefs/last_respawn.md item 3).
Enes's real takes go to vocal/last_respawn/ and replace these in phase 4.
  python tools/tts/lrs.py src          -> $TTS_DIR/lrs_chr/<key>_0.wav
  python tools/tts/lrs.py build src    -> $TTS_DIR/lrs/<key>.wav + script.json (durations, used by blender/last_respawn.py)
Keys = line numbers of briefs/last_respawn_voice_sheet.md (script v2, 23 lines). The text comes from SCRIPT in
blender/last_respawn.py. Speakers: G = Goblin 47, K = Bell Knight, B = Bellwright."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'blender'))
os.environ.setdefault('MODE', 'audio')
import multi
from last_respawn import SCRIPT

VOICES = {'G': ('am_puck', 'en-us'), 'K': ('bm_george', 'en-gb'), 'B': ('bm_lewis', 'en-gb')}
# per speaker: (speed, pitch_st); a few lines are faster / slower
STYLE = {'G': (1.15, 3.0), 'K': (0.95, -1.0), 'B': (0.88, -3.0)}
SPEED = {'l01': 1.05, 'l12': 1.0, 'l22': 0.8, 'l23': 1.1, 'l21': 0.9}
PITCH = {'l23': 3.5}
D = [(k, spk, [(txt, SPEED.get(k, STYLE[spk][0]), PITCH.get(k, STYLE[spk][1]), 0, 0)]) for k, _, spk, txt, _, _ in SCRIPT]

if __name__ == '__main__':
    multi.main(D, VOICES, 'lrs')
