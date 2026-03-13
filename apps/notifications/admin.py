from django.contrib import admin
from .models import Notification, UserNotificationSettings


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "title", "type", "is_read", "sent_at"]
    list_filter = ["type", "is_read", "sent_at"]
    search_fields = ["user__phone", "title"]


@admin.register(UserNotificationSettings)
class UserNotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ["user", "push_enabled", "email_enabled", "sms_enabled", "marketing_enabled"]