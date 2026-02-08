from typing import Generator
from src.database import get_session as get_db_session
from sqlmodel import Session

def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session."""
    db_session_gen = get_db_session()
    try:
        db = next(db_session_gen)
        yield db
    finally:
        db.close()