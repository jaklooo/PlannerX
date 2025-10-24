"""Calendar service for event recurrence and date calculations."""
from datetime import datetime, date, timedelta
from typing import List
from zoneinfo import ZoneInfo


def get_timezone() -> ZoneInfo:
    """Get the configured timezone."""
    return ZoneInfo("Europe/Prague")


def get_today(tz: ZoneInfo = None) -> date:
    """Get today's date in the configured timezone."""
    if tz is None:
        tz = get_timezone()
    return datetime.now(tz).date()


def get_week_range(target_date: date = None) -> tuple[date, date]:
    """
    Get the start and end dates of the week containing target_date.
    
    Args:
        target_date: Date to get week for (defaults to today)
    
    Returns:
        Tuple of (start_date, end_date) for the week (Monday to Sunday)
    """
    if target_date is None:
        target_date = get_today()
    
    # Get Monday of this week
    start = target_date - timedelta(days=target_date.weekday())
    # Get Sunday of this week
    end = start + timedelta(days=6)
    
    return start, end


def expand_recurring_events(events: List, start_date: date, end_date: date) -> List[dict]:
    """
    Expand recurring events to individual occurrences within a date range.
    
    Args:
        events: List of Event objects
        start_date: Start of date range
        end_date: End of date range
    
    Returns:
        List of expanded event dictionaries with actual dates
    """
    expanded = []
    
    for event in events:
        if event.repeat_rule == "NONE":
            # Single occurrence
            if start_date <= event.start_at.date() <= end_date:
                expanded.append({
                    "event": event,
                    "occurrence_date": event.start_at.date(),
                })
        
        elif event.repeat_rule == "DAILY":
            # Daily recurrence
            current = event.start_at.date()
            while current <= end_date:
                if current >= start_date:
                    expanded.append({
                        "event": event,
                        "occurrence_date": current,
                    })
                current += timedelta(days=1)
        
        elif event.repeat_rule == "WEEKLY":
            # Weekly recurrence (same day of week)
            current = event.start_at.date()
            while current <= end_date:
                if current >= start_date:
                    expanded.append({
                        "event": event,
                        "occurrence_date": current,
                    })
                current += timedelta(weeks=1)
        
        elif event.repeat_rule == "MONTHLY":
            # Monthly recurrence (same day of month)
            current = event.start_at.date()
            while current <= end_date:
                if current >= start_date:
                    expanded.append({
                        "event": event,
                        "occurrence_date": current,
                    })
                
                # Next month, same day
                try:
                    if current.month == 12:
                        current = current.replace(year=current.year + 1, month=1)
                    else:
                        current = current.replace(month=current.month + 1)
                except ValueError:
                    # Day doesn't exist in next month (e.g., Jan 31 -> Feb 31)
                    # Move to last day of next month
                    if current.month == 12:
                        next_month = 1
                        next_year = current.year + 1
                    else:
                        next_month = current.month + 1
                        next_year = current.year
                    
                    # Last day of next month
                    if next_month == 12:
                        last_day = 31
                    elif next_month in [4, 6, 9, 11]:
                        last_day = 30
                    elif next_month == 2:
                        # Check for leap year
                        if next_year % 4 == 0 and (next_year % 100 != 0 or next_year % 400 == 0):
                            last_day = 29
                        else:
                            last_day = 28
                    else:
                        last_day = 31
                    
                    current = date(next_year, next_month, last_day)
    
    return expanded


def is_overdue(due_date: datetime) -> bool:
    """Check if a task is overdue."""
    if due_date is None:
        return False
    now = datetime.now(get_timezone())
    return due_date < now
