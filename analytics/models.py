"""
Analytics Models for tracking website usage and statistics
"""
from django.db import models
from django.utils import timezone
from datetime import timedelta


class PageView(models.Model):
    """Track individual page views"""
    path = models.CharField(max_length=500)
    session_key = models.CharField(max_length=100, db_index=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    referer = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    # Device/Browser info (parsed from user agent)
    is_mobile = models.BooleanField(default=False)
    browser = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp', 'path']),
            models.Index(fields=['session_key', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.path} at {self.timestamp}"


class DailyStats(models.Model):
    """Aggregated daily statistics"""
    date = models.DateField(unique=True, db_index=True)

    # Visitor metrics
    total_page_views = models.IntegerField(default=0)
    unique_visitors = models.IntegerField(default=0)

    # Candidate metrics
    total_candidates = models.IntegerField(default=0)
    new_candidates = models.IntegerField(default=0)
    approved_candidates = models.IntegerField(default=0)

    # Engagement metrics
    avg_session_duration = models.FloatField(default=0)  # in seconds
    bounce_rate = models.FloatField(default=0)  # percentage

    # Top pages
    top_page = models.CharField(max_length=500, blank=True)
    top_page_views = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Daily Statistics'

    def __str__(self):
        return f"Stats for {self.date}"

    @classmethod
    def get_or_create_today(cls):
        """Get or create stats for today"""
        today = timezone.now().date()
        stats, created = cls.objects.get_or_create(date=today)
        return stats

    @classmethod
    def get_date_range_stats(cls, start_date, end_date):
        """Get aggregated stats for date range"""
        stats = cls.objects.filter(date__gte=start_date, date__lte=end_date)
        return {
            'total_page_views': sum(s.total_page_views for s in stats),
            'avg_unique_visitors': int(sum(s.unique_visitors for s in stats) / max(len(stats), 1)),
            'total_new_candidates': sum(s.new_candidates for s in stats),
            'total_approved_candidates': sum(s.approved_candidates for s in stats),
        }


class CandidateRegistrationEvent(models.Model):
    """Track candidate registration events"""
    candidate_id = models.IntegerField()
    full_name = models.CharField(max_length=200)
    position_level = models.CharField(max_length=50)
    province = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Candidate Registration Event'

    def __str__(self):
        return f"{self.full_name} registered on {self.timestamp.date()}"


class PopularPage(models.Model):
    """Track popular pages over time"""
    path = models.CharField(max_length=500, unique=True)
    view_count = models.IntegerField(default=0)
    unique_visitor_count = models.IntegerField(default=0)
    last_viewed = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-view_count']

    def __str__(self):
        return f"{self.path} ({self.view_count} views)"


class GeolocationStats(models.Model):
    """
    Track geolocation API usage statistics per day.
    Replaces cache-based analytics with persistent database storage.
    """
    date = models.DateField(unique=True, db_index=True)

    # Request metrics
    total_requests = models.IntegerField(default=0)
    successful = models.IntegerField(default=0)
    failed = models.IntegerField(default=0)

    # Province breakdown (stored as JSON)
    provinces = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Geolocation Statistics'
        verbose_name_plural = 'Geolocation Statistics'
        indexes = [
            models.Index(fields=['date', 'total_requests']),
        ]

    def __str__(self):
        return f"Geolocation stats for {self.date} ({self.total_requests} requests)"

    @property
    def success_rate(self):
        """Calculate success rate percentage"""
        if self.total_requests > 0:
            return (self.successful / self.total_requests) * 100
        return 0

    @classmethod
    def get_or_create_for_date(cls, date):
        """Get or create stats for a specific date"""
        stats, created = cls.objects.get_or_create(date=date)
        return stats