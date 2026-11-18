"""Step 5: the shot timing engine. Frame numbers are authoritative (24 fps, 0-indexed). Every state is a PURE FUNCTION of (cut, frame).
Keyframes are integer frames and linear interpolation only (no easing, no IK at run time, no physics). The only 'solve' is a one-time brute-force
arm-angle search at import for the 'TAKE' pose (so the archer's hand meets the goblin's raised arrow).
"""
import math
import numpy as np
import characters as CH

FPS = 24; FLIGHT = 6; Q0 = 6
ARCHER_POS = (2.8, -0.40); POST = (6.55, 0.0)
WALL_X = 7.0
LANE_DZ = 0.109                           # arrow lane = archer z + 0.109 (the nocked arrow sits at the draw hand)
SLOTS = [(6.62, -0.30, 3), (6.60, -0.37, -4), (6.58, -0.44, 5), (6.64, -0.33, -3), (6.60, -0.41, 4)]    # floor pile: tail x, z, yaw deg (tip x stays < 7.0)

def clamp01(x): return max(0.0, min(1.0, x))
def lerp(a, b, u): return a + (b - a) * u
def ramp(f, f0, f1): return clamp01((f - f0) / (f1 - f0)) if f1 > f0 else (1.0 if f >= f0 else 0.0)

# ============================================================================= cut definitions (the brief's tables, verbatim)
CUTS = {
 'master': dict(
    frames=360, file='MISS_15s_master.mp4',
    cams=[(0, 92, 'A'), (92, 158, 'B'), (158, 264, 'C'), (264, 360, 'D')],
    shots=[('S1', 0, 92), ('S2', 92, 158), ('S3', 158, 235), ('S4', 235, 298), ('S5', 298, 360)],
    releases=[53, 106, 134], ducks=[77, 113, 142], popups=[(70, 'board'), (115, 'board'), (144, 'board'), (350, 'board')],
    moves=[(262, 'floor', 'gob', 1), (312, 'gob', 'archer', 1)],
    walks=[(264, 292), (322, 350)], sheet=[0, 92, 158, 235, 298, 355],
    subs=[(5, 86, 'Why can he never hit a target that never moves?', {'never'}), (96, 139, 'Five shots. Five misses.', {'five'}),
          (163, 226, "It isn't dodging. It's being polite.", {'polite'}), (245, 288, 'So the goblin brings the arrow back...', {'back'}),
          (302, 350, '...and stands in front of the target again.', {'again'})]),
 'extended': dict(
    frames=720, file='MISS_30s_extended.mp4',
    cams=[(0, 92, 'A'), (92, 178, 'B'), (178, 269, 'A'), (269, 437, 'C'), (437, 542, 'E'), (542, 638, 'D'), (638, 720, 'A')],
    shots=[('S1', 0, 92), ('S2', 92, 178), ('S3', 178, 269), ('S4', 269, 350), ('S5', 350, 437), ('S6', 437, 542), ('S7', 542, 638), ('S8', 638, 720)],
    releases=[53, 106, 134, 163, 238], ducks=[77, 113, 142, 170, 686],
    popups=[(70, 'board'), (115, 'board'), (144, 'board'), (173, 'board'), (247, 'wall'), (706, 'board')],
    moves=[(370, 'floor', 'gob', 1), (437, 'floor', 'gob', 2), (504, 'gob', 'crate', 3), (542, 'floor', 'gob', 1), (566, 'gob', 'archer', 1)],
    walks=[(390, 430), (437, 492), (530, 542), (584, 620)], sheet=[0, 92, 178, 269, 350, 437, 542, 638],
    subs=[(5, 86, 'Why can he never hit a target that never moves?', {'never'}), (96, 139, 'Five shots. Five misses.', {'five'}),
          (187, 250, 'This one, he took very seriously.', {'seriously'}), (283, 341, "The target isn't dodging. It's being polite.", {'polite'}),
          (358, 427, 'And every time, it brings the arrow back.', {'back'}), (446, 528, 'A small pile by the wall. Just in case.', {'pile'}),
          (557, 629, 'It has never once been thanked.', {'never', 'thanked'}), (658, 701, 'Not once.', {'once'})]),
}
# the one ramp start that is not derived: the 'took it seriously' draw (feet re-set 185-196, draw held 197-235, release 238)
RAMP_OVERRIDE = {'extended': {238: 189}}
# release poses are held this long before lowering (S3 of the extended cut lowers the bow 250-262)
REL_HOLD = {'extended': {238: 12}}

