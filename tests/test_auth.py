"""Tests for authentication."""
import pytest
from app.auth.firebase import verify_id_token


def test_verify_dev_token(app):
    """Test verification of development token."""
    with app.app_context():
        token_data = verify_id_token("dev_testuser:test@example.com")
        
        assert token_data["uid"] == "testuser"
        assert token_data["email"] == "test@example.com"
        assert token_data["email_verified"] is True


def test_require_auth_decorator(client, auth_headers):
    """Test @require_auth decorator."""
    # Should fail without auth
    response = client.get("/tasks/")
    assert response.status_code == 401
    
    # Should succeed with auth
    response = client.get("/tasks/", headers=auth_headers)
    assert response.status_code == 200


def test_user_creation_on_first_login(client):
    """Test that user is created on first authenticated request."""
    from app.models.user import User
    from app import db
    
    headers = {
        "Authorization": "Bearer dev_newuser:newuser@example.com",
        "Content-Type": "application/json"
    }
    
    # Make authenticated request
    response = client.get("/tasks/", headers=headers)
    
    # Check user was created
    user = User.query.filter_by(uid="newuser").first()
    assert user is not None
    assert user.email == "newuser@example.com"


def test_invalid_token_format(client):
    """Test that invalid token format is rejected."""
    headers = {
        "Authorization": "Bearer invalid_token_format"
    }
    
    response = client.get("/tasks/", headers=headers)
    assert response.status_code == 401
