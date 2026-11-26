# Kayıt Noktasındaki Bekçi — Türkçe ses kayıt föyü (Enes, 26 Kasım akşamı)

Video: `renders/save_point/` · script `examples/save_point.py` · klon sesler `tools/tts/sp.py`
Her satır ayrı bir dosya: `vocal/save_point/tr/Kayit (1).m4a` … `Kayit (13).m4a` (numara = satır numarası).
Sakin ve net oku. Video sonra 1.2x hızlanıyor (perde değişmez). Satırın başında ya da sonunda uzun sessizlik bırakma.
**Metni değiştirirsen** yeni metni de yaz (altyazı birebir okuduğun cümle olacak). Cümle sayısı değişirse sorun değil.
Satır uzarsa resim kendini senin kaydına göre kaydırıyor (EN'deki gibi), video 40 sn'nin altında kalmalı.

| # | Kim | Şu anki metin | Ton |
|---|---|---|---|
| 1 | Bekçi | Yine mi? | yorgun, sıcak, alışkanlık gibi (şaşırmıyor) |
| 2 | Anlatıcı | Her öldüğünde bu ateşin başında uyanıyordu. | sakin, bilgi verir gibi |
| 3 | Anlatıcı | Yaşlı bekçi de her seferinde kepçesine bir çentik atıyordu. | sakin, "bir çentik" hafif vurgulu |
| 4 | Kahraman | Kaç oldu? | nefes nefese, meraklı |
| 5 | Bekçi | Doksan dokuz. | düz, kuru |
| 6 | Kahraman | Kimse doksan dokuz kere ölmez. | yarı gülerek, biraz gururlu |
| 7 | Bekçi | Ben öldüm. Bin on iki kere. | sessiz, yavaş, dramsız |
| 8 | Anlatıcı | Öbür yüzü doluydu. Eski çentikler. Solmuş. | yavaş, parçalar arası kısa duraklar |
| 9 | Bekçi | Sonra bir gün kalkmayı bıraktım. | çok sessiz, kendi kendine |
| 10 | Kahraman | O zaman benimkileri daha sayma. | kararlı, küçük bir gülümseme |
| 11 | Bekçi | Döndüğünde çorban sıcak olacak. | sıcak, biraz huysuz |
| 12 | Anlatıcı | Bekçi bıçağını kaldırdı. | nötr, kısa |
| 13 | Bekçi | Kalk hadi, evlat. | önce hafif iç çekiş, sonra yumuşak, şefkatli |

Kadın satırı yok.
Gelince: `own_prep.py sp "vocal/save_point/tr" --lines` (TTS_DIR = `renders/save_point/tr_voice_tts`) -> `sp.py build own` -> SUB_LANG=tr render.
