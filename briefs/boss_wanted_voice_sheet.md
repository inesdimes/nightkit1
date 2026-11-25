# Why Does the Final Boss Have a Help Wanted Sign? — ses kayıt föyü (Enes)

Video: `renders/boss_wanted/` (sessiz versiyon). Script: `examples/boss_wanted.py`, zamanlama: `tools/tts/bw.py`.
Her satır ayrı bir dosya: `vocal/boss_wanted/Kayit (1).m4a` … `Kayit (15).m4a` (numara = satır numarası).
Sakin ve net oku; video sonra 1.2x hızlanıyor (sesin perdesi değişmez). Satırın başında ya da sonunda uzun sessizlik bırakma.

| # | Kim | Satır | Videoda başlar (final sn) | En fazla (normal hızda) | Ton |
|---|---|---|---|---|---|
| 1 | Anlatıcı | The boss wasn't attacking. He was hiring. | 0.0 | 3.3 sn | hemen, net, kuru mizah |
| 2 | Boss | Want my job? | 3.0 | 2.4 sn | yorgun, sıradan |
| 3 | Şövalye | I came to defeat you. | 5.15 | 3.3 sn | kendinden emin |
| 4 | Anlatıcı | His health bar now showed nearly ten thousand failed fights. | 8.05 | 3.4 sn | bilgi verir gibi, "failed fights" vurgulu |
| 5 | Boss | Same arena. Same speech. Every single respawn. | 11.05 | 3.4 sn | sıkılmış, kısa kesik cümleler |
| 6 | Anlatıcı | Then he handed the knight his sword and a contract. | 14.05 | 4.6 sn | biraz hızlı |
| 7 | Şövalye | What's the pay? | 18.05 | 2.2 sn | şüpheli |
| 8 | Boss | One health bar. Infinite respawns. | 20.1 | 3.3 sn | düz, yan hakları okur gibi |
| 9 | Anlatıcı | The knight signed without reading the tiny print. | 23.05 | 4.6 sn | kuru |
| 10 | Boss | No breaks. | 27.1 | 3.4 sn | deadpan |
| 11 | Anlatıcı | The old boss finally left smiling. | 30.1 | **2.1 sn** | hafif eğlenmiş |
| 12 | Anlatıcı | His first challenger arrived before the ink dried. | 32.05 | 3.6 sn | tempo artar |
| 13 | Yeni Boss (Şövalye) | Boss wanted. | 35.25 | **0.8 sn** | eski boss'u taklit eder |
| 14 | Anlatıcı | The new knight looked exactly like him. | 36.1 | **2.0 sn** | "exactly" hafif vurgulu |
| 15 | Anlatıcı | The loop had found its next boss. | 37.95 | 2.2 sn | net punchline |

Kalın süreler sıkışık olanlar. Daha uzun bir take gelirse sonraki satırlar otomatik kayar ve video 40 sn'yi biraz geçer; sesi hızlandırmıyoruz.
Kadın satırı yok.

## Türkçe kanal (İkinci Diski Takınız) — Türkçe kayıt alırsan
`vocal/boss_wanted/türkçe/Kayit (1..15).m4a`, aynı sıra:
1 BOSS SALDIRMIYORDU. İŞE ALIM YAPIYORDU. · 2 İŞİMİ İSTER MİSİN? · 3 SENİ YENMEYE GELDİM. · 4 CAN ÇUBUĞUNDA NEREDEYSE ON BİN BAŞARISIZ DÖVÜŞ YAZIYORDU. ·
5 AYNI ARENA. AYNI KONUŞMA. HER SEFERİNDE YENİDEN DOĞUŞ. · 6 KILICINI VE BİR SÖZLEŞMEYİ ŞÖVALYEYE UZATTI. · 7 ÜCRETİ NE? · 8 BİR CAN ÇUBUĞU. SINIRSIZ YENİDEN DOĞUŞ. ·
9 ŞÖVALYE KÜÇÜK YAZILARI OKUMADAN İMZALADI. · 10 MOLA YOK. · 11 ESKİ BOSS SONUNDA GÜLÜMSEYEREK ÇIKTI. · 12 MÜREKKEP KURUMADAN İLK RAKİBİ GELDİ. ·
13 BOSS ARANIYOR. · 14 YENİ ŞÖVALYE TIPKI ONA BENZİYORDU. · 15 DÖNGÜ SIRADAKİ BOSSUNU BULMUŞTU.

## Kayıtlar gelince (Claude)
```
python tools/tts/own_prep.py bw "vocal/boss_wanted" --lines
python tools/tts/bw.py build own
python tools/render_parts.py examples/boss_wanted.py --prefix bw --audio boss_wanted.wav --out ../renders/boss_wanted/bw_1x.mp4 --parts 8
sh tools/speedup_raw.sh out/bw_video.mp4 out/boss_wanted.wav <final.mp4> <DUR/1.2>
```
