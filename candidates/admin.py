from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
import logging
from .models import Candidate, CandidateEvent  # Removed CandidatePost

logger = logging.getLogger(__name__)


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
        (_('Verification Status'), {
            'fields': ('status', 'admin_notes', 'approved_at', 'approved_by'),
            'description': _('Manage the candidate verification status')
        }),
        (_('User Information'), {
            'fields': ('user', 'full_name', 'photo', 'age', 'phone_number')
        }),
        (_('Biography'), {
            'fields': ('bio_en', 'bio_ne'),
            'classes': ('collapse',)
        }),
        (_('Education & Experience'), {
            'fields': ('education_en', 'education_ne', 'experience_en', 'experience_ne',
                      'achievements_en', 'achievements_ne'),
            'classes': ('collapse',)
        }),
        (_('Manifesto'), {
            'fields': ('manifesto_en', 'manifesto_ne'),
            'classes': ('collapse',)
        }),
        (_('Position & Location'), {
            'fields': ('position_level', 'province', 'district', 'municipality',
                      'ward_number', 'constituency_code')
        }),
        (_('Online Presence'), {
            'fields': ('website', 'facebook_url', 'donation_link')
        }),
        (_('Verification Documents (Confidential)'), {
            'fields': ('identity_document', 'candidacy_document', 'terms_accepted'),
            'classes': ('collapse',),
            'description': _('Confidential documents for admin review only - not displayed publicly')
        }),
        (_('Timestamps'), {
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
    get_status_badge.short_description = _('Status')

    def approve_candidates(self, request, queryset):
        """Approve selected candidates"""
        count = 0
        email_sent = 0
        email_failed = 0

        for candidate in queryset.filter(status='pending'):
            candidate.status = 'approved'
            candidate.approved_at = timezone.now()
            candidate.approved_by = request.user
            candidate.save()
            count += 1

            # Send approval email
            try:
                if candidate.send_approval_email():
                    email_sent += 1
                else:
                    email_failed += 1
            except Exception as e:
                email_failed += 1
                logger.error(f"Email error for {candidate.full_name}: {type(e).__name__}: {str(e)}", exc_info=True)

        if count:
            msg = f'{count} candidate(s) approved successfully.'
            if email_sent:
                msg += f' {email_sent} notification email(s) sent.'
            if email_failed:
                msg += f' {email_failed} email(s) failed.'
            self.message_user(request, msg)
        else:
            self.message_user(request, 'No pending candidates to approve.')
    approve_candidates.short_description = _('Approve selected candidates')

    def reject_candidates(self, request, queryset):
        """Reject selected candidates"""
        count = queryset.filter(status='pending').update(status='rejected')
        if count:
            self.message_user(request, f'{count} candidate(s) rejected.')
        else:
            self.message_user(request, 'No pending candidates to reject.')
    reject_candidates.short_description = _('Reject selected candidates')

    def mark_as_pending(self, request, queryset):
        """Mark candidates as pending (for re-review)"""
        count = queryset.update(status='pending', approved_at=None, approved_by=None)
        self.message_user(request, f'{count} candidate(s) marked as pending.')
    mark_as_pending.short_description = _('Mark as pending for review')

    def save_model(self, request, obj, form, change):
        """Override save to handle status changes and send emails"""
        if change and 'status' in form.changed_data:
            old_status = form.initial.get('status')
            new_status = obj.status

            # Handle approval
            if old_status != 'approved' and new_status == 'approved':
                obj.approved_at = timezone.now()
                obj.approved_by = request.user
                # Send approval email
                try:
                    if obj.send_approval_email():
                        messages.success(request, _('Approval email sent to %(email)s') % {'email': obj.user.email})
                    else:
                        messages.warning(request, _('Candidate approved but email notification failed'))
                except Exception as e:
                    messages.warning(request, _('Candidate approved but email failed: %(error)s') % {'error': str(e)})

            # Handle rejection
            elif old_status != 'rejected' and new_status == 'rejected':
                # Clear approval fields
                obj.approved_at = None
                obj.approved_by = None
                # Send rejection email
                try:
                    if obj.send_rejection_email():
                        messages.success(request, _('Rejection email sent to %(email)s') % {'email': obj.user.email})
                    else:
                        messages.warning(request, _('Candidate rejected but email notification failed'))
                except Exception as e:
                    messages.warning(request, _('Candidate rejected but email failed: %(error)s') % {'error': str(e)})

        super().save_model(request, obj, form, change)




# CandidatePost admin removed - candidates can only create events, not posts


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
