"""THE LAST RESPAWN - nightkit version (Enes, 23 Nov 2026: "the same film with nightkit, same camera angles, same everything,
only the graphics are ours").

Same film as blender/last_respawn.py, frame for frame: the Blender script exports, per frame, the camera, every puppet part's
world matrix and the lights (MODE=export -> renders/last_respawn/nk/scene_0001_1392.npz + _meshes.json + _lights.json).
This script draws that with OUR renderer: nightkit's z-buffered flat-shaded rasterizer (zraster), Format 3.0 look
(270x480 internal, depth outline, PS1 dither, x4 upscale), our block-font subtitles and HUD. Same mastered sound
(renders/last_respawn/audio/final.wav, built by `python blender/last_respawn.py audio`).

Run (repo root):
  "<blender>" -b --factory-startup --python blender/last_respawn.py   with MODE=export FRAMES=1-1392   (once, after any Blender change)
  TEST=2,16.5,30 python examples/last_respawn_nk.py        -> test.png
  python tools/render_parts.py examples/last_respawn_nk.py --prefix lrn --audio last_respawn_final.wav \
      --out ../renders/last_respawn/last_respawn_nightkit.mp4 --parts 8
Voices are PLACEHOLDERS (Kokoro) until Enes's takes exist."""
import os, sys, json, math, shutil
import numpy as np
from PIL import Image, ImageDraw
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'blender'))
os.environ.setdefault('MODE', 'audio')
from nightkit.engine import Renderer, Camera
from nightkit.zraster import zrender
from nightkit.look import outline, Subtitles, text_cells, draw_cells
from nightkit import post
import last_respawn as LR

FPS = 24
N = LR.NF                                      # 1392 frames = 58.0 s
W, H, S = 270, 480, 4
FOV = math.degrees(2 * math.atan(18 / 35 * 9 / 16))     # the Blender camera: 35 mm, 36 mm sensor fitted to the height
OUT = os.path.join(ROOT, 'out')
SRC = os.path.join(os.path.dirname(ROOT), 'renders', 'last_respawn')
NK = os.path.join(SRC, 'nk', 'scene_0001_1392')

# ------------------------------------------------------------------ scene data (exported from Blender)
D = np.load(NK + '.npz')
MESH = json.load(open(NK + '_meshes.json'))
LIGHTS = json.load(open(NK + '_lights.json'))
MIX, VIS, CAMP, FWD, WASH = D['mesh_ix'], D['vis'], D['cam'], D['fwd'], D['wash']
MAT = D['M']
NAMES = [str(n) for n in D['names']]


def to_nk(p):
    """Blender (x, y, z up) -> nightkit (x, y up, z): same handedness (x right, up, forward)."""
    p = np.asarray(p, float)
    return p[..., [0, 2, 1]]


def srgb(c):
    return tuple(int(255 * min(1.0, max(0.0, x)) ** (1 / 2.2)) for x in c)


def _closed(P):
    edges = {}
    for idx, _, _ in P:
        for i in range(len(idx)):
            e = tuple(sorted((idx[i], idx[(i + 1) % len(idx)])))
            edges[e] = edges.get(e, 0) + 1
    return all(v == 2 for v in edges.values())


# per mesh: vertices, polygons grouped by size (3 or 4) for vectorised transforms, colours, emissive flags
class MeshNK:
    def __init__(self, m, k):
        self.V = np.array(m['V'], float)
        self.closed = _closed(m['P'])
        self.faces, self.cols, self.emit = [], [], []
        for j, (idx, c, c2) in enumerate(m['P']):
            # our palette treatment: the two-tone materials (bronze/verdigris, stone) alternate per face, not per pixel
            h = (j * 2654435761 + k * 97) % 1000 / 1000.0
            base = c2 if (c[3] < 0.5 and c2 != c[:3] and h < 0.28) else c[:3]
            col = srgb(base)
            if c[3] < 0.5 and c[4] > 0.5:                 # metals read darker without reflections: lift them a little
                col = tuple(min(255, int(v * 1.15 + 10)) for v in col)
            self.faces.append(idx)
            self.cols.append(col)
            self.emit.append(c[3] > 0.5)


