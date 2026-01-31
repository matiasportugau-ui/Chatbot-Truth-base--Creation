# Production Deployment Guide - Panelin API

## Overview

This guide covers the complete production deployment of the Panelin API to Google Cloud Run, including security hardening, observability, CI/CD, and operational best practices.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Google Cloud Platform                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐     ┌─────────────────┐     ┌──────────────────────┐  │
│  │   GitHub     │────▶│  Cloud Build    │────▶│  Artifact Registry   │  │
│  │  (Source)    │     │  (CI/CD)        │     │  (Container Images)  │  │
│  └──────────────┘     └─────────────────┘     └──────────────────────┘  │
│                              │                          │                │
│                              ▼                          ▼                │
│  ┌──────────────┐     ┌─────────────────┐     ┌──────────────────────┐  │
│  │   Secret     │◀───▶│   Cloud Run     │◀───▶│  Cloud Monitoring    │  │
│  │   Manager    │     │  (Staging/Prod) │     │  (Alerts/Dashboards) │  │
│  └──────────────┘     └─────────────────┘     └──────────────────────┘  │
│                              │                                           │
│                              ▼                                           │
│                       ┌─────────────────┐                               │
│                       │  Cloud Trace    │                               │
│                       │  (Distributed   │                               │
│                       │   Tracing)      │                               │
│                       └─────────────────┘                               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Google Cloud project with billing enabled
- `gcloud` CLI installed and authenticated
- GitHub repository connected to Cloud Build
- Required APIs enabled:
  ```bash
  gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    monitoring.googleapis.com \
    cloudtrace.googleapis.com
  ```

## Quick Start

```bash
# 1. Set environment variables
export PROJECT_ID=your-project-id
export REGION=us-central1

# 2. Setup secrets and IAM
chmod +x scripts/setup_secrets.sh
./scripts/setup_secrets.sh

# 3. Add secret values
echo -n 'sk-your-openai-key' | gcloud secrets versions add openai-api-key --data-file=-

# 4. Deploy to Cloud Run
gcloud run deploy panelin-api \
  --source . \
  --region $REGION \
  --service-account panelin-api-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --set-secrets 'OPENAI_API_KEY=openai-api-key:latest'
```

---

## 1. Security Configuration

### 1.1 Service Account (Principle of Least Privilege)

Create a dedicated service account with minimal permissions:

```bash
# Create service account
gcloud iam service-accounts create panelin-api-sa \
  --display-name="Panelin API Service Account"

# Grant only required roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:panelin-api-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:panelin-api-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudtrace.agent"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:panelin-api-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/logging.logWriter"
```

### 1.2 Secret Manager Integration

Store secrets securely using Secret Manager:

```bash
# Create secrets
gcloud secrets create openai-api-key --replication-policy="automatic"
gcloud secrets create mongodb-uri --replication-policy="automatic"

# Add secret versions
echo -n 'your-api-key' | gcloud secrets versions add openai-api-key --data-file=-

# Grant access to service account
gcloud secrets add-iam-policy-binding openai-api-key \
  --member="serviceAccount:panelin-api-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

Deploy with secrets:
```bash
gcloud run deploy panelin-api \
  --set-secrets='OPENAI_API_KEY=openai-api-key:latest,MONGODB_URI=mongodb-uri:latest'
```

### 1.3 Access Control Options

#### Option A: Public API (Current)
```bash
gcloud run deploy panelin-api --allow-unauthenticated
```

#### Option B: IAM-Authenticated (Recommended for Internal)
```bash
gcloud run deploy panelin-api --no-allow-unauthenticated

# Grant specific users/services access
gcloud run services add-iam-policy-binding panelin-api \
  --member="user:developer@example.com" \
  --role="roles/run.invoker"
```

#### Option C: API Gateway with API Keys
For public APIs that need rate limiting and API keys, use API Gateway:
```yaml
# api-gateway-config.yaml
swagger: '2.0'
info:
  title: Panelin API Gateway
  version: 1.0.0
