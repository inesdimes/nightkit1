# Review log - ghost_boo

Every score >= 8 before the final render; at most 3 rounds, then the decision goes to Enes.

## Round 1 - 2026-11-18 - why_do_ghosts_say_boo.mp4

- duration 44.17 s, 1060 frames, 4 cuts at 16.46, 26.79, 32.58, 37.71
- opening motion (first 1 s): 1.20
- still stretches (>= 2 s): none
- quiet stretches (>= 1.5 s without voice-level sound): none
- longest gap between voice-level sounds: 0.4 s
- sheet: out/qa/ghost_boo/critique_r1.png

| criterion | score 1-10 | worst problem |
|---|---|---|
| readability (faces, eyes, props) | 7 | in the payoff (camera C, from 37.71) the ghost turns bright blue-white; in A/B it is cream. Eyes readable everywhere. |
| motivation + timing | 8 | reads without narration: whisper, knock, flicker panic, BOO, lantern left behind |
| framing | 8 | both characters in frame in A; ghost + lantern in B and C; UI and subtitles clear of faces |
| limbs + contacts | 8 | knock hand stops ~10 cm before the wall (hidden by depth from this camera) |
| text | 7 | 1x subtitle font is small on a phone (channel standard, kept) |
| cuts | 7 | 37.67 -> 37.71: colour jump on the ghost (ambient 0.34 -> 0.68 for camera C) |
| sound vs picture | n/a | not scored: Claude cannot listen; measured only (no quiet stretch, -13.9 LUFS) |
| pacing | 8 | no still or quiet stretch >= 1.5 s; longest voice gap 0.4 s |

Top 3 fixes this round:
1. Camera C ambient back toward A/B (0.68 -> ~0.45) so the ghost keeps its colour across the 37.71 cut.
2. (optional) Subtitles at 2x scale: bigger on phones, but changes the channel look -> Enes decides.
3. (minor) Knock hand could reach the wall; not visible from camera A, left as is.

Status: below 8 on readability / text / cuts -> not cleared for a new final. Waiting for Enes (v3 was already delivered before this tool existed).

## Round 2 - 2026-11-18 - why_do_ghosts_say_boo.mp4

- duration 44.17 s, 1060 frames, 4 cuts at 16.46, 26.79, 32.58, 37.71
- opening motion (first 1 s): 1.31
- still stretches (>= 2 s): none
- quiet stretches (>= 1.5 s without voice-level sound): none
- longest gap between voice-level sounds: 0.4 s
- sheet: out/qa/ghost_boo/critique_r2.png

| criterion | score 1-10 | worst problem |
|---|---|---|
| readability (faces, eyes, props) | 8 | ghost keeps its colour into the payoff; both eyes readable in every sampled frame |
| motivation + timing | 8 | unchanged from round 1 |
| framing | 8 | 2x subtitles sit on the bottom edge, below the ghost and the lantern in every camera |
| limbs + contacts | 8 | knock hand ~10 cm short of the wall (not visible from camera A), kept |
| text | 8 | 2x subtitles, max 2 rows of <= 13 characters, widest row 162 of 180 px; no dangling one-word rows |
| cuts | 8 | 37.67 -> 37.71 colour now matches (camera C ambient 0.68 -> 0.45) |
| sound vs picture | n/a | audio unchanged from v3; Enes judges |
| pacing | 8 | unchanged: no still or quiet stretch, longest voice gap 0.4 s |

Top 3 fixes this round: none blocking.

Status: every scored criterion >= 8 -> cleared. check.py 9/9. Delivered as v4.

