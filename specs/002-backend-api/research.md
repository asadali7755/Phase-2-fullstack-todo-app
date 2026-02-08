# Research Findings: Backend API & Database Layer for Todo Full-Stack Web Application

## Key Decisions & Rationale

### 1. SQLModel vs Raw SQL

**Decision**: Use SQLModel ORM for database interactions

**Rationale**:
- SQLModel combines SQLAlchemy and Pydantic, providing both database modeling and API serialization benefits
- Matches the constraint specified in the feature requirements
- Provides type safety through Pydantic integration
- Simplifies development by reducing boilerplate code
- Well-suited for FastAPI ecosystem

**Alternatives considered**:
- Pure SQLAlchemy: Would require separate serialization layer
- Raw SQL: Would lose type safety and ORM benefits
- Tortoise ORM: Less mature and not as well integrated with FastAPI

### 2. Task Ownership Enforcement: Query vs Route Level

**Decision**: Implement ownership enforcement at both query and route levels

**Rationale**:
- Route-level enforcement provides immediate access control
- Query-level enforcement provides additional security layer (defense in depth)
- Both approaches complement each other for robust security
- Query-level filtering ensures data isolation even if route-level checks are bypassed

**Implementation approach**:
- Extract user ID from JWT token in route handlers
- Filter all queries by user ID
- Use dependency injection to ensure user context is available

### 3. Soft Delete vs Hard Delete for Tasks

**Decision**: Use hard delete for tasks

**Rationale**:
- Todo application doesn't typically require soft delete functionality
- Hard delete is simpler to implement and maintain
- Reduces database storage requirements
-符合 user expectations for todo deletion
- No regulatory requirements for data retention mentioned

**Alternative considered**:
- Soft delete: Would add complexity with deleted_at timestamps and query filters

### 4. UUID vs Integer IDs for Tasks

**Decision**: Use UUID for task IDs

**Rationale**:
- Better security - prevents enumeration attacks
-符合 existing codebase patterns (user IDs are UUIDs)
- Distributed system friendly
-符合 best practices for web APIs

**Alternative considered**:
- Integer IDs: Simpler but less secure and not suitable for distributed systems

### 5. Pagination Strategy for Task Listing

**Decision**: Implement pagination with default limits and configurable page sizes

**Rationale**:
- Prevents performance issues with large datasets
-符合 REST API best practices
- Allows clients to control data retrieval
- Enables better performance for users with many tasks

**Implementation approach**:
- Default page size of 20-50 items
- Configurable page size with maximum limits
- Offset-based pagination with limit/offset parameters