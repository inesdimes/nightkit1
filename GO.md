# GO - the current tasks for the PC session (read this when Enes says "GO.md")
Updated by the cloud session, 21 Nov 2026. Day 2 FIXES (Enes: the mimic story is too slow and he did not like its voice).

Cause: the day-2 voices (`tools/tts/mm.py`, `tools/tts/nw.py`) use speed 1.0 and 0.45 s pauses ("Tone 2.0: calm, slow").
The voice Enes liked is four_phases (`tools/tts/fp.py`): speed 1.22, pauses 0-0.15 s. Tone 2.0 is now corrected in briefs/SERIES_14_DAYS.md.

1. `git pull origin ccr-91720a78-gihjic`. Read `briefs/SERIES_14_DAYS.md` (Tone 2.0, voice bullet) and `reviews/mimic_review.md`.
2. Voice for BOTH day-2 videos (mimic and npc_well): same settings as fp.py (S=1.22, pauses inside a line 0-0.15 s, the same pitch trim),
   ~0.3 s between lines, same Kokoro bm_george -> ChatterboxVC chain. Re-time every picture cue to the new sentence timings.
   The videos get shorter; that is wanted (mimic ~22-25 s, npc_well ~40-45 s). No quiet stretch over ~1 s (mimic 14.5-16.7 s goes).
3. Mimic picture fixes (reviews/mimic_review.md): the coin clearly visible inside the chest with a glint, held on "He left a coin";
   teeth bigger and pointed with a dark mouth inside the lid (+ tongue) so the bite reads; frame 0: lid open a crack, teeth glint, a slow breath.
4. No-stop rule: never wait for Enes. All QA (scene_qa, critique >= 8, check.py, no jumps > 6x local level from noise).
5. Overwrite renders\mimic\ and renders\npc_well\; update CONTINUE.md; commit and **push**.
