"""Character voice FX on Enes's own TURKISH takes (26 Nov 2026: "seslerimle biraz da sen oynayabilirsin").
Enes reads every character himself, so the FX give each one its own body. Run AFTER `<mod>.py build own`:
  TTS_DIR=../renders/<proj>/tr_voice_tts python tools/tts/tr_fx.py <bt|ms|na|sp>
The first run copies the clean build to $TTS_DIR/<mod>_dry/ (kept as the 'kuru' version); every run reads from there, so it
can be re-run with new settings. Timing never changes: pitch keeps the length, script.json is untouched, reverb only adds a
short tail after the line (the mixer just places the file at the line's start time).
  bt  troll   : sub-octave shadow under his voice + stone slapback (he lives under a bridge); knight / narrator stay clean
  ms  shop    : the mimic's real voice (an octave down, muffled, wet) grows under the sweet one: 01 faint, 04 more, 07 clearly
      narrator: last line close and dry (the whisper)
  na  boss    : 'Diz çök, ölümlü!' (01 first sentence, 07) = huge throne-hall voice (octave double + big reverb), the rest a
                smaller hall; 08 the whisper stays close
  sp  keeper  : older and deeper (-2 st, warm), hero younger (+1 st): the two people Enes plays sound different"""
import os, sys, json, shutil, subprocess, tempfile
import numpy as np, soundfile as sf
from scipy.signal import fftconvolve, butter, sosfilt
HERE = os.path.dirname(os.path.abspath(__file__))
TTS_DIR = os.environ.get('TTS_DIR', os.path.join(HERE, '..', '..', 'tts'))
mod = sys.argv[1]
OUT = os.path.join(TTS_DIR, mod); DRY = os.path.join(TTS_DIR, mod + '_dry')
if not os.path.isdir(DRY):
    shutil.copytree(OUT, DRY); print('dry copy ->', DRY)
J = json.load(open(os.path.join(DRY, 'script.json'), encoding='utf-8')); SPK = J['spk']
TMP = tempfile.gettempdir()
def lp(x, sr, f, o=4): return sosfilt(butter(o, f, 'low', fs=sr, output='sos'), x)
def hp(x, sr, f, o=2): return sosfilt(butter(o, f, 'high', fs=sr, output='sos'), x)
def ff(x, sr, af):
    p = os.path.join(TMP, 'trfx_in.wav'); q = os.path.join(TMP, 'trfx_out.wav'); sf.write(p, x, sr)
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', p, '-af', af, '-ar', str(sr), '-ac', '1', q], check=True)
    y, _ = sf.read(q); y = y[:len(x)]; return np.pad(y, (0, len(x) - len(y)))
def pitch(x, sr, st, formant='shifted'): return ff(x, sr, f'rubberband=pitch={2 ** (st / 12):.5f}:formant={formant}')
def ir(sr, length, decay, seed, bright):
    r = np.random.default_rng(seed); t = np.arange(int(length * sr)) / sr; n = r.normal(0, 1, len(t)) * np.exp(-t * decay)
    n = lp(n, sr, bright); a = int(0.01 * sr); n[:a] *= np.linspace(0, 1, a); return n / np.sqrt(np.sum(n ** 2))
def reverb(x, sr, wet, length, decay, bright=5000, seed=1, tail=0.6):
    n = len(x) + int(tail * sr); y = np.pad(x, (0, n - len(x)))
    w = fftconvolve(y, ir(sr, length, decay, seed, bright))[:n]; w *= np.sqrt(np.mean(y ** 2)) / (np.sqrt(np.mean(w ** 2)) + 1e-12)
    out = y + wet * w; f = int(0.15 * sr); out[-f:] *= np.linspace(1, 0, f); return out
def slap(x, sr, ms, g):
    d = int(ms / 1000 * sr); y = np.pad(x, (0, d)); y[d:] += g * lp(x, sr, 3500); return y
