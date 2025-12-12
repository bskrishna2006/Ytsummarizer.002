# 🚀 Getting Started Guide

## Complete Setup Instructions for YouTube Video Summarizer

### Prerequisites

Before you begin, ensure you have:
- ✅ Python 3.8 or higher installed
- ✅ Node.js 18 or higher installed
- ✅ A Groq API key (get one free at https://console.groq.com)
- ✅ Git (optional, for version control)

---

## 🎯 Quick Setup (Recommended)

### Option 1: Automated Setup (Windows)

```powershell
cd updated
.\setup.ps1
```

This script will:
1. Install all backend dependencies
2. Install all frontend dependencies
3. Create environment files
4. Display next steps

### Option 2: Manual Setup

Follow the step-by-step guide below.

---

## 📦 Manual Setup Instructions

### Step 1: Backend Setup

1. **Navigate to backend directory:**
```powershell
cd updated\backend
```

2. **Install Python dependencies:**
```powershell
pip install -r requirements.txt
```

3. **Create environment file:**
```powershell
Copy-Item .env.example .env
```

4. **Edit `.env` file and add your Groq API key:**
```
GROQ_API_KEY=your_actual_groq_api_key_here
FLASK_ENV=development
FLASK_DEBUG=1
```

5. **Verify installation:**
```powershell
python app.py
```

You should see:
```
🚀 Starting YouTube Summarizer API...
📡 API available at: http://localhost:5000
```

### Step 2: Frontend Setup

1. **Open a NEW terminal and navigate to frontend directory:**
```powershell
cd updated\frontend
```

2. **Install Node dependencies:**
```powershell
npm install
```

3. **Verify `.env` file exists with:**
```
VITE_API_URL=http://localhost:5000
```

4. **Start development server:**
```powershell
npm run dev
```

You should see:
```
VITE v7.2.7  ready in 2584 ms
➜  Local:   http://localhost:5173/
```

---

## 🎮 Running the Application

### Start Backend (Terminal 1)
```powershell
cd updated\backend
python app.py
```

### Start Frontend (Terminal 2)
```powershell
cd updated\frontend
npm run dev
```

### Access Application
Open your browser and go to: **http://localhost:5173**

---

## 🧪 Testing the Application

1. **Health Check:**
   - Visit: http://localhost:5000/api/health
   - Should return: `{"status": "healthy", "message": "YouTube Summarizer API is running"}`

2. **Test with a Video:**
   - Paste any YouTube URL (e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ)
   - Select summary type
   - Click "Generate Summary"
   - Wait for processing (10-60 seconds depending on video length)

---

## 🎨 Summary Styles Explained

1. **📋 General Summary**
   - Best for: Quick overview
   - Length: Concise
   - Format: Paragraph form

2. **📖 Detailed Summary**
   - Best for: In-depth understanding
   - Length: Comprehensive
   - Format: Structured paragraphs with key points

3. **•  Bullet Points**
   - Best for: Scannable content
   - Length: Medium
   - Format: Organized list

4. **💡 Key Takeaways**
   - Best for: Action items
   - Length: Brief
   - Format: Main insights only

---

## 🐛 Troubleshooting

### Backend Issues

**Problem: "GROQ_API_KEY not found"**
- Solution: Check backend/.env file has correct API key
- Verify no spaces around the = sign
- Restart backend server

**Problem: "Module not found" errors**
- Solution: Reinstall dependencies
  ```powershell
  pip install -r requirements.txt
  ```

**Problem: Port 5000 already in use**
- Solution: Change port in backend/app.py
  ```python
  app.run(debug=True, host='0.0.0.0', port=5001)
  ```
- Update frontend/.env to match:
  ```
  VITE_API_URL=http://localhost:5001
  ```

### Frontend Issues

**Problem: "Cannot connect to backend"**
- Solution: Ensure backend is running on port 5000
- Check frontend/.env has correct VITE_API_URL
- Look for CORS errors in browser console

**Problem: Blank page or errors**
- Solution: Check browser console (F12)
- Clear browser cache
- Restart frontend dev server

**Problem: Tailwind styles not working**
- Solution: Ensure tailwind.config.js exists
- Check index.css has @tailwind directives
- Restart dev server

### Video Processing Issues

**Problem: "No subtitle file was downloaded"**
- Solution: Video must have captions/subtitles enabled
- Try a different video
- Check if video is public (not private/unlisted)

**Problem: "Invalid YouTube URL"**
- Solution: Use full YouTube URL format
- Supported formats:
  - https://www.youtube.com/watch?v=VIDEO_ID
  - https://youtu.be/VIDEO_ID

---

## 📊 API Endpoints Reference

### GET /api/health
Health check endpoint
```json
Response: {
  "status": "healthy",
  "message": "YouTube Summarizer API is running"
}
```

### POST /api/transcript
Extract transcript from video
```json
Request: {
  "url": "https://youtube.com/watch?v=..."
}

Response: {
  "success": true,
  "video_id": "abc123",
  "transcript": "full text...",
  "word_count": 5000
}
```

### POST /api/summarize
Generate summary from transcript
```json
Request: {
  "transcript": "text...",
  "summary_type": "general",
  "chunk_size": 2500,
  "max_tokens": 500
}

Response: {
  "success": true,
  "summary": "summary text...",
  "statistics": {
    "original_word_count": 5000,
    "summary_word_count": 250,
    "compression_ratio": 5.0,
    "reading_time_minutes": 1
  }
}
```

### POST /api/process
Full pipeline (recommended)
```json
Request: {
  "url": "https://youtube.com/watch?v=...",
  "summary_type": "general"
}

Response: {
  "success": true,
  "video_id": "abc123",
  "transcript": "full text...",
  "summary": "summary text...",
  "statistics": {...}
}
```

---

## 🚀 Production Deployment

### Backend Deployment Options
1. **Heroku** - Easy, free tier available
2. **Railway** - Simple, modern platform
3. **Render** - Free tier with auto-deploy
4. **DigitalOcean** - More control, affordable

### Frontend Deployment Options
1. **Vercel** - Recommended, automatic deployments
2. **Netlify** - Great for static sites
3. **GitHub Pages** - Free, git-based
4. **AWS S3** - Scalable, enterprise-grade

### Environment Variables for Production

**Backend:**
```
GROQ_API_KEY=your_production_key
FLASK_ENV=production
FLASK_DEBUG=0
CORS_ORIGINS=https://your-frontend-domain.com
```

**Frontend:**
```
VITE_API_URL=https://your-backend-api.com
```

---

## 📚 Additional Resources

- **Groq Documentation**: https://console.groq.com/docs
- **yt-dlp Documentation**: https://github.com/yt-dlp/yt-dlp
- **React Documentation**: https://react.dev
- **Flask Documentation**: https://flask.palletsprojects.com
- **Tailwind CSS**: https://tailwindcss.com

---

## 💡 Tips for Best Results

1. **Video Selection:**
   - Choose videos with clear speech
   - Educational/tutorial content works best
   - Ensure captions are available

2. **Summary Types:**
   - Use "General" for quick overviews
   - Use "Detailed" for learning
   - Use "Bullet Points" for note-taking
   - Use "Key Takeaways" for reviews

3. **Performance:**
   - Videos under 30 minutes process fastest
   - Longer videos use smart chunking (may take 1-2 minutes)
   - Free tier has rate limits, use responsibly

---

## 🤝 Support

If you encounter issues:
1. Check this guide's troubleshooting section
2. Review backend/frontend README files
3. Check API logs in terminal
4. Open a GitHub issue with error details

---

## 📄 License

MIT License - Feel free to use and modify for your projects!

---

**Happy Summarizing! 🎉**
