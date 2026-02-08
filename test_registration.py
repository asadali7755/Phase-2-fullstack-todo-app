#!/usr/bin/env python3
"""
Test script to debug the user registration issue
"""
import requests
import json

def test_registration():
    url = "http://localhost:8000/auth/register"

    # Test data
    user_data = {
        "email": "leoali851@gmail.com",
        "password": "Malikx1@"
    }

    print(f"Testing registration with:")
    print(f"  Email: {user_data['email']}")
    print(f"  Password: {user_data['password']} (length: {len(user_data['password'])})")

    try:
        response = requests.post(url, json=user_data)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

        if response.status_code == 200:
            print("SUCCESS: User registered!")
            return True
        else:
            print("FAILED: Registration failed")
            return False

    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to the server. Is it running?")
        return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_registration()