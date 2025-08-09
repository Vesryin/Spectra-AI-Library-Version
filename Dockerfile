FROM python:3.12-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose FastAPI port (Ollama expected external; expose 11434 only if sidecar desired)
EXPOSE 8000

ENV HOST=0.0.0.0 \
    PORT=8000 \
    ENVIRONMENT=production \
    FASTAPI_RELOAD=false \
    SPECTRA_LOG_FORMAT=json \
    SPECTRA_LOG_LEVEL=INFO

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production server via gunicorn + uvicorn workers
CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]