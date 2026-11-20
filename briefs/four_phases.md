# WHY DO FINAL BOSSES HAVE THREE PHASES? - brief (20 Nov 2026, Claude)
Format: same family as the best video so far (Final Boss A: 3.0 K views, 64 % stayed - ANALYTICS.md section 12): a question every
gamer already has + a lore twist, PS1 look, nightkit engine. YouTube/Instagram ~32 s; TikTok cut ~15 s afterwards.

## Why this story (not just a joke)
One character wants something: the old goblin at the bottom has held the "final boss" up for thirty years and is tired.
The knight sees it and chooses to help instead of winning. The twist echoes Final Boss A (the hero becomes part of the boss),
which is the payoff that already worked with this audience.

## Narration (one narrator; ~81 words, target ~25 s of speech)
| # | line | picture (cue lands 0-3 frames before the key word) |
|---|---|---|
| 1 | Why do final bosses always have three phases? | frame 0: huge cloaked boss (3.6 m) towering over the knight, red eyes under a crown, boss bar split in 3 |
| 2 | The knight lands the final blow. Phase one... down. | sword hit, kick-shake, bar segment 1 empties, boss sinks to its knees |
| 3 | Phase two. The boss is somehow shorter. | boss stands up again, a third shorter (cloak now ~2.4 m), wobbles; "PHASE 2" banner |
| 4 | Phase three. Even shorter. | another hit, now ~1.2 m tall, the cloak drags on the floor; "PHASE 3" |
| 5 | Then the cloak slips. | the cloak slides off (one rigid fall) |
| 6 | It was never one monster. It was three goblins, stacked. | reveal: two goblins lie panting, the smallest (crown, giant sword) stands trembling |
| 7 | The one at the bottom had been holding the others for thirty years. | close on the old goblin (grey beard, bent back), HUD: "CARRY WEIGHT: 2 GOBLINS / 30 YEARS" |
| 8 | The knight lowers his sword. | knight lowers the sword, the kid goblin lowers his |
| 9 | And crawls under the cloak. | knight lifts the cloak, ducks under; the goblins climb on top of him |
| 10 | Now the final boss has four phases. | the cloaked boss rises TALLER than before (knight plume pokes out), bar now has 4 segments, "FINAL BOSS - PHASES: 4" |
| 11 | And the old goblin finally gets a day off. | the old goblin sits by the arena wall with a tiny cup, "DAY OFF" emote; end on the last word |

## Assets (reuse first)
- Knight: `examples/final_boss.py` knight() (locked). Arena: final_boss ARENA (boss room).
- Goblins: `examples/loot_restocker.py` goblin() x3 with scale + colour variants (old = grey beard box + darker skin, bent lean;
  middle = default; kid = small, crown, holds the boss's huge sword). No new character model, only parameters.
- NEW: the cloak (one dark tapered box stack, height = 1.2 m x number of members, crown + 2 emissive eyes on top), cup prop.
- HUD: boss bar with N segments, phase banners, carry-weight line, emotes. All 2D overlays.

## Camera (5 setups, cuts only on big changes)
A low angle wide (frame 0, boss huge) -> B side medium for the hits -> C close on the goblins after the reveal ->
D two-shot knight + kid (sword lowering) -> E wide: the new 4-phase boss rises, then the day-off goblin in the corner.
Every hold creeps (motion.creep), hits get motion.kick (7 frames).

## Sound
Hit clangs + kick-shake thuds, phase-change stinger (two-note), cloak whoosh, goblin pant (filtered noise), tiny cup clink,
a short heroic chord that turns comic on "day off". Ducked under the voice (audio.duck_envelope). No silent stretch > 1.2 s.

## Voice
Preferred: Chatterbox on the PC (Enes's own voice reference if recorded; exaggeration ~0.5, 0.7 on "Then the cloak slips.").
Fallback: Kokoro bm_george, speed 1.25 like `tools/tts/sk.py`. No word stress tricks (Enes: they change the voice too much).

## Order (PIPELINE.md, skill nightkit-short)
script_lint -> voice -> measured timings -> asset lock + previews (show Enes 4-6 frames) -> scene_qa -> draft -> critique -> check.py.
