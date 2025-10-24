"""Settings routes."""
from flask import Blueprint, render_template, request, jsonify, g

from app import db
from app.auth.firebase import require_auth

bp = Blueprint("settings", __name__)


@bp.route("/")
@require_auth
def index():
    """Settings page."""
    user = g.current_user
    
    if request.headers.get("Accept") == "application/json":
        return jsonify(user.to_dict())
    
    return render_template("settings.html", user=user)


@bp.route("/update", methods=["POST", "PUT"])
@require_auth
def update():
    """Update user settings."""
    user = g.current_user
    data = request.get_json() if request.is_json else request.form
    
    if "digest_enabled" in data:
        user.digest_enabled = str(data["digest_enabled"]).lower() in ["true", "1", "yes"]
    
    if "digest_time" in data:
        user.digest_time = data["digest_time"]
    
    if "sms_enabled" in data:
        user.sms_enabled = str(data["sms_enabled"]).lower() in ["true", "1", "yes"]
    
    if "phone_number" in data:
        user.phone_number = data["phone_number"]
    
    db.session.commit()
    
    return jsonify(user.to_dict())
