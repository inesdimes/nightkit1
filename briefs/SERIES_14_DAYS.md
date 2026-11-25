# 14-day single-format test (started 21 Nov 2026, Enes + Claude)
Goal: stop switching genres; give YouTube (and viewers) one clear thing this channel is. Decide with data on day 14.

## Format (every video)
- Title: "Why Do <game trope>...?" - a question every player already has.
- Story: the trope -> a character who wants something -> a twist answer -> a small heart -> a short ironic last line.
- PS1 look, nightkit engine, ~30 s, Enes-timbre voice (Kokoro bm_george -> ChatterboxVC), no word-stress tricks.
- Reuse locked assets (knight, boss, goblins, arena, hall, chests); one new prop or set at most.
- Lessons from reviews/four_phases_review.md: the close-up shows the character the line is about, props in hands,
  everyone inside the frame, frame 0 big and moving.

## Tone 2.0 (from day 2, Enes: "the stories feel too childish")
Keep the format (a game trope every player knows + a twist answer), change the depth. Model: Final Boss A, our best video,
which was not a joke: the hero becomes the next prisoner.
- One human truth per video: being forgotten, waiting, repetition, regret, letting go, getting old, a promise kept too long.
- The character has a past: a number of years, a lost thing or person, a promise. The trope is what that past looks like from outside.
- The twist reframes the trope as something sad or human. Humour only dry, never cute (no "+1 FAN", no DAY OFF emotes).
- The ending is bittersweet and quiet: the last line lands softly, it is not a punchline.
- Picture: darker palette, fog, one main light source, creeping holds, fewer cuts; keep the story moving: a new beat every 2-3 s. HUD only where it is part of the story, and at most one UI element at a time.
- Voice (corrected 21 Nov after mimic: Enes found it too slow and did not like the voice): **same pace and settings as four_phases**
  (`tools/tts/fp.py`: Kokoro bm_george speed 1.22, pauses 0-0.15 s inside a line, ~0.3 s between lines, then ChatterboxVC).
  Depth comes from the story and the picture, NOT from a slower voice. No quiet stretch over ~1 s.
- Frame 0 (ANALYTICS 16, speech video 95 % swiped): readable at a glance (clear silhouette, bright enough, a face or an action), moving within the
  first second, and never a skip / exit / loading-style prompt on screen in the first seconds.
- Sound: never a per-sample random gate (`rng.random(n) < p`) - that was the crackle in day 1.

## Format 3.0 (from day 3, 23 Nov 2026, Enes: "we look too crude/janky": constant camera, the subject always in focus, a personality for every character, several voices, 1.2x)
These override any older camera / voice rule above (the "hard cuts every 2.5-4 s" idea from RAPOR Aşama A is NOT used; "fewer cuts, creeping holds" becomes "always moving").
1. **The camera never stops.** Every shot has a slow, eased move (track, push-in, orbit of 10-25 degrees, crane); no static shot, no handheld shake. One move per shot, no zig-zag; cuts only at scene changes (now / flashback / end), at most 4 per video. The move is motivated (it follows the speaker, reveals, or closes in).
2. **The subject stays in focus.** The video's subject (the character the question is about) stays inside the middle third of the frame and is the largest, brightest thing in it for the whole video. Helper characters and props are lit lower and a little smaller; the subject gets the one accent colour. When a helper enters, the camera RE-FRAMES so everyone fits: build a group framing (`follow_group(subject, others)`: bounding box of everyone speaking or acting, 15 % margin, eased), never let a head touch the frame edge, never crop a speaker. The group framing eases back to the subject when the helper leaves.
3. **Every character has a personality the viewer can read with the sound off.** A character card in every brief: (a) silhouette / prop (b) idle loop (what the body does when nothing happens) (c) signature gesture (d) how they react to the subject (e) voice. No generic standing boxes: idle motion from frame 0.
4. **Several voices, two versions (Enes, 23 Nov).** Claude generates the AI voices; Enes records the lines himself too, and the better one is used per video (or per character). Narrator AI = Enes timbre (Kokoro bm_george -> ChatterboxVC). Each character AI = a DIFFERENT Kokoro voice, NOT converted to Enes (the conversion flattens them); contrast in pitch and speed (e.g. bm_lewis, bm_fable, am_michael, am_adam, af_nicole, bf_emma). Character lines <= 8 words, in the character's own words; the narrator only bridges. Subtitle colour = speaker. Output both: `tts/<name>/` (AI) and a recording list in `briefs/ENES_VOICE_SCRIPTS.md` (`tts/<name>_own/`, built with `python tools/tts/<name>.py build own`); render the AI version first, re-render with Enes's takes when they arrive. Test every AI voice on 2 lines before the full build.
5. **1.2x (Enes, 23 Nov: speed the FINISHED video up).** Build the video at the natural pace (narrator Kokoro S=1.22, pauses 0-0.15 s, ~0.3 s between lines), then speed the finished mux up 1.2x as done for enemies_queue (`setpts=PTS/1.2,fps=24` + `atempo=1.2`, then `acompressor=threshold=0.2:ratio=3:attack=5:release=80,loudnorm=I=-14:TP=-2.0`). The times in the briefs are FINAL times (after the speed-up): the build is 1.2x longer. Keep the 1.0x file in `scratch_old/`. Check that the voice still sounds clean after atempo (`sc_check.py`) and that the planned beats still land (subtitle times scale automatically).
6. Additions from the analyses (ANALYTICS 9-20, RAPOR): (a) the stake is said and shown by ~6 s (every curve loses half the audience by ~0:10); (b) character speech or a SFX at 0.0 s, no silence over 0.3 s; (c) last frame = frame 0 composition (loops gave 125-160 % retention); (d) one HUD counter at most, it carries the story; (e) judge each video by stayed % first (target >= 60 %), then average view %; (f) no on-screen "send this to..." CTA (it fights the quiet ending): put the question in the pinned comment instead.
7. **Look (decided 23 Nov): 270x480 internal resolution (x4 to 1080x1920) + depth outline + soft post (no scanlines) is the DEFAULT for all new videos** (as in `examples/one_gold_potion.py`: `W,H,S=270,480,4`, `outline()`); the old 180x320 + heavy VHS look is retired. Port the outline into the shared engine on the first build (do not copy-paste per video).

