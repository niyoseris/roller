# Kullanım Kılavuzu

## Kurulum ve Başlatma

### 0. Ollama Kurulumu (Gerekli!)

Uygulama Ollama kullanır - ücretsiz, yerel LLM platformu:

```bash
# macOS kurulum
brew install ollama

# Ollama'yı başlat
ollama serve

# Bir model indir (önerilen)
ollama pull qwen2.5:7b
```

**Detaylı kurulum için:** `OLLAMA_SETUP.md` dosyasına bakın.

### 1. Hızlı Başlangıç

En kolay yol `start.sh` scriptini kullanmak:

```bash
cd /Users/niyoseris/Desktop/Python/agentic
./start.sh
```

Bu script:
- Virtual environment oluşturur (eğer yoksa)
- Gerekli paketleri yükler
- Uygulamayı başlatır

### 2. Manuel Başlatma

```bash
# Virtual environment oluştur (ilk sefer)
python3 -m venv venv

# Paketleri yükle (ilk sefer)
./venv/bin/pip install -r requirements.txt

# Uygulamayı başlat
./venv/bin/python main.py
```

## Web Monitoring Dashboard

Uygulama başladığında, tarayıcınızdan şu adrese gidin:

```
http://localhost:5001
```

Dashboard'da görebilecekleriniz:
- ✅ Tamamlanan cycle sayısı
- ✅ Gönderilen makale sayısı
- ✅ Son cycle'da toplanan trend sayısı
- ✅ İşlenmiş toplam Wikipedia URL'leri
- ✅ Başlangıç zamanı
- ✅ Son cycle zamanı
- 🆕 **LLM Model Seçimi** - Dropdown'dan istediğiniz Ollama modelini seçin!

### Model Değiştirme

Web arayüzünde **LLM Model** dropdown'u:
1. Mevcut tüm Ollama modellerini gösterir
2. Aktif modeli seçili gösterir
3. Tıklayarak başka bir model seçebilirsiniz
4. Model anında değişir - yeniden başlatma gerekmez!

**Örnek:**
- gemma3:12b → Yüksek doğruluk
- qwen2.5:7b → Dengeli performans
- phi4-mini:3.8b-fp16 → Hızlı

## Nasıl Çalışır?

### 1. Trend Toplama (Her 60 Dakikada Bir)

Uygulama şu platformlardan **GERÇEK TRENDLERİ** toplar:
- 🐦 Twitter/X (trends24.in) - Gerçek trending keywords
- 🤖 Reddit - Keyword extraction
- 🔍 Google Trends (PyTrends) - Daily trending searches
- 📱 TikTok - Trending hashtags
- 🔎 Bing Trends - Search trends

**Not:** Haber başlıkları değil, gerçek trend keyword'leri alınır!

### 2. 🔍 Wikipedia Makalesi Bulma

Toplanan **her trend** için:
- Wikipedia API kullanılarak ilgili makale aranır
- Bulunan makalenin URL'i ve içeriği alınır
- Daha önce işlenmiş mi kontrol edilir (duplicate detection)
- Yeni makaleler işleme alınır

**Önemli:** Tüm trendler işlenir, filtreleme yapılmaz!

### 3. 🧠 AI ile Akıllı Kategorileme (Ollama)

Ollama LLM kullanarak makale analiz edilir ve 27 kategoriden biri seçilir:

**Kategoriler:**
- Architecture, Arts, Business, Culture, Dance
- Economics, Education, Engineering, Entertainment
- Environment, Fashion, Film, Food, Geography
- History, Literature, Medicine, Music, Philosophy
- Politics, Psychology, Religion, Science, Sports
- Technology, Theater, Transportation

**Örnek Kategorileme:**
- "Tesla earnings Q4" → **Business** ✅
- "Lakers vs Warriors highlights" → **Sports** ✅
- "Climate summit in Paris" → **Environment** ✅

AI kategorileme başarısız olursa keyword-based fallback sistemi devreye girer.

### 4. 🚀 roll.wiki'ye Gönderme

Her makale için POST request gönderilir:
```
POST https://roll.wiki/api/v1/summarize
Parameters:
  - url: [Wikipedia URL]
  - save: true
  - category: [Ollama ile kategorilenen kategori]
  - secret: laylaylom
```

