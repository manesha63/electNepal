"""
API Authentication Models
"""
import secrets
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class APIKey(models.Model):
    """
    Model to store API keys for external developers/partners
    """
    # Key identification
    key = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=100, help_text="Name to identify this API key")

    # Owner information
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='api_keys',
        null=True,
        blank=True,
        help_text="User who owns this API key (optional)"
    )

    # Contact information for non-user API keys
    contact_email = models.EmailField(
        help_text="Contact email for this API key holder"
    )
    organization = models.CharField(
        max_length=200,
        blank=True,
        help_text="Organization using this API key"
    )

    # Permissions and limits
    is_active = models.BooleanField(default=True)
    can_read = models.BooleanField(default=True, help_text="Can read public data")
    can_write = models.BooleanField(default=False, help_text="Can write/modify data")
    rate_limit = models.IntegerField(
        default=1000,
        help_text="Requests per hour allowed"
    )

    # Usage tracking
    last_used = models.DateTimeField(null=True, blank=True)
    total_requests = models.BigIntegerField(default=0)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Optional expiration date for this key"
    )
    notes = models.TextField(
        blank=True,
        help_text="Internal notes about this API key"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['key', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.organization or 'Individual'})"

    @classmethod
    def generate_key(cls):
        """Generate a secure random API key"""
        return f"eln_{secrets.token_urlsafe(32)}"

    def is_valid(self):
        """Check if API key is valid and not expired"""
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True

    def record_usage(self):
        """Record that this API key was used"""
        self.last_used = timezone.now()
        self.total_requests += 1
        self.save(update_fields=['last_used', 'total_requests'])


class APIKeyUsageLog(models.Model):
    """
    Log API key usage for analytics and rate limiting
    """
    api_key = models.ForeignKey(APIKey, on_delete=models.CASCADE, related_name='usage_logs')
    endpoint = models.CharField(max_length=200)
    method = models.CharField(max_length=10)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    response_status = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['api_key', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.api_key.name} - {self.endpoint} at {self.timestamp}"