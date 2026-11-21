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
  This is one possible reason for the 15 % (hypothesis, to re-check with more data).

## 9. Lifetime check (17 Nov 2026, YouTube, "since publish")
| Video | Length | Views | Views in first 48 h | Watch time | Stayed / swiped | Likes | Subs | Top audience |
|---|---|---|---|---|---|---|---|---|
| I Stole From The Wrong Rat | 61 s | 1.1K | 156 (steady trickle across all 48 h) | 4.9 h | **52.6 %** / 47.4 % | 15 | +1 | US 50 %, male 13–17 |
| She Hid Her Boyfriend From 10,000… | 35 s | 1.2K | 388 | 3.4 h | 45.7 % / 54.3 % | 7 | 0 | US 26 %, male 13–17 |
| He left one game after 80 hours… | 27 s | 1.3K | 167 | 2.8 h | 37.7 % / 62.3 % | 15 | +2 | US 23 %, TR 19 %, male 13–17 |
| If this cat was a PS1 fighter | 7 s | 1.3K | 219 | 1.0 h | 15.3 % / 84.7 % | 6 | +2 | TR 45 %, female 25–34 |

Reading:
- All four stopped at ~1.1–1.3K = the Shorts test pool; none passed it. Each got one small second wave later.
- The higher the stayed % (a story with a character and a conflict), the more watch time and the more steady traffic.
  The Rat King is the only one still getting views every few hours.
- Story videos reach the target audience (English-speaking male gamers, 13–17). The cat video reached a different audience
  (Turkish women 25–34): it has no story, so it doesn't build the channel's audience.
- Guard Forgets A (15 % stayed, first hours only) sits near the cat's level; first-frame framing is one possible reason. Too early to tell.

(Observations only, not rules: keep producing and re-check as more data comes in.)

## 10. Rat King, first 14 s (re-rendered from the code, 17 Nov; no narration in this render)
Observations only, not rules.
- 0–5 s, hook: from frame 0 the Rat King (LV 99) fills the frame, red eyes; the sword slams at 0.35 s with a screen shake and the boss bar appears at ~1 s.
- At 5.0 s there is a hard cut to a bright forest, "LEVEL 1" (flashback): colour, place and stakes all reset at once.
- 5–9 s: the knight walks in and takes the cheese (+1 CHEESE at ~9 s). Little happens before the steal.
- 10–14 s: the small rat sits alone, small in a wide shot, then a close-up on its sad face.
- The retention curve falls from 100 % to ~45 % in the first ~10 s, then stays flat to the end. That fall overlaps the flashback cut and the slow steal.
- Possible things to test later (one per video): a shorter flashback setup (steal by ~6 s); keeping a hint of the boss / the stakes on screen during the flashback.

## 11. The 15 Nov posts on three platforms (snapshot 17 Nov 2026, ~19:14, read from Enes's screenshots)
Observations only, not rules. Numbers marked ~ are read off charts.

| Video (61 s) | Platform | Views | Likes / saves / shares | Retention | Audience / traffic |
|---|---|---|---|---|---|
| Never Trust The Last Save Point (posted 15 Nov 20:04) | YouTube Shorts | ~1.0K (1,094 in 48 h) | 18 likes, +1 sub, 5.1 h watch time | stayed **58.2 %** / swiped 41.8 %; curve falls to ~40 % by ~0:10, flat to ~0:55, small drop at the end | 13–17 male; US 17 %, TR 4 %, DE 2 %; Shorts feed 1.0K, other YouTube features 63, other 16 |
| Never Trust The Last Save Point | Instagram Reels | 620 (508 viewers) | 9 likes, 0 comments, 1 save, 0 shares | — | 100 % non-followers |
| Never Trust The Last Save Point ("This is me. And that... is also me.") | TikTok | 303 (21 min total play time) | 0 likes, 0 comments, 0 shares, 0 saves, 0 new followers | average watch **4.19 s** (7 % of 61 s); fully watched **1.6 %**; most viewers left at **0:01** | For You 98.4 %, profile 1.0 %, other 0.6 % |
| He Picked The Wrong NPC (posted 15 Nov 22:07) | YouTube Shorts | 492 (all in the first 48 h, most in the first hours) | 14 likes, +1 sub, 2.1 h watch time | stayed **56.2 %** / swiped 43.8 %; curve falls to ~50 % by ~0:10, then declines slowly to ~10 % at 1:00 | 13–17 male; US 38 %, UK 6 %, NL 3 %; Shorts feed 464, other 28 |
| He Picked The Wrong NPC ("One stranger said no. Then the whole street did.") | TikTok | 374 (33 min total play time) | 3 likes, 0 comments, 1 share, 1 save, 0 new followers | average watch **4.79 s** (8 % of 61 s); fully watched **1.2 %**; most viewers left at **0:02** | For You 94.7 %, other 5.3 % |
| He Picked The Wrong NPC | Instagram Reels | 122 (102 viewers) | 0 likes, 0 comments, 0 saves, 0 shares | — | — |

