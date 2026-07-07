# 02 - System Architecture

> **Project:** AI Resume Analyzer & Job Match Platform
> **Version:** 1.0

---

# Purpose

This document defines the overall system architecture, project structure, data flow, and development principles. Every implementation must follow this architecture.

---

# Architecture Overview

The application follows a modern 3-tier architecture with clear separation of concerns.

```
Frontend (React + Vite)
        │
        ▼
 REST API (FastAPI)
        │
        ▼
Business Services
        │
        ▼
Database Layer (SQLAlchemy)
        │
        ▼
PostgreSQL
```

External Services:

- Groq API (AI)
- Local File Storage (Uploads)

---

# Technology Stack

## Frontend

- React
- Vite
- Tailwind CSS
- React Router
- Axios
- React Hook Form
- Recharts

## Backend

- Python 3.12+
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- JWT
- bcrypt

## Database

- PostgreSQL

## AI

- Groq API
- Future-ready for OpenAI

---

# Project Structure

```
resume-ai-platform/

backend/
    app/
        api/
        auth/
        core/
        database/
        models/
        schemas/
        services/
        repositories/
        utils/
        middleware/
        main.py

frontend/
    src/
        components/
        pages/
        layouts/
        hooks/
        services/
        context/
        routes/
        assets/
        styles/

docs/
docker/
scripts/
uploads/
```

---

# Request Flow

```
User

↓

React UI

↓

Axios API Request

↓

FastAPI Router

↓

Service Layer

↓

Repository Layer

↓

PostgreSQL

↓

JSON Response

↓

React UI Update
```

---

# AI Flow

```
Resume Upload

↓

Resume Parser

↓

Extract Information

↓

Groq AI

↓

Generate Analysis

↓

Store Report

↓

Display Dashboard
```

---

# Design Principles

- Clean Architecture
- SOLID Principles
- Modular Components
- Reusable Code
- Separation of Concerns
- Single Responsibility
- Dependency Injection

---

# Backend Rules

- Business logic belongs only in Services.
- Routes must remain lightweight.
- Database queries belong in Repositories.
- Models define database tables.
- Schemas validate API requests and responses.

---

# Frontend Rules

- Pages contain layout only.
- Components are reusable.
- API calls are isolated in Services.
- Forms use React Hook Form.
- State is managed through Context or custom hooks.
- No inline styles.

---

# Security Layers

- JWT Authentication
- Password Hashing
- Input Validation
- Role-Based Access Control
- Secure File Upload
- Environment Variables

---

# Scalability

The architecture should support:

- Multiple AI providers
- Cloud deployment
- Redis caching
- Background jobs
- Microservice migration
- Horizontal scaling

---

# Development Rules

- Keep modules independent.
- Avoid duplicated code.
- Use meaningful file names.
- Maintain consistent folder structure.
- Write reusable functions.
- Follow REST standards.

---

# Acceptance Criteria

- Architecture is modular.
- No circular dependencies.
- Components are reusable.
- API follows REST principles.
- Business logic is separated.
- Easy to scale and maintain.

---

# Agent Instructions

The AI coding agent must:

- Follow this architecture strictly.
- Never place business logic inside UI components.
- Never access the database directly from API routes.
- Never duplicate services.
- Build scalable and maintainable modules.
- Follow the folder structure exactly.
- Keep frontend and backend loosely coupled.