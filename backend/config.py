"""
Configuration module for multilingual YouTube summarizer.
Contains model names, language mappings, and settings.

All models used are FREE and run LOCALLY - no API costs!
"""

import os

# =============================================================================
# MODEL CONFIGURATION
# =============================================================================

# Whisper model for speech-to-text (runs locally)
# Options: "openai/whisper-tiny", "openai/whisper-small", "openai/whisper-medium"
# Smaller = faster but less accurate, larger = slower but more accurate
WHISPER_MODEL = "openai/whisper-small"

# NLLB-200 model for translation (runs locally)
# Using distilled version for lower RAM usage (~2.4GB)
NLLB_MODEL = "facebook/nllb-200-distilled-600M"

# Groq model for summarization (free API)
GROQ_MODEL = "llama-3.1-8b-instant"

# =============================================================================
# LANGUAGE CONFIGURATION
# =============================================================================

# Mapping from simple language codes to NLLB-200 language codes
# NLLB uses format: language_Script (e.g., hin_Deva for Hindi in Devanagari)
LANGUAGE_MAP = {
    # English (including regional variants)
    "eng": {"nllb": "eng_Latn", "name": "English", "script": "Latin"},
    "en": {"nllb": "eng_Latn", "name": "English", "script": "Latin"},
    "en-in": {"nllb": "eng_Latn", "name": "English", "script": "Latin"},
    "en-us": {"nllb": "eng_Latn", "name": "English", "script": "Latin"},
    "en-gb": {"nllb": "eng_Latn", "name": "English", "script": "Latin"},
    "en-au": {"nllb": "eng_Latn", "name": "English", "script": "Latin"},
    "english": {"nllb": "eng_Latn", "name": "English", "script": "Latin"},
    
    # Hindi (including regional variants)
    "hin": {"nllb": "hin_Deva", "name": "Hindi", "script": "Devanagari"},
    "hi": {"nllb": "hin_Deva", "name": "Hindi", "script": "Devanagari"},
    "hi-in": {"nllb": "hin_Deva", "name": "Hindi", "script": "Devanagari"},
    
    # Tamil
    "tam": {"nllb": "tam_Taml", "name": "Tamil", "script": "Tamil"},
    "ta": {"nllb": "tam_Taml", "name": "Tamil", "script": "Tamil"},
    "ta-in": {"nllb": "tam_Taml", "name": "Tamil", "script": "Tamil"},
    
    # Telugu
    "tel": {"nllb": "tel_Telu", "name": "Telugu", "script": "Telugu"},
    "te": {"nllb": "tel_Telu", "name": "Telugu", "script": "Telugu"},
    "te-in": {"nllb": "tel_Telu", "name": "Telugu", "script": "Telugu"},
    
    # Kannada
    "kan": {"nllb": "kan_Knda", "name": "Kannada", "script": "Kannada"},
    "kn": {"nllb": "kan_Knda", "name": "Kannada", "script": "Kannada"},
    "kn-in": {"nllb": "kan_Knda", "name": "Kannada", "script": "Kannada"},
    
    # Malayalam
    "mal": {"nllb": "mal_Mlym", "name": "Malayalam", "script": "Malayalam"},
    "ml": {"nllb": "mal_Mlym", "name": "Malayalam", "script": "Malayalam"},
    "ml-in": {"nllb": "mal_Mlym", "name": "Malayalam", "script": "Malayalam"},
    
    # Gujarati
    "guj": {"nllb": "guj_Gujr", "name": "Gujarati", "script": "Gujarati"},
    "gu": {"nllb": "guj_Gujr", "name": "Gujarati", "script": "Gujarati"},
    "gu-in": {"nllb": "guj_Gujr", "name": "Gujarati", "script": "Gujarati"},
    
    # Bengali
    "ben": {"nllb": "ben_Beng", "name": "Bengali", "script": "Bengali"},
    "bn": {"nllb": "ben_Beng", "name": "Bengali", "script": "Bengali"},
    "bn-in": {"nllb": "ben_Beng", "name": "Bengali", "script": "Bengali"},
    "bn-bd": {"nllb": "ben_Beng", "name": "Bengali", "script": "Bengali"},
    
    # Marathi
    "mar": {"nllb": "mar_Deva", "name": "Marathi", "script": "Devanagari"},
    "mr": {"nllb": "mar_Deva", "name": "Marathi", "script": "Devanagari"},
    "mr-in": {"nllb": "mar_Deva", "name": "Marathi", "script": "Devanagari"},
    
    # Punjabi
    "pan": {"nllb": "pan_Guru", "name": "Punjabi", "script": "Gurmukhi"},
    "pa": {"nllb": "pan_Guru", "name": "Punjabi", "script": "Gurmukhi"},
    "pa-in": {"nllb": "pan_Guru", "name": "Punjabi", "script": "Gurmukhi"},
    
    # Urdu
    "urd": {"nllb": "urd_Arab", "name": "Urdu", "script": "Arabic"},
    "ur": {"nllb": "urd_Arab", "name": "Urdu", "script": "Arabic"},
    "ur-pk": {"nllb": "urd_Arab", "name": "Urdu", "script": "Arabic"},
    "ur-in": {"nllb": "urd_Arab", "name": "Urdu", "script": "Arabic"},
}

