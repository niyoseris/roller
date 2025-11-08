#!/usr/bin/env python3
"""
Google Trends Screenshot Test - Yeni URL ile
https://trends.google.com/trending?geo=US&hl=tr
"""

import asyncio
import logging
import os
from google_trends_collector import GoogleTrendsCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test():
    print("=" * 70)
    print("🔍 Google Trends Screenshot Test - Yeni URL")
    print("=" * 70)
    print()
    print("📍 URL: https://trends.google.com/trending?geo=US&hl=tr")
    print()
    
    # Check Gemini API key
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key or gemini_key == 'your_gemini_api_key_here':
        print("⚠️  Gemini API key eksik!")
        print("   .env dosyasına ekleyin: GEMINI_API_KEY=your_key")
        print("   API key: https://makersuite.google.com/app/apikey")
        print()
        use_gemini = False
    else:
        print(f"✅ Gemini API key bulundu: {gemini_key[:10]}...")
        use_gemini = True
    
    print()
    print("-" * 70)
    print("📸 Ekran görüntüsü alınıyor...")
    print()
    
    collector = GoogleTrendsCollector(use_gemini=use_gemini)
    
    if use_gemini:
        print("🤖 Gemini Flash ile analiz edilecek...")
    else:
        print("⚠️  Sadece ekran görüntüsü alınacak (Gemini analizi yok)")
    
    print()
    
    trends = await collector.get_trends_from_screenshot()
    
    print()
    print("=" * 70)
    print(f"📊 Sonuç: {len(trends)} trend bulundu")
    print("=" * 70)
    print()
    
    if trends:
        for i, trend in enumerate(trends, 1):
            print(f"{i:2}. {trend}")
    else:
        print("❌ Trend bulunamadı")
        print()
        if not use_gemini:
            print("💡 İpucu: Gemini API key eklerseniz analiz çalışır")
        else:
            print("Sorun giderme:")
            print("1. Screenshot klasörünü kontrol edin: ls -la screenshots/")
            print("2. Son screenshot'a bakın: open screenshots/*.png")
            print("3. İnternet bağlantısı var mı?")
    
    print()
    print("=" * 70)
    
    # Show screenshot location
    import glob
    screenshots = sorted(glob.glob("screenshots/google_trends_*.png"))
    if screenshots:
        latest = screenshots[-1]
        print(f"📸 Ekran görüntüsü: {latest}")
        print(f"   Görmek için: open {latest}")
    
    print()

if __name__ == "__main__":
    asyncio.run(test())
