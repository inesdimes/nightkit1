"""WHY DO LOADING SCREENS SHOW TIPS? (Insert Disc 2, 28 Nov 2026) ~33 s final (x1.2 after), nightkit HD, 9:16. FAST COMEDY.
Brief: briefs/loading_tips.md v2 (lines locked by Enes 28 Nov). While the bar loads, a goblin crew builds the level FOR REAL; Bob the
foreman writes the tips because the bar slows while a tip is on screen. He runs out of tips at 99 %, the gate has no door, the crew hide
as a door, two statues and a pot; the hero smashes the pot, takes Bob's coin and walks on; Bob stamps HIRED over FIRED; the next level
loads = frame 0 (Bob hammering, LOADING 12 %).
Voices: tools/tts/lt.py (all Enes's clone; Bob +3 st x1.12, goblin +5 st, door -2 st). Reuses: dragon_taxes knight + helmet + torch +
trees + ground, the HD dragon (as a stone statue). New: HD goblins (performance faces + gestures, hard hats, ears), the floating
half-built courtyard in the white void, wall blocks, scaffolding, crane, portal, tip board, mimic chest, pots + shards, planks,
clipboard (LATE = FIRED -> HIRED), loading UI (bar, tip box, coin, hourglass, PRESS X), sparks, dust, speed lines.
Render: python tools/render_seq.py examples/loading_tips.py --prefix lt --seqs s1,s2,s3,s4,s5 / --master <out>
Stills: TEST=seq python examples/loading_tips.py -> test_lt.png | TEST=assets -> asset sheet"""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from nightkit.engine import Renderer, Camera, refresh
from nightkit.zraster import zrender
from nightkit import post, look, hd, motion, font, body, hands
from nightkit import face as facemod
import dragon_taxes as dtx

W, H, S = 270, 480, 4
PI = math.pi; V = np.array; FPS = 24
sm = motion.smooth
hsh, lerp, lerp3, mixc = dtx.hsh, dtx.lerp, dtx.lerp3, dtx.mixc
def seg01(t, a, b): return max(0.0, min(1.0, (t - a) / (b - a))) if b > a else (1.0 if t >= b else 0.0)
def win(t, a, b, r=0.25): return sm(seg01(t, a, a + r)) * (1 - sm(seg01(t, b - r, b)))
def nz(v): v = V(v, float); n = np.linalg.norm(v); return v / n if n > 1e-9 else v
def rot_y(d):
    d = nz(d); u, w = hd.frame_for(d, (1.0, 0, 0)); return np.column_stack([u, d, -w])
def grip_pt(P, key, off=0.075, lift=0.03): return P['_' + key + 'wrist'] + P['_' + key + 'dir'] * off + P['_' + key + 'palm'] * lift
def F(x): return round(x * 1.2, 4)
def ang_to(p, q): return math.atan2(q[0] - p[0], q[2] - p[2])
def back(u, s=1.7):                                                  # ease-out with overshoot (pop-in squash)
    u = min(1.0, max(0.0, u)); u -= 1; return u * u * ((s + 1) * u + s) + 1
SUB_LANG = os.environ.get('SUB_LANG', 'en'); TRL = SUB_LANG == 'tr'

# ======================= timeline (build seconds; the master is sped up x1.2) =======================
from nightkit.audio import Sound, duck_envelope
OUT = 'out'; os.makedirs(OUT, exist_ok=True)
TTS_DIR = os.environ.get('TTS_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tts'))
SCR = json.load(open(os.path.join(TTS_DIR, 'lt', 'script.json'), encoding='utf-8'))
KEYS = ['%02d' % i for i in range(0, 14)]
T0 = {}
def tend(k): return T0[k] + SCR['dur'][k]
def ws(k, i): s_ = SCR['sent'][k]; return T0[k] + s_[min(i, len(s_) - 1)][0]
def we(k, i): s_ = SCR['sent'][k]; return T0[k] + s_[min(i, len(s_) - 1)][1]
T0['00'] = 0.1                                       # N: Why do loading screens show tips?   (Bob hammering, LOADING 12 %)
S_JUMP = tend('00') + 0.05; T_JUMP = S_JUMP + 0.1    # close-up Bob: the bar JUMPS 12 -> 47 %, his hat pops off
T0['01'] = T_JUMP + 0.2                              # BOB: Too fast! Slow it down! He's at the door!
S_DOOR = ws('01', 2) - 0.2                           # whip pan: the hero's silhouette in the white doorway
S_TIP = tend('01') + 0.15                            # Bob at the tip board
T_TIPON = S_TIP + 0.2                                # TIP: TAKE YOUR TIME types on, the bar slows (hourglass)
T0['02'] = S_TIP + 0.25                              # N: The tips aren't for you. They're for them.
T0['03'] = tend('02') + 0.15                         # N: Every tip you read buys them time.
T_ROOF = (T0['02'] + 0.5, T0['02'] + 1.4)            # the crane sets the tower roof down (in the back of the tip shot)
S_MONT = tend('03') + 0.12                           # one whip-pan orbit: chest, torches, dragon
T0['04'] = S_MONT + 0.12                             # BOB: Chest! Torches! Dragon! Faster!
T_CHEST = ws('04', 0) - 0.15                         # the chest drops in (lands +0.32)
T_TORCH = ws('04', 1) - 0.05                         # four torches whoosh on
T_DRAGON = (ws('04', 2) - 0.45, ws('04', 2) + 0.55)  # the dragon statue is lowered on its rope
T_WALL = ws('04', 3) - 0.1                           # "Faster!": the low wall courses pop in
T_TREES = [S_MONT + 0.2, S_MONT + 0.38, S_MONT + 0.56, ws('04', 3) + 0.1, ws('04', 3) + 0.25, ws('04', 3) + 0.4]
T_WINK = tend('04') + 0.1                            # the chest opens an eye and WINKS at the goblin
T0['05'] = T_WINK + 0.3                              # GOBLIN: Boss, the chest winked at me.
S_99 = tend('05') + 0.15                             # wide crane-down: the tip box is EMPTY -> the bar races to 99 %
T_EMPTY = S_99 + 0.05; T_99 = (S_99 + 0.15, S_99 + 0.6)
T0['06'] = S_99 + 0.4                                # BOB: Ninety-nine percent! We made it, boys!
T_LOOK = tend('06') + 0.12                           # everyone turns to the gate: NO DOOR
T0['07'] = T_LOOK + 0.35                             # GOBLIN: Boss... where's the door?
S_100 = tend('07') + 0.15                            # WORDLESS: 100 %, PRESS X blinks, Bob's eye twitches
T_100 = S_100 + 0.35
S_PLACES = S_100 + 1.7
T0['08'] = S_PLACES + 0.05                           # BOB: Places! Everybody, places!
T_DIVE = (T0['08'] + 0.2, T0['08'] + 1.45)
S_HERO = tend('08') + 0.25                           # over the hero's shoulder: he walks in
T_WALK = (S_HERO - 0.3, S_HERO + 1.1)
T_KNOCK = (T_WALK[1] + 0.05, T_WALK[1] + 0.55)       # knock knock
T0['09'] = T_KNOCK[1] + 0.02                         # DOOR: Creak.
T0['10'] = tend('09') + 0.15                         # KNIGHT: Huh. Nice door. Very... wooden.
T_SPOT = tend('10') - 0.3                            # he spots the pot, turns, lifts the sword
T_LIFT = (T_SPOT + 0.25, T_SPOT + 0.7)
S_POT = T_LIFT[1] - 0.05
T_SMASH = S_POT + 0.18
T0['11'] = T_SMASH + 0.42                            # BOB: Plus one gold?
T_TAKE = (tend('11') + 0.05, tend('11') + 0.5)       # the hero TAKES the coin, shrugs, walks off
T_LEAVE = T_TAKE[1] + 0.05
T_STAMP = T_TAKE[1] + 0.3                            # Bob stamps HIRED over FIRED (held until S_GATE)
T0['12'] = T_STAMP + 0.08                            # BOB: Still hired!
T0['13'] = tend('12') + 0.12                         # N: Next level's loading. Read the tips... or skip?
S_GATE = max(T_STAMP + 1.25, ws('13', 1) - 1.0)      # the hero steps into the bright gate
T_FLASH = ws('13', 1) - 0.4; T_RESET = T_FLASH + 0.2 # white flash -> the frame-0 shot (next level, LOADING 12 %)
DUR = round(tend('13') + 0.3, 3); N = int(round(DUR * FPS))
LINES = [(k, T0[k]) for k in KEYS]
def fr(x): return int(round(x * FPS))
CUTS = [('open', 0.0), ('jump', S_JUMP), ('door', S_DOOR), ('tip', S_TIP), ('mont', S_MONT), ('wide', S_99), ('twitch', S_100),
        ('places', S_PLACES), ('hero', S_HERO), ('pot', S_POT), ('gate', S_GATE), ('loop', T_RESET)]
SEQS = [('s1', 0, fr(S_MONT)), ('s2', fr(S_MONT), fr(S_99)), ('s3', fr(S_99), fr(S_HERO)), ('s4', fr(S_HERO), fr(S_POT)), ('s5', fr(S_POT), N)]
def scene(t):
    nm = CUTS[0][0]
    for n_, a in CUTS:
        if t >= a: nm = n_
    return nm
def TT(t):
    """the level's own clock: after the white flash the NEXT level loads, so everything restarts (t - DUR < 0 = the moments before frame 0)"""
    return t - DUR if t >= T_RESET else t
def talking(t, key):
    if key not in T0: return 0.0
    for a, b, _ in SCR['sent'][key]:
        if T0[key] + a <= t < T0[key] + b: return 0.55 + 0.45 * math.sin((t - T0[key]) * 17.0)
    return 0.0
def talk_any(t, keys): return max([talking(t, k) for k in keys] + [0.0])

# ======================= the loading bar + the tips (the rule of the story) =======================
def bar(t):
    """percent shown on the bar. Fast with no tip on screen, slow while a tip is up; 12 % again after the reset"""
    u = TT(t)
    if u < T_JUMP: return 12.0
    if u < T_JUMP + 0.18: return lerp(12, 47, sm(seg01(u, T_JUMP, T_JUMP + 0.18)))
    if u < T_TIPON: return lerp(47, 58, seg01(u, T_JUMP + 0.18, T_TIPON))          # racing: no tip yet
    if u < S_MONT: return lerp(58, 64, seg01(u, T_TIPON, S_MONT))                  # tip up: crawling
    if u < T_EMPTY: return lerp(64, 80, seg01(u, S_MONT, T_EMPTY))                 # tip up (they build like mad)
    if u < T_99[1]: return lerp(80, 99, sm(seg01(u, T_99[0], T_99[1])))            # the tip box is EMPTY: it races
    if u < T_100: return 99.0
    return 100.0
def tip_text(t):
    u = TT(t)
    if u < T_TIPON: return None
    if u < S_MONT: return 'TAKE YOUR TIME'
    if u < T_EMPTY: return 'CHESTS ARE ALWAYS SAFE'
    if u < T_100: return ''
    return None
def tip_t0(t):
    u = TT(t); return T_TIPON if u < S_MONT else S_MONT
def slowed(t): u = TT(t); return T_TIPON + 0.25 <= u < T_EMPTY
def ui_on(t): u = TT(t); return u < S_HERO - 0.25

# ======================= set: the floating courtyard =======================
STONE = [(186, 178, 162), (176, 168, 152), (194, 186, 170), (170, 162, 148)]
BLOCKC = [(168, 160, 146), (158, 150, 138), (176, 168, 152), (150, 144, 134)]
WOOD = (150, 104, 62); WOOD_D = (116, 78, 46)
VOIDC = (240, 242, 248)
WALL_X = (-2.95, 4.3); WALL_Z = (6.0, 6.5); GATE_X = 0.7; COURSE = 0.4
TOWERS = [(-1.35, -0.7), (0.7, 1.35)]; TOWER_Z = (5.85, 6.65); TOWER_H = 3.2
LOW_X = (-2.95, -1.35)                                   # the low (unfinished) stretch: courses 3-5 pop in on "Faster!"
def _blocks():
    """every wall block: (centre, half size, colour, appear time or None, id)"""
    out = []; n = 0; zc = sum(WALL_Z) / 2; hz = (WALL_Z[1] - WALL_Z[0]) / 2
    for c in range(6):
        y0 = c * COURSE; x = WALL_X[0] - (0.35 if c % 2 else 0.0)
        while x < WALL_X[1] - 1e-6:
            a, b = max(x, WALL_X[0]), min(x + 0.7, WALL_X[1]); x += 0.7
            segs = [(a, b)]
            for t0, t1 in TOWERS + ([(-GATE_X, GATE_X)] if c < 5 else []):          # cut out the towers + the gate opening
                nxt = []
                for s0, s1 in segs:
                    if s1 <= t0 or s0 >= t1: nxt.append((s0, s1)); continue
                    if s0 < t0: nxt.append((s0, t0))
                    if s1 > t1: nxt.append((t1, s1))
                segs = nxt
            for s0, s1 in segs:
                if s1 - s0 < 0.05: continue
                low = s1 <= LOW_X[1] + 1e-6 and c >= 3
                ap = (T_WALL + 0.05 * ((c - 3) * 3 + int((s0 - LOW_X[0]) / 0.7))) if low else None
                col = hd.shade(BLOCKC[int(hsh(n, 5) * 4)], 0.93 + 0.12 * hsh(n, 6))
                out.append(((0.5 * (s0 + s1), y0 + COURSE / 2, zc), (0.5 * (s1 - s0) - 0.01, COURSE / 2 - 0.01, hz), col, ap, n)); n += 1
    for i, (t0, t1) in enumerate(TOWERS):                                                    # gate towers (thicker, taller)
        for c in range(8):
            col = hd.shade(BLOCKC[int(hsh(n, 5) * 4)], 0.95 + 0.1 * hsh(n, 6))
            out.append(((0.5 * (t0 + t1), c * COURSE + COURSE / 2, sum(TOWER_Z) / 2), (0.5 * (t1 - t0) - 0.005, COURSE / 2 - 0.01, (TOWER_Z[1] - TOWER_Z[0]) / 2), col, None, n)); n += 1
    return out
BLOCKS = _blocks()
BOB_BLOCK = min((b for b in BLOCKS if abs(b[0][1] - 1.0) < 0.05 and b[0][0] < -1.4), key=lambda b: abs(b[0][0] + 1.9))   # the block Bob hammers (course 2)
BOB_X = BOB_BLOCK[0][0]
def merlons(done_low):
    Q = []; zc = sum(WALL_Z) / 2
    x = WALL_X[0]
    while x < WALL_X[1] - 0.2:
        inside_t = any(t0 - 0.05 < x + 0.15 < t1 + 0.05 for t0, t1 in TOWERS)
        if not inside_t and (done_low or x > LOW_X[1]):
            Q += hd.bx((x + 0.15, 2.4 + 0.15, zc), np.eye(3), (0.15, 0.15, 0.25), (162, 154, 140))
        x += 0.6
    for t0, t1 in TOWERS:
        for j in range(3): Q += hd.bx((t0 + 0.11 + j * 0.215, TOWER_H + 0.12, TOWER_Z[0] + 0.12), np.eye(3), (0.07, 0.12, 0.1), (162, 154, 140))
    return Q
def roof(c, s=1.0):
    """a pointed tower roof (cone of slate) - c = bottom centre"""
    return hd.lathe(tuple(c), np.eye(3), [(0.48 * s, 0.0), (0.52 * s, 0.04), (0.05, 1.05 * s)], 12, (92, 70, 120),
                    colfn=lambda i, j: (110, 84, 140) if i % 2 else (92, 70, 120))
