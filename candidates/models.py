from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.urls import reverse
from locations.models import Province, District, Municipality
from .translation import AutoTranslationMixin


def candidate_photo_path(instance, filename):
    return f'candidates/{instance.user.username}/{filename}'

# Temporary function to fix migration issue - will be removed after migration
def verification_doc_path(instance, filename):
    return f'verification/{instance.user.username}/{filename}'




class Candidate(AutoTranslationMixin, models.Model):
    POSITION_LEVELS = [
        ('ward', 'Ward Representative'),
        ('local_executive', 'Local Executive (Mayor/Chairperson)'),
        ('provincial', 'Provincial Assembly'),
        ('federal', 'Federal Parliament'),
    ]

    # Fields that should be auto-translated
    TRANSLATABLE_FIELDS = ['bio', 'education', 'experience', 'manifesto']
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200, help_text="Full name as it appears on official documents")
    photo = models.ImageField(upload_to=candidate_photo_path, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    bio_en = models.TextField(help_text="Biography in English")
    bio_ne = models.TextField(blank=True, help_text="Biography in Nepali (optional)")
    is_mt_bio_ne = models.BooleanField(default=False, help_text="True if bio_ne is machine translated")

    education_en = models.TextField(blank=True)
    education_ne = models.TextField(blank=True)
    is_mt_education_ne = models.BooleanField(default=False, help_text="True if education_ne is machine translated")

    experience_en = models.TextField(blank=True)
    experience_ne = models.TextField(blank=True)
    is_mt_experience_ne = models.BooleanField(default=False, help_text="True if experience_ne is machine translated")

    manifesto_en = models.TextField(blank=True)
    manifesto_ne = models.TextField(blank=True)
    is_mt_manifesto_ne = models.BooleanField(default=False, help_text="True if manifesto_ne is machine translated")

    position_level = models.CharField(max_length=20, choices=POSITION_LEVELS)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, null=True, blank=True)
    ward_number = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(35)],
        help_text="Ward number (1-35, required for ward-level positions)"
    )
    constituency_code = models.CharField(max_length=50, blank=True)


    website = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    donation_link = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['position_level', 'district']),
            models.Index(fields=['province', 'district', 'municipality']),
            models.Index(fields=['full_name']),
        ]

    def clean(self):
        if self.position_level == 'ward' and not self.ward_number:
            raise ValidationError('Ward number is required for ward-level positions')
        if self.position_level == 'ward' and not self.municipality:
            raise ValidationError('Municipality is required for ward-level positions')
        if self.municipality and self.municipality.district != self.district:
            raise ValidationError('Municipality must belong to the selected district')
        if self.district.province != self.province:
            raise ValidationError('District must belong to the selected province')

    def get_absolute_url(self):
        return reverse('candidates:detail', kwargs={'pk': self.pk})



    def get_display_location(self):
        parts = [self.municipality.name_en if self.municipality else self.district.name_en]
        if self.ward_number:
            parts.append(f"Ward {self.ward_number}")
        parts.append(self.district.name_en)
        parts.append(self.province.name_en)
        return ", ".join(parts)

    def _fill_missing_pair(self, en_field, ne_field, mt_flag_field):
        """
        Auto-translate from English to Nepali if Nepali is empty
        Never overwrites existing Nepali content
        """
        en_value = getattr(self, en_field, "") or ""
        ne_value = getattr(self, ne_field, "") or ""

        # Only translate if English exists and Nepali is empty
        if en_value and not ne_value:
            from core.mt import mt
            translated = mt.translate(en_value, "en", "ne")
            setattr(self, ne_field, translated)
            setattr(self, mt_flag_field, True)

    def autotranslate_missing(self):
        """
        Auto-translate all empty Nepali fields from English
        """
        self._fill_missing_pair("bio_en", "bio_ne", "is_mt_bio_ne")
        self._fill_missing_pair("education_en", "education_ne", "is_mt_education_ne")
        self._fill_missing_pair("experience_en", "experience_ne", "is_mt_experience_ne")
        self._fill_missing_pair("manifesto_en", "manifesto_ne", "is_mt_manifesto_ne")

    def save(self, *args, **kwargs):
        # Auto-translate missing Nepali fields (never overwrites existing)
        self.autotranslate_missing()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.get_position_level_display()})"


class CandidatePost(AutoTranslationMixin, models.Model):
    # Fields that should be auto-translated
    TRANSLATABLE_FIELDS = ['title', 'content']

    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='posts')

    title_en = models.CharField(max_length=200)
    title_ne = models.CharField(max_length=200, blank=True)
    is_mt_title_ne = models.BooleanField(default=False, help_text='True if title_ne is machine translated')

    content_en = models.TextField()
    content_ne = models.TextField(blank=True)
    is_mt_content_ne = models.BooleanField(default=False, help_text='True if content_ne is machine translated')

    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['candidate', '-created_at']),
            models.Index(fields=['is_published', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.candidate.full_name}: {self.title_en}"


class CandidateEvent(AutoTranslationMixin, models.Model):
    # Fields that should be auto-translated
    TRANSLATABLE_FIELDS = ['title', 'description', 'location']

    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='events')

    title_en = models.CharField(max_length=200)
    title_ne = models.CharField(max_length=200, blank=True)
    is_mt_title_ne = models.BooleanField(default=False, help_text='True if title_ne is machine translated')

    description_en = models.TextField()
    description_ne = models.TextField(blank=True)
    is_mt_description_ne = models.BooleanField(default=False, help_text='True if description_ne is machine translated')

    event_date = models.DateTimeField()

    location_en = models.CharField(max_length=200)
    location_ne = models.CharField(max_length=200, blank=True)
    is_mt_location_ne = models.BooleanField(default=False, help_text='True if location_ne is machine translated')

    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['event_date']
        indexes = [
            models.Index(fields=['candidate', 'event_date']),
            models.Index(fields=['is_published', 'event_date']),
        ]
    
    def __str__(self):
        return f"{self.candidate.full_name}: {self.title_en}"