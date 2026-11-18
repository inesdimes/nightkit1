"""Frame composition: world + characters + arrows -> 180x320 render -> UI (popups, subtitles) -> PS1 post chain.
The UI is drawn on the 180x320 layer BEFORE the post chain, so it is quantized, dithered and upscaled with everything else."""
import numpy as np
from PIL import Image
import raster as R, font as FNT, world as WORLD, characters as CH, timeline as T

_WORLD = None
def world_faces():
    global _WORLD
    if _WORLD is None: _WORLD = WORLD.build_world()
    return _WORLD

FILL = (242, 242, 234); OUTLINE = (34, 34, 42); HILITE = (242, 160, 58)

def camera_for(cut, f):
    k, a, b = T.cam_at(cut, f); cam = WORLD.CAMERAS[k]
    if k == 'A':                                              # the one permitted exception: a 2 % slow push-in over the whole shot
        u = (f - a) / max(1, (b - a)); pos = cam.pos + (cam.target - cam.pos) * 0.02 * u; return R.Camera(pos, cam.target, cam.fov, 'A')
    return cam

def scene_faces(cut, f):
    F = list(world_faces())
    ast = T.archer_state(cut, f); gst = T.goblin_state(cut, f)
    F += CH.make_archer(ast) + CH.make_goblin(gst)
    for tail, d in T.flying_arrows(cut, f) + T.floor_arrows(cut, f): F += CH.make_arrow(tail, d)
    cs = T.crate_state(cut, f)
    if cs: F += CH.make_arrow_crate(cs[0], cs[1], 3)
    return F, ast, gst

# ----------------------------------------------------------------------------- popup + subtitles
def draw_popup(img, anchor, scale, alpha):
    m = FNT.text_mask('MISS', 3); h, w = m.shape
    if abs(scale - 1.0) > 1e-6:
        m = np.array(Image.fromarray(m.astype(np.uint8) * 255).resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.NEAREST)) > 127; h, w = m.shape
    pad = 2; big = np.zeros((h + 2 * pad, w + 2 * pad), bool); big[pad:pad + h, pad:pad + w] = m; ol = FNT._dilate(big, pad) & ~big
    x0 = int(round(anchor[0] - big.shape[1] / 2)); y0 = int(round(anchor[1] - big.shape[0] / 2))
    for mask, col in ((ol, OUTLINE), (big, FILL)):
        ys, xs = np.nonzero(mask); ys += y0; xs += x0; ok = (ys >= 0) & (ys < R.H) & (xs >= 0) & (xs < R.W); ys, xs = ys[ok], xs[ok]
        img[ys, xs] = (img[ys, xs].astype(np.float32) * (1 - alpha) + np.array(col, np.float32) * alpha).astype(np.uint8)

ANCHOR = dict(board=(0.62 * R.W, 0.42 * R.H), wall=(0.44 * R.W, 0.44 * R.H), tr=(0.70 * R.W, 0.10 * R.H))

MAXW = R.W - 8
def sub_layout(text, hl):
    """word-wrapped runs (max two lines). returns list of lines, each a list of (text, colour) runs"""
    words = []
    for w in text.split(' '):
        key = ''.join(ch for ch in w if ch.isalnum()).lower(); words.append((w, HILITE if key in hl else FILL))
    return FNT.wrap(words, MAXW, 1)

def sub_rect(lines, lift=0):
    n = len(lines); h = 8 + 9 * (n - 1); w = max(sum(FNT.text_width(t) for t, _ in FNT.line_runs(l)) + FNT.text_width(' ') * 0 for l in lines)
    w = max(FNT.text_width(''.join(t for t, _ in FNT.line_runs(l))) for l in lines)
    y0 = R.H - 4 - 1 - h - lift; x0 = None; return y0, h, w

def collisions(cut, f, cam, gst, rect):
    """does the subtitle rectangle (x0,y0,x1,y1) cover the goblin's face or the bullseye? the head is approximated by its projected box"""
    gx, gz = gst['pos']; hits = []
    c = cam.project((gx, 0.40 * gst.get('squash', 1.0) if gst.get('squash') else 0.40, gz))
    if c:
        r = 0.11 * cam.fpx / c[2]; box = (c[0] - r, c[1] - r, c[0] + r, c[1] + r)
        if not (rect[2] < box[0] or rect[0] > box[2] or rect[3] < box[1] or rect[1] > box[3]): hits.append('goblin face')
    b = cam.project((6.98, 0.78, 0.0))
    if b and rect[0] <= b[0] <= rect[2] and rect[1] <= b[1] <= rect[3]: hits.append('bullseye')
    return hits

def subtitle_placement(cut, f, cam, gst):
    """returns (lines, y0, x0, lift) or None. lifts the block by 4 px steps until nothing collides"""
    s = T.sub_at(cut, f)
    if not s: return None
    lines = sub_layout(*s); lift = 0
    for _ in range(12):
        y0, h, w = sub_rect(lines, lift); x0 = (R.W - w) // 2; rect = (x0 - 1, y0 - 1, x0 + w + 1, y0 + h + 1)
        if not collisions(cut, f, cam, gst, rect): break
        lift += 4
    return lines, y0, x0, lift, (x0 - 1, y0 - 1, x0 + w + 1, y0 + h + 1)

def draw_subtitle(img, place):
    lines, y0, x0, lift, _ = place
    for i, line in enumerate(lines):
        w = FNT.text_width(''.join(t for t, _ in FNT.line_runs(line))); FNT.draw_runs(img, x0 + (max(FNT.text_width(''.join(t for t, _ in FNT.line_runs(l))) for l in lines) - w) // 2, y0 + 9 * i, FNT.line_runs(line), 1, OUTLINE, 1)

# ----------------------------------------------------------------------------- the frame
def frame180(cut, f):
    """the finished 180x320 frame (render + UI + PS1 post chain) plus the metadata the QA needs"""
    faces, ast, gst = scene_faces(cut, f); cam = camera_for(cut, f)
    img = R.render(faces, cam, f)
    for kind, sc, al in T.popup_at(cut, f): draw_popup(img, ANCHOR[kind], sc, al)
    place = subtitle_placement(cut, f, cam, gst)
    if place: draw_subtitle(img, place)
    return R.post(img, f), dict(cam=cam, archer=ast, goblin=gst, sub=place)
