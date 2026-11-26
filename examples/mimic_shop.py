"""WHY DO SHOPKEEPERS BUY YOUR JUNK? (Insert Disc 2, 26 Nov 2026) ~37 s final (x1.2 after), nightkit HD, 9:16. Tone: CREEPY (Enes).
Brief: briefs/MIMIC_SHOP_FULL_BRIEF.txt. Voices: Enes's cloned voice, tools/tts/ms.py.
The shopkeeper buys everything, never blinks, pays with wet gold; the counter breathes and swallows the junk. "Can I see the back room?"
"There is no back room." The counter is a mimic's mouth and the shopkeeper is its lure, hanging on its tongue. The shop menu offers
SELL: HERO. He runs; the door bites shut; outside, the windows open like eyes. The next hero walks in = frame 0 (loop).
Reuses: forget_potion ADV (hero) + ground/tree/stars, dragon_taxes KNIGHT (next hero), coin. New: shopkeeper (lure), mimic counter
(breathing lid, teeth, tongue), shop interior + junk shelves + candle, door jaws, shop exterior with window eyes, SHOP menu UI.
Render in sequences (Enes, 26 Nov):  python tools/render_seq.py examples/mimic_shop.py --prefix ms --seqs s1,s2,s3,s4,s5 / --master <out>
Stills: TEST=seq python examples/mimic_shop.py -> test_ms.png"""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera
from nightkit.zraster import zrender
from nightkit import post, look, hd, motion
import forget_potion as fp
import dragon_taxes as dtx

W, H, S = 270, 480, 4
PI = math.pi; V = np.array; FPS = 24
sm = motion.smooth
seg01, win, lerp, lerp3, hsh, ang_to, mixc = fp.seg01, fp.win, fp.lerp, fp.lerp3, fp.hsh, fp.ang_to, fp.mixc
SUB_LANG = os.environ.get('SUB_LANG', 'en'); TRL = SUB_LANG == 'tr'
def F(x): return round(x * 1.2, 4)
def wpt(base, yaw, l): return V(base, float) + hd.Ry(yaw) @ V(l, float)

# ======================= cast =======================
SHOPK = hd.spec(h=1.86, build=0.86, skin=(214, 204, 186), hair=(30, 26, 24), hair_style='short', eye=(40, 36, 34), brow=(36, 30, 28),
                lip=(150, 96, 96), tunic=(62, 46, 72), tunic2=(48, 36, 56), skirt=0.55, pants=(48, 36, 56), boots=(48, 36, 56),
                belt=(110, 84, 50), buckle=(220, 190, 110), apron=(120, 104, 84), collar=(150, 140, 120))
SK_K = SHOPK['h'] / 1.78
ADV = fp.ADV; KNIGHT = dtx.KNIGHT
def shopkeeper(P, grin=1.0, talk=0.0):
    """hd.human + the GRIN: a mouth far too wide, with a row of teeth (talk opens it); his eyes are never closed"""
    Q = hd.human(SHOPK, P); hc = P['_head']; RH = P['_RH']; k = SK_K
    Z = hd._ZF[(round(k, 3), 0.0)]; up = RH @ V((0, 1.0, 0)); mn = hd.nz(RH @ V((0, -0.15, 1.0)))
    mc = hc + RH @ V((0, -0.05 * k, Z['mouth'] + 0.002))
    w = 0.034 * k * grin + 0.018 * k * (1 - grin); h = 0.007 * k + 0.012 * k * talk
    pts = [(-w, 0.008 * k), (-w * 0.6, -h * 0.6), (0, -h), (w * 0.6, -h * 0.6), (w, 0.008 * k), (w * 0.5, 0.0), (-w * 0.5, 0.0)]
    Q += hd.poly_decal(tuple(mc), tuple(mn), tuple(up), pts, (40, 10, 14), lift=0.0045)
    Q += hd.poly_decal(tuple(mc), tuple(mn), tuple(up), [(-w * 0.82, 0.004 * k), (w * 0.82, 0.004 * k), (w * 0.7, -0.003 * k), (-w * 0.7, -0.003 * k)], (236, 230, 210), lift=0.0055)
    for i in range(9):                                                                     # tooth gaps
        x = -w * 0.7 + i * w * 1.4 / 8; Q += hd.decal(tuple(mc + RH @ V((x, 0.0005, 0))), tuple(mn), tuple(up), 0.0012 * k, 0.007 * k, (120, 100, 90), lift=0.006)
    return [q for q in Q if q]

# ======================= set: interior =======================
ZF, ZB, XW, HW = -0.6, 4.2, 2.6, 3.0                 # front wall (door), back wall, half width, wall height
CT = V((0.0, 0.0, 2.2)); CW, CH, CD = 1.05, 1.0, 0.34   # counter centre, half width, height, half depth
HINGE_Z = CT[2] + CD
SK0 = (0.0, 0.0, 2.88)                              # shopkeeper behind the counter, facing the hero (-z)
H0 = (0.12, 0.0, 1.22)                              # hero at the counter
CANDLE = V((-0.72, CH, 2.05))
WOOD, WOOD_D, WALL, WALL_D = (96, 70, 48), (72, 52, 36), (64, 56, 50), (52, 46, 42)
CURT = (1.45, 0.0, ZB - 0.02)
def interior():
    Q = []
    for zf_, nrm in ((ZB, -1),):
        for i, x in enumerate(np.arange(-XW, XW, 0.65)):
            for j, y in enumerate(np.arange(0, HW, 0.5)):
                c = hd.shade(WALL if (i + j) % 2 else WALL_D, 0.9 + 0.2 * hsh(i * 7 + j, 3))
                if abs(x + 0.325 - CURT[0]) < 0.5 and y < 2.0: continue
                Q.append(hd.face([(x, y, zf_), (x + 0.65, y, zf_), (x + 0.65, y + 0.5, zf_), (x, y + 0.5, zf_)][::(1 if nrm < 0 else -1)], c))
    for sx in (-1, 1):                                                                      # side walls (planks)
        for i, z in enumerate(np.arange(ZF, ZB, 0.4)):
            c = hd.shade(WALL_D, 0.85 + 0.25 * hsh(i, 5 + sx))
            pts = [(sx * XW, 0, z), (sx * XW, 0, z + 0.4), (sx * XW, HW, z + 0.4), (sx * XW, HW, z)]
            Q.append(hd.face(pts if sx > 0 else pts[::-1], c))
    # front wall with the door hole (x -0.5..0.5, y 0..2.1)
    for x0, x1, y0, y1 in ((-XW, -0.5, 0, HW), (0.5, XW, 0, HW), (-0.5, 0.5, 2.1, HW)):
        Q.append(hd.face([(x1, y0, ZF), (x0, y0, ZF), (x0, y1, ZF), (x1, y1, ZF)], WALL_D))
    for x in (-0.55, 0.55): Q += hd.bx((x, 1.05, ZF), np.eye(3), (0.06, 1.05, 0.08), WOOD_D)
    Q += hd.bx((0, 2.14, ZF), np.eye(3), (0.6, 0.06, 0.08), WOOD_D)
    for i, z in enumerate(np.arange(ZF, ZB, 1.2)): Q += hd.bx((0, HW - 0.1, z + 0.6), np.eye(3), (XW, 0.08, 0.1), WOOD_D)   # beams
    # back-room curtain (dark, a doorway that leads nowhere)
    Q.append(hd.face([(CURT[0] - 0.5, 0, ZB), (CURT[0] + 0.5, 0, ZB), (CURT[0] + 0.5, 2.0, ZB), (CURT[0] - 0.5, 2.0, ZB)][::-1], (20, 14, 16)))
    for i in range(6):
        x = CURT[0] - 0.42 + i * 0.17; Q += hd.limb((x, 0.05, ZB - 0.04), (x, 1.95, ZB - 0.04), 0.05, 0.05, (92, 26, 34) if i % 2 else (76, 20, 28), n=6, m=1)
    # shelves of junk on the back wall
    for y in (1.05, 1.65, 2.25):
        Q += hd.bx((-0.35, y, ZB - 0.2), np.eye(3), (1.6, 0.03, 0.2), WOOD)
    for i in range(14):
        y = (1.05, 1.65, 2.25)[i % 3] + 0.03; x = -1.8 + 3.0 * hsh(i, 11); z = ZB - 0.2
        kind = i % 4
        if kind == 0: Q += hd.sword((x, y + 0.03, z), (1.0, 0.05, 0.0), (0, 1.0, 0), col=(130, 104, 86), length=0.6)
        elif kind == 1: Q += hd.ellip((x, y + 0.2, z + 0.05), hd.Rx(-0.2), (0.17, 0.17, 0.03), 10, 3, (110, 84, 60))
        elif kind == 2: Q += hd.ellip((x, y + 0.08, z), np.eye(3), (0.11, 0.09, 0.11), 8, 4, (120, 120, 126), v1=PI * 0.55)
        else: Q += hd.limb((x - 0.12, y + 0.02, z), (x + 0.12, y + 0.03, z), 0.02, 0.025, (220, 214, 196), n=5, m=1)
    return [q for q in Q if q]
