FROM python:3.11-slim

WORKDIR /app

# Copy requirements from the agent directory
COPY panelin_agent_v2/requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the agent code
COPY panelin_agent_v2/ /app

# Cloud Run provides the PORT environment variable.
# We set a default for local testing.
ENV PORT=8080

# Use shell form to allow variable expansion of ${PORT}
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT}"]
