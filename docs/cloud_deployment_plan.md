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
- **Secrets** sourced from **Secret Manager** and injected into Cloud Run at deploy time (supports rotation).
- **Dedicated service account** for the service with least-privilege IAM roles.
- **Access control** defined explicitly (public vs IAM-authenticated).

## Production Hardening Additions (Recommended)
- **Security & identity**: Secret Manager + service account scoping + avoid public endpoints unless required.
- **Runtime limits**: define CPU, memory, concurrency, min/max instances, and timeouts.
- **Health checks**: implement `/health` (liveness) and `/ready` (readiness).
- **Observability**: error-rate and latency alerts, tracing for external calls.
- **Data persistence**: decide on Cloud SQL/Firestore/GCS if state is required.

---

## Implementation Plan (Step-by-Step)

### 1) Containerize the API
Create a `Dockerfile` in the repo root (or in `Copia de panelin_agent_v2` if that is the runtime context):

```Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Cloud Run provides $PORT at runtime.
ENV PORT=8000

# Use shell form to expand ${PORT} correctly in Cloud Run.
CMD ["bash", "-c", "python -m uvicorn api:app --host 0.0.0.0 --port ${PORT}"]
```

> If the API lives inside `Copia de panelin_agent_v2`, adjust the Docker build context accordingly.

### 2) Add a `.dockerignore`
Avoid shipping large files (e.g., training data, analysis outputs). Recommended patterns:

```
**/training_data/**
**/analysis_output/**
**/ingestion_analysis_output/**
**/*.pdf
**/*.csv
**/*.json
**/wiki/**
**/.kb_update_cache/**
**/.corrections_backup/**
**/__pycache__/**
```

### 3) Pin Dependencies
Pin versions in `requirements.txt` for reproducible builds and safer rollbacks.

### 4) Create a Cloud Build config
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
      # Access control (choose one):
      # - --allow-unauthenticated
      # - --no-allow-unauthenticated
      # Runtime limits (tune for your workload):
      - --cpu
      - "1"
      - --memory
      - "512Mi"
      - --concurrency
      - "40"
      - --timeout
      - "60"
      - --min-instances
      - "0"
      - --max-instances
      - "5"
      # Service account (least privilege):
      - --service-account
      - ${_SERVICE_ACCOUNT}
      # Secret Manager bindings (example):
      # - --set-secrets=API_KEY=panelin-api-key:latest
substitutions:
  _REGION: us-central1
  _REPO: panelin
  _SERVICE: panelin-api
  _SERVICE_ACCOUNT: panelin-api-sa@${_PROJECT_ID}.iam.gserviceaccount.com
```

### 5) CI/CD Gating & Environments (Recommended)
- Add **lint/tests** before deploy in Cloud Build.
- Use **staging vs production** deploy targets with controlled promotion.
- Tag images by environment (e.g., `:staging`, `:prod`) and keep rollback history.

### 6) Create Artifact Registry Repo
```bash
gcloud artifacts repositories create panelin \
  --repository-format=docker \
  --location=us-central1
```

### 7) Deploy to Cloud Run (Manual First Run)
```bash
gcloud run deploy panelin-api \
  --source . \
  --region us-central1 \
  --service-account panelin-api-sa@PROJECT_ID.iam.gserviceaccount.com \
  --cpu 1 \
  --memory 512Mi \
  --concurrency 40 \
  --timeout 60 \
  --min-instances 0 \
  --max-instances 5
# Add --allow-unauthenticated only if the API is truly public.
```

### 8) Update OpenAPI Schema for Production
Replace the temporary Localtunnel URL with the Cloud Run URL:

```json
"servers": [
  { "url": "https://panelin-api-xxxxx-uc.a.run.app", "description": "Cloud Run Production" }
]
```

### 9) Monitoring & Reliability
- Enable **Cloud Run logging** (default).
- Implement `/health` (liveness) and `/ready` (readiness) endpoints.
- Add alerting in Cloud Monitoring:
  - Error rate > X%
  - Latency P95 > X ms
  - Restart frequency or cold starts spikes
- Add tracing for external calls (Cloud Trace or OpenTelemetry).

### 10) Secrets & Access Control
- Create secrets in **Secret Manager** and bind them at deploy time.
- Grant the Cloud Run service account only the roles it needs.
- If the API is private, use IAM auth (or API Gateway/IAP) instead of a public endpoint.
- Consider **Cloud Armor** or API Gateway for IP allowlists and rate limits.

### 11) Data Persistence (If Needed)
- If the API stores state, choose one:
  - **Cloud SQL** for relational data
  - **Firestore** for document data
  - **GCS** for file/object storage

---

## Fallback Option (If You Prefer AWS)
- Use **AWS App Runner** (simple) or **ECS Fargate + ALB** (more control).
- The container and OpenAPI steps remain the same.
- AWS App Runner has a similar developer experience to Cloud Run.

---

## Deliverables Checklist
- [ ] `Dockerfile`
- [ ] `.dockerignore`
- [ ] `requirements.txt` pinned
- [ ] `cloudbuild.yaml`
- [ ] Cloud Run service live
- [ ] OpenAPI schema updated with Cloud Run URL
- [ ] `/health` and `/ready` endpoints
- [ ] Secrets bound via Secret Manager
- [ ] Access policy defined (public vs IAM)

---

## Summary
**Best choice:** **Google Cloud Run** for this repo because it is minimal, scalable, and matches the current FastAPI/Uvicorn usage while removing local-tunnel and manual steps.
