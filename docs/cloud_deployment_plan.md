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
Create a `Dockerfile` in the repo root (or in `Copia de panelin_agent_v2` if that is the runtime context):

```Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Cloud Run provides $PORT
ENV PORT=8000

CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "${PORT}"]
```

> If the API lives inside `Copia de panelin_agent_v2`, adjust the Docker build context accordingly.

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
      - --allow-unauthenticated
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
  --allow-unauthenticated
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
- Add `/health` endpoint for readiness.
- Add basic alerts on error rate and latency.

---

## Fallback Option (If You Prefer AWS)
- Use **AWS App Runner** (simple) or **ECS Fargate + ALB** (more control).
- The container and OpenAPI steps remain the same.
- AWS App Runner has a similar developer experience to Cloud Run.

---

## Deliverables Checklist
- [x] `Dockerfile` (Created in `Copia de panelin_agent_v2/Dockerfile`)
- [x] `.dockerignore` (Created in `Copia de panelin_agent_v2/.dockerignore`)
- [x] `cloudbuild.yaml` (Created in workspace root)
- [ ] Cloud Run service live
- [ ] OpenAPI schema updated with Cloud Run URL
- [x] Optional: `/health` endpoint (Implemented in `api.py`)

## Improvements and Security
See `docs/cloud_run_deployment_improvements.md` for details on:
- Production-grade Dockerfile (using `sh -c` for PORT expansion)
- Health and Readiness probes
- Resource limits and autoscaling configuration
- Secret Manager and IAM recommendations

---

## Summary
**Best choice:** **Google Cloud Run** for this repo because it is minimal, scalable, and matches the current FastAPI/Uvicorn usage while removing local-tunnel and manual steps.
