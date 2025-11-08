# 🤖 Roller - Yapay Zeka Destekli Video Oluşturucu

**Wikipedia makalelerini otomatik olarak ilgi çekici YouTube Shorts videolarına dönüştüren otonom yapay zeka ajanı.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Google Gemini](https://img.shields.io/badge/AI-Gemini%202.5-orange.svg)](https://ai.google.dev/)

[English](README.md) | **Türkçe**

---

## ✨ Özellikler

### 🎬 **Otomatik Video Üretimi**
- **Yapay Zeka Destekli Anlatım**: Google Gemini TTS kullanarak yüksek kaliteli metin-konuşma (60 saniyenin altındaki videolar için 1.2x hız)
- **Çoklu TTS Desteği**: Gemini TTS → Edge TTS → Bark TTS yedekleme zinciri
- **Dinamik Metin Katmanı**: Markdown formatında güzel kaydırmalı metin animasyonu
- **Akıllı Video Seçimi**: Pexels API'den trend anahtar kelimelerine uygun rastgele arka plan videoları
- **YouTube Shorts Uyumlu**: Dikey format (1080x1920), mobil görüntüleme için optimize

### 🎯 **Akıllı Trend İşleme**
- **Google Gemini AI**: Trendleri analiz ederek Wikipedia URL'lerini bulur ve kategorileri belirler
- **27 Kategori**: Otomatik kategorizasyon (Spor, Bilim, Eğlence, vb.)
- **Manuel Trend Girişi**: Özel trendler eklemek için web kontrol paneli
- **Oturum Yönetimi**: İlerlemeyi, işlenmiş trendleri ve hataları takip eder
- **Akıllı Yeniden Deneme**: Başarısız trendleri atlar ve işlemeye devam eder

### 🚀 **YouTube Otomasyonu**
- **YouTube Shorts'a Otomatik Yükleme**: Videolar oluşturulduktan sonra otomatik yüklenir
- **OAuth2 Kimlik Doğrulama**: Güvenli Google API entegrasyonu
- **Kategori Klasörleri**: Videolar `output_videos/` içinde kategorilere göre düzenlenir
- **Metadata Yönetimi**: Otomatik oluşturulan başlık ve açıklamalar

### 📊 **Gerçek Zamanlı Kontrol Paneli**
- **Web Arayüzü**: `http://localhost:5001` adresinde güzel, responsive kontrol paneli
- **Canlı İstatistikler**: Makaleler, videolar, YouTube yüklemeleri takibi
- **Trend İlerlemesi**: Trend durumlarıyla görsel ilerleme çubuğu (⏳ beklemede, 🔄 işleniyor, ✅ başarılı, ❌ başarısız)
- **Video Galerisi**: Videoları doğrudan kontrol panelinde oynatma, kategorilere göre düzenlenmiş
- **Oturum Kontrolleri**: Başlat, duraklat, sıfırla özellikleri

### 🛠️ **Geliştirici Dostu**
- **Yapılandırılabilir**: `config.py` ile kapsamlı ayarlar
- **Loglama**: Hata ayıklama için kapsamlı kayıt tutma
- **Hata Yönetimi**: Sağlam hata kurtarma ve raporlama
- **Otomatik Yenileme**: Kontrol paneli her 5 saniyede güncellenir

---

## 🚀 Hızlı Başlangıç

### Gereksinimler

- Python 3.8+
- FFmpeg (video işleme için)
- Google Gemini API anahtarı
- Pexels API anahtarı (arka plan videoları için)
- YouTube API kimlik bilgileri (opsiyonel, otomatik yükleme için)

### Kurulum

1. **Depoyu klonlayın**
```bash
git clone https://github.com/niyoseris/roller.git
cd roller
```

2. **Sanal ortam oluşturun**
```bash
python3 -m venv venv
source venv/bin/activate  # Windows'ta: venv\Scripts\activate
```

3. **Bağımlılıkları yükleyin**
```bash
pip install -r requirements.txt
```

4. **API anahtarlarını yapılandırın**
```bash
cp .env.example .env
# .env dosyasını düzenleyin ve API anahtarlarınızı ekleyin:
# - GEMINI_API_KEY (gerekli)
# - PEXELS_API_KEY (videolar için gerekli)
# - ROLL_WIKI_SECRET (makale gönderimi için gerekli)
# - TWITTER kimlik bilgileri (opsiyonel)
```

5. **Uygulamayı çalıştırın**
```bash
python3 main.py
```

6. **Kontrol panelini açın**
```
http://localhost:5001
```

---

## 📖 Kullanım Kılavuzu

### Trend Ekleme

1. Kontrol panelini `http://localhost:5001` adresinden açın
2. "Manuel Trend Ekle" bölümüne trendleri girin (her satıra bir tane):
```
ChatGPT
NBA Finalleri
İklim Değişikliği
Taylor Swift
```
3. **"🚀 Ekle ve Başlat"** butonuna tıklayın
4. Sihrin gerçekleşmesini izleyin! ✨

### Nasıl Çalışır

```
Kullanıcı Girişi → Gemini AI Analizi → Wikipedia Çekme → Video Oluşturma → YouTube Yükleme
       ↓                ↓                    ↓                  ↓                  ↓
    Trendler      URL + Kategori          Özet            Anlatım           Otomatik
                  + Anahtar Kelimeler     + Metin         + Video           Shorts
```

**İşleme Hattı:**
1. **AI Analizi**: Gemini her trend için Wikipedia URL'sini ve kategorisini bulur
2. **İçerik Çekme**: Wikipedia API'den makale özetini alır
3. **Video Oluşturma**:
   - Anlatım sesi oluşturur (Gemini/Edge/Bark TTS)
   - Pexels'den eşleşen arka plan videosu çeker
   - Markdown destekli kaydırmalı metin katmanı oluşturur
   - Ses + video + metin birleştirir
4. **YouTube Yükleme**: YouTube Short olarak otomatik yükler (etkinse)
5. **Kontrol Paneli Güncelleme**: Gerçek zamanlı ilerleme takibi

---

## ⚙️ Yapılandırma

### Ana Ayarlar (`config.py`)

```python
# Zamanlama
REQUEST_DELAY = 30  # Trend işleme arasındaki saniye
CYCLE_INTERVAL = 3600  # Döngüler arası saniye

# Özellikler
VIDEO_ENABLED = True  # Video oluşturmayı etkinleştir
YOUTUBE_ENABLED = True  # YouTube yüklemeyi etkinleştir
TWITTER_ENABLED = True  # Twitter paylaşımını etkinleştir

# Video Ayarları
VIDEO_SETTINGS = {
    'scroll_speed': 350,      # Metin kaydırma hızı (px/s)
    'font_size': 42,          # Metin boyutu
    'video_volume': 0.0,      # Arka plan ses seviyesi (0.0 = sessiz)
    'force_english_tts': True # Her zaman İngilizce TTS kullan
}
```

### YouTube Kurulumu (Opsiyonel)

Detaylı talimatlar için **[docs/YOUTUBE_SETUP.md](docs/YOUTUBE_SETUP.md)** dosyasına bakın.

**Hızlı adımlar:**
1. Google Cloud projesi oluşturun
2. YouTube Data API v3'ü etkinleştirin
3. `youtube_credentials.json` dosyasını indirin
4. İlk OAuth akışını çalıştırın

---

## 📂 Proje Yapısı

```
roller/
├── main.py                 # Ana uygulama giriş noktası
├── config.py              # Yapılandırma ayarları
├── dashboard.py           # Flask web kontrol paneli
├── gemini_analyzer.py     # Gemini AI entegrasyonu
├── video_creator.py       # Video oluşturma motoru
├── youtube_uploader.py    # YouTube Shorts yükleyici
├── session_manager.py     # Oturum durum yönetimi
├── text_to_speech.py      # TTS oluşturma
├── templates/
│   └── dashboard.html     # Kontrol paneli UI
├── output_videos/         # Oluşturulan videolar (kategoriye göre)
│   ├── Sports/
│   ├── Science/
│   └── ...
├── .env.example          # Ortam değişkenleri şablonu
├── requirements.txt      # Python bağımlılıkları
├── README.md            # İngilizce README
└── README_TR.md         # Bu dosya
```

---

## 🎨 Video Çıktısı

**Format Özellikleri:**
- **Çözünürlük**: 1080x1920 (9:16 dikey)
- **Süre**: <60 saniye (Shorts için optimize)
- **Ses**: 1.2x hızda İngilizce anlatım
- **Video**: Yüksek kaliteli Pexels görüntüleri
- **Metin**: Markdown formatında kaydırmalı katman
- **Çıktı**: `output_videos/{Kategori}/{trend}_shorts.mp4`

---

## 🔑 Gerekli API Anahtarları

| Servis | Amaç | Gerekli | Anahtar Alın |
|---------|---------|----------|---------|
| **Gemini API** | AI analizi & TTS | ✅ Evet | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| **Pexels API** | Arka plan videoları | ✅ Evet | [Pexels API](https://www.pexels.com/api/) |
| **Roll.Wiki** | Makale gönderimi | ✅ Evet | [roll.wiki](https://roll.wiki/) ile iletişime geçin |
| **YouTube API** | Otomatik yükleme | ⚠️ Opsiyonel | [Google Cloud Console](https://console.cloud.google.com/) |
| **Twitter API** | Tweet paylaşımı | ⚠️ Opsiyonel | [Twitter Developer Portal](https://developer.twitter.com/) |

---

## 📊 Kategoriler (Toplam 27)

```
Mimarlık    Sanat       İş          Kültür      Dans
Ekonomi     Eğitim      Mühendislik Eğlence     Çevre
Moda        Film        Yemek       Coğrafya    Tarih
Edebiyat    Tıp         Müzik       Felsefe     Siyaset
Psikoloji   Din         Bilim       Spor        Teknoloji
Tiyatro     Ulaşım
```

---

## 🐛 Sorun Giderme

### Yaygın Sorunlar

**1. "GEMINI_API_KEY not found"**
- `.env.example` dosyasından `.env` dosyası oluşturun
- Gemini API anahtarınızı ekleyin

**2. "FFmpeg not found"**
- FFmpeg'i yükleyin: `brew install ffmpeg` (Mac) veya [ffmpeg.org](https://ffmpeg.org/) adresinden indirin

**3. "Pexels API rate limit"**
- Ücretsiz katman: 200 istek/saat
- Bekleyin veya ücretli plana yükseltin

**4. Videolar oluşmuyor**
- Loglardaki TTS yedekleme zincirini kontrol edin
- Pexels API anahtarını doğrulayın
- FFmpeg'in yüklü olduğundan emin olun

**5. YouTube yükleme başarısız**
- `youtube_credentials.json` dosyasının mevcut olduğunu kontrol edin
- OAuth akışını yeniden çalıştırın: `python3 youtube_uploader.py`
- API kotasını doğrulayın (10.000 birim/gün)

---

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen:

1. Depoyu fork edin
2. Özellik dalı oluşturun (`git checkout -b feature/harika-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -m 'feat: Harika özellik ekle'`)
4. Dalı push edin (`git push origin feature/harika-ozellik`)
5. Pull Request açın

Detaylı bilgi için [CONTRIBUTING.md](CONTRIBUTING.md) dosyasına bakın.

---

## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır - detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

## 🙏 Teşekkürler

- **Google Gemini** - AI analizi ve TTS için
- **Pexels** - Yüksek kaliteli stok videolar için
- **Microsoft Edge TTS** - Yedek anlatım için
- **Suno AI Bark** - Yerel TTS yedekleme için
- **Roll.Wiki** - Makale özetleme platformu için

---

## 📮 İletişim & Destek

- **Sorunlar**: [GitHub Issues](https://github.com/niyoseris/roller/issues)
- **Tartışmalar**: [GitHub Discussions](https://github.com/niyoseris/roller/discussions)

---

**❤️ ve 🤖 AI ile yapıldı**

---

## 🔮 Yol Haritası

- [ ] Çok dilli destek
- [ ] Özel video şablonları
- [ ] Instagram Reels desteği
- [ ] TikTok otomatik yükleme
- [ ] Ses klonlama entegrasyonu
- [ ] Gelişmiş video efektleri
- [ ] Toplu işleme modu
- [ ] Harici entegrasyonlar için REST API

---

## 💡 İpuçları

### Performans
- İlk çalıştırmada Bark TTS modelleri indirilir (~2GB)
- Gemini TTS en hızlı ve kaliteli seçenektir
- Pexels API ücretsiz katmanı 200 istek/saat sınırlıdır

### Güvenlik
- `.env` dosyanızı asla GitHub'a yüklemeyin
- API anahtarlarınızı düzenli olarak rotasyona tabi tutun
- YouTube OAuth token'larını güvenli tutun

### Özelleştirme
- `config.py` içindeki video ayarlarını değiştirin
- Dashboard tema renklerini `templates/dashboard.html` içinden düzenleyin
- `video_creator.py` içinde video efektleri ekleyin

---

## 📺 Örnek Videolar

Projenin oluşturduğu örnek videolar için [output_videos/](output_videos/) klasörüne bakın.

Her video şunları içerir:
- ✅ Profesyonel anlatım
- ✅ İlgili arka plan görüntüleri
- ✅ Kaydırmalı markdown metin
- ✅ YouTube Shorts optimizasyonu
- ✅ Otomatik kategorizasyon

---

## ⚡ Hızlı Komutlar

```bash
# Uygulamayı başlat
python3 main.py

# Testleri çalıştır
python3 -m pytest tests/

# Tek bir trend test et
python3 tests/test_manual_trend.sh

# YouTube kimlik doğrulama test et
python3 youtube_uploader.py

# Gemini API test et
python3 tests/test_gemini_trends.py
```

---

**Başarılar! 🚀**
