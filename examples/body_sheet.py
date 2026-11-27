"""Review sheet for nightkit/body.py (phase 3). Not a video.
  python examples/body_sheet.py          # every gesture, 3/4 front, medium-full shot
  python examples/body_sheet.py clip     # an 8 s performance (Performer timeline) -> renders/body_sheet/clip
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
            cloak=(60, 80, 140), cloak_len=0.9)
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
        t = f / 24; P = pf.at(t); P['cape_sway'] = 0.0
        render(hd.human(S, P), *CAM).resize((1080, 1920), Image.NEAREST).save(os.path.join(d, f'f_{f + 1:04d}.png'))
    print('wrote clip frames')
if __name__ == '__main__':
    {'sheet': sheet, 'clip': clip}[sys.argv[1] if len(sys.argv) > 1 else 'sheet']()
