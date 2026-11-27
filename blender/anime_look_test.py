"""ANIME CUTSCENE LOOK TEST (Insert Disc 2, 28 Nov 2026) - 4 s vertical, Blender 5.3. Hand-inked sports-anime cutscene inside a PS1 medieval RPG.
Reuses blender/id2_assets.py (blue knight, green instructor, hurdle, courtyard, painted atlases, toon material) and its vertical settings
(look_setup 540x960 -> x2 nearest = 1080x1920, 24 fps). Every look change lives HERE, so id2_assets keeps the current style for comparison:
- the knight's face: the small sphere eyes/brows are hidden and replaced by FLAT INKED SHAPES fitted to the face (eye white, iris, pupil,
  one catch-light, a heavy upper lid, an angular brow) - two hand-designed poses: WATCH (pupils up-right, lids open, brows lifted) and
  DECIDE (pupils down at the hurdle, upper lids lowered over the iris top, brows low and angled in). Flat shapes survive 540x960.
- the visor rides just above the brows like a brim: ONE broad hard shadow across the upper face; the eye shapes are emissive so they stay
  readable inside it.
- armour: base colour + one hard-edged shadow (id2 toon) + small deliberately placed highlight slivers (helmet dome, pauldron, visor edge).
- ink: Freestyle line sets - heavy on eyelids/brows/visor/helmet rim, medium on the outer silhouette of the cast + hurdle, NONE on the courtyard.
Shots: 0.0-1.0 wide side (instructor demonstrates the jump, the knight watches from the left facing right) | 1.0-2.2 tight under the visor
(eyes follow him up ... drop to the hurdle, the brow settles: the DECISION at 1.62 s, held) | 2.2-4.0 three-quarter side (plants his foot,
lowers his shoulder, through the hurdle: contact + the board breaking in one frame, the next stride beyond it).
Run:  python blender/id2_assets.py ../renders/anime_look_test/tex   (system python paints the atlases)
      blender -b --factory-startup --python blender/anime_look_test.py   (MODE=still FRAMES=1,46 | MODE=anim)"""
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bpy
from mathutils import Vector, Euler
import id2_assets as A
MODE = os.environ.get('MODE', 'still')
OUT = os.path.join(HERE, '..', '..', 'renders', 'anime_look_test'); TEX = os.path.join(OUT, 'tex'); os.makedirs(OUT, exist_ok=True)
FPS = 24; DUR = 4.0; NF = int(DUR * FPS)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def seg(t, a, b): return clamp((t - a) / (b - a))
def sm(u): u = clamp(u); return u * u * (3 - 2 * u)
def lerp(a, b, u): return a + (b - a) * u
def lerpv(a, b, u): return Vector(a).lerp(Vector(b), u)

# ---------------- beats ----------------
S_A, S_B, S_C = 0.0, 1.0, 2.2
I_CROUCH = (0.05, 0.25); I_JUMP = (0.25, 0.72); I_LAND = (0.72, 0.92)
T_LOOKUP = (1.0, 1.4)                   # eyes follow him up (WATCH pose)
T_DECIDE = 1.62                         # the eyes DROP to the hurdle, lids lower, brow settles (DECIDE pose) - held to 2.2
T_PLANT = (2.2, 2.45); T_SHOULDER = (2.42, 2.68); T_CONTACT = 3.255
K_Y0 = -2.2; K_YC = -0.36               # the knight stands here; contact position (shoulder at the top board)
I_X = 0.42; I_Y0, I_Y1 = -0.85, 0.85; I_ASIDE = (-1.7, 1.6)

def knight_y(t):
    if t < T_SHOULDER[1]: return K_Y0 - 0.12 * sm(seg(t, *T_PLANT))                     # the planted step back
    if t < T_CONTACT: u = seg(t, T_SHOULDER[1], T_CONTACT); return lerp(K_Y0 - 0.12, K_YC, u ** 1.4)
    return K_YC + 2.5 * (t - T_CONTACT)                                                 # straight through, beyond the board

