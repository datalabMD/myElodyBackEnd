from django.db import models

from core.models import UUIDModel, TimeStampedModel


class Promotion(UUIDModel, TimeStampedModel):
    TYPE_CHOICES = [
        ("promotion", "Акция"),
        ("news", "Новость"),
    ]

    title = models.CharField(
        max_length=255,
        verbose_name="Заголовок",
    )
    subtitle = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Подзаголовок",
    )
    description = models.TextField(
        verbose_name="Описание",
    )
    image_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="URL изображения",
    )
    start_date = models.DateField(
        verbose_name="Дата начала",
    )
    end_date = models.DateField(
        verbose_name="Дата окончания",
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="promotion",
        verbose_name="Тип",
    )
    category = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Категория",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна",
    )
    participating_stores = models.ManyToManyField(
        "stores.Store",
        blank=True,
        related_name="promotions",
        verbose_name="Участвующие аптеки",
    )

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"
        db_table = "promotions"
        ordering = ["-start_date"]

    def __str__(self):
        return self.title


class NewsItem(UUIDModel, TimeStampedModel):
    title = models.CharField(
        max_length=255,
        verbose_name="Заголовок",
    )
    subtitle = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Подзаголовок",
    )
    content = models.TextField(
        verbose_name="Содержание",
    )
    image_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="URL изображения",
    )
    published_at = models.DateTimeField(
        verbose_name="Дата публикации",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна",
    )

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        db_table = "news_items"
        ordering = ["-published_at"]

    def __str__(self):
        return self.title