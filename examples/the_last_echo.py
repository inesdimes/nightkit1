"""THE LAST ECHO v2 (Insert Disc 2, 24 Nov 2026) ~58 s, 9:16, nightkit HD figures, no speed-up.
v2 = Enes's revision brief (pasted 24 Nov): story causality made visible. Hook = the child's hand knocking; the candle; a flame
transition + YEARS AGO into the warm memory (brother trapped, knocks, young Aren rushes, the brother points to the passage that shows
the moonlit outside, 'Don't come back for me. Get them out.', young Aren hesitates, leads the others out); the pointing composition
cuts to the same passage today; the child knocks the same rhythm; Aren freezes; flash of the pointing hand; the direct route
collapses; he sets the candle down, crawls through the passage, pulls the child out before it gives way; mother; the candle dies;
silence. v1 (first brief) is kept in ../scratch_old/the_last_echo_v1.py.
Voices: tools/tts/le.py (draft AI; Enes records later). Brief: briefs/the_last_echo.md (v2 section).

  TEST=0,5,10 python examples/the_last_echo.py      -> test_le.png contact sheet"""
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
def flat(v): v = V(v, float).copy(); v[1] = 0; return v / (np.linalg.norm(v) + 1e-9)

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

# ======================= layout =======================
TC = V((0.0, 0.0, 6.0)); R_IN, R_OUT = 2.4, 2.9
PHI_DOOR = 2.75; PHI_PASS = -2.45; PH_W = 0.13; PH_H = 0.74
def ring_pt(phi, r, y=0.0): return V((TC[0] + r * math.sin(phi), y, TC[2] + r * math.cos(phi)))
DOOR_OUT = ring_pt(PHI_DOOR, R_OUT); DOOR_DIR = V((math.sin(PHI_DOOR), 0, math.cos(PHI_DOOR)))
DOOR_IN = ring_pt(PHI_DOOR, R_IN)
PASS_OUT = ring_pt(PHI_PASS, R_OUT); PASS_IN = ring_pt(PHI_PASS, R_IN); OUTD = V((math.sin(PHI_PASS), 0, math.cos(PHI_PASS)))
PERP = V((OUTD[2], 0, -OUTD[0]))
DIRM = -OUTD; PERPM = V((DIRM[2], 0, -DIRM[0]))
MOUND = DOOR_OUT + DOOR_DIR * 0.25
MF = MOUND + DOOR_DIR * 1.3                                      # where Aren stands to dig at the doorway
DIG = MOUND + DOOR_DIR * 0.72 + V((0, 0.55, 0))                  # the stone he pulls at
A0 = V((0.3, 0.0, 0.55)); YAW0 = ang_to(A0, TC)
M0 = V((-2.5, 0.0, 0.25))                                        # the mother, waiting
CROUCH = PASS_OUT + OUTD * 0.75 + PERP * 0.45                    # he kneels here at the passage
RK = PASS_OUT + OUTD * 0.25 + PERP * 0.66                        # the rock he sets the candle on
CANDLE_ON_ROCK = RK + V((0, 0.115, 0))
C_ST = PASS_OUT + OUTD * 1.05 - PERP * 0.12                      # the child, out
AEND = PASS_OUT + OUTD * 0.75 + PERP * 1.05                      # Aren after the rescue (aside)
HUGP = M0 + flat(C_ST - M0) * 0.55
# memory: passage -> young Aren -> beam -> brother on one line
YA0 = PASS_IN + DIRM * 0.95 - PERPM * 0.15; YA1 = PASS_IN + DIRM * 1.75
BEAM_C = PASS_IN + DIRM * 2.35; BR = PASS_IN + DIRM * 3.15
MEMC = BEAM_C + DIRM * 0.38 - PERPM * 0.55 + V((0, 0.62, 0))
SLAB = BR - DIRM * 0.38 + PERPM * 0.2 + V((0, 0.42, 0))
# present inside: the child under a fallen beam, near the passage
CH = PASS_IN + DIRM * 1.3 + PERPM * 0.45
KNOCKST = CH + flat(PASS_IN - CH) * 0.3 + V((PERPM[0] * -0.12, 0.3, PERPM[2] * -0.12))

# ======================= voice timings =======================
SCR = json.load(open(os.path.join(TTS_DIR, 'le', 'script.json')))
def D_(k): return SCR['dur'][k]
T0 = {}
KN = 0.42
def tend(k): return T0[k] + D_(k)
def ws(k, i): return T0[k] + SCR['sent'][k][i][0]
T_K0 = 0.15                                                       # hook: the child's knocks
T_FRZ0 = T_K0 + 2 * KN + 0.3                                      # cut to Aren freezing
T0['01'] = T_FRZ0 + 0.3
T_LIGHT = tend('01') - 0.1
T0['02'] = T_LIGHT + 0.35
T_WIDE = ws('02', 0) + 1.1                                        # wide of the dangerous ruin
T_FLAME = ws('02', 1) - 0.05                                       # into the flame
T_MEM = tend('02') + 0.35                                         # the flame transition
T_MK = T_MEM + 1.25                                               # the brother's knocks
T_RUSH = (T_MK + 2 * KN + 0.2, T_MK + 2 * KN + 1.0)
T_POINT = T_RUSH[1] - 0.15
T0['03'] = T_POINT + 0.45
T_HES = (tend('03') + 0.1, tend('03') + 1.6)                      # looks at the passage, back at his brother
T0['04'] = tend('03') + 0.55
T_LEAVE = (ws('04', 1) - 0.2, ws('04', 2) + 0.3)                  # leads them out, looks back
T_PTCU = ws('04', 2) - 0.15                                       # the pointing hand
T_NOW = tend('04') + 0.35                                         # cut: the same passage today
T_CK = T_NOW + 1.05                                               # the child's knocks
T_FRZ = T_CK + 2 * KN + 0.2
T0['05'] = T_FRZ + 0.35
T_FLASH = (ws('05', 1) - 0.65, ws('05', 1) + 0.15)
T_SEE = T_FLASH[1]
T_DIRECT = tend('05') + 0.35                                      # he tries the doorway
T_DIG = (T_DIRECT + 1.25, T_DIRECT + 2.45)
T_SHIFT = T_DIG[1]
T0['06'] = T_SHIFT + 0.8
T_BACK = (T_SHIFT + 0.05, T_SHIFT + 0.75)
T_RUNP = (T_SHIFT + 1.35, T_SHIFT + 3.3)                          # hurries to the passage
T_SET = (T_RUNP[1] + 0.05, T_RUNP[1] + 0.65)                      # kneels, sets the candle on the rock
T_CRAWL = (T_SET[1] + 0.1, T_SET[1] + 1.4)                        # crawls in
T_INSIDE = T_CRAWL[1] - 0.25                                      # cut inside
T_REACH = (T_INSIDE + 0.25, T_INSIDE + 0.85)
T_TAKE = T_INSIDE + 1.15
T_FALL2 = T_TAKE + 0.45                                           # stones crash where the child was
T_PULL = (T_TAKE + 0.35, T_TAKE + 1.3)
T_EXIT = T_PULL[1] - 0.1                                          # cut outside: they come out
T_OUTP = (T_EXIT, T_EXIT + 1.5)
T_COLLAPSE = T_OUTP[1] + 0.1
T_RUNM = (T_COLLAPSE + 0.45, T_COLLAPSE + 1.75)                   # the child runs to the mother
T_HUG = T_RUNM[1]
T_COUT = T_HUG + 1.0                                              # the candle dies
T_TURN = (T_COUT + 0.55, T_COUT + 1.25)
T0['07'] = T_COUT + 2.1
T_END = ws('07', 1) - 0.2                                         # last shot: the dead candle in his hand
DUR = round(tend('07') + 1.3, 2); N = int(round(DUR * FPS))
T_FADE = DUR - 0.9
LINES = [(k, T0[k]) for k in sorted(T0)]

def talking(t, key, rate=6.5):
    if key not in T0: return None
    for a, b, _ in SCR['sent'][key]:
        if T0[key] + a <= t < T0[key] + b: return 'open' if (t * rate + 0.2 * math.sin(t * 13)) % 1.0 < 0.55 else 'soft'
    return None

# ======================= shots: (start, name) =======================
SHOTS = [(0.0, 'hook'), (T_FRZ0, 'freeze0'), (T_LIGHT - 0.55, 'light'), (T_WIDE, 'wide0'), (T_FLAME, 'flame'),
         (T_MEM, 'm_est'), (T_MK - 0.25, 'm_knock'), (T_RUSH[0], 'm_point'), (T0['03'] + 0.15, 'm_face'), (tend('03') + 0.05, 'm_hes'),
         (T_LEAVE[0], 'm_leave'), (T_PTCU, 'm_hand'),
         (T_NOW, 'p_match'), (T_CK - 0.12, 'p_knock'), (T_FRZ - 0.05, 'p_freeze'), (T_FLASH[0], 'flash'), (T_FLASH[1], 'p_see'),
         (T_DIRECT, 'p_direct'), (T_RUNP[0] + 0.9, 'p_pass'), (T_INSIDE, 'p_inside'), (T_EXIT, 'p_exit'),
         (T_RUNM[0], 'h_run'), (T_COUT - 0.75, 'h_candle'), (T_COUT + 0.45, 'h_turn'), (T0['07'] + 0.2, 'h_two'), (T_END, 'h_end')]
def shot_at(t):
    nm = SHOTS[0][1]
    for a, n in SHOTS:
        if t >= a: nm = n
    return nm
MEMSHOTS = {'m_est', 'm_knock', 'm_point', 'm_face', 'm_hes', 'm_leave', 'm_hand', 'flash'}
HANDW = None
INSIDE_NOW = {'hook', 'p_match', 'p_knock', 'p_inside'}
def era(sh): return 'mem' if sh in MEMSHOTS else ('in' if sh in INSIDE_NOW else 'out')

