from django.contrib.auth import get_user_model

from django.contrib import admin
from django.contrib.auth import admin as auth_admin

from . import models

# Register your models here.

# Here you have to import the User model from your app!
from .models import User


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    list_display = ['user_id', 'email', 'first_name', 'account_type', 'is_superuser']
