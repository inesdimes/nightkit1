# WHY DOES THE TUTORIAL GUY NEVER COME WITH YOU? - brief (23 Nov 2026, Claude) - day 3, 22:00 slot (~42 s), Tone 2.0
Rules: briefs/SERIES_14_DAYS.md ("Tone 2.0" + frame 0 lesson), othercreators/RAPOR.md Aşama A (subject >= 50 % of frame height in frame 0, ONE accent colour,
ONE HUD counter, last frame = frame 0). PS1, nightkit, Enes-timbre voice (Kokoro bm_george S=1.22 -> ChatterboxVC, `tools/tts/fp.py` settings).

## Story
An old tutorial guide stands at the edge of the starting field, next to a low fence, and says "Press SPACE to jump" to every new hero.
Ten thousand heroes. Every one jumps the fence and never looks back. Forty years ago he tried it himself: he crossed the fence, saw the first
slime, froze, and walked back. He has stood here ever since, teaching others the one thing he could not do.
One knight finishes the lesson and does not leave. He stands at the fence and holds out a hand. The old man looks at the grass on the other
side, takes ONE step past the fence, and goes back to his spot. But now he leaves the gate open.
Human truth: being the one who stays behind / teaching others a courage you never found.

## Narration (~100 words, 0.3 s between lines)
| # | line | picture |
|---|---|---|
| 1 | Why does the tutorial guy never come with you? | frame 0: CLOSE on the old guide (face + raised pointing stick), tooltip box "PRESS SPACE TO JUMP"; he bounces on his toes (moving at once); HUD top-left: "HEROES TAUGHT: 10,000" |
| 2 | He has taught "press space to jump" ten thousand times. | pull back: a hero jumps the fence in a gold arc, the counter ticks to 10,001 |
| 3 | Every hero listens. Every hero jumps. Nobody looks back. | three quick heroes (cape colours only) clear the fence and run off; seasons change behind the guide (leaf, snow, rain); counter keeps ticking |
| 4 | Forty years ago, he tried it himself. | warm-grey flashback, a young guide steps over the fence |
| 5 | He saw the first slime, and froze. | the slime (one box, wobbling) fills the frame; the young guide's hands rise, stop |
| 6 | He walked back. He has stood here ever since. | the young guide walks back across the fence line; cut to now: same spot, old man, same pose; the counter is frozen on the cut |
| 7 | So he teaches the one thing he couldn't do. | close on his hand tapping the fence post; the tooltip: "PRESS SPACE TO JUMP" |
| 8 | Then one knight finished the lesson, and didn't leave. | the knight jumps once, lands, turns back (first hero ever to turn) |
| 9 | He stood at the fence, and held out his hand. | two-shot over the fence: knight's gauntlet open, the old man's stick lowered |
| 10 | The old man looked at the grass on the other side. | slow creeping close-up on his eyes; wind moves the grass beyond the fence (the only warm gold in the scene) |
| 11 | He took one step. | his boot crosses the fence line; HUD swaps to "STEPS OUTSIDE: 1" (the counter is the only UI, it replaces the old one) |
| 12 | Then he went back to his spot. | he steps back, taps his hat, raises the stick: the same pose as frame 0 |
| 13 | But now he leaves the gate open. | the gate swings open in the wind; wide shot, the knight waiting on the far side; last frame composes like frame 0 (guide, stick, tooltip); end on the last word |

## Assets
- Reuse: knight(), motion helpers, tooltip/dialogue-box code from npc_well.py, HUD code, `tools/render_parts.py`. The old-man model of npc_well.py
  recoloured (green tunic, brown hat) is allowed if a new model is too slow; otherwise NEW: tutorial guide (box human, pointing stick, big hat, a "?" patch).
- NEW: low wooden fence + gate (boxes), starting field (flat grass quad, 3 round trees, one signpost), one slime (single green box, wobble).
- One accent colour: warm gold (the grass beyond the fence, the arc of the jump). Field itself cool blue-grey dusk; the guide's side is slightly darker than the far side.

## Camera (5 setups, hard cuts 2.5-4 s, no drift)
A close on the guide (frame 0) -> B wide of the fence + heroes passing -> C flashback (warm-grey, low angle on the slime) ->
D two-shot knight / guide over the fence (creeping close-up) -> E closing wide, ends on the frame-0 composition.

## Sound
Wind, soft grass footsteps, a dull "blip" for the tooltip, a tiny jump "boing" per hero (square wave, soft, varied pitch), flashback: air goes dead then the slime's wet wobble;
the single step: one soft footstep and a held breath of quiet; the gate creak; a low two-note pad under the last line. Never a per-sample random gate.

## No-stop rule
Never wait for Enes. All QA (script_lint, scene_qa, critique >= 8, check.py). Render to renders\tutorial_guy\. Captions: captions/tutorial_guy.md.
