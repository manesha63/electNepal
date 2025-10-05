from django.contrib import admin
from .models import EmailVerification, PasswordResetToken


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_verified', 'created_at', 'verified_at']
    list_filter = ['is_verified', 'created_at', 'verified_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['token', 'created_at', 'verified_at']
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_used', 'created_at', 'used_at']
    list_filter = ['is_used', 'created_at', 'used_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['token', 'created_at', 'used_at']
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')