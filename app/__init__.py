"""PlannerX Application Factory."""
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, g, jsonify
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Initialize extensions
db = SQLAlchemy()
scheduler = BackgroundScheduler()

logger = logging.getLogger(__name__)


def create_app(config_name="development"):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Load configuration
    from app.config import get_config

    config = get_config(config_name)
    app.config.from_object(config)
    
    # Disable strict slashes for all routes (allow URLs with or without trailing slash)
    app.url_map.strict_slashes = False

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import bp as dashboard_bp
    from app.routes.tasks import bp as tasks_bp
    from app.routes.events import bp as events_bp
    from app.routes.contacts import bp as contacts_bp
    from app.routes.settings import bp as settings_bp
    from app.routes.health import bp as health_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(tasks_bp, url_prefix="/tasks")
    app.register_blueprint(events_bp, url_prefix="/events")
    app.register_blueprint(contacts_bp, url_prefix="/contacts")
    app.register_blueprint(settings_bp, url_prefix="/settings")
    app.register_blueprint(health_bp)

    # Error handlers
    @app.errorhandler(401)
    def unauthorized(e):
        if "application/json" in g.get("accept_type", ""):
            return jsonify({"error": "Unauthorized"}), 401
        return "Unauthorized", 401

    @app.errorhandler(404)
    def not_found(e):
        if "application/json" in g.get("accept_type", ""):
            return jsonify({"error": "Not found"}), 404
        return "Not found", 404

    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Server error: {e}")
        if "application/json" in g.get("accept_type", ""):
            return jsonify({"error": "Internal server error"}), 500
        return "Internal server error", 500

    # Initialize scheduler
    if not scheduler.running:
        from app.tasks.daily_digest import send_daily_digests

        timezone = ZoneInfo(app.config.get("TIMEZONE", "Europe/Prague"))
        digest_hour = app.config.get("DIGEST_HOUR", 7)
        digest_minute = app.config.get("DIGEST_MINUTE", 0)

        scheduler.add_job(
            func=lambda: send_daily_digests(app),
            trigger=CronTrigger(
                hour=digest_hour, minute=digest_minute, timezone=timezone
            ),
            id="daily_digest",
            name="Send daily digest emails",
            replace_existing=True,
        )

        scheduler.start()
        logger.info(
            f"Scheduler started. Daily digest job scheduled for {digest_hour:02d}:{digest_minute:02d} {timezone}"
        )

    # Shutdown scheduler on app teardown
    import atexit

    atexit.register(lambda: scheduler.shutdown())

    # Create tables
    with app.app_context():
        db.create_all()

    return app
