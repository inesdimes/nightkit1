"""WHY DOES THE FINAL BOSS HAVE A HELP WANTED SIGN? (Insert Disc 2, 25 Nov 2026) 48 s build -> x1.2 = 40.0 s final, 9:16, nightkit HD.
Brief: briefs/FINAL_BOSS_HELP_WANTED_FULL_BRIEF.txt (GPT). Enes (25 Nov): rebuild the final boss as an HD figure, NO voice in this render
(he records the 15 lines afterwards), render everything without stopping.
Timeline: every beat is written in FINAL seconds (the brief's table) and converted with F() = x1.2 build seconds.
Voices: tts/bw/script.json holds PLANNED durations (tools/tts/bw.py plan) until Enes's takes arrive; voice wavs are mixed in when present.
Story: the boss holds up a HELP WANTED sign instead of fighting; FIGHTS: 9999 (planted); he hands over sword + contract; the knight signs;
wordless beat = the boss lets his sword drop, the knight's eyes follow it; the old boss leaves smiling, the knight takes the spot and raises
the same sign as an identical knight charges in -> last frame = frame 0 (camera, charge position, run phase, music phase).

Asset preview: ASSET=boss|sign|cast python examples/boss_wanted.py -> test_bw_<asset>.png
Frames:        TEST=0,1.5,... python examples/boss_wanted.py -> test_bw.png   (times are BUILD seconds; TESTF=... takes final seconds)
Render:        python tools/render_parts.py examples/boss_wanted.py --prefix bw --audio boss_wanted.wav --out ../renders/boss_wanted/bw_1x.mp4
Master x1.2:   sh tools/speedup_raw.sh out/bw_video.mp4 out/boss_wanted.wav <final.mp4> 40.0"""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import numpy as np
from PIL import Image, ImageDraw
from nightkit.engine import Renderer, Camera
from nightkit.zraster import zrender
from nightkit import post, look, hd, motion, font
import dragon_taxes as dtx                      # locked: the series knight (HD, open helmet, blue cape + plume)
import final_boss as FB                         # locked: the boss arena (checker floor, stone walls, pillars, throne, gate + corridor), torches

W, H, S = 270, 480, 4
PI = math.pi
V = np.array
FPS = 24
hsh, lerp, lerp3, mixc = dtx.hsh, dtx.lerp, dtx.lerp3, dtx.mixc
sm = motion.smooth
def seg01(t, a, b): return max(0.0, min(1.0, (t - a) / (b - a))) if b > a else (1.0 if t >= b else 0.0)
def win(t, a, b, r=0.25): return sm(seg01(t, a, a + r)) * (1 - sm(seg01(t, b - r, b)))
def F(x): return round(x * 1.2, 4)                  # final seconds -> build seconds
def nz(v): v = V(v, float); n = np.linalg.norm(v); return v / n if n > 1e-9 else v
SUB_LANG = os.environ.get('SUB_LANG', 'en')
TRL = SUB_LANG == 'tr'

# ======================= timeline =======================
TTS_DIR = os.environ.get('TTS_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tts'))
SCR = json.load(open(os.path.join(TTS_DIR, 'bw', 'script.json')))
KEYS = ['%02d' % i for i in range(1, 16)]
SLOT = {k: F(x) for k, x in zip(KEYS, (0.05, 3.0, 5.15, 8.05, 11.05, 14.05, 18.05, 20.1, 23.05, 27.1, 30.1, 32.05, 35.25, 36.1, 37.95))}
def _lines():
    out = []; prev = -1.0
    for k in KEYS: t0 = max(SLOT[k], prev + 0.2); out.append((k, round(t0, 3))); prev = t0 + SCR['dur'][k]
    return out
LINES = _lines(); T0 = dict(LINES)
def tend(k): return T0[k] + SCR['dur'][k]
DUR = round(max(F(40.0), tend('15') + 0.25), 3); N = int(round(DUR * FPS))
TEND = DUR                                          # loop point (= frame 0)
CUTS = [('open', 0.0), ('two', F(3.0)), ('ots', F(5.0)), ('counter', F(8.0)), ('sweep', F(11.0)), ('offer', F(14.0)), ('kmcu', F(18.0)),
        ('benefit', F(20.0)), ('signed', F(23.0)), ('nobreak', F(27.0)), ('drop', F(29.0)), ('exit', F(30.0)), ('enter', F(32.0)),
        ('snap', F(35.0)), ('approach', F(36.0)), ('loop', F(38.0))]
def scene(t):
    cur = 'open'
    for nm, a in CUTS:
        if t >= a: cur = nm
    return cur
T_PLANT = (F(3.05), F(3.75))        # the boss plants the sign beside him
T_DROP = F(29.2)                    # wordless beat: he lets the sword go
T_EXIT = F(30.15)                   # the old boss turns and walks out
T_ROLE = F(30.8)                    # boss bar FINAL BOSS -> KNIGHT, red light flicker
T_GRAB = (F(35.0), F(35.25), F(35.65))     # the new boss takes the sign: reach, grab, snapped up
def talking(t, key):
    if key not in T0: return None
    for a, b, _ in SCR['sent'][key]:
        if T0[key] + a <= t < T0[key] + b: return 'open' if (t * 7.3 + 0.2 * math.sin(t * 13)) % 1.0 < 0.55 else None
    return None

# ======================= cast =======================
BOSS_H = 2.3
BOSS = hd.spec(h=BOSS_H, build=1.22, skin=(132, 116, 138), hair=(120, 104, 126), hair_style='bald', eye=(232, 70, 54), brow=(34, 26, 36),
               lip=(84, 56, 76), tunic=(34, 28, 40), tunic2=(26, 22, 32), skirt=0.5, pants=(30, 26, 36), boots=(22, 18, 26),
               belt=(92, 28, 34), buckle=(214, 190, 120), gloves=(40, 32, 46), cloak=(78, 34, 74), cloak_len=1.12, collar=(120, 34, 40))
PLUM = (78, 34, 74); PLUM_D = (58, 24, 56); BLK = (30, 26, 36); MRED = (136, 36, 42); PGOLD = (214, 190, 120); HORN = (186, 172, 150); HORN_D = (140, 128, 110)
def boss(P):
    """HD final boss: 2.3 m HD human (near-black armour, plum cloak) + horned pale-gold crown (no hood: the eyes stay visible),
    spiked plum pauldrons, a chest plate with a red gem, a high red collar and long cloak"""
    Q = hd.human(BOSS, P); RW = P['_RW']; ch = P['_chest']; RH = P['_RH']; hc = P['_head']; k = BOSS_H / 1.78; bw = BOSS['build']
    for sd in (1, -1):                                                                      # pauldrons with a spike
        c = ch + RW @ V((sd * 0.2 * bw, 0.07 * k, -0.01))
        Q += hd.ellip(c, RW @ hd.Rz(-sd * 0.3), (0.12 * bw, 0.085, 0.12), 10, 5, PLUM, v1=PI * 0.6, colfn=lambda i, j, cl: PLUM_D if i == 2 else PLUM)
        Q += hd.ellip(c + RW @ V((sd * 0.02, -0.02, 0)), RW @ hd.Rz(-sd * 0.3), (0.125 * bw, 0.03, 0.125), 10, 2, PGOLD, v0=PI * 0.5, v1=PI * 0.62)
        Q += hd.limb(c + RW @ V((sd * 0.04, 0.05, 0)), c + RW @ V((sd * 0.13, 0.2, -0.02)), 0.035, 0.004, HORN_D, n=6, m=1)
    Q += hd.ellip(ch + RW @ V((0, -0.03, 0.04)), RW, (0.19 * bw, 0.19, 0.11 * bw), 12, 6, BLK, keep=lambda c: c[2] > 0.0,
                  colfn=lambda i, j, cl: (52, 44, 58) if (j % 6 == 0) else BLK)
    Q += hd.decal(ch + RW @ V((0, 0.0, 0.11 * bw + 0.045)), RW @ V((0, 0, 1.0)), RW @ V((0, 1.0, 0)), 0.035, 0.05, (220, 40, 46), emit=True, lift=0.004)
    # horned crown: a pale-gold band ABOVE the brows + two curved horns sweeping back and up
    rx, ry, rz = 0.09 * k, 0.116 * k, 0.103 * k
    def L(x, y, z): return hc + RH @ V((x, y, z))
    Q += hd.limb(L(0, 0.062 * k, -0.006 * k), L(0, 0.082 * k, -0.01 * k), rz * 1.0, rz * 0.96, PGOLD, n=16, m=1, ref=RH @ V((0, 0, 1.0)), flat=0.9)
    for a in (-0.9, -0.45, 0.0, 0.45, 0.9):                                                 # crown points
        p = L(rx * 1.0 * math.sin(a), 0.082 * k, rz * 0.98 * math.cos(a)); Q += hd.limb(p, p + RH @ V((0, 0.035 * k, 0)), 0.012 * k, 0.002, PGOLD, n=4, m=1)
    Q += hd.bx(L(0, 0.072 * k, rz * 1.0), RH, (0.012 * k, 0.012 * k, 0.006), (220, 40, 46), emit=True)
    for sd in (1, -1):
        pts = [L(sd * rx * 0.85, 0.06 * k, -0.01 * k), L(sd * rx * 1.35, 0.1 * k, -0.04 * k), L(sd * rx * 1.6, 0.17 * k, -0.08 * k), L(sd * rx * 1.5, 0.25 * k, -0.11 * k)]
        rr = [0.03 * k, 0.024 * k, 0.016 * k, 0.004]
        for i in range(3): Q += hd.limb(pts[i], pts[i + 1], rr[i], rr[i + 1], HORN if i % 2 == 0 else HORN_D, n=7, m=1)
    return [q for q in Q if q]

