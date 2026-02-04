FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Cloud Run provides $PORT environment variable
ENV PORT=8000

# Expose the port (documentation only, Cloud Run uses $PORT)
EXPOSE 8000

# Health check (optional but recommended)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health')" || exit 1

# Use shell form so ${PORT} expands at runtime
CMD sh -c "python -m uvicorn api:app --host 0.0.0.0 --port ${PORT}"
