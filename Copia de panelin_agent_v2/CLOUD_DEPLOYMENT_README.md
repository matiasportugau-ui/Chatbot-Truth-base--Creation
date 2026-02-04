# Panelin Agent V2 - Cloud Run Deployment Guide

## Overview

This guide explains how to deploy the Panelin Agent V2 API to Google Cloud Run.

## Prerequisites

1. **Google Cloud Project** with billing enabled
2. **gcloud CLI** installed and authenticated
3. **Required APIs enabled**:
   - Cloud Run API
   - Cloud Build API
   - Artifact Registry API
   - Secret Manager API (optional, for secrets)

## Quick Start - Manual Deployment

### 1. Set Environment Variables

```bash
export PROJECT_ID="your-project-id"
export REGION="us-central1"
export SERVICE="panelin-api"
```

### 2. Deploy from Source

```bash
cd "Copia de panelin_agent_v2"

gcloud run deploy $SERVICE \
  --source . \
  --region $REGION \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --concurrency 80 \
  --min-instances 0 \
  --max-instances 10 \
  --allow-unauthenticated
```

### 3. Get the Service URL

```bash
gcloud run services describe $SERVICE --region $REGION --format="value(status.url)"
```

## CI/CD Deployment (Recommended)

### 1. Create Artifact Registry Repository

```bash
gcloud artifacts repositories create panelin \
  --repository-format=docker \
  --location=$REGION
```

### 2. Create Service Account

```bash
gcloud iam service-accounts create panelin-runner \
  --display-name="Panelin API Runner"
```

### 3. Set Up Cloud Build Trigger

Connect your GitHub repository to Cloud Build and create a trigger that uses `cloudbuild.yaml`:

```bash
# From GitHub integration in Cloud Console
# Or use gcloud:
gcloud builds triggers create github \
  --repo-name="Chatbot-Truth-base--Creation" \
  --repo-owner="matiasportugau-ui" \
  --branch-pattern="^main$" \
  --build-config="Copia de panelin_agent_v2/cloudbuild.yaml"
```

### 4. (Optional) Set Up Secrets

```bash
# Create secret
echo -n "your-openai-api-key" | gcloud secrets create OPENAI_API_KEY --data-file=-

# Grant access to service account
gcloud secrets add-iam-policy-binding OPENAI_API_KEY \
  --member="serviceAccount:panelin-runner@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

Then uncomment the `--set-secrets` line in `cloudbuild.yaml`.

## Health Endpoints

The API exposes the following health endpoints:

| Endpoint | Purpose | Usage |
|----------|---------|-------|
| `/health` | Liveness probe | Checks if service is running |
| `/ready` | Readiness probe | Checks if service can handle requests |

### Configure Cloud Run Probes

```bash
gcloud run services update $SERVICE \
  --region $REGION \
  --liveness-probe-path=/health \
  --startup-probe-path=/ready
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port (set by Cloud Run) | 8080 |
| `CLOUD_RUN_URL` | Public URL for OpenAPI schema | https://panelin-api-xxxxx-uc.a.run.app |
| `OPENAI_API_KEY` | OpenAI API key (optional) | - |

## Monitoring

### View Logs

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE" --limit 100
```

### Set Up Alerts

1. Go to Cloud Monitoring in Google Cloud Console
2. Create alerting policies for:
   - Error rate > 1%
   - P95 latency > 2000ms
   - Instance count > threshold

## Updating the Deployment

### Update with New Image

```bash
gcloud run deploy $SERVICE \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/panelin/panelin-api:latest \
  --region $REGION
```

### Update Environment Variables

```bash
gcloud run services update $SERVICE \
  --region $REGION \
  --set-env-vars="CLOUD_RUN_URL=https://your-new-url.run.app"
```

## Troubleshooting

### Common Issues

1. **Container fails to start**
   - Check logs: `gcloud run logs read --service=$SERVICE`
   - Verify PORT environment variable is used correctly

2. **Health checks failing**
   - Ensure `/health` endpoint returns 200
   - Increase startup timeout if needed

3. **Permission denied errors**
   - Verify service account has necessary roles
   - Check Secret Manager access if using secrets

### Rollback

```bash
# List revisions
gcloud run revisions list --service=$SERVICE --region=$REGION

# Rollback to previous revision
gcloud run services update-traffic $SERVICE \
  --region $REGION \
  --to-revisions=panelin-api-00001-xxx=100
```

## Files Created

| File | Description |
|------|-------------|
| `Dockerfile` | Container configuration |
| `.dockerignore` | Files excluded from container |
| `cloudbuild.yaml` | Cloud Build CI/CD pipeline |
| `requirements.txt` | Pinned Python dependencies |

## API Documentation

Once deployed, access the API documentation at:
- Swagger UI: `https://<your-cloud-run-url>/docs`
- OpenAPI JSON: `https://<your-cloud-run-url>/openapi.json`
