# WHY DO HEROES SMASH EVERY POT? - brief v2 (23 Nov 2026, Claude) - day 3, 02:00 slot (~30 s FINAL time at 1.2x), Tone 2.0 + Format 3.0
Rules: briefs/SERIES_14_DAYS.md ("Tone 2.0" + "Format 3.0": constant camera, subject in focus + group framing, character cards, several voices, 1.2x).
PS1, nightkit. Narrator = Kokoro bm_george S=1.22 -> ChatterboxVC (Enes timbre). Characters = other Kokoro voices, raw.

## Story
An old woman sets out a new clay pot every morning; every hero smashes it for the coin inside. Forty years, no thank you. She hides the coin on purpose: her son
left to be a hero and never wrote, and she hopes someone does the same for him. One knight does not swing: he puts the coin back and sits down; she makes tea.
The pot stays on the shelf. Human truth: waiting for someone who left / a small kindness sent out into the world.
(Not a copy of day 2: nobody leaves an object, the knight gives her his time.)

## Character cards
| Who | Silhouette / prop | Idle loop | Signature gesture | Reaction to the subject | Voice (test first) | Subtitle colour |
|---|---|---|---|---|---|---|
| **Old woman (SUBJECT)** | grey bun, apron, shawl, broom | dusts a pot, hums (a few notes), glances at the door every 3 s | presses the coin into the clay, pats the pot | fussy, warm, hopeful each time the door opens | warm old female (bf_emma slowed a touch, or af_nicole lowered) | gold |
| **Hero 1** (grey cape, loud) | big swing | swings before he is in the door | smash, grab, leave | does not see her | am_adam, gruff: "Ha!" | red |
| **Hero 2** (blue cape, greedy) | counts out loud | rubs hands | shakes the shards for loose coins | "Is that all?" | bm_lewis, sneering | blue |
| **Hero 3** (green cape, in a hurry) | runs | already out the door | kicks the pot | "Out of my way!" | am_michael | green |
| **Knight** | locked knight | still, head tilts at the pot | lifts the lid, sees the coin, puts it back, takes off his helmet | gentle | am_michael low: "I won't. Sorry." | white-blue |
| **Boy (flashback only)** | small, wooden sword | swings at air | waves | - | no speech: a child's laugh SFX | - |
| **Narrator** | - | - | - | - | Enes timbre | white |

## Script and picture (times are FINAL; ~88 words)
| # | speaker | line | picture + camera move |
|---|---|---|---|
| 1 | Narrator | Why do heroes smash every pot? | frame 0: CLOSE on a pot at the door: a sword shatters it, shards + a gold coin fly at the camera; the camera swings left and settles on the woman's face in the doorway (>= 50 % of height, she flinches and picks up her broom); HUD "POTS: 14,600" |
| 2 | Woman | "Come in, dear. Mind the step." (hopeful, to Hero 1) | tracking shot beside her as she carries a new pot to the shelf; group framing holds her + Hero 1 |
| 3 | Hero 1 / Hero 2 / Hero 3 | "Ha!" / "Is that all?" / "Out of my way!" | orbit of 15 degrees around the shelf: three heroes, three smashes; each leaves; she sweeps after each, shoulders a little lower; counter ticks |
| 4 | Narrator | Forty years. Nobody ever said thank you. | slow push-in on her hands pressing a coin into a pot |
| 5 | Narrator | Her son left to be a hero, and never wrote. | flashback (warm-grey) crane down on the boy at the door with a wooden sword; the doorway empties; counter freezes |
| 6 | Narrator | So every hero leaves her house with a coin. Maybe someone is doing the same for him. | pull-back: a hero's back going down the lane, coin glint; she watches from the doorway |
| 7 | Narrator | One knight walked in, and didn't swing. | camera tracks the knight in; group framing: knight + woman + the pot |
| 8 | Knight | "I won't. Sorry." | push-in: gauntlet lifts the lid, sees the coin, puts it back, sits on the stool |
| 9 | Woman | "Oh... sit, sit. Tea?" | two-shot orbit at the table; she sets two cups, steam; HUD becomes "POTS SMASHED TODAY: 0" (the only UI) |
| 10 | Narrator | That pot is still on the shelf. The only one she never had to replace. | slow crane up to the whole pot on the shelf, glowing gold in the window light; ends on the frame-0 composition (door, pot, woman), whole this time |

## Assets
Reuse knight(), motion helpers, HUD, `tools/render_parts.py`, `follow_group()` (built in the tutorial_guy session; if that session has not happened yet, build it here). NEW: old woman,
three recoloured heroes, clay pots + shards, cottage doorway + table + two cups, the boy. One accent colour gold (coin, last-pot glow). Interior dark warm brown, one window as main light.

## Sound
Morning birds, "tock" of a pot set down, filtered shatter (no per-sample gate), coin clink, her humming (4-5 soft notes), kettle, steam, cup set down; flashback goes quiet, a wooden-sword tap; low two-note pad under the last line.

## No-stop rule
Never wait for Enes. All QA (script_lint, scene_qa, critique >= 8, check.py; add: subject inside the middle third in >= 95 % of frames, no speaker cropped). Render to renders\pots\. Captions: captions/pots.md.
