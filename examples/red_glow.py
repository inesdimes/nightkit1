"""WHY DO BOSSES GLOW RED BEFORE THEY ATTACK? (Insert Disc 2, 28 Nov 2026) ~34 s final (x1.2 after), nightkit HD, 9:16. TENSION.
Brief: briefs/red_glow.md (Enes's seed + Claude, approved 28 Nov with 3 touches). The red glow is not the boss: the hero's old master,
trapped in the Hollow King's chest crystal, lights it to warn every hero. The hero's stare on "Master?" gives him away; the boss follows
the stare to his own chest, rips the crystal out and crushes it (a spark escapes into the neck seam); no glow = no warning, the boss fakes
an attack; the real strike: the helmet's eye slits glow red ("Still here, boy. Left!"); the hero's shield sweeps over the lens = frame 0.
Voices: tools/tts/rg.py (N/K/M/H cloned Enes). Reuses: dragon_taxes knight + helmet, final_boss arena + wall torches.
New: the Hollow King (2.7 m hollow armour, closed horned helmet with eye slits, chest crystal cavity), the tiny master + ember,
the round shield with the white sun (shield in the RIGHT hand: the camera side), the greatsword, shards, sparks, crystal glow.
Assets:  ASSET=cast|boss|master|shield python examples/red_glow.py -> test_rg_<asset>.png
Stills:  TEST=seq | TEST=1.0,2.0 (build s) | TESTF=... (final s) python examples/red_glow.py -> test_rg.png
Render:  python tools/render_seq.py examples/red_glow.py --prefix rg --seqs s1,s2,s3,s4,s5 / --master <out>"""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from nightkit.engine import Renderer, Camera, refresh
from nightkit.zraster import zrender
from nightkit import post, look, hd, motion, font
import dragon_taxes as dtx
import final_boss as FB

W, H, S = 270, 480, 4
PI = math.pi; V = np.array; FPS = 24
sm = motion.smooth
hsh, lerp, lerp3, mixc = dtx.hsh, dtx.lerp, dtx.lerp3, dtx.mixc
def seg01(t, a, b): return max(0.0, min(1.0, (t - a) / (b - a))) if b > a else (1.0 if t >= b else 0.0)
def win(t, a, b, r=0.25): return sm(seg01(t, a, a + r)) * (1 - sm(seg01(t, b - r, b)))
def nz(v): v = V(v, float); n = np.linalg.norm(v); return v / n if n > 1e-9 else v
def F(x): return round(x * 1.2, 4)
def grip_pt(P, key, off=0.075, lift=0.03): return P['_' + key + 'wrist'] + P['_' + key + 'dir'] * off + P['_' + key + 'palm'] * lift
def angd(a, b, u): return a + ((b - a + PI) % (2 * PI) - PI) * u
SUB_LANG = os.environ.get('SUB_LANG', 'en'); TRL = SUB_LANG == 'tr'

# ======================= voice timing =======================
from nightkit.audio import Sound, duck_envelope
OUT = 'out'; os.makedirs(OUT, exist_ok=True)
TTS_DIR = os.environ.get('TTS_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tts'))
def _load_scr():
    f = os.path.join(TTS_DIR, 'rg', 'script.json')
    if os.path.exists(f): return json.load(open(f, encoding='utf-8'))
    import importlib.util as _iu                                         # no voice yet: planned lengths (asset work / stills)
    sp_ = _iu.spec_from_file_location('rg_tts', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'tts', 'rg.py'))
    m_ = _iu.module_from_spec(sp_); sp_.loader.exec_module(m_)
    dur = {}; sent = {}
    for k, s_, ss in m_.D:
        x = 0.0; sent[k] = []
        for (tx, *_), pl in zip(ss, m_.PLAN[k]): sent[k].append([round(x, 3), round(x + pl, 3), tx.upper()]); x += pl + 0.25
        dur[k] = round(x - 0.25, 2)
    return dict(dur=dur, sent=sent)
SCR = _load_scr()
KEYS = ['%02d' % i for i in range(0, 11)]

# ======================= timeline (BUILD seconds; final = build / 1.2) =======================
T0 = {}
def tend(k): return T0[k] + SCR['dur'][k]
T0['00'] = 0.12                                    # N: "Why do bosses glow red before they attack?"  (frame 1: he sees the crystal, dives)
T_LOOK = (0.36, 0.7)                               # touch 1: (the shield clears the lens) his eyes go UP to the glowing crystal ...
T_DIVE = (0.82, 1.5)                               # ... then he dives (camera-left)
T_LIFT = (1.05, 1.85)                              # only now the boss lifts the sword
T_SLAM = 2.3                                       # the blade hits the spot he just left (final 1.92 s)
S_SIDE = max(T_SLAM + 0.3, tend('00') + 0.05)
T0['01'] = S_SIDE + 0.15                           # N: "Every hero dodges the glow. Nobody asks who lights it."
T_RISE = (S_SIDE, S_SIDE + 0.7)                    # he comes up, shield raised: the white sun faces the lens
S_CRYS = tend('01') + 0.2                          # push into the crystal: the master
T0['02'] = S_CRYS + 0.75                           # M: "Left! Now!"
S_SWEEP = tend('02') + 0.1
T_DIVE2 = (S_SWEEP + 0.05, S_SWEEP + 0.65)         # the sword is still down; he dives left anyway ...
T_SWEEP = (S_SWEEP + 0.45, S_SWEEP + 1.05)         # ... THEN the sweep comes and misses
T_STARE = S_SWEEP + 1.1                            # touch 2: his stare locks on the crystal (and stays)
T0['03'] = T_STARE + 0.35                          # K: "Master? You fell here..."
S_MASTER = tend('03') + 0.15
T0['04'] = S_MASTER + 0.2                          # M: "Forty heroes since. I warned every one."
S_LOOKD = tend('04') + 0.2                         # WORDLESS BEAT: the boss follows the stare down to his own chest
T_FOLLOW = (S_LOOKD + 0.1, S_LOOKD + 0.7)          # helmet turns to the hero ...
T_TILT = (S_LOOKD + 0.8, S_LOOKD + 1.6)            # ... then tilts down to the chest; the master looks up
S_RIP = S_LOOKD + 2.0
T0['05'] = S_RIP + 0.1                             # H: "Traitor."
T_GRIP = (tend('05') + 0.05, tend('05') + 0.45)    # the gauntlet closes around the crystal
T0['06'] = T_GRIP[1] - 0.15                        # M: "Run, b-"  (cut off by the rip)
T_RIP = (tend('06') - 0.02, tend('06') + 0.3)      # ripped out
T_CRUSH = T_RIP[1] + 0.35                          # crushed in the fist: shards, the red dies
T_SPARK = (T_CRUSH + 0.05, T_CRUSH + 0.8)          # one tiny spark slips between the fingers into the neck seam
S_DARK = T_CRUSH + 1.0
T0['07'] = S_DARK + 0.3                            # N: "No glow. No warning. One heart left."
S_FAKE = tend('07') + 0.15
T_WIND = (S_FAKE + 0.1, S_FAKE + 0.6)              # HEAD FAKE: a huge windup ...
T_DIVE3 = (S_FAKE + 0.45, S_FAKE + 1.05)           # ... he dives ... nothing comes
T_LAUGH = S_FAKE + 1.15
T0['08'] = S_FAKE + 1.0                            # N: "He learned the hero's tells. Now he fakes his own."
S_HELM = tend('08') + 0.15
T_SLITS = S_HELM + 0.55                            # the eye slits light up red from inside
T0['09'] = T_SLITS + 0.35                          # M (muffled, in the helmet): "Still here, boy. Left!"
S_LOOP = tend('09') + 0.15                         # frame-1 framing; the shield comes up over the lens
T0['10'] = S_LOOP + 0.25                           # N: "Dodge again, or save him?"
DUR = round(max(tend('10') + 0.75, S_LOOP + 2.2), 3); N = int(round(DUR * FPS))
T_COVER = (DUR - 0.55, DUR)                        # the shield covers the lens (frame 0 uncovers it: one continuous wipe)
LINES = [(k, T0[k]) for k in KEYS]
def fr(x): return int(round(x * FPS))
CUTS = [('open', 0.0), ('side', S_SIDE), ('crys', S_CRYS), ('sweep', S_SWEEP), ('stare', T_STARE - 0.1), ('master', S_MASTER), ('lookd', S_LOOKD), ('rip', S_RIP),
        ('dark', S_DARK), ('fake', S_FAKE), ('helm', S_HELM), ('loop', S_LOOP)]
SEQS = [('s1', 0, fr(S_CRYS)), ('s2', fr(S_CRYS), fr(S_LOOKD)), ('s3', fr(S_LOOKD), fr(S_DARK)), ('s4', fr(S_DARK), fr(S_HELM)), ('s5', fr(S_HELM), N)]
def scene(t):
    nm = CUTS[0][0]
    for n_, a in CUTS:
        if t >= a: nm = n_
    return nm
def talking(t, key):
    if key not in T0: return 0.0
    for a, b, _ in SCR['sent'][key]:
        if T0[key] + a <= t < T0[key] + b: return 0.5 + 0.5 * math.sin((t - T0[key]) * 17.0)
    return 0.0
def glow_on(t):
    """the master's red light 0..1.2: chest (until the crush) -> nothing -> helmet (from T_SLITS); pulses with his puffs"""
    pulse = 0.82 + 0.18 * max(0.0, math.sin(t * 6.3)) ** 3
    if t < T_RIP[0]: return pulse * (1.0 - 0.35 * win(t, T_TILT[0], T_RIP[0], 0.2) * (0.5 + 0.5 * math.sin(t * 40)))   # flicker when seen
    if t < T_CRUSH: return lerp(0.9, 0.5, seg01(t, T_RIP[0], T_CRUSH))
    return 0.0
def helm_on(t):
    if t < T_SLITS: return 0.0
    return sm(seg01(t, T_SLITS, T_SLITS + 0.25)) * (0.85 + 0.15 * max(0.0, math.sin(t * 6.3)) ** 3)
def crystal_state(t):
    """'in' (in the chest), 'hand' (ripped, in the fist), 'gone' (crushed)"""
    if t < T_RIP[0]: return 'in'
    if t < T_CRUSH: return 'hand'
    return 'gone'

# ======================= cast =======================
KN = dtx.KNIGHT
SH_COL = (52, 70, 120); SH_RIM = (178, 186, 200); SUN = (228, 220, 192)
def shield(c, n, up, r=0.3):
    """round shield: c = centre of the front face, n = front normal, up = its up; steel rim, blue field, WHITE SUN (planted)"""
    c = V(c, float); n = nz(n); up = nz(V(up, float) - n * float(V(up, float) @ n)); sd = np.cross(up, n)
    R = np.column_stack([sd, n, -up])                                              # lathe axis = local y = the normal
    Q = hd.lathe(tuple(c - n * 0.05), R, [(r * 0.98, 0.0), (r, 0.02), (r * 0.9, 0.05)], 20, SH_COL)
    Q += hd.lathe(tuple(c - n * 0.004), R, [(r * 1.02, 0.0), (r * 0.96, 0.012)], 20, SH_RIM, cap0=False, cap1=False)
    Q += hd.lathe(tuple(c - n * 0.004), R, [(r * 0.94, 0.0), (r * 0.94, 0.003)], 20, SH_COL, cap0=False)
    Q += hd.lathe(tuple(c - n * 0.06), R, [(r * 0.95, 0.0), (r * 0.6, -0.02)], 16, hd.shade(SH_COL, 0.7))     # back side
    Q += sun_emblem(c + n * 0.004, n, up, r * 0.62)
    return [q for q in Q if q]
