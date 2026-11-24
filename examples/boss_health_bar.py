"""WHAT IF THE BOSS'S HEALTH BAR WAS THE VILLAGE'S? (Insert Disc 2, 24 Nov 2026) 36 s build -> x1.2 = 30.0 s final, 9:16, nightkit HD.
Brief: briefs/boss_health_bar.md (GPT prompt, written for "the repository"; Enes: always nightkit).
Timeline = the brief's seconds x 1.2 (B()), so after tools/speedup.sh every beat lands on the brief's timestamp.
Story additions approved by Enes (24 Nov): 1) planted lantern: the guardian shields the SAME lantern that hangs at the old woman's door;
2) wordless beat: the lights come back one by one, her door lantern last, she lifts her hand to it; 3) loop: the knight raises his sword
to the castle -> frame 0 is the sword coming down.
Voices: Enes/Betul record every line (brief: no synthetic voices). Until then tts/bhb/script.json holds PLANNED durations (tools/tts/bhb.py plan)
and the film carries SFX + music + subtitles only.

Asset preview: ASSET=guardian|seal|village python examples/boss_health_bar.py -> test_bhb_<asset>.png
Frames:        TEST=0,1.5,... python examples/boss_health_bar.py -> test_bhb.png
Render:        python tools/render_parts.py examples/boss_health_bar.py --prefix bhb --audio boss_health_bar.wav --out ../renders/boss_health_bar/bhb_1x.mp4"""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera
from nightkit.zraster import zrender
from nightkit import post, look, hd, motion
import dragon_taxes as dtx                      # locked assets: the series knight, the old woman, houses, rocks, trees, torches, stars

W, H, S = 270, 480, 4
PI = math.pi
V = np.array
FPS = 24
hsh, lerp, lerp3, mixc = dtx.hsh, dtx.lerp, dtx.lerp3, dtx.mixc
sm = motion.smooth
def seg01(t, a, b): return max(0.0, min(1.0, (t - a) / (b - a))) if b > a else (1.0 if t >= b else 0.0)
def win(t, a, b, r=0.25): return sm(seg01(t, a, a + r)) * (1 - sm(seg01(t, b - r, b)))
RECUT = [(0.0, 0.3), (3.0, 2.2), (3.4, 2.4), (6.0, 4.3), (9.0, 5.7), (11.2, 7.0), (12.0, 7.4), (15.0, 9.0), (16.64, 10.4), (18.0, 11.5), (19.0, 12.2),
         (21.0, 13.4), (23.2, 15.2), (24.0, 16.2), (24.6, 16.4), (27.0, 18.2), (30.0, 21.2)]
def B(x):
    """v2 recut (Enes, 24 Nov: 20-22 s): the v1 timeline (brief seconds) mapped onto the new final seconds, x1.2 = build seconds"""
    for (a0, b0), (a1, b1) in zip(RECUT, RECUT[1:]):
        if x <= a1 or (a1, b1) == RECUT[-1]: return round(1.2 * (b0 + (b1 - b0) * (x - a0) / (a1 - a0)), 3)
SUB_LANG = os.environ.get('SUB_LANG', 'en')            # 'tr' = Turkish subtitles + HUD (voice stays)
def F(x): return round(x * 1.2, 3)                  # new final seconds -> build seconds
T_HIT = B(0.0)                                      # the sword lands (0.3 s into the video)
def nz(v): v = V(v, float); n = np.linalg.norm(v); return v / n if n > 1e-9 else v

# ======================= palette =======================
ST = (124, 118, 108); ST2 = (100, 96, 90); MOSS = (74, 96, 58); IRON = (64, 64, 72); IRON2 = (92, 92, 102)
GOLD = (236, 190, 70); CURSE = (170, 70, 255); CURSE_D = (60, 20, 90); WARM = (255, 200, 110)

# ======================= the guardian =======================
def _rock_col(base, seed):
    return lambda i, j, cl: MOSS if hsh(i * 13 + j * 7, seed) > 0.86 else hd.shade(base, 0.86 + 0.22 * hsh(i * 5 + j * 11, seed + 1))
def _rocky(seed, amt=0.08):
    return lambda p: p * (1 + amt * math.sin(p[0] * 9 + seed) * math.cos(p[1] * 7 + seed * 2) + amt * 0.6 * math.sin(p[2] * 11 + seed * 3))
def guardian(P):
    """chained stone guardian, ~3.2 m standing. P: base, yaw, kneel 0..1, hunch, twist, recoil, head=(yaw, pitch), rh_w / lh_w (world hand
    targets), eye, crack (chest light), talk. Fills P['_chest'], P['_anchor'] (chest ring), P['_rwr'], P['_lwr'], P['_rsh'], P['_lsh'], P['_head']."""
    g = P.get; base = V(g('base', (0, 0, 0)), float); Rb = hd.Ry(g('yaw', 0.0)); kn = g('kneel', 0.0)
    def Wp(p): return base + Rb @ V(p, float)
    hip = lerp(1.42, 0.98, kn)
    pel = Wp((0, hip, 0))
    lean = 0.12 + 0.42 * g('hunch', 0.0) - 0.35 * g('recoil', 0.0)
    Rc = Rb @ hd.Ry(g('twist', 0.0)) @ hd.Rx(lean) @ hd.Rz(0.12 * g('recoil', 0.0))
    chest = pel + Rc @ V((0, 0.78, 0))
    Q = []
    Q += hd.ellip(pel + Rc @ V((0, 0.12, 0)), Rc, (0.5, 0.36, 0.38), 12, 6, ST2, deform=_rocky(1), colfn=_rock_col(ST2, 3))           # hips
    Q += hd.ellip(pel + Rc @ V((0, 0.42, 0.02)), Rc, (0.46, 0.34, 0.36), 12, 6, ST2, deform=_rocky(2), colfn=_rock_col(ST2, 4))      # belly
    Q += hd.ellip(chest, Rc, (0.74, 0.5, 0.5), 14, 7, ST, deform=_rocky(3, 0.06), colfn=_rock_col(ST, 5))                         # chest
    Q += hd.bx(pel + Rc @ V((0, 0.18, 0.0)), Rc, (0.52, 0.07, 0.4), (78, 60, 44))                                                  # a leather belt
    # the chest light (cracks) and the iron ring the chain hangs from
    cl = g('crack', 1.0); cc = mixc((70, 60, 50), (255, 196, 96), cl)
    nrm = Rc @ V((0, 0, 1.0)); up = Rc @ V((0, 1.0, 0))
    for k, (x, y, a, L_) in enumerate(((0.0, 0.08, 0.0, 0.34), (0.1, 0.22, 0.7, 0.22), (-0.1, 0.24, -0.8, 0.24), (0.13, -0.08, -0.5, 0.2), (-0.12, -0.1, 0.6, 0.2))):
        c = chest + Rc @ V((x, y, 0.5)); u2 = hd.Rz(a) @ V((0, 1.0, 0))
        Q += hd.decal(c, nrm, Rc @ u2, 0.05, L_, cc, emit=cl > 0.05, lift=0.01)
    anc = chest + Rc @ V((0.0, 0.06, 0.53))
    Q += hd.lathe(anc, Rc @ hd.Rx(PI / 2), [(0.15, 0), (0.15, 0.05), (0.09, 0.07)], 10, IRON)
    P['_anchor'] = anc + nrm * 0.07; P['_chest'] = chest; P['_nrm'] = nrm
    # neck, head, collar
    hy, hp = g('head', (0.0, 0.0))
    neck = chest + Rc @ V((0, 0.46, 0.12)); RH = Rc @ hd.Rx(-lean * 0.6) @ hd.Ry(hy) @ hd.Rx(-hp)
    hc = neck + RH @ V((0, 0.22, 0.12))
    Q += hd.lathe(neck - Rc @ V((0, 0.06, 0)), Rc, [(0.3, 0), (0.3, 0.12), (0.26, 0.14)], 12, IRON2)                                    # iron collar
    Q += hd.ellip(hc, RH, (0.3, 0.3, 0.3), 12, 7, ST, deform=_rocky(6, 0.05), colfn=_rock_col(ST, 7))
    Q += hd.bx(hc + RH @ V((0, 0.07, 0.25)), RH, (0.27, 0.055, 0.07), hd.shade(ST, 0.8))                                           # brow ridge
    Q += hd.bx(hc + RH @ V((0, -0.17, 0.13)), RH, (0.21, 0.07, 0.16), hd.shade(ST, 0.9))                                           # jaw
    ey = g('eye', 1.0); ec = mixc((40, 40, 40), (150, 230, 255), ey)
    for sd in (1, -1): Q += hd.bx(hc + RH @ V((sd * 0.11, -0.005, 0.285)), RH, (0.065, 0.028, 0.012), ec, emit=ey > 0.05)
    mo = g('talk', 0.0); Q += hd.bx(hc + RH @ V((0, -0.13, 0.29)), RH, (0.1, 0.012 + 0.025 * mo, 0.01), mixc((50, 46, 44), (150, 230, 255), 0.25 + 0.75 * mo), emit=True)
    P['_head'] = hc
    # arms
    for sd, key in ((1, 'r'), (-1, 'l')):
        sh = chest + Rc @ V((sd * 0.82, 0.2, -0.02)); P['_' + key + 'sh'] = sh
        Q += hd.ellip(sh, Rc, (0.32, 0.28, 0.3), 10, 6, ST, deform=_rocky(8 + sd), colfn=_rock_col(ST, 9 + sd))
        tgt = g(key + 'h_w')
        if tgt is None: tgt = sh + Rc @ V((sd * 0.25, -1.25, 0.25))
        pole = Rb @ V((sd * 0.8, -0.4, -0.6)) if g(key + 'pole') is None else V(g(key + 'pole'), float)
        el, wr = hd.ik2(sh, V(tgt, float), 0.74, 0.7, pole)
        Q += hd.limb(sh, el, 0.21, 0.17, ST2, n=10, m=2, ref=Rc @ V((0, 0, 1.0)), bulge=0.05, colfn=lambda i, j: hd.shade(ST2, 0.9 + 0.15 * ((i + j) % 2)))
        Q += hd.ellip(el, Rc, (0.17, 0.17, 0.17), 8, 4, ST2)
        Q += hd.limb(el, wr, 0.17, 0.15, ST, n=10, m=2, ref=Rc @ V((0, 0, 1.0)), bulge=0.04)
        d = nz(wr - el); Q += hd.limb(wr - d * 0.16, wr + d * 0.02, 0.2, 0.2, IRON, n=10, m=1, ref=Rc @ V((0, 0, 1.0)))         # shackle
        palm = nz(V(g(key + 'palm', (0, 0, 0)), float)) if g(key + 'palm') is not None else nz(Rc @ V((-sd * 1.0, 0, 0.3)))
        side = nz(np.cross(d, palm)); hcn = wr + d * 0.17
        Q += hd.ellip(hcn, np.column_stack([side, d, palm]), (0.15, 0.19, 0.1), 9, 5, ST, deform=_rocky(11 + sd, 0.05))
        cur = g(key + 'curl', 0.6)
        for f_ in range(3):                                                                                                  # three thick fingers
            b0 = hcn + d * 0.14 + side * (f_ - 1) * 0.085; tip = b0 + d * 0.12 * (1 - cur) + palm * 0.12 * cur + d * 0.05
            Q += hd.limb(b0, tip, 0.045, 0.038, ST, n=6, m=1, ref=palm)
        Q += hd.limb(hcn + side * sd * 0.0 + palm * 0.04 - d * 0.04, hcn + palm * 0.13 - side * 0.1 + d * 0.04, 0.045, 0.038, ST, n=6, m=1, ref=d)
        P['_' + key + 'wr'] = wr; P['_' + key + 'hand'] = hcn; P['_' + key + 'palmv'] = palm
    # legs: kneel = right knee down, left foot forward
    for sd, key in ((1, 'r'), (-1, 'l')):
        hp_ = pel + Rb @ V((sd * 0.3, -0.12, 0))
        stand = V((sd * 0.36, 0.12, 0.05))
        kneelf = V((sd * 0.34, 0.14, -0.62)) if sd > 0 else V((sd * 0.4, 0.12, 0.62))
        ft = Wp(lerp3(tuple(stand), tuple(kneelf), kn))
        kp = Rb @ V((0, 0.0 if sd > 0 else 0.3, 1.0))
        knee, an = hd.ik2(hp_, ft, 0.66, 0.66, kp)
        Q += hd.limb(hp_, knee, 0.24, 0.19, ST2, n=10, m=2, ref=Rb @ V((0, 0, 1.0)), bulge=0.05)
        Q += hd.ellip(knee, Rb, (0.19, 0.19, 0.19), 8, 4, ST)
        Q += hd.limb(knee, an, 0.19, 0.16, ST, n=10, m=2, ref=Rb @ V((0, 0, 1.0)), bulge=0.04)
        fd = Rb @ V((0, 0, 1.0)); fd = fd if (sd < 0 or kn < 0.5) else nz(fd * 0.3 + V((0, -1.0, 0)) * 0.0 + fd)
        Q += hd.bx(an + fd * 0.12 - V((0, 0.06, 0)), Rb, (0.17, 0.08, 0.26), ST2)
        P['_' + key + 'knee'] = knee
    return [q for q in Q if q]

# ======================= chain, lantern, seal =======================
def sagline(p0, p1, sag, n=24, floor=0.04):
    p0 = V(p0, float); p1 = V(p1, float); pts = []
    for i in range(n + 1):
        u = i / n; p = p0 + (p1 - p0) * u; p[1] = max(floor, p[1] - sag * 4 * u * (1 - u)); pts.append(p)
    return pts
def chain(pts, col=(104, 104, 116), step=0.14, big=1.3, skip=None):
    """links every `step` m along the polyline; alternating 90-degree roll. skip(s) -> True leaves a link out (broken chain)"""
    Q = []; pts = [V(p, float) for p in pts]; seg = [np.linalg.norm(b - a) for a, b in zip(pts, pts[1:])]; Lt = sum(seg)
    s = step * 0.5; k = 0
    while s < Lt:
        acc = 0.0
        for i, L_ in enumerate(seg):
            if acc + L_ >= s: u = (s - acc) / max(L_, 1e-9); c = pts[i] + (pts[i + 1] - pts[i]) * u; d = nz(pts[i + 1] - pts[i]); break
            acc += L_
        if skip is None or not skip(s / Lt):
            a, b = hd.frame_for(d, (0, 1, 0) if abs(d[1]) < 0.9 else (1, 0, 0))
            if k % 2: a, b = b, a
            Rl = np.column_stack([a, d, b])
            Q += hd.ellip(c, Rl, (0.045 * big, 0.08 * big, 0.016 * big), 8, 3, hd.shade(col, 0.9 + 0.2 * (k % 2)))
        s += step; k += 1
    return Q