host: panelin-api-gateway.endpoints.PROJECT_ID.cloud.goog
x-google-backend:
  address: https://panelin-api-xxxxx-uc.a.run.app
security:
  - api_key: []
securityDefinitions:
  api_key:
    type: apiKey
    name: x-api-key
    in: header
```

---

## 2. Dockerfile Configuration

The production Dockerfile (`/Dockerfile`) includes:

- **Multi-stage build** for smaller image size
- **Non-root user** for security
- **Proper PORT handling** using shell form CMD
- **Health checks** built-in

Key points:
```dockerfile
# CORRECT: Shell form expands $PORT
CMD exec uvicorn api:app --host 0.0.0.0 --port $PORT

# WRONG: JSON form does NOT expand variables
# CMD ["uvicorn", "api:app", "--port", "${PORT}"]
```

---

## 3. Cloud Run Configuration

### 3.1 Resource Limits

Configure resources in `cloudrun-service.yaml`:

| Environment | CPU | Memory | Min Instances | Max Instances | Concurrency |
|-------------|-----|--------|---------------|---------------|-------------|
| Staging     | 1   | 512Mi  | 0             | 10            | 80          |
| Production  | 2   | 1Gi    | 1             | 100           | 80          |

### 3.2 Deploy with Configuration

```bash
# Apply full service configuration
gcloud run services replace cloudrun-service.yaml

# Or deploy with inline options
gcloud run deploy panelin-api \
  --memory 1Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 100 \
  --concurrency 80 \
  --timeout 300s \
  --cpu-boost
```

### 3.3 Health Probes

The API exposes three health endpoints:

| Endpoint   | Purpose              | Cloud Run Usage |
|------------|----------------------|-----------------|
| `/health`  | Overall health       | Startup probe   |
| `/ready`   | Dependency readiness | Readiness probe |
| `/live`    | Process alive check  | Liveness probe  |

---

## 4. CI/CD Pipeline

### 4.1 Pipeline Overview

The `cloudbuild.yaml` implements:

1. **Lint** - Code quality checks (black, isort)
2. **Test** - Unit tests with coverage
3. **Build** - Multi-stage Docker build
4. **Push** - Image to Artifact Registry
5. **Deploy Staging** - Automatic on main branch
6. **Smoke Tests** - Validate staging deployment
7. **Deploy Production** - Manual via version tags

### 4.2 Deployment Strategy

| Trigger | Action |
|---------|--------|
| PR opened | Run lint + tests only |
| Push to main | Deploy to staging |
| Tag v*.*.* | Deploy to production |

### 4.3 Setup Cloud Build Trigger

```bash
# Create trigger for main branch
gcloud builds triggers create github \
  --repo-name=panelin \
  --repo-owner=your-org \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml

# Create trigger for version tags
gcloud builds triggers create github \
  --repo-name=panelin \
  --repo-owner=your-org \
  --tag-pattern="^v[0-9]+\.[0-9]+\.[0-9]+$" \
  --build-config=cloudbuild.yaml
```

### 4.4 Production Release Process

```bash
# 1. Create version tag
git tag -a v1.2.3 -m "Release 1.2.3: Feature X, Bug Y fixed"

# 2. Push tag to trigger production deploy
git push origin v1.2.3