## Posting rules (updated 22 Nov 2026 from the YouTube audience data, ANALYTICS.md sections 18-19)
Target audience: Europe and America. YouTube is the main platform (it reaches abroad: US 24 %, TR 15 %); Instagram and TikTok
get the same videos but are not used for decisions (TikTok is 82 % Türkiye; Instagram shows no country split yet).
- TWO videos a day, scheduled (YouTube Studio "Schedule", Instagram/Meta scheduling, TikTok Studio on the computer):
  - **Updated 25 Nov (ANALYTICS 21, agreed with Enes): YouTube English uploads at 01:00 TR.** All three 01:00 posts reached YouTube's
    normal band (US top region); the three 22:00 posts did not (first shown in Turkey). Instagram: the slot does not seem to matter.
  - (old rule, replaced) 1st video 22:30-23:30 TR, 2nd ~01:00 TR.
  - **Best videos on Saturday and Sunday evenings** (the brightest cells in YouTube's "when your viewers are on YouTube").
  Length follows the topic, not the slot: never pad a story; since 25 Nov keep videos at 40 s or under, fantasy/RPG tropes only,
  the cover title burned into the first 1.5-2 s, end with a question that invites comments, like-nudge toast via nightkit/cta.py.
- Everything in English (titles, captions, hashtags, voice). No trend hashtags. Never delete or re-upload.
- Success is measured on **YouTube**: stayed-to-watch % first (target >= 60 %), then views. Instagram KPI kept as a side note:
  skip rate (< 30 %) and average watch %.
- 48 h after each post: Enes sends YouTube screenshots (overview, stayed/swiped, avg view + retention curve, traffic source);
  Claude logs them in ANALYTICS.md (with the slot) and names at most 3 changes.
- Track the two slots separately; if the 2nd video keeps starting near 0 while the 1st does not, revisit the spacing (Enes decides).

## Day 14 decision
Keep the format if median views or stayed % rise over the 14 days. If both stay flat (median < 300 views and stayed < 50 %),
change the format based on what the retention curves show. Not before.

## Queue (Claude writes the briefs a day ahead; GO.md points to the next two)
| # | Slot | Title | Want / twist / heart / last line | Assets |
|---|---|---|---|---|
| 1 | 22:00 | Why Do Final Bosses Give a Speech Before the Fight? | wrote it 30 years ago, every hero presses SKIP / one knight doesn't / 11 minutes, the knight claps / "He lost in one hit. Best day of his life." | boss, knight, arena + throne, candles |
| 3 | 02:00 | Why Do Enemies Attack One at a Time? | goblins take a number / #47 waited 3 h, the hero saves and quits / the hero comes back just for him / "He framed the ticket." | goblins, knight, hall |
| 4 | 22:00 | Why Do NPCs Repeat the Same Line? | (Tone 2.0) an old man at a well: "The well is dry" for 40 years / he says it so nobody climbs down where his wife's ring fell / one knight climbs down and brings the ring up / "He never said that line again. The village was quieter. So was he." | old villager (new), well, village at dusk, knight |
| 2 | 02:00 | Why Do Mimics Pretend to Be Chests? | (Tone 2.0) a chest opened and emptied by every hero for a hundred years learned to bite / one knight opens it, takes nothing and leaves a coin inside / "For the first time in a hundred years, something was given back." | knight, chest (+ teeth), dungeon hall |
| 5 | (moved, rework) | Why Is the Legendary Sword Only 50 Gold? | **same story as briefs/one_gold_potion.md (shopkeeper, 50 gold, ex-hero): do not build as is** - the shopkeeper was the last hero and failed / he sells it cheap so someone finishes / the knight brings back the boss's crown / "He still charged him 50 gold." | shopkeeper (new), knight, shop |
| 6 | **day 3, 02:00** (`briefs/pots.md`) | Why Do Heroes Smash Every Pot? | an old woman replaces the pots for 40 years and hides a coin in each (her son left to be a hero) / nobody says thanks / one knight puts the coin back and sits down for tea / "The only pot she never had to replace." | old woman (new), knight, cottage |
| 7 | **day 3, 22:00** (`briefs/tutorial_guy.md`) | Why Does the Tutorial Guy Never Come With You? | he has taught "press space to jump" 10,000 times / he froze at the first slime 40 years ago / the knight holds out a hand, he takes ONE step past the fence / "But now he leaves the gate open." | tutorial NPC (new), knight, field + fence |
| 9 | 02:00 | Why Do Enemies Drop Gold? | every morning a goblin mother gives her kids pocket money for work / the hero collects it / one knight gives the coins back / "She gave them right back to the kids." | goblins, knight, hall |
| 8 | 22:00 | Why Does the Horse Always Come When You Whistle? | the horse runs across the whole map at full speed, every time, for years / it has never rested / one day the hero walks to the horse instead / "The horse slept for a week." | horse (new), knight, field |
| 10 | 02:00 | Why Do Dungeon Traps Always Miss the Hero? | an old goblin engineer builds every trap / they miss on purpose: his son is an adventurer / the son finally visits / "The traps still miss. Now they also wave." | goblin engineer, knight/son, hall |
