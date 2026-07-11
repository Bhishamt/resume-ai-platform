# =============================================================================
# AI Resume Analyzer & Job Match Platform — Developer Makefile
# =============================================================================

.PHONY: help dev-backend dev-frontend dev install-backend install-frontend \
        test lint format migrate migrate-new docker-dev docker-prod \
        celery-worker celery-beat flower redis-start clean

help:
	@echo "Available commands:"
	@echo "  make dev              - Start backend + frontend (requires tmux)"
	@echo "  make dev-backend      - Start FastAPI dev server"
	@echo "  make dev-frontend     - Start Vite dev server"
	@echo "  make install-backend  - Install backend dependencies"
	@echo "  make install-frontend - Install frontend dependencies"
	@echo "  make test             - Run backend tests"
	@echo "  make lint             - Run linters"
	@echo "  make migrate          - Run Alembic migrations"
	@echo "  make migrate-new      - Create a new migration"
	@echo "  make celery-worker    - Start Celery worker (all queues)"
	@echo "  make celery-beat      - Start Celery beat scheduler"
	@echo "  make flower           - Start Flower monitoring UI"
	@echo "  make docker-dev       - Start dev Docker stack"
	@echo "  make docker-prod      - Start production Docker stack"
	@echo "  make clean            - Remove build artifacts"

# ─── Development ──────────────────────────────────────────────────────────────

dev-backend:
	cd backend && venv/Scripts/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

# ─── Testing ──────────────────────────────────────────────────────────────────

test:
	cd backend && venv/Scripts/pytest tests/ -v --tb=short

test-coverage:
	cd backend && venv/Scripts/pytest tests/ --cov=app --cov-report=html --cov-report=term

# ─── Linting ──────────────────────────────────────────────────────────────────

lint:
	cd backend && venv/Scripts/ruff check app/ --fix
	cd frontend && npm run lint

format:
	cd backend && venv/Scripts/ruff format app/

# ─── Database Migrations ──────────────────────────────────────────────────────

migrate:
	cd backend && venv/Scripts/alembic upgrade head

migrate-new:
	@read -p "Migration name: " name; \
	cd backend && venv/Scripts/alembic revision --autogenerate -m "$$name"

migrate-rollback:
	cd backend && venv/Scripts/alembic downgrade -1

# ─── Background Jobs ──────────────────────────────────────────────────────────

celery-worker:
	cd backend && venv/Scripts/celery -A app.core.celery_app worker --loglevel=info \
		--queues=default,ai,email,cleanup --concurrency=2

celery-beat:
	cd backend && venv/Scripts/celery -A app.core.celery_app beat --loglevel=info

flower:
	cd backend && venv/Scripts/celery -A app.core.celery_app flower --port=5555

# ─── Docker ───────────────────────────────────────────────────────────────────

docker-dev:
	docker compose up -d

docker-prod:
	docker compose -f docker-compose.prod.yml up -d --build

docker-logs:
	docker compose -f docker-compose.prod.yml logs -f

docker-down:
	docker compose -f docker-compose.prod.yml down

docker-build:
	docker compose -f docker-compose.prod.yml build

# ─── Utilities ────────────────────────────────────────────────────────────────

clean:
	find backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find backend -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find backend -name "*.pyc" -delete 2>/dev/null || true
	cd frontend && rm -rf dist/ 2>/dev/null || true
