"""THE LAST ECHO (Insert Disc 2, 24 Nov 2026) ~60 s, 9:16, nightkit HD figures (no speed-up: the brief wants a restrained ~58 s cut).
Brief: briefs/the_last_echo.md (pasted by Enes 24 Nov; approved plan: no story additions, identical knocks, passage visible before the choice,
warm memory / cold present, loop: last frame = the candle in Aren's hand like frame 0, short fade).
Voices: tools/tts/le.py (draft AI; Enes + Betul record later: briefs/the_last_echo_voice_sheet.md).

  TEST=0,5,10 python examples/the_last_echo.py      -> test_le.png contact sheet
  ASSET=lineup|set python examples/the_last_echo.py -> test_le_<asset>.png"""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera
from nightkit.zraster import zrender
from nightkit import post, look, hd, motion
from nightkit.audio import Sound, duck_envelope

W, H, S = 270, 480, 4
PI = math.pi
FPS = 24
V = np.array
OUT = 'out'; os.makedirs(OUT, exist_ok=True)
TTS_DIR = os.environ.get('TTS_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tts'))
sm = motion.smooth
def seg01(t, a, b): return max(0.0, min(1.0, (t - a) / (b - a))) if b > a else (1.0 if t >= b else 0.0)
def win(t, a, b, r=0.25): return sm(seg01(t, a, a + r)) * (1 - sm(seg01(t, b - r, b)))
def lerp(a, b, u): return a + (b - a) * u
def lerp3(a, b, u): return tuple(a[i] + (b[i] - a[i]) * u for i in range(len(a)))
def hsh(i, s=0): v = math.sin(i * 127.1 + s * 311.7) * 43758.5453; return v - math.floor(v)
def ang_to(p, q): return math.atan2(q[0] - p[0], q[2] - p[2])
def wrap(a): return (a + PI) % (2 * PI) - PI
def angl(a, b, u): return a + wrap(b - a) * u
def mixc(a, b, u): return tuple(int(round(x + (y - x) * max(0.0, min(1.0, u)))) for x, y in zip(a, b))
def nz2(x, z): l = math.hypot(x, z); return (x / l, z / l)

# ======================= cast =======================
AREN = hd.spec(h=1.82, build=1.04, skin=(212, 168, 134), hair=(58, 42, 32), hair_style='messy', beard=(74, 54, 40), eye=(70, 100, 130),
               tunic=(78, 80, 88), tunic2=(62, 64, 72), skirt=0.26, pants=(58, 54, 52), boots=(52, 38, 28), belt=(60, 40, 26),
               cloak=(44, 80, 156), cloak_len=1.0, collar=(70, 96, 160))
YOUNG = hd.spec(h=1.76, build=0.94, skin=(220, 176, 140), hair=(62, 44, 32), hair_style='messy', eye=(70, 100, 130),
                tunic=(86, 88, 96), tunic2=(70, 72, 80), skirt=0.24, pants=(64, 58, 54), boots=(56, 40, 30), belt=(60, 40, 26),
                cloak=(50, 88, 166), cloak_len=0.9, collar=(70, 96, 160))
BRO = hd.spec(h=1.8, build=1.0, skin=(222, 178, 142), hair=(126, 86, 50), hair_style='messy', eye=(80, 110, 130),
              tunic=(150, 112, 70), tunic2=(124, 92, 58), skirt=0.24, pants=(84, 68, 52), boots=(64, 46, 32), belt=(70, 46, 28))
CHILD = hd.spec(h=1.16, build=0.86, skin=(230, 186, 150), hair=(80, 56, 38), hair_style='messy', eye=(70, 100, 140),
                tunic=(170, 92, 70), tunic2=(140, 74, 56), skirt=0.18, pants=(96, 80, 64), boots=(80, 58, 40), belt=(90, 60, 40))
MOTHER = hd.spec(h=1.66, build=0.92, fem=1.0, skin=(228, 186, 156), hair=(64, 44, 34), hair_style='long', eye=(80, 100, 70),
                 tunic=(120, 96, 120), tunic2=(96, 76, 98), skirt=0.6, pants=(96, 76, 98), boots=(80, 60, 44), belt=(90, 64, 50),
                 cloak=(110, 104, 92), cloak_len=0.8)
SURV1 = hd.spec(h=1.7, build=1.0, skin=(196, 160, 130), hair=(160, 156, 150), hair_style='short', beard=(170, 164, 156), eye=(70, 70, 70),
                tunic=(96, 88, 76), tunic2=(80, 72, 62), pants=(70, 62, 54), boots=(56, 44, 34))
SURV2 = hd.spec(h=1.6, build=0.9, fem=1.0, skin=(214, 172, 140), hair=(90, 60, 40), hair_style='bun', eye=(80, 76, 60),
                tunic=(110, 100, 84), tunic2=(90, 82, 70), skirt=0.5, pants=(90, 82, 70), boots=(70, 54, 40))
CAST = dict(aren=AREN, young=YOUNG, bro=BRO, child=CHILD, mother=MOTHER)

# ======================= layout (top view, metres) =======================
TC = V((0.0, 0.0, 6.0)); R_IN, R_OUT = 2.4, 2.9
PHI_DOOR = 2.75; PHI_PASS = -2.45
def ring_pt(phi, r, y=0.0): return V((TC[0] + r * math.sin(phi), y, TC[2] + r * math.cos(phi)))
DOOR_OUT = ring_pt(PHI_DOOR, R_OUT); DOOR_DIR = V((math.sin(PHI_DOOR), 0, math.cos(PHI_DOOR)))
PASS_OUT = ring_pt(PHI_PASS, R_OUT); PASS_IN = ring_pt(PHI_PASS, R_IN); OUTD = V((math.sin(PHI_PASS), 0, math.cos(PHI_PASS)))   # outward
PERP = V((OUTD[2], 0, -OUTD[0]))
MOUND = DOOR_OUT + DOOR_DIR * 0.25
CRV = MOUND + DOOR_DIR * 0.74 + V((0, 0.3, 0))                     # the crevice in the rubble where the child's hand knocks
A0 = V((0.3, 0.0, 0.55))                                            # Aren, start (faces the camera, the tower behind him)
GHOST = V((-0.42, 0.0, 1.8))
CROUCH = PASS_OUT + OUTD * 0.62 + PERP * 0.42                         # where he kneels at the passage
C_ST = PASS_OUT + OUTD * 0.95 - PERP * 0.05                           # the child, out
M0 = V((-0.7, 0.0, 1.4))                                            # the mother, waiting (right of frame in the wide)
HUG = C_ST + (M0 - C_ST) / np.linalg.norm(M0 - C_ST) * 0.21
A_HOME = CROUCH + PERP * 0.35 + OUTD * 0.25                           # after standing up he steps back from the child
# memory (inside the tower, years before): passage -> young Aren -> beam -> brother on one line
DIRM = -OUTD
YA = PASS_IN + DIRM * 1.35; BR = PASS_IN + DIRM * 3.15; BEAM_C = PASS_IN + DIRM * 2.35
PERPM = V((DIRM[2], 0, -DIRM[0]))
MEMC = BEAM_C + DIRM * 0.38 - PERPM * 0.55 + V((0, 0.62, 0))            # the memory's candle stub on the rubble
SLAB = BR - DIRM * 0.38 + PERPM * 0.2 + V((0, 0.42, 0))                  # the stone he knocks on

# ======================= voice timings =======================
SCR = json.load(open(os.path.join(TTS_DIR, 'le', 'script.json')))
def D_(k): return SCR['dur'][k]
def sent(k, i): return SCR['sent'][k][i]
T0 = {}
KN = 0.42                                                            # spacing of the three knocks (identical every time)
T_K1 = 0.30
T0['01'] = 1.45
def tend(k): return T0[k] + D_(k)
def ws(k, i): return T0[k] + sent(k, i)[0]
def we(k, i): return T0[k] + sent(k, i)[1]
T_LIGHT = tend('01') - 0.3
T0['02'] = T_LIGHT + 0.5
T_GHOST = (T0['02'] + 0.9, T0['02'] + 2.3)
T0['03'] = tend('02') + 0.3
T_TURN = (T0['03'] - 0.2, T0['03'] + 0.8)
T_REACH = (ws('03', 1) - 0.2, ws('03', 1) + 1.2)
T0['04'] = tend('03') + 0.3
T_MEM = tend('04') + 0.4                                             # match-cut (dissolve centre)
T_MK = T_MEM + 0.75                                                  # the brother's three knocks
T_POINT = T_MK + 2 * KN + 0.35
T_SHAKE = (T_POINT + 0.95, T_POINT + 2.0)
T0['05'] = T_POINT + 1.0
T0['06'] = tend('05') + 0.3
T_NOW = tend('06') + 0.3
T_CK = T_NOW + 0.55                                                  # the child's three knocks
T0['07'] = T_CK + 2 * KN + 0.75
T_STEP = (ws('07', 1) - 0.1, ws('07', 1) + 0.9)
T_FALL = ws('07', 1) + 0.6
T_FLASH = (ws('07', 2) - 0.45, ws('07', 2) + 0.45)
T_TURNP = T_FLASH[1] + 0.05
T_PASS = tend('07') - 0.3                                            # cut: at the passage
T_ARRIVE = T_PASS + 0.45
T_KNEEL = (T_ARRIVE - 0.1, T_ARRIVE + 0.35)
T_CLR = [(T_KNEEL[1] + 0.05 + 0.46 * i, T_KNEEL[1] + 0.05 + 0.46 * (i + 1)) for i in range(3)]
T_IN = (T_CLR[2][1] + 0.05, T_CLR[2][1] + 0.6)
T_TAKE = T_IN[1] + 0.3
T_PULL = (T_TAKE + 0.3, T_TAKE + 1.5)
T_HOME = T_PULL[1] + 0.1
T_RUN = (T_HOME + 0.1, T_HOME + 1.35)
T_HUG = T_RUN[1]
T0['08'] = T_HUG + 0.15
T_OUT = tend('08') + 0.5                                             # the candle goes out
T_LOOKB = (T_OUT + 0.55, T_OUT + 1.25)
T_LOWER = (T_OUT + 1.9, T_OUT + 2.5)
T0['09'] = T_OUT + 2.75
T0['10'] = tend('09') + 0.4
T_WALK = tend('10') + 0.75
T0['11'] = T_WALK + 0.35
T_ENDCU = ws('11', 1) - 0.25
DUR = round(tend('11') + 1.15, 2); N = int(round(DUR * FPS))
T_FADE = DUR - 0.85
LINES = [(k, T0[k]) for k in sorted(T0)]

def scene(t):
    if t < T_MEM: return 'cost'
    if t < T_NOW: return 'mem'
    if T_FLASH[0] <= t < T_FLASH[1]: return 'flash'
    if t < T_HOME: return 'choice'
    if t < T_WALK: return 'home'
    return 'walk'
def talking(t, key, rate=7.3):
    if key not in T0: return None
    for a, b, _ in SCR['sent'][key]:
        if T0[key] + a <= t < T0[key] + b: return 'open' if (t * rate + 0.2 * math.sin(t * 13)) % 1.0 < 0.55 else 'soft'
    return None

# ======================= set pieces =======================
def rock(c, r, col=(96, 92, 88), seed=0, flat=0.6, R=None):
    def d(p): k = 1 + 0.2 * math.sin(p[0] * 31 + seed) * math.cos(p[2] * 23 + seed * 2); return p * k
    return hd.ellip(c, hd.Ry(seed) if R is None else R, (r, r * flat, r * 0.9), 8, 5, col, deform=d, colfn=lambda i, j, cl: hd.shade(col, 0.82 + 0.25 * hsh(i * 13 + j, seed)))
