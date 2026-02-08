"""
Models package for the Todo application backend.
Contains data models for User and Todo entities.
"""

from . import user
from . import todo

# Import all models to ensure they're loaded together to avoid circular imports
from .user import User, UserBase, UserRead, UserCreate, UserUpdate
from .todo import Todo, TodoBase, TodoRead, TodoCreate, TodoUpdate, TodoListResponse

__all__ = [
    "User",
    "UserBase", 
    "UserRead",
    "UserCreate",
    "UserUpdate",
    "Todo",
    "TodoBase",
    "TodoRead",
    "TodoCreate", 
    "TodoUpdate",
    "TodoListResponse"
]