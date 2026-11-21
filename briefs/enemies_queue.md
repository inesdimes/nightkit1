# WHY DO ENEMIES ATTACK ONE AT A TIME? - brief (21 Nov 2026, Claude) - 14-day test, day 1, 02:00 slot (~30 s)
Format and rules: briefs/SERIES_14_DAYS.md. PS1, nightkit, Enes-timbre voice.

## Narration v3 - NEW STORY (21 Nov 2026, Enes: "give it a new story, answer the same question differently") - 11 lines, ~33 s
Answer: the goblins have a rule, carved after the first hero. Voice: tools/tts/eq2.py. Script: examples/enemies_queue.py.
| # | line | picture |
|---|---|---|
| 1 | Why don't enemies ever attack all at once? | centred title card; knight hits the front goblin |
| 2 | Because of a rule. | the wall board: RULE 1 / ONE AT A TIME |
| 3 | It was written after the first hero came. | FLASHBACK (blue-grey): a small red-caped rookie walks into the hall |
| 4 | Nine goblins rushed him at once. | nine goblins rush him, dogpile, red flash, he flickers out |
| 5 | He never came back. | the ring of goblins where he stood, heads down |
| 6 | The goblins stood in the dark for a long time. | lights out, only torches |
| 7 | Then the oldest one carved a rule... one at a time. | a grey elder goblin with a hat chisels the board, letters appear one by one |
| 8 | So the next hero lived. And the next. | present: the knight hits goblin 45, then 46 |
| 9 | Every goblin in this line knows he will lose. | faces in the queue, #47 gulps |
| 10 | He steps up anyway. So you can reach level two. | #47 steps up, club up, one hit, LEVEL 2 pops |
| 11 | It was never a fight. It was a welcome. | the whole queue waves at the knight |

## Assets
Reuse: goblin() (examples/loot_restocker.py, colour/scale variants), knight(), the hall (examples/last10_collapse.py) or the arena.
NEW: ticket machine (box + red light), "NOW SERVING" sign (box with a 2D number overlay), ticket (small white quad), frame (box).
HUD: WAIT timer, pause menu (SAVE & QUIT / CONTINUE), PAUSED.

## Camera (4 setups)
A close on #47 (frame 0) -> B side wide of the queue + sign -> C #47 alone in the dark -> D the hit and the framed ticket.

## Sound
Queue murmur, ticket-machine "ding" on each number, two hits, pause-menu click + everything muted (only torches), continue chime,
one hit, a tiny proud trumpet note at the frame. Ducked under the narrator.

## Voice + no-stop rule
Same as four_phases. Never wait for Enes; run all QA; render to C:\Users\USER\Documents\blender-shorts\renders\enemies_queue\.
Captions: captions/enemies_queue.md.
