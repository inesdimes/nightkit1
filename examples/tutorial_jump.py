"""WHY DO TUTORIALS MAKE YOU JUMP? (Insert Disc 2, 27 Nov 2026) ~28 s final (x1.2 after), nightkit HD, 9:16.
Story: Enes's GPT brief (27 Nov). Rule: the tutorial gate opens when SOMEONE on the course leaves the ground; the counter does not
check who. The knight smashes three hurdles (counter stays 0/1), the instructor steps in to demonstrate, the knight shoulder-charges
him over the last hurdle -> JUMPS 1/1, the gate opens, the instructor lands on course 2 -> DOUBLE JUMP -> the knight lowers his
shoulder again -> loop to frame 0.
Claude additions: the spoken title as line 00; PRESS X TO JUMP prompts the knight ignores; TUTORIAL 1-1 HUD; the game jump sound on the
launch; course 2 = the same layout seen again (the last shot ends exactly on frame 0).
Voices: Enes's cloned voice, tools/tts/tj.py (TR: his own takes).
Reuses: dragon_taxes KNIGHT + helmet (never_attack plate pieces). New: instructor, JUMP sign, hurdles that break, training yard, gates, counter.
Render in sequences:  python tools/render_seq.py examples/tutorial_jump.py --prefix tj --seqs s1,s2,s3,s4,s5 / --master <out>
Stills: TEST=seq python examples/tutorial_jump.py -> test_tj.png  (TEST=1.0,2.0 for build seconds)"""
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
def grip_pt(P, key, off=0.075, lift=0.03): return P['_' + key + 'wrist'] + P['_' + key + 'dir'] * off + P['_' + key + 'palm'] * lift
def F(x): return round(x * 1.2, 4)
SUB_LANG = os.environ.get('SUB_LANG', 'en'); TRL = SUB_LANG == 'tr'

# ======================= cast =======================
def knight(P):
    """the series knight (dragon_taxes spec + helmet, plate pieces as in never_attack)"""
    Q = hd.human(dtx.KNIGHT, P); RW = P['_RW']; ch = P['_chest']; st = (178, 186, 200); dk = (128, 136, 152)
    for sd in (1, -1):
        c = ch + RW @ V((sd * 0.19, 0.075, -0.01))
        Q += hd.ellip(c, RW @ hd.Rz(-sd * 0.35), (0.1, 0.07, 0.1), 10, 5, st, v1=PI * 0.6, colfn=lambda i, j, cl: dk if i == 2 else st)
        kn = P['_' + ('r' if sd > 0 else 'l') + 'knee']; Q += hd.ellip(kn, RW, (0.06, 0.06, 0.065), 8, 4, st)
    Q += hd.ellip(ch + RW @ V((0, -0.02, 0.035)), RW, (0.17, 0.17, 0.1), 12, 6, st, keep=lambda c: c[2] > 0.0, colfn=lambda i, j, cl: dk if (j % 6 == 0) else st)
    Q += dtx.knight_helmet(P)
    return Q
INSTR = hd.spec(h=1.72, build=0.86, skin=(226, 182, 146), hair=(84, 58, 40), hair_style='short', eye=(70, 90, 60), brow=(46, 32, 24),
                tunic=(236, 194, 44), tunic2=(206, 162, 32), skirt=0.32, pants=(54, 62, 92), boots=(44, 36, 30), belt=(40, 40, 52),
                buckle=(226, 226, 232), gloves=(246, 246, 240), collar=(250, 248, 238))
BROW = (40, 28, 20)
def instructor(P):
    """thin tutorial instructor: yellow jacket, white collar + gloves, navy trousers, BUSHY brows (extra blocks over the hd brows)"""
    Q = hd.human(INSTR, P); hc = P['_head']; RH = P['_RH']; k = INSTR['h'] / 1.78; rz = 0.103 * k
    b = P.get('brow', 0.0); up = P.get('brow_up', 0.0)
    for sd in (1, -1):
        c = hc + RH @ V((sd * 0.035 * k, (0.045 + 0.016 * up) * k, rz * 0.9))
        Q += hd.bx(c, RH @ hd.Rz(sd * (0.32 * b - 0.18 * up)), (0.024 * k, 0.0085 * k, 0.008), BROW)
    return [q for q in Q if q]

# ======================= props =======================
SIGN_B = (34, 82, 196); SIGN_W = (246, 246, 240)
def glyph_quads(s, c, u, v, n, px, col, emit=True, lift=0.004):
    """pixel-font text as 3D quads: centred at c, u = right, v = up, n = out of the surface; px = metres per font pixel"""
    font.check(s); Q = []; w = font.width(s); c = V(c, float) + V(n, float) * lift; u = V(u, float); v = V(v, float)
    for kk, ch in enumerate(s.upper()):
        for j, row in enumerate(font.FONT[ch]):
            for i, bit in enumerate(row):
                if bit != '1': continue
                x0 = (kk * 6 + i - w / 2) * px; y0 = (3.5 - j) * px
                q = hd.face([c + u * x0 + v * y0, c + u * (x0 + px) + v * y0, c + u * (x0 + px) + v * (y0 - px), c + u * x0 + v * (y0 - px)], col, emit=emit)
                if q is not None:
                    if float(q['n'] @ V(n, float)) < 0: q = hd.face([c + u * x0 + v * y0, c + u * x0 + v * (y0 - px), c + u * (x0 + px) + v * (y0 - px), c + u * (x0 + px) + v * y0], col, emit=emit)
                    Q.append(q)
    return Q
def panel(c, u, v, n, w, h, col, emit=False):
    c = V(c, float); u = V(u, float); v = V(v, float); n = V(n, float)
    q = hd.face([c - u * w - v * h, c + u * w - v * h, c + u * w + v * h, c - u * w + v * h], col, emit=emit)
    if q is not None and float(q['n'] @ n) < 0: q = hd.face([c - u * w - v * h, c - u * w + v * h, c + u * w + v * h, c + u * w - v * h], col, emit=emit)
    return [q] if q else []
def jump_sign(P):
    """the JUMP road sign: pole in the left hand, a blue board with white JUMP on top; P['_pole'] = pole direction (world),
    P['_board'] = the direction the board faces (world)"""
    g = grip_pt(P, 'l', 0.06, 0.0); d = nz(P.get('_pole', (0, 1.0, 0))); fn = V(P.get('_board', (0, 0, 1.0)), float)
    fn = nz(fn - d * float(fn @ d)); u = nz(np.cross(fn, d))
    Q = hd.limb(tuple(g - d * 0.3), tuple(g + d * 0.82), 0.016, 0.016, (150, 150, 158), n=6, m=1)
    bc = g + d * 1.0
    Q += hd.bx(tuple(bc), np.column_stack([u, d, fn]), (0.37, 0.19, 0.012), (220, 220, 226))
    Q += panel(bc + fn * 0.0135, u, d, fn, 0.35, 0.17, SIGN_B, emit=True)
    Q += panel(bc + fn * 0.0145, u, d, fn, 0.33, 0.15, SIGN_W, emit=True) + panel(bc + fn * 0.0155, u, d, fn, 0.315, 0.135, SIGN_B, emit=True)
    Q += glyph_quads('JUMP', bc + fn * 0.016, u, d, fn, 0.024, SIGN_W)
    Q += panel(bc - fn * 0.0135, u, d, -fn, 0.36, 0.18, (170, 170, 178))
    P['_signc'] = bc
    return [q for q in Q if q]

# ======================= hurdles =======================
WOOD = (176, 128, 78); WOOD_D = (138, 98, 58); GREEN = (70, 150, 70); RED = (200, 52, 46); WHITE_P = (236, 230, 216)
HALF = 0.7                                     # half width of a hurdle (posts at +-HALF): the instructor runs outside at x = -1.2
def plank_col(kind, j):
    if kind == 'green': return GREEN if j % 2 == 0 else hd.shade(GREEN, 0.85)
    if kind == 'final': return RED if j % 2 == 0 else WHITE_P
    return WOOD if j % 2 == 0 else WOOD_D
HURDLE_KIND = {1: ('wood', 0.95, 2), 2: ('wood', 1.3, 3), 3: ('green', 1.6, 4), 4: ('final', 1.05, 3)}
def plank_heights(i):
    _, h, n = HURDLE_KIND[i]; return [h * (j + 1) / n - 0.06 for j in range(n)]
def pieces(i, z, t_hit, vk=2.8):
    """the planks of hurdle i break into two halves each; every half flies on a fixed ballistic path, lands and lies still"""
    out = []
    for j, y in enumerate(plank_heights(i)):
        for sd in (1, -1):
            s = j * 2 + (0 if sd > 0 else 1) + i * 13
            vx = sd * (1.4 + 1.6 * hsh(s, 1)); vy = 1.6 + 2.2 * hsh(s, 2) + 0.4 * j; vz = vk * (0.5 + 0.4 * hsh(s, 3))
            if i == 3 and j == len(plank_heights(i)) - 1 and sd < 0: vx, vy, vz = -3.6, 3.4, 1.0          # the green plank spins out of frame
            spin = (2 * hsh(s, 4) - 1) * 9.0
            p0 = V((sd * HALF * 0.5, y, z), float); g = 9.8
            tl = (vy + math.sqrt(vy * vy + 2 * g * (y - 0.04))) / g
            out.append(dict(p0=p0, v=V((vx, vy, vz)), spin=spin, tl=tl, j=j, sd=sd, t0=t_hit, kind=HURDLE_KIND[i][0]))
    return out
