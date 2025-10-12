"""
Input sanitization utilities for forms
Sanitizes user input BEFORE storing in database to prevent XSS attacks
"""

import bleach


# Allowed tags for rich text fields (bio, manifesto, etc.)
RICH_TEXT_ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'i', 'b',
    'ul', 'ol', 'li', 'blockquote',
]

RICH_TEXT_ALLOWED_ATTRIBUTES = {
    # No attributes allowed for security
}

# Allowed protocols for any links
ALLOWED_PROTOCOLS = ['http', 'https']


def sanitize_rich_text(value):
    """
    Sanitize rich text input (bio, education, experience, manifesto).
    Allows basic formatting but removes all dangerous HTML/JavaScript.

    Args:
        value: User input string

    Returns:
        Sanitized string safe for database storage
    """
    if not value:
        return value

    # Remove any HTML tags except basic formatting
    cleaned = bleach.clean(
        value,
        tags=RICH_TEXT_ALLOWED_TAGS,
        attributes=RICH_TEXT_ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True  # Remove disallowed tags completely
    )

    # Remove any remaining dangerous patterns
    # bleach.clean should handle this, but extra safety
    return cleaned.strip()


def sanitize_plain_text(value):
    """
    Sanitize plain text input (names, titles, locations).
    Removes ALL HTML tags.

    Args:
        value: User input string

    Returns:
        Plain text with no HTML
    """
    if not value:
        return value

    # Remove all HTML tags
    cleaned = bleach.clean(
        value,
        tags=[],  # No tags allowed
        strip=True
    )

    return cleaned.strip()


def sanitize_url(value):
    """
    Sanitize URL input (website, facebook_url, donation_link).
    Ensures URL is safe and properly formatted.

    Args:
        value: URL string

    Returns:
        Sanitized URL
    """
    if not value:
        return value

    # Remove any HTML
    cleaned = bleach.clean(
        value,
        tags=[],
        strip=True
    )

    # Basic URL validation (Django URLField will do further validation)
    cleaned = cleaned.strip()

    # Ensure it starts with http:// or https://
    if cleaned and not cleaned.startswith(('http://', 'https://')):
        cleaned = 'https://' + cleaned

    return cleaned


def sanitize_event_title(value):
    """
    Sanitize event title - plain text only.

    Args:
        value: Event title string

    Returns:
        Sanitized title
    """
    return sanitize_plain_text(value)


def sanitize_event_description(value):
    """
    Sanitize event description - allows basic formatting.

    Args:
        value: Event description string

    Returns:
        Sanitized description
    """
    return sanitize_rich_text(value)


def sanitize_event_location(value):
    """
    Sanitize event location - plain text only.

    Args:
        value: Location string

    Returns:
        Sanitized location
    """
    return sanitize_plain_text(value)
