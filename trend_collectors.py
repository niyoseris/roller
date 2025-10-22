"""
Trend collectors for various platforms
Each collector implements get_us_trends() method to fetch trending topics in the US
"""

import asyncio
import logging
from typing import List
import aiohttp
from bs4 import BeautifulSoup
import json

logger = logging.getLogger(__name__)


class BaseTrendCollector:
    """Base class for trend collectors"""
    
    async def get_us_trends(self) -> List[str]:
        """Get trending topics in the US. Must be implemented by subclasses."""
        raise NotImplementedError


class GoogleTrendsCollector(BaseTrendCollector):
    """Collect trends from Google Trends"""
    
    async def get_us_trends(self) -> List[str]:
        """Get US trends from Google Trends"""
        try:
            url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=15) as response:
                    if response.status == 200:
                        text = await response.text()
                        soup = BeautifulSoup(text, 'xml')
                        
                        trends = []
                        for item in soup.find_all('item'):
                            title = item.find('title')
                            if title:
                                trends.append(title.text.strip())
                        
                        return trends[:20]  # Limit to top 20
        except Exception as e:
            logger.error(f"GoogleTrendsCollector error: {e}")
        
        return []


class TwitterTrendsCollector(BaseTrendCollector):
    """Collect trends from Twitter/X"""
    
    async def get_us_trends(self) -> List[str]:
        """Get US trends from Twitter - using getdaytrends.com as alternative"""
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
                        # Look for trending topics
                        for element in soup.find_all('a', class_='topic'):
                            trend_text = element.text.strip()
                            if trend_text and not trend_text.startswith('#'):
                                trends.append(trend_text)
                        
                        return trends[:15]  # Limit to top 15
        except Exception as e:
            logger.error(f"TwitterTrendsCollector error: {e}")
        
        return []


class RedditTrendsCollector(BaseTrendCollector):
    """Collect trends from Reddit"""
    
    async def get_us_trends(self) -> List[str]:
        """Get trending topics from Reddit"""
        try:
            url = "https://www.reddit.com/r/all/hot/.json?limit=25"
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'TrendCollector/1.0'
                }
                async with session.get(url, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        trends = []
                        for post in data.get('data', {}).get('children', []):
                            post_data = post.get('data', {})
                            title = post_data.get('title', '').strip()
                            if title:
                                trends.append(title)
                        
                        return trends[:20]  # Limit to top 20
        except Exception as e:
            logger.error(f"RedditTrendsCollector error: {e}")
        
        return []


class YahooNewsCollector(BaseTrendCollector):
    """Collect trending news from Yahoo News"""
    
    async def get_us_trends(self) -> List[str]:
        """Get trending news from Yahoo News"""
        try:
            url = "https://news.yahoo.com/"
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                async with session.get(url, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        text = await response.text()
                        soup = BeautifulSoup(text, 'html.parser')
                        
                        trends = []
                        # Look for article headlines
                        for element in soup.find_all('h3'):
                            headline = element.text.strip()
                            if headline and len(headline) > 10:
                                trends.append(headline)
                        
                        return trends[:15]  # Limit to top 15
        except Exception as e:
            logger.error(f"YahooNewsCollector error: {e}")
        
        return []


class YahooTrendsCollector(BaseTrendCollector):
    """Collect trends from Yahoo Trends"""
    
    async def get_us_trends(self) -> List[str]:
        """Get US trends from Yahoo"""
        try:
            url = "https://www.yahoo.com/topics/trending-now"
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                async with session.get(url, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        text = await response.text()
                        soup = BeautifulSoup(text, 'html.parser')
                        
                        trends = []
                        # Look for trending topics
                        for element in soup.find_all(['h2', 'h3', 'h4']):
                            trend_text = element.text.strip()
                            if trend_text and len(trend_text) > 5:
                                trends.append(trend_text)
                        
                        return trends[:15]  # Limit to top 15
        except Exception as e:
            logger.error(f"YahooTrendsCollector error: {e}")
        
        return []


class GoogleNewsCollector(BaseTrendCollector):
    """Collect trending news from Google News"""
    
    async def get_us_trends(self) -> List[str]:
        """Get US trending news from Google News"""
        try:
            url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=15) as response:
                    if response.status == 200:
                        text = await response.text()
                        soup = BeautifulSoup(text, 'xml')
                        
                        trends = []
                        for item in soup.find_all('item'):
                            title = item.find('title')
                            if title:
                                trends.append(title.text.strip())
                        
                        return trends[:20]  # Limit to top 20
        except Exception as e:
            logger.error(f"GoogleNewsCollector error: {e}")
        
        return []
