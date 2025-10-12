"""
Standardized API response utilities for consistent error and success handling.

This module provides helper functions to ensure all API endpoints return
responses in a consistent format, improving frontend developer experience
and reducing confusion.

Standard Formats:
- Error responses: {'error': 'message'}
- Success responses: {'success': True, 'message': 'message'}
- Data responses: {'data': {...}, ...} or direct data
"""

from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status as drf_status


def error_response(message, status=400, use_drf=False):
    """
    Return a standardized error response.

    Args:
        message (str): Error message to return
        status (int): HTTP status code (default: 400)
        use_drf (bool): Whether to use DRF Response (True) or Django JsonResponse (False)

    Returns:
        JsonResponse or Response: Standardized error response

    Examples:
        # Django view
        return error_response('Invalid province_id', status=400)

        # DRF view
        return error_response('Municipality not found', status=404, use_drf=True)
    """
    error_data = {'error': str(message)}

    if use_drf:
        return Response(error_data, status=status)
    else:
        return JsonResponse(error_data, status=status)


def success_response(message, data=None, status=200, use_drf=False):
    """
    Return a standardized success response.

    Args:
        message (str): Success message
        data (dict, optional): Additional data to include
        status (int): HTTP status code (default: 200)
        use_drf (bool): Whether to use DRF Response (True) or Django JsonResponse (False)

    Returns:
        JsonResponse or Response: Standardized success response

    Examples:
        # Simple success
        return success_response('Event deleted successfully')

        # Success with data
        return success_response('Profile updated', data={'candidate_id': 123})
    """
    response_data = {
        'success': True,
        'message': str(message)
    }

    if data:
        response_data.update(data)

    if use_drf:
        return Response(response_data, status=status)
    else:
        return JsonResponse(response_data, status=status)


def validation_error_response(errors, status=400, use_drf=False):
    """
    Return a standardized validation error response.

    Useful for form validation errors with field-specific messages.

    Args:
        errors (dict or str): Validation errors (field: message mapping or single message)
        status (int): HTTP status code (default: 400)
        use_drf (bool): Whether to use DRF Response (True) or Django JsonResponse (False)

    Returns:
        JsonResponse or Response: Standardized validation error response

    Examples:
        return validation_error_response({'email': 'Invalid email format'})
        return validation_error_response('Form validation failed')
    """
    if isinstance(errors, dict):
        error_data = {
            'error': 'Validation failed',
            'fields': errors
        }
    else:
        error_data = {'error': str(errors)}

    if use_drf:
        return Response(error_data, status=status)
    else:
        return JsonResponse(error_data, status=status)


# Common HTTP status codes as constants for convenience
HTTP_400_BAD_REQUEST = 400
HTTP_403_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404
HTTP_500_INTERNAL_SERVER_ERROR = 500
