"""Voice for "Why do bridge trolls want tolls?" (bt, 26 Nov 2026). Brief: briefs/BRIDGE_TROLL_FULL_BRIEF.txt.
English = Enes's CLONED voice (same recipe as Save Point, tools/tts/sp.py): one reference per speaker, cut from his own takes.
  N narrator <- tts/sp_refs/N_en.wav (his narrator takes)
  T troll    <- tts/sp_refs/B_en.wav (his tired old boss + guardian takes), pitched down TROLL_ST semitones in the build
  K knight   <- tts/sp_refs/K_en.wav (his knight takes)
Turkish: Enes records the TR lines himself (26 Nov: the TR clone was too artificial) -> TR text here is only for the subtitles
and the recording sheet (briefs/bridge_troll_voice_sheet.md). No Turkish voice is generated.
Steps:
  python tools/tts/bt.py refs                          # tts/bt_refs/<N|T|K>_en.wav (copies of the sp refs)
  <chatterbox python> tools/tts/clone_lines.py bt en --takes 3   # -> tts/bt_own/<key>_all.wav
  python tools/tts/bt.py build own                     # trims + levels + sentence timings -> tts/bt/script.json
  python tools/tts/bt.py plan                          # planned timings only (no audio)"""
import os, sys, json, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import multi
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VOICES = {'K': ('am_adam', 'en-us'), 'T': ('bm_george', 'en-gb')}
D = [('00', 'N', [("Why do bridge trolls want tolls?", 1.0, 0, 0, 0)]),          # hook; Enes 26 Nov: this v2 take beat the 'livelier' v3 one          # hook (Enes 26 Nov): the title, spoken with weight
     ('01', 'T', [("One coin.", 1.0, 0, 0, 0), ("To cross.", 1.0, 0, 0, 0.25)]),
     ('02', 'K', [("Or I cut you in half.", 1.0, 0, 0, 0)]),
     ('03', 'T', [("Fine. Go ahead and cross.", 1.0, 0, 0, 0)]),
     ('04', 'N', [("The knight didn't pay.", 1.0, 0, 0, 0), ("The bridge did.", 1.0, 0, 0, 0.3)]),
     ('05', 'N', [("Halfway over, the old arch cracked.", 1.0, 0, 0, 0)]),
     ('06', 'T', [("The king stopped paying for this bridge forty years ago.", 1.0, 0, 0, 0)]),
     ('07', 'K', [("Why didn't you just say so?", 1.0, 0, 0, 0)]),
     ('08', 'T', [("You had a sword.", 1.0, 0, 0, 0)]),
     ('09', 'N', [("The knight emptied his purse.", 1.0, 0, 0, 0)]),
     ('10', 'T', [("Every coin is one stone.", 1.0, 0, 0, 0)]),
     ('11', 'N', [("By dawn, the crack was gone.", 1.0, 0, 0, 0)]),
     ('12', 'N', [("Trolls don't want your gold.", 1.0, 0, 0, 0), ("Bridges do.", 1.0, 0, 0, 0.3)])]
TR = {'00': ['Köprü trolleri neden geçiş parası ister?'], '01': ['Bir sikke.', 'Geçmek için.'], '02': ['Yoksa seni ikiye bölerim.'], '03': ['Peki. Buyur, geç.'],
      '04': ['Şövalye ödemedi.', 'Köprü ödedi.'], '05': ['Yarı yolda eski kemer çatladı.'],
      '06': ['Kral bu köprüye kırk yıl önce para vermeyi bıraktı.'], '07': ['Neden baştan söylemedin?'], '08': ['Elinde kılıç vardı.'],
      '09': ['Şövalye kesesini boşalttı.'], '10': ['Her sikke bir taş.'], '11': ['Şafakta çatlak kapanmıştı.'],
      '12': ['Troller altınını istemez.', 'Köprüler ister.']}
def tr_upper(s): return s.replace('i', 'İ').replace('ı', 'I').upper()
TR_SUB = {k: [tr_upper(x) for x in v] for k, v in TR.items()}
# delivery (Chatterbox exaggeration): the troll is slow, gruff and tired; the knight cocky, then thrown
EXAG = {'00': 0.8, '01': 0.45, '03': 0.4, '06': 0.5, '08': 0.35, '10': 0.4, '02': 0.65, '07': 0.6, '12': 0.55}
PLAN = {'00': [2.2], '01': [0.8, 0.7], '02': [1.4], '03': [1.5], '04': [1.3, 1.0], '05': [2.1], '06': [3.2], '07': [1.4], '08': [1.1],
        '09': [1.7], '10': [1.6], '11': [1.8], '12': [1.6, 0.9]}