def knight(P): return dtx.knight(P)
def grip_pt(P, key, off=0.075, lift=0.03): return P['_' + key + 'wrist'] + P['_' + key + 'dir'] * off + P['_' + key + 'palm'] * lift

# ======================= the HELP WANTED sign (pole + painted board) =======================
POLE_L = 2.4; BOARD = (1.0, 0.62); SIGN_GRIP = 0.8
WOOD = (122, 86, 54); WOOD_D = (92, 62, 38); PAPER = (226, 210, 168); INK = (150, 30, 30)
SIGN_TXT = ('ELEMAN', 'ARANIYOR') if TRL else ('HELP', 'WANTED')
def _txt_cells(s):
    out = []
    for k_, ch in enumerate(s):
        for j, row in enumerate(font.FONT[ch]):
            for i, b in enumerate(row):
                if b == '1': out.append((k_ * 6 + i, j))
    return out, len(s) * 6 - 1
def sign(bot, up, fwd):
    """bot = pole foot (world), up = pole direction, fwd = the painted face's normal. Text on both faces."""
    bot = V(bot, float); up = nz(up); fwd = nz(V(fwd, float) - up * float(V(fwd, float) @ up)); side = np.cross(up, fwd); Q = []
    top = bot + up * POLE_L
    Q += hd.limb(bot, top, 0.028, 0.026, WOOD, n=6, m=2, ref=fwd)
    bc = bot + up * (POLE_L - BOARD[1] / 2 - 0.04)
    R = np.column_stack([side, up, fwd])
    Q += hd.bx(bc, R, (BOARD[0] / 2 + 0.03, BOARD[1] / 2 + 0.03, 0.018), WOOD_D)
    Q += hd.bx(bc, R, (BOARD[0] / 2, BOARD[1] / 2, 0.026), PAPER)
    l1, w1 = _txt_cells(SIGN_TXT[0]); l2, w2 = _txt_cells(SIGN_TXT[1]); cw = min(0.9 / max(w1, w2), 0.03)
    for face_n in (1, -1):
        for cells, wd, row in ((l1, w1, 0), (l2, w2, 1)):
            y0 = bc + up * ((0.5 - row) * 10.5 * cw + 3.5 * cw)
            for (cx, cy) in cells:
                xx = -(cx - wd / 2 + 0.5) * cw * face_n
                c = y0 + side * xx - up * cy * cw + fwd * face_n * 0.027
                Q += hd.decal(c, fwd * face_n, up, cw * 1.04, cw * 1.04, INK, lift=0.002)
    return [q for q in Q if q]

# ======================= positions =======================
B0 = (0.0, 0.0, 11.5); BYAW = PI                    # the boss faces -z (towards the gate)
KST = (-0.9, 0.0, 9.55)                             # where the charging knight stops (left of the boss in the opening frame)
KYAW = math.atan2(-KST[0], 11.5 - KST[2])           # standing knight faces the boss
K_NEW = (0.2, 0.0, 11.55)                           # the knight's spot as the new boss
S_PLANT = (0.55, 0.0, 11.95)                        # the planted sign, behind the boss's left shoulder
RUN0 = 8.4                                         # the charger's z at frame 0 (and at the loop point)
EXIT_PTS = [(0.0, 0.0, 11.5), (1.5, 0.0, 10.4), (1.45, 0.0, -2.0)]
def bl(p): return V(B0, float) + hd.Ry(BYAW) @ V(p, float)            # boss-local -> world
def ang_to(p, q): return math.atan2(q[0] - p[0], q[2] - p[2])

# ======================= poses =======================
def run_phase(z): return z * 2 * PI / 1.55
LANE = [(-20.0, -0.3), (1.6, -0.3), (RUN0, -1.17), (KST[2], KST[0]), (20.0, KST[0] + (20 - KST[2]) * 0.23)]
def lane_x(z): return float(np.interp(z, [a for a, _ in LANE], [b for _, b in LANE]))
def lane_yaw(z): return math.atan2(lane_x(z + 0.05) - lane_x(z - 0.05), 0.1)
def charger(z, t, stop=0.0):
    """the charging knight at depth z on the lane: sword raised behind the head; stop 0..1 = the swing that halts short of the sign"""
    P = dict(base=(lane_x(z), 0.0, z), yaw=lerp(lane_yaw(z), KYAW, stop), eyes='wide', mouth='grit', brow=0.8, lean=0.22 * (1 - stop), cape_sway=0.5 * (1 - stop) + 0.15 * math.sin(t * 1.3))
    run = 1 - stop
    if run > 0.02: P['walk'] = run_phase(z); P['stride'] = 0.36 * run; P['lift'] = 0.14 * run
    P['rh'] = lerp3((0.14, 2.02, -0.02), (0.24, 1.85, 0.3), sm(stop)); P['rgrip'] = 0.9; P['rpalm'] = (-1.0, 0, 0.0)
    P['lh'] = lerp3((-0.24, 1.15, 0.28), (-0.22, 1.12, 0.2), stop); P['lgrip'] = 0.6
    P['head'] = (0.0, 0.18, 0.0)
    return P
GUARD = (0.55, 1.7, 0.9)                            # blade towards the raised sign (it stops ~0.9 m short of it)
def charger_blade(t, stop):
    """sword direction for the charge: back over the shoulder while running, forward-up when the swing stops"""
    return nz(lerp3((0.05, 0.75, -0.65), GUARD, sm(stop)))
def k_run_z(t):
    """the opening charge (t < 1.4) - decelerates from RUN0 to the stop"""
    u = seg01(t, 0.0, F(0.8)); return KST[2] - (KST[2] - RUN0) * (1 - u) ** 2
CH_PATH = look.Path([(F(31.5), -14.2), (F(32.0), -13.2), (F(36.0), -4.4), (F(38.0), 1.6), (TEND, RUN0), (TEND + F(0.8), KST[2])])
def challenger_z(t): return CH_PATH(t)

