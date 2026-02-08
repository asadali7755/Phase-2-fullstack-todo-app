# Data Model: Authentication & User Isolation for Todo Full-Stack Web Application

## Key Entities

### User
Represents a registered user of the application.

**Fields**:
- id (UUID/String): Unique identifier for the user
- email (String): User's email address (unique, required)
- hashed_password (String): Securely hashed password (required)
- created_at (DateTime): Timestamp when the user account was created
- updated_at (DateTime): Timestamp when the user account was last updated
- is_active (Boolean): Flag indicating if the user account is active

**Relationships**:
- One-to-Many: A user can have multiple Todo items

**Validation Rules**:
- Email must be a valid email format
- Email must be unique across all users
- Email and password are required for registration
- Password must be securely hashed before storage

**State Transitions**:
- Pending Registration → Active (after successful verification)
- Active → Inactive (upon account deactivation)

### JWT (JSON Web Token)
A compact, URL-safe means of representing claims to be transferred between two parties.

**Fields**:
- sub (Subject): User ID
- email (String): User's email address
- exp (Expiration): Unix timestamp for token expiration
- iat (Issued At): Unix timestamp for token issuance
- jti (JWT ID): Unique identifier for the token (optional, for blacklisting)

**Validation Rules**:
- Token must be properly signed with the shared secret
- Token must not be expired at the time of validation
- Token signature must match the stored secret
- Optional: Token ID must not be in the blacklist (if using blacklisting)

**State Transitions**:
- Active → Expired (after expiration time)
- Active → Invalidated (if added to blacklist during logout)

### Todo
Represents a task item owned by a specific user.

**Fields**:
- id (UUID/String): Unique identifier for the todo
- title (String): Title or description of the task (required)
- description (String): Detailed description of the task (optional)
- completed (Boolean): Flag indicating if the task is completed
- user_id (UUID/String): Foreign key linking to the owning user
- created_at (DateTime): Timestamp when the todo was created
- updated_at (DateTime): Timestamp when the todo was last updated

**Relationships**:
- Many-to-One: Multiple todos belong to one user

**Validation Rules**:
- Title is required for creating a new todo
- User ID must correspond to an existing, active user
- Only the owner can modify or delete the todo
- User ID must be validated against the authenticated user's identity

**State Transitions**:
- Created → Active (default state)
- Active → Completed (when marked as done)
- Completed → Active (when unmarked)

## Data Access Patterns

### User-Specific Queries
- Retrieve all todos for a specific user (filtered by user_id)
- Count todos for a specific user
- Filter todos by completion status for a specific user

### Authentication-Related Queries
- Find user by email for login verification
- Update user's last login timestamp
- Verify user's active status

### User Isolation Enforcement
- All queries accessing user data must include user_id filter
- Cross-user data access must be explicitly prevented in queries
- Authorization checks must occur before data retrieval/modification