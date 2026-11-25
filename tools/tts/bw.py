"""Voice for "Why Does the Final Boss Have a Help Wanted Sign?" (bw, 25 Nov 2026). Brief: briefs/FINAL_BOSS_HELP_WANTED_FULL_BRIEF.txt,
cue sheet: briefs/boss_wanted_voice_sheet.md. Enes: no voice in the first render, he records every line afterwards.
Until then the film is timed from planned durations:
  python tools/tts/bw.py plan                        # tts/bw/script.json from planned durations (no audio)
Enes's takes (one m4a per LINE, Kayit (1..15).m4a in line order):
  python tools/tts/own_prep.py bw "vocal/<folder>" --lines ; python tools/tts/bw.py build own
Speakers: N narrator, B boss, K knight (13 = the knight as the new boss, speaker K)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import multi
VOICES = {'K': ('am_adam', 'en-us'), 'B': ('bm_george', 'en-gb')}
D = [('01', 'N', [("The boss wasn't attacking.", 1.0, 0, 0, 0), ("He was hiring.", 1.0, 0, 0, 0.2)]),
     ('02', 'B', [("Want my job?", 1.0, 0, 0, 0)]),
     ('03', 'K', [("I came to defeat you.", 1.0, 0, 0, 0)]),
     ('04', 'N', [("His health bar now showed nearly ten thousand failed fights.", 1.0, 0, 0, 0)]),
     ('05', 'B', [("Same arena.", 1.0, 0, 0, 0), ("Same speech.", 1.0, 0, 0, 0.2), ("Every single respawn.", 1.0, 0, 0, 0.2)]),
     ('06', 'N', [("Then he handed the knight his sword and a contract.", 1.0, 0, 0, 0)]),
     ('07', 'K', [("What's the pay?", 1.0, 0, 0, 0)]),
     ('08', 'B', [("One health bar.", 1.0, 0, 0, 0), ("Infinite respawns.", 1.0, 0, 0, 0.2)]),
     ('09', 'N', [("The knight signed without reading the tiny print.", 1.0, 0, 0, 0)]),
     ('10', 'B', [("No breaks.", 1.0, 0, 0, 0)]),
     ('11', 'N', [("The old boss finally left smiling.", 1.0, 0, 0, 0)]),
     ('12', 'N', [("His first challenger arrived before the ink dried.", 1.0, 0, 0, 0)]),
     ('13', 'K', [("Boss wanted.", 1.0, 0, 0, 0)]),
     ('14', 'N', [("The new knight looked exactly like him.", 1.0, 0, 0, 0)]),
     ('15', 'N', [("The loop had found its next boss.", 1.0, 0, 0, 0)])]
# planned sentence lengths in seconds at 1x (the film runs 1.2x after): ~2.9 words/s calm read
PLAN = {'01': [1.35, 1.0], '02': [1.0], '03': [1.45], '04': [3.3], '05': [0.85, 0.85, 1.15], '06': [3.2], '07': [0.95],
        '08': [1.0, 1.1], '09': [2.9], '10': [0.9], '11': [2.0], '12': [2.8], '13': [0.85], '14': [2.2], '15': [2.0]}
def plan():
    out = os.path.join(multi.TTS_DIR, 'bw'); os.makedirs(out, exist_ok=True); dur = {}; txt = {}; sent = {}; spk = {}
    for k, s, ss in D:
        pos = 0.0; sent[k] = []
        for (tx, *_, pause), d in zip(ss, PLAN[k]): pos += pause; sent[k].append([round(pos, 3), round(pos + d, 3), tx]); pos += d
        dur[k] = round(pos, 2); txt[k] = ' '.join(x[0] for x in ss); spk[k] = s
    json.dump({'text': txt, 'dur': dur, 'sent': sent, 'spk': spk, 'planned': True}, open(os.path.join(out, 'script.json'), 'w'), indent=1); print('planned', dur)
if __name__ == '__main__':
    if sys.argv[1] == 'plan': plan()
    else: multi.main(D, VOICES, 'bw')
