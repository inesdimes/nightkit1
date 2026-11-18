"""Step 3: the two LOCKED characters, built once as parameterized constructors and reusable in future videos.
  make_archer(state) -> faces        make_goblin(state) -> faces        make_arrow(tail, direction) -> faces
Both are pure functions of the state dict (the timeline turns a frame number into a state). Characters are built in a local frame:
+Y up, +Z = the way the character faces, +X = the character's LEFT. Then yaw (degrees about +Y) and position (x, z) place them in the world.
Everything is axis-aligned or simply rotated boxes (no spheres, no cylinders); poses are integer joint angles, no IK, no easing."""
import math
import numpy as np
from raster import (mat, aabb, oriented_box, limb_box, quad_face, transform_faces, squash_faces, rot_x, rot_y, rot_z, Face)

D = math.radians

def dirv(az, el):
    """azimuth (deg) in the local XZ plane from +X toward +Z, elevation (deg) above the horizontal"""
    a, e = D(az), D(el); return np.array([math.cos(e) * math.cos(a), math.sin(e), math.cos(e) * math.sin(a)])

def _basis(u):
    u = np.asarray(u, float); u = u / np.linalg.norm(u); ref = np.array([0, 1.0, 0]) if abs(u[1]) < 0.9 else np.array([1.0, 0, 0])
    v = np.cross(ref, u); v /= np.linalg.norm(v); w = np.cross(u, v); return np.stack([u, v, w], 1)

def _group(faces, R, pivot):
    """rotate a group of faces about a pivot"""
    pivot = np.asarray(pivot, float); return transform_faces(faces, R, pivot - np.asarray(R) @ pivot)

def _rot_pt(R, pivot, p):
    pivot = np.asarray(pivot, float); return np.asarray(R) @ (np.asarray(p, float) - pivot) + pivot

# ============================================================================= ARROW
ARROW_SHAFT = '#C9B27E'; ARROW_HEAD = '#9AA0A6'; ARROW_FLETCH = '#B33A3A'
ARROW_LEN = 0.30; ARROW_TIP = 0.33            # shaft + head: the tip is 0.33 from the tail

def make_arrow(tail, direction, scale=1.0):
    """one thin shaft 0.30 x 0.008 x 0.008, a 0.03 arrowhead and a 0.04 fletching. tail = back end of the arrow, direction = unit vector"""
    t = np.asarray(tail, float); d = np.asarray(direction, float); d = d / np.linalg.norm(d); B = _basis(d); s = scale
    F = limb_box(t, t + d * ARROW_LEN * s, 0.008, mat(ARROW_SHAFT))
    F += oriented_box(t + d * (ARROW_LEN + 0.015) * s, B, (0.015 * s, 0.008, 0.008), mat(ARROW_HEAD))
    F += oriented_box(t + d * 0.02 * s, B, (0.02 * s, 0.014, 0.003), mat(ARROW_FLETCH))
    return F

CRATE_SIZE = (0.10, 0.07, 0.07)
def make_arrow_crate(center, yaw_deg=0.0, n=3):
    """the small crate of arrows the goblin brings in the extended cut: one box + n shafts sticking out (n is visible)"""
    c = np.asarray(center, float); F = aabb(c, CRATE_SIZE, mat('#6B5638'))
    for i in range(n):
        x = (i - (n - 1) / 2) * 0.028; F += limb_box(c + [x, 0.02, 0], c + [x, 0.12, 0.0], 0.009, mat(ARROW_SHAFT)) + aabb(c + [x, 0.11, 0], (0.014, 0.025, 0.004), mat(ARROW_FLETCH))
    return transform_faces(F, rot_y(D(yaw_deg)), c - rot_y(D(yaw_deg)) @ c)

# ============================================================================= ARCHER
C_HOOD = '#2E2A3A'; C_TUNIC = '#3E7A6B'; C_SKIN = '#C9A27E'; C_BOOT = '#6B4A2F'; C_QUIVER = '#4A3B2A'; C_EYE = '#1E1E1E'; C_BOW = '#6B4A2F'; C_STRING = '#D8D0B8'
HIP_Y = 0.44

