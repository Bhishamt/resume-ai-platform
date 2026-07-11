# Developer Guide

## Setup Development Environment

1. **Clone the repo**
   ```bash
   git clone https://github.com/Bhishamt/resume-ai-platform.git
   ```

2. **Start Infrastructure (DB & Redis)**
   ```bash
   docker-compose up -d db redis
   ```

3. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Run migrations
   alembic upgrade head
   
   # Start server
   uvicorn app.main:app --reload
   
   # In a separate terminal, start Celery worker
   celery -A app.core.celery_app worker --loglevel=info
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Code Style & Linting
- **Python**: We use `ruff` for linting, `black` for formatting, and `isort` for import sorting. Run `python -m black .` and `python -m ruff check .` before committing.
- **JavaScript**: We use `eslint` and `prettier`. Run `npm run lint`.

## Testing
- Backend tests are written with `pytest`. Run `pytest` in the `backend` directory.
- Frontend tests (if added) run via `npm test`.

## Branching Strategy
- `main`: Production-ready code.
- `develop`: Main development branch.
- Feature branches: `feat/feature-name`
- Bugfix branches: `fix/bug-name`
