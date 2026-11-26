# WHAT IF YOU NEVER ATTACK THE FINAL BOSS? - brief (26 Nov 2026, Claude; Enes approved the idea)
Video 4 of 26 Nov (after Bridge Troll, Mimic Shop, 99 Times Revive). nightkit HD, ~36 s, 5 separate sequences (render_seq.py rule).

## ENDING CHANGED (Enes, 26 Nov): counter overflow instead of the crown hand-over
9,999 -> MAX -> 'Oh no... not again.' -> glitch -> reset to frame 0 -> 'Kneel before me, mortal!' -> whisper 'Hey... want some tea again?'.
The table below is the first plan; the built timeline + lines are in examples/never_attack.py and tools/tts/na.py.

## Core idea
Turn-based rule: the hero always moves first. The knight picks WAIT every turn, so the boss can never act.
Counter ladder (TURNS WAITED) + speed ramp + emotional turn (lonely boss) + double-meaning punchline "Your turn." + loop.

## HUD (always on)
- Top-left: `TURNS WAITED: n` (yellow digits, ticks with a soft click; speed tag x1 -> x10 -> x100 -> x1000 next to it)
- Bottom: battle menu ATTACK / MAGIC / ITEM / **WAIT** (cursor always lands on WAIT)
- Boss HP bar top: never moves (100 %)

## Beats (EN line | TR line | picture)
| # | t | EN | TR | picture |
|---|---|---|---|---|
| S1 | 0-2.5 | (title, spoken) What if you never attack the final boss? | Final boss'a hiç saldırmasan ne olur? | FRAME 0: boss face fills top 2/3, knight small bottom, title burned mid-frame, TURNS WAITED: 0, cursor jumps ATTACK -> WAIT |
| S1 | 2.5-6 | BOSS: Kneel, mortal! ... It's your turn. Attack! | Diz çök, ölümlü! ... Sıra sende. Saldır! | boss roars, rule popup "HERO MOVES FIRST"; WAIT. 1 -> 10 |
| S2 | 6-11 | BOSS: Any day now... I can't move until you do! | Hadi ama... Sen oynamadan ben kıpırdayamam! | x10: boss taps foot, ultimate orb fizzles; 10 -> 100 |
| S3 | 11-17 | BOSS: Fine. ...Tea? | Peki. ...Çay? | x100: boss sits on the stairs, two cups; 100 -> 500 |
| S3 | 17-23 | BOSS: Three hundred years. Nobody ever stayed this long. | Üç yüz yıl. Kimse bu kadar kalmadı. | x1000: candles melt, cobwebs, knight's beard grows grey, boss laughing; 500 -> 9,998 |
| -- | ~23.5 | CTA toast (cta.py) ACHIEVEMENT UNLOCKED / LIKE = +1 XP | BAŞARIM AÇILDI / BEĞEN = +1 XP | top of frame (length: ask Enes) |
| S4 | 23-30 | BOSS: Every hero hit me in the first second. You... listened. | Her kahraman ilk saniyede vurdu. Sen... dinledin. | x1: old frail boss stands, takes off crown, puts it on the knight. 9,999 |
| S4 | 30-32 | BOSS: Your turn. | Sıra sende. | crown lands; boss fades to dust smiling. Double meaning |
| S5 | 32-36 | (text) Would YOU wait 9,999 turns? | 9.999 tur bekler miydin? | LOOP: knight (now in boss armour) on throne, face fills frame like frame 0, door opens, new hero, counter resets TURNS WAITED: 0, new hero's cursor on ATTACK |

## Assets
Reuse: boss + arena + throne (examples/final_boss.py / skip_speech.py / boss_health_bar.py), knight (nightkit/hd.py), HP bar
(boss_health_bar.py), cta.py.
NEW: battle menu with cursor, TURNS WAITED counter + speed tag, teacups + teapot, candles (height animates), cobweb planes,
grey beard swap on the knight, crown hand-over, dust fade.
Clipping watch (Enes spots it): boss hand + cup, crown on the knight's helmet, seated boss vs stairs.

## Camera (one idea per sequence)
S1 close on boss face (frame 0 rule) -> S2 side two-shot -> S3 low wide, slow push-in during the time-lapse -> S4 close two-shot,
crown -> S5 frame-0 composition mirrored for the loop.

## Sound
Boss roar, menu click per WAIT, counter ticks speeding into a whir, tea pour, clock ticks under the time-lapse, music box at the
"three hundred years" line, silence before "Your turn.", door creak at the loop.

## Voice
EN: boss = Enes Chatterbox clone (approved 2b settings, tools/tts/enes.py), title line same voice; knight silent.
TR: Enes's own takes (own_prep --lines + build own), lines from the TR column. SUB_LANG=tr.

## Deliverables
renders/never_attack/: EN mp4 (1.2x post per format 3.0 rules if it stays <=40 s), EN + TR thumbnails, captions/never_attack.md
(EN + TR), TR line sheet briefs/never_attack_voice_sheet.md.