ROOF_ON = V((0.5 * sum(TOWERS[1]), TOWER_H + 0.24, sum(TOWER_Z) / 2))
PORTAL = V((-3.6, 0.0, 6.75)); PORTAL_N = nz((0.85, 0.0, -0.5)); PORTAL_U = nz(np.cross((0, 1.0, 0), PORTAL_N))   # the white doorway (the level's entrance)
def portal():
    Q = []; R = np.column_stack([PORTAL_U, (0, 1.0, 0), PORTAL_N])
    for sd in (1, -1): Q += hd.bx(tuple(PORTAL + PORTAL_U * sd * 0.62 + V((0, 1.15, 0))), R, (0.1, 1.15, 0.14), (150, 142, 130))
    Q += hd.bx(tuple(PORTAL + V((0, 2.38, 0))), R, (0.74, 0.12, 0.16), (140, 132, 120))
    Q += hd.decal(tuple(PORTAL - PORTAL_N * 0.05 + V((0, 1.12, 0))), -PORTAL_N if False else PORTAL_N, (0, 1.0, 0), 1.04, 2.24, (255, 255, 255), emit=True, lift=0.0)
    return Q
CRANE = V((3.7, 0.0, 7.7)); CRANE_H = 5.6; JIB = 4.7
def crane_state(t):
    """(jib yaw, trolley radius, hook height, load: 'roof' / 'dragon' / None)"""
    u = TT(t)
    a_roof = ang_to(CRANE, ROOF_ON); r_roof = float(np.hypot(*(ROOF_ON - CRANE)[[0, 2]]))
    a_dr = ang_to(CRANE, DRAGON_AT); r_dr = float(np.hypot(*(DRAGON_AT - CRANE)[[0, 2]]))
    if u < T_ROOF[0]:
        s = sm(seg01(u, -3.0, T_ROOF[0] - 0.3)); return lerp(a_roof + 1.0, a_roof, s), lerp(r_roof + 0.6, r_roof, s), lerp(4.7, ROOF_ON[1] + 1.45, sm(seg01(u, T_ROOF[0] - 1.6, T_ROOF[0]))), 'roof'
    if u < T_ROOF[1]:
        return a_roof, r_roof, lerp(ROOF_ON[1] + 1.45, ROOF_ON[1] + 1.1, sm(seg01(u, *T_ROOF))), ('roof' if u < T_ROOF[1] - 0.05 else None)
    if u < T_DRAGON[0] - 1.4:                                                  # swings away behind the wall (off camera) and back with the dragon
        s = sm(seg01(u, T_ROOF[1], T_DRAGON[0] - 1.4)); return lerp(a_roof, a_roof + 0.9, s), lerp(r_roof, 2.5, s), lerp(ROOF_ON[1] + 1.1, 4.3, s), (None if s < 0.5 else 'dragon')
    if u < T_DRAGON[0]:
        s = sm(seg01(u, T_DRAGON[0] - 1.4, T_DRAGON[0])); return lerp(a_roof + 0.9, a_dr, s), lerp(2.5, r_dr, s), 4.3, 'dragon'
    if u < T_DRAGON[1]:
        return a_dr, r_dr, lerp(4.3, PLINTH_H + DR_H + 0.35, sm(seg01(u, *T_DRAGON))), 'dragon'
    s = sm(seg01(u, T_DRAGON[1] + 0.1, T_DRAGON[1] + 1.5)); return lerp(a_dr, a_dr + 0.4, s), r_dr, lerp(PLINTH_H + DR_H + 0.35, 4.2, s), None
def crane(t):
    a, r, hy, load = crane_state(t); Q = []; c = CRANE; m = 0.18
    for dx, dz in ((m, m), (-m, m), (m, -m), (-m, -m)): Q += hd.limb(tuple(c + V((dx, 0, dz))), tuple(c + V((dx, CRANE_H, dz))), 0.03, 0.03, (226, 176, 40), n=5, m=1)
    for i in range(9):                                                         # lattice braces
        y0 = i * CRANE_H / 9; y1 = y0 + CRANE_H / 9
        for (ax, az), (bx_, bz) in (((m, m), (-m, m)), ((m, -m), (m, m)), ((-m, -m), (m, -m)), ((-m, m), (-m, -m))):
            Q += hd.limb(tuple(c + V((ax, y0, az))), tuple(c + V((bx_, y1, bz))), 0.015, 0.015, (206, 160, 36), n=4, m=1)
    d = V((math.sin(a), 0, math.cos(a))); top = c + V((0, CRANE_H, 0))
    Q += hd.bx(tuple(top + V((0, 0.25, 0))), hd.Ry(a), (0.32, 0.25, 0.32), (226, 176, 40))                       # the cab
    Q += hd.decal(tuple(top + V((0, 0.3, 0)) + d * 0.325), d, (0, 1, 0), 0.4, 0.26, (200, 230, 250), emit=False, lift=0.0)
    Q += hd.limb(tuple(top + V((0, 0.12, 0))), tuple(top + V((0, 0.12, 0)) + d * JIB), 0.07, 0.05, (226, 176, 40), n=4, m=1, ref=(0, 1, 0))
    Q += hd.limb(tuple(top + V((0, 0.12, 0))), tuple(top + V((0, 0.12, 0)) - d * 1.5), 0.08, 0.08, (226, 176, 40), n=4, m=1, ref=(0, 1, 0))
    Q += hd.bx(tuple(top + V((0, -0.05, 0)) - d * 1.35), hd.Ry(a), (0.3, 0.25, 0.25), (130, 128, 124))           # counterweight
    tr = top + V((0, 0.05, 0)) + d * r; hook = V((tr[0], hy, tr[2]))
    Q += hd.limb(tuple(tr), tuple(hook), 0.008, 0.008, (50, 46, 44), n=4, m=1) + hd.bx(tuple(tr), hd.Ry(a), (0.12, 0.06, 0.1), (90, 86, 80))
    Q += hd.ellip(tuple(hook), np.eye(3), (0.04, 0.05, 0.04), 6, 4, (70, 66, 60))
    if load == 'roof':
        for sd in (1, -1): Q += hd.limb(tuple(hook), tuple(hook + V((sd * 0.3, -0.42, 0))), 0.006, 0.006, (50, 46, 44), n=4, m=1)
        Q += roof(hook - V((0, 1.45, 0)))
    if load == 'dragon':
        for sd in (1, -1):
            for sz in (1, -1): Q += hd.limb(tuple(hook), tuple(hook + V((sd * 0.25, -0.35, sz * 0.4))), 0.006, 0.006, (50, 46, 44), n=4, m=1)
        Q += dragon_statue(hook - V((0, DR_H + 0.35, 0)))
    return Q, hook, load
def roof_placed(t): u = TT(t); return u >= T_ROOF[1] - 0.05
# ---- the dragon statue (the HD dragon, in stone, small) ----
DRAGON_AT = V((2.45, 0.0, 3.55)); PLINTH_H = 0.45
_DR = None; DR_H = 0.0
def _dragon_faces():
    global _DR, DR_H
    if _DR is None:
        P = dict(dtx.dragon_pose(0.0)); P['base'] = (0.0, 0.0, 0.0); P['yaw'] = 0.0
        Q = dtx.dragon(P); pts = np.array([p for q in Q for p in q['p']]); lo, hi = pts.min(0), pts.max(0); c = (lo + hi) / 2; s = 1.9 / (hi[2] - lo[2])
        out = []
        for q in Q:
            g = sum(q['col']) / 3; col = (int(g * 0.55 + 70), int(g * 0.55 + 68), int(g * 0.55 + 64))
            f = hd.face([tuple((V(p) - V((c[0], lo[1], c[2]))) * s) for p in q['p']], col)
            if f: out.append(f)
        _DR = out; DR_H = (hi[1] - lo[1]) * s
    return _DR
_dragon_faces()
DR_YAW = -2.3
def dragon_statue(c):
    R = hd.Ry(DR_YAW); c = V(c, float); out = []
    for q in _dragon_faces():
        f = hd.face([tuple(c + R @ V(p)) for p in q['p']], q['col'])
        if f: out.append(f)
    return out
def dragon_placed(t): u = TT(t); return u >= T_DRAGON[1]
# ---- props ----
TORCH_POS = [V((-3.65, 0.0, z)) for z in (1.4, 2.55, 3.7, 4.85)]
def torch_k(i, t):
    u = TT(t); a = T_TORCH + 0.15 * i
    if u < a: return 0.0
    return 0.9 * back(seg01(u, a, a + 0.25), 2.5) if u < a + 0.25 else 0.9
def torch_posts():
    Q = []
    for p in TORCH_POS:
        Q += hd.limb(tuple(p), tuple(p + V((0, 1.3, 0))), 0.045, 0.035, (92, 70, 52), n=6, m=1)
        Q += hd.lathe(tuple(p + V((0, 1.28, 0))), np.eye(3), [(0.05, 0.0), (0.11, 0.12), (0.12, 0.14)], 8, (70, 64, 60))
    return Q
TREES = [(-2.2, 7.5, 3.6), (-0.2, 8.1, 4.2), (1.7, 7.9, 3.4), (-4.05, 0.4, 2.8), (4.1, 0.6, 3.0), (4.15, 2.3, 2.6)]
def tree_s(i, t):
    u = TT(t); a = T_TREES[i]
    return 0.0 if u < a else back(seg01(u, a, a + 0.22), 2.2)
def tree_faces(i, s):
    x, z, h = TREES[i]; Q = dtx.tree(x, z, h, col=(70, 130, 70), trunk=(96, 70, 48), seed=i)
    if s >= 0.999 and s <= 1.001: return Q
    b = V((x, 0.0, z)); out = []
    for q in Q:
        f = hd.face([tuple(b + (V(p) - b) * V((s, s, s))) for p in q['p']], q['col'])
        if f: out.append(f)
    return out
CHEST_AT = V((-0.95, 0.0, 3.25)); CHEST_YAW = PI + 0.3          # its front (and the mimic's eyes) toward the courtyard
def chest_y(t):
    u = TT(t)
    if u < T_CHEST: return None
    a = seg01(u, T_CHEST, T_CHEST + 0.32)
    if a < 1: return 3.2 * (1 - a * a)
    b = seg01(u, T_CHEST + 0.32, T_CHEST + 0.52); return 0.12 * math.sin(PI * b)
def chest(t, y):
    """the mimic: a plain treasure chest... with an eye that opens and winks; teeth peek out of the lid seam"""
    c = CHEST_AT + V((0, y, 0)); R = hd.Ry(CHEST_YAW); Q = []
    def L(p): return tuple(c + R @ V(p))
    Q += hd.bx(L((0, 0.2, 0)), R, (0.36, 0.2, 0.25), WOOD)
    for x in (-0.24, 0.24): Q += hd.bx(L((x, 0.2, 0)), R, (0.035, 0.205, 0.255), (96, 90, 84))
    Q += hd.loft([V(L((-0.37, 0.4, 0))), V(L((0.37, 0.4, 0)))], [R @ V((0, 0, 1.0))] * 2, [R @ V((0, 1.0, 0))] * 2, [(0.255, 0.16), (0.255, 0.16)], 10,
                 hd.shade(WOOD, 1.06), th0=0.0, th1=PI)
    Q += hd.bx(L((0, 0.37, 0.26)), R, (0.06, 0.07, 0.015), (226, 190, 80))                                             # lock plate
    u = TT(t); e = win(u, T_WINK - 0.25, T_WINK + 1.6, 0.12)
    if e > 0:                                                                                                          # the mimic's eye on the lid + teeth
        for sd in (1, -1):
            closed = sd > 0 and T_WINK <= u < T_WINK + 0.28
            ec = L((sd * 0.14, 0.5, 0.2)); n_ = R @ V((0, 0.45, 1.0)); n_ = nz(n_)
            if closed: Q += hd.decal(ec, n_, R @ V((0, 1.0, 0)), 0.13 * e, 0.025, (30, 20, 20), lift=0.008)
            else:
                Q += hd.decal(ec, n_, R @ V((0, 1.0, 0)), 0.12 * e, 0.09 * e, (250, 244, 220), lift=0.006)
                Q += hd.decal(tuple(V(ec) + n_ * 0.004), n_, R @ V((0, 1.0, 0)), 0.045 * e, 0.06 * e, (30, 20, 20), lift=0.006)
        for i in range(7):
            x = -0.3 + 0.1 * i; Q.append(hd.face([L((x - 0.04, 0.4, 0.258)), L((x + 0.04, 0.4, 0.258)), L((x, 0.4 - 0.06 * e, 0.258))], (246, 240, 226)))
    return [q for q in Q if q]
POT_BIG = V((-1.12, 0.0, 5.5)); POTS_SMALL = [V((-1.72, 0.0, 5.62)), V((-1.62, 0.0, 5.2))]
CLAY = (186, 112, 70); CLAY_D = (150, 86, 54)
def pot(c, s=1.0):
    prof = [(0.2 * s, 0.0), (0.33 * s, 0.22 * s), (0.36 * s, 0.4 * s), (0.28 * s, 0.62 * s), (0.2 * s, 0.72 * s), (0.23 * s, 0.78 * s)]
    return hd.lathe(tuple(c), np.eye(3), prof, 14, CLAY, colfn=lambda i, j: CLAY_D if j == 2 else CLAY, cap1=False) + \
        hd.poly_decal(tuple(V(c) + V((0, 0.77 * s, 0))), (0, 1.0, 0), (0, 0, 1.0), [(0.2 * s * math.cos(a), 0.2 * s * math.sin(a)) for a in np.linspace(0, 2 * PI, 13)[:-1]], (40, 26, 18), lift=0.0)
_POTQ = None
def shards(t):
    """the big pot after the smash: its faces fly out, spin and settle on the floor"""
    global _POTQ
    if _POTQ is None: _POTQ = pot(POT_BIG, 1.0)
    u = TT(t) - T_SMASH; out = []
    for i, q in enumerate(_POTQ):
        P_ = [V(p) for p in q['p']]; c = sum(P_) / len(P_); d = nz(V((c[0] - POT_BIG[0], 0.0, c[2] - POT_BIG[2])) + V((0, 0.2, 0)))
        sp = 1.6 + 1.4 * hsh(i, 11); tt_ = min(u, 0.9); off = d * sp * tt_ * (1 - 0.35 * tt_) + V((0, 2.2 * tt_ - 4.9 * tt_ * tt_, 0))
        ang = (3 + 5 * hsh(i, 12)) * tt_; Rr = hd.Rx(ang) @ hd.Rz(ang * 0.7)
        pts = [c + off + Rr @ (p - c) * 0.9 for p in P_]
        ymin = min(p[1] for p in pts)
        if ymin < 0.01: pts = [p + V((0, 0.01 - ymin, 0)) for p in pts]
        f = hd.face([tuple(p) for p in pts], q['col'])
        if f: out.append(f)
    return out
PLANKS_PILE = V((1.05, 0.0, 5.55))
PLANK_Y = [(0.12, 0.44), (0.48, 0.8), (0.84, 0.96), (1.07, 1.39), (1.43, 1.75), (1.79, 1.98)]   # the gap 0.96-1.07 = the door goblin's eyes
def planks(mode, u=1.0):
    """'pile' leaning on the tower, 'door' held in the gate, 'open' swung aside like a door"""
    Q = []
    for i, (y0, y1) in enumerate(PLANK_Y):
        col = hd.shade(WOOD, 0.9 + 0.18 * hsh(i, 3))
        if mode == 'pile':
            c = PLANKS_PILE + V((0.0, 0.08 + 0.05 * i, -0.02 * i)); R = hd.Ry(PI / 2) @ hd.Rz(0.05 * i)
            Q += hd.bx(tuple(c), R, (0.66, 0.025, (y1 - y0) / 2), col)
        else:
            ang = 0.0 if mode == 'door' else -1.45 * u
            hinge = V((0.68, 0.0, 5.97)); R = hd.Ry(ang)
            c = hinge + R @ V((-0.68, (y0 + y1) / 2, 0.0))
            Q += hd.bx(tuple(c), R, (0.67, (y1 - y0) / 2, 0.022), col)
            for x in (-1.3, -0.06):
                Q += hd.decal(tuple(hinge + R @ V((x, (y0 + y1) / 2, -0.024))), R @ V((0, 0, -1.0)), (0, 1, 0), 0.014, 0.014, (70, 60, 50), lift=0.002)
    return Q
