"""Characters vs set props for examples/loading_tips.py (28 Nov 2026, the night_freeze lesson: 'NPCs in the walls').
Every frame (no render): each visible character's vertices are tested against the solid props (wall blocks, towers, pots, the chest,
the tip board, the dragon plinth, Bob's crate, torch posts, scaffold poles). Prints the hit windows per character + prop.
  python tools/qa/props_lt.py [--step 1] [--t0 0 --t1 99]"""
import os, sys, io, argparse, contextlib, math
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')); sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'examples'))
import numpy as np
ap = argparse.ArgumentParser(); ap.add_argument('--step', type=int, default=1); ap.add_argument('--t0', type=float, default=0.0); ap.add_argument('--t1', type=float, default=1e9)
a = ap.parse_args()
os.environ.pop('TEST', None)
with contextlib.redirect_stdout(io.StringIO()): import loading_tips as L
V = np.array
def boxes(t):
    """axis-aligned solids (name, lo, hi), shrunk 1 cm"""
    u = L.TT(t); out = []
    for c, h_, col, ap_, n in L.BLOCKS:
        if ap_ is not None and u < ap_ + 0.18: continue
        c = V(c); h_ = V(h_); out.append(('wall', c - h_ + 0.01, c + h_ - 0.01))
    out.append(('crate', V((L.BOB_X - 0.3, 0.0, 6.6)) + 0.01, V((L.BOB_X + 0.3, 0.49, 7.1)) - 0.01))
    out.append(('plinth', L.DRAGON_AT - V((0.5, 0.0, 0.5)) + 0.01, L.DRAGON_AT + V((0.5, L.PLINTH_H, 0.5)) - 0.01))
    cy = L.chest_y(t)
    if cy is not None: out.append(('chest', L.CHEST_AT + V((-0.3, cy, -0.3)), L.CHEST_AT + V((0.3, cy + 0.5, 0.3))))
    return out
def cyls(t):
    """vertical cylinders (name, centre xz, radius, y0, y1)"""
    u = L.TT(t); out = []
    if u < L.T_SMASH: out.append(('pot', L.POT_BIG, 0.33, 0.0, 0.76))
    for p in L.POTS_SMALL: out.append(('small pot', p, 0.18, 0.0, 0.42))
    for p in L.TORCH_POS: out.append(('torch post', p, 0.05, 0.0, 1.4))
    for x in (1.75, 2.85, 3.95):
        for z in (5.35, 5.9): out.append(('scaffold pole', V((x, 0.0, z)), 0.03, 0.0, 2.75))
    out.append(('board', L.BOARD + V((0, 0, 0)), 0.12, 0.62, 1.38))           # the board itself is thin: a short fat cylinder around its centre line is enough
    return out
def chars(t):
    out = []
    with contextlib.redirect_stdout(io.StringIO()):
        BP, BX = L.bob_state(t)
        if BX['vis']: out.append(('Bob', L.goblin(L.BOB, BP)))
        for nm, fn, S_ in (('G1', L.g1_state, L.G1), ('G2', L.g2_state, L.G2), ('G3', L.g3_state, L.G3)):
            P, _ = fn(t); out.append((nm, L.goblin(S_, P)))
        HP, HX = L.hero_state(t)
        if HP is not None and not HX['sil']: out.append(('hero', L.knight(HP)))
    return out
hits = {}
f = int(round(a.t0 * L.FPS)); last = int(min(L.DUR, a.t1) * L.FPS)
while f < last:
    t = f / L.FPS; B = boxes(t); C = cyls(t)
    for nm, Q in chars(t):
        P = np.array([p for q in Q for p in q['p']], float)
        for pn, lo, hi in B:
            if pn == 'crate' and nm == 'Bob': continue
            inside = np.all((P > lo) & (P < hi), axis=1)
            if inside.any():
                d = float(np.min(np.minimum(P[inside] - lo, hi - P[inside]).min(1)))
                if d > 0.015: hits.setdefault((nm, pn), []).append((t, d))
        for pn, c, r, y0, y1 in C:
            if nm == 'Bob' and pn == 'pot': continue
            dx = P[:, 0] - c[0]; dz = P[:, 2] - c[2]; rr = np.sqrt(dx * dx + dz * dz)
            inside = (rr < r - 0.01) & (P[:, 1] > y0) & (P[:, 1] < y1)
            if inside.any():
                d = float((r - rr[inside]).max())
                if d > 0.015: hits.setdefault((nm, pn), []).append((t, d))
    f += a.step
if not hits: print('props: 0 hits'); sys.exit(0)
for (nm, pn), lst in sorted(hits.items()):
    ts = [x[0] for x in lst]; win_ = []; s0 = ts[0]; p_ = ts[0]
    for x in ts[1:]:
        if x - p_ > 1.5 * a.step / L.FPS: win_.append((s0, p_)); s0 = x
        p_ = x
    win_.append((s0, p_))
    print(f'{nm:5s} in {pn:13s} max {max(x[1] for x in lst):.3f} m  ' + ', '.join(f'{x:.2f}-{y:.2f} ({L.scene(x)})' for x, y in win_))
sys.exit(1)
