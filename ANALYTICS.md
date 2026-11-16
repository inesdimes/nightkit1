# ANALİZ & KURGU KURALLARI — Insert Disc 2

Son güncelleme: 16 Kasım 2026. Kaynak: YouTube Studio + TikTok "Video analysis" ekran görüntüleri.

---

## 1. Veriler

### YouTube Shorts
| Video | Süre | Görüntüleme | İzleyen / geçen | Ort. izleme | Abone |
|---|---|---|---|---|---|
| I Stole From The Wrong Rat (Rat King) | 60 sn | 1.073 | **%51,9** / %48,1 | 0:31 (%51) | +1 |
| He left one game after 80… ("I DON'T GET IT") | 27 sn | 1.317 | %37,7 / %62,3 | 0:17 (**%64**) | +2 |
| I was the last player online | 30 sn | ~1.100 (tahmin) | %20,1 / %79,9 | — | ? |
| If this cat was a PS1 fighter | 6 sn | 1.344 | %15,3 / **%84,7** | 0:11 (%162, döngü) | +2 |

- Trafiğin ~%96'sı Shorts akışından geliyor; aramadan gelen pay %2–4.
- Dört video da ~1.000–1.350 görüntülemelik ilk test grubunda takılıp kalmış (grafik: hızlı yükseliş, ardından düz çizgi).
- Rat King: ilk 20 saniyede %100'den ~%45'e düşüyor. 0:20'den 1:00'e kadar seyirci neredeyse hiç azalmıyor.
- He left one game: ~0:04'te ani bir kırılma var.

### TikTok
| Video | Süre | Görüntüleme | Ort. izleme | Sonuna kadar izleyen | Beğeni / yorum / paylaşım / kayıt |
|---|---|---|---|---|---|
| I DON'T GET IT | 26,8 sn | 1.192 | 6,5 sn (%24) | %7,8 | 10 / 0 / 0 / 0 |
| Cat PS1 fighter | 6 sn | 1.076 | 4,4 sn (%73) | %25,7 | 3 / 0 / 0 / 1 |
| Last player online | 30 sn | 374 | 3,1 sn (%10) | %1,9 | 4 / 1 / 0 / 1 |

- "I DON'T GET IT" retention: 0:00–0:03 arasında %100'den ~%30'a iniyor. Bu noktadan sonra eğri neredeyse düz, sonda ~%15–20 kalıyor. TikTok'a göre izleyicilerin çoğu **0:02'de** bırakıyor.
- Beğenilerin %25'i 0:01'de geliyor (açılış karesi: "HE SEARCHED FOR THE TOKEN ALL GAME..."). Ek tepeler 0:05, 0:09, 0:13 ve 0:18'de; 0:19'dan sonra hiç beğeni yok. Toplam 10 beğeni olduğu için istatistik olarak zayıf.

## 2. Teşhis
1. **Sorun içerik değil, ilk 3 saniye.** İlk 3 saniyeyi geçen izleyici videonun sonuna kadar kalıyor.
2. **Sessizlik izleyici kaybettiriyor.** "I DON'T GET IT" videosunda 0:02'de (boş sandık) ve 0:06'da (arkadaşlar gelmeden önce) sessiz anlar var. Uzun formatta komik duraklama işlevi görebilecek bu anlar, Shorts'ta izleyicinin kaydırıp gitmesine yol açıyor.
3. **Karanlık açılış kaydırılıyor.** "Last player" videosunun ilk karesi siyah, üstündeki yazı da okunamayacak kadar küçük ("SERVER STATUS / PLAYERS 2/16").
4. **Vaat ilk karede görünmüyor.** Cat videosunun konsepti "fighting game" ama ilk karede ne can barı ne "ROUND 1" yazısı ne de bir vuruş var.
5. **Etkileşim için çağrı yok.** 0 yorum, 0 paylaşım, 0 takipçi.

