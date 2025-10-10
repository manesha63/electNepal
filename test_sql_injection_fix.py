#!/usr/bin/env python
"""
Test script to verify SQL injection vulnerability fix in locations/views.py
Tests input validation for province_id, district_id, and municipality_id parameters
"""

import os
import sys
import django
import json

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from django.test import RequestFactory, Client
from locations.models import Province, District, Municipality


def test_validation_helper():
    """Test 1: Validation helper function works correctly"""
    print("\n" + "="*60)
    print("TEST 1: Validation Helper Function")
    print("="*60)

    from locations.views import _validate_int_param

    test_cases = [
        # (input, param_name, should_pass, expected_result)
        ("1", "test", True, 1),
        ("42", "test", True, 42),
        ("999", "test", True, 999),
        ("", "test", True, None),
        (None, "test", True, None),
        ("abc", "test", False, None),
        ("1'; DROP TABLE", "test", False, None),
        ("1.5", "test", False, None),
        ("-1", "test", False, None),
        ("0", "test", False, None),
        ("999999999999999999999", "test", True, 999999999999999999999),
    ]

    passed = 0
    failed = 0

    for input_val, param_name, should_pass, expected in test_cases:
        try:
            result = _validate_int_param(input_val, param_name)
            if should_pass:
                if result == expected:
                    print(f"✓ PASS: '{input_val}' -> {result}")
                    passed += 1
                else:
                    print(f"✗ FAIL: '{input_val}' returned {result}, expected {expected}")
                    failed += 1
            else:
                print(f"✗ FAIL: '{input_val}' should have raised ValueError but returned {result}")
                failed += 1
        except ValueError as e:
            if not should_pass:
                print(f"✓ PASS: '{input_val}' correctly raised ValueError: {str(e)[:50]}...")
                passed += 1
            else:
                print(f"✗ FAIL: '{input_val}' raised unexpected ValueError: {e}")
                failed += 1

    test_passed = failed == 0
    if test_passed:
        print(f"\n✓ TEST 1 PASSED: {passed}/{passed+failed} cases handled correctly")
    else:
        print(f"\n✗ TEST 1 FAILED: {failed}/{passed+failed} cases failed")

    return test_passed


def test_districts_api_valid_input():
    """Test 2: Districts API with valid input"""
    print("\n" + "="*60)
    print("TEST 2: Districts API - Valid Input")
    print("="*60)

    client = Client()

    # Get a real province ID
    province = Province.objects.first()
    if not province:
        print("✗ SKIP: No provinces in database")
        return False

    print(f"Testing with Province ID: {province.id} ({province.name_en})")

    # Test with valid province ID
    response = client.get(f'/api/districts/?province={province.id}')

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"✓ PASS: Got {len(data)} districts")
        if len(data) > 0:
            print(f"  Sample: {data[0]['name_en']}")
        return True
    else:
        print(f"✗ FAIL: Expected 200, got {response.status_code}")
        return False


def test_districts_api_invalid_input():
    """Test 3: Districts API with malicious/invalid input"""
    print("\n" + "="*60)
    print("TEST 3: Districts API - Invalid/Malicious Input")
    print("="*60)

    client = Client()

    malicious_inputs = [
        "abc",
        "1'; DROP TABLE districts;--",
        "null",
        "<script>alert('xss')</script>",
        "../../etc/passwd",
        "-1",
        "0",
        "1.5",
        "999999999",  # Non-existent ID (should return empty, not error)
    ]

    passed = 0
    failed = 0

    for malicious_input in malicious_inputs:
        response = client.get(f'/api/districts/?province={malicious_input}')

        if response.status_code == 400:
            data = json.loads(response.content)
            if 'error' in data:
                print(f"✓ PASS: '{malicious_input}' -> 400 Bad Request: {data['error'][:50]}...")
                passed += 1
            else:
                print(f"✗ FAIL: '{malicious_input}' -> 400 but no error message")
                failed += 1
        elif response.status_code == 200:
            # Non-existent ID should return empty array, not error
            data = json.loads(response.content)
            if isinstance(data, list) and len(data) == 0:
                print(f"✓ PASS: '{malicious_input}' -> Empty result (no crash)")
                passed += 1
            else:
                print(f"✗ FAIL: '{malicious_input}' -> Unexpected 200 with data")
                failed += 1
        elif response.status_code == 500:
            print(f"✗ FAIL: '{malicious_input}' -> 500 Server Error (validation failed)")
            failed += 1
        else:
            print(f"✗ FAIL: '{malicious_input}' -> Unexpected status {response.status_code}")
            failed += 1

    test_passed = failed == 0
    if test_passed:
        print(f"\n✓ TEST 3 PASSED: All malicious inputs handled safely")
    else:
        print(f"\n✗ TEST 3 FAILED: {failed} inputs caused errors")

    return test_passed


