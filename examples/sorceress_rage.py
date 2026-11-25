"""THE FIRST TO EVER RAGEBAIT - visual adaptation of a source reel (Insert Disc 2, 25 Nov 2026). 57.57 s, 30 fps, 9:16, nightkit HD + face rig.
Brief: pasted GPT brief (visual adaptation; original audio unchanged). Source: voice/snapgram.io_fv3w5zze9dpz.mp4 (copy + analysis in
voice/sorceress_src/: mesh.json = MediaPipe FaceMesh per source frame, words.json = Whisper word times, src48k.wav = the untouched audio).
The source has TWO voices. v2 (Enes, 25 Nov evening): the SORCERESS is the angry voice (0-5.95, 28.62-33.85, 42.6-55.45 s: mouth from the
audio: loudness + vowel colour), the KNIGHT is the calm ragebaiter (on-screen speaker 5.95-28.62, 33.85-42.6, 55.45-57.35 s: mouth + head
from the tracked face). They face each other (a real exchange), simple readable faces: smug troll vs. annoyed -> furious.
Gags on her measured beats: helmet trembles on her first rise (4.97 s), pops on 'Alright' (33.43 s) -> he talks on with a crooked helmet,
fire at her strongest word ('UP', 43.57 s) inside the real 0.37 s pause 44.03-44.40 s while he ducks; he straightens the helmet at the end.

Frames:  TEST=0,13.3,... python examples/sorceress_rage.py -> test_sr.png
Render:  python tools/render_parts.py examples/sorceress_rage.py --prefix sr --audio sorceress_rage.wav --out <scratch> --parts 8, then mux
         out/sr_video.mp4 + voice/sorceress_src/src48k.wav + out/sr_sfx.wav with amix normalize=0 (never loudnorm: the audio stays untouched)"""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera
from nightkit.zraster import zrender
from nightkit import post, look, hd, motion, font, facerig
import dragon_taxes as dtx                      # locked: the series knight (HD body, open helmet, blue cape + plume), torch flames

W, H, S = 270, 480, 4
PI = math.pi
V = np.array
FPS = 30
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SRC = os.path.join(ROOT, 'voice', 'sorceress_src')
hsh, lerp, lerp3, mixc = dtx.hsh, dtx.lerp, dtx.lerp3, dtx.mixc
sm = motion.smooth
def seg01(t, a, b): return max(0.0, min(1.0, (t - a) / (b - a))) if b > a else (1.0 if t >= b else 0.0)
def win(t, a, b, r=0.15): return sm(seg01(t, a - r, a)) * (1 - sm(seg01(t, b, b + r)))
def nz(v): v = V(v, float); n = np.linalg.norm(v); return v / n if n > 1e-9 else v

# ======================= source analysis -> performance tracks =======================
MESH = json.load(open(os.path.join(SRC, 'mesh.json')))
DUR = round(MESH['N'] / MESH['fps'], 4); N = int(round(DUR * FPS))
KN_TALK = [(5.95, 28.62), (33.85, 42.6), (55.45, 57.35)]       # on-screen speaker -> the KNIGHT (tracked mouth)
SO_TALK = [(0.0, 5.95), (28.62, 33.85), (42.6, 55.45)]         # off-screen voice -> the SORCERESS (audio-driven mouth)
T_TREMBLE = 4.97; T_POP = 33.43; T_LAND = 34.02; T_FIX = (34.15, 34.75); T_FIRE = (44.03, 44.4); T_FIX2 = (53.4, 54.15)
def in_w(t, ws, pad=0.0): return any(a - pad <= t < b + pad for a, b in ws)
def _tracks():
    from scipy.ndimage import median_filter, uniform_filter1d
    import soundfile as sf
    from scipy.signal import butter, sosfiltfilt
    R = MESH['rows']; n = len(R); fps = MESH['fps']
    def ser(k):
        v = np.array([r[k] if r else np.nan for r in R], float); i = np.arange(n); m = ~np.isnan(v); return np.interp(i, i[m], v[m])
    T = np.arange(n) / fps
    op = median_filter(ser('open'), 3); iw = ser('inner_w')
    roll = uniform_filter1d(ser('roll'), 7); pitch = uniform_filter1d(ser('pitch'), 9)
    kt = uniform_filter1d(np.array([in_w(t, KN_TALK) for t in T], float), 5)
    C = {}
    # knight: the tracked mouth of the on-screen speaker
    C['kopen'] = np.clip((op - 0.014) / 0.19, 0, 1.15) * kt; C['kjaw'] = C['kopen'] * 0.95
    iwm = np.median(iw[kt > 0.5]); C['kwide'] = np.clip((iw - iwm) / 0.06, 0, 1) * kt * 0.7
    C['kround'] = np.clip((iwm - iw) / 0.05, 0, 1) * np.clip(C['kopen'] * 2.5, 0, 1) * kt
    rm = np.median(roll); pm = np.median(pitch)
    C['ktilt'] = -np.radians(roll - rm) * 0.4 * kt; C['knod'] = -(pitch - pm) * 1.4 * kt
    # sorceress: the off-screen voice -> loudness (attack 1 frame, release ~3 frames) + vowel colour (spectral centroid) + sibilants
    a, sr = sf.read(os.path.join(SRC, 'src48k.wav')); a = a.mean(1) if a.ndim > 1 else a
    sos = butter(4, [200, 3000], btype='band', fs=sr, output='sos'); e = np.abs(sosfiltfilt(sos, a)); hop = sr / fps
    env = np.array([e[int(k * hop):int((k + 1) * hop)].mean() for k in range(n)]); edb = 20 * np.log10(env + 1e-6)
    st = np.array([in_w(t, SO_TALK) for t in T], float)
    lv = np.clip((edb + 42.0) / 24.0, 0, 1) * st
    out = np.zeros(n); x = 0.0
    for i, v in enumerate(lv): x = x + (v - x) * (0.8 if v > x else 0.42); out[i] = x
    cen = np.zeros(n); sib = np.zeros(n); fr = np.fft.rfftfreq(int(hop * 2), 1 / sr)
    for k in range(n):
        seg = a[int(k * hop):int(k * hop) + int(hop * 2)]
        if len(seg) < int(hop * 2): break
        sp = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
        band = (fr > 300) & (fr < 3500); cen[k] = (sp[band] * fr[band]).sum() / (sp[band].sum() + 1e-9)
        sib[k] = sp[(fr > 4500) & (fr < 9000)].sum() / (sp[(fr > 200) & (fr < 9000)].sum() + 1e-9)
    cs = st > 0.5; c0, c1 = np.percentile(cen[cs], 15), np.percentile(cen[cs], 85)
    C['sopen'] = out * 1.1; C['sjaw'] = out
    cw = np.clip((uniform_filter1d(cen, 3) - c0) / (c1 - c0 + 1e-9), 0, 1)
    C['swide'] = out * cw * 0.9; C['sround'] = out * (1 - cw) * 0.7
    C['steeth'] = np.clip((sib - np.percentile(sib[cs], 70)) / (np.percentile(sib[cs], 97) - np.percentile(sib[cs], 70) + 1e-9), 0, 1) * st * (1 - np.clip(out * 2, 0, 1))
    C['slv'] = lv; C['edb'] = edb; C['T'] = T
    return C
