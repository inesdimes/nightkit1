"""Insert Disc 2 - reusable procedural Blender assets (28 Nov 2026), built to briefs/ART_DIRECTION_insert_disc_2.md.
Hand-painted medieval PS1 look: painted texture atlases (made by the SYSTEM python with PIL: `python blender/id2_assets.py <tex dir>`),
a toon material with BROAD PAINTED SHADOWS (Diffuse -> Shader to RGB -> 2-step colour ramp, cool shadow tint, x painted texture,
emitted = flat paint), marks anchored to objects as small child geometry, characters as FK puppets that FACE +Y.
Recurring cast cues: KNIGHT = squat silhouette, bent ochre plume, loose visor (+ chipped paint where it bangs the helmet), faded blue armour.
INSTRUCTOR = tall, thin, feet together, precise; deep green coat, white gloves + collar, big readable eyes (pupils move on their own).
Coordinates: Blender, z up, characters face +Y."""
import os, math, random
try:
    import bpy, bmesh
    from mathutils import Vector, Euler
except ImportError:
    bpy = None

# ======================= painted textures (system python) =======================
TEXDEF = {   # name: (base, alt, (stroke colour, n strokes) or None, seed, blobs, chips)
    'wall':   ((226, 218, 200), (214, 206, 188), ((234, 228, 212), 8), 1, 7, None),
    'ground': ((206, 192, 160), (194, 180, 148), ((214, 202, 172), 10), 2, 8, None),
    'flag':   ((196, 186, 166), (184, 174, 154), ((206, 198, 180), 6), 3, 6, None),
    'red':    ((178, 58, 44), (158, 48, 38), ((196, 72, 56), 9), 4, 6, ((150, 104, 64), 7)),        # chipped red timber: chips show wood
    'red_d':  ((140, 44, 34), (126, 38, 30), ((156, 56, 44), 6), 5, 5, ((132, 92, 56), 5)),
    'armour': ((122, 142, 170), (108, 128, 156), ((146, 164, 188), 9), 6, 6, None),                 # faded blue
    'armour_d': ((96, 112, 138), (86, 100, 126), ((112, 128, 152), 6), 7, 5, None),
    'steel':  ((168, 174, 184), (148, 156, 168), ((196, 202, 210), 8), 8, 6, None),
    'ochre':  ((214, 156, 50), (190, 130, 36), ((236, 184, 82), 8), 9, 6, None),
    'skin':   ((228, 180, 146), (214, 164, 130), None, 10, 4, None),
    'coat':   ((44, 96, 72), (36, 80, 60), ((58, 114, 86), 10), 11, 6, None),
    'cloth':  ((96, 84, 72), (84, 74, 64), ((108, 96, 84), 6), 12, 5, None),
}
def paint_all(tex_dir, size=256):
    from PIL import Image, ImageDraw, ImageFilter
    os.makedirs(tex_dir, exist_ok=True)
    for name, (base, alt, strokes, seed, blobs, chips) in TEXDEF.items():
        rnd = random.Random(seed); im = Image.new('RGB', (size, size), base)
        lay = Image.new('L', (size, size), 0); d = ImageDraw.Draw(lay)
        for _ in range(blobs):                                         # large painted colour shapes
            cx, cy = rnd.uniform(0, size), rnd.uniform(0, size); rx, ry = rnd.uniform(0.14, 0.32) * size, rnd.uniform(0.08, 0.22) * size
            d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=rnd.randint(150, 230))
        im = Image.composite(Image.new('RGB', (size, size), alt), im, lay.filter(ImageFilter.GaussianBlur(size * 0.03)))
        d = ImageDraw.Draw(im)
        if strokes:                                                    # a few long brush strokes
            for _ in range(strokes[1]):
                x0, y0 = rnd.uniform(0, size), rnd.uniform(0, size); a = rnd.uniform(-0.3, 0.3) + (0 if rnd.random() < 0.6 else math.pi / 2)
                L = rnd.uniform(0.18, 0.45) * size; d.line([(x0, y0), (x0 + L * math.cos(a), y0 + L * math.sin(a))], fill=strokes[0], width=max(2, size // 60))
        if chips:                                                      # chipped paint: irregular patches of bare wood
            for _ in range(chips[1]):
                cx, cy = rnd.uniform(0, size), rnd.uniform(0, size); r = rnd.uniform(0.03, 0.07) * size
                d.polygon([(cx + r * math.cos(a) * rnd.uniform(0.5, 1.2), cy + r * math.sin(a) * rnd.uniform(0.5, 1.2)) for a in [i * math.pi / 4 for i in range(8)]], fill=chips[0])
        im.save(os.path.join(tex_dir, name + '.png'))
    return sorted(TEXDEF)

# ======================= Blender helpers =======================
def _link(ob): bpy.context.scene.collection.objects.link(ob); return ob
def empty(name, parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    e = _link(bpy.data.objects.new(name, None)); e.parent = parent; e.location = loc; e.rotation_euler = rot; e.empty_display_size = 0.05; return e
_MATS = {}
SHADOW_TINT = (0.56, 0.56, 0.74)                                      # broad painted shadow: cooler + darker
def toon(name, col=None, tex=None, tex_dir=None, shade=True):
    """flat painted material: colour (or painted texture) x a 2-band light ramp (broad shadow shapes), emitted (no specular)"""
    if name in _MATS: return _MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial'); em = nt.nodes.new('ShaderNodeEmission'); nt.links.new(em.outputs[0], out.inputs['Surface'])
    if tex:
        ti = nt.nodes.new('ShaderNodeTexImage'); ti.image = bpy.data.images.load(os.path.join(tex_dir, tex + '.png')); ti.interpolation = 'Closest'; base = ti.outputs['Color']
    else:
        rgb = nt.nodes.new('ShaderNodeRGB'); rgb.outputs[0].default_value = (*[(c / 255) ** 2.2 for c in col], 1); base = rgb.outputs[0]
    if shade:
        df = nt.nodes.new('ShaderNodeBsdfDiffuse'); df.inputs['Color'].default_value = (1, 1, 1, 1); s2r = nt.nodes.new('ShaderNodeShaderToRGB'); nt.links.new(df.outputs[0], s2r.inputs[0])
        ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.interpolation = 'CONSTANT'
        e0, e1 = ramp.color_ramp.elements[0], ramp.color_ramp.elements[1]
        e0.position = 0.0; e0.color = (*SHADOW_TINT, 1); e1.position = 0.25; e1.color = (1.0, 1.0, 1.0, 1)
        bw = nt.nodes.new('ShaderNodeRGBToBW'); nt.links.new(s2r.outputs['Color'], bw.inputs[0]); nt.links.new(bw.outputs[0], ramp.inputs['Fac'])
        mul = nt.nodes.new('ShaderNodeVectorMath'); mul.operation = 'MULTIPLY'
        nt.links.new(base, mul.inputs[0]); nt.links.new(ramp.outputs['Color'], mul.inputs[1]); nt.links.new(mul.outputs[0], em.inputs['Color'])
    else:
        nt.links.new(base, em.inputs['Color'])
    _MATS[name] = m; return m
def prim(kind, name, m, parent=None, loc=(0, 0, 0), rot=(0, 0, 0), scl=(1, 1, 1), v=10, r=8, r2=0.0):
    if kind == 'cube': bpy.ops.mesh.primitive_cube_add(size=1.0)
    elif kind == 'cyl': bpy.ops.mesh.primitive_cylinder_add(vertices=v, radius=1.0, depth=1.0)
    elif kind == 'sph': bpy.ops.mesh.primitive_uv_sphere_add(segments=v, ring_count=r, radius=1.0)
    elif kind == 'cone': bpy.ops.mesh.primitive_cone_add(vertices=v, radius1=1.0, radius2=r2, depth=1.0)
    ob = bpy.context.active_object; ob.name = name; ob.data.materials.append(m)
    ob.parent = parent; ob.location = loc; ob.rotation_euler = rot; ob.scale = scl
    return ob
def mesh(name, verts, faces, m, parent=None, loc=(0, 0, 0)):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update(); me.uv_layers.new()
    ob = _link(bpy.data.objects.new(name, me)); ob.data.materials.append(m); ob.parent = parent; ob.location = loc; return ob
def materials(tex_dir):
    T = {k: toon(k, tex=k, tex_dir=tex_dir) for k in TEXDEF}
    for k, c in (('dark', (34, 28, 30)), ('white', (246, 244, 236)), ('brass', (214, 176, 70)), ('boot', (78, 62, 50)), ('trous', (44, 42, 48)),
                 ('hair', (30, 26, 26)), ('wood', (150, 104, 64)), ('knot', (88, 50, 28)), ('chip', (226, 230, 236)), ('stick', (96, 64, 38))):
        T[k] = toon(k, col=c)
    T['eye_white'] = toon('eye_white', col=(250, 250, 246), shade=False); T['pupil'] = toon('pupil', col=(24, 20, 24), shade=False)
    return T

# ======================= the courtyard (pale and quiet) =======================
def courtyard(T, length=14.0, back_y=9.5):
    prim('cube', 'ground', T['ground'], loc=(0, 3, -0.02), scl=(14, 2 * length, 0.04))
    for i in range(10):                                                # a few pale flagstones along the run (quiet marks)
        prim('cube', f'flag{i}', T['flag'], loc=(-0.2 + 0.4 * (i % 2), -4 + 1.4 * i, 0.002), rot=(0, 0, 0.1 * (i % 3 - 1)), scl=(1.1, 0.9, 0.004))
    for sd in (1, -1):                                                  # tall pale courtyard walls: a quiet backdrop on both sides
        prim('cube', f'wall{sd}', T['wall'], loc=(sd * 3.6, 3, 2.25), scl=(0.5, 2 * length, 4.5))
        prim('cube', f'wall_cap{sd}', T['flag'], loc=(sd * 3.5, 3, 4.56), scl=(0.7, 2 * length, 0.12))
        for k in range(5): prim('cube', f'buttress{sd}{k}', T['wall'], loc=(sd * 3.25, -3 + 3 * k, 1.1), scl=(0.3, 0.5, 2.2))
    prim('cube', 'wall_back', T['wall'], loc=(0, back_y, 2.25), scl=(8, 0.5, 4.5))

# ======================= the hurdle: chipped red timber, a knot; planks that break =======================
HURDLE_H = 0.95; HURDLE_HALF = 0.75
def hurdle(T, name, y, broken_parts=True):
    """returns dict(root, planks=[(obj, home_loc)] as left/right halves per plank so it can burst)"""
    root = empty(name, loc=(0, y, 0)); H = {'root': root, 'pieces': []}
    for sd in (1, -1):
        prim('cube', f'{name}_post{sd}', T['red_d'], root, (sd * HURDLE_HALF, 0, HURDLE_H / 2 + 0.04), scl=(0.1, 0.1, HURDLE_H + 0.08))
        prim('cube', f'{name}_foot{sd}', T['red_d'], root, (sd * HURDLE_HALF, 0, 0.04), scl=(0.2, 0.56, 0.08))
    for j, z in enumerate((0.48, HURDLE_H - 0.06)):
        for sd in (1, -1):
            ob = prim('cube', f'{name}_pl{j}{sd}', T['red'], root, (sd * HURDLE_HALF / 2, 0, z), scl=(HURDLE_HALF - 0.004, 0.065, 0.13))
            if j == 1 and sd == 1:                                     # the knot (anchored to its plank)
                prim('cyl', f'{name}_knot', T['knot'], ob, (0.15, -0.55, 0.05), rot=(math.pi / 2, 0, 0), scl=(0.05, 0.3, 0.05))
            H['pieces'].append((ob, Vector(ob.location), j, sd))
    return H
def plank(T, name, parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    """a loose red plank half (the one hooked on the knight's shoulder)"""
    p = prim('cube', name, T['red'], parent, loc, rot, scl=(HURDLE_HALF - 0.004, 0.065, 0.13))
    prim('cube', name + '_split', T['wood'], p, (0.49, 0, 0), scl=(0.03, 1.02, 0.9))          # the splintered end (bare wood)
    return p

# ======================= the knight: squat, bent ochre plume, loose visor, faded blue armour =======================
def knight(T, name='knight'):
    K = {}; root = empty(name); K['root'] = root
    pel = empty(name + '_pel', root, (0, 0, 0.66)); K['pel'] = pel; tor = empty(name + '_tor', pel); K['tor'] = tor
    prim('cyl', name + '_torso', T['armour'], tor, (0, 0, 0.26), scl=(0.26, 0.21, 0.52), v=12)
    prim('cyl', name + '_skirt', T['cloth'], pel, (0, 0, -0.06), scl=(0.27, 0.22, 0.2), v=12)
    prim('cyl', name + '_belt', T['dark'], tor, (0, 0, 0.02), scl=(0.27, 0.22, 0.05), v=12)
    prim('cube', name + '_buckle', T['brass'], tor, (0, 0.22, 0.02), scl=(0.06, 0.01, 0.05))
    prim('cube', name + '_device', T['ochre'], tor, (0, 0.21, 0.3), scl=(0.06, 0.012, 0.22))
    for sd in (1, -1): prim('sph', f'{name}_pauld{sd}', T['armour_d'], tor, (sd * 0.28, 0, 0.47), scl=(0.16, 0.15, 0.11))
    neck = empty(name + '_neck', tor, (0, 0, 0.52)); head = empty(name + '_head', neck, (0, 0, 0.14)); K['head'] = head
    prim('sph', name + '_face', T['skin'], head, (0, 0, 0), scl=(0.13, 0.13, 0.14))
    K['eyes'] = [prim('sph', f'{name}_eye{sd}', T['dark'], head, (sd * 0.045, 0.118, 0.02), scl=(0.019, 0.01, 0.024), v=8, r=6) for sd in (1, -1)]
    K['brows'] = [prim('cube', f'{name}_brow{sd}', T['hair'], head, (sd * 0.05, 0.12, 0.068), scl=(0.055, 0.012, 0.014)) for sd in (1, -1)]
    K['mouth'] = prim('cube', name + '_mouth', T['dark'], head, (0, 0.122, -0.055), scl=(0.05, 0.01, 0.012))
    hel = empty(name + '_helm', head); dome = prim('sph', name + '_dome', T['steel'], hel, (0, 0, 0.03), scl=(0.16, 0.16, 0.16), v=14, r=10)
    bm = bmesh.new(); bm.from_mesh(dome.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if (v.co.z < 0.32 and v.co.y > -0.25) or v.co.z < -0.45], context='VERTS'); bm.to_mesh(dome.data); bm.free()
    prim('cyl', name + '_rim', T['armour_d'], hel, (0, 0, 0.085), scl=(0.153, 0.153, 0.018), v=14)
    prim('cyl', name + '_chip', T['chip'], hel, (0.02, 0.14, 0.112), rot=(math.pi / 2 - 0.4, 0, 0.25), scl=(0.026, 0.014, 0.004), v=8)   # chipped paint where the visor bangs
    vis = empty(name + '_visor', hel, (0, 0, 0.06)); K['visor'] = vis
    vv, vf = [], []; rr = 0.17; n = 9
    for z0, z1 in ((-0.085, -0.025), (-0.015, 0.035)):
        b = len(vv)
        for i in range(n + 1): a = -1.05 + 2.1 * i / n; vv += [(rr * math.sin(a), rr * math.cos(a), z0), (rr * math.sin(a), rr * math.cos(a), z1)]
        for i in range(n): vf.append((b + 2 * i, b + 2 * i + 2, b + 2 * i + 3, b + 2 * i + 1))
    mesh(name + '_visorplate', vv, vf, T['steel'], vis)
    for sd in (1, -1): prim('sph', f'{name}_rivet{sd}', T['brass'], hel, (sd * 0.168, 0, 0.06), scl=(0.016, 0.016, 0.016), v=8, r=6)
    cu = bpy.data.curves.new(name + '_plume', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.03; cu.bevel_resolution = 2
    sp = cu.splines.new('BEZIER'); pts = [(0, -0.02, 0.17), (0, 0.0, 0.3), (0, 0.09, 0.35), (0, 0.17, 0.26)]
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts): bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    pl = _link(bpy.data.objects.new(name + '_plume', cu)); pl.parent = hel; pl.data.materials.append(T['ochre'])
    for sd, key in ((1, 'r'), (-1, 'l')):
        sh = empty(f'{name}_sh{key}', tor, (sd * 0.31, 0, 0.44)); K['sh' + key] = sh
        prim('cyl', f'{name}_ua{key}', T['armour'], sh, (0, 0, -0.13), scl=(0.075, 0.075, 0.26))
        el = empty(f'{name}_el{key}', sh, (0, 0, -0.26)); K['el' + key] = el
        prim('cyl', f'{name}_fa{key}', T['armour_d'], el, (0, 0, -0.12), scl=(0.065, 0.065, 0.24))
        prim('sph', f'{name}_hand{key}', T['steel'], el, (0, 0, -0.27), scl=(0.068, 0.068, 0.068))
    for sd, key in ((1, 'r'), (-1, 'l')):
        hp = empty(f'{name}_hip{key}', pel, (sd * 0.12, 0, -0.04)); K['hip' + key] = hp
        prim('cyl', f'{name}_th{key}', T['cloth'], hp, (0, 0, -0.15), scl=(0.09, 0.09, 0.3))
        kn = empty(f'{name}_kn{key}', hp, (0, 0, -0.3)); K['kn' + key] = kn
        prim('sph', f'{name}_cop{key}', T['armour'], kn, (0, 0.03, 0), scl=(0.078, 0.078, 0.078), v=8, r=6)
        prim('cyl', f'{name}_sn{key}', T['boot'], kn, (0, 0, -0.14), scl=(0.082, 0.082, 0.28))
        prim('cube', f'{name}_ft{key}', T['boot'], kn, (0, 0.05, -0.3), scl=(0.13, 0.23, 0.08))
    return K

# ======================= the instructor: tall, thin, precise; big readable eyes =======================
def instructor(T, name='instr'):
    I = {}; root = empty(name); I['root'] = root
    pel = empty(name + '_pel', root, (0, 0, 1.02)); I['pel'] = pel; tor = empty(name + '_tor', pel); I['tor'] = tor
    prim('cyl', name + '_torso', T['coat'], tor, (0, 0, 0.32), scl=(0.16, 0.12, 0.64), v=12)
    prim('cone', name + '_tails', T['coat'], pel, (0, 0, -0.2), scl=(0.22, 0.17, 0.42), r2=0.75, v=12)
    for b in range(3): prim('sph', f'{name}_btn{b}', T['brass'], tor, (0, 0.122, 0.18 + 0.13 * b), scl=(0.014, 0.008, 0.014), v=6, r=4)
    prim('cyl', name + '_collar', T['white'], tor, (0, 0, 0.64), scl=(0.11, 0.1, 0.06), v=12)
    prim('cyl', name + '_whistle', T['brass'], tor, (0.05, 0.135, 0.4), rot=(0, math.pi / 2, 0), scl=(0.014, 0.014, 0.06), v=8)
    neck = empty(name + '_neck', tor, (0, 0, 0.66)); head = empty(name + '_head', neck, (0, 0, 0.14)); I['head'] = head
    prim('sph', name + '_face', T['skin'], head, (0, 0, 0), scl=(0.105, 0.115, 0.135))
    prim('sph', name + '_hair', T['hair'], head, (0, -0.014, 0.04), scl=(0.11, 0.115, 0.105))
    I['pupils'] = []
    for sd in (1, -1):                                                 # BIG whites + pupils that slide (the glance must read on a phone)
        prim('sph', f'{name}_white{sd}', T['eye_white'], head, (sd * 0.044, 0.09, 0.02), scl=(0.04, 0.025, 0.03), v=10, r=8)
        I['pupils'].append(prim('sph', f'{name}_pupil{sd}', T['pupil'], head, (sd * 0.044, 0.112, 0.02), scl=(0.018, 0.006, 0.02), v=8, r=6))
        prim('cube', f'{name}_brow{sd}', T['hair'], head, (sd * 0.044, 0.1, 0.062), rot=(0, sd * 0.15, 0), scl=(0.05, 0.012, 0.014))
    I['mouth'] = prim('cube', name + '_mouth', T['dark'], head, (0, 0.104, -0.055), scl=(0.05, 0.008, 0.008))
    prim('cone', name + '_nose', T['skin'], head, (0, 0.11, -0.005), rot=(-math.pi / 2, 0, 0), scl=(0.018, 0.018, 0.04), v=6)
    for sd, key in ((1, 'r'), (-1, 'l')):
        sh = empty(f'{name}_sh{key}', tor, (sd * 0.19, 0, 0.6)); I['sh' + key] = sh
        prim('cyl', f'{name}_ua{key}', T['coat'], sh, (0, 0, -0.165), scl=(0.05, 0.05, 0.33))
        el = empty(f'{name}_el{key}', sh, (0, 0, -0.33)); I['el' + key] = el
        prim('cyl', f'{name}_fa{key}', T['coat'], el, (0, 0, -0.14), scl=(0.045, 0.045, 0.28))
        prim('sph', f'{name}_hand{key}', T['white'], el, (0, 0, -0.31), scl=(0.05, 0.05, 0.05))
    prim('cyl', name + '_finger', T['white'], I['elr'], (0, 0, -0.39), scl=(0.014, 0.014, 0.1), v=6)          # the pointing finger
    for sd, key in ((1, 'r'), (-1, 'l')):
        hp = empty(f'{name}_hip{key}', pel, (sd * 0.06, 0, -0.02)); I['hip' + key] = hp
        prim('cyl', f'{name}_th{key}', T['trous'], hp, (0, 0, -0.24), scl=(0.065, 0.065, 0.48))
        kn = empty(f'{name}_kn{key}', hp, (0, 0, -0.48)); I['kn' + key] = kn
        prim('cyl', f'{name}_sn{key}', T['trous'], kn, (0, 0, -0.23), scl=(0.055, 0.055, 0.46))
        prim('cube', f'{name}_ft{key}', T['dark'], kn, (0, 0.06, -0.48), scl=(0.09, 0.25, 0.07))
    return I

def look_setup(sc, res=(540, 960), lines=1.3):
    sc.render.engine = 'BLENDER_EEVEE'; sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    try: sc.eevee.taa_render_samples = 16
    except Exception: pass
    try: sc.eevee.use_shadows = True
    except Exception: pass
    sc.view_settings.view_transform = 'Standard'
    sc.render.use_freestyle = True; sc.render.line_thickness_mode = 'ABSOLUTE'; sc.render.line_thickness = lines
    try: sc.view_layers[0].freestyle_settings.linesets[0].linestyle.color = (0.14, 0.1, 0.16)
    except Exception: pass
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; nt = w.node_tree           # bright sky for the camera, LOW ambient light:
    bg = nt.nodes['Background']; bg.inputs[0].default_value = (0.7, 0.72, 0.78, 1); bg.inputs[1].default_value = 0.18     # so shadowed sides fall
    sky = nt.nodes.new('ShaderNodeBackground'); sky.inputs[0].default_value = (0.82, 0.84, 0.88, 1); sky.inputs[1].default_value = 1.0   # in the shadow band
    lp = nt.nodes.new('ShaderNodeLightPath'); mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Camera Ray'], mx.inputs[0]); nt.links.new(bg.outputs[0], mx.inputs[1]); nt.links.new(sky.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], nt.nodes['World Output'].inputs['Surface'])
    sc.render.image_settings.file_format = 'PNG'

if __name__ == '__main__' and bpy is None:
    import sys
    d = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'renders', 'id2_tex')
    print('painted', paint_all(d), '->', d)
