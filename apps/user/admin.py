from django.contrib.auth import get_user_model

from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _
# Register your models here.

from .models import User


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    list_display = ['user_id', 'email', 'first_name', 'account_type', 'is_superuser']
    search_fields=['email']
    fieldsets = (
        (None, {"fields": ("username", "password","parent_user","account_type")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email","License")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )