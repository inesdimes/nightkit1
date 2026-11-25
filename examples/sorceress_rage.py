"""THE FIRST TO EVER RAGEBAIT - visual adaptation of a source reel (Insert Disc 2, 25 Nov 2026). 57.57 s, 30 fps, 9:16, nightkit HD + face rig.
Brief: pasted GPT brief (visual adaptation; original audio unchanged). Source: voice/snapgram.io_fv3w5zze9dpz.mp4 (copy + analysis in
voice/sorceress_src/: mesh.json = MediaPipe FaceMesh per source frame, words.json = Whisper word times, src48k.wav = the untouched audio).
The source has TWO voices: the on-screen speaker (6-28.6 s, 34-42.6 s, 55.45-57.3 s) and an off-screen voice (the rant). Enes (25 Nov):
the sorceress plays the on-screen speaker (mouth / eyes / brows / head from the tracked face), the knight plays the off-screen voice
(mouth from the audio envelope). Gags on measured beats: helmet tremble on the first rise (10.67 s), helmet pops on the loudest speaker
word (13.30 s), fire in the real 0.4 s pause after the knight's 'up!' (44.00-44.40 s) while he ducks.

Frames:  TEST=0,13.3,... python examples/sorceress_rage.py -> test_sr.png
Render:  python tools/render_parts.py examples/sorceress_rage.py --prefix sr --audio sorceress_rage.wav --out ../renders/sorceress_rage/x.mp4 --parts 8
         (render_parts' loudnorm must NOT be used for the final: mux the untouched source audio with tools in the docstring of build_audio)"""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera
from nightkit.zraster import zrender
from nightkit import post, look, hd, motion, font, facerig
import dragon_taxes as dtx                      # locked: the series knight (HD, open helmet, blue cape + plume), torch flames

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
SPK = [(5.95, 28.62), (33.85, 42.6), (55.45, 57.35)]          # on-screen speaker -> the sorceress talks
KNV = [(0.0, 5.95), (28.62, 33.85), (42.6, 55.45)]             # off-screen voice -> the knight talks
T_TREMBLE = 10.667; T_POP = 13.30; T_FIRE = (44.0, 44.4)       # measured beats (see the docstring)
T_LAND = 13.95; T_FIX = (15.75, 16.6); T_FIX2 = (29.0, 30.0)
def in_w(t, ws, pad=0.0): return any(a - pad <= t < b + pad for a, b in ws)
def _tracks():
    from scipy.ndimage import median_filter, uniform_filter1d
    import soundfile as sf
    from scipy.signal import butter, sosfiltfilt
    R = MESH['rows']; n = len(R); fps = MESH['fps']
    def ser(k):
        v = np.array([r[k] if r else np.nan for r in R], float); i = np.arange(n); m = ~np.isnan(v); return np.interp(i, i[m], v[m])
    T = np.arange(n) / fps
    op = median_filter(ser('open'), 3); iw = ser('inner_w'); eR = ser('eyeR'); eL = ser('eyeL'); bR = ser('browR'); bL = ser('browL')
    roll = uniform_filter1d(ser('roll'), 5); yaw = uniform_filter1d(ser('yaw'), 7); pitch = uniform_filter1d(ser('pitch'), 7)
    spk = np.array([in_w(t, SPK) for t in T], float); spk = uniform_filter1d(spk, 5)
    C = {}
    C['open'] = np.clip((op - 0.014) / 0.19, 0, 1.15) * spk
    C['jaw'] = C['open'] * 0.95
    iwm = np.median(iw[spk > 0.5]); C['wide'] = np.clip((iw - iwm) / 0.06, 0, 1) * spk * 0.8
    C['round'] = np.clip((iwm - iw) / 0.05, 0, 1) * np.clip(C['open'] * 2.5, 0, 1) * spk
    em = np.median(np.r_[eR, eL])
    C['eyesR'] = np.clip(eR / em, 0.0, 1.3); C['eyesL'] = np.clip(eL / em, 0.0, 1.3)
    bm = np.median(np.r_[bR, bL])
    C['browR'] = np.clip((bR - bm) / 0.016, -1, 1.2); C['browL'] = np.clip((bL - bm) / 0.016, -1, 1.2)
    rm = np.median(roll); ym = np.median(yaw); pm = np.median(pitch)
    C['tilt'] = -np.radians(roll - rm) * 0.55; C['hyaw'] = -(yaw - ym) * 0.28; C['nod'] = -(pitch - pm) * 2.2
    # knight: off-screen voice envelope (200-3000 Hz), attack 15 ms / release 60 ms, only in his windows
    a, sr = sf.read(os.path.join(SRC, 'src48k.wav')); a = a.mean(1) if a.ndim > 1 else a
    sos = butter(4, [200, 3000], btype='band', fs=sr, output='sos'); e = np.abs(sosfiltfilt(sos, a)); hop = sr / fps
    env = np.array([e[int(k * hop):int((k + 1) * hop)].mean() for k in range(n)]); edb = 20 * np.log10(env + 1e-6)
    kn = np.array([in_w(t, KNV) for t in T], float)
    lv = np.clip((edb - (-40.0)) / 24.0, 0, 1) * kn
    out = np.zeros(n); x = 0.0
    for i, v in enumerate(lv): x = x + (v - x) * (0.75 if v > x else 0.45); out[i] = x
    C['kmouth'] = out; C['edb'] = edb; C['T'] = T
    return C
