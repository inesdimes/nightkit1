"""Body acting for hd humans (Insert Disc 2, 28 Nov 2026) - phase 3 of the human performance system.
A gesture library + a Performer that turns a timeline of gestures into hd pose dicts, with the animation principles built in:
anticipation + overshoot on the arms, the head arriving a beat after the body, breathing, a slow idle weight shift, and per-gesture
oscillation (waving, clapping, laughing, sobbing). Face (nightkit/face.py) and fingers (nightkit/hands.py) come along with each gesture.

    perf = body.Performer(S, [(0.0, 'idle'), (0.6, 'wave'), (2.0, 'shrug'), (3.4, 'arms_crossed', dict(face='smug'))])
    P = perf.at(t, talk=amp); P.update(base=..., yaw=...); Q = hd.human(S, P)
    body.point_at(S, target_world, base, yaw)        # a gesture dict that points the nearer arm at a world point
    body.GESTURES                                    # names: see the table below

Everything is opt-in through new pose keys (rhc / palm_c / pole_c / shrug, see hd.human); scripts that do not use body.py are unchanged.
Arm targets are in the CHEST frame (origin at the chest point, x = the character's right, y = up, z = forward), so the arms ride
along when the torso leans, twists or bows."""
import math
import numpy as np
from . import hd, hands, face as facemod
V = np.array

def arm(x, y, z, palm=(-1, 0, 0.2), pole=(0.5, -0.3, -1.0), fingers='relaxed', wrist=(0.0, 0.0), shrug=(0.0, 0.0)):
    """one arm, written for the RIGHT side (x = out to the right); mirror() makes the left"""
    return dict(hc=(x, y, z), palm_c=tuple(palm), pole_c=tuple(pole), fingers=fingers, wrist=tuple(wrist), shrug=tuple(shrug))
def mirror(a):
    m = dict(a); m['hc'] = (-a['hc'][0],) + tuple(a['hc'][1:]); m['palm_c'] = (-a['palm_c'][0],) + tuple(a['palm_c'][1:])
    m['pole_c'] = (-a['pole_c'][0],) + tuple(a['pole_c'][1:]); return m
