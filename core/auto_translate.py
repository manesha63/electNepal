"""
Enhanced Automatic Translation System for ElectNepal
Ensures all content is automatically translated without manual intervention
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from googletrans import Translator
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Initialize translator globally
translator = Translator()

class SmartTranslator:
    """
    Smart translation with caching and fallback
    """

    @staticmethod
    def translate(text, src='en', dest='ne'):
        """
        Translate text with caching
        """
        if not text:
            return ""

        # Create cache key
        cache_key = f"trans_{src}_{dest}_{hash(text)}"

        # Check cache first
        cached = cache.get(cache_key)
        if cached:
            return cached

        try:
            # Attempt translation
            result = translator.translate(text, src=src, dest=dest)
            translated = result.text

            # Cache for 30 days
            cache.set(cache_key, translated, 60*60*24*30)

            return translated

        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            # Return original text as fallback
            return text

def auto_translate_model_fields(instance, fields_to_translate):
    """
    Automatically translate specified fields on a model instance
    """
    smart_translator = SmartTranslator()

    for field_base in fields_to_translate:
        en_field = f"{field_base}_en"
        ne_field = f"{field_base}_ne"
        mt_flag = f"is_mt_{field_base}_ne"

        # Check if fields exist on the model
        if not hasattr(instance, en_field) or not hasattr(instance, ne_field):
            continue

        # Get English content
        en_content = getattr(instance, en_field, "")
        ne_content = getattr(instance, ne_field, "")

        # Only translate if English exists and Nepali is empty
        if en_content and not ne_content:
            try:
                # Perform translation
                translated = smart_translator.translate(en_content, 'en', 'ne')
                setattr(instance, ne_field, translated)

                # Set machine translation flag if it exists
                if hasattr(instance, mt_flag):
                    setattr(instance, mt_flag, True)

                logger.info(f"Auto-translated {en_field} for {instance.__class__.__name__} {instance.pk}")

            except Exception as e:
                logger.error(f"Failed to translate {en_field}: {str(e)}")

# Signal handlers for automatic translation
@receiver(pre_save, sender='candidates.Candidate')
def auto_translate_candidate(sender, instance, **kwargs):
    """
    Automatically translate Candidate fields before saving
    """
    fields_to_translate = ['bio', 'education', 'experience', 'manifesto']
    auto_translate_model_fields(instance, fields_to_translate)

@receiver(pre_save, sender='candidates.CandidatePost')
def auto_translate_post(sender, instance, **kwargs):
    """
    Automatically translate CandidatePost fields before saving
    """
    fields_to_translate = ['title', 'content']
    auto_translate_model_fields(instance, fields_to_translate)

@receiver(pre_save, sender='candidates.CandidateEvent')
def auto_translate_event(sender, instance, **kwargs):
    """
    Automatically translate CandidateEvent fields before saving
    """
    fields_to_translate = ['title', 'description', 'location']
    auto_translate_model_fields(instance, fields_to_translate)

# Location model translations
@receiver(post_save, sender='locations.Province')
def ensure_province_translation(sender, instance, created, **kwargs):
    """
    Ensure provinces have Nepali names
    """
    if created or not instance.name_ne:
        smart_translator = SmartTranslator()
        if instance.name_en and not instance.name_ne:
            instance.name_ne = smart_translator.translate(instance.name_en)
            instance.save(update_fields=['name_ne'])

@receiver(post_save, sender='locations.District')
def ensure_district_translation(sender, instance, created, **kwargs):
    """
    Ensure districts have Nepali names
    """
    if created or not instance.name_ne:
        smart_translator = SmartTranslator()
        if instance.name_en and not instance.name_ne:
            instance.name_ne = smart_translator.translate(instance.name_en)
            instance.save(update_fields=['name_ne'])

@receiver(post_save, sender='locations.Municipality')
def ensure_municipality_translation(sender, instance, created, **kwargs):
    """
    Ensure municipalities have Nepali names
    """
    if created or not instance.name_ne:
        smart_translator = SmartTranslator()
        if instance.name_en and not instance.name_ne:
            instance.name_ne = smart_translator.translate(instance.name_en)
            instance.save(update_fields=['name_ne'])

def translate_all_existing_content():
    """
    One-time function to translate all existing content in the database
    """
    from candidates.models import Candidate, CandidatePost, CandidateEvent
    from locations.models import Province, District, Municipality

    smart_translator = SmartTranslator()

    # Translate all candidates
    print("Translating candidates...")
    for candidate in Candidate.objects.all():
        fields = ['bio', 'education', 'experience', 'manifesto']
        auto_translate_model_fields(candidate, fields)
        candidate.save()

    # Translate all posts
    print("Translating posts...")
    for post in CandidatePost.objects.all():
        fields = ['title', 'content']
        auto_translate_model_fields(post, fields)
        post.save()

    # Translate all events
    print("Translating events...")
    for event in CandidateEvent.objects.all():
        fields = ['title', 'description', 'location']
        auto_translate_model_fields(event, fields)
        event.save()

    # Translate all locations
    print("Translating locations...")
    for province in Province.objects.all():
        if province.name_en and not province.name_ne:
            province.name_ne = smart_translator.translate(province.name_en)
            province.save()

    for district in District.objects.all():
        if district.name_en and not district.name_ne:
            district.name_ne = smart_translator.translate(district.name_en)
            district.save()

    for municipality in Municipality.objects.all():
        if municipality.name_en and not municipality.name_ne:
            municipality.name_ne = smart_translator.translate(municipality.name_en)
            municipality.save()

    print("Translation complete!")