def floor(t, ripple=0.0):
    """floor boards (they ripple, from the counter outward, in the reveal)"""
    Q = []
    for i, x in enumerate(np.arange(-XW, XW, 0.26)):
        for j, z in enumerate(np.arange(ZF, ZB, 0.6)):
            def y(xx, zz):
                if ripple <= 0: return 0.0
                d = math.hypot(xx - CT[0], zz - CT[2]); return 0.045 * ripple * math.sin(d * 7.0 - t * 14.0) * max(0.0, 1 - d / 3.2)
            c = hd.shade(WOOD if i % 2 else WOOD_D, 0.85 + 0.2 * hsh(i * 13 + j, 9))
            Q.append(hd.face([(x, y(x, z), z), (x, y(x, z + 0.6), z + 0.6), (x + 0.26, y(x + 0.26, z + 0.6), z + 0.6), (x + 0.26, y(x + 0.26, z), z)], c))
    return [q for q in Q if q]
# ---- the mimic counter
def counter(lid=0.0, t=0.0, glow=0.0):
    """box with plank front; the top board is the LID, hinged at the back edge (lid = angle in radians). Under it: the mouth."""
    Q = []; x0, x1 = -CW, CW; zf_, zb_ = CT[2] - CD, CT[2] + CD
    for i, x in enumerate(np.arange(x0, x1, 0.21)):                                         # front planks
        Q.append(hd.face([(x + 0.21, 0, zf_), (x, 0, zf_), (x, CH - 0.06, zf_), (x + 0.21, CH - 0.06, zf_)], hd.shade(WOOD, 0.85 + 0.2 * hsh(i, 21))))
    for sx in (-1, 1):
        pts = [(sx * CW, 0, zf_), (sx * CW, 0, zb_), (sx * CW, CH - 0.06, zb_), (sx * CW, CH - 0.06, zf_)]
        Q.append(hd.face(pts if sx > 0 else pts[::-1], WOOD_D))
    Q.append(hd.face([(x0, 0, zb_), (x1, 0, zb_), (x1, CH - 0.06, zb_), (x0, CH - 0.06, zb_)], WOOD_D))
    Q += hd.bx((0, 0.06, zf_ - 0.02), np.eye(3), (CW + 0.03, 0.06, 0.03), WOOD_D)
    # mouth inside (seen when the lid lifts): dark red flesh, lower teeth along the front edge
    Q.append(hd.face([(x0 + 0.04, CH - 0.2, zf_ + 0.04), (x1 - 0.04, CH - 0.2, zf_ + 0.04), (x1 - 0.04, CH - 0.2, zb_ - 0.04), (x0 + 0.04, CH - 0.2, zb_ - 0.04)][::-1], (70, 14, 20), emit=glow > 0.3))
    for z in (zf_ + 0.03,):
        Q.append(hd.face([(x0 + 0.03, CH - 0.2, z), (x1 - 0.03, CH - 0.2, z), (x1 - 0.03, CH - 0.06, z), (x0 + 0.03, CH - 0.06, z)][::-1], (110, 30, 36)))
    nT = 13
    for i in range(nT):
        x = x0 + 0.08 + i * (2 * CW - 0.16) / (nT - 1); hgt = 0.09 + 0.04 * hsh(i, 31); yb = CH - 0.22          # tips stay under the closed lid
        Q.append(hd.face([(x - 0.05, yb, zf_ + 0.05), (x + 0.05, yb, zf_ + 0.05), (x, yb + hgt, zf_ + 0.06)], (236, 228, 206)))
        Q.append(hd.face([(x + 0.05, yb, zf_ + 0.05), (x - 0.05, yb, zf_ + 0.05), (x, yb + hgt, zf_ + 0.06)], (200, 190, 170)))
    # the lid: rotates about the back edge
    Rl = hd.Rx(lid); hinge = V((0, CH, zb_))
    def L(p): return tuple(hinge + Rl @ (V(p, float) - hinge))
    th = 0.06; zf2 = zf_ - 0.04
    top = [L((x0 - 0.04, CH, zf2)), L((x1 + 0.04, CH, zf2)), L((x1 + 0.04, CH, zb_)), L((x0 - 0.04, CH, zb_))]
    Q.append(hd.face(top[::-1], hd.shade(WOOD, 1.05)))
    Q.append(hd.face([L((x0 - 0.04, CH - th, zf2)), L((x1 + 0.04, CH - th, zf2)), L((x1 + 0.04, CH, zf2)), L((x0 - 0.04, CH, zf2))], WOOD_D))
    under = [L((x0 - 0.04, CH - th, zf2)), L((x1 + 0.04, CH - th, zf2)), L((x1 + 0.04, CH - th, zb_)), L((x0 - 0.04, CH - th, zb_))]
    Q.append(hd.face(under, (90, 20, 28)))
    for i in range(nT - 1):                                                                 # upper teeth on the lid's front edge
        x = x0 + 0.13 + i * (2 * CW - 0.26) / (nT - 2); hgt = 0.09 + 0.05 * hsh(i, 33)
        a, b, c = L((x - 0.05, CH - th, zf2 + 0.11)), L((x + 0.05, CH - th, zf2 + 0.11)), L((x, CH - th - hgt, zf2 + 0.12))
        Q.append(hd.face([a, b, c], (236, 228, 206))); Q.append(hd.face([b, a, c], (200, 190, 170)))
    if 0.0105 < lid < 0.06:                                                                 # breathing seam: a faint red glow, only at the top of a breath
        Q.append(hd.face([(x0 + 0.3, CH - 0.02, zf_ - 0.005), (x1 - 0.3, CH - 0.02, zf_ - 0.005), (x1 - 0.3, CH - 0.008, zf_ - 0.005), (x0 + 0.3, CH - 0.008, zf_ - 0.005)][::-1], (96, 16, 20), emit=True))
    return [q for q in Q if q]
def tongue(top, u=1.0):
    """from the throat inside the counter, up and back to the lure's belly (top)"""
    a = V((0.0, CH - 0.2, CT[2] - 0.05)); b = V(top, float); m1 = V((0.0, 1.75, CT[2] - 0.2)); m2 = V((0.0, 2.15, HINGE_Z + 0.02))   # out of the mouth, up over the lid's edge, into him
    pts = [dtx.bez(a, m1, m2, b, s_) for s_ in np.linspace(0, 1, 9)]
    Q = []
    for i in range(8):
        r0 = 0.12 - 0.07 * i / 8; r1 = 0.12 - 0.07 * (i + 1) / 8
        Q += hd.limb(tuple(pts[i]), tuple(pts[i + 1]), r0 * 1.25, r1 * 1.25, (196, 70, 84) if i % 2 else (176, 58, 72), n=8, m=1)
    return [q for q in Q if q]
def candle(t, on=1.0):
    c = CANDLE; Q = hd.lathe(tuple(c), np.eye(3), [(0.035, 0), (0.035, 0.16), (0.03, 0.17)], 7, (226, 218, 196))
    Q += hd.lathe(tuple(c - V((0, 0.0, 0))), np.eye(3), [(0.07, 0), (0.08, 0.015)], 8, (90, 84, 74))
    if on > 0.05:
        f = c + V((0, 0.17, 0)); hgt = 0.06 * (0.85 + 0.15 * math.sin(t * 13))
        for ang in (0.0, PI / 2):
            dx, dz = 0.016 * math.cos(ang), 0.016 * math.sin(ang)
            Q.append(hd.face([f + V((-dx, 0, -dz)), f + V((dx, 0, dz)), f + V((0.004 * math.sin(t * 9), hgt, 0))], (255, 214, 120), emit=True))
    return [q for q in Q if q]
