"""
Feature Control Dashboard for Agentic Trend Collector
Web interface to enable/disable features and monitor system status
"""

from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import json
import os
import asyncio
import subprocess
import signal
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from session_manager import SessionManager
from gemini_analyzer import GeminiAnalyzer
from url_tracker import URLTracker
import config

# Try to import VideoCreator - optional feature
try:
    from video_creator import VideoCreator
    VIDEO_CREATOR_AVAILABLE = True
except ImportError:
    VIDEO_CREATOR_AVAILABLE = False
    print("⚠️  Video creation functionality not available")

# Try to import TTS - optional feature
try:
    from text_to_speech import generate_speech, generate_multi_speaker_speech
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("⚠️  TTS functionality not available (missing google-genai package)")

app = Flask(__name__)
CORS(app)

# Initialize session manager, Gemini analyzer, and URL tracker
session_manager = SessionManager()
gemini_analyzer = GeminiAnalyzer()
url_tracker = URLTracker()

# Debug: Print all registered routes on startup
import atexit
def print_routes():
    print("\n" + "="*60)
    print("📋 Registered Flask Routes:")
    print("="*60)
    for rule in app.url_map.iter_rules():
        print(f"  {rule.methods} {rule.rule}")
    print("="*60 + "\n")
atexit.register(print_routes)

# Global process management
main_py_process = None

# Global TrendAgent reference (set by main.py)
trend_agent = None

# Configuration file for features
CONFIG_FILE = "dashboard_config.json"

# Default configuration
DEFAULT_CONFIG = {
    "features": {
        "twitter_posting": True,
        "video_creation": True,
        "youtube_upload": False,
        "google_trends_screenshot": True,
        "gemini_tts": True,
        "web_monitor": True
    },
    "trends_extraction": {
        "use_ocr": False,  # OCR is disabled by default
        "use_javascript_extraction": True,  # Direct page content extraction
        "max_scroll_attempts": 10,  # Maximum number of scroll attempts
        "scroll_wait_seconds": 2,  # Wait time between scrolls
        "min_content_length": 100  # Minimum characters for valid content
    },
    "video_settings": {
        "font_size": 40,  # Text font size in videos
        "padding_horizontal": 50,  # Horizontal padding from edges (pixels)
        "padding_vertical": 50,  # Vertical padding from edges (pixels)
        "stroke_width": 2,  # Text outline/stroke width (pixels)
        "scroll_speed": 50,  # Pixels per second for scrolling text
        "video_volume": 0.1,  # Background video volume (0.0-1.0)
        "force_english_tts": True  # Always use English for TTS
    },
    "settings": {
        "request_delay": 1800,  # 30 minutes
        "cycle_interval": 3600,  # 60 minutes
        "youtube_category": "22",  # People & Blogs
        "video_language": "en",
        "port": 5001
    },
    "stats": {
        "cycles_completed": 0,
        "articles_submitted": 0,
        "tweets_posted": 0,
        "videos_created": 0,
        "youtube_uploads": 0,
        "tts_generated": 0,
        "last_update": None
    }
}


def load_config():
    """Load configuration from file"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()


def save_config(config):
    """Save configuration to file"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


@app.route('/')
def index():
    """Dashboard homepage"""
    config = load_config()
    return render_template('dashboard.html', config=config)


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    config = load_config()
    return jsonify(config)


@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration"""
    try:
        new_config = request.json
        save_config(new_config)
        return jsonify({"success": True, "message": "Configuration updated"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


# Feature control removed - features are now managed through config file


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get current statistics"""
    config = load_config()
    return jsonify(config.get('stats', {}))


