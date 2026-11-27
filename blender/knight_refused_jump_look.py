"""THE KNIGHT WHO REFUSED TO JUMP - 4 s vertical look test (Blender 5.3, 28 Nov 2026), art direction briefs/ART_DIRECTION_insert_disc_2.md.
Reusable assets: blender/id2_assets.py (painted atlases, broad-shadow toon material, knight, instructor, breakable hurdle, courtyard).
Beats (each its own moment at phone size):
  0.00  mid-run; a red plank from hurdle 1 hooked over his shoulder; hurdle 2 intact ahead; beyond it the tall instructor at the top
        of an immaculate demo jump, knees tucked, pointing proudly at his feet.
  0.35-0.90  BEAT 1 - the knight sees him: a confident little nod.
  1.00-1.45  lowers his shoulder ... 1.45 BEAT 2 - straight through hurdle 2, the visor drops over his eyes on impact.
  0.60  the instructor lands neatly, still pointing at his feet (never stops).
  2.40-3.60  BEAT 3 - the knight runs past blind: ONLY the instructor's eyes move, sideways (camera has pushed in on him).
Steps: python blender/id2_assets.py <tex>   (system python paints the atlases; Blender's python has no PIL)
       blender -b --factory-startup --python blender/knight_refused_jump_look.py      (MODE=still FRAMES=1,20 | MODE=anim)"""
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bpy
from mathutils import Vector, Euler
import id2_assets as A
MODE = os.environ.get('MODE', 'still')
OUT = os.path.join(HERE, '..', '..', 'renders', 'knight_refused_jump'); TEX = os.path.join(OUT, 'tex'); os.makedirs(OUT, exist_ok=True)
FPS = 24; DUR = 4.0; NF = int(DUR * FPS)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def seg(t, a, b): return clamp((t - a) / (b - a))
def sm(u): u = clamp(u); return u * u * (3 - 2 * u)
def win(t, a, b, r=0.15): return sm(seg(t, a, a + r)) * (1 - sm(seg(t, b - r, b)))
def lerp(a, b, u): return a + (b - a) * u
def lerpv(a, b, u): return Vector(a).lerp(Vector(b), u)

# ---------------- beats ----------------
T_NOD = (0.35, 0.9); T_SHOULDER = (1.0, 1.42); T_HIT = 1.45; T_LAND = 0.6; T_GLANCE = (2.4, 3.6)
I_POS = (-0.95, 2.2); I_APEX = 0.5
def knight_y(t): return -2.9 + 1.76 * t if t < T_HIT else -0.35 + 1.9 * (t - T_HIT)