# 3. Monitor deployment in Cloud Build console
```

---

## 5. Observability

### 5.1 Structured Logging

Logs are JSON-formatted for Cloud Logging:

```json
{
  "timestamp": "2026-01-31T10:00:00Z",
  "level": "INFO",
  "message": "Request completed",
  "httpRequest": {
    "requestMethod": "POST",
    "requestUrl": "/quotes",
    "status": 200,
    "latency": "125.5ms"
  }
}
```

View logs:
```bash
gcloud run logs read panelin-api --region=us-central1 --limit=100
```

### 5.2 Alerting Policies

The `monitoring/alerting-policies.yaml` defines alerts for:

| Alert | Condition | Severity |
|-------|-----------|----------|
| High Error Rate | >5% errors over 5 min | Critical |
| High Latency | P95 >2s over 5 min | Warning |
| Cold Starts | >10/hour | Info |
| Container Restarts | >3 in 10 min | Critical |
| Memory Usage | >80% | Warning |
| 5xx Errors | Any occurrence | Critical |

Setup:
```bash
chmod +x monitoring/setup_monitoring.sh
./monitoring/setup_monitoring.sh
```

### 5.3 Dashboard

A pre-configured dashboard (`monitoring/setup_monitoring.sh`) includes:

- Request count by response code
- Latency percentiles (P50, P95, P99)
- Instance count
- CPU/Memory utilization
- Cold start frequency

---

## 6. Operations

### 6.1 Rollback

```bash
# List revisions
gcloud run revisions list --service=panelin-api --region=us-central1

# Rollback to specific revision
gcloud run services update-traffic panelin-api \
  --region=us-central1 \
  --to-revisions=panelin-api-00005-abc=100
```

### 6.2 Canary Deployments

```bash
# Route 10% to new version
gcloud run services update-traffic panelin-api \
  --region=us-central1 \
  --to-revisions=panelin-api-00010-new=10,panelin-api-00009-stable=90

# Gradually increase to 100%
gcloud run services update-traffic panelin-api \
  --region=us-central1 \
  --to-latest
```

### 6.3 Debug Live Instance

```bash
# Tail logs
gcloud run logs tail panelin-api --region=us-central1

# View in Cloud Console
open https://console.cloud.google.com/run/detail/us-central1/panelin-api/logs
```

---

## 7. Cost Optimization

### 7.1 Recommendations

| Setting | Cost Impact | When to Use |
|---------|-------------|-------------|
| `min-instances=0` | Lower cost | Staging, low-traffic |
| `min-instances=1` | Higher cost, better latency | Production |
| `cpu-throttling=true` | Lower cost | Request-based workloads |
| `cpu-boost` | Slight increase | Reduce cold start latency |

### 7.2 Estimated Costs

For a typical workload (10K requests/day, 200ms avg latency):

| Component | Monthly Cost |
|-----------|--------------|
| Cloud Run (1 min instance) | ~$30-50 |
| Secret Manager | <$1 |
| Cloud Monitoring | Free tier |
| Artifact Registry | ~$5 |
| **Total** | **~$40-60/month** |

---

## 8. Checklist

### Pre-Deployment
- [ ] All tests passing locally
- [ ] Environment variables documented
- [ ] Secrets created in Secret Manager
- [ ] Service account configured with minimal permissions
- [ ] .dockerignore excludes large files

### Deployment
- [ ] Image builds successfully
- [ ] Staging deployment works
- [ ] /health and /ready endpoints respond
- [ ] Smoke tests pass

### Post-Deployment
- [ ] Alerting policies configured
- [ ] Dashboard created
- [ ] Runbook documented
- [ ] Rollback tested

---

## File Reference

| File | Purpose |
|------|---------|
| `Dockerfile` | Production container image |
| `.dockerignore` | Build exclusions |
| `cloudbuild.yaml` | CI/CD pipeline |
| `cloudrun-service.yaml` | Service configuration |
| `api.py` | Production API with health checks |
| `requirements-production.txt` | Pinned dependencies |
| `scripts/setup_secrets.sh` | Secret Manager setup |
| `monitoring/alerting-policies.yaml` | Alert definitions |
| `monitoring/setup_monitoring.sh` | Monitoring setup |

---

## Support

For issues:
1. Check logs: `gcloud run logs read panelin-api`
2. Review alerts in Cloud Monitoring
3. Check service status: `gcloud run services describe panelin-api`