# ======================= set pieces =======================
def rock(c, r, col=(96, 92, 88), seed=0, flat_=0.6, R=None):
    def d(p): k = 1 + 0.2 * math.sin(p[0] * 31 + seed) * math.cos(p[2] * 23 + seed * 2); return p * k
    return hd.ellip(c, hd.Ry(seed) if R is None else R, (r, r * flat_, r * 0.9), 8, 5, col, deform=d, colfn=lambda i, j, cl: hd.shade(col, 0.82 + 0.25 * hsh(i * 13 + j, seed)))
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
        if abs(wrap(phi0 - 1.1)) < 0.5: top -= 1.6 * (1 - abs(wrap(phi0 - 1.1)) / 0.5)
        for j in range(int(top / ch)):
            y = j * ch; ph = phi0 + (dph / 2 if j % 2 else 0)
            if abs(wrap(ph - PHI_DOOR)) < 0.2 and y < 2.0: continue
            if abs(wrap(ph - PHI_PASS)) < PH_W and y < PH_H: continue
            if abs(wrap(ph - PHI_PASS)) < 0.2 and PH_H <= y < PH_H + 0.3: continue        # room for the (falling) lintel
            rm = (R_IN + R_OUT) / 2; c = ring_pt(ph, rm, y + ch / 2)
            col = hd.shade(ST[(i * 3 + j) % 4], 0.84 + 0.24 * hsh(i * 17 + j, 5))
            if y > top - ch * 1.5 and hsh(i, j) < 0.35: continue
            if 1.2 < y < 3.0 and hsh(i * 7, j) < 0.05: col = (40, 38, 40)                     # cracks
            Q += hd.bx(c, hd.Ry(ph), (rm * dph / 2 - 0.012, ch / 2 - 0.01, (R_OUT - R_IN) / 2), col)
    for s in (-1, 1):
        c = ring_pt(PHI_DOOR + s * 0.1, R_OUT - 0.22, 2.14 + 0.04 * (s < 0))
        Q += hd.bx(c, hd.Ry(PHI_DOOR) @ hd.Rz(0.06 * s), (0.31, 0.12, 0.26), (110, 104, 96))
    Q += [hd.face([ring_pt(PHI_DOOR - 0.2, R_OUT - 0.3, 0), ring_pt(PHI_DOOR - 0.2, R_OUT - 0.3, 2.0), ring_pt(PHI_DOOR + 0.2, R_OUT - 0.3, 2.0), ring_pt(PHI_DOOR + 0.2, R_OUT - 0.3, 0)], (8, 8, 12))]
    for s in (-1, 1):                                                                              # side walls of the passage
        Q += [hd.face([ring_pt(PHI_PASS + s * PH_W, R_OUT, 0), ring_pt(PHI_PASS + s * PH_W, R_OUT, PH_H), ring_pt(PHI_PASS + s * PH_W, R_IN, PH_H), ring_pt(PHI_PASS + s * PH_W, R_IN, 0)], (44, 42, 46))]
    Q += [hd.face([ring_pt(PHI_PASS - PH_W, R_OUT, PH_H), ring_pt(PHI_PASS + PH_W, R_OUT, PH_H), ring_pt(PHI_PASS + PH_W, R_IN, PH_H), ring_pt(PHI_PASS - PH_W, R_IN, PH_H)], (36, 34, 38))]
    for i in range(-6, 6):
        for j in range(-6, 6):
            x, z = TC[0] + i * 0.42, TC[2] + j * 0.42
            if math.hypot(x + 0.21 - TC[0], z + 0.21 - TC[2]) > R_IN + 0.1: continue
            Q.append(hd.face([(x + 0.01, 0.004, z + 0.01), (x + 0.01, 0.004, z + 0.41), (x + 0.41, 0.004, z + 0.41), (x + 0.41, 0.004, z + 0.01)], hd.shade(ST[(i + j) % 4], 0.6 + 0.2 * hsh(i * 7 + j, 9))))
    return [q for q in Q if q]
def outside_set():
    Q = ground(-12, 12, -14, 16, 0.8, [(58, 62, 52), (52, 56, 48), (64, 64, 54), (48, 50, 46)], seed=3)
    Q += hd.ellip(MOUND, hd.Ry(PHI_DOOR), (1.15, 0.98, 0.82), 12, 6, (92, 88, 84), colfn=lambda i, j, cl: hd.shade((96, 92, 86), 0.8 + 0.3 * hsh(i * 5 + j, 2)))
    for i in range(14):
        a = hsh(i, 4) * PI - PI / 2; rr = 0.5 + 0.4 * hsh(i, 5)
        c = MOUND + hd.Ry(PHI_DOOR) @ V((rr * math.sin(a) * 1.1, 0, rr * math.cos(a) * 0.6)) + V((0, 0.98 * math.sqrt(max(0.05, 1 - rr * rr)), 0))
        if np.linalg.norm(c - DIG) < 0.25: continue
        Q += rock(c, 0.13 + 0.1 * hsh(i, 6), seed=i + 3)
    Q += rock(PASS_OUT + OUTD * 0.15 - PERP * 0.62, 0.22, seed=40) + rock(RK, 0.19, (104, 100, 96), seed=41, flat_=0.6)
    for i in range(18):
        a = hsh(i, 7) * 2 * PI; r = 3.3 + 2.5 * hsh(i, 8); c = TC + V((r * math.sin(a), 0.1, r * math.cos(a)))
        bad = [PASS_OUT, A0, CROUCH, M0, HUGP, C_ST, MF]
        if min(np.linalg.norm((c - b)[[0, 2]]) for b in bad) < 1.3: continue
        Q += hd.bx(c, hd.Ry(a) @ hd.Rz(0.2 * hsh(i, 9)), (0.22, 0.12, 0.17), ST[i % 4])
    Q += tree_dead(-5.5, 7.0, 3.4, seed=2) + tree_dead(5.2, 9.0, 3.0, seed=5)
    for i in range(7): x = -36 + 12 * i; Q += hd.ellip((x, -3, 40), np.eye(3), (10, 7 + 3 * hsh(i, 2), 3), 10, 5, (36, 42, 52))
    for i in range(6): x = -30 + 12 * i; Q += hd.ellip((x, -3, -42), np.eye(3), (10, 6 + 3 * hsh(i, 3), 3), 10, 5, (44, 46, 58))
    # from outside the passage reads dark: a dark plate just inside the inner mouth
    Q += [hd.face([ring_pt(PHI_PASS - PH_W, R_IN - 0.02, 0), ring_pt(PHI_PASS - PH_W, R_IN - 0.02, PH_H), ring_pt(PHI_PASS + PH_W, R_IN - 0.02, PH_H), ring_pt(PHI_PASS + PH_W, R_IN - 0.02, 0)], (5, 5, 8), emit=True)]
    return [q for q in Q if q]
def outer_light(col):
    """seen from inside: the passage opens on the moonlit outside (safety)"""
    return [q for q in [hd.face([ring_pt(PHI_PASS - PH_W, R_OUT + 0.02, 0), ring_pt(PHI_PASS - PH_W, R_OUT + 0.02, PH_H), ring_pt(PHI_PASS + PH_W, R_OUT + 0.02, PH_H), ring_pt(PHI_PASS + PH_W, R_OUT + 0.02, 0)], col, emit=True)] if q]
def memory_set():
    Q = []
    a = BEAM_C - PERPM * 1.5 + V((0, 0.12, 0)); b = BEAM_C + PERPM * 1.4 + V((0, 0.95, 0))
    Q += hd.limb(a, b, 0.13, 0.12, (92, 62, 40), n=8, m=3)
    Q += hd.limb(BEAM_C + PERPM * 1.3 + V((0, 0.9, 0)), BEAM_C + PERPM * 1.2 + DIRM * 0.6 + V((0, 3.2, 0)), 0.09, 0.08, (84, 56, 36), n=7, m=2)
    for i in range(22):
        u = hsh(i, 3) * 2.4 - 1.2; v = hsh(i, 4) * 0.9
        c = BEAM_C + PERPM * u + DIRM * (0.15 + v) + V((0, 0.12 + 0.4 * (1 - abs(u) / 1.2) * hsh(i, 5), 0))
        if np.linalg.norm((c - BR)[[0, 2]]) < 0.45: continue
        Q += rock(c, 0.12 + 0.13 * hsh(i, 6), seed=i + 50)
    Q += hd.bx(SLAB - V((0, 0.2, 0)), hd.Ry(ang_to(BR, PASS_IN)), (0.22, 0.2, 0.16), (122, 118, 110))
    Q += hd.bx(MEMC - V((0, 0.08, 0)), np.eye(3), (0.12, 0.08, 0.12), (110, 106, 100))
    return [q for q in Q if q]
def inside_now_set():
    """today, inside: the child's pocket under a fallen beam; the doorway blocked from inside"""
    Q = []
    tw = flat(PASS_IN - CH); sd = V((tw[2], 0, -tw[0]))
    Q += hd.limb(CH - tw * 0.35 + sd * 0.9 + V((0, 0.05, 0)), CH - tw * 0.25 - sd * 0.8 + V((0, 1.05, 0)), 0.12, 0.11, (70, 56, 44), n=8, m=3)
    for i in range(18):
        a = hsh(i, 2) * 2 * PI; r = 0.55 + 0.6 * hsh(i, 3); c = CH - tw * 0.6 + V((r * math.sin(a), 0.1 + 0.2 * hsh(i, 4), r * math.cos(a) * 0.6))
        if np.linalg.norm((c - CH)[[0, 2]]) < 0.42: continue
        Q += rock(c, 0.12 + 0.12 * hsh(i, 5), (100, 98, 96), seed=i + 90)
    Q += hd.ellip(DOOR_IN - DOOR_DIR * 0.5, hd.Ry(PHI_DOOR), (1.2, 1.1, 0.9), 12, 6, (86, 84, 82))
    Q += hd.bx(KNOCKST - V((0, 0.17, 0)), hd.Ry(ang_to(CH, PASS_IN)), (0.18, 0.17, 0.12), (120, 116, 110))
    return [q for q in Q if q]
_SETS = {}
def get_set(name):
    if name not in _SETS: _SETS[name] = {'tower': tower_set, 'out': outside_set, 'mem': memory_set, 'innow': inside_now_set}[name]()
    return _SETS[name]

# ======================= props =======================
def candle(base, lit=1.0, t=0.0, smoke=0.0, seed=0):
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
def candle_state(t):
    if t < T_LIGHT + 0.15: return 0.0, 0.0
    if t < T_COUT - 0.55: return seg01(t, T_LIGHT + 0.15, T_LIGHT + 0.5), 0.0
    if t < T_COUT:
        u = seg01(t, T_COUT - 0.55, T_COUT); return (1 - u * 0.6) * (0.55 + 0.45 * abs(math.sin(t * 23))), 0.0
    return 0.0, max(0.0, 1.0 - seg01(t, T_COUT + 0.1, T_COUT + 3.5))
