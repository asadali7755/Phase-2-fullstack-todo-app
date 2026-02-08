"""
Database initialization script for the Todo application.
This script creates all necessary tables in the database.
"""
import os
import sys
from sqlmodel import SQLModel, create_engine

# Add the src directory to the path so we can import the models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def init_database():
    # Get database URL from environment variable
    # Explicitly set the database to SQLite for initialization
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo_app.db")
    
    # Override with SQLite if it's the default PostgreSQL URL
    if "neondb_owner" in DATABASE_URL:
        DATABASE_URL = "sqlite:///./todo_app.db"

    print(f"Initializing database with URL: {DATABASE_URL}")

    # Create the engine
    engine = create_engine(DATABASE_URL, echo=True)

    # Import models here to ensure they're registered with SQLModel
    from src.models import user, todo  # Import to register models

    # Create all tables
    print("Creating database tables...")
    SQLModel.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()