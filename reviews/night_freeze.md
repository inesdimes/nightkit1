# Review log - night_freeze

Every score >= 8 before the final render; at most 3 rounds, then the decision goes to Enes.

## Round 1 - 2026-11-27 - why_do_npcs_stand_still_at_night_draft1.mp4

- duration 29.17 s, 700 frames, 10 cuts at 2.21, 4.08, 7.38, 8.08, 11.46, 14.62, 16.29, 18.25, 18.92, 21.88
- opening motion (first 1 s): 2.30
- still stretches (>= 2 s): none
- quiet stretches (>= 1.5 s without voice-level sound): 26.8-29.1 s
- longest gap between voice-level sounds: 2.3 s
- sheet: out\qa\night_freeze\critique_r1.png

| criterion | score 1-10 | worst problem |
|---|---|---|
| readability (faces, eyes, props) | 7 | the fog eyes small in the reveal |
| motivation + timing | 8 | - |
| framing | 7 | Marta's cape in front of the cat / hat / dawn shots (fixed on stills before draft 1) |
| limbs + contacts | 8 | stills only; broom + wave hand approximate |
| text | 9 | - |
| cuts | 8 | the dawn shot opens on an empty dark spot for ~1 s (kept: his spot is empty) |
| sound vs picture | - | check FAIL: 0.5 s silence at 4.0 s + a quiet tail 26.8-29.1 s |
| pacing | 8 | - |

Top 3 fixes this round:
1. a constant night pad + louder wind, owl, eye creak (silence + quiet tail)
2. louder footsteps in the loop walk
3. stronger push-in on frame 0 (opening motion 2.3)

## Round 2 - 2026-11-27 - why_do_npcs_stand_still_at_night_29s.mp4

- duration 29.17 s, 700 frames, 10 cuts at 2.21, 4.08, 7.38, 8.08, 11.46, 14.62, 16.29, 18.25, 18.92, 21.88
- opening motion (first 1 s): 2.56
- still stretches (>= 2 s): none
- quiet stretches (>= 1.5 s without voice-level sound): none
- longest gap between voice-level sounds: 1.2 s
- sheet: out\qa\night_freeze\critique_r2.png

| criterion | score 1-10 | worst problem |
|---|---|---|
| readability (faces, eyes, props) | 8 | - |
| motivation + timing | 8 | - |
| framing | 8 | flame close-up: armour fills the frame |
| limbs + contacts | 8 | stills only |
| text | 9 | - |
| cuts | 8 | flags = planned cuts / subtitle swaps |
| sound vs picture | - | measured: -13.9 LUFS, -2.0 dBTP, no silence (Enes listens) |
| pacing | 8 | opening motion 2.6 (dark, slow creep): low on purpose for the creepy tone |

Top 3 fixes this round: none blocking -> final = `renders/night_freeze/why_do_npcs_stand_still_at_night_29s.mp4`.

## Round 3 - 2026-11-27 - why_do_npcs_stand_still_at_night_v2_29s.mp4

- duration 29.38 s, 705 frames, 11 cuts at 2.21, 4.08, 7.38, 8.08, 11.46, 14.62, 16.29, 18.25, 18.75, 19.12, 22.08
- opening motion (first 1 s): 3.16
- still stretches (>= 2 s): none
- quiet stretches (>= 1.5 s without voice-level sound): none
- longest gap between voice-level sounds: 1.2 s
- sheet: out\qa\night_freeze\critique_r3.png

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

## Round 4 - 2026-11-27 - why_do_npcs_stand_still_at_night_v2_29s.mp4

- duration 29.38 s, 705 frames, 11 cuts at 2.21, 4.08, 7.38, 8.08, 11.46, 14.62, 16.29, 18.25, 18.88, 19.12, 22.08
- opening motion (first 1 s): 3.16
- still stretches (>= 2 s): none
- quiet stretches (>= 1.5 s without voice-level sound): none
- longest gap between voice-level sounds: 1.2 s
- sheet: out\qa\night_freeze\critique_r4.png

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

## Round 4 - 2026-11-27 - why_do_npcs_stand_still_at_night_v2_29s.mp4

