"""
Template filters for sanitizing user-generated content
Prevents XSS attacks while preserving safe formatting
"""

from django import template
from django.utils.safestring import mark_safe
import bleach

register = template.Library()

# Define allowed HTML tags and attributes
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'i', 'b',
    'ul', 'ol', 'li', 'blockquote', 'code', 'pre',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'a', 'span', 'div'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target', 'rel'],
    'span': ['class'],
    'div': ['class'],
}

# Define allowed protocols for links
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']


@register.filter(name='sanitize')
def sanitize_html(value):
    """
    Sanitize HTML content to prevent XSS attacks
    Allows basic formatting tags but strips dangerous content
    """
    if not value:
        return ''

    # Clean the HTML using bleach
    cleaned = bleach.clean(
        value,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True  # Strip disallowed tags instead of escaping
    )

    # Mark as safe for Django template rendering
    return mark_safe(cleaned)


@register.filter(name='sanitize_linebreaks')
def sanitize_linebreaks(value):
    """
    Sanitize content and convert line breaks to <br> tags
    Similar to Django's linebreaksbr but with XSS protection
    """
    if not value:
        return ''

    # First sanitize the content
    cleaned = bleach.clean(
        value,
        tags=[],  # No HTML tags allowed initially
        strip=True
    )

    # Then convert newlines to <br> tags
    # This is safe because we've already sanitized the content
    cleaned = cleaned.replace('\n', '<br>')

    # Clean again with br tags allowed
    cleaned = bleach.clean(
        cleaned,
        tags=['br'],
        strip=True
    )

    return mark_safe(cleaned)


@register.filter(name='sanitize_rich')
def sanitize_rich(value):
    """
    Sanitize content while preserving rich text formatting
    Converts line breaks and allows basic formatting tags
    """
    if not value:
        return ''

    # Replace line breaks with <br> tags before sanitizing
    # This preserves paragraph structure
    value = value.replace('\n\n', '</p><p>')
    value = value.replace('\n', '<br>')
    value = f'<p>{value}</p>' if value and not value.startswith('<p>') else value

    # Clean the HTML with more permissive settings for rich content
    cleaned = bleach.clean(
        value,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True
    )

    return mark_safe(cleaned)


@register.filter(name='sanitize_plain')
def sanitize_plain(value):
    """
    Remove all HTML tags and return plain text
    Useful for displaying user content in contexts where no formatting is desired
    """
    if not value:
        return ''

    # Remove all HTML tags
    cleaned = bleach.clean(
        value,
        tags=[],  # No tags allowed
        strip=True
    )

    return cleaned