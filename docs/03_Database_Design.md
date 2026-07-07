# 03 - Database Design

> **Project:** AI Resume Analyzer & Job Match Platform
> **Version:** 1.0

---

# Purpose

This document defines the database schema, relationships, constraints, and best practices for the platform. The database must be normalized, scalable, and optimized for production.

---

# Database

**Engine:** PostgreSQL

**ORM:** SQLAlchemy

**Migration Tool:** Alembic

---

# Core Tables

## users

Stores user accounts.

Fields:

- id (UUID)
- full_name
- email (Unique)
- password_hash
- avatar_url
- role (user/admin)
- is_active
- created_at
- updated_at

---

## resumes

Stores uploaded resumes.

Fields:

- id
- user_id (FK)
- file_name
- file_path
- file_type
- file_size
- upload_date

Relationship:

User → Many Resumes

---

## analysis_reports

Stores resume analysis results.

Fields:

- id
- resume_id (FK)
- ats_score
- resume_score
- strengths
- weaknesses
- grammar_feedback
- formatting_feedback
- created_at

Relationship:

Resume → Many Reports

---

## job_descriptions

Stores job descriptions.

Fields:

- id
- user_id
- title
- company
- description
- created_at

---

## job_matches

Stores job matching results.

Fields:

- id
- resume_id
- job_description_id
- match_percentage
- matching_skills
- missing_skills
- suggested_keywords
- created_at

---

## ai_feedback

Stores AI-generated content.

Fields:

- id
- user_id
- resume_id
- prompt_type
- response
- provider
- tokens_used
- created_at

---

## upload_history

Stores upload logs.

Fields:

- id
- user_id
- resume_id
- action
- uploaded_at

---

# Relationships

```
User
 ├── Resumes
 │      ├── Analysis Reports
 │      ├── AI Feedback
 │      └── Job Matches
 │
 └── Job Descriptions
```

---

# Indexes

Create indexes for:

- email
- user_id
- resume_id
- created_at
- job_description_id

---

# Constraints

- Email must be unique.
- Foreign keys required.
- Cascade delete for child records.
- No nullable primary fields.
- Validate file size before storage.

---

# Naming Convention

Tables:

snake_case

Columns:

snake_case

Primary Key:

id

Foreign Key:

<entity>_id

---

# Data Types

- UUID for primary keys
- TEXT for AI responses
- VARCHAR for names
- BOOLEAN for flags
- TIMESTAMP WITH TIME ZONE for dates
- JSONB for structured AI data (if needed)

---

# Performance

- Normalize data (3NF)
- Avoid duplicate records
- Use indexes on frequently queried fields
- Paginate large datasets
- Optimize JOIN queries

---

# Future Tables

Potential additions:

- interview_sessions
- resume_versions
- notifications
- activity_logs
- user_settings
- ai_usage
- api_keys

---

# Acceptance Criteria

- Fully normalized schema
- Proper foreign keys
- Indexed queries
- Migration-ready
- Scalable design
- Production-ready

---

# Agent Instructions

The AI coding agent must:

- Use SQLAlchemy models.
- Generate Alembic migrations.
- Never hardcode SQL queries unless necessary.
- Enforce relationships using foreign keys.
- Apply indexes where appropriate.
- Keep schema extensible for future features.
- Validate database constraints before deployment.