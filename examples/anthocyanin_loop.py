"""SAPKALI MOLEKUL: AYNI SU IKI RENK - 70 s loop Short (1080x1920, 2D pixel art, no Blender needed).
Usage:  python examples/anthocyanin_loop.py audio      # VO + SFX + music -> timeline.json, audio_final.wav
        python examples/anthocyanin_loop.py preview    # contact sheet of key frames (fast check)
        python examples/anthocyanin_loop.py video      # render + mux -> anthocyanin_loop_v1_en.mp4
        python examples/anthocyanin_loop.py qa         # frame0==frame2099, palette, safe area, loudness, size
Output dir: renders/anthocyanin (outside the repo)."""
import os, sys, json, math, subprocess, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
OUT = os.environ.get('ANTH_OUT', os.path.abspath(os.path.join(ROOT, '..', 'renders', 'anthocyanin')))
TTS_DIR = os.path.join(ROOT, 'tts')
os.makedirs(OUT, exist_ok=True)
SR = 48000; DUR = 70.0; FPS = 30; NF = 2100
W, H = 360, 640
BG = (0x1A, 0x14, 0x20); PUR = (0x6A, 0x3F, 0xA0); PNK = (0xE0, 0x45, 0x7B)
BLU = (0x2E, 0x7B, 0xC4); CRM = (0xF2, 0xE4, 0xC9); YEL = (0xF5, 0xC5, 0x42)
PALETTE = [BG, PUR, PNK, BLU, CRM, YEL]
BAY = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0

# ---------------------------------------------------------------- script (tts text, caption text)
SC = [0, 3, 10, 22, 35, 48, 58, 68, 70]   # scene starts (s)
NAR, LEM, MOL = 'nar', 'lem', 'mol'
SCRIPT = {
 's1': dict(win=(0.0, 3.4), maxf=2.0, speed=1.4, items=[
    ('A', NAR, 'I squeezed lemon into cabbage juice... PINK!', 'I squeezed lemon into cabbage juice… PINK!'),
    ('B', NAR, 'Added carbonate... BLUE!', 'Added carbonate… BLUE!'),
    ('C', NAR, 'Same water, two colors. How?!', 'Same water, two colors. How?!')]),
 's2': dict(win=(3.7, 9.9), maxf=1.5, speed=0.95, items=[
    ('a', NAR, 'Meet the culprit:', 'Meet the culprit:'),
    ('b', NAR, 'Anthocyanin!', 'Anthocyanin!'),
    ('c', NAR, 'The color boss of purple cabbage juice.', 'The color boss of purple cabbage juice.'),
    ('d', NAR, "And he's holding tiny H plus hats.", "And he’s holding tiny H+ hats.")]),
 's3': dict(win=(10.2, 21.9), maxf=1.5, speed=0.95, items=[
    ('a', NAR, 'Lemon arrives, and the mix turns acidic.', 'Lemon arrives, and the mix turns acidic.'),
    ('b', NAR, 'Anthocyanin grabs the hats:', 'Anthocyanin grabs the hats:'),
    ('l', LEM, "I've got the hat!", 'LEMON: “I’ve got the hat!”'),
    ('c', NAR, 'The color turns pink.', 'The color turns pink.')]),
 's4': dict(win=(22.2, 34.9), maxf=1.5, speed=0.95, items=[
    ('a', NAR, 'Then carbonate arrives, and the mix turns basic.', 'Then carbonate arrives, and the mix turns basic.'),
    ('b', NAR, 'Carbonate collects the hats.', 'Carbonate collects the hats.'),
    ('c', NAR, 'Anthocyanin is left hatless:', 'Anthocyanin is left hatless:'),
    ('l', MOL, "Where's my hat?!", 'ANTHOCYANIN: “Where’s my hat?!”'),
    ('d', NAR, 'The color turns blue.', 'The color turns blue.')]),
 's5': dict(win=(35.2, 47.9), maxf=1.5, speed=0.95, items=[
    ('a', NAR, "So here's the deal:", 'So here’s the deal:'),
    ('b', NAR, 'H plus hat on, it is pink. Hat off, it is blue.', 'H+ hat on: pink. Hat off: blue.'),
    ('c', NAR, 'The color change is just the molecule putting hats on and taking them off.', 'The color change is just the molecule putting hats on and taking them off.')]),
 's6': dict(win=(48.2, 57.9), maxf=1.5, speed=0.95, items=[
    ('a', NAR, 'So how do we get purple back?', 'So how do we get purple back?'),
    ('b', NAR, 'We pull the pH to the middle.', 'We pull the pH to the middle.'),
    ('c', NAR, 'The hats balance out, and purple returns.', 'The hats balance out, and purple returns.'),
    ('d', NAR, 'pH seven, the stage is yours!', 'pH 7, the stage is yours!')]),
 's7': dict(win=(58.2, 67.9), maxf=1.4, speed=1.0, end_align=True, items=[
    ('a', NAR, "And now... let's rewind.", 'And now… let’s rewind.'),
    ('b', NAR, 'I squeezed lemon into cabbage juice...', 'I squeezed lemon into cabbage juice…')]),
}
VOICE = {NAR: ('af_heart', 1.0), LEM: ('af_nova', 1.15), MOL: ('af_sky', 1.25)}   # voice, pitch factor (resample)
GAP = 0.14

# ---------------------------------------------------------------- audio helpers
def _sf():
    import soundfile as sf
    return sf

def trim(a, thr=0.012, pre=120, post=360):
    nz = np.where(np.abs(a) > thr)[0]
    return a[max(0, nz[0] - pre):nz[-1] + post] if len(nz) else a

def tempo(a, f, sr):
    if abs(f - 1) < 0.01: return a
    sf = _sf(); p = os.path.join(OUT, '_t_in.wav'); q = os.path.join(OUT, '_t_out.wav')
    sf.write(p, a, sr)
    chain = []; r = f
    while r > 2.0: chain.append('atempo=2.0'); r /= 2.0
    chain.append('atempo=%.4f' % r)
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', p, '-af', ','.join(chain), q], check=True)
    b, _ = sf.read(q); return b

