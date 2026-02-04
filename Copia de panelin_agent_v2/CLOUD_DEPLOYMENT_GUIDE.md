# Panelin Agent V2 - Cloud Run Deployment Guide

## Overview

This guide covers deploying the Panelin Agent V2 API to Google Cloud Run.

## Prerequisites

1. **Google Cloud SDK** installed and configured
2. **Docker** installed locally (for local testing)
3. A **GCP Project** with billing enabled
4. Required APIs enabled:
   - Cloud Run API
   - Cloud Build API
   - Artifact Registry API
   - Secret Manager API

## Quick Start

### 1. Enable Required APIs

```bash
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com
```

### 2. Create Artifact Registry Repository

```bash
gcloud artifacts repositories create panelin \
    --repository-format=docker \
    --location=us-central1 \
    --description="Panelin Agent Docker images"
```

### 3. Create Service Account (Recommended)

```bash
# Create service account
gcloud iam service-accounts create panelin-runner \
    --display-name="Panelin API Runner"

# Grant minimal permissions
PROJECT_ID=$(gcloud config get-value project)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:panelin-runner@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### 4. Store Secrets (if needed)

```bash
# Example: Store OpenAI API key
echo -n "your-api-key-here" | gcloud secrets create OPENAI_API_KEY \
    --data-file=-

# Grant access to the service account
gcloud secrets add-iam-policy-binding OPENAI_API_KEY \
    --member="serviceAccount:panelin-runner@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### 5. Deploy to Cloud Run

#### Option A: Direct Deploy (Simplest)

```bash
gcloud run deploy panelin-api \
    --source . \
    --region us-central1 \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --concurrency 80 \
    --min-instances 0 \
    --max-instances 10 \
    --allow-unauthenticated
```

#### Option B: Using Cloud Build (CI/CD)

```bash
# Submit build
gcloud builds submit \
    --config=cloudbuild.yaml \
    --substitutions=_REGION=us-central1,_REPO=panelin,_SERVICE=panelin-api
```

### 6. Update the Cloud Run URL

After deployment, update the `CLOUD_RUN_URL` environment variable:

```bash
# Get the deployed URL
gcloud run services describe panelin-api --region us-central1 --format='value(status.url)'

# Update the service with the correct URL
gcloud run services update panelin-api \
    --region us-central1 \
    --set-env-vars "CLOUD_RUN_URL=https://panelin-api-xxxxx-uc.a.run.app"
```

## Local Development

### Build and Run Locally

```bash
# Build the image
docker build -t panelin-api .

# Run locally
docker run -p 8080:8080 panelin-api

# Test endpoints
curl http://localhost:8080/health
curl http://localhost:8080/ready
```

## Health Endpoints

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `/health` | Liveness probe | Returns 200 if service is alive |
| `/ready` | Readiness probe | Returns 200 if service can accept traffic |
| `/` | Root info | Basic service information |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port (set by Cloud Run) | 8080 |
| `CLOUD_RUN_URL` | Public URL for OpenAPI schema | (placeholder) |
| `OPENAI_API_KEY` | OpenAI API key (via Secret Manager) | - |

## Monitoring

### View Logs

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=panelin-api" \
    --limit=50 \
    --format="table(timestamp,textPayload)"
```

### Create Alerts (Recommended)

```bash
# Create notification channel first, then:
# - Error rate > 5%
# - P95 latency > 3000ms
# - Cold start frequency alerts
```

## Troubleshooting

### Container Won't Start

1. Check logs: `gcloud run services logs read panelin-api`
2. Verify the PORT is being read: `ENV PORT=8080`
3. Ensure the CMD uses shell expansion for `${PORT}`

### Connection Refused

1. Ensure the server binds to `0.0.0.0`, not `127.0.0.1`
2. Check that the port matches `$PORT`

### Slow Cold Starts

1. Consider `--min-instances 1` for low-latency requirements
2. Optimize the Docker image (use slim base, reduce layers)
3. Lazy-load heavy dependencies

## Cost Optimization

- Set `--min-instances 0` to scale to zero when idle
- Use `--cpu-throttling` to reduce idle CPU costs
- Monitor request patterns and adjust `--max-instances`

## Security Checklist

- [ ] Service account with least privilege
- [ ] Secrets in Secret Manager (not env vars or code)
- [ ] `--no-allow-unauthenticated` for internal APIs
- [ ] VPC connector for private resources
- [ ] Regular dependency updates
