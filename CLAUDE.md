# Insert Disc 2 / nightkit - start here

Enes writes in Turkish; answer in Turkish.

## Start of every session
1. Read `CONTINUE.md` (video table, open work, next steps) and `PIPELINE.md` (production + QA). Nothing else unless needed.
2. For a new short or a revision, follow the skill `.claude/skills/nightkit-short` (stop at every STOP gate).

## This PC (local, not a cloud container)
- Windows 10, NVIDIA RTX 4060 8 GB. Shell: PowerShell (Bash also available).
- Blender 5.3: `C:\Program Files\Blender Foundation\Blender 5.3\blender.exe`
  run scripts with `blender -b --factory-startup --python <script>`; settings via env vars (`$env:MODE=...`).
- No ffmpeg on PATH: mux video + audio with Blender's sequencer (see `mux()` in `blender/misty_pilot.py`).
- System Python has numpy + Pillow (contact sheets, checks).
- Renders and MP4s live outside the repo in `C:\Users\USER\Documents\blender-shorts\renders\<project>\` (never commit them).

## Blender work
- Scripts in `blender/`. Always: low-res preview first (50 %, few samples), show Enes, final only after his OK.
- EEVEE (4.2+): do not use a world volume - it blocks sun and sky light. Use a large volume box for haze.
- Do not pipe Blender output through `Select-Object -First N`; it kills the render.
- Claude cannot listen: report sound by measurement (RMS / peak), Enes judges it.

## End of every session
Update `CONTINUE.md` (video table + newest work) and `ANALYTICS.md` (new numbers, same day), commit, and **push** (changed 20 Nov 2026, Enes's decision: the PC stays the home of the repo, but GitHub is the shared copy so cloud sessions see the same analytics and state). Start of every PC session: `git pull`. Videos are never committed.