def ground(x0, x1, z0, z1, step, cols, seed=0, y=0.0):
    Q = []; xs = np.arange(x0, x1 + 1e-6, step); zs = np.arange(z0, z1 + 1e-6, step)
    for i in range(len(xs) - 1):
        for j in range(len(zs) - 1):
            a, b, c, d = xs[i], xs[i + 1], zs[j], zs[j + 1]; h = hsh(i * 31 + j * 7, seed)
            col = hd.shade(cols[int(h * len(cols)) % len(cols)], 0.9 + 0.2 * hsh(i * 3 + j * 17, seed + 1))
            q = hd.face([(a, y, c), (a, y, d), (b, y, d), (b, y, c)], col)
            if q: Q.append(q)
    return Q
def tree_dead(x, z, h, col=(52, 46, 42), seed=0):
    Q = hd.limb((x, 0, z), (x + 0.1, h, z), 0.12, 0.05, col, n=7, m=2)
    for i in range(4):
        y = h * (0.45 + 0.13 * i); a = hsh(seed, i) * 2 * PI; L = 0.9 - 0.15 * i
        Q += hd.limb((x + 0.05, y, z), (x + L * math.sin(a), y + 0.5 * L, z + L * math.cos(a)), 0.04, 0.012, col, n=5, m=1)
    return Q
ST = [(118, 116, 112), (104, 104, 102), (128, 124, 118), (96, 96, 96)]
def tower_set():
    Q = []
    nseg = 40; dph = 2 * PI / nseg; ch = 0.32
    for i in range(nseg):
        phi0 = i * dph
        top = 3.3 + 2.6 * (0.5 + 0.5 * math.cos(phi0)) + 0.9 * (hsh(i, 2) - 0.5)
        if abs(wrap(phi0 - 1.1)) < 0.5: top -= 1.6 * (1 - abs(wrap(phi0 - 1.1)) / 0.5)          # a collapsed bite on the right
        for j in range(int(top / ch)):
            y = j * ch; ph = phi0 + (dph / 2 if j % 2 else 0)
            if abs(wrap(ph - PHI_DOOR)) < 0.2 and y < 2.0: continue
            if abs(wrap(ph - PHI_PASS)) < 0.13 and y < 0.74: continue
            rm = (R_IN + R_OUT) / 2; c = ring_pt(ph, rm, y + ch / 2)
            col = hd.shade(ST[(i * 3 + j) % 4], 0.84 + 0.24 * hsh(i * 17 + j, 5))
            if y > top - ch * 1.5 and hsh(i, j) < 0.35: continue                                    # ragged top
            Q += hd.bx(c, hd.Ry(ph), (rm * dph / 2 - 0.012, ch / 2 - 0.01, (R_OUT - R_IN) / 2), col)
    # door: lintel (cracked) + dark inside; the mound of rubble in front of it
    for s in (-1, 1):
        c = ring_pt(PHI_DOOR + s * 0.1, R_OUT - 0.22, 2.14 + 0.04 * (s < 0))
        Q += hd.bx(c, hd.Ry(PHI_DOOR) @ hd.Rz(0.06 * s), (0.31, 0.12, 0.26), (110, 104, 96))
    Q += [hd.face([ring_pt(PHI_DOOR - 0.2, R_OUT - 0.3, 0) + V((0, y_, 0)) for y_ in (0,)] + [ring_pt(PHI_DOOR - 0.2, R_OUT - 0.3, 2.0), ring_pt(PHI_DOOR + 0.2, R_OUT - 0.3, 2.0), ring_pt(PHI_DOOR + 0.2, R_OUT - 0.3, 0)], (8, 8, 12))]
    # passage: lintel + dark recess (seen from outside and inside)
    Q += hd.bx(ring_pt(PHI_PASS, (R_IN + R_OUT) / 2, 0.83), hd.Ry(PHI_PASS), (0.42, 0.09, 0.27), (100, 96, 90))
    Q += [hd.face([ring_pt(PHI_PASS - 0.13, 2.66, 0.0), ring_pt(PHI_PASS - 0.13, 2.66, 0.74), ring_pt(PHI_PASS + 0.13, 2.66, 0.74), ring_pt(PHI_PASS + 0.13, 2.66, 0.0)], (4, 4, 6), emit=True)]
    for s in (-1, 1):                                                                              # side walls of the passage
        Q += [hd.face([ring_pt(PHI_PASS + s * 0.13, R_OUT, 0), ring_pt(PHI_PASS + s * 0.13, R_OUT, 0.74), ring_pt(PHI_PASS + s * 0.13, 2.66, 0.74), ring_pt(PHI_PASS + s * 0.13, 2.66, 0)], (40, 40, 44))]
    # floor inside (flagstones)
    for i in range(-6, 6):
        for j in range(-6, 6):
            x, z = TC[0] + i * 0.42, TC[2] + j * 0.42
            if math.hypot(x + 0.21 - TC[0], z + 0.21 - TC[2]) > R_IN + 0.1: continue
            Q.append(hd.face([(x + 0.01, 0.004, z + 0.01), (x + 0.01, 0.004, z + 0.41), (x + 0.41, 0.004, z + 0.41), (x + 0.41, 0.004, z + 0.01)], hd.shade(ST[(i + j) % 4], 0.6 + 0.2 * hsh(i * 7 + j, 9))))
    return [q for q in Q if q]
def outside_set():
    Q = ground(-12, 12, -14, 16, 0.8, [(58, 62, 52), (52, 56, 48), (64, 64, 54), (48, 50, 46)], seed=3)
    Q += hd.ellip(MOUND, hd.Ry(PHI_DOOR), (1.15, 0.98, 0.82), 12, 6, (92, 88, 84), colfn=lambda i, j, cl: hd.shade((96, 92, 86), 0.8 + 0.3 * hsh(i * 5 + j, 2)))
    for i in range(14):                                                                            # rocks on the mound
        a = hsh(i, 4) * PI - PI / 2; rr = 0.5 + 0.4 * hsh(i, 5)
        c = MOUND + hd.Ry(PHI_DOOR) @ V((rr * math.sin(a) * 1.1, 0, rr * math.cos(a) * 0.6)) + V((0, 0.98 * math.sqrt(max(0.05, 1 - rr * rr)), 0))
        if np.linalg.norm(c - CRV) < 0.3: continue
        Q += rock(c, 0.13 + 0.1 * hsh(i, 6), seed=i + 3)
    Q += [hd.face([CRV + hd.Ry(PHI_DOOR) @ V((x_, y_, 0.02)) for x_, y_ in ((-0.13, -0.07), (-0.1, 0.08), (0.12, 0.07), (0.14, -0.06))], (6, 6, 8), emit=True)]   # the crevice
    Q += rock(CRV + DOOR_DIR * 0.12 + V((0.0, -0.2, 0)), 0.12, (120, 116, 110), seed=31, flat=0.5)                 # the stone the child taps
    Q += rock(PASS_OUT + OUTD * 0.15 - PERP * 0.55, 0.22, seed=40) + rock(PASS_OUT + OUTD * 0.2 + PERP * 0.62, 0.2, seed=41)
    for i in range(18):                                                                            # scattered fallen blocks
        a = hsh(i, 7) * 2 * PI; r = 3.3 + 2.5 * hsh(i, 8); c = TC + V((r * math.sin(a), 0.1, r * math.cos(a)))
        if np.linalg.norm((c - PASS_OUT)[[0, 2]]) < 1.6 or np.linalg.norm((c - A0)[[0, 2]]) < 1.5 or np.linalg.norm((c - CROUCH)[[0, 2]]) < 1.2: continue
        if np.linalg.norm((c - M0)[[0, 2]]) < 1.0 or np.linalg.norm((c - HUG)[[0, 2]]) < 1.2: continue
        Q += hd.bx(c, hd.Ry(a) @ hd.Rz(0.2 * hsh(i, 9)), (0.22, 0.12, 0.17), ST[i % 4])
    Q += tree_dead(-5.5, 7.0, 3.4, seed=2) + tree_dead(5.2, 9.0, 3.0, seed=5)
    for i in range(7): x = -36 + 12 * i; Q += hd.ellip((x, -3, 40), np.eye(3), (10, 7 + 3 * hsh(i, 2), 3), 10, 5, (36, 42, 52))
    for i in range(6): x = -30 + 12 * i; Q += hd.ellip((x, -3, -42), np.eye(3), (10, 6 + 3 * hsh(i, 3), 3), 10, 5, (44, 46, 58))
    return [q for q in Q if q]
def memory_set():
    """inside, years before: the fallen beam, rubble on the brother's side, dust"""
    Q = []
    a = BEAM_C - PERPM * 1.5 + V((0, 0.12, 0)); b = BEAM_C + PERPM * 1.4 + V((0, 0.95, 0))
    Q += hd.limb(a, b, 0.13, 0.12, (92, 62, 40), n=8, m=3)
    Q += hd.limb(BEAM_C + PERPM * 1.3 + V((0, 0.9, 0)), BEAM_C + PERPM * 1.2 + DIRM * 0.6 + V((0, 3.2, 0)), 0.09, 0.08, (84, 56, 36), n=7, m=2)   # a second beam, still leaning
    for i in range(16):
        u = hsh(i, 3) * 2.4 - 1.2; v = hsh(i, 4) * 0.9
        c = BEAM_C + PERPM * u + DIRM * (0.2 + v) + V((0, 0.12 + 0.35 * (1 - abs(u) / 1.2) * hsh(i, 5), 0))
        if np.linalg.norm((c - BR)[[0, 2]]) < 0.45: continue
        Q += rock(c, 0.12 + 0.12 * hsh(i, 6), seed=i + 50)
    Q += hd.bx(SLAB - V((0, 0.2, 0)), hd.Ry(ang_to(BR, PASS_IN)), (0.22, 0.2, 0.16), (122, 118, 110))
    Q += hd.bx(MEMC - V((0, 0.08, 0)), np.eye(3), (0.12, 0.08, 0.12), (110, 106, 100))
    return [q for q in Q if q]
_SETS = {}
def get_set(name):
    if name not in _SETS: _SETS[name] = {'tower': tower_set, 'out': outside_set, 'mem': memory_set}[name]()
    return _SETS[name]

