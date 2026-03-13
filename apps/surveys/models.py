from django.db import models

from core.models import UUIDModel, TimeStampedModel


class Survey(UUIDModel, TimeStampedModel):
    title = models.CharField(
        max_length=255,
        verbose_name="Заголовок",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )
    reward_bonus = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Бонус за прохождение",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
    )
    starts_at = models.DateTimeField(
        verbose_name="Начало",
    )
    ends_at = models.DateTimeField(
        verbose_name="Конец",
    )
    target_tiers = models.JSONField(
        default=list,
        verbose_name="Целевые уровни лояльности",
    )

    class Meta:
        verbose_name = "Опрос"
        verbose_name_plural = "Опросы"
        db_table = "surveys"

    def __str__(self):
        return self.title


class SurveyQuestion(UUIDModel):
    QUESTION_TYPE_CHOICES = [
        ("single_choice", "Один вариант"),
        ("multiple_choice", "Множественный выбор"),
        ("text", "Текст"),
    ]

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Опрос",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок",
    )
    question_text = models.TextField(
        verbose_name="Текст вопроса",
    )
    question_type = models.CharField(
        max_length=30,
        choices=QUESTION_TYPE_CHOICES,
        default="single_choice",
        verbose_name="Тип вопроса",
    )
    options = models.JSONField(
        default=list,
        verbose_name="Варианты ответов",
    )
    is_required = models.BooleanField(
        default=True,
        verbose_name="Обязательный",
    )

    class Meta:
        verbose_name = "Вопрос опроса"
        verbose_name_plural = "Вопросы опросов"
        db_table = "survey_questions"
        ordering = ["order"]

    def __str__(self):
        return f"Вопрос {self.order}: {self.question_text[:50]}"


class SurveyAnswer(UUIDModel):
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Опрос",
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="survey_answers",
        verbose_name="Пользователь",
    )
    answers = models.JSONField(
        default=dict,
        verbose_name="Ответы",
    )
    submitted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Отправлено",
    )

    class Meta:
        verbose_name = "Ответ на опрос"
        verbose_name_plural = "Ответы на опросы"
        db_table = "survey_answers"

    def __str__(self):
        return f"Ответ {self.user.phone} на {self.survey.title}"