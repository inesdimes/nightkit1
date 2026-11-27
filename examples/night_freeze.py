"""WHY DO NPCS STAND STILL AT NIGHT? (Insert Disc 2, 28 Nov 2026) ~29 s final (x1.2 after), nightkit HD, 9:16. CREEPY.
Brief: briefs/night_freeze.md (Claude) + the rules filter (rules v27 Nov c): the Watcher only sees what MOVES. The villagers stand still
facing the walls all night; the knight walks in waving, keeps moving, is spotted; his torch flame keeps moving when he freezes; old Bram
throws his red hat (moves) and is taken instead. At dawn every NPC respawns: Marta puts the wet hat on Bram: "Nice weather today!" ->
night again -> a new hero walks in = frame 0 (loop).
Voices: tools/tts/nf.py (N/K/B cloned Enes, Marta = Kokoro whisper). Reuses: dragon_taxes knight + helmet, villagers, houses, torch.
New: the Watcher (fog giant, lantern eyes, long fingers), cat, red hat, night street, detection cone + meter, dawn time-lapse.
Render: python tools/render_seq.py examples/night_freeze.py --prefix nf --seqs s1,s2,s3,s4,s5 / --master <out>
Stills: TEST=seq python examples/night_freeze.py -> test_nf.png"""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera, refresh
from nightkit.zraster import zrender
from nightkit import post, look, hd, motion, font
import dragon_taxes as dtx

W, H, S = 270, 480, 4
PI = math.pi; V = np.array; FPS = 24
sm = motion.smooth
hsh, lerp, lerp3, mixc = dtx.hsh, dtx.lerp, dtx.lerp3, dtx.mixc
def seg01(t, a, b): return max(0.0, min(1.0, (t - a) / (b - a))) if b > a else (1.0 if t >= b else 0.0)
def win(t, a, b, r=0.25): return sm(seg01(t, a, a + r)) * (1 - sm(seg01(t, b - r, b)))
def nz(v): v = V(v, float); n = np.linalg.norm(v); return v / n if n > 1e-9 else v
def rot_y(d):
    """3x3 rotation whose local y axis points along d"""
    d = nz(d); u, w = hd.frame_for(d, (1.0, 0, 0)); return np.column_stack([u, d, -w])
def grip_pt(P, key, off=0.075, lift=0.03): return P['_' + key + 'wrist'] + P['_' + key + 'dir'] * off + P['_' + key + 'palm'] * lift
def F(x): return round(x * 1.2, 4)
SUB_LANG = os.environ.get('SUB_LANG', 'en'); TRL = SUB_LANG == 'tr'

# ======================= timeline =======================
from nightkit.audio import Sound, duck_envelope
OUT = 'out'; os.makedirs(OUT, exist_ok=True)
TTS_DIR = os.environ.get('TTS_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tts'))
SCR = json.load(open(os.path.join(TTS_DIR, 'nf', 'script.json'), encoding='utf-8'))
KEYS = ['%02d' % i for i in range(0, 10)]
T0 = {}
def tend(k): return T0[k] + SCR['dur'][k]
def ws(k, i): s_ = SCR['sent'][k]; return T0[k] + s_[min(i, len(s_) - 1)][0]
def we(k, i): s_ = SCR['sent'][k]; return T0[k] + s_[min(i, len(s_) - 1)][1]
T0['00'] = 0.1
T0['01'] = tend('00') + 0.15                       # "Hello? Is anyone home?" (he waves at Marta)
S_EYES = T0['01'] - 0.05                            # close-up: only her eyes move
T_EYE_MOVE = we('01', 0) + 0.2
S_REVEAL = tend('01') + 0.35
T_OPEN = S_REVEAL + 0.45                            # the lantern eyes open in the fog
THOOMS = [T0['01'] + 0.5, T_OPEN + 0.1]
T0['02'] = T_OPEN + 0.9                             # "They aren't broken. They're hiding."
S_CAT = tend('02') + 0.25
T_CAT = (S_CAT + 0.25, S_CAT + 1.05)                # the cat dashes across
T_SNAP = S_CAT + 0.85; T_YANK = S_CAT + 1.05
T0['03'] = T_YANK + 0.45                            # Marta: "Stop. Moving."
T0['04'] = tend('03') + 0.25                        # N: "It only sees what moves."
S_HERO = tend('04') + 0.15
T0['05'] = S_HERO + 0.25                            # K: "Hide? I'm the hero."
T_SHADOW = tend('05') + 0.3                         # his shadow is thrown ahead of him by the cone: he stops
S_TURN = T_SHADOW + 1.2
T_TURN = (S_TURN + 0.15, S_TURN + 0.75)             # he turns: the face is right there
S_FLAME = S_TURN + 2.0                              # wordless beat = S_TURN .. S_FLAME
T0['06'] = S_FLAME + 0.35                           # N: "But fire never stands still."
S_HAT = tend('06') + 0.3
T_THROW = S_HAT + 0.6; T_LANDHAT = T_THROW + 1.25
T_GRAB = (T_THROW + 0.45, T_THROW + 1.05)
T0['07'] = T_LANDHAT + 0.2                          # N: "Every night, someone has to move."
S_DAWN = tend('07') + 0.3
T_SUN = (S_DAWN, S_DAWN + 1.3)                      # time-lapse sunrise
T0['08'] = S_DAWN + 1.0                             # N: "At dawn, every NPC respawns."
T_RESPAWN = we('08', 0) - 0.55
T_HATON = (T_RESPAWN + 0.6, T_RESPAWN + 1.4)
T0['09'] = max(tend('08') + 0.3, T_HATON[1] - 0.2)  # Bram: "Nice weather today!"
S_LOOP = tend('09') + 0.35
T_NIGHT = (S_LOOP, S_LOOP + 1.0)                    # time-lapse back to night
DUR = round(S_LOOP + 2.4, 3); N = int(round(DUR * FPS))
LINES = [(k, T0[k]) for k in KEYS]
def fr(x): return int(round(x * FPS))
CUTS = [('open', 0.0), ('eyes', S_EYES), ('reveal', S_REVEAL), ('cat', S_CAT), ('hero', S_HERO), ('turn', S_TURN), ('flame', S_FLAME),
        ('hat', S_HAT), ('dawn', S_DAWN), ('loop', S_LOOP)]
SEQS = [('s1', 0, fr(S_CAT)), ('s2', fr(S_CAT), fr(S_TURN)), ('s3', fr(S_TURN), fr(S_HAT)), ('s4', fr(S_HAT), fr(S_DAWN)), ('s5', fr(S_DAWN), N)]
def scene(t):
    nm = CUTS[0][0]
    for n_, a in CUTS:
        if t >= a: nm = n_
    return nm
def talking(t, key):
    if key not in T0: return 0.0
    for a, b, _ in SCR['sent'][key]:
        if T0[key] + a <= t < T0[key] + b: return 0.5 + 0.5 * math.sin((t - T0[key]) * 17.0)
    return 0.0
def night(t):
    """1 = night, 0 = day (dawn time-lapse, then back to night for the loop)"""
    if t < T_SUN[0]: return 1.0
    if t < T_NIGHT[0]: return 1 - sm(seg01(t, *T_SUN))
    return sm(seg01(t, *T_NIGHT))
def dawn_left(t):
    """the DAWN counter in seconds (30 -> 0 by S_DAWN; back to 30 for the loop)"""
    if t >= T_NIGHT[0] + 0.5: return 30
    if t >= S_DAWN: return 0
    return max(0, int(math.ceil(30 * (1 - t / S_DAWN))))
def detect(t):
    """the Watcher's detection of the knight 0..1 (the meter)"""
    if t < T_OPEN + 0.3 or t >= T_GRAB[0] + 0.3: return 0.0
    if t < S_CAT: return 0.06
    if t < T_YANK: return lerp(0.06, 0.3, seg01(t, S_CAT, T_YANK))
    if t < S_HERO: return 0.3
    if t < T_SHADOW: return lerp(0.3, 0.62, seg01(t, S_HERO, T_SHADOW))
    if t < S_TURN + 0.6: return lerp(0.62, 0.95, seg01(t, T_SHADOW, S_TURN + 0.6))
    if t < S_FLAME: return 0.95
    return lerp(0.95, 0.99, seg01(t, S_FLAME, T_THROW))

# ======================= set: the night street =======================
STREET = [(92, 88, 96), (84, 80, 90), (98, 94, 102), (80, 78, 86)]
GRASS = [(54, 70, 52), (48, 64, 48)]
WALLS = [(150, 140, 118), (142, 134, 114), (154, 144, 122), (146, 138, 116)]
ROOFS = [(150, 70, 52), (120, 64, 50), (136, 76, 56), (110, 70, 56)]
HOUSES = []
for i, z in enumerate((-8.5, -4.0, 0.6, 5.2, 9.8)):
    HOUSES.append((-3.0 - 1.7, z, -PI / 2, i))
    HOUSES.append((3.0 + 1.7, z + 1.4, PI / 2, i + 5))
def window_pts():
    """window centres on the facades (they glow warm until the eyes open)"""
    out = []
    for x, z, yaw, i in HOUSES:
        sd = -1 if x < 0 else 1; out.append(((sd * 2.98, 1.7, z - 0.95), (-sd, 0, 0), i))
    return out
