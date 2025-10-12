#!/usr/bin/env python
"""
Manual verification that forms work correctly with sanitization
Tests that forms can still be instantiated and validated
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from django.contrib.auth.models import User
from candidates.models import Candidate
from locations.models import Province, District, Municipality
from candidates.forms import CandidateRegistrationForm, CandidateUpdateForm, CandidateEventForm
from authentication.forms import CandidateSignupForm
from django.utils import timezone
from datetime import timedelta

print("=" * 80)
print("VERIFYING FORMS WORK CORRECTLY")
print("=" * 80)

# Test 1: Check that models can be queried
print("\n1. Checking database access:")
print("-" * 40)
try:
    province_count = Province.objects.count()
    district_count = District.objects.count()
    municipality_count = Municipality.objects.count()
    print(f"✓ PASS: Database accessible")
    print(f"  Provinces: {province_count}, Districts: {district_count}, Municipalities: {municipality_count}")
except Exception as e:
    print(f"✗ FAIL: Database error - {e}")

# Test 2: CandidateEventForm with clean data
print("\n2. Testing CandidateEventForm with clean data:")
print("-" * 40)

clean_event_data = {
    'title_en': 'Community Meeting',
    'description_en': '<p>Join us for a discussion about local issues</p>',
    'location_en': 'Town Hall',
    'event_date': timezone.now() + timedelta(days=7),
    'is_published': True,
}

form = CandidateEventForm(data=clean_event_data)
if form.is_valid():
    print("✓ PASS: Form validates clean data correctly")
    print(f"  Title: {form.cleaned_data['title_en']}")
else:
    print("✗ FAIL: Form rejected clean data")
    print(f"  Errors: {form.errors}")

# Test 3: CandidateEventForm with past date (should fail)
print("\n3. Testing CandidateEventForm rejects past dates:")
print("-" * 40)

past_event_data = {
    'title_en': 'Past Meeting',
    'description_en': 'This was yesterday',
    'location_en': 'Town Hall',
    'event_date': timezone.now() - timedelta(days=1),
    'is_published': True,
}

form = CandidateEventForm(data=past_event_data)
if not form.is_valid() and 'event_date' in form.errors:
    print("✓ PASS: Form correctly rejects past dates")
else:
    print("✗ FAIL: Form should reject past dates")

# Test 4: CandidateSignupForm with valid data
print("\n4. Testing CandidateSignupForm with valid data:")
print("-" * 40)

import random
random_num = random.randint(10000, 99999)

valid_signup_data = {
    'username': f'verifyuser{random_num}',
    'email': f'verify{random_num}@test.com',
    'password1': 'TestPassword123!',
    'password2': 'TestPassword123!',
}

form = CandidateSignupForm(data=valid_signup_data)
if form.is_valid():
    print("✓ PASS: Signup form validates correctly")
    print(f"  Username: {form.cleaned_data['username']}")
    print(f"  Email: {form.cleaned_data['email']}")
else:
    print("✗ FAIL: Signup form validation failed")
    print(f"  Errors: {form.errors}")

# Test 5: Check form imports don't cause errors
print("\n5. Testing form imports and initialization:")
print("-" * 40)

try:
    from candidates.forms import CandidateRegistrationForm
    form1 = CandidateRegistrationForm()
    print("✓ PASS: CandidateRegistrationForm imports and initializes")
except Exception as e:
    print(f"✗ FAIL: CandidateRegistrationForm error - {e}")

try:
    from candidates.forms import CandidateUpdateForm
    form2 = CandidateUpdateForm()
    print("✓ PASS: CandidateUpdateForm imports and initializes")
except Exception as e:
    print(f"✗ FAIL: CandidateUpdateForm error - {e}")

try:
    from candidates.forms import CandidateEventForm
    form3 = CandidateEventForm()
    print("✓ PASS: CandidateEventForm imports and initializes")
except Exception as e:
    print(f"✗ FAIL: CandidateEventForm error - {e}")

try:
    from authentication.forms import CandidateSignupForm
    form4 = CandidateSignupForm()
    print("✓ PASS: CandidateSignupForm imports and initializes")
except Exception as e:
    print(f"✗ FAIL: CandidateSignupForm error - {e}")

# Test 6: Verify sanitization module
print("\n6. Testing sanitization module:")
print("-" * 40)

try:
    from core.sanitize import (
        sanitize_plain_text,
        sanitize_rich_text,
        sanitize_url,
        sanitize_event_title,
        sanitize_event_description,
        sanitize_event_location
    )
    print("✓ PASS: All sanitization functions importable")

    # Quick sanity check
    test_html = "<script>alert('test')</script>Hello"
    result = sanitize_plain_text(test_html)
    if "<script>" not in result:
        print("✓ PASS: Sanitization removes script tags")
    else:
        print("✗ FAIL: Script tags not removed")

except Exception as e:
    print(f"✗ FAIL: Sanitization module error - {e}")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
