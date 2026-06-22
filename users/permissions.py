from rest_framework.permissions import BasePermission


class IsCreatorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and hasattr(request.user, 'role')
            and request.user.role in ('CREATOR', 'ADMIN')
        )


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and hasattr(request.user, 'role')
            and request.user.role == 'ADMIN'
        )