WIN = window_pts()
def street_set():
    Q = dtx.ground(-3.0, 3.0, -14.0, 22.0, 0.75, STREET, seed=21)
    Q += dtx.ground(-24.0, -3.0, -14.0, 30.0, 3.0, GRASS, seed=22) + dtx.ground(3.0, 24.0, -14.0, 30.0, 3.0, GRASS, seed=23)
    Q += dtx.ground(-3.0, 3.0, 22.0, 40.0, 2.0, GRASS, seed=24)
    for x, z, yaw, i in HOUSES:
        Q += dtx.house(x, z, yaw, 4.0, 3.4, 2.8, WALLS[i % 4], ROOFS[i % 4], seed=i)
    # the cart, two lamp posts, a barrel, the village gate arch at the end of the street
    Q += hd.bx((-1.85, 0.62, 8.2), hd.Ry(0.2), (0.5, 0.06, 0.8), (110, 80, 52)) + hd.bx((-1.85, 0.3, 8.2), hd.Ry(0.2), (0.06, 0.3, 0.06), (86, 62, 42))
    for sd in (1, -1): Q += hd.lathe(V((-1.85, 0.34, 8.2)) + hd.Ry(0.2) @ V((sd * 0.56, 0, 0)), hd.Ry(0.2) @ hd.Rz(PI / 2), [(0.34, 0), (0.34, 0.06)], 12, (90, 66, 44))
    for (x, z) in ((-2.55, -1.6), (2.55, 7.6)): Q += hd.bx((x, 1.2, z), np.eye(3), (0.06, 1.2, 0.06), (60, 46, 34))
    Q += hd.lathe((-2.5, 0, 3.0), np.eye(3), [(0.28, 0.0), (0.32, 0.4), (0.28, 0.8)], 9, (110, 76, 46))
    for sd in (1, -1): Q += hd.bx((sd * 2.4, 1.8, 15.0), np.eye(3), (0.4, 1.8, 0.4), (120, 116, 112))
    Q += hd.bx((0, 3.75, 15.0), np.eye(3), (2.8, 0.2, 0.45), (100, 74, 52))
    for i in range(14):                                                               # trees beyond the village
        x = (5 + 14 * hsh(i, 31)) * (1 if i % 2 else -1); z = 17 + 16 * hsh(i, 32)
        Q += dtx.tree(x, z, 4 + 3 * hsh(i, 33), col=(30, 44, 40), trunk=(44, 34, 28), seed=i)
    return [q for q in Q if q]
SET = None
def set_faces():
    global SET
    if SET is None: SET = street_set()
    return SET
PUDDLES = [(-0.9, -2.2, 0.55), (-0.6, 3.4, 0.5), (1.0, 5.2, 0.6), (0.4, 8.6, 0.5)]
def puddles(t, nt):
    """dark puddles with a moon glint; rings ripple after every THOOM"""
    Q = []
    for i, (x, z, r) in enumerate(PUDDLES):
        col = mixc((150, 170, 200), (24, 30, 48), nt)
        Q += hd.poly_decal((x, 0.012, z), (0, 1.0, 0), (0, 0, 1.0), [(r * math.cos(a), 0.7 * r * math.sin(a)) for a in np.linspace(0, 2 * PI, 12)[:-1]], col, emit=True, lift=0.0)
        Q += hd.poly_decal((x + 0.15, 0.014, z - 0.08), (0, 1.0, 0), (0, 0, 1.0), [(0.09 * math.cos(a), 0.05 * math.sin(a)) for a in np.linspace(0, 2 * PI, 8)[:-1]], mixc((230, 230, 220), (170, 190, 230), nt), emit=True, lift=0.0)
        for th in THOOMS:
            u = (t - th) / 0.9
            if 0 <= u < 1:
                rr = r * (0.2 + 0.8 * u); c2 = mixc((130, 150, 190), (40, 48, 70), u)
                for a in np.linspace(0, 2 * PI, 14)[:-1]:
                    b = a + 2 * PI / 13
                    q = hd.face([(x + rr * math.cos(a), 0.016, z + 0.7 * rr * math.sin(a)), (x + rr * math.cos(b), 0.016, z + 0.7 * rr * math.sin(b)),
                                 (x + (rr + 0.03) * math.cos(b), 0.016, z + 0.7 * (rr + 0.03) * math.sin(b)), (x + (rr + 0.03) * math.cos(a), 0.016, z + 0.7 * (rr + 0.03) * math.sin(a))], c2, emit=True)
                    if q: Q.append(q)
    return Q
def windows(t):
    """warm windows that click off one by one after the eyes open (back on at dawn? no: dawn = daylight; on again in the loop night)"""
    Q = []
    for k, (c, n, i) in enumerate(WIN):
        off_t = T_OPEN + 0.25 + 0.22 * (k % 7)
        lit = (t < off_t) or (t >= T_NIGHT[0] + 0.6)
        if night(t) < 0.5: continue
        col = (255, 196, 110) if lit else (22, 22, 32)
        Q += hd.decal(V(c) + V(n) * 0.02, n, (0, 1, 0), 0.6, 0.5, col, emit=lit, lift=0.0)
    return Q
def sky(t, zc):
    """night dome (stars, moon) <-> dawn dome; moves with the camera"""
    nt = night(t)
    def col(e):
        top_n, hor_n = (10, 14, 34), (34, 44, 78); top_d, hor_d = (110, 150, 214), (255, 196, 150)
        return mixc(mixc(hor_d, top_d, min(1, e * 1.6)), mixc(hor_n, top_n, min(1, e * 1.6)), nt)
    Q = hd.ellip((0, -6, zc), np.eye(3), (110, 80, 110), 22, 9, (20, 24, 40), v1=PI * 0.54, closed=False, colfn=lambda i, j, cl: col(max(0.0, cl[1] / 80)))
    for q in Q: q['emit'] = True
    if nt > 0.3:
        for i in range(50):
            a = 2 * PI * hsh(i, 71); e = 0.25 + 0.6 * hsh(i, 72); r = 90; x = r * math.cos(e) * math.sin(a); y = r * math.sin(e) - 6; z = zc + r * math.cos(e) * math.cos(a); s = 0.35
            Q.append(hd.face([(x - s, y, z), (x, y - s, z), (x + s, y, z), (x, y + s, z)], mixc((20, 24, 40), (220, 226, 240), nt), emit=True))
            Q.append(hd.face([(x - s, y, z), (x, y + s, z), (x + s, y, z), (x, y - s, z)], mixc((20, 24, 40), (220, 226, 240), nt), emit=True))
        mc = V((-30.0, 38.0, zc + 60.0))
        for sgn in (1, -1): Q.append(hd.face([mc + V((5 * math.cos(a), 5 * math.sin(a), 0)) for a in np.linspace(0, sgn * 2 * PI, 16)[:-1]], mixc((40, 44, 60), (236, 236, 222), nt), emit=True))
    if nt < 0.9:                                                                          # the sun comes up behind the houses
        sy = lerp(-6.0, 18.0, 1 - nt); sc_ = V((25.0, sy, zc + 70.0))
        for sgn in (1, -1): Q.append(hd.face([sc_ + V((7 * math.cos(a), 7 * math.sin(a), 0)) for a in np.linspace(0, sgn * 2 * PI, 16)[:-1]], (255, 236, 180), emit=True))
    return [q for q in Q if q]

# ======================= cast =======================
KN = dtx.KNIGHT
def knight(P):
    Q = hd.human(KN, P); RW = P['_RW']; ch = P['_chest']; st = (178, 186, 200); dk = (128, 136, 152)
    for sd in (1, -1):
        c = ch + RW @ V((sd * 0.19, 0.075, -0.01))
        Q += hd.ellip(c, RW @ hd.Rz(-sd * 0.35), (0.1, 0.07, 0.1), 10, 5, st, v1=PI * 0.6, colfn=lambda i, j, cl: dk if i == 2 else st)
        kn = P['_' + ('r' if sd > 0 else 'l') + 'knee']; Q += hd.ellip(kn, RW, (0.06, 0.06, 0.065), 8, 4, st)
    Q += hd.ellip(ch + RW @ V((0, -0.02, 0.035)), RW, (0.17, 0.17, 0.1), 12, 6, st, keep=lambda c: c[2] > 0.0, colfn=lambda i, j, cl: dk if (j % 6 == 0) else st)
    Q += dtx.knight_helmet(P)
    return Q
MARTA = dtx.WOMAN; BRAM = dtx.VIL3
VILS = [(dtx.VIL1, (-2.1, 5.0), PI / 2 + 0.4), (dtx.VIL2, (2.1, 6.6), -PI / 2), (dtx.KID, (-1.9, -2.9), 0.6)]
M_POS = (0.25, 1.15); B_POS = (1.75, 2.75)
HAT = (196, 36, 40)
def red_hat(c, R, s=1.0):
    c = V(c, float)
    Q = hd.lathe(tuple(c), R, [(0.13 * s, 0.0), (0.12 * s, 0.03 * s), (0.085 * s, 0.12 * s), (0.04 * s, 0.24 * s), (0.005, 0.3 * s)], 10, HAT)
    Q += hd.lathe(tuple(c - R @ V((0, 0.005, 0))), R, [(0.17 * s, 0.0), (0.17 * s, 0.02 * s)], 10, hd.shade(HAT, 0.8))
    return [q for q in Q if q]
