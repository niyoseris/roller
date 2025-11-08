"""
Google Gemini API Integration
Provides visual analysis and text-to-speech functionality
"""

import os
import logging
import base64
import json
from typing import Optional
import aiohttp
from dotenv import load_dotenv
from exceptions import TTSQuotaExceeded

load_dotenv()

logger = logging.getLogger(__name__)


class GeminiAnalyzer:
    """Google Gemini API for vision and TTS"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found in .env file")
        
        # Gemini API endpoints - use gemini-2.5-flash (fast, supports vision & text)
        self.vision_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
        self.tts_api_url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={self.api_key}"
        
    async def is_available(self) -> bool:
        """Check if Gemini API is available"""
        return bool(self.api_key)
    
    async def analyze_screenshot(self, image_path: str, prompt: str = None) -> Optional[str]:
        """
        Analyze a screenshot using Gemini Vision API
        
        Args:
            image_path: Path to the image file
            prompt: Custom prompt for analysis (default: trend analysis)
        
        Returns:
            Analysis text or None if failed
        """
        if not await self.is_available():
            logger.error("Gemini API key not configured")
            return None
        
        try:
            # Read and encode image
            with open(image_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Default prompt for trend analysis
            if not prompt:
                prompt = """Analyze this Google Trends screenshot and provide a detailed analysis:
                
1. List all trending topics visible in the image
2. Identify any patterns or categories (politics, entertainment, sports, etc.)
3. Note any particularly significant trends
4. Suggest which topics would make good content

