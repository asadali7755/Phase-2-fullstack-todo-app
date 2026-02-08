---
name: database-schema-design
description: Design efficient database schemas, create tables, and manage migrations for scalable applications.
---

# Database Schema Design

## Instructions

### 1. Schema Planning
- Identify entities and relationships
- Define primary and foreign keys
- Normalize data to reduce redundancy

### 2. Table Creation
- Choose correct data types
- Apply constraints (NOT NULL, UNIQUE)
- Add indexes for performance

### 3. Migrations
- Track schema changes with version control
- Write reversible migrations (up & down)
- Avoid breaking existing data

### 4. Relationships
- One-to-one
- One-to-many
- Many-to-many using junction tables

## Best Practices
- Follow consistent naming conventions
- Use integer or UUID primary keys
- Index frequently queried columns
- Keep schema simple and readable
- Document schema decisions

## Example Structure
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(150) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE posts (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL,
  title VARCHAR(200) NOT NULL,
  body TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
