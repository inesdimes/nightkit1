# Continuation note — Insert Disc 2 (17 Nov 2026)

Paste this into a new chat. Repo: `inesdimes/nightkit1`, branch `ccr-f9cdf9b1-6cua2c` (all work is here, not on `main`).
Read first: `HANDOFF.md` (channel, rules, video table), `PIPELINE.md` (production + QA process), `ANALYTICS.md` (data, observations).

## Working agreement
- Posted videos are never re-edited or re-uploaded.
- New videos use the latest observations (ANALYTICS.md sections 9–10): big, close, moving character in frame 0; story starts within ~6 s; no silent stretches; a payoff at the end. Observations, not rules.
- One video per day on YouTube; check stats at 48 h.
- Rendered videos are NOT in the repo (`deliverables/`, `*.mp4` ignored); Enes keeps them on his PC.
- Save tokens: batch feedback into one message, approve a short plan before big changes, only re-check changed scenes.

## Setup in a new container (gitignored, so it is gone)
```bash
pip install scipy soundfile kokoro-onnx
mkdir -p tts && cd tts && for f in kokoro-v1.0.int8.onnx voices-v1.0.bin; do curl -sSL -o $f https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f; done; cd ..
python tools/tts/<fb|lr|gf|sz|ap>.py      # regenerate the voice lines a script needs
```
(For Final Boss B also run A's `PART=audio` first; same for Guard Forgets B.)

## Videos
| Video | Script | Status |
|---|---|---|
| Final Boss A (30.5 s) | examples/final_boss.py | rendered, not posted |
| Final Boss B (60.25 s) | examples/final_boss_b.py | **posted 16 Nov 21:21** (got ~0 views; 2nd post that evening) |
| Guard Forgets A (30.6 s) | examples/guard_forgets.py | **posted 16 Nov 20:30**: ~300 views, 15 % stayed (early reading) |
| Guard Forgets B (59.6 s) | examples/guard_forgets_b.py | rendered, not posted; open question: post as-is (clean A/B) or remake the first 3 s |
| Loot Restocker A (29.9 s) | examples/loot_restocker.py | rendered, not posted; the 60 s B was never made |
| Safe Zone v2 (52.3 s) | examples/safe_zone.py | rendered, not posted |
| One Apple v4 (30.6 s) | examples/one_apple.py | rendered, not posted; for **YouTube + Instagram** |
| One Apple 15 s cut (15.25 s) | examples/one_apple_15.py (imports v4 assets; voice `tools/tts/ap15.py`) | rendered, not posted; for **TikTok** |

Captions ready: `captions/final_boss.md`, `captions/guard_forgets.md`, `captions/one_apple.md`.

## Next steps
1. 48 h stats of the 16 Nov posts (YT stayed/swiped, retention graph) -> add to ANALYTICS.md.
2. Captions for Safe Zone, Loot Restocker.
3. Decide Guard Forgets B (see table).
4. New briefs as Enes sends them (follow PIPELINE.md; QA with `python tools/qa/scene_qa.py examples/<script>.py`).
