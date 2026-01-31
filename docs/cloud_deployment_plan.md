# Cloud Deployment Recommendation & Implementation Plan

## Best Option: Google Cloud Run + Artifact Registry + Cloud Build

**Why this is the best fit for this repo**
- **Container-native**: The current deployment script runs a FastAPI/Uvicorn service locally (`api:app`). Cloud Run is optimized for containerized HTTP services and removes server management overhead.
- **Auto-scaling and cost efficiency**: Scales to zero when idle and scales up with traffic.
- **Simplified HTTPS & public URL**: Cloud Run provides a stable HTTPS endpoint that can replace the current Localtunnel URL injection step.
- **Easy CI/CD**: Cloud Build integrates directly with GitHub and Artifact Registry.

## Current State Observations
The local deployment helper (`scripts/deploy_thewolf.py`) currently:
- Starts Uvicorn locally on port 8000.
- Uses Localtunnel to expose the service publicly and prints a modified OpenAPI schema.

This is excellent for local dev but **not production-grade** because:
- Localtunnel URLs are ephemeral.
- The server is bound to `127.0.0.1`.
- The process requires a terminal to stay alive.

## Target Cloud Architecture (Minimal & Stable)
- **Container image** built from this repo.
- **Cloud Run service** exposes `https://<service>.run.app`.
- **OpenAPI servers** entry points to the Cloud Run URL for the action schema.
- **Secrets** stored in environment variables (Cloud Run supports direct secret injection).

---

## Implementation Plan (Step-by-Step)

### 1) Containerize the API
Create a `Dockerfile` in the repo root (this repo’s deployable FastAPI app lives in `Copia de panelin_agent_v2/api.py`).

```Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install pinned production deps (recommended)
COPY ["Copia de panelin_agent_v2/requirements.prod.txt", "/app/requirements.txt"]
RUN python -m pip install --no-cache-dir -r /app/requirements.txt

# Copy only the API runtime folder
COPY ["Copia de panelin_agent_v2/", "/app/"]

# Cloud Run injects $PORT (default 8080)
ENV PORT=8080

# IMPORTANT: use a shell so ${PORT} expands
CMD ["sh","-c","python -m uvicorn api:app --host 0.0.0.0 --port ${PORT:-8080}"]
```

> **Important**: In JSON-array `CMD` format, `${PORT}` does **not** expand unless you run through a shell (`sh -c`). This is a common Cloud Run startup failure.

### 2) Add a `.dockerignore`
Avoid shipping large files (e.g., training data, analysis outputs).

### 3) Create a Cloud Build config
Example `cloudbuild.yaml`:

```yaml
steps:
  - name: "gcr.io/cloud-builders/docker"
    args: ["build", "-t", "${_REGION}-docker.pkg.dev/${_PROJECT_ID}/${_REPO}/${_SERVICE}:$COMMIT_SHA", "."]
  - name: "gcr.io/cloud-builders/docker"
    args: ["push", "${_REGION}-docker.pkg.dev/${_PROJECT_ID}/${_REPO}/${_SERVICE}:$COMMIT_SHA"]
  - name: "gcr.io/google.com/cloudsdktool/cloud-sdk"
    entrypoint: gcloud
    args:
      - run
      - deploy
      - ${_SERVICE}
      - --image
      - ${_REGION}-docker.pkg.dev/${_PROJECT_ID}/${_REPO}/${_SERVICE}:$COMMIT_SHA
      - --region
      - ${_REGION}
      - --platform
      - managed
      # Prefer private-by-default (remove this line only if API must be public)
      - --no-allow-unauthenticated
substitutions:
  _REGION: us-central1
  _REPO: panelin
  _SERVICE: panelin-api
```

### 4) Create Artifact Registry Repo
```bash
gcloud artifacts repositories create panelin \
  --repository-format=docker \
  --location=us-central1
```

### 5) Deploy to Cloud Run (Manual First Run)
```bash
gcloud run deploy panelin-api \
  --source . \
  --region us-central1 \
  --no-allow-unauthenticated
```

### 6) Update OpenAPI Schema for Production
Replace the temporary Localtunnel URL with the Cloud Run URL:

```json
"servers": [
  { "url": "https://panelin-api-xxxxx-uc.a.run.app", "description": "Cloud Run Production" }
]
```

### 7) Monitoring & Reliability
- Enable **Cloud Run logging** (default).
- Implement **liveness vs readiness** explicitly:
  - `GET /health`: liveness (process is up)
  - `GET /ready`: readiness (KB loaded + valid)
- Add basic alerts on error rate and latency.

---

## Production Hardening (Recommended)

### Security & Identity
- **Dedicated Service Account (least privilege)**: create and deploy with a service account specific to this service.
- **Secret Manager (don’t paste secrets as “flat” env vars)**: inject secrets via Cloud Run secret references, enabling rotation.
- **Restrict access**:
  - If internal/private: keep `--no-allow-unauthenticated` and use IAM Auth (caller must be authenticated).
  - If public: consider API Gateway + auth + rate limiting, and/or Cloud Armor for IP allowlists.

Example (Secret Manager injection):

```bash
gcloud run deploy panelin-api \
  --image "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/panelin-api:${TAG}" \
  --region "${REGION}" \
  --service-account "panelin-api-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --no-allow-unauthenticated \
  --set-secrets "OPENAI_API_KEY=OPENAI_API_KEY:latest"
```

### Cloud Run runtime settings (avoid surprises)
Define explicit limits so behavior is predictable:
- `--cpu`, `--memory`
- `--concurrency`
- `--timeout`
- `--min-instances` (optional, for low-latency / reduce cold starts)
- `--max-instances` (cost control)

### Observability
Add Cloud Monitoring alerts with concrete thresholds, e.g.:
- error rate \(> X%\)
- latency P95 \(> Y ms\)
- container restarts / cold starts spikes

### Data persistence
Cloud Run containers are stateless. If you need state:
- **DB**: Cloud SQL / Firestore (preferred for transactional/state)
- **Storage**: GCS for blobs/files

---

## Fallback Option (If You Prefer AWS)
- Use **AWS App Runner** (simple) or **ECS Fargate + ALB** (more control).
- The container and OpenAPI steps remain the same.
- AWS App Runner has a similar developer experience to Cloud Run.

---

## Deliverables Checklist
- [ ] `Dockerfile`
- [ ] `.dockerignore`
- [ ] `cloudbuild.yaml`
- [ ] Cloud Run service live
- [ ] OpenAPI schema updated with Cloud Run URL
- [ ] Optional: `/health` endpoint

---

## Summary
**Best choice:** **Google Cloud Run** for this repo because it is minimal, scalable, and matches the current FastAPI/Uvicorn usage while removing local-tunnel and manual steps.
