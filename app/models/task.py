"""Task model."""
from datetime import datetime
from app import db


class Task(db.Model):
    """Task model."""

    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=True)
    
    title = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    due_at = db.Column(db.DateTime, nullable=True, index=True)
    
    # LOW, MEDIUM, HIGH
    priority = db.Column(db.String(20), default="MEDIUM")
    
    # TODO, DOING, DONE
    status = db.Column(db.String(20), default="TODO", index=True)
    
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="tasks")
    project = db.relationship("Project", back_populates="tasks")

    def __repr__(self):
        return f"<Task {self.title}>"

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "title": self.title,
            "notes": self.notes,
            "due_at": self.due_at.isoformat() if self.due_at else None,
            "priority": self.priority,
            "status": self.status,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
