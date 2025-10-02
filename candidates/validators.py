from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import os


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