def sun_emblem(c, n, up, r, col=SUN):
    """the white sun: a disc + 8 rays (flat decals)"""
    n = nz(n); Q = hd.poly_decal(tuple(c), tuple(n), tuple(up), [(0.38 * r * math.cos(a), 0.38 * r * math.sin(a)) for a in np.linspace(0, 2 * PI, 14)[:-1]], col, lift=0.0)
    for i in range(8):
        a = 2 * PI * i / 8; w = 0.085 * r
        ca, sa = math.cos(a), math.sin(a)
        pts = [(0.48 * r * ca - w * sa, 0.48 * r * sa + w * ca), (r * ca, r * sa), (0.48 * r * ca + w * sa, 0.48 * r * sa - w * ca)]
        Q += hd.poly_decal(tuple(c), tuple(n), tuple(up), pts, col, lift=0.0)
    return Q
def knight(P):
    Q = dtx.knight(P)
    st = P.get('_shield')
    if st is not None: Q += shield(*st)
    return Q
def knight_shield(P, raise_=0.0):
    """shield strapped to the RIGHT forearm (camera side): front normal = out of the forearm's outer side, slightly forward"""
    wr = V(P['_rwrist']); el = V(P['_rel']); d = nz(wr - el); palm = V(P['_rpalm'])
    out_ = nz(-palm + 0.0 * d)                                                     # the back of the hand
    c = wr * 0.62 + el * 0.38 + out_ * 0.17                                       # in front of the fist (it poked through at 0.12)
    return c, out_, d

# ----------------------- the Hollow King -----------------------
BOSS_H = 2.7
BOSS = hd.spec(h=BOSS_H, build=1.45, skin=(30, 28, 34), hair=(30, 28, 34), hair_style='bald', eye=(20, 18, 22), brow=(30, 28, 34),
               lip=(30, 28, 34), tunic=(44, 44, 54), tunic2=(34, 34, 42), skirt=0.55, pants=(38, 38, 46), boots=(30, 30, 36),
               belt=(70, 24, 28), buckle=(150, 140, 120), gloves=(52, 52, 62), cloak=(52, 22, 30), cloak_len=1.1, collar=(60, 60, 72))
IRON = (58, 58, 70); IRON_D = (40, 40, 50); IRON_L = (96, 96, 112); TRIM = (150, 126, 84); RED = (230, 46, 40)
CR_R = 0.17; CR_Y = 0.02; CR_DEPTH = 0.1                                     # shallower than the torso surface (it showed inside the window)
def boss(P, crystal='in', glow=1.0, helm=0.0):
    """HD 2.7 m armour: hd.human (dark, its face hidden inside the closed helmet) + pauldrons, vambraces, greaves, a breastplate with
    a round CAVITY (the crystal window), a closed horned helmet with two eye slits. Returns faces; sets P['_crys'] (centre, R)"""
    Q = hd.human(BOSS, P); RW = P['_RW']; ch = P['_chest']; RH = P['_RH']; hc = P['_head']; k = BOSS_H / 1.78; bw = BOSS['build']
    for sd, key in ((1, 'r'), (-1, 'l')):                                          # pauldrons (layered, spiked)
        c = ch + RW @ V((sd * 0.2 * bw, 0.06 * k, -0.01))
        for i, (s_, col) in enumerate(((1.0, IRON), (0.82, IRON_D))):
            Q += hd.ellip(c + RW @ V((sd * 0.02 * i, -0.05 * i, 0)), RW @ hd.Rz(-sd * (0.35 + 0.2 * i)), (0.13 * bw * s_, 0.09 * s_, 0.13 * s_), 10, 5, col, v1=PI * 0.6,
                          colfn=lambda i_, j, cl, col=col: hd.shade(col, 0.8) if i_ == 2 else col)
        Q += hd.limb(c + RW @ V((sd * 0.05, 0.07, 0)), c + RW @ V((sd * 0.16, 0.26, -0.03)), 0.04, 0.004, IRON_L, n=6, m=1)
        el = P['_' + key + 'el']; wr = P['_' + key + 'wrist']                         # vambrace + elbow cop
        Q += hd.limb(el + (wr - el) * 0.12, wr - (wr - el) * 0.08, 0.075, 0.068, IRON, n=10, m=1, ref=RW @ V((0, 0, 1.0)))
        Q += hd.ellip(el, RW, (0.075, 0.075, 0.075), 8, 4, IRON_D)
        kn = P['_' + key + 'knee']; an = P['_' + key + 'ankle']                        # greave + knee cop
        Q += hd.limb(kn + (an - kn) * 0.08, an - (an - kn) * 0.12, 0.09, 0.08, IRON, n=10, m=1, ref=RW @ V((0, 0, 1.0)))
        Q += hd.ellip(kn, P['_RP'], (0.095, 0.09, 0.1), 8, 4, IRON_D)
    # breastplate: a front shell with the round cavity cut out of it
    bc = ch + RW @ V((0, -0.04, 0.03)); brx, bry, brz = 0.24 * bw, 0.25, 0.17 * bw
    cc_l = V((0, CR_Y + 0.04, 0))                                                   # cavity centre in the plate frame (y up, z forward)
    def keep(c_):
        if c_[2] < 0.0: return False
        return math.hypot(c_[0] - cc_l[0], c_[1] - cc_l[1]) > CR_R * 1.05
    Q += hd.ellip(bc, RW, (brx, bry, brz), 16, 9, IRON, keep=keep, colfn=lambda i, j, cl: IRON_L if (j % 8 == 0) else IRON)
    # the cavity: a short tube into the plate + a back wall; inside it the master (drawn by the caller with P['_crys'])
    zf = brz * math.sqrt(max(0.0, 1 - (cc_l[0] / brx) ** 2 - (cc_l[1] / bry) ** 2))
    cf = bc + RW @ V((cc_l[0], cc_l[1], zf))                                       # the opening (front)
    nrm = RW @ V((0, 0, 1.0)); Rc = np.column_stack([RW @ V((1.0, 0, 0)), nrm, -(RW @ V((0, 1.0, 0)))])
    lit = crystal == 'in'
    def in_hole(q):                                                             # body / plate faces inside the window's cylinder (they showed through)
        v = V(q['c']) - cf; al = float(v @ nrm); rad = float(np.linalg.norm(v - nrm * al)); return rad < CR_R * 1.0 and -0.6 < al < 0.03
    Q = [q for q in Q if q and not in_hole(q)]
    gl_ = glow if lit else 0.0
    tube = hd.lathe(tuple(cf - nrm * CR_DEPTH), Rc, [(CR_R * 0.9, 0.0), (CR_R, CR_DEPTH)], 16, mixc((10, 6, 8), (150, 34, 26), gl_), cap0=False, cap1=False)
    ux_, uy_ = RW @ V((1.0, 0, 0)), RW @ V((0, 1.0, 0)); bw_c = cf - nrm * CR_DEPTH                # the back wall: two flat discs (a lathe from r=0 broke)
    back = []
    for rr_, dz_, col_ in ((CR_R * 0.92, 0.0, (128, 24, 18)), (CR_R * 0.5, 0.002, (200, 44, 30))):
        q_ = hd.face([tuple(bw_c + nrm * dz_ + ux_ * rr_ * math.cos(a_) + uy_ * rr_ * math.sin(a_)) for a_ in np.linspace(0, 2 * PI, 17)[:-1]],
                     mixc((8, 4, 6), col_, gl_), inside=bw_c - nrm * 1.0)
        if q_: back.append(q_)
    for q in tube + back: q['emit'] = True; q['nobias'] = True                     # never lit by lamps (dark when empty); no emissive depth pull
    Q += tube + back
    Q += hd.lathe(tuple(cf - nrm * 0.01), Rc, [(CR_R * 1.18, 0.0), (CR_R * 1.02, 0.03)], 18, TRIM, cap0=False, cap1=False)   # gold bezel (no caps: a cap covered the window)
    P['_crys'] = (cf, Rc, nrm)
    # faulds (hip plates) + a gorget
    for i in range(3):
        Q += hd.ellip(P['_pel'] + P['_RP'] @ V((0, -0.08 - 0.09 * i, 0.0)), P['_RP'], (0.21 * bw, 0.06, 0.15 * bw), 14, 4, IRON if i % 2 == 0 else IRON_D, v0=PI * 0.25, v1=PI * 0.75)
    Q += hd.limb(P['_neck'] - RW @ V((0, 0.03, 0)), P['_neck'] + RW @ V((0, 0.08, 0)), 0.15, 0.13, IRON_D, n=12, m=1, ref=RW @ V((0, 0, 1.0)))
    # the closed helmet (bigger than the head: nothing of the face shows) + eye slits + horns
    def L(x, y, z): return hc + RH @ V((x, y, z))
    hr = (0.105 * k, 0.135 * k, 0.12 * k)
    Q += hd.ellip(L(0, 0.01 * k, 0.004 * k), RH, hr, 16, 10, IRON, colfn=lambda i, j, cl: IRON_L if (i == 0 or j == 0) else IRON)
    Q += hd.bx(L(0, 0.02 * k, hr[2] * 0.98), RH, (0.006 * k, 0.11 * k, 0.012 * k), IRON_L)                         # nose ridge
    Q += hd.limb(L(0, -0.08 * k, 0.03 * k), L(0, -0.12 * k, 0.05 * k), 0.08 * k, 0.07 * k, IRON_D, n=12, m=1, ref=RH @ V((0, 0, 1.0)))   # chin guard
    for sd in (1, -1):
        xs, ys = sd * 0.042 * k, 0.012 * k; zs = (hr[2]) * math.sqrt(max(0.0, 1 - (xs / hr[0]) ** 2 - ((ys - 0.01 * k) / hr[1]) ** 2))
        sc_ = L(xs, ys, zs + 0.004 * k)
        sn = nz(RH @ V((xs / hr[0] ** 2, 0.0, zs / hr[2] ** 2)))
        slit = hd.decal(tuple(sc_), tuple(sn), tuple(RH @ V((0, 1.0, 0))), 0.034 * k, 0.009 * k, mixc((8, 6, 8), (255, 70, 46), helm), emit=helm > 0.05, lift=0.004)
        Q += slit
        pts = [L(sd * 0.08 * k, 0.07 * k, -0.01 * k), L(sd * 0.14 * k, 0.12 * k, -0.03 * k), L(sd * 0.16 * k, 0.2 * k, -0.07 * k), L(sd * 0.13 * k, 0.27 * k, -0.1 * k)]
        rr = [0.03 * k, 0.024 * k, 0.015 * k, 0.003]
        for i in range(3): Q += hd.limb(pts[i], pts[i + 1], rr[i], rr[i + 1], (150, 140, 124) if i % 2 == 0 else (118, 110, 98), n=7, m=1)
    P['_slits'] = [L(sd * 0.042 * k, 0.012 * k, hr[2] * 0.97) for sd in (1, -1)]
    return [q for q in Q if q]
def greatsword(hilt, d, up, L_=2.0, w=0.075, col=(150, 154, 168)):
    """a giant's two-handed sword: hilt = the guard point, d = blade direction; grip runs back from the hilt 0.42 m"""
    d = nz(d); up = nz(V(up, float) - d * float(V(up, float) @ d)); sd = np.cross(d, up); h = V(hilt, float); Q = []
    Q += hd.limb(h - d * 0.42, h, 0.028, 0.028, (52, 30, 32), n=7, m=2, ref=up)
    Q += hd.ellip(h - d * 0.45, np.column_stack([sd, d, up]), (0.045, 0.045, 0.045), 7, 4, TRIM)
    Q += hd.bx(h + d * 0.02, np.column_stack([sd, d, up]), (0.2, 0.03, 0.035), TRIM)
    tip = h + d * L_
    for sgn in (1, -1):
        e = sd * w * sgn
        hd._add(Q, hd.face([h + d * 0.05 + e, tip - d * 0.16 + e * 0.6, tip, h + d * 0.05], col if sgn > 0 else hd.shade(col, 0.86), h - up * sgn * 0.1, closed=False))
        hd._add(Q, hd.face([h + d * 0.05 + e, tip - d * 0.16 + e * 0.6, tip, h + d * 0.05], hd.shade(col, 0.95), h + up * sgn * 0.1, closed=False))
    Q += hd.bx(h + d * (L_ * 0.4), np.column_stack([sd, d, up]), (0.012, L_ * 0.33, 0.0372), (90, 92, 104))      # fuller
    return [q for q in Q if q]
