"""Step 1: the software rasterizer and the PS1 post chain. numpy + Pillow only.

Internal resolution 180x320, EXACTLY. No anti-aliasing: every pixel is the flat colour of the nearest face.
Shading is three discrete tones per material (base / darker side / darkest underside) chosen from the face normal.
Post chain (on the 180x320 layer, before the x6 nearest-neighbour upscale): ordered 4x4 Bayer dither + 5-bit quantize,
per-frame grain, 1 % row jitter, 1 px chromatic offset, vignette (max 18 %). Everything is seeded by the frame number.
"""
import math
import numpy as np

W, H, SCALE = 180, 320, 6
FOV_V = 50.0
NEAR = 0.05
BG = (26, 26, 34)

def rgb(h):
    h = h.lstrip('#'); return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

class Mat:
    """three tones per material: base, darker side, darkest underside"""
    def __init__(self, hexcol):
        b = np.array(rgb(hexcol), float)
        self.tones = (tuple(b), tuple(np.round(b * 0.72)), tuple(np.round(b * 0.5)))
        self.hex = hexcol

_MATS = {}
def mat(hexcol):
    if hexcol not in _MATS: _MATS[hexcol] = Mat(hexcol)
    return _MATS[hexcol]

class Face:
    """one flat convex quad with an outward normal. emissive faces ignore shading and flicker; glow faces get the torch tone step"""
    __slots__ = ('p', 'n', 'm', 'emissive', 'glow', 'tone')
    def __init__(self, p, n, m, emissive=False, glow=False, tone=None):
        self.p = np.asarray(p, float); self.n = np.asarray(n, float); self.m = m; self.emissive = emissive; self.glow = glow; self.tone = tone

LIGHT = np.array([-0.35, 0.0, 0.94]); LIGHT /= np.linalg.norm(LIGHT)

def tone_index(n):
    """the face normal decides the tone: tops are base, undersides darkest, vertical faces base when they face the light side"""
    if n[1] > 0.5: return 0
    if n[1] < -0.5: return 2
    return 0 if float(n @ LIGHT) >= 0 else 1

# ----------------------------------------------------------------------------- primitives
def oriented_box(center, axes, half, m, emissive=False, glow=False):
    """axes: 3x3 matrix whose COLUMNS are the unit box axes (world); half: half-extents along them"""
    c = np.asarray(center, float); A = np.asarray(axes, float); h = np.asarray(half, float); out = []
    for i in range(3):
        j, k = (i + 1) % 3, (i + 2) % 3
        for s in (1, -1):
            n = s * A[:, i]; o = c + n * h[i]; u = A[:, j] * h[j]; v = A[:, k] * h[k]
            out.append(Face([o + u + v, o - u + v, o - u - v, o + u - v], n, m, emissive, glow))
    return out

def aabb(center, size, m, emissive=False, glow=False):
    return oriented_box(center, np.eye(3), np.asarray(size, float) / 2, m, emissive, glow)

def limb_box(p0, p1, thick, m, thick2=None):
    """a box running from p0 to p1 with a square (or thick x thick2) section"""
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float); d = p1 - p0; L = float(np.linalg.norm(d))
    if L < 1e-9: return []
    u = d / L; ref = np.array([0, 1.0, 0]) if abs(u[1]) < 0.9 else np.array([1.0, 0, 0])
    v = np.cross(ref, u); v /= np.linalg.norm(v); w = np.cross(u, v)
    return oriented_box((p0 + p1) / 2, np.stack([u, v, w], 1), (L / 2, thick / 2, (thick2 or thick) / 2), m)

def quad_face(p, m, emissive=False, glow=False, up=None):
    """a single flat quad (decals). its normal is the plane normal, oriented toward `up` when given"""
    p = np.asarray(p, float); n = np.cross(p[1] - p[0], p[3] - p[0]); n /= np.linalg.norm(n) + 1e-12
    if up is not None and float(n @ np.asarray(up, float)) < 0: n = -n
    return Face(p, n, m, emissive, glow)

def rot_y(a):
    c, s = math.cos(a), math.sin(a); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
def rot_x(a):
    c, s = math.cos(a), math.sin(a); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
def rot_z(a):
    c, s = math.cos(a), math.sin(a); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

def transform_faces(faces, R, t):
    R = np.asarray(R, float); t = np.asarray(t, float)
    return [Face(f.p @ R.T + t, R @ f.n, f.m, f.emissive, f.glow, f.tone) for f in faces]

def squash_faces(faces, k, y0=0.0):
    """non-uniform vertical squash about y0 (the goblin duck). normals are recomputed from the squashed points"""
    out = []
    for f in faces:
        p = f.p.copy(); p[:, 1] = y0 + (p[:, 1] - y0) * k
        n = np.cross(p[1] - p[0], p[3] - p[0]); ln = np.linalg.norm(n)
        n = f.n if ln < 1e-12 else n / ln
        if float(n @ f.n) < 0: n = -n
        out.append(Face(p, n, f.m, f.emissive, f.glow, f.tone))
    return out

# ----------------------------------------------------------------------------- camera
class Camera:
    def __init__(self, pos, target, fov=FOV_V, name=''):
        self.pos = np.asarray(pos, float); self.target = np.asarray(target, float); self.fov = fov; self.name = name
        f = self.target - self.pos; f /= np.linalg.norm(f); r = np.cross(f, [0, 1.0, 0]); r /= np.linalg.norm(r); u = np.cross(r, f)
        self.f, self.r, self.u = f, r, u; self.fpx = (H / 2) / math.tan(math.radians(fov) / 2)
    def to_cam(self, pts):
        d = np.asarray(pts, float) - self.pos; return np.stack([d @ self.r, d @ self.u, d @ self.f], -1)
    def project(self, p):
        c = self.to_cam(np.asarray(p, float)[None, :])[0]
        if c[2] < NEAR: return None
        return (W / 2 + self.fpx * c[0] / c[2], H / 2 - self.fpx * c[1] / c[2], c[2])

