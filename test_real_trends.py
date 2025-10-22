"""
Test script for REAL trend collectors
Tests each collector independently to verify they return actual trends, not news
"""

import asyncio
import logging
from real_trend_collectors import (
    GoogleTrendsCollector,
    TwitterTrendsCollector,
    RedditTrendingCollector,
    TikTokTrendsCollector,
    BingTrendsCollector
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_real_trends():
    """Test all real trend collectors"""
    print("=" * 70)
    print("🔍 GERÇEK TREND COLLECTORS TEST")
    print("=" * 70)
    
    collectors = [
        ("Google Trends (PyTrends)", GoogleTrendsCollector()),
        ("Twitter Trends", TwitterTrendsCollector()),
        ("Reddit Trending Keywords", RedditTrendingCollector()),
        ("TikTok Trends", TikTokTrendsCollector()),
        ("Bing Trends", BingTrendsCollector())
    ]
    
    all_trends = []
    
    for name, collector in collectors:
        print(f"\n{'='*70}")
        print(f"📊 Testing: {name}")
        print(f"{'='*70}")
        
        try:
            trends = await collector.get_us_trends()
            
            if trends:
                print(f"✅ Found {len(trends)} trends:")
                for i, trend in enumerate(trends[:10], 1):
                    # Check if it looks like a news headline (too long, contains "-")
                    is_news = len(trend) > 80 or " - " in trend
                    emoji = "⚠️" if is_news else "✓"
                    print(f"   {i:2d}. {emoji} {trend[:70]}")
                
                all_trends.extend(trends)
            else:
                print(f"❌ No trends found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n{'='*70}")
    print(f"📈 SUMMARY")
    print(f"{'='*70}")
    print(f"Total unique trends collected: {len(set(all_trends))}")
    
    # Analyze results
    print(f"\n{'='*70}")
    print(f"🔍 TREND QUALITY ANALYSIS")
    print(f"{'='*70}")
    
    news_like = []
    real_trends = []
    
    for trend in set(all_trends):
        # Heuristic: News headlines are usually long and contain source markers
        if len(trend) > 80 or " - " in trend or "says" in trend.lower():
            news_like.append(trend)
        else:
            real_trends.append(trend)
    
    print(f"✅ Real Trends: {len(real_trends)}")
    print(f"⚠️  News-like items: {len(news_like)}")
    
    if real_trends:
        print(f"\n✅ Sample REAL Trends:")
        for trend in real_trends[:15]:
            print(f"   • {trend}")
    
    if news_like:
        print(f"\n⚠️  Sample NEWS Headlines (should be avoided):")
        for news in news_like[:5]:
            print(f"   • {news[:70]}...")
    
    print(f"\n{'='*70}")
    print(f"🎯 RECOMMENDATION")
    print(f"{'='*70}")
    
    if len(real_trends) > len(news_like):
        print("✅ GOOD: Majority are real trends!")
    else:
        print("⚠️  WARNING: Too many news headlines!")
        print("   Consider adjusting collectors or adding filtering.")
    
    print(f"\n{'='*70}")

if __name__ == "__main__":
    asyncio.run(test_real_trends())
