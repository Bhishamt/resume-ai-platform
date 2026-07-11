# Deployment Guide

This guide covers deploying the AI Resume Analyzer to production.

## 1. Database & Cache (Render / Railway)
- Provision a **PostgreSQL** database.
- Provision a **Redis** instance.
- Note the connection URLs (`DATABASE_URL`, `REDIS_URL`).

## 2. Storage (AWS S3 / Cloudflare R2)
- Create a bucket for storing resumes.
- Generate Access Key and Secret Key.

## 3. Backend Deployment (Render / Railway)
1. Connect your GitHub repository to Render/Railway.
2. Select the `backend` folder as the root.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Set Environment Variables:
   - `DATABASE_URL`
   - `REDIS_URL`
   - `SECRET_KEY`
   - `GEMINI_API_KEY`
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_BUCKET_NAME`

## 4. Celery Worker (Render / Railway)
1. Create a Background Worker service.
2. Root directory: `backend`
3. Start Command: `celery -A app.core.celery_app worker --loglevel=info`
4. Use the exact same Environment Variables as the backend.

## 5. Frontend Deployment (Vercel / Netlify)
1. Connect repository to Vercel.
2. Set Root Directory to `frontend`.
3. Build Command: `npm run build`
4. Output Directory: `dist`
5. Set Environment Variable:
   - `VITE_API_URL`: Your deployed backend URL (e.g., `https://resume-api.up.railway.app`)

## Post-Deployment
- Run database migrations: `alembic upgrade head` (can be added to the backend Start Command).
- Verify CORS settings in the backend to ensure the frontend domain is allowed.
