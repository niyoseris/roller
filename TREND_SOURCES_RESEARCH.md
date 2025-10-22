# 🔍 Gerçek Trend Kaynakları Araştırması

## 📊 Mevcut Durum - Problem Analizi

### ❌ Şu Anda Ne Alınıyor?
```
"ICJ says Israel must allow UN aid deliveries..." → HABER BAŞLIĞI
"Zelensky Says Strike on Kindergarten..." → HABER BAŞLIĞI
"Health insurance sticker shock begins..." → HABER BAŞLIĞI
```

### ✅ Ne Alınmalı?
```
"Taylor Swift" → GERÇEK TREND
"iPhone 15" → GERÇEK TREND
"World Cup 2026" → GERÇEK TREND
"ChatGPT" → GERÇEK TREND
```

## 🎯 Gerçek Trend Platformları

### 1. **Google Trends** (EN İYİ KAYNAK)

#### Resmi API
```python
# PyTrends kütüphanesi (resmi değil ama kararlı)
from pytrends.request import TrendReq

pytrends = TrendReq(hl='en-US', tz=360)
trending = pytrends.trending_searches(pn='united_states')
```

**Avantajlar:**
- ✅ Gerçek trendler
- ✅ Günlük güncelleme
- ✅ Güvenilir
- ✅ Ücretsiz

**Dezavantajlar:**
- ⚠️ Rate limiting var
- ⚠️ Resmi API değil

#### RSS Feed (Mevcut - Düzeltilmeli)
```
URL: https://trends.google.com/trends/trendingsearches/daily/rss?geo=US
```

**Sorun:** XML parsing hatalı, düzeltilmeli.

---

### 2. **Twitter/X Trends**

#### A. Resmi API (Twitter API v2)
```python
import tweepy

client = tweepy.Client(bearer_token='TOKEN')
trends = client.get_place_trends(id=23424977)  # USA WOEID
```

**Avantajlar:**
- ✅ Gerçek zamanlı
- ✅ Resmi kaynak
- ✅ Doğru trendler

**Dezavantajlar:**
- ❌ API key gerekli (ücretsiz tier sınırlı)
- ❌ Rate limit: 75 req/15min

#### B. Scraping Alternatifi (Önerilen)
```
Site: https://getdaytrends.com/united-states/
Site: https://trends24.in/united-states/
```

**Not:** Mevcut getdaytrends collector çalışmıyor, HTML yapısı değişmiş.

---

### 3. **TikTok Trends** (ÇOK POPÜLER)

#### Scraping
```
URL: https://www.tiktok.com/discover
```

**Avantajlar:**
- ✅ Genç kitlede çok popüler
- ✅ Viral içerik trendleri
- ✅ Müzik ve challenge'lar

**Dezavantajlar:**
- ⚠️ JavaScript rendering gerekli (Playwright/Selenium)
- ⚠️ Sık değişen HTML yapısı

---

### 4. **YouTube Trending**

#### YouTube Data API v3
```python
from googleapiclient.discovery import build

youtube = build('youtube', 'v3', developerKey='KEY')
request = youtube.videos().list(
    part='snippet',
    chart='mostPopular',
    regionCode='US',
    maxResults=50
)
```

**Avantajlar:**
- ✅ Resmi API
- ✅ Video bazlı trendler
- ✅ Ücretsiz (quota limiti var)

**Dezavantajlar:**
- ⚠️ API key gerekli
- ⚠️ Quota: 10,000 units/day

---

### 5. **Reddit Hot Topics** (Mevcut - İyileştirilebilir)

```python
# Subreddit bazlı trending
subreddits = ['all', 'news', 'worldnews', 'technology', 'entertainment']
```

**Sorun:** Post başlıkları alınıyor, trendler değil.

**Çözüm:** Post başlıklarından trend keyword'leri extract etmek.

---

### 6. **Instagram/Meta Trends**

#### Unofficial API
```
Site: https://www.instagram.com/explore/tags/
```

**Avantajlar:**
- ✅ Hashtag trendleri
- ✅ Görsel içerik popülaritesi

**Dezavantajlar:**
- ❌ Resmi API yok
- ❌ Login gerekli
- ❌ Bot detection

---

### 7. **Bing Trends**

```
URL: https://www.bing.com/news/trending
```

**Avantajlar:**
- ✅ Ücretsiz
- ✅ Resmi kaynak

**Dezavantajlar:**
- ⚠️ Google kadar popüler değil

---

## 🛠️ ÖNERİLEN ÇÖZÜM PAKETİ

### ⭐ Tier 1: Mutlaka Olmalı

1. **Google Trends (PyTrends)**
   - Kurulum: `pip install pytrends`
   - En güvenilir kaynak
   - Gerçek arama trendleri

