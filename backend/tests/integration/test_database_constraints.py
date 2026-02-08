import pytest
from sqlmodel import Session, create_engine, select
from sqlmodel.pool import StaticPool
from sqlalchemy.exc import IntegrityError
import uuid

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.models.todo import Todo
from src.models.user import User
from src.services.todo_service import TodoService


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


def test_database_constraints_user_id_foreign_key(session):
    """Test that foreign key constraint prevents orphaned todos."""
    # Create a todo with a non-existent user_id - this should fail with integrity error
    fake_user_id = uuid.uuid4()

    # Directly creating a todo without using the service to test constraint
    todo = Todo(
        title="Test Todo",
        user_id=fake_user_id
    )

    session.add(todo)
    with pytest.raises(IntegrityError):
        session.commit()


def test_database_constraints_user_email_unique(session):
    """Test that unique constraint prevents duplicate emails."""
    # Create first user
    user1 = User(
        email="test@example.com",
        hashed_password="hashed_password_here"
    )
    session.add(user1)
    session.commit()
    session.refresh(user1)

    # Try to create another user with same email - should fail
    user2 = User(
        email="test@example.com",  # Same email as user1
        hashed_password="another_hashed_password"
    )
    session.add(user2)
    with pytest.raises(IntegrityError):
        session.commit()


def test_data_persistence_across_sessions(engine):
    """Test that data persists across different database sessions."""
    from backend.src.models.base import SQLModel

    # Create first session and add data
    SQLModel.metadata.create_all(bind=engine)
    with Session(engine) as session1:
        user = User(
            email="persistent@example.com",
            hashed_password="hashed_password"
        )
        session1.add(user)
        session1.commit()
        session1.refresh(user)

        todo = Todo(
            title="Persistent Todo",
            user_id=user.id
        )
        session1.add(todo)
        session1.commit()
        session1.refresh(todo)

        user_id = user.id
        todo_id = todo.id

    # Create second session and verify data still exists
    with Session(engine) as session2:
        # Check user exists
        user_query = select(User).where(User.id == user_id)
        retrieved_user = session2.exec(user_query).first()
        assert retrieved_user is not None
        assert retrieved_user.email == "persistent@example.com"

        # Check todo exists
        todo_query = select(Todo).where(Todo.id == todo_id)
        retrieved_todo = session2.exec(todo_query).first()
        assert retrieved_todo is not None
        assert retrieved_todo.title == "Persistent Todo"
        assert retrieved_todo.user_id == user_id


def test_todo_title_length_constraint(session):
    """Test that title length constraints are enforced."""
    user = User(
        email="constraint_test@example.com",
        hashed_password="hashed_password"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Test that a very long title (over 255 chars) causes validation error
    long_title = "t" * 256  # 256 characters, exceeding the limit

    with pytest.raises(ValueError, match="Title must be between 1-255 characters"):
        Todo(title=long_title)


def test_todo_description_length_constraint(session):
    """Test that description length constraints are enforced."""
    user = User(
        email="constraint_test2@example.com",
        hashed_password="hashed_password"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Test that a very long description (over 1000 chars) causes validation error
    long_description = "d" * 1001  # 1001 characters, exceeding the limit

    with pytest.raises(ValueError, match="Description must be ≤ 1000 characters if provided"):
        Todo(title="Valid Title", description=long_description)


def test_concurrent_database_operations(engine):
    """Test concurrent database operations for data integrity."""
    from backend.src.models.base import SQLModel
    from threading import Thread
    import time

    # Create database schema
    SQLModel.metadata.create_all(bind=engine)

    # Create a user first
    with Session(engine) as session:
        user = User(
            email="concurrent@example.com",
            hashed_password="hashed_password"
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        user_id = user.id

    # Function to create todos concurrently
    def create_todos(start_idx, num_todos):
        for i in range(num_todos):
            with Session(engine) as session:
                todo = Todo(
                    title=f"Concurrent Todo {start_idx + i}",
                    user_id=user_id
                )
                session.add(todo)
                session.commit()

    # Create multiple threads to simulate concurrent operations
    threads = []
    for t in range(3):
        thread = Thread(target=create_todos, args=(t * 10, 10))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Verify all todos were created correctly
    with Session(engine) as session:
        todos = session.exec(select(Todo).where(Todo.user_id == user_id)).all()
        assert len(todos) == 30  # 3 threads * 10 todos each

        # Check for duplicates or inconsistencies
        titles = [todo.title for todo in todos]
        assert len(set(titles)) == len(titles)  # All titles should be unique