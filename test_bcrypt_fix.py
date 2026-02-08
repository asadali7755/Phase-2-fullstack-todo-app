#!/usr/bin/env python3
"""
Test script to verify the bcrypt password truncation fix
"""

import sys
sys.path.append('/mnt/e/course/hackthon2_todo-app/PHASE22/backend')

# Test the password truncation logic
def test_password_truncation():
    print("Testing password truncation logic...")

    # Import the password hashing function
    from backend.src.services.auth_service import hash_password

    # Test cases
    test_passwords = [
        "short",          # Too short (should fail validation at model level)
        "password123",    # Within limits
        "a" * 50,         # Within limits
        "a" * 72,         # At bcrypt limit
        "a" * 80,         # Over bcrypt limit (should be truncated)
        "a" * 100,        # Way over bcrypt limit (should be truncated)
    ]

    for i, pwd in enumerate(test_passwords):
        try:
            if len(pwd) < 8:
                print(f"Test {i+1}: Password '{pwd[:10]}...' ({len(pwd)} chars) - SKIPPED (too short)")
                continue

            print(f"Test {i+1}: Password '{pwd[:10]}...' ({len(pwd)} chars) - Attempting to hash...")

            # This should not throw an error now
            hashed = hash_password(pwd)
            print(f"         SUCCESS: Password hashed successfully (original: {len(pwd)} chars)")
        except Exception as e:
            print(f"         ERROR: {e}")

    print("\nTesting complete!")

if __name__ == "__main__":
    test_password_truncation()