import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool
from datetime import timedelta, datetime
from jose import jwt
import os
import uuid

from backend.src.main import app
from backend.src.database import get_session
from backend.src.models.user import User
from backend.src.auth.jwt_utils import create_access_token


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
        email="edge-case-test@example.com",
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


def test_maximum_length_text_fields_validation(client, valid_token):
    """Test handling of maximum length text fields validation."""
    headers = {"Authorization": f"Bearer {valid_token}"}

    # Test maximum title length (255 chars)
    max_title = "t" * 255
    response = client.post("/todos/", json={"title": max_title}, headers=headers)
    assert response.status_code == 201  # Should succeed

    # Test over maximum title length (256 chars)
    over_max_title = "t" * 256
    response = client.post("/todos/", json={"title": over_max_title}, headers=headers)
    assert response.status_code == 422  # Should fail with validation error

    # Test maximum description length (1000 chars)
    max_description = "d" * 1000
    response = client.post("/todos/", json={"title": "Valid Title", "description": max_description}, headers=headers)
    assert response.status_code == 201  # Should succeed

    # Test over maximum description length (1001 chars)
    over_max_description = "d" * 1001
    response = client.post("/todos/", json={"title": "Valid Title", "description": over_max_description}, headers=headers)
    assert response.status_code == 422  # Should fail with validation error


def test_expired_jwt_token_scenarios(client, valid_token, mock_user):
    """Test handling of expired JWT token scenarios."""
    # Create an expired token manually
    to_encode = {"sub": str(mock_user.id)}
    expire = datetime.utcnow() - timedelta(minutes=10)  # Expired 10 minutes ago

    expired_token = jwt.encode(
        {**to_encode, "exp": expire.timestamp()},
        os.getenv("SECRET_KEY", "your-secret-key-change-in-production"),
        algorithm="HS256"
    )

    headers = {"Authorization": f"Bearer {expired_token}"}

    # Test that all endpoints reject expired tokens
    response = client.get("/todos/", headers=headers)
    assert response.status_code == 401

    response = client.post("/todos/", json={"title": "Test"}, headers=headers)
    assert response.status_code == 401

    response = client.get(f"/todos/{uuid.uuid4()}", headers=headers)
    assert response.status_code == 401

    response = client.put(f"/todos/{uuid.uuid4()}", json={"title": "Updated"}, headers=headers)
    assert response.status_code == 401

    response = client.delete(f"/todos/{uuid.uuid4()}", headers=headers)
    assert response.status_code == 401

    response = client.patch(f"/todos/{uuid.uuid4()}/complete", headers=headers)
    assert response.status_code == 401


def test_malformed_json_handling(client, valid_token):
    """Test handling of malformed JSON in API requests."""
    headers = {"Authorization": f"Bearer {valid_token}"}

    # Test with malformed JSON (using raw text instead of JSON)
    response = client.post(
        "/todos/",
        content='{"title": "malformed json without proper closing',
        headers={**headers, "Content-Type": "application/json"}
    )
    # This might return 422 or 400 depending on FastAPI's handling of malformed JSON

    # Test with empty request body where content-type is JSON but body is empty
    response = client.post(
        "/todos/",
        content='',
        headers={**headers, "Content-Type": "application/json"}
    )
    assert response.status_code in [422, 400]


def test_access_to_deleted_todos(client, valid_token):
    """Test handling of access to deleted todos."""
    headers = {"Authorization": f"Bearer {valid_token}"}

    # Create a todo
    create_response = client.post("/todos/", json={"title": "To Delete"}, headers=headers)
    assert create_response.status_code == 201
    todo_id = create_response.json()["id"]

    # Delete the todo
    delete_response = client.delete(f"/todos/{todo_id}", headers=headers)
    assert delete_response.status_code == 204

    # Try to access the deleted todo
    get_response = client.get(f"/todos/{todo_id}", headers=headers)
    assert get_response.status_code == 404

    # Try to update the deleted todo
    update_response = client.put(f"/todos/{todo_id}", json={"title": "Updated"}, headers=headers)
    assert update_response.status_code == 404

    # Try to delete the already deleted todo
    delete_response = client.delete(f"/todos/{todo_id}", headers=headers)
    assert delete_response.status_code == 404

    # Try to toggle completion of the deleted todo
    patch_response = client.patch(f"/todos/{todo_id}/complete", headers=headers)
    assert patch_response.status_code == 404


