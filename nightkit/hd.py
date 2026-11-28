"""HD figures for nightkit (24 Nov 2026, Enes: "more detailed visuals with nightkit"): many-face humans and props for zraster.

The old box humans (examples/npc_well.py NW.human) are ~150 faces. These are ~1,500-2,500: lofted torso and limbs with
round cross-sections, joint spheres, a shaped head with eyes / brows / nose / mouth decals and face states, hair shells,
hands with fingers (grip 0..1), boots, a skirt / tunic with folds and an optional cloak. Arms and legs are 2-bone IK
chains, so acting is written as hand / foot targets (body-local or world).

Coordinates: metres, y up. Local body frame: x = the figure's right-hand side (same convention as NW.human: rh at +x),
y up, z forward. yaw rotates the body like engine.ry. All faces are zraster dicts; closed surfaces carry wind=1 (back-face cull).

  Q = human(SPEC, dict(base=(x,0,z), yaw=0.0, rh=(0.3,1.2,0.3), eyes='open', mouth='smile'))
  SPEC = dict(h=1.78, build=1.0, skin=..., hair=..., hair_style='short', tunic=..., pants=..., boots=..., cloak=None, ...)"""
import math
import numpy as np
from .engine import quad

PI = math.pi


# ------------------------------------------------------------------ maths
def Rx(a):
    c, s = math.cos(a), math.sin(a); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
def Ry(a):
    c, s = math.cos(a), math.sin(a); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
def Rz(a):
    c, s = math.cos(a), math.sin(a); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
def nz(v):
    v = np.asarray(v, float); n = np.linalg.norm(v); return v / n if n > 1e-12 else v
def frame_for(d, ref):
    """two unit vectors perpendicular to d; u lies in the plane of d and ref (u ~ ref)"""
    d = nz(d); r = np.asarray(ref, float)
    u = r - d * float(r @ d)
    if np.linalg.norm(u) < 1e-6:
        r = np.array([0, 0, 1.0]) if abs(d[2]) < 0.9 else np.array([1.0, 0, 0]); u = r - d * float(r @ d)
    u = nz(u); v = np.cross(d, u); return u, v
def ik2(a, t, l1, l2, pole):
    """2-bone IK: root a, target t, bone lengths, pole direction (where the middle joint bends to). -> (mid, end)"""
    a = np.asarray(a, float); t = np.asarray(t, float); d = t - a; dist = np.linalg.norm(d)
    dist = min(max(dist, abs(l1 - l2) + 1e-3), (l1 + l2) * 0.999); dr = nz(d) if np.linalg.norm(d) > 1e-9 else np.array([0, -1.0, 0])
    ca = (l1 * l1 + dist * dist - l2 * l2) / (2 * l1 * dist); sa = math.sqrt(max(0.0, 1 - ca * ca))
    p = np.asarray(pole, float); pp = p - dr * float(p @ dr)
    pp = nz(pp) if np.linalg.norm(pp) > 1e-9 else frame_for(dr, (0, 0, 1))[0]
    mid = a + dr * l1 * ca + pp * l1 * sa; end = a + dr * dist; return mid, end
def mix(c1, c2, u): return tuple(int(round(a + (b - a) * u)) for a, b in zip(c1, c2))
def shade(c, k): return tuple(int(max(0, min(255, round(x * k)))) for x in c)


# ------------------------------------------------------------------ face builders
def face(pts, col, inside=None, emit=False, closed=True):
    """one polygon; if `inside` is given the winding is flipped so the normal points away from it (needed for back-face culling)"""
    P = []
    for p in pts:
        p = tuple(float(x) for x in p)
        if not P or max(abs(p[i] - P[-1][i]) for i in range(3)) > 1e-7: P.append(p)
    if len(P) > 2 and max(abs(P[0][i] - P[-1][i]) for i in range(3)) <= 1e-7: P.pop()
    if len(P) < 3: return None
    q = quad(P, col, emit)
    if np.linalg.norm(np.cross(np.subtract(P[1], P[0]), np.subtract(P[2], P[0]))) < 1e-12:
        if len(P) > 3:
            q = quad(P[1:] + P[:1], col, emit)
        if not np.isfinite(q['n']).all() or np.linalg.norm(q['n']) < 0.5: return None
    if inside is not None:
        if float(q['n'] @ (q['c'] - np.asarray(inside, float))) < 0:
            q = quad(P[::-1], col, emit)
        if closed: q['wind'] = 1.0
    return q
def _add(Q, q):
    if q is not None: Q.append(q)

def rings_mesh(R, col, centers=None, cap0=True, cap1=True, colfn=None, closed=True, wrap=True):
    """R: list of rings (each a list of n points); faces between neighbours, outward from each ring's centre."""
    Q = []; m = len(R); n = len(R[0])
    C = centers if centers is not None else [np.mean(r, axis=0) for r in R]
    for i in range(m - 1):
        inside = (np.asarray(C[i]) + np.asarray(C[i + 1])) / 2
        for j in range(n if wrap else n - 1):
            k = (j + 1) % n; c = colfn(i, j) if colfn else col
            _add(Q, face([R[i][j], R[i][k], R[i + 1][k], R[i + 1][j]], c, inside, closed=closed))
    if cap0 and wrap:
        _add(Q, face(R[0], colfn(-1, 0) if colfn else col, np.asarray(C[0]) + (np.asarray(C[0]) - np.asarray(C[1])) * -0.5, closed=closed))
    if cap1 and wrap:
        _add(Q, face(R[-1], colfn(m, 0) if colfn else col, np.asarray(C[-1]) + (np.asarray(C[-2]) - np.asarray(C[-1])) * 0.5, closed=closed))
    return Q

def loft(cs, us, vs, rs, n, col, fold=None, cap0=True, cap1=True, colfn=None, th0=0.0, th1=2 * PI, closed=True):
    """generalised tube: centres cs, frame vectors us/vs, radii rs[(ru, rv)]. fold(i, theta) -> radius factor"""
    wrap = abs((th1 - th0) - 2 * PI) < 1e-6; R = []
    for i, (c, u, v, (ru, rv)) in enumerate(zip(cs, us, vs, rs)):
        ring = []
        for j in range(n if wrap else n + 1):
            th = th0 + (th1 - th0) * j / n; f = fold(i, th) if fold else 1.0
            ring.append(np.asarray(c) + np.asarray(u) * ru * math.cos(th) * f + np.asarray(v) * rv * math.sin(th) * f)
        R.append(ring)
    return rings_mesh(R, col, cs, cap0, cap1, colfn, closed, wrap)

def limb(a, b, ra, rb, col, n=8, m=3, ref=(0, 0, 1), bulge=0.0, flat=1.0, cap0=True, cap1=True, colfn=None):
    """tapered round tube from a to b (radius ra -> rb), m segments, slight mid bulge; flat < 1 squashes it along v"""
    a = np.asarray(a, float); b = np.asarray(b, float); d = b - a
    if np.linalg.norm(d) < 1e-6: return []
    u, v = frame_for(d, ref); cs = []; rs = []
    for i in range(m + 1):
        s = i / m; r = (ra + (rb - ra) * s) * (1 + bulge * math.sin(PI * s)); cs.append(a + d * s); rs.append((r, r * flat))
    return loft(cs, [u] * (m + 1), [v] * (m + 1), rs, n, col, cap0=cap0, cap1=cap1, colfn=colfn)

