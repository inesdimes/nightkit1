"""Misty valley pilot (7 s, 1080x1920, 24 fps), Blender 5.x + EEVEE, fully procedural.

No narration: image + sound effects only.

Run (Windows PowerShell, from repo root):
  $env:MODE='preview'; blender -b --factory-startup --python blender/misty_pilot.py   # 50 %, 16 samples
  $env:MODE='final';   blender -b --factory-startup --python blender/misty_pilot.py   # 100 %, 96 samples, motion blur
  $env:MODE='audio';   blender -b --factory-startup --python blender/misty_pilot.py   # writes sfx.wav
  $env:MODE='mux'; $env:SRC='preview'; blender -b --factory-startup --python blender/misty_pilot.py
  $env:MODE='still'; $env:FRAMES='1,84,168'  -> single test frames
Env: OUT (output folder), PCT, SAMPLES, FRAMES.
"""
import os, math, json, wave
import numpy as np

FPS = 24
NF = 168                       # 7.0 s
SR = 48000
MODE = os.environ.get('MODE', 'preview')
OUT = os.environ.get('OUT', os.path.join(os.path.expanduser('~'), 'Documents', 'blender-shorts',
                                         'renders', 'misty_pilot'))

# ---- shared timing (picture + sound) ------------------------------------------------
STROKE = 40                    # rowing cycle in frames
STROKE0 = 6                    # first oar catch
CATCHES = [f for f in range(STROKE0, NF + 1, STROKE)]
FISH_F = 100                   # fish jump / plop
CAW_F = [30, 44, 57, 79, 95]   # crow calls while the flock crosses
CREAK_F = 12                   # pier plank creak
BELL_F = 128                   # far bell across the water
FISH_POS = (4.5, 17.0)
BOAT_Y = 27.0


# ======================================================================================
#  numpy helpers (terrain)
# ======================================================================================
def _vnoise(x, y, seed, scale):
    g = np.random.default_rng(seed).uniform(-1, 1, (257, 257))
    xs, ys = x / scale, y / scale
    xi, yi = np.floor(xs).astype(np.int64), np.floor(ys).astype(np.int64)
    fx, fy = xs - xi, ys - yi
    u, v = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    xi %= 256
    yi %= 256
    a, b = g[xi, yi], g[xi + 1, yi]
    c, d = g[xi, yi + 1], g[xi + 1, yi + 1]
    return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v


def fbm(x, y, seed, scale, octaves=5):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    s, amp, tot = 0.0, 1.0, 0.0
    for i in range(octaves):
        s = s + amp * _vnoise(x + i * 37.1, y - i * 19.7, seed + i, scale / (2 ** i))
        tot += amp
        amp *= 0.5
    return s / tot


def sstep(a, b, t):
    x = np.clip((np.asarray(t, float) - a) / (b - a), 0, 1)
    return x * x * (3 - 2 * x)


def meander(y):
    return 12 * np.sin(np.asarray(y, float) / 90 + 0.5)


