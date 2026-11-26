"""WHY DO BRIDGE TROLLS WANT TOLLS? (Insert Disc 2, 26 Nov 2026) ~35 s final (x1.2 after), nightkit HD, 9:16.
Brief: briefs/BRIDGE_TROLL_FULL_BRIEF.txt (Claude pitch, Enes approved 26 Nov). Voices: Enes's cloned voice, tools/tts/bt.py.
Reuses: forget_potion's stone bridge (night / dawn) + lantern, dragon_taxes' knight + old woman + purse sack + coins.
New: the TROLL (hd.human 2.45 m + nose, ears, tusks, moss), toll bucket, trowel, crack + patch, falling stone, dust, BRIDGE HP HUD.

Enes (26 Nov): render in at most 5 SEQUENCES, so a fix only re-renders one of them:
  python tools/render_seq.py examples/bridge_troll.py --prefix bt --seqs s1,s2,s3,s4,s5      # -> ../renders/bridge_troll/seq/<s>.mp4
  python tools/render_seq.py examples/bridge_troll.py --prefix bt --master <out.mp4>          # concat + audio + x1.2
Stills: TEST=0,0.5,1.0 python examples/bridge_troll.py -> test_bt.png   (TEST=seq: 3 stills per shot)"""
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
seg01, win, lerp, lerp3, hsh, ang_to = fp.seg01, fp.win, fp.lerp, fp.lerp3, fp.hsh, fp.ang_to
mixc = fp.mixc
SUB_LANG = os.environ.get('SUB_LANG', 'en'); TRL = SUB_LANG == 'tr'
def F(x): return round(x * 1.2, 4)                  # final seconds -> build seconds
deck_y, bank_y, BW = fp.deck_y, fp.bank_y, fp.BW

# ======================= cast =======================
TROLL = hd.spec(h=2.45, build=1.7, skin=(118, 134, 98), hair=(118, 134, 98), hair_style='bald', eye=(214, 176, 70), brow=(52, 60, 40),
                lip=(92, 98, 72), tunic=(84, 70, 54), tunic2=(70, 58, 44), sleeves='none', skirt=0.36, pants=(112, 128, 94),
                boots=(92, 106, 78), belt=(140, 116, 76), buckle=(150, 140, 120))
TK = TROLL['h'] / 1.78
KNIGHT = dtx.KNIGHT; WOMAN = dtx.WOMAN
TSKIN = TROLL['skin']; TSKIN_D = hd.shade(TSKIN, 0.8); MOSS = (64, 98, 50); MOSS2 = (84, 116, 58); IVORY = (232, 224, 192)
def troll(P):
    """hd.human + the troll parts: big nose, pointed ears, two tusks, a heavy brow ridge, moss on the shoulders and the scalp"""
    Q = hd.human(TROLL, P); hc = P['_head']; RH = P['_RH']; RW = P['_RW']; k = TK
    Z = hd._ZF[(round(k, 3), 0.0)]
    def L(x, y, z): return hc + RH @ V((x, y, z))
    Q += hd.ellip(L(0, -0.02 * k, Z['nose'] + 0.012 * k), RH, (0.026 * k, 0.03 * k, 0.026 * k), 9, 6, hd.shade(TSKIN, 0.94))   # bulb nose
    Q += hd.ellip(L(0, 0.037 * k, Z['browR'] - 0.012 * k), RH, (0.06 * k, 0.01 * k, 0.016 * k), 10, 4, TSKIN_D)            # brow ridge
    for sd in (1, -1):
        b0 = L(sd * 0.086 * k, 0.016 * k, -0.008 * k); b1 = L(sd * 0.086 * k, -0.018 * k, 0.002 * k); tp_ = L(sd * 0.168 * k, 0.04 * k, -0.022 * k)
        mid = (b0 + b1) / 2; ins = [mid + (b0 - mid) * 0.6 + RH @ V((sd * 0.004, 0, 0.002)), mid + (b1 - mid) * 0.6 + RH @ V((sd * 0.004, 0, 0.002)), mid + (tp_ - mid) * 0.7]
        for pts, col in (([b0, b1, tp_], TSKIN), ([b1, b0, tp_], TSKIN)):
            q = hd.face(pts, col)
            if q: Q.append(q)                                                                                       # pointed ear (flat leaf, both sides)
        t0 = L(sd * 0.021 * k, -0.06 * k, Z['mouth'] + 0.004 * k); t1 = t0 + RH @ V((sd * 0.004, 0.026 * k, 0.006))
        Q += hd.limb(t0, t1, 0.007 * k, 0.0015, IVORY, n=5, m=1)                                                           # tusk
    for i, (x, y, z, r) in enumerate(((0.17, 0.12, -0.02, 0.07), (-0.16, 0.13, 0.0, 0.06), (0.1, 0.16, -0.06, 0.05), (-0.06, 0.15, -0.08, 0.045))):
        c = P['_chest'] + RW @ V((x * k / 1.38 * 1.7 / 1.7, y, z)); Q += hd.ellip(c, RW, (r, r * 0.45, r), 7, 4, MOSS if i % 2 else MOSS2)
    Q += hd.ellip(L(0.02 * k, 0.1 * k, -0.02 * k), RH, (0.05 * k, 0.02 * k, 0.045 * k), 7, 3, MOSS)                       # moss on the scalp
    return [q for q in Q if q]
def knight(P): return dtx.knight(P)

# ======================= set =======================
TP = (-7.9, 0.0, -1.75)                        # the troll's toll spot, beside the road at the west end of the bridge
TRV = (-8.95, 0.0, -0.3)                       # where a traveller stops (the camera of frame 0 = the traveller's eyes)
TP_YAW = ang_to(TP, TRV)
def wpt(base, yaw, l): return V(base, float) + hd.Ry(yaw) @ V(l, float)
BUCKET = tuple(wpt(TP, TP_YAW, (-0.55, 0.0, 0.32)))      # on his left, a little in front
POST = tuple(wpt(TP, TP_YAW, (0.62, 0.0, -0.5)))          # lantern post on his right, behind
BK_R = 0.16; BK_H = 0.27
def bucket(fill=0.0, coins_top=3):
    """wooden toll bucket; the coin heap rises out of the dark inside as `fill` (0..1) grows"""
    b = V(BUCKET, float); Q = []
    Q += hd.lathe(tuple(b), np.eye(3), [(BK_R * 0.86, 0.0), (BK_R, BK_H)], 12, (122, 86, 52), colfn=lambda i, j: (104, 72, 44) if i % 2 else (122, 86, 52), cap1=False)
    for y in (0.05, BK_H - 0.04): Q += hd.limb(tuple(b + V((0, y - 0.012, 0))), tuple(b + V((0, y + 0.012, 0))), BK_R * (0.88 + 0.12 * y / BK_H) + 0.006, BK_R * (0.88 + 0.12 * y / BK_H) + 0.006, (70, 66, 62), n=12, m=1)
    top = b + V((0, BK_H, 0)); ring = [(BK_R * 0.96 * math.cos(2 * PI * i / 14), BK_R * 0.96 * math.sin(2 * PI * i / 14)) for i in range(14)]
    Q += hd.poly_decal(tuple(top), (0, 1.0, 0), (0, 0, 1.0), ring, (40, 28, 18), lift=0.0)
    if fill > 0.01:                                                                   # heap of coins
        hgt = 0.075 * fill; Q += hd.ellip(tuple(top + V((0, -0.03 + hgt * 0.6, 0))), np.eye(3), (BK_R * 0.9, 0.03 + hgt * 0.5, BK_R * 0.9), 12, 5, (222, 176, 62),
                                         colfn=lambda i, j, cl: (250, 212, 96) if (i + j) % 3 == 0 else (222, 176, 62), v1=PI * 0.5)
    n = coins_top + int(16 * fill)
    for i in range(n):
        a = 2 * PI * hsh(i, 61); r = BK_R * 0.75 * math.sqrt(hsh(i, 62)); y = 0.004 + (0.075 * fill * (1 - (r / BK_R) ** 2) * 0.9 if fill > 0.01 else 0.0)
        Q += dtx.coin(tuple(top + V((r * math.cos(a), y, r * math.sin(a)))), hd.Rx(0.5 * (hsh(i, 63) - 0.5)) @ hd.Rz(0.5 * (hsh(i, 64) - 0.5)), s=1.1)
    return [q for q in Q if q]
