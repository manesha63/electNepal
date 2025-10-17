from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.crypto import get_random_string
import uuid
from datetime import timedelta


class EmailVerification(models.Model):
    """Model to track email verification tokens for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    last_verification_check = models.DateTimeField(null=True, blank=True)  # Track when user last verified during login

    def is_expired(self):
        """Check if verification token has expired (72 hours)"""
        expiry_time = self.created_at + timedelta(hours=72)
        return timezone.now() > expiry_time

    def verify(self):
        """Mark email as verified"""
        if not self.is_expired():
            self.is_verified = True
            self.verified_at = timezone.now()
            self.save()

            # Update user's is_active status
            self.user.is_active = True
            self.user.save()
            return True
        return False

    def regenerate_token(self):
        """Generate a new token (for resending verification email)"""
        self.token = uuid.uuid4()
        self.created_at = timezone.now()
        self.save()
        return self.token

    def needs_reverification(self):
        """Check if user needs to reverify (after 7 days)"""
        if not self.is_verified:
            return True  # Not verified at all

        if not self.last_verification_check:
            # Never checked during login, use initial verification date
            if self.verified_at:
                days_since = (timezone.now() - self.verified_at).days
                return days_since >= 7
            return True

        # Check if 7 days have passed since last verification check
        days_since = (timezone.now() - self.last_verification_check).days
        return days_since >= 7

    def update_verification_check(self):
        """Update the last verification check timestamp"""
        self.last_verification_check = timezone.now()
        self.save()

    class Meta:
        verbose_name = "Email Verification"
        verbose_name_plural = "Email Verifications"

    def __str__(self):
        return f"{self.user.username} - {'Verified' if self.is_verified else 'Pending'}"


class PasswordResetToken(models.Model):
    """Model to track password reset tokens"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        """Check if reset token has expired (24 hours)"""
        expiry_time = self.created_at + timedelta(hours=24)
        return timezone.now() > expiry_time

    def mark_as_used(self):
        """Mark token as used"""
        self.is_used = True
        self.used_at = timezone.now()
        self.save()

    class Meta:
        verbose_name = "Password Reset Token"
        verbose_name_plural = "Password Reset Tokens"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"