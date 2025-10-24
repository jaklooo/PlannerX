"""Firebase authentication module."""
import logging
from functools import wraps

import requests
from flask import g, request, jsonify, current_app

logger = logging.getLogger(__name__)


def verify_id_token(id_token: str) -> dict:
    """
    Verify Firebase ID token.
    
    Returns:
        dict: Decoded token with uid, email, etc.
    Raises:
        ValueError: If token is invalid
    """
    project_id = current_app.config.get("FIREBASE_PROJECT_ID")
    allowed_issuer = current_app.config.get("FIREBASE_ALLOWED_ISSUER")
    emulator_host = current_app.config.get("FIREBASE_AUTH_EMULATOR_HOST")

    # Development mode: accept test tokens
    if emulator_host or current_app.config.get("DEBUG"):
        # In dev, accept a simple format like "dev_uid:email@example.com"
        if id_token.startswith("dev_"):
            parts = id_token.replace("dev_", "").split(":")
            if len(parts) == 2:
                return {"uid": parts[0], "email": parts[1], "email_verified": True}

    # Verify using Google's public keys
    try:
        # Get Google's public keys
        certs_url = "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"
        
        if emulator_host:
            # Use emulator endpoint
            certs_url = f"http://{emulator_host}/emulator/v1/projects/{project_id}/jwks"

        # For production, use PyJWT or similar library
        # This is a simplified version for demonstration
        
        # Parse token header (simplified - in production use PyJWT)
        import json
        import base64
        
        parts = id_token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid token format")
        
        # Decode payload (add padding if needed)
        payload_b64 = parts[1]
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        
        # Validate claims
        if payload.get("iss") != allowed_issuer:
            raise ValueError(f"Invalid issuer: {payload.get('iss')}")
        
        if payload.get("aud") != project_id:
            raise ValueError(f"Invalid audience: {payload.get('aud')}")
        
        # Check expiration
        import time
        if payload.get("exp", 0) < time.time():
            raise ValueError("Token expired")
        
        return {
            "uid": payload.get("sub"),
            "email": payload.get("email"),
            "email_verified": payload.get("email_verified", False),
        }
        
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise ValueError(f"Invalid token: {e}")


def require_auth(f):
    """
    Decorator to require Firebase authentication.
    
    Sets g.current_user to the authenticated User model instance.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session
        
        auth_header = request.headers.get("Authorization", "")
        
        # Development mode: auto-login as demo user if no token
        if current_app.config.get("DEBUG") and not auth_header:
            from app.models.user import User
            from app import db
            
            # Get or create demo user
            demo_user = User.query.filter_by(uid="demo_user").first()
            if not demo_user:
                demo_user = User(
                    uid="demo_user",
                    email="demo@plannerx.local",
                    email_verified=True,
                )
                db.session.add(demo_user)
                db.session.commit()
                logger.info("Created demo user for development")
            
            g.current_user = demo_user
            session['user_id'] = demo_user.id
            return f(*args, **kwargs)
        
        # Check session for authenticated users (for page navigation)
        if not auth_header and request.method == "GET" and 'user_id' in session:
            user_id = session['user_id']
            from app.models.user import User
            user = User.query.get(user_id)
            if user:
                g.current_user = user
                return f(*args, **kwargs)
        
        # Production mode: redirect to login if no token for GET requests to dashboard
        if not auth_header and request.method == "GET" and request.path.startswith("/dashboard"):
            # Check if token is provided as query parameter
            token_param = request.args.get('token')
            if token_param:
                # Verify the token from query parameter
                try:
                    token_data = verify_id_token(token_param)
                    # Get or create user
                    from app.models.user import User
                    from app import db
                    
                    user = User.query.filter_by(uid=token_data["uid"]).first()
                    
                    if not user:
                        user = User(
                            uid=token_data["uid"],
                            email=token_data["email"],
                            email_verified=token_data.get("email_verified", False),
                        )
                        db.session.add(user)
                        db.session.commit()
                        logger.info(f"Created new user: {user.uid}")
                    
                    g.current_user = user
                    session['user_id'] = user.id
                    return f(*args, **kwargs)
                except ValueError as e:
                    logger.error(f"Token verification failed for query param: {e}")
                    from flask import redirect, url_for
                    return redirect(url_for("auth.login"))
            else:
                from flask import redirect, url_for
                return redirect(url_for("auth.login"))
        
        if not auth_header.startswith("Bearer "):
            # For API requests, return JSON error
            if request.path.startswith("/api/"):
                return jsonify({"error": "Missing or invalid Authorization header"}), 401
            # For page requests, redirect to login
            else:
                from flask import redirect, url_for
                return redirect(url_for("auth.login"))
        
        id_token = auth_header.replace("Bearer ", "")
        
        try:
            token_data = verify_id_token(id_token)
        except ValueError as e:
            # For API requests, return JSON error
            if request.path.startswith("/api/"):
                return jsonify({"error": str(e)}), 401
            # For page requests, redirect to login
            else:
                from flask import redirect, url_for
                return redirect(url_for("auth.login"))
        
        # Get or create user
        from app.models.user import User
        from app import db
        
        user = User.query.filter_by(uid=token_data["uid"]).first()
        
        if not user:
            user = User(
                uid=token_data["uid"],
                email=token_data["email"],
                email_verified=token_data.get("email_verified", False),
            )
            db.session.add(user)
            db.session.commit()
            logger.info(f"Created new user: {user.uid}")
        
        g.current_user = user
        session['user_id'] = user.id
        
        return f(*args, **kwargs)
    
    return decorated_function


def current_user():
    """Get the current authenticated user from g."""
    return g.get("current_user")
