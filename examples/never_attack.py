"""WHAT IF YOU NEVER ATTACK THE FINAL BOSS? (Insert Disc 2, 26 Nov 2026) ~30 s final (x1.2 after), nightkit HD, 9:16.
Brief: briefs/never_attack.md. Voices: Enes's cloned voice, tools/tts/na.py (TR: his own takes).
Turn-based rule: the hero moves first. The knight picks WAIT, every turn, so the boss can never act. TURNS WAITED climbs
(x1 -> x10 -> x100 -> x1000): the boss shouts, taps his foot, gives up, sits down and offers tea. Centuries pass (candles melt,
cobwebs, beards). "Every hero hit me in the first second. You stayed." The counter hits 9,999 -> MAX -> "Oh no... not again." ->
the game overflows and resets to frame 0: young boss, young knight, counter 0. "Kneel, mortal!" ... then a whisper: "Psst... tea again?"
Reuses: final_boss arena (throne dais, torches, gate), dragon_taxes KNIGHT, boss_wanted's HD boss (copied: that module loads its own voice).
New: battle menu + TURNS WAITED HUD, teacups + teapot, candles that melt, cobwebs, beards, overflow glitch.
Render in sequences (Enes, 26 Nov):  python tools/render_seq.py examples/never_attack.py --prefix na --seqs s1,s2,s3,s4,s5 / --master <out>
Stills: TEST=seq python examples/never_attack.py -> test_na.png  (TEST=1.0,2.0 for build seconds)"""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera
from nightkit.zraster import zrender
from nightkit import post, look, hd, motion, font
import dragon_taxes as dtx
import final_boss as FB

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
BOSS_H = 2.3; BK = BOSS_H / 1.78
_BOSS = dict(h=BOSS_H, build=1.22, skin=(132, 116, 138), hair=(120, 104, 126), hair_style='bald', eye=(232, 70, 54), brow=(34, 26, 36),
             lip=(84, 56, 76), tunic=(34, 28, 40), tunic2=(26, 22, 32), skirt=0.5, pants=(30, 26, 36), boots=(22, 18, 26),
             belt=(92, 28, 34), buckle=(214, 190, 120), gloves=(40, 32, 46), cloak=(78, 34, 74), cloak_len=1.12, collar=(120, 34, 40))
BOSS_Y = hd.spec(**_BOSS)
BOSS_O = hd.spec(**dict(_BOSS, beard=(220, 218, 214), brow=(210, 206, 200), skin=(150, 138, 152)))          # 300 years later
PLUM = (78, 34, 74); PLUM_D = (58, 24, 56); BLK = (30, 26, 36); PGOLD = (214, 190, 120); HORN = (186, 172, 150); HORN_D = (140, 128, 110)
def boss(P, old=0.0):
    """boss_wanted's HD final boss (2.3 m, plum cloak, horned pale-gold crown); old > 0.5 = white beard + paler skin"""
    SP = BOSS_O if old > 0.5 else BOSS_Y
    Q = hd.human(SP, P); RW = P['_RW']; ch = P['_chest']; RH = P['_RH']; hc = P['_head']; k = BK; bw = SP['build']
    for sd in (1, -1):
        c = ch + RW @ V((sd * 0.2 * bw, 0.07 * k, -0.01))
        Q += hd.ellip(c, RW @ hd.Rz(-sd * 0.3), (0.12 * bw, 0.085, 0.12), 10, 5, PLUM, v1=PI * 0.6, colfn=lambda i, j, cl: PLUM_D if i == 2 else PLUM)
        Q += hd.ellip(c + RW @ V((sd * 0.02, -0.02, 0)), RW @ hd.Rz(-sd * 0.3), (0.125 * bw, 0.03, 0.125), 10, 2, PGOLD, v0=PI * 0.5, v1=PI * 0.62)
        Q += hd.limb(c + RW @ V((sd * 0.04, 0.05, 0)), c + RW @ V((sd * 0.13, 0.2, -0.02)), 0.035, 0.004, HORN_D, n=6, m=1)
    Q += hd.ellip(ch + RW @ V((0, -0.03, 0.04)), RW, (0.19 * bw, 0.19, 0.11 * bw), 12, 6, BLK, keep=lambda c: c[2] > 0.0,
                  colfn=lambda i, j, cl: (52, 44, 58) if (j % 6 == 0) else BLK)
    Q += hd.decal(ch + RW @ V((0, 0.0, 0.11 * bw + 0.045)), RW @ V((0, 0, 1.0)), RW @ V((0, 1.0, 0)), 0.035, 0.05, (220, 40, 46), emit=True, lift=0.004)
    rx, ry, rz = 0.09 * k, 0.116 * k, 0.103 * k
    def L(x, y, z): return hc + RH @ V((x, y, z))
    Q += hd.limb(L(0, 0.062 * k, -0.006 * k), L(0, 0.082 * k, -0.01 * k), rz * 1.0, rz * 0.96, PGOLD, n=16, m=1, ref=RH @ V((0, 0, 1.0)), flat=0.9)
    for a in (-0.9, -0.45, 0.0, 0.45, 0.9):
        p = L(rx * 1.0 * math.sin(a), 0.082 * k, rz * 0.98 * math.cos(a)); Q += hd.limb(p, p + RH @ V((0, 0.035 * k, 0)), 0.012 * k, 0.002, PGOLD, n=4, m=1)
    Q += hd.bx(L(0, 0.072 * k, rz * 1.0), RH, (0.012 * k, 0.012 * k, 0.006), (220, 40, 46), emit=True)
    for sd in (1, -1):
        pts = [L(sd * rx * 0.85, 0.06 * k, -0.01 * k), L(sd * rx * 1.35, 0.1 * k, -0.04 * k), L(sd * rx * 1.6, 0.17 * k, -0.08 * k), L(sd * rx * 1.5, 0.25 * k, -0.11 * k)]
        rr = [0.03 * k, 0.024 * k, 0.016 * k, 0.004]
        for i in range(3): Q += hd.limb(pts[i], pts[i + 1], rr[i], rr[i + 1], HORN if i % 2 == 0 else HORN_D, n=7, m=1)
    P['_horns'] = [L(sd * rx * 1.5, 0.25 * k, -0.11 * k) for sd in (1, -1)]
    return [q for q in Q if q]
KN_Y = dtx.KNIGHT
KN_M = hd.spec(**dict(dtx.KNIGHT, beard=(70, 52, 40)))
KN_O = hd.spec(**dict(dtx.KNIGHT, beard=(214, 212, 208), hair=(200, 198, 194), brow=(200, 198, 194)))
def knight(P, age=0.0):
    """the series knight (dragon_taxes): age 0 young, 0.35+ brown beard, 0.7+ grey beard"""
    SP = KN_O if age >= 0.7 else (KN_M if age >= 0.35 else KN_Y)
    Q = hd.human(SP, P); RW = P['_RW']; ch = P['_chest']; st = (178, 186, 200); dk = (128, 136, 152)
    for sd in (1, -1):
        c = ch + RW @ V((sd * 0.19, 0.075, -0.01))
        Q += hd.ellip(c, RW @ hd.Rz(-sd * 0.35), (0.1, 0.07, 0.1), 10, 5, st, v1=PI * 0.6, colfn=lambda i, j, cl: dk if i == 2 else st)
        kn = P['_' + ('r' if sd > 0 else 'l') + 'knee']; Q += hd.ellip(kn, RW, (0.06, 0.06, 0.065), 8, 4, st)
    Q += hd.ellip(ch + RW @ V((0, -0.02, 0.035)), RW, (0.17, 0.17, 0.1), 12, 6, st, keep=lambda c: c[2] > 0.0, colfn=lambda i, j, cl: dk if (j % 6 == 0) else st)
    Q += dtx.knight_helmet(P)
    return Q

