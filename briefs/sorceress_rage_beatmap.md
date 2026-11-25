# The First To Ever Ragebait — source beat map + timing notes (25 Nov 2026)

Source: `voice/snapgram.io_fv3w5zze9dpz.mp4` — 57.57 s, 30 fps, 576x650, AAC 44.1 kHz stereo, -14.1 LUFS, -1.8 dBTP.
On-screen text: "The first to ever ragebait" + 🤣🤣 for the whole clip (kept; pixel font + two pixel laughing faces, the font has no emoji).
Script: `examples/sorceress_rage.py`. Render: `renders/sorceress_rage/the_first_to_ever_ragebait_sorceress_58s.mp4` (30 fps, 1080x1920, 57.57 s).
Analysis: `voice/sorceress_src/mesh.json` (MediaPipe FaceMesh, 1726/1727 frames), `words.json` (Whisper small.en word times), `db.npy`.

## Two voices (measured: tracked mouth vs audio envelope)
| Time (s) | Voice | Words (Whisper, approximate) | In the adaptation |
|---|---|---|---|
| 0.00–5.95 | off-screen | mostly unintelligible ("Because…") | knight talks (mouth from the audio envelope), sorceress listens, unimpressed half-smirk |
| 5.95–28.62 | on-screen speaker | "Because you just said my name name. So you must really be mad mad, and for what? Why you mad mad for? You mad mad, you must really be mad mad if you call me my name name. Calling me Steven, no bae, no boo boo, no butter, my name name." | sorceress talks: mouth / eyes / brows / head from the tracked face, irritation layer builds |
| 28.62–33.85 | off-screen | quiet, mostly unintelligible ("Alright…") | knight talks + straightens his helmet; she rolls her eyes |
| 33.85–42.60 | on-screen speaker | "I didn't know you wanted me to do it do it. If you say yo just do it do it, I would have did it right then and there. I'm gonna just do it. I'm just not gonna do it, do it." | sorceress talks |
| 42.60–55.45 | off-screen (the rant, profane) | "Shut the f*** up, up! How about that? You like that? … Up, up! Shut the f*** up, up! F***ing dickhead dickhead! Stupid b**** b****! That's what you want?" | knight yells; she glares → fire → calm smirk |
| 55.45–57.35 | on-screen speaker | "…but you really mad, man." | sorceress, final line |

## Gags (snapped to measured beats)
- 10.67 s helmet trembles: first loud rise of her speech (-10.4 dB band peak, "you must really…").
- 13.30 s helmet pops: the loudest word of her performance (-8.9 dB, "what"); arc 0.2 m, spin, glint; lands crooked 13.95 s; ping at -34 dB under the voice.
- 15.75–16.6 s he tries to fix it, freezes when she starts again (16.74 s "You mad mad"); 29.0–30.0 s he fixes it fully (his own talking section).
- 44.00–44.40 s fire: inside a real 0.4 s silence (-56…-60 dB) right after his "Shut the f*** up, up!"; he ducks 3 frames early, keeps yelling "How about that? You like that?" while coming back up.

## Where the visuals could not follow the brief / the source cleanly
1. The brief assumed the sorceress speaks the whole clip. She speaks only the on-screen speaker's parts; the off-screen voice (incl. the angriest part) is the knight (Enes's choice, 25 Nov).
2. The opening: the source starts with the off-screen voice, so frame 0 has the knight talking, not the sorceress.
3. 0–6 s and 28.6–34 s: the off-screen voice is quiet and Whisper could not read it; the knight's mouth follows the loudness only (no word shapes).
4. 42.6–45.6 s: the source speaker keeps his mouth half open (grinning) while the other voice yells; the sorceress keeps her mouth closed there so the yelling clearly belongs to the knight.
5. The strongest angry beat is the knight's line, so the fire is her answer to his outburst rather than the top of her own anger.
6. Loop: the clip ends on her line and the knight back in his opening pose with the helmet straight; it is close to frame 0 but not a perfect loop (frame 0 has the knight mid-sentence). The audio is not cut or extended for a loop.
7. The audio contains strong profanity; it is untouched as the brief asks (may limit monetisation; this is someone else's reel: posting it can draw a copyright / reused-content claim).
