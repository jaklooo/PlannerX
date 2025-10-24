"""Contact model."""
from datetime import datetime, date
from app import db


class Contact(db.Model):
    """Contact model - for tracking birthdays and name days."""

    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    
    # Store as DATE (without year if unknown)
    birthday_date = db.Column(db.Date, nullable=True)
    name_day_date = db.Column(db.Date, nullable=True)  # MM-DD format
    
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="contacts")

    def __repr__(self):
        return f"<Contact {self.name}>"

    def has_birthday_today(self, today: date = None) -> bool:
        """Check if contact has birthday today."""
        if not self.birthday_date:
            return False
        if today is None:
            today = date.today()
        return (
            self.birthday_date.month == today.month
            and self.birthday_date.day == today.day
        )

    def has_name_day_today(self, today: date = None) -> bool:
        """Check if contact has name day today."""
        if not self.name_day_date:
            return False
        if today is None:
            today = date.today()
        return (
            self.name_day_date.month == today.month
            and self.name_day_date.day == today.day
        )

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "birthday_date": self.birthday_date.isoformat() if self.birthday_date else None,
            "name_day_date": self.name_day_date.isoformat() if self.name_day_date else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
