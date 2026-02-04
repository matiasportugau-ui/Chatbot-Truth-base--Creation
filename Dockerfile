FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# Install runtime deps (pinned for Cloud Run image reproducibility)
COPY ["Copia de panelin_agent_v2/requirements-cloudrun.txt", "/app/requirements-cloudrun.txt"]
RUN pip install --no-cache-dir -r /app/requirements-cloudrun.txt

# Copy the API source into a path without spaces
COPY ["Copia de panelin_agent_v2", "/app/panelin_api"]

WORKDIR /app/panelin_api

EXPOSE 8080

# Cloud Run injects $PORT; shell form expands it at runtime.
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT}"]
