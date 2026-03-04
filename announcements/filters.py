"""
Filter classes for Announcement queries.
Supports filtering by department, type, status, and date range.
"""
import django_filters

from .models import Announcement


class AnnouncementFilter(django_filters.FilterSet):
    """
    FilterSet for announcements.
    Supports:
    - department: filter by department ID
    - type: filter by announcement type ID
    - status: filter by status (active/inactive) — managers only benefit
    - created_after: announcements created on or after a date
    - created_before: announcements created on or before a date
    """
    department = django_filters.NumberFilter(field_name='department__id')
    type = django_filters.NumberFilter(field_name='type__id')
    status = django_filters.ChoiceFilter(
        choices=Announcement.Status.choices,
        field_name='status',
    )
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
    )
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
    )

    class Meta:
        model = Announcement
        fields = ['department', 'type', 'status', 'created_after', 'created_before']
