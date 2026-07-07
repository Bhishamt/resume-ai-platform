# 20 - AI Coding Agent Rules

## Objective

Build a production-ready SaaS application that follows enterprise software engineering standards.

---

## General Rules

- Never generate placeholder code.
- Never skip error handling.
- Never leave TODO comments.
- Never hardcode secrets.
- Never duplicate business logic.
- Always write modular code.
- Always prefer reusable components.
- Always follow the project architecture.

---

## Development Workflow

For every feature:

1. Understand requirements.
2. Design architecture.
3. Implement backend.
4. Implement frontend.
5. Connect API.
6. Write tests.
7. Run lint.
8. Verify responsiveness.
9. Update documentation.
10. Continue only if all checks pass.

---

## UI Rules

- Follow the UI Design System.
- Use Tailwind CSS only.
- Build responsive layouts.
- Support dark mode.
- Use loading, error, and empty states.
- Use subtle animations.
- Keep spacing consistent.

---

## Backend Rules

- Use FastAPI best practices.
- Validate all requests with Pydantic.
- Keep routes thin.
- Place business logic in services.
- Use repositories for database access.
- Generate Alembic migrations.

---

## Database Rules

- Use PostgreSQL.
- Enforce foreign keys.
- Add indexes where appropriate.
- Never use raw SQL unless necessary.

---

## AI Rules

- Use an AI service layer.
- Never call Groq directly from routes.
- Validate AI responses.
- Log AI usage.
- Design for multiple AI providers.

---

## Security Rules

- Use JWT authentication.
- Hash passwords with bcrypt.
- Validate all input.
- Protect private routes.
- Secure file uploads.
- Store secrets in environment variables.

---

## Testing Rules

Every feature must include:

- Unit tests
- Integration tests
- API tests

Never continue with failing tests.

---

## Code Quality

Follow:

- Clean Architecture
- SOLID
- DRY
- KISS

Keep code readable, maintainable, and scalable.

---

## Git Rules

Use meaningful commits:

feat:
fix:
docs:
refactor:
test:
style:

---

## Final Requirement

Do not consider any feature complete until:

- Code is production-ready.
- Tests pass.
- Documentation is updated.
- No critical issues remain.
