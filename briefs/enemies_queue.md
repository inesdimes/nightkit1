# WHY DO ENEMIES ATTACK ONE AT A TIME? - brief (21 Nov 2026, Claude) - 14-day test, day 1, 02:00 slot (~30 s)
Format and rules: briefs/SERIES_14_DAYS.md. PS1, nightkit, Enes-timbre voice.

## Narration (~65 words)
| # | line | picture (cue 0-3 frames before the key word) |
|---|---|---|
| 1 | Why do enemies always attack one at a time? | frame 0: CLOSE on a small goblin holding a paper ticket "47", a queue of goblins behind him, the knight fighting one at the front |
| 2 | Because they take a number. | a ticket machine on the wall + a sign "NOW SERVING: 45" (2D overlay on the sign, readable) |
| 3 | Goblin forty-seven has been waiting for three hours. | #47 checks his ticket, sighs; HUD "WAIT: 3:02:11" |
| 4 | Forty-five got hit. Forty-six got hit. | two quick hits at the front, the sign ticks to 46, then 47 |
| 5 | Forty-seven stepped up... and the hero saved and quit. | #47 steps forward, raises his club; HUD pause menu "SAVE & QUIT" selected; the knight freezes and vanishes |
| 6 | The dungeon went dark. Forty-seven kept waiting. | lights out, only torches; #47 alone at the front, still holding the ticket; HUD "PAUSED" |
| 7 | The next morning, the hero came back. Just for him. | light returns, "CONTINUE"; the knight appears, looks at #47, nods |
| 8 | Forty-seven lost in one hit. | one hit, #47 falls back, smiling |
| 9 | He framed the ticket. | the ticket "47" in a little frame on the wall next to the ticket machine; end on the last word |

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
