"""
Provider-agnostic Machine Translation Service
Supports Google Cloud Translation, Azure Translator, and LibreTranslate
"""
import hashlib
import os
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class MTClient:
    """
    Unified machine translation client that can swap between providers
    """
    def __init__(self):
        self.engine = getattr(settings, 'MT_ENGINE', 'libre')
        self.client = None
        self.requests = None

        if self.engine == "google":
            try:
                from google.cloud import translate_v2 as translate
                self.client = translate.Client()
                logger.info("Google Cloud Translation client initialized")
            except ImportError:
                logger.warning("Google Cloud Translation library not installed")
                self.engine = "fallback"
            except Exception as e:
                logger.error(f"Failed to initialize Google Translation: {e}")
                self.engine = "fallback"

        elif self.engine in ["azure", "libre"]:
            try:
                import requests
                self.requests = requests
                logger.info(f"{self.engine.title()} translation client initialized")
            except ImportError:
                logger.warning("Requests library not installed")
                self.engine = "fallback"

        if self.engine == "fallback":
            logger.info("Using fallback dictionary translation")

    def translate(self, text, src="en", tgt="ne"):
        """
        Translate text from source to target language

        Args:
            text: Text to translate
            src: Source language code (default: 'en')
            tgt: Target language code (default: 'ne')

        Returns:
            Translated text or original if translation fails
        """
        if not text:
            return ""

        # Generate cache key
        cache_key = f"mt:{self.engine}:{src}:{tgt}:{hashlib.md5(text.encode('utf-8')).hexdigest()}"

        # Check cache first
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        translated = text  # Default fallback

        try:
            if self.engine == "google" and self.client:
                result = self.client.translate(
                    text,
                    source_language=src,
                    target_language=tgt
                )
                translated = result.get("translatedText", text)

            elif self.engine == "azure" and self.requests:
                url = getattr(settings, 'AZURE_MT_ENDPOINT', '')
                key = getattr(settings, 'AZURE_MT_KEY', '')
                region = getattr(settings, 'AZURE_MT_REGION', '')

                if url and key:
                    headers = {
                        "Ocp-Apim-Subscription-Key": key,
                        "Ocp-Apim-Subscription-Region": region,
                        "Content-type": "application/json"
                    }
                    payload = [{"text": text}]
                    response = self.requests.post(
                        f"{url}&from={src}&to={tgt}",
                        json=payload,
                        headers=headers,
                        timeout=15
                    )
                    if response.status_code == 200:
                        translated = response.json()[0]["translations"][0]["text"]

            elif self.engine == "libre" and self.requests:
                url = getattr(settings, 'LIBRE_MT_URL', 'http://localhost:5000/translate')

                try:
                    response = self.requests.post(
                        url,
                        data={"q": text, "source": src, "target": tgt},
                        timeout=15
                    )
                    if response.status_code == 200:
                        translated = response.json().get("translatedText", text)
                except Exception as e:
                    logger.debug(f"LibreTranslate not available: {e}")
                    # Fall through to dictionary translation

            # Fallback to dictionary translation
            if translated == text and src == "en" and tgt == "ne":
                translated = self._dictionary_translate(text)

        except Exception as e:
            logger.error(f"Translation error ({self.engine}): {e}")
            # Use dictionary as ultimate fallback
            if src == "en" and tgt == "ne":
                translated = self._dictionary_translate(text)

        # Cache the result for 30 days
        cache.set(cache_key, translated, 60 * 60 * 24 * 30)
        return translated

    def _dictionary_translate(self, text):
        """
        Simple dictionary-based translation for common terms
        Used as fallback when MT providers are unavailable
        """
        # Simple dictionary for common terms to avoid circular import
        translation_dict = {
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
            "mayor": "मेयर",
            "representative": "प्रतिनिधि",
        }

        # Simple word-by-word translation
        words = text.lower().split()
        translated_words = []
        for word in words:
            translated_words.append(translation_dict.get(word, word))

        return ' '.join(translated_words) if translated_words else text


# Singleton instance
mt = MTClient()