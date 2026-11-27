"""Voice for "Why do NPCs stand still at night?" (nf = night freeze, 27 Nov 2026). Brief: briefs/night_freeze.md (+ rules filter:
the rule is spoken ("It only sees what moves.", "But fire never stands still."), Bram respawns at dawn and says his repeated line).
English: N narrator + K knight + B Bram (old villager) = Enes's CLONED voice (sp_refs N / K / B), M Marta = raw Kokoro bf_emma
(female, made breathy in the build: a whisper). Turkish: Enes / Betül record the lines (briefs/night_freeze_voice_sheet.md).
Steps:
  python tools/tts/nf.py refs
  python tools/tts/nf.py src                                  # Kokoro for Marta (and placeholders)
  <chatterbox python> tools/tts/clone_lines.py nf en --takes 4
  <chatterbox python> tools/tts/asr_check.py nf --pick
  python tools/tts/nf.py build own"""
import os, sys, json, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import multi
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VOICES = {'K': ('am_adam', 'en-us'), 'B': ('bm_george', 'en-gb'), 'M': ('bf_emma', 'en-gb')}
D = [('00', 'N', [("Why do NPCs stand still at night?", 1.0, 0, 0, 0)]),
     ('01', 'K', [("Hello?", 1.0, 0, 0, 0), ("Is anyone home?", 1.0, 0, 0, 0.2)]),
     ('02', 'N', [("They aren't broken.", 1.0, 0, 0, 0), ("They're hiding.", 1.0, 0, 0, 0.3)]),
     ('03', 'M', [("Stop. Moving.", 0.85, 0, 0, 0)]),
     ('04', 'N', [("It only sees what moves.", 1.0, 0, 0, 0)]),
     ('05', 'K', [("Hide?", 1.0, 0, 0, 0), ("I'm the hero.", 1.0, 0, 0, 0.2)]),
     ('06', 'N', [("But fire never stands still.", 1.0, 0, 0, 0)]),
     ('07', 'N', [("Every night, someone has to move.", 1.0, 0, 0, 0)]),
     ('08', 'N', [("At dawn, every NPC respawns.", 1.0, 0, 0, 0)]),
     ('09', 'B', [("Nice weather today!", 1.0, 0, 0, 0)])]
TR = {'00': ['NPC\'ler geceleri neden kıpırdamaz?'], '01': ['Merhaba?', 'Kimse yok mu?'], '02': ['Bozuk değiller.', 'Saklanıyorlar.'],
      '03': ['Kıpırdama.'], '04': ['O sadece kıpırdayanı görür.'], '05': ['Saklanmak mı?', 'Ben kahramanım.'],
      '06': ['Ama ateş hiç durmaz.'], '07': ['Her gece birinin kıpırdaması gerekir.'], '08': ['Şafakta her NPC yeniden doğar.'],
      '09': ['Bugün hava ne güzel!']}
def tr_upper(s): return s.replace('i', 'İ').replace('ı', 'I').replace('â', 'A').upper()
TR_SUB = {k: [tr_upper(x) for x in v] for k, v in TR.items()}
EXAG = {'00': 0.45, '01': 0.55, '02': 0.4, '04': 0.4, '05': 0.6, '06': 0.45, '07': 0.45, '08': 0.45, '09': 0.65}
PLAN = {'00': [2.2], '01': [0.6, 1.0], '02': [1.1, 0.9], '03': [1.2], '04': [1.5], '05': [0.6, 0.9], '06': [1.6], '07': [2.0], '08': [1.9], '09': [1.3]}
CLONED = ('N', 'K', 'B')
def refs():
    src = os.path.join(REPO, 'tts', 'sp_refs'); out = os.path.join(REPO, 'tts', 'nf_refs'); os.makedirs(out, exist_ok=True)
    for spk in CLONED: shutil.copy(os.path.join(src, f'{spk}_en.wav'), os.path.join(out, f'{spk}_en.wav')); print(spk)
def lines_json(lang):
    out = {}
    for k, s, ss in D:
        if lang == 'en' and s not in CLONED: continue                       # Marta = Kokoro, not cloned
        txt = ' '.join(TR[k]) if lang == 'tr' else ' '.join(x[0] for x in ss)
        out[k] = dict(text=txt, spk=s, exag=EXAG.get(k, 0.5))
    return out
def whisper():
    """Marta's line: breathy whisper (band-limited voice + shaped noise following its envelope), quieter"""
    import numpy as np, soundfile as sf
    f = os.path.join(multi.TTS_DIR, 'nf', '03.wav')
    if not os.path.exists(f): return
    y, sr = sf.read(f); y = y if y.ndim == 1 else y.mean(1)
    from scipy.signal import butter, sosfilt
    env = np.sqrt(np.convolve(y ** 2, np.ones(int(0.02 * sr)) / int(0.02 * sr), 'same'))
    nse = sosfilt(butter(4, [1800, 7000], 'bandpass', fs=sr, output='sos'), np.random.default_rng(3).normal(0, 1, len(y))) * env * 2.2
    v = sosfilt(butter(4, [600, 6000], 'bandpass', fs=sr, output='sos'), y) * 0.55
    z = v + nse; z = z / np.abs(z).max() * 0.95; sf.write(f, z, sr); print('whisper 03')
def tighten(max_gap=0.45, keep=0.35):
    import numpy as np, soundfile as sf
    out = os.path.join(multi.TTS_DIR, 'nf'); jf = os.path.join(out, 'script.json'); J = json.load(open(jf))
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
        multi.main(D, VOICES, 'nf', TR)
        if len(sys.argv) > 2 and sys.argv[2] == 'own': whisper(); tighten()
