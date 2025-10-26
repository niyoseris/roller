#!/usr/bin/env python3
"""
Video Creator - Pexels video + scrolling text + narration
"""

import os
import requests
from pathlib import Path
from typing import Optional
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip, ImageClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from gtts import gTTS
import edge_tts
import asyncio
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoCreator:
    """Creates videos with scrolling text and narration"""
    
    def __init__(self, pexels_api_key: Optional[str] = None):
        """
        Initialize VideoCreator
        
        Args:
            pexels_api_key: Pexels API key (get from https://www.pexels.com/api/)
        """
        self.pexels_api_key = pexels_api_key or os.getenv('PEXELS_API_KEY')
        self.output_dir = Path('output_videos')
        self.output_dir.mkdir(exist_ok=True)
        
        self.temp_dir = Path('temp_videos')
        self.temp_dir.mkdir(exist_ok=True)
    
    def search_pexels_video(self, query: str, orientation: str = "portrait", 
                           size: str = "medium") -> Optional[dict]:
        """
        Search for a video on Pexels
        
        Args:
            query: Search query (e.g., "technology", "nature")
            orientation: "portrait" (default, for Reels/Shorts), "landscape", or "square"
            size: "large", "medium", or "small"
            
        Returns:
            Video info dict or None
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
            "per_page": 1
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('videos') and len(data['videos']) > 0:
                video = data['videos'][0]
                logger.info(f"Found video: {video.get('url')}")
                
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
    
    async def create_narration_edge(self, text: str, output_path: Path, voice: str = 'en-US-AriaNeural') -> bool:
        """
        Create high-quality narration using Edge TTS (Microsoft, free)
        
        Args:
            text: Text to convert to speech
            output_path: Output audio file path
            voice: Voice name (en-US-AriaNeural, tr-TR-AhmetNeural, etc.)
                   Full list: https://speech.microsoft.com/portal/voicegallery
        """
        try:
            logger.info(f"Creating high-quality narration with Edge TTS ({voice})...")
            logger.info(f"Text preview: {text[:80]}...")
            
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(output_path))
            
            logger.info(f"✅ High-quality narration saved: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Edge TTS failed: {e}")
            logger.info("Falling back to gTTS...")
            return self.create_narration_gtts(text, output_path)
    
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
    
    def create_scrolling_text_clip(self, text: str, video_size: tuple, 
                                   duration: float, font_size: int = 40,
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
        font_size: int = 40,
        video_volume: float = 0.1
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
        """
        try:
            logger.info("Creating video with text and narration...")
            
            # Load video
            video = VideoFileClip(str(video_path))
            video_duration = video.duration
            video_size = video.size
            video_height = video_size[1]
            
            logger.info(f"Video loaded: {video_duration}s, {video_size}")
            
            # Calculate text scroll duration
            # Text needs to scroll from bottom to completely off screen at top
            lines = text.split('\n')
            line_height = font_size + 15
            text_box_height = len(lines) * line_height
            start_y = video_height - 200  # Start position (200px from bottom)
            
            # Total distance to scroll = start_y + text_box_height
            # Time = distance / speed
            scroll_distance = start_y + text_box_height
            scroll_duration = scroll_distance / scroll_speed
            
            logger.info(f"Text scroll: {len(lines)} lines, {text_box_height}px height")
            logger.info(f"Scroll duration: {scroll_duration:.1f}s (distance: {scroll_distance}px at {scroll_speed}px/s)")
            
            # Lower video audio volume  
            if video.audio:
                # MoviePy 2.x: multiply audio frames by volume factor
                def volume_modifier(get_frame, t):
                    return get_frame(t) * video_volume
                
                lowered_audio = video.audio.transform(volume_modifier)
                video = video.with_audio(lowered_audio)
                logger.info(f"Video audio volume set to {video_volume}")
            
            # Create narration with gTTS (simple and reliable)
            narration_path = self.temp_dir / "narration.mp3"
            
            # Use gTTS for narration (works in sync context)
            try:
                tts = gTTS(text=text, lang=narration_lang, slow=False)
                tts.save(str(narration_path))
                success = True
                logger.info(f"Narration created with gTTS ({narration_lang})")
            except Exception as e:
                logger.error(f"gTTS error: {e}")
                success = False
            
            if success:
                narration_audio = AudioFileClip(str(narration_path))
                logger.info(f"Narration duration: {narration_audio.duration:.1f}s")
            else:
                logger.warning("Narration creation failed, continuing without it")
                narration_audio = None
            
            # Use scroll duration as target duration (text must scroll completely off)
            target_duration = scroll_duration
            logger.info(f"Target video duration: {target_duration:.1f}s (scroll duration)")
            
            # Loop video if shorter than scroll duration
            if video_duration < target_duration:
                loop_count = int(target_duration / video_duration) + 1
                logger.info(f"Looping video {loop_count} times to match scroll duration")
                from moviepy.editor import concatenate_videoclips
                video = concatenate_videoclips([video] * loop_count)
                video = video.with_duration(target_duration)
                logger.info(f"Video looped to {target_duration:.1f}s")
            
            # Use video as base (text will be added with FFmpeg later)
            final_video = video
            
            # Add narration audio if available (loop it if shorter than video)
            if narration_audio:
                narration_duration = narration_audio.duration
                if narration_duration < target_duration:
                    # Loop narration to match video duration
                    from moviepy.editor import concatenate_audioclips
                    loop_count = int(target_duration / narration_duration) + 1
                    narration_audio = concatenate_audioclips([narration_audio] * loop_count)
                    narration_audio = narration_audio.with_duration(target_duration)
                    logger.info(f"Narration looped to match video duration")
                
                # Mix with original audio if exists
                if video.audio:
                    from moviepy.editor import CompositeAudioClip
                    final_audio = CompositeAudioClip([video.audio, narration_audio])
                    final_video = final_video.with_audio(final_audio)
                else:
                    final_video = final_video.with_audio(narration_audio)
            
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
                scroll_speed=scroll_speed
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
    
    def add_scrolling_text_ffmpeg(self, video_path: Path, text: str, output_path: Path,
                                   video_size: tuple, duration: float,
                                   font_size: int = 40, scroll_speed: float = 50) -> bool:
        """
        Add scrolling text to video using FFmpeg drawtext filter
        
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
            
            # Calculate max text width with minimal padding (maximize text width)
            padding = 30  # 15px each side - minimal safe margin
            max_text_width = width - (padding * 2)
            
            # Word wrap text to fit within max width
            # Maximize words per line - fit as much as possible in video width
            # For 45px font on 720px width: ~25-28 chars per line (5-8 words)
            chars_per_line = int(max_text_width / (font_size * 0.6))
            
            # Wrap text to multiple lines
            words = text.split()
            lines = []
            current_line = []
            current_length = 0
            
            for word in words:
                word_length = len(word) + 1  # +1 for space
                if current_length + word_length > chars_per_line and current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = word_length
                else:
                    current_line.append(word)
                    current_length += word_length
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Limit lines for display
            lines = lines[:80]  # Max 80 lines
            
            # Calculate scroll parameters
            start_y = height  # Start from bottom
            scroll_pixels_per_sec = scroll_speed
            
            # Calculate text box dimensions
            line_height = font_size + 15  # Font size + line spacing
            text_box_height = len(lines) * line_height
            
            # Create multiple drawtext filters (one per line) for proper multi-line
            # All lines scrolling together
            drawtext_filters = []
            
            for i, line in enumerate(lines):
                # Escape text for FFmpeg
                line_escaped = line.replace("'", "'\\''").replace(":", "\\:").replace("%", "\\%")
                
                # Calculate y position for this line
                # base_y = start position - (scroll_speed * t) + (line_number * line_height)
                line_offset = i * line_height
                
                # Create drawtext filter for this line
                filter_text = (
                    f"drawtext="
                    f"text='{line_escaped}':"
                    f"fontsize={font_size}:"
                    f"fontcolor=white:"
                    f"borderw=3:"
                    f"bordercolor=black:"
                    f"x=(w-text_w)/2:"  # Center each line
                    f"y={start_y}+{line_offset}-{scroll_pixels_per_sec}*t:"
                    f"fontfile=/System/Library/Fonts/Supplemental/Arial.ttf"
                )
                drawtext_filters.append(filter_text)
            
            # Combine all drawtext filters with comma
            drawtext_filter = ','.join(drawtext_filters)
            
            # FFmpeg command
            cmd = [
                'ffmpeg',
                '-i', str(video_path),
                '-vf', drawtext_filter,
                '-codec:a', 'copy',  # Copy audio without re-encoding
                '-y',  # Overwrite output
                str(output_path)
            ]
            
            logger.info("Running FFmpeg for scrolling text...")
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
                return False
                
        except Exception as e:
            logger.error(f"Error adding scrolling text: {e}")
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
        video_volume: float = 0.1
    ) -> Optional[Path]:
        """
        Complete workflow: Search Pexels → Download → Create video with text + narration
        
        Args:
            search_query: Pexels search query
            text: Text to display and narrate
            output_filename: Output video filename
            narration_lang: Language for narration
            scroll_speed: Text scrolling speed
            font_size: Text font size
            orientation: Video orientation ('portrait' for Reels/Shorts, 'landscape', 'square')
            video_volume: Original video volume (0.0-1.0, default 0.1)
            
        Returns:
            Path to created video or None
        """
        # Search video
        video_info = self.search_pexels_video(search_query, orientation=orientation)
        if not video_info:
            logger.error("No video found!")
            return None
        
        # Download video
        temp_video_path = self.temp_dir / f"temp_{video_info['id']}.mp4"
        if not self.download_video(video_info['url'], temp_video_path):
            logger.error("Video download failed!")
            return None
        
        # Create final video
        output_path = self.output_dir / output_filename
        success = self.create_video_with_text_and_narration(
            video_path=temp_video_path,
            text=text,
            output_path=output_path,
            narration_lang=narration_lang,
            scroll_speed=scroll_speed,
            font_size=font_size,
            video_volume=video_volume
        )
        
        # Cleanup temp video
        if temp_video_path.exists():
            temp_video_path.unlink()
        
        return output_path if success else None


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
