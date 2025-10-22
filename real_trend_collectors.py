"""
REAL Trend Collectors - Gerçek trendleri toplayan collectors
Haber başlıkları DEĞİL, gerçek trend keyword'leri alır
"""

import asyncio
import logging
from typing import List
import aiohttp
from bs4 import BeautifulSoup
from pytrends.request import TrendReq
import pandas as pd

logger = logging.getLogger(__name__)


class BaseTrendCollector:
    """Base class for trend collectors"""
    
    async def get_us_trends(self) -> List[str]:
        """Get trending topics in the US. Must be implemented by subclasses."""
        raise NotImplementedError


class GoogleTrendsCollector(BaseTrendCollector):
    """Collect REAL trends from Google Trends using PyTrends"""
    
    def __init__(self):
        """Initialize PyTrends"""
        self.pytrends = None
        self._initialize()
    
    def _initialize(self):
        """Initialize pytrends connection"""
        try:
            self.pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))
            logger.info("Google Trends (PyTrends) initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PyTrends: {e}")
    
    async def get_us_trends(self) -> List[str]:
        """Get real trending searches from Google Trends"""
        # Try RSS feed first (more reliable)
        try:
            trends = await self._get_trends_from_rss()
            if trends:
                return trends
        except Exception as e:
            logger.warning(f"RSS feed failed: {e}")
        
        # Fallback to PyTrends API
        if not self.pytrends:
            self._initialize()
            if not self.pytrends:
                return []
        
        try:
            # Run in executor since pytrends is synchronous
            loop = asyncio.get_event_loop()
            df = await loop.run_in_executor(
                None,
                self.pytrends.trending_searches,
                'united_states'
            )
            
            if df is not None and len(df) > 0:
                # DataFrame'in ilk sütunu trend keyword'lerini içerir
                trends = df[0].tolist()
                logger.info(f"Google Trends: Found {len(trends)} real trends")
                return trends[:20]  # Top 20
                
        except Exception as e:
            logger.error(f"GoogleTrendsCollector error: {e}")
        
        return []
    
    async def _get_trends_from_rss(self) -> List[str]:
        """Fallback: Get trends from Google Trends RSS"""
        url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=15) as response:
                if response.status == 200:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'xml')
                    
                    trends = []
                    for item in soup.find_all('title'):
                        title = item.text.strip()
                        # Skip the feed title
                        if title and title != "Daily Search Trends":
                            trends.append(title)
                    
                    return trends[:20]
        return []


class TwitterTrendsCollector(BaseTrendCollector):
    """Collect REAL trends from Twitter using trends24.in"""
    
    async def get_us_trends(self) -> List[str]:
        """Get real Twitter/X trends"""
        try:
            # Try trends24.in first
            trends = await self._get_from_trends24()
            if trends:
                return trends
            
            # Fallback: getdaytrends
            trends = await self._get_from_getdaytrends()
            if trends:
                return trends
                
        except Exception as e:
            logger.error(f"TwitterTrendsCollector error: {e}")
        
        return []
    
    async def _get_from_trends24(self) -> List[str]:
        """Get trends from trends24.in"""
        url = "https://trends24.in/united-states/"
        
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            async with session.get(url, headers=headers, timeout=15) as response:
                if response.status == 200:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    
                    trends = []
                    
                    # Method 1: Look for trend cards
                    for trend_card in soup.find_all('ol', class_='trend-card__list'):
                        for li in trend_card.find_all('li'):
                            trend = li.get_text(strip=True)
                            if trend and not trend.startswith('http'):
                                # Clean hashtag
                                if trend.startswith('#'):
                                    trend = trend[1:]
                                trends.append(trend)
                    
                    # Method 2: Look for any anchor with trend class
                    if not trends:
                        for a in soup.find_all('a', href=True):
                            if 'trend' in a.get('href', ''):
                                trend = a.get_text(strip=True)
                                if trend and len(trend) > 2:
                                    if trend.startswith('#'):
                                        trend = trend[1:]
                                    trends.append(trend)
                    
                    if trends:
                        logger.info(f"Trends24: Found {len(trends)} Twitter trends")
                        return list(set(trends))[:15]  # Deduplicate and limit
        return []
    
    async def _get_from_getdaytrends(self) -> List[str]:
        """Get trends from getdaytrends.com"""
        url = "https://getdaytrends.com/united-states/"
        
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            async with session.get(url, headers=headers, timeout=15) as response:
                if response.status == 200:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    
                    trends = []
                    # Look for trending topics with various selectors
                    for element in soup.select('a.topic, .trend-link, .trend-item'):
                        trend_text = element.get_text(strip=True)
                        if trend_text and not trend_text.startswith('#'):
                            trends.append(trend_text)
                    
                    if trends:
                        logger.info(f"GetDayTrends: Found {len(trends)} Twitter trends")
                        return trends[:15]
        return []


