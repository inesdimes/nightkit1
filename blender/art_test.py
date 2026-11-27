"""ART DIRECTION TEST - Blender 5.3 version (28 Nov 2026). Same choreography as examples/art_test.py: examples/art_test_chor.py.
Hand-painted medieval PS1 look: low-poly puppets, painted texture atlases generated with Python (large colour shapes + brush strokes,
'Closest' filtering), marks anchored to the objects as small geometry (hurdle knot + chipped paint, helmet chip, shield thumb wear),
Freestyle ink lines, a quiet painted sky + field, the strongest colour on the knight / hurdle / instructor. Rendered at 360x640, upscaled x3.
  blender -b --factory-startup --python blender/art_test.py                 (MODE=still FRAMES=1,30,90 | MODE=anim)
Coordinates: chor (x, y up, z forward) -> Blender (x, z, y)."""
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, 'examples'))
import art_test_chor as C
try:
    import bpy
    from mathutils import Vector, Euler, Matrix
except ImportError: bpy = None                                        # system python: only paints the textures (python blender/art_test.py)
MODE = os.environ.get('MODE', 'still')
OUT = os.path.join(REPO, '..', 'renders', 'art_test', 'blender'); TEX = os.path.join(OUT, 'tex'); os.makedirs(TEX, exist_ok=True)
FPS = C.FPS; NF = int(round(C.DUR * FPS))
def B(p): return Vector((p[0], p[2], p[1]))                          # chor -> Blender

