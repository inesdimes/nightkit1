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

## 4. Yeni videolarda iki tip render (A/B)
Paylaşılmış videolar **yeniden kurgulanmayacak ve yeniden yüklenmeyecek** (reuse içerik riski). Bu A/B testi yalnızca yeni hikâyelere uygulanır: her yeni hikâye iki versiyon olarak çıkar.

| | **Tip A — Hızlı kesim** | **Tip B — Hikâye kesimi** |
|---|---|---|
| Hedef | TikTok + Reels | YouTube Shorts |
| Süre | 15–22 sn | 28–40 sn |
| Açılış | Karşıtlık ya da sonuç ilk karede | Merak sorusu ilk karede |
| Tempo | Sessizlik yok; her 1,5–2 sn'de yeni bir olay | Sessizlik yok; nefes anları müzik veya SFX ile dolu |
| Final | Punchline, ardından döngü | Punchline, tepki, döngü ve yorum sorusu |

Ölçüm: 48. saatte YT izleyen/geçen oranı ve ortalama izleme süresi, TT 3. saniyedeki retention ve sonuna kadar izleme oranı.
Hedefler: YT izleyen oranı ≥ %60; TT 3. saniyede kalan ≥ %50, sonuna kadar izleyen ≥ %20.

## 5. Paylaşılmış videolardan çıkan dersler (yeni videolara uygulanır)
| Video | Ders |
|---|---|
| I DON'T GET IT | 0:02 ve 0:06'daki sessizlik izleyiciyi kaybettirdi. Punchline daha erken gelmeli, karşıtlık ("80 HOURS · 0 TOKENS") ilk karede olmalı. |
| Rat King | Hikâye tuttu, ama giriş 20 sn sürdü. Çatışma 0. saniyede başlamalı. |
| Last player online | Karanlık ilk kare ve küçük yazı kaydırılmaya yol açtı. Horror videolarda da ilk kare aydınlık ve okunur olmalı. |
| Cat PS1 fighter | Döngü çalıştı (%162), ama vaat (can barı, "FIGHT!") ilk karede görünmüyordu. |

## 6. Analiz ritmi
- **Video başına:** 48–72. saatte tek bir kontrol. Shorts'un ilk test dalgası bu sürede biter. 7. günde son bir not alınır. Arada bakılmaz.
- **Haftalık:** Sabit bir günde (ör. Pazar) o haftanın videoları bu dosyaya eklenir.
- **Yön değişikliği:** Ancak ~15–20 video ya da 4–6 hafta veri birikince. Tek bir videoya bakarak format değiştirilmez.
- Her seferinde **tek bir değişkeni** değiştir (açılış, süre ya da tempo); aksi halde neyin işe yaradığı anlaşılmaz.

## 7. Eksik veriler
- "Last player online" videosunun YT retention grafiği ve ortalama izleme süresi
- TikTok "Viewers" sekmesi (trafik kaynağı, ülke dağılımı)
- Instagram Reels metrikleri

## 8. Posting log
| Date (TR) | Time | Video | Platform | First reading |
|---|---|---|---|---|
| 16 Nov 2026 | 20:30 | Guard Forgets — A (30 s) | ? | ~300 views, "viewed" rate 15 % (early, same evening) |
| 16 Nov 2026 | 21:21 | Final Boss — B (60 s) | ? | — |

Notes:
- These are two different stories, not an A/B pair: each video's own A/B partner (Guard Forgets B, Final Boss A) is still unposted.
- Guard Forgets A, first frame (0.0 s): the guard and the thief are small and far down the corridor, and the hook text covers the top half.
  This breaks the section 3 checklist ("0th frame: bright, contrasty, a moving character, readable"). It is the most likely cause of the 15 %.
