"""THE LAST RESPAWN (58 s, 1080x1920, 24 fps) - Blender 5.3 EEVEE, phases 1-3 (blockout, hook test, loop test).
Brief: briefs/last_respawn.md (wins) + briefs/last_respawn_gpt.md. Characters are rigid-part puppets (parts parented to empties),
posed every frame from Python by a frame_change_pre handler (no keyframes, no skinning, no cloth).

Time: frame f (1..1392), t = (f-1)/24. The opening (t < 8) and the ending (t >= 52) are ONE virtual shot in loop time u:
u = t for the opening, u = t - 58 for the ending, so frame 1392 (u = -1/24) flows into frame 1 (u = 0). Everything in the
alley (camera, goblin, arrow, sound) is a function of u. 8 <= t < 52 is a coarse animatic (beats B1-B6) for staging only.

Run (PowerShell, repo root):
  $env:MODE='still'; $env:FRAMES='1'; $env:PCT='100'; $env:SAMPLES='64'; blender -b --factory-startup --python blender/last_respawn.py
  $env:MODE='anim';  $env:FRAMES='1-192'   -> renders/last_respawn/preview/f_####.png (PCT 50, SAMPLES 16 default)
  python blender/last_respawn.py audio      -> renders/last_respawn/audio/{full,hook,loop}.wav (system Python, numpy + soundfile)
  $env:MODE='mux'; $env:CUT='hook'|'loop'   -> renders/last_respawn/last_respawn_<cut>_.mp4
Voices are PLACEHOLDERS (tools/tts/lrs.py, Kokoro) until Enes's takes exist."""
import os, sys, math, json
import numpy as np

FPS = 24
NF = 1392
T_END = NF / FPS                       # 58.0
MODE = os.environ.get('MODE', 'audio' if (len(sys.argv) > 1 and sys.argv[-1] == 'audio') else 'still')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get('OUT', os.path.join(os.path.dirname(REPO), 'renders', 'last_respawn'))
TTS = os.environ.get('TTS_DIR', os.path.join(REPO, 'tts'))
CH = (60.0, 0.0, 0.0)                  # bell chamber origin (separate set, far from the alley)

# ======================================================================================
#  shared timing (pure python: used by picture AND sound)
# ======================================================================================
V = 3.2                                # run speed m/s
T_HIT = 0.25                           # arrow impact (u)
T_LOOSE = -0.75                        # arrow leaves the bow (u, end of the film)
T_VANISH = 0.85                        # goblin dissolves
T_RESPAWN = 1.2                        # goblin re-appears above the knight
T_CATCH = 1.5
T_SNAP = 3.4                           # HUD 1 -> 0
T_END_RESPAWN = -5.8                   # goblin restored in the alley (u)

# the script (v2, 23 Nov: Enes "too many silent parts" -> 23 lines, no gap over ~3 s except the bell and the wordless reach).
# (key, start t, speaker, text, highlighted word, colour c=cyan a=amber). Durations come from tts/lrs/script.json.
SCRIPT = [
    ('l01', 1.85, 'G', 'Not again!', 'again!', 'c'),
    ('l02', 3.75, 'K', 'Who keeps doing that?', 'Who', 'a'),
    ('l03', 5.9, 'G', 'The bell stopped!', 'bell', 'a'),
    ('l04', 7.1, 'K', 'Then we wake it up.', 'wake', 'a'),
    ('l05', 9.0, 'G', "And they're coming!", 'coming!', 'a'),
    ('l06', 10.7, 'K', 'Empty armour. They follow the bell.', 'Empty', 'c'),
    ('l07', 13.3, 'G', 'Then why are they following US?!', 'US?!', 'a'),
    ('l08', 16.0, 'B', 'The bell needs one last life!', 'life!', 'c'),
    ('l09', 18.6, 'K', 'Take mine!', 'mine!', 'c'),
    ('l10', 20.0, 'B', 'You gave yours years ago.', 'years', 'a'),
    ('l11', 22.2, 'G', 'Gave what?', 'what?', 'a'),
    ('l12', 25.4, 'G', "You're hollow?", 'hollow?', 'c'),
    ('l13', 26.8, 'K', 'For a very long time.', 'long', 'a'),
    ('l14', 28.75, 'G', 'They followed us here!', 'here!', 'a'),
    ('l15', 31.0, 'B', 'They remember their commander.', 'commander.', 'a'),
    ('l16', 33.9, 'B', 'He built this bell. He was its first life.', 'first', 'c'),
    ('l17', 37.0, 'K', "And I'll be its last.", 'last.', 'c'),
    ('l18', 38.7, 'B', "Restart it, and you're gone.", 'gone.', 'c'),
    ('l19', 41.5, 'G', 'There has to be another way!', 'another', 'a'),
    ('l20', 43.6, 'K', "There isn't.", "isn't.", 'a'),
    ('l21', 45.4, 'K', 'Then make this one count.', 'count.', 'c'),
    ('l22', 54.0, 'G', 'Knight...?', 'Knight...?', 'c'),
    ('l23', T_END - 1.05, 'G', 'No... NOT AGAIN!', 'AGAIN!', 'c'),
]
LINES = {k: t for k, t, *_ in SCRIPT}
SPK = {k: s for k, _, s, *_ in SCRIPT}
TEXT = {k: x for k, _, _, x, *_ in SCRIPT}
HILITE = {k: (w, c) for k, _, _, _, w, c in SCRIPT}
LAST = SCRIPT[-1][0]


def lines_of(spk):
    return [k for k in LINES if SPK[k] == spk]


def talking(spk, t, durs):
    """0..1 mouth / nod amount while one of this speaker's lines plays at film time t."""
    for k in lines_of(spk):
        if LINES[k] <= t < LINES[k] + durs.get(k, 0.8):
            return 0.5 + 0.5 * abs(math.sin(2 * math.pi * 5.5 * (t - LINES[k])))
    return 0.0


def line_durs():
    try:
        return json.load(open(os.path.join(TTS, 'lrs', 'script.json')))['dur']
    except Exception:
        return {k: 0.3 + 0.07 * len(v) for k, v in TEXT.items()}


def ss(a, b, x):
    x = min(max((x - a) / (b - a), 0.0), 1.0)
    return x * x * (3 - 2 * x)


def bump(a, b, c, d, x):
    return ss(a, b, x) * (1 - ss(c, d, x))


def lerp(a, b, w):
    return a + (b - a) * w


def vel_g(u):
    if u < 0:
        return V * ss(-1.0, 0.0, u)
    if u < T_HIT:
        return V
    return V * (1 - ss(T_HIT, 0.75, u))


def vel_k(u):
    if u < 0:
        return V * ss(-1.0, 0.0, u)
    if u < 0.5:
        return V
    return V * (1 - ss(0.5, 1.7, u))


_UG = np.arange(-7.0, 9.0 + 1e-9, 1 / 480)
_I0 = int(round(7.0 * 480))


def _integ(vf):
    v = np.array([vf(x) for x in _UG])
    c = np.concatenate([[0], np.cumsum((v[1:] + v[:-1]) / 2) / 480])
    return c - c[_I0]


_YG, _YK = _integ(vel_g), _integ(vel_k)


def Yg(u):
    return float(np.interp(u, _UG, _YG))


def Yk(u):
    return float(np.interp(u, _UG, _YK))


def loop_u(t):
    """loop time for the alley shot, None in the middle animatic."""
    if t < 8.0:
        return t
    if t >= 52.0:
        return t - T_END
    return None


GX, KX = -0.55, 0.55                   # goblin / knight lanes in the alley
ARCHER = (2.4, -13.0, 7.8)             # bow hand on the bridge


def arrow_target():
    return (GX + 0.1, Yg(T_HIT) - 0.08, 0.93)


def arrow_pos(u):
    p0, p1 = ARCHER, arrow_target()
    w = (u - T_LOOSE) / (T_HIT - T_LOOSE)
    return tuple(p0[i] + (p1[i] - p0[i]) * w for i in range(3))


def run_phase_g(u):
    return Yg(u) / 1.15 * 2 * math.pi + 1.3


def run_phase_k(u):
    return Yk(u) / 1.7 * 2 * math.pi


def b1_center(t):
    """B1 (8-15): both turn and run back towards -Y, shells behind them."""
    sp = lambda x: 2.8 * ss(8.8, 9.4, x)
    xs = np.linspace(8.0, t, 200) if t > 8 else np.array([8.0, 8.0])
    d = float(np.trapezoid([sp(x) for x in xs], xs)) if hasattr(np, 'trapezoid') else float(np.trapz([sp(x) for x in xs], xs))
    return Yk(8.0) - d, sp(t)


# ======================================================================================
#  THE MIDDLE (15-52 s, bell chamber) - pure data, shared with the future nightkit version
#  Chamber-local coordinates (metres): entrance gap at y = -8, bell above (0, 1.5), mechanism at (0, 2.6..3.0),
#  crank (0.9, 2.55), chain handle (1.6, 1.8, 1.9), slipping gear (-2.4, -0.2, 1.6), axis along y.
#  Every track is a list of keys; values between keys are smoothstep-eased, held before the first / after the last key.
# ======================================================================================
def key_at(keys, t):
    """keys = [(t, v0, v1, ...)]: eased piecewise interpolation, returns a tuple."""
    if t <= keys[0][0]:
        return tuple(keys[0][1:])
    for a, b in zip(keys[:-1], keys[1:]):
        if t < b[0]:
            w = ss(a[0], b[0], t)
            return tuple(x + (y - x) * w for x, y in zip(a[1:], b[1:]))
    return tuple(keys[-1][1:])


def cr_at(keys, t):
    """Catmull-Rom through camera keys (t, x, y, z, tx, ty, tz): the camera never stops inside the chamber.
    'CUT' entries split the list into separate shots."""
    segs, cur = [], []
    for k in keys:
        if k == 'CUT':
            segs.append(cur)
            cur = []
        else:
            cur.append(k)
    segs.append(cur)
    if len(segs) > 1:
        seg = segs[0]
        for sg in segs[1:]:
            if t >= sg[0][0]:
                seg = sg
        keys = seg
    if t <= keys[0][0]:
        return tuple(keys[0][1:])
    if t >= keys[-1][0]:
        return tuple(keys[-1][1:])
    i = max(j for j in range(len(keys) - 1) if keys[j][0] <= t)
    p0, p1, p2 = keys[max(i - 1, 0)], keys[i], keys[i + 1]
    p3 = keys[min(i + 2, len(keys) - 1)]
    s = (t - p1[0]) / (p2[0] - p1[0])
    s = 0.15 * s + 0.85 * s * s * (3 - 2 * s)          # mostly eased, never fully stopped
    out = []
    for k in range(1, 7):
        a, b, c, d = p0[k], p1[k], p2[k], p3[k]
        out.append(0.5 * (2 * b + (-a + c) * s + (2 * a - 5 * b + 4 * c - d) * s * s + (-a + 3 * b - 3 * c + d) * s ** 3))
    return tuple(out)


CAM_CH = [   # t, camera xyz, target xyz (chamber-local). v2 (23 Nov): every speaker in frame, no empty frames, no
    #          camera through bodies or gears; a CUT wherever the old path whipped across the room.
    (14.62, 0.1, -10.5, 1.75, 0.0, -5.8, 1.55),     # cut on the frame his torso fills (14.62), never through him
    (15.0, 0.1, -8.7, 1.75, 0.0, -4.0, 1.55),       # knight's back fills the lens, he runs away from us (occlusion reveal)
    (15.95, 0.0, -6.3, 1.75, -0.3, -2.3, 1.5),
    'CUT',                                          # the Bellwright, side-on beside the slipping gear (gear edge-on)
    (16.0, 0.6, -0.7, 1.85, -2.4, 0.55, 1.5),
    (16.85, 0.35, -0.9, 1.8, -2.4, 0.55, 1.5),
    'CUT',
    (16.9, -2.3, -2.7, 1.75, -0.4, -2.4, 1.6),
    (17.5, -0.9, 0.4, 1.7, -0.45, -2.5, 1.7),       # front: the sword knocks the falling hook away from the goblin
    (18.3, -1.3, 0.5, 1.75, -0.1, -1.6, 1.55),      # "Take mine!": medium shot, he steps up to the Bellwright
    (19.95, -1.5, 0.35, 1.75, 0.6, -0.6, 1.55),
    'CUT',                                          # the Bellwright answers (reverse shot from beside the knight)
    (20.0, -0.4, -0.05, 1.7, -2.4, 0.75, 1.5),
    (22.1, -0.75, 0.1, 1.65, -2.4, 0.75, 1.5),
    'CUT',                                          # the goblin: "Gave what?"
    (22.15, 1.2, -3.6, 1.35, -0.6, -2.8, 0.9),
    (23.45, 1.4, -2.6, 1.35, -0.6, -1.0, 0.9),
    'CUT',                                          # cut on the knight's turn
    (23.5, -1.3, -2.7, 1.6, 0.6, -0.6, 1.4),
    (24.8, -0.55, -1.95, 1.55, 0.55, -0.6, 1.35),   # push in: the open breastplate
    (25.6, -0.5, -4.8, 1.5, -0.2, -1.0, 1.15),      # both: the goblin recoils, the knight's open chest
    (27.35, -0.55, -5.0, 1.5, -0.2, -1.0, 1.2),
    'CUT',                                          # the shells arrive through the entrance
    (27.4, 2.6, -1.0, 1.6, 0.0, -6.5, 1.3),
    (28.4, 2.9, -1.5, 1.7, -0.2, -3.8, 1.2),
    (28.95, 2.9, -1.6, 1.75, -0.2, -3.8, 1.1),
    'CUT',                                          # from above the knight's shoulder: they kneel in unison (V formation)
    (29.0, -0.3, -0.2, 2.5, 0.0, -4.4, 0.5),
    (30.85, -0.3, -0.3, 2.5, 0.0, -4.4, 0.55),
    'CUT',                                          # low, behind the kneeling shells, up at their commander
    (30.9, 0.9, -6.6, 2.3, 0.6, -0.6, 1.6),
    (32.55, 0.7, -6.4, 2.25, 0.6, -0.6, 1.6),
    'CUT',                                          # the same emblem on the central gear (above the panel)
    (32.6, 2.0, -2.2, 2.2, 0.0, 2.8, 3.0),
    (34.0, 2.3, -2.6, 2.3, 0.0, 2.8, 3.0),
    (35.2, 1.6, -2.3, 1.75, 0.6, -0.6, 1.9),        # tilt down onto the knight
    (36.15, 1.5, -2.1, 1.75, 0.6, -0.6, 1.9),
    'CUT',                                          # the mechanism: the Bellwright opens the panel
    (36.2, -1.6, -0.6, 1.75, 0.0, 2.4, 1.7),
    (37.0, -1.4, -1.2, 1.75, 0.0, 2.0, 1.6),
    (39.5, -1.2, -0.4, 1.7, -0.5, 2.0, 1.5),
    (40.55, -1.0, -0.2, 1.7, -0.4, 2.0, 1.5),
    'CUT',                                          # beside the crank: his hand, the goblin's hands on his wrist
    (40.6, 1.95, 3.4, 1.6, 1.1, 1.8, 1.4),
    (43.5, 2.3, 3.4, 1.95, 0.9, 1.55, 1.7),
    (45.0, 3.3, 0.4, 2.15, 1.0, 1.6, 1.8),          # over the goblin's head onto the visor
    (47.6, 3.1, 0.1, 2.1, 1.1, 1.7, 1.7),
    (48.9, 3.6, -2.6, 1.2, 0.6, 1.2, 3.6),          # wide: the bell swings, the soul runs up into it, the armour falls
    (49.55, 3.5, -2.4, 1.25, 0.6, 1.2, 3.4),
    'CUT',                                          # from where the knight stood: the goblin's face as the light washes over him
    (49.6, 1.25, 2.25, 1.25, 1.75, 1.2, 1.05),
    (52.0, 1.35, 2.0, 1.1, 1.75, 1.2, 1.05),
]

KN_POS = [(14.6, 0.05, -9.4), (15.0, 0.05, -7.6), (16.2, -0.3, -2.2), (18.6, -0.3, -2.2), (19.2, 0.6, -0.6), (38.0, 0.6, -0.6), (39.3, 0.9, 1.55)]
KN_ROT = [(15.0, 0.0), (18.6, 0.0), (19.0, 1.19), (23.3, 1.19), (24.0, 2.42), (27.6, 2.42), (28.4, math.pi),
          (35.5, math.pi), (36.6, 0.15), (44.2, 0.15), (45.0, -1.96), (46.8, -1.96), (47.2, -1.22)]
