from django.conf import settings
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

from core.models import UUIDModel, TimeStampedModel


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("Phone number is required")
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(phone, password, **extra_fields)


phone_validator = RegexValidator(
    regex=r"^\+?[1-9]\d{6,14}$",
    message="Номер телефона должен быть в формате +373xxxxxxxx",
)


class User(AbstractBaseUser, UUIDModel, TimeStampedModel):
    phone = models.CharField(
        max_length=16,
        unique=True,
        validators=[phone_validator],
        verbose_name="Телефон",
    )
    email = models.EmailField(
        unique=True,
        blank=True,
        null=True,
        verbose_name="Email",
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Персонал")
    is_superuser = models.BooleanField(default=False, verbose_name="Суперпользователь")

    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        db_table = "users"

    def __str__(self):
        return self.phone


class CustomerProfile(UUIDModel, TimeStampedModel):
    GENDER_CHOICES = [
        ("male", "Мужской"),
        ("female", "Женский"),
        ("other", "Другой"),
    ]

    TIER_CHOICES = [
        ("bronze", "Bronze"),
        ("silver", "Silver"),
        ("gold", "Gold"),
        ("platinum", "Platinum"),
    ]

    STATUS_CHOICES = [
        ("active", "Активен"),
        ("inactive", "Неактивен"),
        ("suspended", "Заблокирован"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь",
    )
    first_name = models.CharField(max_length=100, blank=True, verbose_name="Имя")
    last_name = models.CharField(max_length=100, blank=True, verbose_name="Фамилия")
    middle_name = models.CharField(max_length=100, blank=True, verbose_name="Отчество")
    birth_date = models.DateField(
        blank=True, null=True, verbose_name="Дата рождения"
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        verbose_name="Пол",
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        verbose_name="Аватар",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
        verbose_name="Статус",
    )
    loyalty_tier = models.CharField(
        max_length=20,
        choices=TIER_CHOICES,
        default="bronze",
        verbose_name="Уровень лояльности",
    )
    registered_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата регистрации"
    )

    class Meta:
        verbose_name = "Профиль клиента"
        verbose_name_plural = "Профили клиентов"
        db_table = "customer_profiles"

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.user.phone})"

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()