def at_len(pts, f):
    """point and direction at fraction f of a polyline"""
    pts = [V(p, float) for p in pts]; seg = [np.linalg.norm(b - a) for a, b in zip(pts, pts[1:])]; s = f * sum(seg); acc = 0.0
    for i, L_ in enumerate(seg):
        if acc + L_ >= s or i == len(seg) - 1: u = min(1.0, (s - acc) / max(L_, 1e-9)); return pts[i] + (pts[i + 1] - pts[i]) * u, nz(pts[i + 1] - pts[i])
        acc += L_
def lantern(c, on=1.0, t=0.0, seed=0, R=None, k=1.0):
    """small iron lantern with a warm flame; the same model hangs at the old woman's door (planted detail)"""
    c = V(c, float); R = np.eye(3) if R is None else R; Q = []
    fl = on * (0.85 + 0.15 * math.sin(t * 17 + seed) * math.sin(t * 7.3 + seed * 2))
    core = mixc((50, 40, 36), (255, 214, 120), fl)
    Q += hd.bx(c, R, (0.07 * k, 0.09 * k, 0.07 * k), core, emit=fl > 0.05)                                                     # the glass + flame
    for sx in (-1, 1):
        for sz in (-1, 1): Q += hd.bx(c + R @ V((sx * 0.072 * k, 0, sz * 0.072 * k)), R, (0.012 * k, 0.1 * k, 0.012 * k), (40, 36, 40))   # cage posts
    Q += hd.bx(c - R @ V((0, 0.1 * k, 0)), R, (0.09 * k, 0.015 * k, 0.09 * k), (40, 36, 40))
    Q += hd.lathe(c + R @ V((0, 0.095 * k, 0)), R, [(0.1 * k, 0), (0.02 * k, 0.08 * k)], 4, (46, 40, 44), cap1=False)
    Q += hd.lathe(c + R @ V((0, 0.19 * k, 0)), R @ hd.Rx(PI / 2), [(0.035 * k, -0.008 * k), (0.035 * k, 0.008 * k)], 8, (46, 40, 44))      # ring
    return Q
def half_disc(c, R, r, th, a0, a1, col, n=10):
    """a slab: disc sector from angle a0 to a1 (radians, in the disc plane), thickness th; R columns = (u, v, normal)"""
    c = V(c, float); u, v, w = R[:, 0], R[:, 1], R[:, 2]
    ring = [c + (u * math.cos(a0 + (a1 - a0) * i / n) + v * math.sin(a0 + (a1 - a0) * i / n)) * r for i in range(n + 1)]
    fr = [p - w * th / 2 for p in ring]; bk = [p + w * th / 2 for p in ring]; Q = []
    Q.append(hd.face([c - w * th / 2] + fr, col, inside=c)); Q.append(hd.face([c + w * th / 2] + bk[::-1], hd.shade(col, 0.8), inside=c))
    for i in range(n): Q.append(hd.face([fr[i], fr[i + 1], bk[i + 1], bk[i]], hd.shade(col, 0.75), inside=c))
    Q.append(hd.face([fr[0], bk[0], c + w * th / 2, c - w * th / 2], hd.shade(col, 0.7), inside=c))
    Q.append(hd.face([fr[-1], c - w * th / 2, c + w * th / 2, bk[-1]], hd.shade(col, 0.7), inside=c))
    return [q for q in Q if q]
CROWN_OLD = [(-0.27, -0.13), (0.27, -0.13), (0.27, 0.03), (0.33, 0.2), (0.15, 0.06), (0.0, 0.25), (-0.15, 0.06), (-0.33, 0.2), (-0.27, 0.03)]
CROWN_PCS = [[(-0.32, -0.17), (0.32, -0.17), (0.32, 0.03), (-0.32, 0.03)], [(-0.32, 0.03), (-0.13, 0.03), (-0.32, 0.29)],
             [(-0.14, 0.03), (0.14, 0.03), (0.0, 0.33)], [(0.13, 0.03), (0.32, 0.03), (0.32, 0.29)]]
JEWELS = [[(x - 0.04, y), (x, y - 0.04), (x + 0.04, y), (x, y + 0.04)] for x, y in ((-0.3, 0.3), (0.0, 0.35), (0.3, 0.3))]
BAND_GEMS = [[(x - 0.04, -0.1), (x + 0.04, -0.1), (x + 0.04, -0.04), (x - 0.04, -0.04)] for x in (-0.19, 0.0, 0.19)]
def clipx(pts, side):
    """clip a convex 2D polygon to x>=0 (side 1) / x<=0 (side -1); side 0 = no clip. The decal's u axis is mirrored (-w normal), so flip x."""
    pts = [(-x, y) for x, y in pts]
    if side == 0: return pts
    out = []
    f = (lambda p: p[0] * side >= 0)
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        if f(a): out.append(a)
        if f(a) != f(b): k = a[0] / (a[0] - b[0]); out.append((0.0, a[1] + (b[1] - a[1]) * k))
    return out
def seal_faces(c, R, glow=0.0, crack=0.0, split=0.0, t=0.0):
    """the king's seal: iron disc, gold crown emblem facing -normal (R[:,2]); split > 0 breaks it into two halves that fall apart"""
    Q = []; c = V(c, float); u, v, w = R[:, 0], R[:, 1], R[:, 2]
    rim = mixc((96, 90, 100), (190, 110, 255), glow)
    for side, (a0, a1) in ((-1, (PI / 2, 3 * PI / 2)), (1, (-PI / 2, PI / 2))):
        off = u * side * 0.12 * split - v * 0.35 * split * (1 if side < 0 else 0.4); Rs = R
        cc = c + off
        sh_ = [V((side * 0.3, 0.4, 0.0)), V((side * 0.3, 0.78, 0.0)), V((side * 0.16, 0.92, 0.0)), V((0.0, 0.94, 0.0))]   # the padlock shackle (half)
        if split > 0: sh_ = sh_[:3]
        for a_, b_ in zip(sh_, sh_[1:]): Q += hd.limb(cc + R @ a_, cc + R @ b_, 0.065, 0.065, IRON2, n=6, m=1)
        Q += hd.bx(cc + R @ V((side * 0.3, 0.42, 0.0)), R, (0.1, 0.06, 0.1), IRON)                                # shackle collar
        Q += half_disc(cc, Rs, 0.52, 0.12, a0, a1, IRON)
        Q += half_disc(cc - w * 0.065, Rs, 0.43, 0.02, a0, a1, rim)
        Q += half_disc(cc - w * 0.075, Rs, 0.39, 0.02, a0, a1, (70, 66, 78))
        for k in range(6):                                                                                     # rivets
            a = a0 + (a1 - a0) * (k + 0.5) / 6; Q += hd.bx(cc - w * 0.07 + (u * math.cos(a) + v * math.sin(a)) * 0.47, R, (0.025, 0.025, 0.02), IRON2)
    # the crown: convex pieces (band + three spikes) + jewels; once split, each piece is clipped to its half
    cg = mixc(GOLD, (255, 236, 160), glow)
    for side in ((0,) if split <= 0 else (-1, 1)):
        off = (u * side * 0.12 * split - v * 0.35 * split * (1 if side < 0 else 0.4)) if side else V((0.0, 0, 0))
        for pc, col, dz in [(p_, cg, 0.09) for p_ in CROWN_PCS] + [(j_, (230, 50, 50), 0.1) for j_ in JEWELS] + [(b_, (60, 120, 230), 0.1) for b_ in BAND_GEMS]:
            pp = clipx(pc, -side)
            pp = [(x * 0.78, y * 0.78 - 0.04) for x, y in pp]
            if len(pp) >= 3: Q += hd.poly_decal(c + off - w * dz, -w, v, pp, col, emit=glow > 0.3)
    if split <= 0:                                                                                                  # keyhole
        Q += hd.decal(c - w * 0.1 - v * 0.3, -w, v, 0.07, 0.07, (14, 12, 16), lift=0.0) + hd.decal(c - w * 0.1 - v * 0.36, -w, v, 0.035, 0.1, (14, 12, 16), lift=0.0)
    if crack > 0 and split <= 0:                                                                                   # the crack line runs top -> bottom
        pts = [(0.0, 0.5), (0.05, 0.3), (-0.04, 0.12), (0.04, -0.05), (-0.05, -0.25), (0.02, -0.5)]
        k = max(2, int(round(crack * len(pts))))
        for (x0, y0), (x1, y1) in zip(pts[:k - 1], pts[1:k]):
            m_ = ((x0 + x1) / 2, (y0 + y1) / 2); L_ = math.hypot(x1 - x0, y1 - y0); a = math.atan2(x1 - x0, y1 - y0)
            Q += hd.decal(c - w * 0.1 + u * (-m_[0]) + v * m_[1], -w, hd.Rz(0) @ (v * math.cos(a) - u * math.sin(a) * -1), 0.035, L_ + 0.02, (255, 244, 220), emit=True, lift=0.0)
    return [q for q in Q if q]

# ======================= world layout =======================
G0 = (0.0, 0.0, 2.45); GYAW = PI                  # guardian kneels facing -z
K0 = (0.15, 0.0, 0.72)                              # knight faces +z
SEAL_C = V((2.35, 1.45, 1.15)); SEAL_N = nz((-0.35, 0.0, -1.0))    # the seal faces the knight
def seal_R():
    w = -SEAL_N; v = V((0, 1.0, 0)); u = nz(np.cross(v, w)); return np.column_stack([u, v, w])
SEAL_R = seal_R()
SH_L = SEAL_C + SEAL_R @ V((-0.12, 0.93, 0.0)); SH_R = SEAL_C + SEAL_R @ V((0.12, 0.93, 0.0))   # where the two chain ends loop through the shackle
PILLAR = (2.45, 0.0, 1.35)
HILL_X0, HILL_K = 20.0, 0.6                          # the village hillside: rises from x = 20 towards +x, facing the ruin
def hill_y(x, z): return max(0.0, HILL_K * (x - HILL_X0))
VIL0 = V((41.0, 0.6 * 21.0, 0.5))                        # the village, on its hill across the plain (+x), houses facing the ruin (-x)
VYAW = PI / 2; RV = hd.Ry(VYAW)
def vil(p): return VIL0 + RV @ V(p, float)
def vil_g(p):
    """village-local point -> world, standing on the hillside"""
    w = vil(p); w[1] = hill_y(w[0], w[2]) + float(p[1]); return w
def xform(Q, R, d):
    d = V(d, float); out = []
    for q in Q:
        if q is None: continue
        q = dict(q); q['p'] = [tuple(R @ V(p_, float) + d) for p_ in q['p']]; q['c'] = R @ V(q['c'], float) + d; q['n'] = R @ V(q['n'], float); out.append(q)
    return out
def shift(Q, d):
    d = V(d, float); out = []
    for q in Q:
        if q is None: continue
        q = dict(q); q['p'] = [tuple(V(p_, float) + d) for p_ in q['p']]; q['c'] = V(q['c'], float) + d; out.append(q)
    return out
CAST0 = V((-75.0, 0.0, 40.0))                      # the king's castle on its hill (-x, behind the ruin)
GA = [V((-1.55, 0.06, 3.05)), V((1.45, 0.06, 3.15))]   # floor rings of the wrist chains
GROUND_CH = [SH_R, SEAL_C + SEAL_R @ V((0.75, 0.2, 0.1)), SEAL_C + SEAL_R @ V((0.85, -0.6, 0.1)), V((3.3, 0.06, 1.8)), V((4.2, 0.04, 4.6))]
for _k in range(1, 13):
    _p = V((4.2, 0, 4.6)) + (vil((-2.0, 0, -5.0)) - V((4.2, 0, 4.6))) * (_k / 12); GROUND_CH.append(V((_p[0], hill_y(_p[0], _p[2]) + 0.05, _p[2])))

# ======================= the village lights (the HUD counts these) =======================
# 9 windows + the old woman's door lantern (index 9). die / relight times in build seconds.
HOUSES = [(0.0, 0.0, 0.0, 4.2, 3.2, 2.8, (176, 160, 132), (110, 58, 46)), (-5.2, 1.2, 0.25, 3.6, 3.0, 2.6, (166, 154, 128), (96, 60, 48)),
          (5.0, 0.8, -0.2, 4.0, 3.2, 3.0, (180, 166, 140), (120, 70, 52)), (-2.6, 6.5, 0.1, 3.8, 3.0, 2.8, (170, 156, 130), (104, 62, 50)),
          (3.2, 6.8, -0.1, 3.4, 3.0, 2.6, (160, 150, 126), (92, 58, 46)), (9.0, 3.2, -0.35, 3.6, 3.0, 2.7, (170, 160, 134), (110, 64, 50))]
def _hpt(hi, lx, ly):
    x, z, yaw, w, d, h, _, _ = HOUSES[hi]; R = RV @ hd.Ry(yaw); g = vil_g((x, 0, z)); return g + R @ V((lx, ly, -d / 2 - 0.04)), R @ V((0, 0, -1.0))
WIN = []
for hi, lx, ly in ((1, -0.8, 1.6), (1, 0.9, 1.6), (2, -1.0, 1.7), (2, 1.0, 1.7), (3, 0.0, 1.6), (4, -0.7, 1.5), (5, 0.6, 1.6), (0, -0.05, 2.3), (0, -1.1, 1.6)):
    WIN.append(_hpt(hi, lx, ly))
DOOR = _hpt(0, 0.95, 1.0)
LANT_L = V((0.95 + 0.75, 1.82, -1.6 - 0.32))          # her door lantern (village-local), on a bracket right of the door
LANT_W = vil(LANT_L) + V((0, hill_y(*vil((0, 0, 0))[[0, 2]]) - VIL0[1], 0))
WOM0 = tuple(vil((1.0, 0.0, -2.75)))                # on her house's terrace
T_VWIN = T_HIT + 0.1; T_VBACK = F(1.15)              # v3.1: the cut to the village window right after the impact
DIE = {5: T_VWIN + 0.14, 9: F(5.1)}
# v3 (GPT review 2): the seal strike -> chain breaks -> current back -> the village relights to 10/10, one sequence
T_IMPACT2 = B(19.0); T_REV = F(12.95); T_RELIT = F(13.55); T_KFALL = F(14.4); T_FREE = F(16.4); T_STAND = F(15.0)
RELIGHT = {9: F(13.62), 5: F(13.8)}
T_SIP = F(7.9)                                       # v4: the life siphon (village -> chain -> seal -> the king's crown) becomes visible
T_HALO = F(14.6); T_CROWN = F(14.85); T_KNEEL = F(15.05)   # the king: halo breaks, crown falls, he drops to one knee
def light_on(i, t):
    if i not in DIE: return 1.0
    a = DIE[i]; b = RELIGHT[i]
    if t < a: return 1.0
    fo = 0.3                                                                    # the opening window goes out WITH the hit
    if t < a + fo: return max(0.0, 1 - (t - a) / fo) * (0.55 + 0.45 * (math.sin(t * 60) > 0))   # flicker out
    if t < b: return 0.0
    return min(1.0, (t - b) / 0.2) * (0.7 + 0.3 * (math.sin((t - b) * 50) > -0.3) if t < b + 0.3 else 1.0)