BOARD = V((-2.75, 0.0, 3.05)); BOARD_N = nz((0.55, 0.0, -1.0)); BOARD_U = nz(np.cross(BOARD_N, (0, 1.0, 0)))   # the viewer's right, looking at the sheet
def tip_board():
    """an easel with a big paper sheet (the text goes on in 2D, mapped onto the sheet)"""
    Q = []; R = np.column_stack([BOARD_U, (0, 1.0, 0), BOARD_N])
    for sd in (1, -1): Q += hd.limb(tuple(BOARD + BOARD_U * sd * 0.38 - BOARD_N * 0.05), tuple(BOARD + BOARD_U * sd * 0.3 + V((0, 1.45, 0))), 0.025, 0.02, WOOD_D, n=5, m=1)
    Q += hd.limb(tuple(BOARD - BOARD_N * 0.45), tuple(BOARD + V((0, 1.35, 0)) - BOARD_N * 0.04), 0.022, 0.02, WOOD_D, n=5, m=1)   # the back leg
    Q += hd.bx(tuple(BOARD + V((0, 1.0, 0))), R, (0.47, 0.37, 0.02), WOOD)
    Q += hd.decal(tuple(BOARD + V((0, 1.0, 0)) - BOARD_N * 0.0 + BOARD_N * 0.025), BOARD_N, (0, 1, 0), 0.86, 0.66, (246, 242, 230), lift=0.0)
    return Q
def board_corners():
    c = BOARD + V((0, 1.0, 0)) + BOARD_N * 0.03; u = BOARD_U * 0.43; v = V((0, 0.33, 0))
    return [c - u + v, c + u + v, c + u - v, c - u - v]                # TL TR BR BL as seen from the front
def scaffold():
    Q = []
    for x in (1.75, 2.85, 3.95):
        for z in (5.35, 5.9): Q += hd.limb((x, 0, z), (x, 2.75, z), 0.03, 0.03, WOOD_D, n=5, m=1)
    for y in (1.3, 2.5):
        for z in (5.35, 5.9): Q += hd.limb((1.7, y, z), (4.0, y, z), 0.022, 0.022, WOOD_D, n=4, m=1)
    for i in range(5): Q += hd.bx((1.95 + 0.42 * i, 1.33, 5.63), np.eye(3), (0.2, 0.025, 0.32), hd.shade(WOOD, 0.92 + 0.1 * (i % 2)))
    for i in range(3): Q += hd.bx((3.3 + 0.0 * i, 1.38 + 0.21 * i, 5.62), hd.Ry(0.2 * i), (0.3, 0.1, 0.2), BLOCKC[i])
    return Q
def floor_set():
    Q = dtx.ground(-4.5, 4.5, -0.6, 8.7, 0.6, STONE, seed=31)
    Q += hd.bx((0, -0.36, 4.05), np.eye(3), (4.5, 0.35, 4.65), (150, 140, 126))
    for i in range(9):                                                         # the island's broken underside
        x = -4.0 + 8.0 * hsh(i, 41); z = -0.2 + 8.6 * hsh(i, 42); r = 0.6 + 0.8 * hsh(i, 43)
        Q += hd.lathe((x, -0.7, z), hd.Rx(PI), [(r, 0.0), (r * 0.5, 0.8 + 1.4 * hsh(i, 44)), (0.05, 1.4 + 1.6 * hsh(i, 45))], 7, (136, 126, 112))
    for x, z in ((-2.6, 2.2), (1.5, 1.6), (3.2, 4.3)):                         # stacks of spare blocks
        for j in range(2): Q += hd.bx((x + 0.05 * j, 0.2 + 0.4 * j, z), hd.Ry(0.3 * j), (0.32, 0.2, 0.24), BLOCKC[j + 1])
    Q += hd.bx(tuple(DRAGON_AT + V((0, PLINTH_H / 2, 0))), hd.Ry(DR_YAW), (0.55, PLINTH_H / 2, 0.85), (160, 152, 140))
    Q += hd.bx((BOB_X, 0.25, 6.85), np.eye(3), (0.3, 0.25, 0.25), WOOD)    # Bob's crate behind the low wall
    return Q
def void_set(zc):
    """the unloaded world: a white dome and a faint grid far below"""
    Q = hd.ellip((0, -6, zc), np.eye(3), (110, 80, 110), 16, 7, VOIDC, v1=PI * 0.62, closed=False)
    for q in Q: q['emit'] = True
    for i in range(-8, 9):
        x = i * 3.0; q = hd.face([(x - 0.04, -6.0, -30), (x - 0.04, -6.0, 50), (x + 0.04, -6.0, 50), (x + 0.04, -6.0, -30)], (206, 212, 228), emit=True)
        if q: Q.append(q)
    for j in range(-10, 17):
        z = j * 3.0; q = hd.face([(-30, -6.0, z - 0.04), (-30, -6.0, z + 0.04), (30, -6.0, z + 0.04), (30, -6.0, z - 0.04)], (206, 212, 228), emit=True)
        if q: Q.append(q)
    return Q
_STATIC = None
def static_set():
    global _STATIC
    if _STATIC is None: _STATIC = floor_set() + portal() + torch_posts() + scaffold() + tip_board()
    return _STATIC
_WALLQ = {}
def wall_faces(t):
    """wall blocks; the low stretch pops in on "Faster!" (squash pop); cached once it is complete"""
    u = TT(t); key = 'done' if u >= T_WALL + 0.6 else ('start' if u < T_WALL else None)
    if key in _WALLQ: return _WALLQ[key]
    Q = []
    for c, h_, col, ap, n in BLOCKS:
        if ap is not None:
            if u < ap: continue
            s = back(seg01(u, ap, ap + 0.18), 2.0); h_ = (h_[0] * s, h_[1] * s, h_[2] * s)
        Q += hd.bx(c, np.eye(3), h_, col)
    Q += merlons(u >= T_WALL + 0.45)
    Q += roof(V((0.5 * sum(TOWERS[0]), TOWER_H + 0.24, sum(TOWER_Z) / 2)))
    if key: _WALLQ[key] = Q
    return Q

# ======================= cast =======================
GOB_SKIN = (124, 166, 78)
def gob_spec(skin, tunic, pants=(86, 72, 58), h=1.1, build=1.0):
    return hd.spec(h=h, build=build, skin=skin, hair=skin, hair_style='bald', eye=(236, 196, 60), brow=hd.shade(skin, 0.55), lip=hd.shade(skin, 0.7),
                   tunic=tunic, tunic2=hd.shade(tunic, 0.82), sleeves='short', skirt=0.12, pants=pants, boots=(70, 52, 38), belt=(70, 50, 32), buckle=(200, 176, 96))
BOB = gob_spec(GOB_SKIN, (232, 124, 40), h=1.12, build=1.08)                          # orange vest: the foreman
G1 = gob_spec((112, 154, 76), (70, 98, 156), h=1.04, build=0.92)                    # the worried one (talks)
G2 = gob_spec((138, 160, 86), (132, 88, 54), h=1.1)                                 # the door
G3 = gob_spec((100, 146, 96), (156, 64, 52), h=1.08)                                # the other statue
G4 = gob_spec((128, 150, 80), (96, 110, 130), h=1.05)                               # crane operator (in the cab)
HAT_Y = (244, 196, 44); HAT_W = (244, 242, 236)
HS = 1.32                                                                            # chibi-lite head scale
def goblin_parts(S_, P, hat=HAT_Y, hat_off=None, pencil=False):
    """big pointed ears, a long nose, the hard hat (above the brows: the eyes stay visible)"""
    hc = P['_head']; RH = P['_RH']; k = P['_hk']; sk = S_['skin']; Q = []
    def L(x, y, z, R=RH): return hc + R @ V((x * k, y * k, z * k))
    for sd in (1, -1):
        b0 = L(sd * 0.082, 0.035, -0.012); b1 = L(sd * 0.082, -0.03, 0.008); tp = L(sd * 0.235, 0.075, -0.05); md = L(sd * 0.15, 0.03, -0.03)
        for pts in ([b0, b1, tp], [b1, b0, tp]):
            q = hd.face(pts, sk if pts[0] is b0 else hd.shade(sk, 0.85))
            if q: Q.append(q)
        for pts in ([L(sd * 0.09, 0.02, -0.004), L(sd * 0.09, -0.012, 0.004), md], [L(sd * 0.09, -0.012, 0.004), L(sd * 0.09, 0.02, -0.004), md]):
            q = hd.face([V(p) + RH @ V((sd * 0.002, 0, 0.003)) for p in pts], hd.mix(sk, (150, 80, 80), 0.35))
            if q: Q.append(q)
    Q += hd.limb(tuple(L(0, -0.012, 0.094)), tuple(L(0, -0.034, 0.168)), 0.017 * k, 0.006 * k, hd.shade(sk, 0.96), n=7, m=1)   # long nose
    if hat is not None:
        Rh = RH if hat_off is None else hat_off[0]; hc_h = hc if hat_off is None else hat_off[1]
        def Lh(x, y, z): return hc_h + Rh @ V((x * k, y * k, z * k))
        Q += hd.ellip(tuple(Lh(0, 0.058, -0.004)), Rh, (0.1 * k, 0.088 * k, 0.112 * k), 12, 5, hat, v1=PI * 0.5,
                      colfn=lambda i, j, cl: hd.shade(hat, 0.86) if i % 6 == 0 else hat)
        Q += hd.lathe(tuple(Lh(0, 0.052, 0.0)), Rh, [(0.122 * k, 0.0), (0.118 * k, 0.012 * k)], 14, hd.shade(hat, 0.92))
        Q += hd.limb(tuple(Lh(0, 0.146, -0.07)), tuple(Lh(0, 0.146, 0.07)), 0.012 * k, 0.012 * k, hd.shade(hat, 0.82), n=5, m=1)   # ridge
        if hat == HAT_W: Q += hd.ellip(tuple(Lh(0, 0.062, -0.004)), Rh, (0.101 * k, 0.03 * k, 0.113 * k), 12, 3, (210, 60, 40), v0=PI * 0.42, v1=PI * 0.5)
    if pencil:
        Q += hd.limb(tuple(L(0.1, 0.035, -0.035)), tuple(L(0.2, 0.065, 0.02)), 0.007 * k, 0.007 * k, (240, 200, 60), n=5, m=1)
        Q += hd.limb(tuple(L(0.2, 0.065, 0.02)), tuple(L(0.225, 0.07, 0.035)), 0.007 * k, 0.001, (60, 50, 40), n=5, m=1)
    return [q for q in Q if q]
def goblin(S_, P, **kw):
    P['head_scale'] = HS; Q = hd.human(S_, P); return Q + goblin_parts(S_, P, **kw)
KN = dtx.KNIGHT
def knight(P): return dtx.knight(P)
def silhouette(Q, col=(34, 34, 46)):
    for q in Q: q['col'] = col; q['emit'] = True
    return Q
# ---- hand-held props ----
def hammer(grip, d, up):
    """d = handle direction (from the fist to the head), up = the striking face normal side"""
    grip = V(grip, float); d = nz(d); head = grip + d * 0.24
    Q = hd.limb(tuple(grip - d * 0.06), tuple(head), 0.013, 0.012, (140, 96, 56), n=6, m=1)
    side = nz(np.cross(d, up)); fwd = nz(np.cross(side, d))
    Q += hd.limb(tuple(head - fwd * 0.07), tuple(head + fwd * 0.06), 0.032, 0.032, (110, 112, 118), n=8, m=1, ref=tuple(side))
    return Q, head + fwd * 0.07
def clipboard_quad(c, nrm, upv, w=0.2, h=0.27):
    nrm = nz(nrm); upv = nz(upv - nrm * (upv @ nrm)); rt = nz(np.cross(nrm, upv))       # rt = the viewer's right when the sheet faces them
    return [c - rt * w / 2 + upv * h / 2, c + rt * w / 2 + upv * h / 2, c + rt * w / 2 - upv * h / 2, c - rt * w / 2 - upv * h / 2]
def clipboard(quad, nrm):
    tl, tr, br, bl = [V(p) for p in quad]; n_ = nz(nrm); c = (tl + br) / 2
    Q = [hd.face([tuple(p - n_ * 0.008) for p in (tl, tr, br, bl)], (130, 90, 56)), hd.face([tuple(p - n_ * 0.008) for p in (bl, br, tr, tl)], (110, 76, 46))]
    m = (tl + tr) / 2; Q += hd.bx(tuple(m + n_ * 0.006 - nz(tl - bl) * 0.01), np.column_stack([nz(tr - tl), nz(tl - bl), n_]), (0.04, 0.012, 0.008), (170, 172, 180))
    return [q for q in Q if q]
def stamp_tool(grip, d):
    d = nz(d); return hd.limb(tuple(grip - d * 0.03), tuple(grip + d * 0.08), 0.018, 0.022, (150, 60, 40), n=6, m=1) + \
        hd.bx(tuple(grip + d * 0.1), rot_y(d), (0.04, 0.02, 0.03), (60, 40, 30))
def coin3(c, R=None): return dtx.coin(V(c, float), np.eye(3) if R is None else R, 1.0)

# ----------------------- performances -----------------------
A = body.arm
def G_(**kw): return dict(kw)
GRIP = hands.pose('grip', r=0.03) if 'grip' in hands.PRESETS else 'fist'
# Bob: custom gestures (chest frame, 1.78 m scale; Performer scales them)
CLUTCH = G_(r=A(0.2, -0.3, 0.2, palm=(-1, 0, 0.2), fingers='fist'), l=dict(hc=(-0.06, -0.12, 0.3), palm_c=(0.3, 0, 1), pole_c=(-1, -0.5, 0.2), fingers='fist', wrist=(0.0, 0.0), shrug=(0.03, 0.0)),
            face='scared')
WRITE = G_(r=A(0.12, -0.08, 0.42, palm=(0, -0.6, 1), pole=(1, -1, -0.3), fingers='fist'), l=dict(hc=(-0.24, -0.42, 0.08), palm_c=(1, 0, 0.2), pole_c=(-0.5, -0.3, -1), fingers='relaxed', wrist=(0.0, 0.0), shrug=(0.0, 0.0)),
            lean=0.12, head=(0.0, 0.12, 0.0), face='determined')
POINT_HOLD = G_(r=A(0.28, 0.1, 0.48, palm=(0, -1, 0), pole=(1, -0.8, -0.2), fingers='point'), l=dict(hc=(-0.1, -0.15, 0.28), palm_c=(0.3, 0, 1), pole_c=(-1, -0.5, 0.2), fingers='fist', wrist=(0.0, 0.0), shrug=(0.0, 0.0)),
                face='angry')
COIN_UP = G_(r=A(0.16, 0.12, 0.32, palm=(0, 1, 0.2), pole=(1, -1, -0.3), fingers='fist'), l=dict(hc=(-0.2, -0.32, 0.2), palm_c=(1, 0, 0.3), pole_c=(-1, -0.4, -0.6), fingers='relaxed', wrist=(0.0, 0.0), shrug=(0.04, 0.0)),
             crouch=0.0, head=(0.0, -0.08, 0.1), face=('embarrassed', dict(smR=0.5, smL=0.5)))
STAMP_HOLD = G_(r=A(0.1, 0.08, 0.36, palm=(0, -1, 0.1), pole=(1, -1, -0.3), fingers='fist'), l=dict(hc=(-0.06, -0.12, 0.32), palm_c=(0.3, 0, 1), pole_c=(-1, -0.5, 0.2), fingers='fist', wrist=(0.0, 0.0), shrug=(0.0, 0.0)),
                face='smug')
