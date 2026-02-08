#!/usr/bin/env python3
"""
Test script to register a user directly using the service functions
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.src.database import engine
from backend.src.models.user import UserCreate
from backend.src.services.auth_service import create_user
from sqlmodel import Session

def test_direct_registration():
    # Create a session
    with Session(engine) as session:
        # Create user data
        user_data = UserCreate(
            email="leoali851@gmail.com",
            password="Malikx1@"
        )

        print(f"Attempting to create user:")
        print(f"  Email: {user_data.email}")
        print(f"  Password: {'*' * len(user_data.password)} (length: {len(user_data.password)})")

        try:
            # Try to create the user directly using the service
            created_user = create_user(session, user_data)
            print(f"SUCCESS: User created with ID: {created_user.id}")
            print(f"Email: {created_user.email}")
            return True
        except ValueError as e:
            print(f"VALUE ERROR: {str(e)}")
            return False
        except Exception as e:
            print(f"EXCEPTION: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    test_direct_registration()