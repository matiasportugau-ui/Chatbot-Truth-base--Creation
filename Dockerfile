# ============================================================================
# Panelin Agent V2 - Production Dockerfile
# ============================================================================
# Multi-stage build for optimized container size and security
# Properly handles Cloud Run's PORT environment variable
# ============================================================================

# -----------------------------
# Stage 1: Builder
# -----------------------------
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better layer caching
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install production web server dependencies
RUN pip install --no-cache-dir \
    uvicorn[standard]==0.29.0 \
    fastapi==0.111.0 \
    gunicorn==22.0.0 \
    python-multipart==0.0.9

# -----------------------------
# Stage 2: Production Runtime
# -----------------------------
FROM python:3.11-slim AS runtime

# Security: Create non-root user
RUN groupadd -r panelin && useradd -r -g panelin panelin

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=panelin:panelin . /app

# Cloud Run injects PORT environment variable (default 8080)
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check endpoint validation
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health')" || exit 1

# Switch to non-root user for security
USER panelin

# Expose the port (documentation only - Cloud Run manages this)
EXPOSE ${PORT}

# -----------------------------
# Entrypoint with proper PORT expansion
# -----------------------------
# Using shell form to ensure ${PORT} is expanded at runtime
# This is CRITICAL for Cloud Run compatibility
CMD exec uvicorn api:app \
    --host 0.0.0.0 \
    --port ${PORT} \
    --workers 1 \
    --loop uvloop \
    --http httptools \
    --access-log \
    --log-level info
