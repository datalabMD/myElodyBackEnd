from django.contrib import admin
from .models import Survey, SurveyQuestion, SurveyAnswer


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ["title", "reward_bonus", "is_active", "starts_at", "ends_at"]
    list_filter = ["is_active"]
    search_fields = ["title"]


@admin.register(SurveyQuestion)
class SurveyQuestionAdmin(admin.ModelAdmin):
    list_display = ["survey", "order", "question_text", "question_type"]


@admin.register(SurveyAnswer)
class SurveyAnswerAdmin(admin.ModelAdmin):
    list_display = ["survey", "user", "submitted_at"]
    search_fields = ["user__phone"]