REST = arm(0.25, -0.46, 0.04)
def both(a): return dict(r=a, l=mirror(a))
# gesture = dict(r=arm, l=arm (in RIGHT-side coordinates only when made with both(); explicit l arms are written as-is),
#                body channels (lean, twist, side, crouch, pel, head=(yaw, nod, tilt), rf, lf, rkpole, lkpole),
#                face = preset or (preset, overrides), osc = [(channel, index, amplitude, Hz)])
GESTURES = {
    'idle':         dict(**both(REST)),
    'wave':         dict(r=arm(0.34, 0.36, 0.1, palm=(0, 0, 1), pole=(1, -0.6, 0), fingers='wave'), l=mirror(REST),
                         head=(0.0, 0.0, -0.08), face='laughing', osc=[('rwrist', 1, 0.38, 2.4)]),
    'point_fwd':    dict(r=arm(0.25, 0.13, 0.5, palm=(0, -1, 0), pole=(1, -0.8, -0.2), fingers='point'), l=mirror(REST), face='determined'),
    'shrug':        dict(**both(arm(0.3, -0.24, 0.24, palm=(0.25, 1, 0.15), pole=(1, -1, -0.5), fingers='open', shrug=(0.055, 0.0))),
                         head=(0.0, -0.04, 0.2), face=('deadpan', dict(browR=0.7, browL=0.5, smR=-0.3, smL=-0.3))),
    'arms_crossed': dict(r=arm(-0.11, -0.25, 0.2, palm=(0, 0, -1), pole=(1, -0.3, 0.5), fingers=hands.pose('grip', r=0.045), wrist=(0.8, 0.0)),     # right forearm under,
                         l=dict(hc=(0.12, -0.1, 0.25), palm_c=(0, 0, -1), pole_c=(-1, -0.3, 0.5), fingers=hands.pose('grip', r=0.045), wrist=(0.8, 0.0), shrug=(0.0, 0.0)),   # left on top
                         lean=-0.04, head=(0.0, -0.06, 0.0), face='smug'),
    'hips':         dict(**both(arm(0.21, -0.33, 0.0, palm=(-1, -0.2, 0.3), pole=(1, 0.0, -0.8), fingers='relaxed', wrist=(-0.5, 0.0))),
                         lean=-0.06, head=(0.0, -0.1, 0.0), face='proud'),
    'facepalm':     dict(r=arm(0.03, 0.2, 0.2, palm=(0, 0.2, -1), pole=(1, -1, 0.1), fingers='open', wrist=(-0.6, 0.0)), l=mirror(REST),
                         lean=0.08, head=(0.0, 0.3, 0.06), face=('deadpan', dict(eyesR=0.0, eyesL=0.0, smR=-0.4, smL=-0.4))),
    'think':        dict(r=arm(0.05, 0.12, 0.21, palm=(-1, 0.3, 0), pole=(1, -1, -0.2), fingers='relaxed', wrist=(-0.4, 0.0)),
                         l=dict(hc=(0.06, -0.22, 0.26), palm_c=(0, 1, 0), pole_c=(-1, -0.6, 0.3), fingers='relaxed', wrist=(0.0, 0.0), shrug=(0.0, 0.0)),
                         head=(0.15, -0.12, 0.12), face=('neutral', dict(look=(0.5, 0.6), browR=0.4, browL=-0.1, press=0.5))),
    'cheer':        dict(**both(arm(0.28, 0.62, 0.06, palm=(-1, 0, 0), pole=(1, 0.0, -0.5), fingers='fist')), lean=-0.1, head=(0.0, -0.15, 0.0),
                         face='laughing', osc=[('rhc', 1, 0.03, 2.0), ('lhc', 1, 0.03, 2.0)]),
    'fist_pump':    dict(r=arm(0.22, -0.06, 0.28, palm=(-1, 0, 0), pole=(1, -1, 0.0), fingers='fist'), l=mirror(REST), crouch=0.04, lean=0.1, face='determined'),
    'hands_up':     dict(**both(arm(0.36, 0.3, 0.14, palm=(0, 0, 1), pole=(1, -0.8, -0.3), fingers='spread', wrist=(-1.0, 0.0))), lean=-0.12, face='scared'),
    'salute':       dict(r=arm(0.23, 0.25, 0.15, palm=(-0.2, -0.5, 1), pole=(1, -0.1, 0.0), fingers=hands.pose('open', spread=0.0, thumb=(0.0, 0.2, 0.0))),
                         l=mirror(REST), head=(0.0, -0.05, 0.0), face='determined'),
    'scratch_head': dict(r=arm(0.1, 0.38, -0.02, palm=(-1, -0.5, 0), pole=(1, 0.2, 0.4), fingers='claw'), l=mirror(REST),
                         head=(0.0, 0.05, -0.15), face='embarrassed', osc=[('rwrist', 0, 0.3, 3.0)]),
    'clap':         dict(**both(arm(0.062, -0.08, 0.36, palm=(-1, 0, 0), pole=(1, -1, -0.3), fingers=hands.pose('open', spread=0.0), wrist=(-0.5, 1.2))), face='laughing',
                         osc=[('rhc', 0, 0.034, 3.0), ('lhc', 0, -0.034, 3.0)]),     # palms meet flat, fingers up and together (bodycheck: no finger through the other hand)
    'bow':          dict(**both(arm(0.23, -0.44, 0.12)), lean=0.6, head=(0.0, 0.25, 0.0), face=('neutral', dict(eyesR=0.15, eyesL=0.15))),
    'laugh':        dict(**both(arm(0.155, -0.28, 0.16, palm=(0, 0, -1), pole=(1, -1, -0.4), fingers='open')), lean=-0.12, head=(0.0, -0.2, 0.0),
                         face='laughing', osc=[('lean', None, 0.04, 4.0), ('rshrug', 0, 0.012, 4.0), ('lshrug', 0, 0.012, 4.0)]),
    'cry':          dict(**both(arm(0.088, 0.19, 0.2, palm=(0, 0, -1), pole=(1, -1, 0.0), fingers='relaxed', wrist=(-0.6, 0.5))),
                         lean=0.12, head=(0.0, 0.3, 0.0), face='sad', osc=[('rshrug', 0, 0.014, 3.0), ('lshrug', 0, 0.014, 3.0)]),
    'shocked':      dict(**both(arm(0.2, 0.08, 0.26, palm=(0, 0, 1), pole=(1, -1, -0.2), fingers='spread', wrist=(-1.0, 0.0))), lean=-0.15,
                         head=(0.0, -0.08, 0.0), face='shocked'),
    'slump':        dict(**both(arm(0.2, -0.47, 0.16, fingers='relaxed', shrug=(-0.035, 0.07))), lean=0.34, crouch=0.05, head=(0.0, 0.45, 0.0), face='sad'),
    'proud':        dict(**both(arm(0.21, -0.33, 0.0, palm=(-1, -0.2, 0.3), pole=(1, 0.0, -0.8), fingers='relaxed', wrist=(-0.5, 0.0))),
                         lean=-0.1, head=(0.0, -0.14, 0.0), face='proud'),
    'kneel':        dict(r=arm(0.25, -0.33, 0.27, palm=(-0.6, -0.6, 0.3), pole=(1, -0.5, -0.4), wrist=(0.3, 0.0)),
                         l=mirror(arm(0.2, -0.4, 0.17, palm=(-1, 0, 0.4), pole=(0.6, -0.3, -1.0), fingers='relaxed')),
                         crouch=0.44, lean=0.36, twist=-0.12, side=0.04, head=(0.06, 0.42, 0.05),
                         face=('neutral', dict(eyesR=0.55, eyesL=0.55, browR=-0.1, browL=-0.1, press=0.3)),
                         rf=(0.11, 0.075, 0.36), lf=(-0.11, 0.07, -0.44), rkpole=(0.1, 0.0, 1.0), lkpole=(-0.05, -1.0, 0.25),
                         osc=[('lean', None, 0.012, 0.25)]),
}
BODY = dict(lean=0.0, twist=0.0, side=0.0, crouch=0.0, pel=(0.0, 0.0, 0.0), head=(0.0, 0.0, 0.0))
FEET = dict(rf=(0.11, 0.075, 0.02), lf=(-0.11, 0.075, 0.02), rkpole=(0.15, 0.0, 1.0), lkpole=(-0.15, 0.0, 1.0))