def trowel(grip, d, n):
    """mason's trowel: wooden handle + a flat diamond steel blade that leaves the handle at the tip end (n = blade face normal)"""
    g = V(grip, float); d = hd.nz(V(d, float)); n = hd.nz(V(n, float)); w = hd.nz(np.cross(d, n))
    Q = hd.limb(tuple(g - d * 0.05), tuple(g + d * 0.07), 0.016, 0.014, (120, 84, 50), n=6, m=1)
    Q += hd.limb(tuple(g + d * 0.07), tuple(g + d * 0.1 - n * 0.03), 0.006, 0.006, (90, 90, 96), n=4, m=1)
    c = g + d * 0.1 - n * 0.035
    Q.append(hd.face([c - d * 0.01, c + d * 0.08 + w * 0.06, c + d * 0.2, c + d * 0.08 - w * 0.06], (196, 200, 206)))
    Q.append(hd.face([c + d * 0.2, c + d * 0.08 + w * 0.06, c - d * 0.01, c + d * 0.08 - w * 0.06], (150, 154, 160)))
    return [q for q in Q if q]
def trowel_rest():
    """leaning in the bucket at night (frame 0 shows it next to him)"""
    b = V(BUCKET) + V((0.04, BK_H + 0.02, 0.0)); return trowel(tuple(b + V((0.0, 0.1, 0.0))), (0.15, -0.9, 0.2), (0.9, 0.1, -0.3))
def toll_post(on=1.0, t=0.0):
    p = V(POST, float); Q = hd.limb(tuple(p), tuple(p + V((0, 2.35, 0))), 0.06, 0.05, (60, 46, 34), n=6, m=1)
    arm = p + V((0, 2.3, 0)); f = hd.nz(V(TP) - p); f[1] = 0; f = hd.nz(f); Q += hd.limb(tuple(arm), tuple(arm + f * 0.42), 0.03, 0.03, (60, 46, 34), n=5, m=1)
    c = arm + f * 0.4 + V((0, -0.32, 0)); Q += hd.limb(tuple(c + V((0, 0.2, 0))), tuple(c + V((0, 0.3, 0))), 0.008, 0.008, (40, 30, 24), n=4, m=1)
    Lq = hd.lathe(tuple(c), np.eye(3), [(0.07, 0), (0.1, 0.05), (0.1, 0.18), (0.045, 0.23)], 8, mixc((90, 70, 50), (255, 214, 130), on))
    for q in Lq: q['emit'] = on > 0.2
    return [q for q in Q + Lq if q], tuple(c + V((0, 0.1, 0)))
# ---- the crack on the downstream (-z) face, over the crown of the arch, and its patch at dawn
FZ = -1.185
CRACK = [(0.24, 1.95), (0.13, 1.86), (0.19, 1.78), (0.05, 1.7), (0.11, 1.62), (-0.01, 1.56), (0.03, 1.5)]
def crack_faces(u, patch=0.0):
    """u = how far the crack has run (0..1); patch = how much is filled with fresh mortar (0..1, from the top)"""
    Q = []; n = len(CRACK) - 1
    for i in range(n):
        a = V((CRACK[i][0], CRACK[i][1], FZ)); b = V((CRACK[i + 1][0], CRACK[i + 1][1], FZ)); g = max(0.0, min(1.0, u * n - i))
        if g <= 0: break
        b = a + (b - a) * g; d = hd.nz(b - a); w = np.cross(d, V((0, 0, -1.0))) * (0.024 - 0.008 * i / n)
        pf = max(0.0, min(1.0, patch * n - i))
        if pf > 0.02:
            m = a + (b - a) * pf; w2 = w * 1.9
            Q.append(hd.face([a - w2, m - w2, m + w2, a + w2], (184, 176, 156)))
            if pf < 1.0: Q.append(hd.face([m - w, b - w, b + w, m + w], (22, 16, 14)))
        else: Q.append(hd.face([a - w, b - w, b + w, a + w], (22, 16, 14)))
    return [q for q in Q if q]
STONE0 = V((0.06, 1.47, -0.75))
def falling_stone(t, t0):
    """a voussoir chunk drops from the crown into the stream and is gone"""
    if t < t0 - 0.05: return []
    u = t - t0; y = STONE0[1] - 4.9 * max(0.0, u) ** 2
    if y < -0.45: return []
    c = STONE0 + V((0.03 * u, y - STONE0[1], -0.25 * u)); R = hd.Rx(2.5 * u) @ hd.Rz(1.3 * u)
    return hd.bx(tuple(c), R, (0.1, 0.06, 0.12), (124, 120, 112))
def splash(t, t0):
    u = t - t0
    if not (0 <= u < 0.5): return []
    Q = []
    for i in range(12):
        a = 2 * PI * i / 12; r = 0.08 + 0.45 * u; y = -0.3 + 1.6 * u - 4.9 * u * u
        Q += hd.bx((STONE0[0] + r * math.cos(a), max(-0.31, y), STONE0[2] - 0.65 + r * math.sin(a)), np.eye(3), (0.012, 0.012, 0.012), (200, 214, 230), emit=True)
    return [q for q in Q if q]
def dust(t, a, b, rate=1.0, seed=0, x0=0.05, z0=-0.9, y0=1.5, spread=0.5):
    """grit falling off the crown (under the arch) while [a, b)"""
    if not (a <= t < b + 1.0): return []
    Q = []
    for i in range(int(30 * rate)):
        ph = hsh(i, seed + 1) * 1.2; u = ((t - a) + ph) % 1.2
        if t - u < a or t - u > b: continue
        x = x0 + spread * (hsh(i, seed + 2) - 0.5); z = z0 + spread * 1.6 * (hsh(i, seed + 3) - 0.5); y = y0 - 4.9 * u * u
        if y < -0.3: continue
        s_ = 0.006 + 0.006 * hsh(i, seed + 4); Q += hd.bx((x, y, z), np.eye(3), (s_, s_, s_), (150, 140, 124))
    return [q for q in Q if q]
_SET = []
def set_faces():
    if not _SET: _SET.append(fp.bridge_set() + road())
    return _SET[0]
def road():
    """dirt road onto the west ramp + a few stones by the toll spot"""
    Q = []
    for i, x in enumerate(np.arange(-14.0, -6.9, 0.7)):
        for j, z in enumerate(np.arange(-0.84, 0.84, 0.56)):
            Q.append(hd.face([(x, 0.004, z), (x, 0.004, z + 0.56), (x + 0.7, 0.004, z + 0.56), (x + 0.7, 0.004, z)], hd.shade((104, 88, 66), 0.9 + 0.15 * hsh(i * 7 + j, 71))))
    for i in range(5): Q += fp.rock((-8.6 + 1.1 * hsh(i, 72) - 0.4, 0.04, -2.6 - 0.9 * hsh(i, 73)), 0.12 + 0.1 * hsh(i, 74), (100, 96, 90), seed=i + 20)
    return [q for q in Q if q]
_SKY = {}
def sky(kind):
    if kind not in _SKY:
        if kind == 'night': _SKY[kind] = fp.sky_disc((-14, 16, 30), 1.2, (214, 222, 240)) + fp.stars(17, 60, 32, 5, 26, -30, 30)
        else: _SKY[kind] = fp.sky_disc((26, 3.4, 16), 1.6, (255, 236, 186))
    return _SKY[kind]

# =====================================================================================================================
#                                                      TIMELINE
# =====================================================================================================================
from nightkit.audio import Sound, duck_envelope
OUT = 'out'; os.makedirs(OUT, exist_ok=True)
TTS_DIR = os.environ.get('TTS_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tts'))
SCR = json.load(open(os.path.join(TTS_DIR, 'bt', 'script.json'), encoding='utf-8'))
KEYS = ['%02d' % i for i in range(0, 13)]
# gaps after each line (build s); the sequence breaks add their own action time
GAP = {'01': 0.3, '02': 0.25, '03': 1.05, '04': 0.35, '05': 1.45, '06': 0.35, '07': 0.2, '08': 1.0, '09': 0.75, '10': 0.75, '11': 2.2, '12': 0.35}
LEAD = {'01': 0.25, '04': 0.35, '06': 0.6, '09': 0.3, '11': 0.5}          # sequence starts: action before the first line
# HOOK (Enes 26 Nov: 'no hook'): the narrator says the title first, over the troll close-up, then the troll asks US for a coin.
# The hook block is a WHOLE number of frames, so every later sequence only shifts by whole frames and its rendered file stays valid.
HOOK_LEAD = 0.15
HOOK = math.ceil((HOOK_LEAD + SCR['dur']['00'] + 0.45) * FPS) / FPS
def _lines():
    t = HOOK; out = [('00', HOOK_LEAD)]
    for k in KEYS[1:]:
        t += LEAD.get(k, 0.0); out.append((k, round(t, 3))); t += SCR['dur'][k] + GAP[k]
    return out, t
