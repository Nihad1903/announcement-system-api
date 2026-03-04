"""
Custom User model with role-based access support.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Extended User model with role field for RBAC.
    Roles: 'manager' (admin) or 'user' (regular).
    """

    class Role(models.TextChoices):
        MANAGER = 'manager', 'Manager'
        USER = 'user', 'User'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
        db_index=True,
        help_text='User role for access control.',
    )

    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'

    @property
    def is_manager(self):
        return self.role == self.Role.MANAGER
