# GO - read this when Enes says "GO.md"

## What changed in the cloud session (21-22 Nov 2026) - read these before any new video
1. **Posting rules** (`briefs/SERIES_14_DAYS.md`, "Posting rules"): target Europe + America, YouTube is the main platform;
   1st video 22:30-23:30 TR, 2nd ~01:00 TR, best videos on weekend evenings, all scheduled. Data: `ANALYTICS.md` sections 16-19.
2. **Frame 0 rule** (series plan, Tone 2.0): readable at a glance, moving in the first second, never a skip/exit/loading prompt
   (the speech video had "PRESS X TO SKIP" in frame 0 and 95 % swiped on YouTube's first sample).
3. **Voice**: same pace as four_phases (speed 1.22, short pauses); depth comes from story and picture, not a slow voice.
4. **Sound**: never a per-sample random gate `rng.random(n) < p` (that was the day-1 crackle). Use `nightkit.audio.soft_fire()` for fire.
5. **ONE TAKE** (`briefs/STYLE_one_take.md`, `examples/onetake/`): an optional extra system (one continuous take, the camera breathes
   with the story). It does not replace the main look. Tool: `tools/qa/look_metrics.py`.
6. **Research kit** (`research/README.md`): `tools/llm/gemini.py --youtube <link>` + `research/hook_template.txt` to analyse reference Shorts with Gemini.
7. `vocal/` is in `.gitignore`: Enes's raw recordings are never committed.

## Current task - THE LAST RESPAWN (Blender, phases 1-3, then STOP)
**SHELVED 23 Nov 2026 (late): Enes did not like the story or the render - back to nightkit shorts.** Earlier status: finalized with placeholder voices - Blender final + nightkit version (same camera / staging / timing) in `renders/last_respawn/`, details in `reviews/last_respawn.md`. Open: Enes's 23 voice takes (`briefs/last_respawn_voice_sheet.md`), then re-render both (one audio rebuild, both read the same tracks).
1. `git pull origin ccr-91720a78-gihjic`. Read `briefs/last_respawn.md` FIRST (it overrides parts of `briefs/last_respawn_gpt.md`), then the GPT brief.
2. Use **Opus** for this task (new world, new rigs). Blender 5.3 per CLAUDE.md; characters are rigid-part puppets keyframed from Python.
3. Run phase 1 (blockout + frame-0 still), phase 2 (hook test 00:00-00:08, preview quality, placeholder voices) and phase 3
   (loop test 00:52-00:58 + 00:00-00:03 joined). Then STOP and give Enes the two preview MP4s + the frame-0 still + an honest note
   on how long the full film would take in Blender.
4. Commit scripts (not renders) and push. Enes's raw voice takes live in `vocal/last_respawn/` (gitignored); do not wait for them in phases 1-3.

## Day 3 (PC session, 23 Nov 2026) - rejected
tutorial_guy + pots were built in Format 3.0 and rejected by Enes (stories had no emotion + bugs); renders deleted, stories to be rewritten (CONTINUE.md).
Format 3.0 (constant camera, follow_group, multi-voice, 1.2x, 270x480 + outline) stays the default: `briefs/SERIES_14_DAYS.md`. Four Phases / Stolen Car 48 h numbers: `ANALYTICS.md` section 20.

## Earlier task (One Take mimic final render) - still open, lower priority
Updated by the cloud session, 22 Nov 2026. ONE TAKE: final render of the mimic story (Enes liked the system and the camera moves).

ONE TAKE is an optional extra system, separate from the main Insert Disc 2 look: one continuous take whose camera pulls back and
pushes in with the story, a big bright hero object, counters/tags, the end loops into the start. Rules: `briefs/STYLE_one_take.md`.

1. `git pull origin ccr-91720a78-gihjic`.
2. Voice: replace the placeholder lines in `$TTS_DIR/mmx/` (keys 1-7, text in `tools/onetake/voice_mimic.py`) with Enes's voice
   (his own recording via `tools/tts/own_prep.py`, or the Kokoro -> ChatterboxVC chain, four_phases pace). Re-time `M.LINES` in
   `examples/onetake/mimic_v2.py` to the new durations (keep the camera keys in step with the lines).
3. Fix the known visual bugs: the knight's armour blows out to white in the close-ups (lower the key light on him / the bloom);
   the coin must read clearly (bigger, glint, a beat longer); the time-lapse heroes a little bigger in frame; the chest interior
   not over-lit; aim for `python tools/qa/look_metrics.py` motion >= 3 (more teeth / gold / particle motion), keep brightness >= 50, contrast >= 35.
4. Render with `PART=a:b` in parallel + `PART=audio`, mux, `python tools/qa/check.py` must pass. Output: renders\one_take_mimic\.
5. No-stop rule: never wait for Enes. End: MP4 path + look_metrics numbers; update CONTINUE.md; commit and **push**.
