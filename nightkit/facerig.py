"""Shared high-density face rig (ported from examples/fox_wind.py, 24 Nov 2026), colours + details set per character with set_style().
Expression dict E keys: browR/L, innerR/L, furrow, eyesR/L (0 shut .. 1 open .. 1.3 wide), squintR/L, smR/L (smile corners), press,
open, round, wide, teeth, jaw, cheekR/L, hollowR/L, look=(x, y). Usage:
    facerig.set_style(skin=..., eye=..., ...); M = facerig.Mesh(head_centre, head_R)
    facerig.head_mesh(M, E); facerig.eyes_geo(M, E); facerig.brows_geo(M, E); facerig.nose_geo(M, E); facerig.mouth_geo(M, E); M.Q -> faces"""
import math
import numpy as np
from . import hd
from .hd import shade, mix as mixc
PI = math.pi
V = np.array
ST = dict(skin=(226, 178, 142), eye=(70, 120, 92), brow=(64, 38, 22), lip=(196, 112, 104), mouth_in=(58, 18, 24), teeth=(236, 230, 214),
          tongue=(178, 78, 86), stubble=True, scar=True)
def set_style(**kw): ST.update(kw)
RX, RY, RZ = 0.09, 0.116, 0.103
def base_def(p):
    x, y, z = p[..., 0].copy(), p[..., 1].copy(), p[..., 2].copy()
    ny = np.clip(-y / RY, 0, 1); neg = y < 0
    x = np.where(neg, x * (1 - 0.30 * ny ** 1.4), x)
    z = np.where(neg & (z > 0), z * (1 + 0.08 * ny), z)
    z = np.where(neg & (z <= 0), z * (1 - 0.25 * ny), z)
    z = np.where(z > 0, z * 0.93, z)
    x = np.where(y > 0.02, x * 1.02, x)
    # brow ridge + cheekbones: a touch of relief so the flat shading reads as a face
    br = np.exp(-((y - 0.03) / 0.012) ** 2) * np.exp(-(x / 0.06) ** 2) * (z > 0)
    ck = sum(np.exp(-(((x - s * 0.052) / 0.02) ** 2 + ((y + 0.012) / 0.016) ** 2)) for s in (1, -1)) * (z > 0)
    z = z + 0.004 * br + 0.004 * ck
    return np.stack([x, y, z], -1)
