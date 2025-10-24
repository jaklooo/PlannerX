"""Tests for tasks functionality."""
import json
from datetime import datetime, timedelta


def test_create_task(client, auth_headers, test_user):
    """Test creating a new task."""
    data = {
        "title": "New Task",
        "notes": "Task notes",
        "priority": "HIGH",
        "status": "TODO",
        "due_at": (datetime.utcnow() + timedelta(days=1)).isoformat()
    }
    
    response = client.post(
        "/tasks/create",
        data=json.dumps(data),
        headers=auth_headers
    )
    
    assert response.status_code == 201
    result = json.loads(response.data)
    assert result["title"] == "New Task"
    assert result["priority"] == "HIGH"


def test_list_tasks(client, auth_headers, sample_task):
    """Test listing tasks."""
    response = client.get("/tasks/", headers=auth_headers)
    
    assert response.status_code == 200
    # Check HTML response contains task title
    assert b"Test Task" in response.data


def test_list_tasks_json(client, auth_headers, sample_task):
    """Test listing tasks with JSON response."""
    headers = auth_headers.copy()
    headers["Accept"] = "application/json"
    
    response = client.get("/tasks/", headers=headers)
    
    assert response.status_code == 200
    tasks = json.loads(response.data)
    assert len(tasks) >= 1
    assert tasks[0]["title"] == "Test Task"


def test_update_task(client, auth_headers, sample_task):
    """Test updating a task."""
    data = {
        "title": "Updated Task",
        "status": "DONE"
    }
    
    response = client.put(
        f"/tasks/{sample_task.id}",
        data=json.dumps(data),
        headers=auth_headers
    )
    
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result["title"] == "Updated Task"
    assert result["status"] == "DONE"
    assert result["completed_at"] is not None


def test_delete_task(client, auth_headers, sample_task):
    """Test deleting a task."""
    response = client.delete(
        f"/tasks/{sample_task.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    
    # Verify task is deleted
    response = client.get(
        f"/tasks/{sample_task.id}",
        headers=auth_headers
    )
    assert response.status_code == 404


def test_snooze_task(client, auth_headers, sample_task):
    """Test snoozing a task."""
    original_due = sample_task.due_at
    
    response = client.post(
        f"/tasks/{sample_task.id}/snooze",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    result = json.loads(response.data)
    
    new_due = datetime.fromisoformat(result["due_at"].replace("Z", "+00:00"))
    assert new_due > original_due


def test_user_isolation(client, auth_headers, sample_task):
    """Test that users can only access their own tasks."""
    # Try to access with different user
    other_headers = {
        "Authorization": "Bearer dev_otheruser:other@example.com",
        "Content-Type": "application/json"
    }
    
    response = client.get(
        f"/tasks/{sample_task.id}",
        headers=other_headers
    )
    
    assert response.status_code == 404
