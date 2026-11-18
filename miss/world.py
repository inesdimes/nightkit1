"""Step 2: the locked world. Right-handed: +X down the corridor (the shooting direction), +Y up, +Z toward the viewer's side.
Floor y=0, back wall z=-1.5, END WALL x=+7 (the target board hangs on it), open side z=+1.5 (no wall, cameras sit there).
Everything is boxes / flat quads; one wall torch is the only moving light (a 3-frame flicker loop)."""
import numpy as np
from raster import Camera, aabb, quad_face, mat, Face

X0, X1 = -3.0, 8.0            # the visible slab extends beyond the corridor so cameras never see the void behind the action
END_X = 7.0
BOARD = dict(x=END_X - 0.02, y=0.78, z=0.0, w=0.42, h=0.48, d=0.04)
TORCH = np.array([2.0, 1.6, -1.45])
CRATE = dict(c=(6.2, 0.08, -1.0), size=0.16)
WALLS = {   # AABBs (min, max) used by the camera asserts
    'floor':    ((X0, -0.3, -1.55), (X1, 0.0, 4.0)),
    'back wall': ((X0, 0.0, -1.55), (X1, 3.0, -1.5)),
    'end wall': ((END_X, 0.0, -1.5), (END_X + 0.05, 3.0, 1.5)),
    'ceiling':  ((X0, 3.0, -1.55), (X1, 3.05, 1.5)),
}

CAMERAS = {
    'A': Camera((-1.2, 0.90, 1.90), (3.5, 0.70, 0.00), 50, 'A'),
    'B': Camera((1.5, 1.05, 3.20), (6.0, 0.60, 0.00), 55, 'B'),
    'C': Camera((5.2, 0.55, 1.60), (6.4, 0.30, 0.00), 45, 'C'),
    'D': Camera((5.6, 0.85, 2.40), (2.5, 0.55, 0.00), 55, 'D'),
    'E': Camera((5.0, 0.18, 1.30), (6.2, 0.15, -1.00), 50, 'E'),
}

def _jitter_rng(): return np.random.default_rng(7)           # seeded once: the per-block colour variation is the same on every run

def _vary(hexcol, d):
    b = np.array([int(hexcol[1:3], 16), int(hexcol[3:5], 16), int(hexcol[5:7], 16)]) + d
    return '#%02X%02X%02X' % tuple(int(np.clip(v, 0, 255)) for v in b)

def _flat(p, hexcol, up, glow=False):
    return quad_face(p, mat(hexcol), glow=glow, up=up)

def near_torch(c, r=1.1): return float(np.linalg.norm(np.asarray(c) - TORCH)) < r