# ---- door jaws (seen from inside and outside)
def door_jaws(u):
    """u 0 = open doorway, 1 = shut: an upper jaw drops and a lower jaw rises, teeth interlocking in the middle"""
    if u <= 0.0: return []
    Q = []; ytop = lerp(2.1, 1.05, u); ybot = lerp(0.0, 1.05, u)
    for z_, flip in ((ZF + 0.02, 1), (ZF - 0.02, -1)):
        for y0, y1, td in ((ytop, 2.1, -1), (0.0, ybot, 1)):
            if y1 - y0 < 0.005: continue
            pts = [(-0.5, y0, z_), (0.5, y0, z_), (0.5, y1, z_), (-0.5, y1, z_)]
            Q.append(hd.face(pts if flip > 0 else pts[::-1], (96, 22, 30)))
            edge = y0 if td < 0 else y1
            for i in range(7):
                x = -0.43 + i * 0.143 + (0.07 if td > 0 else 0.0); hgt = 0.13
                tri = [(x - 0.06, edge, z_), (x + 0.06, edge, z_), (x, edge + td * hgt, z_)]
                Q.append(hd.face(tri if (flip * td) < 0 else tri[::-1], (236, 228, 206)))
    return [q for q in Q if q]
# ---- exterior
EXT_ROOF = (40, 34, 40)
def exterior(eyes=0.0, t=0.0):
    Q = []; w, d, h = XW + 0.03, None, HW + 0.03
    Q += fp.ground(-12, 12, -16, 12, 0.8, [(40, 48, 36), (44, 50, 38), (36, 42, 32)], seed=33)
    for i, x in enumerate(np.arange(-14.0, 14.0, 0.7)):                                     # road in front of the door
        Q.append(hd.face([(x, 0.004, -2.2), (x, 0.004, -1.2), (x + 0.7, 0.004, -1.2), (x + 0.7, 0.004, -2.2)][::-1], hd.shade((88, 76, 60), 0.9 + 0.15 * hsh(i, 41))))
    Q.append(hd.face([(-0.5, 0.004, -1.2), (-0.5, 0.004, ZF - 0.03), (0.5, 0.004, ZF - 0.03), (0.5, 0.004, -1.2)][::-1], (88, 76, 60)))
    # walls (outside faces)
    z0, z1 = ZF - 0.03, ZB + 0.03
    for x0, x1, y0, y1 in ((-w, -0.5, 0, h), (0.5, w, 0, h), (-0.5, 0.5, 2.1, h)):
        for i, y in enumerate(np.arange(y0, y1, 0.5)):
            Q.append(hd.face([(x0, y, z0), (x1, y, z0), (x1, min(y1, y + 0.5), z0), (x0, min(y1, y + 0.5), z0)][::-1], hd.shade((70, 60, 52), 0.85 + 0.2 * hsh(i + int(x0 * 3), 43))))
    for sx in (-1, 1):
        pts = [(sx * w, 0, z0), (sx * w, 0, z1), (sx * w, h, z1), (sx * w, h, z0)]
        Q.append(hd.face(pts[::-1] if sx > 0 else pts, (58, 50, 44)))
    ridge = h + 1.5
    for sx in (-1, 1):
        pts = [(sx * (w + 0.3), h - 0.1, z0 - 0.3), (0, ridge, z0 - 0.3), (0, ridge, z1 + 0.3), (sx * (w + 0.3), h - 0.1, z1 + 0.3)]
        Q.append(hd.face(pts if sx > 0 else pts[::-1], hd.shade(EXT_ROOF, 1.0 if sx > 0 else 0.8)))
    Q.append(hd.face([(-w, h, z0), (w, h, z0), (0, ridge - 0.05, z0)][::-1], (70, 60, 52)))
    for x in (-w, w): Q += hd.bx((x, h / 2, z0), np.eye(3), (0.1, h / 2, 0.1), (50, 38, 28))
    # two upper windows = the EYES (dark shutters -> yellow slits -> wide with a slit pupil)
    for sx in (-1, 1):
        c = V((sx * 1.35, 2.05, z0 - 0.02)); ww, hh = 0.46, 0.04 + 0.2 * eyes
        Q.append(hd.face([tuple(c + V((-0.5, -0.4, 0.01))), tuple(c + V((0.5, -0.4, 0.01))), tuple(c + V((0.5, 0.4, 0.01))), tuple(c + V((-0.5, 0.4, 0.01)))][::-1], (34, 26, 22)))
        if eyes > 0.02:
            pts = [(ww * math.cos(a), hh * math.sin(a) * abs(math.sin(a)) ** 0.15) for a in np.linspace(0, 2 * PI, 17)[:-1]]
            Q += hd.poly_decal(tuple(c), (0, 0, -1.0), (0, 1.0, 0), pts, (255, 206, 50), emit=True, lift=0.01)
            Q += hd.poly_decal(tuple(c), (0, 0, -1.0), (0, 1.0, 0), [(x * 0.72, y * 0.72) for x, y in pts], (255, 140, 20), emit=True, lift=0.02)
            look_x = 0.07 * math.sin(t * 1.7) if eyes > 0.9 else 0.0
            Q += hd.poly_decal(tuple(c + V((look_x, 0, 0))), (0, 0, -1.0), (0, 1.0, 0), [(0, -hh * 0.92), (0.05, 0), (0, hh * 0.92), (-0.05, 0)], (14, 6, 4), lift=0.03)
    for i in range(16):
        a = 2 * PI * hsh(i, 51); r = 8 + 5 * hsh(i, 52); x = r * math.sin(a); z = 4 + r * abs(math.cos(a)) * 0.8
        Q += fp.tree(x, z, 4 + 2 * hsh(i, 53), seed=i + 70)
    Q += fp.sky_disc((-10, 14, 26), 1.1, (214, 222, 240)) + fp.stars(23, 50, 28, 6, 22, -26, 26)
    return [q for q in Q if q]

# =====================================================================================================================
#                                                      TIMELINE
# =====================================================================================================================
from nightkit.audio import Sound, duck_envelope
OUT = 'out'; os.makedirs(OUT, exist_ok=True)
TTS_DIR = os.environ.get('TTS_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tts'))
SCR = json.load(open(os.path.join(TTS_DIR, 'ms', 'script.json'), encoding='utf-8'))
KEYS = ['%02d' % i for i in range(0, 10)]
LEAD = {'00': 0.15, '03': 0.3, '06': 0.3, '08': 0.25}
GAP = {'00': 0.3, '01': 0.35, '02': 0.45, '03': 0.25, '04': 0.35, '05': 0.5, '06': 0.3, '07': 3.0, '08': 1.95, '09': 0.45}
def _lines():
    t = 0.0; out = []
    for k in KEYS:
        t += LEAD.get(k, 0.0)
        if k == '09': t += 0.9                      # outside: the shop opens its eyes before the line
        out.append((k, round(t, 3))); t += SCR['dur'][k] + GAP[k]
    return out, t
