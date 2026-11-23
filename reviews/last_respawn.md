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
