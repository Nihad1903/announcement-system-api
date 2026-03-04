"""
Custom permission classes for role-based access control.
"""
from rest_framework.permissions import BasePermission

# Role constants
ROLE_MANAGER = 'manager'
ROLE_USER = 'user'


class IsManager(BasePermission):
    """
    Permission class that allows access only to users with the 'manager' role.
    """
    message = 'Only managers can perform this action.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == ROLE_MANAGER
        )


class IsManagerOrReadOnly(BasePermission):
    """
    Permission class that allows:
    - Full access for managers
    - Read-only access for authenticated users
    """
    message = 'Only managers can modify this resource.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True

        return request.user.role == ROLE_MANAGER
