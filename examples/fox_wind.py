"""FOX WIND GAG (Insert Disc 2, 24 Nov 2026) ~10 s vertical musical gag, nightkit HD, no speed-up (lip-sync to the song).
Brief: pasted 24 Nov (wind gag + lip-sync), song = voice/fox.mp3 (reference clip voice/fox.mp4 used for timing / framing only).
New character: SIR BRISK, a young cocky knight (steel plate, red tabard with a gold fox badge, red cape, nasal helm with chin strap).
Tight front shot, camera steady. Calm while the music builds -> on the detected drop a gust hits from the camera, the strap snaps,
the helmet lifts straight up, spins backward out of frame; hair / cape / leaves / torch flames ride the same gust; then he lip-syncs
(mouth driven by the song's vocal band, not invented), smirks, eyebrow flash in the phrase gap; final downbeat = confident look,
off-screen helmet clank, a glance, back to camera.
Face: own high-density head (~1,000 faces + parametric eyes / lids / brows / mouth with teeth + tongue, jaw + cheek deform); the
rest stays the normal hd.py low-poly body.

  TEST=0,2,2.3,4,6 python examples/fox_wind.py   -> test_fw.png contact sheet
  PART=audio python examples/fox_wind.py         -> out/fox_wind.wav (song segment + wind / strap / clank SFX)
  PART=a:b python examples/fox_wind.py           -> out/fw_<a>.mp4 frames a..b"""
import os, sys, math, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE); sys.path.insert(0, ROOT)
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, quad
from nightkit.zraster import zrender
from nightkit import post, look, hd, motion

W, H, S = 360, 640, 3                       # 360x640 internal (x3 = 1080x1920): the brief needs a readable face
FPS = 30                                    # 30 fps for the lip-sync
PI = math.pi
V = np.array
OUT = os.path.join(ROOT, 'out'); os.makedirs(OUT, exist_ok=True)
SONG = os.path.join(ROOT, 'voice', 'fox.mp3')
sm = motion.smooth
def seg01(t, a, b): return max(0.0, min(1.0, (t - a) / (b - a))) if b > a else (1.0 if t >= b else 0.0)
def lerp(a, b, u): return a + (b - a) * u
def mixc(a, b, u): u = max(0.0, min(1.0, u)); return tuple(int(round(x + (y - x) * u)) for x, y in zip(a, b))
def hsh(i, s=0): v = math.sin(i * 127.1 + s * 311.7) * 43758.5453; return v - math.floor(v)
def bump(t, c, w): return math.exp(-((t - c) / w) ** 2)
shade = hd.shade

# ======================= song analysis (drop, tempo, vocal envelope) =======================
def load_song(sr=22050, ch=1):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', SONG, '-ac', str(ch), '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    return x.reshape(-1, ch) if ch > 1 else x

def analyze():
    cache = os.path.join(OUT, 'fox_wind_analysis.npz')
    if os.path.exists(cache) and os.path.getmtime(cache) > os.path.getmtime(SONG) and os.path.getmtime(cache) > os.path.getmtime(__file__):
        z = np.load(cache); return {k: z[k] for k in z.files}
    x = load_song(); sr = 22050; Wn = 1024; hop = 110; fr = sr / hop
    n = (len(x) - Wn) // hop; f = np.fft.rfftfreq(Wn, 1 / sr); win = np.hanning(Wn)
    frames = np.lib.stride_tricks.sliding_window_view(x, Wn)[::hop][:n] * win
    M = np.abs(np.fft.rfft(frames, axis=1))
    L = np.log1p(M * 10)
    flux_all = np.r_[0, np.maximum(np.diff(L, axis=0), 0).sum(1)]
    flux_low = np.r_[0, np.maximum(np.diff(L[:, f < 150], axis=0), 0).sum(1)]
    low = (M[:, f < 150] ** 2).sum(1)
    # the drop = strongest bass onset (flux in the low band x bass energy jump) in the first 6 s
    i6 = int(6 * fr); score = flux_low[:i6] * np.r_[1, low[1:i6] / (low[:i6 - 1] + 1e-9)].clip(0, 20)
    i_drop = int(np.argmax(score)); drop = i_drop / fr
    # tempo: autocorrelation of the (de-trended) onset curve after the drop, 70..180 bpm
    fl = flux_all - np.convolve(flux_all, np.ones(41) / 41, 'same'); fl = np.maximum(fl, 0)
    seg = fl[i_drop:]; ac = np.correlate(seg, seg, 'full')[len(seg) - 1:]
    lags = np.arange(len(ac)) / fr; ok = (lags > 60 / 180) & (lags < 60 / 70)
    i_b = int(np.argmax(np.where(ok, ac, 0)))
    # parabolic refinement
    if 0 < i_b < len(ac) - 1:
        a_, b_, c_ = ac[i_b - 1], ac[i_b], ac[i_b + 1]; i_bf = i_b + 0.5 * (a_ - c_) / (a_ - 2 * b_ + c_ + 1e-12)
    else: i_bf = i_b
    bp = i_bf / fr
    # refine the beat period on the strongest onsets across ~16 beats
    best = (-1, bp)
    for cand in np.linspace(bp * 0.985, bp * 1.015, 61):
        idx = [int(round((drop + k * cand) * fr)) for k in range(1, 20)]; idx = [i for i in idx if i < len(fl) - 2]
        sc = sum(fl[i - 2:i + 3].max() for i in idx)
        if sc > best[0]: best = (sc, cand)
    bp = best[1]
    # vocal entrance: first strong onset after the drop where the vocal band (300-3000 Hz) rises well above the post-drop bed
    vb = (M[:, (f > 300) & (f < 3000)] ** 2).sum(1); vbs = np.convolve(vb, np.ones(9) / 9, 'same')
    i1 = i_drop + int(0.3 * fr); bed = np.median(vbs[i1:i1 + int(1.0 * fr)])
    vox = None
    for i in range(i1, min(len(vbs), i_drop + int(4 * fr))):
        if vbs[i] > 2.2 * bed and fl[i] > np.percentile(fl, 85):
            vox = i / fr; break
    if vox is None: vox = drop + 3 * bp
    out = dict(drop=np.float64(drop), bp=np.float64(bp), vox=np.float64(vox))
    np.savez(cache, **out); return out

A = analyze()
DROP_SRC = float(A['drop']); BP = float(A['bp']); VOX_SRC = float(A['vox'])
SRC0 = DROP_SRC - 4 * BP                    # the clip starts exactly four beats before the drop (one bar of build)
DROP = DROP_SRC - SRC0                      # video time of the drop
VOX = VOX_SRC - SRC0
FINAL = DROP + 16 * BP                      # four bars after the drop: the last downbeat
DUR = round(FINAL + 0.62, 3)
N = int(round(DUR * FPS))
def beat_phase(t): return ((t - DROP) / BP) % 1.0
def beats_between(a, b): k0 = math.ceil((a - DROP) / BP); return [DROP + k * BP for k in range(k0, 64) if DROP + k * BP <= b]

