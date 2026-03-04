"""
Views for Department CRUD operations.
"""
import logging

from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from core.permissions import IsManagerOrReadOnly

from .models import Department
from .serializers import DepartmentSerializer

logger = logging.getLogger('apps')


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Department CRUD.
    - Managers: full CRUD access
    - Users: read-only access
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsManagerOrReadOnly]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def perform_destroy(self, instance):
        """Prevent deletion if department is linked to announcements."""
        if instance.announcements.exists():
            raise ValidationError(
                {'detail': 'Cannot delete department that has linked announcements. '
                           'Remove or reassign announcements first.'}
            )
        logger.info('Department deleted: %s (id=%d)', instance.name, instance.id)
        instance.delete()
