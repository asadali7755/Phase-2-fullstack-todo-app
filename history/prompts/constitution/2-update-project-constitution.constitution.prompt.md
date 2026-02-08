---
id: 2
title: Update Project Constitution
stage: constitution
date: 2026-01-28
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: user
command: "/sp.constitution\n\nProject: Todo Full-Stack Web Application (Spec-Driven, AI-Native Development)\n\nCore principles:\n- Spec-first, agentic development (spec â†’ plan â†’ tasks â†’ implementation)\n- Security by design (authentication and user isolation enforced everywhere)\n- Deterministic, reproducible builds\n- Clear separation of frontend, backend, and data layers\n- No manual coding; all output generated via Claude Code and Spec-Kit Plus\n\nKey standards:\n- All features must be derived directly from approved specifications\n- All API endpoints must be RESTful and fully documented\n- Authentication must use Better Auth with JWT-based verification\n- All backend routes must validate JWTs and enforce task ownership\n- Database access must be handled exclusively through SQLModel ORM\n- Frontend must communicate with backend only via authenticated API calls\n- Errors must be explicit, consistent, and machine-readable\n\nConstraints:\n- Frontend: Next.js 16+ using App Router\n- Backend: Python FastAPI\n- ORM: SQLModel\n- Database: Neon Serverless PostgreSQL\n- Authentication: Better Auth (frontend) + JWT verification (backend)\n- Environment-based secrets management (BETTER_AUTH_SECRET)\n- No shared session state between frontend and backend\n- Must implement all 5 Basic Level Todo features\n\nDevelopment constraints:\n- Follow Agentic Dev Stack workflow strictly\n- No handwritten code outside generated outputs\n- Each spec must be independently reviewable\n- All changes must be traceable to a spec or plan step\n\nSuccess criteria:\n- Users can sign up and sign in securely\n- JWT tokens are issued, transmitted, and verified correctly\n- All API endpoints require valid authentication\n- Users can only access and modify their own tasks\n- Tasks persist correctly in Neon PostgreSQL\n- Frontend is responsive and usable on desktop and mobile\n- End-to-end flow works: auth â†’ task CRUD â†’ persistence\n- Project passes hackathon Phase-2 review for process, prompts, and execution"
labels: ["constitution", "project-setup"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - "/mnt/e/course/hackthon2_todo-app/PHASE22/.specify/memory/constitution.md"
tests:

---

## Prompt

/sp.constitution

Project: Todo Full-Stack Web Application (Spec-Driven, AI-Native Development)

Core principles:
- Spec-first, agentic development (spec → plan → tasks → implementation)
- Security by design (authentication and user isolation enforced everywhere)
- Deterministic, reproducible builds
- Clear separation of frontend, backend, and data layers
- No manual coding; all output generated via Claude Code and Spec-Kit Plus

Key standards:
- All features must be derived directly from approved specifications
- All API endpoints must be RESTful and fully documented
- Authentication must use Better Auth with JWT-based verification
- All backend routes must validate JWTs and enforce task ownership
- Database access must be handled exclusively through SQLModel ORM
- Frontend must communicate with backend only via authenticated API calls
- Errors must be explicit, consistent, and machine-readable

Constraints:
- Frontend: Next.js 16+ using App Router
- Backend: Python FastAPI
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth (frontend) + JWT verification (backend)
- Environment-based secrets management (BETTER_AUTH_SECRET)
- No shared session state between frontend and backend
- Must implement all 5 Basic Level Todo features

Development constraints:
- Follow Agentic Dev Stack workflow strictly
- No handwritten code outside generated outputs
- Each spec must be independently reviewable
- All changes must be traceable to a spec or plan step

Success criteria:
- Users can sign up and sign in securely
- JWT tokens are issued, transmitted, and verified correctly
- All API endpoints require valid authentication
- Users can only access and modify their own tasks
- Tasks persist correctly in Neon PostgreSQL
- Frontend is responsive and usable on desktop and mobile
- End-to-end flow works: auth → task CRUD → persistence
- Project passes hackathon Phase-2 review for process, prompts, and execution

## Response snapshot

The project constitution has been updated to version 0.1.0, reflecting the initial definition of core principles, standards, constraints, and success criteria.

Files requiring manual follow-up for consistency with the new constitution include:
*   `.specify/templates/plan-template.md`
*   `.specify/templates/spec-template.md`
*   `.specify/templates/tasks-template.md`
*   `README.md`

Suggested commit message: `docs: amend constitution to v0.1.0 (initial definition)`

## Outcome

- ✅ Impact: Project constitution defined and updated.
- 🧪 Tests: N/A
- 📁 Files: Updated .specify/memory/constitution.md
- 🔁 Next prompts: User needs to update dependent templates and README.md manually or prompt for further assistance.
- 🧠 Reflection: Successfully updated the constitution based on user input and provided clear follow-up actions and commit message.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
