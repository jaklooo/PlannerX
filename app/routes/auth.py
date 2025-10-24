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
    """Landing page with login."""
    return render_template("login.html", 
                         firebase_api_key=config.FIREBASE_API_KEY,
                         firebase_auth_domain=f"{config.FIREBASE_PROJECT_ID}.firebaseapp.com",
                         firebase_project_id=config.FIREBASE_PROJECT_ID,
                         firebase_storage_bucket=f"{config.FIREBASE_PROJECT_ID}.firebasestorage.app",
                         firebase_messaging_sender_id=config.FIREBASE_MESSAGING_SENDER_ID,
                         firebase_app_id=config.FIREBASE_APP_ID)


@auth_bp.route("/login", methods=["GET"])
def login():
    """Login page."""
    return render_template("login.html",
                         firebase_api_key=config.FIREBASE_API_KEY,
                         firebase_auth_domain=f"{config.FIREBASE_PROJECT_ID}.firebaseapp.com",
                         firebase_project_id=config.FIREBASE_PROJECT_ID,
                         firebase_storage_bucket=f"{config.FIREBASE_PROJECT_ID}.firebasestorage.app",
                         firebase_messaging_sender_id=config.FIREBASE_MESSAGING_SENDER_ID,
                         firebase_app_id=config.FIREBASE_APP_ID)


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