# ======================= props =======================
CUP_W = (232, 226, 214); CUP_B = (60, 110, 170); TEA = (120, 70, 36)
def cup(c, R=None, s=1.0, tea=True):
    R = np.eye(3) if R is None else R; c = V(c, float)
    Q = hd.lathe(tuple(c), R, [(0.028 * s, 0.0), (0.036 * s, 0.012 * s), (0.042 * s, 0.05 * s), (0.044 * s, 0.056 * s)], 9, CUP_W)
    Q += hd.lathe(tuple(c + R @ V((0, 0.03 * s, 0))), R, [(0.043 * s, 0.0), (0.044 * s, 0.008 * s)], 9, CUP_B)
    if tea: Q += hd.poly_decal(tuple(c + R @ V((0, 0.05 * s, 0))), tuple(R @ V((0, 1.0, 0))), tuple(R @ V((0, 0, 1.0))), [(0.04 * s * math.cos(a), 0.04 * s * math.sin(a)) for a in np.linspace(0, 2 * PI, 10)[:-1]], TEA, lift=0.0)
    Q += hd.limb(tuple(c + R @ V((0.042 * s, 0.042 * s, 0))), tuple(c + R @ V((0.062 * s, 0.025 * s, 0))), 0.007 * s, 0.007 * s, CUP_W, n=5, m=1)
    return [q for q in Q if q]
def teapot(c):
    c = V(c, float)
    Q = hd.ellip(tuple(c + V((0, 0.11, 0))), np.eye(3), (0.13, 0.11, 0.13), 10, 6, CUP_W, colfn=lambda i, j, cl: CUP_B if i == 3 else CUP_W)
    Q += hd.ellip(tuple(c + V((0, 0.22, 0))), np.eye(3), (0.05, 0.03, 0.05), 8, 3, CUP_B)
    Q += hd.limb(tuple(c + V((0.0, 0.1, -0.11))), tuple(c + V((0.0, 0.2, -0.22))), 0.03, 0.014, CUP_W, n=6, m=1)
    Q += hd.limb(tuple(c + V((0.0, 0.17, 0.12))), tuple(c + V((0.0, 0.06, 0.13))), 0.012, 0.012, CUP_W, n=5, m=1)
    return [q for q in Q if q]
CANDLES = [(-1.9, 0.4, 14.85), (-1.45, 0.4, 14.75), (1.5, 0.4, 14.8), (1.95, 0.4, 14.9), (-1.1, 0.8, 15.35), (1.2, 0.8, 15.4)]
def candles(t, melt):
    """candles on the dais steps: melt 0..1 shortens them to stubs, wax puddles grow; they flicker faster in the time-lapse"""
    Q = []
    for i, c in enumerate(CANDLES):
        c = V(c, float); h0 = 0.34 + 0.12 * hsh(i, 3); h = max(0.03, h0 * (1 - 0.92 * melt))
        Q += hd.lathe(tuple(c), np.eye(3), [(0.045, 0), (0.045, h), (0.038, h + 0.01)], 7, (230, 222, 200))
        if melt > 0.05: Q += hd.poly_decal(tuple(c + V((0, 0.003, 0))), (0, 1.0, 0), (0, 0, 1.0), [((0.06 + 0.12 * melt) * math.cos(a), (0.05 + 0.1 * melt) * math.sin(a)) for a in np.linspace(0, 2 * PI, 10)[:-1]], (222, 214, 192), lift=0.0)
        f = c + V((0, h + 0.012, 0)); fh = 0.07 * (0.8 + 0.2 * math.sin(t * 13 + i * 2))
        for ang in (0.0, PI / 2):
            dx, dz = 0.02 * math.cos(ang), 0.02 * math.sin(ang)
            Q.append(hd.face([f + V((-dx, 0, -dz)), f + V((dx, 0, dz)), f + V((0.004 * math.sin(t * 9 + i), fh, 0))], (255, 214, 120), emit=True))
    return [q for q in Q if q]
WEB = (196, 198, 206)
def web(c, u, v, size, amt, seed=0):
    """a corner cobweb: radial strands from corner c between directions u and v + sagging rings; amt 0..1 grows it"""
    if amt <= 0.02: return []
    c = V(c, float); u = nz(u); v = nz(v); Q = []; n = 5; R = size * (0.4 + 0.6 * amt)
    dirs = [nz(u * (1 - a) + v * a) for a in np.linspace(0, 1, n)]
    for i, d in enumerate(dirs): Q += hd.limb(tuple(c), tuple(c + d * R * (0.9 + 0.2 * hsh(i, seed))), 0.006, 0.004, WEB, n=4, m=1)
    for r in np.linspace(0.3, 0.95, max(1, int(round(3 * amt)))):
        for i in range(n - 1):
            a = c + dirs[i] * R * r; b = c + dirs[i + 1] * R * r; m_ = (a + b) / 2 - V((0, 0.02 * R, 0))
            Q += hd.limb(tuple(a), tuple(m_), 0.004, 0.004, WEB, n=4, m=1) + hd.limb(tuple(m_), tuple(b), 0.004, 0.004, WEB, n=4, m=1)
    return [q for q in Q if q]
def strand(a, b, amt, sag=0.06):
    if amt <= 0.05: return []
    a = V(a, float); b = V(b, float); m_ = (a + b) / 2 - V((0, sag, 0)); Q = []
    for p, q in ((a, m_), (m_, b)): Q += hd.limb(tuple(p), tuple(q), 0.005, 0.005, WEB, n=4, m=1)
    return [q for q in Q if q]

# =====================================================================================================================
#                                                      TIMELINE
# =====================================================================================================================
from nightkit.audio import Sound, duck_envelope
OUT = 'out'; os.makedirs(OUT, exist_ok=True)
TTS_DIR = os.environ.get('TTS_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tts'))
SCR = json.load(open(os.path.join(TTS_DIR, 'na', 'script.json'), encoding='utf-8'))
KEYS = ['%02d' % i for i in range(0, 9)]
LEAD = {'00': 0.15, '03': 0.3}
GAP = {'00': 0.3, '01': 1.7, '02': 0.45, '03': 1.5, '04': 1.5, '05': 0.95, '06': 1.3, '07': 0.75, '08': 2.1}
def _lines():
    t = 0.0; out = []
    for k in KEYS:
        t += LEAD.get(k, 0.0); out.append((k, round(t, 3))); t += SCR['dur'][k] + GAP[k]
    return out, t
LINES, _T_END = _lines(); T0 = dict(LINES)
def tend(k): return T0[k] + SCR['dur'][k]
def ws(k, i): s_ = SCR['sent'][k]; return T0[k] + s_[min(i, len(s_) - 1)][0]
def we(k, i): s_ = SCR['sent'][k]; return T0[k] + s_[min(i, len(s_) - 1)][1]
# beats
T_CURSOR = 0.6                                       # frame 0: cursor ATTACK -> WAIT
T_RULE = (we('01', 0) + 0.05, tend('01') + 0.3)      # popup HERO MOVES FIRST
PRESS = [tend('01') + 0.3, tend('01') + 0.75, tend('01') + 1.15]       # WAIT, WAIT, WAIT (x1)
T_RAMP = (PRESS[-1] + 0.3, tend('02'))               # x10: 3 -> 100
S2 = T0['02'] - 0.3
T_SIT = (we('03', 0) + 0.05, we('03', 0) + 1.0)      # "Fine." -> he sits on the step
T_OFFER = (ws('03', 1) - 0.25, ws('03', 1) + 0.45)   # "Tea?" -> the cup goes out
T_STEP = (ws('03', 1) + 0.2, tend('03') + 0.6)       # the knight takes one step and the cup
T_TAKE = tend('03') + 0.55
S3 = tend('03') + 1.0                                # TIME-LAPSE starts
T_LAPSE = (S3, T0['05'] - 0.35)
S4 = T_LAPSE[1]
T_9999 = tend('05') + 0.2; T_MAX = T_9999 + 0.45
T_GLITCH = (tend('06') + 0.1, tend('06') + 1.0)
S5 = T_GLITCH[1]                                     # reset: frame 0 again
T_LEAN = (tend('07') + 0.2, T0['08'] + 0.2)          # he glances around, leans in
T_BACK = (tend('08') + 0.3, tend('08') + 0.9)        # back to the frame-0 pose
T_Q = (tend('08') + 0.35, None)
DUR = round(tend('08') + GAP['08'], 3); N = int(round(DUR * FPS))
T_Q = (T_Q[0], DUR)
def fr(x): return int(round(x * FPS))
SEQS = [('s1', 0, fr(S2)), ('s2', fr(S2), fr(S3)), ('s3', fr(S3), fr(S4)), ('s4', fr(S4), fr(S5)), ('s5', fr(S5), N)]
CUTS = [('open', 0.0), ('wait', PRESS[0] - 0.25), ('tap', S2), ('sit', T0['03'] - 0.2), ('lapse', S3), ('close', S4),
        ('max', T_9999 - 0.25), ('reset', S5), ('whisper', T_LEAN[0] + 0.2), ('loop', T_BACK[0])]
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
def lapse(t): return seg01(t, *T_LAPSE)               # 0..1 across the centuries
def centuries(t):
    """age 0..1 of the world: frozen at 1 after the lapse until the reset"""
    if t >= S5 or t < 0: return 0.0
    return sm(lapse(t)) if t < T_LAPSE[1] else 1.0

