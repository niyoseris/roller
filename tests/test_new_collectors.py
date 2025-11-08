"""
Test new trend collectors
"""
import asyncio
import logging
from real_trend_collectors import (
    YandexTrendsCollector,
    BraveSearchTrendsCollector,
    DuckDuckGoTrendsCollector,
    BingTrendsCollector
)

# Enable logging
logging.basicConfig(level=logging.INFO)

async def test_collectors():
    """Test all new collectors"""
    
    collectors = [
        ("Yandex", YandexTrendsCollector()),
        ("Brave Search", BraveSearchTrendsCollector()),
        ("DuckDuckGo", DuckDuckGoTrendsCollector()),
        ("Bing", BingTrendsCollector())
    ]
    
    print("🧪 Testing New Trend Collectors")
    print("=" * 70)
    
    for name, collector in collectors:
        print(f"\n📊 Testing {name}...")
        print("-" * 70)
        
        try:
            trends = await collector.get_us_trends()
            
            if trends:
                print(f"✅ {name}: Found {len(trends)} trends")
                print(f"   First 5: {trends[:5]}")
            else:
                print(f"⚠️  {name}: No trends found")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
        
        print()
        await asyncio.sleep(2)  # Be nice to servers

if __name__ == "__main__":
    asyncio.run(test_collectors())
