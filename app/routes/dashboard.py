"""Dashboard routes."""
from datetime import datetime, timedelta
from flask import Blueprint, render_template, g

from app.auth.firebase import require_auth
from app.models.task import Task
from app.models.event import Event
from app.services.calendar import get_today, get_week_range, expand_recurring_events

bp = Blueprint("dashboard", __name__)


@bp.route("/")
@require_auth
def index():
    """Dashboard - today's overview."""
    user = g.current_user
    today = get_today()
    tomorrow = today + timedelta(days=1)
    week_start, week_end = get_week_range(today)
    
    # Today's tasks
    tasks_today = (
        Task.query.filter_by(user_id=user.id)
        .filter(Task.status != "DONE")
        .filter(Task.due_at >= datetime.combine(today, datetime.min.time()))
        .filter(Task.due_at < datetime.combine(tomorrow, datetime.min.time()))
        .order_by(Task.priority.desc(), Task.due_at.asc())
        .all()
    )
    
    # This week's tasks
    tasks_week = (
        Task.query.filter_by(user_id=user.id)
        .filter(Task.status != "DONE")
        .filter(Task.due_at >= datetime.combine(week_start, datetime.min.time()))
        .filter(Task.due_at < datetime.combine(week_end, datetime.max.time()))
        .order_by(Task.due_at.asc())
        .all()
    )
    
    # Overdue tasks
    overdue_tasks = (
        Task.query.filter_by(user_id=user.id)
        .filter(Task.status != "DONE")
        .filter(Task.due_at < datetime.combine(today, datetime.min.time()))
        .order_by(Task.due_at.asc())
        .limit(10)
        .all()
    )
    
    # Today's events
    events_raw = (
        Event.query.filter_by(user_id=user.id)
        .filter(Event.start_at >= datetime.combine(today, datetime.min.time()))
        .filter(Event.start_at < datetime.combine(tomorrow, datetime.min.time()))
        .order_by(Event.start_at.asc())
        .all()
    )
    
    events_today = expand_recurring_events(events_raw, today, today)
    
    return render_template(
        "dashboard.html",
        today=today,
        tasks_today=tasks_today,
        tasks_week=tasks_week,
        overdue_tasks=overdue_tasks,
        events_today=events_today,
    )
