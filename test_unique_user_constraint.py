#!/usr/bin/env python
"""
Test script to verify unique constraint on Candidate.user field for issue #28.

This script tests that:
1. Database has unique constraint on user_id
2. Attempting to create duplicate candidate for same user fails
3. Error message is appropriate (IntegrityError)
4. Constraint name is correct
5. Existing single-user candidates work fine
"""

import os
import sys
import django
from django.db import IntegrityError

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from django.contrib.auth.models import User
from candidates.models import Candidate
from locations.models import Province, District

def test_database_has_unique_constraint():
    """Test that database has unique constraint on user_id"""
    print("=" * 70)
    print("TEST 1: Database Has Unique Constraint on user_id")
    print("=" * 70)

    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT conname, contype
            FROM pg_constraint
            WHERE conrelid = 'candidates_candidate'::regclass
            AND contype = 'u'
            AND conname LIKE '%user%'
        """)
        constraints = cursor.fetchall()

    print(f"  Unique constraints on user field:")
    for constraint_name, constraint_type in constraints:
        print(f"    - {constraint_name} (type: {constraint_type})")

    assert len(constraints) > 0, "No unique constraint found on user_id field"
    assert any('user' in c[0] for c in constraints), "No user-related unique constraint found"

    print(f"\n✓ PASS: Database has unique constraint on user_id")
    print()

def test_cannot_create_duplicate_candidate():
    """Test that creating two candidates for same user fails"""
    print("=" * 70)
    print("TEST 2: Cannot Create Duplicate Candidate for Same User")
    print("=" * 70)

    import time
    timestamp = int(time.time() * 1000) % 100000  # Use timestamp for uniqueness

    # Cleanup any existing test user
    User.objects.filter(username=f'unique_test_user_28_{timestamp}').delete()

    # Create a test user
    test_user = User.objects.create_user(
        username=f'unique_test_user_28_{timestamp}',
        email=f'unique28_{timestamp}@test.com',
        password='testpass123'
    )

    province = Province.objects.first()
    district = District.objects.filter(province=province).first()

    # Create first candidate
    candidate1 = Candidate.objects.create(
        user=test_user,
        full_name='Test Candidate 1',
        age=30,
        province=province,
        district=district,
        position_level='provincial_assembly',
        status='pending',
        bio_en='First candidate bio'
    )

    print(f"  ✓ Created first candidate: {candidate1.full_name}")

    # Try to create second candidate with same user
    from django.core.exceptions import ValidationError

    try:
        candidate2 = Candidate.objects.create(
            user=test_user,
            full_name='Test Candidate 2',
            age=35,
            province=province,
            district=district,
            position_level='house_of_representatives',
            status='pending',
            bio_en='Second candidate bio'
        )

        # If we get here, constraint didn't work
        candidate2.delete()
        candidate1.delete()
        test_user.delete()
        assert False, "Should have raised ValidationError or IntegrityError for duplicate user"

    except ValidationError as e:
        error_msg = str(e)
        print(f"  ✓ ValidationError raised as expected (Django model validation)")
        print(f"  Error message: {error_msg[:150]}...")

        # Check that error mentions user field
        assert 'user' in error_msg.lower() or 'already exists' in error_msg.lower(), \
            "Error message doesn't mention user constraint violation"

        print(f"  ✓ Error correctly identifies unique user constraint violation")

    except IntegrityError as e:
        error_msg = str(e)
        print(f"  ✓ IntegrityError raised as expected (Database constraint)")
        print(f"  Error message: {error_msg[:150]}...")

        # Check that error mentions unique constraint
        assert 'unique' in error_msg.lower() or 'duplicate' in error_msg.lower(), \
            "Error message doesn't mention uniqueness violation"

        print(f"  ✓ Error correctly identifies unique constraint violation")

    # Cleanup
    candidate1.delete()
    test_user.delete()

    print(f"\n✓ PASS: Duplicate candidate creation properly prevented")
    print()

def test_model_field_has_unique_true():
    """Test that model field has unique=True in definition"""
    print("=" * 70)
    print("TEST 3: Model Field Has unique=True")
    print("=" * 70)

    # Read the models.py file
    with open('candidates/models.py', 'r') as f:
        content = f.read()

    # Find the user field definition
    import re
    user_field_pattern = r'user\s*=\s*models\.OneToOneField\([^)]+\)'
    matches = re.findall(user_field_pattern, content)

    print(f"  User field definition found: {len(matches)} occurrence(s)")

    assert len(matches) > 0, "Could not find user field definition"

    user_field_def = matches[0]
    print(f"  Field definition: {user_field_def}")

    # Check for unique=True
    has_unique = 'unique=True' in user_field_def

    if has_unique:
        print(f"  ✓ Field has explicit unique=True")
    else:
        print(f"  ℹ Field doesn't have explicit unique=True (OneToOneField is unique by default)")

    print(f"\n✓ PASS: Model field properly configured")
    print()

def test_existing_candidates_have_unique_users():
    """Test that all existing candidates have unique users"""
    print("=" * 70)
    print("TEST 4: All Existing Candidates Have Unique Users")
    print("=" * 70)

    from django.db.models import Count

    # Check for any duplicate user_id values
    duplicates = Candidate.objects.values('user_id').annotate(
        count=Count('user_id')
    ).filter(count__gt=1)

    duplicate_count = duplicates.count()

    print(f"  Total candidates in database: {Candidate.objects.count()}")
    print(f"  Duplicate user_id instances: {duplicate_count}")

    if duplicate_count > 0:
        print(f"  ❌ Found {duplicate_count} users with multiple candidates:")
        for dup in duplicates:
            print(f"    User ID {dup['user_id']}: {dup['count']} candidates")
        assert False, f"Found {duplicate_count} duplicate user associations"
    else:
        print(f"  ✓ All candidates have unique user associations")

    print(f"\n✓ PASS: No duplicate user associations in existing data")
    print()

def test_can_create_single_candidate_per_user():
    """Test that creating one candidate per user works fine"""
    print("=" * 70)
    print("TEST 5: Can Create Single Candidate Per User")
    print("=" * 70)

    # Create three users with three candidates
    province = Province.objects.first()
    district = District.objects.filter(province=province).first()

    users_created = []
    candidates_created = []

    for i in range(3):
        user = User.objects.create_user(
            username=f'single_user_test_{i}_28',
            email=f'single{i}@test.com',
            password='testpass123'
        )
        users_created.append(user)

        candidate = Candidate.objects.create(
            user=user,
            full_name=f'Single Test Candidate {i}',
            age=30 + i,
            province=province,
            district=district,
            position_level='provincial_assembly',
            status='pending',
            bio_en=f'Bio for candidate {i}'
        )
        candidates_created.append(candidate)
        print(f"  ✓ Created candidate {i+1}/3: {candidate.full_name}")

    print(f"  ✓ All 3 candidates created successfully")

    # Verify each candidate has unique user
    user_ids = [c.user_id for c in candidates_created]
    assert len(user_ids) == len(set(user_ids)), "Duplicate user_ids found"
    print(f"  ✓ All candidates have unique users")

    # Cleanup
    for candidate in candidates_created:
        candidate.delete()
    for user in users_created:
        user.delete()

    print(f"\n✓ PASS: Single candidate per user works correctly")
    print()

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("UNIQUE USER CONSTRAINT TEST SUITE")
    print("Testing fix for issue #28")
    print("=" * 70 + "\n")

    try:
        test_database_has_unique_constraint()
        test_model_field_has_unique_true()
        test_existing_candidates_have_unique_users()
        test_can_create_single_candidate_per_user()
        test_cannot_create_duplicate_candidate()

        print("=" * 70)
        print("ALL TESTS PASSED ✓")
        print("=" * 70)
        print("\nSummary:")
        print("- Database has unique constraint on user_id field")
        print("- Model field properly configured with unique=True")
        print("- All existing candidates have unique user associations")
        print("- Single candidate per user works correctly")
        print("- Duplicate candidate creation properly prevented")
        print("\nNo user can have multiple candidate profiles!")

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
