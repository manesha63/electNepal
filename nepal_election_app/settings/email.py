"""
Email configuration for ElectNepal
"""

from decouple import config

# Email settings
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

# Production email settings (configure in .env)
if EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
    EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
    DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@electnepal.com')
    CONTACT_EMAIL = 'electnepal5@gmail.com'
else:
    # Development settings
    DEFAULT_FROM_EMAIL = 'dev@electnepal.local'
    CONTACT_EMAIL = 'electnepal5@gmail.com'

# Email subjects prefix
EMAIL_SUBJECT_PREFIX = '[ElectNepal] '

# Admin emails
ADMINS = [
    ('ElectNepal Admin', 'electnepal5@gmail.com'),
]

MANAGERS = ADMINS

# Email verification settings
EMAIL_VERIFICATION_TIMEOUT = 72  # hours
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3