def boss_pose(t):
    P = dict(base=B0, yaw=BYAW, eyes='half', mouth='neutral', brow=-0.6, lean=0.03, cape_sway=0.12 * math.sin(t * 1.1), look=(0.0, -0.3))
    P['head'] = (0.35, -0.12, 0.0)
    # left hand (sign hand): raised sign -> planted -> gestures; right hand: the sword
    up_raise = (-0.5, 1.42, 0.46); low = (-0.36, 0.85, 0.2)
    u0 = 0.72 + 0.28 * sm(seg01(t, 0.0, F(0.3)))                      # frame 0: the sign is already 70 % up ("snaps up")
    lh = lerp3(low, up_raise, u0); lgrip = 0.9; lpalm = (1.0, 0, 0.0)
    pl = sm(seg01(t, T_PLANT[0], T_PLANT[1]))
    plant_h = wld(S_PLANT) + V((0.0, SIGN_GRIP + 0.02, 0.0)) + V((0.06, 0, -0.03))
    if pl > 0: lh = lerp3(lh, tuple(plant_h), pl)
    rel = sm(seg01(t, T_PLANT[1], T_PLANT[1] + 0.35))
    gest = (-0.4, 1.25, 0.52)                                         # palm up towards the contract UI
    point_up = (-0.32, 2.35, 0.32)                                    # pointing up at the HUD bar
    if rel > 0:
        lh = lerp3(lh, gest, sm(seg01(t, T_PLANT[1] + 0.1, T_PLANT[1] + 0.7))); lgrip = lerp(0.9, 0.3, rel); lpalm = lerp3((1.0, 0, 0), (0.2, 1.0, 0.3), rel)
        dn = sm(seg01(t, F(5.0), F(5.6))); lh = lerp3(lh, (-0.3, 1.05, 0.15), dn); lpalm = lerp3(lpalm, (1.0, 0, 0.2), dn)
    a = sm(seg01(t, F(8.0), F(8.5))) * (1 - sm(seg01(t, F(10.6), F(11.1))))           # 0:08 points at the counter
    if a > 0: lh = lerp3(lh, point_up, a); lgrip = lerp(lgrip, 0.65, a); lpalm = lerp3(lpalm, (1.0, 0, 0.0), a)
    sw = seg01(t, F(11.1), F(12.6))                                    # 0:11 sweeps one arm around the arena
    if 0 < sw < 1 or (F(11.1) <= t < F(12.9)):
        ang = lerp(0.2, -1.6, sm(sw)); r = 0.62; aw = win(t, F(11.0), F(12.9), F(0.35))
        lh = lerp3(lh, (-r * math.cos(ang) * 1.0 - 0.1, 1.65, 0.12 + r * math.sin(-ang) * 0.0 + 0.45 * math.cos(ang) * 0.9), aw); lgrip = lerp(lgrip, 0.25, aw)
        lpalm = lerp3(lpalm, (0.0, -1.0, 0.0), aw)
    slump = sm(seg01(t, F(12.7), F(13.5))) * (1 - sm(seg01(t, F(14.0), F(14.5))))     # ... then the shoulders drop
    P['lean'] += 0.16 * slump; P['head'] = (0.35, -0.12 - 0.25 * slump, 0.0)
    cg = win(t, F(15.6), F(17.6), F(0.4))                             # indicates the contract
    if cg > 0: lh = lerp3(lh, gest, cg); lpalm = lerp3(lpalm, (0.2, 1.0, 0.3), cg); lgrip = lerp(lgrip, 0.3, cg)
    tp = win(t, F(20.2), F(21.3), F(0.3)); me = win(t, F(21.3), F(22.8), F(0.3))        # taps the bar (points up), then himself
    if tp > 0: lh = lerp3(lh, point_up, tp); lgrip = lerp(lgrip, 0.65, tp); lpalm = lerp3(lpalm, (1.0, 0, 0), tp)
    if me > 0: lh = lerp3(lh, (-0.16, 1.62, 0.44), me); lgrip = lerp(lgrip, 0.7, me); lpalm = lerp3(lpalm, (0.6, 0.0, -0.8), me)
    nb = win(t, F(27.05), F(28.9), F(0.3))                           # "No breaks": palm up to the side + a small shrug
    if nb > 0:
        lh = lerp3(lh, (-0.5, 1.3, 0.38), nb); lpalm = lerp3(lpalm, (0.0, 1.0, 0.2), nb); lgrip = lerp(lgrip, 0.25, nb)
        sh = win(t, F(27.9), F(28.5), F(0.2)); P['head'] = (0.3, -0.08, 0.18 * sh); P['pel'] = (0, 0.03 * sh, 0)
    P['lh'] = lh; P['lgrip'] = lgrip; P['lpalm'] = lpalm
    # right hand: the sword at his side -> offered towards the knight (0:14) -> back -> let go (0:29)
    rh_side = (0.36, 1.08, 0.2); rh_off = (0.3, 1.42, 0.68)
    of = win(t, F(14.15), F(17.6), F(0.5))
    rh = lerp3(rh_side, rh_off, of)
    lw = sm(seg01(t, F(12.8), F(13.5))) * (1 - sm(seg01(t, F(14.0), F(14.4))))       # "lowers his weapon"
    rh = lerp3(rh, (0.37, 0.95, 0.14), lw)
    P['rh'] = rh; P['rgrip'] = 0.9 if t < T_DROP else lerp(0.9, 0.2, seg01(t, T_DROP, T_DROP + 0.15)); P['rpalm'] = (-1.0, 0, 0.1)
    # face: tired; looks at the knight; at the drop he looks down at the sword; then a smile
    if t >= T_DROP - 0.1:
        P['head'] = (0.25, -0.4, 0.0); P['look'] = (0.4, -1.0)
    mt = None
    for k_ in ('02', '05', '08', '10'):
        mt = mt or talking(t, k_)
    if mt: P['mouth'] = mt
    if T0['05'] <= t < tend('05') + 0.3: P['eyes'] = 'half'; P['brow'] = -0.75
    # exit: turns and walks out (smiling)
    if t >= T_EXIT:
        P['eyes'] = 'open'; P['brow'] = -0.2; P['mouth'] = 'smile'; P['look'] = (0.0, 0.0); P['head'] = (0.0, 0.05, 0.0)
        P['lh'] = None; P['rh'] = None; P['lgrip'] = 0.4; P['rgrip'] = 0.4
        for k_ in ('lh', 'rh'): P.pop(k_, None)
        d0 = math.dist(EXIT_PTS[0], EXIT_PTS[1]); d1 = math.dist(EXIT_PTS[1], EXIT_PTS[2]); sp = 1.3
        s = max(0.0, (t - T_EXIT - 0.35) * sp) * sm(min(1.0, (t - T_EXIT) / 0.6))
        if s < d0: p = lerp3(EXIT_PTS[0], EXIT_PTS[1], s / d0); yaw = ang_to(EXIT_PTS[0], EXIT_PTS[1])
        else: p = lerp3(EXIT_PTS[1], EXIT_PTS[2], min(1.0, (s - d0) / d1)); yaw = ang_to(EXIT_PTS[1], EXIT_PTS[2])
        tu = sm(seg01(t, T_EXIT, T_EXIT + 0.5)); P['yaw'] = dtx.angl(BYAW, yaw, tu); P['base'] = p
        if s > 0: P['walk'] = s * 2 * PI / 1.5; P['stride'] = 0.32
        P['lean'] = 0.02
    return P
def wld(w):
    """world point -> boss-local (at B0, BYAW)"""
    return hd.Ry(BYAW).T @ (V(w, float) - V(B0, float))
def boss_sword(t, P):
    """the boss's sword: in his right fist, blade down-forward; offered tip down (0:14); dropped at T_DROP -> lies flat on the stones"""
    if t < T_DROP:
        g = grip_pt(P, 'r', 0.07, 0.02); of = win(t, F(14.15), F(17.6), F(0.5))
        d = nz(lerp3(bl((0.06, -0.92, 0.38)) - V(B0), bl((0.0, -1.0, 0.05)) - V(B0), of))
        return hd.sword(g, d, P['_rpalm'], col=(150, 150, 166), grip=(40, 30, 40), guard=PGOLD, length=1.05), g
    # fall: the hilt drops, the blade tips over to lie on the floor (towards -x)
    u = seg01(t, T_DROP, T_DROP + 0.45); g0 = _DROP_G[0]
    a = sm(u) * (PI / 2 - 0.05)
    tip_dir = nz(V((-math.sin(a), -math.cos(a), 0.0)))
    hilt = V((g0[0], lerp(g0[1], 0.07, min(1.0, u * 1.6)), g0[2]))
    if u >= 1.0:
        bump = 0.03 * max(0.0, math.sin(min(1.0, (t - T_DROP - 0.45) / 0.18) * PI)); hilt = hilt + V((0, bump, 0))
    hilt[1] = max(hilt[1], 0.035 + max(0.0, -tip_dir[1]) * 0.0)
    if hilt[1] + tip_dir[1] * 1.15 < 0.03: tip_dir = nz(V((tip_dir[0], (0.03 - hilt[1]) / 1.15, 0.0)))
    return hd.sword(hilt, tip_dir, V((0, 0, 1.0)) if u > 0.5 else V((1.0, 0, 0)), col=(150, 150, 166), grip=(40, 30, 40), guard=PGOLD, length=1.05), hilt
_DROP_G = [None]