# ---------------- the inked eyes (head-local, the face sphere is 0.13 x 0.13 x 0.14, front = +Y) ----------------
SKIN_SHADOW = (175, 138, 127)                      # skin x the toon shadow tint (matches the id2 shadow band)
EYE_W = (250, 246, 236); IRIS = (64, 92, 132); LID = (26, 20, 26); BROW = (40, 30, 26)
def ring(cx, cz, rx, rz, n=12): return [(cx + rx * math.cos(2 * math.pi * i / n), cz + rz * math.sin(2 * math.pi * i / n)) for i in range(n)]
def face_shape(name, pts2, m, parent, y, sd):
    """flat shape in the eye plane: pts2 = [(x, z)] relative to the eye centre; the plane is turned to follow the face curve"""
    vs = [(x, 0.0, z) for x, z in pts2]
    ob = A.mesh(name, vs, [tuple(range(len(vs)))], m, parent); ob.location = (0, y, 0)
    return ob
def build_eyes(T, K):
    head = K['head']; E = {}
    m_w = A.toon('a_eyewhite', col=EYE_W, shade=False); m_i = A.toon('a_iris', col=IRIS, shade=False); m_p = A.toon('a_pupil', col=(14, 12, 16), shade=False)
    m_h = A.toon('a_hi', col=(255, 255, 255), shade=False); m_l = A.toon('a_lid', col=LID, shade=False); m_b = A.toon('a_brow', col=BROW, shade=False)
    # reference (vintage boxing anime poster): SMALL iris + dot pupil in a lot of white, narrow sharp almond, heavy dark upper lid,
    # a short lower-lid stroke at the outer corner, thick angular brows sitting low on the eyes, a hard brow-ridge shadow
    for sd, key in ((1, 'r'), (-1, 'l')):
        piv = A.empty(f'eye_{key}', head, (sd * 0.046, 0.121, 0.022), (0, 0, sd * 0.36))
        E['piv' + key] = piv
        white = [(-0.025 * sd, -0.002), (-0.01 * sd, 0.009), (0.014 * sd, 0.011), (0.029 * sd, 0.006), (0.021 * sd, -0.007), (0.002 * sd, -0.01), (-0.016 * sd, -0.008)]
        face_shape(f'eyew_{key}', white, m_w, piv, 0.004, sd)
        irs = A.empty(f'iris_{key}', piv, (0, 0.0055, 0)); E['iris' + key] = irs
        face_shape(f'irisd_{key}', ring(0, 0, 0.0074, 0.0086), m_i, irs, 0.0, sd)
        face_shape(f'pupil_{key}', ring(0, 0, 0.0034, 0.0042, 8), m_p, irs, 0.0004, sd)
        face_shape(f'hl_{key}', ring(0.0028 * sd, 0.003, 0.0017, 0.0017, 6), m_h, irs, 0.0008, sd)
        lid = A.empty(f'lidp_{key}', piv, (0, 0.007, 0)); E['lid' + key] = lid
        face_shape(f'lid_{key}', [(-0.028 * sd, -0.001), (-0.012 * sd, 0.012), (0.014 * sd, 0.016), (0.035 * sd, 0.011), (0.038 * sd, 0.002),
                                  (0.027 * sd, 0.005), (0.013 * sd, 0.0075), (-0.011 * sd, 0.0055), (-0.023 * sd, -0.002)], m_l, lid, 0.0, sd)
        face_shape(f'lidskin_{key}', [(-0.029 * sd, 0.0), (-0.012 * sd, 0.013), (0.014 * sd, 0.017), (0.036 * sd, 0.012), (0.036 * sd, 0.05), (-0.029 * sd, 0.05)],
                   A.toon('a_lidskin', col=SKIN_SHADOW, shade=False), lid, -0.0004, sd)
        face_shape(f'lowlid_{key}', [(0.006 * sd, -0.0115), (0.022 * sd, -0.0085), (0.03 * sd, -0.003), (0.021 * sd, -0.006), (0.006 * sd, -0.0095)], m_l, piv, 0.0045, sd)
        brow = A.empty(f'browp_{key}', head, (sd * 0.05, 0.127, 0.06), (0, 0, sd * 0.3)); E['brow' + key] = brow
        face_shape(f'brow_{key}', [(-0.03 * sd, 0.001), (-0.005 * sd, 0.012), (0.024 * sd, 0.012), (0.036 * sd, 0.004), (0.03 * sd, -0.002), (0.0, 0.0), (-0.026 * sd, -0.009)], m_b, brow, 0.0, sd)
    fur = A.empty('furrow', head, (0, 0.128, 0.064)); E['furrow'] = fur                         # the knitted-brow strokes (DECIDE only)
    for sd in (1, -1): face_shape(f'furrow_{sd}', [(sd * 0.003, -0.012), (sd * 0.007, 0.01), (sd * 0.0055, 0.011), (sd * 0.0015, -0.011)], m_l, fur, 0.0, sd)
    for ob in K['eyes'] + K['brows']: ob.hide_render = True
    # ONE broad hard shadow across the upper face (cel style, hand-placed), two fitted versions: WATCH and DECIDE (lower over the eyes).
    # Moving one strip down pushed its top inside the sphere (a lit V on the forehead), so each version is fitted to the face surface.
    rx, ry, rz = 0.13, 0.13, 0.14; n = 12; xs = [-0.112 + 0.224 * i / n for i in range(n + 1)]
    def surf(x, z): q = 1 - (x / rx) ** 2 - (z / rz) ** 2; return ry * math.sqrt(max(0.0, q)) + 0.0025
    def strip(name, drop):
        vs = []; fs_ = []
        for i, x in enumerate(xs):
            zb = 0.04 - drop + 0.012 * (x / 0.112) + (0.006 if i in (3, 4, 8, 9) else 0.0)
            for z in (0.134, 0.118, zb + 0.55 * (0.118 - zb), zb + 0.25 * (0.118 - zb), zb): vs.append((x, surf(x, z), z))
        for i in range(n):
            for j in range(4): a = i * 5 + j; fs_.append((a, a + 5, a + 6, a + 1))
        return A.mesh(name, vs, fs_, A.toon('a_faceshadow', col=SKIN_SHADOW, shade=False), head)
    E['shadowA'] = strip('face_shadow_watch', 0.0); E['shadowB'] = strip('face_shadow_decide', 0.013)
    return E
