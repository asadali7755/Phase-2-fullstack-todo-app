# Authentication API Contract

## Overview
This document defines the API contract for user authentication functionality in the Todo application. All endpoints require JWT-based authentication as specified in the project constitution.

## Base URL
`/api/v1/auth`

## Authentication Headers
All authenticated requests must include:
```
Authorization: Bearer <JWT_TOKEN>
```

## Endpoints

### POST /register
Register a new user account.

#### Request
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

#### Response (201 Created)
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "created_at": "2026-01-28T10:00:00Z"
}
```

#### Error Responses
- `400 Bad Request`: Invalid input (e.g., malformed email, weak password)
- `409 Conflict`: Email already exists

### POST /login
Authenticate user and return JWT.

#### Request
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

#### Response (200 OK)
```json
{
  "access_token": "jwt-token-string",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### Error Responses
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Invalid credentials

### POST /logout
Log out the current user and invalidate their session.

#### Request
Headers:
```
Authorization: Bearer <JWT_TOKEN>
```

#### Response (200 OK)
```json
{
  "message": "Successfully logged out"
}
```

#### Error Responses
- `401 Unauthorized`: Invalid or expired token

### GET /me
Retrieve information about the currently authenticated user.

#### Request
Headers:
```
Authorization: Bearer <JWT_TOKEN>
```

#### Response (200 OK)
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "created_at": "2026-01-28T10:00:00Z"
}
```

#### Error Responses
- `401 Unauthorized`: Invalid or expired token