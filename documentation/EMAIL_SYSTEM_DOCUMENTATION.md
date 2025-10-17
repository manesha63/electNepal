# ElectNepal Email Delivery & Verification System Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Configuration](#configuration)
3. [Email Types & Templates](#email-types--templates)
4. [Email Verification System](#email-verification-system)
5. [Password Reset System](#password-reset-system)
6. [Candidate Notification System](#candidate-notification-system)
7. [AWS SES Integration](#aws-ses-integration)
8. [Testing & Monitoring](#testing--monitoring)
9. [Troubleshooting Guide](#troubleshooting-guide)
10. [Security Considerations](#security-considerations)
11. [API Reference](#api-reference)
12. [Deployment Checklist](#deployment-checklist)

---

## System Overview

ElectNepal's email system provides comprehensive email functionality including user verification, password reset, and candidate notifications. The system uses AWS SES (Simple Email Service) for reliable email delivery with full HTML template support and bilingual capabilities.

### Key Features
- **Email Verification**: Required for account activation
- **Password Reset**: Secure token-based password recovery
- **Candidate Notifications**: Automated emails for registration, approval, and rejection
- **Admin Alerts**: Instant notifications for new candidate registrations
- **HTML Templates**: Professional, responsive email designs
- **Error Logging**: Comprehensive logging for debugging and monitoring
- **Rate Limiting**: Protection against abuse
- **Transaction Safety**: Emails sent only after successful database commits

### System Architecture
```
User Action → Django View → Email Service → AWS SES → Recipient
                ↓               ↓
            Database        Email Logs
```

---

## Configuration

### Environment Variables (.env)
```bash
# Email Backend Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

# AWS SES SMTP Settings (US East N. Virginia)
EMAIL_HOST=email-smtp.us-east-1.amazonaws.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=AKIATXIKHFSRSIE334VE
EMAIL_HOST_PASSWORD=BPmm2uILsjNz2X7uTm9ndrolt35ViIfJqjfmAb81q3A2
DEFAULT_FROM_EMAIL=electnepal5@gmail.com
SERVER_EMAIL=electnepal5@gmail.com
```

### Settings Configuration (`nepal_election_app/settings/email.py`)
```python
from decouple import config

# Email backend selection
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

# Production email settings
if EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
    EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
    DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@electnepal.com')
    CONTACT_EMAIL = 'electnepal5@gmail.com'
else:
    # Development settings
    DEFAULT_FROM_EMAIL = 'dev@electnepal.local'
    CONTACT_EMAIL = 'electnepal5@gmail.com'

# Email configuration
EMAIL_SUBJECT_PREFIX = '[ElectNepal] '
ADMINS = [('ElectNepal Admin', 'electnepal5@gmail.com')]
MANAGERS = ADMINS

# Verification settings
EMAIL_VERIFICATION_TIMEOUT = 72  # hours
ACCOUNT_EMAIL_REQUIRED = True
```

### Logging Configuration (`nepal_election_app/settings/logging.py`)
```python
'loggers': {
    'candidates.emails': {
        'handlers': ['console', 'email_file', 'mail_admins'],
        'level': 'DEBUG',
        'propagate': False,
    },
    'authentication.emails': {
        'handlers': ['console', 'email_file', 'mail_admins'],
        'level': 'DEBUG',
        'propagate': False,
    },
}
```

---

## Email Types & Templates

### 1. Authentication Emails

#### Email Verification
- **Template**: `authentication/emails/email_verification.html`
- **Trigger**: User registration
- **Expiry**: 72 hours
- **Contents**:
  - Verification link
  - Welcome message
  - Instructions for next steps

#### Password Reset
- **Template**: `authentication/emails/password_reset.html`
- **Trigger**: Forgot password request
- **Expiry**: 24 hours
- **Contents**:
  - Reset link
  - Security warning
  - Support contact

#### Welcome Email
- **Template**: `authentication/emails/welcome.html`
- **Trigger**: Successful email verification
- **Contents**:
  - Welcome message
  - Getting started guide
  - Important links

### 2. Candidate Emails

#### Registration Confirmation
- **Template**: `candidates/emails/registration_confirmation.html`
- **Trigger**: Candidate profile submission
- **Recipients**: Candidate
- **Contents**:
  - Submission confirmation
  - Review process timeline
  - Next steps

#### Admin Notification
- **Template**: `candidates/emails/admin_notification.html`
- **Trigger**: New candidate registration
- **Recipients**: All admin users
- **Contents**:
  - Candidate details
  - Review link
  - Quick actions

#### Approval Notification
- **Template**: `candidates/emails/approval_notification.html`
- **Trigger**: Admin approves candidate
- **Recipients**: Candidate
- **Contents**:
  - Congratulations message
  - Dashboard access link
  - Profile management tips

#### Rejection Notification
- **Template**: `candidates/emails/rejection_notification.html`
- **Trigger**: Admin rejects candidate
- **Recipients**: Candidate
- **Contents**:
  - Rejection reason
  - Revision instructions
  - Resubmission link

---

## Email Verification System

### Overview
The email verification system ensures that users provide valid email addresses before accessing the platform.

### Database Models

#### EmailVerification Model (`authentication/models.py`)
```python
class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        """Check if verification token has expired (72 hours)"""
        expiry_time = self.created_at + timedelta(hours=72)
        return timezone.now() > expiry_time

    def verify(self):
        """Mark email as verified and activate user"""
        if not self.is_expired():
            self.is_verified = True
            self.verified_at = timezone.now()
            self.save()

            # Activate user account
            self.user.is_active = True
            self.user.save()
            return True
        return False

    def regenerate_token(self):
        """Generate a new token for resending verification"""
        self.token = uuid.uuid4()
        self.created_at = timezone.now()
        self.save()
        return self.token
```

### Verification Flow

```mermaid
graph LR
    A[User Registration] --> B[Create Inactive User]
    B --> C[Generate Verification Token]
    C --> D[Send Verification Email]
    D --> E[User Clicks Link]
    E --> F{Token Valid?}
    F -->|Yes| G[Activate User Account]
    F -->|No| H[Show Error/Resend Option]
    G --> I[Redirect to Login]
```

### Implementation

#### Registration View (`authentication/views.py`)
```python
class CandidateSignupView(CreateView):
    def form_valid(self, form):
        # Save user as inactive
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # Create verification record
        verification = EmailVerification.objects.create(user=user)

        # Send verification email
        self.send_verification_email(user, verification.token)

        messages.success(
            self.request,
            f'Please check {user.email} to verify your account.'
        )
        return redirect('authentication:login')

    def send_verification_email(self, user, verification_token):
        domain = self.request.get_host()
        protocol = 'https' if self.request.is_secure() else 'http'
        verification_url = f"{protocol}://{domain}/auth/verify-email/{verification_token}/"

        context = {
            'user': user,
            'verification_url': verification_url,
            'expiry_hours': 72
        }

        html_message = render_to_string(
            'authentication/emails/email_verification.html',
            context
        )

        send_mail(
            subject="[ElectNepal] Verify Your Email Address",
            message=f"Click here to verify: {verification_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
```

#### Verification Handler (`authentication/views.py`)
```python
class EmailVerificationView(View):
    def get(self, request, token):
        try:
            verification = EmailVerification.objects.get(token=token)

            if verification.is_verified:
                messages.info(request, 'Email already verified.')
                return redirect('authentication:login')

            if verification.is_expired():
                messages.error(request, 'Verification link expired.')
                return redirect('authentication:resend_verification')

            if verification.verify():
                messages.success(request, 'Email verified successfully!')
                return redirect('authentication:login')

        except EmailVerification.DoesNotExist:
            messages.error(request, 'Invalid verification link.')
            return redirect('authentication:login')
```

### Resend Verification

```python
class ResendVerificationView(TemplateView):
    def post(self, request):
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            if hasattr(user, 'email_verification'):
                if not user.email_verification.is_verified:
                    # Regenerate token
                    new_token = user.email_verification.regenerate_token()
                    # Send new email
                    self._send_verification_email(user, new_token)
                    messages.success(request, f'New verification sent to {email}')

        except User.DoesNotExist:
            # Don't reveal if email exists
            messages.info(request, 'If account exists, verification will be sent.')

        return redirect('authentication:login')
```

---

## Password Reset System

### Database Models

#### PasswordResetToken Model (`authentication/models.py`)
```python
class PasswordResetToken(models.Model):
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
```

### Reset Flow

```mermaid
graph LR
    A[Forgot Password] --> B[Enter Email]
    B --> C[Generate Reset Token]
    C --> D[Send Reset Email]
    D --> E[User Clicks Link]
    E --> F{Token Valid?}
    F -->|Yes| G[Show Reset Form]
    F -->|No| H[Show Error]
    G --> I[Set New Password]
    I --> J[Mark Token Used]
    J --> K[Redirect to Login]
```

### Implementation

#### Forgot Password View (`authentication/views.py`)
```python
class ForgotPasswordView(TemplateView):
    template_name = 'authentication/forgot_password.html'

    def post(self, request):
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            # Create reset token
            reset_token = PasswordResetToken.objects.create(user=user)

            # Send reset email
            self._send_reset_email(user, reset_token.token)

        except User.DoesNotExist:
            pass  # Don't reveal if email exists

        messages.info(
            request,
            'If account exists, reset instructions will be sent.'
        )
        return redirect('authentication:login')
```

#### Reset Password View (`authentication/views.py`)
```python
class ResetPasswordView(TemplateView):
    template_name = 'authentication/reset_password.html'

    def post(self, request, token):
        try:
            reset_token = PasswordResetToken.objects.get(
                token=token,
                is_used=False
            )

            if reset_token.is_expired():
                messages.error(request, 'Reset link has expired.')
                return redirect('authentication:forgot_password')

            # Get new password
            password = request.POST.get('password')
            password_confirm = request.POST.get('password_confirm')

            if password != password_confirm:
                messages.error(request, 'Passwords do not match.')
                return redirect('authentication:reset_password', token=token)

            # Update password
            user = reset_token.user
            user.set_password(password)
            user.save()

            # Mark token as used
            reset_token.mark_as_used()

            messages.success(request, 'Password reset successfully!')
            return redirect('authentication:login')

        except PasswordResetToken.DoesNotExist:
            messages.error(request, 'Invalid reset link.')
            return redirect('authentication:forgot_password')
```

---

## Candidate Notification System

### Overview
The candidate notification system handles all email communications related to candidate registration, approval, and rejection.

### Email Triggers

#### 1. Registration Confirmation
**When**: Candidate completes 4-step registration
**Recipients**: Candidate, Admin team
**Implementation**:

```python
# In candidates/views.py
def send_registration_emails():
    """Send email notifications after successful database commit"""
    try:
        # Send confirmation to candidate
        candidate.send_registration_confirmation()
        # Notify admins about new registration
        candidate.notify_admin_new_registration()
    except Exception as e:
        logger.error(f"Failed to send emails: {e}")

# Use transaction.on_commit for safety
transaction.on_commit(send_registration_emails)
```

#### 2. Approval Notification
**When**: Admin approves candidate profile
**Recipients**: Candidate
**Implementation**:

```python
# In candidates/models.py
def send_approval_notification(self):
    """Send approval email to candidate"""
    context = {
        'candidate': self,
        'dashboard_url': f"{settings.SITE_URL}/candidates/dashboard/",
        'profile_url': f"{settings.SITE_URL}/candidates/{self.pk}/"
    }

    html_message = render_to_string(
        'candidates/emails/approval_notification.html',
        context
    )

    send_mail(
        subject="[ElectNepal] Your Profile Has Been Approved!",
        message="Congratulations! Your profile is now live.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[self.user.email],
        html_message=html_message,
        fail_silently=False,
    )
```

#### 3. Rejection Notification
**When**: Admin rejects candidate profile
**Recipients**: Candidate
**Implementation**:

```python
# In candidates/models.py
def send_rejection_notification(self):
    """Send rejection email with feedback"""
    context = {
        'candidate': self,
        'admin_notes': self.admin_notes,
        'edit_url': f"{settings.SITE_URL}/candidates/dashboard/"
    }

    html_message = render_to_string(
        'candidates/emails/rejection_notification.html',
        context
    )

    send_mail(
        subject="[ElectNepal] Profile Revision Required",
        message=f"Admin notes: {self.admin_notes}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[self.user.email],
        html_message=html_message,
        fail_silently=False,
    )
```

### Transaction Safety
All candidate emails use `transaction.on_commit()` to ensure emails are only sent after successful database commits:

```python
with transaction.atomic():
    candidate.save()
    # Other database operations

    def send_emails():
        candidate.send_registration_confirmation()
        candidate.notify_admin_new_registration()

    transaction.on_commit(send_emails)
```

---

## AWS SES Integration

### Current Status
- **Mode**: Sandbox (Development)
- **Region**: US East (N. Virginia) - us-east-1
- **Verified Email**: electnepal5@gmail.com
- **Daily Limit**: 200 emails (sandbox mode)

### Sandbox Limitations
1. Can only send to verified email addresses
2. Maximum 200 emails per 24 hours
3. Maximum 1 email per second

### Production Setup Steps

#### 1. Request Production Access
```bash
# AWS CLI command
aws ses put-account-sending-attributes \
    --region us-east-1 \
    --sending-enabled
```

#### 2. Verify Domain
```python
# Domain verification in AWS Console
1. Navigate to SES > Verified identities
2. Click "Create identity"
3. Choose "Domain"
4. Enter: electnepal.com
5. Add DNS records to domain registrar
```

#### 3. Configure DKIM
```python
# Enable DKIM signing
1. In SES Console, select domain
2. Click "DKIM" tab
3. Generate DKIM tokens
4. Add CNAME records to DNS
```

#### 4. Setup SPF Record
```
# Add to DNS TXT record
"v=spf1 include:amazonses.com ~all"
```

#### 5. Configure Bounce Handling
```python
# Setup SNS topic for bounces
1. Create SNS topic: electnepal-ses-bounces
2. Subscribe endpoint to topic
3. Configure SES to use topic
```

### Error Handling

#### Common SES Errors
```python
try:
    send_mail(...)
except SMTPDataError as e:
    if e.smtp_code == 554:
        # Email not verified in SES
        logger.error(f"Unverified recipient: {email}")
    elif e.smtp_code == 552:
        # Message too large
        logger.error("Email exceeds size limit")
except SMTPAuthenticationError:
    # Invalid credentials
    logger.error("SES authentication failed")
except Exception as e:
    logger.error(f"Unexpected email error: {e}")
```

---

## Testing & Monitoring

### Testing Suite

#### Run Complete Email Test
```bash
# Test all email functionality
python test_email_system.py
```

#### Test Script (`test_email_system.py`)
```python
#!/usr/bin/env python
"""Complete email system test suite"""

def test_basic_connection():
    """Test SMTP connection"""
    connection = get_connection()
    connection.open()
    print(f"✓ Connected to {settings.EMAIL_HOST}")
    connection.close()

def test_simple_email():
    """Test sending plain text email"""
    send_mail(
        subject='Test Email',
        message='Test message',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['test@example.com'],
        fail_silently=False,
    )

def test_html_email():
    """Test HTML template email"""
    html_message = render_to_string('email_template.html', context)
    send_mail(..., html_message=html_message)

def test_verification_flow():
    """Test complete verification flow"""
    user = User.objects.create_user(...)
    verification = EmailVerification.objects.create(user=user)
    # Send verification email
    # Test token validation
    # Test expiry

def test_password_reset_flow():
    """Test password reset flow"""
    # Similar to verification
```

### Monitoring

#### Email Logs
```bash
# View recent email logs
tail -f logs/email.log

# Check for errors
grep ERROR logs/email.log

# Count emails sent today
grep "$(date +%Y-%m-%d)" logs/email.log | grep "sent successfully" | wc -l
```

#### Django Shell Monitoring
```python
# Check pending verifications
from authentication.models import EmailVerification
pending = EmailVerification.objects.filter(is_verified=False)
print(f"Pending verifications: {pending.count()}")

# Check recent password resets
from authentication.models import PasswordResetToken
from django.utils import timezone
from datetime import timedelta

recent = PasswordResetToken.objects.filter(
    created_at__gte=timezone.now() - timedelta(days=1)
)
print(f"Password resets (24h): {recent.count()}")
```

### Performance Metrics
```python
# Email sending performance
import time
from django.core.mail import send_mail

start = time.time()
send_mail(...)
duration = time.time() - start
print(f"Email sent in {duration:.2f} seconds")
```

---

## Troubleshooting Guide

### Common Issues & Solutions

#### 1. Email Not Received
**Symptoms**: Email sent successfully but not in inbox
**Possible Causes**:
- Email in spam folder
- Recipient email not verified in SES (sandbox mode)
- Email bounced

**Solutions**:
```bash
# Check if email is verified in SES
grep "recipient_email" logs/email.log

# Check for bounce
grep "SMTPDataError" logs/email.log
```

#### 2. Error 554: Message Rejected
**Cause**: Recipient email not verified in SES sandbox
**Solution**:
```python
# Verify email in AWS SES Console
# Or request production access
```

#### 3. Verification Link Expired
**Cause**: User clicked link after 72 hours
**Solution**:
```python
# User can request new verification
# Navigate to /auth/resend-verification/
```

#### 4. Email Templates Not Found
**Cause**: Missing template files
**Solution**:
```bash
# Check template exists
ls authentication/templates/authentication/emails/

# Verify template path in view
python manage.py shell
>>> from django.template.loader import get_template
>>> get_template('authentication/emails/email_verification.html')
```

#### 5. SMTP Authentication Failed
**Cause**: Invalid AWS SES credentials
**Solution**:
```python
# Verify credentials in .env
EMAIL_HOST_USER=your_ses_username
EMAIL_HOST_PASSWORD=your_ses_password

# Test connection
python manage.py shell
>>> from django.core.mail import get_connection
>>> conn = get_connection()
>>> conn.open()
```

### Debug Commands

#### Test Email Connection
```python
python manage.py shell
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Test Subject',
    'Test message',
    settings.DEFAULT_FROM_EMAIL,
    ['test@example.com'],
    fail_silently=False,
)
```

#### Check Email Configuration
```python
python manage.py shell
from django.conf import settings

print(f"Backend: {settings.EMAIL_BACKEND}")
print(f"Host: {settings.EMAIL_HOST}")
print(f"Port: {settings.EMAIL_PORT}")
print(f"From: {settings.DEFAULT_FROM_EMAIL}")
```

#### Resend Verification Manually
```python
python manage.py shell
from django.contrib.auth.models import User
from authentication.models import EmailVerification

user = User.objects.get(email='user@example.com')
verification = EmailVerification.objects.get(user=user)
new_token = verification.regenerate_token()
# Manually trigger email send
```

---

## Security Considerations

### 1. Token Security
- **UUID4 tokens**: Cryptographically secure random tokens
- **One-time use**: Tokens invalidated after use
- **Expiration**: Automatic expiry (72h verification, 24h reset)

### 2. Rate Limiting
```python
# Applied to sensitive views
@ratelimit(key='ip', rate='5/h', method='POST', block=True)
class CandidateSignupView(CreateView):
    # Prevents email bombing
```

### 3. Email Validation
```python
# Validate email format
from django.core.validators import validate_email

try:
    validate_email(email)
except ValidationError:
    # Invalid email format
```

### 4. CSRF Protection
```html
<!-- All forms include CSRF token -->
<form method="post">
    {% csrf_token %}
    <!-- form fields -->
</form>
```

### 5. Information Disclosure Prevention
```python
# Don't reveal if email exists
messages.info(
    request,
    'If account exists, instructions will be sent.'
)
```

### 6. SQL Injection Prevention
```python
# Use Django ORM (parameterized queries)
User.objects.get(email=email)  # Safe
# Never use raw SQL with user input
```

### 7. HTML Injection Prevention
```python
# Templates auto-escape HTML
{{ user_input }}  # Escaped
{{ user_input|safe }}  # Only if trusted
```

---

## API Reference

### Email Verification Endpoints

#### POST /auth/signup/
Creates new user account and sends verification email.

**Request:**
```json
{
    "username": "testuser",
    "email": "test@example.com",
    "password1": "SecurePass123!",
    "password2": "SecurePass123!",
    "first_name": "Test",
    "last_name": "User"
}
```

**Response:**
- Success: Redirect to login with success message
- Failure: Form with validation errors

#### GET /auth/verify-email/<uuid:token>/
Verifies email address using token.

**Response:**
- Valid token: Activates account, redirects to login
- Expired token: Error message, option to resend
- Invalid token: Error message

#### POST /auth/resend-verification/
Resends verification email.

**Request:**
```json
{
    "email": "test@example.com"
}
```

### Password Reset Endpoints

#### POST /auth/forgot-password/
Initiates password reset process.

**Request:**
```json
{
    "email": "test@example.com"
}
```

#### GET /auth/reset-password/<uuid:token>/
Displays password reset form.

#### POST /auth/reset-password/<uuid:token>/
Updates user password.

**Request:**
```json
{
    "password": "NewSecurePass123!",
    "password_confirm": "NewSecurePass123!"
}
```

---

## Deployment Checklist

### Pre-Production
- [ ] Request AWS SES production access
- [ ] Verify sending domain (electnepal.com)
- [ ] Configure DKIM signing
- [ ] Setup SPF records
- [ ] Configure bounce handling with SNS
- [ ] Test with production email addresses
- [ ] Setup email monitoring dashboard
- [ ] Configure CloudWatch alarms

### Security
- [ ] Rotate AWS SES credentials
- [ ] Enable 2FA on AWS account
- [ ] Review rate limiting settings
- [ ] Test CSRF protection
- [ ] Verify SSL/TLS configuration
- [ ] Audit email templates for XSS

### Monitoring
- [ ] Setup email delivery metrics
- [ ] Configure bounce/complaint tracking
- [ ] Create alerting for high bounce rates
- [ ] Monitor email sending quotas
- [ ] Setup log aggregation

### Testing
- [ ] Test all email flows in staging
- [ ] Verify email rendering across clients
- [ ] Test with various email providers
- [ ] Confirm mobile responsiveness
- [ ] Load test email sending capacity

### Documentation
- [ ] Document SES configuration
- [ ] Create runbook for common issues
- [ ] Document email template changes process
- [ ] Train support team on email system

---

## Maintenance Tasks

### Daily
- Monitor email logs for errors
- Check SES sending metrics
- Review bounce/complaint rates

### Weekly
- Analyze email delivery performance
- Review and clean up old tokens
- Check for unusual email patterns

### Monthly
- Rotate email logs
- Review and update email templates
- Audit email security settings
- Update documentation

### Cleanup Scripts

#### Remove Expired Tokens
```python
# Run as management command
from authentication.models import EmailVerification, PasswordResetToken
from django.utils import timezone
from datetime import timedelta

# Clean expired email verifications
expired_verifications = EmailVerification.objects.filter(
    is_verified=False,
    created_at__lt=timezone.now() - timedelta(hours=72)
)
print(f"Deleting {expired_verifications.count()} expired verifications")
expired_verifications.delete()

# Clean used/expired password reset tokens
expired_resets = PasswordResetToken.objects.filter(
    models.Q(is_used=True) |
    models.Q(created_at__lt=timezone.now() - timedelta(hours=24))
)
print(f"Deleting {expired_resets.count()} expired/used reset tokens")
expired_resets.delete()
```

---

## Contact & Support

- **Technical Issues**: electnepal5@gmail.com
- **AWS SES Support**: AWS Support Console
- **Documentation Updates**: Create GitHub issue
- **Emergency Contact**: System Administrator

---

*Last Updated: January 2025*
*Version: 1.0*
*Status: Production Ready (pending SES production access)*