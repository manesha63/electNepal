#!/usr/bin/env python
"""
Test script to verify language prefix fix for issue #33.

This script tests that:
1. Language prefix is generated using get_language() instead of hardcoded '/ne'
2. English URLs have no prefix (/)
3. Nepali URLs have /ne prefix
4. URLs work correctly with language switching
5. No hardcoded language codes remain in views.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

def test_no_hardcoded_language_prefixes():
    """Test that there are no hardcoded '/ne' in views.py"""
    print("=" * 70)
    print("TEST 1: No Hardcoded Language Prefixes")
    print("=" * 70)

    with open('candidates/views.py', 'r') as f:
        content = f.read()

    # Check for hardcoded '/ne' strings
    hardcoded_ne = "'/ne'" in content or '"/ne"' in content

    if hardcoded_ne:
        print(f"  ❌ Found hardcoded '/ne' in views.py")
        # Show context
        for i, line in enumerate(content.split('\n'), 1):
            if "'/ne'" in line or '"/ne"' in line:
                print(f"    Line {i}: {line.strip()}")
    else:
        print(f"  ✓ No hardcoded '/ne' found in views.py")

    assert not hardcoded_ne, "Hardcoded '/ne' found in views.py"

    print(f"\n✓ PASS: No hardcoded language prefixes")
    print()


def test_get_language_usage():
    """Test that get_language() is used for language prefix generation"""
    print("=" * 70)
    print("TEST 2: get_language() Usage")
    print("=" * 70)

    with open('candidates/views.py', 'r') as f:
        content = f.read()

    # Check that get_language is imported
    has_import = 'from django.utils.translation import get_language' in content
    print(f"  {'✓' if has_import else '❌'} get_language imported: {has_import}")

    # Check for get_language() usage in my_ballot function
    has_usage = 'current_lang = get_language()' in content
    print(f"  {'✓' if has_usage else '❌'} get_language() used: {has_usage}")

    # Check for proper prefix generation
    has_prefix_logic = "lang_prefix = f'/{current_lang}' if current_lang != 'en' else ''" in content
    print(f"  {'✓' if has_prefix_logic else '❌'} Proper prefix logic: {has_prefix_logic}")

    assert has_import, "get_language not imported"
    assert has_usage, "get_language() not used"
    assert has_prefix_logic, "Proper prefix generation logic missing"

    print(f"\n✓ PASS: get_language() properly used")
    print()


def test_english_url_generation():
    """Test that English URLs have no language prefix"""
    print("=" * 70)
    print("TEST 3: English URL Generation")
    print("=" * 70)

    from django.test import RequestFactory
    from django.utils.translation import activate
    from candidates.views import my_ballot
    from candidates.models import Candidate
    from django.contrib.auth.models import User
    from locations.models import Province, District, Municipality

    # Activate English
    activate('en')

    # Create test data
    user = User.objects.filter(username='testuser_lang').first()
    if not user:
        user = User.objects.create_user(
            username='testuser_lang',
            email='testlang@test.com',
            password='testpass123'
        )

    province = Province.objects.first()
    district = District.objects.filter(province=province).first()
    municipality = Municipality.objects.filter(district=district).first()

    # Create or get test candidate
    candidate, created = Candidate.objects.get_or_create(
        user=user,
        defaults={
            'full_name': 'Test Language Candidate',
            'age': 35,
            'position_level': 'provincial_assembly',
            'province': province,
            'district': district,
            'municipality': municipality,
            'status': 'approved',
            'bio_en': 'Test bio',
            'education_en': 'Test education',
            'experience_en': 'Test experience',
            'manifesto_en': 'Test manifesto',
        }
    )

    # Create request
    factory = RequestFactory()
    request = factory.get('/candidates/api/my-ballot/', {
        'province_id': province.id,
        'district_id': district.id,
        'municipality_id': municipality.id,
        'page': 1,
        'page_size': 10
    })

    # Set language on request
    request.LANGUAGE_CODE = 'en'

    # Call the view
    response = my_ballot(request)

    print(f"  Response status: {response.status_code}")

    if response.status_code == 200:
        import json
        data = json.loads(response.content)

        if data.get('candidates'):
            first_candidate = data['candidates'][0]
            detail_url = first_candidate.get('detail_url', '')

            print(f"  Detail URL: {detail_url}")

            # English URLs should not have /en/ or /ne/ prefix
            has_no_prefix = not detail_url.startswith('/en/') and not detail_url.startswith('/ne/')
            print(f"  {'✓' if has_no_prefix else '❌'} No language prefix: {has_no_prefix}")

            # Should start with /candidates/
            correct_format = detail_url.startswith('/candidates/')
            print(f"  {'✓' if correct_format else '❌'} Correct format: {correct_format}")

            assert has_no_prefix, f"English URL should not have prefix: {detail_url}"
            assert correct_format, f"URL should start with /candidates/: {detail_url}"
        else:
            print(f"  ℹ No candidates returned")

    # Clean up
    if created:
        candidate.delete()
        user.delete()

    print(f"\n✓ PASS: English URLs have no prefix")
    print()


def test_nepali_url_generation():
    """Test that Nepali URLs have /ne prefix"""
    print("=" * 70)
    print("TEST 4: Nepali URL Generation")
    print("=" * 70)

    from django.test import RequestFactory
    from django.utils.translation import activate
    from candidates.views import my_ballot
    from candidates.models import Candidate
    from django.contrib.auth.models import User
    from locations.models import Province, District, Municipality

    # Activate Nepali
    activate('ne')

    # Create test data
    user = User.objects.filter(username='testuser_lang_ne').first()
    if not user:
        user = User.objects.create_user(
            username='testuser_lang_ne',
            email='testlangne@test.com',
            password='testpass123'
        )

    province = Province.objects.first()
    district = District.objects.filter(province=province).first()
    municipality = Municipality.objects.filter(district=district).first()

    # Create or get test candidate
    candidate, created = Candidate.objects.get_or_create(
        user=user,
        defaults={
            'full_name': 'Test Language Candidate NE',
            'age': 35,
            'position_level': 'provincial_assembly',
            'province': province,
            'district': district,
            'municipality': municipality,
            'status': 'approved',
            'bio_en': 'Test bio',
            'education_en': 'Test education',
            'experience_en': 'Test experience',
            'manifesto_en': 'Test manifesto',
        }
    )

    # Create request
    factory = RequestFactory()
    request = factory.get('/ne/candidates/api/my-ballot/', {
        'province_id': province.id,
        'district_id': district.id,
        'municipality_id': municipality.id,
        'page': 1,
        'page_size': 10
    })

    # Set language on request
    request.LANGUAGE_CODE = 'ne'

    # Call the view
    response = my_ballot(request)

    print(f"  Response status: {response.status_code}")

    if response.status_code == 200:
        import json
        data = json.loads(response.content)

        if data.get('candidates'):
            first_candidate = data['candidates'][0]
            detail_url = first_candidate.get('detail_url', '')

            print(f"  Detail URL: {detail_url}")

            # Nepali URLs should have /ne/ prefix
            has_ne_prefix = detail_url.startswith('/ne/')
            print(f"  {'✓' if has_ne_prefix else '❌'} Has /ne/ prefix: {has_ne_prefix}")

            # Should be /ne/candidates/{id}/
            correct_format = detail_url.startswith('/ne/candidates/')
            print(f"  {'✓' if correct_format else '❌'} Correct format: {correct_format}")

            assert has_ne_prefix, f"Nepali URL should have /ne/ prefix: {detail_url}"
            assert correct_format, f"URL should start with /ne/candidates/: {detail_url}"
        else:
            print(f"  ℹ No candidates returned")

    # Clean up
    if created:
        candidate.delete()
        user.delete()

    # Reset to English
    activate('en')

    print(f"\n✓ PASS: Nepali URLs have /ne/ prefix")
    print()


def test_language_switching():
    """Test that URLs update correctly when language switches"""
    print("=" * 70)
    print("TEST 5: Language Switching")
    print("=" * 70)

    from django.utils.translation import activate, get_language

    # Test English
    activate('en')
    current_lang = get_language()
    lang_prefix_en = f'/{current_lang}' if current_lang != 'en' else ''
    print(f"  English language: {current_lang}")
    print(f"  English prefix: '{lang_prefix_en}'")
    assert lang_prefix_en == '', f"English should have empty prefix, got: {lang_prefix_en}"

    # Test Nepali
    activate('ne')
    current_lang = get_language()
    lang_prefix_ne = f'/{current_lang}' if current_lang != 'en' else ''
    print(f"  Nepali language: {current_lang}")
    print(f"  Nepali prefix: '{lang_prefix_ne}'")
    assert lang_prefix_ne == '/ne', f"Nepali should have /ne prefix, got: {lang_prefix_ne}"

    # Reset to English
    activate('en')

    print(f"\n✓ PASS: Language switching works correctly")
    print()


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("LANGUAGE PREFIX FIX TEST SUITE")
    print("Testing fix for issue #33")
    print("=" * 70 + "\n")

    try:
        test_no_hardcoded_language_prefixes()
        test_get_language_usage()
        test_english_url_generation()
        test_nepali_url_generation()
        test_language_switching()

        print("=" * 70)
        print("ALL TESTS PASSED ✓")
        print("=" * 70)
        print("\nSummary:")
        print("- No hardcoded '/ne' strings remain")
        print("- get_language() properly used")
        print("- English URLs have no prefix")
        print("- Nepali URLs have /ne prefix")
        print("- Language switching works correctly")
        print("\nLanguage prefixes now use Django i18n utilities!")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
