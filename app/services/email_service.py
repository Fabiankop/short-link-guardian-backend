from app.core.celery_app import send_email_task

async def send_email_background(to_email: str, subject: str, body: str):
    send_email_task.delay(to_email, subject, body)
