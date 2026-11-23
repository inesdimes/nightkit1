"""WHAT IF THE DRAGON WAS STEALING THE KING'S TAXES BACK? (Insert Disc 2, 23 Nov 2026) ~45 s build (x1.2 after), PS1 fantasy, 9:16.
Brief: briefs/dragon_taxes.md (written for Blender; Enes: always nightkit -> built with the HD figures, nightkit/hd.py).
Story additions approved by Enes (23 Nov): 1) frame-0 HUD "QUEST: SLAY THE DRAGON" paid off by "QUEST UPDATED - PROTECT THE VILLAGE";
2) wordless beat: the old woman finds her own sewn patch on a torn sack, strokes it, hugs the sack -> "That's our winter tax.";
3) wordless beat before the last lines: a village kid gets the first coin, waves at the dragon's shadow, the dragon dips a wing.
Format 3.0: constant camera, subject in the middle third, speaker-coloured subtitles, 270x480 + depth outline.

Asset lock: ASSET=dragon|cast|horse|props python examples/dragon_taxes.py -> test_dt_<asset>.png"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import numpy as np
from PIL import Image
from nightkit.engine import Renderer, Camera
from nightkit.zraster import zrender
from nightkit import post, look, hd

W, H, S = 270, 480, 4
PI = math.pi
V = np.array
def hsh(i, s=0): v = math.sin(i * 127.1 + s * 311.7) * 43758.5453; return v - math.floor(v)
def lerp(a, b, u): return a + (b - a) * u
def lerp3(a, b, u): return tuple(a[i] + (b[i] - a[i]) * u for i in range(len(a)))
def mixc(a, b, u): return tuple(int(round(x + (y - x) * max(0.0, min(1.0, u)))) for x, y in zip(a, b))
def bez(p0, p1, p2, p3, u):
    a = 1 - u; return a ** 3 * p0 + 3 * a * a * u * p1 + 3 * a * u * u * p2 + u ** 3 * p3

# ======================= cast (asset lock) =======================
KNIGHT = hd.spec(h=1.84, build=1.08, skin=(214, 170, 136), hair=(60, 44, 34), hair_style='short', eye=(70, 110, 150), helmet=None,
                 tunic=(150, 158, 172), tunic2=(122, 130, 146), skirt=0.26, pants=(112, 118, 130), boots=(74, 78, 90),
                 belt=(70, 50, 36), buckle=(210, 180, 90), gloves=(150, 156, 168), cloak=(36, 78, 176), cloak_len=1.05, collar=(186, 194, 206))
WOMAN = hd.spec(h=1.6, build=0.94, fem=1.0, skin=(224, 184, 156), hair=(206, 204, 200), hair_style='bun', eye=(90, 76, 60), brow=(170, 166, 160),
                tunic=(104, 66, 58), tunic2=(86, 54, 48), skirt=0.74, pants=(86, 54, 48), boots=(62, 46, 36), belt=(70, 50, 40),
                buckle=(120, 96, 70), cloak=(158, 136, 100), cloak_len=0.5, lip=(176, 120, 110))
CAPTAIN = hd.spec(h=1.82, build=1.12, skin=(206, 156, 124), hair=(40, 30, 26), beard=(46, 34, 28), eye=(60, 50, 40), helmet=(104, 106, 116),
                  tunic=(150, 34, 40), tunic2=(118, 26, 32), skirt=0.3, pants=(60, 50, 46), boots=(40, 30, 26), belt=(40, 30, 24),
                  buckle=(220, 180, 80), gloves=(60, 48, 42), cloak=(104, 22, 30), collar=(210, 172, 80))
SOLDIER = hd.spec(h=1.76, build=1.06, skin=(200, 154, 120), hair=(70, 50, 36), eye=(60, 60, 60), helmet=(124, 128, 138),
                  tunic=(126, 38, 42), tunic2=(100, 30, 34), skirt=0.26, pants=(66, 56, 50), boots=(44, 34, 28), detail=0.5)
VIL1 = hd.spec(h=1.76, build=1.04, skin=(210, 160, 122), hair=(90, 60, 36), hair_style='short', beard=(96, 64, 40), eye=(70, 80, 60),
               tunic=(112, 96, 64), tunic2=(92, 78, 52), skirt=0.24, pants=(80, 66, 50), boots=(60, 44, 32))
VIL2 = hd.spec(h=1.66, build=0.9, fem=1.0, skin=(232, 192, 162), hair=(120, 70, 40), hair_style='long', eye=(80, 110, 70),
               tunic=(70, 104, 76), tunic2=(56, 84, 62), skirt=0.62, pants=(56, 84, 62), boots=(70, 50, 36), belt=(90, 60, 40))
VIL3 = hd.spec(h=1.72, build=1.18, skin=(220, 170, 136), hair=(150, 140, 130), hair_style='bald', beard=(170, 164, 156), eye=(70, 70, 70),
               tunic=(140, 120, 96), tunic2=(116, 98, 78), sleeves='short', skirt=0.16, pants=(86, 70, 54), boots=(60, 44, 32), apron=(196, 186, 166))
KID = hd.spec(h=1.2, build=0.86, skin=(230, 186, 150), hair=(170, 110, 60), hair_style='messy', eye=(70, 100, 140),
              tunic=(70, 110, 170), tunic2=(56, 90, 140), skirt=0.18, pants=(110, 90, 66), boots=(80, 56, 40))

def knight(P):
    """the series Knight: HD human + plate pieces (pauldrons, breastplate, knee cops)"""
    Q = hd.human(KNIGHT, P); RW = P['_RW']; ch = P['_chest']; st = (178, 186, 200); dk = (128, 136, 152)
    for sd in (1, -1):
        c = ch + RW @ V((sd * 0.19, 0.075, -0.01))
        Q += hd.ellip(c, RW @ hd.Rz(-sd * 0.35), (0.1, 0.07, 0.1), 10, 5, st, v1=PI * 0.6, colfn=lambda i, j, cl: dk if i == 2 else st)
        kn = P['_' + ('r' if sd > 0 else 'l') + 'knee']; Q += hd.ellip(kn, RW, (0.06, 0.06, 0.065), 8, 4, st)
    Q += hd.ellip(ch + RW @ V((0, -0.02, 0.035)), RW, (0.17, 0.17, 0.1), 12, 6, st, keep=lambda c: c[2] > 0.0, colfn=lambda i, j, cl: dk if (j % 6 == 0) else st)
    Q += knight_helmet(P)
    return Q
def knight_helmet(P):
    """open-faced helmet that sits ABOVE the brows (23 Nov: the old brim covered the eyes and looked comic): dome, rim, cheek guards,
    neck guard, a gold ridge and the series' blue plume"""
    k = KNIGHT['h'] / 1.78; hc = P['_head']; RH = P['_RH']; rx, ry, rz = 0.09 * k, 0.116 * k, 0.103 * k
    st = (182, 190, 204); dk = (130, 138, 154); gold = (214, 184, 92); blue = (44, 88, 190)
    def L(x, y, z): return hc + RH @ V((x, y, z))
    Q = hd.ellip(L(0, 0.016 * k, -0.006 * k), RH, (rx * 1.15, ry * 1.0, rz * 1.13), 16, 6, st, v1=PI * 0.41, closed=False,
                 colfn=lambda i, j, cl: hd.shade(st, 1.08) if j % 4 == 0 else st)
    Q += hd.limb(L(0, 0.046 * k, -0.006 * k), L(0, 0.06 * k, -0.006 * k), rz * 1.17, rz * 1.15, dk, n=16, m=1, ref=RH @ V((0, 0, 1.0)), flat=0.9)
    for sd in (1, -1):
        Q += hd.bx(L(sd * rx * 1.1, -0.004 * k, -0.004 * k), RH @ hd.Rz(-sd * 0.1) @ hd.Ry(sd * 0.12), (0.008, 0.054 * k, 0.05 * k), st)
        Q += hd.bx(L(sd * rx * 1.12, 0.03 * k, 0.03 * k), RH, (0.006, 0.006, 0.006), gold)
    Q += hd.bx(L(0, -0.035 * k, -rz * 1.08), RH @ hd.Rx(0.35), (rx * 0.95, 0.045 * k, 0.008), dk)
    Q += hd.bx(L(0, ry * 1.0 + 0.016 * k, -0.01 * k), RH, (0.007, 0.012 * k, rz * 0.95), gold)
    sw = P.get('cape_sway', 0.0) * 0.4
    for i in range(5):                                                         # the plume: blue strands from the top towards the back
        a = L(0, ry + 0.02 * k, -0.02 * k - 0.012 * i); b = L(0.012 * (i - 2) + sw * 0.05, ry + 0.06 * k - 0.006 * i, -0.13 * k - 0.02 * i)
        c_ = L(0.02 * (i - 2) + sw * 0.08, ry - 0.02 * k - 0.01 * i, -0.2 * k - 0.025 * i)
        Q += hd.limb(a, b, 0.012, 0.016, blue if i % 2 else hd.shade(blue, 0.85), n=5, m=1) + hd.limb(b, c_, 0.016, 0.004, blue, n=5, m=1)
    return Q

# ======================= the dragon =======================
DR = dict(scale=(58, 92, 80), scale2=(44, 74, 64), belly=(186, 160, 108), belly2=(160, 136, 90), horn=(224, 214, 186), claw=(38, 34, 32),
          eye=(255, 176, 40), mem=(120, 58, 54), mem2=(96, 44, 44), spine=(150, 116, 74), mouth=(110, 30, 34), teeth=(236, 230, 210))
def _frame_pts(pts):
    """rotation-minimising frames (u, v) along a polyline (u starts towards local 'up')"""
    us, vs = [], []; up = V((0, 1.0, 0))
    for i in range(len(pts)):
        d = hd.nz(pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)])
        u = up - d * float(up @ d)
        if np.linalg.norm(u) < 1e-6: u = V((0, 0, 1.0)) - d * d[2]
        u = hd.nz(u); up = u; us.append(u); vs.append(np.cross(d, u))
    return us, vs
def tube(pts, radii, col, belly, n=14, flat=1.0, cap0=True, cap1=True, band=0):
    """scaled tube along pts; underside (local -u) in belly colour with plate bands"""
    us, vs = _frame_pts(pts)
    def cf(i, j):
        th = 2 * PI * j / n
        if math.cos(th) < -0.45: return belly if (i + band) % 2 == 0 else hd.shade(belly, 0.86)
        return col if (j + i) % 3 else hd.shade(col, 0.84)
    return hd.loft(pts, us, vs, [(r, r * flat) for r in radii], n, col, colfn=cf, cap0=cap0, cap1=cap1)

