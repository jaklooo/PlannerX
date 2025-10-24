"""Tasks routes."""
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify, g

from app import db
from app.auth.firebase import require_auth
from app.models.task import Task
from app.models.project import Project

bp = Blueprint("tasks", __name__)


@bp.route("/")
@require_auth
def list_tasks():
    """List all tasks for current user."""
    user = g.current_user
    filter_by = request.args.get("filter", "all")
    
    query = Task.query.filter_by(user_id=user.id)
    
    if filter_by == "today":
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        query = query.filter(
            Task.due_at >= datetime.combine(today, datetime.min.time()),
            Task.due_at < datetime.combine(tomorrow, datetime.min.time())
        )
    elif filter_by == "week":
        from app.services.calendar import get_week_range
        week_start, week_end = get_week_range()
        query = query.filter(
            Task.due_at >= datetime.combine(week_start, datetime.min.time()),
            Task.due_at < datetime.combine(week_end, datetime.max.time())
        )
    elif filter_by == "overdue":
        query = query.filter(Task.due_at < datetime.now()).filter(Task.status != "DONE")
    
    tasks = query.order_by(Task.due_at.asc()).all()
    projects = Project.query.filter_by(user_id=user.id).all()
    
    if request.headers.get("Accept") == "application/json":
        return jsonify([task.to_dict() for task in tasks])
    
    return render_template("tasks.html", tasks=tasks, projects=projects, filter=filter_by)


@bp.route("/create", methods=["POST"])
@require_auth
def create_task():
    """Create a new task."""
    user = g.current_user
    data = request.get_json() if request.is_json else request.form
    
    task = Task(
        user_id=user.id,
        title=data.get("title"),
        notes=data.get("notes", ""),
        project_id=data.get("project_id") or None,
        priority=data.get("priority", "MEDIUM"),
        status=data.get("status", "TODO"),
    )
    
    # Parse due_at
    due_at_str = data.get("due_at")
    if due_at_str:
        try:
            task.due_at = datetime.fromisoformat(due_at_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            pass
    
    db.session.add(task)
    db.session.commit()
    
    if request.is_json:
        return jsonify(task.to_dict()), 201
    
    return jsonify({"success": True, "id": task.id})


@bp.route("/<int:task_id>", methods=["GET"])
@require_auth
def get_task(task_id):
    """Get a specific task."""
    user = g.current_user
    task = Task.query.filter_by(id=task_id, user_id=user.id).first_or_404()
    
    return jsonify(task.to_dict())


@bp.route("/<int:task_id>", methods=["PUT", "PATCH"])
@require_auth
def update_task(task_id):
    """Update a task."""
    user = g.current_user
    task = Task.query.filter_by(id=task_id, user_id=user.id).first_or_404()
    
    data = request.get_json() if request.is_json else request.form
    
    if "title" in data:
        task.title = data["title"]
    if "notes" in data:
        task.notes = data["notes"]
    if "priority" in data:
        task.priority = data["priority"]
    if "status" in data:
        task.status = data["status"]
        if data["status"] == "DONE" and not task.completed_at:
            task.completed_at = datetime.utcnow()
        elif data["status"] != "DONE":
            task.completed_at = None
    if "project_id" in data:
        task.project_id = data["project_id"] or None
    if "due_at" in data:
        due_at_str = data["due_at"]
        if due_at_str:
            try:
                task.due_at = datetime.fromisoformat(due_at_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass
        else:
            task.due_at = None
    
    db.session.commit()
    
    return jsonify(task.to_dict())


@bp.route("/<int:task_id>", methods=["DELETE"])
@require_auth
def delete_task(task_id):
    """Delete a task."""
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"!!! DELETE TASK CALLED: task_id={task_id}, user={g.current_user.id if hasattr(g, 'current_user') else 'NO USER'}")
    
    user = g.current_user
    task = Task.query.filter_by(id=task_id, user_id=user.id).first_or_404()
    
    db.session.delete(task)
    db.session.commit()
    
    logger.error(f"!!! DELETE SUCCESS: task {task_id} deleted")
    return jsonify({"success": True})


@bp.route("/<int:task_id>/snooze", methods=["POST"])
@require_auth
def snooze_task(task_id):
    """Snooze a task by 1 day."""
    from datetime import timedelta
    
    user = g.current_user
    task = Task.query.filter_by(id=task_id, user_id=user.id).first_or_404()
    
    if task.due_at:
        task.due_at = task.due_at + timedelta(days=1)
        db.session.commit()
    
    return jsonify(task.to_dict())
