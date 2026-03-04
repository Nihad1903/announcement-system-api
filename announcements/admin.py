"""
Admin configuration for announcements app.
"""
from django.contrib import admin

from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'department', 'status', 'is_deleted', 'created_by', 'created_at']
    list_filter = ['status', 'is_deleted', 'type', 'department']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    raw_id_fields = ['type', 'department', 'created_by']