LINES, _T_END = _lines(); T0 = dict(LINES)
def tend(k): return T0[k] + SCR['dur'][k]
def ws(k, i): return T0[k] + SCR['sent'][k][min(i, len(SCR['sent'][k]) - 1)][0]
S2 = T0['03'] - LEAD['03']; S3 = T0['06'] - LEAD['06']; S4 = T0['08'] - LEAD['08']
T_RUN = (tend('08') - 0.2, tend('08') + 1.3)        # turns and runs for the door
T_JAW = (tend('08') + 1.15, tend('08') + 1.55)      # the door bites shut behind him
S5 = tend('08') + GAP['08']
T_EYES = (S5 + 0.1, S5 + 0.7)
T_NEXT = tend('09') + 0.2                           # the next hero walks up to the door
T_LOOPF = T_NEXT + 1.3
DUR = round(T_LOOPF + 0.5, 3); N = int(round(DUR * FPS))
def fr(x): return int(round(x * FPS))
SEQS = [('s1', 0, fr(S2)), ('s2', fr(S2), fr(S3)), ('s3', fr(S3), fr(S4)), ('s4', fr(S4), fr(S5)), ('s5', fr(S5), N)]
# beats
T_SWORD = (-0.6, 0.35)                              # frame 0: he lifts the rusty sword (the loop tail shows the start)
T_COIN = tend('01') - 0.35                          # the coin drops on the counter
GULPS = [ws('02', 1) + 0.45, ws('02', 2) + 0.45]    # the counter swallows the spoon, the shield
T_PALM = ws('05', 1) - 0.1
T_FREEZE = T0['07'] - 0.05
T_RIP = (tend('07') + 0.2, tend('07') + 1.4)        # WORDLESS: the floor ripples, he looks down
T_LID = (tend('07') + 1.0, tend('07') + 2.0)        # the lid opens: teeth
T_RISE = (tend('07') + 1.5, tend('07') + 2.7)       # the lure rises on the tongue, arms limp, head lolls
T_MENU = (tend('07') + 2.0, T0['08'] + 1.5)         # SELL: HERO
CUTS = [('open', 0.0), ('m1', T0['02'] - 0.1), ('m2', ws('02', 1) - 0.1), ('m3', ws('02', 2) - 0.1),
        ('ask', S2), ('eat', T0['04'] - 0.15), ('eyes', T0['05'] - 0.1), ('wet', ws('05', 1) - 0.15),
        ('back', S3), ('noroom', T0['07'] - 0.2), ('look', tend('07') + 0.15), ('reveal', T_LID[0] - 0.1),
        ('wide', S4), ('door', T_RUN[0] + 0.55),
        ('ext', S5), ('next', T_NEXT), ('loop', T_LOOPF)]
def scene(t):
    if t < 0: return 'loop'
    nm = CUTS[0][0]
    for n_, a in CUTS:
        if t >= a: nm = n_
    return nm
def talking(t, key):
    if key not in T0: return 0.0
    for a, b, _ in SCR['sent'][key]:
        if T0[key] + a <= t < T0[key] + b: return 0.5 + 0.5 * math.sin((t - T0[key]) * 17.0)
    return 0.0

# =====================================================================================================================
#                                                      POSES
# =====================================================================================================================
def lid_angle(t):
    if t < 0 or t < T_LID[0]:
        a = 0.012 * (0.5 + 0.5 * math.sin(2 * PI * 0.32 * t))                                  # breathing
        for g in GULPS: a += 0.22 * win(t, g, g + 0.45, 0.12)                                  # gulp
        return a
    return 1.45 * sm(seg01(t, *T_LID)) + 0.03 * math.sin(t * 3.0) * sm(seg01(t, T_LID[1], T_LID[1] + 0.5))
def shop_pose(t):
    """returns pose, grin, talk, rise (0..1), held item"""
    sc = scene(t)
    P = dict(base=SK0, yaw=PI, eyes='wide', mouth='neutral', brow=0.25, lean=0.16, nod=0.08, look=(0.0, 0.0))
    P['rf'] = (0.1, 0.8, -0.05); P['lf'] = (-0.1, 0.8, -0.05); P['rkpole'] = (0.1, 1.0, 0.2); P['lkpole'] = (-0.1, 1.0, 0.2)   # legs folded away (he has none)
    P['rh_w'] = (CT[0] - 0.32, CH + 0.04, CT[2] + 0.15); P['lh_w'] = (CT[0] + 0.32, CH + 0.04, CT[2] + 0.15)
    P['rpalm'] = (0, -1.0, 0); P['lpalm'] = (0, -1.0, 0); P['rpalm_local'] = False; P['lpalm_local'] = False; P['rgrip'] = 0.3; P['lgrip'] = 0.3
    grin = 1.0; talk = max(talking(t, k) for k in ('01', '04', '07')); item = None; rise = 0.0
    # the rusty sword, lifted for us to see (frame 0 / loop tail)
    sw = sm(seg01(t, *T_SWORD)) * (1 - sm(seg01(t, T_COIN - 0.5, T_COIN - 0.1))) if t < T0['02'] else 0.0
    if sw > 0:
        P['rh_w'] = tuple(lerp3(V(P['rh_w']), V((CT[0] - 0.28, 1.5, CT[2] + 0.32)), sw)); P['rpalm'] = (1.0, 0, 0); P['rgrip'] = 0.9; item = ('sword', sw)
    if T_COIN - 0.6 <= t < T_COIN + 0.3 and t < T0['02']:                                  # left hand over the counter, drops a coin
        u = win(t, T_COIN - 0.6, T_COIN + 0.3, 0.25); P['lh_w'] = tuple(lerp3(V(P['lh_w']), V((0.1, 1.25, CT[2] - 0.2)), u)); P['lpalm'] = (0, -1.0, 0)
    for g in GULPS:                                                                          # slides the item into the seam
        u = win(t, g - 0.5, g + 0.2, 0.2)
        if u > 0: P['rh_w'] = tuple(lerp3(V(P['rh_w']), V((0.05, CH + 0.05, CT[2] - 0.15)), u))
    if T0['04'] - 0.2 <= t < tend('04') + 0.6: P['head'] = (0.0, 0.05, 0.35 * win(t, T0['04'] - 0.2, tend('04') + 0.6, 0.3))
    if sc == 'eyes': P['look'] = (0.0, 0.0); P['nod'] = 0.0
    if t >= T_FREEZE and t >= 0:
        P['brow'] = 0.0; talk = talking(t, '07')
    rise = sm(seg01(t, *T_RISE)) if t >= 0 else 0.0
    if rise > 0:                                                                             # lifted on the tongue: a puppet
        P['base'] = (SK0[0], 0.88 * rise + 0.03 * math.sin(t * 2.3) * rise, SK0[2] + 0.08 * rise)
        for kk in ('rh_w', 'lh_w'): P.pop(kk, None)
        P['rh'] = lerp3((0.32, 1.0, 0.25), (0.26, 0.52, 0.06), rise); P['lh'] = lerp3((-0.32, 1.0, 0.25), (-0.24, 0.5, 0.08), rise)
        P['rgrip'] = 0.1; P['lgrip'] = 0.1; P['rpalm'] = None; P['lpalm'] = None; P.pop('rpalm_local', None); P.pop('lpalm_local', None)
        P['head'] = (0.0, -0.1 * rise, 0.62 * rise + 0.05 * math.sin(t * 1.9) * rise); P['lean'] = 0.05; P['nod'] = 0.0
        if P['rpalm'] is None: P.pop('rpalm'); P.pop('lpalm')
    return P, grin, talk, rise, item
def shop_layer(t):
    P, grin, talk, rise, item = shop_pose(t); Q = shopkeeper(P, grin, talk)
    if item and item[0] == 'sword':
        g = fp.grip_pt(P, 'r', 0.06, 0.0); Q += hd.sword(tuple(g), tuple(hd.nz(V((0.35, 1.0, -0.15)))), P['_rpalm'], col=(140, 104, 80), grip=(70, 50, 36), guard=(120, 90, 60), length=0.75)
    if rise > 0.02 or (t >= T_LID[0] and t >= 0):
        Q += tongue(P['_pel'] + V((0, -0.05, -0.06)))
    return Q, P
