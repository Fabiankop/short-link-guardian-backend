from celery import Celery
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

@celery_app.task
def send_email_task(to_email: str, subject: str, body: str):
    # Aquí iría la integración real con SendGrid, etc.
    print(f"[Celery] Sending email to {to_email}: {subject}\n{body}")
