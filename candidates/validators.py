from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import os
from PIL import Image
import io


def validate_file_size(file):
    """Validate file size - max 10MB for documents"""
    max_size_mb = 10
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(
            _('File size cannot exceed %(max_size)s MB.'),
            params={'max_size': max_size_mb}
        )


def validate_image_size(file):
    """Validate image file size - max 5MB for photos"""
    max_size_mb = 5
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(
            _('Image size cannot exceed %(max_size)s MB.'),
            params={'max_size': max_size_mb}
        )


def validate_file_extension(file):
    """Validate file extension for documents"""
    valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError(
            _('Invalid file type. Allowed types: PDF, JPG, JPEG, PNG'),
        )


def validate_image_extension(file):
    """Validate image file extension"""
    valid_extensions = ['.jpg', '.jpeg', '.png']
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError(
            _('Invalid image type. Allowed types: JPG, JPEG, PNG'),
        )


def validate_file_content_type(file):
    """
    Validate file content type by checking magic bytes (file signature).

    This prevents malicious files disguised with fake extensions.
    Checks actual file content, not just the filename extension.
    """
    # Read first few bytes to check file signature
    file.seek(0)  # Reset file pointer to beginning
    file_start = file.read(512)  # Read first 512 bytes
    file.seek(0)  # Reset again for further processing

    # Get file extension from filename
    ext = os.path.splitext(file.name)[1].lower()

    # PDF magic bytes: %PDF
    if ext == '.pdf':
        if not file_start.startswith(b'%PDF'):
            raise ValidationError(
                _('File appears to be corrupted or is not a valid PDF document. '
                  'Please upload a legitimate PDF file.'),
            )

    # Image validation using Pillow (checks actual image format)
    # Pillow is the modern replacement for deprecated imghdr module
    elif ext in ['.jpg', '.jpeg', '.png']:
        try:
            # Use Pillow to detect and validate actual image type
            img = Image.open(io.BytesIO(file_start))
            detected_format = img.format.lower() if img.format else None

            if detected_format is None:
                raise ValidationError(
                    _('File appears to be corrupted or is not a valid image. '
                      'Please upload a legitimate image file.'),
                )

            # Map extensions to expected Pillow formats
            extension_format_map = {
                '.jpg': 'jpeg',
                '.jpeg': 'jpeg',
                '.png': 'png',
            }

            expected_format = extension_format_map.get(ext)

            # Check if detected format matches expected format
            if detected_format != expected_format:
                raise ValidationError(
                    _('File content does not match extension. Expected %(expected)s but got %(actual)s. '
                      'Please upload a valid file without changing its extension.'),
                    params={'expected': expected_format.upper(), 'actual': detected_format.upper()}
                )
        except (IOError, OSError) as e:
            # PIL raises IOError/OSError for invalid or corrupted images
            raise ValidationError(
                _('File appears to be corrupted or is not a valid image. '
                  'Please upload a legitimate image file.'),
            )