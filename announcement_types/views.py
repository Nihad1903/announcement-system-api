"""
Views for AnnouncementType CRUD operations.
"""
import logging

from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from core.permissions import IsManagerOrReadOnly

from .models import AnnouncementType
from .serializers import AnnouncementTypeSerializer

logger = logging.getLogger('apps')


class AnnouncementTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for AnnouncementType CRUD.
    - Managers: full CRUD access
    - Users: read-only access
    """
    queryset = AnnouncementType.objects.all()
    serializer_class = AnnouncementTypeSerializer
    permission_classes = [IsManagerOrReadOnly]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def perform_destroy(self, instance):
        """Prevent deletion if type is linked to announcements."""
        if instance.announcements.exists():
            raise ValidationError(
                {'detail': 'Cannot delete announcement type that has linked announcements. '
                           'Remove or reassign announcements first.'}
            )
        logger.info('AnnouncementType deleted: %s (id=%d)', instance.name, instance.id)
        instance.delete()
