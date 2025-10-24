"""Daily digest generation service."""
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List
from flask import render_template

from app.models.user import User
from app.models.task import Task
from app.models.event import Event
from app.models.contact import Contact
from app.services.calendar import get_today, expand_recurring_events
from app.services.meniny import get_name_day
from app.services.news import fetch_news, summarize_news_with_ai

logger = logging.getLogger(__name__)


def generate_digest_data(user: User) -> Dict:
    """
    Generate digest data for a user.
    
    Args:
        user: User object
    
    Returns:
        Dictionary with all digest sections
    """
    today = get_today()
    tomorrow = today + timedelta(days=1)
    
    # Tasks for today
    tasks_today = (
        Task.query.filter_by(user_id=user.id)
        .filter(Task.status != "DONE")
        .filter(Task.due_at >= datetime.combine(today, datetime.min.time()))
        .filter(Task.due_at < datetime.combine(tomorrow, datetime.min.time()))
        .order_by(
            Task.priority.desc(),  # HIGH first
            Task.due_at.asc()
        )
        .all()
    )
    
    # Overdue tasks
    overdue_tasks = (
        Task.query.filter_by(user_id=user.id)
        .filter(Task.status != "DONE")
        .filter(Task.due_at < datetime.combine(today, datetime.min.time()))
        .order_by(Task.due_at.asc())
        .limit(5)
        .all()
    )
    
    # Events for today
    events_raw = (
        Event.query.filter_by(user_id=user.id)
        .filter(Event.start_at >= datetime.combine(today, datetime.min.time()))
        .filter(Event.start_at < datetime.combine(tomorrow, datetime.min.time()))
        .order_by(Event.start_at.asc())
        .all()
    )
    
    # Expand recurring events
    events_today = expand_recurring_events(events_raw, today, today)
    
    # Birthdays and name days
    contacts = Contact.query.filter_by(user_id=user.id).all()
    birthdays_today = [c for c in contacts if c.has_birthday_today(today)]
    namedays_today = [c for c in contacts if c.has_name_day_today(today)]
    
    # Get today's name day names
    nameday_names = get_name_day(today)
    
    # News
    news_items = fetch_news(max_items=5)
    news_summary = summarize_news_with_ai(fetch_news(max_items=50, fetch_all=True), max_summary_items=5)
    
    return {
        "user": user,
        "today": today,
        "tasks_today": tasks_today,
        "overdue_tasks": overdue_tasks,
        "events_today": events_today,
        "birthdays_today": birthdays_today,
        "namedays_today": namedays_today,
        "nameday_names": nameday_names,
        "news_items": news_items,
        "news_summary": news_summary,
    }


def render_digest_html(digest_data: Dict) -> str:
    """
    Render digest data to HTML email.
    
    Args:
        digest_data: Dictionary from generate_digest_data
    
    Returns:
        HTML string
    """
    return render_template("emails/daily_digest.html", **digest_data)


def should_send_digest(user: User) -> bool:
    """
    Check if digest should be sent to user.
    
    Args:
        user: User object
    
    Returns:
        bool: True if should send
    """
    if not user.digest_enabled:
        return False
    
    if not user.email:
        return False
    
    # Additional checks can be added here
    # e.g., check if user has opted out, last sent time, etc.
    
    return True