def cat(c, yaw, ph, s=1.0):
    c = V(c, float); R = hd.Ry(yaw); BK = (22, 20, 26)
    Q = hd.ellip(tuple(c + R @ V((0, 0.17, 0))), R, (0.08, 0.075, 0.2), 8, 5, BK)
    Q += hd.ellip(tuple(c + R @ V((0, 0.27, 0.2))), R, (0.07, 0.065, 0.07), 8, 5, BK)
    for sd in (1, -1):
        Q.append(hd.face([c + R @ V((sd * 0.025, 0.32, 0.21)), c + R @ V((sd * 0.07, 0.31, 0.2)), c + R @ V((sd * 0.05, 0.38, 0.2))], BK))
        Q += hd.decal(c + R @ V((sd * 0.028, 0.285, 0.265)), R @ V((0, 0, 1.0)), (0, 1, 0), 0.018, 0.014, (220, 220, 120), emit=True)
    for k_, (lx, lz) in enumerate(((0.05, 0.13), (-0.05, 0.13), (0.05, -0.13), (-0.05, -0.13))):
        sw = 0.09 * math.sin(ph + (k_ % 2) * PI + (k_ // 2) * PI * 0.5)
        Q += hd.limb(tuple(c + R @ V((lx, 0.13, lz))), tuple(c + R @ V((lx, 0.0, lz + sw))), 0.018, 0.014, BK, n=5, m=1)
    Q += hd.limb(tuple(c + R @ V((0, 0.2, -0.19))), tuple(c + R @ V((0, 0.36, -0.32))), 0.016, 0.01, BK, n=5, m=1)
    return [q for q in Q if q]

# ----------------------- the Watcher -----------------------
ROBE = (24, 26, 36); ROBE2 = (32, 34, 46); MASK = (168, 162, 152); MASK_D = (120, 114, 108); HANDC = (170, 164, 156); WEYE = (255, 244, 196)
def watcher(base, head, lean=0.0, reach=None, eyes=1.0, esz=1.0):
    """the Watcher: a 6 m hooded robe of fog-dark cloth, a long neck, a cracked white mask with two lantern eyes,
    long sleeves and very long pale fingers. head = world centre of the mask; reach = where the right hand's fingers go (or None)"""
    base = V(base, float); head = V(head, float); Q = []
    sh_c = base + V((0, 4.25, 0))
    Q += hd.lathe(tuple(base), np.eye(3), [(0.95, 0.0), (0.78, 1.0), (0.6, 2.4), (0.5, 3.6), (0.56, 4.25)], 14, ROBE,
                  colfn=lambda i, j: ROBE2 if j % 2 else ROBE, cap0=False)
    Q += hd.ellip(tuple(sh_c), np.eye(3), (0.75, 0.22, 0.45), 12, 5, ROBE2)
    d = nz(head - sh_c); Q += hd.limb(tuple(sh_c), tuple(head - d * 0.35), 0.2, 0.17, ROBE, n=8, m=3)
    fwd = V((head[0] - sh_c[0], 0, head[2] - sh_c[2]))
    fwd = nz(fwd) if np.linalg.norm(fwd) > 0.05 else V((0, 0, -1.0))
    yaw = math.atan2(fwd[0], fwd[2]); Rh = hd.Ry(yaw) @ hd.Rx(0.2 + lean)
    Q += hd.ellip(tuple(head + Rh @ V((0, 0.06, -0.08))), Rh, (0.44, 0.58, 0.42), 12, 8, ROBE2, keep=lambda c: c[2] < 0.16)       # the hood
    Q += hd.ellip(tuple(head), Rh, (0.3, 0.42, 0.2), 12, 8, MASK, keep=lambda c: c[2] > -0.02,
                  colfn=lambda i, j, cl: MASK_D if cl[1] < -0.25 else MASK)                                                   # the mask
    Q += hd.decal(tuple(head + Rh @ V((0.06, 0.05, 0.205))), Rh @ V((0, 0, 1.0)), Rh @ V((0.25, 1.0, 0)), 0.012, 0.3, (60, 56, 52), lift=0.006)   # the crack
    for sd in (1, -1):
        ec = head + Rh @ V((sd * 0.11, 0.1, 0.18))
        Q += hd.ellip(tuple(ec), Rh, (0.085 * esz, 0.06 * esz, 0.03), 8, 4, (16, 14, 18))                                       # socket
        E = hd.ellip(tuple(ec + Rh @ V((0, 0, 0.018))), Rh, (0.06 * esz, 0.042 * esz, 0.02), 8, 4, mixc((40, 40, 50), WEYE, eyes))
        for q in E: q['emit'] = eyes > 0.05
        Q += E
    for sd in (1, -1):
        s_ = sh_c + V((sd * 0.72, -0.05, 0))
        tgt = V(reach, float) if (reach is not None and sd > 0) else s_ + V((sd * 0.35, -2.2, 0.5))
        el = (s_ + tgt) / 2 + V((sd * 0.45, 0.5, 0))
        Q += hd.limb(tuple(s_), tuple(el), 0.2, 0.17, ROBE, n=8, m=2) + hd.limb(tuple(el), tuple(tgt), 0.17, 0.2, ROBE2, n=8, m=2)   # sleeves
        dd = nz(tgt - el); Q += hd.ellip(tuple(tgt + dd * 0.08), rot_y(dd), (0.08, 0.05, 0.1), 8, 4, HANDC)
        side = nz(np.cross(dd, V((0, 1.0, 0))))
        for k_ in range(4):
            sp = (k_ - 1.5) * 0.22; a0 = tgt + dd * 0.14 + side * sp * 0.15
            mid = a0 + nz(dd + side * sp) * 0.45; tip = mid + nz(dd + side * sp * 1.4 + V((0, -0.35, 0))) * 0.4
            Q += hd.limb(tuple(a0), tuple(mid), 0.025, 0.018, HANDC, n=5, m=1) + hd.limb(tuple(mid), tuple(tip), 0.018, 0.006, HANDC, n=5, m=1)
    return [q for q in Q if q], Rh
W_BASE0 = V((0.6, 0.0, 13.0))                                                                 # far down the street, in the fog
def watcher_state(t):
    """(base, head, lean, reach, eyes 0..1) or None"""
    if t < S_REVEAL or night(t) < 0.5 and t < T_NIGHT[0]: return None
    if t >= T_NIGHT[0]: return None
    eyes = sm(seg01(t, T_OPEN - 0.1, T_OPEN + 0.25))
    base = V(W_BASE0); head = base + V((0, 5.4, -0.4))
    if t >= S_HERO:                                                                           # it glides up behind the knight
        u = sm(seg01(t, S_HERO, S_TURN)); kz = knight_pos(t)[2]
        base = lerp3(tuple(W_BASE0), (0.1, 0.0, kz + 3.6), u); base = V(base); head = base + V((0, lerp(5.4, 4.2, u), lerp(-0.4, -1.8, u)))
    if t >= S_TURN:
        kz = knight_pos(t)[2]; base = V((0.1, 0.0, kz + 3.2)); head = V((0.15, 2.05, kz + 0.75))
    reach = None
    if t >= T_GRAB[0] and t < T_GRAB[1] + 1.5:                                                 # the fingers come for Bram
        u = sm(seg01(t, T_GRAB[0], T_GRAB[1])); bp = V((B_POS[0], 1.2, B_POS[1]))
        base = V((0.6, 0.0, 11.0)); head = base + V((0, 4.8, -0.8)); reach = tuple(lerp3(tuple(base + V((0.8, 3.6, -0.6))), tuple(bp), u))
        if t > T_GRAB[1]:
            bx = V(bram_state(t)[0]['base']) if bram_state(t)[0] is not None else V((0.6, 2.2, 10.0)); reach = tuple(bx + V((0.0, 1.5, 0.0)))
    if T_LANDHAT <= t < S_DAWN: base = V((0.6, 0.0, 12.0 + 8 * seg01(t, T_LANDHAT, S_DAWN))); head = base + V((0, 5.0, -0.6))
    return base, head, 0.0, reach, eyes

# ----------------------- poses -----------------------
Z_ARR = 0.15; X_K = -0.55                                                    # frame 0: the knight arrives next to Marta
def knight_pos(t):
    """(x, yaw, z, walking speed)"""
    if t >= S_LOOP:                                                                          # the loop: a new hero walks in = frame 0
        u = t - DUR; return X_K, 0.0, Z_ARR + 1.3 * u if u < 0 else Z_ARR, 1.3
    if t < S_HERO:
        z = Z_ARR + 1.3 * (t - t * t / 1.2) if t < 0.6 else Z_ARR + 0.39
        return X_K, 0.0, z, (1.3 * (1 - t / 0.6) if t < 0.6 else 0.0)
    # "Hide? I'm the hero." he turns his back to the fog and swaggers down the street (towards -z), stops at his shadow
    z0 = Z_ARR + 0.39; u = seg01(t, T0['05'] + 0.45, T_SHADOW); z = z0 - 2.4 * sm(u)
    yaw = PI * sm(seg01(t, T0['05'] - 0.25, T0['05'] + 0.45))
    return lerp(X_K, -0.5, sm(u)), yaw, z, (1.3 if 0.02 < u < 0.98 else 0.0)
def smooth_pose(fn, t, span=0.12):
    """average every numeric pose value over +-span (weights 1-2-3-2-1), only with samples from the same shot"""
    P0 = fn(t)
    if P0 is None: return None
    sc = scene(t); S_ = []
    for dt, w in ((-span, 1), (-span / 2, 2), (0.0, 3), (span / 2, 2), (span, 1)):
        ts = t + dt
        if ts < 0 or ts >= DUR or scene(ts) != sc: continue
        P = P0 if dt == 0 else fn(ts)
        if P is not None: S_.append((P, w))
    out = dict(P0)
    for k, v in P0.items():
        if k.startswith('_') or isinstance(v, (str, bool)) or v is None: continue
        vals = [(P.get(k), w) for P, w in S_]
        if any(x is None or type(x) != type(v) for x, _ in vals): continue
        wt = sum(w for _, w in vals)
        if isinstance(v, (int, float)): out[k] = sum(float(x) * w for x, w in vals) / wt
        elif isinstance(v, (tuple, list)) and all(len(x) == len(v) for x, _ in vals):
            out[k] = tuple(sum(float(x[i]) * w for x, w in vals) / wt for i in range(len(v)))
    return out
def knight_pose(t):
    x, yaw, z, v = knight_pos(t); tt = t - DUR if t >= S_LOOP else t
    P = dict(base=(x, 0.0, z), yaw=yaw, eyes='open', mouth='smile', brow=0.2, lean=0.04, cape_sway=0.2 * math.sin(t * 1.7), head=(0.0, 0.0, 0.0))
    P['rh'] = (0.22, 1.18, 0.32); P['rgrip'] = 0.95; P['rpalm'] = (-1.0, 0.0, 0.0)                   # the torch, held forward
    P['lh'] = (-0.24, 1.0, 0.1); P['lgrip'] = 0.4
    P['walk'] = 2 * PI * 0.9 * tt; P['stride'] = 0.3 * min(1.0, v / 1.3)
    if t >= S_LOOP or t < S_EYES + 0.2:                                                       # frame 0 / loop: the wave in front of her face
        wv = win(tt, -0.6, S_EYES + 0.2, 0.3) if t < S_LOOP else sm(seg01(t, DUR - 0.6, DUR))
        if wv > 0:
            fc = V((M_POS[0] - 0.2, 1.52, M_POS[1] - 0.05)); base_ = V((x, 0.0, z))
            hw = lerp3(tuple(base_ + V((-0.24, 1.0, 0.1))), tuple(fc), wv); P.pop('lh', None)
            P['lh_w'] = (hw[0], hw[1], hw[2] + 0.07 * math.sin(tt * 13) * wv); P['lgrip'] = 0.1; P['lpalm'] = (1.0, 0.0, 0.2); P['lpalm_local'] = False
            P['head'] = (0.55 * wv, 0.0, 0.0); P['look'] = (0.6 * wv, 0.0)
            P['mouth'] = 'open' if talking(t, '01') > 0.5 else 'smile'
    if S_EYES + 0.2 <= t < S_HERO:
        P['head'] = (0.45, 0.0, 0.0); P['mouth'] = 'open' if talking(t, '01') > 0.5 else 'smile'
        if t >= S_REVEAL: P['mouth'] = 'neutral'; P['brow'] = 0.1; P['head'] = (0.0, 0.15, 0.0)
        if t >= S_CAT: P['_sword'] = True; P['lh'] = (-0.3, 1.25, 0.35); P['lgrip'] = 0.9                 # draws the sword
    if t >= S_HERO and t < S_TURN:
        P['_sword'] = True; P['lh'] = (-0.3, 1.25, 0.35); P['lgrip'] = 0.9
        P['mouth'] = 'open' if talking(t, '05') > 0.5 else 'smile'; P['brow'] = -0.2; P['head'] = (0.0, 0.05, 0.05)
        if t >= T_SHADOW - 0.2:                                                                       # he sees the light + his long shadow: stops
            u = sm(seg01(t, T_SHADOW - 0.2, T_SHADOW + 0.3)); P['head'] = (0.0, -0.35 * u, 0.0); P['look'] = (0.0, -0.6 * u); P['mouth'] = 'neutral' if u > 0.5 else P['mouth']
            P['eyes'] = 'wide' if u > 0.5 else 'open'; P['brow'] = 0.0
    if t >= S_TURN and t < S_HAT + 2.0:
        P['_sword'] = True; P['lh'] = (-0.3, 1.25, 0.35); P['lgrip'] = 0.9
        u = sm(seg01(t, *T_TURN)); P['yaw'] = PI - 0.0; P['head'] = (PI * 0.62 * u, 0.12 * u, 0.0); P['twist'] = 0.55 * u; P['look'] = (0.6 * u, 0.25 * u)
        P['eyes'] = 'wide'; P['brow'] = -0.4; P['mouth'] = 'o' if u > 0.6 else 'neutral'
        P['lf'] = (-0.11, 0.075 + 0.12 * u, 0.12 * u)                                                 # frozen mid-step, one foot up
        if t >= S_FLAME: P['look'] = (0.6, -0.35)                                                     # eyes down to the torch
        if t >= T_THROW: P['look'] = (0.2, 0.0)
    if t >= S_HAT + 2.0 and t < S_LOOP:                                                               # dawn: relaxes, stunned
        P['_sword'] = False; P['eyes'] = 'open'; P['mouth'] = 'neutral'; P['brow'] = -0.3; P['head'] = (0.3, 0.0, 0.0)
    return P
EYE_DIR = -0.9
def marta_pose(t):
    """frozen facing the wall; only her eyes move; at dawn she turns, picks up the hat, puts it on Bram; back to the wall in the loop"""
    P = dict(base=(M_POS[0], 0.0, M_POS[1]), yaw=-PI / 2, eyes='open', mouth='neutral', brow=-0.3, lean=0.08, head=(0.0, 0.0, 0.0))
    P['lh'] = (-0.12, 1.12, 0.3); P['rh'] = (0.1, 0.85, 0.42); P['lgrip'] = 0.9; P['rgrip'] = 0.9; P['_broom'] = True
    if S_EYES <= t < S_REVEAL:
        P['look'] = (EYE_DIR * sm(seg01(t, T_EYE_MOVE, T_EYE_MOVE + 0.5)), 0.0); P['eyes'] = 'wide' if t > T_EYE_MOVE + 0.3 else 'open'
    if T0['03'] - 0.1 <= t < tend('03') + 0.2: P['look'] = (-EYE_DIR, 0.0); P['eyes'] = 'half'
    if S_DAWN + 0.6 <= t < T_NIGHT[1]:
        u = sm(seg01(t, S_DAWN + 0.6, S_DAWN + 1.1)); P['yaw'] = lerp(-PI / 2, -2.4, u); P.pop('_broom', None); P['eyes'] = 'open'; P['mouth'] = 'smile'; P['brow'] = 0.0
        hp = V((B_POS[0] - 0.2, 0.0, B_POS[1] + 0.6)); m0 = V((M_POS[0], 0.0, M_POS[1]))
        w = sm(seg01(t, S_DAWN + 0.9, T_HATON[0]));  P['base'] = tuple(lerp3(tuple(m0), tuple(hp), w))
        if 0.02 < w < 0.98: P['walk'] = 2 * PI * 1.2 * t; P['stride'] = 0.25
        if t >= T_HATON[0]:
            h_ = win(t, T_HATON[0], T_HATON[1] + 0.2, 0.3); P['lh'] = lerp3((-0.2, 0.9, 0.05), (0.15, 1.75, 0.45), h_); P['rh'] = lerp3((0.2, 0.9, 0.05), (0.35, 1.75, 0.45), h_)
        if t >= T_NIGHT[0]:                                                                            # back to her wall
            r = sm(seg01(t, T_NIGHT[0], T_NIGHT[0] + 0.8)); P['base'] = tuple(lerp3(tuple(hp), tuple(m0), r)); P['yaw'] = lerp(-2.4, -PI / 2, r)
            if r > 0.9: P['_broom'] = True; P['lh'] = (-0.12, 1.12, 0.3); P['rh'] = (0.1, 0.85, 0.42)
            P['walk'] = 2 * PI * 1.4 * t; P['stride'] = 0.3; P['mouth'] = 'neutral'
    elif S_DAWN <= t < S_DAWN + 0.6: P['mouth'] = 'neutral'
    return P
def bram_state(t):
    """'here' / 'gone' / 'respawn' + pose"""
    P = dict(base=(B_POS[0], 0.0, B_POS[1]), yaw=-PI / 2 - 0.35, eyes='open', mouth='neutral', brow=-0.2, head=(0.0, 0.0, 0.0))
    P['lh'] = (-0.22, 0.92, 0.12); P['rh'] = (0.22, 0.92, 0.12)
    hat = 'head'
    if S_HAT - 0.6 <= t < T_GRAB[1]:
        P['head'] = (0.25, 0.0, 0.0); P['look'] = (0.4, 0.0)                                       # looks at the knight
        g = sm(seg01(t, S_HAT, T_THROW)); P['rh'] = lerp3((0.2, 0.9, 0.05), (0.08, 1.82, 0.05), g); P['rgrip'] = 0.8   # takes his hat
        if t < T_THROW and g > 0.9: hat = 'hand'
        if t >= T_THROW:
            th = sm(seg01(t, T_THROW, T_THROW + 0.25)); P['rh'] = lerp3((0.08, 1.82, 0.05), (0.55, 1.7, 0.6), th); P['rgrip'] = lerp(0.8, 0.1, th); hat = 'fly'
            P['yaw'] = -PI / 2 - 0.35 - 0.4 * th; P['eyes'] = 'half'; P['mouth'] = 'soft'
    if T_GRAB[1] - 0.1 <= t < T_GRAB[1] + 1.5:                                                     # taken: lifted, then drawn back into the fog
        lift = sm(seg01(t, T_GRAB[1] - 0.1, T_GRAB[1] + 0.5)); pull = seg01(t, T_GRAB[1] + 0.4, T_GRAB[1] + 1.5) ** 2
        P['base'] = (lerp(B_POS[0], 0.6, pull), 0.9 * lift + 2.2 * pull, lerp(B_POS[1], 10.0, pull)); P['eyes'] = 'wide'; P['mouth'] = 'o'
        P['lh'] = (-0.4, 1.7, 0.2); P['rh'] = (0.4, 1.7, 0.2); hat = 'fly' if t < T_LANDHAT else 'ground'
    if t >= T_GRAB[1] + 1.5 and t < T_RESPAWN: return None, ('ground' if t < T_HATON[0] else 'marta')
    if T_RESPAWN <= t < S_LOOP + 0.8:
        P['yaw'] = -PI / 2 - 0.35 - (0.9 if t < T_NIGHT[0] else 0.9 * (1 - sm(seg01(t, T_NIGHT[0], T_NIGHT[0] + 0.6))))
        P['mouth'] = 'open' if talking(t, '09') > 0.5 else 'smile'; P['brow'] = 0.2; P['eyes'] = 'open'
        hat = 'marta' if t < T_HATON[1] - 0.25 else 'head'
        if t >= T_NIGHT[0] + 0.5: P['mouth'] = 'neutral'
    if t >= T_LANDHAT and hat == 'fly' and t < T_RESPAWN: hat = 'ground'
    return P, hat
HAT_LAND = V((-0.6, 0.02, 3.4))
def vil_pose(i, t):
    sp, (x, z), yaw = VILS[i]
    P = dict(base=(x, 0.0, z), yaw=yaw, eyes='open', mouth='neutral', brow=-0.2, head=(0.0, 0.0, 0.0))
    if i == 0: P['rh'] = (0.25, 1.6, 0.35); P['lh'] = (-0.2, 1.45, 0.3); P['rgrip'] = 0.8; P['lgrip'] = 0.8
    if i == 1: P['rh'] = (0.22, 0.6, 0.15); P['rgrip'] = 0.9; P['lean'] = 0.25
    if i == 2: P['rf'] = (0.11, 0.2, 0.18); P['lh'] = (-0.2, 1.0, -0.1); P['rh'] = (0.25, 1.05, 0.2)          # the kid: frozen mid-step
    day = 1 - night(t)
    if day > 0.3 and t < T_NIGHT[1]:
        P['yaw'] = yaw + 0.6 * min(1.0, day * 1.4) * (1 if x < 0 else -1); P['mouth'] = 'smile'; P['brow'] = 0.1; P['eyes'] = 'open'
        P['lh'] = (-0.3, 1.0 + 0.4 * max(0, math.sin(t * 4 + i)), 0.1)
    return P

# =====================================================================================================================
#                                                      CAMERA
# =====================================================================================================================
O_POS = V((-1.25, 1.35, Z_ARR + 2.45)); O_TGT = V((-0.15, 1.3, Z_ARR + 0.5)); O_FOV = 42.0
def cam_shot(t):
    sc = scene(t); idx = [n for n, _ in CUTS].index(sc); a = CUTS[idx][1]; b = CUTS[idx + 1][1] if idx + 1 < len(CUTS) else DUR; u = sm(seg01(t, a, b))
    if sc in ('open', 'loop'):
        tt = t if sc == 'open' else t - DUR
        k = motion.creep(max(0.0, tt), 0.0, 0.0065) if tt >= 0 else 1.0
        if sc == 'loop':                                                                       # pulls back in on the frame-0 framing at DUR
            s = sm(seg01(t, S_LOOP, DUR - 0.4)); p0 = V((-0.35, 1.6, 1.85)); t0_ = V((1.4, 1.4, 2.6))
            return V(lerp3(tuple(p0), tuple(O_POS), s)), V(lerp3(tuple(t0_), tuple(O_TGT), s)), lerp(48.0, O_FOV, s)
        return V(motion.dolly(tuple(O_POS), tuple(O_TGT), k)), O_TGT, O_FOV
    if sc == 'eyes':
        hc = V((M_POS[0] - 0.05, 1.5, M_POS[1])); p = hc + V((-0.62, 0.04, 0.22)); return V(motion.dolly(tuple(p), tuple(hc), motion.creep(t, a, 0.002))), hc, 30.0
    if sc == 'reveal':
        p0 = V((0.4, 1.3, -3.6)); p1 = V((0.3, 1.45, -1.6)); tg = V((0.3, lerp(2.6, 4.4, sm(seg01(t, a, T_OPEN + 0.4))), 18.0))
        return V(lerp3(tuple(p0), tuple(p1), u)), tg, 40.0
    if sc == 'cat':
        p = V((-1.7, 0.75, lerp(1.4, 1.7, u))); return p, V((0.5, 0.5, 3.4)), 48.0
    if sc == 'hero':
        kx, _, kz, _ = knight_pos(t); return V((kx + 0.9, 1.45, kz - 2.6 + 0.4 * u)), V((kx - 0.1, 1.35, kz + 0.8)), 46.0
    if sc == 'turn':
        kx, _, kz, _ = knight_pos(t); p = V((kx - 0.55, 1.62, kz - 1.15)); tg = V((kx + 0.15, 1.85, kz + 0.45))
        return V(motion.dolly(tuple(p), tuple(tg), motion.creep(t, a, 0.002))), tg, 52.0
    if sc == 'flame':
        kx, _, kz, _ = knight_pos(t); tg = V((kx + 0.12, 1.4, kz - 0.25)); p = tg + V((-0.25, 0.08, -0.75))
        return V(motion.dolly(tuple(p), tuple(tg), motion.creep(t, a, 0.003))), tg, 40.0
    if sc == 'hat':
        p = V((-0.25, 1.6, 1.85 + 0.15 * u)); tg = V(lerp3((1.6, 1.55, 2.95), tuple(HAT_LAND + V((0.4, 0.5, 0.0))), sm(seg01(t, T_GRAB[1] - 0.1, T_LANDHAT + 0.3))))
        return p, tg, 46.0
    if sc == 'dawn':
        p = V((-0.35, 1.6, 2.05 - 0.2 * u)); tg = V((1.4, 1.4, 2.6)); return p, tg, 50.0
    return O_POS, O_TGT, O_FOV

# =====================================================================================================================
#                                                      RENDER
# =====================================================================================================================
def proj_shadow(Q, L, col=(8, 10, 20)):
    """flatten faces onto the ground (y = 0.013) as seen from the light point L (dark emissive)"""
    L = V(L, float); out = []
    for q in Q:
        pts = []
        for p in q['p']:
            p = V(p); d = p - L
            if d[1] >= -1e-3: pts = None; break
            s = (0.013 - L[1]) / d[1]; pts.append(tuple(L + d * s))
        if pts:
            f = hd.face(pts, col, emit=True)
            if f is not None:
                if f['n'][1] < 0: f = hd.face(pts[::-1], col, emit=True)
                if f is not None: out.append(f)
    return out
def world(t):
    pos, tgt, fov = cam_shot(t); nt = night(t); zc = float(pos[2])
    KP = smooth_pose(knight_pose, t); QK = knight(KP)
    layers = [sky(t, zc), set_faces(), puddles(t, nt), windows(t)]
    # the torch in his left hand (flame always moves)
    tc = grip_pt(KP, 'r', 0.05, 0.0) + V((0.0, 0.2, 0.0))
    if t < S_HAT + 2.0 or t >= S_LOOP:
        ax = nz(np.cross(KP['_rdir'], KP['_rpalm'])); ax = ax if ax[1] > 0 else -ax; ax = nz(ax + V((0, 0.6, 0)))
        g0 = grip_pt(KP, 'r', 0.04, 0.0); tc = g0 + ax * 0.2
        layers.append(hd.limb(tuple(g0 - ax * 0.2), tuple(tc), 0.016, 0.022, (82, 56, 34), n=6, m=1)
                      + hd.lathe(tuple(tc - ax * 0.04), rot_y(ax), [(0.03, 0.0), (0.034, 0.05)], 7, (52, 38, 28)))
        layers.append(dtx.torch_faces(tc + ax * 0.01, t * (1.6 if S_FLAME <= t < S_HAT else 1.0), k=0.62 if S_FLAME <= t < S_HAT else 0.5, seed=3, stick=False))
        KP['_flame'] = tc + ax * 0.08
    if KP.get('_sword'):
        gr = grip_pt(KP, 'l', 0.06, 0.0); d = hd.Ry(KP['yaw']) @ V((-0.05, 0.95, 0.45)); layers.append(hd.sword(tuple(gr), tuple(nz(d)), KP['_lpalm'], length=0.85))
    layers.append(QK)
    MP = smooth_pose(marta_pose, t); layers.append(hd.human(MARTA, MP))
    if MP.get('_broom'):
        a_ = grip_pt(MP, 'l', 0.05, 0.0); b_ = grip_pt(MP, 'r', 0.05, 0.0); d_ = nz(b_ - a_); tip = b_ + d_ * 0.75
        layers.append(hd.limb(tuple(a_ - d_ * 0.25), tuple(tip), 0.016, 0.016, (120, 86, 52), n=6, m=1) + hd.limb(tuple(tip), tuple(tip + d_ * 0.3), 0.03, 0.12, (190, 160, 90), n=8, m=1))
    BP, hat = bram_state(t)
    if BP is not None: BP = smooth_pose(lambda x: bram_state(x)[0], t)
    if BP is not None:
        sc_ = 1.0
        if T_RESPAWN <= t < T_RESPAWN + 0.4: sc_ = sm(seg01(t, T_RESPAWN, T_RESPAWN + 0.4))
        QB = hd.human(BRAM, BP)
        if sc_ < 1.0:
            c0 = V((B_POS[0], 0.0, B_POS[1]))
            k_ = 0.25 + 0.75 * sc_
            for q in QB: q['p'] = [tuple(c0 + (V(p) - c0) * k_) for p in q['p']]; refresh(q)
        layers.append(QB)
        if hat == 'head': layers.append(red_hat(V(BP['_head']) + BP['_RH'] @ V((0, 0.1, -0.01)), BP['_RH']))
        if hat == 'hand': layers.append(red_hat(grip_pt(BP, 'r', 0.05, 0.05), hd.Rx(2.6)))
    if hat == 'fly':
        u = seg01(t, T_THROW, T_LANDHAT); p0 = V((B_POS[0] - 0.4, 1.9, B_POS[1] + 0.1)); p = lerp3(tuple(p0), tuple(HAT_LAND), u); p = V(p) + V((0, 1.6 * math.sin(PI * u), 0))
        layers.append(red_hat(p, hd.Rz(u * 7.0) @ hd.Rx(u * 3.0)))
    elif hat == 'ground': layers.append(red_hat(HAT_LAND + V((0, 0.0, 0)), hd.Rx(1.4)))
    elif hat == 'marta': layers.append(red_hat(grip_pt(MP, 'r', 0.04, 0.06), hd.Rx(0.3)))
    for i in range(len(VILS)): layers.append(hd.human(VILS[i][0], smooth_pose(lambda x, i=i: vil_pose(i, x), t)))
    if T_CAT[0] - 0.3 <= t < T_YANK + 0.3:                                                       # the cat
        if t < T_SNAP: u = seg01(t, T_CAT[0], T_CAT[1]); c = V((lerp(-2.6, 2.4, u), 0.0, 3.2))
        else:
            u = sm(seg01(t, T_SNAP + 0.1, T_YANK + 0.3)); cs = V((lerp(-2.6, 2.4, seg01(T_SNAP, *T_CAT)), 0.0, 3.2)); c = V(lerp3(tuple(cs), (0.6, 4.5, 26.0), u ** 1.6))
        if t < T_YANK + 0.25: layers.append(cat(c, PI / 2, t * 22))
    ws_ = watcher_state(t)
    if ws_ is not None:
        base, head, lean, reach, eyes = ws_; QW, RW_ = watcher(base, head, lean, reach, eyes, 1.6 if scene(t) in ('reveal', 'cat') else 1.0); layers.append(QW); ws_ = ws_ + (RW_,)
    # lights: the moon (cool, from high left), the torch (warm, flicker), window glow before the eyes open, the eye glow; dawn sun
    L = []
    flick = 1.0 + 0.15 * math.sin(t * 23) + 0.1 * math.sin(t * 37)
    L.append((tuple(V(tgt) + V((-8.0, 12.0, 6.0))), mixc((255, 226, 190), (110, 130, 200), nt), lerp(26.0, 7.0, nt)))
    if t < S_HAT + 2.0 or t >= S_LOOP: L.append((tuple(tc + V((0, 0.35, 0.1))), (255, 170, 90), 0.9 * flick * nt + 0.1))
    if ws_ is not None and ws_[4] > 0.2:
        L.append((tuple(V(ws_[1]) + ws_[5] @ V((0, -0.4, 1.4))), (210, 220, 190), 0.6 * ws_[4]))
        ga = gaze_aim(t)
        if ga is not None: L.append((tuple(ga + V((0, 1.4, 0))), (220, 236, 200), 1.3 * ws_[4]))          # the spot really lights who stands in it
    if t >= S_HERO and t < S_TURN + 0.6 and ws_ is not None:                                      # the cone shines down on him from behind: his shadow
        layers.append(proj_shadow(QK, V(ws_[1]) + V((0, 0, -0.4))))
    return layers, L, (KP, MP, ws_)
def frame_low(t):
    pos, tgt, fov = cam_shot(t); nt = night(t)
    sh = sum(motion.kick(t, th, amp=0.03, frames=8) for th in THOOMS)
    pos = V(pos) + V((0.0, sh, 0.0)); cam = Camera.look(tuple(pos), tuple(tgt))
    layers, L, poses = world(t)
    fog = mixc((236, 206, 184), (22, 28, 50), nt)
    R = Renderer(W, H, fog=fog)
    img, vi, zb = zrender(R, cam, layers, L, fov=fov, fog_start=lerp(25.0, 5.0, nt), fog_end=lerp(80.0, 21.0, nt), ambient=lerp(0.45, 0.16, nt), return_z=True)
    a = look.outline(np.asarray(img).astype(np.float32), zb)
    a = np.clip((a - 80) * 1.12 + 84, 0, 255)
    if nt > 0.01: a = a * (1 - 0.25 * nt) + (a * np.array([0.78, 0.86, 1.18])) * 0.25 * nt        # moonlight blue grade
    return post.ps1(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), levels=6), vi, R, poses, zb

# ======================= overlays (1080 x 1920) =======================
def tw(s, sc): return font.width(s, sc)
def ctext(d, s, y, sc, col, o=4, x=None):
    x = int(540 - tw(s, sc) / 2) if x is None else x
    look.draw_cells(d, look.text_cells(s, x, y, sc, col), o)
TX = dict(dawn='ŞAFAK' if TRL else 'DAWN', cov=('NPC\'LER GECELERİ', 'NEDEN', 'KIPIRDAMAZ?') if TRL else ('WHY DO NPCS', 'STAND STILL', 'AT NIGHT?'))
for _s in [TX['dawn'], *TX['cov']]: font.check(_s)
WHT = (240, 236, 226); PALE = (226, 232, 255); RED = (255, 70, 60)
def hud(d, t):
    if night(t) < 0.5 and t < T_NIGHT[0] + 0.5: return
    s = dawn_left(t); txt = f"{TX['dawn']} 0:{s:02d}"
    d.rectangle([40, 40, 470, 150], fill=(10, 12, 28)); d.rectangle([40, 40, 470, 150], outline=(120, 130, 190), width=4)
    ctext(d, txt, 64, 9, PALE, o=5, x=66)
def meter(d, t):
    v = detect(t)
    if v <= 0.0: return
    x0, y0 = 640, 50; wb = 370; shake = int(6 * math.sin(t * 60)) if v > 0.9 else 0
    d.rectangle([x0 - 8 + shake, y0 - 8, x0 + wb + 8 + shake, y0 + 92], fill=(10, 12, 28)); d.rectangle([x0 - 8 + shake, y0 - 8, x0 + wb + 8 + shake, y0 + 92], outline=(150, 150, 170), width=4)
    cx, cy = x0 + 46 + shake, y0 + 42                                                             # the eye icon
    d.ellipse([cx - 34, cy - 20, cx + 34, cy + 20], fill=(236, 230, 200)); d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=(30, 30, 40))
    bx0 = x0 + 100 + shake; d.rectangle([bx0, y0 + 24, x0 + wb - 6 + shake, y0 + 60], fill=(40, 40, 52))
    col = mixc((240, 220, 120), RED, seg01(v, 0.5, 0.95)); d.rectangle([bx0, y0 + 24, bx0 + int((x0 + wb - 6 - x0 - 100) * v), y0 + 60], fill=col)