TR_ = _tracks()
def tr(k, t): return float(np.interp(t, TR_['T'], TR_[k]))

# ======================= cast (both get the face rig) =======================
SOR = hd.spec(h=1.7, build=0.9, fem=1.0, skin=(230, 188, 158), hair=(118, 46, 30), hair_style='long', eye=(84, 120, 70), brow=(96, 40, 26),
              lip=(190, 96, 96), tunic=(46, 108, 66), tunic2=(36, 88, 54), skirt=0.95, sleeves='long', pants=(36, 88, 54), boots=(60, 40, 30),
              belt=(196, 162, 70), buckle=(236, 200, 90), collar=(204, 170, 76), cloak=(30, 72, 46), cloak_len=1.0)
GOLD = (226, 190, 84)
STYLE = {'sor': dict(skin=SOR['skin'], eye=SOR['eye'], brow=SOR['brow'], lip=(186, 92, 96), mouth_in=(70, 20, 30), teeth=(240, 234, 222),
                     tongue=(186, 84, 92), stubble=False, scar=False),
         'kn': dict(skin=dtx.KNIGHT['skin'], eye=dtx.KNIGHT['eye'], brow=(56, 40, 30), lip=(176, 112, 100), mouth_in=(60, 20, 24), teeth=(236, 230, 214),
                    tongue=(178, 78, 86), stubble=True, scar=False)}
_orig_head = hd.head
def rig_head(hc, RH, S_, P, k):
    """both characters get the high-density face rig; the sorceress adds long auburn hair + a gold circlet, the knight short hair"""
    if 'E' not in P: return _orig_head(hc, RH, S_, P, k)
    who = P['_who']; facerig.set_style(**STYLE[who])
    E = P['E']; M = facerig.Mesh(hc, RH)
    facerig.head_mesh(M, E); facerig.eyes_geo(M, E); facerig.brows_geo(M, E); facerig.nose_geo(M, E); facerig.mouth_geo(M, E)
    rx, ry, rz = facerig.RX, facerig.RY, facerig.RZ
    Q = M.Q + hd.hair(hc, RH, S_, P, 1.0, (rx, ry, rz), lambda p: facerig.base_def(V(p, float)[None])[0])
    if who == 'sor':
        def L(x, y, z): return hc + RH @ V((x, y, z))
        Q += hd.limb(L(0, 0.058, -0.004), L(0, 0.07, -0.008), rz * 1.08, rz * 1.06, GOLD, n=16, m=1, ref=RH @ V((0, 0, 1.0)), flat=0.92)   # circlet
        Q += hd.bx(L(0, 0.066, rz * 1.06), RH, (0.009, 0.009, 0.004), (60, 200, 120), emit=True)                                       # green gem
    return Q
