"""Hands with real fingers for hd humans (Insert Disc 2, 28 Nov 2026) - phase 2 of the human performance system.
Opt-in per hand: P['rfingers'] / P['lfingers'] = a preset name or a dict; without it hd.human keeps the old one-value grip hand,
so every existing video renders exactly as before.

    P['rfingers'] = 'point'                                  # a preset
    P['rfingers'] = hands.pose('grip', r=0.02)               # wrap a handle of radius 2 cm
    P['lfingers'] = hands.blend(hands.pose('open'), hands.pose('fist'), u)
    P['rwrist'] = (flex, dev)                                # wrist bend in radians: + flex toward the palm, + dev toward the thumb

Hand dict: f = 4 finger curls (index, middle, ring, pinky), each a number 0..1 or a tuple (knuckle, middle joint, tip joint);
spread 0..1; thumb = (out, across, curl): out = away from the palm side, across = over the palm toward the pinky, curl = bend.
After hd.human: P['_rtips'] = 5 fingertip points (thumb, index, middle, ring, pinky), P['_rgrip'] = the centre of a closed grip."""
import math
import numpy as np
from . import hd
from .hd import nz, limb, bx, shade, mix
V = np.array
def _f(c): return tuple(c) if isinstance(c, (tuple, list)) else (c, c, c)
PRESETS = {
    'relaxed':   dict(f=(0.22, 0.3, 0.36, 0.42), spread=0.15, thumb=(0.25, 0.1, 0.2)),
    'open':      dict(f=(0.0, 0.0, 0.0, 0.0), spread=0.25, thumb=(0.45, 0.0, 0.0)),
    'spread':    dict(f=(0.0, 0.0, 0.0, 0.0), spread=1.0, thumb=(1.0, 0.0, 0.0)),            # "stop!" / jazz hand
    'fist':      dict(f=(1.0, 1.0, 1.0, 1.0), spread=0.0, thumb=(0.15, 0.75, 0.55)),
    'point':     dict(f=(0.0, 1.0, 1.0, 1.0), spread=0.0, thumb=(0.1, 0.6, 0.55)),
    'thumbs_up': dict(f=(1.0, 1.0, 1.0, 1.0), spread=0.0, thumb=(0.0, -0.25, 0.0)),
    'peace':     dict(f=(0.0, 0.0, 1.0, 1.0), spread=0.9, thumb=(0.1, 0.65, 0.55)),
    'ok':        dict(f=((0.55, 0.7, 0.5), 0.1, 0.15, 0.2), spread=0.6, thumb=(0.35, 0.55, 0.35), touch=1),
    'pinch':     dict(f=((0.45, 0.4, 0.25), 0.55, 0.65, 0.75), spread=0.1, thumb=(0.35, 0.5, 0.25), touch=1),
    'claw':      dict(f=((0.15, 0.95, 0.8), (0.15, 0.95, 0.8), (0.15, 0.95, 0.8), (0.15, 0.95, 0.8)), spread=0.7, thumb=(0.6, 0.2, 0.7)),
    'grip':      dict(f=(0.72, 0.75, 0.78, 0.8), spread=0.0, thumb=(0.1, 0.55, 0.35)),     # around a sword / torch / mug handle
    'wave':      dict(f=(0.0, 0.05, 0.08, 0.12), spread=0.55, thumb=(0.6, 0.0, 0.05)),
    'beckon':    dict(f=(0.5, 1.0, 1.0, 1.0), spread=0.0, thumb=(0.1, 0.6, 0.55)),          # animate index 0 <-> 0.8
    'one':       dict(f=(0.0, 1.0, 1.0, 1.0), spread=0.0, thumb=(0.1, 0.65, 0.55)),
    'two':       dict(f=(0.0, 0.0, 1.0, 1.0), spread=0.35, thumb=(0.1, 0.65, 0.55)),
    'three':     dict(f=(0.0, 0.0, 0.0, 1.0), spread=0.35, thumb=(0.1, 0.7, 0.6)),
    'four':      dict(f=(0.0, 0.0, 0.0, 0.0), spread=0.35, thumb=(0.0, 0.85, 0.55)),
    'five':      dict(f=(0.0, 0.0, 0.0, 0.0), spread=0.45, thumb=(0.75, 0.0, 0.0)),
}
def pose(name='relaxed', r=None, **over):
    """a full hand dict; grip with r (handle radius, m) sets the curls so the fingertips close around it"""
    H = dict(PRESETS[name]); H.update(over)
    if name == 'grip' and r is not None:
        c = float(np.clip(1.0 - (r - 0.008) / 0.05, 0.35, 1.0)); H['f'] = (c * 0.9, c * 0.95, c, c)
    return H
