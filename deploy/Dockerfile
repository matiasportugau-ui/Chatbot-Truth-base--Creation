# ============================================
# PANELIN PRODUCTION DOCKERFILE
# Cloud Run Optimized - v2.0
# ============================================
# 
# Key Features:
# - Multi-stage build for smaller image
# - Correct PORT expansion with shell exec
# - Non-root user for security
# - Health check support
# - Python 3.11 slim base
#
# Build:
#   docker build -t panelin-api:latest -f deploy/Dockerfile .
#
# Run locally:
#   docker run -p 8080:8080 -e PORT=8080 panelin-api:latest
# ============================================

# ---- Builder Stage ----
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better caching
COPY requirements.txt requirements-prod.txt ./

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install production dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-prod.txt


# ---- Production Stage ----
FROM python:3.11-slim as production

# Labels for image metadata
LABEL maintainer="Panelin Engineering <engineering@bmcuruguay.com>"
LABEL version="2.0.0"
LABEL description="Panelin API - BMC Uruguay Panel Quotation Service"

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    # Default port (Cloud Run will override via PORT env)
    PORT=8080 \
    # Application settings
    APP_ENV=production \
    LOG_LEVEL=INFO \
    # Worker settings
    WORKERS=1 \
    WORKER_TIMEOUT=120

# Create non-root user for security
RUN groupadd --gid 1000 panelin && \
    useradd --uid 1000 --gid panelin --shell /bin/bash --create-home panelin

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=panelin:panelin . .

# Switch to non-root user
USER panelin

# Expose port (documentation only - Cloud Run manages networking)
EXPOSE 8080

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health')" || exit 1

# IMPORTANT: Use shell form to expand ${PORT} variable
# Cloud Run sets PORT dynamically, and JSON form ["uvicorn", ...] does NOT expand variables
CMD sh -c "uvicorn api:app --host 0.0.0.0 --port ${PORT} --workers ${WORKERS} --timeout-keep-alive ${WORKER_TIMEOUT} --access-log"
