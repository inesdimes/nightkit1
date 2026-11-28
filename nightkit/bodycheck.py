"""Automatic body checks for hd humans (Insert Disc 2, 27 Nov 2026) - phase 4 of the human performance system.
Reads the joint outputs hd.human writes into the pose dict (P['_torso'], '_head', '_rsh', '_rel', '_rwrist', '_rtips', ...),
so it works for every video without changing it.

Per pose (check_pose):
  arm-torso     upper arm / forearm / hand / fingertips inside the torso (arm through the body)
  arm-head      forearm / hand / fingertips inside the head (fingers in the face)
  arm-arm       the two forearms pass through each other, or the two hands overlap
  hand-other    a hand inside ANOTHER character's torso / head (two people in one frame)
  leg-leg       thighs / shins pass through each other
  foot-ground   an ankle below the ground (feet sinking in)
  elbow-fold    the elbow folds tighter than ~25 degrees (the forearm inside the upper arm)
Across frames (Monitor):
  jump          a joint moves faster than a person can (body-relative, per frame), e.g. a pose that snaps
  pop           a sudden change of velocity (a joint that starts / stops dead or reverses in one frame)

    mon = bodycheck.Monitor(fps=24)
    for f in frames:
        mon.frame(t)                       # once per frame, before the hd.human calls
        P = ...; Q = hd.human(S, P); mon.add(S, P, who='hero')
    print(mon.text())
or, with no script changes: bodycheck.install(mon) wraps hd.human so every call is checked (tools/qa/body_qa.py)."""
import math
import numpy as np
V = np.array
# limb radii used for the checks (a bit under the drawn ones, so touching is not a hit)
R_UP, R_FORE, R_THIGH, R_SHIN = 0.044, 0.034, 0.07, 0.05
TOL = 0.015                                     # penetration depth that counts as a hit (m)
# fastest believable joint speed, body-relative, metres per frame at 24 fps (pop = change of speed in one frame)
SPEED = dict(head=0.07, chest=0.07, rwrist=0.22, lwrist=0.22, rel=0.16, lel=0.16, rtip=0.3, ltip=0.3, rknee=0.12, lknee=0.12, rankle=0.2, lankle=0.2)
POP = dict(head=0.04, chest=0.04, rwrist=0.11, lwrist=0.11, rel=0.09, lel=0.09, rtip=0.16, ltip=0.16, rknee=0.08, lknee=0.08, rankle=0.12, lankle=0.12)

def _a(x): return None if x is None else np.asarray(x, float)
def torso_depth(p, T):
    """how deep point p is inside the torso loft T = P['_torso'] (m; <= 0 = outside)"""
    best = -1.0
    for (c0, R0, rx0, rz0), (c1, R1, rx1, rz1) in zip(T, T[1:]):
        c0 = _a(c0); c1 = _a(c1); ax = c1 - c0; L2 = float(ax @ ax)
        if L2 < 1e-9: continue
        u = float((p - c0) @ ax) / L2
        if u < 0.0 or u > 1.0: continue
        c = c0 + ax * u; R = _a(R0) if u < 0.5 else _a(R1); rx = rx0 + (rx1 - rx0) * u; rz = rz0 + (rz1 - rz0) * u
        q = R.T @ (p - c); e = math.hypot(q[0] / rx, q[2] / rz)
        best = max(best, (1.0 - e) * min(rx, rz))
    return best
def head_depth(p, P):
    hc = _a(P.get('_head')); RH = _a(P.get('_RH'))
    if hc is None or RH is None: return -1.0
    hk = P.get('_hk', 1.0); r = V((0.09, 0.116, 0.103)) * hk; q = RH.T @ (p - hc) / r; e = float(np.linalg.norm(q))
    return (1.0 - e) * float(r.min())