def build_world():
    """returns the list of static faces (the torch flame is emissive and flickers inside the renderer)"""
    rng = _jitter_rng(); F = []
    # floor slab + grout lines
    F += aabb(((X0 + X1) / 2, -0.15, (-1.5 + 4.0) / 2), (X1 - X0, 0.3, 5.5), mat('#4A4A52'))
    for x in np.arange(X0, X1 + 0.01, 0.5):                                   # grout along z
        F.append(_flat([(x - 0.01, 0.002, -1.5), (x + 0.01, 0.002, -1.5), (x + 0.01, 0.002, 4.0), (x - 0.01, 0.002, 4.0)], '#3C3C44', (0, 1, 0), glow=near_torch((x, 0, -1.4), 1.6)))
    for z in np.arange(-1.5, 4.01, 0.5):                                      # grout along x
        F.append(_flat([(X0, 0.002, z - 0.01), (X1, 0.002, z - 0.01), (X1, 0.002, z + 0.01), (X0, 0.002, z + 0.01)], '#3C3C44', (0, 1, 0)))
    # back wall (faces +z) with stone blocks
    F += aabb(((X0 + X1) / 2, 1.5, -1.525), (X1 - X0, 3.0, 0.05), mat('#5A5A66'))
    bw, bh = 0.5, 0.3
    for iy in range(10):
        off = 0.25 if iy % 2 else 0.0
        for x in np.arange(X0 - 0.5 + off, X1, bw):
            d = int(rng.integers(-7, 8)); c = (x + bw / 2, (iy + 0.5) * bh)
            F.append(_flat([(x + 0.01, iy * bh + 0.01, -1.499), (x + bw - 0.01, iy * bh + 0.01, -1.499), (x + bw - 0.01, (iy + 1) * bh - 0.01, -1.499), (x + 0.01, (iy + 1) * bh - 0.01, -1.499)],
                           _vary('#5A5A66', d), (0, 0, 1), glow=near_torch((c[0], c[1], -1.5), 1.2)))
    # end wall (faces -x) with stone blocks
    F += aabb((END_X + 0.025, 1.5, 0.0), (0.05, 3.0, 3.0), mat('#5A5A66'))
    for iy in range(10):
        off = 0.25 if iy % 2 else 0.0
        for z in np.arange(-1.5 - 0.5 + off, 1.5, bw):
            d = int(rng.integers(-7, 8)); z0, z1 = max(z, -1.5), min(z + bw, 1.5)
            if z1 - z0 < 0.04: continue
            F.append(_flat([(END_X - 0.001, iy * bh + 0.01, z0 + 0.01), (END_X - 0.001, iy * bh + 0.01, z1 - 0.01), (END_X - 0.001, (iy + 1) * bh - 0.01, z1 - 0.01), (END_X - 0.001, (iy + 1) * bh - 0.01, z0 + 0.01)],
                           _vary('#5A5A66', d), (-1, 0, 0)))
    # ceiling
    F += aabb(((X0 + X1) / 2, 3.025, 0.0), (X1 - X0, 0.05, 3.0), mat('#3A3A44'))
    # the crate (the only prop) at (6.2, 0.08, -1.0), 0.16 cube
    F += aabb(CRATE['c'], (CRATE['size'],) * 3, mat('#6B5638'))
    # target board on the end wall, facing -x: board, two painted rings, bullseye (nested rectangles: boxes and quads only)
    b = BOARD; F += aabb((b['x'], b['y'], b['z']), (b['d'], b['h'], b['w']), mat('#C9B27E'))
    fx = b['x'] - b['d'] / 2 - 0.001
    def rect(hw, hh, hexcol, k):
        return _flat([(fx - 0.0004 * k, b['y'] - hh, b['z'] - hw), (fx - 0.0004 * k, b['y'] - hh, b['z'] + hw), (fx - 0.0004 * k, b['y'] + hh, b['z'] + hw), (fx - 0.0004 * k, b['y'] + hh, b['z'] - hw)], hexcol, (-1, 0, 0))
    F += [rect(0.18, 0.20, '#B08A55', 1), rect(0.15, 0.17, '#C9B27E', 2), rect(0.12, 0.14, '#B08A55', 3), rect(0.09, 0.11, '#C9B27E', 4), rect(0.05, 0.06, '#B33A3A', 5)]
    # wall torch on the back wall: bracket + emissive flame (the only moving light, 3-frame brightness loop)
    F += aabb((TORCH[0], 1.52, -1.47), (0.04, 0.10, 0.05), mat('#3A2E24'))
    F += aabb((TORCH[0], 1.62, -1.455), (0.06, 0.10, 0.04), mat('#F2A03A'), emissive=True)
    return F

# ----------------------------------------------------------------------------- camera asserts
def _inside(p, box, eps=1e-6): return all(box[0][i] - eps <= p[i] <= box[1][i] + eps for i in range(3))
def _seg_hits_box(a, b, box):
    """slab test: does the segment a->b intersect the AABB?"""
    a = np.asarray(a, float); d = np.asarray(b, float) - a; t0, t1 = 0.0, 1.0
    for i in range(3):
        if abs(d[i]) < 1e-12:
            if a[i] < box[0][i] or a[i] > box[1][i]: return False
        else:
            ta, tb = (box[0][i] - a[i]) / d[i], (box[1][i] - a[i]) / d[i]
            if ta > tb: ta, tb = tb, ta
            t0, t1 = max(t0, ta), min(t1, tb)
            if t0 > t1: return False
    return True

def check_cameras():
    """returns a list of (camera, rule, ok, detail): not inside any wall AABB, and a clear line of sight to its target point"""
    out = []
    for k, cam in CAMERAS.items():
        inside = [n for n, b in WALLS.items() if _inside(cam.pos, b)]
        out.append((k, 'camera is not inside any wall', not inside, ', '.join(inside) or 'ok'))
        hit = [n for n, b in WALLS.items() if _seg_hits_box(cam.pos, cam.target - 0.02 * (cam.target - cam.pos) / np.linalg.norm(cam.target - cam.pos), b)]
        out.append((k, 'clear line of sight to the target', not hit, ', '.join(hit) or 'ok'))
    return out
