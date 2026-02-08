# API Contracts: Frontend-Backend Communication for Todo Application

## Base API Configuration
**Base URL**: `https://api.todoapp.com/v1` (or `http://localhost:8000/v1` for development)

## Authentication
All endpoints require JWT token in Authorization header:
`Authorization: Bearer <jwt_token>`

## Common Response Structure
```typescript
interface ApiResponse<T> {
  data?: T;
  error?: {
    message: string;
    code?: string;
    details?: Record<string, any>;
  };
  success: boolean;
}
```

## API Endpoints

### Authentication Endpoints
**POST** `/auth/register`
- **Description**: Register a new user account
- **Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "confirmPassword": "securePassword123"
}
```
- **Success Response**: `201 Created`
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid-string",
      "email": "user@example.com"
    }
  }
}
```
- **Error Responses**: 400 Bad Request (validation errors), 409 Conflict (email exists)

**POST** `/auth/login`
- **Description**: Authenticate user and return JWT token
- **Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```
- **Success Response**: `200 OK`
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid-string",
      "email": "user@example.com"
    },
    "token": "jwt-token-string"
  }
}
```
- **Error Responses**: 400 Bad Request (validation errors), 401 Unauthorized (invalid credentials)

### Todo Management Endpoints

**GET** `/todos`
- **Description**: Get all todos for the authenticated user
- **Query Parameters**:
  - `limit`: Number (default: 50, max: 100)
  - `offset`: Number (default: 0)
  - `completed`: Boolean (optional, filter by completion status)
- **Success Response**: `200 OK`
```json
{
  "success": true,
  "data": {
    "todos": [
      {
        "id": "uuid-string",
        "title": "Todo title",
        "description": "Optional description",
        "completed": false,
        "user_id": "user-uuid",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
      }
    ],
    "total": 1,
    "offset": 0,
    "limit": 50
  }
}
```
- **Error Responses**: 401 Unauthorized, 500 Internal Server Error

**POST** `/todos`
- **Description**: Create a new todo for the authenticated user
- **Request Body**:
```json
{
  "title": "New todo title",
  "description": "Optional description"
}
```
- **Success Response**: `201 Created`
```json
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "title": "New todo title",
    "description": "Optional description",
    "completed": false,
    "user_id": "user-uuid",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```
- **Error Responses**: 401 Unauthorized, 422 Unprocessable Entity (validation errors), 500 Internal Server Error

**GET** `/todos/{id}`
- **Description**: Get a specific todo by ID for the authenticated user
- **Path Parameter**: `id` (UUID)
- **Success Response**: `200 OK`
```json
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "title": "Todo title",
    "description": "Optional description",
    "completed": false,
    "user_id": "user-uuid",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```
- **Error Responses**: 401 Unauthorized, 403 Forbidden, 404 Not Found, 500 Internal Server Error

**PUT** `/todos/{id}`
- **Description**: Update a specific todo by ID for the authenticated user
- **Path Parameter**: `id` (UUID)
- **Request Body**:
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "completed": true
}
```
- **Success Response**: `200 OK`
```json
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "title": "Updated title",
    "description": "Updated description",
    "completed": true,
    "user_id": "user-uuid",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-02T00:00:00Z"
  }
}
```
- **Error Responses**: 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Unprocessable Entity, 500 Internal Server Error

**DELETE** `/todos/{id}`
- **Description**: Delete a specific todo by ID for the authenticated user
- **Path Parameter**: `id` (UUID)
- **Success Response**: `204 No Content`
```json
{
  "success": true
}
```
- **Error Responses**: 401 Unauthorized, 403 Forbidden, 404 Not Found, 500 Internal Server Error

**PATCH** `/todos/{id}/complete`
- **Description**: Toggle the completion status of a specific todo
- **Path Parameter**: `id` (UUID)
- **Request Body**: Empty
- **Success Response**: `200 OK`
```json
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "title": "Todo title",
    "description": "Optional description",
    "completed": true,
    "user_id": "user-uuid",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-02T00:00:00Z"
  }
}
```
- **Error Responses**: 401 Unauthorized, 403 Forbidden, 404 Not Found, 500 Internal Server Error

## Error Response Format
```json
{
  "success": false,
  "error": {
    "message": "Human-readable error message",
    "code": "ERROR_CODE",
    "details": {
      "field": "specific field causing the error"
    }
  }
}
```

## Common Error Codes
- `UNAUTHORIZED`: 401 - Invalid or missing JWT token
- `FORBIDDEN`: 403 - User attempting to access another user's resources
- `NOT_FOUND`: 404 - Resource does not exist
- `VALIDATION_ERROR`: 422 - Invalid request data
- `INTERNAL_ERROR`: 500 - Server error