def knight_pose(t):
    """the hero: charge -> guard -> listens -> signs -> takes the boss's spot -> raises the sign"""
    if t < F(1.4):
        stop = sm(seg01(t, F(0.55), F(1.0))); P = charger(k_run_z(t), t, stop); P['_blade'] = charger_blade(t, stop); return P
    P = dict(base=KST, yaw=KYAW, eyes='open', mouth='neutral', brow=0.5, lean=0.06, cape_sway=0.15 * math.sin(t * 1.3), head=(0.0, 0.2, 0.0))
    P['rh'] = (0.24, 1.3, 0.42); P['rgrip'] = 0.9; P['rpalm'] = (-1.0, 0, 0.0); P['lh'] = (-0.24, 1.08, 0.18); P['lgrip'] = 0.5
    blade = nz(GUARD) if t < F(3.6) else nz(lerp3(GUARD, (0.25, 0.55, 1.0), sm(seg01(t, F(3.6), F(4.4))))); P['eyes'] = 'wide' if t < F(2.6) else 'open'
    # 0:05 looks from the sign to the boss
    if F(5.0) <= t < F(8.0):
        s_ = sm(seg01(t, F(5.1), F(5.5))) * (1 - sm(seg01(t, F(6.4), F(6.9))))
        P['head'] = (0.3 * s_, 0.2 + 0.12 * s_, 0.0); P['look'] = (0.8 * s_, 0.4 * s_)
    if T0['03'] <= t < tend('03') + 0.2: P['brow'] = 0.8
    if t >= F(14.0): P['brow'] = lerp(0.5, -0.2, sm(seg01(t, F(14.2), F(15.0))))
    # 0:18 eyebrow lift, sword tip lowered, left hand gestures at the contract
    lo = sm(seg01(t, F(18.0), F(18.7)))
    if lo > 0:
        P['rh'] = lerp3(P['rh'], (0.25, 1.0, 0.34), lo); blade = nz(lerp3(tuple(blade), (0.0, -0.55, 1.0), lo))
        g_ = win(t, F(18.2), F(20.2), F(0.35)); P['lh'] = lerp3(P['lh'], (-0.22, 1.18, 0.46), g_); P['lpalm'] = (0.2, 1.0, 0.2) if g_ > 0.3 else None
        if P['lpalm'] is None: P.pop('lpalm')
        P['lgrip'] = lerp(0.5, 0.2, g_)
        if F(18.0) <= t < F(20.3): P['brow'] = -0.55; P['eyes'] = 'wide' if t < F(18.6) else 'open'
    # 0:23 nods as he signs
    nod = win(t, F(24.0), F(24.7), F(0.25))
    if nod > 0: P['head'] = (0.0, 0.2 - 0.3 * nod, 0.0)
    if F(25.3) <= t < F(29.0): P['mouth'] = 'smile' if t < F(26.5) else 'neutral'
    # 0:29 his eyes follow the falling sword
    if t >= T_DROP - 0.05:
        e = sm(seg01(t, T_DROP, T_DROP + 0.35)); P['head'] = (-0.35 * e, 0.2 - 0.45 * e, 0.0); P['look'] = (-0.9 * e, -1.0 * e)
    # 0:30 steps into the boss's spot
    if t >= F(30.6):
        pts = [KST, (-0.45, 0.0, 10.65), K_NEW]; u = seg01(t, F(30.6), F(32.3)); us = sm(u)
        d0 = math.dist(pts[0], pts[1]); d1 = math.dist(pts[1], pts[2]); s = us * (d0 + d1)
        p = lerp3(pts[0], pts[1], s / d0) if s < d0 else lerp3(pts[1], pts[2], (s - d0) / d1)
        P['base'] = p; P['walk'] = s * 2 * PI / 1.3; P['stride'] = 0.28
        yaw_w = ang_to(pts[0], pts[1]) if s < d0 else ang_to(pts[1], pts[2])
        P['yaw'] = dtx.angl(yaw_w, PI, sm(seg01(t, F(31.9), F(32.6)))) if u > 0.6 else yaw_w
        if u >= 1: P.pop('walk')
        P['head'] = (0.0, 0.08, 0.0); P['look'] = (0.0, 0.0); P['brow'] = 0.3; P['eyes'] = 'open'; P['mouth'] = 'neutral'
        P['rh'] = (0.3, 1.02, 0.16); blade = nz((0.05, -0.85, 0.4)); P['lh'] = (-0.25, 0.98, 0.1)
    # 0:35 the new boss snaps up the sign (left hand)
    if t >= T_GRAB[0]:
        P['brow'] = 0.6; P['head'] = (0.0, 0.12, 0.0)
        grab = wld_k(V(S_PLANT) + V((0.0, SIGN_GRIP + 0.02, 0.0))) + V((-0.06, 0, -0.03))
        up_raise = V((-0.5, 1.3, 0.46))
        u1 = sm(seg01(t, T_GRAB[0], T_GRAB[1])); u2 = sm(seg01(t, T_GRAB[1], T_GRAB[2]))
        lh = lerp3(P['lh'], tuple(grab), u1); lh = lerp3(lh, tuple(up_raise), u2)
        P['lh'] = lh; P['lgrip'] = lerp(0.5, 0.9, u1); P['lpalm'] = (1.0, 0.0, 0.0) if u1 > 0.5 else (0.6, 0.0, 0.4)
    mt = talking(t, '03') or talking(t, '07') or talking(t, '13')
    if mt: P['mouth'] = mt
    P['_blade'] = blade
    return P
def wld_k(w):
    """world -> knight-local at its new spot (facing -z)"""
    return hd.Ry(PI).T @ (V(w, float) - V(K_NEW, float))
def knight_sword(P):
    g = grip_pt(P, 'r', 0.06, 0.0); RB = hd.Ry(P.get('yaw', 0.0)); d = nz(RB @ V(P['_blade']))
    return hd.sword(g, d, P['_rpalm'], length=0.85)

def sign_state(t, BP, KP):
    """(bottom, up, fwd) of the sign"""
    fwd_b = V((0.0, 0.0, -1.0))
    if t < T_PLANT[1] + 0.02:
        g = grip_pt(BP, 'l', 0.07, 0.0); up = nz(lerp3((0.0, 1.0, -0.05), (0.0, 1.0, 0.0), seg01(t, T_PLANT[0], T_PLANT[1])))
        bot = g - up * SIGN_GRIP
        pl = seg01(t, T_PLANT[0], T_PLANT[1])
        if pl > 0.85: bot = lerp3(tuple(bot), S_PLANT, (pl - 0.85) / 0.15)
        bot = V(bot); bot[1] = max(0.0, bot[1]); return bot, up, fwd_b
    if t < T_GRAB[1] or KP is None or '_lwrist' not in KP:
        return V(S_PLANT, float), V((0, 1.0, 0)), fwd_b
    g = grip_pt(KP, 'l', 0.07, 0.0); up = V((0, 1.0, 0)); bot = g - up * SIGN_GRIP; bot[1] = max(0.0, bot[1])
    return bot, up, fwd_b

def challenger_pose(t):
    z = challenger_z(t)
    if t >= TEND: z = challenger_z(t)
    P = charger(z, t, 0.0); P['_blade'] = charger_blade(t, 0.0); return P

# ======================= world =======================
RED_KEY = (255, 46, 36)
def red_level(t):
    """arena red light: steady, two pulses at 0:11 ('same arena'), a 3-frame flicker when the job changes hands"""
    v = 1.0 + 0.55 * (win(t, F(11.35), F(11.75), 0.12) + win(t, F(12.15), F(12.55), 0.12))
    fr = int(round((t - T_ROLE) * FPS))
    if 0 <= fr < 3: v *= (0.15, 1.6, 0.35)[fr]
    return v
_PC = {}
def poses(t):
    if t not in _PC:
        if len(_PC) > 6: _PC.clear()
        BP = boss_pose(t); QB = boss(BP); KP = knight_pose(t); QK = knight(KP); _PC[t] = (BP, QB, KP, QK)
    return _PC[t]
def world(t):
    BP, QB, KP, QK = poses(t)
    layers = [FB.ARENA, FB.gate_doors(1.75), FB.torches(t)]
    layers.append(QB)
    if t < T_DROP: Ssw, g = boss_sword(t, BP); _DROP_G[0] = g
    else:
        if _DROP_G[0] is None: boss_sword(T_DROP - 1e-3, boss_pose(T_DROP - 1e-3)); _DROP_G[0] = grip_pt(_bp_cache(T_DROP - 1e-3), 'r', 0.07, 0.02)
        Ssw, _ = boss_sword(t, BP)
    layers.append(Ssw)
    layers.append(QK); layers.append(knight_sword(KP))
    bot, up, fwd = sign_state(t, BP, KP); layers.append(sign(bot, up, fwd))
    if F(31.5) <= t:
        CP = challenger_pose(t); layers.append(knight(CP)); layers.append(knight_sword(CP))
    L = FB.torch_lights(t, dim=0.42)
    rl = red_level(t)
    L.append(((0.0, 4.8, 8.8), RED_KEY, 0.6 * rl))                                       # the red boss light
    L.append(((-3.2, 3.0, 6.8), (180, 186, 220), 0.85))                                   # neutral-cool fill from the gate side
    L.append(((2.5, 3.5, 13.5), (150, 90, 170), 0.8))                                     # cool plum rim from behind
    glows = []
    return layers, L, (10, 6, 10), 0.26 * (0.85 + 0.15 * rl), glows, BP, KP
_BPC = {}
def _bp_cache(t):
    if t not in _BPC: P = boss_pose(t); boss(P); _BPC[t] = P
    return _BPC[t]
def _init_drop():
    P = _bp_cache(T_DROP - 1e-3); _DROP_G[0] = grip_pt(P, 'r', 0.07, 0.02)
_init_drop()

