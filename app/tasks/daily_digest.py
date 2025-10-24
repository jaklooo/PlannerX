"""Daily digest scheduled task."""
import logging
from flask import Flask

from app.models.user import User
from app.services.digest import generate_digest_data, render_digest_html, should_send_digest
from app.services.emailer import send_email
from app.services.sms import send_sms

logger = logging.getLogger(__name__)


def send_daily_digests(app: Flask):
    """
    Send daily digest emails to all users.
    
    This function is called by APScheduler.
    """
    with app.app_context():
        logger.info("Starting daily digest job")
        
        users = User.query.filter_by(digest_enabled=True).all()
        
        success_count = 0
        error_count = 0
        
        for user in users:
            try:
                if not should_send_digest(user):
                    logger.debug(f"Skipping digest for {user.email}")
                    continue
                
                # Generate digest data
                digest_data = generate_digest_data(user)
                
                # Render HTML
                html = render_digest_html(digest_data)
                
                # Send email
                subject = f"Dobrý deň! Váš denný prehľad pre {digest_data['today'].strftime('%d.%m.%Y')}"
                
                if send_email(user.email, subject, html):
                    success_count += 1
                    logger.info(f"Digest sent to {user.email}")
                    
                    # Send SMS if enabled
                    if user.sms_enabled and user.phone_number:
                        tasks_count = len(digest_data["tasks_today"])
                        events_count = len(digest_data["events_today"])
                        sms_text = f"PlannerX: Dnes máte {tasks_count} úloh a {events_count} udalostí."
                        send_sms(user.phone_number, sms_text)
                else:
                    error_count += 1
                    logger.error(f"Failed to send digest to {user.email}")
            
            except Exception as e:
                error_count += 1
                logger.error(f"Error sending digest to {user.email}: {e}", exc_info=True)
        
        logger.info(
            f"Daily digest job completed. "
            f"Success: {success_count}, Errors: {error_count}, Total users: {len(users)}"
        )