MESHES = [MeshNK(m, k) for k, m in enumerate(MESH)]
SKIP = ('fog', 'mist', 'wash', 'ch_mist', 'sky')


def frame_index(t):
    return min(N - 1, max(0, int(round(t * FPS))))


def world_faces(fi, cam):
    """all visible faces of frame fi as zraster dicts (nightkit axes), crudely frustum-culled."""
    cp = np.array(cam[:3])
    yaw, pitch = cam[3], cam[4]
    fwd = np.array([math.sin(yaw) * math.cos(pitch), math.sin(pitch), math.cos(yaw) * math.cos(pitch)])
    cosv = math.cos(math.radians(FOV / 2 * 16 / 9 * 1.15))     # a cone slightly wider than the (taller) vertical FOV
    out = []
    for oi in np.nonzero(VIS[fi])[0]:
        if any(s in NAMES[oi] for s in SKIP):
            continue
        me = MESHES[MIX[oi]]
        M = MAT[fi, oi]
        Pw = to_nk(me.V @ M[:3, :3].T + M[:3, 3])
        rel = Pw - cp
        dist = np.linalg.norm(rel, axis=1)
        inside = (rel @ fwd) > -0.3
        if not inside.any():
            continue
        ang_ok = (rel @ fwd) / np.maximum(dist, 1e-6) > cosv
        near = dist < 2.5
        if not (ang_ok | near).any() and np.linalg.norm(Pw.mean(0) - cp) > 3.0:
            # the object's vertices are all outside the view cone; keep big objects whose span may still cross the view
            if np.ptp(Pw, axis=0).max() < 6.0:
                continue
        if dist.min() > 60:
            continue
        for idx, col, em in zip(me.faces, me.cols, me.emit):
            p = Pw[idx]
            n = np.cross(p[1] - p[0], p[2] - p[0])
            nn = np.linalg.norm(n)
            if nn < 1e-12:
                continue
            n = -n / nn                                   # the axis swap flips the winding: Blender normals point out
            c = p.mean(0)
            q = dict(p=[tuple(v) for v in p], col=col, emit=em, n=n, c=c, nobias=True)   # real geometry: no decal bias
            if me.closed:
                q['wind'] = 1.0
            out.append(q)
    return out


def scene_lights(fi):
    L = []
    cp = CAMP[fi]
    lamps = []
    for pos, col, energy, kind, _ in LIGHTS[fi]:
        p = to_nk(pos)
        li = math.sqrt(energy) * 0.055
        c = tuple(int(255 * min(1, x)) for x in col)
        if kind == 'AREA' or energy > 400:
            L.append((tuple(p), c, li * (1.25 if kind == 'AREA' else 1.0)))
        else:
            d = float(np.linalg.norm(np.asarray(pos) - cp))
            w = 1 - LR.ss(7.0, 12.0, d)                   # lamps fade in/out with distance: no light pops between frames
            if w > 0:
                lamps.append((tuple(p), c, li * w))
    return L + lamps


def in_chamber(t):
    return LR.T_WIPE <= t < 52.0


RND = Renderer(W, H, fog=(18, 26, 40))
CYAN = np.array([140, 242, 255], np.float32)


def render_low(t):
    fi = frame_index(t)
    pos = to_nk(CAMP[fi])
    tgt = pos + to_nk(FWD[fi])
    cam = Camera.look(tuple(pos), tuple(tgt))
    ch = in_chamber(t)
    RND.fog = (34, 26, 24) if ch else (18, 26, 40)
    faces = world_faces(fi, cam)
    img, vi, zb = zrender(RND, cam, [faces], scene_lights(fi), fov=FOV, fog_start=6 if ch else 7,
                          fog_end=26 if ch else 34, ambient=0.30 if ch else 0.26, return_z=True)
    a = np.asarray(img).astype(np.float32)
    a = outline(a, zb)
    a = np.clip((a - 118) * 1.08 + 118, 0, 255)
    w = float(WASH[fi])
    if w > 0:
        a = a * (1 - 0.92 * w) + CYAN * 0.92 * w
    return Image.fromarray(a.astype(np.uint8)), vi


