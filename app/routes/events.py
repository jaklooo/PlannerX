"""Events routes."""
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify, g

from app import db
from app.auth.firebase import require_auth
from app.models.event import Event
from app.services.calendar import get_week_range, expand_recurring_events

bp = Blueprint("events", __name__)


@bp.route("/")
@require_auth
def list_events():
    """List all events for current user."""
    user = g.current_user
    view = request.args.get("view", "week")  # week, month, day
    
    query = Event.query.filter_by(user_id=user.id)
    
    if view == "week":
        week_start, week_end = get_week_range()
        events_raw = query.filter(
            Event.start_at >= datetime.combine(week_start, datetime.min.time()),
            Event.start_at < datetime.combine(week_end, datetime.max.time())
        ).order_by(Event.start_at.asc()).all()
        
        events = expand_recurring_events(events_raw, week_start, week_end)
    else:
        events_raw = query.order_by(Event.start_at.asc()).limit(50).all()
        events = [{"event": e, "occurrence_date": e.start_at.date()} for e in events_raw]
    
    if request.headers.get("Accept") == "application/json":
        return jsonify([{
            **e["event"].to_dict(),
            "occurrence_date": e["occurrence_date"].isoformat()
        } for e in events])
    
    return render_template("events.html", events=events, view=view)


@bp.route("/create", methods=["POST"])
@require_auth
def create_event():
    """Create a new event."""
    user = g.current_user
    data = request.get_json() if request.is_json else request.form
    
    event = Event(
        user_id=user.id,
        title=data.get("title"),
        description=data.get("description", ""),
        location=data.get("location", ""),
        repeat_rule=data.get("repeat_rule", "NONE"),
    )
    
    # Parse dates
    start_at_str = data.get("start_at")
    if start_at_str:
        try:
            event.start_at = datetime.fromisoformat(start_at_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return jsonify({"error": "Invalid start_at format"}), 400
    
    end_at_str = data.get("end_at")
    if end_at_str:
        try:
            event.end_at = datetime.fromisoformat(end_at_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            pass
    
    db.session.add(event)
    db.session.commit()
    
    if request.is_json:
        return jsonify(event.to_dict()), 201
    
    return jsonify({"success": True, "id": event.id})


@bp.route("/<int:event_id>", methods=["GET"])
@require_auth
def get_event(event_id):
    """Get a specific event."""
    user = g.current_user
    event = Event.query.filter_by(id=event_id, user_id=user.id).first_or_404()
    
    return jsonify(event.to_dict())


@bp.route("/<int:event_id>", methods=["PUT", "PATCH"])
@require_auth
def update_event(event_id):
    """Update an event."""
    user = g.current_user
    event = Event.query.filter_by(id=event_id, user_id=user.id).first_or_404()
    
    data = request.get_json() if request.is_json else request.form
    
    if "title" in data:
        event.title = data["title"]
    if "description" in data:
        event.description = data["description"]
    if "location" in data:
        event.location = data["location"]
    if "repeat_rule" in data:
        event.repeat_rule = data["repeat_rule"]
    
    if "start_at" in data:
        start_at_str = data["start_at"]
        if start_at_str:
            try:
                event.start_at = datetime.fromisoformat(start_at_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass
    
    if "end_at" in data:
        end_at_str = data["end_at"]
        if end_at_str:
            try:
                event.end_at = datetime.fromisoformat(end_at_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass
    
    db.session.commit()
    
    return jsonify(event.to_dict())


@bp.route("/<int:event_id>", methods=["DELETE"])
@require_auth
def delete_event(event_id):
    """Delete an event."""
    user = g.current_user
    event = Event.query.filter_by(id=event_id, user_id=user.id).first_or_404()
    
    db.session.delete(event)
    db.session.commit()
    
    return jsonify({"success": True})
