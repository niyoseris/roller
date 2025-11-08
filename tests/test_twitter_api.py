"""
Test Twitter API connection and posting
"""

import asyncio
import logging
from twitter_poster import TwitterPoster

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_api_poster():
    """Test the Twitter API poster"""
    print("=" * 60)
    print("Testing Twitter API Poster")
    print("=" * 60)
    
    # Initialize poster
    poster = TwitterPoster()
    
    if not poster.is_enabled():
        print("❌ Twitter API poster is not enabled")
        print("Please check your Twitter API credentials in .env")
        return
    
    print("✅ Twitter API poster initialized")
    
    # Test posting a tweet
    print("\n" + "=" * 60)
    print("Testing tweet posting...")
    print("=" * 60)
    
    trend = "Python Programming"
    category = "Technology"
    article_id = 1234  # Example article ID
    
    success = await poster.post_tweet_async(trend, category, article_id)
    
    if success:
        print("✅ Test tweet posted successfully via API!")
    else:
        print("❌ Failed to post test tweet via API")
        print("Check the error messages above for details")
    
    print("✅ Test completed")

if __name__ == "__main__":
    asyncio.run(test_api_poster())