# poses: integer joint angles. arm = (upper az, upper el, lower az, lower el), each segment 0.14 long. az from +X toward +Z (local), el above horizontal.
ARCHER_POSES = {
 'IDLE':          dict(L=(-10, -75, 85, -75), R=(95, -75, 190, -75), head_yaw=0,   head_pitch=0,  pitch=0, eyes='NEUTRAL', mouth='NEUTRAL', arrow=None,    bow_rot=0,  stance=0.065),
 'DRAW':          dict(L=(20, 0, 45, 0),      R=(95, 30, -5, -5),    head_yaw=60,  head_pitch=0,  pitch=0, eyes='SQUINT',  mouth='FLAT',    arrow='nocked', bow_rot=3, stance=0.10),
 'RELEASE':       dict(L=(25, 20, 40, -15),   R=(200, -50, 210, 75), head_yaw=60,  head_pitch=0,  pitch=0, eyes='NEUTRAL', mouth='FLAT',    arrow=None,    bow_rot=-2, stance=0.10),
 'LOWER':         dict(L=(25, -30, 75, -60),  R=(95, -75, 190, -75), head_yaw=40,  head_pitch=5,  pitch=0, eyes='NEUTRAL', mouth='FLAT',    arrow=None,    bow_rot=0,  stance=0.075),
 'LOOK_AT_HAND':  dict(L=(-10, -75, 85, -75), R=(90, 10, 50, -55),   head_yaw=-20, head_pitch=25, pitch=0, eyes='NEUTRAL', mouth='NEUTRAL', arrow='hand', bow_rot=0,  stance=0.065),
 'LOOK_AT_BOARD': dict(L=(-30, -65, 90, -60), R=(95, -75, 190, -75), head_yaw=85,  head_pitch=0,  pitch=0, eyes='NEUTRAL', mouth='FLAT',    arrow=None,    bow_rot=0,  stance=0.065),
 'SIGH':          dict(L=(-10, -75, 85, -75), R=(95, -75, 190, -75), head_yaw=0,   head_pitch=8,  pitch=2, eyes='NEUTRAL', mouth='SMALL_O', arrow=None,    bow_rot=0,  stance=0.065),
}
ARCHER_DEFAULT = dict(pos=(2.8, -0.40), stance=None, yaw=0.0, pose='IDLE', eyes=None, mouth=None, quiver=6, arrow=None, roll=0.0, pitch=None, head_yaw=None, head_pitch=None, bow_rot=None, arms=None)

