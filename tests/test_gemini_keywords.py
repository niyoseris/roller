#!/usr/bin/env python3
"""Test Gemini video keyword generation"""

import asyncio
import sys
import logging
from gemini_analyzer import GeminiAnalyzer

# Enable logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

async def test_keywords():
    """Test video keyword generation"""
    
    analyzer = GeminiAnalyzer()
    
    # Test cases
    topics = [
        "Zohran Mamdani",
        "Elon Musk",
        "New York Mayor"
    ]
    
    print("🎬 Testing Gemini Video Keywords\n")
    print("=" * 60)
    
    for topic in topics:
        print(f"\n📌 Topic: {topic}")
        print("-" * 60)
        
        try:
            keywords = await analyzer.get_video_search_keywords(topic, max_keywords=5)
            
            print(f"✅ Generated {len(keywords)} keywords:")
            for i, keyword in enumerate(keywords, 1):
                print(f"   {i}. {keyword}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_keywords())
