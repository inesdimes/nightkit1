"""WHY DOES THE SAVE POINT KEEPER COUNT YOUR DEATHS? (Insert Disc 2, 26 Nov 2026) ~33.5 s final (x1.2 after), nightkit HD, 9:16.
Brief: briefs/SAVE_POINT_FULL_BRIEF.txt (Claude draft, Enes approved 26 Nov). Enes: the cover text sits in the MIDDLE of the frame,
next to the action, not at the top.
Reuses: forget_potion's camp set + fire + HD adventurer (ADV). New: the keeper (old, grey beard, green hood), ladle with notches
(side A fresh / side B old + faded), knife, bowl, bedroll, rusty sword, far gate with a red glow.

Stills: TEST=0,0.5,1.0 python examples/save_point.py -> test_sp.png"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera
from nightkit.zraster import zrender
from nightkit import post, look, hd, motion, font
import forget_potion as fp

W, H, S = 270, 480, 4
PI = math.pi; V = np.array; FPS = 24
sm = motion.smooth
seg01, win, lerp, lerp3, hsh, ang_to = fp.seg01, fp.win, fp.lerp, fp.lerp3, fp.hsh, fp.ang_to
SUB_LANG = os.environ.get('SUB_LANG', 'en'); TRL = SUB_LANG == 'tr'
def F(x): return round(x * 1.2, 4)                  # final seconds -> build seconds (planned; warped to the real takes later)

# ======================= cast =======================
ADV = fp.ADV
KEEPER = hd.spec(h=1.7, build=1.0, skin=(204, 160, 128), hair=(132, 128, 124), hair_style='short', beard=(150, 146, 140),
                 eye=(70, 76, 84), brow=(170, 166, 160), tunic=(92, 80, 62), tunic2=(74, 64, 50), skirt=0.3, pants=(70, 60, 50),
                 boots=(56, 42, 32), belt=(54, 38, 26), cloak=(46, 74, 52), cloak_len=1.0, hood=True)

# ======================= set: camp + new props =======================
FIRE = fp.FIRE                                       # (0.95, 0, 2.55)
HERO = (0.5, 0.0, 1.85); HERO_YAW = PI - 0.05        # foreground, on the bedroll in front of the fire, facing the lens
KEEP = (1.3, 0.0, 3.0); KEEP_YAW = ang_to(KEEP, HERO) + 0.2
LOG = (1.35, 0.0, 3.2)
WOOD = (150, 108, 66); WOOD_D = (104, 72, 44); NOTCH_A = (232, 206, 160); NOTCH_B = (70, 54, 40)

def bedroll():
    c = V(HERO) + V((0.0, 0.0, 0.25))
    Q = hd.bx(tuple(c + V((0, 0.03, 0))), hd.Ry(HERO_YAW), (0.42, 0.03, 1.0), (122, 52, 46))
    Q += hd.limb(tuple(c + hd.Ry(HERO_YAW) @ V((-0.38, 0.09, -0.8))), tuple(c + hd.Ry(HERO_YAW) @ V((0.38, 0.09, -0.8))), 0.09, 0.09, (140, 64, 54), n=8, m=1)
    return Q
def keeper_log():
    return hd.limb((LOG[0] - 0.7, 0.2, LOG[2] + 0.25), (LOG[0] + 0.55, 0.21, LOG[2] - 0.2), 0.2, 0.19, (88, 64, 44), n=10, m=3)
def rusty_sword():
    p = V(KEEP) + V((0.45, 0.0, 0.75))
    return hd.sword(tuple(p + V((0.03, 0.95, 0.0))), (0.06, -1.0, 0.05), (1.0, 0, 0), col=(132, 96, 70), grip=(60, 44, 34), guard=(110, 84, 60), length=0.85)
def far_gate():
    Q = []; z = 15.0; x = -1.6
    Q.append(hd.face([(x - 2.2, 0, z), (x + 2.2, 0, z), (x + 2.2, 3.6, z), (x - 2.2, 3.6, z)], (26, 22, 30)))
    for i in range(5): Q.append(hd.face([(x - 2.2 + i * 1.0, 3.6, z), (x - 1.7 + i * 1.0, 3.6, z), (x - 1.7 + i * 1.0, 4.1, z), (x - 2.2 + i * 1.0, 4.1, z)], (26, 22, 30)))
    Q.append(hd.face([(x - 0.7, 0, z - 0.02), (x + 0.7, 0, z - 0.02), (x + 0.7, 1.9, z - 0.02), (x, 2.4, z - 0.02), (x - 0.7, 1.9, z - 0.02)], (150, 32, 26), emit=True))
    return [q for q in Q if q]
_SET = []
def set_faces():
    if not _SET: _SET.append(fp.camp_set() + bedroll() + keeper_log() + rusty_sword())
    return _SET[0]

# ---- the ladle (polish pass 26 Nov): a real wooden ladle = short handle + a deep round bowl at the end.
# The keeper holds the handle end; the notches are tally marks on the handle's top face (side A), the back is covered (side B).
HANDLE = 0.36; BOWL_R = 0.085; BOWL_D = 0.07; GRIP_BACK = 0.07        # handle runs from hold - 0.07 to hold + 0.29
NA_OLD = 14                                                          # side A: earlier tally marks already cut
def slot_u(i): return 0.035 + (i // 5) * 0.066 + (i % 5) * 0.011       # tally groups of five along the handle (from the hold point)
GROOVE = (78, 50, 30); LIP = (240, 214, 168); GROOVE_B = (98, 80, 62); LIP_B = (150, 124, 96)
def ladle_axes(d, side_up, flip=0.0):
    d = hd.nz(V(d, float)); n0 = hd.nz(V(side_up, float) - d * np.dot(side_up, d)); s0 = np.cross(d, n0); a = flip * PI
    n = n0 * math.cos(a) + s0 * math.sin(a); return d, n0, n, np.cross(d, n)
def notch_pt(hold, d, side_up, i):
    """world point on side A's surface where tally mark i sits (only valid while side A is up)"""
    d, n0, n, s = ladle_axes(d, side_up, 0.0); return V(hold, float) + d * slot_u(i) + n0 * 0.026
