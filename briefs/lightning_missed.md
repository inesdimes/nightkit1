# THE LIGHTNING MISSED - locked decisions (18 Nov 2026)
Series: **What Happens Next?** (new series inside Insert Disc 2: a real-world science fact told through a retro-game logic joke;
it must not repeat the formats of the existing videos). Full GPT brief was pasted in chat; this file keeps only what Claude locked.

## Decisions
- Narration cut from 110 to **80 words**: Kokoro `bm_george` really delivers ~2.5-2.8 words/s, not 3.67. Speech = 28.7 s, so the
  main video is **~32.8 s** (not 30.0 s). TikTok 15 s cut: ~35-40 words, own TTS, not sped up.
- The shield is a NEW prop (knight() has none); crouch / stagger / inspect-shield are new poses on the same knight().
- Shots 4-6 share one camera for ~10 s: give them motion (pulsing cyan bands, `motion.creep`, maybe a glide) so critique does not flag a still stretch.
- HP bar visible from frame 0. HIGH / LOW labels are 2D overlays at 1080x1920, not 3D text.
- Hard cuts: 3 (CAM 01 -> 02 -> 03 -> 04), moved to the real line starts below.

## Locked voice (tools/tts/lm.py, speed 1.0; lines in tts/lm/*.wav, gitignored)
| key | start s | dur s | text |
|---|---|---|---|
| 1 | 0.25 | 3.87 | The lightning misses the knight, but his health bar drops by half. |
| 2 | 4.57 | 3.24 | His shield is untouched. The pillar took the hit. |
| 3 | 8.16 | 4.21 | He runs. Another bolt lands behind him. One HP left. |
| 4 | 12.87 | 2.86 | Wait. If it keeps missing, what is hurting him? |
| 5 | 16.23 | 4.72 | You see, lightning doesn't need a direct hit. Its current spreads through the ground. |
| 6 | 21.35 | 4.13 | Boots on two different voltages let current pass through his body. |
| 7 | 26.18 | 2.06 | He slams the guardhouse door. |
| 8 | 29.14 | 3.65 | His shield was useless. So he equipped the whole castle. |

Spoken end at 32.79 s. `python tools/qa/script_lint.py tools/tts/scripts/lm.json` -> pace 2.46 w/s (expected for this channel), no other hints.

## Next
Plan step 2: asset lock (courtyard + guardhouse facade, shield prop, new knight poses), then QA manifest and previews.