def point_at(S, target, base=(0, 0, 0), yaw=0.0, face='determined'):
    """a gesture that points the nearer arm straight at a world point (both arms otherwise at rest)"""
    k = S['h'] / 1.78; bw = S['build']
    Ri = hd.Ry(yaw).T; tl = Ri @ (V(target, float) - V(base, float))                       # target in the body frame
    side = 1 if tl[0] >= 0 else -1
    sh = V((side * 0.178 * bw, 1.38 * k, -0.01)); d = tl - sh; d = d / (np.linalg.norm(d) + 1e-9)
    reach = 0.535 * k; x, y, z = d * reach + V((side * 0.178 * bw, 0.05 * k, -0.01))
    a = arm(abs(x), y, z, palm=(0, -1, 0), pole=(1, -1, -0.2), fingers='point')
    if side > 0: return dict(r=a, l=mirror(REST), face=face)
    return dict(r=REST, l=mirror(a), face=face)

# ---------------- flattening + blending ----------------
def _flat(G, k, bw, feet):
    """gesture -> full channel dict (lengths scaled to the character)"""
    out = {}
    for sd, key in (('r', 'r'), ('l', 'l')):
        a = G.get(key, REST if key == 'r' else mirror(REST))
        x, y, z = a['hc']; out[key + 'hc'] = (x * bw, y * k, z * k)
        out[key + 'palm_c'] = tuple(a['palm_c']); out[key + 'pole_c'] = tuple(a['pole_c'])
        f = a['fingers']; out[key + 'fingers'] = hands.pose(f) if isinstance(f, str) else dict(f)
        out[key + 'wrist'] = tuple(a['wrist']); out[key + 'shrug'] = tuple(a['shrug'])
    for c, v in BODY.items(): out[c] = G.get(c, v)
    if feet:
        for c, v in FEET.items(): out[c] = G.get(c, v)
    return out
def _lerp(a, b, u):
    if isinstance(a, dict): return hands.blend(a, b, u)
    if isinstance(a, tuple): return tuple(x + (y - x) * u for x, y in zip(a, b))
    return a + (b - a) * u
def _back(u, s=0.07):                                          # slow in, a small overshoot past the pose, settle (follow-through)
    u = min(1.0, max(0.0, u)); a = min(1.0, u * 1.18); e = a * a * a * (a * (a * 6 - 15) + 10)
    return e + s * math.sin(math.pi * min(1.0, max(0.0, (u - 0.62) / 0.38))) ** 2       # sin^2: no speed jump where it starts / ends
def _slerp(a, b, u):
    om = math.acos(max(-1.0, min(1.0, float(a @ b))))
    if om < 1e-4: return a
    return (math.sin((1 - u) * om) * a + math.sin(u * om) * b) / math.sin(om)
