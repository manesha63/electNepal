"""
Simple analytics for geolocation tracking with database persistence
"""
from django.utils import timezone
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class GeolocationAnalytics:
    """
    Track geolocation API usage and success rates.
    Uses database for persistence instead of cache.
    """

    @staticmethod
    def track_request(lat, lng, success, province_name=None):
        """
        Track a geolocation request with database persistence.

        Args:
            lat: Latitude coordinate
            lng: Longitude coordinate
            success: Boolean indicating if request was successful
            province_name: Name of province (if successful)

        Returns:
            dict: Current analytics data for the day
        """
        from analytics.models import GeolocationStats

        try:
            # Get today's date
            today = timezone.now().date()

            # Use select_for_update with NOWAIT to prevent race conditions
            # Wrap entire operation in atomic transaction
            with transaction.atomic():
                # First, ensure the record exists (outside of lock to avoid deadlocks)
                # get_or_create is atomic for creation
                stats, created = GeolocationStats.objects.get_or_create(date=today)

                # Now lock it for update
                stats = GeolocationStats.objects.select_for_update().get(date=today)

                # Update counts
                stats.total_requests += 1
                if success:
                    stats.successful += 1
                    if province_name:
                        # Update provinces JSON field
                        provinces = stats.provinces or {}
                        provinces[province_name] = provinces.get(province_name, 0) + 1
                        stats.provinces = provinces
                else:
                    stats.failed += 1

                stats.save()

                # Return analytics data in same format as before
                return {
                    'total_requests': stats.total_requests,
                    'successful': stats.successful,
                    'failed': stats.failed,
                    'provinces': stats.provinces or {}
                }

        except Exception as e:
            logger.error(f"Failed to track geolocation request: {e}")
            # Return empty analytics on error to not break calling code
            return {
                'total_requests': 0,
                'successful': 0,
                'failed': 0,
                'provinces': {}
            }

    @staticmethod
    def get_stats(date=None):
        """
        Get analytics for a specific date or today.

        Args:
            date: datetime.date object or None for today

        Returns:
            dict: Analytics data with success_rate calculated
        """
        from analytics.models import GeolocationStats

        try:
            # Use today if date not provided
            if date is None:
                target_date = timezone.now().date()
            else:
                target_date = date if hasattr(date, 'date') else date

            # Try to get stats from database
            try:
                stats = GeolocationStats.objects.get(date=target_date)
                analytics = {
                    'total_requests': stats.total_requests,
                    'successful': stats.successful,
                    'failed': stats.failed,
                    'provinces': stats.provinces or {},
                    'success_rate': stats.success_rate
                }
            except GeolocationStats.DoesNotExist:
                # Return empty stats if no data for this date
                analytics = {
                    'total_requests': 0,
                    'successful': 0,
                    'failed': 0,
                    'provinces': {},
                    'success_rate': 0
                }

            return analytics

        except Exception as e:
            logger.error(f"Failed to get geolocation stats: {e}")
            return {
                'total_requests': 0,
                'successful': 0,
                'failed': 0,
                'provinces': {},
                'success_rate': 0
            }

    @staticmethod
    def get_summary():
        """
        Get a summary of recent analytics (last 30 days).

        Returns:
            dict: Summary with today's stats and 30-day aggregates
        """
        from analytics.models import GeolocationStats

        try:
            summary = {
                'today': GeolocationAnalytics.get_stats(),
                'total_all_time': 0,
                'success_rate_all_time': 0
            }

            # Aggregate last 30 days from database
            end_date = timezone.now().date()
            start_date = end_date - timezone.timedelta(days=29)

            stats_queryset = GeolocationStats.objects.filter(
                date__gte=start_date,
                date__lte=end_date
            )

            # Calculate totals
            total_requests = sum(s.total_requests for s in stats_queryset)
            total_successful = sum(s.successful for s in stats_queryset)

            summary['total_all_time'] = total_requests
            if total_requests > 0:
                summary['success_rate_all_time'] = (total_successful / total_requests) * 100

            return summary

        except Exception as e:
            logger.error(f"Failed to get geolocation summary: {e}")
            return {
                'today': GeolocationAnalytics.get_stats(),
                'total_all_time': 0,
                'success_rate_all_time': 0
            }