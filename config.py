"""
Configuration file for Trend Collector Agent
Modify these settings as needed
"""

import os

# API Configuration
ROLL_WIKI_API = "https://roll.wiki/api/v1/summarize"
ROLL_WIKI_SECRET = os.getenv('ROLL_WIKI_SECRET', '')

# Timing Configuration (in seconds)
REQUEST_DELAY = 30  # Delay between each Wikipedia article submission
CYCLE_INTERVAL = 3600  # Interval between trend collection cycles (60 minutes)

# Trend Collection Limits
MAX_TRENDS_PER_PLATFORM = 200  # Maximum trends to collect from each platform

# Available Categories (case-sensitive)
CATEGORIES = [
    "Architecture",
    "Arts",
    "Business",
    "Culture",
    "Dance",
    "Economics",
    "Education",
    "Engineering",
    "Entertainment",
    "Environment",
    "Fashion",
    "Film",
    "Food",
    "Geography",
    "History",
    "Literature",
    "Medicine",
    "Music",
    "Philosophy",
    "Politics",
    "Psychology",
    "Religion",
    "Science",
    "Sports",
    "Technology",
    "Theater",
    "Transportation"
]

# Database Configuration
PROCESSED_URLS_DB = "processed_urls.json"
LOG_FILE = "trend_collector.log"

# HTTP Configuration
REQUEST_TIMEOUT = 15  # Timeout for HTTP requests in seconds
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Logging Configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Twitter Configuration
# To enable Twitter posting, set these environment variables:
# - TWITTER_API_KEY (Consumer Key)
# - TWITTER_API_SECRET (Consumer Secret)
# - TWITTER_ACCESS_TOKEN
# - TWITTER_ACCESS_TOKEN_SECRET
# - TWITTER_BEARER_TOKEN (optional, for API v2)
TWITTER_ENABLED = True  # Set to False to disable Twitter posting
TWITTER_POST_ON_SUCCESS = True  # Post tweet when article is successfully submitted

# Video Configuration
VIDEO_ENABLED = True  # Set to False to skip video creation (faster processing)

# YouTube Configuration
YOUTUBE_ENABLED = True  # Set to False to disable YouTube Shorts upload

# Video Settings
VIDEO_SETTINGS = {
    'scroll_speed': 350,      # Pixels per second (default: 50, faster: 100+)
    'font_size': 42,          # Text size (default: 24, mobile: 24-28)
    'video_volume': 0.0,      # Background video volume (0.0=muted, 0.1=quiet, 1.0=full)
    'padding_horizontal': 20, # Left/right padding
    'padding_vertical': 50,   # Top/bottom padding
    'stroke_width': 2,        # Text outline width
    'force_english_tts': True # Always use English TTS
}
