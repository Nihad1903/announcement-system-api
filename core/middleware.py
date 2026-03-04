"""
Custom middleware for the API.
"""
import logging
import time

logger = logging.getLogger('apps')


class RequestLoggingMiddleware:
    """
    Middleware to log request/response details.
    Logs method, path, status code, and response time.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.monotonic()

        response = self.get_response(request)

        duration = time.monotonic() - start_time
        logger.info(
            '%s %s %s %.3fs',
            request.method,
            request.get_full_path(),
            response.status_code,
            duration,
        )

        return response
