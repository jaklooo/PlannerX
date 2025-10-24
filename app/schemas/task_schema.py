"""Task validation schemas."""
from datetime import datetime
from typing import Optional


class TaskSchema:
    """Task validation schema."""
    
    @staticmethod
    def validate_create(data: dict) -> dict:
        """Validate task creation data."""
        errors = []
        
        if not data.get("title"):
            errors.append("Title is required")
        
        if data.get("priority") and data["priority"] not in ["LOW", "MEDIUM", "HIGH"]:
            errors.append("Priority must be LOW, MEDIUM, or HIGH")
        
        if data.get("status") and data["status"] not in ["TODO", "DOING", "DONE"]:
            errors.append("Status must be TODO, DOING, or DONE")
        
        if errors:
            raise ValueError("; ".join(errors))
        
        return data
    
    @staticmethod
    def validate_update(data: dict) -> dict:
        """Validate task update data."""
        if data.get("priority") and data["priority"] not in ["LOW", "MEDIUM", "HIGH"]:
            raise ValueError("Priority must be LOW, MEDIUM, or HIGH")
        
        if data.get("status") and data["status"] not in ["TODO", "DOING", "DONE"]:
            raise ValueError("Status must be TODO, DOING, or DONE")
        
        return data