hd.head = rig_head
KSPEC = dict(dtx.KNIGHT); KSPEC['helmet'] = None
def knight_body(P):
    """the series knight without his helmet (dtx.knight minus knight_helmet): the helmet is animated separately"""
    Q = hd.human(KSPEC, P); RW = P['_RW']; ch = P['_chest']; st = (178, 186, 200); dk = (128, 136, 152)
    for sd in (1, -1):
        c = ch + RW @ V((sd * 0.19, 0.075, -0.01))
        Q += hd.ellip(c, RW @ hd.Rz(-sd * 0.35), (0.1, 0.07, 0.1), 10, 5, st, v1=PI * 0.6, colfn=lambda i, j, cl: dk if i == 2 else st)
    Q += hd.ellip(ch + RW @ V((0, -0.02, 0.035)), RW, (0.17, 0.17, 0.1), 12, 6, st, keep=lambda c: c[2] > 0.0, colfn=lambda i, j, cl: dk if (j % 6 == 0) else st)
    return Q

# ======================= set: one castle corridor (stone blocks, two torches, one banner) =======================
WALLZ = -1.9
def build_set():
    Q = []; bw, bh = 0.46, 0.25
    Q.append(hd.face([(-3, -0.1, WALLZ - 0.02), (3, -0.1, WALLZ - 0.02), (3, 3.4, WALLZ - 0.02), (-3, 3.4, WALLZ - 0.02)], (40, 34, 40)))
    for r in range(14):
        y0 = r * bh; off = (r % 2) * bw / 2
        for c in range(-7, 7):
            x0 = c * bw + off; g = 0.82 + 0.26 * hsh(r * 31 + c, 41)
            col = hd.shade(mixc((110, 98, 92), (122, 108, 96), hsh(r * 7 + c, 43)), g)
            Q.append(hd.face([(x0 + 0.012, y0 + 0.012, WALLZ), (x0 + bw - 0.012, y0 + 0.012, WALLZ), (x0 + bw - 0.012, y0 + bh - 0.012, WALLZ), (x0 + 0.012, y0 + bh - 0.012, WALLZ)], col))
    for sx in (-1, 1):                                    # side walls receding towards the camera (the corridor)
        x = sx * 1.75
        for r in range(14):
            y0 = r * bh
            for c in range(6):
                z0 = WALLZ + c * 0.5; g = 0.7 + 0.2 * hsh(r * 13 + c + sx, 5)
                col = hd.shade((104, 94, 90), g)
                Q.append(hd.face([(x, y0 + 0.01, z0 + 0.01), (x, y0 + 0.01, z0 + 0.49), (x, y0 + bh - 0.01, z0 + 0.49), (x, y0 + bh - 0.01, z0 + 0.01)], col))
    for c in range(-4, 4):                                # flagstone floor
        for r in range(6):
            x0 = c * 0.5; z0 = WALLZ + r * 0.5; col = hd.shade((82, 74, 70), 0.85 + 0.25 * hsh(c * 5 + r, 9))
            Q.append(hd.face([(x0 + 0.01, 0, z0 + 0.01), (x0 + 0.49, 0, z0 + 0.01), (x0 + 0.49, 0, z0 + 0.49), (x0 + 0.01, 0, z0 + 0.49)], col))
    # one banner (deep red with a gold crest)
    bx0, bx1, by0, by1, bz = -0.36, -0.12, 1.92, 2.4, WALLZ + 0.03
    Q += hd.limb(V((bx0 - 0.06, by1 + 0.03, bz + 0.02)), V((bx1 + 0.06, by1 + 0.03, bz + 0.02)), 0.018, 0.018, (90, 62, 40), n=6, m=1)
    pts = [(bx0, by1), (bx1, by1), (bx1, by0 + 0.15), ((bx0 + bx1) / 2, by0), (bx0, by0 + 0.15)]
    Q.append(hd.face([(x, y, bz) for x, y in pts], (132, 26, 34)))
    cx, cy = (bx0 + bx1) / 2, 2.2
    Q.append(hd.face([(cx, cy + 0.09, bz + 0.004), (cx + 0.07, cy + 0.02, bz + 0.004), (cx, cy - 0.09, bz + 0.004), (cx - 0.07, cy + 0.02, bz + 0.004)], GOLD))
    return [q for q in Q if q]
SET = build_set()
TORCH = [V((-0.5, 1.8, WALLZ + 0.12)), V((0.55, 1.8, WALLZ + 0.12))]
def torches(t, boost=0.0):
    Q = []
    for i, p in enumerate(TORCH):
        Q += hd.bx(p + V((0, -0.2, -0.08)), np.eye(3), (0.03, 0.06, 0.04), (60, 56, 60))
        Q += dtx.torch_faces(p, t, k=1.0 + boost, seed=i * 3)
    return Q

# ======================= poses + faces (a two-shot: they face each other) =======================
KN0 = (0.25, 0.0, -0.2); SOR0 = (-0.21, 0.0, 0.05); KYAW0 = -0.42; SYAW0 = 0.4
def E0():
    return dict(open=0.0, jaw=0.0, wide=0.0, round=0.0, teeth=0.0, press=0.0, eyesR=1.0, eyesL=1.0, browR=0.0, browL=0.0, innerR=0.0, innerL=0.0,
                furrow=0.0, squintR=0.0, squintL=0.0, smR=0.0, smL=0.0, cheekR=0.0, cheekL=0.0, look=(0.0, 0.0))
