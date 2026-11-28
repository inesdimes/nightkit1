# Why do bosses glow red before they attack? — full brief (Claude, 28 Nov 2026, rules v28 Nov)

Status: APPROVED by Enes 28 Nov with 3 touches (below), building in nightkit HD.

## Enes's touches (28 Nov, locked)
1. First dodge: we READ that the knight sees the crystal (eyes flick to it, then he dives); the sword lands where he just stood by 2.0 s.
2. On "Master?" the apprentice's gaze gives the master away; the Hollow King FOLLOWS that gaze down to his own chest.
3. Finale: after the helmet glows, the shield sweeps across and covers the frame -> wipe into frame 1 (where the shield flashes past the lens).
- "Still here, boy. Left!" stays as is. Last line = "Dodge again, or save him?". No extra narrator line.

Original status: brief ready. Seed idea by Enes (28 Nov): the chest glows red -> the knight dodges before the boss even lifts
his sword; the light is an old knight trapped inside the armour; the boss rips the stone out; next attack the helmet glows red.
Tone: TENSION (gerilim) + a quiet emotional reveal. Final ~34 s (x1.2 post). Spoken words: 64 (see the note in the self-check).
Build: nightkit HD, 5 sequences (S1-S5 below), cloned EN voice, all lines male (Enes).

## Cover (first 1.5-2 s)
WHY DO BOSSES / GLOW RED / BEFORE ATTACKS?   ·   TR: PATRONLAR / NEDEN KIRMIZI / PARLAR?

## Rule of the story
The red glow is not the boss. It is the last fallen knight, trapped inside the armour, warning the next hero.
Logic check (every glow in the film comes from the master, never from the boss):
- S1 chest glows -> the hero dodges before the sword moves (the master warned him).
- S2 inside the crystal: the master blowing on an ember = the glow. He is the hero's old master (same white sun).
- S3 the hero dodged TOO EARLY twice -> therefore the boss notices, looks at his own chest, rips the crystal out.
- S4 no crystal = no glow = no warning -> the boss can now fake attacks.
- S5 the master escaped into the helmet (spark at 18.2 s) -> the eye slits glow red -> the hero dodges again.

## Stakes + urgency
- Root for: the young knight (one heart left) and, from 8 s, his old master.
- Can lose: the hero's last heart; the master (when the crystal is crushed).
- Urgency: the boss attacks every 3-4 s; HUD HP = ONE heart, blinking (frame 1), blinking faster after the glow dies.

## Cast
- HERO (BUILT: nightkit/hd.py knight, open helmet, blue plume, eyes visible) + sword + round shield with a WHITE SUN emblem
  (NEW decal, PLANTED: must read clearly at 2.0-4.5 s).
- THE HOLLOW KING (boss, reuse final_boss / boss_health_bar boss, re-skinned): 2.5x the hero, black iron plate, horned helmet with
  two dark EYE SLITS (empty inside: hollow armour), a round RED CRYSTAL window in the chest (fist-sized for him), huge greatsword.
  Voice comes out of an empty helmet.
- THE MASTER (NEW from the HD knight, scaled to fit inside the crystal): old, grey beard (never_attack beard swap), white sun on his
  tabard, warm inner light. Holds a floating RED EMBER between his cupped hands at chest height (hands never touch the ember or the
  face); he puffs his cheeks and the ember flares = the glow. Max 4 characters: 3 used.

## Place
- One place: the boss arena (reuse final_boss arena): cold blue stone hall, two lit braziers (glow + floor pool + real light, the
  light must read), cracked floor, dust in the air. While the crystal lives, everything near the boss carries a red bounce light;
  after 17 s only the cold blue + braziers remain.