def dragon(P):
    """P: base, yaw, head (local point of the skull centre), hyaw, hpitch, jaw 0..1, claw 0..1 (right front paw opens + lifts),
    rpaw (local), wing 0 folded .. 1 spread, flap (rad), tail (sway), eye (glow 0..1), blink, lie (0 lying .. 1 standing tall)"""
    g = lambda k, d=None: P.get(k, d)
    base = V(g('base', (0, 0, 0)), float); Rb = hd.Ry(g('yaw', 0.0)) @ hd.Rx(-g('pitch', 0.0)) @ hd.Rz(g('roll', 0.0))
    def Wp(p): return base + Rb @ V(p, float)
    Q = []; lie = g('lie', 0.0); C = DR
    by = 1.15 + 0.5 * lie
    # ---- body
    bc = Wp((0, by, -1.2))
    Q += hd.ellip(bc, Rb @ hd.Rx(0.08), (1.25, 1.05, 2.1), 18, 11, C['scale'],
                  colfn=lambda i, j, cl: (C['belly'] if i % 2 else C['belly2']) if cl[1] < -0.55 else (C['scale'] if (i + j) % 3 else C['scale2']))
    # ---- tail: a curve back and round to the right, sways
    sw = g('tail', 0.0); fly = g('fly', False)
    tp = [V((0, by - 0.1, -3.0)), V((0.2 + sw * 0.4, 0.6, -5.0)), V((2.4 + sw, 0.35, -5.8)), V((3.6 + sw * 1.4, 0.25, -4.4))]
    if fly: tp = [V((0, by - 0.05, -3.0)), V((0.35 + sw * 0.3, by + 0.05, -4.4)), V((-0.35 + sw * 0.8, by + 0.4, -5.8)), V((sw * 1.2, by + 0.75, -7.2))]
    pts = [Wp(bez(*tp, u)) for u in np.linspace(0, 1, 16)]
    Q += tube(pts, [0.62 * (1 - u) ** 1.15 + 0.03 for u in np.linspace(0, 1, 16)], C['scale'], C['belly'], n=12)
    for i in range(1, 15, 2):                                                  # tail spikes
        u = i / 15; c = Wp(bez(*tp, u)); r = 0.62 * (1 - u) ** 1.15 + 0.03
        Q.append(hd.face([c + V((0, r * 0.9, -0.14)), c + V((0, r * 0.9 + 0.12 + 0.2 * (1 - u), 0.02)), c + V((0, r * 0.9, 0.14))], C['spine']))
    # ---- neck: bezier from the shoulders to the head
    hp = V(g('head', (0.0, 1.6, 2.4)), float)
    sh = V((0, by + 0.55, 0.55)); n1 = sh + V((0, 0.9, 0.55)); n2 = hp + V((0, 0.1, -1.0))
    pts = [Wp(bez(sh, n1, n2, hp + V((0, 0, -0.25)), u)) for u in np.linspace(0, 1, 11)]
    Q += tube(pts, [0.78 - 0.46 * u for u in np.linspace(0, 1, 11)], C['scale'], C['belly'], n=16, flat=0.92, cap1=False)
    for i in range(1, 11):                                                     # neck + back ridge
        a = pts[i - 1]; b = pts[i]; d = hd.nz(b - a); u_ = hd.nz(V((0, 1.0, 0)) - d * d[1]); r = 0.78 - 0.46 * i / 10
        c = (a + b) / 2 + u_ * r * 0.92; Q.append(hd.face([c - d * 0.12, c + u_ * (0.16 + 0.1 * (1 - i / 10)) - d * 0.02, c + d * 0.12], C['spine']))
    for i in range(8):
        c = Wp((0, by + 1.02 - 0.05 * i, 0.2 - 0.42 * i)); Q.append(hd.face([c + Rb @ V((0, 0, 0.16)), c + Rb @ V((0, 0.28, 0)), c + Rb @ V((0, 0, -0.16))], C['spine']))
    # ---- head
    RH = Rb @ hd.Ry(g('hyaw', 0.0)) @ hd.Rx(-g('hpitch', 0.0)); hc = Wp(hp)
    def HP(x, y, z): return hc + RH @ V((x, y, z))
    Q += hd.ellip(hc, RH, (0.44, 0.42, 0.5), 16, 10, C['scale'], deform=lambda p: V((p[0] * (1 - 0.2 * max(0, p[1]) / 0.42), p[1] * (0.85 if p[1] > 0 else 1.0), p[2])),
                  colfn=lambda i, j, cl: C['belly'] if cl[1] < -0.22 else (C['scale'] if (i + j) % 3 else C['scale2']))
    # upper jaw / snout: a CLOSED, flattened tube (23 Nov: the open half-tube read as a pipe in close-ups)
    SL = 0.95; n_ = 7; ss = np.linspace(0, 1, n_)
    def sn_w(s): return 0.33 - 0.13 * s
    def sn_h(s): return 0.2 - 0.07 * s
    def sn_y(s): return 0.02 - 0.02 * s
    tipk = ((0.05, 0.82), (0.09, 0.5), (0.105, 0.15))                         # rounded nose tip
    cs = [HP(0, sn_y(s), 0.12 + (SL - 0.12) * s) for s in ss] + [HP(0, sn_y(1) - 0.01 * j, SL + dz) for j, (dz, _) in enumerate(tipk)]
    rr = [(sn_w(s), sn_h(s)) for s in ss] + [(sn_w(1) * f, sn_h(1) * f) for _, f in tipk]; us = [RH @ V((1.0, 0, 0))] * len(cs); vs = [RH @ V((0, 1.0, 0))] * len(cs)
    Q += hd.loft(cs, us, vs, rr, 16, C['scale'], cap0=False, cap1=True,
                 colfn=lambda i, j: (C['belly'] if 9 <= j <= 15 else (C['scale2'] if (i + j) % 3 == 0 else C['scale'])))
    for i in range(3):                                                         # nose ridge
        s = 0.25 + 0.25 * i; Q += hd.ellip(HP(0, sn_y(s) + sn_h(s) * 0.92, 0.12 + (SL - 0.12) * s), RH, (0.06, 0.03, 0.09), 6, 3, C['scale2'])
    # lower jaw: a closed tube on a hinge that sits under the snout when shut
    ja = 0.5 * g('jaw', 0.0); hinge = V((0, -0.1, 0.05)); RJ = RH @ hd.Rx(ja); JL = SL - 0.08
    def JP(x, y, z): return hc + RH @ hinge + RJ @ V((x, y, z))
    def jw(s): return 0.29 - 0.12 * s
    def jh(s): return 0.1 - 0.035 * s
    cs = [JP(0, -0.06, 0.05 + (JL - 0.05) * s) for s in ss] + [JP(0, -0.06, JL + dz) for dz, _ in tipk[:2]]
    rr = [(jw(s), jh(s)) for s in ss] + [(jw(1) * f, jh(1) * f) for _, f in tipk[:2]]; us = [RJ @ V((1.0, 0, 0))] * len(cs); vs = [RJ @ V((0, 1.0, 0))] * len(cs)
    Q += hd.loft(cs, us, vs, rr, 14, C['belly'], cap0=True, cap1=True,
                 colfn=lambda i, j: C['belly2'] if (i % 2 or j < 7) else C['belly'])
    if ja > 0.04:                                                              # the inside of the mouth shows only when it opens
        q = hd.face([HP(-0.26, sn_y(0.1) - sn_h(0.1) * 0.85, 0.2), HP(-0.15, sn_y(0.95) - sn_h(0.95) * 0.85, SL - 0.06), HP(0.15, sn_y(0.95) - sn_h(0.95) * 0.85, SL - 0.06), HP(0.26, sn_y(0.1) - sn_h(0.1) * 0.85, 0.2)], C['mouth'])
        Q += [q] if q else []
        q = hd.face([JP(-0.24, -0.06 + jh(0.1) * 0.9, 0.12), JP(-0.13, -0.06 + jh(0.95) * 0.9, JL - 0.06), JP(0.13, -0.06 + jh(0.95) * 0.9, JL - 0.06), JP(0.24, -0.06 + jh(0.1) * 0.9, 0.12)], C['mouth'])
        Q += [q] if q else []
    # teeth: upper fangs on the snout's lower edge, lower teeth on the jaw's upper edge (short, so the closed mouth shows a neat row)
    for i in range(5):
        s = 0.25 + 0.17 * i
        for sd in (1, -1):
            x = sd * sn_w(s) * 0.82; b = HP(x, sn_y(s) - sn_h(s) * 0.55, 0.12 + (SL - 0.12) * s); ln = 0.075 + (0.05 if i == 1 else 0.0)
            Q.append(hd.face([b + RH @ V((0, 0, -0.03)), b + RH @ V((0, -ln, 0)), b + RH @ V((0, 0, 0.03))], C['teeth']))
            if i < 4:
                sj = 0.2 + 0.18 * i; bj = JP(sd * jw(sj) * 0.8, -0.06 + jh(sj) * 0.55, 0.05 + (JL - 0.05) * sj)
                Q.append(hd.face([bj + RJ @ V((0, 0, -0.025)), bj + RJ @ V((0, 0.06, 0)), bj + RJ @ V((0, 0, 0.025))], C['teeth']))
    # eyes (glowing, slit pupils), brow ridges, nostrils
    eg = g('eye', 1.0); bl = g('blink', 0.0)
    for sd in (1, -1):
        ec = HP(sd * 0.3, 0.1, 0.3); n = hd.nz(RH @ V((sd * 0.85, 0.15, 0.5)))
        if bl < 0.7:
            for q in hd.ellip(ec, RH @ hd.Ry(sd * 0.9), (0.06, 0.046 * (1 - bl), 0.04), 8, 4, mixc((90, 60, 30), C['eye'], eg)):
                q['emit'] = eg > 0.3; Q.append(q)
            Q += hd.decal(ec + n * 0.036, n, RH @ V((0, 1.0, 0)), 0.014, 0.06 * (1 - bl), (20, 12, 8), lift=0.006)
        else:
            Q += hd.ellip(ec, RH @ hd.Ry(sd * 0.9), (0.078, 0.058, 0.052), 8, 4, C['scale2'])
        Q += hd.bx(HP(sd * 0.28, 0.2, 0.3), RH @ hd.Rz(sd * 0.35) @ hd.Rx(-0.15), (0.13, 0.035, 0.12), C['scale2'])
        Q += hd.decal(HP(sd * 0.09, 0.115, SL - 0.1), hd.nz(RH @ V((sd * 0.3, 1.0, 0.4))), RH @ V((0, 0, 1.0)), 0.07, 0.045, (24, 20, 18), lift=0.01)
        # horns: up and back from the top of the skull, curving
        h0 = HP(sd * 0.2, 0.3, -0.12); h1 = h0 + RH @ V((sd * 0.12, 0.34, -0.2)); h2 = h1 + RH @ V((sd * 0.06, 0.18, -0.36)); h3 = h2 + RH @ V((0, -0.02, -0.3))
        hcol = (196, 180, 140)
        Q += hd.limb(h0, h1, 0.1, 0.075, hcol, n=8, m=1) + hd.limb(h1, h2, 0.075, 0.04, hd.shade(hcol, 0.9), n=8, m=1) + hd.limb(h2, h3, 0.04, 0.008, hd.shade(hcol, 0.78), n=6, m=1)
        # cheek frills
        for k in range(3):
            c = HP(sd * 0.38, -0.05 - 0.06 * k, -0.05 - 0.08 * k)
            Q.append(hd.face([c, c + RH @ V((sd * 0.2, 0.06 - 0.04 * k, -0.22)), c + RH @ V((0, -0.06, -0.1))], C['spine']))
    # ---- legs (front: ik; the right paw is the claw that opens)
    claw = g('claw', 0.0)
    for sd, key in ((1, 'r'), (-1, 'l')):
        s0 = Wp((sd * 0.95, by + 0.05, 0.25))
        paw = V(g(key + 'paw', (sd * 1.05, 0.12, 1.55)), float); pw = Wp(paw)
        if key == 'r': pw = pw + V((0, 0.35 * claw, 0))
        el, wr = hd.ik2(s0, pw, 1.0, 1.0, Rb @ V((sd * 0.3, 0.2, -1.0)))
        Q += hd.ellip(s0, Rb, (0.42, 0.5, 0.5), 10, 6, C['scale'])
        Q += tube([s0 + (el - s0) * u for u in np.linspace(0, 1, 4)], [0.36, 0.33, 0.3, 0.26], C['scale'], C['belly'], n=10, cap0=False)
        Q += hd.ellip(el, Rb, (0.25, 0.25, 0.25), 8, 5, C['scale2'])
        Q += tube([el + (wr - el) * u for u in np.linspace(0, 1, 4)], [0.24, 0.2, 0.18, 0.17], C['scale'], C['belly'], n=10, cap0=False)
        Q += hd.ellip(wr + V((0, -0.02, 0)), Rb, (0.26, 0.14, 0.3), 10, 5, C['scale2'])
        op = claw if key == 'r' else 0.0
        for f in range(4):                                                     # talons: curl down onto the stone; open = lift + spread
            a = (-0.6 + 0.4 * f) * (1 + 0.6 * op)
            dirf = hd.nz(Rb @ V((math.sin(a), 0.0, math.cos(a))))
            p0 = wr + dirf * 0.22 + V((0, -0.02, 0)); p1 = p0 + dirf * 0.18 + V((0, 0.05 * op - 0.02, 0)); p2 = p1 + dirf * (0.08 + 0.06 * op) + V((0, -0.12 * (1 - op) + 0.06 * op, 0))
            Q += hd.limb(p0, p1, 0.065, 0.05, C['scale'], n=6, m=1) + hd.limb(p1, p2, 0.045, 0.006, C['claw'], n=6, m=1)
        # hind leg haunch + foot
        hc_ = Wp((sd * 1.05, by - 0.2, -2.3)); Q += hd.ellip(hc_, Rb, (0.5, 0.75, 0.85), 10, 6, C['scale'], colfn=lambda i, j, cl: C['scale2'] if j % 3 == 0 else C['scale'])
        ft = Wp((sd * 0.85, by - 0.75, -3.0)) if fly else Wp((sd * 1.25, 0.12, -1.6)); Q += hd.ellip(ft, Rb, (0.25, 0.13, 0.35), 8, 4, C['scale2'])
        for f in range(3):
            a = -0.35 + 0.35 * f; dirf = Rb @ V((math.sin(a), 0, math.cos(a))); p0 = ft + dirf * 0.3
            Q += hd.limb(p0, p0 + dirf * 0.14 + V((0, -0.1, 0)), 0.045, 0.006, C['claw'], n=5, m=1)
    # ---- wings: arm + 4 fingers + membranes. fold 0 = folded along the back, 1 = spread; flap = rotation about the body axis
    wg = g('wing', 0.0); fl = g('flap', 0.0)
    for sd in (1, -1):
        root = V((sd * 0.75, by + 0.85, -0.35)); Rf = hd.Rz(sd * fl)
        wrist_f = root + V((sd * 0.55, 0.65, -1.2)); wrist_s = root + V((sd * 2.8, 1.5, 0.2))
        wrist = root + Rf @ (lerp3(wrist_f, wrist_s, wg) - root); wrist = V(wrist)
        elbow = root + Rf @ (V(lerp3(root + V((sd * 0.45, 0.85, -0.3)), root + V((sd * 1.4, 0.9, 0.35)), wg)) - root)
        tips = []
        for f in range(4):
            tf = wrist_f + V((sd * (0.15 + 0.1 * f), -0.55 - 0.2 * f, -1.0 - 0.45 * f))
            a = 0.35 - 0.42 * f; ts = wrist_s + V((sd * 2.6 * math.cos(a), 2.4 * math.sin(a) - 0.2, -0.7 - 0.55 * f))
            tips.append(root + Rf @ (V(lerp3(tf, ts, wg)) - root))
        Wr, El = Wp(wrist), Wp(elbow); Rt = Wp(root)
        Q += hd.limb(Rt, El, 0.16, 0.12, C['scale'], n=8, m=1) + hd.limb(El, Wr, 0.12, 0.08, C['scale'], n=8, m=1) + hd.ellip(Wr, Rb, (0.1, 0.1, 0.1), 6, 4, C['scale2'])
        Q += hd.limb(Wr, Wr + (Wr - El) * 0.18, 0.06, 0.01, C['claw'], n=5, m=1)
        T = [Wp(tp_) for tp_ in tips]
        for f in range(4): Q += hd.limb(Wr, T[f], 0.055, 0.015, C['scale2'], n=5, m=2)
        trail = [Wr] + T + [Wp(root + V((0, -0.35, -1.6 - 0.3 * wg)))]
        for f in range(len(trail) - 2):                                        # membrane fans (two-sided)
            a_, b_ = trail[f + 1], trail[f + 2]; mid = (a_ + b_) / 2 + (Wr - (a_ + b_) / 2) * 0.12
            col = C['mem'] if f % 2 == 0 else C['mem2']
            for q in (hd.face([Wr, a_, mid], col), hd.face([Wr, mid, b_], hd.shade(col, 0.92))): Q += [q] if q else []
        q = hd.face([Wr, El, Rt, trail[-1]], C['mem2']); Q += [q] if q else []
    return [q for q in Q if q is not None]

# ======================= the horse (+ rider) =======================
def horse(P, col=(96, 64, 44), mane=(36, 28, 24), saddle=(110, 30, 36)):
    """P: base, yaw, gallop (phase, None = standing), rear 0..1, head (nod). Returns faces + P['_saddle'] (world), P['_stirrup_r/l'], P['_RB']"""
    g = lambda k, d=None: P.get(k, d)
    base = V(g('base', (0, 0, 0)), float); rear = g('rear', 0.0); gp = g('gallop')
    Ry_ = hd.Ry(g('yaw', 0.0)); Rr = hd.Rx(-0.75 * rear); Rb = Ry_ @ Rr
    piv = V((0, 0.1, -0.6))                                                     # rears up around the hind feet
    bob = 0.06 * math.sin(2 * gp) if gp is not None else 0.0
    def Wp(p): return base + Ry_ @ (piv + Rr @ (V(p, float) - piv)) + V((0, bob, 0))
    Q = []; dk = hd.shade(col, 0.82)
    Q += hd.ellip(Wp((0, 1.22, 0)), Rb, (0.33, 0.36, 0.82), 14, 8, col, colfn=lambda i, j, cl: dk if cl[1] < -0.25 else col)
    Q += hd.ellip(Wp((0, 1.28, -0.55)), Rb, (0.34, 0.36, 0.38), 10, 6, col)
    Q += hd.ellip(Wp((0, 1.3, 0.5)), Rb, (0.32, 0.38, 0.36), 10, 6, col)
    nd = g('nod', 0.0)
    n0 = Wp((0, 1.42, 0.68)); n1 = Wp((0, 1.92 - 0.1 * nd, 1.0 + 0.06 * nd)); hdp = Wp((0, 1.66 - 0.15 * nd, 1.38 + 0.05 * nd))
    Q += hd.limb(n0, n1, 0.22, 0.14, col, n=10, m=2, ref=Rb @ V((0, 0, 1.0)), flat=0.75)
    Q += hd.limb(n1 - (n1 - n0) * 0.05, hdp, 0.13, 0.075, col, n=10, m=2, ref=Rb @ V((0, 1.0, 0)), flat=0.7)
    Q += hd.ellip(hdp, Rb, (0.07, 0.07, 0.08), 6, 4, dk)
    for sd in (1, -1):
        Q += hd.limb(n1 + Rb @ V((sd * 0.05, 0.05, -0.04)), n1 + Rb @ V((sd * 0.07, 0.2, -0.08)), 0.03, 0.005, col, n=5, m=1)
        e = n1 + (hdp - n1) * 0.25 + Rb @ V((sd * 0.1, 0.02, 0)); Q += hd.decal(e, Rb @ V((sd * 1.0, 0, 0.2)), V((0, 1.0, 0)), 0.03, 0.025, (16, 12, 10), lift=0.01)
    for i in range(7):                                                          # mane
        u = i / 6; c = n0 + (n1 - n0) * u + Rb @ V((0, 0.16 - 0.04 * u, -0.06))
        Q.append(hd.face([c + Rb @ V((0, 0, -0.08)), c + Rb @ V((0, 0.12, -0.06)), c + Rb @ V((0, 0.0, 0.08)), c + Rb @ V((0, -0.14, -0.04))], mane))
    ts = Wp((0, 1.38, -0.92)); tsw = 0.15 * math.sin((gp or 0.0) * 2)
    Q += hd.limb(ts, ts + Rb @ V((tsw, -0.55, -0.25)), 0.07, 0.03, mane, n=6, m=2)
    # legs
    for sd, zz, ph in ((1, 0.55, 0.0), (-1, 0.55, 0.6), (1, -0.6, PI), (-1, -0.6, PI + 0.6)):
        hip = Wp((sd * 0.2, 1.05, zz)); front = zz > 0
        if gp is not None:
            a = gp + ph; fz = 0.42 * math.sin(a); up = max(0.0, math.cos(a)) * 0.3
            ft = Wp((sd * 0.2, 0.06 + up, zz + fz))
        else:
            ft = Wp((sd * 0.2, 0.06, zz + 0.02))
            if rear > 0 and front: ft = Wp((sd * 0.2, 0.06 + 0.5 * rear, zz + 0.35 * rear))
            if rear > 0 and not front: ft = base + V((0, 0.06, 0)) + hd.Ry(g('yaw', 0.0)) @ V((sd * 0.2, 0, zz))
        kn, an = hd.ik2(hip, ft, 0.55, 0.52, Rb @ V((0, 0, 1.0 if not front else -1.0)) if not front else Rb @ V((0, 0, -1.0)))
        Q += hd.limb(hip, kn, 0.12, 0.07, col, n=8, m=1) + hd.limb(kn, an, 0.055, 0.045, col, n=8, m=1)
        Q += hd.limb(an, an - V((0, 0.07, 0)), 0.06, 0.065, (40, 32, 28), n=8, m=1)
    sd_c = Wp((0, 1.6, 0.05)); Q += hd.bx(sd_c, Rb, (0.2, 0.05, 0.26), (70, 44, 30))
    for sd in (1, -1): Q += hd.bx(Wp((sd * 0.34, 1.42, 0.05)), Rb @ hd.Rz(sd * 0.25), (0.012, 0.17, 0.24), saddle)
    P['_saddle'] = sd_c + V((0, 0.05, 0)); P['_RB'] = Rb
    P['_stir_r'] = Wp((0.34, 0.92, 0.12)); P['_stir_l'] = Wp((-0.34, 0.92, 0.12))
    return Q
def rider(S_, Ph, P):
    """seat a human spec on a horse pose Ph (after horse()); P = extra human pose keys"""
    k = S_['h'] / 1.78; yaw = Ph.get('yaw', 0.0)
    base = Ph['_saddle'] - V((0, 0.93 * k - 0.04, 0)); Q_ = dict(base=tuple(base), yaw=yaw, rf_w=tuple(Ph['_stir_r']), lf_w=tuple(Ph['_stir_l']),
                                                                 rkpole=(0.2, 0.1, 1.0), lkpole=(-0.2, 0.1, 1.0), rfdir=tuple(hd.Ry(yaw) @ V((0, 0, 1.0))), lfdir=tuple(hd.Ry(yaw) @ V((0, 0, 1.0))))
    Q_.update(P); return Q_