CLIP_L = dict(hc=(-0.1, -0.3, 0.3), palm_c=(1.0, 0.0, 0.3), pole_c=(-1, -0.5, -0.3), fingers='fist', wrist=(0.0, 0.0), shrug=(0.0, 0.0))   # clipboard held low in front
JUMP_SHOCK = G_(r=A(0.3, 0.42, 0.2, palm=(-1, 0, 0), pole=(1, -0.5, -0.5), fingers='fist'), l=CLIP_L, lean=-0.1, head=(0.0, -0.1, 0.0), face='shocked')
JUMP_WAVE = G_(r=A(0.34, 0.52, 0.16, palm=(-1, 0, 0), pole=(1, -0.5, -0.5), fingers='fist'), l=CLIP_L, lean=-0.05, face=('angry', dict(open=0.6)), osc=[('rhc', 0, 0.05, 3.2)])
SCRATCH = dict(body.GESTURES['scratch_head']); SCRATCH['r'] = A(0.15, 0.5, 0.0, palm=(-1, -0.5, 0), pole=(1, 0.2, 0.4), fingers='claw')   # the goblin head is 32 % bigger
DOOR_HOLD = G_(**body.both(A(0.3, -0.12, 0.22, palm=(0, 0, 1), pole=(1, -0.6, -0.4), fingers='open')), face='deadpan')
STATUE_A = G_(r=A(0.3, 0.55, 0.12, palm=(-1, 0, 0), pole=(1, 0, -0.5), fingers='fist'), l=A(-0.0, -0.33, 0.0) if False else body.mirror(A(0.21, -0.33, 0.0, palm=(-1, -0.2, 0.3), pole=(1, 0.0, -0.8), fingers='relaxed', wrist=(-0.5, 0.0))),
              head=(0.25, -0.12, 0.0), face=('proud', dict(eyesR=1.05, eyesL=1.05)))
STATUE_B = G_(r=A(0.36, 0.22, 0.3, palm=(0, -1, 0), pole=(1, -0.8, -0.2), fingers='point'), l=body.mirror(A(0.25, -0.46, 0.04)), lean=0.08, head=(-0.2, -0.05, 0.0),
              face=('determined', dict(eyesR=1.0, eyesL=1.0)))
# Bob's whole performance (absolute build times; times before 0 belong to the loop's run-in)
BOB_PERF = body.Performer(BOB, [(-5.0, 'idle', dict(face=('determined', dict(press=0.9)))), (T_JUMP, JUMP_SHOCK, dict(blend=0.14)), (ws('01', 1) - 0.1, JUMP_WAVE, dict(blend=0.18)),
                                (S_TIP - 0.4, WRITE, dict(blend=0.2)), (S_MONT - 0.2, POINT_HOLD, dict(blend=0.15)), (ws('04', 1) - 0.1, 'point_fwd', dict(blend=0.15)),
                                (ws('04', 2) - 0.1, POINT_HOLD, dict(blend=0.15)), (S_99 - 0.2, 'idle', dict(face='proud')), (T0['06'] - 0.25, 'cheer', dict(blend=0.4)),
                                (T_LOOK - 0.1, 'idle', dict(face='shocked', blend=0.5)), (S_100 + 0.2, 'idle', dict(face=('shocked', dict(eyesR=1.3, eyesL=1.3)))),
                                (T0['08'] - 0.12, 'point_fwd', dict(face='angry', blend=0.24)), (T_DIVE[0] + 0.3, 'hands_up', dict(blend=0.15)),
                                (T_SMASH + 0.12, COIN_UP, dict(blend=0.25)), (T_TAKE[1] + 0.05, 'slump', dict(face=('sad', dict(eyesR=0.7, eyesL=0.7)), blend=0.25)),
                                (T_STAMP - 0.3, STAMP_HOLD, dict(blend=0.2)), (T_RESET - 0.2, 'idle', dict(face=('determined', dict(press=0.9))))], seed=3)
G1_PERF = body.Performer(G1, [(-5.0, 'idle', dict(face='neutral')), (T_CHEST + 0.3, 'shocked', dict(blend=0.15)), (T_WINK + 0.05, SCRATCH, dict(face='scared', blend=0.4)),
                              (T0['05'] + 0.2, body.point_at(G1, CHEST_AT + V((0, 0.4, 0)), (-1.55, 0, 2.75), ang_to((-1.55, 0, 2.75), CHEST_AT), face='scared'), dict(blend=0.2)),
                              (S_99 - 0.2, 'idle', dict(face='laughing')), (T0['06'] - 0.05, 'cheer', dict(blend=0.4)), (T_LOOK - 0.05, 'idle', dict(face='scared', blend=0.5)),
                              (T0['07'] + 0.1, SCRATCH, dict(face='sad', blend=0.55)), (T_DIVE[0] + 0.4, STATUE_A, dict(blend=0.35)), (T_RESET - 0.2, 'idle', dict(face='neutral'))], seed=5)
G2_PERF = body.Performer(G2, [(-5.0, 'idle', dict(face='determined')), (S_99 - 0.2, 'idle', dict(face='laughing')), (T0['06'], 'cheer', dict(blend=0.4)),
                              (T_LOOK, 'idle', dict(face='shocked', blend=0.5)), (T_DIVE[0] + 0.4, DOOR_HOLD, dict(blend=0.4)), (T_RESET - 0.2, 'idle', dict(face='determined'))], seed=7)
G3_PERF = body.Performer(G3, [(-5.0, 'idle', dict(face='determined')), (S_99 - 0.2, 'idle', dict(face='laughing')), (T0['06'] - 0.1, 'cheer', dict(blend=0.4)),
                              (T_LOOK - 0.02, 'idle', dict(face='shocked', blend=0.5)), (T_DIVE[0] + 0.45, STATUE_B, dict(blend=0.35)), (T_RESET - 0.2, 'idle', dict(face='determined'))], seed=9)
# ---- where everybody stands, per scene ----
BOB_WALL = V((BOB_X, 0.5, 6.85))                    # on his crate behind the low wall
BOB_TIP = BOARD + BOARD_U * 0.64 + BOARD_N * 0.2  # right of the tip board (as we look at it)
BOB_MONT = V((-0.15, 0.0, 2.35))
LINE_Z = 4.05
BOB_LINE = V((-0.55, 0.0, LINE_Z)); G1_LINE = V((-1.55, 0.0, LINE_Z - 0.1)); G2_LINE = V((0.45, 0.0, LINE_Z + 0.05)); G3_LINE = V((1.45, 0.0, LINE_Z - 0.05))
G1_MONT = V((-1.6, 0.0, 2.75)); G2_MONT = V((2.55, 0.0, 4.95)); G3_MONT = V((3.25, 0.0, 3.0))
G1_STATUE = V((-2.2, 0.0, 4.5)); G3_STATUE = V((1.75, 0.0, 4.55)); G2_DOOR = V((0.0, 0.0, 6.2))
def to_chest(P, S_, w_pt):
    """a world point in the chest frame of a pose (before hd.human runs): lets a hand target blend with the Performer's arm targets"""
    k = S_['h'] / 1.78; R = hd.Ry(P['yaw']); ch = V(P['base'], float) + R @ V((0.0, 1.33 * k - P.get('crouch', 0.0), 0.0)); return tuple(R.T @ (V(w_pt, float) - ch))
def blend_hc(P, key, tgt, w):
    if w <= 0: return
    P[key] = tuple(V(lerp3(tuple(P[key]), tuple(tgt), min(1.0, w))))
def hop_path(a, b, u, h=0.5):
    p = V(lerp3(tuple(a), tuple(b), sm(u))); return p + V((0, h * math.sin(PI * min(1.0, max(0.0, u))), 0))
def hammer_phase(u):
    """0 = up, 1 = struck (the block); impacts every 0.62 s, frame 0 = the hammer coming DOWN (impact at 0.06 s)"""
    per = 0.62; x = (u - 0.06) % per
    if x < 0.3: return max(0.0, 1 - x / 0.3) ** 2 * 0.0 + (1 - sm(x / 0.3))      # rebound up
    if x < per - 0.12: return 0.0
    return ((x - (per - 0.12)) / 0.12) ** 1.6                                   # fast strike
def hammer_impacts(t0, t1):
    out = []; per = 0.62; k0 = math.floor((t0 - 0.06) / per)
    for k_ in range(k0, k0 + int((t1 - t0) / per) + 3):
        x = 0.06 + k_ * per
        if t0 <= x < t1: out.append(x)
    return out
def bob_state(t):
    """(pose, extras) — extras: hammer / clip (quad mode) / stamp / coin / hat (world frame of the hat if off the head) / visible"""
    u = TT(t); sc = scene(t); X = dict(hammer=False, clip='belt', stamp=False, coin=False, hat=None, vis=True)
    talk = talk_any(t, ['01', '04', '06', '08', '11', '12'])
    P = BOB_PERF.at(u, talk=talk)
    P['base'] = tuple(BOB_WALL); P['yaw'] = PI
    if sc in ('open', 'loop', 'jump') or u < S_TIP:
        X['hammer'] = True; X['clip'] = 'belt'
        hp = hammer_phase(u) if u < T_JUMP else hammer_phase(T_JUMP) * (1 - sm(seg01(u, T_JUMP, T_JUMP + 0.2)))
        up_ = V((BOB_X - 0.2, 1.88, 6.72)); dn = V((BOB_X - 0.17, 1.42, 6.5))
        hand = V(lerp3(tuple(up_), tuple(dn), hp)); d = nz(V(lerp3((0.0, 0.75, 0.66), (0.0, -0.52, -0.85), hp)))
        w_ = 1 - sm(seg01(u, T_JUMP, T_JUMP + 0.3))                           # the hands go up in panic: the hammer rides along (blended, no snap)
        blend_hc(P, 'rhc', to_chest(P, BOB, hand), w_); blend_hc(P, 'lhc', to_chest(P, BOB, (BOB_X + 0.28, 1.25, 6.33)), w_)
        if w_ > 0.5: P['lpalm_c'] = (0.0, -1.0, 0.3)
        X['hdir'] = d; X['hdir_w'] = w_
        if u < T_JUMP: P['face'] = facemod.expr('determined', press=0.9, look=(0.0, -0.5))
        if u >= T_JUMP + 0.12 and u < S_DOOR: X['clip'] = 'chest'
        if T_JUMP <= u < T_JUMP + 0.75:                                       # the hat pops off and drops back, crooked
            a = seg01(u, T_JUMP, T_JUMP + 0.75); X['hat'] = ('pop', a)
        elif u >= T_JUMP + 0.75: X['hat'] = ('crooked', 1.0)
    elif sc == 'tip' or u < S_MONT:
        cp_ = cam_shot(S_TIP + 0.5)[0]; P['base'] = tuple(BOB_TIP); P['yaw'] = ang_to(BOB_TIP, cp_) - 0.95; X['hat'] = ('crooked', 1.0)   # 3/4 to us, writing beside him
        ph = (u - S_TIP) * 9.0; bc = BOARD + V((0, 1.0, 0)) + BOARD_N * 0.06
        if u >= T_TIPON - 0.1:
            wt = bc + BOARD_U * (0.3 + 0.05 * math.sin(ph)) + V((0, -0.06 + 0.035 * math.sin(ph * 1.7), 0)); X['pencil_hand'] = True
            blend_hc(P, 'rhc', to_chest(P, BOB, wt), sm(seg01(u, T_TIPON - 0.1, T_TIPON + 0.25)))
        if u >= T0['03'] + 0.2: P['face'] = facemod.expr('smug', look=(0.8, 0.1))                 # a sly look at the camera: "they're for them"
    elif sc == 'mont':
        P['base'] = tuple(BOB_MONT); X['clip'] = 'hand'; X['hat'] = ('crooked', 1.0)
        ks = [(S_MONT - 1.0, ang_to(BOB_MONT, CHEST_AT)), (ws('04', 1) - 0.1, ang_to(BOB_MONT, TORCH_POS[1])), (ws('04', 2) - 0.1, ang_to(BOB_MONT, DRAGON_AT)), (ws('04', 3) - 0.1, ang_to(BOB_MONT, V((-2.2, 0, 6.2))))]
        y_ = ks[0][1]
        for (ta, ya) in ks[1:]: y_ = lerp(y_, ya, sm(seg01(u, ta - 0.15, ta + 0.25)))
        P['yaw'] = y_ - 0.25
    elif sc == 'wide':
        P['base'] = tuple(BOB_LINE); X['clip'] = 'hand'; X['hat'] = ('crooked', 1.0)
        tr = sm(seg01(u, T_LOOK - 0.05, T_LOOK + 0.7)); P['yaw'] = lerp(PI, 0.15, tr)
    elif sc == 'twitch':
        P['base'] = tuple(BOB_LINE); X['clip'] = 'hand'; X['hat'] = ('crooked', 1.0)
        tr = sm(seg01(u, S_100 + 0.15, S_100 + 0.9)); P['yaw'] = lerp(0.15, PI, tr)                     # turns from the gate to us (the player)
        tw_ = (math.sin((u - S_100) * 38) > 0.3) and u > S_100 + 0.9
        P['face'] = facemod.expr('shocked', eyesR=1.3, eyesL=(0.55 if tw_ else 1.25), squintL=(0.8 if tw_ else 0.0), browL=(-0.6 if tw_ else 0.7), look=(0.0, 0.0))
    elif sc == 'places':
        X['clip'] = 'hand'; X['hat'] = ('crooked', 1.0)
        a = seg01(u, T_DIVE[0] + 0.25, T_DIVE[0] + 1.0); tgt = POT_BIG + V((0, 0.0, 0))
        b0 = V(BOB_LINE); P['base'] = tuple(hop_path(b0, tgt + V((0, 0.35, 0)), a, 0.9)); P['yaw'] = ang_to(b0, tgt) if a < 1 else PI
        if a > 0: P['crouch'] = 0.15 * math.sin(PI * a)
        if a >= 1: X['vis'] = False                                                                     # inside the pot
    elif sc in ('hero',):
        X['vis'] = False
    elif sc in ('pot', 'gate'):
        P['base'] = tuple(POT_BIG + V((0, 0.0, 0))); P['yaw'] = PI + 0.3; X['hat'] = ('crooked', 1.0)
        if u < T_SMASH: X['vis'] = False
        P['crouch'] = 0.3 * (1 - sm(seg01(u, T_STAMP - 0.4, T_STAMP)))
        if T_SMASH <= u < T_TAKE[0] + 0.25: X['coin'] = True
        if u >= T_STAMP - 0.35: X['clip'] = 'chest'; X['stamp'] = True
        else: X['clip'] = 'belt'
        if T0['11'] - 0.05 <= u < T_TAKE[0]: P['face'] = facemod.expr('embarrassed', smR=0.6, smL=0.6, look=(0.6, 0.15))
        if u >= T_STAMP - 0.3:                                               # stamp: wind up, SLAM onto the sheet, hold, lift a little
            k_ = BOB['h'] / 1.78; up_ = V((0.09, 0.1, 0.34)); dn_ = V((0.07, -0.02, 0.3))
            w1 = sm(seg01(u, T_STAMP - 0.3, T_STAMP - 0.08)); w2 = seg01(u, T_STAMP - 0.08, T_STAMP) ** 2; w3 = sm(seg01(u, T_STAMP + 0.35, T_STAMP + 0.6))
            hc_ = V(P['rhc']); a_ = V(lerp3(tuple(hc_), tuple(up_), w1)); a_ = V(lerp3(tuple(a_), tuple(dn_), w2)); a_ = V(lerp3(tuple(a_), (0.09, 0.03, 0.34), w3 * 0.6))
            P['rhc'] = tuple(a_); P['rpalm_c'] = (0.0, 0.0, -1.0)
    return P, X
def gob_simple(perf, S_, t, base, yaw, talkk=()):
    P = perf.at(TT(t), talk=talk_any(t, list(talkk))); P['base'] = tuple(base); P['yaw'] = yaw; return P
