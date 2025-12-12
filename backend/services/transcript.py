import re
import os
import tempfile
import yt_dlp


class TranscriptService:
    """Service for extracting transcripts from YouTube videos"""
    
    def extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL"""
        regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
        match = re.search(regex, url)
        if match:
            return match.group(1)
        raise ValueError("Invalid YouTube URL")
    
    def clean_autogen_transcript(self, text: str) -> str:
        """
        Cleans auto-generated YouTube captions:
        1. Removes <c>...</c> tags
        2. Removes <00:00:00.000> timestamps
        3. Collapses multiple spaces
        """
        # Remove <c>...</c> tags
        text = re.sub(r"</?c>", "", text)
        
        # Remove timestamps like <00:00:06.480>
        text = re.sub(r"<\d{2}:\d{2}:\d{2}\.\d{3}>", "", text)
        
        # Collapse multiple spaces
        text = re.sub(r"\s+", " ", text).strip()
        
        return text
    
    def get_video_transcript(self, url: str, lang: str = "en") -> str:
        """
        Get transcript using yt-dlp
        
        Args:
            url: YouTube video URL
            lang: Language code (default: "en")
            
        Returns:
            Cleaned transcript text
            
        Raises:
            Exception: If transcript cannot be extracted
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            ydl_opts = {
                "skip_download": True,          # do not download video
                "writesubtitles": True,         # download manual captions if available
                "writeautomaticsub": True,      # download auto-generated captions
                "subtitlesformat": "vtt",       # force VTT output
                "outtmpl": os.path.join(temp_dir, "%(id)s.%(ext)s"),  # save in temp dir
                "quiet": True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)
                    # Download subtitles to temp directory
                    ydl.download([url])
                    
                    # Find the subtitle file
                    sub_file = None
                    for file in os.listdir(temp_dir):
                        if file.startswith(info["id"]) and file.endswith(".vtt"):
                            sub_file = os.path.join(temp_dir, file)
                            break
                    
                    if not sub_file:
                        raise Exception("No subtitle file was downloaded. Video may not have captions.")
                    
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
                        raise Exception("Extracted transcript is too short or empty")
                    
                    return clean_text
                    
                except Exception as e:
                    raise Exception(f"Could not retrieve transcript: {str(e)}")