def build():
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    sc = bpy.context.scene; T = A.materials(TEX); R = {}
    A.courtyard(T, back_y=-7.5)
    for nm in ('wall1', 'wall-1', 'wall_back'):                                           # lower walls: pale, quiet, they do not shade the yard
        ob = bpy.data.objects[nm]; ob.scale.z = 2.8; ob.location.z = 1.4
    for nm in ('wall_cap1', 'wall_cap-1'): bpy.data.objects[nm].location.z = 2.86                                                           # the far wall stands behind the knight
    A.hurdle(T, 'hurdle1_ruin', -6.5)                                                    # (off-screen behind) where the plank came from
    R['h2'] = A.hurdle(T, 'hurdle2', 0.0)
    rnd = random.Random(5); R['splinters'] = []
    for i in range(12):                                                                   # splinters: hidden until the hit
        ob = A.prim('cube', f'spl{i}', T['red'] if i % 3 else T['wood'], None, (0, 0, -5), scl=(0.03 + 0.04 * rnd.random(), 0.012, 0.012))
        R['splinters'].append((ob, Vector((rnd.uniform(-1, 1), rnd.uniform(0.6, 1.6), rnd.uniform(0.8, 2.2))), rnd.uniform(-20, 20)))
    K = A.knight(T); R['K'] = K
    R['plank'] = A.plank(T, 'shoulder_plank', K['tor'], (0.33, -0.08, 0.6), (0.25, -0.55, 1.5))       # hooked over the right shoulder
    I = A.instructor(T); R['I'] = I
    cam = A._link(bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))); sc.camera = cam; cam.data.sensor_fit = 'HORIZONTAL'; R['cam'] = cam
    sun = A._link(bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN'))); sun.data.energy = 4.0
    sun.rotation_euler = Vector((-0.28, -0.32, -0.9)).to_track_quat('-Z', 'Y').to_euler()          # from behind the camera, high-right: fronts lit, far sides in broad shadow        # from the camera side: walls + ground lit, far sides in broad shadow            # from the front-right, high: broad shadow sides
    try: sun.data.angle = math.radians(3)
    except Exception: pass
    A.look_setup(sc)
    return sc, R

def set_rot(ob, x=0.0, y=0.0, z=0.0): ob.rotation_euler = Euler((x, y, z))
def update(R, t):
    K, I = R['K'], R['I']
    # ---------------- knight ----------------
    y = knight_y(t); ph = 2 * math.pi * 1.7 * t; s = math.sin(ph)
    K['root'].location = (0.0, y, 0.0); K['pel'].location = (0, 0, 0.66 + 0.035 * abs(math.cos(ph)))
    sho = sm(seg(t, *T_SHOULDER)) * (1 - sm(seg(t, T_HIT + 0.05, T_HIT + 0.45)))           # shoulder down, then up again
    lean = 0.14 + 0.35 * sho; twist = -0.45 * sho
    set_rot(K['tor'], x=-lean, z=twist)
    set_rot(K['hipr'], x=0.7 * s); set_rot(K['hipl'], x=-0.7 * s)
    set_rot(K['knr'], x=-0.95 * max(0.0, -s) - 0.1); set_rot(K['knl'], x=-0.95 * max(0.0, s) - 0.1)
    shr = [-0.5 * s, 0, 0]; shl = [0.5 * s, 0, 0]; elr = 1.1; ell = 1.1
    if sho > 0: shl = [lerp(0.5 * s, 0.9, sho), 0, lerp(0, 0.4, sho)]; ell = lerp(1.1, 1.8, sho); shr = [lerp(-0.5 * s, -0.6, sho), 0, 0]
    set_rot(K['shr'], *shr); set_rot(K['shl'], *shl); set_rot(K['elr'], x=elr); set_rot(K['ell'], x=ell)
    # head: sees the instructor (up-right), the confident little nod, tucks for the hit, then up again (blind, unbothered)
    look = win(t, 0.2, 1.0, 0.18); nod = math.sin(math.pi * seg(t, 0.5, 0.82)) if 0.5 <= t < 0.82 else 0.0
    hx = 0.12 * look - 0.38 * nod - 0.25 * sho; hz = -0.28 * look
    set_rot(K['head'], x=hx, z=hz)
    smirk = win(t, 0.45, 1.05, 0.12)
    K['mouth'].scale = (0.05 + 0.025 * smirk, 0.01, 0.012 if t < T_HIT else 0.03 * win(t, T_HIT, T_HIT + 0.5, 0.08) + 0.012)
    K['mouth'].rotation_euler = Euler((0, 0.25 * smirk, 0))
    K['brows'][0].location = (0.05, 0.12, 0.068 + 0.02 * smirk)                          # one brow up with the nod
    # the visor: rests up, drops over the eyes ON the impact (with a bounce)
    if t < T_HIT: va = 1.35
    else:
        u = t - T_HIT; va = 1.35 * max(0.0, 1 - u / 0.07) + 0.12 * math.exp(-10 * u) * abs(math.sin(30 * u)) * (u > 0.07)
    set_rot(K['visor'], x=va)
    R['plank'].rotation_euler = Euler((0.25 + 0.06 * math.sin(ph * 2), -0.55, 1.5 + 0.05 * s))   # the hooked plank jiggles with every step
    # ---------------- hurdle 2 bursts ----------------
    for ob, home, j, sd in R['h2']['pieces']:
        if t < T_HIT: ob.location = home; ob.rotation_euler = Euler((0, 0, 0)); continue
        u = t - T_HIT; v0 = Vector((sd * (1.0 + 0.6 * j), 1.6 + 0.6 * (1 - j), 1.4 + 1.2 * j)); g = 9.8
        p = home + v0 * u + Vector((0, 0, -0.5 * g * u * u)); land = p.z < 0.07
        if land:                                                                          # lies where it lands
            tl = (v0.z + math.sqrt(v0.z ** 2 + 2 * g * (home.z - 0.07))) / g; p = home + v0 * tl + Vector((0, 0, -0.5 * g * tl * tl)); p.z = 0.07; u = tl
        ob.location = p; ob.rotation_euler = Euler((sd * 6 * u, 3 * u, sd * 4 * u))
    for sd in (1, -1):
        post = bpy.data.objects[f'hurdle2_post{sd}']; post.rotation_euler = Euler((0.25 * sm(seg(t, T_HIT, T_HIT + 0.25)), -sd * 0.2 * sm(seg(t, T_HIT, T_HIT + 0.25)), 0))
    for ob, v0, spin in R['splinters']:
        if t < T_HIT or t > T_HIT + 0.9: ob.location = (0, 0, -5); continue
        u = t - T_HIT; p = Vector((0, -0.1, 0.8)) + v0 * u + Vector((0, 0, -4.9 * u * u)); p.z = max(0.02, p.z); ob.location = p; ob.rotation_euler = Euler((spin * u, spin * 0.6 * u, 0))
    # ---------------- instructor: the end of a perfect demo jump, lands, keeps pointing; only the eyes move ----------------
    I['root'].location = (I_POS[0], I_POS[1], I_APEX * max(0.0, 1 - (t / T_LAND) ** 2) if t < T_LAND else 0.0)
    set_rot(I['root'], z=0.12)                                                            # faces the camera (he demonstrates to us); the knight passes on his right
    tuck = 1.0 - sm(seg(t, 0.3, 0.55)); land = math.sin(math.pi * seg(t, T_LAND, T_LAND + 0.3)) if T_LAND <= t < T_LAND + 0.3 else 0.0
    I['pel'].location = (0, 0, 1.02 - 0.12 * land)
    set_rot(I['tor'], x=0.08 - 0.05 * land)                                               # chest out
    set_rot(I['hipr'], x=1.75 * tuck + 0.35 * land, y=0.3 * tuck); set_rot(I['hipl'], x=1.75 * tuck + 0.35 * land, y=-0.3 * tuck)
    set_rot(I['knr'], x=-2.5 * tuck - 0.7 * land); set_rot(I['knl'], x=-2.5 * tuck - 0.7 * land)
    set_rot(I['shr'], x=0.42, y=0.0, z=-0.08); set_rot(I['elr'], x=0.05)                  # pointing proudly at his feet
    set_rot(I['shl'], x=-0.15, y=-0.55, z=0.0); set_rot(I['ell'], x=1.75)                 # other hand on the hip
    set_rot(I['head'], x=0.14)                                                            # chin up, never moves
    gl = sm(seg(t, T_GLANCE[0], T_GLANCE[0] + 0.25)) + 0.6 * sm(seg(t, 2.95, 3.3))        # the eyes slide sideways after the knight
    for sd, pu in zip((1, -1), I['pupils']): pu.location = (sd * 0.044 + 0.024 * min(1.0, gl), 0.112 - 0.006 * min(1.0, gl), 0.02 - 0.003 * gl)
    I['mouth'].scale = (0.05, 0.008, 0.008)
    # ---------------- camera: three-quarter side, diagonal (knight lower-left, hurdle centre, instructor upper-right); pushes in for the glance
    p0, g0, f0 = (1.15, 10.0, 1.4), (-0.62, 0.3, 1.12), 18.0                            # ahead of the run, a long lens (depth compressed): knight
    p1, g1, f1 = (1.05, 9.7, 1.4), (-0.64, 0.35, 1.12), 18.0                            # upper-left, hurdle centre, instructor lower-right; a slow creep
    u = sm(seg(t, 0.0, DUR)); pos = lerpv(p0, p1, u); tgt = lerpv(g0, g1, u)
    if T_HIT <= t < T_HIT + 0.25: pos = pos + Vector((0, 0, 0.05 * math.sin((t - T_HIT) * 80) * (1 - (t - T_HIT) / 0.25)))
    cam = R['cam']; cam.location = pos; cam.rotation_euler = (tgt - pos).to_track_quat('-Z', 'Y').to_euler(); cam.data.angle_x = math.radians(lerp(f0, f1, u))

if __name__ == '__main__':
    sc, R = build()
    def handler(scene, *_): update(R, (scene.frame_current - 1) / FPS)
    bpy.app.handlers.frame_change_pre.append(handler)
    if MODE == 'anim':
        d = os.path.join(OUT, 'frames'); os.makedirs(d, exist_ok=True)
        update(R, 0.0); sc.frame_set(1); sc.frame_start, sc.frame_end = 1, NF; sc.render.fps = FPS; sc.render.filepath = os.path.join(d, 'f_'); bpy.ops.render.render(animation=True)
    else:
        for f in [int(x) for x in os.environ.get('FRAMES', '1').split(',')]:
            sc.frame_set(f); update(R, (f - 1) / FPS); sc.render.filepath = os.path.join(OUT, 'still_%04d.png' % f); bpy.ops.render.render(write_still=True)
    print('RENDER done')
