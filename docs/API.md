# API Documentation

The backend exposes a RESTful API built with FastAPI.

## Authentication
All protected endpoints require a `Bearer` token in the `Authorization` header.
Tokens are obtained via the `/api/v1/auth/login` endpoint.

## Core Endpoints

### Auth
- `POST /api/v1/auth/login` - Authenticate user and get JWT
- `POST /api/v1/auth/register` - Register a new user
- `GET /api/v1/auth/me` - Get current authenticated user

### Resumes
- `POST /api/v1/resumes/upload` - Upload a new resume (PDF/DOCX)
- `GET /api/v1/resumes/` - List all user resumes
- `GET /api/v1/resumes/{id}` - Get details of a specific resume
- `DELETE /api/v1/resumes/{id}` - Delete a resume

### Job Matching
- `POST /api/v1/job-matching/match` - Run the deterministic job matching algorithm
- `GET /api/v1/job-matching/history` - Get match history

### AI Assistant
- `POST /api/v1/ai/chat` - Send a message to the AI career assistant
- `GET /api/v1/ai/history` - Get chat history

### Admin
- `GET /api/v1/admin/users` - List all users (Admin only)
- `GET /api/v1/admin/analytics` - System analytics (Admin only)

## Interactive Docs
When the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