def village_count(t):
    return sum(1 for i in range(10) if (i not in DIE) or t < DIE[i] or t >= RELIGHT[i] + 0.05)

# ======================= timeline (build seconds; the brief's timeline x 1.2) =======================
TTS_DIR = os.environ.get('TTS_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tts'))
SCR = json.load(open(os.path.join(TTS_DIR, 'bhb', 'script.json')))
SLOT = {'01': F(0.4), '02': F(3.1), '03': F(6.55), '04': F(9.55), '05': F(16.9)}
KEYS = ['01', '02', '03', '04', '05']
def _lines():
    out = []; prev = 0.0
    for k in KEYS: t0 = max(SLOT[k], prev + 0.2); out.append((k, round(t0, 3))); prev = t0 + SCR['dur'][k]
    return out
LINES = _lines(); T0 = dict(LINES); T_0Q = T_FREE
def tend(k): return T0[k] + SCR['dur'][k]
T_QUEST = tend('05') + 0.05                          # the quest UI appears right after the guardian's line
T_TURN = 1e9                                         # v4: no turn; QUEST COMPLETE, then the end
DUR = round(T_QUEST + F(1.1), 2); N = int(round(DUR * FPS))
T_CASTLE = max(F(7.05), tend('03') + 0.05)            # own takes: the castle cut waits for the end of 'Why?'
T_SHOUT = B(16.64)
T_CU = B(18.6)                                       # cut to the close-up of the seal, just before the swing lands
CUTS = [('hit', 0.0), ('vwin', T_VWIN), ('hit', T_VBACK), ('track', F(3.0)), ('wom2', F(4.7)), ('why', F(6.0)), ('castle', T_CASTLE), ('siphon', T_SIP), ('king', F(9.4)),
        ('strike', F(11.0)), ('sealcu', T_CU), ('reverse', T_REV), ('vwin2', T_RELIT), ('kfall', T_KFALL), ('quest', T_FREE)]
def scene(t):
    cur = 'hit'
    for nm, a in CUTS:
        if t >= a: cur = nm
    return cur
PULSES = [(T_HIT + 0.05, 'out'), (F(3.0), 'out')]     # curse pulses along the chain to the village

def talking(t, key):
    if key not in T0: return 0.0
    for a, b, _ in SCR['sent'][key]:
        if T0[key] + a <= t < T0[key] + b: return 1.0 if (t * 7.3 + 0.2 * math.sin(t * 13)) % 1.0 < 0.55 else 0.0
    return 0.0

# ======================= poses =======================
CHEST_LOCAL_HIT = None
def guardian_pose(t):
    P = dict(base=G0, yaw=GYAW, kneel=1.0, hunch=0.55, twist=0.0, recoil=0.0, head=(0.0, -0.15), eye=1.0, crack=1.0)
    lan = guardian_lantern_pos(t)
    # hands cup the lantern (left palm under it, right hand shielding the side facing the knight)
    P['lh_w'] = tuple(lan + V((0.16, -0.2, 0.06))); P['lpalm'] = (0.2, 1.0, 0.0); P['lcurl'] = 0.35
    P['rh_w'] = tuple(lan + V((-0.2, 0.05, -0.12))); P['rpalm'] = (0.8, 0.0, 0.4); P['rcurl'] = 0.55
    # the opening hit: delayed recoil, a chain pull
    r = sm(seg01(t, T_HIT + 0.03, T_HIT + 0.25)) * (1 - sm(seg01(t, T_HIT + 0.5, T_HIT + 1.4)))
    P['recoil'] = 0.55 * r; P['twist'] = -0.25 * r; P['head'] = (0.2 * r, -0.15 + 0.3 * r)
    P['eye'] = 1.0 - 0.6 * r
    # the dark wave hits its back: it curls over the lantern
    wv = 0.0
    P['hunch'] += 0.35 * wv; P['head'] = (P['head'][0] - 0.15 * wv, P['head'][1] - 0.25 * wv)
    sc = scene(t)
    if t >= B(9.0) and t < B(15.0): P['hunch'] += 0.2
    # every pulse drains the chest light a little
    P['crack'] = 1.0 - 0.5 * sum(win(t, a, a + 1.0, 0.2) for a, _ in PULSES)
    # the strike on the seal: it flinches with the chain, then the light comes back
    if t >= T_IMPACT2 - 0.05:
        j = win(t, T_IMPACT2, T_IMPACT2 + 0.8, 0.12); P['recoil'] = 0.25 * j; P['crack'] = 1.0
        P['head'] = (0.0, lerp(-0.15, 0.25, sm(seg01(t, T_IMPACT2 + 0.6, T_IMPACT2 + 1.6))))
    if t >= T_STAND - 0.5:                                                          # chain pull, then it rises
        pull = win(t, T_STAND - 0.5, T_STAND + 0.1, 0.2); P['recoil'] += 0.12 * pull
        u = sm(seg01(t, T_STAND, T_STAND + 1.8)); P['kneel'] = 1.0 - u; P['hunch'] = lerp(P['hunch'], 0.05, u)
        P['head'] = (0.0, lerp(0.25, -0.35, sm(seg01(t, T_STAND + 1.2, T_STAND + 2.2))))    # looks down at the knight
    P['talk'] = talking(t, '05')
    if t >= B(27.0): P['eye'] = 1.0 + 0.0 * P['talk']
    return P
def guardian_lantern_pos(t):
    """the lantern sits in front of its chest, low; when it stands it holds it up at its side"""
    k = sm(seg01(t, T_STAND, T_STAND + 1.8))
    wv = 0.0
    a = V(G0) + V((0.0, 1.12 - 0.12 * wv, -0.72 + 0.12 * wv)); b = V(G0) + V((-0.55, 1.75, -0.55))
    return a + (b - a) * k
def guardian_lantern_on(t):
    return 1.0 - 0.3 * sum(win(t, a, a + 1.0, 0.2) for a, _ in PULSES)

HIT_SWING = 0.0
def knight_pose(t):
    """(P, sword tip target or None, sword length)"""
    P = dict(base=K0, yaw=0.0, eyes='open', mouth='neutral', brow=0.6, lean=0.08, cape_sway=0.12 * math.sin(t * 1.4))
    P['lh'] = (-0.28, 1.0, 0.12); P['lgrip'] = 0.6
    G = guardian_pose(t); gp = dict(G); guardian(gp)
    hit = gp['_rsh'] + V((0.05, 0.05, -0.3))
    sh = V(K0) + V((-0.2, 1.48, 0.0))
    if t < B(6.0) or scene(t) == 'shield':
        # the strike at frame 0 (blade on the guardian's shoulder) -> recoil back to guard
        u = sm(seg01(t, T_HIT + 0.08, T_HIT + 0.7))
        strike_h = sh + nz(hit - sh) * 0.62; guard_h = V(K0) + V((-0.25, 1.15, 0.42))
        hand = strike_h + (guard_h - strike_h) * u
        tip = hit + (guard_h + V((0.1, 1.1, 0.5)) - hit) * u
        if t < T_HIT:                                                                # frame 0: the swing is already coming down
            a = 0.25 + 0.75 * (t / T_HIT) ** 1.6; up_h = V(K0) + V((-0.45, 1.85, -0.05))
            hand = up_h + (strike_h - up_h) * a; tip_up = up_h + V((-0.2, 0.75, -0.55))
            tip = tip_up + (hit - tip_up) * a; P['lean'] = 0.05 + 0.15 * a; P['twist'] = 0.3 * (1 - a)
        P['rh_w'] = tuple(hand); P['lean'] = 0.2 - 0.12 * u
        if scene(t) == 'shield':                                                     # draws his arm back for another strike
            a = sm(seg01(t, B(6.15), B(6.9)))
            back_h = V(K0) + V((-0.42, 1.78, -0.12))
            P['rh_w'] = tuple(guard_h + (back_h - guard_h) * a); tip = V(P['rh_w']) + nz(V((-0.35, 0.75, -0.55)) * a + (V((0.1, 1.0, 0.6))) * (1 - a)) * 0.9
            P['twist'] = 0.3 * a; P['mouth'] = 'open' if talking(t, '03') else 'neutral'; P['brow'] = 0.9
            P['head'] = (-0.2 * a, 0.12, 0.0)
        return P, tip
    # point at the seal (sword lowered)
    if t < B(18.0):
        P['brow'] = -0.1; P['head'] = (0.45 * sm(seg01(t, B(15.0), B(15.5))), 0.05, 0.0); P['yaw'] = -0.35 * sm(seg01(t, B(15.1), B(15.7)))
        low = sm(seg01(t, B(15.0), B(15.25))); pt = sm(seg01(t, B(15.3), B(15.85)))
        sh_w = V(K0) + V((-0.2, 1.45, 0.0)); to_seal = nz(SEAL_C - sh_w)
        down_h = V(K0) + V((-0.26, 0.95, 0.3)); point_h = sh_w + to_seal * 0.55 + V((0, -0.05, 0))
        P['rh_w'] = tuple(down_h + (point_h - down_h) * pt)
        tip = V(P['rh_w']) + nz(V((-0.3, -0.9, 0.6)) * (1 - pt) + to_seal * pt) * 0.9
        P['mouth'] = 'open' if talking(t, '03') else 'neutral'
        if t >= T_SHOUT: P['head'] = (0.45, 0.05, 0.0)
        if F(6.0) <= t < F(7.9):                                                  # looks down the chain, then up to the castle: "Why?"
            a = sm(seg01(t, F(6.25), F(6.7))); P['head'] = (lerp(0.5, -0.6, a), lerp(0.3, -0.25, a), 0.0); P['yaw'] = -0.45 * a; P['brow'] = 0.8
        return P, tip
    # the strike on the seal: pivot, step, swing
    if t < T_FREE:
        piv = sm(seg01(t, B(18.0), B(18.6))); stp = seg01(t, B(18.2), B(18.85))
        k1 = V((1.05, 0.0, 0.35)); P['base'] = tuple(V(K0) + (k1 - V(K0)) * sm(stp))
        if 0 < stp < 1: P['walk'] = sm(stp) * 4.0; P['stride'] = 0.35
        yaw_s = math.atan2(SEAL_C[0] - k1[0], SEAL_C[2] - k1[2]); P['yaw'] = lerp(0.0, yaw_s, piv)
        Rk = hd.Ry(P['yaw']); shw = V(P['base']) + Rk @ V((-0.2, 1.48, 0.0))
        wind = sm(seg01(t, B(18.3), B(18.8))); sw = sm(seg01(t, B(18.8), T_IMPACT2))
        up_h = V(P['base']) + Rk @ V((-0.42, 1.82, -0.1)); hit_h = shw + nz(SEAL_C - shw) * 0.62
        rest_h = V(P['base']) + Rk @ V((-0.25, 1.15, 0.42))
        hand = rest_h + (up_h - rest_h) * wind
        hand = hand + (hit_h - hand) * sw
        P['rh_w'] = tuple(hand); P['brow'] = 0.9; P['lean'] = 0.08 + 0.14 * sw; P['twist'] = 0.3 * wind * (1 - sw)
        tip_up = up_h + Rk @ V((-0.3, 0.7, -0.6)); tip_hit = SEAL_C + SEAL_N * 0.02
        tip = tip_up * (1 - sw) + tip_hit * sw if wind > 0 else V(P['base']) + Rk @ V((-0.4, 0.05, 0.9))
        if t >= T_IMPACT2 + 0.25:                                                  # recovers, looks at the guardian
            r = sm(seg01(t, T_IMPACT2 + 0.25, T_IMPACT2 + 1.0)); P['rh_w'] = tuple(V(hit_h) + (V(P['base']) + Rk @ V((-0.26, 0.95, 0.25)) - V(hit_h)) * r)
            tip = tip_hit + (V(P['base']) + Rk @ V((-0.4, 0.05, 0.95)) - tip_hit) * r
            P['head'] = (-0.6 * sm(seg01(t, T_IMPACT2 + 0.6, T_IMPACT2 + 1.3)), 0.0, 0.0)
        return P, tip
    # the guardian rises; the knight faces it, looks up; then turns to the castle and raises his sword
    k1 = V((1.05, 0.0, 0.35)); P['base'] = tuple(k1)
    yaw_g = math.atan2(G0[0] - k1[0], G0[2] - k1[2]); yaw_c = math.atan2(CAST0[0] - k1[0], CAST0[2] - k1[2])
    tr = sm(seg01(t, T_TURN, T_TURN + 0.8))
    P['yaw'] = lerp(yaw_g, yaw_c, tr); Rk = hd.Ry(P['yaw'])
    P['head'] = (0.0, lerp(0.0, 0.32, sm(seg01(t, T_STAND + 0.8, T_STAND + 2.0))) * (1 - tr), 0.0); P['brow'] = 0.4 + 0.4 * tr
    rest_h = V(P['base']) + Rk @ V((-0.26, 0.95, 0.25)); up_h = V(P['base']) + Rk @ V((-0.32, 2.0, 0.3))
    ra = sm(seg01(t, T_TURN + 0.4, T_TURN + 1.2))
    P['rh_w'] = tuple(rest_h + (up_h - rest_h) * ra)
    tip = V(P['rh_w']) + nz(Rk @ V((0.0, 0.9, 0.55)) * ra + Rk @ V((-0.15, -1.0, 0.7)) * (1 - ra)) * 0.9
    return P, tip
def knight_layers(t):
    P, tip = knight_pose(t); Q = dtx.knight(P)
    g = dtx.grip_pt(P, 'r', 0.06, 0.0); d = nz(V(tip) - g)
    L_ = 0.85 if (t >= T_HIT + 0.7 or t < T_HIT - 0.12) else max(0.6, min(1.05, float(np.linalg.norm(V(tip) - g)) - 0.02))
    return Q + hd.sword(g, d, P['_rpalm'], length=L_), P

