from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import redis


@shared_task
def cleanup_expired_otp():
    """Clean up expired OTP codes"""
    from django.conf import settings
    import redis
    
    r = redis.Redis.from_url(settings.CELERY_BROKER_URL)
    
    keys = r.keys("otp:*")
    for key in keys:
        ttl = r.ttl(key)
        if ttl == -1:
            r.delete(key)
    
    return f"Cleaned up {len(keys)} expired OTP codes"


@shared_task
def process_expired_bonuses():
    """Process expired bonuses"""
    from apps.loyalty.models import BonusLedger
    from django.conf import settings
    
    expiration_days = 365
    
    expired_bonuses = BonusLedger.objects.filter(
        type="earned",
        expires_at__lte=timezone.now(),
    )
    
    count = 0
    for bonus in expired_bonuses:
        BonusLedger.objects.create(
            user=bonus.user,
            type="expired",
            amount=bonus.amount,
            description=f"Сгоревшие бонусы",
        )
        count += 1
    
    return f"Processed {count} expired bonuses"


@shared_task
def send_birthday_bonuses():
    """Send birthday bonuses"""
    from apps.users.models import CustomerProfile
    from apps.loyalty.models import BonusLedger
    from datetime import date
    
    today = date.today()
    profiles = CustomerProfile.objects.filter(
        birth_date__month=today.month,
        birth_date__day=today.day,
        user__is_active=True
    )
    
    bonus_amount = 50
    
    for profile in profiles:
        BonusLedger.objects.create(
            user=profile.user,
            type="bonus",
            amount=bonus_amount,
            description="Бонус ко дню рождения",
        )
    
    return f"Sent birthday bonuses to {profiles.count()} users"


@shared_task
def sync_erp_transactions():
    """Sync transactions from ERP (placeholder)"""
    return "No new transactions to sync"


@shared_task
def cleanup_old_sessions():
    """Clean up old sessions"""
    from django.contrib.sessions.models import Session
    
    expired = Session.objects.filter(expire_date__lt=timezone.now())
    count = expired.count()
    expired.delete()
    
    return f"Cleaned up {count} expired sessions"