---
name: auth-skill
description: Build secure authentication systems including signup, signin, password hashing, JWT tokens, and Better Auth integration.
---

# Authentication Skill

## Instructions

1. **User Registration (Signup)**
   - Validate user input (email, password)
   - Prevent duplicate users
   - Hash password before storing
   - Save user securely in database

2. **User Login (Signin)**
   - Verify user credentials
   - Compare hashed passwords
   - Handle invalid login attempts
   - Generate JWT token on success

3. **Password Hashing**
   - Use bcrypt or argon2
   - Apply salting automatically
   - Never store plain-text passwords

4. **JWT Token Handling**
   - Create access tokens on login
   - Set token expiration
   - Verify tokens for protected routes
   - Support refresh tokens if required

5. **Better Auth Integration**
   - Centralized authentication configuration
   - Secure session & token management
   - Middleware-based route protection
   - Easy integration with backend frameworks

---

## Best Practices
- Always hash passwords before saving
- Store secrets in environment variables
- Keep JWT expiration short
- Use HTTPS for all auth routes
- Protect sensitive routes with middleware
- Log errors without exposing credentials

---

## Example Structure

```js
// Signup
POST /signup
- Validate input
- Hash password
- Save user
