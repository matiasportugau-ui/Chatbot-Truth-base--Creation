# Panelin Wolf API - Cloud Run
# Build from repo root so config + panelin_agent_v2 are both available.
FROM python:3.11-slim

WORKDIR /app

# Runtime env: Cloud Run sets PORT
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Install dependencies (pinned in requirements-cloudrun.txt)
COPY requirements-cloudrun.txt /app/requirements-cloudrun.txt
RUN pip install --no-cache-dir -r requirements-cloudrun.txt

# Copy only what the API needs
COPY config/ /app/config/
COPY panelin_agent_v2/ /app/panelin_agent_v2/

# Cloud Run expects the container to listen on $PORT
# Shell form so ${PORT} expands at runtime
CMD ["sh", "-c", "python -m uvicorn panelin_agent_v2.api:app --host 0.0.0.0 --port ${PORT}"]
