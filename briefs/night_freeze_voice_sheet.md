# Why do NPCs stand still at night? — voice sheet (28 Nov 2026)

English: N narrator / K knight / B Bram = Enes's cloned voice (`tools/tts/nf.py`), Whisper-checked (line 05 "Hide" heard as "Hyde" = same sound;
line 08 "respawns": take 1 of the hyphenated re-clone, Whisper heard "respawns"). M Marta = Kokoro bf_emma made into a whisper (PLACEHOLDER:
Betül can record it, EN and TR).
**Turkish: Enes records N / K / B, Betül records Marta (line 4)**, one m4a per line, `Kayıt (1)` = line 1.
Recipe: copy into `renders/night_freeze/tr_voice_tts/mix` -> `TTS_DIR=../renders/night_freeze/tr_voice_tts python tools/tts/own_prep.py nf <mix> --lines`
-> `TTS_DIR=../renders/night_freeze/tr_voice_tts python tools/tts/nf.py build own`
-> `SUB_LANG=tr TTS_DIR=../renders/night_freeze/tr_voice_tts python tools/render_seq.py examples/night_freeze.py --prefix nftr --seqs s1,s2,s3,s4,s5`
-> `... --master ../renders/night_freeze/npcler_geceleri_neden_kipirdamaz_TR_seslendirme.mp4 --audio night_freeze_tr.wav`.

| Kayıt | speaker | EN | TR (record this) | how to read |
|---|---|---|---|---|
| 1 | NARR | Why do NPCs stand still at night? | NPC'ler geceleri neden kıpırdamaz? | hook: calm, low, a little ominous |
| 2 | KNIGHT | Hello? Why is nobody moving? | Merhaba? Neden kimse kıpırdamıyor? | cheerful, puzzled, loud |
| 3 | NARR | They aren't broken. They're hiding. | Bozuk değiller. Saklanıyorlar. | quiet, slow; pause before "Saklanıyorlar" |
| 4 | MARTA (Betül) | Stop. Moving. | Kıpırdama. | WHISPER through the teeth, terrified |
| 5 | NARR | It only sees what moves. | O sadece kıpırdayanı görür. | very calm, like a rule |
| 6 | KNIGHT | Hide? I'm the hero. | Saklanmak mı? Ben kahramanım. | laughing, cocky |
| 7 | NARR | But fire never stands still. | Ama ateş hiç durmaz. | low, tense |
| 8 | NARR | Every night, someone has to move. | Her gece birinin kıpırdaması gerekir. | heavy, slow, sad |
| 9 | NARR | At dawn, every NPC respawns. | Şafakta her NPC yeniden doğar. | lighter, relief |
| 10 | BRAM | Nice weather today! | Bugün hava ne güzel! | bright, too cheerful (the NPC line) |
| 11 | BRAM | Over here! | Buraya bak! | SHOUTED, waving his hat: he draws the monster's eye off the knight on purpose (plays between lines 7 and 8 in the film) |