# ----------------------------------------------------------------------------- rasterizer
def _tri(img, zb, a, b, c, za, zb_, zc, col):
    minx = max(0, int(math.floor(min(a[0], b[0], c[0])))); maxx = min(W - 1, int(math.ceil(max(a[0], b[0], c[0]))))
    miny = max(0, int(math.floor(min(a[1], b[1], c[1])))); maxy = min(H - 1, int(math.ceil(max(a[1], b[1], c[1]))))
    if minx > maxx or miny > maxy: return
    den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
    if abs(den) < 1e-9: return
    X, Y = np.meshgrid(np.arange(minx, maxx + 1) + 0.5, np.arange(miny, maxy + 1) + 0.5)
    l1 = ((b[1] - c[1]) * (X - c[0]) + (c[0] - b[0]) * (Y - c[1])) / den
    l2 = ((c[1] - a[1]) * (X - c[0]) + (a[0] - c[0]) * (Y - c[1])) / den
    l3 = 1 - l1 - l2
    inside = (l1 >= -1e-7) & (l2 >= -1e-7) & (l3 >= -1e-7)
    if not inside.any(): return
    d = l1 * za + l2 * zb_ + l3 * zc
    sub = zb[miny:maxy + 1, minx:maxx + 1]; m = inside & (d > sub)
    if not m.any(): return
    sub[m] = d[m]; img[miny:maxy + 1, minx:maxx + 1][m] = col

TORCH_FLICKER = (1.00, 0.82, 0.92)     # emissive brightness, 3-frame loop
TORCH_GLOW = (1.10, 1.00, 1.05)        # tone step of faces next to the torch, same loop

def render(faces, cam, frame=0, bg=BG, cull=True):
    """returns the raw 180x320x3 uint8 image (flat colours, z-buffered, back-face culled)"""
    img = np.empty((H, W, 3), np.uint8); img[:] = bg; zb = np.zeros((H, W))
    cp = cam.pos; fl = TORCH_FLICKER[frame % 3]; gl = TORCH_GLOW[frame % 3]
    for f in faces:
        if cull and float(f.n @ (f.p[0] - cp)) >= 0: continue
        if f.emissive: col = tuple(min(255, int(round(v * fl))) for v in f.m.tones[0])
        else:
            col = f.m.tones[tone_index(f.n) if f.tone is None else f.tone]
            if f.glow: col = tuple(min(255, int(round(v * gl))) for v in col)
            else: col = tuple(int(v) for v in col)
        c = cam.to_cam(f.p)
        poly = []; n = len(c)                                  # clip against the near plane
        for i in range(n):
            a = c[i]; b = c[(i + 1) % n]; ina = a[2] > NEAR; inb = b[2] > NEAR
            if ina: poly.append(a)
            if ina != inb:
                u = (NEAR - a[2]) / (b[2] - a[2]); poly.append(a + (b - a) * u)
        if len(poly) < 3: continue
        P = [(W / 2 + cam.fpx * q[0] / q[2], H / 2 - cam.fpx * q[1] / q[2]) for q in poly]; Z = [1.0 / q[2] for q in poly]
        if max(p[0] for p in P) < 0 or min(p[0] for p in P) > W or max(p[1] for p in P) < 0 or min(p[1] for p in P) > H: continue
        for i in range(1, len(P) - 1): _tri(img, zb, P[0], P[i], P[i + 1], Z[0], Z[i], Z[i + 1], col)
    return img

# ----------------------------------------------------------------------------- PS1 post chain
BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], float) / 16.0
_BAY = np.tile(BAYER4, (H // 4 + 1, W // 4 + 1))[:H, :W, None]
_yy, _xx = np.mgrid[0:H, 0:W]
_r = np.sqrt(((_xx + 0.5 - W / 2) / (W / 2)) ** 2 + ((_yy + 0.5 - H / 2) / (H / 2)) ** 2); _r = _r / _r.max()
VIGNETTE = (1.0 - 0.18 * _r ** 2)[..., None]          # 18 % darker at the extreme corners

def post(img, frame):
    """1+2 quantize to 5 bits with the ordered 4x4 Bayer threshold, 3 grain, 4 row jitter, 5 chromatic offset, 6 vignette"""
    a = img.astype(np.float32)
    q = np.clip(np.floor(a / 8.0 + _BAY), 0, 31)                                   # 5-bit levels (8 steps of 8-bit)
    a = ((q.astype(np.int32) << 3) | (q.astype(np.int32) >> 2)).astype(np.float32)
    rng = np.random.default_rng(10_000 + frame)
    a = a + rng.integers(-4, 5, size=(H, W, 1)).astype(np.float32)               # per-frame VHS grain, amplitude 4 levels
    rows = np.random.default_rng(20_000 + frame).random(H) < 0.01
    for y in np.nonzero(rows)[0]: a[y] = np.roll(a[y], 1 if (y + frame) % 2 else -1, axis=0)     # 1 px horizontal jitter
    a[:, :, 0] = np.roll(a[:, :, 0], 1, axis=1); a[:, :, 2] = np.roll(a[:, :, 2], -1, axis=1)   # chromatic offset: R +1 px, B -1 px
    a = a * VIGNETTE
    return np.clip(a, 0, 255).astype(np.uint8)

def upscale(img):
    """nearest-neighbour integer x6 -> 1080x1920"""
    return np.repeat(np.repeat(img, SCALE, axis=0), SCALE, axis=1)
