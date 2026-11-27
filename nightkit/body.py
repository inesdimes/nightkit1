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
    'point_fwd':    dict(r=arm(0.47, 0.1, 0.42, palm=(0, -1, 0), pole=(1, -0.8, -0.2), fingers='point'), l=mirror(REST), face='determined'),
    'shrug':        dict(**both(arm(0.3, -0.24, 0.24, palm=(0.25, 1, 0.15), pole=(1, -1, -0.5), fingers='open', shrug=(0.055, 0.0))),
                         head=(0.0, -0.04, 0.2), face=('deadpan', dict(browR=0.7, browL=0.5, smR=-0.3, smL=-0.3))),
    'arms_crossed': dict(r=arm(-0.06, -0.17, 0.2, palm=(0, 0, -1), pole=(1, -0.8, -0.1), fingers=hands.pose('grip', r=0.045)),
                         l=dict(hc=(0.06, -0.12, 0.245), palm_c=(0, 0, -1), pole_c=(-1, -0.8, -0.1), fingers=hands.pose('grip', r=0.045), wrist=(0.0, 0.0), shrug=(0.0, 0.0)),
                         lean=-0.04, head=(0.0, -0.06, 0.0), face='smug'),
    'hips':         dict(**both(arm(0.21, -0.33, 0.0, palm=(-1, -0.2, 0.3), pole=(1, 0.0, -0.8), fingers='relaxed', wrist=(-0.5, 0.0))),
                         lean=-0.06, head=(0.0, -0.1, 0.0), face='proud'),
    'facepalm':     dict(r=arm(0.03, 0.2, 0.2, palm=(0, 0.2, -1), pole=(1, -1, 0.1), fingers='open', wrist=(-0.6, 0.0)), l=mirror(REST),
                         lean=0.08, head=(0.0, 0.3, 0.06), face=('deadpan', dict(eyesR=0.0, eyesL=0.0, smR=-0.4, smL=-0.4))),
    'think':        dict(r=arm(0.05, 0.12, 0.21, palm=(-1, 0.3, 0), pole=(1, -1, -0.2), fingers='relaxed', wrist=(-0.4, 0.0)),
                         l=dict(hc=(0.06, -0.22, 0.21), palm_c=(0, 1, 0), pole_c=(-1, -1, -0.3), fingers='relaxed', wrist=(0.0, 0.0), shrug=(0.0, 0.0)),
                         head=(0.15, -0.12, 0.12), face=('neutral', dict(look=(0.5, 0.6), browR=0.4, browL=-0.1, press=0.5))),
    'cheer':        dict(**both(arm(0.28, 0.62, 0.06, palm=(-1, 0, 0), pole=(1, 0.0, -0.5), fingers='fist')), lean=-0.1, head=(0.0, -0.15, 0.0),
                         face='laughing', osc=[('rhc', 1, 0.03, 2.0), ('lhc', 1, 0.03, 2.0)]),
    'fist_pump':    dict(r=arm(0.22, -0.06, 0.28, palm=(-1, 0, 0), pole=(1, -1, 0.0), fingers='fist'), l=mirror(REST), crouch=0.04, lean=0.1, face='determined'),
    'hands_up':     dict(**both(arm(0.36, 0.3, 0.14, palm=(0, 0, 1), pole=(1, -0.8, -0.3), fingers='spread', wrist=(-1.0, 0.0))), lean=-0.12, face='scared'),
    'salute':       dict(r=arm(0.23, 0.25, 0.15, palm=(-0.2, -0.5, 1), pole=(1, -0.1, 0.0), fingers=hands.pose('open', spread=0.0, thumb=(0.0, 0.2, 0.0))),
                         l=mirror(REST), head=(0.0, -0.05, 0.0), face='determined'),
    'scratch_head': dict(r=arm(0.1, 0.38, -0.02, palm=(-1, -0.5, 0), pole=(1, 0.2, 0.4), fingers='claw'), l=mirror(REST),
                         head=(0.0, 0.05, -0.15), face='embarrassed', osc=[('rwrist', 0, 0.3, 3.0)]),
    'clap':         dict(**both(arm(0.035, -0.08, 0.32, palm=(-1, 0, 0), pole=(1, -1, -0.3), fingers='open')), face='laughing',
                         osc=[('rhc', 0, 0.04, 3.0), ('lhc', 0, -0.04, 3.0)]),
    'bow':          dict(**both(arm(0.16, -0.46, 0.1)), lean=0.6, head=(0.0, 0.25, 0.0), face=('neutral', dict(eyesR=0.15, eyesL=0.15))),
    'laugh':        dict(**both(arm(0.1, -0.28, 0.17, palm=(0, 0, -1), pole=(1, -1, -0.4), fingers='open')), lean=-0.12, head=(0.0, -0.2, 0.0),
                         face='laughing', osc=[('lean', None, 0.04, 4.0), ('rshrug', 0, 0.012, 4.0), ('lshrug', 0, 0.012, 4.0)]),
    'cry':          dict(**both(arm(0.06, 0.19, 0.2, palm=(0, 0, -1), pole=(1, -1, 0.0), fingers='relaxed', wrist=(-0.6, 0.0))),
                         lean=0.12, head=(0.0, 0.3, 0.0), face='sad', osc=[('rshrug', 0, 0.014, 3.0), ('lshrug', 0, 0.014, 3.0)]),
    'shocked':      dict(**both(arm(0.2, 0.08, 0.26, palm=(0, 0, 1), pole=(1, -1, -0.2), fingers='spread', wrist=(-1.0, 0.0))), lean=-0.15,
                         head=(0.0, -0.08, 0.0), face='shocked'),
    'slump':        dict(**both(arm(0.2, -0.47, 0.16, fingers='relaxed', shrug=(-0.035, 0.07))), lean=0.34, crouch=0.05, head=(0.0, 0.45, 0.0), face='sad'),
    'proud':        dict(**both(arm(0.21, -0.33, 0.0, palm=(-1, -0.2, 0.3), pole=(1, 0.0, -0.8), fingers='relaxed', wrist=(-0.5, 0.0))),
                         lean=-0.1, head=(0.0, -0.14, 0.0), face='proud'),
    'kneel':        dict(r=arm(0.26, -0.34, 0.24, pole=(1, -0.5, -0.4)), l=mirror(REST), crouch=0.44, lean=0.08,
                         rf=(0.11, 0.075, 0.36), lf=(-0.11, 0.07, -0.44), rkpole=(0.1, 0.0, 1.0), lkpole=(-0.05, -1.0, 0.25), head=(0.0, 0.15, 0.0)),
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
    return e + s * math.sin(math.pi * min(1.0, max(0.0, (u - 0.62) / 0.38)))
