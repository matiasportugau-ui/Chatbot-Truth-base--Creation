FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Run the application
# Using sh -c to ensure $PORT is expanded correctly
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT}"]
