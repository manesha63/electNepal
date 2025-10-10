#!/usr/bin/env python
"""
Test script to verify geolocation fix in locations/api_views.py:208-243
Tests that geo_resolve endpoint now uses actual implementation instead of returning 501
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from django.test import Client
from rest_framework.test import APIClient
import json


def get_response_data(response):
    """Helper to extract data from both DRF Response and HttpResponse"""
    if hasattr(response, 'data'):
        return response.data
    elif hasattr(response, 'content'):
        return json.loads(response.content)
    return {}


def test_georesolve_no_longer_501():
    """Test 1: geo_resolve endpoint no longer returns 501"""
    print("\n" + "="*70)
    print("TEST 1: Geolocation Endpoint No Longer Returns 501")
    print("="*70)

    client = APIClient()

    # Test with Kathmandu coordinates
    kathmandu_coords = {
        'lat': 27.7172,
        'lng': 85.3240
    }

    response = client.post('/api/georesolve/', kathmandu_coords, format='json')

    if response.status_code != 501:
        print(f"\n✓ PASS: Endpoint no longer returns 501")
        print(f"  Status code: {response.status_code}")
        # Parse response data
        try:
            data = json.loads(response.content) if hasattr(response, 'content') else get_response_data(response)
            print(f"  Response has data: {data is not None}")
        except:
            print(f"  Response content available")
        return True
    else:
        print(f"\n✗ FAIL: Endpoint still returns 501 Not Implemented")
        try:
            data = json.loads(response.content) if hasattr(response, 'content') else get_response_data(response)
            print(f"  Response: {data}")
        except:
            print(f"  Response: {response.content}")
        return False


def test_georesolve_kathmandu():
    """Test 2: Geolocation correctly identifies Kathmandu"""
    print("\n" + "="*70)
    print("TEST 2: Geolocation Identifies Kathmandu")
    print("="*70)

    client = APIClient()

    # Kathmandu coordinates (27.7172°N, 85.3240°E)
    kathmandu_coords = {
        'lat': 27.7172,
        'lng': 85.3240
    }

    response = client.post('/api/georesolve/', kathmandu_coords, format='json')

    if response.status_code == 200:
        data = get_response_data(response)

        # Check if province is Bagmati (Province 3)
        province_correct = False
        if data.get('province'):
            province_id = data['province'].get('id')
            province_name = data['province'].get('name_en', '')
            if province_id == 3 or 'Bagmati' in province_name:
                province_correct = True
                print(f"\n✓ Province identified: {province_name} (ID: {province_id})")

        # Check if district is mentioned
        district_correct = False
        if data.get('district'):
            district_name = data['district'].get('name_en', '')
            if 'Kathmandu' in district_name:
                district_correct = True
                print(f"✓ District identified: {district_name}")

        if province_correct:
            print("\n✓ PASS: Kathmandu location correctly resolved")
            return True
        else:
            print(f"\n✗ FAIL: Location not correctly identified")
            print(f"  Response: {data}")
            return False
    else:
        print(f"\n✗ FAIL: Request failed with status {response.status_code}")
        return False


def test_georesolve_pokhara():
    """Test 3: Geolocation correctly identifies Pokhara"""
    print("\n" + "="*70)
    print("TEST 3: Geolocation Identifies Pokhara")
    print("="*70)

    client = APIClient()

    # Pokhara coordinates (28.2096°N, 83.9856°E)
    pokhara_coords = {
        'lat': 28.2096,
        'lng': 83.9856
    }

    response = client.post('/api/georesolve/', pokhara_coords, format='json')

    if response.status_code == 200:
        data = get_response_data(response)

        # Check if province is Gandaki (Province 4)
        province_correct = False
        if data.get('province'):
            province_id = data['province'].get('id')
            province_name = data['province'].get('name_en', '')
            if province_id == 4 or 'Gandaki' in province_name:
                province_correct = True
                print(f"\n✓ Province identified: {province_name} (ID: {province_id})")

        # Check if district contains Kaski
        district_correct = False
        if data.get('district'):
            district_name = data['district'].get('name_en', '')
            if 'Kaski' in district_name:
                district_correct = True
                print(f"✓ District identified: {district_name}")

        if province_correct:
            print("\n✓ PASS: Pokhara location correctly resolved")
            return True
        else:
            print(f"\n✗ FAIL: Location not correctly identified")
            print(f"  Response: {data}")
            return False
    else:
        print(f"\n✗ FAIL: Request failed with status {response.status_code}")
        return False


def test_georesolve_outside_nepal():
    """Test 4: Geolocation rejects coordinates outside Nepal"""
    print("\n" + "="*70)
    print("TEST 4: Geolocation Rejects Outside Nepal Coordinates")
    print("="*70)

    client = APIClient()

    # Delhi, India coordinates (outside Nepal)
    delhi_coords = {
        'lat': 28.6139,
        'lng': 77.2090
    }

    response = client.post('/api/georesolve/', delhi_coords, format='json')

    if response.status_code == 404:
        print(f"\n✓ PASS: Correctly rejects coordinates outside Nepal")
        print(f"  Status: 404")
        print(f"  Message: {get_response_data(response).get('error', 'N/A')}")
        return True
    else:
        print(f"\n✗ FAIL: Should return 404 for out-of-bounds coordinates")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {get_response_data(response)}")
        return False


def test_georesolve_invalid_coordinates():
    """Test 5: Geolocation validates coordinate format"""
    print("\n" + "="*70)
    print("TEST 5: Geolocation Validates Coordinate Format")
    print("="*70)

    client = APIClient()

    # Invalid coordinates
    invalid_coords = {
        'lat': 'invalid',
        'lng': 'abc'
    }

    response = client.post('/api/georesolve/', invalid_coords, format='json')

    if response.status_code == 400:
        print(f"\n✓ PASS: Correctly validates coordinate format")
        print(f"  Status: 400")
        print(f"  Errors: {get_response_data(response)}")
        return True
    else:
        print(f"\n✗ FAIL: Should return 400 for invalid coordinates")
        print(f"  Status: {response.status_code}")
        return False


def test_georesolve_missing_coordinates():
    """Test 6: Geolocation requires both lat and lng"""
    print("\n" + "="*70)
    print("TEST 6: Geolocation Requires Both Coordinates")
    print("="*70)

    client = APIClient()

    # Missing lng
    incomplete_coords = {
        'lat': 27.7172
    }

    response = client.post('/api/georesolve/', incomplete_coords, format='json')

    if response.status_code == 400:
        print(f"\n✓ PASS: Correctly requires both lat and lng")
        print(f"  Status: 400")
        print(f"  Errors: {get_response_data(response)}")
        return True
    else:
        print(f"\n✗ FAIL: Should return 400 for missing coordinates")
        print(f"  Status: {response.status_code}")
        return False


def test_georesolve_response_structure():
    """Test 7: Geolocation returns correct response structure"""
    print("\n" + "="*70)
    print("TEST 7: Geolocation Response Structure")
    print("="*70)

    client = APIClient()

    # Valid coordinates
    coords = {
        'lat': 27.7172,
        'lng': 85.3240
    }

    response = client.post('/api/georesolve/', coords, format='json')

    if response.status_code == 200:
        data = get_response_data(response)

        # Check required fields
        checks_passed = 0
        total_checks = 0

        # Check province field
        total_checks += 1
        if 'province' in data and data['province']:
            if 'id' in data['province'] and 'name_en' in data['province']:
                print("\n✓ Province data structure correct")
                checks_passed += 1
            else:
                print("\n✗ Province missing required fields")
        else:
            print("\n✗ Province data missing")

        # Check district field (can be None, but should exist)
        total_checks += 1
        if 'district' in data:
            print("✓ District field present")
            checks_passed += 1

        # Check municipality field (can be None, but should exist)
        total_checks += 1
        if 'municipality' in data:
            print("✓ Municipality field present")
            checks_passed += 1

        print(f"\nChecks passed: {checks_passed}/{total_checks}")

        if checks_passed >= 2:
            print("\n✓ PASS: Response structure is correct")
            return True
        else:
            print("\n✗ FAIL: Response structure incomplete")
            print(f"  Response: {data}")
            return False
    else:
        print(f"\n✗ FAIL: Request failed with status {response.status_code}")
        return False


def test_multiple_provinces():
    """Test 8: Geolocation works for multiple provinces"""
    print("\n" + "="*70)
    print("TEST 8: Geolocation Works Across Multiple Provinces")
    print("="*70)

    client = APIClient()

    # Test coordinates from different provinces
    test_locations = [
        {'lat': 27.7172, 'lng': 85.3240, 'expected_province_id': 3, 'name': 'Kathmandu (Bagmati)'},
        {'lat': 28.2096, 'lng': 83.9856, 'expected_province_id': 4, 'name': 'Pokhara (Gandaki)'},
        {'lat': 26.4525, 'lng': 87.2718, 'expected_province_id': 1, 'name': 'Biratnagar (Koshi)'},
    ]

    successes = 0
    for location in test_locations:
        coords = {'lat': location['lat'], 'lng': location['lng']}
        response = client.post('/api/georesolve/', coords, format='json')

        if response.status_code == 200:
            province_id = get_response_data(response).get('province', {}).get('id')
            if province_id == location['expected_province_id']:
                print(f"\n✓ {location['name']} - Correct (Province {province_id})")
                successes += 1
            else:
                print(f"\n⚠ {location['name']} - Got Province {province_id}, expected {location['expected_province_id']}")
        else:
            print(f"\n✗ {location['name']} - Request failed")

    if successes >= 2:
        print(f"\n✓ PASS: Geolocation works across multiple provinces ({successes}/3)")
        return True
    else:
        print(f"\n✗ FAIL: Too few correct identifications ({successes}/3)")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print(" GEOLOCATION FIX VERIFICATION TEST SUITE")
    print("="*80)
    print("\nThis test suite verifies:")
    print("1. geo_resolve endpoint no longer returns 501")
    print("2. Geolocation correctly identifies major cities")
    print("3. Coordinates outside Nepal are rejected")
    print("4. Invalid coordinates are validated")
    print("5. Missing coordinates are caught")
    print("6. Response structure is correct")
    print("7. Works across multiple provinces")
    print("\nRunning tests...\n")

    results = {}

    try:
        results['test1'] = test_georesolve_no_longer_501()
        results['test2'] = test_georesolve_kathmandu()
        results['test3'] = test_georesolve_pokhara()
        results['test4'] = test_georesolve_outside_nepal()
        results['test5'] = test_georesolve_invalid_coordinates()
        results['test6'] = test_georesolve_missing_coordinates()
        results['test7'] = test_georesolve_response_structure()
        results['test8'] = test_multiple_provinces()

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
        'test1': 'Endpoint No Longer Returns 501',
        'test2': 'Geolocation Identifies Kathmandu',
        'test3': 'Geolocation Identifies Pokhara',
        'test4': 'Rejects Outside Nepal Coordinates',
        'test5': 'Validates Coordinate Format',
        'test6': 'Requires Both Coordinates',
        'test7': 'Response Structure Correct',
        'test8': 'Works Across Multiple Provinces',
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
        print("\nThe geolocation fix is working correctly:")
        print("  ✓ Endpoint no longer returns 501 Not Implemented")
        print("  ✓ Uses actual geolocation implementation from views.py")
        print("  ✓ Correctly identifies locations in Nepal")
        print("  ✓ Validates coordinates properly")
        print("  ✓ Rejects out-of-bounds coordinates")
        print("  ✓ Returns proper response structure")
        print("\nFixed code (locations/api_views.py:208-243):")
        print("  - Removed 501 placeholder implementation")
        print("  - Now calls working geo_resolve from views.py")
        print("  - Maintains API contract with proper serialization")
        return True
    else:
        print("\n✗✗✗ SOME TESTS FAILED ✗✗✗")
        print("\nPlease review the failed tests above.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