def cover(d, t):
    if not (0 <= t < T0['01'] + 0.3): return
    lines = TX['cov']; scs = [9, 10, 11]; y = 300
    w = max(tw(s, sc) for s, sc in zip(lines, scs)); yy = y
    for i, (s, sc) in enumerate(zip(lines, scs)):
        if i == len(lines) - 1: d.rectangle([540 - w / 2 - 30, yy - 18, 540 + w / 2 + 30, yy + 7 * sc + 18], fill=(70, 18, 30))
        ctext(d, s, yy, sc, (255, 222, 120) if i == len(lines) - 1 else WHT, o=6); yy += 7 * sc + 34
def gaze_aim(t):
    sc = scene(t)
    if sc == 'reveal': return V((lerp(-2.0, 1.5, 0.5 + 0.5 * math.sin(t * 1.3)), 0.0, 6.0))
    if sc == 'cat':
        if t < T_SNAP: return V((lerp(1.5, -1.5, seg01(t, S_CAT, T_SNAP)), 0.0, 3.0))
        return V((lerp(-2.6, 2.4, seg01(T_SNAP, *T_CAT)), 0.0, 3.2)) + (V((0.6, 0, 26.0)) - V((lerp(-2.6, 2.4, seg01(T_SNAP, *T_CAT)), 0.0, 3.2))) * sm(seg01(t, T_SNAP + 0.1, T_YANK + 0.3)) * 0.3
    if sc == 'hero': kx, _, kz, _ = knight_pos(t); return V((kx, 0.0, kz + 0.1))
    if sc == 'hat': return V(lerp3((-0.5, 0.0, 1.0), (B_POS[0], 0.0, B_POS[1]), sm(seg01(t, T_THROW - 0.1, T_THROW + 0.35))))
    return None
