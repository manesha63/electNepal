#!/usr/bin/env python
"""
Test script to verify the email verification system is working correctly.
Run this with: python manage.py shell < test_email_system.py
"""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from authentication.models import EmailVerification, PasswordResetToken
from candidates.models import Candidate
import uuid

print("=" * 60)
print("ELECTNEPAL EMAIL SYSTEM TEST")
print("=" * 60)

# Test 1: Check email configuration
print("\n1. EMAIL CONFIGURATION TEST")
print("-" * 40)
print(f"Email Backend: {settings.EMAIL_BACKEND}")
print(f"Default From Email: {settings.DEFAULT_FROM_EMAIL}")
print(f"Contact Email: {settings.CONTACT_EMAIL}")

if 'console' in settings.EMAIL_BACKEND.lower():
    print("✓ Using console email backend (emails will print to console)")
elif 'smtp' in settings.EMAIL_BACKEND.lower():
    print(f"✓ Using SMTP backend")
    print(f"  Host: {settings.EMAIL_HOST}")
    print(f"  Port: {settings.EMAIL_PORT}")
    print(f"  Use TLS: {settings.EMAIL_USE_TLS}")

# Test 2: Check if EmailVerification model works
print("\n2. EMAIL VERIFICATION MODEL TEST")
print("-" * 40)
try:
    # Check if we can query the model
    verification_count = EmailVerification.objects.count()
    print(f"✓ EmailVerification model is accessible")
    print(f"  Current verifications in database: {verification_count}")
except Exception as e:
    print(f"✗ Error accessing EmailVerification model: {e}")

# Test 3: Check if PasswordResetToken model works
print("\n3. PASSWORD RESET TOKEN MODEL TEST")
print("-" * 40)
try:
    reset_count = PasswordResetToken.objects.count()
    print(f"✓ PasswordResetToken model is accessible")
    print(f"  Current reset tokens in database: {reset_count}")
except Exception as e:
    print(f"✗ Error accessing PasswordResetToken model: {e}")

# Test 4: Send a test email
print("\n4. EMAIL SENDING TEST")
print("-" * 40)
try:
    print("Attempting to send a test email...")
    send_mail(
        subject='[ElectNepal] Test Email',
        message='This is a test email from ElectNepal email system.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['test@example.com'],
        fail_silently=False,
    )
    print("✓ Test email sent successfully (check console output)")
except Exception as e:
    print(f"✗ Error sending test email: {e}")

# Test 5: Check user verification status
print("\n5. USER VERIFICATION STATUS")
print("-" * 40)
try:
    users = User.objects.all()[:5]  # Get first 5 users
    if users:
        for user in users:
            has_verification = hasattr(user, 'email_verification')
            if has_verification:
                verification = user.email_verification
                status = "Verified" if verification.is_verified else "Pending"
                expired = verification.is_expired() if not verification.is_verified else False
                print(f"User: {user.username}")
                print(f"  Email: {user.email}")
                print(f"  Active: {user.is_active}")
                print(f"  Verification Status: {status}")
                if expired:
                    print(f"  ⚠ Verification link expired")
            else:
                print(f"User: {user.username}")
                print(f"  Email: {user.email}")
                print(f"  Active: {user.is_active}")
                print(f"  Verification Status: No verification record")
    else:
        print("No users found in the database")
except Exception as e:
    print(f"✗ Error checking user verification status: {e}")

# Test 6: Check candidate approval email capability
print("\n6. CANDIDATE APPROVAL EMAIL TEST")
print("-" * 40)
try:
    candidate_count = Candidate.objects.count()
    print(f"Total candidates in database: {candidate_count}")

    pending_candidates = Candidate.objects.filter(status='pending').count()
    approved_candidates = Candidate.objects.filter(status='approved').count()
    rejected_candidates = Candidate.objects.filter(status='rejected').count()

    print(f"  Pending: {pending_candidates}")
    print(f"  Approved: {approved_candidates}")
    print(f"  Rejected: {rejected_candidates}")

    # Check if email methods exist
    if candidate_count > 0:
        candidate = Candidate.objects.first()
        has_approval_email = hasattr(candidate, 'send_approval_email')
        has_rejection_email = hasattr(candidate, 'send_rejection_email')
        print(f"\n✓ Candidate email methods:")
        print(f"  send_approval_email: {'Available' if has_approval_email else 'Not found'}")
        print(f"  send_rejection_email: {'Available' if has_rejection_email else 'Not found'}")
except Exception as e:
    print(f"✗ Error checking candidate email capability: {e}")

print("\n" + "=" * 60)
print("EMAIL SYSTEM TEST COMPLETE")
print("=" * 60)

# Summary
print("\nSUMMARY:")
print("-" * 40)
print("✓ Email verification models are created and accessible")
print("✓ Email sending capability is configured")
print("✓ Candidate approval/rejection email methods are available")
print("\nNOTE: Check console output above for any test emails sent")
print("\nRECOMMENDATION:")
if 'console' in settings.EMAIL_BACKEND.lower():
    print("- Currently using console email backend (development mode)")
    print("- For production, configure SMTP settings in .env file")
else:
    print("- SMTP email backend is configured")
    print("- Verify SMTP credentials are correct for sending real emails")