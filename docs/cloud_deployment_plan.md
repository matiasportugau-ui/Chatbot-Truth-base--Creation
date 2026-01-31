# Cloud Deployment Recommendation & Implementation Plan

> **📚 For complete production deployment, see [PRODUCTION_DEPLOYMENT_GUIDE.md](./PRODUCTION_DEPLOYMENT_GUIDE.md)**

## Best Option: Google Cloud Run + Artifact Registry + Cloud Build

**Why this is the best fit for this repo**
- **Container-native**: The current deployment script runs a FastAPI/Uvicorn service locally (`api:app`). Cloud Run is optimized for containerized HTTP services and removes server management overhead.
- **Auto-scaling and cost efficiency**: Scales to zero when idle and scales up with traffic.
- **Simplified HTTPS & public URL**: Cloud Run provides a stable HTTPS endpoint that can replace the current Localtunnel URL injection step.
- **Easy CI/CD**: Cloud Build integrates directly with GitHub and Artifact Registry.

## Production-Ready Files (Updated)

The following files have been created/updated for production deployment:

| File | Purpose |
|------|---------|
| `/Dockerfile` | Multi-stage build with proper PORT handling |
| `/.dockerignore` | Comprehensive exclusions for faster builds |
| `/cloudbuild.yaml` | CI/CD with staging/production, tests, quality gates |
| `/cloudrun-service.yaml` | Full service configuration with resources, probes |
| `/api.py` | Production API with /health, /ready, /live endpoints |
| `/requirements-production.txt` | Pinned versions for reproducibility |
| `/scripts/setup_secrets.sh` | Secret Manager and IAM setup |
| `/monitoring/alerting-policies.yaml` | Cloud Monitoring alerts |
| `/monitoring/setup_monitoring.sh` | Dashboard and alerting setup |

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

> ⚠️ **IMPORTANT FIX**: The original CMD used JSON form which does NOT expand `${PORT}`.
> The production Dockerfile uses shell form: `CMD exec uvicorn ... --port $PORT`

The production `Dockerfile` in the repo root includes:

```Dockerfile
# Multi-stage build for smaller image
FROM python:3.11-slim as builder
# ... dependency installation ...

FROM python:3.11-slim as production
# Run as non-root user for security
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
USER appuser

# CORRECT: Shell form properly expands $PORT
CMD exec uvicorn api:app --host 0.0.0.0 --port $PORT --workers 1
```

See `/Dockerfile` for the complete implementation with:
- Multi-stage build for smaller images
- Non-root user for security
- Proper PORT environment variable handling
- Health check configuration

### 2) Add a `.dockerignore`
Avoid shipping large files (e.g., training data, analysis outputs).

### 3) Create a Cloud Build config

The production `cloudbuild.yaml` includes a full CI/CD pipeline:

```yaml
# Simplified overview - see /cloudbuild.yaml for full implementation
steps:
  # 1. Lint - Code quality checks
  - name: 'python:3.11-slim'
    id: 'lint'
    # Runs black, isort checks

  # 2. Test - Unit tests with coverage
  - name: 'python:3.11-slim'
    id: 'test'
    # Runs pytest

  # 3. Build - Docker image with caching
  - name: 'gcr.io/cloud-builders/docker'
    id: 'build'

  # 4. Push - To Artifact Registry
  - name: 'gcr.io/cloud-builders/docker'
    id: 'push'

  # 5. Deploy Staging - On main branch push
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    id: 'deploy-staging'
    # Includes resource limits, secrets, health probes

  # 6. Smoke Tests - Validate staging
  - name: 'gcr.io/cloud-builders/curl'
    id: 'smoke-test-staging'

  # 7. Deploy Production - On version tag (v*.*.*)
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    id: 'deploy-production'
    # --no-allow-unauthenticated for production
```

Key improvements:
- **Quality gates**: Lint and test before deploy
- **Staging/Production environments**: Separate configurations
- **Smoke tests**: Validate deployment before production
- **Version tagging**: Production deploys on `v*.*.*` tags

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

### Core Files (Completed ✅)
- [x] `Dockerfile` - Multi-stage build with proper PORT handling
- [x] `.dockerignore` - Comprehensive exclusions
- [x] `cloudbuild.yaml` - Full CI/CD pipeline with quality gates
- [x] `cloudrun-service.yaml` - Resource limits, scaling, health probes
- [x] `api.py` - Production API with `/health`, `/ready`, `/live` endpoints
- [x] `requirements-production.txt` - Pinned dependency versions

### Security (Completed ✅)
- [x] `scripts/setup_secrets.sh` - Secret Manager setup
- [x] Service account with minimal permissions
- [x] IAM configuration for least privilege
- [x] Secret injection via Cloud Run

### Observability (Completed ✅)
- [x] `monitoring/alerting-policies.yaml` - 7 production alerts
- [x] `monitoring/setup_monitoring.sh` - Dashboard and uptime checks
- [x] Structured JSON logging for Cloud Logging
- [x] Request tracing with Cloud Trace headers

### Deployment Tasks (Manual)
- [ ] Create Artifact Registry repository
- [ ] Add secret values to Secret Manager
- [ ] Deploy Cloud Run service
- [ ] Configure Cloud Build triggers
- [ ] Update OpenAPI schema with Cloud Run URL
- [ ] Verify alerting policies

---

## Summary
**Best choice:** **Google Cloud Run** for this repo because it is minimal, scalable, and matches the current FastAPI/Uvicorn usage while removing local-tunnel and manual steps.
