"""ART DIRECTION TEST - nightkit version (28 Nov 2026). Choreography: examples/art_test_chor.py (shared with blender/art_test.py).
Art direction (Enes's doc "insert-disc-2-art-direction"): hand-painted medieval PS1 world, phone-readable physical joke without sound.
- Knight: SQUAT silhouette, bent OCHRE plume, LOOSE visor that slips over his eyes; chipped paint where the visor hits the helmet;
  a kite shield with thumb wear at the grip.
- Instructor: tall, feet together, precise; deep green coat, white gloves + collar, a pointer stick, a brass whistle.
- Surfaces: large painted colour shapes (blotch noise on the static set), few marks anchored to objects (decals in local space):
  a knot + chipped paint on the hurdle, thumb wear on the shield, the chip on the helmet. Background quieter (desaturated),
  the strongest contrast on the knight / hurdle / instructor.
Render: python tools/render_seq.py examples/art_test.py --prefix at --seqs A,B,C --speed 1.0 / --master <out> --speed 1.0
Stills: TEST=0.5,1.0 python examples/art_test.py -> test_at.png"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera
from nightkit.zraster import zrender
from nightkit import post, look, hd, motion
import dragon_taxes as dtx
import art_test_chor as C

W, H, S = 270, 480, 4
PI = math.pi; V = np.array; FPS = C.FPS; DUR = C.DUR; N = int(round(DUR * FPS))
hsh, lerp3, mixc = dtx.hsh, dtx.lerp3, dtx.mixc
def nz(v): v = V(v, float); n = np.linalg.norm(v); return v / n if n > 1e-9 else v
def grip_pt(P, key, off=0.075, lift=0.03): return P['_' + key + 'wrist'] + P['_' + key + 'dir'] * off + P['_' + key + 'palm'] * lift
def fr(x): return int(round(x * FPS))
SEQS = [('A', 0, fr(C.SHOTS[0][2])), ('B', fr(C.SHOTS[1][1]), fr(C.SHOTS[1][2])), ('C', fr(C.SHOTS[2][1]), N)]
OUT = 'out'; os.makedirs(OUT, exist_ok=True)

# ======================= painted helpers =======================
def blotch(x, z, seed, scale=1.6):
    """low-frequency 'paint' value 0..1 from world x, z (large colour shapes, not fine noise)"""
    a = math.sin(x / scale * 1.7 + seed) * math.cos(z / scale * 1.3 - seed * 0.7)
    b = math.sin((x + z) / scale * 0.9 + seed * 2.1)
    return 0.5 + 0.35 * a + 0.15 * b
def painted_ground(x0, x1, z0, z1, step, cA, cB, seed):
    Q = []
    xs = np.arange(x0, x1 + 1e-6, step); zs = np.arange(z0, z1 + 1e-6, step)
    for i in range(len(xs) - 1):
        for j in range(len(zs) - 1):
            a, b, c, d = xs[i], xs[i + 1], zs[j], zs[j + 1]; u = blotch((a + b) / 2, (c + d) / 2, seed)
            col = mixc(cA, cB, 1.0 if u > 0.62 else (0.0 if u < 0.38 else (u - 0.38) / 0.24))
            q = hd.face([(a, 0.0, c), (a, 0.0, d), (b, 0.0, d), (b, 0.0, c)], col)
            if q: Q.append(q)
    return Q

# ======================= the set (quiet, desaturated) =======================
GRASS_A = (118, 140, 92); GRASS_B = (134, 150, 104); PATH_A = (176, 156, 120); PATH_B = (190, 170, 132)
def set_faces():
    Q = painted_ground(-14, 14, -16, 18, 1.0, GRASS_A, GRASS_B, 1.3)
    Q += [dict(q, p=[(x, 0.004, z) for (x, y, z) in q['p']]) for q in painted_ground(-0.95, 0.95, -8, 6, 0.5, PATH_A, PATH_B, 4.1)]
    for q in Q[-len(painted_ground(-0.95, 0.95, -8, 6, 0.5, PATH_A, PATH_B, 4.1)):]: pass
    for k in range(13):                                                                # a low split-rail fence far behind (quiet)
        z = -9.0 + 1.6 * k
        for sd in (1, -1):
            Q += hd.bx((sd * 4.5, 0.45, z), np.eye(3), (0.05, 0.45, 0.05), (128, 110, 86))
            Q += hd.bx((sd * 4.5, 0.7, z + 0.8), np.eye(3), (0.03, 0.03, 0.8), (140, 122, 96))
    for i in range(9):
        sd = 1 if i % 2 else -1; x = sd * (7 + 6 * hsh(i, 5)); z = -12 + 26 * hsh(i, 6)
        Q += dtx.tree(x, z, 4 + 2 * hsh(i, 7), col=(96, 124, 84), trunk=(110, 90, 70), seed=i)
    return [q for q in Q if q]
SET = set_faces()
def sky():
    def col(e): return mixc((236, 226, 200), (150, 180, 214), min(1.0, e * 1.5))
    Q = hd.ellip((0, -6, 0), np.eye(3), (90, 70, 90), 20, 8, (200, 210, 220), v1=PI * 0.54, closed=False, colfn=lambda i, j, cl: col(max(0.0, cl[1] / 70)))
    for q in Q: q['emit'] = True
    for i in range(7):                                                                 # painted cloud shapes: big, soft-edged ovals
        a = -1.0 + 2.0 * hsh(i, 21); r = 60; x = r * math.sin(a); z = r * math.cos(a) * (1 if i % 2 else -1); y = 18 + 14 * hsh(i, 22)
        for k in range(2):
            Cq = hd.ellip((x + k * 6, y + k * 1.5, z), hd.Ry(a), (9 + 6 * hsh(i, 23), 2.4, 4), 10, 4, mixc((246, 240, 226), (226, 230, 236), k * 0.6))
            for q in Cq: q['emit'] = True
            Q += Cq
    return [q for q in Q if q]
SKY = sky()
# ---------------- the hurdle: knot + chipped paint (the obstacle carries the joke: strongest colour) ----------------
H_WOOD = (196, 120, 60); H_WOOD_D = (150, 88, 44); H_PAINT = (224, 210, 186)
def hurdle(t):
    a = C.hurdle_wobble(t); R = hd.Rx(-a); base = V((0.0, 0.0, C.HURDLE_Z)); Q = []
    def P_(p): return base + R @ V(p, float)
    for sd in (1, -1):
        Q += hd.bx(tuple(P_((sd * C.HURDLE_HALF, C.HURDLE_H / 2, 0))), R, (0.05, C.HURDLE_H / 2, 0.05), H_WOOD_D)
        Q += hd.bx(tuple(P_((sd * C.HURDLE_HALF, 0.04, 0))), R, (0.1, 0.04, 0.28), H_WOOD_D)
    for j, y in enumerate((0.48, C.HURDLE_H - 0.06)):
        Q += hd.bx(tuple(P_((0, y, 0))), R, (C.HURDLE_HALF, 0.065, 0.03), H_WOOD if j else hd.shade(H_WOOD, 0.92))
        for k_, x in enumerate((-0.45, 0.0, 0.45)):                                     # white painted bands, chipped at the middle top
            w_ = 0.11 if not (j == 1 and k_ == 1) else 0.07
            Q += hd.bx(tuple(P_((x, y, -0.032))), R, (w_, 0.066, 0.003), H_PAINT)
    n = R @ V((0, 0, -1.0)); up = R @ V((0, 1.0, 0))
    kc = P_((0.28, C.HURDLE_H - 0.06, -0.034))                                          # the knot: dark eye + two rings
    Q += hd.poly_decal(tuple(kc), tuple(n), tuple(up), [(0.035 * math.cos(q), 0.022 * math.sin(q)) for q in np.linspace(0, 2 * PI, 9)[:-1]], (90, 52, 28), lift=0.002)
    for r_ in (0.05, 0.065):
        for q0 in np.linspace(0, 2 * PI, 10)[:-1]:
            q1 = q0 + 2 * PI / 9 * 0.7
            Q += hd.poly_decal(tuple(kc), tuple(n), tuple(up), [(r_ * math.cos(q0), 0.6 * r_ * math.sin(q0)), (r_ * math.cos(q1), 0.6 * r_ * math.sin(q1)),
                                                               (r_ * 1.12 * math.cos(q1), 0.6 * r_ * 1.12 * math.sin(q1)), (r_ * 1.12 * math.cos(q0), 0.6 * r_ * 1.12 * math.sin(q0))], (150, 86, 44), lift=0.0021)
    return [q for q in Q if q]

# ======================= the knight: squat, bent ochre plume, loose visor =======================
KNIGHT = hd.spec(h=1.5, build=1.32, skin=(222, 172, 136), hair=(90, 60, 40), eye=(60, 80, 110), brow=(80, 54, 36),
                 tunic=(64, 92, 152), tunic2=(52, 76, 128), skirt=0.3, pants=(120, 124, 136), boots=(70, 60, 54),
                 belt=(96, 66, 40), buckle=(214, 170, 70), gloves=(140, 144, 156), collar=(170, 176, 188))
STEEL = (176, 182, 194); STEEL_D = (124, 130, 144); OCHRE = (214, 158, 46); OCHRE_D = (172, 118, 30)
def helmet(P, visor):
    """dome + rim; the visor plate hinges at the ears: visor 0 = raised on the forehead, 1 = down over the eyes (slit);
    a chipped-paint patch on the brow where it bangs; the bent ochre plume"""
    k = KNIGHT['h'] / 1.78; hc = P['_head']; RH = P['_RH']; rx, ry, rz = 0.09 * k, 0.116 * k, 0.103 * k
    def L(x, y, z): return hc + RH @ V((x, y, z))
    Q = hd.ellip(L(0, 0.02 * k, -0.005), RH, (rx * 1.2, ry * 1.04, rz * 1.17), 16, 6, STEEL, v1=PI * 0.43, closed=False,
                 colfn=lambda i, j, cl: hd.shade(STEEL, 1.08) if j % 4 == 0 else STEEL)
    Q += hd.limb(L(0, 0.05 * k, -0.005), L(0, 0.065 * k, -0.005), rz * 1.2, rz * 1.18, STEEL_D, n=16, m=1, ref=RH @ V((0, 0, 1.0)), flat=0.9)
    # the chip: lighter bare metal with a dark rim, centre of the brow (where the visor hits)
    cc = L(0.012, 0.066 * k, rz * 1.17); nn = RH @ V((0, 0.25, 1.0)); upv = RH @ V((0, 1.0, 0))
    Q += hd.poly_decal(tuple(cc), tuple(nz(nn)), tuple(upv), [(0.026 * math.cos(a) * (1 + 0.3 * math.sin(3 * a)), 0.014 * math.sin(a)) for a in np.linspace(0, 2 * PI, 9)[:-1]], (70, 64, 60), lift=0.004)
    Q += hd.poly_decal(tuple(cc), tuple(nz(nn)), tuple(upv), [(0.02 * math.cos(a) * (1 + 0.3 * math.sin(3 * a)), 0.01 * math.sin(a)) for a in np.linspace(0, 2 * PI, 9)[:-1]], (226, 228, 232), lift=0.005)
    # the visor: a curved plate (part of a cylinder around the face), rotated about the ear axis
    ang = -1.35 * (1 - visor)                                                   # radians about local x: 0 = down
    piv = L(0, 0.03 * k, 0.0); Rv = RH @ hd.Rx(ang)
    rr = rz * 1.24; pts_top = []; segs = 9
    for i in range(segs):
        a0 = -1.05 + 2.1 * i / segs; a1 = -1.05 + 2.1 * (i + 1) / segs
        for (y0, y1, col) in ((-0.075 * k, -0.02 * k, STEEL), (-0.012 * k, 0.03 * k, STEEL)):          # two bands, a slit between
            pa = [V((rr * math.sin(a0), y0, rr * math.cos(a0))), V((rr * math.sin(a1), y0, rr * math.cos(a1))), V((rr * math.sin(a1), y1, rr * math.cos(a1))), V((rr * math.sin(a0), y1, rr * math.cos(a0)))]
            q = hd.face([piv + Rv @ p for p in pa], hd.shade(col, 0.95 + 0.1 * (i % 2)))
            if q: Q.append(q)
            q = hd.face([piv + Rv @ p for p in pa[::-1]], STEEL_D)
            if q: Q.append(q)
    for sd in (1, -1): Q += hd.ellip(tuple(L(sd * rr * 0.98, 0.03 * k, 0.0)), RH, (0.012, 0.016, 0.016), 6, 3, (214, 170, 70))   # hinge rivets
    # the plume: up, then bent forward and drooping (ochre)
    sw = P.get('cape_sway', 0.0) * 0.3
    pts = [L(0, ry * 1.02, -0.01), L(0.0, ry * 1.02 + 0.09 * k, -0.04), L(sw * 0.05, ry * 1.02 + 0.15 * k, 0.03 * k), L(sw * 0.08, ry * 1.02 + 0.13 * k, 0.12 * k), L(sw * 0.1, ry * 1.02 + 0.06 * k, 0.17 * k)]
    rad = [0.02, 0.03, 0.034, 0.026, 0.008]
    for i in range(4): Q += hd.limb(tuple(pts[i]), tuple(pts[i + 1]), rad[i], rad[i + 1], OCHRE if i % 2 == 0 else OCHRE_D, n=7, m=1)
    return [q for q in Q if q]
SHIELD_B = (46, 70, 132); SHIELD_RIM = (176, 150, 96)
def shield(P):
    """kite shield on the left forearm; thumb wear (paler worn patch) by the grip edge"""
    wr = P['_lwrist']; d = P['_ldir']; pal = P['_lpalm']; c = wr - d * 0.12 + pal * 0.07
    n = nz(pal); up = nz(np.cross(n, d)) if np.linalg.norm(np.cross(n, d)) > 1e-6 else V((0, 1.0, 0))
    if up[1] < 0: up = -up
    r_ = nz(np.cross(up, n)); pts = [(0.0, 0.26), (0.2, 0.18), (0.18, -0.06), (0.0, -0.32), (-0.18, -0.06), (-0.2, 0.18)]
    def w(p, s=1.0, off=0.0): return c + r_ * p[0] * s + up * p[1] * s + n * off
    Q = [q for q in [hd.face([w(p, 1.0, 0.0) for p in pts], SHIELD_RIM), hd.face([w(p, 1.0, -0.01) for p in pts[::-1]], hd.shade(SHIELD_RIM, 0.8)),
                     hd.face([w(p, 0.86, 0.004) for p in pts], SHIELD_B)] if q]
    for q in Q:
        if q is Q[0] or q is Q[2]:
            if float(q['n'] @ n) < 0: q['p'] = q['p'][::-1]; hd.refresh(q) if hasattr(hd, 'refresh') else None
    Q += hd.poly_decal(tuple(w((0.0, 0.03), 1.0, 0.006)), tuple(n), tuple(up), [(0.05 * math.cos(a), 0.11 * math.sin(a)) for a in np.linspace(0, 2 * PI, 8)[:-1]], OCHRE, lift=0.0)   # the device: an ochre bar
    Q += hd.poly_decal(tuple(w((0.15, 0.08), 1.0, 0.007)), tuple(n), tuple(up), [(0.03 * math.cos(a), 0.02 * math.sin(a)) for a in np.linspace(0, 2 * PI, 8)[:-1]], (92, 112, 168), lift=0.0)  # thumb wear
    return [q for q in Q if q]
def knight_pose(t):
    d = C.knight(t); P = dict(base=(d['x'], 0.0, d['z']), yaw=d['yaw'], eyes='open', mouth='smile', brow=0.3, lean=0.05, head=(0.0, 0.0, 0.0), cape_sway=0.3 * math.sin(t * 3.0))
    P['look'] = (d['look_side'], d['look_up']); P['head'] = (0.6 * d['look_side'], 0.6 * d['look_up'], 0.0)
    P['rh'] = (0.26, 0.82, 0.12); P['lh'] = (-0.24, 0.9, 0.22); P['lpalm'] = (-1.0, 0.0, 0.0); P['rgrip'] = 0.6
    k = d['arms_k']; sp = d['speed']
    if sp > 0.05:
        a = min(1.0, sp / 2.0); P['walk'] = d['phase']; P['stride'] = 0.42 * a; P['lift'] = 0.15 * a; P['lean'] = 0.08 + 0.12 * a
        s_ = math.sin(d['phase'])
        if d['arms'] == 'run': P['rh'] = lerp3(P['rh'], (0.24, 0.95, 0.12 - 0.3 * s_), k)
    if d['arms'] == 'slap': P['rh'] = lerp3(P['rh'], (0.1, 1.38, 0.26), k); P['rgrip'] = 0.2; P['rpalm'] = (0.0, 0.3, -1.0); P['mouth'] = 'grit'
    if d['arms'] == 'blind':
        wig = 0.05 * math.sin(t * 11)
        P['rh'] = lerp3(P['rh'], (0.2, 1.05 + wig, 0.5), k); P['lh'] = lerp3(P['lh'], (-0.2, 1.05 - wig, 0.45), k); P['rgrip'] = 0.1; P['mouth'] = 'o'; P['brow'] = -0.3
    if d['fold'] > 0:
        f = d['fold']
        P['base'] = (d['x'], 0.28 * f, d['z'] + 0.38 * f); P['lean'] = 0.08 + 1.35 * f; P['crouch'] = 0.0
        P['rf'] = (0.1, lerp3((0.1, 0.075, 0.0), (0.1, 0.06, -0.3), f)[1], -0.3 * f); P['lf'] = (-0.1, 0.06, -0.26 * f)
        P['rkpole'] = (0.2, 0.0, 1.0); P['lkpole'] = (-0.2, 0.0, 1.0)
        P['rh'] = lerp3(P['rh'], (0.22, 0.25, 0.7), d['arms_k'] if d['arms'] == 'dangle' else 1.0); P['lh'] = lerp3(P['lh'], (-0.25, 0.3, 0.62), f)
        P['mouth'] = 'o'; P['brow'] = -0.4; P.pop('walk', None)
        if d['arms'] == 'thumb': P['rh'] = lerp3((0.22, 0.25, 0.7), (0.38, 0.95, 0.55), k); P['rgrip'] = 0.95; P['mouth'] = 'smile'
    return P, d
def knight_faces(t):
    P, d = knight_pose(t); Q = hd.human(KNIGHT, P); RW = P['_RW']; ch = P['_chest']
    for sd in (1, -1):                                                                  # round pauldrons (squat silhouette)
        c = ch + RW @ V((sd * 0.2 * 1.25, 0.06, -0.01))
        Q += hd.ellip(c, RW @ hd.Rz(-sd * 0.3), (0.13, 0.09, 0.12), 10, 5, STEEL, v1=PI * 0.62, colfn=lambda i, j, cl: STEEL_D if i == 2 else STEEL)
    Q += helmet(P, d['visor']) + shield(P)
    return Q, P

# ======================= the instructor: tall, feet together, precise =======================
INSTR = hd.spec(h=1.98, build=0.78, skin=(214, 170, 140), hair=(30, 26, 26), hair_style='short', eye=(70, 60, 50), brow=(30, 24, 22),
                tunic=(42, 94, 70), tunic2=(34, 78, 58), skirt=0.42, pants=(40, 40, 46), boots=(24, 22, 24), belt=(30, 28, 30),
                buckle=(214, 180, 90), gloves=(244, 244, 238), collar=(246, 244, 236))
def instr_pose(t):
    d = C.instructor(t)
    P = dict(base=(d['x'], d['y'], d['z']), yaw=d['yaw'], eyes='half' if not d['blink'] else 'closed', mouth='neutral', brow=0.2, lean=-0.03, head=(0.0, -d['head'], 0.0))
    P['crouch'] = d['crouch']
    if d.get('step'): P['walk'] = 2 * PI * 1.6 * t; P['stride'] = 0.22; P['lift'] = 0.08
    if not d.get('step'): P['lf'] = (-0.055, 0.075, 0.02); P['rf'] = (0.055, 0.075, 0.02)                      # feet together
    if d['tuck'] > 0: P['lf'] = (-0.055, 0.075 + 0.35 * d['tuck'], -0.1 * d['tuck']); P['rf'] = (0.055, 0.075 + 0.35 * d['tuck'], -0.1 * d['tuck']); P['lean'] = 0.15 * d['tuck']
    P['rh'] = (0.2, 0.98, 0.04); P['lh'] = (-0.2, 0.98, 0.04); P['rgrip'] = 0.9; P['lgrip'] = 0.5
    k = d['arms_k']
    if d['arms'] == 'back': P['rh'] = lerp3(P['rh'], (0.22, 0.9, -0.32), k); P['lh'] = lerp3(P['lh'], (-0.22, 0.9, -0.32), k)
    if d['arms'] == 'up': P['rh'] = lerp3(P['rh'], (0.42, 2.12, 0.08), k); P['lh'] = lerp3(P['lh'], (-0.42, 2.12, 0.08), k); P['mouth'] = 'smile' if k > 0.5 else 'neutral'
    if d['arms'] == 'behind': P['rh'] = lerp3(P['rh'], (0.07, 1.0, -0.2), k); P['lh'] = lerp3(P['lh'], (-0.07, 1.0, -0.2), k)
    if d['arms'] == 'point':
        P['lh'] = (-0.07, 1.0, -0.2); P['rh'] = lerp3((0.07, 1.0, -0.2), (0.22, 1.22, 0.5), k); P['rpalm'] = (-1.0, 0.0, 0.0); P['head'] = (0.0, -0.25, 0.0)
    return P, d
def instr_faces(t):
    P, d = instr_pose(t); Q = hd.human(INSTR, P)
    g = grip_pt(P, 'r', 0.05, 0.0); dd = P['_rdir']                                     # the pointer stick
    Q += hd.limb(tuple(g - dd * 0.05), tuple(g + dd * 0.7), 0.011, 0.007, (90, 60, 36), n=5, m=1) + hd.ellip(tuple(g + dd * 0.7), np.eye(3), (0.015, 0.015, 0.015), 6, 3, (236, 232, 220))
    ch = P['_chest']; RW = P['_RW']                                                       # the brass whistle on a cord
    wc = ch + RW @ V((0.04, -0.06, 0.13 * 0.78 + 0.02))
    Q += hd.limb(tuple(ch + RW @ V((0.0, 0.12, 0.08))), tuple(wc), 0.004, 0.004, (240, 240, 236), n=4, m=1) + hd.limb(tuple(wc), tuple(wc + RW @ V((0.0, -0.05, 0.02))), 0.012, 0.01, (214, 176, 70), n=6, m=1)
    return Q, P

# ======================= render =======================
def frame_low(t):
    nm, pos, tgt, fov = C.camera(t)
    sh = motion.kick(t, C.K_CRASH, amp=0.04, frames=7)
    pos = V(pos) + V((0.0, sh, 0.0)); cam = Camera.look(tuple(pos), tuple(tgt))
    QK, KP = knight_faces(t); QI, IP = instr_faces(t)
    layers = [SKY, SET, hurdle(t), QI, QK]
    L = [(tuple(V(tgt) + V((-5.0, 9.0, 4.0))), (255, 238, 210), 20.0), (tuple(V(tgt) + V((5.0, 3.0, -3.0))), (170, 190, 230), 5.0)]
    R = Renderer(W, H, fog=(226, 226, 214))
    img, vi, zb = zrender(R, cam, layers, L, fov=fov, fog_start=14, fog_end=40, ambient=0.5, return_z=True)
    a = look.outline(np.asarray(img).astype(np.float32), zb)
    a = np.clip((a - 80) * 1.05 + 84, 0, 255)
    return post.ps1(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), levels=8), vi
def frame_final(t):
    img, vi = frame_low(t); return post.upscale(img, S)

TEST = os.environ.get('TEST')
if TEST and __name__ == '__main__':
    ts = [float(x) for x in TEST.split(',')]
    tw_ = int(os.environ.get('TW', '240')); th = tw_ * 16 // 9
    ims = [Image.fromarray(np.clip(frame_final(x), 0, 255).astype(np.uint8)) for x in ts]
    if os.environ.get('SZ') == 'full':
        for x, im in zip(ts, ims): im.save(f'test_at_{x:.2f}.png')
    if os.environ.get('SZ') == 'work':
        for x in ts: frame_low(x)[0].save(f'test_at_work_{x:.2f}.png')
    ims = [im.resize((tw_, th), Image.LANCZOS) for im in ims]
    shp = Image.new('RGB', (len(ims) * (tw_ + 2), th + 18), (30, 30, 30)); dd = ImageDraw.Draw(shp)
    for i, (im, x) in enumerate(zip(ims, ts)): shp.paste(im, (i * (tw_ + 2), 0)); dd.text((i * (tw_ + 2) + 4, th + 3), f'{x:.2f} {C.camera(x)[0]}', fill=(255, 255, 0))
    shp.save('test_at.png'); print('written'); sys.exit()

# ======================= audio (foley from the shared events) =======================
def build_audio(path):
    from nightkit.audio import Sound
    s = Sound(DUR, loop=False, seed=5); sr = s.sr; n = s.n; t = s.t; FX = np.zeros(n); BED = np.zeros(n)
    def put(x, t0, v=1.0, buf=None):
        b = FX if buf is None else buf; i = int(round(t0 * sr)); j = min(n, i + len(x))
        if i < n: b[i:j] += (x * v)[:j - i]
    def tone(t0, f, d, v, dec=6.0, glide=0.0, harm=(1.0,)):
        tt = s.T(d); fr_ = f * (1 + glide * tt / d); ph = np.cumsum(fr_) / sr
        put(sum(a * np.sin(2 * np.pi * ph * (k + 1)) for k, a in enumerate(harm)) * np.exp(-tt * dec) * np.minimum(1, tt / 0.004), t0, v)
    def nb(t0, d, lo, hi, v, seed, shape=1.0): put(s.filt_short(s.noise(d, seed), lo=lo, hi=hi) * np.sin(np.pi * s.T(d) / d) ** shape, t0, v)
    BED += s.filt(s.rng.normal(0, 1, n), lo=150, hi=1500) * 0.01
    for k in range(10):
        x = 0.4 + 0.75 * k; tone(x, 2400 + 300 * hsh(k, 2), 0.08, 0.006, dec=20, glide=0.3)
    for t0, kind in C.sound_events():
        if kind == 'step': tone(t0, 90, 0.12, 0.05, dec=20); tone(t0 + 0.01, 1900, 0.05, 0.008, dec=40, harm=(1.0, 0.6))
        if kind == 'cloth': nb(t0, 0.25, 400, 2500, 0.03, 1)
        if kind == 'whoosh': nb(t0, 0.45, 300, 2000, 0.06, 2)
        if kind == 'land': tone(t0, 70, 0.2, 0.08, dec=14); nb(t0, 0.1, 800, 4000, 0.02, 3)
        if kind == 'tada': tone(t0, 523, 0.18, 0.025, dec=6, harm=(1.0, 0.4)); tone(t0 + 0.14, 784, 0.4, 0.025, dec=4, harm=(1.0, 0.4))
        if kind == 'clank': tone(t0, 880, 0.25, 0.05, dec=14, harm=(1.0, 0.7, 0.5, 0.3)); tone(t0, 1320, 0.2, 0.02, dec=18)
        if kind == 'crash': tone(t0, 60, 0.4, 0.16, dec=9); nb(t0, 0.3, 200, 4000, 0.12, 4, 0.4); tone(t0 + 0.02, 700, 0.3, 0.04, dec=10, harm=(1.0, 0.6, 0.4)); nb(t0 + 0.2, 0.9, 150, 700, 0.03, 5)
        if kind == 'creak': tone(t0, 300, 0.6, 0.03, dec=1.5, glide=0.6, harm=(1.0, 0.5, 0.3, 0.2))
        if kind == 'tiny': tone(t0, 660, 0.2, 0.015, dec=8, harm=(1.0, 0.3))
    s.L = BED + FX; s.R = np.roll(BED, 500) + FX; s.reverb(0.1, length=1.0, decay=4.0)
    return s.save(path, peak=0.9)
if __name__ == '__main__' and os.environ.get('PART') == 'audio':
    print(build_audio(os.path.join(OUT, os.environ.get('AUDIO_NAME', 'art_test.wav')))); sys.exit()
if __name__ == '__main__' and os.environ.get('PART'):
    a, b = map(int, os.environ['PART'].split(':'))
    import subprocess
    p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W * S}x{H * S}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', os.path.join(OUT, f"{os.environ.get('PART_PREFIX', 'at')}_{a:05d}.mp4")], stdin=subprocess.PIPE)
    vhs = post.VHS(W * S, H * S, S, grade='none', chroma=0, scan_dark=1.0, vignette=0.25, grain=0.6, band_period=1e9)
    for f in range(a, min(b, N)): p.stdin.write(vhs(frame_final(f / FPS), f, f / FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done', a, b); sys.exit()
