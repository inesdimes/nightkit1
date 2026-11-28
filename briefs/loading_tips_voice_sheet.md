# Why do loading screens show tips? — voice sheet (28 Nov 2026)

English: every speaker = Enes's cloned voice (`tools/tts/lt.py`), Whisper-checked. N narrator / K knight clean; O Bob +3 st, G goblin +5 st,
D door goblin -2 st (pitched in the build). No female lines.
**Turkish: Enes records all 14 lines**, one m4a per line, `Kayıt (1)` = line 00. Read Bob and the goblin a little higher and faster
yourself; the FX pass (`tools/tts/tr_fx.py`) can add the goblin colour afterwards, the clean version stays as `_kuru`.
Recipe: copy into `renders/loading_tips/tr_voice_tts/mix` -> `TTS_DIR=../renders/loading_tips/tr_voice_tts python tools/tts/own_prep.py lt <mix> --lines`
-> `SUB_LANG=tr TTS_DIR=../renders/loading_tips/tr_voice_tts python tools/tts/lt.py build own`
-> `SUB_LANG=tr TTS_DIR=../renders/loading_tips/tr_voice_tts python tools/render_seq.py examples/loading_tips.py --prefix lttr --seqs s1,s2,s3,s4,s5`
-> `... --master ../renders/loading_tips/yukleme_ekranlari_neden_ipucu_gosterir_TR_seslendirme.mp4 --audio loading_tips_tr.wav`.

| Kayıt | speaker | EN | TR (record this) | how to read |
|---|---|---|---|---|
| 1 | NARR | Why do loading screens show tips? | Yükleme ekranları neden ipucu gösterir? | hook: calm, clear, a little curious |
| 2 | BOB | Too fast! Slow it down! He's at the door! | Çok hızlı! Yavaşlat şunu! Kapıya geldi! | PANIC, high, fast; three short shouts |
| 3 | NARR | The tips aren't for you. They're for them. | İpuçları senin için değil. Onlar için. | dry; small pause before "Onlar için" |
| 4 | NARR | Every tip you read buys them time. | Okuduğun her ipucu onlara zaman kazandırır. | dry, like a rule |
| 5 | BOB | Chest! Torches! Dragon! Faster! | Sandık! Meşaleler! Ejderha! Çabuk! | barking orders, each word a separate shout |
| 6 | GOBLIN | Boss, the chest winked at me. | Patron, sandık bana göz kırptı. | worried, small voice, almost a whine |
| 7 | BOB | Ninety-nine percent! We made it, boys! | Yüzde doksan dokuz! Yetiştirdik çocuklar! | relief, cheering, out of breath |
| 8 | GOBLIN | Boss... where's the door? | Patron... kapı nerede? | slow dread; long pause after "Patron" |
| 9 | BOB | Places! Everybody, places! | Yerlerinize! Herkes yerine! | shout, urgent |
| 10 | DOOR | ...Creak. | ...Gıcırt. | flat, deadpan: a goblin pretending to be a door |
| 11 | KNIGHT | Huh. Nice door. Very... wooden. | Hıh. Güzel kapı. Pek bir... tahta. | puzzled, slow, squinting |
| 12 | BOB | Plus one gold? | Artı bir altın? | sheepish, a hopeful smile |
| 13 | BOB | Still hired! | Hâlâ işteyim! | whispered triumph |
| 14 | NARR | Next level's loading. Read the tips... or skip? | Sıradaki level yükleniyor. İpuçlarını okur musun... geçer misin? | dry, a wink; a real question at the end |
