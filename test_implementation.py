"""
Test script to verify the authentication and user isolation implementation.
This script checks that all the required components have been created.
"""

import os
from pathlib import Path

def check_backend_files():
    """Check that all required backend files exist."""
    backend_base = Path("backend/src")

    required_files = [
        "main.py",
        "database.py",
        "models/__init__.py",
        "models/user.py",
        "models/todo.py",
        "services/__init__.py",
        "services/auth_service.py",
        "services/todo_service.py",
        "api/__init__.py",
        "api/auth_router.py",
        "api/todo_router.py",
        "utils/__init__.py",
        "utils/jwt_utils.py",
        "middleware/__init__.py",
        "middleware/auth.py"
    ]

    print("Checking backend files...")
    all_found = True
    for file in required_files:
        file_path = backend_base / file
        if file_path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file}")
            all_found = False

    return all_found

def check_frontend_files():
    """Check that all required frontend files exist."""
    frontend_base = Path("frontend")

    required_files = [
        "pages/login.tsx",
        "pages/register.tsx",
        "pages/dashboard.tsx",
        "pages/todos.tsx",
        "pages/_app.tsx",
        "src/components/auth/LoginForm.tsx",
        "src/components/auth/RegisterForm.tsx",
        "src/components/todos/TodoItem.tsx",
        "src/pages/login.tsx",
        "src/pages/register.tsx",
        "src/pages/dashboard.tsx",
        "src/pages/todos.tsx",
        "src/services/auth.ts",
        "src/services/api.ts",
        "src/hooks/useAuth.ts",
        "src/types/index.ts"
    ]

    print("\nChecking frontend files...")
    all_found = True
    for file in required_files:
        file_path = frontend_base / file
        if file_path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file}")
            all_found = False

    return all_found

def check_config_files():
    """Check that configuration files exist."""
    print("\nChecking configuration files...")
    all_found = True

    config_files = [
        "backend/requirements.txt",
        "frontend/package.json",
        ".env.example",
        ".gitignore",
        "frontend/tsconfig.json",
        "frontend/tailwind.config.js",
        "frontend/postcss.config.js",
        "frontend/next.config.js",
        "frontend/styles/globals.css"
    ]

    for file in config_files:
        file_path = Path(file)
        if file_path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file}")
            all_found = False

    return all_found

def main():
    print("Verifying Authentication & User Isolation Implementation...\n")

    backend_ok = check_backend_files()
    frontend_ok = check_frontend_files()
    config_ok = check_config_files()

    print(f"\nResults:")
    print(f"Backend files: {'✓' if backend_ok else '✗'}")
    print(f"Frontend files: {'✓' if frontend_ok else '✗'}")
    print(f"Configuration files: {'✓' if config_ok else '✗'}")

    overall_success = backend_ok and frontend_ok and config_ok
    print(f"Overall: {'✓ SUCCESS' if overall_success else '✗ FAILURE'}")

    if overall_success:
        print("\nThe implementation appears to be complete!")
        print("All required components for the authentication and user isolation feature have been created.")
    else:
        print("\nSome components are missing. Please check the implementation.")

if __name__ == "__main__":
    main()