@app.route('/api/stats', methods=['POST'])
def update_stats():
    """Update statistics"""
    try:
        config = load_config()
        new_stats = request.json
        config['stats'].update(new_stats)
        config['stats']['last_update'] = datetime.now().isoformat()
        save_config(config)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update settings"""
    try:
        config = load_config()
        new_settings = request.json
        config['settings'].update(new_settings)
        save_config(config)
        return jsonify({"success": True, "message": "Settings updated"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route('/api/video-settings', methods=['POST'])
def update_video_settings():
    """Update video settings"""
    try:
        config = load_config()
        new_settings = request.json
        
        # Ensure video_settings key exists
        if 'video_settings' not in config:
            config['video_settings'] = DEFAULT_CONFIG['video_settings'].copy()
        
        config['video_settings'].update(new_settings)
        save_config(config)
        return jsonify({"success": True, "message": "Video settings updated"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


# TTS endpoints removed - TTS is managed internally by video creator


# ============= Session Management Endpoints =============

@app.route('/api/session/status', methods=['GET'])
def get_session_status():
    """Get current session status"""
    try:
        status = session_manager.get_session_status()
        trends_list = session_manager.session.get('manual_trends', [])
        processed = session_manager.session.get('processed_trends', [])
        failed = session_manager.session.get('failed_trends', [])
        trend_data = session_manager.session.get('trend_data', {})
        
        # For backward compatibility, also provide trend_urls
        trend_urls = {}
        for trend, data in trend_data.items():
            if isinstance(data, dict):
                trend_urls[trend] = data.get('url', '')
            else:
                trend_urls[trend] = data
        
        return jsonify({
            "success": True,
            "status": status,
            "trends": trends_list,
            "processed": processed,
            "failed": failed,
            "trend_data": trend_data,
            "trend_urls": trend_urls  # For backward compatibility
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/session/trends', methods=['POST'])
def set_trends():
    """Set manual trends list - FAST response, Gemini optional"""
    print("=" * 60)
    print("📝 /api/session/trends endpoint called")
    
    try:
        data = request.json
        trends = data.get('trends', [])
        use_gemini = data.get('use_gemini', True)  # Optional flag
        
        print(f"📊 Received {len(trends) if isinstance(trends, list) else 'string'} trends")
        
        # Parse trends - handle both line-separated string and array
        if isinstance(trends, str):
            trends = [t.strip() for t in trends.split('\n') if t.strip()]
        
        if not trends:
            print("❌ No trends provided")
            return jsonify({"success": False, "message": "Trend listesi boş"}), 400
        
        print(f"✅ Parsed {len(trends)} trends")
        
        # IMMEDIATELY create session with empty trend_data
        # This ensures fast response
        # Status will be "paused" so user must click "Start" button
        print("💾 Creating session (fast path)...")
        success = session_manager.start_new_session(trends, {}, auto_start=False)
        
        if not success:
            print("❌ Session save failed")
            return jsonify({"success": False, "message": "Trendler eklenemedi"}), 400
        
        print(f"✅ Session created successfully!")
        
        # Return immediately - don't wait for Gemini
        response = {
            "success": True,
            "message": f"{len(trends)} trend eklendi (Gemini tamamlanınca otomatik başlayacak)" if use_gemini else f"{len(trends)} trend eklendi ve başlatıldı",
            "total_trends": len(trends),
            "data_found": 0,
            "trend_data": {},
            "gemini_status": "processing" if use_gemini else "skipped"
        }
        
        print(f"✅ Returning immediate success response")
        print("=" * 60)
        
        # Auto-start session immediately (Gemini will analyze each trend individually now)
        session_manager.session['status'] = 'running'
        session_manager.save_session()
        print("✅ Session auto-started (Gemini will analyze each trend as it's processed)")
        
        return jsonify(response), 200
            
    except Exception as e:
        print(f"🔥 CRITICAL ERROR in set_trends: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"Hata: {str(e)}"}), 500


@app.route('/api/session/trends/add', methods=['POST'])
def add_trends():
    """Add trends to existing session"""
    try:
        data = request.json
        trends = data.get('trends', [])
        
        # Parse trends
        if isinstance(trends, str):
            trends = [t.strip() for t in trends.split('\n') if t.strip()]
        
        if not trends:
            return jsonify({"success": False, "message": "Trend listesi boş"}), 400
        
        success = session_manager.add_trends_to_session(trends)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"{len(trends)} yeni trend eklendi",
                "total_trends": session_manager.session['total_trends']
            })
        else:
            return jsonify({"success": False, "message": "Trendler eklenemedi"}), 400
            
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/session/start', methods=['POST'])
def start_session():
    """Start or resume scan session"""
    print("=" * 60)
    print("▶️  /api/session/start endpoint called")
    
    try:
        current_status = session_manager.session.get('status', 'idle')
        trends_count = len(session_manager.session.get('manual_trends', []))
        current_index = session_manager.session.get('current_index', 0)
        
        print(f"📊 Current Status: {current_status}")
        print(f"📋 Trends: {trends_count} total, index: {current_index}")
        
        if current_status == 'paused':
            print("✅ Status is paused, resuming...")
            session_manager.resume_session()
            print("✅ Session resumed!")
            print(f"🚀 main.py should now process trends starting from index {current_index}")
            print("=" * 60)
            return jsonify({
                "success": True,
                "message": "Tarama başlatıldı - main.py çalışıyorsa işlemeye başlayacak"
            })
        elif current_status == 'idle':
            print("❌ Status is idle, no trends added")
            print("=" * 60)
            return jsonify({
                "success": False,
                "message": "Önce trend listesi ekleyin"
            }), 400
        else:
            print(f"⚠️  Status is already: {current_status}")
            print("=" * 60)
            return jsonify({
                "success": True,
                "message": f"Tarama durumu: {current_status}"
            })
            
    except Exception as e:
        print(f"🔥 ERROR in start_session: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/session/pause', methods=['POST'])
def pause_session():
    """Pause current scan session"""
    try:
        session_manager.pause_session()
        return jsonify({
            "success": True,
            "message": "Tarama duraklatıldı"
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/session/reset', methods=['POST'])
def reset_session():
    """Reset session"""
    try:
        session_manager.reset_session()
        return jsonify({
            "success": True,
            "message": "Oturum sıfırlandı"
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/reports', methods=['GET'])
def get_reports():
    """Get all reports"""
    try:
        reports = session_manager.get_reports()
        return jsonify({
            "success": True,
            "reports": reports,
            "count": len(reports)
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/reports/<trend>', methods=['GET'])
def get_report(trend):
    """Get report for specific trend"""
    try:
        report = session_manager.get_report(trend)
        if report:
            return jsonify({
                "success": True,
                "report": report
            })
        else:
            return jsonify({
                "success": False,
                "message": "Rapor bulunamadı"
            }), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/reports/clear', methods=['POST'])
def clear_reports():
    """Clear all reports"""
    try:
        session_manager.clear_reports()
        return jsonify({
            "success": True,
            "message": "Tüm raporlar silindi"
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/videos', methods=['GET'])
def list_videos():
    """List all created videos (including category folders)"""
    try:
        import os
        from pathlib import Path
        
        output_dir = Path('output_videos')
        if not output_dir.exists():
            return jsonify({
                "success": True,
                "videos": [],
                "count": 0
            })
        
        videos = []
        
        # Scan root folder for videos
        for video_file in output_dir.glob('*.mp4'):
            stat = video_file.stat()
            videos.append({
                "filename": video_file.name,
                "path": str(video_file),
                "relative_path": video_file.name,
                "category": None,
                "size": stat.st_size,
                "created_at": stat.st_mtime,
                "trend_name": video_file.stem.replace('_shorts', '').replace('_', ' ')
            })
        
        # Scan category folders for videos
        for category_folder in output_dir.iterdir():
            if category_folder.is_dir():
                category_name = category_folder.name
                for video_file in category_folder.glob('*.mp4'):
                    stat = video_file.stat()
                    videos.append({
                        "filename": video_file.name,
                        "path": str(video_file),
                        "relative_path": f"{category_name}/{video_file.name}",
                        "category": category_name.replace('_', ' '),
                        "size": stat.st_size,
                        "created_at": stat.st_mtime,
                        "trend_name": video_file.stem.replace('_shorts', '').replace('_', ' ')
                    })
        
        # Sort by creation time, newest first
        videos.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({
            "success": True,
            "videos": videos,
            "count": len(videos)
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ============= Video Recreation (Moved to main.py) =============
# The /api/video/recreate endpoint is now defined in main.py
# to keep all TrendAgent operations centralized


@app.route('/api/video/<path:filename>', methods=['GET'])
def serve_video(filename):
    """Serve video file (supports category folders)"""
    try:
        from pathlib import Path
        video_path = Path('output_videos') / filename
        
        if not video_path.exists():
            return jsonify({
                "success": False,
                "message": "Video bulunamadı"
            }), 404
        
        return send_file(str(video_path), mimetype='video/mp4')
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ============= Main.py Process Control =============

@app.route('/api/agent/status', methods=['GET'])
def get_agent_status():
    """Get main.py agent status"""
    global main_py_process
    
    is_running = main_py_process is not None and main_py_process.poll() is None
    
    return jsonify({
        "success": True,
        "running": is_running,
        "pid": main_py_process.pid if is_running else None
    })


@app.route('/api/agent/start', methods=['POST'])
def start_agent():
    """Start main.py agent"""
    global main_py_process
    
    print("=" * 60)
    print("🚀 Starting main.py agent...")
    
    try:
        # Check if already running
        if main_py_process and main_py_process.poll() is None:
            print("⚠️  Agent already running")
            print("=" * 60)
            return jsonify({
                "success": False,
                "message": "Agent zaten çalışıyor"
            }), 400
        
        # Start main.py as subprocess
        print("  → Launching subprocess...")
        main_py_process = subprocess.Popen(
            ['python3', 'main.py'],
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"  ✅ Agent started with PID: {main_py_process.pid}")
        print("=" * 60)
        
        return jsonify({
            "success": True,
            "message": "Agent başlatıldı",
            "pid": main_py_process.pid
        })
        
    except Exception as e:
        print(f"🔥 ERROR starting agent: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/agent/stop', methods=['POST'])
def stop_agent():
    """Stop main.py agent"""
    global main_py_process
    
    print("=" * 60)
    print("🛑 Stopping main.py agent...")
    
    try:
        if not main_py_process or main_py_process.poll() is not None:
            print("⚠️  Agent not running")
            print("=" * 60)
            return jsonify({
                "success": False,
                "message": "Agent zaten durmuş"
            }), 400
        
        print(f"  → Terminating PID: {main_py_process.pid}")
        main_py_process.terminate()
        
        # Wait for graceful shutdown
        try:
            main_py_process.wait(timeout=5)
            print("  ✅ Agent stopped gracefully")
        except subprocess.TimeoutExpired:
            print("  ⚠️  Timeout, forcing kill...")
            main_py_process.kill()
            main_py_process.wait()
            print("  ✅ Agent killed")
        
        main_py_process = None
        print("=" * 60)
        
        return jsonify({
            "success": True,
            "message": "Agent durduruldu"
        })
        
    except Exception as e:
        print(f"🔥 ERROR stopping agent: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/agent/restart', methods=['POST'])
def restart_agent():
    """Restart main.py agent"""
    print("=" * 60)
    print("🔄 Restarting main.py agent...")
    
    # Stop first
    stop_result = stop_agent()
    if stop_result[1] not in [200, 400]:  # 400 means already stopped
        return stop_result
    
    # Start
    return start_agent()


@app.route('/api/create-video', methods=['POST'])
def create_video():
    """Create video for a single trend"""
    if not VIDEO_CREATOR_AVAILABLE:
        return jsonify({
            "success": False,
            "message": "Video Creator not available"
        }), 400
    
    try:
        data = request.json
        trend = data.get('trend', '').strip()
        text = data.get('text', '').strip()
        scroll_speed = int(data.get('scroll_speed', 50))
        font_size = int(data.get('font_size', 45))
        orientation = data.get('orientation', 'portrait')
        video_volume = float(data.get('video_volume', 0.1))
        
        if not trend:
            return jsonify({
                "success": False,
                "message": "Trend name required"
            }), 400
        
        if not text:
            return jsonify({
                "success": False,
                "message": "Text content required"
            }), 400
        
        print(f"🎬 Creating video for: {trend}")
        print(f"  → Scroll speed: {scroll_speed} px/s")
        print(f"  → Font size: {font_size}")
        print(f"  → Orientation: {orientation}")
        
        # Create video
        video_creator = VideoCreator(
            use_edge_tts=True,
            use_gemini_tts=True,
            use_bark_tts=True,
            config={'video_settings': config.VIDEO_SETTINGS}
        )
        video_filename = f"{trend.replace(' ', '_').replace('/', '_')}_shorts.mp4"
        
        video_path = video_creator.create_video_from_pexels(
            search_query=trend,
            text=text,
            output_filename=video_filename,
            narration_lang='en',
            scroll_speed=scroll_speed,
            font_size=font_size,
            orientation=orientation,
            video_volume=video_volume
        )
        
        if video_path:
            print(f"  ✅ Video created: {video_path}")
            return jsonify({
                "success": True,
                "message": "Video created successfully",
                "video_path": str(video_path)  # Convert PosixPath to string
            })
        else:
            print("  ❌ Video creation failed")
            return jsonify({
                "success": False,
                "message": "Video creation failed"
            }), 500
            
    except Exception as e:
        print(f"🔥 ERROR creating video: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


if __name__ == '__main__':
    # Initialize config file if it doesn't exist
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
    
    config = load_config()
    port = config['settings'].get('port', 5001)
    
    print(f"🚀 Dashboard starting on http://localhost:{port}")
    print(f"📊 Feature Control Panel: http://localhost:{port}")
    
    # Debug: Print all routes
    print("\n" + "="*60)
    print("📋 Registered Flask Routes:")
    print("="*60)
    for rule in app.url_map.iter_rules():
        print(f"  {list(rule.methods)} {rule.rule}")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)
