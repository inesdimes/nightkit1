# What if the boss's health bar was the village's? — voice cue sheet (v4 story, 19.6 s)

Story (v4, GPT brief 24 Nov): the king chained the guardian and enchanted the seal. Every wound to the guardian is sent to the village,
and the king siphons the villagers' life through the chain to stay immortal. The knight breaks the seal: the life goes back, the
village is saved, the king becomes mortal. Ends on QUEST COMPLETE — VILLAGE SAVED.

Record ONE file per line, in this order: `vocal/Boss Health Bar/Kayit (1).m4a` … `Kayit (5).m4a` (5 files).
Woman lines (Kayit 2 and 4) can be Betül's.

The film is built at 1x (23.6 s) and sped up 1.2x at the end -> 19.6 s. Read at your normal pace:
"max length" is the recorded length (1x) that still fits before the next beat.

| # | Speaker | Line (exact, = subtitle) | Final video (s) | Build 1x start (s) | Max length at 1x | Direction |
|---|---|---|---|---|---|---|
| 1 | Narrator | What if every hit on the guardian killed a villager? | 0.40 – 2.57 | 0.48 | 3.0 s | calm but urgent, right after the sword lands |
| 2 | Old woman | The king's seal sends every wound to us! | 3.10 – 4.93 | 3.72 | 3.0 s | frightened, accusing; she's on camera from 4.7 |
| 3 | Knight | Why? | 6.55 – 7.01 | 7.86 | 0.8 s | quiet, stunned, looking up at the castle |
| 4 | Old woman | To keep him immortal. | 9.55 – 10.72 | 11.46 | 1.7 s | bitter, plays over the king on his wall |
| 5 | Guardian | Now the king can bleed again. | 16.90 – 18.48 | 20.28 | 2.2 s | deep, slow, satisfied (the mix adds a stone-hall echo) |

QUEST COMPLETE / VILLAGE SAVED appears right after line 5 and the video ends ~1 s later, so a longer take 5 makes the video longer.

## Picture / sound beats (final video seconds)
| t | Beat | Sound |
|---|---|---|
| 0.00 | the sword is already coming down, HUD VILLAGE 10/10 | swing whoosh |
| 0.30 | HIT on the chained guardian | metal impact, chain snap |
| 0.38 | cut to a village house: its window goes dark, HUD 10/10 -> 9/10 | pfft, HUD drop blip, village bell cut short |
| 0.96 | back at the fight: the guardian recoils | stone groan |
| 3.00 | a purple wound-pulse runs from the guardian's chest along the chain into the king's seal (a padlock with the crown) | low magical pulse, chain creak |
| 4.70 | the old woman at her door; 5.1 her lantern dies (HUD 8/10) | pfft, HUD drop |
| 6.00 | the knight's face: looks down the chain, then up: "Why?" | |
| 7.05 | what he sees: the king's castle on its hill | |
| 7.90 | the village: gold life-motes rise from every window and run along the chain towards the ruin | thin shimmering drone starts |
| 9.40 | the king on his castle wall: the gold stream flows into his crown, a gold halo over his head | low brass sting |
| 11.00 | the knight turns from the guardian to the seal; 11.9 close-up, 12.2 the strike: the lock splits, the chains drop | sharp metal crack, ~0.7 s near-silence, links on stone |
| 12.95 | the gold stream reverses: out of the sky, past the broken seal, back down the chain | reverse rush |
| 13.55 | the dark window lights up again, HUD 8 -> 9 -> 10/10 | bell rings again, rising chimes |
| 14.40 | the king: the halo shatters (14.6), the crown falls (14.85), he drops to one knee (15.05); the gold leaves him | glassy shatter, crown clank, a heavy knee thud |
| 16.40 | the freed guardian stands beside the knight; 16.9 "Now the king can bleed again." | stone movement |
| 18.53 | QUEST COMPLETE / VILLAGE SAVED; end 19.6 | quest-complete jingle |

Stems (separate tracks): `bhb_dialogue.wav`, `bhb_music.wav`, `bhb_fx_ambience.wav` (`out/bhb_stems/`, copied to `renders/boss_health_bar/stems/`).

## After recording
```
python tools/tts/own_prep.py bhb "vocal/Boss Health Bar" --lines
python tools/tts/bhb.py build own
python tools/render_parts.py examples/boss_health_bar.py --prefix bhb --audio boss_health_bar.wav --out ../renders/boss_health_bar/bhb_v4_1x.mp4 --parts 8
sh tools/speedup_raw.sh out/bhb_video.mp4 out/boss_health_bar.wav <out.mp4> <DUR / 1.2>
```
(not speedup.sh: its loudnorm clips the hit at 0.3 s). A longer take makes DUR grow; `TEST=0 python examples/boss_health_bar.py` prints it.
