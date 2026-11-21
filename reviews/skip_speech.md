# Review log - skip_speech

Every score >= 8 before the final render; at most 3 rounds, then the decision goes to Enes.

## Round 1 - 2026-11-21 - ss_draft1.mp4

- duration 40.50 s, 972 frames, 32 cuts at 0.12, 6.42, 12.00, 14.54, 14.58, 14.62, 14.67, 14.71, 14.75, 14.79, 15.88, 16.79, 16.83, 16.88, 16.92, 16.96, 17.00, 17.04, 17.12, 17.75, 17.79, 17.83, 17.88, 17.92, 17.96, 18.00, 18.46, 20.50, 23.00, 27.12, 33.21, 35.71
- opening motion (first 1 s): 1.13
- still stretches (>= 2 s): none
- quiet stretches (>= 1.5 s without voice-level sound): 28.5-30.9 s
- longest gap between voice-level sounds: 2.4 s
- sheet: out\qa\skip_speech\critique_r1.png

| criterion | score 1-10 | worst problem |
|---|---|---|
| readability (faces, eyes, props) | 8 | boss, scroll, HUD, happy ^ ^ eyes read; heroes in the gate shots are small (~30 px) |
| motivation + timing | 8 | skip / flash / VICTORY land on "skip" and "next"; hit on "dodge" |
| framing | 7 | gate shots (C): knight tiny, boss's back fills the right side |
| limbs + contacts | 8 | sword touches the boss on the hit (scene_qa intersect at 35.6 s = the planned contact) |
| text | 9 | PRESS X TO SKIP, REHEARSAL #10,950, SKIPPED 1,248, 11:02, +1 FAN all readable |
| cuts | 8 | the "cuts" at 14.5-18.0 s are the planned fight flashes |
| sound vs picture | 7 | the time-lapse (28.5-30.9 s) is quiet: fast chatter + clock too soft |
| pacing | 8 | no still stretch; three skips in 4 s keep the middle fast |

Top 3 fixes this round:
1. time-lapse sound: fast chatter x3, clock ticks x3.5
2. gate shots tighter (fov 58 -> 50) so the heroes read bigger; boss cape darker so the back reads as a cloak, not a red blob
3. fight flash shorter and lighter (0.28 s / 85 % -> 0.2 s / 75 %)

## Round 2 - 2026-11-21 - ss_draft2.mp4

- duration 40.50 s, 972 frames, 25 cuts at 0.12, 6.42, 12.00, 14.54, 14.58, 14.62, 14.67, 14.71, 15.88, 16.79, 16.83, 16.88, 16.92, 17.12, 17.75, 17.79, 17.83, 17.88, 17.92, 18.46, 20.50, 23.00, 27.12, 33.21, 35.71
- opening motion (first 1 s): 1.13
- still stretches (>= 2 s): none
- quiet stretches (>= 1.5 s without voice-level sound): none
- longest gap between voice-level sounds: 1.0 s
- sheet: out\qa\skip_speech\critique_r2.png

| criterion | score 1-10 | worst problem |
|---|---|---|
| readability (faces, eyes, props) | 8 | heroes bigger in the gate shots; the lying boss reads from above (horns, ^ ^ eyes) |
| motivation + timing | 8 | the bow is short (0.9 s) before the cut to the fight |
| framing | 8 | the boss's back + cape still covers the right third of the gate shots (over-the-shoulder by design) |
| limbs + contacts | 8 | sword-on-boss contact at the hit is intended; clapping hands meet |
| text | 9 | all HUD lines readable, subtitles match the voice |
| cuts | 8 | detected cuts are the planned flashes |
| sound vs picture | 8 | measured only: no quiet stretch, max gap 1.0 s; Enes judges the murmur + voice |
| pacing | 8 | 40.5 s, the story needs it (22:00 slot) |

All scores >= 8 -> final.
Weak spots left: the boss model is the locked blocky final_boss boss (no mouth, so "speaking" is shown by gestures + murmur only); the scroll is a flat strip; the heroes are recoloured copies of the same knight.