def puff(c, t, t0, d=1.2, n=10, r=0.6, col=(120, 116, 112), s0=0.06):
    if not (t0 < t < t0 + d): return []
    u = seg01(t, t0, t0 + d); Q = []
    for i in range(n):
        a = 2 * PI * i / n + hsh(i, 1); rr = 0.1 + r * u * (0.6 + 0.4 * hsh(i, 2)); p = V(c, float) + V((rr * math.cos(a), 0.05 + 0.5 * u * hsh(i, 3), rr * math.sin(a)))
        s = s0 * (1 - u) + 0.015
        Q.append(hd.face([p + V((-s, 0, 0)), p + V((0, s, 0)), p + V((s, 0, 0)), p + V((0, -s, 0))], col, emit=True))
    return [q for q in Q if q]
def falling(t, t0, top, land, size=0.1, d=0.5, seed=0, col=(116, 110, 102)):
    """a stone falling from top to land at t0..t0+d, then lying there"""
    if t < t0 - 0.05: return []
    u = seg01(t, t0, t0 + d); c = V(lerp3(top, land, u * u)); R = hd.Rx(u * 3 + seed) @ hd.Rz(u * 2)
    return hd.bx(c, R, (size, size * 0.75, size * 0.85), col)
DEBRIS_OUT = [(1.1 + 3.1 * k + 0.9 * hsh(k, 3), PI * 2 * hsh(k, 4)) for k in range(18)]
def debris_out(t):
    """small stones keep falling off the ruin (it is dangerous)"""
    Q = []
    for k, (t0, ph) in enumerate(DEBRIS_OUT):
        if t0 - 0.05 < t < t0 + 1.6:
            top = ring_pt(ph, R_OUT + 0.05, 3.6 + hsh(k, 5)); land = ring_pt(ph, R_OUT + 0.4 + 0.4 * hsh(k, 6), 0.06)
            Q += falling(t, t0, top, land, 0.05 + 0.03 * hsh(k, 7), 0.6, k)
            if t > t0 + 0.6: Q += puff(land, t, t0 + 0.6, 0.8, 6, 0.3, s0=0.03)
    return Q
DEBRIS_MEM = [(T_MEM + 0.4 + 1.3 * k + 0.5 * hsh(k, 9), k) for k in range(12)]
def debris_mem(t):
    Q = []
    for t0, k in DEBRIS_MEM:
        if t0 - 0.05 < t < t0 + 1.3:
            p = BEAM_C + PERPM * (hsh(k, 1) * 2.4 - 1.2) + DIRM * (hsh(k, 2) * 1.2 - 0.6)
            Q += falling(t, t0, p + V((0, 3.2, 0)), p + V((0, 0.08, 0)), 0.05 + 0.04 * hsh(k, 3), 0.6, k, (130, 110, 90))
            if t > t0 + 0.6: Q += puff(p, t, t0 + 0.6, 0.7, 6, 0.3, (200, 160, 120), 0.03)
    return Q
def dust_faces(t, centre, n=40, col=(255, 214, 150)):
    Q = []
    for i in range(n):
        c = centre + PERPM * (hsh(i, 1) * 3 - 1.5) + DIRM * (hsh(i, 2) * 3 - 1.8) + V((0.1 * math.sin(t * 0.4 + i), 0.3 + 2.2 * hsh(i, 3) - (t * 0.12 + hsh(i, 5)) % 1.0 * 0.4, 0))
        s = 0.006 + 0.006 * hsh(i, 4)
        Q.append(hd.face([c + V((-s, 0, 0)), c + V((0, s, 0)), c + V((s, 0, 0)), c + V((0, -s, 0))], col, emit=True))
    return [q for q in Q if q]
def lintel(t, collapse=True):
    """the passage lintel: falls and blocks the passage after the escape"""
    base = ring_pt(PHI_PASS, (R_IN + R_OUT) / 2, PH_H + 0.1)
    if not collapse or t < T_COLLAPSE: return hd.bx(base, hd.Ry(PHI_PASS), (0.42, 0.09, 0.27), (100, 96, 90))
    u = seg01(t, T_COLLAPSE, T_COLLAPSE + 0.3)
    Q = hd.bx(base - V((0, 0.42 * u * u, 0)) + OUTD * 0.1 * u, hd.Ry(PHI_PASS) @ hd.Rz(0.35 * u), (0.42, 0.09, 0.27), (100, 96, 90))
    for k in range(6):
        top = ring_pt(PHI_PASS + (hsh(k, 1) - 0.5) * 0.25, R_OUT + 0.05, 1.3 + 0.8 * hsh(k, 2))
        land = PASS_OUT + OUTD * (0.15 + 0.35 * hsh(k, 3)) + PERP * (hsh(k, 4) - 0.5) * 0.6 + V((0, 0.1, 0))
        Q += falling(t, T_COLLAPSE + 0.08 * k, top, land, 0.1 + 0.04 * hsh(k, 5), 0.4, k + 30)
    Q += puff(PASS_OUT + OUTD * 0.3, t, T_COLLAPSE + 0.25, 1.8, 14, 1.0, s0=0.08)
    return Q
def shift_faces(t):
    """the doorway rubble shifts: stones slide down the mound at him, the lintel sags"""
    Q = []
    for k in range(7):
        a = (hsh(k, 1) - 0.5) * 1.2; st = MOUND + hd.Ry(PHI_DOOR) @ V((a * 0.7, 0.9, 0.25)); en = MOUND + DOOR_DIR * (1.0 + 0.3 * hsh(k, 2)) + hd.Ry(PHI_DOOR) @ V((a, 0.1, 0))
        if t < T_SHIFT - 0.1: continue
        u = seg01(t, T_SHIFT + 0.05 * k, T_SHIFT + 0.05 * k + 0.55); c = V(lerp3(st, en, sm(u))) + V((0, 0.15 * math.sin(PI * u), 0))
        Q += rock(c, 0.1 + 0.05 * hsh(k, 3), (106, 102, 96), seed=k + 70)
    if t >= T_SHIFT - 0.05:
        Q += puff(MOUND + DOOR_DIR * 0.9 + V((0, 0.3, 0)), t, T_SHIFT, 1.8, 14, 1.0, s0=0.09)
        sag = sm(seg01(t, T_SHIFT, T_SHIFT + 0.4))
        Q += hd.bx(ring_pt(PHI_DOOR, R_OUT + 0.05, 2.05 - 0.6 * sag), hd.Ry(PHI_DOOR) @ hd.Rz(0.4 * sag), (0.5, 0.11, 0.2), (98, 94, 88))
    return Q
def dig_stone(t):
    if t < T_DIG[0] + 0.35: c = DIG
    elif t < T_SHIFT: c = DIG + DOOR_DIR * 0.12 * (0.5 + 0.5 * math.sin((t - T_DIG[0]) * 9))
    else: c = DIG + DOOR_DIR * 0.12
    return rock(c, 0.13, (110, 106, 100), seed=88)

# ======================= pose helpers =======================
def wpt(P, l): return V(P['base'], float) + hd.Ry(P['yaw']) @ V(l, float)
def loc(base, yaw, p): return tuple(hd.Ry(yaw).T @ (V(p, float) - V(base, float)))
def head_to(P, tgt, k=1.0): a = wrap(ang_to(P['base'], tgt) - P['yaw']); return max(-1.1, min(1.1, a)) * k
def kneel(P, front='r', drop=0.43):
    b = 'l' if front == 'r' else 'r'; s = 1 if front == 'r' else -1
    P.update(crouch=drop); P[front + 'f'] = (s * 0.14, 0.07, 0.33); P[b + 'f'] = (-s * 0.13, 0.06, -0.52); P[b + 'kpole'] = (0, -0.8, 1.0)
    P[b + 'fdir'] = None; return P
def crawl(P, ph=0.0, u=1.0):
    """on hands and knees (u blends from kneeling), phase ph shuffles the limbs"""
    P.update(crouch=lerp(0.43, 0.6, u), lean=lerp(0.25, 1.15, u), nod=lerp(0.0, -0.75, u))
    sw = 0.06 * math.sin(ph)
    P['rf'] = (0.12, 0.07, -0.55 + sw); P['lf'] = (-0.12, 0.07, -0.55 - sw); P['rkpole'] = (0, -1.0, 0.4); P['lkpole'] = (0, -1.0, 0.4)
    P['rfdir'] = None; P['lfdir'] = None
    P['rh'] = (0.17, 0.04 + 0.03 * max(0, math.sin(ph)), 0.5 - sw); P['lh'] = (-0.17, 0.04 + 0.03 * max(0, -math.sin(ph)), 0.5 + sw)
    P['rpalm'] = P['lpalm'] = (0, -1.0, 0.0); P['rgrip'] = P['lgrip'] = 0.2
    return P
HOLD = (-0.07, 1.2, 0.3)
def hold_base(P, key='l'): return P['_' + key + 'wrist'] + P['_' + key + 'dir'] * 0.075 + P['_' + key + 'palm'] * 0.028