TR_ = _tracks()
def tr(k, t): return float(np.interp(t, TR_['T'], TR_[k]))

# ======================= cast =======================
SOR = hd.spec(h=1.7, build=0.9, fem=1.0, skin=(230, 188, 158), hair=(118, 46, 30), hair_style='long', eye=(84, 120, 70), brow=(96, 40, 26),
              lip=(190, 96, 96), tunic=(46, 108, 66), tunic2=(36, 88, 54), skirt=0.95, sleeves='long', pants=(36, 88, 54), boots=(60, 40, 30),
              belt=(196, 162, 70), buckle=(236, 200, 90), collar=(204, 170, 76), cloak=(30, 72, 46), cloak_len=1.0)
GOLD = (226, 190, 84)
SOR_STYLE = dict(skin=SOR['skin'], eye=SOR['eye'], brow=SOR['brow'], lip=(186, 92, 96), mouth_in=(70, 20, 30), teeth=(240, 234, 222),
                 tongue=(186, 84, 92), stubble=False, scar=False)
_orig_head = hd.head
def rig_head(hc, RH, S_, P, k):
    """the sorceress gets the high-density face rig (facerig) + long auburn hair + a gold circlet; everyone else the stock HD head"""
    if 'E' not in P: return _orig_head(hc, RH, S_, P, k)
    facerig.set_style(**SOR_STYLE)
    E = P['E']; M = facerig.Mesh(hc, RH)
    facerig.head_mesh(M, E); facerig.eyes_geo(M, E); facerig.brows_geo(M, E); facerig.nose_geo(M, E); facerig.mouth_geo(M, E)
    rx, ry, rz = facerig.RX, facerig.RY, facerig.RZ
    Q = M.Q + hd.hair(hc, RH, S_, P, 1.0, (rx, ry, rz), lambda p: facerig.base_def(V(p, float)[None])[0])
    def L(x, y, z): return hc + RH @ V((x, y, z))
    Q += hd.limb(L(0, 0.058, -0.004), L(0, 0.07, -0.008), rz * 1.08, rz * 1.06, GOLD, n=16, m=1, ref=RH @ V((0, 0, 1.0)), flat=0.92)   # circlet
    Q += hd.bx(L(0, 0.066, rz * 1.06), RH, (0.009, 0.009, 0.004), (60, 200, 120), emit=True)                                       # its green gem
    return Q
hd.head = rig_head

