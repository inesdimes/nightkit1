# WHAT IF THE DRAGON WAS STEALING THE KING'S TAXES BACK? - production brief (23 Nov 2026)
Source: `briefs/dragon_taxes_gpt.txt` (GPT). This file adapts it; where they disagree, this file wins.
~45 s, 9:16, 1080x1920, 24 fps, 22:30 slot. Engine: **Blender** (rigid-puppet rig + lighting from `blender/last_respawn/`).

## Fixes to the source
1. **Hook = title.** The first line asks the title question ("What if the dragon was stealing the king's taxes back?"), not a different one.
2. **Coins do not carry a village crest** (kingdom coins carry the king's face). What the woman recognises are the **tax sacks**:
   rough sacks with a painted Hearthmoor seal and "WINTER TAX" - shown as a close 2D insert so it reads.
3. **The king lives in the Last Castle on the hill** (world bible): the soldiers come from there; the castle is in the night wide shot.
4. **How the soldiers leave must be shown:** the dragon's wingbeat blows out every torch; in the dark the soldiers' horses bolt;
   the captain is the last to back away. No fight, no gore.
5. **The Knight speaks two short lines** here (series Knight: silver, blue cape). World bible note: he "speaks rarely, in short lines".
6. **No crowds:** 3 villagers + the old woman; 3 soldiers + the captain on horseback (riders can stay at a distance as silhouettes with torches).

## Narration and dialogue (exact)
| Time | Picture | Line |
|---|---|---|
| 0:00-0:03 | FRAME 0: the Knight's sword points at a huge dragon head in a torch-lit cave; the dragon opens its claw: tax sacks spill gold onto the stone | NARRATOR: What if the dragon was stealing the king's taxes back? |
| 0:03-0:06 | the old woman (from Hearthmoor, shawl) kneels to a torn sack; close insert: the painted seal HEARTHMOOR - WINTER TAX | WOMAN: That's our winter tax. |
| 0:06-0:09 | the Knight, eyes on the dragon | KNIGHT: The dragon stole it. |
| 0:09-0:12 | the dragon lowers its head to the Knight's level, calm, no attack | DRAGON: No. The king did. |
| 0:12-0:15 | the dragon pushes a pile of sacks forward; all with the same seal | NARRATOR: For years, it had robbed the royal tax wagons. |
| 0:15-0:18 | the Knight's sword dips; the woman closes her fist on a coin | WOMAN: We starved while the king grew rich. |
| 0:18-0:21 | from the cave mouth: night road, a line of torches, the Last Castle on its hill behind | NARRATOR: Then the king's soldiers arrived. |
| 0:21-0:24 | the captain on horseback points | CAPTAIN: Kill the beast. Bring back what belongs to the crown. |
| 0:24-0:27 | the Knight looks at the dragon, then the villagers, then the captain | NARRATOR: The quest was simple. Slay the dragon. |
| 0:27-0:30 | the Knight turns his sword toward the captain | KNIGHT: I found the real thief. |
| 0:30-0:33 | the dragon steps beside the Knight; villagers gather the sacks behind them | DRAGON: Then stand with them. |
| 0:33-0:36 | one huge wingbeat: every torch goes out; horses bolt in the dark; the captain backs away last | NARRATOR: By dawn, the village had its gold back. |
| 0:36-0:39 | dawn, Hearthmoor square: the woman hands out coins to the 3 villagers; the Knight at the village gate | WOMAN: This time, we keep what we earn. |
| 0:39-0:42 | the dragon's shadow sweeps over the square; the dragon circles the road above | NARRATOR: And the dragon kept watch over the road. |
| 0:42-0:45 | HUD: QUEST UPDATED - PROTECT THE VILLAGE; the Knight lowers his sword and turns to the villagers | NARRATOR: Turns out, the monster had been guarding them all along. |

## Picture rules
- Frame 0: dragon head + the Knight's sword big in frame, gold spilling (motion in the first second), the question as a short on-screen line.
- The sack seal and the HUD are 2D overlays / close inserts. Subtitles in the channel's big boxed style; speaker colours:
  narrator white, Knight cyan, dragon deep orange, woman amber, captain grey.
- Light: warm torch-lit cave, cold blue night road with orange torch dots, the dark after the wingbeat, pale gold dawn in the square.
- Contrast >= 35 (`tools/qa/look_metrics.py`), no milky haze near the camera, nothing closer than ~1 m to the lens unless it is the subject.
- Something new every 2-3 s; no silence over ~1 s; mix -14 LUFS, true peak <= -1.5 dBTP.

## Assets and cost
- **The dragon is the big new asset** (expensive): rigid-part low-poly dragon (head + jaw, neck segments, one claw that opens,
  folded/spread wings). Most of the film it sits in the cave; the flight is shown as the wing silhouette against the dawn sky + its shadow.
- New: the old woman, the captain on a horse, 3 soldiers, 3 villagers (simple silhouettes for extras), tax sacks, the cave, the night road,
  Hearthmoor square + gate. Reuse: the Knight.

## Voices
Narrator = Enes. Other lines: Enes, or Kokoro placeholders on the PC (Knight `am_adam`, dragon `bm_george` pitched down 4-5 semitones
+ a little cave reverb, woman `bf_emma`, captain `bm_lewis`), never presented as Enes's performance. Sheet: `briefs/dragon_taxes_voice_sheet.md`.

## Sound
Sword drawn, sacks and coins spilling on stone, the dragon's slow breathing, cave echo on its lines, wind rising, hooves + a horn,
shields, one enormous wingbeat that kills all the torches (then sudden quiet with horses fleeing), dawn birds and warm strings,
wingbeats overhead, one heroic note, cut.

## Captions
YouTube title: What If the Dragon Was Stealing the King's Taxes Back? 💿
Description: The quest said: slay the dragon. Then the knight saw whose gold it was guarding. 🐉
A tiny story from a retro game that never existed. Whose side would you take? 👇
#ps1 #retrogaming #dragon #rpg #shortfilm #gamestory #pleaseinsertdisc2
Pinned comment: Would you have finished the quest? 🐉👇