def expr_def(p, E):
    x, y, z = p[..., 0].copy(), p[..., 1].copy(), p[..., 2].copy()
    jaw = E.get('jaw', 0.0)
    if jaw:
        w = np.clip((-y - 0.058) / 0.022, 0, 1); w = w * w * (3 - 2 * w) * np.clip((z + 0.04) / 0.05, 0, 1)
        a = 0.2 * jaw * w; py, pz = y + 0.01, z + 0.02
        y = -0.01 + py * np.cos(a) - pz * np.sin(a); z = -0.02 + py * np.sin(a) + pz * np.cos(a)
    fr = np.clip((z + 0.01) / 0.03, 0, 1)                       # front-of-face weight (soft, no seam)
    x0, y0 = x.copy(), y.copy()
    for sd, side in ((1, 'R'), (-1, 'L')):
        ck = E.get('cheek' + side, 0.0); hol = E.get('hollow' + side, 0.0); sm_ = E.get('sm' + side, 0.0)
        if ck:
            # cheek apple: rises toward the lower lid, pushes forward and out
            g = np.exp(-(((x0 - sd * 0.046) / 0.024) ** 2 + ((y0 + 0.024) / 0.022) ** 2)) * fr
            eyeguard = np.clip((-0.004 - y0) / 0.014, 0, 1) ** 1.5               # no forward bulge under the eye decals (no poke-through)
            z = z + 0.014 * ck * g * eyeguard; y = y + 0.012 * ck * g * np.clip((0.006 - y0) / 0.01, 0, 1); x = x + sd * 0.004 * ck * g
            # the face outline widens at cheek height (silhouette)
            gs = np.exp(-((y0 + 0.022) / 0.024) ** 2) * np.clip((sd * x0 - 0.05) / 0.03, 0, 1) * np.clip((z + 0.05) / 0.05, 0, 1)
            x = x + sd * 0.007 * ck * gs; y = y + 0.004 * ck * gs
            # nasolabial fold: a groove from the nose wing down past the mouth corner
            ax, ay, bx_, by_ = sd * 0.015, -0.018, sd * 0.032, -0.066
            dx, dy = bx_ - ax, by_ - ay; L2 = dx * dx + dy * dy
            tpar = np.clip(((x0 - ax) * dx + (y0 - ay) * dy) / L2, 0, 1)
            dist = np.hypot(x0 - (ax + tpar * dx), y0 - (ay + tpar * dy))
            fold = np.exp(-(dist / 0.0075) ** 2) * np.sin(np.pi * tpar) * fr
            z = z - 0.006 * ck * fold
            fl = E.get('fill', 0.0) * ck
            if fl:
                # opt-in (28 Nov): a big grin bunches the lower cheek too - without this the lifted apple leaves a hollow below it
                # and the jaw line steps in under the widened cheek (the 'collapsed' laughing face)
                gl_ = np.exp(-(((x0 - sd * 0.05) / 0.026) ** 2 + ((y0 + 0.05) / 0.024) ** 2)) * fr
                z = z + 0.007 * fl * gl_
                gs2 = np.exp(-((y0 + 0.05) / 0.03) ** 2) * np.clip((sd * x0 - 0.035) / 0.03, 0, 1) * np.clip((z + 0.05) / 0.05, 0, 1)
                x = x + sd * 0.006 * fl * gs2
        if sm_:
            # skin at the mouth corner follows the corner up and out
            gc = np.exp(-(((x0 - sd * 0.024) / 0.013) ** 2 + ((y0 + 0.05) / 0.013) ** 2)) * fr
            y = y + 0.005 * sm_ * gc; x = x + sd * 0.004 * sm_ * gc
        if hol:
            # pursed lips: the cheek pulls in below the cheekbone
            gh = np.exp(-(((x0 - sd * 0.052) / 0.02) ** 2 + ((y0 + 0.052) / 0.02) ** 2)) * fr
            z = z - 0.009 * hol * gh; x = x - sd * 0.006 * hol * gh
            gl = np.exp(-(((x0 - sd * 0.018) / 0.012) ** 2 + ((y0 + 0.05) / 0.012) ** 2)) * fr
            x = x - sd * 0.004 * hol * gl                              # mouth corners drawn in with the pucker
    return np.stack([x, y, z], -1)
def sph(u, v): return np.stack([RX * np.sin(v) * np.sin(u), RY * np.cos(v), RZ * np.sin(v) * np.cos(u)], -1)
def surf(u, v, E): return expr_def(base_def(sph(u, v)), E)
def on_uv(u, v, lift, E):
    u = np.asarray(u, float); v = np.asarray(v, float); p = surf(u, v, E); e = 1e-3
    du = surf(u + e, v, E) - surf(u - e, v, E); dv = surf(u, v + e, E) - surf(u, v - e, E)
    n = np.cross(du, dv); n = n / (np.linalg.norm(n, axis=-1, keepdims=True) + 1e-12)
    n = np.where((n * p).sum(-1, keepdims=True) < 0, -n, n)
    return p + n * np.asarray(lift, float)[..., None] if np.ndim(lift) else p + n * lift
def on(xy, lift, E):
    xy = np.asarray(xy, float).reshape(-1, 2); x, y = xy[:, 0], xy[:, 1]
    v = np.arccos(np.clip(y / RY, -0.995, 0.995)); u = np.arcsin(np.clip(x / (RX * np.sin(v)), -0.995, 0.995))
    return on_uv(u, v, lift, E)