def woman_pose(t):
    P = dict(base=WOM0, yaw=PI + VYAW, eyes='open', mouth='neutral', brow=-0.4, lean=0.02, cape_sway=0.1 * math.sin(t * 1.7), hair_sway=0.0)
    sc = scene(t)
    if sc == 'wom1':
        a = sm(seg01(t, B(3.05), B(3.5)))
        P['head'] = (0.5 * (1 - a), 0.12 * a, 0.0)                                         # from the dying window to the hill
        P['rh'] = lerp3((0.2, 0.9, 0.08), (0.26, 1.48, 0.32), a); P['rpalm'] = (0, 0, 1.0); P['rgrip'] = 0.05
        P['brow'] = -0.9; P['eyes'] = 'wide' if a > 0.5 else 'open'
        P['mouth'] = 'open' if talking(t, '02') else ('neutral' if a < 0.5 else 'o')
    elif sc in ('wom2', 'stream'):
        P['head'] = (0.0, 0.32, 0.0); P['brow'] = -0.7; P['mouth'] = 'open' if talking(t, '02') else 'neutral'
        P['lh'] = (-0.16, 1.15, 0.16); P['lgrip'] = 0.7
    elif sc == 'shout':
        P['head'] = (0.0, 0.18, 0.0); P['brow'] = 0.2; P['mouth'] = 'open' if talking(t, '06') else 'o'
        P['rh'] = (0.3, 1.5, 0.42); P['rpalm'] = (-0.3, -1.0, 0.0); P['rgrip'] = 0.3
        P['lh'] = (-0.2, 1.3, 0.22); P['lgrip'] = 0.1; P['lpalm'] = (0, 0, 1.0)
    elif sc == 'lamp':
        u = sm(seg01(t, B(23.25), B(23.75)))
        P['base'] = tuple(vil((0.95, 0.0, -2.6))); P['yaw'] = -2.55; P['head'] = (0.25, 0.05, 0.0); P['mouth'] = 'smile' if t > RELIGHT[9] + 0.15 else 'neutral'; P['brow'] = 0.3 if t > RELIGHT[9] else -0.5
        P['eyes'] = 'open'
        rest = vil((0.95, 0.0, -2.6)) + V((0, 0.92, 0)) + RV @ V((0.25, 0, 0.1)); near = LANT_W + RV @ V((-0.24, -0.08, -0.12))
        P['rh_w'] = tuple(rest + (near - rest) * u); P['rpalm'] = tuple(RV @ V((1.0, 0.0, 0.2))); P['rpalm_local'] = False; P['rgrip'] = 0.15
    return P

# ======================= sets =======================
_SETS = {}
def get_set(nm):
    if nm not in _SETS: _SETS[nm] = {'ruin': ruin_set, 'plain': plain_set, 'village': village_set, 'sky': sky_set, 'cwall': castle_wall_set}[nm]()
    return _SETS[nm]
TORCH = [(-2.9, 2.35, 3.6), (3.8, 2.35, 3.4), (-2.4, 2.2, 6.2)]
def ruin_set():
    """the dungeon entrance: a ring of broken pillars on a stone floor, the dark dungeon gate behind the knight, the seal pillar"""
    Q = dtx.ground(-9, 9, -7, 9, 0.75, [(92, 88, 82), (84, 80, 76), (100, 94, 86), (78, 74, 70)], seed=21)
    for i in range(11):                                                                     # broken pillars
        a = -0.5 + 2 * PI * i / 11; r = 5.4 + 0.5 * hsh(i, 3); x = r * math.sin(a); z = 1.5 + r * math.cos(a)
        if abs(x) < 2.2 and z < -1.5: continue
        h = 1.2 + 2.4 * hsh(i, 4)
        Q += hd.lathe((x, 0, z), hd.Ry(i), [(0.48, 0), (0.42, 0.15), (0.36, 0.25), (0.36, h), (0.3, h + 0.15)], 8, hd.shade(ST, 0.85 + 0.2 * hsh(i, 5)), cap1=True)
        Q += dtx.rock((x + 0.5, 0.15, z + 0.4), 0.25 + 0.2 * hsh(i, 6), ST2, seed=i)
    # the gate behind the knight (-z)
    GZ = -4.6
    for sx in (-1, 1): Q += hd.bx((sx * 1.6, 1.9, GZ), np.eye(3), (0.5, 1.9, 0.5), ST2)
    Q += hd.bx((0, 4.05, GZ), np.eye(3), (2.2, 0.3, 0.55), ST2) + hd.bx((0, 1.75, GZ + 0.1), np.eye(3), (1.1, 1.75, 0.05), (14, 12, 18))
    for i in range(8):
        a = PI * (0.08 + 0.84 * hsh(i, 9)); x = 7.6 * math.cos(a) * (1 if i % 2 else -1); z = -3.0 - 2.5 * hsh(i, 10)
        Q += dtx.rock((x, 0.3, z), 0.6 + 0.6 * hsh(i, 11), ST2, seed=i + 5)
    # the seal pillar + its iron bracket
    px, _, pz = PILLAR
    Q += hd.bx((px, 0.45, pz), hd.Ry(0.33), (0.36, 0.45, 0.36), ST2) + hd.bx((px, 0.95, pz), hd.Ry(0.33), (0.3, 0.06, 0.3), ST)
    Q += hd.bx((px, 1.0, pz) + V((0, 0, 0)), hd.Ry(0.33), (0.06, 0.12, 0.06), IRON)
    Q += hd.limb((px, 0.95, pz), SEAL_C + SEAL_R @ V((0, -0.3, 0.12)), 0.05, 0.05, IRON, n=6, m=1)
    for x, y, z in TORCH:
        Q += hd.lathe((x * 1.05, 0, z * 1.02 if z > 0 else z), np.eye(3), [(0.34, 0), (0.3, y - 0.3)], 8, ST2) + hd.bx((x, y - 0.25, z), np.eye(3), (0.06, 0.08, 0.06), (50, 40, 32))
    for c in GA: Q += hd.lathe(c, hd.Rx(PI / 2), [(0.12, -0.02), (0.12, 0.02)], 8, IRON) + hd.bx(c - V((0, 0.03, 0)), np.eye(3), (0.15, 0.03, 0.15), IRON2)
    return [q for q in Q if q]
def plain_set():
    """the dark plain between the ruin and the village, the road, trees, the castle hill"""
    Q = dtx.ground(-120, 20, 9, 130, 3.0, [(34, 44, 36), (30, 40, 34), (40, 48, 38)], seed=31) + dtx.ground(-120, 20, -60, -12, 3.0, [(34, 44, 36), (30, 40, 34)], seed=34)
    Q += dtx.ground(-120, -9, -12, 9, 3.0, [(34, 44, 36), (30, 40, 34)], seed=32) + dtx.ground(9, 20, -12, 9, 3.0, [(34, 44, 36), (30, 40, 34)], seed=33)
    for j in range(16):                                                                     # the road to the village
        e_ = vil((0.0, 0.0, -8.0)); e_[1] = 0.02; s_ = V((6.5, 0.02, 0.5)); p0 = s_ + (e_ - s_) * (j / 16); p1 = s_ + (e_ - s_) * ((j + 1) / 16)
        sd = nz(np.cross(p1 - p0, (0, 1, 0))) * 1.2
        p0 = p0 + V((0, hill_y(p0[0], p0[2]), 0)); p1 = p1 + V((0, hill_y(p1[0], p1[2]), 0))
        Q.append(hd.face([p0 - sd, p1 - sd, p1 + sd, p0 + sd], hd.shade((74, 66, 56), 0.9 + 0.15 * hsh(j, 2))))
    for i in range(40):
        x = -90 + 110 * hsh(i, 41); z = -50 + 160 * hsh(i, 42)
        if abs(x) < 10 and abs(z) < 10: continue
        if hill_y(x, z) > 0.0: continue
        if abs(z - 0.5) < 4 and 0 < x < 40: continue
        Q += dtx.tree(x, z, 4 + 4 * hsh(i, 43), col=(26, 40, 36), seed=i)
    # castle hill + the castle (cold, a few red windows)
    cx, cz = CAST0[0], CAST0[2]
    Q += hd.ellip((cx, -8, cz), np.eye(3), (40, 26, 26), 18, 7, (30, 36, 40), v1=PI * 0.5)
    Q += hd.ellip((cx - 10, -12, cz - 45), np.eye(3), (40, 26, 30), 16, 6, (26, 32, 38), v1=PI * 0.5)
    cy = 17.0; CS = (64, 62, 76)
    Q += hd.bx((cx, cy + 3.0, cz), np.eye(3), (8.5, 3.0, 3.5), CS)
    for dx, h in ((-8.5, 11), (8.5, 10), (-2.8, 16), (3.2, 13)):
        Q += hd.lathe((cx + dx, cy, cz), np.eye(3), [(1.6, 0), (1.6, h)], 8, CS) + hd.lathe((cx + dx, cy + h, cz), np.eye(3), [(2.1, 0), (0.05, 3.6)], 8, (44, 36, 56), cap1=False)
        Q += hd.decal((cx + dx, cy + h * 0.72, cz - 1.62), (0, 0, -1.0), (0, 1, 0), 0.7, 1.0, (230, 70, 60), emit=True)
        Q += hd.decal((cx + dx + 1.62, cy + h * 0.72, cz), (1.0, 0, 0), (0, 1, 0), 0.7, 1.0, (230, 70, 60), emit=True)
    for k in range(5): Q += hd.decal((cx - 5 + 2.5 * k, cy + 3.5, cz - 3.52), (0, 0, -1.0), (0, 1, 0), 0.5, 0.8, (220, 70, 60), emit=True)
    for k in range(3): Q += hd.decal((cx + 8.52, cy + 3.5, cz - 2 + 2 * k), (1.0, 0, 0), (0, 1, 0), 0.5, 0.8, (220, 70, 60), emit=True)
    return [q for q in Q if q]
def village_set():
    Q = []
    for j in range(14):                                                                      # the hillside
        for i in range(10):
            x0 = HILL_X0 + 5.0 * j; x1 = x0 + 5.0; z0 = -45 + 9 * i; z1 = z0 + 9
            q = hd.face([(x0, hill_y(x0, 0), z0), (x0, hill_y(x0, 0), z1), (x1, hill_y(x1, 0), z1), (x1, hill_y(x1, 0), z0)], hd.shade((54, 66, 50), 0.85 + 0.25 * hsh(i * 7 + j, 52)))
            Q += [q] if q else []
    def put(L_, at):                                                                         # local faces built at local (x, *, z) -> world on the slope
        g = vil_g(at); return shift(xform([q for q in L_ if q], RV, VIL0), (0, g[1] - VIL0[1], 0))
    for (x, z, yaw, w, d, h, wl, rf) in HOUSES:
        Q += put(dtx.house(x, z, yaw, w, d, h, wl, rf) + hd.bx((x, -1.2, z), hd.Ry(yaw), (w / 2 + 0.15, 1.2, d / 2 + 0.15), (92, 86, 80)), (x, 0, z))
        Q += put(dtx.ground(x - w / 2 - 1.2, x + w / 2 + 1.2, z - d / 2 - 2.6, z + d / 2 + 0.6, 0.7, [(96, 88, 74), (88, 82, 70), (104, 94, 78)], seed=51 + int(x)), (x, 0, z))
    bx_, bz = 1.0, 11.0                                                                       # the bell tower
    Q += put(hd.bx((bx_, 2.5, bz), np.eye(3), (1.0, 4.5, 1.0), (150, 140, 120)) + hd.lathe((bx_, 7.0, bz), hd.Ry(PI / 4), [(1.5, 0), (0.05, 2.2)], 4, (100, 56, 44), cap1=False)
             + hd.decal((bx_, 5.9, bz - 1.02), (0, 0, -1.0), (0, 1, 0), 0.9, 1.0, (30, 26, 30)) + hd.lathe((bx_, 5.55, bz - 0.6), np.eye(3), [(0.36, 0), (0.28, 0.35), (0.12, 0.55)], 8, (190, 150, 70)), (bx_, 0, bz))
    Q += put(hd.limb(LANT_L + V((0, 0.33, 0.33)), LANT_L + V((0, 0.33, 0)), 0.02, 0.02, (44, 38, 40), n=5, m=1)          # her lantern bracket
             + hd.limb(LANT_L + V((0, 0.33, 0)), LANT_L + V((0, 0.2, 0)), 0.012, 0.012, (44, 38, 40), n=4, m=1), (0, 0, 0))
    for i in range(6): Q += put(hd.lathe((-7 + 2.8 * i, 0, -6.5), np.eye(3), [(0.06, -0.3), (0.06, 1.0)], 4, (80, 62, 44)), (-7 + 2.8 * i, 0, -6.5))   # a fence
    return [q for q in Q if q]
def sky_set():
    def col(e):
        stops = [(0.0, (44, 40, 70)), (0.12, (30, 30, 62)), (0.4, (16, 18, 42)), (1.0, (8, 10, 24))]
        for (a, ca), (b, cb) in zip(stops, stops[1:]):
            if e <= b: return mixc(ca, cb, (e - a) / (b - a))
        return stops[-1][1]
    Q = hd.ellip((0, -6, 30), np.eye(3), (190, 150, 190), 28, 12, (20, 20, 40), v1=PI * 0.53, closed=False, colfn=lambda i, j, cl: col(max(0.0, cl[1] / 150)))
    for q in Q: q['emit'] = True
    Q += dtx.sky_disc((40, 46, 170), 5.0, (226, 230, 244)) + dtx.stars(7, 90, 175, 8, 80, -110, 110)
    for i in range(6):
        cc = (40, 40, 66); x = -90 + 36 * i; y = 26 + 14 * hsh(i, 61)
        C_ = hd.ellip((x, y, 168), np.eye(3), (18 + 8 * hsh(i, 62), 2.5, 4), 10, 4, cc)
        for q in C_: q['emit'] = True
        Q += C_
    return [q for q in Q if q]

# ======================= curse: pulses along the chain, the dark wave, the reverse current =======================
def chest_chain_pts(t):
    G = guardian_pose(t); gp = dict(G); guardian(gp); a = gp['_anchor']; b = SH_L
    taut = win(t, T_HIT, T_HIT + 0.9, 0.08) + 0.6 * win(t, T_STAND - 0.5, T_STAND + 0.1, 0.2)
    return sagline(a, b, 0.32 * (1 - 0.8 * min(1.0, taut)) + 0.02 * math.sin(t * 2.0), n=20), gp
def full_route(t):
    pts, _ = chest_chain_pts(t); return pts + [SEAL_C] + GROUND_CH