# ======================= candle =======================
def candle(base, lit=1.0, t=0.0, burnt=False, smoke=0.0, seed=0):
    """small candle on a brass dish: base = bottom centre. Returns faces, flame point"""
    base = V(base, float); Q = []
    Q += hd.lathe(base, np.eye(3), [(0.045, 0.0), (0.05, 0.008), (0.046, 0.014)], 10, (176, 140, 70))
    Q += hd.lathe(base + V((0, 0.012, 0)), np.eye(3), [(0.021, 0.0), (0.021, 0.075), (0.016, 0.085)], 9, (226, 214, 190))
    wk = base + V((0, 0.097, 0)); Q += hd.limb(base + V((0, 0.082, 0)), wk, 0.003, 0.003, (30, 24, 20), n=4, m=1)
    fp = wk + V((0, 0.03, 0))
    if lit > 0.02:
        k = lit * (0.85 + 0.15 * math.sin(t * 17 + seed) + 0.08 * math.sin(t * 41)); sw = 0.006 * math.sin(t * 9 + seed)
        for ang in (0.0, PI / 2):
            dx, dz = 0.012 * k * math.cos(ang), 0.012 * k * math.sin(ang)
            Q.append(hd.face([wk + V((-dx, 0.004, -dz)), wk + V((0, -0.002, 0)), wk + V((dx, 0.004, dz)), wk + V((sw, 0.055 * k, 0))], (255, 170, 70), emit=True))
            Q.append(hd.face([wk + V((-dx * 0.5, 0.006, -dz * 0.5)), wk + V((dx * 0.5, 0.006, dz * 0.5)), wk + V((sw * 0.6, 0.032 * k, 0))], (255, 238, 180), emit=True))
    if smoke > 0.01:
        for i in range(7):
            u = ((t * 0.5 + i / 7) % 1.0); y = 0.01 + 0.35 * u; s = 0.003 + 0.006 * u
            c = wk + V((0.02 * math.sin(i * 2 + t * 3) * u + 0.04 * u, y, 0.015 * math.cos(i + t * 2) * u))
            if u < smoke * 0.8: Q.append(hd.face([c + V((-s, 0, 0)), c + V((0, s * 1.6, 0)), c + V((s, 0, 0)), c + V((0, -s, 0))], mixc((110, 110, 116), (70, 72, 80), u)))
    return [q for q in Q if q], fp

def hold_base(P, key='l'): return P['_' + key + 'wrist'] + P['_' + key + 'dir'] * 0.075 + P['_' + key + 'palm'] * 0.028
def wpt(P, l): return V(P['base'], float) + hd.Ry(P['yaw']) @ V(l, float)
def loc(base, yaw, p): return tuple(hd.Ry(yaw).T @ (V(p, float) - V(base, float)))
def head_to(P, tgt, k=1.0):
    """head yaw towards a world point (relative to the body yaw), clamped"""
    a = wrap(ang_to(P['base'], tgt) - P['yaw']); return max(-1.1, min(1.1, a)) * k
def kneel(P, front='r', drop=0.43):
    b = 'l' if front == 'r' else 'r'; s = 1 if front == 'r' else -1
    P.update(crouch=drop); P[front + 'f'] = (s * 0.14, 0.07, 0.33); P[b + 'f'] = (-s * 0.13, 0.06, -0.52); P[b + 'kpole'] = (0, -0.8, 1.0)
    P[b + 'fdir'] = None; return P

# ======================= Aren =======================
HOLD = (-0.07, 1.2, 0.3)                                    # where the candle hand rests (local)
def candle_state(t):
    """lit amount, smoke"""
    if t < T_LIGHT + 0.15: return 0.0, 0.0
    if t < T_OUT - 0.5: return min(1.0, seg01(t, T_LIGHT + 0.15, T_LIGHT + 0.5) * 1.0), 0.0
    if t < T_OUT:
        u = seg01(t, T_OUT - 0.5, T_OUT); return (1 - u * 0.5) * (0.6 + 0.4 * abs(math.sin(t * 23))) if u < 0.98 else 0.0, 0.0
    return 0.0, max(0.0, 1.0 - seg01(t, T_OUT + 0.1, T_OUT + 3.5))
def aren_present(t):
    """cost (before the memory) + choice + home + walk"""
    P = dict(base=tuple(A0), yaw=PI, eyes='open', mouth='neutral', brow=-0.3, lean=0.03, cape_sway=0.15 * math.sin(t * 1.3))
    P['lh'] = HOLD; P['lgrip'] = 0.55; P['lpalm'] = (0.0, 1.0, 0.15)
    if t < T_MEM:
        fr = win(t, T_K1 + 0.12, T_LIGHT - 0.6, 0.3)                              # freezes, looks back at the tower
        P['head'] = (0.95 * fr, -0.05 * fr, 0.0); P['twist'] = 0.25 * fr
        if T_K1 + 0.1 < t < T_K1 + 1.3: P['eyes'] = 'wide'; P['brow'] = 0.1
        lt = win(t, T_LIGHT - 0.45, T_LIGHT + 0.6, 0.25)                         # strikes the flint at the wick
        if lt > 0:
            P['rh'] = lerp3((0.2, 0.9, 0.1), (0.03, 1.13, 0.34), lt); P['rgrip'] = 0.85; P['rpalm'] = (-1.0, 0.0, 0.2); P['nod'] = 0.35 * lt
        if T_LIGHT - 0.45 < t < T_GHOST[0]: P['nod'] = max(P.get('nod', 0.0), 0.3); P['eyes'] = 'half' if t > T_LIGHT + 0.2 else 'open'
        if t >= T_LIGHT + 0.2: P['brow'] = -0.5; P['mouth'] = 'soft'
        tu = sm(seg01(t, *T_TURN))                                                # senses him, turns round to face him
        if tu > 0:
            P['yaw'] = angl(PI, ang_to(A0, GHOST), tu); P['nod'] = lerp(0.3, 0.0, tu); P['eyes'] = 'wide' if tu < 1 else 'open'; P['brow'] = -0.6
        rc = sm(seg01(t, *T_REACH)) * (1 - sm(seg01(t, T_MEM - 0.6, T_MEM + 0.2)))   # reaches - and stops short
        if rc > 0:
            stop = 0.55 + 0.05 * (1 - seg01(t, T_REACH[1] - 0.4, T_REACH[1]))
            P['rh'] = lerp3((0.2, 0.9, 0.1), (0.07, 1.3, stop), rc); P['rgrip'] = lerp(0.3, 0.15, rc); P['rpalm'] = (-0.2, 0.0, 1.0)
            if t > T_REACH[1] - 0.3: P['rgrip'] = 0.35 * seg01(t, T_REACH[1] - 0.3, T_REACH[1] + 0.4)
        if t >= T0['04'] - 0.1: P['eyes'] = 'sad'; P['brow'] = -0.8; P['mouth'] = 'o' if t < tend('04') + 0.2 else 'soft'
        return P
    # ---------------- choice
    yaw0 = ang_to(A0, GHOST); P['yaw'] = yaw0; P['brow'] = -0.5
    if t < T_STEP[0]:
        lk_d = sm(seg01(t, T_CK + 0.05, T_CK + 0.4)); lk_p = win(t, T0['07'] + 0.3, T_STEP[0] - 0.05, 0.35)
        P['head'] = (lerp(head_to(P, CRV) * lk_d, head_to(P, PASS_OUT), lk_p), 0.1 * lk_d, 0.0)
        if T_CK <= t < T_CK + 1.2: P['eyes'] = 'wide'; P['brow'] = 0.15
        return P
    stp = seg01(t, *T_STEP); dstep = V(CRV[[0, 1, 2]]) * V((1, 0, 1)) - A0; dstep = dstep / np.linalg.norm(dstep)
    A1 = A0 + dstep * 0.75
    if t < T_TURNP:                                                              # nearly goes for the doorway; a stone falls; stops
        ys = ang_to(A0, CRV); P['yaw'] = angl(yaw0, ys, sm(seg01(t, T_STEP[0], T_STEP[0] + 0.3)))
        P['base'] = lerp3(A0, A1, sm(stp)); P['walk'] = sm(stp) * 6.0; P['stride'] = 0.28; P['lean'] = 0.08
        if t >= T_FALL:
            r = win(t, T_FALL, T_TURNP + 0.2, 0.15); P['lean'] = -0.1 * r; P['eyes'] = 'wide'; P['brow'] = 0.2; P['walk'] = None; P['base'] = tuple(A1)
            P['head'] = (0.0, -0.12 * r, 0.0)
        return P
    # turns to the passage, walks there, kneels, clears the stones, reaches in, takes the child's hand
    path_u = seg01(t, T_TURNP + 0.15, T_ARRIVE); us = sm(path_u) * 0.6 + path_u * 0.4
    P['yaw'] = angl(ang_to(A0, CRV), ang_to(A1, CROUCH), sm(seg01(t, T_TURNP, T_TURNP + 0.35)))
    P['base'] = lerp3(A1, CROUCH, us); P['walk'] = us * 18.0; P['stride'] = 0.34; P['lean'] = 0.1; P['brow'] = -0.2
    if t >= T_ARRIVE - 0.2:
        P['walk'] = None; P['yaw'] = angl(P['yaw'], ang_to(CROUCH, PASS_OUT), sm(seg01(t, T_ARRIVE - 0.2, T_ARRIVE + 0.2)))
    if t >= T_KNEEL[0]:
        kneel(P, 'l', 0.43 * sm(seg01(t, *T_KNEEL))); P['lean'] = 0.28
        P['lh'] = (-0.2, 0.62, 0.25); P['lpalm'] = (0.0, 1.0, 0.2)                    # candle held low, lighting the passage
    return P
def stones(t):
    """the three loose stones in front of the passage: (centre, radius) per stone, and which one is in the hand"""
    S0 = [PASS_OUT + OUTD * 0.14 - PERP * 0.12 + V((0, 0.13, 0)), PASS_OUT + OUTD * 0.16 + PERP * 0.14 + V((0, 0.12, 0)), PASS_OUT + OUTD * 0.12 + V((0, 0.36, 0))]
    order = [2, 0, 1]; out = []
    for k, i in enumerate(order):
        a, b = T_CLR[k]; g = seg01(t, a + 0.18, b - 0.05)
        dst = CROUCH + PERP * (0.5 + 0.12 * k) + OUTD * 0.2 + V((0, 0.1, 0))
        if g <= 0: c = S0[i]
        else:
            u = sm(g); c = lerp3(S0[i], dst, u); c = V(c) + V((0, 0.25 * math.sin(PI * u), 0))
        out.append((i, V(c), 0.12 if i != 2 else 0.1, a, b))
    return out
def aren_hands_choice(P, t):
    """right hand: the stones, the reach into the passage, the child's hand"""
    if t < T_CLR[0][0]: return None
    for i, c, r, a, b in stones(t):
        if a <= t < b:
            g = seg01(t, a, a + 0.18); rest = wpt(P, (0.22, 0.75, 0.25))
            P['rh_w'] = tuple(lerp3(rest, c + V((0, r * 0.7, 0)) - OUTD * 0.02, sm(g)) if g < 1 else c + V((0, r * 0.7, 0)))
            P['rgrip'] = 0.7; P['rpalm'] = (0.0, -1.0, 0.1); return None
    if t < T_TAKE:
        u = sm(seg01(t, *T_IN)); inside = PASS_OUT - OUTD * 0.3 + V((0, 0.34, 0))
        P['rh_w'] = tuple(lerp3(wpt(P, (0.22, 0.75, 0.25)), inside, u)); P['rgrip'] = 0.2; P['rpalm'] = (0.0, 1.0, 0.3); return None
    hc = child_hand_pt(t); P['rh_w'] = tuple(hc + V((0.0, 0.02, 0.0))); P['rgrip'] = 0.55; P['rpalm'] = (0.0, 1.0, 0.0)
    return None
def child_hand_pt(t):
    u = sm(seg01(t, *T_PULL)); a = PASS_OUT - OUTD * 0.26 + V((0, 0.34, 0)); b = C_ST + OUTD * 0.25 - PERP * -0.25 + V((0, 0.72, 0))
    return V(lerp3(a, b, u))