# ======================= props =======================
SACK = (152, 126, 86); SACK2 = (128, 104, 70)
def sack(base, R=None, s=1.0, torn=False, patch=False, seal=True, slump=0.0):
    """burlap tax sack (lathe with a tied neck); seal = red painted circle on the front; patch = the old woman's own stitched blue patch"""
    R = np.eye(3) if R is None else R; b = V(base, float)
    prof = [(0.0, 0.0), (0.16 * s, 0.01 * s), (0.21 * s, 0.1 * s), (0.2 * s * (1 + 0.3 * slump), 0.22 * s * (1 - 0.35 * slump)), (0.12 * s, 0.32 * s * (1 - 0.4 * slump)), (0.05 * s, 0.36 * s * (1 - 0.4 * slump))]
    Q = hd.lathe(b, R, prof, 10, SACK, colfn=lambda i, j: SACK2 if (j + i) % 3 == 0 else SACK)
    if not torn:
        tp = 0.36 * s * (1 - 0.4 * slump)
        Q += hd.lathe(b + R @ V((0, tp, 0)), R, [(0.05 * s, 0), (0.07 * s, 0.04 * s), (0.03 * s, 0.07 * s)], 8, SACK2)
        Q += hd.limb(b + R @ V((0, tp - 0.005, 0)), b + R @ V((0, tp + 0.01, 0)), 0.055 * s, 0.055 * s, (90, 64, 40), n=8, m=1)
    n = R @ V((0, 0, 1.0)); up = R @ V((0, 1.0, 0))
    if seal:
        Q += hd.poly_decal(b + R @ V((0, 0.16 * s, 0.205 * s)), n, up, [(0.07 * s * math.cos(a), 0.07 * s * math.sin(a)) for a in np.linspace(0, 2 * PI, 10)[:-1]], (170, 34, 30), lift=0.01)
        Q += hd.decal(b + R @ V((0, 0.16 * s, 0.205 * s)), n, up, 0.06 * s, 0.014 * s, (232, 210, 160), lift=0.013)
    if patch:
        pc = b + R @ hd.Ry(0.9) @ V((0, 0.12 * s, 0.205 * s)); pn = R @ hd.Ry(0.9) @ V((0, 0, 1.0))
        Q += hd.decal(pc, pn, up, 0.1 * s, 0.09 * s, (70, 96, 150), lift=0.01)
        for k in range(5):
            y = -0.04 + 0.02 * k; Q += hd.decal(pc + up * y * s, pn, up, 0.1 * s, 0.006 * s, (210, 200, 160), lift=0.012)
    if torn:
        Q += hd.poly_decal(b + R @ V((0.0, 0.3 * s, 0.1 * s)), R @ V((0, 1.0, 0.4)), R @ V((0, 0, 1.0)), [(-0.06 * s, -0.03 * s), (0.0, 0.05 * s), (0.07 * s, -0.02 * s), (0.02 * s, -0.06 * s)], (30, 22, 14), lift=0.01)
    return Q
def coin(c, R=None, s=1.0, col=(246, 204, 84)):
    R = np.eye(3) if R is None else R
    return hd.lathe(V(c, float), R, [(0.026 * s, 0), (0.026 * s, 0.006 * s)], 7, col, colfn=lambda i, j: hd.shade(col, 1.1) if i == 1 else col)
def gold_pile(c, r, h, seed=0, n=26):
    c = V(c, float); Q = hd.lathe(c, np.eye(3), [(r, 0), (r * 0.75, h * 0.4), (r * 0.35, h * 0.85), (0.02, h)], 12, (226, 178, 62),
                                     colfn=lambda i, j: (250, 210, 90) if (i + j) % 3 == 0 else (226, 178, 62))
    for i in range(n):
        a = 2 * PI * hsh(i, seed); rr = r * (0.3 + 0.9 * hsh(i, seed + 1)); y = max(0.0, h * (1 - rr / r)) * 0.9
        Q += coin(c + V((rr * math.cos(a), y + 0.005, rr * math.sin(a))), hd.Rx(0.4 * (hsh(i, seed + 2) - 0.5)) @ hd.Rz(0.4 * (hsh(i, seed + 3) - 0.5)))
    return Q
def torch_faces(c, t, k=1.0, seed=0, stick=True):
    """hand / wall torch: stick + flickering flame (k = flame size, 0 = out)"""
    c = V(c, float); Q = []
    if stick: Q += hd.limb(c - V((0, 0.45, 0)), c, 0.025, 0.035, (70, 48, 30), n=6, m=1) + hd.lathe(c - V((0, 0.06, 0)), np.eye(3), [(0.045, 0), (0.05, 0.07)], 7, (50, 36, 26))
    if k > 0.02:
        for i in range(5):
            a = 2 * PI * i / 5 + seed; hgt = k * (0.15 + 0.06 * hsh(i, seed)) * (0.8 + 0.2 * math.sin(t * (11 + i) + i + seed)); w = 0.075 * k
            col = (255, 220, 110) if i % 2 == 0 else (255, 140, 50)
            for ang in (0.0, PI / 2):
                dx, dz = w * math.cos(a + ang), w * math.sin(a + ang)
                q = hd.face([c + V((-dx, 0.0, -dz)), c + V((dx, 0.0, dz)), c + V((0.02 * math.sin(t * 7 + i), hgt, 0))], col, emit=True); Q += [q] if q else []
    return Q

# ======================= asset lock preview =======================
def shot(layers, cam_pos, tgt, fov=40, lights=None, fog=(30, 30, 40), amb=0.45):
    R = Renderer(W, H, fog=fog); cam = Camera.look(cam_pos, tgt)
    L = lights or [((1.5, 2.5, -2.0), (255, 226, 190), 2.0), ((-2.5, 1.5, 1.0), (150, 170, 230), 0.8)]
    img, vi, zb = zrender(R, cam, layers, L, fov=fov, fog_start=10, fog_end=60, ambient=amb, return_z=True)
    a = look.outline(np.asarray(img).astype(np.float32), zb)
    return post.ps1(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), levels=6)