def pulse_heads(t):
    """[(position, strength)] of curse pulses travelling guardian -> seal -> village (speed in fractions/s of the route)"""
    out = []
    if t >= T_IMPACT2: return out
    for a, kind in PULSES:
        u = (t - a) / 2.3
        if 0 <= u <= 1:
            route = full_route(t); pts_c, _ = chest_chain_pts(t)
            Lc = sum(np.linalg.norm(V(b_) - V(a_)) for a_, b_ in zip(pts_c, pts_c[1:])); Lt = sum(np.linalg.norm(V(b_) - V(a_)) for a_, b_ in zip(route, route[1:]))
            fc = Lc / Lt                                                          # the guardian -> seal part gets 55 % of the time (readable)
            f = (u / 0.55) * fc if u < 0.55 else fc + (u - 0.55) / 0.45 * (1 - fc)
            for k in range(10):
                ff = f - 0.006 * k * (0.15 if u < 0.55 else 1.0)
                if 0 <= ff <= 1: p, _ = at_len(route, ff); out.append((p, 1.0 - 0.08 * k))
    return out
def curse_faces(t):
    Q = []; L = []
    for p, s in pulse_heads(t):
        r = 0.06 + 0.05 * s; c = mixc(CURSE_D, CURSE, s)
        for ang in (0.0, PI / 2):
            dx, dz = r * math.cos(ang), r * math.sin(ang)
            q = hd.face([p + V((-dx, 0, -dz)), p + V((0, r * 1.3, 0)), p + V((dx, 0, dz)), p + V((0, -r * 1.3, 0))], c, emit=True); Q += [q] if q else []
    heads = pulse_heads(t)
    if heads: L.append((tuple(heads[0][0] + V((0, 0.4, 0))), (170, 80, 255), 0.8))
    # the dark wave: shards rolling in from behind the guardian (+z), breaking over its back
    if False:
        u = seg01(t, B(6.1), B(8.4))
        for i in range(70):
            z = 9.0 - 6.5 * u + 3.0 * hsh(i, 71) - 1.2 * (1 if hsh(i, 75) > 0.5 else 0) * u
            x = -3.0 + 6.0 * hsh(i, 72); y = 0.4 + 3.2 * hsh(i, 73) + 0.4 * math.sin(t * 3 + i)
            if z < G0[2] + 0.4 and abs(x) < 1.6 and y < 3.2: z = G0[2] + 0.4 + 0.3 * hsh(i, 74); x += math.copysign(0.9, x) * u     # splits around its back
            fade = 1 - seg01(t, B(9.0), B(9.8)); s = (0.12 + 0.14 * hsh(i, 76)) * fade
            if s < 0.02: continue
            c = mixc((24, 8, 40), (120, 40, 200), hsh(i, 77))
            q = hd.face([(x - s, y, z), (x, y + s * 1.6, z + s * 0.3), (x + s, y - s * 0.4, z)], c, emit=True); Q += [q] if q else []
        L.append(((0.0, 2.0, G0[2] + 1.5), (140, 60, 230), 0.35 * win(t, B(6.4), B(9.4), 0.4)))
    # after the seal breaks: the current reverses, races back along the ground chain and up into the sky to the castle
    if False:
        u = seg01(t, T_REV, T_REV + 0.9)
        back = GROUND_CH[::-1] + [SEAL_C, SEAL_C + V((-3, 4, 0.5)), SEAL_C + V((-25, 14, 10)), CAST0 + V((0, 22, 0))]
        for k in range(70):
            f = u * 1.3 - 0.0045 * k
            if 0 <= f <= 1:
                p, _ = at_len(back, f); r = 0.16 + 0.45 * min(1.0, np.linalg.norm(p - SEAL_C) / 14.0); c = mixc(CURSE, CURSE_D, k / 70)
                for ang in (0.0, PI / 2):
                    dx, dz = r * math.cos(ang), r * math.sin(ang)
                    q = hd.face([p + V((-dx, 0, -dz)), p + V((0, r * 1.3, 0)), p + V((dx, 0, dz)), p + V((0, -r * 1.3, 0))], c, emit=True); Q += [q] if q else []
    return Q, L

# ======================= the king (castle wall) + the stolen life =======================
KING = hd.spec(h=1.78, build=1.12, skin=(214, 176, 150), hair=(214, 210, 204), hair_style='short', beard=(220, 216, 210), eye=(70, 60, 50), brow=(200, 196, 190),
               tunic=(96, 30, 110), tunic2=(76, 22, 90), skirt=0.86, pants=(76, 22, 90), boots=(50, 36, 30), belt=(200, 160, 60), buckle=(240, 200, 80),
               gloves=(200, 160, 60), cloak=(150, 24, 36), cloak_len=1.15, collar=(236, 232, 226))
KING0 = V((CAST0[0], 23.0, CAST0[2] - 2.2))                     # on the castle's main wall (top at y = 23)
LIFE = (255, 214, 110)
def crown_q(c, R, glow=0.0):
    col = mixc(GOLD, (255, 240, 170), glow); Q = hd.lathe(c, R, [(0.115, 0.0), (0.122, 0.075)], 10, col)
    for k in range(5):
        a = 2 * PI * k / 5; Q += hd.bx(c + R @ V((0.118 * math.sin(a), 0.1, 0.118 * math.cos(a))), R @ hd.Ry(a), (0.028, 0.035, 0.01), col)
    Q += hd.bx(c + R @ V((0, 0.04, 0.124)), R, (0.02, 0.02, 0.01), (220, 40, 50), emit=glow > 0.3)
    return Q
def king_pose(t):
    P = dict(base=tuple(KING0), yaw=PI - 0.2, eyes='open', mouth='smile', brow=0.5, lean=-0.04, cape_sway=0.08 * math.sin(t * 1.3))
    P['rh'] = (0.42, 1.42, 0.22); P['lh'] = (-0.42, 1.42, 0.22); P['rgrip'] = 0.2; P['lgrip'] = 0.2; P['head'] = (0.0, -0.12, 0.0)
    if t >= T_HALO - 0.1:
        a = sm(seg01(t, T_HALO, T_HALO + 0.35)); P['eyes'] = 'wide'; P['mouth'] = 'o'; P['brow'] = -0.6
        P['rh'] = lerp3((0.42, 1.42, 0.22), (0.12, 1.25, 0.2), a); P['lh'] = lerp3((-0.42, 1.42, 0.22), (-0.14, 1.2, 0.18), a)
        P['head'] = (0.0, lerp(-0.12, 0.15, a), 0.0)
    k = sm(seg01(t, T_KNEEL, T_KNEEL + 0.45))
    if k > 0:
        P['crouch'] = 0.43 * k; P['rf'] = lerp3((0.12, 0.07, 0.0), (0.14, 0.07, 0.33), k); P['lf'] = lerp3((-0.12, 0.07, 0.0), (-0.13, 0.06, -0.52), k)
        P['lkpole'] = (0, -0.8, 1.0); P['lfdir'] = None; P['head'] = (0.0, lerp(0.15, 0.45, k), 0.0); P['lean'] = 0.15 * k
        P['eyes'] = 'sad' if t > T_KNEEL + 0.5 else 'wide'; P['mouth'] = 'o'
    return P
def king_layers(t):
    P = king_pose(t); Q = hd.human(KING, P); G = []; L = []
    hc = P['_head']; RH = P['_RH']; on = 1.0 if t < T_HALO else 0.0
    sip = seg01(t, F(9.4), F(9.9)) if t < T_IMPACT2 else max(0.0, 1 - (t - T_IMPACT2) / 0.6)
    c0 = hc + RH @ V((0, 0.105, 0))
    if t < T_CROWN: Q += crown_q(c0, RH, glow=0.4 + 0.6 * sip)
    else:                                                                           # it falls off his head, bounces on the stones
        u = t - T_CROWN; y = c0[1] + 0.9 * u - 5.5 * u * u; fl = KING0[1] + 0.05
        if y < fl: y = fl + 0.12 * abs(math.sin(u * 9)) * math.exp(-u * 4)
        c = V((c0[0] + 0.35 * min(u, 0.6), y, c0[2] - 0.55 * min(u, 0.7))); Q += crown_q(c, hd.Rz(min(1.5, 3.5 * u)) @ hd.Rx(-min(1.2, 2.5 * u)))
    # the immortality halo: a gold ring of shards over his head; it flickers and shatters
    hx = hc + V((0, 0.42, 0)); n_ = 14
    for i in range(n_):
        a = 2 * PI * i / n_ + t * 0.8; d = V((math.cos(a), 0, math.sin(a))); p = hx + d * 0.3
        if t >= T_HALO:
            u = t - T_HALO
            if u > 0.7: continue
            p = p + d * 1.4 * u + V((0, 0.8 * u - 4.0 * u * u, 0))
        fl = 1.0 if t < T_HALO - 0.15 else (0.4 + 0.6 * (int(t * 30) % 2))
        col = mixc((90, 70, 30), (255, 226, 130), fl * (1 if t < T_HALO else max(0, 1 - (t - T_HALO) / 0.7)))
        q = hd.face([p + V((0, 0.05, 0)), p + d * 0.05, p - V((0, 0.05, 0)), p - d * 0.05], col, emit=True); Q += [q] if q else []
    if t < T_HALO + 0.2: G.append((hx, (255, 220, 120), 1.3)); L.append((tuple(hx + V((0, 0.2, -0.8))), (255, 210, 120), 0.9))
    G.append((c0, (255, 210, 110), 0.6 + 0.8 * sip)) if t < T_CROWN else None
    return Q, G, L
def castle_wall_set():
    cx, cz = CAST0[0], CAST0[2]; Q = []
    for k in range(-4, 5):                                                          # crenellations on the front edge, open in front of the king
        if abs(k) <= 1: continue
        Q += hd.bx((cx + k * 0.95, 23.35, cz - 3.3), np.eye(3), (0.3, 0.35, 0.2), (78, 76, 90))
    Q += hd.bx((cx, 23.55, cz - 0.9), np.eye(3), (0.55, 0.55, 0.12), (70, 30, 80)) + hd.bx((cx, 23.25, cz - 1.25), np.eye(3), (0.5, 0.25, 0.3), (70, 30, 80))   # his throne
    Q += hd.bx((cx, 24.15, cz - 0.9), np.eye(3), (0.6, 0.06, 0.13), GOLD)
    for sx in (-1, 1): Q += hd.lathe((cx + sx * 1.7, 23.0, cz - 2.4), np.eye(3), [(0.18, 0), (0.12, 0.7), (0.26, 0.85)], 6, (60, 56, 64), cap1=True)   # braziers
    return [q for q in Q if q]
def _life_path():
    pts = [V(p, float) for p in GROUND_CH[::-1]] + [SEAL_C, SEAL_C + V((-3.0, 4.0, 0.5)), SEAL_C + V((-25.0, 14.0, 10.0))]
    cr = KING0 + V((0, 1.95, 0)); pts += [cr + V((16.0, 6.0, -12.0)), cr + V((4.0, 1.6, -3.0)), cr + V((0.8, 0.3, -0.5)), cr]
    cum = np.concatenate([[0.0], np.cumsum([np.linalg.norm(b - a) for a, b in zip(pts, pts[1:])])]); return np.array(pts), cum
LIFE_P, LIFE_C = _life_path()
def life_faces(t, cpos):
    """the stolen life: gold motes village -> chain -> seal -> crown (T_SIP .. the strike), then back crown -> village (after the strike)"""
    Q = []; G = []
    if T_SIP <= t < T_IMPACT2 + 0.05: sp = 4.0 * (t - T_SIP); amp = sm(seg01(t, T_SIP, T_SIP + 0.4)) * (0.3 if t > T_IMPACT2 else 1.0)
    elif T_IMPACT2 + 0.12 <= t < T_FREE: sp = -9.0 * (t - T_IMPACT2); amp = 1.0 - sm(seg01(t, T_FREE - 0.4, T_FREE))
    else: return Q, G
    if abs(sp) < 1e9:
        e = V(GROUND_CH[-1], float)
        for i, (wp, wn) in enumerate(WIN + [(LANT_W, V((0, 0, -1.0)))]):
            if light_on(i, t) < 0.05 and sp > 0: continue
            a_ = wp + wn * 0.3; L_ = float(np.linalg.norm(e - a_)); g_ = 0.5
            for s_ in np.arange((sp * 0.6) % g_, L_, g_):
                f_ = s_ / L_; p = a_ + (e - a_) * f_ + V((0, 1.5 * math.sin(PI * f_), 0)); dd_ = float(np.linalg.norm(p - cpos))
                if dd_ > 75: continue
                r = max(0.035, 0.0065 * dd_) * amp * 0.9; c = mixc((150, 110, 40), LIFE, 0.7)
                q = hd.face([p + V((-r, 0, 0)), p + V((0, r * 1.3, 0)), p + V((r, 0, 0)), p + V((0, -r * 1.3, 0))], c, emit=True); Q += [q] if q else []
    Lt = LIFE_C[-1]; gap = 0.32; s0 = sp % gap
    ss = np.arange(s0, Lt, gap)
    px = np.interp(ss, LIFE_C, LIFE_P[:, 0]); py = np.interp(ss, LIFE_C, LIFE_P[:, 1]); pz = np.interp(ss, LIFE_C, LIFE_P[:, 2])
    P_ = np.stack([px, py, pz], 1); dd = np.linalg.norm(P_ - cpos[None, :], axis=1)
    near = []
    for i in np.nonzero(dd < 75)[0]:
        p = P_[i] + V((0, 0.06 * math.sin(ss[i] * 3 + t * 5), 0)); r = max(0.035, 0.0065 * dd[i]) * amp
        if r < 0.01: continue
        c = mixc((150, 110, 40), LIFE, 0.6 + 0.4 * math.sin(ss[i] * 1.7 + t * 9))
        for ang in (0.0, PI / 2):
            dx, dz = r * math.cos(ang), r * math.sin(ang)
            q = hd.face([p + V((-dx, 0, -dz)), p + V((0, r * 1.3, 0)), p + V((dx, 0, dz)), p + V((0, -r * 1.3, 0))], c, emit=True); Q += [q] if q else []
        near.append((dd[i], p))
    for _, p in sorted(near, key=lambda x: x[0])[:24]: G.append((p, LIFE, 0.5 * amp))
    return Q, G

# ======================= the world at time t =======================
def sparks(c, t, t0):
    u = seg01(t, t0, t0 + 0.35); Q = []
    for i in range(14):
        d = nz((hsh(i, 81) - 0.5, hsh(i, 82) - 0.2, hsh(i, 83) - 0.8)); p = V(c, float) + d * (0.1 + 0.9 * u) - V((0, 0.6 * u * u, 0)); s = 0.05 * (1 - u)
        if s < 0.005: continue
        q = hd.face([p - d * s * 2, p + V((0, s, 0)), p + d * s * 2], (255, 240, 170), emit=True); Q += [q] if q else []
    return Q
