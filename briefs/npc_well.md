# WHY DO NPCs REPEAT THE SAME LINE? - brief (21 Nov 2026, Claude) - day 2, 22:00 slot (~55 s), Tone 2.0
Rules: briefs/SERIES_14_DAYS.md (read "Tone 2.0" first). PS1, nightkit, Enes-timbre voice (Kokoro bm_george -> ChatterboxVC), calm and slow.

## Story
An old villager stands at a dry well and says the same line to every hero: "The well is dry, traveler." Forty years.
Nobody asks why. The line is not dialogue: forty years ago his wife's ring fell down the well and she went down after it and
did not come up. Since then he says the well is dry, so no one else climbs down. One knight stops, looks at the rope, and climbs.
He comes back up with the ring. The old man says something new for the first time, and walks away from the well.

## Narration (~105 words; 0.4-0.7 s between sentences)
| # | line | picture |
|---|---|---|
| 1 | Why do NPCs always repeat the same line? | frame 0: CLOSE on the old man's face at dusk, fog, lantern light; a dialogue box: "THE WELL IS DRY, TRAVELER." |
| 2 | This one has said it for forty years. | slow pull back: he stands next to a stone well; a hero walks past him without stopping |
| 3 | To every hero. Every day. "The well is dry." | three heroes pass in three short beats (same dialogue box each time), seasons change: leaves, snow, rain |
| 4 | Nobody ever asked him why. | the old man alone, the empty village behind him, one lit window |
| 5 | Forty years ago, his wife dropped her ring down this well. | warm flashback colour: a woman leans over the well, a small gold glint falls |
| 6 | She went down to find it. She never came back up. | the rope swings in the empty well; flashback fades to grey |
| 7 | So he stands here, and tells everyone it's dry. | back to now: his hand on the stone rim, the same line in the dialogue box |
| 8 | So nobody else goes down. | close on the rope, frayed, tied to the well's post |
| 9 | Then one knight stopped. | a knight halts, looks at the old man, then at the rope |
| 10 | He didn't talk. He climbed. | the knight climbs down into the dark; only the lantern circle at the top |
| 11 | When he came back up, he held out a ring. | the knight climbs out, opens his gauntlet: a small gold ring in the lantern light |
| 12 | For the first time in forty years, the old man said something new. | the dialogue box opens: "...THANK YOU." |
| 13 | He never said that line again. The village was quieter. So was he. | the old man walks away from the well for the first time, ring in his closed hand; the knight stays by the well; end on the last word |

## Assets
- Reuse: knight() (examples/final_boss.py), motion helpers, HUD/subtitle code from the recent shorts, render driver tools/render_parts.py.
- NEW: old villager (box human: bent back, grey beard, long coat, cane), the woman (flashback only, silhouette-like, warm tint),
  stone well (cylinder of boxes) + post + rope (segments) + bucket, small village at dusk (2-3 house fronts, one lit window, fog),
  ring (tiny gold box with emissive glint), lantern on a post (one main light source).
- Dialogue box: classic RPG box at the bottom-third (above the subtitles), white border, the NPC's line in capitals.

## Camera (5 setups, long creeping holds)
A close on the old man (frame 0) -> B wide well + village (heroes passing, seasons) -> C flashback (warm, soft) ->
D the knight at the rope (two-shot, then the dark well from above) -> E the old man walking away, knight by the well.

## Sound
Dusk wind, distant crickets, a slow creak of the rope, soft footsteps of the passing heroes, a dull "blip" for the dialogue box;
flashback: warmer air, a small metallic "tink" when the ring falls; climbing: rope creak, stone scrape, echo from the well;
the ring: one soft chime. No music except a low two-note pad under the last line. Never a per-sample random gate.

## No-stop rule
Never wait for Enes. All QA (script_lint, scene_qa, critique >= 8, check.py). Render to renders\npc_well\. Captions: captions/npc_well.md.
