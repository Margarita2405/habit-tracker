from django.core.exceptions import ValidationError
from django.db import models

from config import settings


class Habit(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Создатель")
    action = models.CharField(max_length=255, verbose_name="Действие")
    time = models.TimeField(verbose_name="Время выполнения")
    place = models.CharField(max_length=255, verbose_name="Место выполнения")

    # Разделение на полезные и приятные
    is_pleasant = models.BooleanField(default=False, verbose_name="Признак приятной привычки")
    reward = models.CharField(max_length=255, blank=True, null=True, verbose_name="Вознаграждение")
    bound_habit = models.ForeignKey(
        "self", on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Связанная привычка"
    )

    # Правило 2 минут и периодичность
    periodicity = models.IntegerField(default=1, verbose_name="Периодичность (в днях)")
    duration = models.IntegerField(default=2, verbose_name="Время на выполнение (мин)")

    # Публичность
    is_public = models.BooleanField(default=False, verbose_name="Публичный доступ")

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["time", "action"]

    def clean(self):
        # Ограничение из условий (время выполнения не более 2 минут)
        if self.duration > 2:
            raise ValidationError("Время на выполнение привычки не должно превышать 2 минут.")

        # Логика связанных и полезных привычек
        if self.is_pleasant:
            if self.reward or self.bound_habit:
                raise ValidationError("Приятная привычка не может содержать вознаграждение или связанную привычку.")
        else:
            if not self.reward and not self.bound_habit:
                raise ValidationError(
                    "У полезной привычки должно быть вознаграждение или связанная приятная привычка."
                )

    def __str__(self):
        return f"{self.action} ({self.place})"


class HabitLog(models.Model):
    """Модель для фиксации факта выполнения привычки."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="logs", verbose_name="Пользователь"
    )
    habit = models.ForeignKey("Habit", on_delete=models.CASCADE, related_name="logs", verbose_name="Привычка")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время выполнения")
    status = models.BooleanField(default=True, verbose_name="Статус выполнения")

    class Meta:
        verbose_name = "Выполнение привычки"
        verbose_name_plural = "Выполнения привычек"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user.username} выполнил '{self.habit.action}' в {self.timestamp}"
