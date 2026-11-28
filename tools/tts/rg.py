"""Voice for "Why do bosses glow red before they attack?" (rg = red glow, 28 Nov 2026). Brief: briefs/red_glow.md (Enes approved + 3 touches).
English = Enes's CLONED voice, every speaker male:
  N narrator  <- sp_refs N (dry, tense)        K the young knight <- sp_refs K
  M the master (old knight trapped in the crystal / helmet) <- sp_refs B (old), muffled glass / helmet ring in the video build
  H the Hollow King <- sp_refs N, pitched DOWN PITCH['H'] st here + iron reverb in the video build (an empty helmet speaks)
Turkish: Enes records every line himself (TR text below = subtitles + the recording sheet briefs/red_glow_voice_sheet.md).
Steps:
  python tools/tts/rg.py refs
  <chatterbox python> tools/tts/clone_lines.py rg en --takes 4
  <chatterbox python> tools/tts/asr_check.py rg --pick
  python tools/tts/rg.py build own"""
import os, sys, json, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import multi
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VOICES = {'K': ('am_adam', 'en-us'), 'M': ('bm_george', 'en-gb'), 'H': ('am_adam', 'en-us')}
D = [('00', 'N', [("Why do bosses glow red before they attack?", 1.0, 0, 0, 0)]),
     ('01', 'N', [("Every hero dodges the glow.", 1.0, 0, 0, 0), ("Nobody asks who lights it.", 1.0, 0, 0, 0.25)]),
     ('02', 'M', [("Left!", 1.0, 0, 0, 0), ("Now!", 1.0, 0, 0, 0.1)]),
     ('03', 'K', [("Master?", 1.0, 0, 0, 0), ("You fell here...", 1.0, 0, 0, 0.25)]),
     ('04', 'M', [("Forty heroes since.", 1.0, 0, 0, 0), ("I warned every one.", 1.0, 0, 0, 0.25)]),
     ('05', 'H', [("Traitor.", 1.0, 0, 0, 0)]),
     ('06', 'M', [("Run, boy!", 1.0, 0, 0, 0)]),                                    # cut off after "Run, b-" in the build (cutoff())
     ('07', 'N', [("No glow.", 1.0, 0, 0, 0), ("No warning.", 1.0, 0, 0, 0.2), ("One heart left.", 1.0, 0, 0, 0.2)]),
     ('08', 'N', [("He learned the hero's tells.", 1.0, 0, 0, 0), ("Now he fakes his own.", 1.0, 0, 0, 0.2)]),
     ('09', 'M', [("Still here, boy.", 1.0, 0, 0, 0), ("Left!", 1.0, 0, 0, 0.15)]),
     ('10', 'N', [("Dodge again, or save him?", 1.0, 0, 0, 0)])]
TR = {'00': ['Patronlar saldırmadan önce neden kırmızı parlar?'], '01': ['Her kahraman ışıktan kaçar.', 'Kimse onu kimin yaktığını sormaz.'],
      '02': ['Sola!', 'Hemen!'], '03': ['Usta?', 'Sen burada düşmüştün...'], '04': ['O günden beri kırk kahraman.', 'Hepsini uyardım.'],
      '05': ['Hain.'], '06': ['Kaç, evl—'], '07': ['Işık yok.', 'Uyarı yok.', 'Tek can kaldı.'],
      '08': ['Kahramanı okumayı öğrendi.', 'Şimdi o kandırıyor.'], '09': ['Hâlâ buradayım evlat.', 'Sola!'],
      '10': ['Yine kaçar mısın, yoksa onu kurtarır mısın?']}
def tr_upper(s): return s.replace('i', 'İ').replace('ı', 'I').replace('â', 'A').replace('—', '-').upper()      # the pixel font has no Â
TR_SUB = {k: [tr_upper(x) for x in v] for k, v in TR.items()}
# delivery: narrator low + tense, never shouting (hook clean); the master urgent / tired / warm; the knight shocked, breaking;
# the boss slow and flat (the pitch-down carries the weight)
EXAG = {'00': 0.45, '01': 0.4, '02': 0.65, '03': 0.55, '04': 0.4, '05': 0.35, '06': 0.65, '07': 0.4, '08': 0.4, '09': 0.55, '10': 0.45}
PLAN = {'00': [2.2], '01': [1.3, 1.4], '02': [0.4, 0.4], '03': [0.6, 1.0], '04': [1.2, 1.2], '05': [0.8], '06': [0.8],
        '07': [0.7, 0.8, 1.0], '08': [1.4, 1.1], '09': [0.9, 0.4], '10': [1.6]}