def _archer(state):
    s = dict(ARCHER_DEFAULT); s.update(state); P = dict(ARCHER_POSES[s['pose']])
    for k in ('head_yaw', 'head_pitch', 'pitch', 'bow_rot', 'eyes', 'mouth'):
        if s[k] is not None: P[k] = s[k]
    if s['stance'] is not None: P['stance'] = s['stance']
    if s['arrow'] is not None: P['arrow'] = None if s['arrow'] == 'none' else s['arrow']
    if s['arms'] is not None: P.update(s['arms'])
    tunic, boot = mat(C_TUNIC), mat(C_BOOT)
    legs, upper = [], []
    # ---- legs: upper 0.22 + lower 0.22 (a 0.12 shin and a 0.10 boot), hips at y=0.44
    for sx in (1, -1):
        hip = np.array([sx * 0.065, HIP_Y, 0]); ank = np.array([sx * P['stance'], 0.10, 0.0]); kn = (hip + ank) / 2 + np.array([0, 0.0, 0.0]); kn[1] = 0.22
        legs += limb_box(hip, kn, 0.075, tunic) + limb_box(kn, ank, 0.065, tunic) + aabb((sx * P['stance'], 0.05, 0.02), (0.08, 0.10, 0.12), boot)
    # ---- upper body (everything above the hip rotates together for the sway / the sigh dip)
    upper += aabb((0, 0.59, 0), (0.22, 0.30, 0.14), tunic) + aabb((0, 0.71, 0), (0.30, 0.06, 0.12), tunic)
    # quiver on the back (-z): a tilted box with one shaft per remaining arrow
    qB = rot_z(D(14)); qc = np.array([-0.16, 0.66, -0.10])
    upper += oriented_box(qc, qB, (0.03, 0.11, 0.03), mat(C_QUIVER))
    qtop = qc + qB @ np.array([0, 0.11, 0])
    for i in range(int(s['quiver'])):
        off = (i - 2.5) * 0.011; base = qtop + qB @ np.array([off, 0, 0.012 * ((i % 2) - 0.5)])
        upper += limb_box(base - qB @ np.array([0, 0.02, 0]), base + qB @ np.array([0, 0.10, 0]), 0.010, mat(ARROW_SHAFT))
        upper += aabb(base + qB @ np.array([0, 0.095, 0]), (0.014, 0.025, 0.004), mat(ARROW_FLETCH))
    # ---- arms (two segments each, thin, no hands: the lower arm box just ends)
    SL, SR = np.array([0.15, 0.71, 0.0]), np.array([-0.15, 0.71, 0.0]); pts = {}
    for name, S_, a in (('L', SL, P['L']), ('R', SR, P['R'])):
        E = S_ + 0.14 * dirv(a[0], a[1]); Hh = E + 0.14 * dirv(a[2], a[3]); pts[name] = (S_, E, Hh)
        upper += limb_box(S_, E, 0.05, tunic) + limb_box(E, Hh, 0.05, tunic)
    hand_L, hand_R = pts['L'][2], pts['R'][2]
    # ---- head: hood box 0.26 x 0.22 x 0.20 + a hood peak (0.26 total with the peak), a flat skin panel, two eyes, one mouth. face texture = swappable quads
    head = aabb((0, 0.85, 0), (0.26, 0.22, 0.20), mat(C_HOOD)) + oriented_box((0, 0.958, -0.035), rot_x(D(-25)), (0.05, 0.022, 0.05), mat(C_HOOD))
    head += aabb((0, 0.855, 0.101), (0.16, 0.12, 0.004), mat(C_SKIN))
    ez = 0.1035; eye = mat(C_EYE)
    def q(cx, cy, w, h, z=ez): return quad_face([(cx - w / 2, cy - h / 2, z), (cx + w / 2, cy - h / 2, z), (cx + w / 2, cy + h / 2, z), (cx - w / 2, cy + h / 2, z)], eye, up=(0, 0, 1))
    if P['eyes'] == 'NEUTRAL': head += [q(-0.035, 0.875, 0.020, 0.020), q(0.035, 0.875, 0.020, 0.020)]
    elif P['eyes'] == 'SQUINT': head += [q(-0.035, 0.875, 0.020, 0.008), q(0.035, 0.875, 0.020, 0.008)]
    my = 0.815
    if P['mouth'] == 'NEUTRAL': head += [q(0, my, 0.030, 0.006)]
    elif P['mouth'] == 'FLAT': head += [q(0, my - 0.004, 0.030, 0.006)]
    elif P['mouth'] == 'SMALL_O': head += [q(0, my, 0.014, 0.014)]
    neck = np.array([0, 0.74, 0]); Rh = rot_y(D(P['head_yaw'])) @ rot_x(D(P['head_pitch'])); head = _group(head, Rh, neck)
    upper += head
    # ---- bow: held in the left hand. three thin boxes forming a shallow arc (0.34 tall, 0.06 deep) + ONE straight string box. the bow plane sits 0.035 BEHIND the arm
    # (-z), so the string can never touch the arm. the string is a straight line and never bends: during a draw only the whole bow tilts a few degrees.
    Bc = hand_L + np.array([0, 0, -0.035]); wood = mat(C_BOW)
    bow = aabb(Bc, (0.05, 0.10, 0.04), wood)
    bow += limb_box(Bc + [0, 0.05, 0], Bc + [-0.06, 0.17, 0], 0.025, wood, 0.03) + limb_box(Bc + [0, -0.05, 0], Bc + [-0.06, -0.17, 0], 0.025, wood, 0.03)
    string = aabb(Bc + [-0.06, 0, 0], (0.005, 0.34, 0.005), mat(C_STRING))
    Rb = rot_z(D(P['bow_rot'])); bow = _group(bow, Rb, Bc); string = _group(string, Rb, Bc)
    upper += bow + string
    # ---- arrow (nocked: along +x, resting above the grip, tail at the right hand; or held in the right hand)
    info = {}
    if P['arrow'] == 'nocked':
        lane_y = Bc[1] + 0.052; tail = np.array([hand_R[0], lane_y, Bc[2]]); upper += make_arrow(tail, (1, 0, 0)); info['arrow_tail'] = tail; info['arrow_dir'] = np.array([1.0, 0, 0])
    elif P['arrow'] == 'hand':
        d = np.array([0.0, 0.6, 0.8]); tail = hand_R - d * 0.06; upper += make_arrow(tail, d)
    # ---- upper-body group transform: roll (sway) about z, pitch (the sigh dip) about x, both through the hips
    pv = np.array([0, HIP_Y, 0]); Ru = rot_z(D(s['roll'])) @ rot_x(D(P['pitch'])); upper = _group(upper, Ru, pv)
    yaw = rot_y(D(s['yaw'])); t = np.array([s['pos'][0], 0, s['pos'][1]])
    W_ = lambda p: yaw @ _rot_pt(Ru, pv, p) + t                                   # local point -> world point (the same chain the faces go through)
    if 'arrow_tail' in info: info['arrow_tail'] = W_(info['arrow_tail']); info['arrow_dir'] = yaw @ Ru @ info['arrow_dir']
    info['hand_L'] = W_(hand_L); info['hand_R'] = W_(hand_R); info['bow_grip'] = W_(Bc)
    info['elbow_L'] = W_(pts['L'][1]); sa = _rot_pt(Rb, Bc, Bc + np.array([-0.06, 0.17, 0])); sb = _rot_pt(Rb, Bc, Bc + np.array([-0.06, -0.17, 0])); info['string_a'] = W_(sa); info['string_b'] = W_(sb)
    chain = lambda F: transform_faces(_group(F, Ru, pv), yaw, t)
    info['string_aabb'] = _faces_aabb(chain(string)); info['left_forearm_aabb'] = _faces_aabb(chain(limb_box(pts['L'][1], pts['L'][2], 0.05, tunic)))
    faces = transform_faces(legs + upper, yaw, t)
    return faces, info