POSES = {   # hand-designed: iris aim (x, z), lid drop, brow (dz, tilt, inner drop)
    'neutral': dict(aim=(0.0, 0.0), lid=0.0, brow=(0.0, 0.0)),
    'watch':   dict(aim=(0.008, 0.004), lid=-0.001, brow=(0.005, -0.1)),          # following him UP-right: a lot of white below the iris
    'decide':  dict(aim=(0.006, -0.0045), lid=0.0055, brow=(-0.008, 0.36), shade=1.0, furrow=1.0),   # DOWN at the hurdle: heavy lids, brows knit low        # DOWN at the hurdle: lids lowered over the iris, brows low + angled in
}
def pose_eyes(E, p, sd_flip=True):
    for sd, key in ((1, 'r'), (-1, 'l')):
        ax, az = p['aim']; E['iris' + key].location = (ax, 0.0055, az)                  # both eyes aim the same way (to his right / up-down)
        E['lid' + key].location = (0, 0.007, -p['lid'])
        dz, tilt = p['brow']; E['brow' + key].location = (sd * 0.05, 0.127, 0.066 + dz)
        E['brow' + key].rotation_euler = Euler((0, sd * tilt, sd * 0.3))
    dec = p.get('shade', 0.0) >= 0.5                                                     # the shadow SNAPS lower over the eyes at the decision
    E['shadowA'].location = (0, -0.06 if dec else 0.0, 0); E['shadowB'].location = (0, 0.0 if dec else -0.06, 0)   # (the off one tucked inside the head)
    f = p.get('furrow', 0.0); E['furrow'].scale = (1.0, 1.0, max(0.05, f))                # no hide_render toggling in a frame handler: it crashes the animation render
    E['furrow'].location = (0, 0.128 if f >= 0.05 else -0.05, 0.064)                    # off = tucked inside the head                          # the shadow dips over the eyes at the decision
