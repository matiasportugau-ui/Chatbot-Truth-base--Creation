# Panelin API - Production Deployment Guide

This guide covers deploying the Panelin API to Google Cloud Run with production-grade configurations.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Quick Start](#quick-start)
4. [Detailed Setup](#detailed-setup)
5. [Configuration Reference](#configuration-reference)
6. [Security Considerations](#security-considerations)
7. [Monitoring & Alerting](#monitoring--alerting)
8. [Troubleshooting](#troubleshooting)
9. [Maintenance](#maintenance)

---

## Prerequisites

### Required Tools

```bash
# Google Cloud SDK
gcloud --version  # >= 450.0.0

# Docker (for local testing)
docker --version  # >= 24.0.0

# Python (for local development)
python --version  # >= 3.11
```

### GCP Permissions

The deploying user/service account needs:

- `roles/run.admin` - Cloud Run administration
- `roles/artifactregistry.admin` - Artifact Registry management
- `roles/secretmanager.admin` - Secret Manager setup
- `roles/iam.serviceAccountAdmin` - Service account creation
- `roles/cloudbuild.builds.editor` - Cloud Build execution

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Google Cloud                              │
│                                                                   │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │   Client    │───▶│ Cloud Run   │───▶│  Secret Manager     │  │
│  │  (Browser/  │    │ panelin-api │    │  - openai-api-key   │  │
│  │   Mobile)   │    │             │    │  - mongodb-uri      │  │
│  └─────────────┘    └──────┬──────┘    └─────────────────────┘  │
│                            │                                      │
│                            ▼                                      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │   Cloud     │◀───│   Cloud     │    │  Artifact Registry  │  │
│  │  Logging    │    │   Trace     │    │  panelin-api:latest │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Cloud Monitoring                          │ │
│  │  - Error rate alerts    - Latency alerts                     │ │
│  │  - CPU/Memory alerts    - Cold start monitoring              │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### 1. Initial Setup (One-time)

```bash
# Set your project
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"

# Run the setup script
chmod +x deploy/secret-manager-setup.sh
./deploy/secret-manager-setup.sh $PROJECT_ID $REGION
```

### 2. Add Secrets

```bash
# Add OpenAI API key
echo -n "sk-your-openai-api-key" | \
  gcloud secrets versions add openai-api-key --data-file=- --project=$PROJECT_ID

# Add MongoDB URI
echo -n "mongodb+srv://user:password@cluster.mongodb.net/panelin" | \
  gcloud secrets versions add mongodb-uri --data-file=- --project=$PROJECT_ID
```

### 3. Deploy

```bash
# Build and deploy using Cloud Build
gcloud builds submit --config=deploy/cloudbuild.yaml \
  --substitutions=_PROJECT_ID=$PROJECT_ID,_REGION=$REGION,_ENV=production \
  --project=$PROJECT_ID
```

### 4. Verify

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe panelin-api \
  --region=$REGION --project=$PROJECT_ID --format='value(status.url)')

# Test health endpoint
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  "$SERVICE_URL/health"
```

---

## Detailed Setup

### Step 1: Enable APIs

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  monitoring.googleapis.com \
  cloudtrace.googleapis.com \
  --project=$PROJECT_ID
```

### Step 2: Create Service Account

```bash
# Create dedicated service account
gcloud iam service-accounts create panelin-api \
  --display-name="Panelin API Service Account" \
  --project=$PROJECT_ID

# Grant necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:panelin-api@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:panelin-api@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudtrace.agent"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:panelin-api@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/monitoring.metricWriter"
```

### Step 3: Create Artifact Registry

```bash
gcloud artifacts repositories create panelin \
  --repository-format=docker \
  --location=$REGION \
  --project=$PROJECT_ID
```

### Step 4: Configure Secrets

```bash
# Create secrets (empty initially)
for SECRET in openai-api-key mongodb-uri; do
  gcloud secrets create $SECRET \
    --replication-policy="user-managed" \
    --locations=$REGION \
    --project=$PROJECT_ID
done

# Add secret values
echo -n "your-api-key" | gcloud secrets versions add openai-api-key --data-file=-
echo -n "mongodb+srv://..." | gcloud secrets versions add mongodb-uri --data-file=-
```

### Step 5: Build & Deploy

```bash
# Option A: Using Cloud Build (recommended)
gcloud builds submit --config=deploy/cloudbuild.yaml --project=$PROJECT_ID

# Option B: Manual build and deploy
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/panelin/panelin-api:latest \
  -f deploy/Dockerfile .

docker push $REGION-docker.pkg.dev/$PROJECT_ID/panelin/panelin-api:latest

gcloud run deploy panelin-api \
  --image=$REGION-docker.pkg.dev/$PROJECT_ID/panelin/panelin-api:latest \
  --region=$REGION \
  --project=$PROJECT_ID \
  --service-account=panelin-api@$PROJECT_ID.iam.gserviceaccount.com \
  --set-secrets="OPENAI_API_KEY=openai-api-key:latest,MONGODB_URI=mongodb-uri:latest" \
  --memory=512Mi \
  --cpu=1 \
  --timeout=300 \
  --concurrency=80 \
  --min-instances=0 \
  --max-instances=10 \
  --no-allow-unauthenticated
```

---

## Configuration Reference

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PORT` | HTTP port (set by Cloud Run) | 8080 | Auto |
| `APP_ENV` | Environment (development/staging/production) | development | Yes |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | INFO | No |
| `WORKERS` | Uvicorn worker count | 1 | No |
| `WORKER_TIMEOUT` | Worker timeout in seconds | 120 | No |
| `ENABLE_TRACING` | Enable Cloud Trace | false | No |
| `ENABLE_METRICS` | Enable custom metrics | true | No |

### Secrets (via Secret Manager)

| Secret Name | Description |
|-------------|-------------|
| `openai-api-key` | OpenAI API key for LLM |
| `mongodb-uri` | MongoDB connection string |
| `google-sheets-credentials` | Google Sheets service account JSON |

### Resource Limits

| Resource | Development | Staging | Production |
|----------|-------------|---------|------------|
| CPU | 1 | 1 | 1-2 |
| Memory | 256Mi | 512Mi | 512Mi-1Gi |
| Concurrency | 40 | 80 | 80 |
| Min Instances | 0 | 0 | 1 |
| Max Instances | 2 | 5 | 10 |
| Timeout | 60s | 300s | 300s |

---

## Security Considerations

### Authentication Options

#### Option 1: IAM-based (Recommended for internal services)

```bash
# Require IAM authentication
gcloud run services update panelin-api \
  --no-allow-unauthenticated \
  --region=$REGION

# Grant access to specific service accounts
gcloud run services add-iam-policy-binding panelin-api \
  --member="serviceAccount:client@other-project.iam.gserviceaccount.com" \
  --role="roles/run.invoker" \
  --region=$REGION
```

#### Option 2: Public with API Gateway

```bash
# Allow public access
gcloud run services add-iam-policy-binding panelin-api \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --region=$REGION

# Add Cloud Armor for rate limiting/WAF
# Configure API Gateway for key-based auth
```

### Secret Rotation

```bash
# Add new secret version
echo -n "new-api-key" | gcloud secrets versions add openai-api-key --data-file=-

# Cloud Run automatically picks up latest version on next cold start
# Force refresh by deploying new revision:
gcloud run services update panelin-api --region=$REGION
```

### Network Security

```yaml
# In cloudrun-service.yaml, add VPC connector for private resources:
annotations:
  run.googleapis.com/vpc-access-connector: projects/PROJECT_ID/locations/REGION/connectors/panelin-vpc
  run.googleapis.com/vpc-access-egress: private-ranges-only
```

---

## Monitoring & Alerting

### Deploy Alerting Policies

```bash
# Create alerting policies from YAML
# Note: This requires manual import in Cloud Console or Terraform

# Via gcloud (limited support):
gcloud alpha monitoring policies create \
  --policy-from-file=deploy/monitoring-alerts.yaml \
  --project=$PROJECT_ID
```

### Key Metrics to Monitor

| Metric | Threshold | Action |
|--------|-----------|--------|
| Error Rate | > 5% for 5 min | Investigate logs, consider rollback |
| P95 Latency | > 2000ms | Check traces, optimize queries |
| CPU Utilization | > 80% | Scale up or optimize code |
| Memory Utilization | > 85% | Increase memory or fix leaks |
| Cold Start Rate | > 20% | Increase min-instances |

### Logging

```bash
# View recent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=panelin-api" \
  --limit=50 --project=$PROJECT_ID

# Stream logs
gcloud run services logs tail panelin-api --region=$REGION --project=$PROJECT_ID
```

### Tracing

Enable Cloud Trace for distributed tracing:

1. Set `ENABLE_TRACING=true` in environment variables
2. Install OpenTelemetry packages (uncomment in requirements-prod.txt)
3. View traces in Cloud Console → Trace

---

## Troubleshooting

### Common Issues

#### Container fails to start

```bash
# Check container logs
gcloud run services logs read panelin-api --region=$REGION --limit=100

# Common causes:
# - Missing environment variables
# - Secret access denied
# - Port binding issues
# - Import errors
```

#### Health check failures

```bash
# Verify health endpoint locally
docker run -p 8080:8080 -e PORT=8080 panelin-api:latest
curl http://localhost:8080/health

# Check Cloud Run health check config
gcloud run services describe panelin-api --region=$REGION --format=yaml
```

#### Secret access denied

```bash
# Verify service account has secretAccessor role
gcloud secrets get-iam-policy openai-api-key --project=$PROJECT_ID

# Grant if missing
gcloud secrets add-iam-policy-binding openai-api-key \
  --member="serviceAccount:panelin-api@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

#### High latency / cold starts

```bash
# Set minimum instances to avoid cold starts
gcloud run services update panelin-api \
  --min-instances=1 \
  --region=$REGION

# Enable startup CPU boost
gcloud run services update panelin-api \
  --cpu-boost \
  --region=$REGION
```

---

## Maintenance

### Updating the Service

```bash
# Deploy new version
gcloud builds submit --config=deploy/cloudbuild.yaml

# Rollback to previous revision
gcloud run services update-traffic panelin-api \
  --to-revisions=REVISION_NAME=100 \
  --region=$REGION
```

### Rotating Secrets

```bash
# 1. Add new secret version
echo -n "new-key" | gcloud secrets versions add openai-api-key --data-file=-

# 2. Deploy new revision (picks up latest secret)
gcloud run services update panelin-api --region=$REGION

# 3. Disable old secret version after verification
gcloud secrets versions disable VERSION_ID --secret=openai-api-key
```

### Scaling Configuration

```bash
# Update autoscaling
gcloud run services update panelin-api \
  --min-instances=1 \
  --max-instances=20 \
  --concurrency=100 \
  --region=$REGION
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `deploy/Dockerfile` | Multi-stage production Dockerfile |
| `deploy/.dockerignore` | Files to exclude from Docker build |
| `deploy/cloudbuild.yaml` | Cloud Build CI/CD configuration |
| `deploy/cloudrun-service.yaml` | Cloud Run service manifest |
| `deploy/secret-manager-setup.sh` | Initial setup script |
| `deploy/monitoring-alerts.yaml` | Alerting policy definitions |
| `requirements-prod.txt` | Pinned production dependencies |
| `api.py` | Production API with health endpoints |

---

## Support

For issues or questions:

1. Check [Troubleshooting](#troubleshooting) section
2. Review Cloud Logging for errors
3. Contact engineering team

---

*Last updated: 2026-01-31*
*Version: 2.0.0*
