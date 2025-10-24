"""SMS service via Twilio."""
import logging
from flask import current_app

logger = logging.getLogger(__name__)


def send_sms(to: str, text: str) -> bool:
    """
    Send an SMS via Twilio.
    
    Args:
        to: Recipient phone number (E.164 format)
        text: Message text
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        account_sid = current_app.config.get("TWILIO_ACCOUNT_SID")
        auth_token = current_app.config.get("TWILIO_AUTH_TOKEN")
        from_number = current_app.config.get("TWILIO_FROM_NUMBER")

        if not all([account_sid, auth_token, from_number]):
            logger.info("Twilio not configured, SMS not sent")
            return False

        # Import Twilio client (optional dependency)
        try:
            from twilio.rest import Client
        except ImportError:
            logger.warning("Twilio SDK not installed, SMS not sent")
            return False

        client = Client(account_sid, auth_token)
        message = client.messages.create(body=text, from_=from_number, to=to)

        logger.info(f"SMS sent to {to}, SID: {message.sid}")
        return True

    except Exception as e:
        logger.error(f"Failed to send SMS to {to}: {e}")
        return False