# ============================================================================= archer
def ov(name):
    A = CH.ARCHER_POSES[name]
    return dict(head_yaw=A['head_yaw'], head_pitch=A['head_pitch'], pitch=A['pitch'], bow_rot=A['bow_rot'], stance=A['stance'], L=A['L'], R=A['R'],
                eyes=A['eyes'], mouth=A['mouth'], draw=1.0 if name == 'DRAW' else 0.0)
def blend_ov(a, b, u):
    o = {}
    for k in ('head_yaw', 'head_pitch', 'pitch', 'bow_rot', 'stance', 'draw'): o[k] = lerp(a[k], b[k], u)
    for k in ('L', 'R'): o[k] = tuple(lerp(a[k][i], b[k][i], u) for i in range(4))
    src = b if u >= 0.5 else a; o['eyes'] = src['eyes']; o['mouth'] = src['mouth']; return o

def solve_arm(shoulder, target, side=(-1, 0, 0), L=0.14):
    """one-time brute-force search (10 degree grid) for two arm segments whose end meets the target; the elbow is pushed outward"""
    sh = np.asarray(shoulder, float); tg = np.asarray(target, float); best = None
    for az1 in range(40, 181, 10):
        for el1 in range(-90, 31, 10):
            E = sh + L * CH.dirv(az1, el1)
            for az2 in range(0, 200, 10):
                for el2 in range(-90, 61, 10):
                    Hh = E + L * CH.dirv(az2, el2); c = float(np.linalg.norm(Hh - tg)) * 100 + 4.0 * max(0.0, float((E - sh) @ np.asarray(side)) * -1)
                    if best is None or c < best[0]: best = (c, (az1, el1, az2, el2), Hh)
    return best
_TAKE = solve_arm((-0.15, 0.71, 0.0), (-0.12, 0.46, 0.12))
TAKE_ERR = float(np.linalg.norm(_TAKE[2] - np.array((-0.12, 0.46, 0.12))))
def take_pose():
    o = ov('IDLE'); o.update(R=_TAKE[1], head_yaw=0, head_pitch=20, eyes='NEUTRAL', mouth='NEUTRAL'); return o

def archer_keys(cut):
    C = CUTS[cut]; rel = C['releases']; ro = RAMP_OVERRIDE.get(cut, {}); rh = REL_HOLD.get(cut, {})
    IDLE, DRAW, REL, LOW, SIGH, HAND, BOARD, TAKE = ov('IDLE'), ov('DRAW'), ov('RELEASE'), ov('LOWER'), ov('SIGH'), ov('LOOK_AT_HAND'), ov('LOOK_AT_BOARD'), take_pose()
    PRE = blend_ov(IDLE, DRAW, 0.7)                           # frame 0: already mid-draw
    K = [(0, PRE), (4, DRAW)]
    for i, r in enumerate(rel):
        if i > 0:
            p = rel[i - 1]; rs = ro.get(r, min(max(p + 16, r - 30), r - 8)); K += [(rs, LOW if rs - (p + 14) < 12 else SIGH), (rs + 8, DRAW)]
        K += [(r, DRAW), (r, REL)]
        hold = rh.get(r, 6); nxt = rel[i + 1] if i + 1 < len(rel) else None
        K += [(r + hold, REL), (r + hold + (12 if r in rh else 8), LOW)]
    last = rel[-1]
    if cut == 'master':
        K += [(last + 26, SIGH), (300, SIGH), (304, TAKE), (312, TAKE), (318, HAND), (326, HAND), (334, BOARD), (340, BOARD), (348, DRAW), (360, DRAW)]
    else:
        K += [(last + 34, SIGH), (542, SIGH), (550, TAKE), (566, TAKE), (574, BOARD), (648, BOARD), (656, DRAW), (694, DRAW), (702, LOW), (720, LOW)]
    # a hard cut is two keys on the same frame (the later one wins at that frame)
    return sorted(K, key=lambda k: k[0])

