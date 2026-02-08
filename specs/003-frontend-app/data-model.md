# Data Model: Frontend Application for Todo Full-Stack Web Application

## Frontend-Specific Data Structures

### User Session State
**Description**: Represents the authenticated user's session state managed by Better Auth

**Fields**:
- `user`: Object containing user information (id, email, etc.)
- `token`: JWT token for API authentication
- `expiresAt`: Expiration timestamp for the session
- `isLoading`: Boolean indicating if session is being loaded
- `isAuthenticated`: Boolean indicating current authentication status

**State Transitions**:
- `uninitialized` → `loading` → `authenticated` | `unauthenticated`
- `authenticated` → `expired` → `unauthenticated`

### Todo Item State (Frontend)
**Description**: Frontend representation of a todo item with additional UI state

**Fields**:
- `id`: String/UUID - Unique identifier for the todo
- `title`: String - Task title (1-255 characters)
- `description`: String (Optional) - Task description (≤1000 characters)
- `completed`: Boolean - Completion status
- `createdAt`: Date - Creation timestamp
- `updatedAt`: Date - Last update timestamp
- `isEditing`: Boolean - UI state for inline editing
- `isLoading`: Boolean - UI state for pending operations

**State Transitions**:
- `loading` → `idle` → `editing` | `saving` | `deleting`
- `saving` → `idle` | `error`
- `deleting` → `idle` | `error`

### API Response State
**Description**: Wrapper for API responses to handle loading and error states

**Fields**:
- `data`: Actual data payload (optional)
- `isLoading`: Boolean - indicates ongoing request
- `isError`: Boolean - indicates request failure
- `error`: Error object/message (optional)
- `isSuccess`: Boolean - indicates successful request

## Frontend Component Data Flow

### Authentication Flow
1. User initiates sign-in/sign-up
2. Better Auth handles credentials
3. Session object created with JWT token
4. Token automatically attached to API requests
5. Protected routes become accessible

### Todo Management Flow
1. Fetch todos from API with JWT authentication
2. Store in component state
3. User modifies todo (create/update/delete)
4. Send request to API with JWT authentication
5. Update local state optimistically
6. Handle response/error and adjust state accordingly

## API Client Configuration

### Request Headers
- `Authorization`: `Bearer ${jwtToken}` for authenticated requests
- `Content-Type`: `application/json` for JSON payloads

### Error Handling
- Network errors: Show user-friendly message
- 401 Unauthorized: Redirect to sign-in
- 403 Forbidden: Show access denied message
- 422 Validation errors: Show field-specific errors
- 5xx Server errors: Show generic error message

## UI State Management

### Global States
- Authentication state (managed by Better Auth)
- Current user information
- Application-wide loading states
- Error notification queue

### Component-Specific States
- Form input values and validation
- Modal/dialog visibility
- Loading states for specific operations
- Temporary UI states (hover, focus, etc.)

## Data Validation Rules

### Client-Side Validation
- Title: Required, 1-255 characters
- Description: Optional, ≤1000 characters
- Email format validation for authentication
- Password strength requirements

### Server-Side Validation
- All client-side validations repeated on server
- User ownership verification for todo operations
- JWT token validity and expiration checks