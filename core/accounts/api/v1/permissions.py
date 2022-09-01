from rest_framework.permissions import BasePermission


class NotAuthenticated(BasePermission):
    """
    Do NOT allows access to authenticated users.
    """

    def has_permission(self, request, view):
        return not bool(request.user and request.user.is_authenticated)
