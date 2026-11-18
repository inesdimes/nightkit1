# Review log - lightning_missed

Every score >= 8 before the final render; at most 3 rounds, then the decision goes to Enes.

## Round 1 - 2026-11-18 - lightning_missed_draft.mp4

- duration 33.00 s, 792 frames, 19 cuts at 0.04, 0.08, 0.12, 0.25, 4.58, 9.88, 9.92, 9.96, 10.00, 12.88, 16.96, 17.00, 17.04, 17.08, 21.33, 26.00, 28.54, 28.58, 28.62
- opening motion (first 1 s): 6.21
- still stretches (>= 2 s): none
- quiet stretches (>= 1.5 s without voice-level sound): none
- longest gap between voice-level sounds: 0.9 s
- sheet: out/qa/lightning_missed/critique_r1.png

| criterion | score 1-10 | worst problem |
|---|---|---|
| readability (faces, eyes, props) | 8 | knight, shield, pillar, door all read; strike 1 frame 0 is washed out by the flash but the bolt and MISS read by 0.1 s |
| motivation + timing | 8 | beats are placed on measured TTS starts; the replay slow-motion lands strike 2 at 16.9 s on "You see" |
| framing | 7 | CAM 02 knight is only ~20 % of the height; CAM 03 shows his back, huge (about 60 %) |
| limbs + contacts | 8 | scene_qa clean; shield and pose stagger read, crouch looks stiff |
| text | 9 | all UI and subtitles fit; HIGH / LOW readable but sit close to the path line |
| cuts | 8 | 3 hard cuts as briefed; flash frames show as pops in check.py (intended) |
| sound vs picture | 8 | measured only: no silence, gap 0.9 s, -13.9 LUFS, -1.4 dBTP. Enes judges the sound |
| pacing | 8 | narration 2.46 w/s with room for UI and effects; CAM 04 holds on a closed door for the last 6 s |

Top 3 fixes this round:
1. CAM 02: bring the camera closer so the knight is larger (the pillar + door must stay in frame)
2. CAM 03: show the boots from the side rather than the back (boots on two tiles must read)
3. last 6 s: the closed door alone is a still-ish hold; add the castle in frame (wider CAM 04) so "equipped the whole castle" is literal
