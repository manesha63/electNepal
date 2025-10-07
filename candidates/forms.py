from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Candidate, CandidateEvent  # CandidatePost removed


class CandidateRegistrationForm(forms.ModelForm):
    """Form for candidate self-registration (for authenticated users)"""

    terms_accepted = forms.BooleanField(required=True)
    photo = forms.ImageField(required=True, help_text=_("Profile photo is required (JPG/PNG, max 5MB)"))

    # Make profile content fields required
    bio_en = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=True)
    education_en = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True)
    experience_en = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True)
    achievements_en = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'placeholder': _('List your key achievements')}), required=True)
    manifesto_en = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), required=True)

    class Meta:
        model = Candidate
        fields = [
            'full_name', 'photo', 'age', 'phone_number',
            'bio_en', 'bio_ne', 'education_en', 'education_ne',
            'experience_en', 'experience_ne', 'achievements_en', 'achievements_ne',
            'manifesto_en', 'manifesto_ne',
            'office', 'position_level', 'province', 'district', 'municipality',
            'ward_number', 'constituency_code', 'website', 'facebook_url',
            'identity_document', 'candidacy_document', 'terms_accepted'
        ]
        labels = {
            'position_level': _('Seat'),  # Rename Position Level to Seat
            'office': _('Office'),
        }
        widgets = {
            'age': forms.NumberInput(attrs={'min': 18, 'max': 120, 'placeholder': _('Age'), 'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'photo': forms.FileInput(attrs={'accept': 'image/jpeg,image/jpg,image/png', 'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'bio_en': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'bio_ne': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'education_en': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'education_ne': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'experience_en': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'experience_ne': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'achievements_en': forms.Textarea(attrs={'rows': 3, 'placeholder': _('List your key achievements'), 'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'achievements_ne': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'manifesto_en': forms.Textarea(attrs={'rows': 5, 'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'manifesto_ne': forms.Textarea(attrs={'rows': 5, 'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'ward_number': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'identity_document': forms.FileInput(attrs={'accept': 'image/*,application/pdf', 'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'candidacy_document': forms.FileInput(attrs={'accept': 'image/*,application/pdf', 'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add responsive classes to all remaining fields not in widgets
        for field_name, field in self.fields.items():
            if field_name not in ['terms_accepted']:  # Skip checkbox
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Remove spaces, dashes, and parentheses
            phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')

            # Remove country code if present
            if phone.startswith('+977'):
                phone = phone[4:]
            elif phone.startswith('977'):
                phone = phone[3:]

            # Validate Nepal phone number format
            # Accepts:
            # 1. Mobile: 10 digits starting with 97, 98, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80
            # 2. Landline: 9-10 digits starting with 01-09 area codes
            import re

            # Mobile pattern: 10 digits starting with 80-98
            mobile_pattern = r'^(9[0-8]|8[0-9])\d{8}$'

            # Landline pattern: area code (01-09) + 5-8 digits (total 7-10 digits)
            # Examples: 01-4123456 (Kathmandu), 021-123456 (Pokhara), 061-123456 (Pokhara old)
            landline_pattern = r'^0[1-9]\d{5,8}$'

            if not (re.match(mobile_pattern, phone) or re.match(landline_pattern, phone)):
                raise ValidationError(
                    _("Please enter a valid Nepal phone number. Mobile: 10 digits starting with 80-98 (e.g., 9812345678). Landline: area code + number (e.g., 014123456)")
                )

            # Return in standard format with country code
            return f"+977{phone}"
        return phone
    
    def clean(self):
        cleaned_data = super().clean()

        # Validate position-specific requirements
        position_level = cleaned_data.get('position_level')
        ward_number = cleaned_data.get('ward_number')
        municipality = cleaned_data.get('municipality')

        # Define position types that require specific location levels
        ward_level_positions = ['ward_chairperson', 'ward_member', 'ward']
        local_level_positions = ['mayor_chairperson', 'deputy_mayor_vice_chairperson', 'municipal', 'local']
        district_level_positions = ['chief_district_coordination', 'deputy_chief_district', 'district']
        provincial_positions = ['provincial_assembly', 'provincial']
        federal_positions = ['house_of_representatives', 'national_assembly', 'federal']

        # Ward-level positions require both municipality and ward
        if position_level in ward_level_positions:
            if not municipality:
                raise ValidationError(_("Municipality is required for ward-level positions."))
            if not ward_number:
                raise ValidationError(_("Ward number is required for ward-level positions."))

        # Local-level positions require municipality but not ward
        elif position_level in local_level_positions:
            if not municipality:
                raise ValidationError(_("Municipality is required for local-level positions."))
            # Ward is optional for local level

        # District, Provincial, and Federal positions don't require municipality or ward
        # But district and province are still required (handled by field required=True)

        return cleaned_data
    
    def save(self, commit=True, user=None):
        # Create candidate profile for authenticated user
        candidate = super().save(commit=False)
        if user:
            candidate.user = user

        if commit:
            candidate.save()

        return candidate


class CandidateUpdateForm(forms.ModelForm):
    """Form for candidates to update their profile"""

    class Meta:
        model = Candidate
        fields = [
            'full_name', 'photo', 'phone_number',
            'bio_en', 'bio_ne', 'education_en', 'education_ne',
            'experience_en', 'experience_ne', 'manifesto_en', 'manifesto_ne',
            'website', 'facebook_url', 'donation_link'
        ]
        widgets = {
            'bio_en': forms.Textarea(attrs={'rows': 4}),
            'bio_ne': forms.Textarea(attrs={'rows': 4}),
            'education_en': forms.Textarea(attrs={'rows': 3}),
            'education_ne': forms.Textarea(attrs={'rows': 3}),
            'experience_en': forms.Textarea(attrs={'rows': 3}),
            'experience_ne': forms.Textarea(attrs={'rows': 3}),
            'manifesto_en': forms.Textarea(attrs={'rows': 5}),
            'manifesto_ne': forms.Textarea(attrs={'rows': 5}),
        }

    def clean(self):
        """
        Clear machine translation flags when user manually edits Nepali fields
        """
        cleaned_data = super().clean()

        # Check each Nepali field - if it has content and changed, it's human-edited
        mt_flag_pairs = [
            ('bio_ne', 'is_mt_bio_ne'),
            ('education_ne', 'is_mt_education_ne'),
            ('experience_ne', 'is_mt_experience_ne'),
            ('manifesto_ne', 'is_mt_manifesto_ne'),
        ]

        for ne_field, mt_flag in mt_flag_pairs:
            if ne_field in self.changed_data and cleaned_data.get(ne_field):
                # User edited this field, clear the MT flag
                cleaned_data[mt_flag] = False

        return cleaned_data


# Posts functionality removed - candidates can only create events
# class CandidatePostForm(forms.ModelForm):
#     """Form for candidates to create posts"""
#
#     class Meta:
#         model = CandidatePost
#         fields = ['title_en', 'content_en', 'is_published']
#         widgets = {
#             'title_en': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'placeholder': _('Post Title')}),
#             'content_en': forms.Textarea(attrs={'rows': 8, 'class': 'w-full px-4 py-2 border rounded-lg', 'placeholder': _('Post Content')}),
#         }
#         labels = {
#             'title_en': _('Title (English)'),
#             'content_en': _('Content (English)'),
#         }
#
#     def clean_title_en(self):
#         title = self.cleaned_data.get('title_en')
#         if len(title) < 5:
#             raise ValidationError(_("Title must be at least 5 characters long."))
#         return title


class CandidateEventForm(forms.ModelForm):
    """Form for candidates to create events"""

    class Meta:
        model = CandidateEvent
        fields = ['title_en', 'description_en', 'event_date', 'location_en', 'is_published']
        widgets = {
            'title_en': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'placeholder': _('Event Title')}),
            'description_en': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-4 py-2 border rounded-lg'}),
            'event_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full px-4 py-2 border rounded-lg'}),
            'location_en': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'placeholder': _('Event Location')}),
        }
        labels = {
            'title_en': _('Event Title (English)'),
            'description_en': _('Description (English)'),
            'location_en': _('Location (English)'),
        }
    
    def clean_event_date(self):
        from django.utils import timezone
        event_date = self.cleaned_data.get('event_date')
        if event_date and event_date < timezone.now():
            raise ValidationError(_("Event date cannot be in the past."))
        return event_date