def height(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    yy = np.maximum(y, 0)
    half = 15 + 0.18 * yy
    d = np.maximum(np.abs(x - meander(y)) - half, 0)
    n = fbm(x, y, 3, 70)
    h = 0.05 * d ** 1.5 - 1.0 + n * (0.5 + 0.08 * d)
    h = h + sstep(200, 460, y) * (70 + 60 * fbm(x, y, 5, 180))
    h = h + sstep(-12, -28, y) * 5.0
    return h


# ======================================================================================
#  AUDIO (numpy only)
# ======================================================================================
def _ffilt(x, lo=None, hi=None, tilt=0.0):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = np.ones_like(f)
    fs = np.maximum(f, 1.0)
    if lo:
        g *= 1 / np.sqrt(1 + (lo / fs) ** 4)
    if hi:
        g *= 1 / np.sqrt(1 + (fs / hi) ** 4)
    if tilt:
        g *= (np.maximum(f, 20) / 1000.0) ** tilt
    return np.fft.irfft(X * g, len(x))


def _lfo(n, step_s, rng, lo=0.0, hi=1.0):
    pts = rng.uniform(lo, hi, int(n / (step_s * SR)) + 3)
    xp = np.arange(len(pts)) * step_s * SR
    v = np.interp(np.arange(n), xp, pts)
    k = int(step_s * SR / 2) | 1
    return np.convolve(v, np.ones(k) / k, mode='same')


def _norm(x):
    p = np.max(np.abs(x))
    return x / p if p > 0 else x


def _place(bus, sig, t0, gain, pan):
    """Add mono sig at time t0 (s) with equal-power pan (-1 left .. 1 right)."""
    i = int(t0 * SR)
    if i >= bus.shape[1]:
        return
    sig = sig[:bus.shape[1] - i]
    a = (pan + 1) * math.pi / 4
    bus[0, i:i + len(sig)] += sig * gain * math.cos(a)
    bus[1, i:i + len(sig)] += sig * gain * math.sin(a)


def build_audio(path):
    rng = np.random.default_rng(3)
    n = int(SR * NF / FPS)
    t = np.arange(n) / SR
    dry = np.zeros((2, n))
    wet = np.zeros((2, n))       # reverb send

    # wind bed: brown-ish noise, slow gusts, two decorrelated channels
    gust = 0.55 + 0.45 * _lfo(n, 0.9, rng)
    for ch in range(2):
        w = _norm(_ffilt(rng.standard_normal(n), lo=35, hi=900, tilt=-0.9))
        dry[ch] += w * gust * 0.22
    whistle = _norm(_ffilt(rng.standard_normal(n), lo=480, hi=760)) * _lfo(n, 1.3, rng, 0, 1) ** 2
    dry += whistle * 0.025

    # reeds rustle (high, follows the gusts)
    for ch in range(2):
        r = _norm(_ffilt(rng.standard_normal(n), lo=2600, hi=8500)) * (gust - 0.35).clip(0) ** 1.5
        dry[ch] += r * 0.05

    # water lapping against the pier posts
    tt = 0.15
    while tt < n / SR - 0.3:
        dur = rng.uniform(0.25, 0.5)
        m = int(dur * SR)
        env = np.minimum(np.arange(m) / (0.05 * SR), 1) * np.exp(-np.arange(m) / (0.12 * SR))
        s = _norm(_ffilt(rng.standard_normal(m), lo=180, hi=rng.uniform(700, 1300))) * env
        _place(dry, s, tt, rng.uniform(0.05, 0.10), rng.uniform(-0.5, 0.5))
        if rng.random() < 0.5:            # small cluck
            c = int(0.035 * SR)
            ck = _norm(_ffilt(rng.standard_normal(c), lo=500, hi=1600)) * np.hanning(c)
            _place(dry, ck, tt + rng.uniform(0.05, 0.2), 0.05, rng.uniform(-0.4, 0.4))
        tt += rng.uniform(0.45, 1.0)

    # crows: harsh harmonic caw through a formant band, distant
    for k, f in enumerate(CAW_F):
        for rep in range(rng.integers(1, 3) + (1 if k % 2 == 0 else 0)):
            dur = rng.uniform(0.26, 0.36)
            m = int(dur * SR)
            tl = np.arange(m) / SR
            f0 = rng.uniform(430, 560) * (1 + 0.12 * np.exp(-tl / 0.05)) * (1 - 0.1 * tl / dur)
            ph = 2 * np.pi * np.cumsum(f0 * (1 + 0.02 * rng.standard_normal(m))) / SR
            s = sum(np.sin(h * ph) / h ** 0.7 for h in range(1, 14))
            s = s + 0.6 * rng.standard_normal(m)
            s = _norm(_ffilt(s, lo=700, hi=2600))
            s *= np.minimum(tl / 0.02, 1) * np.exp(-np.maximum(tl - dur * 0.55, 0) / 0.05)
            s = _ffilt(s, hi=3200)
            pan = float(np.interp(f, [20, 110], [0.7, -0.7]))
            t0 = f / FPS + rep * rng.uniform(0.38, 0.5)
            _place(dry, s, t0, 0.11, pan)
            _place(wet, s, t0, 0.20, pan)

    # oars: dip splash at each catch, oarlock squeak at end of the drive
    for f in CATCHES:
        pan = float(np.interp(f, [1, NF], [0.4, 0.15]))
        m = int(0.35 * SR)
        tl = np.arange(m) / SR
        sp = _norm(_ffilt(rng.standard_normal(m), lo=300, hi=2800)) * np.exp(-tl / 0.07) * np.minimum(tl / 0.01, 1)
        _place(dry, sp, f / FPS, 0.05, pan)
        _place(wet, sp, f / FPS, 0.10, pan)
        m = int(0.16 * SR)
        tl = np.arange(m) / SR
        fq = np.linspace(rng.uniform(850, 950), rng.uniform(650, 720), m)
        ph = 2 * np.pi * np.cumsum(fq) / SR
        sq = (np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.2 * np.sin(3.1 * ph)) * np.hanning(m)
        _place(dry, _ffilt(sq, hi=2500), (f + 20) / FPS, 0.02, pan)
        _place(wet, sq, (f + 20) / FPS, 0.05, pan)

    # pier plank creak
    m = int(0.5 * SR)
    tl = np.arange(m) / SR
    rate = 35 + 40 * np.sin(np.pi * tl / 0.5)
    pulses = (np.sin(2 * np.pi * np.cumsum(rate) / SR) > 0.97).astype(float)
    cr = _norm(_ffilt(pulses + 0.02 * rng.standard_normal(m), lo=250, hi=1800)) * np.hanning(m)
    _place(dry, cr, CREAK_F / FPS, 0.12, -0.2)

    # fish plop: pitch drop + splash + droplets
    m = int(0.5 * SR)
    tl = np.arange(m) / SR
    fq = 180 + 520 * np.exp(-tl / 0.02)
    plop = np.sin(2 * np.pi * np.cumsum(fq) / SR) * np.exp(-tl / 0.05)
    spl = _norm(_ffilt(rng.standard_normal(m), lo=400, hi=4000)) * np.exp(-tl / 0.09) * 0.6
    fishs = plop + spl
    for _ in range(5):
        d0 = rng.uniform(0.12, 0.42)
        i0 = int(d0 * SR)
        k = int(0.03 * SR)
        fr = rng.uniform(1400, 3200)
        dr = np.sin(2 * np.pi * np.cumsum(np.linspace(fr, fr * 1.3, k)) / SR) * np.hanning(k) * 0.25
        fishs[i0:i0 + k] += dr[:max(0, min(k, m - i0))]
    _place(dry, fishs, FISH_F / FPS, 0.14, 0.2)
    _place(wet, fishs, FISH_F / FPS, 0.22, 0.2)

    # far bell across the water: inharmonic partials, long decay, only reverb + muffled dry
    m = int(3.0 * SR)
    tl = np.arange(m) / SR
    bell = sum(a * np.sin(2 * np.pi * 196 * r * tl) * np.exp(-tl / dcy)
               for r, a, dcy in [(0.5, 0.6, 2.5), (1, 1, 2.0), (1.19, 0.5, 1.4), (1.5, 0.4, 1.2),
                                 (2.0, 0.35, 0.9), (2.52, 0.2, 0.7), (3.0, 0.15, 0.5)])
    bell = _ffilt(bell * np.minimum(tl / 0.004, 1), hi=1400)
    _place(dry, bell, BELL_F / FPS, 0.035, -0.35)
    _place(wet, bell, BELL_F / FPS, 0.09, -0.35)

    # reverb: decaying stereo noise IR (wide, lakeside)
    irn = int(2.6 * SR)
    ti = np.arange(irn) / SR
    out = dry.copy()
    for ch in range(2):
        ir = _ffilt(rng.standard_normal(irn), hi=3500) * np.exp(-ti / 0.55)
        ir /= np.sqrt(np.sum(ir ** 2))
        L = n + irn
        conv = np.fft.irfft(np.fft.rfft(wet[ch], L) * np.fft.rfft(ir, L), L)[:n]
        out[ch] += conv * 0.9

    # fade in/out edges, level: RMS ~ -19 dBFS, peak <= -1.5 dBFS
    fade = np.minimum(np.minimum(t / 0.25, 1), np.minimum((n / SR - t) / 0.4, 1))
    out *= fade
    rms = np.sqrt(np.mean(out ** 2))
    peak = np.max(np.abs(out))
    out *= min(0.112 / rms, 0.84 / peak)
    rms = np.sqrt(np.mean(out ** 2))
    print('AUDIO rms dBFS %.1f peak dBFS %.1f' % (20 * np.log10(rms), 20 * np.log10(np.max(np.abs(out)))))
    pcm = (np.clip(out.T, -1, 1) * 32767).astype('<i2')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())


