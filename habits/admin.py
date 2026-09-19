from django.contrib import admin

from .models import Habit, HabitLog


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ("action", "creator", "time", "place", "is_public", "is_pleasant")
    list_filter = ("is_public", "is_pleasant", "periodicity")
    search_fields = ("action", "creator__email")


@admin.register(HabitLog)
class HabitLogAdmin(admin.ModelAdmin):
    list_display = ("habit", "user", "timestamp", "status")
    list_filter = ("status", "timestamp")