# ======================= Aren (present, outside) =======================
def aren(t):
    """returns pose, and where the candle is ('hand' or 'rock')"""
    P = dict(base=tuple(A0), yaw=YAW0, eyes='open', mouth='neutral', brow=-0.3, lean=0.03, cape_sway=0.15 * math.sin(t * 1.3))
    P['lh'] = HOLD; P['lgrip'] = 0.55; P['lpalm'] = (0.0, 1.0, 0.15); where = 'hand'
    if t < T_MEM:
        fr = sm(seg01(t, T_FRZ0, T_FRZ0 + 0.25))
        if t < T_FRZ0 + 0.1:                                                        # walking past when the knocks come
            P['base'] = tuple(A0 + V((-0.5, 0, -0.3)) * (1 - seg01(t, 0, T_FRZ0 + 0.1))); P['walk'] = t * 6
        P['yaw'] = angl(YAW0 - 0.6, YAW0, fr)
        if T_FRZ0 <= t < T_LIGHT - 0.4: P['eyes'] = 'wide'; P['brow'] = 0.15; P['lean'] = -0.06; P['mouth'] = 'o' if t < T_FRZ0 + 1.2 else 'neutral'
        lt = win(t, T_LIGHT - 0.45, T_LIGHT + 0.6, 0.25)
        if lt > 0:
            P['rh'] = lerp3((0.2, 0.9, 0.1), (0.03, 1.31, 0.34), lt); P['rgrip'] = 0.85; P['rpalm'] = (-1.0, 0.0, 0.2)
        if t > T_LIGHT - 0.45: P['nod'] = 0.3; P['eyes'] = 'half' if t > T_LIGHT + 0.3 else 'open'; P['brow'] = -0.6; P['mouth'] = 'soft'
        if t > T_FLAME: P['nod'] = 0.35; P['eyes'] = 'sad'
        return P, where
    P['nod'] = 0.1
    if t < T_DIRECT:
        if T_CK - 0.05 <= t: P['eyes'] = 'wide'; P['brow'] = 0.2; P['nod'] = -0.05; P['lean'] = -0.05
        if T_CK + 0.05 <= t < T_FLASH[0]: P['head'] = (0.0, -0.06 * sm(seg01(t, T_CK, T_CK + 0.2)), 0.0); P['mouth'] = 'o'
        if t >= T_SEE:                                                              # turns his head: the passage
            u = sm(seg01(t, T_SEE, T_SEE + 0.4)); P['head'] = (head_to(P, PASS_OUT) * u, 0.0, 0.0); P['eyes'] = 'open'; P['brow'] = -0.5; P['mouth'] = 'neutral'
        return P, where
    if t < T_SHIFT:                                                                 # the direct route: to the doorway, digs
        u = seg01(t, T_DIRECT, T_DIG[0]); P['base'] = lerp3(A0, MF, sm(u)); P['yaw'] = angl(YAW0, ang_to(A0, MF), sm(seg01(t, T_DIRECT, T_DIRECT + 0.3)))
        if u < 1: P['walk'] = sm(u) * 11; P['stride'] = 0.36; P['lean'] = 0.15; P['brow'] = 0.3
        else:
            P['yaw'] = ang_to(MF, DIG)
            P['rh_w'] = tuple(DIG + V((0, 0.1, 0)) - DOOR_DIR * (-0.02 + 0.1 * (0.5 + 0.5 * math.sin((t - T_DIG[0]) * 9)))); P['rgrip'] = 0.8; P['rpalm'] = (0, -1.0, 0)
            P['lean'] = 0.35; P['brow'] = 0.8; P['mouth'] = 'grit'; P['crouch'] = 0.12
        return P, where
    if t < T_RUNP[0]:                                                               # the rubble shifts: thrown back
        u = sm(seg01(t, *T_BACK)); bk = MF + DOOR_DIR * 0.75
        P['base'] = lerp3(MF, bk, u); P['yaw'] = ang_to(MF, DIG)
        if u < 1: P['walk'] = -u * 5; P['stride'] = 0.3
        P['lean'] = -0.15 * u; P['eyes'] = 'wide'; P['brow'] = 0.4; P['mouth'] = 'o'
        P['rh'] = lerp3((0.2, 0.9, 0.1), (0.05, 1.5, 0.32), win(t, T_SHIFT, T_RUNP[0], 0.15)); P['rgrip'] = 0.4; P['rpalm'] = (0, 0, 1.0)
        if t > T_BACK[1] + 0.1: P['head'] = (head_to(P, PASS_OUT) * sm(seg01(t, T_BACK[1] + 0.1, T_RUNP[0])), 0.0, 0.0); P['brow'] = -0.2
        return P, where
    if t < T_SET[0]:                                                                # hurries to the passage
        u = seg01(t, *T_RUNP); us = sm(u) * 0.5 + u * 0.5; bk = MF + DOOR_DIR * 0.75
        P['base'] = lerp3(bk, CROUCH, us); P['yaw'] = ang_to(bk, CROUCH); P['walk'] = us * 24; P['stride'] = 0.45; P['lift'] = 0.14; P['lean'] = 0.2
        P['lh'] = (-0.12, 1.05, 0.3)
        if u > 0.85: P['yaw'] = angl(P['yaw'], ang_to(CROUCH, PASS_OUT), sm(seg01(u, 0.85, 1.0)))
        return P, where
    P['base'] = tuple(CROUCH); P['yaw'] = ang_to(CROUCH, PASS_OUT)
    if t < T_CRAWL[0]:                                                              # kneels, sets the candle on the rock
        kneel(P, 'l', 0.43 * sm(seg01(t, T_SET[0], T_SET[0] + 0.3))); P['lean'] = 0.3
        u = sm(seg01(t, T_SET[0] + 0.15, T_SET[1]))
        P['lh_w'] = tuple(lerp3(wpt(P, HOLD), CANDLE_ON_ROCK + V((0.0, 0.03, 0)), u)); P['lpalm'] = (0, 1.0, 0)
        P['head'] = (head_to(P, RK) * u, 0.3 * u, 0.0)
        if u > 0.98: where = 'rock'
        return P, where
    where = 'rock'
    if t < T_EXIT:                                                                  # crawls into the passage
        u = seg01(t, *T_CRAWL); a = CROUCH; m = PASS_OUT + OUTD * 0.85; b = PASS_IN + DIRM * 0.25
        pth = lerp3(a, m, min(1, u * 2.5)) if u < 0.4 else lerp3(m, b, (u - 0.4) / 0.6)
        P['base'] = tuple(pth); P['yaw'] = ang_to(PASS_OUT, PASS_IN); crawl(P, u * 18, min(1.0, u * 4))
        P['brow'] = 0.3; P['eyes'] = 'open'
        return P, where
    u = sm(seg01(t, T_OUTP[0], T_OUTP[0] + 1.0)); a = PASS_OUT - OUTD * 0.05; b = AEND       # backs out with the child
    P['base'] = lerp3(a, b, u); P['yaw'] = ang_to(PASS_OUT, PASS_IN)
    if u < 1: crawl(P, u * 12, 1.0 - 0.6 * u)
    else: kneel(P, 'l', 0.43); P['lean'] = 0.2
    P['rh_w'] = tuple(child_hand(t) + V((0, 0.02, 0))); P['rgrip'] = 0.55; P['rpalm'] = (0, 1.0, 0)
    P['lh'] = (-0.2, 0.75, 0.25)
    rel = sm(seg01(t, T_RUNM[0] - 0.2, T_RUNM[0] + 0.2))
    if rel > 0:
        P.pop('rh_w'); P['rh'] = (0.22, 0.6, 0.25); kneel(P, 'l', 0.43); P['lean'] = 0.2
        P['yaw'] = angl(ang_to(PASS_OUT, PASS_IN), ang_to(b, HUGP), sm(seg01(t, T_RUNM[0], T_RUNM[1])))
        P['eyes'] = 'half'; P['brow'] = -0.3; P['mouth'] = 'neutral'
    if t > T_HUG: P['mouth'] = 'soft'
    tu = win(t, T_TURN[0], T0['07'] + 0.2, 0.35)                                    # the candle dies: he turns, as if to hear his brother
    if tu > 0: P['head'] = (head_to(P, PASS_OUT) * tu, -0.05 * tu, 0.0); P['eyes'] = 'open'; P['brow'] = -0.7; P['mouth'] = 'neutral'
    if t > T0['07'] + 0.2:                                                          # picks the dead candle up
        g = sm(seg01(t, T0['07'] + 0.3, T0['07'] + 1.0))
        P['lh_w'] = tuple(lerp3(CANDLE_ON_ROCK + V((0, 0.03, 0)), wpt(P, (-0.1, 1.05, 0.32)), g)); P['lpalm'] = (0, 1.0, 0); P['lgrip'] = 0.5
        P['head'] = (head_to(P, HUGP) * 0.4 * (1 - g), 0.35 * g, 0.0); P['eyes'] = 'sad' if g < 1 else 'half'; P['brow'] = -0.5
        if g > 0.05: where = 'hand'
        if t > ws('07', 1) + 0.6: P['mouth'] = 'smile'; P['brow'] = -0.2
    return P, where
def aren_inside(t):
    """inside: crawls out of the inner mouth, reaches, takes the child's hand, pulls back"""
    P = dict(base=tuple(PASS_IN + DIRM * 0.25), yaw=ang_to(PASS_OUT, PASS_IN), eyes='open', mouth='neutral', brow=0.4)
    u = seg01(t, T_INSIDE, T_REACH[0]); P['base'] = lerp3(PASS_IN - DIRM * 0.15, PASS_IN + DIRM * 0.4, sm(u))
    crawl(P, u * 8, 1.0)
    r = sm(seg01(t, *T_REACH))
    if r > 0:
        hp = child_hand(t) if t >= T_TAKE else lerp3(wpt(P, (0.17, 0.05, 0.5)), V(CH) + flat(PASS_IN - CH) * 0.45 + V((0, 0.25, 0)), r)
        P['rh_w'] = tuple(V(hp) + V((0, 0.02, 0))); P['rgrip'] = 0.5 if t >= T_TAKE else 0.15; P['rpalm'] = (0, 1.0, 0) if t >= T_TAKE else (0, 0.3, 1.0)
        P['lean'] = 0.95
    if t > T_PULL[0]:
        b = sm(seg01(t, *T_PULL)); P['base'] = lerp3(PASS_IN + DIRM * 0.4, PASS_IN - DIRM * 0.3, b)
    return P

# ======================= the child, the mother =======================
def child_hand(t):
    if t < T_EXIT:
        a = V(CH) + flat(PASS_IN - CH) * 0.45 + V((0, 0.25, 0)); b = PASS_IN + DIRM * 0.25 + V((0, 0.3, 0))
        return V(lerp3(a, b, sm(seg01(t, *T_PULL))))
    u = sm(seg01(t, T_OUTP[0], T_OUTP[1])); a = PASS_OUT + V((0, 0.32, 0)); b = C_ST + flat(CROUCH - C_ST) * 0.32 + V((0, 0.62, 0))
    return V(lerp3(a, b, u))
def child_inside(t):
    tw = flat(PASS_IN - CH)
    P = dict(base=tuple(CH), yaw=ang_to(CH, PASS_IN), eyes='wide', mouth='o', brow=0.4, crouch=0.45, lean=0.25)
    P['rf'] = (0.12, 0.07, 0.3); P['lf'] = (-0.12, 0.07, 0.25); P['rkpole'] = (0.1, 1, 0.4); P['lkpole'] = (-0.1, 1, 0.4)
    kn = loc(CH, P['yaw'], KNOCKST + V((0, 0.03, 0)))
    ph = 0.0
    for t0 in (T_K0, T_CK):
        for k in range(3):
            if abs(t - (t0 + k * KN)) < 0.19: ph = max(ph, 1 - abs(t - (t0 + k * KN)) / 0.19)
    lift = 0.08 * (1 - ph)
    P['rh'] = (kn[0], kn[1] + 0.02 + 1.6 * lift, kn[2]); P['rgrip'] = 0.95; P['rpalm'] = (0, -1.0, 0); P['lh'] = (-0.14, 0.42, 0.18); P['lgrip'] = 0.4
    if t > T_INSIDE:                                                                # crawls towards Aren, takes his hand
        r = sm(seg01(t, T_INSIDE + 0.3, T_TAKE))
        P['base'] = lerp3(CH, CH + tw * 0.2, r); crawl(P, r * 6, r * 0.8)
        P['crouch'] = 0.38; P['nod'] = -0.5 * r
        P['rh_w'] = tuple(child_hand(t)); P['rgrip'] = 0.55; P['rpalm'] = (0, -1.0, 0)
        if t > T_PULL[0]:
            b = sm(seg01(t, *T_PULL)); P['base'] = lerp3(CH + tw * 0.2, PASS_IN + DIRM * 0.7, b)
    return P
