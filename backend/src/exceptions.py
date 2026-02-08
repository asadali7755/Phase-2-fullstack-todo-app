"""Custom exceptions for the Todo API."""

from typing import Optional
from fastapi import HTTPException, status


class TodoException(HTTPException):
    """Base exception class for Todo API errors."""

    def __init__(self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(status_code=status_code, detail=detail)


class TodoNotFoundException(TodoException):
    """Raised when a requested todo is not found."""

    def __init__(self, todo_id: str):
        super().__init__(
            detail=f"Todo with ID {todo_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class TodoAccessDeniedException(TodoException):
    """Raised when a user attempts to access another user's todo."""

    def __init__(self, todo_id: str):
        super().__init__(
            detail=f"Access denied to todo with ID {todo_id}",
            status_code=status.HTTP_403_FORBIDDEN
        )


class TodoValidationException(TodoException):
    """Raised when todo data validation fails."""

    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


class UserNotFoundException(TodoException):
    """Raised when a requested user is not found."""

    def __init__(self, user_id: str):
        super().__init__(
            detail=f"User with ID {user_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class DatabaseConnectionException(TodoException):
    """Raised when there's a database connection issue."""

    def __init__(self, detail: Optional[str] = None):
        super().__init__(
            detail=detail or "Database connection failed",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class JWTTokenException(TodoException):
    """Raised when JWT token validation fails."""

    def __init__(self, detail: str = "Invalid or expired token"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class InputValidationException(TodoException):
    """Raised when input validation fails."""

    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )