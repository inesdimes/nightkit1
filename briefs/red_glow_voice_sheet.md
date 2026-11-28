# Why do bosses glow red before they attack? — voice sheet (28 Nov 2026)

English: N narrator / K knight / M master / H Hollow King = Enes's cloned voice (`tools/tts/rg.py`), Whisper-checked
(04: take 0 picked by hand, Whisper's pick heard "Forty heroes six"; 06 "Run, boy!" is cut after "Run, b-" in the build).
In the video: M is filtered (glassy inside the crystal, metal ring inside the helmet), H is pitched down -6 st with an iron echo.
**Turkish: Enes records every line**, one m4a per line, `Kayıt (1)` = line 1. The FX (glass / helmet / pitch) are added in the build.
Recipe: copy into `renders/red_glow/tr_voice_tts/mix` -> `TTS_DIR=../renders/red_glow/tr_voice_tts python tools/tts/own_prep.py rg <mix> --lines`
-> `SUB_LANG=tr TTS_DIR=../renders/red_glow/tr_voice_tts python tools/tts/rg.py build own`
-> `SUB_LANG=tr TTS_DIR=../renders/red_glow/tr_voice_tts python tools/render_seq.py examples/red_glow.py --prefix rgtr --seqs s1,s2,s3,s4,s5`
-> `... --master ../renders/red_glow/patronlar_neden_kirmizi_parlar_TR_seslendirme.mp4 --audio red_glow_tr.wav`.

| Kayıt | speaker | EN | TR (record this) | how to read |
|---|---|---|---|---|
| 1 | NARR | Why do bosses glow red before they attack? | Patronlar saldırmadan önce neden kırmızı parlar? | hook: low, tense, clear (no shouting) |
| 2 | NARR | Every hero dodges the glow. Nobody asks who lights it. | Her kahraman ışıktan kaçar. Kimse onu kimin yaktığını sormaz. | quiet, leaning in; small pause between the sentences |
| 3 | MASTER (old knight) | Left! Now! | Sola! Hemen! | urgent, short, a little hoarse (an old man shouting from inside glass) |
| 4 | KNIGHT | Master? You fell here... | Usta? Sen burada düşmüştün... | shocked, the voice breaks on the second sentence |
| 5 | MASTER | Forty heroes since. I warned every one. | O günden beri kırk kahraman. Hepsini uyardım. | tired, warm, slow |
| 6 | BOSS | Traitor. | Hain. | very slow, flat, deep (it gets pitched down + echo) |
| 7 | MASTER | Run, boy! | Kaç, evlat! | SHOUTED; read the whole line, the build cuts it after "Kaç, ev-" (the crystal is crushed) |
| 8 | NARR | No glow. No warning. One heart left. | Işık yok. Uyarı yok. Tek can kaldı. | flat, slow, each part its own beat |
| 9 | NARR | He learned the hero's tells. Now he fakes his own. | Kahramanı okumayı öğrendi. Şimdi o kandırıyor. | cold |
| 10 | MASTER | Still here, boy. Left! | Hâlâ buradayım evlat. Sola! | breathless, a small smile in "buradayım"; "Sola!" sharp |
| 11 | NARR | Dodge again, or save him? | Yine kaçar mısın, yoksa onu kurtarır mısın? | straight to the viewer, a real question |
