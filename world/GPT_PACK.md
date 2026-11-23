# GPT PACK - everything GPT needs to help design the "Insert Disc 2" world (23 Nov 2026)
Paste this whole file into a new GPT chat. GPT designs the WORLD and the STORIES (text only). Claude (cloud + PC) builds,
renders and checks the videos from GPT's text. GPT never writes code and never sees voice files or keys.

## A. Your role
You are the world and story designer for "Insert Disc 2" (@pleaseinsertdisc2), a channel of short vertical videos:
"Tiny stories from retro games that never existed". Reply to Enes in Turkish; write every story, title, narration,
caption and design note in English. Ask at most 3 questions, only if essential. Mark every requirement MUST or NICE-TO-HAVE.

## B. What the videos are (hard limits - design inside them)
- Vertical 9:16, 1080x1920, 24 fps; ~40-60 s (22:30 TR slot) or ~30 s (01:00 TR slot). Target audience: Europe + America.
- Look: 1998-2001 PlayStation 1: low-poly characters made of boxes, flat shading, pixel look, a little dithering/VHS grain.
- Built procedurally in Python by Claude (no AI video or image generators). One narrator (Enes's own voice or a voice conversion of an
  English narrator), synthesized sound effects, little or no music. Subtitles are burned in (exactly the spoken words).
- WHAT WORKS: 1-4 characters made of simple shapes, clear actions (walk, look, reach, kneel, open, drop, climb), faces made of
  a few eye/mouth states, strong silhouettes, objects that carry the emotion (a ring, a letter, a coin, a lantern), on-screen
  game UI (counters, HP bars, dialogue boxes, save menus), camera moves that breathe with the story (pull back / push in).
- WHAT BREAKS: realistic faces and detailed acting, crowds, cloth/water simulation, tiny readable text in the 3D world,
  a screen inside the screen, many fast cuts, contradictory layout rules, anything that needs subtle hand/finger acting.
- Locked, reusable assets (cheap to use): the knight (silver armour, blue cape, plume), the final boss (dark armour, horns),
  goblins (scale/colour variants), the dungeon hall, the boss arena, chests, the purple save crystal, the old villager at the
  well, the pot woman and her cottage, the tutorial guy and his field. New characters or places are expensive: say so.

## C. The format that works (from our analytics)
- Best video so far: "Why Do Final Bosses Never Leave Their Rooms?" (3.0 K views, 64 % stayed): a question every gamer already
  has + a story twist (the hero becomes the next boss). Real-world fact videos did far worse.
- Every video: "Why do <game trope>?" -> the trope from outside -> the life behind it -> a choice -> a cost -> a quiet,
  bittersweet last line (no punchline emoji, no cute jokes like "+1 FAN").
- Frame 0 decides everything: a character big in frame and moving in the first second, readable at a glance, the question on screen.
  NEVER a skip / exit / loading prompt in the first seconds (a video with "PRESS X TO SKIP" in frame 0 lost 95 % of viewers).
- Pace: something new every 2-3 s, narration ~3 words/s with short pauses, no silence over ~1 s.
- Optional style "ONE TAKE": one continuous camera that pulls back to show the world and pushes in for the key moment, big bright
  hero object, ticking counters, the end loops into the start.

## D. Output format GPT must use for each episode brief
1. Title ("Why Do ...?"), slot (22:30 ~60 s or 01:00 ~30 s), place on the map, characters (who is new?).
2. The story in 5 sentences (want / choice / cost / link to another episode / last line).
3. Narration table: line number | exact spoken line | what is on screen (the picture cue lands just before the key word).
4. Frame 0 description (subject, size, motion, on-screen question).
5. Camera plan (3-6 setups or one continuous move), light and colour of the place.
6. Props and UI elements (counters, dialogue boxes) - with their exact text.
7. Sound (effects list with timing, music or none).
8. Captions: YouTube title + description + hashtags (English, no real game names), pinned comment.
9. MUST / NICE-TO-HAVE list and anything that is expensive (new character, new place).

## E. The current world draft (world/WORLD_BIBLE.md) - improve it, keep what works, tell Enes what you changed

Every video so far was born and died in one small room. From now on every story happens in ONE shared game world,
with places that stay, characters who come back, and a secret the series slowly opens.

