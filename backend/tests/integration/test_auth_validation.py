import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool
import uuid
from datetime import timedelta, datetime
from jose import jwt
import os

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.main import app
from src.database import get_session
from src.models.user import User


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


def test_jwt_validation_missing_token(client):
    """Test that endpoints return 401 when no token is provided."""
    # Test GET /todos
    response = client.get("/todos/")
    assert response.status_code == 401

    # Test POST /todos
    response = client.post("/todos/", json={"title": "Test Todo"})
    assert response.status_code == 401

    # Test GET /todos/{id}
    response = client.get(f"/todos/{uuid.uuid4()}")
    assert response.status_code == 401

    # Test PUT /todos/{id}
    response = client.put(f"/todos/{uuid.uuid4()}", json={"title": "Updated Todo"})
    assert response.status_code == 401

    # Test DELETE /todos/{id}
    response = client.delete(f"/todos/{uuid.uuid4()}")
    assert response.status_code == 401

    # Test PATCH /todos/{id}/complete
    response = client.patch(f"/todos/{uuid.uuid4()}/complete")
    assert response.status_code == 401


def test_jwt_validation_invalid_token(client):
    """Test that endpoints return 401 when an invalid token is provided."""
    headers = {"Authorization": "Bearer invalid.token.here"}

    # Test GET /todos
    response = client.get("/todos/", headers=headers)
    assert response.status_code == 401

    # Test POST /todos
    response = client.post("/todos/", json={"title": "Test Todo"}, headers=headers)
    assert response.status_code == 401

    # Test GET /todos/{id}
    response = client.get(f"/todos/{uuid.uuid4()}", headers=headers)
    assert response.status_code == 401

    # Test PUT /todos/{id}
    response = client.put(f"/todos/{uuid.uuid4()}", json={"title": "Updated Todo"}, headers=headers)
    assert response.status_code == 401

    # Test DELETE /todos/{id}
    response = client.delete(f"/todos/{uuid.uuid4()}", headers=headers)
    assert response.status_code == 401

    # Test PATCH /todos/{id}/complete
    response = client.patch(f"/todos/{uuid.uuid4()}/complete", headers=headers)
    assert response.status_code == 401


def test_jwt_validation_expired_token(client, mock_user):
    """Test that endpoints return 401 when an expired token is provided."""
    # Create an expired token manually
    to_encode = {"sub": str(mock_user.id)}
    expire = datetime.utcnow() - timedelta(minutes=10)  # Expired 10 minutes ago

    encoded_jwt = jwt.encode(
        {**to_encode, "exp": expire.timestamp()},
        os.getenv("SECRET_KEY", "your-secret-key-change-in-production"),
        algorithm="HS256"
    )

    headers = {"Authorization": f"Bearer {encoded_jwt}"}

    # Test GET /todos
    response = client.get("/todos/", headers=headers)
    assert response.status_code == 401

    # Test POST /todos
    response = client.post("/todos/", json={"title": "Test Todo"}, headers=headers)
    assert response.status_code == 401

    # Test GET /todos/{id}
    response = client.get(f"/todos/{uuid.uuid4()}", headers=headers)
    assert response.status_code == 401

    # Test PUT /todos/{id}
    response = client.put(f"/todos/{uuid.uuid4()}", json={"title": "Updated Todo"}, headers=headers)
    assert response.status_code == 401

    # Test DELETE /todos/{id}
    response = client.delete(f"/todos/{uuid.uuid4()}", headers=headers)
    assert response.status_code == 401

    # Test PATCH /todos/{id}/complete
    response = client.patch(f"/todos/{uuid.uuid4()}/complete", headers=headers)
    assert response.status_code == 401


def test_jwt_validation_malformed_token(client):
    """Test that endpoints return 401 when a malformed token is provided."""
    headers = {"Authorization": "Bearer this.is.not.a.valid.jwt.token.format"}

    # Test GET /todos
    response = client.get("/todos/", headers=headers)
    assert response.status_code == 401

    # Test POST /todos
    response = client.post("/todos/", json={"title": "Test Todo"}, headers=headers)
    assert response.status_code == 401


def test_ownership_validation_wrong_user_id_in_token(client, session, mock_user):
    """Test that users with wrong user ID in token still get proper validation."""
    # Create a valid token for a different user ID
    fake_user_id = str(uuid.uuid4())
    from backend.src.auth.jwt_utils import create_access_token
    fake_token = create_access_token(data={"sub": fake_user_id})

    headers = {"Authorization": f"Bearer {fake_token}"}

    # Even with a valid token for a different user, we should still get proper responses
    # (either 404 if resource doesn't exist for that user, or 403 if access is denied)
    response = client.get("/todos/", headers=headers)
    assert response.status_code == 200  # Should return 200 with empty list for fake user
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0