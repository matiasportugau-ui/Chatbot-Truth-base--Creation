# ============================================================================
# Panelin API - Production Dockerfile
# ============================================================================
# Multi-stage build for optimized production image
# Properly handles Cloud Run's PORT environment variable
# ============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install dependencies
# -----------------------------------------------------------------------------
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt /app/requirements.txt
COPY panelin_agent_v2/requirements.txt /app/panelin_agent_v2_requirements.txt

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install all dependencies with pinned versions
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r panelin_agent_v2_requirements.txt

# Install production server dependencies
RUN pip install --no-cache-dir \
    uvicorn[standard]==0.30.1 \
    gunicorn==22.0.0 \
    fastapi==0.111.0 \
    pydantic==2.7.4 \
    opentelemetry-instrumentation-fastapi==0.46b0 \
    opentelemetry-exporter-gcp-trace==1.6.0 \
    google-cloud-secret-manager==2.20.0

# -----------------------------------------------------------------------------
# Stage 2: Production - Minimal runtime image
# -----------------------------------------------------------------------------
FROM python:3.11-slim as production

# Security: Run as non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code (respecting .dockerignore)
COPY --chown=appuser:appgroup . /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    # Default port (Cloud Run will override via PORT env var)
    PORT=8080 \
    # Uvicorn settings
    UVICORN_WORKERS=1 \
    UVICORN_HOST=0.0.0.0 \
    # Enable Cloud Run optimizations
    GOOGLE_CLOUD_PROJECT="" \
    K_SERVICE="" \
    K_REVISION=""

# Health check (Cloud Run uses HTTP probes)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health')" || exit 1

# Switch to non-root user
USER appuser

# Expose port (documentation only - Cloud Run sets PORT)
EXPOSE 8080

# -----------------------------------------------------------------------------
# CMD: Properly expand PORT variable using shell form
# -----------------------------------------------------------------------------
# IMPORTANT: JSON form ["python", "-m", "uvicorn", ...] does NOT expand ${PORT}
# We use shell form with exec to ensure proper signal handling
# 
# For production with gunicorn (recommended for multi-worker):
# CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker api:app
#
# For Cloud Run with single worker (uvicorn is sufficient):
CMD exec uvicorn api:app --host 0.0.0.0 --port $PORT --workers 1 --loop uvloop --http httptools
