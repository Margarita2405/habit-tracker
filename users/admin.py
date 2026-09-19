from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("email", "username", "telegram_id", "is_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (("Telegram", {"fields": ("telegram_id",)}),)