SCR = json.load(open(os.path.join(ROOT, 'tts', 'lrs', 'script.json')))
SUBS = Subtitles(SCR, [(k, t0) for k, t0 in LR.LINES.items()], W, H, S,
                 {'G': (170, 240, 120), 'K': (130, 228, 255), 'B': (255, 196, 120)}, title_key='-none-', n=20)
AMB = (255, 176, 60)
RED = (255, 70, 60)
CYT = (130, 238, 255)


def overlays(arr, t):
    u = LR.loop_u(t)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    if u is not None and u >= 0 and 3.0 <= u < 7.9:
        zero = u >= LR.T_SNAP
        pop = 1 + 0.6 * LR.bump(LR.T_SNAP, LR.T_SNAP + 0.04, LR.T_SNAP + 0.1, LR.T_SNAP + 0.3, u)
        jit = int(10 * math.sin(u * 90) * LR.bump(LR.T_SNAP, LR.T_SNAP + 0.02, LR.T_SNAP + 0.25, LR.T_SNAP + 0.4, u))
        draw_cells(d, text_cells('RESPAWNS LEFT', 300, 90, 5, AMB), 3)
        sc = int(round(10 * pop))
        draw_cells(d, text_cells('0' if zero else '1', 700 + jit, 72 - 4 * (sc - 10), sc, RED if zero else AMB), 4)
    if u is not None and -5.4 <= u < -3.4:
        sc = 6 if u > -5.2 else 7
        txt = 'RESPAWNS RESTORED'
        draw_cells(d, text_cells(txt, int(540 - len(txt) * 6 * sc / 2), 96, sc, CYT), 3)
    a = np.asarray(im).astype(np.float32)
    if t < LR.T_END - 0.15 or True:
        a = SUBS.apply(a, t)
    return a


def frame_final(t):
    img, vi = render_low(t)
    img = post.ps1(img, levels=6)
    return overlays(post.upscale(img, S), t)


TEST = os.environ.get('TEST')
if TEST and __name__ == '__main__':
    ts = [float(x) for x in TEST.split(',')]
    ims = [Image.fromarray(np.clip(frame_final(x), 0, 255).astype(np.uint8)).resize((360, 640), Image.LANCZOS) for x in ts]
    sheet = Image.new('RGB', (360 * len(ims), 640))
    for i, im in enumerate(ims):
        sheet.paste(im, (360 * i, 0))
    sheet.save(os.environ.get('TESTOUT', os.path.join(ROOT, 'test.png')))
    print('test written')
    sys.exit()
if __name__ == '__main__' and os.environ.get('PART') == 'audio':
    os.makedirs(OUT, exist_ok=True)
    shutil.copy(os.path.join(SRC, 'audio', 'final.wav'), os.path.join(OUT, 'last_respawn_final.wav'))
    print('audio copied')
    sys.exit()
if __name__ == '__main__' and os.environ.get('PART'):
    import subprocess
    a, b = map(int, os.environ['PART'].split(':'))
    os.makedirs(OUT, exist_ok=True)
    p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W * S}x{H * S}',
                          '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p',
                          os.path.join(OUT, f'lrn_{a:05d}.mp4')], stdin=subprocess.PIPE)
    vhs = post.VHS(W * S, H * S, S, grade='none', chroma=0, scan_dark=1.0, vignette=0.22, grain=0.9, band_period=1e9)
    for f in range(a, min(b, N)):
        p.stdin.write(vhs(frame_final(f / FPS), f, f / FPS).tobytes())
    p.stdin.close()
    p.wait()
    print('part done', a, b)
    sys.exit()
