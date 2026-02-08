import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool
from datetime import datetime, timezone
import uuid
from unittest.mock import patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.main import app
from src.database import get_session
from src.models.todo import Todo
from src.models.user import User
from src.auth.jwt_utils import create_access_token


# Create an in-memory SQLite database for testing
@pytest.fixture(name="engine")
def fixture_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    yield engine


@pytest.fixture(name="session")
def fixture_session(engine):
    from backend.src.models.base import SQLModel

    SQLModel.metadata.create_all(bind=engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def fixture_client(session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="mock_user")
def fixture_mock_user(session):
    # Create a mock user for testing
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # bcrypt hash for "password"
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="valid_token")
def fixture_valid_token(mock_user):
    # Create a valid JWT token for the mock user
    return create_access_token(data={"sub": str(mock_user.id)})


def test_create_todo_success(client, valid_token, session, mock_user):
    """Test successful creation of a todo."""
    headers = {"Authorization": f"Bearer {valid_token}"}
    payload = {
        "title": "Test Todo",
        "description": "Test Description"
    }

    response = client.post("/todos/", json=payload, headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["description"] == "Test Description"
    assert data["completed"] is False
    assert data["user_id"] == str(mock_user.id)

    # Verify the todo was saved to the database
    todo_in_db = session.get(Todo, data["id"])
    assert todo_in_db is not None
    assert todo_in_db.title == "Test Todo"


def test_create_todo_missing_title(client, valid_token):
    """Test creating a todo with missing title should fail."""
    headers = {"Authorization": f"Bearer {valid_token}"}
    payload = {
        "description": "Test Description"
    }

    response = client.post("/todos/", json=payload, headers=headers)

    assert response.status_code == 422  # Validation error


def test_get_todos_success(client, valid_token, session, mock_user):
    """Test successful retrieval of todos for a user."""
    # Create a few todos for the user
    headers = {"Authorization": f"Bearer {valid_token}"}

    # Create first todo
    client.post("/todos/", json={"title": "Todo 1"}, headers=headers)
    # Create second todo
    client.post("/todos/", json={"title": "Todo 2", "description": "Second todo"}, headers=headers)

    response = client.get("/todos/", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    titles = [item["title"] for item in data]
    assert "Todo 1" in titles
    assert "Todo 2" in titles


def test_get_todo_by_id_success(client, valid_token, session, mock_user):
    """Test successful retrieval of a specific todo by ID."""
    headers = {"Authorization": f"Bearer {valid_token}"}
    payload = {"title": "Specific Todo"}

    # Create a todo first
    create_response = client.post("/todos/", json=payload, headers=headers)
    todo_id = create_response.json()["id"]

    response = client.get(f"/todos/{todo_id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == "Specific Todo"


def test_get_todo_by_id_invalid_format(client, valid_token):
    """Test getting a todo with invalid ID format."""
    headers = {"Authorization": f"Bearer {valid_token}"}

    response = client.get("/todos/invalid-id", headers=headers)

    assert response.status_code == 400  # Bad Request


def test_get_todo_by_id_not_found(client, valid_token):
    """Test getting a todo that doesn't exist."""
    headers = {"Authorization": f"Bearer {valid_token}"}
    fake_uuid = str(uuid.uuid4())

    response = client.get(f"/todos/{fake_uuid}", headers=headers)

    assert response.status_code == 404


def test_update_todo_success(client, valid_token, session, mock_user):
    """Test successful update of a todo."""
    headers = {"Authorization": f"Bearer {valid_token}"}
    payload = {"title": "Original Title", "description": "Original Description"}

    # Create a todo first
    create_response = client.post("/todos/", json=payload, headers=headers)
    todo_id = create_response.json()["id"]

    # Update the todo
    update_payload = {
        "title": "Updated Title",
        "description": "Updated Description",
        "completed": True
    }
    response = client.put(f"/todos/{todo_id}", json=update_payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated Description"
    assert data["completed"] is True


def test_delete_todo_success(client, valid_token, session):
    """Test successful deletion of a todo."""
    headers = {"Authorization": f"Bearer {valid_token}"}
    payload = {"title": "Todo to Delete"}

    # Create a todo first
    create_response = client.post("/todos/", json=payload, headers=headers)
    todo_id = create_response.json()["id"]

    response = client.delete(f"/todos/{todo_id}", headers=headers)

    assert response.status_code == 204  # No Content

    # Verify the todo was deleted from the database
    todo_in_db = session.get(Todo, todo_id)
    assert todo_in_db is None


def test_toggle_todo_completion_success(client, valid_token, session):
    """Test successful toggling of a todo's completion status."""
    headers = {"Authorization": f"Bearer {valid_token}"}
    payload = {"title": "Toggle Todo"}

    # Create a todo first
    create_response = client.post("/todos/", json=payload, headers=headers)
    todo_id = create_response.json()["id"]

    # Initially should be false
    response = client.get(f"/todos/{todo_id}", headers=headers)
    assert response.json()["completed"] is False

    # Toggle completion
    response = client.patch(f"/todos/{todo_id}/complete", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is True

    # Toggle again
    response = client.patch(f"/todos/{todo_id}/complete", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is False


def test_unauthorized_access(client):
    """Test that accessing endpoints without authorization returns 401."""
    response = client.get("/todos/")
    assert response.status_code == 401

    response = client.post("/todos/", json={"title": "Test"})
    assert response.status_code == 401


def test_pagination_parameters(client, valid_token, session, mock_user):
    """Test pagination parameters work correctly."""
    headers = {"Authorization": f"Bearer {valid_token}"}

    # Create 5 todos
    for i in range(5):
        client.post("/todos/", json={"title": f"Todo {i+1}"}, headers=headers)

    # Test limit and offset
    response = client.get("/todos/?limit=2&offset=0", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    response = client.get("/todos/?limit=2&offset=2", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2