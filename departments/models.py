"""
Department model for organizational structure.
"""
from django.db import models


class Department(models.Model):
    """
    Represents an organizational department.
    Used to categorize announcements by department.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text='Department name (e.g., IT, HR, Marketing).',
    )
    description = models.TextField(
        blank=True,
        default='',
        help_text='Optional description of the department.',
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text='Whether the department is active.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'departments'
        ordering = ['name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return self.name