def aren_home(t):
    P = dict(base=tuple(CROUCH), yaw=ang_to(CROUCH, PASS_OUT), eyes='open', mouth='neutral', brow=-0.3, lean=0.05, cape_sway=0.1 * math.sin(t * 1.2))
    up = sm(seg01(t, T_HOME, T_HOME + 0.6))
    if up < 1: kneel(P, 'l', 0.43 * (1 - up))
    bk = sm(seg01(t, T_HOME + 0.5, T_HOME + 1.3)); P['base'] = lerp3(CROUCH, A_HOME, bk)
    if 0 < bk < 1: P['walk'] = -bk * 3.0; P['stride'] = 0.2
    P['yaw'] = angl(ang_to(CROUCH, PASS_OUT), ang_to(A_HOME, HUG), sm(seg01(t, T_HOME + 0.3, T_HUG + 0.4)))
    P['lh'] = lerp3((-0.2, 0.62, 0.25), HOLD, up); P['lgrip'] = 0.55; P['lpalm'] = (0.0, 1.0, 0.15)
    rel = sm(seg01(t, T_RUN[0] + 0.5, T_RUN[0] + 1.0))
    if rel < 1:
        P['rh_w'] = tuple(lerp3(child_hand_pt(T_PULL[1]) + V((0, 0.02, 0)), wpt(P, (0.22, 0.9, 0.08)), rel)); P['rgrip'] = 0.55 * (1 - rel)
    if t > T_HUG: P['eyes'] = 'half'; P['brow'] = -0.4; P['lean'] = 0.02; P['nod'] = 0.08
    # the candle goes out: he turns as if to hear his brother; nothing; lowers the candle; looks at the child
    lb = win(t, T_LOOKB[0], T_LOWER[0] + 0.2, 0.35)
    if lb > 0: P['head'] = (-0.95 * lb, -0.05 * lb, 0.0); P['twist'] = -0.25 * lb; P['eyes'] = 'open' if lb > 0.5 else P['eyes']; P['brow'] = -0.7
    lw = sm(seg01(t, *T_LOWER))
    if lw > 0: P['lh'] = lerp3(HOLD, (-0.2, 0.86, 0.12), lw); P['lpalm'] = (0.2, 1.0, 0.1)
    if t > T_LOWER[1]: P['head'] = (head_to(P, C_ST) * 0.5, 0.15, 0.0); P['eyes'] = 'open'; P['brow'] = -0.4
    mt = talking(t, '10', 5.0)
    if mt: P['mouth'] = mt
    if t > tend('10') + 0.15: P['mouth'] = 'smile'; P['brow'] = -0.2; P['eyes'] = 'half'
    return P
WALK0 = A_HOME + V((0.0, 0, -0.3)); WALK_DIR = V((0.08, 0, -1.0)) / np.linalg.norm(V((0.08, 0, -1.0)))
def aren_walk(t):
    u = t - T_WALK; tu = sm(seg01(t, T_WALK, T_WALK + 0.5))
    d = max(0.0, u - 0.2) * 1.05 * sm(seg01(t, T_WALK + 0.1, T_WALK + 0.6))
    P = dict(base=tuple(WALK0 + WALK_DIR * d), yaw=angl(ang_to(A_HOME, HUG), ang_to(V((0, 0, 0)), WALK_DIR), tu), eyes='open', mouth='smile' if u < 1.6 else 'neutral',
             brow=-0.15, lean=0.06, cape_sway=0.35)
    if d > 0: P['walk'] = d * 6.2; P['stride'] = 0.3
    P['lh'] = (-0.2, 0.9, 0.16); P['lgrip'] = 0.55; P['lpalm'] = (0.2, 1.0, 0.1)
    if t > T_ENDCU - 0.1: P['lh'] = (-0.12, 0.98, 0.26); P['nod'] = 0.22; P['eyes'] = 'half'
    return P

# ======================= the others =======================
def ghost_pose(t):
    P = dict(base=tuple(GHOST), yaw=ang_to(GHOST, A0), eyes='open', mouth='soft', brow=-0.2, lean=0.0, nod=0.06)
    mt = talking(t, '04', 4.5)
    if mt: P['mouth'] = mt
    if t > tend('04'): P['mouth'] = 'smile'
    return P
def ghost_alpha(t):
    return 0.55 * sm(seg01(t, *T_GHOST)) * (1 - sm(seg01(t, T_MEM - 0.3, T_MEM + 0.1))) * (0.9 + 0.1 * math.sin(t * 17))
def young_pose(t):
    yb = ang_to(YA, BR)
    P = dict(base=tuple(YA), yaw=yb, eyes='wide', mouth='o', brow=0.2, lean=0.06, cape_sway=0.1 * math.sin(t * 2))
    gl = win(t, T_POINT + 0.15, T_POINT + 0.75, 0.15)                             # glances back at the passage...
    P['head'] = (0.9 * gl, 0.0, 0.0); P['twist'] = 0.2 * gl
    st = sm(seg01(t, T_POINT + 0.7, T_POINT + 1.3))                              # ...then steps towards his brother instead, hand out
    if st > 0:
        P['base'] = lerp3(YA, YA + DIRM * 0.35, st); P['walk'] = st * 4.0 if st < 1 else None; P['lean'] = 0.15
        P['rh'] = lerp3((0.2, 0.9, 0.1), (0.1, 1.2, 0.5), st); P['rpalm'] = (-0.3, 0.0, 1.0); P['rgrip'] = 0.15; P['mouth'] = 'open' if t < T0['05'] else 'o'
    if t >= T0['05'] + 1.3: P['brow'] = -0.6; P['eyes'] = 'sad'; P['mouth'] = 'neutral'
    return P
def bro_pose(t):
    """kneeling behind the beam: knocks three times, points to the passage, shakes his head, points again"""
    P = dict(base=tuple(BR), yaw=ang_to(BR, PASS_IN), eyes='open', mouth='neutral', brow=-0.3, lean=0.15)
    kneel(P, 'r', 0.5)
    sl = loc(BR, P['yaw'], SLAB + V((0, 0.12, 0)))
    if t < T_POINT:
        ph = 0.0
        for k in range(3):
            tk = T_MK + k * KN; ph = max(ph, 1 - min(1.0, abs(t - tk) / 0.19)) if abs(t - tk) < 0.19 else ph
        lift = 0.0 if t < T_MK - 0.4 else (0.09 * (1 - ph) if t < T_MK + 2 * KN + 0.1 else 0.09)
        P['rh'] = (sl[0], sl[1] + 0.06 + lift, sl[2]); P['rgrip'] = 0.95; P['rpalm'] = (0.0, -1.0, 0.0)
        if t < T_MK - 0.4: P['rh'] = lerp3((0.25, 0.65, 0.25), P['rh'], sm(seg01(t, T_MEM - 0.3, T_MK - 0.4)))
        P['head'] = (-0.25, 0.25, 0.0); P['eyes'] = 'open'; P['brow'] = 0.1
        return P
    pt = sm(seg01(t, T_POINT, T_POINT + 0.35)); P['head'] = (0.0, 0.0, 0.0)
    sh = P_ = None
    aim = PASS_IN + V((0, 0.5, 0))
    urgent = sm(seg01(t, T_SHAKE[0], T_SHAKE[0] + 0.3))
    hand = lerp3(loc(BR, P['yaw'], SLAB + V((0, 0.2, 0))), (0.32, 1.15 + 0.05 * urgent, 0.58), pt)
    P['rh'] = hand; P['rgrip'] = 0.8; P['rpalm'] = (-1.0, 0.0, 0.0)
    if t > T_POINT + 0.4 and urgent > 0:
        P['rh'] = (0.3, 1.18 + 0.03 * math.sin(t * 14) * win(t, T_SHAKE[0], T_SHAKE[1], 0.2), 0.62)
    shk = win(t, T_SHAKE[0], T_SHAKE[1], 0.15)
    P['head'] = (0.3 * math.sin((t - T_SHAKE[0]) * 2 * PI * 2.4) * shk + head_to(P, YA) * 0.3, 0.0, 0.0)
    P['brow'] = -0.7 if t > T_SHAKE[0] else -0.3; P['eyes'] = 'open'
    mt = talking(t, '05', 6.5)
    if mt: P['mouth'] = mt
    if t > tend('05'): P['mouth'] = 'smile'; P['brow'] = -0.5; P['eyes'] = 'half'
    return P
def surv_poses(t):
    out = []
    for sp, off, ya in ((SURV1, -PERPM * 0.55 + DIRM * 0.55, 0.4), (SURV2, PERPM * 0.5 + DIRM * 0.45, -0.3)):
        b = PASS_IN + off
        P = dict(base=tuple(b), yaw=ang_to(b, YA) + ya, crouch=0.42, lean=0.35, eyes='open', mouth='neutral', brow=-0.6, nod=0.1)
        P['rf'] = (0.13, 0.07, 0.22); P['lf'] = (-0.13, 0.07, 0.1)
        P['rh'] = (0.12, 0.62, 0.32); P['lh'] = (-0.12, 0.62, 0.32); P['rgrip'] = P['lgrip'] = 0.5
        out.append((sp, P))
    return out
def child_pose(t):
    """crawls out of the passage holding Aren's hand, stands; the mother's hug; asks"""
    if t < T_TAKE - 0.05: return None
    u = sm(seg01(t, *T_PULL)); b = lerp3(PASS_OUT - OUTD * 0.55, C_ST, u)
    P = dict(base=tuple(b), yaw=ang_to(PASS_IN, PASS_OUT + OUTD), eyes='wide', mouth='o', brow=0.3)
    cr = 1 - sm(seg01(t, T_PULL[1] - 0.5, T_PULL[1] + 0.1))
    P.update(crouch=0.28 * cr, lean=0.75 * cr + 0.05); P['nod'] = -0.5 * cr
    P['lh_w'] = tuple(child_hand_pt(t)); P['lgrip'] = 0.6; P['lpalm'] = (0.0, -1.0, 0.0)
    if t > T_PULL[1]:
        P['lh_w'] = tuple(child_hand_pt(T_PULL[1]))
        rel = sm(seg01(t, T_RUN[0] + 0.5, T_RUN[0] + 1.0))
        if rel > 0: P.pop('lh_w'); P['lh'] = (-0.16, 0.6, 0.1)
        P['yaw'] = angl(P['yaw'], ang_to(C_ST, M0), sm(seg01(t, T_RUN[0], T_RUN[0] + 0.5))); P['eyes'] = 'open'; P['mouth'] = 'neutral'
    if t >= T_HUG - 0.25:                                                    # in her arms: hands on her shoulders
        M = mother_pose(t); hd.human(MOTHER, M)
        P['base'] = tuple(C_ST); P['yaw'] = ang_to(C_ST, M['base'])
        sh_l = M['_chest'] + M['_RW'] @ V((-0.15, 0.06, 0.02)); sh_r = M['_chest'] + M['_RW'] @ V((0.15, 0.06, 0.02))
        h = sm(seg01(t, T_HUG - 0.25, T_HUG + 0.1))
        P['lh_w'] = tuple(sh_r + V((0, 0.03, 0))) if h > 0.5 else None; P['rh_w'] = tuple(sh_l + V((0, 0.03, 0))) if h > 0.5 else None
        if P['lh_w'] is None: P.pop('lh_w'); P.pop('rh_w')
        P['lgrip'] = P['rgrip'] = 0.35; P['eyes'] = 'closed' if t < T_OUT + 1.5 else 'open'; P['mouth'] = 'neutral'; P['lean'] = 0.1
        if t > T0['09'] - 0.7:                                               # lets go, turns to Aren (still in her arms)
            u = sm(seg01(t, T0['09'] - 0.7, T0['09'] - 0.05))
            P['yaw'] = angl(P['yaw'], ang_to(C_ST, A_HOME), 0.55 * u)
            if u > 0.3: P.pop('lh_w', None); P.pop('rh_w', None); P['lh'] = (-0.17, 0.55, 0.08); P['rh'] = (0.17, 0.55, 0.08)
            P['head'] = (head_to(P, A_HOME) * u, -0.15, 0.0); P['eyes'] = 'open'
        mt = talking(t, '09', 6.0)
        if mt: P['mouth'] = mt
    return P