def turns(t):
    """TURNS WAITED + speed tag"""
    if t < 0 or t >= S5: return 0, ''
    if t < PRESS[0]: return 0, ''
    if t < T_RAMP[0]: return sum(1 for p in PRESS if t >= p), 'x1'
    if t < S3:
        if t < T_RAMP[1]:
            u = seg01(t, *T_RAMP); return int(round(3 * (100 / 3) ** (u ** 1.3))), 'x10'
        return 100 + int((t - T_RAMP[1]) * 9), 'x10'
    if t < T_LAPSE[1]:
        u = lapse(t); c0 = 100 + int((S3 - T_RAMP[1]) * 9)
        return int(round(c0 * (9990 / c0) ** (u ** 0.8))), ('x100' if u < 0.25 else 'x1000')
    if t < T_9999:
        u = seg01(t, T_LAPSE[1], T_9999 - 0.1); return 9990 + int(u * 8.99), 'x1'
    return 9999, 'x1'

# =====================================================================================================================
#                                                      POSES
# =====================================================================================================================
B_STAND = (0.2, 0.4, 14.95); B_SIT = (0.2, 0.4, 14.82); BYAW = PI
K0 = (0.0, 0.0, 12.9); K1 = (0.0, 0.0, 13.55)
MEET = V((-0.1, 1.08, 14.05))                         # where the cup changes hands
POT = (0.95, 0.4, 14.95)
def bl(p, base=B_STAND): return V(base, float) + hd.Ry(BYAW) @ V(p, float)
def wl(w, base): return hd.Ry(BYAW).T @ (V(w, float) - V(base, float))
def boss_frame0(t):
    """the frame-0 pose (also the reset and the loop tail): standing on the step, left fist up, sword pointed at the hero"""
    P = dict(base=B_STAND, yaw=BYAW, eyes='open', mouth='grit', brow=0.9, lean=0.05, cape_sway=0.15 * math.sin(t * 1.3), look=(0.0, -0.2), head=(0.0, -0.08, 0.0))
    P['lh'] = (-0.42, 2.28, 0.34); P['lgrip'] = 0.95; P['lpalm'] = (1.0, 0.0, 0.0)
    P['rh'] = (0.34, 1.42, 0.5); P['rgrip'] = 0.95; P['rpalm'] = (-1.0, 0.0, 0.0)
    P['_sword'] = nz((-0.05, -0.25, 1.0))
    return P