def child_out(t):
    if t < T_EXIT: return None
    if t < T_RUNM[0] - 0.2:
        u = sm(seg01(t, T_OUTP[0] + 0.15, T_OUTP[1])); a = PASS_IN + DIRM * 0.2; b = C_ST
        P = dict(base=tuple(lerp3(a, b, u)), yaw=ang_to(PASS_IN, PASS_OUT), eyes='wide', mouth='o', brow=0.3)
        cr = 1 - sm(seg01(t, T_OUTP[1] - 0.5, T_OUTP[1] + 0.1)); crawl(P, u * 10, cr)
        P['crouch'] = 0.38 * cr; P['lean'] = 1.0 * cr + 0.05
        if cr < 0.05:
            for k_ in ('rf', 'lf', 'rh', 'lh', 'rkpole', 'lkpole'): P.pop(k_, None)
            P['nod'] = 0.0
        P['rh_w'] = tuple(child_hand(t)); P['rgrip'] = 0.55; P['rpalm'] = (0, -1.0, 0)
        if t > T_COLLAPSE: P['head'] = (0.9 * win(t, T_COLLAPSE, T_RUNM[0], 0.15), 0.0, 0.0)
        return P
    r = seg01(t, *T_RUNM); ur = sm(r) * 0.5 + r * 0.5; end = HUGP
    P = dict(base=tuple(lerp3(C_ST, end, ur)), yaw=ang_to(C_ST, M0), eyes='open', mouth='open', brow=0.2, lean=0.15)
    if r < 1: P['walk'] = ur * 16; P['stride'] = 0.3; P['lift'] = 0.12
    if t > T_HUG - 0.2:
        P['base'] = tuple(end); M = mother(t); hd.human(MOTHER, M)
        sh_l = M['_chest'] + M['_RW'] @ V((-0.15, 0.06, 0.02)); sh_r = M['_chest'] + M['_RW'] @ V((0.15, 0.06, 0.02))
        P['lh_w'] = tuple(sh_r + V((0, 0.03, 0))); P['rh_w'] = tuple(sh_l + V((0, 0.03, 0))); P['lgrip'] = P['rgrip'] = 0.35
        P['eyes'] = 'closed'; P['mouth'] = 'neutral'; P['lean'] = 0.1; P.pop('walk', None)
    return P
MKNEEL = M0 + flat(C_ST - M0) * 0.12
def mother(t):
    P = dict(base=tuple(M0), yaw=ang_to(M0, TC), eyes='open', mouth='neutral', brow=-0.7, lean=0.0)
    P['rh'] = (0.06, 1.1, 0.22); P['lh'] = (-0.06, 1.08, 0.22); P['rgrip'] = P['lgrip'] = 0.5
    if T_SHIFT < t < T_RUNM[0]: P['eyes'] = 'wide'; P['mouth'] = 'o'; P['rh'] = (0.05, 1.32, 0.25); P['lh'] = (-0.05, 1.3, 0.25)
    if t >= T_COLLAPSE + 0.2: P['yaw'] = angl(P['yaw'], ang_to(M0, C_ST), sm(seg01(t, T_COLLAPSE + 0.2, T_COLLAPSE + 0.6)))
    if t >= T_RUNM[0]:
        r = sm(seg01(t, T_RUNM[0], T_HUG)); P['base'] = lerp3(M0, MKNEEL, r)
        P['eyes'] = 'open'; P['mouth'] = 'open'; P['brow'] = -0.4
        P['rh'] = lerp3((0.06, 1.1, 0.22), (0.3, 1.0, 0.45), r); P['lh'] = lerp3((-0.06, 1.08, 0.22), (-0.3, 1.0, 0.45), r); P['rgrip'] = P['lgrip'] = 0.15
    if t >= T_HUG - 0.3:
        kn = sm(seg01(t, T_HUG - 0.3, T_HUG + 0.15)); P['base'] = tuple(MKNEEL); kneel(P, 'r', 0.5 * kn); P['lean'] = 0.15
        cb = HUGP + V((0, 0.62, 0)); away = flat(cb - MKNEEL); side = V((away[2], 0, -away[0]))
        P['rh_w'] = tuple(cb + away * 0.14 + side * 0.17); P['lh_w'] = tuple(cb + away * 0.14 - side * 0.17); P['rgrip'] = P['lgrip'] = 0.3
        P['eyes'] = 'closed'; P['mouth'] = 'smile' if t > T_HUG + 0.6 else 'o'; P['brow'] = -0.5; P['nod'] = 0.15
    return P

# ======================= memory people =======================
MEM_PT = T_POINT + 0.6                                            # the reference moment of the pointing composition (flash insert)
def bro(t):
    P = dict(base=tuple(BR), yaw=ang_to(BR, PASS_IN), eyes='open', mouth='neutral', brow=-0.3, lean=0.15)
    kneel(P, 'r', 0.5)
    sl = loc(BR, P['yaw'], SLAB + V((0, 0.12, 0)))
    if t < T_POINT:
        ph = 0.0
        for k in range(3):
            tk = T_MK + k * KN
            if abs(t - tk) < 0.19: ph = max(ph, 1 - abs(t - tk) / 0.19)
        lift = 0.09 * (1 - ph) if t < T_MK + 2 * KN + 0.1 else 0.09
        P['rh'] = (sl[0], sl[1] + 0.06 + lift, sl[2]); P['rgrip'] = 0.95; P['rpalm'] = (0.0, -1.0, 0.0)
        P['head'] = (-0.25, 0.25, 0.0); P['brow'] = 0.1; P['mouth'] = 'grit'
        if t > T_RUSH[0]: P['head'] = (0.0, 0.0, 0.0); P['eyes'] = 'wide'
        return P
    pt = sm(seg01(t, T_POINT, T_POINT + 0.3))
    aim = V(loc(BR, P['yaw'], PASS_IN + V((0, 0.45, 0)))); sh_ = V((0.18, 1.0, 0.0))
    d = (aim - sh_) / np.linalg.norm(aim - sh_); tip = sh_ + d * 0.55
    P['rh'] = lerp3(V(sl) + V((0, 0.15, 0)), tip, pt); P['rgrip'] = 0.8; P['rpalm'] = (-1.0, 0.0, 0.0)
    shk = win(t, T0['03'], T0['03'] + 0.9, 0.15)
    P['head'] = (0.3 * math.sin((t - T0['03']) * 2 * PI * 2.2) * shk, 0.0, 0.0); P['brow'] = -0.7; P['eyes'] = 'open'
    mt = talking(t, '03', 6.5)
    if mt: P['mouth'] = mt
    if t > tend('03') + 0.2: P['mouth'] = 'soft'; P['brow'] = -0.5
    if t > T_LEAVE[0] + 0.5: P['mouth'] = 'smile'; P['eyes'] = 'half'
    return P
_bp = bro(MEM_PT + 0.4); hd.human(BRO, _bp); HANDW = _bp['_rwrist'] + _bp['_rdir'] * 0.08
def young(t):
    P = dict(base=tuple(YA0), yaw=ang_to(YA0, BR), eyes='wide', mouth='o', brow=0.2, lean=0.06, cape_sway=0.1 * math.sin(t * 2))
    P['rh'] = (0.2, 0.95, 0.25); P['rgrip'] = 0.4; P['lh'] = (-0.2, 0.95, 0.15); P['lgrip'] = 0.4
    if t < T_RUSH[0]:
        P['head'] = (0.0, -0.1, 0.0); return P
    u = seg01(t, *T_RUSH); us = sm(u)
    P['base'] = lerp3(YA0, YA1, us)
    if u < 1: P['walk'] = us * 9; P['stride'] = 0.42; P['lean'] = 0.25
    P['rh'] = lerp3((0.2, 0.95, 0.25), (0.08, 1.2, 0.55), us); P['rgrip'] = 0.15; P['rpalm'] = (-0.3, 0, 1.0)
    if t > T_POINT + 0.2: P['rh'] = lerp3((0.08, 1.2, 0.55), (0.2, 0.95, 0.25), sm(seg01(t, T_POINT + 0.2, T_POINT + 0.8))); P['lean'] = 0.06
    if t >= T_HES[0]:                                                               # looks at the passage... back at his brother
        k = win(t, T_HES[0], T_HES[0] + 0.85, 0.2); P['head'] = (1.0 * k, 0.0, 0.0); P['twist'] = 0.35 * k; P['brow'] = -0.4 if k > 0.5 else -0.7; P['mouth'] = 'neutral'
        if t > T_HES[0] + 0.9: P['eyes'] = 'sad'; P['mouth'] = 'grit'
    if t >= T_LEAVE[0]:                                                             # goes back to the passage, leading them; looks back
        u = seg01(t, T_LEAVE[0], T_LEAVE[0] + 1.6); us = sm(u); tgt = PASS_IN + DIRM * 0.35
        P['base'] = lerp3(YA1, tgt, us); P['yaw'] = ang_to(YA1, PASS_IN)
        if u < 1: P['walk'] = us * 8; P['stride'] = 0.34
        else: P.pop('walk', None)
        lb = win(t, T_LEAVE[0] + 1.5, T_LEAVE[1], 0.3)
        P['head'] = (1.05 * lb, 0.0, 0.0); P['twist'] = 0.45 * lb; P['eyes'] = 'sad'; P['brow'] = -0.8; P['mouth'] = 'neutral'
        P['rh'] = (0.25, 1.0, 0.3); P['rgrip'] = 0.2
        if t > T_LEAVE[1] - 0.2:
            v = sm(seg01(t, T_LEAVE[1] - 0.2, T_LEAVE[1] + 0.9)); P['base'] = lerp3(tgt, PASS_OUT + OUTD * 0.2, v); crawl(P, v * 10, v)
            P['yaw'] = ang_to(PASS_IN, PASS_OUT); P['head'] = (0.0, 0.0, 0.0); P['twist'] = 0.0
    return P