LINES, _T_END = _lines(); T0 = dict(LINES)
def tend(k): return T0[k] + SCR['dur'][k]
def ws(k, i): return T0[k] + SCR['sent'][k][i][0]
# sequences (Enes: <= 5, rendered separately)
S2 = T0['04'] - LEAD['04']; S3 = T0['06'] - LEAD['06']; S4 = T0['09'] - LEAD['09']; S5 = T0['11'] - LEAD['11']
T_EVE = tend('12') + GAP['12']                     # night again: the next traveller walks up
T_LOOPF = T_EVE + 0.95                             # frame-0 framing at negative time (the moment before frame 0)
DUR = round(T_LOOPF + 0.5, 3); N = int(round(DUR * FPS))
def fr(x): return int(round(x * FPS))
SEQS = [('s1', 0, fr(S2)), ('s2', fr(S2), fr(S3)), ('s3', fr(S3), fr(S4)), ('s4', fr(S4), fr(S5)), ('s5', fr(S5), N)]
# beats
T_PALM = (T0['01'] - 0.55, T0['01'] + 0.3)        # after the title: his palm comes up toward the traveller (= us)
T_THREAT = (T0['02'] - 0.1, T0['02'] + 0.45)        # knight raises the sword at him
T_ASIDE = (T0['03'] + 0.2, T0['03'] + 1.1)          # troll steps aside, sweeps his arm to the bridge
T_PASS = (T0['03'] + 0.9, S2 + 0.0)                 # knight walks past onto the ramp
T_GROAN = ws('04', 1) - 0.05                        # "The bridge did."
T_CRACK = tend('05') - 0.25                         # "...cracked."
T_FALL = T_CRACK + 0.35
T_SNAP = T_CRACK + 0.85                             # the troll at his post hears it
T_RUN = T_SNAP + 0.3
T_LOWER = (tend('08') + 0.1, tend('08') + 0.8)      # knight looks at his sword and lowers it
T_POUR = (T0['09'] + 0.45, T0['09'] + 2.3)          # purse turned over, coins rain into the bucket
N_COIN = 24
T_PAT = (tend('11') + 0.25, tend('11') + 1.0)       # WORDLESS: palm flat on the stone
T_KWAVE = (tend('11') + 1.1, tend('11') + 2.0)      # the knight on the far bank looks back, lifts his hand
CUTS = [('open', 0.0), ('knight', T0['02'] - 0.2), ('aside', T0['03'] - 0.15),
        ('walk', S2), ('crack', T_CRACK - 0.45), ('react', T_SNAP - 0.15),
        ('hold', S3), ('kn3', T0['07'] - 0.15), ('tr3', T0['08'] - 0.15),
        ('pay', S4), ('bucket', T0['10'] - 0.35),
        ('dawn', S5), ('wl', tend('11') + 0.1), ('far', T_KWAVE[0] - 0.05), ('wide', T0['12'] - 0.2), ('eve', T_EVE), ('loop', T_LOOPF)]
def scene(t):
    if t < 0: return 'loop'
    nm = CUTS[0][0]
    for n_, a in CUTS:
        if t >= a: nm = n_
    return nm
NIGHT = {'open', 'knight', 'aside', 'walk', 'crack', 'react', 'hold', 'kn3', 'tr3', 'pay', 'bucket', 'eve', 'loop'}
def talking(t, key):
    if key not in T0: return None
    for a, b, _ in SCR['sent'][key]:
        if T0[key] + a <= t < T0[key] + b: return 'open' if (t * 7.3 + 0.2 * math.sin(t * 13)) % 1.0 < 0.55 else 'neutral'
    return None
def say(P, t, keys):
    for k in keys:
        m = talking(t, k)
        if m: P['mouth'] = m

