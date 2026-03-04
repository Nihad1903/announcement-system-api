"""
Custom validators for file uploads and input sanitization.
"""
import os

from django.conf import settings
from django.core.exceptions import ValidationError


def validate_image_file(value):
    """
    Validate uploaded image files:
    - Check file extension against allowed list
    - Check file size against maximum
    """
    ext = os.path.splitext(value.name)[1].lstrip('.').lower()
    allowed = getattr(settings, 'ALLOWED_IMAGE_EXTENSIONS', ['jpg', 'jpeg', 'png', 'gif', 'webp'])
    if ext not in allowed:
        raise ValidationError(
            f'Unsupported file extension "{ext}". Allowed: {", ".join(allowed)}'
        )

    max_size_mb = getattr(settings, 'MAX_IMAGE_SIZE_MB', 5)
    max_size_bytes = max_size_mb * 1024 * 1024
    if value.size > max_size_bytes:
        raise ValidationError(
            f'File size ({value.size / (1024 * 1024):.1f}MB) exceeds '
            f'the maximum allowed size ({max_size_mb}MB).'
        )
