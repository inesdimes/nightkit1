# WHY DOES THE TUTORIAL GUY NEVER COME WITH YOU? - brief v2 (23 Nov 2026, Claude) - day 3, 22:00 slot (~40 s FINAL time at 1.2x), Tone 2.0 + Format 3.0
Rules: briefs/SERIES_14_DAYS.md ("Tone 2.0" + "Format 3.0": constant camera, subject in focus + group framing, character cards, several voices, 1.2x).
PS1, nightkit. Narrator voice = Kokoro bm_george S=1.22 -> ChatterboxVC (Enes timbre). Character voices = other Kokoro voices, raw (not converted).

## Story
An old tutorial guide stands at the edge of the starting field, next to a low fence, and says "Press SPACE to jump" to every new hero. Ten thousand heroes,
every one jumps the fence and never looks back. Forty years ago he tried it himself, saw the first slime and froze. He has stood here ever since, teaching
the one thing he could not do. One knight finishes the lesson, turns back and holds out a hand. The old man takes ONE step past the fence, goes back to
his spot, and now leaves the gate open. Human truth: being the one who stays behind / teaching a courage you never found.

## Character cards
| Who | Silhouette / prop | Idle loop | Signature gesture | Reaction to the subject | Voice (test first) | Subtitle colour |
|---|---|---|---|---|---|---|
| **Guide (SUBJECT)** | old, big hat, pointing stick, "?" patch, green tunic | bounces on his toes, stick tapping the post every 2 s | claps once, stick up: "Press SPACE!" | proud of every hero, a flicker of envy when they leave | warm old Kokoro male (bm_fable or bm_lewis), cheerful, slightly rushed | gold |
| **Hero 1** (red cape) | fast, rude | already running | jumps without listening | "Yeah, yeah!" | am_michael, bored | red |
| **Hero 2** (blue cape) | nervous, over-careful | checks the fence twice | tiny hop | "Is it safe?" | af_nicole, quick | blue |
| **Hero 3** (purple cape) | cocky | flexes | show-off flip | "Watch this!" | am_adam, loud (bm_george is the narrator, do not reuse it) | purple |
| **Knight** (SUBJECT's mirror) | locked knight | stands still, head turns slowly | turns back, holds out a gauntlet | patient | one line only, am_michael low, soft: "Just one step." | white-blue |
| **Slime** | one green box | wobble | fills the frame | menace that is actually tiny | squelch SFX only | - |
| **Narrator** | - | - | - | - | Enes timbre | white |

## Script and picture (times are FINAL; ~108 words)
| # | speaker | line | picture + camera move |
|---|---|---|---|
| 1 | Narrator | Why does the tutorial guy never come with you? | frame 0: guide CLOSE (face + stick, >= 50 % of height, bouncing); slow push-in then drift back and up; tooltip "PRESS SPACE TO JUMP"; HUD "HEROES TAUGHT: 10,000" |
| 2 | Guide | "Press SPACE to jump!" | camera tracks left as Hero 1 runs in; group framing holds guide + hero (both inside); the hero jumps in a gold arc: counter 10,001 |
| 3 | Hero 1 / Hero 2 / Hero 3 | "Yeah, yeah!" / "Is it safe?" / "Watch this!" | camera orbits 15 degrees around the guide while three heroes pass; seasons change behind him; the guide stays centred, each hero leaves the frame on the right; guide's head follows each one, hand half raised |
| 4 | Narrator | Nobody ever looks back. | crane up on the empty field: the guide small but still the brightest thing |
| 5 | Narrator | Forty years ago, he tried it himself. | flashback (warm-grey), tracking shot behind a young guide stepping over the fence |
| 6 | Narrator | He saw the first slime, and froze. | push-in: the slime fills the frame, the young guide's hands rise and stop; squelch |
| 7 | Narrator | He walked back. He has stood here ever since. | pull-back: young guide walks back, dissolves into the old guide on the same spot; the counter freezes |
| 8 | Guide | "Press SPACE to jump!" (softer, to nobody) | slow push-in on his tired face; stick taps the post |
| 9 | Narrator | Then one knight finished the lesson, and didn't leave. | camera follows the knight's jump, he lands, turns: first hero ever to turn |
| 10 | Knight | "Just one step." | two-shot orbit over the fence (group framing: guide + knight both fully in frame), knight's hand held out |
| 11 | Narrator | The old man looked at the grass on the other side. | slow creeping close-up on his eyes, wind in the gold grass beyond |
| 12 | Narrator | He took one step. | camera tracks his boot over the fence line; HUD becomes "STEPS OUTSIDE: 1" (the only UI) |
| 13 | Narrator | Then he went back to his spot. But now he leaves the gate open. | pull-back + crane: gate swings open, the knight waits on the far side; ends on the frame-0 composition (guide, stick, tooltip), still drifting |

## Assets
Reuse knight(), motion helpers, tooltip code (npc_well.py), HUD, `tools/render_parts.py`. NEW: guide (or recoloured old man), fence + gate, field, slime, two more cape colours.
New helper needed (build in this session, reuse for every later video): `follow_group()` camera (see Format 3.0 item 2) in `nightkit.motion` or `tools/`.
One accent colour: warm gold (jump arc, grass beyond the fence). Field cool blue-grey; the guide's side darker than the far side.

## Sound
Wind, grass steps, tooltip "blip", soft jump "boing" per hero, flashback goes quiet then the slime squelch; one soft footstep and a held breath for the step; gate creak; low two-note pad under the last line. No per-sample gate.

## No-stop rule
Never wait for Enes. All QA (script_lint, scene_qa, critique >= 8, check.py; add: the subject's centre stays inside the middle third in >= 95 % of frames, no speaker cropped). Render to renders\tutorial_guy\. Captions: captions/tutorial_guy.md.