def ellip(c, R, rad, nu, nv, col, deform=None, keep=None, colfn=None, v0=0.0, v1=PI, closed=True):
    """ellipsoid at c with rotation R and radii rad=(rx, ry, rz); latitude from the top (v=0) down to v1.
    deform(p_local) -> p_local; keep(p_local_centre) -> bool filters faces (open shells such as hair)."""
    c = np.asarray(c, float); rx_, ry_, rz_ = rad; G = []
    for i in range(nv + 1):
        v = v0 + (v1 - v0) * i / nv; row = []
        for j in range(nu):
            u = 2 * PI * j / nu
            p = np.array([rx_ * math.sin(v) * math.sin(u), ry_ * math.cos(v), rz_ * math.sin(v) * math.cos(u)])
            if deform: p = deform(p)
            row.append(p)
        G.append(row)
    Q = []
    for i in range(nv):
        for j in range(nu):
            k = (j + 1) % nu; pl = [G[i][j], G[i][k], G[i + 1][k], G[i + 1][j]]; cl = np.mean(pl, axis=0)
            if keep and not keep(cl): continue
            col_ = colfn(i, j, cl) if colfn else col
            _add(Q, face([c + R @ p for p in pl], col_, c + R @ (cl * 0.3), closed=closed))
    return Q

def lathe(base, R, prof, n, col, colfn=None, cap0=True, cap1=True):
    """surface of revolution around the local y axis: prof = [(radius, y), ...] bottom to top"""
    base = np.asarray(base, float); cs = [base + R @ np.array([0, y, 0]) for _, y in prof]
    u = R @ np.array([1.0, 0, 0]); v = R @ np.array([0, 0, 1.0])
    return loft(cs, [u] * len(cs), [v] * len(cs), [(r, r) for r, _ in prof], n, col, colfn=colfn, cap0=cap0, cap1=cap1)

def bx(c, R, half, col, emit=False):
    """oriented box: centre, rotation, half sizes"""
    c = np.asarray(c, float); hx, hy, hz = half; V = []
    for sx, sy, sz in ((-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)):
        V.append(c + R @ np.array([sx * hx, sy * hy, sz * hz]))
    Q = []
    for f in ((0, 1, 2, 3), (5, 4, 7, 6), (4, 0, 3, 7), (1, 5, 6, 2), (3, 2, 6, 7), (4, 5, 1, 0)):
        _add(Q, face([V[i] for i in f], col, c, emit))
    return Q

def decal(c, n, up, w, h, col, emit=False, lift=0.003):
    """flat rectangle on a surface: centre c, surface normal n, 'up' direction; two-sided (no culling)"""
    n = nz(n); u = nz(np.cross(np.asarray(up, float), n)); v = np.cross(n, u); c = np.asarray(c, float) + n * lift
    q = face([c - u * w / 2 - v * h / 2, c + u * w / 2 - v * h / 2, c + u * w / 2 + v * h / 2, c - u * w / 2 + v * h / 2], col, emit=emit)
    return [q] if q else []

def poly_decal(c, n, up, pts2, col, emit=False, lift=0.003):
    """flat polygon on a surface from 2D points (u right, v up)"""
    n = nz(n); u = nz(np.cross(np.asarray(up, float), n)); v = np.cross(n, u); c = np.asarray(c, float) + n * lift
    q = face([c + u * a + v * b for a, b in pts2], col, emit=emit); return [q] if q else []


# ------------------------------------------------------------------ the human
SKIN = (222, 176, 140)
DEFAULT = dict(h=1.78, build=1.0, fem=0.0, skin=SKIN, hair=(70, 46, 30), hair_style='short', beard=None,
               eye=(70, 90, 60), brow=None, lip=None,
               tunic=(120, 70, 50), tunic2=None, sleeves='long', skirt=0.28, pants=(76, 64, 54), boots=(60, 42, 30),
               belt=(54, 36, 24), buckle=(210, 180, 90), cloak=None, cloak_len=0.95, hood=False, apron=None,
               helmet=None, gloves=None, collar=None, detail=1.0)

def spec(**kw):
    s = dict(DEFAULT); s.update(kw); return s

def walk_cycle(phase, stride=0.32, lift=0.11):
    """foot targets (local, relative to each hip's rest point) and pelvis bob for a walking phase in radians"""
    out = []
    for side, off in ((1, 0.0), (-1, PI)):
        p = phase + off; fz = stride * math.sin(p); up = max(0.0, math.cos(p)) * lift
        out.append((fz, up))
    bob = 0.025 * (abs(math.sin(phase)) - 0.6)
    return out, bob

def _carry(d_from, p, d_to):
    """p rotated by the smallest rotation that takes direction d_from to d_to, then made perpendicular to d_to"""
    a = nz(np.asarray(d_from, float)); b = nz(np.asarray(d_to, float)); p = np.asarray(p, float)
    ax = np.cross(a, b); sn = float(np.linalg.norm(ax)); cs = float(a @ b)
    if sn > 1e-6:
        ax = ax / sn; p = p * cs + np.cross(ax, p) * sn + ax * float(ax @ p) * (1 - cs)
    q = p - b * float(p @ b); return q / np.linalg.norm(q) if np.linalg.norm(q) > 1e-9 else p
def palm_transport(d, d0, p0, d1, p1, u):
    """palm direction (chest frame) for forearm direction d during a blend: the start palm (p0 on forearm d0) and the end palm
    (p1 on d1) are both carried onto d, then turned into each other ABOUT the forearm by u. The palm never crosses the forearm axis,
    so the hand frame cannot flip mid-move (it did when a world-space palm blend met a swinging forearm)."""
    d = nz(np.asarray(d, float)); q0 = _carry(d0, p0, d); q1 = _carry(d1, p1, d)
    phi = math.atan2(float(np.cross(q0, q1) @ d), float(q0 @ q1)); u = min(1.0, max(0.0, u)); c, s_ = math.cos(phi * u), math.sin(phi * u)
    return q0 * c + np.cross(d, q0) * s_ + d * float(d @ q0) * (1 - c)

