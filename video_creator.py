#!/usr/bin/env python3
"""
Video Creator - Pexels video + scrolling text + narration
"""

import os
import requests
from pathlib import Path
from typing import Optional
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip, ImageClip, concatenate_videoclips, CompositeAudioClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from gtts import gTTS
import edge_tts
import asyncio
import subprocess
import logging
import random
from gemini_analyzer import GeminiAnalyzer
from exceptions import TTSQuotaExceeded

# Try to import Piper TTS (local, fast, free)
try:
    from piper_tts import PiperTTS
    PIPER_TTS_AVAILABLE = True
except ImportError:
    PIPER_TTS_AVAILABLE = False
    logger.info("⚠️  Piper TTS not available (install with: pip install piper-tts)")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import markdown for rich text support
try:
    import markdown
    from bs4 import BeautifulSoup
    MARKDOWN_SUPPORT = True
except ImportError:
    MARKDOWN_SUPPORT = False
    logger.info("⚠️  Markdown support not available (install with: pip install markdown beautifulsoup4)")


class VideoCreator:
    """Creates videos with scrolling text and narration"""
    
    def __init__(
        self, 
        pexels_api_key: Optional[str] = None, 
        use_gemini_tts: bool = True,
        use_piper_tts: bool = False,
        use_edge_tts: bool = True,
        use_bark_tts: bool = True,
        config: dict = None
    ):
        """
        Initialize VideoCreator
        
        Args:
            pexels_api_key: Pexels API key (get from https://www.pexels.com/api/)
            use_gemini_tts: Use Gemini TTS instead of gTTS (default: True)
            use_piper_tts: Use Piper TTS (local, fast) if available (default: False)
            use_edge_tts: Use Edge TTS (Microsoft, high quality, free) (default: True)
            use_bark_tts: Use Bark TTS from Suno AI (local, high quality fallback) (default: True)
            config: Configuration dictionary from dashboard
        """
        self.pexels_api_key = pexels_api_key or os.getenv('PEXELS_API_KEY')
        self.output_dir = Path('output_videos')
        self.output_dir.mkdir(exist_ok=True)
        
        self.temp_dir = Path('temp_videos')
        self.temp_dir.mkdir(exist_ok=True)
        
        # Load video settings from config
        self.config = config or {}
        video_settings = self.config.get('video_settings', {})
        self.font_size = video_settings.get('font_size', 24)
        self.padding_horizontal = video_settings.get('padding_horizontal', 50)
        self.padding_vertical = video_settings.get('padding_vertical', 50)
        self.stroke_width = video_settings.get('stroke_width', 2)
        self.scroll_speed = video_settings.get('scroll_speed', 50)
        self.video_volume = video_settings.get('video_volume', 0.1)
        self.force_english_tts = video_settings.get('force_english_tts', True)
        
        # Initialize TTS engines (priority: Gemini > Edge > Bark > Piper > gTTS)
        self.use_edge_tts = use_edge_tts
        self.use_gemini_tts = use_gemini_tts
        self.use_piper_tts = use_piper_tts
        self.use_bark_tts = use_bark_tts
        self.piper_tts = None
        self.gemini_analyzer = None
        self.bark_model = None
        
        # Always initialize Gemini for video search keywords (even if not using for TTS)
        if use_gemini_tts or use_edge_tts:
            self.gemini_analyzer = GeminiAnalyzer()
            logger.info("✅ Gemini initialized for video search keywords")
        
        # 1. Edge TTS (Highest priority - Microsoft, studio quality, free)
        if use_edge_tts:
            logger.info("✅ Edge TTS enabled (Microsoft, studio quality, free)")
            logger.info(f"   Voice: en-US-GuyNeural (professional narrator)")
            logger.info("   📌 Using premium neural voices with natural prosody")
        
        # 2. Gemini TTS (High quality, Google)
        elif use_gemini_tts:
            logger.info(f"✅ Gemini TTS enabled (Google, Charon voice)")
            logger.info(f"   English: {self.force_english_tts}")
        
        # 3. Piper TTS (Local, fast, good quality)
        elif use_piper_tts:
            try:
                from piper_tts import PiperTTS
                # Use high quality voice model for better performance
                self.piper_tts = PiperTTS(voice_model="en_US-libritts-high")
                logger.info("✅ Piper TTS enabled (local, fast, free)")
                logger.info(f"   Voice: en_US-libritts-high (high quality)")
            except Exception as e:
                logger.warning(f"⚠️  Piper TTS not available: {e}")
                logger.info("   Falling back to gTTS")
        
        # 4. Final fallback to gTTS (basic quality)
        else:
            logger.info(f"Using gTTS (basic quality)")
            logger.info(f"   English: {self.force_english_tts}")
    
    def search_pexels_video(self, query: str, orientation: str = "portrait", 
                           size: str = "medium") -> Optional[dict]:
        """
        Search for a video on Pexels and randomly select one from results
        
        Args:
            query: Search query (e.g., "technology", "nature")
            orientation: "portrait" (default, for Reels/Shorts), "landscape", or "square"
            size: "large", "medium", or "small"
            
        Returns:
            Video info dict or None (randomly selected from up to 15 results)
        """
        if not self.pexels_api_key:
            logger.error("Pexels API key not provided!")
            return None
        
        url = "https://api.pexels.com/videos/search"
        headers = {"Authorization": self.pexels_api_key}
        params = {
            "query": query,
            "orientation": orientation,
            "size": size,
            "per_page": 15  # Get multiple videos for random selection
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('videos') and len(data['videos']) > 0:
                # Randomly select a video from the results
                video = random.choice(data['videos'])
                logger.info(f"🎲 Randomly selected video (from {len(data['videos'])} results): {video.get('url')}")
                
                # Get HD video file
                video_files = video.get('video_files', [])
                for vf in video_files:
                    if vf.get('quality') == 'hd':
                        return {
                            'url': vf.get('link'),
                            'width': vf.get('width'),
                            'height': vf.get('height'),
                            'duration': video.get('duration'),
                            'id': video.get('id')
                        }
                
                # Fallback to first video file
                if video_files:
                    vf = video_files[0]
                    return {
                        'url': vf.get('link'),
                        'width': vf.get('width'),
                        'height': vf.get('height'),
                        'duration': video.get('duration'),
                        'id': video.get('id')
                    }
            
            logger.warning(f"No videos found for query: {query}")
            return None
            
        except Exception as e:
            logger.error(f"Error searching Pexels: {e}")
            return None
    
    def download_video(self, video_url: str, output_path: Path) -> bool:
        """Download video from URL"""
        try:
            logger.info(f"Downloading video from {video_url}")
            response = requests.get(video_url, stream=True)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Video downloaded: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            return False
    
    async def create_narration_edge(self, text: str, output_path: Path, voice: str = 'en-US-AriaNeural', rate: str = '+20%') -> bool:
        """
        Create high-quality narration using Edge TTS (Microsoft, free)
        
        Args:
            text: Text to convert to speech
            output_path: Output audio file path
            voice: Voice name (en-US-AriaNeural, tr-TR-AhmetNeural, etc.)
                   Full list: https://speech.microsoft.com/portal/voicegallery
            rate: Speech rate (e.g., '+20%' for 20% faster, '-10%' for slower)
        """
        try:
            logger.info(f"Creating high-quality narration with Edge TTS ({voice}, rate={rate})...")
            logger.info(f"Text preview: {text[:80]}...")
            
            communicate = edge_tts.Communicate(text, voice, rate=rate)
            await communicate.save(str(output_path))
            
            logger.info(f"✅ High-quality narration saved: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Edge TTS failed: {e}")
            logger.warning("⚠️  Edge TTS failed, will retry after waiting...")
            return False
    
    def create_narration_gtts(self, text: str, output_path: Path, lang: str = 'en') -> bool:
        """
        Fallback: Create narration using gTTS (lower quality but reliable)
        
        Args:
            text: Text to convert to speech
            output_path: Output audio file path
            lang: Language code ('en', 'tr', etc.)
        """
        try:
            logger.info(f"Creating narration with gTTS for: {text[:50]}...")
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(str(output_path))
            logger.info(f"Narration saved: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating narration: {e}")
            return False
    
    def create_narration_bark(self, text: str, output_path: Path) -> bool:
        """
        Create narration using Bark TTS from Suno AI (high quality local fallback)
        
        Args:
            text: Text to convert to speech
            output_path: Output audio file path
        """
        try:
            logger.info(f"Creating narration with Bark TTS (Suno AI)...")
            logger.info(f"Text preview: {text[:80]}...")
            
            # Lazy load Bark (only when needed)
            if self.bark_model is None:
                logger.info("Loading Bark TTS model from Suno AI...")
                from bark import SAMPLE_RATE, generate_audio, preload_models
                # Download and load all models (first time only)
                preload_models()
                self.bark_model = True  # Mark as loaded
                logger.info("✅ Bark TTS model loaded")
            
            from bark import SAMPLE_RATE, generate_audio
            
            # Generate speech with Bark
            # Use 'v2/en_speaker_6' for male narrator voice
            audio_array = generate_audio(text, history_prompt="v2/en_speaker_6")
            
            # Save audio
            from scipy.io.wavfile import write as write_wav
            write_wav(str(output_path), SAMPLE_RATE, audio_array)
            
            logger.info(f"✅ Bark TTS narration saved: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Bark TTS failed: {e}")
            logger.warning("⚠️  Bark TTS failed, will retry after waiting...")
            import traceback
            traceback.print_exc()
            return False
    
    def _clean_text_for_tts(self, text: str) -> str:
        """
        Clean text for TTS by removing markdown, asterisks, and special formatting
        
        Args:
            text: Raw text with possible markdown
            
        Returns:
            Cleaned text suitable for TTS
        """
        import re
        
        # Remove markdown bold (**text** or __text__)
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        
        # Remove markdown italic (*text* or _text_)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)
        
        # Remove markdown headers (# ## ###)
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        
        # Remove markdown links [text](url)
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
        
        # Remove remaining single asterisks/underscores
        text = text.replace('*', '').replace('_', '')
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        logger.debug(f"Cleaned text for TTS: {text[:100]}...")
        return text
    
    def _calculate_optimal_scroll_speed(self, text: str, video_width: int, video_height: int, 
                                       narration_duration: float = None, 
                                       font_size: int = 24) -> tuple[float, float]:
        """
        Calculate optimal scroll speed based on text length, video height, and narration duration
        Uses the EXACT same text wrapping logic as FFmpeg to ensure accurate calculation
        
        Args:
            text: Text to display
            video_width: Width of video in pixels
            video_height: Height of video in pixels
            narration_duration: Duration of narration in seconds (if available)
            font_size: Font size in pixels
            
        Returns:
            Tuple of (scroll_speed in px/s, target_duration in seconds)
        """
        # Use EXACT same calculation as FFmpeg (lines 608-645)
        padding = 30  # 15px each side - minimal safe margin
        max_text_width = video_width - (padding * 2)
        chars_per_line = int(max_text_width / (font_size * 0.6))
        
        # Wrap text exactly like FFmpeg does
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            
            # If word is too long for a line, put it on its own line anyway
            if word_length > chars_per_line:
                # Flush current line first if it has content
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = []
                    current_length = 0
                # Add long word on its own line
                lines.append(word)
            elif current_length + word_length > chars_per_line and current_line:
                # Current line is full, start new line
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_length
            else:
                # Add word to current line
                current_line.append(word)
                current_length += word_length
        
        # Don't forget the last line
        if current_line:
            lines.append(' '.join(current_line))
        
        # No arbitrary line limit - show all text
        # lines = lines[:80]  # REMOVED: This was causing text truncation
        
        # Calculate text height using EXACT same formula as FFmpeg
        # FFmpeg uses line_h which is calculated internally, we match it here
        line_height = int(font_size * 1.2)  # FFmpeg's default line height is ~1.2x font size
        text_box_height = len(lines) * line_height
        
        # Total scroll distance: text starts at bottom (video_height) and scrolls up
        # until last line reaches top (y=0), then continues until ALL text is completely off screen
        # We need to add full text height to ensure last line scrolls completely off top
        scroll_distance = video_height + text_box_height
        
        if narration_duration:
            # Use narration duration for perfect sync
            optimal_speed = scroll_distance / narration_duration
            target_duration = narration_duration
            logger.info(f"📐 Optimal scroll calculation (exact FFmpeg logic):")
            logger.info(f"   Text: {len(text)} chars, {len(lines)} lines")
            logger.info(f"   Line height: {line_height}px (font_size {font_size}px * 1.2)")
            logger.info(f"   Text box height: {text_box_height}px")
            logger.info(f"   Video height: {video_height}px")
            logger.info(f"   Scroll distance: {scroll_distance}px (video_height + text_box_height)")
            logger.info(f"   Narration: {narration_duration:.1f}s")
            logger.info(f"   Optimal speed: {optimal_speed:.1f}px/s")
            logger.info(f"   ✅ At t={narration_duration:.1f}s: y = {video_height} - {optimal_speed:.1f} * {narration_duration:.1f} = {video_height - (optimal_speed * narration_duration):.1f}px (should be ~-{text_box_height}px)")
            logger.info(f"   ✅ Text will finish scrolling exactly when narration ends")
            return (optimal_speed, target_duration)
        else:
            # No narration - use config default or estimate based on reading speed
            # Average reading: ~200 words per minute = ~3.3 words/sec
            words_count = len(words)
            estimated_read_time = words_count / 3.3  # seconds
            optimal_speed = scroll_distance / estimated_read_time
            target_duration = estimated_read_time
            logger.info(f"📐 Estimated scroll (no narration):")
            logger.info(f"   Text: {words_count} words, {len(lines)} lines")
            logger.info(f"   Estimated read time: {estimated_read_time:.1f}s")
            logger.info(f"   Optimal speed: {optimal_speed:.1f}px/s")
            return (optimal_speed, target_duration)
    
    def create_scrolling_text_clip(self, text: str, video_size: tuple, 
                                   duration: float, font_size: int = 28,
                                   color: str = 'white', bg_color: str = 'black',
                                   scroll_speed: float = 50) -> TextClip:
        """
        Create a scrolling text clip
        
        Args:
            text: Text to display
            video_size: (width, height) of the video
            duration: Duration in seconds
            font_size: Font size
            color: Text color
            bg_color: Background color
            scroll_speed: Scrolling speed (pixels per second)
        """
        width, height = video_size
        
        # Create text clip with semi-transparent black background
        txt_clip = TextClip(
            text=text,
            font_size=font_size,
            color=color,
            bg_color=bg_color,
            method='caption',
            size=(width - 100, None),  # Leave margins
            font='Arial'
        )
        
        # Calculate scrolling (don't use opacity to avoid mask issues)
        text_height = txt_clip.h
        start_y = height  # Start below screen
        end_y = -text_height  # End above screen
        
        # Create position function for scrolling
        def make_frame_func(t):
            # Linear scrolling
            y_position = start_y - (scroll_speed * t)
            return txt_clip.get_frame(t)
        
        def position_func(t):
            y = start_y - (scroll_speed * t)
            # Keep position within reasonable bounds to avoid mask issues
            # Allow scrolling from bottom to top completely
            return ('center', y)
        
        # Set position and duration (MoviePy 2.x API)
        txt_clip = txt_clip.with_position(position_func)
        txt_clip = txt_clip.with_duration(duration)
        
        return txt_clip
    
    def create_video_with_text_and_narration(
        self,
        video_path: Path,
        text: str,
        output_path: Path,
        narration_lang: str = 'en',
        scroll_speed: float = 50,
        font_size: int = 28,
        video_volume: float = 0.1,
        use_markdown: bool = False
    ) -> bool:
        """
        Create final video with scrolling text and narration
        
        Args:
            video_path: Input video file path
            text: Text to display and narrate
            output_path: Output video file path
            narration_lang: Language for narration ('en', 'tr', etc.)
            scroll_speed: Text scrolling speed (pixels per second)
            font_size: Text font size
            video_volume: Original video volume (0.0-1.0, default 0.1 for low)
            use_markdown: Enable markdown formatting in text
        """
        try:
            logger.info("Creating video with text and narration...")
            
            # Load video
            video = VideoFileClip(str(video_path))
            video_duration = video.duration
            video_size = video.size
            video_height = video_size[1]
            
            # Calculate optimal font size based on video resolution
            # Formula: font_size = video_height / 30
            # Examples: 720p → 24px, 1080p → 36px, 1280p → 43px, 1440p → 48px
            calculated_font_size = max(20, min(60, int(video_height / 30)))
            
            # Override font_size parameter with calculated value
            font_size = calculated_font_size
            
            logger.info(f"Video loaded: {video_duration}s, {video_size}")
            logger.info(f"📏 Calculated font size: {font_size}px (based on {video_height}px height)")
            
            # Handle video audio based on volume setting
            if video.audio:
                if video_volume == 0.0:
                    # Completely mute video - remove audio track for efficiency
                    video = video.without_audio()
                    logger.info(f"🔇 Video audio muted (removed)")
                else:
                    # Lower video audio volume
                    # MoviePy 2.x: multiply audio frames by volume factor
                    def volume_modifier(get_frame, t):
                        return get_frame(t) * video_volume
                    
                    lowered_audio = video.audio.transform(volume_modifier)
                    video = video.set_audio(lowered_audio)
                    logger.info(f"🔉 Video audio volume set to {video_volume}")
            
            # Create narration (priority: Gemini Flash > Edge > Retry after 5 min)
            # Use .mp3 for Edge/Gemini TTS, .wav for Piper TTS
            narration_path = self.temp_dir / "narration.mp3"
            success = False
            max_retries = 3
            retry_count = 0
            
            # Clean text for TTS (remove markdown, asterisks, etc.)
            tts_text = self._clean_text_for_tts(text)
            
            while not success and retry_count < max_retries:
                if retry_count > 0:
                    logger.warning(f"⏳ TTS failed, waiting 5 minutes before retry {retry_count}/{max_retries}...")
                    import time
                    time.sleep(300)  # Wait 5 minutes
                    logger.info(f"🔄 Retrying TTS (attempt {retry_count + 1}/{max_retries})...")
                
                # 1. Try Gemini TTS first (highest priority)
                if self.use_gemini_tts and self.gemini_analyzer:
                    try:
                        logger.info("Creating narration with Gemini Flash TTS (primary)...")
                        # Run async Gemini TTS - ALWAYS English
                        import asyncio
                        import concurrent.futures
                        
                        # Check if event loop is running
                        try:
                            loop = asyncio.get_running_loop()
                            # If we're in an event loop, use run_in_executor
                            with concurrent.futures.ThreadPoolExecutor() as executor:
                                success = executor.submit(
                                    lambda: asyncio.run(self.gemini_analyzer.text_to_speech(
                                        text=tts_text,
                                        output_path=str(narration_path),
                                        language_code="en-US",
                                        speaking_rate=1.2  # %20 faster for <60s videos
                                    ))
                                ).result()
                        except RuntimeError:
                            # No event loop running, safe to use asyncio.run
                            success = asyncio.run(self.gemini_analyzer.text_to_speech(
                                text=tts_text,
                                output_path=str(narration_path),
                                language_code="en-US",
                                speaking_rate=1.2  # %20 faster for <60s videos
                            ))
                        
                        if success:
                            logger.info(f"✅ Narration created with Gemini Flash TTS")
                            break  # Success, exit retry loop
                        else:
                            logger.warning("⚠️  Gemini TTS failed, trying Edge TTS...")
                    except Exception as e:
                        logger.warning(f"⚠️  Gemini TTS error: {e}, trying Edge TTS...")
                        success = False
                
                # 2. Fallback to Edge TTS if Gemini failed
                if not success and self.use_edge_tts:
                    try:
                        logger.info("Creating narration with Edge TTS (fallback)...")
                        
                        # Select best voice for narration
                        voices = [
                            "en-US-GuyNeural",
                            "en-US-DavisNeural",
                            "en-US-TonyNeural",
                        ]
                        selected_voice = voices[0]
                        
                        # Run async Edge TTS
                        import asyncio
                        import concurrent.futures
                        
                        # Check if event loop is running
                        try:
                            loop = asyncio.get_running_loop()
                            with concurrent.futures.ThreadPoolExecutor() as executor:
                                success = executor.submit(
                                    lambda: asyncio.run(self.create_narration_edge(
                                        text=tts_text,
                                        output_path=narration_path,
                                        voice=selected_voice
                                    ))
                                ).result()
                        except RuntimeError:
                            success = asyncio.run(self.create_narration_edge(
                                text=tts_text,
                                output_path=narration_path,
                                voice=selected_voice
                            ))
                        
                        if success:
                            logger.info(f"✅ Narration created with Edge TTS ({selected_voice})")
                            break  # Success, exit retry loop
                        else:
                            logger.warning("⚠️  Edge TTS also failed, trying Bark TTS...")
                    except Exception as e:
                        logger.warning(f"⚠️  Edge TTS error: {e}, trying Bark TTS...")
                        success = False
                
                # 3. Fallback to Bark TTS if Edge also failed
                if not success and self.use_bark_tts:
                    try:
                        logger.info("Creating narration with Bark TTS (Suno AI local fallback)...")
                        bark_temp_path = self.temp_dir / "narration_bark_temp.wav"
                        success = self.create_narration_bark(
                            text=tts_text,
                            output_path=bark_temp_path
                        )
                        
                        if success:
                            # Speed up Bark narration by 20% using FFmpeg
                            logger.info("⚡ Speeding up Bark narration by 20% for <60s videos...")
                            import subprocess
                            speed_cmd = [
                                'ffmpeg', '-y', '-i', str(bark_temp_path),
                                '-filter:a', 'atempo=1.2',
                                str(narration_path)
                            ]
                            subprocess.run(speed_cmd, check=True, capture_output=True)
                            bark_temp_path.unlink()  # Clean up temp file
                            logger.info(f"✅ Narration created with Bark TTS (sped up 20%)")
                            break  # Success, exit retry loop
                        else:
                            logger.warning("⚠️  Bark TTS also failed")
                    except Exception as e:
                        logger.warning(f"⚠️  Bark TTS error: {e}")
                        success = False
                
                # If all failed, increment retry counter
                if not success:
                    retry_count += 1
            
            # Final check after all retries
            if not success:
                logger.error(f"❌ TTS failed after {max_retries} attempts (waited {max_retries * 5} minutes total)")
                logger.error("❌ Cannot proceed without TTS - stopping video creation")
                return None  # Stop here, don't continue
            
            if success:
                narration_audio = AudioFileClip(str(narration_path))
                logger.info(f"Narration duration: {narration_audio.duration:.1f}s")
            else:
                logger.warning("Narration creation failed, continuing without it")
                narration_audio = None
            
            # IMPORTANT: Calculate optimal scroll speed based on text and narration
            video_width = video_size[0]
            if narration_audio:
                # Use narration duration for perfect sync
                narration_duration = narration_audio.duration
                scroll_speed, target_duration = self._calculate_optimal_scroll_speed(
                    text=text,
                    video_width=video_width,
                    video_height=video_height,
                    narration_duration=narration_duration,
                    font_size=font_size
                )
                logger.info(f"✅ Target video duration: {target_duration:.1f}s (narration duration)")
            else:
                # No narration, estimate based on reading speed
                scroll_speed, target_duration = self._calculate_optimal_scroll_speed(
                    text=text,
                    video_width=video_width,
                    video_height=video_height,
                    narration_duration=None,
                    font_size=font_size
                )
                logger.info(f"Target video duration: {target_duration:.1f}s (scroll duration)")
            
            # Loop video if shorter than target duration
            if video_duration < target_duration:
                loop_count = int(target_duration / video_duration) + 1
                logger.info(f"Looping video {loop_count} times to match target duration")
                video = concatenate_videoclips([video] * loop_count)
                video = video.set_duration(target_duration)
                logger.info(f"Video looped to {target_duration:.1f}s")
            
            # Use video as base (text will be added with FFmpeg later)
            final_video = video
            
            # Add narration audio if available
            if narration_audio:
                # Ensure narration matches video duration
                narration_duration = narration_audio.duration
                if narration_duration > target_duration:
                    # Trim narration to match video (shouldn't happen but handle it)
                    logger.warning(f"Narration longer than video, trimming: {narration_duration:.1f}s -> {target_duration:.1f}s")
                    narration_audio = narration_audio.set_duration(target_duration)
                elif narration_duration < target_duration:
                    # This shouldn't happen with our logic, but handle it just in case
                    logger.warning(f"Narration shorter than video, this shouldn't happen")
                    # Keep narration as is, video will continue after narration ends
                
                # Mix with original audio if exists
                if video.audio:
                    final_audio = CompositeAudioClip([video.audio, narration_audio])
                    final_video = final_video.set_audio(final_audio)
                else:
                    final_video = final_video.set_audio(narration_audio)
            
            # Write video without text first
            temp_output = self.temp_dir / "temp_no_text.mp4"
            logger.info(f"Writing video to {temp_output}")
            final_video.write_videofile(
                str(temp_output),
                codec='libx264',
                audio_codec='aac',
                fps=24,
                preset='medium'
            )
            
            # Add scrolling text with FFmpeg
            logger.info("Adding scrolling text overlay with FFmpeg...")
            if not self.add_scrolling_text_ffmpeg(
                video_path=temp_output,
                text=text,
                output_path=output_path,
                video_size=video_size,
                duration=target_duration,
                font_size=font_size,
                scroll_speed=scroll_speed,
                use_markdown=use_markdown
            ):
                # If FFmpeg fails, use video without text
                logger.warning("FFmpeg text overlay failed, using video without text")
                import shutil
                shutil.copy(temp_output, output_path)
            
            # Cleanup
            video.close()
            if narration_audio:
                narration_audio.close()
            
            logger.info(f"✅ Video created successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating video: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _parse_simple_markdown(self, text: str) -> list:
        """
        Parse simple markdown formatting (**bold**, *italic*)
        Returns list of (text, style) tuples where style is 'bold', 'italic', or 'normal'
        """
        import re
        
        segments = []
        pos = 0
        
        # Pattern: **bold** or *italic*
        pattern = r'(\*\*([^\*]+)\*\*|\*([^\*]+)\*)'
        
        for match in re.finditer(pattern, text):
            # Add normal text before match
            if match.start() > pos:
                segments.append((text[pos:match.start()], 'normal'))
            
            # Add styled text
            if match.group(2):  # **bold**
                segments.append((match.group(2), 'bold'))
            elif match.group(3):  # *italic*
                segments.append((match.group(3), 'italic'))
            
            pos = match.end()
        
        # Add remaining normal text
        if pos < len(text):
            segments.append((text[pos:], 'normal'))
        
        return segments if segments else [(text, 'normal')]
    
    def _create_text_image_with_markdown(self, text: str, width: int, font_size: int = 48,
                                          use_markdown: bool = True) -> Optional[Path]:
        """
        Create an image with text supporting markdown formatting using PIL
        
        Args:
            text: Text with markdown formatting
            width: Image width
            font_size: Base font size
            use_markdown: Enable markdown parsing
        
        Returns:
            Path to created image or None
        """
        try:
            # Try to load fonts
            try:
                font_regular = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", font_size)
                font_bold = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", font_size)
            except:
                # Fallback to default font
                logger.warning("Could not load custom fonts, using default")
                font_regular = ImageFont.load_default()
                font_bold = font_regular
            
            # Word wrap and parse markdown
            padding = 40
            max_text_width = width - (padding * 2)
            
            lines = []
            current_line = []
            current_width = 0
            
            if use_markdown:
                segments = self._parse_simple_markdown(text)
            else:
                segments = [(text, 'normal')]
            
            for segment_text, style in segments:
                words = segment_text.split()
                font = font_bold if style == 'bold' else font_regular
                
                for word in words:
                    word_width = font.getbbox(word + ' ')[2]
                    
                    if current_width + word_width > max_text_width and current_line:
                        lines.append(current_line)
                        current_line = [(word + ' ', style)]
                        current_width = word_width
                    else:
                        current_line.append((word + ' ', style))
                        current_width += word_width
            
            if current_line:
                lines.append(current_line)
            
            # Calculate image height
            line_height = int(font_size * 1.5)
            image_height = len(lines) * line_height + padding * 2
            
            # Create image
            image = Image.new('RGBA', (width, image_height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # Draw text with styles
            y = padding
            for line in lines:
                x = padding
                for word, style in line:
                    font = font_bold if style == 'bold' else font_regular
                    
                    # Draw text with border (stroke)
                    for offset_x in [-3, 0, 3]:
                        for offset_y in [-3, 0, 3]:
                            if offset_x != 0 or offset_y != 0:
                                draw.text((x + offset_x, y + offset_y), word, 
                                         font=font, fill=(0, 0, 0, 255))
                    
                    # Draw main text
                    draw.text((x, y), word, font=font, fill=(255, 255, 255, 255))
                    
                    x += font.getbbox(word)[2]
                
                y += line_height
            
            # Save image
            image_path = self.temp_dir / "scrolling_text_rendered.png"
            image.save(image_path)
            
            logger.info(f"✅ Created markdown-formatted text image: {image_path}")
            logger.info(f"   Size: {width}x{image_height}px, Lines: {len(lines)}")
            
            return image_path
            
        except Exception as e:
            logger.error(f"Error creating text image: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def add_scrolling_text_ffmpeg(self, video_path: Path, text: str, output_path: Path,
                                   video_size: tuple, duration: float,
                                   font_size: int = 28, scroll_speed: float = 50,
                                   use_markdown: bool = False) -> bool:
        """
        Add scrolling text to video using FFmpeg drawtext filter with text file
        This avoids command line length limits and escape character issues
        
        Args:
            video_path: Input video path
            text: Text to display
            output_path: Output video path
            video_size: (width, height)
            duration: Video duration
            font_size: Font size
            scroll_speed: Scrolling speed (pixels per second)
        """
        try:
            width, height = video_size
            
            # If markdown is enabled, use PIL-rendered image approach
            if use_markdown:
                logger.info("🎨 Using PIL with markdown formatting")
                text_image_path = self._create_text_image_with_markdown(text, width, font_size, use_markdown=True)
                
                if not text_image_path:
                    logger.warning("Failed to create markdown image, falling back to plain text")
                    use_markdown = False
                else:
                    # Get image dimensions
                    with Image.open(text_image_path) as img:
                        img_width, img_height = img.size
                    
                    # Calculate scroll parameters
                    start_y = height
                    end_y = -img_height
                    scroll_distance = start_y - end_y
                    
                    # Adjust scroll speed if needed
                    if duration > 0:
                        calculated_speed = scroll_distance / duration
                        logger.info(f"📐 Image scroll: {img_width}x{img_height}px, speed: {calculated_speed:.1f}px/s")
                    else:
                        calculated_speed = scroll_speed
                    
                    # Use FFmpeg overlay filter with scrolling
                    ffmpeg_cmd = [
                        'ffmpeg',
                        '-i', str(video_path),
                        '-i', str(text_image_path),
                        '-filter_complex',
                        f"[1:v]format=rgba[text];[0:v][text]overlay=x=0:y={start_y}-{calculated_speed}*t[out]",
                        '-map', '[out]',
                        '-codec:a', 'copy',
                        '-y',
                        str(output_path)
                    ]
                    
                    logger.info("🎬 Running FFmpeg with markdown-formatted image overlay...")
                    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        logger.info(f"✅ Markdown text overlay added successfully")
                        return True
                    else:
                        logger.error(f"FFmpeg error: {result.stderr}")
                        logger.warning("Falling back to plain text mode")
                        use_markdown = False
            
            # Plain text mode (original implementation)
            if not use_markdown:
                # Calculate max text width with minimal padding
                padding = 30
                max_text_width = width - (padding * 2)
                chars_per_line = int(max_text_width / (font_size * 0.6))
                
                # Word wrap text
                words = text.split()
                lines = []
                current_line = []
                current_length = 0
                
                for word in words:
                    word_length = len(word) + 1
                    
                    if word_length > chars_per_line:
                        if current_line:
                            lines.append(' '.join(current_line))
                            current_line = []
                            current_length = 0
                        lines.append(word)
                    elif current_length + word_length > chars_per_line and current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                        current_length = word_length
                    else:
                        current_line.append(word)
                        current_length += word_length
                
                if current_line:
                    lines.append(' '.join(current_line))
                
                logger.info(f"📝 Text wrapping: {len(text)} chars → {len(words)} words → {len(lines)} lines")
                logger.info(f"   Chars per line: {chars_per_line}, Font size: {font_size}px, Video width: {width}px")
                
                # Write wrapped text to file (NO ESCAPING NEEDED!)
                text_file = self.temp_dir / "scrolling_text.txt"
                with open(text_file, 'w', encoding='utf-8') as f:
                    for line in lines:
                        f.write(line + '\n')
                
                logger.info(f"💾 Wrote {len(lines)} lines to text file: {text_file}")
                
                # Calculate scroll parameters - match the calculation in _calculate_optimal_scroll_speed
                start_y = height
                line_height = int(font_size * 1.2)  # FFmpeg's default line height (~1.2x font size)
                text_box_height = len(lines) * line_height
                
                logger.info(f"📹 FFmpeg scroll parameters:")
                logger.info(f"   Lines: {len(lines)}, Line height: {line_height}px, Text height: {text_box_height}px")
                logger.info(f"   Start Y: {start_y}px, Scroll speed: {scroll_speed:.1f}px/s")
                logger.info(f"   Duration: {duration:.1f}s, Final Y: {start_y - (scroll_speed * duration):.1f}px")
                
                # Use textfile parameter - much simpler and no escape issues!
                # Single drawtext filter for all text with newline support
                # NOTE: line_h parameter not supported in some FFmpeg versions, using default line spacing
                drawtext_filter = (
                    f"drawtext="
                    f"textfile='{text_file}':"
                    f"fontsize={font_size}:"
                    f"fontcolor=white:"
                    f"borderw=3:"
                    f"bordercolor=black:"
                    f"x=(w-text_w)/2:"
                    f"y={start_y}-{scroll_speed}*t:"
                    f"fontfile=/System/Library/Fonts/Supplemental/Arial.ttf"
                )
                
                # Add header overlay
                header_text = "by roll.wiki . video from pexels, article from wikipedia."
                # Minimal escaping for header only
                header_escaped = header_text.replace("'", "'\\''").replace(":", "\\:")
                header_filter = (
                    f"drawtext="
                    f"text='{header_escaped}':"
                    f"fontsize=14:"
                    f"fontcolor=white:"
                    f"borderw=1:"
                    f"bordercolor=black:"
                    f"x=(w-text_w)/2:"
                    f"y=15:"
                    f"fontfile=/System/Library/Fonts/Supplemental/Arial.ttf"
                )
                
                # Combine filters
                combined_filter = f"{drawtext_filter},{header_filter}"
                
                # FFmpeg command
                cmd = [
                    'ffmpeg',
                    '-i', str(video_path),
                    '-vf', combined_filter,
                    '-codec:a', 'copy',
                    '-y',
                    str(output_path)
                ]
                
                logger.info("Running FFmpeg with text file for scrolling text...")
                logger.info(f"FFmpeg filter length: {len(combined_filter)} chars (much shorter!)")
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    logger.info("✅ Scrolling text added successfully")
                    return True
                else:
                    logger.error(f"FFmpeg error: {result.stderr}")
                    logger.error(f"FFmpeg command: {' '.join(cmd)}")
                    return False
                
        except Exception as e:
            logger.error(f"Error adding scrolling text: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_video_from_pexels(
        self,
        search_query: str,
        text: str,
        output_filename: str,
        narration_lang: str = 'en',
        scroll_speed: float = 50,
        font_size: int = 40,
        orientation: str = 'portrait',
        video_volume: float = 0.1,
        use_markdown: bool = False,
        category: str = None
    ) -> Optional[Path]:
        """
        Complete workflow: Search Pexels → Download → Create video with text + narration
        
        Args:
            search_query: Pexels search query
            text: Text to display and narrate (supports **bold** and *italic* markdown)
            output_filename: Output video filename
            narration_lang: Language for narration
            scroll_speed: Text scrolling speed
            font_size: Text font size
            orientation: Video orientation ('portrait' for Reels/Shorts, 'landscape', 'square')
            video_volume: Original video volume (0.0-1.0, default 0.1)
            use_markdown: Enable markdown formatting (**bold**, *italic*)
            
        Returns:
            Path to created video or None
        """
        # Clean search query - remove trend counts (e.g., "George W. Bush13K" -> "George W. Bush")
        import re
        cleaned_query = re.sub(r'\d+[KkMm]?$', '', search_query).strip()
        if cleaned_query != search_query:
            logger.info(f"🧹 Cleaned search query: '{search_query}' -> '{cleaned_query}'")
        
        # Search video with Gemini keyword suggestions
        video_info = None
        search_keywords = []  # Will be filled by Gemini
        
        # Get alternative keywords from Gemini if available - PRIORITIZE GEMINI
        if self.gemini_analyzer:
            try:
                import asyncio
                # Check if event loop is running
                try:
                    loop = asyncio.get_running_loop()
                    # If we're in an event loop, use run_in_executor
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        keywords = executor.submit(
                            lambda: asyncio.run(self.gemini_analyzer.get_video_search_keywords(cleaned_query, max_keywords=5))
                        ).result()
                except RuntimeError:
                    # No event loop running, safe to use asyncio.run
                    keywords = asyncio.run(self.gemini_analyzer.get_video_search_keywords(cleaned_query, max_keywords=5))
                
                search_keywords = keywords
                logger.info(f"🎬 Trying {len(search_keywords)} keywords from Gemini: {search_keywords}")
            except Exception as e:
                logger.warning(f"Could not get Gemini keywords: {e}")
                # Fallback to cleaned query only if Gemini fails
                search_keywords = [cleaned_query]
        else:
            # No Gemini, use cleaned query
            search_keywords = [cleaned_query]
        
        # Try each keyword until we find a video
        for i, keyword in enumerate(search_keywords, 1):
            logger.info(f"🔍 Trying keyword {i}/{len(search_keywords)}: '{keyword}'")
            video_info = self.search_pexels_video(keyword, orientation=orientation)
            if video_info:
                logger.info(f"✅ Found video with keyword: '{keyword}'")
                break
            else:
                logger.warning(f"❌ No video found for: '{keyword}'")
        
        if not video_info:
            logger.error(f"💔 No video found after trying all {len(search_keywords)} keywords!")
            return None
        
        # Download video
        temp_video_path = self.temp_dir / f"temp_{video_info['id']}.mp4"
        if not self.download_video(video_info['url'], temp_video_path):
            logger.error("Video download failed!")
            return None
        
        # Create final video with category folder
        if category:
            # Create category folder if it doesn't exist
            category_folder = self.output_dir / category.replace(' ', '_').replace('/', '_')
            category_folder.mkdir(parents=True, exist_ok=True)
            output_path = category_folder / output_filename
            logger.info(f"📁 Saving video to category folder: {category}/{output_filename}")
        else:
            output_path = self.output_dir / output_filename
        
        success = self.create_video_with_text_and_narration(
            video_path=temp_video_path,
            text=text,
            output_path=output_path,
            narration_lang=narration_lang,
            scroll_speed=scroll_speed,
            font_size=font_size,
            video_volume=video_volume,
            use_markdown=use_markdown
        )
        
        # Cleanup temp video
        if temp_video_path.exists():
            temp_video_path.unlink()
        
        return output_path if success else None
    
    async def create_video_with_gemini_tts(
        self,
        search_query: str,
        summary_text: str,
        output_filename: str = "output_shorts.mp4",
        voice_name: str = "Charon",
        orientation: str = "portrait"
    ) -> Optional[Path]:
        """
        Create video with Gemini TTS + scrolling text + looping Pexels video
        
        Workflow:
        1. Generate TTS audio with Gemini (Charon voice)
        2. Download Pexels video
        3. Create scrolling text overlay
        4. Loop video to match TTS duration
        5. Combine: looping video + scrolling text + TTS audio
        
        Args:
            search_query: Search term for Pexels video
            summary_text: roll.wiki summary text to display and narrate
            output_filename: Output video filename
            voice_name: Gemini TTS voice (default: Charon)
            orientation: Video orientation (portrait/landscape)
            
        Returns:
            Path to created video or None if failed
        """
        try:
            logger.info(f"🎬 Creating video: {search_query}")
            logger.info(f"   Voice: Gemini TTS ({voice_name})")
            logger.info(f"   Summary length: {len(summary_text)} chars")
            
            # Step 1: Generate TTS with Gemini
            logger.info("🎤 Step 1: Generating TTS with Gemini...")
            audio_path = self.temp_dir / f"tts_{search_query.replace(' ', '_')}.mp3"
            
            if not self.gemini_analyzer:
                logger.error("Gemini analyzer not initialized")
                return None
            
            # Generate TTS using Gemini
            # Charon is a valid Gemini TTS voice (lowercase)
            success = await self.gemini_analyzer.text_to_speech(
                text=summary_text,
                output_path=str(audio_path),
                language_code="en-US",
                voice_name=voice_name.lower(),  # Gemini voices are lowercase
                speaking_rate=1.0
            )
            
            if not success or not audio_path.exists():
                logger.error("Failed to generate Gemini TTS")
                return None
                
            logger.info(f"✅ TTS generated: {audio_path}")
            
            # Get TTS duration
            audio_clip = AudioFileClip(str(audio_path))
            tts_duration = audio_clip.duration
            logger.info(f"   TTS duration: {tts_duration:.1f} seconds")
            audio_clip.close()
            
            # Step 2: Search and download Pexels video
            logger.info("📹 Step 2: Searching Pexels video...")
            pexels_video_info = self.search_pexels_video(
                query=search_query,
                orientation=orientation,
                size="medium"
            )
            
            if not pexels_video_info:
                logger.warning(f"No Pexels video found for '{search_query}', trying generic search...")
                pexels_video_info = self.search_pexels_video(
                    query="trending",
                    orientation=orientation,
                    size="medium"
                )
            
            if not pexels_video_info:
                logger.error("Failed to find Pexels video")
                return None
            
            logger.info(f"✅ Found Pexels video: {pexels_video_info['url']}")
            
            # Download the video
            pexels_video_path = self.temp_dir / f"pexels_{search_query.replace(' ', '_')}.mp4"
            download_success = self.download_video(pexels_video_info['url'], pexels_video_path)
            
            if not download_success or not pexels_video_path.exists():
                logger.error("Failed to download Pexels video")
                return None
                
            logger.info(f"✅ Pexels video downloaded: {pexels_video_path}")
            
            # Step 3: Loop video to match TTS duration
            logger.info(f"🔁 Step 3: Looping video to match TTS ({tts_duration:.1f}s)...")
            video_clip = VideoFileClip(str(pexels_video_path))
            video_duration = video_clip.duration
            
            # Calculate how many loops needed
            loops_needed = int(np.ceil(tts_duration / video_duration))
            logger.info(f"   Video duration: {video_duration:.1f}s, loops needed: {loops_needed}")
            
            # Create looped video
            if loops_needed > 1:
                looped_video = concatenate_videoclips([video_clip] * loops_needed)
                looped_video = looped_video.subclipped(0, tts_duration)
            else:
                looped_video = video_clip.subclipped(0, min(tts_duration, video_duration))
            
            logger.info(f"✅ Looped video created: {looped_video.duration:.1f}s")
            
            # Step 4: Create scrolling text overlay
            logger.info("📝 Step 4: Creating scrolling text overlay...")
            
            # Get video dimensions
            video_width, video_height = looped_video.size
            logger.info(f"   Video size: {video_width}x{video_height}")
            
            # Create scrolling text with configurable settings
            text_width = video_width - (self.padding_horizontal * 2)
            txt_clip = TextClip(
                text=summary_text,
                font='Arial',
                font_size=self.font_size,
                color='white',
                bg_color='transparent',
                stroke_color='black',
                stroke_width=self.stroke_width,
                size=(text_width, None),
                method='caption'
            )
            
            # Calculate scroll distance and speed
            txt_height = txt_clip.size[1]
            scroll_distance = video_height + txt_height
            scroll_duration = tts_duration
            
            # Position function for scrolling
            def scroll_position(t):
                progress = t / scroll_duration
                y = video_height - (progress * scroll_distance)
                return (self.padding_horizontal, y)
            
            txt_clip = txt_clip.set_position(scroll_position)
            txt_clip = txt_clip.set_duration(tts_duration)
            
            logger.info(f"✅ Scrolling text created")
            
            # Step 5: Composite video + text + audio
            logger.info("🎭 Step 5: Combining video + text + audio...")
            
            final_video = CompositeVideoClip([looped_video, txt_clip], size=looped_video.size)
            final_video = final_video.set_duration(tts_duration)
            
            # Add TTS audio
            final_audio = AudioFileClip(str(audio_path))
            final_video = final_video.set_audio(final_audio)
            
            # Output path
            output_path = self.output_dir / output_filename
            logger.info(f"💾 Saving video to: {output_path}")
            
            # Write video file
            final_video.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                fps=30,
                preset='medium',
                threads=4,
                write_logfile=False,
                logger=None  # Suppress moviepy logging
            )
            
            # Cleanup
            video_clip.close()
            looped_video.close()
            txt_clip.close()
            final_audio.close()
            final_video.close()
            
            logger.info(f"✅ Video created successfully: {output_path}")
            return output_path
            
        except TTSQuotaExceeded:
            # Re-raise TTS quota exception to be handled by caller
            raise
        except Exception as e:
            logger.error(f"Error creating video with Gemini TTS: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None


def main():
    """Example usage"""
    from dotenv import load_dotenv
    load_dotenv()
    
    # Example text (you can use Wikipedia summary)
    text = """
    NASA (National Aeronautics and Space Administration) is an independent agency 
    of the U.S. federal government responsible for the civil space program, 
    aeronautics research, and space research. NASA was established in 1958, 
    succeeding the National Advisory Committee for Aeronautics (NACA), 
    to give the U.S. space development effort a distinctly civilian orientation.
    """
    
    creator = VideoCreator()
    
    result = creator.create_video_from_pexels(
        search_query="space nasa rocket",
        text=text.strip(),
        output_filename="nasa_shorts.mp4",
        narration_lang='en',
        scroll_speed=80,  # Faster for vertical
        font_size=45,  # Bigger for mobile
        orientation='portrait',  # Vertical for Reels/Shorts
        video_volume=0.1  # Low video volume
    )
    
    if result:
        print(f"\n✅ Video created successfully: {result}")
    else:
        print("\n❌ Video creation failed")


if __name__ == "__main__":
    main()
