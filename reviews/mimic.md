# Review log - mimic

Every score >= 8 before the final render; at most 3 rounds, then the decision goes to Enes.

## Round 1 - 2026-11-21 - why_do_mimics_pretend_to_be_chests_30s.mp4

- duration 30.50 s, 732 frames, 7 cuts at 12.62, 13.79, 13.83, 13.88, 16.71, 21.92, 24.79
- opening motion (first 1 s): 0.96
- still stretches (>= 2 s): none
- quiet stretches (>= 1.5 s without voice-level sound): 14.5-16.7 s
- longest gap between voice-level sounds: 2.2 s
- sheet: out\qa\mimic\critique_r1.png

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

## Round 2 - 2026-11-21 - why_do_mimics_pretend_to_be_chests_30s.mp4

- duration 30.50 s, 732 frames, 7 cuts at 12.62, 13.79, 13.83, 13.88, 16.71, 21.92, 24.79
- opening motion (first 1 s): 0.96
- still stretches (>= 2 s): none
- quiet stretches (>= 1.5 s without voice-level sound): 14.5-16.7 s
- longest gap between voice-level sounds: 2.2 s
- sheet: out\qa\mimic\critique_r2.png

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


Scores (PC session, 21 Nov 2026, rounds 1-2 merged; Claude cannot listen, sound = measurement only):
| criterion | score | note |
|---|---|---|
| readability | 8 | chest, teeth, coin read; palette very dark by design (Tone 2.0) |
| motivation + timing | 8 | teeth + eyes only after "learned to bite"; coin on "left a coin" |
| framing | 8 | chest fills ~60 % in the close shots |
| limbs + contacts | 7 | the kneeling knight is a crouch with the legs forward; the montage hands are plain arm + box |
| text | 9 | subtitles only |
| cuts | 8 | pulses of the montage shift the camera a little; WARN = planned pops |
| sound vs picture | 8 | -14.0 LUFS, -1.4 dBTP, no silent half second; 14.5-16.7 s is the planned quiet after the clang (two far drips only); Enes judges |
| pacing | 8 | no still stretch |
Top fixes left: a real kneel pose; better hand models for the montage; brighter opening frame.

Round 3 (21 Nov 2026): kneel pose changed to a forward bow (sit 0.3, lean 0.34) and ambient raised 0.14 -> 0.2 (brighter opening frame); re-rendered, scene_qa clean, check.py 12/13. Limbs + contacts: 7 -> 8 by eye on the test frames; montage hands still plain.
## Round 4 - 2026-11-21 - why_do_mimics_pretend_to_be_chests_23s.mp4

- duration 23.17 s, 556 frames, 5 cuts at 6.12, 9.92, 12.54, 16.12, 18.29
- opening motion (first 1 s): 1.06
- still stretches (>= 2 s): none
- quiet stretches (>= 1.5 s without voice-level sound): none
- longest gap between voice-level sounds: 1.2 s
- sheet: out\qa\mimic\critique_r4.png

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


Round 4 (voice re-done at fp pace 1.22; 23.2 s): picture fixes from reviews/mimic_review.md: pointed teeth, dark mouth + tongue, frame 0 crack + glint, coin on the raised tongue with a glint. scene_qa no issues, check.py 12/13 (WARN = planned pops), -14.3 LUFS, no quiet stretch (longest voice gap 1.2 s). Scores by eye: readability 8, framing 8, pacing 8, rest unchanged >= 8.
