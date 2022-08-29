from rest_framework.permissions import BasePermission


class IsVerified(BasePermission):
    """
    Only allows access to verified users.
    """
    def has_permission(self, request, view):
        print(request.user)
        return request.user.is_verified