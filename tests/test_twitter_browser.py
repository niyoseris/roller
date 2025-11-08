"""
Test script for Twitter Browser Poster
Tests login and posting functionality
"""

import asyncio
import logging
from twitter_browser_poster import TwitterBrowserPoster

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_browser_poster():
    """Test the Twitter browser poster"""
    print("=" * 60)
    print("Testing Twitter Browser Poster")
    print("=" * 60)
    
    # Initialize poster
    poster = TwitterBrowserPoster()
    
    if not poster.is_enabled():
        print("❌ Twitter browser poster is not enabled")
        print("Please configure TWITTER_USERNAME and TWITTER_PASSWORD in .env")
        return
    
    print("✅ Twitter browser poster initialized")
    
    # Test posting a tweet
    print("\n" + "=" * 60)
    print("Testing tweet posting...")
    print("=" * 60)
    
    trend = "Python Programming"
    category = "Technology"
    article_id = 1234  # Example article ID
    
    success = await poster.post_tweet_async(trend, category, article_id)
    
    if success:
        print("✅ Test tweet posted successfully!")
    else:
        print("❌ Failed to post test tweet")
    
    # Close browser
    print("\nClosing browser...")
    poster.close()
    print("✅ Test completed")

if __name__ == "__main__":
    asyncio.run(test_browser_poster())
