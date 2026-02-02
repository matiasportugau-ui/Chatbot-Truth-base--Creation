FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY ["Copia de panelin_agent_v2/requirements.txt", "."]

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY ["Copia de panelin_agent_v2", "."]

# Cloud Run sets PORT environment variable (default 8080)
ENV PORT=8080

# Run the application
# Using sh -c to ensure $PORT is expanded correctly
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT} --workers 1"]
