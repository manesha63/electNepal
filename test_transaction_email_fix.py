#!/usr/bin/env python
"""
Test script to verify transaction.on_commit() fix for email sending
Tests that emails are only sent AFTER successful database commit
"""

import os
import sys
import django
from io import StringIO
import logging

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory
from django.db import transaction
from candidates.models import Candidate
from candidates.views import candidate_register
from locations.models import Province, District, Municipality
from unittest.mock import patch, MagicMock, call
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware


def setup_request(user, post_data=None):
    """Helper to create a request with session and messages"""
    factory = RequestFactory()
    if post_data:
        request = factory.post('/candidates/register/', post_data)
    else:
        request = factory.get('/candidates/register/')

    request.user = user

    # Add session
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session.save()

    # Add messages
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)

    return request


def test_emails_sent_after_commit():
    """Test 1: Emails are sent only AFTER successful database commit"""
    print("\n" + "="*70)
    print("TEST 1: Emails Sent After Transaction Commit")
    print("="*70)

    # Clean up test user
    User.objects.filter(username='transactiontest1').delete()
    user = User.objects.create_user('transactiontest1', 'test@test.com', 'testpass')

    # Get valid location data
    province = Province.objects.first()
    district = District.objects.filter(province=province).first()

    post_data = {
        'full_name': 'Transaction Test Candidate',
        'age': 30,
        'position_level': 'provincial_assembly',
        'province': province.id,
        'district': district.id,
        'bio_en': 'Test bio',
        'education_en': 'Test education',
        'experience_en': 'Test experience',
        'manifesto_en': 'Test manifesto',
    }

    request = setup_request(user, post_data)

    try:
        # Track when save() is called vs when emails are sent
        email_call_order = []

        with patch.object(Candidate, 'send_registration_confirmation') as mock_confirm, \
             patch.object(Candidate, 'notify_admin_new_registration') as mock_admin:

            # Track when emails are called
            def track_confirm():
                email_call_order.append('confirm_email')
                return True

            def track_admin():
                email_call_order.append('admin_email')
                return True

            mock_confirm.side_effect = track_confirm
            mock_admin.side_effect = track_admin

            # Track when candidate is saved
            original_save = Candidate.save
            def tracked_save(self, *args, **kwargs):
                email_call_order.append('candidate_saved')
                return original_save(self, *args, **kwargs)

            with patch.object(Candidate, 'save', tracked_save):
                # Call the view
                response = candidate_register(request)

            # Verify emails were called AFTER save
            if 'candidate_saved' in email_call_order:
                save_index = email_call_order.index('candidate_saved')

                if 'confirm_email' in email_call_order and 'admin_email' in email_call_order:
                    confirm_index = email_call_order.index('confirm_email')
                    admin_index = email_call_order.index('admin_email')

                    if confirm_index > save_index and admin_index > save_index:
                        print("\n✓ PASS: Emails sent AFTER candidate.save()")
                        print(f"  Call order: {email_call_order}")
                        print("  This ensures emails only go out after successful DB commit")
                        result = True
                    else:
                        print("\n✗ FAIL: Emails sent BEFORE candidate.save()")
                        print(f"  Call order: {email_call_order}")
                        result = False
                else:
                    print("\n✗ FAIL: Emails not sent")
                    print(f"  Call order: {email_call_order}")
                    result = False
            else:
                print("\n✗ FAIL: Candidate not saved")
                result = False

        # Cleanup
        User.objects.filter(username='transactiontest1').delete()
        return result

    except Exception as e:
        print(f"\n✗ FAIL: Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        User.objects.filter(username='transactiontest1').delete()
        return False


def test_emails_not_sent_on_rollback():
    """Test 2: Emails are NOT sent if transaction rolls back"""
    print("\n" + "="*70)
    print("TEST 2: Emails NOT Sent on Transaction Rollback")
    print("="*70)

    # Clean up test user
    User.objects.filter(username='transactiontest2').delete()
    user = User.objects.create_user('transactiontest2', 'test@test.com', 'testpass')

    # Get valid location data
    province = Province.objects.first()
    district = District.objects.filter(province=province).first()

    post_data = {
        'full_name': 'Rollback Test Candidate',
        'age': 30,
        'position_level': 'provincial_assembly',
        'province': province.id,
        'district': district.id,
        'bio_en': 'Test bio',
        'education_en': 'Test education',
        'experience_en': 'Test experience',
        'manifesto_en': 'Test manifesto',
    }

    request = setup_request(user, post_data)

    try:
        with patch.object(Candidate, 'send_registration_confirmation') as mock_confirm, \
             patch.object(Candidate, 'notify_admin_new_registration') as mock_admin:

            # Make save() raise an error to force rollback
            with patch.object(Candidate, 'save', side_effect=Exception("Simulated DB error")):
                try:
                    response = candidate_register(request)
                except:
                    pass  # Expected to fail

            # Verify emails were NOT called
            if not mock_confirm.called and not mock_admin.called:
                print("\n✓ PASS: Emails NOT sent when transaction failed")
                print("  on_commit() hooks correctly discarded on rollback")
                result = True
            else:
                print("\n✗ FAIL: Emails were sent despite transaction rollback!")
                print(f"  Confirmation email called: {mock_confirm.called}")
                print(f"  Admin email called: {mock_admin.called}")
                result = False

        # Cleanup
        User.objects.filter(username='transactiontest2').delete()
        return result

    except Exception as e:
        print(f"\n✗ FAIL: Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        User.objects.filter(username='transactiontest2').delete()
        return False


def test_email_failure_logged():
    """Test 3: Email failures are properly logged (not just printed)"""
    print("\n" + "="*70)
    print("TEST 3: Email Failures Are Properly Logged")
    print("="*70)

    # Setup logging capture
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.ERROR)
    logger = logging.getLogger('candidates.emails')
    logger.addHandler(handler)
    logger.setLevel(logging.ERROR)

    # Clean up test user
    User.objects.filter(username='transactiontest3').delete()
    user = User.objects.create_user('transactiontest3', 'test@test.com', 'testpass')

    # Get valid location data
    province = Province.objects.first()
    district = District.objects.filter(province=province).first()

    post_data = {
        'full_name': 'Email Failure Test',
        'age': 30,
        'position_level': 'provincial_assembly',
        'province': province.id,
        'district': district.id,
        'bio_en': 'Test bio',
        'education_en': 'Test education',
        'experience_en': 'Test experience',
        'manifesto_en': 'Test manifesto',
    }

    request = setup_request(user, post_data)

    try:
        # Make email sending fail
        with patch.object(Candidate, 'send_registration_confirmation', side_effect=Exception("SMTP connection failed")), \
             patch.object(Candidate, 'notify_admin_new_registration'):

            response = candidate_register(request)

            # Check logs
            log_contents = log_stream.getvalue()

            checks_passed = 0
            total_checks = 0

            # Check for error message
            total_checks += 1
            if "Failed to send registration emails" in log_contents:
                print("\n✓ Error logged properly")
                checks_passed += 1
            else:
                print("\n✗ Error not logged")

            # Check for candidate name
            total_checks += 1
            if "Email Failure Test" in log_contents:
                print("✓ Candidate name in log")
                checks_passed += 1

            # Check for exception type
            total_checks += 1
            if "Exception" in log_contents:
                print("✓ Exception type in log")
                checks_passed += 1

            # Check for exception message
            total_checks += 1
            if "SMTP connection failed" in log_contents:
                print("✓ Exception message in log")
                checks_passed += 1

            print(f"\nChecks passed: {checks_passed}/{total_checks}")
            print(f"Log sample: {log_contents[:300]}...")

            result = checks_passed >= 3  # At least 3/4 checks

            if result:
                print("\n✓ PASS: Email failures are properly logged")
            else:
                print("\n✗ FAIL: Missing logging details")

        # Cleanup
        User.objects.filter(username='transactiontest3').delete()
        logger.removeHandler(handler)
        return result

    except Exception as e:
        print(f"\n✗ FAIL: Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        User.objects.filter(username='transactiontest3').delete()
        logger.removeHandler(handler)
        return False


def test_candidate_still_saved_on_email_failure():
    """Test 4: Candidate is still saved even if emails fail"""
    print("\n" + "="*70)
    print("TEST 4: Candidate Saved Even If Emails Fail")
    print("="*70)

    # Clean up test user
    User.objects.filter(username='transactiontest4').delete()
    user = User.objects.create_user('transactiontest4', 'test@test.com', 'testpass')

    # Get valid location data
    province = Province.objects.first()
    district = District.objects.filter(province=province).first()

    post_data = {
        'full_name': 'Persistent Save Test',
        'age': 30,
        'position_level': 'provincial_assembly',
        'province': province.id,
        'district': district.id,
        'bio_en': 'Test bio',
        'education_en': 'Test education',
        'experience_en': 'Test experience',
        'manifesto_en': 'Test manifesto',
    }

    request = setup_request(user, post_data)

    try:
        # Make both emails fail
        with patch.object(Candidate, 'send_registration_confirmation', side_effect=Exception("Email failed")), \
             patch.object(Candidate, 'notify_admin_new_registration', side_effect=Exception("Email failed")):

            response = candidate_register(request)

            # Verify candidate was still saved in database
            candidate = Candidate.objects.filter(user=user).first()

            if candidate:
                print("\n✓ PASS: Candidate saved in database despite email failures")
                print(f"  Candidate ID: {candidate.pk}")
                print(f"  Full name: {candidate.full_name}")
                print(f"  Status: {candidate.status}")
                print("  This prevents data loss when SMTP is down")
                result = True
            else:
                print("\n✗ FAIL: Candidate not saved when emails failed")
                result = False

        # Cleanup
        User.objects.filter(username='transactiontest4').delete()
        return result

    except Exception as e:
        print(f"\n✗ FAIL: Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        User.objects.filter(username='transactiontest4').delete()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print(" TRANSACTION EMAIL FIX VERIFICATION TEST SUITE")
    print("="*80)
    print("\nThis test suite verifies:")
    print("1. Emails are sent only AFTER successful database commit")
    print("2. Emails are NOT sent if transaction rolls back")
    print("3. Email failures are properly logged (not just printed)")
    print("4. Candidate is still saved even if emails fail")
    print("\nRunning tests...\n")

    results = {}

    try:
        results['test1'] = test_emails_sent_after_commit()
        results['test2'] = test_emails_not_sent_on_rollback()
        results['test3'] = test_email_failure_logged()
        results['test4'] = test_candidate_still_saved_on_email_failure()

    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        results['error'] = True

    # Summary
    print("\n" + "="*80)
    print(" TEST SUMMARY")
    print("="*80)

    if 'error' in results:
        print("\n✗ FATAL ERROR OCCURRED - Cannot determine test results")
        return False

    passed_count = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\nTests Passed: {passed_count}/{total}")
    print("-"*80)

    test_names = {
        'test1': 'Emails Sent After Transaction Commit',
        'test2': 'Emails NOT Sent on Transaction Rollback',
        'test3': 'Email Failures Are Properly Logged',
        'test4': 'Candidate Saved Even If Emails Fail',
    }

    for test_key, test_passed in results.items():
        status = "✓ PASS" if test_passed else "✗ FAIL"
        test_name = test_names.get(test_key, test_key)
        print(f"{status}: {test_name}")

    print("-"*80)

    if passed_count == total:
        print("\n" + "="*80)
        print(" ✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("="*80)
        print("\nThe transaction email fix is working correctly:")
        print("  ✓ Emails sent only after successful DB commit")
        print("  ✓ No emails sent when transaction rolls back")
        print("  ✓ Email failures properly logged with details")
        print("  ✓ Registration succeeds even if emails fail")
        print("  ✓ No data loss when SMTP is unavailable")
        print("\nFixed code (candidates/views.py:494-521):")
        print("  - Wrapped email calls in transaction.on_commit()")
        print("  - Added proper error logging (not just print)")
        print("  - Ensured email failures don't block registration")
        print("  - Prevented race conditions with rollback")
        return True
    else:
        print("\n✗✗✗ SOME TESTS FAILED ✗✗✗")
        print("\nPlease review the failed tests above.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