def knight_body(P):
    """the series knight without his helmet (dtx.knight minus knight_helmet): the helmet is animated separately"""
    Q = hd.human(dtx.KNIGHT, P); RW = P['_RW']; ch = P['_chest']; st = (178, 186, 200); dk = (128, 136, 152)
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

# ======================= poses =======================
SOR0 = (-0.12, 0.0, 0.0); KN0 = (0.17, 0.0, -0.6); KYAW0 = -0.38
def fire_u(t): return seg01(t, T_FIRE[0], T_FIRE[1])
def sor_expr(t):
    """face-rig expression from the tracked source face (speaker windows) + the listening / irritation layer"""
    talk = in_w(t, SPK, 0.05)
    E = dict(open=tr('open', t), jaw=tr('jaw', t), wide=tr('wide', t), round=tr('round', t), teeth=0.0, press=0.0,
             eyesR=tr('eyesR', t), eyesL=tr('eyesL', t), browR=0.0, browL=0.0, innerR=0.0, innerL=0.0, furrow=0.0,
             squintR=0.0, squintL=0.0, smR=0.0, smL=0.0, look=(0.0, 0.0))
    br = 0.7 * tr('browR', t); bl = 0.7 * tr('browL', t)
    # irritation builds across her performance (the brief): furrow + squint ramp, inner brows pull down
    irr = 0.15 + 0.55 * seg01(t, 6.0, 42.0)
    E['browR'] = br - 0.25 * irr; E['browL'] = bl - 0.25 * irr; E['furrow'] = irr; E['innerR'] = -0.4 * irr; E['innerL'] = -0.4 * irr
    E['squintR'] = 0.25 * irr; E['squintL'] = 0.25 * irr
    if not talk:
        E['press'] = 0.6; E['open'] = 0.0; E['jaw'] = 0.0
        # listening to the knight: the opening (unimpressed half-smirk), the second rant (eye-roll), the big rant (furious -> fire -> calm smirk)
        if t < 6.0: E['smR'] = 0.35; E['eyesR'] = min(E['eyesR'], 0.85); E['eyesL'] = min(E['eyesL'], 0.85)
        if 28.6 <= t < 33.85: E['look'] = (0.0, 0.7 * win(t, 30.2, 31.2, 0.3)); E['smR'] = 0.25
        if 42.6 <= t < T_FIRE[0]:
            k = seg01(t, 42.6, 43.6); E['furrow'] = 0.7 + 0.3 * k; E['squintR'] = 0.4 + 0.4 * k; E['squintL'] = 0.4 + 0.4 * k
            E['browR'] = -0.6 - 0.3 * k; E['browL'] = -0.6 - 0.3 * k; E['look'] = (0.85 * k, 0.1)
        if T_FIRE[1] <= t < 55.45:
            c = sm(seg01(t, T_FIRE[1] + 0.2, T_FIRE[1] + 1.2)); E['furrow'] = 0.9 * (1 - c) + 0.35 * c; E['smR'] = 0.55 * c; E['smL'] = 0.2 * c
            E['squintR'] = 0.3; E['squintL'] = 0.3; E['look'] = (0.6 * (1 - c), 0.0); E['browR'] = -0.2 + 0.5 * c; E['browL'] = -0.4
    fu = fire_u(t)
    if 0 < fu < 1 or (T_FIRE[0] - 0.12 <= t < T_FIRE[1] + 0.12):                  # breathes fire: jaw wide, brows down hard
        f = win(t, T_FIRE[0], T_FIRE[1], 0.1)
        E['open'] = lerp(E['open'], 1.1, f); E['jaw'] = lerp(E['jaw'], 1.1, f); E['wide'] = lerp(E['wide'], 0.6, f); E['furrow'] = 1.0
        E['browR'] = -1.0; E['browL'] = -1.0; E['eyesR'] = 0.8; E['eyesL'] = 0.8; E['press'] = 0.0; E['look'] = (1.0, 0.0)
    # natural blinks while listening (the tracked eyes carry the blinks while she talks)
    if not talk:
        for b in (2.3, 4.9, 31.0, 47.6, 51.8, 54.0):
            bk = max(0.0, 1 - abs(t - b) / 0.07)
            E['eyesR'] *= 1 - bk; E['eyesL'] *= 1 - bk
    return E
