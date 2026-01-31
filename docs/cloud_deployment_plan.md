# Cloud Deployment Recommendation & Implementation Plan

> **Updated: 2026-01-31** - Enhanced for production-grade deployment with security, observability, and reliability improvements.

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

## Target Cloud Architecture (Production-Grade)
- **Container image** built from this repo with multi-stage optimization.
- **Cloud Run service** exposes `https://<service>.run.app`.
- **OpenAPI servers** entry points to the Cloud Run URL for the action schema.
- **Secrets** stored in **Secret Manager** with automatic injection at runtime.
- **Dedicated service account** with minimal IAM privileges.
- **Health/readiness endpoints** for proper orchestration.
- **Monitoring & alerting** for operational visibility.

---

## Production Files Overview

The following production-ready files have been created:

| File | Purpose |
|------|---------|
| `Dockerfile` | Multi-stage build with proper PORT handling |
| `.dockerignore` | Excludes large files, datasets, and sensitive data |
| `api.py` | Production API with /health and /ready endpoints |
| `cloudbuild.yaml` | CI/CD for staging with quality gates |
| `cloudbuild-production.yaml` | Stricter CI/CD for production |
| `cloudrun-config.yaml` | Resource and security configuration reference |
| `docs/PRODUCTION_DEPLOYMENT_GUIDE.md` | Comprehensive deployment guide |

---

## Implementation Plan (Step-by-Step)

### 1) Containerize the API (UPDATED)

The `Dockerfile` in the repo root uses multi-stage build and **properly handles PORT expansion**:

```Dockerfile
FROM python:3.11-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim AS runtime
RUN groupadd -r panelin && useradd -r -g panelin panelin
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY --chown=panelin:panelin . /app
ENV PORT=8080
USER panelin

# CRITICAL: Use shell form for proper ${PORT} expansion
CMD exec uvicorn api:app --host 0.0.0.0 --port ${PORT}
```

> **Note**: JSON array CMD format (`["cmd", "arg"]`) does NOT expand environment variables. Use shell form with `exec` for proper handling.

### 2) Add a `.dockerignore` (IMPLEMENTED)

Comprehensive exclusions to avoid shipping:
- Large JSON files and datasets
- Training data and analysis outputs
- PDFs and media files
- Development tools and tests
- Git history and IDE files

### 3) Create Cloud Build configs (IMPLEMENTED)

Two configurations available:

**`cloudbuild.yaml`** - For staging:
- Runs lint and tests (non-blocking)
- Deploys to staging environment
- Includes health check verification

**`cloudbuild-production.yaml`** - For production:
- **Strict** test requirements (must pass)
- Security scanning with bandit and safety
- Canary deployment support
- Production resource limits

### 4) Create Artifact Registry Repo
```bash
gcloud artifacts repositories create panelin \
  --repository-format=docker \
  --location=us-central1 \
  --description="Panelin API container images"
```

### 5) Security Setup (NEW)

#### Create dedicated service account:
```bash
gcloud iam service-accounts create panelin-api \
  --display-name="Panelin API Service Account"

# Grant minimal privileges
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:panelin-api@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

#### Store secrets in Secret Manager:
```bash
echo -n "sk-your-key" | gcloud secrets create OPENAI_API_KEY --data-file=-
echo -n "shpat_your-key" | gcloud secrets create SHOPIFY_API_KEY --data-file=-
```

### 6) Deploy to Cloud Run (UPDATED)

#### Staging:
```bash
gcloud run deploy panelin-api-staging \
  --image us-central1-docker.pkg.dev/$PROJECT_ID/panelin/panelin-api:latest \
  --region us-central1 \
  --memory 512Mi \
  --cpu 1 \
  --concurrency 80 \
  --min-instances 0 \
  --max-instances 10 \
  --no-allow-unauthenticated \
  --service-account panelin-api@$PROJECT_ID.iam.gserviceaccount.com \
  --set-secrets "OPENAI_API_KEY=OPENAI_API_KEY:latest" \
  --set-env-vars "ENVIRONMENT=staging,LOG_LEVEL=DEBUG"
