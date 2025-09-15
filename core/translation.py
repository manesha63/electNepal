"""
Machine Translation Module for ElectNepal
Provides translation services for candidate content fields
"""

import json
import hashlib
from typing import Optional
from django.core.cache import cache
from django.conf import settings

# For MVP, we'll use a simple translation API or dictionary
# In production, you can integrate Google Cloud Translation, Azure, or LibreTranslate

class TranslationService:
    """
    Translation service for converting between English and Nepali
    """

    def __init__(self):
        # In production, initialize API clients here
        # For now, we'll use a simple dictionary for common translations
        self.translation_dict = {
            # Common political terms
            "candidate": "उम्मेदवार",
            "independent": "स्वतन्त्र",
            "election": "निर्वाचन",
            "vote": "मत",
            "democracy": "लोकतन्त्र",
            "ward": "वडा",
            "municipality": "नगरपालिका",
            "district": "जिल्ला",
            "province": "प्रदेश",
            "federal": "संघीय",
            "parliament": "संसद",
            "assembly": "सभा",
            "representative": "प्रतिनिधि",
            "mayor": "मेयर",
            "chairperson": "अध्यक्ष",
            "deputy": "उप",
            "manifesto": "घोषणापत्र",
            "policy": "नीति",
            "development": "विकास",
            "education": "शिक्षा",
            "health": "स्वास्थ्य",
            "infrastructure": "पूर्वाधार",
            "economy": "अर्थतन्त्र",
            "corruption": "भ्रष्टाचार",
            "transparency": "पारदर्शिता",
            "accountability": "जवाफदेहिता",
            "governance": "शासन",
            "public": "सार्वजनिक",
            "service": "सेवा",
            "community": "समुदाय",
            "youth": "युवा",
            "women": "महिला",
            "employment": "रोजगार",
            "agriculture": "कृषि",
            "tourism": "पर्यटन",
            "environment": "वातावरण",
            "justice": "न्याय",
            "security": "सुरक्षा",
            "peace": "शान्ति",
            "progress": "प्रगति",
            "reform": "सुधार",
            "rights": "अधिकार",
            "citizen": "नागरिक",
            "participation": "सहभागिता",
        }

    def translate_text(self, text: str, source_lang: str = 'en', target_lang: str = 'ne') -> str:
        """
        Translate text from source language to target language

        Args:
            text: Text to translate
            source_lang: Source language code ('en' or 'ne')
            target_lang: Target language code ('en' or 'ne')

        Returns:
            Translated text
        """
        if not text or source_lang == target_lang:
            return text

        # Generate cache key
        cache_key = self._get_cache_key(text, source_lang, target_lang)

        # Check cache first
        cached_translation = cache.get(cache_key)
        if cached_translation:
            return cached_translation

        # Perform translation
        translated = self._perform_translation(text, source_lang, target_lang)

        # Cache the result (expire after 30 days)
        cache.set(cache_key, translated, 60 * 60 * 24 * 30)

        return translated

    def _get_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """Generate a cache key for translation"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return f"translation:{source_lang}:{target_lang}:{text_hash}"

    def _perform_translation(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Perform the actual translation

        In production, this would call Google Cloud Translation, Azure, or LibreTranslate
        For MVP, we'll use a simple dictionary-based approach
        """

        # For demonstration, we'll do simple word replacement
        # In production, use a proper translation API

        if source_lang == 'en' and target_lang == 'ne':
            # English to Nepali
            translated = text
            for eng_word, nep_word in self.translation_dict.items():
                # Case-insensitive replacement
                import re
                pattern = re.compile(re.escape(eng_word), re.IGNORECASE)
                translated = pattern.sub(nep_word, translated)
            return translated

        elif source_lang == 'ne' and target_lang == 'en':
            # Nepali to English (reverse dictionary)
            translated = text
            for eng_word, nep_word in self.translation_dict.items():
                translated = translated.replace(nep_word, eng_word)
            return translated

        return text

    def translate_candidate_fields(self, candidate, force=False):
        """
        Auto-translate missing fields for a candidate

        Args:
            candidate: Candidate model instance
            force: Force translation even if target field is not empty

        Returns:
            Boolean indicating if any fields were updated
        """
        updated = False

        # Translation pairs: (source_field, target_field, source_lang, target_lang)
        translation_pairs = [
            ('bio_en', 'bio_ne', 'en', 'ne'),
            ('education_en', 'education_ne', 'en', 'ne'),
            ('experience_en', 'experience_ne', 'en', 'ne'),
            ('manifesto_en', 'manifesto_ne', 'en', 'ne'),
        ]

        for source_field, target_field, source_lang, target_lang in translation_pairs:
            source_text = getattr(candidate, source_field, '')
            target_text = getattr(candidate, target_field, '')

            # Only translate if source exists and target is empty (or force=True)
            if source_text and (not target_text or force):
                translated = self.translate_text(source_text, source_lang, target_lang)
                setattr(candidate, target_field, translated)

                # Mark as machine translated (if field exists)
                mt_flag_field = f'is_mt_{target_field}'
                if hasattr(candidate, mt_flag_field):
                    setattr(candidate, mt_flag_field, True)

                updated = True

        return updated