GB_POS = [(14.6, 0.7, -10.1), (15.0, 0.7, -8.3), (16.4, -0.6, -2.95), (22.0, -0.6, -2.95), (23.0, -0.6, -0.95), (25.3, -0.6, -0.95),
          (25.8, -1.0, -1.35), (40.4, -1.0, -1.35), (40.8, 1.9, 0.9), (41.2, 1.65, 2.0), (44.3, 1.65, 2.0), (45.0, 1.75, 1.2)]
GB_ROT = [(15.0, 0.0), (22.0, 0.0), (23.0, -1.33), (27.6, -1.33), (28.2, -3.14), (36.0, -3.14), (36.6, 0.0),
          (40.3, 0.0), (40.5, -0.75), (41.0, -0.75), (41.3, 1.07), (44.4, 1.07), (45.0, 1.1)]
BW_POS = [(15.0, -2.4, 0.75), (36.0, -2.4, 0.75), (37.4, -0.7, 2.0)]
BW_ROT = [(15.0, math.pi), (19.5, math.pi), (20.3, 4.33), (30.8, 4.33), (31.4, 5.50), (38.3, 5.42), (38.7, 4.43)]
SHELL_X = [-1.6 + 0.8 * i for i in range(5)]           # V formation: never in a line along the lens
SHELL_Y = [-3.4 - 0.9 * abs(i - 2) for i in range(5)]
T_SHELLS_IN, T_SHELLS_STOP, T_KNEEL = 26.0, 28.8, 29.6
PLATE = [(15.0, 0.0), (24.0, 0.0), (24.8, 1.75), (33.5, 1.75), (34.2, 0.0)]
SWORD_DRAWN = (16.9, 36.0)
T_YANK, T_BELL, T_CRUMBLE = 47.5, 47.9, 48.8
T_WIPE = 14.62                         # B1 -> chamber: the knight's torso fills the lens

# pose keys: (t, blend seconds before t, {joint: (rx, ry, rz)}); joints not named go back to 0
KN_POSE = [
    (15.0, 0.1, {'cape': (-0.5, 0, 0)}),
    (16.9, 0.3, {'shoulder_R': (2.2, -0.3, 0), 'elbow_R': (0.4, 0, 0), 'shoulder_L': (0.4, 0.5, 0)}),
    (17.6, 0.15, {'shoulder_R': (1.2, -0.9, 0.6), 'elbow_R': (0.2, 0, 0), 'shoulder_L': (0.6, 0.7, 0)}),
    (18.3, 0.3, {'shoulder_R': (0.8, -0.2, 0), 'elbow_R': (0.8, 0, 0), 'shoulder_L': (0.3, 0.4, 0)}),
    (18.9, 0.3, {'shoulder_L': (1.0, -0.6, 0), 'elbow_L': (1.6, 0, 0), 'shoulder_R': (0.4, -0.1, 0), 'elbow_R': (0.6, 0, 0),
                 'torso': (-0.1, 0, 0), 'head': (0.1, 0, 0)}),
    (20.6, 0.5, {'shoulder_R': (0.25, 0, 0), 'elbow_R': (0.5, 0, 0), 'head': (0.05, 0, 0)}),
    (23.7, 0.3, {'head': (-0.45, 0, 0), 'shoulder_R': (0.25, 0, 0), 'elbow_R': (0.5, 0, 0)}),
    (24.0, 0.25, {'head': (-0.45, 0, 0), 'shoulder_L': (1.2, -0.5, 0), 'elbow_L': (1.2, 0, 0), 'elbow_R': (0.5, 0, 0)}),
    (25.0, 0.4, {'head': (-0.2, 0, 0), 'shoulder_L': (0.2, 0.2, 0), 'elbow_L': (0.3, 0, 0), 'elbow_R': (0.5, 0, 0)}),
    (27.8, 0.4, {'head': (0.0, 0, 0), 'elbow_R': (0.5, 0, 0)}),
    (29.8, 0.5, {'head': (-0.18, 0, 0), 'elbow_R': (0.5, 0, 0)}),
    (33.4, 0.3, {'head': (-0.3, 0, 0), 'shoulder_L': (1.1, -0.5, 0), 'elbow_L': (1.2, 0, 0)}),
    (34.4, 0.4, {'head': (0.0, 0, 0)}),
    (39.4, 0.4, {'shoulder_R': (1.25, 0.1, 0), 'elbow_R': (0.5, 0, 0), 'head': (-0.2, 0, 0)}),
    (43.0, 0.5, {'shoulder_R': (1.25, 0.1, 0), 'elbow_R': (0.5, 0, 0), 'head': (-0.1, 0, -0.6)}),
    (44.6, 0.4, {'shoulder_R': (1.25, 0.1, 0), 'elbow_R': (0.5, 0, 0), 'head': (-0.1, 0, -0.6),
                 'shoulder_L': (1.1, -0.7, 0), 'elbow_L': (0.4, 0, 0)}),
    (45.3, 0.4, {'shoulder_R': (0.4, 0, 0), 'elbow_R': (0.5, 0, 0), 'head': (-0.05, 0, -0.5)}),
    (47.1, 0.35, {'shoulder_R': (2.75, -0.35, 0), 'elbow_R': (0.2, 0, 0), 'head': (0.3, 0, 0)}),
    (47.65, 0.15, {'shoulder_R': (1.3, -0.2, 0), 'elbow_R': (1.2, 0, 0), 'torso': (-0.25, 0, 0), 'head': (0.15, 0, 0)}),
    (48.3, 0.4, {'shoulder_R': (0.6, -0.1, 0), 'elbow_R': (0.6, 0, 0), 'torso': (-0.1, 0, 0), 'head': (0.35, 0, 0)}),
]
GB_POSE = [
    (15.0, 0.1, {'scarf': (-0.9, 0, 0)}),
    (16.6, 0.3, {'torso': (-0.2, 0, 0), 'thigh_L': (0.3, 0, 0), 'knee_L': (-0.5, 0, 0), 'thigh_R': (0.3, 0, 0),
                 'knee_R': (-0.5, 0, 0), 'shoulder_L': (0.9, 0.3, 0), 'shoulder_R': (0.9, -0.3, 0), 'elbow_L': (1.0, 0, 0),
                 'elbow_R': (1.0, 0, 0)}),
    (17.45, 0.15, {'torso': (-0.45, 0, 0), 'thigh_L': (1.0, 0, 0), 'knee_L': (-1.6, 0, 0), 'thigh_R': (1.0, 0, 0),
                   'knee_R': (-1.6, 0, 0), 'shoulder_L': (2.7, 0.3, 0), 'shoulder_R': (2.7, -0.3, 0), 'elbow_L': (2.0, 0, 0),
                   'elbow_R': (2.0, 0, 0)}),
    (18.6, 0.4, {'torso': (-0.1, 0, 0), 'shoulder_L': (0.4, 0.2, 0), 'shoulder_R': (0.4, -0.2, 0), 'head': (0.25, 0, 0)}),
    (23.2, 0.4, {'head': (0.3, 0, 0), 'shoulder_R': (0.2, 0, 0)}),
    (25.5, 0.2, {'torso': (0.35, 0, 0), 'shoulder_L': (1.4, 0.4, 0), 'shoulder_R': (1.4, -0.4, 0), 'elbow_L': (1.0, 0, 0),
                 'elbow_R': (1.0, 0, 0), 'head': (0.2, 0, 0)}),
    (27.0, 0.5, {'torso': (0.1, 0, 0), 'shoulder_L': (0.4, 0.2, 0), 'shoulder_R': (0.4, -0.2, 0), 'head': (0.25, 0, 0)}),
    (29.8, 0.3, {'torso': (0.15, 0, 0), 'head': (0.1, 0, 0), 'shoulder_L': (0.3, 0.3, 0), 'shoulder_R': (0.3, -0.3, 0)}),
    (31.5, 0.5, {'head': (0.2, 0, 0)}),
    (41.2, 0.25, {'shoulder_L': (1.45, 0.25, 0), 'shoulder_R': (1.45, -0.25, 0), 'elbow_L': (0.3, 0, 0), 'elbow_R': (0.3, 0, 0),
                  'torso': (-0.15, 0, 0), 'head': (0.35, 0, 0)}),
    (44.8, 0.4, {'shoulder_L': (0.3, 0.1, 0), 'shoulder_R': (0.3, -0.1, 0), 'head': (0.35, 0, 0)}),
    (48.2, 0.3, {'torso': (0.3, 0, 0), 'shoulder_L': (2.5, 0.4, 0), 'shoulder_R': (2.5, -0.4, 0), 'elbow_L': (1.6, 0, 0),
                 'elbow_R': (1.6, 0, 0), 'head': (0.15, 0, 0)}),
    (49.6, 0.6, {'torso': (0.1, 0, 0), 'shoulder_R': (1.4, 0, 0), 'elbow_R': (0.2, 0, 0), 'shoulder_L': (0.7, 0.3, 0),
                 'head': (0.1, 0, 0)}),
]
BW_POSE = [
    (15.0, 0.1, {'shoulder_L': (1.6, 0, 0), 'shoulder_R': (1.6, 0, 0), 'elbow_L': (0.4, 0, 0), 'elbow_R': (0.4, 0, 0),
                 'torso': (-0.35, 0, 0), 'thigh_L': (0.45, 0, 0), 'knee_L': (-0.3, 0, 0), 'thigh_R': (-0.3, 0, 0)}),
    (16.2, 0.3, {'shoulder_L': (1.6, 0, 0), 'shoulder_R': (1.6, 0, 0), 'elbow_L': (0.4, 0, 0), 'elbow_R': (0.4, 0, 0),
                 'torso': (-0.35, 0, 0), 'thigh_L': (0.45, 0, 0), 'knee_L': (-0.3, 0, 0), 'thigh_R': (-0.3, 0, 0),
                 'head': (0, 0, 0.6)}),
    (19.9, 0.6, {'head': (0, 0, 0)}),
    (22.4, 0.3, {'shoulder_R': (1.5, -0.1, 0), 'elbow_R': (0.1, 0, 0)}),
    (24.0, 0.5, {'head': (-0.1, 0, 0)}),
    (31.4, 0.4, {'shoulder_R': (1.3, -0.3, 0), 'elbow_R': (0.2, 0, 0)}),
    (33.2, 0.5, {}),
    (37.8, 0.4, {'shoulder_L': (2.3, 0.2, 0), 'shoulder_R': (2.3, -0.2, 0), 'elbow_L': (0.5, 0, 0), 'elbow_R': (0.5, 0, 0)}),
    (38.5, 0.4, {'head': (0.05, 0, 0)}),
    (48.1, 0.3, {'shoulder_R': (2.6, -0.3, 0), 'elbow_R': (1.8, 0, 0), 'torso': (0.15, 0, 0), 'head': (-0.2, 0, 0)}),
]
GB_FACE = [(15.0, 'terror'), (16.0, 'shock'), (22.5, 'neutral'), (24.5, 'shock'), (27.0, 'shock'), (28.0, 'terror'),
           (29.8, 'shock'), (31.5, 'sad'), (38.6, 'shock'), (41.0, 'plead'), (44.5, 'sad'), (47.9, 'terror')]


def face_at(t):
    """(previous face, current face, blend) at time t."""
    i = max([j for j, (tk, _) in enumerate(GB_FACE) if tk <= t] or [0])
    cur = GB_FACE[i][1]
    prev = GB_FACE[i - 1][1] if i else cur
    return prev, cur, ss(GB_FACE[i][0], GB_FACE[i][0] + 0.25, t)


def pose_keys_at(keys, t):
    r = dict(keys[0][2])
    for tk, d, p in keys[1:]:
        w = ss(tk - d, tk, t)
        if w <= 0:
            break
        names = set(r) | set(p)
        r = {n: tuple(a + (b - a) * w for a, b in zip(r.get(n, (0, 0, 0)), p.get(n, (0, 0, 0)))) for n in names}
    return r


class Mover:
    """position track + walk phase (distance travelled) for one character, sampled once."""
    def __init__(self, pos, rot, stride):
        self.pos, self.rot, self.stride = pos, rot, stride
        self.tg = np.arange(14.5, 52.0 + 1e-9, 1 / 96)
        xy = np.array([key_at(pos, t) for t in self.tg])
        d = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(xy, axis=0).T))])
        self.dist = d
        self.speed = np.gradient(d, self.tg)

    def at(self, t):
        x, y = key_at(self.pos, t)
        rz = key_at(self.rot, t)[0]
        ph = float(np.interp(t, self.tg, self.dist)) / self.stride * 2 * math.pi
        sp = float(np.interp(t, self.tg, self.speed))
        return x, y, rz, ph, sp


MV_K = Mover(KN_POS, KN_ROT, 1.7)
MV_G = Mover(GB_POS, GB_ROT, 1.15)
MV_B = Mover(BW_POS, BW_ROT, 1.2)


# ======================================================================================
#  AUDIO (numpy + soundfile, system python)
# ======================================================================================
SR = 48000


