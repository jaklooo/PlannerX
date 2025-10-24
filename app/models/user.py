"""User model."""
from datetime import datetime
from app import db


class User(db.Model):
    """User model - linked to Firebase Auth."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(128), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), nullable=False)
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Settings
    digest_enabled = db.Column(db.Boolean, default=True)
    digest_time = db.Column(db.String(5), default="07:00")  # HH:MM format
    sms_enabled = db.Column(db.Boolean, default=False)
    phone_number = db.Column(db.String(20), nullable=True)

    # Relationships
    projects = db.relationship("Project", back_populates="user", cascade="all, delete-orphan")
    tasks = db.relationship("Task", back_populates="user", cascade="all, delete-orphan")
    events = db.relationship("Event", back_populates="user", cascade="all, delete-orphan")
    contacts = db.relationship("Contact", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "uid": self.uid,
            "email": self.email,
            "email_verified": self.email_verified,
            "digest_enabled": self.digest_enabled,
            "digest_time": self.digest_time,
            "sms_enabled": self.sms_enabled,
            "phone_number": self.phone_number,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
