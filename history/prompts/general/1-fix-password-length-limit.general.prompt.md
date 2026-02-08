---
id: 1
title: Fix Password Length Limit Issue
stage: refactor
date_iso: 2026-02-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 003-frontend-app
user: user
command: "password cannot be longer than 72 bytes, truncate manually if necessary (e.g. my_password[:72]) singup main ye error arha he isko 8 charagers pe kro sirf 8 caraters ya os se oper ka ho to bs submit ho jana chaiya ye cheez hata do"
labels: ["backend", "security", "password", "validation"]
spec: null
ticket: null
pr: null
adr: null
---

## User Prompt
```
password cannot be longer than 72 bytes, truncate manually if necessary (e.g. my_password[:72]) singup main ye error arha he isko 8 charagers pe kro sirf 8 caraters ya os se oper ka ho to bs submit ho jana chaiya ye cheez hata do
```

## Response Text
Fixed the password length limit issue by modifying both the auth service and user model:

1. Updated `hash_password` function in `backend/src/services/auth_service.py` to automatically truncate passwords to 72 bytes maximum instead of raising an error
2. Modified the password validator in `backend/src/models/user.py` to remove the 70-character limit, keeping only the minimum 8-character requirement

These changes allow users to submit passwords of any length, but they will be automatically truncated to 72 bytes to comply with bcrypt's limitations, eliminating the error while maintaining security.

## Files Modified
- backend/src/services/auth_service.py
- backend/src/models/user.py
- backend/src/auth/jwt_utils.py
- backend/src/auth/security.py

## Tests Performed
- Verified that the password hashing still works correctly
- Confirmed that passwords longer than 72 bytes will be automatically truncated
- Ensured that the minimum 8-character validation remains in place