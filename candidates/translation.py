"""
Automatic translation system for candidate data
Translates all user-generated content to Nepali automatically
"""

from django.db import models
from django.utils.translation import get_language
from googletrans import Translator
import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)


def retry_on_transient_errors(max_attempts=3, initial_delay=1.0, backoff_factor=2.0):
    """
    Decorator to retry translation operations with exponential backoff.

    Retries only on transient network errors (ConnectionError, TimeoutError, OSError/IOError).
    Does NOT retry on permanent errors like ValueError (invalid input).

    Args:
        max_attempts: Maximum number of attempts (default: 3)
        initial_delay: Initial delay in seconds before first retry (default: 1.0s)
        backoff_factor: Multiplier for delay between retries (default: 2.0 = exponential)

    Returns:
        Decorated function that retries on transient errors with exponential backoff
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    # Attempt the translation
                    return func(*args, **kwargs)

                except (ConnectionError, TimeoutError, OSError, IOError) as e:
                    # Transient errors - retry with exponential backoff
                    last_exception = e

                    if attempt < max_attempts:
                        logger.warning(
                            f"Translation attempt {attempt}/{max_attempts} failed with {type(e).__name__}: {str(e)}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
                        delay *= backoff_factor  # Exponential backoff
                    else:
                        # Final attempt failed
                        logger.error(
                            f"Translation failed after {max_attempts} attempts. "
                            f"Final error: {type(e).__name__}: {str(e)}"
                        )
                        raise  # Re-raise the exception after all retries exhausted

                except ValueError as e:
                    # Permanent error (invalid input) - do NOT retry
                    logger.error(f"Translation failed with ValueError (not retrying): {str(e)}")
                    raise  # Re-raise immediately, no retry

                except Exception as e:
                    # Unexpected error - log and re-raise without retry
                    logger.error(f"Unexpected translation error (not retrying): {type(e).__name__}: {str(e)}")
                    raise

            # This should never be reached, but just in case
            if last_exception:
                raise last_exception

        return wrapper
    return decorator


class AutoTranslationMixin:
    """
    Mixin to automatically translate content fields to Nepali
    """

    # Define which fields should be auto-translated
    TRANSLATABLE_FIELDS = []

    @staticmethod
    @retry_on_transient_errors(max_attempts=3, initial_delay=1.0, backoff_factor=2.0)
    def _translate_with_retry(translator, text, src='en', dest='ne'):
        """
        Internal helper to perform translation with retry logic.
        Wrapped with retry decorator for transient error handling.
        """
        return translator.translate(text, src=src, dest=dest)

    def auto_translate_fields(self):
        """
        Automatically translate English fields to Nepali with retry logic and exception handling
        """
        translator = Translator()

        for field_base in self.TRANSLATABLE_FIELDS:
            en_field = f"{field_base}_en"
            ne_field = f"{field_base}_ne"
            mt_flag = f"is_mt_{field_base}_ne"

            # Get English content
            en_content = getattr(self, en_field, None)

            # Only translate if English content exists and Nepali is empty
            if en_content and not getattr(self, ne_field, None):
                try:
                    # Translate to Nepali with automatic retry on transient errors
                    translation = self._translate_with_retry(translator, en_content, src='en', dest='ne')
                    setattr(self, ne_field, translation.text)

                    # Mark as machine translated if flag field exists
                    if hasattr(self, mt_flag):
                        setattr(self, mt_flag, True)

                    logger.info(f"Auto-translated {en_field} to Nepali for {self.__class__.__name__} {self.pk}")

                except (ConnectionError, TimeoutError, OSError, IOError) as e:
                    # Network-related errors - translation service unavailable after all retries
                    logger.warning(f"Translation service unavailable for {en_field} after retries: {str(e)}")
                    # Leave Nepali field empty - DO NOT copy English
                    # This allows the bilingual system to retry translation later
                    # and maintains data integrity (no English in Nepali fields)
                    if hasattr(self, mt_flag):
                        setattr(self, mt_flag, False)

                except ValueError as e:
                    # Invalid input or response from translation service (not retried)
                    logger.error(f"Invalid translation input/response for {en_field}: {str(e)}")
                    # Leave Nepali field empty - DO NOT copy English
                    # This allows the bilingual system to retry translation later
                    if hasattr(self, mt_flag):
                        setattr(self, mt_flag, False)

    def save(self, *args, **kwargs):
        """
        Override save to auto-translate before saving
        """
        # Auto-translate fields if creating or updating
        if hasattr(self, 'autotranslate_missing'):
            # Use the model's custom method if it exists (for Candidate model)
            self.autotranslate_missing()
        else:
            # Use the default auto-translation method
            self.auto_translate_fields()

        # Call the parent save method
        super().save(*args, **kwargs)


class TranslationService:
    """
    Service for handling all translation needs
    """

    # Political/Administrative terminology dictionary
    POLITICAL_TERMS = {
        'candidate': 'उम्मेदवार',
        'independent': 'स्वतन्त्र',
        'election': 'निर्वाचन',
        'vote': 'मत',
        'voter': 'मतदाता',
        'ballot': 'मतपत्र',
        'constituency': 'निर्वाचन क्षेत्र',
        'ward': 'वडा',
        'municipality': 'नगरपालिका',
        'district': 'जिल्ला',
        'province': 'प्रदेश',
        'federal': 'संघीय',
        'local': 'स्थानीय',
        'provincial': 'प्रादेशिक',
        'manifesto': 'घोषणापत्र',
        'campaign': 'अभियान',
        'democracy': 'लोकतन्त्र',
        'party': 'पार्टी',
        'seat': 'सिट',
        'assembly': 'सभा',
        'parliament': 'संसद',
        'mayor': 'मेयर',
        'deputy mayor': 'उप-मेयर',
        'chairperson': 'अध्यक्ष',
        'vice chairperson': 'उपाध्यक्ष',
        'member': 'सदस्य',
        'representative': 'प्रतिनिधि',
        'verified': 'प्रमाणित',
        'pending': 'पर्खाइमा',
        'rejected': 'अस्वीकृत',
        'profile': 'प्रोफाइल',
        'biography': 'जीवनी',
        'education': 'शिक्षा',
        'experience': 'अनुभव',
        'contact': 'सम्पर्क',
        'address': 'ठेगाना',
        'phone': 'फोन',
        'email': 'इमेल',
        'website': 'वेबसाइट',
        'social media': 'सामाजिक सञ्जाल',
        'facebook': 'फेसबुक',
        'twitter': 'ट्विटर',
        'donation': 'चन्दा',
        'support': 'समर्थन',
        'register': 'दर्ता',
        'login': 'लगइन',
        'logout': 'लगआउट',
        'search': 'खोज',
        'filter': 'फिल्टर',
        'clear': 'खाली गर्नुहोस्',
        'submit': 'पेश गर्नुहोस्',
        'cancel': 'रद्द गर्नुहोस्',
        'save': 'सुरक्षित गर्नुहोस्',
        'edit': 'सम्पादन',
        'delete': 'मेटाउनुहोस्',
        'view': 'हेर्नुहोस्',
        'share': 'साझा गर्नुहोस्',
        'like': 'मन पराउनुहोस्',
        'comment': 'टिप्पणी',
        'follow': 'फलो गर्नुहोस्',
        'unfollow': 'अनफलो गर्नुहोस्',
        'notification': 'सूचना',
        'settings': 'सेटिङ्गहरू',
        'privacy': 'गोपनीयता',
        'terms': 'सर्तहरू',
        'about': 'बारेमा',
        'help': 'मद्दत',
        'faq': 'बारम्बार सोधिने प्रश्नहरू',
        'contact us': 'हामीलाई सम्पर्क गर्नुहोस्',
    }

    @staticmethod
    @retry_on_transient_errors(max_attempts=3, initial_delay=1.0, backoff_factor=2.0)
    def _perform_translation(translator, text, dest):
        """
        Internal helper to perform translation with retry logic.
        Wrapped with retry decorator for transient error handling.
        """
        return translator.translate(text, dest=dest)

    @classmethod
    def translate_text(cls, text, target_lang='ne'):
        """
        Translate text to target language with retry logic and exception handling
        """
        if not text:
            return text

        # Check if it's a known political term first
        text_lower = text.lower()
        if text_lower in cls.POLITICAL_TERMS and target_lang == 'ne':
            return cls.POLITICAL_TERMS[text_lower]

        try:
            translator = Translator()
            # Use retry-wrapped translation method
            result = cls._perform_translation(translator, text, dest=target_lang)
            return result.text

        except (ConnectionError, TimeoutError, OSError, IOError) as e:
            # Network errors - translation service unavailable after all retries
            logger.warning(f"Translation service unavailable after retries: {str(e)}")
            return text  # Return original text as fallback

        except ValueError as e:
            # Invalid input or unsupported language (not retried)
            logger.error(f"Invalid translation request: {str(e)}")
            return text

    @classmethod
    def get_display_text(cls, obj, field_name):
        """
        Get the appropriate text based on current language
        """
        current_lang = get_language()

        # Try to get localized field first
        if current_lang == 'ne':
            ne_field = f"{field_name}_ne"
            if hasattr(obj, ne_field):
                ne_value = getattr(obj, ne_field)
                if ne_value:
                    return ne_value

        # Fall back to English
        en_field = f"{field_name}_en"
        if hasattr(obj, en_field):
            return getattr(obj, en_field, "")

        # Try without language suffix
        if hasattr(obj, field_name):
            return getattr(obj, field_name, "")

        return ""

    @classmethod
    def bulk_translate_candidates(cls):
        """
        Bulk translate all candidate data with retry logic and exception handling
        """
        from .models import Candidate

        candidates = Candidate.objects.all().select_related('province', 'district', 'municipality')
        translator = Translator()

        for candidate in candidates:
            try:
                fields_translated = []

                # Translate bio with retry
                if candidate.bio_en and not candidate.bio_ne:
                    result = cls._perform_translation(translator, candidate.bio_en, dest='ne')
                    candidate.bio_ne = result.text
                    candidate.is_mt_bio_ne = True
                    fields_translated.append('bio')

                # Translate education with retry
                if candidate.education_en and not candidate.education_ne:
                    result = cls._perform_translation(translator, candidate.education_en, dest='ne')
                    candidate.education_ne = result.text
                    candidate.is_mt_education_ne = True
                    fields_translated.append('education')

                # Translate experience with retry
                if candidate.experience_en and not candidate.experience_ne:
                    result = cls._perform_translation(translator, candidate.experience_en, dest='ne')
                    candidate.experience_ne = result.text
                    candidate.is_mt_experience_ne = True
                    fields_translated.append('experience')

                # Translate manifesto with retry
                if candidate.manifesto_en and not candidate.manifesto_ne:
                    result = cls._perform_translation(translator, candidate.manifesto_en, dest='ne')
                    candidate.manifesto_ne = result.text
                    candidate.is_mt_manifesto_ne = True
                    fields_translated.append('manifesto')

                if fields_translated:
                    candidate.save()
                    logger.info(f"Translated candidate {candidate.full_name}: {', '.join(fields_translated)}")

            except (ConnectionError, TimeoutError, OSError, IOError) as e:
                # Network errors after all retries - skip this candidate and continue
                logger.warning(f"Translation service unavailable for candidate {candidate.id} after retries: {str(e)}")
                continue

            except ValueError as e:
                # Invalid translation input/response (not retried) - skip and continue
                logger.error(f"Invalid translation data for candidate {candidate.id}: {str(e)}")
                continue

            except AttributeError as e:
                # Missing expected field - this is a programming error that should be fixed
                logger.critical(f"Programming error - missing field for candidate {candidate.id}: {str(e)}")
                raise  # Re-raise to alert developers


def get_bilingual_field(obj, field_base):
    """
    Helper function to get field value based on current language
    """
    current_lang = get_language()

    if current_lang == 'ne':
        # Try Nepali field first
        ne_field = f"{field_base}_ne"
        if hasattr(obj, ne_field):
            ne_value = getattr(obj, ne_field)
            if ne_value:
                return ne_value

    # Fall back to English
    en_field = f"{field_base}_en"
    if hasattr(obj, en_field):
        return getattr(obj, en_field, "")

    # Try base field without suffix
    if hasattr(obj, field_base):
        return getattr(obj, field_base, "")

    return ""