def human(S, P):
    """S = spec(...), P = pose dict. Returns a list of zraster faces."""
    g = lambda k, d=None: P.get(k, d)
    k = S['h'] / 1.78; bw = S['build']; fem = S['fem']; det = S.get('detail', 1.0)
    nl = 10 if det >= 1 else 8                     # ring resolution of the limbs
    base = np.asarray(g('base', (0, 0, 0)), float); yaw = g('yaw', 0.0)
    Rb = Ry(yaw) @ Rx(g('pitch', 0.0)) @ Rz(g('roll', 0.0))
    crouch = g('crouch', 0.0)
    # walking
    feet_walk = None; bob = 0.0
    if g('walk') is not None:
        feet_walk, bob = walk_cycle(g('walk'), g('stride', 0.3), g('lift', 0.1))
    hip_h = 0.93 * k - crouch + bob
    pel_l = np.array([0, hip_h, 0.0]) + np.asarray(g('pel', (0, 0, 0)), float)
    def W(p): return base + Rb @ np.asarray(p, float)
    def Wd(d): return Rb @ np.asarray(d, float)
    Q = []
    # ---- spine: pelvis -> waist -> chest -> neck
    lean = g('lean', 0.0); twist = g('twist', 0.0); side = g('side', 0.0)
    Rsp = Ry(twist * 0.5) @ Rx(lean * 0.5) @ Rz(side * 0.5); Rch = Ry(twist) @ Rx(lean) @ Rz(side)
    pel = W(pel_l)
    waist = pel + Wd(Rsp @ np.array([0, 0.2 * k, 0]))
    chest = waist + Wd(Rch @ np.array([0, 0.2 * k, 0]))
    neck = chest + Wd(Rch @ np.array([0, 0.13 * k, 0]))
    RW = Rb @ Rch                                                          # chest world rotation
    RP = Rb @ Rsp
    # torso loft (section frames follow the spine)
    tun = S['tunic']; tun2 = S['tunic2'] or shade(tun, 0.82)
    secs = [  # (centre, R, rx, rz, colour)
        (pel + Wd(np.array([0, -0.02, 0])), RP, 0.155 * bw + 0.02 * fem, 0.105 * bw, tun),
        (pel + Wd(Rsp @ np.array([0, 0.09 * k, 0])), RP, 0.15 * bw + 0.01 * fem, 0.1 * bw, tun),
        (waist, RP, (0.14 - 0.02 * fem) * bw, 0.095 * bw, tun),
        (waist + Wd(Rch @ np.array([0, 0.1 * k, 0.005])), RW, (0.165 - 0.01 * fem) * bw, (0.11 + 0.012 * fem) * bw, tun),
        (chest + Wd(Rch @ np.array([0, 0.03 * k, 0.0])), RW, (0.178 - 0.02 * fem) * bw, 0.105 * bw, tun),
        (chest + Wd(Rch @ np.array([0, 0.1 * k, -0.01])), RW, (0.15 - 0.025 * fem) * bw, 0.085 * bw, tun),
        (neck + Wd(Rch @ np.array([0, -0.005, -0.012])), RW, 0.07, 0.065, tun)]
    P['_torso'] = [(c, Rr, rxx, rzz) for c, Rr, rxx, rzz, _ in secs]; P['_RP'] = RP   # for nightkit/bodycheck.py
    R = []; C = []
    for c, Rr, rxx, rzz, _ in secs:
        ring = []
        for j in range(16):
            th = 2 * PI * j / 16; fr = 1.0 + (0.03 * math.cos(2 * th) if det >= 1 else 0)
            ring.append(c + Rr @ np.array([rxx * math.cos(th) * fr, 0, rzz * math.sin(th) * fr]))
        R.append(ring); C.append(c)
    Q += rings_mesh(R, tun, C, colfn=lambda i, j: tun if (i < 5 or j % 2) else tun2)
    # collar / neckline
    if S['collar']:
        Q += limb(neck + Wd(Rch @ np.array([0, -0.03, -0.01])), neck + Wd(Rch @ np.array([0, 0.03, -0.01])), 0.085, 0.075, S['collar'], n=12, m=1, ref=RW @ np.array([0, 0, 1.0]))
    # belt + buckle
    bc = pel + Wd(Rsp @ np.array([0, 0.06 * k, 0]))
    Q += limb(bc - (RP @ np.array([0, 0.025, 0])), bc + (RP @ np.array([0, 0.025, 0])), 0.158 * bw + 0.015 * fem + 0.006, 0.152 * bw + 0.012 * fem + 0.006, S['belt'], n=16, m=1, ref=RP @ np.array([0, 0, 1.0]), flat=0.68)
    Q += bx(bc + (RP @ np.array([0, 0, 0.104 * bw + 0.006])), RP, (0.03, 0.026, 0.008), S['buckle'])
    # skirt (tunic hem with folds)
    sk = S['skirt']
    if sk and sk > 0.02:
        top = pel + (RP @ np.array([0, 0.035, 0]))
        cs = [top + Wd(np.array([0, -sk * s, 0])) for s in (0, 0.5, 1.0)]
        # the hem follows the thighs a little when walking / sitting
        sw = 0.0 if feet_walk is None else 0.05 * math.sin(g('walk'))
        us = [Rb @ Ry(twist * 0.5) @ np.array([1.0, 0, 0])] * 3; vs = [Rb @ Ry(twist * 0.5) @ np.array([0, 0, 1.0])] * 3
        rs = [(0.158 * bw + 0.015 * fem, 0.108 * bw), (0.19 * bw + 0.02 * fem, 0.15 * bw + 0.03 * crouch), (0.215 * bw + 0.03 * fem, 0.175 * bw + 0.08 * crouch)]
        fold = lambda i, th: 1 + (0.06 * i / 2) * math.cos(9 * th + sw * 8) if det >= 1 else 1.0
        Q += loft(cs, us, vs, rs, 18, tun2, fold=fold, cap0=False, cap1=False, closed=False)
    if S['apron']:
        ac = pel + (RP @ np.array([0, -0.12, 0.155 * bw]))
        Q += bx(ac, RP @ Rx(-0.08), (0.15, 0.24, 0.006), S['apron'])
    # ---- head
    hy, hp, ht = g('head', (0.0, 0.0, 0.0)) if isinstance(g('head', 0.0), (tuple, list)) else (g('head', 0.0), g('nod', 0.0), g('tilt', 0.0))
    RH = RW @ Ry(hy) @ Rx(-hp) @ Rz(ht)
    Q += limb(neck - Wd(Rch @ np.array([0, 0.02, 0])), neck + RH @ np.array([0, 0.06 * k, 0.0]), 0.05 * (1 - 0.1 * fem), 0.046, S['skin'], n=nl, m=1, ref=RW @ np.array([0, 0, 1.0]))
    hc = neck + RH @ np.array([0, 0.125 * k, 0.014])
    P['_hk'] = k
    if P.get('face') is not None:                                          # opt-in performance face (nightkit/face.py); old face otherwise
        from . import face as _face
        hk = k * P.get('head_scale', 1.0)                                  # bigger heads read at phone size (chibi-lite); grows up from the neck
        hc = neck + RH @ np.array([0, 0.125 * hk - 0.02 * (hk - k), 0.014])
        Q += _face.head(hc, RH, S, P, hk); P['_hk'] = hk
    else:
        Q += head(hc, RH, S, P, k)
    # ---- arms
    sw_walk = 0.0 if feet_walk is None else math.sin(g('walk'))
    for sd, key in ((1, 'r'), (-1, 'l')):
        sh = chest + Wd(Rch @ np.array([sd * (0.178 - 0.02 * fem) * bw, 0.05 * k, -0.01]))
        if g(key + 'shrug') is not None:                                   # opt-in (nightkit/body.py): shoulder up / forward in the chest frame
            su, sf = g(key + 'shrug'); sh = sh + Wd(Rch @ np.array([0.0, su, sf]))
        la, lf = 0.29 * k, 0.255 * k
        tgt = g(key + 'h_w')
        if tgt is None and g(key + 'hc') is not None:                      # opt-in (nightkit/body.py): hand target in the chest frame
            tgt = chest + Wd(Rch @ np.asarray(g(key + 'hc'), float))
        if tgt is None:
            tl = g(key + 'h')
            if tl is None:
                tl = np.array([sd * 0.25 * bw, hip_h - 0.06 * k + crouch * 0.6, 0.04 - sd * 0.0]) + np.array([0, 0, -0.14 * sd * sw_walk])
                tl = Rch @ (tl - pel_l) + pel_l
            tgt = W(np.asarray(tl, float))
        pole = Wd(Rch @ np.array([sd * 0.5, -0.3, -1.0]))
        if g(key + 'pole') is not None: pole = Wd(np.asarray(g(key + 'pole'), float))
        if g(key + 'pole_c') is not None: pole = Wd(Rch @ np.asarray(g(key + 'pole_c'), float))
        el, wr = ik2(sh, tgt, la, lf, pole)
        slv = tun if S['sleeves'] in ('long', 'short') else S['skin']
        arm_col = S['skin'] if S['sleeves'] in ('short', 'none') else tun
        Q += ellip(sh, RW, (0.055 * bw, 0.05, 0.056), 8, 5, slv)
        Q += limb(sh, el, 0.052 * bw, 0.042, slv, n=nl, m=2, ref=Wd(np.array([0, 0, 1.0])), bulge=0.06, cap0=False)
        Q += ellip(el, RW, (0.043, 0.043, 0.043), 8, 4, arm_col)
        if S['sleeves'] == 'long':
            cuff = wr + (el - wr) * 0.12
            Q += limb(el, cuff, 0.042, 0.037, tun, n=nl, m=2, ref=Wd(np.array([0, 0, 1.0])), bulge=0.05, cap0=False)
            Q += limb(cuff + (el - wr) * 0.03, cuff - (el - wr) * 0.02, 0.043, 0.043, tun2, n=nl, m=1, ref=Wd(np.array([0, 0, 1.0])))
        else:
            Q += limb(el, wr, 0.04, 0.03, S['skin'], n=nl, m=2, ref=Wd(np.array([0, 0, 1.0])), bulge=0.05, cap0=False)
        palm = g(key + 'palm')
        if g(key + 'palm_c') is not None: palm = Rch @ np.asarray(g(key + 'palm_c'), float)
        palm = Wd(Rch @ np.array([-sd * 1.0, 0, 0.2])) if palm is None else (Wd(np.asarray(palm, float)) if g(key + 'palm_local', True) else np.asarray(palm, float))
        if g(key + 'palm_tr') is not None:                                 # opt-in (nightkit/body.py): the palm carried along with the forearm
            palm = RW @ palm_transport(RW.T @ nz(wr - el), *g(key + 'palm_tr'))
        if g(key + 'fingers') is not None:                                # opt-in hand with real fingers (nightkit/hands.py); old grip hand otherwise
            from . import hands as _hands
            _o = {}; Q += _hands.hand(wr, wr - el, palm, g(key + 'fingers'), S['gloves'] or S['skin'], k, ring=(S.get('ring') if key == S.get('ring_hand', 'l') else None),
                                      side=sd, wrist=g(key + 'wrist', (0.0, 0.0)), out=_o)
            P['_' + key + 'tips'] = _o['tips']; P['_' + key + 'grip'] = _o['grip']
        else:
            Q += hand(wr, wr - el, palm, g(key + 'grip', 0.25), S['gloves'] or S['skin'], k, ring=(S.get('ring') if key == S.get('ring_hand', 'l') else None), side=sd)
        P['_' + key + 'wrist'] = wr; P['_' + key + 'dir'] = nz(wr - el); P['_' + key + 'palm'] = nz(palm); P['_' + key + 'el'] = el; P['_' + key + 'sh'] = sh
    # ---- legs
    for sd, key in ((1, 'r'), (-1, 'l')):
        hip = pel + (RP @ np.array([sd * 0.092 * bw, -0.035, 0]))
        lt, ls = 0.445 * k, 0.43 * k
        ft = g(key + 'f_w')
        if ft is None:
            fl = g(key + 'f')
            if fl is None:
                fl = np.array([sd * 0.11 * bw, 0.075, 0.02])
                if feet_walk is not None:
                    fz, up = feet_walk[0 if sd == 1 else 1]; fl = fl + np.array([0, up, fz])
            ft = W(fl)
        kpole = Wd(np.array([sd * 0.15, 0, 1.0])) if g(key + 'kpole') is None else Wd(np.asarray(g(key + 'kpole'), float))
        kn, an = ik2(hip, ft, lt, ls, kpole)
        Q += limb(hip, kn, 0.078 * bw + 0.008 * fem, 0.058, S['pants'], n=nl, m=2, ref=Wd(np.array([0, 0, 1.0])), bulge=0.05, cap0=False)
        Q += ellip(kn, RP, (0.057, 0.057, 0.057), 8, 4, S['pants'])
        bt = kn + (an - kn) * 0.42
        Q += limb(kn, bt, 0.055, 0.05, S['pants'], n=nl, m=1, ref=Wd(np.array([0, 0, 1.0])), cap0=False)
        Q += limb(bt + (kn - an) * 0.04, an, 0.062, 0.05, S['boots'], n=nl, m=2, ref=Wd(np.array([0, 0, 1.0])), cap0=True)
        Q += limb(bt + (kn - an) * 0.06, bt + (kn - an) * 0.0, 0.066, 0.066, shade(S['boots'], 0.75), n=nl, m=1, ref=Wd(np.array([0, 0, 1.0])))
        fdir = g(key + 'fdir'); fdir = nz(Wd(np.array([sd * 0.08, 0, 1.0]))) if fdir is None else nz(np.asarray(fdir, float))
        Q += foot(an, fdir, S['boots'], k)
        P['_' + key + 'knee'] = kn; P['_' + key + 'ankle'] = an; P['_' + key + 'hip'] = hip
    # ---- cloak (open at the front, folds, hangs from the shoulders)
    if S['cloak']:
        if S.get('cloak_hd'): Q += cloak_hd(chest, neck, RW, RP, Rb, pel, base, S, P, k, bw)   # opt-in soft cloth cloak
        else: Q += cloak(chest, neck, RW, RP, pel, S, P, k, bw)
    P['_head'] = hc; P['_chest'] = chest; P['_pel'] = pel; P['_RH'] = RH; P['_RW'] = RW; P['_waist'] = waist; P['_neck'] = neck
    return Q

