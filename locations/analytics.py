"""
Simple analytics for geolocation tracking
"""
from django.core.cache import cache
from django.utils import timezone
import json


class GeolocationAnalytics:
    """Track geolocation API usage and success rates"""

    @staticmethod
    def track_request(lat, lng, success, province_name=None):
        """Track a geolocation request"""
        # Get current date key
        date_key = timezone.now().strftime('%Y-%m-%d')
        analytics_key = f'geo_analytics:{date_key}'

        # Get current analytics
        analytics = cache.get(analytics_key) or {
            'total_requests': 0,
            'successful': 0,
            'failed': 0,
            'provinces': {}
        }

        # Update counts
        analytics['total_requests'] += 1
        if success:
            analytics['successful'] += 1
            if province_name:
                analytics['provinces'][province_name] = analytics['provinces'].get(province_name, 0) + 1
        else:
            analytics['failed'] += 1

        # Save back to cache (24 hours)
        cache.set(analytics_key, analytics, 86400)

        return analytics

    @staticmethod
    def get_stats(date=None):
        """Get analytics for a specific date or today"""
        if date is None:
            date_key = timezone.now().strftime('%Y-%m-%d')
        else:
            date_key = date.strftime('%Y-%m-%d')

        analytics_key = f'geo_analytics:{date_key}'
        analytics = cache.get(analytics_key) or {
            'total_requests': 0,
            'successful': 0,
            'failed': 0,
            'provinces': {}
        }

        # Calculate success rate
        if analytics['total_requests'] > 0:
            analytics['success_rate'] = (analytics['successful'] / analytics['total_requests']) * 100
        else:
            analytics['success_rate'] = 0

        return analytics

    @staticmethod
    def get_summary():
        """Get a summary of recent analytics"""
        summary = {
            'today': GeolocationAnalytics.get_stats(),
            'total_all_time': 0,
            'success_rate_all_time': 0
        }

        # Aggregate last 30 days
        total_requests = 0
        total_successful = 0

        for i in range(30):
            date = timezone.now() - timezone.timedelta(days=i)
            stats = GeolocationAnalytics.get_stats(date)
            total_requests += stats['total_requests']
            total_successful += stats['successful']

        summary['total_all_time'] = total_requests
        if total_requests > 0:
            summary['success_rate_all_time'] = (total_successful / total_requests) * 100

        return summary