def g1_state(t):
    u = TT(t); sc = scene(t)
    if sc in ('open', 'loop', 'jump', 'door', 'tip') or u < S_MONT:
        P = gob_simple(G1_PERF, G1, t, (-0.6, 0.0, 4.6), PI + 0.6)                               # carrying a block to the wall (background)
        ph = (u % 3.0) / 3.0; P['base'] = tuple(V((-0.6, 0.0, 4.6)) + V((0.5 * math.sin(2 * PI * ph), 0, 0.2 * math.cos(2 * PI * ph))))
        return P, dict(carry=True)
    if sc == 'mont': P = gob_simple(G1_PERF, G1, t, G1_MONT, ang_to(G1_MONT, CHEST_AT), ('05',)); return P, {}
    if sc in ('wide', 'twitch'):
        P = gob_simple(G1_PERF, G1, t, G1_LINE, PI, ('07',)); tr = sm(seg01(u, T_LOOK, T_LOOK + 0.75)); P['yaw'] = lerp(PI, 0.1, tr); return P, {}
    a = seg01(u, T_DIVE[0] + 0.2, T_DIVE[0] + 0.75)
    P = gob_simple(G1_PERF, G1, t, hop_path(G1_LINE, G1_STATUE, a, 0.45), lerp(0.1, PI - 0.5, sm(a)))
    if sc in ('hero',) and u > T0['10'] + 0.4: P['face'] = facemod.expr('proud', look=(0.7, 0.0))      # its eyes follow the hero
    return P, {}
def g2_state(t):
    u = TT(t); sc = scene(t)
    if sc in ('open', 'loop', 'jump', 'door', 'tip') or u < S_99:
        P = gob_simple(G2_PERF, G2, t, G2_MONT, PI - 0.4); return P, dict(hammer_low=True)
    if sc in ('wide', 'twitch'):
        P = gob_simple(G2_PERF, G2, t, G2_LINE, PI); tr = sm(seg01(u, T_LOOK + 0.05, T_LOOK + 0.8)); P['yaw'] = lerp(PI, -0.1, tr); return P, {}
    a = seg01(u, T_DIVE[0] + 0.15, T_DIVE[0] + 0.8)
    if a < 1:
        P = gob_simple(G2_PERF, G2, t, hop_path(G2_LINE, G2_DOOR, a, 0.35), lerp(ang_to(G2_LINE, G2_DOOR), PI, sm(seg01(a, 0.55, 1.0))))
        return P, dict(planks='carry' if a > 0.35 else 'pile', a=a)
    P = gob_simple(G2_PERF, G2, t, G2_DOOR, PI, ('09',))
    if u >= T_LEAVE + 0.2:                                                                       # swings aside like a door for the hero
        o = sm(seg01(u, T_LEAVE + 0.2, T_LEAVE + 0.9)); P['base'] = tuple(G2_DOOR + V((0.42 * o, 0, -0.05 * o)))
        return P, dict(planks='open', a=o)
    return P, dict(planks='door', a=1.0)
def g3_state(t):
    u = TT(t); sc = scene(t)
    if sc in ('open', 'loop', 'jump', 'door', 'tip') or u < S_MONT:
        P = gob_simple(G3_PERF, G3, t, (2.4, 1.33, 5.62), PI); return P, dict(scaff=True)         # on the scaffold
    if sc == 'mont': P = gob_simple(G3_PERF, G3, t, G3_MONT, ang_to(G3_MONT, DRAGON_AT)); return P, dict(rope=True)
    if sc in ('wide', 'twitch'):
        P = gob_simple(G3_PERF, G3, t, G3_LINE, PI); tr = sm(seg01(u, T_LOOK + 0.02, T_LOOK + 0.75)); P['yaw'] = lerp(PI, -0.2, tr); return P, {}
    a = seg01(u, T_DIVE[0] + 0.25, T_DIVE[0] + 0.8)
    return gob_simple(G3_PERF, G3, t, hop_path(G3_LINE, G3_STATUE, a, 0.45), lerp(-0.2, PI + 0.4, sm(a))), {}
# ---- the hero ----
HERO_A = V((-2.55, 0.0, 4.55)); HERO_M = V((-1.0, 0.0, 4.55)); HERO_B = V((-0.05, 0.0, 5.33)); HERO_POT = V((-0.42, 0.0, 5.28))
def hero_path(u):
    """two straight legs with a rounded corner; returns (pos, yaw, speed)"""
    a = seg01(u, *T_WALK); L1 = np.linalg.norm(HERO_M - HERO_A); L2 = np.linalg.norm(HERO_B - HERO_M); s = sm(a) * (L1 + L2)
    p = HERO_A + (HERO_M - HERO_A) * (s / L1) if s < L1 else HERO_M + (HERO_B - HERO_M) * ((s - L1) / L2)
    y1 = ang_to(HERO_A, HERO_M); y2 = ang_to(HERO_M, HERO_B); w = sm(seg01(s, L1 - 0.4, L1 + 0.4)); yaw = lerp(y1, y2, w)
    if a >= 1: yaw = lerp(y2, 0.0, sm(seg01(u, T_WALK[1], T_WALK[1] + 0.3)))
    sp = (L1 + L2) / (T_WALK[1] - T_WALK[0]) * 6 * a * (1 - a) if 0 < a < 1 else 0.0
    return p, yaw, sp
def hero_state(t):
    """(pose or None, extras)"""
    u = TT(t); sc = scene(t); X = dict(sword=False, coin=False, sil=False)
    if u < S_DOOR - 0.05 or sc == 'loop':
        return None, X
    if u < S_HERO - 0.3:                                                    # the silhouette in the white doorway, tapping his foot
        b = PORTAL - PORTAL_N * 0.1; P = dict(base=tuple(b), yaw=math.atan2(PORTAL_N[0], PORTAL_N[2]), eyes='open', mouth='neutral', brow=-0.3, head=(0.0, 0.0, 0.0))
        P['lh'] = (-0.2, 1.05, 0.12); P['rh'] = (0.22, 1.05, 0.12); P['lgrip'] = 0.3; P['rgrip'] = 0.3
        tap = max(0.0, math.sin((u - S_DOOR) * 13)); P['rf'] = (0.11, 0.075 + 0.05 * tap, 0.12 + 0.03 * tap); X['sil'] = True
        if T_TIPON + 0.3 <= u < S_MONT: P['head'] = (0.0, -0.12, 0.0)        # reading the tip
        return P, X
    p, yaw, sp = hero_path(u)
    P = dict(base=tuple(p), yaw=yaw, eyes='open', mouth='neutral', brow=0.0, lean=0.04, cape_sway=0.15 * math.sin(t * 1.9), head=(0.0, 0.0, 0.0))
    P['lh'] = (-0.24, 0.98, 0.1); P['rh'] = (0.25, 0.98, 0.1); P['lgrip'] = 0.4; P['rgrip'] = 0.4
    if sp > 0.05: P['walk'] = 2 * PI * 0.95 * (u - T_WALK[0]); P['stride'] = 0.3 * min(1.0, sp / 1.3); P['lift'] = 0.1 * min(1.0, sp / 1.3)
    if False:                                                               # knock knock on the planks (blended below)
        pass
    kw = win(u, T_KNOCK[0] - 0.25, T_KNOCK[1] + 0.3, 0.25)
    if kw > 0:
        k_ = math.sin(PI * seg01(u, T_KNOCK[0], T_KNOCK[0] + 0.25)) + math.sin(PI * seg01(u, T_KNOCK[0] + 0.25, T_KNOCK[1]))
        P['rh'] = lerp3(P['rh'], (0.17, 1.12, 0.5 + 0.05 * k_), kw); P['rgrip'] = lerp(0.4, 1.0, kw)
    if u >= T0['10'] - 0.1:
        P['mouth'] = 'open' if talking(t, '10') > 0.5 else 'neutral'; P['brow'] = -0.4; P['head'] = (0.05, 0.12, 0.08); P['look'] = (0.0, 0.2)
    if u >= T_SPOT:                                                         # spots the pot (his left), turns, sword up
        tr = sm(seg01(u, T_SPOT, T_SPOT + 0.35)); P['yaw'] = lerp(0.0, ang_to(HERO_B, POT_BIG), tr)
        P['base'] = tuple(lerp3(tuple(HERO_B), tuple(HERO_POT), sm(seg01(u, T_SPOT + 0.1, T_LIFT[0])))); P['eyes'] = 'open'; P['brow'] = 0.3; P['mouth'] = 'smile'
        X['sword'] = True; li = sm(seg01(u, *T_LIFT)); P['rh'] = lerp3((0.3, 1.1, 0.35), (0.2, 2.2, 0.22), li); P['rgrip'] = 1.0
        P['lh'] = lerp3((-0.24, 0.98, 0.1), (0.07, 2.16, 0.24), li); P['lgrip'] = 0.9; X['sdir'] = lerp3((0.05, 0.9, 0.45), (0.0, 0.3, -1.0), li)
    if u >= T_SMASH - 0.2:
        sw = sm(seg01(u, T_SMASH - 0.2, T_SMASH)); P['rh'] = lerp3((0.2, 2.2, 0.22), (0.15, 0.95, 0.55), sw); P['lh'] = lerp3((0.07, 2.16, 0.24), (0.05, 0.95, 0.5), sw)
        X['sdir'] = lerp3((0.0, 0.3, -1.0), (0.0, -0.55, 0.85), sw); P['lean'] = 0.04 + 0.25 * sw
        if u >= T_SMASH + 0.25:
            rr = sm(seg01(u, T_SMASH + 0.25, T_SMASH + 0.7)); P['rh'] = lerp3((0.15, 0.95, 0.55), (0.3, 1.0, 0.2), rr); P['lh'] = lerp3((0.05, 0.95, 0.5), (-0.24, 0.98, 0.15), rr)
            X['sdir'] = lerp3((0.0, -0.55, 0.85), (0.1, -0.95, 0.2), rr); P['lean'] = lerp(0.29, 0.04, rr); P['lgrip'] = 0.4
    if T_TAKE[0] <= u < T_TAKE[1] + 0.4:                                     # takes the coin from Bob's fingers
        tk = win(u, T_TAKE[0], T_TAKE[1] + 0.4, 0.22); bp, _ = bob_state(t); P['lh_w'] = None
        X['take'] = tk
    if u >= T_TAKE[1]: X['coin'] = True
    if u >= T_LEAVE:                                                         # shrugs and walks off into the gate
        a = seg01(u, T_LEAVE, T_FLASH + 0.1); gate_in = V((0.05, 0.0, 6.45))
        b0 = HERO_POT; p = V(lerp3(tuple(b0), tuple(gate_in), sm(a))); P['base'] = tuple(p); P['yaw'] = ang_to(b0, gate_in)
        if 0.0 < a < 0.98: ew = sm(seg01(u, T_LEAVE, T_LEAVE + 0.35)) * (1 - sm(seg01(a, 0.85, 0.98))); P['walk'] = 2 * PI * 0.9 * (u - T_LEAVE); P['stride'] = 0.28 * ew; P['lift'] = 0.09 * ew
        P['mouth'] = 'smile'; P['head'] = (0.0, 0.0, 0.0); P['look'] = (0.0, 0.0)
    return P, X

# =====================================================================================================================
#                                                      CAMERA
# =====================================================================================================================
O_POS = V((BOB_X + 0.28, 1.5, 5.55)); O_TGT = V((BOB_X - 0.08, 1.42, 6.85)); O_FOV = 44.0
MONT_C = V((-0.35, 0.9, 3.3))
def mont_ang(u):
    """orbit angle: chest -> torches (whip left) -> dragon (whip right through the middle) -> back to the chest for the wink"""
    keys = [(S_MONT, -0.15), (ws('04', 1) - 0.15, -0.2), (ws('04', 1) + 0.12, -0.55), (ws('04', 2) - 0.2, -0.6), (ws('04', 2) + 0.1, 0.85),
            (ws('04', 3) - 0.05, 0.85), (ws('04', 3) + 0.25, -0.35), (T_WINK - 0.25, -0.2), (S_99, -0.25)]
    for (a, x), (b, y) in zip(keys, keys[1:]):
        if u < b: return lerp(x, y, sm(seg01(u, a, b)))
    return keys[-1][1]
def mont_tgt(u):
    keys = [(S_MONT, CHEST_AT + V((0, 0.6, 0))), (ws('04', 1) - 0.15, CHEST_AT + V((0, 0.6, 0))), (ws('04', 1) + 0.12, V((-3.65, 1.45, 3.2))),
            (ws('04', 2) - 0.2, V((-3.65, 1.45, 3.3))), (ws('04', 2) + 0.1, DRAGON_AT + V((0, 1.3, 0))), (ws('04', 3) - 0.05, DRAGON_AT + V((0, 1.3, 0))),
            (ws('04', 3) + 0.25, V((-2.15, 1.4, 6.0))), (T_WINK - 0.25, CHEST_AT + V((-0.2, 0.6, -0.3))), (S_99, CHEST_AT + V((-0.3, 0.6, -0.4)))]
    for (a, x), (b, y) in zip(keys, keys[1:]):
        if u < b: return V(lerp3(tuple(x), tuple(y), sm(seg01(u, a, b))))
    return keys[-1][1]
def cam_shot(t):
    sc = scene(t); idx = [n for n, _ in CUTS].index(sc); a = CUTS[idx][1]; b = CUTS[idx + 1][1] if idx + 1 < len(CUTS) else DUR; u = sm(seg01(t, a, b)); tt = TT(t)
    if sc in ('open', 'loop'):
        k = math.exp(-0.006 * FPS * tt)                                    # one slow push-in through the loop seam (tt < 0 = a little wider)
        return V(motion.dolly(tuple(O_POS), tuple(O_TGT), k)), O_TGT, O_FOV
    if sc == 'jump':
        hc = V((BOB_X, 1.55, 6.8)); p = hc + V((0.12, 0.08, -1.15)); return V(motion.dolly(tuple(p), tuple(hc), motion.creep(t, a, 0.003))), hc, 40.0
    if sc == 'door':                                                       # whip pan to the white doorway
        w = sm(seg01(t, a, a + 0.22)); p = V((-1.45, 1.55, 4.7)); t0_ = V((BOB_X, 1.55, 6.8)); t1_ = PORTAL + V((0, 1.15, 0))
        return p, V(lerp3(tuple(t0_), tuple(t1_), w)), 44.0
    if sc == 'tip':
        tg = BOARD + V((0.4, 0.92, 0.05)); p = tg + V((1.05, 0.22, -1.45)); return V(motion.dolly(tuple(p), tuple(tg), motion.creep(t, a, 0.004))), tg, 46.0
    if sc == 'mont':
        an = mont_ang(t); R_ = lerp(2.7, 1.75, sm(seg01(t, T_WINK - 0.45, T_WINK - 0.1))); p = MONT_C + V((R_ * math.sin(an), lerp(1.05, 0.55, sm(seg01(t, T_WINK - 0.45, T_WINK - 0.1))), -R_ * math.cos(an)))
        return p, mont_tgt(t), 52.0
    if sc == 'wide':                                                       # crane-down onto the crew, the gate behind them
        p = V(lerp3((0.1, 3.3, -0.3), (0.0, 1.75, 0.75), sm(seg01(t, a, a + 1.4)))); tg = V(lerp3((0.0, 0.5, 4.4), (-0.05, 1.05, 4.7), sm(seg01(t, a, a + 1.4))))
        if t >= T_LOOK - 0.1:                                              # a small push on the empty gate
            w = sm(seg01(t, T_LOOK - 0.1, T_LOOK + 0.9)); p = V(lerp3(tuple(p), (-0.05, 1.7, 0.6), w)); tg = V(lerp3(tuple(tg), (0.0, 1.2, 6.2), w))
        return p, tg, 52.0
    if sc == 'twitch':
        hc = BOB_LINE + V((0, 1.02, 0)); p = hc + V((0.05, 0.02, -0.95)); return V(motion.dolly(tuple(p), tuple(hc), motion.creep(t, a, 0.003))), hc, 34.0
    if sc == 'places':
        p = V(lerp3((0.95, 1.6, 2.2), (0.75, 1.55, 2.6), u)); return p, V((-0.45, 0.8, 5.25)), 56.0
    if sc == 'hero':                                                       # over the hero's right shoulder
        hp, yaw, _ = hero_path(min(tt, T_WALK[1] + 0.4)); f = V((math.sin(yaw), 0, math.cos(yaw))); rt = V((math.cos(yaw), 0, -math.sin(yaw)))
        p = hp + V((0, 1.8, 0)) - f * 1.7 + rt * 1.05; tg = hp + V((0, 1.0, 0)) + f * 2.0 - rt * 0.15
        if tt >= T_SPOT: w = sm(seg01(tt, T_SPOT, T_SPOT + 0.5)); tg = V(lerp3(tuple(tg), tuple(POT_BIG + V((0, 0.7, 0))), w))
        return p, tg, 46.0
    if sc == 'pot':
        tg = POT_BIG + V((0.12, 0.62, 0.0)); p = tg + V((0.55, 0.12, -1.35))
        if t >= T_STAMP - 0.4: w = sm(seg01(t, T_STAMP - 0.4, T_STAMP + 0.2)); tg2 = POT_BIG + V((0.0, 0.78, 0.0)); p = V(lerp3(tuple(p), tuple(tg2 + V((0.3, 0.06, -1.0))), w)); tg = V(lerp3(tuple(tg), tuple(tg2), w))
        return V(motion.dolly(tuple(p), tuple(tg), motion.creep(t, a, 0.002))), tg, 44.0
    if sc == 'gate':
        tg = V((0.0, 1.15, 6.0)); p = V((0.85, 1.6, 2.7)); return V(motion.dolly(tuple(p), tuple(tg), motion.creep(t, a, 0.006))), tg, 44.0
    return O_POS, O_TGT, O_FOV