def blend(A, B, u):
    A = pose(A) if isinstance(A, str) else A; B = pose(B) if isinstance(B, str) else B
    lr = lambda a, b: a + (b - a) * u
    return dict(f=tuple(tuple(lr(x, y) for x, y in zip(_f(a), _f(b))) for a, b in zip(A['f'], B['f'])),
                spread=lr(A['spread'], B['spread']), thumb=tuple(lr(x, y) for x, y in zip(A['thumb'], B['thumb'])), touch=(B if u >= 0.5 else A).get('touch'))

# joint angle budget per unit curl (knuckle, middle, tip) - a full fist is ~ 85 + 100 + 70 degrees
JA = (1.48, 1.75, 1.2)
FING = [  # across offset (x palm half-widths, + = thumb side), length (m at k = 1), segment split, radius, spread angle
    (0.68, 0.083, (0.46, 0.31, 0.23), 0.0098, 0.16),    # index
    (0.22, 0.091, (0.46, 0.31, 0.23), 0.0101, 0.04),    # middle
    (-0.24, 0.085, (0.46, 0.31, 0.23), 0.0096, -0.09),  # ring
    (-0.68, 0.068, (0.47, 0.30, 0.23), 0.0086, -0.24),  # pinky
]

def hand(wr, d, palm_n, H, col, k, ring=None, side=-1, wrist=(0.0, 0.0), out=None):
    """the hand at the wrist, pointing along d, palm facing palm_n; H = a pose dict or preset name. Returns faces; out (dict) gets the tips."""
    H = pose(H) if isinstance(H, str) else H
    d = nz(np.asarray(d, float)); pn = np.asarray(palm_n, float); pp = pn - d * float(pn @ d)
    pn = nz(pp) if np.linalg.norm(pp) > 1e-6 else hd.frame_for(d, (0, 0, 1))[0]
    sdv = np.cross(d, pn) * (1.0 if side < 0 else -1.0)            # across the palm, thumb side = +sdv (same convention as hd.hand)
    fl, dv = wrist                                                   # wrist bend: flex toward the palm, deviate toward the thumb
    if fl or dv:
        d2 = nz(d * math.cos(fl) + pn * math.sin(fl)); pn = nz(pn * math.cos(fl) - d * math.sin(fl)); d = d2
        d2 = nz(d * math.cos(dv) + sdv * math.sin(dv)); sdv = nz(sdv * math.cos(dv) - d * math.sin(dv)); d = d2
    Q = []; dk = shade(col, 0.9); nail = mix(col, (255, 236, 226), 0.35)
    pl = 0.088 * k; pw = 0.041 * k; pt = 0.016 * k
    # palm: a slightly cupped block, wider at the knuckles
    cup = 0.25 * float(np.mean([_f(c)[0] for c in H['f']]))
    Rm = np.column_stack([sdv, -pn, d])
    Q += bx(wr + d * pl * 0.42 + pn * pt * 0.1, Rm, (pw * 0.9, pt, pl * 0.42), col)
    Q += bx(wr + d * pl * 0.86 + pn * pt * 0.25 * cup, Rm, (pw * 1.02, pt * 0.92, pl * 0.12), col)
    Q += limb(wr - d * 0.012 * k, wr + d * 0.02 * k, 0.03 * k, 0.034 * k, col, n=6, m=1, ref=-pn, flat=0.62)      # wrist into the palm
    # thenar pad (the thumb muscle) on the palm side
    Q += hd.ellip(wr + d * pl * 0.32 + sdv * pw * 0.55 + pn * pt * 0.6, Rm, (pw * 0.42, pt * 0.9, pl * 0.3), 6, 3, shade(col, 0.97))
    sp = float(H['spread']); tips = []
    for i, (ax, ln, split, rad, sang) in enumerate(FING):
        c3 = _f(H['f'][i]); base = wr + d * (pl * (0.95 + 0.04 * (1 - abs(ax)))) + sdv * ax * pw - pn * pt * 0.15
        a = sang * (0.35 + 0.9 * sp)                                 # spread fans the fingers around the palm normal
        f = nz(d * math.cos(a) + sdv * math.sin(a)); n = pn.copy(); p = base
        for s_i in range(3):
            th = c3[s_i] * JA[s_i]
            f2 = nz(f * math.cos(th) + n * math.sin(th)); n = nz(n * math.cos(th) - f * math.sin(th)); f = f2
            L_ = ln * k * split[s_i]; r0 = rad * k * (1 - 0.1 * s_i); r1 = r0 * 0.9
            q = p + f * L_
            Q += limb(p - f * r0 * 0.6, q, r0, r1, col if s_i < 2 else dk, n=5, m=1, ref=-n)
            if ring is not None and i == 2 and s_i == 0: Q += limb(p + f * L_ * 0.25, p + f * L_ * 0.5, r0 * 1.25, r0 * 1.25, ring, n=6, m=1, ref=-n)
            p = q
        Q += bx(p - f * 0.006 * k - n * rad * k * 0.75, np.column_stack([np.cross(n, f), -n, f]), (rad * k * 0.6, 0.0012 * k, 0.005 * k), nail)   # nail
        tips.append(p)
    # thumb: the TIP is placed (palm frame: x = across to the thumb side, y = out of the palm, z = along the fingers), then 3 segments
    # follow a curve from the base that bows away from the palm centre (the knuckle), more with curl. touch = a finger index (1 = index):
    # the tip lands on that fingertip (ok sign, pinch).
    to, ta, tc = H['thumb']
    PF = lambda x, y, z: wr + sdv * x * pw + pn * y * pt + d * z * pl
    tb = PF(0.72, 0.5, 0.14)
    rest = V((1.55, 1.5, 0.86)); o_ = V((2.35, 0.4, 0.68)); a_ = V((-0.35, 3.0, 0.72)); u_ = V((2.3, 0.9, 0.98))
    tl = rest + to * (o_ - rest) + max(0.0, ta) * (a_ - rest) + max(0.0, -ta) * 4.0 * (u_ - rest) - tc * V((0.25, -0.2, 0.18))
    tip = PF(*tl)
    if H.get('touch') is not None: tip = tips[H['touch'] - 1] + nz(tb - tips[H['touch'] - 1]) * 0.011 * k
    mid = (tb + tip) / 2; ctr = PF(0.0, 0.0, 0.45); ch = tip - tb; ln_ = np.linalg.norm(ch)
    bow = mid - ctr; bow = nz(bow - ch * float(bow @ ch) / max(ln_ * ln_, 1e-9))
    c1 = mid + bow * (0.005 + 0.03 * tc + 0.01 * max(0.0, ta)) * k
    pts = [(1 - u) ** 2 * tb + 2 * (1 - u) * u * c1 + u * u * tip for u in (0.0, 0.45, 0.76, 1.0)]
    for s_i, r0 in enumerate((0.0135, 0.0118, 0.0105)):
        a0, b0 = pts[s_i], pts[s_i + 1]; f = nz(b0 - a0)
        Q += limb(a0 - f * r0 * k * 0.5, b0, r0 * k, r0 * k * 0.88, col if s_i < 2 else dk, n=5, m=1, ref=bow)
    p = pts[-1]; bend = nz(-bow - f * float(-bow @ f))
    Q += bx(p - f * 0.006 * k + bow * 0.0095 * k, np.column_stack([np.cross(bend, f), -bend, f]), (0.0065 * k, 0.0012 * k, 0.0055 * k), nail)
    tips.insert(0, p)
    if out is not None: out['tips'] = tips; out['grip'] = wr + d * pl * 1.05 + pn * 0.035 * k; out['d'] = d; out['pn'] = pn
    return Q