# ======================= camera =======================
O0 = V((-1.25, 0.75, 6.25)); O1 = V((-1.12, 0.78, 6.6)); OT = V((0.0, 2.0, 11.4))
OV = (O1 - O0) / F(3.0)
def cam_shot(t):
    sc = scene(t)
    if sc == 'open':
        return tuple(O0 + OV * t), tuple(OT), 29.0
    if sc in ('snap', 'loop'):                                      # the opening framing (exactly frame 0's camera at the loop point)
        return tuple(O0 + OV * (t - TEND)), tuple(OT), 29.0
    BP, _, KP, _ = poses(t); bh = V(BP['_head'], float); kh = V(KP['_head'], float)
    if sc == 'two':
        u = seg01(t, F(3.0), F(5.0)); return lerp3((-4.0, 1.45, 10.3), (-3.8, 1.5, 10.45), u), tuple((bh + kh) / 2 - V((0, 0.35, 0))), 50.0
    if sc == 'ots':
        u = seg01(t, F(5.0), F(8.0)); return lerp3((-0.2, 2.5, 12.85), (-0.15, 2.45, 12.65), u), tuple(kh - V((0, 0.1, 0))), 38.0
    if sc == 'counter':
        u = sm(seg01(t, F(8.0), F(10.2))); return lerp3((0.75, 1.45, 8.8), (0.7, 1.55, 8.9), u), lerp3((0.0, 1.95, 11.4), (0.0, 2.75, 11.4), u), 46.0
    if sc == 'sweep':
        u = seg01(t, F(11.0), F(14.0)); return lerp3((-2.7, 1.7, 11.0), (-2.5, 1.65, 10.8), u), tuple(bh - V((0.0, 0.55, 0.0)) + V((0, 0, -0.3))), 46.0
    if sc == 'offer':
        u = seg01(t, F(14.0), F(18.0)); return lerp3((-2.6, 1.0, 10.6), (-2.45, 1.05, 10.7), u), lerp3((-0.35, 1.45, 10.6), (-0.35, 1.5, 10.6), u), 46.0
    if sc == 'kmcu':
        u = seg01(t, F(18.0), F(20.0)); return lerp3((-0.6, 1.62, 10.85), (-0.55, 1.6, 10.7), u), tuple(kh - V((0, 0.25, 0))), 40.0
    if sc == 'benefit':
        u = seg01(t, F(20.0), F(23.0)); return lerp3((-2.6, 1.6, 9.3), (-2.5, 1.62, 9.45), u), tuple(bh - V((0.0, 0.25, 0.0))), 42.0
    if sc == 'signed':
        u = seg01(t, F(23.0), F(27.0)); return lerp3((-1.75, 1.75, 11.1), (-1.65, 1.72, 10.9), u), tuple(kh - V((0, 0.55, 0))), 50.0
    if sc == 'nobreak':
        u = seg01(t, F(27.0), F(29.0)); return tuple(bh + V((0.55, -0.2, -1.75)) + V((-0.05, 0, 0.15)) * u), tuple(bh - V((0, 0.32, 0))), 42.0
    if sc == 'drop':
        g = V(_DROP_G[0], float); u = seg01(t, F(29.0), F(30.0))
        return tuple(V((-1.75, 0.6, 12.0)) + V((0.05, -0.02, -0.1)) * u), tuple(V((-0.8, 0.95, 10.35))), 56.0
    if sc == 'exit':
        BP = boss_pose(t); bp = V(BP['base'], float); u = seg01(t, F(30.0), F(32.0))
        return tuple(bp + V((1.3, 1.65, -2.7)) + V((-0.2, 0, 0.3)) * u), tuple(bp + V((-0.1, 1.55, 0.0))), 48.0
    if sc == 'enter':                                              # pan from the knight in his new spot to the gate: the challenger runs in
        u = sm(seg01(t, F(32.4), F(34.4)))
        return lerp3((-1.1, 1.8, 13.3), (-0.9, 1.75, 13.0), seg01(t, F(32.0), F(35.0))), lerp3((0.2, 1.5, 11.5), (-0.4, 1.3, 0.0), u), 40.0
    # approach: low, beside the new boss (his sign in the foreground), long lens towards the gate
    u = seg01(t, F(36.0), F(38.0)); return lerp3((1.3, 0.9, 14.2), (1.25, 0.92, 14.0), u), lerp3((-0.5, 1.3, 4.0), (-0.55, 1.3, 4.6), u), 40.0

# ======================= render =======================
def frame_low(t):
    pos, tgt, fov = cam_shot(t); cam = Camera.look(tuple(pos), tuple(tgt))
    layers, L, fog, amb, glows, BP, KP = world(t)
    R = Renderer(W, H, fog=fog)
    img, vi, zb = zrender(R, cam, layers, L, fov=fov, fog_start=9, fog_end=30, ambient=amb, return_z=True)
    a = look.outline(np.asarray(img).astype(np.float32), zb)
    a = np.clip((a * np.array([1.0, 0.98, 1.05]) - 80) * 1.18 + 84, 0, 255)
    return post.ps1(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), levels=6), vi

# ======================= HUD, contract UI, subtitles (1080 x 1920) =======================
def tw(s, sc): return font.width(s, sc) if hasattr(font, 'width') else len(s) * 6 * sc - sc
def ctext(d, s, y, sc, col, o=4, x=None):
    x = int(540 - tw(s, sc) / 2) if x is None else x
    look.draw_cells(d, look.text_cells(s, x, y, sc, col), o)
TX = dict(boss='SON BOSS' if TRL else 'FINAL BOSS', knight='ŞÖVALYE' if TRL else 'KNIGHT', fights='DÖVÜŞ' if TRL else 'FIGHTS',
          phase='AŞAMA 3' if TRL else 'PHASE 3', pos1='BOSS POZİSYONU' if TRL else 'BOSS POSITION', pos2='AÇIK' if TRL else 'OPEN',
          yes='EVET' if TRL else 'YES', no='HAYIR' if TRL else 'NO', hp='CAN: 100' if TRL else 'HP: 100',
          resp1='YENİDEN DOĞUŞ:' if TRL else 'RESPAWNS:', resp2='SINIRSIZ' if TRL else 'INFINITE', signed='İMZALANDI' if TRL else 'SIGNED',
          days='İZİN GÜNÜ YOK' if TRL else 'NO DAYS OFF', breaks='MOLA YOK' if TRL else 'NO BREAKS',
          cov1='BOSS', cov2='ARANIYOR' if TRL else 'WANTED', contract='SÖZLEŞME' if TRL else 'CONTRACT')
GLD = (255, 214, 96); WHT = (246, 242, 230); RED = (230, 56, 50)
def fights(t):
    if t < T_ROLE: return '9999'
    return '0' if t < F(36.0) else '1'
