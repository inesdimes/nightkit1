"""Step 6 (audio): everything synthesized in numpy, 44.1 kHz stereo, no samples, no models, no network.
  music   one 4-bar minor loop at 92 BPM (low pulse bass, detuned saw-ish lead, soft noise hat on every beat); muted for the last 2 s of the extended cut
  ambience a continuous torch crackle that runs from frame 0 to the last frame (nothing is ever silent)
  sfx     bow_creak, release, arrow_whoosh, arrow_thud, miss_blip, duck_step, footstep, crate_set, pat, ui_ding (placed at the frames of timeline.audio_events)
  narration is an OPTIONAL step (offline espeak-ng only); if none is installed nothing is faked and a line->frame TODO goes into NOTES.md
Loudness: the mix is measured with ffmpeg's ebur128 (a subprocess, no extra dependency) and scaled to -16 LUFS integrated, peaks < -1 dBFS."""
import math, os, re, shutil, subprocess, wave
import numpy as np
import timeline as T

SR = 44100; FPS = 24

def spf(): return SR / FPS
def at(frame): return int(round(frame * SR / FPS))

def fft_filter(x, lo=None, hi=None):
    """zero-phase band-pass / low-pass / high-pass by FFT masking (numpy only)"""
    n = len(x); X = np.fft.rfft(x); fr = np.fft.rfftfreq(n, 1 / SR); m = np.ones_like(fr)
    if lo: m *= fr >= lo
    if hi: m *= fr <= hi
    return np.fft.irfft(X * m, n)

def noise(n, seed): return np.random.default_rng(seed).standard_normal(n)
def env_bump(n, a=0.02, power=1.5):
    t = np.linspace(0, 1, n); return np.minimum(1, t / max(a, 1e-6)) * (1 - t) ** power
def tt(d): return np.arange(int(d * SR)) / SR

# ----------------------------------------------------------------------------- sfx
def sfx_bow_creak():
    n = int(0.35 * SR); t = np.arange(n) / SR; f = 140 + 90 * np.sin(2 * np.pi * 3.0 * t) - 60 * t / 0.35; ph = np.cumsum(f) / SR
    x = np.sign(np.sin(2 * np.pi * ph)) * 0.35 + fft_filter(noise(n, 1), 200, 1400) * 0.9
    return fft_filter(x, 90, 1800) * np.sin(np.pi * np.arange(n) / n) ** 0.8 * 0.5
def sfx_release():
    n = int(0.12 * SR); t = np.arange(n) / SR; f = 900 - 5000 * t; sq = np.sign(np.sin(2 * np.pi * np.cumsum(np.maximum(f, 220)) / SR))
    x = sq * np.exp(-t * 30) * 0.4; x[:60] += np.linspace(1, 0, 60) * 0.9; return x
def sfx_arrow_whoosh():
    n = int(0.25 * SR); return fft_filter(noise(n, 2), 1400, 5200) * np.sin(np.pi * np.arange(n) / n) ** 1.2 * 0.5
def sfx_arrow_thud():
    n = int(0.15 * SR); t = np.arange(n) / SR; x = np.sin(2 * np.pi * np.cumsum(130 - 400 * t) / SR) * np.exp(-t * 28) + fft_filter(noise(n, 3), 300, 1600) * np.exp(-t * 60) * 0.6
    return x * 0.9
def sfx_miss_blip():
    a = tt(0.09); b = tt(0.09)
    n1 = np.sign(np.sin(2 * np.pi * np.cumsum(440 + 1600 * a) / SR)) * np.exp(-a * 8); n2 = np.sign(np.sin(2 * np.pi * np.cumsum(587 - 2100 * b) / SR)) * np.exp(-b * 9)
    return np.concatenate([n1, n2]) * 0.3
def sfx_duck_step():
    n = int(0.10 * SR); return fft_filter(noise(n, 4), 80, 700) * env_bump(n, 0.05, 2.0) * 0.8
def sfx_footstep(i=0):
    n = int(0.06 * SR); return fft_filter(noise(n, 10 + i % 3), 100, 1100) * env_bump(n, 0.03, 2.0) * 0.6
def _knock(f0, d=0.1, seed=0):
    n = int(d * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * f0 * t) * np.exp(-t * 38) + fft_filter(noise(n, seed), 400, 2400) * np.exp(-t * 90) * 0.4)
