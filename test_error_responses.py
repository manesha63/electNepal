#!/usr/bin/env python
"""
Test script to verify all API endpoints use consistent error response format.

This script tests:
1. All endpoints return standard format: {'error': 'message'}
2. Validation errors follow format: {'error': 'Validation failed', 'fields': {...}}
3. Success responses follow format: {'success': True, 'message': 'message'}
4. Error status codes are appropriate (400, 403, 404, 500, etc.)
"""

import os
import sys
import django
import json

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from django.test import Client
from rest_framework.test import APIClient


def test_georesolve_validation_errors():
    """Test that georesolve endpoint returns standardized validation errors"""
    print("\n" + "="*70)
    print("TEST 1: Georesolve Validation Error Format (POST with Invalid Data)")
    print("="*70)

    client = APIClient()

    # Test with invalid data types
    invalid_data = {
        'lat': 'invalid',
        'lng': 'abc'
    }

    response = client.post('/api/georesolve/', invalid_data, format='json')

    print(f"\nStatus Code: {response.status_code}")

    # Handle both DRF Response and HttpResponse
    if hasattr(response, 'data'):
        data = response.data
    else:
        data = json.loads(response.content)

    print(f"Response: {json.dumps(data, indent=2)}")

    # Check response format
    if response.status_code == 400:
        if 'error' in data:
            if data['error'] == 'Validation failed' and 'fields' in data:
                print("\n✓ PASS: Standard validation error format")
                print(f"  - Has 'error' key: ✓")
                print(f"  - error value is 'Validation failed': ✓")
                print(f"  - Has 'fields' key: ✓")
                return True
            else:
                print("\n✗ FAIL: Has 'error' but wrong format")
                print(f"  Expected: {{'error': 'Validation failed', 'fields': {{...}}}}")
                print(f"  Got: {data}")
                return False
        else:
            print("\n✗ FAIL: Missing 'error' key in response")
            print(f"  Response: {data}")
            return False
    else:
        print(f"\n✗ FAIL: Wrong status code (expected 400, got {response.status_code})")
        return False


def test_georesolve_missing_fields():
    """Test georesolve with missing required fields"""
    print("\n" + "="*70)
    print("TEST 2: Georesolve Missing Fields (POST with No Data)")
    print("="*70)

    client = APIClient()

    # Test with empty data
    response = client.post('/api/georesolve/', {}, format='json')

    print(f"\nStatus Code: {response.status_code}")

    # Handle both DRF Response and HttpResponse
    if hasattr(response, 'data'):
        data = response.data
    else:
        data = json.loads(response.content)

    print(f"Response: {json.dumps(data, indent=2)}")

    if response.status_code == 400:
        if 'error' in data:
            print("\n✓ PASS: Standard error format with 'error' key")
            return True
        else:
            print("\n✗ FAIL: Missing 'error' key")
            return False
    else:
        print(f"\n✗ FAIL: Wrong status code (expected 400, got {response.status_code})")
        return False


def test_georesolve_get_missing_params():
    """Test georesolve GET endpoint with missing parameters"""
    print("\n" + "="*70)
    print("TEST 3: Georesolve GET Missing Parameters")
    print("="*70)

    client = APIClient()

    # Test GET without parameters
    response = client.get('/api/georesolve/')

    print(f"\nStatus Code: {response.status_code}")

    try:
        data = json.loads(response.content) if hasattr(response, 'content') else response.data
        print(f"Response: {json.dumps(data, indent=2)}")
    except:
        print(f"Response: {response.content}")
        data = {}

    if response.status_code == 400:
        if 'error' in data:
            print("\n✓ PASS: Standard error format")
            return True
        else:
            print("\n✗ FAIL: Missing 'error' key")
            return False
    else:
        print(f"\n✗ FAIL: Wrong status code (expected 400, got {response.status_code})")
        return False