# =====================================================================================================================
#                                                      POSES
# =====================================================================================================================
TB = (0.32, -0.55, -0.12)                           # troll under the arch, in the stream, facing downstream (-z)
TD = (0.62, -0.55, -1.72)                           # dawn: in the stream at the downstream face, right of the crack
def troll_pose(t):
    sc = scene(t)
    if sc in ('open', 'knight', 'aside', 'react', 'eve', 'loop') or t < S2:
        P = dict(base=TP, yaw=TP_YAW, eyes='half', mouth='neutral', brow=0.15, lean=0.3, nod=0.32)
        P['rh'] = (0.34, 0.95, 0.1); P['lh'] = (-0.34, 0.95, 0.08); P['rgrip'] = 0.35; P['lgrip'] = 0.35
        tt = t if t >= 0 else t
        if sc == 'loop' or sc == 'eve': tt = t if t < 0 else -0.6 - 0.0 * t       # waiting, palm not up yet
        up = sm(seg01(tt, *T_PALM)) * (1 - sm(seg01(t, T_ASIDE[0] - 0.1, T_ASIDE[0] + 0.3))) if t < S2 or t < 0 else 0.0
        if sc == 'eve': up = 0.0
        tgt = wpt(TP, TP_YAW, (0.24, 1.84, 0.68))
        if up > 0:
            P['rh_w'] = tuple(lerp3(wpt(TP, TP_YAW, (0.34, 0.95, 0.1)), tgt, up)); P['rpalm'] = (0, 1.0, 0.15); P['rpalm_local'] = False; P['rgrip'] = 0.1; P['rpole'] = (0.5, -1.0, -0.2)
            P.pop('rh', None)
        if 0 <= t < T0['01'] + 0.3:                                                          # hook: he straightens up over us (looms), then leans in to ask
            rise = win(t, 0.0, T0['01'] + 0.3, 0.7); P['lean'] = 0.3 - 0.2 * rise; P['nod'] = 0.32 - 0.12 * rise
            if t >= T_PUNCH - 0.1: P['eyes'] = 'open'; P['brow'] = 0.45
        if 0 <= t < T0['02']: P['eyes'] = 'half' if t < ws('01', 1) - 0.1 else 'open'; P['brow'] = 0.2
        say(P, t, ('01', '03'))
        if T0['02'] - 0.1 <= t < T0['03']: P['eyes'] = 'half'; P['brow'] = -0.1; P['nod'] = 0.05; P['mouth'] = 'neutral' if t < tend('02') else 'soft'
        if t >= T_ASIDE[0] and t < S2:                                                      # one step back off the road, arm toward the bridge
            a = sm(seg01(t, *T_ASIDE)); P['base'] = tuple(lerp3(TP, wpt(TP, TP_YAW, (-0.35, 0, -0.35)), a))
            P['yaw'] = TP_YAW + 0.6 * a; P['lh'] = lerp3((-0.34, 0.95, 0.08), (-0.62, 1.32, 0.32), a); P['lgrip'] = 0.1; P['lpalm'] = (0, 1.0, 0.3)
            P['head'] = (0.35 * a, 0.05, 0.0); P['eyes'] = 'half'
        if sc == 'react':                                                                  # the crack: head snaps round, then he runs
            P['base'] = TP; P['yaw'] = TP_YAW; s_ = sm(seg01(t, T_SNAP, T_SNAP + 0.18))
            P['head'] = (1.1 * s_, 0.0, 0.0); P['eyes'] = 'wide' if s_ > 0.5 else 'half'; P['brow'] = -0.6 * s_; P['mouth'] = 'o' if s_ > 0.5 else 'neutral'
            r = max(0.0, t - T_RUN)
            if r > 0:
                dirr = hd.nz(V((-3.2, 0, -2.0)) - V(TP)); P['base'] = tuple(V(TP) + dirr * (2.6 * r + 0.6 * r * r)); P['yaw'] = lerp(TP_YAW, math.atan2(dirr[0], dirr[2]), sm(seg01(t, T_RUN, T_RUN + 0.25)))
                P['walk'] = r * 11.0; P['stride'] = 0.55; P['lift'] = 0.2; P['lean'] = 0.35; P['head'] = (0.0, 0.0, 0.0)
                for kk in ('rh', 'lh', 'rh_w'): P.pop(kk, None)
        return P, None
    if sc in ('walk', 'crack'):                                                             # (not seen: at his post)
        return dict(base=TP, yaw=TP_YAW, eyes='half', mouth='neutral', brow=0.1, lean=0.16), None
    if sc in ('hold', 'kn3', 'tr3', 'pay', 'bucket'):                                       # under the arch, holding it up
        shake = 0.012 * math.sin(t * 37) + 0.008 * math.sin(t * 23)
        P = dict(base=TB, yaw=PI, crouch=0.44, lean=0.28, eyes='half', mouth='grit', brow=0.8, nod=0.32)
        P['rh_w'] = (TB[0] - 0.42 + shake, 1.41 + shake, TB[2] - 0.12); P['lh_w'] = (TB[0] + 0.4 - shake, 1.33 - shake, TB[2] - 0.1)
        P['rpalm'] = (0, 1.0, 0); P['lpalm'] = (0, 1.0, 0); P['rpalm_local'] = False; P['lpalm_local'] = False; P['rgrip'] = 0.15; P['lgrip'] = 0.15
        P['rf'] = (0.22, 0.075, 0.12); P['lf'] = (-0.22, 0.075, -0.18); P['rkpole'] = (0.3, 0, 1.0); P['lkpole'] = (-0.3, 0, 1.0)
        P['rpole'] = (0.8, -0.6, -0.2); P['lpole'] = (-0.8, -0.6, -0.2)
        if T0['06'] <= t < tend('06'): P['eyes'] = 'open'; P['nod'] = 0.18
        if t >= T0['07'] - 0.1: P['head'] = (0.45, 0.12, 0.0); P['eyes'] = 'open'                    # looks at the knight on the bank
        say(P, t, ('06', '08', '10'))
        if T0['08'] <= t < tend('08') + 0.3: P['brow'] = -0.2
        return P, None
    # dawn: he faces the camera on the west side with the wall on his right: the RIGHT hand patches the crack with the trowel,
    # then the trowel goes into his belt and the right palm lies flat on the stone (wordless beat)
    P = dict(base=TD, yaw=TD_YAW, eyes='open', mouth='soft', brow=-0.1, lean=0.1, nod=0.05)
    tip = V((0.06 + 0.06 * math.sin(t * 5.0), 1.74 - 0.18 * (0.5 + 0.5 * math.sin(t * 2.1)), FZ - 0.02))
    stroke = 1.0 - sm(seg01(t, T_PAT[0] - 0.4, T_PAT[0]))
    rest_g = wpt(TD, TD_YAW, (0.34, 0.98, 0.12))
    g = lerp3(rest_g, tip - TROW_D * 0.33, stroke)
    P['rh_w'] = tuple(g); P['rgrip'] = 0.85; P['rpalm'] = (0, 0, -1.0); P['rpole'] = (0.8, -1.0, -0.4)
    P['lh'] = (-0.36, 1.0, 0.12)
    if stroke > 0.02: P['head'] = (0.45, 0.1, 0.0)                                         # watching his own work
    pat = sm(seg01(t, *T_PAT))
    if pat > 0:                                                                            # right palm flat on the stone, eyes closed a moment
        P['rh_w'] = tuple(lerp3(rest_g, PAT_PT - V((0, 0, 0.05)), pat)); P['rpalm'] = (0, 0, 1.0); P['rpalm_local'] = False; P['rgrip'] = 0.0
        P['nod'] = lerp(0.05, 0.15, pat); P['head'] = (0.55 * pat, 0.12, 0.0)
        P['eyes'] = 'closed' if T_PAT[1] - 0.2 <= t < T_PAT[1] + 0.55 else 'open'; P['mouth'] = 'smile' if t > T_PAT[1] else 'soft'
    if t >= T_KWAVE[0]: P['head'] = (lerp(0.55, -0.35, sm(seg01(t, T_KWAVE[0], T_KWAVE[0] + 0.4))), 0.0, 0.0); P['eyes'] = 'open'
    return P, (stroke, tip)
TD_YAW = -1.05
TROW_D = hd.nz(V((-0.3, 0.1, 1.0)))
PAT_PT = V((0.22, 1.42, FZ))
def troll_layer(t):
    P, tw = troll_pose(t); Q = troll(P)
    if tw is not None:
        stroke, tip = tw
        if stroke > 0.15 or t < T_PAT[0] - 0.4:
            g = fp.grip_pt(P, 'r', 0.07 * TK, 0.0); d = hd.nz(tip - g)
            Q += trowel(tuple(g), tuple(d), (0, 1.0, 0.0))
        else:                                                                              # tucked into his belt
            RP = P['_RW']; b0 = P['_pel'] + RP @ V((-0.22 * 1.7, 0.02, 0.12)); Q += trowel(tuple(b0 + V((0, 0.08, 0))), tuple(hd.nz(RP @ V((0.0, -1.0, 0.25)))), tuple(RP @ V((0, 0, 1.0))))
    return Q, P