def ladle(hold, d, side_up, flip=0.0, newA=(1.0, 0.0)):
    """newA = progress (0..1) of the two marks cut in the film: #15 (his 99th death, frame 0 -> ladle close-up) and #16 (the 100th, end)"""
    d, n0, n, s = ladle_axes(d, side_up, flip); h = V(hold, float)
    h0 = h - d * GRIP_BACK; h1 = h0 + d * HANDLE
    Q = hd.limb(tuple(h0), tuple(h1), 0.025, 0.02, WOOD, n=10, m=2, ref=tuple(n))
    Q += hd.ellip(tuple(h0), np.column_stack([s, n, d]), (0.026, 0.026, 0.02), 8, 4, WOOD)                     # rounded handle end
    bc = h1 + d * (BOWL_R * 0.95) - n * 0.012                                       # the bowl hangs off the end, hollow facing side A
    Rb = np.column_stack([s, n, d])
    Q += hd.ellip(tuple(bc), Rb, (BOWL_R, 0.05, BOWL_R), 14, 8, WOOD_D, v0=PI * 0.5, v1=PI,
                  colfn=lambda i, j, cl: hd.shade(WOOD_D, 0.88) if (i + j) % 2 else WOOD_D)       # solid round underside
    ring = [(BOWL_R * math.cos(2 * PI * k / 20), BOWL_R * math.sin(2 * PI * k / 20)) for k in range(20)]
    Q += hd.poly_decal(tuple(bc), tuple(n), tuple(d), ring, (184, 134, 84), lift=0.001)                   # light rim
    Q += hd.poly_decal(tuple(bc), tuple(n), tuple(d), [(x * 0.82, y * 0.82) for x, y in ring], (62, 40, 24), lift=0.002)   # dark hollow
    Q += hd.poly_decal(tuple(bc + d * 0.012), tuple(n), tuple(d), [(x * 0.45, y * 0.35) for x, y in ring], (84, 56, 34), lift=0.003)
    Q += hd.limb(tuple(h1 - d * 0.02), tuple(bc - d * (BOWL_R * 0.9)), 0.021, 0.019, WOOD, n=8, m=1)     # neck into the rim
    def mark(u, nrm, w, col_g, col_l, k=1.0, tilt=0.0):
        c = h + d * u + nrm * 0.0255; ax = hd.nz(d + np.cross(nrm, d) * tilt)          # tilt != 0: the diagonal strike of a tally group
        out = hd.decal(tuple(c), tuple(nrm), tuple(ax), w * k, 0.0065, col_g, lift=0.0015)
        if k > 0.15: out += hd.decal(tuple(c + ax * 0.0048), tuple(nrm), tuple(ax), w * k, 0.0024, col_l, lift=0.002)
        return out
    def tally(i, nrm, col_g, col_l, pr=1.0, base_u=0.0, gap=0.066):
        g, j = divmod(i, 5); u0 = base_u + 0.035 + g * gap
        if j < 4: return mark(u0 + j * 0.011, nrm, 0.03, col_g, col_l, k=pr)
        return mark(u0 + 0.0165, nrm, 0.062, col_g, col_l, k=pr, tilt=1.6)          # 5th = strike across the four
    nA = n0 * math.cos(flip * PI) + np.cross(d, n0) * math.sin(flip * PI)            # side A normal (follows the flip)
    for i in range(NA_OLD): Q += tally(i, nA, GROOVE, LIP)
    for i, pr in ((NA_OLD, newA[0]), (NA_OLD + 1, newA[1])):
        if pr > 0.02: Q += tally(i, -(-nA), mixc(WOOD, GROOVE, min(1, pr * 1.6)), LIP, pr=min(1.0, pr * 1.25))
    nB = -nA                                                                          # side B: his own deaths, tally groups end to end, faded
    for i in range(35): Q += tally(i, nB, GROOVE_B, LIP_B, base_u=-0.06, gap=0.047)
    for g_ in range(8):                                                               # ... and on over the back of the bowl
        th = 2 * PI * g_ / 8
        for j in range(5):
            ang = th + (j - 2) * 0.09 if j < 4 else th; r_ = BOWL_R * 0.62
            loc = V((r_ * math.cos(ang), -0.034, r_ * math.sin(ang))); p_ = bc + Rb @ loc
            nrm = hd.nz(Rb @ V((0.62 * math.cos(ang), -0.8, 0.62 * math.sin(ang)))); radial = hd.nz(Rb @ V((math.cos(ang), 0, math.sin(ang))))
            Q += hd.decal(tuple(p_ + nrm * 0.004), tuple(nrm), tuple(radial if j < 4 else hd.nz(radial + Rb @ V((-math.sin(ang), 0, math.cos(ang))) * 1.4)),
                          0.004 if j < 4 else 0.005, 0.022 if j < 4 else 0.034, GROOVE_B, lift=0.001)
    return [q for q in Q if q]
def mixc(a, b, u): return tuple(int(round(x + (y - x) * max(0.0, min(1.0, u)))) for x, y in zip(a, b))
def knife(grip, tip, face_n=None):
    """blade ends exactly at `tip` (always aimed at the ladle). The blade is a flat steel shape whose face turns toward face_n
    (the camera side) so it reads as a knife, not a wire."""
    g = V(grip, float); tp = V(tip, float); d = hd.nz(tp - g)
    fn = V((0, 1.0, 0)) if face_n is None else hd.nz(V(face_n, float))
    w = np.cross(d, fn)
    if np.linalg.norm(w) < 1e-4: w = np.cross(d, V((1.0, 0, 0)))
    w = hd.nz(w); L = np.linalg.norm(tp - g)
    Q = hd.limb(tuple(g - d * 0.06), tuple(g + d * 0.028), 0.015, 0.014, (70, 50, 34), n=6, m=1)
    Q += hd.limb(tuple(g + d * 0.026), tuple(g + d * 0.034), 0.02, 0.02, (150, 126, 80), n=6, m=1)       # guard
    b0 = g + d * 0.034; spine = [b0 + w * 0.012, b0 + d * (L - 0.034) * 0.75 + w * 0.009, tp]
    edge = [b0 - w * 0.012, b0 + d * (L - 0.034) * 0.6 - w * 0.011]
    Q.append(hd.face([spine[0], spine[1], spine[2], edge[1], edge[0]], (214, 220, 228)))
    Q.append(hd.face([edge[0], edge[1], spine[2], edge[1] + w * 0.004], (250, 252, 255)))                 # bright cutting edge
    return [q for q in Q if q]

def respawn_motes(t, t0=0.0, d=0.9):
    """the save point brings him back: pale-blue motes rise off him and fade (frame 0 = mid-respawn, the loop's white flash lands here)"""
    u = (t - t0) / d
    if not (-0.3 <= u < 1.0): return []
    Q = []
    for i in range(26):
        a = PI * (hsh(i, 21) - 0.5) * 1.4; r = 0.3 + 0.22 * hsh(i, 22); ph = (u + hsh(i, 23) * 0.5)
        y = 0.3 + 0.9 * ph; s_ = 0.009 * (1 - 0.6 * u)
        x = HERO[0] + r * math.sin(a); z = HERO[2] + 0.1 + r * abs(math.cos(a)) * 0.5
        col = (210, 240, 255) if i % 3 else (150, 210, 255)
        Q += hd.bx((x, y, z), np.eye(3), (s_, s_, s_), col, emit=True)
    return [q for q in Q if q]

def text_w(s, sc): return len(s) * 6 * sc - sc
COVER = ('99 KERE', 'ÖLDÜN') if TRL else ('YOU DIED', '99 TIMES')
COVER_Y = int(os.environ.get('COVER_Y', '1300'))      # middle of the frame, beside the action (Enes 26 Nov); no POV line (Enes)
def cover_overlay(im, t, a=0.0, b=None):
    """two lines: white with a blood-red block shadow, then big gold-yellow on a red band; punches in over 0.12 s"""
    b = (T0['02'] - 0.15) if b is None else b
    if not (a <= t < b): return
    d = ImageDraw.Draw(im); pop = sm(seg01(t, 0, 0.12)); sc0 = 16 if pop >= 1 else 19
    s1, s2 = COVER; y1 = COVER_Y; y2 = COVER_Y + 8 * sc0 + 34
    sc2 = sc0 + 2; w2 = text_w(s2, sc2)
    d.rectangle([540 - w2 / 2 - 34, y2 - 22, 540 + w2 / 2 + 34, y2 + 7 * sc2 + 22], fill=(150, 14, 18))      # red band behind line 2
    for s_, y, sc, col, sh in ((s1, y1, sc0, (255, 255, 255), (170, 16, 20)), (s2, y2, sc2, (255, 222, 40), (60, 0, 0))):
        x = int(540 - text_w(s_, sc) / 2)
        look.draw_cells(d, look.text_cells(s_, x + 10, y + 10, sc, sh), 0)                                   # block shadow
        look.draw_cells(d, look.text_cells(s_, x, y, sc, col), 7)
# =====================================================================================================================
#                                                      THE FILM
# =====================================================================================================================
import json
from nightkit.audio import Sound, duck_envelope, soft_fire
OUT = 'out'; os.makedirs(OUT, exist_ok=True)
TTS_DIR = os.environ.get('TTS_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tts'))
SCR = json.load(open(os.path.join(TTS_DIR, 'sp', 'script.json'), encoding='utf-8'))
KEYS = ['%02d' % i for i in range(1, 14)]
GAP = {'01': 0.45, '02': 0.3, '03': 0.45, '04': 0.2, '05': 0.3, '06': 0.95, '07': 0.4, '08': 0.4, '09': 0.35, '10': 0.3, '11': 0.5, '12': 0.0}
T_WL = 2.4                                        # wordless beat after line 12 (build s)
T_DIE = 1.7                                       # red flash + YOU DIED before line 13
def _lines():
    t = 0.3; out = []
    for k in KEYS:
        out.append((k, round(t, 3))); t += SCR['dur'][k] + GAP.get(k, 0.0)
        if k == '12': t += T_WL + T_DIE
    return out