def drive(x, k): pk = np.abs(x).max() + 1e-9; return np.tanh(k * x / pk) / np.tanh(k) * pk
def shadow(x, sr, st=-12, cut=900, g=0.2):
    """a darker copy of the voice under it (sub-octave), muffled"""
    s = lp(pitch(x, sr, st), sr, cut); return x + g * s * (np.sqrt(np.mean(x ** 2)) / (np.sqrt(np.mean(s ** 2)) + 1e-12))
def eq(x, sr, af): return ff(x, sr, af)
def proc(k, x, sr):
    s = SPK[k]; sent = J['sent'][k]
    if mod == 'bt':
        if s == 'T':
            x = shadow(x, sr, -12, 700, 0.22); x = drive(x, 1.8); x = eq(x, sr, 'equalizer=f=120:t=q:w=1:g=3,equalizer=f=2800:t=q:w=1.5:g=1.5')
            x = slap(x, sr, 85, 0.28); return reverb(x, sr, 0.22, 1.2, 4.0, 3500, 3, 0.5)
        if s == 'N': return eq(x, sr, 'equalizer=f=180:t=q:w=1:g=1.5,acompressor=threshold=-22dB:ratio=2.5:attack=8:release=150:makeup=2')
        return x
    if mod == 'ms':
        if s == 'S':
            g = {'01': 0.10, '04': 0.28, '07': 0.5}[k]
            dark = lp(pitch(x, sr, -12, 'shifted'), sr, 1100); dark = drive(dark, 2.5)
            d = int(0.025 * sr); dark = np.pad(dark, (d, 0))[:len(x)]                           # the real voice comes from a little deeper inside
            x = x + g * dark * (np.sqrt(np.mean(x ** 2)) / (np.sqrt(np.mean(dark ** 2)) + 1e-12))
            return reverb(x, sr, 0.12 + 0.2 * g, 0.9, 6.0, 2500, 5, 0.4)                            # small, wet room: the inside of a mouth
        if s == 'N' and k == '09': return eq(x, sr, 'equalizer=f=150:t=q:w=1:g=3,acompressor=threshold=-30dB:ratio=3:attack=5:release=120:makeup=4')
        if s == 'N': return reverb(x, sr, 0.1, 1.0, 5.0, 4000, 7, 0.4)
        return x
    if mod == 'na':
        if s == 'N': return x
        def big(y):
            y = shadow(y, sr, -12, 800, 0.3); y = drive(y, 2.0); y = slap(y, sr, 120, 0.25)
            return reverb(y, sr, 0.5, 2.8, 2.2, 4500, 11, 1.2)
        def hall(y): return reverb(y, sr, 0.22, 2.0, 3.0, 4500, 11, 0.7)
        if k == '07': return big(x)
        if k == '01':
            c = int((sent[0][1] + sent[1][0]) / 2 * sr); f = int(0.02 * sr)          # cut in the pause between the two sentences
            a = x.copy(); a[c:] = 0; a[c - f:c] *= np.linspace(1, 0, f); b = x - a       # the big part echoes on under 'Sıra sende'
            A = big(a); B = hall(b); n = max(len(A), len(B)); return np.pad(A, (0, n - len(A))) + np.pad(B, (0, n - len(B)))
        if k == '08': return eq(x, sr, 'equalizer=f=200:t=q:w=1:g=2,acompressor=threshold=-30dB:ratio=3:attack=5:release=120:makeup=4')
        return hall(x)
    if mod == 'sp':
        if s == 'B':
            x = pitch(x, sr, -2.0, 'shifted'); x = eq(x, sr, 'equalizer=f=160:t=q:w=1:g=2,lowpass=f=7500')
            return reverb(x, sr, 0.08, 0.8, 6.0, 3500, 13, 0.3)
        if s == 'K': return pitch(x, sr, 1.0, 'preserved')
        return x
    return x
for k in J['dur']:
    y, sr = sf.read(os.path.join(DRY, k + '.wav')); y = y if y.ndim == 1 else y.mean(1); n0 = len(y)
    z = proc(k, y, sr); z = z / (np.abs(z).max() + 1e-9) * 0.95
    sf.write(os.path.join(OUT, k + '.wav'), z, sr); print(mod, k, SPK[k], round(n0 / sr, 2), '->', round(len(z) / sr, 2), 's')
