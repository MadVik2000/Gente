"""
This file contains all the configuration for celery scheduler
"""
import os
from datetime import timedelta

from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gente.settings")

app = Celery("gente")

if settings.CELERY_TIMEZONE:
    app.conf.enable_utc = False
    app.conf.update(timezone=settings.CELERY_TIMEZONE)

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "check-chat-queue-every-two-seconds": {
        "task": "chats.tasks.remove_expired_users",
        "schedule": timedelta(seconds=2),
    }
}