# Google Cloud Translation Integration (for production)
class GoogleTranslationService(TranslationService):
    """
    Google Cloud Translation API integration
    Requires: pip install google-cloud-translate
    """

    def __init__(self):
        super().__init__()
        try:
            from google.cloud import translate_v2 as translate
            self.client = translate.Client()
            self.available = True
        except ImportError:
            self.client = None
            self.available = False

    def _perform_translation(self, text: str, source_lang: str, target_lang: str) -> str:
        """Use Google Cloud Translation API"""
        if not self.available or not self.client:
            # Fallback to simple translation
            return super()._perform_translation(text, source_lang, target_lang)

        try:
            result = self.client.translate(
                text,
                source_language=source_lang,
                target_language=target_lang,
                format_='text'
            )
            return result['translatedText']
        except Exception as e:
            print(f"Google Translation API error: {e}")
            # Fallback to simple translation
            return super()._perform_translation(text, source_lang, target_lang)


# LibreTranslate Integration (for self-hosted option)
class LibreTranslateService(TranslationService):
    """
    LibreTranslate API integration (self-hosted or public API)
    """

    def __init__(self, api_url='https://libretranslate.com/translate', api_key=None):
        super().__init__()
        self.api_url = api_url
        self.api_key = api_key

    def _perform_translation(self, text: str, source_lang: str, target_lang: str) -> str:
        """Use LibreTranslate API"""
        import requests

        try:
            payload = {
                'q': text,
                'source': source_lang,
                'target': target_lang,
                'format': 'text'
            }

            if self.api_key:
                payload['api_key'] = self.api_key

            response = requests.post(self.api_url, data=payload, timeout=10)
            response.raise_for_status()

            result = response.json()
            return result.get('translatedText', text)

        except Exception as e:
            print(f"LibreTranslate API error: {e}")
            # Fallback to simple translation
            return super()._perform_translation(text, source_lang, target_lang)


# Factory function to get the appropriate translation service
def get_translation_service():
    """
    Get the configured translation service

    Returns appropriate service based on settings
    """
    # Check settings for which service to use
    service_type = getattr(settings, 'TRANSLATION_SERVICE', 'simple')

    if service_type == 'google':
        return GoogleTranslationService()
    elif service_type == 'libretranslate':
        api_url = getattr(settings, 'LIBRETRANSLATE_URL', 'https://libretranslate.com/translate')
        api_key = getattr(settings, 'LIBRETRANSLATE_API_KEY', None)
        return LibreTranslateService(api_url, api_key)
    else:
        return TranslationService()


# Singleton instance
translation_service = get_translation_service()