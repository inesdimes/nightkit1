# GO - the current task for the PC session (read this when Enes says "GO.md")
Updated by the cloud session, 21 Nov 2026. FIX the crackle in the day-1 audio (Enes: "cızırtı var").

## What the cloud session measured
Both day-1 MP4s (skip_speech 40 s, enemies_queue 29 s) contain many isolated sample spikes. The cause is the "torch crackle" line
in `build_audio()`:  `s.filt(noise, lo=1500, hi=7000) * (s.rng.random(n) < 0.002)` - single random samples of high-passed noise,
~96 per second, i.e. digital static / vinyl crackle, not a fire. In enemies_queue the paused stretch adds a second, louder copy
(`< 0.004`, x0.5) -> clusters of clicks at 15.2-16.3, 17.6-18.0 and 19.7-20.4 s. skip_speech: clicks at 15.5, 22.5, 22.8 s.
The same line exists in examples/four_phases.py (447) and examples/save_killed.py (419), already posted: do NOT re-upload those
(posted videos are never re-edited); only stop using the line from now on.

## Do
1. `git pull origin ccr-91720a78-gihjic`.
2. In `examples/skip_speech.py` and `examples/enemies_queue.py`: delete every `(s.rng.random(n)<...)` crackle line.
   If a fire sound is wanted, use a soft bed instead: low-passed noise (200-1500 Hz) with a slow random amplitude wobble, at least
   20 dB under the voice, and a few real crackles (3-6 per second, each a 5-15 ms burst with an exponential decay, never single samples).
3. Re-run only the audio and the mux (`PART=audio`, then mux with the existing video parts; the picture does not change).
4. Check: `python tools/qa/check.py <mp4>` passes; no sample-to-sample jump > 6x the local level (the cloud check); write the numbers.
5. Never use a per-sample random gate (`rng.random(n) < p`) for sound again: add that sentence to PIPELINE.md (sound section).
6. Overwrite the two MP4s in renders\skip_speech\ and renders\enemies_queue\, commit, **push**.