## 3. Kurgu kuralları (her yeni video ve her yeniden kurgu için kontrol listesi)
- [ ] **0. kare = hook:** aydınlık, kontrastlı, hareket halinde bir karakter. Yazı büyük olmalı: 5x7 font en az ×3–4 ölçekte.
- [ ] **Ses 0,0 sn'de başlıyor.** İlk cümle sorunu ya da çatışmayı söylüyor; kurulum sahnesi yok.
- [ ] **Hiç sessizlik yok.** 0,3 sn'yi geçen her boşluk SFX, müzik vuruşu ya da bir replikle dolduruluyor.
- [ ] **Videonun vaadi ilk 2 saniyede ekranda.** Örnek: hikâyede bir karşıtlık varsa ("80 HOURS · 0 TOKENS") en baştan gösteriliyor.
- [ ] **Punchline erken ve hızlı geliyor.** Kurulum ile vuruş arası en fazla ~2 sn.
- [ ] **Süre:** TikTok/Reels için 15–25 sn, YouTube Shorts için 25–40 sn. 60 saniyelik hikâyelerde ilk 20 sn sıkıştırılıyor.
- [ ] **Son kare ilk kareye bağlanıyor** (döngü). Cat videosunda kalan izleyiciler videoyu ortalama 1,6 kez izledi.
- [ ] **Finalde tek satırlık bir yorum sorusu** var (ör. "Who's the real NPC here?").
- [ ] Sabit bir seri kartı ("💿 DISC 2") kullanılıyor; abone dönüşümünü artırmak için.

## 4. Aynı hikâyeyi iki tipte render etmek (A/B)
Her hikâye iki versiyon olarak çıkar:

| | **Tip A — Hızlı kesim** | **Tip B — Hikâye kesimi** |
|---|---|---|
| Hedef | TikTok + Reels (+ Shorts testi) | YouTube Shorts (+ TikTok testi) |
| Süre | 15–22 sn | 28–40 sn |
| Açılış | Karşıtlık / sonuç ilk karede ("80 HOURS · 0 TOKENS") | Merak sorusu ilk karede ("HE SEARCHED FOR THE TOKEN ALL GAME...") |
| Tempo | Sessizlik yok; her 1,5–2 sn'de yeni bir olay | Sessizlik yok; kısa nefes anları müzik veya SFX ile dolu |
| Final | Punchline, hemen ardından döngü | Punchline, kısa bir tepki anı, döngü ve yorum sorusu |

**Ölçüm:** Her iki tip her iki platformda aynı saatte (TR 19:00–21:00) ama farklı günlerde paylaşılır. 48. saatte şu metrikler not edilir:
- YT: izleyen/geçen %, ortalama izleme süresi, izlenme yüzdesi
- TT: 3. saniyedeki retention, ortalama izleme süresi, sonuna kadar izleme oranı, yorum ve paylaşım

Hedefler: YT'de izleyen oranı **≥ %60**, TT'de 3. saniyede kalan **≥ %50** ve sonuna kadar izleme **≥ %20**.

## 5. Mevcut videolar için yeniden kurgu planı
| Video | Yapılacak |
|---|---|
| **I DON'T GET IT** (ilk sırada) | 0:02 ve 0:06'daki sessizlikler kaldırılacak. Sandık ~0:01,5'te açılacak; açılış sesi, "womp" efekti ve "EMPTY?!" eklenecek. Arkadaşlar ~0:03,5'te ayak sesi ve müzik vuruşuyla girecek. Açılış karesine "80 HOURS · 0 TOKENS" satırı eklenecek. Toplam süre 27 → ~22 sn. Son kare ilk kareye bağlanacak. Script repoda yok: video dosyası (ffmpeg ile yeniden kurgu) ya da `.py` dosyası gerekiyor. |
| **Rat King** | İlk 20 sn sıkıştırılacak ve çatışma 0. saniyeye alınacak. Tip A versiyonu ~25 sn olacak. |
| **Last player online** | Karanlık ilk karenin yerine aydınlık, büyük yazılı bir kare ve görünür bir tehdit konacak. "PLAYERS: 2/16" yazısı ekranı dolduracak. |
| **Cat PS1 fighter** | İlk karede can barları, "ROUND 1 — FIGHT!" yazısı ve hemen bir vuruş olacak. |
| **Wrong NPC** | Handoff'ta 0 görüntülemede takıldığı yazıyor; yayın durumu kontrol edilecek. Yeniden kurguda "SIDE QUEST ACTIVATED" açılışı kullanılacak. |

## 6. Eksik veriler
- "Last player online" videosunun YT retention grafiği ve ortalama izleme süresi
- TikTok "Viewers" sekmesi (trafik kaynağı, ülke dağılımı)
- Instagram Reels metrikleri
