"""
Agentic Trend Collector Application
Collects US trends from multiple platforms and submits Wikipedia articles to roll.wiki
"""

import asyncio
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Set, Optional
import aiohttp
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from real_trend_collectors import (
    TwitterTrendsCollector,
    RedditTrendingCollector,
    GetDayTrendsCollector
)
from wikipedia_finder import WikipediaFinder
from url_tracker import URLTracker
from web_monitor import WebMonitor
from ollama_analyzer import OllamaAnalyzer
from together_ai_analyzer import TogetherAIAnalyzer
from twitter_poster import TwitterPoster
from video_creator import VideoCreator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trend_collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
ROLL_WIKI_API = "https://roll.wiki/api/v1/summarize"
SECRET = "laylaylom"
REQUEST_DELAY = 1800  # 30 minutes (1800 seconds) between requests
CYCLE_INTERVAL = 3600  # 60 minutes in seconds

CATEGORIES = [
    "Architecture", "Arts", "Business", "Culture", "Dance", "Economics",
    "Education", "Engineering", "Entertainment", "Environment", "Fashion",
    "Film", "Food", "Geography", "History", "Literature", "Medicine",
    "Music", "Philosophy", "Politics", "Psychology", "Religion", "Science",
    "Sports", "Technology", "Theater", "Transportation"
]