def seg_dist(a, b, c, d):
    """closest distance between segments ab and cd"""
    u = b - a; v = d - c; w = a - c; A = u @ u; B = u @ v; C = v @ v; D = u @ w; E = v @ w; den = A * C - B * B
    s = 0.0 if den < 1e-12 else float(np.clip((B * E - C * D) / den, 0, 1))
    t = float(np.clip((B * s + E) / C, 0, 1)) if C > 1e-12 else 0.0
    s = float(np.clip((B * t - D) / A, 0, 1)) if A > 1e-12 else 0.0
    return float(np.linalg.norm((a + u * s) - (c + v * t)))
def hand_centre(P, s):
    """middle of the palm: with real fingers from the tips (follows the wrist bend), else along the forearm"""
    wr = _a(P['_' + s + 'wrist']); tp = P.get('_' + s + 'tips')
    if tp: return wr + (np.mean([_a(t) for t in tp[1:]], axis=0) - wr) * 0.4
    return wr + _a(P['_' + s + 'dir']) * 0.045
def arm_points(P, s):
    """(label, point, radius) along one arm: upper arm (away from the shoulder), forearm, wrist, fingertips"""
    sh, el, wr = _a(P.get('_' + s + 'sh')), _a(P.get('_' + s + 'el')), _a(P.get('_' + s + 'wrist'))
    if sh is None or el is None or wr is None: return []
    out = [('upper arm', sh + (el - sh) * u, R_UP) for u in (0.75, 1.0)]        # not nearer the shoulder: the arm is attached there
    out += [('forearm', el + (wr - el) * u, R_FORE) for u in (0.33, 0.66)]
    out.append(('hand', hand_centre(P, s), 0.022))
    names = ('thumb', 'index', 'middle', 'ring', 'pinky')
    for n, tp in zip(names, P.get('_' + s + 'tips') or []): out.append((n + ' tip', _a(tp), 0.006))
    return out