def mother_pose(t):
    run = seg01(t, *T_RUN); ur = sm(run) * 0.5 + run * 0.5
    end = C_ST + (M0 - C_ST) / np.linalg.norm(M0 - C_ST) * 0.42
    P = dict(base=tuple(lerp3(M0, end, ur)), yaw=ang_to(M0, C_ST), eyes='wide', mouth='o', brow=-0.4, lean=0.0)
    if t < T_RUN[0]:
        P['rh'] = (0.06, 1.1, 0.22); P['lh'] = (-0.06, 1.08, 0.22); P['rgrip'] = P['lgrip'] = 0.5; P['eyes'] = 'open'; P['mouth'] = 'neutral'; P['brow'] = -0.7
        return P
    if run < 1: P['walk'] = ur * 15.0; P['stride'] = 0.4; P['lift'] = 0.15; P['lean'] = 0.2
    if t >= T_HUG - 0.3:
        kn = sm(seg01(t, T_HUG - 0.3, T_HUG + 0.15)); kneel(P, 'r', 0.5 * kn); P['lean'] = 0.15
        P['walk'] = None; P['base'] = tuple(end); P['yaw'] = ang_to(end, C_ST)
        # arms round the child's back
        cb = C_ST + V((0, 0.62, 0)); away = (C_ST - end) / np.linalg.norm(C_ST - end); side = V((away[2], 0, -away[0]))
        P['rh_w'] = tuple(cb + away * 0.12 + side * 0.17); P['lh_w'] = tuple(cb + away * 0.12 - side * 0.17); P['rgrip'] = P['lgrip'] = 0.3
        P['eyes'] = 'closed'; P['mouth'] = 'smile' if t > T_HUG + 0.6 else 'o'; P['brow'] = -0.5; P['nod'] = 0.15
        if t > T0['09'] - 0.4: P['eyes'] = 'half'; P['head'] = (head_to(P, A_HOME) * 0.4, 0.1, 0.0)
    return P

# ======================= cameras =======================
def P3(keys): return look.Path(keys)
def keyed(t, K):
    pos = P3([(a, p) for a, p, _, _ in K])(t); tgt = P3([(a, q) for a, _, q, _ in K])(t); fov = P3([(a, f) for a, _, _, f in K])(t)
    return pos, tgt, float(fov[0]) if hasattr(fov, '__len__') else float(fov)
def A(x, y, z): return tuple(A0 + V((x, y, z)))
MEM_T0 = T_MEM - 0.25
def cam_cost(t):
    if t < T0['03'] - 0.1:
        K = [(0.0, A(0.16, 1.42, -1.05), A(0.0, 1.36, 0.0), 36.0), (T_K1 + 0.8, A(0.18, 1.45, -1.15), A(0.0, 1.38, 0.1), 38.0),
             (T0['01'] + 2.0, A(0.6, 1.75, -3.8), A(-1.1, 1.55, 3.6), 52.0), (T_LIGHT - 0.8, A(0.65, 1.8, -4.3), A(-1.1, 1.6, 3.6), 54.0),
             (T_LIGHT - 0.79, A(0.12, 1.42, -0.95), A(-0.04, 1.3, -0.25), 34.0), (T_LIGHT + 0.6, A(0.12, 1.44, -1.0), A(-0.04, 1.33, -0.2), 34.0),
             (T_GHOST[0], A(0.15, 1.5, -1.7), A(-0.3, 1.42, 0.6), 42.0), (T0['03'] - 0.1, A(0.12, 1.52, -1.9), A(-0.32, 1.42, 0.7), 44.0)]
        if t < T_LIGHT - 0.8: K = K[:4]
        else: K = K[4:]
        return keyed(t, K)
    if t < T0['04'] - 0.15:
        K = [(T0['03'] - 0.1, A(2.6, 1.5, 0.45), A(-0.35, 1.3, 0.62), 40.0), (T0['04'] - 0.15, A(2.35, 1.45, 0.5), A(-0.35, 1.3, 0.62), 38.0)]
        return keyed(t, K)
    hc = GHOST + V((0, 1.6, 0)); ah = A0 + V((0, 1.62, 0)); dl = (hc - ah) / np.linalg.norm(hc - ah); pp = V((dl[2], 0, -dl[0]))
    K = [(T0['04'] - 0.15, tuple(ah - dl * 0.45 + pp * 0.32 + V((0, 0.04, 0))), tuple(hc), 30.0), (T_MEM + 0.3, tuple(ah - dl * 0.3 + pp * 0.3 + V((0, 0.03, 0))), tuple(hc), 26.0)]
    return keyed(t, K)
def cam_cost_candle(t):
    """the match-cut source: the flame of Aren's candle"""
    P = aren_present(t); hd.human(AREN, P); c = hold_base(P) + V((0, 0.12, 0))
    return tuple(c + V((0.0, 0.03, -0.38)) if False else c + (V(P['base']) - V(GHOST)) * 0.0 + V((0.12, 0.02, -0.3))), tuple(c), 30.0
def cam_mem(t):
    fl = MEMC + V((0, 0.13, 0))
    if t < T_POINT - 0.1:                                                        # the candle -> the brother knocking (seen from young Aren's side)
        K = [(T_MEM - 0.3, tuple(fl - DIRM * 0.34 + V((0, 0.03, 0))), tuple(fl), 30.0),
             (T_MEM + 0.5, tuple(fl - DIRM * 0.6 - PERPM * 0.1 + V((0, 0.2, 0))), tuple(fl + DIRM * 0.4 + V((0, 0.1, 0))), 38.0),
             (T_MK - 0.1, tuple(BR - DIRM * 1.6 + PERPM * 0.5 + V((0, 1.3, 0))), tuple(lerp3(SLAB, BR, 0.5) + V((0, 0.55, 0))), 40.0),
             (T_POINT - 0.1, tuple(BR - DIRM * 1.45 + PERPM * 0.48 + V((0, 1.28, 0))), tuple(lerp3(SLAB, BR, 0.5) + V((0, 0.6, 0))), 38.0)]
        return keyed(t, K)
    K = [(T_POINT - 0.1, tuple(BR + DIRM * 1.2 + PERPM * 1.0 + V((0, 1.45, 0))), tuple(lerp3(BR, PASS_IN, 0.5) + V((0, 0.7, 0))), 48.0),
         (T0['05'] + 0.2, tuple(BR + DIRM * 1.25 + PERPM * 0.95 + V((0, 1.5, 0))), tuple(lerp3(BR, PASS_IN, 0.55) + V((0, 0.75, 0))), 48.0)]
    if t < T0['05'] + 0.2: return keyed(t, K)
    if t < T0['06'] + 0.1:                                                       # his face as he says it
        f = BR + V((0, 1.12, 0))
        K = [(T0['05'] + 0.2, tuple(BR - DIRM * 1.3 + PERPM * 0.35 + V((0, 1.22, 0))), tuple(f), 30.0), (T0['06'] + 0.1, tuple(BR - DIRM * 1.1 + PERPM * 0.32 + V((0, 1.2, 0))), tuple(f), 27.0)]
        return keyed(t, K)
    if t < ws('06', 3) - 0.1:                                                    # young Aren between, the brother pointing
        K = [(T0['06'] + 0.1, tuple(BR + DIRM * 1.3 + PERPM * 1.1 + V((0, 1.5, 0))), tuple(lerp3(BR, PASS_IN, 0.55) + V((0, 0.75, 0))), 50.0),
             (ws('06', 3) - 0.1, tuple(BR + DIRM * 1.0 + PERPM * 0.95 + V((0, 1.45, 0))), tuple(lerp3(BR, PASS_IN, 0.6) + V((0, 0.7, 0))), 48.0)]
        return keyed(t, K)
    K = [(ws('06', 3) - 0.1, tuple(YA + DIRM * 0.95 - PERPM * 0.55 + V((0, 1.65, 0))), tuple(PASS_IN + V((0, 0.4, 0))), 42.0),     # the way out
         (T_NOW, tuple(YA + DIRM * 0.55 - PERPM * 0.45 + V((0, 1.5, 0))), tuple(PASS_IN + V((0, 0.38, 0))), 30.0)]
    return keyed(t, K)
FLASH_SRC = T_POINT + 0.9
def cam_choice(t):
    if t < T0['07'] - 0.1:                                                       # the crevice: the child's hand knocks
        K = [(T_NOW - 0.2, tuple(CRV + DOOR_DIR * 0.75 + V((0.12, 0.3, 0))), tuple(CRV + V((0, -0.06, 0))), 34.0), (T0['07'] - 0.1, tuple(CRV + DOOR_DIR * 0.65 + V((0.1, 0.25, 0))), tuple(CRV + V((0, -0.06, 0))), 32.0)]
        if t < T_CK + 2 * KN + 0.35: return keyed(t, K)
        f = A0 + V((0, 1.62, 0)); fw = V((math.sin(ang_to(A0, GHOST)), 0, math.cos(ang_to(A0, GHOST))))
        K = [(T_CK + 2 * KN + 0.35, tuple(f + fw * 0.85 + V((0.25, -0.05, 0))), tuple(f), 32.0), (T0['07'] + 2.0, tuple(f + fw * 0.95 + V((0.28, -0.05, 0))), tuple(f), 33.0)]
        return keyed(t, K)
    if t < T_STEP[0]:
        f = A0 + V((0, 1.62, 0)); fw = V((math.sin(ang_to(A0, GHOST)), 0, math.cos(ang_to(A0, GHOST))))
        K = [(T_CK + 2 * KN + 0.35, tuple(f + fw * 0.85 + V((0.25, -0.05, 0))), tuple(f), 32.0), (T_STEP[0], tuple(f + fw * 0.98 + V((0.3, -0.05, 0))), tuple(f), 33.0)]
        return keyed(t, K)
    if t < T_PASS:                                                               # wide: the doorway, the falling stone, the passage
        K = [(T_STEP[0], (-1.9, 1.7, -2.4), (-0.15, 1.25, 3.2), 50.0), (T_PASS, (-2.3, 1.65, -2.0), (-0.75, 1.0, 3.2), 50.0)]
        return keyed(t, K)
    side = PASS_OUT + OUTD * 2.1 - PERP * 0.55; midp = lerp3(CROUCH, PASS_OUT, 0.5)
    K = [(T_PASS, tuple(side + OUTD * 0.6 + V((0, 1.35, 0))), tuple(V(midp) + V((0, 0.55, 0))), 46.0),
         (T_CLR[2][1], tuple(side + V((0, 1.1, 0))), tuple(V(midp) + V((0, 0.42, 0))), 42.0),
         (T_TAKE + 0.2, tuple(side - OUTD * 0.6 + V((0, 0.85, 0))), tuple(PASS_OUT + OUTD * 0.1 + V((0, 0.38, 0))), 36.0),
         (T_HOME, tuple(side - OUTD * 0.1 + V((0, 1.1, 0))), tuple(PASS_OUT + OUTD * 0.6 + V((0, 0.55, 0))), 44.0)]
    return keyed(t, K)
