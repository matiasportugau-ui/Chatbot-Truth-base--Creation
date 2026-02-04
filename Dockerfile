FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

WORKDIR /app

COPY ["Copia de panelin_agent_v2/requirements.txt", "/app/requirements.txt"]
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

WORKDIR /app/Copia de panelin_agent_v2

CMD ["sh", "-c", "python -m uvicorn api:app --host 0.0.0.0 --port ${PORT}"]
