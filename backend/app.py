"""
YouTube Video Summarizer API - Multilingual Edition

Flask backend that provides:
- Multilingual transcript extraction (subtitles + Whisper fallback)
- Translation between English and 10+ Indian languages
- AI-powered summarization using Groq (free API)

All ML models run LOCALLY for FREE:
- Whisper (speech-to-text)
- NLLB-200 (translation)

Only Groq API is used externally (free tier).
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging

from services.transcript import TranscriptService
from services.summarizer import SummarizerService
from config import (
    SUPPORTED_LANGUAGES,
    get_language_name,
    is_english,
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Initialize services (lazy-loaded for heavy models)
transcript_service = TranscriptService()
summarizer_service = SummarizerService()

# Translation service is lazy-loaded to avoid loading 2.4GB model on startup
_translation_service = None

def get_translation_service():
    """Lazy-load the translation service."""
    global _translation_service
    if _translation_service is None:
        from services.translation import TranslationService
        _translation_service = TranslationService()
    return _translation_service


# =============================================================================
# HEALTH & INFO ENDPOINTS
# =============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'YouTube Summarizer API is running',
        'version': '2.0.0',
        'features': ['multilingual', 'whisper', 'translation']
    }), 200


@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get list of supported languages"""
    return jsonify({
        'success': True,
        'languages': SUPPORTED_LANGUAGES
    }), 200


@app.route('/api/warmup', methods=['POST'])
def warmup_models():
    """
    Pre-load ML models to avoid delay on first request.
    This endpoint can take 1-5 minutes depending on download speeds.
    """
    try:
        results = {}
        
        # Optionally warm up translation service
        if request.json and request.json.get('translation', False):
            logger.info("Warming up translation model...")
            translation_service = get_translation_service()
            translation_service.warmup()
            results['translation'] = 'loaded'
        
        # Optionally warm up whisper
        if request.json and request.json.get('whisper', False):
            logger.info("Warming up Whisper model...")
            from services.speech_to_text import SpeechToTextService
            stt = SpeechToTextService()
            stt.warmup()
            results['whisper'] = 'loaded'
        
        return jsonify({
            'success': True,
            'message': 'Models warmed up successfully',
            'models': results
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Warmup failed',
            'message': str(e)
        }), 500


# =============================================================================
# TRANSCRIPT ENDPOINTS
# =============================================================================

