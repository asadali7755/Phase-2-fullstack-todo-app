---
name: backend-skill
description: Generate backend routes, handle requests and responses, and connect to databases.
---

# Backend Skill – API & Database Handling

Build backend APIs by generating routes, handling requests and responses, and connecting to databases.

---

## Instructions

### 1. Project Setup
- Initialize backend framework (Express / FastAPI / Django)
- Configure environment variables
- Create folder structure:
  - routes
  - controllers
  - models
  - services
  - database

### 2. Routing
- Create RESTful routes:
  - GET
  - POST
  - PUT
  - DELETE
- Group routes logically
- Use middleware for authentication and validation

### 3. Request & Response Handling
- Read request body, params, and query
- Validate incoming data
- Return structured JSON responses
- Handle errors using proper HTTP status codes

### 4. Database Connection
- Connect to database (MongoDB / PostgreSQL / MySQL)
- Define schemas or models
- Perform CRUD operations
- Handle async queries safely

---

## Best Practices
- Follow REST API standards
- Keep controllers thin and reusable
- Use async/await with try–catch
- Never expose sensitive data
- Use environment variables for secrets

---

## Example Structure (Node.js + Express)

### Route File
```js
// routes/user.routes.js
import express from "express";
import { createUser, getUsers } from "../controllers/user.controller.js";

const router = express.Router();

router.post("/users", createUser);
router.get("/users", getUsers);

export default router;
