from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.core.mail import send_mail, mail_admins
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from locations.models import Province, District, Municipality
from .translation import AutoTranslationMixin
from .validators import validate_file_size, validate_image_size, validate_file_extension, validate_image_extension, validate_file_content_type
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
        ('ward_chairperson', _('Ward Chairperson')),
        ('ward_member', _('Ward Member')),

        # Local Unit Level (Municipality/Rural Municipality/Metropolitan/Sub-Metropolitan)
        ('mayor_chairperson', _('Mayor/Chairperson')),
        ('deputy_mayor_vice_chairperson', _('Deputy Mayor/Vice Chairperson')),

        # Provincial Level
        ('provincial_assembly', _('Provincial Assembly Member')),

        # Federal Level
        ('house_of_representatives', _('House of Representatives Member')),
        ('national_assembly', _('National Assembly Member')),
    ]

    OFFICE_CHOICES = [
        ('federal', _('Federal')),
        ('provincial', _('Provincial')),
        ('municipal', _('Municipal')),
        ('ward', _('Ward')),
    ]

    STATUS_CHOICES = [
        ('pending', _('Pending Review')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]

    # Fields that should be auto-translated
    TRANSLATABLE_FIELDS = ['bio', 'education', 'experience', 'achievements', 'manifesto']
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    full_name = models.CharField(max_length=200, help_text="Full name as it appears on official documents")
    photo = models.ImageField(
        upload_to=candidate_photo_path,
        blank=True,
        null=True,
        validators=[validate_image_size, validate_image_extension, validate_file_content_type],
        help_text=_("Profile photo (JPG/PNG, max 5MB)")
    )
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
        validators=[MinValueValidator(1)],
        help_text="Ward number (required for ward-level positions, must be valid for the selected municipality)"
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
        validators=[validate_file_size, validate_file_extension, validate_file_content_type],
        help_text=_("National ID/Citizenship/Driver's License (PDF/JPG/PNG, max 10MB, confidential)")
    )
    candidacy_document = models.FileField(
        upload_to='verification_docs/candidacy/%Y/%m/',
        blank=True,
        null=True,
        validators=[validate_file_size, validate_file_extension, validate_file_content_type],
        help_text=_("Official election declaration paper (PDF/JPG/PNG, max 10MB, confidential)")
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
            # Index for candidate list queries - status filter with descending created_at and name sort
            # Matches query pattern: filter(status='approved').order_by('-created_at', 'full_name')
            models.Index(fields=['status', '-created_at', 'full_name'], name='status_created_name_idx'),
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

        # Dynamic ward number validation: check against municipality's actual total_wards
        if self.ward_number and self.municipality:
            if self.ward_number > self.municipality.total_wards:
                raise ValidationError({
                    'ward_number': f'Invalid ward number. {self.municipality.name_en} only has {self.municipality.total_wards} wards. Please select a ward between 1 and {self.municipality.total_wards}.'
                })

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
        except (ImportError, Site.DoesNotExist) as e:
            logger.warning(f"Site framework not configured: {e}")
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
            except Exception as admin_err:
                logger.error(f"Failed to notify admin of email failure: {admin_err}")

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
            except Exception as admin_err:
                logger.error(f"Failed to notify admin of approval email failure: {admin_err}")

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
            except Exception as admin_err:
                logger.error(f"Failed to notify admin of rejection email failure: {admin_err}")

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
                logger.info(f"Successfully translated {en_field} to Nepali for Candidate {self.full_name} (ID: {self.pk})")
            except Exception as e:
                # Log translation failure with detailed error information
                logger.error(
                    f"Translation failed for Candidate {self.full_name} (ID: {self.pk}): "
                    f"Field '{en_field}' translation to '{ne_field}' failed. "
                    f"Error: {type(e).__name__}: {str(e)}"
                )

                # Notify admins about translation failure (async to avoid blocking)
                try:
                    mail_admins(
                        subject=f"Translation Failure: Candidate {self.full_name}",
                        message=f"Auto-translation failed for candidate '{self.full_name}' (ID: {self.pk}).\n\n"
                                f"Field: {en_field} → {ne_field}\n"
                                f"Error: {type(e).__name__}: {str(e)}\n\n"
                                f"The English content has been copied as fallback.\n"
                                f"Manual translation review required.\n\n"
                                f"Candidate profile: {settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'N/A'}/admin/candidates/candidate/{self.pk}/change/",
                        fail_silently=True  # Don't raise exception if email fails
                    )
                except Exception as email_error:
                    logger.error(f"Failed to send admin notification email: {type(email_error).__name__}: {str(email_error)}")

                # If translation fails, copy English text as fallback
                setattr(self, ne_field, en_value)
                setattr(self, mt_flag_field, False)

                logger.warning(f"Fallback applied: Copied English content to {ne_field} for Candidate {self.full_name} (ID: {self.pk})")

    def autotranslate_missing(self):
        """
        Auto-translate all empty Nepali fields from English
        """
        self._fill_missing_pair("bio_en", "bio_ne", "is_mt_bio_ne")
        self._fill_missing_pair("education_en", "education_ne", "is_mt_education_ne")
        self._fill_missing_pair("experience_en", "experience_ne", "is_mt_experience_ne")
        self._fill_missing_pair("manifesto_en", "manifesto_ne", "is_mt_manifesto_ne")

    def save(self, *args, **kwargs):
        # Enforce full_clean() validation to prevent bypassing location hierarchy checks
        # This ensures validation runs even for .create(), .update(), and direct saves
        # Prevents invalid foreign key relationships (e.g., district not in province)
        # Can be bypassed with save(skip_validation=True) only when absolutely necessary
        if not kwargs.pop('skip_validation', False):
            self.full_clean()

        # Optimize photo if it's being uploaded or changed
        if self.photo:
            # Check if this is a new upload or photo has changed
            if self.pk is None:  # New instance
                should_optimize = True
            else:
                # Check if photo has changed by comparing with database
                try:
                    old_instance = Candidate.objects.get(pk=self.pk)
                    should_optimize = old_instance.photo != self.photo
                except Candidate.DoesNotExist:
                    should_optimize = True

            if should_optimize:
                try:
                    from .image_utils import optimize_image, should_optimize_image

                    # Only optimize if necessary (large file or dimensions)
                    if should_optimize_image(self.photo):
                        optimized = optimize_image(self.photo)
                        if optimized:
                            self.photo = optimized
                            logger.info(f"Successfully optimized photo for candidate {self.full_name}")
                except ImportError as e:
                    # Log import error but don't fail the upload
                    logger.error(f"Failed to import image optimization utilities: {type(e).__name__}: {str(e)}")
                    logger.warning(f"Photo uploaded without optimization for candidate {self.full_name}")
                except Exception as e:
                    # Catch any other unexpected errors during optimization
                    logger.error(
                        f"Unexpected error during image optimization for candidate {self.full_name} (ID: {self.pk}): "
                        f"{type(e).__name__}: {str(e)}"
                    )
                    logger.warning(f"Photo uploaded without optimization for candidate {self.full_name}")

        # Check if this is a new instance or if we need translation
        is_new = self.pk is None
        needs_translation = False

        # Check if any Nepali fields are missing while English fields exist
        if is_new or not self.bio_ne or not self.education_ne or not self.experience_ne or not self.manifesto_ne:
            fields_to_check = [
                ('bio_en', 'bio_ne'),
                ('education_en', 'education_ne'),
                ('experience_en', 'experience_ne'),
                ('manifesto_en', 'manifesto_ne')
            ]
            for en_field, ne_field in fields_to_check:
                en_value = getattr(self, en_field, "") or ""
                ne_value = getattr(self, ne_field, "") or ""
                if en_value and not ne_value:
                    needs_translation = True
                    break

        # Save the instance first
        super().save(*args, **kwargs)

        # If translation is needed, schedule it to run AFTER the transaction commits
        # This prevents race conditions where the background thread tries to access
        # a candidate that hasn't been committed to the database yet
        if needs_translation:
            from django.db import transaction
            from .async_translation import translate_candidate_async

            # Prepare fields to translate
            fields_to_translate = [
                ('bio_en', 'bio_ne', 'is_mt_bio_ne'),
                ('education_en', 'education_ne', 'is_mt_education_ne'),
                ('experience_en', 'experience_ne', 'is_mt_experience_ne'),
                ('manifesto_en', 'manifesto_ne', 'is_mt_manifesto_ne')
            ]

            # Use on_commit to ensure translation starts only after transaction commits
            transaction.on_commit(
                lambda: translate_candidate_async(self.pk, fields_to_translate)
            )

    def __str__(self):
        return f"{self.full_name} ({self.get_position_level_display()})"



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
    
    def save(self, *args, **kwargs):
        # Check if this is a new instance or if we need translation
        is_new = self.pk is None
        needs_translation = False

        # Check if any Nepali fields are missing while English fields exist
        if is_new or not self.title_ne or not self.description_ne or not self.location_ne:
            fields_to_check = [
                ('title_en', 'title_ne'),
                ('description_en', 'description_ne'),
                ('location_en', 'location_ne')
            ]
            for en_field, ne_field in fields_to_check:
                en_value = getattr(self, en_field, "") or ""
                ne_value = getattr(self, ne_field, "") or ""
                if en_value and not ne_value:
                    needs_translation = True
                    break

        # Save the instance first (skip AutoTranslationMixin's save)
        models.Model.save(self, *args, **kwargs)

        # If translation is needed, schedule it to run AFTER the transaction commits
        # This prevents race conditions where the background thread tries to access
        # an event that hasn't been committed to the database yet
        if needs_translation:
            from django.db import transaction
            from .async_translation import translate_event_async

            # Prepare fields to translate
            fields_to_translate = [
                ('title_en', 'title_ne', 'is_mt_title_ne'),
                ('description_en', 'description_ne', 'is_mt_description_ne'),
                ('location_en', 'location_ne', 'is_mt_location_ne')
            ]

            # Use on_commit to ensure translation starts only after transaction commits
            transaction.on_commit(
                lambda: translate_event_async(self.pk, fields_to_translate)
            )

    def __str__(self):
        return f"{self.candidate.full_name}: {self.title_en}"