def synth_vo():
    """returns dict id -> (audio at 24k float, voice kind)"""
    sf = _sf(); cache = os.path.join(OUT, 'vo'); os.makedirs(cache, exist_ok=True)
    k = None; res = {}
    for sk, sc in SCRIPT.items():
        for iid, kind, tts, cap in sc['items']:
            key = hashlib.md5((tts + kind + str(sc['speed'])).encode()).hexdigest()[:10]
            p = os.path.join(cache, f'{sk}_{iid}_{key}.wav')
            if not os.path.exists(p):
                if k is None:
                    from kokoro_onnx import Kokoro
                    k = Kokoro(f'{TTS_DIR}/kokoro-v1.0.int8.onnx', f'{TTS_DIR}/voices-v1.0.bin')
                spd = sc['speed'] * (1.1 if kind != NAR else 1.0)
                a, sr = k.create(tts, voice=VOICE[kind][0], speed=spd, lang='en-us')
                sf.write(p, a, sr)
            a, sr = sf.read(p); a = trim(a)
            pf = VOICE[kind][1]
            if pf != 1.0:
                from scipy.signal import resample_poly
                a = resample_poly(a, 100, int(round(100 * pf)))      # pitch (and speed) up
            if sr != SR:
                from scipy.signal import resample_poly
                a = resample_poly(a, SR, sr)
            res[(sk, iid)] = a / max(1e-6, np.max(np.abs(a)))
    return res

# ---------------------------------------------------------------- sfx synth
def _env(n, a=0.005, d=0.1):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    e *= np.exp(-np.arange(n) / SR / d); return e

def tone(f0, f1, dur, wave='sq', decay=0.12):
    n = int(dur * SR); t = np.arange(n) / SR
    f = np.linspace(f0, f1, n); ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sign(np.sin(ph)) * 0.6 if wave == 'sq' else np.sin(ph)
    return s * _env(n, 0.003, decay)