Provide a clear, structured analysis in English."""
            
            # Prepare request payload
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": image_data
                            }
                        }
                    ]
                }]
            }
            
            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.vision_api_url,
                    json=payload,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        # Extract text from response
                        candidates = result.get('candidates', [])
                        if candidates:
                            content = candidates[0].get('content', {})
                            parts = content.get('parts', [])
                            if parts:
                                analysis = parts[0].get('text', '')
                                logger.info(f"Gemini Vision analysis successful ({len(analysis)} chars)")
                                return analysis
                    else:
                        error_text = await response.text()
                        logger.error(f"Gemini Vision API error {response.status}: {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error analyzing screenshot with Gemini: {e}")
            return None
    
    async def analyze_text(self, text_prompt: str) -> Optional[str]:
        """
        Analyze text using Gemini API (text-only, no vision)
        
        Args:
            text_prompt: Text prompt for analysis
        
        Returns:
            Analysis result or None if failed
        """
        if not await self.is_available():
            logger.error("Gemini API key not configured")
            return None
        
        try:
            # Prepare request payload for text-only analysis
            payload = {
                "contents": [{
                    "parts": [
                        {"text": text_prompt}
                    ]
                }]
            }
            
            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.vision_api_url,  # Same endpoint works for text-only
                    json=payload,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        # Extract text from response
                        candidates = result.get('candidates', [])
                        if candidates:
                            content = candidates[0].get('content', {})
                            parts = content.get('parts', [])
                            if parts:
                                analysis = parts[0].get('text', '')
                                logger.info(f"Gemini text analysis successful ({len(analysis)} chars)")
                                return analysis
                    else:
                        error_text = await response.text()
                        logger.error(f"Gemini text API error {response.status}: {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error analyzing text with Gemini: {e}")
            return None
    
    async def text_to_speech(
        self, 
        text: str, 
        output_path: str,
        language_code: str = "en-US",
        voice_name: str = "Charon",
        speaking_rate: float = 1.0
    ) -> bool:
        """
        Convert text to speech using Gemini TTS with Charon voice
        
        Args:
            text: Text to convert
            output_path: Where to save the audio file
            language_code: Language code (not used for Gemini TTS)
            voice_name: Gemini voice name (default: "Charon")
            speaking_rate: Speech speed (not used for Gemini TTS)
        
        Returns:
            True if successful, False otherwise
        """
        if not await self.is_available():
            logger.error("Gemini API key not configured")
            return False
        
        try:
            from google import genai
            from google.genai import types
            import struct
            import mimetypes
            
            # Initialize Gemini client
            client = genai.Client(api_key=self.api_key)
            
            # Gemini TTS model
            model = "gemini-2.5-flash-preview-tts"
            
            # Create content with text
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=text)],
                ),
            ]
            
            # Configure with Charon voice
            generate_content_config = types.GenerateContentConfig(
                temperature=1,
                response_modalities=["audio"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice_name
                        )
                    )
                ),
            )
            
            # Generate audio
            audio_chunks = []
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ):
                if (
                    chunk.candidates is None
                    or chunk.candidates[0].content is None
                    or chunk.candidates[0].content.parts is None
                ):
                    continue
                    
                if chunk.candidates[0].content.parts[0].inline_data and chunk.candidates[0].content.parts[0].inline_data.data:
                    inline_data = chunk.candidates[0].content.parts[0].inline_data
                    data_buffer = inline_data.data
                    
                    # Convert to WAV if needed
                    file_extension = mimetypes.guess_extension(inline_data.mime_type)
                    if file_extension is None or file_extension != ".mp3":
                        file_extension = ".wav"
                        data_buffer = self._convert_to_wav(inline_data.data, inline_data.mime_type)
                    
                    audio_chunks.append(data_buffer)
            
            # Save combined audio
            if audio_chunks:
                with open(output_path, 'wb') as f:
                    for chunk in audio_chunks:
                        f.write(chunk)
                logger.info(f"✅ Gemini TTS saved to: {output_path}")
                return True
            else:
                logger.error("No audio data received from Gemini TTS")
                return False
                        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error converting text to speech with Gemini TTS: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Check if it's a quota exceeded error
            if "RESOURCE_EXHAUSTED" in error_msg or "quota" in error_msg.lower():
                logger.error("🚫 TTS Quota exceeded! Raising exception to retry later...")
                # Extract retry delay if available in error message
                retry_seconds = 300  # Default 5 minutes
                if "retry in" in error_msg.lower():
                    # Try to extract seconds from error message
                    import re
                    match = re.search(r'retry in (\d+(?:\.\d+)?)s', error_msg.lower())
                    if match:
                        retry_seconds = max(int(float(match.group(1))), 300)  # At least 5 minutes
                raise TTSQuotaExceeded(retry_after_seconds=retry_seconds)
            
            return False
    
    def _convert_to_wav(self, audio_data: bytes, mime_type: str) -> bytes:
        """
        Convert audio data to WAV format
        
        Args:
            audio_data: Raw audio data
            mime_type: MIME type of the audio
            
        Returns:
            WAV formatted audio bytes
        """
        import struct
        
        # Parse audio parameters from MIME type
        bits_per_sample = 16
        sample_rate = 24000
        
        parts = mime_type.split(";")
        for param in parts:
            param = param.strip()
            if param.lower().startswith("rate="):
                try:
                    rate_str = param.split("=", 1)[1]
                    sample_rate = int(rate_str)
                except (ValueError, IndexError):
                    pass
            elif param.startswith("audio/L"):
                try:
                    bits_per_sample = int(param.split("L", 1)[1])
                except (ValueError, IndexError):
                    pass
        
        # Create WAV header
        num_channels = 1
        data_size = len(audio_data)
        bytes_per_sample = bits_per_sample // 8
        block_align = num_channels * bytes_per_sample
        byte_rate = sample_rate * block_align
        chunk_size = 36 + data_size
        
        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",          # ChunkID
            chunk_size,       # ChunkSize
            b"WAVE",          # Format
            b"fmt ",          # Subchunk1ID
            16,               # Subchunk1Size (16 for PCM)
            1,                # AudioFormat (1 for PCM)
            num_channels,     # NumChannels
            sample_rate,      # SampleRate
            byte_rate,        # ByteRate
            block_align,      # BlockAlign
            bits_per_sample,  # BitsPerSample
            b"data",          # Subchunk2ID
            data_size         # Subchunk2Size
        )
        
        return header + audio_data
    
    async def get_video_search_keywords(self, topic: str, max_keywords: int = 5) -> list[str]:
        """
        Get alternative video search keywords from Gemini for better Pexels results
        
        Args:
            topic: The main topic/trend to find videos for
            max_keywords: Maximum number of alternative keywords to return
            
        Returns:
            List of search keywords, starting with the original topic
        """
        try:
            prompt = f"""Topic: {topic}