def check_pose(P, base=None, others=()):
    """-> list of (kind, message, depth_m). others = pose dicts of the other characters in the same frame."""
    out = []; T = P.get('_torso')
    for s, side in (('r', 'right'), ('l', 'left')):
        pts = arm_points(P, s)
        if not pts: continue
        worst = {}
        for lab, p, r in pts:
            if T is not None:
                d = torso_depth(p, T) + r
                if d > TOL and d > worst.get(('torso', lab), (0,))[0]: worst[('torso', lab)] = (d,)
            d = head_depth(p, P) + r
            if d > TOL and d > worst.get(('head', lab), (0,))[0]: worst[('head', lab)] = (d,)
            for j, O in enumerate(others):
                if O.get('_torso') is not None:
                    d = torso_depth(p, O['_torso']) + r
                    if d > TOL * 2: worst[('other', lab)] = (max(d, worst.get(('other', lab), (0,))[0]),)
        for (what, lab), (d,) in worst.items():
            kind = {'torso': 'arm-torso', 'head': 'arm-head', 'other': 'hand-other'}[what]
            where = {'torso': 'the body', 'head': 'the head', 'other': "another character's body"}[what]
            out.append((kind, f'{side} {lab} {d * 100:.0f} cm inside {where}', d))
        sh, el, wr = _a(P['_' + s + 'sh']), _a(P['_' + s + 'el']), _a(P['_' + s + 'wrist'])
        a1 = el - sh; a2 = wr - el; cosang = float(-(a1 @ a2) / (np.linalg.norm(a1) * np.linalg.norm(a2) + 1e-9))
        ang = math.degrees(math.acos(max(-1.0, min(1.0, cosang))))
        if ang < 25.0: out.append(('elbow-fold', f'{side} elbow folded to {ang:.0f} deg', (25.0 - ang) / 100))
    # the two arms
    if P.get('_rel') is not None and P.get('_lel') is not None:
        re_, rw_, le_, lw_ = _a(P['_rel']), _a(P['_rwrist']), _a(P['_lel']), _a(P['_lwrist'])
        d = seg_dist(re_, re_ + (rw_ - re_) * 0.7, le_, le_ + (lw_ - le_) * 0.7)          # the wrists themselves may touch (clap)
        if 2 * R_FORE - d > TOL: out.append(('arm-arm', f'forearms {100 * (2 * R_FORE - d):.0f} cm into each other', 2 * R_FORE - d))
        hr = hand_centre(P, 'r'); hl = hand_centre(P, 'l'); d = float(np.linalg.norm(hr - hl))
        if d < 0.028: out.append(('arm-arm', f'hands overlap ({d * 100:.0f} cm apart)', 0.028 - d))
        # fingers through the other hand: each fingertip vs the other hand's finger bones (hand centre -> tips)
        for a_, b_, hb in (('r', 'l', hl), ('l', 'r', hr)):
            ta, tb = P.get('_' + a_ + 'tips'), P.get('_' + b_ + 'tips')
            if not ta or not tb: continue
            dm = min(seg_dist(_a(t), _a(t), hb, _a(u)) for t in ta for u in tb)
            if dm < 0.012: out.append(('arm-arm', f'{"right" if a_ == "r" else "left"} fingers through the other hand (a tip {dm * 100:.1f} cm from its finger bones)', 0.012 - dm)); break
    # legs
    if P.get('_rknee') is not None and P.get('_lknee') is not None:
        for a, b, r, nm in (('hip', 'knee', R_THIGH, 'thighs'), ('knee', 'ankle', R_SHIN, 'shins')):
            d = seg_dist(_a(P['_r' + a]) + (_a(P['_r' + b]) - _a(P['_r' + a])) * 0.15, _a(P['_r' + b]),
                         _a(P['_l' + a]) + (_a(P['_l' + b]) - _a(P['_l' + a])) * 0.15, _a(P['_l' + b]))
            if 2 * r - d > TOL * 1.5: out.append(('leg-leg', f'{nm} {100 * (2 * r - d):.0f} cm into each other', 2 * r - d))
        gy = float(_a(P.get('base', base if base is not None else (0, 0, 0)))[1])
        for s, side in (('r', 'right'), ('l', 'left')):
            h = float(_a(P['_' + s + 'ankle'])[1]) - gy
            if h < 0.045: out.append(('foot-ground', f'{side} ankle {100 * (0.075 - h):.0f} cm too low (foot in the ground)', 0.075 - h))
    return out

def joints(P):
    """body-relative joint positions tracked for jumps (relative to the pelvis, so walking / travelling is not a jump)"""
    pel = _a(P.get('_pel'))
    if pel is None: return {}
    J = {}
    for n, key in (('head', '_head'), ('chest', '_chest'), ('rwrist', '_rwrist'), ('lwrist', '_lwrist'), ('rel', '_rel'), ('lel', '_lel'),
                   ('rknee', '_rknee'), ('lknee', '_lknee'), ('rankle', '_rankle'), ('lankle', '_lankle')):
        if P.get(key) is not None: J[n] = _a(P[key]) - pel
    for s in 'rl':
        tp = P.get('_' + s + 'tips')
        if tp: J[s + 'tip'] = _a(tp[1]) - pel
    return J

