# WHY DO FINAL BOSSES GIVE A SPEECH BEFORE THE FIGHT? - brief (21 Nov 2026, Claude) - 14-day test, day 1
Format and rules: briefs/SERIES_14_DAYS.md. ~32 s, PS1, nightkit. Post at 22:00 TR (the longer slot; as long as the story needs).

## Narration (~95 words)
| # | line | picture (cue 0-3 frames before the key word) |
|---|---|---|
| 1 | Why do final bosses always give a speech before the fight? | frame 0: CLOSE on the boss on his throne mid-gesture, one arm raised, "PRESS X TO SKIP" blinking at the bottom of the HUD |
| 2 | This one wrote his speech thirty years ago. | boss with a long scroll unrolling to the floor |
| 3 | He rehearsed it every night. Pauses. Hand gestures. A dramatic cape flip. | empty arena at night, boss alone: raises arm, pauses, flips cape; HUD "REHEARSAL #10,950" |
| 4 | Then the first hero arrived, and pressed skip. | a knight walks in, "X" pressed (HUD button flash), speech cut, scroll drops, quick fight flash, "VICTORY" |
| 5 | So did the next one. And the next. | fast repeats; HUD counter "SKIPPED: 1,248" |
| 6 | Until one knight walked in... and didn't press anything. | a new knight stands still; the "PRESS X TO SKIP" prompt blinks... and fades out |
| 7 | The boss froze. Nobody had ever heard his second sentence. | boss close: eyes flicker, scroll trembling |
| 8 | He spoke for eleven minutes. | time-lapse: candles burn down, the knight sits cross-legged, boss gestures wildly; HUD timer 00:00 -> 11:02 |
| 9 | When it ended, the knight clapped. | knight stands and claps; boss bows deeply |
| 10 | Then the fight began. He was too happy to dodge. | one sword hit, boss falls backwards, smiling eyes, "VICTORY" |
| 11 | He lost in one hit. Best day of his life. | boss on the floor, a tiny "+1 FAN" emote above him; end on the last word |

## Assets
Reuse: boss() and knight() from examples/final_boss.py (locked), the arena. NEW: throne (box stack), scroll (long thin quad),
candles (small boxes + emissive flame that shrink in the time-lapse). HUD: PRESS X TO SKIP, REHEARSAL / SKIPPED counters, timer, +1 FAN.

## Camera (5 setups)
A close on the boss (frame 0, big, moving) -> B wide arena (rehearsal at night) -> C entrance (heroes skipping, repeats) ->
D two-shot knight + boss (the one who listens, time-lapse) -> E low angle: the hit and the happy fall.

## Sound
Boss voice is NOT spoken (only the narrator); during the speech: a muffled low "mwah-mwah" murmur (filtered noise bursts) +
candle crackle; skip = a sharp UI click and a cut-off; clapping; one sword clang; a small victory jingle. Ducked under the narrator.

## Voice + no-stop rule
Same as four_phases: Kokoro bm_george -> ChatterboxVC to voice/enes_ref_main.wav. Never wait for Enes; run all QA; final render to
C:\Users\USER\Documents\blender-shorts\renders\skip_speech\. Captions: captions/skip_speech.md.
