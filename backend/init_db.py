"""
Database initialization script for the Todo application.
This script creates all necessary tables in the database.
"""
from sqlmodel import SQLModel, create_engine
import os
from src.models.user import User
from src.models.todo import Todo

def init_database():
    # Get database URL from environment variable
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo_app.db")

    print(f"Initializing database with URL: {DATABASE_URL}")

    # Create the engine
    engine = create_engine(DATABASE_URL, echo=True)

    # Create all tables
    print("Creating database tables...")
    SQLModel.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()