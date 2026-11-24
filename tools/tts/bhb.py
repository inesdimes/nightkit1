"""Voice for "What if the boss's health bar was the village's?" (bhb, 24 Nov 2026). Brief: briefs/boss_health_bar.md, cue sheet:
briefs/boss_health_bar_voice_sheet.md. The brief says NO synthetic voices: Enes (and Betul for the woman) record every line.
Until then the film is timed from planned durations:
  python tools/tts/bhb.py plan                       # tts/bhb/script.json from planned durations (no audio)
Enes's takes (one m4a per LINE, Kayit (1..7).m4a in line order):
  python tools/tts/own_prep.py bhb "vocal/<folder>" --lines ; python tools/tts/bhb.py build own
Speakers: N narrator, W old woman, K knight, G guardian."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import multi
VOICES = {'K': ('am_adam', 'en-us'), 'W': ('bf_emma', 'en-gb'), 'G': ('bm_george', 'en-gb')}
D = [('01', 'N', [("What if every hit hurt the village?", 1.0, 0, 0, 0)]),
     ('02', 'W', [("Stop!", 1.0, 0, 0, 0), ("Every wound reaches us!", 1.0, 0, 0, 0.15)]),
     ('03', 'K', [("It attacked first!", 1.0, 0, 0, 0)]),
     ('04', 'W', [("It's holding the curse back.", 1.0, 0, 0, 0)]),
     ('05', 'K', [("Then what do I strike?", 1.0, 0, 0, 0)]),
     ('06', 'W', [("The king's seal!", 1.0, 0, 0, 0)]),
     ('07', 'G', [("The king is next.", 1.0, 0, 0, 0)])]
PLAN = {'01': [1.9], '02': [0.6, 1.4], '03': [1.25], '04': [1.75], '05': [1.45], '06': [1.05], '07': [1.6]}    # seconds at 1x (the film runs 1.2x after)
def plan():
    out = os.path.join(multi.TTS_DIR, 'bhb'); os.makedirs(out, exist_ok=True); dur = {}; txt = {}; sent = {}; spk = {}
    for k, s, ss in D:
        pos = 0.0; sent[k] = []
        for (tx, *_, pause), d in zip(ss, PLAN[k]): pos += pause; sent[k].append([round(pos, 3), round(pos + d, 3), tx]); pos += d
        dur[k] = round(pos, 2); txt[k] = ' '.join(x[0] for x in ss); spk[k] = s
    json.dump({'text': txt, 'dur': dur, 'sent': sent, 'spk': spk, 'planned': True}, open(os.path.join(out, 'script.json'), 'w'), indent=1); print('planned', dur)
if __name__ == '__main__':
    if sys.argv[1] == 'plan': plan()
    else: multi.main(D, VOICES, 'bhb')
