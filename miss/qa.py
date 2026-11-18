"""Section 11: continuity asserts, run programmatically before encoding. Every rule reports PASS, FAIL or DEVIATION.
DEVIATION = the brief's own tables contradict the rule (the tables are authoritative, the conflict is logged in NOTES.md and shown here with the real numbers).
A FAIL blocks encoding."""
import math
import numpy as np
import raster as R, world as WORLD, characters as CH, timeline as T, scene as S, font as FNT

def _aabb(faces):
    p = np.concatenate([f.p for f in faces]); return p.min(0), p.max(0)

def _seg_point_dist(a, b, p):
    a = np.asarray(a, float); b = np.asarray(b, float); p = np.asarray(p, float); d = b - a; u = np.clip(((p - a) @ d) / (d @ d + 1e-12), 0, 1); return float(np.linalg.norm(p - (a + d * u)))

def run_qa(cut, audio_info=None):
    C = T.CUTS[cut]; N = C['frames']; res = []                            # (status, rule, detail)
    def add(ok, rule, detail, dev=False): res.append(('DEVIATION' if (dev and not ok) else ('PASS' if ok else 'FAIL'), rule, detail))

    # ---- arrow ledger, every frame
    bad = []; q_prev = T.Q0
    for f in range(N):
        L = T.ledger(cut, f); tot = L['floor'] + L['gob'] + L['archer'] + L['crate'] + L['inflight']
        if tot != L['released'] or min(L['floor'], L['gob'], L['archer'], L['crate']) < 0: bad.append((f, L['released'], tot))
        if L['quiver'] > q_prev: bad.append((f, 'quiver grew', L['quiver']))
        q_prev = L['quiver']
    add(not bad, 'arrow ledger: floor + hands + crate + in flight == arrows released, at every frame (quiver never grows)', f'{N} frames checked' + (f', first mismatch {bad[0]}' if bad else ''))
    chk = ([(91, 'floor', 1), (157, 'floor', 3), (263, 'floor', 2), (263, 'gob', 1), (313, 'archer', 1), (313, 'floor', 2)] if cut == 'master' else
           [(177, 'floor', 4), (268, 'floor', 5), (371, 'floor', 4), (371, 'gob', 1), (505, 'crate', 3), (505, 'floor', 2), (567, 'archer', 1), (567, 'floor', 1), (567, 'crate', 3)])
    miss = [(f, k, T.ledger(cut, f)[k], v) for f, k, v in chk if T.ledger(cut, f)[k] != v]
    add(not miss, 'arrow ledger checkpoints from the brief', f'{len(chk)} checkpoints' + (f', mismatches {miss}' if miss else ''))
    if cut == 'master':
        add(False, "brief's master ledger says 'handed to the archer = 1 in hand, floor 1'", 'conservation gives floor 2 (3 released = 1 in hand + 2 on the floor)', dev=True)
    qs = [T.ledger(cut, f)['quiver'] for f in range(N)]; add(qs[-1] == T.Q0 - len(C['releases']), 'quiver shows one shaft fewer per release', f'{T.Q0} -> {qs[-1]} shafts')

    # ---- per-frame geometry: scale, intersections, arrows, camera
    hA, hG, ratio, intersections, tips, camfail, cams_px, face_px, string_d, ears_x = [], [], [], [], [], [], {}, [], [], []
    for f in range(N):
        faces, ast, gst = S.scene_faces(cut, f); cam = S.camera_for(cut, f)
        a_faces = CH.make_archer(ast); g_faces = CH.make_goblin(gst); a_lo, a_hi = _aabb(a_faces); g_lo, g_hi = _aabb(g_faces)
        sq = gst.get('squash') or 1.0
        if sq == 1.0 and gst['pose'] not in ('LOOK_DOWN',): hG.append(g_hi[1] - g_lo[1])
        hA.append(a_hi[1] - a_lo[1])
        # no character box intersects another: body AABB of the archer (torso, legs, head) vs the goblin's AABB
        ax, az = ast['pos']; body = (np.array([ax - 0.17, 0.0, az - 0.10]), np.array([ax + 0.17, 1.02, az + 0.10]))   # torso half-depth 0.07, head half-depth 0.10
        ov = np.minimum(body[1], g_hi) - np.maximum(body[0], g_lo)
        if (ov > 0).all(): intersections.append((f, 'archer body vs goblin', float(ov.min())))
        ov2 = np.minimum(np.array([7.0, 9, 9]), g_hi) - np.array([6.96, -9, -9])                    # the board / end wall
        if g_hi[0] > 6.96: intersections.append((f, 'goblin vs board/end wall', float(g_hi[0] - 6.96)))
        ears_x.append(g_hi[0])
        info = CH.archer_info(ast); sd = min(_seg_point_dist(info['string_a'], info['string_b'], info['hand_L'] + (info['elbow_L'] - info['hand_L']) * t) for t in (0.0, 0.1, 0.2, 0.3)); string_d.append((sd, f))
        # arrows: tip never beyond the wall plane
        for tail, d in T.flying_arrows(cut, f) + T.floor_arrows(cut, f): tips.append(float((tail + d * CH.ARROW_TIP)[0]))
        # camera inside a wall AABB (including the CAM A push-in)
        for n_, b in WORLD.WALLS.items():
            if WORLD._inside(cam.pos, b): camfail.append((f, n_))
        # projected heights (per camera) and face size
        pf = cam.project((ax, 0.0, az)); pt = cam.project((ax, 1.0, az))
        if pf and pt and 0 < pf[1] < R.H and 0 < pt[1] < R.H: cams_px.setdefault(cam.name, []).append((pf[1] - pt[1], pf[2]))
        hp = cam.project((ax, 0.85, az)); gp = cam.project((gst['pos'][0], 0.40 * sq, gst['pos'][1]))
        on = lambda q: q is not None and 0 < q[0] < R.W and 0 < q[1] < R.H and q[2] > 0.3          # only heads that are actually on screen
        if on(hp): face_px.append((0.22 * cam.fpx / hp[2], f, 'archer head'))
        if on(gp): face_px.append((0.16 * cam.fpx / gp[2], f, 'goblin head'))
    add(max(hA) - min(hA) < 0.12 and 0.97 < min(hA) and max(hA) < 1.08, 'archer scale: world height identical in every shot (pose lean allowed)', f'archer {min(hA):.3f}..{max(hA):.3f} (target 1.00)')
    gt = np.array(hG); add(0.495 <= gt.min() and gt.max() <= 0.55, 'goblin scale: 0.52 world units (52 % of the archer), measured in every standing/walking frame', f'goblin {gt.min():.3f}..{gt.max():.3f}; ratio {np.mean(gt) / np.mean(hA):.2f}')
    lines = []
    for k, v in sorted(cams_px.items()):
        px = np.array([a for a, _ in v]); dp = np.array([d for _, d in v]); fpx = WORLD.CAMERAS[k].fpx; expect = fpx * 1.0 / dp
        lines.append(f'CAM {k}: archer {px.min():.0f}-{px.max():.0f} px tall, expected {expect.min():.0f}-{expect.max():.0f} px (fpx*H/depth)')
    ok_cam = all(abs(np.mean([a / (fpx_ * 1.0 / d) for a, d in v]) - 1) < 0.25 for k, v in cams_px.items() for fpx_ in [WORLD.CAMERAS[k].fpx])
    add(ok_cam, 'projected archer height matches the expected range in every camera', '; '.join(lines) if lines else 'archer is not fully visible in most cameras')
    add(not intersections, 'no character box intersects another character / the board (AABB each frame)', 'worst: ' + (str(max(intersections, key=lambda x: x[2])) if intersections else 'none') + f'; goblin max x {max(ears_x):.3f} (< 6.96, ears vs wall in CAM C)')
    sd = min(string_d); add(sd[0] > 0.0275, 'bow string never touches the hand (string to the last 30 % of the left forearm, thickness included)', f'min clearance {sd[0] - 0.0275:+.3f} units at frame {sd[1]}')
    add(not camfail, 'no camera position is inside any wall AABB (every frame, incl. the CAM A push-in)', 'ok' if not camfail else str(camfail[:3]))
    for k, rule, ok, detail in WORLD.check_cameras(): add(ok, f'CAM {k}: {rule}', detail)
    add(max(tips) <= 7.0 + 1e-6, 'no arrow ever penetrates the wall plane or the board (tip x <= 7.0)', f'max tip x {max(tips):.4f}')
    flights = []
    for r in C['releases']:
        xs = [T.flying_arrows(cut, f)[0][0][0] for f in range(r, r + T.FLIGHT + 1)]; d = np.diff(xs); flights.append(float(d.max() - d.min()))
    add(max(flights) < 1e-9, 'arrows travel in a straight line at constant speed and stop at the wall plane', f'{len(flights)} flights, speed variation {max(flights):.1e}')
    big = [x for x in face_px if x[0] > R.H / 4]; add(not big, 'no face is shown larger than 1/4 of the frame height (projected head height)', f'largest {max(face_px)[0]:.0f} px ({max(face_px)[2]}, frame {max(face_px)[1]}); limit {R.H // 4} px')

    # ---- cuts
    spans = [(b - a) for a, b, _ in C['cams']]; add(min(spans) >= 29, 'no cut shorter than 29 frames (1.20 s)', f'shortest camera span {min(spans)} frames; first cut at frame {C["cams"][0][1]}')
    # ---- framing rules
    a0 = S.camera_for(cut, 0); ax, az = T.archer_pos(cut, 0); pa = a0.project((ax, 0.9, az)); pb = a0.project((6.98, 0.78, 0.0))
    add(pa[0] / R.W < 1 / 3 and pb[0] / R.W > 2 / 3, 'CAM A frames the archer in the left third and the board in the right third', f'archer x={pa[0] / R.W:.2f}, board x={pb[0] / R.W:.2f}')
    # ---- subtitles
    subs = C['subs']; ovl = [(a, b) for a, b in zip(subs, subs[1:]) if b[0] < a[1]]; add(not ovl, 'no subtitle overlaps another', f'{len(subs)} lines')
    nl = max(len(S.sub_layout(t, h)) for _, _, t, h in subs); add(nl <= 2, 'every subtitle fits on at most two lines', f'max {nl} lines (width {S.MAXW}px)')
    lifts = 0; collide = 0
    for f in range(N):
        faces, ast, gst = S.scene_faces(cut, f); place = S.subtitle_placement(cut, f, S.camera_for(cut, f), gst)
        if place:
            if place[3]: lifts += 1
            if S.collisions(cut, f, S.camera_for(cut, f), gst, place[4]): collide += 1
    add(collide == 0, "subtitles never cover the goblin's face or the bullseye (moved up 4 px when needed)", f'{lifts} frames needed a lift, {collide} collisions left')
    if cut == 'master': add(False, "subtitle 'Five shots. Five misses.' is kept exactly as written", 'the master cut shows 3 shots (1 + 2), the extended 4 before it; text is not changed', dev=True)
    if cut == 'extended': add(False, "'S8 button: NO subtitle' vs 'f658-701 Not once.' inside S8", 'the explicit frame line wins: \"Not once.\" shows 658-701, S8 has no other subtitle', dev=True)
    # ---- popups
    mx = max(len(T.popup_at(cut, f)) for f in range(N)); add(mx <= 2, 'never more than two popups on screen at once', f'max {mx}')
    # ---- ducks vs arrows and blips
    rel = C['releases']; ducks = C['ducks']; misses = [t for t, k in C['popups']]
    matched = [(max(r for r in rel if r < d), d) for d in ducks if any(r < d < r + 40 for r in rel)]
    late = [(r, d, r + T.FLIGHT) for r, d in matched if not d > r + T.FLIGHT]
    add(not late, 'the goblin ducks AFTER each arrow has already missed (duck frame > arrow arrival)', ', '.join(f'release {r}: arrival {r + T.FLIGHT}, duck {d}' for r, d in matched) + (f'; early: {late}' if late else ''))
    early_ok = [d for d in ducks if not any(r < d < r + 40 for r in rel)]
    add(early_ok == ([686] if cut == 'extended' else []), 'only frame 686 (extended) is a duck with no arrow before it', f'duck frames without an arrow: {early_ok}')
    deltas = []
    for r, d in matched:
        m = min((t for t in misses if t >= r), default=None); deltas.append((r, d, m, d - m if m is not None else None))
    off = [x for x in deltas if x[3] != 6]
    add(not off, 'goblin ducks 6 frames after miss_blip in every shot (duck_step sfx 6 frames after miss_blip)', 'frame table gives ' + ', '.join(f'MISS {m}/duck {d} ({dd:+d})' for r, d, m, dd in deltas), dev=True)
    # ---- audio
    if audio_info:
        add(abs(audio_info['lufs'] + 16) < 0.5, 'integrated loudness is -16 LUFS (ffmpeg ebur128)', f"{audio_info['lufs']:.2f} LUFS"); add(audio_info['peak_db'] < -1.0, 'peaks under -1 dBFS', f"{audio_info['peak_db']:.2f} dBFS")
    return res

def format_report(cut, res):
    c = {'PASS': 0, 'FAIL': 0, 'DEVIATION': 0}
    for st, _, _ in res: c[st] += 1
    out = [f'=== {cut} cut: {c["PASS"]} PASS, {c["FAIL"]} FAIL, {c["DEVIATION"]} DEVIATION ===']
    for st, rule, detail in res: out.append(f'{st:9s} {rule}\n          -> {detail}')
    return '\n'.join(out) + '\n', c
