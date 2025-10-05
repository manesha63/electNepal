"""
Custom API Key Authentication for Django REST Framework
"""
from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache
from rest_framework import authentication, exceptions
from .models import APIKey, APIKeyUsageLog


class APIKeyAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication using API keys in the X-API-Key header
    """
    keyword = 'X-API-Key'

    def authenticate(self, request):
        """
        Authenticate the request using API key from header
        Returns tuple of (user, auth) if authenticated, or None
        """
        # Get API key from header
        api_key = self.get_api_key_from_header(request)

        if not api_key:
            # No API key provided - let other auth methods handle it
            return None

        # Check cache first for performance
        cache_key = f"apikey_{api_key}"
        cached_apikey = cache.get(cache_key)

        if cached_apikey == 'invalid':
            raise exceptions.AuthenticationFailed('Invalid API key')

        if cached_apikey:
            apikey_obj = cached_apikey
        else:
            # Validate API key from database
            try:
                apikey_obj = APIKey.objects.select_related('user').get(
                    key=api_key
                )
            except APIKey.DoesNotExist:
                # Cache invalid key for 5 minutes to prevent database hammering
                cache.set(cache_key, 'invalid', 300)
                raise exceptions.AuthenticationFailed('Invalid API key')

            # Cache valid key for 5 minutes
            cache.set(cache_key, apikey_obj, 300)

        # Check if key is valid
        if not apikey_obj.is_valid():
            raise exceptions.AuthenticationFailed('API key is inactive or expired')

        # Check rate limiting
        if not self.check_rate_limit(apikey_obj):
            raise exceptions.Throttled(detail='Rate limit exceeded')

        # Record usage asynchronously (simplified - in production use Celery)
        self.record_usage(request, apikey_obj)

        # Return user if associated, otherwise None for anonymous API access
        return (apikey_obj.user, apikey_obj)

    def get_api_key_from_header(self, request):
        """
        Extract API key from request header
        """
        return request.META.get('HTTP_X_API_KEY') or request.headers.get('X-API-Key')

    def check_rate_limit(self, apikey_obj):
        """
        Check if API key has exceeded rate limit
        """
        # Use sliding window rate limiting
        now = timezone.now()
        one_hour_ago = now - timedelta(hours=1)

        # Count requests in the last hour
        cache_key = f"rate_{apikey_obj.key}"
        request_count = cache.get(cache_key, 0)

        if request_count >= apikey_obj.rate_limit:
            return False

        # Increment counter
        cache.set(cache_key, request_count + 1, 3600)  # Expire after 1 hour
        return True

    def record_usage(self, request, apikey_obj):
        """
        Record API key usage for analytics
        """
        try:
            # Update last used timestamp
            apikey_obj.record_usage()

            # Get client IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR', '0.0.0.0')

            # Log usage (in production, do this asynchronously)
            APIKeyUsageLog.objects.create(
                api_key=apikey_obj,
                endpoint=request.path,
                method=request.method,
                ip_address=ip,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                response_status=200  # Will be updated by middleware
            )
        except Exception:
            # Don't let logging errors break the request
            pass

    def authenticate_header(self, request):
        """
        Return string to use for WWW-Authenticate header
        """
        return 'API-Key'


class OptionalAPIKeyAuthentication(APIKeyAuthentication):
    """
    Same as APIKeyAuthentication but doesn't fail if no key provided
    Useful for endpoints that work with or without authentication
    """

    def authenticate(self, request):
        """
        Authenticate if API key provided, otherwise return None
        """
        try:
            return super().authenticate(request)
        except exceptions.AuthenticationFailed:
            # If API key is invalid, still fail
            raise
        except Exception:
            # For any other issues, allow anonymous access
            return None