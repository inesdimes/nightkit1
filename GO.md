# GO - the current task for the PC session (read this when Enes says "GO.md")
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
