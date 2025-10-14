#!/usr/bin/env python
"""
Simple test to verify image optimization works on upload.
Uses a real image file from disk to avoid validator issues.
"""

import os
import sys
import django
from django.core.files import File

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from PIL import Image
from django.contrib.auth.models import User
from candidates.models import Candidate
from locations.models import Province, District


def create_temp_image():
    """Create a large temporary image file"""
    from PIL import Image
    img = Image.new('RGB', (2000, 2000), color='blue')
    test_path = '/tmp/test_optimization_2000x2000.jpg'
    img.save(test_path, 'JPEG', quality=95)
    return test_path


def test_optimization():
    print("\n" + "="*80)
    print(" IMAGE OPTIMIZATION TEST")
    print("="*80)

    # Step 1: Create test image
    print("\n[1/6] Creating 2000x2000px test image...")
    test_image_path = create_temp_image()
    original_size = os.path.getsize(test_image_path)
    print(f"✓ Test image: {test_image_path}")
    print(f"  Size: {original_size / 1024:.1f}KB, Dimensions: 2000x2000px")

    # Step 2: Create test user
    print("\n[2/6] Creating test user...")
    test_user = User.objects.create_user(
        username='test_img_opt',
        email='test@test.com',
        password='pass123'
    )
    print(f"✓ User: {test_user.username}")

    # Step 3: Get location data
    print("\n[3/6] Getting location data...")
    province = Province.objects.first()
    district = District.objects.filter(province=province).first()
    print(f"✓ Location: {province.name_en} / {district.name_en}")

    # Step 4: Create candidate with large image
    print("\n[4/6] Creating candidate with large image...")
    candidate = Candidate(
        user=test_user,
        full_name='Image Optimization Test',
        age=30,
        bio_en='Testing image optimization',
        position_level='provincial_assembly',
        province=province,
        district=district,
        status='pending'
    )

    # Open and attach the image
    with open(test_image_path, 'rb') as f:
        candidate.photo.save('test_image.jpg', File(f), save=False)

    print("  Saving candidate (optimization should run)...")
    candidate.save()
    print(f"✓ Candidate saved (ID: {candidate.pk})")

    # Step 5: Verify optimization
    print("\n[5/6] Verifying optimization...")
    candidate.refresh_from_db()

    if not candidate.photo:
        print("✗ No photo saved")
        cleanup(candidate, test_image_path)
        return False

    saved_path = candidate.photo.path
    saved_size = os.path.getsize(saved_path)
    saved_img = Image.open(saved_path)
    saved_width, saved_height = saved_img.size

    print(f"\n  ORIGINAL IMAGE:")
    print(f"    Size: {original_size / 1024:.1f}KB")
    print(f"    Dimensions: 2000x2000px")
    print(f"\n  SAVED IMAGE:")
    print(f"    Path: {saved_path}")
    print(f"    Size: {saved_size / 1024:.1f}KB")
    print(f"    Dimensions: {saved_width}x{saved_height}px")

    # Check optimization
    checks = []
    if saved_width <= 800 and saved_height <= 800:
        checks.append(("Dimensions", True, f"2000x2000 → {saved_width}x{saved_height}"))
    else:
        checks.append(("Dimensions", False, f"{saved_width}x{saved_height} (expected ≤800x800)"))

    if saved_size < original_size:
        reduction = ((original_size - saved_size) / original_size) * 100
        checks.append(("Size", True, f"{original_size / 1024:.1f}KB → {saved_size / 1024:.1f}KB ({reduction:.1f}% reduction)"))
    else:
        checks.append(("Size", False, f"Not reduced"))

    print(f"\n  OPTIMIZATION RESULTS:")
    all_passed = True
    for name, passed, detail in checks:
        status = "✓" if passed else "✗"
        print(f"    {status} {name}: {detail}")
        if not passed:
            all_passed = False

    # Step 6: Cleanup
    print("\n[6/6] Cleaning up...")
    cleanup(candidate, test_image_path)

    return all_passed


def cleanup(candidate, test_image_path):
    """Clean up test data"""
    try:
        # Delete saved photo
        if candidate.photo and os.path.exists(candidate.photo.path):
            os.remove(candidate.photo.path)
            print(f"  ✓ Deleted: {candidate.photo.path}")

        # Delete candidate and user
        user = candidate.user
        candidate.delete()
        user.delete()
        print(f"  ✓ Deleted candidate and user")

        # Delete temp file
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
            print(f"  ✓ Deleted: {test_image_path}")

    except Exception as e:
        print(f"  ⚠ Cleanup error: {e}")


if __name__ == '__main__':
    success = test_optimization()

    print("\n" + "="*80)
    if success:
        print(" ✓✓✓ TEST PASSED ✓✓✓")
        print("="*80)
        print("\nConclusion: Image optimization IS WORKING automatically on upload!")
        print("\nIssue #6 status: ✅ ALREADY IMPLEMENTED (issue tracker is outdated)")
    else:
        print(" ✗✗✗ TEST FAILED ✗✗✗")
        print("="*80)
        print("\nConclusion: Optimization code exists but may not be working")
    print("="*80)

    sys.exit(0 if success else 1)