PITCH = {'H': -6.0}
TEMPO = {'H': 0.92}
def refs():
    src = os.path.join(REPO, 'tts', 'sp_refs'); out = os.path.join(REPO, 'tts', 'rg_refs'); os.makedirs(out, exist_ok=True)
    for spk, s in (('N', 'N'), ('K', 'K'), ('M', 'B'), ('H', 'N')):
        shutil.copy(os.path.join(src, f'{s}_en.wav'), os.path.join(out, f'{spk}_en.wav')); print(spk, '<-', s)
def lines_json(lang):
    out = {}
    for k, s, ss in D:
        txt = ' '.join(TR[k]) if lang == 'tr' else ' '.join(x[0] for x in ss)
        out[k] = dict(text=txt, spk=s, exag=EXAG.get(k, 0.5))
    return out
def pitch():
    """after `build own`: the boss line pitched down + slowed (sentence timings scaled)"""
    import soundfile as sf, emph
    out = os.path.join(multi.TTS_DIR, 'rg'); jf = os.path.join(out, 'script.json'); J = json.load(open(jf))
    for k, s, _ in D:
        if s not in PITCH: continue
        f = os.path.join(out, k + '.wav'); y, sr = sf.read(f); tp = TEMPO.get(s, 1.0)
        z = emph.shape(y, PITCH[s], tp, 0.0); z = z / max(1e-9, abs(z).max()) * 0.95; sf.write(f, z, sr)
        J['sent'][k] = [[round(a / tp, 3), round(b / tp, 3), tx] for a, b, tx in J['sent'][k]]; J['dur'][k] = round(len(z) / sr, 2)
        print('pitch', k, s, PITCH[s], 'tempo', tp, '->', J['dur'][k])
    json.dump(J, open(jf, 'w'), indent=1)
def cutoff(key='06'):
    """'Run, boy!' -> 'Run, b-': keep the first word, the pause, and ~70 ms of the second word, then a 6 ms cut (the crush covers it)"""
    import numpy as np, soundfile as sf
    out = os.path.join(multi.TTS_DIR, 'rg'); jf = os.path.join(out, 'script.json'); J = json.load(open(jf))
    f = os.path.join(out, key + '.wav'); y, sr = sf.read(f); fr = int(0.01 * sr); n = len(y) // fr
    db = 20 * np.log10(np.sqrt((y[:n * fr].reshape(n, fr) ** 2).mean(1)) + 1e-9); v = db > (db.max() - 30)
    on = [i for i in range(1, n) if v[i] and not v[i - 1]]                       # word onsets (10 ms frames)
    first = int(np.argmax(v))
    nxt = [i for i in on if i > first + 15]
    if not nxt: print('cutoff: no second word found, kept whole'); return
    end = (nxt[0] + 7) * fr; z = y[:end].copy(); r = int(0.006 * sr); z[-r:] *= np.linspace(1, 0, r)
    sf.write(f, z, sr); J['dur'][key] = round(len(z) / sr, 2); J['sent'][key] = [[J['sent'][key][0][0], round(len(z) / sr, 3), 'RUN, B-']]
    json.dump(J, open(jf, 'w'), indent=1); print('cutoff', key, '->', J['dur'][key])
def tighten(max_gap=0.45, keep=0.32):
    """cut inner pauses longer than max_gap down to `keep` s (the clone leaves long silences) and move the sentence timings"""
    import numpy as np, soundfile as sf
    out = os.path.join(multi.TTS_DIR, 'rg'); jf = os.path.join(out, 'script.json'); J = json.load(open(jf))
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
            m = (a + b) // 2; h = (b - a - int(keep * 100)) // 2             # remove the middle, keep `keep` s of the pause (the old copy removed only `keep`)
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
        multi.main(D, VOICES, 'rg', TR)
        if len(sys.argv) > 2 and sys.argv[2] == 'own' and os.environ.get('SUB_LANG') != 'tr': pitch(); cutoff(); tighten()
