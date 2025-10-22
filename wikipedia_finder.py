"""
Wikipedia article finder
Searches for Wikipedia articles related to trending topics
"""

import logging
import aiohttp
import urllib.parse
from typing import Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class WikipediaFinder:
    """Find Wikipedia articles for trending topics"""
    
    def __init__(self):
        self.base_url = "https://en.wikipedia.org"
        self.api_url = f"{self.base_url}/w/api.php"
    
    async def find_article(self, topic: str) -> Optional[str]:
        """Find Wikipedia article URL for a given topic"""
        try:
            # First, try direct search using Wikipedia API
            params = {
                'action': 'opensearch',
                'search': topic,
                'limit': 1,
                'namespace': 0,
                'format': 'json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # OpenSearch returns [query, [titles], [descriptions], [urls]]
                        if len(data) >= 4 and len(data[3]) > 0:
                            url = data[3][0]
                            logger.info(f"Found Wikipedia article for '{topic}': {url}")
                            return url
                        
                        # If no direct match, try search
                        return await self._search_article(topic)
        except Exception as e:
            logger.error(f"Error finding article for '{topic}': {e}")
        
        return None
    
    async def _search_article(self, topic: str) -> Optional[str]:
        """Search for article using Wikipedia's search"""
        try:
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': topic,
                'srlimit': 1,
                'format': 'json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        search_results = data.get('query', {}).get('search', [])
                        if search_results:
                            title = search_results[0]['title']
                            # Construct URL from title
                            encoded_title = urllib.parse.quote(title.replace(' ', '_'))
                            url = f"{self.base_url}/wiki/{encoded_title}"
                            logger.info(f"Found Wikipedia article via search for '{topic}': {url}")
                            return url
        except Exception as e:
            logger.error(f"Error searching article for '{topic}': {e}")
        
        return None
    
    async def get_article_summary(self, url: str) -> str:
        """Get article summary/intro text for categorization"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        text = await response.text()
                        soup = BeautifulSoup(text, 'html.parser')
                        
                        # Get first paragraph
                        content_div = soup.find('div', {'id': 'mw-content-text'})
                        if content_div:
                            paragraphs = content_div.find_all('p', recursive=False)
                            for p in paragraphs:
                                text = p.get_text().strip()
                                if len(text) > 50:  # Get first substantial paragraph
                                    return text[:500]  # Return first 500 chars
        except Exception as e:
            logger.error(f"Error getting article summary from {url}: {e}")
        
        return ""
    
    async def get_summary_by_title(self, title: str) -> str:
        """Get Wikipedia article summary using API (faster than scraping)"""
        try:
            params = {
                'action': 'query',
                'prop': 'extracts',
                'exintro': '1',  # Use string instead of boolean
                'explaintext': '1',  # Use string instead of boolean
                'titles': title,
                'format': 'json'
            }
            
            headers = {
                'User-Agent': 'TrendCollector/1.0 (Educational Project)'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_url, params=params, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        pages = data.get('query', {}).get('pages', {})
                        
                        for page_id, page_data in pages.items():
                            if page_id != '-1':  # -1 means not found
                                extract = page_data.get('extract', '')
                                if extract:
                                    # Return first 500 characters
                                    return extract[:500]
        except Exception as e:
            logger.error(f"Error getting summary for '{title}': {e}")
        
        return ""
