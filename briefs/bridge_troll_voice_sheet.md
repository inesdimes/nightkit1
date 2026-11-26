# Why do bridge trolls want tolls? — voice sheet (26 Nov 2026)

English = Enes's cloned voice (`tools/tts/bt.py`, refs from his own takes: N narrator, T troll = his tired-boss/guardian
takes pitched -2 st, K knight). Every take checked with Whisper (`tools/tts/asr_check.py bt`).
**Turkish: Enes records these himself**: one m4a per line, **`Kayıt (1)` = line 1 (the hook) ... `Kayıt (13)` = line 13**.
He may change the TR text (then the TR dict in `tools/tts/bt.py` is updated so the subtitles match).
Recipe (folder ready: `renders/bridge_troll/tr_voice_tts/` with `mix/` + fpo/dt script copies):
  copy his files into `tr_voice_tts/mix` -> `TTS_DIR=../renders/bridge_troll/tr_voice_tts python tools/tts/own_prep.py bt <mix> --lines`
  -> same TTS_DIR: `python tools/tts/bt.py build own` (troll lines pitched -2 st, inner pauses tightened)
  -> `SUB_LANG=tr TTS_DIR=... python tools/render_seq.py examples/bridge_troll.py --prefix bttr --seqs s1,s2,s3,s4,s5` (-> seq_tr/)
  -> same env: `--master ../renders/bridge_troll/kopru_trolleri_neden_gecis_parasi_ister_TR_seslendirme.mp4 --audio bridge_troll_tr.wav`
  (the Turkish timing is new, so all 5 sequences render once; later fixes again touch one sequence)

| Kayıt | speaker | EN | TR (record this) | how to read |
|---|---|---|---|---|
| 1 | NARR | Why do bridge trolls want tolls? | Köprü trolleri neden geçiş parası ister? | HOOK: punchy, like a question you dare them to answer; weight on "tolls" / "parası" |
| 2 | TROLL | One coin. To cross. | Bir sikke. Geçmek için. | deep, slow, bored, a small pause between |
| 3 | KNIGHT | Or I cut you in half. | Yoksa seni ikiye bölerim. | cocky, a little smile |
| 4 | TROLL | Fine. Go ahead and cross. | Peki. Buyur, geç. | shrug, no anger at all |
| 5 | NARR | The knight didn't pay. The bridge did. | Şövalye ödemedi. Köprü ödedi. | calm; small pause, weight on "köprü" |
| 6 | NARR | Halfway over, the old arch cracked. | Yarı yolda eski kemer çatladı. | faster, tense on "çatladı" |
| 7 | TROLL | The king stopped paying for this bridge forty years ago. | Kral bu köprüye kırk yıl önce para vermeyi bıraktı. | strained, holding something heavy, through the teeth |
| 8 | KNIGHT | Why didn't you just say so? | Neden baştan söylemedin? | shocked, guilty |
| 9 | TROLL | You had a sword. | Elinde kılıç vardı. | quiet, tired, no blame |
| 10 | NARR | The knight emptied his purse. | Şövalye kesesini boşalttı. | calm |
| 11 | TROLL | Every coin is one stone. | Her sikke bir taş. | warm, slow |
| 12 | NARR | By dawn, the crack was gone. | Şafakta çatlak kapanmıştı. | soft |
| 13 | NARR | Trolls don't want your gold. Bridges do. | Troller altınını istemez. Köprüler ister. | short pause, last two words land |