class Mesh:
    """collects faces in head-local coordinates, then maps them to the world"""
    def __init__(self, hc, R): self.hc = np.asarray(hc, float); self.R = R; self.Q = []
    def W(self, p): return self.hc + np.asarray(p) @ self.R.T
    def tri(self, a, b, c, col, emit=False):
        q = hd.face([self.W(a), self.W(b), self.W(c)], col, emit=emit)
        if q: self.Q.append(q)
    def strip(self, top, bot, col, emit=False, colfn=None):
        """quads between two point rows (local), split into triangles (always convex)"""
        for j in range(len(top) - 1):
            c = colfn(j) if colfn else col
            self.tri(top[j], top[j + 1], bot[j + 1], c, emit); self.tri(top[j], bot[j + 1], bot[j], c, emit)
    def fan(self, c, ring, col, emit=False):
        for j in range(len(ring)): self.tri(c, ring[j], ring[(j + 1) % len(ring)], col, emit)

_HEADGRID = {}
def head_mesh(M, E, hair_on=True):
    uu = np.r_[np.linspace(-1.25, 1.25, 31)[:-1], np.linspace(1.25, 2 * PI - 1.25, 19)[:-1]] % (2 * PI)
    vv = np.r_[np.linspace(0, 0.95, 7)[:-1], np.linspace(0.95, 2.55, 21)[:-1], np.linspace(2.55, PI, 6)]
    nu, nv = len(uu), len(vv) - 1
    U, Vv = np.meshgrid(uu, vv); G = surf(U, Vv, E)
    sk = ST['skin']; skd = shade(sk, 0.9); stub = mixc(sk, (120, 86, 64), 0.22); blush = mixc(sk, (226, 130, 116), 0.12)
    hcW = M.hc
    for i in range(nv):
        for j in range(nu):
            k = (j + 1) % nu; pl = [G[i, j], G[i, k], G[i + 1, k], G[i + 1, j]]; cl = np.mean(pl, axis=0)
            x, y, z = cl
            col = sk
            if y < -0.06 and abs(x) > 0.04: col = skd
            if ST['stubble'] and y < -0.044 and z > -0.01 and not (abs(x) < 0.03 and y > -0.08): col = stub      # light stubble along the jaw + chin
            if ST['stubble'] and y < -0.088 and z > -0.02: col = stub
            if z > 0.03 and abs(abs(x) - 0.05) < 0.016 and -0.042 < y < -0.012: col = blush
            q = hd.face([M.W(p) for p in pl], col, inside=hcW)
            if q: M.Q.append(q)
    # ears
    for sd in (1, -1):
        ec = V((sd * RX * 0.96, -0.004, -0.006))
        for q in hd.ellip(M.W(ec), M.R, (0.012, 0.03, 0.019), 8, 5, shade(sk, 0.93)): M.Q.append(q)