LINES = _lines(); T0 = dict(LINES)
def tend(k): return T0[k] + SCR['dur'][k]
def ws(k, i): return T0[k] + SCR['sent'][k][i][0]
# beats (build seconds)
T_BOWL = (T0['02'] + 0.3, T0['02'] + 1.1, T0['02'] + 1.8)            # reach to the bowl on the stone, lift, on the lap
T_FLIP = (T0['07'] - 0.85, T0['07'] - 0.1)                         # the keeper turns the ladle over
T_GLANCE = (T0['09'] - 0.1, tend('09') + 0.2)                      # he looks back at the rusty sword
T_UP = (T0['10'] - 0.35, T0['10'] + 0.6)                           # the hero puts the bowl down and stands
T_PICK = (T0['10'] + 0.6, T0['10'] + 1.3)                          # picks up his sword
T_WALK = tend('10') + 0.15                                         # walks off toward the red gate
T_RAISE = (T0['12'] - 0.1, T0['12'] + 0.7)                         # the keeper raises his knife
T_STOP = (tend('12') + 0.1, tend('12') + 0.4)                      # WORDLESS: the knife stops above the ladle
T_LOWER = (tend('12') + 1.0, tend('12') + 1.6)                     # ... and goes down, no notch; he looks toward the gate
T_BOOM = tend('12') + T_WL                                         # far red flash + roar
T_SIGH = (T0['13'] - 0.55, T0['13'] - 0.1)                         # sigh, the knife goes back to the ladle
T_WHITE = tend('13') + 0.35                                        # respawn flash
T_LOOPF = T_WHITE + 0.22                                           # after the white: the frame-0 shot at negative time
DUR = round(T_LOOPF + 0.45, 3); N = int(round(DUR * FPS))
CUTS = [('open', 0.0), ('two', T0['02'] - 0.15), ('ladleA', T0['03'] - 0.1), ('talk', T0['04'] - 0.15), ('flip', T_FLIP[0] - 0.1),
        ('sword', T0['09'] - 0.25), ('stand', T0['10'] - 0.45), ('leave', T0['12'] - 0.25), ('stop', T_STOP[0] - 0.15), ('died', T_BOOM - 0.05), ('end', T0['13'] - 0.55)]
def scene(t):
    if t < 0: return 'open'
    nm = CUTS[0][0]
    for n_, a in CUTS:
        if t >= a: nm = n_
    return nm
def talking(t, key):
    if key not in T0: return None
    for a, b, _ in SCR['sent'][key]:
        if T0[key] + a <= t < T0[key] + b: return 'open' if (t * 7.3 + 0.2 * math.sin(t * 13)) % 1.0 < 0.55 else 'neutral'
    return None

# ======================= props on the ground =======================
STONE = (0.02, 0.0, 1.62); BOWL0 = V((0.02, 0.13, 1.62))           # the bowl waits on a flat stone at his right
SWORD0 = (0.98, 0.03, 1.45)                                        # his own sword lies at his left
GATE = V((-4.6, 0.0, -13.5)); WALK_DIR = hd.nz(GATE - V(HERO)); WALK_YAW = math.atan2(WALK_DIR[0], WALK_DIR[2])
def stone_faces(): return fp.rock(STONE, 0.17, (104, 98, 92), seed=4, flat=0.45)
def bowl(c, tilt=None):
    c = V(c, float); R = np.eye(3) if tilt is None else tilt
    Q = hd.lathe(tuple(c - V((0, 0.045, 0))), R, [(0.02, 0.0), (0.075, 0.02), (0.1, 0.06)], 10, (120, 82, 52), cap1=False)
    Q += hd.ellip(tuple(c + R @ V((0, 0.045, 0))), R, (0.09, 0.006, 0.09), 10, 3, (170, 110, 60))         # the soup
    return [q for q in Q if q]
def steam(c, t, k=1.0):
    Q = []
    for i in range(5):
        u = (t * 0.4 + hsh(i, 31)) % 1.0; x = c[0] + 0.03 * math.sin(t * 2 + i * 2) * u; y = c[1] + 0.06 + 0.35 * u; z = c[2] + 0.02 * math.cos(i + t)
        s_ = 0.012 * (1 - u) * k
        if s_ > 0.003: Q += hd.bx((x, y, z), np.eye(3), (s_, s_, s_), (200, 196, 190), emit=False)
    return [q for q in Q if q]
def gate_far():
    """dark castle gate far away on the open side of the camp (only seen in 'leave' / 'died'), red glow in the doorway"""
    Q = []; c = GATE; ux = hd.nz(np.cross((0, 1.0, 0), WALK_DIR))
    def P_(a, y): return tuple(c + ux * a + V((0, y, 0)))
    Q.append(hd.face([P_(-3.0, 0), P_(3.0, 0), P_(3.0, 4.2), P_(-3.0, 4.2)], (22, 18, 26)))
    for i in range(6): Q.append(hd.face([P_(-3.0 + i * 1.1, 4.2), P_(-2.45 + i * 1.1, 4.2), P_(-2.45 + i * 1.1, 4.8), P_(-3.0 + i * 1.1, 4.8)], (22, 18, 26)))
    for sx in (-3.6, 3.6): Q.append(hd.face([P_(sx - 0.8, 0), P_(sx + 0.8, 0), P_(sx + 0.8, 6.0), P_(sx - 0.8, 6.0)], (20, 16, 24)))
    off = -WALK_DIR * 0.05
    Q.append(hd.face([tuple(V(P_(-0.9, 0)) + off), tuple(V(P_(0.9, 0)) + off), tuple(V(P_(0.9, 2.3)) + off), tuple(V(P_(0, 3.0)) + off), tuple(V(P_(-0.9, 2.3)) + off)], (190, 40, 28), emit=True))
    G = fp.ground(-9, 9, -18, -3, 1.0, [(46, 52, 36), (52, 56, 38), (42, 46, 34)], seed=9)                   # the camp ground stops at z=-3
    return [q for q in Q + G if q]
_SET2 = []
def set2():
    if not _SET2: _SET2.append(stone_faces() + gate_far())
    return _SET2[0]