def _dlerp(a, b, u):
    """a direction-like vector turned from a to b (slerp of the direction, lerp of the length) - never shrinks through zero"""
    a, b = V(a), V(b); na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-9 or nb < 1e-9: return tuple(a + (b - a) * u)
    da, db = a / na, b / nb; L = na + (nb - na) * u
    if da @ db > -0.99: return tuple(_slerp(da, db, u) * L)
    m = V((0, 0, 1.0)) if abs(da[2]) < 0.9 else V((0, 1.0, 0))          # opposite: turn via a side direction
    m = m - da * (m @ da); m = m / np.linalg.norm(m)
    return tuple((_slerp(da, m, u * 2) if u < 0.5 else _slerp(m, db, u * 2 - 1)) * L)
def _raw_human(): return getattr(hd.human, '__wrapped__', hd.human)   # unwrapped by bodycheck.install: internal still poses are not characters
def _smooth(u): u = min(1.0, max(0.0, u)); return u * u * (3 - 2 * u)
ARM = ('hc', 'palm_c', 'pole_c', 'wrist', 'shrug')
HEAD_PAD = 0.06                                                  # extra head keep-out for the hand path in transit (finger length)
X_AMP, X_POW, X_UP = 0.16, 1.0, 0.5                              # crossed arms: the top arm lifts over the other forearm in transit (grid-searched: 0 hits on 8 transitions)

