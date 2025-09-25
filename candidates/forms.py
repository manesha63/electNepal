from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Candidate, CandidatePost, CandidateEvent


class CandidateRegistrationForm(forms.ModelForm):
    """Form for candidate self-registration"""
    
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    terms_accepted = forms.BooleanField(required=True)
    
    class Meta:
        model = Candidate
        fields = [
            'full_name', 'photo', 'age', 'phone_number',
            'bio_en', 'bio_ne', 'education_en', 'education_ne',
            'experience_en', 'experience_ne', 'manifesto_en', 'manifesto_ne',
            'position_level', 'province', 'district', 'municipality',
            'ward_number', 'constituency_code', 'website', 'facebook_url'
        ]
        widgets = {
            'age': forms.NumberInput(attrs={'min': 18, 'max': 120, 'placeholder': 'Age'}),
            'bio_en': forms.Textarea(attrs={'rows': 4}),
            'bio_ne': forms.Textarea(attrs={'rows': 4}),
            'education_en': forms.Textarea(attrs={'rows': 3}),
            'education_ne': forms.Textarea(attrs={'rows': 3}),
            'experience_en': forms.Textarea(attrs={'rows': 3}),
            'experience_ne': forms.Textarea(attrs={'rows': 3}),
            'manifesto_en': forms.Textarea(attrs={'rows': 5}),
            'manifesto_ne': forms.Textarea(attrs={'rows': 5}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Remove spaces and dashes
            phone = phone.replace(' ', '').replace('-', '')
            # Nepal phone number validation
            if not (phone.startswith('+977') or phone.startswith('977') or phone.startswith('98') or phone.startswith('97')):
                raise ValidationError("Please enter a valid Nepal phone number.")
        return phone
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match.")
        
        # Validate position-specific requirements
        position_level = cleaned_data.get('position_level')
        ward_number = cleaned_data.get('ward_number')
        municipality = cleaned_data.get('municipality')
        
        if position_level == 'ward':
            if not ward_number:
                raise ValidationError("Ward number is required for ward-level positions.")
            if not municipality:
                raise ValidationError("Municipality is required for ward-level positions.")
        
        return cleaned_data
    
    def save(self, commit=True):
        # Create user account
        user = User.objects.create_user(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        
        # Create candidate profile
        candidate = super().save(commit=False)
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


class CandidatePostForm(forms.ModelForm):
    """Form for candidates to create posts"""

    class Meta:
        model = CandidatePost
        fields = ['title_en', 'content_en', 'is_published']
        widgets = {
            'title_en': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'placeholder': 'Post Title'}),
            'content_en': forms.Textarea(attrs={'rows': 8, 'class': 'w-full px-4 py-2 border rounded-lg', 'placeholder': 'Post Content'}),
        }
        labels = {
            'title_en': 'Title (English)',
            'content_en': 'Content (English)',
        }

    def clean_title_en(self):
        title = self.cleaned_data.get('title_en')
        if len(title) < 5:
            raise ValidationError("Title must be at least 5 characters long.")
        return title


class CandidateEventForm(forms.ModelForm):
    """Form for candidates to create events"""

    class Meta:
        model = CandidateEvent
        fields = ['title_en', 'description_en', 'event_date', 'location_en', 'is_published']
        widgets = {
            'title_en': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'placeholder': 'Event Title'}),
            'description_en': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-4 py-2 border rounded-lg'}),
            'event_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full px-4 py-2 border rounded-lg'}),
            'location_en': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'placeholder': 'Event Location'}),
        }
        labels = {
            'title_en': 'Event Title (English)',
            'description_en': 'Description (English)',
            'location_en': 'Location (English)',
        }
    
    def clean_event_date(self):
        from django.utils import timezone
        event_date = self.cleaned_data.get('event_date')
        if event_date and event_date < timezone.now():
            raise ValidationError("Event date cannot be in the past.")
        return event_date