KB = (-2.75, 0.0, -1.85)                            # knight on the west bank by the arch (seq 3)
KPAY = (-8.95, 0.0, -1.38)                          # at the bucket (seq 4)
SWORD_IN = (-9.35, 0.0, -1.0)                       # his sword stuck in the ground while he pays
KFAR = (4.7, 0.0, -2.6)                             # dawn, east bank
def knight_pose(t):
    sc = scene(t)
    P = dict(base=TRV, yaw=ang_to(TRV, TP), eyes='open', mouth='neutral', brow=0.4, lean=0.04, cape_sway=0.12 * math.sin(t * 1.3))
    P['rh'] = (0.26, 0.95, 0.22); P['rgrip'] = 0.9; P['rpalm'] = (-1.0, 0, 0.0); P['lh'] = (-0.25, 0.96, 0.1); P['lgrip'] = 0.5
    sword = 'hand'
    if t < S2:
        th = win(t, T_THREAT[0], T0['03'] + 0.3, 0.3)
        P['rh'] = lerp3((0.26, 0.95, 0.22), (0.2, 1.35, 0.5), th); P['brow'] = 0.7 if th > 0.3 else 0.4
        say(P, t, ('02',))
        if t >= T0['03']: P['brow'] = lerp(0.7, -0.1, sm(seg01(t, T0['03'], tend('03'))))
        if t >= T_PASS[0]:
            u = seg01(t, T_PASS[0], T_PASS[1] + 0.6); x = lerp(TRV[0], -6.2, u); z = lerp(TRV[2], 0.0, sm(u))
            P['base'] = (x, max(0.0, deck_y(x) if x > -7.0 else 0.0), z); P['yaw'] = ang_to(TRV, (-6.2, 0, 0.0)) * (1 - u) + PI / 2 * u
            P['walk'] = u * 9.0; P['stride'] = 0.34; P['head'] = (-0.5 * (1 - sm(seg01(t, T_PASS[0], T_PASS[0] + 0.8))), 0.0, 0.0)
        return P, sword
    if sc in ('walk', 'crack', 'react'):                                                    # up the deck
        u = seg01(t, S2, T_CRACK - 0.05); x = lerp(-4.9, -0.35, u)
        P['base'] = (x, deck_y(x), 0.15); P['yaw'] = PI / 2; P['walk'] = (t - S2) * 5.5; P['stride'] = 0.32
        P['rh'] = (0.24, 0.92, 0.15)
        if t >= T_GROAN: P['head'] = (0.0, 0.25 * win(t, T_GROAN, T_GROAN + 0.9, 0.2), 0.0); P['brow'] = 0.0
        if t >= T_CRACK - 0.05:                                                             # stagger: knees bend, arms out
            P.pop('walk', None); s_ = sm(seg01(t, T_CRACK - 0.05, T_CRACK + 0.25)); P['base'] = (-0.35, deck_y(-0.35), 0.15)
            P['crouch'] = 0.22 * s_; P['lean'] = 0.15 * s_; P['rh'] = lerp3((0.24, 0.92, 0.15), (0.48, 1.05, 0.25), s_); P['lh'] = lerp3((-0.25, 0.96, 0.1), (-0.5, 1.05, 0.25), s_)
            P['eyes'] = 'wide'; P['brow'] = -0.6; P['mouth'] = 'o'; P['head'] = (0.0, 0.35 * s_, 0.0)
        return P, sword
    if sc in ('hold', 'kn3', 'tr3'):                                                        # on the bank, sword in hand, then lowered
        P['base'] = KB; P['yaw'] = ang_to(KB, TB); P['brow'] = -0.3; P['eyes'] = 'wide' if t < T0['07'] else 'open'
        P['rh'] = (0.27, 1.0, 0.3); P['head'] = (0.0, -0.1, 0.0)
        say(P, t, ('07',))
        if t >= tend('07'): P['brow'] = -0.5
        lo = sm(seg01(t, *T_LOWER))
        if lo > 0: P['head'] = (0.15 * lo, 0.45 * lo, 0.0); P['rh'] = lerp3((0.27, 1.0, 0.3), (0.24, 0.78, 0.12), lo); P['eyes'] = 'sad' if lo > 0.6 else 'open'; P['brow'] = -0.7
        return P, sword
    if sc in ('pay', 'bucket'):                                                             # at the bucket, the sword stuck in the ground
        P['base'] = KPAY; P['yaw'] = ang_to(KPAY, BUCKET); P['brow'] = -0.3; P['head'] = (0.0, 0.35, 0.0); P['lean'] = 0.12
        u = sm(seg01(t, T_POUR[0] - 0.4, T_POUR[0]))
        P['lh_w'] = tuple(lerp3(wpt(KPAY, P['yaw'], (-0.2, 1.05, 0.3)), purse_hold(), u)); P['lgrip'] = 0.85; P['lpalm'] = (0, 0, 1.0)
        P['rh'] = (0.25, 0.92, 0.12); P['rgrip'] = 0.3
        if t >= T_POUR[1] + 0.3: P['mouth'] = 'soft'; P['brow'] = 0.0
        return P, 'ground'
    # dawn: the far bank, looks back, lifts his hand
    P['base'] = KFAR; P['yaw'] = PI * 0.55; P['rh'] = (0.25, 0.92, 0.12); P['eyes'] = 'open'; P['brow'] = 0.0
    if t >= T_KWAVE[0] - 0.4:
        u = sm(seg01(t, T_KWAVE[0] - 0.4, T_KWAVE[0] + 0.3)); P['yaw'] = lerp(PI * 0.55, ang_to(KFAR, TD), u)
        w = sm(seg01(t, T_KWAVE[0] + 0.3, T_KWAVE[0] + 0.7)); P['lh'] = lerp3((-0.25, 0.96, 0.1), (-0.32, 1.72, 0.18), w); P['lgrip'] = 0.0; P['lpalm'] = (0, 0, 1.0)
        P['mouth'] = 'smile' if w > 0.5 else 'neutral'
    if t >= T0['12'] - 0.2:
        u = max(0.0, t - (T0['12'] + 0.4)); P['lh'] = (-0.25, 0.96, 0.1); P['yaw'] = PI * 0.5; P['base'] = (KFAR[0] + 0.9 * u, 0.0, KFAR[2] - 0.1 * u); P['walk'] = u * 5.5 if u > 0 else None
        if P['walk'] is None: P.pop('walk')
    return P, sword
def purse_hold(): return V(BUCKET) + V((-0.03, BK_H + 0.5, 0.05))
def purse_R(t):
    u = sm(seg01(t, T_POUR[0] - 0.15, T_POUR[0] + 0.35)); return hd.Rx(PI * 0.95 * u)
def knight_layer(t):
    P, sw = knight_pose(t); Q = knight(P)
    if sw == 'hand':
        g = fp.grip_pt(P, 'r', 0.06, 0.0); RW = P['_RW']
        d = hd.nz(RW @ V((0.05, 0.45, 1.0))) if (t < S2 and win(t, T_THREAT[0], T0['03'] + 0.3, 0.3) > 0.4) else hd.nz(RW @ V((0.06, -0.72, 0.6)))
        if scene(t) in ('hold', 'kn3', 'tr3') and t >= T_LOWER[0]: d = hd.nz(lerp3(RW @ V((0.06, -0.72, 0.6)), V((0.0, -1.0, 0.15)), sm(seg01(t, *T_LOWER))))
        Q += hd.sword(tuple(g), tuple(d), P['_rpalm'], length=0.85)
    elif sw == 'ground':
        Q += hd.sword((SWORD_IN[0], 0.62, SWORD_IN[2]), (0.08, -1.0, 0.05), (1.0, 0, 0), length=0.85)
    if scene(t) in ('pay', 'bucket') and t < T_POUR[1] + 1.2:
        g = fp.grip_pt(P, 'l', 0.05, 0.0); R = purse_R(t); s_ = 0.34
        Q += dtx.sack(tuple(V(g) - R @ V((0, 0.36 * s_, 0))), R, s=s_, seal=False, slump=0.6 * seg01(t, T_POUR[0], T_POUR[1]))
    return Q, P
WOM0 = (-11.2, 0.0, 0.55)
def woman_layer(t):
    """the next traveller (only in 'eve'): walks up the road to the troll"""
    u = seg01(t, T_EVE - 0.2, T_LOOPF + 0.1); P = dict(base=lerp3(WOM0, TRV, u), yaw=ang_to(WOM0, TRV), eyes='open', mouth='neutral', brow=-0.1, lean=0.08, cape_sway=0.1)
    P['walk'] = u * 8.0; P['stride'] = 0.24
    return hd.human(WOMAN, P)
def coins_fall(t):
    """the purse empties: each coin drops from the purse mouth into the bucket; returns (faces, landed count)"""
    if not (T_POUR[0] <= t): return [], 0
    Q = []; landed = 0; mouth = purse_hold() + V((0, -0.06, 0)); top = V(BUCKET) + V((0, BK_H + 0.02, 0)); h = mouth[1] - top[1]
    tf = math.sqrt(2 * h / 9.8)
    for i in range(N_COIN):
        t0 = T_POUR[0] + 0.25 + (T_POUR[1] - T_POUR[0] - 0.5) * (i / N_COIN) ** 0.8 + 0.03 * hsh(i, 81)
        u = t - t0
        if u < 0: continue
        if u >= tf: landed += 1; continue
        y = mouth[1] - 4.9 * u * u; dx = 0.05 * (hsh(i, 82) - 0.5) * u / tf; dz = 0.05 * (hsh(i, 83) - 0.5) * u / tf
        Q += dtx.coin((mouth[0] + dx, y, mouth[2] + dz), hd.Rx(u * 9 + i) @ hd.Rz(u * 7), s=1.1)
    return [q for q in Q if q], landed
def coin_land_times():
    mouth = purse_hold() + V((0, -0.06, 0)); h = mouth[1] - (BUCKET[1] + BK_H + 0.02); tf = math.sqrt(2 * h / 9.8)
    return [T_POUR[0] + 0.25 + (T_POUR[1] - T_POUR[0] - 0.5) * (i / N_COIN) ** 0.8 + 0.03 * hsh(i, 81) + tf for i in range(N_COIN)]
LANDS = coin_land_times()

# ======================= HUD: the bridge's HP =======================
HP0 = 7
def hp(t):
    if t < T_GROAN + 0.15: return HP0
    if t < T_CRACK + 0.05: return HP0 - 1
    return HP0 - 4 + sum(1 for x in LANDS if t >= x)
