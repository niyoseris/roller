"""
Test Together AI integration
"""

import asyncio
from together_ai_analyzer import TogetherAIAnalyzer

async def test_together_ai():
    """Test Together AI analyzer"""
    print("=" * 70)
    print("Testing Together AI Integration")
    print("=" * 70)
    
    analyzer = TogetherAIAnalyzer()
    
    if not await analyzer.is_available():
        print("❌ Together AI not available")
        return
    
    print("✅ Together AI is available\n")
    
    # Test 1: Categorization
    print("-" * 70)
    print("Test 1: Categorization")
    print("-" * 70)
    
    trend = "Elon Musk"
    summary = "Elon Musk is a businessman and investor known for founding Tesla and SpaceX."
    
    category = await analyzer.categorize_trend(trend, summary)
    print(f"Trend: {trend}")
    print(f"Category: {category}\n")
    
    # Test 2: Tweet Generation
    print("-" * 70)
    print("Test 2: Tweet Generation")
    print("-" * 70)
    
    trend = "Python Programming"
    category = "Technology"
    summary = "Python is a high-level programming language known for its simplicity and versatility in software development."
    roll_wiki_url = "https://roll.wiki/summary/1234"
    
    tweet = await analyzer.generate_tweet(trend, category, summary, roll_wiki_url)
    print(f"\nGenerated Tweet ({len(tweet)} chars):")
    print("-" * 70)
    print(tweet)
    print("-" * 70)
    
    # Test 3: Multiple tweet generations
    print("\n" + "=" * 70)
    print("Test 3: Multiple Tweet Examples")
    print("=" * 70)
    
    test_cases = [
        ("NBA Finals", "Sports", "The NBA Finals is the championship series of the NBA.", "https://roll.wiki/summary/5678"),
        ("Climate Change", "Environment", "Climate change refers to long-term shifts in temperatures and weather patterns.", "https://roll.wiki/summary/9012"),
        ("Taylor Swift", "Music", "Taylor Swift is an American singer-songwriter known for her narrative songwriting.", "https://roll.wiki/summary/3456"),
    ]
    
    for trend, category, summary, url in test_cases:
        tweet = await analyzer.generate_tweet(trend, category, summary, url)
        print(f"\n📌 {trend} - {category}")
        print(f"Tweet ({len(tweet)} chars): {tweet[:100]}...")

if __name__ == "__main__":
    asyncio.run(test_together_ai())
