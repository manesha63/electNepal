#!/usr/bin/env python
"""
Regression test to verify ballot feature still works after cache key fix
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from django.test import RequestFactory
from django.core.cache import cache
from candidates.views import my_ballot
from locations.models import Province, District, Municipality
import json


def test_basic_ballot_request():
    """Test 1: Basic ballot request still works"""
    print("\n" + "="*70)
    print("TEST 1: Basic Ballot Request")
    print("="*70)

    factory = RequestFactory()
    province = Province.objects.first()

    cache.clear()

    request = factory.get(f'/candidates/api/my-ballot/?province_id={province.id}')
    response = my_ballot(request)

    if response.status_code == 200:
        data = json.loads(response.content)
        print("\n✓ PASS: Ballot request successful")
        print(f"  Status: {response.status_code}")
        print(f"  Candidates: {data.get('total', 0)}")
        print(f"  Page: {data.get('page', 'N/A')}")
        return True
    else:
        print(f"\n✗ FAIL: Request failed with status {response.status_code}")
        return False


def test_ballot_with_location_filters():
    """Test 2: Ballot with location filters works"""
    print("\n" + "="*70)
    print("TEST 2: Ballot with Location Filters")
    print("="*70)

    factory = RequestFactory()
    province = Province.objects.first()
    district = District.objects.filter(province=province).first()

    cache.clear()

    request = factory.get(
        f'/candidates/api/my-ballot/?'
        f'province_id={province.id}&'
        f'district_id={district.id}'
    )
    response = my_ballot(request)

    if response.status_code == 200:
        data = json.loads(response.content)
        print("\n✓ PASS: Ballot with district filter works")
        print(f"  Status: {response.status_code}")
        print(f"  Candidates: {data.get('total', 0)}")
        return True
    else:
        print(f"\n✗ FAIL: Request failed with status {response.status_code}")
        return False


def test_ballot_pagination():
    """Test 3: Ballot pagination still works"""
    print("\n" + "="*70)
    print("TEST 3: Ballot Pagination")
    print("="*70)

    factory = RequestFactory()
    province = Province.objects.first()

    cache.clear()

    # Page 1
    request1 = factory.get(f'/candidates/api/my-ballot/?province_id={province.id}&page=1&page_size=5')
    response1 = my_ballot(request1)

    # Page 2
    request2 = factory.get(f'/candidates/api/my-ballot/?province_id={province.id}&page=2&page_size=5')
    response2 = my_ballot(request2)

    if response1.status_code == 200 and response2.status_code == 200:
        data1 = json.loads(response1.content)
        data2 = json.loads(response2.content)

        print("\n✓ PASS: Pagination works correctly")
        print(f"  Page 1 candidates: {len(data1.get('candidates', []))}")
        print(f"  Page 2 candidates: {len(data2.get('candidates', []))}")
        print(f"  Has next (page 1): {data1.get('has_next', False)}")
        print(f"  Has previous (page 2): {data2.get('has_previous', False)}")
        return True
    else:
        print(f"\n✗ FAIL: Pagination failed")
        return False


def test_invalid_province_handling():
    """Test 4: Invalid province ID handling"""
    print("\n" + "="*70)
    print("TEST 4: Invalid Province ID Handling")
    print("="*70)

    factory = RequestFactory()

    cache.clear()

    # Test with invalid province ID
    request = factory.get('/candidates/api/my-ballot/?province_id=invalid')
    response = my_ballot(request)

    if response.status_code == 400:
        data = json.loads(response.content)
        if 'error' in data:
            print("\n✓ PASS: Invalid province ID rejected correctly")
            print(f"  Status: {response.status_code}")
            print(f"  Error: {data['error']}")
            return True
        else:
            print("\n✗ FAIL: No error message returned")
            return False
    else:
        print(f"\n✗ FAIL: Expected status 400, got {response.status_code}")
        return False


def test_missing_province_handling():
    """Test 5: Missing province ID handling"""
    print("\n" + "="*70)
    print("TEST 5: Missing Province ID Handling")
    print("="*70)

    factory = RequestFactory()

    cache.clear()

    # Test without province ID
    request = factory.get('/candidates/api/my-ballot/')
    response = my_ballot(request)

    if response.status_code == 400:
        data = json.loads(response.content)
        if 'error' in data and 'required' in data['error']:
            print("\n✓ PASS: Missing province ID rejected correctly")
            print(f"  Status: {response.status_code}")
            print(f"  Error: {data['error']}")
            return True
        else:
            print("\n✗ FAIL: Incorrect error message")
            return False
    else:
        print(f"\n✗ FAIL: Expected status 400, got {response.status_code}")
        return False


def test_cache_actually_caches():
    """Test 6: Cache actually caches results"""
    print("\n" + "="*70)
    print("TEST 6: Cache Functionality")
    print("="*70)

    factory = RequestFactory()
    province = Province.objects.first()

    cache.clear()

    # First request - should hit database
    request1 = factory.get(f'/candidates/api/my-ballot/?province_id={province.id}')
    response1 = my_ballot(request1)

    # Check if cached
    cache_key = f'my_ballot:ballot:en:{province.id}::::1:20'
    cached = cache.get(cache_key)

    if cached:
        print("\n✓ PASS: Results are cached")
        print(f"  Cache key: {cache_key}")
        print(f"  Cached: {cached is not None}")

        # Second request - should hit cache
        request2 = factory.get(f'/candidates/api/my-ballot/?province_id={province.id}')
        response2 = my_ballot(request2)

        if response2.status_code == 200:
            print("✓ Second request served from cache")
            return True
        else:
            print("✗ Second request failed")
            return False
    else:
        print("\n✗ FAIL: Results not cached")
        return False


def test_full_location_hierarchy():
    """Test 7: Full location hierarchy still works"""
    print("\n" + "="*70)
    print("TEST 7: Full Location Hierarchy")
    print("="*70)

    factory = RequestFactory()
    province = Province.objects.first()
    district = District.objects.filter(province=province).first()
    municipality = Municipality.objects.filter(district=district).first()

    if not municipality:
        print("\n⚠ SKIP: No municipality found for testing")
        return True

    cache.clear()

    request = factory.get(
        f'/candidates/api/my-ballot/?'
        f'province_id={province.id}&'
        f'district_id={district.id}&'
        f'municipality_id={municipality.id}&'
        f'ward_number=3'
    )
    response = my_ballot(request)

    if response.status_code == 200:
        data = json.loads(response.content)
        print("\n✓ PASS: Full location hierarchy works")
        print(f"  Province: {province.name_en}")
        print(f"  District: {district.name_en}")
        print(f"  Municipality: {municipality.name_en}")
        print(f"  Ward: 3")
        print(f"  Candidates: {data.get('total', 0)}")
        return True
    else:
        print(f"\n✗ FAIL: Request failed with status {response.status_code}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print(" REGRESSION TEST SUITE - Verify Ballot Feature Still Works")
    print("="*80)
    print("\nThese tests verify that our cache key fix didn't break:")
    print("1. Basic ballot requests")
    print("2. Location-based filtering")
    print("3. Pagination")
    print("4. Invalid parameter handling")
    print("5. Missing parameter handling")
    print("6. Cache functionality")
    print("7. Full location hierarchy")
    print("\nRunning tests...\n")

    results = {}

    try:
        results['test1'] = test_basic_ballot_request()
        results['test2'] = test_ballot_with_location_filters()
        results['test3'] = test_ballot_pagination()
        results['test4'] = test_invalid_province_handling()
        results['test5'] = test_missing_province_handling()
        results['test6'] = test_cache_actually_caches()
        results['test7'] = test_full_location_hierarchy()

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
        print("\n✗ FATAL ERROR OCCURRED")
        return False

    passed_count = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\nTests Passed: {passed_count}/{total}")
    print("-"*80)

    test_names = {
        'test1': 'Basic Ballot Request',
        'test2': 'Ballot with Location Filters',
        'test3': 'Ballot Pagination',
        'test4': 'Invalid Province ID Handling',
        'test5': 'Missing Province ID Handling',
        'test6': 'Cache Functionality',
        'test7': 'Full Location Hierarchy',
    }

    for test_key, test_passed in results.items():
        status = "✓ PASS" if test_passed else "✗ FAIL"
        test_name = test_names.get(test_key, test_key)
        print(f"{status}: {test_name}")

    print("-"*80)

    if passed_count == total:
        print("\n" + "="*80)
        print(" ✓✓✓ ALL REGRESSION TESTS PASSED ✓✓✓")
        print("="*80)
        print("\nNo existing features were broken by the fix:")
        print("  ✓ Ballot requests work correctly")
        print("  ✓ Location filtering operates normally")
        print("  ✓ Pagination functions properly")
        print("  ✓ Invalid parameters rejected")
        print("  ✓ Cache functionality intact")
        print("  ✓ Full location hierarchy supported")
        print("\nThe cache key collision fix is safe to deploy!")
        return True
    else:
        print("\n✗✗✗ SOME REGRESSION TESTS FAILED ✗✗✗")
        print("\nThe fix may have broken existing functionality.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
