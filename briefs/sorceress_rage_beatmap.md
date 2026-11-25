# The First To Ever Ragebait — source beat map + timing notes (25 Nov 2026)

Source: `voice/snapgram.io_fv3w5zze9dpz.mp4` — 57.57 s, 30 fps, 576x650, AAC 44.1 kHz stereo, -14.1 LUFS, -1.8 dBTP.
On-screen text: "The first to ever ragebait" + 🤣🤣 for the whole clip (kept; pixel font + two pixel laughing faces, the font has no emoji).
Script: `examples/sorceress_rage.py`. Render: `renders/sorceress_rage/the_first_to_ever_ragebait_sorceress_58s.mp4` (30 fps, 1080x1920, 57.57 s).
Analysis: `voice/sorceress_src/mesh.json` (MediaPipe FaceMesh, 1726/1727 frames), `words.json` (Whisper small.en word times), `db.npy`.

## Two voices -> v2 roles (Enes, 25 Nov evening: the angry voice is the sorceress, the calm ragebaiter is the knight; they face each other)
| Time (s) | Voice | Words (Whisper, approximate) | In the adaptation |
|---|---|---|---|
| 0.00–5.95 | off-screen | mostly unintelligible ("Because…") | sorceress talks (mouth from loudness + vowel colour), annoyed; knight smirks |
| 5.95–28.62 | on-screen speaker | "Because you just said my name name. So you must really be mad mad, and for what? Why you mad mad for? You mad mad, you must really be mad mad if you call me my name name. Calling me Steven, no bae, no boo boo, no butter, my name name." | knight trolls (mouth + head from the tracked face), smug grin, one brow up; she fumes, hands on hips, eye-roll at "no butter" |
| 28.62–33.85 | off-screen | quiet ("Alright…") | sorceress, exasperated; helmet pops on her last word |
| 33.85–42.60 | on-screen speaker | "I didn't know you wanted me to do it do it. If you say yo just do it do it, I would have did it right then and there. I'm gonna just do it. I'm just not gonna do it, do it." | knight trolls on with a crooked helmet (tried to fix it, froze under her glare) |
| 42.60–55.45 | off-screen (the rant, profane) | "Shut the f*** up, up! How about that? You like that? … Up, up! Shut the f*** up, up! F***ing dickhead dickhead! Stupid b**** b****! That's what you want?" | sorceress rages, points at him, FIRE after "UP!", he ducks; then he grins through the rest and straightens the helmet |
| 55.45–57.35 | on-screen speaker | "…but you really mad, man." | knight, smug; she glares |

## Gags (snapped to her measured beats)
- 4.97 s helmet trembles: her first loud rise (-17.7 dB band peak).
- 33.43 s helmet pops: her "Alright" emphasis (-18.4 dB); arc 0.22 m, spin, glint; lands crooked 34.02 s; he tries to fix it 34.15–34.75 s and freezes under her glare (34.6 s); fixed for good 53.4–54.15 s (a real pause in her rant).
- 44.03–44.40 s fire: inside the real 0.37 s silence (-56…-60 dB) right after her loudest word "UP!" (43.57 s, -11.6 dB); he ducks 3 frames early, eyes shut, then grins again.

## Where the visuals could not follow the brief / the source cleanly
1. 0–6 s and 28.6–34 s: the off-screen voice is quiet and Whisper could not read it; her mouth follows loudness + vowel colour only (no video reference for that voice at all, also in the rant).
2. The helmet pop is on her "Alright" (her first strong word) rather than in her first section: her opening is quiet (max -17.7 dB), so that section only gets the tremble.
3. 42.6–45.6 s: the source speaker keeps his mouth half open (grinning) while she yells; the knight shows an alarmed face there instead, then grins.
4. Loop: the clip ends on his line with the helmet straight and both in their opening poses; close to frame 0 but not a perfect loop. The audio is not cut or extended.
5. The audio contains strong profanity; untouched as the brief asks (may limit monetisation; this is someone else's reel: posting it can draw a copyright / reused-content claim).
