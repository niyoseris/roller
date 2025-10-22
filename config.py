"""
Configuration file for Trend Collector Agent
Modify these settings as needed
"""

# API Configuration
ROLL_WIKI_API = "https://roll.wiki/api/v1/summarize"
ROLL_WIKI_SECRET = "laylaylom"

# Timing Configuration (in seconds)
REQUEST_DELAY = 30  # Delay between each Wikipedia article submission
CYCLE_INTERVAL = 3600  # Interval between trend collection cycles (60 minutes)

# Trend Collection Limits
MAX_TRENDS_PER_PLATFORM = 20  # Maximum trends to collect from each platform

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