def survivors(t):
    out = []
    for i, (sp, off) in enumerate(((SURV1, -PERPM * 0.55 + DIRM * 0.55), (SURV2, PERPM * 0.5 + DIRM * 0.45))):
        b0 = PASS_IN + off
        P = dict(base=tuple(b0), yaw=ang_to(b0, YA0) + (0.4 if i == 0 else -0.3), crouch=0.42, lean=0.35, eyes='open', mouth='neutral', brow=-0.6, nod=0.1)
        P['rf'] = (0.13, 0.07, 0.22); P['lf'] = (-0.13, 0.07, 0.1); P['rh'] = (0.12, 0.62, 0.32); P['lh'] = (-0.12, 0.62, 0.32); P['rgrip'] = P['lgrip'] = 0.5
        if t > T_LEAVE[0] + 0.3 + 0.5 * i:                                          # into the passage, out to safety
            v = seg01(t, T_LEAVE[0] + 0.3 + 0.5 * i, T_LEAVE[0] + 1.7 + 0.5 * i); m = PASS_IN + DIRM * 0.2; e = PASS_OUT + OUTD * 0.4
            if v >= 1: continue
            pth = lerp3(b0, m, min(1, v * 2)) if v < 0.5 else lerp3(m, e, (v - 0.5) * 2)
            P = dict(base=tuple(pth), yaw=ang_to(PASS_IN, PASS_OUT), eyes='open', mouth='neutral', brow=-0.4); crawl(P, v * 14, 1.0)
        out.append((sp, P))
    return out

# ======================= cameras =======================
def P3(keys): return look.Path(keys)
def keyed(t, K):
    pos = P3([(a, tuple(p)) for a, p, _, _ in K])(t); tgt = P3([(a, tuple(q)) for a, _, q, _ in K])(t); fov = P3([(a, f) for a, _, _, f in K])(t)
    return tuple(pos), tuple(tgt), float(np.ravel(fov)[0])
FW0 = V((math.sin(YAW0), 0, math.cos(YAW0))); RT0 = V((FW0[2], 0, -FW0[0]))
def face0(): return A0 + V((0, 1.6, 0))
def cam_for(sh, t):
    if sh == 'hook':                                                                # the child's hand knocking
        c = KNOCKST + V((0, 0.12, 0)); tw = flat(PASS_IN - CH); sd = V((tw[2], 0, -tw[0]))
        return keyed(t, [(0.0, c + tw * 0.5 + sd * 0.35 + V((0, 0.12, 0)), c - tw * 0.1 + V((0, 0.12, 0)), 40.0), (T_FRZ0, c + tw * 0.45 + sd * 0.32 + V((0, 0.12, 0)), c - tw * 0.1 + V((0, 0.12, 0)), 38.0)])
    if sh in ('freeze0', 'p_freeze'):
        f = face0(); t0 = T_FRZ0 if sh == 'freeze0' else T_FRZ - 0.05
        return keyed(t, [(t0, f + FW0 * 0.95 + RT0 * 0.3 - V((0, 0.05, 0)), f, 30.0), (t0 + 2.0, f + FW0 * 0.8 + RT0 * 0.26 - V((0, 0.05, 0)), f, 28.0)])
    if sh == 'light':
        c = A0 + V((0, 1.33, 0)) + FW0 * 0.3
        return keyed(t, [(T_LIGHT - 0.55, c + FW0 * 0.75 + RT0 * 0.15 + V((0, 0.12, 0)), c + V((0, 0.08, 0)), 36.0), (T_WIDE, c + FW0 * 0.65 + RT0 * 0.12 + V((0, 0.12, 0)), c + V((0, 0.1, 0)), 34.0)])
    if sh == 'wide0':
        return keyed(t, [(T_WIDE, A0 + V((1.7, 1.8, -3.2)), V((-0.8, 2.0, 5.0)), 54.0), (T_FLAME, A0 + V((1.5, 1.7, -2.6)), V((-0.6, 1.9, 5.0)), 52.0)])
    if sh == 'flame':                                                               # push into the flame
        P, _ = aren(t); hd.human(AREN, P); fp = hold_base(P) + V((0, 0.13, 0))
        u = sm(seg01(t, T_FLAME, T_MEM))
        return tuple(fp + FW0 * lerp(0.55, 0.07, u) + V((0, lerp(0.12, 0.0, u), 0))), tuple(fp), lerp(34.0, 20.0, u)
    if sh == 'm_est':
        return keyed(t, [(T_MEM, YA0 - DIRM * 0.4 - PERPM * 1.1 + V((0, 2.0, 0)), BEAM_C + V((0, 0.6, 0)), 52.0), (T_MK - 0.25, YA0 - DIRM * 0.2 - PERPM * 1.0 + V((0, 1.8, 0)), BEAM_C + DIRM * 0.4 + V((0, 0.6, 0)), 48.0)])
    if sh == 'm_knock':
        return keyed(t, [(T_MK - 0.25, BR - DIRM * 1.5 + PERPM * 0.55 + V((0, 1.25, 0)), lerp3(SLAB, BR, 0.5) + V((0, 0.55, 0)), 38.0), (T_RUSH[0], BR - DIRM * 1.3 + PERPM * 0.5 + V((0, 1.2, 0)), lerp3(SLAB, BR, 0.5) + V((0, 0.55, 0)), 34.0)])
    if sh == 'm_point':
        tt = t
        K = [(T_RUSH[0], BR + DIRM * 1.0 + PERPM * 0.75 + V((0, 1.35, 0)), lerp3(BR, PASS_IN, 0.6) + V((0, 0.6, 0)), 48.0), (T0['03'] + 0.15, BR + DIRM * 0.85 + PERPM * 0.65 + V((0, 1.3, 0)), lerp3(BR, PASS_IN, 0.62) + V((0, 0.55, 0)), 46.0)]
        return keyed(tt, K)
    if sh == 'm_face':
        f = BR + V((0, 1.12, 0))
        return keyed(t, [(T0['03'] + 0.15, BR - DIRM * 1.25 + PERPM * 0.35 + V((0, 1.22, 0)), f, 30.0), (tend('03') + 0.05, BR - DIRM * 1.05 + PERPM * 0.32 + V((0, 1.2, 0)), f, 27.0)])
    if sh == 'm_hes':                                                               # young Aren between: passage behind him, brother in front
        f = YA1 + V((0, 1.56, 0)); dl = flat(BR - YA1)
        return keyed(t, [(tend('03') + 0.05, f + dl * 0.95 + PERPM * 0.25 + V((0, -0.05, 0)), f - dl * 0.3, 36.0), (T_LEAVE[0], f + dl * 0.85 + PERPM * 0.22 + V((0, -0.05, 0)), f - dl * 0.3, 34.0)])
    if sh == 'm_leave':
        return keyed(t, [(T_LEAVE[0], BR + DIRM * 0.6 + PERPM * 1.0 + V((0, 1.5, 0)), lerp3(BR, PASS_IN, 0.65) + V((0, 0.6, 0)), 50.0), (T_PTCU, BR + DIRM * 0.45 + PERPM * 0.9 + V((0, 1.45, 0)), lerp3(BR, PASS_IN, 0.75) + V((0, 0.5, 0)), 46.0)])
    if sh in ('m_hand', 'p_match', 'flash'):                                        # behind his pointing hand, to the passage (and the same view today)
        w = HANDW; d = flat(PASS_IN - w); sd = V((d[2], 0, -d[0]))
        t0 = T_PTCU if sh != 'flash' else T_FLASH[0]
        K = [(t0, w - d * 0.55 + sd * 0.14 + V((0, 0.14, 0)), PASS_IN + V((0, 0.42, 0)), 36.0), (t0 + 3.5, w - d * 0.45 + sd * 0.12 + V((0, 0.12, 0)), PASS_IN + V((0, 0.4, 0)), 33.0)]
        return keyed(t, K)
    if sh == 'p_knock': return cam_for('hook', 0.5 + (t - T_CK) * 0.3)
    if sh == 'p_see':                                                               # behind Aren: the passage his brother pointed to
        return keyed(t, [(T_SEE, PASS_OUT + OUTD * 2.8 - PERP * 0.3 + V((0, 1.35, 0)), PASS_OUT + V((0, 0.45, 0)), 44.0), (T_DIRECT, PASS_OUT + OUTD * 2.2 - PERP * 0.25 + V((0, 1.1, 0)), PASS_OUT + V((0, 0.4, 0)), 38.0)])
    if sh == 'p_direct':                                                            # the doorway (right) and the passage (left)
        return keyed(t, [(T_DIRECT, (-0.6, 1.7, -2.6), (0.5, 1.0, 3.0), 50.0), (T_SHIFT, (0.4, 1.5, -1.0), (1.2, 1.0, 2.6), 46.0), (T_RUNP[0] + 0.9, (0.0, 1.6, -1.6), (0.2, 1.0, 3.0), 50.0)])
    if sh == 'p_pass':
        side = PASS_OUT + OUTD * 2.2 - PERP * 0.6; midp = V(lerp3(CROUCH, PASS_OUT, 0.5))
        return keyed(t, [(T_RUNP[0] + 0.9, side + OUTD * 0.6 + V((0, 1.4, 0)), midp + V((0, 0.6, 0)), 50.0), (T_SET[1], side + OUTD * 0.1 + V((0, 1.05, 0)), midp + V((0, 0.4, 0)), 42.0),
                         (T_INSIDE, side - OUTD * 0.3 + V((0, 0.9, 0)), PASS_OUT + V((0, 0.35, 0)), 38.0)])
    if sh == 'p_inside':
        tw = flat(PASS_IN - CH); sd = V((tw[2], 0, -tw[0])); mid = V(lerp3(PASS_IN, CH, 0.5))
        return keyed(t, [(T_INSIDE, mid + sd * 1.45 + V((0, 1.0, 0)), mid + V((0, 0.35, 0)), 46.0), (T_EXIT, mid + sd * 1.25 + V((0, 0.85, 0)), mid + V((0, 0.3, 0)), 42.0)])
    if sh == 'p_exit':
        side = PASS_OUT + OUTD * 2.4 - PERP * 0.8
        return keyed(t, [(T_EXIT, side + V((0, 1.1, 0)), PASS_OUT + OUTD * 0.5 + V((0, 0.4, 0)), 46.0), (T_RUNM[0], side + OUTD * 0.3 + V((0, 1.3, 0)), PASS_OUT + OUTD * 0.7 + V((0, 0.6, 0)), 52.0)])
    if sh == 'h_run':
        mid = (C_ST + M0) / 2
        return keyed(t, [(T_RUNM[0], mid + V((2.2, 1.45, -2.4)), mid + V((0, 0.8, 0)), 48.0), (T_COUT - 0.75, mid + V((1.9, 1.35, -2.0)), mid + V((-0.2, 0.75, 0)), 44.0)])
    if sh == 'h_candle':                                                            # the candle on the rock; the reunion beyond
        c = CANDLE_ON_ROCK + V((0, 0.1, 0)); d = flat(HUGP - c)
        return keyed(t, [(T_COUT - 0.75, c - d * 0.42 + V((0, 0.08, 0)), V(HUGP) + V((0, 0.7, 0)), 38.0), (T_COUT + 0.45, c - d * 0.34 + V((0, 0.05, 0)), c + d * 0.3 + V((0, 0.03, 0)), 32.0)])
    if sh == 'h_turn':
        P, _ = aren(t); f = V(P['base']) + V((0, 1.18, 0)); fw = V((math.sin(P['yaw']), 0, math.cos(P['yaw']))); pd = flat(PASS_OUT - V(P['base']))
        return keyed(t, [(T_COUT + 0.45, f + pd * 0.75 + fw * 0.45 + V((0, 0.02, 0)), f, 34.0), (T0['07'] + 0.2, f + pd * 0.68 + fw * 0.4, f, 32.0)])
    if sh == 'h_two':
        b = AEND; d = flat(HUGP - b); sd = V((d[2], 0, -d[0]))
        return keyed(t, [(T0['07'] + 0.2, b - d * 1.2 + sd * 0.7 + V((0, 1.7, 0)), lerp3(b, HUGP, 0.55) + V((0, 0.7, 0)), 48.0), (T_END, b - d * 1.0 + sd * 0.6 + V((0, 1.6, 0)), lerp3(b, HUGP, 0.6) + V((0, 0.7, 0)), 46.0)])
    P, _ = aren(t); hd.human(AREN, P); c = hold_base(P) + V((0, 0.1, 0)); fw = V((math.sin(P['yaw']), 0, math.cos(P['yaw'])))     # h_end
    return keyed(t, [(T_END, c + fw * 0.8 + V((0.05, 0.28, 0)), c + V((0, 0.22, 0)), 40.0), (DUR, c + fw * 0.7 + V((0.05, 0.25, 0)), c + V((0, 0.24, 0)), 38.0)])

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
def world(t, sh, pos, tgt):
    L = []; layers = []; e = era(sh)
    if e == 'mem':
        tt = T_PTCU + 1.0 if sh == 'flash' else t
        layers += [get_set('tower'), get_set('mem'), dust_faces(tt, BEAM_C), debris_mem(tt), outer_light((120, 140, 186)), lintel(tt, False)]
        cq, fp = candle(MEMC, 1.0, tt, seed=3); layers.append(cq)
        fl = 1 + 0.08 * math.sin(tt * 11) + 0.05 * math.sin(tt * 29)
        L += [(tuple(fp + V((0, 0.1, 0))), (255, 186, 120), 1.5 * fl), (tuple(BR + V((0.4, 2.6, 0.3))), (240, 200, 160), 0.7), (tuple(PASS_IN + V((0, 0.5, 0)) + DIRM * 0.3), (190, 205, 235), 0.45),
              ((0, 9, 6), (120, 110, 130), 0.5)]
        layers.append(hd.human(BRO, bro(tt))); layers.append(hd.human(YOUNG, young(tt)))
        for sp, P in survivors(tt): layers.append(hd.human(sp, P))
        return layers, L, (34, 24, 18), 0.3, 6, 22
    if e == 'in':
        layers += [get_set('tower'), get_set('innow'), outer_light((96, 112, 150)), lintel(t), dust_faces(t, CH, 25, (150, 160, 190))]
        L += [((0.0, 7.0, 6.0), (110, 126, 180), 1.4), (tuple(PASS_IN + V((0, 0.5, 0)) + DIRM * 0.4), (120, 140, 190), 0.8)]
        layers.append(hd.human(CHILD, child_inside(t)))
        if sh == 'p_inside':
            layers.append(hd.human(AREN, aren_inside(t)))
            for k in range(5):                                                      # stones crash down where the child was
                p = CH + V(((hsh(k, 1) - 0.5) * 0.5, 0.08, (hsh(k, 2) - 0.5) * 0.5))
                layers.append(falling(t, T_FALL2 + 0.07 * k, p + V((0, 2.8, 0)), p, 0.08 + 0.04 * hsh(k, 3), 0.45, k + 40, (110, 106, 100)))
            layers.append(puff(CH, t, T_FALL2 + 0.4, 1.2, 12, 0.7, (130, 132, 140), 0.07))
            L.append((tuple(PASS_OUT + V((0, 0.4, 0))), (255, 180, 110), 0.5))
        return layers, L, (14, 16, 24), 0.32, 6, 22
    layers += [get_set('tower'), get_set('out'), lintel(t), debris_out(t), shift_faces(t), dig_stone(t)]
    dawn = 0.35 * sm(seg01(t, T_HUG - 2.0, DUR))
    rain = 1.0 - 0.7 * sm(seg01(t, T_COUT - 0.5, DUR))
    L += [((-12, 14, -6), mixc((120, 140, 200), (200, 170, 150), dawn), 1.25 + 0.5 * dawn), ((8, 6, 10), (90, 100, 140), 0.6)]
    cf = V(pos, float); fw_ = V(tgt, float) - cf; fw_ = fw_ / (np.linalg.norm(fw_) + 1e-9); L.append((tuple(cf - fw_ * 1.6 + V((0.3, 1.0, 0))), (120, 134, 180), 0.45))
    fog = mixc((18, 22, 36), (120, 104, 104), dawn); amb = lerp(0.36, 0.42, dawn)
    P, where = aren(t)
    hidden = T_CRAWL[1] - 0.05 < t < T_EXIT                                         # he is inside the tower
    if not hidden: layers.append(hd.human(AREN, P))
    lit, smoke = candle_state(t)
    cb = hold_base(P) if (where == 'hand' and not hidden) else CANDLE_ON_ROCK
    cq, fp = candle(cb, lit, t, smoke=smoke); layers.append(cq)
    if lit > 0: L.append((tuple(fp + V((0, 0.05, 0))), (255, 180, 100), 0.75 * lit * (0.92 + 0.08 * math.sin(t * 19))))
    if T_LIGHT - 0.2 < t < T_LIGHT + 0.2:
        for i in range(6):
            u = seg01(t, T_LIGHT - 0.2, T_LIGHT + 0.2); p = fp + V(((hsh(i, 1) - 0.5) * 0.15 * u, (hsh(i, 2) - 0.2) * 0.1 * u, (hsh(i, 3) - 0.5) * 0.12 * u))
            layers.append([q for q in [hd.face([p, p + V((0.006, 0.006, 0)), p + V((0.012, 0, 0))], (255, 230, 150), emit=True)] if q])
        L.append((tuple(fp), (255, 210, 140), 1.0))
    C = child_out(t)
    if C is not None: layers.append(hd.human(CHILD, C))
    layers.append(hd.human(MOTHER, mother(t)))
    layers.append(rain_faces(pos, tgt, t, rain))
    return layers, L, fog, amb, 8, 40