_KCACHE = {}
def archer_ov(cut, f):
    K = _KCACHE.setdefault(cut, archer_keys(cut)); i = max(j for j, k in enumerate(K) if k[0] <= f) if f >= K[0][0] else 0
    nxt = next((k for k in K[i + 1:] if k[0] > f), None)
    if nxt is None or K[i][0] == nxt[0]: return K[i][1]
    return blend_ov(K[i][1], nxt[1], (f - K[i][0]) / (nxt[0] - K[i][0]))

def tri(f, period=16): return (abs((f % period) - period / 2) - period / 4) / (period / 4)       # linear zig-zag -1..1

def ledger(cut, f):
    """arrow ledger: released == floor + in hands (goblin, archer) + crate + in flight, at EVERY frame"""
    C = CUTS[cut]; rel = C['releases']
    released = sum(1 for r in rel if r <= f); inflight = sum(1 for r in rel if r <= f <= r + FLIGHT); landed = sum(1 for r in rel if f >= r + FLIGHT + 1)
    cnt = dict(floor=landed, gob=0, archer=0, crate=0); slots = list(range(landed))
    for t, a, b, n in C['moves']:
        if f >= t:
            cnt[a] -= n; cnt[b] += n
            if a == 'floor': slots = slots[:-n] if n else slots
    return dict(released=released, inflight=inflight, floor=cnt['floor'], gob=cnt['gob'], archer=cnt['archer'], crate=cnt['crate'], slots=slots, quiver=Q0 - released)

def archer_pos(cut, f):
    z = ARCHER_POS[1] + (-0.07 * ramp(f, 185, 196) if cut == 'extended' else 0.0)      # the extended 'serious' shot: he re-sets his feet
    return (ARCHER_POS[0], z)

def archer_state(cut, f):
    o = archer_ov(cut, f); L = ledger(cut, f); st = dict(pos=archer_pos(cut, f), pose='IDLE', quiver=L['quiver'], roll=1.5 * o['draw'] * tri(f))
    st.update(head_yaw=o['head_yaw'], head_pitch=o['head_pitch'], pitch=o['pitch'], bow_rot=o['bow_rot'], stance=o['stance'], eyes=o['eyes'], mouth=o['mouth'], arms=dict(L=o['L'], R=o['R']))
    st['arrow'] = 'nocked' if o['draw'] > 0.5 else ('hand' if L['archer'] > 0 else 'none')
    return st

_TAIL = {}
def release_lane(cut, r):
    """the arrow's start (tail) and direction at release, taken from the archer model one frame earlier"""
    if (cut, r) not in _TAIL:
        info = CH.archer_info(archer_state(cut, r - 1)); _TAIL[(cut, r)] = (np.array(info['arrow_tail']), np.array(info['arrow_dir']))
    return _TAIL[(cut, r)]

def flying_arrows(cut, f):
    """arrows travelling in a straight line along +X at constant speed, stopping exactly at the wall plane (tip at x = 7.0)"""
    out = []
    for r in CUTS[cut]['releases']:
        if r <= f <= r + FLIGHT:
            tail, d = release_lane(cut, r); end_x = WALL_X - CH.ARROW_TIP; x = lerp(tail[0], end_x, (f - r) / FLIGHT)
            out.append((np.array([x, tail[1], tail[2]]), np.array([1.0, 0, 0])))
    return out

def floor_arrows(cut, f):
    out = []
    for k in ledger(cut, f)['slots']:
        x, z, yaw = SLOTS[k % len(SLOTS)]; a = math.radians(yaw); out.append((np.array([x, 0.014, z]), np.array([math.cos(a), 0, math.sin(a)])))
    return out

# ============================================================================= goblin
def duck_state(f, ducks):
    """DUCK: squash to 0.85 over 6 frames, hold 8, recover 8. returns (squash, weight 0..1)"""
    for d in ducks:
        u = f - d
        if 0 <= u < 22:
            w = u / 6 if u < 6 else (1.0 if u < 14 else 1 - (u - 14) / 8)
            return 1 - 0.15 * w, w
    return 1.0, 0.0

def base_goblin(): return dict(pos=POST, yaw=-90.0, pose='STAND')