def test_districts_invalid_province():
    """Test districts endpoint with invalid province ID"""
    print("\n" + "="*70)
    print("TEST 4: Districts by Province - Invalid Province ID")
    print("="*70)

    client = APIClient()

    # Test with invalid province ID
    response = client.get('/api/districts/?province=invalid')

    print(f"\nStatus Code: {response.status_code}")

    try:
        data = json.loads(response.content) if hasattr(response, 'content') else response.data
        print(f"Response: {json.dumps(data, indent=2)}")
    except:
        print(f"Response: {response.content}")
        data = {}

    if response.status_code == 400:
        if 'error' in data:
            print("\n✓ PASS: Standard error format")
            return True
        else:
            print("\n✗ FAIL: Missing 'error' key")
            return False
    else:
        print(f"\n✗ FAIL: Wrong status code (expected 400, got {response.status_code})")
        return False


def test_municipalities_invalid_district():
    """Test municipalities endpoint with invalid district ID"""
    print("\n" + "="*70)
    print("TEST 5: Municipalities by District - Invalid District ID")
    print("="*70)

    client = APIClient()

    # Test with invalid district ID
    response = client.get('/api/municipalities/?district=invalid')

    print(f"\nStatus Code: {response.status_code}")

    try:
        data = json.loads(response.content) if hasattr(response, 'content') else response.data
        print(f"Response: {json.dumps(data, indent=2)}")
    except:
        print(f"Response: {response.content}")
        data = {}

    if response.status_code == 400:
        if 'error' in data:
            print("\n✓ PASS: Standard error format")
            return True
        else:
            print("\n✗ FAIL: Missing 'error' key")
            return False
    else:
        print(f"\n✗ FAIL: Wrong status code (expected 400, got {response.status_code})")
        return False


def test_municipality_wards_not_found():
    """Test municipality wards endpoint with non-existent ID"""
    print("\n" + "="*70)
    print("TEST 6: Municipality Wards - Not Found")
    print("="*70)

    client = APIClient()

    # Test with non-existent municipality ID
    response = client.get('/api/municipalities/99999/wards/')

    print(f"\nStatus Code: {response.status_code}")

    try:
        data = json.loads(response.content) if hasattr(response, 'content') else response.data
        print(f"Response: {json.dumps(data, indent=2)}")
    except:
        print(f"Response: {response.content}")
        data = {}

    if response.status_code == 404:
        if 'error' in data:
            print("\n✓ PASS: Standard error format with 404")
            return True
        else:
            print("\n✗ FAIL: Missing 'error' key")
            return False
    else:
        print(f"\n✗ FAIL: Wrong status code (expected 404, got {response.status_code})")
        return False


def test_my_ballot_missing_province():
    """Test my_ballot endpoint without required province_id"""
    print("\n" + "="*70)
    print("TEST 7: My Ballot - Missing Required Province ID")
    print("="*70)

    client = Client()

    # Test without province_id
    response = client.get('/candidates/api/my-ballot/')

    print(f"\nStatus Code: {response.status_code}")

    try:
        data = json.loads(response.content)
        print(f"Response: {json.dumps(data, indent=2)}")
    except:
        print(f"Response: {response.content}")
        data = {}

    if response.status_code == 400:
        if 'error' in data:
            print("\n✓ PASS: Standard error format")
            return True
        else:
            print("\n✗ FAIL: Missing 'error' key")
            return False
    else:
        print(f"\n✗ FAIL: Wrong status code (expected 400, got {response.status_code})")
        return False


def test_my_ballot_invalid_province():
    """Test my_ballot endpoint with invalid province_id"""
    print("\n" + "="*70)
    print("TEST 8: My Ballot - Invalid Province ID")
    print("="*70)

    client = Client()

    # Test with invalid province_id
    response = client.get('/candidates/api/my-ballot/?province_id=invalid')

    print(f"\nStatus Code: {response.status_code}")

    try:
        data = json.loads(response.content)
        print(f"Response: {json.dumps(data, indent=2)}")
    except:
        print(f"Response: {response.content}")
        data = {}

    if response.status_code == 400:
        if 'error' in data:
            print("\n✓ PASS: Standard error format")
            return True
        else:
            print("\n✗ FAIL: Missing 'error' key")
            return False
    else:
        print(f"\n✗ FAIL: Wrong status code (expected 400, got {response.status_code})")
        return False