def sor_pose(t):
    talk = in_w(t, SPK, 0.05)
    hy = tr('hyaw', t) if talk else 0.0; nod = tr('nod', t) if talk else 0.0; tilt = tr('tilt', t) if talk else 0.0
    if 42.6 <= t < 45.2: hy = lerp(hy, -0.45, win(t, 43.3, 44.6, 0.35)); tilt = lerp(tilt, -0.08, win(t, 43.3, 44.6, 0.35))   # turns to the knight to breathe fire
    if 28.6 <= t < 33.85: tilt = 0.08 * win(t, 29.0, 33.4, 0.4)
    br = 0.012 * math.sin(t * 2 * PI / 3.6)                                            # breathing
    P = dict(base=SOR0, yaw=0.0, lean=0.02 + br * 0.5, head=(hy, nod, tilt), pel=(0, br, 0), cape_sway=0.05 * math.sin(t * 0.9))
    gst = win(t, 17.0, 19.5, 0.5) + win(t, 36.4, 38.6, 0.5)                              # restrained hand movement on long phrases
    P['rh'] = lerp3((0.2, 0.92, 0.2), (0.24, 1.08, 0.3), gst); P['lh'] = (-0.2, 0.9, 0.18); P['rgrip'] = 0.35; P['lgrip'] = 0.4
    P['E'] = sor_expr(t)
    return P

def k_talk(t): return tr('kmouth', t)
def knight_pose(t):
    """reactions: glance, uneasy, follows the helmet with his eyes, freezes mid-fix, ducks under the fire, recovers"""
    P = dict(base=KN0, yaw=KYAW0, eyes='open', mouth='neutral', brow=0.2, lean=0.04, cape_sway=0.1 * math.sin(t * 1.2), look=(-0.4, 0.0), head=(-0.15, 0.05, 0.0))
    P['rh'] = (0.24, 0.98, 0.14); P['lh'] = (-0.22, 0.96, 0.16); P['rgrip'] = 0.5; P['lgrip'] = 0.5
    kt = k_talk(t)
    if in_w(t, KNV):                                  # he talks (off-screen voice): turns to her, brow up
        P['head'] = (-0.35, 0.02, 0.0); P['look'] = (-0.6, 0.0); P['brow'] = 0.5 if t > 42 else -0.1
        P['mouth'] = 'open' if kt > 0.5 else ('o' if kt > 0.18 else 'neutral')
        if t > 42.6: P['brow'] = 0.9; P['eyes'] = 'wide' if kt > 0.6 else 'open'
    else:                                              # listening: eyes on her, uneasy
        P['look'] = (-0.8, 0.0); P['brow'] = -0.25
    if 8.6 <= t < 9.6: P['head'] = (-0.15, 0.05, 0.06 * win(t, 8.7, 9.4, 0.2)); P['brow'] = -0.5          # one restrained uneasy reaction
    # the helmet pop: eyes up, mouth 'o'
    if T_POP - 0.05 <= t < T_LAND + 0.4:
        P['look'] = (0.0, 1.0); P['eyes'] = 'wide'; P['mouth'] = 'o'; P['head'] = (-0.1, 0.25 * win(t, T_POP, T_LAND, 0.15), 0.0)
    # tries to straighten the helmet, then freezes when her expression intensifies
    fx = win(t, T_FIX[0], T_FIX[1], 0.25)
    if fx > 0:
        P['rh'] = lerp3(P['rh'], (0.2, 1.66, 0.06), fx); P['lh'] = lerp3(P['lh'], (-0.2, 1.66, 0.06), fx); P['rgrip'] = 0.3; P['lgrip'] = 0.3
        P['rpalm'] = (-1.0, 0.0, 0.0); P['lpalm'] = (1.0, 0.0, 0.0)
    fx2 = win(t, T_FIX2[0], T_FIX2[1], 0.3)
    if fx2 > 0:
        P['rh'] = lerp3(P['rh'], (0.2, 1.66, 0.06), fx2); P['lh'] = lerp3(P['lh'], (-0.2, 1.66, 0.06), fx2); P['rpalm'] = (-1.0, 0.0, 0.0); P['lpalm'] = (1.0, 0.0, 0.0)
    if T_FIX[1] <= t < T_FIX[1] + 1.0: P['eyes'] = 'wide'; P['brow'] = -0.6; P['look'] = (-0.9, 0.0)
    # duck under the fire (anticipates by a few frames), keeps yelling from down there, recovers
    dk = sm(seg01(t, T_FIRE[0] - 0.1, T_FIRE[0] + 0.12)) * (1 - sm(seg01(t, T_FIRE[1] + 0.35, T_FIRE[1] + 0.9)))
    if dk > 0:
        P['crouch'] = 0.3 * dk; P['lean'] = 0.04 + 0.3 * dk; P['head'] = (-0.35, 0.25 * dk, 0.0); P['eyes'] = 'wide'; P['look'] = (-0.3, 1.0)
        P['rh'] = lerp3(P['rh'], (0.22, 1.25, 0.32), dk); P['lh'] = lerp3(P['lh'], (-0.24, 1.28, 0.3), dk)
        P['rf'] = (0.14, 0.07, 0.12); P['lf'] = (-0.14, 0.07, -0.08)
    return P

