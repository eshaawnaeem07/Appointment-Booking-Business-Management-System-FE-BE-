# Import tasks so Celery autodiscover can find them
from app.workers.tasks import mark_no_show

__all__ = ["mark_no_show"]