def _smooth(u): u = min(1.0, max(0.0, u)); return u * u * (3 - 2 * u)
ARM = ('hc', 'palm_c', 'pole_c', 'wrist', 'shrug')

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
        self.keys = [(t, _flat(G, self.k, self.bw, self.feet), G, o) for t, G, o in gs]
        fk = []
        for t, G, o in gs:
            f = G.get('face')
            if f is None or not face: continue
            fk.append((t + 0.04, f[0], f[1]) if isinstance(f, tuple) else (t + 0.04, f))
        self.ftrack = facemod.Track([(0.0, 'neutral')] + fk, seed=seed + 1) if face else None
        self._starts = [self.keys[0][1]]                       # the state each key starts blending FROM
        for i in range(1, len(self.keys)):
            self._starts.append(self._eval(i - 1, self.keys[i][0], head_lag=False))
    def _eval(self, i, t, head_lag=True):
        t0, tgt, G, o = self.keys[i]; src = self._starts[i] if i < len(self._starts) else tgt
        D = max(np.linalg.norm(V(tgt[s + 'hc']) - V(src[s + 'hc'])) for s in 'rl')
        bl = o.get('blend', min(0.8, max(0.35, 0.3 + 0.36 * D)))          # timing from distance: big arm moves take longer
        u = (t - t0) / bl if bl > 0 else 1.0
        ua = _back(u); ub = _smooth(u); uh = _smooth(((t - 0.08) - t0) / bl) if head_lag else ub
        out = {}
        for c in tgt:
            uu = ua if c[1:] in ARM else (uh if c == 'head' else ub)
            if c in ('rfingers', 'lfingers'): uu = _smooth(u * 1.4)
            if c in ('rhc', 'lhc'): out[c] = self._arc(c[0], src[c], tgt[c], uu); continue
            out[c] = _lerp(src[c], tgt[c], uu)
        # anticipation: the hands dip back a touch before a big move
        if 0 < u < 0.35:
            w = math.sin(u / 0.35 * math.pi) * 0.12
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
        if om < 1e-4: n = na
        elif om > math.pi - 0.05: return _lerp(a, b, u)
        else: n = (math.sin((1 - u) * om) * na + math.sin(u * om) * nb) / math.sin(om)
        return tuple(sh + n * (la + (lb - la) * u))
    def at(self, t, talk=0.0):
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
        if talk > 0.02:
            hy, hn, ht = P['head']; P['head'] = (hy + 0.03 * talk * math.sin(t * 5.3), hn + 0.03 * talk * math.sin(t * 7.9), ht)
        if self.ftrack is not None: P['face'] = self.ftrack.at(t, talk=talk)
        return P
