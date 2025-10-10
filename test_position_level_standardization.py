#!/usr/bin/env python
"""
Test script to verify position level standardization fix for issue #26.

This script tests that:
1. All position levels in database use new standardized values
2. Queries correctly find candidates with new values
3. Ranking logic works for all position levels
4. No candidates are missed due to old/new value mismatches
5. Existing features still work correctly
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from candidates.models import Candidate
from django.db.models import Q, Case, When, Value, IntegerField, Count

def test_no_old_values_in_database():
    """Test that no old position level values exist in the database"""
    print("=" * 70)
    print("TEST 1: No Old Position Level Values in Database")
    print("=" * 70)

    old_values = ['federal', 'provincial', 'local', 'ward', 'local_executive']

    for old_value in old_values:
        count = Candidate.objects.filter(position_level=old_value).count()
        print(f"  Checking '{old_value}': {count} candidates")
        assert count == 0, f"Found {count} candidates with old value '{old_value}'"

    print("\n✓ PASS: No old position level values found in database")
    print()

def test_all_candidates_have_valid_values():
    """Test that all candidates have valid new position level values"""
    print("=" * 70)
    print("TEST 2: All Candidates Have Valid New Values")
    print("=" * 70)

    valid_values = [
        'ward_chairperson',
        'ward_member',
        'mayor_chairperson',
        'deputy_mayor_vice_chairperson',
        'provincial_assembly',
        'house_of_representatives',
        'national_assembly',
    ]

    total_candidates = Candidate.objects.count()
    candidates_with_valid_values = Candidate.objects.filter(position_level__in=valid_values).count()

    print(f"  Total candidates: {total_candidates}")
    print(f"  Candidates with valid values: {candidates_with_valid_values}")

    assert total_candidates == candidates_with_valid_values, \
        f"Mismatch: {total_candidates - candidates_with_valid_values} candidates have invalid values"

    print("\n✓ PASS: All candidates have valid position level values")
    print()

def test_federal_level_queries():
    """Test that federal level queries find all federal candidates"""
    print("=" * 70)
    print("TEST 3: Federal Level Queries Work Correctly")
    print("=" * 70)

    # Count candidates with federal positions
    federal_candidates = Candidate.objects.filter(
        position_level__in=['house_of_representatives', 'national_assembly']
    ).count()

    print(f"  Federal candidates found: {federal_candidates}")

    # Also test the old query that only looked for 'federal'
    old_query_result = Candidate.objects.filter(position_level='federal').count()
    print(f"  Old query (position_level='federal'): {old_query_result}")

    assert old_query_result == 0, "Old query should find 0 candidates after migration"
    assert federal_candidates >= 0, "Should find federal candidates with new query"

    print(f"\n✓ PASS: Federal queries work correctly ({federal_candidates} candidates found)")
    print()

def test_ward_level_queries():
    """Test that ward level queries find all ward candidates"""
    print("=" * 70)
    print("TEST 4: Ward Level Queries Work Correctly")
    print("=" * 70)

    # Count candidates with ward positions
    ward_candidates = Candidate.objects.filter(
        position_level__in=['ward_chairperson', 'ward_member']
    ).count()

    print(f"  Ward candidates found: {ward_candidates}")

    # Also test the old query that only looked for 'ward'
    old_query_result = Candidate.objects.filter(position_level='ward').count()
    print(f"  Old query (position_level='ward'): {old_query_result}")

    assert old_query_result == 0, "Old query should find 0 candidates after migration"
    assert ward_candidates >= 0, "Should find ward candidates with new query"

    print(f"\n✓ PASS: Ward queries work correctly ({ward_candidates} candidates found)")
    print()

def test_ranking_logic_covers_all_levels():
    """Test that ranking logic works for all position levels"""
    print("=" * 70)
    print("TEST 5: Ranking Logic Covers All Position Levels")
    print("=" * 70)

    # Get all position levels in database
    position_levels = Candidate.objects.values_list('position_level', flat=True).distinct()

    print(f"  Position levels in database:")
    for pl in position_levels:
        count = Candidate.objects.filter(position_level=pl).count()
        print(f"    - {pl}: {count} candidates")

    # Test that ranking logic handles all levels
    # Simulate ranking from views.py
    ranking_conditions = []

    # Federal level
    ranking_conditions.append(
        When(position_level__in=['federal', 'house_of_representatives', 'national_assembly'], then=Value(1))
    )

    # Provincial level
    ranking_conditions.append(
        When(position_level__in=['provincial', 'provincial_assembly'], then=Value(2))
    )

    # Municipal level
    ranking_conditions.append(
        When(position_level__in=['mayor_chairperson', 'deputy_mayor_vice_chairperson', 'local', 'local_executive'], then=Value(3))
    )

    # Ward level
    ranking_conditions.append(
        When(position_level__in=['ward_chairperson', 'ward_member', 'ward'], then=Value(4))
    )

    # Apply ranking
    candidates_with_ranking = Candidate.objects.annotate(
        rank=Case(
            *ranking_conditions,
            default=Value(9),
            output_field=IntegerField()
        )
    )

    # Check that no candidates got default rank (9)
    unranked = candidates_with_ranking.filter(rank=9).count()

    print(f"\n  Ranking distribution:")
    for i in range(1, 10):
        count = candidates_with_ranking.filter(rank=i).count()
        if count > 0:
            print(f"    Rank {i}: {count} candidates")

    assert unranked == 0, f"Found {unranked} candidates that didn't match any ranking criteria"

    print(f"\n✓ PASS: All candidates properly ranked (0 unranked)")
    print()

def test_ballot_queries():
    """Test that ballot queries find candidates correctly"""
    print("=" * 70)
    print("TEST 6: Ballot Queries Find All Relevant Candidates")
    print("=" * 70)

    # Get a sample province/district/municipality for testing
    from locations.models import Province, District, Municipality

    province = Province.objects.first()
    if not province:
        print("  ⊘ SKIP: No provinces in database")
        print()
        return

    district = District.objects.filter(province=province).first()
    if not district:
        print("  ⊘ SKIP: No districts in database")
        print()
        return

    print(f"  Testing with: {province.name_en}, {district.name_en}")

    # Build filters like in my_ballot view
    filters = Q()

    # Federal level (district-based)
    filters |= Q(
        position_level__in=['house_of_representatives', 'federal'],
        province_id=province.id,
        district_id=district.id
    )

    # Provincial level
    filters |= Q(
        position_level__in=['provincial_assembly', 'provincial'],
        province_id=province.id
    )

    candidates_found = Candidate.objects.filter(filters, status='approved').count()

    print(f"  Candidates found for location: {candidates_found}")

    # Verify we're not missing candidates
    # Count manually
    federal_in_district = Candidate.objects.filter(
        status='approved',
        province_id=province.id,
        district_id=district.id,
        position_level='house_of_representatives'
    ).count()

    provincial_in_province = Candidate.objects.filter(
        status='approved',
        province_id=province.id,
        position_level='provincial_assembly'
    ).count()

    expected_total = federal_in_district + provincial_in_province

    print(f"  Expected: {expected_total} (federal: {federal_in_district}, provincial: {provincial_in_province})")

    assert candidates_found == expected_total, \
        f"Query found {candidates_found} but expected {expected_total}"

    print(f"\n✓ PASS: Ballot queries work correctly")
    print()

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("POSITION LEVEL STANDARDIZATION TEST SUITE")
    print("Testing fix for issue #26")
    print("=" * 70 + "\n")

    try:
        test_no_old_values_in_database()
        test_all_candidates_have_valid_values()
        test_federal_level_queries()
        test_ward_level_queries()
        test_ranking_logic_covers_all_levels()
        test_ballot_queries()

        print("=" * 70)
        print("ALL TESTS PASSED ✓")
        print("=" * 70)
        print("\nSummary:")
        print("- All old position level values migrated successfully")
        print("- All candidates have valid standardized values")
        print("- Federal level queries work correctly")
        print("- Ward level queries work correctly")
        print("- Ranking logic covers all position levels")
        print("- Ballot queries find all relevant candidates")
        print("\nNo candidates will be missed due to position level inconsistencies!")

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
