# THE LAST RESPAWN - production brief (23 Nov 2026)
Source: `briefs/last_respawn_gpt.md` (GPT, approved story direction). Everything in that file applies, EXCEPT the changes below
(decided by Enes with Claude). Where the two files disagree, this file wins.

## Changes to the GPT brief
1. **The sacrificing knight is NOT our series Knight.** He is **the Bell Knight**: an old commander, hollow armour, tarnished
   bronze plates, a torn grey cape, the pale cyan chest emblem. Our Knight (silver, blue cape) does not appear in this episode
   (a later episode can find the Bell Knight's empty armour). Replace "THE KNIGHT" with "THE BELL KNIGHT" everywhere.
2. **"The Keeper" is renamed "the Bellwright"** (the Keeper is the lighthouse keeper of the world bible).
3. **Voices:** no narrator. Enes voices all three characters (separate clean takes per line; see `briefs/last_respawn_voice_sheet.md`).
   Fallback if a take is missing: Kokoro on the PC (Bell Knight `bm_george`, Bellwright `bm_lewis` pitched down, Goblin 47 `am_puck`
   pitched up) - placeholders only, never presented as Enes's performance. Light FX: metallic resonance on the Bell Knight,
   short stone reverb on the Bellwright, the Goblin dry.
4. **Detail is welcome, but every rule must be SHOWN, not only said:** the counter 1 -> 0 (respawn rule), the motionless bell
   (failure), the open breastplate with only a spark (hollow), the kneeling shells (they remember him), the spark leaving his chest
   into the bell (the price), the same alley + the same arrow (the loop). If a rule has no picture, it does not go in.
5. **Shells:** 5 (instanced), not 8. Running: short bursts; mostly fast walking + gliding camera (box characters look stiff when running).
6. **Production: Blender, in phases with a decision gate** (below). Characters are rigid-part puppets (boxes/low-poly parts parented
   to bones or empties, keyframed from Python), NOT skinned meshes: no weight painting, no cloth, no face rig.

## Phases (the PC session runs 1-3 without stopping, then stops for Enes)
1. **Blockout:** graybox alley + bell chamber + the three characters + 5 shells + arrow, in `blender/last_respawn/`. Frame-0 still.
2. **Hook test:** render 00:00-00:08 at preview quality (50 %, low samples) with placeholder voices.
3. **Loop test:** render 00:52-00:58 + 00:00-00:03 joined; check camera, pose, arrow path, whistle across the boundary.
   **STOP: send the hook test and loop test to Enes.** He decides: continue in Blender, or move the episode to nightkit.
4. Look development, Enes's real voice takes, full render, QA (`tools/qa/check.py`, loop check), captions.