def cone(arr, t, vi, R, ws_):
    """the Watcher's gaze: a soft pale beam from its eyes + a bright spot on the ground where it lands"""
    if ws_ is None or ws_[4] < 0.3 or night(t) < 0.5: return arr
    aim = gaze_aim(t)
    if aim is None: return arr
    sc = scene(t); a0 = CUTS[[n for n, _ in CUTS].index(sc)][1]; fade = sm(seg01(t, a0, a0 + 0.3)) * ws_[4]
    arr = pool(arr, R, vi, aim, 1.0, (210, 226, 190), 0.55 * fade, 16)                     # the spot: always, even when the head is off-screen
    head = V(ws_[1]); a = _proj(R, vi, head + V((0, 0.08, 0.2)))
    side = nz(np.cross(aim - head, V((0, 1.0, 0)))); rad = 1.0
    b = _proj(R, vi, aim + side * rad); c = _proj(R, vi, aim - side * rad)
    if a is None or b is None or c is None: return arr
    ov = Image.new('L', (W * S, H * S), 0); dd = ImageDraw.Draw(ov)
    dd.polygon([(a[0], a[1]), (b[0], b[1]), (c[0], c[1])], fill=int(55 * fade))
    m = np.asarray(ov.filter(ImageFilter.GaussianBlur(10))).astype(np.float32)[..., None] / 255.0
    return arr * (1 - m * 0.4) + np.array([232, 240, 214], np.float32) * m