def noise(dur, lo=None, hi=None, sweep=None, decay=None):
    from scipy.signal import butter, sosfilt
    n = int(dur * SR); x = np.random.default_rng(int(dur * 1000)).standard_normal(n)
    if lo and hi:
        x = sosfilt(butter(2, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
    if sweep == 'up': x *= np.sin(np.linspace(0, np.pi, n)) ** 2 * np.linspace(0.3, 1, n)
    elif sweep == 'down': x *= np.sin(np.linspace(0, np.pi, n)) ** 2 * np.linspace(1, 0.3, n)
    if decay: x *= _env(n, 0.002, decay)
    return x

def arp(notes, step, wave='sq', decay=0.12):
    n = int(step * len(notes) * SR + 0.3 * SR); o = np.zeros(n)
    for i, f in enumerate(notes):
        s = tone(f, f, step * 1.4, wave, decay); a = int(i * step * SR); o[a:a + len(s)] += s[:n - a]
    return o

def mixn(*xs):
    n = max(len(x) for x in xs); o = np.zeros(n)
    for x in xs: o[:len(x)] += x
    return o

SFX = {
 'pop': lambda: tone(300, 900, 0.09, 'sin', 0.04),
 'whoosh': lambda: noise(0.45, 400, 5000, 'up'),
 'throw': lambda: noise(0.3, 600, 6000, 'up'),
 'catch': lambda: mixn(tone(500, 250, 0.1, 'sq', 0.05), noise(0.05, 800, 4000, None, 0.02) * 0.4),
 'tada': lambda: arp([523, 659, 784, 1047, 1047], 0.09),
 'collect': lambda: arp([440, 554, 659], 0.06),
 'kick': lambda: tone(140, 40, 0.18, 'sin', 0.09) * 1.2,
 'snare': lambda: mixn(noise(0.14, 1500, 9000, None, 0.05), tone(220, 180, 0.08, 'sin', 0.03) * 0.5),
 'win': lambda: arp([523, 659, 784, 659, 784, 1047, 1319], 0.085),
 'micdrop': lambda: np.concatenate([mixn(tone(90, 30, 0.35, 'sin', 0.12) * 1.3, noise(0.35, 100, 2000, None, 0.06)),
                                    np.zeros(int(0.06 * SR)), tone(2200, 2400, 0.5, 'sin', 0.3) * 0.25]),
 'rewind': lambda: rewind(2.0),
 'click': lambda: mixn(tone(1800, 600, 0.02, 'sq', 0.01), tone(90, 60, 0.08, 'sin', 0.03)),
 'fizz': lambda: noise(0.5, 3000, 9000, 'down') * 0.5,
}

def rewind(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    wow = 1 + 0.04 * np.sin(2 * np.pi * 9 * t)
    f = np.linspace(900, 2800, n) * wow
    s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.3
    x = s + noise(dur, 1000, 8000) * 0.5 * (0.6 + 0.4 * np.sin(2 * np.pi * 14 * t))
    return x * np.minimum(1, np.minimum(t / 0.05, (dur - t) / 0.2))

def music():
    """very light 8-bit arpeggio, seamless loop (35 bars of 2 s, 5-chord cycle), tails wrap around."""
    out = np.zeros(int(DUR * SR))
    chords = [(220, 261.6, 329.6), (174.6, 220, 261.6), (261.6, 329.6, 392), (196, 246.9, 293.7), (164.8, 207.7, 246.9)]
    step = 0.25
    for bar in range(35):
        ch = chords[bar % 5]
        for i in range(8):
            f = ch[[0, 1, 2, 1, 0, 1, 2, 1][i]] * (2 if i % 4 == 2 else 1)
            s = tone(f, f, 0.22, 'sq', 0.09) * 0.5
            a = int((bar * 2 + i * step) * SR)
            idx = (np.arange(len(s)) + a) % len(out); out[idx] += s
    return out / np.max(np.abs(out))

# ---------------------------------------------------------------- timeline (VO placement + anchors)
def build_timeline():
    vo = synth_vo(); T = {'seg': {}, 'cap': [], 'sfx': [], 'an': {}}
    mix = np.zeros(int(DUR * SR))
    for sk, sc in SCRIPT.items():
        ds = [len(vo[(sk, it[0])]) / SR for it in sc['items']]
        a0, a1 = sc['win']; avail = a1 - a0 - 0.1
        f = max(1.0, sum(ds) / (avail - GAP * (len(ds) - 1)))
        if sk == 's1' and f > sc['maxf']: f = sc['maxf']      # hook may overflow its 3 s a little
        f = min(f, sc['maxf'] + (0.4 if sk == 's1' else 0))
        durs = [d / f for d in ds]
        tot = sum(durs) + GAP * (len(ds) - 1)
        t = a1 - tot if sc.get('end_align') else a0 + (0.0 if sk == 's1' else 0.1)
        for it, d in zip(sc['items'], durs):
            iid, kind, tts, cap = it
            a = tempo(vo[(sk, iid)], f, SR)
            lvl = 0.5 if kind == NAR else 0.45        # -6 dB / -7 dB peak
            s0 = int(t * SR); mix[s0:s0 + len(a)] += a[:len(mix) - s0] * lvl
            T['seg'][sk + iid] = [round(t, 3), round(t + len(a) / SR, 3)]
            T['cap'].append([round(t, 3) if not (sk == 's1' and iid == 'A') else 0.0, round(t + len(a) / SR + 0.25, 3), cap])
            t += len(a) / SR + GAP
    seg = lambda k: T['seg'][k]
    clamp = lambda v, lo, hi: max(lo, min(hi, v))
    A = T['an']
    A['pT'] = round(clamp(seg('s1A')[1] - 0.15, 0.9, 1.8), 3)
    A['bT'] = round(clamp(seg('s1B')[1] - 0.15, A['pT'] + 0.75, 2.8), 3)
    A['s2land'] = 3.9; A['s2hat'] = [round(seg('s2d')[0] + 0.5 + 0.6 * i, 3) for i in range(3)]
    A['s3acid'] = round(seg('s3a')[0] + 0.7, 3)
    A['s3throw'] = [round(seg('s3b')[0] + 0.1 + 0.55 * i, 3) for i in range(3)]
    A['s4carb'] = 22.5
    A['s4acid'] = round(seg('s4a')[0] + 1.3, 3)
    A['s4steal'] = [round(seg('s4b')[0] + 0.1 + 0.6 * i, 3) for i in range(3)]
    A['s5start'] = seg('s5b')[0]
    A['s6mix'] = seg('s6b')[0]
    A['mic'] = round(min(seg('s6d')[1] + 0.15, 57.1), 3)
    A['rew'] = round(seg('s7a')[0], 3)
    # sfx events (time, name)
    S = T['sfx']; add = lambda t, n: S.append([round(t, 3), n])
    add(0.0, 'pop'); add(A['pT'] - 0.45, 'whoosh'); add(A['pT'], 'pop'); add(A['bT'] - 0.45, 'throw'); add(A['bT'], 'pop'); add(A['bT'] + 0.1, 'fizz')
    add(3.0, 'whoosh'); add(A['s2land'], 'pop'); add(seg('s2b')[0], 'tada')
    for t in A['s2hat']: add(t, 'pop')
    add(10.0, 'whoosh'); add(A['s3acid'], 'pop')
    for t in A['s3throw']: add(t, 'throw'); add(t + 0.55, 'catch')
    add(seg('s3l')[0] - 0.3, 'pop')
    add(22.0, 'whoosh'); add(A['s4acid'], 'fizz')
    for t in A['s4steal']: add(t, 'throw'); add(t + 0.55, 'collect')
    add(35.0, 'whoosh')
    b = 0.0
    while 35.4 + b < 47.8:
        add(35.4 + b, 'kick')
        if int(b / 0.5) % 2 == 1: add(35.4 + b, 'snare')
        b += 0.5
    add(48.0, 'whoosh'); add(A['s6mix'] + 0.4, 'pop'); add(seg('s6d')[0], 'win'); add(A['mic'], 'micdrop')
    add(58.0, 'whoosh'); add(A['rew'], 'rewind'); add(66.0, 'rewind')
    add(69.85, 'click')
    # sfx -> mix at -18 dB peak (relative to VO -6 dB)
    sx = np.zeros(len(mix))
    for t, n in S:
        s = SFX[n](); s = s / max(1e-6, np.max(np.abs(s))) * 10 ** (-18 / 20) * (1.0 if n != 'rewind' else 1.0)
        a = int(t * SR); sx[a:a + len(s)] += s[:max(0, len(sx) - a)]
    mu = music() * 10 ** (-24 / 20)
    tot = mix + sx + mu
    tot = np.clip(tot, -1, 1)
    sf = _sf(); raw = os.path.join(OUT, 'audio_raw.wav'); sf.write(raw, np.stack([tot, tot], 1), SR)
    fin = os.path.join(OUT, 'audio_final.wav')
    r = subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-y', '-i', raw, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
    js = json.loads(r.stderr[r.stderr.rfind('{'):r.stderr.rfind('}') + 1])
    af = ('loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true'
          % (js['input_i'], js['input_tp'], js['input_lra'], js['input_thresh'], js['target_offset']))
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', raw, '-af', af, '-ar', '48000', '-ac', '2', fin], check=True)
    json.dump(T, open(os.path.join(OUT, 'timeline.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('timeline ok; hook VO ends %.2f s, last VO ends %.2f s' % (seg('s1C')[1], seg('s7b')[1]))
    return T

# ---------------------------------------------------------------- drawing
FONTS = {}
def font(name, size):
    k = (name, size)
    if k not in FONTS:
        p = os.path.join(OUT, 'PressStart2P-Regular.ttf' if name == 'ps' else 'VT323-Regular.ttf')
        FONTS[k] = ImageFont.truetype(p, size)
    return FONTS[k]

def text(d, xy, s, f, fill, anchor='la', shadow=True):
    d.fontmode = '1'
    if shadow: d.text((xy[0] + 2, xy[1] + 2), s, font=f, fill=BG, anchor=anchor)
    d.text(xy, s, font=f, fill=fill, anchor=anchor)

def wrap(s, f, maxw):
    lines = []; cur = ''
    for w in s.split(' '):
        t = (cur + ' ' + w).strip()
        if f.getlength(t) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

def dshade(im, box, only, amt=0.55, mode='diag'):
    x0, y0, x1, y1 = [int(v) for v in box]; x0 = max(0, x0); y0 = max(0, y0); x1 = min(W, x1); y1 = min(H, y1)
    if x1 <= x0 or y1 <= y0: return
    a = np.asarray(im.crop((x0, y0, x1, y1))).copy()
    m = np.all(a == only, axis=2)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    u = (xx - x0) / max(1, x1 - x0 - 1); v = (yy - y0) / max(1, y1 - y0 - 1)
    g = (u * 0.6 + v * 0.4) if mode == 'diag' else v
    dark = m & (BAY[yy % 4, xx % 4] < g * amt)
    a[dark] = BG
    im.paste(Image.fromarray(a), (x0, y0))

def hat(d, x, yb, tilt=0):
    d.rectangle((x - 15, yb - 3, x + 15, yb), fill=CRM)
    d.rectangle((x - 10, yb - 16, x + 10, yb - 3), fill=YEL)
    d.rectangle((x - 10, yb - 16, x + 10, yb - 15), fill=CRM)
    text(d, (x, yb - 9), 'H+', font('ps', 8), BG, 'mm', shadow=False)

def eyes(d, cx, cy, sp, r, look=(0, 0), panic=False, sad=False):
    for sx in (-1, 1):
        ex = cx + sx * sp
        d.ellipse((ex - r, cy - r, ex + r, cy + r), fill=CRM)
        pr = 2 if panic else max(2, r // 2)
        px = ex + look[0] + (sx * 1 if panic else 0); py = cy + look[1]
        d.ellipse((px - pr, py - pr, px + pr, py + pr), fill=BG)

def mol(im, d, cx, cy, r, col, mood='happy', hats=0, look=(0, 0), arms='down', hatoff=0):
    ax = {'down': 10, 'up': -20, 'out': -2}[arms]
    for sx in (-1, 1):
        x0 = cx + sx * (r - 2); x1 = cx + sx * (r + 12); y0 = cy + 6; y1 = cy + 6 + ax
        d.line((x0, y0, x1, y1), fill=col, width=5); d.ellipse((x1 - 4, y1 - 4, x1 + 4, y1 + 4), fill=CRM)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
    dshade(im, (cx - r, cy - r, cx + r, cy + r), col, 0.8)
    d = ImageDraw.Draw(im)
    eyes(d, cx, cy - r // 4, r // 3, max(6, r // 5), look, mood == 'panic')
    my = cy + r // 3
    if mood == 'happy': d.arc((cx - 9, my - 8, cx + 9, my + 6), 20, 160, fill=BG, width=3)
    elif mood == 'panic': d.ellipse((cx - 5, my - 2, cx + 5, my + 9), fill=BG)
    elif mood == 'sad': d.arc((cx - 9, my, cx + 9, my + 14), 200, 340, fill=BG, width=3)
    else: d.line((cx - 7, my + 2, cx + 7, my + 2), fill=BG, width=3)
    if mood == 'sad':
        d.line((cx - r // 3 - 8, cy - r // 4 - 12, cx - r // 3 + 6, cy - r // 4 - 8), fill=BG, width=3)
        d.line((cx + r // 3 + 8, cy - r // 4 - 12, cx + r // 3 - 6, cy - r // 4 - 8), fill=BG, width=3)
    for k in range(hats):
        hat(d, cx + (2 if k % 2 else -2) + hatoff, cy - r + 4 - k * 13)
    return d

def lemon(im, d, cx, cy, r, mood='smug', arms=0):
    d.line((cx - r + 2, cy + 8, cx - r - 12, cy + 8 + arms), fill=YEL, width=4)
    d.line((cx + r - 2, cy + 8, cx + r + 12, cy + 8 - arms), fill=YEL, width=4)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=CRM)
    d.ellipse((cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4), fill=YEL)
    for k in range(8):
        a = k * math.pi / 4
        d.line((cx, cy, cx + (r - 5) * math.cos(a), cy + (r - 5) * math.sin(a)), fill=CRM, width=1)
    d.rectangle((cx - 22, cy - 9, cx - 3, cy + 3), fill=BG, outline=CRM)
    d.rectangle((cx + 3, cy - 9, cx + 22, cy + 3), fill=BG, outline=CRM)
    d.line((cx - 3, cy - 5, cx + 3, cy - 5), fill=CRM, width=2)
    d.line((cx - 18, cy - 6, cx - 12, cy - 6), fill=CRM)
    d.line((cx - 8, cy + 12, cx + 6, cy + 12), fill=BG, width=3); d.line((cx + 6, cy + 12, cx + 10, cy + 8), fill=BG, width=3)

def carb(im, d, cx, cy, w, h, hats=0, laugh=0):
    x0, y0, x1, y1 = cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2
    d.line((x0, cy + 4, x0 - 12, cy + 18 - laugh), fill=CRM, width=5); d.line((x1, cy + 4, x1 + 12, cy + 18 - laugh), fill=CRM, width=5)
    d.rectangle((x0, y0, x1, y1), fill=CRM, outline=BG, width=2)
    d.rectangle((x0 + 2, y1 - 16, x1 - 2, y1 - 2), fill=BG)
    text(d, (cx, y1 - 9), 'Na2CO3', font('ps', 8), CRM, 'mm', shadow=False)
    for sx in (-1, 1):
        ex = cx + sx * 12
        d.ellipse((ex - 4, cy - 8, ex + 4, cy), fill=BG)
        d.line((ex - sx * 10, cy - 17 - 4, ex + sx * 4, cy - 12), fill=BG, width=4)
    d.arc((cx - 8, cy + 2, cx + 8, cy + 12), 200, 340, fill=BG, width=3)
    for k in range(hats):
        hat(d, cx + (3 if k % 2 else -3), y0 + 3 - k * 13)

def beaker(im, d, cx, cy, w, h, col, level=0.6, bubbles=0, t=0.0, label=None):
    x0, y0, x1, y1 = cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2
    ly = int(y1 - (y1 - y0) * level)
    d.rectangle((x0, ly, x1, y1), fill=col)
    dshade(im, (x0, ly, x1, y1), col, 0.9)
    d = ImageDraw.Draw(im)
    wob = int(round(math.sin(t * 6) * 1))
    d.line((x0 + 3, ly + wob, x1 - 3, ly + wob), fill=CRM, width=1)
    for i in range(bubbles):
        bx = x0 + 10 + (i * 37 + 13) % max(10, w - 20); by = y1 - 8 - int(((t * 30 + i * 17) % (y1 - ly - 10)))
        if by > ly + 3: d.rectangle((bx, by, bx + 2, by + 2), fill=CRM)
    d.line((x0, y0 - 6, x0, y1), fill=CRM, width=3); d.line((x1, y0 - 6, x1, y1), fill=CRM, width=3)
    d.line((x0, y1, x1, y1), fill=CRM, width=3); d.line((x0 - 6, y0 - 6, x0 + 4, y0 - 6), fill=CRM, width=3); d.line((x1 - 4, y0 - 6, x1 + 6, y0 - 6), fill=CRM, width=3)
    if label:
        d.rectangle((cx - 30, ly + 14, cx + 30, ly + 38), fill=BG)
        text(d, (cx, ly + 26), label, font('ps', 16), YEL, 'mm', shadow=False)
    return d

def bubble(d, cx, cy, s, tail='down', fill=CRM, ink=BG):
    f = font('vt', 28); tw = f.getlength(s) + 16
    d.rectangle((cx - tw / 2, cy - 18, cx + tw / 2, cy + 14), fill=fill)
    if tail == 'down': d.polygon([(cx - 8, cy + 14), (cx + 8, cy + 14), (cx, cy + 26)], fill=fill)
    d.fontmode = '1'; d.text((cx, cy - 2), s, font=f, fill=ink, anchor='mm')

def drop(d, x, y, c=YEL):
    d.polygon([(x, y - 12), (x - 6, y), (x + 6, y)], fill=c); d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=c)

def hatfly(d, p0, p1, u, h=60):
    u = max(0.0, min(1.0, u)); x = p0[0] + (p1[0] - p0[0]) * u; y = p0[1] + (p1[1] - p0[1]) * u - 4 * h * u * (1 - u)
    hat(d, int(x), int(y))

def icon(d, kind, x, y):
    if kind in ('shock', 'dizzy'):
        d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=YEL)
        if kind == 'shock':
            d.ellipse((x - 6, y - 5, x - 2, y - 1), fill=BG); d.ellipse((x + 2, y - 5, x + 6, y - 1), fill=BG)
            d.ellipse((x - 3, y + 2, x + 3, y + 8), fill=BG)
        else:
            for sx in (-4, 4):
                d.line((x + sx - 3, y - 6, x + sx + 3, y), fill=BG); d.line((x + sx - 3, y, x + sx + 3, y - 6), fill=BG)
            d.line((x - 5, y + 5, x - 2, y + 3), fill=BG, width=2); d.line((x - 2, y + 3, x + 2, y + 6), fill=BG, width=2); d.line((x + 2, y + 6, x + 5, y + 4), fill=BG, width=2)
    elif kind == 'hat':
        hat(d, x, y + 8)
    elif kind == 'rew':
        d.polygon([(x - 12, y), (x, y - 8), (x, y + 8)], fill=YEL); d.polygon([(x, y), (x + 12, y - 8), (x + 12, y + 8)], fill=YEL)

def title(d, l1, l2=None, c1=CRM, c2=YEL, ic=None, ic_line=2):
    f = font('ps', 16)
    text(d, (180, 52), l1, f, c1, 'ma')
    if l2:
        text(d, (180, 82), l2, f, c2, 'ma')
    if ic:
        s = l2 if (l2 and ic_line == 2) else l1
        y = 90 if (l2 and ic_line == 2) else 60
        icon(d, ic, int(180 + f.getlength(s) / 2 + 20), y)

def frame_ui(d, t):
    for (x, y, sx, sy) in ((10, 44, 1, 1), (350, 44, -1, 1), (10, 528, 1, -1), (350, 528, -1, -1)):
        d.line((x, y, x + 18 * sx, y), fill=CRM, width=2); d.line((x, y, x, y + 18 * sy), fill=CRM, width=2)
        d.rectangle((min(x + 4 * sx, x + 6 * sx), min(y + 4 * sy, y + 6 * sy), max(x + 4 * sx, x + 6 * sx), max(y + 4 * sy, y + 6 * sy)), fill=YEL)

def bgdots(im):
    a = np.asarray(im).copy()
    ys, xs = np.mgrid[0:H-6:12, 0:W-6:12]
    a[ys + 6, xs + 6] = PUR
    return Image.fromarray(a)

def seg_of(T, k): return T['seg'][k]

# ---------------------------------------------------------------- scenes
def drawhead(im, d, T, g, lt, hold):
    pass

def sc1(im, d, T, g, lt):
    A = T['an']; pT = A['pT']; bT = A['bT']
    col = PUR if lt < pT else (PNK if lt < bT else BLU)
    bob = 0 if lt < 0.05 else int(round(math.sin(lt * 14) * 1.5))
    # shaker box (karbonat) + lemon half at top
    lemon(im, d, 120, 175 + bob, 26, arms=0)
    carb(im, d, 262, 175, 52, 44)
    beaker(im, d, 180, 335, 130, 150, col, 0.6, bubbles=(6 if lt >= bT else 0), t=lt)
    d = ImageDraw.Draw(im)
    if lt < pT - 0.45: drop(d, 150, 205)
    elif lt < pT:
        u = (lt - (pT - 0.45)) / 0.45; drop(d, 150 + int(30 * u), int(205 + (290 - 205) * u * u))
    if bT - 0.45 <= lt < bT:
        u = (lt - (bT - 0.45)) / 0.45
        for i in range(7):
            d.rectangle((248 - i * 9 + int(8 * u), int(200 + (290 - 200) * u * u + i * 5 - 10), 251 - i * 9 + int(8 * u), int(203 + (290 - 200) * u * u + i * 5 - 10)), fill=CRM)
    for tt in (pT, bT):
        if 0 <= lt - tt < 0.3:
            for k in range(8):
                a = k * math.pi / 4; r = 14 + (lt - tt) * 70
                d.rectangle((180 + r * math.cos(a) * 1.4 - 2, 273 + r * math.sin(a) * 0.5 - 2 - 8, 180 + r * math.cos(a) * 1.4 + 1, 273 + r * math.sin(a) * 0.5 + 1 - 8), fill=CRM)
    f = font('ps', 16)
    text(d, (22, 52), 'LEMON:', f, CRM); text(d, (22 + f.getlength('LEMON: '), 52), 'PINK', f, PNK); icon(d, 'shock', 292, 60)
    text(d, (22, 82), 'CARBONATE:', f, CRM); text(d, (22 + f.getlength('CARBONATE: '), 82), 'BLUE', f, BLU); icon(d, 'dizzy', 292, 90)

def sc2(im, d, T, g, lt):
    A = T['an']; seg = T['seg']
    title(d, 'CULPRIT FOUND:', 'ANTHOCYANIN')
    u = lt / 0.9
    base = 330
    if lt < 0.9: cy = base + int(260 * (1 - u) ** 2) * 1 - int(0)
    else:
        ph = (lt - 0.9) / 0.6
        amp = [38, 18, 8, 0][min(3, int(ph))]
        cy = base - int(amp * abs(math.sin(math.pi * (ph % 1))))
    nh = sum(1 for t in A['s2hat'] if g >= t)
    look = ((lt * 6) % 4 - 2, 0) if lt > 1.8 else (0, 0)
    pos = [(105, 255), (255, 255), (180, 190)]
    for i in range(nh):
        px, py = pos[i]; py += int(round(math.sin((lt + i) * 5) * 2))
        hat(d, px, py)
    mol(im, d, 180, cy, 46, PUR, 'happy', 0, look, 'up' if nh else 'down')
    d = ImageDraw.Draw(im)
    if g >= seg['s2c'][0] and g < seg['s2d'][1] + 1.5:
        d.rectangle((24, 418, 336, 446), fill=CRM)
        text(d, (180, 432), 'COLOR BOSS', font('vt', 28), BG, 'mm', shadow=False)
    if 0 <= g - seg['s2b'][0] < 0.5:
        for k in range(6):
            a = k * math.pi / 3 + 0.3; r = 62 + (g - seg['s2b'][0]) * 60
            d.rectangle((180 + r * math.cos(a) - 2, 330 + r * math.sin(a) - 2, 180 + r * math.cos(a) + 2, 330 + r * math.sin(a) + 2), fill=YEL)

def sc3(im, d, T, g, lt):
    A = T['an']; seg = T['seg']
    title(d, 'LEMON THROWS HATS', '=> PINK', CRM, PNK)
    th = A['s3throw']; fl = 0.55
    lemx = 420 - min(1, max(0, (lt - 0.4) / 0.9)) * 150
    landed = sum(1 for t in th if g >= t + fl)
    col = PNK if landed >= 2 else PUR
    bcol = PNK if g >= A['s3acid'] else PUR
    mpos = (125, 320)
    beaker(im, d, 285, 395, 70, 80, bcol, 0.6, bubbles=3 if bcol == PNK else 0, t=lt)
    d = ImageDraw.Draw(im)
    arms = 'up' if landed < 3 else 'out'
    mood = 'happy' if landed >= 1 else 'panic'
    mol(im, d, mpos[0], mpos[1], 44, col, mood, landed, ((lt * 5) % 4 - 2, 0), arms)
    d = ImageDraw.Draw(im)
    if lemx < 400: lemon(im, d, int(lemx), 240, 30, arms=int(8 * ((lt * 4) % 2)))
    d = ImageDraw.Draw(im)
    for i, t in enumerate(th):
        if t <= g < t + fl:
            tgt = (mpos[0], mpos[1] - 44 + 4 - 13 * i - 14)
            hatfly(d, (int(lemx) - 10, 222), tgt, (g - t) / fl, 55)
    if A['s3acid'] - 0.25 <= g < A['s3acid']:
        drop(d, 285, int(250 + (g - (A['s3acid'] - 0.25)) * 600))
    if seg['s3l'][0] <= g < seg['s3l'][1] + 0.6: bubble(d, 255, 185, 'I GOT THE HAT!')

def sc4(im, d, T, g, lt):
    A = T['an']; seg = T['seg']
    title(d, 'CARBONATE STEALS', 'HATS => BLUE', CRM, BLU)
    st = A['s4steal']; fl = 0.55
    taken = sum(1 for t in st if g >= t + fl)
    leaving = sum(1 for t in st if g >= t)
    mx, my = 215, 320
    cx = -60 + min(1, max(0, (lt - 0.3) / 1.0)) * 145
    col = PNK if taken < 2 else (PUR if taken < 3 else BLU)
    if g >= seg['s4l'][0] - 0.3: col = BLU
    bcol = BLU if g >= A['s4acid'] else PNK
    beaker(im, d, 305, 400, 62, 74, bcol, 0.6, bubbles=3, t=lt)
    d = ImageDraw.Draw(im)
    nh = 3 - leaving
    panic = g >= seg['s4c'][0]
    mol(im, d, mx, my, 44, col, 'panic' if panic else 'happy', max(0, nh), ((lt * 7) % 6 - 3, 0), 'up' if panic else 'down')
    d = ImageDraw.Draw(im)
    carb(im, d, int(cx), 345, 66, 60, hats=taken, laugh=int(6 * ((lt * 5) % 2)))
    d = ImageDraw.Draw(im)
    for i, t in enumerate(st):
        if t <= g < t + fl:
            hatfly(d, (mx, my - 44 - 10 - 13 * (2 - i)), (int(cx), 345 - 30 - 13 * i - 6), (g - t) / fl, 70)
    if seg['s4l'][0] <= g < seg['s4l'][1] + 0.6: bubble(d, 215, 205, 'WHERE IS MY HAT?!')

def ph_at(g, A, T):
    t0 = A['s5start']
    if g < t0: return 7.0
    s = g - t0
    if s < 1.0: return 7 - 5 * s
    if s < 2.5: return 2.0
    if s < 4.0: return 2 + 10 * (s - 2.5) / 1.5
    if s < 5.0: return 12.0
    k = s - 5.0
    return 7 + 5 * math.cos(2 * math.pi * k / 2.4)

def col_ph(p): return PNK if p < 5 else (PUR if p < 9 else BLU)

def sc5(im, d, T, g, lt):
    A = T['an']
    title(d, 'COLOR = HAT', 'GAME', CRM, YEL, ic='hat')
    p = ph_at(g, A, T); col = col_ph(p)
    hats = 2 if p < 5 else (1 if p < 9 else 0)
    bt = int(lt * 2)
    dx = [-10, 10][bt % 2] if g >= A['s5start'] else 0
    dy = -int(10 * abs(math.sin(lt * 6.28 * 1.0))) if g >= A['s5start'] else 0
    mol(im, d, 180 + dx, 260 + dy, 46, col, 'happy' if hats else 'sad' if p > 9 else 'happy', hats, (dx / 4, 0), 'up' if bt % 2 else 'out')
    d = ImageDraw.Draw(im)
    x0, x1, by = 30, 330, 390
    for i in range(15):
        c = col_ph(i); xa = x0 + i * 20; xb = xa + 20
        d.rectangle((xa, by, xb - 1, by + 22), fill=c)
        if i in (4, 5, 8, 9):   # dithered blends at the borders
            o = PNK if i < 7 else PUR; o2 = PUR if i < 7 else BLU
            for yy in range(by, by + 23):
                for xx in range(xa, xb):
                    if BAY[yy % 4, xx % 4] < (0.5 if i in (4, 8) else 0.5) and ((i in (4, 8) and xx >= xa + 10) or (i in (5, 9) and xx < xa + 10)):
                        d.point((xx, yy), fill=o if i in (4, 5) else o2)
        d.line((xa, by + 22, xa, by + 28), fill=CRM)
    d.line((x1 + 0, by + 22, x1, by + 28), fill=CRM)
    for n in (0, 7, 14):
        text(d, (x0 + n * 20 + (0 if n < 14 else 0), by + 44), str(n), font('vt', 28), CRM, 'mm')
    text(d, (x0 - 4, by - 14), 'ACID', font('vt', 24), PNK, 'lm'); text(d, (x1 + 4, by - 14), 'BASE', font('vt', 24), BLU, 'rm')
    mx = x0 + p * 20
    d.polygon([(mx, by - 2), (mx - 8, by - 14), (mx + 8, by - 14)], fill=YEL)

def sc6(im, d, T, g, lt):
    A = T['an']; seg = T['seg']
    title(d, 'pH 7 = PURPLE', 'IS BACK', CRM, PUR)
    mixed = g >= A['s6mix'] + 0.4
    col = PUR if mixed else PNK
    beaker(im, d, 235, 335, 130, 160, col, 0.65, bubbles=4, t=lt, label='pH 7' if g >= seg['s6d'][0] - 0.3 else None)
    d = ImageDraw.Draw(im)
    mol(im, d, 100, 340, 38, col if mixed else PNK, 'happy', 1 if mixed else 2, ((lt * 5) % 4 - 2, 0), 'up' if mixed else 'down')
    d = ImageDraw.Draw(im)
    if g >= A['mic'] - 1.0:
        u = g - (A['mic'] - 1.0); y0 = 150; fl = 1.0
        if u < fl: y = y0 + (410 - y0) * (u / fl) ** 2
        else:
            b = (u - fl); y = 410 - int(26 * abs(math.sin(b * 9)) * math.exp(-b * 4))
        y = int(y)
        d.ellipse((294, y - 28, 314, y - 8), fill=CRM); d.rectangle((300, y - 8, 308, y + 14), fill=YEL)
        d.rectangle((298, y + 14, 310, y + 18), fill=CRM)
    if g >= A['mic'] and g < A['mic'] + 0.8:
        text(d, (230, 245), '*PAT*', font('ps', 8), YEL, 'mm', shadow=False) if False else None

def cassette(im, d, T, g, lt, spin=1.0):
    x0, y0, x1, y1 = 60, 200, 300, 330
    d.rectangle((x0, y0, x1, y1), fill=CRM, outline=BG, width=3)
    d.rectangle((x0 + 20, y0 + 14, x1 - 20, y0 + 62), fill=BG)
    for cx in (x0 + 70, x1 - 70):
        d.ellipse((cx - 22, y0 + 18, cx + 22, y0 + 58), fill=PUR)
        a0 = (lt * spin * 8) % (2 * math.pi)
        for k in range(3):
            a = a0 + k * 2 * math.pi / 3
            d.line((cx, y0 + 38, cx + 18 * math.cos(a), y0 + 38 + 18 * math.sin(a)), fill=CRM, width=3)
        d.ellipse((cx - 5, y0 + 33, cx + 5, y0 + 43), fill=BG)
    d.rectangle((x0 + 50, y1 - 36, x1 - 50, y1 - 8), fill=YEL)
    text(d, (180, y1 - 22), 'pH 7 MIX', font('ps', 8), BG, 'mm', shadow=False)

def sc7(im, d, T, g, lt):
    A = T['an']; rew = A['rew']
    if g < rew:
        title(d, 'SHALL WE', 'REWIND?', CRM, YEL, ic='rew')
        cassette(im, d, T, g, lt, 0.3)
        d = ImageDraw.Draw(im)
        mol(im, d, 180, 400, 28, PUR, 'happy', 1, ((lt * 5) % 4 - 2, 0), 'down')
    elif g < 67.5:
        u = (g - rew) / (67.5 - rew)
        if u < 0.4: s, l = sc4, 13.0 * (1 - u / 0.4)
        elif u < 0.8: s, l = sc3, 11.5 * (1 - (u - 0.4) / 0.4)
        else: s, l = sc1, 3.0 * (1 - (u - 0.8) / 0.2)
        gl = (22.0 if s is sc4 else 10.0 if s is sc3 else 0.0) + l
        l = math.floor(l * 12) / 12
        s(im, d, T, gl, l)
        d = ImageDraw.Draw(im)
        icon(d, 'rew', 318, 112)
    else:
        sc1(im, d, T, 0.0, 0.0)

SCENES = [sc1, sc2, sc3, sc4, sc5, sc6, sc7]

# ---------------------------------------------------------------- silence cuts (seconds in the 70 s master)
CUTS = [(17.0, 22.0), (31.0, 35.0), (44.1, 48.0), (59.0, 64.1)]   # all after the last VO word of a scene, before the next scene's flash
def kept_frames():
    gone = set()
    for a, b in CUTS: gone.update(range(int(round(a * FPS)), int(round(b * FPS))))
    return [f for f in range(NF) if f not in gone]

def cut_audio():
    sf = _sf(); a, sr = sf.read(os.path.join(OUT, 'audio_raw.wav')); keep = kept_frames()
    runs = []; st = keep[0]; pv = keep[0]
    for f in keep[1:]:
        if f != pv + 1: runs.append((st, pv + 1)); st = f
        pv = f
    runs.append((st, pv + 1))
    xf = int(0.02 * SR); out = None
    for r0, r1 in runs:
        seg = a[int(r0 / FPS * SR):int(r1 / FPS * SR)].copy()
        if out is None: out = seg
        else:
            fade = np.linspace(0, 1, xf)[:, None]
            out[-xf:] *= (1 - fade)
            seg[:xf] *= fade
            out = np.concatenate([out, seg])
    raw = os.path.join(OUT, 'audio_cut_raw.wav'); sf.write(raw, out, SR)
    r = subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-y', '-i', raw, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
    js = json.loads(r.stderr[r.stderr.rfind('{'):r.stderr.rfind('}') + 1])
    af = ('loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true'
          % (js['input_i'], js['input_tp'], js['input_lra'], js['input_thresh'], js['target_offset']))
    fin = os.path.join(OUT, 'audio_final_cut.wav')
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', raw, '-af', af, '-ar', '48000', '-ac', '2', fin], check=True)
    print('cut audio %.2f s' % (len(out) / SR)); return fin

# ---------------------------------------------------------------- compositor
SHAKE = [(-4, 0), (4, 2), (-3, -2), (3, 1), (-2, 0), (1, 0)]
FLASH_AT = [3.0, 10.0, 22.0, 35.0, 48.0, 58.0]

def cap_at(T, g):
    for a, b, s in T['cap']:
        if a <= g < b: return s
    return None

def shake_frames(T):
    ev = {}
    pts = FLASH_AT + [T['an']['pT'], T['an']['bT'], T['an']['mic']]
    for t in pts:
        f0 = int(round(t * FPS))
        for i in range(6): ev.setdefault(f0 + i, SHAKE[i])
    return ev

def render(T, f, shk=None):
    """returns native 360x640 PIL image (pre-effects)"""
    if f >= 68 * FPS: sc, g, lt = 0, 0.0, 0.0              # scene 8: exact copy of frame 0
    else:
        g = f / FPS
        sc = max(i for i, s in enumerate(SC[:7]) if g >= s - 1e-9)
        lt = math.floor((f - SC[sc] * FPS) * 12 / FPS) / 12.0
        g = SC[sc] + lt
    im = Image.new('RGB', (W, H), BG); im = bgdots(im); d = ImageDraw.Draw(im)
    SCENES[sc](im, d, T, g, lt)
    d = ImageDraw.Draw(im)
    frame_ui(d, g)
    cp = cap_at(T, g if f < 68 * FPS else 0.0)
    if cp:
        fnt = font('vt', 30); lines = wrap(cp, fnt, 330)
        y = 465
        for ln in lines[:3]:
            text(d, (180, y), ln, fnt, CRM, 'ma'); y += 28
    if shk and f in shk:
        dx, dy = shk[f]; n = Image.new('RGB', (W, H), BG); n.paste(im, (dx, dy)); im = n
    return im

def fx_masks():
    Hh, Ww = H * 3, W * 3
    yy, xx = np.mgrid[0:Hh, 0:Ww]
    bay = BAY[yy % 4, xx % 4]
    scan = ((yy % 3) == 2) & (bay < 0.25)                       # 3 px pitch, ~8 % overall darkening
    cy, cx = Hh / 2, Ww / 2
    r = np.sqrt(((yy - cy) / cy) ** 2 + ((xx - cx) / cx) ** 2) / 1.414
    vig = bay < np.clip((r - 0.55) * 1.4, 0, 0.6)
    return scan | vig

def finish(im, f, mask, T):
    a = np.asarray(im)
    g = f / FPS
    if T['an']['rew'] <= g < 67.5 or (66.0 <= g < 68.0 and f < 68 * FPS):
        a = a.copy(); rng = np.random.default_rng(f)
        for _ in range(5):
            y = int(rng.integers(40, 540)); h = int(rng.integers(3, 14)); o = int(rng.integers(-12, 13))
            a[y:y + h] = np.roll(a[y:y + h], o, axis=1)
        y = int(rng.integers(40, 540)); a[y:y + 2] = np.where(rng.random((2, W, 1)) < 0.5, np.array(CRM), np.array(BG)).astype(np.uint8)
    up = np.repeat(np.repeat(a, 3, axis=0), 3, axis=1)
    up = np.where(mask[:, :, None], np.array(BG, dtype=np.uint8), up)
    return up

def render_video(T, only=None, out=None, cut=False):
    out = out or os.path.join(OUT, 'anthocyanin_loop_v1_en_short.mp4' if cut else 'anthocyanin_loop_v1_en.mp4')
    frames = kept_frames() if cut else list(range(NF))
    afile = cut_audio() if cut else os.path.join(OUT, 'audio_final.wav')
    shk = shake_frames(T); mask = fx_masks(); flash = {int(round(t * FPS)) for t in FLASH_AT + [T['an']['pT'], T['an']['bT']]}
    cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', '30', '-i', '-',
           '-i', afile, '-map', '0:v', '-map', '1:a',
           '-c:v', 'libx264', '-preset', 'slow', '-qp', '18', '-pix_fmt', 'yuv420p', '-x264-params', 'keyint=60:min-keyint=1:scenecut=0:aq-mode=0:mbtree=0',
           '-force_key_frames', 'expr:eq(n,0)+eq(n,%d)' % (len(frames) - 1), '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2',
           '-frames:v', str(len(frames)), out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    hs = {}
    for i, f in enumerate(frames):
        im = render(T, f, shk)
        up = finish(im, f, mask, T)
        if f in flash: up = np.full_like(up, CRM)
        if f in (0, NF - 1): hs[f] = hashlib.md5(up.tobytes()).hexdigest()
        p.stdin.write(up.tobytes())
        if i % 300 == 0: print('frame', i, flush=True)
    p.stdin.close(); p.wait()
    print('raw frame0 == frame2099:', hs[0] == hs[NF - 1], hs)

# ---------------------------------------------------------------- qa / preview
def preview(T):
    shk = shake_frames(T); mask = fx_masks()
    fr = [0, 12, 40, 70, 150, 240, 330, 420, 520, 700, 840, 1000, 1200, 1400, 1650, 1900, 1960, 2050, 2099]
    fr = [int(x) for x in os.environ.get('FRAMES', ','.join(map(str, fr))).split(',')]
    ims = [Image.fromarray(finish(render(T, f, shk), f, mask, T)).resize((270, 480), Image.NEAREST) for f in fr]
    cols = 7; rows = (len(ims) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * 274, rows * 484), (60, 60, 60))
    for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * 274, (i // cols) * 484))
    p = os.path.join(OUT, 'preview.png'); sheet.save(p); print(p, fr)

def qa(T):
    mask = fx_masks(); shk = shake_frames(T); pal = set(PALETTE); bad = 0; worst = 0
    for f in range(0, NF, 37):
        a = finish(render(T, f, shk), f, mask, T)
        u = np.unique(a.reshape(-1, 3), axis=0)
        n = sum(1 for c in u if tuple(c) not in pal); worst = max(worst, n); bad += n > 0
    a0 = finish(render(T, 0, shk), 0, mask, T); a1 = finish(render(T, NF - 1, shk), NF - 1, mask, T)
    print('raw frame0 == frame2099:', np.array_equal(a0, a1))
    print('off-palette colours in sampled frames: worst', worst, 'frames affected', bad)
    mp = os.path.join(OUT, 'anthocyanin_loop_v1_en.mp4')
    if os.path.exists(mp):
        print('size MB', round(os.path.getsize(mp) / 1e6, 1))
        for t, n in (('0', 0), ('69.9667', 2099)):
            subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', mp, '-vf', 'select=eq(n\,%d)' % n, '-fps_mode', 'passthrough', '-frames:v', '1', os.path.join(OUT, f'dec_{t}.png')])
        x = np.asarray(Image.open(os.path.join(OUT, 'dec_0.png')).convert('RGB')).astype(int); y = np.asarray(Image.open(os.path.join(OUT, 'dec_69.9667.png')).convert('RGB')).astype(int)
        print('decoded mp4 frame0 vs last: max abs diff', int(np.abs(x - y).max()), 'differing px', int((np.abs(x - y).sum(2) > 0).sum()))
        r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_name,width,height,r_frame_rate,nb_frames,duration', '-of', 'compact', mp], capture_output=True, text=True); print(r.stdout)
        r = subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-i', mp, '-af', 'loudnorm=I=-14:print_format=summary', '-f', 'null', '-'], capture_output=True, text=True)
        print([l for l in r.stderr.splitlines() if 'Input Integrated' in l or 'Input True Peak' in l])
    print('last VO ends', T['seg']['s7b'][1], '(must be <= 68.0)')

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if mode in ('audio', 'all'): T = build_timeline()
    T = json.load(open(os.path.join(OUT, 'timeline.json'), encoding='utf-8'))
    if mode == 'preview': preview(T)
    if mode in ('video', 'all'): render_video(T)
    if mode == 'cut': render_video(T, cut=True)
    if mode in ('qa', 'all'): qa(T)
