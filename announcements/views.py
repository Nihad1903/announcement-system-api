"""
Views for Announcement CRUD and listing.
"""
import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from core.permissions import IsManager, IsManagerOrReadOnly
from core.responses import success_response

from .filters import AnnouncementFilter
from .models import Announcement
from .serializers import (
    AnnouncementCreateSerializer,
    AnnouncementDetailSerializer,
    AnnouncementListSerializer,
    AnnouncementUpdateSerializer,
)

logger = logging.getLogger('apps')


class AnnouncementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Announcement CRUD.
    - Managers: full CRUD access (see all, including inactive/deleted)
    - Users: read-only, only active & non-deleted announcements
    """
    permission_classes = [IsManagerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AnnouncementFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Return appropriate queryset based on user role:
        - Managers see all non-deleted announcements (including inactive)
        - Users see only active, non-deleted announcements
        """
        qs = Announcement.objects.select_related('type', 'department', 'created_by')

        if self.request.user.is_authenticated and self.request.user.is_manager:
            return qs.filter(is_deleted=False)

        return qs.filter(status=Announcement.Status.ACTIVE, is_deleted=False)

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return AnnouncementCreateSerializer
        if self.action in ('update', 'partial_update'):
            return AnnouncementUpdateSerializer
        if self.action == 'retrieve':
            return AnnouncementDetailSerializer
        return AnnouncementListSerializer

    def perform_create(self, serializer):
        """Set the created_by field to the current user."""
        serializer.save(created_by=self.request.user)
        logger.info(
            'Announcement created: "%s" by %s',
            serializer.instance.title,
            self.request.user.username,
        )

    def perform_update(self, serializer):
        """Log announcement updates."""
        serializer.save()
        logger.info(
            'Announcement updated: "%s" (id=%d) by %s',
            serializer.instance.title,
            serializer.instance.id,
            self.request.user.username,
        )

    def perform_destroy(self, instance):
        """Soft delete instead of hard delete."""
        instance.soft_delete()
        logger.info(
            'Announcement soft-deleted: "%s" (id=%d) by %s',
            instance.title,
            instance.id,
            self.request.user.username,
        )