def cam_home(t):
    mid = (C_ST + M0) / 2
    if t < T0['08'] + 0.2:
        K = [(T_HOME, (-1.0, 1.5, -1.3), (-1.75, 0.9, 2.3), 52.0), (T0['08'] + 0.2, (-1.35, 1.45, -0.6), (-2.1, 0.85, 2.5), 46.0)]
        return keyed(t, K)
    if t < T_OUT + 0.4:                                                          # the candle in the foreground, the reunion beyond
        P = aren_home(t); hd.human(AREN, P); c = hold_base(P) + V((0, 0.1, 0)); to = HUG + V((0, 0.7, 0))
        d = (V(to) - c); d = d / np.linalg.norm(d)
        if t > T_OUT - 0.6:
            return tuple(c - d * 0.36 + V((0.0, 0.05, 0))), tuple(c + d * 0.2), 34.0
        return tuple(c - d * 0.42 + V((0.0, 0.1, 0))), tuple(to), 40.0
    f = A_face(t)
    if t < T_LOWER[1] + 0.1:
        P = aren_home(t); fw = V((math.sin(P['yaw']), 0, math.cos(P['yaw'])))
        K = [(T_OUT + 0.4, tuple(f + fw * 0.85 + V((0.15, -0.08, 0)) + PERP * 0.2), tuple(f - V((0, 0.12, 0))), 34.0), (T_LOWER[1] + 0.1, tuple(f + fw * 0.95 + PERP * 0.25 + V((0.1, -0.06, 0))), tuple(f - V((0, 0.1, 0))), 34.0)]
        return keyed(t, K)
    if t < T0['10'] - 0.1:                                                       # the child in her mother's arms asks
        c = C_ST + V((0, 0.98, 0)); dl = V(C_ST) - V(A_HOME); dl = dl / np.linalg.norm(dl); pp = V((-dl[2], 0, dl[0]))
        if pp[2] > 0: pp = -pp
        mp = V(A_HOME) + dl * 0.22 + pp * 0.28
        K = [(T_LOWER[1] + 0.1, tuple(mp + V((0, 1.3, 0))), tuple(c), 38.0), (T0['10'] - 0.1, tuple(mp + dl * 0.08 + V((0, 1.27, 0))), tuple(c), 35.0)]
        return keyed(t, K)
    P = aren_home(t); fw = V((math.sin(P['yaw']), 0, math.cos(P['yaw'])))
    K = [(T0['10'] - 0.1, tuple(f + fw * 0.8 - PERP * 0.15), tuple(f - V((0, 0.08, 0))), 30.0), (T_WALK, tuple(f + fw * 0.72 - PERP * 0.15), tuple(f - V((0, 0.06, 0))), 28.0)]
    return keyed(t, K)
def A_face(t):
    P = aren_home(t); return V(P['base']) + V((0, 1.6, 0))
def cam_walk(t):
    if t < T_ENDCU:
        P = aren_walk(t); b = V(P['base'])
        K = [(T_WALK, tuple(WALK0 + V((-1.1, 1.8, 2.0))), tuple(WALK0 + WALK_DIR * 6 + V((0, 1.2, 0))), 46.0), (T_ENDCU, tuple(WALK0 + WALK_DIR * 0.6 + V((-0.9, 1.75, 1.7))), tuple(WALK0 + WALK_DIR * 8 + V((0, 1.3, 0))), 44.0)]
        return keyed(t, K)
    P = aren_walk(t); b = V(P['base'])                                           # the end frame: the dead candle in his hand (= frame 0 framing)
    return tuple(b + WALK_DIR * 1.05 + V((0.12, 1.42, 0))), tuple(b + V((0, 1.36, 0))), 36.0
def cam_shot(t, sc=None):
    sc = sc or scene(t)
    if sc == 'cost': return cam_cost(t)
    if sc == 'mem': return cam_mem(t)
    if sc == 'flash': return cam_mem(FLASH_SRC)
    if sc == 'choice': return cam_choice(t)
    if sc == 'home': return cam_home(t)
    return cam_walk(t)

# ======================= world =======================
def rain_faces(pos, tgt, t, amt=1.0, n=230, col=(120, 134, 160)):
    if amt <= 0.01: return []
    cp = V(pos, float); f = V(tgt, float) - cp; f[1] = 0; f = f / (np.linalg.norm(f) + 1e-9); rt = V((f[2], 0, -f[0]))
    Q = []
    for i in range(int(n * amt)):
        d = 0.8 + 7.5 * hsh(i, 1); s = (hsh(i, 2) - 0.5) * 2 * d * 0.6; base = cp + f * d + rt * s
        y = cp[1] + 3.5 - ((t * 8.5 + hsh(i, 3) * 7.0) % 7.0); L = 0.2; w = 0.004 + 0.004 * d / 8
        a = V((base[0], y, base[2])); b = a + V((0.03, -L, 0))
        Q.append(hd.face([a - rt * w, a + rt * w, b + rt * w, b - rt * w], col, emit=True))
    return [q for q in Q if q]
def dust_faces(t, n=40):
    Q = []
    for i in range(n):
        c = BEAM_C + PERPM * (hsh(i, 1) * 3 - 1.5) + DIRM * (hsh(i, 2) * 3 - 1.8) + V((0.1 * math.sin(t * 0.4 + i), 0.3 + 2.0 * hsh(i, 3) + 0.08 * math.sin(t * 0.3 + i * 2), 0))
        s = 0.006 + 0.006 * hsh(i, 4)
        Q.append(hd.face([c + V((-s, 0, 0)), c + V((0, s, 0)), c + V((s, 0, 0)), c + V((0, -s, 0))], (255, 214, 150), emit=True))
    return [q for q in Q if q]
def falling_stone(t):
    top = ring_pt(PHI_DOOR + 0.05, R_OUT + 0.05, 2.36); land = MOUND + DOOR_DIR * 0.45 + V((0.05, 0.86, 0))
    if t < T_FALL: c = top; R = np.eye(3)
    else:
        u = seg01(t, T_FALL, T_FALL + 0.45); c = V(lerp3(top, land, u)) + V((0, 0.25 * math.sin(PI * u) - 0.25 * u * u * 0, 0)); R = hd.Rx(u * 3) @ hd.Rz(u * 2)
        if t > T_FALL + 0.45: c = land + DOOR_DIR * 0.25 * sm(seg01(t, T_FALL + 0.45, T_FALL + 0.9)) + V((0, -0.1 * seg01(t, T_FALL + 0.45, T_FALL + 0.9), 0)); R = hd.Rx(3) @ hd.Rz(2)
    Q = hd.bx(c, R, (0.11, 0.08, 0.09), (116, 110, 102))
    if T_FALL + 0.4 < t < T_FALL + 1.6:                                          # dust puff
        u = seg01(t, T_FALL + 0.4, T_FALL + 1.6)
        for i in range(10):
            a = 2 * PI * i / 10; r = 0.1 + 0.5 * u; p = land + V((r * math.cos(a), 0.05 + 0.3 * u * hsh(i, 3), r * math.sin(a)))
            s = 0.05 * (1 - u) + 0.02
            Q.append(hd.face([p + V((-s, 0, 0)), p + V((0, s, 0)), p + V((s, 0, 0)), p + V((0, -s, 0))], (120, 118, 118), emit=True))
    return [q for q in Q if q]
def child_hand_faces(t):
    """the child's small hand in the crevice, knocking a pebble three times (only around the knocks)"""
    if not (T_NOW - 0.3 < t < T_STEP[0]): return []
    ph = 0.0
    for k in range(3):
        tk = T_CK + k * KN
        if abs(t - tk) < 0.19: ph = max(ph, 1 - abs(t - tk) / 0.19)
    out_ = sm(seg01(t, T_NOW - 0.3, T_CK - 0.25)) * (1 - sm(seg01(t, T_CK + 2 * KN + 1.6, T_CK + 2 * KN + 2.2)))
    if out_ < 0.02: return []
    R = hd.Ry(PHI_DOOR)
    wr = CRV + DOOR_DIR * (0.08 * out_) + V((0, -0.02 + 0.08 * (1 - ph) * (t < T_CK + 2 * KN + 0.3), 0))
    el = CRV - DOOR_DIR * 0.22 + V((0, 0.03, 0))
    Q = hd.limb(el, wr, 0.03, 0.026, (170, 92, 70), n=7, m=1)
    Q += hd.hand(wr, wr - el, V((0, -1.0, 0)), 0.95, CHILD['skin'], 0.62)
    Q += rock(wr + DOOR_DIR * 0.05 + V((0, -0.03, 0)), 0.02, (140, 136, 130), seed=77)
    return Q
def stones_faces(t):
    if t < T_NOW: return []
    Q = []
    for i, c, r, a, b in stones(t): Q += rock(c, r, (106, 102, 96), seed=60 + i, flat=0.7)
    return Q
def world(t, sc, pos, tgt, ghost=True):
    L = []; layers = []; fog = (16, 20, 30); amb = 0.3; fs, fe = 8, 40
    if sc in ('mem', 'flash'):
        tt = FLASH_SRC if sc == 'flash' else t
        layers += [get_set('tower'), get_set('mem'), dust_faces(tt)]
        lt, _ = 1.0, 0
        cq, fp = candle(MEMC, 1.0, tt, seed=3); layers.append(cq)
        fl = 1 + 0.08 * math.sin(tt * 11) + 0.05 * math.sin(tt * 29)
        L += [(tuple(fp + V((0, 0.1, 0))), (255, 186, 120), 1.5 * fl), (tuple(BR + V((0.4, 2.6, 0.3))), (240, 200, 160), 0.7), (tuple(PASS_IN + V((0, 1.2, 0)) + DIRM * 0.8), (210, 170, 130), 0.5),
              ((0, 9, 6), (120, 110, 130), 0.5)]
        layers.append(hd.human(BRO, bro_pose(tt))); layers.append(hd.human(YOUNG, young_pose(tt)))
        for sp, P in surv_poses(tt): layers.append(hd.human(sp, P))
        fog = (34, 24, 18); amb = 0.3; fs, fe = 6, 22
        return layers, L, fog, amb, fs, fe
    layers += [get_set('tower'), get_set('out')]
    dawn = sm(seg01(t, T_HOME - 1.0, DUR)) if t > T_HOME - 1.0 else 0.0
    rain = 1.0 - sm(seg01(t, T_OUT - 1.0, T_WALK + 0.5))
    L += [((-12, 14, -6), mixc((120, 140, 200), (200, 170, 150), dawn), 1.2 + 0.8 * dawn), ((8, 6, 10), (90, 100, 140), 0.6)]
    if dawn > 0: L.append(((-4, 4, -30), (255, 190, 140), 3.0 * dawn))
    fog = mixc((18, 22, 36), (150, 120, 112), dawn * 0.85); amb = lerp(0.36, 0.46, dawn)
    cf = V(pos, float); fw_ = V(tgt, float) - cf; fw_ = fw_ / (np.linalg.norm(fw_) + 1e-9); L.append((tuple(cf - fw_ * 1.6 + V((0.3, 1.0, 0))), (120, 134, 180), 0.45))
    if dawn > 0.05:                                                                   # dawn band low in the sky (behind the camera at the start)
        for i in range(12):
            x0 = -40 + 7 * i; c = mixc((40, 44, 70), (255, 196, 140), dawn)
            layers.append([q for q in [hd.face([(x0, -1, -46), (x0 + 7, -1, -46), (x0 + 7, 4, -46), (x0, 4, -46)], c, emit=True),
                                         hd.face([(x0, 4, -46), (x0 + 7, 4, -46), (x0 + 7, 9, -46), (x0, 9, -46)], mixc(c, fog, 0.5), emit=True)] if q])
        layers.append([q for q in [hd.face([(-4 + 1.6 * math.cos(2 * PI * k / 14), 1.2 + 1.6 * math.sin(2 * PI * k / 14), -45.5) for k in range(14)], mixc((120, 100, 90), (255, 232, 190), dawn), emit=True)] if q])
    layers.append(falling_stone(t)); layers.append(child_hand_faces(t)); layers.append(stones_faces(t))
    # Aren + candle
    if sc == 'cost': P = aren_present(t)
    elif sc == 'choice': P = aren_present(t)
    elif sc == 'home': P = aren_home(t)
    else: P = aren_walk(t)
    if sc == 'choice': hd.human(AREN, P); aren_hands_choice(P, t)
    layers.append(hd.human(AREN, P))
    lit, smoke = candle_state(t)
    cq, fp = candle(hold_base(P), lit, t, smoke=smoke); layers.append(cq)
    if lit > 0: L.append((tuple(fp + V((0, 0.05, 0))), (255, 180, 100), 0.75 * lit * (0.92 + 0.08 * math.sin(t * 19))))
    if T_LIGHT - 0.2 < t < T_LIGHT + 0.2:                                            # flint sparks
        for i in range(6):
            u = seg01(t, T_LIGHT - 0.2, T_LIGHT + 0.2); p = fp + V(((hsh(i, 1) - 0.5) * 0.15 * u, (hsh(i, 2) - 0.2) * 0.1 * u, (hsh(i, 3) - 0.5) * 0.12 * u))
            layers.append([q for q in [hd.face([p, p + V((0.006, 0.006, 0)), p + V((0.012, 0, 0))], (255, 230, 150), emit=True)] if q])
        L.append((tuple(fp), (255, 210, 140), 1.2))
    if sc == 'cost' and ghost:
        G = ghost_pose(t); layers.append(hd.human(BRO, G))
    if sc in ('choice', 'home', 'walk'):
        C = child_pose(t)
        if C is not None: layers.append(hd.human(CHILD, C))
        if t >= T_HOME - 0.2: layers.append(hd.human(MOTHER, mother_pose(t)))
    layers.append(rain_faces(pos, tgt, t, rain))
    fs, fe = (8, 40) if dawn < 0.5 else (14, 70)
    return layers, L, fog, amb, fs, fe