def hurdle_faces(i, z, t, t_hit):
    kind, h, n = HURDLE_KIND[i]; Q = []
    for sd in (1, -1): Q += hd.bx((sd * HALF, h / 2 + 0.04, z), np.eye(3), (0.045, h / 2 + 0.04, 0.045), WOOD_D)
    for sd in (1, -1): Q += hd.bx((sd * HALF, 0.03, z), np.eye(3), (0.09, 0.03, 0.22), WOOD_D)
    if t_hit is None or t < t_hit:
        for j, y in enumerate(plank_heights(i)):
            Q += hd.bx((0, y, z), np.eye(3), (HALF, 0.06, 0.028), plank_col(kind, j))
            if kind == 'final':
                for x in (-0.55, -0.15, 0.25, 0.62): Q += hd.bx((x, y, z - 0.03), np.eye(3), (0.09, 0.061, 0.002), WHITE_P if j % 2 == 0 else RED)
        return [q for q in Q if q]
    for pc in pieces(i, z, t_hit):
        dt = min(t - t_hit, pc['tl']); p = pc['p0'] + pc['v'] * dt + V((0, -4.9 * dt * dt, 0))
        p[1] = max(0.04, p[1]); a = pc['spin'] * dt
        R = hd.Ry(0.6 * a) @ hd.Rz(a) if t - t_hit < pc['tl'] else hd.Ry(0.6 * pc['spin'] * pc['tl'])
        Q += hd.bx(tuple(p), R, (HALF * 0.48, 0.06, 0.028), plank_col(pc['kind'], pc['j']))
    for m in range(10):                                                              # splinters for the first 0.6 s
        dt = t - t_hit
        if dt > 0.6: break
        s = i * 31 + m; d = V((2 * hsh(s, 1) - 1, 0.6 + hsh(s, 2), 0.3 + hsh(s, 3))); p = V((0.0, 0.6, z)) + d * 3.0 * dt + V((0, -4.9 * dt * dt, 0))
        Q += hd.bx(tuple(p), hd.Rz(hsh(s, 4) * 6 + dt * 20), (0.05, 0.012, 0.012), WOOD)
    return [q for q in Q if q]

# =====================================================================================================================
#                                                      TIMELINE
# =====================================================================================================================
from nightkit.audio import Sound, duck_envelope
OUT = 'out'; os.makedirs(OUT, exist_ok=True)
TTS_DIR = os.environ.get('TTS_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tts'))
SCR = json.load(open(os.path.join(TTS_DIR, 'tj', 'script.json'), encoding='utf-8'))
KEYS = ['%02d' % i for i in range(0, 10)]
VK = 2.8                                             # the knight's running speed (m/s)
Z_H1 = 2.75                                          # hurdle 1 (frame 0: the knight is at z = 0, running at it)
T_H1 = (Z_H1 - 0.32) / VK
T0 = {}
def tend(k): return T0[k] + SCR['dur'][k]
def ws(k, i): s_ = SCR['sent'][k]; return T0[k] + s_[min(i, len(s_) - 1)][0]
def we(k, i): s_ = SCR['sent'][k]; return T0[k] + s_[min(i, len(s_) - 1)][1]
T0['00'] = 0.1
T0['01'] = tend('00') + 0.2
T0['02'] = tend('01') + 0.3
T0['03'] = tend('02') + 0.3
T_FAKE = tend('03') + 0.05                           # he looks up at hurdle 2, straightens as if to jump ...
T_H2 = T_FAKE + 0.65                                 # ... then shoulders through it
T_H3 = T_H2 + 1.1
T0['04'] = T_H3 + 0.3
T0['05'] = tend('04') + 0.35
T0['06'] = tend('05') + 0.3
T_HIT = tend('06') + 0.2                             # the shoulder hits the instructor
T_FLY = 1.85                                          # the wordless beat (flight) in build seconds
T_ONE = T_HIT + 0.55                                 # JUMPS 1/1 (over the last hurdle)
T_GATE = (T_ONE + 0.02, T_ONE + 0.22)
T_LAND = T_HIT + T_FLY
T_H4 = T_LAND + 0.55                                 # the knight smashes the last hurdle too (seen through the gate)
T0['07'] = T_LAND + 0.45
T_C2 = tend('07') + 0.45                             # cut: course 2
T0['08'] = T_C2 + 0.35
T_DJ = we('08', 0) - 0.55                            # DOUBLE JUMP pops above his head on "two jumps"
T_LOOP = tend('08') + 0.25
T0['09'] = T_LOOP + 0.2
DUR = round(tend('09') + 0.4, 3); N = int(round(DUR * FPS))
LINES = [(k, T0[k]) for k in KEYS]
def fr(x): return int(round(x * FPS))
CUTS = [('open', 0.0), ('side', T_H1 + 0.55), ('low', T0['03'] - 0.15), ('h3', T_H2 + 0.55), ('stop', T0['05'] - 0.2),
        ('charge', T0['06'] - 0.1), ('flight', T_HIT + 0.12), ('gate', T_LAND - 0.1), ('c2', T_C2)]
SEQS = [('s1', 0, fr(T0['03'] - 0.15)), ('s2', fr(T0['03'] - 0.15), fr(T0['05'] - 0.2)), ('s3', fr(T0['05'] - 0.2), fr(T_HIT + 0.12)),
        ('s4', fr(T_HIT + 0.12), fr(T_C2)), ('s5', fr(T_C2), N)]
def scene(t):
    nm = CUTS[0][0]
    for n_, a in CUTS:
        if t >= a: nm = n_
    return nm
def course(t): return 2 if t >= T_C2 else 1
def talking(t, key):
    if key not in T0: return 0.0
    for a, b, _ in SCR['sent'][key]:
        if T0[key] + a <= t < T0[key] + b: return 0.5 + 0.5 * math.sin((t - T0[key]) * 17.0)
    return 0.0

# ----------------------- the knight's run (course 1), integrated once -----------------------
_DT = 0.005
def _vk(t):
    v = VK * (1 - 0.55 * win(t, T_FAKE - 0.1, T_H2 - 0.12, 0.18))            # the fake jump: he almost stops
    if t >= T_HIT: v = VK * max(0.0, 1 - (t - T_HIT) / 0.38) * 0.9                # boots slide on the stone
    return v
_TS = np.arange(0.0, T_HIT + 0.6, _DT); _ZS = np.concatenate([[0.0], np.cumsum([_vk(x) * _DT for x in _TS[:-1]])])
def zk1(t): return float(np.interp(t, _TS, _ZS))
Z_H2 = zk1(T_H2) + 0.32; Z_H3 = zk1(T_H3) + 0.32
Z_I = zk1(T_HIT) + 0.55                              # the instructor stands here, facing the knight
Z_H4 = Z_I + 0.55; GZ = Z_H4 + 3.4                   # the last hurdle, the exit gate
ZS = -7.6                                            # the entry gate (course 2 = this layout again, starting at the same gate)
Z_STOP = zk1(T_HIT + 0.6)
Z_LAND = GZ + 3.2; X_LAND = -0.9                     # he lands sitting, facing +z (course 1) = ZS + 3.2 on course 2
WALK_A = T_H4 + 0.35; Z_WALK_END = GZ - 0.35
# course 2: the knight walks in through the entry gate, then runs into frame 0 (u = t - DUR <= 0)
_U2 = T_C2 - DUR
def _z2(u, vw):
    if u >= -1.2: return VK * u
    if u >= -1.9: a = u + 1.2; return -1.2 * VK + a * VK + a * a * (VK - vw) / (2 * 0.7)          # ramp walk -> run
    return -1.2 * VK - 0.7 * (VK + vw) / 2 + (u + 1.9) * vw
_lo, _hi = 0.3, 3.0
for _ in range(40):
    _m = (_lo + _hi) / 2
    if _z2(_U2, _m) < ZS + 0.3: _hi = _m
    else: _lo = _m
VW2 = (_lo + _hi) / 2
def knight_z(t):
    if course(t) == 2: return _z2(t - DUR, VW2)
    if t < T_HIT + 0.6: return zk1(t)
    if t < T_H4 - 0.4: return Z_STOP
    if t < WALK_A: return Z_STOP + 0.45 * sm(seg01(t, T_H4 - 0.4, T_H4 + 0.05))
    return Z_STOP + 0.45 + (Z_WALK_END - Z_STOP - 0.45) * seg01(t, WALK_A, T_C2)