- duration 29.38 s, 705 frames, 11 cuts at 2.21, 4.08, 7.38, 8.08, 11.46, 14.62, 16.29, 18.25, 18.88, 18.92, 22.08
- opening motion (first 1 s): 3.16
- still stretches (>= 2 s): none
- quiet stretches (>= 1.5 s without voice-level sound): none
- longest gap between voice-level sounds: 1.2 s
- sheet: out\qa\night_freeze\critique_r4.png

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

## Enes's review of v1 (28 Nov 2026) -> v2
Enes: the boss looks bad, the lighting does not read as light, NPCs pass through walls, the torch is too big and not in the hand, moves are jerky.
Measured causes + fixes:
- Bram stood INSIDE the cart the whole film and Marta walked through it at dawn (the cart read as a wall/table on the stills; never
  checked). New per-frame intersection check (character vertices vs houses / cart / barrel / posts): 0 hits after moving the cart.
- Jerky: per-frame jumps of head/wrists up to 0.81 m (Bram's pull), 0.37 m (Marta), snaps on every pose-branch switch. Fix: every pose
  is averaged over +-0.12 s inside its shot (smooth_pose), the knight turns in 0.7 s, walking stride follows the speed, Bram is lifted
  then drawn away over 1.6 s, the hat only leaves his head when the hand is there. Remaining max ~0.14 m/frame = normal arm speed.
- Light: real ground pools (masked to the street by the depth buffer, so people are not painted over), glows for torch / windows / eyes,
  a soft beam + a bright spot where the gaze lands + a real light there; the spot fades in (no pop when the head is off-screen).
- The Watcher redesigned: hooded robe, cracked white mask, lantern eyes in dark sockets, sleeves, long pale jointed fingers.
- Torch: own model, stick through the fist along the grip axis, flame 0.5 (was 1.0-1.25 with a 0.45 m stick above the hand).
- Final v2: `renders/night_freeze/why_do_npcs_stand_still_at_night_v2_29s.mp4` (29.4 s, check 11/13 = 1.2x length + planned cuts).
  Remaining critique flags at 18.9 s = the camera pan + the spot sweeping onto Bram (checked frame by frame: continuous).
## Round 5 - 2026-11-27 - why_do_npcs_stand_still_at_night_v3_32s.mp4

- duration 32.21 s, 773 frames, 12 cuts at 2.21, 4.88, 8.17, 8.88, 12.25, 15.42, 17.08, 19.04, 19.92, 20.75, 24.25, 27.21
- opening motion (first 1 s): 2.66
- still stretches (>= 2 s): none
- quiet stretches (>= 1.5 s without voice-level sound): none
- longest gap between voice-level sounds: 1.4 s
- sheet: out\qa\night_freeze\critique_r5.png

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

## Enes's review of v2 (28 Nov 2026) -> v3
- Cover question bigger + centred (auto-size per line). DAWN box sized from its text.
- The knight's LEFT arm reached across his body: hd's right hand sits at local +x, Marta stands at his right -> torch in the LEFT hand,
  wave + sword with the RIGHT. Lesson: hd 'r' = local +x (for yaw 0 = world +x).
- "Walking but not walking": hd walk_cycle lifts the feet with the default lift even at stride 0 -> walk/stride/lift only while moving.
- "Is anyone home?" made no sense with everyone in the street -> "Hello? Why is nobody moving?" (answered by "They aren't broken. They're hiding.").
- Why Bram threw his hat was unclear -> he takes it off and WAVES it high: "Over here!" (new line 10): he moves on purpose to pull the gaze off
  the knight; the hat falls from his hand when he is taken.
- Why Marta put the hat on him was unclear -> at dawn she picks the hat out of the puddle on camera, Bram respawns bald and pats his head,
  then she puts it on. The pointed hat read as a traffic cone -> red felt hat with a brim, band and white feather.
- Checks: 0 intersections, Marta/Bram no overlap, joint jumps > 0.15 m/frame only in Bram's (intended) accelerating pull into the fog.
  Day ambience + lute added (check found 3 silent half-seconds in the dawn part).
- Final v3: `renders/night_freeze/why_do_npcs_stand_still_at_night_v3_32s.mp4` (32.2 s, -14 LUFS, check 11/13 = 1.2x length + planned cuts).