Generate {max_keywords - 1} stock video search keywords.

STRICT RULES:
❌ NO PEOPLE - No faces, no humans, no body parts
❌ NO CROWDS - No groups, no audiences
✅ ONLY: Objects, buildings, nature, technology, abstract concepts

Examples:
- Elon Musk → rocket launch, circuit board, satellite dish, night cityscape
- Climate Change → melting glacier, wind turbine, solar panel farm, factory smoke
- NYC Mayor → city skyline, capitol building, american flag, government building

Keywords for "{topic}" (NO PEOPLE, comma-separated):"""

            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 1024  # Increased from 300 to allow for thinking + output
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.vision_api_url,
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        text = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                        
                        # Check if response hit MAX_TOKENS (incomplete)
                        finish_reason = data.get('candidates', [{}])[0].get('finishReason', '')
                        if finish_reason == 'MAX_TOKENS':
                            logger.warning(f"⚠️ Gemini hit MAX_TOKENS for '{topic}', response may be incomplete")
                        
                        logger.info(f"🎬 Gemini raw response for '{topic}' ({len(text)} chars): {text[:500] if text else '(empty)'}")
                        
                        # Parse keywords from response - PRIORITIZE GEMINI SUGGESTIONS
                        keywords = []  # Start empty
                        
                        # Try comma-separated first
                        if ',' in text:
                            # Find the last line (likely contains the keywords)
                            lines = text.strip().split('\n')
                            last_line = lines[-1] if lines else ''
                            
                            for keyword in last_line.split(','):
                                keyword = keyword.strip().strip('"').strip("'").strip('-•*')
                                if keyword and len(keyword) < 40 and len(keywords) < max_keywords - 1:
                                    keywords.append(keyword)
                        
                        # If no comma-separated, try line-separated
                        if not keywords:
                            for line in text.strip().split('\n'):
                                # Clean the line: remove bullets, numbers, markdown, quotes
                                line = line.strip()
                                # Remove numbered lists (1. 2. etc)
                                if line and line[0].isdigit():
                                    line = line.split('.', 1)[-1] if '.' in line else line
                                # Remove markdown bold **text**
                                line = line.replace('**', '')
                                # Remove bullets and special chars
                                line = line.strip('-•*→').strip().strip('"').strip("'")
                                # Skip empty lines, very long lines (explanations), or lines with colons (headers)
                                if line and len(line) < 40 and ':' not in line and len(keywords) < max_keywords - 1:
                                    keywords.append(line)
                        
                        # Add original topic as LAST fallback
                        keywords.append(topic)
                        
                        logger.info(f"🎬 Gemini video keywords for '{topic}': {keywords}")
                        return keywords
                    else:
                        logger.warning(f"Gemini video keywords request failed: {response.status}")
                        return [topic]
        
        except Exception as e:
            logger.error(f"Error getting video keywords from Gemini: {e}")
            return [topic]
    
    async def analyze_trend_complete(self, trend: str) -> Optional[dict]:
        """
        Analyze a single trend and get ALL information in one call:
        - Wikipedia URL
        - Category
        - Video keywords
        
        Args:
            trend: Trend name/keyword
        
        Returns:
            Dictionary with: {
                "wikipedia_url": "https://en.wikipedia.org/wiki/...",
                "category": "Sports",
                "video_keywords": ["keyword1", "keyword2", ...]
            }
        """
        if not await self.is_available():
            logger.error("Gemini API key not configured")
            return None
        
        try:
            # Available categories for roll.wiki
            categories = [
                "Architecture", "Arts", "Business", "Culture", "Dance", "Economics",
                "Education", "Engineering", "Entertainment", "Environment", "Fashion",
                "Film", "Food", "Geography", "History", "Literature", "Medicine",
                "Music", "Philosophy", "Politics", "Psychology", "Religion", "Science",
                "Sports", "Technology", "Theater", "Transportation"
            ]
            
            prompt = f"""You are a Wikipedia and content expert. For this trend, provide:

Trend: {trend}

