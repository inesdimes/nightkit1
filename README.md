# nightkit

Procedural PS1-style analog horror shorts for **THE THINGS WE SEE AT NIGHT**.
Everything (geometry, camera, light, figure, sound) is generated from code: no AI images, no stock audio.

## Requirements
- Python 3.10+, `pip install numpy pillow matplotlib`
- `ffmpeg` / `ffprobe` on the PATH

## Quick start
```bash
python examples/elevator.py      # renders out/the_elevator.mp4 and prints the checks
```

## Modules
| Module | What it gives you |
| --- | --- |
| `engine` | `Renderer` (low-poly software renderer, layers, point lights, flashlight cone, fog), `Camera.look`, `box`, `quad`, `tiled_plane`, `wall_region`, rotations |
| `scenes` | Parametric locations: `elevator_hall`, `elevator_cabin`, `sliding_doors`, `corridor`, `stairwell`, `parking_garage`, `bus_stop`, `lamp_panel` |
| `figures` | `the_figure` (series silhouette: tall, thin, hunched, head bowed, `k` = how solid it reads), `walker_profile` |
| `motion` | `smooth`/easing, `Track` keyframes, `slow_approach`, `approach_and_return`, `handheld` (loop-periodic sway), `sudden_turn`, `walk_bob` |
| `scares` | `Outages`, `plan_outages`, `creeping_positions`, `CreepWhenDark` (it only moves in the dark), `reflection`, `shake` |
| `audio` | `Sound` (loop-safe: circular filters/reverb, wrapping events): hum, air, drone, fluorescent, crackle, door slide, motor, creak, tick, ding, knock, breath, reversed `music_box`, `poisson` events, `silence`, `reverb`, `save(rotate_seconds=)` |
| `post` | `ps1` colour reduction + dither, `upscale`, `VHS` (grade, chroma, scanlines, grain, tracking band per loop), `map_texture` (full-res text on screens), `Encoder` |
| `font` | 5x7 pixel font; `check()` raises if a glyph is missing |
| `check` | `probe`, `near_duplicates`, `loop_seam`, `audio_seam`, `spectrogram`, `contact_sheet` |

## Status
- Production-tested: `elevator_hall`, `elevator_cabin`, `sliding_doors`, `corridor`, `the_figure`, all of `motion`, `scares`, `audio`, `post`, `check` (Episode 01 is rebuilt with them in `examples/elevator.py`).
- First drafts (render correctly, will be refined in their own episode): `stairwell`, `parking_garage`, `bus_stop`, `walker_profile`.

## Layers (important)
`Renderer.render(cam, [pre, main], ...)` draws each layer depth-sorted, in order. Anything that is always behind an
opening (an elevator cabin, a room behind a doorway) goes in `pre`; the walls with the opening go in `main`.
Build walls around openings with `wall_region` so they stop exactly at the frame.

## Series rules
1. It only moves when the lights go out (`CreepWhenDark`).
2. The figure is never fully revealed: no face, no detail, low contrast at first (`k` 0.25 -> 0.9).
3. A clock or display reading **03:07** appears somewhere in every episode.
4. 20 s, 9:16, 24 fps, seamless loop; the final event leads into the opening.

## Loop checklist
- Camera rests (zero velocity) at the loop point; `handheld(t, loop)` only.
- No outage or event crosses the loop boundary unless it is meant to wrap.
- `Sound(loop=True)` + `cyc()` frequencies; `VHS(band_period=loop)`.
- Start the file at the strongest frame with `START_FRAME` and `save(rotate_seconds=START_FRAME/FPS)`.
- Run `check.loop_seam` (seam <= ~1.2x median) and `check.audio_seam` (seam_hf <= median_hf).

## Episode recipe
1. Pick a scene builder and a camera path (`approach_and_return` for loops).
2. Plan outages (`plan_outages`) and figure positions (`creeping_positions`).
3. Render frames into `[pre, main]`, add overlays (texts with `font`, `reflection`).
4. Build the sound with `Sound`, matching every visual event.
5. Encode with `post.Encoder`, then run every `check` function and look at a `contact_sheet`.
