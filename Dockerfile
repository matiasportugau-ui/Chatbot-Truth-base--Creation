FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install runtime deps first for better layer caching
COPY "Copia de panelin_agent_v2/requirements-prod.txt" /app/requirements-prod.txt
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements-prod.txt

# Copy only the API runtime code
COPY "Copia de panelin_agent_v2" "/app/Copia de panelin_agent_v2"

WORKDIR "/app/Copia de panelin_agent_v2"

# Cloud Run provides $PORT (commonly 8080)
ENV PORT=8080
EXPOSE 8080

# Use shell form so ${PORT} expands at runtime.
CMD ["sh", "-c", "python -m uvicorn api:app --host 0.0.0.0 --port ${PORT}"]