def gem(c, R, s=1.0, glow=1.0):
    """the crystal itself (ripped out): a red faceted gem, glowing while the master is inside"""
    col = mixc((60, 14, 16), (255, 80, 60), glow)
    Q = hd.ellip(tuple(c), R, (CR_R * 0.85 * s, CR_R * 0.85 * s, CR_R * 0.55 * s), 8, 4, col)
    for q in Q: q['emit'] = glow > 0.1
    return Q

# ----------------------- the master (old knight, tiny, inside the crystal) -----------------------
MS = 0.3                                                                       # the master is built full size, then scaled into the window
M_ANCH = V((0.0, 1.36, 0.0))                                                   # his chest point that sits at the window centre
MASTER = hd.spec(h=1.84, build=1.0, skin=(208, 168, 138), hair=(206, 204, 200), hair_style='short', beard=(214, 212, 206), eye=(60, 80, 110),
                 brow=(220, 218, 212), tunic=(150, 140, 120), tunic2=(124, 116, 100), skirt=0.0, pants=(90, 84, 76), boots=(60, 54, 48),
                 belt=(70, 50, 36), buckle=(210, 180, 90), gloves=(150, 156, 168), collar=(186, 194, 206))
def fit_frame(nrm, up):
    """rotation: canonical +z (his facing) -> nrm, canonical +y -> up (orthogonalised)"""
    z = nz(nrm); y = nz(V(up, float) - z * float(V(up, float) @ z)); x = np.cross(y, z); return np.column_stack([x, y, z])
def to_window(p, at, Rf, s=MS): return V(at) + Rf @ ((V(p, float) - M_ANCH) * s)
def master(P, at, Rf, s=MS):
    """the master (canonical pose: base at the origin, facing +z), scaled by s into the window at `at` with frame Rf:
    grey beard, worn tabard with the WHITE SUN on the chest"""
    Q = hd.human(MASTER, P); RW = P['_RW']; ch = P['_chest']
    Q += sun_emblem(ch + RW @ V((0, -0.01, 0.125)), RW @ V((0, 0, 1.0)), RW @ V((0, 1.0, 0)), 0.075)
    Q = [q for q in Q if q and np.mean([p[1] for p in q['p']]) > 0.98]          # above the hips only (the legs poked out under the plate)
    for q in Q: q['p'] = [tuple(to_window(p, at, Rf, s)) for p in q['p']]; refresh(q)
    return Q
def master_pose(t):
    """canonical pose (base at the origin, facing +z); returns (P, ember point in canonical space)"""
    P = dict(base=(0.0, 0.0, 0.0), yaw=0.0, eyes='open', mouth='neutral', brow=-0.3, lean=0.12, head=(0.0, 0.0, 0.0))
    P['lh'] = (-0.11, 1.2, 0.3); P['rh'] = (0.11, 1.2, 0.3); P['lgrip'] = 0.3; P['rgrip'] = 0.3
    P['lpalm'] = (1.0, 0.3, 0.3); P['rpalm'] = (-1.0, 0.3, 0.3)
    puff = max(0.0, math.sin(t * 6.3)) ** 3
    P['mouth'] = 'o' if puff > 0.4 else 'neutral'
    sc = scene(t)
    if sc == 'crys' and t >= T0['02'] - 0.35:                                     # waves hard to screen-left: "Left! Now!"
        u = sm(seg01(t, T0['02'] - 0.35, T0['02'])); wv = math.sin((t - T0['02']) * 14)
        P['rh'] = lerp3(P['rh'], (0.42 + 0.08 * wv, 1.62, 0.2), u); P['rgrip'] = 0.1; P['eyes'] = 'wide'; P['brow'] = 0.5
        P['mouth'] = 'open' if talking(t, '02') > 0.4 else 'grit'
    if sc in ('sweep', 'stare', 'master'):
        P['eyes'] = 'half' if sc == 'master' else 'open'; P['brow'] = -0.5
        if talking(t, '04') > 0.4: P['mouth'] = 'open'
        if sc == 'master': P['head'] = (0.0, -0.15 * win(t, T0['04'] + 0.3, T0['04'] + 1.3, 0.3), 0.0)   # a tired nod
    if sc == 'lookd':
        u = sm(seg01(t, T_TILT[0] + 0.2, T_TILT[1])); P['head'] = (0.0, 0.5 * u, 0.0); P['look'] = (0.0, 0.8 * u); P['eyes'] = 'wide' if u > 0.4 else 'open'
        P['mouth'] = 'neutral'; P['lean'] = 0.18 - 0.2 * u
    if sc == 'rip':
        P['eyes'] = 'wide'; P['brow'] = 0.6; P['mouth'] = 'open' if talking(t, '06') > 0.3 else 'o'; P['head'] = (0.0, 0.45, 0.0)
        P['lh'] = (-0.4, 1.55, 0.25); P['rh'] = (0.4, 1.55, 0.25); P['lgrip'] = 0.1; P['rgrip'] = 0.1
    return P, V((0.0, 1.22, 0.36))

# ======================= the duel layout =======================
B0 = V((0.45, 0.0, 9.0)); H0 = V((-0.5, 0.0, 7.6))                               # 1.97 m apart: the slam reaches H0; depth-staged for 9:16
BYAW0 = math.atan2(-0.6, -1.0); HYAW0 = math.atan2(1.0, -0.35)                   # both cheated 3/4 toward the lens (stage cheat)
_HR = V((math.cos(HYAW0), 0, -math.sin(HYAW0))); _HF = V((math.sin(HYAW0), 0, math.cos(HYAW0)))
H1 = H0 + _HR * 0.8 - _HF * 0.3                                                # first dive: his right = screen-left in frame 1 (lands at the frame edge)
H2 = H1 - _HR * 0.95 + _HF * 0.1                                               # the low dive under the sweep (his left)
H3 = H2 - _HF * 1.0 + _HR * 0.5                                                # the head-fake dive (away)
def ang_to(p, q): return math.atan2(q[0] - p[0], q[2] - p[2])

# ======================= the boss: body + sword =======================
def bl(p, base=None, yaw=None):
    """boss-local -> world"""
    return V(B0 if base is None else base, float) + hd.Ry(BYAW0 if yaw is None else yaw) @ V(p, float)
SW_L = 1.75
def boss_base(t):
    """he steps in toward the hero for the real strike (S_HELM)"""
    if t >= S_HELM and t < S_LOOP: return B0 + V((-0.5, 0.0, -0.12)) * sm(seg01(t, S_HELM, S_HELM + 0.8))
    return V(B0)
def shoulder_c(t): return bl((0.0, 2.05, 0.32), boss_base(t))                 # the swing pivot sits in front of the chest (hands stay out of the helmet)
def rest_sword(t):
    hilt = bl((0.42, 1.5, 0.5), boss_base(t)); tip = bl((0.62, 0.0, 0.5 + math.sqrt(SW_L ** 2 - 1.5 ** 2 - 0.2 ** 2)), boss_base(t)); tip[1] = 0.0
    return hilt, nz(tip - hilt)
def arc_sword(t, th, tgt=None, r=None):
    """overhead arc in the plane through the shoulders toward tgt (world floor point); th in radians (110 deg = over/behind the head).
    r (hilt distance from the shoulders) is chosen so that the tip lands exactly on tgt at the slam angle"""
    S_ = shoulder_c(t); tgt = V(H0 if tgt is None else tgt, float); f = tgt - S_; f[1] = 0.0; f = nz(f)
    if r is None: r = min(1.0, max(0.45, float(np.linalg.norm(tgt - S_)) - SW_L))
    u = nz(f * math.cos(th) + V((0, 1.0, 0)) * math.sin(th)); return S_ + u * r, u
TH_BACK = math.radians(128)
def up_sword(t, tgt=None, th=TH_BACK):
    """the windup: hilt above his RIGHT shoulder, blade back over it (hands beside the helmet, not over it)"""
    tgt = V(H0 if tgt is None else tgt, float); f = tgt - boss_base(t); f[1] = 0.0; f = nz(f); rv = nz(np.cross(f, V((0, 1.0, 0)))) * -1.0
    hilt = bl((0.36, 2.62, 0.3), boss_base(t))
    d = nz(f * math.cos(th) + V((0, 1.0, 0)) * math.sin(th) + rv * 0.18)
    return hilt, d
def slam_sw(t, u, tgt=None):
    """windup -> slam: the hilt travels forward-down, the blade direction rotates in the vertical plane (no lerp through zero)"""
    h0, _ = up_sword(t, tgt); h1, d1 = arc_sword(t, slam_angle(t, tgt), tgt)
    tgt = V(H0 if tgt is None else tgt, float); f = tgt - boss_base(t); f[1] = 0.0; f = nz(f); rv = nz(np.cross(f, V((0, 1.0, 0)))) * -1.0
    th = lerp(TH_BACK, slam_angle(t, tgt), u); d = nz(f * math.cos(th) + V((0, 1.0, 0)) * math.sin(th) + rv * 0.18 * (1 - u))
    return V(lerp3(tuple(h0), tuple(h1), sm(u))), d
def slam_angle(t, tgt=None):
    S_ = shoulder_c(t); tgt = V(H0 if tgt is None else tgt, float); dh = math.hypot(tgt[0] - S_[0], tgt[2] - S_[2]); return math.atan2(-S_[1], dh)
TH_UP = math.radians(80)                                                       # raised in front of the helmet (112 put the forearms through it)
def blend_sw(a, b, u):
    return V(lerp3(tuple(a[0]), tuple(b[0]), u)), nz(V(lerp3(tuple(a[1]), tuple(b[1]), u)))
def sweep_sword(t, ang):
    """horizontal sweep: blade radial at y 1.05, hilt 0.8 m from his centre; ang 0 = straight at the hero's first spot"""
    c = boss_base(t) + V((0, 1.05, 0)); f0 = V(H0) - V(B0); f0[1] = 0; a0 = math.atan2(f0[0], f0[2]) + ang
    u = V((math.sin(a0), 0.0, math.cos(a0))); return c + u * 0.95, u
def lift_sw(t, rest, up, u):
    """rest -> up through a point in front of him (a straight blend swept the blade and the arms through his body)"""
    mid = (bl((0.05, 1.75, 0.8), boss_base(t)), nz(bl((0.1, 0.75, 0.65), boss_base(t)) - boss_base(t)))
    return blend_sw(rest, mid, sm(min(1.0, u * 2))) if u < 0.5 else blend_sw(mid, up, sm(u * 2 - 1))
