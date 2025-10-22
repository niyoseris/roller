# 📡 roll.wiki API Dokümantasyonu

## API Endpoint

```
https://roll.wiki/api/v1/summarize
```

## HTTP Method

**GET** request

## Parametreler

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | ✅ Yes | Wikipedia article URL (https://en.wikipedia.org/wiki/...) |
| `save` | string | ✅ Yes | "true" to save the article |
| `category` | string | ✅ Yes | Category name (27 options) |
| `secret` | string | ✅ Yes | API authentication key ("laylaylom") |

## Örnek Request

### cURL
```bash
curl "https://roll.wiki/api/v1/summarize?url=https://en.wikipedia.org/wiki/NBA&save=true&category=Sports&secret=laylaylom"
```

### Python (aiohttp)
```python
import aiohttp

url = "https://roll.wiki/api/v1/summarize"
params = {
    "url": "https://en.wikipedia.org/wiki/NBA",
    "save": "true",
    "category": "Sports",
    "secret": "laylaylom"
}

async with aiohttp.ClientSession() as session:
    async with session.get(url, params=params) as response:
        status = response.status
        data = await response.text()
```

### Full URL
```
https://roll.wiki/api/v1/summarize?url=https://en.wikipedia.org/wiki/NBA&save=true&category=Sports&secret=laylaylom
```

---

## Response Codes

### ✅ 200 OK - Success
Makale başarıyla submit edildi ve işlendi.

**Example Response:**
```json
{
  "data": {
    "image_url": null,
    "language": "en",
    "original_content": "The National Basketball Association (NBA) is...",
    ...
  },
  "success": true
}
```

**Uygulama Davranışı:**
- ✅ Success olarak işaretle
- ✅ URL'i processed_urls.json'a ekle
- ✅ Log: "Successfully submitted"

---

### ℹ️ 409 Conflict - Already Exists
Makale zaten roll.wiki'de var.

**Example Response:**
```json
{
  "data": {
    "image_url": null,
    "language": "en",
    "original_content": "The National Basketball Association (NBA) is...",
    ...
  }
}
```

**Uygulama Davranışı:**
- ✅ Success olarak kabul et
- ✅ URL'i processed_urls.json'a ekle
- ℹ️ Log: "Article already exists in roll.wiki"

**Not:** Duplicate submission, ama zararlı değil. Makale zaten sistemde.

---

### ⚠️ 404 Not Found - Wikipedia Article Not Found
Wikipedia'da böyle bir makale yok.

**Example Response:**
```json
{
  "error": "Article \"XYZ\" not found on Wikipedia",
  "success": false
}
```

**Uygulama Davranışı:**
- ❌ Failure olarak işaretle
- ⚠️ URL'i processed_urls.json'a EKLEME
- ⚠️ Log: "Wikipedia article not found"

**Sebep:** 
- Yanlış URL format
- Makale gerçekten yok
- Redirect edilmiş veya silinmiş

---

### ❌ 500 Internal Server Error
roll.wiki sunucu hatası.

**Uygulama Davranışı:**
- ❌ Failure olarak işaretle
- ❌ URL'i processed_urls.json'a EKLEME
- ❌ Log: "Failed to submit: Status 500"

**Sebep:**
- Sunucu problemi
- Geçici hata
- Tekrar denenebilir

---

## Kategoriler (27 Seçenek)

```
Architecture, Arts, Business, Culture, Dance, Economics,
Education, Engineering, Entertainment, Environment, Fashion,
Film, Food, Geography, History, Literature, Medicine, Music,
Philosophy, Politics, Psychology, Religion, Science, Sports,
Technology, Theater, Transportation
```

---

## Örnekler

### Örnek 1: NBA (Sports)
```
GET https://roll.wiki/api/v1/summarize?url=https://en.wikipedia.org/wiki/NBA&save=true&category=Sports&secret=laylaylom

Response: 409 Conflict (already exists)
Action: Skip (already in roll.wiki)
```

### Örnek 2: Everest (Geography)
```
GET https://roll.wiki/api/v1/summarize?url=https://en.wikipedia.org/wiki/Everest&save=true&category=Geography&secret=laylaylom

Response: 409 Conflict (already exists)
Action: Skip (already in roll.wiki)
```

### Örnek 3: Talus_Labs (Technology)
```
GET https://roll.wiki/api/v1/summarize?url=https://en.wikipedia.org/wiki/Talus_Labs&save=true&category=Technology&secret=laylaylom

Response: 404 Not Found
Action: Skip (Wikipedia article doesn't exist)
```

### Örnek 4: Donald_Trump (Politics)
```
GET https://roll.wiki/api/v1/summarize?url=https://en.wikipedia.org/wiki/Donald_Trump&save=true&category=Politics&secret=laylaylom

Response: 200 OK or 409 Conflict
Action: Success
```

---

## Uygulamamızda Kullanım

### URL Oluşturma
```python
def create_wikipedia_url(self, trend: str) -> str:
    # "NBA10K" → "NBA"
    clean_trend = re.sub(r'\d+[KkMm]?\s*$', '', trend).strip()
    # "NBA" → "https://en.wikipedia.org/wiki/NBA"
    return f"https://en.wikipedia.org/wiki/{clean_trend}"
```

### Kategori Belirleme
```python
# Ollama LLM ile
category = await self.llm_analyzer.categorize_trend("NBA", "")
# Result: "Sports"
```

### Gönderim
```python
params = {
    "url": "https://en.wikipedia.org/wiki/NBA",
    "save": "true",
    "category": "Sports",
    "secret": "laylaylom"
}

async with session.get(ROLL_WIKI_API, params=params) as response:
    if response.status == 200:
        # Success
    elif response.status == 409:
        # Already exists (still success)
    elif response.status == 404:
        # Wikipedia not found
```

---

## Test Script

Test için `test_rollwiki.py` kullanabilirsiniz:

```bash
./venv/bin/python test_rollwiki.py
```

Test edilen URL'ler:
- ✅ NBA (409 - already exists)
- ✅ Everest (409 - already exists)
- ❌ Talus_Labs (404 - not found)

---

## Rate Limiting

### Uygulamamızda
- ⏳ Her submission arasında **30 saniye** delay
- 🔄 Her cycle **60 dakika** ara
- 📊 Günlük maksimum: ~840 request

### roll.wiki'nin Limiti
- ❓ Bilinmiyor (dokümantasyon yok)
- ✅ 30 saniye delay yeterince güvenli
- ✅ 409 response'ları sorun değil

---

## Error Handling

### Timeout
```python
timeout=30  # 30 saniye timeout
```

### Network Error
```python
try:
    async with session.get(...) as response:
        ...
except Exception as e:
    logger.error(f"Error: {e}")
    return False
```

### Invalid Response
```python
if status not in [200, 409, 404, 500]:
    logger.warning(f"Unexpected status: {status}")
    return False
```

---

## Özet

### API Format
```
GET https://roll.wiki/api/v1/summarize?url=WIKIPEDIA_URL&save=true&category=CATEGORY&secret=laylaylom
```

### Success Criteria
- ✅ 200 OK → Yeni makale eklendi
- ✅ 409 Conflict → Makale zaten var (OK)

### Failure Criteria
- ❌ 404 Not Found → Wikipedia'da yok
- ❌ 500 Server Error → Sunucu problemi
- ❌ Timeout → Network problemi

### Uygulama Akışı
```
Trend → URL Oluştur → LLM Kategorile → roll.wiki'ye Gönder
```

**Her şey hazır ve çalışıyor! 🎉**
