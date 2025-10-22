"""
Agentic Trend Collector Application
Collects US trends from multiple platforms and submits Wikipedia articles to roll.wiki
"""

import asyncio
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Set
import aiohttp
from real_trend_collectors import (
    TwitterTrendsCollector,
    RedditTrendingCollector,
    GetDayTrendsCollector
)
from wikipedia_finder import WikipediaFinder
from url_tracker import URLTracker
from web_monitor import WebMonitor
from ollama_analyzer import OllamaAnalyzer

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
REQUEST_DELAY = 30  # seconds between requests
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
    
    def __init__(self, enable_web_monitor=True, ollama_model=None):
        self.collectors = [
            GetDayTrendsCollector(),           # GetDayTrends - Twitter hashtags (PRIMARY)
            TwitterTrendsCollector(),          # Trends24 - Twitter trends (BACKUP)
            RedditTrendingCollector()          # Reddit - Trending keywords
        ]
        self.wikipedia_finder = WikipediaFinder()
        self.url_tracker = URLTracker()
        self.web_monitor = WebMonitor(self) if enable_web_monitor else None
        self.llm_analyzer = OllamaAnalyzer(model_name=ollama_model)
        self.stats = {
            'cycles_completed': 0,
            'articles_submitted': 0
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
    
    async def submit_to_rollwiki(self, wikipedia_url: str, category: str) -> bool:
        """Submit a Wikipedia article to roll.wiki"""
        params = {
            "url": wikipedia_url,
            "save": "true",
            "category": category,
            "secret": SECRET
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(ROLL_WIKI_API, params=params, timeout=30) as response:
                    response_text = await response.text()
                    status = response.status
                    
                    if status == 200:
                        logger.info(f"✅ Successfully submitted: {wikipedia_url} (Category: {category})")
                        logger.info(f"   Response: {response_text[:100]}")
                        return True
                    elif status == 409:
                        # Article already exists in roll.wiki
                        logger.info(f"ℹ️  Article already exists in roll.wiki: {wikipedia_url}")
                        return True  # Consider as success (already processed)
                    elif status == 404:
                        # Wikipedia article not found
                        logger.warning(f"⚠️  Wikipedia article not found: {wikipedia_url}")
                        logger.warning(f"   Response: {response_text[:200]}")
                        return False
                    else:
                        logger.warning(f"❌ Failed to submit {wikipedia_url}: Status {status}")
                        logger.warning(f"   Response: {response_text[:200]}")
                        return False
        except Exception as e:
            logger.error(f"Error submitting {wikipedia_url}: {e}")
            return False
    
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
        
        # Step 3: Summary → LLM → Category
        logger.info(f"  🤖 Step 3: Categorizing with Ollama using Wikipedia summary...")
        category = await self.categorize_trend(trend, summary)
        logger.info(f"  ✅ Category determined: {category}")
        
        # Step 4: URL + Category → roll.wiki
        logger.info(f"  🚀 Step 4: Submitting to roll.wiki...")
        logger.info(f"     URL: {wikipedia_url}")
        logger.info(f"     Category: {category}")
        success = await self.submit_to_rollwiki(wikipedia_url, category)
        
        if success:
            self.url_tracker.mark_processed(wikipedia_url)
            logger.info(f"  ✅ Successfully submitted to roll.wiki!")
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
                
                # Wait between requests (except for the last one)
                if i < len(trends):
                    logger.info(f"⏳ Waiting {REQUEST_DELAY} seconds before next trend...")
                    logger.info("")
                    await asyncio.sleep(REQUEST_DELAY)
                    
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
        logger.info("=" * 60)
    
    async def run(self):
        """Main run loop - execute cycles every 60 minutes"""
        logger.info("Trend Agent started!")
        logger.info(f"Configuration: {REQUEST_DELAY}s delay between requests, {CYCLE_INTERVAL}s between cycles")
        
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
    agent = TrendAgent()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