def mix_into(E, P, u):
    for k, v in P.items():
        if k == 'look': E['look'] = (lerp(E['look'][0], v[0], u), lerp(E['look'][1], v[1], u))
        else: E[k] = lerp(E[k], v, u)
def blink(E, t, times, d=0.07):
    for b in times:
        bk = max(0.0, 1 - abs(t - b) / d); E['eyesR'] *= 1 - bk; E['eyesL'] *= 1 - bk
ANNOYED = dict(furrow=0.45, browR=-0.4, browL=-0.4, innerR=-0.35, innerL=-0.35, squintR=0.2, squintL=0.2, press=0.5)
FUMING = dict(furrow=0.9, browR=-0.85, browL=-0.85, innerR=-0.7, innerL=-0.7, squintR=0.55, squintL=0.55, press=1.0, eyesR=0.95, eyesL=0.95)
RAGE = dict(furrow=1.0, browR=-1.0, browL=-1.0, innerR=-0.85, innerL=-0.85, squintR=0.15, squintL=0.15, eyesR=1.12, eyesL=1.12, press=0.0)
EXASP = dict(furrow=0.35, browR=0.1, browL=0.1, innerR=0.45, innerL=0.45, squintR=0.1, squintL=0.1, eyesR=0.8, eyesL=0.8)
def sor_expr(t):
    """the sorceress: annoyed -> fuming while he trolls -> rage (fire) -> a cold glare at his last line"""
    E = E0(); mix_into(E, ANNOYED, 1.0)
    talk = in_w(t, SO_TALK)
    if talk:
        E['open'] = tr('sopen', t); E['jaw'] = tr('sjaw', t); E['wide'] = tr('swide', t); E['round'] = tr('sround', t); E['teeth'] = tr('steeth', t); E['press'] = 0.0
    if 5.95 <= t < 28.62:                                       # listening to his 'mad mad / name name': it gets to her
        mix_into(E, FUMING, 0.25 + 0.6 * seg01(t, 6.5, 27.0))
        r = win(t, 21.9, 22.7, 0.15); E['look'] = (0.0, 0.95 * r); E['eyesR'] *= 1 - 0.3 * r; E['eyesL'] *= 1 - 0.3 * r     # eye-roll ('no butter')
    if 28.62 <= t < 33.85: mix_into(E, EXASP, 0.85 * win(t, 28.7, 33.2, 0.3))         # 'Alright...' exasperated
    if 33.85 <= t < 42.6:
        mix_into(E, FUMING, 1.0)
        g = win(t, 34.6, 35.6, 0.12); E['eyesR'] += 0.2 * g; E['eyesL'] += 0.2 * g; E['browR'] -= 0.15 * g; E['browL'] -= 0.15 * g   # the glare that freezes him
    if 42.6 <= t < 55.45:
        mix_into(E, RAGE, sm(seg01(t, 42.55, 42.75)))
        lv = tr('slv', t); E['eyesR'] += 0.12 * lv; E['eyesL'] += 0.12 * lv; E['cheekR'] = 0.3 * lv; E['cheekL'] = 0.3 * lv
        if t >= 50.0: mix_into(E, dict(squintR=0.35, squintL=0.35), 0.6)
    if t >= 55.45: mix_into(E, FUMING, 1.0); mix_into(E, dict(squintR=0.7, squintL=0.7, eyesR=0.75, eyesL=0.75), 0.6)   # cold glare
    f = win(t, T_FIRE[0], T_FIRE[1], 0.07)                    # breathes fire
    if f > 0: mix_into(E, dict(open=1.15, jaw=1.15, wide=0.7, round=0.0, teeth=0.0, furrow=1.0, browR=-1.0, browL=-1.0, eyesR=0.8, eyesL=0.8), f)
    blink(E, t, (2.75, 9.2, 14.6, 19.1, 25.3, 30.3, 37.4, 40.8, 49.6, 56.3))
    return E
