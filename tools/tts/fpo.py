"""Voice for "What if every healing potion made someone forget you?" (fpo, 24 Nov 2026, Format 3.0 several voices). Brief: briefs/forget_potion.md,
line numbers = briefs/forget_potion_voice_sheet.md. Narrator N = Kokoro bm_george -> ChatterboxVC (Enes timbre). Characters raw Kokoro (brief):
  K Kaya af_heart | M Mira bf_emma | I innkeeper bm_lewis | A adventurer am_adam
  python tools/tts/fpo.py src ; <chatterbox python> tools/tts/vc.py fpo ; python tools/tts/fpo.py build vc
  Enes's own takes: tts/fpo_own/<key>_<i>.wav, then python tools/tts/fpo.py build own"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import multi
S = 1.18; P = 0.12
VOICES = {'K': ('af_heart', 'en-us'), 'M': ('bf_emma', 'en-gb'), 'I': ('bm_lewis', 'en-gb'), 'A': ('am_adam', 'en-us')}
_D = [('01', 'N', [("What if every healing potion made someone forget you?", S, -1.4, 1.5, 0)]),
      ('02', 'K', [("Stay back!", 1.1, 0.5, 1.5, 0), ("Who are you?", 1.05, 0.8, 1.0, 0.08)]),
      ('03', 'N', [("He thought the first time was a trick of the light.", S, 0, 0.5, 0)]),
      ('04', 'N', [("Then the soldier he'd saved forgot his name.", S * 0.97, -0.2, 0.5, 0)]),
      ('05', 'I', [("Rooms are for paying guests.", 1.0, -0.5, 0.5, 0)]),
      ('06', 'N', [("The innkeeper forgot his face.", S * 0.97, -0.1, 0.5, 0)]),
      ('07', 'N', [("The label had been there all along.", S * 0.92, -0.2, 0.5, 0)]),
      ('08', 'N', [("Then, beneath the old bridge,", S, 0, 0.5, 0), ("he found Mira.", S * 0.95, -0.2, 0.5, 0.06), ("The woman he loved.", S * 0.88, -0.4, 0.5, 0.14),
                   ("Dying.", S * 0.85, -0.6, 0.5, 0.16)]),
      ('09', 'N', [("One potion could save her.", S * 0.9, -0.3, 0.0, 0)]),
      ('10', 'N', [("But someone would forget her.", S * 0.92, -0.2, 0.5, 0), ("And he knew who.", S * 0.85, -0.5, 0.5, P + 0.1)]),
      ('11', 'M', [("You came back for me!", 1.02, 1.0, 1.0, 0)]),
      ('12', 'A', [("I'm sorry...", 0.9, 0.0, 0.0, 0), ("have we met?", 0.95, 0.3, 0.0, 0.15)]),
      ('13', 'N', [("She wanted to tell him everything.", S * 0.95, -0.1, 0.5, 0)]),
      ('14', 'N', [("Instead, she let him believe they'd just met.", S * 0.93, -0.3, 0.5, 0)]),
      ('15', 'M', [("Wait!", 1.0, 1.5, 2.0, 0), ("What's your name?", 1.0, 1.0, 1.5, 0.12)]),
      ('16', 'N', [("He gave her a new life.", S * 0.9, -0.2, 0.5, 0), ("Now she keeps their story for both of them.", S * 0.88, -0.5, 0.5, P + 0.05)])]
D = [(k, spk, [(tx, sp, (st - 0.6) if spk == 'N' else st, g, pause) for tx, sp, st, g, pause in ss]) for k, spk, ss in _D]
if __name__ == '__main__': multi.main(D, VOICES, 'fpo')
