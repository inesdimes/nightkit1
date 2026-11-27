"""Review sheet for nightkit/hands.py (phase 2). Not a video.
  python examples/hand_sheet.py          # every preset, palm / side / back view (right hand)
  python examples/hand_sheet.py body     # presets on a figure in medium close-up at phone size
Output: C:/Users/USER/Documents/blender-shorts/renders/hand_sheet/"""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera
from nightkit.zraster import zrender
from nightkit import hd, hands, face, look
V = np.array
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'renders', 'hand_sheet'); os.makedirs(OUT, exist_ok=True)
SKIN = (222, 176, 140)
NAMES = list(hands.PRESETS)

def render(layers, pos, tgt, W, H, fov, light_c):
    L = [(tuple(V(light_c) + V((-1.5, 2.5, 2.5))), (255, 240, 220), 1.6), (tuple(V(light_c) + V((2.0, 0.4, 1.5))), (170, 196, 236), 0.6)]
    R = Renderer(W, H, fog=(214, 222, 232))
    img, vi, zb = zrender(R, Camera.look(tuple(pos), tuple(tgt)), layers, L, fov=fov, fog_start=30, fog_end=60, ambient=0.45, return_z=True)
    return Image.fromarray(np.clip(look.outline(np.asarray(img).astype(np.float32), zb), 0, 255).astype(np.uint8))

def label(im, txt):
    d = ImageDraw.Draw(im); d.rectangle((0, im.height - 18, im.width, im.height), fill=(20, 20, 24)); d.text((5, im.height - 15), txt, fill=(255, 230, 120)); return im

def sheet():
    c = V((0, 0.09, 0)); cells = []
    for n in NAMES:
        Q = hands.hand(V((0, 0, 0.0)), V((0, 1.0, 0)), V((0, 0, 1.0)), n, SKIN, 1.0, side=1)   # right hand, fingers up, palm to camera
        row = []
        for nm, yaw in (('palm', 15), ('side', 80), ('back', 180)):
            a = math.radians(yaw); pos = c + V((math.sin(a) * 0.42, 0.04, math.cos(a) * 0.42))
            row.append(render([Q], pos, c, 200, 220, 34, c))
        im = Image.new('RGB', (600, 220)); [im.paste(r, (i * 200, 0)) for i, r in enumerate(row)]
        cells.append(label(im, n))
    cols = 3; rows = (len(cells) + cols - 1) // cols; sh = Image.new('RGB', (cols * 604, rows * 224), (30, 30, 34))
    for i, c_ in enumerate(cells): sh.paste(c_, ((i % cols) * 604, (i // cols) * 224))
    sh.save(os.path.join(OUT, 'hand_sheet.png')); print('wrote hand_sheet.png')

S = hd.spec(h=1.78, build=1.05, skin=SKIN, hair=(62, 44, 32), hair_style='messy', eye=(70, 110, 150), brow=(46, 32, 24))
GEST = [  # (label, fingers, hand target in body-local metres, palm local, face, extra pose keys)
    ('point', 'point', (0.38, 1.5, 0.42), (0, -1, 0), 'determined', dict(rpole=(1.0, -0.8, -0.2))),
    ('wave', 'wave', (0.36, 1.7, 0.12), (0, 0, 1), 'laughing', {}),
    ('thumbs up', 'thumbs_up', (0.26, 1.3, 0.36), (-1, 0, 0), 'proud', {}),
    ('stop', 'spread', (0.3, 1.32, 0.5), (0, 0, 1), 'scared', dict(rwrist=(-1.25, 0.0), rpole=(1.0, -1.0, 0.0))),
    ('peace', 'peace', (0.3, 1.66, 0.25), (0, 0, 1), 'smug', {}),
    ('fist', 'fist', (0.36, 1.12, 0.22), (-1, 0, 0), 'angry', dict(rpole=(1.0, -0.5, -0.6))),
]
def body():
    cells = []
    for lab, fg, h, pal, fc, ex in GEST:
        P = dict(face=face.expr(fc), rh=h, rpalm=pal, rfingers=fg, lfingers='relaxed', **ex)
        Q = hd.human(S, P); hc = V(P['_head']); tgt = hc + V((0.08, -0.2, 0)); pos = tgt + V((0.25, 0.02, 1.5))
        im = render([Q], pos, tgt, 270, 480, 40, hc).resize((135, 240), Image.LANCZOS)
        cells.append(label(im, lab))
    sh = Image.new('RGB', (len(cells) * 139, 244), (30, 30, 34))
    for i, c_ in enumerate(cells): sh.paste(c_, (i * 139, 0))
    sh.save(os.path.join(OUT, 'hand_body_phone.png'))
    big = Image.new('RGB', (len(cells) * 274, 484), (30, 30, 34))
    for i, (lab, fg, h, pal, fc, ex) in enumerate(GEST):
        P = dict(face=face.expr(fc), rh=h, rpalm=pal, rfingers=fg, lfingers='relaxed', **ex)
        Q = hd.human(S, P); hc = V(P['_head']); tgt = hc + V((0.08, -0.2, 0)); pos = tgt + V((0.25, 0.02, 1.5))
        big.paste(label(render([Q], pos, tgt, 270, 480, 40, hc), lab), (i * 274, 0))
    big.save(os.path.join(OUT, 'hand_body.png')); print('wrote hand_body*.png')


def clip():
    """counting 1-5, fist, ok, beckon (index curling twice): poses snap in over 3 frames (hands.blend)"""
    seq = [(0.0, 'relaxed'), (0.4, 'one'), (0.8, 'two'), (1.2, 'three'), (1.6, 'four'), (2.0, 'five'), (2.5, 'fist'), (3.0, 'ok'), (3.5, 'beckon')]
    d = os.path.join(OUT, 'clip'); os.makedirs(d, exist_ok=True); c = V((0, 0.09, 0))
    for f in range(108):
        t = f / 24; i = max(j for j in range(len(seq)) if seq[j][0] <= t); a = seq[max(0, i - 1)][1]; b = seq[i][1]
        u = min(1.0, (t - seq[i][0]) / 0.125); u = 1 - (1 - u) ** 3
        H = hands.blend(a, b, u)
        if b == 'beckon' and u >= 1.0:
            w = 0.5 - 0.5 * math.cos((t - seq[i][0] - 0.125) * 2 * math.pi * 2.2); H['f'] = ((w * 0.9 + 0.1, w * 0.9 + 0.2, w * 0.7),) + tuple(H['f'][1:])
        Q = hands.hand(V((0, 0, 0.0)), V((0, 1.0, 0)), V((0, 0, 1.0)), H, SKIN, 1.0, side=1)
        render([Q], c + V((0.1, 0.04, 0.4)), c, 270, 480, 40, c).resize((1080, 1920), Image.NEAREST).save(os.path.join(d, f'f_{f + 1:04d}.png'))
    print('wrote clip frames')

if __name__ == '__main__':
    {'sheet': sheet, 'body': body, 'clip': clip}[sys.argv[1] if len(sys.argv) > 1 else 'sheet']()