SMUG = dict(browR=0.75, browL=-0.1, innerR=0.2, innerL=0.0, squintR=0.3, squintL=0.18, eyesR=0.88, eyesL=0.9, smR=0.7, smL=0.3, press=0.3, cheekR=0.3)
def kn_expr(t):
    """the knight: a smug troll (one brow up, crooked grin) - surprised at the pop, alarmed at her rant, scared under the fire, smug again"""
    E = E0(); mix_into(E, SMUG, 1.0)
    talk = in_w(t, KN_TALK)
    if talk:
        E['open'] = tr('kopen', t); E['jaw'] = tr('kjaw', t); E['wide'] = tr('kwide', t); E['round'] = tr('kround', t); E['press'] = 0.0
        E['smR'] = 0.55; E['smL'] = 0.2
        E['browR'] += 0.25 * min(1.0, tr('kopen', t) * 2)                                  # brow bounces on his stressed syllables
    if t < 5.95: mix_into(E, dict(smR=0.35, smL=0.1, browR=0.4), 1.0)                       # waits for his turn, a little smirk
    e = win(t, T_TREMBLE - 0.05, T_TREMBLE + 0.55, 0.1); E['look'] = (0.0, 0.7 * e); E['browR'] += 0.3 * e; E['browL'] += 0.4 * e
    sp = win(t, T_POP - 0.03, 33.83, 0.08)                                                    # the pop: eyes up, brows up, 'o'
    if sp > 0: mix_into(E, dict(eyesR=1.3, eyesL=1.3, browR=1.0, browL=1.0, innerR=0.4, innerL=0.4, smR=0.0, smL=0.0, open=0.45, jaw=0.45, round=0.9, look=(0.0, 1.0), squintR=0.0, squintL=0.0), sp)
    fr = win(t, 34.6, 35.0, 0.08)                                                             # freezes under her glare
    if fr > 0: mix_into(E, dict(eyesR=1.25, eyesL=1.25, browR=0.9, browL=0.8, smR=0.1, smL=0.0, squintR=0.0, squintL=0.0), fr)
    al = sm(seg01(t, 42.65, 43.1)) * (1 - sm(seg01(t, 45.6, 46.8)))                          # her rant: the grin drops
    if al > 0: mix_into(E, dict(eyesR=1.2, eyesL=1.2, browR=0.9, browL=0.9, innerR=0.5, innerL=0.5, smR=0.0, smL=0.0, squintR=0.0, squintL=0.0), al)
    dk = win(t, T_FIRE[0] - 0.08, T_FIRE[1] + 0.25, 0.08)                                     # under the fire: eyes shut tight, teeth gritted
    if dk > 0: mix_into(E, dict(eyesR=0.0, eyesL=0.0, squintR=1.0, squintL=1.0, furrow=0.8, browR=-0.6, browL=-0.6, wide=0.8, teeth=1.0, open=0.15, smR=0.0, smL=0.0), dk)
    if not talk and t >= 46.8: mix_into(E, dict(smR=0.85, smL=0.45, cheekR=0.5, cheekL=0.3), sm(seg01(t, 46.8, 47.6)))   # enjoys her rage
    blink(E, t, (1.4, 8.3, 12.7, 17.9, 23.4, 27.6, 31.1, 39.2, 48.9, 52.6))
    return E
def sor_pose(t):
    talk = in_w(t, SO_TALK); lv = tr('slv', t) if talk else 0.0
    br = 0.012 * math.sin(t * 2 * PI / 3.6)
    nod = -0.06 * lv + 0.03 * math.sin(t * 1.1)
    rant = sm(seg01(t, 42.55, 42.9)) * (1 - sm(seg01(t, 55.3, 55.9)))
    hy = 0.32 + 0.05 * math.sin(t * 0.7)
    if 21.9 <= t < 22.8: hy -= 0.1 * win(t, 22.0, 22.7, 0.2)
    P = dict(base=SOR0, yaw=SYAW0, lean=0.02 + 0.08 * rant + br * 0.5, head=(hy, nod - 0.04 * rant, 0.05 * math.sin(t * 0.9)), pel=(0, br, 0), cape_sway=0.05 * math.sin(t * 0.9))
    P['rh'] = (0.2, 0.92, 0.2); P['lh'] = (-0.2, 0.9, 0.18); P['rgrip'] = 0.35; P['lgrip'] = 0.4
    pt = win(t, 42.75, 43.85, 0.15) + win(t, 45.9, 47.3, 0.2) + 0.8 * win(t, 49.8, 50.9, 0.2)           # points at him while she yells
    if pt > 0: P['rh'] = lerp3(P['rh'], (0.12, 1.36, 0.52), min(1.0, pt)); P['rgrip'] = 0.75
    cr = 0.9 * win(t, 5.9, 28.4, 0.5) + 0.9 * win(t, 34.0, 42.4, 0.5)                                 # hands on her hips while he trolls
    if cr > 0:
        P['lh'] = lerp3(P['lh'], (-0.21, 1.0, 0.0), cr); P['rh'] = lerp3(P['rh'], (0.21, 1.0, 0.0), cr * (1 - min(1.0, pt)))
        P['lpole'] = (-1.0, -0.2, -0.3); P['rpole'] = (1.0, -0.2, -0.3)
    P['E'] = sor_expr(t); P['_who'] = 'sor'
    return P
