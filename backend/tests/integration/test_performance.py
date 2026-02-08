import pytest
import time
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool
import uuid
import statistics

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.main import app
from src.database import get_session
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
        email="perf-test@example.com",
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


def test_performance_response_times(client, valid_token):
    """Test that API responses meet performance requirements (<2 seconds 95% of the time)."""
    headers = {"Authorization": f"Bearer {valid_token}"}

    response_times = []

    # Make multiple requests to measure response times
    for i in range(20):
        start_time = time.time()

        # Create a todo
        payload = {"title": f"Performance Test Todo {i}", "description": f"Test description {i}"}
        response = client.post("/todos/", json=payload, headers=headers)
        assert response.status_code == 201

        # Get the todo
        todo_id = response.json()["id"]
        get_response = client.get(f"/todos/{todo_id}", headers=headers)
        assert get_response.status_code == 200

        # Update the todo
        update_payload = {"title": f"Updated Performance Test Todo {i}"}
        put_response = client.put(f"/todos/{todo_id}", json=update_payload, headers=headers)
        assert put_response.status_code == 200

        end_time = time.time()
        response_times.append(end_time - start_time)

    # Calculate 95th percentile
    response_times.sort()
    percentile_95 = response_times[int(len(response_times) * 0.95)]

    # Verify 95% of requests respond within 2 seconds
    assert percentile_95 < 2.0, f"95th percentile response time ({percentile_95}s) exceeds 2 seconds"


def test_performance_list_endpoint(client, valid_token, session, mock_user):
    """Test performance of the list endpoint with multiple todos."""
    headers = {"Authorization": f"Bearer {valid_token}"}

    # Create 50 todos
    for i in range(50):
        payload = {"title": f"Batch Todo {i}"}
        response = client.post("/todos/", json=payload, headers=headers)
        assert response.status_code == 201

    # Measure time to fetch all todos
    start_time = time.time()
    response = client.get("/todos/", headers=headers)
    end_time = time.time()

    assert response.status_code == 200
    assert len(response.json()) == 50
    assert (end_time - start_time) < 2.0, f"List endpoint took {(end_time - start_time)}s, exceeds 2 seconds"


def test_performance_pagination(client, valid_token, session, mock_user):
    """Test performance of pagination parameters."""
    headers = {"Authorization": f"Bearer {valid_token}"}

    # Create 100 todos
    for i in range(100):
        payload = {"title": f"Paging Todo {i}"}
        response = client.post("/todos/", json=payload, headers=headers)
        assert response.status_code == 201

    # Test pagination performance
    start_time = time.time()
    response = client.get("/todos/?limit=10&offset=0", headers=headers)
    first_page_time = time.time() - start_time

    assert response.status_code == 200
    assert len(response.json()) <= 10
    assert first_page_time < 1.0, f"First page took {first_page_time}s, exceeds 1 second"

    start_time = time.time()
    response = client.get("/todos/?limit=10&offset=50", headers=headers)
    middle_page_time = time.time() - start_time

    assert response.status_code == 200
    assert len(response.json()) <= 10
    assert middle_page_time < 1.0, f"Middle page took {middle_page_time}s, exceeds 1 second"


def test_single_request_performance(client, valid_token):
    """Test that individual requests are fast."""
    headers = {"Authorization": f"Bearer {valid_token}"}

    # Test create performance
    start_time = time.time()
    payload = {"title": "Quick Test Todo", "description": "Quick description"}
    response = client.post("/todos/", json=payload, headers=headers)
    create_time = time.time() - start_time

    assert response.status_code == 201
    assert create_time < 1.0, f"Create request took {create_time}s, exceeds 1 second"

    todo_id = response.json()["id"]

    # Test get performance
    start_time = time.time()
    response = client.get(f"/todos/{todo_id}", headers=headers)
    get_time = time.time() - start_time

    assert response.status_code == 200
    assert get_time < 0.5, f"Get request took {get_time}s, exceeds 0.5 seconds"

    # Test update performance
    start_time = time.time()
    update_payload = {"title": "Updated Quick Test Todo"}
    response = client.put(f"/todos/{todo_id}", json=update_payload, headers=headers)
    update_time = time.time() - start_time

    assert response.status_code == 200
    assert update_time < 0.5, f"Update request took {update_time}s, exceeds 0.5 seconds"

    # Test delete performance
    start_time = time.time()
    response = client.delete(f"/todos/{todo_id}", headers=headers)
    delete_time = time.time() - start_time

    assert response.status_code == 204
    assert delete_time < 0.5, f"Delete request took {delete_time}s, exceeds 0.5 seconds"


def test_concurrent_performance(client, valid_token):
    """Test performance under concurrent load."""
    import threading
    import queue

    headers = {"Authorization": f"Bearer {valid_token}"}
    result_queue = queue.Queue()

    def make_requests(thread_id):
        """Function to run in each thread."""
        thread_results = []
        for i in range(5):  # Each thread makes 5 requests
            start_time = time.time()

            payload = {"title": f"Thread {thread_id} Todo {i}"}
            response = client.post("/todos/", json=payload, headers=headers)

            end_time = time.time()
            thread_results.append((response.status_code, end_time - start_time))

        result_queue.put(thread_results)

    # Create and start multiple threads
    threads = []
    for i in range(5):  # 5 concurrent threads
        thread = threading.Thread(target=make_requests, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Collect and analyze results
    all_results = []
    while not result_queue.empty():
        all_results.extend(result_queue.get())

    # Verify all requests succeeded
    for status_code, _ in all_results:
        assert status_code == 201

    # Calculate average response time
    response_times = [time_taken for _, time_taken in all_results]
    avg_response_time = sum(response_times) / len(response_times)

    # Verify average response time is reasonable under concurrent load
    assert avg_response_time < 1.0, f"Average response time under concurrent load ({avg_response_time}s) exceeds 1 second"

    # Calculate 95th percentile
    response_times.sort()
    percentile_95 = response_times[int(len(response_times) * 0.95)] if response_times else 0

    assert percentile_95 < 2.0, f"95th percentile response time under concurrent load ({percentile_95}s) exceeds 2 seconds"