"""Manually trigger daily digest for testing."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from app.tasks.daily_digest import send_daily_digests


def main():
    """Run daily digest job manually."""
    app = create_app("development")
    
    print("📧 Running daily digest job manually...")
    print("=" * 50)
    
    send_daily_digests(app)
    
    print("=" * 50)
    print("✅ Digest job completed")


if __name__ == "__main__":
    main()
