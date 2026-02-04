# Panelin Agent V2 - Cloud Run Dockerfile
# ========================================
# Optimized for Google Cloud Run deployment

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
# Note: We copy from "Copia de panelin_agent_v2" as the main API source
COPY "Copia de panelin_agent_v2/" /app/

# Copy knowledge base files needed by the application
COPY panelin_core/knowledge_base/ /app/config/

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Cloud Run provides $PORT environment variable (default to 8080)
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Health check configuration
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Use shell form so ${PORT} expands at runtime
# Cloud Run expects the container to listen on the port specified by $PORT
CMD ["sh", "-c", "python -m uvicorn api:app --host 0.0.0.0 --port ${PORT}"]
