# GO - the current tasks for the PC session (read this when Enes says "GO.md")
Updated 23 Nov 2026 by Claude (PC). DAY 3 of the 14-day test. Day-2 fixes from 21 Nov are done (see CONTINUE.md "Day 2").

Start: `git pull`, read `briefs/SERIES_14_DAYS.md` (Tone 2.0 + frame 0 lesson), `othercreators/RAPOR.md` section 4 Aşama A, `ANALYTICS.md` sections 16-17.

1. **22:00 slot, ~42 s:** `briefs/tutorial_guy.md` - Why does the tutorial guy never come with you?
2. **02:00 slot, ~32 s:** `briefs/pots.md` - Why do heroes smash every pot?
Voice for both: same chain as four_phases (`tools/tts/fp.py` S=1.22, pauses 0-0.15 s, ~0.3 s between lines, Kokoro bm_george -> ChatterboxVC). Copy `tools/tts/nw.py` / `vc.py <name>` as the template.
Frame 0: subject >= 50 % of frame height, moving in the first second, no skip/exit prompt. One accent colour, one HUD counter, last frame = frame 0 composition.
No-stop rule: never wait for Enes. All QA (script_lint, scene_qa, critique >= 8, check.py). Render to renders\tutorial_guy\ and renders\pots\. Captions in captions/<name>.md.
Update CONTINUE.md, commit and push at the end.

Note: the queue item "Legendary Sword Only 50 Gold" was moved out of day 3 - it repeats the one_gold_potion story (shopkeeper, 50 gold, "last hero"). Rework it before use.
