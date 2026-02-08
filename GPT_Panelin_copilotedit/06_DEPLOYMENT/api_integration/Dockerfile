# Panelin V3 API - Dockerfile for Google Cloud Run
# Build context: GPT_Panelin_copilotedit/

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy Python tools (calculator and dependencies)
COPY 03_PYTHON_TOOLS /app/03_PYTHON_TOOLS

# Copy knowledge base files (required by calculator)
COPY 01_KNOWLEDGE_BASE /app/01_KNOWLEDGE_BASE

# Copy API application files
COPY 06_DEPLOYMENT/api_integration/main.py /app/main.py
COPY 06_DEPLOYMENT/api_integration/requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for Cloud Run
EXPOSE 8080

# Set environment variable for Cloud Run
ENV PORT=8080

# Run the FastAPI application - use shell form to expand $PORT
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