def hp_visible(t): return T_GROAN - 0.2 <= t < T_EVE and t >= 0
def hp_pops(): return [T_GROAN + 0.15, T_CRACK + 0.05] + LANDS
LBL = 'KÖPRÜ' if TRL else 'BRIDGE'
def hud(im, t):
    if not hp_visible(t): return
    d = ImageDraw.Draw(im); v = hp(t); x0, y0 = 60, 92
    pop = max([win(t, p, p + 0.3, 0.1) for p in hp_pops() if p <= t + 0.01] + [0.0])
    alpha_in = sm(seg01(t, T_GROAN - 0.2, T_GROAN + 0.05))
    if alpha_in < 0.1: return
    look.draw_cells(d, look.text_cells(LBL, x0, y0, 5, (236, 228, 206)), 3)
    vs = f'{v}/100'; colv = (255, 92, 70) if v < 7 else ((255, 214, 60) if v < 20 else (150, 236, 120))
    sc = 5 + (1 if pop > 0.4 else 0)
    look.draw_cells(d, look.text_cells(vs, x0 + 6 * 5 * len(LBL) + 30, y0 - (sc - 5) * 3, sc, colv), 3)
    bx0, by0, bw, bh = x0, y0 + 52, 460, 30
    d.rectangle([bx0 - 6, by0 - 6, bx0 + bw + 6, by0 + bh + 6], fill=(10, 8, 12)); d.rectangle([bx0 - 2, by0 - 2, bx0 + bw + 2, by0 + bh + 2], outline=(160, 140, 110), width=3)
    fw = int(bw * v / 100.0)
    if fw > 0: d.rectangle([bx0, by0, bx0 + fw, by0 + bh], fill=colv); d.rectangle([bx0, by0, bx0 + fw, by0 + 7], fill=tuple(min(255, c + 50) for c in colv))
    if pop > 0: d.rectangle([bx0 + fw - 8, by0 - 4, bx0 + fw + 8, by0 + bh + 4], fill=(255, 255, 255))

# =====================================================================================================================
#                                                      CAMERA
# =====================================================================================================================
OPEN_POS = V((-8.62, 1.78, -0.78)); OPEN_TGT = V((-8.0, 1.98, -1.42))
def cam_shot(t):
    sc = scene(t)
    if sc in ('open', 'loop'):
        u = sm(seg01(t, -1.0, T0['01'] + 1.0)); return lerp3(OPEN_POS + V((-0.17, -0.02, 0.22)), OPEN_POS, u), OPEN_TGT, 40.0
    def span(i):
        a = CUTS[i][1]; b = CUTS[i + 1][1] if i + 1 < len(CUTS) else DUR; return sm(seg01(t, a, b))
    idx = [n for n, _ in CUTS].index(sc); u = span(idx)
    if sc == 'knight':                                                       # over the troll's shoulder at the knight
        return lerp3((-8.0, 2.05, -1.45), (-8.08, 2.0, -1.35), u), lerp3((-8.95, 1.45, -0.3), (-8.95, 1.5, -0.3), u), 42.0
    if sc == 'aside':
        return lerp3((-10.7, 1.75, 1.6), (-10.4, 1.7, 1.3), u), lerp3((-7.9, 1.45, -0.9), (-7.3, 1.35, -0.6), u), 50.0
    if sc == 'walk':
        kp = V(knight_pose(t)[0]['base']); tg = kp + V((0.3, 0.95, 0.0)); return tg + V((-0.9, 0.35, -3.9)), tg, 44.0
    if sc == 'crack':
        return lerp3((0.55, 1.45, -2.7), (0.45, 1.5, -2.45), u), (0.1, 1.72, -1.1), 46.0
    if sc == 'react':
        return lerp3((-9.3, 2.0, -3.6), (-9.2, 1.95, -3.5), u), (-7.6, 1.6, -1.8), 50.0
    if sc == 'hold':
        return lerp3((0.8, 0.72, -2.15), (0.68, 0.78, -1.9), u), lerp3((0.3, 1.02, -0.2), (0.3, 1.06, -0.2), u), 46.0
    if sc == 'kn3':
        return lerp3((-1.75, 1.35, -3.15), (-1.85, 1.38, -3.05), u), (-2.75, 1.55, -1.85), 44.0
    if sc == 'tr3':
        return lerp3((0.75, 0.75, -1.85), (0.7, 0.78, -1.7), u), (0.3, 1.0, -0.2), 46.0
    if sc == 'pay':
        return lerp3((-7.55, 1.6, -3.55), (-7.7, 1.52, -3.3), u), lerp3((-8.75, 0.95, -1.6), (-8.7, 0.88, -1.7), u), 46.0
    if sc == 'bucket':
        b = V(BUCKET); return lerp3(b + V((0.6, 0.95, -0.55)), b + V((0.48, 0.85, -0.44)), u), b + V((-0.1, 0.42, 0.1)), 44.0
    if sc == 'dawn':
        return lerp3((-1.35, 1.6, -2.3), (-1.2, 1.62, -2.15), u), lerp3((0.25, 1.5, -1.45), (0.3, 1.55, -1.45), u), 48.0
    if sc == 'wl':
        return lerp3((-0.75, 1.62, -2.35), (-0.65, 1.62, -2.25), u), (0.4, 1.52, -1.45), 44.0
    if sc == 'far':
        return lerp3((2.6, 1.5, -5.4), (2.7, 1.5, -5.2), u), (4.6, 1.3, -2.6), 40.0
    if sc == 'wide':
        return lerp3((-5.6, 2.5, -8.6), (-5.1, 2.4, -8.0), u), lerp3((1.0, 1.0, -0.6), (0.9, 1.0, -0.6), u), 46.0
    # eve: over the old woman's shoulder as she walks up
    return lerp3((-11.9, 1.85, 1.3), (-10.2, 1.75, 0.45), u), (-7.9, 1.6, -1.7), 46.0

# =====================================================================================================================
#                                                      RENDER
# =====================================================================================================================
def frame_low(t):
    pos, tgt, fov = cam_shot(t); cam = Camera.look(tuple(pos), tuple(tgt)); sc = scene(t)
    night = sc in NIGHT
    layers = [set_faces()]
    lp_on = 1.0 if night else 0.15
    tq, tl = toll_post(lp_on, t); layers.append(tq)
    lq, lpos = fp.lantern_faces(lp_on); layers.append(lq)
    fill = 0.0
    if t >= T_POUR[0]: fill = min(1.0, sum(1 for x in LANDS if t >= x) / N_COIN)
    layers.append(bucket(fill if t < S5 or t < 0 else 1.0))
    if not (sc in ('dawn', 'wl', 'far', 'wide') and t >= 0): layers.append(trowel_rest())
    # crack + stone + dust
    cu = 0.0 if t < 0 else sm(seg01(t, T_CRACK - 0.08, T_CRACK + 0.3))
    patch = sm(seg01(t, S5, tend('11') - 0.1)) if t >= S5 else 0.0
    if sc in ('dawn', 'wl', 'far', 'wide'): cu = 1.0
    if sc in ('eve', 'loop'): cu, patch = 0.0, 0.0
    if cu > 0: layers.append(crack_faces(cu, patch))
    if 0 <= t < S3: layers.append(falling_stone(t, T_FALL)); layers.append(splash(t, T_FALL + 0.6))
    if night and t >= 0:
        layers.append(dust(t, T_GROAN, T_GROAN + 0.6, 0.5, 1))
        layers.append(dust(t, T_CRACK, T_CRACK + 1.4, 1.4, 2))
        if S3 <= t < S5: layers.append(dust(t, S3, S5, 0.45, 3, x0=0.2, z0=-0.2, y0=1.5, spread=0.9))
    # people
    show_t = not (sc in ('walk', 'crack') and False)
    TQ, TPz = troll_layer(t); layers.append(TQ)
    if sc not in ('open', 'loop', 'eve'):
        KQ, KP = knight_layer(t); layers.append(KQ)
    if 0 <= t and sc in ('pay', 'bucket'):
        cq, _ = coins_fall(t); layers.append(cq)
    if sc == 'eve': layers.append(woman_layer(t))
    # sky + light
    if night:
        layers.append(sky('night')); fog = (16, 22, 36); amb = 0.32
        L = [((8, 10, -7), (130, 150, 215), 1.6), (tl, (255, 186, 110), 1.6), (lpos, (255, 190, 110), 1.1)]
        if sc in ('hold', 'kn3', 'tr3'): L.append(((0.3, 0.6, -1.6), (120, 140, 200), 0.9))
        fs, fe = 9, 42
    else:
        layers.append(sky('dawn')); fog = (196, 152, 124); amb = 0.44
        L = [((24, 3, -4), (255, 196, 140), 2.3), ((-8, 10, -6), (190, 190, 215), 0.9)]
        fs, fe = 14, 70
    R = Renderer(W, H, fog=fog)
    img, vi, zb = zrender(R, cam, layers, L, fov=fov, fog_start=fs, fog_end=fe, ambient=amb, return_z=True)
    a = look.outline(np.asarray(img).astype(np.float32), zb)
    a = a * (np.array([0.93, 0.98, 1.08]) if night else np.array([1.06, 1.0, 0.92]))
    a = np.clip((a - 112) * 1.12 + 110, 0, 255)
    return post.ps1(Image.fromarray(a.astype(np.uint8)), levels=6), vi

