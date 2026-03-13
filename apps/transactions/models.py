from django.db import models

from apps.users.models import User
from apps.stores.models import Store
from core.models import UUIDModel, TimeStampedModel


class Transaction(UUIDModel, TimeStampedModel):
    STATUS_CHOICES = [
        ("pending", "Ожидает"),
        ("completed", "Завершена"),
        ("refunded", "Возврат"),
        ("cancelled", "Отменена"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="Пользователь",
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.PROTECT,
        related_name="transactions",
        verbose_name="Аптека",
    )
    transaction_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Номер транзакции",
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма чека",
    )
    bonus_earned = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Начислено бонусов",
    )
    bonus_spent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Списано бонусов",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="completed",
        verbose_name="Статус",
    )
    receipt_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="URL чека",
    )
    transaction_date = models.DateTimeField(
        verbose_name="Дата транзакции",
    )
    erp_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="ID в ERP",
    )

    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"
        db_table = "transactions"
        ordering = ["-transaction_date"]

    def __str__(self):
        return f"{self.transaction_number} - {self.total_amount} MDL"


class TransactionItem(UUIDModel):
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Транзакция",
    )
    product_id = models.CharField(
        max_length=100,
        verbose_name="ID товара",
    )
    product_name = models.CharField(
        max_length=255,
        verbose_name="Название товара",
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Количество",
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена за единицу",
    )
    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Скидка",
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма по строке",
    )
    promotion = models.ForeignKey(
        "promotions.Promotion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transaction_items",
        verbose_name="Акция",
    )
    is_promotional = models.BooleanField(
        default=False,
        verbose_name="По акции",
    )

    class Meta:
        verbose_name = "Позиция чека"
        verbose_name_plural = "Позиции чеков"
        db_table = "transaction_items"

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"