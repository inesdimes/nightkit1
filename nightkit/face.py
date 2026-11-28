"""Face performance layer for hd humans (Insert Disc 2, 28 Nov 2026) - phase 1 of the human performance system.
Built on nightkit/facerig.py (the high-density face from Fox Wind / Sorceress). Opt-in: an hd pose with P['face'] (an expression dict or a
preset name) draws this face; without it hd.human keeps the old decal face, so every existing video renders exactly as before.

    P['face'] = face.expr('determined')                         # a preset
    P['face'] = face.expr('smug', smR=1.0, look=(0.4, 0))       # a preset + overrides
    P['FX'] = ('sweat', 'blush')                             # anime marks: sweat, vein, blush, gloom, sparkle
    T = face.Track([(0.0, 'neutral'), (1.2, 'shocked'), (2.0, 'angry', dict(teeth=1.0))], blinks=True)
    P['face'] = T.at(t, talk=amp)                               # snap + hold (anime timing), auto blinks, mouth from the voice amplitude

Expression channels (facerig): browR/L (-1 low .. 1 high), innerR/L (inner brow end up: worry), furrow (knit), eyesR/L (0 shut .. 1 open ..
1.3 wide), squintR/L, smR/L (mouth corners: + smile, - frown), press, open, round, wide, teeth, jaw, cheekR/L, hollowR/L, look=(x, y),
bold (brow + lash weight; 1 = the old rig, 1.4 default, ~2 for wide shots), eye_size (1 = old rig, 1.15 default)."""
import math
import numpy as np
from . import hd, facerig
V = np.array
NEUTRAL = dict(browR=0.0, browL=0.0, innerR=0.0, innerL=0.0, furrow=0.0, eyesR=1.0, eyesL=1.0, squintR=0.0, squintL=0.0, smR=0.0, smL=0.0,
               press=0.0, open=0.0, round=0.0, wide=0.0, teeth=0.0, jaw=0.0, cheekR=0.0, cheekL=0.0, hollowR=0.0, hollowL=0.0, look=(0.0, 0.0), bold=1.4, eye_size=1.15)
def _both(**kw):
    """helper: browR/browL etc. from brow=..."""
    out = {}
    for k, v in kw.items():
        if k in ('brow', 'inner', 'eyes', 'squint', 'sm', 'cheek', 'hollow'): out[k + 'R'] = v; out[k + 'L'] = v
        else: out[k] = v
    return out
PRESETS = {   # one clear intention each; FX = the anime marks that come with it
    'neutral':     (_both(), ()),
    'determined':  (_both(brow=-0.55, inner=-0.7, furrow=1.0, eyes=0.7, squint=0.4, press=0.85, sm=-0.1), ()),
    'smug':        (dict(browR=0.55, browL=-0.25, eyesR=0.68, eyesL=0.62, smR=0.85, smL=0.05, cheekR=0.55, look=(0.35, 0.0)), ()),
    'shocked':     (_both(brow=0.95, inner=0.3, eyes=1.3, open=0.75, round=0.35, jaw=0.6), ('gloom',)),
    'scared':      (_both(brow=0.6, inner=0.85, eyes=1.22, open=0.3, wide=0.7, teeth=0.7, sm=-0.25), ('sweat',)),
    'deadpan':     (_both(brow=-0.08, eyes=0.52, press=0.35), ()),
    'angry':       (_both(brow=-0.7, inner=-1.1, furrow=1.0, eyes=0.95, squint=0.35, open=0.4, wide=1.0, teeth=1.0, jaw=0.2, sm=-0.3), ('vein',)),
    'proud':       (_both(brow=0.3, eyes=0.72, sm=0.6, cheek=0.6, press=0.25), ('sparkle',)),
    'sad':         (_both(brow=-0.3, inner=1.2, eyes=0.6, sm=-0.7, press=0.4, look=(0.0, -0.6)), ()),
    'embarrassed': (dict(browR=0.2, browL=0.15, innerR=0.6, innerL=0.6, eyesR=0.82, eyesL=0.82, smR=0.35, smL=0.08, look=(0.6, -0.3)), ('blush', 'sweat')),
    'laughing':    (_both(brow=0.4, eyes=0.12, squint=1.0, cheek=1.0, sm=1.0, open=0.8, wide=0.7, teeth=0.6), ()),
}
def expr(name='neutral', **over):
    """a full expression dict: neutral <- preset <- overrides"""
    E = dict(NEUTRAL); p, fx = PRESETS[name]; E.update(p); E.update(over); E['_fx'] = tuple(over.get('_fx', fx)); return E