def knight_pose(t):
    talk = in_w(t, KN_TALK)
    tilt = tr('ktilt', t) if talk else 0.06; nod = tr('knod', t) if talk else 0.0
    P = dict(base=KN0, yaw=KYAW0, lean=0.03, head=(-0.32, nod, tilt), cape_sway=0.1 * math.sin(t * 1.2))
    P['rh'] = (0.25, 0.9, 0.05); P['lh'] = (-0.25, 0.9, 0.05); P['rgrip'] = 0.5; P['lgrip'] = 0.5
    if talk: P['rh'] = lerp3(P['rh'], (0.22, 1.1, 0.3), 0.6 * win(t, 9.5, 12.5, 0.4) + 0.6 * win(t, 36.0, 38.5, 0.4))   # a lazy hand while trolling
    if T_POP - 0.05 <= t < T_LAND + 0.3: P['head'] = (-0.2, 0.22 * win(t, T_POP, T_LAND, 0.12), 0.0)                       # watches the helmet
    for (a, b) in (T_FIX, T_FIX2):                                                                                          # hands to the helmet
        fx = win(t, a, b, 0.22)
        if fx > 0:
            P['rh'] = lerp3(P['rh'], (0.2, 1.68, 0.06), fx); P['lh'] = lerp3(P['lh'], (-0.2, 1.68, 0.06), fx); P['rgrip'] = 0.3; P['lgrip'] = 0.3
            P['rpalm'] = (-1.0, 0.0, 0.0); P['lpalm'] = (1.0, 0.0, 0.0)
    rec = win(t, 42.65, 44.0, 0.2)                                                                                          # leans away from her rant
    P['lean'] -= 0.06 * rec
    dk = sm(seg01(t, T_FIRE[0] - 0.1, T_FIRE[0] + 0.1)) * (1 - sm(seg01(t, T_FIRE[1] + 0.3, T_FIRE[1] + 0.85)))
    if dk > 0:
        P['crouch'] = 0.32 * dk; P['lean'] = 0.03 + 0.32 * dk; P['head'] = (-0.3, 0.2 * dk, 0.0)
        P['rh'] = lerp3(P['rh'], (0.22, 1.3, 0.3), dk); P['lh'] = lerp3(P['lh'], (-0.24, 1.32, 0.28), dk)
        P['rf'] = (0.14, 0.07, 0.12); P['lf'] = (-0.14, 0.07, -0.08)
    P['E'] = kn_expr(t); P['_who'] = 'kn'
    return P

# ======================= the helmet gag =======================
def helmet_state(t, KP):
    """trembles at T_TREMBLE, pops at T_POP (arc + spin, stays in frame), lands crooked (T_LAND), half-fixed at T_FIX then he freezes,
    fully straightened at T_FIX2"""
    hc = V(KP['_head'], float); RH = KP['_RH']; up = RH @ V((0, 1.0, 0))
    tr_ = win(t, T_TREMBLE - 0.05, T_TREMBLE + 0.6, 0.08) + 0.6 * win(t, T_POP - 0.35, T_POP - 0.02, 0.05)
    if tr_ > 0 and t < T_POP:
        j = tr_ * 0.012 * math.sin(t * 95); return hc + up * (abs(j) * 0.6), RH @ hd.Rz(j * 2.2)
    if t < T_POP: return hc, RH
    u = t - T_POP; fl = T_LAND - T_POP
    if u < fl:
        s = u / fl; h = 0.22 * 4 * s * (1 - s)
        return hc + up * (h + 0.01) + (RH @ V((0.05, 0, 0.03))) * s, RH @ hd.Rx(-2 * PI * s) @ hd.Rz(0.6 * s)
    crook = 0.38; off = RH @ V((0.03, 0.012, 0.0))
    b = max(0.0, 1 - (u - fl) / 0.18); off = off + up * 0.025 * b * abs(math.sin((u - fl) * 40))
    k1 = 0.5 * sm(seg01(t, T_FIX[0] + 0.12, T_FIX[1] - 0.05)); k2 = sm(seg01(t, T_FIX2[0] + 0.15, T_FIX2[1] - 0.12))
    keep = (1 - k1) * (1 - k2)
    return hc + off * keep, RH @ hd.Rz(-crook * keep)
def helmet_geo(t, KP):
    pos, R = helmet_state(t, KP)
    Q = dtx.knight_helmet(dict(_head=pos, _RH=R, cape_sway=KP.get('cape_sway', 0.0)))
    g = win(t, T_POP + 0.12, T_POP + 0.24, 0.04)
    if g > 0.05:
        c = pos + R @ V((0.05, 0.1, 0.06)); n = nz(V((0.2, 0.3, 1.0)))
        for a in (0.0, PI / 2):
            u = V((math.cos(a), math.sin(a), 0)) * 0.05 * g; Q.append(hd.face([c - u, c + V((0, 0, 0.01)) + nz(np.cross(u, n)) * 0.006, c + u, c - nz(np.cross(u, n)) * 0.006], (255, 255, 236), emit=True))
    return [q for q in Q if q]

# ======================= the fire =======================
def fire_geo(t, SP, KP0):
    """one short stylised burst from her mouth at the knight's (standing) head height: he ducks, it passes over him onto the wall"""
    if not (T_FIRE[0] - 0.02 <= t < T_FIRE[1] + 0.25): return [], None
    hc = V(SP['_head'], float); RH = SP['_RH']; mo = hc + RH @ V((0.0, -0.055, 0.1))
    tgt = V(KP0, float) + V((0.75, 1.78, -0.5)); d = nz(tgt - mo); L = float(np.linalg.norm(tgt - mo))
    u = (t - T_FIRE[0]) / (T_FIRE[1] - T_FIRE[0]); reach = min(1.0, u / 0.35) * L; tail = max(0.0, (u - 0.85) / 0.4) * L
    side = nz(np.cross(d, V((0, 1.0, 0)))); upv = np.cross(side, d); Q = []
    for i in range(46):
        s = tail + (reach - tail) * hsh(i, 7) if reach > tail else reach
        if s < 0.05: continue
        r = 0.025 + 0.16 * (s / L) ** 0.8
        a = 2 * PI * hsh(i, 9) + t * 9; c = mo + d * s + (side * math.cos(a) + upv * math.sin(a)) * r * hsh(i, 11) * 0.9
        sz = 0.03 + 0.05 * (s / L); col = [(255, 238, 150), (255, 176, 60), (255, 112, 30), (230, 70, 20)][min(3, int(4 * s / L + hsh(i, 13)))]
        q = hd.face([c - side * sz, c + upv * sz * 1.2 + d * 0.02, c + side * sz, c - upv * sz * 0.6], col, emit=True)
        if q: Q.append(q)
    light = (tuple(mo + d * min(reach, L * 0.9)), (255, 140, 50), 0.55 * win(t, T_FIRE[0], T_FIRE[1], 0.06))
    return Q, light

