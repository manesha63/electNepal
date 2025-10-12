"""
Admin interface for Analytics with dashboard and charts
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .models import PageView, DailyStats, CandidateRegistrationEvent, PopularPage, GeolocationStats


class AnalyticsAdminSite(admin.ModelAdmin):
    """Base class for analytics admin"""

    def has_add_permission(self, request):
        """Prevent manual addition"""
        return False

    def has_change_permission(self, request, obj=None):
        """Make read-only"""
        return False


@admin.register(DailyStats)
class DailyStatsAdmin(AnalyticsAdminSite):
    """Admin for daily statistics"""
    list_display = [
        'date',
        'total_page_views',
        'unique_visitors',
        'total_candidates',
        'new_candidates',
        'approved_candidates',
        'top_page_display',
    ]
    list_filter = ['date']
    date_hierarchy = 'date'
    ordering = ['-date']

    def top_page_display(self, obj):
        """Display top page with view count"""
        if obj.top_page:
            return f"{obj.top_page} ({obj.top_page_views} views)"
        return '-'
    top_page_display.short_description = 'Top Page'

    def get_urls(self):
        """Add custom dashboard URL"""
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='analytics_dashboard'),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        """Custom dashboard with charts and graphs"""
        # Get date ranges
        today = timezone.now().date()
        last_7_days = today - timedelta(days=7)
        last_30_days = today - timedelta(days=30)
        last_year = today - timedelta(days=365)

        # Get stats
        stats_7_days = DailyStats.get_date_range_stats(last_7_days, today)
        stats_30_days = DailyStats.get_date_range_stats(last_30_days, today)
        stats_year = DailyStats.get_date_range_stats(last_year, today)

        # Get daily breakdown for charts (last 30 days)
        daily_breakdown = DailyStats.objects.filter(
            date__gte=last_30_days
        ).order_by('date').values('date', 'total_page_views', 'unique_visitors', 'new_candidates')

        # Get popular pages
        popular_pages = PopularPage.objects.all()[:10]

        # Get recent registrations
        recent_registrations = CandidateRegistrationEvent.objects.all()[:10]

        # Browser/Device stats
        total_views_last_30 = PageView.objects.filter(timestamp__gte=timezone.now() - timedelta(days=30))
        mobile_views = total_views_last_30.filter(is_mobile=True).count()
        desktop_views = total_views_last_30.filter(is_mobile=False).count()
        browser_stats = total_views_last_30.values('browser').annotate(count=Count('id')).order_by('-count')[:5]

        context = {
            'title': 'Analytics Dashboard',
            'stats_7_days': stats_7_days,
            'stats_30_days': stats_30_days,
            'stats_year': stats_year,
            'daily_breakdown': list(daily_breakdown),
            'popular_pages': popular_pages,
            'recent_registrations': recent_registrations,
            'mobile_views': mobile_views,
            'desktop_views': desktop_views,
            'browser_stats': list(browser_stats),
        }

        return render(request, 'admin/analytics/dashboard.html', context)


@admin.register(PageView)
class PageViewAdmin(AnalyticsAdminSite):
    """Admin for page views"""
    list_display = ['path', 'session_key_short', 'ip_address', 'browser', 'is_mobile', 'timestamp']
    list_filter = ['is_mobile', 'browser', 'timestamp']
    search_fields = ['path', 'ip_address']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']

    def session_key_short(self, obj):
        """Show shortened session key"""
        return obj.session_key[:10] + '...'
    session_key_short.short_description = 'Session'


@admin.register(CandidateRegistrationEvent)
class CandidateRegistrationEventAdmin(AnalyticsAdminSite):
    """Admin for candidate registration events"""
    list_display = ['full_name', 'position_level', 'province', 'district', 'timestamp']
    list_filter = ['position_level', 'province', 'timestamp']
    search_fields = ['full_name', 'province', 'district']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']


@admin.register(PopularPage)
class PopularPageAdmin(AnalyticsAdminSite):
    """Admin for popular pages"""
    list_display = ['path', 'view_count', 'unique_visitor_count', 'last_viewed']
    ordering = ['-view_count']
    search_fields = ['path']


@admin.register(GeolocationStats)
class GeolocationStatsAdmin(AnalyticsAdminSite):
    """Admin for geolocation statistics"""
    list_display = [
        'date',
        'total_requests',
        'successful',
        'failed',
        'success_rate_display',
        'top_provinces_display'
    ]
    list_filter = ['date']
    date_hierarchy = 'date'
    ordering = ['-date']
    readonly_fields = ['date', 'total_requests', 'successful', 'failed', 'provinces', 'created_at', 'updated_at']

    def success_rate_display(self, obj):
        """Display success rate as percentage"""
        return f"{obj.success_rate:.1f}%"
    success_rate_display.short_description = 'Success Rate'

    def top_provinces_display(self, obj):
        """Display top 3 provinces by request count"""
        if not obj.provinces:
            return '-'
        # Sort provinces by count and get top 3
        sorted_provinces = sorted(obj.provinces.items(), key=lambda x: x[1], reverse=True)[:3]
        return ', '.join([f"{name} ({count})" for name, count in sorted_provinces])
    top_provinces_display.short_description = 'Top Provinces'