def boss_pose(t):
    if t >= S5 or t < 0:
        P = boss_frame0(t)
        if t >= 0 and talking(t, '07') > 0: P['mouth'] = 'open' if talking(t, '07') > 0.5 else 'grit'
        ln = win(t, T_LEAN[0], T_BACK[1], 0.35) if t >= 0 else 0.0
        if ln > 0:                                                                      # glance left/right, lean down to the knight
            gl = math.sin(seg01(t, T_LEAN[0], T_LEAN[0] + 0.7) * 2 * PI) if t < T_LEAN[0] + 0.7 else 0.0
            P['look'] = (0.9 * gl, -0.5 * ln); P['head'] = (0.25 * gl, -0.08 - 0.35 * ln, 0.0); P['lean'] = 0.05 + 0.45 * ln
            P['lh'] = lerp3(P['lh'], (-0.12, 1.92, 0.42), ln); P['lpalm'] = (0.3, 0.0, 1.0); P['lgrip'] = lerp(0.95, 0.3, ln)    # hand beside the mouth
            P['_sword'] = nz(lerp3((-0.05, -0.25, 1.0), (0.1, -1.0, 0.2), ln)); P['rh'] = lerp3(P['rh'], (0.36, 1.1, 0.3), ln)
            P['brow'] = lerp(0.9, -0.3, ln); P['mouth'] = 'smile' if talking(t, '08') < 0.5 else 'o'; P['eyes'] = 'half' if ln > 0.5 else 'open'
        return P
    if t < T0['01']:
        P = boss_frame0(t); P['mouth'] = 'grit'; return P
    P = boss_frame0(t); P['mouth'] = 'grit' if talking(t, '01') < 0.5 else 'open'
    # 01 "Kneel, mortal!" points down at the floor in front of the knight; "It's your turn. Attack!" palm up, beckons
    kn = win(t, T0['01'], we('01', 0) + 0.15, 0.2)
    if kn > 0: P['lh'] = lerp3(P['lh'], (-0.3, 1.32, 0.62), kn); P['lpalm'] = lerp3((1.0, 0, 0), (0, -1.0, 0.3), kn); P['lgrip'] = lerp(0.95, 0.65, kn)
    bk = win(t, ws('01', 1) - 0.1, S2, 0.25)
    if bk > 0:
        bc = 0.08 * math.sin((t - ws('01', 1)) * 9.0) * (1 if t < tend('01') else 0)
        P['lh'] = lerp3(P['lh'], (-0.36, 1.4 + bc, 0.55), bk); P['lpalm'] = lerp3((1.0, 0, 0), (0.0, 1.0, 0.2), bk); P['lgrip'] = lerp(0.95, 0.2, bk)
    # WAIT presses: leans in, expectant; every press he flinches (ready!), nothing happens
    if t >= PRESS[0] - 0.1:
        P['brow'] = 0.3; P['mouth'] = 'neutral'; P['eyes'] = 'wide'
        for p in PRESS:
            f = win(t, p, p + 0.3, 0.1)
            if f > 0: P['lean'] = 0.05 + 0.12 * f; P['head'] = (0.0, -0.08 + 0.08 * f, 0.0)
    # 02: sword tip down to the floor, left fist on the hip, taps his foot; on the second sentence both arms out
    if t >= S2:
        P['_sword'] = nz((0.0, -1.0, 0.25)); P['rh'] = (0.36, 1.1, 0.3); P['eyes'] = 'half'; P['brow'] = -0.3
        P['lh'] = (-0.38, 1.22, 0.1); P['lpalm'] = (-1.0, 0.0, 0.0); P['lgrip'] = 0.9; P['lpole'] = (-1.0, 0.0, -0.3)
        tap = max(0.0, math.sin((t - S2) * 2 * PI * 2.6)) if t < we('02', 0) + 0.3 else 0.0
        P['rf'] = (0.13, 0.075 + 0.05 * tap, 0.12)
        P['mouth'] = 'open' if talking(t, '02') > 0.5 else 'neutral'
        ar = win(t, ws('02', 1) - 0.1, tend('02') + 0.2, 0.2)
        if ar > 0:
            P['lh'] = lerp3(P['lh'], (-0.62, 1.55, 0.42), ar); P['lpalm'] = lerp3((-1.0, 0, 0), (0.0, 1.0, 0.3), ar); P['lgrip'] = lerp(0.9, 0.15, ar); P.pop('lpole', None)
            P['brow'] = lerp(-0.3, 0.8, ar); P['eyes'] = 'wide'
    # 03 "Fine." -> sits on the step; "Tea?" -> holds a cup out
    if t >= T0['03'] - 0.1:
        sd = sm(seg01(t, *T_SIT)); P['eyes'] = 'half'; P['brow'] = -0.5; P['mouth'] = 'open' if talking(t, '03') > 0.5 else 'neutral'
        P['base'] = lerp3(B_STAND, B_SIT, sd); P['crouch'] = 1.06 * sd; P['lean'] = 0.05 + 0.12 * sd
        for key, sx in (('rf', 0.18), ('lf', -0.18)): P[key] = lerp3((sx * 0.75, 0.075, 0.02), (sx, -0.325, 0.62), sd)
        P['rkpole'] = (0.2, 0.6, 1.0); P['lkpole'] = (-0.2, 0.6, 1.0)
        P['rh'] = lerp3((0.36, 1.1, 0.3), (0.45, 0.58, 0.32), sd); P['_sword'] = nz(lerp3((0.0, -1.0, 0.25), (0.15, -0.35, 1.0), sd))
        P['lh'] = lerp3((-0.38, 1.22, 0.1), (-0.3, 0.62, 0.38), sd); P['lpalm'] = (0.0, -1.0, 0.0); P['lgrip'] = 0.3; P.pop('lpole', None)
        of = sm(seg01(t, *T_OFFER)) * (1 - sm(seg01(t, T_TAKE, T_TAKE + 0.5)))
        if of > 0:
            P.pop('rh', None); P['rh_w'] = tuple(lerp3(tuple(bl((0.3, 0.75, 0.35), B_SIT)), tuple(MEET + V((0.0, 0.0, 0.08))), of)); P['rpalm'] = (0, -1.0, 0); P['rpalm_local'] = False; P['rgrip'] = 0.7
            P['lean'] = 0.17 + 0.25 * of; P['eyes'] = 'open'; P['brow'] = -0.1; P['_sword'] = None
        elif t >= T_TAKE: P['_sword'] = None
    # time-lapse: sips his tea, laughs, tells stories (fast); the beard grows
    if t >= S3:
        age = centuries(t); P['base'] = B_SIT; P['crouch'] = 1.06; P['_sword'] = None; P['lean'] = 0.15 + 0.08 * age
        ph = (t - S3) * (6.0 if t < T_LAPSE[1] else 0.0)
        sip = max(0.0, math.sin(ph)) ** 2
        P['rh'] = lerp3((0.26, 0.6, 0.45), (0.05, 1.0, 0.32), sip); P['rgrip'] = 0.75; P['rpalm'] = (-1.0, 0.0, 0.0)
        laugh = max(0.0, math.sin(ph * 0.7 + 1.0)) if t < T_LAPSE[1] else 0.0
        P['mouth'] = 'smile' if laugh > 0.3 else ('open' if math.sin(ph * 3.3) > 0 and t < T_LAPSE[1] else 'neutral')
        P['head'] = (0.0, 0.25 * laugh - 0.05, 0.0); P['eyes'] = 'half' if laugh > 0.5 else 'open'; P['brow'] = -0.2
        P['lh'] = (-0.3 + 0.15 * math.sin(ph * 1.7), 0.9 + 0.25 * max(0.0, math.sin(ph * 1.3)), 0.45); P['lpalm'] = (0.0, 1.0, 0.3); P['lgrip'] = 0.2
        if t >= T_LAPSE[1]:                                                                     # 05: warm, slow; looks at the knight
            P['rh'] = (0.26, 0.6, 0.45); P['lh'] = (-0.3, 0.68, 0.4); P['lpalm'] = (0.0, -1.0, 0.0); P['lgrip'] = 0.3
            P['eyes'] = 'sad' if t < we('05', 0) else 'half'; P['brow'] = -0.7; P['mouth'] = 'open' if talking(t, '05') > 0.5 else ('soft' if t >= ws('05', 1) else 'neutral')
            P['head'] = (0.0, 0.0, 0.08 if t >= ws('05', 1) else 0.0); P['look'] = (0.0, -0.1)
        if t >= T_9999 - 0.1:                                                                   # the counter: he looks up
            u = sm(seg01(t, T_9999 - 0.1, T_9999 + 0.4)); P['head'] = (0.0, 0.45 * u, 0.0); P['look'] = (0.0, 0.9 * u); P['eyes'] = 'wide'; P['brow'] = -0.9
            P['mouth'] = 'o' if talking(t, '06') < 0.5 else 'open'
    return P
def knight_pose(t):
    P = dict(base=K0, yaw=0.0, eyes='open', mouth='neutral', brow=0.5, lean=0.06, cape_sway=0.15 * math.sin(t * 1.3), head=(0.0, 0.2, 0.0))
    P['rh'] = (0.24, 1.3, 0.42); P['rgrip'] = 0.9; P['rpalm'] = (-1.0, 0, 0.0); P['lh'] = (-0.24, 1.08, 0.18); P['lgrip'] = 0.5
    P['_blade'] = nz((0.05, 0.95, 0.45)); P['_cup'] = False
    if 0 <= t < S5:
        # never moves. On every WAIT press: a tiny nod, a polite smile
        for p in PRESS:
            f = win(t, p, p + 0.3, 0.1)
            if f > 0: P['head'] = (0.0, 0.2 - 0.12 * f, 0.0)
        if t >= PRESS[0]: P['mouth'] = 'smile'; P['brow'] = 0.0
        if t >= S2:                                                                              # sword lowered, tip to the floor
            lo = sm(seg01(t, S2, S2 + 0.6)); P['rh'] = lerp3((0.24, 1.3, 0.42), (0.26, 0.98, 0.3), lo); P['_blade'] = nz(lerp3((0.05, 0.95, 0.45), (0.05, -1.0, 0.42), lo))
        if t >= T_STEP[0]:                                                                       # ONE step forward, takes the cup (left hand)
            u = sm(seg01(t, *T_STEP)); P['base'] = lerp3(K0, K1, u)
            if 0 < u < 1: P['walk'] = u * PI * 1.0; P['stride'] = 0.3
            rc = sm(seg01(t, T_STEP[0] + 0.1, T_TAKE)); hold = sm(seg01(t, T_TAKE + 0.1, T_TAKE + 0.6))
            P.pop('lh', None)
            hold_w = tuple(V(K1) + V((-0.1, 1.2, 0.32)))
            P['lh_w'] = tuple(lerp3(tuple(lerp3(tuple(V(K0) + V((-0.24, 1.08, 0.18))), tuple(MEET + V((0.0, 0.0, -0.08))), rc)), hold_w, hold))
            P['lpalm'] = (0, 1.0, 0); P['lpalm_local'] = False; P['lgrip'] = 0.7; P['_cup'] = rc >= 0.99
            P['head'] = (0.0, 0.25, 0.0); P['mouth'] = 'smile'
        if t >= S3:
            age = centuries(t); P['base'] = K1; P.pop('walk', None)
            P['head'] = (0.0, 0.28 - 0.05 * age, 0.0); P['lean'] = 0.06 + 0.05 * age
            ph = (t - S3) * 6.0 if t < T_LAPSE[1] else 0.0
            P['mouth'] = 'smile' if math.sin(ph * 0.7 + 1.0) > 0.3 else 'neutral'
            if t >= T_LAPSE[1]: P['mouth'] = 'soft'; P['eyes'] = 'open'; P['brow'] = -0.2
            if t >= T_9999 - 0.1: u = sm(seg01(t, T_9999, T_9999 + 0.5)); P['head'] = (0.0, 0.28 + 0.4 * u, 0.0); P['look'] = (0.0, 0.8 * u); P['eyes'] = 'wide'
    return P