def lip_track():
    """per video frame: open (0..1), wide (-1..1), sib (teeth), accent; from the vocal band of the song (mouth leads by ~1 frame)"""
    cache = os.path.join(OUT, 'fox_wind_lips.npz')
    if os.path.exists(cache) and os.path.getmtime(cache) > os.path.getmtime(__file__):
        z = np.load(cache); return {k: z[k] for k in z.files}
    x = load_song(); sr = 22050; Wn = 1536; win = np.hanning(Wn); f = np.fft.rfftfreq(Wn, 1 / sr)
    LEAD = 0.035; nf = N + 2; ev = np.zeros(nf); cen = np.zeros(nf); sib = np.zeros(nf); fx = np.zeros(nf); prev = None
    bv = (f > 250) & (f < 3500); bc = (f > 300) & (f < 3000); bs = (f > 4500) & (f < 9000)
    for i in range(nf):
        c = int((SRC0 + i / FPS + LEAD) * sr); a = x[max(0, c - Wn // 2): c + Wn // 2]
        a = np.pad(a, (0, Wn - len(a))) * win; m = np.abs(np.fft.rfft(a)); p = m ** 2
        ev[i] = p[bv].sum(); cen[i] = (f[bc] * p[bc]).sum() / (p[bc].sum() + 1e-12); sib[i] = p[bs].sum() / (p[bv].sum() + 1e-12)
        lm = np.log1p(m[bv] * 10); fx[i] = 0 if prev is None else np.maximum(lm - prev, 0).sum(); prev = lm
    db = 10 * np.log10(ev + 1e-12); tt = np.arange(nf) / FPS
    vm = tt >= VOX - 0.05
    lo, hi = np.percentile(db[vm], 18), np.percentile(db[vm], 96)
    op = np.clip((db - lo) / (hi - lo), 0, 1) ** 0.85
    # consonant closures: the frame before a sharp vocal onset narrows
    thr = np.percentile(fx[vm], 80)
    for i in range(1, nf - 1):
        if fx[i + 1] > thr and fx[i + 1] > fx[i]: op[i] *= 0.4
    op[~vm] = 0.0
    # smoothing: fast attack, quick release
    o2 = op.copy()
    for i in range(1, nf): o2[i] = op[i] if op[i] > o2[i - 1] else o2[i - 1] * 0.35 + op[i] * 0.65
    c0, c1 = np.percentile(cen[vm], 15), np.percentile(cen[vm], 85)
    wide = np.clip((cen - c0) / (c1 - c0 + 1e-9) * 2 - 1, -1, 1)
    sibf = np.clip((sib - np.percentile(sib[vm], 70)) / (np.percentile(sib[vm], 97) - np.percentile(sib[vm], 70) + 1e-9), 0, 1)
    acc = np.clip((fx - thr) / (fx[vm].max() - thr + 1e-9), 0, 1) * vm
    out = dict(open=o2, wide=wide, sib=sibf * vm, acc=acc)
    np.savez(cache, **out); return out
LIP = lip_track()
def lip_at(t, key):
    a = LIP[key]; u = t * FPS; i = int(min(len(a) - 2, max(0, math.floor(u)))); w = min(1.0, max(0.0, u - i)); return float(a[i] * (1 - w) + a[i + 1] * w)
def acc_env(t, tau=0.22):
    """decaying accent (brow pops on strong syllables)"""
    i1 = int(t * FPS); best = 0.0
    for i in range(max(0, i1 - 12), min(len(LIP['acc']), i1 + 1)):
        best = max(best, float(LIP['acc'][i]) * math.exp(-(t - i / FPS) / tau))
    return best

# ======================= timing =======================
T_SNAP = DROP + 0.04                         # the strap snaps on the gust
T_LIFT = (T_SNAP + 0.06, T_SNAP + 0.36)      # straight up off the head
T_GONE = T_SNAP + 1.35                        # out of frame
T_GAP = None                                 # the phrase gap (eyebrow flash): longest quiet stretch in the vocal part
def _find_gap():
    o = LIP['open']; best = (0, None); run = 0
    for i in range(int((VOX + 0.5) * FPS), int((FINAL - 0.6) * FPS)):
        run = run + 1 if o[i] < 0.12 else 0
        if run > best[0]: best = (run, (i - run + 1) / FPS)
    return best[1] if best[0] >= 6 else None
T_GAP = _find_gap()
T_CLANK = FINAL + 0.24
BLINKS = [0.95, VOX - 0.55, VOX + 2.4, (T_GAP + 0.35) if T_GAP else VOX + 3.6, FINAL - 0.75]

def wind(t):
    """gust envelope: a clear hit on the drop, sustain, then dies away"""
    if t < DROP - 0.03: return 0.0
    a = sm(seg01(t, DROP - 0.03, DROP + 0.09))
    d = 1 - sm(seg01(t, DROP + 1.15, DROP + 2.45))
    g = a * (0.25 + 0.75 * d)
    return g * (1 - 0.75 * sm(seg01(t, DROP + 2.45, DROP + 3.4)))
def flutter(t, i=0, f=9.0): return math.sin(t * f + i * 1.7) * 0.6 + math.sin(t * f * 1.9 + i * 0.6) * 0.4

# ======================= cast =======================
SKIN = (226, 178, 142)
HAIR = (92, 56, 30)
STEEL = (128, 134, 148)
KNIGHT = hd.spec(h=1.78, build=1.08, skin=SKIN, hair=HAIR, eye=(70, 120, 92),
                 tunic=STEEL, tunic2=(122, 130, 146), sleeves='long', skirt=0.22, pants=(70, 64, 60), boots=(56, 40, 30),
                 belt=(78, 50, 30), buckle=(214, 178, 84), collar=(168, 176, 190), gloves=(96, 66, 42))
LIP_COL = (196, 112, 104); MOUTH_IN = (58, 18, 24); TEETH = (236, 230, 214); TONGUE = (178, 78, 86)
BROW = (64, 38, 22); RED = (128, 28, 34); GOLD = (220, 182, 84); LEATHER = (82, 52, 30)

# ======================= the head (high density, face rig) =======================
RX, RY, RZ = 0.09, 0.116, 0.103
def base_def(p):
    x, y, z = p[..., 0].copy(), p[..., 1].copy(), p[..., 2].copy()
    ny = np.clip(-y / RY, 0, 1); neg = y < 0
    x = np.where(neg, x * (1 - 0.30 * ny ** 1.4), x)
    z = np.where(neg & (z > 0), z * (1 + 0.08 * ny), z)
    z = np.where(neg & (z <= 0), z * (1 - 0.25 * ny), z)
    z = np.where(z > 0, z * 0.93, z)
    x = np.where(y > 0.02, x * 1.02, x)
    # brow ridge + cheekbones: a touch of relief so the flat shading reads as a face
    br = np.exp(-((y - 0.03) / 0.012) ** 2) * np.exp(-(x / 0.06) ** 2) * (z > 0)
    ck = sum(np.exp(-(((x - s * 0.052) / 0.02) ** 2 + ((y + 0.012) / 0.016) ** 2)) for s in (1, -1)) * (z > 0)
    z = z + 0.004 * br + 0.004 * ck
    return np.stack([x, y, z], -1)
def expr_def(p, E):
    x, y, z = p[..., 0].copy(), p[..., 1].copy(), p[..., 2].copy()
    jaw = E.get('jaw', 0.0)
    if jaw:
        w = np.clip((-y - 0.058) / 0.022, 0, 1); w = w * w * (3 - 2 * w) * np.clip((z + 0.04) / 0.05, 0, 1)
        a = 0.2 * jaw * w; py, pz = y + 0.01, z + 0.02
        y = -0.01 + py * np.cos(a) - pz * np.sin(a); z = -0.02 + py * np.sin(a) + pz * np.cos(a)
    for sd, key in ((1, 'smR'), (-1, 'smL')):
        s_ = E.get(key, 0.0)
        if s_:
            g = np.exp(-(((x - sd * 0.046) / 0.02) ** 2 + ((y + 0.03) / 0.018) ** 2)) * s_ * (z > 0)
            z = z + 0.005 * g; y = y + 0.004 * g
    return np.stack([x, y, z], -1)
def sph(u, v): return np.stack([RX * np.sin(v) * np.sin(u), RY * np.cos(v), RZ * np.sin(v) * np.cos(u)], -1)
def surf(u, v, E): return expr_def(base_def(sph(u, v)), E)
def on_uv(u, v, lift, E):
    u = np.asarray(u, float); v = np.asarray(v, float); p = surf(u, v, E); e = 1e-3
    du = surf(u + e, v, E) - surf(u - e, v, E); dv = surf(u, v + e, E) - surf(u, v - e, E)
    n = np.cross(du, dv); n = n / (np.linalg.norm(n, axis=-1, keepdims=True) + 1e-12)
    n = np.where((n * p).sum(-1, keepdims=True) < 0, -n, n)
    return p + n * lift
def on(xy, lift, E):
    xy = np.asarray(xy, float).reshape(-1, 2); x, y = xy[:, 0], xy[:, 1]
    v = np.arccos(np.clip(y / RY, -0.995, 0.995)); u = np.arcsin(np.clip(x / (RX * np.sin(v)), -0.995, 0.995))
    return on_uv(u, v, lift, E)

class Mesh:
    """collects faces in head-local coordinates, then maps them to the world"""
    def __init__(self, hc, R): self.hc = np.asarray(hc, float); self.R = R; self.Q = []
    def W(self, p): return self.hc + np.asarray(p) @ self.R.T
    def tri(self, a, b, c, col, emit=False):
        q = hd.face([self.W(a), self.W(b), self.W(c)], col, emit=emit)
        if q: self.Q.append(q)
    def strip(self, top, bot, col, emit=False, colfn=None):
        """quads between two point rows (local), split into triangles (always convex)"""
        for j in range(len(top) - 1):
            c = colfn(j) if colfn else col
            self.tri(top[j], top[j + 1], bot[j + 1], c, emit); self.tri(top[j], bot[j + 1], bot[j], c, emit)
    def fan(self, c, ring, col, emit=False):
        for j in range(len(ring)): self.tri(c, ring[j], ring[(j + 1) % len(ring)], col, emit)

_HEADGRID = {}
def head_mesh(M, E, hair_on=True):
    nu, nv = 40, 28
    uu = np.linspace(0, 2 * PI, nu, endpoint=False); vv = np.linspace(0, PI, nv + 1)
    U, Vv = np.meshgrid(uu, vv); G = surf(U, Vv, E)
    sk = SKIN; skd = shade(sk, 0.9); stub = mixc(sk, (120, 86, 64), 0.22); blush = mixc(sk, (226, 130, 116), 0.12)
    hcW = M.hc
    for i in range(nv):
        for j in range(nu):
            k = (j + 1) % nu; pl = [G[i, j], G[i, k], G[i + 1, k], G[i + 1, j]]; cl = np.mean(pl, axis=0)
            x, y, z = cl
            col = sk
            if y < -0.06 and abs(x) > 0.04: col = skd
            if y < -0.044 and z > -0.01 and not (abs(x) < 0.03 and y > -0.08): col = stub      # light stubble along the jaw + chin
            if y < -0.088 and z > -0.02: col = stub
            if z > 0.03 and abs(abs(x) - 0.05) < 0.016 and -0.042 < y < -0.012: col = blush
            q = hd.face([M.W(p) for p in pl], col, inside=hcW)
            if q: M.Q.append(q)
    # ears
    for sd in (1, -1):
        ec = V((sd * RX * 0.96, -0.004, -0.006))
        for q in hd.ellip(M.W(ec), M.R, (0.012, 0.03, 0.019), 8, 5, shade(sk, 0.93)): M.Q.append(q)

def eyes_geo(M, E):
    for sd, side in ((1, 'R'), (-1, 'L')):
        cx, cy = sd * 0.033, 0.012
        op = E['eyes' + side]; sq = E['squint' + side]
        n = 9; s = np.linspace(-1, 1, n); hw = 0.0135
        x = cx + s * hw
        tilt = 0.0012 * s * sd                       # outer corner a touch higher
        up_full = cy + tilt + 0.0085 * (1 - s ** 2) ** 0.8 + 0.0006
        lo_full = cy + tilt - 0.0058 * (1 - s ** 2) ** 0.8
        lid = lo_full + 0.0006 + (up_full - lo_full) * np.clip(op, 0, 1.2) * (1 - 0.45 * sq)
        lid = np.maximum(lid, lo_full + 0.0004)
        llo = lo_full + (lid - lo_full) * 0.55 * sq
        llo = np.minimum(llo, lid - 0.0002)
        P2 = lambda xs, ys, lift: on(np.stack([xs, ys], -1), lift, E)
        # sclera
        M.strip(P2(x, up_full, 0.0012), P2(x, lo_full, 0.0012), (240, 236, 228))
        # iris + pupil + glint (kept inside the eye opening)
        lx, ly = E['look']; ix = cx + np.clip(lx, -1, 1) * 0.0032; iy = cy + 0.0006 + np.clip(ly, -1, 1) * 0.0022
        th = np.linspace(0, 2 * PI, 12, endpoint=False)
        def ring(r):
            xs = ix + np.cos(th) * r; ys = iy + np.sin(th) * r
            ss = np.clip((xs - cx) / hw, -0.97, 0.97)
            top = cy + 0.0012 * ss * sd + 0.0085 * (1 - ss ** 2) ** 0.8; bot = cy + 0.0012 * ss * sd - 0.0058 * (1 - ss ** 2) ** 0.8
            return np.stack([xs, np.clip(ys, bot, top)], -1)
        M.fan(on([[ix, iy]], 0.0018, E)[0], on(ring(0.0056), 0.0018, E), KNIGHT['eye'])
        M.fan(on([[ix, iy]], 0.0022, E)[0], on(ring(0.0035), 0.0022, E), shade(KNIGHT['eye'], 0.55))
        M.fan(on([[ix, iy]], 0.0026, E)[0], on(ring(0.0022), 0.0026, E), (16, 12, 12))
        g0 = on([[ix + 0.0016, iy + 0.0018]], 0.003, E)[0]
        M.fan(g0, on(np.stack([ix + 0.0016 + np.cos(th[::3]) * 0.0009, iy + 0.0018 + np.sin(th[::3]) * 0.0009], -1), 0.003, E), (255, 255, 250), emit=True)
        # upper lid (covers everything above the lid line) + lash line + crease
        lidcol = shade(SKIN, 0.9)
        M.strip(P2(x, up_full + 0.0034, 0.0034), P2(x, lid, 0.0034), lidcol)
        lash = np.where(s * sd > 0, 0.0017, 0.0011)
        M.strip(P2(x * 1.0 + sd * 0.0006 * (s * sd > 0.6), lid + lash, 0.0038), P2(x, lid - 0.0003, 0.0038), (34, 22, 18))
        M.strip(P2(x[1:-1], up_full[1:-1] + 0.0042, 0.0036), P2(x[1:-1], up_full[1:-1] + 0.0034, 0.0036), shade(SKIN, 0.78))
        # lower lid
        M.strip(P2(x, llo, 0.0032), P2(x, lo_full - 0.0026, 0.0032), shade(SKIN, 0.95))
        M.strip(P2(x, llo + 0.0004, 0.0034), P2(x, llo - 0.0004, 0.0034), shade(SKIN, 0.8))

def brows_geo(M, E):
    for sd, side in ((1, 'R'), (-1, 'L')):
        r = E['brow' + side]; inn = E['inner' + side]
        s = np.linspace(-1, 1, 7)                       # -1 = inner end, +1 = outer end
        x = sd * (0.033 + 0.017 * s)
        y = 0.0335 + 0.0068 * r + 0.0026 * (1 - s ** 2) + 0.0042 * inn * (1 - s) / 2 - 0.0012 * s
        th = 0.0048 - 0.0018 * (s + 1) / 2
        M.strip(on(np.stack([x, y + th * 0.55], -1), 0.0042, E), on(np.stack([x, y - th * 0.45], -1), 0.0042, E), BROW)
    # a little scar through the left brow (his left = screen right)
    a = on([[-0.045, 0.046], [-0.042, 0.047]], 0.0046, E); b = on([[-0.036, 0.024], [-0.0335, 0.0245]], 0.0046, E)
    M.tri(a[0], a[1], b[1], (214, 150, 136)); M.tri(a[0], b[1], b[0], (214, 150, 136))

def nose_geo(M, E):
    top = on([[0, 0.014]], -0.002, E)[0]; base = on([[0, -0.024]], -0.003, E)[0]
    fwd = V((0, -0.05, 1.0)); fwd = fwd / np.linalg.norm(fwd)
    tip = base + fwd * 0.021 + V((0, 0.003, 0)); und = base + fwd * 0.01 + V((0, -0.003, 0))
    wR = on([[0.0115, -0.022]], 0.002, E)[0]; wL = on([[-0.0115, -0.022]], 0.002, E)[0]
    mR = on([[0.007, -0.004]], 0.0, E)[0] + fwd * 0.012; mL = on([[-0.007, -0.004]], 0.0, E)[0] + fwd * 0.012
    c1 = shade(SKIN, 1.0); c2 = shade(SKIN, 0.93); c3 = shade(SKIN, 0.8)
    M.tri(top, mR, mL, c1); M.tri(mR, tip, mL, c1)
    M.tri(top, wR, mR, c2); M.tri(mR, wR, tip, c2); M.tri(top, mL, wL, shade(SKIN, 0.9)); M.tri(mL, tip, wL, shade(SKIN, 0.9))
    M.tri(wR, und, tip, c3); M.tri(wL, tip, und, c3)
    nR = und + (wR - und) * 0.45 + V((0, -0.0005, 0)); nL = und + (wL - und) * 0.45 + V((0, -0.0005, 0))
    M.tri(nR, und, wR, (90, 50, 44)); M.tri(nL, wL, und, (90, 50, 44))

def mouth_geo(M, E):
    op = E['open']; wd = E['wide']; smL, smR = E['smL'], E['smR']; tee = E.get('teeth', 0.0)
    n = 13; s = np.linspace(-1, 1, n)
    halfw = 0.0185 * (1 + 0.15 * wd) * (1 + 0.07 * (smL + smR)) * (1 - 0.12 * max(0.0, -wd) * op)
    ih = 0.0011 + 0.021 * op + 0.003 * tee
    cy = -0.051; shift = 0.0026 * (smR - smL)
    smv = np.where(s > 0, smR, smL)
    corner = 0.0085 * smv * np.abs(s) ** 1.5 - 0.0012 * np.abs(s) ** 2
    prof = (1 - s ** 2) ** (0.75 if wd >= 0 else 0.55)
    x = s * halfw + shift
    iu = cy + corner + ih * 0.32 * prof
    il = cy + corner - ih * 0.68 * prof
    sq = np.sqrt(np.clip(1 - s ** 2, 0, 1))
    ou = iu + (0.0042 + 0.0012 * (1 - np.abs(s))) * sq - 0.0011 * np.exp(-(s / 0.14) ** 2) * sq
    ol = il - 0.0072 * sq * (1 - 0.25 * op)
    P2 = lambda xs, ys, lift: on(np.stack([xs, ys], -1), lift, E)
    M.strip(P2(x, iu, 0.0012), P2(x, il, 0.0012), MOUTH_IN)
    if ih > 0.0035:
        tw = np.abs(s) < 0.78
        th_ = np.minimum(iu - il, 0.0042 + 0.003 * tee)
        M.strip(P2(x[tw], iu[tw] + 0.0002, 0.0016), P2(x[tw], iu[tw] - th_[tw], 0.0016), TEETH)
        if tee > 0.3:
            M.strip(P2(x[tw], il[tw] + np.minimum(iu - il, 0.003)[tw], 0.0016), P2(x[tw], il[tw] - 0.0002, 0.0016), shade(TEETH, 0.9))
    if op > 0.35:
        th = np.linspace(0, PI, 8); tc = cy - ih * 0.5
        tx = np.cos(th) * halfw * 0.55 + shift; ty = il[n // 2] + 0.0004 + np.sin(th) * min(ih * 0.3, 0.0055)
        M.strip(P2(tx, ty, 0.0018), P2(tx, np.full_like(ty, il[n // 2] + 0.0003), 0.0018), TONGUE)
    lipd = shade(LIP_COL, 0.86)
    M.strip(P2(x, ou, 0.0022), P2(x, iu, 0.0022), lipd)
    M.strip(P2(x, il, 0.0022), P2(x, ol, 0.0022), LIP_COL)
    # corner creases when smiling (cheek lines)
    for sd, v_ in ((1, smR), (-1, smL)):
        if v_ > 0.25:
            ex = x[-1] if sd > 0 else x[0]; ey = (iu[-1] if sd > 0 else iu[0])
            a = on([[ex + sd * 0.004, ey + 0.004 * v_], [ex + sd * 0.0052, ey + 0.004 * v_]], 0.002, E)
            b = on([[ex + sd * 0.0015, ey - 0.006 * v_], [ex + sd * 0.0027, ey - 0.006 * v_]], 0.002, E)
            M.tri(a[0], a[1], b[1], shade(SKIN, 0.82)); M.tri(a[0], b[1], b[0], shade(SKIN, 0.82))

# ---- hair: scalp shell + wind-driven locks
LOCKS = []
for i in range(44):
    a = -PI * 0.95 + 1.9 * PI * hsh(i, 3)                   # azimuth (0 = front)
    if i < 11: a = -0.8 + 1.6 * i / 10                        # fringe locks across the front
    el = 0.12 + 0.75 * hsh(i, 5) if i >= 11 else 0.45         # polar angle from the top
    ln = (0.062 + 0.02 * hsh(i, 7)) if i < 11 else (0.05 + 0.03 * hsh(i, 9))
    LOCKS.append((a, el, ln, hsh(i, 11)))
def scalp_pt(a, el, r=1.04):
    return V((RX * r * 1.02 * math.sin(el) * math.sin(a), RY * r * math.cos(el), RZ * r * math.sin(el) * math.cos(a)))
def push_out(p, r=1.07):
    q = V((p[0] / (RX * 1.02), p[1] / RY, p[2] / RZ)); d = np.linalg.norm(q)
    return p * (r / d) if d < r else p
def hair_geo(M, E, t, rim_local):
    """rim_local(az) -> y of the helmet rim over this azimuth in head-local coordinates (None = no helmet)"""
    hc_ = HAIR; hd_ = shade(HAIR, 0.8)
    def keep(c):
        x, y, z = c
        if z > 0.03: return y > 0.064 - 0.012 * abs(x) / RX * 3
        if z > -0.01: return y > 0.035
        return y > -0.075
    for q in hd.ellip(M.hc, M.R, (RX * 1.07, RY * 1.05, RZ * 1.07), 18, 12, hc_, deform=lambda p: base_def(p[None])[0], keep=keep,
                      colfn=lambda i, j, cl: hd_ if j % 3 == 0 else hc_, closed=False):
        M.Q.append(q)
    w = wind(t); wdir = V((0, 0.42, -1.0)); wdir = wdir / np.linalg.norm(wdir)
    for i, (a, el, ln, rr) in enumerate(LOCKS):
        root = scalp_pt(a, el, 1.02)
        free = 1.0
        if rim_local is not None:
            free = float(np.clip((rim_local(a) - root[1] - 0.035) / 0.05, 0, 1))
        # rest direction: fringe falls forward-down over the brow, the rest combs down/back along the head
        out = root / np.linalg.norm(root)
        if i < 11: rest = V((0.25 * math.sin(a) - 0.35, -0.5, 0.8))
        else: rest = V((math.sin(a) * 0.35 - 0.15, -0.8, math.cos(a) * 0.3 - 0.25)) + out * 0.08
        rest = rest / np.linalg.norm(rest)
        flat = rest - out * float(rest @ out); flat = flat / (np.linalg.norm(flat) + 1e-9)
        d0 = flat * (1 - free) + rest * free
        L_ = ln * (0.55 + 0.45 * free); pts = [root]; d = d0.copy()
        for sgi in range(3):
            ww = min(0.95, w * free * (0.65 + 0.2 * sgi) * (0.9 + 0.3 * rr))
            fl = flutter(t, i * 3 + sgi, 26 + 6 * rr) * 0.55 * w * free
            wl = V((math.sin(a) * 0.6, 0.18 + 0.15 * rr, -0.85)); wl = wl / np.linalg.norm(wl)
            dd = d * (1 - ww) + wl * ww + V((fl * 0.6, fl * 0.3, 0)) + V((0, -0.08 * (1 - w) * free, 0))
            dd = dd / np.linalg.norm(dd); p = pts[-1] + dd * L_ / 3
            p = push_out(p, 1.06 if free < 1 else 1.08); pts.append(p); d = dd
        wid = (0.04 if i < 11 else 0.05) * (0.9 + 0.3 * rr)
        for sgi in range(3):
            for q in hd.limb(M.W(pts[sgi]), M.W(pts[sgi + 1]), wid * (1 - 0.2 * sgi) / 2, wid * (1 - 0.2 * (sgi + 1)) / 2 + 0.003,
                             hd_ if (i + sgi) % 2 else hc_, n=5, m=1, flat=0.35, ref=M.R @ out):
                M.Q.append(q)

# ======================= helmet (nasal helm + chin strap) =======================
def rim_y(az): return -0.052 + 0.11 * (0.5 + 0.5 * math.cos(az)) ** 1.4      # front rim high (above the brows), back low
def helmet_geo(hc, R, t, snapped, strap_u):
    """helmet in its own frame (origin = head centre when worn). strap_u: 0 = buckled, 1 = both halves hanging free"""
    M = Mesh(hc, R); nu, nv = 28, 9
    pts = []
    for i in range(nv + 1):
        row = []
        for j in range(nu):
            az = 2 * PI * j / nu; vr = math.acos(max(-1, min(1, rim_y(az) / (RY * 1.13))))
            v = vr * i / nv
            x = RX * 1.33 * math.sin(v) * math.sin(az); y = RY * 1.13 * math.cos(v) + 0.012 * (1 - i / nv) * 0; z = RZ * 1.3 * math.sin(v) * math.cos(az)
            if i == 0: y += 0.02
            row.append(V((x, y + 0.012, z)))
        pts.append(row)
    st = STEEL; st2 = shade(STEEL, 1.12); dark = (74, 72, 78)
    for i in range(nv):
        for j in range(nu):
            k = (j + 1) % nu; pl = [pts[i][j], pts[i][k], pts[i + 1][k], pts[i + 1][j]]
            col = st2 if j % 7 == 0 else st
            q = hd.face([M.W(p) for p in pl], col, inside=M.W(V((0, 0.0, 0))))
            if q: M.Q.append(q)
    # inside (dark lining): reversed shell slightly smaller, only visible when it tips
    for i in range(3, nv):
        for j in range(nu):
            k = (j + 1) % nu; pl = [pts[i][j] * 0.97, pts[i + 1][j] * 0.97, pts[i + 1][k] * 0.97, pts[i][k] * 0.97]
            wp = [M.W(p) for p in pl]; q = quad(wp, dark); c = M.W(V((0, 0.0, 0)))
            if not np.isfinite(q['n']).all() or np.linalg.norm(q['n']) < 0.5: continue
            if float(q['n'] @ (q['c'] - c)) > 0: q = quad(wp[::-1], dark)      # normal points inward: seen from inside only
            q['wind'] = 1.0; M.Q.append(q)
    # brass rim band + vertical bands with rivets
    rim = [pts[nv][j] for j in range(nu)] + [pts[nv][0]]
    rim2 = [p + V((0, 0.014, 0)) * 1.0 for p in rim]
    for j in range(nu):
        a, b = rim[j] * 1.015, rim[j + 1] * 1.015; c_, d_ = rim2[j + 1] * 1.015, rim2[j] * 1.015
        q = hd.face([M.W(a), M.W(b), M.W(c_), M.W(d_)], GOLD if j % 2 else shade(GOLD, 0.9), inside=M.W(V((0, 0, 0))))
        if q: M.Q.append(q)
    for j in (0, 7, 14, 21):
        for i in range(nv):
            a = pts[i][j] * 1.02; b = pts[i + 1][j] * 1.02
            for q in hd.limb(M.W(a), M.W(b), 0.006, 0.006, shade(GOLD, 0.85), n=4, m=1): M.Q.append(q)
    # nose guard
    ng_top = pts[nv][0] * 1.02 + V((0, 0.012, 0)); ng_bot = V((0, -0.028, RZ * 1.32))
    for q in hd.bx(M.W((ng_top + ng_bot) / 2), R @ hd.Rx(math.atan2(ng_top[2] - ng_bot[2], ng_top[1] - ng_bot[1])), (0.0065, float(np.linalg.norm(ng_top - ng_bot)) / 2, 0.004), shade(STEEL, 0.85)):
        M.Q.append(q)
    for q in hd.ellip(M.W(V((0, RY * 1.13 + 0.03, 0))), R, (0.012, 0.012, 0.012), 6, 4, GOLD): M.Q.append(q)     # top knob
    # chin strap: two halves from the sides; buckled under the chin, or hanging free (+ the wind) after the snap
    E0 = dict(jaw=0.0)
    ts = np.linspace(0, 1, 7)
    for sd in (1, -1):
        att = V((sd * RX * 1.3, -0.006, 0.0))
        # buckled path on the jaw (head-local; valid while worn)
        uu = sd * (1.5 - 1.25 * ts); vv = 1.62 + 1.12 * ts
        worn = on_uv(uu, vv, 0.0075, E0)
        worn[0] = att
        wv = wind(t)
        free = []
        for k_, s_ in enumerate(ts):
            L_ = 0.16 * s_
            d = V((sd * 0.55, -0.75, -0.35 * wv)) + V((0, 0.5 * wv, -0.6 * wv)); d = d / np.linalg.norm(d)
            fl = flutter(t, k_ + (5 if sd > 0 else 0), 30) * 0.02 * s_ * wv
            free.append(att + d * L_ + V((sd * 0.03 * math.sin(PI * s_), fl, fl)))
        free = np.array(free)
        u = strap_u
        mid = worn + V((sd * 0.07, 0, 0.02)) * np.sin(PI * min(1, u * 1.0))[None] * ts[:, None]
        path = worn * (1 - u) + free * u + (mid - worn) * (1 - abs(2 * u - 1)) * (u < 1)
        top = path + V((0, 0.006, 0)); bot = path - V((0, 0.006, 0))
        M.strip(top, bot, LEATHER)
        M.strip(bot, top, shade(LEATHER, 0.8))
        if sd < 0:
            bpos = path[4]
            for q in hd.bx(M.W(bpos), R, (0.008, 0.008, 0.003), GOLD): M.Q.append(q)
    return M.Q

# ======================= the knight (body + custom head) =======================
def head_tilt(t):
    """(yaw, nod, tilt) of the head over time"""
    yaw = 0.0; nod = 0.0; tilt = 0.0
    # build: still, breathing
    nod += 0.008 * math.sin(t * 2.1)
    # gust hit: head pushed back a touch
    w = wind(t); nod += 0.07 * w * (1 - sm(seg01(t, DROP + 0.5, DROP + 1.2))) + 0.02 * flutter(t, 1, 14) * w * 0.3
    # after the reveal: confident head moves on the beat (small)
    if t > DROP + 0.7:
        k = sm(seg01(t, DROP + 0.7, DROP + 1.1))
        for b in beats_between(DROP + 0.5, DUR + 1):
            nod -= 0.028 * k * bump(t, b + 0.03, 0.07)
        tilt += k * (0.07 * math.sin(2 * PI * (t - DROP) / (4 * BP) + 0.6))
        yaw += k * 0.05 * math.sin(2 * PI * (t - DROP) / (8 * BP))
    # the final pose: chin up a touch, head tilt, and the glance to the clank
    fk = sm(seg01(t, FINAL - 0.05, FINAL + 0.15))
    nod = lerp(nod, 0.05, fk); tilt = lerp(tilt, -0.08, fk); yaw = lerp(yaw, 0.03, fk)
    return yaw, nod, tilt

def expression(t):
    E = dict(eyesR=1.0, eyesL=1.0, squintR=0.12, squintL=0.12, browR=0.0, browL=0.0, innerR=0.0, innerL=0.0, look=(0.0, 0.0),
             open=0.0, wide=0.0, smL=0.0, smR=0.0, teeth=0.0, jaw=0.0)
    # build: calm, slightly serious
    E.update(browR=-0.2, browL=-0.2, innerR=-0.35, innerL=-0.35, smR=0.0, smL=0.0, eyesR=0.82, eyesL=0.82, squintR=0.22, squintL=0.22)
    w = wind(t)
    # gust: squint into the wind
    g = w * (1 - sm(seg01(t, DROP + 0.55, DROP + 0.95)))
    E['squintR'] = E['squintL'] = 0.22 + 0.65 * g; E['eyesR'] = E['eyesL'] = 0.82 - 0.1 * g
    E['innerR'] = E['innerL'] = -0.25 - 0.4 * g; E['browR'] = E['browL'] = -0.15 - 0.3 * g
    # reveal -> cocky: one brow up, smirk
    c = sm(seg01(t, DROP + 0.6, DROP + 0.95))
    if c > 0:
        E['browR'] = lerp(E['browR'], 0.75, c); E['innerR'] = lerp(E['innerR'], 0.1, c)
        E['browL'] = lerp(E['browL'], -0.05, c); E['innerL'] = lerp(E['innerL'], -0.1, c)
        E['smR'] = lerp(E['smR'], 0.8, c); E['smL'] = lerp(E['smL'], 0.15, c)
        E['squintR'] = lerp(E['squintR'], 0.1, c); E['squintL'] = lerp(E['squintL'], 0.38, c)    # a little squint on one eye
        E['eyesR'] = lerp(E['eyesR'], 1.0, c); E['eyesL'] = lerp(E['eyesL'], 0.95, c)
    # singing
    if t > VOX - 0.2:
        k = sm(seg01(t, VOX - 0.2, VOX + 0.1))
        op = lip_at(t, 'open'); wd = lip_at(t, 'wide'); sb = lip_at(t, 'sib'); ac = acc_env(t)
        E['open'] = op * k; E['wide'] = wd * k; E['teeth'] = sb * (1 - op) * k; E['jaw'] = op * 0.9 * k
        E['smR'] = lerp(E['smR'], 0.38 + 0.25 * (1 - op), k); E['smL'] = lerp(E['smL'], 0.1 + 0.1 * (1 - op), k)
        E['browR'] = lerp(E['browR'], 0.25 + 0.55 * ac, k); E['browL'] = lerp(E['browL'], 0.1 + 0.5 * ac, k)
        E['innerR'] = lerp(E['innerR'], 0.15 * ac, k); E['innerL'] = lerp(E['innerL'], 0.25 * ac, k)
        E['squintR'] = lerp(E['squintR'], 0.15 + 0.25 * op, k); E['squintL'] = lerp(E['squintL'], 0.3 + 0.2 * op, k)
    # the eyebrow flash in the phrase gap
    if T_GAP:
        f = math.exp(-((t - (T_GAP + 0.12)) / 0.16) ** 2)
        E['browR'] += 0.6 * f; E['browL'] += 0.55 * f; E['smR'] += 0.3 * f
    # final beat: confident look, then the glance to the clank and back
    fk = sm(seg01(t, FINAL - 0.06, FINAL + 0.12))
    if fk > 0:
        op = E['open'] * (1 - sm(seg01(t, FINAL + 0.05, FINAL + 0.2)))
        E.update(open=op, jaw=op * 0.9, teeth=0.0)
        E['smR'] = lerp(E['smR'], 0.9, fk); E['smL'] = lerp(E['smL'], 0.22, fk)
        E['browR'] = lerp(E['browR'], 0.8, fk); E['browL'] = lerp(E['browL'], 0.0, fk)
        E['squintL'] = lerp(E['squintL'], 0.45, fk); E['squintR'] = lerp(E['squintR'], 0.18, fk)
        gl = sm(seg01(t, T_CLANK + 0.04, T_CLANK + 0.12)) * (1 - sm(seg01(t, T_CLANK + 0.3, T_CLANK + 0.4)))
        E['look'] = (-0.95 * gl, 0.15 * gl)
        E['browL'] += 0.35 * gl
    # blinks
    for b in BLINKS:
        if b is None: continue
        bl = max(0.0, 1 - abs(t - b) / 0.07)
        E['eyesR'] = min(E['eyesR'], 1 - bl); E['eyesL'] = min(E['eyesL'], 1 - bl)
    return E

def pose(t):
    y_, n_, ti = head_tilt(t)
    w = wind(t)
    bounce = 0.0
    if t > DROP + 0.7:
        for b in beats_between(DROP + 0.5, DUR + 1): bounce += 0.006 * bump(t, b + 0.04, 0.08)
    P = dict(base=(0, 0, 0), yaw=0.0, head=(y_, n_, ti), lean=-0.04 * w + 0.01 * math.sin(t * 2.1) - 0.02 * sm(seg01(t, FINAL - 0.1, FINAL + 0.15)),
             pel=(0, -bounce + 0.003 * math.sin(t * 2.1), 0), rgrip=0.7, lgrip=0.7)
    return P

_REST = {}
def head_frame(t):
    """head centre + rotation at time t (runs the body solver without drawing the head)"""
    key = round(t, 4)
    if key in _REST: return _REST[key]
    P = pose(t); P['E'] = expression(t); P['_skip_head'] = True
    hd.human(KNIGHT, P)
    _REST[key] = (P['_head'].copy(), P['_RH'].copy()); return _REST[key]

def my_head(hc, RH, S_, P, k):
    if P.get('_skip_head'): return []
    E = P['E']; M = Mesh(hc, RH)
    head_mesh(M, E); eyes_geo(M, E); brows_geo(M, E); nose_geo(M, E); mouth_geo(M, E)
    hair_geo(M, E, P['_t'], P.get('_rim'))
    return M.Q
hd.head = my_head          # the HD body calls hd.head(); this clip swaps in the face-rig head

def helmet_state(t):
    """-> (centre, rotation, strap_u, rim_local fn for the hair)"""
    hc, R = head_frame(t)
    if t < T_SNAP:
        return hc, R, 0.0, (lambda az: rim_y(az))
    h0, R0 = head_frame(T_SNAP)
    u = t - T_SNAP
    lift = 0.34 * sm(seg01(t, *T_LIFT))
    up = R0 @ V((0, 1.0, 0))
    after = max(0.0, t - T_LIFT[1])
    pos = h0 + up * lift + up * (0.5 * after + 0.55 * after * after) + V((0, 0, -1.0)) * (0.06 * sm(seg01(t, T_LIFT[0], T_LIFT[1])) + 1.6 * after + 1.2 * after * after)
    spin = -0.15 * sm(seg01(t, *T_LIFT)) - (2 * PI) * (1.15 * after + 0.25 * after * after)
    roll = 0.25 * math.sin(after * 6) * min(1, after * 3)
    R_ = R0 @ hd.Rx(spin) @ hd.Rz(roll)
    su = sm(seg01(t, T_SNAP, T_SNAP + 0.12))
    # the rim relative to the (still) head, for the hair: helmet lift measured along the head's up axis
    hc_now, R_now = head_frame(t)
    dy = float((pos - hc_now) @ (R_now @ V((0, 1.0, 0))))
    return pos, R_, su, (lambda az: rim_y(az) + dy)

# ======================= cape, particles, set =======================
def cape_geo(P, t):
    chest = P['_chest']; RW = P['_RW']; w = wind(t)
    rows, cols = 8, 9; ln = 1.0; Q = []
    G = np.zeros((rows + 1, cols, 3))
    for j in range(cols):
        s_ = j / (cols - 1) * 2 - 1
        top = chest + RW @ V((s_ * 0.2, 0.1 - 0.02 * abs(s_), -0.115 - 0.01 * (1 - s_ * s_)))
        p = top.copy(); G[0, j] = p
        for i in range(1, rows + 1):
            v = i / rows
            th = w * (1.2 + 0.4 * v) + 0.06 + 0.18 * w * flutter(t, j + i * 0.5, 16 + 4 * v) * v
            th += 0.05 * math.sin(t * 1.3 + j) * (1 - w)
            d = RW @ V((s_ * (0.12 + 0.55 * w) * 0.5, -math.cos(th), -math.sin(th)))
            ripple = 0.05 * w * v * math.sin(10 * v - t * 22 + j * 0.9)
            d = d / np.linalg.norm(d)
            p = p + d * (ln / rows) + RW @ V((0, ripple, ripple * 0.5))
            G[i, j] = p
    out_c = RED; in_c = (96, 18, 24)
    neck = chest + RW @ V((0, 0.1, 0.0))
    for i in range(rows):
        for j in range(cols - 1):
            pl = [G[i, j], G[i, j + 1], G[i + 1, j + 1], G[i + 1, j]]
            q = quad(pl, out_c if (j % 2) else shade(out_c, 0.88))
            outer = float(q['n'] @ (q['c'] - neck)) > 0
            q1 = q if outer else quad(pl[::-1], q['col']); q1['wind'] = 1.0; Q.append(q1)
            q2 = quad(q1['p'][::-1], in_c); q2['wind'] = 1.0; Q.append(q2)
    # gold edge trim
    for j in range(cols - 1):
        for q in hd.limb(G[rows, j], G[rows, j + 1], 0.008, 0.008, GOLD, n=4, m=1): Q.append(q)
    return Q

def armour_geo(P):
    chest = P['_chest']; RW = P['_RW']; Q = []
    for sd in (1, -1):                       # pauldrons: three overlapping lames
        for k, (dy, r) in enumerate(((0.07, 1.0), (0.035, 0.94), (0.0, 0.88))):
            c = chest + RW @ V((sd * 0.2, dy + 0.02, -0.005))
            Q += hd.ellip(c, RW @ hd.Rz(-sd * 0.35), (0.1 * r, 0.07 * r, 0.11 * r), 12, 4, shade(STEEL, 1.08 - 0.06 * k), v1=PI * 0.5,
                          colfn=lambda i, j, cl: GOLD if i == 3 and k == 0 else None or shade(STEEL, 1.08 - 0.06 * k))
    # tabard: red front panel with gold trim + fox badge
    cs = []; us = []; vs = []; rs = []
    for s_ in np.linspace(0, 1, 5):
        c = chest + RW @ V((0, -0.32 + 0.38 * s_, 0.0)); cs.append(c); us.append(RW @ V((1.0, 0, 0))); vs.append(RW @ V((0, 0, 1.0)))
        rs.append(((0.178 - 0.02 * (1 - s_)) * 1.08 + 0.012, (0.11 - 0.01 * (1 - s_)) * 1.08 + 0.012))
    Q += hd.loft(cs, us, vs, rs, 8, RED, th0=PI / 2 - 0.62, th1=PI / 2 + 0.62, cap0=False, cap1=False, closed=False,
                 colfn=lambda i, j: GOLD if j in (0, 7) else RED)
    bc = chest + RW @ V((0, 0.0, 0.11 * 1.08 + 0.014)); n = RW @ V((0, 0, 1.0)); up = RW @ V((0, 1.0, 0))
    Q += hd.poly_decal(bc, n, up, [(-0.035, 0.02), (0.035, 0.02), (0.0, -0.04)], GOLD, lift=0.002)                 # fox face
    Q += hd.poly_decal(bc, n, up, [(-0.035, 0.02), (-0.03, 0.05), (-0.012, 0.02)], GOLD, lift=0.002)              # ears
    Q += hd.poly_decal(bc, n, up, [(0.012, 0.02), (0.03, 0.05), (0.035, 0.02)], GOLD, lift=0.002)
    Q += hd.poly_decal(bc, n, up, [(-0.004, -0.03), (0.004, -0.03), (0.0, -0.04)], (60, 30, 20), lift=0.003)      # nose
    for sd in (1, -1): Q += hd.poly_decal(bc + RW @ V((sd * 0.014, 0.004, 0)), n, up, [(-0.005, 0.0), (0.005, 0.002), (0.0, -0.003)], (60, 30, 20), lift=0.003)
    return Q

PARTS = []
for i in range(46):
    leaf = i % 3 != 0
    t0 = DROP - 0.05 + (hsh(i, 21) ** 1.6) * 1.9
    side = -1 if i % 2 else 1
    if hsh(i, 23) < 0.25: x0 = (hsh(i, 25) * 2 - 1) * 0.5; y0 = 1.98 + 0.3 * hsh(i, 27)
    else: x0 = side * (0.3 + 0.55 * hsh(i, 25)); y0 = 1.15 + 1.0 * hsh(i, 27)
    PARTS.append(dict(t0=t0, x=x0, y=y0, vz=-(3.5 + 2.5 * hsh(i, 29)), vx=side * 0.25 * hsh(i, 31), vy=0.2 * (hsh(i, 33) - 0.3),
                      sz=(0.03 + 0.025 * hsh(i, 35)) if leaf else 0.008, leaf=leaf,
                      col=[(196, 112, 40), (170, 70, 30), (214, 160, 60), (130, 120, 60)][i % 4] if leaf else (236, 226, 200), spin=6 + 10 * hsh(i, 37)))
def particles(t, camz):
    Q = []
    for i, p in enumerate(PARTS):
        u = t - p['t0']
        if u < 0: continue
        z = camz - 0.12 + p['vz'] * u
        if z < -2.3: continue
        x = p['x'] + p['vx'] * u * (1 + 0.5 * math.sin(u * 5 + i)); y = p['y'] + p['vy'] * u + 0.03 * math.sin(u * 9 + i)
        c = V((x, y, z)); a = p['spin'] * u + i
        R = hd.Ry(a) @ hd.Rx(a * 0.7)
        s_ = p['sz']
        if p['leaf']:
            pts = [c + R @ V((-s_, 0, 0)), c + R @ V((0, 0, s_ * 0.6)), c + R @ V((s_, 0, 0)), c + R @ V((0, 0, -s_ * 0.6))]
            q = hd.face(pts, p['col'])
        else:
            q = hd.face([c + V((-s_, -s_, 0)), c + V((s_, -s_, 0)), c + V((s_, s_, 0)), c + V((-s_, s_, 0))], p['col'], emit=True)
        if q: Q.append(q)
    return Q

WALLZ = -2.6
def build_wall():
    Q = []
    bw, bh = 0.5, 0.27
    Q.append(hd.face([(-4, -1, WALLZ - 0.02), (4, -1, WALLZ - 0.02), (4, 3.3, WALLZ - 0.02), (-4, 3.3, WALLZ - 0.02)], (52, 48, 56)))
    for r in range(int(4.3 / bh) + 1):
        y0 = -1 + r * bh; off = (r % 2) * bw / 2
        for c in range(-9, 9):
            x0 = c * bw + off; g = 0.85 + 0.25 * hsh(r * 31 + c, 41)
            col = shade(mixc((112, 104, 112), (124, 112, 100), hsh(r * 7 + c, 43)), g)
            if y0 > 3.0: continue
            Q.append(hd.face([(x0 + 0.012, y0 + 0.012, WALLZ), (x0 + bw - 0.012, y0 + 0.012, WALLZ), (x0 + bw - 0.012, min(3.0, y0 + bh) - 0.012, WALLZ), (x0 + 0.012, min(3.0, y0 + bh) - 0.012, WALLZ)], col))
    for c in range(-6, 7):                               # merlons
        x0 = c * 0.7
        Q += hd.bx(V((x0, 3.3, WALLZ + 0.1)), np.eye(3), (0.2, 0.3, 0.14), (104, 96, 106))
    Q.append(hd.face([(-4, 3.0, WALLZ + 0.25), (4, 3.0, WALLZ + 0.25), (4, 3.02, WALLZ - 0.02), (-4, 3.02, WALLZ - 0.02)], (90, 84, 94)))
    # dusk sky behind the battlement
    sky = [(60, 50, 96), (120, 80, 120), (196, 120, 110), (232, 164, 110)]
    for i in range(len(sky) - 1):
        y0 = 7.5 - i * 1.4; y1 = y0 - 1.4
        for j in range(6):
            x0 = -12 + j * 4
            q = hd.face([(x0, y1, -14), (x0 + 4, y1, -14), (x0 + 4, y0, -14), (x0, y0, -14)], mixc(sky[i + 1], sky[i], 0.5 + 0.1 * (j % 2)), emit=True)
            if q: Q.append(q)
    return [q for q in Q if q]
WALL = build_wall()
TORCH = [V((-0.95, 1.92, WALLZ + 0.12)), V((0.95, 1.92, WALLZ + 0.12))]
def torches(t):
    Q = []; w = wind(t)
    for i, p in enumerate(TORCH):
        Q += hd.limb(p + V((0, -0.3, -0.06)), p, 0.03, 0.035, (90, 60, 36), n=6, m=1)
        Q += hd.bx(p + V((0, -0.22, -0.1)), np.eye(3), (0.03, 0.06, 0.04), (60, 56, 60))
        fl = flutter(t, i * 4, 13); h = 0.16 * (1 + 0.15 * fl + 0.5 * w * (1 - sm(seg01(t, DROP + 0.2, DROP + 1.2))))
        bend = V((0.06 * fl * (1 + 2 * w) + (0.05 if i else -0.05) * w, 0, -0.12 * w))
        tip = p + V((0, h, 0)) + bend
        for k, (col, sc) in enumerate((((255, 140, 40), 1.0), ((255, 210, 90), 0.6), ((255, 248, 210), 0.3))):
            base = p + V((0, 0.02 + 0.01 * k, 0.01 * k)); r = 0.05 * sc
            for a in range(6):
                a0 = 2 * PI * a / 6; a1 = 2 * PI * (a + 1) / 6
                q = hd.face([base + V((math.cos(a0) * r, 0, math.sin(a0) * r)), base + V((math.cos(a1) * r, 0, math.sin(a1) * r)), base + (tip - p) * (0.6 + 0.4 * sc) + V((0, 0, 0.02 * k))], col, emit=True)
                if q: Q.append(q)
    return Q

# ======================= camera, lights, frame =======================
HC0, _ = head_frame(0.0)
def camera(t):
    push = sm(seg01(t, 0, DUR)) * 0.03
    sh = 0.0035 * w_shake(t)
    pos = V((0.0 + sh, HC0[1] + 0.02 + sh * 0.6, HC0[2] + 0.52 - push))
    tgt = V((0.0, HC0[1] - 0.045, HC0[2]))
    return pos, tgt, 40.0
def w_shake(t):
    if not (DROP - 0.02 < t < DROP + 0.35): return 0.0
    u = t - DROP; return math.sin(u * 70) * math.exp(-u * 9)

def lights(t):
    w = wind(t); f0 = 1 + 0.08 * flutter(t, 2, 15); f1 = 1 + 0.08 * flutter(t, 7, 17)
    flare = 1 + 0.3 * w * (1 - sm(seg01(t, DROP + 0.2, DROP + 1.0)))
    warm = sm(seg01(t, DROP - 0.02, DROP + 0.25))
    key = mixc((232, 230, 240), (255, 236, 214), warm)
    return [((-0.85, HC0[1] + 0.5, 0.75), key, 0.74),
            ((0.8, HC0[1] - 0.1, 0.7), (150, 170, 224), 0.2 - 0.05 * warm),
            ((TORCH[0][0] + 0.15, TORCH[0][1] + 0.2, WALLZ + 0.35), (255, 150, 70), 0.5 * f0 * flare),
            ((TORCH[1][0] - 0.15, TORCH[1][1] + 0.2, WALLZ + 0.35), (255, 150, 70), 0.5 * f1 * flare)]

def scene(t):
    P = pose(t); P['E'] = expression(t); P['_t'] = t
    hpos, hR, su, rimf = helmet_state(t)
    helmet_on = (hpos is not None) and t < T_GONE + 0.3
    P['_rim'] = rimf if (t < T_LIFT[1] + 0.2) else None
    body = hd.human(KNIGHT, P)
    extra = armour_geo(P) + cape_geo(P, t)
    hel = helmet_geo(hpos, hR, t, t >= T_SNAP, su) if helmet_on else []
    return P, body + extra, hel

def render_low(t):
    pos, tgt, fov = camera(t); cam = Camera.look(tuple(pos), tuple(tgt))
    P, char, hel = scene(t)
    layers = [WALL, torches(t), char + hel, particles(t, pos[2])]
    R = Renderer(W, H, fog=(70, 56, 92))
    img, vi, zb = zrender(R, cam, layers, lights(t), fov=fov, fog_start=5, fog_end=30, ambient=0.17, return_z=True)
    a = look.outline(np.asarray(img).astype(np.float32), zb)
    # grade: cool before the drop, warmer + punchier after, a 2-frame lift on the hit
    warm = sm(seg01(t, DROP - 0.02, DROP + 0.25))
    a = a * np.array([1.0 + 0.03 * warm, 1.0, 1.0 - 0.04 * warm])
    a = (a - 112) * (1.08 + 0.05 * warm) + 112
    if DROP - 0.01 <= t < DROP + 0.07: a = a * 1.1 + 6
    return np.clip(a, 0, 255)

def frame_final(t):
    img = Image.fromarray(render_low(t).astype(np.uint8))
    img = post.ps1(img, levels=7)
    return post.upscale(img, S)

def frame(t): return Image.fromarray(np.clip(frame_final(t), 0, 255).astype(np.uint8)).resize((270, 480), Image.BOX)

# ======================= QA manifest =======================
QA = dict(fps=FPS, dur=DUR, W=W, frame=frame, chars={}, geom=lambda t, name, st, V_: [], camera=lambda t: camera(t)[0], min_cam_dist=0.3,
          camera_ok=lambda p: True, allow_jump=[], weapon_events=[],
          scenes=[dict(id='build', t0=0.0, t1=DROP, action='tight front shot, helmet on, calm serious look into the lens'),
                  dict(id='gust', t0=DROP, t1=VOX, action='gust from the camera, strap snaps, helmet lifts + spins back out of frame, smirk'),
                  dict(id='sing', t0=VOX, t1=FINAL, action='lip-sync to the song, brow flash in the gap'),
                  dict(id='button', t0=FINAL, t1=DUR, action='final beat: confident look, off-screen clank, glance, back to camera')],
          texts=lambda: [])

TEST = os.environ.get('TEST')
if TEST and __name__ == '__main__':
    print(f'drop {DROP_SRC:.3f}s (src)  beat {BP:.4f}s = {60 / BP:.1f} bpm  vox {VOX_SRC:.3f}s  start {SRC0:.3f}  final {FINAL:.3f} (video)  dur {DUR}  gap {T_GAP}')
    ts = [float(x) for x in TEST.split(',')] if TEST not in ('all', 'info') else [round(x, 2) for x in np.arange(0, DUR, float(os.environ.get('STEP', '1.0')))]
    if TEST == 'info': sys.exit()
    crop = os.environ.get('CROP')
    ims = []
    for x in ts:
        im = Image.fromarray(np.clip(frame_final(x), 0, 255).astype(np.uint8))
        if crop: im = im.crop((270, 250, 810, 1210))
        ims.append(im.resize((270, 480) if not crop else (360, 640), Image.LANCZOS))
    cw, ch_ = ims[0].size
    per = int(os.environ.get('PER', '8')); rows = (len(ims) + per - 1) // per; shp = Image.new('RGB', (min(per, len(ims)) * (cw + 2), rows * (ch_ + 18)), (30, 30, 30))
    dd = ImageDraw.Draw(shp)
    for i, (im, x) in enumerate(zip(ims, ts)): shp.paste(im, ((i % per) * (cw + 2), (i // per) * (ch_ + 18))); dd.text(((i % per) * (cw + 2) + 4, (i // per) * (ch_ + 18) + ch_ + 3), f'{x:.2f}', fill=(255, 255, 0))
    shp.save(os.environ.get('TEST_OUT', os.path.join(ROOT, 'test_fw.png'))); print('test written'); sys.exit()

# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as sf
    from nightkit.audio import Sound
    sr = 48000
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{SRC0:.4f}', '-t', f'{DUR + 0.5:.4f}', '-i', SONG, '-ac', '2', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    song = np.frombuffer(raw, np.float32).astype(np.float64).reshape(-1, 2)
    n = int(round(DUR * sr)); song = np.pad(song, ((0, max(0, n - len(song))), (0, 0)))[:n]
    t = np.arange(n) / sr
    env = np.clip(t / 0.012, 0, 1) * (1 - np.clip((t - (FINAL + 0.14)) / 0.34, 0, 1))
    song = song * env[:, None]
    s = Sound(DUR, sr=sr, loop=False, seed=7); fx = np.zeros((n, 2))
    def put(x, t0, v=1.0, pan=0.0):
        i = int(round(t0 * sr)); j = min(n, i + len(x))
        if i >= n: return
        fx[i:j, 0] += x[:j - i] * v * (1 - max(0, pan)); fx[i:j, 1] += x[:j - i] * v * (1 + min(0, pan))
    # wind: band noise that follows the gust envelope
    we = np.array([wind(x) for x in t[::480]]); we = np.interp(t, t[::480], we)
    gust = s.filt(np.random.default_rng(3).normal(0, 1, n), lo=250, hi=2600) * 0.9 + s.filt(np.random.default_rng(4).normal(0, 1, n), lo=60, hi=300) * 0.7
    whoosh = gust * we * (0.75 + 0.25 * np.sin(2 * np.pi * 3.1 * t) * np.sin(2 * np.pi * 0.7 * t))
    fx[:, 0] += whoosh * 0.11; fx[:, 1] += np.roll(whoosh, 400) * 0.11
    # strap snap
    tt = s.T(0.06); put(s.filt_short(s.noise(0.06, 11), lo=1500, hi=9000) * np.exp(-tt * 90), T_SNAP, 0.25, -0.2)
    tt = s.T(0.25); put(np.sin(2 * np.pi * 2400 * tt) * np.exp(-tt * 30) * 0.4 + np.sin(2 * np.pi * 3700 * tt) * np.exp(-tt * 40) * 0.3, T_SNAP + 0.005, 0.08, -0.2)
    # off-screen helmet clank (+ one small bounce): inharmonic metal partials, a touch muffled, panned
    def clank(t0, v):
        tt = s.T(0.7); x = sum(a * np.sin(2 * np.pi * f * tt) * np.exp(-tt * d) for f, a, d in ((523, 1.0, 7), (1347, 0.7, 9), (2210, 0.45, 12), (3105, 0.3, 16), (812, 0.5, 8)))
        x = x + s.filt_short(s.noise(0.7, int(t0 * 100)), lo=800, hi=6000) * np.exp(-tt * 60) * 0.8
        put(s.filt_short(x, lo=120, hi=5200), t0, v, 0.45)
    clank(T_CLANK, 0.22); clank(T_CLANK + 0.16, 0.08)
    out = song + fx
    pk = np.abs(out).max(); out = out / pk * 0.9
    sf.write(path, out.astype(np.float32), sr); return path, round(DUR, 3)

if __name__ == '__main__' and os.environ.get('PART') == 'audio':
    print(build_audio(os.path.join(OUT, 'fox_wind.wav'))); sys.exit()
if __name__ == '__main__' and os.environ.get('PART'):
    a, b = map(int, os.environ['PART'].split(':'))
    p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W * S}x{H * S}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', os.path.join(OUT, f'fw_{a:05d}.mp4')], stdin=subprocess.PIPE)
    vhs = post.VHS(W * S, H * S, S, grade='none', chroma=0, scan_dark=1.0, vignette=0.22, grain=0.9, band_period=1e9)
    for f in range(a, min(b, N)): p.stdin.write(vhs(frame_final(f / FPS), f, f / FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done', a, b); sys.exit()