def test_municipalities_api_valid_input():
    """Test 4: Municipalities API with valid input"""
    print("\n" + "="*60)
    print("TEST 4: Municipalities API - Valid Input")
    print("="*60)

    client = Client()

    # Get a real district ID
    district = District.objects.first()
    if not district:
        print("✗ SKIP: No districts in database")
        return False

    print(f"Testing with District ID: {district.id} ({district.name_en})")

    # Test with valid district ID
    response = client.get(f'/api/municipalities/?district={district.id}')

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"✓ PASS: Got {len(data)} municipalities")
        if len(data) > 0:
            print(f"  Sample: {data[0]['name_en']}")
        return True
    else:
        print(f"✗ FAIL: Expected 200, got {response.status_code}")
        return False


def test_municipalities_api_invalid_input():
    """Test 5: Municipalities API with malicious/invalid input"""
    print("\n" + "="*60)
    print("TEST 5: Municipalities API - Invalid/Malicious Input")
    print("="*60)

    client = Client()

    malicious_inputs = [
        "abc",
        "1 OR 1=1",
        "'; DELETE FROM municipalities WHERE '1'='1",
        "-999",
        "0",
        "1.1",
    ]

    passed = 0
    failed = 0

    for malicious_input in malicious_inputs:
        response = client.get(f'/api/municipalities/?district={malicious_input}')

        if response.status_code == 400:
            data = json.loads(response.content)
            if 'error' in data:
                print(f"✓ PASS: '{malicious_input}' -> 400 Bad Request")
                passed += 1
            else:
                print(f"✗ FAIL: '{malicious_input}' -> 400 but no error message")
                failed += 1
        elif response.status_code == 200:
            # Non-existent ID should return empty array
            data = json.loads(response.content)
            if isinstance(data, list) and len(data) == 0:
                print(f"✓ PASS: '{malicious_input}' -> Empty result (no crash)")
                passed += 1
            else:
                print(f"✗ FAIL: '{malicious_input}' -> Unexpected 200 with data")
                failed += 1
        elif response.status_code == 500:
            print(f"✗ FAIL: '{malicious_input}' -> 500 Server Error")
            failed += 1
        else:
            print(f"✗ FAIL: '{malicious_input}' -> Unexpected status {response.status_code}")
            failed += 1

    test_passed = failed == 0
    if test_passed:
        print(f"\n✓ TEST 5 PASSED: All malicious inputs handled safely")
    else:
        print(f"\n✗ TEST 5 FAILED: {failed} inputs caused errors")

    return test_passed


def test_municipality_by_id_invalid_input():
    """Test 6: Municipality by ID with malicious/invalid input"""
    print("\n" + "="*60)
    print("TEST 6: Municipality by ID - Invalid/Malicious Input")
    print("="*60)

    client = Client()

    malicious_inputs = [
        "xxx",
        "1 UNION SELECT",
        "../../",
        "-1",
    ]

    passed = 0
    failed = 0

    for malicious_input in malicious_inputs:
        response = client.get(f'/api/municipalities/?id={malicious_input}')

        if response.status_code == 400:
            data = json.loads(response.content)
            if 'error' in data:
                print(f"✓ PASS: '{malicious_input}' -> 400 Bad Request")
                passed += 1
            else:
                print(f"✗ FAIL: '{malicious_input}' -> 400 but no error message")
                failed += 1
        elif response.status_code == 200:
            # Non-existent ID should return empty array
            data = json.loads(response.content)
            if isinstance(data, list) and len(data) == 0:
                print(f"✓ PASS: '{malicious_input}' -> Empty result (no crash)")
                passed += 1
            else:
                print(f"✗ FAIL: '{malicious_input}' -> Unexpected 200 with data")
                failed += 1
        elif response.status_code == 500:
            print(f"✗ FAIL: '{malicious_input}' -> 500 Server Error")
            failed += 1
        else:
            print(f"✗ FAIL: '{malicious_input}' -> Unexpected status {response.status_code}")
            failed += 1

    test_passed = failed == 0
    if test_passed:
        print(f"\n✓ TEST 6 PASSED: All malicious inputs handled safely")
    else:
        print(f"\n✗ TEST 6 FAILED: {failed} inputs caused errors")

    return test_passed