def knight_speed(t, h=0.02): return (knight_z(t + h) - knight_z(t - h)) / (2 * h)

# ----------------------- the instructor -----------------------
OFFK = [(-9.0, -2.0), (T_H1 + 0.3, -2.0), (T0['02'] - 0.2, 0.9), (T0['03'] + 0.4, 1.3), (T_FAKE, 1.0), (T_H2 + 0.2, 0.3),
        (T_H3 - 0.15, -1.3), (T0['04'] + 0.45, -1.4), (tend('04') - 0.3, -0.1), (T0['05'], -0.1)]
_OFF = look.Path([(a, b) for a, b in OFFK])
X_RUN = -1.05
T_STAND = (T_C2 + 0.15, T_C2 + 0.9)
T_JOG = T_LOOP + 0.05
def inst_pos(t):
    """(x, z, yaw, mode) mode: run / stand / fly / sit"""
    if course(t) == 1:
        if t < T0['05'] - 0.2: return X_RUN, knight_z(t) + float(_OFF(min(t, T0["05"]))), 0.0, 'run'
        if t < T_HIT: return 0.0, Z_I, PI, 'stand'
        if t < T_LAND: return 0.0, Z_I, PI, 'fly'
        return X_LAND, Z_LAND, 0.0, 'sit'
    z0 = ZS + 3.2
    if t < T_STAND[1]: return X_LAND, z0, 0.0, ('sit' if t < T_STAND[0] else 'rise')
    if t < T_JOG: return X_LAND, z0, 0.0, 'stand2'
    s = seg01(t, T_JOG, DUR); dT = DUR - T_JOG; p0, p1, v1 = z0, -2.0, VK
    z = p0 + (3 * s * s - 2 * s ** 3) * (p1 - p0) + (s ** 3 - s * s) * dT * v1
    return lerp(X_LAND, X_RUN, sm(s)), z, 0.0, 'run'
def inst_speed(t, h=0.02): return (inst_pos(t + h)[1] - inst_pos(t - h)[1]) / (2 * h)
# the flight path: (u in 0..1) height of the feet and forward distance
_FLY_Y = look.Path([(0.0, 0.0), (0.08, 1.35), (0.2, 2.05), (0.38, 1.9), (0.56, 1.3), (0.8, 0.55), (1.0, 0.0)])
def fly_state(t):
    u = seg01(t, T_HIT, T_LAND); z = lerp(Z_I, Z_LAND, 1 - (1 - u) ** 1.35); x = lerp(0.0, X_LAND, sm(u)); y = max(0.0, float(_FLY_Y(u)))
    return u, x, y, z

# =====================================================================================================================
#                                                      POSES
# =====================================================================================================================
def rclock(t): return t if course(t) == 1 else t - DUR           # the run clock: course 2 ends at 0 = frame 0
def run_arms(P, ph, amt, side=1.0):
    s_ = math.sin(ph)
    P['rh'] = (0.25, 1.12 + 0.12 * amt * max(0, -s_), 0.16 - 0.34 * amt * s_); P['lh'] = (-0.25, 1.12 + 0.12 * amt * max(0, s_), 0.16 + 0.34 * amt * s_)
    P['rpole'] = (0.6, -0.4, -1.0); P['lpole'] = (-0.6, -0.4, -1.0)
    P['rgrip'] = 0.8; P['lgrip'] = 0.8
def charge_amt(t):
    rc = rclock(t); c = 0.0
    hits = [T_H1] if course(t) == 2 else [T_H1, T_H2, T_H3, T_HIT, T_H4]
    for th in hits:
        pre = 0.32 if th == T_H1 else 0.45
        c = max(c, win(rc, th - pre, th + 0.25, 0.14))
    return c
def knight_pose(t):
    z = knight_z(t); v = knight_speed(t); rc = rclock(t)
    P = dict(base=(0.0, 0.0, z), yaw=0.0, eyes='open', mouth='neutral', brow=0.2, lean=0.04, cape_sway=0.25 * math.sin(t * 3.1), head=(0.0, 0.05, 0.0))
    if v > 0.15:
        ph = 2 * PI * (1.0 * rc + 0.2 * z); P['walk'] = ph; P['stride'] = min(0.6, 0.22 * v); P['lift'] = min(0.26, 0.09 * v)
        P['lean'] = 0.06 + 0.07 * v; run_arms(P, ph, min(1.0, v / VK))
        if v > 1.5: P['mouth'] = 'smile'; P['brow'] = 0.45; P['eyes'] = 'half'                      # cocky, eyes on the hurdle
    c = charge_amt(t)
    if c > 0:                                                                          # shoulder down
        P['lean'] = P['lean'] + 0.28 * c; P['twist'] = -0.5 * c; P['crouch'] = 0.09 * c
        P['rh'] = lerp3(P.get('rh', (0.24, 1.0, 0.1)), (0.08, 1.18, 0.2), c); P['lh'] = lerp3(P.get('lh', (-0.24, 1.0, 0.1)), (-0.28, 0.98, -0.12), c)
        P['brow'] = 0.2 + 0.6 * c; P['mouth'] = 'grit' if c > 0.5 else P['mouth']; P['eyes'] = 'half' if c > 0.6 else 'open'
    if course(t) == 1:
        # the grin grows after every smash
        for k_, th in enumerate((T_H1, T_H2, T_H3)):
            g = win(t, th + 0.15, th + 2.4, 0.2)
            if g > 0.3 and c < 0.5: P['mouth'] = 'smile'; P['brow'] = -0.1 - 0.15 * k_; P['head'] = (0.0, 0.05, 0.05 * (k_ + 1))
        if T0['02'] <= t < tend('02') + 0.2 and c < 0.5:                                # "See?" looks down at the empty gap
            P['mouth'] = 'open' if talking(t, '02') > 0.5 else 'smile'
            lk = win(t, T0['02'], ws('02', 1) + 0.4, 0.2); P['head'] = (-0.35 * lk, 0.05 - 0.3 * lk, 0.0); P['look'] = (-0.6 * lk, -0.5 * lk)
        f = win(t, T_FAKE - 0.05, T_H2 - 0.2, 0.15)                                     # the fake jump
        if f > 0:
            P['lean'] = lerp(P['lean'], -0.08, f); P['crouch'] = 0.2 * f * (1 - seg01(t, T_H2 - 0.45, T_H2 - 0.2)); P['head'] = (0.0, 0.45 * f, 0.0)
            P['look'] = (0.0, 0.7 * f); P['eyes'] = 'wide'; P['brow'] = 0.0; P['mouth'] = 'neutral'
            P['rh'] = lerp3(P.get('rh', (0.24, 1.0, 0.1)), (0.3, 0.95, -0.25), f); P['lh'] = lerp3(P.get('lh', (-0.24, 1.0, 0.1)), (-0.3, 0.95, -0.25), f)
        if T0['06'] - 0.3 <= t < T_HIT:                                                  # "Good. Stand right there." smirk, eyes on him
            P['eyes'] = 'half'; P['brow'] = 0.5
            P['mouth'] = 'open' if talking(t, '06') > 0.5 else ('smile' if c < 0.5 else 'grit')
        if t >= T_HIT + 0.2:                                                             # after the hit: stands, watches him fly, smug
            P['head'] = (0.0, 0.35 * win(t, T_HIT + 0.1, T_LAND + 0.2, 0.3), 0.0); P['mouth'] = 'smile'; P['brow'] = -0.2
    else:
        if v > 0.15 and talking(t, '09') > 0: P['mouth'] = 'open' if talking(t, '09') > 0.5 else 'smile'
        gl = win(t, T0['09'] - 0.15, tend('09') - 0.25, 0.25)                           # the glance back at the instructor
        if gl > 0: P['head'] = (-0.95 * gl, 0.05, 0.0); P['look'] = (-0.8 * gl, 0.0); P['brow'] = 0.4; P['eyes'] = 'half'
        if T_C2 <= t < T_LOOP and v < 2.0: P['mouth'] = 'smile'; P['brow'] = 0.35; P['eyes'] = 'half'
    return P
