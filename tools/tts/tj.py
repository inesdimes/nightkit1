"""Voice for "Why do tutorials make you jump?" (tj = tutorial jump, 27 Nov 2026). Story: GPT brief from Enes (27 Nov), Claude additions:
the spoken title as line 00 (the bridge troll hook lesson), sentence splits for the subtitles.
English = Enes's CLONED voice (recipe of tools/tts/ms.py): N narrator <- sp_refs N, K knight <- sp_refs K,
I instructor <- sp_refs B (his boss takes) pitched UP INST_ST semitones in the build (thin, strict, a traffic warden).
Turkish: Enes records the lines himself (TR text below = subtitles + the recording sheet briefs/tutorial_jump_voice_sheet.md).
Steps:
  python tools/tts/tj.py refs
  <chatterbox python> tools/tts/clone_lines.py tj en --takes 4
  <chatterbox python> tools/tts/asr_check.py tj --pick
  python tools/tts/tj.py build own"""
import os, sys, json, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import multi
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VOICES = {'K': ('am_adam', 'en-us'), 'I': ('bm_george', 'en-gb')}
D = [('00', 'N', [("Why do tutorials make you jump?", 1.0, 0, 0, 0)]),
     ('01', 'N', [("One jump opens the gate.", 1.0, 0, 0, 0), ("Watch the counter.", 1.0, 0, 0, 0.25)]),
     ('02', 'K', [("See?", 1.0, 0, 0, 0), ("There's a shortcut in every tutorial.", 1.0, 0, 0, 0.2)]),
     ('03', 'I', [("That was the easy one.", 1.0, 0, 0, 0), ("The next one's higher.", 1.0, 0, 0, 0.2)]),
     ('04', 'N', [("Three hurdles down.", 1.0, 0, 0, 0), ("The counter still reads zero.", 1.0, 0, 0, 0.25)]),
     ('05', 'I', [("Stop.", 1.0, 0, 0, 0), ("I'll show you how it's done.", 1.0, 0, 0, 0.2)]),
     ('06', 'K', [("Good.", 1.0, 0, 0, 0), ("Stand right there.", 1.0, 0, 0, 0.2)]),
     ('07', 'I', [("Wait.", 1.0, 0, 0, 0), ("That counted?", 1.0, 0, 0, 0.2)]),
     ('08', 'N', [("The next lesson needs two jumps.", 1.0, 0, 0, 0)]),
     ('09', 'K', [("Want to try that twice?", 1.0, 0, 0, 0)])]
TR = {'00': ['Eğitim bölümleri neden hep zıplatır?'], '01': ['Tek zıplama kapıyı açar.', 'Sayaca bak.'],
      '02': ['Gördün mü?', 'Her eğitimde bir kestirme vardır.'], '03': ['O kolaydı.', 'Sıradaki daha yüksek.'],
      '04': ['Üç engel gitti.', 'Sayaç hâlâ sıfır.'], '05': ['Dur.', 'Nasıl yapıldığını göstereyim.'],
      '06': ['Güzel.', 'Tam orada dur.'], '07': ['Bir dakika.', 'Bu sayıldı mı?'],
      '08': ['Sıradaki ders iki zıplama istiyor.'], '09': ['Bunu iki kere denemek ister misin?']}
def tr_upper(s): return s.replace('i', 'İ').replace('ı', 'I').replace('â', 'A').upper()      # the pixel font has no Â
TR_SUB = {k: [tr_upper(x) for x in v] for k, v in TR.items()}
# delivery: narrator calm and dry; knight cocky, grinning; instructor strict, then thrown, then lost
EXAG = {'00': 0.5, '01': 0.45, '02': 0.6, '03': 0.5, '04': 0.45, '05': 0.55, '06': 0.55, '07': 0.5, '08': 0.45, '09': 0.6}
PLAN = {'00': [2.0], '01': [1.4, 1.1], '02': [0.5, 1.8], '03': [1.2, 1.2], '04': [1.1, 1.5], '05': [0.5, 1.5], '06': [0.5, 1.0],
        '07': [0.5, 0.9], '08': [1.8], '09': [1.4]}
INST_ST = 2.0
def refs():
    src = os.path.join(REPO, 'tts', 'sp_refs'); out = os.path.join(REPO, 'tts', 'tj_refs'); os.makedirs(out, exist_ok=True)
    for spk, s in (('N', 'N'), ('I', 'B'), ('K', 'K')):
        shutil.copy(os.path.join(src, f'{s}_en.wav'), os.path.join(out, f'{spk}_en.wav')); print(spk, '<-', s)
def lines_json(lang):
    out = {}
    for k, s, ss in D:
        txt = ' '.join(TR[k]) if lang == 'tr' else ' '.join(x[0] for x in ss)
        out[k] = dict(text=txt, spk=s, exag=EXAG.get(k, 0.5))
    return out
def plan():
    out = os.path.join(multi.TTS_DIR, 'tj'); os.makedirs(out, exist_ok=True); dur = {}; txt = {}; sent = {}; spk = {}
    for k, s, ss in D:
        pos = 0.0; sent[k] = []
        for (tx, *_, pause), d in zip(ss, PLAN[k]): pos += pause; sent[k].append([round(pos, 3), round(pos + d, 3), tx]); pos += d
        dur[k] = round(pos, 2); txt[k] = ' '.join(x[0] for x in ss); spk[k] = s
    json.dump({'text': txt, 'dur': dur, 'sent': sent, 'spk': spk, 'planned': True}, open(os.path.join(out, 'script.json'), 'w'), indent=1); print('planned', dur)
def inst_pitch():
    """after `build own`: pitch the instructor's finished lines up (duration kept, sentence timings stay valid)"""
    import soundfile as sf, emph
    out = os.path.join(multi.TTS_DIR, 'tj')
    for k, s, _ in D:
        if s != 'I': continue
        f = os.path.join(out, k + '.wav'); y, sr = sf.read(f)
        z = emph.shape(y, INST_ST, 1.0, 0.0); z = z / max(1e-9, abs(z).max()) * 0.95; sf.write(f, z, sr); print('instructor pitch', k, INST_ST)
def tighten(max_gap=0.45, keep=0.35):
    """cut inner pauses longer than max_gap down to `keep` s (the clone leaves long silences) and move the sentence timings"""
    import numpy as np, soundfile as sf
    out = os.path.join(multi.TTS_DIR, 'tj'); jf = os.path.join(out, 'script.json'); J = json.load(open(jf))
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
        multi.main(D, VOICES, 'tj', TR)
        if len(sys.argv) > 2 and sys.argv[2] == 'own': inst_pitch(); tighten()
