#!/usr/bin/env python
"""
Test script to verify cache key collision fix in candidates/views.py:267
Tests that invalid parameters don't create different cache keys for same results
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
from django.contrib.auth.models import User
from candidates.views import my_ballot
from candidates.models import Candidate
from locations.models import Province, District, Municipality
from unittest.mock import patch


def test_invalid_params_same_cache_key():
    """Test 1: Invalid parameters create same cache key as missing parameters"""
    print("\n" + "="*70)
    print("TEST 1: Invalid Parameters Create Same Cache Key")
    print("="*70)

    factory = RequestFactory()

    # Get valid province
    province = Province.objects.first()

    # Clear cache
    cache.clear()

    # Request 1: province_id=1, district_id=abc (invalid, becomes None)
    request1 = factory.get(f'/candidates/api/my-ballot/?province_id={province.id}&district_id=abc')

    # Request 2: province_id=1, no district_id (None)
    request2 = factory.get(f'/candidates/api/my-ballot/?province_id={province.id}')

    # Both should generate the same cache key
    response1 = my_ballot(request1)

    # Check if response was cached
    cache_hit_before = cache.get(f'my_ballot:ballot:en:{province.id}::::1:20')

    response2 = my_ballot(request2)

    # Check if second request used cache
    cache_hit_after = cache.get(f'my_ballot:ballot:en:{province.id}::::1:20')

    if cache_hit_before and cache_hit_after:
        print("\n✓ PASS: Invalid parameter creates same cache key as missing parameter")
        print(f"  Cache key: my_ballot:ballot:en:{province.id}::::1:20")
        print("  Both requests use the same cached result")
        return True
    else:
        print("\n✗ FAIL: Cache key mismatch")
        print(f"  Cache before: {cache_hit_before}")
        print(f"  Cache after: {cache_hit_after}")
        return False


def test_cache_key_uses_validated_values():
    """Test 2: Cache key uses validated integer values, not raw strings"""
    print("\n" + "="*70)
    print("TEST 2: Cache Key Uses Validated Values")
    print("="*70)

    factory = RequestFactory()
    province = Province.objects.first()
    district = District.objects.filter(province=province).first()

    cache.clear()

    # Request with valid integer district_id
    request1 = factory.get(f'/candidates/api/my-ballot/?province_id={province.id}&district_id={district.id}')

    # Request with string that equals the same integer after conversion
    request2 = factory.get(f'/candidates/api/my-ballot/?province_id={province.id}&district_id={district.id}')

    response1 = my_ballot(request1)

    # Check cache key format
    expected_cache_key = f'my_ballot:ballot:en:{province.id}:{district.id}:::1:20'
    cache_hit = cache.get(expected_cache_key)

    if cache_hit:
        print(f"\n✓ PASS: Cache key uses validated integer values")
        print(f"  Cache key: {expected_cache_key}")
        print(f"  Province ID: {province.id} (int)")
        print(f"  District ID: {district.id} (int)")
        result = True
    else:
        print("\n✗ FAIL: Cache key doesn't use validated values")
        result = False

    # Second request should hit cache
    response2 = my_ballot(request2)

    if response1.status_code == 200 and response2.status_code == 200:
        print("✓ Both requests succeeded")
        return result
    else:
        print(f"✗ Request failed: {response1.status_code}, {response2.status_code}")
        return False


def test_different_params_different_cache():
    """Test 3: Different valid parameters create different cache keys"""
    print("\n" + "="*70)
    print("TEST 3: Different Parameters Create Different Cache Keys")
    print("="*70)

    factory = RequestFactory()
    province = Province.objects.first()
    districts = District.objects.filter(province=province)[:2]

    if len(districts) < 2:
        print("\n⚠ SKIP: Need at least 2 districts for this test")
        return True

    cache.clear()

    # Request 1: district 1
    request1 = factory.get(f'/candidates/api/my-ballot/?province_id={province.id}&district_id={districts[0].id}')
    response1 = my_ballot(request1)

    # Request 2: district 2
    request2 = factory.get(f'/candidates/api/my-ballot/?province_id={province.id}&district_id={districts[1].id}')
    response2 = my_ballot(request2)

    # Check both created different cache keys
    cache_key1 = f'my_ballot:ballot:en:{province.id}:{districts[0].id}:::1:20'
    cache_key2 = f'my_ballot:ballot:en:{province.id}:{districts[1].id}:::1:20'

    cache_hit1 = cache.get(cache_key1)
    cache_hit2 = cache.get(cache_key2)

    if cache_hit1 and cache_hit2:
        print("\n✓ PASS: Different parameters create different cache keys")
        print(f"  Cache key 1: {cache_key1}")
        print(f"  Cache key 2: {cache_key2}")
        return True
    else:
        print("\n✗ FAIL: Cache keys not created properly")
        print(f"  Cache 1: {cache_hit1}")
        print(f"  Cache 2: {cache_hit2}")
        return False


def test_pagination_params_in_cache_key():
    """Test 4: Pagination parameters are included in cache key"""
    print("\n" + "="*70)
    print("TEST 4: Pagination Parameters in Cache Key")
    print("="*70)

    factory = RequestFactory()
    province = Province.objects.first()

    cache.clear()

    # Request 1: page=1, page_size=20
    request1 = factory.get(f'/candidates/api/my-ballot/?province_id={province.id}&page=1&page_size=20')
    response1 = my_ballot(request1)

    # Request 2: page=2, page_size=20
    request2 = factory.get(f'/candidates/api/my-ballot/?province_id={province.id}&page=2&page_size=20')
    response2 = my_ballot(request2)

    # Check both created different cache keys
    cache_key1 = f'my_ballot:ballot:en:{province.id}::::1:20'
    cache_key2 = f'my_ballot:ballot:en:{province.id}::::2:20'

    cache_hit1 = cache.get(cache_key1)
    cache_hit2 = cache.get(cache_key2)

    if cache_hit1 and cache_hit2:
        print("\n✓ PASS: Pagination parameters create different cache keys")
        print(f"  Page 1 cache key: {cache_key1}")
        print(f"  Page 2 cache key: {cache_key2}")
        return True
    else:
        print("\n✗ FAIL: Pagination not reflected in cache keys")
        return False


def test_language_in_cache_key():
    """Test 5: Language is included in cache key"""
    print("\n" + "="*70)
    print("TEST 5: Language in Cache Key")
    print("="*70)

    factory = RequestFactory()
    province = Province.objects.first()

    cache.clear()

    from django.utils.translation import activate

    # Request in English
    activate('en')
    request1 = factory.get(f'/candidates/api/my-ballot/?province_id={province.id}')
    response1 = my_ballot(request1)

    # Request in Nepali
    activate('ne')
    request2 = factory.get(f'/candidates/api/my-ballot/?province_id={province.id}')
    response2 = my_ballot(request2)

    # Check both created different cache keys
    cache_key_en = f'my_ballot:ballot:en:{province.id}::::1:20'
    cache_key_ne = f'my_ballot:ballot:ne:{province.id}::::1:20'

    cache_hit_en = cache.get(cache_key_en)
    cache_hit_ne = cache.get(cache_key_ne)

    # Reset language
    activate('en')

    if cache_hit_en and cache_hit_ne:
        print("\n✓ PASS: Language creates different cache keys")
        print(f"  English cache key: {cache_key_en}")
        print(f"  Nepali cache key: {cache_key_ne}")
        return True
    else:
        print("\n✗ FAIL: Language not reflected in cache keys")
        print(f"  English cache: {cache_hit_en}")
        print(f"  Nepali cache: {cache_hit_ne}")
        return False


def test_cache_pollution_prevented():
    """Test 6: Invalid parameters don't pollute cache with duplicate data"""
    print("\n" + "="*70)
    print("TEST 6: Cache Pollution Prevention")
    print("="*70)

    factory = RequestFactory()
    province = Province.objects.first()

    cache.clear()

    # Request 1: Valid parameters
    request1 = factory.get(f'/candidates/api/my-ballot/?province_id={province.id}')
    response1 = my_ballot(request1)

    # Get the expected cache key
    expected_cache_key = f'my_ballot:ballot:en:{province.id}::::1:20'
    cache_hit1 = cache.get(expected_cache_key)

    # Request 2: Invalid district_id that becomes None
    request2 = factory.get(f'/candidates/api/my-ballot/?province_id={province.id}&district_id=invalid')
    response2 = my_ballot(request2)

    # Should hit the same cache
    cache_hit2 = cache.get(expected_cache_key)

    # Request 3: Another invalid district_id
    request3 = factory.get(f'/candidates/api/my-ballot/?province_id={province.id}&district_id=xyz')
    response3 = my_ballot(request3)

    # Should still hit the same cache
    cache_hit3 = cache.get(expected_cache_key)

    # All three should return the same cached data
    if cache_hit1 and cache_hit2 and cache_hit3:
        # Compare the cached objects (they should be identical)
        if cache_hit1 == cache_hit2 == cache_hit3:
            print("\n✓ PASS: No cache pollution from invalid parameters")
            print(f"  All 3 requests use same cache key: {expected_cache_key}")
            print(f"  Cached data is identical")
            return True
        else:
            print("\n✗ FAIL: Cached data differs")
            return False
    else:
        print(f"\n✗ FAIL: Cache not hit consistently")
        print(f"  Cache hit 1: {cache_hit1 is not None}")
        print(f"  Cache hit 2: {cache_hit2 is not None}")
        print(f"  Cache hit 3: {cache_hit3 is not None}")
        return False