def falling_links(t):
    """after the strike: the chest chain drops from the broken seal and hangs from the guardian's chest ring to the floor"""
    pts, gp = chest_chain_pts(t); a = gp['_anchor']
    u = sm(seg01(t, T_IMPACT2, T_IMPACT2 + 0.45))
    end0 = SH_L; end1 = V((1.2, 0.05, 1.5))
    e = end0 + (end1 - end0) * u
    if t >= T_STAND + 0.3:                                                                  # it rises: the ring snaps, the chain lies on the floor
        k = sm(seg01(t, T_STAND + 0.3, T_STAND + 0.8)); a = a + (V((0.4, 0.05, 1.9)) - a) * k
    return sagline(a, e, 0.15 + 0.4 * u, n=18)
def wrist_chain(t, gp, key, idx):
    wr = gp['_' + key + 'wr']
    if t < T_STAND + 0.2: return sagline(wr, GA[idx], 0.08, n=10)
    k = sm(seg01(t, T_STAND + 0.2, T_STAND + 0.6))                                          # the chain tears out of the shackle and falls
    end = wr + (GA[idx] + V((0.6 * (1 if idx else -1), 0, -0.5)) - wr) * k
    return sagline(end, GA[idx], 0.05, n=10)
def world(t):
    sc = scene(t); layers = []; L = []; glows = []
    in_vil = sc in ('wom1', 'wom2', 'shout', 'lamp', 'vwin', 'vwin2')
    layers.append(get_set('sky')); layers.append(get_set('plain')); layers.append(get_set('village'))
    layers.append(get_set('ruin'))
    # village lights
    for i, (p, n) in enumerate(WIN):
        on = light_on(i, t); col = mixc((26, 24, 34), (255, 196, 104), on)
        layers.append(hd.decal(p, n, (0, 1, 0), 0.95, 0.8, col, emit=True, lift=0.02))
        layers.append(hd.decal(p, n, (0, 1, 0), 0.08, 0.8, (60, 44, 32), lift=0.035) + hd.decal(p, n, (0, 1, 0), 0.95, 0.07, (60, 44, 32), lift=0.035))
        if on > 0.05: glows.append((p + n * 0.1, (255, 190, 100), 1.6 * on))
        if in_vil and on > 0.05 and np.linalg.norm(p - VIL0) < 4.5: L.append((tuple(p + n * 1.6), (255, 190, 110), 0.45 * on))
    lo = light_on(9, t); layers.append(lantern(LANT_W, lo, t, seed=3))
    if lo > 0.05: glows.append((LANT_W, (255, 200, 110), 1.1 * lo)); L.append((tuple(LANT_W + V((0, 0.0, -0.5))), (255, 190, 110), 0.8 * lo))
    # the ruin: torches, the guardian, chains, the seal, the knight
    for i, (x, y, z) in enumerate(TORCH):
        layers.append(dtx.torch_faces((x, y, z), t, k=1.0, seed=i, stick=False))
        L.append(((x * 0.9, y + 0.4, z), (255, 150, 70), 1.0 * (1 + 0.08 * math.sin(t * 9 + i * 2))))
        glows.append((V((x, y + 0.2, z)), (255, 160, 70), 0.9))
    G = guardian_pose(t); gp = dict(G); layers.append(guardian(gp))
    lp = guardian_lantern_pos(t); lon = max(0.05, guardian_lantern_on(t)); layers.append(lantern(lp, lon, t, seed=1, k=1.5))
    L.append((tuple(lp + V((0, 0.2, -0.9))), (255, 196, 110), 0.55 * lon)); glows.append((lp, (255, 200, 110), 1.1 * lon))
    L.append((tuple(gp['_anchor'] + gp['_nrm'] * 0.5), (255, 190, 100), 0.6 * gp['crack']))
    for e in (0, 1): glows.append((gp['_head'] + hd.Ry(GYAW) @ V(((e - 0.5) * 0.22, 0.0, 0.3)), (150, 230, 255), 0.35 * gp['eye']))
    broken = t >= T_IMPACT2
    if not broken: layers.append(chain(chest_chain_pts(t)[0]))
    else: layers.append(chain(falling_links(t)))
    layers.append(chain(wrist_chain(t, gp, 'r', 0)) + chain(wrist_chain(t, gp, 'l', 1)))
    gch = list(GROUND_CH)
    if broken:
        k_ = sm(seg01(t, T_IMPACT2, T_IMPACT2 + 0.4)); gch[0] = SH_R + (V((2.9, 0.05, 1.05)) - SH_R) * k_; gch[1] = gch[1] + (V((3.0, 0.05, 1.4)) - gch[1]) * k_
    layers.append(chain(gch[:5]) + chain(gch[4:], step=0.5, big=1.7))
    glow = max([win(t, a + 0.9, a + 2.0, 0.2) for a, _ in PULSES] + [0.0]) if not broken else 0.0
    crack = sm(seg01(t, T_IMPACT2 - 0.02, T_IMPACT2 + 0.12)); split = sm(seg01(t, T_IMPACT2 + 0.15, T_IMPACT2 + 0.6))
    layers.append(seal_faces(SEAL_C, SEAL_R, glow=glow + 0.8 * win(t, T_IMPACT2 - 0.02, T_IMPACT2 + 0.3, 0.05), crack=crack, split=split, t=t))
    if glow > 0.05: L.append((tuple(SEAL_C + SEAL_N * 0.6), (180, 90, 255), 0.9 * glow))
    if win(t, T_IMPACT2 - 0.02, T_IMPACT2 + 0.35, 0.05) > 0: L.append((tuple(SEAL_C + SEAL_N * 0.4), (255, 240, 200), 1.4 * win(t, T_IMPACT2 - 0.02, T_IMPACT2 + 0.3, 0.05)))
    if 0 <= t - T_HIT < 0.3: L.append((tuple(gp['_rsh'] + V((0, 0.2, -0.6))), (255, 236, 200), 1.0 * (1 - (t - T_HIT) / 0.3)))
    if 0 <= t - T_HIT < 0.35: layers.append(sparks(gp['_rsh'] + V((0.05, 0.05, -0.32)), t, T_HIT))
    if 0 <= t - T_IMPACT2 < 0.35: layers.append(sparks(SEAL_C + SEAL_N * 0.12, t, T_IMPACT2))
    kq, KP = knight_layers(t); layers.append(kq)
    cq, cl = curse_faces(t); layers.append(cq); L += cl
    lq, lg = life_faces(t, V(cam_shot(t)[0])); layers.append(lq); glows += lg
    if sc in ('king', 'kfall'):
        layers.append(get_set('cwall')); kq, kg, kl = king_layers(t); layers.append(kq); glows += kg; L += kl
        for sx in (-1, 1):
            bp = (CAST0[0] + sx * 1.7, 23.95, CAST0[2] - 2.4); layers.append(dtx.torch_faces(bp, t, k=1.6, seed=7 + sx, stick=False))
            L.append(((bp[0], bp[1] + 0.6, bp[2] - 0.6), (255, 150, 70), 1.1)); glows.append((V(bp) + V((0, 0.2, 0)), (255, 160, 70), 1.0))
    for p_, s_ in pulse_heads(t)[:1]: glows.append((p_, (190, 100, 255), 1.4))
    # the old woman (only drawn near the village cameras)
    if sc in ('wom1', 'wom2', 'shout', 'lamp'):
        Wm = woman_pose(t); layers.append(hd.human(dtx.WOMAN, Wm))
    # lights
    L.append(((6.0, 9.0, 12.0), (120, 140, 210), 0.9))                            # moonlight (rim from behind the guardian)
    if in_vil: L.append((tuple(vil((-6, 6, -10))), (110, 130, 200), 0.7))
    if sc == 'relight' or sc == 'lamp':
        pass
    fog = (14, 14, 28); amb = 0.26 if in_vil else 0.3
    if sc == 'castle':                                                              # the castle must read: a big moon behind it, cold key light
        c_ = V(K0) + V((0, 2.3, 0)); dr = nz(CAST0 + V((0, 27.0, 0)) - c_)
        u_ = nz(np.cross(dr, V((0, 1.0, 0)))); v_ = np.cross(u_, dr); mc = c_ + dr * 160 + u_ * 9.0 + v_ * 4.0
        layers.append([hd.face([mc + (u_ * math.cos(2 * PI * i / 16) + v_ * math.sin(2 * PI * i / 16)) * 15.0 for i in range(16)], (236, 226, 214), emit=True)])
        L.append((tuple(CAST0 + V((25.0, 40.0, -30.0))), (170, 160, 230), 2.2)); amb = 0.5
        for dx in (-8.5, -2.8, 3.2, 8.5): glows.append((CAST0 + V((dx, 17.0 + 8.0, -1.7)), (255, 80, 60), 1.2))
    return layers, L, fog, amb, glows, gp, KP

# ======================= camera =======================
P3 = look.Path
def sh(keys):
    return (keys[0][0], P3([(a, p) for a, p, _, _ in keys]), P3([(a, q) for a, _, q, _ in keys]), P3([(a, f) for a, _, _, f in keys]))
def cam_shot(t):
    sc = scene(t)
    G = V(G0)
    if sc == 'hit':
        u = seg01(t, 0, B(3.0)); return lerp3((-3.0, 0.95, 1.45), (-2.8, 0.95, 1.45), u), lerp3((0.1, 1.5, 1.45), (0.1, 1.5, 1.45), u), lerp(42.0, 40.0, u)
    if sc in ('vwin', 'vwin2'):                                                  # a real window in the village: its light dies / comes back
        u = seg01(t, T_VWIN, T_VBACK) if sc == 'vwin' else seg01(t, T_RELIT, T_KFALL); p, n = WIN[5]
        return tuple(p + n * (7.5 - 0.6 * u) + V((0, 1.6, 0)) - RV @ V((1.2, 0, 0))), tuple(p - V((0, 0.9, 0))), 44.0
    if sc == 'wom1':
        u = seg01(t, B(3.0), B(6.0)); c = V(WOM0)
        return tuple(c + RV @ (V((-0.25, 1.45, -1.95)) + V((0.0, 0.0, 0.15)) * u)), tuple(c + RV @ V((-0.45, 1.65, 0.6))), lerp(46.0, 43.0, u)
    if sc == 'shield':
        u = seg01(t, B(6.0), F(6.6)); return lerp3((-1.45, 1.15, -0.4), (-1.3, 1.15, -0.25), u), lerp3((0.35, 1.45, 2.0), (0.35, 1.45, 2.1), u), lerp(48.0, 45.0, u)
    if sc == 'wom2':
        u = seg01(t, F(4.7), F(6.0)); c = V(WOM0)
        return tuple(c + RV @ (V((0.55, 1.3, -1.9)) + V((0, 0, 0.12)) * u)), tuple(c + RV @ V((0.4, 1.6, 0.4))), lerp(46.0, 43.0, u)
    if sc == 'stream':
        u = seg01(t, B(10.6), B(12.0)); c = V(WOM0)
        return tuple(c + RV @ (V((0.4, 1.7, 0.85)) - V((0, 0, 0.15)) * u)), tuple(V((0.6, 1.4, 1.8))), lerp(17.0, 15.0, u)
    if sc == 'track':
        u = sm(seg01(t, F(3.0), F(4.45)))
        pts, gp = chest_chain_pts(t); a = gp['_anchor']; b = SEAL_C
        b = SEAL_C + SEAL_R @ V((-0.22, 0.0, 0.0)); tg = a + (b - a) * u; p0_ = V((1.75, 1.8, 0.1)); p1_ = SEAL_C + SEAL_N * 1.95 + V((-0.3, 0.12, 0))
        pos = p0_ + (p1_ - p0_) * u
        return tuple(pos), tuple(tg + V((0, -0.05, 0))), lerp(44.0, 40.0, u)
    if sc == 'point':
        u = seg01(t, B(15.0), T_SHOUT); return lerp3((0.9, 1.6, -2.3), (0.95, 1.58, -2.0), u), lerp3((1.05, 1.35, 1.0), (1.1, 1.35, 1.0), u), 50.0
    if sc == 'shout':
        c = V(WOM0); u = seg01(t, T_SHOUT, B(18.0)); return tuple(c + RV @ (V((-0.45, 1.35, -1.7)) + V((0, 0, 0.15)) * u)), tuple(c + RV @ V((0.05, 1.45, 0.3))), 42.0
    if sc == 'strike':
        u = seg01(t, B(18.0), B(21.0)); return lerp3((-0.5, 1.5, -2.3), (-0.4, 1.45, -2.15), u), lerp3((1.3, 1.3, 1.3), (1.35, 1.3, 1.3), u), lerp(50.0, 46.0, u)
    if sc == 'why':                                                              # the knight's face: the chain, then up towards the castle: "Why?"
        u = seg01(t, F(6.0), T_CASTLE); return tuple(V(K0) + V((-0.6, 1.6, 1.05)) + V((0.05, 0, -0.1)) * u), tuple(V(K0) + V((0.0, 1.55, 0.0))), 40.0
    if sc == 'castle':                                                           # what he sees: the king's castle on its hill
        u = seg01(t, T_CASTLE, T_SIP); c = V(K0) + V((0, 2.3, 0)); tg = CAST0 + V((0, 20.0, 0)); return tuple(c + nz(tg - c) * 1.5 * u), tuple(tg), 26.0
    if sc in ('king', 'kfall'):                                                  # the king on the castle wall
        if sc == 'king':
            u = seg01(t, F(9.4), F(11.0)); return tuple(KING0 + V((0.7, 1.55, -2.7)) + V((0, 0, 0.3)) * u), tuple(KING0 + V((0.3, 1.65, 0))), 44.0
        u = seg01(t, T_KFALL, T_FREE); return tuple(KING0 + V((0.8, 1.4, -3.0)) + V((-0.1, -0.2, 0.25)) * u), tuple(KING0 + V((0.2, 1.3 - 0.35 * u, 0))), 46.0
    if sc == 'sealcu':                                                           # close on the padlock: the sword comes in from the left
        u = seg01(t, T_CU, T_REV); u_, v_ = SEAL_R[:, 0], SEAL_R[:, 1]
        c = SEAL_C + v_ * 0.25
        return tuple(c + SEAL_N * 1.15 + u_ * 0.75 + v_ * 0.1 - SEAL_N * 0.12 * u), tuple(c - u_ * 0.15), lerp(52.0, 50.0, u)
    if sc == 'reverse':                                                          # at the broken seal: the current races back past it, up to the castle
        u = seg01(t, T_REV, T_RELIT); return lerp3((6.2, 1.1, -1.6), (6.0, 1.3, -1.5), u), lerp3((1.2, 1.9, 1.6), (0.6, 2.6, 1.8), u), 52.0
    if sc in ('relight', 'siphon'):
        u = seg01(t, T_SIP, F(9.4)); return lerp3((-2.4, 3.0, -1.9), (-2.1, 3.1, -1.7), u), lerp3((34.0, 13.0, 0.5), (36.0, 13.6, 0.5), u), lerp(26.0, 22.0, u)
    if sc == 'lamp':
        u = seg01(t, B(23.2), B(24.0)); c = V(WOM0)
        return tuple(vil((0.65, 1.6, -4.1)) + RV @ V((0, 0, 0.2)) * u), tuple(vil((1.3, 1.62, -2.3))), 36.0
    if sc == 'free':
        u = seg01(t, T_FREE, T_0Q); return lerp3((-0.6, 0.9, -1.0), (-0.55, 0.85, -1.2), u), lerp3((0.3, 2.0, 2.3), (0.2, 2.4, 2.3), u), lerp(50.0, 52.0, u)
    # quest: behind/beside the knight looking up at the guardian; then follows the knight's turn to the castle
    u = sm(seg01(t, T_TURN, T_TURN + 1.2))
    p0, t0_ = V((3.0, 1.45, -2.0)), V((0.75, 2.15, 2.0)); p1, t1_ = V((3.4, 1.8, -0.95)), V((-4.3, 2.6, 3.1))
    u = seg01(t, T_FREE, DUR); return tuple(p0 + V((-0.1, 0.0, 0.35)) * u), tuple(t0_), lerp(48.0, 46.0, u)

