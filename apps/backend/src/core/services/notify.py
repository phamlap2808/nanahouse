from __future__ import annotations

import smtplib
from email.mime.text import MIMEText
from typing import Optional
import httpx
import logging

from core.config import settings


logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, html_body: str) -> bool:
    if not settings.smtp_host or not settings.smtp_user or not settings.smtp_password:
        logger.warning("Email sending skipped: SMTP config missing (SMTP_HOST/USER/PASSWORD)")
        return False
    msg = MIMEText(html_body, "html")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to_email
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_from, [to_email], msg.as_string())
        return True
    except Exception as exc:
        logger.error("Email sending failed to %s: %s", to_email, exc)
        return False


def send_sms(to_phone: str, message: str) -> bool:
    if not settings.sms_api_base_url or not settings.sms_api_key:
        logger.warning("SMS sending skipped: SMS config missing (SMS_API_BASE_URL/SMS_API_KEY)")
        return False
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.post(
                f"{settings.sms_api_base_url}/send",
                headers={"Authorization": f"Bearer {settings.sms_api_key}"},
                json={"to": to_phone, "message": message},
            )
            if 200 <= resp.status_code < 300:
                return True
            logger.error("SMS sending failed to %s: status=%s body=%s", to_phone, resp.status_code, resp.text)
            return False
    except Exception as exc:
        logger.error("SMS sending exception to %s: %s", to_phone, exc)
        return False


