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

## Posting rules (updated 22 Nov 2026 from the YouTube audience data, ANALYTICS.md sections 18-19)
Target audience: Europe and America. YouTube is the main platform (it reaches abroad: US 24 %, TR 15 %); Instagram and TikTok
get the same videos but are not used for decisions (TikTok is 82 % Türkiye; Instagram shows no country split yet).
- TWO videos a day, scheduled (YouTube Studio "Schedule", Instagram/Meta scheduling, TikTok Studio on the computer):
  - **1st video, ~60 s story: 22:30-23:30 TR** (Europe 19:30-21:30, US East 14:30-15:30).
  - **2nd video, ~30 s: ~01:00 TR** (US East 17:00, US West 14:00; 02:00 TR is at the edge of the active band).
  - **Best videos on Saturday and Sunday evenings** (the brightest cells in YouTube's "when your viewers are on YouTube").
  Length follows the topic, not the slot: never pad a story to reach 60 s.
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
| 5 | 22:00 | Why Is the Legendary Sword Only 50 Gold? | the shopkeeper was the last hero and failed / he sells it cheap so someone finishes / the knight brings back the boss's crown / "He still charged him 50 gold." | shopkeeper (new), knight, shop |
| 6 | 02:00 | Why Do Heroes Smash Every Pot? | an old woman has replaced the pots for 40 years and hides a coin in each / the hero never says thanks / one knight brings her a new pot / "She smashed it. Habit." | old woman (new), knight, cottage |
| 7 | 22:00 | Why Does the Tutorial Guy Never Come With You? | he has taught "press jump" 10,000 times / he is afraid to leave the starting field / the knight walks him one step past the fence / "Then he went back. He's really good at teaching jump." | tutorial NPC (new), knight, field + fence |
| 9 | 02:00 | Why Do Enemies Drop Gold? | every morning a goblin mother gives her kids pocket money for work / the hero collects it / one knight gives the coins back / "She gave them right back to the kids." | goblins, knight, hall |
| 8 | 22:00 | Why Does the Horse Always Come When You Whistle? | the horse runs across the whole map at full speed, every time, for years / it has never rested / one day the hero walks to the horse instead / "The horse slept for a week." | horse (new), knight, field |
| 10 | 02:00 | Why Do Dungeon Traps Always Miss the Hero? | an old goblin engineer builds every trap / they miss on purpose: his son is an adventurer / the son finally visits / "The traps still miss. Now they also wave." | goblin engineer, knight/son, hall |