```

#### Production:
```bash
gcloud run deploy panelin-api \
  --image us-central1-docker.pkg.dev/$PROJECT_ID/panelin/panelin-api:latest \
  --region us-central1 \
  --memory 1Gi \
  --cpu 2 \
  --concurrency 100 \
  --timeout 60s \
  --min-instances 1 \
  --max-instances 20 \
  --cpu-boost \
  --no-allow-unauthenticated \
  --service-account panelin-api@$PROJECT_ID.iam.gserviceaccount.com \
  --set-secrets "OPENAI_API_KEY=OPENAI_API_KEY:latest,SHOPIFY_API_KEY=SHOPIFY_API_KEY:latest" \
  --set-env-vars "ENVIRONMENT=production,LOG_LEVEL=WARNING"
```

### 7) Health & Readiness Endpoints (IMPLEMENTED)

The `api.py` now includes:

| Endpoint | Purpose | When to Use |
|----------|---------|-------------|
| `/health` | Liveness probe | Is the process running? |
| `/ready` | Readiness probe | Can accept traffic? |
| `/metrics` | Basic metrics | Operational insights |

### 8) Monitoring & Alerting (NEW)

Set up alerts for:
- **Error rate** > 1% over 5 minutes
- **P95 latency** > 1000ms over 5 minutes
- **Instance restarts** > 3 in 10 minutes

See `docs/PRODUCTION_DEPLOYMENT_GUIDE.md` for complete monitoring setup.

### 9) Update OpenAPI Schema for Production
Replace the temporary Localtunnel URL with the Cloud Run URL:

```json
"servers": [
  { "url": "https://panelin-api-xxxxx-uc.a.run.app", "description": "Cloud Run Production" }
]
```

---

## Resource Configuration

| Environment | CPU | Memory | Concurrency | Min Instances | Max Instances | Timeout |
|------------|-----|--------|-------------|---------------|---------------|---------|
| Staging | 1 | 512Mi | 80 | 0 | 10 | 300s |
| Production | 2 | 1Gi | 100 | 1 | 20 | 60s |

---

## Fallback Option (If You Prefer AWS)
- Use **AWS App Runner** (simple) or **ECS Fargate + ALB** (more control).
- The container and OpenAPI steps remain the same.
- AWS App Runner has a similar developer experience to Cloud Run.

---

## Deliverables Checklist

### Core Infrastructure
- [x] `Dockerfile` - Multi-stage build with proper PORT handling
- [x] `.dockerignore` - Comprehensive exclusions
- [x] `api.py` - Production API with health endpoints
- [x] `cloudbuild.yaml` - CI/CD for staging
- [x] `cloudbuild-production.yaml` - CI/CD for production
- [x] `cloudrun-config.yaml` - Resource configuration reference
- [x] `requirements.txt` - Pinned dependency versions

### Security
- [x] Dedicated service account configuration
- [x] Secret Manager integration
- [x] IAM authentication (--no-allow-unauthenticated)
- [ ] Cloud Armor (optional, for rate limiting)

### Observability
- [x] `/health` endpoint (liveness)
- [x] `/ready` endpoint (readiness)
- [x] `/metrics` endpoint (basic metrics)
- [x] Structured logging for Cloud Logging
- [ ] Cloud Monitoring alerts (manual setup required)
- [ ] Cloud Trace integration (optional)

### Deployment
- [ ] Artifact Registry repository created
- [ ] Staging environment deployed
- [ ] Production environment deployed
- [ ] CI/CD triggers configured

---

## Quick Start

1. **Set up GCP project:**
   ```bash
   export PROJECT_ID="your-project-id"
   gcloud config set project $PROJECT_ID
   ```

2. **Create secrets:**
   ```bash
   echo -n "your-key" | gcloud secrets create OPENAI_API_KEY --data-file=-
   ```

3. **Deploy to staging:**
   ```bash
   gcloud builds submit --config=cloudbuild.yaml
   ```

4. **Deploy to production:**
   ```bash
   gcloud builds submit --config=cloudbuild-production.yaml
   ```

---

## Summary

**Best choice:** **Google Cloud Run** for this repo because it is minimal, scalable, and matches the current FastAPI/Uvicorn usage while removing local-tunnel and manual steps.

**Production improvements implemented:**
- ✅ Proper PORT handling in Dockerfile
- ✅ Secret Manager integration
- ✅ Dedicated service account with minimal privileges
- ✅ Health and readiness endpoints
- ✅ Pinned dependency versions
- ✅ Staging/production environment separation
- ✅ Resource limits and scaling configuration
- ✅ Quality gates in CI/CD (lint, test, security scan)

For complete deployment instructions, see: **[PRODUCTION_DEPLOYMENT_GUIDE.md](./PRODUCTION_DEPLOYMENT_GUIDE.md)**