def inst_pose(t):
    x, z, yaw, mode = inst_pos(t); rc = rclock(t)
    P = dict(base=(x, 0.0, z), yaw=yaw, eyes='open', mouth='neutral', brow=0.5, lean=0.02, head=(0.0, 0.0, 0.0))
    P['lh'] = (-0.16, 1.62, 0.22); P['lgrip'] = 0.95; P['lpalm'] = (1.0, 0.0, 0.0); P['_pole'] = (0.0, 1.0, 0.0)
    P['rh'] = (0.2, 1.38, 0.5); P['rgrip'] = 0.15; P['rpalm'] = (0.0, -0.3, 1.0)                 # points ahead / over the hurdle
    fwd = V((math.sin(yaw), 0, math.cos(yaw)))
    if mode == 'run':
        v = inst_speed(t)
        if v > 0.15:
            ph = 2 * PI * (1.1 * rc + 0.25 * z); P['walk'] = ph; P['stride'] = min(0.5, 0.18 * v); P['lift'] = min(0.16, 0.06 * v); P['lean'] = 0.04 + 0.04 * v
        if course(t) == 1:
            if T0['03'] - 0.2 <= t < T_H2:                                              # "the next one's higher": the hand high
                hi = win(t, ws('03', 1) - 0.2, T_H2 - 0.1, 0.25); P['rh'] = lerp3(P['rh'], (0.25, 1.9, 0.35), hi); P['rpalm'] = (0.0, -1.0, 0.2)
                P['mouth'] = 'open' if talking(t, '03') > 0.5 else 'neutral'
            if T_H2 - 0.1 <= t < T_H3 + 0.6:                                              # the hand stops halfway: shock
                P['eyes'] = 'wide'; P['brow'] = -0.2; P['brow_up'] = 0.8; P['mouth'] = 'o'
                P['rh'] = (0.3, 1.55, 0.35)
            if t >= T0['04']:                                                               # looks down the open lane, then at the zero; frowns
                lk = seg01(t, T0['04'] + 0.3, ws('04', 1) + 0.2)
                P['head'] = (0.0, -0.25 + 0.6 * sm(lk), 0.0); P['look'] = (0.0, -0.4 + 0.9 * sm(lk)); P['brow'] = 0.9; P['mouth'] = 'frown'
                P['rh'] = (0.22, 1.05, 0.15); P['rgrip'] = 0.9
        else:                                                                              # course 2 (the loop): mouth opens, the sign goes up
            lk = win(t, T0['09'] - 0.1, tend('09') + 0.05, 0.2)
            P['head'] = (0.55 * lk, 0.0, 0.0); P['look'] = (0.5 * lk, 0.0)
            P['mouth'] = 'open' if (ws('09', 0) + 0.6 <= t < tend('09')) else 'neutral'; P['brow'] = 0.5 - 0.6 * lk
            up = seg01(t, tend('09') - 0.25, DUR - 0.05); chest = 1 - sm(up)
            P['lh'] = lerp3((-0.06, 1.22, 0.32), (-0.16, 1.62, 0.22), sm(up)); P['_pole'] = tuple(nz(lerp3((0.0, 0.25, 1.0), (0.0, 1.0, 0.0), sm(up))))
            P['rh'] = lerp3((0.08, 1.25, 0.3), (0.2, 1.38, 0.5), sm(up)); P['rgrip'] = lerp(0.8, 0.15, sm(up))
        P['_board'] = tuple(fwd)
    elif mode == 'stand':
        P['lh'] = (-0.2, 1.3, 0.18)
        P['mouth'] = 'open' if talking(t, '05') > 0.5 else 'neutral'; P['brow'] = 0.7
        st = win(t, T0['05'] - 0.3, ws('05', 1) + 0.1, 0.15)                              # "Stop." palm up at the knight
        P['rh'] = lerp3(P['rh'], (0.16, 1.55, 0.42), st); P['rpalm'] = (0.0, 0.2, 1.0); P['rgrip'] = 0.05
        dn = seg01(t, ws('05', 1) + 0.1, ws('05', 1) + 0.7)                               # lowers the sign, bends a knee: he will show it
        P['lh'] = lerp3(P['lh'], (-0.26, 0.98, 0.12), sm(dn)); P['crouch'] = 0.12 * sm(dn) * (1 - 0.4 * win(t, T0['06'], tend('06'), 0.2))
        P['rh'] = lerp3(P['rh'], (0.26, 1.02, 0.1), sm(dn) * (1 - st)); P['rf'] = (0.13, 0.075, 0.12 * sm(dn))
        if t >= T0['06'] - 0.1:                                                             # sees the shoulder coming
            sh = seg01(t, ws('06', 1), T_HIT); P['eyes'] = 'wide'; P['brow_up'] = sm(sh); P['brow'] = 0.7 - 0.9 * sm(sh); P['mouth'] = 'o' if sh > 0.3 else 'neutral'
            P['rh'] = lerp3((0.26, 1.02, 0.1), (0.2, 1.4, 0.4), sm(sh)); P['rpalm'] = (0.0, 0.2, 1.0); P['lean'] = -0.1 * sm(sh)
        P['_board'] = tuple(fwd)
    elif mode in ('sit', 'rise', 'stand2'):
        sit = 1.0 if mode == 'sit' else (1 - sm(seg01(t, *T_STAND)) if mode == 'rise' else 0.0)
        P['crouch'] = 0.82 * sit; P['lean'] = 0.1 * sit
        P['rf'] = lerp3((0.12, 0.075, 0.02), (0.16, 0.06, 0.62), sit); P['lf'] = lerp3((-0.12, 0.075, 0.02), (-0.18, 0.06, 0.55), sit)
        P['rkpole'] = (0.2, 0.6, 1.0); P['lkpole'] = (-0.2, 0.6, 1.0)
        P['lh'] = lerp3((-0.16, 1.3, 0.3), (-0.3, 0.42, 0.25), sit); P['_pole'] = (0.0, 1.0, 0.15)
        P['rh'] = lerp3((0.22, 1.0, 0.1), (0.3, 0.2, -0.1), sit); P['rpalm'] = (0.0, -1.0, 0.0); P['rgrip'] = 0.3
        if course(t) == 1:
            # "Wait. That counted?": over his shoulder up at the counter, then down at the boots in the gate
            up = win(t, T_LAND + 0.25, we('07', 0) + 0.9, 0.3); dn = seg01(t, ws('07', 1) + 0.5, ws('07', 1) + 1.0)
            P['head'] = (1.25 * max(up, sm(dn)), 0.55 * up - 0.2 * sm(dn), 0.0); P['look'] = (0.9 * max(up, sm(dn)), 0.8 * up - 0.4 * sm(dn))
            P['twist'] = 0.45 * max(up, sm(dn)); P['eyes'] = 'wide' if up > 0.5 else 'open'; P['brow_up'] = 0.6
            P['mouth'] = 'open' if talking(t, '07') > 0.5 else 'o'
        else:
            # course 2: stands, reads DOUBLE JUMP above his head, looks at the knight's shoulder, pulls the sign to his chest
            rd = win(t, T_DJ + 0.05, T_DJ + 0.9, 0.2); sh = seg01(t, T_DJ + 0.85, T_DJ + 1.2)
            P['head'] = (-0.9 * sm(sh) * (1 - rd), 0.6 * rd - 0.1 * sm(sh), 0.0); P['look'] = (-0.8 * sm(sh) * (1 - rd), 0.9 * rd - 0.2 * sm(sh))
            P['eyes'] = 'wide' if (rd > 0.4 or sh > 0.5) else 'open'; P['brow_up'] = max(rd, 0.7 * sm(sh)); P['mouth'] = 'o' if sh > 0.5 else 'neutral'
            if sit < 0.5:
                ch = sm(sh); P['lh'] = lerp3((-0.16, 1.3, 0.3), (-0.06, 1.22, 0.32), ch); P['_pole'] = tuple(nz(lerp3((0.0, 1.0, 0.15), (0.0, 0.25, 1.0), ch)))
                P['rh'] = lerp3((0.22, 1.0, 0.1), (0.08, 1.25, 0.3), ch); P['rgrip'] = 0.8
        P['_board'] = tuple(fwd)
    return P
def inst_fly(t):
    """the flight: built standing at the origin, then turned (tumble back, half spin) and moved along the path"""
    u, x, y, z = fly_state(t)
    P = dict(base=(0.0, 0.0, 0.0), yaw=0.0, eyes='wide', mouth='o', brow=-0.2, brow_up=0.6, lean=-0.1, head=(0.0, 0.0, 0.0))
    fl = math.sin(t * 19.0)
    P['lh'] = (-0.3, 1.85, 0.05 + 0.1 * fl); P['lgrip'] = 0.95; P['lpalm'] = (1.0, 0.0, 0.0); P['_pole'] = (0.15 * fl, 1.0, -0.2)
    P['rh'] = (0.45, 1.55 + 0.15 * fl, 0.1); P['rgrip'] = 0.1
    P['crouch'] = 0.25; P['rf'] = (0.14, 0.3, 0.3); P['lf'] = (-0.14, 0.45, 0.15); P['rkpole'] = (0.2, 0.3, 1.0); P['lkpole'] = (-0.2, 0.3, 1.0)
    sq = win(t, T_HIT + 0.3, T_ONE + 0.02, 0.1)                                         # turns his head to the counter and squints ...
    if sq > 0: P['head'] = (0.0, 0.5 * sq, 0.0); P['look'] = (0.0, 0.8 * sq); P['eyes'] = 'half'; P['brow'] = 0.8; P['brow_up'] = 0.0; P['mouth'] = 'neutral'
    if t >= T_ONE: up = sm(seg01(t, T_ONE, T_ONE + 0.12)); P['head'] = (0.0, 0.5 * (1 - 0.5 * up), 0.0); P['look'] = (0.0, 0.7); P['eyes'] = 'wide'; P['brow_up'] = 1.0; P['brow'] = -0.6; P['mouth'] = 'o'    # ... brows shoot up
    Q = instructor(P); Qs = jump_sign(P)
    tumble = -0.55 * math.sin(PI * min(1.0, u * 1.15))                                   # leans back in the air
    spin = PI * (1 - sm(seg01(u, 0.45, 0.88)))                                            # faces the knight (-z) -> lands facing +z
    R = hd.Ry(spin) @ hd.Rx(tumble); piv = V((0.0, 0.95, 0.0)); C = V((x, y + 0.95 - 0.5 * (1 - math.cos(tumble)), z))
    for q in Q + Qs:
        q['p'] = [tuple(C + R @ (V(p) - piv)) for p in q['p']]; refresh(q)
    for kk in ('_head', '_chest', '_pel', '_signc'):
        if kk in P: P[kk] = C + R @ (V(P[kk]) - piv)
    return P, Q, Qs