Provide in JSON format:
1. wikipedia_url: The MOST RELEVANT English Wikipedia page URL (full URL starting with https://en.wikipedia.org/wiki/)
2. category: Best category from this list: {', '.join(categories)}
3. video_keywords: List of 3-5 relevant keywords for finding background videos (simple, visual concepts like "basketball game", "city skyline", "technology", etc.)

IMPORTANT:
- Wikipedia URL must be EXACT and COMPLETE (e.g., "https://en.wikipedia.org/wiki/National_Basketball_Association", NOT just "NBA")
- Category must be ONE of the allowed categories
- Video keywords should be visual concepts (things you can actually see in videos)

Example response format:
{{
  "wikipedia_url": "https://en.wikipedia.org/wiki/National_Basketball_Association",
  "category": "Sports",
  "video_keywords": ["basketball game", "NBA arena", "sports crowd", "basketball players"]
}}

Your response (JSON only):"""
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.vision_api_url,
                    json=payload,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        candidates = result.get('candidates', [])
                        if candidates:
                            content = candidates[0].get('content', {})
                            parts = content.get('parts', [])
                            if parts:
                                text = parts[0].get('text', '').strip()
                                
                                # Try to parse JSON
                                try:
                                    # Remove markdown code blocks if present
                                    if text.startswith('```'):
                                        text = text.split('```')[1]
                                        if text.startswith('json'):
                                            text = text[4:]
                                        # Remove trailing ```
                                        if text.endswith('```'):
                                            text = text[:-3]
                                    
                                    data = json.loads(text.strip())
                                    logger.info(f"🤖 Gemini analysis for '{trend}':")
                                    logger.info(f"   URL: {data.get('wikipedia_url', 'N/A')}")
                                    logger.info(f"   Category: {data.get('category', 'N/A')}")
                                    logger.info(f"   Keywords: {data.get('video_keywords', [])}")
                                    return data
                                    
                                except json.JSONDecodeError as e:
                                    logger.error(f"Failed to parse Gemini JSON response: {e}")
                                    logger.error(f"Raw response: {text[:200]}")
                                    return None
                    else:
                        logger.warning(f"Gemini API request failed: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error analyzing trend with Gemini: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return None
    
    async def find_wikipedia_pages_for_trends(self, trends: list) -> dict:
        """
        Find Wikipedia pages and categories for a list of trends using Gemini AI
        
        Args:
            trends: List of trend names/keywords
        
        Returns:
            Dictionary mapping trend -> {url, category}
            Example: {
                "NBA": {
                    "url": "https://en.wikipedia.org/wiki/National_Basketball_Association",
                    "category": "Sports"
                }
            }
        """
        if not await self.is_available():
            logger.error("Gemini API key not configured")
            return {}
        
        try:
            # Create comma-separated trend list
            trends_text = "\n".join([f"- {trend}" for trend in trends])
            
            # Available categories for roll.wiki
            categories = [
                "Architecture", "Arts", "Business", "Culture", "Dance", "Economics",
                "Education", "Engineering", "Entertainment", "Environment", "Fashion",
                "Film", "Food", "Geography", "History", "Literature", "Medicine",
                "Music", "Philosophy", "Politics", "Psychology", "Religion", "Science",
                "Sports", "Technology", "Theater", "Transportation"
            ]
            
            prompt = f"""You are a Wikipedia expert. For each trend in the list below, provide:
1. The MOST RELEVANT English Wikipedia page URL
2. The best category from the allowed list

IMPORTANT RULES:
1. Return ONLY the exact Wikipedia URL (starting with https://en.wikipedia.org/wiki/)
2. Choose the MAIN article, not disambiguation pages
3. For people, use their full name article
4. For abbreviations (like NBA, NFL), use the full expanded form article
5. If uncertain, choose the most popular/well-known meaning
6. Category MUST be one of these: {', '.join(categories)}
7. Format as JSON with "url" and "category" fields

Trend List:
{trends_text}

Return ONLY valid JSON with all trends, no additional text or explanation.
Example format:
{{
  "NBA": {{
    "url": "https://en.wikipedia.org/wiki/National_Basketball_Association",
    "category": "Sports"
  }},
  "Taylor Swift": {{
    "url": "https://en.wikipedia.org/wiki/Taylor_Swift",
    "category": "Music"
  }},
  "Apple": {{
    "url": "https://en.wikipedia.org/wiki/Apple_Inc.",
    "category": "Technology"
  }}
}}"""
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.1,  # Low temperature for consistent results
                    "topP": 0.8,
                    "topK": 10
                }
            }
            
            logger.info(f"Asking Gemini to find Wikipedia pages for {len(trends)} trends...")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.vision_api_url,
                    json=payload,
                    timeout=60  # Longer timeout for multiple trends
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        candidates = result.get('candidates', [])
                        if candidates:
                            content = candidates[0].get('content', {})
                            parts = content.get('parts', [])
                            if parts:
                                response_text = parts[0].get('text', '')
                                
                                # Clean and parse JSON
                                try:
                                    # Remove markdown code blocks
                                    clean_text = response_text.strip()
                                    if '```json' in clean_text:
                                        clean_text = clean_text.split('```json')[1].split('```')[0]
                                    elif '```' in clean_text:
                                        clean_text = clean_text.split('```')[1].split('```')[0]
                                    
                                    trend_data = json.loads(clean_text.strip())
                                    
                                    logger.info(f"✅ Gemini found {len(trend_data)} Wikipedia pages with categories")
                                    for trend, data in trend_data.items():
                                        if isinstance(data, dict):
                                            logger.info(f"  - {trend}: {data.get('url')} [{data.get('category')}]")
                                        else:
                                            # Backward compatibility: if old format (just URL string)
                                            logger.info(f"  - {trend}: {data}")
                                    
                                    return trend_data
                                    
                                except json.JSONDecodeError as e:
                                    logger.error(f"Failed to parse Gemini JSON response: {e}")
                                    logger.error(f"Response text: {response_text[:500]}")
                                    return {}
                    else:
                        error_text = await response.text()
                        logger.error(f"Gemini API error {response.status}: {error_text}")
                        return {}
                        
        except Exception as e:
            logger.error(f"Error finding Wikipedia pages with Gemini: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {}
    
    async def analyze_trend_context(self, trend: str, summary: str) -> Optional[dict]:
        """
        Analyze trend context and provide insights
        
        Args:
            trend: Trend name
            summary: Wikipedia summary
        
        Returns:
            Dictionary with analysis results
        """
        if not await self.is_available():
            return None
        
        try:
            prompt = f"""Analyze this trend and provide structured information:

Trend: {trend}
Summary: {summary}

Provide:
1. Main topic category
2. Why it's trending (in 1-2 sentences)
3. Target audience
4. Content angle suggestions
5. Best hashtags (3-5)

Format as JSON."""
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.vision_api_url,
                    json=payload,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        candidates = result.get('candidates', [])
                        if candidates:
                            content = candidates[0].get('content', {})
                            parts = content.get('parts', [])
                            if parts:
                                analysis_text = parts[0].get('text', '')
                                # Try to parse as JSON
                                try:
                                    # Remove markdown code blocks if present
                                    clean_text = analysis_text.strip()
                                    if clean_text.startswith('```'):
                                        clean_text = clean_text.split('```')[1]
                                        if clean_text.startswith('json'):
                                            clean_text = clean_text[4:]
                                    analysis = json.loads(clean_text)
                                    return analysis
                                except:
                                    # Return as plain text if JSON parsing fails
                                    return {"analysis": analysis_text}
                    return None
                    
        except Exception as e:
            logger.error(f"Error analyzing trend context: {e}")
            return None


# Test function
async def test_gemini():
    """Test Gemini functionality"""
    analyzer = GeminiAnalyzer()
    
    # Test availability
    available = await analyzer.is_available()
    print(f"Gemini API available: {available}")
    
    if not available:
        print("Please set GEMINI_API_KEY in .env file")
        return
    
    # Test text analysis
    print("\n--- Testing trend analysis ---")
    result = await analyzer.analyze_trend_context(
        "Artificial Intelligence",
        "Artificial intelligence (AI) is intelligence demonstrated by machines..."
    )
    if result:
        print(f"Analysis: {json.dumps(result, indent=2)}")
    
    # Test TTS
    print("\n--- Testing text-to-speech ---")
    success = await analyzer.text_to_speech(
        "Hello, this is a test of Google Text to Speech.",
        "test_tts.mp3",
        language_code="en-US"
    )
    print(f"TTS test: {'Success' if success else 'Failed'}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_gemini())
