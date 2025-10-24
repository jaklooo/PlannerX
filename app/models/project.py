"""Project model."""
from datetime import datetime
from app import db


class Project(db.Model):
    """Project model - for organizing tasks."""

    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    color = db.Column(db.String(7), default="#3B82F6")  # Hex color
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="projects")
    tasks = db.relationship("Task", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project {self.name}>"

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "color": self.color,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