def grade(a, sc, t):
    if sc in ('mem', 'flash'):
        l = a.mean(axis=2, keepdims=True); a = (a * 0.8 + l * 0.2) * np.array([1.07, 0.99, 0.86])
        yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]; r = np.hypot((xx - a.shape[1] / 2) / a.shape[1], (yy - a.shape[0] / 2) / a.shape[0])
        a = a * (1 - 0.55 * np.clip(r - 0.25, 0, 1))[..., None]
        return a
    dawn = sm(seg01(t, T_HOME - 1.0, DUR)) if t > T_HOME - 1.0 else 0.0
    l = a.mean(axis=2, keepdims=True); a = a * 0.75 + l * 0.25
    return a * (np.array([0.86, 0.96, 1.12]) * (1 - dawn) + np.array([1.05, 1.0, 0.95]) * dawn)
def render_low(t, sc, ghost=False):
    pos, tgt, fov = cam_shot(t, sc); cam = Camera.look(tuple(pos), tuple(tgt))
    layers, L, fog, amb, fs, fe = world(t, sc, pos, tgt, ghost)
    R = Renderer(W, H, fog=fog)
    img, vi, zb = zrender(R, cam, layers, L, fov=fov, fog_start=fs, fog_end=fe, ambient=amb, return_z=True)
    a = look.outline(np.asarray(img).astype(np.float32), zb)
    a = grade(a, sc, t)
    a = np.clip((a - 112) * 1.1 + 110, 0, 255)
    return a
def frame_low(t):
    sc = scene(t)
    if sc == 'cost' and ghost_alpha(t) > 0.01:                                        # the brother as a warm, half-there shape
        al = ghost_alpha(t); a0 = render_low(t, sc, ghost=False); a1 = render_low(t, sc, ghost=True)
        a1 = a1 * np.array([1.08, 1.0, 0.86])
        a = a0 * (1 - al) + a1 * al
    else: a = render_low(t, sc)
    # dissolves: the match-cut into the memory, out of it, and the flash
    def mix(a, b_sc, u): return a * (1 - u) + render_low(t, b_sc) * u
    if T_MEM - 0.3 <= t < T_MEM + 0.3: u = sm(seg01(t, T_MEM - 0.3, T_MEM + 0.3)); a = mix(render_low(t, 'cost'), 'mem', u) if sc == 'cost' else render_low(t, 'cost') * (1 - u) + a * u
    if T_NOW <= t < T_NOW + 0.3: u = sm(seg01(t, T_NOW, T_NOW + 0.3)); a = render_low(t, 'mem') * (1 - u) + a * u
    if T_FLASH[0] <= t < T_FLASH[0] + 0.12: u = seg01(t, T_FLASH[0], T_FLASH[0] + 0.12); a = render_low(t, 'choice') * (1 - u) + a * u
    if T_FLASH[1] - 0.12 <= t < T_FLASH[1]: u = seg01(t, T_FLASH[1] - 0.12, T_FLASH[1]); a = a * (1 - u) + render_low(t, 'choice') * u
    return post.ps1(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), levels=6)

# ======================= subtitles + frame =======================
COL = {'N': (242, 238, 226), 'B': (255, 196, 120), 'A': (130, 190, 255), 'C': (255, 186, 196)}
SUBS = look.Subtitles(SCR, LINES, W, H, S, COL, title_key='-none-', n=17,
                      hil={'CANDLE', 'VOICE', 'BROTHER.', 'PASSAGE.', 'KNOCKS', 'OUT.', 'SIGNAL.', 'UNDERSTOOD.', 'ASKED.', 'GONE.', 'STAYED.'})
def frame_final(t):
    img = frame_low(t); arr = post.upscale(img, S)
    arr = SUBS.apply(arr, t)
    if t >= T_FADE: arr = arr * (1 - sm(seg01(t, T_FADE, DUR - 0.12)))
    return arr
def frame(t): return Image.fromarray(np.clip(frame_final(t), 0, 255).astype(np.uint8)).resize((W, H), Image.BOX)

ASSET = os.environ.get('ASSET')
if ASSET and __name__ == '__main__':
    ims = []
    if ASSET == 'lineup':
        Q = []; xs = [-1.6, -0.8, 0.0, 0.8, 1.6]
        for (nm, sp), x in zip(CAST.items(), xs): Q += hd.human(sp, dict(base=(x, 0, 0), yaw=PI, eyes='open', mouth='smile'))
        fl = hd.bx((0, -0.05, 0), np.eye(3), (4, 0.05, 3), (70, 64, 58))
        for cp, tg, fv in (((0, 1.2, -4.6), (0, 0.95, 0), 40), ((-1.6, 1.62, -0.6), (-1.6, 1.58, 0), 30)):
            R_ = Renderer(W, H, fog=(30, 30, 40)); img, vi, zb = zrender(R_, Camera.look(cp, tg), [fl, Q], [((1.5, 2.5, -2.0), (255, 226, 190), 2.0), ((-2.5, 1.5, -1.0), (150, 170, 230), 0.8)], fov=fv, fog_start=10, fog_end=40, ambient=0.45, return_z=True)
            ims.append(post.ps1(Image.fromarray(np.clip(look.outline(np.asarray(img).astype(np.float32), zb), 0, 255).astype(np.uint8)), levels=6))
    out = Image.new('RGB', (W * len(ims), H))
    for i, im in enumerate(ims): out.paste(im, (i * W, 0))
    out.save(f'test_le_{ASSET}.png'); print('written'); sys.exit()