Reading:
- **YouTube:** both 61 s story videos keep 56–58 % "stayed", more than the 15–45 % of the shorter videos in section 9. Both curves drop to ~40–50 % in the first ~10 s and then hold, the same pattern as the Rat King (section 10): once a viewer is past the first ~10 s, most stay.
- **TikTok:** both videos hold viewers far worse than on YouTube: the median viewer is gone at 0:01–0:02 (Save Point: 4.19 s average, 1.6 % finish; NPC: 4.79 s, 1.2 %). The For You page does distribute it (94.7 % of views), so the first 2 s decide, and a 61 s runtime has little chance. This is the reason the TikTok versions are now 15 s with the hook in frame 0.
- **Instagram:** the horror video got 5× the views of the NPC video (620 vs 122); on YouTube the ratio is ~2× (1,094 vs 492). The Instagram NPC reel got no interaction at all. One possible reason (hypothesis): frame 0 of the NPC video is a wide street with two small characters and subtitle text, while the Save Point frame 0 is a close, dark corridor with a red HP bar ("DANGER"). Matches the earlier first-frame observation in section 8.
- **Conversion is ~0 everywhere:** +1 subscriber on each YouTube video, 0 followers on TikTok and Instagram. Reach alone does not build the channel yet.
- **Audience:** YouTube is mostly English-speaking 13–17 male (US 17–38 %); the Save Point video also reached TR (4 %).
- Single videos, small numbers, three different platforms: nothing here is a rule. Re-check with the 16 Nov posts (Guard Forgets A, Final Boss B) and the new 15 s TikTok cuts.

Missing: the 16 Nov posts' 48 h numbers (Enes will post them after 48 h are up).

## 12. Final Boss A vs B on YouTube (read from Enes's screenshots, 20 Nov 2026)
| Video | Age | Views | Engaged views | Unique viewers | Watch time | Avg view | Stayed / swiped | Subs |
|---|---|---|---|---|---|---|---|---|
| Final Boss A, 30.5 s ("Why Do Final Bosses NEVER Leave Their Rooms?") | 34 h | **3.0 K** ("1.8 K above normal") | 1.5 K | 625 (still processing) | 9.4 h ("6.4 h above normal") | 0:20 = **65.7 %** | **64.1 %** / 35.9 % | 0 |
| Final Boss B, 60.25 s | ~3 days | 1.6 K | 918 | 898 (still processing) | 8.3 h | 0:31 = **51.6 %** | **67.5 %** / 32.5 % | **+2** |

Reading:
- The best numbers on the channel so far. Both versions keep 64-68 % "stayed" (earlier best 56-58 %, others 15-45 %). B was "~0 views" on the evening it was posted and recovered later.
- Both retention curves **start above 100 %** (people rewatch the first seconds / loop), drop hard in the first ~7-10 s, then stay almost flat to the end (A ~55 %, B ~60 % -> ~40 %).
- Both got a **second push** a day or more after posting (a step in the views curve): YouTube tested them on a new audience and they passed.
- 30 s: more views, higher % watched. 60 s: more seconds per view (31 s vs 20 s), similar total watch time, and the only one that brought subscribers (+2).
- What is different about this video: the hook is a question gamers already have ("why do final bosses never leave their rooms?") and the answer is a story twist (the knight becomes the next boss), not a science fact. Hypothesis: relatable game tropes + a lore twist work better than explained real-world facts.
- Still small numbers (one topic, two cuts). Unique viewers are marked as still processing.

## 13. Scheduled posts, 20-21 Nov 2026 (Enes scheduled both, no numbers yet)
| Video | Scheduled (Turkey time) | Version posted |
|---|---|---|
| Why Do Final Bosses Always Have Three Phases? (`four_phases`) | 20 Nov 23:00 or 21 Nov 02:00 (Enes: one at 23:00, the other 21 Nov 02:00; which is which not stated) | 30 s final, `why_do_final_bosses_have_three_phases_30s.mp4` |
| What Happens to the Guy Whose Car You Steal? (`stolen_car`) | the other slot | v2 with 1 s cold open (THANKS GARY), `..._33s.mp4`; #GTA6 only as a hashtag in the description |

- Why these hours (Enes's decision): they target the evening of Europe (23:00 TR) and the evening of the USA (02:00 TR); earlier notes assumed a Turkish 19:00-21:00 slot. First time the channel posts at these hours, so compare against the earlier posts with that in mind.
- To do: read both at 48 h (views, engaged views, stayed %, subs, and the country split if YouTube shows it), then fill in this section. Also note whether the #GTA6 hashtag changed the first-hours views of `stolen_car`.

## 13. Lighthouse and the red-cabbage (anthocyanin) loop, first 2 days (Enes, 21 Nov 2026; views only, platform assumed YouTube)
| Video | Type | Views after ~2 days |
|---|---|---|
| Why Do Lighthouses Blink? (60 s, maritime horror, real-world fact) | real fact + horror twist | ~500 |
| Anthocyanin loop (red cabbage, 2D pixel art, science loop) | real science, no game | ~100 |
| (for comparison) Final Boss A (30 s, game trope + lore twist) | game trope | 3.0 K in 34 h (section 12) |
| (for comparison) Final Boss B (60 s, same story) | game trope | 1.6 K in ~3 days |

Reading:
- Supports the section 12 hypothesis: game tropes with a story twist get 3-6x the views of real-world fact videos (500) and ~15-30x
  the science loop without a game (100). Still a handful of videos, and only views (no stayed %, no retention curve yet).
- Missing for both: stayed / swiped %, average view duration, retention curve, subscribers. Ask Enes for the screenshots.
