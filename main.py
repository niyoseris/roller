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
from youtube_uploader import YouTubeUploader
from session_manager import SessionManager
import config
import dashboard  # Import dashboard at module level to register routes

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
    
    def __init__(self, enable_web_monitor=True, ollama_model=None, enable_twitter=True, enable_video=False, enable_youtube=False, use_together_ai=True):
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
        # Add Gemini Analyzer for Wikipedia URL + Category + Video Keywords
        from gemini_analyzer import GeminiAnalyzer
        self.gemini_analyzer = GeminiAnalyzer()
        logger.info("Gemini Analyzer initialized for complete trend analysis")
        self.twitter_poster = TwitterPoster() if enable_twitter else None
        self.video_creator = VideoCreator(
            use_edge_tts=True,       # Edge TTS (secondary, after Gemini)
            use_gemini_tts=True,     # Gemini Flash TTS (primary)
            use_bark_tts=True,       # Bark TTS (tertiary, Suno AI local fallback)
            use_piper_tts=False,     # Piper TTS disabled (lower quality)
            config={'video_settings': config.VIDEO_SETTINGS}
        ) if enable_video else None
        
        # YouTube uploader
        self.youtube_uploader = None
        if enable_youtube:
            self.youtube_uploader = YouTubeUploader()
            if self.youtube_uploader.authenticate():
                logger.info("✅ YouTube upload enabled and authenticated")
            else:
                logger.warning("⚠️ YouTube upload enabled but authentication failed")
                self.youtube_uploader = None
        
        self.session_manager = SessionManager()
        self.stats = {
            'cycles_completed': 0,
            'articles_submitted': 0,
            'tweets_posted': 0,
            'videos_created': 0,
            'youtube_uploads': 0
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
    
    async def submit_to_rollwiki(self, wikipedia_url: str, category: str) -> tuple[bool, Optional[int], Optional[str]]:
        """Submit a Wikipedia article to roll.wiki
        
        Returns:
            tuple: (success: bool, article_id: Optional[int], summary: Optional[str])
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
                        logger.info(f"   Full Response: {response_text}")
                        
                        # Extract article_id and summary from response
                        try:
                            response_data = json.loads(response_text)
                            logger.info(f"   Parsed response data keys: {response_data.keys()}")
                            logger.info(f"   Parsed response data: {response_data}")
                            
                            # Try different possible response formats
                            article_id = (
                                response_data.get('data', {}).get('article_id') or
                                response_data.get('article_id') or
                                response_data.get('id')
                            )
                            logger.info(f"   Extracted article_id: {article_id}")
                            
                            # Extract summary from response
                            summary = response_data.get('data', {}).get('summary', '')
                            if summary:
                                logger.info(f"   ✅ Extracted summary from roll.wiki ({len(summary)} chars):")
                                logger.info(f"   Summary preview: {summary[:200]}...")
                            else:
                                logger.warning(f"   ⚠️ No summary in roll.wiki response!")
                                logger.warning(f"   Response data structure: {response_data}")
                            return (True, article_id, summary)
                        except Exception as e:
                            logger.warning(f"   Failed to parse article_id: {e}")
                            return (True, None, None)
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
                                return (True, article_id, None)
                            else:
                                logger.warning(f"   Could not extract article_id from: {error_message}")
                                return (True, None, None)
                        except Exception as e:
                            logger.warning(f"   Failed to parse article_id: {e}")
                            return (True, None, None)
                    elif status == 404:
                        # Wikipedia article not found
                        logger.warning(f"⚠️  Wikipedia article not found: {wikipedia_url}")
                        logger.warning(f"   Response: {response_text[:200]}")
                        return (False, None, None)
                    else:
                        logger.warning(f"❌ Failed to submit {wikipedia_url}: Status {status}")
                        logger.warning(f"   Response: {response_text[:200]}")
                        return (False, None, None)
        except Exception as e:
            logger.error(f"Error submitting {wikipedia_url}: {e}")
            return (False, None, None)
    
    async def process_trend(self, trend: str, save_report: bool = False, use_gemini_url: bool = False) -> bool:
        """
        Process workflow:
        1. Trend → Gemini → Wikipedia URL + Category + Video Keywords
        2. Wikipedia URL → Wikipedia API → Summary
        3. URL + Category → roll.wiki
        4. Create video using keywords
        
        Args:
            trend: The trend to process
            save_report: If True, save report to session manager
            use_gemini_url: Not used anymore (kept for compatibility)
        """
        logger.info(f"📌 Processing trend: {trend}")
        
        # Step 1: Trend → Gemini → Get Wikipedia URL + Category + Video Keywords
        logger.info(f"  🤖 Step 1: Analyzing trend with Gemini AI...")
        gemini_data = await self.gemini_analyzer.analyze_trend_complete(trend)
        
        if not gemini_data:
            logger.warning(f"  ⚠️  Gemini analysis failed, creating manual URL...")
            wikipedia_url = self.create_wikipedia_url(trend)
            category = None
            video_keywords = [trend]
        else:
            wikipedia_url = gemini_data.get('wikipedia_url')
            category = gemini_data.get('category')
            video_keywords = gemini_data.get('video_keywords', [trend])
            
            if not wikipedia_url:
                logger.warning(f"  ⚠️  No Wikipedia URL from Gemini, creating manual URL...")
                wikipedia_url = self.create_wikipedia_url(trend)
        
        logger.info(f"  ✅ Wikipedia URL: {wikipedia_url}")
        logger.info(f"  ✅ Category: {category or 'Will be determined later'}")
        logger.info(f"  ✅ Video keywords: {video_keywords}")
        
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
        
        # Step 3: Determine category if not provided by Gemini
        if not category:
            logger.info(f"  🤖 Step 3: Categorizing with AI using Wikipedia summary...")
            category = await self.categorize_trend(trend, summary)
            logger.info(f"  ✅ Category determined: {category}")
        else:
            logger.info(f"  ✅ Step 3: Using Gemini-provided category: {category}")
        
        # Step 4: URL + Category → roll.wiki (get summary from roll.wiki)
        logger.info(f"  🚀 Step 4: Submitting to roll.wiki...")
        logger.info(f"     URL: {wikipedia_url}")
        logger.info(f"     Category: {category}")
        success, article_id, roll_wiki_summary = await self.submit_to_rollwiki(wikipedia_url, category)
        
        if success:
            self.url_tracker.mark_processed(wikipedia_url)
            logger.info(f"  ✅ Successfully submitted to roll.wiki!")
            
            # Use roll.wiki summary if available, otherwise use Wikipedia API summary
            if roll_wiki_summary:
                logger.info(f"  📝 Using roll.wiki summary ({len(roll_wiki_summary)} chars)")
                summary = roll_wiki_summary
            else:
                logger.info(f"  📝 Using Wikipedia API summary ({len(summary)} chars)")
            
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
                    # Use first video keyword from Gemini, fallback to trend name
                    search_keyword = video_keywords[0] if video_keywords else trend
                    logger.info(f"     Using video keyword: {search_keyword}")
                    
                    # Create video with roll.wiki summary (full length)
                    video_filename = f"{trend.replace(' ', '_').replace('/', '_')}_shorts.mp4"
                    video_path = self.video_creator.create_video_from_pexels(
                        search_query=search_keyword,  # Use Gemini-provided keyword
                        text=summary,  # Use full summary from roll.wiki
                        output_filename=video_filename,
                        narration_lang='en',  # Use 'tr' for Turkish
                        scroll_speed=50,  # Slower initial speed, will auto-adjust to narration
                        font_size=config.VIDEO_SETTINGS.get('font_size', 24),
                        orientation='portrait',
                        video_volume=config.VIDEO_SETTINGS.get('video_volume', 0.0),
                        category=category  # Save to category folder
                    )
                    
                    if video_path:
                        self.stats['videos_created'] += 1
                        logger.info(f"  ✅ Video created: {video_path}")
                        
                        # Upload to YouTube Shorts if enabled
                        if self.youtube_uploader:
                            try:
                                import os
                                logger.info(f"  📺 Uploading to YouTube Shorts...")
                                
                                # Prepare metadata for Shorts
                                video_title = f"{trend} - Quick Explainer"
                                video_description = f"{summary[:200]}...\n\nStay informed with the latest trends!"
                                video_tags = [trend, "trending", "shorts", category.lower(), "news"]
                                category_id = config.VIDEO_SETTINGS.get('youtube_category', '22')
                                
                                video_id = self.youtube_uploader.upload_video(
                                    video_path=str(video_path),
                                    title=video_title,
                                    description=video_description,
                                    tags=video_tags,
                                    category_id=category_id,
                                    privacy_status="public",
                                    is_shorts=True  # Upload as YouTube Shorts
                                )
                                
                                if video_id:
                                    self.stats['youtube_uploads'] += 1
                                    logger.info(f"  ✅ YouTube Shorts uploaded: https://youtube.com/shorts/{video_id}")
                                else:
                                    logger.warning(f"  ⚠️ YouTube upload failed")
                            except Exception as e:
                                logger.error(f"  ❌ YouTube upload error: {e}")
                    else:
                        logger.warning(f"  ⚠️ Failed to create video")
                except Exception as e:
                    logger.error(f"  ❌ Video creation error: {e}")
            
            # Save report if requested
            if save_report and self.session_manager:
                report = {
                    "trend": trend,
                    "wikipedia_url": wikipedia_url,
                    "category": category,
                    "article_id": article_id,
                    "video_keywords": video_keywords,
                    "success": True,
                    "processed_at": datetime.now().isoformat()
                }
                self.session_manager.mark_trend_processed(trend, True, report)
            
            return True
        else:
            logger.warning(f"  ❌ Failed to submit to roll.wiki")
            
            # Save failed report if requested
            if save_report and self.session_manager:
                report = {
                    "trend": trend,
                    "wikipedia_url": wikipedia_url,
                    "error": "Failed to submit to roll.wiki",
                    "success": False,
                    "processed_at": datetime.now().isoformat()
                }
                self.session_manager.mark_trend_processed(trend, False, report)
        
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
    
    async def recreate_video_for_trend(self, trend: str, summary: str, video_keywords: List[str] = None, category: str = None) -> Optional[str]:
        """
        Recreate video for a specific trend using existing summary
        
        Args:
            trend: Trend name
            summary: Article summary
            video_keywords: Optional list of video keywords from Gemini
            category: Category for organizing videos into folders
            
        Returns:
            Path to created video or None if failed
        """
        if not self.video_creator:
            logger.error("Video creator not enabled!")
            return None
        
        try:
            logger.info(f"🎬 Recreating video for trend: {trend}")
            
            # Use first video keyword from Gemini, fallback to trend name
            search_keyword = video_keywords[0] if video_keywords else trend
            logger.info(f"   Using video keyword: {search_keyword}")
            
            # Create video with roll.wiki summary
            video_filename = f"{trend.replace(' ', '_').replace('/', '_')}_shorts.mp4"
            video_path = self.video_creator.create_video_from_pexels(
                search_query=search_keyword,
                text=summary,
                output_filename=video_filename,
                narration_lang='en',
                scroll_speed=50,
                font_size=config.VIDEO_SETTINGS.get('font_size', 24),
                orientation='portrait',
                video_volume=config.VIDEO_SETTINGS.get('video_volume', 0.0),
                category=category  # Save to category folder
            )
            
            if video_path:
                logger.info(f"✅ Video recreated: {video_path}")
                return str(video_path)
            else:
                logger.warning(f"⚠️ Failed to recreate video")
                return None
                
        except Exception as e:
            logger.error(f"❌ Video recreation error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def process_manual_trends(self) -> bool:
        """Process manual trends from session manager"""
        # Reload session from file to get latest changes from dashboard
        self.session_manager.session = self.session_manager.load_session()
        
        current_status = self.session_manager.session.get('status', 'idle')
        if current_status != 'running':
            return False
        
        next_trend = self.session_manager.get_next_trend()
        if not next_trend:
            return False
        
        try:
            logger.info(f"📌 Processing manual trend: {next_trend}")
            success = await self.process_trend(next_trend, save_report=True, use_gemini_url=True)
            
            if success:
                self.stats['articles_submitted'] += 1
                logger.info(f"✅ Manual trend processed successfully: {next_trend}")
            else:
                logger.info(f"⏭️  Manual trend skipped: {next_trend}")
                # IMPORTANT: Mark failed trend as processed to avoid infinite loop
                # This will increment current_index and move to next trend
                report = {
                    "trend": next_trend,
                    "error": "Wikipedia article not found or processing failed",
                    "success": False,
                    "processed_at": datetime.now().isoformat()
                }
                self.session_manager.mark_trend_processed(next_trend, False, report)
            
            # Only wait if successful and more trends exist
            if success and self.session_manager.session['current_index'] < self.session_manager.session['total_trends']:
                logger.info(f"⏳ Waiting {REQUEST_DELAY} seconds before next trend...")
                await asyncio.sleep(REQUEST_DELAY)
            elif not success:
                logger.info(f"⏭️  Skipping delay, moving to next trend immediately...")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing manual trend '{next_trend}': {e}")
            report = {
                "trend": next_trend,
                "error": str(e),
                "success": False,
                "processed_at": datetime.now().isoformat()
            }
            self.session_manager.mark_trend_processed(next_trend, False, report)
            return True
    
    async def run(self):
        """Main run loop - MANUAL TRENDS ONLY MODE"""
        logger.info("Trend Agent started!")
        logger.info("⚙️  MODE: Manual trends only (automatic collection disabled)")
        logger.info(f"Configuration: {REQUEST_DELAY//60} minutes delay between requests")
        
        # Start web monitor
        if self.web_monitor:
            await self.web_monitor.start()
            logger.info("Web monitoring dashboard available at http://localhost:5001")
        
        while True:
            try:
                # ONLY process manual trends - no automatic collection
                if await self.process_manual_trends():
                    # Manual trend processed, continue loop
                    await asyncio.sleep(1)  # Small delay before checking again
                    continue
                
                # No manual trends, just wait
                logger.info("⏸️  No manual trends to process. Waiting for manual input...")
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in processing: {e}")
                await asyncio.sleep(5)


async def main():
    """Entry point - All modules managed from here"""
    # enable_video from config - can be disabled for faster processing/testing
    # Note: Requires Pexels API key in .env file
    from config import VIDEO_ENABLED, YOUTUBE_ENABLED
    agent = TrendAgent(enable_video=VIDEO_ENABLED, enable_youtube=YOUTUBE_ENABLED, enable_web_monitor=False)
    
    # Make agent globally accessible for dashboard
    dashboard.trend_agent = agent
    
    await agent.run()


def recreate_video():
    """Recreate only the video for a specific trend (uses existing summary)"""
    from flask import request, jsonify
    import os
    
    try:
        data = request.get_json()
        trend = data.get('trend')
        
        if not trend:
            return jsonify({
                "success": False,
                "message": "Trend adı gerekli"
            }), 400
        
        logger.info("=" * 60)
        logger.info(f"🎬 Recreating video for trend: {trend}")
        
        # Get trend report from session manager
        report = dashboard.session_manager.get_report(trend)
        if not report:
            return jsonify({
                "success": False,
                "message": "Trend raporu bulunamadı"
            }), 404
        
        # Extract summary from report or fetch from Roll.wiki
        summary = report.get('summary', '')
        
        # If no summary in report, try to fetch from Roll.wiki using article_id
        if not summary:
            article_id = report.get('article_id')
            
            if not article_id:
                return jsonify({
                    "success": False,
                    "message": "Roll.wiki article ID bulunamadı",
                    "need_article_id": True,
                    "trend": trend
                }), 400
            
            logger.info(f"  📥 Fetching summary from Roll.wiki (article_id: {article_id})")
            import requests
            try:
                roll_api_url = f"https://roll.wiki/api/v1/articles/{article_id}"
                logger.info(f"  🌐 Roll.wiki API URL: {roll_api_url}")
                
                response = requests.get(roll_api_url, timeout=10)
                logger.info(f"  📡 Response status: {response.status_code}")
                
                if response.status_code == 200:
                    roll_data = response.json()
                    
                    if roll_data.get('success') and roll_data.get('data'):
                        article = roll_data['data']
                        summary = article.get('summary', '')
                        logger.info(f"  ✅ Fetched summary from Roll.wiki ({len(summary)} chars)")
                    else:
                        logger.info(f"  ⚠️  Roll.wiki response format unexpected")
                else:
                    logger.info(f"  ⚠️  Roll.wiki API returned status {response.status_code}")
            except Exception as e:
                logger.error(f"  ⚠️  Failed to fetch from Roll.wiki: {e}")
        
        if not summary:
            return jsonify({
                "success": False,
                "message": "Trend için özet bulunamadı"
            }), 404
        
        logger.info(f"  📝 Using summary: {len(summary)} characters")
        
        # Get video keywords and category from report if available
        video_keywords = report.get('video_keywords', [])
        category = report.get('category', None)
        
        # Use TrendAgent if available
        if dashboard.trend_agent and hasattr(dashboard.trend_agent, 'recreate_video_for_trend'):
            logger.info(f"  🤖 Using TrendAgent for video recreation")
            
            # Run async function
            def run_async_recreate():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(
                        dashboard.trend_agent.recreate_video_for_trend(trend, summary, video_keywords, category)
                    )
                finally:
                    loop.close()
            
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor() as executor:
                video_path = executor.submit(run_async_recreate).result()
            
            if video_path:
                logger.info(f"  ✅ Video recreated: {video_path}")
                logger.info("=" * 60)
                video_filename = os.path.basename(video_path)
                return jsonify({
                    "success": True,
                    "message": "Video başarıyla yeniden oluşturuldu",
                    "video_path": str(video_path),
                    "filename": video_filename
                })
            else:
                logger.error("  ❌ Video recreation failed")
                logger.info("=" * 60)
                return jsonify({
                    "success": False,
                    "message": "Video oluşturma başarısız"
                }), 500
        else:
            logger.error("  ❌ TrendAgent not available")
            return jsonify({
                "success": False,
                "message": "TrendAgent not initialized"
            }), 500
            
    except Exception as e:
        logger.error(f"🔥 ERROR recreating video: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


def start_dashboard():
    """Start Flask dashboard in separate thread (managed from main.py)"""
    # Register recreation route manually
    dashboard.app.add_url_rule('/api/video/recreate', 'recreate_video', recreate_video, methods=['POST'])
    dashboard.app.add_url_rule('/api/video-recreate', 'recreate_video_alt', recreate_video, methods=['POST'])
    logger.info("✅ Recreation routes registered in main.py")
    
    # Print all registered routes for debugging
    logger.info("=" * 60)
    logger.info("📋 Flask Dashboard Routes:")
    logger.info("=" * 60)
    for rule in dashboard.app.url_map.iter_rules():
        logger.info(f"  {list(rule.methods)} {rule.rule}")
    logger.info("=" * 60)
    
    # Start Flask app (non-debug mode to avoid reloader conflicts)
    logger.info("🚀 Dashboard running on http://localhost:5001")
    dashboard.app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)


if __name__ == "__main__":
    import threading
    
    logger.info("=" * 60)
    logger.info("🚀 Starting Complete System from main.py")
    logger.info("📊 Dashboard: http://localhost:5001")
    logger.info("🤖 Trend Agent: Initializing...")
    logger.info("📹 Video Creator: Enabled (if configured)")
    logger.info("=" * 60)
    
    # Start dashboard in daemon thread (managed by main.py)
    dashboard_thread = threading.Thread(target=start_dashboard, daemon=True)
    dashboard_thread.start()
    
    # Start trend agent in main thread (primary control)
    asyncio.run(main())
