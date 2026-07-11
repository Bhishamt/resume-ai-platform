# Architecture

## System Overview

The AI Resume Analyzer & Job Match Platform is a modern 3-tier architecture, consisting of a React frontend, a FastAPI backend, and a PostgreSQL database. It incorporates AI parsing via Google Gemini / OpenAI and utilizes Redis for caching and background tasks.

## Frontend Architecture
- **Framework**: React 18 with Vite
- **State Management**: React Context + Hooks
- **Styling**: Tailwind CSS & Framer Motion for animations
- **Charts**: Recharts for visualizing scores and skills
- **Routing**: React Router DOM

## Backend Architecture
- **Framework**: FastAPI (Python 3.10+)
- **ORM**: SQLAlchemy with async drivers (asyncpg)
- **Authentication**: JWT based auth with RBAC (Role-Based Access Control)
- **Background Tasks**: Celery with Redis broker for resume parsing and email notifications.
- **LLM Integration**: Google Gemini via standard API client for resume parsing.

## Infrastructure
- **Database**: PostgreSQL
- **Cache**: Redis
- **Storage**: S3-compatible storage (e.g., AWS S3, Cloudflare R2) for resume PDFs.
- **Containerization**: Docker & Docker Compose for local development and deployment.

## Data Flow
1. **User Upload**: User uploads a resume (PDF) from the React app.
2. **Backend Processing**: FastAPI receives the file, uploads to S3, and schedules a Celery task.
3. **AI Parsing**: Celery worker downloads the file, calls Gemini API to extract structured JSON (skills, experience, education).
4. **Database Storage**: Structured data is saved to PostgreSQL.
5. **Dashboard**: React app fetches the structured data and displays the ATS score and insights.
