"""
CORS (Cross-Origin Resource Sharing) Configuration

Allows API access from external domains/origins.
"""

from decouple import config

# Allow all origins in development, restrict in production
# For production, set CORS_ALLOWED_ORIGINS in .env
if config('DEBUG', default=True, cast=bool):
    # Development: Allow all origins
    CORS_ALLOW_ALL_ORIGINS = True
else:
    # Production: Only allow specific origins
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = config(
        'CORS_ALLOWED_ORIGINS',
        default='http://localhost:3000,http://localhost:8000',
        cast=lambda v: [s.strip() for s in v.split(',')]
    )

# Allow credentials (cookies, authorization headers, etc.)
CORS_ALLOW_CREDENTIALS = True

# Allowed HTTP methods
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Allowed HTTP headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Headers to expose to the browser
CORS_EXPOSE_HEADERS = [
    'content-type',
    'x-csrftoken',
]

# Cache preflight requests for 1 hour
CORS_PREFLIGHT_MAX_AGE = 3600
