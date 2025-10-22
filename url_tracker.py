"""
URL Tracker
Keeps track of processed Wikipedia URLs to avoid duplicates
"""

import json
import logging
from typing import Set
from pathlib import Path

logger = logging.getLogger(__name__)


class URLTracker:
    """Track processed Wikipedia URLs"""
    
    def __init__(self, db_file: str = "processed_urls.json"):
        self.db_file = Path(db_file)
        self.processed_urls: Set[str] = self._load_db()
    
    def _load_db(self) -> Set[str]:
        """Load processed URLs from database file"""
        try:
            if self.db_file.exists():
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    urls = set(data.get('urls', []))
                    logger.info(f"Loaded {len(urls)} processed URLs from database")
                    return urls
        except Exception as e:
            logger.error(f"Error loading URL database: {e}")
        
        return set()
    
    def _save_db(self):
        """Save processed URLs to database file"""
        try:
            data = {
                'urls': list(self.processed_urls)
            }
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving URL database: {e}")
    
    def is_processed(self, url: str) -> bool:
        """Check if URL has been processed"""
        return url in self.processed_urls
    
    def mark_processed(self, url: str):
        """Mark URL as processed"""
        self.processed_urls.add(url)
        self._save_db()
        logger.info(f"Marked as processed: {url}")
    
    def get_count(self) -> int:
        """Get count of processed URLs"""
        return len(self.processed_urls)
    
    def clear(self):
        """Clear all processed URLs (use with caution!)"""
        self.processed_urls.clear()
        self._save_db()
        logger.warning("Cleared all processed URLs")
