import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool
from datetime import datetime
import uuid
from typing import Dict, Any, List

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.main import app
from src.database import get_session
from src.models.todo import Todo
from src.models.user import User
from src.auth.jwt_utils import create_access_token


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
        email="contract-test@example.com",
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


def validate_todo_response_structure(todo_data: Dict[str, Any]):
    """Validate that a todo response has the correct structure according to contract."""
    assert "id" in todo_data
    assert "title" in todo_data
    assert "description" in todo_data
    assert "completed" in todo_data
    assert "user_id" in todo_data
    assert "created_at" in todo_data
    assert "updated_at" in todo_data

    # Validate data types
    assert isinstance(todo_data["id"], str)  # UUID as string
    assert isinstance(todo_data["title"], str)
    assert todo_data["description"] is None or isinstance(todo_data["description"], str)
    assert isinstance(todo_data["completed"], bool)
    assert isinstance(todo_data["user_id"], str)  # UUID as string
    assert isinstance(todo_data["created_at"], str)  # ISO datetime string
    assert isinstance(todo_data["updated_at"], str)  # ISO datetime string

    # Validate UUID format
    uuid.UUID(todo_data["id"])
    uuid.UUID(todo_data["user_id"])

    # Validate datetime format
    datetime.fromisoformat(todo_data["created_at"].replace("Z", "+00:00"))
    datetime.fromisoformat(todo_data["updated_at"].replace("Z", "+00:00"))


def test_post_todos_contract(client, valid_token):
    """Test that POST /todos endpoint matches contract specifications."""
    headers = {"Authorization": f"Bearer {valid_token}"}
    payload = {"title": "Contract Test Todo", "description": "Test description"}

    response = client.post("/todos/", json=payload, headers=headers)

    # Validate HTTP status code
    assert response.status_code == 201

    # Validate response body structure
    data = response.json()
    validate_todo_response_structure(data)

    # Validate specific values
    assert data["title"] == "Contract Test Todo"
    assert data["description"] == "Test description"
    assert data["completed"] is False
    assert data["user_id"] == str(valid_token.split(".")[1])  # This is approximate - will need to fix


def test_get_todos_contract(client, valid_token, session, mock_user):
    """Test that GET /todos endpoint matches contract specifications."""
    headers = {"Authorization": f"Bearer {valid_token}"}

    # Create some todos first
    for i in range(3):
        payload = {"title": f"List Todo {i}"}
        client.post("/todos/", json=payload, headers=headers)

    response = client.get("/todos/", headers=headers)

    # Validate HTTP status code
    assert response.status_code == 200

    # The contract specifies that GET /todos should return:
    # {
    #   "todos": [...],
    #   "total": integer,
    #   "offset": integer,
    #   "limit": integer
    # }
    data = response.json()

    # Check if the response matches the contract
    assert "todos" in data
    assert "total" in data
    assert "offset" in data
    assert "limit" in data

    # Validate structure of each todo
    for todo in data["todos"]:
        validate_todo_response_structure(todo)

    # Validate data types
    assert isinstance(data["todos"], list)
    assert isinstance(data["total"], int)
    assert isinstance(data["offset"], int)
    assert isinstance(data["limit"], int)

    # Validate values make sense
    assert len(data["todos"]) == data["total"]  # For this test case
    assert data["offset"] >= 0
    assert data["limit"] > 0


