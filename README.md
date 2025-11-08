# 🤖 Agentic Trend Video Creator

**Autonomous AI agent that transforms Wikipedia articles into engaging YouTube Shorts videos automatically.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Google Gemini](https://img.shields.io/badge/AI-Gemini%202.5-orange.svg)](https://ai.google.dev/)

## ✨ Features

### 🎬 **Automated Video Production**
- **AI-Powered Narration**: High-quality text-to-speech using Google Gemini TTS (1.2x speed for <60s videos)
- **Multi-TTS Support**: Gemini TTS → Edge TTS → Bark TTS fallback chain
- **Dynamic Text Overlay**: Beautiful markdown-formatted text with scrolling animation
- **Smart Video Selection**: Random background videos from Pexels API matching trend keywords
- **YouTube Shorts Ready**: Portrait format (1080x1920), optimized for mobile viewing

### 🎯 **Intelligent Trend Processing**
- **Google Gemini AI**: Analyzes trends to find Wikipedia URLs and determine categories
- **27 Categories**: Automatic categorization (Sports, Science, Entertainment, etc.)
- **Manual Trend Input**: Web dashboard for adding custom trends
- **Session Management**: Tracks progress, processed trends, and failures
- **Smart Retry**: Skips failed trends and continues processing

### 🚀 **YouTube Automation**
- **Auto-Upload to YouTube Shorts**: Videos automatically uploaded after creation
- **OAuth2 Authentication**: Secure Google API integration
- **Category Folders**: Videos organized by category in `output_videos/`
- **Metadata Management**: Auto-generated titles and descriptions

### 📊 **Real-Time Dashboard**
- **Web Interface**: Beautiful, responsive dashboard at `http://localhost:5001`
- **Live Statistics**: Articles, videos, YouTube uploads tracking
- **Trend Progress**: Visual progress bar with trend status (⏳ pending, 🔄 processing, ✅ success, ❌ failed)
- **Video Gallery**: Play videos directly in dashboard, organized by category
- **Session Controls**: Start, pause, reset functionality

### 🛠️ **Developer-Friendly**
- **Configurable**: Extensive settings via `config.py`
- **Logging**: Comprehensive logging for debugging
- **Error Handling**: Robust error recovery and reporting
- **Hot Reload**: Dashboard updates every 5 seconds

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- FFmpeg (for video processing)
- Google Gemini API key
- Pexels API key (for background videos)
- YouTube API credentials (optional, for auto-upload)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/agentic.git
cd agentic
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure API keys**
```bash
cp .env.example .env
# Edit .env and add your API keys:
# - GEMINI_API_KEY (required)
# - PEXELS_API_KEY (required for videos)
# - ROLL_WIKI_SECRET (required for article submission)
# - TWITTER credentials (optional)
```

5. **Run the application**
```bash
python3 main.py
```

6. **Open dashboard**
```
http://localhost:5001
```

---

## 📖 Usage Guide

### Adding Trends

1. Open the dashboard at `http://localhost:5001`
2. In the "Manuel Trend Ekle" section, enter trends (one per line):
```
ChatGPT
NBA Finals
Climate Change
Taylor Swift
```
3. Click **"🚀 Ekle ve Başlat"**
4. Watch the magic happen! ✨

### How It Works

```
User Input → Gemini AI Analysis → Wikipedia Fetch → Video Creation → YouTube Upload
     ↓              ↓                    ↓                ↓                ↓
  Trends      URL + Category        Summary         Narration      Automatic
              + Keywords            + Text          + Video         Shorts
```

**Processing Pipeline:**
1. **AI Analysis**: Gemini finds Wikipedia URL and category for each trend
2. **Content Fetch**: Gets article summary from Wikipedia API
3. **Video Creation**:
   - Generates narration audio (Gemini/Edge/Bark TTS)
   - Fetches matching background video from Pexels
   - Creates scrolling text overlay with markdown support
   - Combines audio + video + text
4. **YouTube Upload**: Auto-uploads as YouTube Short (if enabled)
5. **Dashboard Update**: Real-time progress tracking

---

## ⚙️ Configuration

### Main Settings (`config.py`)

```python
# Timing
REQUEST_DELAY = 30  # Seconds between trend processing
CYCLE_INTERVAL = 3600  # Seconds between cycles

# Features
VIDEO_ENABLED = True  # Enable video creation
YOUTUBE_ENABLED = True  # Enable YouTube upload
TWITTER_ENABLED = True  # Enable Twitter posting

# Video Settings
VIDEO_SETTINGS = {
    'scroll_speed': 350,      # Text scroll speed (px/s)
    'font_size': 42,          # Text size
    'video_volume': 0.0,      # Background volume (0.0 = muted)
    'force_english_tts': True # Always use English TTS
}
```

### YouTube Setup (Optional)

See **[YOUTUBE_SETUP.md](YOUTUBE_SETUP.md)** for detailed instructions.

**Quick steps:**
1. Create Google Cloud project
2. Enable YouTube Data API v3
3. Download `youtube_credentials.json`
4. Run first-time OAuth flow

---

## 📂 Project Structure

```
agentic/
├── main.py                 # Main application entry point
├── config.py              # Configuration settings
├── dashboard.py           # Flask web dashboard
├── gemini_analyzer.py     # Gemini AI integration
├── video_creator.py       # Video generation engine
├── youtube_uploader.py    # YouTube Shorts uploader
├── session_manager.py     # Session state management
├── text_to_speech.py      # TTS generation
├── templates/
│   └── dashboard.html     # Dashboard UI
├── output_videos/         # Generated videos (by category)
│   ├── Sports/
│   ├── Science/
│   └── ...
├── .env.example          # Environment variables template
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

---

## 🎨 Video Output

**Format Specifications:**
- **Resolution**: 1080x1920 (9:16 portrait)
- **Duration**: <60 seconds (optimized for Shorts)
- **Audio**: English narration at 1.2x speed
- **Video**: High-quality Pexels footage
- **Text**: Scrolling markdown-formatted overlay
- **Output**: `output_videos/{Category}/{trend}_shorts.mp4`

---

## 🔑 API Keys Required

| Service | Purpose | Required | Get Key |
|---------|---------|----------|---------|
| **Gemini API** | AI analysis & TTS | ✅ Yes | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| **Pexels API** | Background videos | ✅ Yes | [Pexels API](https://www.pexels.com/api/) |
| **Roll.Wiki** | Article submission | ✅ Yes | Contact [roll.wiki](https://roll.wiki/) |
| **YouTube API** | Auto-upload | ⚠️ Optional | [Google Cloud Console](https://console.cloud.google.com/) |
| **Twitter API** | Tweet posting | ⚠️ Optional | [Twitter Developer Portal](https://developer.twitter.com/) |

---

## 📊 Categories (27 Total)

```
Architecture  Arts          Business      Culture       Dance
Economics     Education     Engineering   Entertainment Environment
Fashion       Film          Food          Geography     History
Literature    Medicine      Music         Philosophy    Politics
Psychology    Religion      Science       Sports        Technology
Theater       Transportation
```

---

## 🐛 Troubleshooting

### Common Issues

**1. "GEMINI_API_KEY not found"**
- Create `.env` file from `.env.example`
- Add your Gemini API key

**2. "FFmpeg not found"**
- Install FFmpeg: `brew install ffmpeg` (Mac) or download from [ffmpeg.org](https://ffmpeg.org/)

**3. "Pexels API rate limit"**
- Free tier: 200 requests/hour
- Wait or upgrade to paid plan

**4. Videos not creating**
- Check TTS fallback chain in logs
- Verify Pexels API key
- Ensure FFmpeg is installed

**5. YouTube upload fails**
- Check `youtube_credentials.json` exists
- Re-run OAuth flow: `python3 youtube_uploader.py`
- Verify API quota (10,000 units/day)

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google Gemini** for AI analysis and TTS
- **Pexels** for high-quality stock videos
- **Microsoft Edge TTS** for fallback narration
- **Suno AI Bark** for local TTS fallback
- **Roll.Wiki** for article summarization platform

---

## 📮 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/agentic/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/agentic/discussions)

---

**Made with ❤️ and 🤖 AI**

---

## 🔮 Roadmap

- [ ] Multi-language support
- [ ] Custom video templates
- [ ] Instagram Reels support
- [ ] TikTok auto-upload
- [ ] Voice cloning integration
- [ ] Advanced video effects
- [ ] Batch processing mode
- [ ] REST API for external integrations