# =====================================================================================================================
#                                                      CAMERA
# =====================================================================================================================
O_POS = V((0.95, 1.3, 11.55)); O_TGT = V((0.1, 2.12, 14.9)); O_FOV = 23.0
def cam_shot(t):
    sc = scene(t)
    if sc in ('open', 'reset', 'loop') or t < 0:
        if sc == 'open': u = sm(seg01(t, 0.0, PRESS[0])); return lerp3(O_POS + V((0.0, 0.0, -0.25)), O_POS, u), O_TGT, O_FOV
        if sc == 'reset': return O_POS + V((0.0, 0.0, -0.25)), O_TGT, O_FOV           # = frame 0 exactly (the game restarted)
        u = sm(seg01(t, T_BACK[0], DUR)); return lerp3(O_POS, O_POS + V((0.0, 0.0, -0.25)), u), O_TGT, O_FOV   # loop tail -> frame 0
    idx = [n for n, _ in CUTS].index(sc); a = CUTS[idx][1]; b = CUTS[idx + 1][1] if idx + 1 < len(CUTS) else DUR; u = sm(seg01(t, a, b))
    if sc == 'wait': return lerp3((-3.9, 1.5, 13.0), (-3.7, 1.55, 13.15), u), (0.05, 1.25, 13.9), 50.0
    if sc == 'tap': return lerp3((1.5, 1.35, 12.2), (1.35, 1.4, 12.35), u), (0.1, 1.55, 14.9), 42.0
    if sc == 'sit': return lerp3((-2.8, 1.2, 13.3), (-2.65, 1.2, 13.45), u), (0.0, 0.95, 14.1), 46.0
    if sc == 'lapse': return lerp3((-2.75, 1.15, 13.05), (-2.25, 1.12, 13.35), u), (0.05, 1.0, 14.2), 48.0
    if sc == 'close': return lerp3((0.62, 1.32, 13.72), (0.58, 1.33, 13.82), u), (0.15, 1.38, 14.75), 34.0
    if sc == 'max': return lerp3((0.95, 0.95, 13.25), (0.9, 0.92, 13.35), u), (0.1, 1.62, 14.75), 44.0
    if sc == 'whisper': return lerp3((0.6, 1.8, 12.75), (0.55, 1.82, 12.95), u), (0.12, 2.15, 14.6), 34.0
    return O_POS, O_TGT, O_FOV

# =====================================================================================================================
#                                                      RENDER
# =====================================================================================================================
_PC = {}
def poses(t):
    if t not in _PC:
        if len(_PC) > 6: _PC.clear()
        BP = boss_pose(t); age = centuries(t); QB = boss(BP, old=age); KP = knight_pose(t); QK = knight(KP, age); _PC[t] = (BP, QB, KP, QK)
    return _PC[t]
def world(t):
    BP, QB, KP, QK = poses(t); age = centuries(t)
    tf = t if not (S3 <= t < T_LAPSE[1]) else S3 + (t - S3) * 7.0                        # torches flicker fast in the time-lapse
    layers = [FB.ARENA, FB.gate_doors(0.0), FB.torches(tf), QB, QK, candles(tf, age)]
    # boss sword: in his fist, or lying on the step once he sits
    if BP.get('_sword') is not None:
        g = grip_pt(BP, 'r', 0.07, 0.02); d = hd.Ry(BYAW) @ V(BP['_sword'])
        layers.append(hd.sword(tuple(g), tuple(nz(d)), BP['_rpalm'], col=(150, 150, 166), grip=(40, 30, 40), guard=PGOLD, length=1.05))
    elif t >= T0['03']:
        layers.append(hd.sword((1.55, 0.43, 15.1), (-1.0, 0.0, 0.08), (0, 1.0, 0), col=(150, 150, 166), grip=(40, 30, 40), guard=PGOLD, length=1.05))
    # knight sword (right hand)
    g = grip_pt(KP, 'r', 0.06, 0.0); d = hd.Ry(KP.get('yaw', 0.0)) @ V(KP['_blade'])
    layers.append(hd.sword(tuple(g), tuple(nz(d)), KP['_rpalm'], length=0.85)); ktip = g + nz(d) * 0.85
    # tea: the pot from "Tea?" on; the cup in the boss's hand -> the knight's; the boss's own cup in the time-lapse
    if T0['03'] <= t < S5:
        layers.append(teapot(POT))
        if t < T_TAKE:
            if t >= T_OFFER[0]: layers.append(cup(grip_pt(BP, 'r', 0.05, 0.0) - V((0, 0.03, 0)), s=1.3))
        else:
            layers.append(cup(grip_pt(KP, 'l', 0.05, 0.0) - V((0, 0.03, 0)), s=1.3))
            if t >= S3: layers.append(cup(grip_pt(BP, 'r', 0.05, 0.0) - V((0, 0.03, 0)), s=1.3))
    # cobwebs grow in the time-lapse (and stay until the reset)
    if age > 0:
        hc = V(KP['_head']); ch = V(KP['_chest'])
        layers.append(web(hc + V((0.0, 0.12, -0.05)), (0.25, -0.2, 0.0), (0.05, -0.35, 0.1), 0.35, seg01(age, 0.2, 0.7), 1))
        layers.append(strand(ktip, ktip + V((0.25, 0.0, 0.1)), seg01(age, 0.3, 0.6), 0.03))
        layers.append(strand(ch + V((0.2, 0.05, 0)), g + V((0.02, 0.0, 0.0)), seg01(age, 0.4, 0.8), 0.05))
        layers.append(web(V((-1.6, 0.8, 15.2)), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), 0.5, seg01(age, 0.1, 0.5), 2))
        layers.append(web(V((-1.0, 4.6, 17.0)), (1.0, -0.4, 0.0), (0.2, -1.0, 0.0), 0.8, seg01(age, 0.15, 0.6), 3))
        layers.append(web(V((1.0, 4.6, 17.0)), (-1.0, -0.4, 0.0), (-0.2, -1.0, 0.0), 0.8, seg01(age, 0.3, 0.8), 4))
        if '_horns' in BP: layers.append(strand(BP['_horns'][0], BP['_horns'][1], seg01(age, 0.5, 0.9), 0.06))
    L = FB.torch_lights(tf, dim=0.45)
    L.append(((0.0, 4.8, 12.0), (255, 46, 36), 0.55))                                        # red boss light
    L.append(((-3.2, 3.0, 10.5), (180, 186, 220), 0.8))                                       # cool fill
    L.append(((2.5, 3.5, 16.5), (150, 90, 170), 0.75))                                        # plum rim
    if scene(t) == 'whisper': L.append(((0.5, 1.9, 13.2), (255, 200, 160), 0.9))                  # light his face for the whisper
    if T0['03'] <= t < S5:
        L.append(((0.0, 1.2, 14.6), (255, 180, 100), 0.9 * sm(seg01(t, T0['03'], T0['03'] + 1.0))))   # candles warm the tea scene
    return layers, L
def frame_low(t):
    pos, tgt, fov = cam_shot(t); cam = Camera.look(tuple(pos), tuple(tgt))
    layers, L = world(t)
    R = Renderer(W, H, fog=(10, 6, 10))
    img, vi, zb = zrender(R, cam, layers, L, fov=fov, fog_start=9, fog_end=30, ambient=0.26, return_z=True)
    a = look.outline(np.asarray(img).astype(np.float32), zb)
    a = np.clip((a * np.array([1.0, 0.98, 1.05]) - 80) * 1.18 + 84, 0, 255)
    if 0 <= t < S5 and centuries(t) > 0:                                                      # warm, dusty sepia as the years pass
        e = 0.35 * centuries(t); lum = a.mean(axis=2, keepdims=True); a = a * (1 - e) + lum * np.array([1.08, 0.98, 0.82]) * e
    return post.ps1(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), levels=6), vi

