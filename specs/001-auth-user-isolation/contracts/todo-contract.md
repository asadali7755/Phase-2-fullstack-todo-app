# Todo API Contract

## Overview
This document defines the API contract for todo management functionality in the Todo application. All endpoints require JWT-based authentication and enforce user isolation as specified in the project constitution.

## Base URL
`/api/v1/todos`

## Authentication Headers
All requests must include:
```
Authorization: Bearer <JWT_TOKEN>
```

## User Isolation
All endpoints enforce user isolation by:
1. Verifying the JWT and extracting the authenticated user ID
2. Filtering all data access to only include records owned by the authenticated user
3. Returning 403 Forbidden when attempting to access resources owned by other users

## Endpoints

### GET /
Retrieve all todos for the authenticated user.

#### Request
Headers:
```
Authorization: Bearer <JWT_TOKEN>
```

#### Response (200 OK)
```json
[
  {
    "id": "uuid-string",
    "title": "Todo title",
    "description": "Todo description",
    "completed": false,
    "user_id": "authenticated-user-id",
    "created_at": "2026-01-28T10:00:00Z",
    "updated_at": "2026-01-28T10:00:00Z"
  }
]
```

#### Error Responses
- `401 Unauthorized`: Invalid or expired token

### POST /
Create a new todo for the authenticated user.

#### Request
Headers:
```
Authorization: Bearer <JWT_TOKEN>
```

Body:
```json
{
  "title": "New todo title",
  "description": "New todo description",
  "completed": false
}
```

#### Response (201 Created)
```json
{
  "id": "uuid-string",
  "title": "New todo title",
  "description": "New todo description",
  "completed": false,
  "user_id": "authenticated-user-id",
  "created_at": "2026-01-28T10:00:00Z",
  "updated_at": "2026-01-28T10:00:00Z"
}
```

#### Error Responses
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Invalid or expired token

### GET /{id}
Retrieve a specific todo by ID for the authenticated user.

#### Request
Headers:
```
Authorization: Bearer <JWT_TOKEN>
```

Path Parameters:
- `id`: UUID of the todo to retrieve

#### Response (200 OK)
```json
{
  "id": "uuid-string",
  "title": "Todo title",
  "description": "Todo description",
  "completed": false,
  "user_id": "authenticated-user-id",
  "created_at": "2026-01-28T10:00:00Z",
  "updated_at": "2026-01-28T10:00:00Z"
}
```

#### Error Responses
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: Attempting to access a todo owned by another user
- `404 Not Found`: Todo with the specified ID does not exist

### PUT /{id}
Update a specific todo by ID for the authenticated user.

#### Request
Headers:
```
Authorization: Bearer <JWT_TOKEN>
```

Path Parameters:
- `id`: UUID of the todo to update

Body:
```json
{
  "title": "Updated todo title",
  "description": "Updated todo description",
  "completed": true
}
```

#### Response (200 OK)
```json
{
  "id": "uuid-string",
  "title": "Updated todo title",
  "description": "Updated todo description",
  "completed": true,
  "user_id": "authenticated-user-id",
  "created_at": "2026-01-28T10:00:00Z",
  "updated_at": "2026-01-28T11:00:00Z"
}
```

#### Error Responses
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: Attempting to access a todo owned by another user
- `404 Not Found`: Todo with the specified ID does not exist

### DELETE /{id}
Delete a specific todo by ID for the authenticated user.

#### Request
Headers:
```
Authorization: Bearer <JWT_TOKEN>
```

Path Parameters:
- `id`: UUID of the todo to delete

#### Response (204 No Content)

#### Error Responses
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: Attempting to access a todo owned by another user
- `404 Not Found`: Todo with the specified ID does not exist