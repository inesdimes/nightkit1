"""Voice for "The Last Echo" (le, 24 Nov 2026; v2 script = Enes's revision brief, 7 lines, narrator + brother only). Brief: briefs/the_last_echo.md, cue sheet: briefs/the_last_echo_voice_sheet.md.
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
D = [('01', 'N', [("The last time Aren heard those three knocks,", S, -0.6, 0.5, 0), ("his brother was dying.", S * 0.92, -0.9, 0.5, 0.05)]),
     ('02', 'N', [("One candle could replay his brother's final memory.", S, -0.6, 0.5, 0), ("When it went out, Aren would forget the sound of his voice forever.", S * 0.95, -0.8, 0.5, 0.2)]),
     ('03', 'B', [("Don't come back for me.", 1.0, 0.0, 1.0, 0), ("Get them out.", 0.95, 0.2, 1.0, 0.2)]),
     ('04', 'N', [("For years, Aren remembered the knocks,", S, -0.6, 0.5, 0), ("but blamed himself for leaving.", S * 0.95, -0.8, 0.5, 0.05),
                  ("He never understood where his brother was pointing.", S * 0.95, -0.8, 0.5, 0.25)]),
     ('05', 'N', [("Then the child made the same sound.", S, -0.6, 0.5, 0), ("This time, Aren saw what he had missed.", S * 0.92, -0.8, 0.5, 0.3)]),
     ('06', 'N', [("He couldn't reach the child from the front.", S, -0.6, 0.5, 0), ("So he followed the way his brother had shown him.", S * 0.95, -0.8, 0.5, 0.2)]),
     ('07', 'N', [("He forgot the sound of his brother's voice.", S * 0.93, -0.8, 0.5, 0), ("He never forgot what his brother asked him to do.", S * 0.9, -0.9, 0.5, 0.35)])]
if __name__ == '__main__': multi.main(D, VOICES, 'le')