def hero_pose(t):
    sc = scene(t)
    P = dict(base=H0, yaw=0.0, eyes='open', mouth='neutral', brow=0.0, lean=0.03, cape_sway=0.0)
    P['rh'] = (0.24, 0.95, 0.12); P['lh'] = (-0.24, 0.95, 0.1)
    if talking(t, '03') > 0: P['mouth'] = 'open' if talking(t, '03') > 0.5 else 'neutral'; P['brow'] = 0.2; P['lh'] = (-0.3, 1.1, 0.35); P['lgrip'] = 0.0; P['lpalm'] = (0, 1.0, 0)
    if talking(t, '06') > 0: P['mouth'] = 'open' if talking(t, '06') > 0.5 else 'neutral'
    if sc == 'eyes' and (t - T0['05']) % 1.6 < 0.12: P['eyes'] = 'closed'                    # HE blinks
    if T_PALM <= t < S3:                                                                     # the wet coin in his palm
        u = sm(seg01(t, T_PALM, T_PALM + 0.3)); P['rh'] = lerp3((0.24, 0.95, 0.12), (0.12, 1.12, 0.38), u); P['rpalm'] = (0, 1.0, 0); P['rgrip'] = 0.15
        P['head'] = (0.0, 0.35 * u, 0.0)
    if S3 <= t < T0['07']:
        g = win(t, T0['06'] - 0.1, tend('06') + 0.3, 0.3); P['head'] = (0.7 * g, 0.0, 0.0)  # glances at the curtain
    if t >= T0['07']: P['brow'] = -0.5; P['eyes'] = 'open'
    if t >= T_RIP[0]:
        d = sm(seg01(t, T_RIP[0], T_RIP[0] + 0.5)); up_ = sm(seg01(t, T_LID[0], T_LID[0] + 0.3))
        P['head'] = (0.0, 0.5 * d * (1 - up_) - 0.15 * up_, 0.0); P['eyes'] = 'wide' if up_ > 0.2 else 'open'; P['mouth'] = 'o' if up_ > 0.5 else 'neutral'; P['brow'] = -0.8
        back = sm(seg01(t, T_LID[0] + 0.2, T0['08'] + 0.8)); P['base'] = (H0[0], 0.0, H0[2] - 0.45 * back); P['lean'] = -0.1 * back
        if back > 0 and back < 1: P['walk'] = -back * 2.0; P['stride'] = 0.18
    if t >= T_RUN[0]:                                                                        # turns and runs out the door
        u = seg01(t, *T_RUN); tu = sm(seg01(t, T_RUN[0], T_RUN[0] + 0.3))
        p0 = V((H0[0], 0.0, H0[2] - 0.45)); p1 = V((0.0, 0.0, ZF - 1.4))
        P['base'] = tuple(p0 + (p1 - p0) * (u ** 1.3)); P['yaw'] = lerp(0.0, PI, tu); P['walk'] = u * 10.0; P['stride'] = 0.45; P['lift'] = 0.18; P['lean'] = 0.3
        P['head'] = (0.0, 0.0, 0.0); P['eyes'] = 'wide'; P['mouth'] = 'o'
    if sc in ('ext', 'next'):                                                                # outside: bursts out, runs past the camera, looks back
        u = seg01(t, S5, S5 + 2.6); p0 = V((0.0, 0.0, ZF - 0.6)); p1 = V((2.6, 0.0, -7.4))
        P['base'] = tuple(p0 + (p1 - p0) * u); P['yaw'] = ang_to(tuple(p0), tuple(p1)); P['walk'] = (t - S5) * 9.0; P['stride'] = 0.45; P['lift'] = 0.18; P['lean'] = 0.28
        P['head'] = (0.0 if t < T_EYES[0] + 0.3 else 1.4 * win(t, T_EYES[0] + 0.3, T0['09'] + 1.0, 0.3), 0.0, 0.0); P['eyes'] = 'wide'; P['mouth'] = 'o'
    return P
def knight_next(t):
    """the next hero walks up the road to the door (no idea)"""
    u = seg01(t, T_NEXT - 0.6, T_LOOPF + 0.2); p0 = V((-3.6, 0.0, -5.2)); p1 = V((-0.05, 0.0, ZF - 0.5))
    P = dict(base=tuple(p0 + (p1 - p0) * u), yaw=ang_to(tuple(p0), tuple(p1)), eyes='open', mouth='smile', brow=0.2, lean=0.04, cape_sway=0.12, walk=u * 7.0, stride=0.3)
    P['rh'] = (0.24, 0.95, 0.12); return dtx.knight(P)
def coin_faces(t):
    """the wet coin: falls onto the counter (drips), later in his palm (drips)"""
    Q = []
    if 0 <= t < S2:
        u = t - T_COIN
        if u >= 0:
            y = max(CH + 0.006, 1.22 - 4.9 * u * u); c = V((0.1, y, CT[2] - 0.2)); Q += dtx.coin(tuple(c), np.eye(3), s=1.2)
            if y <= CH + 0.007: Q += hd.poly_decal(tuple(V((0.1, CH + 0.002, CT[2] - 0.2))), (0, 1.0, 0), (0, 0, 1.0), [(0.06 * math.cos(a), 0.045 * math.sin(a)) for a in np.linspace(0, 2 * PI, 9)[:-1]], (40, 44, 48), lift=0.0)
    return [q for q in Q if q]
def drips(c, t, n=5, seed=0):
    Q = []
    for i in range(n):
        u = ((t * 1.3) + hsh(i, seed)) % 1.0; y = c[1] - 0.02 - 0.5 * u * u
        Q += hd.bx((c[0] + 0.01 * math.sin(i * 3), y, c[2] + 0.01 * math.cos(i)), np.eye(3), (0.004, 0.007, 0.004), (170, 200, 210), emit=True)
    return [q for q in Q if q]
SALE_ITEMS = {0: 'spoon', 1: 'shield'}
def sale_item(t):
    """the spoon / shield lie on the counter until the gulp"""
    Q = []
    for i, g in enumerate(GULPS):
        a = g - 1.2
        if not (a <= t < g + 0.05) or t < 0: continue
        slide = sm(seg01(t, g - 0.35, g)); c = V((0.25 - 0.2 * slide, CH + 0.01, CT[2] - 0.12 + 0.1 * slide))
        if SALE_ITEMS[i] == 'spoon': Q += hd.limb(tuple(c + V((-0.12, 0.01, 0))), tuple(c + V((0.08, 0.02, 0.04))), 0.01, 0.012, (170, 170, 176), n=5, m=1) + hd.ellip(tuple(c + V((0.11, 0.02, 0.05))), np.eye(3), (0.04, 0.015, 0.03), 6, 3, (180, 180, 186))
        else: Q += hd.ellip(tuple(c + V((0, 0.03, 0))), hd.Rx(-PI / 2 + 0.1), (0.2, 0.2, 0.03), 10, 3, (120, 90, 64), colfn=lambda i_, j, cl: (150, 120, 70) if j == 0 else (120, 90, 64))
    return [q for q in Q if q]

# =====================================================================================================================
#                                                      CAMERA
# =====================================================================================================================
OPEN_POS = V((0.08, 1.5, 2.02)); OPEN_TGT = V((-0.04, 1.68, 2.85))
def cam_shot(t):
    sc = scene(t)
    if sc in ('open', 'loop'):
        u = sm(seg01(t, -1.0, T0['01'] + 1.2)); return lerp3(OPEN_POS + V((0.02, 0.0, -0.22)), OPEN_POS, u), OPEN_TGT, 42.0
    idx = [n for n, _ in CUTS].index(sc); a = CUTS[idx][1]; b = CUTS[idx + 1][1] if idx + 1 < len(CUTS) else DUR; u = sm(seg01(t, a, b))
    if sc == 'm1': return lerp3((1.9, 1.7, 0.6), (1.75, 1.65, 0.75), u), lerp3((0.0, 1.2, 2.2), (0.0, 1.15, 2.2), u), 50.0
    if sc in ('m2', 'm3'): return lerp3((0.55, 1.45, 1.45), (0.5, 1.4, 1.52), u), (0.08, CH + 0.05, CT[2] - 0.08), 40.0
    if sc == 'ask': return lerp3((-0.35, 1.8, 2.6), (-0.3, 1.78, 2.5), u), (0.12, 1.55, 1.22), 40.0
    if sc == 'eat': return lerp3((0.2, 1.62, 1.75), (0.18, 1.62, 1.85), u), (0.0, 1.62, 2.85), 36.0
    if sc == 'eyes': return lerp3((0.06, 1.72, 2.25), (0.05, 1.72, 2.32), u), (0.0, 1.72, 2.85), 32.0
    if sc == 'wet':
        P = hero_pose(t); return lerp3((0.55, 1.45, 1.15), (0.5, 1.42, 1.2), u), (0.24, 1.08, 1.55), 36.0
    if sc == 'back': return lerp3((0.6, 1.7, 2.35), (0.55, 1.7, 2.25), u), (0.12, 1.6, 1.22), 40.0
    if sc == 'noroom': return lerp3((0.15, 1.65, 1.95), (0.12, 1.66, 2.15), u), (0.0, 1.66, 2.88), 34.0
    if sc == 'look': return lerp3((1.2, 0.55, 0.3), (1.1, 0.5, 0.45), u), lerp3((0.3, 0.6, 1.6), (0.2, 0.5, 1.8), u), 50.0
    if sc == 'reveal': return lerp3((0.55, 2.05, 1.05), (0.65, 2.15, 0.85), u), lerp3((0.0, 1.05, 2.3), (0.0, 1.6, 2.6), u), 56.0
    if sc == 'wide': return lerp3((1.75, 1.4, 0.55), (1.85, 1.45, 0.35), u), lerp3((-0.1, 1.35, 2.3), (-0.1, 1.4, 2.2), u), 52.0
    if sc == 'door': return lerp3((0.25, 1.5, 1.4), (0.22, 1.45, 1.1), u), (0.0, 1.1, ZF), 48.0
    if sc == 'ext': return lerp3((2.2, 1.25, -8.4), (2.0, 1.35, -8.0), u), lerp3((0.6, 1.6, -1.0), (0.2, 2.1, 0.0), u), 50.0
    return lerp3((1.3, 1.5, -6.2), (0.9, 1.5, -5.4), u), (-0.2, 1.4, ZF), 46.0     # next