**Workflow:**
1. Wikipedia URL + Category hazırla
2. roll.wiki API'sine POST request gönder
3. Başarılıysa → URL'i processed olarak işaretle
4. 30 saniye bekle
5. Sonraki trend'e geç

### 5. ✅ Duplicate Control

- İşlenen tüm URL'ler `processed_urls.json` dosyasında saklanır
- Bir URL daha önce işlendiyse tekrar gönderilmez
- Bu sayede duplicate submission'lar önlenir
- Sistem yeniden başlatılsa bile işlenmiş URL'ler hatırlanır

## Zaman Ayarları

- **Cycle Aralığı:** 60 dakika (3600 saniye)
- **Request Aralığı:** 30 saniye (her makale gönderimi arasında)

Örnek:
- 10 trend bulundu
- Her biri için Wikipedia aranıyor
- 5 tanesi için makale bulundu
- İlk makale gönderiliyor → 30 saniye bekleniyor
- İkinci makale gönderiliyor → 30 saniye bekleniyor
- ... (devam eder)
- Tüm makaleler gönderildikten sonra 60 dakika bekleniyor
- Yeni cycle başlıyor

## Loglar

Tüm işlemler iki yerde loglanır:
1. **Konsol:** Terminalde canlı görürsünüz
2. **Dosya:** `trend_collector.log` dosyasına kaydedilir

Log örneği:
```
2025-10-22 21:01:54 - main - INFO - Starting trend collection from all platforms...
2025-10-22 21:01:54 - main - INFO - RedditTrendsCollector: Found 20 trends
2025-10-22 21:01:54 - main - INFO - Total unique trends collected: 55
```

## Veri Dosyaları

- **processed_urls.json:** İşlenmiş Wikipedia URL'lerinin listesi
- **trend_collector.log:** Tüm işlem logları

## Durdurma

Uygulamayı durdurmak için:
```
Ctrl+C
```

## Test Etme

### Hızlı Test (Trend Toplama)
```bash
./venv/bin/python test_quick.py
```

Bu test:
- Trend toplama işlevselliğini test eder
- Wikipedia bulma işlevselliğini test eder
- URL tracker'ı test eder
- Ama roll.wiki'ye gerçek gönderim yapmaz

### LLM Entegrasyonu Testi (Ollama)
```bash
./venv/bin/python test_ollama.py
```

Bu test:
- Ollama bağlantısını kontrol eder
- Mevcut modelleri listeler
- Kategorileme doğruluğunu test eder
- Relevance scoring'i test eder
- Model değiştirme özelliğini gösterir

**Örnek Çıktı:**
```
Ollama Available: True

Listing Available Models...
Found 10 models:
- gemma3:12b
- deepseek-r1:14b
- qwen2.5:7b

Trend: 'Tesla earnings report Q4 2024'
Category: Business ✓

Relevance Scoring:
Major earthquake: 0.95
Random drama: 0.40
NASA Mars discovery: 0.90
```

## Sorun Giderme

### Port 5001 kullanımda hatası

Eğer "Address already in use" hatası alırsanız:
```bash
# Port'u kullanan process'i bul
lsof -i :5001

# Process'i durdur
kill -9 [PID]
```

### Trend toplanamıyor

Bazı platformlar zaman zaman erişilemez olabilir. Bu normal.
Uygulama hata alsa bile diğer platformlardan toplamaya devam eder.

### Virtual environment hataları

Virtual environment'ı sıfırdan oluştur:
```bash
rm -rf venv
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

## İstatistikler

Web dashboard üzerinden gerçek zamanlı istatistikleri görebilirsiniz:
- `/api/status` - Sistem durumu
- `/api/stats` - İstatistikler
- `/api/processed` - İşlenmiş URL'ler

Örnek API çağrısı:
```bash
curl http://localhost:5001/api/stats
```

## Öneriler

1. **7/24 Çalıştırma:** Screen veya tmux kullanın:
   ```bash
   screen -S trends
   ./start.sh
   # Ctrl+A+D ile detach
   ```

2. **Otomatik Başlatma:** Sistem açıldığında otomatik başlatmak için systemd service oluşturabilirsiniz

3. **Monitoring:** Web dashboard'u düzenli kontrol edin

4. **Backup:** `processed_urls.json` dosyasını düzenli yedekleyin
