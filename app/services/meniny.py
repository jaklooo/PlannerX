"""Name days (meniny) lookup service."""
import json
import logging
from datetime import date
from pathlib import Path
from typing import List
from flask import current_app

logger = logging.getLogger(__name__)


def load_name_days() -> dict:
    """Load name days from JSON file."""
    try:
        file_path = Path(current_app.config.get("NAME_DAYS_FILE"))
        
        if not file_path.exists():
            logger.warning(f"Name days file not found: {file_path}")
            return {}
        
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    except Exception as e:
        logger.error(f"Failed to load name days: {e}")
        return {}


def get_name_day(target_date: date = None) -> List[str]:
    """
    Get names celebrating on a specific date.
    
    Args:
        target_date: Date to check (defaults to today)
    
    Returns:
        List of names celebrating on that date
    """
    if target_date is None:
        target_date = date.today()
    
    name_days = load_name_days()
    key = target_date.strftime("%m-%d")  # Format: "10-22"
    
    names = name_days.get(key, [])
    return names if isinstance(names, list) else [names]


def find_name_day(name: str) -> date | None:
    """
    Find the date when a specific name is celebrated.
    
    Args:
        name: Name to search for
    
    Returns:
        Date of celebration or None if not found
    """
    name_days = load_name_days()
    name_lower = name.lower()
    
    for date_key, names in name_days.items():
        names_list = names if isinstance(names, list) else [names]
        if any(n.lower() == name_lower for n in names_list):
            month, day = map(int, date_key.split("-"))
            return date(date.today().year, month, day)
    
    return None
