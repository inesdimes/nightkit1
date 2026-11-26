"""Voice for "What if you never attack the final boss?" (na = never attack, 26 Nov 2026). Brief: briefs/never_attack.md.
English = Enes's CLONED voice (recipe of tools/tts/ms.py): N narrator (the spoken title) <- sp_refs N, B boss <- sp_refs B
(his boss takes), pitched DOWN BOSS_ST semitones in the build (big, old). Turkish = Enes records the lines himself.
Ending (Enes, 26 Nov): the counter overflows at 9,999 -> the game resets to frame 0; the boss remembers ("...tea again?").
Steps:
  python tools/tts/na.py refs
  <chatterbox python> tools/tts/clone_lines.py na en --takes 4
  <chatterbox python> tools/tts/asr_check.py na --pick
  python tools/tts/na.py build own"""
import os, sys, json, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import multi
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VOICES = {'B': ('bm_george', 'en-gb')}
D = [('00', 'N', [("What if you never attack the final boss?", 1.0, 0, 0, 0)]),
     ('01', 'B', [("Kneel before me, mortal!", 1.0, 0, 0, 0), ("It's your turn. Attack!", 1.0, 0, 0, 0.5)]),
     ('02', 'B', [("Any day now...", 1.0, 0, 0, 0), ("I can't move until you do!", 1.0, 0, 0, 0.3)]),
     ('03', 'B', [("Fine.", 1.0, 0, 0, 0), ("Would you like some tea?", 1.0, 0, 0, 0.6)]),
     ('04', 'B', [("Three hundred years.", 1.0, 0, 0, 0), ("Nobody ever stayed this long.", 1.0, 0, 0, 0.4)]),
     ('05', 'B', [("Every hero hit me in the first second.", 1.0, 0, 0, 0), ("You stayed.", 1.0, 0, 0, 0.5)]),
     ('06', 'B', [("Oh no... the counter is full!", 1.0, 0, 0, 0)]),
     ('07', 'B', [("Kneel before me, mortal!", 1.0, 0, 0, 0)]),
     ('08', 'B', [("Hey... want some tea again?", 1.0, 0, 0, 0)])]
TR = {'00': ['Final boss\'a hiç saldırmasan ne olur?'], '01': ['Diz çök, ölümlü!', 'Sıra sende. Saldır!'],
      '02': ['Hadi ama...', 'Sen oynamadan ben kıpırdayamam!'], '03': ['Peki.', 'Çay ister misin?'],
      '04': ['Üç yüz yıl.', 'Kimse bu kadar kalmamıştı.'], '05': ['Her kahraman ilk saniyede vurdu.', 'Sen kaldın.'],
      '06': ['Eyvah... sayaç doldu!'], '07': ['Diz çök, ölümlü!'], '08': ['Psst... yine çay ister misin?']}
def tr_upper(s): return s.replace('i', 'İ').replace('ı', 'I').replace('â', 'a').upper()
TR_SUB = {k: [tr_upper(x) for x in v] for k, v in TR.items()}
# delivery: the boss loud at first, then bored, then warm, old and quiet; the narrator calm and clear (Enes picked the calm hook)
EXAG = {'00': 0.5, '01': 0.55, '02': 0.55, '03': 0.4, '04': 0.4, '05': 0.4, '06': 0.45, '07': 0.55, '08': 0.35}
PLAN = {'00': [2.3], '01': [1.6, 1.9], '02': [1.1, 1.8], '03': [0.6, 1.4], '04': [1.4, 1.9], '05': [2.2, 0.9], '06': [2.0],
        '07': [1.6], '08': [1.8]}
BOSS_ST = -1.5
def refs():
    src = os.path.join(REPO, 'tts', 'sp_refs'); out = os.path.join(REPO, 'tts', 'na_refs'); os.makedirs(out, exist_ok=True)
    for spk, s in (('N', 'N'), ('B', 'B')):
        shutil.copy(os.path.join(src, f'{s}_en.wav'), os.path.join(out, f'{spk}_en.wav')); print(spk, '<-', s)
def lines_json(lang):
    out = {}
    for k, s, ss in D:
        txt = ' '.join(TR[k]) if lang == 'tr' else ' '.join(x[0] for x in ss)
        out[k] = dict(text=txt, spk=s, exag=EXAG.get(k, 0.5))
    return out
def plan():
    out = os.path.join(multi.TTS_DIR, 'na'); os.makedirs(out, exist_ok=True); dur = {}; txt = {}; sent = {}; spk = {}
    for k, s, ss in D:
        pos = 0.0; sent[k] = []
        for (tx, *_, pause), d in zip(ss, PLAN[k]): pos += pause; sent[k].append([round(pos, 3), round(pos + d, 3), tx]); pos += d
        dur[k] = round(pos, 2); txt[k] = ' '.join(x[0] for x in ss); spk[k] = s
    json.dump({'text': txt, 'dur': dur, 'sent': sent, 'spk': spk, 'planned': True}, open(os.path.join(out, 'script.json'), 'w'), indent=1); print('planned', dur)
def boss_pitch():
    import soundfile as sf, emph
    out = os.path.join(multi.TTS_DIR, 'na')
    for k, s, _ in D:
        if s != 'B': continue
        f = os.path.join(out, k + '.wav'); y, sr = sf.read(f)
        z = emph.shape(y, BOSS_ST, 1.0, 0.0); z = z / max(1e-9, abs(z).max()) * 0.95; sf.write(f, z, sr); print('boss pitch', k, BOSS_ST)
def tighten(max_gap=0.65, keep=0.5):
    """cut inner pauses longer than max_gap down to `keep` s (the clone leaves long silences) and move the sentence timings"""
    import numpy as np, soundfile as sf
    out = os.path.join(multi.TTS_DIR, 'na'); jf = os.path.join(out, 'script.json'); J = json.load(open(jf))
    for k in J['dur']:
        f = os.path.join(out, k + '.wav'); y, sr = sf.read(f); fr = int(0.01 * sr); n = len(y) // fr
        db = 20 * np.log10(np.sqrt((y[:n * fr].reshape(n, fr) ** 2).mean(1)) + 1e-9); v = db > -40
        cuts = []; i = 0
        while i < n:
            if not v[i]:
                j = i
                while j < n and not v[j]: j += 1
                if i > 0 and j < n and (j - i) / 100 > max_gap: cuts.append((i, j))
                i = j
            else: i += 1
        if not cuts: continue
        parts = []; pos = 0; shift = []
        for a, b in cuts:
            m = (a + b) // 2; h = int(keep * 50)
            parts.append(y[pos * fr:(m - h) * fr]); pos = m + h; shift.append(((m - h) / 100, (m + h) / 100))
        parts.append(y[pos * fr:]); z = np.concatenate(parts); sf.write(f, z, sr)
        def mv(t_):
            d = 0.0
            for a_, b_ in shift:
                if t_ >= b_: d += b_ - a_
                elif t_ > a_: d += t_ - a_
            return round(t_ - d, 3)
        J['sent'][k] = [[mv(a_), mv(b_), tx] for a_, b_, tx in J['sent'][k]]; J['dur'][k] = round(len(z) / sr, 2)
        print('tighten', k, len(cuts), '->', J['dur'][k])
    json.dump(J, open(jf, 'w'), indent=1)
if __name__ == '__main__':
    if sys.argv[1] == 'plan': plan()
    elif sys.argv[1] == 'refs': refs()
    else:
        multi.main(D, VOICES, 'na')
        if len(sys.argv) > 2 and sys.argv[2] == 'own':
            boss_pitch(); tighten()
