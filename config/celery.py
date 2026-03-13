"""Celery configuration for Elody-Farm Loyalty project."""

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("elody_farm")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "cleanup-expired-otp": {
        "task": "tasks.authn.cleanup_expired_otp",
        "schedule": 300.0,
    },
    "process-expired-bonuses": {
        "task": "tasks.loyalty.process_expired_bonuses",
        "schedule": crontab(hour=2, minute=0),
    },
    "send-birthday-bonuses": {
        "task": "tasks.loyalty.send_birthday_bonuses",
        "schedule": crontab(hour=3, minute=0),
    },
    "sync-erp-transactions": {
        "task": "tasks.transactions.sync_erp_transactions",
        "schedule": 900.0,
    },
    "cleanup-old-sessions": {
        "task": "tasks.users.cleanup_old_sessions",
        "schedule": crontab(hour=1, minute=0, day_of_week="sunday"),
    },
}