def grade(a, e, t):
    if e == 'mem':
        l = a.mean(axis=2, keepdims=True); a = (a * 0.8 + l * 0.2) * np.array([1.09, 0.99, 0.84])
        yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]; r = np.hypot((xx - a.shape[1] / 2) / a.shape[1], (yy - a.shape[0] / 2) / a.shape[0])
        return a * (1 - 0.55 * np.clip(r - 0.25, 0, 1))[..., None]
    l = a.mean(axis=2, keepdims=True); a = a * 0.75 + l * 0.25
    return a * np.array([0.86, 0.96, 1.12])
def render_low(t, sh):
    pos, tgt, fov = cam_for(sh, t); cam = Camera.look(tuple(pos), tuple(tgt))
    layers, L, fog, amb, fs, fe = world(t, sh, pos, tgt)
    R = Renderer(W, H, fog=fog)
    img, vi, zb = zrender(R, cam, layers, L, fov=fov, fog_start=fs, fog_end=fe, ambient=amb, return_z=True)
    a = look.outline(np.asarray(img).astype(np.float32), zb)
    a = grade(a, era(sh), t)
    return np.clip((a - 112) * 1.1 + 110, 0, 255)
def warm_glow(a, k):
    """the flame transition: a warm bloom that fills the frame"""
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]; r = np.hypot((xx - a.shape[1] / 2) / a.shape[1], (yy - a.shape[0] * 0.5) / a.shape[1])
    g = np.clip(1.4 * k - r * (1.6 - k), 0, 1)[..., None]
    return a * (1 - g) + np.array([255, 214, 150]) * g
def frame_low(t):
    sh = shot_at(t); a = render_low(t, sh)
    if T_MEM - 0.7 <= t < T_MEM + 0.55:                                             # through the flame into the memory
        k = sm(seg01(t, T_MEM - 0.7, T_MEM)) if t < T_MEM else 1 - sm(seg01(t, T_MEM, T_MEM + 0.55))
        a = warm_glow(a, k)
    if T_FLASH[0] <= t < T_FLASH[0] + 0.12: a = warm_glow(a, 0.7 * (1 - seg01(t, T_FLASH[0], T_FLASH[0] + 0.12)))
    if T_NOW <= t < T_NOW + 0.45: u = sm(seg01(t, T_NOW, T_NOW + 0.45)); a = render_low(t, 'm_hand') * (1 - u) + a * u     # the pointing hand dissolves into today
    return post.ps1(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), levels=6)

# ======================= overlays =======================
def text_w(s, sc): return len(s) * 6 * sc - sc
def label_overlay(im, t):
    a, b = T_MEM + 0.2, T_MEM + 2.2
    if not (a <= t < b): return
    d = ImageDraw.Draw(im); s = 'YEARS AGO'; sc = 9
    look.draw_cells(d, look.text_cells(s, int(540 - text_w(s, sc) / 2), 170, sc, (255, 226, 170)), 4)
COL = {'N': (242, 238, 226), 'B': (255, 196, 120)}
SUBS = look.Subtitles(SCR, LINES, W, H, S, COL, title_key='-none-', n=17,
                      hil={'KNOCKS,', 'KNOCKS', 'DYING.', 'CANDLE', 'VOICE', 'FOREVER.', 'POINTING.', 'SOUND.', 'MISSED.', 'FRONT.', 'SHOWN', 'ASKED'})
