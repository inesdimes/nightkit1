"""Voice for "What if the dragon was stealing the king's taxes back?" (dt, 23 Nov 2026, Format 3.0 several voices). Brief: briefs/dragon_taxes.md,
line numbers = briefs/dragon_taxes_voice_sheet.md. Narrator N = Kokoro bm_george -> ChatterboxVC (Enes timbre). Characters raw Kokoro (brief),
PLACEHOLDERS until Enes records them:
  K Knight am_adam | D dragon bm_george -7 st (cave echo is added in the film mix) | W old woman bf_emma | C captain bm_lewis
  python tools/tts/dt.py src ; <chatterbox python> tools/tts/vc.py dt ; python tools/tts/dt.py build vc
  Enes's own takes: tts/dt_own/<key>_<i>.wav, then python tools/tts/dt.py build own"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import multi
S = 1.18
VOICES = {'K': ('am_adam', 'en-us'), 'D': ('bm_george', 'en-gb'), 'W': ('bf_emma', 'en-gb'), 'C': ('bm_lewis', 'en-gb')}
_D = [('01', 'N', [("What if the dragon was stealing the king's taxes back?", S, -1.0, 1.5, 0)]),
      ('02', 'W', [("That's our winter tax.", 0.98, -1.2, 1.0, 0)]),
      ('03', 'K', [("The dragon stole it.", 1.05, -0.8, 1.0, 0)]),
      ('04', 'D', [("No.", 0.85, -7.0, 2.0, 0), ("The king did.", 0.85, -7.0, 2.0, 0.25)]),
      ('05', 'N', [("For years, it had robbed the royal tax wagons.", S, 0, 0.5, 0)]),
      ('06', 'W', [("We starved", 0.95, -1.2, 1.0, 0), ("while the king grew rich.", 0.95, -1.4, 1.0, 0.1)]),
      ('07', 'N', [("Then the king's soldiers arrived.", S * 0.95, -0.3, 0.5, 0)]),
      ('08', 'C', [("Kill the beast.", 1.05, -0.5, 1.5, 0), ("Bring back what belongs to the crown.", 1.08, -0.5, 1.5, 0.15)]),
      ('09', 'N', [("The quest was simple.", S * 0.95, 0, 0.5, 0), ("Slay the dragon.", S * 0.88, -0.4, 0.5, 0.12)]),
      ('10', 'K', [("I found the real thief.", 1.0, -1.0, 1.0, 0)]),
      ('11', 'D', [("Then stand with them.", 0.85, -7.0, 2.0, 0)]),
      ('12', 'N', [("By dawn, the village had its gold back.", S, 0, 0.5, 0)]),
      ('13', 'W', [("This time,", 1.0, -1.0, 1.0, 0), ("we keep what we earn.", 1.0, -1.0, 1.0, 0.08)]),
      ('14', 'N', [("And the dragon kept watch over the road.", S * 0.95, -0.2, 0.5, 0)]),
      ('15', 'N', [("Turns out,", S, 0, 0.5, 0), ("the monster had been guarding them all along.", S * 0.92, -0.4, 0.5, 0.06)])]
D = [(k, spk, [(tx, sp, (st - 0.6) if spk == 'N' else st, g, pause) for tx, sp, st, g, pause in ss]) for k, spk, ss in _D]
if __name__ == '__main__': multi.main(D, VOICES, 'dt')