TROLL_ST = -2.0                       # the troll's lines are pitched down a little in the build (bigger, heavier)
def refs():
    src = os.path.join(REPO, 'tts', 'sp_refs'); out = os.path.join(REPO, 'tts', 'bt_refs'); os.makedirs(out, exist_ok=True)
    for spk, s in (('N', 'N'), ('T', 'B'), ('K', 'K')):
        shutil.copy(os.path.join(src, f'{s}_en.wav'), os.path.join(out, f'{spk}_en.wav')); print(spk, '<-', s)
def lines_json(lang):
    out = {}
    for k, s, ss in D:
        txt = ' '.join(TR[k]) if lang == 'tr' else ' '.join(x[0] for x in ss)
        out[k] = dict(text=txt, spk=s, exag=EXAG.get(k, 0.5))
    return out
def plan():
    out = os.path.join(multi.TTS_DIR, 'bt'); os.makedirs(out, exist_ok=True); dur = {}; txt = {}; sent = {}; spk = {}
    for k, s, ss in D:
        pos = 0.0; sent[k] = []
        for (tx, *_, pause), d in zip(ss, PLAN[k]): pos += pause; sent[k].append([round(pos, 3), round(pos + d, 3), tx]); pos += d
        dur[k] = round(pos, 2); txt[k] = ' '.join(x[0] for x in ss); spk[k] = s
    json.dump({'text': txt, 'dur': dur, 'sent': sent, 'spk': spk, 'planned': True}, open(os.path.join(out, 'script.json'), 'w'), indent=1); print('planned', dur)
def troll_pitch():
    """after `build own`: pitch the troll's finished lines down (duration kept, sentence timings stay valid)"""
    import soundfile as sf, emph
    out = os.path.join(multi.TTS_DIR, 'bt')
    for k, s, _ in D:
        if s != 'T': continue
        f = os.path.join(out, k + '.wav'); y, sr = sf.read(f)
        z = emph.shape(y, TROLL_ST, 1.0, 0.0); z = z / max(1e-9, abs(z).max()) * 0.95; sf.write(f, z, sr); print('troll pitch', k, TROLL_ST)
def tighten(max_gap=0.45, keep=0.4):
    """the clone leaves long silences inside some lines (01: 1.1 s between 'One coin.' and 'To cross.'): cut every inner pause
    longer than max_gap down to `keep` seconds and move the sentence timings in script.json with it"""
    import numpy as np, soundfile as sf
    out = os.path.join(multi.TTS_DIR, 'bt'); jf = os.path.join(out, 'script.json'); J = json.load(open(jf))
    for k in J['dur']:
        f = os.path.join(out, k + '.wav'); y, sr = sf.read(f); fr = int(0.01 * sr); n = len(y) // fr
        db = 20 * np.log10(np.sqrt((y[:n * fr].reshape(n, fr) ** 2).mean(1)) + 1e-9); v = db > -40
        cuts = []; i = 0                                                      # (start, end) frames of silences to shorten
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
            m = (a + b) // 2; h = int(keep * 50)                              # keep keep/2 on each side of the middle
            parts.append(y[pos * fr:(m - h) * fr]); pos = m + h; shift.append(((m - h) / 100, (m + h) / 100))
        parts.append(y[pos * fr:]); z = np.concatenate(parts); sf.write(f, z, sr)
        def mv(t_):
            d = 0.0
            for a_, b_ in shift:
                if t_ >= b_: d += b_ - a_
                elif t_ > a_: d += t_ - a_
            return round(t_ - d, 3)
        J['sent'][k] = [[mv(a_), mv(b_), tx] for a_, b_, tx in J['sent'][k]]; J['dur'][k] = round(len(z) / sr, 2)
        print('tighten', k, len(cuts), 'pause(s) ->', J['dur'][k], J['sent'][k])
    json.dump(J, open(jf, 'w'), indent=1)
if __name__ == '__main__':
    if sys.argv[1] == 'plan': plan()
    elif sys.argv[1] == 'refs': refs()
    else:
        multi.main(D, VOICES, 'bt')
        if len(sys.argv) > 2 and sys.argv[2] == 'own': troll_pitch(); tighten()
