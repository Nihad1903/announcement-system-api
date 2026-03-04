"""
Root URL configuration for the Announcement Management Platform API.
All API endpoints are versioned under /api/v1/.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """API root endpoint — health check and version info."""
    return Response({
        'status': 'success',
        'message': 'Announcement Management Platform API',
        'version': 'v1',
        'endpoints': {
            'auth': '/api/v1/auth/',
            'announcements': '/api/v1/announcements/',
            'departments': '/api/v1/departments/',
            'announcement_types': '/api/v1/announcement-types/',
        },
    })


# API v1 URL patterns
api_v1_patterns = [
    path('auth/', include('accounts.urls', namespace='accounts')),
    path('announcements/', include('announcements.urls', namespace='announcements')),
    path('departments/', include('departments.urls', namespace='departments')),
    path('announcement-types/', include('announcement_types.urls', namespace='announcement_types')),
]

urlpatterns = [
    path('', api_root, name='api_root'),
    path('admin/', admin.site.urls),
    path('api/v1/', include((api_v1_patterns, 'api_v1'))),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

