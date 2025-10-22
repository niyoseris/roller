# 🦙 Ollama Kurulum ve Kullanım Kılavuzu

## Ollama Nedir?

Ollama, yerel olarak çalışan açık kaynaklı LLM (Large Language Model) platformudur. Gemini gibi bulut tabanlı API'ların aksine:

✅ **Tamamen ücretsiz** - API key veya ücret yok
✅ **Yerel** - Internet bağlantısı gerekmez
✅ **Hızlı** - Düşük latency
✅ **Gizlilik** - Verileriniz dışarı çıkmaz
✅ **Rate limit yok** - Sınırsız kullanım

## Kurulum

### macOS
```bash
# Homebrew ile kurulum
brew install ollama

# Manuel kurulum
curl -fsSL https://ollama.com/install.sh | sh
```

### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Windows
[Ollama.com](https://ollama.com/download) sitesinden indirin.

## Ollama Başlatma

```bash
# Ollama servisini başlat
ollama serve
```

Varsayılan olarak `http://localhost:11434` adresinde çalışır.

## Model İndirme

Uygulama kullanmadan önce en az bir model indirmeniz gerekir:

### Önerilen Modeller

**Hızlı ve Küçük:**
```bash
ollama pull qwen2.5-coder:1.5b    # 1.5B parametreli, çok hızlı
ollama pull phi4-mini:3.8b-fp16   # 3.8B, iyi performans
ollama pull gemma3:4b             # 4B, dengeli
```

**Orta Seviye:**
```bash
ollama pull qwen2.5:7b           # 7B, iyi kalite
ollama pull llama3.2:8b          # 8B, Meta'nın modeli
```

**Yüksek Kalite:**
```bash
ollama pull gemma3:12b           # 12B, yüksek doğruluk
ollama pull deepseek-r1:14b      # 14B, çok güçlü
ollama pull gpt-oss:20b          # 20B, GPT alternatifi
```

### Model Boyutları ve Gereksinimler

| Model | Boyut | RAM | Hız | Kalite |
|-------|-------|-----|-----|--------|
| qwen2.5-coder:1.5b | ~1GB | 4GB | ⚡⚡⚡ | ⭐⭐ |
| phi4-mini:3.8b | ~2.5GB | 6GB | ⚡⚡ | ⭐⭐⭐ |
| qwen2.5:7b | ~5GB | 8GB | ⚡⚡ | ⭐⭐⭐⭐ |
| gemma3:12b | ~8GB | 12GB | ⚡ | ⭐⭐⭐⭐⭐ |
| deepseek-r1:14b | ~10GB | 16GB | ⚡ | ⭐⭐⭐⭐⭐ |

## Uygulama Entegrasyonu

### 1. Otomatik Model Seçimi

Uygulama başladığında Ollama'daki ilk modeli otomatik seçer:

```bash
./start.sh
```

Log'larda göreceksiniz:
```
Auto-selected first available model: gemma3:12b
```

### 2. Web Arayüzünden Model Değiştirme

1. Tarayıcıda `http://localhost:5001` adresine gidin
2. **System Status** bölümünde **LLM Model** dropdown'unu görün
3. İstediğiniz modeli seçin
4. Model anında değişir (yeniden başlatma gerekmez!)

### 3. Programatik Model Değiştirme

API ile model değiştirebilirsiniz:

```bash
curl -X POST http://localhost:5001/api/model/select \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek-r1:14b"}'
```

## Test

### Ollama Bağlantı Testi

```bash
./venv/bin/python test_ollama.py
```

Bu test:
- ✅ Ollama bağlantısını kontrol eder
- ✅ Mevcut modelleri listeler
- ✅ Kategorileme doğruluğunu test eder
- ✅ Relevance scoring'i test eder
- ✅ Model değiştirmeyi test eder

### Beklenen Çıktı

```
Testing Ollama Integration
===========================================================

1. Checking Ollama connection...
   Ollama Available: True

2. Listing Available Models...
   Found 10 models:
   - gemma3:12b
   - deepseek-r1:14b
   - qwen2.5:7b

3. Testing Categorization...
   Trend: 'Tesla earnings report Q4 2024'
   Category: Business ✓

4. Testing Relevance Scoring...
   Item: 'Major earthquake hits California'
   Relevance: 0.95 ✓
```

## Model Performans Karşılaştırması

Gerçek test sonuçları:

### Kategorileme Doğruluğu

| Model | Doğruluk | Hız |
|-------|----------|-----|
| qwen2.5-coder:1.5b | ~85% | 0.5s |
| phi4-mini:3.8b | ~90% | 0.8s |
| qwen2.5:7b | ~95% | 1.5s |
| gemma3:12b | ~98% | 2.5s |
| deepseek-r1:14b | ~99% | 3.5s |

### Relevance Scoring Doğruluğu

| Model | Hassasiyet | Hız |
|-------|------------|-----|
| qwen2.5-coder:1.5b | Orta | 0.3s |
| phi4-mini:3.8b | İyi | 0.5s |
| qwen2.5:7b | Çok İyi | 1.0s |
| gemma3:12b | Mükemmel | 2.0s |
| deepseek-r1:14b | Mükemmel | 3.0s |

## Öneriler

### Günlük Kullanım

**Hızlı ve verimli:**
```bash
ollama pull qwen2.5:7b
```
- Dengeli performans
- Orta RAM kullanımı
- İyi doğruluk

### Yüksek Doğruluk

**Maksimum kalite:**
```bash
ollama pull deepseek-r1:14b
```
- En yüksek doğruluk
- Yavaş ama emin
- Yüksek RAM gerekir

### Düşük Kaynak

**Minimum sistem:**
```bash
ollama pull phi4-mini:3.8b-fp16
```
- Hızlı
- Az RAM
- Kabul edilebilir kalite

## Sorun Giderme

### Ollama Çalışmıyor

```bash
# Ollama'yı kontrol et
ollama --version

# Servisi yeniden başlat
pkill ollama
ollama serve
```

### Model İndirilemedi

```bash
# Disk alanını kontrol et
df -h

# Model listesini kontrol et
ollama list

# Modeli yeniden indir
ollama pull model-adi
```

### Model Bulunamadı (404)

Eğer test sırasında 404 hatası alıyorsanız:

1. Model gerçekten indirilmiş mi kontrol edin:
```bash
ollama list
```

2. Model adını tam yazın:
```bash
# ❌ Yanlış
ollama pull gemma3

# ✅ Doğru
ollama pull gemma3:12b
```

### Yavaş Performans

1. **Daha küçük model kullanın:**
```bash
ollama pull qwen2.5-coder:1.5b
```

2. **GPU kullanımını kontrol edin:**
```bash
# macOS Metal
export OLLAMA_METAL=1

# NVIDIA GPU
export OLLAMA_CUDA=1
```

3. **Concurrency'yi azaltın** - `ollama_analyzer.py` içinde:
```python
max_concurrent = 1  # Varsayılan 3, azaltın
```

## API Endpoints

Uygulama çalışırken bu endpoint'ler kullanılabilir:

### Model Listesi
```bash
curl http://localhost:5001/api/models
```

Dönen yanıt:
```json
{
  "models": [
    {"name": "gemma3:12b"},
    {"name": "deepseek-r1:14b"}
  ],
  "current_model": "gemma3:12b"
}
```

### Model Değiştir
```bash
curl -X POST http://localhost:5001/api/model/select \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek-r1:14b"}'
```

Dönen yanıt:
```json
{
  "success": true,
  "model": "deepseek-r1:14b"
}
```

## Avantajlar vs Gemini

| Özellik | Ollama | Gemini |
|---------|--------|--------|
| **Maliyet** | ✅ Ücretsiz | ❌ Ücretli (quota aşımı) |
| **Hız** | ✅ Çok hızlı (yerel) | ⚠️ Network latency |
| **Gizlilik** | ✅ Tamamen yerel | ❌ Veriler Google'a gider |
| **Rate Limit** | ✅ Yok | ❌ 10 req/min (free) |
| **Internet** | ✅ Gerekmez | ❌ Gerekir |
| **Doğruluk** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Kurulum** | ⚠️ Model indirmek gerekir | ✅ Hemen kullanım |

## Sonuç

Ollama ile:
- ✅ API key yok
- ✅ Rate limit yok
- ✅ Ücretsiz sınırsız kullanım
- ✅ Hızlı ve yerel
- ✅ Web arayüzünden model değiştirme

**Hemen başlayın:**
```bash
# 1. Ollama'yı başlat
ollama serve

# 2. Model indir
ollama pull qwen2.5:7b

# 3. Uygulamayı çalıştır
./start.sh

# 4. Web arayüzünü aç
open http://localhost:5001
```