# =====================================================================================================================
#                                                      SET (training yard)
# =====================================================================================================================
STONE = [(186, 178, 160), (172, 164, 148), (196, 188, 170), (164, 158, 142)]
SAND = [(204, 180, 136), (196, 172, 128), (210, 188, 144)]
GRASS = [(112, 160, 76), (104, 150, 70), (120, 168, 82)]
WALLC = (164, 156, 142)
def chunk(z0, z1, seed):
    """one 8 m piece of the yard: stone floor, the sandy lane, low stone walls with a cap, banner posts, grass + trees outside"""
    Q = []
    Q += dtx.ground(-3.0, -1.0, z0, z1, 1.0, STONE, seed=seed) + dtx.ground(1.0, 3.0, z0, z1, 1.0, STONE, seed=seed + 1)
    Q += dtx.ground(-1.0, 1.0, z0, z1, 1.0, SAND, seed=seed + 2)
    Q += dtx.ground(-16.0, -3.0, z0, z1, 4.0, GRASS, seed=seed + 3) + dtx.ground(3.0, 16.0, z0, z1, 4.0, GRASS, seed=seed + 4)
    for sd in (1, -1):
        zz = z0
        while zz < z1 - 1e-6:
            L_ = 1.0 + 0.3 * hsh(int(zz * 7) + sd, seed); zb = min(z1, zz + L_)
            Q += hd.bx((sd * 3.25, 0.5, (zz + zb) / 2), np.eye(3), (0.25, 0.5, (zb - zz) / 2 - 0.01), hd.shade(WALLC, 0.9 + 0.15 * hsh(int(zz * 5), seed + sd)))
            zz = zb
        Q += hd.bx((sd * 3.25, 1.04, (z0 + z1) / 2), np.eye(3), (0.3, 0.05, (z1 - z0) / 2), hd.shade(WALLC, 1.08))
        # banner post with a tutorial flag (blue / yellow)
        pz = z0 + 4.0
        Q += hd.bx((sd * 3.25, 2.0, pz), np.eye(3), (0.05, 1.0, 0.05), (110, 80, 50))
        fc = (44, 92, 196) if (int(z0 / 8) + (sd > 0)) % 2 else (236, 196, 52)
        Q += [q for q in [hd.face([(sd * 3.25, 2.95, pz), (sd * 3.25, 2.95, pz + 0.7), (sd * 3.25 - sd * 0.02, 2.25, pz + 0.55), (sd * 3.25 - sd * 0.02, 2.2, pz + 0.05)], fc),
                          hd.face([(sd * 3.25, 2.95, pz), (sd * 3.25 - sd * 0.02, 2.2, pz + 0.05), (sd * 3.25 - sd * 0.02, 2.25, pz + 0.55), (sd * 3.25, 2.95, pz + 0.7)], fc)] if q]
        # barrels / hay bales outside the wall
        if hsh(int(z0), seed + 9 + sd) > 0.4:
            bz = z0 + 1.5 + 4 * hsh(int(z0), seed + 10 + sd)
            Q += hd.lathe((sd * 4.1, 0.0, bz), np.eye(3), [(0.3, 0.0), (0.34, 0.4), (0.3, 0.8)], 9, (140, 96, 56))
        if hsh(int(z0), seed + 11 + sd) > 0.5:
            Q += hd.bx((sd * 4.6, 0.32, z0 + 6.0), hd.Ry(0.3), (0.5, 0.32, 0.35), (214, 186, 96))
    for i in range(3):
        sd = 1 if hsh(i, seed + 20) > 0.5 else -1; x = sd * (6.0 + 8 * hsh(i, seed + 21)); zt = z0 + 8 * hsh(i, seed + 22)
        Q += dtx.tree(x, zt, 4 + 2.5 * hsh(i, seed + 23), col=(74, 120, 64), trunk=(96, 70, 44), seed=seed + i)
    return [q for q in Q if q]
CHUNK = 8.0
_CH = {}
def yard(zc, reach=36.0):
    Q = []
    k0 = int(math.floor((zc - reach) / CHUNK)); k1 = int(math.floor((zc + reach) / CHUNK))
    for k in range(k0, k1 + 1):
        if k not in _CH:
            if len(_CH) > 40: _CH.clear()
            _CH[k] = chunk(k * CHUNK, (k + 1) * CHUNK, 100 + (k % 7) * 13)
        Q += _CH[k]
    return Q
GATE_STONE = (150, 142, 128)
def gatehouse(z, lift, panel_txt=None, panel_col=(255, 186, 60), lamp=None, counter_back=None):
    """stone gatehouse across the yard at z: two towers, a lintel, an iron portcullis that rises by `lift` 0..1,
    above it the counter panel (pixel text on both faces) or a lamp"""
    Q = []
    for sd in (1, -1):
        Q += hd.bx((sd * 2.1, 2.3, z), np.eye(3), (0.9, 2.3, 0.6), GATE_STONE)
        Q += hd.bx((sd * 2.1, 4.7, z), np.eye(3), (1.0, 0.12, 0.7), hd.shade(GATE_STONE, 1.1))
        for m in range(3): Q += hd.bx((sd * (1.45 + 0.6 * m), 4.95, z), np.eye(3), (0.18, 0.15, 0.62), hd.shade(GATE_STONE, 1.05))
        Q += hd.bx((sd * 5.0, 1.6, z), np.eye(3), (2.0, 1.6, 0.4), hd.shade(GATE_STONE, 0.95))
    Q += hd.bx((0, 3.9, z), np.eye(3), (1.25, 0.7, 0.55), hd.shade(GATE_STONE, 0.97))
    yo = 3.0 * lift
    for i in range(7): Q += hd.bx((-1.05 + 0.35 * i, 1.5 + yo, z), np.eye(3), (0.022, 1.5, 0.022), (60, 62, 70))
    for j in range(5): Q += hd.bx((0, 0.3 + 0.62 * j + yo, z), np.eye(3), (1.15, 0.025, 0.025), (60, 62, 70))
    for i in range(7): Q += hd.bx((-1.05 + 0.35 * i, 0.03 + yo, z), np.eye(3), (0.035, 0.05, 0.035), (90, 92, 100))
    if panel_txt is not None:
        for sd in (1, -1):
            n = V((0, 0, -sd * 1.0)); u = V((sd * 1.0, 0, 0)); c = V((0, 3.72, z - sd * 0.56))
            Q += panel(c, u, V((0, 1.0, 0)), n, 1.0, 0.27, (34, 28, 26)) + panel(c + n * 0.003, u, V((0, 1.0, 0)), n, 0.96, 0.23, (18, 14, 14), emit=True)
            txt = panel_txt if (counter_back is None or sd > 0) else counter_back
            Q += glyph_quads(txt, c + n * 0.006, u, V((0, 1.0, 0)), n, 0.034, panel_col)
    if lamp is not None:
        for sd in (1, -1): Q += panel(V((0, 3.72, z - sd * 0.56)), V((sd * 1.0, 0, 0)), V((0, 1.0, 0)), V((0, 0, -sd * 1.0)), 0.3, 0.16, lamp, emit=True)
    return [q for q in Q if q]
def sky(zc):
    """sunny sky: emissive dome (blue overhead, pale at the horizon) + a few flat clouds, centred on the camera's z"""
    def col(e):
        stops = [(0.0, (226, 236, 244)), (0.15, (186, 214, 240)), (0.45, (120, 172, 232)), (1.0, (84, 140, 220))]
        for (a, ca), (b, cb) in zip(stops, stops[1:]):
            if e <= b: return mixc(ca, cb, (e - a) / (b - a))
        return stops[-1][1]
    Q = hd.ellip((0, -6, zc), np.eye(3), (120, 90, 120), 24, 10, (200, 220, 240), v1=PI * 0.54, closed=False, colfn=lambda i, j, cl: col(max(0.0, cl[1] / 90)))
    for q in Q: q['emit'] = True
    for i in range(10):
        a = 2 * PI * hsh(i, 61); r = 70 + 20 * hsh(i, 62); x = r * math.sin(a); zz = zc + r * math.cos(a); y = 26 + 22 * hsh(i, 63)
        C_ = hd.ellip((x, y, zz), hd.Ry(a), (16 + 10 * hsh(i, 64), 2.5, 6), 10, 4, (248, 250, 252))
        for q in C_: q['emit'] = True
        Q += C_
    return [q for q in Q if q]
