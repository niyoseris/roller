"""
Twitter Poster - Automatically posts articles to Twitter
"""

import logging
import tweepy
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class TwitterPoster:
    """Handles posting articles to Twitter"""
    
    def __init__(self, api_key: str = None, api_secret: str = None, 
                 access_token: str = None, access_token_secret: str = None,
                 bearer_token: str = None):
        """
        Initialize Twitter API client
        
        Args:
            api_key: Twitter API key (Consumer Key)
            api_secret: Twitter API secret (Consumer Secret)
            access_token: Twitter Access Token
            access_token_secret: Twitter Access Token Secret
            bearer_token: Twitter Bearer Token (for API v2)
        """
        self.enabled = False
        self.client = None
        
        # Get credentials from parameters or environment variables
        self.api_key = api_key or os.getenv('TWITTER_API_KEY')
        self.api_secret = api_secret or os.getenv('TWITTER_API_SECRET')
        self.access_token = access_token or os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = access_token_secret or os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        self.bearer_token = bearer_token or os.getenv('TWITTER_BEARER_TOKEN')
        
        # Initialize Twitter client
        self._init_client()
    
    def _init_client(self):
        """Initialize Twitter API client"""
        try:
            if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
                logger.warning("Twitter credentials not configured. Twitter posting disabled.")
                logger.info("To enable Twitter posting, set these environment variables:")
                logger.info("  - TWITTER_API_KEY")
                logger.info("  - TWITTER_API_SECRET")
                logger.info("  - TWITTER_ACCESS_TOKEN")
                logger.info("  - TWITTER_ACCESS_TOKEN_SECRET")
                return
            
            # Create Twitter API v2 client
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret
            )
            
            self.enabled = True
            logger.info("✅ Twitter API client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Twitter client: {e}")
            logger.warning("Twitter posting will be disabled")
            self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if Twitter posting is enabled"""
        return self.enabled
    
    def format_tweet(self, trend: str, category: str, roll_wiki_url: str) -> str:
        """
        Format an engaging tweet optimized for Twitter algorithm (~140 chars)
        
        Args:
            trend: The trending topic
            category: The article category
            roll_wiki_url: The roll.wiki article URL
            
        Returns:
            Formatted tweet text with relevant keywords and hashtags
        """
        # Clean trend name
        import re
        clean_trend = re.sub(r'\d+[KkMm]?\s*$', '', trend).strip()
        clean_trend = clean_trend.lstrip('#')
        
        # Category-specific hashtags and keywords for Twitter algorithm
        category_hashtags = {
            "Politics": "#Politics #News #Breaking #WorldNews #Government",
            "Sports": "#Sports #Game #Victory #Championship #Athletes",
            "Entertainment": "#Entertainment #Celebrity #Movies #TV #Shows",
            "Music": "#Music #NewMusic #Artist #Song #Concert",
            "Technology": "#Tech #Innovation #AI #Technology #Digital",
            "Business": "#Business #Economy #Finance #Markets #Investing",
            "Science": "#Science #Research #Discovery #Innovation #STEM",
            "Medicine": "#Health #Medicine #Healthcare #Wellness #Medical",
            "Film": "#Film #Movies #Cinema #Hollywood #BoxOffice",
            "Food": "#Food #Foodie #Cooking #Recipe #Delicious",
            "Fashion": "#Fashion #Style #Trend #Designer #OOTD",
            "Environment": "#Climate #Environment #Sustainability #GreenEnergy",
            "Arts": "#Art #Artist #Creative #Design #Gallery",
            "Literature": "#Books #Reading #Author #Literature #BookLovers",
            "Education": "#Education #Learning #Students #Knowledge #School",
            "Culture": "#Culture #Society #History #Tradition #Heritage"
        }
        
        # Get relevant hashtags for category
        hashtags = category_hashtags.get(category, "#Trending #News #Viral")
        # Take first 3 hashtags to keep tweet concise
        hashtag_list = hashtags.split()[:3]
        hashtag_str = " ".join(hashtag_list)
        
        # Engaging tweet variations
        templates = [
            f"🔥 Trending: {clean_trend}\n📖 Learn more {hashtag_str}\n🔗 {roll_wiki_url}",
            f"📰 What's {clean_trend}?\n✨ Quick summary {hashtag_str}\n🔗 {roll_wiki_url}",
            f"🌟 {clean_trend} explained\n💡 Everything you need to know {hashtag_str}\n🔗 {roll_wiki_url}",
            f"🚀 {clean_trend} is trending!\n📚 Read the full story {hashtag_str}\n🔗 {roll_wiki_url}",
            f"💬 Everyone's talking about {clean_trend}\n📖 Get informed {hashtag_str}\n🔗 {roll_wiki_url}"
        ]
        
        # Choose template based on trend name length
        import random
        random.seed(hash(clean_trend))  # Consistent selection for same trend
        
        # Try templates until one fits within 280 chars (Twitter limit)
        for template in templates:
            tweet = template
            if len(tweet) <= 280:
                return tweet
        
        # Fallback: Simple format if all templates are too long
        short_hashtags = hashtag_list[0] if hashtag_list else "#Trending"
        return f"🔥 {clean_trend}\n{short_hashtags}\n🔗 {roll_wiki_url}"
    
    def post_tweet(self, trend: str, category: str, article_id: Optional[int], tweet_text: str = None) -> bool:
        """
        Post a tweet about the article
        
        Args:
            trend: The trending topic
            category: The article category
            article_id: The roll.wiki article ID
            
        Returns:
            True if tweet was posted successfully, False otherwise
        """
        if not self.enabled:
            logger.info("Twitter posting is disabled - skipping tweet")
            return False
        
        if not article_id:
            logger.warning("No article_id provided - cannot post tweet")
            return False
        
        try:
            # Create roll.wiki URL with article_id
            # Format: https://roll.wiki/summary/1462
            roll_wiki_url = f"https://roll.wiki/summary/{article_id}"
            
            # Use provided tweet_text or format a new one
            if not tweet_text:
                tweet_text = self.format_tweet(trend, category, roll_wiki_url)
            
            # Post tweet
            logger.info(f"🐦 Posting tweet: {tweet_text[:50]}...")
            response = self.client.create_tweet(text=tweet_text)
            
            if response.data:
                tweet_id = response.data['id']
                logger.info(f"✅ Tweet posted successfully! Tweet ID: {tweet_id}")
                logger.info(f"   View at: https://twitter.com/i/web/status/{tweet_id}")
                return True
            else:
                logger.warning("⚠️ Tweet posted but no response data received")
                return True
                
        except tweepy.TweepyException as e:
            logger.error(f"❌ Twitter API error: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error posting tweet: {e}")
            return False
    
    async def post_tweet_async(self, trend: str, category: str, article_id: Optional[int], tweet_text: str = None) -> bool:
        """
        Async wrapper for post_tweet
        
        Args:
            trend: The trending topic
            category: The article category
            article_id: The roll.wiki article ID
            
        Returns:
            True if tweet was posted successfully, False otherwise
        """
        # tweepy doesn't support async natively, so we run it in the event loop
        import asyncio
        return await asyncio.to_thread(self.post_tweet, trend, category, article_id, tweet_text)
