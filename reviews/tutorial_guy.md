# Review log - tutorial_guy

Every score >= 8 before the final render; at most 3 rounds, then the decision goes to Enes.

## Round 1 - 2026-11-23 - why_does_the_tutorial_guy_never_come_with_you_35s.mp4

- duration 34.62 s, 831 frames, 5 cuts at 5.25, 5.62, 9.50, 10.21, 27.83
- opening motion (first 1 s): 1.19
- still stretches (>= 2 s): none
- quiet stretches (>= 1.5 s without voice-level sound): none
- longest gap between voice-level sounds: 1.1 s
- sheet: out\qa\tutorial_guy\critique_r1.png

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

## Round 2 - 2026-11-23 - why_does_the_tutorial_guy_never_come_with_you_35s.mp4

- duration 34.62 s, 831 frames, 2 cuts at 9.50, 10.21
- opening motion (first 1 s): 1.32
- still stretches (>= 2 s): none
- quiet stretches (>= 1.5 s without voice-level sound): none
- longest gap between voice-level sounds: 1.1 s
- sheet: out\qa\tutorial_guy\critique_r2.png

| criterion | score 1-10 | worst problem |
|---|---|---|
| readability (faces, eyes, props) | 8 | frame 0 reads at once (hat, beard, stick, gold "?" patch, 52 % of the height); the SPACE key cap floats a bit far above the hat |
| motivation + timing | 8 | each hero enters on his own line; the dissolve young -> old lands on line 7; the knight's turn is slow but motivated |
| framing | 8 | guide inside the middle third in 97 % of frames (tools/qa/framing.py), never static; he is small (25-30 %) while 2 heroes are in the group and in the rain crane |
| limbs + contacts | 7 | box humans: the step over the gate and the hand-out are suggested (hop, arm forward), no real contact; the knight's sitting legs are not used here |
| text | 8 | subtitle colour = speaker, title card above the face; counter + key cap are the only UI |
| cuts | 9 | 1 hard cut (flashback in), 1 dissolve (out); the camera never jumps (smoothing of the group framing) |
| sound vs picture | 7 | measured only: -13.7 LUFS, -1.3 dBTP, longest voice-level gap 1.1 s; Enes must listen (5 voices, VC narrator) |
| pacing | 8 | 34.6 s final (brief 42): the story needs less; no padding. Every line has a picture beat |

Top 3 fixes this round:
1. The 7s are limb contacts + sound-by-measurement: they stay 7 until Enes listens / the box humans get real hands.
2. A season pop at the end of the rain crane (11.4 s build): the ground palette switches in one frame.
3. Two heroes in the group make the guide small for ~1 s; acceptable for the "everyone fits" rule.

Round 1 was rendered before the group-framing smoothing (5 camera jumps) and is superseded by round 2. Round 2: scene_qa clean, check.py 11/13 (FAIL script length = 1.2x speed-up by design, WARN = planned pops).
