# Review log - pots

Every score >= 8 before the final render; at most 3 rounds, then the decision goes to Enes.

## Round 1 - 2026-11-23 - why_do_heroes_smash_every_pot_32s.mp4

- duration 32.54 s, 781 frames, 3 cuts at 11.29, 14.58, 18.92
- opening motion (first 1 s): 5.54
- still stretches (>= 2 s): none
- quiet stretches (>= 1.5 s without voice-level sound): none
- longest gap between voice-level sounds: 1.3 s
- sheet: out\qa\pots\critique_r1.png

| criterion | score 1-10 | worst problem |
|---|---|---|
| readability (faces, eyes, props) |  |  |
| motivation + timing |  |  |
| framing |  |  |
| limbs + contacts |  |  |
| text |  |  |
| cuts |  |  |
| sound vs picture |  |  |
| pacing |  |  |

Top 3 fixes this round:
1. 
2. 
3. 

## Round 2 - 2026-11-23 - why_do_heroes_smash_every_pot_32s.mp4

- duration 32.54 s, 781 frames, 3 cuts at 11.29, 14.58, 18.92
- opening motion (first 1 s): 5.54
- still stretches (>= 2 s): none
- quiet stretches (>= 1.5 s without voice-level sound): none
- longest gap between voice-level sounds: 1.3 s
- sheet: out\qa\pots\critique_r2.png

| criterion | score 1-10 | worst problem |
|---|---|---|
| readability (faces, eyes, props) | 8 | woman: grey bun, apron, gold brooch; pot + lid + coin read; shards fly at the camera in frame 0 |
| motivation + timing | 8 | each smash lands on its line; the pot glows only after the coin goes back |
| framing | 8 | woman 48 % of the height at frame 0 and again at the last frame; middle third in 100 % of frames; she is small (27-31 %) in the tea two-shot |
| limbs + contacts | 7 | the knight's lid lift is suggested (hand near the lid), the seated knight's legs look like slabs, her arms at the pot are long brown bars; one 3-vertex knight/woman overlap at 28.6-29.0 s |
| text | 8 | title card above her face, speaker colours, one counter (POTS -> POTS SMASHED TODAY: 0) |
| cuts | 9 | 2 hard cuts (flashback in / out); the other "cut" the tool reports at 18.9 s is a subtitle swap |
| sound vs picture | 7 | measured only: -13.8 LUFS, -2.0 dBTP, longest voice-level gap 1.3 s; Enes must listen |
| pacing | 8 | 32.5 s final (brief 30); no quiet stretch |

Top 3 fixes this round:
1. Give the knight a real seated pose / hands on the lid (limbs 7).
2. Tea two-shot: bring the camera closer once the cups are down.
3. Real hands for the woman at the pot (her sleeves read as bars).

Round 1 -> 2: the anonymous hero now fades out of the group framing instead of popping out; the cut critique.py reports at 18.9 s turned out to be a subtitle-box swap, not a camera jump. Round 2: scene_qa 2 tiny knight/woman overlaps (3 vertices), check.py 11/13 (FAIL script length = 1.2x speed-up by design).
