"""
Quick test script to verify the application works
Tests one cycle without waiting 60 minutes
"""

import asyncio
import sys
from main import TrendAgent

async def quick_test():
    """Run a quick test of the trend collection system"""
    print("=" * 60)
    print("Starting Quick Test")
    print("=" * 60)
    
    agent = TrendAgent(enable_web_monitor=False)
    
    # Test trend collection
    print("\n1. Testing trend collection...")
    trends = await agent.collect_trends()
    print(f"   Collected {len(trends)} unique trends")
    
    if trends:
        print(f"\n   Sample trends (first 5):")
        for i, trend in enumerate(trends[:5], 1):
            print(f"   {i}. {trend}")
    
    # Test Wikipedia finder with first trend
    if trends:
        print(f"\n2. Testing Wikipedia finder with: '{trends[0]}'")
        wiki_url = await agent.wikipedia_finder.find_article(trends[0])
        if wiki_url:
            print(f"   Found: {wiki_url}")
            
            # Test categorization
            summary = await agent.wikipedia_finder.get_article_summary(wiki_url)
            category = agent.categorize_trend(trends[0], summary)
            print(f"   Category: {category}")
        else:
            print("   No Wikipedia article found")
    
    # Test URL tracker
    print("\n3. Testing URL tracker...")
    test_url = "https://en.wikipedia.org/wiki/Test"
    is_processed = agent.url_tracker.is_processed(test_url)
    print(f"   Is '{test_url}' processed? {is_processed}")
    
    print("\n" + "=" * 60)
    print("Quick test completed!")
    print(f"Total processed URLs in database: {agent.url_tracker.get_count()}")
    print("=" * 60)

if __name__ == "__main__":
    try:
        asyncio.run(quick_test())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError during test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