def test_existing_functionality():
    """Test 7: Verify existing functionality still works"""
    print("\n" + "="*60)
    print("TEST 7: Existing Functionality Verification")
    print("="*60)

    client = Client()
    tests_passed = []

    # Test 1: Get districts for Province 1 (Koshi)
    response = client.get('/api/districts/?province=1')
    if response.status_code == 200:
        data = json.loads(response.content)
        if len(data) > 0:
            print(f"✓ PASS: Province 1 has {len(data)} districts")
            tests_passed.append(True)
        else:
            print(f"✗ FAIL: Province 1 returned no districts")
            tests_passed.append(False)
    else:
        print(f"✗ FAIL: Province 1 query failed with status {response.status_code}")
        tests_passed.append(False)

    # Test 2: Get municipalities for a district
    district = District.objects.first()
    if district:
        response = client.get(f'/api/municipalities/?district={district.id}')
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"✓ PASS: District {district.name_en} returned {len(data)} municipalities")
            tests_passed.append(True)
        else:
            print(f"✗ FAIL: Municipality query failed")
            tests_passed.append(False)

    # Test 3: Get specific municipality by ID
    municipality = Municipality.objects.first()
    if municipality:
        response = client.get(f'/api/municipalities/?id={municipality.id}')
        if response.status_code == 200:
            data = json.loads(response.content)
            if len(data) == 1 and data[0]['id'] == municipality.id:
                print(f"✓ PASS: Municipality by ID returned correct result")
                tests_passed.append(True)
            else:
                print(f"✗ FAIL: Municipality by ID returned incorrect data")
                tests_passed.append(False)
        else:
            print(f"✗ FAIL: Municipality by ID query failed")
            tests_passed.append(False)

    all_passed = all(tests_passed)
    if all_passed:
        print(f"\n✓ TEST 7 PASSED: All existing functionality works")
    else:
        print(f"\n✗ TEST 7 FAILED: Some existing functionality broken")

    return all_passed


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print(" SQL INJECTION FIX VERIFICATION TEST SUITE")
    print("="*80)
    print("\nThis test suite verifies:")
    print("1. Input validation helper function works correctly")
    print("2. Valid inputs still work (no breaking changes)")
    print("3. Invalid/malicious inputs are safely rejected")
    print("4. All existing functionality preserved")
    print("\nRunning tests...\n")

    results = {}

    try:
        results['test1'] = test_validation_helper()
        results['test2'] = test_districts_api_valid_input()
        results['test3'] = test_districts_api_invalid_input()
        results['test4'] = test_municipalities_api_valid_input()
        results['test5'] = test_municipalities_api_invalid_input()
        results['test6'] = test_municipality_by_id_invalid_input()
        results['test7'] = test_existing_functionality()

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
        'test1': 'Validation Helper Function',
        'test2': 'Districts API - Valid Input',
        'test3': 'Districts API - Invalid Input',
        'test4': 'Municipalities API - Valid Input',
        'test5': 'Municipalities API - Invalid Input',
        'test6': 'Municipality by ID - Invalid Input',
        'test7': 'Existing Functionality',
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
        print("\nThe SQL injection fix is working correctly:")
        print("  ✓ Input validation prevents malicious input")
        print("  ✓ Returns clean 400 errors for invalid input")
        print("  ✓ No server crashes or 500 errors")
        print("  ✓ All existing functionality preserved")
        print("  ✓ No breaking changes")
        print("\nThe application is now secure against SQL injection attacks.")
        return True
    else:
        print("\n✗✗✗ SOME TESTS FAILED ✗✗✗")
        print("\nPlease review the failed tests above.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
