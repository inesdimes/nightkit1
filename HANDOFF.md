# HANDOFF — Insert Disc 2 (ex VIDIVENIGAMING)

Paste this file (or the repo link) at the start of a new chat so Claude can continue.

## Channel
- Name: **Insert Disc 2** — handle **@pleaseinsertdisc2** (TikTok done; claim the same on YouTube + Instagram)
- Format: original 55–65 s PS1-style shorts, 9:16 1080x1920, English voice + subtitles
- Bios: YouTube "💿 PLEASE INSERT DISC 2 — Tiny stories from retro games that never existed…", TikTok "Tiny retro game stories 💿 New disc every day", IG 3 lines (💿 / 👾 / 📼)
- Posting plan: YouTube 1/day ~19:00–21:00 TR, TikTok 1–2/day, Reels 1/day
- Branding: `branding/` (A_disc_profile = profile pic, banner_2560x1440, B/C alt concepts)

## Videos (scripts in `examples/`)
| Video | Script | Status |
|---|---|---|
| The Last Save Point (horror, 60 s) | last_save.py (`VOICE=enes` = Enes's own recordings) | posted YT, ~170 views/3 h |
| He Picked The Wrong NPC (60 s) | wrong_npc.py | posted YT 15 Nov ~22:08, stuck at 0 views; wait, then re-cut with a "SIDE QUEST ACTIVATED" opening |
| How Big Was It? (T-Rex game show) | gameshow.py | v3 ready (face 3/4 cams, legendary banana) |
| The Chest That Scammed Me | chest_scam.py | ready |
| The T-Rex Size Mystery | trex_size.py | dropped by Enes |
| Final Boss — Experiment A (30.5 s) | final_boss.py | rendered: deliverables/final_boss_A.mp4 |
| Final Boss — Experiment B (60.25 s, same story, slower mystery) | final_boss_b.py (imports A; 0–4 s + last 3.9 s are A's frames/audio) | rendered: deliverables/final_boss_B.mp4 |
| The Rat King, AUTO-TRACK (face_track.py), earlier GTA/streamer remakes | see examples | done |

## Analytics
- See `ANALYTICS.md` (16 Nov 2026): data, diagnosis, editing checklist, A/B plan for NEW videos (no re-cuts of posted ones), lessons, review rhythm.

## Pipeline
- Renderer: `nightkit` + **`nightkit/zraster.py` (z-buffer, use this — fixes "seeing inside models")**. Draw face decals as separate layers with `bias=1.004`; tag decals with `q['hc']` (head centre) and cull when `|c-cam| >= |hc-cam|`.
- Internal 180x320, upscale x6, 24 fps. `TEST=1.0,5.0 python examples/X.py` → test.png; `PART=a:b` renders frames to `out/<prefix>_a.mp4`; `PART=audio` builds the wav; concat + mux with `-af loudnorm=I=-14:TP=-1.5`.
- Run two PARTs in parallel (2 cores), ~8 min per 60 s video.
- Font: 5x7 `nightkit.font` — check text widths so panels don't overflow; add missing glyphs (`? ! + %`) to `font.FONT`.
- Cameras on side-eyed animals (T-Rex, birds): use 3/4 views, not straight-on.

## Voices
- All scripts read voices/models from `TTS_DIR` (env var; default `<repo>/tts/`, gitignored). Kokoro TTS offline: `kokoro-v1.0.int8.onnx` + `voices-v1.0.bin` from the kokoro-onnx GitHub releases (Hugging Face is blocked); `pip install kokoro-onnx`.
- Voices used: narrator am_michael, female af_heart/af_bella, am_puck, am_fenrir (T-Rex, pitched 0.78 + drive), bm_george (gator), af_sky (duck), am_onyx (skeleton). Line schedules: `tools/tts/scripts/*.json`; generators `tools/tts/n*.py`.
- Enes's own voice FX chain (pitch down, sub-octave, slapback, reverb, crystal comb filter): `tools/voice_fx/`.

## Enes's rules
English subtitles exactly as spoken, keywords highlighted; hook in first 1–2 s; no clickbait; no real logos/brands/game assets; anonymise real people; deliver video + TikTok/Reels captions + Shorts title + hashtags + source timestamps + edit summary.
