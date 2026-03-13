from django.db import models

from apps.users.models import User
from core.models import UUIDModel, TimeStampedModel


class Notification(UUIDModel, TimeStampedModel):
    TYPE_CHOICES = [
        ("system", "Системное"),
        ("marketing", "Маркетинговое"),
        ("bonus", "Бонусное"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Пользователь",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Заголовок",
    )
    message = models.TextField(
        verbose_name="Сообщение",
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="system",
        verbose_name="Тип",
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name="Прочитано",
    )
    sent_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Отправлено",
    )
    read_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Прочитано в",
    )

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
        db_table = "notifications"
        ordering = ["-sent_at"]

    def __str__(self):
        return f"{self.title} - {self.user.phone}"


class UserNotificationSettings(UUIDModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="notification_settings",
        verbose_name="Пользователь",
    )
    push_enabled = models.BooleanField(
        default=True,
        verbose_name="Push-уведомления",
    )
    email_enabled = models.BooleanField(
        default=True,
        verbose_name="Email-уведомления",
    )
    sms_enabled = models.BooleanField(
        default=False,
        verbose_name="SMS-уведомления",
    )
    marketing_enabled = models.BooleanField(
        default=True,
        verbose_name="Маркетинговые",
    )
    bonus_notifications = models.BooleanField(
        default=True,
        verbose_name="Бонусные уведомления",
    )

    class Meta:
        verbose_name = "Настройки уведомлений"
        verbose_name_plural = "Настройки уведомлений"
        db_table = "user_notification_settings"

    def __str__(self):
        return f"Настройки уведомлений {self.user.phone}"