def eyes_geo(M, E):
    for sd, side in ((1, 'R'), (-1, 'L')):
        cx, cy = sd * 0.033, 0.012
        op = E['eyes' + side]; sq = E['squint' + side]
        es = E.get('eye_size', 1.0)                    # 1 = the original rig (Fox Wind / Sorceress); face.py uses a bigger anime eye
        n = 9; s = np.linspace(-1, 1, n); hw = 0.0135 * es
        x = cx + s * hw
        tilt = 0.0012 * s * sd                       # outer corner a touch higher
        ck = E.get('cheek' + side, 0.0); wide_ = float(np.clip((op - 1.0) / 0.3, 0, 1)); KU = 0.0085 * es * (1 + 0.3 * wide_); KL = 0.0058 * es * (1 + 0.2 * wide_)
        up_full = cy + tilt + KU * (1 - s ** 2) ** 0.8 + 0.0006
        lo_full = cy + tilt - KL * (1 - s ** 2) ** 0.8
        lid = lo_full + 0.0006 + (up_full - lo_full) * np.clip(op / 1.3, 0, 1.0) * (1 - 0.5 * sq)
        lid = np.maximum(lid, lo_full + 0.0004)
        llo = lo_full + (lid - lo_full) * np.clip(0.55 * sq + 0.5 * ck, 0, 0.9)
        llo = np.minimum(llo, lid - 0.0002)
        P2 = lambda xs, ys, lift: on(np.stack([xs, ys], -1), lift, E)
        # sclera
        M.strip(P2(x, up_full, 0.0012), P2(x, lo_full, 0.0012), (240, 236, 228))
        # iris + pupil + glint (kept inside the eye opening)
        lx, ly = E['look']; ix = cx + np.clip(lx, -1, 1) * 0.0032 * es; iy = cy + 0.0006 + np.clip(ly, -1, 1) * 0.0022 * es
        th = np.linspace(0, 2 * PI, 12, endpoint=False)
        def ring(r):
            xs = ix + np.cos(th) * r; ys = iy + np.sin(th) * r
            ss = np.clip((xs - cx) / hw, -0.97, 0.97)
            top = cy + 0.0012 * ss * sd + KU * (1 - ss ** 2) ** 0.8; bot = cy + 0.0012 * ss * sd - KL * (1 - ss ** 2) ** 0.8
            return np.stack([xs, np.clip(ys, bot, top)], -1)
        M.fan(on([[ix, iy]], 0.0018, E)[0], on(ring(0.0056 * es), 0.0018, E), ST['eye'])
        M.fan(on([[ix, iy]], 0.0022, E)[0], on(ring(0.0035 * es), 0.0022, E), shade(ST['eye'], 0.55))
        M.fan(on([[ix, iy]], 0.0026, E)[0], on(ring(0.0022 * es), 0.0026, E), (16, 12, 12))
        g0 = on([[ix + 0.0016, iy + 0.0018]], 0.003, E)[0]
        M.fan(g0, on(np.stack([ix + 0.0016 + np.cos(th[::3]) * 0.0009, iy + 0.0018 + np.sin(th[::3]) * 0.0009], -1), 0.003, E), (255, 255, 250))
        # upper lid (covers everything above the lid line) + lash line + crease
        lidcol = shade(ST['skin'], 0.9)
        M.strip(P2(x, up_full + 0.0034, 0.0034), P2(x, lid, 0.0034), lidcol)
        lash = np.where(s * sd > 0, 0.0017, 0.0011) * E.get('bold', 1.0)
        M.strip(P2(x * 1.0 + sd * 0.0006 * (s * sd > 0.6), lid + lash, 0.0038), P2(x, lid - 0.0003, 0.0038), (34, 22, 18))
        M.strip(P2(x[1:-1], up_full[1:-1] + 0.0042, 0.0036), P2(x[1:-1], up_full[1:-1] + 0.0034, 0.0036), shade(ST['skin'], 0.84))
        # lower lid
        M.strip(P2(x, llo, 0.0032), P2(x, lo_full - 0.0026, 0.0032), shade(ST['skin'], 0.95))
        M.strip(P2(x, llo + 0.0004, 0.0034), P2(x, llo - 0.0004, 0.0034), shade(ST['skin'], 0.8))