# ======================= render =======================
def proj(cam, fov, P):
    cx, cy, cz, yaw, pitch = cam; ca, sa, cp, sp = math.cos(yaw), math.sin(yaw), math.cos(pitch), math.sin(pitch); fpx = W / (2 * math.tan(math.radians(fov) / 2))
    px, py, pz = P[0] - cx, P[1] - cy, P[2] - cz; X = ca * px - sa * pz; Z = sa * px + ca * pz; Y = cp * py - sp * Z; Z2 = sp * py + cp * Z
    if Z2 < 0.1: return None
    return W / 2 + fpx * X / Z2, H / 2 - fpx * Y / Z2, Z2, fpx
def add_glows(a, zb, cam, fov, glows):
    """soft halos around light sources (windows, lanterns, torches, eyes) so they read on a phone; hidden ones (z-test) get none"""
    for p, col, k in glows:
        r = proj(cam, fov, p)
        if r is None: continue
        x, y, Z, fpx = r
        if not (-20 < x < W + 20 and -20 < y < H + 20): continue
        xi, yi = int(x), int(y)
        if 0 <= xi < W and 0 <= yi < H and zb[yi, xi] > 1.0 / max(Z - 0.6, 0.05): continue
        rad = max(2.2, min(26.0, 0.55 * fpx / Z)) * (0.8 + 0.4 * min(1.0, k))
        x0, x1 = max(0, int(x - 3 * rad)), min(W, int(x + 3 * rad) + 1); y0, y1 = max(0, int(y - 3 * rad)), min(H, int(y + 3 * rad) + 1)
        if x0 >= x1 or y0 >= y1: continue
        gx, gy = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
        f = np.exp(-((gx - x) ** 2 + (gy - y) ** 2) / (rad * rad)) * 0.5 * min(1.6, k) * min(1.0, Z / 9.0)
        a[y0:y1, x0:x1] += f[..., None] * V(col, float)[None, None, :]
    return a
def frame_low(t):
    pos, tgt, fov = cam_shot(t); cam = Camera.look(tuple(pos), tuple(tgt)); sc = scene(t)
    layers, L, fog, amb, glows, gp, KP = world(t)
    R = Renderer(W, H, fog=fog)
    shake = (0, 0)
    if 0 <= t - T_HIT < 0.3: k = 1 - (t - T_HIT) / 0.3; shake = (2.0 * math.sin(t * 90) * k, 1.5 * math.cos(t * 77) * k)
    if 0 <= t - T_IMPACT2 < 0.3: k = 1 - (t - T_IMPACT2) / 0.3; shake = (2.0 * math.sin(t * 90) * k, 1.5 * math.cos(t * 70) * k)
    img, vi, zb = zrender(R, cam, layers, L, fov=fov, fog_start=30, fog_end=170, ambient=amb, shake=shake, return_z=True)
    a = look.outline(np.asarray(img).astype(np.float32), zb)
    a = add_glows(a, zb, cam, fov, glows)
    for i, (p, n) in enumerate([]):
        if i in DIE and 0 <= t - DIE[i] < 0.45:
            r = proj(cam, fov, p)
            if r is not None and 0 <= r[0] < W and 0 <= r[1] < H:
                u = (t - DIE[i]) / 0.45; rad = 3 + 14 * u; gx, gy = np.meshgrid(np.arange(W) + 0.5, np.arange(H) + 0.5)
                ring = np.abs(np.hypot(gx - r[0], gy - r[1]) - rad) < 1.1
                a[ring] = a[ring] * (0.3 + 0.7 * u) + V((255.0, 70.0, 60.0)) * (1 - u) * 0.9
        if i in RELIGHT and 0 <= t - RELIGHT[i] < 0.45:
            r = proj(cam, fov, p)
            if r is not None and 0 <= r[0] < W and 0 <= r[1] < H:
                u = (t - RELIGHT[i]) / 0.45; rad = 3 + 14 * u; gx, gy = np.meshgrid(np.arange(W) + 0.5, np.arange(H) + 0.5)
                ring = np.abs(np.hypot(gx - r[0], gy - r[1]) - rad) < 1.1
                a[ring] = a[ring] * (0.3 + 0.7 * u) + V((120.0, 255.0, 140.0)) * (1 - u) * 0.9
    a = np.clip((a * np.array([1.0, 0.98, 1.06]) - 80) * 1.22 + 86, 0, 255)
    # impact flashes
    fl = max(0.0, 1 - abs(t - T_HIT - 0.03) / 0.08) * 0.3 + max(0.0, 1 - abs(t - T_IMPACT2 - 0.03) / 0.08) * 0.3
    if fl > 0: a = a + (255 - a) * fl * 0.5
    return post.ps1(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), levels=6), vi