## Shot table (FINAL seconds)
| time | camera | what happens + FX | line | game text |
|---|---|---|---|---|
| S1 0.0-2.0 | medium, low angle, slow push-in | FRAME 1 (opens as the shield wipes out of the lens): the hero big in the left foreground, eyes on the crystal (0.0-0.5), then dives to screen-left, shield flashing past the lens. Behind him the Hollow King towers centre-right, chest crystal FLARING red (bloom, red pool on the floor + on the hero's armour). The greatsword still rests point-down on the floor: he hasn't even lifted it. Cover title in the clear top-right area. | N: Why do bosses glow red before they attack? | HP ♥ (one heart, blinking) |
| S1 1.5-4.5 | side view, medium, static + shake | The greatsword slams down exactly where the hero just stood, impact at 2.0 s: stone cracks, sparks, dust, camera shake. The hero rolls up, shield raised, WHITE SUN facing camera (planted). Boss bar slides in at the top. | N: Every hero dodges the glow. Nobody asks who lights it. | THE HOLLOW KING (boss bar) |
| S2 4.5-8.0 | close-up, slow push-in into the crystal | Through the red glass: a tiny old knight pressed against the inside, ember floating between his hands; each puff = a red pulse. He waves one arm hard to screen-left. | MASTER (tiny, muffled through glass): Left! Now! | |
| S2 8.0-11.0 | over the hero's shoulder, slow orbit | The sword is still down, but the hero dives left again; THEN the sweep comes from the right and misses by a hand. The hero stares at the crystal: the tiny knight wears the SAME white sun as his shield. His gaze locks on the crystal (and stays there) = he gives the master away. | HERO: Master? You fell here... | |
| S2 11.0-14.0 | close-up on the crystal, the hero's face reflected in the glass | The master nods, tired. The ember in his hands is smaller than before. | MASTER: Forty heroes since. I warned every one. | |
| S3 14.0-16.0 | low angle, close-up on the boss helmet, very slow push-in | WORDLESS BEAT (1.5 s): music cuts, only a low hum + a heartbeat. The huge helmet first follows the hero's stare, then tilts slowly DOWN to its own chest. Inside the crystal the master freezes and looks UP. The glow flickers. | (none) | |
| S3 16.0-19.0 | close-up, side: gauntlet + chest | The gauntlet closes AROUND the crystal (fingers outside the plate, never through it), rips it out: crack, red sparks; crushes it, shards rain, the red light dies, the hall goes cold blue. Easy to miss: one tiny red spark slips between the fingers into the neck seam at 18.2 s (closes the gap for 26 s). | BOSS (deep, hollow): Traitor. · MASTER (cut off): Run, b— | |
| S4 19.0-22.5 | medium on the hero, eye level, slow push-in | The hero alone in the blue dark, shield shaking, breath fog. Behind him the boss with a black hole where the crystal was. No glow. | N: No glow. No warning. One heart left. | HP ♥ blinking fast |
| S4 22.5-26.0 | medium side two-shot | HEAD FAKE: the boss jerks the sword high in a huge windup; the hero flinches and dives; nothing comes. The boss holds the sword up, a low iron laugh. The hero is on the floor, wide open. | N: He learned the hero's tells. Now he fakes his own. | |
| S5 26.0-29.5 | close-up on the boss helmet, low angle, slow push-in | The boss steps in for the real strike, sword rising... the two EYE SLITS light up RED from inside; a tiny silhouette with the ember appears in one slit. | MASTER (muffled, ringing inside the helmet): Still here, boy. Left! | |
| S5 29.5-34.0 | = FRAME 1 framing (medium, low angle, slow push-in) | The hero raises the shield toward the lens, the boss's helmet glowing behind it; on the last line the shield sweeps across and COVERS the frame -> the wipe continues into 0.0, where the shield clears the lens and the chest glows again: a new fight, same helper. | N: Dodge again, or save him? | |

- Planted detail: the white sun on the hero's shield (2.0 s) -> the same sun on the master (9.5 s) = he is the hero's master.
  Second plant: the spark into the neck seam (18.2 s) -> the helmet glow (27 s).
- Wordless beat: 14.0-16.0, the helmet tilts down, the master looks up.
- Head fake: 22.5 s, the fake windup (we expect the strike, nothing comes). The crush at 17 s also fakes the master's death.
- Loop: the shield covers the lens at the end (33.6-34.0) and uncovers it at 0.0-0.3 = one continuous wipe; same camera as frame 1.
- Re-hooks: 2.0 crash, 4.5 a face in the crystal, 8.0 the white sun / "Master?", 11.0 forty heroes, 14.0 the boss looks down,
  16.0 the crystal ripped out, 19.0 no warning, 22.5 the fake, 26.0 the helmet glows, 29.5 the dive + question.

## Lines (EN = Enes's cloned voice; TR = Enes records)
| # | speaker | EN | TR | read |
|---|---|---|---|---|
| 00 | N | Why do bosses glow red before they attack? | Patronlar saldırmadan önce neden kırmızı parlar? | hook, low, tense |
| 01 | N | Every hero dodges the glow. Nobody asks who lights it. | Her kahraman ışıktan kaçar. Kimse onu kimin yaktığını sormaz. | quiet, leaning in |
| 02 | MASTER | Left! Now! | Sola! Hemen! | urgent, small + muffled |
| 03 | HERO | Master? You fell here... | Usta? Sen burada düşmüştün... | shocked, breaking |
| 04 | MASTER | Forty heroes since. I warned every one. | O günden beri kırk kahraman. Hepsini uyardım. | tired, warm |
| 05 | BOSS | Traitor. | Hain. | very deep, slow, metallic |
| 06 | MASTER | Run, b— | Kaç, evl— | cut off mid-word |
| 07 | N | No glow. No warning. One heart left. | Işık yok. Uyarı yok. Tek can kaldı. | flat, slow, each part a beat |
| 08 | N | He learned the hero's tells. Now he fakes his own. | Kahramanı okumayı öğrendi. Şimdi o kandırıyor. | cold |
| 09 | MASTER | Still here, boy. Left! | Hâlâ buradayım evlat. Sola! | breathless, a small smile in it |
| 10 | N | Dodge again, or save him? | Yine kaçar mısın, yoksa onu kurtarır mısın? | direct to the viewer |

Voice treatment: MASTER = Enes slightly older/lower, band-passed + glassy reverb (crystal) / metal ring (helmet).
BOSS = pitched down hard + iron reverb, no mouth (the helmet is empty).

## Sound + FX
- Bed: cold hall drone, brazier crackle, a slow war drum that tightens with each attack; drum and music CUT at 14.0 (wordless beat),
  heartbeat only; back at 19.0 as a thin high string; full hit at 26.0 when the slits glow.
- The glow: a rising glass hum + a breath "whoo" every pulse (the master's puff). Sword: whoosh, stone crack, debris, shake.
- The rip: metal shriek, glass crack, crunch in the fist, shards tinkling, the red hum chokes off, 0.4 s near-silence.
- Fake windup: big whoosh that stops dead, iron laugh. Helmet glow: the same glass hum, now muffled and ringing.
- Visual FX: red bloom + red floor pool + red rim on the hero (light must read), embers and dust in the air, sparks on impact,
  floor cracks decal, glass shards, the tiny spark trail into the neck seam, breath fog in the dark phase, eye-slit glow beams.
- Like toast (cta.py) at ~65 % = ~22 s, during the dark phase (top of frame); ask Enes 0.5 s or 1.5 s.

## Clipping watch (Enes spots these)
- Gauntlet around the crystal: fingers wrap outside the chest plate; the crystal travels with the fist.
- The master's hands vs the ember and his face: hands apart, ember floats between them; no hand at the mouth.
- The hero's dives/rolls: shield and sword vs the floor and his own body; the sword tip in the floor in S1 (no sinking).
- The boss sweep at 8-11 s: the blade passes a clear hand's width from the hero, never through him.
- Joint-jump + intersection checks per frame (tools/qa), as in night_freeze v3.

## Captions / comment
Pinned comment (A/B): **Dodge or save?** · TR: **Kaçar mısın, kurtarır mısın?**

## Self-check
[x] proven mould: "Why do <boss rule>?" + lore twist (a fallen knight lights the glow); every glow comes from the master
[x] frame 1 big + moving (mid-dive) + bright (red flare); only ONE game text (HP heart) besides the cover
[x] stakes (one heart) + urgency (attacks every 3-4 s) in 3 s; re-hooks every 2-4 s; head fake at 22.5 (+ fake death at 17)
[x] every beat BUT/THEREFORE (dodges too early -> therefore the boss notices -> therefore no warning -> but he fakes -> but the helmet glows); spark closes the helmet gap
[~] ~34 s; 64 words, under the ~80-90 budget on purpose: the dives, the crash, the rip and the fake are sound-driven action beats
    (no silence > 1 s except the wordless beat). Enes: no extra line.
[x] planted white sun + spark, wordless beat 14-16, loop to frame 1
[x] ending + pinned comment = A/B question