# =====================================================================================================================
#                                                      RENDER
# =====================================================================================================================
def hat_world(P, X):
    """the hat frame: on the head, popping (up + spin + back down), or crooked"""
    RH = P['_RH']; hc = P['_head']
    if X['hat'] is None: return None
    kind, a = X['hat']
    if kind == 'pop':
        up = 0.55 * math.sin(PI * a); spin = 2 * PI * a; tilt = 0.25 * a
        return (RH @ hd.Ry(spin) @ hd.Rz(tilt), hc + V((0, up, 0)))
    return (RH @ hd.Rz(0.22) @ hd.Ry(0.3), hc + RH @ V((0.012, 0.004, 0.0)))
def sparks(t):
    """hammer sparks at every impact (Bob at the wall)"""
    Q = []; u = TT(t)
    for ti in hammer_impacts(u - 0.4, u + 0.001):
        if ti > T_JUMP: continue
        a = u - ti; c = V((BOB_X - 0.17, 1.24, 6.2))
        for i in range(9):
            d = nz(V((hsh(i, int(ti * 50)) - 0.5, 0.6 + 0.6 * hsh(i, 7 + int(ti * 50)), hsh(i, 9 + int(ti * 50)) - 0.75)))
            p = c + d * (2.2 * a) + V((0, -3.0 * a * a, 0)); s = 0.022 * (1 - a / 0.4)
            if s > 0.003: Q.append(hd.face([tuple(p + V((-s, 0, 0))), tuple(p + V((0, s, 0))), tuple(p + V((s, 0, 0))), tuple(p + V((0, -s, 0)))], (255, 220, 120), emit=True))
    return [q for q in Q if q]
def dust(c, t0, t, n=8, r=0.5, seed=0, col=(226, 220, 206)):
    a = t - t0
    if a < 0 or a > 0.7: return []
    Q = []
    for i in range(n):
        ang = 2 * PI * i / n + seed; d = V((math.cos(ang), 0.15 + 0.2 * hsh(i, seed), math.sin(ang)))
        p = V(c) + d * r * (1 - (1 - a / 0.7) ** 2) + V((0, 0.12, 0)); s = 0.12 * (1 - a / 0.7) + 0.02
        Q += hd.ellip(tuple(p), np.eye(3), (s, s * 0.8, s), 6, 3, col)
    return Q
def world(t):
    pos, tgt, fov = cam_shot(t); zc = float(pos[2]); u = TT(t); sc = scene(t)
    layers = [void_set(zc), static_set(), wall_faces(t)]
    # crane + loads
    QC, hook, load = crane(t); layers.append(QC)
    if roof_placed(t): layers.append(roof(ROOF_ON))
    if dragon_placed(t): layers.append(dragon_statue(DRAGON_AT + V((0, PLINTH_H, 0))))
    # torches, trees, chest, pots, planks
    for i, p in enumerate(TORCH_POS):
        k = torch_k(i, t)
        if k > 0: layers.append(dtx.torch_faces(p + V((0, 1.38, 0)), t, k=k, seed=i, stick=False))
    for i in range(len(TREES)):
        s = tree_s(i, t)
        if s > 0.01: layers.append(tree_faces(i, s))
    cy = chest_y(t)
    if cy is not None: layers.append(chest(t, cy)); layers.append(dust(CHEST_AT, T_CHEST + 0.32, u, 10, 0.7, 3))
    for p in POTS_SMALL: layers.append(pot(p, 0.55))
    if u < T_SMASH: layers.append(pot(POT_BIG, 1.0))
    else: layers.append(shards(t))
    layers.append(sparks(t))
    if T_WALL <= u < T_WALL + 1.0: layers.append(dust(V((-2.15, 1.2, 5.9)), T_WALL + 0.2, u, 8, 0.9, 5))
    # ---- Bob
    BP, BX = bob_state(t); B = None
    if BX['vis']:
        Q = goblin(BOB, BP, hat=(None if BX['hat'] is not None else HAT_W), pencil=not BX.get('pencil_hand'))
        hw = hat_world(BP, BX)
        if hw is not None: Q += goblin_parts(BOB, BP, hat=HAT_W, hat_off=hw)[-(0):] if False else _hat_only(BP, hw)
        layers.append(Q); B = BP
        if BX['hammer']:
            g = BP.get('_rgrip', grip_pt(BP, 'r', 0.05, 0.0)); d0 = nz(BP['_rdir'] * 0.3 + V((0, 1.0, 0))); w_ = BX.get('hdir_w', 0.0)
            d = nz(V(lerp3(tuple(d0), tuple(BX['hdir']), w_))) if BX.get('hdir') is not None else d0
            Qh, _ = hammer(g, d, V((0, 0, -1.0))); layers.append(Qh)
        if BX.get('pencil_hand'):
            g = BP.get('_rgrip', grip_pt(BP, 'r', 0.05, 0.0)); layers.append(hd.limb(tuple(g), tuple(g + BOARD_N * -0.09 + V((0, -0.02, 0))), 0.008, 0.004, (240, 200, 60), n=5, m=1))
        cq = clip_quad(BP, BX)
        if cq is not None: layers.append(clipboard(*cq))
        if BX['stamp']:
            g = BP.get('_rgrip', grip_pt(BP, 'r', 0.05, 0.0)); layers.append(stamp_tool(g, -(BP['_RW'] @ nz(V((0.0, 0.25, 1.0))))))
        if BX['coin']:
            g = BP.get('_rgrip', grip_pt(BP, 'r', 0.05, 0.0)); layers.append(coin3(g + V((0, 0.06, 0)), hd.Rx(PI / 2)))
        if sc in ('pot', 'gate') and u >= T_SMASH:                                          # pot shards resting on his shoulders
            for sd in (1, -1):
                c = BP['_' + ('r' if sd > 0 else 'l') + 'sh'] + V((0, 0.05, 0))
                layers.append(hd.ellip(tuple(c), hd.Rz(0.4 * sd), (0.08, 0.02, 0.06), 6, 3, CLAY, v1=PI * 0.5))
    # ---- crew
    G1P, _ = g1_state(t); layers.append(goblin(G1, G1P))
    G2P, G2X = g2_state(t); layers.append(goblin(G2, G2P))
    if G2X.get('hammer_low'):
        g = G2P.get('_rgrip', grip_pt(G2P, 'r', 0.05, 0.0)); layers.append(hammer(g, nz(G2P['_rdir'] * 0.2 + V((0, 0.9, 0))), V((0, 0, 1.0)))[0])
    pm = G2X.get('planks')
    if pm in (None, 'pile'): layers.append(planks('pile'))
    elif pm == 'carry':
        a = G2X['a']; Qp = planks('door'); c0 = PLANKS_PILE + V((0, 0.3, 0)); c1 = V((0.0, 1.05, 5.97)); off = V(lerp3(tuple(c0), tuple(c1), sm(seg01(a, 0.35, 1.0)))) - c1
        for q in Qp: q['p'] = [tuple(V(p) + off) for p in q['p']]; refresh(q)
        layers.append(Qp)
    elif pm == 'door': layers.append(planks('door'))
    else: layers.append(planks('open', G2X['a']))
    G3P, _ = g3_state(t); layers.append(goblin(G3, G3P))
    # the crane operator in the cab (small, far)
    a, r, hy, _ = crane_state(t); d = V((math.sin(a), 0, math.cos(a)))
    P4 = dict(base=tuple(CRANE + V((0, CRANE_H + 0.02, 0)) + d * 0.05), yaw=a, eyes='open', mouth='neutral', head=(0.0, -0.2, 0.0)); P4['lh'] = (-0.2, 0.7, 0.25); P4['rh'] = (0.2, 0.7, 0.25)
    layers.append(goblin_old(G4, P4))
    # ---- the hero
    HP, HX = hero_state(t)
    if HP is not None:
        if HX.get('take') is not None and B is not None:
            tk = HX['take']; cpos = B.get('_rgrip', grip_pt(B, 'r', 0.05, 0.0)) + V((0, 0.06, 0)); HP['lh_w'] = tuple(lerp3(tuple(V(HP['base']) + hd.Ry(HP['yaw']) @ V((-0.24, 0.98, 0.1))), tuple(cpos + V((0.02, 0.03, -0.03))), tk))
            HP['lgrip'] = 0.5 + 0.5 * tk
        QK = knight(HP)
        if HX['sil']: QK = silhouette(QK)
        layers.append(QK)
        if HX['sword']:
            gr = grip_pt(HP, 'r', 0.06, 0.0); d = hd.Ry(HP['yaw']) @ V(HX.get('sdir', (0.05, 0.9, 0.45))); layers.append(hd.sword(tuple(gr), tuple(nz(d)), HP['_rpalm'], length=0.85))
        if HX['coin'] and u < T_FLASH: layers.append(coin3(grip_pt(HP, 'l', 0.06, 0.03), hd.Rx(PI / 2)))
    if u >= T_LEAVE + 0.3 and sc in ('gate',):                                              # the gate becomes the exit: white light
        layers.append(hd.decal((0.0, 1.0, 6.42), (0, 0, -1.0), (0, 1, 0), 1.38, 2.0, (255, 255, 255), emit=True, lift=0.0))
    # lights: soft white sky light + the torches (warm, flicker)
    L = [(tuple(V(tgt) + V((-5.0, 9.0, -4.0))), (255, 250, 240), 20.0), (tuple(V(tgt) + V((6.0, 5.0, 2.0))), (220, 230, 255), 6.0)]
    for i, p in enumerate(TORCH_POS):
        k = torch_k(i, t)
        if k > 0: L.append((tuple(p + V((0, 1.6, 0))), (255, 170, 90), 1.2 * k * (1 + 0.12 * math.sin(t * 23 + i))))
    return layers, L, dict(B=B, BX=BX, H=HP, HX=HX)
def _hat_only(P, hw):
    """the hard hat alone at a given frame (used while it pops off / sits crooked)"""
    Rh, c = hw; k = P['_hk']; hat = HAT_W; Q = []
    def Lh(x, y, z): return c + Rh @ V((x * k, y * k, z * k))
    Q += hd.ellip(tuple(Lh(0, 0.058, -0.004)), Rh, (0.1 * k, 0.088 * k, 0.112 * k), 12, 5, hat, v1=PI * 0.5, colfn=lambda i, j, cl: hd.shade(hat, 0.86) if i % 6 == 0 else hat)
    Q += hd.lathe(tuple(Lh(0, 0.052, 0.0)), Rh, [(0.122 * k, 0.0), (0.118 * k, 0.012 * k)], 14, hd.shade(hat, 0.92))
    Q += hd.limb(tuple(Lh(0, 0.146, -0.07)), tuple(Lh(0, 0.146, 0.07)), 0.012 * k, 0.012 * k, hd.shade(hat, 0.82), n=5, m=1)
    Q += hd.ellip(tuple(Lh(0, 0.062, -0.004)), Rh, (0.101 * k, 0.03 * k, 0.113 * k), 12, 3, (210, 60, 40), v0=PI * 0.42, v1=PI * 0.5)
    return [q for q in Q if q]
def goblin_old(S_, P):
    """far / tiny goblin (the crane operator): the plain hd face is enough at that size"""
    Q = hd.human(S_, P); return Q + goblin_parts(S_, P, hat=HAT_Y)
def clip_quad(P, X):
    """(quad, normal) of Bob's clipboard: on the belt, clutched to the chest (facing out), or held in the left hand"""
    mode = X['clip']
    if mode is None: return None
    RW = P['_RW']; k = P['_hk'] / HS * 1.0
    if mode == 'belt':
        c = P['_pel'] + RW @ V((-0.17, -0.02, 0.06)); n_ = RW @ nz(V((-0.6, 0.0, 0.8))); up = RW @ V((0, 1.0, 0.0))
        return clipboard_quad(c, n_, up, 0.14, 0.19), n_
    if mode in ('chest', 'hand'):
        g = grip_pt(P, 'l', 0.03, 0.0); n_ = RW @ nz(V((0.0, 0.25, 1.0))); up = RW @ V((0, 1.0, 0.0)); rt = RW @ V((1.0, 0, 0))
        c = g + rt * 0.08 + n_ * 0.02
        return clipboard_quad(c, n_, up, 0.15, 0.2), n_
    return None
def frame_low(t):
    pos, tgt, fov = cam_shot(t)
    sh = motion.kick(t, T_JUMP, amp=0.035, frames=7) + motion.kick(t, T_SMASH, amp=0.03, frames=6) + motion.kick(t, T_CHEST + 0.32, amp=0.02, frames=5)
    pos = V(pos) + V((0.0, sh, 0.0)); cam = Camera.look(tuple(pos), tuple(tgt))
    layers, L, info = world(t)
    R = Renderer(W, H, fog=VOIDC)
    img, vi, zb = zrender(R, cam, layers, L, fov=fov, fog_start=11.0, fog_end=34.0, ambient=0.5, return_z=True)
    a = look.outline(np.asarray(img).astype(np.float32), zb)
    a = np.clip((a - 80) * 1.08 + 84, 0, 255)
    return post.ps1(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), levels=6), vi, R, info, zb

# ======================= overlays (1080 x 1920) =======================
def tw(s, sc): return font.width(s, sc)
def ctext(d, s, y, sc, col, o=4, x=None):
    x = int(540 - tw(s, sc) / 2) if x is None else x
    look.draw_cells(d, look.text_cells(s, x, y, sc, col), o)
TX = dict(load='YÜKLENİYOR' if TRL else 'LOADING', tip='İPUCU:' if TRL else 'TIP:', px='DEVAM İÇİN X' if TRL else 'PRESS X TO CONTINUE',
          tips={'TAKE YOUR TIME': 'ACELE ETME' if TRL else 'TAKE YOUR TIME', 'CHESTS ARE ALWAYS SAFE': 'SANDIKLAR HEP GÜVENLİDİR' if TRL else 'CHESTS ARE ALWAYS SAFE', '': ''},
          cov=('YÜKLEME EKRANI', 'NEDEN İPUCU', 'GÖSTERİR?') if TRL else ('WHY DO', 'LOADING TIPS', 'EXIST?'),
          clip=('LISTE', 'DUVAR', 'MESALE', 'EJDERHA', 'GEC = KOVULDUN') if TRL else ('TO DO:', 'WALL', 'TORCHES', 'DRAGON', 'LATE = FIRED'),
          hired='İŞTE' if TRL else 'HIRED', gold='+1 ALTIN' if TRL else '+1 G')
for _s in [TX['load'], TX['tip'], TX['px'], TX['hired'], TX['gold'], *TX['cov'], *TX['clip'], *TX['tips'].values()]: font.check(_s)
WHT = (240, 236, 226); YEL = (255, 214, 70); RED = (230, 50, 44); INK = (40, 36, 44)
def coin_icon(d, cx, cy, t, r=30):
    w = abs(math.cos(t * 4.2)) * r + 3
    d.ellipse([cx - w, cy - r, cx + w, cy + r], fill=(250, 206, 70), outline=(150, 100, 20), width=4)
    if w > 10: d.rectangle([cx - w * 0.2, cy - r * 0.5, cx + w * 0.2, cy + r * 0.5], fill=(200, 150, 40))