# ======================= hero =======================
def hero_pose(t):
    """sits up from the bedroll with a gasp, picks up the bowl, laughs, stands, takes his sword, walks to the gate"""
    up = sm(seg01(t, -0.1, 0.6))
    P = dict(base=HERO, yaw=HERO_YAW, crouch=0.8, lean=lerp(-0.7, -0.15, up), eyes='wide', mouth='o', brow=0.5, nod=lerp(-0.15, 0.05, up))
    P['rf'] = (0.16, 0.07, 0.66); P['lf'] = (-0.08, 0.07, 0.58); P['rkpole'] = (0.1, 1.0, 0.3); P['lkpole'] = (-0.1, 1.0, 0.3)
    P['rh'] = (0.3, 0.12, -0.18); P['lh'] = (-0.3, 0.12, -0.15); P['rgrip'] = 0.3; P['lgrip'] = 0.3
    P['head'] = (0.35 * up, lerp(-0.15, 0.08, up), 0.0)
    if t > 1.0:                                                                   # breathing again; looks at the keeper
        lk = sm(seg01(t, 1.0, 1.5)); P['head'] = (lerp(0.35, 0.55, lk), 0.05, 0.0); P['eyes'] = 'open' if t > 1.6 else 'wide'
        P['mouth'] = 'neutral' if t > 1.3 else 'o'; P['brow'] = lerp(0.5, 0.1, lk); P['twist'] = 0.15 * lk
    bowl_at = None
    if t >= T_BOWL[0]:                                                            # right hand: to the bowl on the stone -> lap
        r = sm(seg01(t, T_BOWL[0], T_BOWL[1])); l = sm(seg01(t, T_BOWL[1], T_BOWL[2]))
        reach = BOWL0 + V((0.0, 0.03, 0.0)); lap = wpt(HERO, HERO_YAW, (0.02, 0.42, 0.3))
        hand = lerp3(wpt(HERO, HERO_YAW, (0.3, 0.12, -0.18)), reach, r) if l <= 0 else lerp3(reach, lap, l)
        P['rh_w'] = tuple(hand); P['rgrip'] = 0.6; P['rpalm'] = (0, 1.0, 0); P['rpalm_local'] = True
        if l > 0.2: P['lh'] = lerp3((-0.3, 0.12, -0.15), (-0.06, 0.4, 0.3), sm(seg01(t, T_BOWL[1] + 0.2, T_BOWL[2]))); P['lgrip'] = 0.5
        bowl_at = V(hand) + V((0, 0.07, 0)) if r >= 1 else BOWL0
        P['lean'] = lerp(-0.15, 0.12, l)
    if T0['04'] <= t: P['mouth'] = talking(t, '04') or 'neutral'; P['brow'] = 0.3; P['eyes'] = 'open'
    if T0['06'] - 0.1 <= t < tend('06') + 0.4: P['mouth'] = talking(t, '06') or 'smile'; P['brow'] = 0.6
    if t >= T0['07']: P['mouth'] = 'neutral'; P['brow'] = -0.3; P['eyes'] = 'open'
    if T_GLANCE[0] + 0.25 <= t < T_UP[0]: P['head'] = (0.75, 0.1, 0.0)       # follows the keeper's look to the rusty sword
    if t >= T_UP[0]:                                                              # bowl back on the stone, stand up
        u = sm(seg01(t, *T_UP)); dn = sm(seg01(t, T_UP[0], T_UP[0] + 0.35))
        hand = lerp3(wpt(HERO, HERO_YAW, (0.02, 0.42, 0.3)), BOWL0 + V((0, 0.03, 0)), dn)
        P['rh_w'] = tuple(hand) if u < 0.5 else None
        if u >= 0.5: P.pop('rh_w', None); P['rh'] = lerp3((0.3, 0.5, 0.1), (0.22, 0.85, 0.05), sm(seg01(u, 0.5, 1.0)))
        bowl_at = hand + V((0, 0.07, 0)) if dn < 1 else BOWL0
        if t >= T_UP[0] + 0.35: bowl_at = BOWL0
        P['crouch'] = lerp(0.8, 0.0, sm(seg01(t, T_UP[0] + 0.3, T_UP[1]))); P['lean'] = lerp(0.12, 0.25, u) * (1 - sm(seg01(t, T_UP[1] - 0.2, T_UP[1] + 0.2)))
        P['rf'] = lerp3((0.16, 0.07, 0.66), (0.11, 0.075, 0.02), u); P['lf'] = lerp3((-0.08, 0.07, 0.58), (-0.11, 0.075, 0.02), u)
        P['rkpole'] = None; P['lkpole'] = None; P['lh'] = (-0.25, 0.85, 0.05) if u > 0.5 else P.get('lh')
        P['head'] = (lerp(0.55, 0.3, u), 0.0, 0.0); P['brow'] = 0.4; P['mouth'] = talking(t, '10') or 'neutral'
        P['yaw'] = lerp(HERO_YAW, HERO_YAW - 0.9, sm(seg01(t, T_UP[1] - 0.2, T_PICK[0] + 0.2)))
    if t >= T_PICK[0]:                                                            # bends to the sword at his left and takes it
        u = sm(seg01(t, *T_PICK)); bend = win(t, T_PICK[0], T_PICK[1] + 0.25, 0.3)
        P['crouch'] = 0.32 * bend; P['lean'] = 0.45 * bend
        P['lh_w'] = tuple(lerp3(wpt(P['base'], P['yaw'], (-0.25, 0.85, 0.05)), V(SWORD0) + V((0, 0.06, 0.32)), bend)) if t < T_PICK[1] else None
        if t >= T_PICK[1]: P.pop('lh_w', None); P['lh'] = (-0.22, 0.95, 0.25)
        P['lgrip'] = 0.9 if u > 0.5 else 0.4; P['mouth'] = talking(t, '10') or 'neutral'
    if t >= T_WALK:                                                               # walks off toward the red gate
        d = 1.15 * max(0.0, t - T_WALK - 0.3) + 0.5 * sm(seg01(t, T_WALK, T_WALK + 0.6)) * 0.6
        base = V(HERO) + WALK_DIR * d; P['base'] = tuple(base); P['yaw'] = lerp(HERO_YAW - 0.9, WALK_YAW, sm(seg01(t, T_WALK, T_WALK + 0.5)))
        P['crouch'] = 0.0; P['lean'] = 0.08; P['walk'] = d * 5.2; P['stride'] = 0.34; P['head'] = (0.0, 0.0, 0.0)
        P['rf'] = None; P['lf'] = None; P['rh'] = None; P['lh'] = (-0.22, 0.95, 0.25); P['cape_sway'] = 0.3 * math.sin(t * 4)
        for kk in ('rf', 'lf', 'rh'): P.pop(kk, None)
    return P, bowl_at
def wpt(base, yaw, l): return V(base, float) + hd.Ry(yaw) @ V(l, float)
def hero_sword(P, t):
    if t < T_PICK[0] + 0.35: return hd.sword(SWORD0, (0.0, 0.0, -1.0), (0, 1.0, 0), length=0.78)
    g = fp.grip_pt(P, 'l', 0.06, 0.0); RW = P['_RW']
    return hd.sword(tuple(g), hd.nz(RW @ V((0.1, 0.55, 0.6))) if t < T_WALK else hd.nz(RW @ V((0.05, -0.75, 0.55))), P['_lpalm'], length=0.78)

# ======================= keeper =======================
def keeper_pose(t):
    P = dict(base=KEEP, yaw=KEEP_YAW, crouch=0.48, lean=0.28, eyes='half', mouth='neutral', brow=-0.2, nod=0.25)
    P['rf'] = (0.14, 0.07, 0.36); P['lf'] = (-0.14, 0.07, 0.32); P['rkpole'] = (0.1, 0.6, 1.0); P['lkpole'] = (-0.1, 0.6, 1.0)
    P['lh'] = (-0.12, 0.72, 0.36); P['lgrip'] = 0.85; P['rgrip'] = 0.85
    for k in ('01', '05', '07', '09', '11', '13'):
        mt = talking(t, k)
        if mt: P['mouth'] = mt
    if T0['01'] - 0.1 <= t < tend('01') + 0.3: P['eyes'] = 'half'; P['brow'] = -0.3
    if T0['07'] - 0.1 <= t < tend('07') + 0.3: P['nod'] = 0.05; P['eyes'] = 'open'; P['brow'] = -0.5   # looks up at the hero
    if T_GLANCE[0] <= t < T_GLANCE[1]:                                          # glances back over his shoulder at the rusty sword
        g = win(t, T_GLANCE[0], T_GLANCE[1], 0.35); P['head'] = (-1.0 * g, 0.0, 0.0); P['twist'] = -0.25 * g; P['eyes'] = 'sad'; P['brow'] = -0.6
    if T0['11'] - 0.2 <= t < tend('11') + 0.5: P['mouth'] = talking(t, '11') or 'smile'; P['eyes'] = 'open'; P['brow'] = 0.1; P['nod'] = 0.05
    if t >= T_RAISE[0] and t < T_SIGH[0]:
        P['eyes'] = 'open'; P['nod'] = lerp(0.25, -0.05, sm(seg01(t, *T_LOWER)))
        P['head'] = (0.25 * sm(seg01(t, *T_LOWER)), 0.0, 0.0); P['brow'] = -0.4 if t > T_LOWER[0] else -0.1
        if t >= T_LOWER[1] + 0.2: P['mouth'] = 'soft'
    if T_BOOM <= t < T_SIGH[0]: P['eyes'] = 'closed' if t > T_BOOM + 0.35 else 'wide'; P['brow'] = -0.7
    if t >= T_SIGH[0]: P['eyes'] = 'half'; P['brow'] = -0.4; P['nod'] = 0.3; P['mouth'] = talking(t, '13') or 'soft'
    return P
