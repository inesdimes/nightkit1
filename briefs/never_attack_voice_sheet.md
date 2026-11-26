# What if you never attack the final boss? — voice sheet (26 Nov 2026)

English = Enes's cloned voice (`tools/tts/na.py`: N narrator = the spoken title, B boss = his boss takes pitched -1.5 st), every take
checked with Whisper (`tools/tts/asr_check.py na --pick`). Short lines broke in the clone ("Fine. Tea?" -> "Five, two, one",
"Kneel, mortal!" -> "Neo-Mortal"), so the EN text is a little longer than the brief; the TR text keeps the short lines.
**Turkish: Enes records the lines**, one m4a per line, `Kayıt (1)` = line 1.
Recipe: copy into `renders/never_attack/tr_voice_tts/mix` -> `TTS_DIR=../renders/never_attack/tr_voice_tts python tools/tts/own_prep.py na <mix> --lines`
-> `TTS_DIR=../renders/never_attack/tr_voice_tts python tools/tts/na.py build own`
-> `SUB_LANG=tr TTS_DIR=../renders/never_attack/tr_voice_tts python tools/render_seq.py examples/never_attack.py --prefix natr --seqs s1,s2,s3,s4,s5`
-> `... --master ../renders/never_attack/final_bossa_hic_saldirmasan_TR_seslendirme.mp4 --audio never_attack_tr.wav`.

| Kayıt | speaker | EN | TR (record this) | how to read |
|---|---|---|---|---|
| 1 | NARR | What if you never attack the final boss? | Final boss'a hiç saldırmasan ne olur? | HOOK: calm, clear, a real question |
| 2 | BOSS | Kneel before me, mortal! It's your turn. Attack! | Diz çök, ölümlü! ... Sıra sende. Saldır! | 1st part BIG and loud; short pause; then bossy, impatient |
| 3 | BOSS | Any day now... I can't move until you do! | Hadi ama... Sen oynamadan ben kıpırdayamam! | bored, then frustrated (it's the rule!) |
| 4 | BOSS | Fine. Would you like some tea? | Peki. ... Çay ister misin? | gives up (sigh); after the pause suddenly polite |
| 5 | BOSS | Three hundred years. Nobody ever stayed this long. | Üç yüz yıl. Kimse bu kadar kalmamıştı. | warm, old, a little laugh, touched |
| 6 | BOSS | Every hero hit me in the first second. You stayed. | Her kahraman ilk saniyede vurdu. Sen kaldın. | quiet, honest; "Sen kaldın." soft, almost thankful |
| 7 | BOSS | Oh no... not again. | Eyvah... yine mi? | looks up at the counter, he knows what is coming |
| 8 | BOSS | Kneel before me, mortal! | Diz çök, ölümlü! | EXACTLY like line 2, big (the game restarted) |
| 9 | BOSS | Hey... want some tea again? | Psst... yine çay ister misin? | WHISPER, conspiratorial, a smile in the voice |
