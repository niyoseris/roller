"""
Test the new tweet format
"""

from twitter_poster import TwitterPoster

def test_formats():
    """Test different tweet formats"""
    poster = TwitterPoster()
    
    # Test different categories and trends
    test_cases = [
        ("Elon Musk", "Business", "https://roll.wiki/summary/1234"),
        ("NBA Finals", "Sports", "https://roll.wiki/summary/5678"),
        ("Python Programming", "Technology", "https://roll.wiki/summary/9012"),
        ("Taylor Swift", "Music", "https://roll.wiki/summary/3456"),
        ("Climate Change", "Environment", "https://roll.wiki/summary/7890"),
    ]
    
    print("=" * 70)
    print("NEW TWEET FORMAT EXAMPLES")
    print("=" * 70)
    
    for trend, category, url in test_cases:
        tweet = poster.format_tweet(trend, category, url)
        print(f"\n📌 Trend: {trend} | Category: {category}")
        print(f"📝 Tweet ({len(tweet)} chars):")
        print("-" * 70)
        print(tweet)
        print("-" * 70)

if __name__ == "__main__":
    test_formats()