class TrendAgent:
    """Main agent that orchestrates trend collection and submission"""
    
    def __init__(self, enable_web_monitor=True, ollama_model=None, enable_twitter=True, enable_video=False, use_together_ai=True):
        self.collectors = [
            GetDayTrendsCollector(),           # GetDayTrends - Twitter hashtags (PRIMARY)
            TwitterTrendsCollector(),          # Trends24 - Twitter trends (BACKUP)
            RedditTrendingCollector()          # Reddit - Trending keywords
        ]
        self.wikipedia_finder = WikipediaFinder()
        self.url_tracker = URLTracker()
        self.web_monitor = WebMonitor(self) if enable_web_monitor else None
        # Use Together AI by default, fallback to Ollama
        if use_together_ai:
            self.llm_analyzer = TogetherAIAnalyzer()
            logger.info("Using Together AI for analysis and tweet generation")
        else:
            self.llm_analyzer = OllamaAnalyzer(model_name=ollama_model)
            logger.info("Using Ollama for analysis")
        self.twitter_poster = TwitterPoster() if enable_twitter else None
        self.video_creator = VideoCreator() if enable_video else None
        self.stats = {
            'cycles_completed': 0,
            'articles_submitted': 0,
            'tweets_posted': 0,
            'videos_created': 0
        }
        
    async def collect_trends(self) -> List[str]:
        """Collect trends from all platforms and use LLM to prioritize by relevance"""
        logger.info("Starting trend collection from all platforms...")
        all_trends = set()
        
        for collector in self.collectors:
            try:
                trends = await collector.get_us_trends()
                all_trends.update(trends)
                logger.info(f"{collector.__class__.__name__}: Found {len(trends)} trends")
            except Exception as e:
                logger.error(f"Error collecting from {collector.__class__.__name__}: {e}")
        
        trends_list = list(all_trends)
        logger.info(f"Total unique trends collected: {len(trends_list)}")
        
        # Return all trends without filtering
        # Each trend will be processed: Wikipedia → Categorization → Submit
        return trends_list
    
    def create_wikipedia_url(self, trend: str) -> str:
        """
        Create Wikipedia URL directly from trend name
        Format: https://en.wikipedia.org/wiki/TREND_NAME
        """
        # Clean the trend name
        # Remove hashtags, numbers like "10K", "176K", etc.
        import re
        
        # Remove trailing numbers like "10K", "176K", etc.
        clean_trend = re.sub(r'\d+[KkMm]?\s*$', '', trend).strip()
        
        # Remove hashtags
        clean_trend = clean_trend.lstrip('#')
        
        # Replace spaces with underscores
        clean_trend = clean_trend.replace(' ', '_')
        
        # Create Wikipedia URL
        wikipedia_url = f"https://en.wikipedia.org/wiki/{clean_trend}"
        
        return wikipedia_url
    
    async def categorize_trend(self, trend: str, summary: str = "") -> str:
        """
        Determine the best category for a trend using Ollama LLM
        Falls back to keyword-based categorization if LLM is unavailable
        """
        # Try LLM categorization first
        is_available = await self.llm_analyzer.is_available()
        if is_available:
            try:
                # LLM categorizes based on trend name + Wikipedia summary
                category = await self.llm_analyzer.categorize_trend(trend, summary)
                return category
            except Exception as e:
                logger.warning(f"LLM categorization failed, using fallback: {e}")
        
        # Fallback: keyword-based categorization
        trend_lower = trend.lower()
        summary_lower = summary.lower() if summary else ""
        combined = trend_lower + " " + summary_lower
        
        # Category keywords mapping
        category_keywords = {
            "Politics": ["election", "president", "congress", "senate", "government", "politician", "vote", "policy"],
            "Sports": ["nfl", "nba", "mlb", "nhl", "soccer", "football", "basketball", "baseball", "championship", "team", "player"],
            "Entertainment": ["movie", "celebrity", "actor", "actress", "hollywood", "show", "series", "streaming"],
            "Music": ["singer", "album", "song", "concert", "band", "musician", "grammy"],
            "Technology": ["tech", "ai", "software", "apple", "google", "microsoft", "app", "smartphone", "computer"],
            "Business": ["company", "ceo", "stock", "market", "economy", "trade", "business", "corporation"],
            "Science": ["research", "study", "scientist", "space", "nasa", "discovery", "vaccine"],
            "Medicine": ["health", "doctor", "hospital", "disease", "medical", "treatment", "patient"],
            "Film": ["film", "director", "cinema", "oscar", "box office"],
            "Geography": ["country", "city", "island", "mountain", "river", "continent"],
            "History": ["war", "historical", "ancient", "century", "era"],
            "Food": ["restaurant", "chef", "recipe", "cooking", "cuisine"],
            "Fashion": ["fashion", "designer", "model", "clothing", "style"],
            "Environment": ["climate", "environment", "pollution", "nature", "wildlife"],
            "Arts": ["art", "artist", "painting", "sculpture", "gallery", "museum"],
            "Literature": ["author", "book", "novel", "writer", "poetry"],
            "Religion": ["church", "religious", "faith", "christian", "islam", "buddhist"],
            "Education": ["school", "university", "college", "education", "student", "teacher"],
            "Transportation": ["car", "automobile", "flight", "train", "transportation", "vehicle"]
        }
        
        # Score each category based on trend name + summary
        scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in combined)
            if score > 0:
                scores[category] = score
        
        # Return category with highest score, or default to Culture
        if scores:
            return max(scores, key=scores.get)
        return "Culture"
    
    async def submit_to_rollwiki(self, wikipedia_url: str, category: str) -> tuple[bool, Optional[int]]:
        """Submit a Wikipedia article to roll.wiki
        
        Returns:
            tuple: (success: bool, article_id: Optional[int])
        """
        params = {
            "url": wikipedia_url,
            "save": "true",
            "category": category,
            "secret": SECRET
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # Increased timeout to 120s for roll.wiki processing
                async with session.get(ROLL_WIKI_API, params=params, timeout=120) as response:
                    response_text = await response.text()
                    status = response.status
                    
                    if status == 200:
                        logger.info(f"✅ Successfully submitted: {wikipedia_url} (Category: {category})")
                        logger.info(f"   Response: {response_text[:100]}")
                        
                        # Extract article_id from response
                        try:
                            response_data = json.loads(response_text)
                            logger.info(f"   Parsed response data: {response_data}")
                            # Try different possible response formats
                            article_id = (
                                response_data.get('data', {}).get('article_id') or
                                response_data.get('article_id') or
                                response_data.get('id')
                            )
                            logger.info(f"   Extracted article_id: {article_id}")
                            return (True, article_id)
                        except Exception as e:
                            logger.warning(f"   Failed to parse article_id: {e}")
                            return (True, None)
                    elif status == 409:
                        # Article already exists in roll.wiki
                        logger.info(f"ℹ️  Article already exists in roll.wiki: {wikipedia_url}")
                        # Extract article_id from error message: "Article already exists in database with ID 1630"
                        try:
                            response_data = json.loads(response_text)
                            error_message = response_data.get('error', '')
                            
                            # Parse article_id from error message
                            import re
                            match = re.search(r'with ID (\d+)', error_message)
                            if match:
                                article_id = int(match.group(1))
                                logger.info(f"   Extracted article_id from error: {article_id}")
                                return (True, article_id)
                            else:
                                logger.warning(f"   Could not extract article_id from: {error_message}")
                                return (True, None)
                        except Exception as e:
                            logger.warning(f"   Failed to parse article_id: {e}")
                            return (True, None)
                    elif status == 404:
                        # Wikipedia article not found
                        logger.warning(f"⚠️  Wikipedia article not found: {wikipedia_url}")
                        logger.warning(f"   Response: {response_text[:200]}")
                        return (False, None)
                    else:
                        logger.warning(f"❌ Failed to submit {wikipedia_url}: Status {status}")
                        logger.warning(f"   Response: {response_text[:200]}")
                        return (False, None)
        except Exception as e:
            logger.error(f"Error submitting {wikipedia_url}: {e}")
            return (False, None)
    
    async def process_trend(self, trend: str) -> bool:
        """
        Process workflow:
        1. Trend → Wikipedia URL
        2. Wikipedia URL → Wikipedia API → Summary
        3. Summary → LLM → Category
        4. URL + Category → roll.wiki
        """
        logger.info(f"📌 Processing trend: {trend}")
        
        # Step 1: Trend → Wikipedia URL
        logger.info(f"  🔗 Step 1: Creating Wikipedia URL from trend...")
        wikipedia_url = self.create_wikipedia_url(trend)
        logger.info(f"  ✅ Wikipedia URL: {wikipedia_url}")
        
        # Check if already processed
        if self.url_tracker.is_processed(wikipedia_url):
            logger.info(f"  ⏭️  Already processed, skipping")
            return False
        
        # Step 2: Wikipedia URL → Extract title → Wikipedia API → Summary
        logger.info(f"  📖 Step 2: Fetching Wikipedia summary via API...")
        # Extract title from URL (e.g., "https://en.wikipedia.org/wiki/NBA" → "NBA")
        import re
        url_title = wikipedia_url.split('/wiki/')[-1]
        url_title = url_title.replace('_', ' ')  # Convert underscores to spaces
        
        summary = await self.wikipedia_finder.get_summary_by_title(url_title)
        
        if not summary:
            logger.warning(f"  ❌ No Wikipedia article found at: {wikipedia_url}")
            return False
        
        logger.info(f"  ✅ Summary fetched ({len(summary)} chars): {summary[:80]}...")
        
        # Check if this page should be skipped (no meaningful content)
        summary_lower = summary.lower()
        
        # 1. Disambiguation pages (anlam ayrımı)
        disambiguation_indicators = [
            "may refer to:",
            "may refer to",
            "may mean:",
            "may stand for:",
            "can refer to:",
            "most commonly refers to:",
            "commonly refers to:",
            "disambiguation",
            "is a disambiguation"
        ]
        
        if any(indicator in summary_lower for indicator in disambiguation_indicators):
            logger.warning(f"  ⚠️  Skipping disambiguation page (anlam ayrımı sayfası)")
            return False
        
        # 2. Surname/Name pages (soyadı/isim sayfaları)
        import re
        
        # Check if it's a surname/name page using regex patterns
        name_patterns = [
            r'\bis\s+(?:a|an)\s+(?:\w+\s+)*surname\b',  # "is a surname", "is an occupational surname"
            r'\bis\s+(?:a|an)\s+(?:\w+\s+)*(?:male|female|masculine|feminine|given|personal)?\s*name\b',  # "is a name", "is a male name", etc.
            r'\bsurname\s+originating\b',  # "surname originating"
            r'\bfamily\s+name\b',  # "family name"
            r'\bgiven\s+name\b',  # "given name"
        ]
        
        for pattern in name_patterns:
            if re.search(pattern, summary_lower):
                logger.warning(f"  ⚠️  Skipping name/surname page (isim/soyadı sayfası)")
                return False
        
        # 3. List pages (liste sayfaları)
        if summary_lower.startswith("this is a list of") or summary_lower.startswith("list of"):
            logger.warning(f"  ⚠️  Skipping list page (liste sayfası)")
            return False
        
        # 4. Very short content (çok kısa içerik)
        if len(summary) < 100:
            logger.warning(f"  ⚠️  Skipping page with insufficient content (yetersiz içerik: {len(summary)} chars)")
            return False
        
        # Step 3: Summary → LLM → Category
        logger.info(f"  🤖 Step 3: Categorizing with AI using Wikipedia summary...")
        category = await self.categorize_trend(trend, summary)
        logger.info(f"  ✅ Category determined: {category}")
        
        # Step 4: URL + Category → roll.wiki
        logger.info(f"  🚀 Step 4: Submitting to roll.wiki...")
        logger.info(f"     URL: {wikipedia_url}")
        logger.info(f"     Category: {category}")
        success, article_id = await self.submit_to_rollwiki(wikipedia_url, category)
        
        if success:
            self.url_tracker.mark_processed(wikipedia_url)
            logger.info(f"  ✅ Successfully submitted to roll.wiki!")
            
            # Post to Twitter if enabled
            if self.twitter_poster and self.twitter_poster.is_enabled():
                logger.info(f"  🐦 Step 5: Posting to Twitter...")
                
                # Generate tweet using Together AI if available
                tweet_text = None
                if isinstance(self.llm_analyzer, TogetherAIAnalyzer):
                    roll_wiki_url = f"https://roll.wiki/summary/{article_id}"
                    logger.info(f"  🤖 Generating optimized tweet with Together AI...")
                    tweet_text = await self.llm_analyzer.generate_tweet(trend, category, summary, roll_wiki_url)
                    if tweet_text:
                        logger.info(f"  ✨ AI-generated tweet: {tweet_text[:100]}...")
                
                tweet_success = await self.twitter_poster.post_tweet_async(trend, category, article_id, tweet_text)
                if tweet_success:
                    self.stats['tweets_posted'] += 1
                    logger.info(f"  ✅ Tweet posted successfully!")
                else:
                    logger.warning(f"  ⚠️ Failed to post tweet (article still submitted to roll.wiki)")
            
            # Create video if enabled
            if self.video_creator:
                logger.info(f"  🎬 Step 6: Creating video...")
                try:
                    # Create video with Wikipedia summary
                    video_filename = f"{trend.replace(' ', '_').replace('/', '_')}_shorts.mp4"
                    video_path = self.video_creator.create_video_from_pexels(
                        search_query=trend,
                        text=summary[:500],  # Limit text length
                        output_filename=video_filename,
                        narration_lang='en',  # Use 'tr' for Turkish
                        scroll_speed=80,
                        font_size=45,
                        orientation='portrait',
                        video_volume=0.1
                    )
                    
                    if video_path:
                        self.stats['videos_created'] += 1
                        logger.info(f"  ✅ Video created: {video_path}")
                    else:
                        logger.warning(f"  ⚠️ Failed to create video")
                except Exception as e:
                    logger.error(f"  ❌ Video creation error: {e}")
            
            return True
        else:
            logger.warning(f"  ❌ Failed to submit to roll.wiki")
        
        return False
    
    async def run_cycle(self):
        """Run one complete cycle of trend collection and submission"""
        logger.info("=" * 60)
        logger.info(f"🔄 Starting new cycle at {datetime.now()}")
        logger.info("=" * 60)
        
        # Collect trends
        logger.info("📊 Collecting trends from all sources...")
        trends = await self.collect_trends()
        
        if not trends:
            logger.warning("⚠️  No trends collected in this cycle")
            return
        
        logger.info(f"✅ Collected {len(trends)} unique trends")
        logger.info(f"🔄 Processing trends: Create Wikipedia URL → LLM Categorization → roll.wiki submission")
        logger.info("")
        
        # Process each trend with delay
        processed_count = 0
        for i, trend in enumerate(trends, 1):
            try:
                logger.info(f"[{i}/{len(trends)}] " + "="*50)
                success = await self.process_trend(trend)
                if success:
                    processed_count += 1
                    self.stats['articles_submitted'] += 1
                
                # Only wait if successful AND not the last trend
                if success and i < len(trends):
                    logger.info(f"⏳ Waiting {REQUEST_DELAY} seconds ({REQUEST_DELAY//60} minutes) before next trend...")
                    logger.info("")
                    await asyncio.sleep(REQUEST_DELAY)
                elif not success:
                    logger.info(f"⏭️  Skipping delay, moving to next trend immediately...")
                    logger.info("")
                    
            except Exception as e:
                logger.error(f"❌ Error processing trend '{trend}': {e}")
        
        # Update statistics
        self.stats['cycles_completed'] += 1
        if self.web_monitor:
            self.web_monitor.update_stats(
                cycles_completed=self.stats['cycles_completed'],
                articles_submitted=self.stats['articles_submitted'],
                last_cycle_time=datetime.now().isoformat(),
                last_trends_count=len(trends)
            )
        
        logger.info("")
        logger.info("=" * 60)
        logger.info(f"✅ Cycle completed!")
        logger.info(f"📊 Results: {processed_count} articles submitted out of {len(trends)} trends")
        logger.info(f"📈 Total articles submitted: {self.stats['articles_submitted']}")
        if self.twitter_poster and self.twitter_poster.is_enabled():
            logger.info(f"🐦 Total tweets posted: {self.stats['tweets_posted']}")
        logger.info("=" * 60)
    
    async def run(self):
        """Main run loop - execute cycles every 60 minutes"""
        logger.info("Trend Agent started!")
        logger.info(f"Configuration: {REQUEST_DELAY//60} minutes delay between requests, {CYCLE_INTERVAL//60} minutes between cycles")
        
        # Start web monitor
        if self.web_monitor:
            await self.web_monitor.start()
            logger.info("Web monitoring dashboard available at http://localhost:5001")
        
        while True:
            try:
                await self.run_cycle()
            except Exception as e:
                logger.error(f"Error in cycle: {e}")
            
            # Wait for next cycle
            logger.info(f"Waiting {CYCLE_INTERVAL} seconds until next cycle...")
            await asyncio.sleep(CYCLE_INTERVAL)


async def main():
    """Entry point"""
    # enable_video=True to create videos for each trend
    # Note: Requires Pexels API key in .env file
    agent = TrendAgent(enable_video=True)  # Set to True to enable video creation
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
