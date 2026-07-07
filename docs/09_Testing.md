# 09 - Testing

## Purpose

Ensure the application is stable, secure, and production-ready before deployment.

---

## Testing Levels

- Unit Tests
- Integration Tests
- API Tests
- UI Tests
- End-to-End Tests

---

## Backend

Framework: Pytest

Test:

- Authentication
- APIs
- Services
- Database
- AI Service

---

## Frontend

Framework:

- Vitest
- React Testing Library

Test:

- Components
- Forms
- Routing
- Dashboard
- Upload Flow

---

## E2E

Framework:

- Playwright

Test complete user journeys.

---

## Coverage Goal

Minimum Coverage:

- Backend: 90%
- Frontend: 85%

---

## CI Pipeline

Every push must run:

- Lint
- Unit Tests
- Integration Tests
- Build

---

## Acceptance Criteria

- All tests pass
- No critical bugs
- Production build succeeds

---

## Agent Instructions

Never continue development if tests fail.