_SKY = {}
def sky_at(zc):
    """the dome is built once and moved with the camera (no pop when the camera travels)"""
    if 'q' not in _SKY: _SKY['q'] = sky(0.0)
    out = []
    for q in _SKY['q']:
        p_ = [(x, y, z + zc) for (x, y, z) in q['p']]; out.append(dict(q, p=p_, c=q['c'] + V((0, 0, zc))))
    return out

# =====================================================================================================================
#                                                      CAMERA
# =====================================================================================================================
Z_CAM0 = 4.35; X_CAM0 = -0.3; Y_CAM0 = 1.5; FOV0 = 31.0
def cam_open(t):
    """frame 0 (and the loop): beyond hurdle 1, looking back at the knight; tracks back from t = 0, holds (creeping) before 0"""
    zk = knight_z(t) if t >= 0 else _z2(t, VW2)
    if t >= 0: dz = 2.0 * (t * t / 1.2 if t < 0.6 else (t - 0.3))
    else: dz = 0.0
    sway = 0.03 * math.sin(t * 0.9)
    pos = V((X_CAM0 + sway, Y_CAM0, Z_CAM0 + dz)); tgt = V((-0.12, 1.02, zk + 0.2))
    return pos, tgt, FOV0
def cam_shot(t):
    sc = scene(t); zk = knight_z(t)
    idx = [n for n, _ in CUTS].index(sc); a = CUTS[idx][1]; b = CUTS[idx + 1][1] if idx + 1 < len(CUTS) else DUR; u = sm(seg01(t, a, b))
    if sc == 'open': return cam_open(t)
    if sc == 'side': return V((2.6, 1.35, zk + 0.35 + 0.25 * u)), V((0.0, 1.15, zk + 0.05)), 42.0
    if sc == 'low': return V((2.55, 0.5, zk + 0.75)), V((0.0, 1.4, zk + 0.3)), 48.0
    if sc == 'h3':
        d = lerp(3.7, 3.0, u); return V((1.45, 1.62, zk + d)), V((-0.25, 1.38, zk + 0.1)), 42.0
    if sc == 'stop':
        p = V((0.4, 1.6, Z_I - 2.3)); tg = V((0.0, 1.78, Z_I)); return V(motion.dolly(tuple(p), tuple(tg), motion.creep(t, a, 0.0025))), tg, 46.0
    if sc == 'charge': return V((2.6, 1.3, lerp(Z_I - 1.45, Z_I - 1.1, u))), V((0.0, 1.15, Z_I - 0.85)), 46.0
    if sc == 'flight':
        _, x_, y_, z_ = fly_state(t); w_ = sm(seg01(t, T_HIT, T_LAND - 0.3))
        tg = V((lerp(0.0, -0.3, w_), lerp(1.9, 2.4, w_), lerp(Z_I + 1.2, GZ, w_)))
        return V((lerp(1.35, 1.2, u), lerp(0.95, 1.1, u), lerp(Z_I - 2.7, Z_I - 2.1, u))), tg - V((0.1, 0, 0)), 42.0
    if sc == 'gate':
        p = V((0.85, 0.9, GZ + 6.2)); tg = V((-0.45, 1.25, GZ + 2.0)); return V(motion.dolly(tuple(p), tuple(tg), motion.creep(t, a, 0.002))), tg, 50.0
    if sc == 'c2':
        # one continuous shot: from the instructor rising by the entry gate, pulling back into the frame-0 framing (eases to a stop at DUR)
        pe, te, fe = cam_open(DUR - 1e-4 - DUR)
        ps = V((0.15, 1.45, ZS + 6.4)); ts = V((-0.5, 1.3, ZS + 2.6))
        s = seg01(t, T_C2 + 0.2, DUR); e = 1 - (1 - s) ** 2 if s < 1 else 1.0
        e = sm(s)
        tgt_k = V((-0.12, 1.02, knight_z(t) + 0.2))
        tg = lerp3(tuple(ts), tuple(tgt_k), sm(seg01(t, T_LOOP - 0.4, DUR - 0.25)))
        return V(lerp3(tuple(ps), tuple(pe), e)), V(tg), lerp(44.0, FOV0, e)
    return cam_open(t)

# =====================================================================================================================
#                                                      RENDER
# =====================================================================================================================
def world(t):
    pos, tgt, fov = cam_shot(t); c2 = course(t) == 2
    KP = knight_pose(t); QK = knight(KP)
    x, z, yaw, mode = inst_pos(t)
    if mode == 'fly': IP, QI, QS = inst_fly(t)
    else: IP = inst_pose(t); QI = instructor(IP); QS = jump_sign(IP)
    zc = float(pos[2]) * 0.5 + float(tgt[2]) * 0.5
    layers = [sky_at(zc), yard(zc)]
    hz = [(1, Z_H1, None if c2 else T_H1)]
    if not c2: hz += [(2, Z_H2, T_H2), (3, Z_H3, T_H3), (4, Z_H4, T_H4)]
    else: hz += [(2, Z_H2, None), (3, Z_H3, None)]
    for i, zz, th in hz:
        if abs(zz - zc) < 40: layers.append(hurdle_faces(i, zz, t, th))
    # gates: the entry gate (open, green lamp) and the exit gate with the counter
    if abs(ZS - zc) < 45: layers.append(gatehouse(ZS, 1.0, lamp=(90, 230, 110)))
    if not c2 and abs(GZ - zc) < 60:
        lift = sm(seg01(t, *T_GATE)); one = t >= T_ONE; blink = one and t < T_ONE + 0.6 and int((t - T_ONE) * 10) % 2 == 1
        txt = 'JUMPS 1/1' if one else 'JUMPS 0/1'; col = (90, 255, 120) if one else (255, 186, 60)
        if blink: col = (200, 255, 210)
        layers.append(gatehouse(GZ, lift, panel_txt=txt, panel_col=col))
    layers += [QK, QI, QS]
    sun = V(tgt) + V((-5.0, 9.0, 3.0)); fill = V(tgt) + V((4.0, 3.0, -4.0))
    L = [(tuple(sun), (255, 240, 214), 20.0), (tuple(fill), (170, 196, 236), 4.5)]
    return layers, L, (KP, IP)
SHAKE = []
def frame_low(t):
    pos, tgt, fov = cam_shot(t)
    sh = 0.0
    for th in ([T_H1] if course(t) == 2 else [T_H1, T_H2, T_H3, T_HIT]):
        sh += motion.kick(rclock(t), th, amp=0.035 if th != T_HIT else 0.06)
    pos = V(pos) + V((0.0, sh, 0.0))
    cam = Camera.look(tuple(pos), tuple(tgt))
    layers, L, poses = world(t)
    R = Renderer(W, H, fog=(214, 228, 240))
    img, vi, zb = zrender(R, cam, layers, L, fov=fov, fog_start=12, fog_end=31, ambient=0.5, return_z=True)
    a = look.outline(np.asarray(img).astype(np.float32), zb)
    a = np.clip((a - 80) * 1.08 + 86, 0, 255)
    return post.ps1(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), levels=6), vi, R, poses

# ======================= overlays (1080 x 1920) =======================
def tw(s, sc): return font.width(s, sc)
def ctext(d, s, y, sc, col, o=4, x=None):
    x = int(540 - tw(s, sc) / 2) if x is None else x
    look.draw_cells(d, look.text_cells(s, x, y, sc, col), o)
TX = dict(tut1='EĞİTİM 1-1' if TRL else 'TUTORIAL 1-1', tut2='EĞİTİM 1-2' if TRL else 'TUTORIAL 1-2',
          jumps='ZIPLAMA' if TRL else 'JUMPS', press=('BAS', 'ZIPLA') if TRL else ('PRESS', 'TO JUMP'),
          cov=('EĞİTİMLER NEDEN', 'HEP ZIPLATIR?') if TRL else ('WHY DO', 'TUTORIALS MAKE', 'YOU JUMP?'),
          dj=('YENİ DERS', 'ÇİFT ZIPLAMA') if TRL else ('NEW LESSON', 'DOUBLE JUMP'))
for _s in [TX['tut1'], TX['tut2'], TX['jumps'], *TX['press'], *TX['cov'], *TX['dj']]: font.check(_s)
GLD = (255, 214, 96); WHT = (246, 242, 230); GRN = (100, 255, 130); AMB = (255, 196, 70)
def counter_state(t):
    if course(t) == 2: return 0, 2
    return (1 if t >= T_ONE else 0), 1