# ======================= overlays (1080 x 1920) =======================
def tw(s, sc): return font.width(s, sc)
def ctext(d, s, y, sc, col, o=4, x=None):
    x = int(540 - tw(s, sc) / 2) if x is None else x
    look.draw_cells(d, look.text_cells(s, x, y, sc, col), o)
TX = dict(boss='SON BOSS' if TRL else 'FINAL BOSS', turns='BEKLENEN TUR' if TRL else 'TURNS WAITED',
          menu=(('SALDIR', 'BÜYÜ'), ('EŞYA', 'BEKLE')) if TRL else (('ATTACK', 'MAGIC'), ('ITEM', 'WAIT')),
          rule=('KAHRAMAN', 'ÖNCE OYNAR') if TRL else ('HERO MOVES', 'FIRST'),
          cov=('FINAL BOSS\'A HİÇ', 'SALDIRMASAN?') if TRL else ('WHAT IF YOU NEVER', 'ATTACK THE BOSS?'),
          q=('9.999 TUR', 'BEKLER MİYDİN?') if TRL else ('WOULD YOU WAIT', '9,999 TURNS?'),
          err=('TUR SINIRI', 'AŞILDI') if TRL else ('TURN LIMIT', 'EXCEEDED'), maxs='MAX')
for _s in [TX['boss'], TX['turns'], *TX['rule'], *TX['cov'], *TX['q'], *TX['err'], *sum(TX['menu'], ())]: font.check(_s)
GLD = (255, 214, 96); WHT = (246, 242, 230); RED = (230, 56, 50)
def fmt(n): return f'{n:,}'.replace(',', '.') if TRL else f'{n:,}'
def hud(d, t):
    """top: FINAL BOSS + full red bar (it never moves), TURNS WAITED counter + speed tag (kept above y 260: the like toast lives at 280+)"""
    ctext(d, TX['boss'], 54, 6, (255, 226, 190), x=64)
    x0, x1, y0, y1 = 64, 1016, 112, 146
    d.rectangle([x0 - 8, y0 - 8, x1 + 8, y1 + 8], fill=(0, 0, 0)); d.rectangle([x0, y0, x1, y1], fill=(214, 40, 44)); d.rectangle([x0, y0, x1, y0 + 8], fill=(255, 150, 140))
    n, tag = turns(t); s = f"{TX['turns']}: "
    big = t >= T_9999 and t < S5
    ctext(d, s, 186, 7, WHT, o=5, x=64); xn = 64 + tw(s, 7)
    if t >= T_MAX and t < S5:
        if int(t * 8) % 2 == 0: ctext(d, TX['maxs'], 176, 9, RED, o=5, x=xn)
    else:
        ctext(d, fmt(n), 176, 9, GLD if not big else (255, 255, 255), o=5, x=xn)
    if tag and t < T_MAX:
        tg = ('HIZ ' if TRL else 'SPEED ') + tag.upper(); ctext(d, tg, 250, 4, (255, 110, 90) if tag != 'x1' else (180, 176, 170), o=4, x=int(1016 - tw(tg, 5)))
def menu(d, t):
    """the battle menu (2 x 2): the cursor jumps ATTACK -> WAIT in frame 0; WAIT flashes on every press"""
    if t >= S2 and t < S5: return
    if t >= S5 and t >= T_LEAN[0] and t < T_BACK[1]: return
    x0, y0, cw, ch = 150, 1180, 390, 92
    d.rectangle([x0 - 10, y0 - 10, x0 + 2 * cw + 10, y0 + 2 * ch + 10], fill=(214, 190, 120)); d.rectangle([x0, y0, x0 + 2 * cw, y0 + 2 * ch], fill=(16, 14, 34))
    tl = t - S5 if t >= S5 else t
    cur = (0, 0) if tl < T_CURSOR else (1, 1)
    flash = any(0 <= t - p < 0.18 for p in PRESS) or (T_RAMP[0] <= t < T_RAMP[1] and int(t * 10) % 2 == 0)
    for r in range(2):
        for c in range(2):
            s = TX['menu'][r][c]; x = x0 + c * cw + 70; y = y0 + r * ch + 26; on = (r, c) == cur
            col = (255, 255, 255) if on else (170, 166, 190)
            if on and flash and (r, c) == (1, 1): d.rectangle([x0 + c * cw + 8, y0 + r * ch + 8, x0 + (c + 1) * cw - 8, y0 + (r + 1) * ch - 8], fill=(80, 70, 160))
            ctext(d, s, y, 6, col, x=x)
            if on:
                cx, cy = x - 46, y + 4
                d.polygon([(cx - 3, cy - 3), (cx + 27, cy + 21), (cx - 3, cy + 45)], fill=(0, 0, 0)); d.polygon([(cx, cy), (cx + 24, cy + 21), (cx, cy + 42)], fill=GLD)
def popups(d, t):
    if T_RULE[0] <= t < T_RULE[1]:
        pop = sm(seg01(t, T_RULE[0], T_RULE[0] + 0.12)); sc = 9 if pop >= 1 else 7
        y = 430; w = max(tw(s, sc) for s in TX['rule'])
        d.rectangle([540 - w / 2 - 36, y - 26, 540 + w / 2 + 36, y + 2 * 8 * sc + 40], fill=(14, 12, 26)); d.rectangle([540 - w / 2 - 36, y - 26, 540 + w / 2 + 36, y + 2 * 8 * sc + 40], outline=GLD, width=6)
        ctext(d, TX['rule'][0], y, sc, WHT, o=4); ctext(d, TX['rule'][1], y + 8 * sc + 14, sc, GLD, o=4)
def cover(d, t):
    if not (0 <= t < T0['01'] + 0.5): return
    sc1, sc2 = 9, 11; y = 880
    w = max(tw(TX['cov'][0], sc1), tw(TX['cov'][1], sc2))
    d.rectangle([540 - w / 2 - 30, y + 8 * sc1 + 8, 540 + w / 2 + 30, y + 8 * sc1 + 8 * sc2 + 46], fill=(110, 16, 24))
    ctext(d, TX['cov'][0], y, sc1, WHT, o=6); ctext(d, TX['cov'][1], y + 8 * sc1 + 26, sc2, (255, 222, 40), o=6)
def question(d, t):
    if not (T_Q[0] <= t): return
    pop = sm(seg01(t, T_Q[0], T_Q[0] + 0.15)); sc1, sc2 = (9, 12) if pop >= 1 else (7, 10); y = 860
    w = max(tw(TX['q'][0], sc1), tw(TX['q'][1], sc2))
    d.rectangle([540 - w / 2 - 34, y - 26, 540 + w / 2 + 34, y + 8 * sc1 + 8 * sc2 + 56], fill=(14, 12, 26)); d.rectangle([540 - w / 2 - 34, y - 26, 540 + w / 2 + 34, y + 8 * sc1 + 8 * sc2 + 56], outline=GLD, width=6)
    ctext(d, TX['q'][0], y, sc1, WHT, o=5); ctext(d, TX['q'][1], y + 8 * sc1 + 26, sc2, GLD, o=6)
