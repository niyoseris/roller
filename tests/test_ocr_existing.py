#!/usr/bin/env python3
"""
Mevcut screenshot ile OCR test
"""

import asyncio
import logging
import os
import glob
from google_trends_collector import GoogleTrendsCollector

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

async def test():
    print("=" * 80)
    print("🔍 Mevcut Screenshot ile OCR Test")
    print("=" * 80)
    print()
    
    # Check Gemini API key
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key or gemini_key == 'your_gemini_api_key_here':
        print("❌ Gemini API key eksik!")
        print("   .env dosyasına ekleyin: GEMINI_API_KEY=your_key")
        return
    
    print(f"✅ Gemini API key bulundu")
    print()
    
    # Find existing screenshot
    screenshots = sorted(glob.glob("screenshots/google_trends_*.png"))
    if not screenshots:
        print("❌ screenshots/ klasöründe screenshot bulunamadı")
        print("   Önce screenshot alın: python test_trends_screenshot.py")
        return
    
    screenshot_path = screenshots[-1]
    print(f"📸 Screenshot: {screenshot_path}")
    print()
    
    # Create collector
    collector = GoogleTrendsCollector(use_gemini=True)
    
    print("-" * 80)
    print("📝 Step 1: OCR ile text extraction...")
    print("-" * 80)
    
    # Extract text
    extracted_text = await collector.extract_text_from_screenshot(screenshot_path)
    
    if not extracted_text:
        print("❌ Text extraction başarısız")
        return
    
    print(f"✅ {len(extracted_text)} karakter text çıkarıldı")
    print()
    
    print("-" * 80)
    print("💾 Step 2: Text dosyasına kaydetme...")
    print("-" * 80)
    
    # Save to file
    text_path = await collector.save_text_to_file(extracted_text, screenshot_path)
    
    if text_path:
        print(f"✅ Kaydedildi: {text_path}")
        print()
        
        # Show preview
        print("-" * 80)
        print("📄 Text Önizleme (ilk 20 satır):")
        print("-" * 80)
        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:20]
                for line in lines:
                    print(line.rstrip())
                if len(lines) == 20:
                    print("...")
        except Exception as e:
            print(f"❌ Okuma hatası: {e}")
        print()
    
    print("-" * 80)
    print("🔍 Step 3: Trend analizi...")
    print("-" * 80)
    
    # Analyze for trends
    trends = await collector.analyze_text_for_trends(extracted_text)
    
    print()
    print("=" * 80)
    print(f"📊 Sonuç: {len(trends)} trend bulundu")
    print("=" * 80)
    print()
    
    if trends:
        print("🎯 Trendler:")
        for i, trend in enumerate(trends, 1):
            print(f"  {i:2}. {trend}")
    else:
        print("❌ Trend bulunamadı")
    
    print()
    print("=" * 80)
    print()
    print("💡 Text dosyasını görüntüle:")
    print(f"   cat {text_path}")
    print()

if __name__ == "__main__":
    asyncio.run(test())