# =====================================================================================================================
#                                                      RENDER
# =====================================================================================================================
_SET = []
def set_in():
    if not _SET: _SET.append(interior())
    return _SET[0]
_EXT = {}
def frame_low(t):
    pos, tgt, fov = cam_shot(t); cam = Camera.look(tuple(pos), tuple(tgt)); sc = scene(t)
    outside = sc in ('ext', 'next') and t >= 0
    layers = []
    if outside:
        e = sm(seg01(t, *T_EYES)); key = round(e, 2) if e < 1 else 1.0
        layers.append(exterior(e, t)); layers.append(door_jaws(1.0 - sm(seg01(t, T_NEXT - 0.4, T_NEXT + 0.6)) if sc == 'next' else 1.0))
        P = hero_pose(t); layers.append(hd.human(ADV, P))
        if sc == 'next': layers.append(knight_next(t))
        fog = (18, 22, 36); amb = 0.4; fs, fe = 12, 45
        L = [((-8, 10, -9), (140, 160, 225), 2.4), ((6, 4, -10), (90, 100, 150), 0.8)]
        if e > 0: L += [((-1.35, 2.05, ZF - 0.6), (255, 200, 80), 1.2 * e), ((1.35, 2.05, ZF - 0.6), (255, 200, 80), 1.2 * e)]
    else:
        rip = win(t, *T_RIP, 0.3) if t >= 0 else 0.0
        layers += [set_in(), floor(t, rip), counter(lid_angle(t), t, glow=sm(seg01(t, *T_LID)) if t >= 0 else 0.0), candle(t)]
        jaw = sm(seg01(t, *T_JAW)) if t >= 0 else 0.0
        layers.append(door_jaws(jaw))
        SQ, SP = shop_layer(t); layers.append(SQ)
        if sc not in ('open', 'loop', 'eyes', 'noroom', 'eat'):
            HP = hero_pose(t); layers.append(hd.human(ADV, HP))
            if T_PALM <= t < S3:
                g = fp.grip_pt(HP, 'r', 0.05, 0.03); layers.append(dtx.coin(tuple(g + V((0, 0.01, 0))), np.eye(3), s=1.2)); layers.append(drips(g, t, 4, 7))
        layers.append(coin_faces(t)); layers.append(sale_item(t))
        if 0 <= t < S2 and t >= T_COIN - 0.6 and t < T_COIN + 0.3:
            layers.append(drips(V((0.1, 1.22, CT[2] - 0.2)), t, 3, 5))
        fl = 1 + 0.15 * math.sin(t * 11) + 0.07 * math.sin(t * 23)
        L = [(tuple(CANDLE + V((0.25, 0.22, -0.15))), (255, 168, 96), 1.7 * fl), ((0.8, 2.6, 0.2), (60, 90, 100), 0.35)]
        gl = sm(seg01(t, *T_LID)) if t >= 0 else 0.0
        if gl > 0: L.append(((0, CH + 0.1, CT[2]), (255, 40, 40), 1.6 * gl))
        for g in GULPS:
            w_ = win(t, g, g + 0.45, 0.12)
            if w_ > 0: L.append(((0, CH + 0.05, CT[2] - 0.2), (255, 50, 50), 0.8 * w_))
        fog = (4, 5, 7); amb = 0.12; fs, fe = 4, 13
    R = Renderer(W, H, fog=fog)
    img, vi, zb = zrender(R, cam, layers, L, fov=fov, fog_start=fs, fog_end=fe, ambient=amb, return_z=True)
    a = look.outline(np.asarray(img).astype(np.float32), zb)
    if not outside:                                                                         # creepy grade: less colour, a cold green cast
        lum = a.mean(axis=2, keepdims=True); a = (lum * 0.35 + a * 0.65) * np.array([0.94, 1.0, 0.96])
    else: a = a * np.array([0.92, 0.97, 1.08])
    a = np.clip((a - 112) * 1.18 + 104, 0, 255)
    return post.ps1(Image.fromarray(a.astype(np.uint8)), levels=6), vi

# ======================= overlays =======================
def text_w(s, sc): return len(s) * 6 * sc - sc
COVER = ('TÜCCAR NEDEN', 'HURDA ALIR?') if TRL else ('WHY DO SHOPS', 'BUY JUNK?')
COVER = tuple(c.replace('Â', 'A') for c in COVER)
COVER_Y = int(os.environ.get('COVER_Y', '1330'))
T_PUNCH = T0['00'] + 0.7 * SCR['dur']['00']
def cover_overlay(im, t):
    b = T0['01'] + 0.6
    if not (0 <= t < b): return
    d = ImageDraw.Draw(im); pop = sm(seg01(t, 0, 0.12)); sc0 = 12 if pop >= 1 else 14
    punch = win(t, T_PUNCH, T_PUNCH + 0.35, 0.08)
    s1, s2 = COVER; y1 = COVER_Y; y2 = COVER_Y + 8 * sc0 + 30; sc2 = sc0 + 1 + (2 if punch > 0.5 else 0); w2 = text_w(s2, sc2)
    y2 -= 7 if punch > 0.5 else 0
    d.rectangle([540 - w2 / 2 - 34, y2 - 22, 540 + w2 / 2 + 34, y2 + 7 * sc2 + 22], fill=(110, 16, 24))
    for s_, y, sc, col, sh in ((s1, y1, sc0, (255, 255, 255), (90, 10, 16)), (s2, y2, sc2, (255, 222, 40), (40, 0, 0))):
        x = int(540 - text_w(s_, sc) / 2)
        look.draw_cells(d, look.text_cells(s_, x + 10, y + 10, sc, sh), 0)
        look.draw_cells(d, look.text_cells(s_, x, y, sc, col), 7)
# the SHOP menu (top of the frame): SELL list with a cursor; later the last entry is the hero
MENU_EN = [('RUSTY SWORD', '1G'), ('BENT SPOON', '1G'), ('BROKEN SHIELD', '1G')]
MENU_TR = [('PASLI KILIÇ', '1A'), ('EĞRİ KAŞIK', '1A'), ('KIRIK KALKAN', '1A')]
SELL = 'SAT' if TRL else 'SELL'; HERO_ITEM = ('KAHRAMAN', '???') if TRL else ('HERO', '???')
GOLD = 'ALTIN' if TRL else 'GOLD'
def cursor(d, x, y, sc, col):
    d.polygon([(x - 3, y - 3), (x + 4 * sc + 3, y + 3.5 * sc), (x - 3, y + 7 * sc + 3)], fill=(0, 0, 0)); d.polygon([(x, y), (x + 4 * sc, y + 3.5 * sc), (x, y + 7 * sc)], fill=col)
