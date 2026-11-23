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
| What happens to the guy whose car you steal? (31.6 s, PS1 comedy) | examples/stolen_car.py (voice `tools/tts/sc.py` + `sc_vc.py` + `sc_check.py`; Gary + driver box humans, car, police car, street/house/sunset) | FINAL 20 Nov (no-stop run): scene_qa clean (one known stand-in false positive), critique r1-r3, `check.py` 12/13 (WARN = police-light flashes) -> `renders/stolen_car/what_happens_to_the_guy_whose_car_you_steal_33s.mp4` (v2 with a 1.0 s cold open of the THANKS GARY scene, Enes's request; v1 without it kept as `v1_no_coldopen_32s.mp4`); not posted; captions in `captions/stolen_car.md` |
| Why do final bosses give a speech before the fight? (40.5 s, 14-day test day 1, **22:00 slot**) | examples/skip_speech.py (voice `tools/tts/ss.py` + `tools/tts/vc.py ss`; locked boss/knight/arena; new scroll, boss cape, candles, happy eyes, skip-prompt HUD) | FINAL 21 Nov (no-stop run): scene_qa clean (planned sword contact), critique r1-r2 all >= 8, `check.py` 12/13 (WARN = planned flashes / subtitle changes) -> `renders/skip_speech/why_do_final_bosses_give_a_speech_40s.mp4`; not posted; captions `captions/skip_speech.md` |
| Why don't enemies ever attack all at once? (32.8 s, **new story 21 Nov**, 02:00 slot) | examples/enemies_queue.py (voice `tools/tts/eq2.py` + `tools/tts/vc.py eq2`; flashback: rookie hero + nine goblins + dogpile + mourning ring + grey elder carving the rule board; LEVEL 2 pop; old ticket story kept in `scratch_old/enemies_queue_v2_ticket.py` outside the repo) | scene_qa clean, `check.py` 12/13 (WARN = planned flashes / subtitle changes) -> `renders/enemies_queue/why_do_enemies_attack_one_at_a_time_33s.mp4`; mux used `acompressor=threshold=0.2:ratio=3:attack=5:release=80,loudnorm=I=-14:TP=-2.0` (the plain loudnorm left a 0.1 dBTP peak); not posted; captions `captions/enemies_queue.md` |

| Why is this potion only 1 gold? (39 s, wordless, pilot for `othercreators/RAPOR.md`, 22 Nov) | examples/one_gold_potion.py (brief `briefs/one_gold_potion.md`; no voice, music box + SFX; 270x480 x4, depth outline, HUD counter, flashback) | draft1 rendered: `check.py` 12/13 -> `renders/one_gold_potion/draft1.mp4`; not posted; Enes must watch + listen; weak spots in `reviews/one_gold_potion.md` |
| Why does the tutorial guy never come with you? (34.6 s final = 41.6 s x 1.2, 14-day test day 3, **22:00 slot**, Format 3.0) | examples/tutorial_guy.py (voices `tools/tts/tg.py` + `multi.py` + `vc.py tg`; new tutorial guide (hat, stick, gold ? patch), fence + gate, field, slime, gold jump trails, seasons) | scene_qa clean, `check.py` 11/13 (FAIL = script length: the file is the 1.2x speed-up; WARN = planned pops), critique r2 in `reviews/tutorial_guy.md` -> `renders/tutorial_guy/why_does_the_tutorial_guy_never_come_with_you_35s.mp4` (1.0x kept in `renders/tutorial_guy/scratch_old/`); not posted; captions `captions/tutorial_guy.md` |
| Why do heroes smash every pot? (32.5 s final = 39 s x 1.2, day 3, **02:00 slot**, Format 3.0) | examples/pots.py (voices `tools/tts/pt.py`; new old woman (bun, apron, shawl, gold brooch), cottage + door shelf + shelf wall + table, pots with lids, shards, boy flashback, tea) | scene_qa: two 3-vertex knight/woman overlaps (28.6-29.0 s), `check.py` 11/13 as above, critique r2 in `reviews/pots.md` -> `renders/pots/why_do_heroes_smash_every_pot_32s.mp4`; not posted; captions `captions/pots.md` |
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

## 14-day single-format test (from 21 Nov 2026)
- Plan, posting rules and the topic queue: `briefs/SERIES_14_DAYS.md`. Two "Why do <game trope>?" videos a day, scheduled: 22:30-23:30 TR (~60 s story) and ~01:00 TR (~30 s); best videos on weekend evenings; YouTube is the main platform (posting rules in the series plan). Day 1 = `briefs/skip_speech.md` + `briefs/enemies_queue.md` (GO.md).
- **Day 1 built on the PC, 21 Nov (no-stop run)** - both MP4s in the video table. Voice option 1 for both (Kokoro bm_george -> ChatterboxVC -> Enes timbre); new generic `tools/tts/vc.py <name...>` replaces the per-video `*_vc.py` copies; `ss.py` has reusable `src()` / `build()` (`eq.py` imports them; the mixed-sample-rate fix from sc.py is built in). All lines pass `sc_check.py` (pitch +3..+14 % of the reference, no clipping). **Enes must listen.**
- skip_speech: 40.5 s, not the brief's ~32 s (97 words + skip montage + an 11-minute time-lapse; the slot allows 40-60 s). Weak spots: the locked boss has no mouth, so "speaking" is gestures + a filtered murmur; the over-the-shoulder gate shots show the boss's back + cape on the right third; the heroes are the same knight recoloured (orange / green / purple / blue).
- enemies_queue: 29.2 s. Set = the loot_restocker hallway (the brief allowed hall or arena; the last10 hall needs `tts/l10`, not on this PC). Frame 0 shows #47's face + the ticket "47"; the fight at the front is revealed by a camera swing at 0.9-1.9 s (not in frame 0 as the brief said). Font has no '&': the menu says SAVE AND QUIT. Two silent gaps found by `check.py` (15.5 s after the quit, 26.5 s after the last hit) were filled with a low pause hum + torch crackle and a short "defeated" jingle.
- Next (GO.md): Claude writes the day-2 briefs (queue #4 NPC weather, #2 mimic).

- **21 Nov 2026 audio fix (GO.md):** the day-1 crackle line (`rng.random(n)<p` gate) is replaced by `nightkit.audio.soft_fire()` in `skip_speech.py` and `enemies_queue.py`; audio + mux re-run, both MP4s overwritten (picture unchanged), `check.py` 12/13 as before. Jumps > 6x local level: skip_speech 1793 -> 600, enemies_queue 1910 -> 378; the rest are the planned square-wave SFX (the same count with the fire removed: 578 / 351). Fire = -44 / -48 dBFS RMS, voice -12 dBFS. The old line still sits in the already posted `four_phases.py` and `save_killed.py` (not touched). **Enes must listen.**

## Day 2 (21 Nov 2026, PC, no-stop run, Tone 2.0)
- **Why do NPCs repeat the same line?** (40.5 s, 22:00 slot, re-voiced fast 21 Nov): `examples/npc_well.py` (voice `tools/tts/nw.py` + `tools/tts/vc.py nw`; new old villager + wife box humans, stone well + windlass + rope, dusk village, lantern, ring, RPG dialogue box; knight reused, heroes recoloured by cape only). `scene_qa` clean (one planned contact: the old man takes the ring), `check.py` 12/13 (WARN = hard cuts / dialogue box pops) -> `renders/npc_well/why_do_npcs_repeat_the_same_line_40s.mp4`; not posted; captions `captions/npc_well.md`. All 13 lines kept; 0.3 s between lines; the climb is compressed to ~3.4 s. `scene_qa`: one 3-vertex knight/old-man overlap at 32.8-33.3 s (the ring hand-over, not visible).
- **Why do mimics pretend to be chests?** (23.2 s, 02:00 slot, re-voiced fast + picture fixes 21 Nov): `examples/mimic.py` (voice `tools/tts/mm.py` + `vc.py mm`; chest with a hinged lid, teeth/tongue/eyes only after "learned to bite", coin, hero hands, stone alcove, one torch). `scene_qa` clean, `check.py` 12/13 -> `renders/mimic/why_do_mimics_pretend_to_be_chests_23s.mp4`; not posted; captions `captions/mimic.md`.
- Voice for both (re-done 21 Nov per GO.md, four_phases pace): Kokoro bm_george speed 1.22, pauses 0-0.15 s inside a line, ~0.3 s between lines (was 1.0 / 0.45 s) -> ChatterboxVC -> Enes timbre; `sc_check.py` all lines ok (pitch +5..+11 %). **Enes must listen.**
- Sound: new `nightkit.audio.soft_fire()` (day-1 crackle fix) is used in mimic only; npc_well has no fire. Jumps > 6x local level: mimic 379, npc_well 478 (planned SFX; no per-sample gate anywhere).
- Weak spots: see `reviews/npc_well.md` and `reviews/mimic.md` (limbs + contacts scored 7 in both: the ring hand-over and the montage hands in mimic (kneel pose and opening brightness fixed in round 3); the old man glides instead of walking; mimic's quiet stretch is gone (longest voice gap 1.2 s, npc_well 0.8 s). Mimic picture fixes done: big pointed teeth + dark red mouth + tongue, frame 0 lid open a crack with breathing and a tooth glint, the tongue rises when calm so the coin sits visibly on it with a steady glint).

## ONE TAKE (optional extra system, 22 Nov 2026)
- Named by Enes. One continuous take, the camera breathes with the story, bright hero object, counters, loops. Rules `briefs/STYLE_one_take.md`, test `examples/onetake/mimic_v2.py` (26 s), tool `tools/qa/look_metrics.py`. PC final render: GO.md.

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
- v2 (Enes asked): the video starts with 1.0 s of the end scene (note slapped on, police lights, driver sprints; no voice, FX only), then the story from frame 0 of Gary. `PRE`/`TEASE0` in the script; total 32.6 s; first cut was 2.3 s, Enes: too long.
- Weak spots left (2 scores at 7): Gary is small in the driveway shot (lines 3-4); keys / sandwich / note contact is only suggested by the arm over the cabin; police cars are plain dark boxes; sound judged by measurement only (-14.3 LUFS, -1.5 dBTP, no gap > 0.6 s). script_lint hints (pace 2.97 w/s, no pivot / question beat) ignored on purpose: the brief fixes the narration.
- scene_qa: the driver stand-in jumps at 29.08 s (QA only, he is not drawn before he steps out). Untracked scratch files `test1.png` etc. stay uncommitted.

## 20 Nov 2026 - four_phases (GO.md task, no-stop run)
- Built per `briefs/four_phases.md`: `examples/four_phases.py` (cloak boss 3.6 -> 2.4 -> 1.2 m, three hits, cloak slips, goblin reveal, knight + goblins under the cloak, 4 phases, old goblin day off). Render driver: `tools/render_parts.py` (parallel parts + concat + loudnorm mux, ~1 min).
- **Voice option used: 1 (ChatterboxVC).** Kokoro bm_george speaks each sentence (`tools/tts/fp.py src`), `tools/tts/fp_vc.py` converts to `voice/enes_ref_main.wav` (Chatterbox embedded python), `fp.py build vc` assembles. VC pitch follows the source loosely, so each sentence is pulled to ~+5 % of the reference pitch (clamped +-2.5 st) with rubberband. Automatic checks (`tools/tts/fp_check.py`): no clipping (peak 0.95), longest pause 0.22 s, pitch +5..+9 % of the reference (116 Hz), every line fits its window. Fallbacks 2/3 were not needed. **Enes must listen** (accent, artefacts from VC + pitch shift); the Kokoro-only version is `fp.py build src`.
- Brief inconsistency (kept the brief's picture): the new boss counts 4 phases, but the old goblin sits outside, so only knight + middle + kid are under the cloak (3 members). Cloak height / HUD show 4.8 m / "PHASES: 4" as written.
- Weak spots: sword contact on the cloak reads weakly from the side camera (limbs+contacts 7/10); goblins step into the cloak skirt (a hop hides most of it); the old goblin's cup is a plain white box; sound judged by measurement only (-14.1 LUFS, peak -1.4 dBFS, no gap > 0.6 s between voice-level sounds). Script lint hints (no "Wait...?" beat, no explicit "because") ignored: the narration is fixed by the brief.
- Setup note: `tools/tts/lr.py` must have been run once (loot_restocker.py reads `tts/lr/script.json` at import).

- 20 Nov 2026: Enes scheduled four_phases and stolen_car (TR 23:00 and 21 Nov 02:00, for the Europe / USA evenings); thumbnails made with `tools/thumb.py`. Next: read both at 48 h, fill ANALYTICS.md section 13.

- **21 Nov 2026 (Enes's request, both day-2 videos):** the question (line 1) is now a centred title card (outlined text, no box, ~34 % from the top); every other sentence uses a roomier subtitle box (scale 7.0, letter spacing 6.9, line height 12.8, wider padding, 130 px from the bottom). npc_well dialogue box moved up 18 internal px so a 4-line subtitle never touches it. Mimic bugs fixed: teeth poked through the closing lid (they retract now), the coin glint beam poked through the closed lid, frame-0 title no longer a subtitle. Re-rendered both MP4s, `check.py` 12/13 each (WARN = planned pops).

- **21 Nov 2026 (hooks + own voice):** punchier questions: mimic "Why did this chest learn to bite?", npc_well "Why has this man said the same line for forty years?" (line 2 now "It is the only thing he says."); voices regenerated, mimic line 1 no longer off-pitch (was 209 Hz). Enes may record the lines himself: `briefs/ENES_VOICE_SCRIPTS.md`; put his per-sentence wavs in `tts/<mm|nw>_own/<key>_<i>.wav`, run `python tools/tts/<mm|nw>.py build own`, then `render_parts.py` as usual (ss.build mode `own` only trims silence). Both MP4s re-rendered, `check.py` 12/13.

- **21 Nov 2026 (skip_speech + enemies_queue, Enes's request):** both got the new subtitle style + the question as a centred title card (skip_speech hook now "Why do final bosses give a speech nobody hears?", `tools/tts/ss.py` re-voiced; the PRESS X TO SKIP prompt moved up). enemies_queue got a completely new story (see its row and `briefs/enemies_queue.md` v3). skip_speech.mp4 re-rendered (check.py 12/13). **Enes must listen.**

- **21 Nov 2026 (Enes's own voice, enemies_queue):** Enes recorded the 15 sentences of the new story (`vocal/enemies_queue/Kayit (1..15).m4a`, sentence order = `tools/tts/eq2.py` D order; raw files NOT committed). `tools/tts/own_prep.py eq2 vocal/enemies_queue` removes the record-button click, trims, levels; `python tools/tts/eq2.py build own` assembles (RMS-levelled lines, soft limiter, pauses from the D table) -> `tts/eq2/` (the AI version is kept in `tts/eq2_synth/`). The video re-timed itself: 45.4 s. Final: `renders/enemies_queue/why_do_enemies_attack_one_at_a_time_45s.mp4` (check.py 12/13, -14.6 LUFS, -1.7 dBTP, longest voice gap 1.3 s). Same workflow for the other videos.
- **21 Nov 2026:** enemies_queue final = the own-voice render sped up 1.2x (ffmpeg `setpts=PTS/1.2,fps=24` + `atempo=1.2`, then compressor + loudnorm): `renders/enemies_queue/why_do_enemies_attack_one_at_a_time_38s.mp4` (37.8 s, -14.7 LUFS, -1.7 dBTP). The 1.0x version (45 s) is in `scratch_old/`.

## Day 3 (23 Nov 2026, PC, no-stop run, Format 3.0) - tutorial_guy (22:00) + pots (02:00)
- **New shared tools:** `nightkit/look.py` (`outline()` ported from one_gold_potion.py, which now imports it; `follow_group()` group framing with bisection + ternary search on the blend; `blend_pts()` eased entry/exit of a helper; `Path` = Catmull-Rom camera track whose speed never drops to zero; `smooth_shot()` temporal smoothing of the group framing; `Subtitles` = speaker-coloured subtitles, question = title card (`card_y/card_sc/card_n` options); `hud_counter()`), `tools/tts/multi.py` (several voices: narrator via VC, characters raw Kokoro, `build src|vc|own` with per-sentence Enes takes), `tools/qa/framing.py` (middle third %, camera speed, subject height per time; no render), `tools/speedup.sh` (the 1.2x step). `NW.human()` got optional `hair`, `coat_col`, `acc` and `kind='boy'` (defaults = old output; run `python tools/qa/regress.py compare` after changes).
- **Format 3.0 result:** guide in the middle third in 97 % of frames, woman 100 %; frame 0 subject 52 % / 48 % of the height; the camera is never static (>= 0.09 m/s); cuts: tutorial_guy 1 hard cut + 1 dissolve, pots 2 hard cuts.
- **Voices:** narrator = Kokoro bm_george -> ChatterboxVC (checked with `sc_check.py`: +5..+9 % of the reference). Characters raw: guide bm_fable, hero 1 am_michael (-2 st), hero 2 af_nicole, hero 3 am_adam (+4.5 st), knight am_onyx (soft); pots: woman bf_emma, heroes am_adam / bm_lewis / am_michael, knight am_onyx. `sc_check.py` flags the characters on purpose (different pitch); the pitch tracker is unreliable on short lines. **Enes must listen** to all five voices. Recording lists: `briefs/ENES_VOICE_SCRIPTS.md` (`tts/tg_own/`, `tts/pt_own/`, then `python tools/tts/<tg|pt>.py build own` + `render_parts.py` + `tools/speedup.sh`).
- **Deviations from the briefs:** tutorial_guy is 34.6 s final, not 42 (the story needs less; no padding); the SPACE key cap shows only on the guide's two lines (no tooltip in frame 0: title card + counter already there); hero 2's cape is teal (the knight owns blue); title card sits at 20 % from the top (not 34 %) so it does not cover the face; pots: the "shelf" of the last line is the door shelf where the pot stands, and the woman does not leave her spot at tea (table next to her).
- **Weak spots:** box-human limbs (hop over the gate, lid lift, seated knight legs look like slabs); sound judged by measurement only; a season pop at the end of the rain crane; the hero line `3b` in pots is measured at 92 Hz by an unreliable tracker.
- Rebuild: `python tools/tts/<tg|pt>.py src`, `<chatterbox python> tools/tts/vc.py <tg|pt>`, `python tools/tts/<tg|pt>.py build vc`, `python tools/render_parts.py examples/<tutorial_guy|pots>.py --prefix <tg|pt> --audio <tutorial_guy|pots>.wav --out ../renders/<name>/scratch_old/<name>_1x.mp4`, `sh tools/speedup.sh <1x> <final>`.

- **23 Nov 2026 (later): Enes REJECTED both day-3 videos** (many bugs; stories too simple and boring; emotion does not land) and deleted the renders (the MP4 paths in the video table no longer exist; they are not posted). The code, voices recipe and tools stay in the repo. Enes will review and rewrite the stories himself and send them back; do not rebuild tutorial_guy / pots from the old briefs. Lessons: plant a detail that the twist reverses, give the key emotional beat a wordless 2-3 s, narrator states less; never call a video good from tool output alone (Claude cannot watch/listen).

## 23 Nov 2026 - THE LAST RESPAWN, phases 1-3 (PC, Blender) - STOPPED at the gate
- Merged the cloud branch `ccr-91720a78-gihjic` into `misty-pilot` (ANALYTICS: the PC's Four Phases section is now 20).
- `blender/last_respawn.py` (alley + tower + chamber, puppets posed by a frame handler, numpy sound, loop-time design) and
  `tools/tts/lrs.py` (Kokoro placeholders). Outputs in `renders/last_respawn/`: `frame0_1080x1920.png`, `last_respawn_hook_0001-0192.mp4`,
  `last_respawn_loop_0001-0216.mp4`, `sheet_mid.png`. Details, measurements, problems and the time estimate: `reviews/last_respawn.md`.
- **Waiting for Enes:** continue in Blender or move the episode to nightkit; knight pop at the loop boundary OK or not; his 13 voice takes
  (`briefs/last_respawn_voice_sheet.md` -> `vocal/last_respawn/`).
- **Later (Enes: continue in Blender, keep the knight pop):** the whole film is animated; full preview
  `renders/last_respawn/last_respawn_full_0001-1392.mp4`. Waiting for: Enes's look OK, his voice takes, then the final render.
  **After the Blender film: make the same film in nightkit** (identical camera / timing / staging, only our graphics) - import the
  track data from `blender/last_respawn.py`.

