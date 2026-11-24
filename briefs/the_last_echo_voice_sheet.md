# The Last Echo: voice sheet (11 lines)

Enes records lines 1-8, 10 and 11. Betül records line 9 (the child). Use one file per line, named `vocal/The Last Echo/Kayit (n).m4a`, where n is the line number.
The film takes its timing from the takes (`tools/tts/le.py` + `examples/the_last_echo.py`), so a slower read makes the video longer but does not break it.
The current draft uses AI voices: the narrator is Kokoro converted to Enes's timbre, the characters are raw Kokoro voices.

| # | Speaker | Line | Draft window (s) | Direction |
|---|---|---|---|---|
| 1 | Narrator | What if one candle let you hear the dead again, but took their voice from you forever? | 1.45-6.37 | Warm, intimate, quiet. Small breath after "again,". |
| 2 | Narrator | Aren had saved one candle for his brother. | 6.57-9.17 | Restrained. |
| 3 | Narrator | Every time it replayed his final memory, Aren would lose more of the sound of his voice. | 9.47-14.92 | Slow on "the sound of his voice". |
| 4 | Brother | Aren... | 15.22-16.10 | Soft and natural, like an ordinary brother calling him. NOT ghostly. |
| 5 | Brother | Don't come back for me. Take them through the passage. Get them home. | 19.44-24.05 | Urgent but loving. Short pause between sentences. |
| 6 | Narrator | For years, Aren thought those knocks meant, 'Come back for me.' They didn't. His brother was showing him the way out. | 24.35-31.70 | Pause before "They didn't." |
| 7 | Narrator | Then, from beneath the same stones, a child tapped the same signal. This time, Aren understood. | 34.14-40.77 | Pause before "This time". |
| 8 | Narrator | He couldn't save his brother. But he could still do what his brother asked. | 47.82-52.04 | Gentle and warm. |
| 9 | Child (Betül) | Were you scared? | 55.29-56.31 | Quiet, small voice. |
| 10 | Aren | Yes. | 56.71-57.35 | Tired and honest, with a small relieved breath. |
| 11 | Narrator | The voice was gone. The lesson stayed. | 58.45-61.64 | Slow. Leave a pause between the two sentences. |

Sound beats (not voiced): three identical knocks at 0.30 s, in the memory (with echo) and from the child. The candle goes out at about 52.5 s, followed by silence.

After recording:
`python tools/tts/own_prep.py le "vocal/The Last Echo" --lines` -> `python tools/tts/le.py build own` -> render_parts (prefix `le`, audio `the_last_echo.wav`).
