"""Voice for "Why does the save point keeper count your deaths?" (sp, 26 Nov 2026). Brief: briefs/SAVE_POINT_FULL_BRIEF.txt.
Enes (26 Nov): generate the voices on the PC, cloned from ALL his earlier recordings. Chatterbox only listens to the first
~10 s of a reference, so each speaker gets its own reference, cut from the takes where Enes played that kind of role:
  N narrator  <- his narrator takes (bw, dt, fpo, le, bhb)
  B keeper    <- his tired old final boss (bw B) + the guardian (bhb G)
  K hero      <- his knight takes (bw K, dt K, bhb K)
Steps:
  python tools/tts/sp.py refs                       # tts/sp_refs/<spk>_<en|tr>.wav (system Python)
  <chatterbox python> tools/tts/clone_lines.py sp en   # -> $TTS_DIR/sp_own/<key>_all.wav   (TR: TTS_DIR=../renders/save_point/tr_voice_tts, arg tr)
  python tools/tts/sp.py build own                  # trims + levels + sentence timings -> $TTS_DIR/sp/script.json
  python tools/tts/sp.py plan                       # planned timings only (no audio)"""
import os, sys, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import multi
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VOICES = {'K': ('am_adam', 'en-us'), 'B': ('bm_george', 'en-gb')}
D = [('01', 'B', [("Again?", 1.0, 0, 0, 0)]),
     ('02', 'N', [("Every time he died, he woke up at this fire.", 1.0, 0, 0, 0)]),
     ('03', 'N', [("And every time, the old keeper carved one notch into his ladle.", 1.0, 0, 0, 0)]),
     ('04', 'K', [("How many is that?", 1.0, 0, 0, 0)]),
     ('05', 'B', [("Ninety-nine.", 1.0, 0, 0, 0)]),
     ('06', 'K', [("Nobody dies ninety-nine times.", 1.0, 0, 0, 0)]),
     ('07', 'B', [("I did.", 1.0, 0, 0, 0), ("A thousand and twelve.", 1.0, 0, 0, 0.3)]),
     ('08', 'N', [("The other side was full.", 1.0, 0, 0, 0), ("Old notches.", 1.0, 0, 0, 0.3), ("Faded.", 1.0, 0, 0, 0.3)]),
     ('09', 'B', [("Then one day, I stopped getting up.", 1.0, 0, 0, 0)]),
     ('10', 'K', [("Then don't count mine yet.", 1.0, 0, 0, 0)]),
     ('11', 'B', [("Soup's still warm when you're back.", 1.0, 0, 0, 0)]),
     ('12', 'N', [("The keeper raised his knife.", 1.0, 0, 0, 0)]),
     ('13', 'B', [("Get up, kid.", 1.0, 0, 0, 0)])]
# Turkish voice text (natural case for the TTS) and subtitles (upper case); same sentence count per line as D
TR = {'01': ['Yine mi?'], '02': ['Her öldüğünde bu ateşin başında uyanıyordu.'],
      '03': ['Yaşlı bekçi de her seferinde kepçesine bir çentik atıyordu.'], '04': ['Kaç oldu?'], '05': ['Doksan dokuz.'],
      '06': ['Kimse doksan dokuz kere ölmez.'], '07': ['Ben öldüm.', 'Bin on iki kere.'],
      '08': ['Öbür yüzü doluydu.', 'Eski çentikler.', 'Solmuş.'], '09': ['Sonra bir gün kalkmayı bıraktım.'],
      '10': ['O zaman benimkileri daha sayma.'], '11': ['Döndüğünde çorban sıcak olacak.'], '12': ['Bekçi bıçağını kaldırdı.'],
      '13': ['Kalk hadi, evlat.']}
def tr_upper(s): return s.replace('i', 'İ').replace('ı', 'I').upper()
TR_SUB = {k: [tr_upper(x) for x in v] for k, v in TR.items()}
# delivery per line (exaggeration for Chatterbox): the keeper is tired and quiet, the hero breathless then determined
EXAG = {'01': 0.35, '05': 0.3, '07': 0.35, '09': 0.3, '11': 0.45, '13': 0.4, '04': 0.6, '06': 0.6, '10': 0.65}
PLAN = {'01': [0.8], '02': [2.6], '03': [3.4], '04': [1.1], '05': [0.9], '06': [1.8], '07': [0.7, 1.5], '08': [1.4, 0.9, 0.7],
        '09': [2.2], '10': [1.5], '11': [2.0], '12': [1.6], '13': [1.0]}
