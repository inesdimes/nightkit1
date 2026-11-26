# Why do shopkeepers buy your junk? — voice sheet (26 Nov 2026)

English = Enes's cloned voice (`tools/tts/ms.py`: N narrator, S shopkeeper = his tired-boss takes pitched +2 st, K hero), every take
checked with Whisper (`tools/tts/asr_check.py ms --pick`). **Turkish: Enes records the lines**, one m4a per line, `Kayıt (1)` = line 1.
Recipe: copy into `renders/mimic_shop/tr_voice_tts/mix` -> `TTS_DIR=../renders/mimic_shop/tr_voice_tts python tools/tts/own_prep.py ms <mix> --lines`
-> `python tools/tts/ms.py build own` -> `SUB_LANG=tr TTS_DIR=... python tools/render_seq.py examples/mimic_shop.py --prefix mstr --seqs s1,s2,s3,s4,s5`
-> `--master ../renders/mimic_shop/dukkancilar_neden_hurdani_alir_TR_seslendirme.mp4 --audio mimic_shop_tr.wav`.

| Kayıt | speaker | EN | TR (record this) | how to read |
|---|---|---|---|---|
| 1 | NARR | Why do shopkeepers buy your junk? | Tüccarlar neden hurdalarını satın alır? | HOOK: low, slow, a secret |
| 2 | SHOPKEEPER | A rusty sword? Sold, my friend. | Paslı bir kılıç mı? Satıldı, dostum. | warm, too friendly, smiling the whole time |
| 3 | NARR | He bought everything. Every bent spoon. Every broken shield. | Her şeyi alıyordu. Her eğri kaşığı. Her kırık kalkanı. | calm, a list, slight unease |
| 4 | HERO | What do you even do with all this junk? | Bütün bu hurdayla ne yapıyorsun? | casual, joking |
| 5 | SHOPKEEPER | Oh... I eat well. | Ah... İyi besleniyorum. | pleased, a little pause after Ah |
| 6 | NARR | He never blinked. And his gold was always wet. | Hiç göz kırpmıyordu. Ve altınları hep ıslaktı. | slower, the last word lands |
| 7 | HERO | Can I see the back room? | Arka odayı görebilir miyim? | unsure, quiet |
| 8 | SHOPKEEPER | There is no back room. | Arka oda yok. | flat, the smile stays |
| 9 | NARR | Mimics learned. Heroes stopped opening chests. | Mimikler insan doğasını öğrendi. Kahramanlar da sandık açmayı bıraktı. | low, matter of fact |
| 10 | NARR | But nobody ever skips the shop. | Ama kimse hurdasını satacağı dükkânı atlamaz. | almost a whisper |