T_UNFLIP = (T0['11'] - 0.7, T0['11'] - 0.05)                       # back to side A while the hero stands (small polish adjustment)
def flip_u(t): return sm(seg01(t, *T_FLIP)) * (1 - sm(seg01(t, *T_UNFLIP)))
T_N99 = T0['03'] + 0.62 * SCR['dur']['03']                         # notch #15 (death 99) fully cut ~ on 'notch'
T_N100 = (T_SIGH[1] + 0.05, T_SIGH[1] + 1.05)                       # notch #16 (death 100) during 'Get up, kid.'
def notch_progress(t):
    a = CUTS[2][1]                                                  # most of the cut happens inside the ladle close-up, so it reads
    p99 = 0.15 * sm(seg01(t, 0.0, a)) + 0.85 * sm(seg01(t, a + 0.25, T_N99))
    if t < 0: p99 = 0.0                                             # loop tail: just before frame 0, the cut has not started
    return (p99, sm(seg01(t, *T_N100)))
def carving_now(t): return (0.0 <= t < T0['04'] - 0.2) or (t < 0) or (T_SIGH[1] <= t)
_KC = {}
def _ladle_geo(P):
    lw = fp.grip_pt(P, 'l', 0.06, 0.0); RWk = P['_RW']; d_l = hd.nz(RWk @ V((0.55, 0.45, 0.6))); up = RWk @ V((0, 0.6, 1.0)); return lw, d_l, up
def knife_targets(t, P, lw, d_l, up):
    g, tp = _knife_targets(t, P, lw, d_l, up); return V(g, float), V(tp, float)
def _knife_targets(t, P, lw, d_l, up):
    """(wanted grip, blade tip): the blade always points at the ladle, never at the hero"""
    d, n0, n, side = ladle_axes(d_l, up, 0.0)
    if np.dot(side, P['_RW'] @ V((1.0, 0, 0))) < 0: side = -side              # 'side' = toward his knife hand
    slot = NA_OLD + (1 if t >= T_SIGH[0] else 0)
    NP = notch_pt(lw, d_l, up, slot)
    stroke = math.sin(t * 9.0)                                                 # short sawing strokes across the handle
    tip_c = NP + side * 0.013 * stroke + n0 * 0.002
    grip_c = NP + side * 0.15 + n0 * 0.06 - d * 0.02 + side * 0.013 * stroke
    rest_g = V(P['base']) + hd.Ry(P['yaw']) @ V((0.2, 0.6, 0.3))              # resting on his right knee
    mid = V(lw) + d * 0.2
    rest_t = rest_g + hd.nz(mid - rest_g) * 0.14
    hov_g = NP + n0 * 0.17 + side * 0.07; hov_t = hov_g + hd.nz(NP - hov_g) * 0.135      # wordless: poised over the next notch
    if carving_now(t) and not (T_RAISE[0] <= t < T_SIGH[1]):
        k = 1.0 if t >= T_SIGH[1] or t < T0['04'] - 0.45 else 1 - sm(seg01(t, T0['04'] - 0.45, T0['04'] - 0.2))
        return lerp3(rest_g, grip_c, k), lerp3(rest_t, tip_c, k)
    if T_RAISE[0] <= t < T_SIGH[1]:
        up_ = sm(seg01(t, *T_RAISE)); dn = sm(seg01(t, *T_LOWER)); back = sm(seg01(t, *T_SIGH))
        g = lerp3(lerp3(rest_g, hov_g, up_), rest_g, dn); tp = lerp3(lerp3(rest_t, hov_t, up_), rest_t, dn)
        if t >= T_SIGH[0]: g = lerp3(rest_g, grip_c, back); tp = lerp3(rest_t, tip_c, back)
        return g, tp
    k = sm(seg01(t, T0['04'] - 0.2, T0['04'] + 0.15))                         # carving -> rest
    return rest_g, rest_t
KL = 0.14                                                             # grip -> blade tip
def _fist(P):
    """centre of the right fist and the forearm direction (the knife passes through the fist across the palm)"""
    wr = V(P['_rwrist']); dfa = V(P['_rdir']); pn = V(P['_rpalm']); return wr + dfa * 0.05 + pn * 0.012, dfa
def keeper(t):
    k = round(t * FPS * 4)
    if k not in _KC:
        _KC.clear(); P = keeper_pose(t); P.pop('rh', None)
        P['rh_w'] = tuple(V(P['base']) + hd.Ry(P['yaw']) @ V((0.2, 0.6, 0.3))); hd.human(KEEPER, P)
        lw, d_l, up = _ladle_geo(P)
        g0, tipw = knife_targets(t, P, lw, d_l, up)
        g, dfa = _fist(P); P['rh_w'] = tuple(V(P['rh_w']) + (g0 - g))
        for _ in range(4):                    # knife fix 26 Nov (Enes: odd grip at the end): blade leaves the THUMB side of the fist,
            Q = hd.human(KEEPER, P); lw, d_l, up = _ladle_geo(P)          # square to the forearm, and the wrist is moved so the tip lands on target
            _, tipw = knife_targets(t, P, lw, d_l, up); g, dfa = _fist(P)
            bb = tipw - g; bb = bb - dfa * np.dot(bb, dfa)
            bb = hd.nz(bb) if np.linalg.norm(bb) > 1e-4 else hd.nz(np.cross(dfa, V((0, 1.0, 0))))
            P['rpalm'] = tuple(hd.nz(np.cross(dfa, bb))); P['rpalm_local'] = False    # right hand: thumb side = cross(palm, forearm) = bb
            P['rh_w'] = tuple(V(P['rh_w']) + ((tipw - bb * KL) - g) * 0.85)
        Q = hd.human(KEEPER, P); lw, d_l, up = _ladle_geo(P); g, dfa = _fist(P)
        _, tipw = knife_targets(t, P, lw, d_l, up); bb = tipw - g; bb = hd.nz(bb - dfa * np.dot(bb, dfa))
        rw = g; tip = g + bb * KL
        _KC[k] = (P, Q, lw, d_l, up, rw, tip)
    return _KC[k]
def ladle_frame(t):
    P, Q, lw, d_l, up, rw, tip = keeper(t); n0 = hd.nz(V(up) - d_l * np.dot(up, d_l)); return lw, d_l, n0