def boss_bar(d, t):
    """top HUD: name + red bar + FIGHTS counter (kept above y 240: the like toast lives at y 280-410)"""
    nm = TX['boss'] if t < T_ROLE else TX['knight']
    if 0 <= t - T_ROLE < 0.45:                                   # retro glitch FINAL BOSS -> KNIGHT
        fr = int((t - T_ROLE) * FPS); nm = (TX['boss'], TX['knight'], '#' * len(TX['knight']), TX['boss'], TX['knight'])[min(4, fr // 2)]
    ctext(d, nm, 62, 6, (255, 226, 190) if t < T_ROLE else (150, 220, 255), x=64)
    flash = win(t, F(5.55), F(5.85), 0.06) > 0.5 or (0 <= t - T_ROLE < 0.3 and int(t * 24) % 2 == 0)
    x0, x1, y0, y1 = 64, 1016, 126, 166
    d.rectangle([x0 - 8, y0 - 8, x1 + 8, y1 + 8], fill=(0, 0, 0))
    col = (255, 255, 255) if flash else ((214, 40, 44) if t < T_ROLE else (60, 130, 230))
    d.rectangle([x0, y0, x1, y1], fill=col); d.rectangle([x0, y0, x1, y0 + 9], fill=(255, 150, 140) if t < T_ROLE else (150, 200, 255))
    f = fights(t); s = f'{TX["fights"]}: {f}'
    big = win(t, F(8.25), F(11.0), F(0.3))                       # the planted detail: the counter pops up big, then returns
    pop = (0 <= t - F(36.0) < 0.5)
    if big < 0.02:
        ctext(d, s, 190, 5, GLD if pop and int(t * 24) % 4 < 2 else WHT, x=int(1016 - tw(s, 5)))
    else:
        sc = int(round(lerp(5, 13, big))); y = int(lerp(190, 560, big)); x = int(lerp(1016 - tw(s, 5), 540 - tw(s, sc) / 2, big))
        ctext(d, s, y, sc, GLD if (t * 3) % 1 < 0.75 else (255, 255, 255), o=6, x=x)
    ph = win(t, F(11.25), F(12.45), 0.08)
    if ph > 0 and int(t * 12) % 3 != 2: ctext(d, TX['phase'], 236, 10, (255, 80, 70), o=5)
def cover(d, t):
    """BOSS / WANTED cover title: big in the first 2 s, small under the bar until 4.6 s; back at the loop (35.3 s -> end)"""
    big = 1.0 if t < F(2.15) else (0.0 if t < F(35.3) else (sm(seg01(t, F(35.3), F(35.6))) if t < F(36.0) else (0.0 if t < F(38.0) else 1.0)))
    small = (F(2.15) <= t < F(4.6))
    if big > 0:
        sc = int(round(18 * (0.6 + 0.4 * big))) if F(35.3) <= t < F(36.0) else 18
        y1 = 250; ctext(d, TX['cov1'], y1, sc, WHT, o=8); ctext(d, TX['cov2'], y1 + 8 * sc + 16, sc, (255, 70, 60), o=8)
    elif small:
        u = sm(seg01(t, F(2.15), F(2.4))); sc = int(round(lerp(18, 9, u))); y1 = int(lerp(250, 252, u))
        ctext(d, TX['cov1'] + ' ' + TX['cov2'] if u > 0.6 else TX['cov1'], y1, sc, WHT, o=5)
        if u <= 0.6: ctext(d, TX['cov2'], y1 + 8 * sc + 16, sc, (255, 70, 60), o=6)
def panel(d, x0, y0, x1, y1, col=(24, 18, 28), edge=(214, 190, 120)):
    d.rectangle([x0 - 6, y0 - 6, x1 + 6, y1 + 6], fill=edge); d.rectangle([x0, y0, x1, y1], fill=col)
def contract_ui(im, t):
    d = ImageDraw.Draw(im)
    # 0:14 BOSS POSITION / OPEN
    a = win(t, F(14.5), F(18.0), 0.12)
    if a > 0.5:
        panel(d, 150, 300, 930, 545); ctext(d, TX['contract'], 328, 5, (214, 190, 120)); ctext(d, TX['pos1'], 392, 8, WHT); ctext(d, TX['pos2'], 470, 8, (120, 255, 140))
    # 0:18 YES / NO (big), 0:23 YES highlights, stamp
    yn = F(18.15) <= t < F(27.0)
    if yn:
        hl = t >= F(23.35); blink = hl and t < F(24.0) and int(t * 12) % 2 == 0
        for i, (s, x0) in enumerate(((TX['yes'], 170), (TX['no'], 600))):
            on = (i == 0 and hl)
            fill = (60, 150, 70) if on and not blink else (30, 26, 36); edge = (140, 255, 150) if on else (180, 170, 150)
            if i == 1 and hl: fill, edge = (26, 22, 30), (90, 84, 80)
            panel(d, x0, 1330, x0 + 310, 1460, fill, edge); ctext(d, s, 1366, 9 if len(s) < 5 else 7, WHT if not (i == 1 and hl) else (120, 114, 110), x=int(x0 + 155 - tw(s, 9 if len(s) < 5 else 7) / 2))
    # 0:20 HP: 100 / RESPAWNS: INFINITE
    b = win(t, F(20.35), F(23.0), 0.1)
    if b > 0.5:
        panel(d, 110, 300, 970, 545, (20, 14, 22), (230, 60, 54)); ctext(d, TX['hp'], 330, 8, (255, 110, 100)); ctext(d, TX['resp1'], 418, 6, WHT); ctext(d, TX['resp2'], 475, 7, GLD)
    # 0:24 SIGNED stamp, 0:25 the tiny print rises as large text: NO DAYS OFF; 0:27 NO BREAKS
    if F(24.0) <= t < F(27.0):
        k = seg01(t, F(24.0), F(24.15)); sc = int(round(lerp(16, 11, k)))
        s = TX['signed']; w_ = tw(s, sc); x0 = int(540 - w_ / 2); y0 = 1150
        d.rectangle([x0 - 26, y0 - 22, x0 + w_ + 26, y0 + 7 * sc + 22], outline=(220, 40, 40), width=10); ctext(d, s, y0, sc, (230, 50, 46), o=4)
    if F(25.0) <= t < F(27.0):
        u = sm(seg01(t, F(25.0), F(25.7))); y = int(lerp(1300, 1010, u)); sc = int(round(lerp(3, 8, u)))
        ctext(d, TX['days'], y, sc, WHT, o=5)
    if F(27.15) <= t < F(28.95):
        u = sm(seg01(t, F(27.15), F(27.5))); ctext(d, TX['breaks'], 1230, int(round(lerp(7, 13, u))), (255, 80, 70), o=7)
COL = {'N': (242, 238, 226), 'K': (120, 230, 255), 'B': (255, 150, 140)}
TR = {'01': ['BOSS SALDIRMIYORDU.', 'İŞE ALIM YAPIYORDU.'], '02': ['İŞİMİ İSTER MİSİN?'], '03': ['SENİ YENMEYE GELDİM.'],
      '04': ['CAN ÇUBUĞUNDA NEREDEYSE ON BİN BAŞARISIZ DÖVÜŞ YAZIYORDU.'], '05': ['AYNI ARENA.', 'AYNI KONUŞMA.', 'HER SEFERİNDE YENİDEN DOĞUŞ.'],
      '06': ['KILICINI VE BİR SÖZLEŞMEYİ ŞÖVALYEYE UZATTI.'], '07': ['ÜCRETİ NE?'], '08': ['BİR CAN ÇUBUĞU.', 'SINIRSIZ YENİDEN DOĞUŞ.'],
      '09': ['ŞÖVALYE KÜÇÜK YAZILARI OKUMADAN İMZALADI.'], '10': ['MOLA YOK.'], '11': ['ESKİ BOSS SONUNDA GÜLÜMSEYEREK ÇIKTI.'],
      '12': ['MÜREKKEP KURUMADAN İLK RAKİBİ GELDİ.'], '13': ['BOSS ARANIYOR.'], '14': ['YENİ ŞÖVALYE TIPKI ONA BENZİYORDU.'], '15': ['DÖNGÜ SIRADAKİ BOSSUNU BULMUŞTU.']}
def _sub_scr():
    if not TRL: return SCR
    out = dict(SCR); sent = {}
    for k, v in SCR['sent'].items():
        if len(v) == len(TR[k]): sent[k] = [[a, b, tx] for (a, b, _), tx in zip(v, TR[k])]
        else: sent[k] = [[v[0][0], v[-1][1], ' '.join(TR[k])]]
    out['sent'] = sent
    return out
SUBS = look.Subtitles(_sub_scr(), LINES, W, H, S, COL, title_key='none', card_y=0.70, card_sc=8.0, card_n=15,
                      hil=({'İŞE', 'ALIM', 'BAŞARISIZ', 'DÖVÜŞ', 'SÖZLEŞMEYİ', 'KÜÇÜK', 'YAZILARI', 'TIPKI', 'DÖNGÜ'} if TRL else
                           {'HIRING', 'FAILED', 'FIGHTS', 'CONTRACT', 'TINY', 'PRINT', 'SMILING', 'EXACTLY', 'LOOP'}))
from nightkit import cta
CTA = cta.Achievement(t0=cta.default_time(DUR, dur_on=F(0.5)), lang=SUB_LANG, dur=F(0.5))
def frame_final(t):
    img, vi = frame_low(t); arr = post.upscale(img, S)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    boss_bar(d, t); cover(d, t); contract_ui(im, t)
    return CTA.apply(SUBS.apply(np.asarray(im).astype(np.float32), t), t)

ASSET = os.environ.get('ASSET')
if ASSET and __name__ == '__main__':
    floor = hd.bx((0, -0.05, 0), np.eye(3), (12, 0.05, 12), (70, 64, 58)); ims = []
    if ASSET == 'boss':
        for eyes, brow, mouth, cp, tg, fv in (('half', -0.6, 'neutral', (-0.6, 1.4, 3.8), (0, 1.5, 0), 48), ('half', -0.6, 'neutral', (-0.3, 2.1, 1.0), (0, 2.05, 0), 40),
                                              ('open', -0.2, 'smile', (0.25, 2.1, 0.95), (0, 2.05, 0), 40), ('half', -0.6, 'neutral', (-2.4, 1.6, 2.6), (0, 1.5, 0), 48)):
            P = dict(base=(0, 0, 0), yaw=0.0, eyes=eyes, brow=brow, mouth=mouth, rh=(0.36, 1.08, 0.2), rpalm=(-1.0, 0, 0.1), rgrip=0.9, lh=(-0.42, 1.86, 0.46), lgrip=0.9, lpalm=(1.0, 0, 0))
            Q = boss(P); g = grip_pt(P, 'l', 0.07, 0.0)
            Q += sign(g - V((0, SIGN_GRIP, 0)), (0, 1, 0), (0, 0, 1.0))
            Q += hd.sword(grip_pt(P, 'r', 0.07, 0.02), nz((0.06, -0.92, 0.38)), P['_rpalm'], col=(150, 150, 166), grip=(40, 30, 40), guard=PGOLD, length=1.05)
            ims.append(dtx.shot([floor, Q], cp, tg, fv))
    elif ASSET == 'cast':
        Q = boss(dict(base=(0.9, 0, 0), yaw=PI)) + knight(dict(base=(-0.6, 0, 0), yaw=PI))
        ims.append(dtx.shot([floor, Q], (0.2, 1.4, -6.0), (0.2, 1.2, 0), 40))
    out = Image.new('RGB', (W * S * len(ims) // 2, H * S // 2))
    for i, im in enumerate(ims): out.paste(im.resize((W * S // 2, H * S // 2), Image.NEAREST), (i * W * S // 2, 0))
    out.save(f'test_bw_{ASSET}.png'); print('written'); sys.exit()

TEST = os.environ.get('TEST') or os.environ.get('TESTF')
if TEST and __name__ == '__main__':
    k_ = 1.2 if os.environ.get('TESTF') else 1.0
    ts = [round(float(x) * k_, 4) for x in TEST.split(',')] if TEST != 'all' else [round(x, 2) for x in np.arange(0, DUR, float(os.environ.get('STEP', '1.0')))]
    tw_ = int(os.environ.get('TW', '270'))
    ims = [Image.fromarray(np.clip(frame_final(x), 0, 255).astype(np.uint8)).resize((tw_, tw_ * 16 // 9), Image.LANCZOS) for x in ts]
    th = ims[0].size[1]
    per = int(os.environ.get('PER', '8')); rows = (len(ims) + per - 1) // per; shp = Image.new('RGB', (min(per, len(ims)) * (tw_ + 2), rows * (th + 18)), (30, 30, 30))
    dd = ImageDraw.Draw(shp)
    for i, (im, x) in enumerate(zip(ims, ts)): shp.paste(im, ((i % per) * (tw_ + 2), (i // per) * (th + 18))); dd.text(((i % per) * (tw_ + 2) + 4, (i // per) * (th + 18) + th + 3), f'{x / 1.2:.2f}f {scene(x)}', fill=(255, 255, 0))
    shp.save(os.environ.get('TEST_OUT', 'test_bw.png')); print('test written', DUR); sys.exit()

# ======================= QA manifest =======================
QA = dict(fps=FPS, dur=DUR, W=W, frame=lambda t: Image.fromarray(np.clip(frame_final(t), 0, 255).astype(np.uint8)).resize((W, H), Image.BOX), chars={},
          geom=lambda t, name, st, V_: [], camera=lambda t: cam_shot(t)[0], min_cam_dist=0.3, camera_ok=lambda p: True, allow_jump=[], weapon_events=[],
          scenes=[dict(id=nm, t0=a, t1=(CUTS[i + 1][1] if i + 1 < len(CUTS) else DUR), action=nm) for i, (nm, a) in enumerate(CUTS)],
          texts=lambda: [('hud', TX['boss'], 6), ('hud', 'FIGHTS: 9999', 5), ('hud', TX['cov2'], 26)])

# ======================= AUDIO (stems: dialogue / music / fx+ambience) =======================
from nightkit.audio import Sound, duck_envelope, soft_fire
OUT = 'out'; os.makedirs(OUT, exist_ok=True)
STEM_DIR = os.environ.get('STEM_DIR', os.path.join(OUT, 'bw_stems'))
BAR = 2.0                                           # build seconds per bar; the two-bar loop (4 s) divides DUR = 48 -> the loop point lands on beat 1
def build_audio(path):
    import soundfile as _sf
    s_ = Sound(DUR, loop=False, seed=11); sr = s_.sr; n = s_.n; t = s_.t
    BED = np.zeros(n); FX = np.zeros(n); MUS = np.zeros(n)
    def put(buf, x, t0, v=1.0):
        i = int(round(t0 * sr))
        if i >= n or i + len(x) <= 0: return
        if i < 0: x = x[-i:]; i = 0
        j = min(n, i + len(x)); buf[i:j] += (x * v)[:j - i]
    def nb(t0, d, lo, hi, v, seed, shape=2, buf=None): put(FX if buf is None else buf, s_.filt_short(s_.noise(d, seed), lo=lo, hi=hi) * np.sin(np.pi * s_.T(d) / d) ** shape, t0, v)
    def tone(t0, m, d, v, dec=3.0, att=0.005, glide=0.0, buf=None, harm=(1.0,)):
        f = 440 * 2 ** ((m - 69) / 12); tt = s_.T(d); fr = f * (1 + glide * tt / d); ph = np.cumsum(fr) / sr
        x = sum(a * np.sin(2 * np.pi * ph * (k + 1)) for k, a in enumerate(harm)); put(FX if buf is None else buf, x * np.minimum(1, tt / att) * np.exp(-tt * dec), t0, v)
    def thud(t0, f=60, v=0.1, d=0.3, buf=None): tt = s_.T(d); put(FX if buf is None else buf, np.sin(2 * np.pi * f * tt * (1 - 0.3 * tt / d)) * np.exp(-tt * 14), t0, v)
    def clink(t0, v=0.03, seed=0):
        for k, f in enumerate((2900, 4100, 5300)): tt = s_.T(0.3); put(FX, np.sin(2 * np.pi * f * (1 + 0.02 * hsh(seed + k)) * tt) * np.exp(-tt * (18 + 5 * k)), t0 + k * 0.03, v * (1 - 0.25 * k))
    def step(t0, v=0.05, seed=0, heavy=False):
        nb(t0, 0.07, 80 if heavy else 150, 900 if heavy else 2200, v, seed, 1); thud(t0, 48 if heavy else 70, v * (1.6 if heavy else 0.8), 0.15)
        if not heavy: clink(t0 + 0.01, v * 0.25, seed)                # armour jingle
    def whoosh(t0, d=0.35, v=0.06, seed=1):
        tt = s_.T(d); put(FX, s_.filt_short(s_.noise(d, seed), lo=400, hi=3500) * np.sin(np.pi * tt / d) ** 2 * (1 + tt / d), t0, v)
    def clack(t0, v=0.12):                                           # wooden sign snap
        nb(t0, 0.05, 300, 2500, v, 31, 1); thud(t0, 180, v * 0.6, 0.12); tone(t0, 57, 0.15, v * 0.3, dec=25, harm=(1.0, 0.5, 0.3)); whoosh(t0 - 0.2, 0.25, v * 0.5, 32)
    def ui(t0, m=84, v=0.03, n_=1):
        for i in range(n_): tone(t0 + 0.07 * i, m + 5 * i, 0.12, v, dec=22, harm=(1.0, 0.0, 0.3))
    def stamp(t0, v=0.25): thud(t0, 85, v, 0.25); nb(t0, 0.06, 200, 3000, v * 0.5, 77, 1)
    # ---- arena ambience: torches, a low drone, distant wind from the corridor
    BED += soft_fire(s_, level=0.014, seed=5)
    for f, a in ((41.2, 1.0), (55.0, 0.5)): BED += np.sin(2 * np.pi * f * t + a) * 0.012 * a
    BED += s_.filt(s_.rng.normal(0, 1, n), lo=150, hi=900) * 0.008
    # ---- music: an original two-bar boss loop (D minor, 120 bpm build = 100 bpm final), a quiet bed under everything,
    #      full from 0:11, lower under 'No breaks', relaxes at the exit, back to the bed level for the loop point
    beat = BAR / 4
    def note(buf, t0, m, d, v, harm=(1.0, 0.5, 0.33, 0.25), dec=1.5, att=0.01):
        f = 440 * 2 ** ((m - 69) / 12); tt = s_.T(d); x = sum(a * np.sin(2 * np.pi * f * (k + 1) * tt) for k, a in enumerate(harm))
        put(buf, x * np.minimum(1, tt / att) * np.exp(-tt * dec) * np.minimum(1, (d - tt) / 0.05), t0, v)
    BASS = [38, 38, 41, 40, 38, 38, 33, 37]                        # D D F E | D D A C#
    PAD = [(50, 53, 57), (49, 52, 57)]                             # Dm | A
    loopf = np.zeros(n); bed_m = np.zeros(n)
    for b in range(int(DUR / beat) + 1):
        t0 = b * beat; i = b % 8
        note(loopf, t0, BASS[i], beat * 0.95, 0.06, harm=(1.0, 0.6, 0.3, 0.15), dec=2.0)
        note(bed_m, t0, BASS[i], beat * 0.95, 0.035, harm=(1.0, 0.3), dec=2.5)
        if i % 2 == 0: thud(t0, 52, 0.12, 0.35, buf=loopf)          # drum on 1 and 3
        if i in (3, 7): nb(t0 + beat * 0.5, 0.12, 2000, 8000, 0.012, 900 + b, 2, buf=loopf)   # a tick on the off-beat
        if i % 4 == 0:
            for m in PAD[(i // 4)]: note(loopf, t0, m + 12, BAR * 0.98, 0.012, harm=(1.0, 0.4, 0.2), dec=0.3, att=0.15)
            for m in PAD[(i // 4)]: note(bed_m, t0, m + 12, BAR * 0.98, 0.006, harm=(1.0, 0.3), dec=0.3, att=0.2)
    def ramp(a, b, v0, v1): return np.clip((t - a) / max(1e-6, b - a), 0, 1) * (v1 - v0) + v0
    full = np.clip((t - F(10.9)) / 0.3, 0, 1) * (1 - 0.45 * np.clip((t - F(27.0)) / 0.2, 0, 1) * np.clip((F(29.1) - t) / 0.2, 0, 1))
    full = full * (1 - 0.35 * np.clip((t - T_EXIT) / 0.8, 0, 1)) * (1 - np.clip((t - F(35.0)) / F(3.0), 0, 1))
    MUS += loopf * full + bed_m * (1 - full)
    # ---- 0:00 the charge: fast footsteps (the run-cycle feet), the sign snaps up (clack + whoosh), the sword whooshes and stops
    def run_steps(zfn, a, b, v, seed):
        last = None; tt_ = a
        while tt_ < b:
            ph = run_phase(zfn(tt_)) % PI
            if last is not None and ph < last: step(tt_, v, seed + int(tt_ * 10))
            last = ph; tt_ += 1 / 240
    run_steps(k_run_z, 0.0, F(1.0), 0.05, 100)
    clack(0.06, 0.09); whoosh(F(0.85), 0.3, 0.07, 3)
    # ---- 0:03 armour creak, the sign planted; 0:05 a short sword whoosh; bar flash blip
    for k in range(3): tone(F(3.0) + 0.12 * k, 74 - 3 * k, 0.25, 0.008, dec=8, glide=-0.1, harm=(1.0, 0.7, 0.5))
    thud(T_PLANT[1], 90, 0.18, 0.2); nb(T_PLANT[1], 0.05, 200, 1800, 0.05, 41, 1)
    whoosh(F(5.25), 0.25, 0.05, 5); ui(F(5.6), 72, 0.025)
    # ---- 0:08 UI click on the counter; 0:11 PHASE 3 sting + the two light pulses
    ui(F(8.25), 88, 0.035, 2)
    for m, dl in ((50, 0.0), (53, 0.0), (57, 0.0)): tone(F(11.25) + dl, m, 1.2, 0.03, dec=1.8, harm=(1.0, 0.6, 0.4, 0.3))
    for a in (F(11.35), F(12.15)): thud(a, 45, 0.25, 0.5); nb(a, 0.4, 60, 400, 0.05, int(a * 10), 2)
    # ---- 0:14 sword offered (soft metal), contract (paper); 0:18 YES / NO tones; 0:20 benefits pop
    tone(F(14.3), 93, 1.0, 0.025, dec=3.0, harm=(1.0, 0.5, 0.3)); nb(F(14.5), 0.3, 1500, 7000, 0.03, 51, 2)
    ui(F(18.15), 79, 0.03); ui(F(18.3), 74, 0.03); ui(F(20.35), 84, 0.025, 2)
    # ---- 0:23 YES confirm, SIGNED stamp, NO DAYS OFF stamp; like toast chime; 0:27 'No breaks' thump
    for i, m in enumerate((76, 81, 88)): tone(F(23.35) + 0.08 * i, m, 0.35, 0.03, dec=6, harm=(1.0, 0.3))
    stamp(F(24.0), 0.3); stamp(F(25.6), 0.18); thud(F(27.15), 60, 0.12, 0.3)
    if CTA.on: put(FX, cta.chime(sr), CTA.t0, 1.0)
    # ---- 0:29 the sword clinks on the stone (no silence: music + ambience go on)
    tl = T_DROP + 0.45; tone(tl, 98, 1.2, 0.06, dec=3.5, harm=(1.0, 0.7, 0.4, 0.2)); thud(tl, 110, 0.12, 0.15); clink(tl + 0.17, 0.05, 61); clink(tl + 0.3, 0.025, 62)
    # ---- 0:30 the old boss's heavy steps out; role change glitch; 0:32 the challenger's steps join in the music's rhythm
    for k in range(12): step(T_EXIT + 0.45 + k * 0.62, 0.05 * max(0.25, 1 - k * 0.07), 200 + k, heavy=True)
    for i in range(4): tone(T_ROLE + 0.05 * i, (60, 72, 55, 79)[i], 0.08, 0.025, dec=20, harm=(1.0, 0.5, 0.5))
    nb(T_ROLE, 0.15, 1000, 6000, 0.03, 71, 1)
    for k in range(int((TEND - F(32.0)) / beat) + 1):                      # the challenger's steps on the beat (quieter far away)
        a = F(32.0) + k * beat - (F(32.0) % beat)
        if a < F(32.0) or a >= TEND: continue
        z = challenger_z(a); step(a, 0.06 * float(np.clip((z + 15) / 22, 0.15, 1.0)), 300 + k)
    for k in range(int((TEND - F(38.0)) / (beat / 2))):
        a = F(38.0) + k * beat / 2 + beat / 4
        if a < TEND: step(a, 0.04, 400 + k)
    # ---- 0:35 the sign snaps up again (same clack as frame 0); 0:36 FIGHTS: 1 blip
    clack(T_GRAB[2] - 0.05, 0.09); ui(F(36.0), 91, 0.03)
    # ---- voices (Enes's takes, when present)
    NB = np.zeros(n); wins = []
    for k_, t0 in LINES:
        f_ = os.path.join(TTS_DIR, 'bw', f'{k_}.wav')
        if not os.path.exists(f_): continue
        a, ar = _sf.read(f_); a = a if a.ndim == 1 else a.mean(1)
        a = np.interp(np.arange(int(len(a) * sr / ar)) / sr, np.arange(len(a)) / ar, a); act = np.abs(a) > 0.02 * np.abs(a).max()
        a = a * (0.12 / np.sqrt((a[act] ** 2).mean())); put(NB, a, t0); wins.append((t0, t0 + len(a) / sr))
    g = duck_envelope(n, sr, wins, -7.0, 0.05, 0.25) if wins else np.ones(n)
    bed = BED * g + MUS * (0.6 + 0.4 * g); fx = FX * (0.6 + 0.4 * g)
    L = bed + fx; R_ = np.roll(bed, 700) + np.roll(fx, 200)
    pk = max(np.abs(L).max(), np.abs(R_).max()); gv = (pk * 1.6 / np.abs(NB).max()) if np.abs(NB).max() > 0 else 0.0
    os.makedirs(STEM_DIR, exist_ok=True); sc_ = 0.9 / max(pk, 1e-9)
    _sf.write(os.path.join(STEM_DIR, 'bw_dialogue.wav'), NB * gv * sc_, sr)
    _sf.write(os.path.join(STEM_DIR, 'bw_music.wav'), np.stack([MUS * (0.6 + 0.4 * g), np.roll(MUS * (0.6 + 0.4 * g), 700)], 1) * sc_, sr)
    _sf.write(os.path.join(STEM_DIR, 'bw_fx_ambience.wav'), np.stack([BED * g + fx, np.roll(BED * g, 700) + np.roll(fx, 200)], 1) * sc_, sr)
    s_.L = L + NB * gv; s_.R = R_ + NB * gv; s_.reverb(0.12, length=1.4, decay=3.0)
    fi = np.clip(t / 0.008, 0, 1); s_.L = s_.L * fi; s_.R = s_.R * fi          # no click on the very first sample
    return s_.save(path, peak=0.9)
if __name__ == '__main__' and os.environ.get('PART') == 'audio':
    print(build_audio(os.path.join(OUT, 'boss_wanted.wav'))); sys.exit()
if __name__ == '__main__' and os.environ.get('PART'):
    a, b = map(int, os.environ['PART'].split(':'))
    import subprocess
    p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W * S}x{H * S}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', os.path.join(OUT, f"{os.environ.get('PART_PREFIX', 'bw')}_{a:05d}.mp4")], stdin=subprocess.PIPE)
    vhs = post.VHS(W * S, H * S, S, grade='none', chroma=0, scan_dark=1.0, vignette=0.22, grain=0.9, band_period=1e9)
    for f in range(a, min(b, N)): p.stdin.write(vhs(frame_final(f / FPS), f, f / FPS).tobytes())
    p.stdin.close(); p.wait()
