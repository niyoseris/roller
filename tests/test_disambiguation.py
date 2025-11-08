"""
Test disambiguation page detection
"""

import asyncio
from main import TrendAgent

async def test_disambiguation():
    """Test disambiguation detection"""
    
    agent = TrendAgent(enable_web_monitor=False, enable_video=False, enable_twitter=False)
    
    print("=" * 70)
    print("Testing Disambiguation Page Detection")
    print("=" * 70)
    
    # Test cases
    test_trends = [
        "Volkov",  # Disambiguation page
        "Python Programming Language",  # Real article
        "Mercury",  # Disambiguation page
    ]
    
    for trend in test_trends:
        print(f"\n{'='*70}")
        print(f"Testing: {trend}")
        print('='*70)
        
        result = await agent.process_trend(trend)
        
        if result:
            print(f"✅ Processed successfully")
        else:
            print(f"⏭️  Skipped")
        
        print()

if __name__ == "__main__":
    asyncio.run(test_disambiguation())