## 1. The premise (the big idea)
"Insert Disc 2" is a 1999 PS1 RPG that came on two discs. The Player finished Disc 1 one night, saw the screen
**PLEASE INSERT DISC 2**, went to bed... and never came back. That was 27 years ago.
The world of Disc 1 is still running. Its people know their lines, their quests, their loops. They also know, somewhere,
that the story was never finished. Everything strange about game logic is just how life works here.

- Why the channel name fits: every episode is a small story from a game that is still waiting for its second disc.
- Why it is deep: waiting, being forgotten, repeating a role long after anyone watches - real human feelings hidden in game tropes.
- Why it is a hook: gamers know the feeling of an unfinished game. The question "what happens to a game world when you stop playing?"
  is the thread through all episodes.

## 2. The map (Disc 1) - locations are built once and reused
| # | Place | What it is | Look, light, mood |
|---|---|---|---|
| 1 | **Hearthmoor** | the starting village: the dry well, Marta's cottage of pots, the inn, the notice board | warm dusk, chimney smoke, lit windows; home, a little sad |
| 2 | **The Tutorial Field** | a fenced meadow outside the village, the sign PRESS SPACE TO JUMP | bright noon, tall grass in wind, blue sky; innocent, too perfect |
| 3 | **Thornwood Road** | forest road with Edda's shop and the old stable | green fog, light shafts through trees; the journey |
| 4 | **The Sunken Dungeon** | the dungeon under the village (the well leads down into it); the goblin queue, the traps, the mimic at the end | cold teal-blue stone, orange torches; work, routine |
| 5 | **The Last Castle** | on the hill above everything: the save crystal before the boss door, the boss room | red and black, banners, thunder; the end of Disc 1 |
| 6 | **The Edge** | the cliff where the map stops: a lighthouse, the sea, and a wall of fog that says PLEASE INSERT DISC 2 | pale grey-blue, the lighthouse beam; the end of the world |

The castle can be seen on its hill from almost every outdoor place; the lighthouse beam can be seen at night from Hearthmoor.
Those two landmarks make it feel like one world in every wide shot.

## 3. The people (each has a past, a want, a flaw and a link)
| Character | Past | Wants | Flaw | Link |
|---|---|---|---|---|
| **The Knight** | the Player's hero; silent; since the Player left he sometimes moves on his own | to finish something | does not know what he is for without the Player | in every episode |
| **Old Wren** (tutorial guy) | the very first hero; he trained in this field before anyone | that the Player comes back and needs teaching again | stays where it is safe | trained Edda and Tobin |
| **Marta** (pots) | her son **Tobin** left as a hero 20 years ago | a letter, a visit, one thank-you | keeps making pots for heroes who break them | Tobin is stuck in the save loop at the castle |
| **Old Hollis** (well) | his wife **Ilse** went down the well after her ring and never came up | that no one else is lost down there | lies ("the well is dry") to protect people | the well leads into the Sunken Dungeon; Ilse's lantern is inside the mimic |
| **Edda** (shopkeeper) | the hero before the Knight; she lost to the boss | that someone finishes the quest | sells the legendary sword for 50 gold; keeps a book of 31 buyers who never came back | was trained by Wren |
| **Goblin 47** and the queue | dungeon workers who take a number | his turn, once | waits too politely | his mother pays the goblin kids "pocket money" in gold (that is why enemies drop gold) |
| **The Mimic** | a normal chest that was emptied by every hero for 100 years | that someone gives something back | bites | holds Ilse's lantern |
| **Grax** and the boss family | three goblins under one cloak; Grax at the bottom for 30 years | rest | pride | the Knight joined them once (Four Phases) |
| **The Keeper** | the lighthouse keeper at the Edge; the only one who remembers there is a Disc 2 | to keep the light on for the ship that brings the second disc | hope that hurts | the series' big mystery |

