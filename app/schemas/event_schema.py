"""Event validation schemas."""
from datetime import datetime


class EventSchema:
    """Event validation schema."""
    
    @staticmethod
    def validate_create(data: dict) -> dict:
        """Validate event creation data."""
        errors = []
        
        if not data.get("title"):
            errors.append("Title is required")
        
        if not data.get("start_at"):
            errors.append("Start time is required")
        
        if data.get("repeat_rule") and data["repeat_rule"] not in ["NONE", "DAILY", "WEEKLY", "MONTHLY"]:
            errors.append("Repeat rule must be NONE, DAILY, WEEKLY, or MONTHLY")
        
        if errors:
            raise ValueError("; ".join(errors))
        
        return data
    
    @staticmethod
    def validate_update(data: dict) -> dict:
        """Validate event update data."""
        if data.get("repeat_rule") and data["repeat_rule"] not in ["NONE", "DAILY", "WEEKLY", "MONTHLY"]:
            raise ValueError("Repeat rule must be NONE, DAILY, WEEKLY, or MONTHLY")
        
        return data
