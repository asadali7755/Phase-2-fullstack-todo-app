#!/usr/bin/env python3
"""
Test script to verify frontend can connect to backend authentication endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoints():
    print("Testing backend authentication endpoints...")

    # Test registration
    print("\n1. Testing registration endpoint:")
    reg_response = requests.post(
        f"{BASE_URL}/auth/register",
        headers={"Content-Type": "application/json"},
        json={"email": "test@example.com", "password": "testpassword"}
    )
    print(f"   Registration status: {reg_response.status_code}")
    if reg_response.status_code == 201:
        print("   ✓ Registration successful")
        user_data = reg_response.json()
        print(f"   User ID: {user_data.get('id')}")
    elif reg_response.status_code == 409:
        print("   - User already exists (expected for repeated tests)")
    else:
        print(f"   ✗ Registration failed: {reg_response.text}")

    # Test login
    print("\n2. Testing login endpoint:")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        params={"email": "test@example.com", "password": "testpassword"}
    )
    print(f"   Login status: {login_response.status_code}")
    if login_response.status_code == 200:
        print("   ✓ Login successful")
        token_data = login_response.json()
        print(f"   Access token received: {'yes' if token_data.get('access_token') else 'no'}")
    else:
        print(f"   ✗ Login failed: {login_response.text}")

    # Test /me endpoint with a token (if available)
    print("\n3. Testing /me endpoint:")
    if login_response.status_code == 200:
        token_data = login_response.json()
        access_token = token_data.get('access_token')
        if access_token:
            me_response = requests.get(
                f"{BASE_URL}/auth/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            print(f"   /me status: {me_response.status_code}")
            if me_response.status_code == 200:
                print("   ✓ /me endpoint working")
                user_info = me_response.json()
                print(f"   User email: {user_info.get('email')}")
            else:
                print(f"   ✗ /me failed: {me_response.text}")

    print("\n4. Testing logout endpoint:")
    logout_response = requests.post(f"{BASE_URL}/auth/logout")
    print(f"   Logout status: {logout_response.status_code}")
    if logout_response.status_code == 200:
        print("   ✓ Logout endpoint working")
    else:
        print(f"   ✗ Logout failed: {logout_response.text}")

if __name__ == "__main__":
    test_endpoints()