FROM python:3.11-slim

WORKDIR /app

# Copy requirements file
COPY Copia\ de\ panelin_agent_v2/requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY Copia\ de\ panelin_agent_v2 /app

# Cloud Run provides $PORT environment variable
ENV PORT=8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health')"

# Expose port (documentation only, Cloud Run uses $PORT)
EXPOSE 8080

# Use shell form to allow ${PORT} expansion at runtime
CMD ["sh", "-c", "python -m uvicorn api:app --host 0.0.0.0 --port ${PORT}"]