def sword_state(t):
    """(hilt, blade dir, two-hand weight 0..1: 0 = right hand only, 1 = both hands on the grip)"""
    rest = rest_sword(t)
    if t < S_SIDE + 0.6:                                                       # frame 1: rest -> lift -> slam into the empty spot
        if t < T_LIFT[0]: return rest + (0.0,)
        up = up_sword(t); w2 = sm(seg01(t, T_LIFT[0], T_LIFT[0] + 0.4))
        if t < T_LIFT[1]: return lift_sw(t, rest, up, seg01(t, *T_LIFT)) + (w2,)
        if t < T_SLAM: u = seg01(t, T_LIFT[1] + 0.12, T_SLAM) ** 2.2; return slam_sw(t, u) + (1.0,)
        return arc_sword(t, slam_angle(t)) + (1.0,)                            # the blade stays in the cracked floor
    if t < S_SWEEP:                                                            # he pulls it out and plants it again
        k = sm(seg01(t, S_SIDE + 0.6, S_SIDE + 1.6)); return blend_sw(arc_sword(t, slam_angle(t)), rest, k) + (1 - k,)
    if t < S_MASTER:                                                           # the sweep (one hand) that passes over the low dive
        if t < T_SWEEP[0] - 0.35: return rest + (0.0,)
        a = sweep_sword(t, 1.45)
        if t < T_SWEEP[0]: return blend_sw(rest, a, sm(seg01(t, T_SWEEP[0] - 0.35, T_SWEEP[0]))) + (0.0,)
        u = seg01(t, *T_SWEEP); s_ = sweep_sword(t, lerp(1.45, -0.6, sm(u)))
        if t < T_SWEEP[1] + 0.25: return s_ + (0.0,)
        return blend_sw(sweep_sword(t, -0.6), rest, sm(seg01(t, T_SWEEP[1] + 0.25, T_SWEEP[1] + 1.0))) + (0.0,)
    if t < S_FAKE: return rest + (0.0,)
    if t < S_HELM:                                                             # HEAD FAKE: big windup, held over the head ... nothing
        up = up_sword(t, H2)
        return lift_sw(t, rest, up, seg01(t, *T_WIND)) + (sm(seg01(t, T_WIND[0], T_WIND[0] + 0.3)),)
    if t < S_LOOP:                                                             # the real strike rises (it never lands on screen)
        return up_sword(t, H3, lerp(TH_BACK - 0.3, TH_BACK, sm(seg01(t, S_HELM, S_HELM + 1.0)))) + (1.0,)
    return up_sword(t) + (1.0,)                                        # the loop shot: raised, ready (behind the glowing helmet)
def boss_pose(t):
    base = boss_base(t); yaw = BYAW0
    P = dict(base=tuple(base), yaw=yaw, eyes='half', mouth='neutral', brow=-0.6, lean=0.05, cape_sway=0.1 * math.sin(t * 1.1), head=(0.0, -0.12, 0.0))
    hilt, d, w2 = sword_state(t)
    P['rh_w'] = tuple(hilt - d * 0.12); P['rpalm'] = tuple(nz(np.cross(d, V((0, 1.0, 0))) + V((0, 0.01, 0)))); P['rpalm_local'] = False; P['rgrip'] = 0.95
    free_l = bl((-0.42, 1.18, 0.16), base)                                     # the free left hand (world), blended onto the grip (no snap)
    P['lh_w'] = tuple(lerp3(tuple(free_l), tuple(hilt - d * 0.32), w2)); P['lpalm_local'] = False
    P['lpalm'] = tuple(nz(lerp3(tuple(-nz(np.cross(_BF, V((0, 1.0, 0))))), tuple(-V(P['rpalm'])), w2))); P['lgrip'] = lerp(0.6, 0.95, w2)
    if w2 > 0: P['lpole'] = (-1.0, -0.15 + 0.3 * w2, 0.35)                     # two hands: the left elbow out to the side (it crossed the chest)
    # the stare: helmet follows the hero's gaze (from "Master?"), then down to his own chest
    kh = V(H1) + V((0, 1.0, 0)); dv = kh - V(base); hy_to = angd(0.0, math.atan2(dv[0], dv[2]) - yaw, 1.0)
    f1 = sm(seg01(t, T0['03'] + 0.4, tend('03') + 0.3)) * 0.35 if t < S_LOOKD else 0.0
    if S_LOOKD <= t < S_DARK:
        f1 = 0.35 + 0.65 * sm(seg01(t, *T_FOLLOW))
        dn = sm(seg01(t, *T_TILT)); P['head'] = (hy_to * f1 * (1 - dn), -0.12 - 0.85 * dn, 0.0)
        if t >= S_RIP: P['head'] = (0.0, -0.87 + 0.5 * sm(seg01(t, T_RIP[1], T_CRUSH + 0.3)), 0.0)
    elif f1 > 0: P['head'] = (hy_to * f1, -0.12, 0.0)
    # the rip: the LEFT gauntlet closes around the crystal, tears it out, crushes it
    if S_RIP <= t < S_DARK:
        P['lean'] = 0.1
        cf = boss_crys_front(t)
        g = sm(seg01(t, *T_GRIP)); out = sm(seg01(t, *T_RIP)) ** 0.7
        idle = bl((-0.42, 1.25, 0.25), base); held = bl((-0.55, 1.55, 0.75), base)
        idle = free_l
        hand = V(lerp3(tuple(idle), tuple(cf + nz(cf - bl((0, 1.9, 0), base)) * 0.12), g)); hand = V(lerp3(tuple(hand), tuple(held), out))
        if t >= T_CRUSH - 0.1: hand = hand + V((0, 0.03 * math.sin(t * 50), 0)) * win(t, T_CRUSH - 0.1, T_CRUSH + 0.3, 0.05)
        P.pop('lh', None); P['lh_w'] = tuple(hand); P['lpalm'] = tuple(-nz(cf - bl((0.0, 1.9, 0.0), base))); P['lpalm_local'] = False
        P['lpole'] = (-1.0, -0.35, 0.15)                                       # the elbow out to the side (the arm went through the chest)
        P['lgrip'] = lerp(0.35, 0.9, g) if t < T_CRUSH else 1.0
    if t >= T_LAUGH and t < S_HELM:                                            # an iron laugh: shoulders shake
        P['pel'] = (0.0, 0.025 * abs(math.sin((t - T_LAUGH) * 14)) * win(t, T_LAUGH, T_LAUGH + 1.4, 0.2), 0.0); P['head'] = (0.15, 0.1, 0.0)
    if S_HELM <= t:
        P['head'] = (0.0, -0.05, 0.0)
    P['_hilt'] = hilt; P['_d'] = d
    return P
_CF = {}
def boss_crys_front(t):
    """the cavity's front centre at time t (from the pose without the rip, cached)"""
    k = round(t, 4)
    if k not in _CF:
        if len(_CF) > 50: _CF.clear()
        P = boss_pose_norip(t); boss(P); _CF[k] = P['_crys'][0]
    return _CF[k]
def boss_pose_norip(t):
    base = boss_base(t); P = dict(base=tuple(base), yaw=BYAW0, lean=0.1, head=(0.0, -0.87, 0.0)); hilt, d, _ = sword_state(t)
    P['rh_w'] = tuple(hilt - d * 0.12); P['lh_w'] = tuple(bl((-0.42, 1.18, 0.16), base)); return P

# ======================= the hero =======================
def stance(base, yaw, t):
    P = dict(base=tuple(base), yaw=yaw, eyes='open', mouth='neutral', brow=-0.4, lean=0.1, crouch=0.1, cape_sway=0.15 * math.sin(t * 1.3), head=(0.0, 0.22, 0.0))
    P['rh'] = (0.04, 1.28, 0.42); P['rpalm'] = (0.0, 0.0, -1.0); P['rgrip'] = 0.85                         # shield arm across the chest
    P['lh'] = (-0.3, 1.0, 0.3); P['lgrip'] = 0.9; P['lpalm'] = (1.0, 0.0, 0.0)
    P['rf'] = (0.14, 0.075, -0.12); P['lf'] = (-0.13, 0.075, 0.16)
    P['_blade'] = (-0.55, -0.8, 0.35)                                          # point low, out to his left side (it crossed the frame)
    return P
def dive(P, a, b, u, low=0.0):
    """a sideways dive from a to b (world), u 0..1: arc, body roll toward the travel side, tucked legs, a crouched landing"""
    a = V(a); b = V(b); pu = sm(u); p = a + (b - a) * pu; hgt = (0.32 - 0.2 * low) * math.sin(PI * min(1.0, u * 1.15))
    P['base'] = (p[0], max(0.0, hgt) * (1 if u < 0.87 else 0), p[2])
    yaw = P['yaw']; rv = V((math.cos(yaw), 0, -math.sin(yaw))); dirv = nz(b - a); side = float(dirv @ rv)             # + = his right
    P['roll'] = -0.55 * side * math.sin(PI * u); P['lean'] = 0.25 + 0.25 * low
    tuck = math.sin(PI * min(1.0, u * 1.1)); P['rf'] = (0.14, 0.075 + 0.25 * tuck, 0.05); P['lf'] = (-0.13, 0.075 + 0.3 * tuck, 0.1)
    P['crouch'] = 0.1 + (0.38 + 0.15 * low) * sm(seg01(u, 0.7, 1.0)); P['eyes'] = 'wide'; P['mouth'] = 'grit'; P['brow'] = 0.4
    P['rh'] = (0.06 + 0.2 * low, 1.32 - 0.22 * low, 0.38 + 0.04 * low)       # the low dive: shield out to the side (it went into the head)
    return P
def land(P, u):
    """after a dive: a crouch that rises (u 0..1)"""
    P['crouch'] = lerp(0.53, 0.1, sm(u)); P['lean'] = lerp(0.35, 0.1, sm(u)); return P