# ======================= camera =======================
P3 = look.Path
OPEN_P = lambda t: lerp3((0.6, 1.25, 0.92), (0.61, 1.25, 0.99), sm(seg01(t, -1, 2)))
def cam_shot(t):
    sc = scene(t)
    if sc == 'open': return OPEN_P(t), (0.9, 0.75, 2.6), 50.0
    if sc == 'two':
        a, b = CUTS[1][1], CUTS[2][1]; u = sm(seg01(t, a, b))
        return lerp3((0.55, 1.35, 0.45), (0.5, 1.3, 0.7), u), lerp3((0.75, 0.62, 2.3), (0.8, 0.65, 2.4), u), 52.0
    if sc in ('ladleA', 'flip'):
        i_ = 2 if sc == 'ladleA' else 4
        lw, d_l, n0 = ladle_frame(CUTS[i_][1] + 0.01); c = V(lw) + d_l * 0.21
        u = sm(seg01(t, CUTS[i_][1], CUTS[i_ + 1][1])); side = hd.nz(np.cross(d_l, n0))
        KP_ = keeper(CUTS[i_][1] + 0.01)[0]
        if np.dot(side, KP_['_RW'] @ V((1.0, 0, 0))) < 0: side = -side
        dist = lerp(0.6, 0.5, u) if sc == 'ladleA' else lerp(0.58, 0.42, u)
        pos = c + n0 * dist * 0.9 - side * dist * 0.4 + V((0, 0.04, 0)); return pos, c, 40.0
    if sc == 'talk':
        u = sm(seg01(t, T0['06'] - 0.35, T0['06'] - 0.05))
        if u <= 0.0:
            cr = 0.06 * seg01(t, CUTS[3][1], T0['06']); return V((0.25, 1.15, 1.05 + cr)), (1.25, 0.95, 3.0), 44.0
        cr = 0.05 * seg01(t, T0['06'], CUTS[4][1]); return V((0.3, 1.02, 0.92 + cr)), (0.55, 0.82, 1.9), 44.0
    if sc == 'sword':
        a, b = CUTS[5][1], CUTS[6][1]; u = sm(seg01(t, a, b))
        return lerp3((0.55, 1.2, 1.55), (0.6, 1.2, 1.7), u), (1.45, 0.95, 3.25), 44.0
    if sc == 'stand':
        a, b = CUTS[6][1], CUTS[7][1]; u = sm(seg01(t, a, b))
        return lerp3((0.35, 1.4, -0.75), (0.4, 1.42, -0.5), u), lerp3((0.8, 0.95, 2.2), (0.85, 1.05, 2.3), u), 50.0
    if sc == 'leave':
        a, b = CUTS[7][1], CUTS[8][1]; u = sm(seg01(t, a, b))
        p = lerp3((1.95, 1.35, 3.75), (1.85, 1.3, 3.55), u); q = lerp3((0.3, 0.85, 0.2), (-0.6, 0.95, -2.5), u)
        return p, q, lerp(44.0, 40.0, u)
    if sc in ('stop', 'end'):
        f = hd.nz(V(HERO) - V(KEEP)); f[1] = 0; f = hd.nz(f); sd = hd.nz(np.cross((0, 1.0, 0), f))
        a = CUTS[8][1] if sc == 'stop' else CUTS[10][1]; u = sm(seg01(t, a, a + 2.5))
        dist = lerp(1.05, 0.9, u); pos = V(KEEP) + f * dist + sd * 0.22 + V((0, 1.02, 0)); tgt = V(KEEP) + f * 0.25 + V((0, 0.8, 0))
        return pos, tgt, 44.0
    # died: the wide over his shoulder again, the gate flashes
    u = sm(seg01(t, CUTS[9][1], CUTS[10][1]))
    return lerp3((1.85, 1.3, 3.55), (1.8, 1.28, 3.45), u), (-0.6, 0.95, -2.5), 40.0

# ======================= render =======================
def frame_low(t):
    pos, tgt, fov = cam_shot(t); cam = Camera.look(tuple(pos), tuple(tgt)); sc = scene(t)
    ff = fp.fire_faces(t)
    if sc in ('ladleA', 'flip', 'stop', 'end', 'talk'): ff = ff[:14]                    # flames only: embers near the lens become big orange squares
    layers = [set_faces(), set2(), ff]
    fl = 1 + 0.12 * math.sin(t * 9) + 0.06 * math.sin(t * 23)
    L = [((FIRE[0], 0.55, FIRE[2]), (255, 150, 70), 2.4 * fl), ((-6, 9, -2), (110, 130, 200), 1.0), ((0.4, 1.8, -1.2), (130, 120, 160), 0.6)]
    L.append(((GATE[0], 2.0, GATE[2] + 1.0), (255, 60, 40), 1.2))
    boom = win(t, T_BOOM, T_BOOM + 0.9, 0.12)
    if boom > 0: L.append(((GATE[0], 6.0, GATE[2] + 2.0), (255, 70, 40), 9.0 * boom))
    HP, bowl_at = hero_pose(t)
    hide_hero = t >= T_BOOM - 0.05 and t >= 0
    if not hide_hero:
        layers.append(hd.human(ADV, HP)); layers.append(hero_sword(HP, t))
    else: layers.append(hd.sword(SWORD0, (0.0, 0.0, -1.0), (0, 1.0, 0), length=0.78)) if False else None
    bc = BOWL0 if bowl_at is None else bowl_at
    layers.append(bowl(bc)); layers.append(steam(bc, t))
    rs = respawn_motes(t)
    if rs: layers.append(rs); L.append(((HERO[0], 0.7, HERO[2] - 0.3), (190, 230, 255), 1.4 * (1 - sm(seg01(t, 0.0, 0.9)))))
    KP, KQ, lw, d_l, up, rw, tip = keeper(t); layers.append(KQ)
    cutting = carving_now(t) and not (T_RAISE[0] <= t < T_SIGH[1])
    layers.append(ladle(lw, d_l, up, flip=flip_u(t), newA=notch_progress(t)))
    layers.append(knife(rw, tip, face_n=V(pos) - V(tip)))
    if cutting and sc in ('ladleA', 'open', 'two', 'end'):                              # wood chips curl off the blade tip
        n0 = hd.nz(V(up) - d_l * np.dot(up, d_l)); Q = []
        for i in range(7):
            u_ = (t * 2.4 + hsh(i, 41)) % 1.0; c = V(tip) + n0 * (0.01 + 0.05 * u_) + V((0.025 * math.sin(i * 3) * u_, -0.18 * u_ * u_, 0.02 * math.cos(i) * u_))
            Q += hd.bx(tuple(c), np.eye(3), (0.0045, 0.0045, 0.0045), (232, 204, 158))
        layers.append([q for q in Q if q])
    R = Renderer(W, H, fog=(12, 14, 24))
    img, vi, zb = zrender(R, cam, layers, L, fov=fov, fog_start=9, fog_end=40, ambient=0.34, return_z=True)
    a = look.outline(np.asarray(img).astype(np.float32), zb) * np.array([1.04, 0.98, 0.94])
    if boom > 0: a = a * (1 + 0.25 * boom * np.array([1.0, 0.2, 0.1]))
    a = np.clip((a - 112) * 1.12 + 110, 0, 255)
    return post.ps1(Image.fromarray(a.astype(np.uint8)), levels=6), vi

