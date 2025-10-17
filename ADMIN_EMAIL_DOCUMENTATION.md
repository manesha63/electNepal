# Admin Features & Email Verification Documentation

## ⚠️ CRITICAL ISSUE ALERT

**The email system is currently BROKEN due to missing email templates. All email-sending features will crash in production.**

### Missing Email Templates (6 files)
These templates are referenced in code but DO NOT EXIST:
1. `templates/authentication/emails/email_verification.html`
2. `templates/authentication/emails/password_reset.html`
3. `templates/candidates/emails/registration_confirmation.html`
4. `templates/candidates/emails/admin_notification.html`
5. `templates/candidates/emails/approval_notification.html`
6. `templates/candidates/emails/rejection_notification.html`

**Impact**: Any action that triggers email sending will fail with `TemplateDoesNotExist` error.

---

## Admin Interface Features

### Overview

The Django admin interface has been extensively customized for managing candidates, locations, and users with color-coded status badges, bulk actions, and email notifications.

### 1. Candidate Admin (`candidates/admin.py`)

#### Custom Display

```python
@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = [
        'full_name',
        'position_level',
        'status_badge',  # Color-coded status
        'province',
        'district',
        'municipality',
        'ward_number',
        'created_at',
        'approved_at'
    ]

    def status_badge(self, obj):
        """Display color-coded status badges"""
        colors = {
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
```

#### Filters and Search

```python
list_filter = [
    'status',
    'position_level',
    'province',
    'district',
    'created_at',
    'approved_at'
]

search_fields = [
    'full_name',
    'email',
    'phone_number',
    'bio_en',
    'bio_ne'
]

ordering = ['-created_at']
```

#### Bulk Actions

```python
actions = ['approve_candidates', 'reject_candidates']

def approve_candidates(self, request, queryset):
    """Bulk approve with email notifications"""
    count = 0
    for candidate in queryset.filter(status='pending'):
        candidate.status = 'approved'
        candidate.approved_at = timezone.now()
        candidate.approved_by = request.user
        candidate.save()

        # Send approval email (WILL FAIL - template missing)
        try:
            send_approval_email(candidate)
        except TemplateDoesNotExist:
            pass  # Silently fails

        count += 1

    self.message_user(request, f'{count} candidates approved')

def reject_candidates(self, request, queryset):
    """Bulk reject - BROKEN: doesn't send emails"""
    # BUG: Uses update() instead of save(), so no email sent
    updated = queryset.update(
        status='rejected',
        admin_notes='Bulk rejected'
    )
    self.message_user(request, f'{updated} candidates rejected')
    # NOTE: No rejection emails sent!
```

### 2. Location Admin

#### Province Admin
```python
@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['code', 'name_en', 'name_ne', 'district_count']
    search_fields = ['name_en', 'name_ne', 'code']

    def district_count(self, obj):
        return obj.districts.count()
```

#### District Admin
```python
@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['code', 'name_en', 'name_ne', 'province', 'municipality_count']
    list_filter = ['province']
    search_fields = ['name_en', 'name_ne', 'code']
```

#### Municipality Admin
```python
@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ['code', 'name_en', 'name_ne', 'district', 'municipality_type', 'total_wards']
    list_filter = ['municipality_type', 'district__province', 'district']
    search_fields = ['name_en', 'name_ne', 'code']
```

### 3. User Admin Customization

```python
# authentication/admin.py
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class CustomUserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'date_joined']

    # Add candidate link if exists
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj and hasattr(obj, 'candidate'):
            # Add link to candidate profile
            fieldsets += (
                ('Candidate Profile', {
                    'fields': ('view_candidate_link',)
                }),
            )
        return fieldsets
```

## Email Verification System

### Architecture (PARTIALLY IMPLEMENTED)

The email verification system is coded but non-functional due to missing templates.

### 1. User Registration Flow