def brows_geo(M, E):
    fu = max(0.0, E.get('furrow', 0.0))
    for sd, side in ((1, 'R'), (-1, 'L')):
        r = E['brow' + side]; inn = E['inner' + side] - 0.5 * fu
        s = np.linspace(-1, 1, 7)                       # -1 = inner end, +1 = outer end
        x = sd * (0.033 + 0.017 * s - 0.0035 * fu * (1 - s) / 2)
        y = 0.0295 + 0.012 * (E.get('eye_size', 1.0) - 1) + 0.0095 * r + (0.0024 + 0.0028 * max(0.0, r)) * (1 - s ** 2) + 0.0045 * inn * (1 - s) / 2 - 0.0012 * s
        th = (0.0052 - 0.002 * (s + 1) / 2) * E.get('bold', 1.0)
        M.strip(on(np.stack([x, y + th * 0.55], -1), 0.0042, E), on(np.stack([x, y - th * 0.45], -1), 0.0042, E), ST['brow'])
        if r > 0.55:                                     # forehead line over a high brow
            k_ = min(1.0, (r - 0.55) / 0.4); ys = 0.0295 + 0.0095 * r + 0.012
            xs = sd * np.linspace(0.02, 0.046, 5)
            M.strip(on(np.stack([xs, np.full(5, ys + 0.0006 * k_)], -1), 0.0018, E), on(np.stack([xs, np.full(5, ys - 0.0006 * k_)], -1), 0.0018, E), shade(ST['skin'], 0.86))
    if fu > 0.12:                                        # furrow creases between the brows
        for sd in (1, -1):
            w_ = 0.0007 * min(1.0, fu * 1.6)
            a = on([[sd * 0.0062 - w_, 0.036], [sd * 0.0062 + w_, 0.036]], 0.0026, E); b = on([[sd * 0.0072 - w_, 0.024], [sd * 0.0072 + w_, 0.024]], 0.0026, E)
            M.tri(a[0], a[1], b[1], shade(ST['skin'], 0.78)); M.tri(a[0], b[1], b[0], shade(ST['skin'], 0.78))
    if not ST['scar']: return
    # a little scar through the left brow (his left = screen right)
    a = on([[-0.045, 0.046], [-0.042, 0.047]], 0.0046, E); b = on([[-0.036, 0.024], [-0.0335, 0.0245]], 0.0046, E)
    M.tri(a[0], a[1], b[1], (214, 150, 136)); M.tri(a[0], b[1], b[0], (214, 150, 136))

def nose_geo(M, E):
    top = on([[0, 0.014]], -0.002, E)[0]; base = on([[0, -0.024]], -0.003, E)[0]
    fwd = V((0, -0.05, 1.0)); fwd = fwd / np.linalg.norm(fwd)
    tip = base + fwd * 0.021 + V((0, 0.003, 0)); und = base + fwd * 0.01 + V((0, -0.003, 0))
    wR = on([[0.0115, -0.022]], 0.002, E)[0]; wL = on([[-0.0115, -0.022]], 0.002, E)[0]
    mR = on([[0.007, -0.004]], 0.0, E)[0] + fwd * 0.012; mL = on([[-0.007, -0.004]], 0.0, E)[0] + fwd * 0.012
    c1 = shade(ST['skin'], 1.0); c2 = shade(ST['skin'], 0.93); c3 = shade(ST['skin'], 0.8)
    M.tri(top, mR, mL, c1); M.tri(mR, tip, mL, c1)
    M.tri(top, wR, mR, c2); M.tri(mR, wR, tip, c2); M.tri(top, mL, wL, shade(ST['skin'], 0.9)); M.tri(mL, tip, wL, shade(ST['skin'], 0.9))
    M.tri(wR, und, tip, c3); M.tri(wL, tip, und, c3)
    nR = und + (wR - und) * 0.45 + V((0, -0.0005, 0)); nL = und + (wL - und) * 0.45 + V((0, -0.0005, 0))
    M.tri(nR, und, wR, (90, 50, 44)); M.tri(nL, wL, und, (90, 50, 44))

