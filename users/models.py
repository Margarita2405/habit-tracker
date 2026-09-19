from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя для трекера привычек."""

    email = models.EmailField(unique=True, verbose_name="Электронная почта")
    telegram_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="ID в Telegram для уведомлений")

    # Меняем основное поле для входа на email
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