from PIL import ImageFilter
GMASK = None
def ground_mask(vi, zb):
    """1 where the rendered pixel is the ground plane (y = 0) itself, 0 where something stands in front of it (people, walls)"""
    cx, cy, cz, ca, sa, cp, sp, fpx = vi
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32) + 0.5
    X = (xx - W / 2) / fpx; Y = (H / 2 - yy) / fpx; Z2 = np.ones_like(X)
    py = cp * Y + sp * Z2; Zc = -sp * Y + cp * Z2
    with np.errstate(divide='ignore', invalid='ignore'):
        sg = np.where(py < -1e-4, -cy / py, np.inf)                       # depth (Z2) of the ground hit along this pixel
        dep = np.where(zb > 0, 1.0 / np.maximum(zb, 1e-9), np.inf)
    m = (np.isfinite(sg) & (dep > sg * 0.93)).astype(np.float32)
    return np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize((W * S, H * S), Image.BILINEAR)).astype(np.float32) / 255.0
def _proj(R, vi, p):
    q = R.project(tuple(p), vi); return None if q is None else (q[0] * S, q[1] * S, q[2])
def glow(arr, R, vi, p, rad_m, col, k):
    """additive soft glow around a 3D point (radius in metres -> pixels by depth)"""
    q = _proj(R, vi, p)
    if q is None: return arr
    r = max(6.0, rad_m * vi[7] * S / max(0.2, q[2])); x0, x1 = int(max(0, q[0] - r)), int(min(W * S, q[0] + r)); y0, y1 = int(max(0, q[1] - r)), int(min(H * S, q[1] + r))
    if x1 <= x0 or y1 <= y0: return arr
    yy, xx = np.mgrid[y0:y1, x0:x1]; d = np.sqrt((xx - q[0]) ** 2 + (yy - q[1]) ** 2) / r
    m = np.clip(1 - d, 0, 1) ** 2.2 * k; arr[y0:y1, x0:x1] += m[..., None] * np.array(col, np.float32)
    return arr
