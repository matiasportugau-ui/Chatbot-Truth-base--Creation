# Cloud Deployment Recommendation & Implementation Plan

> **STATUS: IMPLEMENTED** - All deliverables have been created. See `CLOUD_DEPLOYMENT_GUIDE.md` for deployment instructions.

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
- **Secrets** managed in **Secret Manager** and injected into Cloud Run (env or volume) with rotation.
- **Dedicated service account** for the Cloud Run service (least privilege).
- **Access control** decided explicitly: public (`--allow-unauthenticated`) vs IAM-authenticated/IAP.

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

# Use shell form so ${PORT} expands at runtime.
CMD ["sh", "-c", "python -m uvicorn api:app --host 0.0.0.0 --port ${PORT}"]
```

> If the API lives inside `Copia de panelin_agent_v2`, adjust the Docker build context accordingly.
> Note: JSON-form CMD does **not** expand `${PORT}` unless you use a shell.

### 2) Pin dependencies
Ensure `requirements.txt` uses pinned versions for reproducible builds (e.g., via `pip-compile`).

### 3) Add a `.dockerignore`
Avoid shipping large files (e.g., training data, analysis outputs).
Example exclusions (tailor to runtime needs):
```
training_data/
ingestion_analysis_output/
.corrections_backup/
**/*.pdf
**/*.rtf
**/*.zip
**/*.csv
wiki/
docs/
```

### 4) Create a Cloud Build config
Example `cloudbuild.yaml`:

```yaml
steps:
  - name: "gcr.io/cloud-builders/docker"
    args: ["build", "-t", "${_REGION}-docker.pkg.dev/${_PROJECT_ID}/${_REPO}/${_SERVICE}:$COMMIT_SHA", "."]
  - name: "python:3.11-slim"
    entrypoint: sh
    args: ["-c", "pip install -r requirements.txt && pytest -q"]
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
      # Choose one: public or IAM-authenticated
      # - --allow-unauthenticated
      # - --no-allow-unauthenticated
substitutions:
  _REGION: us-central1
  _REPO: panelin
  _SERVICE: panelin-api
```
Add separate triggers for staging vs production and promote by tag.

### 5) Create Artifact Registry Repo
```bash
gcloud artifacts repositories create panelin \
  --repository-format=docker \
  --location=us-central1
```

### 6) Deploy to Cloud Run (Manual First Run)
```bash
gcloud run deploy panelin-api \
  --source . \
  --region us-central1 \
  --service-account panelin-runner@<PROJECT_ID>.iam.gserviceaccount.com \
  --memory 512Mi --cpu 1 \
  --timeout 300 --concurrency 80 \
  --min-instances 0 --max-instances 10 \
  --set-secrets "OPENAI_API_KEY=projects/<PROJECT_ID>/secrets/OPENAI_API_KEY:latest" \
  --no-allow-unauthenticated
```
If the service must be public, replace `--no-allow-unauthenticated` with `--allow-unauthenticated`.

### 7) Health/readiness endpoints
- Implement `/health` (liveness) and `/ready` (readiness) with real checks.
- Configure timeouts/concurrency in Cloud Run to avoid cold-start surprises.

### 8) Monitoring & reliability
- Enable Cloud Run logging (default) and add **Cloud Monitoring alerts**:
  - Error rate > X%
  - P95 latency > X ms
  - Restart frequency / cold starts above threshold
- Add tracing (Cloud Trace or OpenTelemetry) if the service calls external APIs.

### 9) Data persistence strategy
If the service stores state, define the backing system explicitly:
- **Cloud SQL / Firestore** for structured data.
- **GCS** for files/exports.
Avoid relying on the container filesystem (ephemeral).

### 10) Update OpenAPI Schema for Production
Replace the temporary Localtunnel URL with the Cloud Run URL:

```json
"servers": [
  { "url": "https://panelin-api-xxxxx-uc.a.run.app", "description": "Cloud Run Production" }
]
```

---

## Fallback Option (If You Prefer AWS)
- Use **AWS App Runner** (simple) or **ECS Fargate + ALB** (more control).
- The container and OpenAPI steps remain the same.
- AWS App Runner has a similar developer experience to Cloud Run.

---

## Deliverables Checklist
- [x] `Dockerfile` - Created in repo root
- [x] `.dockerignore` - Created with comprehensive exclusions
- [x] `cloudbuild.yaml` - Full CI/CD pipeline configured
- [x] Pinned `requirements.txt` - All dependencies version-locked
- [x] Service account with least privilege - Documented in CLOUD_DEPLOYMENT_GUIDE.md
- [x] Secret Manager integration - Configured in cloudbuild.yaml
- [x] `/health` and `/ready` endpoints - Added to api.py with proper checks
- [x] Cloud Run resource limits (cpu/memory/timeout/concurrency) - Configured in cloudbuild.yaml
- [x] Access control decision (public vs IAM/IAP) - Defaulted to public for GPT Actions
- [x] Monitoring alerts (error rate/latency) - Documented in CLOUD_DEPLOYMENT_GUIDE.md
- [x] Data persistence choice documented - In CLOUD_DEPLOYMENT_GUIDE.md
- [ ] Cloud Run service live - **Pending: requires GCP project and credentials**
- [x] OpenAPI schema updated with Cloud Run URL - Template URL added

---

## Summary
**Best choice:** **Google Cloud Run** for this repo because it is minimal, scalable, and matches the current FastAPI/Uvicorn usage while removing local-tunnel and manual steps.
To be production-grade, add Secret Manager + IAM, explicit resource limits, /health + /ready, alerting/tracing, and a data persistence strategy.
