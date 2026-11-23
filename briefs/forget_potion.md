# WHAT IF EVERY HEALING POTION MADE SOMEONE FORGET YOU? - production brief (23 Nov 2026)
Source story: `briefs/forget_potion_gpt.txt` (GPT). This file adapts it for production; where they disagree, this file wins.
~45 s, 9:16, 1080x1920, 24 fps. 22:30 TR slot. Engine: **Blender** (reuse the rigid-puppet rig and lighting approach from
`blender/last_respawn/`), PS1-flavoured low-poly, warm/cold story lighting.

## One logic fix (MUST) - the rule is the title
In the source, the young woman at 0:00 already forgets him, and at 0:27 the same woman (Mira) forgets him again. That breaks the story.
**Rule: every potion erases the DRINKER from someone's memory** ("made someone forget YOU").
- 0:00: the woman beside him is **Kaya, his travel companion** (not Mira). He drinks -> Kaya forgets him.
- The ring portrait is **Mira** (the one he fears losing). The soldier and the innkeeper forget him too (he kept drinking).
- 0:21-0:27: he gives the last potion to Mira -> by the rule, **someone will forget HER. The closest bond is his.** He knows it and does it anyway.
- Ending (reversed, same beats): Mira wakes and knows him; **he** no longer knows her.

## Narration and dialogue (exact)
| Time | Picture | Line |
|---|---|---|
| 0:00-0:03 | FRAME 0: close, the wounded adventurer gulps a glowing red potion; Kaya beside him jolts awake and recoils | NARRATOR: What if every healing potion made someone forget you? |
| 0:03-0:06 | Kaya draws her sword; he reaches out | KAYA: Stay back! Who are you? |
| 0:06-0:09 | close insert (2D overlay, readable): his ring opens, a tiny painted portrait of Mira | NARRATOR: He thought the first time was a trick of the light. |
| 0:09-0:12 | flashback, desaturated: battle, he drinks; the old soldier he saved looks at him blankly | NARRATOR: Then the soldier he'd saved forgot his name. |
| 0:12-0:15 | the Hearthmoor inn: the innkeeper blocks the door | INNKEEPER: Rooms are for paying guests. NARRATOR: The innkeeper forgot his face. |
| 0:15-0:18 | close insert (2D overlay): the bottle label, faded: A LIFE RESTORED. A BOND FORGOTTEN. | NARRATOR: The label had been there all along. |
| 0:18-0:21 | night, the old stone bridge on Thornwood Road, rain; Mira lies wounded below it | NARRATOR: Then, beneath the old bridge, he found Mira, dying. |
| 0:21-0:24 | he looks from his last potion to her; hand hesitates; heartbeat | NARRATOR: One potion could save her. |
| 0:24-0:27 | he gives her the potion; her wound glows closed; HIS eyes lose their light for a moment | NARRATOR: But someone would forget her. And he knew who. |
| 0:27-0:30 | Mira opens her eyes, smiles, grabs his hand | MIRA: You came back for me! |
| 0:30-0:33 | he looks at her, polite and empty | ADVENTURER: I'm sorry... have we met? |
| 0:33-0:36 | she freezes; then presses a small wooden horse into his palm | NARRATOR: She wanted to tell him everything. |
| 0:36-0:39 | he turns the toy over, smiles kindly at the stranger | NARRATOR: Instead, she let him believe they'd just met. |
| 0:39-0:42 | he walks away along the bridge at dawn; she calls after him | MIRA: Wait! What's your name? |
| 0:42-0:45 | he stops without turning; HUD: QUEST COMPLETE - MEMORY LOST; hard cut to black on the last word | NARRATOR: He gave her a new life. Now she keeps their story for both of them. |

## Picture rules (lessons from our analytics and reviews)
- Frame 0: the adventurer big in frame, the red potion glowing, motion in the first second; the question as a short on-screen line. No title card.
- All text the viewer must read (ring portrait, label, HUD) is a **2D overlay / close insert**, never tiny 3D text.
- Subtitles: the channel's standard burned-in style (big pixel font ~7.5 px per font pixel at 1080 wide, black box, lower third,
  one highlighted word). Speaker colour: narrator white, Kaya/Mira amber, innkeeper grey, adventurer cyan.
- Light tells the story: warm camp fire (0:00), grey flashback, warm inn, cold blue rainy night under the bridge, pale gold dawn at the end.
  Contrast >= 35 (`tools/qa/look_metrics.py`), no milky haze near the camera; nothing closer than ~1 m to the lens unless it is the subject.
- Acting through bodies and objects (box faces have few states): recoil, sword up, reach out, ring opens, block the door, kneel, pour,
  grab the hand, the toy in the palm, walk away, stop without turning.
- Something new every 2-3 s; no silence over ~1 s; mix -14 LUFS, true peak <= -1.5 dBTP.

## Cast and places (cost)
- NEW (expensive): the adventurer, Mira, Kaya, the old soldier, the innkeeper (5 humans). Keep them as rigid-part puppets with
  3-4 face states; the soldier and innkeeper appear for ~3 s each: simple silhouettes are enough.
- Places: a night camp (0:00-0:06), a flashback battle (one small set + fog), the Hearthmoor inn door, the old stone bridge (night + dawn).
  World link: the inn and the bridge belong to the world bible (Hearthmoor, Thornwood Road).

## Voices
Enes reads the narrator (his own voice). The other lines: Enes too, or placeholders on the PC (Kokoro: Kaya `af_heart`, Mira `bf_emma`,
innkeeper `bm_lewis`, adventurer `am_adam`), never presented as Enes's performance. Recording sheet: `briefs/forget_potion_voice_sheet.md`.

## Sound
Bottle clink and gulp, a heartbeat that rises at the choice, sword drawn, ring click, short battle burst, tavern murmur and door creak,
rain and thunder at the bridge, potion pouring, a soft swell when Mira wakes that cuts out on "have we met?", dawn birds, one piano note at the end.

## Captions
YouTube title: What If Every Healing Potion Made Someone Forget You? 💿
Description: He kept drinking to survive. One by one, they forgot him. Then he found her under the old bridge. 🧪
A tiny story from a retro game that never existed. Would you have given her the potion? 👇
#ps1 #retrogaming #rpg #shortfilm #gamestory #darkfantasy #pleaseinsertdisc2
Pinned comment: Would you give her the potion, knowing you'd forget her? 🧪👇
