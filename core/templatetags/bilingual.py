"""
Template tags for automatic bilingual content display
Usage: {% load bilingual %}
"""

from django import template
from django.utils.translation import get_language
from django.utils.safestring import mark_safe
import json

register = template.Library()


@register.filter(name='bilingual')
def bilingual_field(obj, field_name):
    """
    Automatically get the correct language version of a field
    Usage: {{ candidate|bilingual:'bio' }}
    """
    if not obj or not field_name:
        return ""

    current_lang = get_language()

    # Try language-specific field first
    if current_lang == 'ne':
        ne_field = f"{field_name}_ne"
        if hasattr(obj, ne_field):
            value = getattr(obj, ne_field, None)
            if value:
                return value

    # Fallback to English
    en_field = f"{field_name}_en"
    if hasattr(obj, en_field):
        value = getattr(obj, en_field, None)
        if value:
            return value

    # Try base field without suffix
    if hasattr(obj, field_name):
        return getattr(obj, field_name, "")

    return ""


@register.filter(name='location_name')
def location_name(location):
    """
    Get location name in current language
    Usage: {{ province|location_name }}
    """
    if not location:
        return ""

    current_lang = get_language()

    if current_lang == 'ne' and hasattr(location, 'name_ne'):
        name = location.name_ne
        if name:
            return name

    if hasattr(location, 'name_en'):
        return location.name_en

    if hasattr(location, 'name'):
        return location.name

    return str(location)


@register.simple_tag
def trans_choice(en_text, ne_text):
    """
    Choose between English and Nepali text based on current language
    Usage: {% trans_choice "English text" "नेपाली पाठ" %}
    """
    current_lang = get_language()
    return ne_text if current_lang == 'ne' else en_text


@register.simple_tag
def position_display(position_level):
    """
    Display position level in current language
    Usage: {% position_display candidate.position_level %}
    """
    current_lang = get_language()

    positions = {
        'federal': {
            'en': 'Federal Parliament',
            'ne': 'संघीय संसद'
        },
        'provincial': {
            'en': 'Provincial Assembly',
            'ne': 'प्रदेश सभा'
        },
        'local_executive': {
            'en': 'Local Executive (Mayor/Chairperson)',
            'ne': 'स्थानीय कार्यपालिका (मेयर/अध्यक्ष)'
        },
        'ward': {
            'en': 'Ward Representative',
            'ne': 'वडा प्रतिनिधि'
        }
    }

    position_data = positions.get(position_level, {})
    return position_data.get(current_lang, position_data.get('en', position_level))


@register.simple_tag
def seat_display(position_level):
    """
    Display seat/position in current language
    Usage: {% seat_display candidate.position_level %}
    """
    current_lang = get_language()

    seats = {
        'federal': {
            'en': 'Member of Parliament',
            'ne': 'संसद सदस्य'
        },
        'provincial': {
            'en': 'Provincial Assembly Member',
            'ne': 'प्रदेश सभा सदस्य'
        },
        'local_executive': {
            'en': 'Mayor/Chairperson',
            'ne': 'मेयर/अध्यक्ष'
        },
        'ward': {
            'en': 'Ward Chairperson',
            'ne': 'वडा अध्यक्ष'
        }
    }

    seat_data = seats.get(position_level, {})
    return seat_data.get(current_lang, seat_data.get('en', position_level))


@register.inclusion_tag('core/bilingual_field.html')
def render_bilingual_field(obj, field_name, label=None):
    """
    Render a bilingual field with proper formatting
    Usage: {% render_bilingual_field candidate 'bio' 'Biography' %}
    """
    current_lang = get_language()
    value = bilingual_field(obj, field_name)

    # Check if this is machine translated
    mt_flag = f"is_mt_{field_name}_ne"
    is_mt = False
    if current_lang == 'ne' and hasattr(obj, mt_flag):
        is_mt = getattr(obj, mt_flag, False)

    return {
        'value': value,
        'label': label,
        'is_mt': is_mt,
        'field_name': field_name
    }


@register.filter(name='format_bullets')
def format_bullets(text):
    """
    Format text with bullet points
    Usage: {{ text|format_bullets }}
    """
    if not text:
        return ""

    lines = text.split('\n')
    formatted = []

    for line in lines:
        line = line.strip()
        if line:
            # Add bullet if not already present
            if not line.startswith('•') and not line.startswith('-'):
                if len(line) > 5 and line[0].isalpha():
                    line = f"• {line}"
            formatted.append(line)

    return mark_safe('<br>'.join(formatted))


@register.simple_tag
def bilingual_url(url_name, *args, **kwargs):
    """
    Generate URL with current language prefix
    Usage: {% bilingual_url 'candidate:detail' pk=candidate.pk %}
    """
    from django.urls import reverse
    from django.utils.translation import get_language

    current_lang = get_language()

    # Build the URL
    url = reverse(url_name, args=args, kwargs=kwargs)

    # Add language prefix for Nepali
    if current_lang == 'ne' and not url.startswith('/ne/'):
        url = f'/ne{url}'

    return url


@register.filter
def json_dumps(value):
    """
    Convert Python object to JSON string
    Usage: {{ my_dict|json_dumps }}
    """
    try:
        return mark_safe(json.dumps(value))
    except (TypeError, ValueError):
        return "{}"


@register.simple_tag
def ward_label():
    """
    Get 'Ward' label in current language
    """
    current_lang = get_language()
    return "वडा" if current_lang == 'ne' else "Ward"