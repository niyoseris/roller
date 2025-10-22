# Agentic Trend Collector

An autonomous agent that continuously monitors trending topics across multiple platforms and submits relevant Wikipedia articles to roll.wiki.

## Features

- **Multi-Platform Trend Collection**: Monitors REAL trends (not news headlines) from:
  - Twitter/X (via trends24.in) - Real trending keywords
  - Reddit - Keyword extraction from hot posts
  - Google Trends (PyTrends) - Daily trending searches
  - TikTok - Trending hashtags (when available)
  - Bing Trends - Search trends

- **AI-Powered Intelligence (Ollama)**:
  - **Local LLM**: Uses Ollama for completely free, local AI processing
  - **Model Selection**: Choose from 10+ models via web interface
  - **Intelligent Categorization**: AI-powered categorization into 27 categories with ~95% accuracy
  - **No API Keys**: Completely free, no rate limits, works offline
  - **Fallback System**: Keyword-based categorization when LLM is unavailable

- **Intelligent Processing**:
  - Automatically finds Wikipedia articles for trending topics
  - Duplicate detection to avoid reprocessing
  - Rate limiting (30 seconds between requests)
  - Scheduled cycles every 60 minutes

- **Robust & Reliable**:
  - Comprehensive error handling
  - Detailed logging to file and console
  - Persistent storage of processed URLs
  - Asynchronous operations for efficiency

## Installation

1. Install Python 3.8 or higher

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start

The easiest way to start:
```bash
./start.sh
```

Or manually with Python:
```bash
./venv/bin/python main.py
```

### Web Monitoring Dashboard

Once started, access the monitoring dashboard at:
```
http://localhost:5001
```

The dashboard shows:
- Real-time statistics
- Cycles completed
- Articles submitted
- Last cycle information
- Total processed URLs

### How It Works

The agent follows this workflow for each cycle:

1. **Start Web Dashboard** - Port 5001 with real-time statistics
2. **Collect Real Trends** - From multiple reliable sources:
   - **GetDayTrends** (Primary) - Twitter hashtags from getdaytrends.com
   - **Twitter** (Backup) - Twitter trends via Trends24
   - **Reddit** - Trending keywords from r/all
3. **For Each Trend:**
   - 🧹 Clean trend name (remove hashtags, numbers)
   - 📖 Fetch Wikipedia summary via API
   - 🤖 Categorize with Ollama LLM (27 categories, using summary)
   - 🔗 Create Wikipedia URL
   - 🚀 Submit to roll.wiki API (URL + Category)
   - ⏳ Wait 30 seconds before next trend
4. **Complete Cycle** - Wait 60 minutes, repeat

**Key Features:**
- ✅ Wikipedia API for getting article summaries
- ✅ LLM determines category using article content
- ✅ Only valid Wikipedia articles are submitted
- ✅ Duplicate detection to prevent resubmission
- ✅ 30-second delay between submissions

## Configuration

Key settings in `main.py`:

- `REQUEST_DELAY`: Seconds between API requests (default: 30)
- `CYCLE_INTERVAL`: Seconds between cycles (default: 3600 = 60 minutes)
- `SECRET`: roll.wiki API secret (default: "laylaylom")

## Categories

Articles are automatically categorized into one of 27 categories:
- Architecture, Arts, Business, Culture, Dance, Economics
- Education, Engineering, Entertainment, Environment, Fashion
- Film, Food, Geography, History, Literature, Medicine
- Music, Philosophy, Politics, Psychology, Religion, Science
- Sports, Technology, Theater, Transportation

## Logs

The application creates a `trend_collector.log` file with detailed operation logs.

## Data Storage

Processed Wikipedia URLs are stored in `processed_urls.json` to prevent duplicate submissions.

## API Endpoint

Submits to: `https://roll.wiki/api/v1/summarize`

**Method:** GET

**Example:**
```
GET https://roll.wiki/api/v1/summarize?url=https://en.wikipedia.org/wiki/NBA&save=true&category=Sports&secret=laylaylom
```

**Parameters:**
- `url`: Wikipedia article URL
- `save`: true (to save the article)
- `category`: Auto-detected category (27 options)
- `secret`: laylaylom (API authentication)

## Notes

- The application runs continuously. Use Ctrl+C to stop.
- Internet connection required
- Some platforms may have rate limiting
- Ensure the roll.wiki API is accessible
