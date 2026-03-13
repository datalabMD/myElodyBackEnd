from django.db import models

from core.models import UUIDModel, TimeStampedModel


class Store(UUIDModel, TimeStampedModel):
    name = models.CharField(
        max_length=255,
        verbose_name="Название",
    )
    address = models.TextField(
        verbose_name="Адрес",
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name="Широта",
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name="Долгота",
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Телефон",
    )
    opening_hours = models.JSONField(
        default=dict,
        verbose_name="Часы работы",
    )
    services = models.JSONField(
        default=dict,
        verbose_name="Услуги",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна",
    )

    class Meta:
        verbose_name = "Аптека"
        verbose_name_plural = "Аптеки"
        db_table = "stores"

    def __str__(self):
        return self.name