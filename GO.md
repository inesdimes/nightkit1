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
None (25 Nov 2026: Enes says every task is done). The next task will be written here by the cloud session.