def hero_pose(t):
    sc = scene(t); tt = t - DUR if t >= S_LOOP else t
    if t < S_SIDE or t >= S_LOOP:                                              # frame 1 (and the loop shot): H0
        P = stance(H0, HYAW0, t)
        if t >= S_LOOP:                                                        # the loop: helmet glows behind; the shield comes up over the lens
            P['head'] = (0.0, 0.3, 0.0); P['look'] = (0.0, 0.5); P['eyes'] = 'wide'; P['brow'] = 0.3
            u = sm(seg01(t, T_COVER[0] - 0.45, DUR)); P.pop('rh'); P['rh_w'] = tuple(lerp3(tuple(stance_rh_w()), tuple(cover_pt(1.0)), u))
            P['rpalm'] = tuple(nz(cam_fwd_loop() * (0.55 + 0.45 * u) - nz(V(B0) - V(H0)) * 0.45 * (1 - u))); P['rpalm_local'] = False
            return P
        u0 = 1 - sm(seg01(t, 0.0, 0.42))                                       # frame 0: the shield leaves the lens
        P.pop('rh'); P['rh_w'] = tuple(lerp3(tuple(stance_rh_w()), tuple(cover_pt(1.0)), u0))
        P['rpalm'] = tuple(nz(cam_fwd_loop() * (0.55 + 0.45 * u0) - nz(V(B0) - V(H0)) * 0.45 * (1 - u0))); P['rpalm_local'] = False   # shield faces lens + boss
        lk = sm(seg01(t, *T_LOOK)); P['head'] = (0.15 * lk, 0.22 + 0.25 * lk, 0.0); P['look'] = (0.2 * lk, 0.7 * lk)    # touch 1: up at the crystal
        P['eyes'] = 'wide' if lk > 0.5 else 'open'; P['brow'] = lerp(-0.4, 0.5, lk)
        if t >= T_DIVE[0]:
            P.pop('rh_w', None); P['rpalm'] = (0.0, 0.0, -1.0); P['rpalm_local'] = True           # the shield hand rides with the body in the dive
            P = dive(P, H0, H1, seg01(t, *T_DIVE)); P['head'] = (0.0, 0.25, 0.0); P['look'] = (0.0, 0.3)
        if t >= T_DIVE[1]: P['base'] = tuple(H1); P = land(P, 0.0); P['head'] = (0.4, 0.15, 0.0); P['look'] = (0.5, 0.0)
        if t >= T_SLAM - 0.05: P['eyes'] = 'wide'
        return P
    if t < S_SWEEP:                                                            # rises at H1, shield up: the white sun to the lens
        P = stance(H1, HYAW0, t); P = land(P, seg01(t, *T_RISE)); P['head'] = (0.0, 0.15, 0.0)
        r_ = sm(seg01(t, T_RISE[0] + 0.2, T_RISE[1])); P['rh'] = lerp3((0.06, 1.32, 0.38), (0.1, 1.45, 0.48), r_)
        if t >= S_CRYS - 0.5: P['head'] = (0.0, 0.3, 0.0); P['look'] = (0.0, 0.5)
        return P
    if t < S_DARK:                                                             # the low dive under the sweep -> kneels, stares at the crystal
        P = stance(H1, HYAW0, t)
        if t >= T_DIVE2[0]: P = dive(P, H1, H2, seg01(t, *T_DIVE2), low=1.0)
        if t >= T_DIVE2[1]:
            P['base'] = tuple(H2); P['roll'] = 0.0; P['crouch'] = 0.45; P['lean'] = 0.22; P['rf'] = (0.16, 0.075, -0.3); P['lf'] = (-0.13, 0.075, 0.25)
            P['rh'] = (0.34, 0.82, 0.2); P.pop('rpalm', None)                   # shield down at his side: his face is free for the stare
            yaw2 = ang_to(H2, B0); P['yaw'] = angd(HYAW0, yaw2, sm(seg01(t, T_DIVE2[1], T_DIVE2[1] + 0.4)))
            st = sm(seg01(t, T_STARE - 0.2, T_STARE + 0.3))                    # touch 2: the stare locks on the crystal and stays
            P['head'] = (0.0, 0.2 + 0.3 * st, 0.0); P['look'] = (0.0, 0.6 * st); P['eyes'] = 'wide'; P['brow'] = lerp(0.4, 0.7, st)
            P['mouth'] = 'open' if talking(t, '03') > 0.45 else ('o' if st > 0.5 else 'neutral')
            if t >= S_RIP: P['brow'] = 0.9; P['mouth'] = 'open' if T_RIP[0] <= t < T_CRUSH + 0.4 else 'grit'
        return P
    if t < S_FAKE:                                                             # the dark: alone, shield shaking
        P = stance(H2, ang_to(H2, B0), t); P['brow'] = 0.6; P['eyes'] = 'wide'; P['mouth'] = 'neutral'
        P['rh'] = (0.1 + 0.006 * math.sin(t * 31), 1.02 + 0.006 * math.sin(t * 27), 0.38); P['head'] = (0.0, 0.25, 0.0); P['look'] = (0.15 * math.sin(t * 2.1), 0.3)
        return P
    P = stance(H2, ang_to(H2, B0), t); P['eyes'] = 'wide'; P['brow'] = 0.6
    if t >= T_DIVE3[0]: P = dive(P, H2, H3, seg01(t, *T_DIVE3))
    if t >= T_DIVE3[1]:
        P['base'] = tuple(H3); P['roll'] = 0.0; P = land(P, 0.0); P['head'] = (0.3, 0.3, 0.0); P['look'] = (0.3, 0.4)
        if t >= S_HELM: P['head'] = (0.2, 0.45, 0.0); P['look'] = (0.0, 0.6)
    return P
def hero_sword(P):
    g = grip_pt(P, 'l', 0.06, 0.0); d = hd.Ry(P['yaw']) @ V(P.get('_blade', (0.05, 0.55, 1.0)))
    return hd.sword(tuple(g), tuple(nz(d)), P['_lpalm'], length=0.85)
def smooth_pose(fn, t, span=0.06):
    """average every numeric pose value over +-span (weights 1-2-3-2-1), only with samples from the same shot"""
    P0 = fn(t)
    if P0 is None: return None
    sc = scene(t); S_ = []
    for dt, w in ((-span, 1), (-span / 2, 2), (0.0, 3), (span / 2, 2), (span, 1)):
        ts = t + dt
        if ts < 0 or ts >= DUR or scene(ts) != sc: continue
        P = P0 if dt == 0 else fn(ts)
        if P is not None: S_.append((P, w))
    out = dict(P0)
    for k, v in P0.items():
        if k.startswith('_') or isinstance(v, (str, bool)) or v is None: continue
        vals = [(P.get(k), w) for P, w in S_]
        if any(x is None or type(x) != type(v) for x, _ in vals): continue
        wt = sum(w for _, w in vals)
        if isinstance(v, (int, float)): out[k] = sum(float(x) * w for x, w in vals) / wt
        elif isinstance(v, (tuple, list)) and all(len(x) == len(v) for x, _ in vals):
            out[k] = tuple(sum(float(x[i]) * w for x, w in vals) / wt for i in range(len(v)))
    return out

# ======================= camera =======================
HF = V((math.sin(HYAW0), 0, math.cos(HYAW0))); HR = V((math.cos(HYAW0), 0, -math.sin(HYAW0)))       # the hero's forward / right
_BF = V((math.sin(BYAW0), 0, math.cos(BYAW0))); _BL = -V((math.cos(BYAW0), 0, -math.sin(BYAW0)))    # boss forward / boss left
O_POS = V((-0.3, 0.8, 5.35)); O_TGT = V((0.0, 1.55, 8.3)); O_FOV = 48.0
def cam_fwd_loop(): return nz(O_TGT - O_POS)
def cover_pt(u):
    """the block: the shield thrust toward the boss (= toward the lens), at chest height"""
    return V(H0) + _HF * 0.62 + V((0, 1.32, 0)) - _HR * 0.05
def stance_rh_w():
    P = stance(H0, HYAW0, 0.0); hd.human(KN, P); return P['_rwrist']
_SHC = {}
def shield_at(t):
    """the hero's shield face (centre, normal) at t, from the smoothed pose (cached)"""
    k = round(t, 4)
    if k not in _SHC:
        if len(_SHC) > 40: _SHC.clear()
        P = smooth_pose(hero_pose, t); hd.human(KN, P); c, n, _ = knight_shield(P); _SHC[k] = (V(c), V(n))
    return _SHC[k]
def cam_shot(t):
    sc = scene(t); idx = [n for n, _ in CUTS].index(sc); a = CUTS[idx][1]; b = CUTS[idx + 1][1] if idx + 1 < len(CUTS) else DUR; u = sm(seg01(t, a, b))
    if sc in ('open', 'loop'):
        sh_c, sh_n = shield_at(t)                                              # the shield face during the block (from the pose)
        if sc == 'open':
            k = motion.creep(t, 0.0, 0.0022); p = V(motion.dolly(tuple(O_POS), tuple(O_TGT), k))
            back = 1 - sm(seg01(t, 0.0, 0.5))                                  # frame 0: pulls back out of the shield
            return V(lerp3(tuple(p), tuple(sh_c + sh_n * 0.32), back ** 1.5)), V(lerp3(tuple(O_TGT), tuple(sh_c), back ** 1.5)), O_FOV
        s_ = sm(seg01(t, T_COVER[0] - 0.3, DUR)) ** 1.5; p = V(O_POS)
        return V(lerp3(tuple(p), tuple(sh_c + sh_n * 0.32), s_)), V(lerp3(tuple(O_TGT), tuple(sh_c), s_)), O_FOV
    if sc == 'side':                                                           # from beside the boss: the hero rises, the sun to the lens
        tg = V(H1) + V((0.05, 1.05, 0.0)); p = tg + nz(V(B0) - V(H1) + V((0, 0, -1.6))) * 2.6 + V((0, 0.15, 0))
        return V(motion.dolly(tuple(p), tuple(tg), motion.creep(t, a, 0.002))), tg, 44.0
    if sc == 'crys':
        BP = smooth_pose(boss_pose, t); boss(BP); cf, Rc, nrm = BP['_crys']
        tg = cf - nrm * 0.03; p0 = cf + nrm * 1.35 + V((0, -0.25, 0)); p1 = cf + nrm * 0.62 + V((0, -0.08, 0))
        return V(lerp3(tuple(p0), tuple(p1), sm(seg01(t, a, a + 1.6)))), tg, 34.0
    if sc == 'sweep':                                                          # side two-shot: the blade passes over the low dive
        mid = (V(H1) + V(H2)) / 2 * 0.6 + V(B0) * 0.4 + V((0, 0.95, 0)); dl = nz(V(B0) - V(H1)); pp = V((-dl[2], 0, dl[0]))
        if pp[2] > 0: pp = -pp
        p = mid + pp * 3.3 + V((0, -0.15, 0)) + dl * 0.2 * u; return p, mid, 50.0
    if sc == 'stare':                                                          # from the crystal: he stares right into the lens (gives the master away)
        KP = smooth_pose(hero_pose, t); hd.human(KN, KP); hh = V(KP['_head']); cf = boss_crys_front(t)
        p = cf + nz(hh - cf) * 0.5; tg = hh + V((0, -0.05, 0))
        return V(motion.dolly(tuple(p + (p - hh) * 0.0), tuple(tg), motion.creep(t, a, 0.002))), tg, 40.0
    if sc == 'master':
        BP = smooth_pose(boss_pose, t); boss(BP); cf, Rc, nrm = BP['_crys']
        side = nz(V(H2) - cf); side[1] = 0; dirc = nz(nrm * 0.75 + nz(side) * 0.25)
        tg = cf - nrm * 0.03; p = cf + dirc * lerp(0.7, 0.58, u) + V((0, -0.05, 0)); return p, tg, 32.0
    if sc == 'lookd':                                                          # low angle on the boss's upper body: helmet + chest
        BP = smooth_pose(boss_pose, t); boss(BP); cf = BP['_crys'][0]; hc = V(BP['_head'])
        tg = (cf * 0.5 + hc * 0.5); dirc = nz(V(H2) - V(B0)); dirc[1] = 0; dirc = hd.Ry(-1.05) @ nz(dirc)
        p = tg + dirc * lerp(1.85, 1.65, u) + V((0, -0.55, 0)); return p, tg, 40.0
    if sc == 'rip':                                                            # side close-up: gauntlet + chest
        BP = smooth_pose(boss_pose, t); boss(BP); cf = boss_crys_front(t); bf = V((math.sin(BYAW0), 0, math.cos(BYAW0))); br = V((math.cos(BYAW0), 0, -math.sin(BYAW0)))
        tg = cf + bf * 0.25 - br * 0.15 + V((0, 0.0, 0)); p = tg + nz(bf * 0.6 - br * 1.0) * 1.7 + V((0, 0.05, 0))
        return V(motion.dolly(tuple(p), tuple(tg), motion.creep(t, a, 0.0015))), tg, 40.0
    if sc == 'dark':
        yaw = ang_to(H2, B0); f_ = V((math.sin(yaw), 0, math.cos(yaw))); r_ = V((math.cos(yaw), 0, -math.sin(yaw)))
        tg = V(H2) + V((0, 1.35, 0)); p = tg + f_ * 1.6 + r_ * 0.55 + V((0, 0.05, 0))
        return V(motion.dolly(tuple(p), tuple(tg), motion.creep(t, a, 0.0025))), tg + f_ * 0.6, 46.0
    if sc == 'fake':                                                           # side two-shot, perpendicular to the duel line
        mid = (V(H2) + V(B0)) / 2 + V((0, 1.4, 0)); dl = nz(V(B0) - V(H2)); pp = V((-dl[2], 0, dl[0]))
        if pp[2] > 0: pp = -pp
        p = mid + pp * 3.6 + V((0, -0.3, 0)) + dl * 0.2 * u; return p, mid + V((0, 0.15, 0)), 52.0
    if sc == 'helm':
        BP = smooth_pose(boss_pose, t); boss(BP); hc = V(BP['_head']); dirc = nz(V(H3) - V(boss_base(t))); dirc[1] = 0; dirc = nz(dirc)
        tg = hc + V((0, -0.05, 0)); p = tg + dirc * lerp(1.7, 1.25, u) + V((0, -0.55, 0)); return p, tg, 38.0
    return O_POS, O_TGT, O_FOV