class TikTokTrendsCollector(BaseTrendCollector):
    """Collect trends from TikTok Discover page"""
    
    async def get_us_trends(self) -> List[str]:
        """Get TikTok trending hashtags and sounds"""
        try:
            url = "https://www.tiktok.com/discover"
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
                async with session.get(url, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        text = await response.text()
                        soup = BeautifulSoup(text, 'html.parser')
                        
                        trends = []
                        
                        # Look for hashtags in the page
                        for a in soup.find_all('a', href=True):
                            href = a.get('href', '')
                            if '/tag/' in href:
                                # Extract hashtag from URL
                                tag = href.split('/tag/')[-1].split('?')[0]
                                if tag and tag not in trends:
                                    trends.append(tag)
                        
                        if trends:
                            logger.info(f"TikTok: Found {len(trends)} trending tags")
                            return trends[:15]
                            
        except Exception as e:
            logger.error(f"TikTokTrendsCollector error: {e}")
        
        return []


class RedditTrendingCollector(BaseTrendCollector):
    """Extract trending KEYWORDS from Reddit hot posts"""
    
    async def get_us_trends(self) -> List[str]:
        """Extract trending keywords from Reddit"""
        try:
            url = "https://www.reddit.com/r/all/hot/.json?limit=50"
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'TrendCollector/2.0'
                }
                async with session.get(url, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Collect all post titles
                        titles = []
                        for post in data.get('data', {}).get('children', []):
                            post_data = post.get('data', {})
                            title = post_data.get('title', '').strip()
                            if title:
                                titles.append(title)
                        
                        # Extract keywords (simple approach)
                        trends = self._extract_keywords(titles)
                        
                        if trends:
                            logger.info(f"Reddit: Extracted {len(trends)} trending keywords")
                            return trends[:20]
                            
        except Exception as e:
            logger.error(f"RedditTrendingCollector error: {e}")
        
        return []
    
    def _extract_keywords(self, titles: List[str]) -> List[str]:
        """Extract potential trending keywords from titles"""
        import re
        from collections import Counter
        
        # Common words to ignore
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'be', 'been',
            'has', 'have', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'my', 'your', 'his', 'her', 'its', 'our', 'their', 'what', 'which',
            'who', 'when', 'where', 'why', 'how', 'just', 'so', 'than', 'more',
            'about', 'after', 'all', 'also', 'into', 'out', 'up', 'down'
        }
        
        # Extract capitalized words and phrases (likely proper nouns/names)
        keywords = []
        for title in titles:
            # Find capitalized words (potential names/brands)
            words = re.findall(r'\b[A-Z][a-zA-Z]+\b', title)
            for word in words:
                if word.lower() not in stopwords and len(word) > 3:
                    keywords.append(word)
            
            # Find quoted phrases
            quoted = re.findall(r'"([^"]+)"', title)
            keywords.extend(quoted)
            
            # Find words in ALL CAPS (often important)
            caps = re.findall(r'\b[A-Z]{2,}\b', title)
            keywords.extend([w for w in caps if len(w) > 2])
        
        # Count frequencies
        counter = Counter(keywords)
        
        # Return most common keywords
        return [keyword for keyword, count in counter.most_common(30)]