def hud(d, t):
    """top-left: TUTORIAL 1-1 + the jump counter (pulses on 'Watch the counter', turns green with a pop at 1/1)"""
    n, m = counter_state(t); lab = TX['tut2'] if course(t) == 2 else TX['tut1']
    d.rectangle([40, 40, 560, 236], fill=(16, 20, 40)); d.rectangle([40, 40, 560, 236], outline=GLD, width=5)
    ctext(d, lab, 62, 5, (200, 210, 236), o=3, x=66)
    pp = 0.0
    if course(t) == 1:
        pp = max(win(t, ws('01', 1) - 0.05, ws('01', 1) + 0.6, 0.12), win(t, ws('04', 1) + 0.3, ws('04', 1) + 0.9, 0.12) * 0.7)
        pp = max(pp, 1 - seg01(t, T_ONE, T_ONE + 0.35) if t >= T_ONE else 0.0)
    sc = 10 + int(round(3 * pp)); col = GRN if (n >= m and course(t) == 1) else (WHT if pp > 0.5 else AMB)
    s = f"{TX['jumps']} {n}/{m}"; ctext(d, s, 116 - int(10 * pp), sc, col, o=6, x=66)
def prompt_on(t):
    """PRESS X TO JUMP while the knight runs at a hurdle he will not jump"""
    rc = rclock(t)
    hs = [T_H1] if course(t) == 2 else [T_H1, T_H2, T_H3]
    for th in hs:
        if th - 2.1 <= rc < th - 0.05: return int((rc - th) * 6) % 3 != 0
    return False
def prompt(d, t):
    if not prompt_on(t): return
    y = 1290; sc = 7; a, b = TX['press']
    wa, wb = tw(a, sc), tw(b, sc); bw_ = 92; tot = wa + 30 + bw_ + 30 + wb; x0 = int(540 - tot / 2)
    d.rectangle([x0 - 26, y - 30, x0 + tot + 26, y + 7 * sc + 30], fill=(10, 12, 26)); d.rectangle([x0 - 26, y - 30, x0 + tot + 26, y + 7 * sc + 30], outline=(120, 140, 220), width=4)
    ctext(d, a, y, sc, WHT, x=x0); cx = x0 + wa + 30 + bw_ // 2; cy = y + 7 * sc // 2
    d.ellipse([cx - 44, cy - 44, cx + 44, cy + 44], fill=(40, 90, 210), outline=(230, 236, 255), width=5); ctext(d, 'X', cy - 24, 7, WHT, o=3, x=cx - 17)
    ctext(d, b, y, sc, WHT, x=x0 + wa + 30 + bw_ + 30)
def cover(d, t):
    if not (0 <= t < T0['01'] + 0.35): return
    lines = TX['cov']; scs = [9, 10, 11] if len(lines) == 3 else [9, 11]; y = 292
    w = max(tw(s, sc) for s, sc in zip(lines, scs))
    yy = y
    for i, (s, sc) in enumerate(zip(lines, scs)):
        if i == len(lines) - 1: d.rectangle([540 - w / 2 - 30, yy - 18, 540 + w / 2 + 30, yy + 7 * sc + 18], fill=(36, 70, 170))
        ctext(d, s, yy, sc, (255, 222, 40) if i == len(lines) - 1 else WHT, o=6); yy += 7 * sc + 34
def double_jump(d, t, vi, R, IP):
    if not (course(t) == 2 and T_DJ <= t < T_LOOP + 0.35): return
    hc = V(IP['_head']) + V((0.0, 0.42, 0.0)); p = R.project(tuple(hc), vi)
    if p is None: return
    x, y = p[0] * S, p[1] * S; pop = sm(seg01(t, T_DJ, T_DJ + 0.15)); fade = 1 - seg01(t, T_LOOP + 0.15, T_LOOP + 0.35)
    if fade <= 0: return
    sc1, sc2 = (5, 9) if pop >= 1 else (4, 7); a, b = TX['dj']
    y = max(330, min(1100, y - 120)); x = max(60 + tw(b, sc2) / 2, min(1020 - tw(b, sc2) / 2, x))
    w = tw(b, sc2)
    d.rectangle([x - w / 2 - 26, y - 22, x + w / 2 + 26, y + 7 * sc1 + 7 * sc2 + 46], fill=(20, 16, 40)); d.rectangle([x - w / 2 - 26, y - 22, x + w / 2 + 26, y + 7 * sc1 + 7 * sc2 + 46], outline=GLD, width=5)
    ctext(d, a, y, sc1, (200, 210, 236), o=3, x=int(x - tw(a, sc1) / 2)); ctext(d, b, y + 7 * sc1 + 20, sc2, GLD, o=5, x=int(x - w / 2))
COL = {'N': (242, 238, 226), 'K': (150, 200, 255), 'I': (255, 222, 90)}
def _sub_scr():
    if not TRL: return SCR
    import importlib.util as _iu
    sp_ = _iu.spec_from_file_location('tj_tts', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'tts', 'tj.py'))
    m_ = _iu.module_from_spec(sp_); sp_.loader.exec_module(m_); TRS = m_.TR_SUB
    out = dict(SCR); sent = {}
    for k, v in SCR['sent'].items():
        if len(v) == len(TRS[k]): sent[k] = [[a, b, tx] for (a, b, _), tx in zip(v, TRS[k])]
        else: sent[k] = [[v[0][0], v[-1][1], ' '.join(TRS[k])]]
    out['sent'] = sent
    return out
SUBS = look.Subtitles(_sub_scr(), [x for x in LINES if x[0] != '00'], W, H, S, COL, title_key='none', n=17,
                      hil=({'SAYACA', 'SIFIR.', 'İKİ', 'SAYILDI'} if TRL else {'COUNTER.', 'ZERO.', 'COUNTED?', 'TWO', 'TWICE?', 'SHORTCUT'}))
from nightkit import cta
CTA = cta.Achievement(t0=ws('04', 1) + 0.2, lang=SUB_LANG, dur=F(1.5), y=300)
def frame_final(t):
    if t >= DUR: t = t - DUR
    img, vi, R, (KP, IP) = frame_low(t); arr = post.upscale(img, S)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    hud(d, t); prompt(d, t); cover(d, t); double_jump(d, t, vi, R, IP)
    if T_ONE <= t < T_ONE + 0.12 and course(t) == 1: pass
    arr = np.asarray(im).astype(np.float32)
    arr = SUBS.apply(arr, t); arr = CTA.apply(arr, t)
    return arr

