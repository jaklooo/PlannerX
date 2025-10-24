"""Email service."""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, html: str, text: str = None) -> bool:
    """
    Send an email via SMTP.
    
    Args:
        to: Recipient email address
        subject: Email subject
        html: HTML body
        text: Plain text body (optional, will be extracted from HTML if not provided)
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        smtp_host = current_app.config.get("SMTP_HOST")
        smtp_port = current_app.config.get("SMTP_PORT")
        smtp_user = current_app.config.get("SMTP_USER")
        smtp_password = current_app.config.get("SMTP_PASSWORD")
        email_from = current_app.config.get("EMAIL_FROM")
        use_starttls = current_app.config.get("SMTP_STARTTLS", True)

        if not all([smtp_host, smtp_user, smtp_password]):
            logger.warning("SMTP not configured, email not sent")
            return False

        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = email_from
        msg["To"] = to

        # Plain text fallback
        if text:
            part1 = MIMEText(text, "plain")
            msg.attach(part1)

        # HTML content
        part2 = MIMEText(html, "html")
        msg.attach(part2)

        # Send email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.set_debuglevel(0)
            if use_starttls:
                server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        logger.info(f"Email sent to {to}: {subject}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to}: {e}")
        return False
