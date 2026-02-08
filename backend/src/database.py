from sqlmodel import create_engine, Session
from sqlalchemy.pool import QueuePool
from typing import Generator
from .config import settings

# Create engine with connection pooling settings
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG  # Enable SQL logging in debug mode
)

def get_session() -> Generator[Session, None, None]:
    """
    Get a database session.

    Yields:
        Session: A database session
    """
    with Session(engine) as session:
        yield session