# AI Resume Analyzer & Job Match Platform

## Overview
A production-ready SaaS application designed to help job seekers optimize their resumes, improve ATS compatibility, receive AI-powered feedback, and evaluate resume compatibility against job descriptions.

## Folder Structure
```
resume-ai-platform/
├── backend/          # FastAPI backend application
├── frontend/         # React + Vite frontend application
├── docker/           # Dockerfiles and configuration
├── docs/             # Project documentation and guidelines
├── scripts/          # Utility scripts
├── uploads/          # Temporary file storage
├── screenshots/      # UI screenshots for README
├── .github/          # GitHub Actions workflows
├── docker-compose.yml
├── .env.example
└── README.md
```

## Tech Stack
- **Frontend**: React, Vite, Tailwind CSS, React Router, React Hook Form
- **Backend**: FastAPI, SQLAlchemy, Alembic, Pydantic, JWT, bcrypt
- **Database**: PostgreSQL
- **AI Integration**: Groq API
- **Deployment**: Docker, Docker Compose, Nginx

## Installation

### Using Docker (Recommended)
1. Copy `.env.example` to `.env` and fill in the values.
2. Run `docker-compose up --build`

### Local Development

#### Backend
1. `cd backend`
2. `python -m venv venv`
3. `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
4. `pip install -r requirements.txt`
5. `uvicorn app.main:app --reload`

#### Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev`
