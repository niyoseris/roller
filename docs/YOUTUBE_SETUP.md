# 📺 YouTube Shorts Otomatik Upload Kurulumu

## 🎯 Özellikler

- ✅ Oluşturulan videolar otomatik olarak YouTube Shorts'a yüklenir
- ✅ Otomatik `#Shorts` hashtag ekleme
- ✅ Trend bazlı başlık ve açıklama
- ✅ Kategori bazlı etiketleme
- ✅ OAuth2 kimlik doğrulama (güvenli)

## 📋 Ön Gereksinimler

1. Google Cloud Console hesabı
2. YouTube kanalı
3. Python bağımlılıkları:
   ```bash
   pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

## 🚀 Adım 1: Google Cloud Console Kurulumu

### 1.1 Proje Oluşturma
1. [Google Cloud Console](https://console.cloud.google.com/) adresine gidin
2. Yeni proje oluşturun veya mevcut projeyi seçin
3. Proje adını girin (örn: "Agentic Trend Bot")

### 1.2 YouTube Data API v3 Etkinleştirme
1. Sol menüden **APIs & Services** > **Library** seçin
2. "YouTube Data API v3" aratın
3. **Enable** butonuna tıklayın

### 1.3 OAuth 2.0 Credentials Oluşturma
1. Sol menüden **APIs & Services** > **Credentials** seçin
2. **+ CREATE CREDENTIALS** butonuna tıklayın
3. **OAuth client ID** seçin
4. **Application type**: **Desktop app** seçin
5. İsim girin (örn: "Trend Bot Desktop")
6. **CREATE** butonuna tıklayın

### 1.4 Credentials İndirme
1. Oluşturulan credential'ın yanındaki **Download** ikonuna tıklayın
2. İndirilen JSON dosyasını projenizin kök dizinine taşıyın
3. Dosya adını `youtube_credentials.json` olarak değiştirin

## 🔧 Adım 2: Uygulama Kurulumu

### 2.1 Config Dosyasını Ayarlama
`config.py` dosyasında YouTube upload'u etkinleştirin:
```python
# YouTube Configuration
YOUTUBE_ENABLED = True  # Set to False to disable YouTube Shorts upload
```

### 2.2 İlk Kimlik Doğrulama
İlk çalıştırmada OAuth flow başlatılacak:

```bash
python3 main.py
```

1. Tarayıcınızda otomatik olarak Google giriş sayfası açılacak
2. YouTube hesabınızı seçin
3. "Allow" butonuna tıklayarak izinleri onaylayın
4. "The authentication flow has completed" mesajını gördükten sonra tarayıcıyı kapatabilirsiniz

**Not:** İlk kimlik doğrulamadan sonra `youtube_token.pickle` dosyası oluşturulacak ve sonraki çalıştırmalarda kullanılacak.

## 📊 Video Upload Ayarları

### Video Metadata
Videolar aşağıdaki metadata ile yüklenir:

- **Title**: `{Trend} - Quick Explainer`
- **Description**: İlk 200 karakter + `#Shorts` hashtag
- **Tags**: trend adı, "trending", "shorts", kategori, "news"
- **Category**: config.py'den alınır (default: 22 - People & Blogs)
- **Privacy**: Public
- **Shorts Flag**: Otomatik `#Shorts` eklenir

### Kategori Kodları
YouTube kategori ID'leri:
- **22**: People & Blogs
- **24**: Entertainment
- **25**: News & Politics
- **26**: How-to & Style
- **27**: Education
- **28**: Science & Technology

`config.py` içinde değiştirebilirsiniz:
```python
VIDEO_SETTINGS = {
    'youtube_category': '28',  # Science & Technology
    # ... diğer ayarlar
}
```

## 🔒 Güvenlik Notları

1. **youtube_credentials.json**: Bu dosyayı asla GitHub'a yüklemeyin! `.gitignore` dosyasına ekleyin:
   ```
   youtube_credentials.json
   youtube_token.pickle
   ```

2. **Token Yenileme**: Token otomatik olarak yenilenir, manuel müdahale gerekmez

3. **İzinler**: Uygulama sadece video yükleme izni ister (`youtube.upload` scope)

## 📈 Kullanım

### Otomatik Upload
Video oluşturma etkinse, her trend için otomatik olarak:
1. Video oluşturulur
2. Kategori klasörüne kaydedilir
3. YouTube Shorts'a yüklenir
4. Upload URL loglara yazılır

### Log Çıktısı
```
✅ Video created: output_videos/Technology/ChatGPT_shorts.mp4
📺 Uploading to YouTube Shorts...
Upload progress: 50%
Upload progress: 100%
✅ YouTube Shorts uploaded: https://youtube.com/shorts/abc123xyz
```

### Manuel Upload (Gerekirse)
```python
from youtube_uploader import YouTubeUploader

uploader = YouTubeUploader()
uploader.authenticate()

video_id = uploader.upload_video(
    video_path="output_videos/Sports/nba_shorts.mp4",
    title="NBA Finals - Quick Explainer",
    description="Latest NBA news! #Shorts",
    tags=["NBA", "Basketball", "Sports"],
    category_id="17",  # Sports
    privacy_status="public",
    is_shorts=True
)
```

## 🔄 YouTube Shorts URL

Upload edilen videoların URL'leri iki formatta çalışır:
- Regular: `https://youtube.com/watch?v={video_id}`
- Shorts: `https://youtube.com/shorts/{video_id}`

Her iki link de aynı videoya gider, ancak Shorts URL'si mobil cihazlarda Shorts feed'inde açılır.

## ⚠️ Kota Limitleri

YouTube Data API v3 günlük kota limiti vardır:
- **Default**: 10,000 units/day
- **Video Upload**: ~1,600 units
- **Günlük upload limiti**: ~6 video

Daha fazla video yüklemek için:
1. [Google Cloud Console](https://console.cloud.google.com/) > **APIs & Services** > **Quotas**
2. "YouTube Data API v3" seçin
3. Kota artışı için başvuru yapın

## 🐛 Sorun Giderme

### "Credentials file not found"
- `youtube_credentials.json` dosyasının proje kök dizininde olduğundan emin olun

### "Authentication failed"
1. `youtube_token.pickle` dosyasını silin
2. Uygulamayı yeniden başlatın
3. OAuth flow'u tekrar tamamlayın

### "Quota exceeded"
- 24 saat bekleyin veya kota artışı için başvuru yapın

### "Video already exists"
- YouTube aynı video dosyasını tekrar yüklemenize izin vermeyebilir
- Farklı bir trend veya video deneyin

## 📝 Best Practices

1. **Test Etme**: İlk videolarınızı "unlisted" veya "private" olarak yükleyin
2. **Başlıklar**: YouTube Shorts için kısa ve çarpıcı başlıklar kullanın
3. **Hashtag**: `#Shorts` hashtag'i otomatik eklenir, değiştirmeyin
4. **Thumbnail**: YouTube otomatik thumbnail oluşturur (Shorts için özel thumbnail gerekmez)
5. **Video Kalitesi**: Minimum 720p, ideal 1080p portrait video kullanın

## 📞 Destek

Sorularınız için:
- YouTube Data API Docs: https://developers.google.com/youtube/v3
- OAuth 2.0 Guide: https://developers.google.com/identity/protocols/oauth2

---

**Not:** YouTube Shorts otomatik olarak:
- 60 saniyeden kısa
- 9:16 aspect ratio (portrait)
- Minimum 1080p çözünürlük

videolarını "Shorts" olarak algılar. Uygulamanız bu gereksinimleri karşılıyor.