def blend(A, B, u):
    out = {}
    for k in NEUTRAL:
        a, b = A.get(k, NEUTRAL[k]), B.get(k, NEUTRAL[k])
        out[k] = tuple(x + (y - x) * u for x, y in zip(a, b)) if isinstance(a, tuple) else a + (b - a) * u
    out['_fx'] = B.get('_fx', ()) if u >= 0.5 else A.get('_fx', ())
    return out
def _h(i, s=0): v = math.sin(i * 127.1 + s * 311.7) * 43758.5453; return v - math.floor(v)
class Track:
    """keys = [(t, preset, overrides?)]; each key SNAPS in over `snap` s (ease-out, anime timing) and holds until the next key.
    blinks: a 3-frame blink every ~2.2-4 s (not while the eyes are nearly shut). talk(t) amplitude 0..1 drives the mouth on top."""
    def __init__(self, keys, snap=0.09, blinks=True, seed=1):
        self.keys = [(k[0], expr(k[1], **(k[2] if len(k) > 2 else {}))) for k in keys]; self.snap = snap; self.blinks = blinks
        self.blink_t = []; t = 0.6 + 1.5 * _h(seed, 3)
        for i in range(200): self.blink_t.append(t); t += 2.2 + 1.8 * _h(i, seed)
    def base(self, t):
        prev = self.keys[0][1]; cur = prev; t0 = -1e9
        for kt, E in self.keys:
            if t >= kt: prev, cur, t0 = cur, E, kt
        u = min(1.0, max(0.0, (t - t0) / self.snap)); u = 1 - (1 - u) ** 3
        return blend(prev, cur, u) if t0 > -1e9 else dict(cur)
    def at(self, t, talk=0.0, syll=None):
        E = self.base(t)
        if self.blinks and min(E['eyesR'], E['eyesL']) > 0.35:
            for bt in self.blink_t:
                if bt <= t < bt + 0.13:
                    d = (t - bt) / 0.13; c = 1 - abs(2 * d - 1) ** 0.6; E['eyesR'] *= (1 - c); E['eyesL'] *= (1 - c); break
                if bt > t: break
        if talk > 0.02:                                                      # lip sync: open with the amplitude, vowel colour from a syllable phase
            ph = syll if syll is not None else t * 9.0
            v = 0.5 + 0.5 * math.sin(ph); E['open'] = max(E['open'], 0.12 + 0.6 * talk)
            E['round'] = max(E['round'], 0.5 * talk * max(0.0, math.sin(ph * 0.5)))
            E['wide'] = max(E['wide'], 0.4 * talk * v); E['press'] *= (1 - talk)
        return E

