#!/usr/bin/env python3
"""
Google Trends OCR Test
Screenshot'tan text extract edip trend analizi yapar
"""

import asyncio
import logging
import os
from google_trends_collector import GoogleTrendsCollector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test():
    print("=" * 80)
    print("🔍 Google Trends OCR + Trend Analysis Test")
    print("=" * 80)
    print()
    
    # Check Gemini API key
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key or gemini_key == 'your_gemini_api_key_here':
        print("❌ Gemini API key eksik!")
        print("   .env dosyasına ekleyin: GEMINI_API_KEY=your_key")
        print("   API key: https://makersuite.google.com/app/apikey")
        return
    
    print(f"✅ Gemini API key: {gemini_key[:15]}...")
    print()
    print("-" * 80)
    print("📋 İşlem Adımları:")
    print("   1. Screenshot al (headless Chrome)")
    print("   2. OCR ile tüm metinleri çıkar (Gemini Vision)")
    print("   3. Metinleri text dosyasına kaydet")
    print("   4. Text'i analiz et ve trendleri bul (Gemini)")
    print("-" * 80)
    print()
    
    # Create collector with Gemini
    collector = GoogleTrendsCollector(use_gemini=True)
    
    print("🚀 Başlıyor...")
    print()
    
    # Get trends - this will now do OCR + text analysis
    trends = await collector.get_trends_from_screenshot()
    
    print()
    print("=" * 80)
    print(f"📊 Sonuç: {len(trends)} trend bulundu")
    print("=" * 80)
    print()
    
    if trends:
        print("🎯 Bulunan Trendler:")
        print()
        for i, trend in enumerate(trends, 1):
            print(f"  {i:2}. {trend}")
    else:
        print("❌ Trend bulunamadı")
        print()
        print("Sorun giderme:")
        print("  1. screenshots/ klasörünü kontrol edin")
        print("  2. .txt dosyasını okuyun: cat screenshots/*.txt")
        print("  3. Screenshot'a bakın: open screenshots/*.png")
    
    print()
    print("=" * 80)
    
    # Show files
    import glob
    print()
    print("📁 Oluşturulan Dosyalar:")
    print()
    
    screenshots = sorted(glob.glob("screenshots/google_trends_*.png"))
    if screenshots:
        latest_screenshot = screenshots[-1]
        print(f"  📸 Screenshot: {latest_screenshot}")
    
    text_files = sorted(glob.glob("screenshots/google_trends_*.txt"))
    if text_files:
        latest_text = text_files[-1]
        print(f"  📝 Text File: {latest_text}")
        
        # Show first few lines of text file
        print()
        print("  📄 Text dosyası önizleme:")
        print("  " + "-" * 70)
        try:
            with open(latest_text, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:15]  # First 15 lines
                for line in lines:
                    print(f"  {line.rstrip()}")
                if len(lines) == 15:
                    print("  ...")
        except Exception as e:
            print(f"  ❌ Okuma hatası: {e}")
    
    print()
    print("=" * 80)
    print()
    print("💡 Dosyaları görüntülemek için:")
    print(f"   open screenshots/")
    print()

if __name__ == "__main__":
    asyncio.run(test())