# ======================= painted textures (PIL) =======================
def paint(name, base, alt, strokes=None, size=256, seed=1, blobs=6, vertical=None):
    """large painted colour shapes: base + soft blobs of alt + a few long brush strokes; optional vertical gradient (sky).
    Blender's python has no PIL: inside Blender this only returns the path painted before by the system python."""
    p = os.path.join(TEX, name + '.png')
    if bpy is not None: return p
    from PIL import Image, ImageDraw, ImageFilter
    rnd = random.Random(seed); im = Image.new('RGB', (size, size), base)
    if vertical:
        d = ImageDraw.Draw(im)
        for y in range(size):
            u = y / (size - 1); c = tuple(int(vertical[0][i] + (vertical[1][i] - vertical[0][i]) * u) for i in range(3)); d.line([(0, y), (size, y)], fill=c)
    lay = Image.new('L', (size, size), 0); d = ImageDraw.Draw(lay)
    for _ in range(blobs):
        cx, cy = rnd.uniform(0, size), rnd.uniform(0, size); rx, ry = rnd.uniform(0.12, 0.3) * size, rnd.uniform(0.08, 0.22) * size
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=rnd.randint(150, 230))
    lay = lay.filter(ImageFilter.GaussianBlur(size * 0.03))
    im = Image.composite(Image.new('RGB', (size, size), alt), im, lay)
    if strokes:
        d = ImageDraw.Draw(im)
        for _ in range(strokes[1]):
            x0, y0 = rnd.uniform(0, size), rnd.uniform(0, size); a = rnd.uniform(-0.4, 0.4) + (0 if rnd.random() < 0.5 else math.pi / 2)
            L = rnd.uniform(0.15, 0.4) * size; x1, y1 = x0 + L * math.cos(a), y0 + L * math.sin(a)
            d.line([(x0, y0), (x1, y1)], fill=strokes[0], width=max(2, size // 64))
    im.save(p); return p

# ======================= scene helpers =======================
def link(ob): bpy.context.scene.collection.objects.link(ob); return ob
def empty(name, parent=None, loc=(0, 0, 0)):
    e = link(bpy.data.objects.new(name, None)); e.parent = parent; e.location = loc; e.empty_display_size = 0.05; return e
MATS = {}
def mat(name, col, tex=None, rough=0.9, emit=0.0):
    if name in MATS: return MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; p = nt.nodes.get('Principled BSDF')
    p.inputs['Roughness'].default_value = rough
    if 'Specular IOR Level' in p.inputs: p.inputs['Specular IOR Level'].default_value = 0.15
    if tex:
        im = bpy.data.images.load(tex); n = nt.nodes.new('ShaderNodeTexImage'); n.image = im; n.interpolation = 'Closest'
        nt.links.new(n.outputs['Color'], p.inputs['Base Color'])
        if emit > 0: nt.links.new(n.outputs['Color'], p.inputs['Emission Color']); p.inputs['Emission Strength'].default_value = emit
    else:
        p.inputs['Base Color'].default_value = (*[c / 255 for c in col], 1)
        if emit > 0: p.inputs['Emission Color'].default_value = (*[c / 255 for c in col], 1); p.inputs['Emission Strength'].default_value = emit
    MATS[name] = m; return m
def lin(c): return tuple(((x / 255) ** 2.2) * 255 for x in c)                    # sRGB-ish paint colours into linear for flat colours
def add(kind, name, m, parent=None, loc=(0, 0, 0), rot=(0, 0, 0), scl=(1, 1, 1), **kw):
    if kind == 'cube': bpy.ops.mesh.primitive_cube_add(size=1.0)
    elif kind == 'cyl': bpy.ops.mesh.primitive_cylinder_add(vertices=kw.get('v', 10), radius=1.0, depth=1.0)
    elif kind == 'sph': bpy.ops.mesh.primitive_uv_sphere_add(segments=kw.get('v', 12), ring_count=kw.get('r', 8), radius=1.0)
    elif kind == 'cone': bpy.ops.mesh.primitive_cone_add(vertices=kw.get('v', 10), radius1=1.0, radius2=kw.get('r2', 0.0), depth=1.0)
    ob = bpy.context.active_object; ob.name = name; ob.data.materials.append(m)
    ob.parent = parent; ob.location = loc; ob.rotation_euler = rot; ob.scale = scl
    return ob
def poly(name, verts, faces, m, parent=None, loc=(0, 0, 0)):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    if len(me.uv_layers) == 0: me.uv_layers.new()
    ob = link(bpy.data.objects.new(name, me)); ob.data.materials.append(m); ob.parent = parent; ob.location = loc; return ob

# ======================= build =======================
def build():
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    sc = bpy.context.scene
    # ---- painted materials ----
    T = {}
    T['grass'] = mat('grass', None, paint('grass', (118, 140, 92), (134, 152, 104), ((128, 146, 98), 14), seed=2, blobs=9))
    T['path'] = mat('path', None, paint('path', (180, 160, 122), (194, 174, 136), ((170, 150, 114), 10), seed=3))
    T['wood'] = mat('wood', None, paint('wood', (196, 118, 58), (176, 104, 50), ((214, 136, 72), 10), seed=4))
    T['wood_d'] = mat('wood_d', None, paint('wood_d', (150, 88, 44), (134, 78, 38), ((164, 100, 52), 8), seed=5))
    T['paintw'] = mat('paintw', (232, 222, 200))
    T['steel'] = mat('steel', None, paint('steel', (176, 182, 196), (150, 158, 174), ((206, 210, 220), 8), seed=6), rough=0.55)
    T['steel_d'] = mat('steel_d', (120, 126, 140), rough=0.6)
    T['ochre'] = mat('ochre', None, paint('ochre', (216, 160, 48), (190, 132, 34), ((236, 186, 80), 8), seed=7))
    T['tabard'] = mat('tabard', None, paint('tabard', (64, 92, 152), (52, 78, 132), ((80, 108, 170), 10), seed=8))
    T['skin'] = mat('skin', None, paint('skin', (226, 176, 140), (212, 156, 122), None, seed=9, blobs=4))
    T['dark'] = mat('dark', (32, 28, 30)); T['white'] = mat('white', (244, 242, 234)); T['brass'] = mat('brass', (214, 176, 70), rough=0.4)
    T['boot'] = mat('boot', (70, 58, 50)); T['pants'] = mat('pants', (124, 128, 140))
    T['coat'] = mat('coat', None, paint('coat', (42, 94, 70), (34, 78, 58), ((56, 112, 84), 10), seed=10))
    T['trous'] = mat('trous', (40, 40, 46)); T['hair'] = mat('hair', (28, 24, 24))
    T['shieldb'] = mat('shieldb', None, paint('shieldb', (46, 70, 132), (40, 60, 116), ((60, 86, 150), 6), seed=11)); T['rim'] = mat('rim', (176, 150, 96))
    T['wear'] = mat('wear', (96, 114, 168)); T['knot'] = mat('knot', (90, 52, 28)); T['ring'] = mat('ring', (150, 86, 44)); T['chip'] = mat('chip', (228, 230, 234), rough=0.3)
    T['fence'] = mat('fence', (132, 114, 90)); T['tree'] = mat('tree', None, paint('tree', (96, 124, 84), (84, 110, 74), None, seed=12)); T['trunk'] = mat('trunk', (110, 90, 70))
    T['sky'] = mat('sky', None, paint('sky', (150, 180, 214), (244, 240, 228), None, seed=13, blobs=5, vertical=((150, 180, 214), (236, 228, 204))), emit=1.0)
    R = {}
    # ---- set (quiet) ----
    add('cube', 'ground', T['grass'], loc=(0, 1, -0.02), scl=(30, 36, 0.04))
    add('cube', 'path', T['path'], loc=(0, -1, 0.001), scl=(1.9, 14, 0.004))
    for k in range(13):
        y = -9 + 1.6 * k
        for sd in (1, -1):
            add('cube', f'fp{k}{sd}', T['fence'], loc=(sd * 4.5, y, 0.45), scl=(0.1, 0.1, 0.9))
            add('cube', f'fr{k}{sd}', T['fence'], loc=(sd * 4.5, y + 0.8, 0.7), scl=(0.06, 1.6, 0.06))
    rnd = random.Random(3)
    for i in range(9):
        sd = 1 if i % 2 else -1; x = sd * (7 + 6 * rnd.random()); y = -12 + 26 * rnd.random(); h = 4 + 2 * rnd.random()
        add('cyl', f'tt{i}', T['trunk'], loc=(x, y, h * 0.18), scl=(0.12, 0.12, h * 0.36))
        for j in range(3): add('cone', f'tc{i}{j}', T['tree'], loc=(x, y, h * (0.35 + 0.2 * j)), scl=(h * (0.3 - 0.06 * j), h * (0.3 - 0.06 * j), h * 0.32), v=8)
    sky = add('sph', 'sky', T['sky'], loc=(0, 0, -5), scl=(80, 80, 60), v=24, r=12)
    for poly_ in sky.data.polygons: poly_.flip()
    # ---- the hurdle (root rocks about its base) ----
    hr = empty('hurdle'); R['hurdle'] = hr; H_, HW = C.HURDLE_H, C.HURDLE_HALF
    for sd in (1, -1):
        add('cube', f'post{sd}', T['wood_d'], hr, (sd * HW, 0, H_ / 2 + 0.04), scl=(0.1, 0.1, H_ + 0.08))
        add('cube', f'foot{sd}', T['wood_d'], hr, (sd * HW, 0, 0.04), scl=(0.2, 0.56, 0.08))
    for j, z in enumerate((0.48, H_ - 0.06)):
        add('cube', f'plank{j}', T['wood'], hr, (0, 0, z), scl=(2 * HW, 0.06, 0.13))
        for k_, x in enumerate((-0.45, 0.0, 0.45)):
            w = 0.22 if not (j == 1 and k_ == 1) else 0.13                                     # chipped band in the middle of the top plank
            for sy in (1, -1): add('cube', f'band{j}{k_}{sy}', T['paintw'], hr, (x, sy * 0.032, z), scl=(w, 0.004, 0.132))
    # the knot (anchored): dark eye + ring on the top plank, camera side (-y)
    for sy in (1, -1):
        add('cyl', f'knot{sy}', T['knot'], hr, (0.28, sy * 0.036, H_ - 0.06), rot=(math.pi / 2, 0, 0), scl=(0.035, 0.022, 0.004))
        add('cyl', f'knotring{sy}', T['ring'], hr, (0.28, sy * 0.0345, H_ - 0.06), rot=(math.pi / 2, 0, 0), scl=(0.065, 0.04, 0.003))
    # ---- the knight: squat, bent ochre plume, loose visor ----
    K = {}; root = empty('k_root'); K['root'] = root
    pel = empty('k_pel', root, (0, 0, 0.66)); K['pel'] = pel
    tor = empty('k_tor', pel); K['tor'] = tor
    add('cyl', 'k_torso', T['tabard'], tor, (0, 0, 0.26), scl=(0.25, 0.2, 0.52), v=12)
    add('cyl', 'k_skirt', T['tabard'], pel, (0, 0, -0.06), scl=(0.27, 0.22, 0.2), v=12)
    add('cyl', 'k_belt', T['dark'], tor, (0, 0, 0.02), scl=(0.26, 0.21, 0.05), v=12)
    add('cube', 'k_buckle', T['brass'], tor, (0, 0.21, 0.02), scl=(0.06, 0.01, 0.05))
    add('cube', 'k_device', T['ochre'], tor, (0, 0.2, 0.3), scl=(0.06, 0.01, 0.22))              # ochre bar on the tabard
    for sd in (1, -1): add('sph', f'k_pauld{sd}', T['steel'], tor, (sd * 0.27, 0, 0.47), scl=(0.15, 0.14, 0.1))
    neck = empty('k_neck', tor, (0, 0, 0.52)); head = empty('k_head', neck, (0, 0, 0.14)); K['head'] = head
    add('sph', 'k_face', T['skin'], head, (0, 0, 0), scl=(0.13, 0.13, 0.14))
    eyes = []
    for sd in (1, -1):
        eyes.append(add('sph', f'k_eye{sd}', T['dark'], head, (sd * 0.045, 0.118, 0.02), scl=(0.018, 0.01, 0.022), v=8, r=6))
        add('cube', f'k_brow{sd}', T['hair'], head, (sd * 0.05, 0.12, 0.065), scl=(0.05, 0.012, 0.012))
    K['eyes'] = eyes; K['mouth'] = add('cube', 'k_mouth', T['dark'], head, (0, 0.122, -0.055), scl=(0.05, 0.01, 0.012))
    hel = empty('k_helm', head); dome = add('sph', 'k_dome', T['steel'], hel, (0, 0, 0.03), scl=(0.16, 0.16, 0.16), v=14, r=10)
    import bmesh                                                                     # open face: cut the dome above the brows at the front
    bm = bmesh.new(); bm.from_mesh(dome.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if (v.co.z < 0.32 and v.co.y > -0.25) or v.co.z < -0.45], context='VERTS')
    bm.to_mesh(dome.data); bm.free()
    add('cyl', 'k_rim', T['steel_d'], hel, (0, 0, 0.085), scl=(0.153, 0.153, 0.018), v=14)
    add('cyl', 'k_chip', T['chip'], hel, (0.015, 0.14, 0.11), rot=(math.pi / 2, 0, 0.2), scl=(0.022, 0.012, 0.003), v=8)      # chipped paint where the visor bangs
    vis = empty('k_visor', hel, (0, 0, 0.06)); K['visor'] = vis
    vv = []; vf = []; rr = 0.17; n = 9
    for band, (z0, z1) in enumerate(((-0.085, -0.025), (-0.015, 0.035))):
        base = len(vv)
        for i in range(n + 1):
            a = -1.05 + 2.1 * i / n; vv += [(rr * math.sin(a), rr * math.cos(a), z0), (rr * math.sin(a), rr * math.cos(a), z1)]
        for i in range(n): vf.append((base + 2 * i, base + 2 * i + 2, base + 2 * i + 3, base + 2 * i + 1))
    poly('k_visorplate', vv, vf, T['steel'], vis)
    for sd in (1, -1): add('sph', f'k_rivet{sd}', T['brass'], hel, (sd * 0.168, 0, 0.06), scl=(0.016, 0.016, 0.016), v=8, r=6)
    cu = bpy.data.curves.new('k_plume', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.028; cu.bevel_resolution = 2
    sp = cu.splines.new('BEZIER'); pts = [(0, -0.02, 0.17), (0, 0.0, 0.29), (0, 0.08, 0.33), (0, 0.16, 0.25)]
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts): bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    pl = link(bpy.data.objects.new('k_plume', cu)); pl.parent = hel; pl.data.materials.append(T['ochre'])
    for sd, key in ((1, 'r'), (-1, 'l')):                                                         # arms
        sh = empty(f'k_sh{key}', tor, (sd * 0.3, 0, 0.44)); K['sh' + key] = sh
        add('cyl', f'k_ua{key}', T['tabard'], sh, (0, 0, -0.13), scl=(0.07, 0.07, 0.26))
        el = empty(f'k_el{key}', sh, (0, 0, -0.26)); K['el' + key] = el
        add('cyl', f'k_fa{key}', T['steel'], el, (0, 0, -0.12), scl=(0.06, 0.06, 0.24))
        add('sph', f'k_hand{key}', T['steel_d'], el, (0, 0, -0.27), scl=(0.065, 0.065, 0.065))
    sh_ = empty('k_shield', K['ell'], (-0.08, 0.0, -0.12)); sh_.rotation_euler = Euler((0, 0, -math.pi / 2))                                          # kite shield on the left forearm
    pts2 = [(0.0, 0.26), (0.2, 0.18), (0.18, -0.06), (0.0, -0.32), (-0.18, -0.06), (-0.2, 0.18)]
    poly('k_shrim', [(x * 1.0, 0, y) for x, y in pts2], [tuple(range(6))], T['rim'], sh_)
    poly('k_shface', [(x * 0.86, -0.006, y * 0.86) for x, y in pts2], [tuple(range(6))], T['shieldb'], sh_)
    add('cube', 'k_shbar', T['ochre'], sh_, (0, -0.009, 0.02), scl=(0.08, 0.003, 0.24))
    add('cyl', 'k_wear', T['wear'], sh_, (0.15, -0.009, 0.1), rot=(math.pi / 2, 0, 0), scl=(0.03, 0.02, 0.003), v=8)      # thumb wear by the grip
    for sd, key in ((1, 'r'), (-1, 'l')):                                                         # legs
        hp = empty(f'k_hip{key}', pel, (sd * 0.12, 0, -0.04)); K['hip' + key] = hp
        add('cyl', f'k_th{key}', T['pants'], hp, (0, 0, -0.15), scl=(0.09, 0.09, 0.3))
        kn = empty(f'k_kn{key}', hp, (0, 0, -0.3)); K['kn' + key] = kn
        add('sph', f'k_cop{key}', T['steel'], kn, (0, -0.03, 0), scl=(0.075, 0.075, 0.075), v=8, r=6)
        add('cyl', f'k_sn{key}', T['boot'], kn, (0, 0, -0.14), scl=(0.08, 0.08, 0.28))
        add('cube', f'k_ft{key}', T['boot'], kn, (0, 0.05, -0.3), scl=(0.13, 0.22, 0.08))
    R['K'] = K
    # ---- the instructor: tall, thin, green coat, white gloves + collar, pointer, whistle ----
    I = {}; root = empty('i_root'); I['root'] = root
    pel = empty('i_pel', root, (0, 0, 1.02)); I['pel'] = pel; tor = empty('i_tor', pel); I['tor'] = tor
    add('cyl', 'i_torso', T['coat'], tor, (0, 0, 0.32), scl=(0.16, 0.12, 0.64), v=12)
    add('cone', 'i_tails', T['coat'], pel, (0, 0, -0.2), scl=(0.22, 0.17, 0.42), r2=0.75, v=12)
    for b in range(3): add('sph', f'i_btn{b}', T['brass'], tor, (0, 0.122, 0.18 + 0.13 * b), scl=(0.014, 0.008, 0.014), v=6, r=4)
    add('cyl', 'i_collar', T['white'], tor, (0, 0, 0.64), scl=(0.11, 0.1, 0.06), v=12)
    add('cyl', 'i_whcord', T['white'], tor, (0.04, 0.12, 0.5), rot=(-0.3, 0, 0), scl=(0.004, 0.004, 0.2), v=4)
    add('cyl', 'i_whistle', T['brass'], tor, (0.05, 0.135, 0.38), rot=(0, math.pi / 2, 0), scl=(0.014, 0.014, 0.06), v=8)
    neck = empty('i_neck', tor, (0, 0, 0.66)); head = empty('i_head', neck, (0, 0, 0.13)); I['head'] = head
    add('sph', 'i_face', T['skin'], head, (0, 0, 0), scl=(0.1, 0.11, 0.13))
    add('sph', 'i_hair', T['hair'], head, (0, -0.012, 0.035), scl=(0.105, 0.11, 0.105))
    ie = []
    for sd in (1, -1):
        ie.append(add('sph', f'i_eye{sd}', T['dark'], head, (sd * 0.035, 0.092, 0.015), scl=(0.014, 0.008, 0.012), v=8, r=6))
        add('cube', f'i_brow{sd}', T['hair'], head, (sd * 0.038, 0.096, 0.05), scl=(0.04, 0.01, 0.012))
    I['eyes'] = ie; I['mouth'] = add('cube', 'i_mouth', T['dark'], head, (0, 0.098, -0.05), scl=(0.035, 0.008, 0.007))
    for sd, key in ((1, 'r'), (-1, 'l')):
        sh = empty(f'i_sh{key}', tor, (sd * 0.19, 0, 0.6)); I['sh' + key] = sh
        add('cyl', f'i_ua{key}', T['coat'], sh, (0, 0, -0.165), scl=(0.05, 0.05, 0.33))
        el = empty(f'i_el{key}', sh, (0, 0, -0.33)); I['el' + key] = el
        add('cyl', f'i_fa{key}', T['coat'], el, (0, 0, -0.14), scl=(0.045, 0.045, 0.28))
        add('sph', f'i_hand{key}', T['white'], el, (0, 0, -0.31), scl=(0.05, 0.05, 0.05))
    add('cyl', 'i_pointer', mat('stick', (90, 60, 36)), I['elr'], (0, 0.3, -0.31), rot=(math.pi / 2, 0, 0), scl=(0.01, 0.01, 0.7), v=6)
    add('sph', 'i_ptip', T['white'], I['elr'], (0, 0.65, -0.31), scl=(0.016, 0.016, 0.016), v=6, r=4)
    for sd, key in ((1, 'r'), (-1, 'l')):
        hp = empty(f'i_hip{key}', pel, (sd * 0.06, 0, -0.02)); I['hip' + key] = hp
        add('cyl', f'i_th{key}', T['trous'], hp, (0, 0, -0.24), scl=(0.065, 0.065, 0.48))
        kn = empty(f'i_kn{key}', hp, (0, 0, -0.48)); I['kn' + key] = kn
        add('cyl', f'i_sn{key}', T['trous'], kn, (0, 0, -0.23), scl=(0.055, 0.055, 0.46))
        add('cube', f'i_ft{key}', T['dark'], kn, (0, 0.06, -0.48), scl=(0.09, 0.24, 0.06))
    R['I'] = I
    # ---- camera, light, world ----
    cam = link(bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))); sc.camera = cam; cam.data.sensor_fit = 'HORIZONTAL'; R['cam'] = cam
    sun = link(bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN'))); sun.data.energy = 3.2; sun.data.color = (1.0, 0.94, 0.84)
    sun.rotation_euler = Euler((math.radians(50), math.radians(10), math.radians(-35)))
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (0.55, 0.6, 0.66, 1); w.node_tree.nodes['Background'].inputs[1].default_value = 0.9
    sc.render.engine = 'BLENDER_EEVEE'
    sc.render.resolution_x, sc.render.resolution_y = 360, 640; sc.render.resolution_percentage = 100; sc.render.fps = FPS
    try: sc.eevee.taa_render_samples = 16
    except Exception: pass
    sc.view_settings.view_transform = 'Standard'
    sc.render.use_freestyle = True; sc.render.line_thickness_mode = 'ABSOLUTE'; sc.render.line_thickness = 1.1
    try:
        ls = sc.view_layers[0].freestyle_settings.linesets[0].linestyle; ls.color = (0.12, 0.09, 0.14)
    except Exception as e: print('freestyle', e)
    sc.render.image_settings.file_format = 'PNG'
    return sc, R

# ======================= per-frame pose (FK from the shared choreography) =======================
def set_rot(ob, x=0.0, y=0.0, z=0.0): ob.rotation_euler = Euler((x, y, z))
def update(R, t):
    K, I = R['K'], R['I']
    # ---- knight ----
    d = C.knight(t); kr = K['root']; kr.location = B((d['x'], 0.0, d['z'])); set_rot(kr, z=-d['yaw'])
    sp_ = d['speed']; a = min(1.0, sp_ / 2.0) if sp_ > 0.05 else 0.0; ph = d['phase']; s = math.sin(ph)
    K['pel'].location = (0, 0, 0.66 + 0.03 * a * abs(math.cos(ph)))
    lean = 0.08 + 0.16 * a; fold = d['fold']
    set_rot(K['tor'], x=-(lean + 1.3 * fold))
    set_rot(K['hipr'], x=0.75 * a * s + 0.35 * fold); set_rot(K['hipl'], x=-0.75 * a * s + 0.35 * fold)
    set_rot(K['knr'], x=-(0.9 * a * max(0.0, -s) + 0.5 * fold)); set_rot(K['knl'], x=-(0.9 * a * max(0.0, s) + 0.5 * fold))
    if fold > 0: kr.location = B((d['x'], 0.3 * fold, d['z'] + 0.36 * fold))
    shr = [0.5 * a * -s, 0.0, 0.0]; shl = [0.5 * a * s, 0.0, 0.0]; elr = 0.6 + 0.4 * a; ell = 0.9
    k = d['arms_k']
    if d['arms'] == 'slap': shr = [2.6 * k, 0.0, -0.3 * k]; elr = 0.6 + 1.2 * k
    if d['arms'] == 'blind':
        wig = 0.12 * math.sin(t * 11); shr = [1.5 * k + wig, 0, 0]; shl = [1.4 * k - wig, 0, 0]; elr = 0.2; ell = 0.4
    if fold > 0:
        shr = [1.2 * fold, 0, 0]; shl = [1.1 * fold, 0, 0]; elr = 0.2; ell = 0.3
        if d['arms'] == 'thumb': shr = [1.2 + 1.3 * k, 0, -0.5 * k]; elr = 0.2 + 1.3 * k
    set_rot(K['shr'], *shr); set_rot(K['shl'], *shl); set_rot(K['elr'], x=elr); set_rot(K['ell'], x=ell)
    set_rot(K['head'], x=-(0.6 * d['look_up']) + 0.25 * fold, z=0.6 * d['look_side'])
    set_rot(K['visor'], x=1.35 * (1 - d['visor']))
    op = 1.0 if d['arms'] in ('blind',) or (fold > 0 and d['arms'] != 'thumb') else 0.0
    K['mouth'].scale = (0.05, 0.01, 0.012 + 0.03 * op)
    # ---- instructor ----
    e = C.instructor(t); ir = I['root']; ir.location = B((e['x'], e['y'], e['z'])); set_rot(ir, z=-e['yaw'])
    c = e['crouch']; tk = e['tuck']
    I['pel'].location = (0, 0, 1.02 - 0.45 * c)
    set_rot(I['tor'], x=-(0.35 * c + 0.12 * tk) + 0.03)
    th = -(1.0 * c + 1.5 * tk); knb = 2.0 * c + 2.2 * tk
    if e.get('step'): sw = math.sin(2 * math.pi * 1.6 * t); set_rot(I['hipr'], x=0.4 * sw); set_rot(I['hipl'], x=-0.4 * sw); set_rot(I['knr'], x=-0.3); set_rot(I['knl'], x=-0.3)
    else:
        set_rot(I['hipr'], x=-th); set_rot(I['hipl'], x=-th); set_rot(I['knr'], x=-knb); set_rot(I['knl'], x=-knb)
    k = e['arms_k']; shr = [0, 0, 0]; shl = [0, 0, 0]; elr = 0.15; ell = 0.15
    if e['arms'] == 'back': shr = [-0.8 * k, 0, 0]; shl = [-0.8 * k, 0, 0]
    if e['arms'] == 'up': shr = [2.75 * k, 0.4 * k, 0]; shl = [2.75 * k, -0.4 * k, 0]
    if e['arms'] == 'behind': shr = [-0.35 * k, -0.25 * k, 0]; shl = [-0.35 * k, 0.25 * k, 0]; elr = 0.15; ell = 0.15
    if e['arms'] == 'point': shl = [-0.35, 0.25, 0]; ell = 0.15; shr = [-0.35 + 1.55 * k, -0.25 * (1 - k), 0]; elr = 0.15
    set_rot(I['shr'], *shr); set_rot(I['shl'], *shl); set_rot(I['elr'], x=elr); set_rot(I['ell'], x=ell)
    set_rot(I['head'], x=-0.0 + 0.3 * e['head'])
    for ey in I['eyes']: ey.scale = (0.014, 0.008, 0.002 if e['blink'] else 0.012)
    I['mouth'].scale = (0.035 if e['arms'] != 'up' or k < 0.5 else 0.05, 0.008, 0.007)
    # ---- hurdle + camera ----
    set_rot(R['hurdle'], x=C.hurdle_wobble(t))
    nm, pos, tgt, fov = C.camera(t)
    from_ = B(pos); to = B(tgt); cam = R['cam']; cam.location = from_
    cam.rotation_euler = (to - from_).to_track_quat('-Z', 'Y').to_euler(); cam.data.angle_x = math.radians(fov)
    if C.K_CRASH <= t < C.K_CRASH + 0.3: cam.location = from_ + Vector((0, 0, 0.04 * math.sin((t - C.K_CRASH) * 70) * (1 - (t - C.K_CRASH) / 0.3)))

if __name__ == '__main__' and bpy is None:
    # system python: find every paint(...) call in build() (balanced parentheses) and run it -> textures on disk for Blender
    src = open(os.path.abspath(__file__), encoding='utf-8').read(); src = src[src.index('def build():'):src.index('# ======================= per-frame pose')]
    i = 0; n = 0
    while True:
        i = src.find("paint('", i)
        if i < 0: break
        depth = 0
        for j in range(i, len(src)):
            if src[j] == '(': depth += 1
            elif src[j] == ')':
                depth -= 1
                if depth == 0: break
        eval(src[i:j + 1]); n += 1; i = j + 1
    print('painted', n, 'textures ->', TEX)
if __name__ == '__main__' and bpy is not None:
    sc, R = build()
    def handler(scene, *_): update(R, (scene.frame_current - 1) / FPS)
    bpy.app.handlers.frame_change_pre.append(handler)
    d = os.path.join(OUT, 'frames'); os.makedirs(d, exist_ok=True)
    if MODE == 'anim':
        a, b = map(int, os.environ.get('FRAMES', f'1-{NF}').split('-'))
        sc.frame_start, sc.frame_end = a, b; sc.render.filepath = os.path.join(d, 'f_'); bpy.ops.render.render(animation=True)
    else:
        for f in [int(x) for x in os.environ.get('FRAMES', '5').split(',')]:
            sc.frame_set(f); sc.render.filepath = os.path.join(OUT, 'still_%04d.png' % f); bpy.ops.render.render(write_still=True)
    print('RENDER done')