def sfx_crate_set():
    out = np.zeros(int(0.20 * SR)); a = _knock(190, 0.1, 5); b = _knock(165, 0.1, 6); out[:len(a)] += a; k = int(0.09 * SR); out[k:k + len(b)] += b * 0.85; return out * 0.8
def sfx_pat():
    n = int(0.06 * SR); return _knock(900, 0.06, 7) * 0.5
def sfx_ui_ding():
    t = tt(0.25); return (np.sin(2 * np.pi * 1568 * t) + 0.3 * np.sin(2 * np.pi * 3136 * t)) * np.exp(-t * 11) * 0.35

def sfx_for(name, i=0):
    return {'bow_creak': sfx_bow_creak, 'release': sfx_release, 'arrow_whoosh': sfx_arrow_whoosh, 'arrow_thud': sfx_arrow_thud, 'miss_blip': sfx_miss_blip, 'duck_step': sfx_duck_step,
            'crate_set': sfx_crate_set, 'pat': sfx_pat, 'ui_ding': sfx_ui_ding}.get(name, lambda: sfx_footstep(i))()

# ----------------------------------------------------------------------------- music + ambience
def music_loop():
    beat = 60.0 / 92.0; bars = 4; n = int(round(bars * 4 * beat * SR)); out = np.zeros(n)
    bass = [45, 45, 52, 43, 41, 41, 48, 40]           # A2 A2 E3 G2 | F2 F2 C3 E2 per 2 beats  (A minor)
    lead = [69, 72, 76, 72, 74, 72, 69, 67, 65, 69, 72, 69, 71, 68, 64, 0]   # A4 C5 E5 ... a slow minor figure
    def hz(m): return 440.0 * 2 ** ((m - 69) / 12)
    for i, m in enumerate(bass):                      # low pulse bass: a pulse wave on every second beat
        i0 = int(i * 2 * beat * SR); d = int(beat * 1.6 * SR); t = np.arange(d) / SR; sq = np.where(((hz(m) * t) % 1) < 0.35, 1.0, -1.0)
        e = np.minimum(1, t / 0.01) * np.exp(-t * 3.2); out[i0:i0 + d] += (sq * e * 0.22)[:max(0, min(d, n - i0))]
    for i, m in enumerate(lead):                      # detuned saw-ish lead: two saws +-7 cents, a half-beat grid
        if not m: continue
        i0 = int(i * beat * SR); d = int(beat * 0.9 * SR); t = np.arange(d) / SR; f1, f2 = hz(m) * 2 ** (7 / 1200), hz(m) * 2 ** (-7 / 1200)
        saw = (2 * ((f1 * t) % 1) - 1) + (2 * ((f2 * t) % 1) - 1); e = np.minimum(1, t / 0.02) * np.exp(-t * 2.6); out[i0:i0 + d] += (saw * e * 0.07)[:max(0, min(d, n - i0))]
    for b in range(bars * 4):                         # a soft noise hat on every beat
        i0 = int(b * beat * SR); d = int(0.05 * SR); h = fft_filter(noise(d, 100 + b), 5000, 12000) * np.exp(-np.arange(d) / SR * 70) * 0.07; out[i0:i0 + d] += h[:max(0, min(d, n - i0))]
    return out

def ambience(n_samples, seed=21):
    """torch crackle: filtered noise with a slow amplitude wobble plus seeded pops. stereo, never silent"""
    rng = np.random.default_rng(seed); chans = []
    for c in range(2):
        base = fft_filter(rng.standard_normal(n_samples), 600, 7000); t = np.arange(n_samples) / SR
        wob = 0.55 + 0.25 * np.sin(2 * np.pi * 0.37 * t + c) + 0.2 * np.sin(2 * np.pi * 0.91 * t + 1.7 * c)
        x = base * 0.035 * wob + fft_filter(rng.standard_normal(n_samples), 30, 220) * 0.03
        for _ in range(int(n_samples / SR * 7)):                              # pops
            i = int(rng.integers(0, n_samples - 400)); L = int(rng.integers(60, 360)); x[i:i + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 4)) * 0.1 * rng.random()
        chans.append(x)
    return np.stack(chans, 1)

# ----------------------------------------------------------------------------- loudness helpers (ffmpeg ebur128 as a subprocess)
def write_wav(path, x):
    pcm = (np.clip(x, -1, 1) * 32767).astype('<i2'); w = wave.open(path, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes()); w.close()