ASSET = os.environ.get('ASSET')
if ASSET and __name__ == '__main__':
    import time
    ims = []; floor = hd.bx((0, -0.05, 0), np.eye(3), (12, 0.05, 12), (70, 64, 58))
    if ASSET == 'dragon':
        for pose, cp, tg, fv in ((dict(jaw=0.2, claw=0.0), (5.5, 3.2, 6.5), (0, 1.6, 0), 50), (dict(jaw=0.8, claw=1.0, hyaw=0.3), (-1.2, 1.7, 4.6), (0.2, 1.5, 2.0), 46),
                                 (dict(wing=1.0, lie=0.6, head=(0, 2.6, 2.2), hpitch=0.3, jaw=0.4), (0.0, 3.0, 11), (0, 2.6, 0), 60), (dict(wing=0.5, flap=0.4), (-7, 4, -3), (0, 1.8, -0.8), 55)):
            t0 = time.time(); Q = dragon(dict(base=(0, 0, 0), **pose)); bt = time.time() - t0
            t0 = time.time(); ims.append(shot([floor, Q], cp, tg, fv)); print('faces', len(Q), 'build', round(bt, 2), 'render', round(time.time() - t0, 2))
    elif ASSET == 'cast':
        xs = [-2.4, -1.6, -0.8, 0.0, 0.8, 1.6, 2.4]; Q = []
        for i, (sp, x) in enumerate(zip((KNIGHT, WOMAN, CAPTAIN, SOLDIER, VIL1, VIL2, VIL3), xs)):
            P = dict(base=(x, 0, 0), yaw=PI, eyes='open', mouth='neutral')
            Q += knight(P) if sp is KNIGHT else hd.human(sp, P)
        Q += hd.human(KID, dict(base=(3.1, 0, 0), yaw=PI, mouth='smile'))
        ims.append(shot([floor, Q], (0.3, 1.2, -7.0), (0.3, 0.95, 0), 44))
        P = dict(base=(0, 0, 0), yaw=PI + 0.3); Qk = knight(P); ims.append(shot([floor, Qk], (-0.4, 1.7, -1.6), (0, 1.5, 0), 34))
        P = dict(base=(0, 0, 0), yaw=PI - 0.3, eyes='sad', brow=-0.6); Qw = hd.human(WOMAN, P); ims.append(shot([floor, Qw], (0.3, 1.45, -1.3), (0, 1.35, 0), 34))
    elif ASSET == 'horse':
        Ph = dict(base=(0, 0, 0), yaw=PI * 0.5); Q = horse(Ph); Q += hd.human(CAPTAIN, rider(CAPTAIN, Ph, dict(rh=(0.3, 1.5, 0.5), rgrip=0.4, mouth='open', brow=0.8)))
        ims.append(shot([floor, Q], (-1.0, 1.9, -4.8), (0, 1.5, 0), 44))
        Ph2 = dict(base=(0, 0, 0), yaw=PI * 0.5, gallop=1.0); Q2 = horse(Ph2, col=(60, 50, 44)) + hd.human(SOLDIER, rider(SOLDIER, Ph2, dict()))
        ims.append(shot([floor, Q2], (0.5, 1.6, -5.0), (0, 1.3, 0), 44))
        Ph3 = dict(base=(0, 0, 0), yaw=PI * 0.5, rear=1.0); Q3 = horse(Ph3, col=(130, 120, 110)); ims.append(shot([floor, Q3], (0.5, 1.6, -5.0), (0, 1.3, 0), 44))
    elif ASSET == 'props':
        Q = sack((-0.3, 0, 0), patch=True) + sack((0.2, 0, 0.1), hd.Ry(-0.4), torn=True, slump=0.6) + gold_pile((0.0, 0, 0.6), 0.35, 0.22) + torch_faces((0.6, 0.6, 0.3), 0.3)
        Q += coin((0.2, 0.0, -0.3)); ims.append(shot([floor, Q], (0.2, 0.9, -1.6), (0.1, 0.2, 0.2), 40))
    out = Image.new('RGB', (W * S * len(ims) // 2, H * S // 2))
    for i, im in enumerate(ims): out.paste(im.resize((W * S // 2, H * S // 2), Image.NEAREST), (i * W * S // 2, 0))
    out.save(os.environ.get('TEST_OUT', f'test_dt_{ASSET}.png')); print('written')
    sys.exit()

# =====================================================================================================================
#                                                      THE FILM
# =====================================================================================================================
import json
from PIL import ImageDraw
from nightkit import motion, font
from nightkit.audio import Sound, duck_envelope, soft_fire
OUT = 'out'; os.makedirs(OUT, exist_ok=True)
FPS = 24
TTS_DIR = os.environ.get('TTS_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tts'))
sm = motion.smooth
def seg01(t, a, b): return max(0.0, min(1.0, (t - a) / (b - a))) if b > a else (1.0 if t >= b else 0.0)
def win(t, a, b, r=0.25): return sm(seg01(t, a, a + r)) * (1 - sm(seg01(t, b - r, b)))
def ang_to(p, q): return math.atan2(q[0] - p[0], q[2] - p[2])
def angl(a, b, u):
    d = (b - a + PI) % (2 * PI) - PI; return a + d * u

# ======================= voice timings (tools/tts/dt.py) =======================
SCR = json.load(open(os.path.join(TTS_DIR, 'dt', 'script.json')))
KEYS = ['%02d' % i for i in range(1, 16)]
EXTRA = {'01': 2.7, '02': 0.55, '03': 0.35, '04': 0.45, '05': 0.3, '06': 0.5, '07': 0.25, '08': 0.4, '09': 0.35, '10': 0.45,
         '11': 1.75, '12': 0.55, '13': 2.4, '14': 0.35, '15': 0.0}
def _lines():
    t = 0.35; out = []
    for k in KEYS: out.append((k, round(t, 3))); t += SCR['dur'][k] + EXTRA[k]
    return out
LINES = _lines(); T0 = dict(LINES)
def tend(k): return T0[k] + SCR['dur'][k]
def ws(k, i): return T0[k] + SCR['sent'][k][i][0]
def we(k, i): return T0[k] + SCR['sent'][k][i][1]
T_POST = tend('15') + 0.7                       # LOOP: the king posts the quest again ...
T_LOOP = T_POST + 1.25                          # ... and we are back in the cave, the moment before frame 0
DUR = round(T_LOOP + 0.75, 2); N = int(round(DUR * FPS))
T_PATCH = tend('01') + 0.15                       # cut to the woman and her patch
T_OUT = T0['07'] - 0.15                           # the cave mouth, the night road
T_CAP = T0['08'] - 0.12                           # the captain
T_STAND = T0['09'] - 0.1                          # inside: the knight decides
T_WB = tend('11') + 0.15                          # outside: the wingbeat
T_GUST = T_WB + 0.95                              # every torch dies
T_DAWN = tend('12') + 0.3
T_KID = tend('13') + 0.1                          # the kid looks up
T_SKY = tend('13') + 1.25
T_FIN = T0['15'] - 0.25
def scene(t):
    for nm, a in (('loop', T_LOOP), ('fin', T_FIN), ('sky', T_SKY), ('dawn', T_DAWN), ('wing', T_WB), ('stand', T_STAND), ('capt', T_CAP), ('road', T_OUT)):
        if t >= a: return nm
    return 'cave'
CUTS = [0.0, T_PATCH, T0['03'] - 0.1, T0['04'] - 0.75, T0['05'] - 0.1, T0['06'] - 0.1, T_OUT, T_CAP, T_STAND, T0['10'] - 0.1, T0['11'] - 0.5,
        T_WB, T_GUST + 0.5, T_DAWN, T_KID, T_SKY, T_FIN]

def talking(t, key):
    if key not in T0: return None
    for a, b, _ in SCR['sent'][key]:
        if T0[key] + a <= t < T0[key] + b: return 'open' if (t * 7.3 + 0.2 * math.sin(t * 13)) % 1.0 < 0.55 else 'neutral'
    return None
def jaw_talk(t, key):
    if key not in T0: return 0.0
    for a, b, _ in SCR['sent'][key]:
        if T0[key] + a <= t < T0[key] + b: return 0.18 + 0.3 * abs(math.sin((t - T0[key]) * 9.0))
    return 0.0

# ======================= helpers =======================
def grip_pt(P, key, off=0.075, lift=0.03): return P['_' + key + 'wrist'] + P['_' + key + 'dir'] * off + P['_' + key + 'palm'] * lift
def kneel(P, front='r', drop=0.43):
    b = 'l' if front == 'r' else 'r'; s = 1 if front == 'r' else -1
    P.update(crouch=drop); P[front + 'f'] = (s * 0.14, 0.07, 0.33); P[b + 'f'] = (-s * 0.13, 0.06, -0.52); P[b + 'kpole'] = (0, -0.8, 1.0)
    P[b + 'fdir'] = None; return P
def walk(P, p0, p1, t, a, b, rate=7.0, stride=0.3):
    """walk from p0 to p1 between a and b (base, yaw, walk phase)"""
    u = seg01(t, a, b); us = sm(u); P['base'] = lerp3(p0, p1, us)
    if 0 < u < 1: P['walk'] = us * rate * (math.hypot(p1[0] - p0[0], p1[2] - p0[2]) / 1.5); P['stride'] = stride; P['yaw'] = ang_to(p0, p1)
    return u
def dlw(base, yaw, p): return V(base, float) + hd.Ry(yaw) @ V(p, float)
def wld(base, yaw, w): return tuple(hd.Ry(yaw).T @ (V(w, float) - V(base, float)))
def ground(x0, x1, z0, z1, step, cols, seed=0, yfn=None):
    Q = []; xs = np.arange(x0, x1 + 1e-6, step); zs = np.arange(z0, z1 + 1e-6, step)
    for i in range(len(xs) - 1):
        for j in range(len(zs) - 1):
            a, b, c, d = xs[i], xs[i + 1], zs[j], zs[j + 1]; h = hsh(i * 31 + j * 7, seed)
            col = hd.shade(cols[int(h * len(cols)) % len(cols)], 0.9 + 0.2 * hsh(i * 3 + j * 17, seed + 1))
            Y = (lambda x, z: 0.0) if yfn is None else yfn
            q = hd.face([(a, Y(a, c), c), (a, Y(a, d), d), (b, Y(b, d), d), (b, Y(b, c), c)], col)
            if q: Q.append(q)
    return Q
def rock(c, r, col=(96, 92, 88), seed=0, flat=0.6):
    def d(p): k = 1 + 0.18 * math.sin(p[0] * 31 + seed) * math.cos(p[2] * 23 + seed * 2); return p * k
    return hd.ellip(c, hd.Ry(seed), (r, r * flat, r * 0.9), 8, 5, col, deform=d, colfn=lambda i, j, cl: hd.shade(col, 0.82 + 0.25 * hsh(i * 13 + j, seed)))
def sky_disc(c, r, col, n=14):
    c = V(c, float); return [hd.face([c + V((r * math.cos(2 * PI * i / n), r * math.sin(2 * PI * i / n), 0)) for i in range(n)], col, emit=True)]
def stars(seed, n, z, y0, y1, x0, x1):
    Q = []
    for i in range(n):
        x = lerp(x0, x1, hsh(i, seed)); y = lerp(y0, y1, hsh(i, seed + 1)); s = 0.08 + 0.1 * hsh(i, seed + 2)
        Q.append(hd.face([(x - s, y, z), (x, y - s, z), (x + s, y, z), (x, y + s, z)], (200, 210, 235), emit=True))
    return [q for q in Q if q]
def tree(x, z, h, col=(30, 46, 40), trunk=(50, 38, 30), seed=0):
    Q = hd.limb((x, 0, z), (x, h * 0.35, z), 0.09 * h / 4, 0.07 * h / 4, trunk, n=6, m=1)
    for i in range(3):
        y0 = h * (0.25 + 0.22 * i); r = h * (0.3 - 0.07 * i); c = hd.shade(col, 0.85 + 0.15 * (i % 2))
        Q += hd.lathe((x, y0, z), hd.Ry(hsh(seed, i) * 3), [(r, 0), (r * 0.5, h * 0.17), (0.02, h * 0.3)], 8, c, cap1=False)
    return Q

# ======================= sets =======================
TORCHES = [(-3.7, 2.3, 0.2), (3.8, 2.3, 1.2), (-3.9, 2.5, 5.6), (3.9, 2.5, 6.2)]
MOUTH_Z = -6.0
def cave_set():
    Q = ground(-8, 8, -6.4, 12, 0.8, [(84, 74, 64), (76, 68, 60), (92, 80, 68), (70, 62, 56)], seed=3)
    RC = [(92, 80, 70), (80, 70, 62), (104, 90, 76), (72, 64, 58)]
    def d(p): k = 1 + 0.07 * math.sin(p[0] * 1.7 + 1) * math.cos(p[2] * 1.3) + 0.05 * math.sin(p[1] * 2.3 + p[2]); return p * k
    def keep(c):                                                           # the mouth: an arch-shaped hole facing -z
        x, y, z = c[0], c[1] - 0.5, c[2] + 3.0
        if z < -3.5 and abs(x) < 3.6 and y < 4.6 - 0.15 * x * x: return False
        return True
    Q += hd.ellip((0, -0.5, 3.0), np.eye(3), (8.0, 7.2, 9.6), 30, 14, RC[0], deform=d, keep=lambda c: keep(c), v1=PI * 0.55, closed=False,
                  colfn=lambda i, j, cl: hd.shade(RC[(i + j) % 4], 0.85 + 0.2 * hsh(i * 7 + j, 2)))
    for i in range(14):                                                    # stalactites
        x = -5 + 10 * hsh(i, 5); z = -2 + 11 * hsh(i, 6); top = 6.4 - 0.04 * (x * x) - 0.02 * (z - 3) ** 2
        if top < 3.5: continue
        Q += hd.lathe((x, top - 1.0 - 0.8 * hsh(i, 7), z), np.eye(3), [(0.0, 0), (0.12 + 0.1 * hsh(i, 8), 0.9 + 0.8 * hsh(i, 7)), (0.25, 1.2 + 0.8 * hsh(i, 7))], 6, RC[i % 4], cap1=False)
    for i in range(18):                                                    # boulders along the walls
        a = 2 * PI * hsh(i, 9); r = 6.3 + 0.8 * hsh(i, 10); x = r * math.sin(a); z = 3.0 + r * 1.15 * math.cos(a)
        if z < -4.5 and abs(x) < 4: continue
        Q += rock((x, 0.2, z), 0.5 + 0.6 * hsh(i, 11), RC[i % 4], seed=i)
    for x, y, z in TORCHES:                                                # wall brackets
        Q += hd.bx((x * 1.05, y - 0.3, z), np.eye(3), (0.04, 0.2, 0.04), (50, 40, 32))
    Q += gold_pile((-2.6, 0, 4.4), 0.95, 0.6, seed=1, n=40) + gold_pile((2.6, 0, 5.6), 1.15, 0.7, seed=2, n=40) + gold_pile((0.6, 0, 8.4), 1.4, 0.9, seed=3, n=30)
    for i, (x, z) in enumerate(((-3.1, 3.4), (3.0, 4.2), (-2.0, 6.5), (2.2, 7.4))):     # old shields of the knights who came before
        Q += hd.lathe((x, 0.03, z), hd.Rx(-1.35 + 0.2 * hsh(i, 1)) @ hd.Ry(hsh(i, 2)), [(0.32, 0), (0.32, 0.03)], 10, (120 + 30 * (i % 2), 60, 50))
    return [q for q in Q if q]
def outside_set():
    """the night slope outside the mouth: road to the valley, trees, the Last Castle on its hill"""
    Q = ground(-16, 16, -60, MOUTH_Z, 1.2, [(44, 52, 40), (40, 48, 38), (50, 54, 42)], seed=7)
    for j in range(40):                                                    # the road
        z0 = MOUTH_Z - j * 1.3; z1 = z0 - 1.3; x0 = 1.2 * math.sin(z0 / 9); x1 = 1.2 * math.sin(z1 / 9)
        Q.append(hd.face([(x0 - 1.4, 0.01, z0), (x1 - 1.4, 0.01, z1), (x1 + 1.4, 0.01, z1), (x0 + 1.4, 0.01, z0)], hd.shade((104, 92, 76), 0.9 + 0.15 * hsh(j, 3))))
    for i in range(34):
        x = (3.5 + 12 * hsh(i, 1)) * (1 if i % 2 else -1); z = MOUTH_Z - 3 - 50 * hsh(i, 2)
        Q += tree(x, z, 3.5 + 3 * hsh(i, 3), seed=i)
    for i in range(10): Q += rock(((3.0 + 6 * hsh(i, 4)) * (1 if i % 2 else -1), 0.2, MOUTH_Z - 1 - 6 * hsh(i, 5)), 0.4 + 0.5 * hsh(i, 6), (86, 80, 74), seed=i)
    # the Last Castle on its hill
    cx, cz, cy = -16.0, -105.0, 14.0
    Q += hd.ellip((cx, -6, cz), np.eye(3), (44, 20, 28), 18, 7, (34, 42, 40), v1=PI * 0.5)
    Q += hd.ellip((22, -10, -120), np.eye(3), (50, 22, 26), 16, 6, (30, 38, 40), v1=PI * 0.5)
    ST = (70, 70, 80)
    Q += hd.bx((cx, cy + 2.5, cz), np.eye(3), (7.5, 2.5, 3.0), ST)
    for k, (dx, h) in enumerate(((-7.5, 9), (7.5, 9), (-2.5, 13), (3.0, 11))):
        Q += hd.lathe((cx + dx, cy, cz), np.eye(3), [(1.4, 0), (1.4, h)], 8, ST) + hd.lathe((cx + dx, cy + h, cz), np.eye(3), [(1.8, 0), (0.05, 3.2)], 8, (50, 40, 54), cap1=False)
        for w in range(2):
            Q += hd.decal((cx + dx, cy + h * (0.5 + 0.25 * w), cz - 1.42), (0, 0, -1.0), (0, 1, 0), 0.5, 0.8, (255, 206, 110), emit=True)
    for k in range(6): Q += hd.decal((cx - 5 + 2 * k, cy + 3.2, cz - 3.02), (0, 0, -1.0), (0, 1, 0), 0.4, 0.6, (255, 196, 100), emit=True)
    Q += sky_disc((12, 26, -110), 2.6, (226, 230, 244)) + stars(5, 60, -120, 12, 50, -60, 60)
    return [q for q in Q if q]
def house(x, z, yaw, w, d, h, wall, roof, seed=0):
    R = hd.Ry(yaw); c = V((x, 0, z)); TB = (70, 50, 34); Q = hd.bx(c + R @ V((0, h / 2, 0)), R, (w / 2, h / 2, d / 2), wall)
    for sx in (-1, 0, 1): Q += hd.bx(c + R @ V((sx * (w / 2 - 0.08), h / 2, -d / 2 - 0.02)), R, (0.08, h / 2, 0.04), TB)
    Q += hd.bx(c + R @ V((0, h * 0.55, -d / 2 - 0.03)), R, (w / 2, 0.06, 0.04), TB)
    ridge = h + w * 0.45
    for s in (-1, 1):
        Q.append(hd.face([c + R @ V((s * (w / 2 + 0.25), h - 0.1, -d / 2 - 0.3)), c + R @ V((0, ridge, -d / 2 - 0.3)), c + R @ V((0, ridge, d / 2 + 0.3)), c + R @ V((s * (w / 2 + 0.25), h - 0.1, d / 2 + 0.3))], hd.shade(roof, 1.0 if s > 0 else 0.85)))
    for s in (-1, 1): Q.append(hd.face([c + R @ V((-w / 2, h, s * d / 2)), c + R @ V((w / 2, h, s * d / 2)), c + R @ V((0, ridge - 0.05, s * d / 2))], wall))
    Q += hd.decal(c + R @ V((w * 0.22, 1.0, -d / 2 - 0.01)), R @ V((0, 0, -1.0)), (0, 1, 0), 0.8, 1.9, (82, 56, 36))
    Q += hd.decal(c + R @ V((-w * 0.22, h * 0.6, -d / 2 - 0.01)), R @ V((0, 0, -1.0)), (0, 1, 0), 0.7, 0.6, (60, 48, 40))
    Q += hd.decal(c + R @ V((-w * 0.22, h * 0.6, -d / 2 - 0.02)), R @ V((0, 0, -1.0)), (0, 1, 0), 0.06, 0.6, TB)
    Q += hd.bx(c + R @ V((w * 0.3, ridge - 0.2, d * 0.2)), R, (0.2, 0.7, 0.2), (110, 96, 86))
    return Q
GATE_Z = 7.6
def sky_set():
    """dawn sky: emissive dome with a warm-to-blue gradient, clouds, a sun halo"""
    def col(e):
        stops = [(0.0, (255, 200, 150)), (0.08, (250, 176, 150)), (0.25, (214, 168, 190)), (0.5, (150, 160, 214)), (1.0, (96, 128, 200))]
        for (a, ca), (b, cb) in zip(stops, stops[1:]):
            if e <= b: return mixc(ca, cb, (e - a) / (b - a))
        return stops[-1][1]
    Q = hd.ellip((0, -4, 20), np.eye(3), (190, 150, 190), 28, 12, (200, 200, 220), v1=PI * 0.53, closed=False, colfn=lambda i, j, cl: col(max(0.0, (cl[1]) / 150)))
    for q in Q: q['emit'] = True
    for i in range(16):                                                          # clouds: flat, lit from below by the sun
        a = -1.2 + 2.6 * hsh(i, 41); r = 120 + 30 * hsh(i, 42); x = r * math.sin(a); z = 20 + r * math.cos(a); y = 18 + 50 * hsh(i, 43)
        sx = 14 + 16 * hsh(i, 44); cc = mixc((255, 214, 196), (236, 226, 236), y / 70)
        for k in range(3):
            C_ = hd.ellip((x + (k - 1) * sx * 0.6, y + 2 * (k % 2), z), hd.Ry(a), (sx * (0.6 + 0.2 * (k % 2)), 3.0 + 2 * (k % 2), 6), 10, 4, cc,
                          colfn=lambda ii, jj, cl, cc=cc: hd.shade(cc, 0.9) if cl[1] < 0 else cc)
            for q in C_: q['emit'] = True
            Q += C_
    Q += sky_disc((52, 12, 150), 16, (255, 214, 170)) + sky_disc((50, 11.5, 148), 7, (255, 244, 214))
    return [q for q in Q if q]
def birds(t):
    Q = []
    for i in range(7):
        u = (t * 0.06 + hsh(i, 51)) % 1.0; x = -40 + 80 * u; y = 14 + 8 * hsh(i, 52) + 1.5 * math.sin(t * 0.7 + i); z = 40 + 25 * hsh(i, 53)
        f = 0.6 * math.sin(t * 9 + i * 2); s = 0.5
        for sd in (1, -1):
            q = hd.face([(x, y, z), (x - 0.3 * s, y + 0.05, z + sd * 0.0), (x + 0.1, y + sd * 0.0 + f * s * 0.5, z + sd * 0.9 * s)], (60, 50, 60)); Q += [q] if q else []
    return Q
def square_set():
    Q = ground(-12, 12, -8, GATE_Z + 0.4, 0.55, [(150, 138, 120), (136, 126, 110), (160, 146, 126), (128, 118, 104)], seed=11)
    Q += ground(-30, 30, GATE_Z + 0.4, 70, 2.0, [(96, 124, 70), (104, 132, 74), (88, 116, 66)], seed=12)
    for j in range(30):
        z0 = GATE_Z + 0.4 + j * 2.0; z1 = z0 + 2.0; xo = 2.0 * math.sin(z0 / 14)
        Q.append(hd.face([(xo - 1.3, 0.01, z0), (xo - 1.3, 0.01, z1), (2.0 * math.sin(z1 / 14) + 1.3, 0.01, z1), (xo + 1.3, 0.01, z0)], hd.shade((166, 146, 112), 0.92 + 0.1 * hsh(j, 2))))
    for (x, z, yaw, w, d, h, wl, rf) in ((-5.2, 1.0, PI / 2, 4.2, 3.4, 2.8, (206, 192, 160), (150, 70, 52)), (-5.0, 5.4, PI / 2 + 0.1, 3.6, 3.2, 2.6, (196, 184, 156), (120, 64, 50)),
                                         (5.4, 0.6, -PI / 2, 4.4, 3.6, 3.0, (210, 196, 166), (136, 76, 56)), (5.2, 5.2, -PI / 2 - 0.1, 3.6, 3.0, 2.6, (200, 188, 160), (110, 70, 56)),
                                         (-1.2, -6.0, 0.0, 5.0, 3.4, 3.2, (204, 190, 162), (140, 66, 50)), (4.0, -5.4, 0.25, 3.6, 3.2, 2.7, (196, 184, 156), (126, 72, 54))):
        Q += house(x, z, yaw, w, d, h, wl, rf)
    SG = (140, 134, 126)
    for sx in (-1, 1):
        Q += hd.bx((sx * 1.7, 1.3, GATE_Z), np.eye(3), (0.3, 1.3, 0.3), SG) + hd.bx((sx * 1.7, 2.66, GATE_Z), np.eye(3), (0.36, 0.08, 0.36), hd.shade(SG, 0.9))
        Q += hd.bx((sx * 2.9, 0.55, GATE_Z), np.eye(3), (0.9, 0.55, 0.22), hd.shade(SG, 0.95))
    Q += hd.bx((0, 2.85, GATE_Z), np.eye(3), (2.1, 0.12, 0.15), (90, 64, 44)) + hd.bx((0, 2.5, GATE_Z - 0.05), np.eye(3), (0.75, 0.2, 0.03), (120, 86, 52))
    cx, cz = 1.3, 1.6                                                     # the cart with the sacks
    Q += hd.bx((cx, 0.62, cz), hd.Ry(0.3), (0.55, 0.06, 0.8), (116, 84, 54)) + hd.bx((cx, 0.3, cz), hd.Ry(0.3), (0.06, 0.3, 0.06), (90, 64, 44))
    for sd in (1, -1): Q += hd.lathe(V((cx, 0.34, cz)) + hd.Ry(0.3) @ V((sd * 0.6, 0, 0)), hd.Ry(0.3) @ hd.Rz(PI / 2), [(0.34, 0), (0.34, 0.06)], 12, (96, 70, 46))
    for i, (dx, dz) in enumerate(((-0.25, -0.4), (0.2, -0.2), (-0.1, 0.25), (0.25, 0.45))):
        Q += sack(V((cx, 0.68, cz)) + hd.Ry(0.3) @ V((dx, 0, dz)), hd.Ry(0.3 + i), s=0.9)
    for i in range(14):
        x = -26 + 52 * hsh(i, 3); z = 22 + 40 * hsh(i, 4)
        if abs(x) < 4: continue
        Q += tree(x, z, 4 + 3 * hsh(i, 5), col=(60, 92, 56), trunk=(80, 60, 40), seed=i + 30)
    for i in range(5): Q += hd.ellip((-60 + 30 * i, -8, 110), np.eye(3), (26, 16 + 6 * hsh(i, 2), 8), 12, 5, (110, 120, 120), v1=PI * 0.5)
    return [q for q in Q if q]

# ======================= the sacks of the opening =======================
DB0 = (0.0, 0.0, 4.6); DYAW = PI
PAW_UP = (0.95, 0.5, 2.1); PAW_DN = (0.95, 0.12, 1.85)
CLAW_T = (0.35, 1.0); DROP_T = 0.55
SACK_T = (-0.2, 0.0, 1.15)
W_YAW = 2.06; W_K = tuple(V(SACK_T) - V((math.sin(W_YAW), 0, math.cos(W_YAW))) * 0.5)
DROPS = [(SACK_T, True, 0.0), ((-1.45, 0, 2.2), False, 0.12), ((-0.8, 0, 2.05), False, 0.05), ((-1.75, 0, 1.55), False, 0.2), ((-1.1, 0, 1.55), False, 0.1)]
PILE = [((1.75 + 0.42 * (i % 3) + 0.15 * (i // 3), 0, 2.7 + 0.38 * (i // 3)), hsh(i, 3)) for i in range(8)]
def paw_world(t):
    u = sm(seg01(t, 1.9, 3.0)); return dlw(DB0, DYAW, lerp3(PAW_UP, PAW_DN, u)) + V((0, 0.35 * sm(seg01(t, *CLAW_T)) * (1 - u), 0))
def sack_state(i, t):
    """(base, R) of the dropped sack i: hangs under the claw, falls, bounces, rolls to its spot"""
    tgt, torn, dl = DROPS[i]; pw = paw_world(min(t, DROP_T)) if t < DROP_T + dl else paw_world(DROP_T)
    hang = pw + V(((i % 3 - 1) * 0.16, -0.48 - 0.05 * (i % 2), (i // 3 - 0.5) * 0.14))
    td = DROP_T + dl
    if t < td: return hang, hd.Ry(i * 1.3) @ hd.Rz(0.3 * math.sin(t * 3 + i))
    u = seg01(t, td, td + 0.32); fall = V(lerp3(hang, (hang[0], 0.0, hang[2]), u * u))
    if u < 1: return fall, hd.Ry(i * 1.3) @ hd.Rz(0.6 * u)
    r = sm(seg01(t, td + 0.32, td + 0.95)); land = V((hang[0], 0.0, hang[2])); p = land + (V(tgt) - land) * r
    p[1] = 0.06 * abs(math.sin(r * PI * 2)) * (1 - r)
    yaw_end = ang_to(tgt, (0.5, 0, 0.8)) - 0.9 if torn else i * 1.3 + 0.8
    return p, hd.Ry(lerp(i * 1.3, yaw_end, r)) @ hd.Rz(lerp(0.6, 0.0, r) + 0.4 * math.sin(r * PI) * (1 if i % 2 else -1))
COINS = [(hsh(i, 21), hsh(i, 22), hsh(i, 23)) for i in range(34)]
def coins_spill(t):
    """gold pouring from the torn sack as it lands and rolls"""
    Q = []; td = DROP_T + 0.32
    if t < td: return Q
    for i, (a, b, c) in enumerate(COINS):
        t0 = td + 0.6 * a; u = seg01(t, t0, t0 + 0.5)
        src = V(SACK_T) + V((-0.3, 0.12, 0.5)) * (1 - seg01(t0, td, td + 0.63))
        dst = V(SACK_T) + V((-0.9 * b + 0.1, 0.0, 0.25 + 0.9 * c - 0.2))
        if u <= 0: continue
        p = src + (dst - src) * u; p[1] = 0.003 + max(0.0, src[1] * (1 - u) + 0.25 * math.sin(PI * u) * (1 - u) + 0.04 * abs(math.sin(u * PI * 3)) * (1 - u))
        R = hd.Rx(4 * u + a * 6) @ hd.Rz(3 * u * b) if u < 1 else hd.Rx(0.15 * (a - 0.5)) @ hd.Rz(0.15 * (b - 0.5))
        Q += coin(p, R, s=1.1)
    return Q
def pile_faces(t):
    u = sm(seg01(t, T0['05'] + 0.1, T0['05'] + 1.2)); Q = []
    for (x, y, z), h in PILE:
        Q += sack((x - 0.2 * u, 0, z - 0.75 * u), hd.Ry(ang_to((x, 0, z), (3.5, 0, 0.5)) + 0.3 * (h - 0.5)), s=1.0)
    return Q

# ======================= characters =======================
KP0 = (0.35, 0.0, -0.2)
def dragon_pose(t):
    P = dict(base=DB0, yaw=DYAW, head=(0.0, 1.75 + 0.03 * math.sin(t * 1.6), 2.3), hpitch=0.18, jaw=0.06, claw=0.0, eye=1.0, tail=0.25 * math.sin(t * 0.7),
             rpaw=PAW_UP, lie=0.0)
    P['claw'] = sm(seg01(t, *CLAW_T)) * (1 - 0.7 * sm(seg01(t, 2.2, 3.0))); P['rpaw'] = lerp3(PAW_UP, PAW_DN, sm(seg01(t, 1.9, 3.0)))
    for tb in (4.1, 9.3, 15.2, 21.0, 27.5):
        if tb <= t < tb + 0.18: P['blink'] = 1.0
    hl = sm(seg01(t, T0['04'] - 0.7, T0['04'] + 0.15))                       # lowers its head to the knight's level
    P['head'] = lerp3(P['head'], (0.35, 1.28, 3.1), hl); P['hyaw'] = -0.28 * hl; P['hpitch'] = lerp(0.18, -0.05, hl)
    ps = sm(seg01(t, T0['05'] + 0.1, T0['05'] + 1.2)) * (1 - sm(seg01(t, T0['06'], T0['06'] + 0.8)))
    P['lpaw'] = lerp3((-1.05, 0.12, 1.55), (-1.85, 0.12, 1.0), sm(seg01(t, T0['05'] - 0.4, T0['05'] + 0.1)) * (1 - ps)) if ps <= 0 else lerp3((-1.85, 0.12, 1.0), (-1.85, 0.12, 1.8), ps)
    up = sm(seg01(t, T0['05'] - 0.3, T0['05'] + 0.5))
    P['head'] = lerp3(P['head'], (0.25, 1.55, 2.85), up); P['hyaw'] = lerp(P['hyaw'], -0.2, up)
    if t >= T_OUT:                                                          # looks past the knight to the mouth
        u = sm(seg01(t, T_OUT, T_OUT + 0.8)); P['head'] = lerp3(P['head'], (0.0, 2.1, 2.7), u); P['hyaw'] = lerp(P['hyaw'], 0.0, u); P['hpitch'] = lerp(P['hpitch'], 0.05, u)
    st = sm(seg01(t, T0['11'] - 0.5, T0['11'] + 0.9))                         # steps up beside the knight
    if st > 0:
        b = lerp3(DB0, (0.45, 0.0, 3.4), st); P['base'] = b; P['lie'] = 0.35 * st
        tgt = wld(b, DYAW, (1.45, 2.05, -0.15)); P['head'] = lerp3(P['head'], tgt, st); P['hpitch'] = lerp(P['hpitch'], 0.0, st)
        P['rpaw'] = lerp3(P['rpaw'], (0.95, 0.12, 2.0), st); P['lpaw'] = lerp3(P['lpaw'], (-1.05, 0.12, 1.7), st)
    P['jaw'] = max(P['jaw'], jaw_talk(t, '04'), jaw_talk(t, '11'))
    if t >= T_WB:                                                          # rears, wings out, one huge beat
        r = sm(seg01(t, T_WB, T_WB + 0.5)); P['lie'] = lerp(0.35, 1.0, r); P['head'] = lerp3(P['head'], wld(P['base'], DYAW, (1.0, 3.3, -0.6)), r); P['hpitch'] = 0.35 * r
        P['wing'] = sm(seg01(t, T_WB + 0.1, T_WB + 0.65)) * (1 - 0.6 * sm(seg01(t, T_GUST + 1.4, T_GUST + 3.0)))
        up_ = sm(seg01(t, T_WB + 0.45, T_GUST - 0.3)); dn = sm(seg01(t, T_GUST - 0.3, T_GUST + 0.05))
        P['flap'] = 0.55 * up_ - 1.0 * dn + 0.3 * sm(seg01(t, T_GUST + 0.4, T_GUST + 1.4))
        P['jaw'] = 0.5 * win(t, T_GUST - 0.4, T_GUST + 0.8, 0.2)
        P['rpaw'] = lerp3(P['rpaw'], (0.9, 0.9, 2.4), r * (1 - sm(seg01(t, T_GUST + 0.2, T_GUST + 0.9))))
    return P

def knight_pose(t):
    P = dict(base=KP0, yaw=0.0, eyes='open', mouth='neutral', brow=0.5, lean=0.06, cape_sway=0.15 * math.sin(t * 1.3))
    head_w = dlw(DB0, DYAW, (0, 1.75, 2.3))
    aim = 1.0; dip = sm(seg01(t, T0['06'] + 0.2, T0['06'] + 1.0))
    low = max(dip, knight_low(t))
    P['rh'] = lerp3((0.22, 1.28, 0.42), (0.24, 0.95, 0.3), low); P['rgrip'] = 0.9; P['rpalm'] = (-1.0, 0, 0.0)
    P['lh'] = (-0.25, 1.0, 0.15); P['lgrip'] = 0.5
    if T0['04'] - 0.7 <= t < T0['05']: P['brow'] = lerp(0.5, 0.0, sm(seg01(t, T0['04'], tend('04'))))
    if t >= T0['05']: P['brow'] = -0.2
    if T0['03'] <= t < T0['04']: P['head'] = (0.0, 0.05, 0.0)
    mt = talking(t, '03') or talking(t, '10')
    if mt: P['mouth'] = mt
    if t >= T_OUT:                                                          # turns towards the mouth
        u = sm(seg01(t, T_OUT + 0.2, T_OUT + 1.1)); P['yaw'] = lerp(0.0, -PI / 2, u)
    if t >= T_STAND:                                                        # dragon -> villagers -> captain
        a = ws('09', 0); b = ws('09', 1)
        hy = 0.95 * (1 - sm(seg01(t, a + 0.9, a + 1.3))) - 0.95 * sm(seg01(t, b + 0.3, b + 0.75))
        P['head'] = (hy, 0.0, 0.0); P['brow'] = -0.3 if t < b + 0.3 else 0.6; P['eyes'] = 'open'
    turn = sm(seg01(t, T0['10'] - 0.25, T0['10'] + 0.55))
    if turn > 0:
        P['yaw'] = lerp(-PI / 2, -PI, turn); P['head'] = (lerp(-0.95, 0.0, turn), 0.0, 0.0); P['brow'] = 0.7
        P['rh'] = lerp3(P['rh'], (0.18, 1.32, 0.48), turn)
    if t >= T_WB: P['brow'] = 0.4; P['cape_sway'] = 0.15 + 1.2 * win(t, T_GUST - 0.2, T_GUST + 0.9, 0.2)
    return P, aim
def knight_low(t): return win(t, T_PATCH - 0.3, T0['03'] + 0.05, 0.45)
def knight_sword(P, t, tgt_w):
    g = grip_pt(P, 'r', 0.06, 0.0); d = hd.nz(V(tgt_w) - g)
    return hd.sword(g, d, P['_rpalm'], length=0.85)

W_START = (-1.25, 0.0, -0.95)
T_KN = (1.45, tend('01') + 0.05)
def woman_pose(t):
    P = dict(base=W_START, yaw=0.3, eyes='open', mouth='neutral', brow=-0.2, lean=0.05, cape_sway=0.1)
    if t < T_KN[1]:
        walk(P, W_START, W_K, t, T_KN[0], T_KN[1] - 0.25, rate=6.0, stride=0.24)
        if t >= T_KN[1] - 0.25: P['base'] = W_K
    if t >= T_KN[1] - 0.35:
        kn = sm(seg01(t, T_KN[1] - 0.35, T_KN[1] + 0.2)); P['base'] = W_K; P['yaw'] = angl(ang_to(W_START, W_K), W_YAW, kn)
        kneel(P, 'r', 0.43 * kn); P['lean'] = 0.15 + 0.15 * kn
    return P
def woman_sack(t, P):
    """the patched sack: on the floor -> in her hands -> turned (patch) -> stroked -> hugged; returns (base, R) or None if on the floor"""
    tp = T_PATCH; RW = P['_RW']; fw = V((math.sin(W_YAW), 0, math.cos(W_YAW)))
    if t < tp + 0.35: return None
    lift = sm(seg01(t, tp + 0.35, tp + 0.9)); hug = sm(seg01(t, tp + 1.75, tp + 2.35)) * (1 - sm(seg01(t, T0['11'] + 0.9, T0['11'] + 1.5)) * 0.0)
    floor = V(SACK_T); lap = V(W_K) + fw * 0.42 + V((0, 0.4, 0)); chest = P['_chest'] + RW @ V((0, -0.36, 0.33))
    p = floor + (lap - floor) * lift; p = p + (chest - p) * hug
    R = hd.Ry(lerp(ang_to(SACK_T, (0.5, 0, 0.8)) - 0.9, W_YAW - 0.9, lift)) @ hd.Rx(-0.25 * hug)
    return p, R
def woman_act(t):
    P = woman_pose(t); tp = T_PATCH
    if t >= tp:
        Q_ = dict(P); hd.human(WOMAN, Q_)
        sk = woman_sack(t, Q_)
        reach = sm(seg01(t, tp, tp + 0.35))
        fw = V((math.sin(W_YAW), 0, math.cos(W_YAW))); sd_ = V((math.cos(W_YAW), 0, -math.sin(W_YAW)))
        def side_hands(cen, h, rad, front=0.0, grip=0.3):
            """both hands on the OUTSIDE of the sack, palms facing it (no fingers inside)"""
            c_ = V(cen) + V((0, h, 0)) + fw * front
            P['rh_w'] = tuple(c_ + sd_ * rad); P['lh_w'] = tuple(c_ - sd_ * rad); P['rgrip'] = P['lgrip'] = grip
            P['rpalm'] = tuple(-sd_); P['lpalm'] = tuple(sd_); P['rpalm_local'] = False; P['lpalm_local'] = False
        if sk is None:
            side_hands(SACK_T, 0.16, 0.25 + 0.15 * (1 - reach), -0.04)
            P['nod'] = 0.35 * reach; P['eyes'] = 'open'
        else:
            side_hands(sk[0], 0.16, 0.255)
            st = win(t, tp + 1.0, tp + 1.85, 0.15)                              # strokes the patch: the hand glides over it
            if st > 0:
                pn = hd.nz(sk[1] @ hd.Ry(0.9) @ V((0, 0, 1.0))); upv = sk[1] @ V((0, 1.0, 0)); tg_ = hd.nz(np.cross(upv, pn))
                pp = sk[0] + upv * 0.11 + pn * 0.235 + tg_ * 0.05 * math.sin((t - tp) * 8)
                P['rh_w'] = tuple(pp + pn * 0.03 + upv * 0.1); P['rpalm'] = tuple(-pn); P['rgrip'] = 0.1
            P['nod'] = 0.4; P['eyes'] = 'sad'; P['brow'] = -0.8; P['mouth'] = 'soft'
            hug = sm(seg01(t, tp + 1.75, tp + 2.35))
            if hug > 0:
                P['eyes'] = 'closed' if t < T0['02'] - 0.15 else 'sad'; P['nod'] = lerp(0.4, 0.2, hug); P['head'] = (0.0, 0.0, 0.12 * hug)
                side_hands(sk[0], 0.18, 0.25, 0.04, 0.45)
        if t >= T0['02'] - 0.2:                                              # looks up to the knight and the dragon
            u = sm(seg01(t, T0['02'] - 0.2, T0['02'] + 0.3)); P['nod'] = lerp(P.get('nod', 0.0), -0.25, u); P['head'] = (0.5 * u, -0.25 * u, 0.0)
            P['eyes'] = 'open' if t < T0['03'] else 'sad'
        mt = talking(t, '02') or talking(t, '06')
        if mt: P['mouth'] = mt; P['brow'] = -0.6
        if t >= T0['06'] - 0.1:                                             # her right hand closes on a coin from the floor
            u = sm(seg01(t, T0['06'] - 0.1, T0['06'] + 0.5)); cl = sm(seg01(t, ws('06', 1) - 0.1, ws('06', 1) + 0.25))
            P['rh_w'] = tuple(lerp3(P['rh_w'], V(COIN_F) + V((0, 0.06, 0)), u * (1 - sm(seg01(t, ws('06', 1) + 0.3, ws('06', 1) + 0.9)))))
            if cl > 0.5: P['rh_w'] = tuple(lerp3(V(COIN_F) + V((0, 0.06, 0)), V(P['rh_w']) + V((0, 0.4, 0)), sm(seg01(t, ws('06', 1) + 0.3, ws('06', 1) + 0.9))))
            P['rgrip'] = lerp(0.2, 1.0, cl); P['brow'] = -0.9 if t < tend('06') else -0.5; P['nod'] = 0.15
        if t >= T0['11'] + 0.6:                                             # stands, the sack in her arms
            u = sm(seg01(t, T0['11'] + 0.6, T0['11'] + 1.4)); P['crouch'] = 0.43 * (1 - u)
            if u > 0.5:
                for k in ('rf', 'lf', 'lkpole'): P.pop(k, None)
            P['head'] = (0.3, 0.0, 0.0); P['eyes'] = 'open'; P['brow'] = 0.2
    return P
COIN_F = tuple(V(W_K) + V((math.sin(W_YAW), 0, math.cos(W_YAW))) * 0.32 + V((math.cos(W_YAW), 0, -math.sin(W_YAW))) * 0.18 + V((0, 0.005, 0)))

VIL = [(VIL1, (-1.9, 0, -0.9), 0.6, DROPS[1][0]), (VIL2, (-2.3, 0, 0.3), 1.2, DROPS[3][0]), (VIL3, (-1.6, 0, -1.9), 0.4, DROPS[4][0])]
def villager_pose(i, t):
    sp, p0, yaw0, sk = VIL[i]; P = dict(base=p0, yaw=yaw0, eyes='open', mouth='neutral', brow=-0.1)
    P['head'] = (0.2 * math.sin(t * 0.5 + i), 0.0, 0.0)
    if t >= T_OUT: P['eyes'] = 'wide'; P['brow'] = -0.6; P['head'] = (-0.6, 0.0, 0.0)
    ga = T0['11'] - 0.3 + 0.25 * i; tgt = tuple(V(sk) + V((-0.45, 0, -0.3)))
    held = None
    if t >= ga:
        u = walk(P, p0, tgt, t, ga, ga + 1.0, rate=6.5)
        if u >= 1: P['base'] = tgt; P['yaw'] = ang_to(tgt, sk)
        c = sm(seg01(t, ga + 1.0, ga + 1.3)) * (1 - sm(seg01(t, ga + 1.4, ga + 1.8)))
        P['crouch'] = 0.35 * c; P['lean'] = 0.35 * c; P['head'] = (0.0, 0.3 * c, 0.0)
        if t >= ga + 1.25:
            pk = sm(seg01(t, ga + 1.25, ga + 1.8)); fw = V((math.sin(P['yaw']), 0, math.cos(P['yaw'])))
            held = V(sk) + (V(P['base']) + fw * 0.32 + V((0, 0.9, 0)) - V(sk)) * pk
            sd_ = V((math.cos(P['yaw']), 0, -math.sin(P['yaw'])))
            P['rh_w'] = tuple(held + V((0, 0.2, 0)) + sd_ * 0.2); P['lh_w'] = tuple(held + V((0, 0.2, 0)) - sd_ * 0.2); P['rgrip'] = P['lgrip'] = 0.5
    return P, held

# riders at the mouth
RIDERS = [(CAPTAIN, (0.6, 0, -6.6), (96, 64, 44), True), (SOLDIER, (-1.2, 0, -8.0), (60, 50, 44), False), (SOLDIER, (2.2, 0, -8.3), (120, 110, 100), False),
          (SOLDIER, (0.4, 0, -9.6), (80, 56, 40), False)]
def rider_state(i, t):
    """horse pose, human pose, torch on (0..1), torch world point"""
    sp, p, col, cap = RIDERS[i]; Ph = dict(base=p, yaw=0.08 * (i - 1.5), nod=0.3 * math.sin(t * 1.1 + i)); Pr = dict(eyes='open', mouth='neutral', brow=0.7 if cap else 0.3)
    if T_OUT <= t < T_CAP:                                                  # far down the road, galloping up
        z = -34 + 4.2 * (t - T_OUT) - 2.2 * i; x = 1.2 * math.sin(z / 9) + (i % 2 - 0.5) * 1.2
        Ph = dict(base=(x, 0, z), yaw=0.0, gallop=(t * 9 + i * 1.3))
    if t >= T_GUST:                                                         # the dark: rear, then bolt; the captain backs off last
        r = win(t, T_GUST + 0.05, T_GUST + 0.75, 0.2); Ph['rear'] = r * (0.9 if not cap else 0.6)
        if not cap:
            tb = T_GUST + 0.55 + 0.15 * i; u = max(0.0, t - tb)
            if u > 0:
                d = 1 if i % 2 else -1; Ph['yaw'] = lerp(Ph['yaw'], d * PI * 0.55, sm(seg01(u, 0, 0.5))); Ph['gallop'] = t * 10 + i; Ph['rear'] = 0.0
                Ph['base'] = (p[0] + d * 7.5 * u * min(1, u / 0.5), 0, p[2] - 2.5 * u)
        else:
            u = sm(seg01(t, T_GUST + 0.6, T_GUST + 2.0)); Ph['base'] = (p[0], 0, p[2] - 1.1 * u)
            if t > T_GUST + 0.6 and t < T_GUST + 2.0: Ph['gallop'] = -(t * 4)
            v = max(0.0, t - (T_GUST + 2.0))
            if v > 0: Ph['yaw'] = lerp(0.0, PI * 0.6, sm(seg01(v, 0, 0.45))); Ph['gallop'] = t * 10; Ph['base'] = (p[0] + 7.0 * v * min(1, v / 0.4), 0, p[2] - 1.1 - 1.0 * v)
    if cap:
        pt = win(t, T0['08'] - 0.1, tend('08') + 0.2, 0.3)
        Pr.update(rh=(lerp(0.25, 0.3, pt), lerp(1.0, 1.55, pt), lerp(0.25, 0.55, pt)), rgrip=0.5, lh=(-0.15, 0.95, 0.35), lgrip=0.8)
        mt = talking(t, '08')
        if mt: Pr['mouth'] = mt
        if t >= T_GUST: Pr['eyes'] = 'wide'; Pr['brow'] = -0.5; Pr['mouth'] = 'o'
        tq = None; on = 0.0
    else:
        Pr.update(lh=(-0.3, 1.35, 0.25), lgrip=0.9, lpalm=(1.0, 0, 0), rh=(0.15, 1.0, 0.3), rgrip=0.8)
        on = 1.0 - sm(seg01(t, T_GUST - 0.05, T_GUST + 0.15))
        if t >= T_GUST: Pr['eyes'] = 'wide'
    return sp, Ph, Pr, col, on, cap

# dawn
W_D = (0.0, 0.0, 1.3); KID_P = (0.55, 0.0, 0.5)
DV = [(VIL1, (-0.8, 0, 0.35)), (VIL2, (1.25, 0, 0.6)), (VIL3, (-1.5, 0, 1.0))]
KN_GATE = (0.55, 0.0, GATE_Z + 0.6)
GIVES = [T_DAWN + 0.25, T0['13'] + 0.45, ws('13', 1) + 0.25, tend('13') - 0.1]
def woman_dawn(t):
    P = dict(base=W_D, yaw=PI + 0.1, eyes='open', mouth='smile', brow=0.0, lean=0.04)
    P['lh'] = (-0.18, 0.92, 0.22); P['lgrip'] = 0.5
    tg = [KID_P] + [p for _, p in DV]
    for k, tk in enumerate(GIVES):                                         # hands a coin to each one
        u = win(t, tk - 0.35, tk + 0.35, 0.3)
        if u > 0:
            tw = V(tg[k]) + V((0, 0.95 if k else 0.75, 0)); tw = V(W_D) + (tw - V(W_D)) * 0.55; tw[1] = 0.95 if k else 0.78
            P['rh_w'] = tuple(tw); P['rgrip'] = 0.3; P['yaw'] = angl(PI + 0.1, ang_to(W_D, tg[k]), u)
    mt = talking(t, '13')
    if mt: P['mouth'] = mt
    if t >= T_KID + 0.25: u = sm(seg01(t, T_KID + 0.25, T_KID + 0.7)); P['nod'] = -0.45 * u; P['eyes'] = 'wide' if u > 0.5 else 'open'
    return P
def kid_dawn(t):
    P = dict(base=KID_P, yaw=ang_to(KID_P, W_D), eyes='open', mouth='o', brow=0.3)
    g = sm(seg01(t, GIVES[0] - 0.2, GIVES[0] + 0.25))
    P['rh'] = lerp3((0.2, 0.62, 0.05), (0.12, 0.72, 0.3), g); P['rpalm'] = (0, 1.0, 0); P['rgrip'] = 0.2 + 0.5 * sm(seg01(t, GIVES[0] + 0.1, GIVES[0] + 0.4))
    if t >= GIVES[0] + 0.4:
        P['mouth'] = 'smile'; P['rh'] = (0.1, 0.78, 0.25); P['nod'] = 0.35; P['eyes'] = 'wide'
    if t >= T_KID:                                                          # looks up at the shadow, waves
        u = sm(seg01(t, T_KID, T_KID + 0.4)); P['nod'] = lerp(0.35, -0.6, u); P['yaw'] = angl(P['yaw'], -2.4, u); P['mouth'] = 'open'
        wv = sm(seg01(t, T_KID + 0.4, T_KID + 0.7))
        if wv > 0: P['rh'] = (0.25 + 0.08 * math.sin((t - T_KID) * 12), 1.15 * wv + 0.78 * (1 - wv), 0.15); P['rpalm'] = (0, 0, 1.0); P['rgrip'] = 0.0; P['mouth'] = 'smile'
        P['lean'] = -0.1 * u
    return P
def vil_dawn(i, t):
    sp, p = DV[i]; P = dict(base=p, yaw=ang_to(p, W_D), eyes='open', mouth='smile', brow=0.1)
    tk = GIVES[i + 1]; u = win(t, tk - 0.3, tk + 0.45, 0.25)
    if u > 0: P['rh'] = (0.12, 0.95, 0.3); P['rpalm'] = (0, 1.0, 0); P['rgrip'] = 0.3
    if t >= T_KID + 0.3 + 0.1 * i: P['nod'] = -0.4 * sm(seg01(t, T_KID + 0.3 + 0.1 * i, T_KID + 0.8 + 0.1 * i)); P['mouth'] = 'o'
    return P
def knight_gate(t):
    P = dict(base=KN_GATE, yaw=0.0, eyes='open', mouth='neutral', brow=0.2, cape_sway=0.25 * math.sin(t * 1.4))
    P['rh'] = (0.2, 1.1, 0.3); P['rgrip'] = 0.9; P['rpalm'] = (-1.0, 0, 0)
    lw = sm(seg01(t, T_FIN + 0.15, T_FIN + 0.9)); tn = sm(seg01(t, T_FIN + 0.6, T_FIN + 1.7))
    if lw > 0: P['rh'] = lerp3((0.2, 1.1, 0.3), (0.24, 0.82, 0.12), lw)
    if tn > 0: P['yaw'] = lerp(0.0, PI - 0.2, tn); P['mouth'] = 'smile' if tn > 0.6 else 'neutral'; P['brow'] = -0.1
    if T_SKY - 0.3 <= t < T_FIN: P['head'] = (0.0, -0.35, 0.0)
    return P, lw
def sky_dragon(t):
    """flying: passes over the square (the kid's wave), dips a wing, then circles above the road"""
    u = t - T_DAWN; w = 0.3; cx, cz, R_ = 0.0, 24.0, 12.0
    a = -1.3 + w * (t - T_KID)
    p = (cx + R_ * math.cos(a) - 2.0, 10.0 + 1.0 * math.sin(t * 0.8), cz + R_ * math.sin(a) * 1.3)
    da = (-R_ * math.sin(a), 0, R_ * math.cos(a) * 1.3); yaw = math.atan2(da[0], da[2])
    roll = -0.22 - 0.3 * win(t, T_SKY + 0.15, T_SKY + 1.15, 0.3); ph = t * 4.0
    p = (p[0], p[1] - 0.22 * math.sin(ph), p[2])                              # the body rises on the down-stroke
    return dict(base=p, yaw=yaw, roll=roll, pitch=0.06, wing=0.9 + 0.1 * math.cos(ph), flap=0.62 * math.sin(ph), lie=0.0, head=(0, 1.55, 3.6), hpitch=0.02,
                rpaw=(0.7, 0.55, 0.9), lpaw=(-0.7, 0.55, 0.9), jaw=0.05, eye=0.4, tail=0.35 * math.sin(t * 1.3), fly=True)

# ======================= camera =======================
P3 = look.Path
def sh(keys, amp=1.8):
    p0 = V(keys[0][1], float); keys = [(a, tuple(p0 + (V(p, float) - p0) * amp), q, f) for a, p, q, f in keys]                # bigger, livelier camera moves (Format 3.0)
    return (keys[0][0], P3([(a, p) for a, p, _, _ in keys]), P3([(a, q) for a, _, q, _ in keys]), P3([(a, f) for a, _, _, f in keys]))
SHOTS = [sh([(0.0, (1.7, 2.05, -1.05), (-0.55, 1.05, 2.35), 52.0), (T_PATCH, (1.4, 1.95, -0.7), (-0.6, 0.95, 2.1), 48.0)]),
         sh([(T_PATCH, (0.95, 1.25, 0.4), (-0.42, 0.72, 1.35), 40.0), (T0['02'], (0.82, 1.22, 0.5), (-0.48, 0.88, 1.38), 36.0), (T0['03'], (0.8, 1.22, 0.52), (-0.5, 0.92, 1.38), 35.0)]),
         sh([(T0['03'] - 0.1, (0.85, 1.82, 1.45), (0.3, 1.7, -0.2), 36.0), (T0['04'], (0.75, 1.8, 1.35), (0.3, 1.68, -0.2), 34.0)]),
         sh([(T0['04'] - 0.75, (4.4, 1.75, 0.6), (0.05, 1.45, 0.6), 42.0), (T0['05'], (4.0, 1.7, 0.6), (0.05, 1.4, 0.6), 40.0)]),
         sh([(T0['05'] - 0.1, (3.6, 1.65, 0.4), (1.9, 0.4, 2.7), 46.0), (T0['06'], (3.4, 1.6, 0.6), (1.8, 0.4, 2.5), 44.0)]),
         sh([(T0['06'] - 0.1, (1.65, 1.05, 0.15), (-0.45, 0.8, 1.32), 40.0), (T_OUT, (1.55, 1.02, 0.25), (-0.45, 0.8, 1.32), 38.0)]),
         sh([(T_OUT, (0.7, 1.5, -3.2), (-4.0, 4.0, -40.0), 46.0), (T_CAP, (0.6, 1.45, -3.7), (-4.6, 4.2, -40.0), 44.0)]),
         sh([(T_CAP, (2.0, 1.35, -3.3), (0.5, 2.1, -6.7), 46.0), (T_STAND, (1.9, 1.35, -3.6), (0.5, 2.1, -6.7), 44.0)]),
         sh([(T_STAND, (-0.95, 1.76, -0.5), (0.35, 1.7, -0.2), 36.0), (T0['10'] - 0.1, (-0.9, 1.74, -0.4), (0.35, 1.68, -0.2), 34.0)]),
         sh([(T0['10'] - 0.1, (-0.35, 1.4, -2.55), (0.35, 1.55, -0.1), 44.0), (T0['11'] - 0.5, (-0.25, 1.42, -2.35), (0.35, 1.55, -0.1), 42.0)]),
         sh([(T0['11'] - 0.5, (-0.7, 1.4, -4.1), (0.6, 1.65, 0.2), 50.0), (T_WB, (-0.5, 1.45, -3.7), (0.65, 1.7, 0.2), 48.0)]),
         sh([(T_WB, (0.8, 4.6, 9.0), (0.3, 1.8, -6.0), 62.0), (T_GUST + 0.5, (0.7, 4.5, 8.8), (0.3, 1.7, -6.0), 60.0)]),
         sh([(T_GUST + 0.5, (1.9, 2.1, -12.9), (0.3, 2.0, -3.0), 54.0), (T_DAWN, (1.6, 2.0, -12.2), (0.4, 1.9, -4.0), 50.0)]),
         sh([(T_DAWN, (1.8, 1.55, -2.1), (0.1, 1.1, 1.1), 46.0), (T_KID, (1.45, 1.48, -1.65), (0.2, 1.05, 1.0), 44.0)]),
         sh([(T_KID, (-0.5, 0.95, -0.75), (0.55, 0.95, 0.5), 44.0), (T_KID + 0.5, (-0.55, 0.92, -0.8), (0.5, 1.25, 0.6), 46.0), (T_SKY, (-0.6, 0.9, -0.85), (0.5, 1.55, 0.8), 48.0)])]
def cam_shot(t):
    sc = scene(t)
    if sc == 'sky':
        d = sky_dragon(t); p = V((0.3, 0.7, -1.3)); tg = V(d['base']) * 0.85 + V((0, 0, 2.0)) * 0.15
        return tuple(p + V((0.1 * math.sin(t), 0, 0))), tuple(tg), 54.0
    if sc == 'fin':
        u = seg01(t, T_FIN, DUR); return lerp3((-0.45, 1.66, 5.0), (-0.25, 1.62, 5.6), u), lerp3((0.6, 1.58, 8.2), (0.58, 1.55, 8.15), u), lerp(42.0, 38.0, u)
    cur = SHOTS[0]
    for s_ in SHOTS:
        if t >= s_[0]: cur = s_
    return tuple(cur[1](t)), tuple(cur[2](t)), float(cur[3](t))

# ======================= render =======================
_SETS = {}
def get_set(name):
    if name not in _SETS: _SETS[name] = {'cave': cave_set, 'out': outside_set, 'square': square_set, 'sky': sky_set}[name]()
    return _SETS[name]
def wall_torches(t, on=1.0):
    Q = []; L = []
    for i, (x, y, z) in enumerate(TORCHES):
        Q += torch_faces((x, y, z), t, k=on, seed=i, stick=False)
        if on > 0.02: L.append(((x * 0.9, y + 0.3, z), (255, 150, 70), 1.25 * on * (1 + 0.1 * math.sin(t * 9 + i * 2) + 0.05 * math.sin(t * 23 + i))))
    return Q, L
def riders_layers(t, cam_far=False):
    layers = []; L = []
    for i in range(len(RIDERS)):
        sp, Ph, Pr, col, on, cap = rider_state(i, t)
        layers.append(horse(Ph, col=col))
        Pq = rider(sp, Ph, Pr); layers.append(hd.human(sp, Pq))
        if not cap:
            tp = grip_pt(Pq, 'l', 0.06, 0.0) + V((0, 0.05, 0)); layers.append(torch_faces(tp + V((0, 0.4, 0)), t, k=on, seed=i))
            if on > 0.02: L.append((tuple(tp + V((0, 0.6, 0))), (255, 150, 70), 1.6 * on))
        else:
            g = grip_pt(Pq, 'r', 0.06, 0.0); d_ = hd.nz(V((0.2, 0.2, 1.0)) if t < T_GUST else V((0.1, -0.6, 0.6)))
            layers.append(hd.sword(g, d_, Pq['_rpalm'], length=0.8))
    return layers, L
def world(t):
    sc = scene(t); L = []; layers = []; fog = (12, 10, 14); amb = 0.3; fs, fe = 8, 34
    if sc in ('cave', 'road', 'capt', 'stand', 'wing'):
        layers.append(get_set('cave'))
        dark = sm(seg01(t, T_GUST - 0.05, T_GUST + 0.12)) if sc == 'wing' else 0.0
        if sc != 'cave': layers.append(get_set('out'))
        tq, tl = wall_torches(t, 1.0 - dark); layers.append(tq); L += tl
        L.append(((-1.0, 0.8, 2.0), (255, 196, 90), 0.3 * (1 - dark)))
        L.append(((6.0, 14.0, -40.0), (120, 140, 210), (0.25 if sc in ('cave', 'stand') else 1.1) + 0.9 * dark))
        D = dragon_pose(t); layers.append(dragon(D))
        layers.append(coins_spill(t)); layers.append(pile_faces(t))
        for i in range(len(DROPS)):
            if i == 0 and t >= T_PATCH + 0.35: continue
            p, R = sack_state(i, t)
            if i in (1, 3, 4) and t >= T0['11'] - 0.3: continue                  # picked up by the villagers (drawn in their arms)
            layers.append(sack(p, R, s=0.9 if i == 0 else 1.0, torn=(i == 0), patch=(i == 0), slump=0.5 if i == 0 else 0.0))
        K, _ = knight_pose(t); layers.append(knight(K))
        if t < T_OUT:
            lw_ = max(knight_low(t), sm(seg01(t, T0['06'] + 0.2, T0['06'] + 1.0))); tgt = dlw(DB0, DYAW, (0, 1.75, 2.3)) * (1 - lw_) + (V(KP0) + V((0.25, 0.0, 0.75))) * lw_
        elif t < T0['10']: tgt = V(K['_chest']) + hd.Ry(K['yaw']) @ V((0.25, -1.2, 1.0))
        else: tgt = V((0.6, 2.2, -6.6))
        layers.append(knight_sword(K, t, tgt))
        Wm = woman_act(t); layers.append(hd.human(WOMAN, Wm)); sk = woman_sack(t, Wm)
        if sk is not None: layers.append(sack(sk[0], sk[1], s=0.9, torn=True, patch=True, slump=0.5))
        if t >= T0['06'] - 0.1:
            cl = sm(seg01(t, ws('06', 1) - 0.1, ws('06', 1) + 0.25))
            if cl < 0.6: layers.append(coin(COIN_F, s=1.2))
        else: layers.append(coin(COIN_F, s=1.2))
        for i in range(3):
            Pv, held = villager_pose(i, t); layers.append(hd.human(VIL[i][0], Pv))
            if held is not None: layers.append(sack(held - V((0, 0.12, 0)), hd.Ry(Pv['yaw'] + PI), s=0.95))
        if sc != 'cave':
            rl, rL = riders_layers(t); layers += rl; L += rL
            fog = (30, 40, 74); fs, fe = 18, 200
        amb = lerp(0.24, 0.38, dark)
        if dark > 0: L.append(((8.0, 12.0, -25.0), (120, 140, 210), 3.2 * dark))
        if sc == 'road': amb = 0.24
    else:
        layers.append(get_set('square')); layers.append(get_set('sky')); layers.append(birds(t)); fog = (226, 190, 160); amb = 0.5; fs, fe = 40, 420
        L += [((40, 14, 50), (255, 214, 170), 2.4), ((-20, 18, -10), (170, 180, 220), 0.9)]
        if sc != 'sky' or True:
            Wd = woman_dawn(t); layers.append(hd.human(WOMAN, Wd))
            layers.append(sack(V(Wd['_lwrist']) + V((0, -0.3, 0.0)), hd.Ry(Wd['yaw'] + PI - 0.9), s=0.85, torn=True, patch=True, slump=0.4))
            for k, tk in enumerate(GIVES):
                u = seg01(t, tk - 0.05, tk + 0.25)
                if tk - 0.4 <= t < tk + 0.3: layers.append(coin(grip_pt(Wd, 'r', 0.08, 0.04), hd.Rx(1.2), s=1.4))
            Kd = kid_dawn(t); layers.append(hd.human(KID, Kd))
            for i in range(3): layers.append(hd.human(DV[i][0], vil_dawn(i, t)))
            Kn, lw = knight_gate(t); layers.append(knight(Kn))
            g = grip_pt(Kn, 'r', 0.06, 0.0); d_ = hd.nz(lerp3(V((0, 0.95, 0.3)), V((0.05, -1.0, 0.1)), lw)); layers.append(hd.sword(g, d_, Kn['_rpalm'], length=0.85))
        D = sky_dragon(t) if sc in ('sky', 'fin') else None
        if sc == 'dawn' and t >= T_KID - 0.2: D = sky_dragon(t)
        if D is not None: layers.append(dragon(D))
        sw = seg01(t, T_KID - 0.1, T_KID + 0.75)                              # the shadow sweeps over the square
        if 0 < sw < 1:
            c = V((7.0 - 15.0 * sw, 0.02, -2.0 + 6.0 * sw)); ang = math.atan2(-15.0, 6.0); R = hd.Ry(ang)
            shp = [(0, 2.2), (0.5, 0.8), (4.2, 0.2), (0.6, -0.4), (0.25, -2.6), (-0.25, -2.6), (-0.6, -0.4), (-4.2, 0.2), (-0.5, 0.8)]
            q = hd.face([c + R @ V((x, 0, z)) for x, z in shp], (70, 60, 54)); layers.append([q] if q else [])
    return layers, L, fog, amb, fs, fe

def frame_low(t):
    pos, tgt, fov = cam_shot(t); cam = Camera.look(tuple(pos), tuple(tgt)); sc = scene(t)
    layers, L, fog, amb, fs, fe = world(t)
    R = Renderer(W, H, fog=fog)
    img, vi, zb = zrender(R, cam, layers, L, fov=fov, fog_start=fs, fog_end=fe, ambient=amb, return_z=True)
    a = look.outline(np.asarray(img).astype(np.float32), zb)
    if sc in ('road', 'capt', 'wing'): a = np.clip((a * np.array([0.94, 0.98, 1.08]) - 60) * 1.3 + 84, 0, 255)
    elif sc in ('cave', 'stand'): a = np.clip((a * np.array([1.05, 0.99, 0.93]) - 90) * 1.3 + 112, 0, 255)
    else: a = np.clip((a * np.array([1.04, 1.0, 0.94]) - 128) * 1.3 + 122, 0, 255)
    return post.ps1(Image.fromarray(a.astype(np.uint8)), levels=6), vi

# ======================= 2D overlays: quest HUD, the seal insert =======================
def text_w(s, sc): return len(s) * 6 * sc - sc
def hud_overlay(im, t):
    d = ImageDraw.Draw(im)
    show = (t < T0['02'] - 0.2) or (ws('09', 1) - 0.1 <= t < tend('10') + 0.5)
    if show:
        s = 'QUEST: SLAY THE DRAGON'; sc = 6; x = int(540 - text_w(s, sc) / 2); y = 96
        pop = 1.0 if t > 0.25 and not (ws('09', 1) - 0.1 <= t < ws('09', 1) + 0.15) else 1.12
        look.draw_cells(d, look.text_cells(s, x, y, sc, (255, 214, 96)), 4)
        st = sm(seg01(t, T0['10'] + 0.75, T0['10'] + 1.05))
        if st > 0 and t >= T0['10']:
            x0 = x + text_w('QUEST: ', sc); x1 = x0 + int((text_w(s, sc) - text_w('QUEST: ', sc)) * st)
            d.rectangle([x0 - 6, y + 14, x1 + 6, y + 30], fill=(0, 0, 0)); d.rectangle([x0 - 2, y + 18, x1 + 2, y + 26], fill=(255, 70, 60))
    if t >= T_FIN + 0.1:
        u = seg01(t, T_FIN + 0.1, T_FIN + 0.35); s1 = 'QUEST UPDATED'; sc1 = 8 if u >= 1 else 10
        look.draw_cells(d, look.text_cells(s1, int(540 - text_w(s1, sc1) / 2), 110, sc1, (255, 214, 96)), 4)
        if t >= T_FIN + 0.55:
            s2 = 'PROTECT THE VILLAGE'; sc2 = 6; look.draw_cells(d, look.text_cells(s2, int(540 - text_w(s2, sc2) / 2), 220, sc2, (246, 242, 230)), 4)
def seal_overlay(im, t):
    a, b = T0['02'] + 0.5, T0['03'] - 0.08
    if not (a <= t < b): return
    u = sm(seg01(t, a, a + 0.22)) * (1 - sm(seg01(t, b - 0.1, b))); w2 = int(360 * u); h2 = int(300 * u)
    if w2 < 10: return
    cx, cy = 540, 760; d = ImageDraw.Draw(im)
    d.rectangle([cx - w2 - 14, cy - h2 - 14, cx + w2 + 14, cy + h2 + 14], fill=(0, 0, 0))
    d.rectangle([cx - w2, cy - h2, cx + w2, cy + h2], fill=(166, 138, 96))
    for k in range(0, 2 * h2, 14): d.rectangle([cx - w2, cy - h2 + k, cx + w2, cy - h2 + k + 3], fill=(146, 120, 82))
    for k in range(0, 2 * w2, 18): d.rectangle([cx - w2 + k, cy - h2, cx - w2 + k + 3, cy + h2], fill=(154, 128, 88))
    if u > 0.95:
        d.ellipse([cx - 320, cy - 180, cx + 320, cy - 40], outline=(150, 30, 28), width=12)
        for s, y, sc in (('HEARTHMOOR', cy - 128, 7), ('WINTER TAX', cy + 70, 8)):
            look.draw_cells(d, look.text_cells(s, int(cx - text_w(s, sc) / 2), y, sc, (150, 30, 28)), 0)
        d.rectangle([cx + w2 - 150, cy + h2 - 120, cx + w2 - 30, cy + h2 - 20], fill=(70, 96, 150))      # her patch, in the corner
        for k in range(5): d.rectangle([cx + w2 - 150, cy + h2 - 110 + 20 * k, cx + w2 - 30, cy + h2 - 106 + 20 * k], fill=(210, 200, 160))
COL = {'N': (242, 238, 226), 'K': (120, 230, 255), 'D': (255, 128, 48), 'W': (255, 190, 90), 'C': (190, 190, 196)}
SUBS = look.Subtitles(SCR, LINES, W, H, S, COL, title_key='01', card_y=0.68, card_sc=8.0, card_n=15,
                      hil={'DRAGON', 'TAXES', 'WINTER', 'KING', 'STARVED', 'RICH.', 'SOLDIERS', 'KILL', 'SLAY', 'THIEF.', 'STAND', 'GOLD', 'KEEP', 'WATCH', 'GUARDING'})
def poster_overlay(im, t):
    a, b = T_POST, T_LOOP
    if not (a <= t < b): return
    u = sm(seg01(t, a, a + 0.2)); w2 = int(330 * u); h2 = int(430 * u)
    if w2 < 10: return
    cx, cy = 540, 820; d = ImageDraw.Draw(im)
    d.rectangle([cx - w2 - 14, cy - h2 - 14, cx + w2 + 14, cy + h2 + 14], fill=(0, 0, 0)); d.rectangle([cx - w2, cy - h2, cx + w2, cy + h2], fill=(226, 206, 160))
    for k in range(0, 2 * h2, 22): d.rectangle([cx - w2, cy - h2 + k, cx + w2, cy - h2 + k + 3], fill=(214, 192, 146))
    if u > 0.95:
        for s, y, sc, col in (('BY ORDER OF', cy - 360, 5, (90, 60, 40)), ('THE KING', cy - 300, 7, (90, 60, 40)), ('QUEST:', cy - 150, 8, (150, 30, 28)),
                              ('SLAY THE', cy - 60, 9, (150, 30, 28)), ('DRAGON', cy + 40, 10, (150, 30, 28)), ('REWARD: 500 GOLD', cy + 200, 5, (90, 60, 40))):
            look.draw_cells(d, look.text_cells(s, int(cx - text_w(s, sc) / 2), y, sc, col), 0)
        d.ellipse([cx - 60, cy + 290, cx + 60, cy + 410], fill=(160, 30, 30)); d.ellipse([cx - 40, cy + 310, cx + 40, cy + 390], fill=(196, 50, 44))
def frame_final(t):
    if t >= T_LOOP: t = t - DUR                                                   # the loop tail IS the start: frame N-1 -> frame 0 is one step
    img, vi = frame_low(t); arr = post.upscale(img, S)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); hud_overlay(im, t); seal_overlay(im, t); poster_overlay(im, t)
    arr = np.asarray(im).astype(np.float32)
    return SUBS.apply(arr, t)
def frame(t): return Image.fromarray(np.clip(frame_final(t), 0, 255).astype(np.uint8)).resize((W, H), Image.BOX)

TEST = os.environ.get('TEST')
if TEST and __name__ == '__main__':
    ts = [float(x) for x in TEST.split(',')] if TEST != 'all' else [round(x, 2) for x in np.arange(0, DUR, float(os.environ.get('STEP', '0.5')))]
    ims = [Image.fromarray(np.clip(frame_final(x), 0, 255).astype(np.uint8)).resize((270, 480), Image.LANCZOS) for x in ts]
    per = int(os.environ.get('PER', '8')); rows = (len(ims) + per - 1) // per; shp = Image.new('RGB', (min(per, len(ims)) * 272, rows * 498), (30, 30, 30))
    dd = ImageDraw.Draw(shp)
    for i, (im, x) in enumerate(zip(ims, ts)): shp.paste(im, ((i % per) * 272, (i // per) * 498)); dd.text(((i % per) * 272 + 4, (i // per) * 498 + 483), f'{x:.2f} {scene(x)}', fill=(255, 255, 0))
    shp.save(os.environ.get('TEST_OUT', 'test_dt.png')); print('test written', DUR); sys.exit()

# ======================= QA manifest =======================
QA = dict(fps=FPS, dur=DUR, W=W, frame=frame, chars={}, geom=lambda t, name, st, V_: [], camera=lambda t: cam_shot(t)[0], min_cam_dist=0.3,
          camera_ok=lambda p: True, allow_jump=[], weapon_events=[],
          scenes=[dict(id='cave', t0=0.0, t1=T_OUT, action='frame 0: sword at the dragon, the claw opens, sacks + gold spill; the patch; the seal; the dragon: the king did'),
                  dict(id='road', t0=T_OUT, t1=T_CAP, action='the night road: torches, the Last Castle'),
                  dict(id='capt', t0=T_CAP, t1=T_STAND, action='the captain on horseback points'),
                  dict(id='stand', t0=T_STAND, t1=T_WB, action='the knight looks, turns his sword on the captain; the dragon steps beside him'),
                  dict(id='wing', t0=T_WB, t1=T_DAWN, action='one wingbeat: torches out, horses bolt, the captain backs away last'),
                  dict(id='dawn', t0=T_DAWN, t1=T_SKY, action='dawn square: coins handed out; the kid waves at the shadow'),
                  dict(id='sky', t0=T_SKY, t1=T_FIN, action='the dragon dips a wing, circles above the road'),
                  dict(id='fin', t0=T_FIN, t1=T_LOOP, action='QUEST UPDATED - PROTECT THE VILLAGE; the knight lowers his sword, turns to the villagers; the king posts the quest again'),
                  dict(id='loop', t0=T_LOOP, t1=DUR, action='LOOP: back in the cave, the moment before frame 0')],
          texts=lambda: [('hud', 'QUEST: SLAY THE DRAGON', 6), ('hud', 'QUEST UPDATED', 8), ('hud', 'PROTECT THE VILLAGE', 6), ('seal', 'HEARTHMOOR', 7)])

# ======================= AUDIO =======================
LVL = {'02': 0.5, '04': 1.5, '06': 0.0, '08': 0.5, '11': 1.5, '13': 0.5}
def build_audio(path):
    import soundfile as _sf
    from scipy.signal import fftconvolve
    s = Sound(DUR, loop=False, seed=91); sr = s.sr; n = s.n; t = s.t
    BED = np.zeros(n); FX = np.zeros(n); MUS = np.zeros(n)
    def put(buf, x, t0, v=1.0):
        i = int(t0 * sr)
        if i >= n or i + len(x) <= 0: return
        if i < 0: x = x[-i:]; i = 0
        j = min(n, i + len(x)); buf[i:j] += (x * v)[:j - i]
    def nb(t0, d, lo, hi, v, seed, shape=2, buf=None): put(FX if buf is None else buf, s.filt_short(s.noise(d, seed), lo=lo, hi=hi) * np.sin(np.pi * s.T(d) / d) ** shape, t0, v)
    def tone(t0, m, d, v, dec=3.0, att=0.005, glide=0.0, buf=None, harm=(1.0,)):
        f = 440 * 2 ** ((m - 69) / 12); tt = s.T(d); fr = f * (1 + glide * tt / d); ph = np.cumsum(fr) / sr
        x = sum(a * np.sin(2 * np.pi * ph * (k + 1)) for k, a in enumerate(harm))
        put(FX if buf is None else buf, x * np.minimum(1, tt / att) * np.exp(-tt * dec), t0, v)
    def mask(a, b, r=0.15): return np.clip(np.minimum((t - a) / r, (b - t) / r), 0, 1)
    def thud(t0, f=60, v=0.1, d=0.3): tt = s.T(d); put(FX, np.sin(2 * np.pi * f * tt * (1 - 0.3 * tt / d)) * np.exp(-tt * 14), t0, v)
    def clink(t0, v=0.03, seed=0):
        for k, f in enumerate((2900, 4100, 5300)): tt = s.T(0.3); put(FX, np.sin(2 * np.pi * f * (1 + 0.02 * hsh(seed + k)) * tt) * np.exp(-tt * (18 + 5 * k)), t0 + k * 0.03, v * (1 - 0.25 * k))
    def piano(t0, m, v=0.06, d=3.0, buf=None):
        tone(t0, m, d, v, dec=1.3, harm=(1.0, 0.45, 0.2, 0.08), buf=buf); tone(t0 + 0.002, m + 12, d, v * 0.15, dec=2.0, buf=buf)
    def hooves(t0, t1, rate, v, seed=0, fade=None):
        k = 0; tb = t0
        while tb < t1:
            for j, dt_ in enumerate((0.0, 0.07, 0.15)):
                vv = v * (1 if fade is None else max(0.0, 1 - (tb - t0) / fade)); thud(tb + dt_, 70 + 10 * j, vv * (0.8 + 0.3 * hsh(k * 3 + j, seed)), 0.12)
                nb(tb + dt_, 0.05, 300, 2500, vv * 0.4, seed + k * 3 + j, 1)
            tb += 1.0 / rate; k += 1
    def whinny(t0, v=0.03, seed=0):
        d = 1.1; tt = s.T(d); f = 600 + 500 * np.sin(np.pi * tt / d) ** 0.7; vib = 1 + 0.04 * np.sin(2 * np.pi * 11 * tt)
        ph = np.cumsum(f * vib) / sr; x = (np.sin(2 * np.pi * ph) + 0.5 * np.sin(4 * np.pi * ph) + 0.25 * np.sin(6 * np.pi * ph)) * np.sin(np.pi * tt / d) ** 0.6 * np.exp(-tt * 1.2)
        put(FX, x + 0.3 * s.filt_short(s.noise(d, seed), lo=800, hi=4000) * np.exp(-tt * 3), t0, v)
    # ---- CAVE: drone, drips, torches, the dragon's breath
    cave = mask(-1, T_DAWN, 0.05)
    lit = 1 - np.clip((t - T_GUST) / 0.12, 0, 1)
    BED += s.filt(s.rng.normal(0, 1, n), lo=30, hi=180) * 0.05 * cave
    BED += soft_fire(s, level=0.018, mask=cave * lit * (t < T_OUT + 99), seed=5)
    for k in range(int(T_DAWN / 1.3)):
        tb = 0.4 + k * 1.3 + 0.7 * hsh(k, 4); tone(tb, 90 + 6 * hsh(k, 5), 0.25, 0.012, dec=22, glide=-0.2, buf=BED)
    br = 0.5 - 0.5 * np.cos(2 * np.pi * t / 3.4)
    BED += s.filt(s.rng.normal(0, 1, n), lo=60, hi=350) * 0.04 * br ** 2 * cave * (t < T_WB)
    # frame 0: sword ring, claw creak + growl, sacks on stone, the gold
    tone(0.0, 98, 1.4, 0.03, dec=2.0, harm=(1.0, 0.5, 0.3)); nb(0.0, 0.3, 3000, 9000, 0.02, 1, 1)
    tt = s.T(1.2); put(FX, s.filt_short(s.noise(1.2, 3), lo=40, hi=220) * np.sin(np.pi * tt / 1.2) * (1 + 0.5 * np.sin(2 * np.pi * 7 * tt)), CLAW_T[0], 0.18)
    for i, (tg, torn, dl) in enumerate(DROPS):
        thud(DROP_T + dl + 0.32, 58 + 6 * i, 0.12); nb(DROP_T + dl + 0.32, 0.12, 200, 1800, 0.05, 10 + i, 1)
    for i, (a, b, c) in enumerate(COINS): clink(DROP_T + 0.32 + 0.6 * a + 0.5, 0.012 + 0.012 * c, seed=i * 3)
    # the patch: cloth, two soft piano notes, the hug
    nb(T_PATCH + 0.35, 0.5, 400, 3000, 0.02, 21, 2); nb(T_PATCH + 1.0, 0.8, 600, 2500, 0.012, 22, 2)
    piano(T_PATCH + 0.9, 57, 0.05, 3.0, buf=MUS); piano(T_PATCH + 1.8, 64, 0.045, 3.0, buf=MUS); piano(T_PATCH + 1.82, 60, 0.03, 3.0, buf=MUS)
    thud(T0['02'] + 0.5, 80, 0.05, 0.2)                                                                      # the seal stamp
    # the dragon lowers its head: a rumble; the sacks pushed; the coin in her fist
    tt = s.T(1.0); put(FX, s.filt_short(s.noise(1.0, 31), lo=25, hi=120) * np.sin(np.pi * tt / 1.0), T0['04'] - 0.7, 0.2)
    nb(T0['05'] + 0.1, 1.1, 250, 1600, 0.05, 32, 1); clink(T0['05'] + 0.6, 0.02, 4); clink(T0['05'] + 0.9, 0.015, 7)
    clink(ws('06', 1), 0.025, 9); nb(T0['06'] + 0.2, 0.7, 2000, 7000, 0.012, 33, 2)
    # ---- the night: wind, horn, hooves; the captain; the knight turns
    night = mask(T_OUT - 0.3, T_DAWN, 0.4)
    BED += s.filt(s.rng.normal(0, 1, n), lo=200, hi=1500) * 0.03 * night * (0.6 + 0.4 * np.sin(2 * np.pi * t * 0.3))
    tone(T_OUT + 0.2, 50, 1.6, 0.05, dec=1.0, att=0.15, harm=(1.0, 0.7, 0.5, 0.35, 0.2)); tone(T_OUT + 0.2, 57, 1.6, 0.03, dec=1.0, att=0.15, harm=(1.0, 0.6, 0.4))
    hooves(T_OUT + 0.1, T_CAP + 0.3, 2.4, 0.06, seed=40, fade=None)
    whinny(T_CAP + 0.1, 0.02, 41); nb(T_CAP + 0.4, 0.3, 1500, 6000, 0.015, 42, 1)
    for k in range(4): thud(T_STAND + 0.2 + k * 0.6, 48, 0.05, 0.35)                                       # a slow drum under the decision
    tone(T0['10'] + 0.1, 96, 1.2, 0.03, dec=2.0, harm=(1.0, 0.5, 0.3)); nb(T0['10'], 0.4, 2500, 8000, 0.03, 43, 1)
    for k in range(2): thud(T0['11'] - 0.4 + k * 0.55, 40, 0.22, 0.5)                                       # the dragon's steps
    pad = mask(T0['11'] - 0.4, T_GUST - 0.1, 0.6)
    for f, a in ((110.0, 1.0), (138.6, 0.6), (164.8, 0.5)): MUS += np.sin(2 * np.pi * f * t + a) * a * 0.016 * pad
    # ---- the wingbeat: whoosh, torches die, silence, horses bolt
    nb(T_WB + 0.3, 0.6, 100, 900, 0.06, 50, 2)
    tt = s.T(1.4); put(FX, s.filt_short(s.noise(1.4, 51), lo=30, hi=500) * np.exp(-tt * 2.2) * np.minimum(1, tt / 0.25), T_GUST - 0.3, 0.55)
    tt = s.T(1.0); put(FX, s.filt_short(s.noise(1.0, 52), lo=600, hi=3000) * np.exp(-tt * 4) * np.minimum(1, tt / 0.1), T_GUST - 0.15, 0.12)
    for i in range(7): nb(T_GUST + 0.02 * i, 0.18, 800, 5000, 0.03, 53 + i, 1)                               # pfft - the torches
    whinny(T_GUST + 0.15, 0.03, 60); whinny(T_GUST + 0.35, 0.022, 61)
    hooves(T_GUST + 0.6, T_DAWN - 0.2, 2.6, 0.06, seed=62, fade=2.5)
    hooves(T_GUST + 2.0, T_DAWN - 0.2, 2.6, 0.05, seed=70, fade=2.0)
    # ---- DAWN: birds, warm strings, coins, wingbeats overhead, the heroic note
    dn = mask(T_DAWN, T_LOOP, 0.2)
    BED += s.filt(s.rng.normal(0, 1, n), lo=200, hi=1200) * 0.022 * dn
    for k in range(int((DUR - T_DAWN) / 0.7)):
        tb = T_DAWN + k * 0.7 + 0.4 * hsh(k, 12)
        if tb > T_LOOP - 0.3: break
        for j in range(2 + k % 2): tt = s.T(0.09); put(BED, np.sin(2 * np.pi * (2900 + 800 * j + 500 * hsh(k, j)) * tt * (1 + 0.3 * tt / 0.09)) * np.sin(np.pi * tt / 0.09) ** 2, tb + j * 0.13, 0.006)
    st_ = mask(T_DAWN, T_LOOP, 0.3)
    for f, a in ((146.8, 1.0), (185.0, 0.6), (220.0, 0.55), (293.7, 0.3)): MUS += np.sin(2 * np.pi * f * t + a) * a * 0.016 * st_ * (1 + 0.15 * np.sin(2 * np.pi * 0.5 * t))
    for tk in GIVES: clink(tk, 0.025, int(tk * 10))
    for k in range(3):
        tb = T_KID - 0.1 + k * 0.42; tt = s.T(0.5); put(FX, s.filt_short(s.noise(0.5, 80 + k), lo=60, hi=700) * np.sin(np.pi * tt / 0.5) ** 2, tb, 0.15 - 0.03 * k)
    for k in range(4):
        tb = T_SKY + 1.4 + k * 0.9; tt = s.T(0.5); put(FX, s.filt_short(s.noise(0.5, 90 + k), lo=60, hi=600) * np.sin(np.pi * tt / 0.5) ** 2, tb, 0.05)
    for m, dl in ((62, 0.0), (66, 0.0), (69, 0.0), (74, 0.12)): tone(T_FIN + 0.1 + dl, m, 2.4, 0.03, dec=1.0, att=0.03, harm=(1.0, 0.6, 0.4, 0.25))     # the heroic note
    tone(T_FIN + 0.1, 50, 2.4, 0.04, dec=0.9, att=0.03, harm=(1.0, 0.7, 0.5))
    # ---- LOOP: the poster (paper, nail, a low royal horn), then the cave again, as at the start
    nb(T_POST, 0.35, 500, 4000, 0.035, 95, 1); thud(T_POST + 0.18, 75, 0.1, 0.2)
    tone(T_POST + 0.25, 45, 1.2, 0.04, dec=1.4, att=0.08, harm=(1.0, 0.7, 0.5, 0.3))
    lp = mask(T_LOOP - 0.08, DUR + 1, 0.12)
    BED += s.filt(s.rng.normal(0, 1, n), lo=30, hi=180) * 0.05 * lp + soft_fire(s, level=0.018, mask=lp, seed=5)
    BED += s.filt(s.rng.normal(0, 1, n), lo=60, hi=350) * 0.04 * (0.5 - 0.5 * np.cos(2 * np.pi * (t - DUR) / 3.4)) ** 2 * lp
    # ---- voices: RMS-levelled, the dragon gets a cave echo, ducking
    NB = np.zeros(n); wins = []
    ir_t = np.arange(int(0.9 * sr)) / sr; IR = s.rng.normal(0, 1, len(ir_t)) * np.exp(-ir_t * 5.0); IR[0] = 0; IR = IR / np.sqrt((IR ** 2).sum())
    for k_, t0 in LINES:
        a, ar = _sf.read(os.path.join(TTS_DIR, 'dt', f'{k_}.wav')); a = a if a.ndim == 1 else a.mean(1)
        a = np.interp(np.arange(int(len(a) * sr / ar)) / sr, np.arange(len(a)) / ar, a); act = np.abs(a) > 0.02 * np.abs(a).max()
        a = a * (0.12 / np.sqrt((a[act] ** 2).mean())) * 10 ** (LVL.get(k_, 0.0) / 20)
        if SCR['spk'][k_] == 'D':
            wet = fftconvolve(a, IR)[:len(a) + int(0.6 * sr)]; a = np.concatenate([a, np.zeros(len(wet) - len(a))]) + 0.35 * wet
        put(NB, a, t0); wins.append((t0, t0 + len(a) / sr))
    g = duck_envelope(n, sr, wins, -7.0, 0.05, 0.25)
    quiet = 1 - 0.7 * mask(T_GUST + 0.05, T_GUST + 0.6, 0.1)                                                  # sudden quiet after the gust
    bed = (BED * g + MUS * (0.6 + 0.4 * g)) * quiet; fx = FX * (0.55 + 0.45 * g)
    endcut = np.convolve(np.where(t < DUR - 0.05, 1.0, 0.0), np.ones(96) / 96, 'same')
    L = (bed + fx) * endcut; R_ = (np.roll(bed, 700) + np.roll(fx, 200)) * endcut
    pk = max(np.abs(L).max(), np.abs(R_).max()); gv = pk * 1.6 / np.abs(NB).max()
    s.L = L + NB * gv; s.R = R_ + NB * gv; s.reverb(0.1, length=1.4, decay=3.0)
    return s.save(path, peak=0.9)
if __name__ == '__main__' and os.environ.get('PART') == 'audio':
    print(build_audio(os.path.join(OUT, 'dragon_taxes.wav'))); sys.exit()
if __name__ == '__main__' and os.environ.get('PART'):
    a, b = map(int, os.environ['PART'].split(':'))
    import subprocess
    p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W * S}x{H * S}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', os.path.join(OUT, f'dt_{a:05d}.mp4')], stdin=subprocess.PIPE)
    vhs = post.VHS(W * S, H * S, S, grade='none', chroma=0, scan_dark=1.0, vignette=0.22, grain=0.9, band_period=1e9)
    for f in range(a, min(b, N)): p.stdin.write(vhs(frame_final(f / FPS), f, f / FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done', a, b); sys.exit()
