"""Send a test email to verify SMTP configuration."""
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables BEFORE importing app
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from app.services.emailer import send_email


def send_test_email(recipient: str):
    """Send a test email."""
    app = create_app("development")
    
    with app.app_context():
        html = """
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h1 style="color: #3B82F6;">✅ PlannerX Test Email</h1>
            <p>Ak vidíte túto správu, SMTP konfigurácia funguje správne!</p>
            <p style="color: #666; font-size: 14px;">
                Tento email bol odoslaný z <strong>PlannerX</strong> aplikácie.
            </p>
        </body>
        </html>
        """
        
        success = send_email(
            to=recipient,
            subject="[PlannerX] Test Email",
            html=html
        )
        
        if success:
            print(f"✅ Test email sent successfully to {recipient}")
        else:
            print(f"❌ Failed to send test email to {recipient}")
            print("   Check your SMTP configuration in .env file")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python send_test_email.py <recipient@example.com>")
        sys.exit(1)
    
    recipient = sys.argv[1]
    send_test_email(recipient)
