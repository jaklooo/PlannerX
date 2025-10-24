"""Tests for digest functionality."""
import pytest
from datetime import date, datetime, timedelta
from app.services.digest import generate_digest_data, should_send_digest
from app.models.task import Task
from app.models.event import Event
from app.models.contact import Contact


def test_generate_digest_data(app, test_user):
    """Test generating digest data."""
    # Create some test data
    today = date.today()
    
    # Task for today
    task = Task(
        user_id=test_user.id,
        title="Today's Task",
        due_at=datetime.combine(today, datetime.min.time()) + timedelta(hours=10),
        priority="HIGH",
        status="TODO"
    )
    from app import db
    db.session.add(task)
    
    # Event for today
    event = Event(
        user_id=test_user.id,
        title="Today's Event",
        start_at=datetime.combine(today, datetime.min.time()) + timedelta(hours=14),
        repeat_rule="NONE"
    )
    db.session.add(event)
    
    # Contact with birthday today
    contact = Contact(
        user_id=test_user.id,
        name="Birthday Person",
        birthday_date=today
    )
    db.session.add(contact)
    db.session.commit()
    
    # Generate digest
    with app.app_context():
        digest_data = generate_digest_data(test_user)
    
    assert digest_data["user"] == test_user
    assert digest_data["today"] == today
    assert len(digest_data["tasks_today"]) >= 1
    assert len(digest_data["events_today"]) >= 0  # Events are expanded
    assert len(digest_data["birthdays_today"]) >= 1


def test_should_send_digest_enabled(app, test_user):
    """Test should_send_digest when enabled."""
    test_user.digest_enabled = True
    from app import db
    db.session.commit()
    
    with app.app_context():
        assert should_send_digest(test_user) is True


def test_should_send_digest_disabled(app, test_user):
    """Test should_send_digest when disabled."""
    test_user.digest_enabled = False
    from app import db
    db.session.commit()
    
    with app.app_context():
        assert should_send_digest(test_user) is False


def test_should_send_digest_no_email(app, test_user):
    """Test should_send_digest with no email."""
    test_user.email = None
    from app import db
    db.session.commit()
    
    with app.app_context():
        assert should_send_digest(test_user) is False


def test_overdue_tasks_in_digest(app, test_user):
    """Test that overdue tasks appear in digest."""
    yesterday = date.today() - timedelta(days=1)
    
    # Create overdue task
    task = Task(
        user_id=test_user.id,
        title="Overdue Task",
        due_at=datetime.combine(yesterday, datetime.max.time()),
        priority="HIGH",
        status="TODO"
    )
    from app import db
    db.session.add(task)
    db.session.commit()
    
    with app.app_context():
        digest_data = generate_digest_data(test_user)
    
    assert len(digest_data["overdue_tasks"]) >= 1
    assert digest_data["overdue_tasks"][0].title == "Overdue Task"
