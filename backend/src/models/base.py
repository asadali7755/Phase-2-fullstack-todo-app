from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime
import uuid

class Base(SQLModel):
    """Base class for all models with common fields."""

    def generate_uuid(self) -> str:
        """Generate a new UUID for the model."""
        return str(uuid.uuid4())

def get_current_time() -> datetime:
    """Get current time in UTC."""
    return datetime.utcnow()