TEST = os.environ.get('TEST')
if TEST and __name__ == '__main__':
    ts = [float(x) for x in TEST.split(',')] if TEST != 'all' else [round(x, 2) for x in np.arange(0, DUR, float(os.environ.get('STEP', '1.0')))]
    ims = [Image.fromarray(np.clip(frame_final(x), 0, 255).astype(np.uint8)).resize((270, 480), Image.LANCZOS) for x in ts]
    per = int(os.environ.get('PER', '8')); rows = (len(ims) + per - 1) // per; shp = Image.new('RGB', (min(per, len(ims)) * 272, rows * 498), (30, 30, 30))
    dd = ImageDraw.Draw(shp)
    for i, (im, x) in enumerate(zip(ims, ts)): shp.paste(im, ((i % per) * 272, (i // per) * 498)); dd.text(((i % per) * 272 + 4, (i // per) * 498 + 483), f'{x:.2f} {scene(x)}', fill=(255, 255, 0))
    shp.save(os.environ.get('TEST_OUT', 'test_le.png')); print('test written', DUR); sys.exit()

# ======================= QA manifest =======================
QA = dict(fps=FPS, dur=DUR, W=W, frame=frame, chars={}, geom=lambda t, name, st, V_: [], camera=lambda t: cam_shot(t)[0], min_cam_dist=0.3,
          camera_ok=lambda p: True, allow_jump=[], weapon_events=[],
          scenes=[dict(id='cost', t0=0.0, t1=T_MEM, action='night rain, three knocks, Aren lights the candle, his brother appears behind him, he reaches and stops'),
                  dict(id='mem', t0=T_MEM, t1=T_NOW, action='warm memory: the brother knocks, points to the passage, young Aren misunderstands, the way out'),
                  dict(id='choice', t0=T_NOW, t1=T_HOME, action='the child knocks; Aren nearly goes for the doorway; the flash; clears the passage; takes the hand'),
                  dict(id='home', t0=T_HOME, t1=T_WALK, action='the mother runs and hugs the child; the candle goes out; he turns; "Were you scared?" "Yes."'),
                  dict(id='walk', t0=T_WALK, t1=DUR, action='he walks into the dawn; the dead candle in his hand; fade')],
          texts=lambda: [])

# ======================= AUDIO =======================
LVL = {'04': -1.0, '05': 0.0, '09': 0.5, '10': -0.5}
def knock_sample(sr):
    """one dry knock on stone: identical every time (same seed)"""
    n = int(0.16 * sr); tt = np.arange(n) / sr; rng = np.random.default_rng(1234)
    body = np.sin(2 * np.pi * 120 * tt * (1 - 0.25 * tt / 0.16)) * np.exp(-tt * 38)
    click = rng.normal(0, 1, n) * np.exp(-tt * 160)
    from scipy.signal import butter, lfilter
    b, a = butter(2, [700 / (sr / 2), 3200 / (sr / 2)], 'band'); click = lfilter(b, a, click)
    x = body * 0.8 + click * 1.6; return x / np.abs(x).max()
def build_audio(path):
    import soundfile as _sf
    s = Sound(DUR, loop=False, seed=91); sr = s.sr; n = s.n; t = s.t
    BED = np.zeros(n); FX = np.zeros(n); MUS = np.zeros(n); KNK = np.zeros(n)
    def put(buf, x, t0, v=1.0):
        i = int(round(t0 * sr))
        if i >= n or i + len(x) <= 0: return
        if i < 0: x = x[-i:]; i = 0
        j = min(n, i + len(x)); buf[i:j] += (x * v)[:j - i]
    def nb(t0, d, lo, hi, v, seed, shape=2, buf=None): put(FX if buf is None else buf, s.filt_short(s.noise(d, seed), lo=lo, hi=hi) * np.sin(np.pi * s.T(d) / d) ** shape, t0, v)
    def tone(t0, m, d, v, dec=3.0, att=0.005, buf=None, harm=(1.0,)):
        f = 440 * 2 ** ((m - 69) / 12); tt = s.T(d); x = sum(a * np.sin(2 * np.pi * f * (k + 1) * tt) for k, a in enumerate(harm))
        put(FX if buf is None else buf, x * np.minimum(1, tt / att) * np.exp(-tt * dec), t0, v)
    def mask(a, b, r=0.15): return np.clip(np.minimum((t - a) / r, (b - t) / r), 0, 1)
    def step(t0, v=0.03, seed=0, wet=True):
        tt = s.T(0.12); put(FX, s.filt_short(s.noise(0.12, seed), lo=150, hi=4000 if wet else 1800) * np.exp(-tt * 30) + np.sin(2 * np.pi * 75 * tt) * np.exp(-tt * 26) * 0.3, t0, v)
    def piano(t0, m, v=0.05, d=3.0, buf=None):
        tone(t0, m, d, v, dec=1.2, harm=(1.0, 0.45, 0.2, 0.08), buf=buf); tone(t0 + 0.002, m + 12, d, v * 0.15, dec=2.0, buf=buf)
    def stone(t0, v=0.05, seed=0):
        nb(t0, 0.25, 150, 1600, v, seed, 1); tt = s.T(0.2); put(FX, np.sin(2 * np.pi * 70 * tt) * np.exp(-tt * 22), t0 + 0.05, v * 0.8)
    K = knock_sample(sr)
    def knocks(t0, v=0.3, echo=False):
        for k in range(3): put(KNK, K, t0 + k * KN, v)
        if echo:
            for k in range(3): put(KNK, s.filt_short(K, lo=200, hi=2000), t0 + k * KN + 0.38, v * 0.32); put(KNK, s.filt_short(K, lo=200, hi=1500), t0 + k * KN + 0.76, v * 0.12)
    # ---- rain (present), stops towards dawn
    pres = 1 - mask(T_MEM, T_NOW, 0.3)
    rainA = pres * (1 - np.clip((t - (T_OUT - 1.0)) / (T_WALK + 0.5 - T_OUT + 1.0), 0, 1))
    BED += s.filt(s.rng.normal(0, 1, n), lo=900, hi=8000) * 0.045 * rainA
    BED += s.filt(s.rng.normal(0, 1, n), lo=150, hi=900) * 0.02 * rainA
    for k in range(int(DUR * 7)):
        tb = k / 7 + 0.1 * hsh(k, 8)
        if tb < DUR: put(BED, np.sin(2 * np.pi * (1800 + 1500 * hsh(k, 9)) * s.T(0.02)) * np.exp(-s.T(0.02) * 200), tb, 0.008 * float(rainA[min(n - 1, int(tb * sr))]))
    # ---- the knocks: identical every time
    knocks(T_K1, 0.3); knocks(T_MK, 0.3, echo=True); knocks(T_CK, 0.3)
    # ---- candle: flint, flame, out
    nb(T_LIGHT - 0.2, 0.12, 2500, 9000, 0.05, 5, 1); nb(T_LIGHT - 0.05, 0.1, 2500, 9000, 0.05, 6, 1)
    nb(T_LIGHT + 0.12, 0.5, 200, 1500, 0.035, 7, 1)                                                        # the flame catches (soft whoomp)
    lit = np.clip((t - T_LIGHT) / 0.4, 0, 1) * (t < T_OUT) * pres
    BED += s.filt(s.rng.normal(0, 1, n), lo=300, hi=2500) * 0.006 * lit
    nb(T_OUT - 0.05, 0.35, 300, 2200, 0.03, 9, 1)                                                          # it goes out
    # ---- ghost: a faint warm swell (not scary)
    gh = mask(T_GHOST[0], T_MEM, 0.8)
    for f, a in ((220.0, 1.0), (330.0, 0.5)): MUS += np.sin(2 * np.pi * f * t) * a * 0.008 * gh
    # ---- memory: dust, creak, after the knocks' echo the music rises gently (D major)
    mem = mask(T_MEM, T_NOW, 0.3)
    BED += s.filt(s.rng.normal(0, 1, n), lo=80, hi=500) * 0.03 * mem
    for f, a in ((110.0, 1.0), (165.0, 0.5)): MUS += np.sin(2 * np.pi * f * t) * a * 0.012 * mem          # a low warm hum under the memory
    tt = s.T(1.2); put(FX, np.sin(2 * np.pi * (180 + 40 * np.sin(tt * 9)) * tt) * np.exp(-tt * 3) * 0.6, T_MEM + 0.2, 0.012)
    rise = np.clip((t - (T_MK + 2 * KN + 0.9)) / 4.0, 0, 1)
    musA = rise * (1 - mask(T_CK - 0.3, T0['07'] + 0.2, 0.25) * 0.85)                                      # a beat of silence for the child's knocks
    musA = musA * np.clip((T_OUT - 0.25 - t) / 0.25, 0, 1)                                                 # silence when the candle dies
    warm = np.clip((t - T_HOME) / 3.0, 0, 1)
    for f, a in ((146.8, 1.0), (220.0, 0.55), (293.7, 0.4), (370.0, 0.22 + 0.15 * 0)): MUS += np.sin(2 * np.pi * f * t + a) * a * 0.016 * musA * (1 + 0.35 * warm)
    MUS += np.sin(2 * np.pi * 440.0 * t) * 0.006 * musA * warm
    notes = [(T_MK + 2 * KN + 1.0, 62), (T0['05'] + 0.6, 66), (T0['06'] + 0.2, 69), (ws('06', 3), 74), (T0['07'] + 0.3, 62), (T_FLASH[0], 69), (T_TAKE, 74), (T_HUG, 66), (T0['08'] + 0.2, 69)]
    for a_, m in notes: piano(a_, m, 0.045)
    # ---- choice: the falling stone, steps, the stones moved, the child's grip
    stone(T_FALL + 0.45, 0.08, 11); nb(T_FALL + 0.4, 0.8, 300, 3000, 0.02, 12, 1)
    tt = s.T(0.6); put(FX, s.filt_short(s.noise(0.6, 13), lo=60, hi=500) * np.exp(-tt * 4), T_FALL - 0.15, 0.05)   # the lintel grinds
    for k in range(4): step(T_STEP[0] + 0.15 + k * 0.32, 0.03, 20 + k)
    k = 0
    while T_TURNP + 0.2 + k * 0.36 < T_ARRIVE: step(T_TURNP + 0.2 + k * 0.36, 0.03, 30 + k); k += 1
    nb(T_KNEEL[0] + 0.2, 0.25, 200, 1500, 0.03, 40, 1)
    for k, (a_, b_) in enumerate(T_CLR): stone(a_ + 0.18, 0.04, 50 + k); stone(b_ - 0.08, 0.05, 60 + k)
    nb(T_IN[0], 0.5, 200, 1200, 0.02, 70, 1)
    nb(T_TAKE - 0.02, 0.12, 600, 3000, 0.03, 71, 1); tt = s.T(0.12); put(FX, np.sin(2 * np.pi * 95 * tt) * np.exp(-tt * 30), T_TAKE, 0.05)    # small hand grips his
    nb(T_PULL[0] + 0.1, 1.2, 150, 1800, 0.025, 72, 2); stone(T_PULL[0] + 0.5, 0.025, 73)
    # ---- home: the mother runs, the hug
    k = 0
    while T_RUN[0] + k * 0.27 < T_RUN[1]: step(T_RUN[0] + k * 0.27, 0.035, 80 + k); k += 1
    nb(T_HUG - 0.05, 0.4, 200, 1800, 0.035, 85, 1)
    # ---- after the candle: rain thinning, first birds, steps, the end
    dn = np.clip((t - (T_OUT + 1.5)) / 3.0, 0, 1)
    BED += s.filt(s.rng.normal(0, 1, n), lo=200, hi=1200) * 0.018 * dn
    for k in range(int((DUR - T_OUT) / 0.9)):
        tb = T_OUT + 2.5 + k * 0.9 + 0.5 * hsh(k, 12)
        for j in range(2): tt = s.T(0.09); put(BED, np.sin(2 * np.pi * (3000 + 700 * j + 500 * hsh(k, j)) * tt * (1 + 0.3 * tt / 0.09)) * np.sin(np.pi * tt / 0.09) ** 2, tb + j * 0.13, 0.004)
    k = 0
    while T_WALK + 0.3 + k * 0.5 < DUR - 0.5: step(T_WALK + 0.3 + k * 0.5, 0.025, 120 + k, wet=False); k += 1
    endm = mask(tend('10') + 0.3, DUR + 2, 1.2) * np.clip((DUR - 0.1 - t) / 0.8, 0, 1)
    for f, a in ((146.8, 1.0), (220.0, 0.5), (293.7, 0.4), (370.0, 0.3)): MUS += np.sin(2 * np.pi * f * t) * a * 0.012 * endm
    piano(tend('10') + 0.4, 62, 0.05); piano(T0['11'] + 1.2, 66, 0.04); piano(ws('11', 1) + 0.1, 69, 0.045); piano(tend('11') + 0.1, 74, 0.04)
    # ---- voice
    NB = np.zeros(n); wins = []
    for k_, t0 in LINES:
        a, ar = _sf.read(os.path.join(TTS_DIR, 'le', f'{k_}.wav')); a = a if a.ndim == 1 else a.mean(1)
        a = np.interp(np.arange(int(len(a) * sr / ar)) / sr, np.arange(len(a)) / ar, a); act = np.abs(a) > 0.02 * np.abs(a).max()
        a = a * (0.12 / np.sqrt((a[act] ** 2).mean())) * 10 ** (LVL.get(k_, 0.0) / 20)
        put(NB, a, t0); wins.append((t0, t0 + len(a) / sr))
    g = duck_envelope(n, sr, wins, -7.0, 0.05, 0.25)
    endf = np.clip((DUR - 0.05 - t) / 0.9, 0, 1)
    bed = (BED * g + MUS * (0.65 + 0.35 * g)) * endf; fx = FX * (0.6 + 0.4 * g) * endf
    L_ = bed + fx + KNK; R_ = np.roll(bed, 700) + np.roll(fx, 200) + KNK
    pk = max(np.abs(L_).max(), np.abs(R_).max()); gv = pk * 1.6 / np.abs(NB).max()
    s.L = L_ + NB * gv; s.R = R_ + NB * gv; s.reverb(0.1, length=1.2, decay=3.0)
    return s.save(path, peak=0.9)
if __name__ == '__main__' and os.environ.get('PART') == 'audio':
    print(build_audio(os.path.join(OUT, 'the_last_echo.wav'))); sys.exit()
if __name__ == '__main__' and os.environ.get('PART'):
    a, b = map(int, os.environ['PART'].split(':'))
    import subprocess
    p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W * S}x{H * S}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', os.path.join(OUT, f'le_{a:05d}.mp4')], stdin=subprocess.PIPE)
    vhs = post.VHS(W * S, H * S, S, grade='none', chroma=0, scan_dark=1.0, vignette=0.22, grain=0.9, band_period=1e9)
    for f in range(a, min(b, N)): p.stdin.write(vhs(frame_final(f / FPS), f, f / FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done', a, b); sys.exit()