```python
# authentication/views.py
class SignupView(CreateView):
    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False  # Deactivate until email verified
        user.save()

        # Generate verification token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Build verification URL
        verification_url = self.request.build_absolute_uri(
            reverse('verify-email', kwargs={'uidb64': uid, 'token': token})
        )

        # Send verification email (WILL FAIL)
        try:
            send_mail(
                'Verify your ElectNepal account',
                render_to_string('authentication/emails/email_verification.html', {
                    'user': user,
                    'verification_url': verification_url,
                }),
                'electnepal5@gmail.com',
                [user.email],
                html_message=True
            )
        except TemplateDoesNotExist:
            # Template doesn't exist - email not sent!
            pass

        return redirect('verification-sent')
```

### 2. Email Verification Handler

```python
# authentication/views.py
class VerifyEmailView(View):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, 'Email verified successfully!')
            return redirect('login')
        else:
            messages.error(request, 'Invalid verification link')
            return redirect('signup')
```

### 3. Password Reset Flow

```python
# authentication/views.py
class PasswordResetView(FormView):
    def form_valid(self, form):
        email = form.cleaned_data['email']
        users = User.objects.filter(email=email)

        for user in users:
            # Generate reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Build reset URL
            reset_url = self.request.build_absolute_uri(
                reverse('password-reset-confirm', kwargs={
                    'uidb64': uid,
                    'token': token
                })
            )

            # Send reset email (WILL FAIL)
            try:
                send_mail(
                    'Reset your password',
                    render_to_string('authentication/emails/password_reset.html', {
                        'user': user,
                        'reset_url': reset_url,
                    }),
                    'electnepal5@gmail.com',
                    [user.email]
                )
            except TemplateDoesNotExist:
                pass

        return redirect('password-reset-done')
```

### 4. Candidate Registration Emails

```python
# candidates/models.py
@receiver(post_save, sender=Candidate)
def send_candidate_emails(sender, instance, created, **kwargs):
    if created:
        # Send confirmation to candidate (WILL FAIL)
        try:
            send_mail(
                'Registration Received',
                render_to_string('candidates/emails/registration_confirmation.html', {
                    'candidate': instance
                }),
                'electnepal5@gmail.com',
                [instance.email]
            )
        except TemplateDoesNotExist:
            pass

        # Notify admins (WILL FAIL)
        try:
            admin_emails = User.objects.filter(is_staff=True).values_list('email', flat=True)
            send_mail(
                'New Candidate Registration',
                render_to_string('candidates/emails/admin_notification.html', {
                    'candidate': instance
                }),
                'electnepal5@gmail.com',
                admin_emails
            )
        except TemplateDoesNotExist:
            pass
```

### 5. Approval/Rejection Emails

```python
# candidates/models.py
def send_approval_email(candidate):
    """Send approval notification (WILL FAIL)"""
    try:
        send_mail(
            'Your candidacy has been approved',
            render_to_string('candidates/emails/approval_notification.html', {
                'candidate': candidate
            }),
            'electnepal5@gmail.com',
            [candidate.email]
        )
    except TemplateDoesNotExist:
        logger.error(f'Approval email template missing for {candidate.email}')

def send_rejection_email(candidate):
    """Send rejection notification (WILL FAIL)"""
    try:
        send_mail(
            'Update on your candidacy',
            render_to_string('candidates/emails/rejection_notification.html', {
                'candidate': candidate,
                'reason': candidate.admin_notes
            }),
            'electnepal5@gmail.com',
            [candidate.email]
        )
    except TemplateDoesNotExist:
        logger.error(f'Rejection email template missing for {candidate.email}')
```

## Email Configuration

### Current Settings

```python
# settings/email.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # or AWS SES
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'electnepal5@gmail.com'
EMAIL_HOST_PASSWORD = ''  # Not configured

DEFAULT_FROM_EMAIL = 'ElectNepal <electnepal5@gmail.com>'
SERVER_EMAIL = 'electnepal5@gmail.com'
```