# ======================= camera, lights, frame =======================
CAM_P = V((0.02, 1.66, 2.1)); CAM_T = V((0.02, 1.64, -0.1)); FOV = 20.5
def camera(t):
    sh = 0.0
    for t0, amp in ((T_POP, 0.004), (T_FIRE[0], 0.006)):
        if 0 <= t - t0 < 0.3: sh += amp * math.sin((t - t0) * 70) * math.exp(-(t - t0) * 10)
    return CAM_P + V((sh, sh * 0.6, 0)), CAM_T, FOV
def world(t):
    SP = sor_pose(t); KP = knight_pose(t)
    layers = [SET, torches(t, 0.6 * win(t, T_FIRE[0], T_FIRE[1], 0.05))]
    layers.append(hd.human(SOR, SP)); layers.append(knight_body(KP)); layers.append(helmet_geo(t, KP))
    fq, fl = fire_geo(t, SP, KN0); layers.append(fq)
    L = [((0.0, 2.3, 1.6), (255, 226, 196), 0.72), ((-0.9, 1.9, 1.2), (180, 192, 236), 0.24), ((0.9, 1.9, 1.2), (180, 192, 236), 0.24)]
    for i, p in enumerate(TORCH): L.append((tuple(p + V((0.15 * (1 if i else -1), 0.2, 0.3))), (255, 150, 70), 0.6 * (1 + 0.08 * math.sin(t * 13 + i))))
    if fl is not None: L.append(fl)
    return layers, L, SP, KP
def frame_low(t):
    pos, tgt, fov = camera(t); cam = Camera.look(tuple(pos), tuple(tgt))
    layers, L, SP, KP = world(t)
    R = Renderer(W, H, fog=(26, 20, 26))
    img, vi, zb = zrender(R, cam, layers, L, fov=fov, fog_start=4, fog_end=14, ambient=0.18, return_z=True)
    a = look.outline(np.asarray(img).astype(np.float32), zb)
    a = np.clip((a * np.array([1.03, 1.0, 0.97]) - 110) * 1.06 + 104, 0, 255)
    return post.ps1(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), levels=7)

# ======================= the source caption (kept, restyled in pixel font) =======================
CAP = 'THE FIRST TO EVER RAGEBAIT'
EMO = ['..YYYY..', '.YYYYYY.', 'YKYYYYKY', 'YYYYYYYY', 'BKKKKKKB', 'BYKRRKYB', '.YYKKYY.', '..YYYY..']     # laughing-crying face (pixel sprite)
EMO_C = {'Y': (255, 204, 60), 'K': (60, 30, 20), 'B': (110, 190, 255), 'R': (220, 70, 80)}
def caption(d):
    sc = 7; rows = ['THE FIRST TO EVER', 'RAGEBAIT']
    y = 40
    for i, s in enumerate(rows):
        look.draw_cells(d, look.text_cells(s, int(540 - font.width(s, sc) / 2), y + i * 66, sc, (250, 248, 240)), 5)
    ps = 10; ex = 540 - (2 * 8 * ps + 14) // 2; ey = y + 2 * 66 + 8
    for k in range(2):
        for j, row in enumerate(EMO):
            for i, ch in enumerate(row):
                if ch == '.': continue
                x0 = ex + k * (8 * ps + 14) + i * ps; y0 = ey + j * ps
                d.rectangle([x0 - 2, y0 - 2, x0 + ps + 1, y0 + ps + 1], fill=(0, 0, 0))
        for j, row in enumerate(EMO):
            for i, ch in enumerate(row):
                if ch == '.': continue
                x0 = ex + k * (8 * ps + 14) + i * ps; y0 = ey + j * ps; d.rectangle([x0, y0, x0 + ps - 1, y0 + ps - 1], fill=EMO_C[ch])
def frame_final(t):
    img = frame_low(t); arr = post.upscale(img, S)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); caption(ImageDraw.Draw(im))
    return np.asarray(im).astype(np.float32)