def build_audio():
    import soundfile as sf
    rng = np.random.default_rng(11)
    n = int(SR * T_END)
    dry = np.zeros((2, n))
    wet = np.zeros((2, n))

    def ff(x, lo=None, hi=None):
        X = np.fft.rfft(x)
        f = np.maximum(np.fft.rfftfreq(len(x), 1 / SR), 1.0)
        g = np.ones_like(f)
        if lo:
            g *= 1 / np.sqrt(1 + (lo / f) ** 4)
        if hi:
            g *= 1 / np.sqrt(1 + (f / hi) ** 4)
        return np.fft.irfft(X * g, len(x))

    def nrm(x):
        p = np.max(np.abs(x))
        return x / p if p > 0 else x

    def place(bus, s, t0, g, pan=0.0):
        i = int(round(t0 * SR))
        if i < 0:
            s, i = s[-i:], 0
        if i >= n or len(s) == 0:
            return
        s = s[:n - i]
        a = (pan + 1) * math.pi / 4
        bus[0, i:i + len(s)] += s * g * math.cos(a)
        bus[1, i:i + len(s)] += s * g * math.sin(a)

    def tl(d):
        return np.arange(int(d * SR)) / SR

    # ---- ambience: low district hum + distant unintelligible market + gear ticks (alley), chamber rumble (middle)
    t = np.arange(n) / SR
    hum = (np.sin(2 * np.pi * 49 * t) + 0.5 * np.sin(2 * np.pi * 98 * t + 1) + 0.25 * np.sin(2 * np.pi * 147 * t)) * 0.5
    hum += nrm(ff(rng.standard_normal(n), 30, 160)) * 0.8
    for ch in range(2):
        dry[ch] += nrm(hum) * 0.05
        mk = nrm(ff(rng.standard_normal(n), 300, 1400))
        xp = np.arange(0, T_END + 2, 0.4)
        lfo = np.interp(t, xp, rng.uniform(0.2, 1.0, len(xp)))
        dry[ch] += mk * lfo * 0.012
    # gear ticks: irregular, "stuck" stutter (bell is failing), quiet and far
    tk = 0.3
    while tk < T_END:
        m = tl(0.03)
        s = nrm(ff(rng.standard_normal(len(m)), 1500, 6000)) * np.exp(-m / 0.006)
        g = 0.025 if (tk < 8 or tk > 52) else 0.04
        place(dry, s, tk, g, 0.3)
        place(wet, s, tk, g * 2, 0.3)
        tk += rng.choice([0.5, 0.5, 0.5, 0.25, 1.0])

    # ---- sfx library
    def clank(f0=520, d=0.18):
        m = tl(d)
        s = sum(np.sin(2 * np.pi * f0 * r * m) * a for r, a in [(1, 1), (2.41, 0.6), (3.9, 0.4), (5.3, 0.25)])
        s = s * np.exp(-m / 0.04) + 0.5 * nrm(ff(rng.standard_normal(len(m)), 800, 5000)) * np.exp(-m / 0.015)
        return nrm(s)

    def pat(d=0.08):
        m = tl(d)
        return nrm(ff(rng.standard_normal(len(m)), 120, 1500)) * np.exp(-m / 0.018)

    def thud(f0=70, d=0.35):
        m = tl(d)
        return nrm(np.sin(2 * np.pi * f0 * m * (1 + 0.6 * np.exp(-m / 0.03))) * np.exp(-m / 0.08)
                   + 0.4 * nrm(ff(rng.standard_normal(len(m)), 100, 900)) * np.exp(-m / 0.03))

    def crack(d=0.6, up=True):
        m = tl(d)
        z = nrm(ff(rng.standard_normal(len(m)), 2000, 12000)) * np.exp(-m / 0.03)
        f = (900 + 2600 * m / d) if up else (2400 - 1800 * m / d)
        sh = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-m / 0.25) * (1 + 0.5 * np.sin(2 * np.pi * 31 * m))
        return nrm(z + 0.6 * sh)

    def chime(d=1.4):
        m = tl(d)
        s = sum(np.sin(2 * np.pi * f * m) * np.exp(-m / dc) for f, dc in [(1318, 0.5), (1976, 0.4), (2637, 0.3)])
        return nrm(s * np.minimum(m / 0.01, 1))

    def bell(d=7.0):
        m = tl(d)
        s = sum(a * np.sin(2 * np.pi * 98 * r * m) * np.exp(-m / dc)
                for r, a, dc in [(0.5, 0.7, 4.0), (1, 1, 3.2), (1.19, 0.6, 2.2), (1.5, 0.5, 1.8), (2.0, 0.4, 1.3),
                                 (2.52, 0.3, 1.0), (3.0, 0.2, 0.7), (4.1, 0.15, 0.4)])
        return nrm(s * np.minimum(m / 0.003, 1) + 0.3 * thud(55, d)[:len(m)])

    # ---- footsteps from the same run phases as the picture
    def steps(phase_fn, ufrom, uto, t_of_u, kind, pan, gain):
        us = np.arange(ufrom, uto, 1 / 480)
        ph = np.array([phase_fn(x) for x in us])
        k = np.floor(ph / math.pi)
        for i in np.where(np.diff(k) > 0)[0]:
            tt = t_of_u(us[i + 1])
            if 0 <= tt < T_END:
                s = clank(rng.uniform(380, 460), 0.15) * 0.6 + thud(90, 0.15) if kind == 'K' else pat()
                place(dry, s, tt, gain, pan)

    steps(run_phase_k, 0.0, 1.75, lambda x: x, 'K', 0.25, 0.10)
    steps(run_phase_g, 0.0, T_HIT, lambda x: x, 'G', -0.25, 0.09)
    steps(run_phase_g, -1.0, 0.0, lambda x: x + T_END, 'G', -0.25, 0.09)
    # B1 run (8-15) + shells marching (synchronized clang, every 0.62 s)
    for tt in np.arange(9.2, 15.0, 0.19):
        place(dry, clank(rng.uniform(380, 460), 0.12) * 0.5 + thud(90, 0.12), tt, 0.07, 0.2)
    for tt in np.arange(8.4, 15.0, 0.62):
        place(dry, clank(300, 0.3), tt, 0.06, -0.1)
        place(wet, clank(300, 0.3), tt, 0.08, -0.1)

    # ---- the arrow whistle, ONE signal carried across the loop boundary
    wl = T_HIT - T_LOOSE                                   # 1.0 s
    m = tl(wl)
    prog = m / wl
    fq = 1400 + 1500 * prog ** 2
    wh = nrm(ff(rng.standard_normal(len(m)), 1800, 5200)) * 0.5 + np.sin(2 * np.pi * np.cumsum(fq) / SR)
    wh = wh * (0.15 + 0.85 * prog ** 1.6) * np.minimum(m / 0.05, 1)
    cut = int(-T_LOOSE * SR)                               # samples before the boundary
    place(dry, wh[:cut], T_END + T_LOOSE, 0.16, -0.15)    # ending: 57.25 .. 58.0
    place(dry, wh[cut:], 0.0, 0.16, -0.15)                # opening: 0.0 .. 0.25 (seamless continuation)
    place(dry, thud(80, 0.4), T_HIT, 0.32, -0.2)          # impact
    place(dry, nrm(ff(rng.standard_normal(int(0.12 * SR)), 600, 4000)) * np.exp(-tl(0.12) / 0.03), T_HIT, 0.12, -0.2)
    place(dry, clank(700, 0.25), T_END + T_LOOSE - 0.05, 0.05, 0.1)    # far bow twang (ending)
    m = tl(0.5)
    creak = nrm(ff((np.sin(2 * np.pi * np.cumsum(40 + 30 * m) / SR) > 0.95).astype(float), 300, 2500)) * np.hanning(len(m))
    place(dry, creak, T_END - 2.6, 0.06, 0.1)              # bow draw creak: the goblin hears it
    place(wet, creak, T_END - 2.6, 0.1, 0.1)

    # ---- respawn system
    place(dry, crack(0.5, False), T_VANISH, 0.12, -0.2)    # dissolve (falling zap)
    place(dry, crack(0.7, True), T_RESPAWN - 0.05, 0.2, 0.0)
    place(dry, clank(420, 0.3) + thud(70, 0.3), T_CATCH, 0.22, 0.1)   # caught in armour
    m = tl(0.25)
    snap = nrm(ff(rng.standard_normal(len(m)), 400, 3000)) * np.exp(-m / 0.02) + np.sin(2 * np.pi * 110 * m) * np.exp(-m / 0.1)
    place(dry, nrm(snap), T_SNAP, 0.22, 0.0)               # counter snaps to 0
    place(dry, thud(55, 0.6), T_SNAP + 0.02, 0.18, 0.0)
    place(dry, crack(0.7, True), T_END + T_END_RESPAWN, 0.2, -0.2)    # restored in the alley
    place(dry, chime(), T_END - 5.4, 0.08, 0.0)            # RESPAWNS RESTORED

    # ---- middle animatic sfx (coarse)
    m = tl(0.6)
    place(dry, nrm(ff(rng.standard_normal(len(m)), 200, 3000)) * np.hanning(len(m)), 14.5, 0.15, 0.5)   # knight passes the lens
    place(dry, thud(60, 0.5), T_WIPE, 0.2, 0.0)              # burst into the chamber
    place(dry, clank(760, 0.6), 17.55, 0.22, -0.2)         # sword knocks the hook away
    place(wet, clank(760, 0.6), 17.55, 0.25, -0.2)
    place(dry, clank(240, 0.6) + thud(60, 0.6), 18.2, 0.15, 0.3)    # hook hits the floor
    for tt in np.arange(T_SHELLS_IN, T_SHELLS_STOP, 0.62):        # the shells march in, in step
        place(dry, clank(300, 0.3), tt, 0.07, 0.0)
        place(wet, clank(300, 0.3), tt, 0.09, 0.0)
    for tt in np.arange(40.4, 41.2, 0.13):
        place(dry, pat(), tt, 0.08, 0.2)                    # the goblin runs to him
    for k in range(7):
        place(dry, clank(rng.uniform(300, 520), 0.5) + thud(70, 0.5), 49.0 + 0.3 * k + rng.uniform(0, 0.15), 0.09, rng.uniform(-0.4, 0.4))
    for tt in (16.6, 19.8):
        place(dry, clank(260, 0.5), tt, 0.08, 0.3)         # chains / gears
        place(wet, clank(260, 0.5), tt, 0.12, 0.3)
    place(dry, clank(600, 0.5), 24.0, 0.1, 0.0)            # breastplate opens
    for k in range(5):
        place(dry, clank(330 + 7 * k, 0.4) + thud(65, 0.4), 29.6 + 0.012 * k, 0.07, -0.4 + 0.2 * k)   # kneel in unison
        place(wet, clank(330, 0.4), 29.6, 0.1, 0.0)
    m = tl(14.0)
    rum = nrm(ff(rng.standard_normal(len(m)), 25, 120))
    rum = rum * np.minimum(m / 6, 1)
    place(dry, rum, 32.0, 0.08, 0.0)                       # rising gear rumble
    place(dry, clank(500, 0.6), 37.6, 0.1, 0.2)            # mechanism opens
    place(dry, thud(90, 0.4) + clank(350, 0.4), T_YANK, 0.2, 0.2)   # chain snaps tight
    bl = bell(7.0)[:int((52.0 - T_BELL) * SR)]           # the tail is CUT by the cycle reset at 52.0
    bl[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))
    place(dry, bl, T_BELL, 0.5, 0.0)
    place(wet, bl, T_BELL, 0.5, 0.0)
    m = tl(52.0 - T_BELL - 0.1)
    surge = nrm(ff(rng.standard_normal(len(m)), 200, 7000)) * np.minimum(m / 0.4, 1) * (0.4 + 0.6 * m / m[-1])
    place(dry, surge, T_BELL + 0.1, 0.12, 0.0)

    # ---- score (v2): a low string-like pad + clock pulse, so the film never sits in dead air. Ducked under the voices.
    #      3.4 (counter hits 0) -> 47.9 (the bell takes over); a lonely high pad 52.4 -> 56.9 (gone before the arrow whistle,
    #      so the loop boundary stays music-free and seamless).
    durs = line_durs()
    mus = np.zeros(n)
    hz = lambda m: 440.0 * 2 ** ((m - 69) / 12)
    CH_ = [(3.4, [50, 57, 62, 65]), (9.0, [50, 57, 62, 65]), (16.0, [46, 53, 58, 62]), (23.5, [43, 50, 55, 58]),
           (30.0, [45, 52, 57, 61]), (37.0, [50, 57, 62, 65, 69]), (41.5, [46, 53, 58, 62, 65]), (45.4, [45, 52, 57, 61, 64]),
           (47.9, [45, 52, 57, 61, 64])]

    def pad(notes, d, bright=1.0):
        m = tl(d)
        s = np.zeros(len(m))
        for nn in notes:
            f = hz(nn)
            for det in (-0.12, 0.0, 0.11):                 # three detuned voices per note (ensemble)
                ph = rng.uniform(0, 6.28)
                for h, a in ((1, 1.0), (2, 0.35 * bright), (3, 0.18 * bright), (4, 0.08 * bright)):
                    s += a * np.sin(2 * np.pi * f * (1 + det / 100) * h * m + ph * h)
        return s * (1 + 0.15 * np.sin(2 * np.pi * 0.23 * m))
    for (ta, notes), (tb, _) in zip(CH_[:-1], CH_[1:]):
        d = tb - ta + 1.2                                  # overlap = crossfade
        s = pad(notes, d, 0.6 + 0.8 * ss(30, 47, ta))
        env = np.minimum(np.minimum(tl(d) / 1.0, 1), np.clip((d - tl(d)) / 1.2, 0, 1))
        i = int(ta * SR)
        mus[i:i + len(s)] += (s * env)[:n - i]
    swell = np.array([0.55 + 0.45 * ss(3.4, 6.0, x) + 0.5 * ss(36.0, 47.5, x) for x in np.arange(0, T_END, 0.01)])
    mus *= np.interp(t, np.arange(0, T_END, 0.01), swell)
    m = tl(4.6)                                            # alone in the alley: one high, thin chord
    s = pad([74, 77, 81], 4.6, 0.3) * np.minimum(m / 1.2, 1) * np.clip((4.6 - m) / 1.8, 0, 1) * 0.6
    mus[int(52.4 * SR):int(52.4 * SR) + len(s)] += s
    mus = nrm(ff(mus, 60, 2400))
    # pulse: a soft low heartbeat that speeds up towards the yank (37 -> 47.5)
    tb_ = 9.0
    while tb_ < 47.5:
        place(dry, thud(52, 0.4) * (0.5 + 0.5 * ss(30, 47, tb_)), tb_, 0.07 + 0.06 * ss(36, 47, tb_), 0.0)
        tb_ += lerp(1.0, 0.45, ss(36.0, 47.0, tb_))
    duck = np.ones(n)
    for k, t0 in LINES.items():
        a_, b_ = int((t0 - 0.15) * SR), int((t0 + durs.get(k, 1.0) + 0.2) * SR)
        duck[max(a_, 0):min(b_, n)] = 0.5
    duck = np.convolve(duck, np.ones(int(0.12 * SR)) / int(0.12 * SR), 'same')
    mus *= duck
    for ch in range(2):
        dry[ch] += mus * 0.11
        wet[ch] += mus * 0.035

    # ---- voices (placeholders): goblin dry, knight metallic resonance, bellwright short stone reverb
    for k, t0 in LINES.items():
        f = os.path.join(TTS, 'lrs', k + '.wav')
        if not os.path.exists(f):
            print('missing voice', f)
            continue
        y, sr = sf.read(f)
        y = y if y.ndim == 1 else y.mean(1)
        if sr != SR:
            from scipy.signal import resample_poly
            y = resample_poly(y, SR, sr)
        y = y / (np.sqrt(np.mean(y[np.abs(y) > 0.01] ** 2)) + 1e-9) * 0.12
        spk = SPK[k]
        if spk == 'K':
            r = y.copy()
            for dl, g in ((0.0071, 0.35), (0.0113, 0.25), (0.0167, 0.18)):
                d = int(dl * SR)
                r[d:] += y[:-d] * g
            y = r / np.max(np.abs(r)) * np.max(np.abs(y))
        place(dry, y, t0, 1.0, 0.0)
        if spk == 'B' or (15.0 <= t0 < 52.0):
            place(wet, y, t0, 0.35 if spk == 'B' else 0.15, 0.0)

    # ---- reverb: short stone room (bus), alley is narrow -> same IR, less send
    irn = int(1.4 * SR)
    ti = np.arange(irn) / SR
    out = dry.copy()
    i52 = int(52.0 * SR)
    for ch in range(2):
        ir = ff(rng.standard_normal(irn), 150, 5000) * np.exp(-ti / 0.32)
        ir /= np.sqrt(np.sum(ir ** 2))
        L = n + irn
        for part in (0, 1):                                # chamber reverb tail stops dead at the reset
            w = wet[ch].copy()
            if part == 0:
                w[i52:] = 0
            else:
                w[:i52] = 0
            r = np.fft.irfft(np.fft.rfft(w, L) * np.fft.rfft(ir, L), L)[:n] * 0.6
            if part == 0:
                r[i52:] = 0
            out[ch] += r
    # the bell tail is CUT by the reset at 52.0 (hard cycle reset) - nothing to do, the alley starts clean
    # seamless loop: bend the last 20 ms onto the first sample (removes the click of the non-periodic ambience)
    k = int(0.02 * SR)
    ramp = np.linspace(0, 1, k) ** 2
    for ch in range(2):
        out[ch, -k:] += (out[ch, 0] - out[ch, -1]) * ramp
    pk = np.max(np.abs(out))
    out *= 0.84 / pk
    rms = np.sqrt(np.mean(out ** 2))
    print('AUDIO full: rms %.1f dBFS, peak %.1f dBFS' % (20 * np.log10(rms), 20 * np.log10(np.max(np.abs(out)))))
    d = os.path.join(OUT, 'audio')
    os.makedirs(d, exist_ok=True)
    sf.write(os.path.join(d, 'full.wav'), out.T, SR, subtype='PCM_16')
    sf.write(os.path.join(d, 'hook.wav'), out[:, :int(8 * SR)].T, SR, subtype='PCM_16')
    loop = np.concatenate([out[:, int(52 * SR):], out[:, :int(3 * SR)]], 1)
    sf.write(os.path.join(d, 'loop.wav'), loop.T, SR, subtype='PCM_16')
    b = int(6 * SR)                                        # boundary inside loop.wav
    jump = np.abs(loop[:, b] - loop[:, b - 1]).max()
    print('loop boundary sample jump %.4f (typical neighbour %.4f)' % (jump, np.abs(np.diff(loop[:, b - 2000:b], axis=1)).mean()))


