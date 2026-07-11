"""Celery application factory.

Queues:
  - default   : general tasks (resume parsing, etc.)
  - ai        : long-running AI / LLM tasks
  - email     : email sending tasks
  - cleanup   : periodic maintenance tasks

Beat schedule defines recurring jobs executed by Celery Beat.
"""

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "resume_ai",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.resume_tasks",
        "app.tasks.ai_tasks",
        "app.tasks.notification_tasks",
        "app.tasks.cleanup_tasks",
    ],
)

celery_app.conf.update(
    # Serialisation
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Results
    result_expires=3600,  # 1 hour
    task_ignore_result=False,
    # Worker behaviour
    worker_prefetch_multiplier=1,  # Fair dispatch for long tasks
    task_acks_late=True,  # Ack after task completes (safer)
    task_reject_on_worker_lost=True,
    # Retry defaults
    task_max_retries=3,
    task_default_retry_delay=60,  # 60 seconds between retries
    # Queue routing
    task_routes={
        "app.tasks.resume_tasks.*": {"queue": "default"},
        "app.tasks.ai_tasks.*": {"queue": "ai"},
        "app.tasks.notification_tasks.*": {"queue": "email"},
        "app.tasks.cleanup_tasks.*": {"queue": "cleanup"},
    },
    # Task always eager in testing (run synchronously)
    task_always_eager=settings.CELERY_TASK_ALWAYS_EAGER,
    task_eager_propagates=True,
    # Beat periodic schedule
    beat_schedule={
        "cleanup-expired-tokens-hourly": {
            "task": "app.tasks.cleanup_tasks.cleanup_expired_tokens",
            "schedule": crontab(minute=0),  # Every hour
        },
        "cleanup-orphaned-files-daily": {
            "task": "app.tasks.cleanup_tasks.cleanup_orphaned_files",
            "schedule": crontab(hour=2, minute=0),  # 2 AM daily
        },
        "send-weekly-career-summaries": {
            "task": "app.tasks.cleanup_tasks.trigger_weekly_summaries",
            "schedule": crontab(hour=9, minute=0, day_of_week=1),  # Monday 9 AM
        },
    },
)