# ======================================================================================
#  SCENE (bpy)
# ======================================================================================
if MODE not in ('audio',):
    import bpy
    import bmesh
    from mathutils import Vector, Euler

    def setp(obj, attr, val):
        try:
            setattr(obj, attr, val)
        except Exception as e:      # API drift between Blender versions
            print('skip', attr, e)

    def link(ob):
        bpy.context.scene.collection.objects.link(ob)
        return ob

    def mesh_obj(name, verts, faces, mats=(), mat_idx=None, smooth=False):
        me = bpy.data.meshes.new(name)
        me.from_pydata(verts, [], faces)
        for m in mats:
            me.materials.append(m)
        if mat_idx is not None:
            me.polygons.foreach_set('material_index', np.asarray(mat_idx, np.int32))
        if smooth:
            me.polygons.foreach_set('use_smooth', np.ones(len(me.polygons), bool))
        me.update()
        return link(bpy.data.objects.new(name, me))

    # ---------------- materials ----------------
    def new_mat(name):
        m = bpy.data.materials.new(name)
        setp(m, 'use_nodes', True)
        nt = m.node_tree
        if nt is None:
            raise RuntimeError('material without node tree')
        return m, nt

    def principled(m, nt):
        p = nt.nodes.get('Principled BSDF')
        if p is None:
            p = nt.nodes.new('ShaderNodeBsdfPrincipled')
            out = nt.nodes.get('Material Output') or nt.nodes.new('ShaderNodeOutputMaterial')
            nt.links.new(p.outputs[0], out.inputs['Surface'])
        return p

    def mat_basic(name, color, rough=0.85, emit=None, estr=0.0, spec=0.5):
        m, nt = new_mat(name)
        p = principled(m, nt)
        p.inputs['Base Color'].default_value = (*color, 1)
        p.inputs['Roughness'].default_value = rough
        if 'Specular IOR Level' in p.inputs:
            p.inputs['Specular IOR Level'].default_value = spec
        if emit:
            p.inputs['Emission Color'].default_value = (*emit, 1)
            p.inputs['Emission Strength'].default_value = estr
        return m

    def mat_fade(name, color, rough=0.3, alpha_scale=1.0):
        """Alpha from Object Info colour alpha (per-object fade)."""
        m, nt = new_mat(name)
        p = principled(m, nt)
        p.inputs['Base Color'].default_value = (*color, 1)
        p.inputs['Roughness'].default_value = rough
        oi = nt.nodes.new('ShaderNodeObjectInfo')
        mul = nt.nodes.new('ShaderNodeMath')
        mul.operation = 'MULTIPLY'
        mul.inputs[1].default_value = alpha_scale
        nt.links.new(oi.outputs['Alpha'], mul.inputs[0])
        nt.links.new(mul.outputs[0], p.inputs['Alpha'])
        setp(m, 'surface_render_method', 'BLENDED')
        return m

    def mat_terrain():
        m, nt = new_mat('terrain')
        p = principled(m, nt)
        p.inputs['Roughness'].default_value = 0.95
        geo = nt.nodes.new('ShaderNodeNewGeometry')
        sep = nt.nodes.new('ShaderNodeSeparateXYZ')
        nt.links.new(geo.outputs['Position'], sep.inputs[0])
        mr = nt.nodes.new('ShaderNodeMapRange')
        mr.inputs['From Min'].default_value = -1.0
        mr.inputs['From Max'].default_value = 120.0
        nt.links.new(sep.outputs['Z'], mr.inputs['Value'])
        noi = nt.nodes.new('ShaderNodeTexNoise')
        noi.inputs['Scale'].default_value = 0.08
        add = nt.nodes.new('ShaderNodeMath')
        add.operation = 'MULTIPLY_ADD'
        nt.links.new(noi.outputs['Fac'], add.inputs[0])
        add.inputs[1].default_value = 0.08
        nt.links.new(mr.outputs['Result'], add.inputs[2])
        ramp = nt.nodes.new('ShaderNodeValToRGB')
        cr = ramp.color_ramp
        cr.elements[0].position = 0.0
        cr.elements[0].color = (0.05, 0.045, 0.035, 1)        # wet mud
        cr.elements[1].position = 0.05
        cr.elements[1].color = (0.06, 0.075, 0.045, 1)        # moss / grass
        e = cr.elements.new(0.45)
        e.color = (0.05, 0.06, 0.05, 1)
        e = cr.elements.new(0.75)
        e.color = (0.16, 0.16, 0.17, 1)                       # rock
        nt.links.new(add.outputs[0], ramp.inputs['Fac'])
        nt.links.new(ramp.outputs['Color'], p.inputs['Base Color'])
        return m

    def mat_water():
        m, nt = new_mat('water')
        p = principled(m, nt)
        p.inputs['Base Color'].default_value = (0.015, 0.02, 0.022, 1)
        p.inputs['Roughness'].default_value = 0.06
        tc = nt.nodes.new('ShaderNodeTexCoord')
        mp = nt.nodes.new('ShaderNodeMapping')
        mp.inputs['Scale'].default_value = (1.0, 2.2, 1.0)    # stretched ripples, perspective feel
        nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
        noi = nt.nodes.new('ShaderNodeTexNoise')
        noi.noise_dimensions = '4D'
        noi.inputs['Scale'].default_value = 0.9
        noi.inputs['Detail'].default_value = 4
        nt.links.new(mp.outputs[0], noi.inputs['Vector'])
        bump = nt.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = 0.08
        nt.links.new(noi.outputs['Fac'], bump.inputs['Height'])
        nt.links.new(bump.outputs['Normal'], p.inputs['Normal'])
        w = noi.inputs['W']
        for f in range(1, NF + 1):
            w.default_value = f * 0.012
            w.keyframe_insert('default_value', frame=f)
        return m

    def mat_volume(name, density, color=(0.85, 0.87, 0.9), aniso=0.4, ground=None, puff=False):
        m, nt = new_mat(name)
        for nd in list(nt.nodes):
            if nd.type == 'BSDF_PRINCIPLED':
                nt.nodes.remove(nd)
        out = nt.nodes.get('Material Output')
        pv = nt.nodes.new('ShaderNodeVolumePrincipled')
        pv.inputs['Color'].default_value = (*color, 1)
        pv.inputs['Anisotropy'].default_value = aniso
        nt.links.new(pv.outputs[0], out.inputs['Volume'])
        if ground is None and not puff:
            pv.inputs['Density'].default_value = density
            return m, nt
        geo = nt.nodes.new('ShaderNodeNewGeometry')
        mp = nt.nodes.new('ShaderNodeMapping')
        src = geo.outputs['Position']
        if puff:
            tc = nt.nodes.new('ShaderNodeTexCoord')
            src = tc.outputs['Object']
        nt.links.new(src, mp.inputs['Vector'])
        noi = nt.nodes.new('ShaderNodeTexNoise')
        noi.inputs['Scale'].default_value = 0.03 if not puff else 1.4
        noi.inputs['Detail'].default_value = 3
        nt.links.new(mp.outputs[0], noi.inputs['Vector'])
        nr = nt.nodes.new('ShaderNodeMapRange')
        nr.inputs['From Min'].default_value = 0.38
        nr.inputs['From Max'].default_value = 0.72
        nt.links.new(noi.outputs['Fac'], nr.inputs['Value'])
        if puff:
            # radial falloff * noise * object alpha
            ln = nt.nodes.new('ShaderNodeVectorMath')
            ln.operation = 'LENGTH'
            nt.links.new(tc.outputs['Object'], ln.inputs[0])
            fo = nt.nodes.new('ShaderNodeMapRange')
            fo.inputs['From Min'].default_value = 1.0
            fo.inputs['From Max'].default_value = 0.3
            nt.links.new(ln.outputs['Value'], fo.inputs['Value'])
            m1 = nt.nodes.new('ShaderNodeMath')
            m1.operation = 'MULTIPLY'
            nt.links.new(fo.outputs['Result'], m1.inputs[0])
            nt.links.new(nr.outputs['Result'], m1.inputs[1])
            oi = nt.nodes.new('ShaderNodeObjectInfo')
            m2 = nt.nodes.new('ShaderNodeMath')
            m2.operation = 'MULTIPLY'
            nt.links.new(m1.outputs[0], m2.inputs[0])
            nt.links.new(oi.outputs['Alpha'], m2.inputs[1])
            m3 = nt.nodes.new('ShaderNodeMath')
            m3.operation = 'MULTIPLY'
            m3.inputs[1].default_value = density
            nt.links.new(m2.outputs[0], m3.inputs[0])
            nt.links.new(m3.outputs[0], pv.inputs['Density'])
            return m, nt
        # ground fog: height falloff * drifting noise
        sep = nt.nodes.new('ShaderNodeSeparateXYZ')
        nt.links.new(geo.outputs['Position'], sep.inputs[0])
        hz = nt.nodes.new('ShaderNodeMapRange')
        hz.inputs['From Min'].default_value = ground[0]
        hz.inputs['From Max'].default_value = ground[1]
        hz.inputs['To Min'].default_value = 1.0
        hz.inputs['To Max'].default_value = 0.0
        nt.links.new(sep.outputs['Z'], hz.inputs['Value'])
        m1 = nt.nodes.new('ShaderNodeMath')
        m1.operation = 'MULTIPLY_ADD'
        nt.links.new(nr.outputs['Result'], m1.inputs[0])
        m1.inputs[1].default_value = 0.8
        m1.inputs[2].default_value = 0.25
        m2 = nt.nodes.new('ShaderNodeMath')
        m2.operation = 'MULTIPLY'
        nt.links.new(m1.outputs[0], m2.inputs[0])
        nt.links.new(hz.outputs['Result'], m2.inputs[1])
        m3 = nt.nodes.new('ShaderNodeMath')
        m3.operation = 'MULTIPLY'
        m3.inputs[1].default_value = density
        nt.links.new(m2.outputs[0], m3.inputs[0])
        nt.links.new(m3.outputs[0], pv.inputs['Density'])
        loc = mp.inputs['Location']
        for f in range(1, NF + 1):
            loc.default_value = (-f * 0.06, f * 0.02, 0)      # slow drift
            loc.keyframe_insert('default_value', frame=f)
        return m, nt

    # ---------------- per-frame animation helper ----------------
    def anim(ob, path, fn, frames=None):
        for f in (frames or range(1, NF + 1)):
            setattr(ob, path, fn(f))
            ob.keyframe_insert(path, frame=f)

    # ---------------- camera path ----------------
    CAM_A = Vector((-0.1, -5.5, 1.75))
    CAM_B = Vector((-0.45, -1.6, 1.95))
    TGT_A = Vector((1.8, 60, 3.2))
    TGT_B = Vector((0.6, 60, 4.0))

    def cam_at(f):
        t = (f - 1) / (NF - 1)
        e = 0.6 * t + 0.4 * t * t * (3 - 2 * t)
        p = CAM_A.lerp(CAM_B, e) + Vector((0.025 * math.sin(f * 0.07), 0, 0.018 * math.sin(f * 0.11 + 1)))
        return p, TGT_A.lerp(TGT_B, e)

    # ======================================================================================
    def build():
        sc = bpy.context.scene
        for ob in list(bpy.data.objects):
            bpy.data.objects.remove(ob)
        sc.frame_start, sc.frame_end = 1, NF
        sc.render.fps = FPS
        sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
        rng = np.random.default_rng(7)

        # ---------- world: pale sky gradient + sun glow + thin global haze ----------
        world = bpy.data.worlds.new('mist')
        sc.world = world
        setp(world, 'use_nodes', True)
        nt = world.node_tree
        bg = nt.nodes.get('Background')
        wout = nt.nodes.get('World Output')
        sun_dir = Vector((0.45, 0.8, 0.4)).normalized()   # towards the sun, low behind the far range
        tc = nt.nodes.new('ShaderNodeTexCoord')
        nrm = nt.nodes.new('ShaderNodeVectorMath')
        nrm.operation = 'NORMALIZE'
        nt.links.new(tc.outputs['Generated'], nrm.inputs[0])
        sep = nt.nodes.new('ShaderNodeSeparateXYZ')
        nt.links.new(nrm.outputs[0], sep.inputs[0])
        ramp = nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = 0.0
        ramp.color_ramp.elements[0].color = (0.62, 0.63, 0.64, 1)
        ramp.color_ramp.elements[1].position = 0.55
        ramp.color_ramp.elements[1].color = (0.30, 0.35, 0.42, 1)
        nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
        dot = nt.nodes.new('ShaderNodeVectorMath')
        dot.operation = 'DOT_PRODUCT'
        dot.inputs[1].default_value = tuple(sun_dir)
        nt.links.new(nrm.outputs[0], dot.inputs[0])
        pw = nt.nodes.new('ShaderNodeMath')
        pw.operation = 'POWER'
        pw.use_clamp = True
        pw.inputs[1].default_value = 24.0
        nt.links.new(dot.outputs['Value'], pw.inputs[0])
        glow = nt.nodes.new('ShaderNodeVectorMath')
        glow.operation = 'SCALE'
        glow.inputs[0].default_value = (1.0, 0.72, 0.5)
        nt.links.new(pw.outputs[0], glow.inputs['Scale'])
        addc = nt.nodes.new('ShaderNodeVectorMath')
        addc.operation = 'ADD'
        nt.links.new(ramp.outputs['Color'], addc.inputs[0])
        nt.links.new(glow.outputs[0], addc.inputs[1])
        nt.links.new(addc.outputs[0], bg.inputs['Color'])
        bg.inputs['Strength'].default_value = 1.0
        # NOTE: no world volume - since EEVEE 4.2 it is infinite and blocks sun + sky light.
        # The haze is a large volume box instead (built below).

        # ---------- sun ----------
        sd = bpy.data.lights.new('sun', 'SUN')
        sd.energy = 2.6
        sd.color = (1.0, 0.8, 0.62)
        setp(sd, 'angle', math.radians(3))
        sun = link(bpy.data.objects.new('sun', sd))
        sun.rotation_euler = (-sun_dir).to_track_quat('-Z', 'Y').to_euler()

        # ---------- terrain ----------
        ty = -40 + 860 * np.linspace(0, 1, 330) ** 1.55
        tx = np.linspace(-460, 460, 420)
        X, Y = np.meshgrid(tx, ty)
        Z = height(X, Y)
        ny, nx = X.shape
        idx = np.arange(nx * ny).reshape(ny, nx)
        faces = np.stack([idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel(),
                          idx[1:, 1:].ravel(), idx[1:, :-1].ravel()], 1)
        verts = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1)
        mesh_obj('terrain', verts.tolist(), faces.tolist(), [mat_terrain()], smooth=True)

        # ---------- water ----------
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 300, 0))
        water = bpy.context.active_object
        water.scale = (1000, 800, 1)
        water.data.materials.append(mat_water())

        # ---------- pines: one merged mesh ----------
        pine_mats = [mat_basic('needles', (0.018, 0.032, 0.026), 0.9), mat_basic('bark', (0.03, 0.022, 0.017), 0.9)]
        pts_x = rng.uniform(-430, 430, 26000)
        pts_y = -5 + 700 * rng.random(26000) ** 0.8
        ph = height(pts_x, pts_y)
        dens = fbm(pts_x, pts_y, 21, 90)
        keep = (ph > 0.5) & (ph < 230) & (dens > -0.15) & (rng.random(26000) < 0.55)
        # thin out trees far away (fog hides them; keeps the mesh small)
        keep &= rng.random(26000) < np.interp(pts_y, [0, 150, 700], [1.0, 0.6, 0.35])
        V, F, MI = [], [], []
        for x, y, z in zip(pts_x[keep], pts_y[keep], ph[keep]):
            H = rng.uniform(7, 15) * (1.0 + 0.3 * (y > 250))
            b = len(V)
            r = 0.012 * H
            for k in range(5):
                a = 2 * math.pi * k / 5
                V.append((x + r * math.cos(a), y + r * math.sin(a), z - 0.5))
                V.append((x + r * math.cos(a), y + r * math.sin(a), z + 0.35 * H))
            for k in range(5):
                k2 = (k + 1) % 5
                F.append((b + 2 * k, b + 2 * k2, b + 2 * k2 + 1, b + 2 * k + 1))
                MI.append(1)
            for tier in range(3):
                z0 = z + H * (0.18 + 0.22 * tier)
                z1 = z0 + H * (0.5 - 0.08 * tier) if tier < 2 else z + H
                rr = 0.24 * H * (1 - 0.27 * tier) * rng.uniform(0.85, 1.1)
                b = len(V)
                for k in range(7):
                    a = 2 * math.pi * k / 7 + tier
                    V.append((x + rr * math.cos(a), y + rr * math.sin(a), z0 + rng.uniform(-0.2, 0.2)))
                V.append((x, y, z1))
                for k in range(7):
                    F.append((b + k, b + (k + 1) % 7, b + 7))
                    MI.append(0)
        mesh_obj('pines', V, F, pine_mats, MI)
        print('pines', int(keep.sum()))

        # ---------- ground fog layer ----------
        fog_m, _ = mat_volume('groundfog', 0.016, ground=(0.0, 9.0))
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 300, 6))
        fog = bpy.context.active_object
        fog.name = 'groundfog'
        fog.scale = (900, 640, 14)
        fog.data.materials.append(fog_m)
        haze_m, _ = mat_volume('haze', float(os.environ.get('HAZE', 0.0013)), color=(0.74, 0.8, 0.9), aniso=0.55)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 380, 150))
        haze = bpy.context.active_object
        haze.name = 'haze'
        haze.scale = (1300, 900, 320)
        haze.data.materials.append(haze_m)
        setp(haze, 'display_type', 'BOUNDS')
        if os.environ.get('NOFOG'):
            fog.hide_render = True
            haze.hide_render = True
        setp(fog, 'display_type', 'BOUNDS')

        # ---------- pier ----------
        wood = mat_basic('wood', (0.075, 0.055, 0.04), 0.85)
        wood_dark = mat_basic('wood_dark', (0.035, 0.026, 0.02), 0.9)
        for i, y in enumerate(np.arange(-20, 6.01, 0.32)):
            bpy.ops.mesh.primitive_cube_add(size=1, location=(-1.5 + rng.uniform(-0.03, 0.03), y, 0.55))
            pl = bpy.context.active_object
            pl.scale = (1.7 + rng.uniform(-0.08, 0.05), 0.28, 0.05)
            pl.rotation_euler = (0, rng.uniform(-0.015, 0.015), rng.uniform(-0.02, 0.02))
            pl.data.materials.append(wood if i % 3 else wood_dark)
        for y in np.arange(-20, 6.1, 2.6):
            for x in (-2.32, -0.68):
                bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.09, depth=2.2,
                                                    location=(x, y, -0.45))
                po = bpy.context.active_object
                po.rotation_euler = (rng.uniform(-0.04, 0.04), rng.uniform(-0.04, 0.04), 0)
                po.data.materials.append(wood_dark)

        # ---------- seated figure + lantern at the end of the pier ----------
        cloak = mat_basic('cloak', (0.03, 0.03, 0.035), 0.95)
        skin = mat_basic('skin', (0.25, 0.17, 0.13), 0.7)
        def smooth_part(op, mat, **kw):
            op(**kw)
            o = bpy.context.active_object
            o.data.materials.append(mat)
            bpy.ops.object.shade_smooth()
            return o
        # hunched, hooded figure seen from behind: draped base, leaning torso, rounded shoulders
        smooth_part(bpy.ops.mesh.primitive_cone_add, cloak, vertices=24, radius1=0.4, radius2=0.3, depth=0.22,
                    location=(-1.55, 5.5, 0.69))
        body = smooth_part(bpy.ops.mesh.primitive_uv_sphere_add, cloak, segments=24, ring_count=12, radius=1.0,
                           location=(-1.55, 5.52, 0.98))
        body.scale = (0.3, 0.25, 0.4)
        body.rotation_euler = (math.radians(20), 0, 0)
        head = smooth_part(bpy.ops.mesh.primitive_uv_sphere_add, cloak, segments=16, ring_count=8, radius=0.11,
                           location=(-1.55, 5.66, 1.3))       # hooded, seen from behind, sunk into shoulders
        hood = smooth_part(bpy.ops.mesh.primitive_uv_sphere_add, cloak, segments=16, ring_count=8, radius=0.12,
                           location=(0, 0, 0))
        hood.parent = head
        hood.location = (0, -0.05, -0.01)
        hood.scale = (1.05, 1.35, 1.25)
        hood.rotation_euler = (math.radians(-35), 0, 0)
        for sx in (-1, 1):                       # legs dangling over the edge
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.07, depth=0.75,
                                                location=(-1.55 + 0.12 * sx, 6.2, 0.32))
            lg = bpy.context.active_object
            lg.rotation_euler = (math.radians(-25), 0, 0)
            lg.data.materials.append(cloak)
        # head turns towards the crows, then back; breathing
        def head_rot(f):
            look = sstep(38, 62, f) * (1 - sstep(105, 140, f))
            return (0, 0, math.radians(-28) * float(look))
        anim(head, 'rotation_euler', head_rot)
        anim(body, 'scale', lambda f: (0.3, 0.25, 0.4 * (1 + 0.015 * math.sin(f / FPS * 2 * math.pi / 4.2))))

        glass = mat_basic('lantern_glass', (1.0, 0.6, 0.3), 0.3, emit=(1.0, 0.5, 0.18), estr=4)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.92, 5.55, 0.72))
        lan = bpy.context.active_object
        lan.scale = (0.14, 0.14, 0.22)
        lan.data.materials.append(glass)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.92, 5.55, 0.86))
        cap = bpy.context.active_object
        cap.scale = (0.18, 0.18, 0.04)
        cap.data.materials.append(wood_dark)
        ld = bpy.data.lights.new('lantern', 'POINT')
        ld.color = (1.0, 0.55, 0.25)
        setp(ld, 'shadow_soft_size', 0.05)
        lamp = link(bpy.data.objects.new('lantern', ld))
        lamp.location = (-0.92, 5.55, 0.74)
        fl = 0.85 + 0.15 * _lfo(NF * 10, 0.012, np.random.default_rng(5))
        for f in range(1, NF + 1):
            ld.energy = 45 * float(fl[f * 10 - 5])
            ld.keyframe_insert('energy', frame=f)

        # ---------- reeds (foreground framing) ----------
        reed_m = mat_basic('reeds', (0.09, 0.08, 0.045), 0.85)
        clumps = [(-6.0, -3.0), (-4.2, 1.5), (-3.4, -6.5), (2.2, -5.5), (3.6, -1.0), (5.8, 3.5), (-7.5, 4.5), (1.8, 6.5)]
        for ci, (cx, cy) in enumerate(clumps):
            V, F = [], []
            for _ in range(int(rng.integers(40, 75))):
                bx, by = rng.normal(0, 0.55, 2)
                Hh = rng.uniform(1.0, 2.1)
                lean = rng.normal(0, 0.12, 2)
                w = rng.uniform(0.012, 0.025)
                ang = rng.uniform(0, math.pi)
                dx, dy = math.cos(ang) * w, math.sin(ang) * w
                b = len(V)
                seg = 5
                for s in range(seg + 1):
                    u = s / seg
                    px = bx + lean[0] * Hh * u * u
                    py = by + lean[1] * Hh * u * u
                    pz = -0.5 + Hh * u
                    k = 1 - u
                    V += [(px - dx * k, py - dy * k, pz), (px + dx * k, py + dy * k, pz)]
                for s in range(seg):
                    F.append((b + 2 * s, b + 2 * s + 1, b + 2 * s + 3, b + 2 * s + 2))
            ob = mesh_obj('reeds%d' % ci, V, F, [reed_m])
            ob.location = (cx, cy, 0)
            ph0 = rng.uniform(0, 6)
            amp = math.radians(rng.uniform(2.0, 3.5))
            anim(ob, 'rotation_euler', lambda f, ph0=ph0, amp=amp: (
                amp * math.sin(f * 0.09 + ph0) + 0.4 * amp * math.sin(f * 0.23 + 2 * ph0),
                -amp * 1.4 * (0.6 + 0.4 * math.sin(f * 0.05 + ph0)), 0))

        # ---------- rowing boat (midground) ----------
        boat_wood = mat_basic('boat', (0.06, 0.04, 0.03), 0.8)
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=18, v_segments=10, radius=1.0)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z > 0.02], context='VERTS')
        bmesh.ops.scale(bm, vec=(0.62, 1.75, 0.42), verts=bm.verts)
        me = bpy.data.meshes.new('hull')
        bm.to_mesh(me)
        bm.free()
        me.materials.append(boat_wood)
        hull = link(bpy.data.objects.new('boat', me))
        sol = hull.modifiers.new('sol', 'SOLIDIFY')
        sol.thickness = 0.04
        rower_parts = []
        bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.26, radius2=0.12, depth=0.62, location=(0, 0, 0))
        torso = bpy.context.active_object
        torso.data.materials.append(cloak)
        torso.parent = hull
        torso.location = (0, 0.1, 0.25)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=6, radius=0.12, location=(0, 0, 0))
        rh = bpy.context.active_object
        rh.data.materials.append(cloak)
        rh.parent = torso
        rh.location = (0, 0, 0.42)
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.16, depth=0.05, location=(0, 0, 0))
        hat = bpy.context.active_object
        hat.data.materials.append(cloak)
        hat.parent = rh
        hat.location = (0, 0, 0.1)
        oars = []
        for sx in (-1, 1):
            piv = link(bpy.data.objects.new('oarpiv', None))
            piv.parent = hull
            piv.location = (0.55 * sx, 0.05, 0.12)
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=2.4, location=(0, 0, 0))
            oar = bpy.context.active_object
            oar.data.materials.append(wood)
            oar.parent = piv
            oar.rotation_euler = (0, math.radians(90), 0)
            oar.location = (0.75 * sx, 0, 0)
            oars.append((piv, sx))

        def stroke_phase(f):
            return ((f - STROKE0) % STROKE) / STROKE

        def boat_x(f):
            # distance integrates a pulsing speed (faster just after each catch)
            ff = np.arange(1, f + 1)
            p = ((ff - STROKE0) % STROKE) / STROKE
            v = 0.022 + 0.03 * np.where(p < 0.5, np.sin(p * 2 * np.pi), 0) ** 2
            return 12.5 - float(v.sum())

        anim(hull, 'location', lambda f: (boat_x(f), BOAT_Y + 0.05 * math.sin(f * 0.05),
                                          -0.02 + 0.015 * math.sin(f * 0.21)))
        anim(hull, 'rotation_euler', lambda f: (0.012 * math.sin(f * 0.17), 0.02 * math.sin(f * 0.13),
                                                math.radians(90 + 6)))

        def oar_rot(sx):
            def fn(f):
                p = stroke_phase(f)
                if p < 0.5:      # drive: blade in water, sweeps back
                    yaw = -math.radians(40) + math.radians(80) * (p / 0.5)
                    pitch = math.radians(14)
                else:            # recovery: lifted, swings forward
                    q = (p - 0.5) / 0.5
                    yaw = math.radians(40) - math.radians(80) * (q * q * (3 - 2 * q))
                    pitch = math.radians(-6)
                return (0, sx * pitch, sx * yaw)
            return fn

        for piv, sx in oars:
            anim(piv, 'rotation_euler', oar_rot(sx))
        anim(torso, 'rotation_euler', lambda f: (
            math.radians(-18) + math.radians(36) * (stroke_phase(f) / 0.5 if stroke_phase(f) < 0.5
                                                     else 1 - (stroke_phase(f) - 0.5) / 0.5), 0, 0))

        # ---------- ripple rings (oar catches + fish) ----------
        ring_m = mat_fade('ripple', (0.7, 0.72, 0.75), 0.15, 0.55)

        def ripple(x, y, f0, life=60, rmax=2.5):
            bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.03, major_segments=40,
                                             minor_segments=4, location=(x, y, 0.01))
            r = bpy.context.active_object
            r.data.materials.append(ring_m)
            r.scale = (1, 1, 0.2)
            frames = range(max(1, f0 - 1), min(NF, f0 + life) + 1)
            for f in frames:
                u = max(0.0, (f - f0) / life)
                s = 0.05 + rmax * (1 - (1 - u) ** 2)
                r.scale = (s, s, 0.2)
                r.color = (1, 1, 1, 0.0 if f < f0 else (1 - u) ** 1.5)
                r.keyframe_insert('scale', frame=f)
                r.keyframe_insert('color', frame=f)
            if f0 > 2:
                r.color = (1, 1, 1, 0)
                r.keyframe_insert('color', frame=1)

        for f in CATCHES:
            bx = boat_x(f)
            for sx in (-1, 1):
                ripple(bx + 0.2, BOAT_Y + 1.6 * sx, f, life=45, rmax=1.4)
        for k in range(3):
            ripple(FISH_POS[0], FISH_POS[1], FISH_F + k * 7, life=65, rmax=3.2 - 0.6 * k)
        # fish: dark arc leaping out and back in just before the plop
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=6, radius=0.1)
        fish = bpy.context.active_object
        fish.scale = (0.35, 1.0, 0.3)
        fish.data.materials.append(mat_basic('fish', (0.12, 0.13, 0.13), 0.25))

        def fish_loc(f):
            u = (f - (FISH_F - 9)) / 9.0
            if u < 0 or u > 1:
                return (FISH_POS[0], FISH_POS[1], -0.5)
            return (FISH_POS[0], FISH_POS[1] - 0.6 + 0.6 * u, 0.55 * math.sin(math.pi * u))
        anim(fish, 'location', fish_loc)
        anim(fish, 'rotation_euler', lambda f: (math.radians(60) - math.radians(120) *
                                                min(max((f - (FISH_F - 9)) / 9.0, 0), 1), 0, 0))

        # ---------- crows crossing the valley ----------
        crow_m = mat_basic('crow', (0.012, 0.012, 0.014), 0.9)
        for i in range(17):
            V = [(0, 0.3, 0), (0, -0.28, 0), (-0.08, 0.06, 0), (0.08, 0.06, 0), (-0.55, -0.1, 0),
                 (0.55, -0.1, 0), (-0.09, -0.38, 0), (0.09, -0.38, 0)]
            Fc = [(0, 2, 1), (0, 1, 3), (2, 4, 1), (3, 1, 5), (1, 6, 7)]
            ob = mesh_obj('crow%d' % i, V, Fc, [crow_m])
            ob.shape_key_add(name='Basis')
            up = ob.shape_key_add(name='up')
            up.data[4].co = (-0.42, -0.12, 0.38)
            up.data[5].co = (0.42, -0.12, 0.38)
            dn = ob.shape_key_add(name='down')
            dn.data[4].co = (-0.45, -0.05, -0.36)
            dn.data[5].co = (0.45, -0.05, -0.36)
            y = rng.uniform(32, 85)
            z = rng.uniform(13, 27) + (y - 32) * 0.12
            x0 = rng.uniform(38, 62) * (y / 55)
            x1 = -rng.uniform(40, 60) * (y / 55)
            fA = int(rng.uniform(8, 30))
            fB = fA + int(rng.uniform(95, 125))
            fq = rng.uniform(3.6, 4.6)
            phs = rng.uniform(0, 6.3)
            sz = rng.uniform(0.85, 1.15)
            ob.scale = (sz, sz, sz)

            def loc(f, x0=x0, x1=x1, y=y, z=z, fA=fA, fB=fB, phs=phs):
                u = (f - fA) / (fB - fA)
                return (x0 + (x1 - x0) * u, y + 3 * math.sin(u * 3 + phs), z + 0.6 * math.sin(f * 0.15 + phs))
            anim(ob, 'location', loc)
            anim(ob, 'rotation_euler', lambda f, phs=phs: (0.05 * math.sin(f * 0.1 + phs),
                                                           0.15 * math.sin(f * 0.07 + phs), math.radians(90)))
            for f in range(1, NF + 1):
                tt = f / FPS
                glide = 0.5 + 0.5 * math.sin(tt * 1.1 + phs)
                a = 1.0 if glide > 0.35 else 0.25
                s = math.sin(2 * math.pi * fq * tt + phs) * a
                up.value, dn.value = max(s, 0), max(-s, 0)
                up.keyframe_insert('value', frame=f)
                dn.keyframe_insert('value', frame=f)

        # ---------- cabin with lit windows + chimney smoke (left shore) ----------
        cy = 112.0
        xs = np.linspace(meander(cy) - 15 - 0.18 * cy, -200, 400)
        hh = height(xs, np.full_like(xs, cy))
        cx = float(xs[np.argmax(hh > 0.9)])
        cz = float(height(cx, cy))
        print('cabin', cx, cy, cz)
        walls = mat_basic('cabin', (0.07, 0.055, 0.045), 0.9)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, cz + 1.1))
        cab = bpy.context.active_object
        cab.scale = (5.0, 3.8, 3.0)
        cab.rotation_euler = (0, 0, math.radians(18))
        cab.data.materials.append(walls)
        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=3.9, depth=2.0, location=(cx, cy, cz + 3.6))
        roof = bpy.context.active_object
        roof.scale = (1.0, 0.75, 1)
        roof.rotation_euler = (0, 0, math.radians(18 + 45))
        roof.data.materials.append(wood_dark)
        win = mat_basic('window', (1, 0.6, 0.3), 0.5, emit=(1.0, 0.58, 0.25), estr=25)
        rot = math.radians(18)
        for off in (-1.3, 1.1):
            wx = cx + off * math.cos(rot) - (-1.93) * math.sin(rot)
            wy = cy + off * math.sin(rot) + (-1.93) * math.cos(rot)
            bpy.ops.mesh.primitive_plane_add(size=1, location=(wx, wy, cz + 1.1))
            w = bpy.context.active_object
            w.rotation_euler = (math.radians(90), 0, rot)
            w.scale = (0.75, 0.7, 1)
            w.data.materials.append(win)
        wl = bpy.data.lights.new('cabinlight', 'POINT')
        wl.energy = 900
        wl.color = (1.0, 0.55, 0.25)
        wlo = link(bpy.data.objects.new('cabinlight', wl))
        wlo.location = (cx - 2.6 * math.sin(-rot), cy - 2.6 * math.cos(rot), cz + 1.3)
        chx, chy, chz = cx + 1.4, cy + 0.6, cz + 4.6
        bpy.ops.mesh.primitive_cube_add(size=1, location=(chx, chy, chz - 0.6))
        ch = bpy.context.active_object
        ch.scale = (0.6, 0.6, 1.8)
        ch.data.materials.append(wood_dark)
        smoke_m, _ = mat_volume('smoke', 3.0, color=(0.75, 0.76, 0.78), aniso=0.3, puff=True)
        T = 120
        for k in range(14):
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0, location=(chx, chy, chz))
            pf = bpy.context.active_object
            pf.data.materials.append(smoke_m)
            setp(pf, 'display_type', 'WIRE')
            off = k * T / 14
            for f in range(1, NF + 1):
                u = ((f + off) % T) / T
                pf.location = (chx + 6.0 * u ** 1.4 + 0.4 * math.sin(u * 9 + k),
                               chy + 1.5 * u, chz + 0.3 + 7.0 * u ** 0.8)
                s = 0.5 + 2.6 * u
                pf.scale = (s, s, s * 0.8)
                pf.color = (1, 1, 1, float(min(u / 0.08, 1) * (1 - u) ** 1.3))
                pf.keyframe_insert('location', frame=f)
                pf.keyframe_insert('scale', frame=f)
                pf.keyframe_insert('color', frame=f)

        # ---------- far lights across the water (a village waking up) ----------
        dot_m = mat_basic('farlight', (1, 0.6, 0.3), 0.5, emit=(1.0, 0.62, 0.3), estr=60)
        for k in range(6):
            yy = rng.uniform(120, 190)
            sxx = meander(yy) + 15 + 0.18 * yy + rng.uniform(3, 14)
            zz = float(height(sxx, yy)) + 1.2
            bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=4, radius=0.35, location=(sxx, yy, zz))
            bpy.context.active_object.data.materials.append(dot_m)

        # ---------- falling leaves (camera-relative so they cross the frame) ----------
        leaf_ms = [mat_basic('leaf_a', (0.16, 0.06, 0.02), 0.6), mat_basic('leaf_b', (0.2, 0.11, 0.03), 0.6),
                   mat_basic('leaf_c', (0.1, 0.045, 0.02), 0.6)]
        for i in range(9):
            V = [(0, 0.055, 0), (0.022, 0.012, 0.005), (0, -0.05, 0), (-0.022, 0.012, 0.005), (0, 0.0, -0.004)]
            Fl = [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)]
            ob = mesh_obj('leaf%d' % i, V, Fl, [leaf_ms[i % 3]])
            if i == 0:
                fA, dist, sx = -10, 1.5, 0.25      # already in frame at frame 1, close to the lens
            else:
                fA, dist, sx = int(rng.uniform(-60, 150)), rng.uniform(1.2, 3.5), rng.uniform(-0.9, 0.9)
            life = int(rng.uniform(70, 110)) if i else 60
            ph = rng.uniform(0, 6.3)
            spin = rng.uniform(0.1, 0.3, 3)

            def lloc(f, fA=fA, dist=dist, sx=sx, life=life, ph=ph):
                p, tg = cam_at(f)
                fwd = (tg - p).normalized()
                right = fwd.cross(Vector((0, 0, 1))).normalized()
                upv = right.cross(fwd)
                u = (f - fA) / life
                half_v = dist * math.tan(math.radians(36))
                half_h = dist * math.tan(math.radians(21))
                hgt = half_v * (1.3 - 2.6 * u)
                side = half_h * (sx + 0.35 * math.sin(u * 7 + ph) - 0.6 * u)
                q = p + fwd * dist + right * side + upv * hgt
                if q.z < 0.012:
                    q.z = 0.012
                return tuple(q)
            anim(ob, 'location', lloc)
            anim(ob, 'rotation_euler', lambda f, s=spin, ph=ph: (f * s[0] + ph, f * s[1], f * s[2] + ph))

        # ---------- camera ----------
        cd = bpy.data.cameras.new('cam')
        cd.lens = 24
        setp(cd, 'sensor_fit', 'AUTO')
        cd.clip_start = 0.05
        cd.clip_end = 2000
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = 2.8
        cam = link(bpy.data.objects.new('cam', cd))
        sc.camera = cam
        for f in range(1, NF + 1):
            p, tg = cam_at(f)
            cam.location = p
            cam.rotation_euler = (tg - p).to_track_quat('-Z', 'Y').to_euler()
            cd.dof.focus_distance = (Vector((-1.55, 5.45, 1.0)) - p).length
            cam.keyframe_insert('location', frame=f)
            cam.keyframe_insert('rotation_euler', frame=f)
            cd.dof.keyframe_insert('focus_distance', frame=f)

        # ---------- render settings ----------
        sc.render.engine = 'BLENDER_EEVEE'
        ee = sc.eevee
        setp(ee, 'use_raytracing', bool(os.environ.get('RT')))
        setp(ee, 'volumetric_tile_size', '4')
        setp(ee, 'volumetric_samples', 96)
        setp(ee, 'volumetric_start', 0.3)
        setp(ee, 'volumetric_end', 750.0)
        setp(ee, 'volumetric_sample_distribution', 0.9)
        setp(ee, 'use_volumetric_shadows', True)
        setp(ee, 'use_shadows', True)
        vs = sc.view_settings
        setp(vs, 'view_transform', 'AgX')
        looks = [i.identifier for i in vs.bl_rna.properties['look'].enum_items]
        for want in ('AgX - Medium Low Contrast', 'AgX - Base Contrast', 'Medium Low Contrast'):
            if want in looks:
                vs.look = want
                break
        vs.exposure = -0.25
        sc.render.image_settings.file_format = 'PNG'
        sc.render.image_settings.color_mode = 'RGB'
        return sc

    def configure(sc, pct, samples, blur):
        sc.render.resolution_percentage = pct
        setp(sc.eevee, 'taa_render_samples', samples)
        setp(sc.render, 'use_motion_blur', blur)
        if pct < 100:
            setp(sc.eevee, 'volumetric_tile_size', '8')

    def mux(src):
        frames_dir = os.path.join(OUT, src)
        files = sorted(f for f in os.listdir(frames_dir) if f.endswith('.png'))
        wav = os.path.join(OUT, 'sfx.wav')
        sc = bpy.context.scene
        sc.sequence_editor_create()
        se = sc.sequence_editor
        strips = se.strips if hasattr(se, 'strips') else se.sequences
        s = strips.new_image('img', os.path.join(frames_dir, files[0]), 1, 1)
        for f in files[1:]:
            s.elements.append(f)
        strips.new_sound('sfx', wav, 2, 1)
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
        setp(r.ffmpeg, 'constant_rate_factor', 'HIGH' if src == 'preview' else 'PERC_LOSSLESS')
        r.ffmpeg.audio_codec = 'AAC'
        r.ffmpeg.audio_bitrate = 192
        r.ffmpeg.audio_mixrate = 48000
        setp(r.ffmpeg, 'audio_channels', 'STEREO')
        r.use_sequencer = True
        r.filepath = os.path.join(OUT, 'misty_pilot_%s_' % src)
        bpy.ops.render.render(animation=True)
        print('MUX done', OUT)

    # ======================================================================================
    if MODE == 'mux':
        mux(os.environ.get('SRC', 'preview'))
    else:
        sc = build()
        os.makedirs(OUT, exist_ok=True)
        frames = os.environ.get('FRAMES')
        if MODE == 'final':
            configure(sc, int(os.environ.get('PCT', 100)), int(os.environ.get('SAMPLES', 96)), True)
            sub = 'final'
        elif MODE == 'still':
            configure(sc, int(os.environ.get('PCT', 50)), int(os.environ.get('SAMPLES', 16)), False)
            sub = 'stills'
        else:
            configure(sc, int(os.environ.get('PCT', 50)), int(os.environ.get('SAMPLES', 16)), False)
            sub = 'preview'
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'misty_pilot.blend'))
        d = os.path.join(OUT, sub)
        os.makedirs(d, exist_ok=True)
        if frames:
            if '-' in frames:
                a, b = map(int, frames.split('-'))
                todo = range(a, b + 1)
            else:
                todo = [int(x) for x in frames.split(',')]
            for f in todo:
                sc.frame_set(f)
                sc.render.filepath = os.path.join(d, 'f_%04d.png' % f)
                bpy.ops.render.render(write_still=True)
        else:
            sc.render.filepath = os.path.join(d, 'f_')
            bpy.ops.render.render(animation=True)
        print('RENDER done', d)
else:
    build_audio(os.path.join(OUT, 'sfx.wav'))
