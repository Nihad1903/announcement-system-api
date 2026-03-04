"""
Serializers for Department model.
"""
from rest_framework import serializers

from .models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    """
    Full serializer for Department CRUD operations.
    Includes announcement count for list views.
    """
    announcement_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'is_active', 'announcement_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_announcement_count(self, obj):
        """Return count of active announcements in this department."""
        return obj.announcements.filter(
            status='active', is_deleted=False
        ).count()

    def validate_name(self, value):
        """Ensure department name is unique (case-insensitive)."""
        qs = Department.objects.filter(name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('A department with this name already exists.')
        return value