# List of supported languages for API responses
SUPPORTED_LANGUAGES = [
    {"code": "eng", "name": "English", "nllb_code": "eng_Latn"},
    {"code": "hin", "name": "Hindi", "nllb_code": "hin_Deva"},
    {"code": "tam", "name": "Tamil", "nllb_code": "tam_Taml"},
    {"code": "tel", "name": "Telugu", "nllb_code": "tel_Telu"},
    {"code": "kan", "name": "Kannada", "nllb_code": "kan_Knda"},
    {"code": "mal", "name": "Malayalam", "nllb_code": "mal_Mlym"},
    {"code": "guj", "name": "Gujarati", "nllb_code": "guj_Gujr"},
    {"code": "ben", "name": "Bengali", "nllb_code": "ben_Beng"},
    {"code": "mar", "name": "Marathi", "nllb_code": "mar_Deva"},
    {"code": "pan", "name": "Punjabi", "nllb_code": "pan_Guru"},
    {"code": "urd", "name": "Urdu", "nllb_code": "urd_Arab"},
]

# Whisper language code to our language code mapping
# Whisper returns ISO 639-1 codes, we normalize to our codes
WHISPER_LANG_MAP = {
    "en": "eng",
    "hi": "hin",
    "ta": "tam",
    "te": "tel",
    "kn": "kan",
    "ml": "mal",
    "gu": "guj",
    "bn": "ben",
    "mr": "mar",
    "pa": "pan",
    "ur": "urd",
}

# =============================================================================
# RUNTIME SETTINGS
# =============================================================================

# Model loading settings
# Set to True to load models on startup (slower startup, faster first request)
# Set to False for lazy loading (faster startup, slower first request)
PRELOAD_MODELS = False

# Maximum text length for translation (to avoid OOM errors)
MAX_TRANSLATION_LENGTH = 5000  # characters

# Audio extraction settings
AUDIO_FORMAT = "wav"
AUDIO_SAMPLE_RATE = 16000  # Whisper expects 16kHz

# Temporary file settings
TEMP_DIR = os.path.join(os.path.dirname(__file__), "temp")

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_nllb_code(lang_code: str) -> str:
    """Convert a language code to NLLB-200 format."""
    lang_code = lang_code.lower().strip()
    if lang_code in LANGUAGE_MAP:
        return LANGUAGE_MAP[lang_code]["nllb"]
    raise ValueError(f"Unsupported language code: {lang_code}")


def get_language_name(lang_code: str) -> str:
    """Get the full name of a language from its code."""
    lang_code = lang_code.lower().strip()
    if lang_code in LANGUAGE_MAP:
        return LANGUAGE_MAP[lang_code]["name"]
    return lang_code


def normalize_whisper_lang(whisper_code: str) -> str:
    """Convert Whisper's language code to our format."""
    whisper_code = whisper_code.lower().strip()
    return WHISPER_LANG_MAP.get(whisper_code, whisper_code)


def is_english(lang_code: str) -> bool:
    """Check if a language code represents English."""
    lang_code = lang_code.lower().strip()
    return lang_code in ["en", "eng", "english", "en-in", "en-us", "en-gb", "en-au"]
