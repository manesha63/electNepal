from django.contrib import admin
from django.utils.html import format_html
from .models import Candidate, CandidatePost, CandidateEvent


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'position_level', 'province', 'district',
                    'municipality', 'created_at']
    list_filter = ['position_level', 'province',
                   'district', 'created_at']
    search_fields = ['full_name', 'user__username', 'user__email', 
                     'phone_number', 'constituency_code']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'full_name', 'photo', 'date_of_birth', 'phone_number')
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