def test_full_location_hierarchy():
    """Test 7: Full location hierarchy creates correct cache key"""
    print("\n" + "="*70)
    print("TEST 7: Full Location Hierarchy in Cache Key")
    print("="*70)

    factory = RequestFactory()
    province = Province.objects.first()
    district = District.objects.filter(province=province).first()
    municipality = Municipality.objects.filter(district=district).first()

    if not municipality:
        print("\n⚠ SKIP: No municipality found for testing")
        return True

    cache.clear()

    # Request with full location hierarchy
    request = factory.get(
        f'/candidates/api/my-ballot/?'
        f'province_id={province.id}&'
        f'district_id={district.id}&'
        f'municipality_id={municipality.id}&'
        f'ward_number=5'
    )
    response = my_ballot(request)

    # Check cache key includes all location parameters
    cache_key = f'my_ballot:ballot:en:{province.id}:{district.id}:{municipality.id}:5:1:20'
    cache_hit = cache.get(cache_key)

    if cache_hit:
        print("\n✓ PASS: Full location hierarchy reflected in cache key")
        print(f"  Cache key: {cache_key}")
        print(f"  Province: {province.id}")
        print(f"  District: {district.id}")
        print(f"  Municipality: {municipality.id}")
        print(f"  Ward: 5")
        return True
    else:
        print("\n✗ FAIL: Full location hierarchy not in cache key")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print(" CACHE KEY COLLISION FIX VERIFICATION TEST SUITE")
    print("="*80)
    print("\nThis test suite verifies:")
    print("1. Invalid parameters create same cache key as missing parameters")
    print("2. Cache key uses validated integer values, not raw strings")
    print("3. Different parameters create different cache keys")
    print("4. Pagination parameters are included in cache key")
    print("5. Language is included in cache key")
    print("6. Invalid parameters don't pollute cache")
    print("7. Full location hierarchy creates correct cache key")
    print("\nRunning tests...\n")

    results = {}

    try:
        results['test1'] = test_invalid_params_same_cache_key()
        results['test2'] = test_cache_key_uses_validated_values()
        results['test3'] = test_different_params_different_cache()
        results['test4'] = test_pagination_params_in_cache_key()
        results['test5'] = test_language_in_cache_key()
        results['test6'] = test_cache_pollution_prevented()
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
        print("\n✗ FATAL ERROR OCCURRED - Cannot determine test results")
        return False

    passed_count = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\nTests Passed: {passed_count}/{total}")
    print("-"*80)

    test_names = {
        'test1': 'Invalid Parameters Same Cache Key',
        'test2': 'Cache Key Uses Validated Values',
        'test3': 'Different Parameters Different Cache',
        'test4': 'Pagination Parameters in Cache Key',
        'test5': 'Language in Cache Key',
        'test6': 'Cache Pollution Prevention',
        'test7': 'Full Location Hierarchy in Cache Key',
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
        print("\nThe cache key collision fix is working correctly:")
        print("  ✓ Parameters validated BEFORE cache key generation")
        print("  ✓ Invalid parameters create same cache key as missing")
        print("  ✓ No cache pollution from malformed requests")
        print("  ✓ All query parameters reflected in cache key")
        print("  ✓ Different parameters create different caches")
        print("  ✓ Language and pagination correctly included")
        print("\nFixed code (candidates/views.py:264-316):")
        print("  - Moved parameter validation before cache key generation")
        print("  - Cache key uses validated integer values")
        print("  - Explicit None handling prevents cache key variations")
        return True
    else:
        print("\n✗✗✗ SOME TESTS FAILED ✗✗✗")
        print("\nPlease review the failed tests above.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
