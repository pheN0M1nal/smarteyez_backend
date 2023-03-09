from django.contrib.auth import get_user_model

from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext_lazy as _
# Register your models here.

# Here you have to import the User model from your app!
from .models import User,EmailVerificationToken


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    list_display = ['user_id', 'email', 'first_name', 'account_type', 'is_superuser']
    search_fields=['email']
    fieldsets = (
        (None, {"fields": ("username", "password","email","parent_user","account_type")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "License")}),
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
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email','username','account_type', 'password1', 'password2','parent_user'),
        }),
    )

@admin.register(EmailVerificationToken)
class TokenAdmin(admin.ModelAdmin):
    list_display=['owner','token']
    search_fields = ['owner__email']
    fieldsets = (
        (_("Token"), {"fields": ("owner", "token")}),
    )
    readonly_fields = ['owner','token']