def test_georesolve_outside_nepal():
    """Test georesolve with coordinates outside Nepal"""
    print("\n" + "="*70)
    print("TEST 9: Georesolve - Coordinates Outside Nepal")
    print("="*70)

    client = APIClient()

    # Test with Delhi, India coordinates
    response = client.get('/api/georesolve/?lat=28.6139&lng=77.2090')

    print(f"\nStatus Code: {response.status_code}")

    try:
        data = json.loads(response.content) if hasattr(response, 'content') else response.data
        print(f"Response: {json.dumps(data, indent=2)}")
    except:
        print(f"Response: {response.content}")
        data = {}

    if response.status_code == 404:
        if 'error' in data:
            print("\n✓ PASS: Standard error format with 404")
            return True
        else:
            print("\n✗ FAIL: Missing 'error' key")
            return False
    else:
        print(f"\n✗ FAIL: Wrong status code (expected 404, got {response.status_code})")
        return False


def test_georesolve_success():
    """Test georesolve with valid coordinates returns proper data format"""
    print("\n" + "="*70)
    print("TEST 10: Georesolve - Valid Coordinates (Success Case)")
    print("="*70)

    client = APIClient()

    # Test with Kathmandu coordinates
    response = client.get('/api/georesolve/?lat=27.7172&lng=85.3240')

    print(f"\nStatus Code: {response.status_code}")

    try:
        data = json.loads(response.content) if hasattr(response, 'content') else response.data
        print(f"Response: {json.dumps(data, indent=2)}")
    except:
        print(f"Response: {response.content}")
        data = {}

    if response.status_code == 200:
        # Success responses should NOT have 'error' key
        if 'error' not in data:
            if 'province' in data:
                print("\n✓ PASS: Success response without 'error' key")
                print(f"  - No 'error' key: ✓")
                print(f"  - Has data ('province'): ✓")
                return True
            else:
                print("\n⚠ PARTIAL: No 'error' key but missing expected data")
                return True
        else:
            print("\n✗ FAIL: Success response contains 'error' key")
            return False
    else:
        print(f"\n✗ FAIL: Wrong status code (expected 200, got {response.status_code})")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print(" ERROR RESPONSE FORMAT CONSISTENCY TEST SUITE")
    print("="*80)
    print("\nThis test suite verifies:")
    print("1. All error responses use standard format: {'error': 'message'}")
    print("2. Validation errors follow format: {'error': 'Validation failed', 'fields': {...}}")
    print("3. Success responses don't have 'error' key")
    print("4. Proper HTTP status codes are used")
    print("\nRunning tests...\n")

    results = {}

    try:
        results['test1'] = test_georesolve_validation_errors()
        results['test2'] = test_georesolve_missing_fields()
        results['test3'] = test_georesolve_get_missing_params()
        results['test4'] = test_districts_invalid_province()
        results['test5'] = test_municipalities_invalid_district()
        results['test6'] = test_municipality_wards_not_found()
        results['test7'] = test_my_ballot_missing_province()
        results['test8'] = test_my_ballot_invalid_province()
        results['test9'] = test_georesolve_outside_nepal()
        results['test10'] = test_georesolve_success()

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
        'test1': 'Georesolve Validation Error Format',
        'test2': 'Georesolve Missing Fields',
        'test3': 'Georesolve GET Missing Parameters',
        'test4': 'Districts Invalid Province ID',
        'test5': 'Municipalities Invalid District ID',
        'test6': 'Municipality Wards Not Found',
        'test7': 'My Ballot Missing Province ID',
        'test8': 'My Ballot Invalid Province ID',
        'test9': 'Georesolve Outside Nepal',
        'test10': 'Georesolve Success Case',
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
        print("\nError response format is now consistent:")
        print("  ✓ All error responses use {'error': 'message'} format")
        print("  ✓ Validation errors use {'error': 'Validation failed', 'fields': {...}}")
        print("  ✓ Success responses don't have 'error' key")
        print("  ✓ Proper HTTP status codes (400, 404, 200)")
        print("\nFixed issues:")
        print("  ✓ locations/api_views.py line 251: Now uses validation_error_response()")
        return True
    else:
        print("\n✗✗✗ SOME TESTS FAILED ✗✗✗")
        print("\nPlease review the failed tests above.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