def menu_overlay(im, t):
    d = ImageDraw.Draw(im); items = MENU_TR if TRL else MENU_EN
    if 0 <= t < T0['03']:
        cur = 0 if t < GULPS[0] - 1.2 else (1 if t < GULPS[1] - 1.2 else 2)
        sold = (1 if t >= T_COIN else 0) + sum(1 for g in GULPS if t >= g)
        x0, y0, w = 70, 110, 600
        d.rectangle([x0, y0, x0 + w, y0 + 60 + 62 * len(items) + 70], fill=(14, 10, 18)); d.rectangle([x0 + 6, y0 + 6, x0 + w - 6, y0 + 54 + 62 * len(items) + 64], outline=(170, 140, 90), width=4)
        look.draw_cells(d, look.text_cells('SHOP - ' + SELL, x0 + 30, y0 + 22, 5, (255, 214, 60)), 3)
        for i, (nm, pr) in enumerate(items):
            y = y0 + 74 + 62 * i; col = (110, 104, 96) if i < sold else ((255, 255, 255) if i == cur else (200, 196, 186))
            if i == cur and i >= sold: cursor(d, x0 + 22, y, 5, (255, 214, 60))
            look.draw_cells(d, look.text_cells(nm, x0 + 60, y, 5, col), 3); look.draw_cells(d, look.text_cells(pr, x0 + w - 30 - text_w(pr, 5), y, 5, col), 3)
        gy = y0 + 74 + 62 * len(items) + 4; look.draw_cells(d, look.text_cells(f'{GOLD} {12 + sold}', x0 + 30, gy, 5, (255, 214, 60)), 3)
    if T_MENU[0] <= t < T_MENU[1] and t >= 0:                                                    # the menu comes back. one entry.
        fl = 1.0 if (int(t * 18) % 7) else 0.35
        x0, y0, w = 70, 300, 600
        d.rectangle([x0, y0, x0 + w, y0 + 150], fill=(14, 6, 8)); d.rectangle([x0 + 6, y0 + 6, x0 + w - 6, y0 + 144], outline=(200, 40, 40), width=4)
        look.draw_cells(d, look.text_cells('SHOP - ' + SELL, x0 + 30, y0 + 22, 5, (255, 80, 70)), 3)
        nm, pr = HERO_ITEM; col = tuple(int(c * fl) for c in (255, 60, 60))
        cursor(d, x0 + 22, y0 + 86, 6, col); look.draw_cells(d, look.text_cells(nm, x0 + 64, y0 + 86, 6, col), 3)
        look.draw_cells(d, look.text_cells(pr, x0 + w - 30 - text_w(pr, 6), y0 + 86, 6, col), 3)
COL = {'N': (242, 238, 226), 'S': (226, 200, 255), 'K': (255, 196, 90)}
def _sub_scr():
    if not TRL: return SCR
    import importlib.util as _iu
    sp_ = _iu.spec_from_file_location('ms_tts', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'tts', 'ms.py'))
    m_ = _iu.module_from_spec(sp_); sp_.loader.exec_module(m_); TRS = m_.TR_SUB
    out = dict(SCR); sent = {}
    for k, v in SCR['sent'].items():
        if len(v) == len(TRS[k]): sent[k] = [[a, b, tx] for (a, b, _), tx in zip(v, TRS[k])]
        else: sent[k] = [[v[0][0], v[-1][1], ' '.join(TRS[k])]]
    out['sent'] = sent
    return out
SUBS = look.Subtitles(_sub_scr(), [x for x in LINES if x[0] != '00'], W, H, S, COL, title_key='none', n=17,
                      hil=({'ISLAKTI.', 'YOK.', 'MİMİKLER', 'DÜKKANI'} if TRL else {'WET.', 'BLINKED.', 'NO', 'MIMICS', 'SHOP.', 'EAT'}))
from nightkit import cta
CTA = cta.Achievement(t0=S4 + 0.9, lang=SUB_LANG, dur=F(0.5))
def frame_final(t):
    if t >= T_LOOPF: t = t - DUR
    img, vi = frame_low(t); arr = post.upscale(img, S)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); menu_overlay(im, t); cover_overlay(im, t)
    arr = np.asarray(im).astype(np.float32)
    arr = SUBS.apply(arr, t) if t >= 0 else arr
    arr = CTA.apply(arr, t) if t >= 0 else arr
    if t >= 0:
        bl = sm(seg01(t, T_JAW[1] - 0.05, T_JAW[1] + 0.02)) * (1 - sm(seg01(t, S5 - 0.02, S5)))          # black after the bite
        if bl > 0: arr = arr * (1 - bl)
    return arr

