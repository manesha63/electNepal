from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.core.mail import send_mail, mail_admins
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from locations.models import Province, District, Municipality
from .translation import AutoTranslationMixin
import logging

# Get logger for email operations
logger = logging.getLogger('candidates.emails')


def candidate_photo_path(instance, filename):
    return f'candidates/{instance.user.username}/{filename}'

# Temporary function to fix migration issue - will be removed after migration
def verification_doc_path(instance, filename):
    return f'verification/{instance.user.username}/{filename}'




class Candidate(AutoTranslationMixin, models.Model):
    POSITION_LEVELS = [
        # Ward Level
        ('ward_chairperson', 'Ward Chairperson'),
        ('ward_member', 'Ward Member'),

        # Local Unit Level (Municipality/Rural Municipality/Metropolitan/Sub-Metropolitan)
        ('mayor_chairperson', 'Mayor/Chairperson'),
        ('deputy_mayor_vice_chairperson', 'Deputy Mayor/Vice Chairperson'),

        # Provincial Level
        ('provincial_assembly', 'Provincial Assembly Member'),

        # Federal Level
        ('house_of_representatives', 'House of Representatives Member'),
        ('national_assembly', 'National Assembly Member'),
    ]

    OFFICE_CHOICES = [
        ('federal', 'Federal'),
        ('provincial', 'Provincial'),
        ('municipal', 'Municipal'),
        ('ward', 'Ward'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    # Fields that should be auto-translated
    TRANSLATABLE_FIELDS = ['bio', 'education', 'experience', 'achievements', 'manifesto']
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200, help_text="Full name as it appears on official documents")
    photo = models.ImageField(upload_to=candidate_photo_path, blank=True, null=True)
    age = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(18), MaxValueValidator(120)],
        help_text="Age of the candidate (must be 18+ to run for office)"
    )
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

    achievements_en = models.TextField(blank=True, help_text="Key achievements and accomplishments")
    achievements_ne = models.TextField(blank=True)
    is_mt_achievements_ne = models.BooleanField(default=False, help_text="True if achievements_ne is machine translated")

    manifesto_en = models.TextField(blank=True)
    manifesto_ne = models.TextField(blank=True)
    is_mt_manifesto_ne = models.BooleanField(default=False, help_text="True if manifesto_ne is machine translated")

    office = models.CharField(max_length=20, choices=OFFICE_CHOICES, default='municipal', help_text="Office level (Federal/Provincial/Municipal/Ward)")
    position_level = models.CharField(max_length=35, choices=POSITION_LEVELS, verbose_name="Seat", help_text="Specific seat/position being contested")
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
    donation_description = models.CharField(max_length=200, blank=True, help_text="Brief description of what donations will be used for")

    # Identity Verification Documents (confidential - admin only)
    identity_document = models.FileField(
        upload_to='verification_docs/identity/%Y/%m/',
        blank=True,
        null=True,
        help_text="National ID/Citizenship/Driver's License (confidential)"
    )
    candidacy_document = models.FileField(
        upload_to='verification_docs/candidacy/%Y/%m/',
        blank=True,
        null=True,
        help_text="Official election declaration paper (confidential)"
    )
    terms_accepted = models.BooleanField(
        default=False,
        help_text="Candidate has accepted terms and conditions"
    )

    # Approval/Verification fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, help_text="Notes from admin (e.g., rejection reasons)")
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_candidates')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['position_level', 'district']),
            models.Index(fields=['province', 'district', 'municipality']),
            models.Index(fields=['full_name']),
            # Index for ballot queries - exact location matching with status
            models.Index(fields=['status', 'province', 'district', 'municipality', 'ward_number'], name='ballot_location_idx'),
            # Index for position-level filtering with status
            models.Index(fields=['status', 'position_level', 'province'], name='ballot_position_idx'),
            # Index for general status filtering
            models.Index(fields=['status', 'created_at'], name='status_created_idx'),
        ]

    def clean(self):
        # Ward level positions require ward number and municipality
        ward_positions = ['ward_chairperson', 'ward_member']
        if self.position_level in ward_positions:
            if not self.ward_number:
                raise ValidationError('Ward number is required for ward-level positions')
            if not self.municipality:
                raise ValidationError('Municipality is required for ward-level positions')

        # Local unit level positions require municipality but not ward
        local_positions = ['mayor_chairperson', 'deputy_mayor_vice_chairperson']
        if self.position_level in local_positions:
            if not self.municipality:
                raise ValidationError('Municipality is required for local unit positions')

        # Validate location hierarchy
        if self.municipality and self.municipality.district != self.district:
            raise ValidationError('Municipality must belong to the selected district')
        if self.district.province != self.province:
            raise ValidationError('District must belong to the selected province')

    def get_absolute_url(self):
        return reverse('candidates:detail', kwargs={'pk': self.pk})

    def get_domain(self):
        """Get the current site domain for email links"""
        try:
            from django.contrib.sites.models import Site
            current_site = Site.objects.get_current()
            return f"http://{current_site.domain}"
        except:
            return "http://localhost:8000"

    def send_registration_confirmation(self):
        """Send email confirmation to candidate after registration"""
        subject = f"[ElectNepal] Registration Confirmation - {self.full_name}"
        context = {
            'candidate': self,
            'domain': self.get_domain(),
        }

        try:
            html_message = render_to_string(
                'candidates/emails/registration_confirmation.html',
                context
            )

            logger.info(f"Sending registration confirmation to {self.user.email} for candidate {self.full_name}")

            send_mail(
                subject=subject,
                message=f"Your candidate registration has been submitted for review. You will be notified once approved.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"Successfully sent registration confirmation to {self.user.email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send registration confirmation to {self.user.email}: {str(e)}", exc_info=True)

            # Fallback: Try to notify admins about the failure
            try:
                mail_admins(
                    subject=f"[ALERT] Email Failure - Registration Confirmation",
                    message=f"Failed to send registration confirmation to {self.full_name} ({self.user.email}). Error: {str(e)}",
                    fail_silently=True
                )
            except:
                pass

            return False

    def notify_admin_new_registration(self):
        """Notify admins about new candidate registration"""
        subject = f"[Admin Alert] New Candidate Registration: {self.full_name}"
        admin_emails = [email for name, email in settings.ADMINS]

        if not admin_emails:
            logger.warning(f"No admin emails configured for new registration notification")
            return False

        try:
            # Count pending candidates
            pending_count = Candidate.objects.filter(status='pending').count()

            context = {
                'candidate': self,
                'domain': self.get_domain(),
                'pending_count': pending_count,
            }

            html_message = render_to_string(
                'candidates/emails/admin_notification.html',
                context
            )

            logger.info(f"Notifying {len(admin_emails)} admin(s) about new registration: {self.full_name}")

            send_mail(
                subject=subject,
                message=f"New candidate {self.full_name} has registered and requires review.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"Successfully notified admins about {self.full_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to notify admins about {self.full_name}: {str(e)}", exc_info=True)
            # Admin notification failure is critical but shouldn't block registration
            return False

    def send_approval_email(self):
        """Send approval notification to candidate"""
        subject = f"[ElectNepal] Congratulations! Your Profile is Approved"
        context = {
            'candidate': self,
            'domain': self.get_domain(),
        }

        try:
            html_message = render_to_string(
                'candidates/emails/approval_notification.html',
                context
            )

            logger.info(f"Sending approval email to {self.user.email} for candidate {self.full_name}")

            send_mail(
                subject=subject,
                message=f"Congratulations! Your candidate profile has been approved. You can now access your dashboard.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"Successfully sent approval email to {self.user.email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send approval email to {self.user.email}: {str(e)}", exc_info=True)

            # Notify admins about critical email failure
            try:
                mail_admins(
                    subject=f"[CRITICAL] Failed to send approval email",
                    message=f"Failed to send approval notification to {self.full_name} ({self.user.email}). Please contact them manually. Error: {str(e)}",
                    fail_silently=True
                )
            except:
                pass

            return False

    def send_rejection_email(self):
        """Send rejection notification to candidate with reasons"""
        subject = f"[ElectNepal] Profile Review Update"
        context = {
            'candidate': self,
            'domain': self.get_domain(),
            'now': timezone.now(),
        }

        try:
            html_message = render_to_string(
                'candidates/emails/rejection_notification.html',
                context
            )

            logger.info(f"Sending rejection email to {self.user.email} for candidate {self.full_name}")

            send_mail(
                subject=subject,
                message=f"Your candidate profile requires revision. Admin notes: {self.admin_notes or 'Please review our guidelines.'}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"Successfully sent rejection email to {self.user.email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send rejection email to {self.user.email}: {str(e)}", exc_info=True)

            # Notify admins about email failure
            try:
                mail_admins(
                    subject=f"[ALERT] Failed to send rejection email",
                    message=f"Failed to send rejection notification to {self.full_name} ({self.user.email}). They may not know about the rejection. Error: {str(e)}",
                    fail_silently=True
                )
            except:
                pass

            return False

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
            try:
                # Use Google Translate directly for reliable translation
                from googletrans import Translator
                translator = Translator()
                result = translator.translate(en_value, src='en', dest='ne')
                translated = result.text
                setattr(self, ne_field, translated)
                setattr(self, mt_flag_field, True)
            except Exception as e:
                # If translation fails, at least copy the English (better than lowercase)
                setattr(self, ne_field, en_value)
                setattr(self, mt_flag_field, False)

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