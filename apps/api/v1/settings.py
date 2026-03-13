from ninja import Router, Schema

router = Router()


class NotificationSettingsSchema(Schema):
    push_enabled: bool = True
    email_enabled: bool = True
    sms_enabled: bool = False
    marketing_enabled: bool = True
    bonus_notifications: bool = True


class SettingsSchema(Schema):
    language: str = "ru"
    notifications: NotificationSettingsSchema


class LanguageSchema(Schema):
    language: str


class NotificationSettingsUpdateSchema(Schema):
    push_enabled: bool | None = None
    email_enabled: bool | None = None
    sms_enabled: bool | None = None
    marketing_enabled: bool | None = None
    bonus_notifications: bool | None = None


@router.get("", response=SettingsSchema)
def get_settings(request):
    """Get user settings"""
    from apps.settings.models import UserSettings
    from apps.notifications.models import UserNotificationSettings
    
    try:
        settings = UserSettings.objects.get(user=request.user)
        language = settings.language
    except UserSettings.DoesNotExist:
        language = "ru"
    
    try:
        notif_settings = UserNotificationSettings.objects.get(user=request.user)
        notifications = NotificationSettingsSchema(
            push_enabled=notif_settings.push_enabled,
            email_enabled=notif_settings.email_enabled,
            sms_enabled=notif_settings.sms_enabled,
            marketing_enabled=notif_settings.marketing_enabled,
            bonus_notifications=notif_settings.bonus_notifications,
        )
    except UserNotificationSettings.DoesNotExist:
        notifications = NotificationSettingsSchema()
    
    return SettingsSchema(language=language, notifications=notifications)


@router.post("/language")
def update_language(request, data: LanguageSchema):
    """Update language"""
    from apps.settings.models import UserSettings
    
    settings, _ = UserSettings.objects.get_or_create(user=request.user)
    settings.language = data.language
    settings.save()
    
    return {"success": True, "language": data.language}


@router.post("/notifications")
def update_notifications(request, data: NotificationSettingsUpdateSchema):
    """Update notification settings"""
    from apps.notifications.models import UserNotificationSettings
    
    settings, _ = UserNotificationSettings.objects.get_or_create(user=request.user)
    
    if data.push_enabled is not None:
        settings.push_enabled = data.push_enabled
    if data.email_enabled is not None:
        settings.email_enabled = data.email_enabled
    if data.sms_enabled is not None:
        settings.sms_enabled = data.sms_enabled
    if data.marketing_enabled is not None:
        settings.marketing_enabled = data.marketing_enabled
    if data.bonus_notifications is not None:
        settings.bonus_notifications = data.bonus_notifications
    
    settings.save()
    
    return {"success": True}


@router.delete("/account")
def delete_account(request):
    """Delete user account"""
    user = request.user
    user.is_active = False
    user.save()
    
    return {"success": True, "message": "Аккаунт удалён"}