def measure_lufs(path):
    r = subprocess.run(['ffmpeg', '-nostats', '-hide_banner', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True)
    m = re.findall(r'I:\s+(-?[0-9.]+|-inf)\s+LUFS', r.stderr); return float(m[-1]) if m and m[-1] != '-inf' else -70.0

# ----------------------------------------------------------------------------- narration (optional, offline only)
def narration_lines(cut): return [(t0, text) for t0, t1, text, _ in T.CUTS[cut]['subs']]

def try_narration(cut, n_samples, outdir):
    """renders each subtitle line with a LOCAL offline TTS binary (espeak-ng) when one exists. returns (stem or None, note). Never uses a cloud or downloads a voice."""
    exe = shutil.which('espeak-ng') or shutil.which('espeak')
    if not exe: return None, 'no offline TTS binary (espeak-ng / espeak) found: narration skipped'
    stem = np.zeros(n_samples)
    for k, (t0, text) in enumerate(narration_lines(cut)):
        p = os.path.join(outdir, f'tts_{cut}_{k}.wav'); subprocess.run([exe, '-w', p, text], check=True, capture_output=True)
        w = wave.open(p, 'rb'); raw = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(float) / 32768; sr = w.getframerate(); w.close()
        if sr != SR: raw = np.interp(np.arange(int(len(raw) * SR / sr)) / SR, np.arange(len(raw)) / sr, raw)                    # sample-rate conversion only, no time-stretch
        i = at(t0); j = min(n_samples, i + len(raw)); stem[i:j] += raw[:j - i]
    return stem, f'narration rendered with {os.path.basename(exe)}'

def soft_limit(y, knee=0.6, ceil=0.88):
    """transparent below the knee, a tanh shoulder above it: the output never exceeds `ceil` (0.88 = -1.1 dBFS)"""
    a = np.abs(y); over = a > knee; out = y.copy(); out[over] = np.sign(y[over]) * (knee + (ceil - knee) * np.tanh((a[over] - knee) / (ceil - knee))); return out

# ----------------------------------------------------------------------------- the mix
def build_audio(cut, path, workdir):
    C = T.CUTS[cut]; n = at(C['frames']); mute_from = at(C['frames'] - 48) if cut == 'extended' else n          # music off for the last 2 s of the extended button
    loop = music_loop(); m = np.tile(loop, int(math.ceil(n / len(loop))))[:n]; m = m.copy()
    k = int(0.05 * SR); m[mute_from:] = 0
    if mute_from < n: m[mute_from - k:mute_from] *= np.linspace(1, 0, k)                                         # click-free
    amb = ambience(n)
    sfx = np.zeros((n, 2))
    for i, (name, fr) in enumerate(T.audio_events(cut)):
        x = sfx_for(name, i); i0 = at(max(0, fr)); j = min(n, i0 + len(x))
        if j > i0: pan = 0.0 if name != 'footstep' else (-0.15 if (i % 2) else 0.15); sfx[i0:j, 0] += x[:j - i0] * (1 - pan) ; sfx[i0:j, 1] += x[:j - i0] * (1 + pan)
    bed = amb + sfx
    rms = lambda a: float(np.sqrt((a[a != 0] ** 2).mean())) if (a != 0).any() else 1.0
    mus = np.stack([m, np.roll(m, 40)], 1); mus *= 0.5 * rms(bed) / max(rms(mus), 1e-9)                            # the music sits ~6 dB under the bed (the brief's "-22 LUFS relative to the mix")
    mix = bed + mus
    narr, note = try_narration(cut, n, workdir)
    if narr is not None: mix = mix + np.stack([narr, narr], 1) * 0.6 * rms(mix) / max(rms(np.stack([narr, narr], 1)), 1e-9)
    tmp = os.path.join(workdir, f'_{cut}_tmp.wav'); log = []
    gain = 1.0
    for it in range(4):                                       # measure, scale to -16 LUFS, soft-limit under -1 dBFS, re-measure
        y = soft_limit(mix * gain)
        write_wav(tmp, y); lu = measure_lufs(tmp); log.append(lu)
        if abs(lu + 16) < 0.3: break
        gain *= 10 ** ((-16 - lu) / 20)
    peak = float(np.abs(y).max()); write_wav(path, y); os.remove(tmp)
    return dict(lufs=lu, peak_db=20 * math.log10(max(peak, 1e-9)), iterations=log, narration=note, samples=n)
