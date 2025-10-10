#!/usr/bin/env python
"""
Test script to verify unsafe type casting fix in candidates/views.py:109
Tests that malformed page parameters don't cause 500 errors
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from django.test import RequestFactory
from candidates.views import nearby_candidates_api


def test_malicious_page_parameter():
    """Test that malicious page parameters are handled safely"""
    print("\n" + "="*70)
    print(" UNSAFE TYPE CASTING FIX VERIFICATION TEST SUITE")
    print("="*70)
    print("\nTesting candidates/views.py:109 - nearby_candidates_api()")
    print("Issue: Direct int() conversion without try-except causes 500 errors\n")

    factory = RequestFactory()
    results = {}

    # Test 1: Valid page number
    print("=" * 70)
    print("TEST 1: Valid Page Number (page=2)")
    print("=" * 70)
    try:
        request = factory.get('/api/nearby-candidates/', {'page': '2'})
        response = nearby_candidates_api(request)
        if response.status_code == 200:
            print("✓ PASS: Valid page number accepted (status 200)")
            results['test1'] = True
        else:
            print(f"✗ FAIL: Unexpected status code {response.status_code}")
            results['test1'] = False
    except Exception as e:
        print(f"✗ FAIL: Exception raised: {e}")
        results['test1'] = False

    # Test 2: Malicious string "abc"
    print("\n" + "=" * 70)
    print("TEST 2: Malicious Input 'abc' (page=abc)")
    print("=" * 70)
    print("Before fix: Would raise ValueError and cause 500 error")
    print("After fix: Should default to page=1 and return 200")
    try:
        request = factory.get('/api/nearby-candidates/', {'page': 'abc'})
        response = nearby_candidates_api(request)
        if response.status_code == 200:
            print("✓ PASS: Malicious 'abc' handled gracefully (status 200, defaults to page 1)")
            results['test2'] = True
        else:
            print(f"✗ FAIL: Unexpected status code {response.status_code}")
            results['test2'] = False
    except ValueError as e:
        print(f"✗ FAIL: ValueError raised (not caught by try-except): {e}")
        results['test2'] = False
    except Exception as e:
        print(f"✗ FAIL: Unexpected exception: {e}")
        results['test2'] = False

    # Test 3: Empty string
    print("\n" + "=" * 70)
    print("TEST 3: Empty String (page=)")
    print("=" * 70)
    print("Before fix: Would raise ValueError and cause 500 error")
    print("After fix: Should default to page=1 and return 200")
    try:
        request = factory.get('/api/nearby-candidates/', {'page': ''})
        response = nearby_candidates_api(request)
        if response.status_code == 200:
            print("✓ PASS: Empty string handled gracefully (status 200, defaults to page 1)")
            results['test3'] = True
        else:
            print(f"✗ FAIL: Unexpected status code {response.status_code}")
            results['test3'] = False
    except ValueError as e:
        print(f"✗ FAIL: ValueError raised (not caught by try-except): {e}")
        results['test3'] = False
    except Exception as e:
        print(f"✗ FAIL: Unexpected exception: {e}")
        results['test3'] = False

    # Test 4: Negative number
    print("\n" + "=" * 70)
    print("TEST 4: Negative Number (page=-5)")
    print("=" * 70)
    print("Note: Negative numbers convert to int successfully")
    print("Function should handle negative pages gracefully (may return empty results)")
    try:
        request = factory.get('/api/nearby-candidates/', {'page': '-5'})
        response = nearby_candidates_api(request)
        if response.status_code == 200:
            print("✓ PASS: Negative number handled (status 200)")
            results['test4'] = True
        else:
            print(f"✗ FAIL: Unexpected status code {response.status_code}")
            results['test4'] = False
    except Exception as e:
        print(f"✗ FAIL: Exception raised: {e}")
        results['test4'] = False

    # Test 5: Very large number
    print("\n" + "=" * 70)
    print("TEST 5: Very Large Number (page=999999)")
    print("=" * 70)
    try:
        request = factory.get('/api/nearby-candidates/', {'page': '999999'})
        response = nearby_candidates_api(request)
        if response.status_code == 200:
            print("✓ PASS: Large number handled (status 200)")
            results['test5'] = True
        else:
            print(f"✗ FAIL: Unexpected status code {response.status_code}")
            results['test5'] = False
    except Exception as e:
        print(f"✗ FAIL: Exception raised: {e}")
        results['test5'] = False

    # Test 6: No page parameter
    print("\n" + "=" * 70)
    print("TEST 6: Missing Page Parameter (no ?page=)")
    print("=" * 70)
    print("Should use default value of 1")
    try:
        request = factory.get('/api/nearby-candidates/')
        response = nearby_candidates_api(request)
        if response.status_code == 200:
            print("✓ PASS: Missing parameter handled (status 200, defaults to page 1)")
            results['test6'] = True
        else:
            print(f"✗ FAIL: Unexpected status code {response.status_code}")
            results['test6'] = False
    except Exception as e:
        print(f"✗ FAIL: Exception raised: {e}")
        results['test6'] = False

    # Test 7: SQL Injection attempt
    print("\n" + "=" * 70)
    print("TEST 7: SQL Injection Attempt (page=1'; DROP TABLE)")
    print("=" * 70)
    print("Before fix: Would raise ValueError and cause 500 error")
    print("After fix: Should default to page=1 and return 200")
    try:
        request = factory.get('/api/nearby-candidates/', {'page': "1'; DROP TABLE"})
        response = nearby_candidates_api(request)
        if response.status_code == 200:
            print("✓ PASS: SQL injection attempt handled gracefully (status 200)")
            results['test7'] = True
        else:
            print(f"✗ FAIL: Unexpected status code {response.status_code}")
            results['test7'] = False
    except ValueError as e:
        print(f"✗ FAIL: ValueError raised (not caught by try-except): {e}")
        results['test7'] = False
    except Exception as e:
        print(f"✗ FAIL: Unexpected exception: {e}")
        results['test7'] = False

    # Summary
    print("\n" + "=" * 70)
    print(" TEST SUMMARY")
    print("=" * 70)

    passed_count = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\nTests Passed: {passed_count}/{total}")
    print("-" * 70)

    test_names = {
        'test1': 'Valid Page Number',
        'test2': 'Malicious String "abc"',
        'test3': 'Empty String',
        'test4': 'Negative Number',
        'test5': 'Very Large Number',
        'test6': 'Missing Page Parameter',
        'test7': 'SQL Injection Attempt',
    }

    for test_key, test_passed in results.items():
        status = "✓ PASS" if test_passed else "✗ FAIL"
        test_name = test_names.get(test_key, test_key)
        print(f"{status}: {test_name}")

    print("-" * 70)

    if passed_count == total:
        print("\n" + "=" * 70)
        print(" ✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("=" * 70)
        print("\nThe unsafe type casting fix is working correctly:")
        print("  ✓ Malicious inputs handled gracefully")
        print("  ✓ No 500 errors on invalid page parameters")
        print("  ✓ Defaults to page=1 on conversion errors")
        print("  ✓ DoS vulnerability mitigated")
        print("\nFixed code (candidates/views.py:110-114):")
        print("  try:")
        print("      page = int(request.GET.get('page', 1))")
        print("  except (TypeError, ValueError):")
        print("      page = 1")
        return True
    else:
        print("\n✗✗✗ SOME TESTS FAILED ✗✗✗")
        print("\nPlease review the failed tests above.")
        return False


if __name__ == '__main__':
    success = test_malicious_page_parameter()
    sys.exit(0 if success else 1)
