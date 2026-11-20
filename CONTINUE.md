# Continuation note — Insert Disc 2 (18 Nov 2026)

Paste this into a new chat. Repo: `inesdimes/nightkit1`. Shared branch since 20 Nov 2026: `misty-pilot` on the PC; the cloud branch `ccr-91720a78-gihjic` contains all of it (merged 20 Nov) plus the newest analytics. PC: `git pull` at the start, push at the end (see CLAUDE.md). A new session may only be allowed to push to its own branch: create it from this one.
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
| Misty Valley pilot (7.0 s, Blender 5.3 EEVEE, no narration, SFX only) | blender/misty_pilot.py (MODE=preview/final/audio/mux; frames + MP4 in `~/Documents/blender-shorts/renders/misty_pilot/`) | FINAL 18 Nov: 1080x1920, 96 samples, motion blur -> `misty_pilot_final.mp4`; not posted. Note: EEVEE world volume blocks sun/sky since 4.2, so haze is a volume box |
| One Small Mistake #01: The Save That Killed Him (41.6 s, PS1 dark comedy) | examples/save_killed.py (voice `tools/tts/sk.py`, Kokoro bm_george speed 1.25; reuses FB knight + L10 hall; new purple crystal, potion, HUD/pause menu) | FINAL 18 Nov (approved by Enes): critique r1-r2 all >= 8, `check.py` 12/13 (WARN = planned flash pops) -> `renders/save_killed/the_save_that_killed_him_41s.mp4`; not posted. 41.6 s not 30 s: the brief's 115 words do not fit Kokoro's pace |
| The Save That Killed Him, TikTok cut (20.5 s) | examples/save_killed_15.py (imports save_killed.py, only voice `sk.py --cut 15` + beat times change) | FINAL 18 Nov (approved by Enes, 20.5 s kept): critique r1 all >= 8, `check.py` 12/13 -> `renders/save_killed/the_save_that_killed_him_tiktok_20s.mp4`; not posted. Captions: `captions/save_that_killed_him.md` |
| One Apple 15 s cut (15.25 s) | examples/one_apple_15.py (imports v4 assets; voice `tools/tts/ap15.py`) | rendered, not posted; for **TikTok** |
| Why do final bosses have three phases? (30.4 s, PS1 comedy) | examples/four_phases.py (voice `tools/tts/fp.py` + `fp_vc.py`, Enes timbre via ChatterboxVC; cloak boss over 3 goblins, reuses knight/arena/goblin) | FINAL 20 Nov (no-stop run): scene_qa clean, critique r1-r3, `check.py` 12/13 (WARN = planned hit flashes) -> `renders/four_phases/why_do_final_bosses_have_three_phases_30s.mp4`; not posted; TikTok 15 s cut not made |
| What happens to the guy whose car you steal? (31.6 s, PS1 comedy) | examples/stolen_car.py (voice `tools/tts/sc.py` + `sc_vc.py` + `sc_check.py`; Gary + driver box humans, car, police car, street/house/sunset) | FINAL 20 Nov (no-stop run): scene_qa clean (one known stand-in false positive), critique r1-r3, `check.py` 12/13 (WARN = police-light flashes) -> `renders/stolen_car/what_happens_to_the_guy_whose_car_you_steal_32s.mp4`; not posted; captions in `captions/stolen_car.md` |

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

## Tools added after reviewing an outside pipeline (18 Nov)
- `tools/qa/script_lint.py`, frame scan in `tools/qa/check.py`, `nightkit.motion` glide/creep/dolly/kick, `nightkit.audio.duck_envelope`; details in the last section of PIPELINE.md. Story shape is in CHANNEL_PROMPT.md.

## In progress: The Lightning Missed (series: What Happens Next?)
- Enes approved a NEW series inside Insert Disc 2 (real science fact + retro-game logic joke; do not repeat old formats). Voice locked (80 words, ~32.8 s), decisions in `briefs/lightning_missed.md`. Next: asset lock (courtyard, shield, poses) -> `examples/lightning_missed.py`.

