"""Application configuration."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent


class BaseConfig:
    """Base configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Fallback to SQLite for development
        db_path = BASE_DIR / "data" / "db.sqlite3"
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"

    # Email
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_STARTTLS = os.getenv("SMTP_STARTTLS", "true").lower() == "true"
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM = os.getenv("EMAIL_FROM", "PlannerX <no-reply@example.com>")

    # Firebase
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "")
    FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY", "")
    FIREBASE_AUTH_EMULATOR_HOST = os.getenv("FIREBASE_AUTH_EMULATOR_HOST", "")
    FIREBASE_MESSAGING_SENDER_ID = os.getenv("FIREBASE_MESSAGING_SENDER_ID", "")
    FIREBASE_APP_ID = os.getenv("FIREBASE_APP_ID", "")
    FIREBASE_ALLOWED_ISSUER = os.getenv(
        "FIREBASE_ALLOWED_ISSUER",
        f"https://securetoken.google.com/{os.getenv('FIREBASE_PROJECT_ID', '')}",
    )

    # Twilio (SMS)
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER", "")

    # Scheduler
    DIGEST_HOUR = int(os.getenv("DIGEST_HOUR", "7"))
    DIGEST_MINUTE = int(os.getenv("DIGEST_MINUTE", "0"))
    TIMEZONE = os.getenv("TIMEZONE", "Europe/Prague")

    # RSS News
    RSS_CACHE_FILE = BASE_DIR / "data" / "news_cache.json"
    RSS_FEEDS_FILE = BASE_DIR / "data" / "rss_feeds.yaml"
    NAME_DAYS_FILE = BASE_DIR / "data" / "name_days.sk.json"

    # OpenAI API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG = True
    TESTING = False


class ProductionConfig(BaseConfig):
    """Production configuration."""

    DEBUG = False
    TESTING = False


class TestingConfig(BaseConfig):
    """Testing configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


def get_config(config_name="development"):
    """Get configuration object by name."""
    configs = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }
    return configs.get(config_name, DevelopmentConfig)