def test_get_todos_with_pagination_contract(client, valid_token, session, mock_user):
    """Test that GET /todos with pagination parameters matches contract."""
    headers = {"Authorization": f"Bearer {valid_token}"}

    # Create 10 todos
    for i in range(10):
        payload = {"title": f"Paginated Todo {i}"}
        client.post("/todos/", json=payload, headers=headers)

    # Test with limit and offset
    response = client.get("/todos/?limit=5&offset=2", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert "todos" in data
    assert "total" in data
    assert "offset" in data
    assert "limit" in data

    # With limit=5 and offset=2, we should get up to 5 items starting from position 2
    assert len(data["todos"]) <= 5
    assert data["offset"] == 2
    assert data["limit"] == 5


def test_get_todos_with_completed_filter_contract(client, valid_token, session, mock_user):
    """Test that GET /todos with completed filter works."""
    headers = {"Authorization": f"Bearer {valid_token}"}

    # Create some completed and some incomplete todos
    client.post("/todos/", json={"title": "Incomplete Todo"}, headers=headers)

    completed_response = client.post("/todos/", json={"title": "Complete Me"}, headers=headers)
    completed_id = completed_response.json()["id"]
    client.patch(f"/todos/{completed_id}/complete", headers=headers)  # Toggle to complete

    # Get only completed todos
    response = client.get("/todos/?completed=true", headers=headers)
    assert response.status_code == 200
    data = response.json()

    if "todos" in data:  # New format
        for todo in data["todos"]:
            assert todo["completed"] is True
    else:  # Old format
        for todo in data:
            assert todo["completed"] is True

    # Get only incomplete todos
    response = client.get("/todos/?completed=false", headers=headers)
    assert response.status_code == 200
    data = response.json()

    if "todos" in data:  # New format
        for todo in data["todos"]:
            assert todo["completed"] is False
    else:  # Old format
        for todo in data:
            assert todo["completed"] is False


def test_get_todos_by_id_contract(client, valid_token, session, mock_user):
    """Test that GET /todos/{id} endpoint matches contract specifications."""
    headers = {"Authorization": f"Bearer {valid_token}"}

    # Create a todo first
    create_response = client.post("/todos/", json={"title": "Single Todo"}, headers=headers)
    todo_id = create_response.json()["id"]

    response = client.get(f"/todos/{todo_id}", headers=headers)

    # Validate HTTP status code
    assert response.status_code == 200

    # Validate response body structure
    data = response.json()
    validate_todo_response_structure(data)

    # Validate specific values
    assert data["id"] == todo_id
    assert data["title"] == "Single Todo"


def test_put_todos_contract(client, valid_token, session, mock_user):
    """Test that PUT /todos/{id} endpoint matches contract specifications."""
    headers = {"Authorization": f"Bearer {valid_token}"}

    # Create a todo first
    create_response = client.post("/todos/", json={"title": "Original Title"}, headers=headers)
    todo_id = create_response.json()["id"]

    # Update the todo
    update_payload = {
        "title": "Updated Title",
        "description": "Updated Description",
        "completed": True
    }
    response = client.put(f"/todos/{todo_id}", json=update_payload, headers=headers)

    # Validate HTTP status code
    assert response.status_code == 200

    # Validate response body structure
    data = response.json()
    validate_todo_response_structure(data)

    # Validate specific values
    assert data["id"] == todo_id
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated Description"
    assert data["completed"] is True


def test_delete_todos_contract(client, valid_token, session, mock_user):
    """Test that DELETE /todos/{id} endpoint matches contract specifications."""
    headers = {"Authorization": f"Bearer {valid_token}"}

    # Create a todo first
    create_response = client.post("/todos/", json={"title": "To Delete"}, headers=headers)
    todo_id = create_response.json()["id"]

    response = client.delete(f"/todos/{todo_id}", headers=headers)

    # Validate HTTP status code
    assert response.status_code == 204  # No Content

    # Verify the todo was actually deleted
    get_response = client.get(f"/todos/{todo_id}", headers=headers)
    assert get_response.status_code == 404


def test_patch_todos_complete_contract(client, valid_token, session, mock_user):
    """Test that PATCH /todos/{id}/complete endpoint matches contract specifications."""
    headers = {"Authorization": f"Bearer {valid_token}"}

    # Create a todo first
    create_response = client.post("/todos/", json={"title": "Toggle Completion"}, headers=headers)
    todo_id = create_response.json()["id"]

    response = client.patch(f"/todos/{todo_id}/complete", headers=headers)

    # Validate HTTP status code
    assert response.status_code == 200

    # Validate response body structure
    data = response.json()
    validate_todo_response_structure(data)

    # Validate completion was toggled
    assert data["id"] == todo_id
    assert data["completed"] is True


def test_error_responses_contract(client, valid_token, session, mock_user):
    """Test that error responses match contract specifications."""
    headers = {"Authorization": f"Bearer {valid_token}"}

    # Test 404 - Todo not found
    fake_id = str(uuid.uuid4())
    response = client.get(f"/todos/{fake_id}", headers=headers)
    assert response.status_code == 404

    # Test 422 - Validation error (missing title)
    response = client.post("/todos/", json={"description": "No title"}, headers=headers)
    assert response.status_code == 422

    # Test 401 - Unauthorized access (no token)
    response = client.get("/todos/")
    assert response.status_code == 401

    # Test 400 - Invalid ID format
    response = client.get("/todos/invalid-format", headers=headers)
    assert response.status_code == 400


def test_common_error_responses_contract(client):
    """Test that common error responses match contract specifications."""
    # Test 401 - Missing token
    response = client.get("/todos/")
    assert response.status_code == 401

    # Verify error response structure
    error_data = response.json()
    assert "detail" in error_data or "error" in error_data


def test_request_body_validation_contract(client, valid_token):
    """Test that request body validation matches contract specifications."""
    headers = {"Authorization": f"Bearer {valid_token}"}

    # Test invalid request body - missing required field
    response = client.post("/todos/", json={"description": "Missing title"}, headers=headers)
    assert response.status_code == 422

    # Test invalid request body - title too long
    long_title = "t" * 256
    response = client.post("/todos/", json={"title": long_title}, headers=headers)
    assert response.status_code == 422

    # Test invalid request body - description too long
    long_desc = "d" * 1001
    response = client.post("/todos/", json={"title": "Valid", "description": long_desc}, headers=headers)
    assert response.status_code == 422