def mouth_geo(M, E):
    op = max(0.0, E['open']); wd = max(0.0, E['wide']); rd = max(0.0, E.get('round', 0.0)); smL, smR = E['smL'] * (1 - rd), E['smR'] * (1 - 0.7 * rd); tee = E.get('teeth', 0.0)
    n = 13; s = np.linspace(-1, 1, n); pr = float(np.clip(E.get('press', 0.0), 0, 1))
    halfw = 0.0185 * (1 + 0.24 * wd) * (1 + 0.07 * (smL + smR)) * (1 - 0.45 * rd)
    ih = 0.0011 + 0.021 * op * (1 + 0.1 * rd) * (1 - 0.25 * wd) + 0.003 * tee
    cy = -0.051; shift = 0.003 * (smR - smL)
    smv = np.where(s > 0, smR, smL); opp = np.where(s > 0, smL, smR)
    # one-sided smirk: the smiling corner lifts and pulls out, the other corner sinks a touch
    corner = 0.0125 * smv * np.abs(s) ** 1.7 - 0.0025 * np.clip(np.where(s > 0, smL - smR, smR - smL), 0, 1) * np.abs(s) ** 2 - 0.0012 * np.abs(s) ** 2
    prof = (1 - s ** 2) ** (0.75 - 0.3 * rd)
    x = s * halfw * (1 + 0.22 * smv * (np.abs(s) > 0.5)) + shift
    iu = cy + corner + ih * 0.32 * prof
    il = cy + corner - ih * 0.68 * prof
    sq = np.sqrt(np.clip(1 - s ** 2, 0, 1))
    ou = iu + (0.0042 + 0.0012 * (1 - np.abs(s))) * sq * (1 + 0.45 * rd) * (1 - 0.4 * pr) - 0.0011 * np.exp(-(s / 0.14) ** 2) * sq
    ol = il - 0.0072 * sq * (1 - 0.25 * op) * (1 + 0.3 * rd) * (1 - 0.45 * pr)
    pk = 0.0022 * rd                                   # rounded lips push forward
    P2 = lambda xs, ys, lift: on(np.stack([xs, ys], -1), lift + pk * np.sqrt(np.clip(1 - (np.asarray(xs) - shift) ** 2 / (halfw * 1.05) ** 2, 0, 1)), E)
    M.strip(P2(x, iu, 0.0012), P2(x, il, 0.0012), ST['mouth_in'])
    if ih > 0.0035:
        tw = np.abs(s) < 0.78
        th_ = np.minimum(iu - il, 0.0042 + 0.003 * tee + 0.002 * wd)
        M.strip(P2(x[tw], iu[tw] + 0.0002, 0.0016), P2(x[tw], iu[tw] - th_[tw], 0.0016), ST['teeth'])
        if tee > 0.3:
            M.strip(P2(x[tw], il[tw] + np.minimum(iu - il, 0.003)[tw], 0.0016), P2(x[tw], il[tw] - 0.0002, 0.0016), shade(ST['teeth'], 0.9))
    if op > 0.35:
        th = np.linspace(0, PI, 8); tc = cy - ih * 0.5
        tx = np.cos(th) * halfw * 0.55 + shift; ty = il[n // 2] + 0.0004 + np.sin(th) * min(ih * 0.3, 0.0055)
        M.strip(P2(tx, ty, 0.0018), P2(tx, np.full_like(ty, il[n // 2] + 0.0003), 0.0018), ST['tongue'])
    lipd = shade(ST['lip'], 0.86)
    M.strip(P2(x, ou, 0.0022), P2(x, iu, 0.0022), lipd)
    M.strip(P2(x, il, 0.0022), P2(x, ol, 0.0022), ST['lip'])
    # corner creases when smiling (cheek lines)
    for sd, v_ in ((1, smR), (-1, smL)):
        if v_ > 0.25:
            ex = x[-1] if sd > 0 else x[0]; ey = (iu[-1] if sd > 0 else iu[0])
            a = on([[ex + sd * 0.004, ey + 0.004 * v_], [ex + sd * 0.0052, ey + 0.004 * v_]], 0.002, E)
            b = on([[ex + sd * 0.0015, ey - 0.006 * v_], [ex + sd * 0.0027, ey - 0.006 * v_]], 0.002, E)
            M.tri(a[0], a[1], b[1], shade(ST['skin'], 0.82)); M.tri(a[0], b[1], b[0], shade(ST['skin'], 0.82))

