# The Last Echo v2: voice sheet (7 lines)

This sheet follows the revision brief (24 Nov). Enes records all 7 lines, one file per line, named `vocal/The Last Echo/Kayit (n).m4a`, where n is the line number.
There are no child or Aren lines in v2. The film takes its timing from the takes (`tools/tts/le.py` + `examples/the_last_echo.py`), so a slower read makes the video longer but does not break it.
The current draft uses AI voices: the narrator is Kokoro converted to Enes's timbre, the brother is Kokoro bm_daniel.

| # | Speaker | Line | Draft window (s) | Direction |
|---|---|---|---|---|
| 1 | Narrator | The last time Aren heard those three knocks, his brother was dying. | 1.59-5.80 | Quiet hook. Small pause before "his brother was dying". |
| 2 | Narrator | One candle could replay his brother's final memory. When it went out, Aren would forget the sound of his voice forever. | 6.05-13.09 | Warm, intimate. Slow on "forever". |
| 3 | Brother | Don't come back for me. Get them out. | 16.83-19.44 | An ordinary, loving brother: urgent, not ghostly. |
| 4 | Narrator | For years, Aren remembered the knocks, but blamed himself for leaving. He never understood where his brother was pointing. | 19.99-27.29 | Pause before "He never understood". |
| 5 | Narrator | Then the child made the same sound. This time, Aren saw what he had missed. | 30.08-34.90 | Pause before "This time". |
| 6 | Narrator | He couldn't reach the child from the front. So he followed the way his brother had shown him. | 38.50-43.42 | A little more drive (this is the rescue). |
| 7 | Narrator | He forgot the sound of his brother's voice. He never forgot what his brother asked him to do. | 51.60-57.44 | Slow and quiet. Leave a pause between the two sentences. |

Sound beats (not voiced): the same three knocks at 0.15 s (the child), 14.7 s (the brother, with an echo) and 28.7 s (the child). The candle dies at 49.5 s, followed by about 2 s of silence.

After recording:
`python tools/tts/own_prep.py le "vocal/The Last Echo" --lines` -> `python tools/tts/le.py build own` -> render_parts (prefix `le`, audio `the_last_echo.wav`).
