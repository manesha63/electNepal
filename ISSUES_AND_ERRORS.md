# ElectNepal - Issues and Errors Documentation

## Critical Issues (Production Blockers)

### 1. 🔴 Missing Email Templates - WILL CRASH
**Severity**: CRITICAL
**Impact**: All email features will fail with `TemplateDoesNotExist` error
**Location**: Multiple views reference non-existent templates

**Missing Files**:
```
templates/authentication/emails/email_verification.html
templates/authentication/emails/password_reset.html
templates/candidates/emails/registration_confirmation.html
templates/candidates/emails/admin_notification.html
templates/candidates/emails/approval_notification.html
templates/candidates/emails/rejection_notification.html
```

**Affected Features**:
- User registration email verification
- Password reset emails
- Candidate registration confirmation
- Admin notification for new candidates
- Candidate approval/rejection notifications

**Fix Required**:
```bash
# Create template directories
mkdir -p templates/authentication/emails
mkdir -p templates/candidates/emails

# Create all 6 template files with proper HTML structure
```

### 2. 🔴 Email Configuration Not Set
**Severity**: CRITICAL
**Location**: `settings/email.py`

**Issue**:
- `EMAIL_HOST_PASSWORD` is empty
- No AWS SES credentials configured
- SMTP settings incomplete

**Impact**: Even if templates exist, emails won't send

**Fix Required**:
```python
# .env file
EMAIL_HOST_PASSWORD=your-app-password
# OR
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_SES_REGION=us-east-1
```

## High Priority Issues

### 3. 🟠 Admin Bulk Reject Doesn't Send Emails
**Severity**: HIGH
**Location**: `candidates/admin.py:156`

**Code Issue**:
```python
def reject_candidates(self, request, queryset):
    # BUG: Uses update() which doesn't trigger save() signals
    updated = queryset.update(
        status='rejected',
        admin_notes='Bulk rejected'
    )
    # No emails sent!
```

**Fix**:
```python
def reject_candidates(self, request, queryset):
    count = 0
    for candidate in queryset.filter(status='pending'):
        candidate.status = 'rejected'
        candidate.admin_notes = 'Bulk rejected'
        candidate.save()  # Triggers post_save signal for email
        count += 1
```

### 4. 🟠 Email Verification Not Enforced
**Severity**: HIGH
**Location**: `authentication/views.py`

**Issue**: Users can login without verifying email
- `is_active=False` is set but not checked during login
- Security risk: unverified emails can access system

**Fix**:
```python
# In LoginView
def form_valid(self, form):
    user = form.get_user()
    if not user.is_active:
        messages.error(self.request, 'Please verify your email first')
        return redirect('verification-required')
    return super().form_valid(form)
```

### 5. 🟠 Password Reset Flow Incomplete
**Severity**: HIGH
**Location**: `authentication/urls.py`, `authentication/views.py`

**Issue**: Missing `PasswordResetConfirmView`
- Reset email sends link to non-existent view
- Users cannot complete password reset

**Fix**: Implement missing view and URL pattern

## Medium Priority Issues

### 6. 🟡 Bare Except Clauses
**Severity**: MEDIUM
**Locations**:
- `candidates/management/commands/optimize_existing_images.py:58`
- Image optimization code

**Issue**:
```python
try:
    # code
except:  # BAD: Catches KeyboardInterrupt, SystemExit, etc.
    pass
```

**Fix**:
```python
try:
    # code
except (IOError, OSError, ValueError) as e:
    logger.error(f"Image optimization failed: {e}")
```

### 7. 🟡 Translation Fallback Copies English
**Severity**: MEDIUM
**Location**: `candidates/translation.py:277-279`

**Issue**:
```python
if not translated_text:
    return original_text  # Copies English to Nepali field
```

**Better Approach**:
```python
if not translated_text:
    return ""  # Leave empty for manual translation
```

### 8. 🟡 No Search Result Highlighting
**Severity**: MEDIUM
**Location**: `candidates/api_views.py`

**Issue**: Search results don't highlight matched terms
**Fix**: Implement PostgreSQL `ts_headline` function

### 9. 🟡 Missing Logging for Failed Emails
**Severity**: MEDIUM
**Location**: Multiple email sending locations

**Issue**: Email failures are silently caught
**Fix**: Add proper logging

## Low Priority Issues

### 10. 🟢 Limited Sort Options
**Severity**: LOW
**Location**: `candidates/api_views.py`

**Current**: Only newest/relevance sorting
**Missing**: A-Z, Z-A, most viewed, recently updated

### 11. 🟢 No Email Template Preview
**Severity**: LOW
**Location**: Admin interface

**Issue**: Admins can't preview emails before sending
**Solution**: Add email preview functionality

### 12. 🟢 No Retry for Failed Translations
**Severity**: LOW
**Location**: `candidates/translation.py`

**Issue**: Failed translations not retried
**Solution**: Implement retry logic with exponential backoff

## Performance Issues

### 13. ⚡ Translation API Blocking
**Severity**: MEDIUM
**Location**: `candidates/models.py` save method

**Issue**:
- Synchronous translation can block for 10-30 seconds
- Already mitigated with async translation

**Current Mitigation**: AsyncTranslator runs in background thread

### 14. ⚡ N+1 Queries Possible
**Severity**: LOW
**Location**: Various views

**Issue**: Some views don't use `select_related`
**Fix**: Add `select_related('province', 'district', 'municipality')`

## Security Considerations

### 15. 🔒 Sensitive Data in Logs
**Severity**: MEDIUM
**Location**: Various logging statements

**Issue**: User emails/phones might be logged
**Fix**: Sanitize logs, use structured logging

### 16. 🔒 Rate Limiting Gaps
**Severity**: LOW
**Location**: Some API endpoints

**Issue**: Not all endpoints have rate limiting
**Fix**: Add rate limiting to all public endpoints

## Data Integrity Issues

### 17. 📊 Orphaned User Accounts
**Severity**: LOW
**Location**: Database

**Issue**: Deleted candidates leave User accounts
**Fix**: CASCADE delete or cleanup command

### 18. 📊 Translation Flag Inconsistency
**Severity**: LOW
**Location**: Database

**Issue**: Some `is_mt_*` flags may be incorrect
**Fix**: Management command to verify/fix flags

## Summary Statistics

- **Critical Issues**: 2
- **High Priority**: 4
- **Medium Priority**: 6
- **Low Priority**: 6
- **Total Issues**: 18

## Immediate Action Required

1. **Create 6 email templates** - Without these, production will crash
2. **Configure email settings** - Add credentials to .env
3. **Fix bulk reject** - Simple code change
4. **Enforce email verification** - Security risk

## Testing Recommendations

### Test Email System
```python
# Test all email sending paths
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Body', 'from@example.com', ['to@example.com'])
```

### Test Templates Exist
```python
# Check if templates render
from django.template.loader import get_template
templates = [
    'authentication/emails/email_verification.html',
    'authentication/emails/password_reset.html',
    # ... etc
]
for t in templates:
    try:
        get_template(t)
        print(f"✓ {t}")
    except TemplateDoesNotExist:
        print(f"✗ {t} - MISSING!")
```

## Monitoring Recommendations

1. **Set up error tracking** (Sentry)
2. **Monitor email delivery rates**
3. **Track translation API failures**
4. **Log admin actions**
5. **Monitor for template errors**

---

**Last Updated**: January 2025
**Reviewed By**: Code Analysis
**Next Review**: Before production deployment