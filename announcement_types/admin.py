"""
Admin configuration for announcement_types app.
"""
from django.contrib import admin

from .models import AnnouncementType


@admin.register(AnnouncementType)
class AnnouncementTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    ordering = ['name']
