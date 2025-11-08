# 🇹🇷 Roller Projesi - Türkçe Tweet Thread

## 📱 Thread 1: Hikaye Anlatımı (Önerilen)

### Tweet 1/8 - Açılış (Hook)
```
🤖 Bir ay önce "Wikipedia'dan otomatik video oluşturan bir AI ajanı yapabilir miyim?" diye düşünmüştüm.

Bugün projeyi açık kaynak olarak yayınlıyorum: ROLLER

İşte adım adım neler yaptım 🧵👇
```

### Tweet 2/8 - Problem
```
📌 Problem:

YouTube Shorts için içerik üretmek zor:
❌ Manuel araştırma
❌ Metin yazma
❌ Ses kaydı
❌ Video editlme
❌ Yükleme

Her video için saatler harcıyordum.
```

### Tweet 3/8 - Çözüm İdeası
```
💡 Çözüm:

Tüm süreci otomatikleştiren bir AI ajanı:

1️⃣ Trend konuları al
2️⃣ Wikipedia'dan bilgi çek
3️⃣ Video oluştur
4️⃣ YouTube'a yükle

Hedef: Tamamen otonom sistem
```

### Tweet 4/8 - Teknik Stack
```
🛠️ Kullandığım Teknolojiler:

• Google Gemini AI → Trend analizi & anlatım
• Pexels API → Arka plan videoları
• FFmpeg → Video işleme
• Flask → Web dashboard
• Python → Ana dil

Her biri belirli bir problemi çözdü.
```

### Tweet 5/8 - Zorluklar
```
🚧 Karşılaştığım Zorluklar:

1. Gemini ile Wikipedia URL bulma
   → Prompt engineering ile çözdüm

2. 60 saniye limiti
   → TTS hızını %20 artırdım

3. Markdown metin desteği
   → PIL ile custom text renderer yazdım

4. YouTube OAuth karmaşıklığı
   → Detaylı dokümantasyon hazırladım
```

### Tweet 6/8 - Özellikler
```
✨ Sonuç:

✅ Otomatik trend işleme
✅ 27 kategoriye akıllı ayırma
✅ Gemini → Edge → Bark TTS fallback
✅ YouTube Shorts otomatik upload
✅ Gerçek zamanlı dashboard
✅ Kategori bazlı video klasörleme

Tamamen açık kaynak!
```

### Tweet 7/8 - İstatistikler
```
📊 Proje İstatistikleri:

• 49 dosya commit edildi
• 9000+ satır kod
• 3 TTS servisi entegre
• 27 kategori desteği
• 100% ücretsiz & açık kaynak

Tüm API key'leri environment variable'a taşıdım.
Güvenlik öncelik! 🔒
```

### Tweet 8/8 - CTA (Call to Action)
```
🚀 Roller artık GitHub'da!

⭐️ Star: https://github.com/niyoseris/roller
📖 Türkçe README mevcut
🎥 YouTube Shorts auto-upload
🤖 Gemini AI powered

Wikipedia → YouTube Shorts
Tamamen otomatik!

#yapayZeka #otomasyon #Python #açıkKaynak #YouTubeShorts
```

---

## 📱 Thread 2: Teknik Odaklı

### Tweet 1/6
```
🤖 "Roller" projesini açık kaynak olarak yayınladım!

Wikipedia makalelerinden otomatik YouTube Shorts üreten AI ajanı.

Teknik detaylar ve mimari 🧵👇

GitHub: https://github.com/niyoseris/roller
```

### Tweet 2/6
```
🏗️ Mimari:

1. Gemini AI → Trend analizi
   • Wikipedia URL bulma
   • Kategori belirleme
   • Keyword extraction

2. Wikipedia API → İçerik çekme
3. TTS Pipeline → Ses üretimi
4. FFmpeg → Video compositing
5. YouTube API → Upload
```

### Tweet 3/6
```
🎙️ TTS Stratejisi (Fallback Chain):

1️⃣ Gemini TTS (Primary)
   → En hızlı, en kaliteli

2️⃣ Edge TTS (Fallback)
   → Gemini fail olursa

3️⃣ Bark TTS (Backup)
   → Tamamen offline

Hiçbir video kaçmaz!
```

