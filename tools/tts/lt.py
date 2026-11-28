"""Voice for "Why do loading screens show tips?" (lt = loading tips, 28 Nov 2026). Brief: briefs/loading_tips.md (v2, lines locked by Enes 28 Nov).
English = Enes's CLONED voice (recipe of tools/tts/tj.py), every speaker male:
  N narrator <- sp_refs N (dry)       K knight <- sp_refs K (puzzled)
  O Bob, goblin foreman <- sp_refs K, pitched UP PITCH['O'] st in the build (a small, loud, panicking boss)
  G goblin builder      <- sp_refs K, pitched up more (the smallest voice in the crew)
  D the door goblin     <- sp_refs B, pitched DOWN (deadpan, wooden)
Turkish: Enes records every line himself (TR text below = subtitles + the recording sheet briefs/loading_tips_voice_sheet.md).
Steps:
  python tools/tts/lt.py refs
  <chatterbox python> tools/tts/clone_lines.py lt en --takes 4
  <chatterbox python> tools/tts/asr_check.py lt --pick
  python tools/tts/lt.py build own"""
import os, sys, json, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import multi
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VOICES = {'K': ('am_adam', 'en-us'), 'O': ('am_adam', 'en-us'), 'G': ('am_adam', 'en-us'), 'D': ('bm_george', 'en-gb')}
D = [('00', 'N', [("Why do loading screens show tips?", 1.0, 0, 0, 0)]),
     ('01', 'O', [("Too fast!", 1.0, 0, 0, 0), ("Slow it down!", 1.0, 0, 0, 0.15), ("He's at the door!", 1.0, 0, 0, 0.15)]),
     ('02', 'N', [("The tips aren't for you.", 1.0, 0, 0, 0), ("They're for them.", 1.0, 0, 0, 0.25)]),
     ('03', 'N', [("Every tip you read buys them time.", 1.0, 0, 0, 0)]),
     ('04', 'O', [("Chest!", 1.0, 0, 0, 0), ("Torches!", 1.0, 0, 0, 0.15), ("Dragon!", 1.0, 0, 0, 0.15), ("Faster!", 1.0, 0, 0, 0.15)]),
     ('05', 'G', [("Boss, the chest winked at me.", 1.0, 0, 0, 0)]),
     ('06', 'O', [("Ninety-nine percent!", 1.0, 0, 0, 0), ("We made it, boys!", 1.0, 0, 0, 0.15)]),
     ('07', 'G', [("Boss...", 1.0, 0, 0, 0), ("where's the door?", 1.0, 0, 0, 0.3)]),
     ('08', 'O', [("Places!", 1.0, 0, 0, 0), ("Everybody, places!", 1.0, 0, 0, 0.15)]),
     ('09', 'D', [("Creak.", 1.0, 0, 0, 0)]),
     ('10', 'K', [("Huh.", 1.0, 0, 0, 0), ("Nice door.", 1.0, 0, 0, 0.2), ("Very... wooden.", 1.0, 0, 0, 0.2)]),
     ('11', 'O', [("Plus one gold?", 1.0, 0, 0, 0)]),
     ('12', 'O', [("Still hired!", 1.0, 0, 0, 0)]),
     ('13', 'N', [("Next level's loading.", 1.0, 0, 0, 0), ("Read the tips... or skip?", 1.0, 0, 0, 0.3)])]
TR = {'00': ['Yükleme ekranları neden ipucu gösterir?'], '01': ['Çok hızlı!', 'Yavaşlat şunu!', 'Kapıya geldi!'],
      '02': ['İpuçları senin için değil.', 'Onlar için.'], '03': ['Okuduğun her ipucu onlara zaman kazandırır.'],
      '04': ['Sandık!', 'Meşaleler!', 'Ejderha!', 'Çabuk!'], '05': ['Patron, sandık bana göz kırptı.'],
      '06': ['Yüzde doksan dokuz!', 'Yetiştirdik çocuklar!'], '07': ['Patron...', 'kapı nerede?'],
      '08': ['Yerlerinize!', 'Herkes yerine!'], '09': ['...Gıcırt.'], '10': ['Hıh.', 'Güzel kapı.', 'Pek bir... tahta.'],
      '11': ['Artı bir altın?'], '12': ['Hâlâ işteyim!'], '13': ['Sıradaki level yükleniyor.', 'İpuçlarını okur musun... geçer misin?']}
