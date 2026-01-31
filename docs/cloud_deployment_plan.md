# Cloud Deployment Plan - Production Grade

## Best Option: Google Cloud Run + Artifact Registry + Cloud Build

**Why this is the best fit for this repo:**
- **Container-native**: The current deployment script runs a FastAPI/Uvicorn service locally (`api:app`). Cloud Run is optimized for containerized HTTP services and removes server management overhead.
- **Auto-scaling and cost efficiency**: Scales to zero when idle and scales up with traffic.
- **Simplified HTTPS & public URL**: Cloud Run provides a stable HTTPS endpoint that can replace the current Localtunnel URL injection step.
- **Easy CI/CD**: Cloud Build integrates directly with GitHub and Artifact Registry.
- **Secret Management**: Native integration with Secret Manager for secure credential storage.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites Setup](#prerequisites-setup)
3. [Containerization](#containerization)
4. [Security Configuration](#security-configuration)
5. [CI/CD Pipeline](#cicd-pipeline)
6. [Deployment Steps](#deployment-steps)
7. [Monitoring & Observability](#monitoring--observability)
8. [Production Checklist](#production-checklist)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Google Cloud Platform                           │
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐  │
│  │   GitHub     │───▶│  Cloud Build │───▶│   Artifact Registry      │  │
│  │   (Source)   │    │  (CI/CD)     │    │   (Container Images)     │  │
│  └──────────────┘    └──────────────┘    └──────────────────────────┘  │
│                              │                        │                  │
│                              ▼                        ▼                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐  │
│  │   Secret     │───▶│  Cloud Run   │◀───│   Cloud Monitoring       │  │
│  │   Manager    │    │  (Service)   │    │   (Alerts & Dashboards)  │  │
│  └──────────────┘    └──────────────┘    └──────────────────────────┘  │
│                              │                                           │
│                              ▼                                           │
│                    ┌──────────────────┐                                  │
│                    │  Cloud Trace     │                                  │
│                    │  (Distributed    │                                  │
│                    │   Tracing)       │                                  │
│                    └──────────────────┘                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Service Configuration

| Parameter | Staging | Production |
|-----------|---------|------------|
| Min Instances | 0 | 1 |
| Max Instances | 5 | 10 |
| CPU | 1 | 1 |
| Memory | 512Mi | 512Mi |
| Concurrency | 80 | 80 |
| Timeout | 300s | 300s |

---

## Prerequisites Setup

### 1. Enable Required APIs

```bash
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  cloudtrace.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com
```

### 2. Create Service Account (Principle of Least Privilege)

```bash
# Create dedicated service account
gcloud iam service-accounts create panelin-api-sa \
  --display-name="Panelin API Service Account" \
  --description="Dedicated SA for Panelin API Cloud Run service"

export SA_EMAIL="panelin-api-sa@${PROJECT_ID}.iam.gserviceaccount.com"

# Grant minimal required permissions
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/logging.logWriter"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/cloudtrace.agent"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/monitoring.metricWriter"
```

### 3. Create Artifact Registry Repository

```bash
gcloud artifacts repositories create panelin \
  --repository-format=docker \
  --location=us-central1 \
  --description="Panelin API container images"
```

---

## Containerization

### Dockerfile

The Dockerfile is located at `/Dockerfile` with the following key features:

- **Multi-stage build**: Separates build dependencies from runtime
- **Non-root user**: Runs as `appuser` for security
- **Shell form CMD**: Properly expands `${PORT}` variable
- **Health check**: Built-in container health verification

```dockerfile
# Key CMD configuration (shell form for variable expansion)
CMD exec uvicorn api:app --host 0.0.0.0 --port ${PORT} --workers 1 --loop uvloop --http httptools
```

### .dockerignore

The `.dockerignore` file excludes:
- Git files and IDE configurations
- Python artifacts (`__pycache__`, `*.pyc`)
- Test files and coverage reports
- Large data files (JSON, CSV, PDF)
- Documentation (except README)
- Build and cache directories

---

## Security Configuration

### Secret Manager Setup

**Never store secrets in environment variables or code. Use Secret Manager.**

```bash
# Create secrets
gcloud secrets create openai-api-key --replication-policy="automatic"
gcloud secrets create mongodb-uri --replication-policy="automatic"

# Add secret values
echo -n "sk-your-api-key" | gcloud secrets versions add openai-api-key --data-file=-
echo -n "mongodb+srv://..." | gcloud secrets versions add mongodb-uri --data-file=-

# Grant access to service account
gcloud secrets add-iam-policy-binding openai-api-key \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding mongodb-uri \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"
```

### Access Control Options

| Mode | Flag | Use Case |
|------|------|----------|
| Public | `--allow-unauthenticated` | Customer-facing APIs |
| IAM Auth | `--no-allow-unauthenticated` | Internal services |
| IAP | + Load Balancer | User authentication |

**Recommended for internal services:**

```bash
gcloud run deploy panelin-api \
  --no-allow-unauthenticated

# Grant access to specific service accounts
gcloud run services add-iam-policy-binding panelin-api \
  --member="serviceAccount:client@project.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
```

See [SECURITY_PRODUCTION_GUIDE.md](./SECURITY_PRODUCTION_GUIDE.md) for detailed security configuration.

---

## CI/CD Pipeline

### Cloud Build Configuration

The `cloudbuild.yaml` includes:

1. **Linting & Static Analysis** - Code quality checks
2. **Unit Tests** - Automated testing before deploy
3. **Docker Build** - Multi-tag image building with cache
4. **Security Scan** - Container vulnerability scanning
5. **Deploy** - Cloud Run deployment with full configuration
6. **Verify** - Post-deployment health checks

### Trigger Setup

```bash
# Create GitHub trigger for main branch (production)
gcloud builds triggers create github \
  --repo-name="your-repo" \
  --repo-owner="your-org" \
  --branch-pattern="^main$" \
  --build-config="cloudbuild.yaml" \
  --substitutions="_ENV=production,_MIN_INSTANCES=1"

# Create trigger for develop branch (staging)
gcloud builds triggers create github \
  --repo-name="your-repo" \
  --repo-owner="your-org" \
  --branch-pattern="^develop$" \
  --build-config="cloudbuild.yaml" \
  --substitutions="_ENV=staging,_MIN_INSTANCES=0"
```

---

## Deployment Steps

### Option A: First-Time Manual Deploy

```bash
# Build and push image
docker build -t us-central1-docker.pkg.dev/${PROJECT_ID}/panelin/panelin-api:v1 .
docker push us-central1-docker.pkg.dev/${PROJECT_ID}/panelin/panelin-api:v1

# Deploy to Cloud Run
gcloud run deploy panelin-api \
  --image=us-central1-docker.pkg.dev/${PROJECT_ID}/panelin/panelin-api:v1 \
  --region=us-central1 \
  --platform=managed \
  --memory=512Mi \
  --cpu=1 \
  --concurrency=80 \
  --timeout=300s \
  --min-instances=0 \
  --max-instances=10 \
  --service-account=${SA_EMAIL} \
  --set-secrets="OPENAI_API_KEY=openai-api-key:latest,MONGODB_URI=mongodb-uri:latest" \
  --allow-unauthenticated
```

### Option B: Using Service YAML

```bash
# Deploy using the declarative service configuration
gcloud run services replace cloudrun-service.yaml --region=us-central1
```

### Option C: Source Deploy (Simplest)

```bash
gcloud run deploy panelin-api \
  --source . \
  --region=us-central1
```

---

## Monitoring & Observability

### Health Endpoints

The API provides three health-related endpoints:

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `/` | Basic info | Service name, version, uptime |
| `/health` | Liveness probe | Quick health check |
| `/ready` | Readiness probe | Validates dependencies |

### Alert Policies

Configured alerts in `monitoring/alert-policies.yaml`:

1. **High Error Rate** - Error rate > 5%
2. **High Latency** - P95 latency > 2000ms
3. **Container Restarts** - Frequent container crashes
4. **Cold Start Rate** - Excessive cold starts
5. **Memory Usage** - Memory > 80%
6. **Traffic Anomaly** - Unusual request volume

### Deploy Alerts

```bash
# Create alert policies
gcloud alpha monitoring policies create \
  --policy-from-file=monitoring/alert-policies.yaml
```

### Create Notification Channel

```bash
# Email notification
gcloud alpha monitoring channels create \
  --display-name="Panelin Ops Team" \
  --type=email \
  --channel-labels="email_address=ops@company.com"

# Slack notification
gcloud alpha monitoring channels create \
  --display-name="Panelin Alerts Slack" \
  --type=slack \
  --channel-labels="channel_name=#panelin-alerts"
```

See [monitoring/observability-setup.md](../monitoring/observability-setup.md) for detailed observability configuration.

---

## Production Checklist

### Before Deployment

- [ ] **Dockerfile** uses shell form CMD for `${PORT}` expansion
- [ ] **Service Account** created with minimal permissions
- [ ] **Secrets** stored in Secret Manager (not env vars)
- [ ] **Health endpoints** `/health` and `/ready` implemented
- [ ] **Requirements pinned** with exact versions
- [ ] **.dockerignore** excludes large/sensitive files
- [ ] **Tests** pass in CI pipeline

### Security

- [ ] Access control configured (IAM or public with rate limiting)
- [ ] Secret Manager integrated for all credentials
- [ ] Container runs as non-root user
- [ ] Dependencies scanned for vulnerabilities

### Observability

- [ ] Structured logging configured
- [ ] Alert policies created
- [ ] Dashboard available
- [ ] Traces enabled for debugging

### Operations

- [ ] Autoscaling configured (min/max instances)
- [ ] Resource limits set (CPU/memory)
- [ ] Timeouts configured appropriately
- [ ] Rollback procedure documented

---

## Quick Reference Commands

```bash
# View service status
gcloud run services describe panelin-api --region=us-central1

# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=panelin-api" --limit=50

# Get service URL
gcloud run services describe panelin-api --region=us-central1 --format="value(status.url)"

# View recent revisions
gcloud run revisions list --service=panelin-api --region=us-central1

# Rollback to previous revision
gcloud run services update-traffic panelin-api \
  --to-revisions=panelin-api-00001-abc=100 \
  --region=us-central1

# Check secrets
gcloud secrets list --filter="labels.app=panelin-api"

# View alert policies
gcloud alpha monitoring policies list --filter="displayName:panelin"
```

---

## Related Documentation

- [Security & Production Guide](./SECURITY_PRODUCTION_GUIDE.md)
- [Observability Setup](../monitoring/observability-setup.md)
- [Alert Policies](../monitoring/alert-policies.yaml)
- [Cloud Run Service Config](../cloudrun-service.yaml)
