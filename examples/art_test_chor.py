"""ART DIRECTION TEST (28 Nov 2026): shared choreography for the same 8 s silent gag in nightkit (examples/art_test.py) and
Blender (blender/art_test.py). Pure math, no engine imports: positions, phases and acting values per time, so both films
tell the joke frame-for-frame the same way and only the look differs.

The gag: the tall instructor demonstrates a precise hurdle jump (feet together, "ta-da"). The squat knight nods, slaps his
loose visor up, charges; the visor slips over his eyes; he runs blind into the hurdle and folds over it. The visor creaks up,
drops again. The instructor stands feet together, deadpan. A weak thumbs-up.
Units: metres, seconds; y up; the run goes along +z; the hurdle stands at z = 0."""
import math
DUR = 8.0; FPS = 24
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def seg(t, a, b): return clamp((t - a) / (b - a)) if b > a else (1.0 if t >= b else 0.0)
def sm(u): u = clamp(u); return u * u * (3 - 2 * u)
def win(t, a, b, r=0.2): return sm(seg(t, a, a + r)) * (1 - sm(seg(t, b - r, b)))
def lerp(a, b, u): return a + (b - a) * u

HURDLE_Z = 0.0; HURDLE_H = 0.95; HURDLE_HALF = 0.75
# ---------------- beats ----------------
I_CROUCH = (0.35, 0.7); I_JUMP = (0.7, 1.25); I_LAND = (1.25, 1.45); I_TADA = (1.45, 2.3); I_TURN = (2.35, 2.9)
I_POINT = (6.2, 7.4)                                    # after the crash: points precisely at the top bar (demonstrates again)
K_NOD = (1.55, 2.1); K_SLAP = (2.2, 2.55)              # nods, slaps the visor up (it bounces: planted, it is loose)
K_RUN = (2.7, 4.85)                                     # runs at the hurdle
K_SLIP = 3.55                                           # the visor slips down over his eyes (clank)
K_CRASH = 4.85                                          # hits the hurdle, folds over it
K_CREAK = (6.0, 6.6); K_DROP = 6.62                     # the visor creaks up ... and drops again
K_THUMB = (7.0, 7.7)
I_Z0, I_Z1 = -0.75, 0.75; I_X = 0.55; I_X1 = -1.35          # after the ta-da he steps aside to watch
K_Z0 = -3.3; K_X = -0.32; K_X0 = -0.95; K_ZC = HURDLE_Z - 0.4        # knight start / contact

def instructor(t):
    """dict: x, z, y (lift of the feet), yaw, crouch 0..1, tuck 0..1 (knees in the air), arms ('side' / 'up' / 'behind' / 'point', amount), head turn"""
    d = dict(x=I_X, z=I_Z0, y=0.0, yaw=0.0, crouch=0.0, tuck=0.0, arms='side', arms_k=0.0, head=0.0, blink=False)
    d['crouch'] = 0.28 * win(t, I_CROUCH[0], I_JUMP[0] + 0.08, 0.2) + 0.22 * win(t, I_JUMP[1] - 0.02, I_LAND[1] + 0.15, 0.08)
    if I_JUMP[0] <= t < I_JUMP[1]:
        u = seg(t, *I_JUMP); d['z'] = lerp(I_Z0, I_Z1, u); d['y'] = 0.85 * math.sin(math.pi * u); d['tuck'] = math.sin(math.pi * u)
    elif t >= I_JUMP[1]: d['z'] = I_Z1
    if t < I_CROUCH[1]: d['arms'] = 'back'; d['arms_k'] = win(t, I_CROUCH[0], I_JUMP[0] + 0.1, 0.2)
    if I_JUMP[0] <= t < I_LAND[1]: d['arms'] = 'up'; d['arms_k'] = 0.6
    if I_LAND[1] <= t < I_TURN[0] + 0.3: d['arms'] = 'up'; d['arms_k'] = win(t, I_LAND[1] - 0.1, I_TURN[0] + 0.3, 0.15)       # ta-da
    if t >= I_TURN[0]:
        d['x'] = lerp(I_X, I_X1, sm(seg(t, *I_TURN))); d['step'] = I_TURN[0] < t < I_TURN[1]
        d['yaw'] = math.pi * sm(seg(t, *I_TURN)); d['arms'] = 'behind'; d['arms_k'] = sm(seg(t, I_TURN[0] + 0.2, I_TURN[1]))
    if t >= I_POINT[0]: d['arms'] = 'point'; d['arms_k'] = win(t, I_POINT[0], I_POINT[1], 0.25)
    d['blink'] = any(a <= t < a + 0.12 for a in (3.1, 5.6, 7.75))
    d['head'] = 0.0 if t < K_CRASH else 0.15 * sm(seg(t, K_CRASH + 0.2, K_CRASH + 0.6))            # looks down at the folded knight
    return d

def _kz(t):
    """the knight's z: stands, accelerates, runs at ~2 m/s, stops dead at the hurdle"""
    if t < K_RUN[0]: return K_Z0
    if t >= K_CRASH: return K_ZC
    u = seg(t, K_RUN[0], K_CRASH)
    return lerp(K_Z0, K_ZC, u ** 1.35)
