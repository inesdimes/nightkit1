# WORKFLOW — GPT + Claude, one video at a time (Insert Disc 2)

Goal: better videos with less Claude usage. GPT does the cheap thinking (ideas, briefs, captions, analytics). Claude does only what needs code, rendering and QA.
Rule of thumb: **one video = one fresh Claude session.** A long chat drowns in old previews and gets worse. The repo files are the memory, not the chat.

## 1. Who does what
| Stage | Who | Output | Claude cost |
|---|---|---|---|
| 1. Idea list (10 ideas, filtered by what the engine can do) | GPT (use `CHANNEL_PROMPT.md`, job A) | 10 one-line ideas | none |
| 2. Pick one idea | Enes | 1 idea | none |
| 3. Production brief (storyboard, narration, timing) | GPT (job B) | brief | none |
| 4. Brief lint (see §3) | GPT, second pass | brief with MUST / NICE-TO-HAVE | none |
| 5. Plan + build + QA + render | **Claude, fresh session** | mp4 + contact sheet | the only expensive step |
| 6. Review (watch the mp4, list fixes in ONE message) | Enes | one numbered list | none |
| 7. Fixes | Claude, same session, only changed shots | new mp4 | small |
| 8. Captions, titles, hashtags, pinned comment | GPT (job C) | `captions/<video>.md` | none |
| 9. Post, 48 h later read the numbers | Enes -> GPT (job D) | notes for `ANALYTICS.md` | none |

## 2. Opening a fresh Claude session (copy this)
> Repo `inesdimes/nightkit1`, branch `ccr-f9cdf9b1-6cua2c`. Read `CONTINUE.md` and `PIPELINE.md` only. Task: build the video in the brief below. Reuse existing assets, do not rebuild anything unchanged. Show a short plan first, wait for my OK, then build.
> [paste the brief]

Why it works: the new session reads ~3 small files instead of 600 messages of history.

## 3. What a brief must look like (GPT checks this before it reaches Claude)
- One idea, one location, 1-3 characters made of boxes. No realistic human faces, no screen-in-a-screen, no cloth/water/crowds.
- No contradictions (e.g. "A in the foreground" AND "A in the upper third"). If two rules clash, GPT removes one.
- Every requirement is tagged MUST or NICE-TO-HAVE. Claude builds MUST first.
- Exact seconds for each shot, exact narration text, and which characters from the asset list are reused.
- Max 4 camera setups for a 15 s video, 6 for 30 s.
- Cheapest videos: reuse a locked asset (knight, skeleton, goblin, cat, duckling + dog, archer). Expensive: any new character or room.

## 4. Claude usage budget (so the week does not run out)
- Previews: only the shots that changed, 3-4 frames each, never the whole video again.
- Full render: once, after QA is clean. Never re-render 60 s to fix one shot (use `PART=a:b`).
- Feedback: one message with a numbered list, not ten small messages.
- Do not ask Claude to write captions, analyse numbers or brainstorm: that is GPT's job.
- If a video is dropped, write one line in `CONTINUE.md` and move on. Do not "fix it a bit more".
- Start a new session when: the chat is long, previews look wrong for no reason, or you switch to a new video.

## 5. What to paste to GPT, per job
- Always: the text of `CHANNEL_PROMPT.md` once at the start of a GPT chat.
- Job B: add "Idea: ... Duration: ... Reuse these assets: ..."
- Job D: paste numbers or screenshots plus the video's name; ask for 3 observations and 1 thing to test on the next video.
- Ask GPT to answer in the repo's format so you can paste into `captions/` and `ANALYTICS.md`.

## 6. Weekly rhythm (about 5 videos)
- Mon: GPT, 10 ideas for the week, pick 5, write 5 briefs.
- Tue-Fri: one fresh Claude session per video, in order of cheapness (reused assets first).
- Daily: post one video (TR 19:00-21:00), save the 48 h numbers.
- Sun: GPT reads the week's numbers; decide next week's themes.

## 7. Quality checklist before a video is called done (Enes, 2 minutes)
1. Frame 0 shows a big, close, moving character (hook).
2. The story is clear with the sound off.
3. No limb/arrow/prop passes through another thing.
4. Subtitles are exactly the narration and never cover a face.
5. The ending is a clear payoff (a joke or an emotion), not a fade-out.
If 3 or more fail: drop the video, do not patch it.
