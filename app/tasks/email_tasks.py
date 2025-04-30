# app/tasks/email_tasks.py
from celery import shared_task
from app.services.email_service import EmailService
from app.dependencies import get_settings
import logging
logger = logging.getLogger(__name__)

settings = get_settings()

@shared_task
def send_account_verification_email(user_email: str, token: str):
    subject = "Verify Your Account"
    body = f"Click the link to verify your account: http://localhost/verify-email/{token}"
    EmailService().send_email(user_email, subject, body)

@shared_task
def send_account_locked_email(user_email: str):
    subject = "Account Locked"
    body = "Your account has been locked due to suspicious activity."
    EmailService().send_email(user_email, subject, body)

@shared_task
def send_account_unlocked_email(user_email: str):
    subject = "Account Unlocked"
    body = "Your account has been unlocked."
    EmailService().send_email(user_email, subject, body)

@shared_task
def send_role_upgrade_email(user_email: str, new_role: str):
    subject = "Role Upgraded"
    body = f"Congratulations! Your role has been upgraded to {new_role}."
    EmailService().send_email(user_email, subject, body)

@shared_task
def send_professional_status_upgrade_email(user_email: str):
    subject = "Professional Status Upgraded"
    body = "Your account has been upgraded to professional status."
    EmailService().send_email(user_email, subject, body)

@shared_task
def send_email_task(payload: dict):
    """
    Generic Celery task that receives payloads from Kafka and sends emails.
    """
    logger.info(f"📩 Received payload for email task: {payload}")

    email = payload.get("email")
    event = payload.get("event")
    token = payload.get("token")
    role = payload.get("role")

    subject = body = ""

    if event == "account.verification":
        subject = "Verify Your Account"
        body = f"Click to verify: http://localhost/verify-email/{token}"
    elif event == "account.lock":
        subject = "Account Locked"
        body = "Your account has been locked due to suspicious activity."
    elif event == "account.unlock":
        subject = "Account Unlocked"
        body = "Your account has been unlocked."
    elif event == "role.upgrade":
        subject = "Role Upgraded"
        body = f"Your role has been upgraded to {role}."
    elif event == "status.professional":
        subject = "Professional Status Upgraded"
        body = "You've been upgraded to professional status!"

    if subject and body:
        logger.info(f"📨 Sending email to {email} | Subject: {subject}")
        EmailService().send_email(email, subject, body)
    else:
        logger.warning(f"⚠️ Unknown email event type or missing data: {event}")