### AWS SES Configuration (For Production)

```python
# .env file
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_SES_REGION=us-east-1

# settings/production.py
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_SES_REGION_NAME = env('AWS_SES_REGION')
AWS_SES_REGION_ENDPOINT = f'email.{AWS_SES_REGION_NAME}.amazonaws.com'
```

## Required Email Templates

### 1. Email Verification Template
```html
<!-- templates/authentication/emails/email_verification.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Verify Your Email</title>
</head>
<body>
    <h2>Welcome to ElectNepal, {{ user.first_name }}!</h2>
    <p>Please verify your email address by clicking the link below:</p>
    <a href="{{ verification_url }}" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
        Verify Email
    </a>
    <p>Or copy this link: {{ verification_url }}</p>
    <p>This link expires in 48 hours.</p>
</body>
</html>
```

### 2. Password Reset Template
```html
<!-- templates/authentication/emails/password_reset.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Password Reset</title>
</head>
<body>
    <h2>Password Reset Request</h2>
    <p>Hi {{ user.first_name }},</p>
    <p>You requested a password reset. Click below to reset:</p>
    <a href="{{ reset_url }}" style="background: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
        Reset Password
    </a>
    <p>If you didn't request this, please ignore this email.</p>
</body>
</html>
```

## Current Status Summary

### ✅ Working Admin Features
- Color-coded status badges
- Bulk approve action (emails fail silently)
- Search and filters
- Custom list displays
- Location hierarchy management

### ❌ Not Working
- **ALL email sending** (templates missing)
- Bulk reject emails (uses .update() not .save())
- Email verification enforcement (users can login without verifying)
- Password reset completion (missing view)

### ⚠️ Issues Found

1. **Critical: Missing Email Templates**
   - Impact: All email features broken
   - Fix: Create 6 template files

2. **Bug: Bulk Reject No Emails**
   - Location: `candidates/admin.py:156`
   - Issue: Uses `queryset.update()` instead of individual `.save()`
   - Fix: Loop through and save individually

3. **Security: Email Not Enforced**
   - Users can login without verifying email
   - Fix: Check `is_active` in login view

4. **Incomplete: Password Reset**
   - Missing `password_reset_confirm` view
   - Fix: Implement the view

## Testing Admin Features

```python
# Test admin actions
def test_bulk_approve(self):
    self.client.login(username='admin', password='admin')

    # Create pending candidates
    candidates = [Candidate.objects.create(...) for _ in range(3)]

    # Bulk approve
    response = self.client.post('/admin/candidates/candidate/', {
        'action': 'approve_candidates',
        '_selected_action': [c.pk for c in candidates]
    })

    # Check approved
    for c in candidates:
        c.refresh_from_db()
        self.assertEqual(c.status, 'approved')
```

## Recommendations

### Immediate Fixes (Production Blockers)

1. **Create Email Templates** (2 hours)
   ```bash
   mkdir -p templates/authentication/emails
   mkdir -p templates/candidates/emails
   # Create all 6 template files
   ```

2. **Fix Bulk Reject** (30 minutes)
   ```python
   def reject_candidates(self, request, queryset):
       for candidate in queryset:
           candidate.status = 'rejected'
           candidate.save()  # Triggers email
   ```

3. **Configure Email Backend** (1 hour)
   - Set up AWS SES or SMTP
   - Add credentials to .env

### Future Improvements

1. **Email Template Management**
   - Use django-templated-email
   - Support bilingual emails
   - Add email preview in admin

2. **Email Queue**
   - Use Celery for async sending
   - Retry failed emails
   - Track email delivery

3. **Admin Dashboard**
   - Add statistics widget
   - Email delivery reports
   - Candidate analytics

---

**Last Updated**: January 2025
**Status**: Admin 95% complete, Email 0% functional
**Critical Issues**: 6 missing email templates