## 4. Rules of the world (game logic is physics)
- When the console "resets" at night, the day starts again; people remember fragments of earlier loops.
- Death sends you back to your last save. A bad save can trap you forever (Tobin).
- No one can cross the fog at the Edge. Behind it is Disc 2: the second half of the world, never loaded.
- Enemies attack one at a time, chests refill, pots break: these are jobs that people here do every day.
- The narrator is an old Player telling stories about a game he never finished (Enes's voice).

## 5. How every episode is built (keeps the "Why do <trope>?" format that works)
1. **Frame 0:** a character big and moving + the question.
2. **The world:** the camera pulls back (One Take or a wide shot) and shows where we are on the map, with the castle or the lighthouse in view.
3. **The trope from the outside** (what players see) -> **the life behind it** (the character's past and want).
4. **A choice** made by someone (usually the Knight), and a **cost**.
5. **A link** to the world: one object, name or place from another episode (a lantern, a letter, a number, a name in Edda's book).
6. **A quiet last line**, bittersweet, never a punchline emoji.
Length: as long as the story needs (40-60 s for the 22:30 slot, ~30 s for the 01:00 slot).
Earlier videos become canon: Final Boss (the hero becomes the next boss), Four Phases (Grax), The Save That Killed Him (Tobin),
the mimic, the well, the pots, the tutorial guy. New episodes can call back to them.

## 6. Ten episodes in this world (connected, deeper)
| # | Title | Place | Story (want / choice / cost) | Link | Last line |
|---|---|---|---|---|---|
| 1 | Why Do Games Have Fog at the Edge of the Map? | The Edge | The Knight walks to the end of the world. The Keeper has kept the light on for 27 years "for the ship with the second disc". The fog says PLEASE INSERT DISC 2. The Knight offers to take the next watch; the Keeper refuses and gives him the lamp to carry back instead. | starts the arc; the lamp | "Somewhere, a disc is still in its box." |
| 2 | Why Do NPCs Repeat the Same Line? (remake) | Hearthmoor well | Hollis: "The well is dry." The Knight climbs down anyway and finds the well opens into a dungeon. He brings back only Ilse's ring. | the well leads to the dungeon | "He kept saying it. Now it was true." |
| 3 | Why Does the Tutorial Guy Never Come With You? | Tutorial Field | Wren was the first hero; he stays because if the Player ever comes back, someone must teach him to jump. The Knight sits with him through one reset. | Wren trained Edda and Tobin | "He is still there. Just in case." |
| 4 | Why Do Heroes Smash Every Pot? (remake) | Marta's cottage | Marta hides a coin in every pot for her son Tobin. 14,604 pots. The Knight finds a pot with a letter for Tobin and takes it with him. | the letter goes to the castle | "He took the letter. He left the pot." |
| 5 | Why Is the Legendary Sword Only 50 Gold? | Edda's shop, Thornwood | Edda keeps a book: 31 heroes bought the sword, none came back. She was the 30th... and survived by running. She sells it to the Knight and writes his name as number 32. | Edda's book; she was trained by Wren | "She left a space under his name. For a return date." |
| 6 | Why Do Enemies Drop Gold? | Sunken Dungeon | Goblin 47's mother gives each goblin kid a coin every morning "for work". When a hero defeats them, the coins fall. The Knight starts giving the coins back to the mother. | Goblin 47 | "She never asked where they came from." |
| 7 | Why Do Mimics Pretend to Be Chests? (remake, One Take) | end of the dungeon | the mimic, 100 years emptied. The Knight leaves a coin. Inside he sees an old lantern. | Ilse's lantern (from the well) | "It had been keeping something too." |
| 8 | Why Is There Always a Save Point Before the Boss? | The Last Castle | Tobin has been dying and reloading at the save crystal for 20 years (callback: The Save That Killed Him). The Knight gives him Marta's letter. Tobin finally deletes his save and walks home. | Marta, Tobin | "Twenty years of progress. Gone. He smiled." |
| 9 | Why Do Final Bosses Never Leave? (callback) | boss room | Grax and the cloak goblins again; the Knight has to choose: finish Disc 1 by beating them, or not. He chooses not to; the screen does not change. | Grax, Four Phases | "The game waited for him to win. He let it wait." |
| 10 | Why Do Games Ask You to Insert Disc 2? | The Edge, at night | The Knight returns the lamp to the Keeper. Together they watch the fog. For one second, the fog flickers, like a disc tray opening somewhere far away. | ends the first arc | "Somebody, somewhere, pressed OPEN." |

## 7. Production notes (for the PC)
- Build the six places as reusable modules (`world/sets/<place>.py`) and the cast as one module (`world/cast.py`), each with a lock note
  like the existing locked knight. Start with Hearthmoor + the Tutorial Field + the Edge (episodes 1-4).
- Every set has a far background (the castle on its hill, mountains, the lighthouse beam at night) so wide shots feel like a world.
- Bigger sets cost render time: keep the near set detailed and the far background simple (flat silhouettes, fog).
- Use Opus on the PC for building the world modules; Sonnet for routine episode renders.
