"""
Announcement model — the core entity of the platform.
"""
from django.conf import settings
from django.db import models

from core.validators import validate_image_file


class Announcement(models.Model):
    """
    Represents an announcement posted by a Manager.
    Supports soft delete via is_deleted flag.
    """

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'

    title = models.CharField(
        max_length=255,
        db_index=True,
        help_text='Announcement title.',
    )
    description = models.TextField(
        help_text='Announcement body/description.',
    )
    image = models.ImageField(
        upload_to='announcements/images/%Y/%m/',
        blank=True,
        null=True,
        validators=[validate_image_file],
        help_text='Optional image attachment.',
    )
    type = models.ForeignKey(
        'announcement_types.AnnouncementType',
        on_delete=models.PROTECT,
        related_name='announcements',
        help_text='Category/type of the announcement.',
    )
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.PROTECT,
        related_name='announcements',
        help_text='Department the announcement belongs to.',
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
        help_text='Announcement visibility status.',
    )
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Soft delete flag.',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='announcements',
        help_text='Manager who created the announcement.',
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'announcements'
        ordering = ['-created_at']
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'
        indexes = [
            models.Index(fields=['status', 'is_deleted', '-created_at'], name='idx_active_announcements'),
            models.Index(fields=['department', 'status'], name='idx_dept_status'),
            models.Index(fields=['type', 'status'], name='idx_type_status'),
        ]

    def __str__(self):
        return self.title

    def soft_delete(self):
        """Mark announcement as deleted without removing from database."""
        self.is_deleted = True
        self.save(update_fields=['is_deleted', 'updated_at'])
