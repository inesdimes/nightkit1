# Why do NPCs stand still at night? — full brief (Claude, 27 Nov 2026, rules v27 Nov b)

Status: brief ready, NOT built. Build with the nightkit-short skill (rules filter already passed, see the self-check at the end).
Tone: CREEPY (Mimic Shop line). Final ~29 s (x1.2 post). Spoken words: 72.

## Cover (first 1.5-2 s)
WHY DO NPCS / STAND STILL / AT NIGHT?

## Rule of the story
The Watcher only sees what MOVES. Villagers survive the night by standing still. Heroes never stop moving.
Logic check: every capture / detection in the film is triggered by motion (cat, torch flame, thrown hat); nothing still is ever seen.

## Stakes + urgency
- Character to root for: the knight (cocky, waves at frozen people) and the old villager Bram (planted: his red hat).
- What can be lost: the knight's life; at the end, Bram's.
- Urgency: HUD `DAWN 0:30` counts down from frame 1; the Watcher's footsteps get closer; a DETECTION meter fills when he moves.

## Cast
- KNIGHT (ALREADY BUILT, dragon_taxes KNIGHT + open helmet, blue plume): carries a TORCH (planted: the flame always moves).
- BRAM, old villager (BUILT: dragon_taxes VIL3 bald + grey beard) + NEW red pointy hat (planted, frame 1).
- MARTA, villager woman (BUILT: dragon_taxes WOMAN), faces a wall; whispers without moving her lips (Betül).
- 3 more villagers (BUILT: VIL1, VIL2, KID), all frozen facing walls / mid-step.
- THE WATCHER (NEW): 6 m tall, thin, made of fog; never fully seen: a long pale face, two lantern eyes (emissive yellow-white), very long
  fingers. It "sees" with a pale CONE of light from its eyes that sweeps the square. A black cat (NEW, small).

## Place
- Village square at NIGHT (BUILT: dragon_taxes square_set houses + npc_well well), blue moonlight, low rolling fog (fog planes),
  lit windows, two torches on posts, a cart, puddles that reflect the moon. Dawn version at the end (dragon_taxes sky_set).

## Shot table (FINAL seconds)
| time | camera | what happens + FX | line | game text |
|---|---|---|---|---|
| 0.0-2.2 | medium, low angle, slow push-in | Frame 1: the knight walks INTO frame between two villagers frozen facing walls, waves his gauntlet in front of Marta's face. Torch flame flickers, embers float up, fog rolls over boots. Bram (red hat) frozen mid-step in the background. | N: Why do NPCs stand still at night? | DAWN 0:30 (ticking) |
| 2.2-5.0 | close-up on Marta's face, very slow push-in | Only her EYES move: slowly to the fog at the end of the street. A single bead of sweat. Off-screen: a deep THOOM, a puddle ripples in the foreground. | K (off, cheerful): Hello? Is anyone home? | |
| 5.0-8.5 | wide reveal (2 s) -> push-in | At the far end of the street two lantern eyes OPEN high above the roofs. THOOM: camera shake, a cart rattles, windows go dark one by one (click click click). The DETECTION meter appears (empty eye icon). | N: They aren't broken. They're hiding. | DETECT meter appears |
| 8.5-12.0 | medium, side tracking | The pale cone sweeps across the square. A black cat dashes across -> the cone SNAPS onto it -> it is yanked into the fog (a meow cut off, a bell rolls back). The knight is still walking, sword drawn. Meter +30 %. | Marta (whisper, lips still): Stop. Moving. | meter 30 % |
| 12.0-15.5 | over the knight's shoulder, slow orbit | Head fake: the knight laughs and keeps going. Bram slowly, slowly moves ONE finger to point at the wall behind the knight: the knight's shadow on the wall is now TWO shadows, the second one 6 m tall. Meter 60 %, footsteps faster. | K: Hide? I'm the hero. | meter 60 % |
| 15.5-18.5 | close-up knight -> slow turn | WORDLESS BEAT (1.5 s): the knight turns; the Watcher's face fills the frame behind him, eyes like lamps. He freezes mid-step, one foot raised. Sound drops to a heartbeat. Only his eyes move to the villagers. | (none) | meter 95 % shaking |
| 18.5-21.5 | extreme close-up: the torch | The TORCH FLAME is still moving: the meter creeps 96, 97, 98... The knight cannot drop it. Bram's hand closes on his red hat. | (none, heartbeat + flame crackle) | meter 98 % |
| 21.5-24.5 | medium, Bram in focus | Bram THROWS his red hat high across the square (slow-mo arc). The cone snaps to Bram's movement -> long fingers out of the fog -> Bram is gone in a swirl of fog; the hat lands in a puddle. Meter drops to 0. | N: Every night, someone has to move. | meter 0 % |
| 24.5-27.0 | wide, time-lapse | DAWN 0:00: the sun shoots up, fog evaporates, birds. The villagers unfreeze and cheerfully repeat their day lines. Marta picks up the wet red hat, holds it to her chest. | Villager: Nice weather today! | DAWN 0:00 -> fades |
| 27.0-29.0 | = frame 1 framing | LOOP: time-lapse back to night, everyone snaps back to the walls; a NEW hero walks in and waves at Marta -> exactly frame 1. | K2 (new hero): Hello? | DAWN 0:30 |

