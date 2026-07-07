# 19 - Environment

## Required Variables

DATABASE_URL

SECRET_KEY

JWT_SECRET

GROQ_API_KEY

UPLOAD_DIR

MAX_UPLOAD_SIZE

APP_ENV

CORS_ORIGINS

---

## Rules

- Never commit .env
- Provide .env.example
- Validate environment variables on startup

---

## Agent Instructions

Application must fail fast if required environment variables are missing.