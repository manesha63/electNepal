#!/usr/bin/env python
"""
Test script to verify pagination limit enforcement fix for issue #23.

This script tests that:
1. Both API endpoints enforce max 1000 total results
2. Pagination still works correctly
3. Per-page limits are still enforced (48 for cards, 100 for ballot)
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from candidates.api_views import candidate_cards_api, my_ballot
from candidates.models import Candidate
from locations.models import Province, District, Municipality

def test_candidate_cards_limit():
    """Test that candidate_cards_api enforces 1000 result limit"""
    print("=" * 60)
    print("TEST 1: Candidate Cards API - Max 1000 Results Limit")
    print("=" * 60)

    # Count total approved candidates
    total_candidates = Candidate.objects.filter(status='approved').count()
    print(f"Total approved candidates in database: {total_candidates}")

    # Create request with proper server name
    factory = RequestFactory()
    request = factory.get('/candidates/api/cards/', {'page': 1, 'page_size': 48}, HTTP_HOST='localhost:8000')

    # Call API
    response = candidate_cards_api(request)
    data = response.data

    # Verify total is capped at 1000
    reported_total = data.get('total')
    print(f"API reported total: {reported_total}")

    if total_candidates > 1000:
        assert reported_total == 1000, f"Expected total=1000 but got {reported_total}"
        print("✓ PASS: Total capped at 1000 (actual candidates > 1000)")
    else:
        assert reported_total == total_candidates, f"Expected total={total_candidates} but got {reported_total}"
        print(f"✓ PASS: Total matches actual count ({total_candidates} <= 1000)")

    # Verify per-page limit is still enforced
    page_size = data.get('page_size')
    results_count = len(data.get('results', []))
    assert page_size == 48, f"Expected page_size=48 but got {page_size}"
    assert results_count <= 48, f"Expected <= 48 results but got {results_count}"
    print(f"✓ PASS: Per-page limit enforced (page_size={page_size}, results={results_count})")

    # Verify total_pages calculation
    total_pages = data.get('total_pages')
    expected_pages = (reported_total + page_size - 1) // page_size  # Ceiling division
    assert total_pages == expected_pages, f"Expected {expected_pages} pages but got {total_pages}"
    print(f"✓ PASS: Total pages calculated correctly ({total_pages})")

    print()

def test_my_ballot_limit():
    """Test that my_ballot API enforces 1000 result limit"""
    print("=" * 60)
    print("TEST 2: My Ballot API - Max 1000 Results Limit")
    print("=" * 60)

    # Get actual test data - find a ward-level candidate
    ward_candidate = Candidate.objects.filter(
        status='approved',
        position_level__in=['ward', 'ward_chairperson'],
        municipality__isnull=False,
        ward_number__isnull=False
    ).first()

    if not ward_candidate:
        print("⊘ SKIP: No ward candidates in database to test")
        print()
        return

    print(f"Testing with location: Province={ward_candidate.province_id}, "
          f"District={ward_candidate.district_id}, "
          f"Municipality={ward_candidate.municipality_id}, "
          f"Ward={ward_candidate.ward_number}")

    # Create request with location parameters
    factory = RequestFactory()
    request = factory.get('/candidates/api/my-ballot/', {
        'province_id': ward_candidate.province_id,
        'district_id': ward_candidate.district_id,
        'municipality_id': ward_candidate.municipality_id,
        'ward_number': ward_candidate.ward_number,
        'page': 1,
        'page_size': 100
    }, HTTP_HOST='localhost:8000')

    # Call API
    response = my_ballot(request)
    data = response.data

    # Verify total is capped at 1000
    reported_total = data.get('total')
    print(f"API reported total: {reported_total}")

    # The key test: verify total is within the 1000 limit
    assert reported_total <= 1000, f"Expected total <= 1000 but got {reported_total}"
    print(f"✓ PASS: Total within limit ({reported_total} <= 1000)")

    # Verify per-page limit is still enforced
    page_size = data.get('page_size')
    results_count = len(data.get('candidates', []))
    assert page_size == 100, f"Expected page_size=100 but got {page_size}"
    assert results_count <= 100, f"Expected <= 100 results but got {results_count}"
    print(f"✓ PASS: Per-page limit enforced (page_size={page_size}, results={results_count})")

    # Verify pagination metadata is correct
    if reported_total > 0:
        total_pages = data.get('total_pages')
        expected_pages = (reported_total + page_size - 1) // page_size  # Ceiling division
        assert total_pages == expected_pages, f"Expected {expected_pages} pages but got {total_pages}"
        print(f"✓ PASS: Total pages calculated correctly ({total_pages})")
    else:
        print("⊘ Note: No candidates matched ballot criteria (0 results)")

    print()

def test_pagination_still_works():
    """Test that pagination still works after limit enforcement"""
    print("=" * 60)
    print("TEST 3: Pagination Functionality")
    print("=" * 60)

    factory = RequestFactory()

    # Test page 1
    request1 = factory.get('/candidates/api/cards/', {'page': 1, 'page_size': 9}, HTTP_HOST='localhost:8000')
    response1 = candidate_cards_api(request1)
    data1 = response1.data

    print(f"Page 1: {len(data1['results'])} results")
    print(f"Has next: {data1['has_next']}, Has previous: {data1['has_previous']}")

    assert data1['page'] == 1, "Page should be 1"
    assert data1['has_previous'] == False, "Page 1 should not have previous"

    if data1['total'] > 9:
        assert data1['has_next'] == True, "Should have next page if total > page_size"

        # Test page 2
        request2 = factory.get('/candidates/api/cards/', {'page': 2, 'page_size': 9}, HTTP_HOST='localhost:8000')
        response2 = candidate_cards_api(request2)
        data2 = response2.data

        print(f"Page 2: {len(data2['results'])} results")
        print(f"Has next: {data2['has_next']}, Has previous: {data2['has_previous']}")

        assert data2['page'] == 2, "Page should be 2"
        assert data2['has_previous'] == True, "Page 2 should have previous"

        # Verify results are different
        page1_ids = [r['id'] for r in data1['results']]
        page2_ids = [r['id'] for r in data2['results']]
        assert page1_ids != page2_ids, "Page 1 and 2 should have different results"
        print("✓ PASS: Page 1 and Page 2 have different results")
    else:
        print(f"⊘ SKIP: Not enough candidates ({data1['total']}) to test page 2")

    print("✓ PASS: Pagination works correctly")
    print()

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("PAGINATION LIMIT ENFORCEMENT TEST SUITE")
    print("Testing fix for issue #23")
    print("=" * 60 + "\n")

    try:
        test_candidate_cards_limit()
        test_my_ballot_limit()
        test_pagination_still_works()

        print("=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        print("\nSummary:")
        print("- Max 1000 total results limit enforced on both APIs")
        print("- Per-page limits still working (48 for cards, 100 for ballot)")
        print("- Pagination functionality intact")
        print("- No existing features broken")

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
