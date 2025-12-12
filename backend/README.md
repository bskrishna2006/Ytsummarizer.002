# YouTube Summarizer - Flask Backend

Flask-based REST API for YouTube video transcript extraction and AI-powered summarization.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Groq API key

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Add your Groq API key to `.env`:
```
GROQ_API_KEY=your_actual_api_key_here
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

### Extract Transcript
```http
POST /api/transcript
Content-Type: application/json

{
  "url": "https://youtube.com/watch?v=..."
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

### Full Processing
```http
POST /api/process
Content-Type: application/json

{
  "url": "https://youtube.com/watch?v=...",
  "summary_type": "general",
  "chunk_size": 2500,
  "max_tokens": 500
}
```

## 🏗️ Project Structure

```
backend/
├── app.py                 # Flask application & routes
├── services/
│   ├── transcript.py      # Transcript extraction service
│   └── summarizer.py      # AI summarization service
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
└── README.md             # This file
```

## 🔧 Configuration

Environment variables in `.env`:
- `GROQ_API_KEY` - Your Groq API key (required)
- `FLASK_ENV` - Environment mode (development/production)
- `FLASK_DEBUG` - Debug mode (0 or 1)

## 📝 Error Handling

All endpoints return JSON responses with consistent error format:
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
