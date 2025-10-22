"""
Test GetDayTrends collector
"""
import asyncio
import logging
from real_trend_collectors import GetDayTrendsCollector

# Enable logging
logging.basicConfig(level=logging.INFO)

async def test_getdaytrends():
    """Test GetDayTrends collector"""
    
    print("🧪 Testing GetDayTrends Collector")
    print("=" * 70)
    
    collector = GetDayTrendsCollector()
    
    try:
        trends = await collector.get_us_trends()
        
        if trends:
            print(f"✅ GetDayTrends: Found {len(trends)} trends")
            print(f"\nTop 10 Trends:")
            for i, trend in enumerate(trends[:10], 1):
                print(f"  {i}. {trend}")
        else:
            print(f"⚠️  GetDayTrends: No trends found")
    except Exception as e:
        print(f"❌ GetDayTrends: Error - {e}")

if __name__ == "__main__":
    asyncio.run(test_getdaytrends())