def head(hc, RH, S, P, k):
    """shaped head + face details + hair. P keys: eyes ('open','closed','blank','wide','half','sad'), mouth ('neutral','smile',
    'open','frown','o','grit','soft'), brow (-1 sad .. 0 .. 1 angry), look (yaw, pitch) of the eyes."""
    g = lambda kk, d=None: P.get(kk, d)
    rx_, ry_, rz_ = 0.09 * k, 0.116 * k, 0.103 * k
    fem = S['fem']
    def deform(p):
        x, y, z = p
        if y < 0:                                             # jaw narrows towards the chin, chin forward a touch
            f = 1 - 0.32 * (-y / ry_) ** 1.4 * (1 - 0.2 * fem); x *= f
            if z > 0: z *= 1 + 0.08 * (-y / ry_)
            else: z *= 1 - 0.25 * (-y / ry_)
        if z > 0: z *= 0.93 - 0.05 * fem                        # flatter face
        if y > 0.02 * k: x *= 1.02
        return np.array([x, y, z])
    sk = S['skin']; skd = shade(sk, 0.9)
    Q = ellip(hc, RH, (rx_, ry_, rz_), 16, 12, sk, deform=deform, colfn=lambda i, j, cl: skd if (cl[1] < -0.06 * k and abs(cl[0]) > 0.05 * k) else sk)
    # z of the deformed surface at (x, y): nearest sample of the parametric grid (cached per head shape)
    def zf(x, y):
        best = 0.0; bd = 1e9
        for v in np.linspace(0.08, PI - 0.08, 46):
            for u in np.linspace(-1.2, 1.2, 33):
                p = deform(np.array([rx_ * math.sin(v) * math.sin(u), ry_ * math.cos(v), rz_ * math.sin(v) * math.cos(u)]))
                d = (p[0] - x) ** 2 + (p[1] - y) ** 2
                if d < bd: bd = d; best = p[2]
        return best
    key = (round(k, 3), round(fem, 2))
    if key not in _ZF:
        _ZF[key] = {nm: zf(x, y) for nm, (x, y) in dict(eyeR=(0.032 * k, 0.012 * k), eyeL=(-0.032 * k, 0.012 * k), nose=(0, -0.012 * k),
                                                          mouth=(0, -0.05 * k), browR=(0.033 * k, 0.034 * k), browL=(-0.033 * k, 0.034 * k),
                                                          cheekR=(0.05 * k, -0.025 * k), cheekL=(-0.05 * k, -0.025 * k), chin=(0, -0.085 * k),
                                                          earR=(rx_ * 0.98, 0.0), earL=(-rx_ * 0.98, 0.0)).items()}
    Z = _ZF[key]
    def L(x, y, nm, dz=0.0): return hc + RH @ np.array([x, y, Z[nm] + dz])
    fwd = RH @ np.array([0, 0, 1.0]); up = RH @ np.array([0, 1.0, 0])
    eyes = g('eyes', 'open'); mouth = g('mouth', 'neutral'); brow = g('brow', 0.0); lk = g('look', (0.0, 0.0))
    white = (236, 232, 222); dark = (30, 22, 20)
    for sd, nm, bn in ((1, 'eyeR', 'browR'), (-1, 'eyeL', 'browL')):
        x = sd * 0.032 * k; y = 0.012 * k; c = L(x, y, nm); n = nz(RH @ np.array([sd * 0.25, 0.05, 1.0]))
        if eyes in ('closed',):
            Q += decal(c, n, up, 0.024 * k, 0.004 * k, shade(sk, 0.55), lift=0.002)
        else:
            hh = {'open': 0.014, 'wide': 0.018, 'half': 0.008, 'blank': 0.013, 'sad': 0.011}.get(eyes, 0.014) * k
            Q += poly_decal(c, n, up, [(-0.013 * k, 0), (-0.006 * k, -hh / 2), (0.007 * k, -hh / 2), (0.013 * k, 0), (0.006 * k, hh / 2), (-0.007 * k, hh / 2)], white, lift=0.0016)
            ix = c + RH @ np.array([lk[0] * 0.006 * k, lk[1] * 0.004 * k, 0]); irc = S['eye'] if eyes != 'blank' else (150, 150, 156)
            Q += decal(ix, n, up, 0.0105 * k, min(hh, 0.0105 * k), irc, lift=0.0026)
            if eyes != 'blank':
                Q += decal(ix, n, up, 0.005 * k, min(hh * 0.6, 0.005 * k), dark, lift=0.0032)
                Q += decal(ix + up * 0.0025 * k + RH @ np.array([0.002 * k, 0, 0]), n, up, 0.0026 * k, 0.0026 * k, (255, 255, 255), emit=True, lift=0.0038)
            if eyes in ('half', 'sad'):                         # upper lid
                Q += decal(c + up * 0.004 * k, n, up, 0.028 * k, 0.007 * k, shade(sk, 0.8), lift=0.0042)
            Q += decal(c + up * hh * 0.55, n, up, 0.03 * k, 0.0025 * k, dark, lift=0.0036)      # lash line
        # brow: inner end up when sad (brow < 0), down when angry (> 0)
        bcol = S['brow'] or shade(S['hair'], 0.85); bc = L(sd * 0.033 * k, 0.034 * k + (0.003 * k if eyes == 'wide' else 0), bn)
        a = -sd * 0.35 * brow
        Q += poly_decal(bc, nz(RH @ np.array([sd * 0.25, 0.1, 1.0])), RH @ (Rz(a) @ np.array([0, 1.0, 0])),
                        [(-0.016 * k, -0.003 * k), (0.016 * k, -0.002 * k), (0.016 * k, 0.003 * k), (-0.016 * k, 0.004 * k)], bcol, lift=0.003)
    # nose: a small wedge
    nb = L(0, -0.018 * k, 'nose', -0.004); tip = nb + fwd * 0.03 * k + up * -0.006 * k; tp = L(0, 0.012 * k, 'nose', -0.006)
    for sd in (1, -1):
        w = RH @ np.array([sd * 0.016 * k, 0, 0])
        _add(Q, face([tp, tip, nb + w], shade(sk, 0.97 if sd > 0 else 0.9), hc))
        _add(Q, face([nb + w, tip, nb], shade(sk, 0.78), hc))
    # mouth
    mc = L(0, -0.05 * k, 'mouth'); mn = nz(RH @ np.array([0, -0.15, 1.0])); lip = S['lip'] or mix(sk, (150, 70, 70), 0.45); md = (60, 24, 24)
    if mouth == 'smile':
        Q += poly_decal(mc, mn, up, [(-0.02 * k, 0.004 * k), (-0.01 * k, -0.003 * k), (0.01 * k, -0.003 * k), (0.02 * k, 0.004 * k), (0.01 * k, 0.0), (-0.01 * k, 0.0)], md)
    elif mouth == 'soft':
        Q += poly_decal(mc, mn, up, [(-0.016 * k, 0.002 * k), (0, -0.002 * k), (0.016 * k, 0.002 * k), (0, 0.0005 * k)], lip)
    elif mouth in ('open', 'o'):
        w_ = 0.016 if mouth == 'open' else 0.009; h_ = 0.012 if mouth == 'open' else 0.011
        Q += poly_decal(mc, mn, up, [(-w_ * k, 0), (-w_ * 0.5 * k, -h_ * k), (w_ * 0.5 * k, -h_ * k), (w_ * k, 0), (w_ * 0.5 * k, h_ * 0.25 * k), (-w_ * 0.5 * k, h_ * 0.25 * k)], md)
    elif mouth == 'frown':
        Q += poly_decal(mc, mn, up, [(-0.018 * k, -0.004 * k), (-0.008 * k, 0.002 * k), (0.008 * k, 0.002 * k), (0.018 * k, -0.004 * k), (0.008 * k, -0.0005 * k), (-0.008 * k, -0.0005 * k)], md)
    elif mouth == 'grit':
        Q += decal(mc, mn, up, 0.032 * k, 0.008 * k, (226, 220, 206)); Q += decal(mc, mn, up, 0.034 * k, 0.0018 * k, md, lift=0.004)
    else:
        Q += decal(mc, mn, up, 0.036 * k, 0.005 * k, md)
    Q += decal(mc - up * 0.008 * k, mn, up, 0.026 * k, 0.006 * k, lip, lift=0.0015)
    # ears
    for sd, nm in ((1, 'earR'), (-1, 'earL')):
        ec = hc + RH @ np.array([sd * rx_ * 0.96, -0.004 * k, -0.006 * k])
        Q += ellip(ec, RH, (0.012 * k, 0.03 * k, 0.019 * k), 6, 4, shade(sk, 0.93))
    Q += hair(hc, RH, S, P, k, (rx_, ry_, rz_), deform)
    return Q
