# MECHANISM style - an optional extra look (22 Nov 2026). Does NOT replace the Insert Disc 2 PS1 look or its rules.
Use it per video when a topic has a mechanism to show. Lessons measured on two reference explainers (an engine cutaway in low-poly 3D,
a pixel-art fission chain reaction); their numbers vs ours: motion 2.7-4.0 vs 1.5-1.8, brightness 42-62 vs 32-36, contrast 32-50 vs 16-23.

1. One hero object, centred, 50-60 % of the frame, on a dark clean stage (gradient + soft spotlight); it reads at a glance.
2. The object itself is always moving (breathing, parts working, particles), not only the camera.
3. The animation IS the explanation: cutaway, time-lapse / slow-mo tag, counters that tick (numbers that grow keep people watching).
4. Light tells the story: glowing key parts + bloom; brightness ~50+, contrast ~35+.
5. One continuous camera move, no cuts (transform instead of cutting); the end loops into the start.
6. One boxed label at a time (top), one small tag (top-left), subtitles at the bottom; nothing else on screen.
7. No limb acting where an object can tell it (e.g. only a gauntlet, not a whole knight).
8. Voice: four_phases pace; no gap > ~0.5 s.

Tools: `python tools/qa/look_metrics.py <mp4>` (targets: motion >= 3, brightness >= 50, contrast >= 35).
Test videos: `examples/mech/mimic_mech.py` (v1, chest only) and `examples/mech/mimic_mech2.py` (v2, story: the camera pulls back to the heroes and the knight and pushes in on the chest; 26 s, loops). Placeholder Kokoro voice `tools/mech/voice_mimic.py`.
Result of the test (cloud, 22 Nov): motion 2.31, brightness 49.5, contrast 49.4 (ours before: 1.52 / 31.7 / 15.9).
v2 (22 Nov): motion 2.40, brightness 51.7, contrast 46.7.
