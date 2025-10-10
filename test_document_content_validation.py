#!/usr/bin/env python
"""
Test script to verify document content-type validation for issue #30.

This script tests that:
1. Validator checks actual file content, not just extension
2. Legitimate PDFs pass validation
3. Fake PDFs (renamed executables) fail validation
4. Legitimate images pass validation
5. Fake images (renamed files) fail validation
6. Content mismatch detection works (e.g., PNG renamed to JPG)
"""

import os
import sys
import django
from io import BytesIO

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from candidates.validators import validate_file_content_type


def test_validator_exists():
    """Test that content-type validator exists"""
    print("=" * 70)
    print("TEST 1: Content-Type Validator Exists")
    print("=" * 70)

    # Check validator is imported
    from candidates import validators

    has_validator = hasattr(validators, 'validate_file_content_type')
    print(f"  validate_file_content_type exists: {has_validator}")

    assert has_validator, "validate_file_content_type not found in validators module"

    # Check validator is callable
    is_callable = callable(validators.validate_file_content_type)
    print(f"  Validator is callable: {is_callable}")

    assert is_callable, "validate_file_content_type is not callable"

    print(f"\n✓ PASS: Content-type validator exists and is callable")
    print()


def test_legitimate_pdf_passes():
    """Test that legitimate PDF files pass validation"""
    print("=" * 70)
    print("TEST 2: Legitimate PDF Passes Validation")
    print("=" * 70)

    # Create a minimal valid PDF file (PDF magic bytes + basic structure)
    pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/Resources <<\n/Font <<\n/F1 <<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Times-Roman\n>>\n>>\n>>\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n264\n%%EOF'

    # Create uploaded file with .pdf extension
    pdf_file = SimpleUploadedFile("test_document.pdf", pdf_content, content_type="application/pdf")

    try:
        validate_file_content_type(pdf_file)
        print(f"  ✓ Legitimate PDF passed validation")
        pdf_passed = True
    except ValidationError as e:
        print(f"  ❌ Legitimate PDF failed: {e}")
        pdf_passed = False

    assert pdf_passed, "Legitimate PDF should pass validation"

    print(f"\n✓ PASS: Legitimate PDFs pass content validation")
    print()


def test_fake_pdf_fails():
    """Test that fake PDF files (wrong content) fail validation"""
    print("=" * 70)
    print("TEST 3: Fake PDF Fails Validation")
    print("=" * 70)

    # Create fake PDF (executable or text file renamed to .pdf)
    fake_pdf_content = b'MZ\x90\x00\x03\x00\x00\x00'  # PE/COFF executable magic bytes
    fake_pdf_file = SimpleUploadedFile("malware.pdf", fake_pdf_content, content_type="application/pdf")

    try:
        validate_file_content_type(fake_pdf_file)
        print(f"  ❌ Fake PDF passed validation (SECURITY RISK!)")
        fake_pdf_failed = False
    except ValidationError as e:
        print(f"  ✓ Fake PDF rejected: {str(e)[:100]}...")
        fake_pdf_failed = True

    assert fake_pdf_failed, "Fake PDF should fail validation"

    # Also test text file renamed to PDF
    text_as_pdf = SimpleUploadedFile("text.pdf", b'This is just a text file', content_type="application/pdf")

    try:
        validate_file_content_type(text_as_pdf)
        print(f"  ❌ Text file as PDF passed validation (SECURITY RISK!)")
        text_pdf_failed = False
    except ValidationError as e:
        print(f"  ✓ Text file as PDF rejected: {str(e)[:100]}...")
        text_pdf_failed = True

    assert text_pdf_failed, "Text file disguised as PDF should fail"

    print(f"\n✓ PASS: Fake PDFs properly rejected")
    print()


def test_legitimate_images_pass():
    """Test that legitimate image files pass validation"""
    print("=" * 70)
    print("TEST 4: Legitimate Images Pass Validation")
    print("=" * 70)

    # Minimal valid PNG file (PNG magic bytes + IHDR chunk)
    png_content = (
        b'\x89PNG\r\n\x1a\n'  # PNG signature
        b'\x00\x00\x00\rIHDR'  # IHDR chunk
        b'\x00\x00\x00\x01\x00\x00\x00\x01'  # 1x1 pixel
        b'\x08\x02\x00\x00\x00'  # Color type, etc
        b'\x90wS\xde'  # CRC
        b'\x00\x00\x00\x00IEND\xaeB`\x82'  # IEND chunk
    )

    png_file = SimpleUploadedFile("test_image.png", png_content, content_type="image/png")

    try:
        validate_file_content_type(png_file)
        print(f"  ✓ Legitimate PNG passed validation")
        png_passed = True
    except ValidationError as e:
        print(f"  ❌ Legitimate PNG failed: {e}")
        png_passed = False

    # Minimal valid JPEG file (JPEG magic bytes)
    jpeg_content = (
        b'\xff\xd8\xff\xe0'  # JPEG SOI + APP0
        b'\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'  # JFIF header
        b'\xff\xd9'  # EOI
    )

    jpeg_file = SimpleUploadedFile("test_image.jpg", jpeg_content, content_type="image/jpeg")

    try:
        validate_file_content_type(jpeg_file)
        print(f"  ✓ Legitimate JPEG passed validation")
        jpeg_passed = True
    except ValidationError as e:
        print(f"  ❌ Legitimate JPEG failed: {e}")
        jpeg_passed = False

    assert png_passed, "Legitimate PNG should pass"
    assert jpeg_passed, "Legitimate JPEG should pass"

    print(f"\n✓ PASS: Legitimate images pass content validation")
    print()