# ---------------- anime marks, drawn on the face surface (facerig local units, scaled with the head) ----------------
def _fx(M, E, fx):
    on = lambda xy, lift: facerig.on(np.asarray(xy, float), lift, E)
    if 'sweat' in fx:                                                        # a big teardrop at the temple
        c = (0.069, 0.05); sz = 0.62                                         # 0.62: the 27 Nov drop was too big (half the eye height)
        pts = [(c[0] + sz * 0.009 * math.sin(a) * (1 - 0.6 * math.cos(a) if a < math.pi else 1), c[1] + sz * 0.016 * math.cos(a) * (0.7 if a < math.pi / 2 or a > 3 * math.pi / 2 else 1.0)) for a in np.linspace(0, 2 * math.pi, 12, endpoint=False)]
        ring = on(pts, 0.016); cc = on([c], 0.016)[0]; M.fan(cc, ring, (176, 214, 255), emit=True)
        M.fan(on([(c[0] - sz * 0.0025, c[1] - sz * 0.003)], 0.017)[0], on([(c[0] - sz * 0.0025 + sz * 0.002 * math.cos(a), c[1] - sz * 0.003 + sz * 0.004 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 6, endpoint=False)], 0.017), (250, 252, 255), emit=True)
    if 'vein' in fx:                                                         # the cross-shaped anger mark
        cx, cy = -0.042, 0.062
        for a in (0.4, 0.4 + math.pi / 2, 0.4 + math.pi, 0.4 + 3 * math.pi / 2):
            p0 = (cx + 0.003 * math.cos(a), cy + 0.003 * math.sin(a)); p1 = (cx + 0.011 * math.cos(a + 0.35), cy + 0.011 * math.sin(a + 0.35))
            nx, ny = -math.sin(a) * 0.0016, math.cos(a) * 0.0016
            q = on([(p0[0] + nx, p0[1] + ny), (p1[0] + nx, p1[1] + ny), (p1[0] - nx, p1[1] - ny), (p0[0] - nx, p0[1] - ny)], 0.016)
            M.tri(q[0], q[1], q[2], (214, 36, 40), emit=True); M.tri(q[0], q[2], q[3], (214, 36, 40), emit=True)
    if 'blush' in fx:                                                        # pink cheek ovals + three hatch strokes
        for sd in (1, -1):
            cx, cy = sd * 0.047, -0.022
            M.fan(on([(cx, cy)], 0.0046)[0], on([(cx + 0.015 * math.cos(a), cy + 0.008 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 12, endpoint=False)], 0.0046), (238, 140, 146))
            for i in (-1, 0, 1):
                x0 = cx + i * 0.006
                q = on([(x0 - 0.002, cy + 0.004), (x0 - 0.0008, cy + 0.004), (x0 + 0.0022, cy - 0.004), (x0 + 0.001, cy - 0.004)], 0.0052)
                M.tri(q[0], q[1], q[2], (196, 70, 84)); M.tri(q[0], q[2], q[3], (196, 70, 84))
    if 'gloom' in fx:                                                        # vertical shock lines over the upper face
        for i in range(5):
            x0 = -0.036 + 0.018 * i; top = 0.085; bot = 0.045 + 0.01 * (i % 2)
            q = on([(x0 - 0.0016, top), (x0 + 0.0016, top), (x0 + 0.0016, bot), (x0 - 0.0016, bot)], 0.016)
            M.tri(q[0], q[1], q[2], (60, 58, 120)); M.tri(q[0], q[2], q[3], (60, 58, 120))
    if 'sparkle' in fx:                                                      # a four-point glint by the temple
        cx, cy = 0.068, 0.06
        for a in (0.0, math.pi / 2, math.pi, 3 * math.pi / 2):
            q = on([(cx, cy), (cx + 0.012 * math.cos(a) - 0.002 * math.sin(a), cy + 0.012 * math.sin(a) + 0.002 * math.cos(a)), (cx + 0.016 * math.cos(a), cy + 0.016 * math.sin(a)), (cx + 0.012 * math.cos(a) + 0.002 * math.sin(a), cy + 0.012 * math.sin(a) - 0.002 * math.cos(a))], 0.016)
            M.tri(q[0], q[1], q[2], (255, 246, 190), emit=True); M.tri(q[0], q[2], q[3], (255, 246, 190), emit=True)

def head(hc, RH, S, P, k):
    """the hd hook: a facerig head in this character's colours + its hair / helmet / beard (hd.hair) + anime marks"""
    E = P['face']; E = expr(E) if isinstance(E, str) else E
    if 'look' not in E or E.get('look') == (0.0, 0.0):
        lk = P.get('look'); E = dict(E, look=(lk[0], lk[1]) if lk else (0.0, 0.0))
    facerig.set_style(skin=S['skin'], eye=S['eye'], brow=S['brow'] or hd.shade(S['hair'], 0.85), lip=S['lip'] or hd.mix(S['skin'], (150, 70, 70), 0.45),
                      stubble=bool(S.get('beard')) and False, scar=False)
    M = facerig.Mesh(hc, RH * k)
    facerig.head_mesh(M, E); facerig.eyes_geo(M, E); facerig.brows_geo(M, E); facerig.nose_geo(M, E); facerig.mouth_geo(M, E)
    _fx(M, E, tuple(P.get('FX', ())) + tuple(E.get('_fx', ())))
    rad = (facerig.RX * k, facerig.RY * k, facerig.RZ * k)
    Q = M.Q + hd.hair(hc, RH, S, P, k, rad, lambda p: facerig.base_def(np.asarray(p, float)[None] / k)[0] * k)
    return Q
