"""
Serializers for Announcement model.
Separate serializers for Create, Update, List, and Detail actions.
"""
from rest_framework import serializers

from announcement_types.serializers import AnnouncementTypeSerializer
from departments.serializers import DepartmentSerializer

from .models import Announcement


class AnnouncementListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for announcement list views.
    Includes nested type/department names and created_by username.
    """
    type_name = serializers.CharField(source='type.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    created_by_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'image', 'status',
            'type', 'type_name',
            'department', 'department_name',
            'created_by_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = fields

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f'{obj.created_by.first_name} {obj.created_by.last_name}'.strip() or obj.created_by.username
        return None


class AnnouncementDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for announcement detail view.
    Includes full nested type and department objects.
    """
    type = AnnouncementTypeSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    created_by_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'description', 'image', 'status',
            'type', 'department',
            'created_by', 'created_by_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = fields

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f'{obj.created_by.first_name} {obj.created_by.last_name}'.strip() or obj.created_by.username
        return None


class AnnouncementCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating announcements.
    Accepts type and department as foreign key IDs.
    """

    class Meta:
        model = Announcement
        fields = [
            'title', 'description', 'image',
            'type', 'department', 'status',
        ]

    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError('Title must be at least 3 characters long.')
        return value.strip()

    def validate_description(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError('Description must be at least 10 characters long.')
        return value.strip()

    def to_representation(self, instance):
        """Return the detail serializer representation after creation."""
        return AnnouncementDetailSerializer(instance, context=self.context).data


class AnnouncementUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating announcements.
    All fields optional for partial updates.
    """

    class Meta:
        model = Announcement
        fields = [
            'title', 'description', 'image',
            'type', 'department', 'status',
        ]
        extra_kwargs = {field: {'required': False} for field in fields}

    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError('Title must be at least 3 characters long.')
        return value.strip()

    def validate_description(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError('Description must be at least 10 characters long.')
        return value.strip()

    def to_representation(self, instance):
        """Return the detail serializer representation after update."""
        return AnnouncementDetailSerializer(instance, context=self.context).data