def test_invalid_todo_id_formats(client, valid_token):
    """Test handling of invalid todo ID formats."""
    headers = {"Authorization": f"Bearer {valid_token}"}

    # Test various invalid ID formats
    invalid_ids = [
        "invalid-uuid-format",
        "123",  # Too short
        "this-is-not-a-valid-uuid-at-all-really-long-string",
        "",  # Empty string
        "special!@#$%chars",
        "spaces in uuid",
    ]

    for invalid_id in invalid_ids:
        # Test GET
        response = client.get(f"/todos/{invalid_id}", headers=headers)
        assert response.status_code == 400  # Should return 400 for invalid format

        # Test PUT
        response = client.put(f"/todos/{invalid_id}", json={"title": "Updated"}, headers=headers)
        assert response.status_code == 400

        # Test DELETE
        response = client.delete(f"/todos/{invalid_id}", headers=headers)
        assert response.status_code == 400

        # Test PATCH
        response = client.patch(f"/todos/{invalid_id}/complete", headers=headers)
        assert response.status_code == 400


def test_empty_title_handling(client, valid_token):
    """Test handling of empty titles (should be rejected)."""
    headers = {"Authorization": f"Bearer {valid_token}"}

    # Test empty string title
    response = client.post("/todos/", json={"title": ""}, headers=headers)
    assert response.status_code == 422

    # Test whitespace-only title (should be stripped and become empty)
    response = client.post("/todos/", json={"title": "   "}, headers=headers)
    assert response.status_code == 422

    # Test title with only special whitespace characters
    response = client.post("/todos/", json={"title": "\t\n\r"}, headers=headers)
    assert response.status_code == 422


def test_boundary_values_for_pagination(client, valid_token, session, mock_user):
    """Test boundary values for pagination parameters."""
    headers = {"Authorization": f"Bearer {valid_token}"}

    # Create 10 todos
    for i in range(10):
        client.post("/todos/", json={"title": f"Boundary Todo {i}"}, headers=headers)

    # Test with limit = 0
    response = client.get("/todos/?limit=0", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 0

    # Test with negative offset
    response = client.get("/todos/?offset=-5", headers=headers)
    # FastAPI typically handles negative offsets gracefully or returns 422

    # Test with very high limit (should be capped at 100 according to contract)
    response = client.get("/todos/?limit=1000", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] <= 100  # Should be capped


def test_special_characters_in_input(client, valid_token):
    """Test handling of special characters in input."""
    headers = {"Authorization": f"Bearer {valid_token}"}

    special_inputs = [
        {"title": "Title with unicode: 🚀🔥🎉"},
        {"title": "Title with symbols: !@#$%^&*()"},
        {"title": "Title with quotes: \"double\" and 'single'"},
        {"title": "Title with brackets: []{}<>"},
        {"title": "Title with slashes: /\\|"},
        {"title": "Title with control chars: \n\t\r"},
        {"title": "Title with HTML-like: <script>alert('xss')</script>", "description": "Description with HTML"},
        {"title": "SQL injection attempt: '; DROP TABLE--", "description": "Another '; DROP TABLE-- test"}
    ]

    for input_data in special_inputs:
        response = client.post("/todos/", json=input_data, headers=headers)
        # All should either succeed or return a proper error, not crash
        assert response.status_code in [201, 422]


def test_null_values_handling(client, valid_token):
    """Test handling of null values in optional fields."""
    headers = {"Authorization": f"Bearer {valid_token}"}

    # Test creating with null description (should work)
    response = client.post("/todos/", json={"title": "Todo with null desc", "description": None}, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["description"] is None

    # Test updating with null values
    todo_id = response.json()["id"]
    response = client.put(f"/todos/{todo_id}", json={"description": None}, headers=headers)
    assert response.status_code == 200


def test_extremely_large_input_handling(client, valid_token):
    """Test handling of extremely large input (potential DoS protection)."""
    headers = {"Authorization": f"Bearer {valid_token}"}

    # Create an extremely large title (much larger than allowed)
    huge_title = "t" * 10000  # Way over the 255 char limit
    response = client.post("/todos/", json={"title": huge_title}, headers=headers)
    assert response.status_code == 422  # Should return validation error, not crash

    # Create an extremely large description
    huge_description = "d" * 10000  # Way over the 1000 char limit
    response = client.post("/todos/", json={"title": "Valid", "description": huge_description}, headers=headers)
    assert response.status_code == 422  # Should return validation error, not crash