def tr_upper(s): return s.replace('i', 'İ').replace('ı', 'I').replace('â', 'A').upper()      # the pixel font has no Â
TR_SUB = {k: [tr_upper(x) for x in v] for k, v in TR.items()}
# delivery: narrator calm + dry (the hook clean, Bridge Troll lesson: no high exaggeration on the clone); Bob panics, barks, cheers,
# then sheepish; the small goblin worried; the door flat; the knight slow and puzzled
EXAG = {'00': 0.45, '01': 0.65, '02': 0.4, '03': 0.4, '04': 0.65, '05': 0.5, '06': 0.65, '07': 0.45, '08': 0.65, '09': 0.3,
        '10': 0.45, '11': 0.45, '12': 0.55, '13': 0.45}
PLAN = {'00': [2.0], '01': [0.6, 0.8, 0.9], '02': [1.2, 0.9], '03': [1.7], '04': [0.4, 0.5, 0.5, 0.5], '05': [1.5],
        '06': [1.2, 1.0], '07': [0.5, 0.9], '08': [0.5, 1.0], '09': [0.7], '10': [0.4, 0.6, 1.0], '11': [0.9], '12': [0.7],
        '13': [1.2, 1.6]}
PITCH = {'O': 3.0, 'G': 5.0, 'D': -2.0}
TEMPO = {'O': 1.12, 'G': 1.05}                      # Bob panics: a little faster (keeps the short near 31 s)
def refs():
    src = os.path.join(REPO, 'tts', 'sp_refs'); out = os.path.join(REPO, 'tts', 'lt_refs'); os.makedirs(out, exist_ok=True)
    for spk, s in (('N', 'N'), ('K', 'K'), ('O', 'K'), ('G', 'K'), ('D', 'B')):
        shutil.copy(os.path.join(src, f'{s}_en.wav'), os.path.join(out, f'{spk}_en.wav')); print(spk, '<-', s)
def lines_json(lang):
    out = {}
    for k, s, ss in D:
        txt = ' '.join(TR[k]) if lang == 'tr' else ' '.join(x[0] for x in ss)
        out[k] = dict(text=txt, spk=s, exag=EXAG.get(k, 0.5))
    return out
def goblin_pitch():
    """after `build own`: pitch the goblins' finished lines; Bob also talks faster (TEMPO: he panics; the sentence timings are scaled)"""
    import soundfile as sf, emph
    out = os.path.join(multi.TTS_DIR, 'lt'); jf = os.path.join(out, 'script.json'); J = json.load(open(jf))
    for k, s, _ in D:
        if s not in PITCH: continue
        f = os.path.join(out, k + '.wav'); y, sr = sf.read(f); tp = TEMPO.get(s, 1.0)
        z = emph.shape(y, PITCH[s], tp, 0.0); z = z / max(1e-9, abs(z).max()) * 0.95; sf.write(f, z, sr)
        J['sent'][k] = [[round(a / tp, 3), round(b / tp, 3), tx] for a, b, tx in J['sent'][k]]; J['dur'][k] = round(len(z) / sr, 2)
        print('pitch', k, s, PITCH[s], 'tempo', tp, '->', J['dur'][k])
    json.dump(J, open(jf, 'w'), indent=1)
def tighten(max_gap=0.45, keep=0.35):
    """cut inner pauses longer than max_gap down to `keep` s (the clone leaves long silences) and move the sentence timings"""
    import numpy as np, soundfile as sf
    out = os.path.join(multi.TTS_DIR, 'lt'); jf = os.path.join(out, 'script.json'); J = json.load(open(jf))
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
    if sys.argv[1] == 'refs': refs()
    else:
        multi.main(D, VOICES, 'lt', TR)
        if len(sys.argv) > 2 and sys.argv[2] == 'own' and os.environ.get('SUB_LANG') != 'tr': goblin_pitch(); tighten()
