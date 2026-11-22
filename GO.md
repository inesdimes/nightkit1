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

## Current task
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
