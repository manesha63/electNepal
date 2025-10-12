"""
Automatic translation system for candidate data
Translates all user-generated content to Nepali automatically
"""

from django.db import models
from django.utils.translation import get_language
from googletrans import Translator
import logging

logger = logging.getLogger(__name__)


class AutoTranslationMixin:
    """
    Mixin to automatically translate content fields to Nepali
    """

    # Define which fields should be auto-translated
    TRANSLATABLE_FIELDS = []

    def auto_translate_fields(self):
        """
        Automatically translate English fields to Nepali with specific exception handling
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
                    # Translate to Nepali
                    translation = translator.translate(en_content, src='en', dest='ne')
                    setattr(self, ne_field, translation.text)

                    # Mark as machine translated if flag field exists
                    if hasattr(self, mt_flag):
                        setattr(self, mt_flag, True)

                    logger.info(f"Auto-translated {en_field} to Nepali for {self.__class__.__name__} {self.pk}")

                except (ConnectionError, TimeoutError) as e:
                    # Network-related errors - translation service unavailable
                    logger.warning(f"Translation service unavailable for {en_field}: {str(e)}")
                    # Copy English content as fallback
                    setattr(self, ne_field, en_content)
                    if hasattr(self, mt_flag):
                        setattr(self, mt_flag, False)

                except ValueError as e:
                    # Invalid input or response from translation service
                    logger.error(f"Invalid translation input/response for {en_field}: {str(e)}")
                    setattr(self, ne_field, en_content)
                    if hasattr(self, mt_flag):
                        setattr(self, mt_flag, False)

                except (OSError, IOError) as e:
                    # File/network I/O errors
                    logger.error(f"I/O error during translation of {en_field}: {str(e)}")
                    setattr(self, ne_field, en_content)
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

    @classmethod
    def translate_text(cls, text, target_lang='ne'):
        """
        Translate text to target language with specific exception handling
        """
        if not text:
            return text

        # Check if it's a known political term first
        text_lower = text.lower()
        if text_lower in cls.POLITICAL_TERMS and target_lang == 'ne':
            return cls.POLITICAL_TERMS[text_lower]

        try:
            translator = Translator()
            result = translator.translate(text, dest=target_lang)
            return result.text

        except (ConnectionError, TimeoutError) as e:
            # Network errors - translation service unavailable
            logger.warning(f"Translation service unavailable: {str(e)}")
            return text  # Return original text as fallback

        except ValueError as e:
            # Invalid input or unsupported language
            logger.error(f"Invalid translation request: {str(e)}")
            return text

        except (OSError, IOError) as e:
            # I/O errors during translation
            logger.error(f"I/O error during translation: {str(e)}")
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
        Bulk translate all candidate data with specific exception handling
        """
        from .models import Candidate

        candidates = Candidate.objects.all()
        translator = Translator()

        for candidate in candidates:
            try:
                fields_translated = []

                # Translate bio
                if candidate.bio_en and not candidate.bio_ne:
                    candidate.bio_ne = translator.translate(candidate.bio_en, dest='ne').text
                    candidate.is_mt_bio_ne = True
                    fields_translated.append('bio')

                # Translate education
                if candidate.education_en and not candidate.education_ne:
                    candidate.education_ne = translator.translate(candidate.education_en, dest='ne').text
                    candidate.is_mt_education_ne = True
                    fields_translated.append('education')

                # Translate experience
                if candidate.experience_en and not candidate.experience_ne:
                    candidate.experience_ne = translator.translate(candidate.experience_en, dest='ne').text
                    candidate.is_mt_experience_ne = True
                    fields_translated.append('experience')

                # Translate manifesto
                if candidate.manifesto_en and not candidate.manifesto_ne:
                    candidate.manifesto_ne = translator.translate(candidate.manifesto_en, dest='ne').text
                    candidate.is_mt_manifesto_ne = True
                    fields_translated.append('manifesto')

                if fields_translated:
                    candidate.save()
                    logger.info(f"Translated candidate {candidate.full_name}: {', '.join(fields_translated)}")

            except (ConnectionError, TimeoutError) as e:
                # Network errors - skip this candidate and continue
                logger.warning(f"Translation service unavailable for candidate {candidate.id}: {str(e)}")
                continue

            except ValueError as e:
                # Invalid translation input/response
                logger.error(f"Invalid translation data for candidate {candidate.id}: {str(e)}")
                continue

            except (OSError, IOError) as e:
                # I/O errors
                logger.error(f"I/O error translating candidate {candidate.id}: {str(e)}")
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