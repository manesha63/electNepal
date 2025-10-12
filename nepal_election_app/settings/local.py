from .base import *
from .cors import *
from decouple import config
import dj_database_url

DEBUG = True
# Use PostgreSQL
DATABASES = {
    'default': dj_database_url.parse(
        config('DATABASE_URL',
               default='postgresql://electnepal_user:electnepal123@localhost:5432/electnepal')
    )
}

# Alternative configuration (if dj_database_url doesn't work)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': config('DB_NAME', default='electnepal'),
#         'USER': config('DB_USER', default='electnepal_user'),
#         'PASSWORD': config('DB_PASSWORD', default='electnepal123'),
#         'HOST': config('DB_HOST', default='localhost'),
#         'PORT': config('DB_PORT', default='5432'),
#     }
# }

# Connection Pooling Configuration
# Reuse database connections to improve performance and reduce overhead
DATABASES['default']['CONN_MAX_AGE'] = 600  # Keep connections alive for 10 minutes

# Connection timeout and options
DATABASES['default'].setdefault('OPTIONS', {})
DATABASES['default']['OPTIONS']['connect_timeout'] = 10  # Connection timeout in seconds
DATABASES['default']['OPTIONS']['options'] = '-c statement_timeout=30000'  # 30 seconds for queries

# Connection pool settings (for development)
# These help manage connection lifecycle efficiently
DATABASES['default']['ATOMIC_REQUESTS'] = False  # Only use transactions when explicitly needed
DATABASES['default']['AUTOCOMMIT'] = True  # PostgreSQL default, ensures connections are returned to pool