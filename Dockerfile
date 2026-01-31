FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install runtime dependencies (pinned for reproducibility)
COPY "Copia de panelin_agent_v2/requirements.txt" /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy only the API runtime code to keep image small
COPY "Copia de panelin_agent_v2" /app

# Cloud Run provides $PORT (default to 8080 locally)
ENV PORT=8080

# NOTE: Use shell form to expand ${PORT}; JSON CMD does not expand env vars.
CMD ["sh", "-c", "python -m uvicorn api:app --host 0.0.0.0 --port ${PORT:-8080} --proxy-headers --forwarded-allow-ips='*'"]

