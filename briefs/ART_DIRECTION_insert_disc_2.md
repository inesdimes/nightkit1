---
name: insert-disc-2-art-direction
description: Art direction for procedural Blender shorts set in the hand-painted medieval world of Insert Disc 2.
---
(Enes, 28 Nov 2026 - his doc, kept verbatim for reference; test built in both engines: examples/art_test.py + blender/art_test.py,
shared choreography examples/art_test_chor.py, renders in renders/art_test/ incl. a side-by-side comparison.)

Build a hand-painted medieval PS1 world for vertical comedy shorts.
The audience should recognize the recurring cast and understand the
physical joke on a phone screen, even with the sound off.

Character design
- Give each recurring character three recognition cues: a silhouette
  feature, a signature color, and a prop or costume piece that can act.
- For the knight, use a squat silhouette, a bent ochre plume, and a
  loose visor that slips over his eyes. Keep these cues across episodes.
- Give scene partners a different posture and rhythm. The instructor
  stands tall, feet together, and demonstrates each move precisely.
- Pose the head, hands, and torso around one clear intention per beat.
  Hold the reaction long enough for the viewer to catch it.

Surfaces and color
- Start with large painted color shapes. Add a few marks that belong
  to the object: thumb wear on a shield grip, a knot in a hurdle,
  chipped paint where the knight's visor hits his helmet.
- Generate reusable painted texture atlases with Python when needed.
  Anchor marks to the object so they stay still during movement.
- Keep the background quieter than the action. Reserve the strongest
  color contrast for the character, prop, or obstacle carrying the joke.

Camera and readability
- Compose for 9:16 from the start. Keep the face, the acting hand,
  and the object it acts on readable at phone size.
- For a physical gag, show the cause and the reaction in the same
  frame whenever possible. Give moving silhouettes clear space.
- Check a frame at the actual working resolution before adding grain,
  dithering, or fine texture. Keep effects that preserve the acting.
