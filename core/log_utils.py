"""
Logging utilities for sanitizing sensitive data.

This module provides functions to mask/sanitize PII (Personally Identifiable Information)
in log messages to prevent sensitive data exposure while maintaining debugging capability.
"""


def sanitize_email(email):
    """
    Sanitize email address by masking the local part.

    Examples:
        john.doe@example.com -> j***e@example.com
        admin@gmail.com -> a***n@gmail.com
        a@test.com -> a***@test.com

    Args:
        email (str): Email address to sanitize

    Returns:
        str: Sanitized email address with masked local part
    """
    if not email or '@' not in email:
        return "[REDACTED_EMAIL]"

    try:
        local, domain = email.rsplit('@', 1)

        if len(local) <= 2:
            # Very short local part - just show first character
            masked_local = f"{local[0]}***"
        else:
            # Show first and last character, mask the middle
            masked_local = f"{local[0]}***{local[-1]}"

        return f"{masked_local}@{domain}"
    except (IndexError, AttributeError):
        return "[REDACTED_EMAIL]"


def sanitize_username(username):
    """
    Sanitize username by masking most characters.

    Examples:
        johndoe -> j***e
        admin -> a***n
        ab -> a***

    Args:
        username (str): Username to sanitize

    Returns:
        str: Sanitized username with masked characters
    """
    if not username:
        return "[REDACTED_USERNAME]"

    try:
        username = str(username)

        if len(username) <= 2:
            return f"{username[0]}***"
        else:
            return f"{username[0]}***{username[-1]}"
    except (IndexError, AttributeError):
        return "[REDACTED_USERNAME]"


def sanitize_phone(phone):
    """
    Sanitize phone number by masking middle digits.

    Examples:
        +1234567890 -> +123***890
        9851234567 -> 985***567

    Args:
        phone (str): Phone number to sanitize

    Returns:
        str: Sanitized phone number with masked digits
    """
    if not phone:
        return "[REDACTED_PHONE]"

    try:
        phone = str(phone)

        if len(phone) <= 6:
            return f"{phone[:2]}***"
        else:
            # Show first 3 and last 3 digits
            return f"{phone[:3]}***{phone[-3:]}"
    except (IndexError, AttributeError):
        return "[REDACTED_PHONE]"


def get_user_identifier(user):
    """
    Get a safe identifier for logging (user ID + sanitized email/username).

    Args:
        user: Django User object

    Returns:
        str: Safe identifier string like "User(ID:5, email:j***e@example.com)"
    """
    try:
        user_id = getattr(user, 'id', 'N/A')
        email = getattr(user, 'email', None)
        username = getattr(user, 'username', None)

        parts = [f"ID:{user_id}"]

        if email:
            parts.append(f"email:{sanitize_email(email)}")
        elif username:
            parts.append(f"username:{sanitize_username(username)}")

        return f"User({', '.join(parts)})"
    except Exception:
        return "User(UNKNOWN)"
