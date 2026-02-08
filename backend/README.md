# Todo API Backend

Backend API for Todo Full-Stack Web Application built with FastAPI and SQLModel.

## Features

- RESTful API for todo management
- JWT-based authentication and authorization
- User isolation - users can only access their own todos
- Pagination support
- Comprehensive error handling
- Structured logging
- Database connection pooling
- Input validation and sanitization

## Tech Stack

- Python 3.11+
- FastAPI
- SQLModel (SQLAlchemy + Pydantic)
- Neon Serverless PostgreSQL
- PyJWT for authentication
- Passlib for password hashing

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables (see `.env.example`)

## Environment Variables

Create a `.env` file with the following variables:

```
DATABASE_URL=postgresql://username:password@host:port/database
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=False
```

## Running the Application

```bash
# Run the application
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or using the main.py directly
python src/main.py
```

## API Endpoints

### Authentication

All endpoints require a valid JWT token in the Authorization header:
`Authorization: Bearer <token>`

### Todo Management

#### Create Todo
- `POST /todos/`
- Request Body: `{"title": "string", "description": "string"}`
- Response: 201 Created with Todo object

#### Get Todos (List)
- `GET /todos/`
- Query Parameters: `limit`, `offset`, `completed`
- Response: 200 OK with paginated TodoListResponse

#### Get Todo by ID
- `GET /todos/{id}`
- Response: 200 OK with Todo object

#### Update Todo
- `PUT /todos/{id}`
- Request Body: `{"title": "string", "description": "string", "completed": boolean}`
- Response: 200 OK with updated Todo object

#### Delete Todo
- `DELETE /todos/{id}`
- Response: 204 No Content

#### Toggle Todo Completion
- `PATCH /todos/{id}/complete`
- Response: 200 OK with updated Todo object

## Health Check

- `GET /health`
- Returns service health status

## Error Handling

Common error responses:
- `401 Unauthorized`: Invalid or missing JWT token
- `403 Forbidden`: User attempting to access another user's resources
- `404 Not Found`: Resource does not exist
- `422 Unprocessable Entity`: Invalid request data
- `500 Internal Server Error`: Server error

## Running Tests

```bash
# Install test dependencies
pip install pytest httpx

# Run all tests
pytest

# Run specific test file
pytest tests/path/to/test_file.py

# Run with coverage
pytest --cov=src tests/
```

## Database Migrations

The application uses SQLModel for database operations. For production deployments, you may want to set up Alembic for migrations.

## Security

- JWT tokens are required for all endpoints
- Users can only access their own todos
- Input validation is performed on all endpoints
- SQL injection is prevented through ORM usage
- Passwords are hashed using bcrypt

## Performance

- Connection pooling configured for database
- Pagination available for list endpoints
- Proper indexing on database columns
- Efficient querying with proper filters