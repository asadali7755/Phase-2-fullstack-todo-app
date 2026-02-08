# Quickstart Guide: Backend API & Database Layer for Todo Full-Stack Web Application

## Prerequisites
- Python 3.11+
- pip package manager
- Git
- Neon Serverless PostgreSQL account (or local PostgreSQL for development)

## Setup Instructions

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 3. Environment Variables
Create `.env` file in the backend directory:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/todo_app
NEON_DATABASE_URL=your_neon_connection_string  # For production
SECRET_KEY=your_jwt_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Database Setup
```bash
# Initialize database (if not already done)
python backend/init_db.py

# Or for Neon PostgreSQL
python backend/init_neon_db.py
```

## Running the Application

### Development Mode
```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
cd backend
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## API Usage Examples

### Authentication
First, obtain a JWT token from the authentication service (assumed to be implemented separately):
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
```

### Create a Todo
```bash
curl -X POST http://localhost:8000/todos \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn FastAPI", "description": "Complete the tutorial"}'
```

### Get All Todos
```bash
curl -X GET http://localhost:8000/todos \
  -H "Authorization: Bearer <your-jwt-token>"
```

### Update a Todo
```bash
curl -X PUT http://localhost:8000/todos/<todo-id> \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title", "completed": true}'
```

### Delete a Todo
```bash
curl -X DELETE http://localhost:8000/todos/<todo-id> \
  -H "Authorization: Bearer <your-jwt-token>"
```

## Testing

### Run Unit Tests
```bash
cd backend
pytest tests/unit/ -v
```

### Run Integration Tests
```bash
cd backend
pytest tests/integration/ -v
```

### Run Contract Tests
```bash
cd backend
pytest tests/contract/ -v
```

## Project Structure
```
backend/
├── src/
│   ├── models/          # SQLModel database models
│   ├── api/             # FastAPI route handlers
│   ├── services/        # Business logic and data access
│   ├── auth/            # JWT authentication utilities
│   └── database.py      # Database connection management
├── tests/
│   ├── unit/            # Individual component tests
│   ├── integration/     # API and database integration tests
│   └── contract/        # API contract compliance tests
├── requirements.txt     # Python dependencies
└── init_db.py          # Database initialization script
```

## Key Components

### Models (src/models/)
- `todo.py`: Todo SQLModel definition
- `user.py`: User SQLModel definition

### API Routes (src/api/)
- `todos.py`: Todo-related endpoints
- `auth.py`: Authentication endpoints (dependency)

### Services (src/services/)
- `todo_service.py`: Todo business logic
- `user_service.py`: User business logic
- `auth_service.py`: Authentication logic

### Authentication (src/auth/)
- `jwt_utils.py`: JWT token creation and validation
- `security.py`: Password hashing and verification