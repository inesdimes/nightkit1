"""Voice for "The Last Echo" (le, 24 Nov 2026). Brief: briefs/the_last_echo.md, cue sheet: briefs/the_last_echo_voice_sheet.md.
Draft voices (Enes approved 24 Nov: AI timing now, his + Betul's own takes replace them later):
  N narrator Kokoro bm_george -> ChatterboxVC (Enes timbre) | B brother bm_daniel | A Aren am_michael | C child af_sky (pitch up)
  python tools/tts/le.py src ; <chatterbox python> tools/tts/vc.py le ; python tools/tts/le.py build vc
Own takes: python tools/tts/own_prep.py le "vocal/<folder>" --lines ; python tools/tts/le.py build own
Brief: warm, intimate, restrained narrator; the brother an ordinary familiar voice (not ghostly)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import multi
S = 1.1
VOICES = {'B': ('bm_daniel', 'en-gb'), 'A': ('am_michael', 'en-us'), 'C': ('af_sky', 'en-us')}
D = [('01', 'N', [("What if one candle let you hear the dead again,", S, -0.6, 0.5, 0), ("but took their voice from you forever?", S * 0.97, -0.8, 0.5, 0.12)]),
     ('02', 'N', [("Aren had saved one candle for his brother.", S * 0.97, -0.6, 0.5, 0)]),
     ('03', 'N', [("Every time it replayed his final memory,", S, -0.6, 0.5, 0), ("Aren would lose more of the sound of his voice.", S * 0.95, -0.8, 0.5, 0.08)]),
     ('04', 'B', [("Aren...", 0.85, 0.0, 0.0, 0)]),
     ('05', 'B', [("Don't come back for me.", 1.0, 0.0, 1.0, 0), ("Take them through the passage.", 1.02, 0.2, 1.0, 0.15), ("Get them home.", 0.92, -0.2, 1.0, 0.2)]),
     ('06', 'N', [("For years, Aren thought those knocks meant,", S, -0.6, 0.5, 0), ("'Come back for me.'", S * 0.92, -0.8, 0.5, 0.1),
                  ("They didn't.", S * 0.9, -1.0, 0.5, 0.25), ("His brother was showing him the way out.", S * 0.95, -0.8, 0.5, 0.2)]),
     ('07', 'N', [("Then, from beneath the same stones,", S, -0.6, 0.5, 0), ("a child tapped the same signal.", S * 0.97, -0.6, 0.5, 0.05),
                  ("This time, Aren understood.", S * 0.9, -0.9, 0.5, 0.3)]),
     ('08', 'N', [("He couldn't save his brother.", S * 0.95, -0.7, 0.5, 0), ("But he could still do what his brother asked.", S * 0.93, -0.8, 0.5, 0.3)]),
     ('09', 'C', [("Were you scared?", 0.95, 2.5, 0.0, 0)]),
     ('10', 'A', [("Yes.", 0.85, -0.5, 0.0, 0)]),
     ('11', 'N', [("The voice was gone.", S * 0.9, -0.8, 0.5, 0), ("The lesson stayed.", S * 0.85, -1.0, 0.5, 0.35)])]
if __name__ == '__main__': multi.main(D, VOICES, 'le')