TEST = os.environ.get('TEST')
if TEST and __name__ == '__main__':
    if TEST == 'seq': ts = sorted(set([round(a + (b - a) * f, 2) for i, (n_, a) in enumerate(CUTS) for b in [CUTS[i + 1][1] if i + 1 < len(CUTS) else DUR] for f in (0.1, 0.5, 0.9)]))
    else: ts = [float(x) for x in TEST.split(',')]
    tw_ = int(os.environ.get('TW', '200')); th = tw_ * 16 // 9
    ims = [Image.fromarray(np.clip(frame_final(x), 0, 255).astype(np.uint8)) for x in ts]
    if os.environ.get('SZ') == 'full':
        for x, im in zip(ts, ims): im.save(f'test_ms_{x:.2f}.png')
    ims = [im.resize((tw_, th), Image.LANCZOS) for im in ims]
    per = int(os.environ.get('PER', '9')); rows = (len(ims) + per - 1) // per; shp = Image.new('RGB', (min(per, len(ims)) * (tw_ + 2), rows * (th + 18)), (30, 30, 30))
    dd = ImageDraw.Draw(shp)
    for i, (im, x) in enumerate(zip(ims, ts)): shp.paste(im, ((i % per) * (tw_ + 2), (i // per) * (th + 18))); dd.text(((i % per) * (tw_ + 2) + 4, (i // per) * (th + 18) + th + 3), f'{x:.2f} {x / 1.2:.1f}f {scene(x)}', fill=(255, 255, 0))
    shp.save(os.environ.get('TEST_OUT', 'test_ms.png')); print('test written', DUR, round(DUR / 1.2, 2), SEQS); sys.exit()

QA = dict(fps=FPS, dur=DUR, W=W, frame=lambda t: Image.fromarray(np.clip(frame_final(t), 0, 255).astype(np.uint8)).resize((W, H), Image.BOX), chars={},
          geom=lambda t, name, st, V_: [], camera=lambda t: cam_shot(t)[0], min_cam_dist=0.3, camera_ok=lambda p: True, allow_jump=[], weapon_events=[],
          scenes=[dict(id=nm, t0=a, t1=(CUTS[i + 1][1] if i + 1 < len(CUTS) else DUR), action=nm) for i, (nm, a) in enumerate(CUTS)],
          texts=lambda: [('hud', COVER[0], 12), ('hud', COVER[1], 13)])

# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as _sf
    s = Sound(DUR, loop=False, seed=97); sr = s.sr; n = s.n; t = s.t
    BED = np.zeros(n); FX = np.zeros(n); MUS = np.zeros(n)
    def put(buf, x, t0, v=1.0):
        i = int(round(t0 * sr))
        if i >= n or i + len(x) <= 0: return
        if i < 0: x = x[-i:]; i = 0
        j = min(n, i + len(x)); buf[i:j] += (x * v)[:j - i]
    def tone(t0, m, d, v, dec=3.0, att=0.005, glide=0.0, buf=None, harm=(1.0,)):
        f = 440 * 2 ** ((m - 69) / 12); tt = s.T(d); fr_ = f * (1 + glide * tt / d); ph = np.cumsum(fr_) / sr
        x = sum(a * np.sin(2 * np.pi * ph * (k + 1)) for k, a in enumerate(harm)); put(FX if buf is None else buf, x * np.minimum(1, tt / att) * np.exp(-tt * dec), t0, v)
    def nb(t0, d, lo, hi, v, seed, shape=2, buf=None): put(FX if buf is None else buf, s.filt_short(s.noise(d, seed), lo=lo, hi=hi) * np.sin(np.pi * s.T(d) / d) ** shape, t0, v)
    def thud(t0, f=60, v=0.1, d=0.3): tt = s.T(d); put(FX, np.sin(2 * np.pi * f * tt * (1 - 0.3 * tt / d)) * np.exp(-tt * 14), t0, v)
    def step(t0, v=0.03, seed=0): tt = s.T(0.12); put(FX, s.filt_short(s.noise(0.12, seed), lo=150, hi=1800) * np.exp(-tt * 30) + np.sin(2 * np.pi * 75 * tt) * np.exp(-tt * 26) * 0.3, t0, v)
    def mask(a, b, r=0.15): return np.clip(np.minimum((t - a) / r, (b - t) / r), 0, 1)
    def squelch(t0, v=0.05, seed=0, d=0.35):
        tt = s.T(d); x = s.filt_short(s.noise(d, seed), lo=120, hi=900) * np.sin(np.pi * tt / d) ** 1.2 * (1 + 0.8 * np.sin(2 * np.pi * (18 + 30 * tt) * tt)); put(FX, x, t0, v)
    outside = mask(S5, DUR + 1, 0.02); inside = 1 - outside
    # room: low drone that never resolves, the counter BREATHING (in time with the lid), candle, clock-less silence
    BED += s.filt(s.rng.normal(0, 1, n), lo=40, hi=160) * 0.02 * inside
    BED += (np.sin(2 * np.pi * 55 * t) * 0.006 + np.sin(2 * np.pi * 58.3 * t) * 0.005) * inside
    breath = (0.5 + 0.5 * np.sin(2 * np.pi * 0.32 * t)) ** 3
    BED += s.filt(s.rng.normal(0, 1, n), lo=200, hi=1200) * 0.012 * breath * inside * (1 - mask(T_LID[0], S5, 0.1))
    BED += s.filt(s.rng.normal(0, 1, n), lo=150, hi=1500) * 0.012 * outside                         # night wind outside
    # music: a broken music box (minor, detuned, slowing), out for the reveal
    notes = [76, 79, 83, 79, 76, 75, 76, 72, 71, 72, 76, 71]
    x = 0.4; k = 0
    while x < S4 - 0.2:
        m = notes[k % len(notes)]; tone(x, m, 0.9, 0.012, dec=4.0, harm=(1.0, 0.0, 0.35), buf=MUS); tone(x + 0.003, m + 0.12, 0.9, 0.006, dec=4.0, buf=MUS)
        x += 0.42 + 0.01 * k * (1 if x > S2 else 0); k += 1
    MUS *= (1 - mask(T_RIP[0] - 0.2, DUR + 1, 0.3))
    # hook: low hit + dissonant cluster; a sting on 'JUNK'
    thud(0.02, 46, 0.2, 0.6); [tone(0.03, m, 1.4, 0.02, dec=1.8, harm=(1.0, 0.4)) for m in (40, 41, 47)]
    thud(T_PUNCH, 60, 0.1, 0.3); tone(T_PUNCH, 88, 0.4, 0.012, dec=6)
    # sales: the coin (wet clink), the gulps
    tone(T_COIN + 0.35, 100, 0.2, 0.02, dec=18, harm=(1.0, 0.5)); squelch(T_COIN + 0.36, 0.02, 3, 0.15)
    for i, g in enumerate(GULPS): squelch(g, 0.07, 10 + i, 0.4); thud(g + 0.1, 50, 0.06, 0.3)
    # wet coin drip in his palm
    for k in range(3): tone(T_PALM + 0.4 + 0.45 * k, 98 + k, 0.08, 0.008, dec=30)
    # 'There is no back room.' -> silence -> the floor, the lid creak, teeth, wet tongue, a growl
    tt = s.T(1.2); put(FX, np.sin(2 * np.pi * (38 + 6 * np.sin(tt * 7)) * tt) * np.sin(np.pi * tt / 1.2) * (1 + 0.5 * s.filt_short(s.noise(1.2, 61), lo=30, hi=200) * 6), T_RIP[0], 0.08)
    for k in range(5): s.creak(T_RIP[0] + 0.15 * k + 0.1, v=0.02, f0=300 + 60 * k)
    tt = s.T(1.0); put(FX, np.sin(2 * np.pi * (180 + 90 * np.sin(tt * 11)) * tt) * np.exp(-tt * 2) * np.sin(np.pi * tt / 1.0), T_LID[0], 0.03)
    squelch(T_LID[0] + 0.4, 0.09, 62, 0.6); squelch(T_RISE[0] + 0.2, 0.08, 63, 0.7)
    tt = s.T(2.2); put(FX, s.filt_short(s.noise(2.2, 64), lo=40, hi=260) * np.sin(np.pi * tt / 2.2) * (1 + 0.6 * np.sin(2 * np.pi * 11 * tt)), T_LID[1] - 0.2, 0.12)
    for k, m in enumerate((36, 37, 43)): tone(T_LID[0] + 0.3 + 0.1 * k, m, 2.4, 0.03, dec=1.2, harm=(1.0, 0.6, 0.4, 0.2))
    # menu beep (SELL: HERO), glitchy
    for k in range(6): tone(T_MENU[0] + 0.07 * k, 84 - (k % 2) * 6, 0.06, 0.012, dec=20)
    # run, the bite, black
    x = T_RUN[0] + 0.25
    while x < T_JAW[0]: step(x, 0.05, int(x * 30)); x += 0.24
    thud(T_JAW[1], 40, 0.3, 0.6); nb(T_JAW[1], 0.2, 800, 6000, 0.08, 71, 0.6); [tone(T_JAW[1] + 0.02, m, 0.4, 0.02, dec=8, harm=(1.0, 0.5)) for m in (60, 66)]
    # outside: running steps, the eyes open (two low tones + a wet blink), a deep breath from the house
    x = S5 + 0.1
    while x < S5 + 2.4: step(x, 0.04 * max(0.2, 1 - (x - S5) / 2.6), int(x * 40)); x += 0.24
    for k, m in enumerate((33, 39)): tone(T_EYES[0] + 0.1 * k, m, 2.5, 0.035, dec=0.9, harm=(1.0, 0.5, 0.3))
    squelch(T_EYES[0] + 0.05, 0.05, 72, 0.4)
    tt = s.T(2.0); put(FX, s.filt_short(s.noise(2.0, 73), lo=60, hi=400) * np.sin(np.pi * tt / 2.0) ** 2, tend('09') - 0.6, 0.06)
    x = T_NEXT - 0.5
    while x < T_LOOPF: step(x, 0.025, int(x * 50)); x += 0.5
    if CTA.on: put(FX, cta.chime(sr), CTA.t0, 1.0)
    # voice
    NB = np.zeros(n); wins = []
    for k_, t0 in LINES:
        f_ = os.path.join(TTS_DIR, 'ms', f'{k_}.wav')
        if not os.path.exists(f_): continue
        a, ar = _sf.read(f_); a = a if a.ndim == 1 else a.mean(1)
        a = np.interp(np.arange(int(len(a) * sr / ar)) / sr, np.arange(len(a)) / ar, a); act = np.abs(a) > 0.02 * np.abs(a).max()
        a = a * (0.12 / np.sqrt((a[act] ** 2).mean())); put(NB, a, t0); wins.append((t0, t0 + len(a) / sr))
    gd = duck_envelope(n, sr, wins, -7.0, 0.05, 0.25) if wins else np.ones(n)
    bed = BED * gd + MUS * (0.6 + 0.4 * gd); fx = FX * (0.6 + 0.4 * gd)
    L = bed + fx; R_ = np.roll(bed, 700) + np.roll(fx, 200)
    pk = max(np.abs(L).max(), np.abs(R_).max()); gv = (pk * 1.6 / np.abs(NB).max()) if np.abs(NB).max() > 0 else 0.0
    s.L = L + NB * gv; s.R = R_ + NB * gv; s.reverb(0.16, length=1.6, decay=3.0)
    fi = np.clip(t / 0.008, 0, 1); s.L = s.L * fi; s.R = s.R * fi
    return s.save(path, peak=0.9)
if __name__ == '__main__' and os.environ.get('PART') == 'audio':
    print(build_audio(os.path.join(OUT, os.environ.get('AUDIO_NAME', 'mimic_shop.wav')))); sys.exit()
if __name__ == '__main__' and os.environ.get('PART'):
    a, b = map(int, os.environ['PART'].split(':'))
    import subprocess
    p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W * S}x{H * S}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', os.path.join(OUT, f"{os.environ.get('PART_PREFIX', 'ms')}_{a:05d}.mp4")], stdin=subprocess.PIPE)
    vhs = post.VHS(W * S, H * S, S, grade='none', chroma=0, scan_dark=1.0, vignette=0.45, grain=1.2, band_period=1e9)
    for f in range(a, min(b, N)): p.stdin.write(vhs(frame_final(f / FPS), f, f / FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done', a, b); sys.exit()