def test_fake_images_fail():
    """Test that fake image files fail validation"""
    print("=" * 70)
    print("TEST 5: Fake Images Fail Validation")
    print("=" * 70)

    # Text file renamed to PNG
    fake_png = SimpleUploadedFile("fake.png", b'This is not an image', content_type="image/png")

    try:
        validate_file_content_type(fake_png)
        print(f"  ❌ Fake PNG passed validation (SECURITY RISK!)")
        fake_png_failed = False
    except ValidationError as e:
        print(f"  ✓ Fake PNG rejected: {str(e)[:100]}...")
        fake_png_failed = True

    assert fake_png_failed, "Fake PNG should fail validation"

    # Binary file renamed to JPG
    fake_jpg = SimpleUploadedFile("fake.jpg", b'\x00\x00\x00\x00binary data', content_type="image/jpeg")

    try:
        validate_file_content_type(fake_jpg)
        print(f"  ❌ Fake JPEG passed validation (SECURITY RISK!)")
        fake_jpg_failed = False
    except ValidationError as e:
        print(f"  ✓ Fake JPEG rejected: {str(e)[:100]}...")
        fake_jpg_failed = True

    assert fake_jpg_failed, "Fake JPEG should fail validation"

    print(f"\n✓ PASS: Fake images properly rejected")
    print()


def test_content_extension_mismatch():
    """Test that content-extension mismatches are detected"""
    print("=" * 70)
    print("TEST 6: Content-Extension Mismatch Detection")
    print("=" * 70)

    # Real PNG file but with .jpg extension
    png_content = (
        b'\x89PNG\r\n\x1a\n'
        b'\x00\x00\x00\rIHDR'
        b'\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00'
        b'\x90wS\xde'
        b'\x00\x00\x00\x00IEND\xaeB`\x82'
    )

    png_as_jpg = SimpleUploadedFile("image.jpg", png_content, content_type="image/jpeg")

    try:
        validate_file_content_type(png_as_jpg)
        print(f"  ❌ PNG-as-JPG passed validation (should detect mismatch)")
        mismatch_detected = False
    except ValidationError as e:
        error_msg = str(e)
        print(f"  ✓ Mismatch detected: {error_msg[:100]}...")
        # Check if error mentions the mismatch
        mismatch_detected = 'does not match' in error_msg.lower() or 'expected' in error_msg.lower()

    assert mismatch_detected, "Content-extension mismatch should be detected"

    print(f"\n✓ PASS: Content-extension mismatches properly detected")
    print()


def test_validator_applied_to_model_fields():
    """Test that validator is applied to model fields"""
    print("=" * 70)
    print("TEST 7: Validator Applied to Model Fields")
    print("=" * 70)

    from candidates.models import Candidate

    # Check photo field validators
    photo_field = Candidate._meta.get_field('photo')
    photo_validators = [v.__name__ if hasattr(v, '__name__') else str(v) for v in photo_field.validators]

    print(f"  Photo field validators: {photo_validators}")
    has_content_validator_photo = any('validate_file_content_type' in str(v) for v in photo_validators)

    # Check identity_document field validators
    identity_field = Candidate._meta.get_field('identity_document')
    identity_validators = [v.__name__ if hasattr(v, '__name__') else str(v) for v in identity_field.validators]

    print(f"  Identity document validators: {identity_validators}")
    has_content_validator_identity = any('validate_file_content_type' in str(v) for v in identity_validators)

    # Check candidacy_document field validators
    candidacy_field = Candidate._meta.get_field('candidacy_document')
    candidacy_validators = [v.__name__ if hasattr(v, '__name__') else str(v) for v in candidacy_field.validators]

    print(f"  Candidacy document validators: {candidacy_validators}")
    has_content_validator_candidacy = any('validate_file_content_type' in str(v) for v in candidacy_validators)

    assert has_content_validator_photo, "Photo field missing content validator"
    assert has_content_validator_identity, "Identity document field missing content validator"
    assert has_content_validator_candidacy, "Candidacy document field missing content validator"

    print(f"  ✓ All file upload fields have content-type validator")

    print(f"\n✓ PASS: Validator properly applied to all model fields")
    print()


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("DOCUMENT CONTENT-TYPE VALIDATION TEST SUITE")
    print("Testing fix for issue #30")
    print("=" * 70 + "\n")

    try:
        test_validator_exists()
        test_legitimate_pdf_passes()
        test_fake_pdf_fails()
        test_legitimate_images_pass()
        test_fake_images_fail()
        test_content_extension_mismatch()
        test_validator_applied_to_model_fields()

        print("=" * 70)
        print("ALL TESTS PASSED ✓")
        print("=" * 70)
        print("\nSummary:")
        print("- Content-type validator exists and is callable")
        print("- Legitimate PDFs pass validation (magic bytes checked)")
        print("- Fake PDFs properly rejected (malware protection)")
        print("- Legitimate images pass validation (actual format checked)")
        print("- Fake images properly rejected (renamed files blocked)")
        print("- Content-extension mismatches detected")
        print("- Validator applied to all file upload fields (photo, documents)")
        print("\nMalicious file uploads are now prevented!")

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
