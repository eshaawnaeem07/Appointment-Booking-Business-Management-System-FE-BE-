from celery import Celery
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env", override=True)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0").strip().strip('"').strip("'")

celery_app = Celery(
    "bookingSystem",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.workers.tasks"],  # Explicitly include tasks
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,  # Acknowledge after task completes
    worker_prefetch_multiplier=1,  # Fetch one task at a time
    beat_schedule={
        "mark-overdue-no-shows-every-5-minutes": {
            "task": "app.workers.tasks.mark_overdue_no_shows",
            "schedule": 300.0,
        },
        "auto-complete-past-appointments-every-minute": {
            "task": "app.workers.tasks.auto_complete_past_appointments",
            "schedule": 60.0,  # Check every minute if any appointments should be completed
        },
    },
)

if sys.platform.startswith("win"):
    celery_app.conf.worker_pool = "solo"
    celery_app.conf.worker_concurrency = 1


# app.workers.celery_app.celery.
celery = celery_app
