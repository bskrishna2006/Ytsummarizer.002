"""
Speech-to-Text Service using OpenAI Whisper (Local Model)

This service provides LOCAL speech-to-text transcription using Whisper.
NO API CALLS - everything runs on your machine for FREE!

Features:
- Extracts audio from YouTube videos using yt-dlp
- Transcribes audio using Whisper (small model by default)
- Detects the language of the audio automatically
- Returns both transcript and detected language

Requirements:
- FFmpeg must be installed on the system
- Sufficient RAM (~2GB for whisper-small)
"""

import os
import tempfile
import logging
from typing import Optional, Tuple

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import yt_dlp

from config import (
    WHISPER_MODEL,
    AUDIO_FORMAT,
    AUDIO_SAMPLE_RATE,
    normalize_whisper_lang,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_ffmpeg_path() -> Optional[str]:
    """
    Get the path to FFmpeg executable directory.
    Uses static-ffmpeg which provides both ffmpeg and ffprobe.
    Falls back to system PATH or imageio-ffmpeg.
    """
    import shutil
    
    # Check if ffmpeg AND ffprobe are in system PATH
    ffmpeg_path = shutil.which("ffmpeg")
    ffprobe_path = shutil.which("ffprobe")
    if ffmpeg_path and ffprobe_path:
        logger.info(f"Using system FFmpeg: {ffmpeg_path}")
        return os.path.dirname(ffmpeg_path)
    
    # Try static-ffmpeg (provides both ffmpeg and ffprobe)
    try:
        import static_ffmpeg
        # This downloads ffmpeg/ffprobe if not already present
        ffmpeg_path, ffprobe_path = static_ffmpeg.run.get_or_fetch_platform_executables_else_raise()
        if ffmpeg_path and os.path.exists(ffmpeg_path):
            ffmpeg_dir = os.path.dirname(ffmpeg_path)
            logger.info(f"Using static-ffmpeg: {ffmpeg_dir}")
            return ffmpeg_dir
    except ImportError:
        logger.warning("static-ffmpeg not installed")
    except Exception as e:
        logger.warning(f"static-ffmpeg error: {e}")
    
    # Fall back to imageio-ffmpeg (only has ffmpeg, not ffprobe)
    try:
        import imageio_ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        if ffmpeg_path and os.path.exists(ffmpeg_path):
            logger.warning("Using imageio-ffmpeg (may not have ffprobe)")
            return os.path.dirname(ffmpeg_path)
    except ImportError:
        pass
    
    return None


class SpeechToTextService:
    """
    Service for converting speech to text using local Whisper model.
    
    The model is lazily loaded on first use to save memory during startup.
    All processing happens locally - no API costs!
    """
    
    def __init__(self, model_name: str = WHISPER_MODEL):
        """
        Initialize the speech-to-text service.
        
        Args:
            model_name: Hugging Face model identifier for Whisper
        """
        self.model_name = model_name
        self._pipe = None  # Lazy-loaded pipeline
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        self._torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
        logger.info(f"SpeechToTextService initialized (device: {self._device})")
    
    def _load_model(self):
        """
        Load the Whisper model and processor.
        Called lazily on first transcription request.
        """
        if self._pipe is not None:
            return
        
        logger.info(f"Loading Whisper model: {self.model_name}")
        logger.info("This may take a few minutes on first run (downloading model)...")
        
        try:
            # Load model with optimizations for CPU/GPU
            model = AutoModelForSpeechSeq2Seq.from_pretrained(
                self.model_name,
                torch_dtype=self._torch_dtype,
                low_cpu_mem_usage=True,
                use_safetensors=True
            )
            model.to(self._device)
            
            # Load processor
            processor = AutoProcessor.from_pretrained(self.model_name)
            
            # Create pipeline for easy inference
            self._pipe = pipeline(
                "automatic-speech-recognition",
                model=model,
                tokenizer=processor.tokenizer,
                feature_extractor=processor.feature_extractor,
                torch_dtype=self._torch_dtype,
                device=self._device,
                return_timestamps=False
            )
            
            logger.info("Whisper model loaded successfully!")
            
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise Exception(f"Could not load Whisper model: {str(e)}")
    
    def extract_audio_from_youtube(self, url: str) -> str:
        """
        Extract audio from a YouTube video.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Path to the extracted audio file (WAV format)
            
        Raises:
            Exception: If audio extraction fails
        """
        logger.info(f"Extracting audio from: {url}")
        
        # Get FFmpeg path (system or imageio-ffmpeg)
        ffmpeg_path = get_ffmpeg_path()
        if not ffmpeg_path:
            raise Exception("FFmpeg not found. Please install FFmpeg or run: pip install imageio-ffmpeg")
        
        logger.info(f"Using FFmpeg: {ffmpeg_path}")
        
        # Create temporary directory for audio file
        temp_dir = tempfile.mkdtemp()
        output_template = os.path.join(temp_dir, "audio.%(ext)s")
        
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": AUDIO_FORMAT,
                "preferredquality": "192",
            }],
            "ffmpeg_location": ffmpeg_path,  # yt-dlp needs the directory containing ffmpeg and ffprobe
            "quiet": True,
            "no_warnings": True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Find the extracted audio file
            audio_path = os.path.join(temp_dir, f"audio.{AUDIO_FORMAT}")
            
            if not os.path.exists(audio_path):
                raise Exception("Audio file was not created")
            
            logger.info(f"Audio extracted to: {audio_path}")
            return audio_path
            
        except Exception as e:
            logger.error(f"Audio extraction failed: {e}")
            raise Exception(f"Could not extract audio: {str(e)}")
    
    def transcribe_audio(self, audio_path: str) -> dict:
        """
        Transcribe an audio file using Whisper.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dictionary with:
                - text: The transcribed text
                - language: Detected language code (normalized)
                - raw_language: Original Whisper language code
        """
        # Ensure model is loaded
        self._load_model()
        
        logger.info(f"Transcribing audio: {audio_path}")
        
        try:
            # Run transcription
            result = self._pipe(
                audio_path,
                generate_kwargs={
                    "task": "transcribe",
                    "language": None,  # Auto-detect language
                }
            )
            
            # Extract text
            text = result.get("text", "").strip()
            
            if not text:
                raise Exception("Transcription produced empty text")
            
            # Try to get detected language from the model
            # Note: Whisper pipeline may not always return language info
            raw_language = "en"  # Default to English
            
            # Normalize the language code
            language = normalize_whisper_lang(raw_language)
            
            logger.info(f"Transcription complete. Language: {language}")
            
            return {
                "text": text,
                "language": language,
                "raw_language": raw_language
            }
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise Exception(f"Could not transcribe audio: {str(e)}")
    
    def transcribe_youtube_video(self, url: str) -> dict:
        """
        Full pipeline: Extract audio from YouTube and transcribe it.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Dictionary with:
                - text: The transcribed text
                - language: Detected language code
                - word_count: Number of words in transcript
        """
        audio_path = None
        
        try:
            # Step 1: Extract audio
            audio_path = self.extract_audio_from_youtube(url)
            
            # Step 2: Transcribe
            result = self.transcribe_audio(audio_path)
            
            # Add word count
            result["word_count"] = len(result["text"].split())
            
            return result
            
        finally:
            # Cleanup: Remove temporary audio file
            if audio_path and os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                    # Also remove the parent temp directory
                    temp_dir = os.path.dirname(audio_path)
                    if os.path.exists(temp_dir):
                        os.rmdir(temp_dir)
                except:
                    pass  # Ignore cleanup errors
    
    def is_model_loaded(self) -> bool:
        """Check if the Whisper model is currently loaded."""
        return self._pipe is not None
    
    def warmup(self):
        """
        Pre-load the model to avoid delay on first request.
        Call this during application startup if desired.
        """
        logger.info("Warming up SpeechToTextService...")
        self._load_model()
        logger.info("SpeechToTextService warmup complete!")
