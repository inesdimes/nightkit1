"""WHAT IF EVERY HEALING POTION MADE SOMEONE FORGET YOU? (Insert Disc 2, 24 Nov 2026) ~45 s build (x1.2 after), PS1 dark fantasy, 9:16.
Brief: briefs/forget_potion.md (Blender there; Enes 24 Nov: "nightkite dÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¶n" -> built in nightkit with the new HD figures, nightkit/hd.py).
Story decisions (Enes 24 Nov): the wooden horse is planted in the ring portrait (young Mira holds it); line 13 stays (no wordless beat).
Format 3.0: constant camera, subject in the middle third, speaker-coloured subtitles, 270x480 + depth outline.

Asset lock: ASSET=lineup|faces|props python examples/forget_potion.py -> test_fp_<asset>.png"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import numpy as np
from PIL import Image
from nightkit.engine import Renderer, Camera
from nightkit.zraster import zrender
from nightkit import post, look, hd

W, H, S = 270, 480, 4
PI = math.pi

# ======================= cast (asset lock) =======================
ADV = hd.spec(h=1.8, build=1.02, skin=(214, 166, 128), hair=(62, 42, 30), hair_style='messy', eye=(64, 92, 120),
              tunic=(96, 104, 72), tunic2=(78, 84, 58), skirt=0.24, pants=(70, 58, 48), boots=(58, 40, 28),
              belt=(60, 38, 24), cloak=(46, 62, 82), cloak_len=1.0, collar=(110, 84, 60), ring=(240, 196, 80), ring_hand='l')
MIRA = hd.spec(h=1.68, build=0.9, fem=1.0, skin=(232, 190, 160), hair=(150, 72, 40), hair_style='long', eye=(90, 120, 70),
               tunic=(196, 184, 156), tunic2=(150, 120, 96), skirt=0.62, pants=(150, 120, 96), boots=(96, 66, 44),
               belt=(120, 70, 50), buckle=(200, 170, 90), collar=None)
KAYA = hd.spec(h=1.72, build=0.95, fem=1.0, skin=(196, 148, 112), hair=(34, 28, 30), hair_style='pony', eye=(70, 56, 40),
               tunic=(146, 66, 48), tunic2=(118, 50, 38), skirt=0.2, pants=(64, 56, 60), boots=(50, 36, 30),
               belt=(50, 34, 26), buckle=(180, 180, 190), gloves=(90, 62, 44))
SOLDIER = hd.spec(h=1.74, build=1.08, skin=(206, 158, 124), hair=(160, 156, 150), hair_style='short', beard=(176, 172, 166),
                  tunic=(120, 124, 130), tunic2=(96, 100, 108), skirt=0.26, pants=(80, 70, 60), boots=(56, 44, 34),
                  helmet=(150, 156, 164), eye=(80, 80, 90))
INNK = hd.spec(h=1.74, build=1.28, skin=(226, 168, 132), hair=(90, 60, 40), hair_style='bald', beard=(110, 70, 42),
               tunic=(170, 140, 110), tunic2=(140, 112, 86), sleeves='short', skirt=0.12, pants=(90, 70, 52), boots=(64, 46, 32),
               apron=(222, 214, 196), eye=(70, 60, 50))
CAST = dict(adv=ADV, mira=MIRA, kaya=KAYA, soldier=SOLDIER, innk=INNK)


def shot(layers, cam_pos, tgt, fov=40, lights=None, fog=(30, 30, 40), amb=0.45):
    R = Renderer(W, H, fog=fog); cam = Camera.look(cam_pos, tgt)
    L = lights or [((1.5, 2.5, -2.0), (255, 226, 190), 2.0), ((-2.5, 1.5, 1.0), (150, 170, 230), 0.8)]
    img, vi, zb = zrender(R, cam, layers, L, fov=fov, fog_start=10, fog_end=40, ambient=amb, return_z=True)
    a = look.outline(np.asarray(img).astype(np.float32), zb)
    return post.ps1(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), levels=6)


ASSET = os.environ.get('ASSET')
if ASSET and __name__ == '__main__':
    import time
    ims = []
    if ASSET == 'lineup':
        xs = [-1.6, -0.8, 0.0, 0.8, 1.6]
        poses = [dict(base=(x, 0, 0), yaw=PI + 0.25 * (i - 2) * 0.3, eyes='open', mouth='neutral') for i, x in enumerate(xs)]
        poses[0].update(rh=(0.25, 1.35, 0.35), rgrip=0.8, mouth='smile')
        poses[1].update(mouth='soft', head=(0.2, 0.05, 0.08))
        poses[2].update(rh=(0.3, 1.1, 0.35), lh=(-0.2, 1.0, 0.3), mouth='open', brow=0.7, eyes='wide')
        poses[3].update(mouth='frown', brow=0.4)
        poses[4].update(lh=(-0.25, 1.05, 0.3), rh=(0.25, 1.05, 0.3), lgrip=0.9, rgrip=0.9, mouth='grit')
        Q = []; t0 = time.time()
        for sp, po in zip(CAST.values(), poses): Q += hd.human(sp, po)
        print('faces', len(Q), 'build', round(time.time() - t0, 2))
        floor = hd.bx((0, -0.05, 0), np.eye(3), (4, 0.05, 3), (70, 64, 58))
        for cp, tg, fv in (((0, 1.2, -4.6), (0, 0.95, 0), 40), ((-1.2, 1.5, -1.8), (-1.2, 1.2, 0), 30)):
            t0 = time.time(); ims.append(shot([floor, Q], cp, tg, fv)); print('render', round(time.time() - t0, 2))
    elif ASSET == 'faces':
        for i, (nm, sp) in enumerate(CAST.items()):
            for po in (dict(eyes='open', mouth='smile'), dict(eyes='blank', mouth='neutral', brow=-0.6)):
                P_ = dict(base=(0, 0, 0), yaw=PI + 0.35, **po); Q = hd.human(sp, P_); hc = P_['_head']
                ims.append(shot([Q], (hc[0] - 0.16, hc[1] + 0.02, hc[2] - 0.5), tuple(hc - np.array([0, 0.02, 0])), 34))
    elif ASSET == 'props':
        Q = hd.potion((-0.12, 0.0, 0.0), scale=1.0) + hd.wooden_horse((0.1, 0, 0), hd.Ry(-0.9), scale=1.6) + hd.sword((0.0, 0.03, 0.3), (1, 0.02, 0), (0, 1, 0), length=0.5)
        ims.append(shot([Q], (0, 0.28, -0.62), (0, 0.06, 0.05), 34, fog=(40, 36, 44)))
    out = Image.new('RGB', (W * S * len(ims) // 2, H * S // 2))
    for i, im in enumerate(ims): out.paste(im.resize((W * S // 2, H * S // 2), Image.NEAREST), (i * W * S // 2, 0))
    out.save(os.environ.get('TEST_OUT', f'test_fp_{ASSET}.png')); print('written')
    sys.exit()

# =====================================================================================================================
#                                                      THE FILM
# =====================================================================================================================
import json
from PIL import ImageDraw
from nightkit import motion, font
from nightkit.audio import Sound, duck_envelope, soft_fire
OUT = 'out'; os.makedirs(OUT, exist_ok=True)
FPS = 24
TTS_DIR = os.environ.get('TTS_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tts'))
sm = motion.smooth
def seg01(t, a, b): return max(0.0, min(1.0, (t - a) / (b - a))) if b > a else (1.0 if t >= b else 0.0)
def win(t, a, b, r=0.25): return sm(seg01(t, a, a + r)) * (1 - sm(seg01(t, b - r, b)))
def lerp(a, b, u): return a + (b - a) * u
def lerp3(a, b, u): return tuple(a[i] + (b[i] - a[i]) * u for i in range(len(a)))
def hsh(i, s=0): v = math.sin(i * 127.1 + s * 311.7) * 43758.5453; return v - math.floor(v)
def ang_to(p, q): return math.atan2(q[0] - p[0], q[2] - p[2])
def mixc(a, b, u): return tuple(int(round(x + (y - x) * max(0.0, min(1.0, u)))) for x, y in zip(a, b))
V = np.array

# ======================= voice timings (tools/tts/fpo.py) =======================
SCR = json.load(open(os.path.join(TTS_DIR, 'fpo', 'script.json')))
KEYS = ['%02d' % i for i in range(1, 17)]
EXTRA = {'01': 0.2, '02': 0.45, '03': 0.3, '04': 0.35, '05': 0.25, '06': 0.3, '07': 0.35, '08': 0.3, '09': 0.5, '10': 0.6,
         '11': 0.35, '12': 0.35, '13': 0.3, '14': 0.4, '15': 0.5, '16': 0.0}
def _lines():
    t = 0.35; out = []
    for k in KEYS: out.append((k, round(t, 3))); t += SCR['dur'][k] + EXTRA[k]
    return out
LINES = _lines(); T0 = dict(LINES)
def tend(k): return T0[k] + SCR['dur'][k]
def ws(k, i): return T0[k] + SCR['sent'][k][i][0]
T_BLACK = tend('16') - 0.12                     # hard cut to black on the last word
DUR = round(T_BLACK + 0.55, 2); N = int(round(DUR * FPS))
# scene cuts
T_BAT = T0['04'] - 0.2; T_INN = T0['05'] - 0.3; T_LAB = T0['07'] - 0.25; T_BR = T0['08'] - 0.15; T_DAWN = T0['15'] - 0.4
def scene(t):
    if t < T_BAT: return 'camp'
    if t < T_INN: return 'battle'
    if t < T_LAB: return 'inn'
    if t < T_BR: return 'label'
    if t < T_DAWN: return 'bridge'
    return 'dawn'
CUTS = [0.0, T_BAT, T_INN, T_LAB, T_BR, T_DAWN]

def talking(t, key):
    """mouth state while a character speaks its line (sentence windows from the voice build)"""
    if key not in T0: return None
    for a, b, _ in SCR['sent'][key]:
        if T0[key] + a <= t < T0[key] + b: return 'open' if (t * 7.3 + 0.2 * math.sin(t * 13)) % 1.0 < 0.55 else 'neutral'
    return None

# ======================= held props =======================
def grip_pt(P, key, off=0.075, lift=0.03): return P['_' + key + 'wrist'] + P['_' + key + 'dir'] * off + P['_' + key + 'palm'] * lift
def up_R(u, fwd=(0, 0, 1.0)):
    u = hd.nz(u); x = np.cross(u, np.asarray(fwd, float))
    if np.linalg.norm(x) < 1e-4: x = np.cross(u, np.array([1.0, 0, 0]))
    x = hd.nz(x); z = np.cross(x, u); return np.column_stack([x, u, z])
def mouth_pt(P, fwd=0.11, down=0.05): return P['_head'] + P['_RH'] @ np.array([0, -down, fwd])
def head_pose(S, P):
    """run the figure once to learn where its head is (for hands that must reach the mouth)"""
    Q = dict(P); hd.human(S, Q); return Q

# ======================= sets =======================
def tree(x, z, h, col=(34, 56, 42), trunk=(58, 42, 30), seed=0):
    Q = hd.limb((x, 0, z), (x, h * 0.35, z), 0.09 * h / 4, 0.07 * h / 4, trunk, n=6, m=1)
    for i in range(4):
        y0 = h * (0.22 + 0.18 * i); r = h * (0.32 - 0.06 * i) * (0.9 + 0.2 * hsh(seed, i)); c = hd.shade(col, 0.85 + 0.1 * (i % 2) + 0.1 * hsh(seed, i + 9))
        Q += hd.lathe((x, y0, z), hd.Ry(hsh(seed, i) * 3), [(r, 0), (r * 0.55, h * 0.16), (0.02, h * 0.3)], 9, c, colfn=lambda a, j, c=c: hd.shade(c, 0.86) if j % 2 else c, cap1=False)
    return Q
def rock(c, r, col=(96, 92, 88), seed=0, flat=0.6):
    def d(p): k = 1 + 0.18 * math.sin(p[0] * 31 + seed) * math.cos(p[2] * 23 + seed * 2); return p * k
    return hd.ellip(c, hd.Ry(seed), (r, r * flat, r * 0.9), 8, 5, col, deform=d, colfn=lambda i, j, cl: hd.shade(col, 0.82 + 0.25 * hsh(i * 13 + j, seed)))
def ground(x0, x1, z0, z1, step, cols, seed=0, y=0.0, yfn=None):
    Q = []; xs = np.arange(x0, x1 + 1e-6, step); zs = np.arange(z0, z1 + 1e-6, step)
    for i in range(len(xs) - 1):
        for j in range(len(zs) - 1):
            a, b, c, d = xs[i], xs[i + 1], zs[j], zs[j + 1]; h = hsh(i * 31 + j * 7, seed)
            col = hd.shade(cols[int(h * len(cols)) % len(cols)], 0.9 + 0.2 * hsh(i * 3 + j * 17, seed + 1))
            Y = (lambda x, z: y) if yfn is None else yfn
            q = hd.face([(a, Y(a, c), c), (a, Y(a, d), d), (b, Y(b, d), d), (b, Y(b, c), c)], col)
            if q: Q.append(q)
    return Q
def sky_disc(c, r, col, n=14):
    c = np.asarray(c, float); return [hd.face([c + np.array([r * math.cos(2 * PI * i / n), r * math.sin(2 * PI * i / n), 0]) for i in range(n)], col, emit=True)]
def stars(seed, n, z, y0, y1, x0, x1):
    Q = []
    for i in range(n):
        x = lerp(x0, x1, hsh(i, seed)); y = lerp(y0, y1, hsh(i, seed + 1)); s = 0.05 + 0.06 * hsh(i, seed + 2)
        Q.append(hd.face([(x - s, y, z), (x, y - s, z), (x + s, y, z), (x, y + s, z)], (200, 210, 235), emit=True))
    return [q for q in Q if q]

# ---- CAMP: night clearing, fire, tent, pines
FIRE = (0.95, 0.0, 2.55)
def camp_set():
    Q = ground(-9, 9, -3, 16, 0.75, [(52, 60, 40), (58, 62, 42), (48, 52, 38), (64, 58, 44)], seed=3)
    for i in range(22):
        a = 2 * PI * i / 22 + hsh(i, 1) * 0.2; r = 6.5 + 3.5 * hsh(i, 2); x = FIRE[0] + r * math.sin(a); z = FIRE[2] + r * math.cos(a)
        if z < 0.5: continue
        Q += tree(x, z, 3.6 + 2.2 * hsh(i, 3), seed=i)
    for i in range(8):                                                          # fire ring stones
        a = 2 * PI * i / 8; Q += rock((FIRE[0] + 0.34 * math.cos(a), 0.05, FIRE[2] + 0.34 * math.sin(a)), 0.09, (110, 104, 98), seed=i)
    Q += hd.limb((FIRE[0] - 0.25, 0.08, FIRE[2] - 0.12), (FIRE[0] + 0.25, 0.12, FIRE[2] + 0.1), 0.05, 0.045, (70, 46, 30), n=7, m=1)
    Q += hd.limb((FIRE[0] - 0.15, 0.1, FIRE[2] + 0.22), (FIRE[0] + 0.12, 0.08, FIRE[2] - 0.24), 0.045, 0.04, (82, 54, 34), n=7, m=1)
    Q += hd.limb((-1.6, 0.18, 3.4), (0.4, 0.2, 3.9), 0.18, 0.17, (88, 64, 44), n=10, m=3)        # fallen log behind them
    tx, tz = -2.6, 4.6; c1 = (150, 138, 104); c2 = (124, 112, 84)                                # tent
    A_, B_, C_, D_, E_, F_ = (tx - 1.0, 0, tz - 0.9), (tx + 1.0, 0, tz - 0.9), (tx, 1.3, tz - 0.9), (tx - 1.0, 0, tz + 0.9), (tx + 1.0, 0, tz + 0.9), (tx, 1.3, tz + 0.9)
    for pts, c in (([A_, C_, F_, D_], c1), ([B_, E_, F_, C_], c2), ([D_, F_, E_], c2)): Q.append(hd.face(pts, c))
    Q.append(hd.face([A_, (tx - 0.1, 0, tz - 0.9), C_], c2)); Q.append(hd.face([(tx + 0.1, 0, tz - 0.9), B_, C_], c1))
    Q.append(hd.face([(tx - 0.1, 0, tz - 0.89), (tx + 0.1, 0, tz - 0.89), C_], (30, 26, 22)))
    Q += hd.lathe((1.9, 0, 3.4), np.eye(3), [(0.18, 0), (0.2, 0.35), (0.16, 0.45)], 9, (100, 72, 48))                    # pack
    Q += sky_disc((-9, 14, 26), 1.3, (220, 226, 240)) + stars(5, 40, 28, 6, 22, -22, 22)
    return [q for q in Q if q]
def fire_faces(t, k=1.0):
    Q = []
    for i in range(7):
        a = 2 * PI * i / 7 + 0.3; r = 0.1 + 0.05 * hsh(i, 4); x = FIRE[0] + r * math.cos(a) * 0.6; z = FIRE[2] + r * math.sin(a) * 0.6
        h = k * (0.34 + 0.18 * hsh(i, 5)) * (0.75 + 0.25 * math.sin(t * (9 + i) + i * 2.1)); w = 0.07 + 0.03 * hsh(i, 6)
        col = (255, 210, 90) if i % 3 == 0 else ((255, 150, 50) if i % 3 == 1 else (240, 96, 36))
        for ang in (0.0, PI / 2):
            dx, dz = w * math.cos(a + ang), w * math.sin(a + ang); sw = 0.03 * math.sin(t * 7 + i)
            Q.append(hd.face([(x - dx, 0.1, z - dz), (x + dx, 0.1, z + dz), (x + sw, 0.1 + h, z)], col, emit=True))
    for i in range(10):                                                         # embers rising
        u = (t * 0.55 + hsh(i, 8)) % 1.0; x = FIRE[0] + 0.2 * math.sin(i * 3 + t * 1.3) * u; z = FIRE[2] + 0.15 * math.cos(i * 2 + t) * u; y = 0.3 + 1.6 * u; s = 0.014
        if u < 0.85: Q += hd.bx((x, y, z), np.eye(3), (s, s, s), (255, 170, 70), emit=True)
    return [q for q in Q if q]

# ---- BATTLE (flashback): mud, broken cart, spears, banner, smoke
def battle_set():
    Q = ground(-10, 10, -3, 18, 0.8, [(88, 72, 58), (76, 64, 52), (96, 80, 62), (70, 60, 50)], seed=7)
    cx, cz = 1.35, 2.9                                                            # cart (on its side a little)
    R = hd.Ry(0.5) @ hd.Rz(0.12)
    Q += hd.bx((cx, 0.6, cz), R, (0.9, 0.28, 0.55), (110, 80, 54)) + hd.bx((cx, 0.95, cz), R, (0.92, 0.06, 0.58), (90, 64, 44))
    for sx in (-1, 1):
        c = V((cx, 0.0, cz)) + R @ V((sx * 0.55, 0.42, -0.6)); Rw = R @ hd.Rx(PI / 2)
        Q += hd.lathe(c - R @ V((0, 0, 0.04)), Rw, [(0.42, 0), (0.42, 0.08)], 14, (84, 60, 40))
        for k in range(6): Q += hd.limb(c, c + R @ V((0.38 * math.cos(k * PI / 3), 0.38 * math.sin(k * PI / 3), -0.06)), 0.02, 0.02, (64, 46, 30), n=4, m=1)
    for i, (x, z, a, b) in enumerate(((-2.4, 5.0, 0.35, 0.2), (-1.6, 6.4, -0.3, 0.1), (2.6, 6.0, 0.25, -0.3), (3.6, 4.4, -0.4, 0.2), (-3.4, 3.2, 0.15, 0.4), (0.4, 7.5, 0.1, -0.1))):
        top = (x + 1.6 * math.sin(a), 1.6 * math.cos(a) * math.cos(b), z + 1.6 * math.sin(b))
        Q += hd.limb((x, 0, z), top, 0.022, 0.018, (92, 72, 52), n=5, m=1) + hd.limb(top, V(top) + hd.nz(V(top) - V((x, 0, z))) * 0.2, 0.03, 0.003, (150, 150, 156), n=4, m=1)
    Q += hd.limb((-1.2, 0, 4.2), (-1.15, 3.2, 4.2), 0.04, 0.035, (80, 60, 44), n=6, m=1)                     # banner pole
    Q += rock((-0.9, 0.05, 1.2), 0.25, (96, 90, 84), seed=2) + rock((2.4, 0.06, 1.5), 0.3, (90, 86, 80), seed=5)
    for i in range(5): Q += hd.bx((-4 + 2 * i + hsh(i, 2), 0.25, 9 + 2 * hsh(i, 3)), hd.Ry(hsh(i, 4) * 3), (0.5, 0.25, 0.3), (70, 60, 50))
    return [q for q in Q if q]
def battle_fx(t):
    Q = []
    for i in range(8):                                                           # banner cloth: torn strips that wave
        y = 3.05 - i * 0.11; w = 0.7 - 0.05 * i - 0.2 * hsh(i, 9); ph = t * 3 + i * 0.4
        p0 = (-1.15, y, 4.2); p1 = (-1.15 + w, y + 0.03 * math.sin(ph), 4.2 + 0.12 * math.sin(ph + 1))
        Q.append(hd.face([p0, p1, (p1[0], p1[1] - 0.1, p1[2]), (p0[0], p0[1] - 0.1, p0[2])], (150, 40, 36) if i % 2 else (126, 34, 30)))
    for j, (x, z) in enumerate(((-3.2, 8.0), (3.0, 10.0), (0.5, 12.0))):                               # smoke columns from distant fires
        for i in range(7):
            u = ((t * 0.18 + i / 7 + hsh(j, 1)) % 1.0); r = 0.35 + 0.9 * u; y = 0.4 + 5.0 * u
            Q += hd.ellip((x + 0.6 * u * math.sin(j + u * 3), y, z), np.eye(3), (r, r * 0.7, r), 7, 4, hd.shade((96, 94, 92), 1.1 - 0.4 * u))
        for i in range(4):
            h = 0.5 + 0.3 * math.sin(t * 8 + i + j); a = i * 1.4
            Q.append(hd.face([(x + 0.3 * math.cos(a), 0.0, z + 0.3 * math.sin(a)), (x - 0.3 * math.cos(a), 0.0, z - 0.3 * math.sin(a)), (x, h, z)], (255, 140, 60), emit=True))
    return [q for q in Q if q]

# ---- INN: Hearthmoor front door at night
DOOR_Z = 3.0
def inn_set():
    Q = ground(-6, 6, -3, DOOR_Z, 0.3, [(92, 88, 82), (80, 76, 72), (104, 98, 90), (72, 70, 66)], seed=11)
    PL = (150, 136, 112); TB = (62, 42, 28); z = DOOR_Z
    def wall(x0, x1, y0, y1):
        Qw = []
        for i, x in enumerate(np.arange(x0, x1 - 1e-6, 0.5)):
            for j, y in enumerate(np.arange(y0, y1 - 1e-6, 0.5)):
                xa, xb, ya, yb = x, min(x + 0.5, x1), y, min(y + 0.5, y1); c = hd.shade(PL, 0.88 + 0.16 * hsh(i * 7 + j, 3))
                Qw.append(hd.face([(xa, ya, z), (xa, yb, z), (xb, yb, z), (xb, ya, z)], c))
        return Qw
    Q += wall(-5, -0.6, 0, 4.4) + wall(0.6, 5, 0, 4.4) + wall(-0.6, 0.6, 2.2, 4.4)
    for x in (-5.0, -3.0, -0.75, 0.6, 3.0, 4.85): Q += hd.bx((x + 0.075, 2.2, z - 0.05), np.eye(3), (0.075, 2.2, 0.06), TB)       # posts
    for y in (0.15, 2.2, 4.3): Q += hd.bx((0, y, z - 0.06), np.eye(3), (5.1, 0.07, 0.06), TB)                                      # beams
    for sx in (-1, 1):
        for x0, y0 in ((-4.6, 0.25), (-2.6, 0.3), (1.1, 0.25), (3.2, 0.3)):
            Q += hd.limb((x0, y0 + 0.05, z - 0.06), (x0 + 1.3, y0 + 1.8, z - 0.06), 0.045, 0.045, TB, n=4, m=1) if sx > 0 else []
    for wx in (-2.0, 2.0):                                                     # glowing windows with mullions
        Q.append(hd.face([(wx - 0.55, 2.7, z - 0.01), (wx + 0.55, 2.7, z - 0.01), (wx + 0.55, 3.6, z - 0.01), (wx - 0.55, 3.6, z - 0.01)], (255, 196, 110), emit=True))
        Q += hd.bx((wx, 3.15, z - 0.03), np.eye(3), (0.03, 0.47, 0.02), TB) + hd.bx((wx, 3.15, z - 0.03), np.eye(3), (0.57, 0.03, 0.02), TB)
        Q += hd.bx((wx, 2.66, z - 0.1), np.eye(3), (0.62, 0.04, 0.1), TB)
    Q += hd.bx((0, 4.6, z - 0.5), hd.Rx(-0.35), (5.4, 0.08, 0.7), (60, 42, 36))                                                      # roof edge
    Q.append(hd.face([(-0.6, 0, z + 1.4), (0.6, 0, z + 1.4), (0.6, 2.2, z + 1.4), (-0.6, 2.2, z + 1.4)], (255, 186, 96), emit=True))  # lit interior
    for sx in (-1, 1): Q.append(hd.face([(sx * 0.6, 0, z), (sx * 0.6, 0, z + 1.4), (sx * 0.6, 2.2, z + 1.4), (sx * 0.6, 2.2, z)], (150, 96, 56)))
    Q.append(hd.face([(-0.6, 2.2, z), (0.6, 2.2, z), (0.6, 2.2, z + 1.4), (-0.6, 2.2, z + 1.4)], (120, 80, 50)))
    Q.append(hd.face([(-0.6, 0.002, z), (0.6, 0.002, z), (0.6, 0.002, z + 1.4), (-0.6, 0.002, z + 1.4)], (170, 120, 70)))
    Q += hd.bx((-1.4, 2.95, z - 0.45), np.eye(3), (0.02, 0.02, 0.45), (40, 30, 24))                                                  # sign bracket + board
    Q += hd.bx((-1.4, 2.62, z - 0.55), np.eye(3), (0.32, 0.22, 0.025), (120, 86, 52))
    Q += hd.lathe((-1.4, 2.5, z - 0.58), hd.Rx(PI / 2), [(0.085, 0), (0.085, 0.01)], 10, (220, 170, 70)) + hd.bx((-1.28, 2.6, z - 0.585), np.eye(3), (0.03, 0.05, 0.008), (220, 170, 70))
    Q += hd.bx((-1.4, 2.83, z - 0.585), np.eye(3), (0.1, 0.03, 0.008), (240, 234, 220))                                              # foam on the mug
    Q += hd.bx((0.95, 2.0, z - 0.12), np.eye(3), (0.02, 0.02, 0.1), (40, 30, 24))
    Q += hd.lathe((0.95, 1.72, z - 0.22), np.eye(3), [(0.06, 0), (0.08, 0.06), (0.08, 0.18), (0.03, 0.26)], 8, (255, 214, 130), cap1=True)
    for q in Q[-10:]: q['emit'] = True
    Q += hd.lathe((2.6, 0, 2.2), np.eye(3), [(0.28, 0), (0.32, 0.4), (0.28, 0.8)], 10, (110, 76, 48)) + hd.lathe((3.2, 0, 2.5), np.eye(3), [(0.28, 0), (0.32, 0.4), (0.28, 0.8)], 10, (96, 68, 44))
    Q += sky_disc((-8, 13, 30), 1.0, (220, 226, 240)) + stars(9, 30, 32, 6, 20, -20, 20)
    return [q for q in Q if q]
def door_leaf(t):
    """door hinged at x=-0.6; open (swung inwards) until line 06, then it shuts"""
    u = sm(seg01(t, T0['06'] - 0.05, T0['06'] + 0.45)); a = lerp(-1.75, 0.0, u)
    R = hd.Ry(a); c = V((-0.6, 0, DOOR_Z + 0.04)) + R @ V((0.6, 1.1, 0.04))
    Q = hd.bx(c, R, (0.6, 1.1, 0.05), (96, 62, 38))
    for k in (-0.35, 0.35): Q += hd.bx(c + R @ V((0, k * 1.6, -0.06)), R, (0.58, 0.05, 0.015), (52, 40, 32))
    Q += hd.bx(c + R @ V((0.42, 0, -0.07)), R, (0.03, 0.05, 0.02), (180, 150, 80))
    return Q, u

# ---- BRIDGE: old stone bridge over a stream on Thornwood Road
def deck_y(x): return 0.25 + 1.65 * math.cos(PI * max(-7.0, min(7.0, x)) / 14.0)
ARCH_R = 1.9; ARCH_Y = -0.35; BW = 1.1
def bank_y(x, z=0.0):
    ax = abs(x); return 0.0 if ax > 2.6 else (-0.55 if ax < 1.9 else -0.55 + 0.55 * sm((ax - 1.9) / 0.7))
def bridge_set():
    Q = []; ST = [(128, 124, 116), (116, 112, 106), (138, 132, 122), (108, 106, 100)]
    Q += ground(-14, 14, -10, 16, 0.7, [(58, 72, 46), (52, 66, 44), (64, 76, 50), (70, 66, 50)], seed=21, yfn=lambda x, z: bank_y(x, z) - 0.002)
    for i in range(int(-1.9 / 0.38), int(1.9 / 0.38)):
        for j in range(-14, 22):
            x0, x1, z0, z1 = i * 0.38, (i + 1) * 0.38, j * 0.7, (j + 1) * 0.7
            Q.append(hd.face([(x0, -0.32, z0), (x0, -0.32, z1), (x1, -0.32, z1), (x1, -0.32, z0)], (30, 44, 60)))
    # arch ring (voussoirs through the whole width)
    n = 15
    for i in range(n):
        a0 = PI * i / n; a1 = PI * (i + 1) / n; am = (a0 + a1) / 2
        c = V((-(ARCH_R + 0.18) * math.cos(am), ARCH_Y + (ARCH_R + 0.18) * math.sin(am), 0)); Rr = hd.Rz(am - PI / 2)
        Q += hd.bx(c, Rr, (ARCH_R * PI / n * 0.5 - 0.01, 0.18, BW + 0.04), ST[i % 4])
    # spandrel walls + abutments: stone courses on both faces
    for zf in (-BW, BW):
        for i, x in enumerate(np.arange(-7.0, 7.0, 0.42)):
            top = deck_y(x + 0.21) - 0.12
            for j, y in enumerate(np.arange(-0.3, top, 0.26)):
                xm = x + 0.21 + (0.1 if j % 2 else -0.1); ym = y + 0.13
                if (xm ** 2 + (ym - ARCH_Y) ** 2) ** 0.5 < ARCH_R + 0.36: continue
                if ym < bank_y(xm) - 0.05: continue
                hgt = min(0.13, (top - y) / 2)
                Q += hd.bx((xm, y + hgt, zf), np.eye(3), (0.2, hgt - 0.008, 0.06), hd.shade(ST[(i + j) % 4], 0.9 + 0.2 * hsh(i * 9 + j, 4)))
        Q.append(hd.face([(-7, -0.6, zf * 0.98), (7, -0.6, zf * 0.98), (7, 0.6, zf * 0.98), (-7, 0.6, zf * 0.98)], (90, 88, 84)))
    # deck surface (cobbles) + parapets
    for i, x in enumerate(np.arange(-7.0, 7.0, 0.35)):
        y0, y1 = deck_y(x), deck_y(x + 0.35)
        for j, z in enumerate(np.arange(-BW, BW - 1e-6, 0.44)):
            c = hd.shade(ST[(i * 3 + j) % 4], 0.85 + 0.15 * hsh(i * 5 + j, 6))
            Q.append(hd.face([(x, y0, z), (x, y0, z + 0.44), (x + 0.35, y1, z + 0.44), (x + 0.35, y1, z)], c))
        for zf in (-BW, BW):
            Q += hd.bx((x + 0.175, (y0 + y1) / 2 + 0.26, zf), hd.Rz(math.atan2(y1 - y0, 0.35)), (0.17, 0.26, 0.11), hd.shade(ST[(i + 2) % 4], 0.95 + 0.1 * hsh(i, 8)))
    Q += hd.limb((-3.6, deck_y(-3.6) + 0.5, -BW), (-3.6, deck_y(-3.6) + 1.7, -BW), 0.05, 0.05, (50, 40, 32), n=6, m=1)     # lantern post
    Q += hd.bx((-3.6, deck_y(-3.6) + 1.72, -BW - 0.2), np.eye(3), (0.02, 0.02, 0.2), (50, 40, 32))
    for i in range(30):                                                         # reeds
        x = (2.0 + 0.6 * hsh(i, 1)) * (1 if i % 2 else -1); z = -6 + 14 * hsh(i, 2)
        if abs(z) < 1.4: continue
        for k in range(3): Q += hd.limb((x + 0.05 * k, bank_y(x) - 0.05, z), (x + 0.1 * k - 0.1, bank_y(x) + 0.6 + 0.3 * hsh(i, k), z + 0.1 * (k - 1)), 0.012, 0.004, (74, 96, 56), n=3, m=1)
    for i in range(9): Q += rock(((2.4 + 1.5 * hsh(i, 3)) * (1 if i % 2 else -1), bank_y(2.4) + 0.05, -5 + 10 * hsh(i, 4)), 0.2 + 0.2 * hsh(i, 5), seed=i)
    Q += rock((-3.0, 0.05, -1.45), 0.32, (104, 100, 94), seed=3, flat=0.8)
    for i in range(24):
        x = -14 + 28 * hsh(i, 7); z = 9 + 7 * hsh(i, 8)
        Q += tree(x, z, 4 + 3 * hsh(i, 9), seed=i + 40)
    for i in range(6):                                                          # far hills
        x = -30 + 12 * i; Q += hd.ellip((x, -2, 34), np.eye(3), (9, 6 + 3 * hsh(i, 2), 3), 10, 5, (40, 52, 50))
    return [q for q in Q if q]
def lantern_faces(on=1.0):
    c = V((-3.6, deck_y(-3.6) + 1.48, -BW - 0.36))
    Q = hd.limb(c + V((0, 0.22, 0)), c + V((0, 0.25, 0)), 0.01, 0.01, (40, 30, 24), n=4, m=1)
    L = hd.lathe(c, np.eye(3), [(0.06, 0), (0.09, 0.05), (0.09, 0.17), (0.04, 0.22)], 8, mixc((90, 70, 50), (255, 214, 130), on))
    for q in L: q['emit'] = on > 0.2
    return Q + L, tuple(c)
def rain_faces(cam, t, amt=1.0, n=220, col=(118, 134, 162)):
    if amt <= 0.01: return []
    cp = V(cam[:3]); yaw = cam[3]; fwd = V((math.sin(yaw), 0, math.cos(yaw))); rt = V((math.cos(yaw), 0, -math.sin(yaw)))
    Q = []
    for i in range(int(n * amt)):
        d = 1.4 + 7.5 * hsh(i, 1); s = (hsh(i, 2) - 0.5) * 2 * d * 0.9; base = cp + fwd * d + rt * s
        y = cp[1] + 3.5 - ((t * 8.5 + hsh(i, 3) * 7.0) % 7.0); L = 0.2; w = 0.0045 + 0.004 * d / 8
        a = V((base[0], y, base[2])); b = a + V((0.04, -L, 0))
        Q.append(hd.face([a - rt * w, a + rt * w, b + rt * w, b - rt * w], col, emit=True))
    return [q for q in Q if q]

# ======================= characters per scene =======================
A_CAMP = (0.0, 0.0, 1.95); YAW_A = PI + 0.35
K0 = (-0.95, 0.0, 2.5); K1 = (-1.55, 0.0, 2.85)
T_GULP = (0.0, 0.75); T_HEAL = 0.8; T_JOLT = 1.45; T_RISE = (1.75, 2.6); T_DRAW = (T0['02'] - 0.25, T0['02'] + 0.1)
T_REACH = (ws('02', 1) - 0.15, ws('02', 1) + 0.3)
def kneel(P, front='r', drop=0.43):
    """down on one knee: front foot planted forward, back knee on the ground"""
    b = 'l' if front == 'r' else 'r'; s = 1 if front == 'r' else -1
    P.update(crouch=drop); P[front + 'f'] = (s * 0.14, 0.07, 0.33); P[b + 'f'] = (-s * 0.13, 0.06, -0.52); P[b + 'kpole'] = (0, -0.8, 1.0)
    P[b + 'fdir'] = None; return P
def adv_camp(t):
    P = dict(base=A_CAMP, yaw=YAW_A, eyes='open', mouth='neutral', brow=-0.2, lean=0.12)
    kneel(P, 'r')
    if t < T_GULP[1] + 0.35:                                                    # gulps: head back, bottle at the lips
        u = win(t, -1, T_GULP[1] + 0.35, 0.35); P.update(nod=-0.42 * u, eyes='closed' if t < T_GULP[1] else 'half')
    if t >= T_HEAL: P['eyes'] = 'open'
    if T_HEAL <= t < T_HEAL + 0.6: P['eyes'] = 'wide'
    look_k = sm(seg01(t, T_JOLT + 0.1, T_JOLT + 0.5))
    if look_k > 0:
        P['head'] = (0.55 * look_k, 0.0, 0.05 * look_k); P['twist'] = 0.2 * look_k
    if t >= T_REACH[0]:
        u = sm(seg01(t, *T_REACH)) * (1 - sm(seg01(t, T_BAT - 2.2, T_BAT - 1.6)))
        P['lh_w'] = tuple(V(A_CAMP) + V((-0.55, 1.05, 0.25)) * 1.0) if u > 0.999 else None
        if 0 < u < 0.999:
            P['lh_w'] = tuple(V(A_CAMP) + lerp3(V((-0.25, 0.55, -0.05)), V((-0.55, 1.05, 0.25)), u))
        P['lgrip'] = 0.15; P['lpalm'] = (0, 1.0, 0.3); P['brow'] = -0.7; P['mouth'] = 'o' if u > 0.5 else 'neutral'
    if t >= T0['03'] - 0.6:                                                     # looks down at the ring in his palm
        u = sm(seg01(t, T0['03'] - 0.6, T0['03'] + 0.1))
        P['lh_w'] = tuple(lerp3(V(A_CAMP) + V((-0.55, 1.05, 0.25)), V(A_CAMP) + V((-0.12, 0.98, -0.32)), u)); P['lpalm'] = (0, 1.0, 0); P['lgrip'] = 0.2
        P['head'] = (lerp(0.55, -0.1, u), 0.0, 0.05); P['nod'] = 0.45 * u; P['twist'] = lerp(0.2, 0.0, u); P['eyes'] = 'sad' if u > 0.5 else 'open'; P['mouth'] = 'neutral'
    return P
def adv_camp_full(t):
    """with the bottle at the lips (needs the head position first)"""
    P = adv_camp(t); bottle = None
    if t < T_GULP[1] + 0.45:
        H_ = head_pose(ADV, P); m = mouth_pt(H_); fw = H_['_RH'] @ V((0, 0, 1.0)); upv = H_['_RH'] @ V((0, 1.0, 0))
        u = 1 - sm(seg01(t, T_GULP[1], T_GULP[1] + 0.45))
        tgt = m + fw * 0.13 + upv * 0.07; low = V(A_CAMP) + V((0.18, 0.85, -0.3))
        P['rh_w'] = tuple(lerp3(low, tgt, u)); P['rgrip'] = 0.85; P['rpalm'] = tuple(-(H_['_RW'] @ V((1.0, 0, 0))))
        bottle = dict(fill=max(0.0, 0.55 - 0.55 * seg01(t, 0.05, T_GULP[1])), tilt_to=m, u=u)
    return P, bottle
def kaya_camp(t):
    P = dict(base=K0, yaw=PI / 2 - 0.35, eyes='closed', mouth='neutral', brow=0.0, hair_sway=0.0)
    rise = sm(seg01(t, *T_RISE)); back = sm(seg01(t, T_RISE[0] + 0.3, T_RISE[1] + 0.5))
    if rise < 1:                                                                # dozing on her heels, arms over the knees
        c = 0.52 * (1 - rise); P.update(crouch=c, lean=0.35 * (1 - rise), nod=0.55 * (1 - sm(seg01(t, T_JOLT, T_JOLT + 0.18))))
        P['rf'] = (0.13, 0.07, 0.18 * (1 - rise)); P['lf'] = (-0.13, 0.07, 0.18 * (1 - rise))
        if rise < 0.3: P['rh'] = (0.12, 0.62, 0.32); P['lh'] = (-0.12, 0.62, 0.32); P['rgrip'] = P['lgrip'] = 0.5
    if t >= T_JOLT: P['eyes'] = 'wide'; P['brow'] = 0.6; P['mouth'] = 'o'
    base = lerp3(K0, K1, back); P['base'] = base
    face_a = ang_to(base, A_CAMP); P['yaw'] = lerp(PI / 2 - 0.35, face_a, sm(seg01(t, T_JOLT + 0.1, T_RISE[1])))
    if back > 0 and back < 1: P['walk'] = -back * 9.0; P['stride'] = 0.22
    d = sm(seg01(t, *T_DRAW))
    if t >= T_DRAW[0] - 0.3:                                                    # draws the sword and points it at him
        P['rh'] = lerp3((-0.12, 0.98, 0.12), (0.18, 1.22, 0.42), d); P['rgrip'] = 0.9; P['lh'] = (-0.22, 1.0, 0.25); P['lgrip'] = 0.3
        P['lean'] = -0.08 * d; P['brow'] = 0.9
    mt = talking(t, '02')
    if mt: P['mouth'] = mt
    P['hair_sway'] = 0.4 * math.sin(t * 5) * win(t, T_JOLT, T_RISE[1] + 0.6, 0.2)
    return P
def kaya_sword(P, t):
    d = sm(seg01(t, *T_DRAW)); RW = P['_RW']
    sheath_h = P['_pel'] + RW @ V((-0.2, -0.02, 0.06)); sheath_d = hd.nz(RW @ V((0.25, -1.0, -0.55)))
    if d <= 0.02: return hd.sword(sheath_h, sheath_d, RW @ V((1.0, 0, 0)), length=0.7)
    g = grip_pt(P, 'r', 0.06, 0.0); tgt = V(A_CAMP) + V((0, 1.2, 0))
    dirv = hd.nz(lerp3(sheath_d, hd.nz(tgt - g + V((0, 0.35, 0))), d))
    return hd.sword(g, dirv, P['_rpalm'], length=0.7)

# battle
A_BAT = (-0.45, 0.0, 2.15); SO = (0.62, 0.0, 2.35)
def adv_battle(t):
    P = dict(base=A_BAT, yaw=ang_to(A_BAT, SO) + 1.2, eyes='open', mouth='neutral', brow=-0.3, lean=0.05, cape_sway=0.3 * math.sin(t * 2))
    bottle = None; tb = T_BAT
    if t < tb + 1.2:
        H_ = head_pose(ADV, dict(P, nod=-0.3)); m = mouth_pt(H_); fw = H_['_RH'] @ V((0, 0, 1.0)); upv = H_['_RH'] @ V((0, 1.0, 0))
        u = win(t, tb - 0.5, tb + 1.2, 0.3); P['nod'] = -0.3 * u
        P['rh_w'] = tuple(lerp3(V(A_BAT) + V((0.2, 0.9, 0.15)), m + fw * 0.13 + upv * 0.07, u)); P['rgrip'] = 0.85; P['rpalm'] = tuple(-(H_['_RW'] @ V((1.0, 0, 0))))
        bottle = dict(fill=max(0.0, 0.5 - 0.5 * seg01(t, tb, tb + 0.9)), tilt_to=m, u=u)
        if u > 0.6: P['eyes'] = 'closed'
    r = sm(seg01(t, tb + 1.3, tb + 1.9))
    if r > 0:                                                                   # bends, offers his hand to the soldier
        P['yaw'] = lerp(P['yaw'], ang_to(A_BAT, SO), r); P['lean'] = 0.05 + 0.35 * r
        P['rh_w'] = tuple(lerp3(V(A_BAT) + V((0.2, 0.9, 0.15)), V(SO) + V((-0.45, 0.7, -0.1)), r)); P['rgrip'] = 0.25; P['rpalm'] = (0.3, 0.4, 0.0)
        P['mouth'] = 'smile' if t < T0['04'] + 1.3 else 'o'
        P['brow'] = -0.2 if t < T0['04'] + 1.3 else -0.8
    return P, bottle
def soldier_battle(t):
    P = dict(base=SO, yaw=ang_to(SO, A_BAT) - 0.55, crouch=0.8, lean=-0.32, eyes='half', mouth='neutral', brow=-0.2)
    P['rf'] = (0.14, 0.07, 0.62); P['lf'] = (-0.16, 0.07, 0.5); P['rkpole'] = (0.2, 1.0, 0.3); P['lkpole'] = (-0.2, 1.0, 0.3)
    P['rh'] = (0.32, 0.17, -0.05); P['lh'] = (-0.32, 0.2, -0.02); P['rpalm'] = (0, -1.0, 0); P['lpalm'] = (0, -1.0, 0); P['rgrip'] = P['lgrip'] = 0.3
    P['head'] = (0.0, 0.1, 0.0)
    lk = sm(seg01(t, T_BAT + 1.0, T_BAT + 1.5))
    P['eyes'] = 'open' if lk > 0.5 else 'half'
    bl = sm(seg01(t, ws('04', 0) + 1.05, ws('04', 0) + 1.5))                     # "...forgot his name": the blank stare, leans away
    if bl > 0:
        P['eyes'] = 'blank'; P['lean'] = -0.32 - 0.16 * bl; P['head'] = (-0.15 * bl, 0.12, -0.18 * bl); P['brow'] = 0.15; P['mouth'] = 'o' if bl < 0.99 or t < ws('04', 0) + 2.1 else 'neutral'
        P['lh'] = lerp3((-0.32, 0.2, -0.02), (-0.15, 0.62, 0.3), bl); P['lpalm'] = (0.2, 0.3, 1.0); P['lgrip'] = 0.1
    return P

# inn
A_INN = (0.32, 0.0, 2.2); IK_ = (0.0, 0.0, DOOR_Z + 0.12)
def adv_inn(t):
    P = dict(base=A_INN, yaw=0.08, eyes='open', mouth='neutral', brow=-0.1, lean=0.04)
    if t < T0['05'] - 0.05:                                                     # walks up to the door
        u = sm(seg01(t, T_INN, T0['05'] - 0.05)); P['base'] = lerp3((0.4, 0, 0.9), A_INN, u); P['walk'] = u * 7.0
    mt = None
    if t >= T0['05'] + 0.2: P['brow'] = -0.6; P['mouth'] = 'o' if t < T0['06'] else 'neutral'
    cl = sm(seg01(t, T0['06'] + 0.4, T0['06'] + 1.2))                           # door shut: head drops
    if cl > 0: P['nod'] = 0.35 * cl; P['eyes'] = 'sad'; P['brow'] = -0.9
    return P
def innk_inn(t):
    back = sm(seg01(t, T0['06'] - 0.4, T0['06'] + 0.1))
    P = dict(base=lerp3(IK_, (0.15, 0, DOOR_Z + 1.0), back), yaw=PI - 0.05, eyes='half', mouth='neutral', brow=0.6, lean=-0.03)
    P['rh'] = (-0.1, 1.13, 0.2); P['lh'] = (0.12, 1.1, 0.22); P['rpole'] = (1.0, -0.5, -0.3); P['lpole'] = (-1.0, -0.5, -0.3); P['rgrip'] = P['lgrip'] = 0.6
    P['rpalm'] = (0, 0, -1.0); P['lpalm'] = (0, 0, -1.0)
    if back > 0: P['walk'] = -back * 4.0
    mt = talking(t, '05')
    if mt: P['mouth'] = mt; P['head'] = (0.0, -0.08, 0.0)
    return P
def adv_label(t):
    tl = T_LAB; u = sm(seg01(t, tl - 0.2, tl + 0.55))
    P = dict(base=A_INN, yaw=lerp(0.08, PI - 0.35, u), eyes='sad', mouth='neutral', brow=-0.7, lean=0.04, nod=0.12)
    lift = sm(seg01(t, tl + 0.2, tl + 0.8))
    P['rh'] = lerp3((0.22, 0.85, 0.1), (0.06, 1.38, 0.36), lift); P['rgrip'] = 0.85; P['rpalm'] = (-1.0, 0, 0.0); P['head'] = (0.08, 0.0, 0.05)
    if t > T0['07'] + 1.0: P['eyes'] = 'wide' if t < T0['07'] + 1.5 else 'open'
    return P

# bridge (night -> pre-dawn)
M_ = (-2.95, 0.0, -1.75); A_KNEEL = (-2.3, 0.0, -1.95); MEET = (-2.62, 0.62, -2.02)
T_ARR = (T_BR + 0.1, T0['08'] + 2.25); T_KN = (T0['08'] + 2.25, T0['08'] + 2.75)
T_LIFT = (T0['09'] - 0.1, T0['09'] + 0.5); T_POUR = (T0['10'] - 0.1, T0['10'] + 0.4, ws('10', 1) - 0.1)
T_GLOW = (T0['10'] + 0.6, ws('10', 1) + 0.3); T_BLANK = (ws('10', 1) + 0.25, T0['11'] - 0.1)
T_WAKE = T0['11'] - 0.55; T_SIT = (T0['11'] - 0.3, T0['11'] + 0.45); T_GRAB = (T0['11'] + 0.3, T0['11'] + 0.75)
T_HORSE = (T0['13'] + 0.75, T0['13'] + 1.45); T_TURN = (T0['14'] + 0.2, tend('14') + 0.3)
def adv_bridge(t):
    P = dict(base=A_KNEEL, yaw=ang_to(A_KNEEL, M_) - 0.4, eyes='open', mouth='neutral', brow=-0.6, lean=0.12, cape_sway=0.0)
    if t < T_ARR[1]:                                                            # runs in from the road, through the rain
        u = seg01(t, *T_ARR); us = sm(u) * 0.7 + u * 0.3; st = (-0.6, 0, -6.2)
        P['base'] = lerp3(st, A_KNEEL, us); P['yaw'] = ang_to(st, A_KNEEL); P['walk'] = us * 14.0; P['stride'] = 0.42; P['lift'] = 0.16; P['lean'] = 0.22
        P['cape_sway'] = 0.9
    kn = sm(seg01(t, *T_KN))
    if t >= T_KN[0]:
        P['yaw'] = lerp(ang_to((-0.6, 0, -6.2), A_KNEEL), ang_to(A_KNEEL, M_) - 0.4, kn)
        kneel(P, 'l', 0.43 * kn); P['lean'] = 0.12 + 0.18 * kn
        P['brow'] = -0.9; P['mouth'] = 'o' if t < T0['09'] else 'neutral'
    # the last potion: lifted, looked at, looked at her
    lf = sm(seg01(t, *T_LIFT)) * (1 - sm(seg01(t, T_POUR[0] - 0.1, T_POUR[0] + 0.3)))
    if lf > 0:
        tr = 0.012 * math.sin(t * 31) * seg01(t, T_LIFT[1], T_LIFT[1] + 0.4)
        P['rh'] = lerp3((0.25, 0.7, 0.1), (0.12 + tr, 1.25, 0.38), lf); P['rgrip'] = 0.85; P['rpalm'] = (-1.0, 0.0, 0.0)
        look_b = 0.5 + 0.5 * math.sin((t - T_LIFT[1]) * 2.6) if t > T_LIFT[1] else 0.0
        P['head'] = (lerp(0.0, -0.55, look_b) * lf, 0.0, 0.0); P['nod'] = lerp(-0.05, 0.25, look_b) * lf
    pr = sm(seg01(t, T_POUR[0], T_POUR[1])) * (1 - sm(seg01(t, T_POUR[2], T_POUR[2] + 0.5)))
    if pr > 0:
        mp = mira_mouth(t); P['rh_w'] = tuple(lerp3(V(A_KNEEL) + V((0.15, 0.9, 0.2)), mp + V((0.12, 0.12, -0.06)), pr)); P['rgrip'] = 0.85; P['rpalm'] = (0.0, 0.0, 1.0)
        P['lh_w'] = tuple(V(mira_head(t)) + V((0.05, -0.12, 0.12))); P['lgrip'] = 0.4; P['lpalm'] = (-1.0, 0.2, 0.0); P['lean'] = 0.35; P['nod'] = 0.3
    bl = win(t, T_BLANK[0], T_BLANK[1], 0.3)
    if bl > 0:                                                                  # the light goes out of his eyes: head up, towards us
        P['nod'] = lerp(P.get('nod', 0.0), -0.08, bl); P['head'] = (-0.5 * bl, 0.0, 0.0); P['lean'] = lerp(P['lean'], 0.15, bl)
        if bl > 0.5: P['eyes'] = 'blank'; P['brow'] = 0.0; P['mouth'] = 'neutral'
    if t >= T_BLANK[1] - 0.1:                                                   # after: a polite stranger
        P['brow'] = 0.15; P['eyes'] = 'open'; P['mouth'] = 'neutral'; P['nod'] = 0.1; P['lean'] = 0.22
    if t >= T_GRAB[0]:
        g = sm(seg01(t, *T_GRAB)); P['lh_w'] = tuple(lerp3(V(A_KNEEL) + V((-0.25, 0.55, -0.1)), V(MEET), g)); P['lgrip'] = 0.3; P['lpalm'] = (0, 1.0, 0)
        P['head'] = (0.0, 0.0, 0.08)
    mt = talking(t, '12')
    if mt: P['mouth'] = mt; P['brow'] = 0.35
    if T0['12'] <= t < T0['13']: P['eyes'] = 'open'
    if t >= T_HORSE[0]:                                                         # takes the toy, turns it over, a kind smile
        h = sm(seg01(t, T_HORSE[1] - 0.2, T_TURN[0] + 0.4))
        P['lh_w'] = tuple(lerp3(V(MEET), V(A_KNEEL) + V((-0.2, 0.98, -0.3)), h)); P['lpalm'] = (0, 1.0, -0.2); P['lgrip'] = 0.25
        P['head'] = (lerp(0.0, -0.2, h), 0.0, 0.0); P['nod'] = 0.3 * h
        if t >= T_TURN[0] + 0.6: P['mouth'] = 'smile'; P['brow'] = 0.0; P['nod'] = lerp(0.3, 0.05, sm(seg01(t, tend('14') - 0.8, tend('14'))))
    return P
_MH = {}
def mira_pose(t):
    sit = sm(seg01(t, *T_SIT))
    P = dict(base=M_, yaw=PI - 0.45, crouch=0.82, lean=lerp(-0.75, -0.25, sit), eyes='closed', mouth='neutral', brow=-0.5, nod=lerp(-0.1, 0.05, sit))
    P['head'] = (lerp(-0.5, 0.15, sit), 0.0, lerp(0.25, 0.0, sit))
    P['rf'] = (0.16, 0.07, 0.68); P['lf'] = (-0.1, 0.07, 0.6); P['rkpole'] = (0.1, 1.0, 0.3); P['lkpole'] = (-0.1, 1.0, 0.3)
    P['rh'] = (0.28, 0.3, 0.1); P['lh'] = (0.05, 0.55, 0.2); P['lpalm'] = (0.4, 0, 1.0); P['rgrip'] = 0.4; P['lgrip'] = 0.4
    if t < T0['08'] + 1.5: P['eyes'] = 'half' if (t % 2.0) < 1.2 else 'closed'
    if t >= T0['09'] - 0.2 and t < T_WAKE: P['eyes'] = 'half'; P['head'] = (-0.2, 0.0, 0.15)
    if T_POUR[0] + 0.2 <= t < T_WAKE: P['eyes'] = 'closed'; P['head'] = (-0.05, -0.1, 0.1)
    if t >= T_WAKE:
        P['eyes'] = 'open'; P['brow'] = 0.2; P['mouth'] = 'smile'
    if t >= T_GRAB[0]:
        g = sm(seg01(t, *T_GRAB)); P['rh_w'] = tuple(lerp3(wpt(P, (0.28, 0.3, 0.1)), V(MEET) + V((-0.05, -0.02, 0.02)), g)); P['rgrip'] = 0.65
    mt = talking(t, '11')
    if mt: P['mouth'] = mt; P['eyes'] = 'wide'
    if t >= T0['12'] + 1.1:                                                     # "have we met?": the smile goes, she freezes
        f = sm(seg01(t, T0['12'] + 1.1, T0['12'] + 1.6)); P['mouth'] = 'o' if f < 0.99 else 'neutral'; P['eyes'] = 'wide'; P['brow'] = -0.4 * f
    if t >= T0['13']:
        P['brow'] = -0.8; P['eyes'] = 'sad'; P['mouth'] = 'neutral'
    if t >= T_HORSE[0]:                                                         # takes the horse from her belt, presses it into his palm
        u1 = sm(seg01(t, T_HORSE[0], T_HORSE[0] + 0.35)); u2 = sm(seg01(t, T_HORSE[0] + 0.35, T_HORSE[1])); u3 = sm(seg01(t, T_HORSE[1] + 0.1, T_HORSE[1] + 0.6))
        p_belt = (-0.18, 0.92, 0.12); p_give = loc(M_, P['yaw'], V(MEET) + V((0.03, 0.07, -0.02)))
        P['lh'] = lerp3(lerp3((0.05, 0.55, 0.2), p_belt, u1), p_give, u2); P['lh'] = lerp3(P['lh'], (0.05, 0.55, 0.2), u3); P['lgrip'] = 0.55; P['lpalm'] = (0, -1.0, 0.0)
        P['rh_w'] = tuple(lerp3(V(MEET) + V((-0.05, -0.02, 0.02)), wpt(P, (0.28, 0.3, 0.1)), u2)); P['rgrip'] = 0.4
    if t >= T0['14']: P['mouth'] = 'soft'; P['brow'] = -0.6; P['eyes'] = 'sad' if t < T0['14'] + 1.2 else 'half'
    return P
def loc(base, yaw, p): return tuple(hd.Ry(yaw).T @ (V(p, float) - V(base, float)))
def wpt(P, l): return V(P['base'], float) + hd.Ry(P['yaw']) @ V(l, float)
def mira_head(t):
    k = round(t * FPS)
    if k not in _MH:
        P = mira_pose(t); hd.human(MIRA, P); _MH.clear(); _MH[k] = P
    return _MH[k]['_head']
def mira_mouth(t):
    mira_head(t); P = _MH[round(t * FPS)]; return mouth_pt(P, 0.1, 0.05)

# dawn: he walks away along the deck, she calls after him
T_STOP = T0['15'] + 0.95
def adv_dawn(t):
    x0 = -3.3; sp = 0.95; ts = T_STOP; x = x0 + sp * (min(t, ts) - T_DAWN) + 0.25 * sm(seg01(t, ts, ts + 0.5))
    P = dict(base=(x, deck_y(x), 0.15), yaw=PI / 2 + 0.03, eyes='open', mouth='neutral', lean=0.05, cape_sway=0.4 * (1 - seg01(t, ts, ts + 1.2)))
    if t < ts + 0.4: P['walk'] = (x - x0) * 4.9; P['stride'] = 0.3
    else: P['head'] = (-0.22 * win(t, ts + 0.5, ts + 1.9, 0.4), 0.0, 0.0)        # a small turn of the head - not a turn back
    P['lh'] = (-0.12, 0.98, 0.3); P['lpalm'] = (0, 1.0, 0); P['lgrip'] = 0.4                                  # holds the toy
    return P
def mira_dawn(t):
    x = -6.0 + 0.45 * sm(seg01(t, T0['15'] - 0.1, T0['15'] + 0.5))
    P = dict(base=(x, deck_y(x), -0.2), yaw=PI / 2 + 0.08, eyes='open', brow=-0.5, mouth='neutral')
    c = win(t, T0['15'] - 0.1, tend('15') + 0.6, 0.3)
    P['rh'] = lerp3((0.24, 0.85, 0.05), (0.3, 1.5, 0.45), c); P['rpalm'] = (0, 0.2, 1.0); P['rgrip'] = 0.1
    mt = talking(t, '15')
    if mt: P['mouth'] = mt; P['eyes'] = 'wide'
    if t > tend('15') + 0.5: P['mouth'] = 'soft'; P['eyes'] = 'sad'
    return P

# ======================= camera =======================
def P3(keys): return look.Path(keys)
CAM = {
 'camp': (P3([(0.0, (-0.3, 1.02, 1.08)), (1.3, (-0.22, 1.05, 1.0)), (T_JOLT + 0.6, (0.2, 1.22, 0.55)), (T0['02'], (0.15, 1.3, 0.2)), (tend('02'), (-0.05, 1.32, 0.15)),
              (T0['03'] - 0.3, (-0.2, 1.36, 0.7)), (T0['03'] + 0.4, (-0.25, 1.42, 1.08)), (T_BAT, (-0.34, 1.45, 1.12))]),
          P3([(0.0, (0.02, 1.2, 1.95)), (1.3, (-0.02, 1.18, 1.97)), (T_JOLT + 0.6, (-0.45, 1.0, 2.2)), (T0['02'], (-0.7, 1.05, 2.4)), (tend('02'), (-0.72, 1.05, 2.38)),
              (T0['03'] - 0.3, (-0.3, 1.02, 1.85)), (T0['03'] + 0.4, (-0.12, 1.0, 1.68)), (T_BAT, (-0.12, 0.98, 1.66))]),
          P3([(0.0, 44.0), (T_JOLT + 0.6, 46.0), (T0['03'] - 0.3, 44.0), (T0['03'] + 0.4, 32.0), (T_BAT, 30.0)])),
 'battle': (P3([(T_BAT, (0.5, 1.45, -0.45)), (T0['04'] + 0.8, (0.35, 1.25, 0.25)), (T_INN, (0.55, 1.0, 0.85))]),
            P3([(T_BAT, (-0.25, 1.25, 2.15)), (T0['04'] + 0.8, (0.05, 1.0, 2.25)), (T_INN, (0.5, 0.78, 2.35))]),
            P3([(T_BAT, 44.0), (T_INN, 38.0)])),
 'inn': (P3([(T_INN, (-1.2, 1.6, -0.5)), (T0['05'], (-0.75, 1.55, 0.6)), (T0['06'], (-0.7, 1.52, 0.75)), (T0['06'] + 1.0, (-0.45, 1.45, 1.0)), (T_LAB, (-0.4, 1.45, 1.05))]),
         P3([(T_INN, (0.2, 1.3, 2.6)), (T0['05'], (0.05, 1.5, 3.0)), (T0['06'], (0.05, 1.48, 3.0)), (T0['06'] + 1.0, (0.3, 1.42, 2.3)), (T_LAB, (0.32, 1.42, 2.25))]),
         P3([(T_INN, 46.0), (T0['05'], 42.0), (T_LAB, 44.0)])),
 'label': (P3([(T_LAB, (0.0, 1.5, 1.05)), (T0['07'] + 1.0, (0.1, 1.48, 1.2)), (T_BR, (0.15, 1.47, 1.28))]),
           P3([(T_LAB, (0.3, 1.42, 2.15)), (T0['07'] + 1.0, (0.3, 1.42, 2.15)), (T_BR, (0.3, 1.43, 2.15))]),
           P3([(T_LAB, 40.0), (T_BR, 34.0)])),
}
def cam_bridge(t):
    """bridge: wide establishing -> two-shot -> close on him with the bottle -> his face as the light goes -> her waking -> two-shot"""
    k = [  # (time, camera, target, fov)
        (T_BR, (2.6, 2.4, -7.2), (-2.0, 0.6, -1.8), 52.0),
        (T0['08'] + 1.6, (0.2, 1.7, -5.5), (-2.2, 0.8, -2.2), 46.0),
        (T_KN[1], (-1.6, 1.3, -4.3), (-2.6, 0.8, -1.9), 44.0),
        (T0['09'] + 0.3, (-3.1, 1.22, -2.55), (-2.45, 1.18, -1.97), 38.0),
        (T0['10'] + 0.4, (-3.25, 1.05, -3.45), (-2.65, 0.78, -1.85), 44.0),
        (ws('10', 1) - 0.1, (-3.05, 1.18, -2.45), (-2.42, 1.15, -1.97), 31.0),
        (T0['11'] - 0.2, (-3.0, 1.17, -2.5), (-2.42, 1.14, -1.97), 31.0),
        (T0['11'] + 0.15, (-2.62, 0.92, -2.62), (-2.98, 0.72, -1.7), 38.0),
        (T0['11'] + 0.8, (-2.57, 0.88, -2.6), (-3.0, 0.7, -1.68), 38.0),
        (T0['12'], (-3.08, 1.2, -2.5), (-2.43, 1.15, -1.97), 33.0),
        (tend('12'), (-3.1, 1.2, -2.52), (-2.43, 1.15, -1.97), 32.0),
        (T0['13'] + 0.3, (-2.55, 0.98, -2.8), (-2.85, 0.75, -1.7), 40.0),
        (T_HORSE[1], (-3.1, 1.0, -3.05), (-2.6, 0.78, -1.9), 40.0),
        (T0['14'] + 0.6, (-3.1, 1.2, -2.6), (-2.45, 1.08, -1.97), 36.0),
        (T_DAWN, (-3.35, 1.25, -3.3), (-2.6, 0.85, -1.85), 42.0)]
    keys_p = [(a, p) for a, p, _, _ in k]; keys_t = [(a, q) for a, _, q, _ in k]; fov = [(a, f) for a, _, _, f in k]
    return P3(keys_p)(t), P3(keys_t)(t), P3(fov)(t)
_CB = None
def cam_dawn(t):
    ax = adv_dawn(t)['base'][0]; mx = -6.0
    pos = P3([(T_DAWN, (-7.5, deck_y(-7.0) + 1.55, -0.85)), (T_STOP, (-7.25, deck_y(-7.0) + 1.55, -0.8)), (DUR, (-6.4, deck_y(-6.4) + 1.6, -0.62))])(t)
    tgt = P3([(T_DAWN, (-3.2, deck_y(-3.2) + 1.0, 0.1)), (T_STOP, (-2.4, deck_y(-2.4) + 1.1, 0.15)), (DUR, (-2.2, deck_y(-2.2) + 1.2, 0.15))])(t)
    fov = P3([(T_DAWN, 44.0), (T_STOP, 40.0), (DUR, 30.0)])(t)
    return pos, tgt, fov
def cam_shot(t):
    sc = scene(t)
    if sc == 'ring': sc = 'camp'
    if sc in CAM: p, q, f = CAM[sc]; return p(t), q(t), f(t)
    if sc == 'bridge': return cam_bridge(t)
    return cam_dawn(t)

# ======================= render =======================
_SETS = {}
def get_set(name):
    if name not in _SETS: _SETS[name] = {'camp': camp_set, 'battle': battle_set, 'inn': inn_set, 'bridge': bridge_set}[name]()
    return _SETS[name]
def potion_in_hand(P, key, b=None, glow=1.0, fill=0.6):
    g = grip_pt(P, key, 0.07, 0.035)
    if b is not None and b.get('u', 0) > 0.05:
        u = hd.nz(b['tilt_to'] - g); upv = hd.nz(lerp3(V((0, 1.0, 0)), u * -1.0 + V((0, 0.0, 0)), b['u'])) if False else hd.nz(lerp3(V((0, 1.0, 0)), u, b['u']))
        R = up_R(upv); base = g - upv * 0.03
        return hd.potion(base, R, fill=b['fill'], glow=glow), g
    R = up_R(V((0, 1.0, 0)) + V(P['_' + key + 'dir']) * 0.2); return hd.potion(g - V((0, 0.04, 0)), R, fill=fill, glow=glow), g
def wound(P, col=(120, 20, 24), glow=0.0, side=1):
    RW = P['_RW']; c = P['_chest'] + RW @ V((side * 0.09, -0.12, 0.1)); n = RW @ V((side * 0.5, 0, 1.0))
    Q = hd.poly_decal(c, n, RW @ V((0, 1.0, 0)), [(-0.025, -0.02), (0.0, -0.03), (0.03, -0.006), (0.02, 0.025), (-0.012, 0.03), (-0.03, 0.006)], hd.shade(col, 0.8), lift=0.012)
    if glow > 0.02:
        Q += hd.poly_decal(c, n, RW @ V((0, 1.0, 0)), [(-0.07 * glow, -0.05 * glow), (0.07 * glow, -0.05 * glow), (0.07 * glow, 0.06 * glow), (-0.07 * glow, 0.06 * glow)], (255, 226, 140), emit=True, lift=0.018)
    return Q
def world(t, cam_pos, cam):
    sc = scene(t); L = []; layers = []; fog = (14, 16, 26); amb = 0.32; fs, fe = 9, 34
    if sc == 'camp':
        layers.append(get_set('camp')); fl = 1 + 0.12 * math.sin(t * 9) + 0.06 * math.sin(t * 23)
        layers.append(fire_faces(t)); L += [((FIRE[0], 0.55, FIRE[2]), (255, 150, 70), 2.3 * fl), ((-6, 9, -2), (110, 130, 200), 1.0), ((0.5, 2.0, -1.5), (120, 120, 160), 0.6)]
        P, b = adv_camp_full(t); layers.append(hd.human(ADV, P))
        heal = win(t, T_HEAL - 0.1, T_HEAL + 0.9, 0.3)
        if t < T_HEAL + 0.6: layers.append(wound(P, glow=heal))
        if b: Qb, gp = potion_in_hand(P, 'r', b, glow=1.0); layers.append(Qb); L.append((tuple(gp), (255, 60, 60), 0.9 * b['u']))
        else:
            g = P['_pel'] + P['_RW'] @ V((0.17, 0.0, 0.08)); layers.append(hd.potion(g, hd.Rz(0.2), fill=0.0, glow=0.0, glass=(120, 132, 140), scale=0.75))    # the empty bottle tucked in the belt
        if heal > 0: L.append((tuple(P['_chest'] + V((0, 0, -0.3))), (255, 90, 80), 1.6 * heal))
        K = kaya_camp(t); layers.append(hd.human(KAYA, K)); layers.append(kaya_sword(K, t))
        fog = (12, 14, 24); amb = 0.34
    elif sc == 'battle':
        layers.append(get_set('battle')); layers.append(battle_fx(t)); fog = (128, 124, 118); amb = 0.55; fs, fe = 5, 26
        L += [((-3, 7, -4), (230, 224, 214), 1.6), ((2, 1, 9), (255, 150, 80), 1.2)]
        P, b = adv_battle(t); layers.append(hd.human(ADV, P))
        if b: Qb, gp = potion_in_hand(P, 'r', b); layers.append(Qb)
        layers.append(hd.human(SOLDIER, soldier_battle(t)))
        layers.append(hd.sword(V(SO) + V((0.55, 0.05, -0.15)), (0.2, 0.02, -1.0), (0, 1.0, 0), length=0.75))
    elif sc in ('inn', 'label'):
        layers.append(get_set('inn')); dl, shut = door_leaf(t); layers.append(dl)
        lan = 1 + 0.05 * math.sin(t * 6)
        L += [((0.95, 1.85, DOOR_Z - 0.6), (255, 196, 120), 0.9 * lan), ((-7, 10, -3), (110, 130, 200), 0.9)]
        if shut < 1: L.append(((0.0, 1.4, DOOR_Z + 0.5), (255, 180, 100), 1.3 * (1 - shut)))
        if shut < 0.98:
            Q_ = [hd.face([(-0.6, 0.004, DOOR_Z), (0.6, 0.004, DOOR_Z), (0.95, 0.004, DOOR_Z - 2.0 * (1 - shut)), (-0.95, 0.004, DOOR_Z - 2.0 * (1 - shut))], (186, 140, 84), emit=True)]
            layers.append([q for q in Q_ if q])
        if sc == 'inn':
            P = adv_inn(t); layers.append(hd.human(ADV, P)); layers.append(hd.human(INNK, innk_inn(t)))
        else:
            P = adv_label(t); layers.append(hd.human(ADV, P)); Qb, gp = potion_in_hand(P, 'r', None, glow=1.0, fill=0.7); layers.append(Qb)
            L.append((tuple(gp + V((0, 0, -0.2))), (255, 70, 70), 0.9))
        fog = (14, 18, 30); amb = 0.34
    else:
        layers.append(get_set('bridge'))
        if sc == 'bridge':
            dawn = sm(seg01(t, T0['11'] - 0.5, T_DAWN)); rain = 1 - sm(seg01(t, T0['11'] - 1.0, T0['13']))
        else:
            dawn = 1.0; rain = 0.0
        fog = mixc((16, 22, 36), (196, 150, 120) if sc == 'dawn' else (78, 84, 106), dawn); amb = lerp(0.3, 0.36, dawn)
        lq, lp = lantern_faces(1.0 - 0.7 * dawn); layers.append(lq)
        L += [((8, 10, -7), mixc((130, 150, 215), (210, 200, 210), dawn), 1.7), (lp, (255, 190, 110), 1.4 * (1 - 0.6 * dawn))]
        if dawn > 0: L.append(((24, 3, 0), (255, 196, 140), 2.2 * dawn))
        if sc == 'dawn':
            layers.append(sky_disc((22, 3.2, 1.6), 1.5, (255, 236, 190)))
            A = adv_dawn(t); layers.append(hd.human(ADV, A)); Mi = mira_dawn(t); layers.append(hd.human(MIRA, Mi))
            layers.append(hd.wooden_horse(grip_pt(A, 'l', 0.06, 0.03), hd.Ry(PI / 2), scale=1.2))
        else:
            layers.append(sky_disc((-12, 15, 30), 1.2, (210, 220, 240)) if dawn < 0.5 else [])
            A = adv_bridge(t); layers.append(hd.human(ADV, A))
            Mi = mira_pose(t); layers.append(hd.human(MIRA, Mi))
            gl = win(t, T_GLOW[0], T_GLOW[1], 0.35)
            if t < T_GLOW[1] - 0.2: layers.append(wound(Mi, col=(130, 18, 22), glow=gl, side=-1))
            if gl > 0: L.append((tuple(Mi['_chest'] + V((0, 0, -0.35))), (255, 214, 130), 1.0 * gl))
            # the last potion: from the belt, lifted, poured
            if t < T_LIFT[0]:
                g = A['_pel'] + A['_RW'] @ V((0.17, 0.0, 0.08)); layers.append(hd.potion(g, np.eye(3), fill=0.7, glow=0.8, scale=0.9))
            elif t < T_POUR[2] + 0.5:
                pr = sm(seg01(t, T_POUR[0], T_POUR[1]))
                b = dict(u=pr, tilt_to=mira_mouth(t), fill=0.7 * (1 - seg01(t, T_POUR[1], T_POUR[2])))
                Qb, gp = potion_in_hand(A, 'r', b if pr > 0.05 else None, glow=1.0, fill=0.7); layers.append(Qb)
                L.append((tuple(gp + V((0, 0.1, -0.15))), (255, 60, 60), 0.5))
            if t >= T_HORSE[0] + 0.35:
                hand_ = 'l'
                if t < T_HORSE[1]: hp = grip_pt(Mi, 'l', 0.06, -0.03); Rh = hd.Ry(1.2)
                else:
                    hp = grip_pt(A, 'l', 0.05, 0.04); sp = sm(seg01(t, *T_TURN)); Rh = hd.Ry(1.2 + 2.4 * sp) @ hd.Rz(0.5 * math.sin(PI * sp))
                layers.append(hd.wooden_horse(hp, Rh, scale=1.2))
            layers.append(rain_faces(cam, t, rain))
        fs, fe = (9, 42) if sc == 'bridge' else (14, 70)
    return layers, L, fog, amb, fs, fe

GRADE = {'camp': np.array([1.04, 0.98, 0.94]), 'battle': None, 'inn': np.array([1.02, 0.98, 0.96]), 'label': np.array([1.02, 0.98, 0.96]),
         'bridge': np.array([0.92, 0.98, 1.08]), 'dawn': np.array([1.06, 1.0, 0.92])}
def frame_low(t):
    pos, tgt, fov = cam_shot(t); cam = Camera.look(tuple(pos), tuple(tgt)); sc = scene(t)
    layers, L, fog, amb, fs, fe = world(t, pos, cam)
    R = Renderer(W, H, fog=fog)
    img, vi, zb = zrender(R, cam, layers, L, fov=fov, fog_start=fs, fog_end=fe, ambient=amb, return_z=True)
    a = look.outline(np.asarray(img).astype(np.float32), zb)
    if sc == 'battle':
        l = a.mean(axis=2, keepdims=True); a = (l * 0.75 + a * 0.25) * np.array([1.0, 0.98, 0.95])
    elif sc == 'bridge':
        dawn = sm(seg01(t, T0['11'] - 0.5, T_DAWN)); a = a * (GRADE['bridge'] * (1 - dawn) + np.array([1.0, 0.99, 0.97]) * dawn)
    elif GRADE.get(sc) is not None: a = a * GRADE[sc]
    a = np.clip((a - 112) * 1.12 + 110, 0, 255)
    return post.ps1(Image.fromarray(a.astype(np.uint8)), levels=6), vi

# ======================= 2D overlays: ring portrait, label, HUD =======================
def _px(d, x, y, w, h, c): d.rectangle([x, y, x + w - 1, y + h - 1], fill=c)
def portrait_img():
    """young Mira holding the wooden horse, painted in the ring: 64x80 pixel art, drawn once"""
    im = Image.new('RGBA', (64, 80), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([0, 0, 63, 79], fill=(238, 214, 168, 255))
    d.ellipse([3, 3, 60, 76], fill=(214, 186, 142, 255))
    d.rectangle([14, 52, 50, 79], fill=(84, 110, 150, 255))                          # dress
    d.ellipse([18, 12, 46, 46], fill=(156, 74, 40, 255))                             # hair back
    d.ellipse([21, 17, 43, 45], fill=(236, 196, 164, 255))                           # face
    d.rectangle([19, 13, 45, 22], fill=(170, 82, 44, 255))                           # fringe
    d.rectangle([17, 22, 21, 52], fill=(156, 74, 40, 255)); d.rectangle([43, 22, 47, 52], fill=(156, 74, 40, 255))
    _px(d, 26, 29, 3, 3, (40, 30, 26, 255)); _px(d, 36, 29, 3, 3, (40, 30, 26, 255))
    d.arc([27, 33, 38, 41], 20, 160, fill=(150, 60, 60, 255), width=2)
    _px(d, 24, 35, 3, 2, (232, 150, 140, 255)); _px(d, 38, 35, 3, 2, (232, 150, 140, 255))
    hc = (184, 128, 74, 255); hk = (130, 88, 52, 255)                                # the wooden horse in her arms
    d.rectangle([24, 56, 40, 63], fill=hc); d.rectangle([38, 49, 43, 58], fill=hc); d.rectangle([40, 46, 48, 51], fill=hc)
    _px(d, 39, 47, 2, 6, hk); _px(d, 45, 47, 1, 1, (30, 20, 14, 255))
    for x in (25, 29, 35, 38): _px(d, x, 63, 2, 6, hc)
    _px(d, 21, 56, 3, 5, hk)
    d.rectangle([18, 58, 26, 62], fill=(236, 196, 164, 255)); d.rectangle([40, 59, 47, 63], fill=(236, 196, 164, 255))   # hands
    return im
PORTRAIT = portrait_img()
def ring_overlay(im, t):
    a, b = T0['03'] + 0.15, T_BAT - 0.12
    if not (a <= t < b): return
    u = sm(seg01(t, a, a + 0.3)) * (1 - sm(seg01(t, b - 0.12, b)))
    if u < 0.02: return
    cx, cy = 540, 700; rx, ry = int(230 * u), int(285 * u)
    if rx < 8: return
    d = ImageDraw.Draw(im)
    d.ellipse([cx - rx - 28, cy - ry - 28, cx + rx + 28, cy + ry + 28], fill=(0, 0, 0))
    d.ellipse([cx - rx - 20, cy - ry - 20, cx + rx + 20, cy + ry + 20], fill=(226, 178, 64))
    d.ellipse([cx - rx - 8, cy - ry - 8, cx + rx + 8, cy + ry + 8], fill=(150, 108, 34))
    p = PORTRAIT.resize((max(1, 2 * rx), max(1, 2 * ry)), Image.NEAREST); im.paste(p, (cx - rx, cy - ry), p)
    for k in range(10):                                                          # little gold beads on the frame
        an = 2 * PI * k / 10 + 0.3; x = cx + (rx + 14) * math.cos(an); y = cy + (ry + 14) * math.sin(an); d.rectangle([x - 6, y - 6, x + 6, y + 6], fill=(255, 224, 120))
def text_w(s, sc): return len(s) * 6 * sc - sc
def label_overlay(im, t):
    a, b = T0['07'] - 0.05, T_BR - 0.08
    if not (a <= t < b): return
    u = sm(seg01(t, a, a + 0.3)); w2 = int(380 * u); h2 = int(230 * u)
    if w2 < 10: return
    cx, cy = 540, 640; d = ImageDraw.Draw(im)
    d.rectangle([cx - w2 - 14, cy - h2 - 14, cx + w2 + 14, cy + h2 + 14], fill=(0, 0, 0))
    d.rectangle([cx - w2, cy - h2, cx + w2, cy + h2], fill=(226, 208, 164))
    for k in range(0, 2 * h2, 24): d.rectangle([cx - w2, cy - h2 + k, cx + w2, cy - h2 + k + 3], fill=(214, 194, 150))
    d.rectangle([cx - w2 + 16, cy - h2 + 16, cx + w2 - 16, cy - h2 + 22], fill=(150, 40, 40)); d.rectangle([cx - w2 + 16, cy + h2 - 22, cx + w2 - 16, cy + h2 - 16], fill=(150, 40, 40))
    if u > 0.95:
        r2 = sm(seg01(t, ws('07', 0) + 0.9, ws('07', 0) + 1.2))
        for s, y, c, vis in (('A LIFE RESTORED.', cy - 95, (60, 40, 30), 1.0), ('A BOND FORGOTTEN.', cy + 25, (170, 30, 30), r2)):
            if vis < 0.5: continue
            sc = 7; look.draw_cells(d, look.text_cells(s, int(cx - text_w(s, sc) / 2), y, sc, c), 0)
def hud_overlay(im, t):
    a = T0['16'] - 0.3
    if t < a or t >= T_BLACK: return
    d = ImageDraw.Draw(im); u = seg01(t, a, a + 0.25)
    s1 = 'QUEST COMPLETE'; sc = 9 if u >= 1 else 11
    look.draw_cells(d, look.text_cells(s1, int(540 - text_w(s1, sc) / 2), 150, sc, (255, 210, 90)), 4)
    if t >= a + 0.9:
        s2 = 'MEMORY LOST'; sc2 = 8; flick = (int(t * 10) % 2 == 0) or t > a + 1.4
        if flick: look.draw_cells(d, look.text_cells(s2, int(540 - text_w(s2, sc2) / 2), 270, sc2, (255, 90, 80)), 4)
COL = {'N': (242, 238, 226), 'K': (255, 190, 90), 'M': (255, 190, 90), 'I': (190, 190, 196), 'A': (120, 230, 255)}
SUBS = look.Subtitles(SCR, LINES, W, H, S, COL, title_key='-none-', n=17,
                      hil={'FORGET', 'TRICK', 'SOLDIER', 'NAME.', 'FACE.', 'LABEL', 'MIRA,', 'DYING.', 'SAVE', 'WHO.', 'EVERYTHING.', 'BELIEVE', 'NEW', 'BOTH'})
def frame_final(t):
    if t >= T_BLACK: return np.zeros((H * S, W * S, 3), np.float32)
    img, vi = frame_low(t); arr = post.upscale(img, S)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); ring_overlay(im, t); label_overlay(im, t); hud_overlay(im, t)
    arr = np.asarray(im).astype(np.float32)
    return SUBS.apply(arr, t)
def frame(t): return Image.fromarray(np.clip(frame_final(t), 0, 255).astype(np.uint8)).resize((W, H), Image.BOX)

TEST = os.environ.get('TEST')
if TEST and __name__ == '__main__':
    ts = [float(x) for x in TEST.split(',')] if TEST != 'all' else [round(x, 2) for x in np.arange(0, DUR, float(os.environ.get('STEP', '0.5')))]
    ims = [Image.fromarray(np.clip(frame_final(x), 0, 255).astype(np.uint8)).resize((270, 480), Image.LANCZOS) for x in ts]
    per = int(os.environ.get('PER', '8')); rows = (len(ims) + per - 1) // per; shp = Image.new('RGB', (min(per, len(ims)) * 272, rows * 498), (30, 30, 30))
    dd = ImageDraw.Draw(shp)
    for i, (im, x) in enumerate(zip(ims, ts)): shp.paste(im, ((i % per) * 272, (i // per) * 498)); dd.text(((i % per) * 272 + 4, (i // per) * 498 + 483), f'{x:.2f}', fill=(255, 255, 0))
    shp.save(os.environ.get('TEST_OUT', 'test_fpo.png')); print('test written', DUR); sys.exit()

# ======================= QA manifest =======================
QA = dict(fps=FPS, dur=DUR, W=W, frame=frame, chars={}, geom=lambda t, name, st, V_: [], camera=lambda t: cam_shot(t)[0], min_cam_dist=0.3,
          camera_ok=lambda p: True, allow_jump=[], weapon_events=[],
          scenes=[dict(id='camp', t0=0.0, t1=T_BAT, action='frame 0: he gulps a glowing red potion; Kaya wakes, recoils, draws; he reaches out; the ring portrait'),
                  dict(id='battle', t0=T_BAT, t1=T_INN, action='flashback: he drinks; the soldier he saved stares blankly'),
                  dict(id='inn', t0=T_INN, t1=T_LAB, action='the innkeeper blocks the door, then shuts it'),
                  dict(id='label', t0=T_LAB, t1=T_BR, action='the bottle label: A LIFE RESTORED. A BOND FORGOTTEN.'),
                  dict(id='bridge', t0=T_BR, t1=T_DAWN, action='rain, the bridge: Mira dying; the last potion; his eyes go out; she wakes; the horse'),
                  dict(id='dawn', t0=T_DAWN, t1=DUR, action='dawn: he walks away along the bridge, she calls, he stops; QUEST COMPLETE - MEMORY LOST; cut to black')],
          texts=lambda: [('hud', 'QUEST COMPLETE', 9), ('hud', 'MEMORY LOST', 8), ('label', 'A BOND FORGOTTEN.', 7)])

# ======================= AUDIO =======================
LVL = {'02': 1.0, '05': -0.5, '11': 0.5, '12': -1.0, '15': 1.5}
def build_audio(path):
    import soundfile as _sf
    s = Sound(DUR, loop=False, seed=77); sr = s.sr; n = s.n; t = s.t
    BED = np.zeros(n); FX = np.zeros(n); MUS = np.zeros(n)
    def put(buf, x, t0, v=1.0):
        i = int(t0 * sr)
        if i >= n or i + len(x) <= 0: return
        if i < 0: x = x[-i:]; i = 0
        j = min(n, i + len(x)); buf[i:j] += (x * v)[:j - i]
    def nb(t0, d, lo, hi, v, seed, shape=2, buf=None): put(FX if buf is None else buf, s.filt_short(s.noise(d, seed), lo=lo, hi=hi) * np.sin(np.pi * s.T(d) / d) ** shape, t0, v)
    def tone(t0, m, d, v, dec=3.0, att=0.005, glide=0.0, buf=None, harm=(1.0,)):
        f = 440 * 2 ** ((m - 69) / 12); tt = s.T(d); fr = f * (1 + glide * tt / d); ph = np.cumsum(fr) / sr
        x = sum(a * np.sin(2 * np.pi * ph * (k + 1)) for k, a in enumerate(harm))
        put(FX if buf is None else buf, x * np.minimum(1, tt / att) * np.exp(-tt * dec), t0, v)
    def mask(a, b, r=0.15): return np.clip(np.minimum((t - a) / r, (b - t) / r), 0, 1)
    def thud(t0, f=60, v=0.1, d=0.3): tt = s.T(d); put(FX, np.sin(2 * np.pi * f * tt * (1 - 0.3 * tt / d)) * np.exp(-tt * 14), t0, v)
    def heart(t0, v=0.12): thud(t0, 52, v, 0.25); thud(t0 + 0.22, 46, v * 0.7, 0.25)
    def clink(t0, v=0.03, seed=0):
        for k, f in enumerate((2900, 4100, 5300)): tt = s.T(0.3); put(FX, np.sin(2 * np.pi * f * (1 + 0.01 * hsh(seed + k)) * tt) * np.exp(-tt * (18 + 5 * k)), t0 + k * 0.03, v * (1 - 0.25 * k))
    def gulp(t0, v=0.06):
        for k in range(3): tt = s.T(0.14); put(FX, np.sin(2 * np.pi * (180 - 60 * tt / 0.14) * tt) * np.sin(np.pi * tt / 0.14) ** 2, t0 + k * 0.22, v)
    def shimmer(t0, d=1.0, v=0.025, base=84):
        for k in range(7): tone(t0 + k * d / 9, base + [0, 4, 7, 12, 16, 19, 24][k], 0.9, v * (1 - k * 0.08), dec=3.5)
    def step(t0, v=0.03, seed=0, wet=False):
        tt = s.T(0.12); put(FX, s.filt_short(s.noise(0.12, seed), lo=150, hi=1800 if not wet else 4000) * np.exp(-tt * 30) + np.sin(2 * np.pi * 75 * tt) * np.exp(-tt * 26) * 0.3, t0, v)
    def piano(t0, m, v=0.06, d=3.0):
        tone(t0, m, d, v, dec=1.3, harm=(1.0, 0.45, 0.2, 0.08)); tone(t0 + 0.002, m + 12, d, v * 0.15, dec=2.0)
    # ---- CAMP: fire, crickets, the gulp, the heal, Kaya wakes, the sword, the ring
    camp = mask(-1, T_BAT, 0.02)
    BED += soft_fire(s, level=0.02, mask=camp, seed=7)
    for k in range(int(T_BAT / 0.45)):
        tb = 0.2 + k * 0.45 + 0.2 * hsh(k, 3)
        for j in range(3): tt = s.T(0.03); put(BED, np.sin(2 * np.pi * 4300 * tt) * np.sin(np.pi * tt / 0.03), tb + j * 0.06, 0.004)
    clink(0.02, 0.025); gulp(0.12, 0.07)
    shimmer(T_HEAL - 0.05, 0.9, 0.03, 81); nb(T_HEAL, 0.9, 2000, 9000, 0.012, 11, 1)
    nb(T_JOLT, 0.35, 300, 2500, 0.05, 12, 1)
    for k in range(4): step(T_RISE[0] + 0.35 + k * 0.28, 0.035, 20 + k)
    nb(T_DRAW[0], 0.4, 2500, 8000, 0.05, 13, 1); tone(T_DRAW[0] + 0.32, 98, 1.1, 0.025, dec=3.0, harm=(1.0, 0.5, 0.3))
    tone(T0['03'] + 0.12, 103, 0.15, 0.03, dec=30)                                                               # ring click
    for k, m in enumerate((76, 79, 83)): tone(T0['03'] + 0.25 + k * 0.12, m, 2.2, 0.018, dec=1.6, harm=(1.0, 0.3))   # a soft bell chord on the portrait
    # ---- BATTLE (flashback): clangs, distant shouts, drums, the gulp; muffled
    bat = mask(T_BAT, T_INN, 0.03)
    BED += s.filt(s.rng.normal(0, 1, n), lo=80, hi=900) * 0.03 * bat * (0.6 + 0.4 * np.sin(2 * np.pi * t * 0.7))
    for k, dt in enumerate((0.0, 0.35, 0.9, 1.6, 2.3)): clink(T_BAT + dt, 0.04 * (1.0 if k < 2 else 0.5), seed=30 + k); nb(T_BAT + dt, 0.15, 400, 3000, 0.03, 40 + k, 1)
    for k in range(6): thud(T_BAT + 0.2 + k * 0.5, 55, 0.07)
    for k in range(3): nb(T_BAT + 0.6 + k * 0.8, 0.6, 300, 1200, 0.025, 50 + k, 2)
    gulp(T_BAT + 0.3, 0.05); tone(ws('04', 0) + 1.2, 52, 2.2, 0.05, dec=1.2, harm=(1.0, 0.5))
    # ---- INN: tavern murmur through the open door, creak, slam, muffled after
    inn = mask(T_INN, T_BR, 0.03); shut = np.clip((t - (T0['06'] + 0.45)) / 0.05, 0, 1)
    mur = s.filt(s.rng.normal(0, 1, n), lo=250, hi=1400) * (0.6 + 0.4 * s.filt(s.rng.normal(0, 1, n), hi=3) * 20)
    BED += mur * 0.035 * inn * (1 - 0.8 * shut)
    for k in range(5): tone(T_INN + 0.3 + k * 0.6 + 0.2 * hsh(k, 6), 72 + 3 * (k % 3), 0.18, 0.006, dec=8)        # mugs clinking far
    for k in range(4): step(T_INN + 0.15 + k * 0.4, 0.035, 60 + k)
    s_creak = s.T(0.5); put(FX, np.sin(2 * np.pi * (520 + 160 * np.sin(s_creak * 22)) * s_creak) * np.exp(-s_creak * 4) * np.sin(np.pi * s_creak / 0.5), T0['06'] - 0.05, 0.03)
    thud(T0['06'] + 0.45, 70, 0.16, 0.4); nb(T0['06'] + 0.45, 0.2, 100, 1200, 0.06, 71, 1)
    BED += s.filt(s.rng.normal(0, 1, n), lo=60, hi=400) * 0.02 * inn                                               # night air
    piano(ws('07', 0) + 1.0, 45, 0.06, 3.5)                                                                     # the label's second line
    # ---- BRIDGE: rain, thunder, running steps, heartbeat, pour, the heal, the light going out
    br = mask(T_BR, T_DAWN, 0.03); rain = br * (1 - np.clip((t - (T0['11'] - 1.0)) / (T0['13'] - T0['11'] + 1.0), 0, 1))
    BED += s.filt(s.rng.normal(0, 1, n), lo=900, hi=8000) * 0.05 * rain
    BED += s.filt(s.rng.normal(0, 1, n), lo=150, hi=900) * 0.02 * rain
    for k in range(int((T_DAWN - T_BR) * 9)): tb = T_BR + k / 9 + 0.1 * hsh(k, 8); put(BED, np.sin(2 * np.pi * (1800 + 1500 * hsh(k, 9)) * s.T(0.02)) * np.exp(-s.T(0.02) * 200), tb, 0.01 * (1 if tb < T0['12'] else 0.4))
    tt = s.T(3.5); put(FX, s.filt_short(s.noise(3.5, 81), lo=25, hi=160) * np.exp(-tt * 1.1) * np.minimum(1, tt / 0.3), T_BR + 0.15, 0.25)
    k = 0
    while T_ARR[0] + 0.2 + k * 0.26 < T_ARR[1]: step(T_ARR[0] + 0.2 + k * 0.26, 0.035, 90 + k, wet=True); k += 1
    nb(T_KN[0] + 0.1, 0.3, 200, 2000, 0.05, 95, 1)
    hb = T0['09'] - 0.3; k = 0
    while hb < T_POUR[0] + 0.6:
        heart(hb, 0.09 + 0.05 * seg01(hb, T0['09'], T0['10'])); hb += 0.9 - 0.3 * seg01(hb, T0['09'], T0['10']); k += 1
    nb(T_LIFT[0] + 0.1, 0.3, 300, 2500, 0.025, 97, 1); clink(T_LIFT[0] + 0.3, 0.015, 3)
    for k in range(8): tone(T_POUR[1] + k * 0.17, 60 + 7 * hsh(k, 4), 0.12, 0.02, dec=15, glide=0.4)              # pour / gurgle
    shimmer(T_GLOW[0], 1.2, 0.03, 79)
    tone(T_BLANK[0], 100, 2.4, 0.02, dec=0.8); tone(T_BLANK[0], 88, 2.0, 0.02, dec=1.0)                          # a thin ringing as the light goes out
    duck_out = 1 - 0.75 * mask(T_BLANK[0], T_BLANK[1] - 0.1, 0.25)
    # Mira wakes: a soft swell that cuts out on "have we met?"
    a0 = T_WAKE; cut = ws('12', 1)
    sw = np.clip((t - a0) / 1.6, 0, 1) * (t < cut)
    for f, a in ((220.0, 1.0), (277.2, 0.7), (329.6, 0.6), (440.0, 0.3)): MUS += np.sin(2 * np.pi * f * t) * a * 0.022 * sw
    # after: a low lonely pad (A minor), birds from line 14
    pad = mask(cut + 0.4, T_DAWN + 0.5, 1.2)
    for f, a in ((110.0, 1.0), (130.8, 0.6), (164.8, 0.5)): MUS += np.sin(2 * np.pi * f * t + a) * a * 0.018 * pad
    # ---- DAWN: birds, breeze, footsteps on stone, the HUD sting, one piano note
    dn = mask(T0['14'], DUR + 1, 1.0)
    BED += s.filt(s.rng.normal(0, 1, n), lo=200, hi=1200) * 0.032 * dn
    for k in range(int((DUR - T0['14']) / 0.8)):
        tb = T0['14'] + k * 0.8 + 0.5 * hsh(k, 12)
        for j in range(2 + k % 2): tt = s.T(0.09); put(BED, np.sin(2 * np.pi * (2900 + 800 * j + 500 * hsh(k, j)) * tt * (1 + 0.3 * tt / 0.09)) * np.sin(np.pi * tt / 0.09) ** 2, tb + j * 0.13, 0.006)
    k = 0
    while T_DAWN + k * 0.52 < T_STOP + 0.3: step(T_DAWN + k * 0.52, 0.022, 120 + k); k += 1
    for k, m in enumerate((72, 76, 79, 84)): tone(T0['16'] - 0.3 + k * 0.09, m, 0.5, 0.02, dec=6, harm=(1.0, 0.3))    # QUEST COMPLETE
    tone(T0['16'] + 0.6, 57, 1.0, 0.03, dec=3, harm=(1.0, 0.6, 0.2))                                                  # MEMORY LOST (low)
    pend = mask(T0['16'], DUR + 1, 1.0)
    for f, a in ((220.0, 1.0), (261.6, 0.6), (329.6, 0.5)): MUS += np.sin(2 * np.pi * f * t) * a * 0.014 * pend
    piano(T_BLACK, 57, 0.08, 2.0)                                                                                     # one piano note on the cut to black
    # ---- voice: RMS-levelled per line, ducking
    NB = np.zeros(n); wins = []
    for k_, t0 in LINES:
        a, ar = _sf.read(os.path.join(TTS_DIR, 'fpo', f'{k_}.wav')); a = a if a.ndim == 1 else a.mean(1)
        a = np.interp(np.arange(int(len(a) * sr / ar)) / sr, np.arange(len(a)) / ar, a); act = np.abs(a) > 0.02 * np.abs(a).max()
        a = a * (0.12 / np.sqrt((a[act] ** 2).mean())) * 10 ** (LVL.get(k_, 0.0) / 20)
        put(NB, a, t0); wins.append((t0, t0 + len(a) / sr))
    g = duck_envelope(n, sr, wins, -7.0, 0.05, 0.25)
    bed = (BED * g + MUS * (0.6 + 0.4 * g)) * duck_out; fx = FX * (0.55 + 0.45 * g)
    endcut = np.where(t < T_BLACK, 1.0, 0.0); endcut = np.convolve(endcut, np.ones(96) / 96, 'same')            # hard cut (no click) at the black
    bed = bed * endcut; fx_end = fx * endcut
    pn = np.zeros(n); tt = s.T(2.0); f = 220.0
    x = (np.sin(2 * np.pi * f * tt) + 0.45 * np.sin(4 * np.pi * f * tt) + 0.2 * np.sin(6 * np.pi * f * tt)) * np.exp(-tt * 1.3) * np.minimum(1, tt / 0.005)
    put(pn, x, T_BLACK, 0.08)
    L = bed + fx_end + pn; R_ = np.roll(bed, 700) + np.roll(fx_end, 200) + pn
    pk = max(np.abs(L).max(), np.abs(R_).max()); gv = pk * 1.6 / np.abs(NB).max()
    s.L = L + NB * gv; s.R = R_ + NB * gv; s.reverb(0.12, length=1.4, decay=3.0)
    return s.save(path, peak=0.9)
if __name__ == '__main__' and os.environ.get('PART') == 'audio':
    print(build_audio(os.path.join(OUT, 'forget_potion.wav'))); sys.exit()
if __name__ == '__main__' and os.environ.get('PART'):
    a, b = map(int, os.environ['PART'].split(':'))
    import subprocess
    p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W * S}x{H * S}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', os.path.join(OUT, f'fpo_{a:05d}.mp4')], stdin=subprocess.PIPE)
    vhs = post.VHS(W * S, H * S, S, grade='none', chroma=0, scan_dark=1.0, vignette=0.22, grain=0.9, band_period=1e9)
    for f in range(a, min(b, N)): p.stdin.write(vhs(frame_final(f / FPS), f, f / FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done', a, b); sys.exit()
