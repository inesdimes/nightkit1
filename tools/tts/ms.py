"""Voice for "Why do shopkeepers buy your junk?" (ms = mimic shop, 26 Nov 2026). Brief: briefs/MIMIC_SHOP_FULL_BRIEF.txt.
English = Enes's CLONED voice (recipe of tools/tts/bt.py / sp.py): N narrator <- sp_refs N, K hero <- sp_refs K,
S shopkeeper <- sp_refs B (his tired-boss takes) pitched UP SHOP_ST semitones in the build (thin, too friendly, wrong).
Turkish: Enes records the lines himself (TR text below is for the subtitles + the recording sheet).
Steps:
  python tools/tts/ms.py refs
  <chatterbox python> tools/tts/clone_lines.py ms en --takes 4
  <chatterbox python> tools/tts/asr_check.py ms --pick        # Whisper: keep the takes that say the right words
  python tools/tts/ms.py build own"""
import os, sys, json, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import multi
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VOICES = {'K': ('am_adam', 'en-us'), 'S': ('bm_george', 'en-gb')}
D = [('00', 'N', [("Why do shopkeepers buy your junk?", 1.0, 0, 0, 0)]),          # hook (Enes 26 Nov): the title, spoken with weight
     ('01', 'S', [("A rusty sword? Sold, my friend.", 1.0, 0, 0, 0)]),
     ('02', 'N', [("He bought everything.", 1.0, 0, 0, 0), ("Every bent spoon.", 1.0, 0, 0, 0.25), ("Every broken shield.", 1.0, 0, 0, 0.25)]),
     ('03', 'K', [("What do you even do with all this junk?", 1.0, 0, 0, 0)]),
     ('04', 'S', [("Oh... I eat well.", 1.0, 0, 0, 0)]),
     ('05', 'N', [("He never blinked.", 1.0, 0, 0, 0), ("And his gold was always wet.", 1.0, 0, 0, 0.3)]),
     ('06', 'K', [("Can I see the back room?", 1.0, 0, 0, 0)]),
     ('07', 'S', [("There is no back room.", 1.0, 0, 0, 0)]),
     ('08', 'N', [("Mimics learned.", 1.0, 0, 0, 0), ("Heroes stopped opening chests.", 1.0, 0, 0, 0.3)]),
     ('09', 'N', [("But nobody ever skips the shop.", 1.0, 0, 0, 0)])]
TR = {'00': ['Tüccarlar neden hurdalarını satın alır?'], '01': ['Paslı bir kılıç mı? Satıldı, dostum.'],
      '02': ['Her şeyi alıyordu.', 'Her eğri kaşığı.', 'Her kırık kalkanı.'], '03': ['Bütün bu hurdayla ne yapıyorsun?'],
      '04': ['Ah... İyi besleniyorum.'], '05': ['Hiç göz kırpmıyordu.', 'Ve altınları hep ıslaktı.'], '06': ['Arka odayı görebilir miyim?'],
      '07': ['Arka oda yok.'], '08': ['Mimikler insan doğasını öğrendi.', 'Kahramanlar da sandık açmayı bıraktı.'], '09': ['Ama kimse hurdasını satacağı dükkânı atlamaz.']}
def tr_upper(s): return s.replace('i', 'İ').replace('ı', 'I').replace('â', 'a').upper()      # the pixel font has no Â
TR_SUB = {k: [tr_upper(x) for x in v] for k, v in TR.items()}
# delivery: the shopkeeper warm and wrong; the hero casual, then uneasy; the narrator low and slow (scary)
EXAG = {'00': 0.55, '01': 0.6, '04': 0.45, '07': 0.35, '03': 0.55, '06': 0.4, '05': 0.4, '08': 0.45, '09': 0.5}
PLAN = {'00': [2.1], '01': [2.0], '02': [1.2, 1.0, 1.1], '03': [1.9], '04': [1.4], '05': [1.1, 1.6], '06': [1.3], '07': [1.3],
        '08': [1.0, 1.8], '09': [1.8]}
SHOP_ST = 2.0
def refs():
    src = os.path.join(REPO, 'tts', 'sp_refs'); out = os.path.join(REPO, 'tts', 'ms_refs'); os.makedirs(out, exist_ok=True)
    for spk, s in (('N', 'N'), ('S', 'B'), ('K', 'K')):
        shutil.copy(os.path.join(src, f'{s}_en.wav'), os.path.join(out, f'{spk}_en.wav')); print(spk, '<-', s)
def lines_json(lang):
    out = {}
    for k, s, ss in D:
        txt = ' '.join(TR[k]) if lang == 'tr' else ' '.join(x[0] for x in ss)
        out[k] = dict(text=txt, spk=s, exag=EXAG.get(k, 0.5))
    return out
def plan():
    out = os.path.join(multi.TTS_DIR, 'ms'); os.makedirs(out, exist_ok=True); dur = {}; txt = {}; sent = {}; spk = {}
    for k, s, ss in D:
        pos = 0.0; sent[k] = []
        for (tx, *_, pause), d in zip(ss, PLAN[k]): pos += pause; sent[k].append([round(pos, 3), round(pos + d, 3), tx]); pos += d
        dur[k] = round(pos, 2); txt[k] = ' '.join(x[0] for x in ss); spk[k] = s
    json.dump({'text': txt, 'dur': dur, 'sent': sent, 'spk': spk, 'planned': True}, open(os.path.join(out, 'script.json'), 'w'), indent=1); print('planned', dur)
def shop_pitch():
    """after `build own`: pitch the shopkeeper's finished lines up (duration kept, sentence timings stay valid)"""
    import soundfile as sf, emph
    out = os.path.join(multi.TTS_DIR, 'ms')
    for k, s, _ in D:
        if s != 'S': continue
        f = os.path.join(out, k + '.wav'); y, sr = sf.read(f)
        z = emph.shape(y, SHOP_ST, 1.0, 0.0); z = z / max(1e-9, abs(z).max()) * 0.95; sf.write(f, z, sr); print('shop pitch', k, SHOP_ST)
def tighten(max_gap=0.45, keep=0.4):
    """the clone leaves long silences inside some lines (01: 1.1 s between 'One coin.' and 'To cross.'): cut every inner pause
    longer than max_gap down to `keep` seconds and move the sentence timings in script.json with it"""
    import numpy as np, soundfile as sf
    out = os.path.join(multi.TTS_DIR, 'ms'); jf = os.path.join(out, 'script.json'); J = json.load(open(jf))
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
        multi.main(D, VOICES, 'ms', TR)
        if len(sys.argv) > 2 and sys.argv[2] == 'own': shop_pitch(); tighten()
