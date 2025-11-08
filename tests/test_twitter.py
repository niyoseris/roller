"""
Test script for Twitter integration
"""

import asyncio
import logging
from twitter_poster import TwitterPoster

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


async def test_twitter_poster():
    """Test Twitter posting functionality"""
    print("=" * 60)
    print("Twitter Poster Test")
    print("=" * 60)
    
    # Initialize Twitter poster
    print("\n1. Initializing Twitter poster...")
    twitter = TwitterPoster()
    
    # Check if enabled
    print(f"\n2. Twitter posting enabled: {twitter.is_enabled()}")
    
    if not twitter.is_enabled():
        print("\n⚠️ Twitter posting is disabled!")
        print("\nTo enable Twitter posting, set these environment variables:")
        print("  export TWITTER_API_KEY='your_api_key'")
        print("  export TWITTER_API_SECRET='your_api_secret'")
        print("  export TWITTER_ACCESS_TOKEN='your_access_token'")
        print("  export TWITTER_ACCESS_TOKEN_SECRET='your_access_token_secret'")
        print("  export TWITTER_BEARER_TOKEN='your_bearer_token'  # Optional")
        print("\nOr set them in your shell configuration file (~/.zshrc or ~/.bashrc)")
        return
    
    # Test tweet formatting
    print("\n3. Testing tweet formatting...")
    test_trend = "#NBA"
    test_category = "Sports"
    test_article_id = 1234  # Example article ID
    test_url = f"https://roll.wiki/summary/{test_article_id}"
    
    tweet_text = twitter.format_tweet(test_trend, test_category, test_url)
    print(f"\nFormatted tweet ({len(tweet_text)} chars):")
    print("-" * 60)
    print(tweet_text)
    print("-" * 60)
    
    # Ask for confirmation before posting
    print("\n4. Ready to post test tweet")
    response = input("\nDo you want to post this test tweet? (yes/no): ").strip().lower()
    
    if response == 'yes':
        print("\n5. Posting test tweet...")
        success = await twitter.post_tweet_async(test_trend, test_category, test_article_id)
        
        if success:
            print("\n✅ Test tweet posted successfully!")
        else:
            print("\n❌ Failed to post test tweet")
    else:
        print("\n⏭️ Skipping tweet posting")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_twitter_poster())