# ======================= the helmet gag =======================
def helmet_state(t, KP):
    """(head centre, rotation) for the helmet: trembles at T_TREMBLE, pops at T_POP (arc + spin, stays in frame), lands crooked,
    half-fixed at T_FIX (freezes), fully straightened at T_FIX2"""
    hc = V(KP['_head'], float); RH = KP['_RH']
    up = RH @ V((0, 1.0, 0))
    tr_ = win(t, T_TREMBLE - 0.05, T_TREMBLE + 0.7, 0.08) + 0.6 * win(t, T_POP - 0.35, T_POP - 0.02, 0.05)
    if tr_ > 0 and t < T_POP:
        j = tr_ * 0.012 * math.sin(t * 95) ; return hc + up * (abs(j) * 0.6), RH @ hd.Rz(j * 2.2)
    crook = 0.0; off = V((0, 0, 0.0))
    if t >= T_POP:
        u = t - T_POP; fl = T_LAND - T_POP
        if u < fl:
            s = u / fl; h = 0.2 * 4 * s * (1 - s)                          # parabola, apex 0.3 m above the head (stays in frame, under the caption)
            pos = hc + up * (h + 0.01) + (RH @ V((0.06, 0, 0.04))) * s
            return pos, RH @ hd.Rx(-2 * PI * s * 1.0) @ hd.Rz(0.6 * s)
        crook = 0.38; off = RH @ V((0.03, 0.012, 0.0))
        b = max(0.0, 1 - (u - fl) / 0.18); off = off + up * 0.025 * b * abs(math.sin((u - fl) * 40))   # a small bounce on landing
        crook *= 1 - 0.55 * sm(seg01(t, T_FIX[0] + 0.15, T_FIX[0] + 0.55))                            # half straightened ... then he freezes
        crook = crook * (1 - sm(seg01(t, T_FIX2[0] + 0.2, T_FIX2[1] - 0.15))) + 0.0
        if t > T_FIX2[1]: crook = 0.0; off = V((0, 0, 0.0))
        else: off = off * (1 - sm(seg01(t, T_FIX2[0] + 0.2, T_FIX2[1] - 0.15)))
    return hc + off, RH @ hd.Rz(-crook)
