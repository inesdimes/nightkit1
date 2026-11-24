# What if the boss's health bar was the village's? (24 Nov 2026)

Source: a GPT-written brief Enes pasted (30 s, 9:16, 1080x1920, 24 fps, 1998-2001 PS1 RPG look, shot-by-shot timeline 0:00-0:30,
exact dialogue for narrator / knight / old woman / guardian, Enes records all voices himself, no synthetic voices).
Built in nightkit HD as `examples/boss_health_bar.py` (Enes: always nightkit). Voice cue sheet: `boss_health_bar_voice_sheet.md`.

## Core rule
A knight attacks a chained guardian. Each hit travels through its chains to the village. The guardian holds back a curse.
The knight must strike the king's seal on the chain, not the guardian.

## Approved additions (Enes, 24 Nov)
1. Planted lantern: the guardian shields the same lantern model that hangs at the old woman's door.
2. Wordless beat (0:23-0:24): the lights come back one by one, her door lantern last; she lifts her hand to it and smiles.
3. Loop: the knight raises his sword toward the castle at the end; frame 0 is the sword striking.

## How the brief maps onto nightkit (adaptations)
- Timeline: built at 36 s = the brief's seconds x 1.2, then `tools/speedup.sh` (Format 3.0) -> exactly 30.0 s, every beat on its brief timestamp.
- Location: one ruin (broken pillars, dungeon gate) with the village on a hillside across the plain (+x) and the king's castle on a hill (-x).
  The village is a terraced hillside so its windows read from the low opening camera, between the knight and the guardian.
- HUD: "VILLAGE n/10" + 10 pips counting the 10 village lights (9 windows + her lantern). The brief says the bar drops at 0:00 and stops at 0:18,
  so it also drops at 3.4 (behind her), 11.2 (her lantern) and 14.3 (during the seal track): 10 -> 6, back to 10 by 23.4.
- "QUEST UPDATED — FIND THE KING": the 5x7 pixel font has no em dash and the line is too wide for 1080 px at a readable size,
  so it is two lines: QUEST UPDATED / FIND THE KING.
- 0:15-0:18 "the knight lowers his sword and points": he points with the sword tip (a left-hand point would cross his body = clipping).
- 0:16.6-0:18: a 1.4 s cut to the woman for "The king's seal!" so the shouted line has a speaker on screen.
- Voices: none rendered (brief). Subtitles use planned timings until Enes's takes are built with `tools/tts/bhb.py build own`.
