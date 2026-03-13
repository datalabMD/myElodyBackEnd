from datetime import datetime

from ninja import Router, Schema, Query
from pydantic import Field

router = Router()


class SurveySchema(Schema):
    id: str
    title: str
    description: str = ""
    reward_bonus: float
    is_available: bool
    is_completed: bool
    starts_at: str
    ends_at: str


class SubmitSurveySchema(Schema):
    answers: dict


class SubmitSurveyResponseSchema(Schema):
    success: bool
    bonus_awarded: float
    message: str


class PaginatedResponse(Schema):
    items: list
    total: int
    page: int
    pages: int


@router.get("", response=PaginatedResponse)
def get_surveys(request, page: int = 1, limit: int = 20):
    """Get available surveys"""
    from apps.surveys.models import Survey, SurveyAnswer
    from datetime import date
    
    today = date.today()
    completed_ids = SurveyAnswer.objects.filter(user=request.user).values_list("survey_id", flat=True)
    
    queryset = Survey.objects.filter(
        is_active=True,
        starts_at__lte=today,
        ends_at__gte=today
    ).exclude(id__in=completed_ids)
    
    total = queryset.count()
    pages = (total + limit - 1) // limit
    offset = (page - 1) * limit
    
    items = [
        SurveySchema(
            id=str(s.id),
            title=s.title,
            description=s.description or "",
            reward_bonus=float(s.reward_bonus),
            is_available=True,
            is_completed=False,
            starts_at=str(s.starts_at),
            ends_at=str(s.ends_at),
        )
        for s in queryset[offset:offset + limit]
    ]
    
    return PaginatedResponse(items=items, total=total, page=page, pages=pages)


@router.post("/{survey_id}/submit", response=SubmitSurveyResponseSchema)
def submit_survey(request, survey_id: str, data: SubmitSurveySchema):
    """Submit survey answers"""
    from apps.surveys.models import Survey, SurveyAnswer
    from django.shortcuts import get_object_or_404
    from django.utils import timezone
    
    survey = get_object_or_404(Survey, id=survey_id, is_active=True)
    
    already_completed = SurveyAnswer.objects.filter(
        survey=survey, user=request.user
    ).exists()
    
    if already_completed:
        return SubmitSurveyResponseSchema(
            success=False, bonus_awarded=0, message="Опрос уже пройден"
        )
    
    answer = SurveyAnswer.objects.create(
        survey=survey,
        user=request.user,
        answers=data.answers
    )
    
    bonus_awarded = 0
    if survey.reward_bonus > 0:
        from apps.loyalty.models import BonusLedger
        BonusLedger.objects.create(
            user=request.user,
            type="bonus",
            amount=survey.reward_bonus,
            description=f"Опрос: {survey.title}"
        )
        bonus_awarded = float(survey.reward_bonus)
    
    return SubmitSurveyResponseSchema(
        success=True,
        bonus_awarded=bonus_awarded,
        message="Спасибо за участие!"
    )