def helmet_geo(t, KP):
    pos, R = helmet_state(t, KP)
    Q = dtx.knight_helmet(dict(_head=pos, _RH=R, cape_sway=KP.get('cape_sway', 0.0)))
    g = win(t, T_POP + 0.12, T_POP + 0.24, 0.04)                                  # a small metal glint in flight
    if g > 0.05:
        c = pos + R @ V((0.05, 0.1, 0.06)); n = nz(V((0.2, 0.3, 1.0)))
        for a in (0.0, PI / 2):
            u = V((math.cos(a), math.sin(a), 0)) * 0.05 * g; Q.append(hd.face([c - u, c + V((0, 0, 0.01)) + nz(np.cross(u, n)) * 0.006, c + u, c - nz(np.cross(u, n)) * 0.006], (255, 255, 236), emit=True))
    return [q for q in Q if q]

# ======================= the fire =======================
def fire_geo(t, SP):
    """one short stylised burst from her mouth towards the knight's (now ducked) head height; above him, onto the wall"""
    if not (T_FIRE[0] - 0.02 <= t < T_FIRE[1] + 0.25): return [], None
    hc = V(SP['_head'], float); RH = SP['_RH']; mo = hc + RH @ V((0.0, -0.055, 0.1))
    tgt = V((1.05, 1.8, WALLZ + 0.25)); d = nz(tgt - mo); L = float(np.linalg.norm(tgt - mo))
    u = (t - T_FIRE[0]) / (T_FIRE[1] - T_FIRE[0]); reach = min(1.0, u / 0.35) * L; tail = max(0.0, (u - 0.85) / 0.4) * L
    side = nz(np.cross(d, V((0, 1.0, 0)))); upv = np.cross(side, d); Q = []
    for i in range(46):
        s = tail + (reach - tail) * hsh(i, 7) if reach > tail else reach
        if s < 0.04: continue
        r = 0.03 + 0.22 * (s / L) ** 0.8
        a = 2 * PI * hsh(i, 9) + t * 9; c = mo + d * s + (side * math.cos(a) + upv * math.sin(a)) * r * hsh(i, 11) * 0.9
        sz = 0.035 + 0.06 * (s / L); col = [(255, 238, 150), (255, 176, 60), (255, 112, 30), (230, 70, 20)][min(3, int(4 * s / L + hsh(i, 13)))]
        q = hd.face([c - side * sz, c + upv * sz * 1.2 + d * 0.02, c + side * sz, c - upv * sz * 0.6], col, emit=True)
        if q: Q.append(q)
    light = (tuple(mo + d * min(reach, L * 0.92)), (255, 140, 50), 0.55 * win(t, T_FIRE[0], T_FIRE[1], 0.06))
    return Q, light

# ======================= camera, lights, frame =======================
CAM_P = V((0.03, 1.64, 1.95)); CAM_T = V((0.03, 1.6, -0.2)); FOV = 18.0
def camera(t):
    sh = 0.0
    for t0, amp in ((T_POP, 0.004), (T_FIRE[0], 0.006)):
        if 0 <= t - t0 < 0.3: sh += amp * math.sin((t - t0) * 70) * math.exp(-(t - t0) * 10)
    return CAM_P + V((sh, sh * 0.6, 0)), CAM_T, FOV
def world(t):
    SP = sor_pose(t); KP = knight_pose(t)
    layers = [SET, torches(t, 0.6 * win(t, T_FIRE[0], T_FIRE[1], 0.05))]
    layers.append(hd.human(SOR, SP)); layers.append(knight_body(KP)); layers.append(helmet_geo(t, KP))
    fq, fl = fire_geo(t, SP); layers.append(fq)
    L = [((-0.9, 2.3, 1.4), (255, 226, 196), 0.72), ((0.9, 1.9, 1.2), (180, 192, 236), 0.26)]
    for i, p in enumerate(TORCH): L.append((tuple(p + V((0.15 * (1 if i else -1), 0.2, 0.3))), (255, 150, 70), 0.65 * (1 + 0.08 * math.sin(t * 13 + i))))
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
