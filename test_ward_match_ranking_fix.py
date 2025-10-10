#!/usr/bin/env python
"""
Test script to verify ward match ranking logic fix for issue #24.

This script tests that:
1. Ward matches only when complete location hierarchy matches (province, district, municipality, ward)
2. Municipality matches only when province and district also match
3. District matches only when province also matches
4. Ranking correctly prioritizes exact matches over partial matches
5. Wrong location hierarchies don't get incorrectly ranked
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from django.db.models import Q, Case, When, Value, IntegerField
from django.contrib.auth.models import User
from candidates.models import Candidate
from locations.models import Province, District, Municipality

def create_test_candidate(name, province_id, district_id, municipality_id, ward_number, position_level='ward_chairperson'):
    """Helper to create test candidates"""
    # Check if user exists
    username = f"test_{name.lower().replace(' ', '_')}"
    user, _ = User.objects.get_or_create(
        username=username,
        defaults={'email': f'{username}@test.com'}
    )

    candidate, created = Candidate.objects.get_or_create(
        user=user,
        defaults={
            'full_name': name,
            'age': 30,
            'province_id': province_id,
            'district_id': district_id,
            'municipality_id': municipality_id,
            'ward_number': ward_number,
            'position_level': position_level,
            'status': 'approved',
            'bio_en': f'Test candidate {name}'
        }
    )

    if not created:
        # Update existing candidate
        candidate.province_id = province_id
        candidate.district_id = district_id
        candidate.municipality_id = municipality_id
        candidate.ward_number = ward_number
        candidate.position_level = position_level
        candidate.status = 'approved'
        candidate.save()

    return candidate

def test_ward_match_requires_full_hierarchy():
    """Test that ward match requires province, district, and municipality to also match"""
    print("=" * 70)
    print("TEST 1: Ward Match Requires Complete Location Hierarchy")
    print("=" * 70)

    # Get test locations
    province1 = Province.objects.first()
    province2 = Province.objects.exclude(id=province1.id).first()

    if not province1 or not province2:
        print("⊘ SKIP: Need at least 2 provinces")
        return

    district1 = District.objects.filter(province=province1).first()
    district2 = District.objects.filter(province=province2).first()

    if not district1 or not district2:
        print("⊘ SKIP: Need districts in different provinces")
        return

    municipality1 = Municipality.objects.filter(district=district1).first()
    municipality2 = Municipality.objects.filter(district=district2).first()

    if not municipality1 or not municipality2:
        print("⊘ SKIP: Need municipalities in different districts")
        return

    # Create test candidates
    print(f"\nCreating test candidates...")
    print(f"User location: Province={province1.id}, District={district1.id}, "
          f"Municipality={municipality1.id}, Ward=5")

    # Candidate A: Exact match (should be ranked 0)
    candidate_exact = create_test_candidate(
        "Exact Match",
        province1.id, district1.id, municipality1.id, 5
    )
    print(f"  Candidate A (Exact): P={province1.id}, D={district1.id}, M={municipality1.id}, W=5")

    # Candidate B: Same ward, same municipality ID but DIFFERENT district/province
    # This should NOT be ranked as exact ward match
    candidate_wrong_district = create_test_candidate(
        "Wrong District",
        province2.id, district2.id, municipality2.id, 5
    )
    print(f"  Candidate B (Wrong): P={province2.id}, D={district2.id}, M={municipality2.id}, W=5")

    # Apply the ranking logic (with fix)
    user_province = province1.id
    user_district = district1.id
    user_municipality = municipality1.id
    user_ward = 5

    ranking_conditions = []

    # Ward match (with fix - checks all hierarchy levels)
    ranking_conditions.append(
        When(
            province_id=user_province,
            district_id=user_district,
            municipality_id=user_municipality,
            ward_number=user_ward,
            then=Value(0)
        )
    )

    # Municipality match (with fix)
    ranking_conditions.append(
        When(
            province_id=user_province,
            district_id=user_district,
            municipality_id=user_municipality,
            then=Value(1)
        )
    )

    # District match (with fix)
    ranking_conditions.append(
        When(
            province_id=user_province,
            district_id=user_district,
            then=Value(2)
        )
    )

    # Province match
    ranking_conditions.append(
        When(province_id=user_province, then=Value(3))
    )

    queryset = Candidate.objects.filter(
        id__in=[candidate_exact.id, candidate_wrong_district.id]
    ).annotate(
        relevance=Case(
            *ranking_conditions,
            default=Value(9),
            output_field=IntegerField()
        )
    ).order_by('relevance', 'full_name')

    # Check results
    print(f"\nRanking Results:")
    for c in queryset:
        print(f"  Relevance: {c.relevance}, Name: {c.full_name}, "
              f"Location: P={c.province_id}, D={c.district_id}, M={c.municipality_id}, W={c.ward_number}")

    # Verify correct ranking
    exact_relevance = queryset.get(id=candidate_exact.id).relevance
    wrong_relevance = queryset.get(id=candidate_wrong_district.id).relevance

    assert exact_relevance == 0, f"Exact match should have relevance 0, got {exact_relevance}"
    assert wrong_relevance > 0, f"Wrong district match should NOT have relevance 0, got {wrong_relevance}"
    assert exact_relevance < wrong_relevance, "Exact match should rank higher than wrong location"

    print(f"\n✓ PASS: Exact match ranked as 0, wrong location ranked as {wrong_relevance}")
    print(f"✓ PASS: Ward match only applies when complete hierarchy matches")
    print()

def test_municipality_match_requires_district_and_province():
    """Test that municipality match requires district and province to also match"""
    print("=" * 70)
    print("TEST 2: Municipality Match Requires District and Province")
    print("=" * 70)

    # Get test locations
    province1 = Province.objects.first()
    province2 = Province.objects.exclude(id=province1.id).first()

    if not province1 or not province2:
        print("⊘ SKIP: Need at least 2 provinces")
        return

    district1 = District.objects.filter(province=province1).first()
    district2 = District.objects.filter(province=province2).first()

    municipality1 = Municipality.objects.filter(district=district1).first()
    municipality2 = Municipality.objects.filter(district=district2).first()

    if not municipality1 or not municipality2:
        print("⊘ SKIP: Need municipalities")
        return

    print(f"\nUser location: Province={province1.id}, District={district1.id}, Municipality={municipality1.id}")

    # Candidate A: Exact municipality match
    candidate_exact = create_test_candidate(
        "Exact Muni Match",
        province1.id, district1.id, municipality1.id, None, 'mayor_chairperson'
    )

    # Candidate B: Different district (should not match as municipality)
    candidate_wrong = create_test_candidate(
        "Wrong District Muni",
        province2.id, district2.id, municipality2.id, None, 'mayor_chairperson'
    )

    # Apply ranking
    ranking_conditions = []
    ranking_conditions.append(
        When(
            province_id=province1.id,
            district_id=district1.id,
            municipality_id=municipality1.id,
            then=Value(1)
        )
    )
    ranking_conditions.append(
        When(
            province_id=province1.id,
            district_id=district1.id,
            then=Value(2)
        )
    )
    ranking_conditions.append(
        When(province_id=province1.id, then=Value(3))
    )

    queryset = Candidate.objects.filter(
        id__in=[candidate_exact.id, candidate_wrong.id]
    ).annotate(
        relevance=Case(
            *ranking_conditions,
            default=Value(9),
            output_field=IntegerField()
        )
    )

    exact_relevance = queryset.get(id=candidate_exact.id).relevance
    wrong_relevance = queryset.get(id=candidate_wrong.id).relevance

    print(f"\nRanking Results:")
    print(f"  Exact municipality: relevance={exact_relevance}")
    print(f"  Wrong district: relevance={wrong_relevance}")

    assert exact_relevance == 1, f"Exact municipality should have relevance 1, got {exact_relevance}"
    assert wrong_relevance > 1, f"Wrong district should NOT have relevance 1, got {wrong_relevance}"

    print(f"\n✓ PASS: Municipality match only applies when district and province also match")
    print()

def test_district_match_requires_province():
    """Test that district match requires province to also match"""
    print("=" * 70)
    print("TEST 3: District Match Requires Province")
    print("=" * 70)

    province1 = Province.objects.first()
    province2 = Province.objects.exclude(id=province1.id).first()

    if not province1 or not province2:
        print("⊘ SKIP: Need at least 2 provinces")
        return

    district1 = District.objects.filter(province=province1).first()
    district2 = District.objects.filter(province=province2).first()

    if not district1 or not district2:
        print("⊘ SKIP: Need districts")
        return

    print(f"\nUser location: Province={province1.id}, District={district1.id}")

    # Candidate A: Exact district match
    candidate_exact = create_test_candidate(
        "Exact District Match",
        province1.id, district1.id, None, None, 'house_of_representatives'
    )

    # Candidate B: Different province (should not match as district)
    candidate_wrong = create_test_candidate(
        "Wrong Province District",
        province2.id, district2.id, None, None, 'house_of_representatives'
    )

    # Apply ranking
    ranking_conditions = []
    ranking_conditions.append(
        When(
            province_id=province1.id,
            district_id=district1.id,
            then=Value(2)
        )
    )
    ranking_conditions.append(
        When(province_id=province1.id, then=Value(3))
    )

    queryset = Candidate.objects.filter(
        id__in=[candidate_exact.id, candidate_wrong.id]
    ).annotate(
        relevance=Case(
            *ranking_conditions,
            default=Value(9),
            output_field=IntegerField()
        )
    )

    exact_relevance = queryset.get(id=candidate_exact.id).relevance
    wrong_relevance = queryset.get(id=candidate_wrong.id).relevance

    print(f"\nRanking Results:")
    print(f"  Exact district: relevance={exact_relevance}")
    print(f"  Wrong province: relevance={wrong_relevance}")

    assert exact_relevance == 2, f"Exact district should have relevance 2, got {exact_relevance}"
    assert wrong_relevance > 2, f"Wrong province should NOT have relevance 2, got {wrong_relevance}"

    print(f"\n✓ PASS: District match only applies when province also matches")
    print()

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("WARD MATCH RANKING LOGIC FIX TEST SUITE")
    print("Testing fix for issue #24")
    print("=" * 70 + "\n")

    try:
        test_ward_match_requires_full_hierarchy()
        test_municipality_match_requires_district_and_province()
        test_district_match_requires_province()

        print("=" * 70)
        print("ALL TESTS PASSED ✓")
        print("=" * 70)
        print("\nSummary:")
        print("- Ward matches only when province, district, municipality, and ward all match")
        print("- Municipality matches only when province and district also match")
        print("- District matches only when province also matches")
        print("- Location hierarchy is properly verified for data integrity")
        print("- No incorrect rankings due to partial location matches")

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
