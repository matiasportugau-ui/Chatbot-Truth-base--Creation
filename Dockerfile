FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

COPY ["Copia de panelin_agent_v2/requirements.txt", "/app/requirements.txt"]
RUN pip install --no-cache-dir -r requirements.txt

COPY ["Copia de panelin_agent_v2/", "/app/"]

EXPOSE 8000

CMD ["sh", "-c", "python -m uvicorn api:app --host 0.0.0.0 --port ${PORT}"]