# ======================= world =======================
SHARDS = [(hsh(i, 5) * 2 - 1, 0.4 + hsh(i, 6) * 1.4, hsh(i, 7) * 2 - 1, hsh(i, 8)) for i in range(16)]
def shards(t, c):
    if not (T_CRUSH <= t < T_CRUSH + 1.0): return []
    u = t - T_CRUSH; Q = []
    for i, (vx, vy, vz, s_) in enumerate(SHARDS):
        p = V(c) + V((vx * 1.1, vy, vz * 1.1)) * u + V((0, -4.9 * u * u, 0))
        if p[1] < 0.02: p[1] = 0.02
        r = 0.018 + 0.02 * s_; a = u * 9 + i
        col = mixc((255, 90, 70), (90, 20, 24), u)
        q = hd.face([tuple(p + V((r * math.cos(a), r * math.sin(a), 0))), tuple(p + V((-r * math.sin(a), r * 0.3, r))), tuple(p + V((-r * math.cos(a), -r * math.sin(a), 0)))], col, emit=u < 0.5)
        if q: Q.append(q)
    return Q
def crack_decal(t):
    """the cracked floor where the blade hit (from T_SLAM on)"""
    if t < T_SLAM: return []
    c = V(H0) + V((0, 0.012, 0)); Q = []
    for i in range(9):
        a = 2 * PI * i / 9 + 0.3 * hsh(i, 3); l = 0.35 + 0.4 * hsh(i, 4)
        e = c + V((math.cos(a) * l, 0, math.sin(a) * l)); n_ = V((-math.sin(a), 0, math.cos(a))) * 0.015
        q = hd.face([tuple(c + n_), tuple(e), tuple(c - n_)], (24, 20, 24))
        if q: Q.append(q)
    return Q
def world(t):
    pos, tgt, fov = cam_shot(t)
    BP = smooth_pose(boss_pose, t); cs = crystal_state(t); gl = glow_on(t); he = helm_on(t)
    QB = boss(BP, crystal='in' if cs == 'in' else 'empty', glow=gl, helm=he)
    layers = [FB.ARENA, FB.torches(t), crack_decal(t), QB]
    cf, Rc, nrm = BP['_crys']; Rf = fit_frame(nrm, BP['_RW'] @ V((0, 1.0, 0)))
    em_w = None
    if cs == 'in':                                                             # the master in the window
        MP, em = master_pose(t); at = cf - nrm * (CR_DEPTH * 0.45)
        layers.append(master(smooth_pose(lambda x: master_pose(x)[0], t) or MP, at, Rf))
        em_w = to_window(em, at, Rf)
        E = hd.ellip(tuple(em_w), np.eye(3), (0.012, 0.014, 0.012), 6, 4, (255, 200, 120))
        for q in E: q['emit'] = True; q['nobias'] = True
        layers.append(E)
    gem_c = None
    if cs == 'hand':
        gem_c = grip_pt(BP, 'l', 0.09, 0.06); layers.append(gem(gem_c, BP['_RW'], 1.0 - 0.25 * seg01(t, T_CRUSH - 0.2, T_CRUSH), glow=gl))
    if T_CRUSH <= t: layers.append(shards(t, grip_pt(BP, 'l', 0.09, 0.06)))
    layers.append(greatsword(BP['_hilt'], BP['_d'], np.cross(BP['_d'], V((0, 1.0, 0))) + V((0, 0.001, 0))))
    KP = smooth_pose(hero_pose, t); QK = knight(KP); KP['_shield'] = knight_shield(KP); QK = knight(KP)
    layers.append(QK); layers.append(hero_sword(KP))
    # lights: cold key from high left, a weak cool fill, the wall torches (dim, warm), the crystal (red), the helmet (red)
    L = [((-4.0, 8.0, 3.0), (130, 150, 230), 9.0), ((3.0, 3.0, 2.0), (90, 100, 160), 1.2)] + FB.torch_lights(t, dim=0.32)
    if cs == 'in':
        L.append((tuple(cf + nrm * 1.3), (255, 60, 40), 1.6 * gl))
        if em_w is not None: L.append((tuple(em_w + nrm * 0.04 + BP['_RW'] @ V((0, 0.02, 0))), (255, 196, 130), 0.5 + 0.35 * gl))
    if cs == 'hand': L.append((tuple(gem_c + V((0, 0.2, 0))), (255, 60, 40), 1.6 * gl))
    if he > 0: L.append((tuple(V(BP['_head']) + BP['_RH'] @ V((0, 0, 0.8))), (255, 60, 40), 1.8 * he))
    return layers, L, (BP, KP, em_w, gem_c)
def frame_low(t):
    pos, tgt, fov = cam_shot(t)
    sh = motion.kick(t, T_SLAM, amp=0.05, frames=8) + motion.kick(t, T_CRUSH, amp=0.02, frames=6) + 0.6 * motion.kick(t, T_SWEEP[1] - 0.25, amp=0.02, frames=5)
    pos = V(pos) + V((0.0, sh, 0.0)); cam = Camera.look(tuple(pos), tuple(tgt))
    layers, L, poses = world(t)
    R = Renderer(W, H, fog=(10, 12, 22))
    img, vi, zb = zrender(R, cam, layers, L, fov=fov, fog_start=7.0, fog_end=24.0, ambient=0.2, return_z=True)
    a = look.outline(np.asarray(img).astype(np.float32), zb)
    a = np.clip((a - 80) * 1.14 + 84, 0, 255)
    a = a * 0.8 + (a * np.array([0.84, 0.9, 1.16])) * 0.2                    # cold grade
    return post.ps1(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), levels=6), vi, R, poses, zb

# ======================= 2D light + glass (1080 x 1920) =======================
def _proj(R, vi, p):
    q = R.project(tuple(p), vi); return None if q is None else (q[0] * S, q[1] * S, q[2])
def glow(arr, R, vi, p, rad_m, col, k):
    q = _proj(R, vi, p)
    if q is None: return arr
    r = max(6.0, rad_m * vi[7] * S / max(0.2, q[2])); x0, x1 = int(max(0, q[0] - r)), int(min(W * S, q[0] + r)); y0, y1 = int(max(0, q[1] - r)), int(min(H * S, q[1] + r))
    if x1 <= x0 or y1 <= y0: return arr
    yy, xx = np.mgrid[y0:y1, x0:x1]; d = np.sqrt((xx - q[0]) ** 2 + (yy - q[1]) ** 2) / r
    m = np.clip(1 - d, 0, 1) ** 2.2 * k; arr[y0:y1, x0:x1] += m[..., None] * np.array(col, np.float32)
    return arr
def pool(arr, R, vi, c, rad, col, k, blur=18):
    pts = [_proj(R, vi, V(c) + V((rad * math.cos(a), 0.0, rad * math.sin(a)))) for a in np.linspace(0, 2 * PI, 20)[:-1]]
    if any(p_ is None for p_ in pts): return arr
    ov = Image.new('L', (W * S, H * S), 0); ImageDraw.Draw(ov).polygon([(p_[0], p_[1]) for p_ in pts], fill=255)
    m = np.asarray(ov.filter(ImageFilter.GaussianBlur(blur))).astype(np.float32) / 255.0 * k
    return arr + m[..., None] * np.array(col, np.float32)
WMASK = [None]
def window_mask(R, vi, BP):
    cf, Rc, nrm = BP['_crys']; ux = BP['_RW'] @ V((1.0, 0, 0)); uy = BP['_RW'] @ V((0, 1.0, 0))
    pts = [_proj(R, vi, cf + ux * CR_R * math.cos(a) + uy * CR_R * math.sin(a)) for a in np.linspace(0, 2 * PI, 25)[:-1]]
    if any(p_ is None for p_ in pts): return None
    ov = Image.new('L', (W * S, H * S), 0); ImageDraw.Draw(ov).polygon([(p_[0], p_[1]) for p_ in pts], fill=255)
    return np.asarray(ov.filter(ImageFilter.GaussianBlur(4))).astype(np.float32) / 255.0
def glass(arr, R, vi, BP, t):
    """the crystal window: a red tint over it, a bright rim and a highlight streak (it reads as glass, the master is behind it)"""
    cf, Rc, nrm = BP['_crys']; ux = BP['_RW'] @ V((1.0, 0, 0)); uy = BP['_RW'] @ V((0, 1.0, 0))
    pts = [_proj(R, vi, cf + nrm * 0.004 + ux * CR_R * math.cos(a) + uy * CR_R * math.sin(a)) for a in np.linspace(0, 2 * PI, 25)[:-1]]
    if any(p_ is None for p_ in pts): return arr
    ov = Image.new('L', (W * S, H * S), 0); dd = ImageDraw.Draw(ov); dd.polygon([(p_[0], p_[1]) for p_ in pts], fill=255)
    m = np.asarray(ov.filter(ImageFilter.GaussianBlur(3))).astype(np.float32) / 255.0
    g = glow_on(t)
    arr = arr * (1 - m[..., None] * 0.12) + m[..., None] * np.array([255, 50, 40], np.float32) * 0.1 * g
    hl = Image.new('L', (W * S, H * S), 0); dh = ImageDraw.Draw(hl)
    arc_ = [_proj(R, vi, cf + nrm * 0.006 + ux * CR_R * 0.78 * math.cos(a) + uy * CR_R * 0.78 * math.sin(a)) for a in np.linspace(1.9, 2.9, 8)]
    if all(p_ is not None for p_ in arc_):
        wd = max(2, int(abs(arc_[0][0] - arc_[-1][0]) * 0.12) + 2); dh.line([(p_[0], p_[1]) for p_ in arc_], fill=200, width=wd)
    mh = np.asarray(hl.filter(ImageFilter.GaussianBlur(2))).astype(np.float32) / 255.0
    return arr + mh[..., None] * np.array([255, 236, 226], np.float32) * 0.55
def lights2d(arr, t, vi, R, poses):
    BP, KP, em_w, gem_c = poses; cs = crystal_state(t); g = glow_on(t)
    for k_, (x, y, z) in enumerate(FB.TORCHES):                                # wall torches: a warm glow
        arr = glow(arr, R, vi, V((x, y + 0.2, z)), 0.5, (255, 140, 60), 0.35)
    if cs == 'in':
        cf, Rc, nrm = BP['_crys']; WMASK[0] = window_mask(R, vi, BP)
        halo = glow(np.zeros_like(arr), R, vi, cf + nrm * 0.05, 0.55, (255, 60, 40), 0.65 * g)
        arr = arr + halo * (1 - WMASK[0][..., None]) if WMASK[0] is not None else arr + halo
        arr = glass(arr, R, vi, BP, t)
        if em_w is not None: arr = glow(arr, R, vi, em_w, 0.05, (255, 200, 120), 0.9)
        arr = pool(arr, R, vi, V((cf[0], 0.0, cf[2])) + nrm * 1.2, 1.6, (255, 50, 36), 0.22 * g, 26)
    if cs == 'hand' and gem_c is not None: arr = glow(arr, R, vi, gem_c, 0.45, (255, 60, 40), 0.6 * g)
    if T_SPARK[0] <= t < T_SPARK[1]:                                           # the escaping spark: fist -> neck seam (easy to miss)
        u = sm(seg01(t, *T_SPARK)); a = grip_pt(BP, 'l', 0.09, 0.06); b = V(BP['_neck']) + BP['_RW'] @ V((0.08, 0.0, 0.12))
        p = a + (b - a) * u + V((0, 0.25 * math.sin(PI * u), 0)); arr = glow(arr, R, vi, p, 0.05, (255, 120, 70), 0.9 * (1 - 0.6 * u))
    he = helm_on(t)
    if he > 0:
        for s_ in BP['_slits']: arr = glow(arr, R, vi, s_, 0.16, (255, 60, 40), 0.7 * he)
    return arr

