"""
Standardized API response helpers.
"""
from rest_framework import status
from rest_framework.response import Response


def success_response(data=None, message='Success', status_code=status.HTTP_200_OK):
    """Return a standardized success response."""
    payload = {
        'status': 'success',
        'message': message,
    }
    if data is not None:
        payload['data'] = data
    return Response(payload, status=status_code)


def created_response(data=None, message='Created successfully'):
    """Return a standardized 201 created response."""
    return success_response(data=data, message=message, status_code=status.HTTP_201_CREATED)


def error_response(message='An error occurred', errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    """Return a standardized error response."""
    payload = {
        'status': 'error',
        'message': message,
    }
    if errors is not None:
        payload['errors'] = errors
    return Response(payload, status=status_code)


def no_content_response():
    """Return a 204 No Content response."""
    return Response(status=status.HTTP_204_NO_CONTENT)