def make_archer(state): return _archer(state)[0]
def archer_info(state): return _archer(state)[1]

def _faces_aabb(faces):
    p = np.concatenate([f.p for f in faces]); return (p.min(0), p.max(0))

# ============================================================================= GOBLIN
C_GOB = '#6FA84A'; C_EAR = '#5C8F3D'; C_LOIN = '#8A6A3A'; C_SCLERA = '#F2F2EA'; C_PUPIL = '#1E1E1E'
GOBLIN_POSES = {          # arm = (az, el), one 0.14 segment each; leg swing in degrees about the hip (forward = +z)
 'STAND':   dict(L=(0, -90), R=(180, -90)),
 'BLINK':   dict(L=(0, -90), R=(180, -90), blink=True),
 'DUCK':    dict(L=(0, -70), R=(180, -70), head_pitch=12, squash=0.85),
 'LOOK_DOWN': dict(L=(0, -90), R=(180, -90), head_pitch=25, pupil=(0, -1)),
 'LOOK_AT_ARCHER': dict(L=(0, -90), R=(180, -90), pupil=(0, 0)),
 'WALK':    dict(L=(0, -90), R=(180, -90)),
 'CARRY':   dict(L=(110, 0), R=(70, 0), carry=True),
 'NOD':     dict(L=(0, -90), R=(180, -90), head_pitch=3),
 'SHRUG':   dict(L=(0, -80), R=(180, -80)),
}
WALK_CYCLE = [(25, -25, 0.0), (0, 0, 0.012), (-25, 25, 0.0), (0, 0, 0.012)]   # (left leg swing, right leg swing, body lift): a 4-frame cycle
GOBLIN_DEFAULT = dict(pos=(6.55, 0.0), arms=None, walk=False, arm_lift=0.0, carry_item='arrow', yaw=-90.0, pose='STAND', head_yaw=0.0, head_pitch=None, pupil=None, blink=None, squash=None, phase=0, carry=None)