# ======================= overlays =======================
def tw(s, sc): return font.width(s, sc)
def ctext(d, s, y, sc, col, o=4, x=None):
    x = int(540 - tw(s, sc) / 2) if x is None else x
    look.draw_cells(d, look.text_cells(s, x, y, sc, col), o)
TX = dict(boss='KOF KRAL' if TRL else 'THE HOLLOW KING', cov=('PATRONLAR', 'NEDEN KIRMIZI', 'PARLAR?') if TRL else ('WHY DO BOSSES', 'GLOW RED', 'BEFORE ATTACKS?'))
for _s in [TX['boss'], *TX['cov']]: font.check(_s)
WHT = (240, 236, 226)
HEART = ['0110110', '1111111', '1111111', '0111110', '0011100', '0001000']
def heart_hud(d, t):
    fast = t >= S_DARK and t < S_LOOP
    on = (int(t * (6 if fast else 2.5)) % 2 == 0) or t < 0.0
    col = (255, 60, 60) if on else (120, 30, 34); x0, y0, c = 60, 64, 14
    d.rectangle([x0 - 14, y0 - 14, x0 + 7 * c + 14, y0 + 6 * c + 14], fill=(8, 8, 14))
    for j, row in enumerate(HEART):
        for i, b in enumerate(row):
            if b == '1': d.rectangle([x0 + i * c, y0 + j * c, x0 + (i + 1) * c - 2, y0 + (j + 1) * c - 2], fill=col)
def boss_bar(d, t):
    if t < S_SIDE + 0.25 or t >= S_LOOP: return
    u = sm(seg01(t, S_SIDE + 0.25, S_SIDE + 0.6)); x0 = int(lerp(1080, 210, u))
    ctext(d, TX['boss'], 66, 5, (255, 214, 190), x=x0)
    x1, y0, y1 = x0 + 800, 116, 146
    d.rectangle([x0 - 6, y0 - 6, x1 + 6, y1 + 6], fill=(0, 0, 0)); d.rectangle([x0, y0, x1, y1], fill=(196, 36, 40)); d.rectangle([x0, y0, x1, y0 + 7], fill=(255, 140, 130))
def cover(d, t):
    if not (0 <= t < F(1.8)): return
    lines = TX['cov']; scs = [min(sc_, max(6, int(1000 / (len(l_) * 6 - 1)))) for l_, sc_ in zip(lines, (12, 15, 11))]
    y = 250; w = max(tw(s, sc) for s, sc in zip(lines, scs)); yy = y
    for i, (s, sc) in enumerate(zip(lines, scs)):
        if i == 1: d.rectangle([540 - w / 2 - 30, yy - 18, 540 + w / 2 + 30, yy + 7 * sc + 18], fill=(110, 16, 20))
        ctext(d, s, yy, sc, (255, 120, 90) if i == 1 else WHT, o=6); yy += 7 * sc + 30
COL = {'N': (242, 238, 226), 'K': (150, 200, 255), 'M': (255, 200, 140), 'H': (255, 110, 100)}
def _sub_scr():
    if not TRL: return SCR
    import importlib.util as _iu
    sp_ = _iu.spec_from_file_location('rg_tts', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'tts', 'rg.py'))
    m_ = _iu.module_from_spec(sp_); sp_.loader.exec_module(m_); TRS = m_.TR_SUB
    out = dict(SCR); sent = {}
    for k, v in SCR['sent'].items():
        if len(v) == len(TRS[k]): sent[k] = [[a, b, tx] for (a, b, _), tx in zip(v, TRS[k])]
        else: sent[k] = [[v[0][0], v[-1][1], ' '.join(TRS[k])]]
    out['sent'] = sent
    return out
SUBS = look.Subtitles(_sub_scr(), [x for x in LINES if x[0] != '00'], W, H, S, COL, title_key='none', n=17,
                      hil=({'KİMİN', 'YAKTIĞINI', 'USTA?', 'HAİN.', 'KANDIRIYOR.', 'KURTARIR'} if TRL else {'WHO', 'LIGHTS', 'MASTER?', 'TRAITOR.', 'FAKES', 'SAVE'}))
from nightkit import cta
CTA = cta.Achievement(t0=T0['08'] - 0.1, lang=SUB_LANG, dur=F(1.5), y=300)
def frame_final(t):
    if t >= DUR: t = t - DUR
    img, vi, R, poses, zb = frame_low(t); arr = post.upscale(img, S)
    arr = lights2d(arr, t, vi, R, poses)
    if T_CRUSH <= t < T_CRUSH + 0.12: arr = arr + (np.array([255, 80, 60], np.float32) - arr) * 0.25          # the crush flash
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    heart_hud(d, t); boss_bar(d, t); cover(d, t)
    arr = np.asarray(im).astype(np.float32)
    arr = SUBS.apply(arr, t); arr = CTA.apply(arr, t)
    return arr

