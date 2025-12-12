# YouTube Summarizer - Multilingual Flask Backend

Flask-based REST API for YouTube video transcript extraction and AI-powered summarization with **full multilingual support**.

## ✨ Features

- 🌐 **11 Languages Supported**: English, Hindi, Tamil, Telugu, Kannada, Malayalam, Gujarati, Bengali, Marathi, Punjabi, Urdu
- 🎤 **Whisper Transcription**: Local speech-to-text when subtitles are unavailable
- 🔄 **NLLB-200 Translation**: Translate between any supported languages
- 🤖 **AI Summarization**: Free Groq API with LLaMA 3.1
- 💸 **100% Free**: All ML models run locally, no paid APIs

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- FFmpeg (for audio extraction)
- Groq API key (free at https://console.groq.com)
- 8GB RAM minimum (16GB recommended)

### Installation

1. Install FFmpeg:
```powershell
# Windows
winget install FFmpeg

# Ubuntu
sudo apt install ffmpeg

# Mac
brew install ffmpeg
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

> **Tip**: For CPU-only installation (saves disk space):
> ```bash
> pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
> pip install -r requirements.txt
> ```

3. Create `.env` file:
```bash
GROQ_API_KEY=your_groq_api_key_here
```

4. Run the server:
```bash
python app.py
```

Server will start at `http://localhost:5000`

## 📡 API Endpoints

### Health Check
```http
GET /api/health
```

### List Supported Languages
```http
GET /api/languages
```

### Pre-load Models (Optional)
```http
POST /api/warmup
Content-Type: application/json

{
  "translation": true,
  "whisper": true
}
```

### Extract Transcript (Multilingual)
```http
POST /api/transcript
Content-Type: application/json

{
  "url": "https://youtube.com/watch?v=...",
  "use_whisper": true
}
```

**Response:**
```json
{
  "success": true,
  "video_id": "xxxxx",
  "transcript": "...",
  "language": "tam",
  "language_name": "Tamil",
  "source": "whisper",
  "word_count": 1500
}
```

### Translate Text
```http
POST /api/translate
Content-Type: application/json

{
  "text": "Hello, how are you?",
  "source_lang": "eng",
  "target_lang": "hin"
}
```

### Detect Language
```http
POST /api/detect-language
Content-Type: application/json

{
  "text": "नमस्ते"
}
```

### Generate Summary
```http
POST /api/summarize
Content-Type: application/json

{
  "transcript": "video transcript text...",
  "summary_type": "general",
  "chunk_size": 2500,
  "max_tokens": 500
}
```

**Summary Types:**
- `general` - Balanced, concise overview
- `detailed` - Comprehensive with key points
- `bullet_points` - Organized list format
- `key_takeaways` - Main insights only

### Full Multilingual Pipeline
```http
POST /api/process
Content-Type: application/json

{
  "url": "https://youtube.com/watch?v=...",
  "summary_type": "general",
  "target_language": "hin"
}
```

**Response:**
```json
{
  "success": true,
  "video_id": "xxxxx",
  "original_language": "tam",
  "original_language_name": "Tamil",
  "transcript": "...",
  "english_transcript": "...",
  "summary": "...",
  "summary_language": "hin",
  "summary_language_name": "Hindi",
  "statistics": {
    "original_word_count": 1500,
    "summary_word_count": 200,
    "compression_ratio": 13.3,
    "reading_time_minutes": 1
  }
}
```

## 🏗️ Project Structure

```
backend/
├── app.py                      # Flask application & routes
├── config.py                   # Model & language configuration
├── services/
│   ├── transcript.py           # Subtitle + Whisper transcript extraction
│   ├── summarizer.py           # Groq AI summarization
│   ├── speech_to_text.py       # Local Whisper transcription
│   └── translation.py          # NLLB-200 translation service
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
└── README.md                   # This file
```

## 🔧 Configuration

### Environment Variables (.env)
```
GROQ_API_KEY=your_groq_api_key_here
```

### Model Settings (config.py)
```python
WHISPER_MODEL = "openai/whisper-small"  # Options: tiny, small, medium
NLLB_MODEL = "facebook/nllb-200-distilled-600M"  # Smallest NLLB
```

## 📊 Model Sizes

| Model | Size | RAM Required |
|-------|------|--------------|
| Whisper-small | ~500MB | ~2GB |
| NLLB-200-distilled | ~2.4GB | ~4GB |
| **Total** | **~3GB** | **~6GB** |

## 🔒 Privacy

All transcription and translation happens **locally on your machine**:
- ✅ Whisper runs locally (no API calls)
- ✅ NLLB-200 runs locally (no API calls)
- ⚡ Only Groq API is used for summarization (free tier)

## 📝 Error Handling

All endpoints return JSON with consistent error format:
```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

HTTP Status Codes:
- `200` - Success
- `400` - Bad request (invalid input)
- `404` - Not found
- `500` - Server error

## 💡 Tips

1. **First Request is Slow**: Models download on first use (~5GB total)
2. **Use Warmup**: Call `/api/warmup` after startup to pre-load models
3. **Memory Usage**: Close other apps when processing videos
4. **CPU vs GPU**: Models auto-detect GPU but work fine on CPU