def goblin_state(cut, f):
    C = CUTS[cut]; s = base_goblin(); sq, dw = duck_state(f, C['ducks'])
    if dw > 0: s.update(pose='DUCK', squash=sq, head_pitch=12 * dw)
    lg = ledger(cut, f)
    def look_down(a0, a1, b0, b1):                          # look at the arrow pile, then back toward the archer
        a = ramp(f, a0, a1) * (1 - ramp(f, b0, b1))
        if a > 0: s.update(head_yaw=-60 * a, head_pitch=25 * a, pupil=(0, -1) if a > 0.5 else (0, 0))
    def bend_pick(f0, f1):                                  # bend toward the pile (-z side) and pick up one arrow at f1
        a = ramp(f, f0, f0 + 5); b = ramp(f, f0 + 5, f1)
        s.update(pose='LOOK_DOWN', pos=(POST[0], lerp(0.0, -0.12, a)), yaw=lerp(-90.0, -180.0, ramp(f, f0, f0 + 7)), squash=lerp(1.0, 0.8, b), head_pitch=lerp(10, 35, b), arms=dict(L=(60, -35), R=(120, -35)))
    def walk(x0, y0, x1, y1, f0, f1, yaw, carry=True, item='arrow', lift=0.0):
        u = ramp(f, f0, f1); s.update(pose='CARRY' if carry else 'WALK', walk=True, phase=f % 4, pos=(lerp(x0, x1, u), lerp(y0, y1, u)), yaw=yaw, carry=carry, carry_item=item, arm_lift=lift)
    def path_walk(pts, carry=True, lift=0.0):             # piecewise-linear route; each leg carries its own facing (the route bends toward CAM D so the walk stays in frame)
        for (f0, x0, z0, y0), (f1, x1, z1, _) in zip(pts, pts[1:]):
            if f0 <= f < f1:
                u = ramp(f, f0, f1); s.update(pose='CARRY' if carry else 'WALK', walk=True, phase=f % 4, pos=(lerp(x0, x1, u), lerp(z0, z1, u)), yaw=y0, carry=carry, arm_lift=lift)
    gz = archer_pos(cut, 566 if cut == 'extended' else 312)[1] + 0.25            # where he stands to hand the arrow up (in front of the archer)
    HX = 2.68
    if cut == 'master':
        if 173 <= f < 176: s['blink'] = True
        look_down(190, 194, 216, 220)
        if 245 <= f < 262: bend_pick(245, 262)
        elif 262 <= f < 264: s.update(pose='CARRY', carry=True, pos=(POST[0], -0.12), yaw=-180.0, arm_lift=0.0)
        elif 264 <= f < 292:
            path_walk([(264, POST[0], -0.12, lerp(-180.0, -62.0, ramp(f, 264, 270))), (278, 4.6, 0.9, lerp(-120.0, -180.0, ramp(f, 279, 285))), (292, HX, gz, None)])
        elif 292 <= f < 312:
            s.update(pose='CARRY', carry=True, pos=(HX, gz), yaw=-180.0, arm_lift=50 * ramp(f, 296, 304))
        elif 312 <= f < 322: s.update(pose='STAND', pos=(HX, lerp(gz, 0.1, ramp(f, 312, 318))), yaw=lerp(-180.0, -299.8, ramp(f, 316, 322)), arms=dict(L=(0, -90), R=(180, -90)))
        elif 322 <= f < 350: path_walk([(322, HX, 0.1, -299.8), (336, 4.6, 0.9, -245.2), (350, POST[0], 0.0, None)], carry=False)
        elif f >= 350: s.update(pose='STAND', yaw=lerp(-245.2, -450.0, ramp(f, 350, 358)))
    else:
        if 285 <= f < 288: s['blink'] = True
        look_down(300, 304, 322, 326)
        if 355 <= f < 370: bend_pick(355, 370)
        elif 370 <= f < 390: s.update(pose='CARRY', carry=True, pos=(POST[0], -0.12), yaw=lerp(-180.0, -90.0, ramp(f, 370, 380)))
        elif 390 <= f < 437: walk(POST[0], -0.12, 3.2, 0.0, 390, 430, -90.0)
        elif 437 <= f < 492:                                                      # the goblin walks in with a small crate of arrows
            u = ramp(f, 437, 490); s.update(pose='CARRY', walk=True, phase=f % 4, carry=True, carry_item='crate', pos=(lerp(6.75, 6.2, u), lerp(0.65, -0.40, u)), yaw=-144.0 + 0.0, arm_lift=0.0)
        elif 492 <= f < 504: s.update(pose='CARRY', carry=True, carry_item='crate', pos=(6.2, -0.40), yaw=-180.0, squash=lerp(1.0, 0.82, ramp(f, 492, 504)))
        elif 504 <= f < 530:
            b = 1 - ramp(f, 504, 512); s.update(pose='STAND', pos=(6.2, -0.40), yaw=-180.0, squash=lerp(0.82, 1.0, ramp(f, 504, 512)), head_pitch=25 * b)
            for t0 in (514, 521):                                                  # two pats
                if t0 <= f < t0 + 4:
                    k = 1 - abs((f - t0) - 2) / 2; s['arms'] = dict(L=(0, -90), R=(90, -25 - 40 * k)); s['head_pitch'] = 25
            if 524 <= f < 530: s['head_pitch'] = 20
        elif 530 <= f < 542: u = ramp(f, 530, 542); s.update(pose='WALK', walk=True, phase=f % 4, pos=(lerp(6.2, 5.9, u), lerp(-0.40, 0.3, u)), yaw=lerp(-180.0, -90.0, ramp(f, 530, 534)))
        elif 542 <= f < 566: s.update(pose='CARRY', carry=True, pos=(HX, gz), yaw=-180.0, arm_lift=50)
        elif 566 <= f < 584: s.update(pose='STAND', pos=(HX, lerp(gz, 0.1, ramp(f, 566, 574))), yaw=lerp(-180.0, -299.8, ramp(f, 574, 580)), arms=dict(L=(0, -90), R=(180, -90)))
        elif 584 <= f < 620: path_walk([(584, HX, 0.1, -299.8), (602, 4.6, 0.9, -245.2), (620, POST[0], 0.0, None)], carry=False)
        elif f >= 620: s.update(pose='STAND', yaw=lerp(-245.2, -450.0, ramp(f, 620, 630)))
    if cut == 'extended' and 504 <= f < 530 and 'arms' not in s: pass
    return s

