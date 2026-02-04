# Panelin Agent V2 - Cloud Run Dockerfile
# =========================================
# Optimized for Google Cloud Run deployment
# Build: docker build -t panelin-api .
# Run: docker run -p 8080:8080 panelin-api

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (minimal for production)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Cloud Run provides $PORT environment variable (defaults to 8080)
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose the port
EXPOSE ${PORT}

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Use shell form so ${PORT} expands at runtime
CMD ["sh", "-c", "python -m uvicorn api:app --host 0.0.0.0 --port ${PORT}"]
