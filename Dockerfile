# Panelin Wolf API - Cloud Run
# Build from repo root so config + panelin_agent_v2 are both available.
FROM python:3.11-slim

WORKDIR /app

# Cloud Run sets PORT=8080; default to 8080 so we always listen on the right port
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Install dependencies (pinned in requirements-cloudrun.txt)
COPY requirements-cloudrun.txt /app/requirements-cloudrun.txt
RUN pip install --no-cache-dir -r requirements-cloudrun.txt

# Copy only what the API needs
COPY config/ /app/config/
COPY panelin_agent_v2/ /app/panelin_agent_v2/

# Entrypoint: read PORT (Cloud Run sets 8080) and start uvicorn
RUN printf '%s\n' '#!/bin/sh' 'set -e' 'PORT="${PORT:-8080}"' 'exec python -m uvicorn panelin_agent_v2.api:app --host 0.0.0.0 --port "$PORT"' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