def hourglass(d, cx, cy, t):
    rot = (t * 2.0) % 1.0 < 0.15
    pts = [(cx - 22, cy - 30), (cx + 22, cy - 30), (cx, cy), (cx + 22, cy + 30), (cx - 22, cy + 30), (cx, cy)]
    if rot: pts = [(cx - 30, cy - 22), (cx - 30, cy + 22), (cx, cy), (cx + 30, cy + 22), (cx + 30, cy - 22), (cx, cy)]
    d.polygon(pts[:3], fill=(250, 230, 180), outline=(60, 50, 40)); d.polygon(pts[3:], fill=(250, 230, 180), outline=(60, 50, 40))
    d.polygon([(cx - 10, cy + 28), (cx + 10, cy + 28), (cx, cy + 12)] if not rot else pts[3:], fill=(230, 180, 60))
def loading_ui(d, t):
    if not ui_on(t): return
    v = bar(t); u = TT(t); pulse = 1.0 + 0.08 * math.exp(-((u - T_JUMP - 0.1) / 0.12) ** 2) + 0.05 * math.exp(-((u - T_99[1]) / 0.12) ** 2)
    x0, x1 = 120, 960; yb = 1495; hb = int(46 * pulse)
    label = f"{TX['load']} {int(v)}%"; ctext(d, label, 1418, 7, WHT, o=5, x=x0)
    coin_icon(d, x1 - 26, 1440, t)
    if slowed(t): hourglass(d, x1 - 110, 1440, t)
    d.rectangle([x0 - 8, yb - 8 - (hb - 46) // 2, x1 + 8, yb + hb + 8 - (hb - 46) // 2], fill=(20, 22, 34)); d.rectangle([x0 - 8, yb - 8 - (hb - 46) // 2, x1 + 8, yb + hb + 8 - (hb - 46) // 2], outline=(220, 220, 236), width=5)
    fill = int((x1 - x0) * v / 100.0); col = (110, 220, 110) if v < 99 else (255, 214, 70)
    d.rectangle([x0, yb - (hb - 46) // 2, x0 + fill, yb + hb - (hb - 46) // 2], fill=col)
    for i in range(0, fill, 36): d.rectangle([x0 + i, yb - (hb - 46) // 2, x0 + i + 12, yb + hb - (hb - 46) // 2], fill=hd.shade(col, 0.86))
    tp = tip_text(t)
    if tp is not None:
        s = TX['tips'][tp]; n = int((u - tip_t0(t)) * 26) if tp else 0; shown = s[:max(0, n)]
        d.rectangle([90, 1236, 990, 1376], fill=(14, 16, 28)); d.rectangle([90, 1236, 990, 1376], outline=(255, 214, 70), width=4)
        ctext(d, TX['tip'], 1262, 6, YEL, o=4, x=118)
        if shown: ctext(d, shown, 1318, 6, WHT, o=4, x=118)
        if tp == '' or n < len(s):                                         # the blinking cursor (alone = he has run out of tips)
            if (t * 3) % 1.0 < 0.55: cx_ = 118 + (tw(shown, 6) + 12 if shown else 0); d.rectangle([cx_, 1318, cx_ + 24, 1318 + 42], fill=WHT)
    if u >= T_100 and (t * 2.6) % 1.0 < 0.62: ctext(d, TX['px'], 1300, 7, YEL, o=5)
def cover(d, t):
    if not (0 <= t < T0['01'] + 0.2): return
    lines = TX['cov']; scs = [min(sc_, max(6, int(1000 / (len(l_) * 6 - 1)))) for l_, sc_ in zip(lines, (12, 13, 15))]
    y = 330; w = max(tw(s, sc) for s, sc in zip(lines, scs)); yy = y
    for i, (s, sc) in enumerate(zip(lines, scs)):
        if i == len(lines) - 1: d.rectangle([540 - w / 2 - 30, yy - 18, 540 + w / 2 + 30, yy + 7 * sc + 18], fill=(30, 90, 50))
        ctext(d, s, yy, sc, YEL if i == len(lines) - 1 else WHT, o=6); yy += 7 * sc + 34
def _proj(R, vi, p):
    q = R.project(tuple(p), vi); return None if q is None else (q[0] * S, q[1] * S, q[2])
def glow(arr, R, vi, p, rad_m, col, k):
    q = _proj(R, vi, p)
    if q is None: return arr
    r = max(6.0, rad_m * vi[7] * S / max(0.2, q[2])); x0, x1 = int(max(0, q[0] - r)), int(min(W * S, q[0] + r)); y0, y1 = int(max(0, q[1] - r)), int(min(H * S, q[1] + r))
    if x1 <= x0 or y1 <= y0: return arr
    yy, xx = np.mgrid[y0:y1, x0:x1]; dd = np.sqrt((xx - q[0]) ** 2 + (yy - q[1]) ** 2) / r
    m = np.clip(1 - dd, 0, 1) ** 2.2 * k; arr[y0:y1, x0:x1] += m[..., None] * np.array(col, np.float32)
    return arr
def pool(arr, R, vi, c, rad, col, k, blur=18):
    pts = [_proj(R, vi, V(c) + V((rad * math.cos(a), 0.0, rad * math.sin(a)))) for a in np.linspace(0, 2 * PI, 20)[:-1]]
    if any(p_ is None for p_ in pts): return arr
    ov = Image.new('L', (W * S, H * S), 0); ImageDraw.Draw(ov).polygon([(p_[0], p_[1]) for p_ in pts], fill=255)
    m = np.asarray(ov.filter(ImageFilter.GaussianBlur(blur))).astype(np.float32) / 255.0 * k
    if GMASK is not None: m = m * GMASK
    return arr + m[..., None] * np.array(col, np.float32)
GMASK = None
def ground_mask(vi, zb):
    cx, cy, cz, ca, sa, cp, sp, fpx = vi
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32) + 0.5
    X = (xx - W / 2) / fpx; Y = (H / 2 - yy) / fpx; Z2 = np.ones_like(X)
    py = cp * Y + sp * Z2
    with np.errstate(divide='ignore', invalid='ignore'):
        sg = np.where(py < -1e-4, -cy / py, np.inf); dep = np.where(zb > 0, 1.0 / np.maximum(zb, 1e-9), np.inf)
    m = (np.isfinite(sg) & (dep > sg * 0.93)).astype(np.float32)
    return np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize((W * S, H * S), Image.BILINEAR)).astype(np.float32) / 255.0
def lights2d(arr, t, vi, R):
    for i, p in enumerate(TORCH_POS):
        k = torch_k(i, t)
        if k <= 0: continue
        f = p + V((0, 1.5, 0)); fl = 1.0 + 0.12 * math.sin(t * 23 + i)
        arr = glow(arr, R, vi, f, 0.5 * fl * k, (255, 150, 60), 0.8)
        arr = pool(arr, R, vi, V((f[0], 0.0, f[2])), 1.1 * fl, (255, 140, 60), 0.16 * k, 20)
    u = TT(t)
    for ti in hammer_impacts(u - 0.12, u + 0.001):
        if ti <= T_JUMP: arr = glow(arr, R, vi, V((BOB_X - 0.17, 1.26, 6.2)), 0.25, (255, 220, 140), 1.1 * (1 - (u - ti) / 0.12))
    e = win(u, T_WINK - 0.25, T_WINK + 1.6, 0.12)
    cy = chest_y(t)
    if e > 0 and cy is not None: arr = glow(arr, R, vi, CHEST_AT + V((0, 0.5 + cy, 0.05)), 0.35, (255, 220, 160), 0.25 * e)
    if scene(t) == 'door' or (S_DOOR <= u < S_HERO):                                         # the doorway's white glow
        arr = glow(arr, R, vi, PORTAL + V((0, 1.15, 0)) - PORTAL_N * 0.1, 1.3, (255, 255, 255), 0.5)
    return arr
def paper_tex(lines, stamp=0.0, w=240, h=320, board=False):
    im = Image.new('RGB', (w, h), (246, 242, 230)); d = ImageDraw.Draw(im)
    if board:
        for i, (s, col) in enumerate(lines): look.draw_cells(d, look.text_cells(s, 16, 20 + i * 58, 5 if len(s) < 9 else 4, col), 2)
        return im
    for i, s in enumerate(lines[:-1]):
        look.draw_cells(d, look.text_cells(s, 14, 16 + i * 40, 3, INK), 2)
        if i > 0: d.rectangle([w - 46, 18 + i * 40, w - 22, 42 + i * 40], outline=INK, width=3)
    yl = h - 64; look.draw_cells(d, look.text_cells(lines[-1], 14, yl, 3 if len(lines[-1]) < 13 else 2, RED), 2)
    if stamp > 0:                                                                             # the HIRED stamp, slammed on at an angle over FIRED
        st = Image.new('RGBA', (w, h), (0, 0, 0, 0)); ds = ImageDraw.Draw(st); s_ = TX['hired']; sc = 7; tw_ = font.width(s_, sc)
        bx0, by0 = (w - tw_) // 2 - 12, h // 2 - 40
        ds.rectangle([bx0, by0, bx0 + tw_ + 24, by0 + 7 * sc + 24], outline=(200, 30, 40, 235), width=7)
        look.draw_cells(ds, look.text_cells(s_, bx0 + 12, by0 + 12, sc, (200, 30, 40)), 1)
        st = st.rotate(14, resample=Image.BICUBIC, center=(w // 2, h // 2)); sk = 1.0 + 0.25 * (1 - stamp)
        if sk != 1.0: st = st.resize((int(w * sk), int(h * sk)), Image.BICUBIC).crop((int(w * (sk - 1) / 2), int(h * (sk - 1) / 2), int(w * (sk - 1) / 2) + w, int(h * (sk - 1) / 2) + h))
        im.paste(st, (0, 0), st)
        d.line([(14, yl + 30), (w - 16, yl + 6)], fill=(200, 30, 40), width=5)
    return im
def map_paper(im, R, vi, quad, tex, zb=None):
    """paste a paper texture onto a 3D quad (2D, after the render); hidden where something stands in front of it (z-buffer test)"""
    pts = [_proj(R, vi, p) for p in quad]
    if any(p is None for p in pts): return im
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    if max(xs) - min(xs) < 14 or max(ys) - min(ys) < 14: return im
    a = (pts[1][0] - pts[0][0]) * (pts[2][1] - pts[0][1]) - (pts[1][1] - pts[0][1]) * (pts[2][0] - pts[0][0])
    if a <= 0: return im                                                     # the back of the sheet faces us
    lay = Image.new('RGB', im.size, (0, 0, 0)); post.map_texture(lay, [(p[0], p[1]) for p in pts], tex)
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).polygon([(p[0], p[1]) for p in pts], fill=255)
    m = np.asarray(m).astype(np.float32) / 255.0
    if zb is not None:                                                       # visible only where the paper is the nearest surface
        zmin = max(0.05, min(p[2] for p in pts) - 0.05)                     # a surface nearer than the sheet hides it
        vis = (zb <= 0) | (zb <= 1.0 / zmin)
        vis = np.asarray(Image.fromarray((vis * 255).astype(np.uint8)).resize(im.size, Image.NEAREST)).astype(np.float32) / 255.0
        m = m * vis
    if m.max() <= 0: return im
    out = np.asarray(im).astype(np.float32) * (1 - m[..., None]) + np.asarray(lay).astype(np.float32) * m[..., None]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
def speed_lines(arr, t):
    """whip-pan streaks: strength from how fast the view direction turns"""
    p0, t0_, _ = cam_shot(t); p1, t1_, _ = cam_shot(min(DUR - 1e-3, t + 1 / FPS))
    if scene(t) != scene(min(DUR - 1e-3, t + 1 / FPS)): return arr
    d0 = nz(V(t0_) - V(p0)); d1 = nz(V(t1_) - V(p1)); w = math.degrees(math.acos(max(-1.0, min(1.0, float(d0 @ d1)))))
    k = seg01(w, 2.5, 7.0)
    if k <= 0: return arr
    ov = Image.new('L', (W * S, H * S), 0); dd = ImageDraw.Draw(ov); rg = np.random.default_rng(int(t * FPS))
    for i in range(26):
        y = int(rg.uniform(0, H * S)); x = int(rg.uniform(-200, W * S)); L_ = int(rg.uniform(200, 700)); dd.rectangle([x, y, x + L_, y + int(rg.uniform(3, 9))], fill=int(170 * k))
    m = np.asarray(ov.filter(ImageFilter.GaussianBlur(2))).astype(np.float32)[..., None] / 255.0
    return arr * (1 - m * 0.55) + 255 * m * 0.55
COL = {'N': (242, 238, 226), 'O': (255, 176, 90), 'G': (160, 220, 120), 'D': (210, 170, 120), 'K': (150, 200, 255)}
def _sub_scr():
    if not TRL: return SCR
    import importlib.util as _iu
    sp_ = _iu.spec_from_file_location('lt_tts', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'tts', 'lt.py'))
    m_ = _iu.module_from_spec(sp_); sp_.loader.exec_module(m_); TRS = m_.TR_SUB
    out = dict(SCR); sent = {}
    for k, v in SCR['sent'].items():
        if len(v) == len(TRS[k]): sent[k] = [[a, b, tx] for (a, b, _), tx in zip(v, TRS[k])]
        else: sent[k] = [[v[0][0], v[-1][1], ' '.join(TRS[k])]]
    out['sent'] = sent
    return out
SUBS = look.Subtitles(_sub_scr(), [x for x in LINES if x[0] != '00'], W, H, S, COL, title_key='none', n=17,
                      hil=({'ONLAR', 'ZAMAN', 'KAPI', 'GEÇER'} if TRL else {'THEM.', 'TIME.', 'DOOR?', 'SKIP?', 'HIRED!'}))
from nightkit import cta
CTA = cta.Achievement(t0=T_LOOK - 1.6, lang=SUB_LANG, dur=F(1.5), y=300)
def frame_final(t):
    if t >= DUR: t = t - DUR
    img, vi, R, info, zb = frame_low(t); arr = post.upscale(img, S)
    global GMASK; GMASK = ground_mask(vi, zb)
    arr = lights2d(arr, t, vi, R)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    u = TT(t); B, BX = info['B'], info['BX']
    if scene(t) == 'tip' or (S_DOOR <= u < S_MONT):                                          # the tip board sheet: Bob's scribbled tips
        lines_ = [('TIPS', INK), ('TAKE YOUR', (40, 60, 140)), ('TIME', (40, 60, 140))] if u >= T_TIPON + 0.4 else [('TIPS', INK)]
        if TRL: lines_ = [('İPUCU', INK), ('ACELE', (40, 60, 140)), ('ETME', (40, 60, 140))] if u >= T_TIPON + 0.4 else [('İPUCU', INK)]
        im = map_paper(im, R, vi, board_corners(), paper_tex(lines_, board=True, w=300, h=230), zb)
    if B is not None and BX['clip'] != 'belt':
        cq = clip_quad(B, BX)
        if cq is not None:
            quad, n_ = cq; qd = [V(p) + nz(n_) * 0.003 for p in quad]
            st = sm(seg01(u, T_STAMP, T_STAMP + 0.08)) if u >= T_STAMP and BX['stamp'] else 0.0
            im = map_paper(im, R, vi, qd, paper_tex(list(TX['clip']), stamp=st), zb)
    d = ImageDraw.Draw(im)
    loading_ui(d, t); cover(d, t)
    H_ = info['H']
    if H_ is not None and T_TAKE[1] - 0.1 <= u < T_TAKE[1] + 0.55:                          # +1 G pops up over the hero's hand
        a = seg01(u, T_TAKE[1] - 0.1, T_TAKE[1] + 0.55); q = _proj(R, vi, grip_pt(H_, 'l', 0.06, 0.03))
        if q is not None: ctext(d, TX['gold'], int(q[1] - 140 - 90 * a), 8, YEL, o=6, x=int(min(1080 - tw(TX['gold'], 8) - 20, max(20, q[0] - tw(TX['gold'], 8) / 2))))
    arr = np.asarray(im).astype(np.float32)
    arr = speed_lines(arr, t)
    if T_JUMP <= u < T_JUMP + 0.12: arr = arr + (255 - arr) * 0.18
    if T_FLASH <= t < T_RESET + 0.35:                                                        # the white flash into the next level
        f = sm(seg01(t, T_FLASH, T_RESET)) if t < T_RESET else 1 - sm(seg01(t, T_RESET, T_RESET + 0.35)); arr = arr + (255 - arr) * f
    arr = SUBS.apply(arr, t); arr = CTA.apply(arr, t)
    return arr

TEST = os.environ.get('TEST')
if TEST and __name__ == '__main__':
    if TEST == 'seq': ts = sorted(set([round(a + (b - a) * f, 2) for i, (n_, a) in enumerate(CUTS) for b in [CUTS[i + 1][1] if i + 1 < len(CUTS) else DUR] for f in (0.1, 0.5, 0.9)]))
    else: ts = [float(x) for x in TEST.split(',')]
    tw_ = int(os.environ.get('TW', '200')); th = tw_ * 16 // 9
    ims = [Image.fromarray(np.clip(frame_final(x), 0, 255).astype(np.uint8)) for x in ts]
    if os.environ.get('SZ') == 'full':
        for x, im in zip(ts, ims): im.save(f'test_lt_{x:.2f}.png')
    ims = [im.resize((tw_, th), Image.LANCZOS) for im in ims]
    per = int(os.environ.get('PER', '10')); rows = (len(ims) + per - 1) // per; shp = Image.new('RGB', (min(per, len(ims)) * (tw_ + 2), rows * (th + 18)), (30, 30, 30))
    dd = ImageDraw.Draw(shp)
    for i, (im, x) in enumerate(zip(ims, ts)): shp.paste(im, ((i % per) * (tw_ + 2), (i // per) * (th + 18))); dd.text(((i % per) * (tw_ + 2) + 4, (i // per) * (th + 18) + th + 3), f'{x:.2f} {x / 1.2:.1f}f {scene(x)}', fill=(255, 255, 0))
    shp.save(os.environ.get('TEST_OUT', 'test_lt.png')); print('test written', DUR, round(DUR / 1.2, 2), SEQS); sys.exit()

QA = dict(fps=FPS, dur=DUR, W=W, frame=lambda t: Image.fromarray(np.clip(frame_final(t), 0, 255).astype(np.uint8)).resize((W, H), Image.BOX), chars={},
          geom=lambda t, name, st, V_: [], camera=lambda t: cam_shot(t)[0], min_cam_dist=0.3, camera_ok=lambda p: True, allow_jump=[], weapon_events=[],
          scenes=[dict(id=nm, t0=a, t1=(CUTS[i + 1][1] if i + 1 < len(CUTS) else DUR), action=nm) for i, (nm, a) in enumerate(CUTS)],
          texts=lambda: [('hud', s, 10) for s in TX['cov']])

# ======================= AUDIO =======================
def build_audio(path):
    import soundfile as _sf
    s = Sound(DUR, loop=False, seed=83); sr = s.sr; n = s.n; t = s.t
    BED = np.zeros(n); FX = np.zeros(n); MUS = np.zeros(n)
    def put(buf, x, t0, v=1.0):
        i = int(round(t0 * sr))
        if i >= n or i + len(x) <= 0: return
        if i < 0: x = x[-i:]; i = 0
        j = min(n, i + len(x)); buf[i:j] += (x * v)[:j - i]
    def tone(t0, m, d, v, dec=3.0, att=0.004, glide=0.0, buf=None, harm=(1.0,), sq=False):
        f = 440 * 2 ** ((m - 69) / 12); tt = s.T(d); fr_ = f * (1 + glide * tt / d); ph = np.cumsum(fr_) / sr
        x = np.sign(np.sin(2 * np.pi * ph)) * 0.6 if sq else sum(a * np.sin(2 * np.pi * ph * (k + 1)) for k, a in enumerate(harm))
        put(FX if buf is None else buf, x * np.minimum(1, tt / att) * np.exp(-tt * dec), t0, v)
    def nb(t0, d, lo, hi, v, seed, shape=2, buf=None): put(FX if buf is None else buf, s.filt_short(s.noise(d, seed), lo=lo, hi=hi) * np.sin(np.pi * s.T(d) / d) ** shape, t0, v)
    def thud(t0, f=60, v=0.1, d=0.3, buf=None): tt = s.T(d); put(FX if buf is None else buf, np.sin(2 * np.pi * f * tt * (1 - 0.3 * tt / d)) * np.exp(-tt * 9), t0, v)
    def clink(t0, v=0.03, seed=0):
        for k_, m in enumerate((96, 103, 108)): tone(t0, m + (seed % 3), 0.18, v * (1 - 0.25 * k_), dec=22, harm=(1.0, 0.3))
        nb(t0, 0.03, 2000, 8000, v * 0.8, 700 + seed, 1)
    def pop(t0, v=0.03, m=84): tone(t0, m, 0.09, v, dec=30, glide=0.6, sq=True)
    def sweep(t0, d, f0, f1, v, sq=False, buf=None):
        tt = s.T(d); ph = np.cumsum(f0 + (f1 - f0) * tt / d) / sr; x = np.sign(np.sin(2 * np.pi * ph)) * 0.6 if sq else np.sin(2 * np.pi * ph)
        put(FX if buf is None else buf, x * np.sin(np.pi * tt / d) ** 0.5, t0, v)
    # ---- the void: a soft airy bed (constant, so the loop seam is invisible)
    BED += s.filt(s.rng.normal(0, 1, n), lo=200, hi=1600) * 0.008
    # ---- music: a frantic construction chiptune; its step follows the bar (fast when racing, slow while a tip is up)
    arp = [60, 64, 67, 72, 67, 64, 62, 65, 69, 74, 69, 65]; bass = [36, 36, 43, 41]
    def step_at(u):
        if u < T_JUMP: return 0.16
        if u < T_TIPON: return 0.11
        if u < S_MONT: return 0.24                                                     # the tip: everything drags
        if u < T_EMPTY: return 0.13
        if u < T_LOOK: return 0.1
        return 0.16
    def music_run(t_from, t_to, uf, vol=1.0, k0=0):
        x = t_from; k = k0
        while x < t_to:
            u = uf(x); st = step_at(u)
            tone(x, arp[k % len(arp)] + 12, st * 0.9, 0.012 * vol, dec=9, sq=True, buf=MUS)
            if k % 2 == 0: tone(x, bass[(k // 4) % 4], st * 1.8, 0.02 * vol, dec=4, sq=True, buf=MUS)
            if k % 4 == 2: nb(x, 0.04, 3000, 9000, 0.006 * vol, 900 + k, 1, buf=MUS)
            x += st; k += 1
    music_run(0.0, T_LOOK, lambda x: x)
    music_run(T_RESET, DUR, lambda x: x - DUR)                                              # the next level: the same groove from its start
    sweep(T_LOOK, 0.55, 330, 50, 0.012, sq=True, buf=MUS)                                    # record-stop
    nb(T_LOOK, 0.3, 300, 3000, 0.02, 31, 1)
    music_run(T0['08'] + 0.1, S_HERO - 0.1, lambda x: T_EMPTY + 0.5, vol=1.1)               # "Places!": a frantic burst
    x = S_HERO; k = 0                                                                       # the hero: a sneaky pizzicato
    while x < T_SMASH - 0.2:
        tone(x, [43, 46, 43, 50][k % 4], 0.25, 0.024, dec=8, harm=(1.0, 0.4, 0.2), buf=MUS); x += 0.34; k += 1
    for k_, m in enumerate((72, 76, 79, 84)): tone(T_TAKE[1] + 0.05 + 0.07 * k_, m, 0.3, 0.012, dec=6, sq=True, buf=MUS)      # loot jingle
    # ---- FX
    for ti in hammer_impacts(-0.01, T_JUMP + 0.01) + [DUR + x_ for x_ in hammer_impacts(T_RESET - DUR, 0.0)]: clink(ti, 0.035, int(ti * 10))
    sweep(T_JUMP, 0.18, 400, 2800, 0.02); thud(T_JUMP + 0.17, 70, 0.08, 0.25)               # the bar zips up
    tone(T_JUMP + 0.05, 67, 0.5, 0.02, dec=5, glide=0.8, harm=(1.0, 0.5))                  # hat boing
    thud(T_JUMP + 0.72, 160, 0.03, 0.1)
    for x_ in np.arange(T_TIPON, S_MONT - 0.2, 0.42): nb(x_, 0.12, 1500, 5000, 0.006, int(x_ * 77), 1)   # scribble
    nb(T_ROOF[0], T_ROOF[1] - T_ROOF[0], 200, 900, 0.006, 12, 1); thud(T_ROOF[1], 90, 0.04, 0.3)        # crane creak + roof down
    tt_ = s.T(0.32); put(FX, s.filt_short(s.noise(0.32, 5), lo=500, hi=3000) * (tt_ / 0.32) ** 2 * 0.03, T_CHEST, 1.0)
    thud(T_CHEST + 0.32, 55, 0.14, 0.35); nb(T_CHEST + 0.32, 0.3, 200, 2000, 0.02, 6, 1)
    for i in range(4): nb(T_TORCH + 0.15 * i, 0.3, 300, 2500, 0.03, 40 + i, 1); tone(T_TORCH + 0.15 * i, 50, 0.3, 0.008, dec=6, glide=0.5)
    for i, tp in enumerate(T_TREES): pop(tp, 0.025, 79 + 3 * (i % 3))
    nb(T_DRAGON[0], T_DRAGON[1] - T_DRAGON[0], 150, 700, 0.008, 51, 1); thud(T_DRAGON[1], 45, 0.16, 0.45); nb(T_DRAGON[1], 0.4, 100, 1200, 0.02, 52, 1)
    for c, h_, col, ap, nn in BLOCKS:
        if ap is not None: pop(ap, 0.012, 72 + (nn % 5))
    tone(T_WINK, 88, 0.3, 0.025, dec=8, harm=(1.0, 0.0, 0.3)); thud(T_WINK + 0.32, 120, 0.04, 0.12); nb(T_WINK + 0.32, 0.06, 800, 3000, 0.02, 61, 1)   # wink ding + chomp
    cr = s.filt_short(s.noise(1.6, 71), lo=400, hi=3000); put(FX, cr * np.sin(np.pi * s.T(1.6) / 1.6) * 0.03, T0['06'] - 0.1, 1.0)                # cheer
    for x_ in np.arange(T_100, S_PLACES, 1 / 2.6): tone(x_, 84, 0.06, 0.012, dec=30, sq=True)                                                       # PRESS X blips
    for x_ in np.arange(S_100 + 0.95, S_PLACES - 0.1, 0.165): tone(x_, 100, 0.02, 0.006, dec=80)                                                  # eye twitch ticks
    for i, d_ in enumerate((0.0, 0.15, 0.3, 0.45)): nb(T_DIVE[0] + 0.25 + d_, 0.3, 400, 3000, 0.025, 80 + i, 1)
    thud(T_DIVE[0] + 1.0, 140, 0.05, 0.12); tone(T_DIVE[0] + 1.0, 55, 0.25, 0.012, dec=9)                                                         # Bob lands in the pot (hollow)
    for x_ in np.arange(S_HERO - 0.3, T_WALK[1], 0.5): thud(x_, 110, 0.03, 0.1); nb(x_, 0.04, 1500, 5000, 0.008, int(x_ * 91), 1)              # knight steps (metal)
    for kt in (T_KNOCK[0] + 0.12, T_KNOCK[0] + 0.37): thud(kt, 190, 0.07, 0.12); nb(kt, 0.03, 600, 2500, 0.02, int(kt * 13), 1)
    tt_ = s.T(0.35); put(FX, np.sin(2 * np.pi * np.cumsum(1800 + 2200 * tt_ / 0.35) / sr) * 0.008 * np.exp(-tt_ * 4), T_LIFT[0], 1.0)            # sword shing
    nb(T_SMASH, 0.5, 600, 7000, 0.09, 91, 0.6); thud(T_SMASH, 80, 0.12, 0.3)                                                                      # pot SMASH
    for i in range(10): tone(T_SMASH + 0.05 + 0.06 * i + 0.03 * hsh(i, 2), 90 + int(10 * hsh(i, 3)), 0.08, 0.01, dec=30)                            # shards tinkle
    tone(T_TAKE[1], 93, 0.4, 0.03, dec=6, harm=(1.0, 0.0, 0.4)); tone(T_TAKE[1] + 0.08, 100, 0.4, 0.025, dec=6, harm=(1.0, 0.0, 0.4))          # coin ding
    thud(T_STAMP, 70, 0.2, 0.3); nb(T_STAMP, 0.06, 300, 2500, 0.05, 95, 1)                                                                       # STAMP
    tt_ = s.T(0.8); put(FX, np.sin(2 * np.pi * np.cumsum(180 + 60 * np.sin(tt_ * 9)) / sr) * 0.01 * np.sin(np.pi * tt_ / 0.8), T_LEAVE + 0.2, 1.0)   # the door-goblin creaks open
    tt_ = s.T(0.6); put(FX, s.filt_short(s.noise(0.6, 97), lo=400, hi=6000) * (tt_ / 0.6) ** 2 * 0.05, T_FLASH - 0.4, 1.0)                          # flash whoosh
    for k_, m in enumerate((72, 79, 84)): tone(T_RESET + 0.05 * k_, m, 0.4, 0.015, dec=5, sq=True)
    if CTA.on: put(FX, cta.chime(sr), CTA.t0, 1.0)
    # ---- voice
    NB = np.zeros(n); wins = []
    for k_, t0 in LINES:
        f_ = os.path.join(TTS_DIR, 'lt', f'{k_}.wav')
        if not os.path.exists(f_): continue
        a, ar = _sf.read(f_); a = a if a.ndim == 1 else a.mean(1)
        a = np.interp(np.arange(int(len(a) * sr / ar)) / sr, np.arange(len(a)) / ar, a); act = np.abs(a) > 0.02 * np.abs(a).max()
        a = a * (0.12 / np.sqrt((a[act] ** 2).mean())); put(NB, a, t0); wins.append((t0, t0 + len(a) / sr))
    gd = duck_envelope(n, sr, wins, -8.0, 0.05, 0.25) if wins else np.ones(n)
    bed = BED * gd + MUS * (0.5 + 0.5 * gd); fx = FX * (0.7 + 0.3 * gd)
    L = bed + fx; R_ = np.roll(bed, 600) + np.roll(fx, 180)
    pk = max(np.abs(L).max(), np.abs(R_).max()); gv = (pk * 1.6 / np.abs(NB).max()) if np.abs(NB).max() > 0 else 0.0
    s.L = L + NB * gv; s.R = R_ + NB * gv; s.reverb(0.12, length=1.4, decay=3.5)
    fi = np.clip(t / 0.008, 0, 1); s.L = s.L * fi; s.R = s.R * fi
    return s.save(path, peak=0.9)
if __name__ == '__main__' and os.environ.get('PART') == 'audio':
    print(build_audio(os.path.join(OUT, os.environ.get('AUDIO_NAME', 'loading_tips.wav')))); sys.exit()
if __name__ == '__main__' and os.environ.get('PART'):
    a, b = map(int, os.environ['PART'].split(':'))
    import subprocess
    p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W * S}x{H * S}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', os.path.join(OUT, f"{os.environ.get('PART_PREFIX', 'lt')}_{a:05d}.mp4")], stdin=subprocess.PIPE)
    vhs = post.VHS(W * S, H * S, S, grade='none', chroma=0, scan_dark=1.0, vignette=0.1, grain=1.4, band_period=1e9)
    for f in range(a, min(b, N)): p.stdin.write(vhs(frame_final(f / FPS), f, f / FPS).tobytes())
    p.stdin.close(); p.wait(); print('part done', a, b); sys.exit()