def mix_pose(a, b, u):
    return dict(aim=(lerp(a['aim'][0], b['aim'][0], u), lerp(a['aim'][1], b['aim'][1], u)), lid=lerp(a['lid'], b['lid'], u),
                brow=(lerp(a['brow'][0], b['brow'][0], u), lerp(a['brow'][1], b['brow'][1], u)), shade=lerp(a.get('shade', 0.0), b.get('shade', 0.0), u), furrow=lerp(a.get('furrow', 0.0), b.get('furrow', 0.0), u))

# ---------------- build ----------------
def build():
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    sc = bpy.context.scene; T = A.materials(TEX); R = {}
    A.courtyard(T, back_y=6.5)
    for nm in ('wall1', 'wall-1', 'wall_back'): ob = bpy.data.objects[nm]; ob.scale.z = 2.8; ob.location.z = 1.4
    for nm in ('wall_cap1', 'wall_cap-1'): bpy.data.objects[nm].location.z = 2.86
    for o in bpy.data.objects:                                                            # quiet courtyard: no flagstone marks in this look
        if o.name.startswith('flag'): o.hide_render = True
    R['h'] = A.hurdle(T, 'hurdle', 0.0)
    rnd = random.Random(7); R['spl'] = []
    for i in range(14):
        ob = A.prim('cube', f'spl{i}', T['red'] if i % 3 else T['wood'], None, (0, 0, -5), scl=(0.03 + 0.05 * rnd.random(), 0.012, 0.014))
        R['spl'].append((ob, Vector((rnd.uniform(-1.2, 1.2), rnd.uniform(0.8, 1.9), rnd.uniform(0.4, 1.8))), rnd.uniform(-25, 25)))
    K = A.knight(T); R['K'] = K; R['E'] = build_eyes(T, K)
    face = bpy.data.objects['knight_face']; face.data.materials[0] = A.toon('a_skin_flat', col=(228, 180, 146), shade=False)   # cel: base colour, the ONE shadow is drawn
    chip = bpy.data.objects['knight_chip']; chip.location = (0.1, 0.07, 0.17); chip.rotation_euler = Euler((0.8, 0.5, 0.9))   # on the steel, off the forehead                                                # the chip sits on the rim, not the forehead
    m_hi = A.toon('a_armour_hi', col=(250, 252, 255), shade=False)                       # deliberately placed armour highlights
    hel = bpy.data.objects['knight_helm']
    A.prim('cube', 'hi_dome', m_hi, hel, (-0.06, 0.07, 0.15), rot=(0.5, -0.35, 0.6), scl=(0.05, 0.004, 0.012))
    A.prim('cube', 'hi_pauld', m_hi, bpy.data.objects['knight_pauld-1'], (0.0, 0.55, 0.55), rot=(0.6, 0, 0.3), scl=(0.45, 0.04, 0.12))
    A.prim('cube', 'hi_visor', m_hi, K['visor'], (-0.07, 0.165, 0.03), rot=(0, 0, 0.4), scl=(0.05, 0.004, 0.006))
    I = A.instructor(T); R['I'] = I
    cam = A._link(bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))); sc.camera = cam; cam.data.sensor_fit = 'HORIZONTAL'; R['cam'] = cam
    sun = A._link(bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN'))); sun.data.energy = 4.0
    sun.rotation_euler = Vector((0.3, -0.42, -0.86)).to_track_quat('-Z', 'Y').to_euler()   # high, from the front: the visor shades the upper face
    try: sun.data.angle = math.radians(1.5)
    except Exception: pass
    A.look_setup(sc, lines=1.0)
    ink(sc, K)
    return sc, R

def ink(sc, K):
    """Freestyle: heavy ink on eyelids / brows / visor / helmet rim, a medium outer silhouette on the cast + hurdle, nothing on the courtyard"""
    def coll(name, pred):
        c = bpy.data.collections.new(name); sc.collection.children.link(c)
        for o in bpy.data.objects:
            if pred(o.name) and o.type in ('MESH', 'CURVE'): c.objects.link(o)
        return c
    heavy = coll('ink_heavy', lambda n: n.startswith(('lid_', 'lowlid_', 'brow_', 'eyew_', 'furrow_', 'face_shadow', 'knight_visorplate', 'knight_rim', 'knight_dome')))
    cast = coll('ink_cast', lambda n: n.startswith(('knight_', 'instr_', 'hurdle', 'spl')))
    fs = sc.view_layers[0].freestyle_settings
    for ls in list(fs.linesets): fs.linesets.remove(ls)
    def lineset(name, c, thick, col, crease):
        ls = fs.linesets.new(name); ls.select_by_collection = True; ls.collection = c; ls.collection_negation = 'INCLUSIVE'
        ls.select_by_visibility = True; ls.select_by_edge_types = True
        ls.select_silhouette = True; ls.select_border = True; ls.select_crease = crease; ls.select_contour = True; ls.select_external_contour = True
        st = ls.linestyle; st.thickness = thick; st.color = col
        return ls
    lineset('heavy', heavy, 2.3, (0.08, 0.05, 0.08), True)
    lineset('outline', cast, 1.6, (0.12, 0.09, 0.14), False)

# ---------------- per frame ----------------
def set_rot(ob, x=0.0, y=0.0, z=0.0): ob.rotation_euler = Euler((x, y, z))
def update(R, t):
    K, I, E = R['K'], R['I'], R['E']
    # ---- knight ----
    y = knight_y(t); K['root'].location = (0.0, y, 0.0)
    plant = sm(seg(t, *T_PLANT)); sho = sm(seg(t, *T_SHOULDER)) * (1 - sm(seg(t, T_CONTACT + 0.1, T_CONTACT + 0.45)))
    running = t >= T_SHOULDER[1]; ph = 2 * math.pi * 1.9 * (t - T_SHOULDER[1]); s = math.sin(ph) if running else 0.0
    K['pel'].location = (0, 0, 0.66 - 0.08 * plant * (1 - sm(seg(t, T_SHOULDER[1], T_SHOULDER[1] + 0.2))) + (0.03 * abs(math.cos(ph)) if running else 0))
    set_rot(K['tor'], x=-(0.04 + 0.12 * plant + 0.42 * sho + (0.1 if running else 0)), z=-0.5 * sho)
    # the plant: right foot steps back, knees bend; then the run cycle
    if not running:
        set_rot(K['hipr'], x=-0.35 * plant); set_rot(K['hipl'], x=0.25 * plant); set_rot(K['knr'], x=-0.35 * plant); set_rot(K['knl'], x=-0.3 * plant)
    else:
        set_rot(K['hipr'], x=0.75 * s); set_rot(K['hipl'], x=-0.75 * s); set_rot(K['knr'], x=-0.95 * max(0, -s) - 0.1); set_rot(K['knl'], x=-0.95 * max(0, s) - 0.1)
    if sho > 0: set_rot(K['shl'], x=0.8 * sho, z=0.35 * sho); set_rot(K['ell'], x=1.7 * sho); set_rot(K['shr'], x=-0.5 * sho); set_rot(K['elr'], x=1.2)
    else: set_rot(K['shl'], x=0.1); set_rot(K['ell'], x=0.25); set_rot(K['shr'], x=0.1); set_rot(K['elr'], x=0.25)
    if running and sho < 0.3: set_rot(K['shr'], x=-0.5 * s); set_rot(K['shl'], x=0.5 * s); set_rot(K['elr'], x=1.1); set_rot(K['ell'], x=1.1)
    # head: watches the jump (turned right towards it, rising with it), in the close-up tilts down to the hurdle at the decision
    if t < S_B:
        up = 0.25 * math.sin(math.pi * seg(t, I_CROUCH[1], I_LAND[1])); set_rot(K['head'], x=up, z=-0.35)
    elif t < S_C:
        dn = sm(seg(t, T_DECIDE - 0.03, T_DECIDE + 0.12)); set_rot(K['head'], x=lerp(0.12, -0.12, dn), z=lerp(-0.22, -0.08, dn))
    else: set_rot(K['head'], x=-0.15 - 0.2 * sho, z=0.0)
    set_rot(K['visor'], x=0.55)                                                          # the visor rides low, like a brim over the shadow
    K['mouth'].scale = (0.045, 0.01, 0.008)                                              # a flat, serious line
    # eyes: WATCH (following up) -> DECIDE (snap down, lids lower, brows settle) - the decision reads in the eyes alone
    if t < S_B: p = mix_pose(POSES['neutral'], POSES['watch'], sm(seg(t, 0.2, 0.6)))
    elif t < T_DECIDE: p = POSES['watch']
    else: p = mix_pose(POSES['watch'], POSES['decide'], sm(seg(t, T_DECIDE, T_DECIDE + 0.14)))
    if t >= S_C: p = POSES['decide']
    pose_eyes(E, p)
    # ---- the hurdle breaks at the contact (crack on the contact frame, then the halves fly) ----
    for ob, home, j, sd in R['h']['pieces']:
        if t < T_CONTACT: ob.location = home; ob.rotation_euler = Euler((0, 0, 0)); continue
        u = t - T_CONTACT; crack = min(1.0, u / 0.05)
        v0 = Vector((sd * (0.9 + 0.7 * j), 1.9 + 0.5 * (1 - j), 1.0 + 1.1 * j)); g = 9.8
        p_ = home + v0 * max(0.0, u - 0.02) + Vector((0, 0, -0.5 * g * max(0.0, u - 0.02) ** 2)); p_.z = max(0.07, p_.z)
        ob.location = p_; ob.rotation_euler = Euler((sd * 0.25 * crack + sd * 5 * max(0, u - 0.02), 2.5 * max(0, u - 0.02), sd * 0.35 * crack + sd * 3 * max(0, u - 0.02)))
    for sd in (1, -1):
        post = bpy.data.objects[f'hurdle_post{sd}']; post.rotation_euler = Euler((0.3 * sm(seg(t, T_CONTACT, T_CONTACT + 0.2)), -sd * 0.15 * sm(seg(t, T_CONTACT, T_CONTACT + 0.2)), 0))
    for ob, v0, spin in R['spl']:
        if t < T_CONTACT or t > T_CONTACT + 0.8: ob.location = (0, 0, -5); continue
        u = t - T_CONTACT; p_ = Vector((-0.05, 0.0, 0.88)) + v0 * u + Vector((0, 0, -4.9 * u * u)); p_.z = max(0.02, p_.z); ob.location = p_; ob.rotation_euler = Euler((spin * u, spin * 0.5 * u, 0))
    # ---- the instructor: a proper jump over the hurdle, lands, steps aside (off screen during the close-up) ----
    if t < S_B:
        c = 0.25 * sm(seg(t, *I_CROUCH)) * (1 - sm(seg(t, I_JUMP[0], I_JUMP[0] + 0.06))) + 0.2 * math.sin(math.pi * seg(t, *I_LAND))
        u = seg(t, *I_JUMP); air = I_JUMP[0] <= t < I_JUMP[1]
        I['root'].location = (I_X, lerp(I_Y0, I_Y1, u), 0.75 * math.sin(math.pi * u) if air else 0.0); set_rot(I['root'], z=0.0)
        tuck = math.sin(math.pi * u) if air else 0.0
        I['pel'].location = (0, 0, 1.02 - 0.42 * c); set_rot(I['tor'], x=-(0.3 * c + 0.15 * tuck))
        set_rot(I['hipr'], x=0.9 * c + 1.4 * tuck); set_rot(I['hipl'], x=0.9 * c + 1.4 * tuck); set_rot(I['knr'], x=-1.8 * c - 2.1 * tuck); set_rot(I['knl'], x=-1.8 * c - 2.1 * tuck)
        arms = 2.6 * (tuck if air else sm(seg(t, I_LAND[0], I_LAND[1])) * (1 - sm(seg(t, 0.92, 1.0))))
        set_rot(I['shr'], x=arms, y=0.3 * arms / 2.6); set_rot(I['shl'], x=arms, y=-0.3 * arms / 2.6); set_rot(I['elr'], x=0.1); set_rot(I['ell'], x=0.1)
        set_rot(I['head'], x=0.1)
    else:
        I['root'].location = (I_ASIDE[0], I_ASIDE[1], 0.0); set_rot(I['root'], z=math.pi + 0.5); I['pel'].location = (0, 0, 1.02)
        for k_ in ('tor', 'hipr', 'hipl', 'knr', 'knl', 'shr', 'shl'): set_rot(I[k_])
        set_rot(I['shr'], x=-0.3, y=-0.25); set_rot(I['shl'], x=-0.3, y=0.25); set_rot(I['elr'], x=0.1); set_rot(I['ell'], x=0.1)
    # ---- cameras ----
    cam = R['cam']
    if t < S_B:   # wide side: the knight on the left facing right, the jump in the middle
        pos = Vector((3.1, -0.95, 1.35)) + Vector((0, 0.1 * t, 0)); tgt = Vector((0.0, -0.85, 1.15)); fov = 62.0
    elif t < S_C: # tight under the visor, a slow push
        hp = Vector((0.0, K_Y0, 1.33)); u = seg(t, S_B, S_C)
        pos = hp + Vector((0.13, 0.62 - 0.08 * u, 0.02)); tgt = hp + Vector((0.0, 0.0, 0.015)); fov = 21.0
    else:         # three-quarter side: contact + the board breaking in one frame, the next stride beyond it
        pos = Vector((2.35, 1.2, 1.1)); tgt = Vector((-0.05, -0.45, 0.85)); fov = 56.0
    if T_CONTACT <= t < T_CONTACT + 0.2: pos = pos + Vector((0, 0, 0.03 * math.sin((t - T_CONTACT) * 90) * (1 - (t - T_CONTACT) / 0.2)))
    cam.location = pos; cam.rotation_euler = (tgt - pos).to_track_quat('-Z', 'Y').to_euler(); cam.data.angle_x = math.radians(fov)

if __name__ == '__main__':
    sc, R = build()
    def handler(scene, *_): update(R, (scene.frame_current - 1) / FPS)
    bpy.app.handlers.frame_change_pre.append(handler)
    if MODE == 'anim':
        d = os.path.join(OUT, 'frames'); os.makedirs(d, exist_ok=True)
        fa, fb = map(int, os.environ.get('FRAMES', f'1-{NF}').split('-')) if '-' in os.environ.get('FRAMES', '-') else (1, NF)
        update(R, (fa - 1) / FPS); sc.frame_set(fa); sc.frame_start, sc.frame_end = fa, fb; sc.render.fps = FPS; sc.render.filepath = os.path.join(d, 'f_'); bpy.ops.render.render(animation=True)
    else:
        for f in [int(x) for x in os.environ.get('FRAMES', '1').split(',')]:
            sc.frame_set(f); update(R, (f - 1) / FPS); sc.render.filepath = os.path.join(OUT, 'still_%04d.png' % f); bpy.ops.render.render(write_still=True)
    print('RENDER done')
