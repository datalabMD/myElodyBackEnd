from datetime import timedelta
from random import randint

import redis
from django.conf import settings
from ninja import Router, Schema
from pydantic import Field

router = Router()


class RequestLoginSchema(Schema):
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{6,14}$")


class RequestLoginResponseSchema(Schema):
    success: bool
    message: str
    expires_in: int = 300


class LoginSchema(Schema):
    phone: str
    code: str = Field(..., min_length=6, max_length=6)


class UserSchema(Schema):
    id: str
    phone: str
    email: str | None = None


class LoginResponseSchema(Schema):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 900
    user: UserSchema


class PasswordResetRequestSchema(Schema):
    phone: str


class VerifyOtpSchema(Schema):
    phone: str
    code: str = Field(..., min_length=6, max_length=6)


class VerifyOtpResponseSchema(Schema):
    valid: bool
    temp_token: str | None = None


class ResetPasswordSchema(Schema):
    temp_token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)


class RefreshTokenSchema(Schema):
    refresh_token: str


class RefreshTokenResponseSchema(Schema):
    access_token: str
    refresh_token: str
    expires_in: int = 900


def get_redis_client():
    return redis.Redis.from_url(settings.CELERY_BROKER_URL, decode_responses=True)


def generate_otp():
    return str(randint(100000, 999999))


def send_sms(phone: str, code: str):
    print(f"[SMS] To: {phone}, Code: {code}")
    return True


@router.post("/request-login", response=RequestLoginResponseSchema)
def request_login(request, data: RequestLoginSchema):
    """Request OTP code for login"""
    redis_client = get_redis_client()
    
    otp = generate_otp()
    key = f"otp:{data.phone}:login"
    
    redis_client.setex(key, 300, otp)
    redis_client.setex(f"otp_attempts:{data.phone}:login", 3600, "0")
    
    send_sms(data.phone, otp)
    
    return RequestLoginResponseSchema(
        success=True,
        message="Код отправлен",
        expires_in=300
    )


@router.post("/login", response=LoginResponseSchema)
def login(request, data: LoginSchema):
    """Login with OTP code"""
    from apps.users.models import User
    from rest_framework_simplejwt.tokens import RefreshToken
    
    redis_client = get_redis_client()
    key = f"otp:{data.phone}:login"
    
    stored_otp = redis_client.get(key)
    
    if not stored_otp:
        return {"error": "Код истёк"}, 401
    
    if stored_otp != data.code:
        attempts_key = f"otp_attempts:{data.phone}:login"
        attempts = int(redis_client.get(attempts_key) or 0) + 1
        redis_client.setex(attempts_key, 3600, str(attempts))
        
        if attempts >= 3:
            redis_client.delete(key)
            return {"error": "Превышено количество попыток"}, 429
        
        return {"error": "Неверный код"}, 401
    
    redis_client.delete(key)
    redis_client.delete(f"otp_attempts:{data.phone}:login")
    
    user, created = User.objects.get_or_create(
        phone=data.phone,
        defaults={"email": f"{data.phone}@elody-farm.md"}
    )
    
    from apps.users.models import CustomerProfile
    if created:
        CustomerProfile.objects.create(user=user)
    
    refresh = RefreshToken.for_user(user)
    
    return LoginResponseSchema(
        access_token=str(refresh.access_token),
        refresh_token=str(refresh),
        expires_in=900,
        user=UserSchema(id=str(user.id), phone=user.phone, email=user.email)
    )


@router.post("/request-password-reset", response=RequestLoginResponseSchema)
def request_password_reset(request, data: PasswordResetRequestSchema):
    """Request password reset OTP"""
    redis_client = get_redis_client()
    
    otp = generate_otp()
    key = f"otp:{data.phone}:password_reset"
    
    redis_client.setex(key, 300, otp)
    send_sms(data.phone, otp)
    
    return RequestLoginResponseSchema(
        success=True,
        message="Код отправлен",
        expires_in=300
    )


@router.post("/verify-otp", response=VerifyOtpResponseSchema)
def verify_otp(request, data: VerifyOtpSchema):
    """Verify OTP code"""
    redis_client = get_redis_client()
    
    purpose = "password_reset" if "password" in str(request) else "login"
    key = f"otp:{data.phone}:{purpose}"
    
    stored_otp = redis_client.get(key)
    
    if stored_otp == data.code:
        redis_client.delete(key)
        import uuid
        temp_token = str(uuid.uuid4())
        redis_client.setex(f"temp_token:{temp_token}", 600, data.phone)
        
        return VerifyOtpResponseSchema(valid=True, temp_token=temp_token)
    
    return VerifyOtpResponseSchema(valid=False)


@router.post("/reset-password")
def reset_password(request, data: ResetPasswordSchema):
    """Reset password with temp token"""
    from apps.users.models import User
    
    redis_client = get_redis_client()
    phone = redis_client.get(f"temp_token:{data.temp_token}")
    
    if not phone:
        return {"error": "Токен истёк"}, 401
    
    if data.new_password != data.confirm_password:
        return {"error": "Пароли не совпадают"}, 400
    
    try:
        user = User.objects.get(phone=phone)
        user.set_password(data.new_password)
        user.save()
        
        redis_client.delete(f"temp_token:{data.temp_token}")
        
        return {"success": True, "message": "Пароль изменён"}
    except User.DoesNotExist:
        return {"error": "Пользователь не найден"}, 404


@router.post("/logout")
def logout(request):
    """Logout user"""
    return {"success": True, "message": "Вышел"}


@router.post("/refresh", response=RefreshTokenResponseSchema)
def refresh_token(request, data: RefreshTokenSchema):
    """Refresh access token"""
    from rest_framework_simplejwt.tokens import RefreshToken
    
    try:
        refresh = RefreshToken(data.refresh_token)
        user = refresh.user
        
        new_refresh = RefreshToken.for_user(user)
        
        return RefreshTokenResponseSchema(
            access_token=str(new_refresh.access_token),
            refresh_token=str(new_refresh),
            expires_in=900
        )
    except Exception as e:
        return {"error": "Неверный токен"}, 401