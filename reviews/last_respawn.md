# THE LAST RESPAWN - phases 1-3 (23 Nov 2026, PC) - STOP gate for Enes

Script: `blender/last_respawn.py` (one file: shared timing, numpy sound, Blender scene). Placeholder voices: `tools/tts/lrs.py` (Kokoro;
Goblin am_puck +3 st, Bell Knight bm_george -1 st + metallic comb, Bellwright bm_lewis -3 st + stone reverb). They are NOT Enes's performance.

## What to look at (outside the repo, `renders/last_respawn/`)
| File | What |
|---|---|
| `frame0_1080x1920.png` | phase 1: frame 0 at full resolution |
| `last_respawn_hook_0001-0192.mp4` | phase 2: 00:00-00:08, 540x960 preview, 16 samples, placeholder voices |
| `last_respawn_loop_0001-0216.mp4` | phase 3: 00:52-00:58 + 00:00-00:03 joined (9 s) |
| `sheet_mid.png` | the middle beats B1-B6 (10, 18, 25, 32, 41, 48 s): coarse staging only, NOT part of the gate |

## What is built
- Sets: one modular alley (stone facades, lit/dark windows, balconies, signs, pipes, sagging cables, 20 flickering lanterns, cold blue
  mist box, skyline silhouettes), a bridge with the archer, the bell tower at the alley end (the bell hangs still, the tower gears
  stutter = the system is failing, counterweight), a coarse round bell chamber (big bell, gears, central gear with the emblem,
  mechanism panel + ring of 12 sparks with one empty slot, crank, chain).
- Puppets (rigid parts on empties, posed every frame by a `frame_change_pre` handler; no keyframes, no skinning): Bell Knight (tarnished
  bronze, torn grey cape, asymmetric pauldrons, hinged breastplate with a black hollow and one cyan spark, cyan emblem + visor glow),
  Goblin 47 (big ears, apron, red scarf, eyes / pupils / brows / mouth = 7 face states), the Bellwright (bell cap, brass mask, lantern),
  5 hollow shells (shared meshes, dull, black visor).
- Opening 0-8 s: run, the arrow hits at 0.25 s, collapse, cyan dissolve, cyan column drops him into the knight's arms (1.5 s), "Not again!",
  he hops down and grabs the knight's arm, HUD `RESPAWNS LEFT 1 -> 0` with a pop + shake at 3.4 s, the camera cranes up and over their
  heads to behind them: the still bell in the tower, "The bell stopped!" while he points.
- Ending 52-58 s: restored in the same alley (cyan flash, `RESPAWNS RESTORED`), alone; he reaches for the empty space where the knight
  ran (wordless beat), hears the bow creak, turns to the archer, terror, turns back, runs, "No... NOT AGAIN!", the arrow enters the frame.
- Subtitles: exact words, lower region, one highlighted word (cyan / amber); HUD in a separate mono font.

## Measured (Claude cannot watch or listen - these are numbers, Enes judges)
- Loop picture: mean frame difference 1392 -> 1 = 11.9 vs 4-7 for neighbouring frames. Goblin position + pose, camera and arrow continue
  exactly (same functions of loop time); **the extra difference is the Bell Knight popping in at frame 1** (he exists in the opening,
  not in the ending - the story demands it). Options for Enes: accept it (the pop itself says "the cycle restarted"), or let the
  ending show a faint cyan outline of him forming beside the goblin in the last 0.3 s.
- Loop sound: the arrow whistle is ONE signal split across the boundary (57.25-58.0 + 0.0-0.25); the ambience is bent onto the first
  sample over the last 20 ms: boundary sample jump 0.0000 (was 0.053). Full mix -23.7 dBFS RMS, -1.5 dBFS peak (preview level, not
  loudness-normalised).
- Render speed (RTX 4060): preview 540x960 / 16 samples = 0.24 s per frame (336 frames in 81 s, two processes). Full 1080x1920 /
  64 samples ~2 s per frame -> the whole 58 s film ~45-60 min.

