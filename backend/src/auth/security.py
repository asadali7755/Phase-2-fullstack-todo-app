from passlib.context import CryptContext
import logging

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a plaintext password."""
    # Truncate password to 72 bytes maximum to comply with bcrypt limits
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # Truncate to 72 bytes and decode back to string
        password = password_bytes[:72].decode('utf-8', errors='ignore')
        logging.info(f"Truncated password to 72 bytes for bcrypt compatibility")
    
    logging.info(f"Attempting to hash password of length: {len(password.encode('utf-8'))} bytes")
    return pwd_context.hash(password)