_ZF = {}

def hair(hc, RH, S, P, k, rad, deform):
    st = S['hair_style']; hc_ = S['hair']; hd = shade(hc_, 0.82); Q = []
    rx_, ry_, rz_ = rad
    if S['helmet']:
        mc = S['helmet']
        Q += ellip(hc + RH @ np.array([0, 0.012 * k, -0.004 * k]), RH, (rx_ * 1.14, ry_ * 1.02, rz_ * 1.1), 16, 7, mc, v1=PI * 0.52,
                   colfn=lambda i, j, cl: shade(mc, 1.08) if j % 4 == 0 else mc)
        Q += limb(hc + RH @ np.array([0, -0.0 * k, 0]), hc + RH @ np.array([0, 0.012 * k, 0]), rx_ * 1.2, rx_ * 1.18, shade(mc, 0.8), n=16, m=1, ref=RH @ np.array([0, 0, 1.0]), flat=1.12)
        Q += bx(hc + RH @ np.array([0, -0.01 * k, rz_ * 1.02]), RH, (0.006 * k, 0.036 * k, 0.008 * k), shade(mc, 0.85))      # nose guard
        return Q
    if st == 'bald':
        Q += ellip(hc, RH, (rx_ * 1.03, ry_ * 1.02, rz_ * 1.03), 14, 8, hc_, deform=deform,
                   keep=lambda c: c[1] < 0.03 * k and c[1] > -0.06 * k and c[2] < 0.02 * k, closed=False)
    else:
        front = {'short': 0.068, 'long': 0.07, 'pony': 0.078, 'bun': 0.078, 'messy': 0.062}.get(st, 0.05) * k
        back = {'short': -0.07, 'long': -0.11, 'pony': -0.06, 'bun': -0.06, 'messy': -0.075}.get(st, -0.07) * k
        def keep(c):
            x, y, z = c
            if z > 0.03 * k: return y > front - 0.012 * k * abs(x) / (rx_) * 3 + (0.012 * k if abs(x) < 0.03 * k and st == 'messy' else 0)
            if z > -0.01 * k: return y > (front + back) / 2 + 0.03 * k
            return y > back
        sc = {'short': 1.06, 'pony': 1.045, 'bun': 1.045, 'long': 1.07}.get(st, 1.08)
        Q += ellip(hc, RH, (rx_ * sc, ry_ * (1.04 if st != 'bun' else 1.03), rz_ * sc), 18, 12, hc_, deform=deform, keep=keep,
                   colfn=lambda i, j, cl: shade(hc_, 0.62) if (abs(cl[0]) < 0.006 * k and cl[2] > -0.02 * k and st in ('long', 'pony', 'bun')) else (hd if (j % 3 == 0) else hc_), closed=False)
        if st == 'messy':          # a few tufts
            for a_ in (-0.7, -0.15, 0.35, 0.85):                  # tufts lying forward over the brow, not spikes
                p = hc + RH @ np.array([0.055 * k * math.sin(a_), ry_ * 0.86, 0.045 * k * math.cos(a_)])
                Q += limb(p, p + RH @ np.array([0.025 * k * math.sin(a_), -0.012 * k, 0.05 * k]), 0.018 * k, 0.005, hd, n=5, m=1, flat=0.55, ref=RH @ np.array([0, 1.0, 0]))
        if st == 'long':           # hair down the back + side locks over the shoulders
            top = hc + RH @ np.array([0, 0.02 * k, -0.05 * k])
            cs = [top + RH @ np.array([0, -s * 0.3 * k, -0.025 * k * s]) for s in np.linspace(0, 1, 5)]
            u = RH @ np.array([1.0, 0, 0]); v = RH @ np.array([0, 0, 1.0])
            rs = [(rx_ * (1.05 - 0.2 * s), 0.06 * k * (1 - 0.4 * s)) for s in np.linspace(0, 1, 5)]
            Q += loft(cs, [u] * 5, [v] * 5, rs, 12, hc_, fold=lambda i, th: 1 + 0.07 * math.cos(7 * th), th0=PI * 1.0, th1=PI * 2.0, cap0=False, cap1=False, closed=False,
                      colfn=lambda i, j: hd if j % 2 else hc_)
            for sd in (1, -1):
                a = hc + RH @ np.array([sd * rx_ * 1.0, 0.03 * k, 0.0]); b = a + RH @ np.array([sd * 0.03 * k, -0.24 * k, -0.01 * k])
                Q += limb(a, b, 0.03 * k, 0.018 * k, hc_, n=8, m=3, flat=0.35, ref=RH @ np.array([1.0 * sd, 0, 0]), colfn=lambda i, j: hd if j % 2 else hc_)
        if st == 'pony':
            a = hc + RH @ np.array([0, 0.03 * k, -rz_ * 1.02]); b = a + RH @ np.array([0, -0.08 * k, -0.06 * k]); c = b + RH @ np.array([0, -0.16 * k, -0.01 * k])
            sw = P.get('hair_sway', 0.0); c = c + RH @ np.array([sw * 0.05, 0, 0])
            Q += bx(a, RH, (0.018 * k, 0.012 * k, 0.012 * k), (150, 40, 40))
            Q += limb(a, b, 0.024 * k, 0.03 * k, hc_, n=7, m=2) + limb(b, c, 0.03 * k, 0.006 * k, hd, n=7, m=3)
        if st == 'bun':
            Q += ellip(hc + RH @ np.array([0, 0.06 * k, -rz_ * 0.92]), RH, (0.04 * k, 0.036 * k, 0.036 * k), 10, 6, hc_)
    if S['beard']:
        bc_ = S['beard']
        Q += ellip(hc, RH, (rx_ * 1.06, ry_ * 1.06, rz_ * 1.08), 16, 12, bc_, deform=deform,
                   keep=lambda c: c[1] < -0.035 * k and c[2] > -0.02 * k and not (abs(c[0]) < 0.022 * k and -0.06 * k < c[1] < -0.04 * k), closed=False,
                   colfn=lambda i, j, cl: shade(bc_, 0.85) if j % 2 else bc_)
        mc = hc + RH @ np.array([0, -0.038 * k, rz_ * 0.98])               # moustache
        Q += bx(mc, RH, (0.026 * k, 0.006 * k, 0.008 * k), bc_)
    return Q

