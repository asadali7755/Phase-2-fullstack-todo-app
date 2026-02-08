import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool
import uuid

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


@pytest.fixture(name="user1")
def fixture_user1(session):
    # Create first user
    user = User(
        id=uuid.uuid4(),
        email="user1@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # bcrypt hash for "password"
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="user2")
def fixture_user2(session):
    # Create second user
    user = User(
        id=uuid.uuid4(),
        email="user2@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # bcrypt hash for "password"
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="user1_token")
def fixture_user1_token(user1):
    return create_access_token(data={"sub": str(user1.id)})


@pytest.fixture(name="user2_token")
def fixture_user2_token(user2):
    return create_access_token(data={"sub": str(user2.id)})


def test_user_cannot_access_other_users_todos(client, session, user1, user2, user1_token, user2_token):
    """Test that users cannot access other users' todos."""
    # Create a todo for user1
    headers_user1 = {"Authorization": f"Bearer {user1_token}"}
    response = client.post("/todos/", json={"title": "User1's Todo"}, headers=headers_user1)
    assert response.status_code == 201
    todo_data = response.json()
    todo_id = todo_data["id"]

    # Verify user1 can access their own todo
    response = client.get(f"/todos/{todo_id}", headers=headers_user1)
    assert response.status_code == 200
    assert response.json()["id"] == todo_id

    # Verify user2 cannot access user1's todo
    headers_user2 = {"Authorization": f"Bearer {user2_token}"}
    response = client.get(f"/todos/{todo_id}", headers=headers_user2)
    assert response.status_code == 404  # Should return 404 since it doesn't exist for user2


def test_user_cannot_update_other_users_todos(client, session, user1, user2, user1_token, user2_token):
    """Test that users cannot update other users' todos."""
    # Create a todo for user1
    headers_user1 = {"Authorization": f"Bearer {user1_token}"}
    response = client.post("/todos/", json={"title": "User1's Todo"}, headers=headers_user1)
    assert response.status_code == 201
    todo_data = response.json()
    todo_id = todo_data["id"]

    # Verify user2 cannot update user1's todo
    headers_user2 = {"Authorization": f"Bearer {user2_token}"}
    update_payload = {"title": "Hacked Todo"}
    response = client.put(f"/todos/{todo_id}", json=update_payload, headers=headers_user2)
    assert response.status_code == 404  # Should return 404 since it doesn't exist for user2


def test_user_cannot_delete_other_users_todos(client, session, user1, user2, user1_token, user2_token):
    """Test that users cannot delete other users' todos."""
    # Create a todo for user1
    headers_user1 = {"Authorization": f"Bearer {user1_token}"}
    response = client.post("/todos/", json={"title": "User1's Todo"}, headers=headers_user1)
    assert response.status_code == 201
    todo_data = response.json()
    todo_id = todo_data["id"]

    # Verify user2 cannot delete user1's todo
    headers_user2 = {"Authorization": f"Bearer {user2_token}"}
    response = client.delete(f"/todos/{todo_id}", headers=headers_user2)
    assert response.status_code == 404  # Should return 404 since it doesn't exist for user2


def test_user_cannot_toggle_other_users_todos(client, session, user1, user2, user1_token, user2_token):
    """Test that users cannot toggle completion of other users' todos."""
    # Create a todo for user1
    headers_user1 = {"Authorization": f"Bearer {user1_token}"}
    response = client.post("/todos/", json={"title": "User1's Todo"}, headers=headers_user1)
    assert response.status_code == 201
    todo_data = response.json()
    todo_id = todo_data["id"]

    # Verify user2 cannot toggle user1's todo
    headers_user2 = {"Authorization": f"Bearer {user2_token}"}
    response = client.patch(f"/todos/{todo_id}/complete", headers=headers_user2)
    assert response.status_code == 404  # Should return 404 since it doesn't exist for user2


def test_user_sees_only_their_own_todos(client, session, user1, user2, user1_token, user2_token):
    """Test that each user sees only their own todos when listing."""
    # Create todos for user1
    headers_user1 = {"Authorization": f"Bearer {user1_token}"}
    client.post("/todos/", json={"title": "User1 Todo 1"}, headers=headers_user1)
    client.post("/todos/", json={"title": "User1 Todo 2"}, headers=headers_user1)

    # Create todos for user2
    headers_user2 = {"Authorization": f"Bearer {user2_token}"}
    client.post("/todos/", json={"title": "User2 Todo 1"}, headers=headers_user2)
    client.post("/todos/", json={"title": "User2 Todo 2"}, headers=headers_user2)
    client.post("/todos/", json={"title": "User2 Todo 3"}, headers=headers_user2)

    # Verify user1 sees only their own todos
    response = client.get("/todos/", headers=headers_user1)
    assert response.status_code == 200
    user1_todos = response.json()
    assert len(user1_todos) == 2
    for todo in user1_todos:
        assert todo["user_id"] == str(user1.id)

    # Verify user2 sees only their own todos
    response = client.get("/todos/", headers=headers_user2)
    assert response.status_code == 200
    user2_todos = response.json()
    assert len(user2_todos) == 3
    for todo in user2_todos:
        assert todo["user_id"] == str(user2.id)