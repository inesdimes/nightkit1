"""Review sheet for the face performance layer (nightkit/face.py, phase 1). Not a video.
  python examples/face_sheet.py            # close-up sheet: old face + every preset, on two characters
  python examples/face_sheet.py wide       # the same presets at phone size in a medium shot (bold vs normal lines)
  python examples/face_sheet.py track      # a 4 s Track test clip (snap + hold, blinks, talk)  -> frames in renders/face_sheet/track
Output: C:/Users/USER/Documents/blender-shorts/renders/face_sheet/"""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera
from nightkit.zraster import zrender
from nightkit import hd, face, look, post
V = np.array
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'renders', 'face_sheet'); os.makedirs(OUT, exist_ok=True)
HERO = hd.spec(h=1.78, build=1.05, skin=(222, 176, 140), hair=(62, 44, 32), hair_style='messy', eye=(70, 110, 150), brow=(46, 32, 24))
GIRL = hd.spec(h=1.64, build=0.92, fem=1.0, skin=(232, 192, 162), hair=(150, 70, 44), hair_style='pony', eye=(80, 120, 70))
NAMES = ['neutral', 'determined', 'smug', 'shocked', 'scared', 'deadpan', 'angry', 'proud', 'sad', 'embarrassed', 'laughing']

def shot(S, P, W, H, dist, fov, yaw=0.0, low=False):
    Q = hd.human(S, P); hc = V(P['_head'])
    tgt = hc + V((0, -0.01 if not low else -0.35, 0)); a = math.radians(yaw)
    pos = tgt + V((math.sin(a) * dist, 0.03 if not low else 0.1, math.cos(a) * dist))
    L = [(tuple(hc + V((-2.0, 3.0, 3.0))), (255, 240, 220), 3.2), (tuple(hc + V((2.5, 0.5, 2.0))), (170, 196, 236), 1.0)]
    R = Renderer(W, H, fog=(214, 222, 232))
    img, vi, zb = zrender(R, Camera.look(tuple(pos), tuple(tgt)), [Q], L, fov=fov, fog_start=30, fog_end=60, ambient=0.45, return_z=True)
    a_ = look.outline(np.asarray(img).astype(np.float32), zb)
    return Image.fromarray(np.clip(a_, 0, 255).astype(np.uint8))

def label(im, txt):
    d = ImageDraw.Draw(im); d.rectangle((0, im.height - 22, im.width, im.height), fill=(20, 20, 24)); d.text((6, im.height - 18), txt, fill=(255, 230, 120)); return im

def sheet():
    for tag, S in (('hero', HERO), ('girl', GIRL)):
        cells = [label(shot(S, dict(), 300, 340, 0.62, 28).resize((300, 340)), 'OLD face')]
        for n in NAMES: cells.append(label(shot(S, dict(face=face.expr(n)), 300, 340, 0.62, 28, yaw=12), n))
        cols = 6; rows = (len(cells) + cols - 1) // cols; sh = Image.new('RGB', (cols * 304, rows * 344), (30, 30, 34))
        for i, c in enumerate(cells): sh.paste(c, ((i % cols) * 304, (i // cols) * 344))
        sh.save(os.path.join(OUT, f'face_sheet_{tag}.png')); print('wrote', f'face_sheet_{tag}.png')

def wide():
    # the repo's working res is 270 x 480 (x4 to 1080 x 1920); a medium shot = head ~ 1/12 of the frame height
    cells = []
    for n in ['neutral', 'determined', 'shocked', 'angry', 'laughing', 'sad']:
        for hs, b, fr in ((1.0, 1.4, 'full'), (1.3, 2.0, 'full'), (1.3, 2.0, 'mcu')):   # default / big head + bold / big head + medium close-up
            im = shot(HERO, dict(face=face.expr(n, bold=b), head_scale=hs), 270, 480, 2.4 if fr == 'full' else 1.15, 40, yaw=15, low=(fr == 'full'))
            im = post.ps1(im, levels=6).resize((135, 240), Image.LANCZOS)        # phone size
            cells.append(label(im, f'{n[:6]} {fr} h{hs}'))
    sh = Image.new('RGB', (6 * 139, 3 * 244), (30, 30, 34))
    for i, c in enumerate(cells): sh.paste(c, ((i // 3) * 139, (i % 3) * 244))
    sh.save(os.path.join(OUT, 'face_wide_phone.png')); print('wrote face_wide_phone.png')

def track():
    T = face.Track([(0.0, 'neutral'), (0.8, 'smug'), (1.6, 'shocked'), (2.4, 'angry'), (3.2, 'laughing')])
    d = os.path.join(OUT, 'track'); os.makedirs(d, exist_ok=True)
    for f in range(96):
        t = f / 24; talk = 0.7 if 0.9 < t < 1.5 else 0.0
        shot(HERO, dict(face=T.at(t, talk=talk)), 270, 480, 0.9, 30, yaw=10).resize((540, 960), Image.NEAREST).save(os.path.join(d, f'f_{f + 1:04d}.png'))
    print('wrote track frames')

if __name__ == '__main__':
    m = sys.argv[1] if len(sys.argv) > 1 else 'sheet'
    {'sheet': sheet, 'wide': wide, 'track': track}[m]()
