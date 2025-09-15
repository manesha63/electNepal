"""
Custom template tags for bilingual content display
"""
from django import template
from django.utils.translation import get_language

register = template.Library()


@register.simple_tag(takes_context=True)
def tdb(context, en_text, ne_text):
    """
    Template tag for bilingual database content
    Usage: {% tdb candidate.bio_en candidate.bio_ne %}

    Args:
        context: Template context (for request)
        en_text: English text
        ne_text: Nepali text

    Returns:
        Appropriate text based on current language
    """
    request = context.get('request')
    lang = getattr(request, 'LANGUAGE_CODE', get_language())

    if lang == 'ne':
        # Prefer Nepali, fall back to English
        return ne_text if ne_text else en_text
    else:
        # Prefer English, fall back to Nepali
        return en_text if en_text else ne_text


@register.simple_tag
def localized_field(obj, field_name):
    """
    Get localized field from an object
    Usage: {% localized_field candidate "bio" %}

    Args:
        obj: Model instance
        field_name: Base field name (without _en/_ne suffix)

    Returns:
        Localized field value
    """
    lang = get_language()

    if lang == 'ne':
        ne_field = f"{field_name}_ne"
        en_field = f"{field_name}_en"
        ne_value = getattr(obj, ne_field, None)
        en_value = getattr(obj, en_field, None)
        return ne_value if ne_value else en_value
    else:
        en_field = f"{field_name}_en"
        ne_field = f"{field_name}_ne"
        en_value = getattr(obj, en_field, None)
        ne_value = getattr(obj, ne_field, None)
        return en_value if en_value else ne_value


@register.simple_tag
def is_mt(obj, field_name):
    """
    Check if a field is machine translated
    Usage: {% is_mt candidate "bio" %}

    Args:
        obj: Model instance
        field_name: Base field name (without _en/_ne suffix)

    Returns:
        Boolean or empty string
    """
    lang = get_language()

    if lang == 'ne':
        mt_field = f"is_mt_{field_name}_ne"
        return getattr(obj, mt_field, False)
    return False


@register.inclusion_tag('core/mt_badge.html')
def mt_badge(obj, field_name):
    """
    Display a badge if content is machine translated
    Usage: {% mt_badge candidate "bio" %}
    """
    is_machine_translated = is_mt(obj, field_name)
    return {
        'is_mt': is_machine_translated,
        'field_name': field_name
    }