def frame_final(t):
    img = frame_low(t); arr = post.upscale(img, S)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); label_overlay(im, t); arr = np.asarray(im).astype(np.float32)
    arr = SUBS.apply(arr, t)
    if t >= T_FADE: arr = arr * (1 - sm(seg01(t, T_FADE, DUR - 0.12)))
    return arr
def frame(t): return Image.fromarray(np.clip(frame_final(t), 0, 255).astype(np.uint8)).resize((W, H), Image.BOX)

TEST = os.environ.get('TEST')
if TEST and __name__ == '__main__':
    ts = [float(x) for x in TEST.split(',')] if TEST != 'all' else [round(x, 2) for x in np.arange(0, DUR, float(os.environ.get('STEP', '1.0')))]
    ims = [Image.fromarray(np.clip(frame_final(x), 0, 255).astype(np.uint8)).resize((270, 480), Image.LANCZOS) for x in ts]
    per = int(os.environ.get('PER', '8')); rows = (len(ims) + per - 1) // per; shp = Image.new('RGB', (min(per, len(ims)) * 272, rows * 498), (30, 30, 30))
    dd = ImageDraw.Draw(shp)
    for i, (im, x) in enumerate(zip(ims, ts)): shp.paste(im, ((i % per) * 272, (i // per) * 498)); dd.text(((i % per) * 272 + 4, (i // per) * 498 + 483), f'{x:.2f} {shot_at(x)}', fill=(255, 255, 0))
    shp.save(os.environ.get('TEST_OUT', 'test_le.png')); print('test written', DUR); sys.exit()

# ======================= QA manifest =======================
QA = dict(fps=FPS, dur=DUR, W=W, frame=frame, chars={}, geom=lambda t, name, st, V_: [], camera=lambda t: cam_for(shot_at(t), t)[0], min_cam_dist=0.3,
          camera_ok=lambda p: True, allow_jump=[], weapon_events=[],
          scenes=[dict(id='hook', t0=0.0, t1=T_MEM, action='the child knocks; Aren freezes; lights the candle; the ruin; into the flame'),
                  dict(id='memory', t0=T_MEM, t1=T_NOW, action='YEARS AGO: brother trapped, knocks, Aren rushes, brother points to the passage, Aren leads them out'),
                  dict(id='clicks', t0=T_NOW, t1=T_DIRECT, action='same passage today; the child knocks; Aren freezes; flash; he sees the passage'),
                  dict(id='rescue', t0=T_DIRECT, t1=T_RUNM[0], action='doorway collapses on him; passage; crawls in; the hand; out before the lintel falls'),
                  dict(id='payoff', t0=T_RUNM[0], t1=DUR, action='mother; the candle dies; he turns; silence; the dead candle')],
          texts=lambda: [('label', 'YEARS AGO', 9)])

# ======================= AUDIO =======================
LVL = {'03': 0.0}
def knock_sample(sr):
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
    def step(t0, v=0.03, seed=0):
        tt = s.T(0.12); put(FX, s.filt_short(s.noise(0.12, seed), lo=150, hi=4000) * np.exp(-tt * 30) + np.sin(2 * np.pi * 75 * tt) * np.exp(-tt * 26) * 0.3, t0, v)
    def piano(t0, m, v=0.05, d=3.0):
        tone(t0, m, d, v, dec=1.2, harm=(1.0, 0.45, 0.2, 0.08)); tone(t0 + 0.002, m + 12, d, v * 0.15, dec=2.0)
    def stone(t0, v=0.05, seed=0):
        nb(t0, 0.25, 150, 1600, v, seed, 1); tt = s.T(0.2); put(FX, np.sin(2 * np.pi * 70 * tt) * np.exp(-tt * 22), t0 + 0.05, v * 0.8)
    def rumble(t0, d, v, seed):
        tt = s.T(d); put(FX, s.filt_short(s.noise(d, seed), lo=25, hi=220) * np.minimum(1, tt / 0.1) * np.exp(-tt * 2.2 / d), t0, v)
    K = knock_sample(sr)
    def knocks(t0, v=0.3, echo=False):
        for k in range(3): put(KNK, K, t0 + k * KN, v)
        if echo:
            for k in range(3): put(KNK, s.filt_short(K, lo=200, hi=2000), t0 + k * KN + 0.38, v * 0.3)
    mem = mask(T_MEM, T_NOW, 0.3); pres = 1 - mem
    inside = np.zeros(n)
    for a_, b_ in ((0.0, T_FRZ0), (T_NOW, T_FRZ - 0.05), (T_INSIDE, T_EXIT)): inside = np.maximum(inside, mask(a_, b_, 0.05))
    rainA = pres * (1 - 0.7 * np.clip((t - (T_COUT - 0.5)) / 4.0, 0, 1)) * (1 - 0.6 * inside)
    BED += s.filt(s.rng.normal(0, 1, n), lo=900, hi=8000) * 0.04 * rainA
    BED += s.filt(s.rng.normal(0, 1, n), lo=150, hi=900) * 0.02 * rainA
    BED += s.filt(s.rng.normal(0, 1, n), lo=40, hi=160) * 0.03 * pres * (0.6 + 0.4 * np.sin(2 * np.pi * 0.13 * t))
    knocks(T_K0, 0.32); knocks(T_MK, 0.32, echo=True); knocks(T_CK, 0.32)
    nb(T_LIGHT - 0.2, 0.12, 2500, 9000, 0.05, 5, 1); nb(T_LIGHT - 0.05, 0.1, 2500, 9000, 0.05, 6, 1); nb(T_LIGHT + 0.12, 0.5, 200, 1500, 0.035, 7, 1)
    tt = s.T(1.2); put(FX, s.filt_short(s.noise(1.2, 8), lo=200, hi=3000) * (tt / 1.2) ** 2, T_MEM - 1.0, 0.05)
    nb(T_COUT - 0.05, 0.35, 300, 2200, 0.03, 9, 1)
    for t0, ph in DEBRIS_OUT:
        if t0 + 0.55 < T_MEM or t0 > T_NOW: stone(t0 + 0.55, 0.015, int(t0 * 10))
    for t0, k in DEBRIS_MEM: stone(t0 + 0.55, 0.02, 100 + k)
    rumble(T_MEM + 0.1, 2.0, 0.12, 30)
    BED += s.filt(s.rng.normal(0, 1, n), lo=80, hi=500) * 0.03 * mem
    rise = np.clip((t - (T_MK + 2 * KN + 0.7)) / 3.0, 0, 1) * mem
    for f, a in ((146.8, 1.0), (220.0, 0.55), (293.7, 0.4)): MUS += np.sin(2 * np.pi * f * t + a) * a * 0.018 * rise
    for f, a in ((110.0, 1.0), (165.0, 0.5)): MUS += np.sin(2 * np.pi * f * t) * a * 0.01 * mem
    for a_, m in ((T_POINT, 62), (T0['03'] + 1.2, 66), (T_HES[0] + 0.4, 69), (T_LEAVE[0] + 0.5, 64), (T_PTCU + 0.3, 62)): piano(a_, m, 0.045)
    for k in range(4): step(T_RUSH[0] + 0.1 + k * 0.2, 0.03, 10 + k)
    ten = pres * np.clip((t - T_NOW) / 1.0, 0, 1) * (1 - mask(T_CK - 0.2, T_FRZ + 0.4, 0.1) * 0.9) * np.clip((T_COUT - 0.3 - t) / 0.3, 0, 1)
    for f, a in ((73.4, 1.0), (110.0, 0.5), (155.6, 0.25)): MUS += np.sin(2 * np.pi * f * t) * a * 0.016 * ten
    hk = mask(-1, T_MEM - 0.5, 0.5)
    for f, a in ((73.4, 1.0), (110.0, 0.4)): MUS += np.sin(2 * np.pi * f * t) * a * 0.01 * hk
    piano(T_FLASH[0], 62, 0.05); piano(T_SEE + 0.1, 69, 0.04)
    k = 0
    while T_DIRECT + 0.1 + k * 0.3 < T_DIG[0]: step(T_DIRECT + 0.1 + k * 0.3, 0.03, 20 + k); k += 1
    for k in range(4): stone(T_DIG[0] + 0.3 + k * 0.3, 0.03, 30 + k)
    rumble(T_SHIFT - 0.1, 1.8, 0.2, 31)
    for k in range(7): stone(T_SHIFT + 0.05 * k + 0.4, 0.05, 40 + k)
    k = 0
    while T_RUNP[0] + k * 0.24 < T_RUNP[1]: step(T_RUNP[0] + k * 0.24, 0.035, 50 + k); k += 1
    tone(T_SET[1] - 0.1, 93, 0.15, 0.015, dec=25)
    nb(T_CRAWL[0], T_CRAWL[1] - T_CRAWL[0], 150, 1500, 0.025, 60, 1)
    nb(T_TAKE - 0.02, 0.12, 600, 3000, 0.03, 61, 1); tt = s.T(0.12); put(FX, np.sin(2 * np.pi * 95 * tt) * np.exp(-tt * 30), T_TAKE, 0.05)
    rumble(T_FALL2 - 0.2, 1.5, 0.18, 62)
    for k in range(5): stone(T_FALL2 + 0.07 * k + 0.4, 0.05, 63 + k)
    nb(T_OUTP[0], 1.4, 150, 1500, 0.025, 70, 2)
    rumble(T_COLLAPSE - 0.1, 2.2, 0.25, 71)
    for k in range(6): stone(T_COLLAPSE + 0.08 * k + 0.38, 0.06, 72 + k)
    k = 0
    while T_RUNM[0] + k * 0.25 < T_RUNM[1]: step(T_RUNM[0] + k * 0.25, 0.03, 80 + k); k += 1
    warm = mask(T_RUNM[0], T_COUT - 0.25, 0.6)
    for f, a in ((146.8, 1.0), (185.0, 0.5), (220.0, 0.5), (293.7, 0.35)): MUS += np.sin(2 * np.pi * f * t) * a * 0.016 * warm
    piano(T_HUG, 66, 0.05); piano(T_HUG + 0.6, 69, 0.04)
    endm = mask(T0['07'] + 0.2, DUR + 2, 1.5) * np.clip((DUR - 0.1 - t) / 0.9, 0, 1)
    for f, a in ((146.8, 1.0), (220.0, 0.5), (293.7, 0.4)): MUS += np.sin(2 * np.pi * f * t) * a * 0.011 * endm
    piano(T0['07'] + 0.3, 62, 0.045); piano(ws('07', 1), 66, 0.04); piano(tend('07') + 0.2, 69, 0.04)
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