class Performer:
    """keys = [(t, gesture name or dict, opts?)]; opts: blend (s; default from the hand travel, 0.35-0.8), face (preset / (preset, overrides) / None = no face change),
    hold_face (True: keep the previous face). A gesture eases in over `blend` with a small wind-up (anticipation) and overshoot on the arms;
    the head lands ~0.08 s after the body. talk (0..1) moves the mouth (face.Track) and adds a little head motion."""
    def __init__(self, S, keys, breath=True, sway=True, feet=None, face=True, seed=0):
        self.S = S; self.k = S['h'] / 1.78; self.bw = S['build']; self.breath = breath; self.sway = sway; self.seed = seed
        gs = []
        for kk in keys:
            t, g = kk[0], kk[1]; o = kk[2] if len(kk) > 2 else {}
            G = dict(GESTURES[g]) if isinstance(g, str) else dict(g)
            if 'face' in o: G['face'] = o['face']
            gs.append((t, G, o))
        self.feet = any(any(c in G for c in FEET) for _, G, _ in gs) if feet is None else feet
        self.keys = [(t, self._condition(_flat(G, self.k, self.bw, self.feet)), G, o) for t, G, o in gs]
        fk = []
        for t, G, o in gs:
            f = G.get('face')
            if f is None or not face: continue
            fk.append((t + 0.04, f[0], f[1]) if isinstance(f, tuple) else (t + 0.04, f))
        self.ftrack = facemod.Track([(0.0, 'neutral')] + fk, seed=seed + 1) if face else None
        self._bl = {}; self._fc = {}
        self._starts = [self.keys[0][1]]                       # the state each key starts blending FROM
        for i in range(1, len(self.keys)):
            self._starts.append(self._eval(i - 1, self.keys[i][0], head_lag=False))
    def _eval(self, i, t, head_lag=True):
        t0, tgt, G, o = self.keys[i]; src = self._starts[i] if i < len(self._starts) else tgt
        crossed = lambda st: st['rhc'][0] < 0.02 and st['lhc'][0] > -0.02
        top = lambda st: 'l' if st['lhc'][2] > st['rhc'][2] else 'r'
        lead = None                                             # crossed arms: unfold the top arm first; fold the under arm in first
        if crossed(src): lead = top(src)
        elif crossed(tgt): lead = 'r' if top(tgt) == 'l' else 'l'
        if 'blend' in o: bl = o['blend']
        else:                                                   # timing from the real hand path (arc round the front + wrist turn)
            bl = self._bl.get(i)
            if bl is None: bl = self._bl[i] = self._blend_time(src, tgt) * (1.25 if lead else 1.0)
        u = (t - t0) / bl if bl > 0 else 1.0
        ua = _back(u); ub = _smooth(u); uh = _smooth(((t - 0.08) - t0) / bl) if head_lag else ub
        out = {}
        side_u = {}; meet = float(np.linalg.norm(V(tgt['rhc']) - V(tgt['lhc']))) < 0.2 * self.k    # the hands end close together (clap, cry)
        for sd in 'rl':                                         # stagger by delaying the other arm (never speed one up: 7 m/s fingertips)
            uu_ = u if lead is None else (min(1.0, u / 0.8) if sd == lead else max(0.0, (u - 0.2) / 0.8))
            uu_ = min(1.0, max(0.0, uu_)); side_u[sd] = (_back(uu_) if lead is None and not meet else _smooth(uu_), _smooth(uu_), uu_)   # no overshoot into the chest when crossing / through the other hand
        topside = (top(src) if crossed(src) else top(tgt)) if lead else None
        for c in tgt:
            uu = side_u[c[0]][0] if c[1:] in ARM else (uh if c == 'head' else ub)
            if c[1:] in ARM and self._near_head(tgt[c[0] + 'hc']): uu = side_u[c[0]][1]      # no overshoot into the face (think, facepalm, cry)
            if meet and c[1:] in ('palm_c', 'wrist'): uu = _smooth(min(1.0, u * 1.4))      # hands that meet turn to face each other BEFORE they arrive
            if c[1:] in ('palm_c', 'pole_c'): out[c] = _dlerp(src[c], tgt[c], uu)            # directions turn, never pass through zero
            if c[1:] == 'palm_c' and uu < 1.0:                  # the palm rides the forearm (hd palm_tr), blended about its axis
                (d0, p0), (d1, p1) = self._fore(i, 'src', src)[c[0]], self._fore(i, 'tgt', tgt)[c[0]]
                out[c[0] + 'palm_tr'] = (d0, p0, d1, p1, max(0.0, uu))
            if c[1:] in ('palm_c', 'pole_c'): continue
            if c in ('rfingers', 'lfingers'): uu = _smooth(u * 1.4)
            if c in ('rhc', 'lhc'):
                p_ = V(self._arc(c[0], src[c], tgt[c], uu))
                if c[0] == topside:                             # the top arm passes IN FRONT of the other forearm, not through it
                    w_ = side_u[c[0]][2]; w_ = w_ ** X_POW if crossed(tgt) else 1 - (1 - w_) ** X_POW     # folding in: clear late; unfolding: clear early
                    p_ = p_ + V((0.0, X_UP, 1.0)) * (X_AMP * self.k) * math.sin(math.pi * w_) ** 2
                out[c] = tuple(p_); continue
            out[c] = _lerp(src[c], tgt[c], uu)
        if lead is None and 0.0 < u < 1.0:                      # hands keep apart in transit (fingers pointing in cross), unless an end pose has them close
            r_, l_ = V(out['rhc']), V(out['lhc']); dv_ = r_ - l_; dn = float(np.linalg.norm(dv_))
            d0_ = float(np.linalg.norm(V(src['rhc']) - V(src['lhc']))); d1_ = float(np.linalg.norm(V(tgt['rhc']) - V(tgt['lhc'])))
            dmin = min(0.32 * self.k, d0_ + (d1_ - d0_) * ub)
            if dn < dmin:
                e_ = dv_ / dn if dn > 1e-6 else V((1.0, 0.0, 0.0)); h_ = (dmin - dn) / 2
                out['rhc'] = tuple(r_ + e_ * h_); out['lhc'] = tuple(l_ - e_ * h_)
        # anticipation: the hands dip back a touch before a big move
        if 0 < u < 0.35 and lead is None:                      # (not when the arms cross: the dip pushes the under arm into the chest)
            w = math.sin(u / 0.35 * math.pi) ** 2 * 0.12               # sin^2: starts and ends with zero speed (no pop)
            for s in 'rl':
                a, b = V(src[s + 'hc']), V(tgt[s + 'hc'])
                if np.linalg.norm(b - a) > 0.15: out[s + 'hc'] = tuple(V(out[s + 'hc']) - (b - a) * w * 0.25)
        return out
    def _arc(self, side, a, b, u):
        """hands travel on arcs around the shoulder (direction slerped, distance lerped), not on straight lines that fold the arm"""
        sh = V(((0.178 if side == 'r' else -0.178) * self.bw, 0.05 * self.k, -0.01))
        da, db = V(a) - sh, V(b) - sh; la, lb = np.linalg.norm(da), np.linalg.norm(db)
        if la < 1e-6 or lb < 1e-6: return _lerp(a, b, u)
        na, nb = da / la, db / lb; om = math.acos(max(-1.0, min(1.0, float(na @ nb))))
        sg = 1.0 if side == 'r' else -1.0
        if om > 1.4:                                            # big swing (hip -> head): go round the front, not through the shoulder / chest
            f = V((0.45 * sg, 0.0, 1.0)); f = f / np.linalg.norm(f); m = na + nb
            m = m / np.linalg.norm(m) if np.linalg.norm(m) > 0.3 else f
            w = min(1.0, (om - 1.4) / 0.9); m = m + w * 1.5 * f; m = m / np.linalg.norm(m)
            n = _slerp(na, m, u * 2) if u < 0.5 else _slerp(m, nb, u * 2 - 1)
        else: n = _slerp(na, nb, u)
        p = sh + n * (la + (lb - la) * u)
        # keep-out: the hand path must stay in front of / beside the torso (chest frame; endpoints may touch it, e.g. hands on hips)
        q = self._push(p) - p; q0 = self._push(V(a)) - V(a); q1 = self._push(V(b)) - V(b)
        uc = min(1.0, max(0.0, u))                              # u overshoots past 1 (_back): the allowance must not go negative
        dq = np.linalg.norm(q) - (np.linalg.norm(q0) * (1 - uc) + np.linalg.norm(q1) * uc)
        if dq > 0 and np.linalg.norm(q) > 1e-9: p = p + q / np.linalg.norm(q) * dq     # only ever pushes out, by what the endpoints do not already allow
        return tuple(p)
    def _fore(self, i, which, st):
        """(forearm direction, palm direction perpendicular to it) per side, chest frame, of a still pose (cached per key)"""
        key = (i, which)
        if key not in self._fc:
            Pt = {c: v for c, v in st.items() if not c.endswith('palm_tr')}; Pt.pop('face', None)
            _raw_human()(dict(self.S, cloak=None), Pt); RW = Pt['_RW']; r = {}
            for s in 'rl':
                d = RW.T @ Pt['_' + s + 'dir']; pc = V(st[s + 'palm_c'], float); pc = pc - d * float(pc @ d)
                r[s] = (tuple(d), tuple(pc / np.linalg.norm(pc)) if np.linalg.norm(pc) > 1e-6 else tuple(V(st[s + 'palm_c'], float)))
            self._fc[key] = r
        return self._fc[key]
    def _condition(self, tgt):
        """palm directions made perpendicular to the forearm of that pose (what hands.hand does anyway, so the still pose is
        unchanged): blending two such directions keeps the palm off the forearm axis, where the hand frame flips (a fingertip pop)"""
        Pt = dict(tgt); Pt.pop('face', None); _raw_human()(dict(self.S, cloak=None), Pt); RW = Pt['_RW']
        for s in 'rl':
            d = Pt['_' + s + 'dir']; pw = RW @ V(tgt[s + 'palm_c'], float); n = np.linalg.norm(pw)
            if n < 1e-9: continue
            pw = pw / n; pp = pw - d * float(pw @ d)
            if np.linalg.norm(pp) > 1e-3: tgt[s + 'palm_c'] = tuple(RW.T @ (pp / np.linalg.norm(pp)))
        return tgt
    def _blend_time(self, src, tgt):
        D = 0.0
        for sd in 'rl':
            a, b = src[sd + 'hc'], tgt[sd + 'hc']; pts = [V(self._arc(sd, a, b, x)) for x in np.linspace(0, 1, 9)]
            L = sum(float(np.linalg.norm(pts[j + 1] - pts[j])) for j in range(8))
            pa, pb = V(src[sd + 'palm_c']), V(tgt[sd + 'palm_c'])
            if np.linalg.norm(pa) > 1e-6 and np.linalg.norm(pb) > 1e-6:      # a hand that turns over moves the fingertips a lot
                L += 0.09 * math.acos(max(-1.0, min(1.0, float(pa @ pb / np.linalg.norm(pa) / np.linalg.norm(pb)))))
            D = max(D, L)
        D += 0.5 * abs(tgt['lean'] - src['lean'])                         # a bow moves the hands too
        return min(0.95, max(0.35, 0.3 + 0.4 * D))
    def _near_head(self, hc):
        return hc[1] > 0.05 * self.k and abs(hc[0]) < 0.16 * self.bw and hc[2] > 0.0
    def _push(self, p):
        """the point moved out of a padded torso ellipse (chest frame: x right, y up, z forward); unchanged when outside"""
        k = self.k; rx = 0.2 * self.bw; rz = 0.17 * k; cz = -0.02 * k
        hc = V((0.0, 0.255 * k, 0.01 * k)); hr = V((0.13 + HEAD_PAD, 0.155 + HEAD_PAD, 0.145 + HEAD_PAD)) * k   # head (bodycheck radii + a hand's thickness + fingers)
        e = (V(p) - hc) / hr; r = float(np.linalg.norm(e))
        if r < 1.0: return hc + (e / r if r > 1e-6 else V((0, 0, 1.0))) * hr
        y0, y1, fd = -0.5 * k, 0.08 * k, 0.07 * k                # the torso band, faded in / out over 7 cm (a hard edge made the hands pop)
        wy = _smooth((p[1] - (y0 - fd)) / fd) * _smooth(((y1 + fd) - p[1]) / fd)
        if wy <= 0.0: return V(p)
        x, z = p[0] / rx, (p[2] - cz) / rz; r = math.hypot(x, z)
        if r >= 1.0: return V(p)
        if r < 1e-6: x, z, r = 0.0, 1.0, 1.0
        q = V((x / r * rx, p[1], cz + z / r * rz)); return V(p) + (q - V(p)) * wy
    def _drive(self, t):
        """where the upper back is (body-local metres, forward / right / up) - what the cloak lags behind"""
        P = self._core(t); k = self.k
        f = 0.45 * k * math.sin(P['lean']) + P['pel'][2] + 0.1 * math.sin(P['twist'])
        s = 0.45 * k * math.sin(-P['side']) + P['pel'][0]
        u = P['pel'][1] - P['crouch'] + 0.2 * (sum(P[c + 'shrug'][0] for c in 'rl'))
        return V((f, s, u))
    def cape(self, t):
        """cloak follow-through: a damped spring per axis integrated from t = 0 on a fixed 1/48 s grid (deterministic, cached).
        Returns (cape_sway, cape_side): the cloth swings back when the body moves forward, sideways the other way, and settles."""
        h = 1.0 / 48; n = max(0, int(round(t / h)))
        if not hasattr(self, '_cs'): self._cs = [(V((0.0, 0.0)), V((0.0, 0.0)))]; self._cx = [self._drive(0.0), self._drive(0.0)]
        w = 2 * math.pi * 1.2; z = 0.32
        while len(self._cs) <= n:
            m = len(self._cs); self._cx.append(self._drive(m * h))
            acc = (self._cx[-1] - 2 * self._cx[-2] + self._cx[-3]) / (h * h)
            a_ = V((acc[0] - 0.5 * acc[2], -acc[1]))                     # forward push -> cloth lags back; a drop lifts it a bit
            d, v = self._cs[-1]; v = v + h * (-w * w * d - 2 * z * w * v + a_); d = d + h * v
            self._cs.append((d, v))
        d = self._cs[n][0]
        return float(np.clip(0.06 + d[0] / 0.15, -0.3, 1.4)), float(np.clip(d[1] / 0.15, -0.8, 0.8))
    def _hdrive(self, t):
        """where the head is (body-local metres: right, up, forward) - what the hair lags behind; a head turn swings the tips too"""
        P = self._core(t); k = self.k; hy, hn, _ = P['head']
        x = 0.62 * k * math.sin(-P['side']) + P['pel'][0] + 0.12 * k * math.sin(hy)
        y = P['pel'][1] - P['crouch'] + 0.62 * k * (math.cos(P['lean']) - 1)
        z = 0.62 * k * math.sin(P['lean']) + P['pel'][2] + 0.12 * k * math.sin(hn)
        return V((x, y, z))
    def hair(self, t):
        """hair follow-through: the same damped spring as the cloak, lighter and quicker (2 Hz). Body-local lag vector (m)."""
        h = 1.0 / 48; n = max(0, int(round(t / h)))
        if not hasattr(self, '_hs'): self._hs = [(V((0.0, 0.0, 0.0)), V((0.0, 0.0, 0.0)))]; self._hx = [self._hdrive(0.0), self._hdrive(0.0)]
        w = 2 * math.pi * 2.0; z = 0.28
        while len(self._hs) <= n:
            m = len(self._hs); self._hx.append(self._hdrive(m * h))
            acc = (self._hx[-1] - 2 * self._hx[-2] + self._hx[-3]) / (h * h)
            d, v = self._hs[-1]; v = v + h * (-w * w * d - 2 * z * w * v - acc); d = d + h * v
            self._hs.append((d, v))
        return np.clip(self._hs[n][0], -0.06, 0.06)
    def _core(self, t):
        i = max(j for j in range(len(self.keys)) if self.keys[j][0] <= t) if t >= self.keys[0][0] else 0
        P = self._eval(i, t)
        # oscillations of the current gesture (fade in with the blend) and the previous one (fade out)
        for j, w in ((i, _smooth((t - self.keys[i][0]) / 0.3)), (i - 1, 1 - _smooth((t - self.keys[i][0]) / 0.3))):
            if j < 0 or w <= 0: continue
            for c, idx, amp, hz in self.keys[j][2].get('osc', []):
                v = amp * w * math.sin(2 * math.pi * hz * t)
                if idx is None: P[c] = P[c] + v
                else: l = list(P[c]); l[idx] += v; P[c] = tuple(l)
        if self.breath:                                                 # ~17 breaths a minute: chest rises, shoulders follow
            b = math.sin(2 * math.pi * t / 3.6 + self.seed)
            P['lean'] += -0.008 * b
            for s in 'rl': P[s + 'shrug'] = (P[s + 'shrug'][0] + 0.005 * b, P[s + 'shrug'][1])
        if self.sway:                                                   # slow weight shift from foot to foot
            w = math.sin(2 * math.pi * t / 6.5 + 1.7 * self.seed)
            P['pel'] = (P['pel'][0] + 0.016 * w * self.k, P['pel'][1] - 0.004 * abs(w), P['pel'][2])
            P['side'] += -0.025 * w
        return P
    def _walk(self, P, ph, stride, ww):
        k, bw = self.k, self.bw; sw = math.sin(ph); feet, bob = hd.walk_cycle(ph, stride, 0.1)
        P['walk'] = ph; P['stride'] = stride
        P['pel'] = (P['pel'][0] * (1 - 0.6 * ww), P['pel'][1] - bob * (1 - ww), P['pel'][2])      # hd adds the bob; no weight shift while stepping
        P['lean'] += 0.05 * ww
        for i, (sd, s) in enumerate(((1, 'r'), (-1, 'l'))):
            d0 = V((sd * 0.11 * bw, 0.075, 0.02)); f = V(P[s + 'f']) if s + 'f' in P else d0
            wf = ww * _smooth(1 - float(np.linalg.norm(f - d0)) / 0.12)                     # a placed foot (kneel) does not step
            fz, up = feet[i]; P[s + 'f'] = tuple(f + V((0, up, fz)) * wf)
            r0 = V(_flat(dict(r=REST, l=mirror(REST)), k, bw, False)[s + 'hc'])
            wa = ww * _smooth(1 - float(np.linalg.norm(V(P[s + 'hc']) - r0)) / (0.16 * k))  # only arms near rest swing
            x, y, z = P[s + 'hc']; P[s + 'hc'] = (x, y + 0.025 * k * wa * sw * sw, z - sd * 0.14 * k * wa * sw * stride / 0.3)
    def at(self, t, talk=0.0, walk=None, stride=0.3, walk_w=1.0):
        """walk = the walking phase (radians, as hd.human's P['walk']; the caller moves base by about 2*stride/pi per radian),
        walk_w (0..1) eases into / out of the walk. Gestures keep playing on top: arms near the rest pose swing against the legs,
        arms doing something (wave, think, ...) keep doing it; feet a gesture places itself (kneel) do not step."""
        P = self._core(t)
        hl = self.hair(t)
        if walk is not None and walk_w > 0:
            self._walk(P, walk, stride, min(1.0, walk_w))
            _, bob = hd.walk_cycle(walk, stride, 0.1); ww = min(1.0, walk_w)
            hl = hl + V((0.0, -0.5 * bob, -0.02)) * ww                     # walking: the step bounce + the air going past
        P['hair_lag'] = tuple(float(c) for c in hl)
        if self.S.get('cloak_hd'):                                      # soft cloak: follow-through + living folds
            P['cape_sway'], P['cape_side'] = self.cape(t); P['cape_t'] = t
        if talk > 0.02:
            hy, hn, ht = P['head']; P['head'] = (hy + 0.03 * talk * math.sin(t * 5.3), hn + 0.03 * talk * math.sin(t * 7.9), ht)
        if self.ftrack is not None: P['face'] = self.ftrack.at(t, talk=talk)
        hy, hn, ht = P['head']; P['head'] = (hy, -hn, ht)              # gesture nod: + = chin down; hd.human's head pitch: + = looks up
        return P