# ======================================================================================
#  SCENE (bpy)
# ======================================================================================
if MODE != 'audio':
    import bpy, bmesh
    from mathutils import Vector, Euler, Matrix

    def setp(obj, attr, val):
        try:
            setattr(obj, attr, val)
        except Exception as e:
            print('skip', attr, e)

    def link(ob):
        bpy.context.scene.collection.objects.link(ob)
        return ob

    def empty(name, parent=None, loc=(0, 0, 0)):
        e = link(bpy.data.objects.new(name, None))
        e.empty_display_size = 0.1
        e.parent = parent
        e.location = loc
        return e

    # ---------------- materials ----------------
    def new_mat(name):
        m = bpy.data.materials.new(name)
        setp(m, 'use_nodes', True)
        return m, m.node_tree

    def bsdf(nt):
        p = nt.nodes.get('Principled BSDF')
        if p is None:
            p = nt.nodes.new('ShaderNodeBsdfPrincipled')
            nt.links.new(p.outputs[0], nt.nodes['Material Output'].inputs['Surface'])
        return p

    def M(name, col, rough=0.8, metal=0.0, emit=None, estr=0.0):
        m, nt = new_mat(name)
        p = bsdf(nt)
        p.inputs['Base Color'].default_value = (*col, 1)
        p.inputs['Roughness'].default_value = rough
        p.inputs['Metallic'].default_value = metal
        if emit:
            p.inputs['Emission Color'].default_value = (*emit, 1)
            p.inputs['Emission Strength'].default_value = estr
        return m

    def M_emit(name, col, strength):
        m, nt = new_mat(name)
        for nd in list(nt.nodes):
            if nd.type == 'BSDF_PRINCIPLED':
                nt.nodes.remove(nd)
        e = nt.nodes.new('ShaderNodeEmission')
        e.inputs['Color'].default_value = (*col, 1)
        e.inputs['Strength'].default_value = strength
        nt.links.new(e.outputs[0], nt.nodes['Material Output'].inputs['Surface'])
        return m

    def M_noise_mix(name, colA, colB, roughA, roughB, metal=0.0, scale=6.0, thr=(0.45, 0.62), bumpstr=0.0, voronoi=False):
        """two-tone material (oxidised bronze, stone, cobbles); per-object variation from Object Info Random."""
        m, nt = new_mat(name)
        p = bsdf(nt)
        p.inputs['Metallic'].default_value = metal
        tc = nt.nodes.new('ShaderNodeTexCoord')
        noi = nt.nodes.new('ShaderNodeTexNoise')
        noi.inputs['Scale'].default_value = scale
        noi.inputs['Detail'].default_value = 4
        nt.links.new(tc.outputs['Object'], noi.inputs['Vector'])
        mr = nt.nodes.new('ShaderNodeMapRange')
        mr.inputs['From Min'].default_value, mr.inputs['From Max'].default_value = thr
        nt.links.new(noi.outputs['Fac'], mr.inputs['Value'])
        oi = nt.nodes.new('ShaderNodeObjectInfo')
        mix = nt.nodes.new('ShaderNodeMix')
        mix.data_type = 'RGBA'
        nt.links.new(mr.outputs['Result'], mix.inputs['Factor'])
        a = nt.nodes.new('ShaderNodeMix')
        a.data_type = 'RGBA'
        a.inputs['A'].default_value = (*colA, 1)
        a.inputs['B'].default_value = tuple(min(1, c * 1.35) for c in colA) + (1,)
        nt.links.new(oi.outputs['Random'], a.inputs['Factor'])
        nt.links.new(a.outputs['Result'], mix.inputs['A'])
        mix.inputs['B'].default_value = (*colB, 1)
        nt.links.new(mix.outputs['Result'], p.inputs['Base Color'])
        rr = nt.nodes.new('ShaderNodeMapRange')
        rr.inputs['To Min'].default_value, rr.inputs['To Max'].default_value = roughA, roughB
        nt.links.new(mr.outputs['Result'], rr.inputs['Value'])
        nt.links.new(rr.outputs['Result'], p.inputs['Roughness'])
        if bumpstr:
            src = noi
            if voronoi:
                vo = nt.nodes.new('ShaderNodeTexVoronoi')
                vo.feature = 'DISTANCE_TO_EDGE'
                vo.inputs['Scale'].default_value = scale
                nt.links.new(tc.outputs['Object'], vo.inputs['Vector'])
                src = vo
            bp = nt.nodes.new('ShaderNodeBump')
            bp.inputs['Strength'].default_value = bumpstr
            nt.links.new(src.outputs['Distance' if voronoi else 'Fac'], bp.inputs['Height'])
            nt.links.new(bp.outputs['Normal'], p.inputs['Normal'])
        return m

    def M_volume(name, density, color, aniso=0.3):
        m, nt = new_mat(name)
        for nd in list(nt.nodes):
            if nd.type == 'BSDF_PRINCIPLED':
                nt.nodes.remove(nd)
        pv = nt.nodes.new('ShaderNodeVolumePrincipled')
        pv.inputs['Color'].default_value = (*color, 1)
        pv.inputs['Density'].default_value = density
        pv.inputs['Anisotropy'].default_value = aniso
        nt.links.new(pv.outputs[0], nt.nodes['Material Output'].inputs['Volume'])
        return m

    # ---------------- meshes (cached, shared between instances) ----------------
    MESH = {}

    def mk(key, build, mat, smooth=False):
        k = key + '|' + (mat.name if mat else '-')
        if k in MESH:
            return MESH[k]
        bm = bmesh.new()
        build(bm)
        me = bpy.data.meshes.new(key)
        bm.to_mesh(me)
        bm.free()
        if mat:
            me.materials.append(mat)
        if smooth:
            me.polygons.foreach_set('use_smooth', np.ones(len(me.polygons), bool))
        MESH[k] = me
        return me

    def box(w, d, h, top=1.0, topd=1.0):
        def b(bm):
            bmesh.ops.create_cube(bm, size=1.0)
            for v in bm.verts:
                v.co.x *= w * (top if v.co.z > 0 else 1)
                v.co.y *= d * (topd if v.co.z > 0 else 1)
                v.co.z *= h
        return ('box%.3f_%.3f_%.3f_%.2f_%.2f' % (w, d, h, top, topd), b)

    def cyl(r, h, seg=8, r2=None):
        r2 = r if r2 is None else r2
        def b(bm):
            bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r2, depth=h)
        return ('cyl%.3f_%.3f_%.3f_%d' % (r, r2, h, seg), b)

    def sph(r, seg=12, ring=8):
        def b(bm):
            bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=ring, radius=r)
        return ('sph%.3f_%d_%d' % (r, seg, ring), b)

    def lathe(name, prof, seg=24):
        def b(bm):
            rings = []
            for r, z in prof:
                rings.append([bm.verts.new((r * math.cos(2 * math.pi * i / seg), r * math.sin(2 * math.pi * i / seg), z))
                              for i in range(seg)])
            for a, c in zip(rings[:-1], rings[1:]):
                for i in range(seg):
                    bm.faces.new((a[i], a[(i + 1) % seg], c[(i + 1) % seg], c[i]))
            bm.faces.new(rings[0][::-1])
        return (name, b)

    def gear(r, teeth, th, hole=0.0):
        def b(bm):
            pts = []
            for i in range(teeth * 4):
                a = 2 * math.pi * i / (teeth * 4)
                rr = r * (1.0 if (i % 4) in (0, 1) else 0.86)
                pts.append((rr * math.cos(a), rr * math.sin(a)))
            top = [bm.verts.new((x, y, th / 2)) for x, y in pts]
            bot = [bm.verts.new((x, y, -th / 2)) for x, y in pts]
            bm.faces.new(top)
            bm.faces.new(bot[::-1])
            N = len(pts)
            for i in range(N):
                bm.faces.new((bot[i], bot[(i + 1) % N], top[(i + 1) % N], top[i]))
        return ('gear%.2f_%d_%.2f' % (r, teeth, th), b)

    def obj(name, geo, mat, parent=None, loc=(0, 0, 0), rot=(0, 0, 0), scl=(1, 1, 1), smooth=False):
        key, b = geo
        ob = link(bpy.data.objects.new(name, mk(key, b, mat, smooth)))
        ob.parent = parent
        ob.location = loc
        ob.rotation_euler = rot
        ob.scale = scl
        return ob

    def poly_obj(name, verts, faces, mat, parent=None, loc=(0, 0, 0)):
        me = bpy.data.meshes.new(name)
        me.from_pydata(verts, [], faces)
        me.materials.append(mat)
        ob = link(bpy.data.objects.new(name, me))
        ob.parent = parent
        ob.location = loc
        return ob

    # ======================================================================================
    #  PUPPETS
    # ======================================================================================
    class Puppet:
        def __init__(self, name):
            self.name = name
            self.root = empty(name)
            self.j = {}
            self.rest = {}
            self.parts = []
            self.vis = True

        def joint(self, name, parent, loc):
            e = empty(self.name + '_' + name, self.j.get(parent, self.root) if isinstance(parent, str) else parent, loc)
            self.j[name] = e
            self.rest[name] = Vector(loc)
            return e

        def part(self, name, geo, mat, joint, loc=(0, 0, 0), rot=(0, 0, 0), scl=(1, 1, 1), smooth=False):
            ob = obj(self.name + '_' + name, geo, mat, self.j[joint] if isinstance(joint, str) else joint, loc, rot, scl, smooth)
            if geo[0].startswith('box') and not smooth:
                bv = ob.modifiers.new('bevel', 'BEVEL')
                bv.width = 0.012
                bv.segments = 1
                setp(bv, 'limit_method', 'ANGLE')
            self.parts.append(ob)
            return ob

        def pose(self, loc, rotz, rots, hips_dz=0.0, scale=1.0, lean=(0.0, 0.0)):
            self.root.location = loc
            self.root.rotation_euler = (lean[0], lean[1], rotz)
            self.root.scale = (scale, scale, scale)
            for n, e in self.j.items():
                e.rotation_euler = rots.get(n, (0, 0, 0))
            self.j['hips'].location = self.rest['hips'] + Vector((0, 0, hips_dz))

        def show(self, v):
            if v != self.vis:
                for p in self.parts:
                    p.hide_render = not v
                    p.hide_viewport = not v
                self.vis = v

    def run_pose(ph, a, arm_bend=1.2, lean=0.22):
        """joint rotations for a run / fast-walk cycle; a = 0 (stand) .. 1 (full run)."""
        r = {}
        for side, o in (('L', 0.0), ('R', math.pi)):
            p = ph + o
            r['thigh_' + side] = (a * 0.8 * math.sin(p), 0, 0)
            r['knee_' + side] = (-a * (0.15 + 1.15 * max(0.0, math.cos(p))), 0, 0)
            r['shoulder_' + side] = (-a * 0.75 * math.sin(p), 0, (0.08 if side == 'L' else -0.08) * a)
            r['elbow_' + side] = (a * arm_bend + 0.15, 0, 0)
        r['hips'] = (0, 0, a * 0.12 * math.sin(ph))
        r['torso'] = (-a * lean, 0, -a * 0.14 * math.sin(ph))
        r['head'] = (a * lean * 0.7, 0, 0)
        return r

    def blend(A, B, w):
        out = dict(A)
        for k, v in B.items():
            a = A.get(k, (0, 0, 0))
            out[k] = tuple(a[i] + (v[i] - a[i]) * w for i in range(3))
        return out

    def add(A, B, w=1.0):
        out = dict(A)
        for k, v in B.items():
            a = A.get(k, (0, 0, 0))
            out[k] = tuple(a[i] + v[i] * w for i in range(3))
        return out

    def build_knight(name, mats, shell=False):
        bz, bzd, cloth, void, cyan, cyan_dim, steel = mats
        P = Puppet(name)
        P.joint('hips', P.root, (0, 0, 1.0))
        P.joint('torso', 'hips', (0, 0, 0.1))
        P.joint('head', 'torso', (0, 0, 0.62))
        for s, sx in (('L', -1), ('R', 1)):
            P.joint('shoulder_' + s, 'torso', (0.33 * sx, 0, 0.5))
            P.joint('elbow_' + s, 'shoulder_' + s, (0, 0, -0.33))
            P.joint('thigh_' + s, 'hips', (0.13 * sx, 0, -0.06))
            P.joint('knee_' + s, 'thigh_' + s, (0, 0, -0.46))
        P.joint('plate', 'torso', (-0.25, 0.12, 0.28))
        P.joint('cape', 'torso', (0, -0.17, 0.55))
        P.joint('cape2', 'cape', (0, 0, -0.55))
        P.part('pelvis', box(0.4, 0.26, 0.2), bz, 'hips', (0, 0, -0.02))
        P.part('fauld', box(0.48, 0.32, 0.14, 0.9, 0.9), bzd, 'hips', (0, 0, -0.15))
        P.part('chest', box(0.42, 0.26, 0.54, 1.32, 1.1), bz, 'torso', (0, -0.04, 0.29))
        P.part('cavity', box(0.34, 0.02, 0.42), void, 'torso', (0, 0.092, 0.3))
        sp = P.part('spark', sph(0.045, 8, 6), cyan, 'torso', (0, 0.11, 0.33))
        P.spark = sp
        P.part('breastplate', box(0.5, 0.07, 0.5, 1.12, 1.0), bz, 'plate', (0.25, 0.0, 0.0))
        P.emblem = P.part('emblem', cyl(0.06, 0.02, 4), cyan_dim if not shell else void, 'plate', (0.25, 0.04, 0.09),
                          (math.radians(90), 0, 0), (0.8, 1.3, 1))
        P.part('gorget', cyl(0.15, 0.12, 8), bzd, 'torso', (0, 0, 0.6))
        P.part('helm', box(0.3, 0.32, 0.36, 0.86, 0.9), bzd, 'head', (0, 0, 0.18))
        P.part('visor', box(0.24, 0.02, 0.04), cyan_dim if not shell else void, 'head', (0, 0.165, 0.2))
        P.part('visor2', box(0.035, 0.02, 0.13), void, 'head', (0, 0.165, 0.12))
        P.part('crest', box(0.04, 0.3, 0.09), bzd, 'head', (0, -0.01, 0.38))
        P.part('pauld_L', sph(0.2, 8, 5), bz, 'shoulder_L', (-0.04, 0, 0.03), (0, 0.25, 0), (1.05, 1.0, 0.72))
        P.part('pauld_L2', sph(0.17, 8, 5), bzd, 'shoulder_L', (-0.08, 0, -0.04), (0, 0.4, 0), (1.0, 0.95, 0.6))
        P.part('pauld_R', sph(0.15, 8, 5), bz, 'shoulder_R', (0.03, 0, 0.02), (0, -0.2, 0), (1.0, 1.0, 0.7))
        for s in ('L', 'R'):
            P.part('arm_' + s, box(0.12, 0.13, 0.3), bzd, 'shoulder_' + s, (0, 0, -0.16))
            P.part('fore_' + s, box(0.12, 0.12, 0.26, 1.15, 1.1), bz, 'elbow_' + s, (0, 0, -0.13))
            P.part('glove_' + s, box(0.13, 0.15, 0.12), bzd, 'elbow_' + s, (0, 0.01, -0.31))
            P.part('thighp_' + s, box(0.17, 0.19, 0.42, 1.1, 1.05), bz, 'thigh_' + s, (0, 0, -0.22))
            P.part('kneec_' + s, sph(0.08, 6, 4), bzd, 'knee_' + s, (0, 0.07, 0))
            P.part('shin_' + s, box(0.15, 0.17, 0.4), bz, 'knee_' + s, (0, 0, -0.2))
            P.part('boot_' + s, box(0.17, 0.3, 0.12), bzd, 'knee_' + s, (0, 0.06, -0.43))
        if not shell:
            V = [(-0.32, 0, 0), (0.32, 0, 0), (0.36, -0.04, -0.56), (-0.36, -0.04, -0.56)]
            P.part_cape1 = poly_obj(name + '_cape1', V, [(0, 1, 2, 3)], cloth, P.j['cape'])
            V2 = [(-0.36, -0.04, 0), (0.36, -0.04, 0), (0.30, -0.02, -0.5), (0.18, -0.03, -0.38), (0.06, -0.02, -0.58),
                  (-0.1, -0.03, -0.42), (-0.22, -0.02, -0.6), (-0.38, -0.03, -0.45)]
            P.part_cape2 = poly_obj(name + '_cape2', V2, [tuple(range(8))], cloth, P.j['cape2'])
            P.parts += [P.part_cape1, P.part_cape2]
            P.sheath = P.part('sheath', box(0.06, 0.09, 0.82), void, 'hips', (-0.27, -0.06, -0.32), (0.18, 0, 0))
            P.hilt = P.part('hilt', box(0.2, 0.04, 0.04), steel, 'hips', (-0.27, -0.0, 0.1), (0.18, 0, 0))
            P.sword = P.part('sword', box(0.05, 0.02, 0.95), steel, 'elbow_R', (0, 0.05, -0.75))
            P.sword_x = P.part('swordx', box(0.2, 0.04, 0.04), bzd, 'elbow_R', (0, 0.05, -0.28))
        return P

    def build_goblin(mats):
        skin, leather, red, eyew, black, mouthm = mats
        P = Puppet('goblin')
        P.joint('hips', P.root, (0, 0, 0.5))
        P.joint('torso', 'hips', (0, 0, 0.05))
        P.joint('head', 'torso', (0, 0, 0.4))
        for s, sx in (('L', -1), ('R', 1)):
            P.joint('shoulder_' + s, 'torso', (0.19 * sx, 0, 0.31))
            P.joint('elbow_' + s, 'shoulder_' + s, (0, 0, -0.2))
            P.joint('thigh_' + s, 'hips', (0.09 * sx, 0, -0.03))
            P.joint('knee_' + s, 'thigh_' + s, (0, 0, -0.22))
        P.joint('scarf', 'torso', (0.05, -0.12, 0.34))
        P.part('belly', sph(0.2, 12, 8), skin, 'torso', (0, 0, 0.16), scl=(1.0, 0.85, 1.2), smooth=True)
        P.part('apron', box(0.3, 0.03, 0.34, 0.8), leather, 'torso', (0, 0.165, 0.1))
        P.part('neckscarf', cyl(0.14, 0.09, 10), red, 'torso', (0, 0, 0.34))
        P.part('scarftail', box(0.08, 0.02, 0.3), red, 'scarf', (0, 0, -0.14))
        P.part('headb', sph(0.19, 14, 10), skin, 'head', (0, 0.02, 0.15), scl=(1.05, 0.95, 0.92), smooth=True)
        for s, sx in (('L', -1), ('R', 1)):
            P.part('ear_' + s, cyl(0.09, 0.36, 4, 0.0), skin, 'head', (0.29 * sx, -0.02, 0.21),
                   (0, math.radians(72) * sx, 0), (1.0, 0.32, 1.0))
            P.part('eye_' + s, sph(0.058, 10, 6), eyew, 'head', (0.075 * sx, 0.15, 0.18), scl=(1, 0.6, 1.1))
        P.eyes = [o for o in P.parts if '_eye_' in o.name]
        P.pupils = [P.part('pupil_' + s, sph(0.027, 8, 5), black, 'head', (0.075 * sx, 0.188, 0.175))
                    for s, sx in (('L', -1), ('R', 1))]
        P.brows = [P.part('brow_' + s, box(0.09, 0.025, 0.022), black, 'head', (0.075 * sx, 0.17, 0.255))
                   for s, sx in (('L', -1), ('R', 1))]
        P.mouth = P.part('mouth', sph(0.06, 10, 6), mouthm, 'head', (0, 0.17, 0.05), scl=(1.2, 0.4, 0.3))
        P.part('nose', cyl(0.035, 0.1, 5, 0.0), skin, 'head', (0, 0.2, 0.12), (math.radians(-80), 0, 0))
        for s in ('L', 'R'):
            P.part('arm_' + s, cyl(0.045, 0.21, 6), skin, 'shoulder_' + s, (0, 0, -0.1))
            P.part('fore_' + s, cyl(0.042, 0.2, 6), skin, 'elbow_' + s, (0, 0, -0.1))
            P.part('hand_' + s, sph(0.06, 8, 5), skin, 'elbow_' + s, (0, 0, -0.22))
            P.part('leg_' + s, cyl(0.06, 0.22, 6), leather, 'thigh_' + s, (0, 0, -0.11))
            P.part('shin_' + s, cyl(0.05, 0.22, 6), skin, 'knee_' + s, (0, 0, -0.11))
            P.part('foot_' + s, box(0.11, 0.22, 0.07), leather, 'knee_' + s, (0, 0.05, -0.245))
        return P

    FACES = {  # pupil scale, brow z, brow tilt (inner up +), mouth open, eye scale z
        'neutral': (1.0, 0.0, 0.0, 0.15, 1.0),
        'run': (0.9, -0.005, -0.25, 0.35, 0.95),
        'pain': (1.0, -0.015, -0.45, 0.6, 0.35),
        'shock': (0.6, 0.03, 0.2, 0.9, 1.25),
        'terror': (0.5, 0.035, 0.5, 1.0, 1.3),
        'sad': (1.0, 0.01, 0.55, 0.12, 0.85),
        'plead': (0.8, 0.02, 0.6, 0.7, 1.1),
    }

    def set_face(G, name, talk=0.0, name2=None, w=0.0):
        f = FACES[name]
        if name2:
            f = tuple(lerp(a, b, w) for a, b in zip(f, FACES[name2]))
        ps, bz, bt, mo, ez = f
        for p in G.pupils:
            p.scale = (ps, ps, ps)
        for e in G.eyes:
            e.scale = (1, 0.6, 1.1 * ez)
        for b, sx in zip(G.brows, (-1, 1)):
            b.location = (0.075 * sx, 0.17, 0.255 + bz)
            b.rotation_euler = (0, bt * sx, 0)
        mo = min(1.0, mo + talk)
        G.mouth.scale = (1.2 - 0.3 * mo, 0.4, 0.25 + 0.9 * mo)

    def build_bellwright(mats):
        coat, brass, leather, lamp, void = mats
        P = Puppet('bellwright')
        P.joint('hips', P.root, (0, 0, 0.62))
        P.joint('torso', 'hips', (0, 0, 0.05))
        P.joint('head', 'torso', (0, 0, 0.62))
        for s, sx in (('L', -1), ('R', 1)):
            P.joint('shoulder_' + s, 'torso', (0.33 * sx, 0, 0.5))
            P.joint('elbow_' + s, 'shoulder_' + s, (0, 0, -0.3))
            P.joint('thigh_' + s, 'hips', (0.15 * sx, 0, -0.05))
            P.joint('knee_' + s, 'thigh_' + s, (0, 0, -0.28))
        P.part('body', cyl(0.34, 0.72, 10, 0.28), coat, 'torso', (0, 0, 0.28))
        P.part('belt', cyl(0.36, 0.08, 10), leather, 'torso', (0, 0, 0.05))
        P.part('head', sph(0.17, 10, 6), void, 'head', (0, 0, 0.12))
        P.part('mask', cyl(0.15, 0.04, 10), brass, 'head', (0, 0.15, 0.12), (math.radians(90), 0, 0))
        for sx in (-1, 1):
            P.part('maskeye%d' % sx, box(0.05, 0.02, 0.02), void, 'head', (0.055 * sx, 0.172, 0.15))
        P.part('cap', lathe('bellcap', [(0.36, 0), (0.3, 0.04), (0.2, 0.1), (0.16, 0.22), (0.1, 0.3), (0.0, 0.32)], 16),
               brass, 'head', (0, 0, 0.2))
        P.part('knob', sph(0.04, 6, 4), brass, 'head', (0, 0, 0.55))
        for s in ('L', 'R'):
            P.part('arm_' + s, cyl(0.08, 0.3, 8), coat, 'shoulder_' + s, (0, 0, -0.15))
            P.part('fore_' + s, cyl(0.075, 0.26, 8), coat, 'elbow_' + s, (0, 0, -0.12))
            P.part('glove_' + s, sph(0.11, 8, 5), leather, 'elbow_' + s, (0, 0, -0.3))
            P.part('leg_' + s, box(0.16, 0.18, 0.3), leather, 'thigh_' + s, (0, 0, -0.14))
            P.part('boot_' + s, box(0.18, 0.28, 0.14), leather, 'knee_' + s, (0, 0.05, -0.26))
        P.lantern = P.part('lantern', box(0.14, 0.14, 0.2), lamp, 'elbow_L', (0, 0.0, -0.5))
        P.part('lanterncap', box(0.18, 0.18, 0.04), brass, 'elbow_L', (0, 0, -0.39))
        return P

    # ======================================================================================
    #  BUILD
    # ======================================================================================
    R = {}

    def build():
        sc = bpy.context.scene
        for ob in list(bpy.data.objects):
            bpy.data.objects.remove(ob)
        sc.frame_start, sc.frame_end = 1, NF
        sc.render.fps = FPS
        sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
        rng = np.random.default_rng(5)

        # ---------- materials ----------
        bronze = M_noise_mix('bronze', (0.30, 0.18, 0.08), (0.12, 0.22, 0.19), 0.62, 0.82, metal=0.8, scale=3, thr=(0.58, 0.72))
        bronze_d = M_noise_mix('bronze_dark', (0.17, 0.11, 0.06), (0.1, 0.18, 0.16), 0.65, 0.85, metal=0.75, scale=3, thr=(0.52, 0.68))
        shell_b = M_noise_mix('shell', (0.17, 0.14, 0.11), (0.12, 0.17, 0.16), 0.55, 0.85, metal=0.7, scale=5, thr=(0.4, 0.55))
        shell_d = M_noise_mix('shell_d', (0.11, 0.1, 0.09), (0.09, 0.12, 0.11), 0.6, 0.9, metal=0.6, scale=5)
        cloth = M('cape', (0.07, 0.065, 0.07), 0.95)
        void = M_emit('void', (0, 0, 0), 0.0)
        cyan = M_emit('soul', (0.08, 0.8, 1.0), 6.0)
        cyan_dim = M_emit('soul_dim', (0.08, 0.8, 1.0), 2.0)
        soul_k = M_emit('soul_k', (0.08, 0.8, 1.0), 2.0)
        steel = M('steel', (0.55, 0.57, 0.6), 0.3, 0.9)
        skin = M('goblin', (0.16, 0.40, 0.09), 0.55)
        leather = M('leather', (0.2, 0.11, 0.05), 0.8)
        red = M('scarf', (0.62, 0.025, 0.02), 0.7)
        eyew = M('eyewhite', (0.95, 0.92, 0.78), 0.3, emit=(1, 0.95, 0.8), estr=0.25)
        black = M('black', (0.005, 0.005, 0.005), 0.4)
        mouthm = M('mouth', (0.08, 0.01, 0.01), 0.6)
        coat = M('coat', (0.12, 0.08, 0.06), 0.9)
        brass = M('brass', (0.6, 0.42, 0.15), 0.35, 0.9)
        lamp = M_emit('lamp', (1.0, 0.55, 0.2), 18.0)
        stone = M_noise_mix('stone', (0.13, 0.12, 0.115), (0.08, 0.085, 0.09), 0.85, 0.95, scale=1.2, thr=(0.4, 0.7), bumpstr=0.3)
        cobble = M_noise_mix('cobble', (0.09, 0.085, 0.08), (0.05, 0.055, 0.06), 0.45, 0.8, scale=2.2, thr=(0.35, 0.7),
                             bumpstr=0.6, voronoi=True)
        wood = M('wood', (0.08, 0.05, 0.03), 0.85)
        window = M_emit('window', (1.0, 0.5, 0.18), 6.0)
        window_d = M('window_dark', (0.02, 0.025, 0.03), 0.3)
        iron = M('iron', (0.06, 0.06, 0.065), 0.6, 0.8)
        fletch = M('fletch', (0.95, 0.9, 0.8), 0.6, emit=(1, 0.95, 0.85), estr=1.5)
        trail = M_emit('trail', (1.0, 0.95, 0.85), 3.0)
        archer_m = M('archer', (0.01, 0.012, 0.015), 0.9)
        R['mats'] = dict(cyan=cyan, cyan_dim=cyan_dim, soul_k=soul_k)

        # ---------- world ----------
        w = bpy.data.worlds.new('cavern')
        sc.world = w
        setp(w, 'use_nodes', True)
        w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.006, 0.012, 0.018, 1)
        w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0

        # ---------- ALLEY (along +Y, walls at x = +-3) ----------
        obj('floor', box(7.0, 110, 0.2), cobble, loc=(0, 4, -0.1))
        lamps = []
        for s in (-1, 1):
            y = -44.0
            i = 0
            while y < 42:
                L = 4.0
                h = float(rng.uniform(6.5, 10.5))
                if s < 0 and 10.0 <= y < 14.0:     # side arch where the shells come in (left wall)
                    obj('arch_top', box(0.9, 4.0, h - 4.2), stone, loc=(s * 3.45, y + 2, 4.2 + (h - 4.2) / 2))
                    obj('arch_dark', box(0.3, 3.2, 4.2), void, loc=(s * 3.85, y + 2, 2.1))
                    y += L
                    continue
                obj('wall', box(0.9, L + 0.02, h), stone, loc=(s * 3.45, y + L / 2, h / 2))
                obj('ledge', box(1.1, L + 0.04, 0.2), stone, loc=(s * 3.4, y + L / 2, h))
                if rng.random() < 0.45:
                    obj('door', box(0.1, 1.3, 2.3), void, loc=(s * 2.99, y + L / 2 + rng.uniform(-0.8, 0.8), 1.15))
                for wz in (3.6, 6.2):
                    if wz < h - 1.0 and rng.random() < 0.8:
                        lit = rng.random() < 0.4
                        obj('win', box(0.06, 0.6, 0.9), window if lit else window_d,
                            loc=(s * 2.99, y + L / 2 + rng.uniform(-1.0, 1.0), wz))
                if rng.random() < 0.3:
                    by = y + L / 2
                    obj('balcony', box(1.0, 2.2, 0.12), wood, loc=(s * 2.55, by, 3.0))
                    obj('rail', box(0.05, 2.2, 0.5), iron, loc=(s * 2.08, by, 3.3))
                if rng.random() < 0.35:
                    obj('pipe', cyl(0.07, h, 6), iron, loc=(s * 2.93, y + rng.uniform(0.3, 3.7), h / 2))
                if rng.random() < 0.25:
                    sy = y + L / 2
                    obj('bracket', box(0.9, 0.05, 0.05), iron, loc=(s * 2.55, sy, 4.4))
                    obj('sign', box(0.05, 0.6, 0.45), wood, loc=(s * 2.3, sy, 4.05))
                if i % 2 == (0 if s < 0 else 1):
                    ly = y + 1.0
                    obj('lantern', box(0.2, 0.2, 0.3), lamp, loc=(s * 2.75, ly, 3.3))
                    obj('lanterncap', box(0.26, 0.26, 0.05), iron, loc=(s * 2.75, ly, 3.48))
                    ld = bpy.data.lights.new('lamp', 'POINT')
                    ld.color = (1.0, 0.55, 0.25)
                    ld.energy = 90
                    setp(ld, 'shadow_soft_size', 0.15)
                    setp(ld, 'use_shadow', False)       # 40 lamps: shadows only from the character lights
                    lo = link(bpy.data.objects.new('lamp', ld))
                    lo.location = (s * 2.5, ly, 3.2)
                    lamps.append((ld, float(rng.uniform(0, 100))))
                y += L
                i += 1
        # cables across the alley (sagging)
        for cy in (-20, -6, 7, 19, 31):
            z0 = float(rng.uniform(5.6, 7.0))
            pts = [(x, cy, z0 - 0.5 * (1 - (x / 3.0) ** 2)) for x in np.linspace(-3, 3, 9)]
            for a, b in zip(pts[:-1], pts[1:]):
                d = Vector(b) - Vector(a)
                ob = obj('cable', cyl(0.02, 1.0, 4), iron, loc=tuple((Vector(a) + Vector(b)) / 2))
                ob.scale = (1, 1, d.length)
                ob.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
        # skyline silhouettes beyond the walls
        sil = M('silhouette', (0.012, 0.016, 0.02), 0.9)
        for k in range(24):
            sx = rng.choice([-1, 1])
            obj('far', box(rng.uniform(3, 7), rng.uniform(3, 7), rng.uniform(12, 26)), sil,
                loc=(sx * rng.uniform(8, 16), rng.uniform(-40, 45), 6))
        # the bridge + the archer (the cycle's hazard)
        obj('bridge', box(6.2, 1.6, 0.5), stone, loc=(0, ARCHER[1], 6.4))
        obj('bridge_arch', box(6.2, 1.2, 0.9, 1.0), stone, loc=(0, ARCHER[1], 5.75))
        ax, ay = ARCHER[0], ARCHER[1]
        obj('archer_body', cyl(0.28, 1.2, 8, 0.16), archer_m, loc=(ax, ay, 7.2))
        obj('archer_hood', sph(0.18, 8, 5), archer_m, loc=(ax, ay, 7.95))
        obj('archer_bow', box(0.04, 0.04, 1.4), archer_m, loc=(ax + 0.25, ay + 0.3, 7.6), rot=(0.3, 0, 0.3))
        R['glint'] = obj('glint', sph(0.06, 6, 4), cyan, loc=(ax + 0.2, ay + 0.4, 7.85))

        # the bell tower at the end of the alley (the bell is visibly still)
        TY = 50.0
        obj('plaza', box(20, 16, 0.2), cobble, loc=(0, TY - 2, -0.1))
        obj('tower', box(8, 8, 13), stone, loc=(0, TY, 6.5))
        for px in (-3.4, 3.4):
            for py in (-3.4, 3.4):
                obj('pillar', box(1.0, 1.0, 7), stone, loc=(px, TY + py, 16.5))
        obj('belfry_floor', box(8.4, 8.4, 0.6), stone, loc=(0, TY, 13.2))
        obj('belfry_roof', box(8.6, 8.6, 0.8), stone, loc=(0, TY, 20.3))
        obj('spire', cyl(5.6, 6.0, 4, 0.0), M('roof', (0.07, 0.09, 0.09), 0.7, 0.5), loc=(0, TY, 23.6),
            rot=(0, 0, math.radians(45)))
        bprof = [(0.25, 0.0), (0.7, -0.2), (1.0, -0.8), (1.15, -1.6), (1.45, -2.3), (1.85, -2.7), (1.75, -2.8), (0.0, -2.8)]
        R['tower_bell'] = obj('tower_bell', lathe('bell_l', bprof, 28), bronze, loc=(0, TY - 1.0, 19.3))
        tl_ = bpy.data.lights.new('belfry', 'POINT')
        tl_.color = (1.0, 0.6, 0.3)
        tl_.energy = 3000
        link(bpy.data.objects.new('belfry', tl_)).location = (0, TY - 4.5, 15.5)
        R['tgear1'] = obj('tgear1', gear(2.2, 14, 0.4), bronze_d, loc=(-2.2, TY - 4.2, 9.0), rot=(math.radians(90), 0, 0))
        R['tgear2'] = obj('tgear2', gear(1.4, 10, 0.4), bronze_d, loc=(1.4, TY - 4.3, 10.6), rot=(math.radians(90), 0, 0))
        R['cweight'] = obj('counterweight', box(0.8, 0.8, 1.2), iron, loc=(3.2, TY - 4.4, 7.0))
        obj('cwchain', cyl(0.04, 5.6, 4), iron, loc=(3.2, TY - 4.4, 10.4))
        # cold blue mist in the alley (volume box, never a world volume)
        fog = obj('mist', box(7.4, 120, 16), M_volume('mist', float(os.environ.get('FOG', 0.008)), (0.4, 0.58, 0.75), 0.35),
                  loc=(0, 6, 7.5))
        setp(fog, 'display_type', 'BOUNDS')
        R['lamps'] = lamps

        # ---------- BELL CHAMBER (coarse blockout for the middle beats) ----------
        cx = Vector(CH)
        obj('ch_floor', cyl(8.5, 0.3, 24), cobble, loc=tuple(cx + Vector((0, 0, -0.15))))
        for k in range(22):
            a = 2 * math.pi * k / 22
            if abs(math.sin(a) + 1) < 0.08:          # gap = the entrance on -Y
                continue
            ob = obj('ch_wall', box(2.5, 0.8, 14), stone, loc=tuple(cx + Vector((8 * math.cos(a), 8 * math.sin(a), 7))),
                     rot=(0, 0, a + math.pi / 2))
        obj('ch_entr', box(3.0, 0.8, 9), stone, loc=tuple(cx + Vector((0, -8, 9.5))))
        R['ch_bell_pivot'] = bp_ = empty('ch_bell_pivot', None, tuple(cx + Vector((0, 1.5, 11.0))))
        bigp = [(r * 1.5, z * 1.5) for r, z in bprof]
        obj('ch_bell', lathe('bell_big', bigp, 32), bronze, parent=bp_, loc=(0, 0, -0.3))
        obj('ch_yoke', box(4.0, 0.6, 0.6), wood, loc=tuple(cx + Vector((0, 1.5, 11.2))))
        R['ch_g1'] = obj('ch_gear1', gear(2.6, 16, 0.4), bronze_d, loc=tuple(cx + Vector((-4.5, 5.6, 5.0))), rot=(math.radians(90), 0, 0.5))
        R['ch_g2'] = obj('ch_gear2', gear(1.6, 12, 0.4), bronze_d, loc=tuple(cx + Vector((3.8, 5.8, 3.2))), rot=(math.radians(90), 0, -0.4))
        R['ch_core'] = obj('ch_core', gear(1.1, 12, 0.35), bronze, loc=tuple(cx + Vector((0, 3.0, 3.3))), rot=(math.radians(90), 0, 0))
        obj('ch_core_emblem', cyl(0.3, 0.06, 4), cyan_dim, loc=tuple(cx + Vector((0, 2.78, 3.3))),
            rot=(math.radians(90), 0, 0), scl=(0.8, 1.3, 1))
        R['ch_panel'] = obj('ch_panel', box(1.9, 0.1, 1.85), iron, loc=tuple(cx + Vector((0, 2.6, 1.6))))
        R['ch_ring'] = ring = empty('ch_ring', None, tuple(cx + Vector((0, 2.9, 1.6))))
        ring.rotation_euler = (math.radians(90), 0, 0)
        for k in range(12):
            a = 2 * math.pi * k / 12
            obj('ch_sparkslot', sph(0.06, 6, 4), cyan if k else void, parent=ring, loc=(0.75 * math.cos(a), 0.75 * math.sin(a), 0))
        R['ch_crank'] = obj('ch_crank', box(0.08, 0.08, 1.0), iron, loc=tuple(cx + Vector((0.9, 2.55, 1.4))), rot=(0.3, 0, 0))
        R['ch_chain'] = obj('ch_chain', cyl(0.05, 9.0, 4), iron, loc=tuple(cx + Vector((1.6, 1.8, 6.4))))
        R['ch_handle'] = obj('ch_handle', box(0.3, 0.06, 0.12), iron, loc=tuple(cx + Vector((1.6, 1.8, 1.85))))
        R['ch_slip'] = obj('ch_slip', gear(1.0, 12, 0.3), bronze_d, loc=tuple(cx + Vector((-2.4, -0.2, 1.6))))
        obj('ch_slip_axle', cyl(0.12, 1.2, 8), iron, loc=tuple(cx + Vector((-2.4, -0.7, 1.6))), rot=(math.radians(90), 0, 0))
        R['lash'] = lp = empty('lash', None, tuple(cx + Vector((-2.2, -0.8, 9.5))))
        obj('lash_chain', cyl(0.04, 3.6, 4), iron, parent=lp, loc=(0, 0, -1.8))
        obj('lash_end', box(0.14, 0.14, 0.2), iron, parent=lp, loc=(0, 0, -3.65))
        R['hook'] = hk = empty('hook', None, tuple(cx + Vector((-0.7, -2.6, 7.5))))
        obj('hook_bar', box(0.08, 0.08, 0.6), iron, parent=hk, loc=(0, 0, 0.1))
        obj('hook_curve', box(0.3, 0.08, 0.08), iron, parent=hk, loc=(0.11, 0, -0.2))
        R['soul'] = [obj('soulbit%d' % k, sph(0.05, 8, 5), cyan) for k in range(14)]
        hd = bpy.data.lights.new('furnace', 'POINT')
        hd.color = (1.0, 0.45, 0.15)
        hd.energy = 2500
        link(bpy.data.objects.new('furnace', hd)).location = tuple(cx + Vector((5.0, -2.0, 2.0)))
        cd_ = bpy.data.lights.new('ch_cold', 'POINT')
        cd_.color = (0.45, 0.7, 1.0)
        cd_.energy = 1200
        link(bpy.data.objects.new('ch_cold', cd_)).location = tuple(cx + Vector((-4.0, -3.0, 6.0)))
        R['beam'] = obj('beam', cyl(0.025, 1.0, 8), cyan)
        R['beam'].hide_render = True
        R['soul_light'] = sl = bpy.data.lights.new('soul_light', 'POINT')
        sl.color = (0.4, 0.9, 1.0)
        R['soul_light_o'] = link(bpy.data.objects.new('soul_light', sl))
        chm = M_volume('ch_mist', 0.006, (0.5, 0.6, 0.75), 0.3)
        ob = obj('ch_mist', cyl(8.4, 13, 16), chm, loc=tuple(cx + Vector((0, 0, 6.5))))
        setp(ob, 'display_type', 'BOUNDS')

        # ---------- characters ----------
        R['K'] = build_knight('knight', (bronze, bronze_d, cloth, void, cyan, soul_k, steel))
        R['G'] = build_goblin((skin, leather, red, eyew, black, mouthm))
        R['B'] = build_bellwright((coat, brass, leather, lamp, void))
        R['S'] = [build_knight('shell%d' % i, (shell_b, shell_d, cloth, void, cyan, void, steel), shell=True) for i in range(5)]

        # arrow: flying + stuck copy
        def arrow(name, parent=None):
            a = empty(name, parent)
            obj(name + '_shaft', cyl(0.016, 1.0, 6), wood, parent=a, loc=(0, 0, -0.5))
            obj(name + '_head', cyl(0.045, 0.14, 4, 0.0), steel, parent=a, loc=(0, 0, 0.06))
            for k in range(3):
                obj(name + '_fl%d' % k, box(0.005, 0.07, 0.2), fletch, parent=a, loc=(0, 0, -0.9),
                    rot=(0, 0, 2 * math.pi * k / 3))
            return a
        R['arrow'] = arrow('arrow')
        R['arrow'].scale = (2.0, 2.0, 2.0)             # stylised: big enough to read on a phone
        R['arrow_trail'] = obj('arrow_trail', cyl(0.012, 1.6, 6, 0.0), trail, parent=R['arrow'], loc=(0, 0, -1.8),
                               rot=(math.pi, 0, 0))
        R['arrow_stuck'] = arrow('arrow_stuck', R['G'].j['torso'])
        R['flash'] = obj('flash', sph(1.0, 16, 10), M_emit('flash', (0.45, 0.95, 1.0), 6.0), smooth=True)
        R['flash_l'] = fl = bpy.data.lights.new('flash_l', 'POINT')
        fl.color = (0.4, 0.9, 1.0)
        R['flash_lo'] = link(bpy.data.objects.new('flash_l', fl))
        R['column'] = obj('column', cyl(0.06, 6.0, 10), M_emit('column', (0.1, 0.75, 1.0), 1.0))

        # ---------- character lights that follow the action ----------
        def area(name, col, energy, size):
            ld = bpy.data.lights.new(name, 'AREA')
            ld.color = col
            ld.energy = energy
            ld.size = size
            return link(bpy.data.objects.new(name, ld))
        R['key'] = area('key', (1.0, 0.66, 0.4), 380, 3.0)
        R['rim'] = area('rim', (0.4, 0.7, 1.0), 700, 2.0)
        R['fill'] = area('fill', (0.45, 0.6, 0.8), 35, 4.0)

        # ---------- camera + HUD + subtitles (camera-parented text) ----------
        cd = bpy.data.cameras.new('cam')
        cd.lens = 35
        setp(cd, 'sensor_fit', 'AUTO')
        cd.sensor_width = 36
        cd.clip_start = 0.05
        cd.clip_end = 400
        cam = link(bpy.data.objects.new('cam', cd))
        sc.camera = cam
        R['cam'] = cam

        def font(p):
            return bpy.data.fonts.load(p) if os.path.exists(p) else None
        f_sub = font('C:/Windows/Fonts/bahnschrift.ttf')
        f_hud = font('C:/Windows/Fonts/consolab.ttf')
        white = M_emit('sub_white', (1, 1, 1), 1.0)
        m_cy = M_emit('sub_cyan', (0.35, 0.95, 1.0), 1.4)
        m_am = M_emit('sub_amber', (1.0, 0.62, 0.18), 1.4)
        m_red = M_emit('hud_red', (1.0, 0.12, 0.08), 1.6)
        shade = M_emit('sub_shadow', (0, 0, 0), 0.0)
        D = 0.5                                   # text plane distance in front of the lens

        def text(name, size, loc, mats, fnt, align='CENTER'):
            cu = bpy.data.curves.new(name, 'FONT')
            cu.size = size
            cu.align_x = align
            cu.align_y = 'CENTER'
            if fnt:
                cu.font = fnt
            for m in mats:
                cu.materials.append(m)
            ob = link(bpy.data.objects.new(name, cu))
            ob.parent = cam
            ob.location = loc
            return ob
        wm, wnt = new_mat('wash')
        for nd in list(wnt.nodes):
            if nd.type == 'BSDF_PRINCIPLED':
                wnt.nodes.remove(nd)
        tr = wnt.nodes.new('ShaderNodeBsdfTransparent')
        em = wnt.nodes.new('ShaderNodeEmission')
        em.inputs['Color'].default_value = (0.55, 0.95, 1.0, 1)
        em.inputs['Strength'].default_value = 2.5
        mx = wnt.nodes.new('ShaderNodeMixShader')
        wnt.links.new(tr.outputs[0], mx.inputs[1])
        wnt.links.new(em.outputs[0], mx.inputs[2])
        wnt.links.new(mx.outputs[0], wnt.nodes['Material Output'].inputs['Surface'])
        setp(wm, 'surface_render_method', 'BLENDED')
        R['wash_fac'] = mx.inputs[0]
        R['wash'] = obj('wash', box(0.4, 0.4, 0.001), wm, parent=cam, loc=(0, 0, -0.1))
        R['wash'].hide_render = True
        R['sub'] = text('sub', 0.0165, (0, -0.128, -D), [white, m_cy, m_am], f_sub)
        R['sub_sh'] = text('sub_sh', 0.0165, (0.0008, -0.1288, -D - 0.001), [shade], f_sub)
        R['hud'] = text('hud', 0.0125, (-0.098, 0.218, -D), [m_am], f_hud, 'LEFT')
        R['hud_sh'] = text('hud_sh', 0.0125, (-0.0975, 0.2175, -D - 0.001), [shade], f_hud, 'LEFT')
        R['hud_n'] = text('hud_n', 0.026, (-0.012, 0.218, -D), [m_am, m_red], f_hud, 'LEFT')
        R['hud_n_sh'] = text('hud_n_sh', 0.026, (-0.0112, 0.2172, -D - 0.001), [shade], f_hud, 'LEFT')
        R['hud_r'] = text('hud_r', 0.0135, (0, 0.218, -D), [m_cy], f_hud)
        R['hud_r_sh'] = text('hud_r_sh', 0.0135, (0.0006, 0.2174, -D - 0.001), [shade], f_hud)
        R['durs'] = line_durs()

        # ---------- render ----------
        sc.render.engine = 'BLENDER_EEVEE'
        ee = sc.eevee
        setp(ee, 'volumetric_tile_size', '8')
        setp(ee, 'volumetric_samples', 48)
        setp(ee, 'volumetric_start', 0.3)
        setp(ee, 'volumetric_end', 90.0)
        setp(ee, 'use_volumetric_shadows', True)
        setp(ee, 'use_shadows', True)
        vs = sc.view_settings
        setp(vs, 'view_transform', 'AgX')
        looks = [i.identifier for i in vs.bl_rna.properties['look'].enum_items]
        for want in ('AgX - Medium High Contrast', 'AgX - Base Contrast'):
            if want in looks:
                vs.look = want
                break
        vs.exposure = float(os.environ.get('EXPOSURE', 0.0))
        sc.render.image_settings.file_format = 'PNG'
        sc.render.image_settings.color_mode = 'RGB'
        sc.render.use_lock_interface = True
        return sc

    # ======================================================================================
    #  PER-FRAME STATE
    # ======================================================================================
    def look(ob, pos, tgt):
        ob.location = pos
        ob.rotation_euler = (Vector(tgt) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()

    def handheld(u):
        return Vector((0.014 * math.sin(2.1 * u) + 0.008 * math.sin(3.7 * u + 1.0), 0.006 * math.sin(1.7 * u + 2),
                       0.011 * math.sin(2.9 * u + 2.0)))

    def cam_alley(u):
        ref = Vector((0, Yk(u), 0))
        if u < 0:
            e = 1 - ss(-6.0, -1.0, u)
            R_, phi, h = 3.5 * (1 + 0.3 * e), 110 + 14 * e, 1.25 + 0.3 * e
            tgt = Vector((-0.3 * e, 0, 0.95 + 0.1 * e))
        else:
            o = ss(3.6, 6.4, u)
            R_ = 3.5 - 0.45 * ss(1.6, 3.4, u) - 1.4 * math.sin(math.pi * o) + 0.55 * o - 0.3 * ss(6.4, 8.0, u)
            phi = 110 + 150 * o
            h = 1.25 + 0.65 * o + 2.2 * math.sin(math.pi * o)       # crane up and over their heads
            tgt = Vector((0, 0, 0.95)) + ss(5.2, 6.6, u) * Vector((0.35, 6.0, 1.1))
        # behind them: the CAMERA shifts right so the knight is not cut by the edge (the lights stay: x 3.2 is behind the wall)
        sh = Vector((0.5 * ss(4.8, 6.4, u), 0, 0)) if u >= 0 else Vector((0, 0, 0))
        pos = ref + sh + Vector((R_ * math.cos(math.radians(phi)), R_ * math.sin(math.radians(phi)), h)) + handheld(u)
        pos.x = max(-2.3, min(2.3, pos.x))            # never inside the alley walls (x = +-3)
        return pos, ref + sh + tgt, ref

    def hide_all(P, v):
        P.show(v)

    def place_lights(ref, flip=0.0):
        """flip 0: camera on +Y (in front of the runners), 1: camera on -Y. The key stays on the camera side."""
        sy = 1 - 2 * flip
        look(R['key'], ref + Vector((2.7, 4.5 * sy, 4.6)), ref + Vector((0, 0, 1.0)))
        look(R['rim'], ref + Vector((-1.8, -3.2 * sy, 3.4)), ref + Vector((0, 0, 1.2)))
        look(R['fill'], ref + Vector((-2.5, 3.5 * sy, 1.5)), ref + Vector((0, 0, 1.0)))

    def knight_alley(u, K):
        if u < 0:
            K.show(False)
            return
        K.show(True)
        y = Yk(u)
        a = vel_k(u) / V
        r = run_pose(run_phase_k(u), a)
        r['cape'] = (-0.5 * a - 0.08 * a * math.sin(u * 9), 0, 0)
        r['cape2'] = (-0.25 * a + 0.1 * a * math.sin(u * 11 + 1), 0, 0)
        idle = math.sin(2 * math.pi * u / 3.0)
        r = add(r, {'torso': (0.02 * idle, 0, 0)})
        # head turns to the goblin when he is hit
        r = add(r, {'head': (0, 0, 0.55 * bump(0.3, 0.6, 0.9, 1.2, u))})
        # catch: both arms forward, then hold, then release
        wc = ss(0.95, 1.35, u) * (1 - ss(3.0, 3.4, u))
        hold = {'shoulder_L': (1.15, 0.1, 0.2), 'shoulder_R': (1.15, -0.1, -0.2), 'elbow_L': (0.7, 0, 0), 'elbow_R': (0.7, 0, 0),
                'torso': (-0.12, 0, 0), 'head': (0.25, 0, 0)}
        r = blend(r, hold, wc)
        # after: left arm offered to the goblin who grabs it
        r = add(r, {'shoulder_L': (0.35, 0.25, 0)}, ss(3.3, 3.6, u))
        # looks up and around the rooftops, then to the tower
        r = add(r, {'head': (0.32, 0, 0.45 * math.sin((u - 3.7) * 2.4))}, bump(3.6, 4.0, 4.9, 5.4, u))
        r = add(r, {'head': (0.18, 0, 0)}, ss(5.6, 6.2, u))
        dz = -0.08 * bump(1.45, 1.6, 1.7, 2.1, u) - 0.02 * wc
        K.pose((KX, y, 0), 0.0, r, dz)
        K.sword.hide_render = K.sword_x.hide_render = True
        K.sheath.hide_render = K.hilt.hide_render = False

    def goblin_alley(u, G):
        A = R['arrow']
        AS = R['arrow_stuck']
        fl, flo, col = R['flash'], R['flash_lo'], R['column']
        fl.hide_render = True
        col.hide_render = True
        R['flash_l'].energy = 0
        show_arrow, show_stuck = False, False
        face, talk, face2, fw = 'run', 0.0, None, 0.0
        if T_LOOSE <= u < T_HIT:
            show_arrow = True
            p = Vector(arrow_pos(u))
            d = (Vector(arrow_target()) - Vector(ARCHER)).normalized()
            A.location = p
            A.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
        if u >= 0:
            y = Yg(u)
            if u < T_HIT:
                G.show(True)
                r = run_pose(run_phase_g(u), 1.0, 1.4, 0.3)
                r['scarf'] = (-0.9, 0, 0)
                face = 'terror'
                G.pose((GX, y, 0), 0.0, r)
            elif u < T_VANISH + 0.1:
                G.show(True)
                show_stuck = u < T_VANISH + 0.1
                w = ss(T_HIT, 0.6, u)
                r = run_pose(run_phase_g(T_HIT), 1.0 - w, 1.4, 0.3)
                r = blend(r, {'torso': (-1.0, 0, 0.2), 'head': (0.5, 0, 0), 'thigh_L': (1.4, 0, 0), 'thigh_R': (1.2, 0, 0),
                              'knee_L': (-2.1, 0, 0), 'knee_R': (-1.9, 0, 0), 'shoulder_L': (2.3, 0.3, 0),
                              'shoulder_R': (2.0, -0.4, 0), 'elbow_L': (0.4, 0, 0), 'elbow_R': (0.6, 0, 0),
                              'scarf': (-0.3, 0, 0)}, w)
                face = 'pain'
                sh = 1 - ss(T_VANISH, T_VANISH + 0.1, u)
                G.pose((GX, y, 0), 0.0, r, -0.27 * ss(0.35, 0.8, u), max(sh, 0.001))
                if u >= T_VANISH - 0.05:
                    e = (u - (T_VANISH - 0.05)) / 0.3
                    fl.hide_render = False
                    fl.location = (GX, y + 0.2, 0.5)
                    s = 0.15 + 0.9 * e
                    fl.scale = (s, s, s)
                    R['flash_l'].energy = 1500 * (1 - e)
                    flo.location = (GX, y + 0.4, 0.8)
                    if e > 0.6:
                        fl.hide_render = True
            elif u < T_RESPAWN:
                G.show(False)
                if u < T_VANISH + 0.3:
                    e = (u - (T_VANISH - 0.05)) / 0.3
                    fl.hide_render = e > 0.6
                    fl.location = (GX, Yg(u) + 0.2, 0.5)
                    fl.scale = (0.15 + 0.9 * e,) * 3
                    R['flash_l'].energy = 1500 * max(0, 1 - e)
            else:
                G.show(True)
                ky = Yk(u)
                hold_p = Vector((KX - 0.05, ky + 0.72, 0.48))
                if u < T_CATCH:
                    e = (u - T_RESPAWN) / (T_CATCH - T_RESPAWN)
                    p = hold_p + Vector((0, 0, 2.2 * (1 - e * e)))
                    r = {'shoulder_L': (2.6, 0.5, 0), 'shoulder_R': (2.6, -0.5, 0), 'thigh_L': (0.6, 0, 0), 'thigh_R': (0.3, 0, 0),
                         'knee_L': (-0.8, 0, 0), 'knee_R': (-0.5, 0, 0), 'scarf': (0.8, 0, 0)}
                    face = 'shock'
                    col.hide_render = False
                    col.location = (hold_p.x, hold_p.y, 3.2)
                    cs = 1 - ss(T_RESPAWN + 0.1, T_CATCH + 0.1, u)
                    col.scale = (cs, cs, 1)
                    R['flash_l'].energy = 600 * cs
                    flo.location = (hold_p.x, hold_p.y, 2.0)
                    G.pose(tuple(p), 0.0, r)
                elif u < 3.0:
                    dip = -0.08 * bump(1.45, 1.6, 1.7, 2.1, u)
                    p = hold_p + Vector((0, 0, dip))
                    r = {'thigh_L': (1.5, 0, 0), 'thigh_R': (1.4, 0, 0), 'knee_L': (-1.3, 0, 0), 'knee_R': (-1.5, 0, 0),
                         'torso': (0.15, 0, 0), 'shoulder_L': (2.7, -0.2, 0), 'elbow_L': (2.0, 0, 0),
                         'shoulder_R': (0.4, -0.2, 0), 'head': (-0.1 + 0.1 * math.sin(u * 3), 0, 0.2), 'scarf': (0.2, 0, 0)}
                    if u < T_CATCH + 0.12:
                        col.hide_render = False
                        col.location = (hold_p.x, hold_p.y, 3.2)
                        cs = 1 - ss(T_RESPAWN + 0.1, T_CATCH + 0.1, u)
                        col.scale = (max(cs, 0.001), max(cs, 0.001), 1)
                    face, face2, fw = 'pain', 'sad', ss(2.4, 2.9, u)
                    G.pose(tuple(p), 0.0, r)
                else:
                    e = ss(3.0, 3.4, u)
                    ground = Vector((0.0, ky + 0.25, 0))
                    p = hold_p.lerp(ground, e) + Vector((0, 0, 0.25 * math.sin(math.pi * e)))
                    stand = {'shoulder_R': (0.6, -1.0, 0), 'elbow_R': (0.5, 0, 0), 'head': (0.35, 0, -0.2),
                             'shoulder_L': (0.1, 0.1, 0), 'scarf': (0.2, 0, 0)}
                    held = {'thigh_L': (1.5, 0, 0), 'thigh_R': (1.4, 0, 0), 'knee_L': (-1.3, 0, 0), 'knee_R': (-1.5, 0, 0)}
                    r = blend(held, stand, e)
                    rz = -0.5 * ss(3.2, 3.6, u)
                    face = 'shock'
                    # points at the tower
                    wpt = bump(5.7, 6.0, 7.4, 7.9, u)
                    r = blend(r, {'shoulder_R': (2.3, -0.15, 0), 'elbow_R': (0.1, 0, 0), 'head': (0.3, 0, 0),
                                  'torso': (-0.05, 0, 0)}, wpt)
                    rz = lerp(rz, 0.0, ss(5.6, 6.0, u))
                    G.pose(tuple(p), rz, r)
        else:
            # ---------------- the ending: restored at the checkpoint, alone ----------------
            y = Yg(u)
            if u < T_END_RESPAWN:
                G.show(False)
            else:
                G.show(True)
                drop = 0.5 * (1 - ss(T_END_RESPAWN, T_END_RESPAWN + 0.2, u))
                land = bump(-5.65, -5.55, -5.4, -5.0, u)
                r = {'thigh_L': (0.9 * land, 0, 0), 'thigh_R': (0.9 * land, 0, 0), 'knee_L': (-1.4 * land, 0, 0),
                     'knee_R': (-1.4 * land, 0, 0), 'torso': (-0.3 * land, 0, 0)}
                face = 'shock'
                # looks around, reaches for the empty space where the knight was
                r = add(r, {'head': (0, 0, 0.5 * math.sin((u + 5.0) * 2.2))}, bump(-5.1, -4.9, -4.7, -4.5, u))
                reach = bump(-4.6, -4.2, -3.7, -3.3, u)
                r = add(r, {'head': (-0.1, 0, -0.8), 'shoulder_R': (0.5, -1.1, 0), 'elbow_R': (0.2, 0, 0),
                            'torso': (0, 0, -0.25)}, reach)
                face2, fw = 'sad', ss(-4.4, -4.0, u)
                r = add(r, {'head': (-0.3, 0, 0)}, bump(-3.6, -3.3, -2.7, -2.5, u))
                # hears the bow, turns round to it, terror
                turn = ss(-2.5, -2.05, u) * (1 - ss(-1.3, -0.95, u))
                rz = 2.8 * turn
                r = add(r, {'head': (0.5, 0, 0), 'torso': (0.1, 0, 0), 'shoulder_L': (0.3, 0.4, 0), 'shoulder_R': (0.3, -0.4, 0)},
                        ss(-2.2, -1.9, u) * (1 - ss(-1.25, -1.0, u)))
                if u > -2.1:
                    face, face2, fw = 'terror', None, 0.0
                tremble = 0.02 * math.sin(u * 60) * bump(-2.0, -1.9, -1.3, -1.1, u)
                r = add(r, {'torso': (tremble, 0, tremble)})
                a = vel_g(u) / V
                if a > 0:
                    rr = run_pose(run_phase_g(u), 1.0, 1.4, 0.3)
                    rr['scarf'] = (-0.9, 0, 0)
                    r = blend(r, rr, ss(-1.0, -0.6, u))
                G.pose((GX, y, drop), rz, r)
                if u >= T_END_RESPAWN and u < T_END_RESPAWN + 0.35:
                    e = (u - T_END_RESPAWN) / 0.35
                    fl.hide_render = False
                    fl.location = (GX, y, 0.6)
                    fl.scale = (0.3 + 1.2 * e,) * 3
                    R['flash_l'].energy = 2500 * (1 - e)
                    flo.location = (GX, y + 0.4, 0.9)
                    fl.hide_render = e > 0.7
        # talking mouth
        durs = R['durs']
        t = u if u >= 0 else u + T_END
        talk = talking('G', t, durs)
        set_face(G, face, talk, face2, fw)
        for ob in A.children:
            ob.hide_render = not show_arrow
        R['arrow_trail'].hide_render = not show_arrow
        for ob in AS.children:
            ob.hide_render = not show_stuck
        if show_stuck:
            d = (Vector(arrow_target()) - Vector(ARCHER)).normalized()
            AS.location = (0.1, -0.05, 0.27)
            AS.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()

    # ---------------- the middle (8-52 s) ----------------
    def b1_cam_y(t):
        y0 = b1_center(min(t, 13.4))[0] - 3.2
        if t <= 13.4:
            return y0
        xs = np.linspace(13.4, t, 60)
        return y0 - 2.8 * float(np.trapezoid([1 - ss(13.4, 14.0, x) for x in xs], xs))

    def hide_fx():
        for ob in R['arrow'].children:
            ob.hide_render = True
        R['arrow_trail'].hide_render = True
        for ob in R['arrow_stuck'].children:
            ob.hide_render = True
        R['flash'].hide_render = True
        R['column'].hide_render = True
        R['flash_l'].energy = 0

    def walk_add(r, ph, a, arms=0.5):
        if a < 0.02:
            return r
        w = run_pose(ph, a)
        w = {k: v for k, v in w.items() if not k.startswith('elbow')}
        for k in ('shoulder_L', 'shoulder_R'):
            w[k] = tuple(x * arms for x in w[k])
        return add(r, w)

    def b1(t):
        K, G, B, S = R['K'], R['G'], R['B'], R['S']
        B.show(False)
        K.show(True)
        G.show(True)
        yc, sp = b1_center(t)
        a = sp / 2.8
        e = ss(8.0, 9.4, t)
        turn = math.pi * ss(8.6, 9.0, t)
        ph = (Yk(8.0) - yc) / 1.7 * 2 * math.pi
        rk = run_pose(ph, a)
        rk['cape'] = (-0.5 * a, 0, 0)
        rk = add(rk, {'shoulder_L': (-0.6, 0.5, 0), 'elbow_L': (-0.8, 0, 0)}, a)       # pulls the goblin by the hand
        rk = add(rk, {'head': (0.18, 0, 0)}, 1 - ss(8.4, 8.9, t))
        K.pose((lerp(KX, 0.3, e), yc, 0), turn, rk)
        K.sword.hide_render = K.sword_x.hide_render = True
        K.sheath.hide_render = K.hilt.hide_render = False
        rg = run_pose((Yk(8.0) - yc) / 1.15 * 2 * math.pi + 1.3, a, 1.4, 0.3)
        rg['scarf'] = (-0.9 * a, 0, 0)
        rg = add(rg, {'shoulder_R': (1.2, -0.3, 0)}, a)
        rg = blend(rg, {'shoulder_R': (2.3, -0.15, 0), 'elbow_R': (0.1, 0, 0), 'head': (0.3, 0, 0)}, 1 - ss(8.2, 8.8, t))
        G.pose((lerp(0.0, -0.35, e), yc + 0.25 + 0.2 * e, 0), turn, rg)
        talk = talking('G', t, R['durs'])
        set_face(G, 'terror', talk)
        for i, P in enumerate(S):
            ti = 8.0 + 0.3 * i
            P.show(t >= ti - 0.3)
            xl = -1.8 + 0.9 * i
            x = lerp(-3.7, xl, ss(ti, ti + 1.2, t))
            y = 12.0 + 0.5 * (i % 2) - 1.6 * max(0.0, t - ti - 0.6)
            rz = lerp(-math.pi / 2, -math.pi, ss(ti + 0.2, ti + 1.0, t))
            P.pose((x, y, 0), rz, run_pose((t - 8.0) * 1.6 * 2 * math.pi, 0.55, 0.3, 0.05))   # one shared step: in unison
        # camera: from the end of the opening (behind them, tower) into a backwards run in front of them, then they pass us
        p0, t0, _ = cam_alley(8.0)
        ky = b1_cam_y(t)
        pb = Vector((lerp(0.5, -0.2, ss(12.0, 13.6, t)) + 0.12 * math.sin(t * 0.9), ky, 1.35)) + handheld(t)
        tb = Vector((0.0, yc + 4.0, 1.4))
        knee = Vector((0.3, yc, 1.55))
        tb = tb.lerp(knee, ss(13.7, 14.6, t))
        look(R['cam'], p0.lerp(pb, e), t0.lerp(tb, e))
        place_lights(Vector((0, yc, 0)), 1.0)

    def chamber(t):
        K, G, B, S = R['K'], R['G'], R['B'], R['S']
        c = Vector(CH)
        K.show(True), G.show(True), B.show(True)
        # --- knight
        x, y, rz, ph, sp = MV_K.at(t)
        r = pose_keys_at(KN_POSE, t)
        r = walk_add(r, ph, min(1.0, sp / 2.6))
        dz = 0.0
        hd = Vector((0, 0, 0))
        cr = ss(T_CRUMBLE, 51.0, t)
        if cr > 0:                                       # the hollow armour gives way: inert parts
            r = add(r, {'thigh_L': (1.5, 0, 0.2), 'thigh_R': (1.3, 0, -0.2), 'knee_L': (-2.4, 0, 0), 'knee_R': (-2.2, 0, 0),
                        'torso': (0.6, 0, 0.25), 'shoulder_L': (-0.3, 0.3, 0), 'shoulder_R': (-0.4, -0.3, 0),
                        'head': (-1.2, 0.4, 0), 'cape': (0.4, 0, 0)}, cr)
            dz = -0.72 * cr
            hd = Vector((-0.2, -0.45, -0.55)) * ss(49.3, 50.4, t)      # falls backwards, away from the goblin
        K.pose(tuple(c + Vector((x, y, 0))), rz, r, dz)
        K.j['head'].location = K.rest['head'] + hd
        K.j['plate'].rotation_euler = (0, 0, key_at(PLATE, t)[0])
        drawn = SWORD_DRAWN[0] <= t < SWORD_DRAWN[1]
        K.sword.hide_render = K.sword_x.hide_render = not drawn
        K.hilt.hide_render = drawn
        K.sheath.hide_render = False
        K.spark.hide_render = t >= T_BELL + 0.1
        R['mats']['soul_k'].node_tree.nodes['Emission'].inputs['Strength'].default_value = \
            (1.6 + 0.8 * math.sin(t * 4.0)) * (1 - ss(T_BELL, T_BELL + 1.5, t))
        # --- goblin
        x, y, rz, ph, sp = MV_G.at(t)
        r = pose_keys_at(GB_POSE, t)
        r['scarf'] = (-0.9 * min(1.0, sp / 2.6) - 0.1, 0, 0)
        r = walk_add(r, ph + 1.3, min(1.0, sp / 2.0), 1.0)
        gdz = -0.15 * bump(17.3, 17.45, 18.2, 18.6, t)
        G.pose(tuple(c + Vector((x, y, 0))), rz, r, gdz)
        f0, f1, w = face_at(t)
        talk = talking('G', t, R['durs'])
        set_face(G, f0, talk, f1, w)
        # --- bellwright
        x, y, rz, ph, sp = MV_B.at(t)
        r = pose_keys_at(BW_POSE, t)
        r = walk_add(r, ph, min(1.0, sp / 2.0))
        if t < 19.6:                                     # shoving the slipping gear
            r = add(r, {'torso': (0.05 * math.sin(t * 5.0), 0, 0)})
        for k in lines_of('B'):
            if LINES[k] <= t < LINES[k] + R['durs'].get(k, 1.5):
                r = add(r, {'head': (0.06 * math.sin(2 * math.pi * 2.5 * (t - LINES[k])), 0, 0)})
        B.pose(tuple(c + Vector((x, y, 0))), rz, r)
        # --- shells: march in, stop, kneel in unison
        for i, P in enumerate(S):
            P.show(t >= T_SHELLS_IN - 0.5)
            e = ss(T_SHELLS_IN, T_SHELLS_STOP, t)
            e2 = ss(T_SHELLS_IN + 1.0, T_SHELLS_STOP, t)           # a file through the gap, then the V
            p = (lerp(0.35 * (i - 2), SHELL_X[i], e2), lerp(-9.5 - 0.6 * abs(i - 2), SHELL_Y[i], e), 0)
            k = ss(T_KNEEL - 0.2, T_KNEEL + 0.15, t)
            walk = run_pose((t - T_SHELLS_IN) * 1.6 * 2 * math.pi, 0.5 * (1 - ss(T_SHELLS_STOP - 0.4, T_SHELLS_STOP, t)), 0.3, 0.05)
            kneel = {'thigh_R': (1.5, 0, 0), 'knee_R': (-1.5, 0, 0), 'thigh_L': (-0.2, 0, 0), 'knee_L': (-2.3, 0, 0),
                     'torso': (-0.35, 0, 0), 'head': (-0.4, 0, 0), 'shoulder_R': (0.4, 0, 0)}
            P.pose(tuple(c + Vector(p)), 0.0, blend(walk, kneel, k), -0.5 * k)
        # --- the chamber machinery
        slip = 0.25 * math.sin(t * 6.0) * (1 - ss(19.4, 20.0, t)) + 0.5 * ss(16.55, 16.7, t) + 0.6 * ss(19.75, 19.9, t)
        R['ch_slip'].rotation_euler = (math.radians(90), slip, 0)
        R['lash'].rotation_euler = (0.75 * math.sin(2.4 * t) * math.exp(-max(0.0, t - 15.0) / 6.0), 0.2 * math.sin(1.7 * t), 0)
        hk = R['hook']
        if t < 17.0:
            hk.location = c + Vector((-0.7, -2.6, 7.5))
        elif t < 17.55:
            e = (t - 17.0) / 0.55
            hk.location = c + Vector((-0.7, -2.6, 7.5 - 5.2 * e * e))
        else:
            e = ss(17.55, 18.2, t)
            hk.location = c + Vector((lerp(-0.7, 1.3, e), lerp(-2.6, -3.4, e), lerp(2.3, 0.12, e) + 0.6 * math.sin(math.pi * e)))
            hk.rotation_euler = (3.0 * e, 1.0 * e, 0)
        R['ch_panel'].location = c + Vector((-2.1 * ss(37.6, 38.4, t), 2.6, 1.6))
        for ob in R['ch_ring'].children:                 # the ring exists only once the panel opens
            ob.hide_render = t < 37.65
        yank = -0.35 * bump(T_YANK - 0.05, T_YANK + 0.1, T_YANK + 0.3, T_YANK + 0.8, t)
        R['ch_chain'].location = c + Vector((1.6, 1.8, 6.4 + yank))
        R['ch_handle'].location = c + Vector((1.6, 1.8, 1.85 + yank))
        bell = 0.0
        if t > T_BELL:
            bell = 0.33 * math.sin(2 * math.pi * (t - T_BELL) / 2.2) * math.exp(-(t - T_BELL) / 6)
        R['ch_bell_pivot'].rotation_euler = (bell, 0, 0)
        # --- the price: the soul leaves his chest and runs into the bell
        kx, ky = MV_K.at(t)[:2]
        chest = c + Vector((kx, ky + 0.15, 1.45))
        bellp = c + Vector((0, 1.5, 6.4))
        on = T_BELL <= t < 50.8
        fade = 1 - ss(49.8, 50.8, t)
        for i, ob in enumerate(R['soul']):
            ob.hide_render = not on
            if on:
                s_ = ((t - T_BELL) * 0.9 + i / len(R['soul'])) % 1.0
                p = chest.lerp(bellp, s_) + Vector((0.5 * math.sin(math.pi * s_) * math.sin(i * 2.3), 0.3 * math.sin(math.pi * s_), 0))
                ob.location = p
                k = (0.6 + 0.6 * math.sin(math.pi * s_)) * fade
                ob.scale = (k, k, k)
        bm = R['beam']
        bm.hide_render = not on
        if on:
            d = bellp - chest
            bm.location = (chest + bellp) / 2
            bm.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
            pul = (1 + 0.3 * math.sin(t * 30)) * fade
            bm.scale = (pul, pul, d.length)
        R['soul_light'].energy = 600 * fade if on else 0.0
        R['soul_light_o'].location = c + Vector((1.35, 0.6, 1.3))
        cx_, cy_, cz_, tx, ty, tz = cr_at(CAM_CH, t)
        cp, tp = c + Vector((cx_, cy_, cz_)) + handheld(t), c + Vector((tx, ty, tz))
        look(R['cam'], cp, tp)
        fw = (tp - cp).normalized()
        rt = fw.cross(Vector((0, 0, 1))).normalized()
        look(R['key'], cp + rt * 1.8 + Vector((0, 0, 1.4)) - fw * 0.5, tp)          # key from the camera side: faces always read
        look(R['rim'], tp + fw * 3.0 - rt * 1.0 + Vector((0, 0, 2.2)), tp)
        look(R['fill'], cp - rt * 2.0 + Vector((0, 0, 0.3)), tp)

    def mid(t):
        hide_fx()
        R['K'].spark.hide_render = False
        if t < T_WIPE:
            for ob in R['soul']:
                ob.hide_render = True
            R['beam'].hide_render = True
            R['soul_light'].energy = 0
            b1(t)
        else:
            chamber(t)

    def subtitles(t):
        durs = R['durs']
        cur = None
        for k, t0 in LINES.items():
            end = t0 + durs.get(k, 0.8) + 0.3
            if k == LAST:
                end = min(end, T_END - 0.15)
            if t0 - 0.05 <= t < end:
                cur = k
        sub, sh = R['sub'], R['sub_sh']
        if cur is None:
            sub.hide_render = sh.hide_render = True
            return
        txt = TEXT[cur]
        if len(txt) > 24:                              # two lines, break at the space nearest the middle
            sp = [i for i, ch in enumerate(txt) if ch == ' ']
            b = min(sp, key=lambda i: abs(i - len(txt) / 2))
            txt = txt[:b] + '\n' + txt[b + 1:]
        sub.hide_render = sh.hide_render = False
        sub.data.body = txt
        sh.data.body = txt
        word, colr = HILITE[cur]
        i0 = txt.find(word)
        for i in range(len(sub.data.body_format)):
            sub.data.body_format[i].material_index = (1 if colr == 'c' else 2) if (i0 >= 0 and i0 <= i < i0 + len(word)) else 0

    def hud(t, u):
        h, hs, n, ns, r, rs = R['hud'], R['hud_sh'], R['hud_n'], R['hud_n_sh'], R['hud_r'], R['hud_r_sh']
        on = u is not None and u >= 0 and 3.0 <= u < 7.9
        for o in (h, hs, n, ns):
            o.hide_render = not on
        if on:
            h.data.body = hs.data.body = 'RESPAWNS LEFT'
            zero = u >= T_SNAP
            n.data.body = ns.data.body = '0' if zero else '1'
            pop = 1 + 0.6 * bump(T_SNAP, T_SNAP + 0.04, T_SNAP + 0.1, T_SNAP + 0.3, u)
            jit = 0.0025 * math.sin(u * 90) * bump(T_SNAP, T_SNAP + 0.02, T_SNAP + 0.25, T_SNAP + 0.4, u)
            n.scale = ns.scale = (pop, pop, pop)
            n.location = (-0.012 + jit, 0.218 - 0.006 * (pop - 1), -0.5)
            ns.location = (-0.0112 + jit, 0.2172 - 0.006 * (pop - 1), -0.501)
            for i in range(len(n.data.body_format)):
                n.data.body_format[i].material_index = 1 if zero else 0
        ron = u is not None and -5.4 <= u < -3.4
        r.hide_render = rs.hide_render = not ron
        if ron:
            r.data.body = rs.data.body = 'RESPAWNS RESTORED'
            s = 1 + 0.15 * (1 - ss(-5.4, -5.2, u))
            r.scale = rs.scale = (s, s, s)

    def update(scene, *_):
        f = scene.frame_current
        t = (f - 1) / FPS
        u = loop_u(t)
        # world motion (alley + tower): stuttering gears (the bell system is failing), lamp flicker, the bell is STILL
        R['tgear1'].rotation_euler = (math.radians(90), 0, 0.25 * math.floor(t * 2) + 0.05 * ss(0, 0.1, (t * 2) % 1))
        R['tgear2'].rotation_euler = (math.radians(90), 0, -0.4 * math.floor(t * 2) - 0.08 * ss(0, 0.1, (t * 2) % 1))
        R['cweight'].location.z = 7.0 + 0.04 * math.sin(t * 1.3)
        for ld, ph in R['lamps']:
            ld.energy = 140 * (0.85 + 0.1 * math.sin(t * 7.3 + ph) + 0.05 * math.sin(t * 23.0 + 2 * ph))
        R['ch_g1'].rotation_euler = (math.radians(90), 0, 0.5 + 0.2 * t)
        R['ch_g2'].rotation_euler = (math.radians(90), 0, -0.4 - 0.32 * t)
        R['ch_ring'].rotation_euler = (math.radians(90), 0, 0.6 * t)
        gl = bump(T_END - 3.0, T_END - 2.9, T_END - 2.7, T_END - 2.4, t)
        R['glint'].hide_render = gl < 0.05
        R['glint'].scale = (0.5 + gl,) * 3
        # soul pulse in the emblem / spark (nice-to-have)
        R['mats']['cyan_dim'].node_tree.nodes['Emission'].inputs['Strength'].default_value = 2.0 + 1.2 * (0.5 + 0.5 * math.sin(t * 4.0))
        K, G, B, S = R['K'], R['G'], R['B'], R['S']
        if u is not None:
            B.show(False)
            for P in S:
                P.show(False)
            K.j['plate'].rotation_euler = (0, 0, 0)
            K.j['head'].location = K.rest['head']
            K.spark.hide_render = False
            R['mats']['soul_k'].node_tree.nodes['Emission'].inputs['Strength'].default_value = 1.6 + 0.8 * math.sin(t * 4.0)
            for ob in R['soul']:
                ob.hide_render = True
            R['beam'].hide_render = True
            R['soul_light'].energy = 0
            knight_alley(u, K)
            goblin_alley(u, G)
            pos, tgt, ref = cam_alley(u)
            look(R['cam'], pos, tgt)
            place_lights(ref, ss(4.5, 6.0, u) if u >= 0 else 0.0)
        else:
            mid(t)
        # the light washes over the goblin at the end of the chamber and is still there when he is restored in the alley
        wf = ss(51.5, 52.0, t) if t < 52.0 else 1 - ss(52.0, 52.3, t)
        R['wash'].hide_render = wf < 0.01
        R['wash_fac'].default_value = wf
        subtitles(t)
        hud(t, u)

    def mux(cut):
        frames_dir = os.path.join(OUT, 'preview')
        if cut == 'hook':
            fr = list(range(1, 193))
        elif cut == 'full':
            fr = list(range(1, NF + 1))
        else:
            fr = list(range(1249, NF + 1)) + list(range(1, 73))
        files = ['f_%04d.png' % f for f in fr]
        missing = [f for f in files if not os.path.exists(os.path.join(frames_dir, f))]
        if missing:
            raise SystemExit('missing frames: %d, first %s' % (len(missing), missing[0]))
        wav = os.path.join(OUT, 'audio', cut + '.wav')
        sc = bpy.context.scene
        sc.sequence_editor_create()
        se = sc.sequence_editor
        strips = se.strips if hasattr(se, 'strips') else se.sequences
        s = strips.new_image('img', os.path.join(frames_dir, files[0]), 1, 1)
        for f in files[1:]:
            s.elements.append(f)
        strips.new_sound('snd', wav, 2, 1)
        img = bpy.data.images.load(os.path.join(frames_dir, files[0]))
        sc.render.resolution_x, sc.render.resolution_y = img.size
        sc.render.resolution_percentage = 100
        sc.render.fps = FPS
        sc.frame_start, sc.frame_end = 1, len(files)
        r = sc.render
        setp(r.image_settings, 'media_type', 'VIDEO')
        r.image_settings.file_format = 'FFMPEG'
        r.ffmpeg.format = 'MPEG4'
        r.ffmpeg.codec = 'H264'
        setp(r.ffmpeg, 'constant_rate_factor', 'HIGH')
        r.ffmpeg.audio_codec = 'AAC'
        r.ffmpeg.audio_bitrate = 192
        r.ffmpeg.audio_mixrate = 48000
        setp(r.ffmpeg, 'audio_channels', 'STEREO')
        r.use_sequencer = True
        r.filepath = os.path.join(OUT, 'last_respawn_%s_' % cut)
        bpy.ops.render.render(animation=True)
        print('MUX done', r.filepath)

    # ======================================================================================
    if MODE == 'mux':
        mux(os.environ.get('CUT', 'hook'))
    else:
        sc = build()
        bpy.app.handlers.frame_change_pre.append(update)
        sc.render.resolution_percentage = int(os.environ.get('PCT', 50))
        setp(sc.eevee, 'taa_render_samples', int(os.environ.get('SAMPLES', 16)))
        os.makedirs(OUT, exist_ok=True)
        if os.environ.get('SAVE'):
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'last_respawn.blend'))
        frames = os.environ.get('FRAMES', '1')
        sub = 'stills' if MODE == 'still' else 'preview'
        d = os.path.join(OUT, sub)
        os.makedirs(d, exist_ok=True)
        if '-' in frames and MODE == 'anim':
            a, b = map(int, frames.split('-'))
            sc.frame_start, sc.frame_end = a, b
            sc.render.filepath = os.path.join(d, 'f_')
            bpy.ops.render.render(animation=True)
        else:
            todo = []
            for part in frames.split(','):
                if '-' in part:
                    a, b = map(int, part.split('-'))
                    todo += list(range(a, b + 1))
                else:
                    todo.append(int(part))
            for f in todo:
                sc.frame_set(f)
                sc.render.filepath = os.path.join(d, 'f_%04d.png' % f)
                bpy.ops.render.render(write_still=True)
        print('RENDER done', d)
elif __name__ == '__main__':
    build_audio()
