# WHY DO HEROES SMASH EVERY POT? - brief (23 Nov 2026, Claude) - day 3, 02:00 slot (~32 s), Tone 2.0
Rules: briefs/SERIES_14_DAYS.md ("Tone 2.0" + frame 0 lesson), othercreators/RAPOR.md Aşama A (subject >= 50 % of frame height in frame 0, ONE accent colour,
ONE HUD counter, last frame = frame 0). PS1, nightkit, Enes-timbre voice (Kokoro bm_george S=1.22 -> ChatterboxVC, `tools/tts/fp.py` settings).

## Story
An old woman in a cottage at the edge of a village sets out a new clay pot every morning. Every hero who walks in smashes it for the coin inside.
Forty years, no thank you. The coin is hers on purpose: her son left to be a hero and never wrote. She hides a coin in every pot so each hero leaves
with something in his pocket - hoping someone is doing the same for him. One knight walks in and does not swing. He finds the coin, puts it back,
sits down at her table. She makes him tea. The pot stays on the shelf.
Human truth: waiting for someone who left / a small kindness sent out into the world.
(Different from day 2 on purpose: nobody leaves a coin, nobody is dead; the knight gives her his time, not an object.)

## Narration (~85 words, 0.3 s between lines)
| # | line | picture |
|---|---|---|
| 1 | Why do heroes smash every pot? | frame 0: CLOSE on a clay pot at the cottage door as a sword shatters it, shards + one gold coin fly toward the camera (moves at once, gold = the only accent); HUD top-left: "POTS: 14,600" |
| 2 | This woman sets out a new one every morning. For forty years. | wide: the old woman carries a fresh pot to a shelf, counter ticks, light changes (day/dusk) |
| 3 | She hides a coin in each one. | close on her hands pressing a coin into the clay before the lid |
| 4 | Nobody has ever said thank you. | three heroes in three quick beats: swing, smash, grab the coin, leave (cape colours only); she sweeps the shards each time |
| 5 | Her son left to be a hero, and never wrote. | warm-grey flash: a small box boy at the door with a wooden sword, then an empty doorway; the counter freezes |
| 6 | So every hero leaves her house with a coin. Maybe someone is doing the same for him. | slow close on her face, one tear-free dry look; a hero's back disappearing down the lane with the coin glint |
| 7 | One knight walked in, and didn't swing. | the knight at the door, sword down, looking at the pot |
| 8 | He found the coin, put it back, and sat down. | gauntlet lifts the lid, sees the coin, closes the lid; he pulls up a stool at her table |
| 9 | She made him tea. | she sets two cups; steam; she sits across from him; HUD swaps to "POTS SMASHED TODAY: 0" (the only UI, it replaces the old one) |
| 10 | That pot is still on the shelf. The only one she never had to replace. | the pot, unbroken, glowing slightly gold in the window light; last frame composed like frame 0 but whole; end on the last word |

## Assets
- Reuse: knight(), motion helpers, HUD code, `tools/render_parts.py`, the clay-pot and coin from the existing sets if present (loot_restocker / last10), the woman model
  of npc_well.py is NOT reused (a new old woman: bun of grey hair, apron, shawl; a recoloured old-man body is acceptable if time is short).
- NEW: clay pots (box + lid, 4-5 on a shelf), cottage doorway + table + two cups (boxes), a few shards (small quads that scatter), a small boy (flashback only, a smaller box human).
- One accent colour: gold (the coin, the glow on the last pot). Interior otherwise dark warm brown, one window as the main light.

## Camera (4 setups, hard cuts 2.5-4 s)
A close on the pot/door (frame 0) -> B wide cottage (counter, heroes passing) -> C the old woman close (hands, then face, creeping) ->
D two-shot at the table (knight + woman, tea) -> end on the shelf, frame-0 composition.

## Sound
Morning birds, soft clay "tock" when the pot is set down, shatter (short noise burst, filtered, no per-sample gate), coin clink, soft footsteps, one kettle, steam hiss, the cup set down;
flashback: room goes quiet, a wooden-sword tap; last line: a low two-note pad. Never a per-sample random gate.

## No-stop rule
Never wait for Enes. All QA (script_lint, scene_qa, critique >= 8, check.py). Render to renders\pots\. Captions: captions/pots.md.