# ======================= overlays =======================
def ctext(d, s, y, sc, col, o=6, shadow=None):
    x = int(540 - text_w(s, sc) / 2)
    if shadow: look.draw_cells(d, look.text_cells(s, x + sc // 2 + 4, y + sc // 2 + 4, sc, shadow), 0)
    look.draw_cells(d, look.text_cells(s, x, y, sc, col), o)
DIED = 'ÖLDÜN' if TRL else 'YOU DIED'
def died_overlay(arr, t):
    a, b = T_BOOM + 0.12, T_WHITE
    if not (a <= t < b): return arr
    u = sm(seg01(t, a, a + 0.15)); fade = 1 - sm(seg01(t, T0['13'] - 0.75, T0['13'] - 0.55))
    band = np.zeros_like(arr[:, :, 0]); band[700:1080] = 1.0
    arr = arr * (1 - 0.55 * u * fade * band[:, :, None])
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    if fade > 0.05:
        sc = int(round(lerp(26, 22, u))); ctext(d, DIED, 830, sc, (220, 24, 24) if fade > 0.5 else (150, 20, 20), o=7, shadow=(40, 0, 0))
    return np.asarray(im).astype(np.float32)
COL = {'N': (242, 238, 226), 'B': (170, 236, 160), 'K': (255, 196, 90)}
def _sub_scr():
    if not TRL: return SCR
    import importlib.util as _iu
    sp_ = _iu.spec_from_file_location('sp_tts', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'tts', 'sp.py'))
    m_ = _iu.module_from_spec(sp_); sp_.loader.exec_module(m_); TRS = m_.TR_SUB
    out = dict(SCR); sent = {}
    for k, v in SCR['sent'].items():
        if len(v) == len(TRS[k]): sent[k] = [[a, b, tx] for (a, b, _), tx in zip(v, TRS[k])]
        else: sent[k] = [[v[0][0], v[-1][1], ' '.join(TRS[k])]]
    out['sent'] = sent
    return out
SUBS = look.Subtitles(_sub_scr(), LINES, W, H, S, COL, title_key='none', n=17,
                      hil=({'ÇENTİK', 'DOKSAN', 'DOKUZ', 'BİN', 'İKİ', 'SOLMUŞ.', 'SAYMAYI'} if TRL else {'NOTCH', 'NINETY-NINE.', 'THOUSAND', 'TWELVE.', 'FADED.', 'FULL.'}))
LBL_D = 'ÖLÜM' if TRL else 'DEATHS'; LBL_K = 'BEKÇİNİN ÖLÜMLERİ' if TRL else 'HIS OWN DEATHS'
def counter_overlay(im, t):
    """game-style death counter on the ladle close-ups: his 98 -> 99 as the notch is finished, the keeper's own count rolling
    to 1012 on the flip (too many notches to read one by one), 99 -> 100 at the end"""
    sc = scene(t); d = ImageDraw.Draw(im)
    def box(label, val, pop=0.0, col=(255, 214, 60)):
        vs = str(val); s1 = 5; s2 = int(round(12 + 4 * pop)); w = max(text_w(label, s1), text_w(vs, s2)) + 44
        x0 = 540 - w // 2; y0 = 150
        d.rectangle([x0, y0, x0 + w, y0 + 7 * s1 + 7 * s2 + 58], fill=(14, 10, 8)); d.rectangle([x0 + 6, y0 + 6, x0 + w - 6, y0 + 7 * s1 + 7 * s2 + 52], outline=(150, 110, 60), width=4)
        ctext(d, label, y0 + 18, s1, (232, 222, 200), o=3); ctext(d, vs, y0 + 7 * s1 + 32 - int(14 * pop), s2, col, o=5)
    if sc == 'ladleA':
        v = 99 if t >= T_N99 else 98; pop = win(t, T_N99, T_N99 + 0.3, 0.12); box(LBL_D, v, pop, (255, 214, 60) if v == 98 else (255, 120, 80))
    elif sc == 'flip' and t >= (ws('07', 1) if len(SCR['sent']['07']) > 1 else T0['07']) - 0.05:
        a, b = ws('07', 1) if len(SCR['sent']['07']) > 1 else T0['07'], tend('07')
        u = sm(seg01(t, a, b - 0.05)); v = int(round(1012 * u)); pop = win(t, b - 0.05, b + 0.3, 0.12)
        box(LBL_K, v, pop, (210, 200, 186) if u < 1 else (255, 120, 80))
    elif sc == 'end' and t >= T_SIGH[1]:
        v = 100 if t >= T_N100[1] else 99; pop = win(t, T_N100[1], T_N100[1] + 0.3, 0.12); box(LBL_D, v, pop, (255, 214, 60) if v == 99 else (255, 120, 80))
from nightkit import cta
CTA = cta.Achievement(t0=cta.default_time(DUR, dur_on=F(1.5)), lang=SUB_LANG, dur=F(1.5))      # Enes 26 Nov: 1.5 s on screen for this one
def frame_final(t):
    if t >= T_LOOPF: t = t - DUR                                                         # loop tail = the frames just before frame 0
    img, vi = frame_low(t); arr = post.upscale(img, S)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); cover_overlay(im, t)
    if t >= 0: counter_overlay(im, t)
    arr = np.asarray(im).astype(np.float32); arr = died_overlay(arr, t)
    arr = SUBS.apply(arr, t) if t >= 0 else arr
    arr = CTA.apply(arr, t) if t >= 0 else arr
    wf = 0.0
    if t >= 0: wf = sm(seg01(t, T_WHITE - 0.12, T_WHITE + 0.08))
    else: wf = 1 - sm(seg01(t, T_LOOPF - DUR, T_LOOPF - DUR + 0.25))
    if wf > 0: arr = arr * (1 - wf) + 255 * wf
    return arr

