# Continuation note — Insert Disc 2 (18 Nov 2026)

Paste this into a new chat. Repo: `inesdimes/nightkit1`, branch `ccr-bf35ef55-cb0f4r` (latest work, includes everything from
`ccr-f9cdf9b1-6cua2c`; not on `main`). A new session may only be allowed to push to its own branch: create it from this one.
Read first: `HANDOFF.md` (channel, rules, video table), `PIPELINE.md` (production + QA process), `ANALYTICS.md` (data, observations).

## Working agreement
- Posted videos are never re-edited or re-uploaded.
- New videos use the latest observations (ANALYTICS.md sections 9–10): big, close, moving character in frame 0; story starts within ~6 s; no silent stretches; a payoff at the end. Observations, not rules.
- One video per day on YouTube; check stats at 48 h.
- Rendered videos are NOT in the repo (`deliverables/`, `*.mp4` ignored); Enes keeps them on his PC.
- Save tokens: batch feedback into one message, approve a short plan before big changes, only re-check changed scenes.

## Setup in a new container (gitignored, so it is gone)
```bash
pip install scipy soundfile kokoro-onnx
mkdir -p tts/v3 && cp tools/tts/scripts/v3.json tts/v3/script.json   # face_track.py (the woman) reads it at import
mkdir -p tts && cd tts && for f in kokoro-v1.0.int8.onnx voices-v1.0.bin; do curl -sSL -o $f https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f; done; cd ..
python tools/tts/<fb|lr|gf|sz|ap|ap15|cd|cp|um|cb|gb|mc|mc2|lh>.py      # regenerate the voice lines a script needs
```
(For Final Boss B also run A's `PART=audio` first; same for Guard Forgets B.)

## Videos
| Video | Script | Status |
|---|---|---|
| Final Boss A (30.5 s) | examples/final_boss.py | rendered, not posted |
| Final Boss B (60.25 s) | examples/final_boss_b.py | **posted 16 Nov 21:21** (got ~0 views; 2nd post that evening) |
| Guard Forgets A (30.6 s) | examples/guard_forgets.py | **posted 16 Nov 20:30**: ~300 views, 15 % stayed (early reading) |
| Guard Forgets B (59.6 s) | examples/guard_forgets_b.py | rendered, not posted; open question: post as-is (clean A/B) or remake the first 3 s |
| Loot Restocker A (29.9 s) | examples/loot_restocker.py | rendered, not posted; the 60 s B was never made |
| Safe Zone v2 (52.3 s) | examples/safe_zone.py | rendered, not posted |
| One Apple v4 (30.6 s) | examples/one_apple.py | rendered, not posted; for **YouTube + Instagram** |
| Cat Dodge Boss (15 s) | examples/cat_dodge.py (voice `tools/tts/cd.py`; woman = `face_track.girl()`, new cat model) | **dropped by Enes (17 Nov)**, do not post |
| Cat POV (15 s, TikTok) | examples/cat_pov.py (voice `tools/tts/cp.py`; imports cat/room/pizza from cat_dodge.py) | rendered, not posted |
| The Smallest Umbrella (15 s, wholesome) | examples/umbrella.py (voice `tools/tts/um.py`; own duckling, dog, umbrella, rainy street) | rendered, not posted |
| The Camera Under My Bed (30 s, PS1 horror) | examples/camera_bed.py (voices `tools/tts/cb.py`; own man model, bedroom, CRT feed compositing) | **dropped by Enes (18 Nov): too many errors**, do not post |
| Why Do Ghosts Say Boo? (60 s, PS1 horror-comedy) | examples/ghost_boo.py (voices `tools/tts/gb.py`; own ghost, janitor, lantern, corridor) | v4 rendered: 44.2 s cut, 2x subtitles, camera C colour fixed -> `deliverables/why_do_ghosts_say_boo.mp4` (60 s v2 also kept); not posted; QA + critique round 2 clean |
| Why Do Mirrors Copy Us? (60.0 s, PS1 surreal comedy) | examples/mirror_copy.py (voices `tools/tts/mc.py`; own robot, mirror room, 2D reflection sprite) | rendered 18 Nov: critique rounds 1-2 all >= 8, `check.py` 9/9 -> `deliverables/why_do_mirrors_copy_us_60s.mp4`; not posted |
| Why Do Mirrors Copy Us? **v2** (34 s, closer camera, SYNC HUD) | examples/mirror_copy_v2.py (imports mirror_copy.py; voice `tools/tts/mc2.py`) | rendered 18 Nov: critique round 1 all >= 8, `check.py` 9/9 -> `deliverables/why_do_mirrors_copy_us_v2_34s.mp4`; not posted; the 60 s cut had a glint bug (stripe crossed the robot), fixed in `mirror_copy.glint()` (60 s file not re-rendered) |
| Why Do Lighthouses Blink? (60.0 s, PS1 maritime horror) | examples/lighthouse.py (voices `tools/tts/lh.py 1.0`; captain follows the wrong light, is lost, a megalodon (side profile, boat lying in its open jaws) swallows the boat; subtitles 1.25x at 1080x1920) | FINAL 18 Nov, `check.py` 9/9 -> `deliverables/why_do_lighthouses_blink_60s.mp4` (older cuts kept in deliverables: `_v1_calm_ending`, `_v2_escape_then_shark`, `_v3_front_shark`); not posted |
| One Apple 15 s cut (15.25 s) | examples/one_apple_15.py (imports v4 assets; voice `tools/tts/ap15.py`) | rendered, not posted; for **TikTok** |

Captions ready: `captions/final_boss.md`, `captions/guard_forgets.md`, `captions/one_apple.md` (`captions/cat_dodge.md` exists but that video was dropped), `captions/cat_pov.md`, `captions/safe_zone.md`, `captions/smallest_umbrella.md`, `captions/camera_under_bed.md`.

## Newest work (18 Nov 2026)
- The Smallest Umbrella (15 s, revised cut): rendered, not posted (`examples/umbrella.py`).
- Cat POV (15 s, TikTok): rendered, not posted (`examples/cat_pov.py`). Cat Dodge Boss and The Camera Under My Bed were dropped by Enes.
- MISS (archer + goblin, `miss/`): standalone project (numpy + Pillow + ffmpeg only), both cuts render with `python render.py --cut master|extended`; steps 1-6 done, README.md and NOTES.md (DEVIATIONS) are written (step 7 done). Narration is skipped (no offline TTS on that machine).
- Start of a new chat: read ONLY this file and `PIPELINE.md` (the skill `.claude/skills/nightkit-short` has the production order). Use `WORKFLOW.md` for the GPT + Claude split, `CHANNEL_PROMPT.md` is the briefing prompt for GPT.
- NEW: `WORKFLOW.md` (GPT + Claude division of work) and `CHANNEL_PROMPT.md` (briefing prompt for GPT).

## Newest work (18 Nov 2026, evening) - Insert Disc 2 sessions
- New videos made this session (all in `examples/`, rendered, not posted): `mirror_copy.py` (60 s) and `mirror_copy_v2.py` (34 s, the better cut; imports the 60 s file), `lighthouse.py` (60 s, final story above). Captions are not written yet for these three.
- Lessons from Enes's feedback (apply to new briefs): big, close character in frame 0; hook with a HUD / danger readout; do not follow a brief literally if it hurts retention (ANALYTICS 9-11: 61 s stories keep 56-58 % on YouTube, the first 10 s decide); subtitles 1.25x drawn at 1080x1920 (`sub_overlay()` in lighthouse.py), not 2x; narration must not be cut mid-sentence.
- Weak spots known in `lighthouse.py`: the megalodon is a blocky low-poly model; the empty-sea hold at 54-57 s is flagged as a still stretch (intentional); Claude cannot listen, so sound was only measured.
- `mirror_copy.glint()` fixed a bug in the 60 s mirror video (stripe crossed the robot); that video was not re-rendered.

## QA tools (added 18 Nov 2026)
- `tools/qa/critique.py` (scored review rounds, log in `reviews/<script>.md`), `tools/qa/check.py` (final-file check),
  `tools/qa/regress.py` (which videos changed after a shared change; baseline `tools/qa/baseline.json`, 13 scripts).
  Process summary: `.claude/skills/nightkit-short/SKILL.md`; details in PIPELINE.md (last section).
- Ghost Boo v4 (2x subtitles, camera C colour fix) cleared critique round 2; log in `reviews/ghost_boo.md`.

## Next steps
1. 48 h stats of the 16 Nov posts (YT stayed/swiped, retention graph) -> add to ANALYTICS.md.
2. Caption for Loot Restocker (Safe Zone, One Apple and Cat POV captions are done, all three platforms).
3. Decide Guard Forgets B (see table).
4. New briefs as Enes sends them (follow PIPELINE.md; QA with `python tools/qa/scene_qa.py examples/<script>.py`).