def pool(arr, R, vi, c, rad, col, k, blur=18):
    """a soft pool of light on the ground (ellipse projected, blurred, added)"""
    pts = [_proj(R, vi, V(c) + V((rad * math.cos(a), 0.0, rad * math.sin(a)))) for a in np.linspace(0, 2 * PI, 20)[:-1]]
    if any(p_ is None for p_ in pts): return arr
    ov = Image.new('L', (W * S, H * S), 0); ImageDraw.Draw(ov).polygon([(p_[0], p_[1]) for p_ in pts], fill=255)
    m = np.asarray(ov.filter(ImageFilter.GaussianBlur(blur))).astype(np.float32) / 255.0 * k
    if GMASK is not None: m = m * GMASK
    return arr + m[..., None] * np.array(col, np.float32)
def lights2d(arr, t, vi, R, KP, ws_):
    nt = night(t)
    if nt < 0.2: return arr
    for k_, (c, n, i) in enumerate(WIN):                                                      # lit windows: glow + a pool on the street
        off_t = T_OPEN + 0.25 + 0.22 * (k_ % 7)
        if (t < off_t) or (t >= T_NIGHT[0] + 0.6):
            arr = glow(arr, R, vi, V(c) + V(n) * 0.05, 0.9, (255, 170, 80), 0.55 * nt)
            arr = pool(arr, R, vi, V((c[0] + n[0] * 1.1, 0.0, c[2])), 0.9, (255, 160, 70), 0.22 * nt, 14)
    if KP.get('_flame') is not None and (t < S_HAT + 2.0 or t >= S_LOOP):                     # the torch
        f = V(KP['_flame']); fl = 1.0 + 0.12 * math.sin(t * 23)
        arr = glow(arr, R, vi, f, 0.55 * fl, (255, 150, 60), 0.85 * nt)
        arr = pool(arr, R, vi, V((f[0], 0.0, f[2])), 1.5 * fl, (255, 140, 60), 0.2 * nt, 22)
    if ws_ is not None and ws_[4] > 0.05:                                                     # the lantern eyes
        Rh = ws_[5]
        for sd in (1, -1): arr = glow(arr, R, vi, V(ws_[1]) + Rh @ V((sd * 0.11, 0.1, 0.24)), 0.16, (255, 236, 170), 0.75 * ws_[4])
    return arr
COL = {'N': (242, 238, 226), 'K': (150, 200, 255), 'M': (255, 190, 200), 'B': (255, 214, 140)}
def _sub_scr():
    if not TRL: return SCR
    import importlib.util as _iu
    sp_ = _iu.spec_from_file_location('nf_tts', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'tts', 'nf.py'))
    m_ = _iu.module_from_spec(sp_); sp_.loader.exec_module(m_); TRS = m_.TR_SUB
    out = dict(SCR); sent = {}
    for k, v in SCR['sent'].items():
        if len(v) == len(TRS[k]): sent[k] = [[a, b, tx] for (a, b, _), tx in zip(v, TRS[k])]
        else: sent[k] = [[v[0][0], v[-1][1], ' '.join(TRS[k])]]
    out['sent'] = sent
    return out
SUBS = look.Subtitles(_sub_scr(), [x for x in LINES if x[0] != '00'], W, H, S, COL, title_key='none', n=17,
                      hil=({'KIPIRDAYANI', 'ATEŞ', 'DOĞAR.'} if TRL else {'MOVES.', 'FIRE', 'RESPAWNS.', 'HIDING.'}))
from nightkit import cta
CTA = cta.Achievement(t0=T0['08'] - 0.1, lang=SUB_LANG, dur=F(1.5), y=300)
def frame_final(t):
    if t >= DUR: t = t - DUR
    img, vi, R, (KP, MP, ws_), zb = frame_low(t); arr = post.upscale(img, S)
    global GMASK; GMASK = ground_mask(vi, zb)
    arr = cone(arr, t, vi, R, ws_); arr = lights2d(arr, t, vi, R, KP, ws_)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    hud(d, t); meter(d, t); cover(d, t)
    arr = np.asarray(im).astype(np.float32)
    if T_GRAB[0] + 0.5 <= t < T_GRAB[1] + 0.5:                                                    # fog swirl where Bram was taken
        u = seg01(t, T_GRAB[0] + 0.5, T_GRAB[1] + 0.5); arr = arr * (1 - 0.25 * math.sin(PI * u)) + np.array([180, 186, 200], np.float32) * 0.25 * math.sin(PI * u)
    if T_RESPAWN <= t < T_RESPAWN + 0.5:                                                         # respawn sparkle flash
        arr = arr + (255 - arr) * 0.35 * (1 - seg01(t, T_RESPAWN, T_RESPAWN + 0.5))
    arr = SUBS.apply(arr, t); arr = CTA.apply(arr, t)
    return arr

