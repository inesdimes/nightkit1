# NOTES — decisions, DEVIATIONS, TODO

## DEVIATIONS (the brief contradicts itself or cannot be met with the allowed tools)
1. **Duck vs. MISS timing.** Section 11 says the duck is 6 frames after the miss_blip everywhere, but the tables give MISS 70/duck 77 (+7), MISS 115/duck 113 (-2), MISS 144/duck 142 (-2), MISS 173/duck 170 (-3). The tables are authoritative. Every duck still starts after the arrow has arrived (arrival = release + 6 frames). duck_step plays on the duck frame. Reported as DEVIATION in qa_report.txt.
2. **Master arrow ledger.** The brief says "1 in hand, floor 1" after the handoff; 3 arrows were released, so conservation gives floor 2. Floor 2 is used.
3. **"Five shots. Five misses."** appears after 3 shots (master) / 4 shots (extended). The text is kept exactly as written.
4. **Extended S8:** "NO subtitle" contradicts "f658-701 Not once." inside S8. The explicit frame line wins: "Not once." shows 658-701, nothing else in S8.
5. **CAM C** "archer as a bow arm and legs in the foreground" is impossible with the locked positions (the archer is behind that camera). CAM B also does not see the archer. Cameras were not moved.
6. **CAM D** is too narrow to see the goblin walk down the corridor. The walk route bends toward the camera (piecewise linear) so the goblin enters the frame.
7. **Narration:** no offline TTS binary (espeak-ng / pyttsx3) on the build machine, so narration is skipped (nothing is faked). The espeak-ng code path exists but is UNTESTED.
8. **Loudness:** -16 LUFS is measured with ffmpeg's ebur128 (a subprocess), not computed in numpy. A soft limiter keeps peaks under -1 dBFS.
9. **Music level:** "-22 LUFS relative to the mix" is read as ~6 dB under the ambience + SFX bed.

## Decisions (simplest option, logged)
- Archer at (2.8, -0.40); body faces the viewer's side (side-on archery stance); the shot lane is z = archer z + 0.109 (misses beside the board). In the extended S3 he steps back 0.07, so the arrow lands 0.15 left of the board.
- Arrows: flight is 6 frames at constant speed; at the wall plane the flying arrow disappears and an arrow lies on the floor in a fixed pile slot (this is what the floor count tracks).
- The goblin's "bend" is a squash plus head pitch; "pats" are two arm taps; the extended arrow crate is one box plus 3 shafts.
- Popups that survive a hard cut move to the top-right and fade out there (otherwise they cover the new shot's face).
- Characters animate with linear interpolation only, integer frames, no easing, no IK at run time (one brute-force arm solve at import for the TAKE pose).

## Known weak spots
- Bow string clears the forearm by only ~2 mm in the DRAW pose (passes the assert).
- Goblin walk arm swing is weak; goblin DUCK squashes the whole body (slight neck gap).
- Archer face is tiny (by the brief's 1/4-frame rule).

## TODO
- Narration: when an offline TTS exists, `python render.py --cut master` picks it up automatically. Line -> start frame (from `timeline.CUTS[...]['subs']`):
  master: 5, 96, 163, 245, 302 | extended: 5, 96, 187, 283, 358, 446, 557, 658.
