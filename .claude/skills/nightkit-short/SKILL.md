---
name: nightkit-short
description: Production order for a new Insert Disc 2 short (or a revision) in this repo. Use when Enes sends a brief or asks to fix / shorten / re-render a video.
---
# Making a short (nightkit)

Read `CONTINUE.md` and `PIPELINE.md` first. Reuse existing models, sets and tools; never rewrite what did not change.
Stop at every gate marked STOP, show the result in a few lines and wait for Enes.

0. **Script lint** - `python tools/qa/script_lint.py <narration>`; read the hints (pace, hook, pivot, last line).
1. **Plan** - a short feasibility plan: what is reused, what is new (models, set), cameras, timing, audio. STOP.
2. **Asset lock** - one function per character / prop / set (PIPELINE phase 1). Preview them yourself with
   `TEST=t1,t2 python examples/<script>.py` (writes test.png).
3. **Manifest + QA** - `QA = dict(...)` at the end of the script; `python tools/qa/scene_qa.py examples/<script>.py`.
   Fix only failing scenes (`--scenes id1,id2`). Look at the sheets yourself; show Enes only changed scenes, few frames.
4. **Draft render** - `PART=a:b` in parallel + `PART=audio`, concat, mux with `loudnorm=I=-14:TP=-1.5`.
5. **Critique** - `python tools/qa/critique.py <draft.mp4> --name <script> --round N`, look at the sheet, fill the
   scores in `reviews/<script>.md`. Fix the top 3, re-render, next round. All scores >= 8, at most 3 rounds. STOP.
6. **Final check** - `python tools/qa/check.py <final.mp4> --script examples/<script>.py` must pass; read its frame-scan WARN lines (black, frozen, pops) by eye.
7. **Deliver** - send the MP4 (videos are not committed). ALWAYS (Enes, 25 Nov 2026), unasked, after every render: EN + TR thumbnails
   (`python tools/thumb.py frame <script> <t_build> <out> "TEXT|y|R,G,B|scale" ...`; avoid İ Ş Ç Ğ Ö Ü in thumbnail text, they shrink in the
   pixel font) and `captions/<name>.md` (YouTube title + description, TikTok, Instagram, hashtags, pinned comment; English channel + İkinci Diski Takınız; hashtags: 3-5 only = brand #pleaseinsertdisc2 / #ikincidiskitakiniz first, 2 niche (#ps1 #retrogaming / #retrooyun), 1-2 topic; no generic #shorts #funny #memes), commit the script + tools + review log, update the video
   table in `CONTINUE.md`. If a shared model changed: `python tools/qa/regress.py compare`, report what changed.

Rules: rendering is procedural only (no AI video or image generation); UI and subtitles are 2D overlays; subtitles
match the spoken words; Claude cannot listen, so sound is described by measurement and judged by Enes.