# ======================= overlays =======================
def text_w(s, sc): return len(s) * 6 * sc - sc
COVER = ('TROL NEDEN', 'PARA İSTER?') if TRL else ('WHY DO TROLLS', 'WANT TOLLS?')
COVER_Y = int(os.environ.get('COVER_Y', '1330'))
T_PUNCH = T0['00'] + 0.66 * SCR['dur']['00']
def cover_overlay(im, t):
    b = T0['02'] - 0.25
    if not (0 <= t < b): return
    d = ImageDraw.Draw(im); pop = sm(seg01(t, 0, 0.12)); sc0 = 12 if pop >= 1 else 14
    punch = win(t, T_PUNCH, T_PUNCH + 0.35, 0.08)                      # 'want TOLLS?' lands: line 2 jumps bigger for a beat
    s1, s2 = COVER; y1 = COVER_Y; y2 = COVER_Y + 8 * sc0 + 30; sc2 = sc0 + 1 + (2 if punch > 0.5 else 0); w2 = text_w(s2, sc2)
    y2 -= 7 if punch > 0.5 else 0
    d.rectangle([540 - w2 / 2 - 34, y2 - 22, 540 + w2 / 2 + 34, y2 + 7 * sc2 + 22], fill=(40, 96, 40))
    for s_, y, sc, col, sh in ((s1, y1, sc0, (255, 255, 255), (30, 70, 30)), (s2, y2, sc2, (255, 222, 40), (20, 40, 10))):
        x = int(540 - text_w(s_, sc) / 2)
        look.draw_cells(d, look.text_cells(s_, x + 10, y + 10, sc, sh), 0)
        look.draw_cells(d, look.text_cells(s_, x, y, sc, col), 7)
COL = {'N': (242, 238, 226), 'T': (170, 226, 120), 'K': (130, 190, 255)}
def _sub_scr():
    if not TRL: return SCR
    import importlib.util as _iu
    sp_ = _iu.spec_from_file_location('bt_tts', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'tts', 'bt.py'))
    m_ = _iu.module_from_spec(sp_); sp_.loader.exec_module(m_); TRS = m_.TR_SUB
    out = dict(SCR); sent = {}
    for k, v in SCR['sent'].items():
        if len(v) == len(TRS[k]): sent[k] = [[a, b, tx] for (a, b, _), tx in zip(v, TRS[k])]
        else: sent[k] = [[v[0][0], v[-1][1], ' '.join(TRS[k])]]
    out['sent'] = sent
    return out
SUBS = look.Subtitles(_sub_scr(), [x for x in LINES if x[0] != '00'], W, H, S, COL, title_key='none', n=17,
                      hil=({'SİKKE.', 'KÖPRÜ', 'ÖDEDİ.', 'ÇATLADI.', 'KIRK', 'KILIÇ', 'TAŞ.', 'İSTER.'} if TRL else {'COIN.', 'BRIDGE', 'CRACKED.', 'FORTY', 'SWORD.', 'STONE.', 'GOLD.', 'BRIDGES'}))
from nightkit import cta
CTA = cta.Achievement(t0=S4 + 0.643, lang=SUB_LANG, dur=F(0.5))     # pinned inside seq 4 (same place as the first render), ~65 %
def frame_final(t):
    if t >= T_LOOPF: t = t - DUR                                                         # loop tail = the frames just before frame 0
    img, vi = frame_low(t); arr = post.upscale(img, S)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); cover_overlay(im, t); hud(im, t)
    arr = np.asarray(im).astype(np.float32)
    arr = SUBS.apply(arr, t) if t >= 0 else arr
    arr = CTA.apply(arr, t) if t >= 0 else arr
    fl = win(t, T_CRACK - 0.02, T_CRACK + 0.12, 0.05) if t >= 0 else 0.0                 # a white hit on the crack
    if fl > 0: arr = arr * (1 - 0.35 * fl) + 255 * 0.35 * fl
    return arr

