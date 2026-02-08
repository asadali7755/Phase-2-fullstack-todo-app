# Data Model: Backend API & Database Layer for Todo Full-Stack Web Application

## Entity Definitions

### Todo Entity
**Description**: Represents a user's task with attributes for title, description, completion status, and timestamps.

**Fields**:
- `id`: UUID (Primary Key) - Unique identifier for the task
- `title`: String (Required) - Task title (max length: 255 characters)
- `description`: String (Optional) - Task description (max length: 1000 characters)
- `completed`: Boolean (Default: False) - Completion status
- `user_id`: UUID (Foreign Key) - Reference to the owning user
- `created_at`: DateTime (Auto-generated) - Creation timestamp
- `updated_at`: DateTime (Auto-generated) - Last update timestamp

**Relationships**:
- Belongs to one User (Many-to-One)
- User can have many Todos (One-to-Many)

**Validation Rules**:
- Title must not be empty
- Title length must be between 1-255 characters
- Description length must be ≤ 1000 characters if provided

### User Entity
**Description**: Represents an authenticated user with associated tasks.

**Fields**:
- `id`: UUID (Primary Key) - Unique identifier for the user
- `email`: String (Unique, Required) - User's email address
- `hashed_password`: String (Required) - BCrypt hashed password
- `created_at`: DateTime (Auto-generated) - Account creation timestamp
- `updated_at`: DateTime (Auto-generated) - Last update timestamp
- `is_active`: Boolean (Default: True) - Account status

**Relationships**:
- Has many Todos (One-to-Many)
- Todos belong to this User (Many-to-One)

## Database Schema Design

### Indexes
- Index on `user_id` in todos table for efficient user-based queries
- Index on `completed` field for filtering completed tasks
- Unique index on `email` in users table

### Constraints
- Foreign key constraint on `user_id` in todos table
- NOT NULL constraints on required fields
- Check constraint to ensure title length requirements

## State Transitions

### Todo States
- **Active**: `completed = False` (default state)
- **Completed**: `completed = True` (after user marks as complete)

### Operations
- **Create**: New todo in Active state
- **Update**: Can transition between Active and Completed states
- **Delete**: Remove todo from database (hard delete)

## API Data Transfer Objects (DTOs)

### TodoCreate
- `title`: String (Required)
- `description`: String (Optional)

### TodoUpdate
- `title`: String (Optional) - If provided, update title
- `description`: String (Optional) - If provided, update description
- `completed`: Boolean (Optional) - If provided, update completion status

### TodoResponse
- `id`: UUID
- `title`: String
- `description`: String (Optional)
- `completed`: Boolean
- `user_id`: UUID
- `created_at`: DateTime
- `updated_at`: DateTime

## Security Considerations

### Data Access Control
- All queries must be filtered by authenticated user's ID
- Cross-user access prevention through query-level filtering
- JWT token validation required for all endpoints

### Data Validation
- Input sanitization for all user-provided content
- Length and format validation for all fields
- SQL injection prevention through ORM usage