def hand(wr, d, palm_n, grip, col, k, ring=None, side=-1):
    """hand at the wrist, pointing along d, palm facing palm_n. grip 0 = open flat, 1 = fist. ~70 faces."""
    d = nz(d); pn = np.asarray(palm_n, float); pn = nz(pn - d * float(pn @ d)) if np.linalg.norm(pn - d * float(pn @ d)) > 1e-6 else frame_for(d, (0, 0, 1))[0]
    sdv = np.cross(d, pn) * (1.0 if side < 0 else -1.0)       # across the palm (thumb side = +sdv); mirrored for the right hand (23 Nov fix: right thumbs pointed the wrong way)
    Q = []; dk = shade(col, 0.88)
    pl = 0.085 * k; pw = 0.042 * k; pt = 0.017 * k
    c = wr + d * pl * 0.5
    Rm = np.column_stack([sdv, -pn, d])                        # local x across, y = back of the hand, z = along the fingers
    Q += bx(c, Rm, (pw, pt, pl * 0.5), col)
    fl = [0.045, 0.05, 0.047, 0.038]
    for i in range(4):
        x = (-1.5 + i) * pw * 0.62; b = wr + d * pl + sdv * x
        ln = fl[i] * k; seg_ = [ln * 0.55, ln * 0.45]; dirc = d.copy(); p = b
        for s_i, sl in enumerate(seg_):
            ang = grip * (1.25 if s_i == 0 else 1.45)
            dirc = nz(dirc * math.cos(ang if s_i == 0 else ang) + pn * math.sin(ang if s_i == 0 else ang)) if s_i == 0 else nz(dirc * math.cos(ang) + np.cross(sdv, dirc) * -math.sin(ang))
            q_ = p + dirc * sl
            Q += limb(p, q_, 0.0095 * k, 0.0085 * k, col if s_i == 0 else dk, n=4, m=1, ref=-pn)
            if ring is not None and i == 2 and s_i == 0:
                Q += limb(p + dirc * sl * 0.25, p + dirc * sl * 0.45, 0.012 * k, 0.012 * k, ring, n=6, m=1, ref=-pn)
            p = q_
    # thumb
    tb = wr + d * pl * 0.25 + sdv * pw * 0.9
    tdir = nz(d * 0.55 + sdv * 0.6 + pn * (0.35 + 0.5 * grip))
    t1 = tb + tdir * 0.035 * k; tdir2 = nz(tdir * 0.6 + d * 0.3 + pn * (0.3 + 0.6 * grip) - sdv * 0.4 * grip)
    Q += limb(tb, t1, 0.012 * k, 0.01 * k, col, n=5, m=1, ref=-pn) + limb(t1, t1 + tdir2 * 0.03 * k, 0.01 * k, 0.0085 * k, dk, n=5, m=1, ref=-pn)
    return Q

def foot(an, fdir, col, k):
    fdir = nz(np.array([fdir[0], 0, fdir[2]])) if abs(fdir[1]) < 0.9 else nz(fdir)
    up = np.array([0, 1.0, 0]); sd = np.cross(up, fdir)
    heel = an - fdir * 0.045 * k; heel[1] = max(heel[1] - 0.05, an[1] - 0.075 * k)
    toe = an + fdir * 0.17 * k; toe[1] = heel[1]
    cs = []; rs = []
    for s, (rw, rh) in zip(np.linspace(0, 1, 5), ((0.04, 0.04), (0.045, 0.05), (0.048, 0.042), (0.046, 0.03), (0.035, 0.022))):
        c = heel + (toe - heel) * s; c = c + up * rh * 0.9; cs.append(c); rs.append((rw * k, rh * k))
    Q = loft(cs, [sd] * 5, [up] * 5, rs, 10, col, colfn=lambda i, j: shade(col, 0.7) if (j >= 6 and j <= 9) else col)
    return Q