# ======================= HUD + subtitles (1080 x 1920) =======================
def text_w(s, sc): return len(s) * 6 * sc - sc
def hud_overlay(im, t):
    d = ImageDraw.Draw(im)
    if t < T_QUEST:
        n = village_count(t)
        drop = any(0 <= t - DIE[i] < 0.5 for i in DIE)
        up = any(0 <= t - RELIGHT[i] < 0.4 for i in RELIGHT)
        sc = 7; s1 = 'KÖY' if SUB_LANG == 'tr' else 'VILLAGE'; s2 = f'{n}/10'
        col = (255, 90, 80) if drop else ((140, 255, 150) if up else (255, 226, 150))
        bump = 1 if (drop or up) and (int(t * 24) % 4 < 2) else 0
        x = 64; y = 92 - 4 * bump
        look.draw_cells(d, look.text_cells(s1, x, y, sc, (246, 242, 230)), 4)
        look.draw_cells(d, look.text_cells(s2, x + text_w(s1, sc) + 3 * sc * 6 // 2, y, sc, col), 4)
        # the bar: 10 pips, the dead ones dark
        bx0 = 64; by0 = y + 70; pw = 84; ph = 34; gap = 10
        d.rectangle([bx0 - 8, by0 - 8, bx0 + 10 * (pw + gap) - gap + 8, by0 + ph + 8], fill=(0, 0, 0))
        for i in range(10):
            on = i < n; c = (220, 60, 54) if on else (54, 30, 34)
            if on and drop and i == n - 1: c = (255, 140, 120)
            d.rectangle([bx0 + i * (pw + gap), by0, bx0 + i * (pw + gap) + pw, by0 + ph], fill=c)
            if on: d.rectangle([bx0 + i * (pw + gap), by0, bx0 + i * (pw + gap) + pw, by0 + 8], fill=(255, 150, 140))
    else:
        u = seg01(t, T_QUEST, T_QUEST + 0.25); s1 = 'GÖREV TAMAMLANDI' if SUB_LANG == 'tr' else 'QUEST COMPLETE'; sc1 = 8 if u >= 1 else 10
        look.draw_cells(d, look.text_cells(s1, int(540 - text_w(s1, sc1) / 2), 100, sc1, (255, 214, 96)), 4)
        if t >= T_QUEST + 0.35:
            s2 = 'KÖY KURTARILDI' if SUB_LANG == 'tr' else 'VILLAGE SAVED'; sc2 = 7; look.draw_cells(d, look.text_cells(s2, int(540 - text_w(s2, sc2) / 2), 200, sc2, (246, 242, 230)), 4)
COL = {'N': (242, 238, 226), 'K': (120, 230, 255), 'W': (255, 190, 90), 'G': (170, 220, 255)}
TR = {'01': ['YA MUHAFIZA VURULAN HER DARBE BİR KÖYLÜYÜ ÖLDÜRÜYORSA?'], '02': ['KRALIN MÜHRÜ HER YARAYI BİZE GÖNDERİYOR!'],
      '03': ['NEDEN?'], '04': ['ONU ÖLÜMSÜZ KILMAK İÇİN.'], '05': ['ARTIK KRALIN DA CANI YANACAK.']}
def _sub_scr():
    if SUB_LANG != 'tr': return SCR
    out = dict(SCR); sent = {}
    for k, v in SCR['sent'].items():
        if len(v) == len(TR[k]): sent[k] = [[a, b, tx] for (a, b, _), tx in zip(v, TR[k])]
        else: sent[k] = [[v[0][0], v[-1][1], ' '.join(TR[k])]]      # the take pauses elsewhere (e.g. a Turkish read): one subtitle for the line
    out['sent'] = sent
    return out
SUBS = look.Subtitles(_sub_scr(), LINES, W, H, S, COL, title_key='none', card_y=0.70, card_sc=8.0, card_n=15,
                      hil=({'DARBE', 'KÖYLÜYÜ', 'ÖLDÜRÜYORSA'} if SUB_LANG == 'tr' else {'HIT', 'KILLED', 'VILLAGER'}))
def frame_final(t):
    img, vi = frame_low(t); arr = post.upscale(img, S)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); hud_overlay(im, t)
    return SUBS.apply(np.asarray(im).astype(np.float32), t)

ASSET = os.environ.get('ASSET')
if ASSET and __name__ == '__main__':
    floor = hd.bx((0, -0.05, 0), np.eye(3), (12, 0.05, 12), (70, 64, 58)); ims = []
    if ASSET == 'guardian':
        for kn, cp, tg, fv in ((1.0, (0.4, 1.6, -2.6), (0, 1.3, 2.0), 50), (0.0, (2.6, 1.8, -2.2), (0, 1.7, 2.4), 56), (1.0, (-3.0, 1.4, 1.6), (0, 1.3, 2.4), 50)):
            P = guardian_pose(B(4.0)) if kn > 0.5 else guardian_pose(B(26.0)); gp = dict(P); Q = guardian(gp)
            lp = guardian_lantern_pos(B(4.0) if kn > 0.5 else B(26.0))
            ims.append(dtx.shot([floor, Q, lantern(lp, 1.0)], cp, tg, fv))
    elif ASSET == 'seal':
        for cr, spl in ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0)):
            Q = seal_faces(SEAL_C, SEAL_R, glow=0.3, crack=cr, split=spl)
            ims.append(dtx.shot([floor, Q], tuple(SEAL_C + SEAL_N * 1.6 + V((0, 0.1, 0))), tuple(SEAL_C), 40))
    out = Image.new('RGB', (W * S * len(ims) // 2, H * S // 2))
    for i, im in enumerate(ims): out.paste(im.resize((W * S // 2, H * S // 2), Image.NEAREST), (i * W * S // 2, 0))
    out.save(f'test_bhb_{ASSET}.png'); print('written'); sys.exit()

TEST = os.environ.get('TEST')
if TEST and __name__ == '__main__':
    ts = [float(x) for x in TEST.split(',')] if TEST != 'all' else [round(x, 2) for x in np.arange(0, DUR, float(os.environ.get('STEP', '0.5')))]
    ims = [Image.fromarray(np.clip(frame_final(x), 0, 255).astype(np.uint8)).resize((int(os.environ.get('TW', '270')), int(os.environ.get('TW', '270')) * 16 // 9), Image.LANCZOS) for x in ts]
    tw = ims[0].size[0]; th = ims[0].size[1]
    per = int(os.environ.get('PER', '8')); rows = (len(ims) + per - 1) // per; shp = Image.new('RGB', (min(per, len(ims)) * (tw + 2), rows * (th + 18)), (30, 30, 30))
    dd = ImageDraw.Draw(shp)
    for i, (im, x) in enumerate(zip(ims, ts)): shp.paste(im, ((i % per) * (tw + 2), (i // per) * (th + 18))); dd.text(((i % per) * (tw + 2) + 4, (i // per) * (th + 18) + th + 3), f'{x:.2f} {scene(x)}', fill=(255, 255, 0))
    shp.save(os.environ.get('TEST_OUT', 'test_bhb.png')); print('test written', DUR); sys.exit()

# ======================= QA manifest =======================
QA = dict(fps=FPS, dur=DUR, W=W, frame=lambda t: Image.fromarray(np.clip(frame_final(t), 0, 255).astype(np.uint8)).resize((W, H), Image.BOX), chars={},
          geom=lambda t, name, st, V_: [], camera=lambda t: cam_shot(t)[0], min_cam_dist=0.3, camera_ok=lambda p: True, allow_jump=[], weapon_events=[],
          scenes=[dict(id=nm, t0=a, t1=(CUTS[i + 1][1] if i + 1 < len(CUTS) else DUR), action=nm) for i, (nm, a) in enumerate(CUTS)],
          texts=lambda: [('hud', 'VILLAGE 10/10', 7), ('hud', 'QUEST COMPLETE', 8), ('hud', 'VILLAGE SAVED', 7)])

# ======================= AUDIO (stems: dialogue / music / fx+ambience) =======================
from nightkit.audio import Sound, duck_envelope, soft_fire
OUT = 'out'; os.makedirs(OUT, exist_ok=True)
STEM_DIR = os.environ.get('STEM_DIR', os.path.join(OUT, 'bhb_stems'))
def build_audio(path):
    import soundfile as _sf
    from scipy.signal import fftconvolve
    s_ = Sound(DUR, loop=False, seed=7); sr = s_.sr; n = s_.n; t = s_.t
    BED = np.zeros(n); FX = np.zeros(n); MUS = np.zeros(n)
    def put(buf, x, t0, v=1.0):
        i = int(t0 * sr)
        if i >= n or i + len(x) <= 0: return
        if i < 0: x = x[-i:]; i = 0
        j = min(n, i + len(x)); buf[i:j] += (x * v)[:j - i]
    def nb(t0, d, lo, hi, v, seed, shape=2, buf=None): put(FX if buf is None else buf, s_.filt_short(s_.noise(d, seed), lo=lo, hi=hi) * np.sin(np.pi * s_.T(d) / d) ** shape, t0, v)
    def tone(t0, m, d, v, dec=3.0, att=0.005, glide=0.0, buf=None, harm=(1.0,)):
        f = 440 * 2 ** ((m - 69) / 12); tt = s_.T(d); fr = f * (1 + glide * tt / d); ph = np.cumsum(fr) / sr
        x = sum(a * np.sin(2 * np.pi * ph * (k + 1)) for k, a in enumerate(harm)); put(FX if buf is None else buf, x * np.minimum(1, tt / att) * np.exp(-tt * dec), t0, v)
    def thud(t0, f=60, v=0.1, d=0.3): tt = s_.T(d); put(FX, np.sin(2 * np.pi * f * tt * (1 - 0.3 * tt / d)) * np.exp(-tt * 14), t0, v)
    def clink(t0, v=0.03, seed=0):
        for k, f in enumerate((2900, 4100, 5300)): tt = s_.T(0.3); put(FX, np.sin(2 * np.pi * f * (1 + 0.02 * hsh(seed + k)) * tt) * np.exp(-tt * (18 + 5 * k)), t0 + k * 0.03, v * (1 - 0.25 * k))
    def bell(t0, v=0.05, mute=None):
        tt = s_.T(4.0); x = sum(a * np.sin(2 * np.pi * f * tt) * np.exp(-tt * dcy) for f, a, dcy in ((392, 1.0, 0.9), (784, 0.5, 1.4), (941, 0.35, 1.8), (1176, 0.25, 2.2), (196, 0.3, 0.7)))
        if mute is not None: x = x * np.clip(1 - (tt - mute) / 0.12, 0, 1)
        put(FX, x, t0, v)
    def mask(a, b, r=0.15): return np.clip(np.minimum((t - a) / r, (b - t) / r), 0, 1)
    def pulse(t0, v=0.12):                                                          # low magical pulse
        tt = s_.T(1.4); f = 55 * (1 + 0.6 * np.exp(-tt * 3)); ph = np.cumsum(f) / sr
        put(FX, (np.sin(2 * np.pi * ph) + 0.3 * np.sin(6 * np.pi * ph)) * np.sin(np.pi * tt / 1.4) ** 2, t0, v)
        put(FX, s_.filt_short(s_.noise(1.4, int(t0 * 10)), lo=300, hi=2500) * np.sin(np.pi * tt / 1.4) ** 4, t0, v * 0.25)
    def hud_drop(t0): tone(t0, 45, 0.35, 0.05, dec=6, harm=(1.0, 0.6, 0.4, 0.3)); tone(t0 + 0.08, 40, 0.35, 0.05, dec=6, harm=(1.0, 0.6, 0.4, 0.3))
    def hud_up(t0, m): tone(t0, m, 0.5, 0.035, dec=5, harm=(1.0, 0.3)); tone(t0 + 0.06, m + 7, 0.5, 0.025, dec=5, harm=(1.0, 0.3))
    vil = np.isin(np.array([scene(x) for x in np.arange(0, DUR, 0.01)]), ['wom1', 'wom2', 'shout', 'lamp', 'vwin', 'vwin2']).astype(float)
    vil = np.repeat(vil, int(sr * 0.01))[:n]; vil = np.concatenate([vil, np.zeros(n - len(vil))]); vil = np.convolve(vil, np.ones(1200) / 1200, 'same')
    # ---- ambience: ruin (torches, low drone) / village (wind)
    BED += soft_fire(s_, level=0.016, mask=(1 - vil), seed=5)
    BED += s_.filt(s_.rng.normal(0, 1, n), lo=200, hi=1400) * 0.03 * (0.4 + 0.6 * vil) * (0.6 + 0.4 * np.sin(2 * np.pi * t * 0.25))
    dark = mask(-1, T_IMPACT2, 0.1)
    for f, a in ((41.2, 1.0), (49.0, 0.6), (61.7, 0.5)): MUS += np.sin(2 * np.pi * f * t + a + 1.5 * np.sin(2 * np.pi * 0.13 * t)) * a * 0.03 * dark
    for f, a in ((110.0, 1.0), (130.8, 0.6), (164.8, 0.4)): MUS += np.sin(2 * np.pi * f * t + a) * a * 0.008 * dark * (0.5 + 0.5 * np.sin(2 * np.pi * t / 4.8))
    # ---- 0:00 the hit: heavy metal impact, chain snap, a village bell going quiet
    h0 = T_HIT; nb(0.0, h0, 300, 2500, 0.05, 2, 1)                                  # the swing whoosh into frame 0
    tone(h0, 93, 1.6, 0.06, dec=2.2, harm=(1.0, 0.6, 0.4, 0.2)); tone(h0, 86, 1.2, 0.04, dec=3.0, harm=(1.0, 0.5)); nb(h0, 0.25, 2000, 9000, 0.06, 1, 1)
    thud(h0, 55, 0.35, 0.5); thud(h0 + 0.05, 42, 0.25, 0.6)
    for k in range(6): clink(h0 + 0.08 + 0.05 * k, 0.03 + 0.01 * (k % 2), seed=k * 5)
    bell(h0 - 0.6, 0.06, mute=0.75); hud_drop(DIE[5]); nb(DIE[5] - 0.05, 0.35, 600, 4000, 0.03, 25, 2)
    tt = s_.T(1.5); put(FX, s_.filt_short(s_.noise(1.5, 9), lo=30, hi=160) * np.exp(-tt * 2.0), h0 + 0.15, 0.3)      # stone groan as it recoils
    # ---- village: wind, distant rumble; each light that dies: a soft pfft + the HUD drop
    for i, a in DIE.items():
        if i == 5: continue
        nb(a, 0.35, 600, 4000, 0.025, 20 + i, 2); hud_drop(a + 0.05)
    tt = s_.T(3.0); put(FX, s_.filt_short(s_.noise(3.0, 21), lo=25, hi=90) * np.sin(np.pi * tt / 3.0), B(3.0), 0.35)
    # ---- curse pulses (low magical pulse synced to each wave) and the dark wave
    for a, kind in PULSES: pulse(a, 0.16)
    # ---- the track: chain creak along the reveal
    for k in range(5):
        tt = s_.T(0.35); put(FX, np.sin(2 * np.pi * (700 + 220 * np.sin(tt * 30)) * tt) * np.exp(-tt * 7), F(3.0) + 0.45 * k, 0.012)
    tone(F(9.42), 57, 2.0, 0.03, dec=1.2, att=0.2, harm=(1.0, 0.5, 0.3), buf=MUS)            # the king: a low brass sting
    sipm = mask(T_SIP, T_IMPACT2, 0.3)                                                          # the siphon: a thin shimmering drone
    for f, a in ((880.0, 1.0), (1318.5, 0.5), (1760.0, 0.25)): MUS += np.sin(2 * np.pi * f * t + 3 * np.sin(2 * np.pi * 5 * t)) * a * 0.006 * sipm
    for k in range(6): clink(T_HALO + 0.03 * k, 0.03, seed=110 + k)                            # the halo shatters
    clink(T_CROWN + 0.3, 0.06, 120); thud(T_CROWN + 0.3, 90, 0.15, 0.2); clink(T_CROWN + 0.5, 0.035, 121)   # the crown hits the stones
    thud(T_KNEEL + 0.4, 50, 0.25, 0.4)                                                          # he drops to one knee
    # ---- the seal strike: sharp metal crack, then a brief silence
    tone(T_IMPACT2, 98, 1.0, 0.07, dec=4.0, harm=(1.0, 0.7, 0.5, 0.3)); nb(T_IMPACT2, 0.12, 3000, 12000, 0.14, 50, 1); thud(T_IMPACT2, 70, 0.3, 0.4)
    for k in range(10): clink(T_IMPACT2 + 0.5 + 0.09 * k + 0.05 * hsh(k, 3), 0.018, seed=60 + k)                # chain links on stone
    quiet = 1 - 0.9 * mask(T_IMPACT2 + 0.12, T_IMPACT2 + 0.9, 0.05)
    # ---- reverse rush + the bell rings again + lights back on
    tt = s_.T(1.0); env = (tt / 1.0) ** 2; put(FX, s_.filt_short(s_.noise(1.0, 70), lo=80, hi=3000) * env * np.exp(-np.maximum(0, tt - 0.85) * 30), T_REV - 0.1, 0.22)
    tt = s_.T(1.6); put(FX, s_.filt_short(s_.noise(1.6, 71), lo=40, hi=600) * np.exp(-tt * 2.5), T_REV + 0.75, 0.25)
    bell(RELIGHT[5] - 0.05, 0.07); bell(RELIGHT[9] - 0.05, 0.05)
    for k, (i, a) in enumerate(sorted(RELIGHT.items(), key=lambda x: x[1])): hud_up(a, 72 + 2 * k)
    warm = mask(T_REV, DUR + 1, 0.8)
    for f, a in ((146.8, 1.0), (185.0, 0.6), (220.0, 0.55), (293.7, 0.3)): MUS += np.sin(2 * np.pi * f * t + a) * a * 0.014 * warm * (1 + 0.15 * np.sin(2 * np.pi * 0.5 * t))
    # ---- it stands: heavy stone movement, chain links falling
    thud(T_STAND - 0.45, 60, 0.12, 0.3); clink(T_STAND - 0.4, 0.03, 80)
    tt = s_.T(2.0); put(FX, s_.filt_short(s_.noise(2.0, 81), lo=30, hi=260) * np.sin(np.pi * tt / 2.0) * (1 + 0.4 * np.sin(2 * np.pi * 9 * tt)), T_STAND, 0.4)
    for k in range(12): clink(T_STAND + 0.25 + 0.08 * k + 0.04 * hsh(k, 8), 0.02, seed=90 + k)
    for k in range(2): thud(T_STAND + 1.8 + 0.5 * k, 45, 0.25, 0.5)
    # ---- quest updated + the knight turns to the castle
    for m, dl in ((62, 0.0), (66, 0.1), (69, 0.2), (74, 0.32), (78, 0.45)): tone(T_QUEST + dl, m, 1.8, 0.03, dec=1.4, att=0.01, harm=(1.0, 0.5, 0.25))
    # ---- voices (Enes's takes, when present): RMS-levelled, the guardian gets a stone-hall echo
    NB = np.zeros(n); wins = []
    ir_t = np.arange(int(0.9 * sr)) / sr; IR = s_.rng.normal(0, 1, len(ir_t)) * np.exp(-ir_t * 5.0); IR[0] = 0; IR = IR / np.sqrt((IR ** 2).sum())
    for k_, t0 in LINES:
        f_ = os.path.join(TTS_DIR, 'bhb', f'{k_}.wav')
        if not os.path.exists(f_): continue
        a, ar = _sf.read(f_); a = a if a.ndim == 1 else a.mean(1)
        a = np.interp(np.arange(int(len(a) * sr / ar)) / sr, np.arange(len(a)) / ar, a); act = np.abs(a) > 0.02 * np.abs(a).max()
        a = a * (0.12 / np.sqrt((a[act] ** 2).mean()))
        if SCR['spk'][k_] == 'G':
            wet = fftconvolve(a, IR)[:len(a) + int(0.6 * sr)]; a = np.concatenate([a, np.zeros(len(wet) - len(a))]) + 0.3 * wet
        put(NB, a, t0); wins.append((t0, t0 + len(a) / sr))
    g = duck_envelope(n, sr, wins, -7.0, 0.05, 0.25) if wins else np.ones(n)
    bed = (BED * g + MUS * (0.6 + 0.4 * g)) * quiet; fx = FX * (0.6 + 0.4 * g) * (0.15 + 0.85 * quiet)
    endcut = np.convolve(np.where(t < DUR - 0.04, 1.0, 0.0), np.ones(96) / 96, 'same')
    L = (bed + fx) * endcut; R_ = (np.roll(bed, 700) + np.roll(fx, 200)) * endcut
    pk = max(np.abs(L).max(), np.abs(R_).max()); gv = (pk * 1.6 / np.abs(NB).max()) if np.abs(NB).max() > 0 else 0.0
    os.makedirs(STEM_DIR, exist_ok=True)                                              # separate tracks (brief): dialogue / music / fx+ambience
    sc_ = 0.9 / max(pk, 1e-9)
    _sf.write(os.path.join(STEM_DIR, 'bhb_dialogue.wav'), NB * gv * sc_ * endcut, sr)
    _sf.write(os.path.join(STEM_DIR, 'bhb_music.wav'), np.stack([MUS * (0.6 + 0.4 * g) * quiet * endcut, np.roll(MUS * (0.6 + 0.4 * g) * quiet, 700) * endcut], 1) * sc_, sr)
    _sf.write(os.path.join(STEM_DIR, 'bhb_fx_ambience.wav'), np.stack([(BED * g * quiet + fx) * endcut, (np.roll(BED * g * quiet, 700) + np.roll(fx, 200)) * endcut], 1) * sc_, sr)
    s_.L = L + NB * gv; s_.R = R_ + NB * gv; s_.reverb(0.1, length=1.4, decay=3.0)
    return s_.save(path, peak=0.9)
if __name__ == '__main__' and os.environ.get('PART') == 'audio':
    print(build_audio(os.path.join(OUT, 'boss_health_bar.wav'))); sys.exit()
if __name__ == '__main__' and os.environ.get('PART'):
    a, b = map(int, os.environ['PART'].split(':'))
    import subprocess
    p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W * S}x{H * S}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', os.path.join(OUT, f'bhb_{a:05d}.mp4')], stdin=subprocess.PIPE)
    vhs = post.VHS(W * S, H * S, S, grade='none', chroma=0, scan_dark=1.0, vignette=0.22, grain=0.9, band_period=1e9)
    for f in range(a, min(b, N)): p.stdin.write(vhs(frame_final(f / FPS), f, f / FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done', a, b); sys.exit()
