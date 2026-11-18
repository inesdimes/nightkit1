# MISS — PS1-style corridor short (archer vs. polite goblin)

Standalone, headless, deterministic. Dependencies: numpy, Pillow, ffmpeg (subprocess). No GPU, no ML, no network.

    python render.py --cut master      -> out/MISS_15s_master.mp4   (360 frames, 15 s)
    python render.py --cut extended    -> out/MISS_30s_extended.mp4 (720 frames, 30 s)
    python render.py --debug qa        -> run all asserts only
    python render.py --debug poses     -> out/contact_poses.png
    python render.py --debug world     -> out/debug/ (5 cameras, turntable, camera asserts)

Also written: `out/contact_<cut>.png`, `out/stills/`, `out/qa_report.txt` (the asserts of section 11; a FAIL blocks encoding, `--force` overrides).

Files: `raster.py` (z-buffer rasterizer + PS1 post chain), `font.py` (own bitmap font), `world.py` (corridor, board, torch, 5 cameras),
`characters.py` (`make_archer`, `make_goblin`, `make_arrow`, `make_arrow_crate`: reusable), `timeline.py` (all frame tables, pure functions of cut + frame),
`scene.py` (frame composition, popups, subtitles), `audio.py` (synthesis + -16 LUFS via ffmpeg ebur128), `qa.py` (asserts), `render.py` (CLI).
Same inputs always give the same mp4 (checked by MD5).
