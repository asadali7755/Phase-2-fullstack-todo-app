from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class TodoCreateDTO(BaseModel):
    """Data transfer object for creating a new todo."""
    title: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class TodoUpdateDTO(BaseModel):
    """Data transfer object for updating an existing todo."""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

    class Config:
        from_attributes = True


class TodoResponseDTO(BaseModel):
    """Data transfer object for returning todo information."""
    id: uuid.UUID
    title: str
    description: Optional[str]
    completed: bool
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True