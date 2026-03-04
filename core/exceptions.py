"""
Global exception handler for the API.
Provides consistent error response format across all endpoints.
"""
import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger('apps')


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns consistent JSON error responses.
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)

    # Handle Django's ValidationError
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, 'message_dict'):
            errors = exc.message_dict
        else:
            errors = {'detail': exc.messages}
        return Response(
            {
                'status': 'error',
                'message': 'Validation error.',
                'errors': errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if response is not None:
        custom_response = {
            'status': 'error',
            'message': _get_error_message(exc),
            'errors': _get_error_details(exc, response),
        }
        response.data = custom_response
        return response

    # Handle unhandled exceptions
    logger.exception(f'Unhandled exception: {exc}', exc_info=exc)
    return Response(
        {
            'status': 'error',
            'message': 'An unexpected error occurred.',
            'errors': {},
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _get_error_message(exc):
    """Extract a human-readable error message from the exception."""
    if isinstance(exc, ValidationError):
        return 'Validation error.'
    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        return 'Authentication failed.'
    if isinstance(exc, PermissionDenied):
        return 'Permission denied.'
    if isinstance(exc, Http404):
        return 'Resource not found.'
    if isinstance(exc, APIException):
        return str(exc.detail) if hasattr(exc, 'detail') else 'An error occurred.'
    return 'An unexpected error occurred.'


def _get_error_details(exc, response):
    """Extract structured error details from the exception."""
    if isinstance(exc, ValidationError):
        return response.data
    if hasattr(exc, 'detail'):
        detail = exc.detail
        if isinstance(detail, dict):
            return detail
        if isinstance(detail, list):
            return {'detail': detail}
        return {'detail': str(detail)}
    return {}