def cloak(chest, neck, RW, RP, pel, S, P, k, bw):
    """cape hung from the shoulders: back half-tube that widens and drops to cloak_len, with folds; sway from P['cape_sway']"""
    col = S['cloak']; dk = shade(col, 0.78); ln = S['cloak_len'] * k; Q = []
    top = neck + RW @ np.array([0, -0.035, -0.02]); sway = P.get('cape_sway', 0.0)
    cs = []; rs = []; us = []; vs = []
    for s in np.linspace(0, 1, 6):
        c = top + np.array([0, -ln * s, 0]) + RW @ np.array([0, 0, -0.06 * s - 0.03]) + (RW @ np.array([0, 0, -1.0])) * (0.06 * s * s + sway * s * s * 0.3)
        cs.append(c); rs.append(((0.2 + 0.12 * s) * bw, (0.13 + 0.1 * s) * bw)); us.append(RW @ np.array([1.0, 0, 0])); vs.append(RW @ np.array([0, 0, 1.0]))
    Q += loft(cs, us, vs, rs, 16, col, fold=lambda i, th: 1 + 0.08 * (i / 5) * math.cos(8 * th), th0=PI * 1.08, th1=PI * 1.92, cap0=False, cap1=False, closed=False,
              colfn=lambda i, j: dk if j % 2 else col)
    if S['hood']:
        hc = P.get('_head_hint', neck + RW @ np.array([0, 0.03, -0.1]))
        Q += ellip(neck + RW @ np.array([0, 0.02, -0.11]), RW @ Rx(0.5), (0.12 * k, 0.05 * k, 0.09 * k), 10, 4, col, closed=False)
    # clasp
    Q += bx(neck + RW @ np.array([0.0, -0.05, 0.075 * bw]), RW, (0.02, 0.02, 0.008), S['buckle'])
    return Q

def cloak_hd(chest, neck, RW, RP, Rb, pel, base, S, P, k, bw):
    """soft cloth cloak (opt-in: spec(cloak_hd=True)); ~ 22 x 32 grid instead of the 6 x 16 tube.
    Each column hangs from the shoulders as a chain under gravity: uneven pleats that deepen toward the hem, a wavy hem,
    the top edge rides the shoulders (shrug / raised arms), the cloth slides over the back, skirt and legs instead of
    passing through them and pools on the ground (kneel / crouch). Motion: P['cape_sway'] (back, as before),
    P['cape_side'] (sideways), P['cape_t'] (time: pleats breathe and a ripple runs down the cloth); body.Performer sets all
    three from the body's own motion with a spring (follow-through)."""
    col = S['cloak']; ln = S['cloak_len'] * k; Q = []; NR, NC = 22, 32
    sway = P.get('cape_sway', 0.0); sside = P.get('cape_side', 0.0); tt = P.get('cape_t', 0.0)
    top = neck + RW @ np.array([0, -0.035, -0.02]); gy = float(base[1]) + 0.012
    th0, th1 = PI * 1.03, PI * 1.97
    bk = RW @ np.array([0, 0, -1.0]); bk[1] = 0.0; bk = nz(bk) if np.linalg.norm(bk) > 1e-6 else np.array([0, 0, -1.0])
    sdw = np.cross(np.array([0, 1.0, 0]), bk)                                  # world sideways (character's right when bk = back)
    # how far each shoulder is raised (shrug, arms up) relative to rest
    lift = {}
    for s_, sg in (('r', 1), ('l', -1)):
        shp = P.get('_' + s_ + 'sh')
        lift[sg] = 0.0 if shp is None else float(np.clip((RW.T @ (np.asarray(shp) - chest))[1] - 0.05 * k, -0.05, 0.12))
    # collision shapes: torso (elliptic, along the spine), skirt, leg + upper-arm capsules
    caps = []
    for a_, b_, r_ in (('_rhip', '_rknee', 0.085), ('_lhip', '_lknee', 0.085), ('_rknee', '_rankle', 0.07), ('_lknee', '_lankle', 0.07),
                       ('_rsh', '_rel', 0.058), ('_lsh', '_lel', 0.058)):
        if P.get(a_) is not None and P.get(b_) is not None: caps.append((np.asarray(P[a_], float), np.asarray(P[b_], float), r_ * max(1.0, bw)))
    sk = S['skirt'] or 0.0; crouch = P.get('crouch', 0.0)
    def collide(p):
        # torso: ellipse around the spine pel -> neck in the chest frame
        ax = neck - pel; u = float(np.clip((p - pel) @ ax / max(ax @ ax, 1e-9), 0.0, 1.0))
        if u > 0.0 or (p - pel) @ ax > -0.02:
            c = pel + ax * u; R_ = RW if u > 0.45 else RP; q = R_.T @ (p - c)
            rx, rz = (0.2 + 0.015 * u) * bw, (0.15 - 0.01 * u) * bw; e = (q[0] / rx) ** 2 + (q[2] / rz) ** 2
            if e < 1.0 or (q[2] > 0.0 and abs(q[0]) < rx):                       # the cloak always stays on the BACK of the torso
                xx = float(np.clip(q[0], -rx * 0.995, rx * 0.995)); q = np.array([xx, q[1], -(rz + 0.012) * math.sqrt(1.0 - (xx / rx) ** 2)]); p = c + R_ @ q
        # skirt hem cone below the pelvis
        if sk > 0.02:
            q = RP.T @ (p - pel); d = -q[1]
            if 0.0 < d < sk + 0.02:
                w = d / sk; rx, rz = (0.17 + 0.06 * w) * bw + 0.012, (0.12 + 0.07 * w) * bw + 0.08 * crouch * w + 0.012
                e = (q[0] / rx) ** 2 + (q[2] / rz) ** 2
                if e < 1.0 or (q[2] > 0.0 and abs(q[0]) < rx):
                    xx = float(np.clip(q[0], -rx * 0.995, rx * 0.995)); p = pel + RP @ np.array([xx, q[1], -rz * math.sqrt(1.0 - (xx / rx) ** 2)])
        for a, b, r in caps:
            ab = b - a; h = float(np.clip((p - a) @ ab / max(ab @ ab, 1e-9), 0.0, 1.0)); c = a + ab * h; dv = p - c; dl = np.linalg.norm(dv)
            if dl < r: p = c + (dv / dl if dl > 1e-6 else bk) * r
        if p[1] < gy: p = p.copy(); p[1] = gy
        return p
    G = []; F = []
    for j in range(NC + 1):
        th = th0 + (th1 - th0) * j / NC; cs, sn = math.cos(th), math.sin(th)
        # pleats: three uneven waves around the back, deeper toward the hem, drifting slowly with time
        def pleat(s):
            a = (0.016 + 0.04 * s ** 1.1) * bw
            return a * (0.55 * math.sin(7 * th + 0.4 + 0.25 * math.sin(tt * 0.9)) + 0.3 * math.sin(12 * th + 1.7 + 1.6 * s + 0.3 * tt)
                        + 0.25 * math.sin(4 * th + 2.3 + 0.4 * math.sin(tt * 0.6 + 1.0)))
        hem = 1.0 + 0.035 * math.sin(5 * th + 0.8) + 0.02 * math.sin(11 * th + 2.0)
        sgn = 1 if cs > 0 else -1; side_w = abs(cs) ** 1.5
        p0 = top + RW @ np.array([0.19 * bw * cs, -0.03 * side_w + lift[sgn] * side_w * 0.8, 0.12 * bw * sn])
        nrm = RW @ np.array([cs, 0, sn])                                       # outward around the body
        D = []
        for i in range(NR + 1):
            s = i / NR; L_ = ln * hem
            p = p0 + np.array([0, -L_ * s, 0]) + RW @ np.array([0.12 * bw * cs * s, 0, 0.1 * bw * sn * s - 0.06 * s])
            p = p + nrm * pleat(s)
            p = p + bk * (0.05 * s * s + sway * s * s * 0.3) + sdw * (sside * s * s * 0.3)
            p = p + bk * (0.012 + 0.03 * abs(sway)) * s ** 1.5 * math.sin(6.0 * s - 3.2 * tt + 0.6 * th)   # ripple travelling down
            D.append(p)
        col_pts = [D[0]]
        for i in range(1, NR + 1):                                             # hang as a chain: keep segment lengths, slide over the body
            seg = np.linalg.norm(D[i] - D[i - 1]); pr = col_pts[-1]; d0 = nz(D[i] - D[i - 1])
            ax = neck - pel; u = float((pr - pel) @ ax / max(ax @ ax, 1e-9))
            if -0.05 < u < 1.0:                                                # on the back: slide along it when gravity points into the body (bow)
                nb = (RW if u > 0.45 else RP) @ np.array([0, 0, -1.0])
                if d0 @ nb < 0.0: d0 = nz(d0 - nb * float(d0 @ nb))
            q = pr + d0 * seg
            col_pts.append(collide(q))
        G.append(col_pts)
        F.append([pleat(i / NR) / ((0.016 + 0.04 * (i / NR) ** 1.1) * bw + 1e-9) for i in range(NR + 1)])
    R = [[G[j][i] for j in range(NC + 1)] for i in range(NR + 1)]
    C = [np.mean([G[j][i] for j in range(NC + 1)], axis=0) - bk * 0.3 for i in range(NR + 1)]   # 'inside' = toward the body
    dk = shade(col, 0.58); lt = shade(col, 1.15)
    def colfn(i, j):
        f = (F[j][i] + F[min(NC, j + 1)][i]) * 0.5                             # pleat crests lighter, valleys darker
        if i == NR - 1: return shade(col, 0.6)                                 # darker hem band so the edge reads
        return mix(dk, lt, float(np.clip(0.5 + 0.7 * f, 0.0, 1.0)))
    Q += rings_mesh(R, col, C, False, False, colfn, False, False)
    if S['hood']:
        Q += ellip(neck + RW @ np.array([0, 0.02, -0.11]), RW @ Rx(0.5), (0.12 * k, 0.05 * k, 0.09 * k), 10, 4, col, closed=False)
    Q += bx(neck + RW @ np.array([0.0, -0.05, 0.075 * bw]), RW, (0.02, 0.02, 0.008), S['buckle'])
    return Q