@app.route('/api/transcript', methods=['POST'])
def get_transcript():
    """
    Extract transcript from YouTube video (multilingual).
    
    Request body: { 
        "url": "youtube_url",
        "use_whisper": true  // optional, default: true
    }
    
    Response: {
        "success": true,
        "video_id": "xxxxx",
        "transcript": "...",
        "language": "tam",
        "language_name": "Tamil",
        "source": "subtitles" | "whisper",
        "word_count": 1500
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
        use_whisper = data.get('use_whisper', True)
        
        # Extract video ID
        video_id = transcript_service.extract_video_id(url)
        
        # Get transcript (with language detection)
        result = transcript_service.get_video_transcript(url, use_whisper_fallback=use_whisper)
        
        return jsonify({
            'success': True,
            'video_id': video_id,
            'transcript': result['transcript'],
            'language': result['language'],
            'language_name': get_language_name(result['language']),
            'source': result['source'],
            'word_count': result['word_count']
        }), 200
        
    except ValueError as e:
        return jsonify({
            'error': 'Invalid URL',
            'message': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Transcript extraction failed: {e}")
        return jsonify({
            'error': 'Transcript extraction failed',
            'message': str(e)
        }), 500


# =============================================================================
# TRANSLATION ENDPOINTS
# =============================================================================

@app.route('/api/translate', methods=['POST'])
def translate_text():
    """
    Translate text between languages.
    
    Request body: {
        "text": "Hello, how are you?",
        "source_lang": "eng",
        "target_lang": "hin"
    }
    
    Response: {
        "success": true,
        "translated_text": "नमस्ते, आप कैसे हैं?",
        "source_lang": "eng",
        "target_lang": "hin"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'error': 'Missing text',
                'message': 'Please provide text to translate'
            }), 400
        
        text = data['text']
        source_lang = data.get('source_lang', 'eng')
        target_lang = data.get('target_lang', 'hin')
        
        # Get translation service
        translation_service = get_translation_service()
        
        # Translate
        translated = translation_service.translate(text, source_lang, target_lang)
        
        return jsonify({
            'success': True,
            'translated_text': translated,
            'source_lang': source_lang,
            'source_lang_name': get_language_name(source_lang),
            'target_lang': target_lang,
            'target_lang_name': get_language_name(target_lang)
        }), 200
        
    except ValueError as e:
        return jsonify({
            'error': 'Invalid language',
            'message': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        return jsonify({
            'error': 'Translation failed',
            'message': str(e)
        }), 500


@app.route('/api/detect-language', methods=['POST'])
def detect_language():
    """
    Detect the language of given text.
    
    Request body: { "text": "नमस्ते" }
    
    Response: {
        "success": true,
        "language": "hin",
        "language_name": "Hindi"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'error': 'Missing text',
                'message': 'Please provide text for language detection'
            }), 400
        
        text = data['text']
        
        # Get translation service (has language detection)
        translation_service = get_translation_service()
        result = translation_service.detect_language(text)
        
        return jsonify({
            'success': True,
            'language': result['code'],
            'language_name': result['name']
        }), 200
        
    except Exception as e:
        logger.error(f"Language detection failed: {e}")
        return jsonify({
            'error': 'Language detection failed',
            'message': str(e)
        }), 500


# =============================================================================
# SUMMARIZATION ENDPOINTS
# =============================================================================

@app.route('/api/summarize', methods=['POST'])
def summarize():
    """
    Generate summary from transcript.
    
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
        compression_ratio = (summary_word_count / original_word_count) * 100 if original_word_count > 0 else 0
        reading_time = max(1, summary_word_count // 200)
        
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
        logger.error(f"Summarization failed: {e}")
        return jsonify({
            'error': 'Summarization failed',
            'message': str(e)
        }), 500


# =============================================================================
# FULL PIPELINE ENDPOINT
# =============================================================================

@app.route('/api/process', methods=['POST'])
def process_video():
    """
    Full multilingual pipeline: Transcript → Translation → Summary → Translation
    
    Request body: {
        "url": "youtube_url",
        "summary_type": "general|detailed|bullet_points|key_takeaways",
        "target_language": "hin" (optional, for translated summary),
        "chunk_size": 2500 (optional),
        "max_tokens": 500 (optional)
    }
    
    Response: {
        "success": true,
        "video_id": "xxxxx",
        "original_language": "tam",
        "original_language_name": "Tamil",
        "transcript": "...",
        "english_transcript": "..." (if original was non-English),
        "summary": "...",
        "summary_language": "hin",
        "summary_language_name": "Hindi",
        "statistics": {...}
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
        target_language = data.get('target_language', 'eng')  # Default: English summary
        chunk_size = data.get('chunk_size', 2500)
        max_tokens = data.get('max_tokens', 500)
        
        # Step 1: Extract video ID
        video_id = transcript_service.extract_video_id(url)
        logger.info(f"Processing video: {video_id}")
        
        # Step 2: Get transcript with language
        logger.info("Step 1/4: Extracting transcript...")
        transcript_result = transcript_service.get_video_transcript(url, use_whisper_fallback=True)
        
        original_transcript = transcript_result['transcript']
        original_language = transcript_result['language']
        original_word_count = transcript_result['word_count']
        
        logger.info(f"Transcript extracted (language: {original_language})")
        
        # Step 3: Translate to English if needed (for summarization)
        english_transcript = original_transcript
        
        if not is_english(original_language):
            logger.info("Step 2/4: Translating to English for summarization...")
            translation_service = get_translation_service()
            english_transcript = translation_service.translate_to_english(
                original_transcript, 
                original_language
            )
            logger.info("Translation to English complete")
        else:
            logger.info("Step 2/4: Skipped (already English)")
        
        # Step 4: Summarize in English
        logger.info("Step 3/4: Generating summary...")
        summary = summarizer_service.summarize(
            text=english_transcript,
            summary_type=summary_type,
            chunk_size=chunk_size,
            max_tokens=max_tokens
        )
        logger.info("Summary generated")
        
        # Step 5: Translate summary to target language if requested
        final_summary = summary
        summary_language = "eng"
        
        if not is_english(target_language):
            logger.info(f"Step 4/4: Translating summary to {target_language}...")
            translation_service = get_translation_service()
            final_summary = translation_service.translate_from_english(summary, target_language)
            summary_language = target_language
            logger.info("Summary translation complete")
        else:
            logger.info("Step 4/4: Skipped (English output requested)")
        
        # Calculate statistics
        summary_word_count = len(final_summary.split())
        compression_ratio = (summary_word_count / original_word_count) * 100 if original_word_count > 0 else 0
        reading_time = max(1, summary_word_count // 200)
        
        response = {
            'success': True,
            'video_id': video_id,
            'original_language': original_language,
            'original_language_name': get_language_name(original_language),
            'transcript': original_transcript,
            'transcript_source': transcript_result['source'],
            'summary': final_summary,
            'summary_language': summary_language,
            'summary_language_name': get_language_name(summary_language),
            'statistics': {
                'original_word_count': original_word_count,
                'summary_word_count': summary_word_count,
                'compression_ratio': round(compression_ratio, 1),
                'reading_time_minutes': reading_time
            }
        }
        
        # Include English transcript if original was non-English
        if not is_english(original_language):
            response['english_transcript'] = english_transcript
        
        # Include English summary if target was non-English
        if not is_english(target_language):
            response['english_summary'] = summary
        
        logger.info("Processing complete!")
        return jsonify(response), 200
        
    except ValueError as e:
        return jsonify({
            'error': 'Invalid URL',
            'message': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        return jsonify({
            'error': 'Processing failed',
            'message': str(e)
        }), 500


# =============================================================================
# ERROR HANDLERS
# =============================================================================

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


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    # Check if API key is set
    if not os.getenv('GROQ_API_KEY'):
        print("⚠️  Warning: GROQ_API_KEY not found in environment variables")
        print("Please set GROQ_API_KEY in your .env file")
    
    print("🚀 Starting YouTube Summarizer API (Multilingual Edition)...")
    print("📡 API available at: http://localhost:5000")
    print()
    print("📋 Endpoints:")
    print("   GET  /api/health          - Health check")
    print("   GET  /api/languages       - List supported languages")
    print("   POST /api/warmup          - Pre-load ML models")
    print("   POST /api/transcript      - Extract transcript")
    print("   POST /api/translate       - Translate text")
    print("   POST /api/detect-language - Detect language")
    print("   POST /api/summarize       - Summarize transcript")
    print("   POST /api/process         - Full pipeline")
    print()
    print("🌐 Supported Languages: English, Hindi, Tamil, Telugu, Kannada,")
    print("                        Malayalam, Gujarati, Bengali, Marathi,")
    print("                        Punjabi, Urdu")
    print()
    print("💡 Tip: First request may be slow (downloading models ~5GB)")
    print("        Use POST /api/warmup to pre-load models")
    
    app.run(debug=False, host='0.0.0.0', port=5000)