def glitch(arr, t):
    """counter overflow: torn rows, RGB split, blocks, the error box, then a white pop into the reset"""
    u = seg01(t, *T_GLITCH); rng = np.random.default_rng(int(t * FPS) + 7); a = arr.copy(); h = a.shape[0]
    k = 4 + int(14 * u)
    for _ in range(k):
        y0 = int(rng.integers(0, h - 40)); hh = int(rng.integers(10, 120)); sh = int(rng.integers(-180, 180) * (0.3 + u))
        a[y0:y0 + hh] = np.roll(a[y0:y0 + hh], sh, axis=1)
    a[..., 0] = np.roll(a[..., 0], int(12 + 30 * u), axis=1); a[..., 2] = np.roll(a[..., 2], -int(12 + 30 * u), axis=1)
    for _ in range(int(6 * u)):
        x0 = int(rng.integers(0, 1000)); y0 = int(rng.integers(0, 1850)); a[y0:y0 + int(rng.integers(20, 90)), x0:x0 + int(rng.integers(40, 260))] = rng.integers(0, 255, 3)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    if u > 0.15:
        y = 800; w = max(tw(s, 10) for s in TX['err'])
        d.rectangle([540 - w / 2 - 40, y - 30, 540 + w / 2 + 40, y + 8 * 10 * 2 + 50], fill=(20, 0, 0)); d.rectangle([540 - w / 2 - 40, y - 30, 540 + w / 2 + 40, y + 8 * 10 * 2 + 50], outline=RED, width=6)
        ctext(d, TX['err'][0], y, 10, RED, o=4); ctext(d, TX['err'][1], y + 90, 10, WHT, o=4)
    a = np.asarray(im).astype(np.float32)
    wf = sm(seg01(t, T_GLITCH[1] - 0.12, T_GLITCH[1]))
    return a * (1 - wf) + 255 * wf
COL = {'N': (242, 238, 226), 'B': (255, 150, 140)}
def _sub_scr():
    if not TRL: return SCR
    import importlib.util as _iu
    sp_ = _iu.spec_from_file_location('na_tts', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'tts', 'na.py'))
    m_ = _iu.module_from_spec(sp_); sp_.loader.exec_module(m_); TRS = m_.TR_SUB
    out = dict(SCR); sent = {}
    for k, v in SCR['sent'].items():
        if len(v) == len(TRS[k]): sent[k] = [[a, b, tx] for (a, b, _), tx in zip(v, TRS[k])]
        else: sent[k] = [[v[0][0], v[-1][1], ' '.join(TRS[k])]]
    out['sent'] = sent
    return out
SUBS = look.Subtitles(_sub_scr(), [x for x in LINES if x[0] != '00'], W, H, S, COL, title_key='none', n=17,
                      hil=({'BEKLE', 'ÇAY?', 'KALDIN.', 'YİNE'} if TRL else {'TURN.', 'TEA?', 'STAYED.', 'AGAIN.', 'AGAIN?', 'MOVE'}))
from nightkit import cta
CTA = cta.Achievement(t0=T_LAPSE[0] + 0.62 * (T_LAPSE[1] - T_LAPSE[0]) - F(0.75), lang=SUB_LANG, dur=F(1.5))      # Enes: 1.5 s on screen
def frame_final(t):
    if t >= DUR: t = t - DUR
    img, vi = frame_low(t); arr = post.upscale(img, S)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    hud(d, t); menu(d, t); popups(d, t); cover(d, t); question(d, t)
    arr = np.asarray(im).astype(np.float32)
    arr = SUBS.apply(arr, t); arr = CTA.apply(arr, t)
    if T_GLITCH[0] <= t < T_GLITCH[1]: arr = glitch(arr, t)
    if S5 <= t < S5 + 0.15: arr = arr + (255 - arr) * (1 - seg01(t, S5, S5 + 0.15))                # white pop -> reset
    return arr

