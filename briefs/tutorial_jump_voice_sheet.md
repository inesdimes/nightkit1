# Why do tutorials make you jump? — voice sheet (27 Nov 2026)

English = Enes's cloned voice (`tools/tts/tj.py`: N narrator <- his narrator takes, K knight <- his knight takes,
I instructor <- his boss takes pitched UP 2 st = thin and strict). Every take checked with Whisper (`asr_check.py tj --pick`): all 10 exact.
**Turkish: Enes records the lines**, one m4a per line, `Kayıt (1)` = line 1 (line 00 = the spoken title).
Recipe: copy into `renders/tutorial_jump/tr_voice_tts/mix` -> `TTS_DIR=../renders/tutorial_jump/tr_voice_tts python tools/tts/own_prep.py tj <mix> --lines`
-> `TTS_DIR=../renders/tutorial_jump/tr_voice_tts python tools/tts/tj.py build own`
-> `SUB_LANG=tr TTS_DIR=../renders/tutorial_jump/tr_voice_tts python tools/render_seq.py examples/tutorial_jump.py --prefix tjtr --seqs s1,s2,s3,s4,s5`
-> `... --master ../renders/tutorial_jump/egitim_bolumleri_neden_hep_ziplatir_TR_seslendirme.mp4 --audio tutorial_jump_tr.wav`.
(The picture re-times itself from the takes; all 5 sequences must be re-rendered for the TR version.)

| Kayıt | speaker | EN | TR (record this) | how to read |
|---|---|---|---|---|
| 1 | NARR | Why do tutorials make you jump? | Eğitim bölümleri neden hep zıplatır? | HOOK: calm, clear, a real question |
| 2 | NARR | One jump opens the gate. Watch the counter. | Tek zıplama kapıyı açar. Sayaca bak. | dry, matter-of-fact; "Sayaca bak." a small hint |
| 3 | KNIGHT | See? There's a shortcut in every tutorial. | Gördün mü? Her eğitimde bir kestirme vardır. | cocky, grinning, pleased with himself |
| 4 | INSTR | That was the easy one. The next one's higher. | O kolaydı. Sıradaki daha yüksek. | strict teacher, a little annoyed, still calm |
| 5 | NARR | Three hurdles down. The counter still reads zero. | Üç engel gitti. Sayaç hâlâ sıfır. | dry; tiny pause before "sıfır" |
| 6 | INSTR | Stop. I'll show you how it's done. | Dur. Nasıl yapıldığını göstereyim. | "Dur." sharp, hand up; then proud, the expert |
| 7 | KNIGHT | Good. Stand right there. | Güzel. Tam orada dur. | slow, smiling, a trap; he does NOT slow down |
| 8 | INSTR | Wait. That counted? | Bir dakika. Bu sayıldı mı? | sitting on the ground, confused, almost offended |
| 9 | NARR | The next lesson needs two jumps. | Sıradaki ders iki zıplama istiyor. | dry, ominous; weight on "iki" |
| 10 | KNIGHT | Want to try that twice? | Bunu iki kere denemek ister misin? | sideways glance, friendly-evil grin |
