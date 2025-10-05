"""
Analytics Middleware for tracking page views and visitor statistics
"""
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from .models import PageView, DailyStats, PopularPage
from .utils import get_client_ip, parse_user_agent


class AnalyticsMiddleware(MiddlewareMixin):
    """
    Middleware to track page views and update analytics
    """

    def process_request(self, request):
        """Track page view on each request"""
        # Skip admin, static, media, and API requests
        path = request.path
        if any(path.startswith(prefix) for prefix in ['/admin/', '/static/', '/media/', '/api/', '/jsi18n/']):
            return None

        # Skip non-GET requests
        if request.method != 'GET':
            return None

        try:
            # Get or create session key
            if not request.session.session_key:
                request.session.create()

            session_key = request.session.session_key
            ip_address = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            referer = request.META.get('HTTP_REFERER', '')

            # Parse user agent
            is_mobile, browser = parse_user_agent(user_agent)

            # Create page view record (async in production via Celery)
            PageView.objects.create(
                path=path,
                session_key=session_key,
                ip_address=ip_address,
                user_agent=user_agent[:500],
                referer=referer[:500],
                is_mobile=is_mobile,
                browser=browser
            )

            # Update popular pages (cache for performance)
            self._update_popular_page(path, session_key)

            # Update daily stats (cache for performance)
            self._update_daily_stats(session_key)

        except Exception as e:
            # Don't let analytics errors break the site
            print(f"Analytics error: {e}")
            pass

        return None

    def _update_popular_page(self, path, session_key):
        """Update popular page counter"""
        try:
            # Use get_or_create to handle race conditions
            popular_page, created = PopularPage.objects.get_or_create(
                path=path,
                defaults={'view_count': 0, 'unique_visitor_count': 0}
            )

            # Increment view count
            popular_page.view_count += 1

            # Check if this is a unique visitor (cache session for 1 hour)
            cache_key = f"visitor_{path}_{session_key}"
            if not cache.get(cache_key):
                popular_page.unique_visitor_count += 1
                cache.set(cache_key, True, 3600)

            popular_page.save()
        except Exception:
            pass

    def _update_daily_stats(self, session_key):
        """Update daily statistics"""
        try:
            stats = DailyStats.get_or_create_today()

            # Increment page views
            stats.total_page_views += 1

            # Check if unique visitor (cache for 24 hours)
            cache_key = f"unique_visitor_{session_key}"
            if not cache.get(cache_key):
                stats.unique_visitors += 1
                cache.set(cache_key, True, 86400)

            # Update candidate counts
            from candidates.models import Candidate
            stats.total_candidates = Candidate.objects.count()
            stats.approved_candidates = Candidate.objects.filter(status='approved').count()

            stats.save()
        except Exception:
            pass