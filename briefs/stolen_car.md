# WHAT HAPPENS TO THE GUY WHOSE CAR YOU STEAL? - brief (20 Nov 2026, Claude; idea chosen by Enes)
Trend: a big open-world crime game just came out. We ride the trend with the genre's tropes (stolen cars, wanted stars,
the owner left on the sidewalk) and NO game name, logo, character, map or music inside the video. The game's name appears
only as one hashtag in the description (Enes's decision, his risk; see captions/stolen_car.md).
Same family as Final Boss / four_phases: a question every player has + a twist + a small heart. PS1 look, nightkit. ~32 s.

## Story
Gary's car has been stolen 900 times. He gave up fighting and started leaving the keys, a sandwich and a note.
Every evening the car comes back, full tank, new dents. Gary thinks the driver is the nicest guy in town.
The last shot shows the driver: five wanted stars, police lights behind him - he parks gently, leaves a "THANKS GARY" note, speeds off.

## Narration (one narrator, ~85 words)
| # | line | picture (cue lands 0-3 frames before the key word) |
|---|---|---|
| 1 | What happens to the guy whose car you steal? | frame 0: CLOSE on Gary (bathrobe, slippers, coffee mug) on the sidewalk, his car screeching away behind him, "VEHICLE STOLEN" banner |
| 2 | Meet Gary. His car has been stolen nine hundred times. | Gary sighs, HUD counter "STOLEN: 899 -> 900" ticks |
| 3 | First, he bought a lock. Then an alarm. Then a second car. | three quick beats in the driveway: steering-wheel lock, blinking alarm, second car parked next to the first |
| 4 | They stole that one too. | both driveway spots empty, Gary holds two key sets |
| 5 | So now, Gary leaves the keys in the ignition. | Gary leans into the car, keys in, door left open |
| 6 | And a sandwich on the passenger seat. | sandwich placed on the seat |
| 7 | And a note: "Bring her back by six." | note on the dashboard, 2D overlay text BRING HER BACK BY 6 |
| 8 | Every evening at six, the car comes back. Full tank. New dents. | sunset; the car rolls back into the driveway, dented, "FUEL: FULL" HUD |
| 9 | Gary has never met the driver. | Gary at the window with his mug, smiling |
| 10 | He thinks it's the nicest guy in town. | street view: the driver's back/arm through the window, five wanted stars blinking at the top |
| 11 | The rest of the town disagrees. | the driver leaves a THANKS GARY note, sprints off; police lights + sirens fill the street; end on the last word |

## Assets
- NEW: Gary (box human: bathrobe, slippers, mustache, mug), the driver (seen from behind / an arm: cap, tank top), a car (box body, 4 wheels,
  dent decals = darker quads), a second car (colour variant), a police car (light bar, red/blue emissive), Gary's house front + driveway,
  a street with palms, lamp posts, a few parked cars; day -> sunset lighting.
- Reuse: motion helpers (glide, creep, kick), HUD/subtitle code from examples/four_phases.py, render driver tools/render_parts.py.
- HUD (2D): VEHICLE STOLEN banner, STOLEN counter, FUEL: FULL, five wanted stars (white outline, yellow fill), notes.

## Camera (5 setups)
A close on Gary (frame 0, big and moving) -> B driveway medium (lock / alarm / second car / keys / sandwich / note) ->
C sunset wide (car returns) -> D window two-shot (Gary + mug) -> E street (driver, stars, police lights).

## Sound
Tyre screech + engine (frame 0), counter tick, lock clunk, alarm chirp, door, paper rustle, evening birds, engine idle,
police sirens at the end. Ducked under the voice; no silent stretch > 1.2 s. No real music or game sounds.

## Voice
Same as four_phases (approved by Enes): Kokoro bm_george source -> ChatterboxVC to `voice/enes_ref_main.wav` (tools/tts/fp.py + fp_vc.py
pattern). Alternative if VC fails: `tools/tts/enes.py` (Chatterbox, Enes reference, 2b settings).

## No-stop rule (Enes)
Do not wait for Enes at any step. Run script_lint, voice, asset lock, scene_qa, critique rounds (>= 8, max 3), check.py, final render.
Lessons from the four_phases review (reviews/four_phases_review.md): the close-up must show the character the line talks about;
props held in hands, never floating; characters fully inside the frame; frame 0 big and moving.