# ------------------------------------------------------------------ props
def potion(base, R=None, liquid=(230, 40, 50), glass=(200, 210, 220), fill=1.0, glow=1.0, cork=(150, 110, 70), scale=1.0):
    """round healing flask (lathe), glowing liquid inside, cork. base = the bottom centre (world)."""
    R = np.eye(3) if R is None else R; s = scale; Q = []
    prof = [(0.0, 0.0), (0.03 * s, 0.002 * s), (0.046 * s, 0.025 * s), (0.05 * s, 0.05 * s), (0.044 * s, 0.075 * s), (0.026 * s, 0.092 * s), (0.014 * s, 0.1 * s), (0.014 * s, 0.135 * s), (0.017 * s, 0.14 * s)]
    # opaque surfaces only (zraster has no transparency): the filled part of the body IS the glowing liquid, the rest is glass
    lq = tuple(int(c * (0.55 + 0.45 * glow)) for c in liquid); lq2 = tuple(min(255, int(c * 1.25 + 20)) for c in lq)
    yf = 0.092 * s * max(0.0, min(1.0, fill))
    def cut(y):
        for (r0, y0), (r1, y1) in zip(prof, prof[1:]):
            if y0 <= y <= y1: return r0 + (r1 - r0) * (y - y0) / max(1e-9, y1 - y0)
        return prof[-1][0]
    lp = [p for p in prof if p[1] < yf] + [(cut(yf), yf)]
    gp = [(cut(yf), yf)] + [p for p in prof if p[1] > yf]
    if fill > 0.02 and len(lp) >= 2:
        L = lathe(base, R, lp, 10, lq, colfn=lambda i, j: lq2 if j in (1, 2) else lq, cap1=False)
        for q in L: q['emit'] = glow > 0.3
        Q += L
    Q += lathe(base, R, gp if fill > 0.02 else prof, 10, glass, colfn=lambda i, j: shade(glass, 1.12) if j in (1, 2) else glass, cap0=fill <= 0.02, cap1=False)
    Q += lathe(np.asarray(base) + R @ np.array([0, 0.128 * s, 0]), R, [(0.016 * s, 0), (0.018 * s, 0.02 * s), (0.014 * s, 0.03 * s)], 8, cork)
    return Q

def wooden_horse(base, R=None, col=(178, 128, 76), scale=1.0):
    """the small carved wooden horse toy (body, neck, head, 4 legs, mane, tail)"""
    R = np.eye(3) if R is None else R; s = scale; b = np.asarray(base, float); dk = shade(col, 0.78); Q = []
    def P(x, y, z): return b + R @ np.array([x * s, y * s, z * s])
    Q += ellip(P(0, 0.05, 0), R, (0.018 * s, 0.018 * s, 0.035 * s), 8, 5, col)
    Q += limb(P(0, 0.06, 0.028), P(0, 0.09, 0.045), 0.011 * s, 0.009 * s, col, n=6, m=1)
    Q += limb(P(0, 0.092, 0.044), P(0, 0.078, 0.066), 0.0085 * s, 0.0055 * s, col, n=6, m=1)
    Q += bx(P(0, 0.08, 0.034), R @ Rx(0.6), (0.0022 * s, 0.006 * s, 0.016 * s), dk)
    for sd_ in (1, -1): Q += limb(P(sd_ * 0.004, 0.096, 0.046), P(sd_ * 0.005, 0.108, 0.042), 0.0028 * s, 0.001 * s, dk, n=4, m=1)
    for x in (-0.011, 0.011):
        for z in (-0.024, 0.024):
            Q += limb(P(x, 0.045, z), P(x, 0.0, z), 0.0055 * s, 0.0045 * s, col, n=5, m=1)
    Q += limb(P(0, 0.058, -0.033), P(0, 0.035, -0.05), 0.005 * s, 0.002 * s, dk, n=5, m=1)
    Q += decal(P(0.0075, 0.085, 0.058), R @ np.array([1.0, 0, 0]), R @ np.array([0, 1.0, 0]), 0.004 * s, 0.004 * s, (30, 20, 14), lift=0.0005)
    Q += decal(P(-0.0075, 0.085, 0.058), R @ np.array([-1.0, 0, 0]), R @ np.array([0, 1.0, 0]), 0.004 * s, 0.004 * s, (30, 20, 14), lift=0.0005)
    return Q

def sword(hilt, d, up, col=(196, 204, 214), grip=(80, 50, 34), guard=(170, 140, 80), length=0.85):
    """straight sword: hilt = point in the hand, d = blade direction, up = flat side normal"""
    d = nz(d); up = nz(np.asarray(up, float) - d * float(np.asarray(up, float) @ d)); sd = np.cross(d, up); Q = []
    h = np.asarray(hilt, float); g0 = h + d * 0.05
    Q += limb(h - d * 0.07, g0, 0.016, 0.016, grip, n=6, m=1, ref=up)
    Q += ellip(h - d * 0.085, np.column_stack([sd, d, up]), (0.02, 0.02, 0.02), 6, 4, guard)
    Q += bx(g0, np.column_stack([sd, d, up]), (0.08, 0.012, 0.016), guard)
    bl = length; tip = g0 + d * bl; w = 0.028
    for sgn in (1, -1):
        e = sd * w * sgn
        _add(Q, face([g0 + e, tip - d * 0.06 + e * 0.7, tip, g0], col if sgn > 0 else shade(col, 0.86), g0 - up * sgn * 0.1, closed=False))
        _add(Q, face([g0 + e, tip - d * 0.06 + e * 0.7, tip, g0], shade(col, 0.95), g0 + up * sgn * 0.1, closed=False))
    return Q