2. **Twitter Trends (Scraping)**
   - trends24.in veya getdaytrends.com
   - Güncel HTML parsing

### ⭐ Tier 2: İlave Kaynaklar

3. **YouTube Trends (API)**
   - API key: Ücretsiz Google Cloud
   - Video bazlı trendler

4. **Reddit Hot Topics**
   - Keyword extraction ile iyileştir
   - NER (Named Entity Recognition) kullan

### ⭐ Tier 3: Bonus

5. **TikTok Trends**
   - Playwright ile scraping
   - Genç kitle için önemli

---

## 🔧 TEKNİK İMPLEMENTASYON

### Seçenek 1: PyTrends (EN KOLAY)

```python
from pytrends.request import TrendReq

class GoogleTrendsCollector:
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360)
    
    async def get_us_trends(self):
        # Daily trending searches
        df = self.pytrends.trending_searches(pn='united_states')
        return df[0].tolist()[:20]
```

**장점:**
- ✅ Çalışması garanti
- ✅ Gerçek trendler
- ✅ Kolay implement

### Seçenek 2: Twitter Trends24

```python
import aiohttp
from bs4 import BeautifulSoup

async def get_twitter_trends():
    url = "https://trends24.in/united-states/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            trends = []
            for trend_card in soup.find_all('ol', class_='trend-card__list'):
                for li in trend_card.find_all('li'):
                    trend = li.text.strip()
                    if trend:
                        trends.append(trend)
            
            return trends[:20]
```

### Seçenek 3: YouTube API

```python
from googleapiclient.discovery import build

class YouTubeTrendsCollector:
    def __init__(self, api_key):
        self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    async def get_us_trends(self):
        request = self.youtube.videos().list(
            part='snippet',
            chart='mostPopular',
            regionCode='US',
            maxResults=50
        )
        response = request.execute()
        
        trends = []
        for item in response['items']:
            title = item['snippet']['title']
            trends.append(title)
        
        return trends
```

---

## 📋 KARŞILAŞTIRMA

| Platform | Gerçek Trend | API Key | Rate Limit | Ücretsiz | Önerilen |
|----------|-------------|---------|------------|----------|----------|
| **Google Trends (PyTrends)** | ✅ | ❌ | ⚠️ Orta | ✅ | ⭐⭐⭐⭐⭐ |
| **Twitter (Scraping)** | ✅ | ❌ | ✅ Yok | ✅ | ⭐⭐⭐⭐ |
| **YouTube API** | ⚠️ Video | ✅ | ⚠️ Quota | ✅ | ⭐⭐⭐ |
| **Reddit API** | ⚠️ Post | ❌ | ✅ Yok | ✅ | ⭐⭐ |
| **TikTok** | ✅ | ❌ | ⚠️ JS | ✅ | ⭐⭐⭐ |
| **Yahoo News** | ❌ Haber | ❌ | ✅ Yok | ✅ | ⭐ |
| **Google News** | ❌ Haber | ❌ | ✅ Yok | ✅ | ⭐ |

---

## 🎯 EN İYİ UYGULAMA

### Önerilen Stack:

```python
collectors = [
    GoogleTrendsCollector(),      # PyTrends - EN İYİ
    TwitterTrendsCollector(),     # Scraping (trends24.in)
    YouTubeTrendsCollector(),     # API (optional)
    TikTokTrendsCollector(),      # Scraping (optional)
]
```

### Kaldırılmalı:
- ❌ Yahoo News (haber başlıkları)
- ❌ Google News (haber başlıkları)
- ⚠️ Reddit (keyword extraction eklenebilir)

---

## 🚀 SONRAKI ADIMLAR

1. **PyTrends Ekle** → En hızlı çözüm
2. **Twitter Scraping Düzelt** → HTML parsing güncelle
3. **YouTube API Ekle** → API key ile
4. **Haber Collectors Kaldır** → Gereksiz
5. **Keyword Extraction** → Reddit için NER

---

## 📚 Kaynaklar

- PyTrends: https://pypi.org/project/pytrends/
- Twitter Trends: https://trends24.in/
- YouTube API: https://developers.google.com/youtube/v3
- TikTok Discover: https://www.tiktok.com/discover

---

## ⚡ HIZLI BAŞLANGIÇ

### 1. PyTrends Kur
```bash
pip install pytrends
```

### 2. Test Et
```python
from pytrends.request import TrendReq
pytrends = TrendReq(hl='en-US', tz=360)
trends = pytrends.trending_searches(pn='united_states')
print(trends[0].tolist())
```

### 3. Sonuç
```
['Taylor Swift', 'NFL Playoffs', 'iPhone 15', 'ChatGPT', ...]
```

✅ **GERÇEK TRENDLER!**
