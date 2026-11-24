# What if the boss's health bar was the village's? — voice cue sheet

Record ONE file per line, in this order: `vocal/Boss Health Bar/Kayit (1).m4a` … `Kayit (7).m4a`.
Woman lines (2, 4, 6) can be Betül's (`vocal/Boss Health Bar/Betül/<n>. cümle.m4a`, see the Betül recipe).

The film is built at 1x (36.0 s) and sped up 1.2x at the end -> 30.0 s. Read at your normal pace:
"max length" is the recorded length (1x) that still fits before the next beat.

| # | Speaker | Line (exact, = subtitle) | Final video (s) | Build 1x start (s) | Max length at 1x | Direction |
|---|---|---|---|---|---|---|
| 1 | Narrator | What if every hit on the boss hurt the village instead? | 0.20 – 2.70 | 0.24 | 3.3 s | calm but urgent, over the sword impact |
| 2 | Old woman | Stop! Every wound reaches us! | 3.25 – 5.04 | 3.90 | 3.1 s | frightened, urgent; short gap after "Stop!" |
| 3 | Knight | It attacked first! | 6.50 – 7.54 | 7.80 | 2.8 s | defensive, arm drawn back |
| 4 | Old woman | It's holding the curse back. | 9.40 – 10.86 | 11.28 | 2.9 s | strained but certain |
| 5 | Knight | Then what do I strike? | 15.25 – 16.46 | 18.30 | 1.7 s | sword lowered, pointing at the seal |
| 6 | Old woman | The king's seal! | 16.85 – 17.73 | 20.22 | 1.3 s | shouting over the rumble |
| 7 | Guardian | The king is next. | 27.35 – 28.68 | 32.82 | 2.8 s | deep, controlled (the mix adds a stone-hall echo) |

Times are planned (tools/tts/bhb.py PLAN). With real takes the film keeps every cut; a line only moves if the line before it runs long.

## Sound / music cue sheet (final video seconds)
| t | Cue |
|---|---|
| 0.00 | heavy metal impact + stone groan, chain links snap, a village bell cut short; HUD 10/10 -> 9/10 (low drop blip) |
| 0.8 | curse pulse (low magical pulse) runs down the chain |
| 3.0 – 5.5 | village: wind, distant rumble; 3.4 her neighbour's window dies (pfft + HUD 8/10) |
| 5.5 – 8.5 | the dark wave (rising whoosh), the lantern flame sputters, pulse |
| 8.1 / 10.2 | pulses synced to the current along the chain; 11.2 her door lantern dies (HUD 7/10) |
| 10.1 – 12.5 | chain creaks along the track; 12.0 low brass sting on the crown; 14.3 window dies (HUD 6/10) |
| 19.0 | sharp metal crack, then ~0.7 s near-silence; chain links rattle onto stone |
| 21.0 – 23.0 | reverse magical rush (swells, cuts), bell rings again at 21.5 and 22.9; rising chime per light (21.6, 22.2, 22.8, 23.4) |
| 24.2 – 26.5 | chain pull, heavy stone movement, links falling, two heavy footsteps |
| 27.0 | QUEST UPDATED jingle (4-note arpeggio) |
| 28.6 – 30.0 | low heroic note, sword ring as the knight turns to the castle; hard cut at 30.0 |

Music: a low dread drone until the seal breaks (19.0), a warm major pad from the reverse current (21.0) to the end.
Stems (separate tracks): `bhb_dialogue.wav`, `bhb_music.wav`, `bhb_fx_ambience.wav` (in `renders/boss_health_bar/stems/`).

## After recording
```
python tools/tts/own_prep.py bhb "vocal/Boss Health Bar" --lines
python tools/tts/bhb.py build own
python tools/render_parts.py examples/boss_health_bar.py --prefix bhb --audio boss_health_bar.wav --out ../renders/boss_health_bar/bhb_1x.mp4 --parts 8
sh tools/speedup.sh ../renders/boss_health_bar/bhb_1x.mp4 ../renders/boss_health_bar/what_if_the_boss_health_bar_was_the_villages_30s.mp4
```