class BingTrendsCollector(BaseTrendCollector):
    """Collect trends from Bing by searching 'trending now'"""
    
    async def get_us_trends(self) -> List[str]:
        """Get trending topics from Bing search results"""
        try:
            # Search for "trending now" on Bing and extract keywords
            url = "https://www.bing.com/search?q=trending+now+2024"
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                async with session.get(url, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        text = await response.text()
                        soup = BeautifulSoup(text, 'html.parser')
                        
                        trends = []
                        # Extract from search result titles
                        for heading in soup.find_all(['h2', 'h3'], limit=30):
                            text_content = heading.get_text(strip=True)
                            # Extract capitalized words (likely proper nouns/trends)
                            import re
                            words = re.findall(r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\b', text_content)
                            for word in words:
                                if len(word) > 3 and len(word) < 40 and word not in trends:
                                    trends.append(word)
                        
                        if trends:
                            logger.info(f"Bing: Found {len(trends)} potential trends")
                            return trends[:15]
                            
        except Exception as e:
            logger.error(f"BingTrendsCollector error: {e}")
        
        return []


class YandexTrendsCollector(BaseTrendCollector):
    """Collect trends from Yandex by searching trending topics"""
    
    async def get_us_trends(self) -> List[str]:
        """Get trending topics from Yandex search"""
        try:
            # Search for trending topics on Yandex
            url = "https://yandex.com/search/?text=trending+now+2024"
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                async with session.get(url, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        text = await response.text()
                        soup = BeautifulSoup(text, 'html.parser')
                        
                        trends = []
                        # Extract keywords from search results
                        import re
                        for heading in soup.find_all(['h2', 'h3', 'a'], limit=30):
                            text_content = heading.get_text(strip=True)
                            # Extract capitalized words
                            words = re.findall(r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\b', text_content)
                            for word in words:
                                if len(word) > 3 and len(word) < 40 and word not in trends:
                                    trends.append(word)
                        
                        if trends:
                            logger.info(f"Yandex: Found {len(trends)} potential trends")
                            return trends[:15]
                            
        except Exception as e:
            logger.error(f"YandexTrendsCollector error: {e}")
        
        return []


class BraveSearchTrendsCollector(BaseTrendCollector):
    """Collect trends from Brave Search"""
    
    async def get_us_trends(self) -> List[str]:
        """Get trending topics from Brave Search"""
        try:
            # Search for trending topics on Brave
            url = "https://search.brave.com/search?q=trending+now+2024"
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                async with session.get(url, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        text = await response.text()
                        soup = BeautifulSoup(text, 'html.parser')
                        
                        trends = []
                        # Extract keywords from search results
                        import re
                        for div in soup.find_all(['div', 'h2', 'h3', 'a'], limit=30):
                            text_content = div.get_text(strip=True)
                            # Extract capitalized words
                            words = re.findall(r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\b', text_content)
                            for word in words:
                                if len(word) > 3 and len(word) < 40 and word not in trends:
                                    trends.append(word)
                        
                        if trends:
                            logger.info(f"Brave: Found {len(trends)} potential trends")
                            return trends[:15]
                            
        except Exception as e:
            logger.error(f"BraveSearchTrendsCollector error: {e}")
        
        return []


class GetDayTrendsCollector(BaseTrendCollector):
    """Collect trending hashtags from GetDayTrends.com"""
    
    async def get_us_trends(self) -> List[str]:
        """Get trending Twitter hashtags from GetDayTrends"""
        try:
            url = "https://getdaytrends.com/united-states/"
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                async with session.get(url, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        text = await response.text()
                        soup = BeautifulSoup(text, 'html.parser')
                        
                        trends = []
                        
                        # Find all links that contain trend hashtags
                        for link in soup.find_all('a', href=True):
                            href = link.get('href', '')
                            if '/trend/' in href:
                                # Extract trend name from link text
                                trend_text = link.get_text(strip=True)
                                if trend_text and trend_text not in trends:
                                    # Remove # if present
                                    trend_clean = trend_text.lstrip('#')
                                    if len(trend_clean) > 2 and len(trend_clean) < 50:
                                        trends.append(trend_clean)
                        
                        if trends:
                            logger.info(f"GetDayTrends: Found {len(trends)} Twitter trends")
                            return trends[:30]  # Top 30 trends
                            
        except Exception as e:
            logger.error(f"GetDayTrendsCollector error: {e}")
        
        return []
