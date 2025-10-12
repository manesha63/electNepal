"""
PostgreSQL configuration for production use
To use this configuration:
1. Install PostgreSQL: sudo apt install postgresql postgresql-contrib
2. Create database: sudo -u postgres createdb electnepal
3. Create user: sudo -u postgres createuser -P electnepal_user
4. Grant privileges: sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE electnepal TO electnepal_user;"
5. Update .env with DATABASE_URL
"""

from .base import *
import dj_database_url
from decouple import config

DEBUG = config('DEBUG', default=False, cast=bool)

# PostgreSQL Configuration
DATABASES = {
    'default': dj_database_url.parse(
        config('DATABASE_URL', 
               default='postgresql://electnepal_user:password@localhost:5432/electnepal')
    )
}

# Alternative explicit configuration
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': config('DB_NAME', default='electnepal'),
#         'USER': config('DB_USER', default='electnepal_user'),
#         'PASSWORD': config('DB_PASSWORD'),
#         'HOST': config('DB_HOST', default='localhost'),
#         'PORT': config('DB_PORT', default='5432'),
#         'OPTIONS': {
#             'connect_timeout': 10,
#         }
#     }
# }

# PostgreSQL-specific optimizations
DATABASES['default']['OPTIONS'] = {
    'connect_timeout': 10,
    'options': '-c statement_timeout=30000'  # 30 seconds
}

# Connection Pooling Configuration for Production
# Persistent connections reduce overhead of creating new connections for each request
DATABASES['default']['CONN_MAX_AGE'] = 600  # Keep connections alive for 10 minutes

# Additional connection settings for production
DATABASES['default']['ATOMIC_REQUESTS'] = False  # Only use transactions when explicitly needed
DATABASES['default']['AUTOCOMMIT'] = True  # PostgreSQL default

# Connection Pool Size Management
# Note: Adjust based on your application's needs and server resources
# Formula: (2 × num_cores) + effective_spindle_count
# For typical web apps with PostgreSQL: 10-20 connections per app instance
# If using external pooler (pgbouncer), these limits are managed there