## In progress: THE LAST 10 SECONDS (series), ep. 1 "The Dungeon Collapse"
- Enes chose the idea (collapsing dungeon, HUD timer 10.0 -> 0.0, loss aversion, ends with one apple). Script `examples/last10_collapse.py` (58 s), voice `tools/tts/l10.py`. Draft 2 rendered, critique round 2 in `reviews/last10_collapse.md`; not posted. Open: pacing of the 19-30 s thought beat.

## Local PC notes (18 Nov 2026, Enes's Windows PC)
- Setup done here: `pip install scipy soundfile kokoro-onnx onnx`, Kokoro files in `tts/`, ffmpeg via `winget install Gyan.FFmpeg`
  (new shells: `$env:Path += ";$env:LOCALAPPDATA\Microsoft\WinGet\Links"` until restart). Renders go to `..\renders\<project>\`.
- kokoro-onnx 0.4.7 has no `create_timed`: `tools/tts/emph.py` now has a fallback that reads the duration output of `kokoro-dur.onnx`.
- `tools/qa/scene_qa.py`: new optional `allow_teleport=[(who,t)]` for planned in-shot resets (respawn under a white flash).
- PowerShell 5.1: `Start-Process -Environment` does not exist; set `$env:PART` before each `Start-Process` for parallel parts.

## Next video (20 Nov 2026): "Why do final bosses have three phases?" - FINAL APPROVED by Enes (video + voice), captions in `captions/four_phases.md`; 5 small fixes listed in `reviews/four_phases_review.md` (optional, not required for posting)
- Brief: `briefs/four_phases.md` (3 goblins in a cloak; the knight joins them -> 4 phases; the old goblin gets a day off). To be built on the PC (nightkit). Voice: Chatterbox cloned Enes but with an Indian-English-sounding accent (Enes does not want it); next = test ChatterboxVC (English source -> Enes timbre) on line 1, see the brief's Voice section for the order.

## Next video (20 Nov 2026): "What happens to the guy whose car you steal?" (trend: new open-world crime game)
- Brief `briefs/stolen_car.md`, captions `captions/stolen_car.md` (game name only as one hashtag in the description: Enes's decision). PC task in `GO.md`.

## Next steps
Cancelled by Enes (20 Nov 2026): the old list (48 h stats, Loot Restocker caption, Guard Forgets B decision) is dropped.
New briefs as Enes sends them (follow PIPELINE.md; QA with `python tools/qa/scene_qa.py examples/<script>.py`).

## 19 Nov 2026 - Antosiyanin loop short (Sapkali Molekul)
- `examples/anthocyanin_loop.py` (pure Pillow/numpy 2D pixel art, no Blender; Kokoro TTS with lang=tr, SFX synthesized, ffmpeg now on PATH).
  `audio` -> `preview` -> `video` -> `qa`. Output: `renders/anthocyanin/anthocyanin_loop_v1.mp4` (1080x1920, 70 s, 17 MB, -14.2 LUFS).
- QA: frame 0 == frame 2099 pixel-exact (also after H.264: QP 18, forced I-frames at 0 and 2099); palette = 6 colours only; last VO ends 67.9 s.
- Not verified by ear: Turkish pronunciation (English Kokoro voices + espeak-tr) - Enes must listen; swap to ElevenLabs if bad.

## 20 Nov 2026 - Enes's own English voice (Chatterbox)
- Chatterbox TTS server is installed at `D:\chatter\Chatterbox-TTS-Server-2.0.0` (web UI `http://localhost:8004`, `start.bat`). Reference recordings are in its `reference_audio\` (`enes_main/curious/deadpan/excited.wav`) and `voice/enes_ref_main.wav` (gitignored).
- Enes tested 3 ways (VC from Kokoro, TTS with his reference at cfg 0.0/0.2, TTS with a Kokoro reference) and chose **2b**: original Chatterbox, reference `enes_ref_main.wav`, exaggeration 0.5, cfg_weight 0.2, seed 3000 ("harika"). The Turkish accent came through the reference at the default cfg 0.5.
- Tool: `tools/tts/enes.py lines.json <name>` -> `$TTS_DIR/<name>/<key>.wav` + `script.json` (same shape as the Kokoro scripts). Run it with the Chatterbox embedded Python (system Python has no torch/chatterbox); stop the web server first (VRAM). Output matches the approved 2b file exactly.
- Gotchas: Turbo ignores cfg_weight/exaggeration (use the original model); `cfg_weight=0.0` crashes in this chatterbox version (tool uses 1e-6); original model files are in the HF cache (downloaded 20 Nov). Not wired into a video yet; the three tone references (curious/deadpan/excited) are short (5-8 s) and untested.

