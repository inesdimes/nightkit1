"""Small like / follow nudge styled as a game 'ACHIEVEMENT UNLOCKED' toast (25 Nov 2026, Enes's decision after the 48 h analytics).

Rules (see ANALYTICS.md, 25 Nov):
  - never in the first 5 s (hook) and never in the last ~2 s (loop endings); default = 65 % of the video
  - top of the frame (y ~ 280 px, below a HUD counter): the bottom 20 % is covered by the caption, the right side by the like / comment buttons
  - small (about 620 x 150 px at 1080x1920), semi-transparent, 0.5 s on screen in the FINAL video (Enes, 25 Nov: it must not stay; pass dur=F(0.5) in sped-up builds)
  - text works on both YouTube and Instagram ('LIKE = +1 XP', no 'subscribe'); SUB_LANG=tr gives the Turkish one

Usage in an example script (times in BUILD seconds):
    from nightkit import cta
    CTA = cta.Achievement(t0=cta.default_time(DUR), lang=SUB_LANG)        # CTA=0 in the environment switches it off
    ... in frame_final, on the full-resolution float array:  arr = CTA.apply(arr, t)
    ... in build_audio:  put(FX, cta.chime(sr), CTA.t0, 1.0)
"""
import os
import numpy as np
from PIL import Image, ImageDraw
from . import font

TEXT = {'en': ('ACHIEVEMENT UNLOCKED', 'LIKE', '= +1 XP'),
        'tr': ('BAŞARIM AÇILDI', 'BEĞEN', '= +1 XP')}
TROPHY = ["01111111110",
          "11011111011",
          "10011111001",
          "11011111011",
          "01111111110",
          "00111111100",
          "00011111000",
          "00001110000",
          "00001110000",
          "00111111100"]
GOLD = (255, 206, 72); GOLD_HI = (255, 240, 170); WHITE = (246, 242, 230); GREEN = (140, 255, 150)
BOX = (14, 12, 26)

def enabled(): return os.environ.get('CTA', '1') != '0'
def default_time(dur, frac=0.65, dur_on=0.5):
    """65 % into the video, but never before 5 s and always ending >= 2 s before the end"""
    return float(min(max(5.0, dur * frac), dur - dur_on - 2.0))
def _ease(u): u = min(1.0, max(0.0, u)); return 1 - (1 - u) ** 3

class Achievement:
    def __init__(self, t0, lang='en', dur=0.5, y=280, x=None, W=1080, slide=0.08, alpha=0.84, on=None):
        self.t0, self.dur, self.y, self.W, self.slide, self.alpha = t0, dur, y, W, slide, alpha
        self.on = enabled() if on is None else on
        h1, w_a, w_b = TEXT.get(lang, TEXT['en'])
        for s in (h1, w_a, w_b): font.check(s)
        self.card = self._card(h1, w_a, w_b)
        cw = self.card[0].size[0]
        self.x = (W - cw) // 2 if x is None else x
    def _card(self, h1, w_a, w_b):
        s1, s2, si = 4, 6, 8                                       # header, main line, trophy cell size (sc 3 was unreadable on a phone)
        tw1 = font.width(h1, s1); tw2 = font.width(w_a + ' ' + w_b, s2)
        icon = len(TROPHY[0]) * si; pad = 22; gap = 20
        w = pad + icon + gap + max(tw1, tw2) + pad; h = pad + 7 * s1 + 14 + 7 * s2 + pad
        im = Image.new('RGB', (w, h), BOX); m = Image.new('L', (w, h), int(255 * self.alpha)); d = ImageDraw.Draw(im); dm = ImageDraw.Draw(m)
        b = 4                                                      # pixel border with cut corners
        for (x0, y0, x1, y1) in ((b, 0, w - b - 1, b - 1), (b, h - b, w - b - 1, h - 1), (0, b, b - 1, h - b - 1), (w - b, b, w - 1, h - b - 1)):
            d.rectangle([x0, y0, x1, y1], fill=GOLD); dm.rectangle([x0, y0, x1, y1], fill=255)
        for (x0, y0) in ((0, 0), (w - b, 0), (0, h - b), (w - b, h - b)): dm.rectangle([x0, y0, x0 + b - 1, y0 + b - 1], fill=0)
        iy = (h - len(TROPHY) * si) // 2
        for j, row in enumerate(TROPHY):
            for i, bit in enumerate(row):
                if bit == '1':
                    c = GOLD_HI if (i in (3, 4) and j < 5) else GOLD
                    d.rectangle([pad + i * si, iy + j * si, pad + i * si + si - 1, iy + j * si + si - 1], fill=c)
                    dm.rectangle([pad + i * si, iy + j * si, pad + i * si + si - 1, iy + j * si + si - 1], fill=255)
        tx = pad + icon + gap
        def txt(s, x, y, sc, col):
            font.text(d, s, x, y, col, sc, shadow=(0, 0, 0))
            for k, ch in enumerate(s.upper()):
                for j, row in enumerate(font.FONT[ch]):
                    for i, bit in enumerate(row):
                        if bit == '1': X = x + (k * 6 + i) * sc; Y = y + j * sc; dm.rectangle([X, Y, X + 2 * sc - 1, Y + 2 * sc - 1], fill=255)
        txt(h1, tx, pad, s1, GOLD)
        y2 = pad + 7 * s1 + 14
        txt(w_a, tx, y2, s2, WHITE); txt(w_b, tx + font.width(w_a + ' ', s2) + s2, y2, s2, GREEN)
        return im, m
    def offset(self, t):
        """vertical slide: None when hidden, else the y of the card's top edge"""
        if not self.on: return None
        u = t - self.t0
        if u < 0 or u > self.dur: return None
        h = self.card[0].size[1]; k = min(_ease(u / self.slide), _ease((self.dur - u) / self.slide))
        return int(round(-h - 10 + (self.y + h + 10) * k))
    def apply(self, arr, t):
        """paste onto a full-resolution float array (H, W, 3); returns the array"""
        y = self.offset(t)
        if y is None: return arr
        im, m = self.card; w, h = im.size; H = arr.shape[0]
        y0, y1 = max(0, y), min(H, y + h)
        if y1 <= y0: return arr
        c = np.asarray(im, np.float32)[y0 - y:y1 - y]; a = np.asarray(m, np.float32)[y0 - y:y1 - y, :, None] / 255.0
        u = t - self.t0
        if u < self.slide + 0.1:                                  # a short gold flash on the border as it lands
            fl = max(0.0, 1 - abs(u - self.slide) / 0.1) * 0.5; c = c + (255 - c) * fl * (a > 0.9)
        reg = arr[y0:y1, self.x:self.x + w]; arr[y0:y1, self.x:self.x + w] = reg * (1 - a) + c * a
        return arr

def chime(sr=48000, v=0.06):
    """the achievement 'ding': two quick bright notes + a soft shimmer, 0.9 s, mono"""
    n = int(0.9 * sr); out = np.zeros(n)
    for t0, f in ((0.0, 1318.5), (0.09, 1975.5)):
        tt = np.arange(n - int(t0 * sr)) / sr; i = int(t0 * sr)
        out[i:] += (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt)) * np.exp(-tt * 6) * np.minimum(1, tt / 0.004)
    tt = np.arange(n) / sr; out += 0.25 * np.sin(2 * np.pi * 2637 * tt) * np.sin(2 * np.pi * 9 * tt) * np.exp(-tt * 4) * np.minimum(1, tt / 0.05)
    return out / np.abs(out).max() * v
