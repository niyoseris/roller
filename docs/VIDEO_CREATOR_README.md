# 🎬 Video Creator - Scrolling Text + Narration

Pexels'den ücretsiz video indirir, üzerine kaydırılan metin ekler ve narration (sesli anlatım) oluşturur.

---

## 📋 Özellikler

- ✅ **Pexels API** ile ücretsiz video arama ve indirme
- ✅ **Kaydırılan metin** (scrolling text overlay)
- ✅ **Text-to-Speech narration** (Google TTS)
- ✅ **Otomatik video oluşturma** (moviepy)
- ✅ **HD video çıktısı**

---

## 🚀 Kurulum

### 1. Pexels API Key Alın

1. https://www.pexels.com/api/ adresine gidin
2. **"Get Started"** tıklayın
3. Ücretsiz hesap oluşturun
4. API key'inizi kopyalayın

### 2. API Key'i .env Dosyasına Ekleyin

`.env` dosyasını açın ve ekleyin:

```bash
PEXELS_API_KEY=your_actual_api_key_here
```

### 3. Gerekli Paketler Yüklü mü Kontrol Edin

```bash
pip install moviepy gtts Pillow imageio imageio-ffmpeg requests
```

---

## 📖 Kullanım

### Basit Kullanım

```bash
python video_creator.py
```

Bu, örnek bir video oluşturacak (NASA hakkında).

### Kendi Metninizle

`video_creator.py` dosyasındaki `main()` fonksiyonunu düzenleyin:

```python
def main():
    from dotenv import load_dotenv
    load_dotenv()
    
    # Your custom text
    text = """
    Bu kısıma istediğiniz metni yazın.
    Bu metin hem videoda kaydırılacak,
    hem de sesli olarak okunacak.
    """
    
    creator = VideoCreator()
    
    result = creator.create_video_from_pexels(
        search_query="technology",  # Pexels arama kelimesi
        text=text.strip(),
        output_filename="my_video.mp4",  # Çıktı dosya adı
        narration_lang='en',  # 'tr' for Turkish, 'en' for English
        scroll_speed=60,  # Metin kaydırma hızı (pixels/second)
        font_size=35  # Font boyutu
    )
    
    if result:
        print(f"\n✅ Video created: {result}")
```

---

## 🎨 Parametreler

### `create_video_from_pexels()`

| Parametre | Açıklama | Örnek |
|-----------|----------|-------|
| `search_query` | Pexels'de aranacak kelime | `"technology"`, `"nature"`, `"space"` |
| `text` | Videoda gösterilecek ve okunacak metin | Wikipedia summary gibi |
| `output_filename` | Çıktı video dosya adı | `"my_video.mp4"` |
| `narration_lang` | Narration dili | `'en'` (İngilizce), `'tr'` (Türkçe) |
| `scroll_speed` | Metin kaydırma hızı (pixels/saniye) | `30` (yavaş), `60` (orta), `100` (hızlı) |
| `font_size` | Font boyutu | `30` (küçük), `40` (orta), `50` (büyük) |

---

## 📁 Çıktılar

Videolar şu klasörlerde oluşturulur:

```
output_videos/      # Final videolar
temp_videos/        # Geçici dosyalar (otomatik silinir)
```

---

## 🧪 Test

### 1. Pexels API Test

```python
from video_creator import VideoCreator
from dotenv import load_dotenv

load_dotenv()
creator = VideoCreator()

# Video ara
video_info = creator.search_pexels_video("technology")
if video_info:
    print("✅ Pexels API çalışıyor!")
    print(f"Video: {video_info}")
else:
    print("❌ Pexels API key kontrol edin!")
```

### 2. Video Oluşturma Test

```bash
python video_creator.py
```

Başarılı olursa:
```
✅ Video created successfully: output_videos/nasa_video.mp4
```

---

## 🔧 Sorun Giderme

### Problem: "Pexels API key not provided"

**Çözüm:** `.env` dosyasında `PEXELS_API_KEY` ayarlandığından emin olun.

```bash
# .env dosyasını kontrol edin
cat .env | grep PEXELS
```

### Problem: "No videos found"

**Çözüm:** Farklı bir arama kelimesi deneyin:
- ❌ "asdfqwer" (anlamsız kelime)
- ✅ "technology", "nature", "city", "ocean"

### Problem: MoviePy hatası

**Çözüm:** FFmpeg yüklü mü kontrol edin:

```bash
# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg
```

### Problem: Text görünmüyor

**Çözüm:** Font ayarlarını değiştirin:

```python
font_size=50  # Daha büyük font
scroll_speed=40  # Daha yavaş kaydırma
```

---

## 📊 Örnek Kullanım Senaryoları

### 1. Wikipedia Summary Video

```python
text = """
NASA is an independent agency of the U.S. federal government 
responsible for the civil space program, aeronautics research, 
and space research.
"""

creator.create_video_from_pexels(
    search_query="nasa space rocket",
    text=text,
    output_filename="nasa_summary.mp4",
    narration_lang='en'
)
```

### 2. Türkçe Video

```python
text = """
Yapay zeka, makinelerin insan benzeri görevleri 
yerine getirmesini sağlayan teknolojilerin genel adıdır.
"""

creator.create_video_from_pexels(
    search_query="artificial intelligence robot",
    text=text,
    output_filename="ai_video_tr.mp4",
    narration_lang='tr'
)
```

### 3. Hızlı Scrolling

```python
creator.create_video_from_pexels(
    search_query="fast technology",
    text=short_text,
    output_filename="fast_video.mp4",
    scroll_speed=100,  # 2x hızlı
    font_size=45
)
```

---

## 🎬 Workflow

1. **Pexels API** → Video ara
2. **Download** → HD videoyu indir
3. **gTTS** → Text'i sesli anlatım yap
4. **MoviePy** → Video + Scrolling Text + Narration
5. **Output** → `output_videos/` klasörüne kaydet

---

## 🆓 API Limitleri

### Pexels (Ücretsiz)

- ✅ 200 requests/hour
- ✅ Unlimited downloads
- ✅ HD video access
- ✅ Commercial use OK

Bizim kullanım: **Her video = 1 request**

---

## 💡 İpuçları

1. **Kısa metinler** daha iyi çalışır (200-300 kelime)
2. **scroll_speed** video uzunluğuna göre ayarlayın
3. **search_query** ile video içeriği eşleşsin
4. **Türkçe narration** için `narration_lang='tr'` kullanın
5. **Font size** video çözünürlüğüne göre ayarlayın

---

## 📝 Örnekler

Hazır örnekler için:

```bash
python video_creator.py  # NASA example
```

Veya kendi örneklerinizi oluşturun!

**Başarılı videolar! 🎉**