class Monitor:
    """collects check_pose + per-joint speed / pop over frames, for any number of characters"""
    def __init__(self, fps=24):
        self.fps = fps; self.s = 24.0 / fps; self.t = None; self.cur = []; self.prev = {}; self.vel = {}; self.issues = []
    def frame(self, t):
        self._flush(); self.t = t
    def cut(self):
        """a camera cut / scene change: do not measure speed across it"""
        self._flush(); self.prev = {}; self.vel = {}
    def add(self, S, P, who=None):
        if who is None:
            sig = (S.get('h'), S.get('build'), str(S.get('tunic')), str(S.get('hair'))); n = sum(1 for w, _ in self.cur if w[:4] == sig)
            who = sig + (n,)
        self.cur.append((who, {k: v for k, v in P.items() if k.startswith('_') or k in ('base', 'walk', 'stride')}))
    def _flush(self):
        if self.t is None or not self.cur: self.cur = []; return
        poses = self.cur; self.cur = []
        for i, (who, P) in enumerate(poses):
            others = [Q for j, (_, Q) in enumerate(poses) if j != i]
            for kind, msg, d in check_pose(P, others=others): self.issues.append((self.t, self._name(who), kind, msg, d))
            J = joints(P); pv = self.prev.get(who); vv = self.vel.get(who, {})
            moving = P.get('walk') is not None or (pv is not None and '_base' in pv and float(np.linalg.norm(_a(P.get('base', (0, 0, 0))) - pv['_base'])) / self.s > 0.02)
            nv = {}
            if pv is not None:
                for n, p in J.items():
                    if n not in pv or n == '_base': continue
                    v = (p - pv[n]) / self.s; sp = float(np.linalg.norm(v)); nv[n] = v
                    lim, plim = SPEED[n], POP[n]
                    if moving:                                           # walking / running: legs and arm swing are fast by design
                        f_ = 4.0 if n[1:] in ('knee', 'ankle') else (1.6 if n != 'head' and n != 'chest' else 1.3); lim *= f_; plim *= f_
                    if sp > lim: self.issues.append((self.t, self._name(who), 'jump', f'{n} moves {sp * 100:.0f} cm in one frame ({sp * 24:.1f} m/s)', sp))
                    elif n in vv:
                        a = float(np.linalg.norm(v - vv[n]))
                        if a > plim: self.issues.append((self.t, self._name(who), 'pop', f'{n} changes speed by {a * 100:.0f} cm/frame at once', a))
            J['_base'] = _a(P.get('base', (0, 0, 0))); self.prev[who] = J; self.vel[who] = nv
    def _name(self, who): return who if isinstance(who, str) else f'char{who[-1]}' if not isinstance(who, tuple) else f"h{who[0]:.2f}#{who[-1]}"
    def close(self): self._flush(); return self.issues
    def windows(self, gap=0.25):
        """issues merged into time windows per (who, kind, part): [(t0, t1, who, kind, worst message, worst value, frames)]"""
        self.close(); W = []
        key = lambda it: (it[1], it[2], ' '.join(w for w in it[3].split() if not any(ch.isdigit() for ch in w))[:40])
        for it in sorted(self.issues, key=lambda it: (key(it), it[0])):
            if W and W[-1][7] == key(it) and it[0] - W[-1][1] <= gap:
                w = W[-1]; W[-1] = (w[0], it[0], w[2], w[3], it[3] if it[4] > w[5] else w[4], max(w[5], it[4]), w[6] + 1, w[7])
            else: W.append((it[0], it[0], it[1], it[2], it[3], it[4], 1, key(it)))
        return sorted([w[:7] for w in W])
    def text(self):
        W = self.windows()
        if not W: return 'body checks: 0 issues'
        L = [f'body checks: {len(W)} issue windows']
        for t0, t1, who, kind, msg, v, n in W: L.append(f'  {t0:6.2f}-{t1:6.2f}s  {who:10s} {kind:11s} {msg}  ({n} frames)')
        return '\n'.join(L)

def install(mon):
    """wrap hd.human so every call in a script is checked (call mon.frame(t) before each frame). Returns an uninstall function."""
    from . import hd
    orig = hd.human
    def human(S, P, *a, **kw):
        Q = orig(S, P, *a, **kw)
        try: mon.add(S, P)
        except Exception as e: mon.issues.append((mon.t or 0.0, 'check', 'error', f'bodycheck failed: {type(e).__name__}: {e}', 0.0))
        return Q
    human.__wrapped__ = orig                       # body.Performer's own still-pose evaluations call this one (not counted as characters)
    hd.human = human
    def undo(): hd.human = orig
    return undo