TEST = os.environ.get('TEST')
if TEST and __name__ == '__main__':
    if TEST == 'seq': ts = sorted(set([round(a + (b - a) * f, 2) for i, (n_, a) in enumerate(CUTS) for b in [CUTS[i + 1][1] if i + 1 < len(CUTS) else DUR] for f in (0.1, 0.5, 0.9)]))
    else: ts = [float(x) for x in TEST.split(',')]
    tw_ = int(os.environ.get('TW', '200')); th = tw_ * 16 // 9
    ims = [Image.fromarray(np.clip(frame_final(x), 0, 255).astype(np.uint8)) for x in ts]
    if os.environ.get('SZ') == 'full':
        for x, im in zip(ts, ims): im.save(f'test_tj_{x:.2f}.png')
    ims = [im.resize((tw_, th), Image.LANCZOS) for im in ims]
    per = int(os.environ.get('PER', '9')); rows = (len(ims) + per - 1) // per; shp = Image.new('RGB', (min(per, len(ims)) * (tw_ + 2), rows * (th + 18)), (30, 30, 30))
    dd = ImageDraw.Draw(shp)
    for i, (im, x) in enumerate(zip(ims, ts)): shp.paste(im, ((i % per) * (tw_ + 2), (i // per) * (th + 18))); dd.text(((i % per) * (tw_ + 2) + 4, (i // per) * (th + 18) + th + 3), f'{x:.2f} {x / 1.2:.1f}f {scene(x)}', fill=(255, 255, 0))
    shp.save(os.environ.get('TEST_OUT', 'test_tj.png')); print('test written', DUR, round(DUR / 1.2, 2), SEQS); sys.exit()

QA = dict(fps=FPS, dur=DUR, W=W, frame=lambda t: Image.fromarray(np.clip(frame_final(t), 0, 255).astype(np.uint8)).resize((W, H), Image.BOX), chars={},
          geom=lambda t, name, st, V_: [], camera=lambda t: cam_shot(t)[0], min_cam_dist=0.3, camera_ok=lambda p: True, allow_jump=[], weapon_events=[],
          scenes=[dict(id=nm, t0=a, t1=(CUTS[i + 1][1] if i + 1 < len(CUTS) else DUR), action=nm) for i, (nm, a) in enumerate(CUTS)],
          texts=lambda: [('hud', s, 10) for s in TX['cov']])

# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as _sf
    s = Sound(DUR, loop=False, seed=61); sr = s.sr; n = s.n; t = s.t
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
    def thud(t0, f=60, v=0.1, d=0.3, buf=None): tt = s.T(d); put(FX if buf is None else buf, np.sin(2 * np.pi * f * tt * (1 - 0.3 * tt / d)) * np.exp(-tt * 14), t0, v)
    SQ = (1.0, 0.0, 0.33, 0.0, 0.2)
    # bed: outdoor air + birds
    BED += s.filt(s.rng.normal(0, 1, n), lo=120, hi=900) * 0.006
    x = 0.4; k = 0
    while x < DUR - 0.3:
        m0 = 88 + 6 * hsh(k, 3); tone(x, m0, 0.09, 0.006, dec=18, glide=0.25, buf=BED); tone(x + 0.11, m0 + 3, 0.07, 0.005, dec=20, glide=-0.2, buf=BED)
        x += 1.1 + 1.6 * hsh(k, 4); k += 1
    # tutorial music: a bright chiptune loop on a grid that divides DUR (the loop seam stays on the beat)
    nb16 = max(1, round(DUR / (16 * 60 / 140.0))); bt = DUR / (16 * nb16)
    bass = [48, 48, 55, 48, 53, 53, 55, 52, 48, 48, 55, 48, 53, 55, 47, 55]
    arp = [72, 76, 79, 76, 72, 77, 81, 77, 71, 74, 79, 74, 72, 76, 79, 84]
    live = lambda x_: not (T_HIT - 0.05 <= x_ < T_C2) if True else True
    for b_ in range(16 * nb16):
        x = b_ * bt; i = b_ % 16
        if not live(x): continue
        tone(x, bass[i], bt * 0.9, 0.04, dec=4, harm=SQ, buf=MUS)
        tone(x, arp[i], bt * 0.45, 0.018, dec=9, harm=SQ, buf=MUS); tone(x + bt / 2, arp[(i + 2) % 16], bt * 0.4, 0.012, dec=10, harm=SQ, buf=MUS)
        if i % 2 == 0: nb(x, 0.05, 3000, 9000, 0.012, 300 + b_, 0.5, buf=MUS)
        if i % 4 == 2: thud(x, 120, 0.03, 0.1, buf=MUS)
    # footsteps (knight heavy + armour, instructor light), from the run phases
    def steps(fn_z, fn_c, cad, off, v, f0, jingle, a, b):
        ts_ = np.arange(a, b, 1 / 240.0); last = None
        for x_ in ts_:
            ph = 2 * np.pi * (cad * fn_c(x_) + off * fn_z(x_)); sgn = math.sin(ph) >= 0
            if last is not None and sgn != last:
                thud(x_, f0, v, 0.12); nb(x_, 0.06, 1500, 5000, v * 0.25, int(x_ * 997) % 10000, 1)
                if jingle: tone(x_ + 0.01, 98 + 3 * (int(x_ * 13) % 3), 0.06, v * 0.08, dec=40)
            last = sgn
    kz = lambda x_: knight_z(x_); kc = lambda x_: rclock(x_)
    steps(kz, kc, 1.0, 0.2, 0.05, 85, True, 0.0, T_HIT + 0.3)
    steps(kz, kc, 1.0, 0.2, 0.035, 85, True, WALK_A, T_C2 - 0.02)
    steps(kz, kc, 1.0, 0.2, 0.05, 85, True, T_C2 + 0.05, DUR)
    iz = lambda x_: inst_pos(x_)[1]
    steps(iz, kc, 1.1, 0.25, 0.018, 120, False, 0.0, T0['05'] - 0.25)
    steps(iz, kc, 1.1, 0.25, 0.018, 120, False, T_JOG + 0.2, DUR)
    # the smashes: whoosh into the shoulder, a crack + splinters, the planks clatter when they land
    def smash(th, v=1.0, dist=1.0):
        nb(th - 0.25, 0.25, 400, 2500, 0.03 * v, int(th * 31), 2)
        thud(th, 68, 0.16 * v * dist, 0.35); nb(th, 0.28, 300, 5000, 0.16 * v * dist, int(th * 37), 0.4)
        for m in range(6): tone(th + 0.02 + 0.03 * m, 60 + 12 * hsh(m, int(th)), 0.04, 0.03 * v * dist, dec=60, harm=(1.0, 0.6, 0.4))
    for i, (zz, th) in enumerate(((Z_H1, T_H1), (Z_H2, T_H2), (Z_H3, T_H3))):
        smash(th)
        for pc in pieces(i + 1, zz, th): thud(th + pc['tl'], 140 + 60 * hsh(pc['j'], 2), 0.025, 0.08); nb(th + pc['tl'], 0.05, 800, 4000, 0.02, int(pc['tl'] * 999), 1)
    # the hit: whoosh, body thump, an 'oof', then the GAME'S JUMP SOUND (the joke), the counter ding + fanfare, the gate chain + clank
    nb(T_HIT - 0.3, 0.3, 400, 2500, 0.04, 901, 2); thud(T_HIT, 55, 0.2, 0.4); nb(T_HIT, 0.18, 150, 900, 0.08, 902, 1)
    tone(T_HIT + 0.04, 62, 0.28, 0.06, dec=3, glide=1.6, harm=SQ)
    tone(T_ONE, 84, 0.12, 0.04, dec=10, harm=SQ); tone(T_ONE + 0.1, 91, 0.35, 0.04, dec=5, harm=SQ)
    for k_, m in enumerate((72, 76, 79, 84)): tone(T_ONE + 0.22 + 0.08 * k_, m, 0.3 if k_ == 3 else 0.12, 0.025, dec=6, harm=SQ, buf=MUS)
    tt = s.T(T_GATE[1] - T_GATE[0]); put(FX, s.filt_short(s.noise(T_GATE[1] - T_GATE[0], 77), lo=1500, hi=6000) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 28 * tt))), T_GATE[0], 0.05)
    thud(T_GATE[1], 48, 0.1, 0.4); tone(T_GATE[1], 55, 0.2, 0.03, dec=8, harm=(1.0, 0.7, 0.5))
    nb(T_LAND - 0.05, 0.2, 200, 1500, 0.05, 903, 1); thud(T_LAND, 60, 0.18, 0.3)
    smash(T_H4, 0.6, 0.6)
    tone(T_DJ, 84, 0.1, 0.03, dec=10, harm=SQ); tone(T_DJ + 0.08, 88, 0.1, 0.03, dec=10, harm=SQ); tone(T_DJ + 0.16, 96, 0.3, 0.03, dec=6, harm=SQ)
    tone(ws('01', 1), 96, 0.06, 0.02, dec=30, harm=SQ)
    # PRESS X prompt blips (each time it appears)
    for th in (T_H1, T_H2, T_H3): tone(th - 2.1, 91, 0.05, 0.012, dec=40, harm=SQ)
    if CTA.on: put(FX, cta.chime(sr), CTA.t0, 1.0)
    # voice
    NB = np.zeros(n); wins = []
    for k_, t0 in LINES:
        f_ = os.path.join(TTS_DIR, 'tj', f'{k_}.wav')
        if not os.path.exists(f_): continue
        a, ar = _sf.read(f_); a = a if a.ndim == 1 else a.mean(1)
        a = np.interp(np.arange(int(len(a) * sr / ar)) / sr, np.arange(len(a)) / ar, a); act = np.abs(a) > 0.02 * np.abs(a).max()
        a = a * (0.12 / np.sqrt((a[act] ** 2).mean())); put(NB, a, t0); wins.append((t0, t0 + len(a) / sr))
    gd = duck_envelope(n, sr, wins, -9.0, 0.05, 0.25) if wins else np.ones(n)
    bed = BED * gd + MUS * (0.5 + 0.5 * gd); fx = FX * (0.65 + 0.35 * gd)
    L = bed + fx; R_ = np.roll(bed, 700) + np.roll(fx, 200)
    pk = max(np.abs(L).max(), np.abs(R_).max()); gv = (pk * 1.6 / np.abs(NB).max()) if np.abs(NB).max() > 0 else 0.0
    s.L = L + NB * gv; s.R = R_ + NB * gv; s.reverb(0.12, length=1.2, decay=4.0)
    fi = np.clip(t / 0.008, 0, 1); s.L = s.L * fi; s.R = s.R * fi
    return s.save(path, peak=0.9)
if __name__ == '__main__' and os.environ.get('PART') == 'audio':
    print(build_audio(os.path.join(OUT, os.environ.get('AUDIO_NAME', 'tutorial_jump.wav')))); sys.exit()
if __name__ == '__main__' and os.environ.get('PART'):
    a, b = map(int, os.environ['PART'].split(':'))
    import subprocess
    p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W * S}x{H * S}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', os.path.join(OUT, f"{os.environ.get('PART_PREFIX', 'tj')}_{a:05d}.mp4")], stdin=subprocess.PIPE)
    vhs = post.VHS(W * S, H * S, S, grade='none', chroma=0, scan_dark=1.0, vignette=0.35, grain=1.2, band_period=1e9)
    for f in range(a, min(b, N)): p.stdin.write(vhs(frame_final(f / FPS), f, f / FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done', a, b); sys.exit()
