# PIPELINE — visual consistency & render quality (all Insert Disc 2 / Vidivenigaming shorts)

Visual consistency and character continuity come first. Long videos are never rendered in one uncontrolled pass:
every short goes through the five phases below, and a phase is only reported as done when it was actually run.

## Phase 1 — Asset lock
nightkit is procedural, so "assets" are code. One function or constant is the single source of truth for each:
- **Characters:** a model function with fixed proportions, palette and clothing, for example `knight()` and `boss()`
  in `examples/final_boss.py`. Poses are parameters (hands, lean, walk, sword state), never a second model.
- **Environment and props:** built once at import (`ARENA`, `gate_doors()`, `torches()`, `barrier_quads()`, the
  dropped sword `sword_on_floor()`).
- **Look:** the palette constants, `Renderer` fog, `zrender` lighting, `post.ps1` and `post.VHS` settings.
- **Reuse:** a variant of a video (for example Experiment B) imports the original module and reuses these
  functions. It never copies and edits them. Shared shots call the original `frame()` directly, so they are
  pixel-identical.
- **Changes:** a model is changed only in its one function, and every video that uses it is re-checked and
  re-rendered.

## Phase 2 — Storyboard validation (scene manifest)
Each script ends with a `QA = dict(...)` manifest. `scenes` lists every shot with its time span, one main action,
the environment and flags (`set='outside'`, `pov=True`). `tools/qa/scene_qa.py` derives the rest and writes it
to `out/qa/<script>/report.md`:
- the start and end position of each character
- the camera start and end
- the objects held at the start and end of the shot

The manifest also declares the events that are allowed on screen:
- **`weapon_events`:** for example a sword drawn, or a sword dropped.
- **`crossings`:** when a body may pass through the barrier.
- **`allow_jump`:** jumps across a cut where the character was off-screen.

## Phase 3 — Preview render
`python tools/qa/scene_qa.py examples/<script>.py` renders a contact sheet for every scene at internal resolution
(180x320). Each sheet shows the start, the 25/50/75 % points and the end. It also writes an overview strip.
`--scenes id1,id2` re-renders only the scenes you name, and `TEST=t1,t2 python examples/<script>.py` renders
single frames.

Review every sheet by eye for:
- appearance and proportions
- hands, arms, legs, heads and weapons
- contact with doors, levers and walls
- camera framing
- whether the action reads without narration

A serious error means the scene is revised and previewed again before any final render. Errors are never hidden
with glitch effects.

## Phase 4 — Visual error checklist
Automatic checks run on every frame (`scene_qa.py`). Everything else is checked by eye on the sheets.

| Error | How it is caught |
|---|---|
| Teleporting within a shot (> 0.3 m or > 40°/frame) | automatic: `teleport` |
| Position jump across a cut (> 0.5 m) not declared | automatic: `cut-jump` |
| Weapon appears, disappears or changes hands without an on-screen action | automatic: `weapon` |
| Body through the barrier, a wall or the floor | automatic: `barrier`, `wall`, `floor` |
| Characters interpenetrate | automatic: `intersect` |
| Camera inside a wall, or near-plane clipping a character | automatic: `camera` |
| Text wider than the frame, or a glyph missing from the font | automatic: `text` |
| Extra or missing limbs, changing faces or clothing, morphing, duplication, unreadable movement, floating objects, distorted text, framing (for example a character filling the frame) | manual, on the contact sheets |

## Phase 5 — Final render
Render only after phases 3 and 4 are clean.
1. Render in parallel parts: `PART=a:b python examples/<script>.py`.
2. Build the audio: `PART=audio python examples/<script>.py`.
3. Concatenate the parts and mux with `loudnorm=I=-14:TP=-1.5`.
4. Keep the output at 1080x1920, 24 fps, the same `post` settings and the same fonts.
5. Draw UI text (subtitles, HUD, health bars, emotes) as 2D overlays after the 3D render.
6. Review the assembled video:
   - extract the last frame before and the first frame after every cut (`out/qa/cuts_*.png`) and check continuity
   - check the duration
   - for variants, check that the shared shots and audio are identical: frame difference about 0 apart from
     encoding, and audio correlation 1.0
   - check that sound effects line up with their on-screen events

## Final Boss A/B rule
Both versions use the same knight, boss, dungeon, barrier, style, opening shot (0–4 s) and final reveal.
B (`final_boss_b.py`) imports A (`final_boss.py`):
- 0–4 s and the last 3.9 s are A's `frame()` output and A's audio samples.
- Everything in between uses A's models and set, with the B-only corridor dressing and the lever added.

## Added 18 Nov 2026: critique, check and regression tools
- **Phase 3b — critique (after a draft render, before the final):** `python tools/qa/critique.py <draft.mp4> --name <script> --round N`.
  It measures what `scene_qa` cannot (static opening, still stretches, quiet stretches, gaps between voice-level sounds),
  detects the real cuts (a light flicker is not a cut) and writes a sheet (12 even frames + B/A frames around each cut) to
  `out/qa/<script>/critique_rN.png`. Each round is logged in `reviews/<script>.md` (tracked in git) with scores 1-10 for:
  readability, motivation + timing, framing, limbs + contacts, text, cuts, sound vs picture, pacing, and the top 3 fixes.
  Every score must be >= 8 before the final. At most 3 rounds, then Enes decides. Claude cannot listen: sound is scored by
  Enes, Claude only reports the measurements.
- **Phase 5 — check the final file:** `python tools/qa/check.py <final.mp4> --script examples/<script>.py`
  (codec, 1080x1920, 24 fps, frame count, script length, -14 LUFS +/- 1, true peak <= -1 dBTP, no silent half-second,
  `frame(t)` deterministic). Exit code 1 = not deliverable.
- **Phase 1 — after changing a shared model, the engine, `post` or the font:** `python tools/qa/regress.py compare`
  lists the videos whose frames changed (md5 of `frame(t)` at 10/50/90 % of the story). Re-check and re-render those.
  After an intended, reviewed change: `python tools/qa/regress.py snapshot examples/<script>.py` (baseline:
  `tools/qa/baseline.json`). Needs the voice lines in `tts/` (see CONTINUE.md setup), or the script shows as 'skipped'.

## Added 18 Nov 2026: camera and readability rules (ideas from an outside Remotion/three.js short pipeline; our engine is different)
Observations to apply in storyboards and to look for in critique rounds, not hard rules.
- **Camera:** hard cuts on big position jumps; everything else is a smooth glide (about 0.75-1.7 s). Every hold creeps
  (slow push-in), so no stretch of 12+ frames is fully static (`critique.py` already reports still stretches). Impact shakes
  flip sign each frame and decay within about 7 frames. Tilts of 4-5 degrees add drama; no random hand-held float.
- **Timing:** reactions start 0-3 frames before the word they illustrate. Lock the picture timing before the sound is made;
  a later timing change means re-running the audio.
- **Readability traps (check on every contact sheet):**
  - a prop closer than about 2 m to the lens becomes a huge cut-off blob at the frame edge: keep it recognisable or remove it
  - a foreground object cut by the frame edge reads as a meaningless shape
  - a hanging or swinging object drawn with a single line can read as a hanging: show the full structure
  - a sign lit from the side goes grey and unreadable: give text faces an unlit material
  - a rail or bar at chest height crossing a character reads as bars through the torso: move the lens or the rail
- **Final-file check idea (not implemented yet):** per-frame scan for black, white, frozen and sudden-pop frames, ignoring
  planned flashes and crossfades (the outside repo does this in `short_qa.py`); would extend `tools/qa/check.py`.
