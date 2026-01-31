FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install pinned runtime dependencies (production build)
COPY ["Copia de panelin_agent_v2/requirements.prod.txt", "/app/requirements.txt"]
RUN python -m pip install --no-cache-dir -r /app/requirements.txt

# Copy only the deployable API + tools (keeps image small)
COPY ["Copia de panelin_agent_v2/", "/app/"]

# Run as non-root for better security
RUN useradd --create-home --uid 10001 appuser && chown -R appuser:appuser /app
USER appuser

# Cloud Run injects PORT (default 8080)
ENV PORT=8080

EXPOSE 8080

CMD ["sh", "-c", "python -m uvicorn api:app --host 0.0.0.0 --port ${PORT:-8080} --proxy-headers --forwarded-allow-ips='*'"]
