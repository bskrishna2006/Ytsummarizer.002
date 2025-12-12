"""
Translation Service using NLLB-200 (Local Model)

This service provides LOCAL translation between English and Indian languages.
NO API CALLS - everything runs on your machine for FREE!

Supported Languages:
- English (eng)
- Hindi (hin)
- Tamil (tam)
- Telugu (tel)
- Kannada (kan)
- Malayalam (mal)
- Gujarati (guj)
- Bengali (ben)
- Marathi (mar)
- Punjabi (pan)
- Urdu (urd)

Model Used: facebook/nllb-200-distilled-600M (~2.4GB)
This is the smallest NLLB model, optimized for lower RAM usage.
"""

import logging
from typing import Optional

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from langdetect import detect, LangDetectException

from config import (
    NLLB_MODEL,
    LANGUAGE_MAP,
    SUPPORTED_LANGUAGES,
    MAX_TRANSLATION_LENGTH,
    get_nllb_code,
    get_language_name,
    is_english,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TranslationService:
    """
    Service for translating text between languages using NLLB-200.
    
    The model is lazily loaded on first use to save memory during startup.
    All processing happens locally - no API costs!
    """
    
    def __init__(self, model_name: str = NLLB_MODEL):
        """
        Initialize the translation service.
        
        Args:
            model_name: Hugging Face model identifier for NLLB-200
        """
        self.model_name = model_name
        self._model = None
        self._tokenizer = None
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"TranslationService initialized (device: {self._device})")
    
    def _load_model(self):
        """
        Load the NLLB-200 model and tokenizer.
        Called lazily on first translation request.
        """
        if self._model is not None:
            return
        
        logger.info(f"Loading NLLB-200 model: {self.model_name}")
        logger.info("This may take a few minutes on first run (downloading ~2.4GB model)...")
        
        try:
            # Load tokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Load model with memory optimizations
            self._model = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32,  # Use float32 for CPU compatibility
                low_cpu_mem_usage=True
            )
            self._model.to(self._device)
            
            logger.info("NLLB-200 model loaded successfully!")
            
        except Exception as e:
            logger.error(f"Failed to load NLLB-200 model: {e}")
            raise Exception(f"Could not load translation model: {str(e)}")
    
    def detect_language(self, text: str) -> dict:
        """
        Detect the language of the given text.
        
        Args:
            text: Text to detect language for
            
        Returns:
            Dictionary with:
                - code: Normalized language code (e.g., "hin")
                - name: Language name (e.g., "Hindi")
                - confidence: Detection confidence (if available)
        """
        try:
            # Use langdetect library
            detected = detect(text)
            
            # Map to our language codes
            lang_mapping = {
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
            
            code = lang_mapping.get(detected, detected)
            name = get_language_name(code)
            
            logger.info(f"Detected language: {name} ({code})")
            
            return {
                "code": code,
                "name": name,
                "raw_code": detected
            }
            
        except LangDetectException as e:
            logger.warning(f"Language detection failed: {e}")
            # Default to English if detection fails
            return {
                "code": "eng",
                "name": "English",
                "raw_code": "en"
            }
    
    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        max_length: int = 1024
    ) -> str:
        """
        Translate text from source language to target language.
        
        Args:
            text: Text to translate
            source_lang: Source language code (e.g., "hin", "eng")
            target_lang: Target language code (e.g., "eng", "tam")
            max_length: Maximum output length
            
        Returns:
            Translated text
            
        Raises:
            ValueError: If language codes are invalid
            Exception: If translation fails
        """
        # Ensure model is loaded
        self._load_model()
        
        # Validate and get NLLB codes
        try:
            source_nllb = get_nllb_code(source_lang)
            target_nllb = get_nllb_code(target_lang)
        except ValueError as e:
            raise ValueError(str(e))
        
        logger.info(f"Translating from {source_lang} to {target_lang}")
        
        # Handle long texts by chunking
        if len(text) > MAX_TRANSLATION_LENGTH:
            logger.info(f"Text too long ({len(text)} chars), chunking...")
            return self._translate_long_text(text, source_lang, target_lang, max_length)
        
        try:
            # Set source language for tokenizer
            self._tokenizer.src_lang = source_nllb
            
            # Tokenize input
            inputs = self._tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=max_length
            )
            inputs = {k: v.to(self._device) for k, v in inputs.items()}
            
            # Get target language token ID
            forced_bos_token_id = self._tokenizer.convert_tokens_to_ids(target_nllb)
            
            # Generate translation
            with torch.no_grad():
                outputs = self._model.generate(
                    **inputs,
                    forced_bos_token_id=forced_bos_token_id,
                    max_length=max_length,
                    num_beams=5,
                    length_penalty=1.0,
                    early_stopping=True
                )
            
            # Decode output
            translated = self._tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
            
            logger.info(f"Translation complete ({len(translated)} chars)")
            
            return translated.strip()
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise Exception(f"Could not translate text: {str(e)}")
    
    def _translate_long_text(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        max_length: int = 1024
    ) -> str:
        """
        Translate long text by splitting into chunks.
        
        Args:
            text: Long text to translate
            source_lang: Source language code
            target_lang: Target language code
            max_length: Maximum output length per chunk
            
        Returns:
            Concatenated translated text
        """
        # Split text into sentences (rough approximation)
        sentences = text.replace("।", ".").replace("॥", ".").split(".")
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if adding this sentence would exceed limit
            if len(current_chunk) + len(sentence) + 2 > MAX_TRANSLATION_LENGTH:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
            else:
                current_chunk = current_chunk + ". " + sentence if current_chunk else sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        
        # Translate each chunk
        translated_chunks = []
        for i, chunk in enumerate(chunks):
            logger.info(f"Translating chunk {i+1}/{len(chunks)}")
            translated = self.translate(chunk, source_lang, target_lang, max_length)
            translated_chunks.append(translated)
        
        return " ".join(translated_chunks)
    
    def translate_to_english(self, text: str, source_lang: str) -> str:
        """
        Convenience method to translate text to English.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            
        Returns:
            English translation
        """
        if is_english(source_lang):
            return text  # Already English
        
        return self.translate(text, source_lang, "eng")
    
    def translate_from_english(self, text: str, target_lang: str) -> str:
        """
        Convenience method to translate English text to another language.
        
        Args:
            text: English text to translate
            target_lang: Target language code
            
        Returns:
            Translated text in target language
        """
        if is_english(target_lang):
            return text  # Already English
        
        return self.translate(text, "eng", target_lang)
    
    def get_supported_languages(self) -> list:
        """
        Get list of supported languages.
        
        Returns:
            List of language dictionaries with code, name, and nllb_code
        """
        return SUPPORTED_LANGUAGES.copy()
    
    def is_model_loaded(self) -> bool:
        """Check if the NLLB model is currently loaded."""
        return self._model is not None
    
    def warmup(self):
        """
        Pre-load the model to avoid delay on first request.
        Call this during application startup if desired.
        """
        logger.info("Warming up TranslationService...")
        self._load_model()
        logger.info("TranslationService warmup complete!")