ASSET = os.environ.get('ASSET')
if ASSET and __name__ == '__main__':
    flo = hd.bx((0, -0.05, 0), np.eye(3), (12, 0.05, 12), (70, 64, 58)); ims = []
    Q = boss(dict(base=(0.6, 0, 0), yaw=0.0), old=1.0) + knight(dict(base=(-0.6, 0, 0), yaw=0.0), 0.8) + cup((0.0, 0.8, 0.3), s=1.3) + teapot((0.0, 0.0, 0.6))
    Q += web(V((0.0, 0.0, 0.0)), (1, 0.3, 0), (0, 1, 0), 0.6, 1.0)
    ims.append(dtx.shot([flo, Q], (0.0, 1.4, 4.5), (0.0, 1.1, 0), 40))
    ims.append(dtx.shot([flo, Q], (0.0, 0.95, 1.2), (0.0, 0.5, 0), 40))
    out = Image.new('RGB', (W * S * len(ims) // 2, H * S // 2))
    for i, im in enumerate(ims): out.paste(im.resize((W * S // 2, H * S // 2), Image.NEAREST), (i * W * S // 2, 0))
    out.save('test_na_asset.png'); print('written'); sys.exit()

TEST = os.environ.get('TEST')
if TEST and __name__ == '__main__':
    if TEST == 'seq': ts = sorted(set([round(a + (b - a) * f, 2) for i, (n_, a) in enumerate(CUTS) for b in [CUTS[i + 1][1] if i + 1 < len(CUTS) else DUR] for f in (0.1, 0.5, 0.9)]))
    else: ts = [float(x) for x in TEST.split(',')]
    tw_ = int(os.environ.get('TW', '200')); th = tw_ * 16 // 9
    ims = [Image.fromarray(np.clip(frame_final(x), 0, 255).astype(np.uint8)) for x in ts]
    if os.environ.get('SZ') == 'full':
        for x, im in zip(ts, ims): im.save(f'test_na_{x:.2f}.png')
    ims = [im.resize((tw_, th), Image.LANCZOS) for im in ims]
    per = int(os.environ.get('PER', '9')); rows = (len(ims) + per - 1) // per; shp = Image.new('RGB', (min(per, len(ims)) * (tw_ + 2), rows * (th + 18)), (30, 30, 30))
    dd = ImageDraw.Draw(shp)
    for i, (im, x) in enumerate(zip(ims, ts)): shp.paste(im, ((i % per) * (tw_ + 2), (i // per) * (th + 18))); dd.text(((i % per) * (tw_ + 2) + 4, (i // per) * (th + 18) + th + 3), f'{x:.2f} {x / 1.2:.1f}f {scene(x)}', fill=(255, 255, 0))
    shp.save(os.environ.get('TEST_OUT', 'test_na.png')); print('test written', DUR, round(DUR / 1.2, 2), SEQS); sys.exit()

QA = dict(fps=FPS, dur=DUR, W=W, frame=lambda t: Image.fromarray(np.clip(frame_final(t), 0, 255).astype(np.uint8)).resize((W, H), Image.BOX), chars={},
          geom=lambda t, name, st, V_: [], camera=lambda t: cam_shot(t)[0], min_cam_dist=0.3, camera_ok=lambda p: True, allow_jump=[], weapon_events=[],
          scenes=[dict(id=nm, t0=a, t1=(CUTS[i + 1][1] if i + 1 < len(CUTS) else DUR), action=nm) for i, (nm, a) in enumerate(CUTS)],
          texts=lambda: [('hud', TX['cov'][0], 9), ('hud', TX['cov'][1], 11)])

# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as _sf
    s = Sound(DUR, loop=False, seed=53); sr = s.sr; n = s.n; t = s.t
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
    def click(t0, v=0.02): tone(t0, 96, 0.05, v, dec=40); tone(t0 + 0.04, 103, 0.06, v * 0.8, dec=40)
    def mask(a, b, r=0.15): return np.clip(np.minimum((t - a) / r, (b - t) / r), 0, 1)
    live = 1 - mask(T_GLITCH[0], S5 + 0.02, 0.02)
    # bed: big hall, torches crackling, low drone
    BED += s.filt(s.rng.normal(0, 1, n), lo=40, hi=160) * 0.018 * live
    BED += s.filt(s.rng.normal(0, 1, n), lo=900, hi=5000) * 0.004 * (0.6 + 0.4 * np.abs(np.sin(t * 7.3))) * live
    # battle music: driving low ostinato (frame 0 -> the waiting) that runs down like a tape stop at "Fine."; back at the reset (loop)
    def battle(a, b, stop=None):
        bt = 60 / 150.0; x = a; k = 0; bass = [38, 38, 41, 38, 43, 41, 38, 36]
        while x < b:
            rate = 1.0
            if stop is not None and x > stop: rate = max(0.3, 1 - (x - stop) / 1.2)
            thud(x, 52 * rate, 0.11, 0.25, buf=MUS)
            tone(x, bass[k % 8] + 12 * math.log2(rate), bt * 0.9, 0.035, dec=5, harm=(1.0, 0.5, 0.33, 0.25), buf=MUS)
            if k % 2 == 1: nb(x, 0.08, 2000, 8000, 0.02, 300 + k, 0.6, buf=MUS)
            if k % 4 == 0: [tone(x, m + 12 * math.log2(rate), bt * 1.8, 0.012, dec=2.0, harm=(1.0, 0.4), buf=MUS) for m in (62, 65, 69)]
            x += bt / rate; k += 1
    battle(0.0, we('03', 0) + 1.0, stop=we('03', 0) - 0.1)
    battle(S5, DUR + 0.5)
    # hook hit + roar on frame 0 and on the reset (identical: loop)
    for t0 in (0.02, S5):
        thud(t0, 44, 0.22, 0.7); tt = s.T(1.1); put(FX, s.filt_short(s.noise(1.1, 9), lo=60, hi=500) * np.sin(np.pi * tt / 1.1) * (1 + 0.6 * np.sin(2 * np.pi * 23 * tt)), t0 + 0.05, 0.07)
    click(T_CURSOR, 0.025); click(S5 + T_CURSOR, 0.025)
    tone(T_RULE[0], 84, 0.15, 0.02, dec=12); tone(T_RULE[0] + 0.1, 88, 0.2, 0.02, dec=10)
    # WAIT presses: a menu click + a little "nothing happens" boop
    for p in PRESS: click(p, 0.03); tone(p + 0.12, 60, 0.18, 0.02, dec=10, harm=(1.0, 0.3))
    # counter: ticks speed up into a whir
    def ticks(a, b, r0, r1, v):
        x = a
        while x < b:
            u = (x - a) / max(1e-6, b - a); r = r0 * (r1 / r0) ** u; tone(x, 100, 0.02, v, dec=80); x += 1.0 / r
    ticks(T_RAMP[0], T_RAMP[1], 6, 28, 0.008)
    ticks(S3, T_LAPSE[1], 18, 40, 0.005)
    tt = s.T(T_LAPSE[1] - S3); put(FX, np.sin(2 * np.pi * (300 + 600 * tt / tt[-1]) * tt) * 0.3 * np.sin(np.pi * tt / tt[-1]), S3, 0.012)   # whir
    for k in range(9): tone(T_LAPSE[1] + 0.2 + k * (T_9999 - 0.3 - T_LAPSE[1]) / 9, 100, 0.03, 0.01, dec=60)
    # foot taps (02), the sit (cloth + thud), tea pour, the cup clink
    x = S2
    while x < we('02', 0) + 0.3: thud(x + 0.05, 90, 0.04, 0.1); x += 1 / 2.6
    nb(T_SIT[0] + 0.1, 0.6, 200, 1500, 0.03, 40); thud(T_SIT[1] - 0.2, 55, 0.08, 0.3)
    tt = s.T(0.9); put(FX, s.filt_short(s.noise(0.9, 41), lo=600, hi=3000) * np.sin(np.pi * tt / 0.9) * (1 + 0.4 * np.sin(2 * np.pi * 37 * tt)), T_OFFER[0] - 0.9, 0.035)
    tone(T_TAKE, 98, 0.15, 0.025, dec=25, harm=(1.0, 0.6)); tone(T_TAKE + 0.01, 105, 0.12, 0.012, dec=30)
    # time-lapse: a fast clock + a warm music box that slows into 05; silence before "Oh no"
    x = S3
    while x < T_LAPSE[1]: tone(x, 93, 0.03, 0.006, dec=60); x += 0.11
    mb = [72, 76, 79, 84, 79, 76, 74, 77, 81, 79, 77, 74, 72, 76, 79, 83, 84]
    x = S3 + 0.2; k = 0
    while x < T_9999 - 0.2:
        tone(x, mb[k % len(mb)], 1.0, 0.014, dec=3.0, harm=(1.0, 0.0, 0.3), buf=MUS); x += 0.36 if x < T_LAPSE[1] else 0.62; k += 1
    # 9,999 -> MAX: an error beep; then the overflow crunch and a white pop
    tone(T_9999, 88, 0.12, 0.02, dec=10)
    for k in range(3): tone(T_MAX + 0.18 * k, 70, 0.14, 0.03, dec=6, harm=(1.0, 0.0, 0.5))
    nb(T_GLITCH[0], T_GLITCH[1] - T_GLITCH[0], 200, 9000, 0.09, 77, 0.3)
    for k in range(6): tone(T_GLITCH[0] + 0.12 * k, 40 + 11 * (k % 3), 0.1, 0.04, dec=8, harm=(1.0, 0.7, 0.5))
    nb(S5 - 0.12, 0.2, 2000, 12000, 0.06, 78, 0.5)
    # the whisper: the battle music ducks while he leans in
    MUS *= (1 - 0.65 * mask(T_LEAN[0], T_BACK[0] + 0.2, 0.25))
    tone(T_Q[0], 84, 0.2, 0.02, dec=8); tone(T_Q[0] + 0.12, 91, 0.3, 0.02, dec=6)
    if CTA.on: put(FX, cta.chime(sr), CTA.t0, 1.0)
    # voice
    NB = np.zeros(n); wins = []
    for k_, t0 in LINES:
        f_ = os.path.join(TTS_DIR, 'na', f'{k_}.wav')
        if not os.path.exists(f_): continue
        a, ar = _sf.read(f_); a = a if a.ndim == 1 else a.mean(1)
        a = np.interp(np.arange(int(len(a) * sr / ar)) / sr, np.arange(len(a)) / ar, a); act = np.abs(a) > 0.02 * np.abs(a).max()
        g_ = 0.7 if k_ == '08' else 1.0                                                     # the whisper sits a bit lower
        a = a * (0.12 * g_ / np.sqrt((a[act] ** 2).mean())); put(NB, a, t0); wins.append((t0, t0 + len(a) / sr))
    gd = duck_envelope(n, sr, wins, -8.0, 0.05, 0.25) if wins else np.ones(n)
    bed = BED * gd + MUS * (0.55 + 0.45 * gd); fx = FX * (0.6 + 0.4 * gd)
    L = bed + fx; R_ = np.roll(bed, 700) + np.roll(fx, 200)
    pk = max(np.abs(L).max(), np.abs(R_).max()); gv = (pk * 1.6 / np.abs(NB).max()) if np.abs(NB).max() > 0 else 0.0
    s.L = L + NB * gv; s.R = R_ + NB * gv; s.reverb(0.2, length=2.0, decay=3.0)
    fi = np.clip(t / 0.008, 0, 1); s.L = s.L * fi; s.R = s.R * fi
    return s.save(path, peak=0.9)
if __name__ == '__main__' and os.environ.get('PART') == 'audio':
    print(build_audio(os.path.join(OUT, os.environ.get('AUDIO_NAME', 'never_attack.wav')))); sys.exit()
if __name__ == '__main__' and os.environ.get('PART'):
    a, b = map(int, os.environ['PART'].split(':'))
    import subprocess
    p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W * S}x{H * S}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', os.path.join(OUT, f"{os.environ.get('PART_PREFIX', 'na')}_{a:05d}.mp4")], stdin=subprocess.PIPE)
    vhs = post.VHS(W * S, H * S, S, grade='none', chroma=0, scan_dark=1.0, vignette=0.45, grain=1.2, band_period=1e9)
    for f in range(a, min(b, N)): p.stdin.write(vhs(frame_final(f / FPS), f, f / FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done', a, b); sys.exit()