REF_SRC = {'N': [('bw', 'N'), ('dt', 'N'), ('fpo', 'N'), ('le', 'N'), ('bhb', 'N')],
           'B': [('bw', 'B'), ('bhb', 'G')],
           'K': [('bw', 'K'), ('dt', 'K'), ('bhb', 'K')]}
TR_DIRS = {'bw': 'boss_wanted', 'bhb': 'boss_health_bar', 'le': 'the_last_echo'}
def refs(target=11.0):
    import numpy as np, soundfile as sf
    from scipy.signal import resample_poly
    out = os.path.join(REPO, 'tts', 'sp_refs'); os.makedirs(out, exist_ok=True); SR = 24000
    for lang in ('en', 'tr'):
        for spk, srcs in REF_SRC.items():
            pools = []
            for proj, code in srcs:
                if lang == 'en': base = os.path.join(REPO, 'tts', proj)
                else:
                    if proj not in TR_DIRS: continue
                    base = os.path.join(REPO, '..', 'renders', TR_DIRS[proj], 'tr_voice_tts', proj)
                try: j = json.load(open(os.path.join(base, 'script.json'), encoding='utf-8'))
                except FileNotFoundError: continue
                takes = []
                for w in sorted(glob.glob(base + '_own/*_all.wav')):
                    k = os.path.basename(w)[:2]
                    if j.get('spk', {}).get(k) != code: continue
                    y, sr = sf.read(w); y = y if y.ndim == 1 else y.mean(1)
                    if sr != SR: y = resample_poly(y, SR, sr)
                    a = np.abs(y) > 0.02 * np.abs(y).max(); idx = np.where(a)[0]
                    if len(idx) == 0: continue
                    y = y[max(0, idx[0] - 1200):idx[-1] + 2400]; d = len(y) / SR
                    if 1.0 <= d <= 6.0: takes.append(y)
                pools.append(takes)
            seq = []; i = 0                                                # interleave the projects so the reference has variety
            while any(pools) and sum(len(x) for x in seq) / SR < target:
                p = pools[i % len(pools)]
                if p: seq.append(p.pop(0))
                i += 1
                if i > 200: break
            if not seq: print('no takes', spk, lang); continue
            gap = np.zeros(int(0.3 * SR)); y = np.concatenate([np.concatenate([s_ / (np.sqrt((s_[np.abs(s_) > 0.01] ** 2).mean()) + 1e-9) * 0.1, gap]) for s_ in seq])
            y = np.clip(y, -0.95, 0.95); f = os.path.join(out, f'{spk}_{lang}.wav'); sf.write(f, y, SR)
            print(f, round(len(y) / SR, 1), 's from', len(seq), 'takes')
def lines_json(lang):
    out = {}
    for k, s, ss in D:
        txt = ' '.join(TR[k]) if lang == 'tr' else ' '.join(x[0] for x in ss)
        out[k] = dict(text=txt, spk=s, exag=EXAG.get(k, 0.5))
    return out
def plan():
    out = os.path.join(multi.TTS_DIR, 'sp'); os.makedirs(out, exist_ok=True); dur = {}; txt = {}; sent = {}; spk = {}
    for k, s, ss in D:
        pos = 0.0; sent[k] = []
        for (tx, *_, pause), d in zip(ss, PLAN[k]): pos += pause; sent[k].append([round(pos, 3), round(pos + d, 3), tx]); pos += d
        dur[k] = round(pos, 2); txt[k] = ' '.join(x[0] for x in ss); spk[k] = s
    json.dump({'text': txt, 'dur': dur, 'sent': sent, 'spk': spk, 'planned': True}, open(os.path.join(out, 'script.json'), 'w'), indent=1); print('planned', dur)
if __name__ == '__main__':
    if sys.argv[1] == 'plan': plan()
    elif sys.argv[1] == 'refs': refs()
    else: multi.main(D, VOICES, 'sp')
