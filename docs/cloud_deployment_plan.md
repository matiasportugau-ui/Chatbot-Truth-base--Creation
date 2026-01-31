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
- **Secrets** stored in Secret Manager and injected into Cloud Run (rotation-friendly, no plain env values).
- **Dedicated service account** for the service (least-privilege access).
- **Access control** defined explicitly: public (`--allow-unauthenticated`) or IAM/IAP/API Gateway for private services.

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

# Cloud Run provides $PORT (defaults to 8080)
ENV PORT=8080

CMD ["sh", "-c", "python -m uvicorn api:app --host 0.0.0.0 --port ${PORT}"]
```

> If the API lives inside `Copia de panelin_agent_v2`, adjust the Docker build context accordingly.
> Pin dependency versions in `requirements.txt` for reproducible builds.

### 2) Add a `.dockerignore`
Avoid shipping large files (e.g., training data, analysis outputs). Example exclusions:
```
training_data/
ingestion_analysis_output/
.kb_update_cache/
**/out/
**/*.pdf
**/*.csv
**/*.rtf
**/*_results.json
```

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

Recommended hardening:
- Add a test/lint step before build/deploy (quality gate).
- Use separate triggers or substitutions for staging vs production promotion.
- Mirror the deploy flags from Step 6 (service account, secrets, resource limits, auth).

### 4) Create Artifact Registry Repo
```bash
gcloud artifacts repositories create panelin \
  --repository-format=docker \
  --location=us-central1
```

### 5) Set up IAM and Secret Manager
```bash
gcloud iam service-accounts create panelin-api-sa \
  --display-name "Panelin API"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:panelin-api-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

Create secrets in Secret Manager (e.g., API keys) and prefer using `:latest` with
regular rotation.

### 6) Deploy to Cloud Run (Manual First Run)
```bash
gcloud run deploy panelin-api \
  --source . \
  --region us-central1 \
  --service-account panelin-api-sa@${PROJECT_ID}.iam.gserviceaccount.com \
  --memory 512Mi \
  --cpu 1 \
  --concurrency 80 \
  --timeout 60 \
  --min-instances 0 \
  --max-instances 10 \
  --set-secrets "OPENAI_API_KEY=projects/${PROJECT_ID}/secrets/OPENAI_API_KEY:latest" \
  --allow-unauthenticated
```

If the service should be private, remove `--allow-unauthenticated` and grant the
`roles/run.invoker` permission to specific identities (or use IAP/API Gateway).
Consider Cloud Armor if you need rate limiting or IP allowlists.

### 7) Update OpenAPI Schema for Production
Replace the temporary Localtunnel URL with the Cloud Run URL:

```json
"servers": [
  { "url": "https://panelin-api-xxxxx-uc.a.run.app", "description": "Cloud Run Production" }
]
```

### 8) Monitoring, Health, and Reliability
- Enable **Cloud Run logging** (default).
- Implement `/health` (liveness) and `/ready` (readiness) endpoints with real checks.
- Use Cloud Monitoring uptime checks against `/health` and alert on failures.
- Define alerts for error rate, latency (P95), and restart/cold-start frequency.
- Add tracing (Cloud Trace or OpenTelemetry) if calling external APIs.

### 9) Data & Persistence
If the service needs state:
- **Cloud SQL** for relational data.
- **Firestore** for document data.
- **GCS** for files and exports.

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
- [ ] Dedicated service account + least-privilege IAM
- [ ] Secrets stored in Secret Manager and injected into Cloud Run
- [ ] Cloud Run service live
- [ ] Cloud Run resource limits set (cpu/memory/concurrency/timeout)
- [ ] OpenAPI schema updated with Cloud Run URL
- [ ] `/health` and `/ready` endpoints
- [ ] Monitoring alerts (error rate, latency, restarts)

---

## Summary
**Best choice:** **Google Cloud Run** for this repo because it is minimal, scalable, and matches the current FastAPI/Uvicorn usage while removing local-tunnel and manual steps.