TEST = os.environ.get('TEST')
if TEST and __name__ == '__main__':
    if TEST == 'seq': ts = sorted(set([round(a + (b - a) * f, 2) for i, (n_, a) in enumerate(CUTS) for b in [CUTS[i + 1][1] if i + 1 < len(CUTS) else DUR] for f in (0.1, 0.5, 0.9)]))
    else: ts = [float(x) for x in TEST.split(',')]
    tw_ = int(os.environ.get('TW', '200')); th = tw_ * 16 // 9
    ims = [Image.fromarray(np.clip(frame_final(x), 0, 255).astype(np.uint8)) for x in ts]
    if os.environ.get('SZ') == 'full':
        for x, im in zip(ts, ims): im.save(f'test_nf_{x:.2f}.png')
    ims = [im.resize((tw_, th), Image.LANCZOS) for im in ims]
    per = int(os.environ.get('PER', '10')); rows = (len(ims) + per - 1) // per; shp = Image.new('RGB', (min(per, len(ims)) * (tw_ + 2), rows * (th + 18)), (30, 30, 30))
    dd = ImageDraw.Draw(shp)
    for i, (im, x) in enumerate(zip(ims, ts)): shp.paste(im, ((i % per) * (tw_ + 2), (i // per) * (th + 18))); dd.text(((i % per) * (tw_ + 2) + 4, (i // per) * (th + 18) + th + 3), f'{x:.2f} {x / 1.2:.1f}f {scene(x)}', fill=(255, 255, 0))
    shp.save(os.environ.get('TEST_OUT', 'test_nf.png')); print('test written', DUR, round(DUR / 1.2, 2), SEQS); sys.exit()

QA = dict(fps=FPS, dur=DUR, W=W, frame=lambda t: Image.fromarray(np.clip(frame_final(t), 0, 255).astype(np.uint8)).resize((W, H), Image.BOX), chars={},
          geom=lambda t, name, st, V_: [], camera=lambda t: cam_shot(t)[0], min_cam_dist=0.3, camera_ok=lambda p: True, allow_jump=[], weapon_events=[],
          scenes=[dict(id=nm, t0=a, t1=(CUTS[i + 1][1] if i + 1 < len(CUTS) else DUR), action=nm) for i, (nm, a) in enumerate(CUTS)],
          texts=lambda: [('hud', s, 10) for s in TX['cov']])

# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as _sf
    s = Sound(DUR, loop=False, seed=71); sr = s.sr; n = s.n; t = s.t
    BED = np.zeros(n); FX = np.zeros(n); MUS = np.zeros(n)
    def put(buf, x, t0, v=1.0):
        i = int(round(t0 * sr))
        if i >= n or i + len(x) <= 0: return
        if i < 0: x = x[-i:]; i = 0
        j = min(n, i + len(x)); buf[i:j] += (x * v)[:j - i]
    def tone(t0, m, d, v, dec=3.0, att=0.005, glide=0.0, buf=None, harm=(1.0,)):
        f = 440 * 2 ** ((m - 69) / 12); tt = s.T(d); fr_ = f * (1 + glide * tt / d); ph = np.cumsum(fr_) / sr
        x = sum(a * np.sin(2 * np.pi * ph * (k + 1)) for k, a in enumerate(harm)); put(FX if buf is None else buf, x * np.minimum(1, tt / att) * np.exp(-tt * dec), t0, v)
    def nb(t0, d, lo, hi, v, seed, shape=2, buf=None): put(FX if buf is None else buf, s.filt_short(s.noise(d, seed), lo=lo, hi=hi) * np.sin(np.pi * s.T(d) / d) ** shape, t0, v)
    def thud(t0, f=60, v=0.1, d=0.3, buf=None): tt = s.T(d); put(FX if buf is None else buf, np.sin(2 * np.pi * f * tt * (1 - 0.3 * tt / d)) * np.exp(-tt * 9), t0, v)
    def mask(a, b, r=0.15): return np.clip(np.minimum((t - a) / r, (b - t) / r), 0, 1)
    nightv = np.array([night(x) for x in t[::480]]); nightv = np.interp(t, t[::480], nightv)
    # bed: night wind + crickets (they STOP when the eyes open; back in the loop night), dawn birds
    BED += s.filt(s.rng.normal(0, 1, n), lo=80, hi=600) * 0.03 * nightv * (0.75 + 0.25 * np.sin(2 * np.pi * 0.23 * t))
    MUS += (np.sin(2 * np.pi * 49 * t) + 0.6 * np.sin(2 * np.pi * 73.5 * t) + 0.25 * np.sin(2 * np.pi * 98 * t + 0.4 * np.sin(2 * np.pi * 0.3 * t))) * 0.011 * nightv
    for t0 in (1.4, S_LOOP + 1.2):
        if t0 < DUR: tone(t0, 67, 0.35, 0.015, dec=4, buf=BED); tone(t0 + 0.45, 64, 0.5, 0.013, dec=3, buf=BED)
    tone(T_EYE_MOVE, 50, 0.5, 0.012, dec=3, glide=0.08, harm=(1.0, 0.5, 0.3)); nb(T_EYE_MOVE, 0.5, 200, 1200, 0.01, 7, 1)
    cr = (np.sin(2 * np.pi * 4200 * t) * (np.sin(2 * np.pi * 28 * t) > 0.6) * (np.sin(2 * np.pi * 0.7 * t) > -0.2)).astype(float) * 0.004
    crick = np.where((t < T_OPEN) | (t > T_NIGHT[0] + 0.5), 1.0, 0.0) * nightv; BED += cr * crick
    x = T_SUN[0] + 0.3; k = 0
    while x < T_NIGHT[0]:
        m0 = 86 + 6 * hsh(k, 3); tone(x, m0, 0.09, 0.008, dec=18, glide=0.25, buf=BED); tone(x + 0.11, m0 + 3, 0.07, 0.006, dec=20, glide=-0.2, buf=BED); x += 0.45 + 0.5 * hsh(k, 4); k += 1
    # torch crackle (soft, a few pops), louder in the flame close-up
    BED += s.filt(s.rng.normal(0, 1, n), lo=200, hi=1500) * 0.006 * nightv * (1 + 2.5 * mask(S_FLAME, S_HAT, 0.1))
    for i in range(int(DUR * 4)):
        t0 = hsh(i, 81) * DUR
        if night(t0) > 0.5: nb(t0, 0.012, 1500, 6000, 0.01 * (3.0 if S_FLAME <= t0 < S_HAT else 1.0), 900 + i, 1)
    # footsteps of the walking knight
    for x_ in np.arange(0.0, DUR, 1 / 1.8):
        v = knight_pos(x_)[3]
        if v > 0.3: thud(x_, 120, 0.035, 0.12); nb(x_, 0.05, 1200, 5000, 0.012, int(x_ * 99), 1); tone(x_ + 0.01, 99, 0.05, 0.004, dec=40)
    # THOOM footsteps of the Watcher: sub + rumble + window rattle
    for th in THOOMS + [S_HERO + 0.4, S_HERO + 1.5, T_SHADOW - 0.2]:
        thud(th, 34, 0.32, 1.2); nb(th, 0.9, 40, 300, 0.06, int(th * 77), 1); nb(th + 0.05, 0.5, 2000, 6000, 0.012, int(th * 55), 1)
    for k_ in range(9): tone(T_OPEN + 0.25 + 0.22 * k_, 100, 0.03, 0.01, dec=60)                    # windows click off
    # the drone: rises with the meter; the eyes open = a low choir swell
    dv = np.interp(t, t[::480], np.array([detect(x) for x in t[::480]]))
    tt = t; MUS += (np.sin(2 * np.pi * 55 * tt) + 0.5 * np.sin(2 * np.pi * 82.5 * tt) + 0.3 * np.sin(2 * np.pi * (110 + 30 * dv) * tt)) * (0.012 + 0.03 * dv) * mask(T_OPEN, S_DAWN, 0.4)
    nb(T_OPEN, 1.6, 200, 900, 0.03, 31, 2, buf=MUS)
    # the cone shimmer while it sweeps; the cat: patter, cut-off meow, bell rolling back
    for a_, b_ in ((S_REVEAL + 0.6, S_REVEAL + 2.0), (S_CAT, T_YANK), (S_HERO, S_TURN), (T_THROW, T_GRAB[1])):
        tt2 = s.T(b_ - a_); put(FX, np.sin(2 * np.pi * (1800 + 300 * np.sin(2 * np.pi * 3 * tt2)) * tt2) * 0.003 * np.sin(np.pi * tt2 / tt2[-1]), a_)
    for x_ in np.arange(T_CAT[0], T_SNAP, 0.09): thud(x_, 300, 0.008, 0.05)
    tone(T_SNAP, 76, 0.22, 0.03, dec=3, glide=0.4, harm=(1.0, 0.5, 0.3)); nb(T_SNAP + 0.18, 0.15, 300, 3000, 0.05, 41, 1)
    for k_ in range(4): tone(T_YANK + 0.3 + 0.18 * k_, 98, 0.12, 0.012 * (1 - k_ / 4), dec=12)
    # heartbeat through the wordless beat + the flame; silence before the throw
    hb = S_TURN + 0.2; k_ = 0
    while hb < T_THROW - 0.15:
        thud(hb, 52, 0.12, 0.25); thud(hb + 0.18, 48, 0.08, 0.2); hb += max(0.5, 0.85 - 0.06 * k_); k_ += 1
    # the throw: slow whoosh, the grab: fog roar + swirl, the hat lands in the puddle (splash)
    nb(T_THROW, 1.1, 300, 2500, 0.04, 51, 1); nb(T_GRAB[0], 0.9, 60, 800, 0.1, 52, 1); thud(T_GRAB[0] + 0.5, 40, 0.2, 0.8)
    nb(T_LANDHAT, 0.25, 800, 5000, 0.04, 53, 0.5)
    # dawn: a bright music-box sting + bell; respawn sparkle; the loop: a reverse whoosh back to night
    for k_, m in enumerate((72, 76, 79, 84, 88)): tone(T_SUN[0] + 0.1 * k_, m, 0.9, 0.02, dec=2.5, harm=(1.0, 0.0, 0.3), buf=MUS)
    tone(T_SUN[0] + 0.6, 60, 2.5, 0.03, dec=1.2, harm=(1.0, 0.6, 0.4, 0.3))
    for k_ in range(8): tone(T_RESPAWN + 0.04 * k_, 96 + (k_ % 4) * 2, 0.15, 0.01, dec=14)
    tt3 = s.T(1.0); put(FX, s.filt_short(s.noise(1.0, 61), lo=300, hi=4000) * (tt3 / 1.0) ** 2, T_NIGHT[0] - 0.1, 0.05)
    if CTA.on: put(FX, cta.chime(sr), CTA.t0, 1.0)
    # voice
    NB = np.zeros(n); wins = []
    for k_, t0 in LINES:
        f_ = os.path.join(TTS_DIR, 'nf', f'{k_}.wav')
        if not os.path.exists(f_): continue
        a, ar = _sf.read(f_); a = a if a.ndim == 1 else a.mean(1)
        a = np.interp(np.arange(int(len(a) * sr / ar)) / sr, np.arange(len(a)) / ar, a); act = np.abs(a) > 0.02 * np.abs(a).max()
        g_ = 0.75 if k_ == '03' else 1.0
        a = a * (0.12 * g_ / np.sqrt((a[act] ** 2).mean())); put(NB, a, t0); wins.append((t0, t0 + len(a) / sr))
    gd = duck_envelope(n, sr, wins, -8.0, 0.05, 0.25) if wins else np.ones(n)
    bed = BED * gd + MUS * (0.55 + 0.45 * gd); fx = FX * (0.65 + 0.35 * gd)
    L = bed + fx; R_ = np.roll(bed, 700) + np.roll(fx, 200)
    pk = max(np.abs(L).max(), np.abs(R_).max()); gv = (pk * 1.6 / np.abs(NB).max()) if np.abs(NB).max() > 0 else 0.0
    s.L = L + NB * gv; s.R = R_ + NB * gv; s.reverb(0.22, length=2.2, decay=3.0)
    fi = np.clip(t / 0.008, 0, 1); s.L = s.L * fi; s.R = s.R * fi
    return s.save(path, peak=0.9)
if __name__ == '__main__' and os.environ.get('PART') == 'audio':
    print(build_audio(os.path.join(OUT, os.environ.get('AUDIO_NAME', 'night_freeze.wav')))); sys.exit()
if __name__ == '__main__' and os.environ.get('PART'):
    a, b = map(int, os.environ['PART'].split(':'))
    import subprocess
    p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W * S}x{H * S}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', os.path.join(OUT, f"{os.environ.get('PART_PREFIX', 'nf')}_{a:05d}.mp4")], stdin=subprocess.PIPE)
    vhs = post.VHS(W * S, H * S, S, grade='none', chroma=0, scan_dark=1.0, vignette=0.5, grain=1.4, band_period=1e9)
    for f in range(a, min(b, N)): p.stdin.write(vhs(frame_final(f / FPS), f, f / FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done', a, b); sys.exit()
