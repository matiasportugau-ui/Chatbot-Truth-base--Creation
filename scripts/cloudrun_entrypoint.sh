#!/bin/sh
# Cloud Run entrypoint: ensure we listen on PORT (default 8080)
set -e
PORT="${PORT:-8080}"
echo "Starting Panelin API on 0.0.0.0:${PORT}" >&2
exec python -m uvicorn panelin_agent_v2.api:app --host 0.0.0.0 --port "$PORT"
