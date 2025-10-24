"""Authentication routes."""
from flask import Blueprint, render_template, jsonify, request
from app.auth.firebase import verify_id_token
from app.models.user import User
from app import db
from app.config import get_config

auth_bp = Blueprint("auth", __name__)
config = get_config()


@auth_bp.route("/")
def index():
    """Landing page - redirect to dashboard."""
    from flask import redirect
    return redirect("/dashboard/")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Logout - clear session."""
    from flask import session
    session.clear()
    return "", 204


@auth_bp.route("/api/verify-token", methods=["POST"])
def verify_token():
    """Verify Firebase token and create/get user."""
    data = request.get_json()
    token = data.get("token")
    
    if not token:
        return jsonify({"error": "Token required"}), 400
    
    try:
        # Verify token
        user_data = verify_id_token(token)
        
        # Get or create user
        user = User.query.filter_by(uid=user_data["uid"]).first()
        if not user:
            user = User(
                uid=user_data["uid"],
                email=user_data.get("email", ""),
            )
            db.session.add(user)
            db.session.commit()
        
        return jsonify({
            "success": True,
            "user": {
                "id": user.id,
                "email": user.email,
                "uid": user.uid,
            }
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 401
