from datetime import date

from ninja import Router, Schema
from pydantic import Field

router = Router()


class ProfileSchema(Schema):
    id: str
    phone: str
    email: str | None = None
    first_name: str = ""
    last_name: str = ""
    middle_name: str = ""
    birth_date: date | None = None
    gender: str = ""
    avatar_url: str | None = None
    loyalty_tier: str = "bronze"
    registered_at: str


class UpdateProfileSchema(Schema):
    first_name: str = ""
    last_name: str = ""
    middle_name: str = ""
    birth_date: date | None = None
    gender: str = ""


class AvatarResponseSchema(Schema):
    avatar_url: str


def get_user_profile(user):
    profile = user.profile
    return ProfileSchema(
        id=str(user.id),
        phone=user.phone,
        email=user.email,
        first_name=profile.first_name,
        last_name=profile.last_name,
        middle_name=profile.middle_name,
        birth_date=profile.birth_date,
        gender=profile.gender,
        avatar_url=user.email if profile.avatar else None,
        loyalty_tier=profile.loyalty_tier,
        registered_at=profile.registered_at.isoformat()
    )


@router.get("", response=ProfileSchema)
def get_profile(request):
    """Get current user profile"""
    return get_user_profile(request.user)


@router.patch("", response=ProfileSchema)
def update_profile(request, data: UpdateProfileSchema):
    """Update current user profile"""
    profile = request.user.profile
    
    if data.first_name is not None:
        profile.first_name = data.first_name
    if data.last_name is not None:
        profile.last_name = data.last_name
    if data.middle_name is not None:
        profile.middle_name = data.middle_name
    if data.birth_date is not None:
        profile.birth_date = data.birth_date
    if data.gender is not None:
        profile.gender = data.gender
    
    profile.save()
    
    return get_user_profile(request.user)


@router.post("/avatar", response=AvatarResponseSchema)
def upload_avatar(request):
    """Upload avatar"""
    return AvatarResponseSchema(avatar_url="/media/avatars/placeholder.jpg")