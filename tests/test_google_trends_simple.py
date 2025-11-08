#!/usr/bin/env python3
"""
Basit Google Trends Test
Headless Chrome ile ekran görüntüsü test eder
"""

import asyncio
import logging
from google_trends_collector import GoogleTrendsCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test():
    print("=" * 60)
    print("🔍 Google Trends Screenshot Test")
    print("=" * 60)
    print()
    
    collector = GoogleTrendsCollector(use_gemini=True)
    
    print("📸 Ekran görüntüsü alınıyor...")
    print("   (İlk çalıştırmada ChromeDriver indirme olabilir)")
    print()
    
    trends = await collector.get_trends_from_screenshot()
    
    print()
    print("=" * 60)
    print(f"✅ {len(trends)} trend bulundu:")
    print("=" * 60)
    
    if trends:
        for i, trend in enumerate(trends, 1):
            print(f"{i:2}. {trend}")
    else:
        print("❌ Trend bulunamadı")
        print()
        print("Sorun giderme:")
        print("1. Chrome kurulu mu? brew install --cask google-chrome")
        print("2. Gemini API key ekli mi? (.env dosyasında)")
        print("3. İnternet bağlantısı var mı?")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test())