Planted detail: Bram's red hat (0.0 s background) -> thrown 21.5 s -> in Marta's hands 25 s.
Head fake: 12.0 s (we expect the hero to fight; he cannot even move) + 21.5 s (we expect the knight to be taken; Bram is).
Re-hooks: 2.2 eyes move, 5.0 the eyes in the fog, 8.5 the cat, 12.0 two shadows, 15.5 the face, 18.5 the flame, 21.5 the hat, 24.5 dawn.

## Lines (EN = Enes's cloned voice, TR = Enes / Betül record)
| # | speaker | EN | TR | read |
|---|---|---|---|---|
| 00 | N | Why do NPCs stand still at night? | NPC'ler geceleri neden kıpırdamaz? | hook, calm, low |
| 01 | KNIGHT | Hello? Is anyone home? | Merhaba? Kimse yok mu? | cheerful, oblivious |
| 02 | N | They aren't broken. They're hiding. | Bozuk değiller. Saklanıyorlar. | quiet, slow |
| 03 | MARTA (Betül) | Stop. Moving. | Kıpırdama. | WHISPER through her teeth |
| 04 | KNIGHT | Hide? I'm the hero. | Saklanmak mı? Ben kahramanım. | laughing, proud |
| 05 | N | Every night, someone has to move. | Her gece birinin kıpırdaması gerekir. | heavy, slow |
| 06 | VILLAGER | Nice weather today! | Bugün hava ne güzel! | bright, too cheerful (the NPC line) |
| 07 | HERO 2 | Hello? | Merhaba? | same as 01 |

## Sound + FX
- Bed: night wind, crickets that STOP at 5.0 s, fog hiss. Music: none until dawn; a low drone that rises with the meter.
- THOOM footsteps (sub 35 Hz + rumble + window rattle) at 2.5, 5.0, 7.0, 13.0, 14.5 (faster); camera shake each.
- Windows clicking dark (5.5-7.5), the cone = a glassy shimmer tone, the cat: dash patter + cut-off meow + bell rolling.
- Heartbeat 15.5-21.5 (speeds up), torch crackle exaggerated at 18.5, the hat whoosh in slow-mo, fog swirl, silence 0.4 s.
- Dawn: a bright music-box sting, birds, the village bell; loop: reverse whoosh back to night.
- Visual FX: rolling fog planes, embers from the torch, eye glow bloom, the cone (additive pale wedge), puddle ripples,
  shadow-on-wall projection (2D overlay), sweat bead, time-lapse sky, slow-mo hat arc with motion trail, meter shake.

## Captions / comment
Pinned comment (A/B): **Freeze or run?** · TR: **Donar mıydın, kaçar mıydın?**

## Self-check
[x] fantasy/RPG trope (NPCs frozen at night), "Why do" title = the rule, every detection is motion
[x] frame 1 big + moving + lit; only ONE game text (DAWN 0:30) besides the cover
[x] stakes + urgency in 3 s (timer, footsteps), re-hook every 3-4 s, two head fakes
[x] ~29 s, 72 words
[x] planted hat, wordless beat 15.5-18.5, loop to frame 1
[x] A/B comment question
