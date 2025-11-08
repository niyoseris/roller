# Twitter Entegrasyonu - Kurulum Rehberi

Bu rehber, uygulamanızın otomatik olarak Twitter'a tweet atması için gerekli adımları açıklar.

## 📋 İçindekiler

1. [Twitter API Erişimi](#twitter-api-erişimi)
2. [API Anahtarlarını Alma](#api-anahtarlarını-alma)
3. [Ortam Değişkenlerini Ayarlama](#ortam-değişkenlerini-ayarlama)
4. [Kurulum](#kurulum)
5. [Test Etme](#test-etme)
6. [Kullanım](#kullanım)
7. [Sorun Giderme](#sorun-giderme)

---

## 🔑 Twitter API Erişimi

Twitter API kullanmak için bir Twitter Developer hesabına ihtiyacınız var.

### Adımlar:

1. **Twitter Developer Portal'a giriş yapın:**
   - https://developer.twitter.com/en/portal/dashboard
   - Twitter hesabınızla giriş yapın

2. **Yeni bir proje oluşturun:**
   - "Create Project" butonuna tıklayın
   - Proje adı: `Trend Collector` (veya istediğiniz bir ad)
   - Use case: Educational veya Making a bot

3. **App oluşturun:**
   - Proje içinde "Create App" yapın
   - App adı: `trend-collector-bot` (benzersiz olmalı)
   - App type: `Read and Write` (tweet atabilmek için gerekli)

---

## 🔐 API Anahtarlarını Alma

App'inizi oluşturduktan sonra API anahtarlarını alın:

### 1. API Key ve API Secret (Consumer Keys)

- App Settings → Keys and tokens
- "API Key and Secret" bölümünden:
  - `API Key` (Consumer Key)
  - `API Secret` (Consumer Secret)
- Bu anahtarları kaydedin (bir daha gösterilemeyecekler)

### 2. Access Token ve Access Token Secret

- Aynı sayfada "Access Token and Secret" bölümü:
  - "Generate" butonuna tıklayın
  - `Access Token`
  - `Access Token Secret`
- Bu anahtarları da kaydedin

### 3. Bearer Token (Opsiyonel)

- "Bearer Token" bölümünden Bearer Token'ı alabilirsiniz
- API v2 için kullanılır

---

## ⚙️ Ortam Değişkenlerini Ayarlama

API anahtarlarınızı ortam değişkenleri olarak ayarlayın:

### macOS/Linux:

#### Geçici (sadece mevcut terminal oturumu için):

```bash
export TWITTER_API_KEY='your_api_key_here'
export TWITTER_API_SECRET='your_api_secret_here'
export TWITTER_ACCESS_TOKEN='your_access_token_here'
export TWITTER_ACCESS_TOKEN_SECRET='your_access_token_secret_here'
export TWITTER_BEARER_TOKEN='your_bearer_token_here'  # Opsiyonel
```

#### Kalıcı (her terminal oturumunda):

**zsh kullanıyorsanız (macOS varsayılan):**

```bash
# ~/.zshrc dosyasını açın
nano ~/.zshrc

# Dosyanın sonuna aşağıdaki satırları ekleyin:
export TWITTER_API_KEY='your_api_key_here'
export TWITTER_API_SECRET='your_api_secret_here'
export TWITTER_ACCESS_TOKEN='your_access_token_here'
export TWITTER_ACCESS_TOKEN_SECRET='your_access_token_secret_here'
export TWITTER_BEARER_TOKEN='your_bearer_token_here'

# Kaydedin (Ctrl+O, Enter, Ctrl+X)

# Değişiklikleri yükleyin:
source ~/.zshrc
```

**bash kullanıyorsanız:**

```bash
# ~/.bashrc dosyasını açın
nano ~/.bashrc

# Aynı export satırlarını ekleyin ve kaydedin
source ~/.bashrc
```

### Windows:

#### PowerShell:

```powershell
$env:TWITTER_API_KEY='your_api_key_here'
$env:TWITTER_API_SECRET='your_api_secret_here'
$env:TWITTER_ACCESS_TOKEN='your_access_token_here'
$env:TWITTER_ACCESS_TOKEN_SECRET='your_access_token_secret_here'
$env:TWITTER_BEARER_TOKEN='your_bearer_token_here'
```

#### Kalıcı olarak ayarlamak için:
1. "Sistem Özellikleri" → "Gelişmiş" → "Ortam Değişkenleri"
2. Her bir değişkeni ekleyin

---

## 📦 Kurulum

1. **Gerekli paketleri yükleyin:**

```bash
cd /Users/niyoseris/Desktop/Python/agentic
pip install -r requirements.txt
```

veya doğrudan:

```bash
pip install tweepy==4.14.0
```

2. **Ortam değişkenlerinin ayarlandığını doğrulayın:**

```bash
echo $TWITTER_API_KEY
# API anahtarınızı görmeli
```

---

## 🧪 Test Etme

Test scriptini çalıştırarak Twitter entegrasyonunu test edin:

```bash
python test_twitter.py
```

Bu script:
- Twitter bağlantısını kontrol eder
- Tweet formatını gösterir
- İsteğe bağlı olarak test tweet'i atar

**Örnek çıktı:**

```
============================================================
Twitter Poster Test
============================================================

1. Initializing Twitter poster...
✅ Twitter API client initialized successfully

2. Twitter posting enabled: True

3. Testing tweet formatting...

Formatted tweet (154 chars):
------------------------------------------------------------
📰 New Article: NBA

📚 Category: Sports

🔗 Read more: https://roll.wiki/NBA

#Wikipedia #Trending
------------------------------------------------------------

4. Ready to post test tweet

Do you want to post this test tweet? (yes/no): yes

5. Posting test tweet...
🐦 Posting tweet: 📰 New Article: NBA...
✅ Tweet posted successfully! Tweet ID: 1234567890
   View at: https://twitter.com/i/web/status/1234567890

============================================================
Test completed!
============================================================
```

---

## 🚀 Kullanım

### Ana uygulamayı çalıştırın:

```bash
python main.py
```

Uygulama artık her başarılı makale gönderiminden sonra otomatik olarak tweet atacak!

**İşleyiş:**

1. Trendler toplanır
2. Wikipedia makalesi bulunur
3. Ollama ile kategori belirlenir
4. roll.wiki'ye gönderilir
5. **✨ Otomatik olarak Twitter'a tweet atılır**

### Twitter'ı devre dışı bırakmak:

Eğer Twitter'ı geçici olarak kapatmak isterseniz:

**Yöntem 1:** Ortam değişkenlerini kaldırın:
```bash
unset TWITTER_API_KEY TWITTER_API_SECRET TWITTER_ACCESS_TOKEN TWITTER_ACCESS_TOKEN_SECRET
```

**Yöntem 2:** Config dosyasını düzenleyin:
```python
# config.py
TWITTER_ENABLED = False
```

---

## 🔧 Sorun Giderme

### "Twitter credentials not configured" hatası

**Çözüm:**
- Ortam değişkenlerinin doğru ayarlandığını kontrol edin:
  ```bash
  env | grep TWITTER
  ```
- Değişkenler görünmüyorsa, tekrar ayarlayın ve terminal'i yeniden başlatın

### "Failed to initialize Twitter client" hatası

**Olası nedenler:**
1. **Yanlış API anahtarları:** Twitter Developer Portal'dan anahtarları kontrol edin
2. **App permissions:** App'inizin "Read and Write" yetkisine sahip olduğunu doğrulayın
3. **Regenerate tokens:** Gerekirse yeni access token oluşturun

### "TweepyException: 403 Forbidden" hatası

**Çözüm:**
- App'inizin "Read and Write" yetkisi olduğunu kontrol edin
- Developer Portal → Your App → Settings → User authentication settings
- App permissions'ı "Read and Write" olarak ayarlayın
- Yeni access token oluşturun

### "Tweet too long" hatası

**Çözüm:**
Kod otomatik olarak uzun tweet'leri kısaltır, ancak sorun devam ederse:
- `twitter_poster.py` dosyasındaki `format_tweet()` metodunu kontrol edin
- Tweet karakteri 280'i geçmemelidir

---

## 📊 Tweet Formatı

Atılan tweetler şu formattadır (kısa format, ~140 karakter):

```
📰 [Trend Adı] - [Kategori]
🔗 https://roll.wiki/summary/[article_id]
#Wikipedia #Trending
```

**Örnek:**

```
📰 NBA - Sports
🔗 https://roll.wiki/summary/1462
#Wikipedia #Trending
```

*Bu format ~90-110 karakter civarındadır ve Twitter'ın eski 140 karakter limitine uygun, öz bir mesajdır.*

---

## 📝 Notlar

- **Rate Limits:** Twitter API'nin rate limit'leri vardır. Uygulama bu limitlere uyar.
- **Free Tier:** Twitter API Free tier kullanıyorsanız aylık tweet limitleri olabilir
- **Monitoring:** Tweet başarısını `trend_collector.log` dosyasından takip edebilirsiniz
- **Statistics:** Web dashboard'da (http://localhost:5001) toplam tweet sayısını görebilirsiniz

---

## 🆘 Yardım

Sorun yaşarsanız:

1. Log dosyasını kontrol edin: `trend_collector.log`
2. Test scriptini çalıştırın: `python test_twitter.py`
3. Twitter API durumunu kontrol edin: https://api.twitterstat.us/

---

## 🎉 Başarıyla Kuruldu!

Artık uygulamanız otomatik olarak Twitter'a tweet atacak. Her başarılı makale gönderimi sonrasında projenizin Twitter hesabından paylaşım yapılacak.

**İyi paylaşımlar! 🐦✨**