## Known problems (seen in the stills)
- The look is a blocky toy-puppet look, not yet the "haunted clockwork diorama" the brief asks for. Box limbs look stiff in the run.
- The Bell Knight's helmet blows out pale on its lit side; the cyan emblem renders near-white (AgX desaturates bright emission).
- The arrow is readable at full resolution in frame 0 but small at preview size; it is scaled 2x already (stylised).
- The sheath reads as a black plank; the goblin's apron is a flat board.
- During the crane over their heads (4-5.5 s) the knight is cut by the frame edge for ~1 s.
- The middle (8-52 s) is only staging: B4 does not show the kneeling shells in frame, B6 is washed out by the soul light; no crumbling
  armour yet, no reflections in the visor.

## Honest estimate for the full film in Blender
Phases 1-3 took one PC session. Remaining: look development (materials, lighting, puppet shapes: the biggest unknown, needs Enes's eye),
animating B1-B6 properly (kneel in unison, breastplate, mechanism, chain pull, bell swing, soul stream, armour crumble), the voice pass
with Enes's 13 takes (the timing is driven by the line start table `LINES`), final render (~1 h) and QA. Realistic: 2-3 more PC
sessions with a review from Enes between them. Moving it to nightkit (2D/numpy) would be faster to animate but would lose the 3D
camera moves (crane, orbit) and the depth of the alley.

## 23 Nov 2026 (later) - Enes: "blender devam. kalsın" -> phase 4 part 1 (no voice takes yet)
- **Full 58 s preview:** `renders/last_respawn/last_respawn_full_0001-1392.mp4` (540x960, 16 samples, placeholder voices; 1392 frames in ~3 min).
- The middle (8-52 s) is now animated, not boards: B1 the shells pour out of the side arch and march in step, the two run back
  towards the lens (camera runs backwards), the knight passes the lens and his body wipes to the chamber (occlusion cut at 15.0);
  B2 the Bellwright braces a slipping gear, the knight's sword knocks a falling hook off the goblin, "Take mine!" over the
  Bellwright's shoulder; B3 he points, CUT on the knight's turn (23.5), push in on the open breastplate (hollow + spark), the goblin
  recoils, the shells walk in; B4 they kneel in unison, low shot over their shoulders, then the same emblem on the central gear;
  B5 the panel slides, the ring of sparks with one empty slot, hand on the crank, the goblin grabs his wrist (shot from behind the
  crank), he moves the hand aside; B6 he turns to the goblin "Then make this one count.", yanks the chain, the bell swings, the soul
  runs up a cyan line into the bell, the armour falls backwards into parts, push in on the goblin's face from where the knight stood,
  cyan light wash that carries across the cut into the restored alley.
- Two cuts inside the film (15.0 occlusion, 23.5 action cut) + the 52.0 reset.
- Sound: hook clang, the shells' steps in unison, goblin run, armour clatter, chain snap at 47.5, bell at 47.9; the bell and the
  chamber reverb tail stop dead at 52.0 (the reset). Loop boundary sample jump still 0.0000.
- Look changes: bevelled puppet parts, warmer lanterns (no lamp shadows: shadow buffer was full), saturated cyan soul colour,
  camera-side key light in the chamber (faces read in every shot).
- All chamber camera keys / character tracks / pose keys / face keys are pure-python data (`CAM_CH`, `KN_*`, `GB_*`, `BW_*`, `MV_*`)
  so the nightkit version (Enes, 23 Nov: same camera, same everything, only our graphics) can import them.
- Still open: the look is the blocky puppet look (Enes to OK or ask for changes before the final 1080p render); the shells look
  like copies of the knight in warm light; no visor reflections; the ending framing keeps the goblin small (empty space where
  the knight ran - intended); Enes's 13 voice takes; final 1080x1920 render (~1 h); then the nightkit version.

## 23 Nov 2026 (later) - Enes: "visual bugs, story good, far too many silent parts" -> v2 pass
- **Silence:** before, 13 lines = 16 s of voice in 58 s, gaps up to 11 s. Now 23 lines (30.4 s of placeholder voice; NEW lines
  4, 6, 7, 11, 13, 14, 16, 17, 20, 22 in `briefs/last_respawn_voice_sheet.md`). New lines plant the twist ("Empty armour. They follow
  the bell." / "Then why are they following US?!" is answered by "They remember their commander."), and the ending reach gets a
  whispered "Knight...?". Plus a quiet score bed (string-like pad, chord per beat, heartbeat that speeds up 36-47.5 s, ducked 6 dB
  under every line; a thin high chord alone in the alley 52.4-56.9, gone before the arrow so the loop boundary stays music-free).
  Measured: the longest stretch under -30 dBFS between 8 and 52 s is now 1.5 s (was 6 s); full mix -22.6 dBFS RMS, -1.5 peak;
  loop boundary sample jump 0.0000.
- **Visual bugs found on a 0.5 s contact sheet and fixed:** goblin held further out of the knight's chest; HUD moved to the top
  (was over the heads); camera shifted right behind them at 5-8 s (knight was cut by the edge), darker cape; the B1 -> chamber wipe
  cut moved to 14.62 s (the camera used to fly through the knight's body, flashing interiors 14.67-14.96 s); the Bellwright side-on
  beside the gear while he speaks (was hidden behind it); "Take mine!" / "You gave yours" / "Gave what?" as medium shots + reverse
  shots (was a 4 s static wide with a tiny knight); the 27.5 s empty frame (wall only) gone; shells walk in as a file through the
  gap (they used to walk through the wall) and kneel in a V, shot from above the knight's shoulder (was a jumble); the commander is
  visible between the kneeling shells; the emblem sits above a bigger panel (it was hidden, and the spark ring peeked out before the
  reveal); the Bellwright in frame for "Restart it"; no camera through the knight at 36 and 40.5 s or the core gear at 41-44 s;
  the goblin's head is no longer a blurry blob at 44-47.5 s; a wide shot for the bell + soul (was looking into the bell); the
  white wash at 51-52 s is 0.5 s shorter. 11 cuts in the middle now (all listed as 'CUT' in `CAM_CH`).
- Still open: the blocky puppet look; the goblin still overlaps the knight's arm a little while held (1.5-3 s); the 15-16 s shot
  is the knight's back (tan box) running away; Enes's 23 takes; final render.

## 23 Nov 2026 (evening) - Enes: "GO.md, finalize, don't wait for me" -> finals (placeholder voices)
Enes's 23 takes are not in `vocal/last_respawn/` yet, so both finals carry the Kokoro placeholders (NOT his performance); when the
takes arrive: replace `tts/lrs/*.wav`, re-time `SCRIPT`, `python blender/last_respawn.py audio`, re-render (both versions read the same tracks).
- **Mastered sound** `renders/last_respawn/audio/final.wav`: BS.1770 loudness in numpy + 4x-oversampled look-ahead limiter
  (`master()` in the script, gain curves on a circularly padded signal): -14.2 LUFS (ffmpeg ebur128 agrees), -1.6 dBTP,
  loop boundary jump 0.0000.
- **Blender final** `renders/last_respawn/last_respawn_final_1080x1920.mp4`: 1080x1920, EEVEE 64 samples, two processes (~3 s/frame), ~50 min; muxed with ffmpeg (now on PATH via winget). `tools/qa/check.py`: 10/11 PASS (1392 frames, -14.2 LUFS, -1.6 dBTP, no silence / black / frozen), WARN frame pops = the planned cuts + respawn flash. Loop picture diff 1392 -> 1 = 12.0 (the accepted knight pop).
- **nightkit version** `renders/last_respawn/last_respawn_nightkit_1080x1920.mp4` (`examples/last_respawn_nk.py`): Blender exports
  per frame the camera, every part's world matrix and the lights (`MODE=export`); nightkit draws it with zraster (flat shading,
  two-tone faces instead of noise textures, depth outline, PS1 dither, 270x480 x4), block-font speaker-coloured subtitles and
  HUD. Same camera, staging and timing frame for frame; same mastered audio. ~0.35 s/frame, the whole film in ~2 min (6 parts).
  `tools/qa/check.py`: 10/11 PASS, WARN frame pops = the planned cuts, the respawn flash and subtitle on/off.
  zraster got an optional per-face `nobias` (no emissive depth bias for real geometry); existing scripts are unaffected.
