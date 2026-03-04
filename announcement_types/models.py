"""
AnnouncementType model for categorizing announcements.
"""
from django.db import models


class AnnouncementType(models.Model):
    """
    Represents a type/category of announcement.
    Examples: General, Urgent, Event, Policy Update.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text='Announcement type name (e.g., General, Urgent, Event).',
    )
    description = models.TextField(
        blank=True,
        default='',
        help_text='Optional description of the announcement type.',
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text='Whether the announcement type is active.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'announcement_types'
        ordering = ['name']
        verbose_name = 'Announcement Type'
        verbose_name_plural = 'Announcement Types'

    def __str__(self):
        return self.name
