from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

from services.transcript import TranscriptService
from services.summarizer import SummarizerService

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Initialize services
transcript_service = TranscriptService()
summarizer_service = SummarizerService()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'YouTube Summarizer API is running'
    }), 200

@app.route('/api/transcript', methods=['POST'])
def get_transcript():
    """
    Extract transcript from YouTube video
    Request body: { "url": "youtube_url" }
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'error': 'Missing YouTube URL',
                'message': 'Please provide a valid YouTube URL'
            }), 400
        
        url = data['url']
        
        # Extract video ID
        video_id = transcript_service.extract_video_id(url)
        
        # Get transcript
        transcript = transcript_service.get_video_transcript(url)
        
        # Calculate word count
        word_count = len(transcript.split())
        
        return jsonify({
            'success': True,
            'video_id': video_id,
            'transcript': transcript,
            'word_count': word_count
        }), 200
        
    except ValueError as e:
        return jsonify({
            'error': 'Invalid URL',
            'message': str(e)
        }), 400
        
    except Exception as e:
        return jsonify({
            'error': 'Transcript extraction failed',
            'message': str(e)
        }), 500

@app.route('/api/summarize', methods=['POST'])
def summarize():
    """
    Generate summary from transcript
    Request body: {
        "transcript": "text",
        "summary_type": "general|detailed|bullet_points|key_takeaways",
        "chunk_size": 2500 (optional),
        "max_tokens": 500 (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'transcript' not in data:
            return jsonify({
                'error': 'Missing transcript',
                'message': 'Please provide transcript text'
            }), 400
        
        transcript = data['transcript']
        summary_type = data.get('summary_type', 'general')
        chunk_size = data.get('chunk_size', 2500)
        max_tokens = data.get('max_tokens', 500)
        
        # Validate summary type
        valid_types = ['general', 'detailed', 'bullet_points', 'key_takeaways']
        if summary_type not in valid_types:
            return jsonify({
                'error': 'Invalid summary type',
                'message': f'Summary type must be one of: {", ".join(valid_types)}'
            }), 400
        
        # Generate summary
        summary = summarizer_service.summarize(
            text=transcript,
            summary_type=summary_type,
            chunk_size=chunk_size,
            max_tokens=max_tokens
        )
        
        # Calculate statistics
        summary_word_count = len(summary.split())
        original_word_count = len(transcript.split())
        compression_ratio = (summary_word_count / original_word_count) * 100
        reading_time = max(1, summary_word_count // 200)  # ~200 words per minute
        return jsonify({
            'success': True,
            'summary': summary,
            'statistics': {
                'original_word_count': original_word_count,
                'summary_word_count': summary_word_count,
                'compression_ratio': round(compression_ratio, 1),
                'reading_time_minutes': reading_time
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Summarization failed',
            'message': str(e)
        }), 500

@app.route('/api/process', methods=['POST'])
def process_video():
    """
    Full pipeline: Extract transcript and generate summary in one call
    Request body: {
        "url": "youtube_url",
        "summary_type": "general|detailed|bullet_points|key_takeaways",
        "chunk_size": 2500 (optional),
        "max_tokens": 500 (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'error': 'Missing YouTube URL',
                'message': 'Please provide a valid YouTube URL'
            }), 400
        
        url = data['url']
        summary_type = data.get('summary_type', 'general')
        chunk_size = data.get('chunk_size', 2500)
        max_tokens = data.get('max_tokens', 500)
        
        # Step 1: Extract video ID
        video_id = transcript_service.extract_video_id(url)
        
        # Step 2: Get transcript
        transcript = transcript_service.get_video_transcript(url)
        original_word_count = len(transcript.split())
        
        # Step 3: Generate summary
        summary = summarizer_service.summarize(
            text=transcript,
            summary_type=summary_type,
            chunk_size=chunk_size,
            max_tokens=max_tokens
        )
        
        # Calculate statistics
        summary_word_count = len(summary.split())
        compression_ratio = (summary_word_count / original_word_count) * 100
        reading_time = max(1, summary_word_count // 200)
        
        return jsonify({
            'success': True,
            'video_id': video_id,
            'transcript': transcript,
            'summary': summary,
            'statistics': {
                'original_word_count': original_word_count,
                'summary_word_count': summary_word_count,
                'compression_ratio': round(compression_ratio, 1),
                'reading_time_minutes': reading_time
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'error': 'Invalid URL',
            'message': str(e)
        }), 400
        
    except Exception as e:
        return jsonify({
            'error': 'Processing failed',
            'message': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not found',
        'message': 'The requested endpoint does not exist'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

if __name__ == '__main__':
    # Check if API key is set
    if not os.getenv('GROQ_API_KEY'):
        print("⚠️  Warning: GROQ_API_KEY not found in environment variables")
        print("Please set GROQ_API_KEY in your .env file")
    
    print("🚀 Starting YouTube Summarizer API...")
    print("📡 API available at: http://localhost:5000")
    print("📋 Endpoints:")
    print("   GET  /api/health")
    print("   POST /api/transcript")
    print("   POST /api/summarize")
    print("   POST /api/process")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
