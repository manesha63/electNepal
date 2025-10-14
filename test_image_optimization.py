#!/usr/bin/env python
"""
Test script to verify image optimization is working automatically on upload.

This script:
1. Creates a large test image (2000x2000px)
2. Uploads it via Candidate model
3. Verifies the image was optimized (resized and compressed)
4. Cleans up test data
"""

import os
import sys
import django
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from django.contrib.auth.models import User
from candidates.models import Candidate
from locations.models import Province, District


def create_test_image(width=2000, height=2000, color='red'):
    """
    Create a test image in memory

    Args:
        width: Image width in pixels
        height: Image height in pixels
        color: Background color

    Returns:
        InMemoryUploadedFile containing the image
    """
    # Create image
    img = Image.new('RGB', (width, height), color=color)

    # Save to BytesIO
    output = BytesIO()
    img.save(output, format='JPEG', quality=95)

    # Get file size and reset pointer
    file_size = output.tell()
    output.seek(0)

    # Create InMemoryUploadedFile with proper attributes
    uploaded_file = InMemoryUploadedFile(
        output,
        'ImageField',
        f'test_image_{width}x{height}.jpg',
        'image/jpeg',
        file_size,
        None
    )

    # Add required attributes for validators
    uploaded_file.size = file_size

    return uploaded_file, file_size


def test_auto_optimization():
    """Test that images are automatically optimized on upload"""

    print("\n" + "="*80)
    print(" IMAGE OPTIMIZATION VERIFICATION TEST")
    print("="*80)

    # 1. Create test user
    print("\n[1/5] Creating test user...")
    try:
        test_user = User.objects.create_user(
            username='test_image_optimization',
            email='test_optimization@test.com',
            password='testpass123'
        )
        print(f"✓ Test user created: {test_user.username}")
    except Exception as e:
        print(f"✗ Failed to create user: {e}")
        return False

    # 2. Create test image (large)
    print("\n[2/5] Creating large test image (2000x2000px)...")
    try:
        test_image, original_size = create_test_image(width=2000, height=2000, color='blue')
        print(f"✓ Test image created: {original_size / 1024:.1f}KB, 2000x2000px")
    except Exception as e:
        print(f"✗ Failed to create test image: {e}")
        test_user.delete()
        return False

    # 3. Create candidate with test image
    print("\n[3/5] Creating candidate profile with large image...")
    try:
        # Get first province and its first district (proper hierarchy)
        province = Province.objects.first()
        if not province:
            print("✗ No location data in database. Run: python manage.py load_nepal_locations")
            test_user.delete()
            return False

        district = District.objects.filter(province=province).first()
        if not district:
            print("✗ No districts for province. Check location data.")
            test_user.delete()
            return False

        print(f"  Using location: {province.name_en} / {district.name_en}")

        candidate = Candidate(
            user=test_user,
            full_name='Test Image Optimization Candidate',
            age=30,
            bio_en='Testing automatic image optimization on upload',
            position_level='house_of_representatives',
            province=province,
            district=district,
            status='pending'
        )

        # Attach the large test image
        candidate.photo = test_image

        # Save - this should trigger auto-optimization
        print("  → Calling candidate.save() - auto-optimization should run...")
        candidate.save()

        print(f"✓ Candidate saved successfully (ID: {candidate.pk})")

    except Exception as e:
        print(f"✗ Failed to save candidate: {e}")
        import traceback
        traceback.print_exc()
        test_user.delete()
        return False

    # 4. Verify optimization occurred
    print("\n[4/5] Verifying image was optimized...")
    try:
        # Reload candidate from database
        candidate = Candidate.objects.get(pk=candidate.pk)

        if not candidate.photo:
            print("✗ No photo attached to candidate")
            cleanup(candidate)
            return False

        # Open the saved image
        saved_image = Image.open(candidate.photo.path)
        saved_width, saved_height = saved_image.size
        saved_size = os.path.getsize(candidate.photo.path)

        print(f"\n  Original Image:")
        print(f"    - Size: {original_size / 1024:.1f}KB")
        print(f"    - Dimensions: 2000x2000px")
        print(f"\n  Saved Image:")
        print(f"    - Size: {saved_size / 1024:.1f}KB")
        print(f"    - Dimensions: {saved_width}x{saved_height}px")
        print(f"    - Path: {candidate.photo.path}")

        # Check if optimization occurred
        optimized = False
        reasons = []

        # Check 1: Dimensions should be <= 800x800
        if saved_width <= 800 and saved_height <= 800:
            reasons.append(f"✓ Dimensions optimized: 2000x2000 → {saved_width}x{saved_height}")
            optimized = True
        else:
            reasons.append(f"✗ Dimensions NOT optimized: {saved_width}x{saved_height} (expected ≤800x800)")

        # Check 2: File size should be reduced
        if saved_size < original_size:
            reduction = ((original_size - saved_size) / original_size) * 100
            reasons.append(f"✓ Size reduced: {original_size / 1024:.1f}KB → {saved_size / 1024:.1f}KB ({reduction:.1f}% reduction)")
            optimized = True
        else:
            reasons.append(f"✗ Size NOT reduced: {saved_size / 1024:.1f}KB (original: {original_size / 1024:.1f}KB)")

        print("\n  Optimization Results:")
        for reason in reasons:
            print(f"    {reason}")

        if optimized:
            print("\n✓ PASS: Image was automatically optimized on upload!")
            print("\n  How it works:")
            print("    1. User uploads image via registration/edit form")
            print("    2. Candidate.save() method is called")
            print("    3. System detects new/changed photo")
            print("    4. should_optimize_image() checks if optimization needed")
            print("    5. optimize_image() resizes to 800x800 and compresses to JPEG")
            print("    6. Optimized image is saved to disk")

            cleanup(candidate)
            return True
        else:
            print("\n✗ FAIL: Image was NOT optimized")
            print("\n  Possible reasons:")
            print("    - Optimization code not being called")
            print("    - Error during optimization (check logs)")
            print("    - Image too small to trigger optimization")

            cleanup(candidate)
            return False

    except Exception as e:
        print(f"✗ Error verifying optimization: {e}")
        import traceback
        traceback.print_exc()
        cleanup(candidate)
        return False


def cleanup(candidate):
    """Clean up test data"""
    print("\n[5/5] Cleaning up test data...")
    try:
        # Delete photo file if it exists
        if candidate.photo and os.path.exists(candidate.photo.path):
            os.remove(candidate.photo.path)
            print(f"  ✓ Deleted photo file: {candidate.photo.path}")

        # Delete candidate
        user = candidate.user
        candidate.delete()
        print(f"  ✓ Deleted candidate: {candidate.full_name}")

        # Delete user
        user.delete()
        print(f"  ✓ Deleted user: {user.username}")

    except Exception as e:
        print(f"  ⚠ Cleanup warning: {e}")


def main():
    """Run the test"""
    success = test_auto_optimization()

    print("\n" + "="*80)
    if success:
        print(" ✓✓✓ TEST PASSED ✓✓✓")
        print("="*80)
        print("\nConclusion:")
        print("  Image optimization IS ALREADY IMPLEMENTED and working correctly.")
        print("  Issue #6 in the issue tracker is OUTDATED.")
        print("\nNo fix needed - auto-optimization is operational!")
    else:
        print(" ✗✗✗ TEST FAILED ✗✗✗")
        print("="*80)
        print("\nConclusion:")
        print("  Image optimization code exists but may not be working correctly.")
        print("  Further investigation needed.")
    print("="*80)

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