def _goblin(state):
    s = dict(GOBLIN_DEFAULT); s.update(state); P = dict(GOBLIN_POSES[s['pose']])
    for k in ('head_pitch', 'pupil', 'blink', 'squash', 'carry'):
        if s[k] is not None: P[k] = s[k]
    P.setdefault('head_pitch', 0); P.setdefault('pupil', (0, 0)); P.setdefault('blink', False); P.setdefault('squash', 1.0); P.setdefault('carry', False)
    body = mat(C_GOB); F = []; lift = 0.0; swing = (0, 0)
    if s['arms']: P.update(s['arms'])
    if s['pose'] == 'WALK' or s['walk']: a, b, lift = WALK_CYCLE[s['phase'] % 4]; swing = (a, b)
    for sx, sw in ((1, swing[0]), (-1, swing[1])):                                   # legs: two short boxes, 0.16 tall
        hip = np.array([sx * 0.04, 0.16 + lift, 0]); end = hip + 0.16 * np.array([0, -math.cos(D(sw)), math.sin(D(sw))])
        F += limb_box(hip, end, 0.065, body, 0.07)
    F += aabb((0, 0.14 + lift, 0), (0.14, 0.07, 0.105), mat(C_LOIN))                  # loincloth
    F += aabb((0, 0.24 + lift, 0), (0.14, 0.16, 0.10), body)                          # torso 0.16
    # arms (one 0.14 segment each); in the walk they swing opposite to the legs
    arms = {}
    for sx, key in ((1, 'L'), (-1, 'R')):
        az, el = P[key]; el = el + (s['arm_lift'] if P['carry'] else 0); sh = np.array([sx * 0.095, 0.30 + lift, 0]); d = dirv(az, el)
        if s['pose'] == 'WALK':                                                     # in the walk the arms swing opposite to the same-side leg
            ang = D(swing[1 if sx == 1 else 0]) * 0.9; d = np.array([sx * 0.05, -math.cos(ang), math.sin(ang)]); d /= np.linalg.norm(d)
        arms[key] = sh + 0.14 * d; F += limb_box(sh, arms[key], 0.04, body)
    if P['carry']:                                                                  # the arrow (or the small arrow crate) lies across both hands
        mid = (arms['L'] + arms['R']) / 2
        F += make_arrow(mid - np.array([0.15, 0, 0]), (1, 0, 0)) if s['carry_item'] == 'arrow' else make_arrow_crate(mid + np.array([0, 0.045, 0.02]), 0.0, 3)
    # head: 0.20 x 0.16 x 0.16 box + two big ears angled outward; eyes (sclera + pupil), one mouth line
    head = aabb((0, 0.404 + lift, 0), (0.20, 0.16, 0.16), body)
    for sx in (1, -1): head += oriented_box((sx * 0.15, 0.472 + lift, 0), rot_z(D(sx * 25)), (0.05, 0.03, 0.01), mat(C_EAR))
    zf = 0.0815; sc, pu, dk = mat(C_SCLERA), mat(C_PUPIL), mat(C_PUPIL)
    def q(cx, cy, w, h, m, z=zf): return quad_face([(cx - w / 2, cy - h / 2, z), (cx + w / 2, cy - h / 2, z), (cx + w / 2, cy + h / 2, z), (cx - w / 2, cy + h / 2, z)], m, up=(0, 0, 1))
    ey = 0.419 + lift
    for sx in (1, -1):
        if P['blink']: head += [q(sx * 0.045, ey, 0.045, 0.008, dk)]
        else:
            head += [q(sx * 0.045, ey, 0.045, 0.05, sc)]
            px, py = P['pupil']; head += [q(sx * 0.045 + px * 0.012, ey + py * 0.012, 0.02, 0.025, pu, zf + 0.0006)]
    head += [q(0, 0.359 + lift, 0.05, 0.004, dk)]
    neck = np.array([0, 0.32 + lift, 0]); Rh = rot_y(D(s['head_yaw'])) @ rot_x(D(P['head_pitch'])); F += _group(head, Rh, neck)
    yaw = rot_y(D(s['yaw'])); t = np.array([s['pos'][0], 0, s['pos'][1]]); faces = transform_faces(F, yaw, t)
    if P['squash'] != 1.0: faces = squash_faces(faces, P['squash'])
    return faces

def make_goblin(state): return _goblin(state)
