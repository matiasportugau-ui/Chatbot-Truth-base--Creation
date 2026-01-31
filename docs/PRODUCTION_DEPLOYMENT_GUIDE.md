# Production Deployment Guide for Panelin API

## Overview

This guide provides comprehensive instructions for deploying the Panelin Agent V2 API to Google Cloud Run with production-grade security, observability, and reliability.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Security Setup](#security-setup)
3. [Secret Manager Configuration](#secret-manager-configuration)
4. [Deployment Steps](#deployment-steps)
5. [Health Checks](#health-checks)
6. [Monitoring & Alerting](#monitoring--alerting)
7. [CI/CD Pipeline](#cicd-pipeline)
8. [Rollback Procedures](#rollback-procedures)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Install Docker
# See: https://docs.docker.com/get-docker/
```

### GCP Project Setup

```bash
# Set project
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  cloudtrace.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com
```

---

## Security Setup

### 1. Create Dedicated Service Account

```bash
# Create service account
gcloud iam service-accounts create panelin-api \
  --display-name="Panelin API Service Account" \
  --description="Dedicated service account for Panelin API with minimal privileges"

# Grant necessary roles (principle of least privilege)
SA_EMAIL="panelin-api@${PROJECT_ID}.iam.gserviceaccount.com"

# Secret Manager access
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"

# Cloud Trace
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/cloudtrace.agent"

# Cloud Logging
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/logging.logWriter"

# Cloud Monitoring
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/monitoring.metricWriter"
```

### 2. Configure Authentication

For **internal/private APIs**:
```bash
# Require authentication (default in our config)
gcloud run deploy panelin-api --no-allow-unauthenticated
```

For **public APIs** (if needed):
```bash
# Allow public access
gcloud run deploy panelin-api --allow-unauthenticated
```

### 3. Optional: Cloud Armor (WAF)

For rate limiting and IP restrictions:

```bash
# Create security policy
gcloud compute security-policies create panelin-api-policy \
  --description="Security policy for Panelin API"

# Add rate limiting rule
gcloud compute security-policies rules create 1000 \
  --security-policy=panelin-api-policy \
  --action=throttle \
  --rate-limit-threshold-count=100 \
  --rate-limit-threshold-interval-sec=60 \
  --conform-action=allow \
  --exceed-action=deny-429
```

---

## Secret Manager Configuration

### Create Secrets

```bash
# Create secrets (replace with actual values)
echo -n "sk-your-openai-key" | gcloud secrets create OPENAI_API_KEY --data-file=-
echo -n "shpat_your-shopify-key" | gcloud secrets create SHOPIFY_API_KEY --data-file=-

# Add more secrets as needed
# echo -n "mongodb://..." | gcloud secrets create MONGODB_URI --data-file=-
```

### Secret Rotation

```bash
# Add a new version (for rotation)
echo -n "sk-new-openai-key" | gcloud secrets versions add OPENAI_API_KEY --data-file=-

# Disable old version
gcloud secrets versions disable OLD_VERSION --secret=OPENAI_API_KEY

# The service will automatically use :latest
```

### Grant Access to Service Account

```bash
# Grant access to secrets
gcloud secrets add-iam-policy-binding OPENAI_API_KEY \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding SHOPIFY_API_KEY \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"
```

---

## Deployment Steps

### 1. Create Artifact Registry Repository

```bash
gcloud artifacts repositories create panelin \
  --repository-format=docker \
  --location=us-central1 \
  --description="Panelin API container images"
```

### 2. Build and Push Image

```bash
# Configure Docker authentication
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build image
docker build -t us-central1-docker.pkg.dev/${PROJECT_ID}/panelin/panelin-api:latest .

# Push image
docker push us-central1-docker.pkg.dev/${PROJECT_ID}/panelin/panelin-api:latest
```

### 3. Deploy to Cloud Run

#### Staging Deployment

```bash
gcloud run deploy panelin-api-staging \
  --image us-central1-docker.pkg.dev/${PROJECT_ID}/panelin/panelin-api:latest \
  --region us-central1 \
  --platform managed \
  --memory 512Mi \
  --cpu 1 \
  --concurrency 80 \
  --timeout 300s \
  --min-instances 0 \
  --max-instances 10 \
  --no-allow-unauthenticated \
  --service-account panelin-api@${PROJECT_ID}.iam.gserviceaccount.com \
  --set-secrets "OPENAI_API_KEY=OPENAI_API_KEY:latest,SHOPIFY_API_KEY=SHOPIFY_API_KEY:latest" \
  --set-env-vars "ENVIRONMENT=staging,LOG_LEVEL=DEBUG"
```

#### Production Deployment

```bash
gcloud run deploy panelin-api \
  --image us-central1-docker.pkg.dev/${PROJECT_ID}/panelin/panelin-api:latest \
  --region us-central1 \
  --platform managed \
  --memory 1Gi \
  --cpu 2 \
  --concurrency 100 \
  --timeout 60s \
  --min-instances 1 \
  --max-instances 20 \
  --cpu-boost \
  --no-allow-unauthenticated \
  --service-account panelin-api@${PROJECT_ID}.iam.gserviceaccount.com \
  --set-secrets "OPENAI_API_KEY=OPENAI_API_KEY:latest,SHOPIFY_API_KEY=SHOPIFY_API_KEY:latest" \
  --set-env-vars "ENVIRONMENT=production,LOG_LEVEL=WARNING"
```

### 4. Verify Deployment

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe panelin-api \
  --region us-central1 --format 'value(status.url)')

# Get identity token for authenticated requests
TOKEN=$(gcloud auth print-identity-token)

# Health check
curl -H "Authorization: Bearer ${TOKEN}" "${SERVICE_URL}/health"

# Readiness check
curl -H "Authorization: Bearer ${TOKEN}" "${SERVICE_URL}/ready"
```

---

## Health Checks

### Endpoints

| Endpoint | Purpose | Expected Response |
|----------|---------|-------------------|
| `/health` | Liveness probe - is the process running? | `{"status": "healthy"}` |
| `/ready` | Readiness probe - can accept traffic? | `{"ready": true}` |
| `/metrics` | Basic metrics | Uptime, request counts |

### Cloud Run Startup Probe

Cloud Run automatically probes the container. Configure startup behavior in the service:

```bash
gcloud run services update panelin-api \
  --region us-central1 \
  --startup-probe-path=/health \
  --startup-probe-initial-delay=5 \
  --startup-probe-timeout=10 \
  --startup-probe-period=15
```

---

## Monitoring & Alerting

### Create Alert Policies

```bash
# Create error rate alert
gcloud alpha monitoring policies create \
  --display-name="Panelin API - High Error Rate" \
  --condition-display-name="Error rate > 1%" \
  --condition-filter="resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"panelin-api\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.labels.response_code_class=\"5xx\"" \
  --notification-channels="YOUR_CHANNEL_ID"

# Create latency alert
gcloud alpha monitoring policies create \
  --display-name="Panelin API - High Latency" \
  --condition-display-name="P95 latency > 1000ms" \
  --condition-filter="resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"panelin-api\" AND metric.type=\"run.googleapis.com/request_latencies\"" \
  --notification-channels="YOUR_CHANNEL_ID"
```

### Dashboard Setup

Create a dashboard in Cloud Monitoring with:

- Request rate (requests/minute)
- Error rate by response code
- Latency percentiles (P50, P95, P99)
- Instance count
- Cold start frequency
- Memory and CPU utilization

### Log-Based Metrics

```bash
# Create metric for application errors
gcloud logging metrics create panelin-api-errors \
  --description="Application errors in Panelin API" \
  --filter='resource.type="cloud_run_revision" AND resource.labels.service_name="panelin-api" AND severity>=ERROR'
```

---

## CI/CD Pipeline

### Using Cloud Build

The repository includes two Cloud Build configurations:

1. **`cloudbuild.yaml`** - For staging deployments
2. **`cloudbuild-production.yaml`** - For production deployments (stricter quality gates)

### Setting Up Triggers

```bash
# Staging trigger (on push to develop branch)
gcloud builds triggers create github \
  --name="panelin-api-staging" \
  --repo-name="panelin" \
  --repo-owner="your-org" \
  --branch-pattern="develop" \
  --build-config="cloudbuild.yaml" \
  --substitutions="_ENVIRONMENT=staging"

# Production trigger (manual or on main branch)
gcloud builds triggers create github \
  --name="panelin-api-production" \
  --repo-name="panelin" \
  --repo-owner="your-org" \
  --branch-pattern="main" \
  --build-config="cloudbuild-production.yaml" \
  --require-approval
```

---

## Rollback Procedures

### Quick Rollback

```bash
# List revisions
gcloud run revisions list --service panelin-api --region us-central1

# Rollback to previous revision
gcloud run services update-traffic panelin-api \
  --region us-central1 \
  --to-revisions PREVIOUS_REVISION=100
```

### Canary Rollback

```bash
# If running canary, route all traffic to stable
gcloud run services update-traffic panelin-api \
  --region us-central1 \
  --to-tags stable=100
```

---

## Troubleshooting

### Common Issues

#### 1. Container Startup Failures

```bash
# Check logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=panelin-api" --limit=50

# Common causes:
# - PORT not properly configured (fixed in our Dockerfile)
# - Missing secrets
# - Dependency import errors
```

#### 2. High Cold Start Latency

```bash
# Increase min-instances
gcloud run services update panelin-api \
  --region us-central1 \
  --min-instances 1

# Enable CPU boost
gcloud run services update panelin-api \
  --region us-central1 \
  --cpu-boost
```

#### 3. Secret Access Errors

```bash
# Verify service account has access
gcloud secrets get-iam-policy OPENAI_API_KEY

# Verify secret exists and has versions
gcloud secrets versions list OPENAI_API_KEY
```

#### 4. Authentication Issues

```bash
# For service-to-service calls
TOKEN=$(gcloud auth print-identity-token --audiences=SERVICE_URL)

# For user access via IAP
# Configure Identity-Aware Proxy in Cloud Console
```

---

## Resource Configuration Reference

| Environment | CPU | Memory | Concurrency | Min Instances | Max Instances | Timeout |
|------------|-----|--------|-------------|---------------|---------------|---------|
| Staging | 1 | 512Mi | 80 | 0 | 10 | 300s |
| Production | 2 | 1Gi | 100 | 1 | 20 | 60s |

---

## SLO Targets

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Availability | 99.9% | < 99.5% |
| Error Rate | < 0.1% | > 1% |
| P50 Latency | < 200ms | > 500ms |
| P95 Latency | < 500ms | > 1000ms |
| P99 Latency | < 1000ms | > 2000ms |

---

## Checklist

- [ ] GCP project configured with required APIs
- [ ] Service account created with minimal privileges
- [ ] Secrets stored in Secret Manager
- [ ] Artifact Registry repository created
- [ ] Container image built and pushed
- [ ] Staging environment deployed and tested
- [ ] Health endpoints verified
- [ ] Monitoring alerts configured
- [ ] CI/CD triggers set up
- [ ] Production deployment completed
- [ ] Rollback procedure tested
