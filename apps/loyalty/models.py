from django.db import models

from apps.users.models import User
from core.models import UUIDModel, TimeStampedModel


class LoyaltyCard(UUIDModel, TimeStampedModel):
    BARCODE_TYPE_CHOICES = [
        ("code128", "Code 128"),
        ("qr", "QR Code"),
        ("ean13", "EAN-13"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="loyalty_cards",
        verbose_name="Владелец",
    )
    card_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Номер карты",
    )
    barcode_type = models.CharField(
        max_length=20,
        choices=BARCODE_TYPE_CHOICES,
        default="code128",
        verbose_name="Тип штрихкода",
    )
    is_virtual = models.BooleanField(default=True, verbose_name="Виртуальная карта")
    has_physical_card = models.BooleanField(
        default=False, verbose_name="Привязана физическая карта"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Карта лояльности"
        verbose_name_plural = "Карты лояльности"
        db_table = "loyalty_cards"

    def __str__(self):
        return f"Карта {self.card_number} ({self.user.phone})"


class BonusLedger(UUIDModel, TimeStampedModel):
    TYPE_CHOICES = [
        ("earned", "Начислено"),
        ("spent", "Списано"),
        ("expired", "Сгорело"),
        ("adjusted", "Корректировка"),
        ("bonus", "Бонус"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bonus_ledger",
        verbose_name="Пользователь",
    )
    transaction = models.ForeignKey(
        "transactions.Transaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bonus_entries",
        verbose_name="Транзакция",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма",
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name="Тип операции",
    )
    description = models.TextField(
        blank=True, verbose_name="Описание"
    )
    expires_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Срок действия",
    )

    class Meta:
        verbose_name = "Запись бонусов"
        verbose_name_plural = "Журнал бонусов"
        db_table = "bonus_ledger"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.type}: {self.amount} для {self.user.phone}"


class BonusSettings(TimeStampedModel):
    bonus_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=5.0,
        verbose_name="Процент начисления бонусов (%)",
    )
    expiration_months = models.PositiveIntegerField(
        default=12,
        verbose_name="Срок действия бонусов (месяцев)",
    )
    min_bonus_to_spend = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=10.0,
        verbose_name="Минимум бонусов для списания",
    )

    class Meta:
        verbose_name = "Настройки бонусов"
        verbose_name_plural = "Настройки бонусов"
        db_table = "bonus_settings"

    def __str__(self):
        return f"Бонусная программа: {self.bonus_rate}%"