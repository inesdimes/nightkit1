# What if the boss's health bar was the village's? — voice cue sheet (v3, 19.7 s)

Record ONE file per line, in this order: `vocal/Boss Health Bar/Kayit (1).m4a` … `Kayit (7).m4a`.
Woman lines (2, 4, 6) can be Betül's (`vocal/Boss Health Bar/Betül/<n>. cümle.m4a`, see the Betül recipe).

The film is built at 1x (23.7 s) and sped up 1.2x at the end -> 19.7 s. Read at your normal pace:
"max length" is the recorded length (1x) that still fits before the next cut. Line 1 was shortened (v2 feedback).

| # | Speaker | Line (exact, = subtitle) | Final video (s) | Build 1x start (s) | Max length at 1x | Direction |
|---|---|---|---|---|---|---|
| 1 | Narrator | What if every hit hurt the village? | 0.40 – 1.98 | 0.48 | 2.0 s | calm but urgent, right after the sword lands |
| 2 | Old woman | Stop! Every wound reaches us! | 2.45 – 4.24 | 2.94 | 2.2 s | frightened, urgent; short gap after "Stop!" |
| 3 | Knight | It attacked first! | 4.41 – 5.45 | 5.29 | 1.5 s | defensive, arm drawn back |
| 4 | Old woman | It's holding the curse back. | 5.85 – 7.31 | 7.02 | 1.8 s | strained but certain |
| 5 | Knight | Then what do I strike? | 9.10 – 10.31 | 10.92 | 1.5 s | sword lowered, pointing at the seal |
| 6 | Old woman | The king's seal! | 10.50 – 11.38 | 12.60 | 1.1 s | shouting over the rumble |
| 7 | Guardian | The king is next. | 17.05 – 18.38 | 20.46 | 1.8 s | deep, controlled (the mix adds a stone-hall echo) |

QUEST UPDATED / FIND THE KING appears right after line 7, then the knight turns to the castle and the video ends ~1.3 s later, so a longer take 7 makes the video longer.

## Picture / sound beats (final video seconds)
| t | Beat | Sound |
|---|---|---|
| 0.00 | sword already coming down (10/10) | swing whoosh |
| 0.30 | HIT: flash, HUD 10/10 -> 9/10, the 'village cam' inset (top left, under the HUD) shows the window going dark | metal impact, chain snap, village bell cut short, HUD drop blip |
| 2.20 | the old woman; 2.40 the window above her dies (HUD 8/10) | wind, distant rumble, pfft + drop blip |
| 4.30 | the guardian curls over its lantern; the dark wave hits its back; the knight draws back (line 4 plays over this shot) | dark whoosh, the flame sputters, pulse |
| 6.60 | short insert: her door lantern dies at 7.0 (HUD 7/10) | magical pulse synced to the wave |
| 7.40 | track: a curse pulse runs from the guardian's chest along the chain into the king's seal (an iron padlock with the crown, locking the chain) | pulse, chain creaks, brass sting on the crown |
| 9.00 | the knight lowers his sword and points it at the seal | |
| 10.40 | the woman shouts "The king's seal!" | rumble |
| 11.50 | the knight pivots; 11.9 close-up of the padlock; 12.20 the strike: crack, the lock splits, both chain ends drop | sharp metal crack, ~0.7 s near-silence, links on stone |
| 12.95 | the current reverses: back along the chain, past the broken seal, up to the king's castle | reverse magical rush |
| 13.55 | the village lights come back with green rings: 13.75, 14.05, her lantern 14.35 -> HUD 10/10 | bell rings again, rising chimes |
| 14.85 | the guardian rises (chain pull first), links fall, it looks down at the knight | heavy stone movement, links falling |
| 16.90 | "The king is next." -> 18.4 QUEST UPDATED / FIND THE KING -> 18.6 the knight turns to the castle, raises his sword; end 19.7 | quest jingle, whoosh, sword ring |

Stems (separate tracks): `bhb_dialogue.wav`, `bhb_music.wav`, `bhb_fx_ambience.wav` (in `renders/boss_health_bar/stems/`).

## After recording
```
python tools/tts/own_prep.py bhb "vocal/Boss Health Bar" --lines
python tools/tts/bhb.py build own
python tools/render_parts.py examples/boss_health_bar.py --prefix bhb --audio boss_health_bar.wav --out ../renders/boss_health_bar/bhb_v3_1x.mp4 --parts 8
```
then `sh tools/speedup_raw.sh out/bhb_video.mp4 out/boss_health_bar.wav <out.mp4> <DUR/1.2>` (not speedup.sh: its loudnorm clips the hit at 0.3 s).
