from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Candidate, CandidatePost, CandidateEvent


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'position_level', 'get_status_badge', 'province', 'district',
                    'municipality', 'created_at']
    list_filter = ['status', 'position_level', 'province',
                   'district', 'created_at']
    search_fields = ['full_name', 'user__username', 'user__email',
                     'phone_number', 'constituency_code']
    readonly_fields = ['created_at', 'updated_at', 'approved_at', 'approved_by']
    actions = ['approve_candidates', 'reject_candidates', 'mark_as_pending']

    fieldsets = (
        ('Verification Status', {
            'fields': ('status', 'admin_notes', 'approved_at', 'approved_by'),
            'description': 'Manage the candidate verification status'
        }),
        ('User Information', {
            'fields': ('user', 'full_name', 'photo', 'age', 'phone_number')
        }),
        ('Biography', {
            'fields': ('bio_en', 'bio_ne'),
            'classes': ('collapse',)
        }),
        ('Education & Experience', {
            'fields': ('education_en', 'education_ne', 'experience_en', 'experience_ne'),
            'classes': ('collapse',)
        }),
        ('Manifesto', {
            'fields': ('manifesto_en', 'manifesto_ne'),
            'classes': ('collapse',)
        }),
        ('Position & Location', {
            'fields': ('position_level', 'province', 'district', 'municipality', 
                      'ward_number', 'constituency_code')
        }),
        ('Online Presence', {
            'fields': ('website', 'facebook_url', 'donation_link')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            'pending': '#FFA500',  # Orange
            'approved': '#28A745',  # Green
            'rejected': '#DC3545',  # Red
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6C757D'),
            obj.get_status_display()
        )
    get_status_badge.short_description = 'Status'

    def approve_candidates(self, request, queryset):
        """Approve selected candidates"""
        count = 0
        for candidate in queryset.filter(status='pending'):
            candidate.status = 'approved'
            candidate.approved_at = timezone.now()
            candidate.approved_by = request.user
            candidate.save()
            count += 1

        if count:
            self.message_user(request, f'{count} candidate(s) approved successfully.')
        else:
            self.message_user(request, 'No pending candidates to approve.')
    approve_candidates.short_description = 'Approve selected candidates'

    def reject_candidates(self, request, queryset):
        """Reject selected candidates"""
        count = queryset.filter(status='pending').update(status='rejected')
        if count:
            self.message_user(request, f'{count} candidate(s) rejected.')
        else:
            self.message_user(request, 'No pending candidates to reject.')
    reject_candidates.short_description = 'Reject selected candidates'

    def mark_as_pending(self, request, queryset):
        """Mark candidates as pending (for re-review)"""
        count = queryset.update(status='pending', approved_at=None, approved_by=None)
        self.message_user(request, f'{count} candidate(s) marked as pending.')
    mark_as_pending.short_description = 'Mark as pending for review'




@admin.register(CandidatePost)
class CandidatePostAdmin(admin.ModelAdmin):
    list_display = ['title_en', 'candidate', 'is_published', 'created_at']
    list_filter = ['is_published', 'created_at', 'candidate']
    search_fields = ['title_en', 'title_ne', 'content_en', 'content_ne', 'candidate__full_name']
    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('candidate', 'title_en', 'title_ne', 'content_en', 'content_ne', 'is_published')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CandidateEvent)
class CandidateEventAdmin(admin.ModelAdmin):
    list_display = ['title_en', 'candidate', 'event_date', 'location_en', 'is_published']
    list_filter = ['is_published', 'event_date', 'candidate']
    search_fields = ['title_en', 'title_ne', 'description_en', 'description_ne', 'location_en', 'location_ne', 'candidate__full_name']
    date_hierarchy = 'event_date'

    fieldsets = (
        (None, {
            'fields': ('candidate', 'title_en', 'title_ne', 'description_en', 'description_ne', 'event_date',
                      'location_en', 'location_ne', 'is_published')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at']