TEST = os.environ.get('TEST')
if TEST and __name__ == '__main__':
    if TEST == 'seq': ts = sorted(set([round(a + (b - a) * f, 2) for i, (n_, a) in enumerate(CUTS) for b in [CUTS[i + 1][1] if i + 1 < len(CUTS) else DUR] for f in (0.1, 0.5, 0.9)]))
    elif TEST == 'all': ts = [round(x, 2) for x in np.arange(0, DUR, float(os.environ.get('STEP', '1.0')))]
    else: ts = [float(x) for x in TEST.split(',')]
    tw_ = int(os.environ.get('TW', '270')); th = tw_ * 16 // 9
    ims = [Image.fromarray(np.clip(frame_final(x), 0, 255).astype(np.uint8)) for x in ts]
    if os.environ.get('SZ') == 'full':
        for x, im in zip(ts, ims): im.save(f'test_bt_{x:.2f}.png')
    ims = [im.resize((tw_, th), Image.LANCZOS) for im in ims]
    per = int(os.environ.get('PER', '8')); rows = (len(ims) + per - 1) // per; shp = Image.new('RGB', (min(per, len(ims)) * (tw_ + 2), rows * (th + 18)), (30, 30, 30))
    dd = ImageDraw.Draw(shp)
    for i, (im, x) in enumerate(zip(ims, ts)): shp.paste(im, ((i % per) * (tw_ + 2), (i // per) * (th + 18))); dd.text(((i % per) * (tw_ + 2) + 4, (i // per) * (th + 18) + th + 3), f'{x:.2f} {x / 1.2:.1f}f {scene(x)}', fill=(255, 255, 0))
    shp.save(os.environ.get('TEST_OUT', 'test_bt.png')); print('test written', DUR, round(DUR / 1.2, 2), SEQS); sys.exit()

QA = dict(fps=FPS, dur=DUR, W=W, frame=lambda t: Image.fromarray(np.clip(frame_final(t), 0, 255).astype(np.uint8)).resize((W, H), Image.BOX), chars={},
          geom=lambda t, name, st, V_: [], camera=lambda t: cam_shot(t)[0], min_cam_dist=0.3, camera_ok=lambda p: True, allow_jump=[], weapon_events=[],
          scenes=[dict(id=nm, t0=a, t1=(CUTS[i + 1][1] if i + 1 < len(CUTS) else DUR), action=nm) for i, (nm, a) in enumerate(CUTS)],
          texts=lambda: [('hud', COVER[0], 12), ('hud', COVER[1], 13), ('hud', LBL, 5)])

# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as _sf
    s = Sound(DUR, loop=False, seed=93); sr = s.sr; n = s.n; t = s.t
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
    def step(t0, v=0.03, seed=0, metal=False):
        tt = s.T(0.12); put(FX, s.filt_short(s.noise(0.12, seed), lo=150, hi=1800) * np.exp(-tt * 30) + np.sin(2 * np.pi * 75 * tt) * np.exp(-tt * 26) * 0.3, t0, v)
        if metal: tone(t0 + 0.01, 96 + (seed % 3), 0.15, v * 0.25, dec=25, harm=(1.0, 0.5))
    def mask(a, b, r=0.15): return np.clip(np.minimum((t - a) / r, (b - t) / r), 0, 1)
    night = np.ones(n); dawn_m = mask(S5, T_EVE, 0.08); night = night - dawn_m
    # stream (everywhere, louder under the arch), crickets at night, birds at dawn, a little wind
    water = s.filt(s.rng.normal(0, 1, n), lo=300, hi=2600) * (0.012 + 0.004 * np.sin(2 * np.pi * 0.31 * t))
    under = mask(S3, S5, 0.05); BED += water * (1 + 1.2 * under)
    BED += s.filt(s.rng.normal(0, 1, n), lo=60, hi=300) * 0.01
    for k in range(int(DUR / 0.5)):
        tb = 0.15 + k * 0.5 + 0.2 * hsh(k, 3)
        if night[min(n - 1, int(tb * sr))] > 0.5:
            for j in range(3): tt = s.T(0.03); put(BED, np.sin(2 * np.pi * 4200 * tt) * np.sin(np.pi * tt / 0.03), tb + j * 0.06, 0.004)
    for k in range(10):
        tb = S5 + 0.3 + k * (T_EVE - S5 - 0.5) / 10 + 0.2 * hsh(k, 5)
        for j in range(2): tone(tb + 0.09 * j, 88 + int(5 * hsh(k, 6)), 0.08, 0.008, dec=10, glide=0.25)
    # frame 0: a low grunt-hum under 'One coin' is the voice itself; the lantern creak
    # knight: steps (S1 pass, S2 deck), the sword raise
    nb(T_THREAT[0] + 0.05, 0.3, 2500, 8000, 0.03, 13, 1); tone(T_THREAT[0] + 0.2, 98, 0.8, 0.014, dec=3.0, harm=(1.0, 0.5, 0.3))
    x = T_PASS[0]; k = 0
    while x < T_CRACK - 0.1:
        if not (S2 - 0.05 < x < S2 + 0.05): step(x, 0.026, 60 + k, metal=True)
        x += 0.5; k += 1
    # the groan: low wood/stone creak with grit
    tt = s.T(1.1); put(FX, np.sin(2 * np.pi * (55 + 12 * np.sin(tt * 9)) * tt) * np.sin(np.pi * tt / 1.1) * (1 + 0.5 * s.filt_short(s.noise(1.1, 31), lo=40, hi=300) * 6), T_GROAN, 0.05)
    nb(T_GROAN + 0.1, 0.8, 1500, 6000, 0.015, 32, 2)
    tone(T_GROAN + 0.15, 52, 0.5, 0.03, dec=4, harm=(1.0, 0.5)); tone(T_GROAN + 0.35, 51, 0.5, 0.03, dec=4, harm=(1.0, 0.5))   # HP -1 'damage' blip
    # the crack: sharp crack + boom, grit, the stone hits the water
    nb(T_CRACK, 0.18, 1200, 9000, 0.12, 41, 0.5); thud(T_CRACK + 0.02, 48, 0.25, 0.6); nb(T_CRACK + 0.1, 1.3, 900, 6000, 0.03, 42, 2)
    for k, m in enumerate((50, 47, 43)): tone(T_CRACK + 0.1 + 0.16 * k, m, 0.6, 0.035, dec=3.5, harm=(1.0, 0.6, 0.3))
    nb(T_FALL + 0.6, 0.5, 400, 5000, 0.08, 43, 0.6); thud(T_FALL + 0.6, 90, 0.06, 0.3)
    # troll runs (heavy steps)
    x = T_RUN; k = 0
    while x < S3 - 0.05: thud(x, 45, 0.07, 0.25); x += 0.22; k += 1
    # under the arch: strain creaks
    for k in range(int((S5 - S3) / 1.3)): s.creak(S3 + 0.4 + k * 1.3 + 0.3 * hsh(k, 9), v=0.012, f0=420)
    nb(T_LOWER[0] + 0.2, 0.25, 2500, 8000, 0.012, 51, 1)
    # coins
    for i, x in enumerate(LANDS):
        tone(x, 100 + int(6 * hsh(i, 91)), 0.18, 0.018, dec=22, harm=(1.0, 0.6, 0.35, 0.2)); tone(x + 0.03, 107 + int(4 * hsh(i, 92)), 0.12, 0.01, dec=30)
    for k in range(6): tone(T_POUR[0] + 0.2 + k * 0.05, 86 + [0, 4, 7, 12, 16, 19][k], 0.3, 0.006, dec=6)
    # trowel scrapes at dawn, the pat on the stone
    x = S5 + 0.2
    while x < T_PAT[0] - 0.3: nb(x, 0.2, 1500, 6000, 0.012, int(x * 40), 1.5); x += 2 * PI / 5.0 / 2
    thud(T_PAT[1] - 0.05, 120, 0.03, 0.15)
    # music: slow 8-bit troll lullaby (D minor, square + soft bass); out for the crack and for the wordless beat; warm chord on the last line
    beat = 0.6; mel = [62, 65, 69, 65, 64, 67, 70, 67, 62, 65, 69, 74, 72, 69, 67, 64]; bass = [38, 38, 41, 41, 43, 43, 45, 45]
    def sq(m, d, v, dec=2.5):
        f = 440 * 2 ** ((m - 69) / 12); tt = s.T(d); x = np.sign(np.sin(2 * np.pi * f * tt)) * 0.55 + np.sin(2 * np.pi * f * tt) * 0.45
        return x * np.minimum(1, tt / 0.01) * np.exp(-tt * dec) * np.minimum(1, (d - tt) / 0.03) * v
    for b in range(int(DUR / beat) + 1):
        t0 = b * beat; put(MUS, sq(mel[b % 16], beat * 0.9, 0.011, 3.0), t0)
        if b % 2 == 0: put(MUS, sq(bass[(b // 2) % 8], beat * 1.9, 0.015, 1.2), t0)
    g = (1 - mask(T_GROAN - 0.1, S3 + 0.8, 0.2)) * (1 - mask(T_PAT[0] - 0.2, T0['12'] - 0.1, 0.2)) * (1 - 0.5 * under)
    MUS = MUS * g
    for k, m in enumerate((62, 66, 69, 74)): tone(T0['12'] + 0.05 + 0.08 * k, m, 2.4, 0.018, dec=1.0, harm=(1.0, 0.4, 0.2), buf=MUS)
    # hook: a low hit + an 8-bit stab under the title, a punch on 'TOLLS?'
    thud(0.02, 52, 0.22, 0.5); nb(0.02, 0.25, 200, 3000, 0.05, 71, 0.5)
    for k, m in enumerate((50, 57, 62)): tone(0.03 + 0.02 * k, m, 0.9, 0.03, dec=2.5, harm=(1.0, 0.5, 0.3, 0.2))
    thud(T_PUNCH, 70, 0.12, 0.3); tone(T_PUNCH + 0.01, 74, 0.5, 0.022, dec=5, harm=(1.0, 0.6, 0.3))
    if CTA.on: put(FX, cta.chime(sr), CTA.t0, 1.0)
    # voice
    NB = np.zeros(n); wins = []
    for k_, t0 in LINES:
        f_ = os.path.join(TTS_DIR, 'bt', f'{k_}.wav')
        if not os.path.exists(f_): continue
        a, ar = _sf.read(f_); a = a if a.ndim == 1 else a.mean(1)
        a = np.interp(np.arange(int(len(a) * sr / ar)) / sr, np.arange(len(a)) / ar, a); act = np.abs(a) > 0.02 * np.abs(a).max()
        a = a * (0.12 / np.sqrt((a[act] ** 2).mean())); put(NB, a, t0); wins.append((t0, t0 + len(a) / sr))
    gd = duck_envelope(n, sr, wins, -7.0, 0.05, 0.25) if wins else np.ones(n)
    bed = BED * gd + MUS * (0.6 + 0.4 * gd); fx = FX * (0.6 + 0.4 * gd)
    L = bed + fx; R_ = np.roll(bed, 700) + np.roll(fx, 200)
    pk = max(np.abs(L).max(), np.abs(R_).max()); gv = (pk * 1.6 / np.abs(NB).max()) if np.abs(NB).max() > 0 else 0.0
    s.L = L + NB * gv; s.R = R_ + NB * gv; s.reverb(0.12, length=1.4, decay=3.0)
    fi = np.clip(t / 0.008, 0, 1); s.L = s.L * fi; s.R = s.R * fi
    return s.save(path, peak=0.9)
if __name__ == '__main__' and os.environ.get('PART') == 'audio':
    print(build_audio(os.path.join(OUT, os.environ.get('AUDIO_NAME', 'bridge_troll.wav')))); sys.exit()
if __name__ == '__main__' and os.environ.get('PART'):
    a, b = map(int, os.environ['PART'].split(':'))
    import subprocess
    p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W * S}x{H * S}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', os.path.join(OUT, f"{os.environ.get('PART_PREFIX', 'bt')}_{a:05d}.mp4")], stdin=subprocess.PIPE)
    vhs = post.VHS(W * S, H * S, S, grade='none', chroma=0, scan_dark=1.0, vignette=0.22, grain=0.9, band_period=1e9)
    for f in range(a, min(b, N)): p.stdin.write(vhs(frame_final(f / FPS), f, f / FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done', a, b); sys.exit()
