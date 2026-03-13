from django.db import models

from apps.users.models import User
from core.models import UUIDModel


class UserSettings(UUIDModel):
    LANGUAGE_CHOICES = [
        ("ru", "Русский"),
        ("ro", "Румынский"),
        ("en", "Английский"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="settings",
        verbose_name="Пользователь",
    )
    language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default="ru",
        verbose_name="Язык",
    )
    currency = models.CharField(
        max_length=3,
        default="MDL",
        verbose_name="Валюта",
    )

    class Meta:
        verbose_name = "Настройки пользователя"
        verbose_name_plural = "Настройки пользователей"
        db_table = "user_settings"

    def __str__(self):
        return f"Настройки {self.user.phone}"