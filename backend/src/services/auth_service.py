from sqlmodel import Session, select
from typing import Optional
from datetime import timedelta
from ..models.user import User, UserCreate
from ..utils.jwt_utils import create_access_token, create_refresh_token
from ..auth.security import verify_password, get_password_hash as hash_password
import uuid


def authenticate_user(session: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user by email and password.

    Args:
        session (Session): Database session
        email (str): User's email
        password (str): User's plaintext password

    Returns:
        User: The authenticated user if credentials are valid, None otherwise
    """
    # Find user by email
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()

    if not user:
        # Don't reveal if user exists or not for security
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def create_user(session: Session, user_create: UserCreate) -> User:
    """
    Create a new user with the provided details.

    Args:
        session (Session): Database session
        user_create (UserCreate): User creation details

    Returns:
        User: The created user
    """
    # Check if user with this email already exists
    existing_user = session.exec(select(User).where(User.email == user_create.email)).first()
    if existing_user:
        raise ValueError("Email already registered")

    # Hash the password
    hashed_password = hash_password(user_create.password)

    # Create the user object
    db_user = User(
        email=user_create.email,
        hashed_password=hashed_password
    )

    # Add to session and commit
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """
    Get a user by their email address.

    Args:
        session (Session): Database session
        email (str): User's email address

    Returns:
        User: The user if found, None otherwise
    """
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    return user


def get_user_by_id(session: Session, user_id: uuid.UUID) -> Optional[User]:
    """
    Get a user by their ID.

    Args:
        session (Session): Database session
        user_id (uuid.UUID): User's ID

    Returns:
        User: The user if found, None otherwise
    """
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    return user


def create_access_token_for_user(user: User) -> str:
    """
    Create an access token for the given user.

    Args:
        user (User): The user to create a token for

    Returns:
        str: The access token
    """
    # Prepare data for the token
    data = {
        "sub": str(user.id),
        "email": user.email
    }

    # Create and return the token
    token = create_access_token(data=data)
    return token


def create_refresh_token_for_user(user: User) -> str:
    """
    Create a refresh token for the given user.

    Args:
        user (User): The user to create a refresh token for

    Returns:
        str: The refresh token
    """
    # Prepare data for the token
    data = {
        "sub": str(user.id),
        "email": user.email
    }

    # Create and return the refresh token
    token = create_refresh_token(data=data)
    return token


def verify_refresh_token(refresh_token: str) -> Optional[dict]:
    """
    Verify a refresh token and return the payload if valid.

    Args:
        refresh_token (str): The refresh token to verify

    Returns:
        dict: The decoded token payload if valid, None otherwise
    """
    from ..utils.jwt_utils import verify_token, is_refresh_token

    # First verify the token is valid
    payload = verify_token(refresh_token)

    if payload and is_refresh_token(refresh_token):
        return payload

    return None