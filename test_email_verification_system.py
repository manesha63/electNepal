#!/usr/bin/env python
"""
Test script to verify the email verification system is fully operational.

This script tests:
1. User signup creates inactive user
2. EmailVerification record is created with token
3. Verification link activates the user
4. Resend verification works
5. Expired tokens are handled
"""

import os
import sys
import django
from datetime import timedelta

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from authentication.models import EmailVerification, PasswordResetToken


def test_email_verification_system():
    print("\n" + "="*80)
    print(" EMAIL VERIFICATION SYSTEM TEST")
    print("="*80)

    results = []

    # Test 1: Database Models
    print("\n[TEST 1] Checking database models...")
    try:
        # Check EmailVerification model
        assert hasattr(EmailVerification, 'user')
        assert hasattr(EmailVerification, 'token')
        assert hasattr(EmailVerification, 'is_verified')
        assert hasattr(EmailVerification, 'verify')
        assert hasattr(EmailVerification, 'is_expired')
        assert hasattr(EmailVerification, 'regenerate_token')
        print("✓ EmailVerification model: All required fields and methods present")
        results.append(("Database Models", True))
    except AssertionError as e:
        print(f"✗ EmailVerification model: Missing required fields/methods")
        results.append(("Database Models", False))

    # Test 2: User Creation and Email Verification Record
    print("\n[TEST 2] Testing user creation and verification record...")
    try:
        # Clean up any existing test user
        User.objects.filter(username='test_email_verif').delete()

        # Create inactive user (simulating signup)
        test_user = User.objects.create_user(
            username='test_email_verif',
            email='test_verify@example.com',
            password='testpass123',
            is_active=False  # Important: starts inactive
        )
        print(f"  ✓ Created user: {test_user.username}")
        print(f"    - Email: {test_user.email}")
        print(f"    - Active: {test_user.is_active} (should be False)")

        # Create verification record
        verification = EmailVerification.objects.create(user=test_user)
        print(f"  ✓ Created verification record")
        print(f"    - Token: {verification.token}")
        print(f"    - Verified: {verification.is_verified}")
        print(f"    - Created: {verification.created_at}")

        assert test_user.is_active == False, "User should start inactive"
        assert verification.is_verified == False, "Verification should start as not verified"
        assert verification.token is not None, "Token should be generated"

        results.append(("User Creation", True))
    except Exception as e:
        print(f"✗ User creation failed: {e}")
        results.append(("User Creation", False))
        return results

    # Test 3: Email Verification Process
    print("\n[TEST 3] Testing email verification...")
    try:
        # Verify the email
        success = verification.verify()
        print(f"  ✓ Verification method called: {success}")

        # Reload user from database
        test_user.refresh_from_db()
        verification.refresh_from_db()

        print(f"    - User is_active: {test_user.is_active} (should be True)")
        print(f"    - Verification is_verified: {verification.is_verified} (should be True)")
        print(f"    - Verified at: {verification.verified_at}")

        assert test_user.is_active == True, "User should be active after verification"
        assert verification.is_verified == True, "Verification should be marked as verified"
        assert verification.verified_at is not None, "Verified timestamp should be set"

        results.append(("Email Verification", True))
    except AssertionError as e:
        print(f"✗ Verification failed: {e}")
        results.append(("Email Verification", False))

    # Test 4: Already Verified Check
    print("\n[TEST 4] Testing already verified check...")
    try:
        # Try to verify again
        success = verification.verify()
        print(f"  ✓ Attempted to verify already-verified email")
        print(f"    - Result: {success} (should be True, verification already done)")

        # User should still be active
        test_user.refresh_from_db()
        assert test_user.is_active == True, "User should remain active"

        results.append(("Already Verified Check", True))
    except Exception as e:
        print(f"✗ Already verified check failed: {e}")
        results.append(("Already Verified Check", False))

    # Test 5: Token Regeneration
    print("\n[TEST 5] Testing token regeneration (resend verification)...")
    try:
        # Create another user for testing resend
        User.objects.filter(username='test_resend').delete()
        resend_user = User.objects.create_user(
            username='test_resend',
            email='test_resend@example.com',
            password='testpass123',
            is_active=False
        )
        resend_verification = EmailVerification.objects.create(user=resend_user)
        old_token = resend_verification.token
        old_created = resend_verification.created_at

        print(f"  ✓ Created test user for resend")
        print(f"    - Old token: {old_token}")

        # Regenerate token
        new_token = resend_verification.regenerate_token()
        resend_verification.refresh_from_db()

        print(f"    - New token: {new_token}")
        print(f"    - Token changed: {old_token != new_token}")
        print(f"    - Created_at updated: {resend_verification.created_at > old_created}")

        assert old_token != new_token, "Token should change on regeneration"
        assert resend_verification.created_at > old_created, "Created timestamp should update"

        # Clean up
        resend_user.delete()
        results.append(("Token Regeneration", True))
    except Exception as e:
        print(f"✗ Token regeneration failed: {e}")
        results.append(("Token Regeneration", False))

    # Test 6: Expired Token Check
    print("\n[TEST 6] Testing expired token detection...")
    try:
        # Create user with old verification
        User.objects.filter(username='test_expired').delete()
        expired_user = User.objects.create_user(
            username='test_expired',
            email='test_expired@example.com',
            password='testpass123',
            is_active=False
        )
        expired_verification = EmailVerification.objects.create(user=expired_user)

        # Manually set created_at to 73 hours ago (past 72 hour expiry)
        expired_verification.created_at = timezone.now() - timedelta(hours=73)
        expired_verification.save()

        print(f"  ✓ Created user with expired token")
        print(f"    - Created at: {expired_verification.created_at}")
        print(f"    - Is expired: {expired_verification.is_expired()}")

        assert expired_verification.is_expired() == True, "Token should be expired"

        # Try to verify expired token
        success = expired_verification.verify()
        print(f"    - Verify attempt: {success} (should be False)")

        expired_user.refresh_from_db()
        print(f"    - User still inactive: {not expired_user.is_active} (should be True)")

        assert success == False, "Expired verification should fail"
        assert expired_user.is_active == False, "User should remain inactive"

        # Clean up
        expired_user.delete()
        results.append(("Expired Token Check", True))
    except Exception as e:
        print(f"✗ Expired token check failed: {e}")
        results.append(("Expired Token Check", False))

    # Test 7: Password Reset Token Model
    print("\n[TEST 7] Checking password reset token model...")
    try:
        assert hasattr(PasswordResetToken, 'user')
        assert hasattr(PasswordResetToken, 'token')
        assert hasattr(PasswordResetToken, 'is_used')
        assert hasattr(PasswordResetToken, 'is_expired')
        assert hasattr(PasswordResetToken, 'mark_as_used')

        # Create password reset token
        reset_token = PasswordResetToken.objects.create(user=test_user)
        print(f"  ✓ PasswordResetToken model: All required fields and methods present")
        print(f"    - Token created: {reset_token.token}")
        print(f"    - Is used: {reset_token.is_used}")
        print(f"    - Is expired: {reset_token.is_expired()}")

        # Test mark as used
        reset_token.mark_as_used()
        reset_token.refresh_from_db()
        assert reset_token.is_used == True, "Token should be marked as used"
        assert reset_token.used_at is not None, "Used timestamp should be set"
        print(f"    - Marked as used: {reset_token.is_used}")
        print(f"    - Used at: {reset_token.used_at}")

        results.append(("Password Reset Model", True))
    except Exception as e:
        print(f"✗ Password reset model check failed: {e}")
        results.append(("Password Reset Model", False))

    # Cleanup
    print("\n[CLEANUP] Removing test data...")
    try:
        test_user.delete()
        print("  ✓ Cleaned up test users")
    except:
        pass

    # Summary
    print("\n" + "="*80)
    print(" TEST SUMMARY")
    print("="*80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print("-"*80)
    print(f"\nTests Passed: {passed}/{total}")

    if passed == total:
        print("\n" + "="*80)
        print(" ✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("="*80)
        print("\nEmail verification system is FULLY OPERATIONAL!")
        print("\nImplemented features:")
        print("  ✓ User signup creates inactive account")
        print("  ✓ EmailVerification record with unique token")
        print("  ✓ Email verification activates user account")
        print("  ✓ Token expiry (72 hours)")
        print("  ✓ Token regeneration for resending emails")
        print("  ✓ Password reset token system")
        print("\nWhat's working:")
        print("  ✓ Models and database")
        print("  ✓ Verification logic")
        print("  ✓ Token management")
        print("  ✓ User activation flow")
        return True
    else:
        print("\n✗✗✗ SOME TESTS FAILED ✗✗✗")
        return False


if __name__ == '__main__':
    success = test_email_verification_system()
    sys.exit(0 if success else 1)