## 20 Nov 2026 - stolen_car (second GO.md task, no-stop run)
- Built per `briefs/stolen_car.md`: `examples/stolen_car.py` (Gary's car stolen 900 times; lock, alarm, second car, keys + sandwich + note; car returns dented at sunset; Gary at the window; driver with 5 wanted stars, THANKS GARY note, police, he sprints off). No game name/logo/character/map/music in the video. Render: `python tools/render_parts.py examples/stolen_car.py --prefix sc --audio stolen_car.wav --out ../renders/stolen_car/x.mp4` (~50 s).
- Voice: option 1 as in four_phases (Kokoro bm_george -> ChatterboxVC -> Enes timbre), all 11 lines pass `sc_check.py` (pitch +4..+13 % of the reference, no clipping). BUG FOUND + fixed in `sc.py build vc`: sentences pulled by rubberband came back at 48 kHz while the others stayed 24 kHz, so mixed rates were concatenated (line 3 got a 2.5 s hole). `sc.py` now resamples every sentence to one rate. `fp.py` has the same latent code but its checked output was fine; not touched. Enes still has to listen.
- Weak spots left (2 scores at 7): Gary is small in the driveway shot (lines 3-4); keys / sandwich / note contact is only suggested by the arm over the cabin; police cars are plain dark boxes; sound judged by measurement only (-14.3 LUFS, -1.5 dBTP, no gap > 0.6 s). script_lint hints (pace 2.97 w/s, no pivot / question beat) ignored on purpose: the brief fixes the narration.
- scene_qa: the driver stand-in jumps at 29.08 s (QA only, he is not drawn before he steps out). Untracked scratch files `test1.png` etc. stay uncommitted.

## 20 Nov 2026 - four_phases (GO.md task, no-stop run)
- Built per `briefs/four_phases.md`: `examples/four_phases.py` (cloak boss 3.6 -> 2.4 -> 1.2 m, three hits, cloak slips, goblin reveal, knight + goblins under the cloak, 4 phases, old goblin day off). Render driver: `tools/render_parts.py` (parallel parts + concat + loudnorm mux, ~1 min).
- **Voice option used: 1 (ChatterboxVC).** Kokoro bm_george speaks each sentence (`tools/tts/fp.py src`), `tools/tts/fp_vc.py` converts to `voice/enes_ref_main.wav` (Chatterbox embedded python), `fp.py build vc` assembles. VC pitch follows the source loosely, so each sentence is pulled to ~+5 % of the reference pitch (clamped +-2.5 st) with rubberband. Automatic checks (`tools/tts/fp_check.py`): no clipping (peak 0.95), longest pause 0.22 s, pitch +5..+9 % of the reference (116 Hz), every line fits its window. Fallbacks 2/3 were not needed. **Enes must listen** (accent, artefacts from VC + pitch shift); the Kokoro-only version is `fp.py build src`.
- Brief inconsistency (kept the brief's picture): the new boss counts 4 phases, but the old goblin sits outside, so only knight + middle + kid are under the cloak (3 members). Cloak height / HUD show 4.8 m / "PHASES: 4" as written.
- Weak spots: sword contact on the cloak reads weakly from the side camera (limbs+contacts 7/10); goblins step into the cloak skirt (a hop hides most of it); the old goblin's cup is a plain white box; sound judged by measurement only (-14.1 LUFS, peak -1.4 dBFS, no gap > 0.6 s between voice-level sounds). Script lint hints (no "Wait...?" beat, no explicit "because") ignored: the narration is fixed by the brief.
- Setup note: `tools/tts/lr.py` must have been run once (loot_restocker.py reads `tts/lr/script.json` at import).
