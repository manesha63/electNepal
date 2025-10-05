"""
Admin interface for API Authentication
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import APIKey, APIKeyUsageLog


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    """
    Admin interface for managing API keys
    """
    list_display = [
        'name',
        'organization',
        'contact_email',
        'status_badge',
        'permissions_badge',
        'rate_limit',
        'total_requests',
        'last_used',
        'created_at'
    ]
    list_filter = ['is_active', 'can_read', 'can_write', 'created_at']
    search_fields = ['name', 'organization', 'contact_email', 'key']
    readonly_fields = ['key', 'created_at', 'updated_at', 'total_requests', 'last_used']
    fieldsets = (
        ('Key Information', {
            'fields': ('key', 'name')
        }),
        ('Owner Information', {
            'fields': ('user', 'organization', 'contact_email')
        }),
        ('Permissions', {
            'fields': ('is_active', 'can_read', 'can_write', 'rate_limit', 'expires_at')
        }),
        ('Usage Statistics', {
            'fields': ('total_requests', 'last_used')
        }),
        ('Metadata', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        """Display status with color badge"""
        if obj.is_valid():
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-weight: bold;">Active</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">Inactive</span>'
        )
    status_badge.short_description = 'Status'

    def permissions_badge(self, obj):
        """Display permissions"""
        permissions = []
        if obj.can_read:
            permissions.append('Read')
        if obj.can_write:
            permissions.append('Write')

        color = '#007bff' if obj.can_write else '#6c757d'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            ', '.join(permissions) if permissions else 'None'
        )
    permissions_badge.short_description = 'Permissions'

    def save_model(self, request, obj, form, change):
        """Auto-generate API key if creating new"""
        if not change:  # New object
            if not obj.key:
                obj.key = APIKey.generate_key()
        super().save_model(request, obj, form, change)


@admin.register(APIKeyUsageLog)
class APIKeyUsageLogAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing API usage logs
    """
    list_display = [
        'api_key',
        'endpoint',
        'method',
        'response_status',
        'ip_address',
        'timestamp'
    ]
    list_filter = ['method', 'response_status', 'timestamp']
    search_fields = ['api_key__name', 'endpoint', 'ip_address']
    readonly_fields = [
        'api_key',
        'endpoint',
        'method',
        'ip_address',
        'user_agent',
        'response_status',
        'timestamp'
    ]
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        """Prevent manual creation of logs"""
        return False

    def has_change_permission(self, request, obj=None):
        """Make logs read-only"""
        return False