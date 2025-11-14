"""
Celery application configuration.
Handles background tasks like email sending and payment processing.
"""
from celery import Celery
from src.config import settings

# Initialize Celery app with Redis as broker and backend
celery_app = Celery(
    "funny_how",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Celery Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    'expire-unpaid-bookings-every-15-minutes': {
        'task': 'expire_unpaid_bookings',
        'schedule': 900.0,  # 15 minutes in seconds (15 * 60)
        'options': {
            'expires': 60,  # Task expires after 60 seconds if not executed
        }
    },
}

# Auto-discover tasks from all modules
celery_app.autodiscover_tasks(
    [
        "src.tasks.email",
        "src.tasks.booking",
        "src.tasks.payment",
    ]
)


@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery."""
    print(f"Request: {self.request!r}")
    return "Debug task completed"
