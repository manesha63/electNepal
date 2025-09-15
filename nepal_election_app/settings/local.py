from .base import *
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