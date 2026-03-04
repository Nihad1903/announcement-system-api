"""
Serializers for AnnouncementType model.
"""
from rest_framework import serializers

from .models import AnnouncementType


class AnnouncementTypeSerializer(serializers.ModelSerializer):
    """
    Full serializer for AnnouncementType CRUD operations.
    Includes announcement count for list views.
    """
    announcement_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AnnouncementType
        fields = ['id', 'name', 'description', 'is_active', 'announcement_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_announcement_count(self, obj):
        """Return count of active announcements with this type."""
        return obj.announcements.filter(
            status='active', is_deleted=False
        ).count()

    def validate_name(self, value):
        """Ensure type name is unique (case-insensitive)."""
        qs = AnnouncementType.objects.filter(name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('An announcement type with this name already exists.')
        return value
