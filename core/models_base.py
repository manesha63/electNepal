"""
Base Model Classes for Automatic Bilingual Support
All models in the project should inherit from these base classes
"""

from django.db import models
from django.core.exceptions import ValidationError
from googletrans import Translator
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class BilingualFieldMixin:
    """
    Mixin that automatically handles bilingual fields
    """

    # Override this in your model
    BILINGUAL_FIELDS = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_bilingual_fields()

    def _setup_bilingual_fields(self):
        """
        Dynamically set up bilingual field tracking
        """
        self._bilingual_fields = []

        for field_base in self.BILINGUAL_FIELDS:
            en_field = f"{field_base}_en"
            ne_field = f"{field_base}_ne"

            if hasattr(self, en_field) and hasattr(self, ne_field):
                self._bilingual_fields.append({
                    'base': field_base,
                    'en': en_field,
                    'ne': ne_field,
                    'mt_flag': f"is_mt_{field_base}_ne"
                })

    def translate_field(self, field_base, force=False):
        """
        Translate a single field from English to Nepali
        """
        en_field = f"{field_base}_en"
        ne_field = f"{field_base}_ne"
        mt_flag = f"is_mt_{field_base}_ne"

        en_value = getattr(self, en_field, None)
        ne_value = getattr(self, ne_field, None)

        # Only translate if English exists and (Nepali is empty OR force is True)
        if en_value and (not ne_value or force):
            try:
                # Use cached translator
                translator = CachedTranslator()
                translated = translator.translate(en_value, 'en', 'ne')

                setattr(self, ne_field, translated)

                # Set MT flag if it exists
                if hasattr(self, mt_flag):
                    setattr(self, mt_flag, True)

                logger.info(f"Translated {en_field} for {self.__class__.__name__}")
                return True

            except Exception as e:
                logger.error(f"Translation failed for {en_field}: {str(e)}")
                return False

        return False

    def auto_translate_all(self, force=False):
        """
        Automatically translate all bilingual fields
        """
        for field_info in self._bilingual_fields:
            self.translate_field(field_info['base'], force)

    def clean(self):
        """
        Validate that at least English fields are provided
        """
        super().clean()

        for field_info in self._bilingual_fields:
            en_value = getattr(self, field_info['en'], None)

            # Ensure at least English is provided for required fields
            field_obj = self._meta.get_field(field_info['en'])
            if not field_obj.blank and not field_obj.null and not en_value:
                raise ValidationError({
                    field_info['en']: f"English version of {field_info['base']} is required"
                })

    def save(self, *args, **kwargs):
        """
        Override save to auto-translate before saving
        """
        # Auto-translate all fields
        self.auto_translate_all()

        # Call parent save
        super().save(*args, **kwargs)


class CachedTranslator:
    """
    Singleton translator with caching
    """
    _instance = None
    _translator = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._translator = Translator()
        return cls._instance

    def translate(self, text, src='en', dest='ne'):
        """
        Translate with caching
        """
        if not text:
            return ""

        # Create cache key
        cache_key = f"trans_{src}_{dest}_{hash(text)}"

        # Check cache
        cached = cache.get(cache_key)
        if cached:
            return cached

        try:
            # Perform translation
            result = self._translator.translate(text, src=src, dest=dest)
            translated = result.text

            # Cache for 30 days
            cache.set(cache_key, translated, 60*60*24*30)

            return translated

        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            # Return empty string instead of original to avoid mixing languages
            return ""


class BilingualCharField(models.CharField):
    """
    Custom CharField that automatically creates bilingual versions
    """

    def contribute_to_class(self, cls, name):
        # Create English field
        en_field = models.CharField(
            max_length=self.max_length,
            blank=self.blank,
            null=self.null,
            default=self.default,
            help_text=f"{self.help_text} (English)" if self.help_text else "English version"
        )
        en_field.contribute_to_class(cls, f"{name}_en")

        # Create Nepali field (always optional)
        ne_field = models.CharField(
            max_length=self.max_length,
            blank=True,
            null=True,
            help_text=f"{self.help_text} (Nepali - auto-translated)" if self.help_text else "Nepali version (auto-translated)"
        )
        ne_field.contribute_to_class(cls, f"{name}_ne")

        # Create MT flag field
        mt_field = models.BooleanField(
            default=False,
            help_text=f"True if {name}_ne is machine translated"
        )
        mt_field.contribute_to_class(cls, f"is_mt_{name}_ne")

        # Add to BILINGUAL_FIELDS if not exists
        if not hasattr(cls, 'BILINGUAL_FIELDS'):
            cls.BILINGUAL_FIELDS = []
        if name not in cls.BILINGUAL_FIELDS:
            cls.BILINGUAL_FIELDS.append(name)


class BilingualTextField(models.TextField):
    """
    Custom TextField that automatically creates bilingual versions
    """

    def contribute_to_class(self, cls, name):
        # Create English field
        en_field = models.TextField(
            blank=self.blank,
            null=self.null,
            default=self.default,
            help_text=f"{self.help_text} (English)" if self.help_text else "English version"
        )
        en_field.contribute_to_class(cls, f"{name}_en")

        # Create Nepali field (always optional)
        ne_field = models.TextField(
            blank=True,
            null=True,
            help_text=f"{self.help_text} (Nepali - auto-translated)" if self.help_text else "Nepali version (auto-translated)"
        )
        ne_field.contribute_to_class(cls, f"{name}_ne")

        # Create MT flag field
        mt_field = models.BooleanField(
            default=False,
            help_text=f"True if {name}_ne is machine translated"
        )
        mt_field.contribute_to_class(cls, f"is_mt_{name}_ne")

        # Add to BILINGUAL_FIELDS if not exists
        if not hasattr(cls, 'BILINGUAL_FIELDS'):
            cls.BILINGUAL_FIELDS = []
        if name not in cls.BILINGUAL_FIELDS:
            cls.BILINGUAL_FIELDS.append(name)


class BilingualModel(BilingualFieldMixin, models.Model):
    """
    Abstract base model with bilingual support
    All content models should inherit from this
    """

    class Meta:
        abstract = True

    def get_field_in_language(self, field_base, language_code=None):
        """
        Get field value in specified language with fallback
        """
        if language_code is None:
            from django.utils.translation import get_language
            language_code = get_language()

        # Try to get field in requested language
        if language_code == 'ne':
            ne_field = f"{field_base}_ne"
            if hasattr(self, ne_field):
                ne_value = getattr(self, ne_field, None)
                if ne_value:
                    return ne_value

        # Fallback to English
        en_field = f"{field_base}_en"
        if hasattr(self, en_field):
            return getattr(self, en_field, "")

        # Last resort - try base field
        if hasattr(self, field_base):
            return getattr(self, field_base, "")

        return ""

    def get_display_dict(self, language_code=None):
        """
        Get all bilingual fields in the current language
        """
        result = {}

        for field_info in self._bilingual_fields:
            result[field_info['base']] = self.get_field_in_language(
                field_info['base'],
                language_code
            )

        return result


class TimestampedBilingualModel(BilingualModel):
    """
    Base model with timestamps and bilingual support
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']