TEST = os.environ.get('TEST') or os.environ.get('TESTF')
if TEST and __name__ == '__main__':
    k_ = 1.2 if os.environ.get('TESTF') else 1.0
    if TEST == 'seq': ts = sorted(set([round(a + (b - a) * f, 2) for i, (n_, a) in enumerate(CUTS) for b in [CUTS[i + 1][1] if i + 1 < len(CUTS) else DUR] for f in (0.1, 0.5, 0.9)]))
    else: ts = [round(float(x) * k_, 4) for x in TEST.split(',')]
    tw_ = int(os.environ.get('TW', '200')); th = tw_ * 16 // 9
    ims = [Image.fromarray(np.clip(frame_final(x), 0, 255).astype(np.uint8)) for x in ts]
    if os.environ.get('SZ') == 'full':
        for x, im in zip(ts, ims): im.save(f'test_rg_{x:.2f}.png')
    ims = [im.resize((tw_, th), Image.LANCZOS) for im in ims]
    per = int(os.environ.get('PER', '10')); rows = (len(ims) + per - 1) // per; shp = Image.new('RGB', (min(per, len(ims)) * (tw_ + 2), rows * (th + 18)), (30, 30, 30))
    dd = ImageDraw.Draw(shp)
    for i, (im, x) in enumerate(zip(ims, ts)): shp.paste(im, ((i % per) * (tw_ + 2), (i // per) * (th + 18))); dd.text(((i % per) * (tw_ + 2) + 4, (i // per) * (th + 18) + th + 3), f'{x:.2f} {x / 1.2:.1f}f {scene(x)}', fill=(255, 255, 0))
    shp.save(os.environ.get('TEST_OUT', 'test_rg.png')); print('test written', DUR, round(DUR / 1.2, 2), SEQS); sys.exit()

QA = dict(fps=FPS, dur=DUR, W=W, frame=lambda t: Image.fromarray(np.clip(frame_final(t), 0, 255).astype(np.uint8)).resize((W, H), Image.BOX), chars={},
          geom=lambda t, name, st, V_: [], camera=lambda t: cam_shot(t)[0], min_cam_dist=0.3, camera_ok=lambda p: True, allow_jump=[], weapon_events=[],
          scenes=[dict(id=nm, t0=a, t1=(CUTS[i + 1][1] if i + 1 < len(CUTS) else DUR), action=nm) for i, (nm, a) in enumerate(CUTS)],
          texts=lambda: [('hud', s, 10) for s in TX['cov']] + [('hud', TX['boss'], 5)])

# ======================= asset previews =======================
ASSET = os.environ.get('ASSET')
def _asset_shot(layers, cp, tg, fv, L=None, amb=0.35):
    R = Renderer(W, H, fog=(14, 16, 26)); cam = Camera.look(tuple(cp), tuple(tg))
    L = L or [((1.5, 3.0, -3.0), (200, 210, 255), 2.2), ((-2.5, 1.5, 1.0), (150, 170, 230), 0.8)]
    img, vi, zb = zrender(R, cam, layers, L, fov=fv, fog_start=10, fog_end=60, ambient=amb, return_z=True)
    a = look.outline(np.asarray(img).astype(np.float32), zb)
    return post.ps1(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), levels=6)
if ASSET and __name__ == '__main__':
    floor = hd.bx((0, -0.05, 0), np.eye(3), (12, 0.05, 12), (70, 64, 58)); ims = []
    if ASSET in ('boss', 'cast'):
        P = dict(base=(0, 0, 0), yaw=0.0, eyes='half', brow=-0.6, mouth='neutral', lh_w=(0.12, 1.95, 0.62), rh_w=(-0.02, 2.05, 0.6), rpalm_local=False, lpalm_local=False,
                 rpalm=(-1.0, 0, 0), lpalm=(1.0, 0, 0), rgrip=0.9, lgrip=0.9)
        QB = boss(P); cf, Rc, nrm = P['_crys']
        MP, em = master_pose(0.3); QM = master(MP, cf - nrm * (CR_DEPTH * 0.45), fit_frame(nrm, P['_RW'] @ V((0, 1.0, 0))))
        Qs = greatsword(V((0.05, 2.0, 0.62)), (0, -1.0, 0.0), (0, 0, 1.0))
        QK = []
        if ASSET == 'cast':
            KP = dict(base=(-1.6, 0, 1.2), yaw=PI / 2 + 0.4, eyes='open', mouth='neutral', rh=(0.3, 1.3, 0.38), rgrip=0.8, lh=(-0.25, 1.0, 0.2), lgrip=0.9)
            QK = knight(KP); KP['_shield'] = knight_shield(KP); QK = knight(KP)
        for cp, tg, fv in (((0.6, 1.5, 5.2), (0, 1.5, 0), 46), ((0.25, 1.95, 1.05), (0, 1.9, 0.3), 30), ((0.3, 2.45, 1.3), (0, 2.45, 0), 34), ((-1.2, 0.8, 4.6), (-0.3, 1.6, 0.5), 48)):
            ims.append(_asset_shot([FB.ARENA if False else floor, QB, QM, Qs, QK], cp, tg, fv, L=[((0.2, 2.2, 1.6), (255, 70, 40), 1.2), ((2.0, 4.0, 3.0), (170, 190, 255), 1.8), ((-3, 2, -2), (120, 130, 200), 0.8)]))
    elif ASSET == 'master':
        MP, em = master_pose(0.3); QM = master(MP, V((0, 1.0, 0)), np.eye(3))
        for cp, tg, fv in (((0.0, 1.03, 0.6), (0, 1.0, 0), 30), ((0.25, 1.05, 0.45), (0, 1.0, 0), 30)):
            ims.append(_asset_shot([floor, QM], cp, tg, fv))
    elif ASSET == 'shield':
        KP = dict(base=(0, 0, 0), yaw=0.0, eyes='open', mouth='neutral', rh=(0.02, 1.3, 0.4), rpalm=(0.0, 0.0, -1.0), rgrip=0.8, lh=(-0.25, 1.0, 0.2), lgrip=0.9)
        QK = knight(KP); KP['_shield'] = knight_shield(KP); QK = knight(KP)
        for cp, tg, fv in (((1.2, 1.4, 2.6), (0.1, 1.2, 0), 40), ((2.6, 1.3, 0.6), (0.1, 1.2, 0), 40)):
            ims.append(_asset_shot([floor, QK], cp, tg, fv))
    out = Image.new('RGB', (W * S * len(ims) // 2, H * S // 2))
    for i, im in enumerate(ims): out.paste(im.resize((W * S // 2, H * S // 2), Image.NEAREST), (i * W * S // 2, 0))
    out.save(f'test_rg_{ASSET}.png'); print('written'); sys.exit()

# ======================= AUDIO =======================
def _comb(x, sr, ms, fb, n_=4):
    """a short feedback comb (glass / metal ring)"""
    d = int(sr * ms / 1000); y = x.copy()
    for k in range(1, n_ + 1):
        if d * k < len(x): y[d * k:] += x[:-d * k] * (fb ** k)
    return y
def voice_fx(a, sr, key, s):
    if key in ('02', '04', '06'):                                              # the master inside the crystal: small, glassy
        y = s.filt_short(a, lo=280, hi=3800); y = _comb(y, sr, 5.5, 0.38); return y * 0.9
    if key == '09':                                                            # ... inside the helmet: metal ring
        y = s.filt_short(a, lo=240, hi=3200); y = _comb(y, sr, 3.2, 0.5, 6); return y * 0.9
    if key == '05':                                                            # the boss: an empty helmet speaks
        y = a + 0.6 * s.filt_short(a, hi=400); y = _comb(y, sr, 11.0, 0.45, 5); return y * 0.8
    return a
def build_audio(path):
    import soundfile as _sf
    from nightkit.audio import soft_fire
    s = Sound(DUR, loop=False, seed=91); sr = s.sr; n = s.n; t = s.t
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
    def thud(t0, f=60, v=0.1, d=0.3, buf=None): tt = s.T(d); put(FX if buf is None else buf, np.sin(2 * np.pi * f * tt * (1 - 0.3 * tt / d)) * np.exp(-tt * 9), t0, v)
    def whoosh(t0, d, v, seed, lo=300, hi=2600): tt = s.T(d); put(FX, s.filt_short(s.noise(d, seed), lo=lo, hi=hi) * np.sin(np.pi * tt / d) ** 1.5 * (tt / d), t0, v)
    def mask(a, b, r=0.15): return np.clip(np.minimum((t - a) / r, (b - t) / r), 0, 1)
    # bed: cold hall air + a low drone, far torch fire
    BED += s.filt(s.rng.normal(0, 1, n), lo=70, hi=500) * 0.022 * (0.8 + 0.2 * np.sin(2 * np.pi * 0.21 * t))
    MUS += (np.sin(2 * np.pi * 46.25 * t) + 0.5 * np.sin(2 * np.pi * 69.3 * t + 0.4 * np.sin(2 * np.pi * 0.25 * t))) * 0.012
    BED += soft_fire(s, level=0.006, crackles_per_s=3.0, seed=7)[:n]
    # war drum: tightens with each attack; CUT for the wordless beat; back at the helmet glow + the loop
    x = 0.0; k = 0
    while x < S_LOOKD:
        thud(x, 58, 0.16, 0.5, buf=MUS); nb(x, 0.08, 80, 400, 0.05, 300 + k, 1, buf=MUS)
        if k % 2 == 1: thud(x + 0.18, 70, 0.08, 0.3, buf=MUS)
        x += max(0.42, 0.75 - 0.012 * k); k += 1
    x = T_SLITS; k = 0
    while x < DUR - 0.05:
        thud(x, 58, 0.18, 0.5, buf=MUS); nb(x, 0.08, 80, 400, 0.05, 400 + k, 1, buf=MUS)
        if k % 2 == 1: thud(x + 0.18, 70, 0.09, 0.3, buf=MUS)
        x += 0.5; k += 1
    # the thin high string in the dark (no glow, no warning)
    st = (np.sin(2 * np.pi * 880 * t) + 0.4 * np.sin(2 * np.pi * 1318.5 * t)) * (0.75 + 0.25 * np.sin(2 * np.pi * 5.5 * t))
    MUS += st * 0.0045 * mask(S_DARK, T_SLITS, 0.5)
    # the glow: a glassy hum + a breath "whoo" on each puff while the crystal lives; muffled again in the helmet
    gl = np.interp(t, t[::480], np.array([glow_on(x_) if crystal_state(x_) != 'gone' else 0.0 for x_ in t[::480]]))
    hm = np.interp(t, t[::480], np.array([helm_on(x_) for x_ in t[::480]]))
    hum = (np.sin(2 * np.pi * 392 * t) + 0.6 * np.sin(2 * np.pi * 587.3 * t + 0.3 * np.sin(2 * np.pi * 0.6 * t)) + 0.3 * np.sin(2 * np.pi * 784 * t))
    BED += hum * 0.004 * gl + s.filt(hum, hi=900) * 0.004 * hm
    for x_ in np.arange(0.25, T_RIP[0], 2 * PI / 6.3): nb(x_, 0.35, 500, 3000, 0.012, int(x_ * 77), 2)
    # frame 1: the shield clears, the dive, the lift, the SLAM (stone crack, debris, the blade rings)
    whoosh(0.0, 0.4, 0.05, 11); whoosh(T_DIVE[0], 0.5, 0.07, 12); thud(T_DIVE[1], 140, 0.06, 0.15); nb(T_DIVE[1], 0.12, 1500, 6000, 0.02, 13, 1)
    whoosh(T_LIFT[0], 0.8, 0.05, 14, 150, 1500)
    thud(T_SLAM, 38, 0.4, 1.1); nb(T_SLAM, 0.5, 60, 700, 0.15, 15, 1); nb(T_SLAM, 0.25, 1500, 7000, 0.05, 16, 1)
    for k_ in range(9): nb(T_SLAM + 0.08 + 0.09 * k_ + 0.03 * hsh(k_, 2), 0.05, 1500, 6000, 0.02 * (1 - k_ / 9), 20 + k_, 1)
    tone(T_SLAM, 64, 0.8, 0.02, dec=5, harm=(1.0, 0.5, 0.3, 0.2))
    # "Left! Now!": the low dive + the sweep passing just over him
    whoosh(T_DIVE2[0], 0.5, 0.07, 31); thud(T_DIVE2[1], 140, 0.06, 0.15)
    whoosh(T_SWEEP[0], T_SWEEP[1] - T_SWEEP[0] + 0.2, 0.11, 32, 200, 2200); tone(T_SWEEP[0] + 0.2, 76, 0.5, 0.012, dec=4, glide=-0.1)
    # the wordless beat: music + drum out, a heartbeat; the helmet scrapes as it turns
    hb = S_LOOKD + 0.1; k_ = 0
    while hb < T_RIP[0]:
        thud(hb, 52, 0.12, 0.25); thud(hb + 0.18, 48, 0.08, 0.2); hb += max(0.5, 0.8 - 0.05 * k_); k_ += 1
    nb(T_FOLLOW[0], 0.6, 1200, 4000, 0.008, 41, 2); nb(T_TILT[0], 0.8, 900, 3500, 0.01, 42, 2)
    MUS *= 1 - 0.85 * mask(S_LOOKD, S_DARK, 0.2)
    # the rip: metal shriek; the crush: glass crack + crunch, shards, the red hum chokes off; near-silence
    tt2 = s.T(0.35); put(FX, np.sin(2 * np.pi * (2400 - 1400 * tt2 / 0.35) * tt2) * 0.02 * np.sin(np.pi * tt2 / 0.35), T_RIP[0])
    nb(T_RIP[0], 0.3, 2000, 7000, 0.05, 51, 1); thud(T_RIP[0], 90, 0.08, 0.2)
    nb(T_CRUSH, 0.12, 2500, 9000, 0.12, 52, 0.5); nb(T_CRUSH + 0.03, 0.25, 300, 2500, 0.08, 53, 1); thud(T_CRUSH, 70, 0.12, 0.3)
    for k_ in range(10): tone(T_CRUSH + 0.05 + 0.07 * k_ + 0.03 * hsh(k_, 5), 96 + int(6 * hsh(k_, 6)), 0.12, 0.012 * (1 - k_ / 12), dec=18)
    for k_ in range(3): tone(T_SPARK[0] + 0.2 + 0.18 * k_, 100 + k_, 0.08, 0.004, dec=25)
    BED *= 1 - 0.8 * mask(T_CRUSH + 0.15, T_CRUSH + 0.6, 0.08)
    # the head fake: a huge windup whoosh that stops dead; the dive; an iron laugh (four low metallic huffs)
    whoosh(T_WIND[0], T_WIND[1] - T_WIND[0], 0.09, 61, 150, 1800); whoosh(T_DIVE3[0], 0.5, 0.07, 62); thud(T_DIVE3[1], 140, 0.06, 0.15)
    for k_ in range(4):
        tt3 = s.T(0.18); y_ = s.filt_short(s.noise(0.18, 70 + k_), lo=90, hi=500) * np.exp(-tt3 * 12)
        put(FX, _comb(y_, sr, 11.0, 0.45, 4), T_LAUGH + 0.22 * k_, 0.12)
    # the real strike: a heavy step, the sword rising; the slits flare (boom + a red sting); the shield whoosh into the loop
    thud(S_HELM + 0.1, 40, 0.25, 0.8); nb(S_HELM + 0.1, 0.3, 80, 500, 0.06, 81, 1); whoosh(S_HELM + 0.2, 1.0, 0.05, 82, 150, 1500)
    thud(T_SLITS, 34, 0.3, 1.2); tone(T_SLITS, 50, 1.6, 0.03, dec=1.5, harm=(1.0, 0.6, 0.4, 0.3)); tone(T_SLITS + 0.02, 74, 0.9, 0.012, dec=3)
    whoosh(T_COVER[0] - 0.3, 0.85, 0.08, 91)
    tone(0.0, 79, 0.5, 0.012, dec=8, harm=(1.0, 0.5, 0.3)); thud(0.0, 120, 0.05, 0.15)
    if CTA.on: put(FX, cta.chime(sr), CTA.t0, 1.0)
    # voice (with the speaker FX)
    NB = np.zeros(n); wins = []
    for k_, t0 in LINES:
        f_ = os.path.join(TTS_DIR, 'rg', f'{k_}.wav')
        if not os.path.exists(f_): continue
        a, ar = _sf.read(f_); a = a if a.ndim == 1 else a.mean(1)
        a = np.interp(np.arange(int(len(a) * sr / ar)) / sr, np.arange(len(a)) / ar, a)
        a = voice_fx(a, sr, k_, s); act = np.abs(a) > 0.02 * np.abs(a).max()
        a = a * (0.12 / np.sqrt((a[act] ** 2).mean())); put(NB, a, t0); wins.append((t0, t0 + len(a) / sr))
    gd = duck_envelope(n, sr, wins, -8.0, 0.05, 0.25) if wins else np.ones(n)
    bed = BED * gd + MUS * (0.55 + 0.45 * gd); fx = FX * (0.7 + 0.3 * gd)
    L = bed + fx; R_ = np.roll(bed, 700) + np.roll(fx, 200)
    pk = max(np.abs(L).max(), np.abs(R_).max()); gv = (pk * 1.6 / np.abs(NB).max()) if np.abs(NB).max() > 0 else 0.0
    s.L = L + NB * gv; s.R = R_ + NB * gv; s.reverb(0.25, length=2.4, decay=3.0)
    fi = np.clip(t / 0.008, 0, 1); s.L = s.L * fi; s.R = s.R * fi
    return s.save(path, peak=0.9)
if __name__ == '__main__' and os.environ.get('PART') == 'audio':
    print(build_audio(os.path.join(OUT, os.environ.get('AUDIO_NAME', 'red_glow.wav')))); sys.exit()
if __name__ == '__main__' and os.environ.get('PART'):
    a, b = map(int, os.environ['PART'].split(':'))
    import subprocess
    p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W * S}x{H * S}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', os.path.join(OUT, f"{os.environ.get('PART_PREFIX', 'rg')}_{a:05d}.mp4")], stdin=subprocess.PIPE)
    vhs = post.VHS(W * S, H * S, S, grade='none', chroma=0, scan_dark=1.0, vignette=0.4, grain=1.4, band_period=1e9)
    for f in range(a, min(b, N)): p.stdin.write(vhs(frame_final(f / FPS), f, f / FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done', a, b); sys.exit()
