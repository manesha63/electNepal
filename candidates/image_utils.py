"""
Image optimization utilities for candidate photos
Automatically resizes and compresses images to improve performance
"""

from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
import os
import logging

logger = logging.getLogger(__name__)


def optimize_image(image_field, max_width=800, max_height=800, quality=85):
    """
    Optimize an image by resizing and compressing it

    Args:
        image_field: Django ImageField instance
        max_width: Maximum width in pixels (default 800px)
        max_height: Maximum height in pixels (default 800px)
        quality: JPEG quality (1-100, default 85)

    Returns:
        Optimized image field or None if optimization fails
    """
    if not image_field:
        return None

    try:
        # Open the image
        img = Image.open(image_field)

        # Convert RGBA to RGB if necessary (for PNG with transparency)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background

        # Calculate the new size while maintaining aspect ratio
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

        # Save the image to a BytesIO object
        output = BytesIO()

        # Determine format
        format_name = 'JPEG'
        content_type = 'image/jpeg'
        extension = 'jpg'

        # Save with optimization
        img.save(
            output,
            format=format_name,
            quality=quality,
            optimize=True,
            progressive=True  # Create progressive JPEG for faster perceived loading
        )

        output.seek(0)

        # Get the original filename without extension
        original_name = os.path.splitext(image_field.name)[0]
        new_name = f"{original_name}.{extension}"

        # Create a new InMemoryUploadedFile with the optimized image
        optimized_image = InMemoryUploadedFile(
            output,
            'ImageField',
            new_name,
            content_type,
            sys.getsizeof(output),
            None
        )

        # Log the optimization
        original_size = image_field.size if hasattr(image_field, 'size') else 0
        optimized_size = sys.getsizeof(output)

        if original_size > 0:
            reduction_percent = ((original_size - optimized_size) / original_size) * 100
            logger.info(
                f"Image optimized: {original_name} "
                f"({original_size / 1024:.1f}KB -> {optimized_size / 1024:.1f}KB, "
                f"{reduction_percent:.1f}% reduction)"
            )

        return optimized_image

    except Exception as e:
        logger.error(f"Error optimizing image: {str(e)}")
        # Return the original image if optimization fails
        return image_field


def should_optimize_image(image_field):
    """
    Check if an image should be optimized

    Args:
        image_field: Django ImageField instance

    Returns:
        Boolean indicating if image should be optimized
    """
    if not image_field:
        return False

    try:
        # Check if it's a new upload (has a file attribute)
        if not hasattr(image_field, 'file'):
            return False

        # Check file size - optimize if larger than 500KB
        if hasattr(image_field, 'size') and image_field.size > 500 * 1024:
            return True

        # Open and check dimensions
        img = Image.open(image_field)
        width, height = img.size

        # Optimize if dimensions are larger than 800x800
        if width > 800 or height > 800:
            return True

        return False

    except Exception as e:
        logger.error(f"Error checking if image should be optimized: {str(e)}")
        return False


def get_image_dimensions(image_field):
    """
    Get the dimensions of an image

    Args:
        image_field: Django ImageField instance

    Returns:
        Tuple of (width, height) or (None, None) if unable to get dimensions
    """
    if not image_field:
        return None, None

    try:
        img = Image.open(image_field)
        return img.size
    except Exception as e:
        logger.error(f"Error getting image dimensions: {str(e)}")
        return None, None