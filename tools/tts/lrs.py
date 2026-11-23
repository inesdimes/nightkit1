"""THE LAST RESPAWN - PLACEHOLDER voices (Kokoro, PC). Never presented as Enes's performance (briefs/last_respawn.md item 3).
Enes's real takes go to vocal/last_respawn/ and replace these in phase 4.
  python tools/tts/lrs.py src          -> $TTS_DIR/lrs_chr/<key>_0.wav
  python tools/tts/lrs.py build src    -> $TTS_DIR/lrs/<key>.wav + script.json (durations, used by blender/last_respawn.py)
Keys = line numbers of briefs/last_respawn_voice_sheet.md. Speakers: G = Goblin 47, K = Bell Knight, B = Bellwright."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import multi

VOICES = {'G': ('am_puck', 'en-us'), 'K': ('bm_george', 'en-gb'), 'B': ('bm_lewis', 'en-gb')}
# (text, speed, pitch_st, gain_db, pause_before_s)
D = [
    ('l01', 'G', [('Not again!', 1.05, 3.0, 0, 0)]),
    ('l02', 'K', [('Who keeps doing that?', 1.0, -1.0, 0, 0)]),
    ('l03', 'G', [('The bell stopped!', 1.2, 3.0, 0, 0)]),
    ('l04', 'G', [("And they're coming!", 1.2, 3.0, 0, 0)]),
    ('l05', 'B', [('The bell needs one last life!', 0.95, -3.0, 0, 0)]),
    ('l06', 'K', [('Take mine!', 1.0, -1.0, 0, 0)]),
    ('l07', 'B', [('You gave yours years ago.', 0.85, -3.0, 0, 0)]),
    ('l08', 'G', [("You're hollow?", 1.0, 3.0, 0, 0)]),
    ('l09', 'B', [('They remember their commander.', 0.85, -3.0, 0, 0)]),
    ('l10', 'B', [("Restart it, and you're gone.", 0.9, -3.0, 0, 0)]),
    ('l11', 'G', [('There has to be another way!', 1.15, 3.0, 0, 0)]),
    ('l12', 'K', [('Then make this one count.', 0.9, -1.0, 0, 0)]),
    ('l13', 'G', [('No... NOT AGAIN!', 1.1, 3.5, 0, 0)]),
]

if __name__ == '__main__':
    multi.main(D, VOICES, 'lrs')
