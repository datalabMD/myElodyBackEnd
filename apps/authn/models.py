from django.db import models

from core.models import UUIDModel, TimeStampedModel


class OTP(UUIDModel, TimeStampedModel):
    PURPOSE_CHOICES = [
        ("login", "Вход"),
        ("password_reset", "Сброс пароля"),
    ]

    phone = models.CharField(
        max_length=16,
        verbose_name="Телефон",
    )
    code = models.CharField(
        max_length=6,
        verbose_name="Код",
    )
    purpose = models.CharField(
        max_length=20,
        choices=PURPOSE_CHOICES,
        default="login",
        verbose_name="Назначение",
    )
    attempts = models.PositiveIntegerField(
        default=0,
        verbose_name="Попыток",
    )
    is_used = models.BooleanField(
        default=False,
        verbose_name="Использован",
    )
    expires_at = models.DateTimeField(
        verbose_name="Истекает",
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP адрес",
    )

    class Meta:
        verbose_name = "OTP код"
        verbose_name_plural = "OTP коды"
        db_table = "otps"
        ordering = ["-created_at"]

    def __str__(self):
        return f"OTP {self.phone} - {self.purpose}"

    @property
    def is_valid(self):
        from django.utils import timezone
        return not self.is_used and timezone.now() < self.expires_at


class PasswordResetToken(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="password_reset_tokens",
        verbose_name="Пользователь",
    )
    token = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="Токен",
    )
    is_used = models.BooleanField(
        default=False,
        verbose_name="Использован",
    )
    expires_at = models.DateTimeField(
        verbose_name="Истекает",
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP адрес",
    )

    class Meta:
        verbose_name = "Токен сброса пароля"
        verbose_name_plural = "Токены сброса пароля"
        db_table = "password_reset_tokens"

    def __str__(self):
        return f"Password reset for {self.user.phone}"