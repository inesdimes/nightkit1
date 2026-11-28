"""Review sheet for nightkit/body.py (phase 3). Not a video.
  python examples/body_sheet.py          # every gesture, 3/4 front, medium-full shot
  python examples/body_sheet.py clip     # an 8 s performance (Performer timeline) -> renders/body_sheet/clip
  python examples/body_sheet.py cloak    # old tube cloak vs soft cloak_hd, 3 angles x 5 poses -> cloak_sheet.png
  python examples/body_sheet.py cloakclip  # the 8 s performance seen from behind 3/4 -> renders/body_sheet/cloakclip
Output: C:/Users/USER/Documents/blender-shorts/renders/body_sheet/"""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera
from nightkit.zraster import zrender
from nightkit import hd, body, look, post
V = np.array
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'renders', 'body_sheet'); os.makedirs(OUT, exist_ok=True)
S = hd.spec(h=1.78, build=1.05, skin=(222, 176, 140), hair=(62, 44, 32), hair_style='messy', eye=(70, 110, 150), brow=(46, 32, 24),
            cloak=(60, 80, 140), cloak_len=0.9, cloak_hd=True)
S_OLD = dict(S, cloak_hd=None)
def ground():
    Q = []
    for i in range(-4, 4):
        for j in range(-4, 4):
            c = (196, 184, 160) if (i + j) % 2 else (186, 174, 150)
            q = hd.face([V((i * 0.6, 0, j * 0.6)), V((i * 0.6, 0, (j + 1) * 0.6)), V(((i + 1) * 0.6, 0, (j + 1) * 0.6)), V(((i + 1) * 0.6, 0, j * 0.6))], c)
            if q: Q.append(q)
    return Q
G = ground()
def render(Q, pos, tgt, W=270, H=480, fov=40):
    L = [(tuple(V(tgt) + V((-3.0, 5.0, 4.0))), (255, 240, 220), 7.0), (tuple(V(tgt) + V((3.5, 1.0, 2.5))), (170, 196, 236), 2.0)]
    R = Renderer(W, H, fog=(214, 222, 232))
    img, vi, zb = zrender(R, Camera.look(tuple(pos), tuple(tgt)), [Q, G], L, fov=fov, fog_start=30, fog_end=60, ambient=0.45, return_z=True)
    return Image.fromarray(np.clip(look.outline(np.asarray(img).astype(np.float32), zb), 0, 255).astype(np.uint8))
def label(im, txt):
    d = ImageDraw.Draw(im); d.rectangle((0, im.height - 18, im.width, im.height), fill=(20, 20, 24)); d.text((5, im.height - 15), txt, fill=(255, 230, 120)); return im
CAM = (V((0.9, 1.25, 2.9)), V((0.0, 1.05, 0.0)))
def sheet():
    names = list(body.GESTURES); cells = []
    for n in names:
        pf = body.Performer(S, [(0.0, n)], breath=False, sway=False); P = pf.at(1.0)
        cells.append(label(render(hd.human(S, P), *CAM), n))
    cols = 7; rows = (len(cells) + cols - 1) // cols; sh = Image.new('RGB', (cols * 274, rows * 484), (30, 30, 34))
    for i, c in enumerate(cells): sh.paste(c, ((i % cols) * 274, (i // cols) * 484))
    sh.save(os.path.join(OUT, 'body_sheet.png')); print('wrote body_sheet.png')
TIMELINE = [(0.0, 'idle'), (0.8, 'wave'), (2.2, 'shrug'), (3.4, 'arms_crossed'), (4.6, 'facepalm'), (5.6, 'think'), (6.8, 'cheer')]
def clip():
    pf = body.Performer(S, TIMELINE); d = os.path.join(OUT, 'clip'); os.makedirs(d, exist_ok=True)
    for f in range(int(8.0 * 24)):
        t = f / 24; P = pf.at(t)
        render(hd.human(S, P), *CAM).resize((1080, 1920), Image.NEAREST).save(os.path.join(d, f'f_{f + 1:04d}.png'))
    print('wrote clip frames')
CAMS = {'front': (V((0.9, 1.25, 2.9)), V((0.0, 1.0, 0.0))), 'side': (V((3.0, 1.2, -0.3)), V((0.0, 1.0, 0.0))), 'back': (V((-1.3, 1.35, -2.7)), V((0.0, 1.0, 0.0)))}
def cloak():
    rows = []
    for g in ('idle', 'cheer', 'bow', 'slump', 'kneel'):
        row = Image.new('RGB', (6 * 274, 484), (30, 30, 34))
        for a, (tag, SS) in enumerate((('old', S_OLD), ('hd', S))):
            pf = body.Performer(SS, [(0.0, g)], breath=False, sway=False); P = pf.at(1.5)
            for b, cn in enumerate(('front', 'side', 'back')):
                row.paste(label(render(hd.human(SS, dict(P)), *CAMS[cn]), f'{g} {tag} {cn}'), ((a * 3 + b) * 274, 0))
        rows.append(row)
    sh = Image.new('RGB', (6 * 274, len(rows) * 484)); [sh.paste(r, (0, i * 484)) for i, r in enumerate(rows)]
    sh.save(os.path.join(OUT, 'cloak_sheet.png')); print('wrote cloak_sheet.png')
def cloakclip():
    pf = body.Performer(S, TIMELINE); d = os.path.join(OUT, 'cloakclip'); os.makedirs(d, exist_ok=True)
    cam = (V((-1.6, 1.3, -2.4)), V((0.0, 1.0, 0.0)))
    for f in range(int(8.0 * 24)):
        t = f / 24; P = pf.at(t)
        render(hd.human(S, P), *cam).resize((1080, 1920), Image.NEAREST).save(os.path.join(d, f'f_{f + 1:04d}.png'))
    print('wrote cloakclip frames')
# the whole system in one take: face presets + every anime mark (FX), fingers, body acting, soft cloak; full shots for the body,
# medium close-ups where the face carries the beat (faces only read that close at phone size). Ends on idle -> loops.
SHOW = [(0.0, 'idle'), (0.5, 'wave'), (2.0, 'scratch_head'), (3.4, 'shocked'), (4.6, 'fist_pump', dict(face='angry')),
        (5.8, 'arms_crossed'), (7.0, 'think'), (8.2, 'proud'), (9.4, 'laugh'), (10.6, 'bow'), (11.8, 'idle')]
SHOW_DUR = 12.6
CLOSE = (V((0.38, 1.62, 0.95)), V((0.0, 1.52, 0.0)))
SHOW_CAMS = [(0.0, CAM), (2.0, CLOSE), (5.8, CAM), (8.2, CLOSE), (9.4, CAM)]       # cuts land on the gesture keys
def show():
    pf = body.Performer(S, SHOW); d = os.path.join(OUT, 'show'); os.makedirs(d, exist_ok=True)
    for f in range(int(SHOW_DUR * 24)):
        t = f / 24; P = pf.at(t); cam = [c for t0, c in SHOW_CAMS if t0 <= t][-1]
        render(hd.human(S, P), *cam).resize((1080, 1920), Image.NEAREST).save(os.path.join(d, f'f_{f + 1:04d}.png'))
    print('wrote show frames')
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'show': show(); sys.exit()
    {'sheet': sheet, 'clip': clip, 'cloak': cloak, 'cloakclip': cloakclip}[sys.argv[1] if len(sys.argv) > 1 else 'sheet']()
