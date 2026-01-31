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
- **Service account** dedicated to the service (least-privilege).
- **Secrets** injected from **Secret Manager** (avoid plaintext env vars in configs).

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

# Cloud Run injects $PORT at runtime
ENV PORT=8080

# JSON-form CMD does not expand ${PORT}; use a shell or read env in code.
CMD ["sh", "-c", "python -m uvicorn api:app --host 0.0.0.0 --port ${PORT}"]
```

> If the API lives inside `Copia de panelin_agent_v2`, adjust the Docker build context accordingly.

### 2) Add a `.dockerignore`
Avoid shipping large files (e.g., training data, analysis outputs). Be explicit:
- `training_data/`, `ingestion_analysis_output/`, `*.pdf`, `*.csv`, `*.json` (large)
- `wiki/`, `docs/` (if not needed at runtime)
- caches, local outputs, and exports (`*.log`, `*.tmp`, `*.cache`)

### 3) Pin dependencies
Ensure `requirements.txt` uses pinned versions for reproducibility.

### 4) Configure service account + Secret Manager
Create a dedicated service account and bind secrets:
```bash
gcloud iam service-accounts create panelin-api-sa \
  --display-name "Panelin API Service Account"

gcloud secrets create PANELIN_API_KEY --replication-policy="automatic"
gcloud secrets add-iam-policy-binding PANELIN_API_KEY \
  --member="serviceAccount:panelin-api-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```
Inject secrets at deploy time:
```bash
gcloud run deploy panelin-api \
  --set-secrets PANELIN_API_KEY=projects/PROJECT_ID/secrets/PANELIN_API_KEY:latest
```

### 5) Create a Cloud Build config
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
      - --service-account
      - ${_SERVICE_ACCOUNT}
      # Remove if private; use IAM + run.invoker instead.
      - --allow-unauthenticated
      # Resource, scaling, and timeout controls (tune for your workload).
      - --cpu
      - "1"
      - --memory
      - "512Mi"
      - --concurrency
      - "40"
      - --timeout
      - "300"
substitutions:
  _REGION: us-central1
  _REPO: panelin
  _SERVICE: panelin-api
  _SERVICE_ACCOUNT: panelin-api-sa@${_PROJECT_ID}.iam.gserviceaccount.com
```

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
  --timeout 300 \
  --max-instances 5 \
  --allow-unauthenticated
```

### 8) Update OpenAPI Schema for Production
Replace the temporary Localtunnel URL with the Cloud Run URL:

```json
"servers": [
  { "url": "https://panelin-api-xxxxx-uc.a.run.app", "description": "Cloud Run Production" }
]
```

### 9) Health, readiness, and timeouts
- Implement **`/health`** (liveness) and **`/ready`** (readiness) endpoints.
- Ensure `/ready` validates critical dependencies (e.g., database connectivity).
- Set **timeouts/retries** in outbound calls to prevent hung requests.

### 10) Monitoring & Reliability
- Enable **Cloud Run logging** (default).
- Add **Cloud Monitoring alerts** for:
  - Error rate > X%
  - P95 latency > X ms
  - Restart frequency / cold starts
- Add **tracing** (Cloud Trace or OpenTelemetry) if calling external APIs.

---

## Fallback Option (If You Prefer AWS)
- Use **AWS App Runner** (simple) or **ECS Fargate + ALB** (more control).
- The container and OpenAPI steps remain the same.
- AWS App Runner has a similar developer experience to Cloud Run.

---

## Deliverables Checklist
- [ ] `Dockerfile`
- [ ] `.dockerignore`
- [ ] `requirements.txt` pinned versions
- [ ] `cloudbuild.yaml`
- [ ] Cloud Run service live
- [ ] OpenAPI schema updated with Cloud Run URL
- [ ] `/health` and `/ready` endpoints
- [ ] Secret Manager integration + service account
- [ ] Resource limits + scaling config

---

## Production Hardening Checklist (Recommended Before Launch)
### Security & Identity
- [ ] Use **Secret Manager** (`--set-secrets`) instead of plaintext env vars.
- [ ] Dedicated **service account** with least-privilege IAM.
- [ ] Decide **public vs private**:
  - Public: keep `--allow-unauthenticated`.
  - Private: remove it and grant `roles/run.invoker` to trusted identities.
- [ ] Consider **API Gateway / Cloud Armor** for rate limiting or IP allowlists.

### Resilience & Availability
- [ ] Define **CPU/memory**, **concurrency**, **timeout**, **min/max instances**.
- [ ] Avoid long cold starts (min-instances) if low latency is required.
- [ ] Implement robust retries and timeouts for external services.

### Observability
- [ ] Alerts for error rate, latency (P95/P99), and restart rates.
- [ ] Tracing for external calls or multi-service flows.

### CI/CD & Release Management
- [ ] Add **lint/tests** to Cloud Build before deploy.
- [ ] Separate **staging/production** with controlled promotion.
- [ ] Versioned releases with rollback strategy.

### Data & Persistence
- [ ] Define state storage: **Cloud SQL**, **Firestore**, or **GCS**.
- [ ] Document backup and retention strategy.

---

## Summary
**Best choice:** **Google Cloud Run** for this repo because it is minimal, scalable, and matches the current FastAPI/Uvicorn usage while removing local-tunnel and manual steps.