### Tweet 4/6
```
📊 Session Management:

• JSON-based state persistence
• Real-time progress tracking
• Failed trend retry logic
• Manual trend input via dashboard

Flask dashboard ile tüm kontrolü elinizde.
```

### Tweet 5/6
```
🎨 Video Pipeline:

1. Pexels'den keyword-based video
2. Markdown-formatted text overlay
3. Scrolling animation
4. Gemini TTS audio (1.2x speed)
5. FFmpeg composite
6. <60s optimization for Shorts

Output: 1080x1920 portrait video
```

### Tweet 6/6
```
🔐 Güvenlik:

• Tüm API key'ler .env'de
• .gitignore ile sensitive files koruması
• YouTube OAuth token güvenliği
• Session files excluded

MIT License ile tamamen açık!

⭐️ https://github.com/niyoseris/roller
```

---

## 📱 Thread 3: Sonuç Odaklı (Kısa & Etkili)

### Tweet 1/4
```
🤖 Wikipedia makalelerini YouTube Shorts'a çeviren AI ajanı yaptım.

Tamamen otomatik. Tamamen açık kaynak.

İşte nasıl çalışıyor 👇
```

### Tweet 2/4
```
Sistem:

📌 Input: "ChatGPT" (trend)

🤖 AI:
→ Wikipedia URL bulur
→ Kategori belirler
→ Özet çıkarır

🎬 Video:
→ Anlatım oluşturur
→ Arka plan videosu ekler
→ YouTube'a yükler

Süre: ~3-5 dakika
```

### Tweet 3/4
```
Teknolojiler:

• Gemini AI (analysis + TTS)
• Pexels (stock videos)
• FFmpeg (processing)
• YouTube API (upload)
• Flask (dashboard)

Tümü Python ile.
Tümü ücretsiz.
```

### Tweet 4/4
```
Proje açık kaynak:

⭐️ https://github.com/niyoseris/roller
📖 Türkçe README
🎥 Auto YouTube upload
🤖 AI-powered

Star atmayı unutmayın!

#Python #AI #YouTubeShorts #açıkKaynak
```

---

## 📱 Tek Tweet Versiyonları

### Versiyon 1: Maksimum Bilgi
```
🤖 "Roller" - Wikipedia'dan otomatik YouTube Shorts üreten AI ajanı

✨ Özellikler:
• Gemini AI ile trend analizi
• 3'lü TTS fallback (Gemini→Edge→Bark)
• Otomatik YouTube upload
• 27 kategori desteği
• Gerçek zamanlı dashboard

Tamamen açık kaynak!

⭐️ https://github.com/niyoseris/roller

#yapayZeka #Python #YouTubeShorts #açıkKaynak
```

### Versiyon 2: Problem-Çözüm
```
Manuel video üretimi mi yorucu?

"Roller" ile:
✅ Trend gir
✅ AI analiz etsin
✅ Video oluşsun
✅ YouTube'a yüklensin

Hepsi otomatik. Hepsi ücretsiz.

Python + Gemini AI
Açık kaynak kod

🔗 https://github.com/niyoseris/roller

#otomasyon #AI #contentCreation
```

### Versiyon 3: Teknik & Kısa
```
🛠️ Yeni proje: Roller

Wikipedia → Gemini AI → Video → YouTube Shorts

Stack: Python, Gemini API, FFmpeg, Flask
Özellik: Auto-upload, 27 kategori, 3x TTS fallback

MIT License | Türkçe docs

⭐️ https://github.com/niyoseris/roller

#Python #AI #OpenSource
```

### Versiyon 4: Emoji Ağırlıklı
```
🤖 AI ajanı yaptım!

📚 Wikipedia makalesi
    ⬇️
🧠 Gemini AI analizi
    ⬇️
🎬 Video oluşturma
    ⬇️
📱 YouTube Shorts

Tamamen otomatik 🚀
Tamamen açık kaynak 💻

👉 https://github.com/niyoseris/roller

#yapayZeka #otomasyon #Python
```

---

