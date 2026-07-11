# Troubleshooting

## Common Issues

### 1. Database Connection Errors
**Error**: `psycopg2.OperationalError: could not connect to server: Connection refused`
**Solution**: Ensure your PostgreSQL service is running and the `DATABASE_URL` in your `.env` file is correct.

### 2. Redis Connection Errors
**Error**: `redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379. Connection refused.`
**Solution**: Make sure the Redis server is running. If using Docker, ensure the `redis` container is up.

### 3. Celery Tasks Not Processing
**Symptom**: Resumes are uploaded but stay in the "Processing" state indefinitely.
**Solution**: Ensure the Celery worker is running (`celery -A app.core.celery_app worker`). Check the worker logs for any errors related to the Gemini API or S3 storage.

### 4. CORS Errors on Frontend
**Symptom**: API requests from the frontend fail with a CORS policy error.
**Solution**: Add your frontend domain to the `CORS_ORIGINS` list in the backend configuration (`app/core/config.py` or via environment variable).

### 5. AI Parsing Fails
**Symptom**: "Failed to extract data using AI."
**Solution**: Verify your `GEMINI_API_KEY` is valid and has not exhausted its quota. Check backend logs for specific API error messages.