def crate_state(cut, f):
    """the small arrow crate once it is set down (extended cut): (centre, yaw) or None. 'straightened' at 528-532"""
    if cut != 'extended' or f < 504: return None
    return (np.array([6.2, 0.035, -0.60]), 8.0 * (1 - ramp(f, 528, 532)))

# ============================================================================= camera, popups, subtitles
def cam_at(cut, f):
    for a, b, k in CUTS[cut]['cams']:
        if a <= f < b: return k, a, b
    a, b, k = CUTS[cut]['cams'][-1]; return k, a, b

def popup_list(cut):
    P = CUTS[cut]['popups']; out = []
    for i, (t0, kind) in enumerate(P):
        end = t0 + 3 + 22 + 4                                         # 3-frame pop-in, hold 22 (0.9 s), 4-frame fade
        if i + 1 < len(P): end = min(end, P[i + 1][0] + 4)            # older popups fade out when a new one appears
        out.append((t0, end, kind))
    return out

def popup_at(cut, f):
    """[(kind, scale, alpha)] for the popups alive at f. never more than two (asserted in qa)"""
    res = []
    for t0, end, kind in popup_list(cut):
        a = f - t0
        if a < 0 or f >= end: continue
        sc = (0.6, 1.15, 1.0)[a] if a < 3 else 1.0
        fade_from = end - 4; al = 1.0 if f < fade_from else (1 - (f - fade_from + 1) / 5)
        if cam_at(cut, f)[1] > t0: kind = 'tr'                       # a popup that survives a hard cut fades out in the top-right corner (it must not sit on the new shot's face)
        res.append((kind, sc, max(0.0, al)))
    return res

def sub_at(cut, f):
    for t0, t1, text, hl in CUTS[cut]['subs']:
        if t0 <= f < t1: return text, hl
    return None

# ============================================================================= audio events (frame-based)
def audio_events(cut):
    C = CUTS[cut]; ev = []
    for i, r in enumerate(C['releases']):
        ev += [('bow_creak', r - 8), ('release', r), ('arrow_whoosh', r), ('arrow_thud', r + FLIGHT)]
    for t, kind in C['popups']: ev.append(('ui_ding' if (cut == 'extended' and t == 706) else 'miss_blip', t))
    for d in C['ducks']: ev.append(('duck_step', d))
    for a, b in C['walks']:
        for f in range(a, b, 4): ev.append(('footstep', f))
    if cut == 'extended': ev += [('crate_set', 504), ('pat', 514), ('pat', 521), ('bow_creak', 664)]
    return sorted(ev, key=lambda e: e[1])
