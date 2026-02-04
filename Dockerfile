FROM python:3.11-slim

# Security: avoid running as root (Cloud Run compatible)
RUN useradd -m -u 10001 appuser

# Keep image lean and predictable
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install runtime dependencies (scoped to the FastAPI service)
# Use JSON-array COPY to safely handle spaces in path names.
COPY ["Copia de panelin_agent_v2/requirements.txt", "/app/requirements.txt"]
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy only the API service code (not the whole monorepo)
COPY ["Copia de panelin_agent_v2", "/app/panelin_api"]

WORKDIR /app/panelin_api

# Cloud Run provides $PORT at runtime
ENV PORT=8080

USER appuser

# Use shell form so ${PORT} expands at runtime.
CMD ["sh", "-c", "python -m uvicorn api:app --host 0.0.0.0 --port ${PORT}"]