TEST = os.environ.get('TEST')
if TEST and __name__ == '__main__':
    ts = [float(x) for x in TEST.split(',')] if TEST != 'all' else [round(x, 2) for x in np.arange(0, DUR, float(os.environ.get('STEP', '1.0')))]
    tw_ = int(os.environ.get('TW', '270')); th = tw_ * 16 // 9
    ims = [Image.fromarray(np.clip(frame_final(x), 0, 255).astype(np.uint8)) for x in ts]
    if os.environ.get('SZ') == 'full':
        for x, im in zip(ts, ims): im.save(f'test_sp_{x:.2f}.png')
    ims = [im.resize((tw_, th), Image.LANCZOS) for im in ims]
    per = int(os.environ.get('PER', '8')); rows = (len(ims) + per - 1) // per; shp = Image.new('RGB', (min(per, len(ims)) * (tw_ + 2), rows * (th + 18)), (30, 30, 30))
    dd = ImageDraw.Draw(shp)
    for i, (im, x) in enumerate(zip(ims, ts)): shp.paste(im, ((i % per) * (tw_ + 2), (i // per) * (th + 18))); dd.text(((i % per) * (tw_ + 2) + 4, (i // per) * (th + 18) + th + 3), f'{x:.2f} {x / 1.2:.1f}f {scene(x)}', fill=(255, 255, 0))
    shp.save(os.environ.get('TEST_OUT', 'test_sp.png')); print('test written', DUR, DUR / 1.2); sys.exit()

QA = dict(fps=FPS, dur=DUR, W=W, frame=lambda t: Image.fromarray(np.clip(frame_final(t), 0, 255).astype(np.uint8)).resize((W, H), Image.BOX), chars={},
          geom=lambda t, name, st, V_: [], camera=lambda t: cam_shot(t)[0], min_cam_dist=0.3, camera_ok=lambda p: True, allow_jump=[], weapon_events=[],
          scenes=[dict(id=nm, t0=a, t1=(CUTS[i + 1][1] if i + 1 < len(CUTS) else DUR), action=nm) for i, (nm, a) in enumerate(CUTS)],
          texts=lambda: [('hud', COVER[0], 16), ('hud', COVER[1], 18), ('hud', DIED, 26)])

# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as _sf
    s = Sound(DUR, loop=False, seed=91); sr = s.sr; n = s.n; t = s.t
    BED = np.zeros(n); FX = np.zeros(n); MUS = np.zeros(n)
    def put(buf, x, t0, v=1.0):
        i = int(round(t0 * sr))
        if i >= n or i + len(x) <= 0: return
        if i < 0: x = x[-i:]; i = 0
        j = min(n, i + len(x)); buf[i:j] += (x * v)[:j - i]
    def nb(t0, d, lo, hi, v, seed, shape=2, buf=None): put(FX if buf is None else buf, s.filt_short(s.noise(d, seed), lo=lo, hi=hi) * np.sin(np.pi * s.T(d) / d) ** shape, t0, v)
    def tone(t0, m, d, v, dec=3.0, att=0.005, glide=0.0, buf=None, harm=(1.0,)):
        f = 440 * 2 ** ((m - 69) / 12); tt = s.T(d); fr = f * (1 + glide * tt / d); ph = np.cumsum(fr) / sr
        x = sum(a * np.sin(2 * np.pi * ph * (k + 1)) for k, a in enumerate(harm)); put(FX if buf is None else buf, x * np.minimum(1, tt / att) * np.exp(-tt * dec), t0, v)
    def thud(t0, f=60, v=0.1, d=0.3, buf=None): tt = s.T(d); put(FX if buf is None else buf, np.sin(2 * np.pi * f * tt * (1 - 0.3 * tt / d)) * np.exp(-tt * 14), t0, v)
    def scrape(t0, d=0.16, v=0.03, seed=0): tt = s.T(d); put(FX, s.filt_short(s.noise(d, seed), lo=1800, hi=7000) * np.sin(np.pi * tt / d) ** 1.5 * (1 + 0.5 * np.sin(2 * np.pi * 38 * tt)), t0, v)
    def step(t0, v=0.03, seed=0): tt = s.T(0.12); put(FX, s.filt_short(s.noise(0.12, seed), lo=150, hi=1800) * np.exp(-tt * 30) + np.sin(2 * np.pi * 75 * tt) * np.exp(-tt * 26) * 0.3, t0, v)
    def mask(a, b, r=0.15): return np.clip(np.minimum((t - a) / r, (b - t) / r), 0, 1)
    # fire + crickets everywhere; the loop tail (after the white) repeats the start
    BED += soft_fire(s, level=0.022, seed=7)
    for k in range(int(DUR / 0.45)):
        tb = 0.2 + k * 0.45 + 0.2 * hsh(k, 3)
        for j in range(3): tt = s.T(0.03); put(BED, np.sin(2 * np.pi * 4300 * tt) * np.sin(np.pi * tt / 0.03), tb + j * 0.06, 0.004)
    # gasp (noise breath) + respawn shimmer at frame 0
    tt = s.T(0.45); put(FX, s.filt_short(s.noise(0.45, 5), lo=500, hi=4000) * np.sin(np.pi * tt / 0.45) ** 0.6 * np.exp(-tt * 2), 0.0, 0.07)
    for k in range(6): tone(0.0 + k * 0.07, 84 + [0, 4, 7, 12, 16, 19][k], 0.8, 0.02 * (1 - k * 0.1), dec=4)
    # carving (open, ladle insert, end)
    for a, b in ((0.0, T0['04'] - 0.2), (T_SIGH[1], DUR)):
        x = a + 0.05
        while x < b - 0.1:
            if not (T_WHITE - 0.1 < x < T_LOOPF): scrape(x, 0.15, 0.03 if CUTS[2][1] <= x < CUTS[3][1] else 0.016, int(x * 50))
            x += 2 * PI / 9.0
    # bowl on the stone (lift / down), wood creak at the flip, sword pick-up, steps away
    thud(T_BOWL[0] + 0.75, 300, 0.02, 0.08); thud(T_UP[0] + 0.35, 280, 0.03, 0.08)
    tt = s.T(0.5); put(FX, np.sin(2 * np.pi * (380 + 120 * np.sin(tt * 18)) * tt) * np.exp(-tt * 5) * np.sin(np.pi * tt / 0.5), T_FLIP[0] + 0.1, 0.02)
    nb(T_PICK[0] + 0.45, 0.35, 2500, 8000, 0.04, 13, 1); tone(T_PICK[0] + 0.6, 98, 0.9, 0.018, dec=3.0, harm=(1.0, 0.5, 0.3))
    x = T_WALK + 0.3; k = 0
    while x < T_BOOM - 0.3: step(x, 0.03 * max(0.2, 1 - k * 0.08), 60 + k); x += 0.48; k += 1
    tone(T_RAISE[0] + 0.3, 101, 0.4, 0.008, dec=8)                                      # a tiny glint as the knife goes up
    # music: a soft 8-bit campfire lullaby (A minor, 2 s bars at the build speed), out for the wordless beat, back under line 13
    beat = 0.5; mel = [69, 72, 76, 72, 71, 74, 79, 74, 69, 72, 76, 81, 79, 76, 74, 71]; bass = [45, 45, 43, 43, 41, 41, 40, 40]
    def sq(m, d, v, dec=2.5):
        f = 440 * 2 ** ((m - 69) / 12); tt = s.T(d); x = np.sign(np.sin(2 * np.pi * f * tt)) * 0.6 + np.sin(2 * np.pi * f * tt) * 0.4
        return x * np.minimum(1, tt / 0.01) * np.exp(-tt * dec) * np.minimum(1, (d - tt) / 0.03) * v
    for b in range(int(DUR / beat) + 1):
        t0 = b * beat; put(MUS, sq(mel[b % 16], beat * 0.9, 0.012, 3.0), t0); put(MUS, sq(mel[b % 16] + 12, beat * 0.5, 0.003, 6.0), t0 + 0.02)
        if b % 2 == 0: put(MUS, sq(bass[(b // 2) % 8], beat * 1.9, 0.016, 1.2), t0)
    mus_g = (1 - mask(T_STOP[0], T_BOOM + 0.6, 0.25)) * (1 - 0.6 * mask(T0['07'] - 0.2, tend('08') + 0.3, 0.3))
    mus_g = mus_g * (1 - mask(T_SIGH[0] - 0.2, T_WHITE, 0.2)) + mask(T_LOOPF, DUR + 1, 0.05) * 0.0
    MUS = MUS * mus_g
    # death: far boom + low roar, then a short low YOU DIED sting
    tt = s.T(2.5); put(FX, s.filt_short(s.noise(2.5, 81), lo=25, hi=180) * np.exp(-tt * 1.6) * np.minimum(1, tt / 0.05), T_BOOM, 0.3)
    tt = s.T(1.6); put(FX, np.sin(2 * np.pi * (70 + 18 * np.sin(tt * 6)) * tt) * np.sin(np.pi * tt / 1.6) * (1 + 0.4 * s.filt_short(s.noise(1.6, 82), lo=20, hi=200) * 10), T_BOOM + 0.15, 0.06)
    for k, m in enumerate((52, 51, 47)): tone(T_BOOM + 0.15 + 0.22 * k, m, 0.9, 0.04, dec=2.5, harm=(1.0, 0.6, 0.4, 0.2))
    tone(T0['13'] + 0.1, 57, 2.0, 0.025, dec=1.2, harm=(1.0, 0.45, 0.2))                 # one soft note under "Get up, kid."
    for k, m in enumerate((76, 81, 84, 88)): tone(T_WHITE - 0.1 + k * 0.06, m, 0.6, 0.03, dec=5, harm=(1.0, 0.3))   # save chime on the flash
    if CTA.on: put(FX, cta.chime(sr), CTA.t0, 1.0)
    # voice
    NB = np.zeros(n); wins = []
    for k_, t0 in LINES:
        f_ = os.path.join(TTS_DIR, 'sp', f'{k_}.wav')
        if not os.path.exists(f_): continue
        a, ar = _sf.read(f_); a = a if a.ndim == 1 else a.mean(1)
        a = np.interp(np.arange(int(len(a) * sr / ar)) / sr, np.arange(len(a)) / ar, a); act = np.abs(a) > 0.02 * np.abs(a).max()
        a = a * (0.12 / np.sqrt((a[act] ** 2).mean())); put(NB, a, t0); wins.append((t0, t0 + len(a) / sr))
    g = duck_envelope(n, sr, wins, -7.0, 0.05, 0.25) if wins else np.ones(n)
    bed = BED * g + MUS * (0.6 + 0.4 * g); fx = FX * (0.6 + 0.4 * g)
    L = bed + fx; R_ = np.roll(bed, 700) + np.roll(fx, 200)
    pk = max(np.abs(L).max(), np.abs(R_).max()); gv = (pk * 1.6 / np.abs(NB).max()) if np.abs(NB).max() > 0 else 0.0
    s.L = L + NB * gv; s.R = R_ + NB * gv; s.reverb(0.12, length=1.4, decay=3.0)
    fi = np.clip(t / 0.008, 0, 1); s.L = s.L * fi; s.R = s.R * fi
    return s.save(path, peak=0.9)
if __name__ == '__main__' and os.environ.get('PART') == 'audio':
    print(build_audio(os.path.join(OUT, os.environ.get('AUDIO_NAME', 'save_point.wav')))); sys.exit()
if __name__ == '__main__' and os.environ.get('PART'):
    a, b = map(int, os.environ['PART'].split(':'))
    import subprocess
    p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W * S}x{H * S}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', os.path.join(OUT, f"{os.environ.get('PART_PREFIX', 'sp')}_{a:05d}.mp4")], stdin=subprocess.PIPE)
    vhs = post.VHS(W * S, H * S, S, grade='none', chroma=0, scan_dark=1.0, vignette=0.22, grain=0.9, band_period=1e9)
    for f in range(a, min(b, N)): p.stdin.write(vhs(frame_final(f / FPS), f, f / FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done', a, b); sys.exit()
