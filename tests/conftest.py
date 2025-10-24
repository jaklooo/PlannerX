"""Pytest configuration and fixtures."""
import pytest
from app import create_app, db
from app.models.user import User
from app.models.task import Task
from app.models.event import Event
from app.models.contact import Contact
from app.models.project import Project


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app("testing")
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create a test user."""
    user = User(
        uid="test_user_123",
        email="test@example.com",
        email_verified=True
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def auth_headers():
    """Return authorization headers with dev token."""
    return {
        "Authorization": "Bearer dev_test_user_123:test@example.com",
        "Content-Type": "application/json"
    }


@pytest.fixture
def sample_task(test_user):
    """Create a sample task."""
    from datetime import datetime, timedelta
    
    task = Task(
        user_id=test_user.id,
        title="Test Task",
        notes="This is a test task",
        due_at=datetime.utcnow() + timedelta(days=1),
        priority="MEDIUM",
        status="TODO"
    )
    db.session.add(task)
    db.session.commit()
    return task


@pytest.fixture
def sample_event(test_user):
    """Create a sample event."""
    from datetime import datetime, timedelta
    
    event = Event(
        user_id=test_user.id,
        title="Test Event",
        description="Test event description",
        start_at=datetime.utcnow() + timedelta(hours=2),
        repeat_rule="NONE"
    )
    db.session.add(event)
    db.session.commit()
    return event


@pytest.fixture
def sample_contact(test_user):
    """Create a sample contact."""
    from datetime import date
    
    contact = Contact(
        user_id=test_user.id,
        name="Test Contact",
        email="contact@example.com",
        birthday_date=date(1990, 5, 15)
    )
    db.session.add(contact)
    db.session.commit()
    return contact