## 📊 Tweet Zamanlama Önerileri

### En İyi Zaman (Türkiye)
- **Hafta İçi**: Salı-Perşembe
- **Saat**: 10:00-12:00 veya 20:00-22:00
- **Kaçınılacak**: Cuma akşam, Cumartesi gündüz

### Hashtag Stratejisi
**Türkçe:**
- #yapayZeka #yapayZekaProjesi
- #otomasyon #Python #açıkKaynak
- #YouTubeShorts #videoOtomasyon
- #kodlama #yazılım #GeminiAI

**İngilizce (global reach için):**
- #AI #MachineLearning #OpenSource
- #Python #Automation #ContentCreation

**Maksimum:** 5-7 hashtag (Twitter algoritması için optimal)

---

## 🎯 Engagement Artırma Taktikleri

### 1. Görsel Ekle
- Dashboard screenshot
- Process flow diagram
- Video example GIF
- Code snippet

### 2. İlk Yorumu Pin'le
```
📚 Dokümantasyon:
• Kurulum: [link]
• YouTube setup: [link]
• API keys: [link]

Sorularınızı GitHub Issues'da sorabilirsiniz!
```

### 3. Yanıt Stratejisi
- İlk 1 saat içinde TÜM yorumları yanıtla
- Teknik sorulara detaylı cevap ver
- Issue/PR'ları teşvik et
- Contributor'ları öv

### 4. Cross-Post
- LinkedIn'de paylaş (profesyonel kitle)
- Reddit r/Turkey, r/Python_Turkey
- Ekşi Sözlük entry'si
- Webrazzi'ye haber gönder

### 5. Follow-up Tweet'ler
**24 saat sonra:**
```
🎉 Roller 24 saatte:
• X star ⭐️
• Y fork 🔱
• Z issue/PR

Türk developer topluluğu harika! 🇹🇷

Henüz bakmadıysanız:
https://github.com/niyoseris/roller
```

---

## 📈 Başarı Metrikleri

**İyi bir ilk gün:**
- 50+ star
- 10+ fork
- 5+ issue/question
- 100+ tweet impression

**Harika bir ilk hafta:**
- 200+ star
- 25+ fork
- 10+ PR/contribution
- 1000+ tweet impression

---

## 💬 Olası Sorulara Hazır Yanıtlar

**Q: "API key'leri nereden alıyoruz?"**
A: Gemini: ai.google.dev/gemini-api, Pexels: pexels.com/api - İkisi de ücretsiz tier'da yeterli. README'de detaylı anlatım var!

**Q: "YouTube upload için ücret var mı?"**
A: Hayır! YouTube Data API günde 10.000 unit ücretsiz. Bir video upload ~1600 unit. Günde 6 video yükleyebilirsiniz bedavaya.

**Q: "Türkçe anlatım desteği var mı?"**
A: Şu an İngilizce TTS kullanıyor ama Edge TTS'de Türkçe ses var. config.py'dan force_english_tts = False yapabilirsiniz!

**Q: "Katkıda bulunabilir miyim?"**
A: Kesinlikle! CONTRIBUTING.md'de detaylar var. En çok ihtiyaç duyulan: Türkçe TTS, multi-language support, Instagram Reels entegrasyonu.

---

## 🎬 Bonus: Video Thread İdeası

Eğer kısa bir demo video çekersen:

```
🎥 "Roller" projesini 60 saniyede gösteriyorum

1. Dashboard'u aç
2. Trend ekle
3. Start'a bas
4. AI çalışsın
5. Video oluşsun
6. YouTube'a yüklensin

Hepsi bu kadar basit!

Video 👇
[video linki]

⭐️ https://github.com/niyoseris/roller
```

---

**Hangi thread/tweet formatını kullanmak istersin?**

1. **Thread 1** (Hikaye) - En engaging
2. **Thread 2** (Teknik) - Developer kitlesi için
3. **Thread 3** (Kısa) - Hızlı okunur
4. **Tek Tweet** - Maksimum reach

**Öneri:** Thread 1'i kullan, ardından 24 saat sonra Tek Tweet Versiyon 1'i paylaş.
