"""
Transcript Service for YouTube Videos

This service extracts transcripts from YouTube videos using multiple methods:
1. First, try to get existing subtitles/captions (fastest, no model needed)
2. If no subtitles available, fallback to audio extraction + Whisper transcription

The fallback uses the SpeechToTextService for local Whisper transcription.
"""

import re
import os
import tempfile
import logging
from typing import Optional, Tuple

import yt_dlp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TranscriptService:
    """
    Service for extracting transcripts from YouTube videos.
    
    Supports two methods:
    1. Subtitle extraction (fast, no ML models)
    2. Audio transcription via Whisper (slower, requires SpeechToTextService)
    """
    
    def __init__(self):
        """Initialize the transcript service."""
        self._speech_to_text = None  # Lazy-loaded
    
    def _get_speech_to_text_service(self):
        """Lazy-load the SpeechToTextService to avoid loading Whisper unless needed."""
        if self._speech_to_text is None:
            from services.speech_to_text import SpeechToTextService
            self._speech_to_text = SpeechToTextService()
        return self._speech_to_text
    
    def extract_video_id(self, url: str) -> str:
        """
        Extract video ID from YouTube URL.
        
        Args:
            url: YouTube URL in various formats
            
        Returns:
            11-character video ID
            
        Raises:
            ValueError: If URL is invalid
        """
        regex = r"(?:v=|\/|youtu\.be\/)([0-9A-Za-z_-]{11}).*"
        match = re.search(regex, url)
        if match:
            return match.group(1)
        raise ValueError("Invalid YouTube URL")
    
    def clean_autogen_transcript(self, text: str) -> str:
        """
        Clean auto-generated YouTube captions.
        
        Removes:
        - <c>...</c> tags
        - Timestamps like <00:00:06.480>
        - Multiple spaces
        
        Args:
            text: Raw VTT subtitle text
            
        Returns:
            Cleaned transcript text
        """
        # Remove <c>...</c> tags
        text = re.sub(r"</?c>", "", text)
        
        # Remove timestamps like <00:00:06.480>
        text = re.sub(r"<\d{2}:\d{2}:\d{2}\.\d{3}>", "", text)
        
        # Collapse multiple spaces
        text = re.sub(r"\s+", " ", text).strip()
        
        return text
    
    def get_subtitles(self, url: str, lang: str = "en") -> Optional[dict]:
        """
        Try to get existing subtitles from YouTube.
        
        Args:
            url: YouTube video URL
            lang: Preferred language code (default: "en")
            
        Returns:
            Dictionary with transcript and language, or None if no subtitles
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            ydl_opts = {
                "skip_download": True,
                "writesubtitles": True,
                "writeautomaticsub": True,
                "subtitlesformat": "vtt",
                "outtmpl": os.path.join(temp_dir, "%(id)s.%(ext)s"),
                "quiet": True,
            }
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    ydl.download([url])
                    
                    # Find subtitle file
                    video_id = info["id"]
                    sub_file = None
                    detected_lang = "eng"
                    
                    for file in os.listdir(temp_dir):
                        if file.startswith(video_id) and file.endswith(".vtt"):
                            sub_file = os.path.join(temp_dir, file)
                            # Try to extract language from filename
                            # Format: videoId.lang.vtt
                            parts = file.split(".")
                            if len(parts) >= 3:
                                detected_lang = parts[-2]
                            break
                    
                    if not sub_file:
                        logger.info("No subtitle file found")
                        return None
                    
                    # Read and clean VTT file
                    lines = []
                    with open(sub_file, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            if line.startswith("WEBVTT"):
                                continue
                            if "-->" in line:
                                continue
                            if re.match(r"^\d+$", line):
                                continue
                            lines.append(line)
                    
                    raw_text = " ".join(lines)
                    clean_text = self.clean_autogen_transcript(raw_text)
                    
                    if not clean_text or len(clean_text.strip()) < 50:
                        logger.info("Extracted subtitles too short")
                        return None
                    
                    # Map common language codes
                    lang_map = {
                        "en": "eng", "en-US": "eng", "en-GB": "eng",
                        "hi": "hin", "hi-IN": "hin",
                        "ta": "tam", "ta-IN": "tam",
                        "te": "tel", "te-IN": "tel",
                        "kn": "kan", "kn-IN": "kan",
                        "ml": "mal", "ml-IN": "mal",
                        "gu": "guj", "gu-IN": "guj",
                        "bn": "ben", "bn-IN": "ben",
                        "mr": "mar", "mr-IN": "mar",
                        "pa": "pan", "pa-IN": "pan",
                        "ur": "urd", "ur-PK": "urd",
                    }
                    
                    normalized_lang = lang_map.get(detected_lang, detected_lang)
                    
                    logger.info(f"Subtitles extracted successfully (language: {normalized_lang})")
                    
                    return {
                        "transcript": clean_text,
                        "language": normalized_lang,
                        "source": "subtitles",
                        "word_count": len(clean_text.split())
                    }
                    
            except Exception as e:
                logger.warning(f"Subtitle extraction failed: {e}")
                return None
    
    def get_video_transcript(self, url: str, use_whisper_fallback: bool = True) -> dict:
        """
        Get transcript from a YouTube video.
        
        First tries to get subtitles. If unavailable and use_whisper_fallback is True,
        falls back to audio extraction and Whisper transcription.
        
        Args:
            url: YouTube video URL
            use_whisper_fallback: Whether to use Whisper if no subtitles (default: True)
            
        Returns:
            Dictionary with:
                - transcript: The transcript text
                - language: Detected/extracted language code
                - source: "subtitles" or "whisper"
                - word_count: Number of words
                
        Raises:
            Exception: If transcript cannot be obtained
        """
        # Try subtitles first (faster, no model needed)
        logger.info("Attempting to get subtitles...")
        result = self.get_subtitles(url)
        
        if result:
            return result
        
        # Fallback to Whisper transcription
        if use_whisper_fallback:
            logger.info("No subtitles found. Falling back to Whisper transcription...")
            
            try:
                stt_service = self._get_speech_to_text_service()
                whisper_result = stt_service.transcribe_youtube_video(url)
                
                return {
                    "transcript": whisper_result["text"],
                    "language": whisper_result["language"],
                    "source": "whisper",
                    "word_count": whisper_result["word_count"]
                }
                
            except Exception as e:
                logger.error(f"Whisper transcription failed: {e}")
                raise Exception(f"Could not retrieve transcript: {str(e)}")
        
        raise Exception("No subtitles available and Whisper fallback is disabled")
    
    def get_video_transcript_legacy(self, url: str, lang: str = "en") -> str:
        """
        Legacy method for backward compatibility.
        Returns only the transcript text (no language info).
        """
        result = self.get_video_transcript(url, use_whisper_fallback=True)
        return result["transcript"]
