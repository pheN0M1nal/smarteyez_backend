from rest_framework import permissions
from .enum import UserAccountType


class IsUserOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.account_type == UserAccountType.USER.value or request.user.account_type == UserAccountType.ADMINISTRATOR.value:
                return True
        return False

