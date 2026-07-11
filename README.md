<div align="center">
  <img src="https://via.placeholder.com/1200x300?text=AI+Resume+Analyzer+%26+Job+Match+Platform" alt="Hero Banner" />

  <h1>AI Resume Analyzer & Job Match Platform</h1>

  <p>
    An enterprise-grade platform for AI-powered resume parsing, deterministic job matching, and actionable career insights.
  </p>

  <p>
    <a href="https://github.com/Bhishamt/resume-ai-platform/actions"><img src="https://img.shields.io/github/actions/workflow/status/Bhishamt/resume-ai-platform/ci.yml" alt="Build Status"></a>
    <a href="https://github.com/Bhishamt/resume-ai-platform/releases"><img src="https://img.shields.io/github/v/release/Bhishamt/resume-ai-platform" alt="Release"></a>
    <a href="https://github.com/Bhishamt/resume-ai-platform/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Bhishamt/resume-ai-platform" alt="License"></a>
  </p>
</div>

---

## 🚀 Live Demo

**[Coming Soon - Vercel / Railway]**

---

## 📸 Screenshots

| Dashboard | ATS Analysis | Job Matching |
|:---:|:---:|:---:|
| <img src="https://via.placeholder.com/400x250?text=Dashboard+Screenshot" alt="Dashboard"> | <img src="https://via.placeholder.com/400x250?text=ATS+Screenshot" alt="ATS Analysis"> | <img src="https://via.placeholder.com/400x250?text=Job+Matching" alt="Job Matching"> |

---

## ✨ Features

- **AI Resume Parsing**: Extract structured data from PDFs, DOCX, and TXT using Gemini/OpenAI.
- **Deterministic Job Matching**: Rule-based algorithm comparing resume skills and experience against job descriptions.
- **ATS Score Simulator**: Analyze formatting, keywords, and readability to predict ATS success.
- **AI Career Assistant**: Chatbot offering tailored advice and mock interview questions based on your profile.
- **Admin Dashboard**: Comprehensive analytics, user management, and system monitoring.
- **Enterprise Security**: JWT auth, RBAC, encrypted data at rest, rate limiting, and CORS configuration.

---

## 🏗️ Architecture

```mermaid
graph TD
    Client[React Frontend] -->|REST/WebSockets| Gateway[FastAPI Backend]
    Gateway --> Auth[Authentication & RBAC]
    Gateway --> Resume[Resume Parser Service]
    Gateway --> Match[Job Match Engine]
    Gateway --> AI[AI Assistant Service]
    
    Resume --> DB[(PostgreSQL)]
    Match --> DB
    AI --> DB
    
    Resume --> Storage[S3 Object Storage]
    Resume --> LLM[Gemini API]
    AI --> LLM
    
    Gateway --> Cache[(Redis Cache)]
    Gateway --> Celery[Background Workers]
```

## 🛠️ Tech Stack

- **Frontend**: React 18, Vite, Tailwind CSS, Framer Motion, Recharts, Lucide Icons
- **Backend**: FastAPI, Python 3.10+, SQLAlchemy, Pydantic, Celery
- **Database**: PostgreSQL
- **Caching & Broker**: Redis
- **AI/LLM**: Google Gemini / OpenAI
- **Deployment**: Docker, Vercel, Railway/Render

---

## 📁 Folder Structure

```
resume-ai-platform/
├── backend/                  # FastAPI Application
│   ├── app/                  # Application code
│   │   ├── api/              # API Endpoints
│   │   ├── core/             # Config, Security
│   │   ├── models/           # SQLAlchemy Models
│   │   ├── schemas/          # Pydantic Schemas
│   │   └── services/         # Business Logic
│   ├── tests/                # Pytest Test Suite
│   └── requirements.txt      # Python Dependencies
├── frontend/                 # React Application
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Page layouts
│   │   ├── hooks/            # Custom React Hooks
│   │   ├── services/         # API Service Clients
│   │   └── lib/              # Utils and Helpers
│   └── package.json          # Node Dependencies
├── docs/                     # Documentation
├── docker-compose.yml        # Local Development Stack
└── README.md
```

---

## ⚙️ Installation & Docker Setup

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.10+

### Quick Start (Docker)

1. Clone the repository:
   ```bash
   git clone https://github.com/Bhishamt/resume-ai-platform.git
   cd resume-ai-platform
   ```
2. Copy the `.env.example` to `.env` and fill in your keys:
   ```bash
   cp .env.example .env
   ```
3. Run with Docker Compose:
   ```bash
   docker-compose up -d
   ```
4. Access the application:
   - Frontend: `http://localhost:5173`
   - Backend API Docs: `http://localhost:8000/docs`

---

## 🔐 Environment Variables

Key environment variables needed in `.env`:

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/resume_db

# Security
SECRET_KEY=your_super_secret_jwt_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis & Celery
REDIS_URL=redis://localhost:6379/0

# AI Provider (Google Gemini)
GEMINI_API_KEY=your_gemini_api_key

# Storage (S3 / R2)
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_BUCKET_NAME=resume-bucket
```

---

## 📚 API Documentation

Once the backend is running, you can view the auto-generated interactive API documentation at:
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`

A Postman collection is available in `docs/postman_collection.json`.

---

## 🚢 Deployment Guide

See `docs/Deployment.md` for full instructions on deploying to production via Vercel (Frontend) and Render/Railway (Backend).

---

## 🗺️ Roadmap

- [x] Core Resume Parsing
- [x] Rule-Based Job Matching
- [x] Admin Dashboard
- [x] UI/UX Polish
- [ ] OAuth2 Social Login (Google/GitHub)
- [ ] Automated Email Reports
- [ ] Mobile Application (React Native)

---

## 🤝 Contributing

Contributions are welcome! Please read `CONTRIBUTING.md` for details on our code of conduct, and the process for submitting pull requests.

---

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.

---

## 🙏 Acknowledgements

- Google Gemini Team for LLM capabilities
- FastAPI framework
- React & Vite communities
- Framer Motion for animations
