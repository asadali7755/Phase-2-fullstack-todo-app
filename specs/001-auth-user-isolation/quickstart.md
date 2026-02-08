# Quickstart Guide: Authentication & User Isolation for Todo Full-Stack Web Application

## Overview
This guide provides a quick overview of the authentication system implementation for the todo application, focusing on JWT-based authentication and user isolation.

## Architecture
The authentication system follows a stateless, JWT-based approach with clear separation between frontend and backend:

1. **Frontend** (Next.js + Better Auth):
   - Handles user registration and login UI
   - Manages JWT storage and transmission
   - Implements user session management

2. **Backend** (FastAPI):
   - Validates JWTs using shared secret
   - Enforces user data isolation
   - Provides authenticated API endpoints

## Key Components

### JWT Structure
Access tokens contain the following claims:
- `sub`: User ID
- `email`: User's email address
- `exp`: Expiration timestamp
- `iat`: Issuance timestamp

### Authentication Flow
1. User registers/logs in via frontend forms
2. Backend issues JWT upon successful authentication
3. Frontend stores JWT and includes in Authorization header for API calls
4. Backend validates JWT and extracts user identity for data isolation
5. Backend returns only data belonging to the authenticated user

### User Isolation
- All API endpoints validate user ownership of requested resources
- Database queries include user ID filters to prevent cross-user access
- Authorization checks occur before any data modification

## Environment Setup
Required environment variables:
- `BETTER_AUTH_SECRET`: Secret key for JWT signing
- `DATABASE_URL`: Connection string for Neon PostgreSQL database
- `JWT_EXPIRATION_DELTA`: Token expiration time (in seconds)

## Running the System
1. Start the backend server
2. Start the frontend application
3. Register a new user or log in with existing credentials
4. Access protected endpoints - JWT will be automatically included in requests
5. Verify that users can only access their own data

## Testing Authentication
- Test successful registration and login
- Verify JWT is included in API requests
- Test authentication failure scenarios (invalid/expired tokens)
- Confirm user isolation by attempting cross-user access