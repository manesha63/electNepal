#!/usr/bin/env python
"""
Test script to verify location hierarchy validation fix in candidates/models.py
Tests that invalid foreign key relationships are prevented at save() level
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from candidates.models import Candidate
from locations.models import Province, District, Municipality


def test_valid_location_hierarchy():
    """Test 1: Valid location hierarchy should work"""
    print("\n" + "="*70)
    print("TEST 1: Valid Location Hierarchy")
    print("="*70)
    print("Testing that valid province → district → municipality works correctly")

    # Clean up test user
    User.objects.filter(username='hiertest001').delete()
    user = User.objects.create_user('hiertest001', 'test@test.com', 'pass')

    # Get a valid location hierarchy
    province = Province.objects.first()
    district = District.objects.filter(province=province).first()
    municipality = Municipality.objects.filter(district=district).first()

    print(f"\nValid hierarchy:")
    print(f"  Province: {province.name_en} (ID: {province.id})")
    print(f"  District: {district.name_en} (ID: {district.id})")
    print(f"  Municipality: {municipality.name_en} (ID: {municipality.id})")

    try:
        candidate = Candidate.objects.create(
            user=user,
            full_name="Valid Hierarchy Test",
            age=30,
            position_level='mayor_chairperson',
            province=province,
            district=district,
            municipality=municipality,
            bio_en="Test bio",
            status='pending'
        )
        print("\n✓ PASS: Valid location hierarchy accepted")
        candidate.delete()
        User.objects.filter(username='hiertest001').delete()
        return True
    except ValidationError as e:
        print(f"\n✗ FAIL: Valid hierarchy rejected: {e}")
        User.objects.filter(username='hiertest001').delete()
        return False
    except Exception as e:
        print(f"\n✗ FAIL: Unexpected error: {e}")
        User.objects.filter(username='hiertest001').delete()
        return False


def test_invalid_district_province():
    """Test 2: Invalid district-province relationship should be rejected"""
    print("\n" + "="*70)
    print("TEST 2: Invalid District-Province Relationship")
    print("="*70)
    print("Testing that district not in selected province is rejected")

    # Clean up test user
    User.objects.filter(username='hiertest002').delete()
    user = User.objects.create_user('hiertest002', 'test@test.com', 'pass')

    # Get provinces and find a district from different province
    province1 = Province.objects.first()
    province2 = Province.objects.exclude(id=province1.id).first()
    district_from_province2 = District.objects.filter(province=province2).first()

    print(f"\nInvalid hierarchy (district from wrong province):")
    print(f"  Province: {province1.name_en} (ID: {province1.id})")
    print(f"  District: {district_from_province2.name_en} (ID: {district_from_province2.id})")
    print(f"  District actually belongs to: {province2.name_en} ❌")

    try:
        candidate = Candidate.objects.create(
            user=user,
            full_name="Invalid District Test",
            age=30,
            position_level='provincial_assembly',  # Provincial position (doesn't require municipality)
            province=province1,  # Province 1
            district=district_from_province2,  # District from Province 2 ❌
            municipality=None,
            bio_en="Test bio",
            status='pending'
        )
        print(f"\n✗ FAIL: Invalid district-province accepted (candidate ID: {candidate.id})")
        candidate.delete()
        User.objects.filter(username='hiertest002').delete()
        return False
    except ValidationError as e:
        if 'District must belong to the selected province' in str(e):
            print(f"\n✓ PASS: Invalid district-province correctly rejected")
            print(f"  Error message: {e}")
            User.objects.filter(username='hiertest002').delete()
            return True
        else:
            print(f"\n✗ FAIL: Wrong validation error: {e}")
            User.objects.filter(username='hiertest002').delete()
            return False
    except Exception as e:
        print(f"\n✗ FAIL: Unexpected error: {e}")
        User.objects.filter(username='hiertest002').delete()
        return False


def test_invalid_municipality_district():
    """Test 3: Invalid municipality-district relationship should be rejected"""
    print("\n" + "="*70)
    print("TEST 3: Invalid Municipality-District Relationship")
    print("="*70)
    print("Testing that municipality not in selected district is rejected")

    # Clean up test user
    User.objects.filter(username='hiertest003').delete()
    user = User.objects.create_user('hiertest003', 'test@test.com', 'pass')

    # Get a valid province and district
    province = Province.objects.first()
    district1 = District.objects.filter(province=province).first()
    district2 = District.objects.filter(province=province).exclude(id=district1.id).first()

    # Get municipality from district2
    municipality_from_district2 = Municipality.objects.filter(district=district2).first()

    print(f"\nInvalid hierarchy (municipality from wrong district):")
    print(f"  Province: {province.name_en} (ID: {province.id})")
    print(f"  District: {district1.name_en} (ID: {district1.id})")
    print(f"  Municipality: {municipality_from_district2.name_en} (ID: {municipality_from_district2.id})")
    print(f"  Municipality actually belongs to: {district2.name_en} ❌")

    try:
        candidate = Candidate.objects.create(
            user=user,
            full_name="Invalid Municipality Test",
            age=30,
            position_level='mayor_chairperson',
            province=province,
            district=district1,  # District 1
            municipality=municipality_from_district2,  # Municipality from District 2 ❌
            bio_en="Test bio",
            status='pending'
        )
        print(f"\n✗ FAIL: Invalid municipality-district accepted (candidate ID: {candidate.id})")
        candidate.delete()
        User.objects.filter(username='hiertest003').delete()
        return False
    except ValidationError as e:
        if 'Municipality must belong to the selected district' in str(e):
            print(f"\n✓ PASS: Invalid municipality-district correctly rejected")
            print(f"  Error message: {e}")
            User.objects.filter(username='hiertest003').delete()
            return True
        else:
            print(f"\n✗ FAIL: Wrong validation error: {e}")
            User.objects.filter(username='hiertest003').delete()
            return False
    except Exception as e:
        print(f"\n✗ FAIL: Unexpected error: {e}")
        User.objects.filter(username='hiertest003').delete()
        return False


def test_direct_save_bypass():
    """Test 4: Direct .save() should also enforce validation"""
    print("\n" + "="*70)
    print("TEST 4: Direct save() Also Enforces Validation")
    print("="*70)
    print("Testing that manually creating and saving also validates")

    # Clean up test user
    User.objects.filter(username='hiertest004').delete()
    user = User.objects.create_user('hiertest004', 'test@test.com', 'pass')

    # Get provinces and invalid district
    province1 = Province.objects.first()
    province2 = Province.objects.exclude(id=province1.id).first()
    district_from_province2 = District.objects.filter(province=province2).first()

    print(f"\nTrying direct instantiation + save() with invalid hierarchy:")
    print(f"  Province: {province1.name_en}")
    print(f"  District: {district_from_province2.name_en} (from {province2.name_en}) ❌")

    try:
        candidate = Candidate(
            user=user,
            full_name="Direct Save Test",
            age=30,
            position_level='provincial_assembly',  # Provincial position (doesn't require municipality)
            province=province1,
            district=district_from_province2,
            bio_en="Test bio",
            status='pending'
        )
        candidate.save()  # This should trigger full_clean()
        print(f"\n✗ FAIL: Invalid hierarchy accepted via save() (candidate ID: {candidate.id})")
        candidate.delete()
        User.objects.filter(username='hiertest004').delete()
        return False
    except ValidationError as e:
        print(f"\n✓ PASS: Invalid hierarchy correctly rejected via save()")
        print(f"  Error message: {e}")
        User.objects.filter(username='hiertest004').delete()
        return True
    except Exception as e:
        print(f"\n✗ FAIL: Unexpected error: {e}")
        User.objects.filter(username='hiertest004').delete()
        return False


def test_skip_validation_flag():
    """Test 5: skip_validation=True should bypass validation (for migrations)"""
    print("\n" + "="*70)
    print("TEST 5: skip_validation=True Flag")
    print("="*70)
    print("Testing that save(skip_validation=True) bypasses validation")

    # Clean up test user
    User.objects.filter(username='hiertest005').delete()
    user = User.objects.create_user('hiertest005', 'test@test.com', 'pass')

    # Get provinces and invalid district
    province1 = Province.objects.first()
    province2 = Province.objects.exclude(id=province1.id).first()
    district_from_province2 = District.objects.filter(province=province2).first()

    print(f"\nTrying save(skip_validation=True) with invalid hierarchy:")
    print(f"  Province: {province1.name_en}")
    print(f"  District: {district_from_province2.name_en} (from {province2.name_en}) ❌")

    try:
        candidate = Candidate(
            user=user,
            full_name="Skip Validation Test",
            age=30,
            position_level='provincial_assembly',  # Provincial position (doesn't require municipality)
            province=province1,
            district=district_from_province2,
            bio_en="Test bio",
            status='pending'
        )
        candidate.save(skip_validation=True)  # Should NOT validate
        print(f"\n✓ PASS: skip_validation=True bypassed validation (candidate ID: {candidate.id})")
        candidate.delete()
        User.objects.filter(username='hiertest005').delete()
        return True
    except ValidationError as e:
        print(f"\n✗ FAIL: skip_validation=True did not bypass validation: {e}")
        User.objects.filter(username='hiertest005').delete()
        return False
    except Exception as e:
        print(f"\n✗ FAIL: Unexpected error: {e}")
        User.objects.filter(username='hiertest005').delete()
        return False


def test_existing_candidates_still_work():
    """Test 6: Existing candidates should still be saveable"""
    print("\n" + "="*70)
    print("TEST 6: Existing Candidates Can Be Updated")
    print("="*70)
    print("Testing that existing valid candidates can still be saved")

    existing = Candidate.objects.filter(status='approved').first()
    if not existing:
        print("\n⚠ SKIP: No existing approved candidates found")
        return True

    print(f"\nTesting update of existing candidate: {existing.full_name}")
    print(f"  Location: {existing.municipality.name_en if existing.municipality else 'N/A'}")

    original_bio = existing.bio_en
    try:
        existing.bio_en = "Updated bio for testing"
        existing.save()
        print(f"\n✓ PASS: Existing candidate updated successfully")

        # Restore original bio
        existing.bio_en = original_bio
        existing.save()
        return True
    except Exception as e:
        print(f"\n✗ FAIL: Could not update existing candidate: {e}")
        # Try to restore
        try:
            existing.bio_en = original_bio
            existing.save(skip_validation=True)
        except:
            pass
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print(" LOCATION HIERARCHY VALIDATION FIX VERIFICATION TEST SUITE")
    print("="*80)
    print("\nThis test suite verifies:")
    print("1. Valid location hierarchies are accepted")
    print("2. Invalid district-province relationships are rejected")
    print("3. Invalid municipality-district relationships are rejected")
    print("4. Direct .save() calls also enforce validation")
    print("5. skip_validation=True flag works for migrations")
    print("6. Existing candidates can still be updated")
    print("\nRunning tests...\n")

    results = {}

    try:
        results['test1'] = test_valid_location_hierarchy()
        results['test2'] = test_invalid_district_province()
        results['test3'] = test_invalid_municipality_district()
        results['test4'] = test_direct_save_bypass()
        results['test5'] = test_skip_validation_flag()
        results['test6'] = test_existing_candidates_still_work()

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
        'test1': 'Valid Location Hierarchy',
        'test2': 'Invalid District-Province (Rejected)',
        'test3': 'Invalid Municipality-District (Rejected)',
        'test4': 'Direct save() Enforces Validation',
        'test5': 'skip_validation=True Flag Works',
        'test6': 'Existing Candidates Can Be Updated',
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
        print("\nThe location hierarchy validation fix is working correctly:")
        print("  ✓ save() method enforces full_clean() validation")
        print("  ✓ Invalid foreign key relationships rejected")
        print("  ✓ Direct database bypasses prevented")
        print("  ✓ Existing candidates not affected")
        print("  ✓ Migration escape hatch available (skip_validation=True)")
        print("\nFixed code (candidates/models.py:416-422):")
        print("  def save(self, *args, **kwargs):")
        print("      if not kwargs.pop('skip_validation', False):")
        print("          self.full_clean()")
        return True
    else:
        print("\n✗✗✗ SOME TESTS FAILED ✗✗✗")
        print("\nPlease review the failed tests above.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
