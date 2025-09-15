"""
Internationalization helper functions
"""
from django.utils.translation import get_language


def pick_lang(request, en_text, ne_text):
    """
    Pick the appropriate language text based on current language
    Falls back to other language if preferred is empty

    Args:
        request: Django request object
        en_text: English text
        ne_text: Nepali text

    Returns:
        Appropriate text based on language preference
    """
    lang = getattr(request, "LANGUAGE_CODE", "en")

    if lang == "ne":
        # Prefer Nepali, fall back to English
        return ne_text if ne_text else en_text
    else:
        # Prefer English, fall back to Nepali
        return en_text if en_text else ne_text


def get_localized_field(obj, field_base):
    """
    Get localized field value from an object

    Args:
        obj: Model instance
        field_base: Base field name (e.g., 'bio', 'manifesto')

    Returns:
        Localized field value
    """
    lang = get_language()

    if lang == 'ne':
        ne_value = getattr(obj, f"{field_base}_ne", None)
        en_value = getattr(obj, f"{field_base}_en", None)
        return ne_value if ne_value else en_value
    else:
        en_value = getattr(obj, f"{field_base}_en", None)
        ne_value = getattr(obj, f"{field_base}_ne", None)
        return en_value if en_value else ne_value


def is_machine_translated(obj, field_base):
    """
    Check if a field was machine translated

    Args:
        obj: Model instance
        field_base: Base field name (e.g., 'bio', 'manifesto')

    Returns:
        Boolean indicating if field is machine translated
    """
    lang = get_language()

    if lang == 'ne':
        return getattr(obj, f"is_mt_{field_base}_ne", False)
    else:
        # English fields are never machine translated (always source)
        return False