TEST = os.environ.get('TEST')
if TEST and __name__ == '__main__':
    ts = [float(x) for x in TEST.split(',')] if TEST != 'all' else [round(x, 2) for x in np.arange(0, DUR, float(os.environ.get('STEP', '2.0')))]
    tw_ = int(os.environ.get('TW', '270'))
    ims = [Image.fromarray(np.clip(frame_final(x), 0, 255).astype(np.uint8)).resize((tw_, tw_ * 16 // 9), Image.LANCZOS) for x in ts]
    th = ims[0].size[1]; per = int(os.environ.get('PER', '8')); rows = (len(ims) + per - 1) // per
    shp = Image.new('RGB', (min(per, len(ims)) * (tw_ + 2), rows * (th + 18)), (30, 30, 30)); dd = ImageDraw.Draw(shp)
    for i, (im, x) in enumerate(zip(ims, ts)): shp.paste(im, ((i % per) * (tw_ + 2), (i // per) * (th + 18))); dd.text(((i % per) * (tw_ + 2) + 4, (i // per) * (th + 18) + th + 3), f'{x:.2f}', fill=(255, 255, 0))
    shp.save(os.environ.get('TEST_OUT', 'test_sr.png')); print('test written', DUR, N); sys.exit()

# ======================= QA manifest =======================
QA = dict(fps=FPS, dur=DUR, W=W, frame=lambda t: Image.fromarray(np.clip(frame_final(t), 0, 255).astype(np.uint8)).resize((W, H), Image.BOX), chars={},
          geom=lambda t, name, st, V_: [], camera=lambda t: camera(t)[0], min_cam_dist=0.3, camera_ok=lambda p: True, allow_jump=[], weapon_events=[],
          scenes=[dict(id='corridor', t0=0.0, t1=DUR, action='one stable shot')], texts=lambda: [('cap', 'THE FIRST TO EVER', 6)])

# ======================= AUDIO: the untouched source track + a few quiet effects (a separate stem) =======================
OUT = os.path.join(ROOT, 'out'); os.makedirs(OUT, exist_ok=True)
def build_audio(path):
    """writes the SFX stem (48 kHz stereo, same length as the source). The final mux = source audio at unity gain + this stem:
    ffmpeg -i video -i voice/sorceress_src/src48k.wav -i out/sr_sfx.wav -filter_complex "[1:a][2:a]amix=inputs=2:normalize=0[a]" ..."""
    import soundfile as sf
    from nightkit.audio import Sound
    s_ = Sound(DUR, loop=False, seed=5); sr = s_.sr; n = s_.n; FX = np.zeros(n)
    def put(x, t0, v=1.0):
        i = int(round(t0 * sr)); j = min(n, i + len(x))
        if i < n: FX[i:j] += (x * v)[:j - i]
    def T(d): return np.arange(int(sr * d)) / sr
    # quiet levels: each effect is set relative to the speech around it (source peaks at -1.8 dBFS, speech RMS ~ -20 dBFS)
    tt = T(0.6)
    ting = sum(a * np.sin(2 * np.pi * f * tt) * np.exp(-tt * d) for f, a, d in ((2637, 1.0, 9), (3951, 0.5, 14), (5274, 0.25, 20)))
    put(ting, T_POP + 0.01, 0.02)                                                 # helmet ping
    tt = T(0.25)
    for k in range(5): put(np.sin(2 * np.pi * (1400 + 300 * k) * tt) * np.exp(-tt * 40), T_TREMBLE + 0.08 * k, 0.006)   # tremble rattle
    put(ting * 0.6, T_LAND, 0.012)                                                # it lands
    rng = np.random.default_rng(3)
    for t0 in (T_FIX[0], T_FIX2[0], T_FIRE[0] - 0.08, T_FIRE[1] + 0.4):           # brief armour movement
        x = s_.filt_short(rng.normal(0, 1, int(sr * 0.2)), lo=1500, hi=6000) * np.sin(np.pi * T(0.2) / 0.2) ** 2; put(x, t0, 0.012)
    d = T_FIRE[1] - T_FIRE[0] + 0.15; tt = T(d)
    whoosh = s_.filt_short(rng.normal(0, 1, len(tt)), lo=120, hi=2400) * np.sin(np.pi * tt / d) ** 1.5
    put(whoosh, T_FIRE[0], 0.05)                                                  # one short fire burst, inside the 0.4 s pause
    fi = np.clip(np.minimum(np.arange(n) / (0.01 * sr), (n - np.arange(n)) / (0.01 * sr)), 0, 1)
    sf.write(path, np.stack([FX * fi, np.roll(FX, 60) * fi], 1), sr)
    return path
if __name__ == '__main__' and os.environ.get('PART') == 'audio':
    print(build_audio(os.path.join(OUT, 'sr_sfx.wav')))
    import shutil; shutil.copy(os.path.join(SRC, 'src48k.wav'), os.path.join(OUT, 'sorceress_rage.wav')); sys.exit()
if __name__ == '__main__' and os.environ.get('PART'):
    a, b = map(int, os.environ['PART'].split(':'))
    import subprocess
    p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W * S}x{H * S}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', os.path.join(OUT, f'sr_{a:05d}.mp4')], stdin=subprocess.PIPE)
    vhs = post.VHS(W * S, H * S, S, grade='none', chroma=0, scan_dark=1.0, vignette=0.2, grain=0.8, band_period=1e9)
    for f in range(a, min(b, N)): p.stdin.write(vhs(frame_final(f / FPS), f, f / FPS).tobytes())
    p.stdin.close(); p.wait()
