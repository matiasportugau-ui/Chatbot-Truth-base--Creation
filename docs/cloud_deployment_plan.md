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
Create a `Dockerfile` in the repo root. For this repo, the runtime FastAPI app lives in `Copia de panelin_agent_v2/api.py`, so the Dockerfile should **only copy that folder** (smaller image + faster builds):

```Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY "Copia de panelin_agent_v2/requirements.txt" /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY "Copia de panelin_agent_v2" /app

# Cloud Run provides $PORT
ENV PORT=8080

# IMPORTANT:
# - JSON-form CMD does NOT expand ${PORT}
# - Use shell to expand $PORT (Cloud Run sets it)
CMD ["sh", "-c", "python -m uvicorn api:app --host 0.0.0.0 --port ${PORT:-8080}"]
```

This repo already includes a production-ready `Dockerfile` at the root with the correct `PORT` handling.

### 2) Add a `.dockerignore`
Avoid shipping large files (training data, PDFs, exports, wiki, etc.). This has a **large impact** on build time and Cloud Build cost because the full repo is the build context.

This repo already includes a production-oriented `.dockerignore` at the root.

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
      # SECURITY: make public only if you explicitly need it
      - --no-allow-unauthenticated
substitutions:
  _REGION: us-central1
  _REPO: panelin
  _SERVICE: panelin-api
```

This repo already includes a `cloudbuild.yaml` at the root (secure-by-default + basic resource flags).

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

#### Recommended Cloud Run flags (production baseline)
Tune these based on load, latency targets, and downstream dependencies:

```bash
gcloud run deploy panelin-api \
  --region us-central1 \
  --no-allow-unauthenticated \
  --cpu 1 \
  --memory 512Mi \
  --concurrency 40 \
  --timeout 300 \
  --min-instances 0 \
  --max-instances 10
```

---

## Security & Identity (production-grade)

### Secret Manager (instead of “plain env vars”)
Prefer binding secrets directly from Secret Manager to Cloud Run:

```bash
# Create secrets (examples)
echo -n "..." | gcloud secrets create OPENAI_API_KEY --data-file=-
echo -n "..." | gcloud secrets create SHOPIFY_WEBHOOK_SECRET --data-file=-

# Deploy and inject secrets as env vars
gcloud run deploy panelin-api \
  --region us-central1 \
  --set-secrets OPENAI_API_KEY=OPENAI_API_KEY:latest,SHOPIFY_WEBHOOK_SECRET=SHOPIFY_WEBHOOK_SECRET:latest
```

**Rotation**: publish a new secret version and redeploy (or reference `:latest` if your process supports it).

### IAM granular (dedicated service account)
Create a service account for the service (least privilege), then deploy with it:

```bash
gcloud iam service-accounts create panelin-api-sa \
  --display-name="Panelin API Cloud Run"

gcloud run deploy panelin-api \
  --region us-central1 \
  --service-account panelin-api-sa@${PROJECT_ID}.iam.gserviceaccount.com
```

Grant only what it needs (e.g., Secret Manager access):

```bash
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:panelin-api-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Restrict access (public vs private)
- **Public API**: only then use `--allow-unauthenticated` and consider adding API Gateway / Cloud Armor for rate limiting / allowlists.
- **Private/internal**: keep `--no-allow-unauthenticated` and require IAM auth (signed identity tokens) or an API Gateway in front.

### 6) Update OpenAPI Schema for Production
Replace the temporary Localtunnel URL with the Cloud Run URL:

```json
"servers": [
  { "url": "https://panelin-api-xxxxx-uc.a.run.app", "description": "Cloud Run Production" }
]
```

### 7) Monitoring & Reliability
- Enable **Cloud Run logging** (default).
- Implement explicit endpoints:
  - `GET /health` (liveness)
  - `GET /ready` (readiness: validates knowledge base is loadable)
- Add basic alerts on error rate and latency (Cloud Monitoring):
  - Error rate \(> X%\)
  - Latency P95 \(> Y ms\)
  - Instance restarts / cold starts frequency (if relevant)

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
- [ ] `/health` (liveness) endpoint
- [ ] `/ready` (readiness) endpoint

---

## Summary
**Best choice:** **Google Cloud Run** for this repo because it is minimal, scalable, and matches the current FastAPI/Uvicorn usage while removing local-tunnel and manual steps.