def knight(t):
    """dict: x, z, yaw, run phase, speed, visor 0 up .. 1 over the eyes, fold 0..1 over the hurdle, head look, arms mode"""
    pr = (_kz(t) - K_Z0) / (K_ZC - K_Z0)
    d = dict(x=lerp(K_X0, K_X, pr), z=_kz(t), yaw=math.atan2(K_X - K_X0, K_ZC - K_Z0) * (1.0 if K_RUN[0] - 0.2 < t < K_CRASH else 0.0), phase=0.0, speed=0.0, visor=0.0, fold=0.0, look_up=0.0, look_side=0.0, arms='rest', arms_k=0.0)
    h = 0.02
    d['speed'] = (_kz(t + h) - _kz(t - h)) / (2 * h) if K_RUN[0] < t < K_CRASH else 0.0
    d['phase'] = 2 * math.pi * (1.6 * (t - K_RUN[0])) if t >= K_RUN[0] else 0.0
    # watches the demo: eyes follow the instructor, a nod
    if t < K_RUN[0]:
        iz = instructor(t)['z']; d['look_side'] = 0.25 * (iz - I_Z0) / (I_Z1 - I_Z0)
        d['look_up'] = 0.25 * win(t, I_JUMP[0], I_LAND[1], 0.15) - 0.25 * math.sin(math.pi * seg(t, *K_NOD)) * (seg(t, *K_NOD) < 1)
    # the visor: 0.15 resting, slapped up to 0 (bounces), slips to 1 at K_SLIP, creaks up, drops
    v = 0.15
    if t >= K_SLAP[0]: v = lerp(0.15, 0.0, sm(seg(t, K_SLAP[0], K_SLAP[0] + 0.12))) + 0.08 * math.exp(-8 * max(0, t - K_SLAP[0] - 0.12)) * abs(math.sin(25 * max(0, t - K_SLAP[0] - 0.12)))
    if t >= K_SLIP: v = min(1.0, (t - K_SLIP) / 0.12) ** 2
    if t >= K_CREAK[0]: v = 1.0 - 0.55 * sm(seg(t, *K_CREAK))
    if t >= K_DROP: v = min(1.0, 0.45 + (t - K_DROP) / 0.1 * 0.55)
    d['visor'] = v
    if K_SLAP[0] <= t < K_SLAP[1] + 0.2: d['arms'] = 'slap'; d['arms_k'] = win(t, K_SLAP[0] - 0.15, K_SLAP[1] + 0.2, 0.12)
    if K_RUN[0] <= t < K_CRASH:
        d['arms'] = 'run'; d['arms_k'] = sm(seg(t, K_RUN[0], K_RUN[0] + 0.3))
        if t >= K_SLIP + 0.15: d['arms'] = 'blind'; d['arms_k'] = sm(seg(t, K_SLIP + 0.15, K_SLIP + 0.45)); d['look_up'] = 0.3
    if t >= K_CRASH:
        d['fold'] = sm(seg(t, K_CRASH, K_CRASH + 0.28)); d['arms'] = 'dangle'; d['arms_k'] = d['fold']
        d['look_up'] = 0.4 * sm(seg(t, *K_CREAK)) * (t < K_DROP + 0.1)
        if t >= K_THUMB[0]: d['arms'] = 'thumb'; d['arms_k'] = sm(seg(t, K_THUMB[0], K_THUMB[0] + 0.35))
    return d

def hurdle_wobble(t):
    """rotation (rad) of the hurdle about its base after the hit: a damped rock, it holds"""
    if t < K_CRASH: return 0.0
    u = t - K_CRASH; return 0.12 * math.exp(-3.2 * u) * math.sin(14 * u)

SHOTS = [  # (name, t0, t1, cam pos start, cam pos end, target start, target end, fov)
    ('A', 0.0, 2.75, (0.55, 1.42, 4.6), (0.5, 1.38, 4.2), (-0.05, 0.95, -1.2), (-0.05, 0.95, -1.3), 46.0),
    ('B', 2.75, 5.45, None, None, None, None, 46.0),
    ('C', 5.45, 8.0, (2.25, 1.15, 0.55), (2.05, 1.12, 0.5), (-0.55, 0.85, 0.35), (-0.55, 0.85, 0.35), 50.0)]
def camera(t):
    """A: wide on the demo, the knight watching behind; B: tracks backwards ~2.4 m in front of the running knight (beside the posts);
    C: side two-shot of the folded knight + the deadpan instructor"""
    if t < SHOTS[1][1]: nm, a, b, p0, p1, g0, g1, fov = SHOTS[0]
    elif t < SHOTS[2][1]:
        kz = _kz(t); kx = knight(t)['x']; z = min(kz + 2.1, 1.6)
        return 'B', (1.05, 1.38, z), (kx - 0.05, 1.22, min(kz, HURDLE_Z - 0.3)), 46.0
    else: nm, a, b, p0, p1, g0, g1, fov = SHOTS[2]
    u = sm(seg(t, a, b)); return nm, tuple(lerp(p0[i], p1[i], u) for i in range(3)), tuple(lerp(g0[i], g1[i], u) for i in range(3)), fov

def sound_events():
    """(time, kind) for both films' foley"""
    ev = [(I_CROUCH[0] + 0.1, 'cloth'), (I_JUMP[0], 'whoosh'), (I_LAND[0], 'land'), (I_TADA[0], 'tada'), (K_SLAP[0] + 0.1, 'clank'),
          (K_SLIP, 'clank'), (K_CRASH, 'crash'), (K_CREAK[0], 'creak'), (K_DROP, 'clank'), (K_THUMB[0] + 0.2, 'tiny')]
    x = K_RUN[0] + 0.15
    while x < K_CRASH - 0.05: ev.append((x, 'step')); x += 1 / 3.2
    return sorted(ev)
